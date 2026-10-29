#!/usr/bin/env python3
"""Selftest for conductor_goodbye.py (CONDUCTOR_GOODBYE_DESIGN_FRESH_EACH_TIME).

Covers: a goodbye is the owner's WHOLE message only (case and punctuation ignored); a goodbye inside a longer message
("goodbye to the old pipe system") never fires; only the Conductor window (seat BENCH, session CONDUCTOR) fires; the
printed close-out carries the ledger, promise, log and restart steps; config off or unreadable -> close-out WITHOUT a
restart, said loudly; settings.json wires it. A mutation check proves the cases can tell a substring matcher apart.
Nothing here restarts anything: the hook only prints.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HOOK = HERE / "conductor_goodbye.py"
sys.path.insert(0, str(HERE))
import conductor_goodbye as G  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


with open(ROOT / "src/RimMandrake/rimflow/dispatcher_schedule.json", encoding="utf-8") as f:
    LIVE = json.load(f)
PH = G.phrases(LIVE)

YES = ["goodbye", "Goodbye!", "  bye. ", "BYE", "gn", "GN!", "good night", "Good night!!", "good-night",
       "done for now.", "Done for now", "that's all", "That’s all.", "thats all", "goodbye\n"]
NO = ["goodbye to the old pipe system", "bye the way, check the hose", "ok bye", "that's all for the hose, now do Y",
      "gnome", "", "   ", "done", "good", "good night of testing ahead?", "say goodbye to FOUNDRY",
      "no goodbye yet", "goodbye? not yet", "bye bye pipes 2", "done for now with art; next: hoses"]


def test_phrases():
    check(bool(PH), "the live schedule carries goodbye_phrases (%s)" % PH)
    for p in YES:
        check(G.is_goodbye(p, PH), "whole-message goodbye fires: %r" % p)
    for p in NO:
        check(not G.is_goodbye(p, PH), "not a whole-message goodbye: %r" % p)
    # mutation check: a substring matcher (the bug this test exists to catch) must fail at least one case
    sub = lambda p, ph: any(x in G.norm(p) for x in ph)  # noqa: E731
    caught = [p for p in NO if sub(p, PH)]
    check(len(caught) >= 3, "mutation: a substring matcher is caught by the negative cases (%d: %s)" % (len(caught), caught[:3]))
    loose = lambda p, ph: G.norm(p).split()[:1] and G.norm(p).split()[0] in ph  # noqa: E731
    check(any(loose(p, PH) for p in NO), "mutation: a first-word matcher is caught too")


def test_window_gate():
    sf = {"name": "CONDUCTOR"}
    check(G.is_conductor({"AGENT_SEAT": "BENCH"}, sf, LIVE)[0], "AGENT_SEAT BENCH + session CONDUCTOR -> the Conductor")
    check(G.is_conductor({"AGENT_SEAT": "BENCH"}, {"name": "CONDUCTOR ▶ SOME_ITEM"}, LIVE)[0],
          "a titled CONDUCTOR session still matches")
    check(G.is_conductor({"AGENT_SEAT": "BENCH"}, {"name": "AGENT BENCH"}, LIVE)[0], "the pre-rename alias matches")
    check(not G.is_conductor({"AGENT_SEAT": "FOUNDRY"}, {"name": "AGENT FOUNDRY"}, LIVE)[0], "FOUNDRY never fires")
    check(not G.is_conductor({}, sf, LIVE)[0], "no AGENT_SEAT (a Remote Control spawn, a helper) never fires")
    check(not G.is_conductor({"AGENT_SEAT": "BENCH"}, {"name": "AGENT CONDUCTOR"}, LIVE)[0],
          "the Conductor role's HOLD window name 'AGENT CONDUCTOR' is not the Conductor window")
    ok, why = G.is_conductor({"AGENT_SEAT": "BENCH"}, None, LIVE)
    check(ok and "UNMEASURED" in why, "session file unreadable -> fires, says so (the request re-checks the name)")


def test_message():
    m = G.message(LIVE, ok_why="ok")
    for need in ("--owner-said", "--for OWNER", "--why", "conductor/log.md", "./publish",
                 "seat_restart.py request --seat BENCH", "--fresh", "--reason goodbye", "Closed out:",
                 "nothing you send is lost", "REFUSED"):
        check(need in m, "the close-out names %r" % need)
    off = json.loads(json.dumps(LIVE))
    off["seat_restart"]["seats"]["BENCH"]["enabled"] = False
    m = G.message(off, ok_why="ok")
    check("seat_restart.py request" not in m and "stays open" in m,
          "seat_restart off for BENCH -> close-out without a restart, window stays open")
    m = G.message({}, ok_why="ok")
    check("seat_restart.py request" not in m and "UNREADABLE" in m, "schedule unreadable -> no restart, said loudly")


def run(prompt, env_seat="BENCH"):
    env = dict(os.environ)
    env.pop("RIMFLOW_SEAT", None)
    env["AGENT_SEAT"] = env_seat
    env["CONDUCTOR_GOODBYE_SESSION_NAME"] = "CONDUCTOR"       # test seam: no real session file is read
    p = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"prompt": prompt}), capture_output=True,
                       text=True, env=env, timeout=30)
    return p.returncode, p.stdout


def test_end_to_end():
    rc, out = run("Good night!")
    check(rc == 0 and "GOODBYE" in out and "seat_restart.py request" in out, "e2e: 'Good night!' prints the close-out")
    rc, out = run("goodbye to the old pipe system")
    check(rc == 0 and out == "", "e2e: 'goodbye to the old pipe system' prints nothing (%r)" % out[:80])
    rc, out = run("bye", env_seat="FOUNDRY")
    check(rc == 0 and out == "", "e2e: FOUNDRY saying bye prints nothing")
    p = subprocess.run([sys.executable, str(HOOK)], input="not json", capture_output=True, text=True, timeout=30)
    check(p.returncode == 0 and p.stdout == "", "e2e: unreadable hook input -> silent, exit 0")


def test_wired():
    with open(ROOT / ".claude/settings.json", encoding="utf-8") as f:
        s = json.load(f)
    cmds = [h.get("command", "") for blk in s["hooks"].get("UserPromptSubmit", []) for h in blk.get("hooks", [])]
    check(any("conductor_goodbye.py" in c for c in cmds), "settings.json runs conductor_goodbye.py on UserPromptSubmit")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                check(False, "%s raised %s: %s" % (name, type(e).__name__, e))
    print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    sys.exit(1 if FAILS else 0)
