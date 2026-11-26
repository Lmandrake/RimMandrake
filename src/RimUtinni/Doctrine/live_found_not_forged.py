#!/usr/bin/env python3
"""live_found_not_forged.py -- live check of OILGAS_BUILDABILITY_EXCISE_FOUND_NOT_FORGED (mandrake.rut.doctrine). Kind A.

    python.exe src/RimUtinni/Doctrine/live_found_not_forged.py [GameName]     exit 0 PASS, 1 FAIL, 2 COULD NOT LOOK

Claim: in a game with Rimefeller and Vanilla Helixien Gas Expanded, the player cannot build the oil works or the
helixien pump, and a newly generated map holds no infinite helixien deposit.
Entry: a running game whose list holds dubwise.rimefeller, vanillaexpanded.helixiengas and mandrake.rut.doctrine
(tier mods__dubwise_rimefeller__vanillaexpanded_helixiengas__mandrake_rut_doctrine), Doctrine at default settings.
Valid opportunity: VHGE seeded infinite deposits on the fresh map (Doctrine's postfix saw the map and removed > 0
cells); a map on which VHGE seeded none is COULD NOT LOOK, never a pass.
Success: the six works read designationCategory null; FuelStorage keeps its category; VHGE's own infiniteGasGrid
on the map holds 0 true cells.
Forbidden: none beyond the success reads (nothing is staged). End: one fresh quicktest map, read once, paused.
Cheaper test: selftest_found_not_forged.py decides the patch offline; only the game shows that the setting gate,
the def loader's empty node and the Harmony postfix act as the offline check assumes (cheaper_why).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))
import scene  # noqa: E402

WORKS = ["OilWell", "DeepOilWell", "OilStorage", "CrudeCracker", "RefineryLoadingBay", "VHGE_HelixienPump"]
KEEP = "FuelStorage"
FINITE = "static:RimMandrake.Utinni.Doctrine.HelixienFinite"


def main(game):
    fails, blind = [], []
    with scene.open(game, needs={"map": "fresh:quicktest"}) as s:
        for w in WORKS:
            v = s.read("def:ThingDef/%s" % w, "designationCategory")
            if v.state != "ok":
                blind.append("%s designationCategory: %r" % (w, v))
            elif v.v not in (None, "", "null"):
                fails.append("%s is buildable: designationCategory %s" % (w, v.v))
        k = s.read("def:ThingDef/%s" % KEEP, "designationCategory")
        if k.state != "ok":
            blind.append("%s designationCategory: %r" % (KEEP, k))
        elif k.v in (None, "", "null"):
            fails.append("%s lost its category: the patch is a blanket" % KEEP)
        seen = s.read(FINITE, "MapsSeen")
        removed = s.read(FINITE, "CellsRemovedLastMap")
        if seen.state != "ok" or removed.state != "ok":
            blind.append("Doctrine's HelixienFinite counters: %r %r (Doctrine or VHGE not loaded?)" % (seen, removed))
        elif int(seen.v) < 1:
            blind.append("VHGE's InitDeposits never ran on this map")
        elif int(removed.v) < 1:
            blind.append("VHGE seeded no infinite deposit on this map: no opportunity")
        grid = s.read("map", "comp<HelixienGasHandler>.infiniteGasGrid.trueCountInt")
        if grid.state != "ok":
            blind.append("VHGE's infiniteGasGrid: %r" % (grid,))
        elif int(grid.v) != 0:
            fails.append("the map holds %s infinite helixien cells" % grid.v)
        print("reads: removed=%s seen=%s grid=%s" % (getattr(removed, "v", None) if removed.state == "ok" else removed.state,
                                                     getattr(seen, "v", None) if seen.state == "ok" else seen.state,
                                                     grid.v if grid.state == "ok" else grid.state))
    for f in fails:
        print("FAIL: " + f)
    for b in blind:
        print("COULD NOT LOOK: " + b)
    if fails:
        return 1
    if blind:
        return 2
    print("PASS: 6 works unbuildable, %s kept, infinite deposits removed on a fresh map" % KEEP)
    return 0


if __name__ == "__main__":
    try:
        rc = main(sys.argv[1] if len(sys.argv) > 1 else "ArchBig")
    except (scene.Fault, scene.Refused) as e:  # the session could not be opened or read: never a FAIL of the mod
        print("COULD NOT LOOK: %s" % e)
        rc = 2
    sys.exit(rc)
