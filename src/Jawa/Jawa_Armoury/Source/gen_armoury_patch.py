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

⛔ SUPERSEDED 2026-08-29 for canon-roster turrets: the three fixed-gun tiers
below lost ownership of every projectile fired by a turret on canon.yml
turrets.official_roster — gen_turret_doctrine.py writes those under the
(squares)^2 doctrine, and its output file sorts after this one so its writes
win. On this generator's NEXT regen, exclude those projectiles from the
emplacement/artillery/turbolaser rungs entirely.

THREE FIXED-GUN TIERS, owner ruled 2026-08-14:
  emplacement         40-200   a defence turret hits like a heavy blaster
  artillery          250-600   a siege gun is heavier, and still not ship-scale
  turbolaser        800-2000   unchanged; the separation above is what keeps
                               "turbolaser" meaning anything

  ⚠️ The artillery rung is a NARROW carve-out from L13 and must not widen. It
  catches only projectiles fired EXCLUSIVELY by turrets -- a gun bolted to a
  power grid is not scarce the way a satchel charge in a pawn's pack is. Every
  hand-carried explosive is still untouched.

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
# Walk UP until the repo root announces itself, rather than counting "..".
# 🔴 Counting broke twice: the drive move made it look fragile, and the
# 2026-08-13 restructure changed this file's depth so the five ".." landed one
# directory ABOVE the repo. `from def_diff import ...` then raised
# ModuleNotFoundError, both generators died, and refresh.py --patches still
# exited 0 — a failure that regenerated nothing while reporting success.
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


_REPO_ROOT = _find_repo_root(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(_REPO_ROOT, "src", "RimMandrake", "Utils"))
from def_diff import iter_live_defs
from def_inventory import build as build_offline, D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA
from patch_provenance import guard, OurWrites, Recorder

# Resolved per-platform, never a bare C:\ literal. A hardcoded Windows path
# here made this generator die under WSL python3 with a FileNotFoundError
# naming ThingDef.json - which reads as "take a fresh dump", when the dump
# was present and only the interpreter was wrong. refresh.py carries the
# same lesson in its own header; game_paths.LOCALLOW is the shared fix.
import game_paths as _GP
DUMP = os.path.join(_GP.DEF_DUMP, "defs", "ThingDef.json")
OUTDIR = os.path.join(_REPO_ROOT, "src", "Jawa", "Jawa_Armoury", "Patches")

# Mods whose HAND weapons sit on our ladder. Additive by design: dropping a mod
# name in here is the whole cost of covering it.
#
# 🔴 EMPLACEMENTS ARE NO LONGER LISTED HERE, and that is the fix rather than an
# omission. Four turret mods used to be in this tuple purely to get their turrets
# into the candidate pool — but this tuple also drags in every NON-turret weapon
# those mods ship, which was never the intent (Vanilla Furniture Expanded -
# Security is a furniture mod that happens to include turrets). Turrets now
# reach the pool through TURRET_GUNS, read from <building><turretGunDef> in the
# defs themselves, so they need no mod name here at all.
#
# ⚠️ One of the four never worked anyway: "Giant imperial turret" matches NONE of
# the 266 modNames in the live dump. It was inert in both tuples — a curated list
# that fails silently and looks maintained. Deleted rather than corrected,
# because nothing now needs it.
SW_MODS = ("Star Wars KotOR Weapons and Armor", "Outer Rim - Core",
           "Outer Rim - Droid Depot", "[JDS] StarWars - Armory",
           "Star Wars : The Force - Lightsaber",
           "[AB] Xenotype: Yautja")
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
         "emplacement": (40, 200),
         # 🔴 ARTILLERY — a THIRD fixed-gun tier, owner ruled 2026-08-14.
         # Defence turret 40-200, siege gun 250-600, turbolaser 800-2000. The
         # gravship's main gun has to read as heavier than a wall turret without
         # becoming ship-scale, and one emplacement rung could not say both.
         #
         # ⚠️ THIS BENDS SETTING LAW 13, DELIBERATELY AND NARROWLY, AND THAT MUST
         # NOT BE QUIETLY WIDENED. L13 says explosives are UNCHANGED because
         # blast has no hard counter and is balanced by scarcity alone. Most
         # artillery is explosive, so an artillery rung necessarily touches
         # blast damage.
         #
         # The reconciliation, and the reason the classifier checks turret
         # exclusivity FIRST: scarcity is what balances a blast weapon, and a
         # thing bolted to the ground on a power grid is not scarce the way a
         # satchel charge in a pawn's inventory is. So this rung catches ONLY
         # projectiles fired exclusively by turrets. Every hand-carried grenade,
         # rocket, mortar shell and charge still returns None and is never
         # touched. If a future edit lets a shared projectile onto this rung it
         # will buff the personal weapon too, which is the exact shared-
         # projectile trap this file has already met three times.
         "artillery": (250, 600)}

