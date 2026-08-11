"""Generate the armoury retune patch from the live dump + the offline load set.

Generated, not hand-written: hundreds of defs, and the tier map moves as the
paradigm does. A generator can be re-run; a hand-edit cannot.

Targets (worldbuilding/setting_physics.md, torso ~40 HP):
  standard blaster   24-34    1-2 shots unarmoured, ~5 vs advanced armour
  heavy blaster      52-72    breaks the 5-shot contract
  slugthrower        18-36    spread wide; the desert-megafauna answer (L11)
  lightsaber         80-120   supreme vs flesh, useless vs vehicle plate (L3)
  vibro              35-52    high AP vs ablative (L14)
  turbolaser        800-2000  two orders above personal (L9)
  ion/stun/sonic     UNCHANGED -- the verb is the weapon (L4/L16)
  explosives         UNCHANGED -- balanced by scarcity alone (L13)

TWO MISTAKES THIS SCRIPT ENCODES, both found by reading its own output:

1. Projectiles are SHARED. Ranking WEAPONS and writing the result onto their
   projectiles let one heavy rifle drag all of KotOR to 66, and inverted
   Low_Blue_Blaster_Bolt (11->66) above High_Blue (25->34). Ranged damage is a
   property of the projectile, so the PROJECTILE is the unit of work. Ordering
   inside a family then survives by construction.

2. Patches hit RAW XML, BEFORE inheritance. All 15 lightsabers inherit tools
   from the abstract Force_LightsaberBase and declare none, so an xpath naming
   a concrete saber matches nothing and throws a red error every launch. Aim at
   the DECLARER -- which also collapses 15 operations into 1.
"""
import collections
import io
import os
import sys

sys.path.insert(0, r"G:\My Drive\Personal\Rimworld\Utils")
from def_diff import iter_live_defs
from def_inventory import build as build_offline, D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA

DUMP = (r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios"
        r"\RimWorld by Ludeon Studios\DefDump\defs\ThingDef.json")
OUTDIR = r"G:\My Drive\Personal\Rimworld\custom_patches\Jawa_Armoury\Patches"

SW_MODS = ("Star Wars KotOR Weapons and Armor", "Outer Rim - Core",
           "Outer Rim - Droid Depot", "[JDS] StarWars - Armory",
           "Star Wars : The Force - Lightsaber")
VERB_MARKERS = ("ion", "stun", "emp", "sonic", "disrupt", "electr", "shock",
                "extinguish", "smoke", "gas", "tear", "foam", "net", "web")
BANDS = {"blaster": (24, 34), "blaster_heavy": (52, 72), "slugthrower": (18, 36),
         "turbolaser": (800, 2000), "lightsaber": (80, 120), "vibro": (35, 52)}

# ---------------------------------------------------------------- collect
projectiles, weapons = {}, []
for d in iter_live_defs(DUMP):
    f = d.get("fields") or {}
    pr = f.get("projectile")
    if isinstance(pr, dict) and isinstance(pr.get("damageAmountBase"), (int, float)):
        projectiles[d.get("defName")] = {"mod": d.get("modName") or "",
                                         "dmg": pr["damageAmountBase"],
                                         "type": pr.get("damageDef") or ""}
    isb = d.get("is") or {}
    if isb.get("weapon") or isb.get("meleeWeapon") or isb.get("rangedWeapon"):
        w = {"defName": d.get("defName") or "", "label": d.get("label") or "",
             "mod": d.get("modName") or "", "ranged": bool(isb.get("rangedWeapon")),
             "proj": None, "tools": []}
        for v in (f.get("verbs") or []):
            if isinstance(v, dict) and isinstance(v.get("defaultProjectile"), str):
                w["proj"] = v["defaultProjectile"]
                break
        for t in (f.get("tools") or []):
            if isinstance(t, dict) and isinstance(t.get("power"), (int, float)):
                w["tools"].append((t.get("label"), t["power"]))
        weapons.append(w)

