#!/usr/bin/env python3
"""selftest_fakeworld_parity: selftest_relentless.FakeWorld keeps up with the real Effects (NIGHTLY_COP_FIX_RED_FDYIER_ALCO).

The class this guards: the validator replay bank (validator_replay.py, read by selftest_validator_mutants.py) ticks the
real supervisor against FakeWorld. When a relentless module starts calling a new `fx.<method>` that only the real
Effects has, every replay case reaching it dies with AttributeError and the nightly goes red on an unmutated bank
(2026-11-05: relentless_reachfix.sweep called fx.reach_probe; FakeWorld had none).

The check is static: every `fx.<name>` used in a relentless*.py module, that the real Effects class defines, that is
not guarded by getattr/hasattr, must exist on a bare FakeWorld. KNOWN_GAPS is the frozen list of gaps that predate
this guard (each reached only by rigs that set the method themselves); it may only shrink. A new name failing here is
fixed by giving FakeWorld a neutral recording default, not by adding it to KNOWN_GAPS.

`--strip NAME` replays an instance: the scan runs on a FakeWorld without NAME, as it stood when that method was missing
(`--strip reach_probe` is the 2026-11-05 red, NIGHTLY_COP_FIX_RED_TOJBIY_TAAI's repeat); it must fail.
"""
import glob
import inspect
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
STRIP = sys.argv[sys.argv.index("--strip") + 1].split(",") if "--strip" in sys.argv[:-1] else []
sys.argv = sys.argv[:1]

import relentless as R               # noqa: E402
import selftest_relentless as T      # noqa: E402

# Frozen 2026-11-05: may only shrink. Never add a name here to make this test pass.
KNOWN_GAPS = frozenset("""
bridge_idle bridge_release bridge_take bundle_clone clone_gap first_touch_hold
game_batch_gap game_implement game_ledger game_mod_gap game_preflight game_rows game_trees health
live_round_alive live_round_launch load_stall_evidence modlist_enable proofs_at prove_alive
prove_launch refusal_print rimflow run_fixture showing_clone told
""".split())

FAILS = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def gaps(fake_cls=T.FakeWorld):
    real = R.Effects
    fw = fake_cls()
    src = " ".join(open(f, encoding="utf-8").read() for f in sorted(glob.glob(os.path.join(HERE, "relentless*.py"))))
    used = set(re.findall(r"\bfx\.([a-z_][a-z0-9_]*)\b", src))
    guarded = set(re.findall(r"(?:getattr|hasattr)\(fx,\s*[\"']([a-z_][a-z0-9_]*)[\"']", src))
    out = []
    for name in sorted(used - guarded):
        member = getattr(real, name, None)
        if member is None or not (callable(member) or isinstance(member, property)):
            continue
        if not hasattr(fw, name):
            out.append(name)
    return out


def stripped(names):
    """-> a FakeWorld class that lacks `names`, as it did before they were given defaults."""
    class Stripped(T.FakeWorld):
        def __getattribute__(self, name):
            if name in names:
                raise AttributeError(name)
            return object.__getattribute__(self, name)
    return Stripped


def main():
    missing = gaps(stripped(STRIP)) if STRIP else gaps()
    new = [m for m in missing if m not in KNOWN_GAPS]
    check(not new, "every unguarded fx.<method> the real Effects has exists on a bare FakeWorld (new gaps: %s)" % new)
    healed = sorted(KNOWN_GAPS - set(missing))
    check(not healed, "KNOWN_GAPS holds no name FakeWorld now has (remove: %s)" % healed)

    # sanity probe: the instrument can see a gap (a FakeWorld stripped of a method it has is caught)
    check("launch" in gaps(stripped(["launch"])), "the scan sees a stripped method (launch)")
    print("RESULT %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
