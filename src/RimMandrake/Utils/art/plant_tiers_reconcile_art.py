#!/usr/bin/env python3
"""plant_tiers_reconcile_art.py - PLANT_TIERS_RECONCILE_MOST_ARE_BAROQUE, the art half of retiring RUT plant twins.

The nonrm_plants_census sheet (2026-10-16) ruled art on RUT_ rows whose RM_ twin takes over. `art.py enact`
installed his pool picks under the RUT_ texPath; this moves them to the RM_ twin's texPath, and retires the RUT_
copies whose exact bytes already live at the RM_ twin. Every write goes through the art ledger (install/retire),
never a file copy. Distinct RUT_-only pictures are left where they are and listed.

    python3 src/RimMandrake/Utils/art/plant_tiers_reconcile_art.py            # plan
    python3 src/RimMandrake/Utils/art/plant_tiers_reconcile_art.py --apply
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402

ROOT = HERE.parents[3]
ME = "script:src/RimMandrake/Utils/art/plant_tiers_reconcile_art.py"
OWNER = ("Completed Plants in the Star Wars and Utinni Tier. Please apply these choices, and then make sure to "
         "sync the art properly between you and Foundry.")

UP = "src/RimUtinni/UtinniPatches/Textures/Things/Plant"
AF = "src/RimUtinni/AshkarrFlora/Textures/Things/Plant"
SB = "src/RimStarWars/SWBestiary/Textures/Things/Plant"
# (RUT_ folder, RM_ folder, RUT_ file prefix, RM_ file prefix)
PAIRS = [
    (f"{UP}/GiantLeaf", "src/RimMandrake/FeverWood/Textures/Things/Plant/RM_GiantLeaf", "GiantLeaf_", "RM_GiantLeaf_"),
    (f"{UP}/RUT_Glower", "src/RimMandrake/Scarlands/Textures/Things/Plant/RM_Glower", "RUT_Glower_", "RM_Glower_"),
    (f"{UP}/FireLavender", "src/RimMandrake/TheForge/Textures/Things/Plant/FireLavender", "FireLavender_", "FireLavender_"),
    (f"{UP}/HeatsinkFungus", "src/RimMandrake/TheForge/Textures/Things/Plant/HeatsinkFungus", "HeatsinkFungus_", "HeatsinkFungus_"),
    (f"{UP}/ScorchedStars", "src/RimMandrake/Scarlands/Textures/Things/Plant/RM_ScorchedStars", "ScorchedStars_", "RM_ScorchedStars_"),
    (f"{AF}/RUT_WildHealroot", "src/RimMandrake/LeaningScrub/Textures/Things/Plant/RM_WildHealroot", "RUT_WildHealroot_", "RM_WildHealroot_"),
    (f"{AF}/RUT_Grellspine", "src/RimMandrake/LeaningScrub/Textures/Things/Plant/RM_Grellspine", "RUT_Grellspine_", "RM_Grellspine_"),
    (f"{AF}/RUT_SweetlineTree", "src/RimMandrake/LeaningScrub/Textures/Things/Plant/RM_SweetlineTree", "RUT_SweetlineTree", "RM_SweetlineTree"),
    # MOVE to Baroque (new RM_ defNames, so the texPath folder moves with them)
    (f"{UP}/RUT_BloomCrop", "src/RimMandrake/ExplosiveGrowth/Textures/Things/Plant/RM_BloomCrop", "RUT_BloomCrop_", "RM_BloomCrop_"),
    (f"{UP}/RUT_DyingCreep", "src/RimMandrake/Contagion/Textures/Things/Plant/RM_DyingCreep", "RUT_DyingCreep_", "RM_DyingCreep_"),
    ("src/RimUtinni/UtinniPatches/Textures/Things/Filth/RUT_DeadCreep", "src/RimMandrake/Contagion/Textures/Things/Filth/RM_DeadCreep", "RUT_DeadCreep_", "RM_DeadCreep_"),
    (f"{SB}/RSW_SurraGrass", "src/RimMandrake/LongShade/Textures/Things/Plant/RM_SurraGrass", "RSW_SurraGrass_", "RM_SurraGrass_"),
    (f"{SB}/RSW_VellaraBloom", "src/RimMandrake/LongShade/Textures/Things/Plant/RM_VellaraBloom", "RSW_VellaraBloom", "RM_VellaraBloom"),
]


def plan():
    moves, retires, kept = [], [], []
    for rut, rm, rp, mp in PAIRS:
        rut_d, rm_d = ROOT / rut, ROOT / rm
        rm_shas = {L.sha256_file(p): p for p in rm_d.glob("*.png")}
        for p in sorted(rut_d.glob("*.png")):
            sha = L.sha256_file(p)
            if sha in rm_shas:
                retires.append(p)
                continue
            dest = rm_d / (mp + p.name[len(rp):])
            if dest.exists():
                kept.append((p, f"distinct, and {dest.name} is taken at the RM_ twin"))
                continue
            moves.append((p, dest, sha))
    return moves, retires, kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    moves, retires, kept = plan()
    for src, dest, sha in moves:
        print(f"move   {src.relative_to(ROOT)} -> {dest.relative_to(ROOT)}  {sha[:12]}")
        if a.apply:
            mod, rel = L.locate(dest)
            L.install(mod, rel, L.store_put_file(src), reason=ME)
            retires.append(src)
    for p in retires:
        print(f"retire {p.relative_to(ROOT)}")
        if a.apply:
            L.retire(p, reason=ME, owner_said=OWNER if L.cached_index().protected(L.sha256_file(p)) else None)
    for p, why in kept:
        print(f"KEPT   {p.relative_to(ROOT)}: {why}")
    print(f"{len(moves)} move(s), {len(retires)} retire(s), {len(kept)} kept{'' if a.apply else ' — DRY RUN'}")


if __name__ == "__main__":
    main()
