#!/usr/bin/env python3
"""hunt_open.py -- a hunt (a kind C search for a fault that shows only sometimes) never opens silently (owner, 2026-11-23,
design/RimMandrake/standing_rulings.md §Live tests have three kinds, section 5). One command tells the Conductor what
happened, why it matters, the next step that tells two causes apart, and what that step costs.

  python3 src/RimMandrake/rimflow/hunt_open.py ITEM --what "..." --why-it-matters "..." --next-step "..." --cost "..."

It writes one HUNT OPENED line (RAISE FIRST) in the Conductor log, then the same text as a note on ITEM.
Exit 0 both written; 2 a field is blank or missing, nothing written; 3 the log line was not written, no note tried;
4 the log line stands and the note did not land (the cause is printed; write the note by hand, not this command again).
RM_HUNT_OPEN_NO_NOTE=1 (tests) writes no note and says so. Page: design/specs/2026-11-23-live-kinds-exit-reader/boundary.md."""
import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FIELDS = ("what", "why_it_matters", "next_step", "cost")


def main(argv=None, runner=subprocess.run):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("item")
    ap.add_argument("--what", required=True, help="what happened")
    ap.add_argument("--why-it-matters", required=True, help="what it means for the player")
    ap.add_argument("--next-step", required=True, help="the next step that tells two causes apart")
    ap.add_argument("--cost", required=True, help="what that step costs")
    ap.add_argument("--seat", default="BENCH")
    a = ap.parse_args(argv)
    val = {k: " ".join(str(getattr(a, k)).split()) for k in FIELDS}
    blank = [k for k in ("item",) + FIELDS if not (a.item.strip() if k == "item" else val[k])]
    if blank:
        print("REFUSED: blank %s; nothing was written. A hunt never opens silently: give every field its text." % ", ".join(
            "ITEM" if b == "item" else "--" + b.replace("_", "-") for b in blank))
        return 2
    text = "what happened: %(what)s | why it matters: %(why_it_matters)s | next step: %(next_step)s | cost: %(cost)s" % val
    import detached_helper as D
    try:
        path = D.conductor_line("%s: %s" % (a.item.strip(), text), time.time(), head="HUNT OPENED (RAISE FIRST)")
    except (OSError, RuntimeError) as e:
        print("FAILED: the Conductor log line was not written (%s); no note was tried" % e)
        return 3
    print("HUNT OPENED line written: %s" % path)
    if os.environ.get("RM_HUNT_OPEN_NO_NOTE"):
        print("note NOT written (RM_HUNT_OPEN_NO_NOTE)")
        return 0
    argv2 = [sys.executable, os.path.join(HERE, "cli.py"), "note", a.item.strip(), "--text", "HUNT OPENED: " + text,
             "--seat", a.seat, "--why", "hunt opened", "--publish"]
    try:
        r = runner(argv2, capture_output=True, text=True)
    except OSError as e:
        print("NOTE NOT WRITTEN: %s; the log line stands. Write it: cli.py note %s --text \"HUNT OPENED: ...\"" % (e, a.item))
        return 4
    tail = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-1:]
    if r.returncode != 0:
        print("NOTE NOT LANDED (cli.py note exit %s: %s); the log line stands, so do not run this command again" % (
            r.returncode, "".join(tail)))
        return 4
    print("note on %s: %s" % (a.item.strip(), "".join(tail)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
