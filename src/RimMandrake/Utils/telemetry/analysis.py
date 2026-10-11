"""Alert rules, sparklines, regression and proof-flip detectors, retention (design §6, §8, §11 Q8a).

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
    "vhdx_slack_gb": 300, "vhdx_slack_only_below_free_gb": 500,
    "commit_pct": 90,
    "ratio_low": 0.5, "ratio_low_window_s": 120, "ratio_low_mult": 1,
    "stall_s": 10, "stall_recent_s": 900,
    "exc_per_s": 50,
    "tps_blind_s": 90, "wsl_blind_s": 600,
    "recent_event_s": 24 * 3600,
}


def _alert(aid, level, text, since, link=None):
    return {"id": aid, "level": level, "text": text, "since": since, "link": link}


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
    vx, wh = host.get("vhdx"), latest.get("wsl_host")
    e = (host.get("vols") or {}).get("E")
    if vx and vx.get("alloc") and wh and wh.get("disk_used") and e:
        slack = (vx["alloc"] - wh["disk_used"]) / GB
        if slack > R["vhdx_slack_gb"] and e["free"] / GB < R["vhdx_slack_only_below_free_gb"]:
            out.append(_alert("vhdx_slack", "amber",
                              f"WSL disk image holds {slack:.0f} GB more than WSL uses, and E: is down to "
                              f"{e['free'] / GB:.0f} GB free", host["ts"]))
    mem = host.get("mem") or {}
    if mem.get("commit_limit"):
        pct = 100.0 * mem["commit_total"] / mem["commit_limit"]
        if pct > R["commit_pct"]:
            out.append(_alert("commit", "amber", f"Windows commit charge at {pct:.0f}% of the limit", host["ts"]))
    # TPS ratio low at normal speed for 2 minutes, unpaused (at speed 3 the full list is CPU-bound
    # by design, ratio ~0.05, so the rule is scoped to mult 1; see the report's open question)
    hist = [h for h in latest.get("tps_hist", []) if now - h[0] <= R["ratio_low_window_s"] + 15]
    run = [h for h in hist if h[2] == "run" and h[3] == R["ratio_low_mult"] and h[1] is not None]
    if run and len(run) == len(hist) and hist[-1][0] - hist[0][0] >= R["ratio_low_window_s"] - 10:
        med = statistics.median(h[1] for h in run)
        if med < R["ratio_low"]:
            out.append(_alert("tps_low", "amber", f"game at {med:.2f}x its target speed for 2 min (normal speed)",
                              run[0][0]))
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
    for r in con.execute("SELECT ts,kind,subject,detail FROM events WHERE ts>? AND kind IN "
                         "('regression','proof_flip','log_milestone') ORDER BY ts", (since,)):
        if r["kind"] == "log_milestone" and "cap" not in str(r["subject"]).lower():
            continue
        txt = {"regression": "possible slowdown after deploy", "proof_flip": "proof row flipped",
               "log_milestone": "game log hit its message cap"}[r["kind"]]
        out.append(_alert(f"{r['kind']}:{int(r['ts'])}:{r['subject']}", "amber",
                          f"{txt}: {str(r['subject'])[:80]}", r["ts"]))
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


# ------------------------------------------------------------------ regression (passive, §6.2 layer 1)

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


def check_deploys(con, now: float, fetch=windows_from_vm) -> int:
    """For each deploy 2 h .. 7 d old not yet judged, compare tick ms per speed before/after."""
    n = 0
    for d in con.execute("SELECT id,ts,subject,detail FROM events WHERE kind='deploy' AND ts BETWEEN ? AND ?",
                         (now - 7 * 86400, now - 2 * 3600)).fetchall():
        done = store.kv_get(con, f"regr:{d['id']}")
        if done and done.get("final"):
            continue
        best = None
        for mult in (1, 3, 6, 12):
            before = fetch("rm_game_tick_ms", d["ts"] - 86400, d["ts"] - 60, mult)
            after = fetch("rm_game_tick_ms", d["ts"] + 120, min(now, d["ts"] + 86400), mult)
            c = compare_windows(before, after)
            c["mult"] = mult
            if c["verdict"] != "UNMEASURED" and (best is None or c["verdict"] == "REGRESSION"):
                best = c
            elif best is None:
                best = c
        final = now - d["ts"] > 86400
        store.kv_set(con, f"regr:{d['id']}", {"final": final, **(best or {})})
        if best and best["verdict"] == "REGRESSION":
            store.add_event(con, now, "regression", d["subject"],
                            {**best, "deploy_ts": d["ts"], "note": "no cause is established; next: "
                             "jawa/map_comp_timing on the slow save"}, "detector", f"regr:{d['id']}")
            n += 1
    con.commit()
    return n


def check_proof_flips(con) -> int:
    """PASS -> anything else between consecutive runs of the same proof script/mod."""
    n = 0
    runs = con.execute("SELECT id,ts,mod,script FROM proof_runs ORDER BY mod,script,ts").fetchall()
    prev = None
    for r in runs:
        if prev and prev["mod"] == r["mod"] and (prev["script"] or "") == (r["script"] or ""):
            a = {x["row_id"]: x["status"] for x in con.execute("SELECT row_id,status FROM proof_rows WHERE run_id=?",
                                                               (prev["id"],))}
            flips = [rid for rid, st in ((x["row_id"], x["status"]) for x in
                                         con.execute("SELECT row_id,status FROM proof_rows WHERE run_id=?", (r["id"],)))
                     if a.get(rid, "").upper() == "PASS" and str(st).upper() != "PASS"]
            if flips and store.add_event(con, r["ts"], "proof_flip", r["mod"],
                                         {"from": prev["id"], "to": r["id"], "rows": flips[:20], "n": len(flips)},
                                         "detector", f"flip:{prev['id']}>{r['id']}"):
                n += 1
        prev = r
    con.commit()
    return n


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
