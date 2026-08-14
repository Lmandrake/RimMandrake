"""Generate the armour retune: categories, ratings, penetration, and leather.

Derived from design/Jawa/worldbuilding/setting_physics.md. Runs entirely OFFLINE against
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
import json
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
from def_inventory import build, D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA
from def_diff import iter_live_defs
from refresh import D_DUMP
from patch_provenance import guard

OUTDIR = os.path.join(ROOT, "src", "Jawa", "Jawa_Armoury", "Patches")
ANIMALS = os.path.join(ROOT, "observed", "2026-08-13",
                       "inventory", "animals.csv")
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
# Not a ladder: suits that are good at different things. Powered armour is not
# "best", it is SPECIALISED, and a blaster ruins it.


class Cap(float):
    """A tier value that may only LOWER a stat, never raise it.

    A flat triple is the right shape for "this suit IS 1.40 sharp" and the
    wrong shape for a family that already ships 17 hand-authored identities.
    The warcaskets need a CEILING, not a value: drop the six sets sitting at
    the engine's MaxArmorRating without touching the plain Warcasket at 1.06.
    And for blunt they need nothing at all -- our 1.60 powered ceiling is ABOVE
    every warcasket blunt value in the load (max 1.50), so "applying" it would
    BUFF all 51 pieces. A tier could not say that before; it can now.

    A tier value is therefore one of:
        1.40        set flat            (every pre-existing tier; unchanged)
        Cap(1.40)   set only if higher  (a ceiling)
        None        leave this stat entirely alone
    """
    __slots__ = ()


ARMOUR_TIERS = [
    # Warcaskets go FIRST, and in their own tier. Both parts are load-bearing:
    #
    #  * They must not fall through into `powered`. Six of the 51 pieces are
    #    named ..._Marine or ..._Cataphract, so a warcasket tier placed AFTER
    #    powered would catch 45 pieces and hand those six a flat 1.60 blunt --
    #    a BUFF of up to +0.95 on suits this tier exists to bring DOWN.
    #  * `warcasket` used to be the first keyword of the powered tier and had
    #    never once matched, because these defs are VFEPirates.WarcasketDef and
    #    the loop below only walked ThingDef. See the of_type note at part 2.
    #
    # Measured 2026-08-12 over all 51 concrete pieces (VFE Pirates 2723801948 +
    # WarCasket Expanded 3535194807), read from source XML because nothing in
    # the load patches warcasket ArmorRating -- Farhan's Warcasket Tweaks
    # (3533261706) touches only Insulation_*, VacuumResistance and
    # equippedStatOffsets, so source values ARE live values:
    #     Sharp 1.02 .. 2.00   18 pieces sit AT 2.00 = engine MaxArmorRating,
    #                          i.e. immune to any zero-AP sharp weapon
    #     Blunt 0.55 .. 1.50   all of it already under our 1.60 -> leave alone
    #     Heat  0.64 .. 1.80   21 pieces above 0.90, several at/over beskar's
    #                          1.20 while wearing sealed plate on a desert world
    ("warcasket", ("warcasket",), (Cap(1.40), None, Cap(0.90))),
    ("powered", ("cataphract", "marine", "powerarmor", "power armor",
                 "exosuit", "forsaken"), (1.40, 1.60, 0.35)),
    ("beskar",  ("mando", "beskar", "malgus"),                 (1.00, 0.90, 1.20)),
    ("cortosis", ("cortosis",),                                (0.20, 0.15, 2.00)),
]

# Already retuned by hand, with its own dated rationale and a different number,
# in src/Jawa/Jawa_Armoury/Patches/Warcasket_HazardRetune.xml (Heat 2.00
# -> 1.30 plus the Insulation_Heat 333 undo). Emitting a Heat op here too would
# put two operations from the SAME mod on one node, and which one wins would be
# a filename-ordering accident. Their Sharp is 1.20 -- already under the cap --
# and blunt is untouched, so skipping them outright loses nothing.
HAND_TUNED = ("VFEP_Warcasket_Hazard", "VFEP_WarcasketHelmet_Hazard",
              "VFEP_WarcasketShoulders_Hazard")

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


def fnum(x, d=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


# VFEPirates.WarcasketDef must be named explicitly. `types` filters on the XML
# ELEMENT NAME, which in RimWorld is the def's C# class -- and WarcasketDef
# SUBCLASSES ThingDef, so asking for "ThingDef" does not bring its subclasses
# along. Adding a type here is safe for everything else: it only widens
# ds.records / by_type / defs, and by_name (the inheritance index) is built over
# every node regardless of this filter.
ds = build(D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA,
           types=("ThingDef", "DamageDef", "VFEPirates.WarcasketDef"))


def declarer(defname, node, defType="ThingDef"):
    """Patches hit raw XML before inheritance; aim at whoever DECLARES node."""
    rec = ds.get(defType, defname)
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


# --- live tool truth ------------------------------------------------------
# Resolving inheritance offline is NOT enough for tools. KotOR Weapons injects
#
#     <tools Inherit="False">   (no <armorPenetration> anywhere in it)
#
# onto each concrete lightsaber, via a PatchOperationAdd in
#   .../2938932438/1.6/AdditionalMods/_TheForceLightsabers/Patches/
#   Patch_KotORLightsaberBalancing.xml            (read 2026-08-11)
#
# Inherit="False" discards the abstract base's tool list outright. So a patch
# aimed at Force_LightsaberBase APPLIES CLEANLY, logs nothing, and is then
# thrown away -- the failure mode with no error message. Confirmed live: 8 of
# 15 sabers kept power 26 / AP -1 while the 7 that still inherit went to 99/0.
#
# Only the live dump shows the tools a weapon actually ends up with, so tool
# work is driven from it and degrades to offline-only with a loud warning.
SABER_COMPS = ("CompProperties_LightsaberBlade", "Comp_LightsaberStance",
               "CompProperties_LightsaberStance")


def load_live_tools():
    # This generator is SAFE against reading its own output -- every value it
    # writes is a constant from the block above (LIGHTSABER_AP, VIBRO_AP by
    # mass, SLUG_AP, the armour tiers), never a function of the current value.
    # gen_armoury_patch.py is not, which is why it routes anchors through the
    # ledger. The banner prints either way: the 2026-08-11 near-miss happened
    # because nobody asked what the dump contained, not because anyone decided
    # wrongly.
    guard(D_DUMP, "gen_armour_patch (values are constants; structure only)")
    path = os.path.join(D_DUMP, "defs", "ThingDef.json")
    if not os.path.isfile(path):
        return None
    out = {}
    for d in iter_live_defs(path):
        f = d.get("fields") or {}
        tools = f.get("tools")
        if not tools:
            continue
        comps = json.dumps(f.get("comps") or [])
        out[d.get("defName")] = {
            # armorPenetration is -1 when the field is absent: Verse.Tool
            # defaults it to -1f, and VerbProperties.AdjustedArmorPenetration
            # then DERIVES it as damage * 0.015 -- so an unset AP silently
            # scales with power and quality. Decompiled 2026-08-11.
            "tools": [(t.get("label"), t.get("armorPenetration")) for t in tools],
            # Tools are not proof of a weapon. A rifle carries a "stock" bash
            # tool, and a RACE def carries its natural attacks: ABAlien_Yautja
            # is a Pawn with tools, so a mod-wide rule aimed at "Yautja blades"
            # otherwise re-armed the Yautja's own fists.
            "melee": bool((d.get("is") or {}).get("meleeWeapon")),
            # Structural, not name-based. "claw saber" (a megafauna weapon) and
            # "Echani Foil" (a vibro-sword) both matched the old substring test
            # and had their AP zeroed; neither carries a lightsaber comp. The
            # comp test also finds Force_ImbuedBlade, which has no saber-ish
            # name at all and the substring test missed entirely.
            "saber": any(c in comps for c in SABER_COMPS),
        }
    return out


LIVE = load_live_tools()
if LIVE is None:
    print("  ! no live dump at %s" % D_DUMP)
    print("  ! falling back to offline names; tool AP may miss injected tools")


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


def set_block(fn, mod, comment, parent_xpath, tag, inner):
    """Like set_field, but for a whole child element rather than one value.

    Replace when the block exists, Add when it does not, decided at load. The
    offline check this replaced was wrong for at least one def and produced a
    duplicate sibling node; see the leather section for the full account.
    """
    block = ("            <%s>" % tag) + NL + inner + ("            </%s>" % tag) + NL
    ops[fn][mod or "?"].append(
        "        <!-- %s -->" % comment + NL +
        '        <li Class="PatchOperationConditional">' + NL +
        "          <xpath>%s/%s</xpath>" % (parent_xpath, tag) + NL +
        '          <match Class="PatchOperationReplace">' + NL +
        "            <xpath>%s/%s</xpath>" % (parent_xpath, tag) + NL +
        "            <value>" + NL + block + "            </value>" + NL +
        "          </match>" + NL +
        '          <nomatch Class="PatchOperationAdd">' + NL +
        "            <xpath>%s</xpath>" % parent_xpath + NL +
        "            <value>" + NL + block + "            </value>" + NL +
        "          </nomatch>" + NL +
        "        </li>" + NL)


def set_field(fn, mod, comment, parent_xpath, tag, value):
    """Set a field that may or may not exist in the raw XML.

    Replace fails when the node is absent; Add duplicates it when present. The
    old code chose Replace and skipped anything lacking the node -- which is why
    ALL TWELVE Yautja blades silently received no armorPenetration at all: none
    of them declares one, so every candidate was skipped by the guard.

    Which case applies is not knowable offline, because another mod can inject
    the parent wholesale at patch time. PatchOperationConditional decides at
    load, so it is also idempotent when the generator is re-run against a dump
    that already contains this mod's own output.
    """
    ops[fn][mod or "?"].append(
        "        <!-- %s -->" % comment + NL +
        '        <li Class="PatchOperationConditional">' + NL +
        "          <xpath>%s/%s</xpath>" % (parent_xpath, tag) + NL +
        '          <match Class="PatchOperationReplace">' + NL +
        "            <xpath>%s/%s</xpath>" % (parent_xpath, tag) + NL +
        "            <value><%s>%s</%s></value>" % (tag, value, tag) + NL +
        "          </match>" + NL +
        '          <nomatch Class="PatchOperationAdd">' + NL +
        "            <xpath>%s</xpath>" % parent_xpath + NL +
        "            <value><%s>%s</%s></value>" % (tag, value, tag) + NL +
        "          </nomatch>" + NL +
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

# ThingDef is NOT the only apparel type in this load, and the loop below used
# to assume it was. `ds.of_type` keys on the XML element name, which is the
# def's C# class; all 51 warcasket pieces declare <VFEPirates.WarcasketDef>, a
# SUBCLASS of ThingDef. So of_type("ThingDef") never yielded one, `warcasket`
# -- the FIRST keyword of the powered tier -- matched nothing from the day it
# was written, and there was no error to notice. Found 2026-08-12.
#
# Two things are true at once and neither is a typo:
#   * the xpath root is /Defs/VFEPirates.WarcasketDef   (XML element = C# class)
#   * the live def dump files these under ThingDef.json (runtime type)
# Farhan's 39 ops use exactly this xpath root, which is independent
# confirmation; so does our own Warcasket_HazardRetune.xml.
APPAREL_TYPES = ("ThingDef", "VFEPirates.WarcasketDef")
tier_counts = collections.Counter()
for rec in [r for t in APPAREL_TYPES for r in ds.of_type(t)]:
    el = rec.element
    if el.find("apparel") is None:
        continue
    dn = rec.defName or ""
    if dn in HAND_TUNED:
        continue
    blob = (dn + " " + (el.findtext("label") or "")).lower()
    for tier, keys, vals in ARMOUR_TIERS:
        if not any(k in blob for k in keys):
            continue
        owner, attr, decl = declarer(dn, "statBases", rec.defType)
        if owner is None:
            continue
        for stat, val in zip(STATS, vals):
            if val is None:
                continue          # this tier deliberately leaves the stat alone
            if decl.find("statBases/" + stat) is None:
                continue          # not declared here; a Replace would miss
            note = ""
            if isinstance(val, Cap):
                # A ceiling, not a value. Read the DECLARER's number, since that
                # is the node the Replace will overwrite. Safe to trust offline:
                # nothing in the load patches warcasket ArmorRating.
                cur = fnum(decl.findtext("statBases/" + stat))
                if cur is None or cur <= val + 1e-9:
                    continue      # already at or under the ceiling; emit nothing
                note = " (was %.2f, capped)" % cur
            replace("Armour_Ratings.xml", rec.modName,
                    "%s [%s] %s -> %.2f%s" % (dn, tier, stat, val, note),
                    "/Defs/%s%s/statBases/%s"
                    % (rec.defType, sel(owner, attr), stat),
                    stat, "%.2f" % val)
        tier_counts[tier] += 1
        break

# ========================================================== 3. penetration
saber_done = set()
vibro_n = slug_n = alien_n = 0
skipped_no_live = []
for rec in ds.of_type("ThingDef"):
    el = rec.element
    dn = rec.defName or ""
    b = (dn + " " + (el.findtext("label") or "")).lower()
    live = (LIVE or {}).get(dn)

    # The slugthrower rule keys off the PROJECTILE, so it is independent of all
    # the tool work below and must not sit behind its early-out.
    if any(k in b for k in ("slug", "cycler", "shatter", "massdriver")) \
            and el.find("projectile/armorPenetrationBase") is not None:
        p_owner, p_attr, _ = declarer(dn, "projectile")
        if p_owner is not None:
            replace("Armour_Penetration.xml", rec.modName,
                    "%s slugthrower AP -> %.2f" % (dn, SLUG_AP),
                    "/Defs/ThingDef%s/projectile/armorPenetrationBase"
                    % sel(p_owner, p_attr),
                    "armorPenetrationBase", "%.2f" % SLUG_AP)
            slug_n += 1

    if live is not None and not live["melee"]:
        continue

    if live is not None:
        is_saber = live["saber"]
    else:
        # Offline fallback only. "foil" is deliberately NOT a term: the sole
        # weapon it ever matched was guy762_vsword_echani, the "Echani Foil",
        # which is a VIBRO-sword -- so the one class built to shear armour had
        # its AP zeroed to lightsaber levels while its damage was raised.
        is_saber = "lightsaber" in b and el.find("tools") is not None
    is_vibro = (not is_saber) and el.find("tools") is not None \
        and ("vibro" in b or "vibra" in b or dn.startswith("guy762_v"))
    # Yautja blades are alien-forged: better than steel, but not the
    # purpose-built armour-shear a vibro-blade is.
    is_alien = (rec.modName == "[AB] Xenotype: Yautja"
                and el.find("tools") is not None and not is_saber and not is_vibro)

    if not (is_saber or is_vibro or is_alien):
        continue

    if is_saber:
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

    owner, attr, decl = declarer(dn, "tools")
    if owner is None:
        continue
    decl_labels = [li.findtext("label") for li in list(decl.find("tools"))]

    # WHERE to aim. If the live tool labels match the ones the declarer wrote,
    # the weapon really does inherit and one operation on the declarer serves
    # every child. If they differ, some mod injected a local <tools> block and
    # only the concrete defName is reachable -- aiming at the base is the exact
    # silent no-op that left 8 of 15 sabers untouched.
    if live is None:
        labels = decl_labels
        skipped_no_live.append(dn)
    elif [l for l, _ in live["tools"]] == decl_labels:
        labels = decl_labels
    else:
        owner, attr = dn, "defName"
        labels = [l for l, _ in live["tools"]]

    if is_saber:
        if owner in saber_done:
            continue
        saber_done.add(owner)

    for lab in labels:
        if not lab:
            continue
        # Every tool, including the hilt. The old guard skipped tools with no
        # <armorPenetration>, which left the hilt deriving AP from its own
        # power -- and since this mod raises saber hilts to 42, that residue
        # showed up in-game as a "zero-AP" lightsaber reading 0.14%.
        set_field("Armour_Penetration.xml", rec.modName,
                  "%s / %s AP -> %.2f" % (owner, lab, ap),
                  '/Defs/ThingDef%s/tools/li[label="%s"]'
                  % (sel(owner, attr), lab),
                  "armorPenetration", "%.2f" % ap)

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
    # Whether a <statFactors> node already exists is NOT knowable offline, and
    # guessing it wrong is not harmless. Leather_Megasquid read as having none,
    # so this emitted a bare Add -- and the def turned out to carry one anyway,
    # leaving TWO sibling <statFactors> nodes in the raw XML. The runtime
    # resolved to ours, but the info card enumerated both (Sharp 81% AND 130%),
    # and which one wins is then a load-order accident waiting to happen.
    #
    # Same bug class as the Yautja blades, opposite direction: that emitter only
    # ever replaced and skipped anything missing the node, this one only ever
    # added and duplicated anything that had it. The conditional decides at load
    # and is right either way, so the offline guess is removed entirely.
    set_block("Armour_Leather.xml", rec.modName,
              "%s : %s" % (dn, why),
              '/Defs/ThingDef[defName="%s"]/stuffProps' % dn,
              "statFactors",
              "".join("              <%s>%.2f</%s>%s" % (name, prof[i], name, NL)
                      for name, i in FACTORS))

# ========================================================== emit
os.makedirs(OUTDIR, exist_ok=True)
HDR = ('<?xml version="1.0" encoding="utf-8"?>' + NL +
       "<!-- %s" + NL +
       "     GENERATED by src/Jawa/Jawa_Armoury/Source/gen_armour_patch.py" + NL +
       "     Do not hand-edit; re-run the generator." + NL +
       "     Rationale: design/Jawa/worldbuilding/setting_physics.md L3/L7/L8/L11/L14 -->" + NL +
       "<Patch>" + NL)
TITLES = {
    "Armour_DamageCategories.xml": "Point energy damage at Heat and sonic at Blunt (L7)",
    "Armour_Ratings.xml": "Armour identities: warcasket vs powered vs beskar vs cortosis (L7/L8)",
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
