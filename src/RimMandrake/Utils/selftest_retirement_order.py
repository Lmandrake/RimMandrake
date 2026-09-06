"""
Selftest: a donor mod retiring OUT OF ORDER is a failing check, not a
discovery weeks later.

DROID_RETIREMENT_ORDER_ASSERT_1: `guy762_KotORDroidBase` carries
ParentName="ABF_Thing_Synstruct_HumanlikeBase", an ABF-owned abstract, and
that folder only loads while guy762.KotORDroids is active. No patch can gate
an inheritance dependency (PatchOperationFindMod adds/removes nodes, it
cannot make a ParentName resolve), so the only safeguard is ORDER: retire
guy762.kotordroids no later than ABF/SynCore. `retirement_order.py` reads
that constraint from `infrastructure/state/facts/retirement_order.json`
rather than carrying it as a hardcoded pair of strings.

Two things are proven here, and the second is the one that matters:

1. The fact file loads and its shape is sane.
2. `check_order` actually FAILS on the bad state — kotordroids + kotorcore
   active, ABF/SynCore both gone — proven against a FIXTURE (a plain set of
   packageIds), never by touching the real ModsConfig.xml. A check that only
   ever runs against "today, and today is fine" proves nothing.

It also checks the live ModsConfig.xml today, same as any other selftest
reads live state — but that pass is not the point of this file; the fixture
failure is.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from retirement_order import constraints, check_order  # noqa: E402

fails = []


def check(ok, what):
    if ok:
        print("  ok   %s" % what)
    else:
        print("  FAIL %s" % what)
        fails.append(what)


print("retirement_order: the fact file itself")
cs = constraints()
check(len(cs) >= 1, "at least the kotordroids/ABF constraint is on file")
kotor_c = next((c for c in cs if c["id"] == "kotordroids_needs_abf_while_kotorcore_active"),
               None)
check(kotor_c is not None, "the kotordroids/ABF constraint is present by id")
if kotor_c:
    check("guy762.kotordroids" in kotor_c["dependent_active_all"],
          "constraint's dependent set names guy762.kotordroids")
    check("guy762.mm.kotorcore" in kotor_c["dependent_active_all"],
          "constraint's dependent set names guy762.mm.kotorcore (the folder gate)")
    check("killathon.artificialbeings" in kotor_c["requires_active_all"],
          "constraint's required set names ABF core")

print("retirement_order: today's live ModsConfig.xml holds no violation")
try:
    live_violations = check_order()
    check(len(live_violations) == 0,
          "no violation live (ABF/SynCore are both still active) -- "
          "found %r" % live_violations)
except OSError as exc:
    # Offline / no ModsConfig reachable from this machine: not what this
    # selftest is proving, so don't fail the suite over it.
    print("  skip live ModsConfig check (%s)" % exc)

print("retirement_order: PROVEN TO FAIL on the bad state (fixture, not the real file)")
# The exact bad state DROID_RETIREMENT_ORDER_ASSERT_1 exists to catch: someone
# unticks ABF/SynCore while guy762.kotordroids + guy762.mm.kotorcore are still
# both active.
bad_state = {
    "guy762.kotordroids", "guy762.mm.kotorcore",
    "erdelf.humanoidalienraces", "unlimitedhugs.hugslib",
}
bad_violations = check_order(active_pids=bad_state)
check(len(bad_violations) == 1,
      "bad state (kotordroids+kotorcore active, ABF/SynCore absent) "
      "yields exactly one violation (got %d)" % len(bad_violations))
if bad_violations:
    v = bad_violations[0]
    check(v["id"] == "kotordroids_needs_abf_while_kotorcore_active",
          "the violation is the kotordroids/ABF constraint, not some other one")
    check(set(v["missing_required"]) ==
          {"killathon.artificialbeings", "killathon.artificialbeings.syncore"},
          "both ABF core and SynCore are reported missing (got %r)"
          % v["missing_required"])

print("retirement_order: the fixture does NOT fail once only ONE side changes")
check(len(check_order(active_pids=bad_state | {"killathon.artificialbeings",
                                                "killathon.artificialbeings.syncore"})) == 0,
      "adding ABF+SynCore back to the bad state clears the violation")
check(len(check_order(active_pids={"guy762.kotordroids",
                                    "erdelf.humanoidalienraces"})) == 0,
      "kotordroids active WITHOUT kotorcore is not flagged -- the "
      "_DroidsBase folder never loads, so there is no live ParentName risk")
check(len(check_order(active_pids={"guy762.mm.kotorcore",
                                    "erdelf.humanoidalienraces"})) == 0,
      "kotorcore active WITHOUT kotordroids is not flagged -- same reason")

print("\n%s: %d failure(s)" % (os.path.basename(__file__), len(fails)))
sys.exit(1 if fails else 0)
