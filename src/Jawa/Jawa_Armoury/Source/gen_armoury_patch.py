"""Generate the armoury retune patch from the live dump + the offline load set.

Generated, not hand-written: hundreds of defs, and the tier map moves as the
paradigm does. A generator can be re-run; a hand-edit cannot.

Targets (design/Jawa/worldbuilding/setting_physics.md, torso ~40 HP):
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

2. Patches hit RAW XML, BEFORE inheritance. Aim at whoever DECLARES the node,
   not at the def you mean, or the xpath matches nothing.

   ...but only where the children really inherit. This script used to say "all
   15 lightsabers inherit tools from Force_LightsaberBase", and that was WRONG:
   KotOR Weapons injects <tools Inherit="False"> onto 8 of them at patch time,
   discarding the base's list. Aiming at the base for those 8 applied cleanly,
   logged nothing, and was thrown away -- 8 sabers kept power 26 and AP -1 while
   the other 7 went to 99 and 0. Offline inheritance cannot see another mod's
   PatchOperations; only the live dump can. Compare live tool labels against the
   declarer's and aim at the concrete defName when they differ.

3. The live dump contains OUR OWN output once our mods are loaded, and this
   script maps old -> new, so it can eat its own tail: 28 -> 99 on the first
   run, then 99 -> 34 on the second, reverting itself in silence. Every anchor
   goes through anchor()/tool_anchors(), which substitutes the recorded
   pre-patch original wherever we write. See src/RimMandrake/Utils/patch_provenance.py.
"""
import collections
import io
import os
import sys

# Resolved from this file, not hardcoded: the repo moved G: -> D: on 2026-08-12
# and is reached by different paths from Windows Python and WSL.
_REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO_ROOT, "src", "RimMandrake", "Utils"))
from def_diff import iter_live_defs
from def_inventory import build as build_offline, D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA
from patch_provenance import guard, OurWrites, Recorder

DUMP = (r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios"
        r"\RimWorld by Ludeon Studios\DefDump\defs\ThingDef.json")
OUTDIR = os.path.join(_REPO_ROOT, "src", "Jawa", "Jawa_Armoury", "Patches")

# Mods whose weapons sit on our ladder. Additive by design: dropping a mod name
# in here is the whole cost of covering it, because everything downstream keys
# off the projectile's own damage type rather than the mod it came from.
SW_MODS = ("Star Wars KotOR Weapons and Armor", "Outer Rim - Core",
           "Outer Rim - Droid Depot", "[JDS] StarWars - Armory",
           "Star Wars : The Force - Lightsaber",
           "[AB] Xenotype: Yautja",
           # Emplacements. Fixed guns are their own tier: heavier than anything
           # a person carries, an order below ship-scale.
           "Giant imperial turret", "Rah's Vanilla Turrets Expansion",
           "Wall Mounted Turrets Version 2",
           "Vanilla Furniture Expanded - Security")
VERB_MARKERS = ("ion", "stun", "emp", "sonic", "disrupt", "electr", "shock",
                "extinguish", "smoke", "gas", "tear", "foam", "net", "web")
BANDS = {"blaster": (24, 34), "blaster_heavy": (52, 72), "slugthrower": (18, 36),
         "turbolaser": (800, 2000), "lightsaber": (80, 120), "vibro": (35, 52),
         # Yautja blades: an apex hunter's kit should beat a club decisively and
         # still lose to a vibro-blade, which is purpose-built to shear armour.
         "alienblade": (30, 45),
         # Emplacements. A basic wall turret hits like a heavy blaster; the
         # giant imperial gun hits like nothing a person can carry. Still an
         # order of magnitude below the ship-scale rung (L9), which is the
         # separation that keeps "turbolaser" meaning something.
         "emplacement": (40, 200)}


def dn_mod_is_yautja(w):
    return w["mod"] == "[AB] Xenotype: Yautja"

