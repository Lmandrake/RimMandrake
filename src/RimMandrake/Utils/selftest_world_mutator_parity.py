"""Selftest: world_mutator_parity.verdict - the PASS/FAIL rule for parity U2 (no save needed)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from world_mutator_parity import verdict  # noqa: E402


def main():
    fails = 0

    def check(name, got, want):
        nonlocal fails
        if got != want:
            fails += 1
            print("FAIL %s: got %r want %r" % (name, got, want))

    check("clean", verdict(27913, 0, [], [])[0], True)
    check("empty read is blind", verdict(0, 0, [], [])[0], False)
    check("unresolved", verdict(10, 1, [], [])[0], False)
    check("rolled survives", verdict(10, 0, [(5, "Caves")], [])[0], False)
    check("stamp missing", verdict(10, 0, [], [(7, "River")])[0], False)
    check("reasons named", len(verdict(0, 2, [(1, "A")], [(2, "B")])[1]), 4)
    print("selftest_world_mutator_parity: %s" % ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
