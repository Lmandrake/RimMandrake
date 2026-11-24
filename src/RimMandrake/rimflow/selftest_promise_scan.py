#!/usr/bin/env python3
"""Regression checks for promise_scan.py and its reader (RIMMANDRAKE_SHOW_UNTRACKED_PROMISES_NEXT_PROMPT_FILE_AT_KILL):
the per-prompt notice in .claude/hooks/conductor_goodbye.py.
The contract itself is acceptance/owed_promise_scan_accept.py.

    python3 src/RimMandrake/rimflow/selftest_promise_scan.py      # exit 0 and "PASS n/n"
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import promise_scan as PS  # noqa: E402
os.environ.pop("RM_ROLE_UNIT", None)   # the hooks run as the Conductor window; a launched run (RM_ROLE_UNIT) prints nothing

RESULTS = []


def check(ok, what):
    RESULTS.append((bool(ok), what))


def tx(tmp, text):
    p = os.path.join(tmp, "tx.jsonl")
    with open(p, "w") as f:
        f.write(json.dumps({"type": "user", "message": {"content": "status?"}}) + "\n")
        f.write(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}) + "\n")
    return p


def scanner():
    check(PS.scan("I’ll send it after lunch.") == ["I’ll send it after lunch."], "a curly apostrophe is a promise")
    check(PS.scan("Done.\n\n```\nI will run this\n```\n\nNothing else.") == [], "a code block is not the reply's words")
    check(PS.scan("- I will file it.\n- I filed the other.") == ["I will file it."], "bullets are sentences of their own")
    check(PS.scan("Is it done? Yes, it landed at 3 PM.") == [], "a question answered in the reply is not a closing ask")
    check(PS.scan("") == [] and PS.scan(None) == [], "an empty reply has no promise")
    check(PS.scan("I will write it. meanwhile, RIMMANDRAKE_OTHER_OWED waits.", ["RIMMANDRAKE_OTHER_OWED"])
          == ["I will write it."], "another sentence's owed id never tracks a promise")
    check(PS.scan("I will ask Dr. Smith to finish RIMMANDRAKE_OTHER_OWED.", ["RIMMANDRAKE_OTHER_OWED"]) == [],
          "an abbreviation's period does not end the sentence")
    check(PS.scan("I will check whether it is yes or no. RIMMANDRAKE_OTHER_OWED waits.", ["RIMMANDRAKE_OTHER_OWED"])
          == ["I will check whether it is yes or no."], "a sentence ending in 'no.' still ends there")
    check(PS.scan("Run:\n~~~\nI will run it.\n~~~\nDone.") == [], "a ~~~ fence is code")
    own = {"RIMMANDRAKE_LAUNCH_FLOWWORKS_REALIGN_OWED": ("launch the FlowWorks realignment fixer", "")}
    check(PS.scan("When the slot frees I will launch the FlowWorks realignment fixer.", owed_items=own) == [],
          "a promise an open owed item's title covers is silent (owner 2026-11-20)")
    own2 = {"RIMMANDRAKE_OWE_PITS": ("rebuild", "RIMMANDRAKE_PITS_REBUILD_TARGET")}
    check(PS.scan("I will relaunch RIMMANDRAKE_PITS_REBUILD_TARGET tonight.", owed_items=own2) == [],
          "a promise naming the item an open owed item acts on is silent")
    check(PS.scan("I will relaunch RIMMANDRAKE_PITS_REBUILD_TARGET tonight.") != [],
          "the same promise with no owed item still shows (T16)")
    check(PS.scan("I will write the summary for the art judge.", owed_items=own) != [],
          "an unrelated promise still shows beside an owed item")
    check(PS.scan("Ex:\n````\n```\nI will run it.\n```\n````\nDone.") == [], "a longer fence holds a shorter one")


def hook():
    tmp = tempfile.mkdtemp(prefix="promise_hook_")
    p = tx(tmp, "Published `abc1234`.\n\nWhen the slot frees I will launch the FlowWorks realignment.")
    data = json.dumps({"prompt": "how is it going", "session_id": "x", "transcript_path": p})
    env = dict(os.environ, AGENT_SEAT="BENCH")
    r = subprocess.run([sys.executable, os.path.join(REPO, ".claude", "hooks", "conductor_goodbye.py")], input=data,
                       cwd=REPO, env=env, capture_output=True, text=True, timeout=120)
    check(r.returncode == 0 and "NOTE, nothing blocked: 1 sentence(s)" in r.stdout and "I will launch" in r.stdout,
          "the per-prompt notice names the last reply's untracked promise (rc %d)" % r.returncode)
    data = json.dumps({"prompt": "how is it going", "session_id": "x", "transcript_path": os.path.join(tmp, "none")})
    r = subprocess.run([sys.executable, os.path.join(REPO, ".claude", "hooks", "conductor_goodbye.py")], input=data,
                       cwd=REPO, env=env, capture_output=True, text=True, timeout=120)
    check(r.returncode == 0 and "NOTE, nothing blocked" not in r.stdout, "no readable reply prints no promise line, exit 0")


def main():
    scanner()
    hook()
    passed = sum(ok for ok, _ in RESULTS)
    for ok, what in RESULTS:
        print("%s  %s" % ("ok  " if ok else "FAIL", what))
    print("%s %d/%d" % ("PASS" if passed == len(RESULTS) else "FAIL", passed, len(RESULTS)))
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
