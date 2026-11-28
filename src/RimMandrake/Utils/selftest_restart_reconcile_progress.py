#!/usr/bin/env python3
"""selftest_restart_reconcile_progress: the restart alarm counts a restart lost only when it shows no progress.

Page: design/specs/2026-11-27-restart-alarm-reads-progress/boundary.md. Item OPS_RESTART_UNSTICK_BENCH_YCVY_ZEXY.

The instance (Archmagi, 2026-11-28): a BENCH goodbye was taken at 04:57:04Z, the fresh window 82515ae6 (pid 213270)
was relaunched at 04:57:12Z and wrote its transcript for its whole first turn, which ended at 05:16:43Z;
restart_verified came at 05:17:28Z. The alarm opened an incident at 05:04:29Z. JOURNAL below is the real BENCH
restart_ lines of the Dispatcher journal (the kill's argv cut). TX_TIMES is the real time of every main-chain record of
that transcript up to the verify, as offsets from its first record, with its kind (u user, t tool call, e end_turn).
The replay runs the real run_pass, pass by pass, on files written as the clock reaches them; the fresh window's session
file names this process, so the real window_alive reads it alive.

Class guard: red on the parent (an incident at 05:04:29Z), green on the fix. Two planted cases stay incidents: a fresh
window that is alive and silent, and no fresh window (no relaunch line; a relaunch line whose window is gone).
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
TMP = Path(tempfile.mkdtemp(prefix="selftest_restart_reconcile_progress_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RM_DISPATCHER_STATE"] = str(TMP / "disp")
os.environ["CLAUDE_CONFIG_DIR"] = str(TMP / "claude")
import ops_watch as OW  # noqa: E402
import restart_reconcile as RR  # noqa: E402
import seat_restart as SR  # noqa: E402

FAILS = []
SHIPPED = json.loads((HERE.parent / "rimflow/dispatcher_schedule.json").read_text(encoding="utf-8"))
# the numbers shipped when the instance happened, pinned: the owner may tune the shipped ones
PINNED = dict(SHIPPED, restart_reconcile_s=600, restart_reconcile_held_s=3900, restart_reconcile_hold_fresh_s=480,
              restart_reconcile_pass_s=120, restart_reconcile_slack_s=60, restart_reconcile_lookback_s=86400)
LIM = RR.limits(PINNED)
FIRE = LIM["restart_reconcile_s"] - LIM["restart_reconcile_pass_s"] - LIM["restart_reconcile_slack_s"]
CLONE = PINNED["seats"]["BENCH"]["clone"]
OLD, NEW = "aede46da-fff8-497d-b7fe-e228c1816fe6", "82515ae6-5d0d-4415-a27d-f670c2d31480"

JOURNAL = [
    {"at": "2026-11-28T04:49:47Z", "do": "restart_cancel", "result": None, "seat": "BENCH", "ticket": None,
     "why": "input after the goodbye (any input cancels a Conductor restart): attachment "},
    {"at": "2026-11-28T04:51:53Z", "do": "restart_request", "result": "started by the Dispatcher", "seat": "BENCH",
     "session_id": OLD, "synthetic": True, "why": "hard context limit: 414776 tokens >= 400000"},
    {"at": "2026-11-28T04:51:53Z", "do": "restart_hold", "result": None, "seat": "BENCH", "why": "grace: 20 s left"},
    {"at": "2026-11-28T04:53:59Z", "do": "restart_cancel", "result": None, "seat": "BENCH", "ticket": None,
     "why": "new input in the window at 2026-11-28T04:53:25Z, after the request"},
    {"at": "2026-11-28T04:56:04Z", "do": "restart_request", "result": "started by the Dispatcher", "seat": "BENCH",
     "session_id": OLD, "synthetic": True, "why": "hard context limit: 435839 tokens >= 400000"},
    {"at": "2026-11-28T04:56:04Z", "do": "restart_hold", "result": None, "seat": "BENCH", "why": "grace: 20 s left"},
    {"at": "2026-11-28T04:57:04Z", "do": "restart_request", "req_ts": 1795841823.5740216, "result": "request taken",
     "seat": "BENCH", "session_id": OLD, "ticket": "GOODBYE",
     "why": "the seat's own request joins the forced restart: goodbye"},
    {"at": "2026-11-28T04:57:04Z", "do": "restart_kill", "gen": "5ceed8087795", "pid": 1668085,
     "result": "killed pid 1668085 (SIGTERM)", "seat": "BENCH", "session_id": OLD, "session_name": "CONDUCTOR",
     "ticket": "GOODBYE", "why": "request: grace over, nothing held, window quiet"},
    {"at": "2026-11-28T04:57:12Z", "do": "restart_relaunched", "result": None, "seat": "BENCH", "session_id": NEW,
     "ticket": "GOODBYE", "why": "new BENCH window (in-tile) 5 s after the kill"},
    {"at": "2026-11-28T05:17:28Z", "do": "restart_verified", "evidence": "fresh BENCH window %s (pid 213270) ended its "
     "first turn at 2026-11-28T05:16:43Z" % NEW, "note": False, "result": None, "seat": "BENCH", "ticket": "GOODBYE"},
]
TX_BASE = 1795841832.3
TX_TIMES = (
    "0u 5t 7t 7t 22u 22u 26t 28t 28u 33t 33u 36t 38t 38u 40t 53u 68t 73t 73t 122u 122u 67u 129t 131t 135u 141t 144t "
    "145u 150t 152t 153u 159t 159u 168t 169t 177u 167u 184t 186t 191u 197t 200t 201u 207t 210t 211u 215t 220t 225u "
    "232t 235t 263u 269t 270t 272u 277t 278t 280u 286t 290t 312u 323t 325t 328u 332t 332u 336t 336u 340t 342t 342u "
    "346t 347t 347u 351t 351u 354t 356t 356u 369t 374t 374u 407t 408t 409u 414t 414u 420t 426t 432u 447t 451t 451u "
    "476t 479t 481u 487t 513t 513u 514t 516u 508u 525t 529t 537u 543t 560u 563t 566t 566u 572t 572u 576t 582t 595u "
    "601t 689u 694t 702t 703u 713t 714u 730t 736t 737u 755t 757t 760u 784t 817t 818u 823t 840u 846t 860u 864t 864u "
    "868t 868u 873t 873u 881t 949u 957t 960t 1041u 1047t 1047t 1050t 1078u 1079u 1084t 1087t 1089u 1094t 1112u 1150e "
    "1171e 1199u 1207t 1208t 1211u").split()
ALARM_AT = OW.epoch("2026-11-28T05:04:29Z")          # the real pass that opened the incident
VERIFIED_AT = OW.epoch("2026-11-28T05:17:28Z")
PASSES = [ALARM_AT + 60 * k for k in range(-7, 14)]   # 04:57:29Z .. 05:17:29Z, one per metronome beat


def check(ok, name):
    print("  %s %s" % ("ok  " if ok else "FAIL", name))
    if not ok:
        FAILS.append(name)


def tx_records():
    out = []
    for w in TX_TIMES:
        t, k = TX_BASE + float(w[:-1]), w[-1]
        if k == "u":
            out.append((t, {"type": "user", "timestamp": _iso(t),
                            "message": {"role": "user", "content": [{"type": "tool_result", "content": "ok"}]}}))
        else:
            out.append((t, {"type": "assistant", "timestamp": _iso(t), "message": {
                "role": "assistant", "stop_reason": "end_turn" if k == "e" else "tool_use",
                "content": [{"type": "text", "text": "done"}] if k == "e" else [{"type": "tool_use", "name": "Bash"}],
                "usage": {"input_tokens": 10, "cache_read_input_tokens": 1000}}}))
    return sorted(out, key=lambda x: x[0])


def _iso(t):
    import datetime
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def my_birth(pid):
    born, why = SR.proc_birth(pid)
    assert why is None and born is not None, "cannot read this process's birth: %r" % why
    return born


def dead_pid():
    p = subprocess.Popen(["true"])
    p.wait()
    return p.pid


class Filer:
    def __init__(self):
        self.todo = []

    def __call__(self, todo, conf):
        self.todo.extend(todo)
        return {a["name"]: None for a in todo}


def replay(name, journal=JOURNAL, tx_until=None, window="alive", sid=NEW):
    """Run the real pass at every beat; -> [(pass time, title)] of each incident opened. Files appear as the clock
    reaches them: journal lines at their time, transcript records at theirs (cut at tx_until)."""
    root = TMP / name / "disp"
    (root / "restart" / "done").mkdir(parents=True)
    home = TMP / name / "claude"
    os.environ["CLAUDE_CONFIG_DIR"] = str(home)
    (home / "sessions").mkdir(parents=True)
    pdir = Path(os.path.dirname(SR.transcript_path(CLONE, sid)))
    pdir.mkdir(parents=True)
    out = TMP / name / "ops"
    sch = json.loads(json.dumps(PINNED))
    sch["seat_restart"]["seats"]["BENCH"]["seat_log"] = str(TMP / name / "log.md")
    if window != "none":
        pid = os.getpid() if window == "alive" else dead_pid()
        born = my_birth(os.getpid()) if window == "alive" else 1
        (home / "sessions" / ("%d.json" % pid)).write_text(json.dumps({
            "pid": pid, "sessionId": sid, "cwd": CLONE, "name": "CONDUCTOR", "procStart": str(born),
            "startedAt": int(TX_BASE * 1000), "kind": "interactive"}), encoding="utf-8")
    recs = tx_records()
    state = {"armed_at": OW.epoch("2026-11-28T04:40:00Z")}
    filer = Filer()
    opened = []
    for now in PASSES:
        with open(root / "journal.jsonl", "w", encoding="utf-8") as f:
            f.writelines(json.dumps(j) + "\n" for j in journal if OW.epoch(j["at"]) <= now)
        with open(pdir / ("%s.jsonl" % sid), "w", encoding="utf-8") as f:
            f.writelines(json.dumps(r) + "\n" for t, r in recs if t <= now and (tx_until is None or t <= tx_until))
        before = set(state.get("open", {}))
        RR.run_pass(now, str(root), sch, state, filer, out)
        for seat in set(state.get("open", {})) - before:
            opened.append((now, seat, state["open"][seat]["title"]))
    return opened


def show(name, got):
    print("  %s: incidents opened %r" % (name, [(OW.iso(t), s, x) for t, s, x in got]))


def t_alive_and_writing_is_no_incident():
    """The instance: the fresh window is alive and writes its transcript for its whole 1,176 s first turn."""
    got = replay("instance")
    show("instance", got)
    check(not got, "alive-and-writing-is-no-incident: the real 2026-11-28 BENCH restart opens no incident (parent: "
          "one at 05:04:29Z)")
    check(not [g for g in got if g[0] == ALARM_AT], "alive-and-writing-is-no-incident: no incident at 05:04:29Z")


def t_alive_and_silent_is_an_incident():
    """Planted: the fresh window is alive and goes silent 60 s after its relaunch; no restart_verified ever comes."""
    silent_from = OW.epoch("2026-11-28T04:58:12Z")
    got = replay("silent", journal=[j for j in JOURNAL if j["do"] != "restart_verified"], tx_until=silent_from)
    show("silent", got)
    last_rec = max(t for t, _ in tx_records() if t <= silent_from)
    check(len(got) == 1 and got[0][1] == "BENCH", "alive-and-silent-is-an-incident: one BENCH incident opens")
    check(bool(got) and got[0][0] - last_rec <= LIM["restart_reconcile_s"],
          "alive-and-silent-is-an-incident: told inside restart_reconcile_s of the last record")
    check(bool(got) and got[0][0] - last_rec >= FIRE,
          "alive-and-silent-is-an-incident: not before the fire time of silence")


def t_no_fresh_window_is_an_incident():
    """Planted: no relaunch line at all; a relaunched window that is gone; a window relaunched before the request."""
    got = replay("nowindow", journal=[j for j in JOURNAL if j["do"] not in ("restart_verified", "restart_relaunched")],
                 tx_until=0, window="none")
    show("no window", got)
    check(len(got) == 1 and got[0][0] == ALARM_AT, "no-fresh-window-is-an-incident: no relaunch line opens the "
          "incident at 05:04:29Z, as before")
    got = replay("gone", journal=[j for j in JOURNAL if j["do"] != "restart_verified"], window="dead")
    show("gone", got)
    check(len(got) == 1 and got[0][0] == ALARM_AT, "no-fresh-window-is-an-incident: a relaunched window that is gone "
          "opens the incident at 05:04:29Z")
    # the request is never acted on (no kill, no relaunch after it); the window that asked is itself the fresh window
    # of an earlier restart, alive and writing. Its earlier relaunch line is no progress of this request.
    stale = [{"at": "2026-11-28T03:00:00Z", "do": "restart_relaunched", "result": None, "seat": "BENCH",
              "session_id": OLD, "ticket": "GOODBYE", "why": "new BENCH window (in-tile) 5 s after the kill"}] + [
        j for j in JOURNAL if j["do"] not in ("restart_verified", "restart_relaunched", "restart_kill")]
    got = replay("stale", journal=stale, sid=OLD)
    show("stale relaunch", got)
    check(len(got) == 1 and got[0][0] == ALARM_AT, "no-fresh-window-is-an-incident: a window relaunched before the "
          "request is no fresh window of it, however it writes")


def main():
    for t in (t_alive_and_writing_is_no_incident, t_alive_and_silent_is_an_incident, t_no_fresh_window_is_an_incident):
        t()
    print("selftest_restart_reconcile_progress: %s" % ("PASS" if not FAILS else "FAIL (%d): %s" % (len(FAILS), FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
