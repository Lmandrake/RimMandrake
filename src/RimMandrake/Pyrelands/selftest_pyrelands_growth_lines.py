#!/usr/bin/env python3
"""selftest_pyrelands_growth_lines: validation.plant_growth_of_lines reads the inspect lines the live game writes.

The lines are the ones jawa/inspect_string returned on game a (Pyrelands visit 4, 2026-11-21,
design/concepts/Pyrelands/version/in_game/visit_4/evidence/script_inspect_probe.log): '70% grown' and 'Mature.'. The
parent's reader searched 'Growth: N%' and read None on all of them (RIMMANDRAKE_READ_PYRE_REGROW_GROWTH_NONE_ON_ALL_SIX_DAYS);
`--old` runs these cases against that reader and must fail. Offline, WSL python3."""
import os, re, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [H, os.path.join(H, "..", "Utils"), os.path.join(H, "..", "Utils", "modcheck")]
import validation  # noqa: E402

NAME = "selftest_pyrelands_growth_lines"
CASES = [
    (["70% grown", "Growth rate: 7.6% (temperature growth multiplier 79%)"], 0.70),
    (["5% grown", "Growth rate: 7.7% (temperature growth multiplier 79%)"], 0.05),
    (["Mature."], 1.0),
    (["Growth rate: 7.6% (temperature growth multiplier 79%)"], None),   # a rate is not a growth
    ([], None),
    (None, None),
]


def old_reader(lines):
    for ln in lines or []:
        m = re.search(r"Growth:\s*(\d+)%", str(ln))
        if m:
            return int(m.group(1)) / 100.0
    return None


def main():
    f = old_reader if "--old" in sys.argv else validation.plant_growth_of_lines
    bad = 0
    for lines, want in CASES:
        got = f(lines)
        ok = (got is None and want is None) or (got is not None and want is not None and abs(got - want) < 1e-9)
        bad += not ok
        print("%s %r -> %r (want %r)" % ("PASS" if ok else "FAIL", lines, got, want))
    print("%s: %d of %d checks failed" % (NAME, bad, len(CASES)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
