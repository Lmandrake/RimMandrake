#!/usr/bin/env python3
"""restart_reconcile: every goodbye or restart request ends in restart_verified or a told incident (CK3 in
design/RimMandrake/operating_requirements_2026-11-01.md, RESTART_JOIN_BUILD_EVERY_GOODBYE_ENDS).

Why it is a separate program: on 2026-11-01 two goodbyes were cancelled by a peer message and nobody heard. Each past fix
sat on the code path that dropped them, so this one trusts nothing there. No AI; its own timer (rm-restart-reconcile,
every restart_reconcile_pass_s); it imports the Dispatcher's readers but never runs a tick and never tells through it.

A REQUEST is any of, joined on seat and time:
  <dispatcher state>/restart/<SEAT>.request.json   written by the seat, whether or not any tick ever read it
  <dispatcher state>/restart/done/*.request.json   a request the Dispatcher took
  journal.jsonl restart_request                    including the ones the Dispatcher started itself
  his whole-message goodbye in a seat's transcript (a seat with goodbye_phrases), read by byte cursor: a window that
                                                   never ran `seat_restart.py request` leaves only this
It ENDS at the first journal restart_verified of that seat at or after it. A restart_cancel ends nothing: that is the
fault. The one exception is a cancel of a request the Dispatcher started itself, which asked nobody ("no restart owed").

An unmatched request alarms restart_reconcile_pass_s + restart_reconcile_slack_s before restart_reconcile_s, so the told
incident lands INSIDE restart_reconcile_s (a verified restart takes ~250 s, journal 2026-10-30..11-01). A request held
for its helpers (deferred, Dispatcher-started, or the Dispatcher still journalling restart_hold or a fresh kill) really takes up to 64
min, so it gets restart_reconcile_held_s from the same file until a cancel takes that away; a goodbye never does. A hold
line only lengthens a bound that still ends: a dropped request stops producing them. "Still journalling" means a hold
within restart_reconcile_hold_fresh_s: a tick stamps its lines at its start and writes them as it acts, so a slow tick
leaves none on disk for its whole length (3 m 56 s on 2026-11-01: a false alarm at 615 s, OPS_RESTART_UNSTICK_FOUNDRY_HDDT).

One open incident per seat, so one outage is one alarm; later requests join it, and a verified restart closes it.
Told, in order, none through the Dispatcher: the Conductor log, the seat's doorbell if armed and free, one fixed ledger
item per seat for BENCH (OPS_ alarm items launch Operations), reopened on a repeat. The pass writes
ops_watch/restart_reconcile.json whatever it finds; deadman_check holds that file to its age. An unreadable journal or
transcript is an incident on the pseudo-seat JOURNAL or TRANSCRIPT, never silence.

    python3 src/RimMandrake/Utils/restart_reconcile.py run [--no-file]
"""
import argparse
import fcntl
import glob
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
import doorbell  # noqa: E402
import goodbye_phrase as GP  # noqa: E402
import ops_watch as OW  # noqa: E402
import seat_restart as SR  # noqa: E402

SCHEDULE = HERE.parent / "rimflow" / "dispatcher_schedule.json"
RULES = HERE / "ops_watch_rules.json"
KEYS = ("restart_reconcile_s", "restart_reconcile_held_s", "restart_reconcile_hold_fresh_s", "restart_reconcile_pass_s",
        "restart_reconcile_slack_s", "restart_reconcile_lookback_s")
JOURNAL_SEAT = "JOURNAL"
TRANSCRIPT_SEAT = "TRANSCRIPT"
STUCK_PASSES = 3                 # a torn tail clears by the next pass; three in a row is a transcript we cannot read


def limits(sch):
    """-> the thresholds. A missing or senseless one fails loudly by name: no default stands in for a limit."""
    out = {}
    for k in KEYS:
        v = sch.get(k)
        if not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0:
            raise ValueError("dispatcher_schedule.json: %s is %r" % (k, v))
        out[k] = v
    if out["restart_reconcile_pass_s"] + out["restart_reconcile_slack_s"] >= out["restart_reconcile_s"]:
        raise ValueError("dispatcher_schedule.json: pass + slack leaves no time inside restart_reconcile_s")
    return out


def read_journal(root):
    """-> ([rows of restart_request, _cancel, _verified, _hold, _kill, _relaunched], None) | ([], why). A torn line is skipped: the
    Dispatcher may be mid-write. An unreadable file is not an empty one."""
    p = os.path.join(root, "journal.jsonl")
    rows = []
    try:
        with open(p, encoding="utf-8") as f:
            for ln in f:
                if '"restart_' not in ln:
                    continue
                try:
                    r = json.loads(ln)
                except ValueError:
                    continue
                if r.get("do") in ("restart_request", "restart_cancel", "restart_verified", "restart_hold", "restart_kill",
                                    "restart_relaunched"):
                    rows.append(r)
    except OSError as e:
        return [], "%s: %s" % (p, e)
    return rows, None


