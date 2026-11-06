#!/usr/bin/env python3
"""selftest_wrapup_session_claims.py — the wrap-up's session census counts the session's OWN claims, not its seat's.

WRAPUP_CLAIMS_FIX_ROBOT_BLAMED_ON_WINDOW: session a5166def's census listed ten Relentless supervisor starts (seat
BENCH, the key it shares with the Conductor's windows) as the window's own still-doing claims, so
wrapup.debris_standing stayed > 0 and its incident open. The fix: cli stamps `session` (CLAUDE_CODE_SESSION_ID) on
every claim/start a Claude window writes (never in a Relentless process), and wrapup.claims_of counts an item only
when the session's own event took it and its latest claim/start is still its own.

Cases:
  stamp      cli._stamp_session stamps claim/start from CLAUDE_CODE_SESSION_ID; not other verbs, not a malformed
             id, not a Relentless process (RIMFLOW_BRIDGE_SEAT=RELENTLESS)
  cli        a real `rimflow claim` in a temp ledger writes `session`; model accepts it (UNIVERSAL_FIELDS)
  instance   the a5166def shape: ten same-seat supervisor starts + one window claim -> one claims row, not eleven
  windows    another window's stamped claim on the same seat is not ours; a stamped start by us is
  taken      an item we claimed and the supervisor (or another session) started after us is carried by its taker
  legacy     unstamped lines keep the old rule (seat, not supervisor's start, not a role run)
  remeasure  a filed session claims row whose item the supervisor took stops standing (row_standing uses the key)
  mutation   without the session filter (seat rule alone) the instance yields 11 rows: the test can fail
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CLI = os.path.join(HERE, "cli.py")
sys.path.insert(0, HERE)
os.environ["RM_UNDER_SELFTEST"] = "1"
import cli  # noqa: E402
import model  # noqa: E402
import wrapup  # noqa: E402

FAILS = []
W = wrapup.RELENTLESS_START_WHY
ME, OTHER = "a5166def-0000-4000-8000-000000000001", "b7777777-0000-4000-8000-000000000002"
SINCE = 1793750400      # 2026-11-04T00:00:00Z


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def ev(verb, iid, ts="2026-11-04T01:00:00Z", seat="BENCH", **kw):
    return dict({"seat": seat, "event": verb, "id": iid, "ts": ts}, **kw)


def ids(evs, states, session=ME, since=SINCE):
    return [i for i, _ in wrapup.claims_of(evs, states, "BENCH", since, session)]


def stamp_cases():
    base = {"CLAUDE_CODE_SESSION_ID": ME}
    e = cli._stamp_session({"event": "claim", "seat": "BENCH", "id": "X"}, base)
    check(e.get("session") == ME, "stamp: a window's claim carries its session id")
    e = cli._stamp_session({"event": "start", "seat": "BENCH", "id": "X"}, base)
    check(e.get("session") == ME, "stamp: a window's start carries its session id")
    e = cli._stamp_session({"event": "note", "seat": "BENCH", "id": "X"}, base)
    check("session" not in e, "stamp: other verbs are untouched")
    e = cli._stamp_session({"event": "claim", "seat": "BENCH", "id": "X"}, {"CLAUDE_CODE_SESSION_ID": "bad id/../x"})
    check("session" not in e, "stamp: a malformed id is not stamped")
    e = cli._stamp_session({"event": "claim", "seat": "BENCH", "id": "X"}, {})
    check("session" not in e, "stamp: no session id, no stamp")
    e = cli._stamp_session({"event": "start", "seat": "BENCH", "id": "X"},
                           dict(base, RIMFLOW_BRIDGE_SEAT="RELENTLESS"))
    check("session" not in e, "stamp: a Relentless process never stamps a window's session")
    check("session" in model.UNIVERSAL_FIELDS, "model: session is a universal field")


def cli_case():
    tmp = tempfile.mkdtemp(prefix="rm_wrapup_sess_")
    try:
        e = {k: v for k, v in os.environ.items()
             if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "RM_ROLE_UNIT", "RIMFLOW_BRIDGE_SEAT")}
        e.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(tmp, "items"),
                 RIMFLOW_PROBE="no-reading", RIMFLOW_SEAT="BUILD", CLAUDE_CODE_SESSION_ID=ME)
        out = []
        for args in (["file", "WRAPUP_SESSION_STAMP_PROBE_FIXTURE", "--for", "BUILD", "--title", "t"],
                     ["claim", "WRAPUP_SESSION_STAMP_PROBE_FIXTURE"]):
            p = subprocess.run([sys.executable, CLI] + args, capture_output=True, text=True, env=e, cwd=REPO,
                               timeout=120)
            out.append(p.returncode)
            if p.returncode:
                print("  %s: %s" % (args[0], (p.stderr or p.stdout).strip()[-300:]))
        lines = []
        for dp, _, fs in os.walk(tmp):
            for f in fs:
                if f.endswith(".jsonl"):
                    with open(os.path.join(dp, f), encoding="utf-8") as fh:
                        lines += [json.loads(x) for x in fh if x.strip()]
        cl = [x for x in lines if x.get("event") == "claim"]
        fl = [x for x in lines if x.get("event") == "file"]
        check(out == [0, 0] and cl and cl[-1].get("session") == ME,
              "cli: a real claim writes session=%s (rc %r, %r)" % (ME[:8], out, cl[-1:] and cl[-1].get("session")))
        check(fl and "session" not in fl[-1], "cli: a file event carries no session")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def instance():
    sup = [ev("start", "SUP%d" % n, why=W) for n in range(10)]
    mine = [ev("claim", "MINE", why="x", session=ME)]
    states = dict({"SUP%d" % n: "doing" for n in range(10)}, MINE="doing")
    got = ids(sup + mine, states)
    check(got == ["MINE"], "instance: ten supervisor starts are not the window's claims: %r" % got)
    # an unstamped same-seat start under another why is legacy: the old seat rule still counts it (a pre-stamp line
    # may be the window's own; the wrap-up never clears on ignorance)
    odd = [ev("start", "SUPX", why="relentless supervisor resumes the item")]
    got = ids(odd + mine, dict(states, SUPX="doing"))
    check("SUPX" in got, "legacy: an unstamped non-supervisor same-seat start still counts (old rule kept): %r" % got)
    # mutation: the seat rule alone counts all eleven
    real = wrapup.own_event
    wrapup.own_event = lambda e, seat, session=None: e.get("seat") == seat
    try:
        n = len(ids(sup + mine, states))
    finally:
        wrapup.own_event = real
    check(n == 11, "mutation: with a seat-only own_event the census files %d rows (11 expected): the test can fail" % n)


def windows_and_taken():
    evs = [ev("claim", "THEIRS", why="x", session=OTHER),
           ev("start", "OURS", why="x", session=ME),
           ev("claim", "TAKEN", why="x", session=ME),
           ev("start", "TAKEN", ts="2026-11-04T02:00:00Z", why=W),
           ev("claim", "STOLEN", why="x", session=ME),
           ev("start", "STOLEN", ts="2026-11-04T02:00:00Z", why="x", session=OTHER),
           ev("claim", "BACK", why=W),
           ev("start", "BACK", ts="2026-11-04T02:00:00Z", why="a window took it over", session=ME),
           ev("claim", "ROLE", why="x", role_unit="rm-role-x-1"),
           ev("claim", "OLD", ts="2020-01-01T00:00:00Z", why="x", session=ME),
           ev("claim", "DONE", why="x", session=ME)]
    states = {k: "doing" for k in ("THEIRS", "OURS", "TAKEN", "STOLEN", "BACK", "ROLE", "OLD")}
    states["DONE"] = "done"
    got = ids(evs, states)
    check(got == ["BACK", "OURS"], "windows/taken: only our own, still ours, still doing, in session: %r" % got)
    got = ids(evs, states, session=OTHER)
    check(got == ["STOLEN", "THEIRS"], "windows: the other session sees its own: %r" % got)


def remeasure():
    class Fake:
        def __init__(self, evs, states):
            self.evs, self.states = evs, states

        def doing_claims(self, seat, since, session=None):
            return wrapup.claims_of(self.evs, self.states, seat, since, session)

    evs = [ev("claim", "MINE", why="x", session=ME), ev("start", "MINE", ts="2026-11-04T03:00:00Z", why=W)]
    rec = {"kind": "session", "key": ME, "seat": "BENCH"}
    row = {"kind": "claims", "what": "MINE"}
    check(not wrapup.row_standing(Fake(evs, {"MINE": "doing"}), row, rec),
          "remeasure: a filed row stops standing once the supervisor takes the item")
    check(wrapup.row_standing(Fake(evs[:1], {"MINE": "doing"}), row, rec),
          "remeasure: our own still-doing claim keeps standing")
    other = dict(rec, key=OTHER)
    check(not wrapup.row_standing(Fake(evs[:1], {"MINE": "doing"}), row, other),
          "remeasure: another session's record never stands on our claim")


def main():
    stamp_cases()
    cli_case()
    instance()
    windows_and_taken()
    remeasure()
    print("selftest_wrapup_session_claims: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