# ---------------------------------------------------------------- declarers
# Resolved BEFORE the live collect, not after. The anchor a value is mapped from
# has to be checked against what we ourselves write, and that check needs the
# xpath -- which needs the declarer. Doing this later is how the generator ended
# up able to read its own output as input.
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


def xpath_of(defname, node, leaf):
    owner, attr, _ = declarer_of(defname, node)
    if owner is None:
        return None
    sel = ('[defName="%s"]' % owner) if attr == "defName" else ('[@Name="%s"]' % owner)
    return "/Defs/ThingDef%s/%s" % (sel, leaf)


# ------------------------------------------------------------- provenance
# The live dump is post-patch, so once our mods are in the load list it contains
# OUR values. This generator maps old -> new, so reading its own output back as
# "old" makes it revert its own work: lightsabers went 28 -> 99 on the first run
# and would have gone 99 -> (clamped) -> 34 on the second. See
# src/RimMandrake/Utils/patch_provenance.py for the full account.
DUMP_STATUS = guard(os.path.dirname(os.path.dirname(DUMP)), "gen_armoury_patch")
OURS = OurWrites()
LEDGER_REC = Recorder()
anchor_src = collections.Counter()
tainted_skipped = []


def tool_anchors(defname, live_tools):
    """Anchors for a weapon's whole tool list, decided together.

    Per-tool is not good enough. When another mod injects a local <tools> block
    the declarer's ledger entry is for a DIFFERENT tool list that merely shares
    some labels -- so looking up "hilt" against the base returned the base's 12
    where the injected block actually ships 10. The live label list versus the
    declarer's is the only honest way to tell which tools we are looking at, and
    that is a property of the list, not of any one entry.
    """
    owner, attr, decl = declarer_of(defname, "tools")
    if decl is None or decl.find("tools") is None:
        anchor_src["no-declarer"] += len(live_tools)
        return live_tools
    decl_labels = [li.findtext("label") for li in list(decl.find("tools"))]
    if [l for l, _ in live_tools] == decl_labels:
        sel = ('[defName="%s"]' % owner) if attr == "defName" \
            else ('[@Name="%s"]' % owner)
    else:
        sel = '[defName="%s"]' % defname     # injected; the base is unreachable
    out = []
    for lab, pw in live_tools:
        xp = '/Defs/ThingDef%s/tools/li[label="%s"]/power' % (sel, lab)
        val, src = OURS.baseline(xp, pw)
        anchor_src[src] += 1
        if src == "live":
            LEDGER_REC.record(xp, pw)
        elif src == "unknown":
            tainted_skipped.append(defname)
            continue
        out.append((lab, val))
    return out


def anchor(defname, node, leaf, live_value):
    """The value to map FROM. Never one of our own writes.

    Live is right everywhere we do not patch. Where we do, the ledger holds the
    value the mod author actually shipped, recorded the first time we touched it
    -- so a re-run reproduces the first run instead of ratcheting.
    """
    xp = xpath_of(defname, node, leaf)
    if xp is None:
        anchor_src["no-declarer"] += 1
        return live_value
    val, src = OURS.baseline(xp, live_value)
    anchor_src[src] += 1
    if src == "live":
        LEDGER_REC.record(xp, live_value)   # pristine today; recorded for tomorrow
    elif src == "unknown":
        tainted_skipped.append(defname)
        return None
    return val


