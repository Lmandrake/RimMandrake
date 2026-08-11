"""Generate the armour retune: categories, ratings, penetration, and leather.

Derived from worldbuilding/setting_physics.md. Runs entirely OFFLINE against
def_inventory, so it works while the live dump is disabled.

THE ENGINE, verified by decompiling Verse.ArmorUtility (do not re-derive):

    public const float MaxArmorRating = 2f;
    float eff = Mathf.Max(armorRating - armorPenetration, 0f);
    if (Rand.Value < eff * 0.5f)  damage = 0;              // deflect
    else if (Rand.Value < eff)  { damage /= 2; Sharp->Blunt; }

Three consequences the whole design rests on:
  * 2.0 IS IMMUNITY. RimWorld names the constant. Armour cannot be stretched
    like damage was; the top tier is "immune to ONE category", not a number.
  * AP subtracts from the rating, so HIGH AP DEFEATS IMMUNITY. A lightsaber with
    AP 0.7 would cut cortosis (2.0 -> 1.3 effective, 65% deflect). Hence
    lightsaber AP is ZERO: its 99 damage does the cutting, and the one armour
    meant to stop it still does.
  * Armour applies PER WORN LAYER and each rolls separately, so layers multiply.
    A single advanced layer near 0.8-0.9 meets the ~5-shot contract; 1.2+ would
    overshoot badly once anything is worn under it.

FOUR JOBS
  1. damage categories  - three defs point at the wrong armour stat
  2. armour ratings     - give powered / beskar / cortosis distinct identities
  3. armour penetration - the lever that was doing nothing
  4. leather            - 165 defs, all flat at 1.00, each able to carry the
                          character of the creature it came from
"""
import collections
import csv
import io
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "Utils"))
from def_inventory import build, D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA

OUTDIR = os.path.join(ROOT, "custom_patches", "Jawa_Armoury", "Patches")
ANIMALS = os.path.join(ROOT, "mods", "inventory", "animals.csv")
NL = "\n"

# --- 1. damage types aimed at the wrong armour stat -----------------------
# Blaster_Damage checking BLUNT means every JDS blaster is stopped by the wrong
# armour. Energy must be Heat (that is what makes ablative armour the answer);
# a sonic pressure wave is Blunt, not Sharp.
CATEGORY_FIX = {
    "Blaster_Damage": "Heat",
    "guy762_RangedDamage_sonic": "Blunt",
    "guy762_MeleeDamage_sonic": "Blunt",
    "guy762_GrenadeDamage_sonic": "Blunt",
    "OuterRim_Ion": "Heat",
}

# --- 2. armour identities -------------------------------------------------
# Not a ladder: three suits that are good at different things. Powered armour
# is not "best", it is SPECIALISED, and a blaster ruins it.
ARMOUR_TIERS = [
    ("powered", ("warcasket", "cataphract", "marine", "powerarmor", "power armor",
                 "exosuit", "forsaken"), (1.40, 1.60, 0.35)),
    ("beskar",  ("mando", "beskar", "malgus"),                 (1.00, 0.90, 1.20)),
    ("cortosis", ("cortosis",),                                (0.20, 0.15, 2.00)),
]

# --- 3. armour penetration ------------------------------------------------
LIGHTSABER_AP = 0.0     # see the header: any higher and cortosis stops working
VIBRO_AP = (0.90, 1.60)  # scaled by weapon mass; an axe opens a warcasket
SLUG_AP = 0.85
ALIEN_BLADE_AP = 0.60      # Yautja blades; see the penetration block

# Comfy-max above which a hide counts as genuinely ABLATIVE (L11).
#
# NOT the animal inventory's HEAT_HARDY flag, which triggers at 50C. That was
# set as a loose "desert-world candidate" screen, and 50C is simply ordinary --
# at that cutoff 61 of 152 hides qualified, including CHINCHILLA, GUINEA PIG and
# THRUMBO, none of which are heat-adapted by any reading.
#
# The data has a cliff: >=60 gives 51 hides, >=70 gives 19, >=75 gives 14. And
# the 14 are exactly right -- Bantha, Ronto, Rycrit, Wraid, Krayt Dragon (i.e.
# Tatooine's bestiary), plus sand lion, behemoth, the 145C geyser fauna and the
# insectoid chitins. When a threshold sweep produces a cliff AND the survivors
# are thematically coherent, that is the real boundary rather than a chosen one.
HEAT_ADAPTED_C = 75.0


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


ds = build(D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA, types=("ThingDef", "DamageDef"))


