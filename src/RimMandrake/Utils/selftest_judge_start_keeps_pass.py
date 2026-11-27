#!/usr/bin/env python3
"""Selftest: a judge run that `start`s a built item can still record its criterion pass
(WORLD_FACES_REDRAW_ABYSS_ROT_RUST, 2026-11-27).

The ticket lane's judge brief orders `rimflow start <ID>`, which moves a built or validated item to `doing`. `verify`
refused every criterion pass on a `doing` item ("counts only against a BUILT artifact. Record `implemented` first"),
and a re-`implemented` forgets the item's earlier passes. So a judge's PASS could not be recorded at all.

Promise: a criterion pass on a `doing` item counts when the item was built and the pass names its built sha.
Still refused: a pass on a `doing` item at another sha (the build may be under rework), and a pass on an item that was
never built. Written by the real CLI into a temp ledger (`RIMFLOW_LEDGER`), never the live one.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CLI = os.path.join(REPO, "src", "RimMandrake", "rimflow", "cli.py")
TMP = tempfile.mkdtemp(prefix="selftest_judge_start_keeps_pass.")
fails = []


def check(ok, what):
    print(("  ok   " if ok else "  FAIL ") + what)
    if not ok:
        fails.append(what)


def env():
    e = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "RM_ROLE_UNIT")
         and not k.startswith("GIT_")}
    e.update(RIMFLOW_LEDGER=os.path.join(TMP, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(TMP, "items"),
             RIMFLOW_PROBE="no-reading", RIMFLOW_SCHEDULE=os.path.join(TMP, "no_schedule.json"),
             RIMFLOW_DRIVER_LOCK="", RIMFLOW_BRIDGE_LOCK=os.path.join(TMP, "bridge.lock"), RM_HOST="archmagi",
             RIMFLOW_SEAT="BENCH")
    return e


def rf(*args):
    p = subprocess.run([sys.executable, CLI] + list(args) + ["--why", "selftest_judge_start_keeps_pass"], env=env(),
                       cwd=REPO, capture_output=True, text=True, timeout=1200)  # hang guard: one CLI call is ~2 s
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def state(i):
    rc, out = rf("show", i)
    return out.split("\n")[0].split()[1] if rc == 0 and out.strip() else "UNMEASURED"


# a sha that origin/main holds and that touches more than the ledger (close and implemented refuse a ledger-only one)
base = subprocess.run(["git", "-C", REPO, "merge-base", "HEAD", "origin/main"], capture_output=True, text=True).stdout.strip()
SHA = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%H", base, "--", ".",
                      ":(exclude)infrastructure/state"], capture_output=True, text=True).stdout.strip()
OTHER = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%H", SHA + "^", "--", ".",
                        ":(exclude)infrastructure/state"], capture_output=True, text=True).stdout.strip()
crit = os.path.join(TMP, "crit.txt")
with open(crit, "w") as fh:
    fh.write("A1 L2: a judge rules the faces PASS on in-game captures\n")

JUDGED, REWORK, NEVER = "JUDGESTART_TEST_ITEM_JUDGED", "JUDGESTART_TEST_ITEM_REWORK", "JUDGESTART_TEST_ITEM_NEVER_BUILT"
for i in (JUDGED, REWORK, NEVER):
    rf("file", i, "--for", "BENCH", "--title", "title of " + i)
for i in (JUDGED, REWORK):
    rc, out = rf("implemented", i, "--sha", SHA, "--criteria-file", crit)
    check(rc == 0, "%s implemented at the base sha (rc %d: %s)" % (i, rc, out.strip()[-160:]))
for i in (JUDGED, REWORK, NEVER):
    rf("claim", i)
    rf("start", i)
    check(state(i) == "doing", "%s is doing after the judge's start (reads %s)" % (i, state(i)))


def t_a_pass_at_the_built_sha_on_a_started_built_item_counts():
    rc, out = rf("verify", JUDGED, "--result", "pass", "--config", "selftest", "--criterion", "A1", "--level", "L2",
                 "--sha", SHA, "--evidence", "selftest")
    check(rc == 0, "a pass at the built sha on a started built item is recorded (rc %d: %s)" % (rc, out.strip()[-200:]))
    check(state(JUDGED) == "done", "the last owed criterion passed: the item is done (reads %s)" % state(JUDGED))


def t_a_pass_at_another_sha_or_on_an_unbuilt_item_stays_refused():
    rc, out = rf("verify", REWORK, "--result", "pass", "--config", "selftest", "--criterion", "A1", "--level", "L2",
                 "--sha", OTHER, "--evidence", "selftest")
    check(rc != 0 and "BUILT" in out, "a pass at another sha on a doing item stays refused (rc %d)" % rc)
    check(state(REWORK) == "doing", "the refused pass changed nothing (reads %s)" % state(REWORK))
    rc, out = rf("verify", NEVER, "--result", "pass", "--config", "selftest", "--criterion", "A1", "--level", "L2",
                 "--sha", SHA, "--evidence", "selftest")
    check(rc != 0, "a criterion pass on a never-built item stays refused (rc %d)" % rc)


def main():
    t_a_pass_at_the_built_sha_on_a_started_built_item_counts()
    t_a_pass_at_another_sha_or_on_an_unbuilt_item_stays_refused()
    print("selftest_judge_start_keeps_pass: %s" % ("PASS" if not fails else "FAIL (%d)" % len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