def _file_row(rec, source, seat=None):
    ts = rec.get("ts") if isinstance(rec, dict) else None
    seat = (rec.get("seat") if isinstance(rec, dict) else None) or seat
    if not seat or not isinstance(ts, (int, float)) or isinstance(ts, bool):
        return None
    return {"seat": seat, "ts": float(ts), "source": source, "reason": str(rec.get("reason") or ""),
            "held": rec.get("deferred") is True}


def read_requests(root):
    """-> rows of the request files, pending and taken. A file that does not parse names its seat and counts as written
    now: it is a request nobody can read."""
    d = SR.restart_dir(root)
    out = []
    for src, pat in (("pending", "*.request.json"), ("done", os.path.join("done", "*.request.json"))):
        for p in glob.glob(os.path.join(d, pat)):
            seat = os.path.basename(p).split(".")[0].split("-")[0]
            row = _file_row(SR._read_json(p), src, seat)
            if row is None:
                try:
                    row = {"seat": seat, "ts": os.path.getmtime(p), "source": src, "reason": "unreadable request file",
                           "held": False}
                except OSError:
                    continue
            out.append(row)
    return out


def read_goodbyes(sch, cursors, now, lookback, stuck=None):
    """-> rows of his whole-message goodbyes in each goodbye seat's transcripts newer than lookback; cursors advance past
    complete records only. Never the code path: this reads what he typed, not what any window did about it."""
    out = []
    keep = {}
    peers = SR.peer_names(sch)
    for seat, cfg in (sch.get("seat_restart", {}).get("seats") or {}).items():
        phr = GP.phrases(cfg, default=())
        clone = (sch.get("seats", {}).get(seat) or {}).get("clone")
        if not phr or not clone:
            continue
        d = os.path.join(SR.claude_home(), "projects", SR.re.sub(r"[^A-Za-z0-9]", "-", clone))
        for p in glob.glob(os.path.join(d, "*.jsonl")):
            try:
                if os.path.getmtime(p) < now - lookback:
                    continue
            except OSError:
                continue
            pos = cursors.get(p, 0)
            try:
                for r, end in SR.scan_records(p, pos):
                    pos = end
                    if r.get("type") == "user" and SR._is_human_input(r, peers) and GP.is_goodbye(SR._text(r), phr):
                        ts = SR._ts(r.get("timestamp"))
                        if ts is not None:
                            out.append({"seat": seat, "ts": ts, "source": "transcript", "reason": "goodbye",
                                        "held": False})
                if stuck is not None:
                    stuck.pop(p, None)
            except (OSError, SR.Malformed):      # a record still being written: read from here next pass
                if stuck is not None:
                    stuck[p] = stuck.get(p, 0) + 1
            keep[p] = pos
    cursors.clear()
    cursors.update(keep)
    return out


def row_key(seat, ts):
    return "%s:%.2f" % (seat, ts)


