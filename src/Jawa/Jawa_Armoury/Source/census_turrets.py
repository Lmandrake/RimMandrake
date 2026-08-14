#!/usr/bin/env python3
"""
census_turrets.py — what every turret in the live load set actually hits for.

WHY THIS EXISTS. gen_armoury_patch.py has an "emplacement" rung, and it decides
membership from a four-name list:

    TURRET_MODS = ("Giant imperial turret", "Rah's Vanilla Turrets Expansion",
                   "Wall Mounted Turrets Version 2",
                   "Vanilla Furniture Expanded - Security")

The live dump carries turrets from THIRTY mods. So the rung was never a survey of
emplacements; it was a survey of four mods someone happened to name, and every
other turret in the game sits wherever its own author left it. This script is the
survey, so the rung can be set from the distribution rather than from a guess.

⚠️ COUNT THE BUILDINGS, NOT THE NAMES. 530 ThingDefs match "turret" by defName or
label; only 142 are real turret buildings. The other ~388 are blueprints, frames,
minified versions, the gun defs themselves and art. The authority is
`fields.building.turretGunDef`, which is a defName string pointing at a SEPARATE
ThingDef — the gun. Name matching over-selects by about 4x and would drag
blueprints onto the damage ladder.

THE JOIN, which is three hops and not one:
    turret building .fields.building.turretGunDef  -> gun defName
    gun            .fields.verbs[].defaultProjectile -> projectile defName
    projectile     .fields.projectile.damageAmountBase -> the number we tune

Damage is a property of the PROJECTILE, never the weapon — the generator learned
that the expensive way, and it is why one heavy rifle once dragged all of KotOR
to 66. This script reports the projectile and how many DISTINCT weapons fire it,
because a projectile shared with a hand weapon must never be promoted to the
emplacement rung: doing so silently buffs the personal gun too.

    python3 census_turrets.py            # summary by mod
    python3 census_turrets.py --full     # every turret, one line each
"""

import collections
import os
import sys

def _find_repo_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".git")) or \
           os.path.isfile(os.path.join(d, "CLAUDE.md")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError("no repo root above %s" % start)
        d = parent


_ROOT = _find_repo_root(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(_ROOT, "src", "RimMandrake", "Utils"))
from def_diff import iter_live_defs            # noqa: E402
import game_paths as _GP                        # noqa: E402

DUMP = os.path.join(_GP.LOCALLOW, "DefDump", "defs", "ThingDef.json")

# Mods the generator already places on the emplacement rung, as of today.
KNOWN = {"Giant imperial turret", "Rah's Vanilla Turrets Expansion",
         "Wall Mounted Turrets Version 2", "Vanilla Furniture Expanded - Security"}

# A projectile carrying one of these is not on the damage ladder at all: the
# verb IS the weapon (setting_physics L4/L16), and explosives are balanced by
# scarcity (L13). Same markers the generator uses, kept in step deliberately.
VERB_MARKERS = ("ion", "stun", "emp", "sonic", "disrupt", "electr", "shock",
                "extinguish", "smoke", "gas", "tear", "foam", "net", "web")
BLAST_MARKERS = ("grenade", "missile", "rocket", "bomb", "charge", "shell",
                 "mortar", "artillery")


def main():
    full = "--full" in sys.argv

    buildings, guns, projectiles = {}, {}, {}
    verb_users = collections.defaultdict(set)   # projectile -> weapons firing it

    for d in iter_live_defs(DUMP):
        f = d.get("fields") or {}
        dn = d.get("defName")
        bld = f.get("building")
        if isinstance(bld, dict) and bld.get("turretGunDef"):
            buildings[dn] = (d.get("modName") or "?", d.get("label") or dn,
                             bld["turretGunDef"])
        verbs = f.get("verbs")
        if verbs:
            guns[dn] = (d.get("modName") or "?", verbs)
            for v in verbs:
                if isinstance(v, dict) and v.get("defaultProjectile"):
                    verb_users[v["defaultProjectile"]].add(dn)
        pj = f.get("projectile")
        if isinstance(pj, dict):
            projectiles[dn] = (d.get("modName") or "?",
                               pj.get("damageAmountBase"),
                               pj.get("damageDef"),
                               pj.get("armorPenetrationBase"))

    rows = []
    for bdn, (mod, label, gundn) in buildings.items():
        g = guns.get(gundn)
        if not g:
            rows.append((mod, label, bdn, gundn, None, None, None, 0, "GUN DEF MISSING"))
            continue
        for v in g[1]:
            if not isinstance(v, dict):
                continue
            pdn = v.get("defaultProjectile")
            if not pdn:
                continue
            p = projectiles.get(pdn)
            dmg = p[1] if p else None
            burst = v.get("burstShotCount") or 1
            note = ""
            blob = (pdn + " " + str(p[2] if p else "")).lower()
            if any(k in blob for k in VERB_MARKERS):
                note = "verb weapon - OFF LADDER"
            elif any(k in blob for k in BLAST_MARKERS):
                note = "explosive - OFF LADDER"
            shared = len(verb_users.get(pdn) or ())
            if not note and shared > 1:
                note = "projectile shared by %d weapons" % shared
            rows.append((mod, label, bdn, gundn, pdn, dmg, burst, shared, note))

    print("turret buildings: %d   distinct mods: %d"
          % (len(buildings), len({r[0] for r in rows})))

    by_mod = collections.defaultdict(list)
    for r in rows:
        by_mod[r[0]].append(r)

    print("\n%-42s %5s %7s %7s %7s  %s"
          % ("mod", "turr", "minDmg", "medDmg", "maxDmg", "on the rung today?"))
    for mod in sorted(by_mod, key=lambda m: -len(by_mod[m])):
        rs = by_mod[mod]
        dmgs = sorted(x[5] for x in rs if isinstance(x[5], (int, float)) and x[5] > 0)
        if dmgs:
            lo, mid, hi = dmgs[0], dmgs[len(dmgs) // 2], dmgs[-1]
        else:
            lo = mid = hi = 0
        print("%-42s %5d %7s %7s %7s  %s"
              % (mod[:42], len(rs), lo, mid, hi,
                 "YES" if mod in KNOWN else "no - UNTUNED"))

    off = [r for r in rows if "OFF LADDER" in r[8]]
    shared = [r for r in rows if r[7] > 1 and "OFF LADDER" not in r[8]]
    print("\noff the ladder by design (verb weapons + explosives): %d" % len(off))
    print("projectiles shared with another weapon (must NOT be promoted): %d"
          % len(shared))
    for r in sorted({(r[4], r[7]) for r in shared}):
        print("    %-40s fired by %d weapons" % r)

    if full:
        print("\n%-38s %-30s %7s %5s  %s"
              % ("turret", "projectile", "dmg", "burst", "note"))
        for r in sorted(rows, key=lambda r: (r[0], -(r[5] or 0))):
            print("%-38s %-30s %7s %5s  %s"
                  % (r[1][:38], str(r[4])[:30], r[5], r[6], r[8]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
