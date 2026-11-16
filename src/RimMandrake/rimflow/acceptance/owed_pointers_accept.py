#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_REFUSE_HANDOFF_POINTER_WITHOUT_OWED_ID (spec:
design/specs/2026-11-15-conductor-restart-loses-nothing.md §3 E4 as amended by §4, and §5 ticket 3). Written by the
filing seat; the builder does not edit it (a wrong clause goes to the Conductor).

    python3 src/RimMandrake/rimflow/acceptance/owed_pointers_accept.py     # exit 0 and "PASS 7/7" when built

THE CONTRACT (a validator: it writes nothing; GPT's read, §4)
  `python3 src/RimMandrake/rimflow/owed.py check-pointers <handoff.md>`
    A pointer is a line starting `- \\`<ID>\\`` that holds `NEXT:`. Each pointer must cite, anywhere on its line, the id
    of an OPEN `kind: owed` item (its own id counts). Exit 0 when all do (or there are no pointers); exit 1 otherwise,
    printing one line per failing pointer with its line number and the reason: `no owed id`, or
    `owed <ID> is closed` (the act is done: drop the pointer, or file the new act).
  Closing a pointer's item never discharges its NEXT: the debt is its own item, so the wake still lists it (E1).
  `handoff.py --check` (the gate in front of HANDOFF READY) runs it on the handoff it checks
  (src/RimMandrake/Utils/handoff.py holds `check-pointers` or `owed.check_pointers`).
"""
import glob
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RIMFLOW, "..", "..", ".."))
CLI = os.path.join(RIMFLOW, "cli.py")
OWED = os.path.join(RIMFLOW, "owed.py")
TOTAL = 7
RESULTS = []


def check(ok, what):
    RESULTS.append((bool(ok), what))


def main():
    tmp = tempfile.mkdtemp(prefix="owed_pointers_")
    items = os.path.join(tmp, "items")
    os.makedirs(items)
    base = {k: v for k, v in os.environ.items() if not k.startswith("RIMFLOW_")}
    base.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=items, RIMFLOW_SEAT="BENCH",
                RIMFLOW_PROBE="no-reading", PYTHONDONTWRITEBYTECODE="1")

    def cli(*a):
        return subprocess.run([sys.executable, CLI] + list(a) + ["--why", "acceptance sandbox"], cwd=REPO, env=base,
                              capture_output=True, text=True, timeout=120)

    t1 = "RIMMANDRAKE_JUDGE_SANDBOX_MOD_BLIND_CYCLE_THREE"
    o1 = "RIMMANDRAKE_TELL_SANDBOX_OWNER_WHERE_MOD_STANDS"
    o2 = "RIMMANDRAKE_CONFIRM_SANDBOX_STALE_ACT_ALREADY_DONE"
    cli("file", t1, "--for", "BENCH", "--title", "a pipeline item", "--kind", "task")
    cli("file", o1, "--for", "BENCH", "--title", "tell him where the mod stands", "--kind", "owed",
        "--caused-by", t1)
    cli("file", o2, "--for", "BENCH", "--title", "confirm closed", "--kind", "owed")
    cli("close", o2, "--no-code", "told him at 3:00 PM PST: it is closed")

    def run(lines):
        f = os.path.join(tmp, "h%d.md" % len(glob.glob(os.path.join(tmp, "h*.md"))))
        open(f, "w").write("# HANDOFF\n\nSome prose naming `%s` with no next step.\n\n" % t1 + "\n".join(lines) + "\n")
        r = subprocess.run([sys.executable, OWED, "check-pointers", f], cwd=REPO, env=base, capture_output=True,
                           text=True, timeout=120)
        return r.returncode, r.stdout + r.stderr

    p1 = "- `%s` — doing; NEXT: tell him where it stands." % t1
    p2 = "- `%s` — doing; NEXT: tell him where it stands (owed `%s`)." % (t1, o1)
    p3 = "- `%s` — proposed; NEXT: tell him." % o1
    p4 = "- `%s` — done; NEXT: confirm closed (owed `%s`)." % (t1, o2)

    def events():
        n = 0
        for f in glob.glob(os.path.join(tmp, "events", "*.jsonl")) + [base["RIMFLOW_LEDGER"]]:
            if os.path.isfile(f):
                n += sum(1 for _ in open(f))
        return n

    before = events()
    rc, out = run([p2, p3])
    check(rc == 0, "pointers citing an open owed id pass (rc %s)" % rc)
    rc, out = run([p1])
    check(rc == 1 and "no owed id" in out, "a pointer with no owed id is refused, naming why")
    rc, out = run([p4])
    check(rc == 1 and ("owed %s is closed" % o2) in out, "a pointer citing a closed owed id is refused, naming it")
    rc, out = run([p1, p2, p3, p4])
    bad = [l for l in out.splitlines() if "no owed id" in l or "is closed" in l]
    check(rc == 1 and len(bad) == 2, "a mixed handoff lists exactly the two failing pointers (got %d)" % len(bad))
    rc, out = run([])
    check(rc == 0, "a handoff with no pointers passes (prose naming an item is not a pointer)")
    check(events() == before and os.path.isfile(OWED), "check-pointers writes nothing to the ledger")
    hp = open(os.path.join(REPO, "src/RimMandrake/Utils/handoff.py"), encoding="utf-8").read()
    check("check-pointers" in hp or "owed.check_pointers" in hp, "handoff.py --check runs check-pointers")
    passed = sum(ok for ok, _ in RESULTS)
    for ok, what in RESULTS:
        print("%s  %s" % ("ok  " if ok else "FAIL", what))
    print("%s %d/%d" % ("PASS" if passed == TOTAL == len(RESULTS) else "FAIL", passed, TOTAL))
    return 0 if passed == TOTAL == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