def join(rows, journal, now, lim, armed_at, told=()):
    """Pure. -> [unmatched requests due now, oldest first]. rows: request rows (files, goodbyes). journal: read_journal.
    A row older than armed_at or the lookback is history; what was unmatched then is not this pass's to say. told: keys
    already alarmed. A later hold or kill does not un-alarm one: only restart_verified ends it."""
    epoch = OW.epoch
    fire = lim["restart_reconcile_s"] - lim["restart_reconcile_pass_s"] - lim["restart_reconcile_slack_s"]
    held = lim["restart_reconcile_held_s"]
    merged = {}

    def add(r):
        if r["ts"] < armed_at or r["ts"] < now - lim["restart_reconcile_lookback_s"] or r["ts"] > now:
            return
        k = (r["seat"], round(r["ts"], 2))
        m = merged.setdefault(k, dict(r, sources=[]))
        m["sources"].append(r["source"])
        m["held"] = m["held"] or r["held"]
        m["synthetic"] = m.get("synthetic") or r.get("synthetic", False)
        m["goodbye"] = m.get("goodbye") or "goodbye" in r["reason"].lower()
    for r in rows:
        add(r)
    verified, cancels, holds, kills = {}, {}, {}, {}
    for j in journal:
        t = epoch(j.get("at"))
        if t is None or not j.get("seat"):
            continue
        if j["do"] == "restart_verified":
            verified.setdefault(j["seat"], []).append(t)
        elif j["do"] == "restart_cancel":
            cancels.setdefault(j["seat"], []).append(t)
        elif j["do"] == "restart_hold":
            holds[j["seat"]] = max(t, holds.get(j["seat"], 0))
        elif j["do"] in ("restart_kill", "restart_relaunched"):
            kills[j["seat"]] = max(t, kills.get(j["seat"], 0))
        elif not str(j.get("result") or "").startswith("would"):     # a dry run asked for nothing
            why = str(j.get("why") or "")
            synth = str(j.get("result") or "").startswith("started by the Dispatcher")
            ts = j.get("req_ts")
            add({"seat": j["seat"], "ts": float(ts) if isinstance(ts, (int, float)) else t, "source": "journal",
                 "reason": why, "held": synth or why.startswith("DEFERRED"), "synthetic": synth})
    out = []
    for m in sorted(merged.values(), key=lambda x: x["ts"]):
        ts = m["ts"]
        if any(v >= ts for v in verified.get(m["seat"], ())):
            continue
        cancelled = [c for c in cancels.get(m["seat"], ()) if c >= ts - 1]
        if cancelled and m.get("synthetic"):
            continue                     # the Dispatcher withdrew its own: nobody asked, nothing is owed
        holding = now - holds.get(m["seat"], 0) <= lim["restart_reconcile_hold_fresh_s"] \
            or now - kills.get(m["seat"], 0) <= fire      # killed: the relaunch has the ordinary time to verify
        patient = (m["held"] or holding) and not m["goodbye"] and not cancelled
        limit = held if patient else fire
        if now - ts >= limit or row_key(m["seat"], ts) in told:
            m["age_s"] = int(now - ts)
            m["cancelled"] = bool(cancelled)
            out.append(m)
    return out


def item_name(seat):
    base = "OPS_RESTART_UNSTICK_%s" % seat
    return "%s_%s" % (base, OW.alarm_twist(base))


def title_of(seat, rows):
    r = rows[0]
    how = "cancelled" if r.get("cancelled") else "no restart_verified"
    return "Restart request of %s unmatched %d s (%s): %s" % (seat, r.get("age_s", 0), how, r.get("reason", "")[:120])


def seat_log(sch, seat):
    cfg = (sch.get("seat_restart", {}).get("seats") or {}).get(seat) or {}
    return cfg.get("seat_log") or (sch.get("seat_restart", {}).get("seats", {}).get("BENCH") or {}).get("seat_log")


def tell_log(sch, seat, line):
    """The Conductor's log: it reads this at wake and it needs no Dispatcher, ledger or filer alive."""
    p = seat_log(sch, "BENCH")
    if not p:
        return "no Conductor log in the schedule"
    try:
        with open(p, "a", encoding="utf-8") as f:
            f.write("\n- restart_reconcile (%s): %s\n" % (OW.iso(time.time()), line))
        return None
    except OSError as e:
        return str(e)[:200]


def tell_seat(root, seat, line, now):
    """Ring the seat's own doorbell. Only an armed window with nothing waiting: a ring nobody takes would hold the
    Dispatcher's next kill, and the Dispatcher's own ring is not ours to overwrite."""
    if not SR._read_json(doorbell.armed_path(seat, root)) or os.path.exists(doorbell.inbox_path(seat, root)):
        return False
    doorbell._write_json_atomic(doorbell.inbox_path(seat, root), {
        "seat": seat, "ring_id": "restart_reconcile-%d" % now, "message": line, "rung_at": now, "session_id": None})
    return True


