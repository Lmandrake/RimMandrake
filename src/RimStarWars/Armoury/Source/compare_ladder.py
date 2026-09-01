"""Before/after ladder: ranged vs melee vs missile, after the patches.

New values are read back OUT of the generated patch XML rather than recomputed,
so this measures what will actually ship, not what the generator intended.
"""
import collections
import glob
import os
import sys
import xml.etree.ElementTree as ET

# 🔴 WALK UP TO A MARKER; DO NOT COUNT "..". This file counted five of them and
# the 2026-08-13 restructure changed its depth, so the path landed above the repo
# and `from def_diff import ...` died with ModuleNotFoundError. The generator
# carries the same lesson in its own header — this script was simply missed.
# A marker file cannot miscount.
def _find_repo_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".git")) or \
           os.path.isfile(os.path.join(d, "CLAUDE.md")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError(
                "could not find the repo root above %s - no .git or CLAUDE.md "
                "on any parent. Refusing to guess." % start)
        d = parent


_REPO_ROOT = _find_repo_root(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "src", "RimMandrake", "Utils"))
from def_diff import iter_live_defs
# ⚠️ And the dump path was a bare C:\ literal, which dies under WSL python3 with a
# FileNotFoundError naming ThingDef.json - reading as "take a fresh dump" when the
# dump is present and only the interpreter is wrong. game_paths resolves it.
import game_paths as _GP
DUMP = os.path.join(_GP.DEF_DUMP, "defs", "ThingDef.json")
PATCHES = os.path.join(_REPO_ROOT, "src", "RimStarWars", "Armoury",
                       "Patches", "*.xml")
TORSO = 40.0

# ---- read the patches back ----------------------------------------------
new_dmg, new_power, new_speed = {}, {}, {}
for path in glob.glob(PATCHES):
    root = ET.parse(path).getroot()
    for li in root.iter():
        if li.get("Class") != "PatchOperationReplace":
            continue
        xp = (li.findtext("xpath") or "")
        val = li.find("value")
        if val is None or not len(val):
            continue
        tag, txt = val[0].tag, (val[0].text or "").strip()
        try:
            num = float(txt)
        except ValueError:
            continue
        # /Defs/ThingDef[defName="X"]/... or [@Name="X"]/...
        key = xp.split('"')[1] if '"' in xp else None
        if key is None:
            continue
        if tag == "damageAmountBase":
            new_dmg[key] = num
        elif tag == "speed":
            new_speed[key] = num
        elif tag == "power":
            lab = xp.split('label="')[1].split('"')[0] if 'label="' in xp else ""
            new_power.setdefault(key, {})[lab] = num
print("patch ops read: %d damage, %d speed, %d melee declarers"
      % (len(new_dmg), len(new_speed), len(new_power)))

# ---- live data -----------------------------------------------------------
proj, weapons = {}, []
for d in iter_live_defs(DUMP):
    f = d.get("fields") or {}
    pr = f.get("projectile")
    if isinstance(pr, dict) and isinstance(pr.get("damageAmountBase"), (int, float)):
        proj[d.get("defName")] = {"dmg": pr["damageAmountBase"],
                                  "speed": pr.get("speed"),
                                  "rad": pr.get("explosionRadius") or 0,
                                  "type": pr.get("damageDef") or ""}
    isb = d.get("is") or {}
    if isb.get("weapon") or isb.get("meleeWeapon") or isb.get("rangedWeapon"):
        w = {"defName": d.get("defName") or "", "label": d.get("label") or "",
             "mod": d.get("modName") or "", "ranged": bool(isb.get("rangedWeapon")),
             "proj": None, "tools": [], "parent": None}
        for v in (f.get("verbs") or []):
            if isinstance(v, dict) and isinstance(v.get("defaultProjectile"), str):
                w["proj"] = v["defaultProjectile"]
                break
        for t in (f.get("tools") or []):
            if isinstance(t, dict) and isinstance(t.get("power"), (int, float)):
                w["tools"].append((t.get("label"), t["power"]))
        weapons.append(w)

SW = ("Star Wars KotOR Weapons and Armor", "Outer Rim - Core",
      "Outer Rim - Droid Depot", "[JDS] StarWars - Armory",
      "Star Wars : The Force - Lightsaber")


def after_ranged(w):
    p = proj.get(w["proj"])
    if not p:
        return None, None
    d = new_dmg.get(w["proj"], p["dmg"])
    return p["dmg"], d


