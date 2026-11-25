#!/usr/bin/env python3
"""selftest_compose_only.py - `modcheck compose MOD` writes the list `run MOD` composes, and leaves it, only for a caller that
owns its game (RIMMANDRAKE_FIX_STEVEDESKTOP_TOP_WASTE_HE_SAID_END_THIS). No game, no ModsConfig: the list writers are stubs."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runner  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    calls = []
    runner.swap_to_test_list = lambda *a: calls.append(("swap",) + a)
    runner.compose_test_list = lambda ids, *a, **k: calls.append(("compose", list(ids)))
    runner.restore_full = lambda *a, **k: calls.append(("restore",))
    runner.test_list_ids = lambda mods: calls.append(("ids", [m for m, _ in mods])) or ["a.dep", "a.mod"]
    os.environ.pop("MODCHECK_STALE_KEEP_COMPOSED", None)
    try:
        runner.compose_only(["Mock"])
        refused = False
    except RuntimeError:
        refused = True
    check(refused and not calls, "without MODCHECK_STALE_KEEP_COMPOSED=1 nothing is written %s" % calls)
    os.environ["MODCHECK_STALE_KEEP_COMPOSED"] = "1"
    ids = runner.compose_only(["Mock"])
    check(calls == [("swap",), ("ids", ["Mock"]), ("compose", ["a.dep", "a.mod"])] and ids == ["a.dep", "a.mod"],
          "the owner of its game gets MINIMAL + the run's own composition, and FULL is not restored %s" % calls)
    print("FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
