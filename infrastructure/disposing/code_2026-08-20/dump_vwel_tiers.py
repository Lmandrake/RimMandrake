#!/usr/bin/env python3
"""
Dump Vanilla Weapons Expanded - Laser (`vanillaexpanded.vwel`, ws 1989352844)
weapon ThingDefs as TWO SEPARATE tiers.

Why two files and not one with a column: the split is load-bearing for
`design/Jawa/worldbuilding/ship_legacy_armoury.md`, whose whole trick is that the
two tiers are NOT equal -- the salvaged tier circulates freely in the world and
the full/ultratech tier is the clan's alone. A single file invites reading them
as one roster, which is the exact mistake the design forbids.

🔴 The split is the MOD's own, not ours. The discriminator is the weaponTag:

    SalvagedLaserGun  -> salvaged   (parent BaseLaserGun)
    SpacerGun/LaserGun/UltratechMelee -> ultratech (parent VWE_BaseLaserGunUltra,
                                        or VWE_LaserSwordBase for the melee one)

That means the tiering survives a mod update without us re-deriving it, and a
weapon that changes tier upstream shows up here as a moved row rather than a
silent reclassification. Do NOT hand-assign a tier.

Reads the mod's XML on disk directly -- it does NOT need the live DefDump, so it
works with the game down and while the dump is stale.

Usage:  python3 src/RimMandrake/Utils/dump_vwel_tiers.py [--out DIR]
"""

import argparse
import glob
import json
import os
import sys
import xml.etree.ElementTree as ET

WS_ID = "1989352844"
PACKAGE_ID = "vanillaexpanded.vwel"

# The three mod roots, per skills/rimworld-start-prep. Only workshop matters here,
# but resolve rather than hardcode so a re-subscribe to a different path still works.
WORKSHOP = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"

# Game is 1.6; the mod ships 1.4/1.5/1.6 side by side and the older trees are stale.
GAME_VERSION = "1.6"

SALVAGED_TAG = "SalvagedLaserGun"


def _text(node, path, default=None):
    v = node.findtext(path)
    return v.strip() if v is not None and v.strip() else default


def _num(node, path):
    v = _text(node, path)
    if v is None:
        return None
    try:
        return float(v) if "." in v else int(v)
    except ValueError:
        return v


def collect(mod_root):
    """Return (salvaged, ultratech, projectiles) lists of dicts."""
    wdir = os.path.join(mod_root, GAME_VERSION, "Defs", "ThingDefs_Misc", "Weapons")
    if not os.path.isdir(wdir):
        sys.exit("no weapons dir at %s" % wdir)

    weapons, projectiles = [], {}
    for f in sorted(glob.glob(os.path.join(wdir, "*.xml"))):
        root = ET.parse(f).getroot()
        for td in root.findall("ThingDef"):
            # Abstract bases carry no defName and are not weapons anyone can hold.
            if td.get("Abstract") == "True" or td.findtext("defName") is None:
                continue
            defname = _text(td, "defName")
            tags = [li.text for li in td.findall(".//weaponTags/li") if li.text]

            # Projectiles are ThingDefs too. They are the `unstable` half of the
            # salvaged story, so keep them -- but keyed separately, not as weapons.
            if _text(td, "thingClass") == "Bullet" or defname.startswith("VWEL_Bullet_"):
                projectiles[defname] = {
                    "defName": defname,
                    "label": _text(td, "label"),
                    "damage": _num(td, "projectile/damageAmountBase"),
                    "armorPenetration": _num(td, "projectile/armorPenetrationBase"),
                    "speed": _num(td, "projectile/speed"),
                    "sourceFile": os.path.basename(f),
                }
                continue

            verb = td.find("verbs/li")
            weapons.append({
                "defName": defname,
                "label": _text(td, "label"),
                "techLevel": _text(td, "techLevel"),
                "parent": td.get("ParentName"),
                "weaponTags": tags,
                "marketValue": _num(td, "statBases/MarketValue"),
                "mass": _num(td, "statBases/Mass"),
                "accuracyTouch": _num(td, "statBases/AccuracyTouch"),
                "accuracyShort": _num(td, "statBases/AccuracyShort"),
                "accuracyMedium": _num(td, "statBases/AccuracyMedium"),
                "accuracyLong": _num(td, "statBases/AccuracyLong"),
                "projectile": _text(verb, "defaultProjectile") if verb is not None else None,
                "range": _num(verb, "range") if verb is not None else None,
                "warmupTime": _num(verb, "warmupTime") if verb is not None else None,
                "burstShotCount": _num(verb, "burstShotCount") if verb is not None else None,
                "isMelee": verb is None,
                "sourceFile": os.path.basename(f),
            })

    salvaged = [w for w in weapons if SALVAGED_TAG in w["weaponTags"]]
    ultratech = [w for w in weapons if SALVAGED_TAG not in w["weaponTags"]]
    return salvaged, ultratech, projectiles


def attach_projectiles(tier, projectiles):
    """Inline each weapon's projectile. The `unstable` variants ARE the tier's
    identity on the salvaged side, so a reader must not have to join two files."""
    for w in tier:
        p = projectiles.get(w.get("projectile"))
        w["projectileDetail"] = p
    return tier


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join("observed", "2026-08-13", "dumps"),
                    help="directory to write the two tier files into")
    a = ap.parse_args()

    mod_root = os.path.join(WORKSHOP, WS_ID)
    if not os.path.isdir(mod_root):
        sys.exit("vwel not installed at %s -- subscribe first (Steam writes the "
                 "folder, never the mod list)" % mod_root)

    salvaged, ultratech, projectiles = collect(mod_root)
    attach_projectiles(salvaged, projectiles)
    attach_projectiles(ultratech, projectiles)

    os.makedirs(a.out, exist_ok=True)
    written = []
    for name, tier, note in (
        ("vwel_tier_salvaged.json", salvaged,
         "Circulates freely in the world -- scavengers make these. Every entry's "
         "projectile is an `unstable` variant; that is the visible worse-ness."),
        ("vwel_tier_ultratech.json", ultratech,
         "The clan's alone. Nobody else fields this tier. Includes the laser "
         "sword (melee) and the tesla gun."),
    ):
        path = os.path.join(a.out, name)
        with open(path, "w") as fh:
            json.dump({
                "tier": name.replace("vwel_tier_", "").replace(".json", ""),
                "sourceMod": {"packageId": PACKAGE_ID, "workshopId": WS_ID,
                              "gameVersionTree": GAME_VERSION},
                "discriminator": "weaponTags contains %s" % SALVAGED_TAG,
                "note": note,
                "count": len(tier),
                "weapons": tier,
            }, fh, indent=2)
        written.append((path, len(tier)))

    for path, n in written:
        print("wrote %-52s %d weapons" % (path, n))
    print("projectiles resolved: %d" % len(projectiles))


if __name__ == "__main__":
    main()