def after_melee(w):
    """Melee patches target the DECLARER, so match by weapon or its base."""
    old = max((p for _, p in w["tools"]), default=None)
    if old is None:
        return None, None
    # direct hit
    if w["defName"] in new_power:
        return old, max(new_power[w["defName"]].values())
    # inherited: find a declarer whose labels match this weapon's labels
    labs = {l for l, _ in w["tools"] if l}
    for owner, m in new_power.items():
        if labs and labs <= set(m):
            return old, max(m.values())
    return old, old


def bucket(w):
    b = (w["defName"] + " " + w["label"]).lower()
    p = proj.get(w["proj"]) or {}
    t = (p.get("type") or "").lower()
    if not w["ranged"]:
        if "saber" in b or "foil" in b:
            return "MELEE lightsaber"
        if "vibro" in b or "vibra" in b:
            return "MELEE vibro"
        return "MELEE conventional"
    if any(m in b for m in ("rocket", "missile", "torpedo")):
        return "MISSILE"
    if any(v in b + t for v in ("ion", "stun", "emp", "sonic", "disrupt")):
        return "VERB (untouched)"
    if "turbolaser" in b + t:
        return "RANGED turbolaser"
    if any(s in b + t for s in ("slug", "cycler", "shatter", "massdriver")):
        return "RANGED slugthrower"
    if any(s in b for s in ("heavy", "cannon", "repeater")):
        return "RANGED blaster heavy"
    return "RANGED blaster"


rows = collections.defaultdict(list)
for w in weapons:
    if w["mod"] not in SW:
        continue
    old, new = (after_melee(w) if not w["ranged"] else after_ranged(w))
    if old is None or new is None:
        continue
    rows[bucket(w)].append((old, new, w))

ORDER = ["MELEE conventional", "RANGED slugthrower", "RANGED blaster",
         "MELEE vibro", "RANGED blaster heavy", "MELEE lightsaber",
         "MISSILE", "RANGED turbolaser", "VERB (untouched)"]

print()
print("=" * 84)
print("THE LADDER, BEFORE -> AFTER   (human fist = 8.2, unarmoured torso = 40 HP)")
print("=" * 84)
print("  %-24s %4s | %13s | %13s | %s"
      % ("class", "n", "median before", "median after", "shots-to-kill"))
for cat in ORDER:
    ws = rows.get(cat) or []
    if not ws:
        continue
    ob = sorted(o for o, _, _ in ws)
    na = sorted(n for _, n, _ in ws)
    mb, ma = ob[len(ob) // 2], na[len(na) // 2]
    stk_b = ("%.1f" % (TORSO / mb)) if mb > 0 else "n/a"
    stk_a = ("%.1f" % (TORSO / ma)) if ma > 0 else "n/a"
    print("  %-24s %4d | %6.0f  (%3.0f-%4.0f) | %6.0f  (%4.0f-%4.0f) | %s -> %s"
          % (cat, len(ws), mb, ob[0], ob[-1], ma, na[0], na[-1], stk_b, stk_a))

print()
print("=" * 84)
print("MISSILES: damage is not the story -- area and speed are")
print("=" * 84)
print("  %-34s %5s %6s %7s  %s" % ("projectile", "dmg", "radius", "speed", "reach"))
for pname in sorted(proj):
    if not any(m in pname.lower() for m in ("rocket", "missile", "torpedo")):
        continue
    p = proj[pname]
    sp_new = new_speed.get(pname, p["speed"])
    if p["rad"] < 0.5:
        continue
    cells = 3.14159 * p["rad"] ** 2
    print("  %-34s %5s %6.1f %4s->%-3s  %.0f cells"
          % (pname[:34], p["dmg"], p["rad"], p["speed"], int(sp_new), cells))

print()
print("=" * 84)
print("WHAT A PERSON SURVIVES  (single hit on an unarmoured torso, ~40 HP)")
print("=" * 84)
ex = [("human fist", 8.2), ("club / vibro-less melee", 22)]
for cat in ("RANGED slugthrower", "RANGED blaster", "MELEE vibro",
            "RANGED blaster heavy", "MELEE lightsaber"):
    ws = rows.get(cat) or []
    if ws:
        na = sorted(n for _, n, _ in ws)
        ex.append((cat, na[len(na) // 2]))
for name, dmg in ex:
    bar = "#" * min(60, int(dmg / 2))
    verdict = ("survives" if dmg < TORSO * 0.5
               else "downed" if dmg < TORSO else "KILLED OUTRIGHT")
    print("  %-24s %6.0f  %-32s %s" % (name, dmg, bar, verdict))