def run_pass(now, root, sch, state, filer, out_dir):
    """One pass. state: the saved dict, updated in place. filer(todo, conf) as ops_watch.real_filer, or None."""
    lim = limits(sch)
    state.setdefault("armed_at", now)
    cursors = state.setdefault("cursors", {})
    open_ = state.setdefault("open", {})
    filed = state.setdefault("filed", {})
    journal, blind = read_journal(root)
    stuck = state.setdefault("stuck", {})
    rows = read_requests(root) + read_goodbyes(sch, cursors, now, lim["restart_reconcile_lookback_s"], stuck)
    state["goodbyes"] = [g for g in state.get("goodbyes", []) + [r for r in rows if r["source"] == "transcript"]
                         if g["ts"] >= now - lim["restart_reconcile_lookback_s"]]
    rows = [r for r in rows if r["source"] != "transcript"] + state["goodbyes"]
    told = {k for cur in open_.values() for k in cur.get("keys", ())}
    due = join(rows, journal, now, lim, state["armed_at"], told)
    by = {}
    for m in due:
        by.setdefault(m["seat"], []).append(m)
    if blind:
        by[JOURNAL_SEAT] = [{"seat": JOURNAL_SEAT, "age_s": 0, "reason": blind}]
    bad = sorted(p for p, n in stuck.items() if n >= STUCK_PASSES)
    if bad:                              # a goodbye behind this line cannot be read: silence here would be a false clean
        by[TRANSCRIPT_SEAT] = [{"seat": TRANSCRIPT_SEAT, "age_s": 0, "reason": "unreadable: " + bad[0]}]
    todo = []
    for seat in sorted(set(by) | set(open_)):
        cur = open_.get(seat)
        if seat not in by:
            if cur:
                note = "restart_reconcile: closed at %s, the seat verified a restart or the request aged out" % OW.iso(now)
                if cur.get("filed"):
                    todo.append({"note_only": True, "item": cur["name"], "name": "note:" + seat, "text": note})
                tell_log(sch, seat, "%s: incident closed" % seat)
                del open_[seat]
            continue
        if not cur:
            title = title_of(seat, by[seat])
            cur = open_[seat] = {"since": OW.iso(now), "name": item_name(seat), "title": title, "filed": False,
                                 "told": {"log": tell_log(sch, seat, title) or "ok",
                                          "doorbell": seat not in (JOURNAL_SEAT, TRANSCRIPT_SEAT) and tell_seat(
                                              root, seat, title + ". Ask for it again or say why not.", now)}}
        cur["rows"] = len(by[seat])
        cur["keys"] = sorted(set(cur.get("keys", ())) | {row_key(m["seat"], m["ts"]) for m in by[seat] if "ts" in m})
        if cur["told"]["log"] != "ok":   # the Conductor's line is owed until it lands
            cur["told"]["log"] = tell_log(sch, seat, cur["title"]) or "ok"
        if not cur.get("filed"):
            todo.append({"aid": "restart_reconcile:" + seat, "name": cur["name"], "title": cur["title"], "seat": seat,
                         "reopen": cur["name"] in filed})
    if todo and filer:
        conf = OW.alarm_conf(json.loads(Path(RULES).read_text(encoding="utf-8")))
        conf["for"] = "BENCH"
        try:
            res = filer(todo, conf)
        except Exception as e:  # noqa: BLE001 - a filing outage retries next pass; the log line is already out
            res = {a["name"]: "%s: %s" % (type(e).__name__, str(e)[:200]) for a in todo}
        for a in todo:
            err = res.get(a["name"], "no answer from the filer")
            seat = a.get("seat")
            if seat in open_:
                open_[seat]["error"] = err
                if err is None:
                    open_[seat]["filed"] = True
                    filed[a["name"]] = OW.iso(now)
                elif not a["reopen"]:
                    filed.setdefault(a["name"], None)   # a spawn that failed may mean it exists: the next try reopens
    line = "%d request(s) read, %d unmatched, %d incident(s) open" % (len(rows), len(due), len(open_))
    report = {"t": now, "at": OW.iso(now), "line": line, "journal": blind or "read", "armed_at": state["armed_at"],
              "open": open_, "unmatched": due}
    OW_atomic(Path(out_dir) / "restart_reconcile.json", report)
    return report


def OW_atomic(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def main(argv=None, filer=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["run"])
    ap.add_argument("--no-file", action="store_true", help="read and report; tell nobody, file nothing, save nothing")
    a = ap.parse_args(argv)
    d = OW.ops_dir()
    d.mkdir(parents=True, exist_ok=True)
    sp = d / "restart_reconcile_state.json"
    with open(d / "restart_reconcile.lock", "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("restart_reconcile: another pass is running")
            return 0
        saved = OW.read_json(sp) if sp.exists() else {}
        if not isinstance(saved, dict):
            raise SystemExit("restart_reconcile: %s is unreadable: refusing to forget open incidents" % sp)
        sch = json.loads(Path(os.environ.get("RM_RESTART_RECONCILE_SCHEDULE") or SCHEDULE).read_text(encoding="utf-8"))
        if a.no_file:
            lim = limits(sch)
            rows = read_requests(doorbell.state_dir())
            print(json.dumps(join(rows, read_journal(doorbell.state_dir())[0], time.time(), lim,
                                  saved.get("armed_at", time.time() - lim["restart_reconcile_lookback_s"])), indent=1))
            return 0
        rep = run_pass(time.time(), doorbell.state_dir(), sch, saved, filer or OW.real_filer, d)
        OW_atomic(sp, saved)
    print("restart_reconcile: " + rep["line"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
