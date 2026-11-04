#!/usr/bin/env python3
"""Selftest for MODCHECK_SWAP_FIX_OUTSIDE_TRY: runner.run() must restore FULL whenever the swap to MINIMAL may have
been applied -- including a swap_to_test_list() that itself raises after MINIMAL is on -- and must neither swap nor
restore on dry_run or MODCHECK_KEEP_MODLIST=1. Offline: every side effect is stubbed; no ModsConfig write."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import runner  # noqa: E402

FAILS = []


def ok(cond, what, got=None):
    print(("PASS  " if cond else "FAIL  ") + what + ("" if cond or got is None else "   got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def attempt(swap, find_mod_dir, env=None, dry_run=False):
    """Run runner.run with stubs; returns (calls, exception or None)."""
    calls = []
    names = ("swap_to_test_list", "restore_full", "find_mod_dir")
    real = {n: getattr(runner, n) for n in names}
    saved = os.environ.pop("MODCHECK_KEEP_MODLIST", None)
    if env:
        os.environ.update(env)

    def fake_swap(*a, **k):
        calls.append("swap")
        swap()

    runner.swap_to_test_list = fake_swap
    runner.restore_full = lambda *a, **k: calls.append("restore")
    runner.find_mod_dir = find_mod_dir
    err = None
    try:
        runner.run([("ToyMod", "X_ITEM")], dry_run=dry_run)
    except Exception as ex:  # noqa: BLE001 -- the test inspects whatever escaped
        err = ex
    finally:
        for n, f in real.items():
            setattr(runner, n, f)
        os.environ.pop("MODCHECK_KEEP_MODLIST", None)
        if saved is not None:
            os.environ["MODCHECK_KEEP_MODLIST"] = saved
    return calls, err


def boom_after_minimal():
    raise RuntimeError("compose_test_list read-back missing ['x.y'] (MINIMAL already applied)")


def boom_find(m):
    raise RuntimeError("no mod dir for " + m)


# 1. the swap itself raises after MINIMAL is applied: restore must still run, and the error must surface
calls, err = attempt(boom_after_minimal, boom_find)
ok(calls == ["swap", "restore"], "swap raising after MINIMAL still calls restore_full", calls)
ok(isinstance(err, RuntimeError) and "read-back" in str(err), "the swap's own error propagates", err)

# 2. swap succeeds, the next step fails: restore runs
calls, err = attempt(lambda: None, boom_find)
ok(calls == ["swap", "restore"], "failure after a good swap calls restore_full", calls)
ok(isinstance(err, RuntimeError) and "no mod dir" in str(err), "the later error propagates", err)

# 3. MODCHECK_KEEP_MODLIST=1: neither swap nor restore
calls, err = attempt(lambda: None, boom_find, env={"MODCHECK_KEEP_MODLIST": "1"})
ok(calls == [], "KEEP_MODLIST never swaps or restores", calls)

# 4. dry_run: neither swap nor restore (the stubbed find_mod_dir may or may not be reached)
calls, err = attempt(lambda: None, boom_find, dry_run=True)
ok("swap" not in calls and "restore" not in calls, "dry_run never swaps or restores", calls)

print("\n%d failure(s)" % len(FAILS) if FAILS else "\nALL PASS")
sys.exit(1 if FAILS else 0)