# ---------------------------------------------------------------- collect
projectiles, weapons = {}, []
for d in iter_live_defs(DUMP):
    f = d.get("fields") or {}
    pr = f.get("projectile")
    if isinstance(pr, dict) and isinstance(pr.get("damageAmountBase"), (int, float)):
        dmg = anchor(d.get("defName"), "projectile",
                     "projectile/damageAmountBase", pr["damageAmountBase"])
        if dmg is not None:
            projectiles[d.get("defName")] = {"mod": d.get("modName") or "",
                                             "dmg": dmg,
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
        raw_tools = [(t.get("label"), t["power"]) for t in (f.get("tools") or [])
                     if isinstance(t, dict)
                     and isinstance(t.get("power"), (int, float))]
        if raw_tools:
            w["tools"] = tool_anchors(w["defName"], raw_tools)
        weapons.append(w)

all_users = collections.defaultdict(list)
for w in weapons:
    if w["proj"]:
        all_users[w["proj"]].append(w)

TURRET_MODS = ("Giant imperial turret", "Rah's Vanilla Turrets Expansion",
               "Wall Mounted Turrets Version 2",
               "Vanilla Furniture Expanded - Security")


def is_turret(w):
    return w["mod"] in TURRET_MODS or "turret" in (w["defName"] or "").lower()


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

    # Emplacement rung, but ONLY if every weapon firing this projectile is a
    # turret. 11 turret projectiles are shared with hand weapons -- Bullet_Shotgun
    # serves VFES_Gun_ShotgunTurret AND Gun_PumpShotgun -- so promoting them
    # would silently buff the personal gun too. Third time this project has met
    # the shared-projectile trap; exclusivity is now checked, not assumed.
    everyone = all_users.get(pname) or []
    if everyone and all(is_turret(u) for u in everyone):
        if p["dmg"] > 0 and not any(k in b for k in ("grenade", "missile", "rocket",
                                                     "bomb", "charge", "shell",
                                                     "mortar", "artillery")):
            return "emplacement"
        return None
    if users and all(is_verb((u["defName"] + " " + u["label"]).lower()) for u in users):
        return None
    if any(s in b for s in ("grenade", "missile", "rocket", "bomb", "charge")):
        return None
    if p["dmg"] <= 0:
        return None
    if "turbolaser" in b:
        return "turbolaser"
    # Yautja plasma is Heat-category energy, exactly like a blaster bolt; their
    # spearguns, discs and shuriken are Sharp-category kinetics, exactly like a
    # slugthrower. Classify by what the damage type IS, not by whose mod it is.
    if "abplasma" in b:
        return "blaster_heavy" if any(k in b for k in ("cannon", "caster")) else "blaster"
    if any(k in b for k in ("abrangedstab", "abrangedcut", "abimpaling")):
        return "slugthrower"
    if any(s in b for s in ("slug", "cycler", "shatter", "massdriver", "bowcaster")):
        return "slugthrower"
    if any(s in b for s in ("heavy", "cannon", "repeater")):
        return "blaster_heavy"
    if any(s in b for s in ("blaster", "bolt", "laser", "energy", "plasma")):
        return "blaster"
    return None


# The INPUT range each rung is assumed to occupy in the unmodified game. These
# are constants on purpose -- see spread() for why that matters.
SOURCE_RANGE = {
    "blaster": (8, 36), "blaster_heavy": (9, 80), "slugthrower": (10, 28),
    "turbolaser": (40, 80), "lightsaber": (24, 34), "vibro": (16, 50),
    "alienblade": (20, 28),
    "emplacement": (12, 110),
}


def spread(items, band, source=None):
    """
    Map each old value onto the target band by a FIXED function of the value.

    NOT by rank. Rank-based spreading was the original implementation and it is
    not idempotent under roster change: it sorts the current members and lays
    them across the band, so adding one new blaster shifts the assigned damage
    of every existing blaster. Install a weapon mod, re-run, and the whole
    armoury churns -- values move for defs nobody touched, and the diff against
    the previous patch is unreadable.

    With a fixed source->target mapping, a given input always produces the same
    output no matter what else is installed. New defs slot in; existing defs
    hold still. That is the property that makes this safe to re-run every time
    the mod list changes, which is the normal case, not the exception.

    Values outside the assumed source range are clamped rather than
    extrapolated, so one wild outlier from a new mod cannot drag a rung.
    """
    lo, hi = band
    slo, shi = source if source else (min(v for _, v in items),
                                      max(v for _, v in items))
    out = {}
    for k, old in items:
        if shi > slo:
            frac = (float(old) - slo) / (shi - slo)
        else:
            frac = 0.5
        frac = max(0.0, min(1.0, frac))          # clamp, never extrapolate
        out[k] = (old, int(round(lo + (hi - lo) * frac)))
    return out


groups = collections.defaultdict(list)
for pname, users in sw_proj.items():
    r = classify(pname, projectiles[pname], users)
    if r:
        groups[r].append((pname, projectiles[pname]["dmg"]))
proj_changes = {}
for r, items in groups.items():
    proj_changes.update(spread(items, BANDS[r], SOURCE_RANGE.get(r)))

melee_groups = collections.defaultdict(list)
for w in sw_weapons:
    if w["ranged"] or not w["tools"]:
        continue
    b = (w["defName"] + " " + w["label"]).lower()
    if is_verb(b):
        continue
    r = ("lightsaber" if ("saber" in b or "foil" in b)
         else "vibro" if ("vibro" in b or "vibra" in b)
         else "alienblade" if dn_mod_is_yautja(w) else None)
    if r:
        melee_groups[r].append((w["defName"], max(p for _, p in w["tools"])))
tool_changes = {}
for r, items in melee_groups.items():
    tool_changes.update(spread(items, BANDS[r], SOURCE_RANGE.get(r)))

for r in sorted(groups):
    print("  %-14s %3d projectiles -> %s" % (r, len(groups[r]), BANDS[r]))
for r in sorted(melee_groups):
    print("  %-14s %3d weapons     -> %s" % (r, len(melee_groups[r]), BANDS[r]))

NL = "\n"
HDR = ('<?xml version="1.0" encoding="utf-8"?>' + NL +
       '<!-- %s' + NL +
       '     GENERATED by src/Jawa/Jawa_Armoury/Source/gen_armoury_patch.py.' + NL +
       '     Do not hand-edit; re-run the generator.' + NL +
       '     Rationale: design/Jawa/worldbuilding/setting_physics.md + balance_paradigm.md -->' + NL +
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
seen_decl, mel_missing, injected = set(), [], []
for dn, (old, new) in sorted(tool_changes.items()):
    owner, attr, rec = declarer_of(dn, "tools")
    if owner is None:
        mel_missing.append(dn)
        continue
    # WHERE to aim. A declarer serves every child only where the children really
    # inherit. KotOR Weapons injects <tools Inherit="False"> onto 8 of the 15
    # lightsabers, which discards the base's tools outright -- so a patch on the
    # base applies cleanly, logs nothing, and is thrown away. Compare the live
    # tool labels against the ones the declarer wrote: if they differ, someone
    # injected a local block and only the concrete defName is reachable.
    decl_pairs = [(li.findtext("label"), li.findtext("power"))
                  for li in list(rec.find("tools"))]
    live_pairs = [(l, str(p)) for l, p in wmap[dn]["tools"]]
    if [l for l, _ in live_pairs] == [l for l, _ in decl_pairs]:
        if owner in seen_decl:
            continue                  # one declarer serves every child
        seen_decl.add(owner)
        pairs = decl_pairs
    else:
        owner, attr, pairs = dn, "defName", live_pairs
        injected.append(dn)
    sel = '[defName="%s"]' % owner if attr == "defName" else '[@Name="%s"]' % owner
    factor = (new / float(old)) if old else 1.0
    ops = []
    for lab, pw in pairs:
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

print("anchors: %s" % dict(anchor_src))
if tainted_skipped:
    print("  ! %d anchors were OUR OWN values with no recorded original;"
          % len(tainted_skipped))
    print("  ! those defs were SKIPPED rather than re-mapped from our output.")
    print("  ! run: python src/RimMandrake/Utils/patch_provenance.py --bootstrap")
    print("  !", sorted(set(tainted_skipped))[:8])
LEDGER_REC.save("gen_armoury_patch, dump %s" % (DUMP_STATUS.captured or "?"))