def declarer(defname, node):
    """Patches hit raw XML before inheritance; aim at whoever DECLARES node."""
    rec = ds.get("ThingDef", defname)
    if rec is None:
        return None, None, None
    if rec.own.find(node) is not None:
        return defname, "defName", rec.own
    seen, pn = set(), rec.parentName
    while pn and pn not in seen:
        seen.add(pn)
        pel = ds.by_name.get(pn)
        pel = getattr(pel, "own", pel)
        if pel is None:
            return None, None, None
        if pel.find(node) is not None:
            return pn, "Name", pel
        pn = pel.get("ParentName")
    return None, None, None


def sel(owner, attr):
    return ('[defName="%s"]' % owner) if attr == "defName" else ('[@Name="%s"]' % owner)


# filename -> source mod -> [op strings]. Grouping by mod is not cosmetic:
# every operation ends up inside a PatchOperationFindMod, because an unguarded
# Replace whose target mod is absent logs a red error on every launch, and this
# mod has to stay droppable.
ops = collections.defaultdict(lambda: collections.defaultdict(list))


def replace(fn, mod, comment, xpath, tag, value):
    ops[fn][mod or "?"].append(
        "        <!-- %s -->" % comment + NL +
        '        <li Class="PatchOperationReplace">' + NL +
        "          <xpath>" + xpath + "</xpath>" + NL +
        "          <value><%s>%s</%s></value>" % (tag, value, tag) + NL +
        "        </li>" + NL)


# ========================================================== 1. categories
for dn, cat in CATEGORY_FIX.items():
    rec = ds.get("DamageDef", dn)
    if rec is None:
        continue
    cur = rec.element.findtext("armorCategory")
    if cur == cat:
        continue
    if rec.own.find("armorCategory") is None:
        print("  ! %s declares no armorCategory (inherited); skipped" % dn)
        continue
    replace("Armour_DamageCategories.xml", rec.modName,
            "%s: %s -> %s" % (dn, cur, cat),
            '/Defs/DamageDef[defName="%s"]/armorCategory' % dn,
            "armorCategory", cat)

# ========================================================== 2. ratings
STATS = ("ArmorRating_Sharp", "ArmorRating_Blunt", "ArmorRating_Heat")
tier_counts = collections.Counter()
for rec in ds.of_type("ThingDef"):
    el = rec.element
    if el.find("apparel") is None:
        continue
    dn = rec.defName or ""
    blob = (dn + " " + (el.findtext("label") or "")).lower()
    for tier, keys, vals in ARMOUR_TIERS:
        if not any(k in blob for k in keys):
            continue
        owner, attr, decl = declarer(dn, "statBases")
        if owner is None:
            continue
        for stat, val in zip(STATS, vals):
            if decl.find("statBases/" + stat) is None:
                continue          # not declared here; a Replace would miss
            replace("Armour_Ratings.xml", rec.modName,
                    "%s [%s] %s -> %.2f" % (dn, tier, stat, val),
                    "/Defs/ThingDef%s/statBases/%s" % (sel(owner, attr), stat),
                    stat, "%.2f" % val)
        tier_counts[tier] += 1
        break

# ========================================================== 3. penetration
# Lightsabers share one abstract base, so one operation serves all of them.
saber_done = set()
vibro_n = slug_n = alien_n = 0
for rec in ds.of_type("ThingDef"):
    el = rec.element
    dn = rec.defName or ""
    b = (dn + " " + (el.findtext("label") or "")).lower()

    is_saber = ("saber" in b or "foil" in b) and el.find("tools") is not None
    is_vibro = ("vibro" in b or "vibra" in b or dn.startswith("guy762_v")) \
        and el.find("tools") is not None
    # Yautja blades are alien-forged: better than steel, but not the
    # purpose-built armour-shear a vibro-blade is.
    is_alien = (rec.modName == "[AB] Xenotype: Yautja"
                and el.find("tools") is not None and not is_saber and not is_vibro)
    if is_saber or is_vibro or is_alien:
        owner, attr, decl = declarer(dn, "tools")
        if owner is None:
            continue
        if is_saber:
            if owner in saber_done:
                continue
            saber_done.add(owner)
            ap = LIGHTSABER_AP
        elif is_alien:
            ap = ALIEN_BLADE_AP
            alien_n += 1
        else:
            try:
                mass = float(el.findtext("statBases/Mass"))
            except (TypeError, ValueError):
                mass = 3.0
            # Mass is the honest size proxy: 0.35 (dagger) .. 8.0 (vibro-axe).
            frac = clamp((mass - 0.35) / (8.0 - 0.35), 0.0, 1.0)
            ap = VIBRO_AP[0] + (VIBRO_AP[1] - VIBRO_AP[0]) * frac
            vibro_n += 1
        for li in list(decl.find("tools")):
            lab = li.findtext("label")
            if not lab or li.find("armorPenetration") is None:
                continue
            replace("Armour_Penetration.xml", rec.modName,
                    "%s / %s AP %s -> %.2f"
                    % (owner, lab, li.findtext("armorPenetration"), ap),
                    '/Defs/ThingDef%s/tools/li[label="%s"]/armorPenetration'
                    % (sel(owner, attr), lab),
                    "armorPenetration", "%.2f" % ap)

    if any(k in b for k in ("slug", "cycler", "shatter", "massdriver")) \
            and el.find("projectile/armorPenetrationBase") is not None:
        owner, attr, decl = declarer(dn, "projectile")
        if owner is None:
            continue
        replace("Armour_Penetration.xml", rec.modName,
                "%s slugthrower AP -> %.2f" % (dn, SLUG_AP),
                "/Defs/ThingDef%s/projectile/armorPenetrationBase" % sel(owner, attr),
                "armorPenetrationBase", "%.2f" % SLUG_AP)
        slug_n += 1

