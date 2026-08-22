#!/usr/bin/env python3
"""End-to-end check of the texture-resolver ladder against the LIVE load set.

    python3 src/RimMandrake/Utils/verify_resolve_texture_live.py

⚠️ SLOW — it builds the 578-mod def set and walks ~47,800 loose PNGs, about four
minutes. The fast guard is `test_resolve_texture.py`; run that in a loop and this
one before believing a result.

🔑 The fixture is `design/Jawa/mods/plant_sprites/manifest.json`: 190 plants, each
recording the absolute PNG a working ladder found and which rung fired. Two
things are checked and the second matters more:

  1. every plant that HAS art resolves;
  2. `Plant_Berry_Leafless` does NOT.

⛔ (2) is the one that catches a bad "fix". Its stem changed — the def declares
`Things/Plant/BerryPlant_Leafless`, ReGrowth's art is `BerryBush_Leafless*` — so
only fuzzy matching reaches it, and fuzzy matching is what put the wrong sprite on
42 Imperial garments. A ladder that resolves this case is GUESSING, and a resolver
that finds everything cannot tell MISSING from NOT FOUND, which is its whole job.

⚠️ The manifest entry for that def carries no `texPath` key at all (only
`missing`/`why`), so a harness that iterates on `texPath` SKIPS it silently and
reports a clean sweep. That happened on 2026-08-22. The path is therefore named
literally below rather than read from the fixture.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import animal_contact_sheet as A                                    # noqa: E402
from def_inventory import build, D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
FIXTURE = os.path.join(ROOT, "design/Jawa/mods/plant_sprites/manifest.json")

# Must stay unresolved. See the module docstring.
MUST_NOT_RESOLVE = [("Plant_Berry_Leafless", "Things/Plant/BerryPlant_Leafless")]


def main():
    if not os.path.isfile(FIXTURE):
        print("no fixture at %s" % FIXTURE)
        return 2
    man = json.load(open(FIXTURE, encoding="utf-8"))
    ds = build(D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA, types=("ThingDef",), quiet=True)
    tex, npng, nroots = A.build_texture_index(ds.mods)
    bundles, nb = A.load_bundle_index()
    print("load set: %d mods, %d loose PNGs in %d roots, %d bundle names"
          % (len(ds.mods), npng, nroots, len(bundles)))

    tested = resolved = 0
    misses = []
    for defn, rec in sorted(man.items()):
        tp = rec.get("texPath")
        if not tp:
            continue                      # the negative cases are checked below
        tested += 1
        hit, _ = A.resolve_texture(tp, tex, bundles, None)
        if hit is None:
            misses.append((defn, tp))
        else:
            resolved += 1

    bad = 0
    print("\npositive: %d/%d resolved" % (resolved, tested))
    for defn, tp in misses:
        bad += 1
        print("  MISS  %-30s %s" % (defn, tp))

    print("\nnegative: %d case(s) that must NOT resolve" % len(MUST_NOT_RESOLVE))
    for defn, tp in MUST_NOT_RESOLVE:
        hit, variant = A.resolve_texture(tp, tex, bundles, None)
        if hit is None:
            print("  ok    %-30s correctly unresolved" % defn)
        else:
            bad += 1
            print("  FAIL  %-30s the ladder GUESSED: %s (%s)" % (defn, hit, variant))

    print("\n%s - %d failure(s)" % ("FAIL" if bad else "OK", bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