sw_weapons = [w for w in weapons if w["mod"] in SW_MODS]
sw_proj = collections.defaultdict(list)
for w in sw_weapons:
    if w["proj"] in projectiles:
        sw_proj[w["proj"]].append(w)
print("SW weapons %d | SW projectiles %d" % (len(sw_weapons), len(sw_proj)))


def is_verb(b):
    return any(v in b for v in VERB_MARKERS)


def classify(pname, p, users):
    b = (pname + " " + p["type"]).lower()
    if is_verb(b):
        return None
    if users and all(is_verb((u["defName"] + " " + u["label"]).lower()) for u in users):
        return None
    if any(s in b for s in ("grenade", "missile", "rocket", "bomb", "charge")):
        return None
    if p["dmg"] <= 0:
        return None
    if "turbolaser" in b:
        return "turbolaser"
    if any(s in b for s in ("slug", "cycler", "shatter", "massdriver", "bowcaster")):
        return "slugthrower"
    if any(s in b for s in ("heavy", "cannon", "repeater")):
        return "blaster_heavy"
    if any(s in b for s in ("blaster", "bolt", "laser", "energy", "plasma")):
        return "blaster"
    return None


def spread(items, band):
    """Map values across the band, PRESERVING their existing order."""
    lo, hi = band
    items = sorted(items, key=lambda kv: kv[1])
    n = len(items)
    out = {}
    for i, (k, old) in enumerate(items):
        frac = (i / (n - 1.0)) if n > 1 else 0.5
        out[k] = (old, int(round(lo + (hi - lo) * frac)))
    return out


groups = collections.defaultdict(list)
for pname, users in sw_proj.items():
    r = classify(pname, projectiles[pname], users)
    if r:
        groups[r].append((pname, projectiles[pname]["dmg"]))
proj_changes = {}
for r, items in groups.items():
    proj_changes.update(spread(items, BANDS[r]))

melee_groups = collections.defaultdict(list)
for w in sw_weapons:
    if w["ranged"] or not w["tools"]:
        continue
    b = (w["defName"] + " " + w["label"]).lower()
    if is_verb(b):
        continue
    r = ("lightsaber" if ("saber" in b or "foil" in b)
         else "vibro" if ("vibro" in b or "vibra" in b) else None)
    if r:
        melee_groups[r].append((w["defName"], max(p for _, p in w["tools"])))
tool_changes = {}
for r, items in melee_groups.items():
    tool_changes.update(spread(items, BANDS[r]))

for r in sorted(groups):
    print("  %-14s %3d projectiles -> %s" % (r, len(groups[r]), BANDS[r]))
for r in sorted(melee_groups):
    print("  %-14s %3d weapons     -> %s" % (r, len(melee_groups[r]), BANDS[r]))

# ---------------------------------------------------------------- declarers
print("resolving declarers (offline)...")
ds = build_offline(D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA, types=("ThingDef",))


def _elem(x):
    """ds.by_name yields raw Elements; ds.get yields DefRecords. Normalise."""
    return getattr(x, "own", x)


def declarer_of(defname, node):
    """
    Who actually DECLARES <node>: this def, or the nearest ancestor.

    Returns (ownerName, 'defName'|'Name', declaringElement). The element comes
    back too, because the caller needs to read the real values it declares --
    not the inheritance-resolved ones, which is what a patch would overwrite.
    """
    rec = ds.get("ThingDef", defname)
    if rec is None:
        return None, None, None
    if rec.own.find(node) is not None:
        return defname, "defName", rec.own

    seen = set()
    parent_name = rec.parentName
    while parent_name and parent_name not in seen:
        seen.add(parent_name)
        pel = _elem(ds.by_name.get(parent_name))
        if pel is None:
            return None, None, None
        if pel.find(node) is not None:
            return parent_name, "Name", pel
        parent_name = pel.get("ParentName")
    return None, None, None


