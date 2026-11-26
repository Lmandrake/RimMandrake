"""check_old_scar_names_load.py - live check of B_SCAR_NAMES_LOAD (RIMMANDRAKE_RENAME_KNOCKBACK_SCAR_DEFS_DIGIT_ENDING_CONFIG_ERROR).

Visit 1's walk save (EK_V020_VISIT1_WALK_20261125_D, ArchSmall) holds 20 scars under their 0.2.0 names (18
RM_KnockbackBlastCrater_3, one _5, one _20, counted in the .rws). After the rename to *_<n>Wide, loading it must keep all
20 under the new names (RM_Patch_ScarOldNames). Prints the scar names on the map and a verdict line; the caller greps
Player.log for an unresolved old name. Nothing is saved.
"""
import collections

import scene

SAVE = "EK_V020_VISIT1_WALK_20261125_D"
WANT = 20
with scene.open("ArchSmall", needs={"map": SAVE}) as s:
    size = s.read("map", "info.sizeInt")
    dims = [int(float(x)) for x in str(size.v).strip("()[] ").split(",")] if size.state == "ok" else [250, 250]
    w, h = dims[0], dims[-1]            # "x,z" or "x,y,z": the first and the last are the map's width and height
    names = []
    for z0 in range(0, h, 50):
        names += [str(v.v) for v in s.read_many(rect=(0, z0, w, min(50, h - z0)), path="def.defName")
                  if v.state == "ok" and str(v.v).startswith("RM_KnockbackBlast") and not str(v.v).startswith("RM_KnockbackBlast" + "Flash")]
    scars = [n for n in names if n.startswith(("RM_KnockbackBlastCrater_", "RM_KnockbackBlastScorch_"))]
    print("SCARS %s" % dict(collections.Counter(scars)))
    new = [n for n in scars if n.endswith("Wide")]
    print("%s OLD_NAMES_LOAD: %d of %d saved scars on the map under their Wide names" % ("PASS" if len(new) == WANT else "FAIL", len(new), WANT))
