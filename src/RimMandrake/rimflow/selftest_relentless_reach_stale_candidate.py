#!/usr/bin/env python3
"""REAPER_SELFTEST_FIX_BLIND_IN_EVERY_BOX died once by a false reopen: its fix (21832017e8, the reaper selftests scan
only their own process tree) closed the proc reach ticket, yet OPS_TMP_DRAIN_RESTORE_JVCO's blind check ran at its own
candidate 65315ab8e7, cut BEFORE that fix: the old selftest walked a stranger's /proc, the Judge was blind again, and
the sweep filed the ticket's "live broken" (2026-11-06 15:27Z). No reach repair can give eyes to a sha that lacks the
fix that gives them; the candidate must be rebased. Rows, through the real tick on selftest_relentless's rig:
  (1) the class ticket closed at a fix the candidate does not hold: blind after the applied repair files no ticket
      (no reopen of the closed one);
  (2) and the item goes back to its builder, told to rebase onto the fix;
  (3) the same, but the candidate holds the fix: the old road stands (the one ticket);
  (4) an unanswerable ancestry (None) is no proof of staleness: the old road stands."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_relentless_blind as B       # noqa: E402
import selftest_relentless_reachfix as RX   # noqa: E402

FAILS = []
TICKET = "REAPER_SELFTEST_FIX_BLIND_IN_EVERY_BOX"
FIX = "21832017e8f21ac7f0595978b2e8f2742e469685"
PROC_BLIND = ("host /proc/<pid> for selftest_scratch_reap_tmp.py's global-hold guard: readlink /proc/1/cwd rc=1; my run "
              "RED 14 FAIL all from 'cannot see a process: pid 366 Permission denied'")


def ok(cond, name):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def run(holds):
    x = RX.rig(probe=(True, "proc_cwds exit 0, 400 chars"))
    x.w.items[TICKET] = "done"
    x.w.closed = {TICKET: FIX}
    x.w.asked = []

    def contains(sha, fix):
        x.w.asked.append((sha, fix))
        return holds
    x.w.contains = contains
    B.to_check(x, "I0")
    RX.blind(x, "I0", proposals=["proc_cwds"], what=PROC_BLIND)
    for _ in range(4):
        if x.st("I0")["status"] in ("checking", "queued"):
            break
        x.tick()
    if x.st("I0")["status"] == "checking":
        RX.blind(x, "I0", what=PROC_BLIND)      # blind again on the same sha after the repair applied
        for _ in range(3):
            x.tick()
    return x


def main():
    x = run(False)
    st = x.st("I0")
    ok(TICKET not in x.w.tickets, "(1) stale candidate: the closed ticket is not refiled or reopened: %s" % x.w.tickets)
    why = str((st.get("last_fail") or {}).get("detail") or "")
    ok(st["status"] != "blocked" and "rebase" in why and FIX[:10] in why,
       "(2) it goes back to its builder to rebase onto %s: %s / %s" % (FIX[:10], st["status"], why[:200]))
    x.done()
    for holds, row in ((True, "(3) the candidate holds the fix"), (None, "(4) ancestry unanswered")):
        x = run(holds)
        ok(x.w.tickets == [TICKET], "%s: blind again files the one ticket: %s" % (row, x.w.tickets))
        x.done()
    print("FAILS: %d" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
