"""Alert rules, sparklines, on-demand window comparison, retention (design §8, §11 Q8a).

Owner, 2026-10-11: coarse "watch out, something's wrong" alarms only (extremely low memory or TPS,
disk filling); version comparison is an on-demand tool (`telemetry around`), never a per-deploy
ceremony. "Minimal is good, add functionality as needed by debugging."

Alerts are not delivered here: they are written to <state>/alerts.json, which RimPulse reads
(pulse_core.classify_telemetry) and turns into red/amber rows with its own ack, toast and digest
machinery. RimPulse stays the one attention surface; Grafana alerting stays off (design §5.6).

Every detector prints its window counts and answers UNMEASURED when it cannot see, never "clean".
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import statistics
import time

import store
from tcommon import cfg, iso, write_json_atomic

GB = 1 << 30

RULES = {  # thresholds (design §8); one place, quoted by the skill
    "disk_red_gb": 20, "disk_amber_gb": 50,
    "mem_avail_gb": 3,
    "commit_pct": 90,
    "ratio_low": 0.5, "ratio_low_window_s": 120, "ratio_low_mult": 1,
    "ratio_bridge_busy_frac": 0.10,   # a window whose main thread spent >10 % on bridge work is not judged
    "ratio_min_windows": 12,
    "stall_s": 10, "stall_recent_s": 900,
    "exc_per_s": 50,
    "tps_blind_s": 90, "wsl_blind_s": 600,
    "recent_event_s": 24 * 3600,
}


def _alert(aid, level, text, since, link=None, detail=None):
    a = {"id": aid, "level": level, "text": text, "since": since, "link": link}
    if detail:
        a["detail"] = detail
    return a


def log_firings(con, alerts: list, now: float) -> int:
    """One `alert_fired` event per alert incident (id + since), so thresholds can be retuned from
    labelled history: `telemetry label <event id> fp|tp` (owner 2026-10-11: watch for noninformative
    false positives and retune until they are gone; reward true detections)."""
    n = 0
    for a in alerts:
        if store.add_event(con, now, "alert_fired", a["id"], a, "telemetryd",
                           f"alert:{a['id']}@{int(a.get('since') or now)}"):
            n += 1
    con.commit()
    return n


def evaluate(latest: dict, con, sources: dict, vm_error: str | None, now: float) -> list[dict]:
    R = RULES
    out = []
    host = latest.get("host") or {}
    for letter, v in (host.get("vols") or {}).items():
        if not v:
            continue
        free_gb = v["free"] / GB
        if free_gb < R["disk_red_gb"]:
            out.append(_alert(f"disk:{letter}", "red", f"{letter}: only {free_gb:.0f} GB free", host["ts"]))
        elif free_gb < R["disk_amber_gb"]:
            out.append(_alert(f"disk:{letter}", "amber", f"{letter}: {free_gb:.0f} GB free", host["ts"]))
    # no empty-space / image-slack alert (owner 2026-10-11: "That's not a danger."); free space only
    mem = host.get("mem") or {}
    if mem.get("phys_avail") and mem["phys_avail"] / GB < R["mem_avail_gb"]:
        out.append(_alert("mem_low", "red", f"Windows has only {mem['phys_avail'] / GB:.1f} GB memory available",
                          host["ts"]))
    if mem.get("commit_limit"):
        pct = 100.0 * mem["commit_total"] / mem["commit_limit"]
        if pct > R["commit_pct"]:
            out.append(_alert("commit", "amber", f"Windows commit charge at {pct:.0f}% of the limit", host["ts"]))
    # TPS ratio low at NORMAL speed for 2 minutes, unpaused (owner card 2026-10-11; speed 3 on the full
    # list is CPU-bound by design). Bridge delay spikes must not trigger it (owner, same day): windows
    # where the bridge held the main thread >10 % are skipped, and the verdict is a median over >= 12
    # remaining windows. Every firing is logged (`alert_fired`) so `telemetry label` can grade it.
    hist = [h for h in latest.get("tps_hist", []) if now - h[0] <= R["ratio_low_window_s"] + 15]
    run = [h for h in hist if h[2] == "run" and h[3] == R["ratio_low_mult"] and h[1] is not None]
    calm = [h for h in run if (h[4] if len(h) > 4 else 0) <= R["ratio_bridge_busy_frac"]]
    if run and len(run) == len(hist) and hist[-1][0] - hist[0][0] >= R["ratio_low_window_s"] - 10 \
            and len(calm) >= R["ratio_min_windows"]:
        med = statistics.median(h[1] for h in calm)
        if med < R["ratio_low"]:
            out.append(_alert("tps_low", "amber", f"game at {med:.2f}x its target speed for 2 min (normal speed)",
                              calm[0][0], detail={"median": med, "windows": len(calm),
                                                  "skipped_bridge_busy": len(run) - len(calm)}))
    for inc in latest.get("incidents", []):
        if now - inc["ts"] < R["stall_recent_s"] and (inc.get("gapS") or 0) >= R["stall_s"]:
            out.append(_alert(f"stall:{int(inc['ts'])}", "amber",
                              f"game froze {inc['gapS']:.0f} s ({inc.get('type')}) at {iso(inc['ts'])[11:16]}",
                              inc["ts"]))
    t = latest.get("tps") or {}
    if t.get("exc") and t.get("dReal") and now - t["ts"] < 120:
        rate = t["exc"] / max(t["dReal"], 0.1)
        if rate > R["exc_per_s"]:
            out.append(_alert("exc_storm", "amber", f"exception storm: {rate:.0f}/s in game log", t["ts"]))
    since = now - R["recent_event_s"]
    for r in con.execute("SELECT ts,kind,subject FROM events WHERE ts>? AND kind='log_milestone' ORDER BY ts",
                         (since,)):
        if "cap" in str(r["subject"]).lower():
            out.append(_alert(f"logcap:{int(r['ts'])}", "amber", "game log hit its message cap", r["ts"]))
    # blindness: the instrument itself
    if vm_error:
        out.append(_alert("blind:vm", "amber", "telemetry: VictoriaMetrics unreachable (points spooled)", now))
    gr = latest.get("game_running")
    tps_src = sources.get("tps") or {}
    last_tps = tps_src.get("last_row_ts")
    if gr and (last_tps is None or now - last_tps > R["tps_blind_s"]) and latest.get("game_running_since", now) < now - 180:
        out.append(_alert("blind:tps", "amber", "telemetry blind: RimWorld runs but its TPS record is silent",
                          last_tps or now))
    wsl = (sources.get("wsl") or {}).get("last_row_ts")
    if wsl is not None and now - wsl > R["wsl_blind_s"]:
        out.append(_alert("blind:wsl", "amber", "telemetry blind: WSL exporter silent", wsl))
    return out


def push_spark(latest: dict, now: float) -> None:
    """One point per minute per sparkline, last 2 h (design §8: four sparklines)."""
    sp = latest.setdefault("sparks", {"tps_ratio": [], "exc_per_s": [], "host_free_gb": [], "min_vol_free_gb": []})
    t = latest.get("tps") or {}
    fresh = t and now - t.get("ts", 0) < 90
    host = latest.get("host") or {}
    vols = [v["free"] / GB for v in (host.get("vols") or {}).values() if v]
    mem = host.get("mem") or {}
    vals = {
        "tps_ratio": t.get("ratio") if fresh else None,
        "exc_per_s": (t["exc"] / max(t.get("dReal") or 1, 0.1)) if fresh and t.get("exc") is not None else None,
        "host_free_gb": (mem["phys_avail"] / GB) if mem.get("phys_avail") else None,
        "min_vol_free_gb": min(vols) if vols else None,
    }
    for k, v in vals.items():
        sp[k].append([int(now), None if v is None else round(v, 3)])
        sp[k] = sp[k][-120:]


def write_state(latest: dict, alerts: list, sources: dict, extra: dict, now: float) -> None:
    write_json_atomic(os.path.join(cfg()["state"], "alerts.json"), {
        "v": 1, "at": now, "alerts": alerts, "sparks": latest.get("sparks", {}),
        "sources": sources, "grafana": cfg()["grafana_url"], **extra})


# ------------------------------------------------------------------ on-demand comparison (`telemetry around`)

def compare_windows(before: list[float], after: list[float], min_n: int = 30) -> dict:
    """Median shift test. Returns verdict REGRESSION / IMPROVED / NO_SHIFT / UNMEASURED with counts."""
    out = {"n_before": len(before), "n_after": len(after)}
    if len(before) < min_n or len(after) < min_n:
        out["verdict"] = "UNMEASURED"
        out["why"] = f"need {min_n} windows each side"
        return out
    mb, ma = statistics.median(before), statistics.median(after)
    mad = statistics.median(abs(x - mb) for x in before) or 1e-9
    shift = ma - mb
    rel = shift / mb if mb else float("inf")
    thr = max(0.20 * mb, 3 * mad)
    out.update({"median_before": mb, "median_after": ma, "shift": shift, "rel": rel, "threshold": thr})
    out["verdict"] = "REGRESSION" if shift > thr else "IMPROVED" if -shift > thr else "NO_SHIFT"
    return out


def windows_from_vm(metric: str, start: float, end: float, mult=None) -> list[float]:
    sel = f'{metric}{{mult="{mult}"}}' if mult is not None else metric
    try:
        d = store.vm_get("/api/v1/export?" + __import__("urllib.parse").parse.urlencode(
            {"match[]": sel, "start": f"{start:.0f}", "end": f"{end:.0f}"}), timeout=30)
    except Exception:  # noqa: BLE001
        return []
    vals = []
    for line in d.splitlines():
        try:
            vals.extend(json.loads(line)["values"])
        except (ValueError, KeyError):
            continue
    return vals


# ------------------------------------------------------------------ retention

def _tree_bytes(d: str) -> int:
    t = 0
    for root, _, files in os.walk(d):
        for f in files:
            try:
                t += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return t


def retention(con, now: float) -> dict:
    c = cfg()
    raw, arch = c["raw"], c["archive"]
    rep = {"moved": 0, "deleted": 0, "bridge_rows": 0}
    have_arch = os.path.isdir(os.path.dirname(arch.rstrip("\\/")) or arch)
    files = sorted(glob.glob(os.path.join(raw, "*", "*")), key=lambda p: os.path.getmtime(p))
    cutoff = now - c["raw_days_hot"] * 86400
    total = sum(os.path.getsize(p) for p in files)
    for p in files:
        old = os.path.getmtime(p) < cutoff
        over = total > c["raw_cap_gb"] * GB
        if not (old or over):
            continue
        size = os.path.getsize(p)
        if have_arch:
            dst = os.path.join(arch, "raw", os.path.basename(os.path.dirname(p)))
            os.makedirs(dst, exist_ok=True)
            shutil.move(p, os.path.join(dst, os.path.basename(p)))
            rep["moved"] += 1
        elif over:
            os.remove(p)
            rep["deleted"] += 1
        else:
            continue
        total -= size
    if have_arch and os.path.isdir(arch):
        afiles = sorted(glob.glob(os.path.join(arch, "raw", "*", "*")), key=lambda p: os.path.getmtime(p))
        atotal = sum(os.path.getsize(p) for p in afiles)
        for p in afiles:
            if atotal <= c["archive_cap_gb"] * GB:
                break
            atotal -= os.path.getsize(p)
            os.remove(p)
            rep["deleted"] += 1
    cur = con.execute("DELETE FROM bridge_calls WHERE ts < ?", (now - c["bridge_rows_days"] * 86400,))
    rep["bridge_rows"] = cur.rowcount
    con.commit()
    logs = c["logs"]
    for p in glob.glob(os.path.join(logs, "*.log")):
        if os.path.getsize(p) > 20 << 20:
            os.replace(p, p + ".1")
    if rep["moved"] or rep["deleted"]:
        store.add_event(con, now, "retention", None, rep, "telemetryd", f"retention:{int(now)}")
        con.commit()
    return rep