# What separates a siege gun from a defence turret: it detonates. Measured on the
# live set -- ordinary turret bullets carry radius 0, while the smallest real
# blast projectile in the load is around 1.0 cells. 1.5 keeps incidental splash
# out of the rung without needing a name list.
ARTILLERY_MIN_RADIUS = 1.5
# And it must hit like a siege piece, not merely splash. Set at the emplacement
# band's own ceiling: below 200 a fixed gun is a defence turret by our own
# definition, so it belongs on 40-200 and not on a rung that starts at 250.
ARTILLERY_MIN_DAMAGE = 100


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
# Projectiles left alone because their damage is a sentinel, not a number.
# Reported at the end rather than dropped silently: a rung that quietly declines
# to tune things is how the emplacement list stayed wrong for weeks.
sentinel_skipped = []


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
# Every gun def named by some building's <turretGunDef>. This is what makes a
# weapon an emplacement, and it is read from the defs rather than from a list of
# mod names -- see TURRET_GUNS below for why that had to change.
turret_guns = set()
for d in iter_live_defs(DUMP):
    f = d.get("fields") or {}
    bld = f.get("building")
    if isinstance(bld, dict) and isinstance(bld.get("turretGunDef"), str):
        turret_guns.add(bld["turretGunDef"])
    pr = f.get("projectile")
    if isinstance(pr, dict) and isinstance(pr.get("damageAmountBase"), (int, float)):
        dmg = anchor(d.get("defName"), "projectile",
                     "projectile/damageAmountBase", pr["damageAmountBase"])
        if dmg is not None:
            projectiles[d.get("defName")] = {"mod": d.get("modName") or "",
                                             "dmg": dmg,
                                             "type": pr.get("damageDef") or "",
                                             # 🔴 The DISCRIMINATOR for the artillery
                                             # rung. Judged by what the projectile
                                             # IS, never by what it is called --
                                             # see classify().
                                             "radius": pr.get("explosionRadius") or 0.0}
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

# 🔴 THIS USED TO BE A LIST OF FOUR MOD NAMES, AND IT WAS NEVER A SURVEY OF
# EMPLACEMENTS. Measured 2026-08-13 against the live dump (census_turrets.py):
# the load carries 142 turret buildings across 25 mods, and the list named 3 of
# them — plus "Giant imperial turret", which matches NONE of the 266 modNames in
# the dump and was therefore inert. A curated list of mod names is the same trap
# as a loadAfter naming a packageId that does not exist: it fails silently and
# looks maintained.
#
# So turret-ness now comes from the defs. A building declares its gun in
# <building><turretGunDef>, so the set of gun defNames those point at IS the set
# of emplacement weapons, exactly and without curation. A new turret mod is
# covered the moment it is in the load, with no edit here at all.
#
# ⚠️ The defName fallback stays, and it is doing real work: some emplacement
# guns are reached through a mod's own C# or through a vehicle turret def rather
# than through building/turretGunDef, so the join alone under-selects.
# ⚠️ It also OVER-selects on its own — 530 defs match "turret" by name while only
# 142 are real turret buildings — but that only matters for things that are not
# weapons, and this predicate is asked exclusively about weapons.
def is_turret(w):
    return w["defName"] in TURRET_GUNS or "turret" in (w["defName"] or "").lower()


# A projectile at this value or above is not a damage number, it is a sentinel
# meaning "this always kills" — Wall Mounted Turrets, Core, [HMC]Wall Furniture
# and Alpha Animals all ship 9999. OWNER RULED 2026-08-13: leave every 9999
# untouched, do not investigate. They stay off the ladder exactly as ion, stun
# and explosives do, and for the same reason — the mechanic IS the weapon.
# 🔴 Do not lower this threshold to catch "big" numbers. GravTech's Singularity
# Cannon is a genuine 1000 and Outer Rim tops out at a genuine 2000; both are
# meant to be on the rung.
SENTINEL_DAMAGE = 9999


TURRET_GUNS = turret_guns

sw_weapons = [w for w in weapons if w["mod"] in SW_MODS]
sw_proj = collections.defaultdict(list)
for w in sw_weapons:
    if w["proj"] in projectiles:
        sw_proj[w["proj"]].append(w)

