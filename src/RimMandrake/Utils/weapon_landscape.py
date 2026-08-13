"""The full armoury landscape: where everything actually sits.

Ranged damage lives on the projectile; melee lives on tools. Unarmed lives on
the pawn's own tools. All three are pulled onto one scale so the ladder is
readable end to end.
"""
import collections
import os
import sys

# Resolved from this file, not hardcoded: the repo moved G: -> D: on 2026-08-12
# and is reached by different paths from Windows Python and WSL.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from def_diff import iter_live_defs
from game_paths import DEF_DUMP

# Was a hardcoded C:\ literal until 2026-08-13, which made this script
# unrunnable under WSL — and it failed by naming a missing ThingDef.json,
# so it read as "the dump is gone" rather than "wrong interpreter".
DUMP = os.path.join(DEF_DUMP, "defs", "ThingDef.json")

HUMAN_TORSO = 40.0   # vanilla-ish; the yardstick for every contract

proj, weapons, unarmed = {}, [], []

for d in iter_live_defs(DUMP):
    f = d.get("fields") or {}
    pr = f.get("projectile")
    if isinstance(pr, dict) and pr.get("damageAmountBase") is not None:
        proj[d.get("defName")] = (pr.get("damageAmountBase"),
                                  pr.get("armorPenetrationBase"),
                                  pr.get("damageDef"))

    # Unarmed reference: pawns with a race carry their own tools.
    isb = d.get("is") or {}
    if isb.get("pawn") and d.get("defName") in ("Human",):
        for t in (f.get("tools") or []):
            if isinstance(t, dict):
                unarmed.append((t.get("label"), t.get("power"),
                                t.get("cooldownTime"), t.get("armorPenetration")))

for d in iter_live_defs(DUMP):
    isb = d.get("is") or {}
    if not (isb.get("weapon") or isb.get("meleeWeapon") or isb.get("rangedWeapon")):
        continue
    f = d.get("fields") or {}
    dn = d.get("defName") or ""
    lab = d.get("label") or ""
    rec = {"defName": dn, "label": lab, "mod": d.get("modName") or "",
           "ranged": bool(isb.get("rangedWeapon")), "dmg": None, "ap": None,
           "type": None, "cool": None, "warm": None, "burst": None}

    for v in (f.get("verbs") or []):
        if not isinstance(v, dict):
            continue
        p = v.get("defaultProjectile")
        if isinstance(p, str) and p in proj:
            rec["dmg"], rec["ap"], rec["type"] = proj[p]
            rec["warm"] = v.get("warmupTime")
            rec["burst"] = v.get("burstShotCount")
            break
    if rec["dmg"] is None:
        best = None
        for t in (f.get("tools") or []):
            if isinstance(t, dict) and isinstance(t.get("power"), (int, float)):
                if best is None or t["power"] > best["power"]:
                    best = t
        if best:
            rec["dmg"] = best.get("power")
            rec["ap"] = best.get("armorPenetration")
            rec["cool"] = best.get("cooldownTime")
            caps = best.get("capacities")
            if isinstance(caps, list) and caps:
                rec["type"] = str(caps[0])
    if isinstance(rec["dmg"], (int, float)):
        weapons.append(rec)

blob = lambda w: (w["defName"] + " " + w["label"] + " " + w["mod"]).lower()


def category(w):
    b = blob(w)
    if "turret" in b or "emplacement" in b:
        return "TURRET"
    if not w["ranged"]:
        if "lightsaber" in b or "saber" in b or "lightfoil" in b:
            return "MELEE lightsaber"
        if "vibro" in b or "vibra" in b:
            return "MELEE vibro"
        if any(s in b for s in ("spear", "club", "axe", "sword", "knife",
                                "mace", "staff", "blade", "gladius", "pike")):
            return "MELEE conventional"
        return "MELEE other"
    t = (w["type"] or "").lower()
    if any(s in t for s in ("ion", "emp", "disrupt", "sonic", "stun", "shock")) \
       or any(s in b for s in ("ion", "emp", "stun", "sonic", "disruptor")):
        return "EXOTIC disable"
    if "bomb" in t or "explos" in t or any(s in b for s in ("rocket", "missile",
                                                            "launcher", "grenade")):
        return "EXPLOSIVE"
    if "flame" in t or "fire" in t or "flame" in b:
        return "INCENDIARY"
    if any(s in t for s in ("blaster", "energy", "laser", "plasma", "turbolaser")):
        return "RANGED blaster"
    if any(s in t for s in ("bullet", "arrow", "stab", "cut", "blunt")):
        return "RANGED kinetic"
    return "RANGED other"


by = collections.defaultdict(list)
for w in weapons:
    by[category(w)].append(w)

print("=== HAND-TO-HAND (Human, the floor of the whole ladder) ===")
for lab, p, c, ap in unarmed:
    print("   %-18s power=%-5s cooldown=%-5s ap=%s" % (lab, p, c, ap))

print("\n=== THE ARMOURY BY CATEGORY  (torso ~%.0f HP) ===" % HUMAN_TORSO)
print("   %-20s %5s %7s %7s %7s %7s   %s"
      % ("category", "n", "min", "median", "p90", "max", "shots-to-kill @median"))
order = ["MELEE other", "MELEE conventional", "MELEE vibro", "MELEE lightsaber",
         "RANGED kinetic", "RANGED blaster", "RANGED other", "EXOTIC disable",
         "INCENDIARY", "EXPLOSIVE", "TURRET"]
for cat in order:
    ws = by.get(cat) or []
    if not ws:
        continue
    ds = sorted(w["dmg"] for w in ws)
    med = ds[len(ds) // 2]
    stk = ("%.1f" % (HUMAN_TORSO / med)) if med > 0 else "n/a"
    print("   %-20s %5d %7.0f %7.0f %7.0f %7.0f   %s"
          % (cat, len(ds), ds[0], med, ds[int(len(ds) * .9)], ds[-1], stk))

print("\n=== THE LADDER: best examples at each rung ===")
for cat in order:
    ws = sorted(by.get(cat) or [], key=lambda w: -w["dmg"])[:4]
    if not ws:
        continue
    print("  %s" % cat)
    for w in ws:
        print("     %6.0f ap=%-6s %-30s %-20s %s"
              % (w["dmg"], str(w["ap"])[:6], w["defName"][:30],
                 str(w["type"])[:20], w["mod"][:22]))

print("\n=== THE STRANGE ONES (non-damage / utility verbs already present) ===")
seen = set()
for w in sorted(by.get("EXOTIC disable") or [], key=lambda w: w["dmg"]):
    key = (w["type"], w["mod"])
    if key in seen:
        continue
    seen.add(key)
    print("   %6.0f  %-30s %-26s %s"
          % (w["dmg"], w["defName"][:30], str(w["type"])[:26], w["mod"][:24]))
