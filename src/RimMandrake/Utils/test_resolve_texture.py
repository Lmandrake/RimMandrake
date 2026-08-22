#!/usr/bin/env python3
"""Unit test for the texture-resolver ladder — synthetic index, no load set.

    python3 src/RimMandrake/Utils/test_resolve_texture.py

🔑 WHY SYNTHETIC. The honest end-to-end check needs the 578-mod load set and
takes minutes; that fixture is `design/Jawa/mods/plant_sprites/manifest.json`
and it is what calibrated these rungs. This file is the fast guard that stops a
rung being deleted by someone who does not have four minutes — one named case
per rung, each traceable to a real def that failed before 2026-08-22.

⛔ A passing run here does NOT mean the resolver is correct against the real
game. It means no rung was removed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from animal_contact_sheet import (          # noqa: E402
    resolve_texture, TextureIndex, BundleIndex)


def loose(*paths):
    idx = TextureIndex()
    for p in paths:
        idx[p] = "/abs/" + p
    return idx


def bundle(*rows):
    """rows are (stem, dirs tuple, source)."""
    idx = BundleIndex()
    for stem, dirs, src in rows:
        path = "/bundle/%s.png" % stem
        idx.setdefault(stem, []).append((src, list(dirs), path))
        if dirs:
            idx.by_dir.setdefault(dirs[-1], []).append(
                (src, tuple(dirs), stem, path))
    idx.has_paths = True
    return idx


CASES = []


def case(name, want_file, tex_path, index, bundles=None):
    CASES.append((name, want_file, tex_path, index, bundles))


# ── the rungs that already worked ────────────────────────────────────────────
case("bare name", "/abs/things/plant/agave.png",
     "Things/Plant/Agave", loose("things/plant/agave.png"))
case("side suffix wins over bare", "/abs/things/pawn/deer_south.png",
     "Things/Pawn/Deer", loose("things/pawn/deer.png",
                               "things/pawn/deer_south.png"))

# ── added 2026-08-22, each from a def that came back "missing" before ────────
case("bare capital (Plant_Agave -> AgaveA.png)", "/abs/things/plant/agavea.png",
     "Things/Plant/Agave", loose("things/plant/agavea.png"))
case("infix (AB_HardyGrass -> GrassA_Leafless)",
     "/abs/things/plant/grassa_leafless.png",
     "Things/Plant/Grass_Leafless", loose("things/plant/grassa_leafless.png"))
case("loose directory (Graphic_Random)", "/abs/things/plant/dandelion/dandeliona.png",
     "Things/Plant/Dandelion", loose("things/plant/dandelion/dandeliona.png",
                                     "things/plant/dandelion/dandelionb.png"))
case("loose directory refuses a _m mask",
     "/abs/things/plant/moss/mossa.png",
     "Things/Plant/Moss", loose("things/plant/moss/moss_m.png",
                                "things/plant/moss/mossa.png"))
case("bundle capital", "/bundle/grassa.png", "Things/Plant/Grass", loose(),
     bundle(("grassa", ("things", "plant"), "mod.a")))
case("bundle infix", "/bundle/brambesa_leafless.png",
     "Things/Plant/Brambes_Leafless", loose(),
     bundle(("brambesa_leafless", ("things", "plant"), "mod.a")))
case("bundle directory, DIFFERENT stem (RG_Bush -> busha)",
     "/bundle/busha.png", "Things/Plant/RG_Bush", loose(),
     bundle(("busha", ("textures", "things", "plant", "rg_bush"), "mod.rg"),
            ("bushb", ("textures", "things", "plant", "rg_bush"), "mod.rg")))

# ── what must STAY unresolved. A resolver that finds everything is lying. ────
NEGATIVE = [
    ("changed stem is NOT guessed (Plant_Berry_Leafless)",
     "Things/Plant/BerryPlant_Leafless", loose("things/plant/berrybush_leafless.png"),
     None),
    ("no art at all", "Things/Plant/Nothing", loose(), None),
]


def main():
    bad = 0
    for name, want, tex, idx, bnd in CASES:
        got, variant = resolve_texture(tex, idx, bnd, None)
        if got != want:
            bad += 1
            print("  FAIL  %-46s\n          want %s\n          got  %s (%s)"
                  % (name, want, got, variant))
        else:
            print("  ok    %-46s %s" % (name, variant))
    for name, tex, idx, bnd in NEGATIVE:
        got, variant = resolve_texture(tex, idx, bnd, None)
        if got is not None:
            bad += 1
            print("  FAIL  %-46s should NOT resolve, got %s" % (name, got))
        else:
            print("  ok    %-46s correctly unresolved" % name)
    print("\n%s - %d case(s), %d failure(s)"
          % ("FAIL" if bad else "OK", len(CASES) + len(NEGATIVE), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
