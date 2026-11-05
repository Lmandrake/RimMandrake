#!/usr/bin/env python3
"""Class guard (NIGHTLY_COP_FIX_RED_RACIBL_KZSJ): the sprite selftest's reference PNG must be crisp enough for its
semi-transparent case to prove anything.

That case (skills/generating-rimworld-sprites/scripts/selftest.py, make_translucent) turns only alpha-255 pixels
translucent and expects validate_sprite.py to reject the result for a midtone fraction above MIDTONE_MAX_FRACTION.
A reference with soft alpha has few solid pixels, so the fixture stays under the bar and the case fails every night
(Pyrinth_a.png, redrawn soft: 3.2% against the 8% bar, red from 2026-11-04). This guard measures the fixture that
case would build from each reference the selftest is run with and refuses one without HEADROOM x the bar, so a
redraw of the reference turns this test red with the reason, not the sprite selftest with a riddle.

    python3 src/RimMandrake/Utils/selftest_sprite_reference_crisp.py                  # the references in use
    python3 src/RimMandrake/Utils/selftest_sprite_reference_crisp.py --reference P    # one PNG (replay an instance)
"""
from __future__ import annotations

import argparse
import ast
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / "skills" / "generating-rimworld-sprites" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS.parents[1] / "generating-images" / "scripts"))
import pnglib  # noqa: E402
import selftest as sprite_selftest  # noqa: E402
import validate_sprite  # noqa: E402

HEADROOM = 1.25   # the translucent fixture must read at least this many times the validator's bar


def runner_reference() -> Path:
    """SPRITE_REFERENCE as run_selftests.py passes it, read from its source (importing the runner has side effects)."""
    tree = ast.parse((REPO / "src/RimMandrake/Utils/run_selftests.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "SPRITE_REFERENCE" for t in node.targets):
            return REPO / ast.literal_eval(node.value)
    raise LookupError("run_selftests.py defines no SPRITE_REFERENCE")


def translucent_fraction(ref: Path) -> float:
    w, h, px = pnglib.read_png(str(ref))
    out = Path(tempfile.mkdtemp()) / "translucent.png"
    pnglib.write_rgba(str(out), w, h, sprite_selftest.make_translucent(w, h, px))
    m = validate_sprite.measure(out)
    return m["midtone"] / m["n"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--reference", action="append", help="PNG to judge instead of the references in use")
    args = ap.parse_args()
    bar = validate_sprite.MIDTONE_MAX_FRACTION
    fails = 0
    if args.reference:
        refs = [Path(r) for r in args.reference]
    else:
        refs = [runner_reference(), Path(sprite_selftest.DEFAULT_REFERENCE)]
        if refs[0].resolve() != refs[1].resolve():
            print(f"FAIL the runner's reference {refs[0]} is not the selftest's default {refs[1]}")
            fails += 1
    for ref in dict.fromkeys(refs):
        if not ref.is_file():
            print(f"FAIL no such reference: {ref}")
            fails += 1
            continue
        frac = translucent_fraction(ref)
        ok = frac >= HEADROOM * bar
        print(f"{'ok  ' if ok else 'FAIL'} {ref.name}: translucent fixture {frac:.1%} vs bar {bar:.0%} "
              f"(needs >= {HEADROOM * bar:.1%}; too soft a reference cannot fail the semi-transparent case)")
        fails += not ok
    print("RESULT:", "PASS" if not fails else f"FAIL ({fails})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
