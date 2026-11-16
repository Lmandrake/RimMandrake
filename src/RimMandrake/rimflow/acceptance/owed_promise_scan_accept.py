#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_SHOW_UNTRACKED_PROMISES_NEXT_PROMPT_FILE_AT_KILL (spec:
design/specs/2026-11-15-conductor-restart-loses-nothing.md §3 E2 as amended by §4, and §5 ticket 2). Written by the
filing seat; the builder does not edit it (a wrong clause goes to the Conductor).

    python3 src/RimMandrake/rimflow/acceptance/owed_promise_scan_accept.py     # exit 0 and "PASS 21/21" when built

THE CONTRACT (advisory first: nothing blocks a turn; GPT's read, §4)
  src/RimMandrake/rimflow/promise_scan.py
    scan(text, owed_ids=()) -> list of the promise sentences in `text` that name no id in `owed_ids`
    CLI: promise_scan.py --text-file F [--owed-ids ID,ID]   prints `PROMISE: <sentence>` per hit; exit 1 if any, 0 if none
  A promise is a sentence in which the Conductor commits itself to a future act or leaves one of its own acts
  unfinished: "I will / I'll …", "When … I will …", "The next window will / should …", "This one is mine",
  "… not launched / not yet launched / never written / still owed / I have not ruled", or a question to him that
  ends the reply. Matching is PER SENTENCE (a promise naming an open owed id is tracked; a target item's id alone is not:
  the T16 loss named its item and was still lost).
  Not promises: past-tense reports ("I launched", "I filed"), text quoted from him or from a reprint (a `>` block,
  the wake's `<<< … >>>` reprint of the old reply), a sentence about someone else's run ("The helper will report"),
  and "Nothing is waiting on you".
  Wiring (static checks): .claude/hooks/conductor_goodbye.py (the per-prompt notice) imports promise_scan, and so does
  src/RimMandrake/rimflow/seat_restart.py (at a backstop kill the last reply's hits are filed as `kind: owed` items
  titled `UNTRACKED promise: <sentence>`; a backstop is never refused for them).
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RIMFLOW, "..", "..", ".."))
sys.path.insert(0, RIMFLOW)
TOTAL = 21
RESULTS = []
OWED = "RIMMANDRAKE_LAUNCH_FLOWWORKS_REALIGNMENT_WHEN_SLOT_FREES"
TARGET = "RIMMANDRAKE_REALIGN_FLOWWORKS_PROOFS_AFTER_UNDER_LIQUID_LAW"

# measured sentences from the 7-day census (spec §1), each a promise the next window lost or acted on late
POSITIVE = [
    "When one of those slots frees I will launch the FlowWorks proof realignment, now that the water pass is done.",
    "Pyrelands, six gaps' live halves: undecided. This one is mine; I have not ruled on it yet.",
    "The one-page owner summary of the pipeline review was never written.",
    "The Lodestar ledger step for the Augur work was skipped, because the ticket tool hung, and is still owed.",
    "Still not launched: the water status-doc correction and the even-step fix.",
    "I'll have the count for you in the morning.",
    "The next window will put its card to you.",
    "I will have the policy written that way after the switch unless you say otherwise.",
    "When one of those slots frees I will launch the realignment (`%s`)." % TARGET,
]
NEGATIVE = [
    "I launched the realignment at 4:50 PM PST (`rm-detached-bench-x-1794790000`).",
    "I filed it as `%s` and published it." % OWED,
    "> I will be back in an hour.",
    "Last reply from the old window: <<< I will launch the realignment when a slot frees. >>>",
    "Nothing is waiting on you right now.",
    "The helper will report when it ends.",
    "When one of those slots frees I will launch the FlowWorks proof realignment (`%s`)." % OWED,
]


def check(ok, what):
    RESULTS.append((bool(ok), what))


def main():
    try:
        import promise_scan
    except Exception as e:                                   # not built yet
        promise_scan = None
        check(False, "promise_scan imports (%s)" % e)
    else:
        check(True, "promise_scan imports")
    for s in POSITIVE:
        got = promise_scan.scan(s, owed_ids=(OWED,)) if promise_scan else None
        check(got and len(got) == 1, "promise found: %s" % s[:70])
    for s in NEGATIVE:
        got = promise_scan.scan(s, owed_ids=(OWED,)) if promise_scan else None
        check(got == [], "not a promise or already tracked: %s" % s[:70])
    # a reply ending in a question to him is a promise (an ask he may answer after the window is gone)
    q = "The timer that tracks GPT's usage has been off since about Nov 6. Should I turn it back on?"
    got = promise_scan.scan(q) if promise_scan else None
    check(got and any("turn it back on" in g for g in got), "a closing question to him is caught")
    # the CLI, on a mixed reply
    tmp = tempfile.mkdtemp(prefix="promise_scan_")
    f = os.path.join(tmp, "reply.md")
    open(f, "w").write("Done: I published `abc1234`.\n\n" + POSITIVE[0] + "\n\n" + NEGATIVE[6] + "\n")
    r = subprocess.run([sys.executable, os.path.join(RIMFLOW, "promise_scan.py"), "--text-file", f,
                        "--owed-ids", OWED], capture_output=True, text=True, timeout=60)
    hits = [l for l in r.stdout.splitlines() if l.startswith("PROMISE: ")]
    check(r.returncode == 1 and len(hits) == 1 and "slots frees" in hits[0],
          "CLI: exit 1 and exactly one PROMISE line on a mixed reply (got rc %s, %d lines)" % (r.returncode, len(hits)))
    hook = open(os.path.join(REPO, ".claude/hooks/conductor_goodbye.py"), encoding="utf-8").read()
    rs = open(os.path.join(RIMFLOW, "seat_restart.py"), encoding="utf-8").read()
    check("promise_scan" in hook, "the per-prompt notice hook uses promise_scan")
    check("promise_scan" in rs and "UNTRACKED promise" in rs,
          "seat_restart files a backstop kill's untracked promises as owed items")
    passed = sum(ok for ok, _ in RESULTS)
    for ok, what in RESULTS:
        print("%s  %s" % ("ok  " if ok else "FAIL", what))
    print("%s %d/%d" % ("PASS" if passed == TOTAL == len(RESULTS) else "FAIL", passed, TOTAL))
    return 0 if passed == TOTAL == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
