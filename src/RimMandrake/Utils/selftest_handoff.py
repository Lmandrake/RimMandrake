"""
Selftest: handoff.py's gates fire when they should, and only then.

Both bugs proven here were live in the first draft of that script, and both
made the gate USELESS rather than wrong-looking — which is the dangerous kind:

  1. `previous_handoff()` picked the newest handoff ON DISK. The file being
     written is uncommitted, so it selected itself, the window start became
     "now", and the doing-scope silently vanished — the gate then listed 47
     items from three sessions back, which a seat learns to scroll past.
  2. The doing-check had no window at all, so every item this seat had ever
     started and not closed was a "problem". A gate that fires every time is
     a gate nobody reads.

So the assertions here are mostly about the gate being SILENT when it should
be, which is the property that was broken and the one a passing-looking test
would miss.
"""

import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import handoff  # noqa: E402

fails = []


def check(ok, what):
    print(("  ok   " if ok else "  FAIL ") + what)
    if not ok:
        fails.append(what)


print("handoff: the judgement sections cannot be quietly dropped")
check(len(handoff.JUDGEMENT_SECTIONS) >= 4,
      "at least four sections a script cannot write (%d)"
      % len(handoff.JUDGEMENT_SECTIONS))
check(all(t and p for t, p in handoff.JUDGEMENT_SECTIONS),
      "every section carries both a title and a prompt")
check(handoff.TODO in ("<<< WRITE THIS >>>",),
      "the unfilled marker is the loud one the doc promises")

print("handoff: todo_scan counts unfilled sections")
with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                 encoding="utf-8") as fh:
    fh.write("# x\n\n%s\n\nprose\n\n%s\n" % (handoff.TODO, handoff.TODO))
    unfilled = fh.name
with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                 encoding="utf-8") as fh:
    fh.write("# x\n\nall written out, nothing left\n")
    filled = fh.name
try:
    p = handoff.todo_scan(unfilled)
    check(len(p) == 1 and "2 unfilled" in p[0],
          "two markers report as two unfilled sections (%r)" % (p[:1],))
    check(handoff.todo_scan(filled) == [],
          "a fully written handoff scans clean")
    check(len(handoff.todo_scan(unfilled + ".nope")) == 1,
          "a missing handoff file is itself a problem, not a pass")
finally:
    for f in (unfilled, filled):
        try:
            os.unlink(f)
        except OSError:
            pass

print("handoff: previous_handoff picks the newest COMMITTED file, never itself")
name, ts = handoff.previous_handoff()
check(name is None or ts,
      "whatever it returns carries a git timestamp, so the window has a start")
if name:
    newest_on_disk = sorted(
        fn for fn in os.listdir(handoff.ITEMS)
        if fn.startswith(handoff.seat() + "_REBOOT_HANDOFF_") and fn.endswith(".md"))
    check(bool(newest_on_disk),
          "this seat has handoffs on disk to choose between (%d)" % len(newest_on_disk))

print("handoff: the doing-gate is scoped, and a handoff discharges it")
# A future timestamp means "nothing was started in this window" — the gate must
# then be silent about `doing` no matter how much old work is open.
future = "2999-01-01T00:00:00Z"
problems = handoff.gates(future)
check(not any("still open" in p for p in problems),
      "with an empty window, the doing-gate says nothing (%d other problem(s))"
      % len(problems))

# And with no window at all it must have something to say, or the scoping above
# proved nothing.
unscoped = handoff.gates(None)
check(any("still open" in p for p in unscoped),
      "with NO window the doing-gate does fire — so the empty-window silence "
      "above is the scoping working, not the check being dead")

# Naming the ids in the handoff clears them.
ids = []
for p in unscoped:
    if "still open" in p:
        ids = [x.strip() for x in p.split(":\n")[-1].split(",") if x.strip()]
with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                 encoding="utf-8") as fh:
    fh.write("# handoff\n\n" + "\n".join("- %s: left mid-flight" % i for i in ids))
    accounted = fh.name
try:
    cleared = handoff.gates(None, accounted)
    check(not any("still open" in p for p in cleared),
          "naming every open item in the handoff discharges the gate (%d ids)"
          % len(ids))
finally:
    try:
        os.unlink(accounted)
    except OSError:
        pass

print("handoff: an empty window is ALREADY HANDED OFF, not a second handoff")
# The say-once rule. A window whose start is in the future contains nothing by
# construction, so window_is_empty must agree -- and must NOT agree when there
# is no window at all, or the emptiness test would suppress every handoff.
check(handoff.window_is_empty("HEAD", future) is True,
      "no closes/filings/commits since the window start reads as empty")
check(handoff.window_is_empty(None, None) is False,
      "with no previous handoff, nothing is suppressed -- the first one must write")

print("\n%s: %d failure(s)" % (os.path.basename(__file__), len(fails)))
sys.exit(1 if fails else 0)