# 🔴 THE POOL IS TWO POOLS, and it used to be one. Everything downstream only
# ever saw projectiles fired by a weapon from SW_MODS, so a turret from any
# other mod could not reach classify() no matter what is_turret() said. That is
# why 22 of the 25 turret-shipping mods were untuned: not a misclassification,
# they were never candidates.
#
# OWNER RULED 2026-08-13: put all 25 on the rung. So emplacements are gathered
# by what they ARE, independently of whose mod they came from — which is the
# same principle the Yautja rows already follow ("classify by what the damage
# type IS, not by whose mod it is").
turret_proj = collections.defaultdict(list)
for w in weapons:
    if w["proj"] in projectiles and is_turret(w):
        turret_proj[w["proj"]].append(w)

candidate_proj = collections.defaultdict(list)
for src in (sw_proj, turret_proj):
    for pname, users in src.items():
        for u in users:
            if u not in candidate_proj[pname]:
                candidate_proj[pname].append(u)

print("SW weapons %d | SW projectiles %d" % (len(sw_weapons), len(sw_proj)))
print("turret guns %d | turret projectiles %d | candidate projectiles %d"
      % (len(TURRET_GUNS), len(turret_proj), len(candidate_proj)))


def is_verb(b):
    return any(v in b for v in VERB_MARKERS)


def classify(pname, p, users):
    b = (pname + " " + p["type"]).lower()
    if is_verb(b):
        return None

    # Sentinel damage is a mechanic, not a number. Owner ruled: untouched.
    # Checked BEFORE the emplacement branch on purpose — every 9999 in the load
    # today belongs to a turret, so putting this test lower would let the rung
    # swallow all of them.
    if isinstance(p["dmg"], (int, float)) and p["dmg"] >= SENTINEL_DAMAGE:
        sentinel_skipped.append((pname, p["dmg"]))
        return None

    # Emplacement rung, but ONLY if every weapon firing this projectile is a
    # turret. 11 turret projectiles are shared with hand weapons -- Bullet_Shotgun
    # serves VFES_Gun_ShotgunTurret AND Gun_PumpShotgun -- so promoting them
    # would silently buff the personal gun too. Third time this project has met
    # the shared-projectile trap; exclusivity is now checked, not assumed.
    # 🔴 THE TURBOLASER TEST MUST COME BEFORE THE TURRET BRANCH. It did not, and
    # the turret branch swallowed it: OuterRim_Proj_HeavyTurbolaser went
    # 2000 -> 600 (artillery) and OuterRim_Proj_Turbolaser 2000 -> 200
    # (emplacement). Capital weapons are MOUNTED -- being turret-exclusive is
    # what a turbolaser IS, so testing exclusivity first can only ever demote it.
    # The ship-scale rung is defined by the weapon, not by its mounting.
    if "turbolaser" in b:
        return "turbolaser"

    everyone = all_users.get(pname) or []
    if everyone and all(is_turret(u) for u in everyone):
        if p["dmg"] <= 0:
            return None
        # 🔴 ARTILLERY IS JUDGED BY EXPLOSION RADIUS, NOT BY NAME. The first
        # version matched the same word list used to EXCLUDE explosives, and
        # "charge" is in it -- so every CHARGE weapon (charged energy, not an
        # explosive charge) was classified as artillery: Bullet_ChargeCannon,
        # Bullet_WallChargeTurret, VFES_Bullet_ChargeComplex and a dozen more.
        # A 14-damage wall turret came out at 250 while the Singularity Cannon
        # was NERFED 1000 -> 421. Ordering destroyed, by a substring.
        # A projectile that detonates has a radius; one that does not, does not.
        # ⚠️ A RADIUS ALONE IS NOT A SIEGE GUN. Requiring only a blast put a
        # 20-damage Alpha Animals turret and a 30-damage wall charge onto a rung
        # whose FLOOR is 250 -- a 12x buff, because spread() clamps anything below
        # the source range to the band minimum. A siege piece hits hard AND
        # detonates; a small turret that happens to splash is an emplacement.
        if (p.get("radius", 0) >= ARTILLERY_MIN_RADIUS
                and p["dmg"] >= ARTILLERY_MIN_DAMAGE):
            return "artillery"
        return "emplacement"
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
    # Measured off the live dump, not chosen: turret-exclusive blast projectiles
    # in this load run from Outer Rim's 2000 down to the small siege pieces, and
    # GravTech's Singularity Cannon sits at 1000. Clamped rather than
    # extrapolated by spread(), so a wilder mod cannot drag the rung.
    "artillery": (100, 2000),
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
for pname, users in candidate_proj.items():
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

if sentinel_skipped:
    print("  sentinel damage left untouched (owner ruled): %d projectile(s)"
          % len(sentinel_skipped))
    for pname, dmg in sorted(set(sentinel_skipped)):
        print("      %-40s %s" % (pname, dmg))

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