NL = "\n"
HDR = ('<?xml version="1.0" encoding="utf-8"?>' + NL +
       '<!-- %s' + NL +
       '     GENERATED by custom_patches/Jawa_Armoury/Source/gen_armoury_patch.py.' + NL +
       '     Do not hand-edit; re-run the generator.' + NL +
       '     Rationale: worldbuilding/setting_physics.md + balance_paradigm.md -->' + NL +
       '<Patch>' + NL)


def repl(xpath, tag, value):
    return ('        <li Class="PatchOperationReplace">' + NL +
            '          <xpath>' + xpath + '</xpath>' + NL +
            '          <value><%s>%d</%s></value>' % (tag, value, tag) + NL +
            '        </li>' + NL)


def emit(fh, title, by_mod):
    fh.write(HDR % title)
    for mod, ops in sorted(by_mod.items()):
        # Unguarded, a Replace whose target mod is absent logs a red error on
        # every launch. This mod must stay droppable.
        fh.write(NL + '  <Operation Class="PatchOperationFindMod">' + NL)
        fh.write('    <mods><li>' + mod + '</li></mods>' + NL)
        fh.write('    <match Class="PatchOperationSequence">' + NL)
        fh.write('      <operations>' + NL)
        for o in ops:
            fh.write(o)
        fh.write('      </operations>' + NL)
        fh.write('    </match>' + NL + '  </Operation>' + NL)
    fh.write(NL + '</Patch>' + NL)


os.makedirs(OUTDIR, exist_ok=True)

ranged_by_mod = collections.defaultdict(list)
missing = []
for pname, (old, new) in sorted(proj_changes.items()):
    owner, attr, _rec = declarer_of(pname, "projectile")
    if owner is None:
        missing.append(pname)
        continue
    sel = '[defName="%s"]' % owner if attr == "defName" else '[@Name="%s"]' % owner
    ranged_by_mod[projectiles[pname]["mod"]].append(
        '        <!-- %s : %s -> %d -->' % (pname, old, new) + NL +
        repl('/Defs/ThingDef' + sel + '/projectile/damageAmountBase',
             'damageAmountBase', new))

with io.open(os.path.join(OUTDIR, "Armoury_RangedDamage.xml"), "w", encoding="utf-8") as fh:
    emit(fh, "Ranged: restretch the ladder (L1, L7, L9, L11)", ranged_by_mod)

wmap = {w["defName"]: w for w in sw_weapons}
melee_by_mod = collections.defaultdict(list)
seen_decl, mel_missing = set(), []
for dn, (old, new) in sorted(tool_changes.items()):
    owner, attr, rec = declarer_of(dn, "tools")
    if owner is None:
        mel_missing.append(dn)
        continue
    if owner in seen_decl:
        continue                      # one declarer serves every child
    seen_decl.add(owner)
    sel = '[defName="%s"]' % owner if attr == "defName" else '[@Name="%s"]' % owner
    factor = (new / float(old)) if old else 1.0
    ops = []
    for li in list(rec.find("tools")):
        lab, pw = li.findtext("label"), li.findtext("power")
        if not lab or pw is None:
            continue
        try:
            newp = int(round(float(pw) * factor))
        except ValueError:
            continue
        ops.append('        <!-- %s / %s : %s -> %d -->' % (owner, lab, pw, newp) + NL +
                   repl('/Defs/ThingDef' + sel + '/tools/li[label="' + lab + '"]/power',
                        'power', newp))
    if ops:
        melee_by_mod[wmap[dn]["mod"]].extend(ops)

with io.open(os.path.join(OUTDIR, "Armoury_MeleePower.xml"), "w", encoding="utf-8") as fh:
    emit(fh, "Melee: lightsabers decisive vs flesh (L3); vibro anti-ablative (L14)",
         melee_by_mod)

print("ranged ops %d in %d groups | melee declarers %d in %d groups"
      % (sum(len(v) for v in ranged_by_mod.values()), len(ranged_by_mod),
         len(seen_decl), len(melee_by_mod)))
if missing:
    print("  ranged skipped (no declarer):", missing[:6])
if mel_missing:
    print("  melee skipped (no declarer):", mel_missing[:6])