# ========================================================== 4. leather
# Every leather currently reads S=1.00 B=1.00 H=1.00 -- 165 defs with no
# character at all. Each one is the hide of a specific creature, so let the
# creature decide what its hide is good for.
animals = {}
if os.path.isfile(ANIMALS):
    with io.open(ANIMALS, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            lf = (r.get("leatherDef") or "").strip()
            if lf:
                animals.setdefault(lf, []).append(r)


def fnum(x, d=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def _median(vals, default=0.0):
    v = sorted(x for x in vals if x is not None)
    return v[len(v) // 2] if v else default


def leather_profile(defname):
    """
    (sharp, blunt, heat, beauty, comfort, why) for one hide.

    Uses the MEDIAN of the source animals, never the max. Leathers are SHARED:
    dozens of species drop Leather_Plain, so taking the max let a single
    heat-hardy outlier declare all plain leather ablative — 87 of 163 hides
    (53%) came out "heat-adapted", turning a rare desert exception into the
    default. Same shape as the shared-projectile bug in the weapon generator:
    when many things map to one output, an extreme is the wrong summary.

    Heat adaptation additionally requires a MAJORITY of the source species to
    qualify, and ignores the sentinel temperatures some mods ship (50000C,
    999, Fahrenheit-conversion artefacts), which would otherwise vote yes.
    """
    src = animals.get(defname) or []
    size = _median([fnum(r.get("baseBodySize")) for r in src])
    armoured = _median([fnum(r.get("armorSharp")) for r in src])

    # A sentinel is not evidence of adaptation.
    temps = [t for t in (fnum(r.get("effectiveTempMax")) for r in src)
             if t is not None and t < 200]
    hardy = sum(1 for r in src if (r.get("HEAT_HARDY") or "") == "YES")
    hot = bool(src) and hardy * 2 > len(src) and _median(temps) >= HEAT_ADAPTED_C

    # Baseline (L7/L11): hide is MASS armour. Good against teeth and claws,
    # poor against energy -- leather must not stop a blaster.
    sharp, blunt, heat = 1.20, 1.10, 0.40
    why = "baseline hide"

    if size and size < 0.2:
        # Vermin. A mouse pelt stops nothing; its value is that it is lovely.
        sharp, blunt, heat = 0.10, 0.10, 0.10
        why = "vermin: protects nothing, but fine and beautiful"
        return sharp, blunt, heat, 1.60, 1.35, why

    if hot:
        # THE DESERT EXCEPTION (L11). Heat-adapted hide is naturally ablative,
        # so it is the one leather that resists energy weapons -- which makes
        # hunting the terrifying thing worth doing.
        sharp, blunt, heat = 1.15, 1.05, 1.30
        why = "heat-adapted: ablative hide, resists energy (L11)"
    elif size >= 5.0:
        sharp, blunt, heat = 1.45, 1.40, 0.45
        why = "megafauna: thick mass armour"
    elif size >= 2.0:
        sharp, blunt, heat = 1.30, 1.25, 0.42
        why = "large beast"

    if armoured >= 0.3:
        sharp = min(sharp + 0.20, 1.60)
        why += "; naturally armoured"

    beauty = 1.25 if size >= 5.0 else 1.05
    comfort = 1.15 if size < 1.0 else 1.00
    return sharp, blunt, heat, beauty, comfort, why


FACTORS = (("ArmorRating_Sharp", 0), ("ArmorRating_Blunt", 1),
           ("ArmorRating_Heat", 2), ("Beauty", 3), ("Comfort", 4))
leather_n = collections.Counter()
for rec in ds.of_type("ThingDef"):
    dn = rec.defName or ""
    if not dn:
        continue
    # Category comes from the RESOLVED element (leathers inherit it from a
    # base) while statFactors are declared LOCALLY. Reading both off the same
    # node found 6 of 165 -- the classic inheritance mix-up this project keeps
    # paying for.
    res = rec.element.find("stuffProps")
    if res is None:
        continue
    cats = [c.text for c in res.findall("categories/li") if c.text]
    if not any("Leather" in (c or "") for c in cats):
        continue
    sp = rec.own.find("stuffProps")
    if sp is None:
        continue                      # inherits wholesale; nothing local to patch
    prof = leather_profile(dn)
    why = prof[5]
    leather_n[why.split(":")[0].split(";")[0]] += 1
    sf = sp.find("statFactors")
    body = "".join("      <%s>%.2f</%s>%s" % (name, prof[i], name, NL)
                   for name, i in FACTORS)
    if sf is None:
        # No statFactors node at all: add one rather than replace nothing.
        ops["Armour_Leather.xml"][rec.modName].append(
            "        <!-- %s : %s -->" % (dn, why) + NL +
            '        <li Class="PatchOperationAdd">' + NL +
            '          <xpath>/Defs/ThingDef[defName="%s"]/stuffProps</xpath>' % dn + NL +
            "          <value>" + NL + "            <statFactors>" + NL +
            "".join("              <%s>%.2f</%s>%s" % (name, prof[i], name, NL)
                    for name, i in FACTORS) +
            "            </statFactors>" + NL + "          </value>" + NL +
            "        </li>" + NL)
    else:
        ops["Armour_Leather.xml"][rec.modName].append(
            "        <!-- %s : %s -->" % (dn, why) + NL +
            '        <li Class="PatchOperationReplace">' + NL +
            '          <xpath>/Defs/ThingDef[defName="%s"]/stuffProps/statFactors</xpath>' % dn + NL +
            "          <value>" + NL + "            <statFactors>" + NL +
            "".join("              <%s>%.2f</%s>%s" % (name, prof[i], name, NL)
                    for name, i in FACTORS) +
            "            </statFactors>" + NL + "          </value>" + NL +
            "        </li>" + NL)

# ========================================================== emit
os.makedirs(OUTDIR, exist_ok=True)
HDR = ('<?xml version="1.0" encoding="utf-8"?>' + NL +
       "<!-- %s" + NL +
       "     GENERATED by custom_patches/Jawa_Armoury/Source/gen_armour_patch.py" + NL +
       "     Do not hand-edit; re-run the generator." + NL +
       "     Rationale: worldbuilding/setting_physics.md L3/L7/L8/L11/L14 -->" + NL +
       "<Patch>" + NL)
TITLES = {
    "Armour_DamageCategories.xml": "Point energy damage at Heat and sonic at Blunt (L7)",
    "Armour_Ratings.xml": "Armour identities: powered vs beskar vs cortosis (L7/L8)",
    "Armour_Penetration.xml": "Penetration: vibro shears, the lightsaber does not (L3/L14)",
    "Armour_Leather.xml": "Every hide carries the character of its creature (L7/L11)",
}
for fn, by_mod in sorted(ops.items()):
    n = 0
    with io.open(os.path.join(OUTDIR, fn), "w", encoding="utf-8") as fh:
        fh.write(HDR % TITLES.get(fn, fn))
        for mod, oplist in sorted(by_mod.items()):
            n += len(oplist)
            fh.write(NL + '  <Operation Class="PatchOperationFindMod">' + NL)
            fh.write("    <mods><li>" + mod + "</li></mods>" + NL)
            fh.write('    <match Class="PatchOperationSequence">' + NL)
            fh.write("      <operations>" + NL)
            for o in oplist:
                fh.write(o)
            fh.write("      </operations>" + NL)
            fh.write("    </match>" + NL + "  </Operation>" + NL)
        fh.write(NL + "</Patch>" + NL)
    print("  %-34s %4d operations in %d mod groups" % (fn, n, len(by_mod)))

print("\narmour tiers matched: %s" % dict(tier_counts))
print("vibro %d | alien blades %d | slugthrowers %d | lightsaber bases %d"
      % (vibro_n, alien_n, slug_n, len(saber_done)))
print("leather profiles: %s" % dict(leather_n))
