"""gen_droidworks_modules.py -- DROIDWORKS_MODULE_ABSORB_1 (packet B2).

Absorbs guy762's droid-module apparel -- the "six-slot" scheme
(droid_system_build_spec.md: hardware/software/sensor/gadget/weapon/shield) --
into Droidworks' own RSW_DW_Module_* namespace, so the 22 already-ported KotOR
kinds (RSW_DW_guy762_DroidRace_*, Defs/PawnKinds_KotOR.xml) whose apparelTags
already carry literal tag strings like "KotORDroidUpgrade_combat" or
"SWCPSpecificDroidTech_HK47Sensor" (verified by grepping the already-generated
PawnKinds_KotOR.xml) finally have a real apparel def to match against. Before
this item those tags matched nothing loaded -- a kind's apparelTags is plain
RimWorld tag-matching (0 matches = no gear, not an error), so kinds silently
spawned with an empty accessory slot.

SOURCE (confirmed on disk, not guessed):
  guy762.MM.KotORCore, workshop 3254370945, packageId "guy762.MM.KotORCore" --
    1.6/AdditionalMods/_DroidsBase/Defs/ThingDefs_DroidEquipment/ (the 9 files
    the packet names: 3 armor tiers, cloak, utility-weapons, weapons,
    light-cannons, sensors, tech). ThingDefs_DroidBatteries.xml and
    ThingDefs_RepairKits.xml in the SAME folder are consumable/resource items,
    not apparel -- correctly excluded by the "9 files" scope, not walked here.
  guy762.KotORDroids, workshop 3047371944, packageId "guy762.KotORDroids" --
    1.6/Defs/ThingDefs_DroidEquipment/*.xml (5 files: sensors, shields,
    shields_exotic, tech, hvyshields) -- the packet's own "+ kotordroids
    equipment" input. Confirmed genuinely ADDITIONAL, not a duplicate
    distribution of kotorcore's copy: defName diff shows only 2 names in
    common (guy762_DroidHardware_regen, guy762_DroidSoftware_exchange), and
    both of those are DEAD COMMENTS in kotorcore's own file (ET.parse without
    comment-preservation never sees them) -- no real collision.

SCOPE NARROWED BY WHAT THE SOURCE ITSELF GATES ON, not a guess:
  Every item in Apparel_KotORDroidWeapons.xml (13), Apparel_KotORLightCannons.xml
  (15) and Apparel_KotORDroidUtilityWeapons.xml (4) -- the "weapon"/"gadget"
  mount slots -- carries `Class="MVCF.Comps.CompProperties_VerbGiver"`
  (Multi Verb Combat Framework), confirmed by grep: 13/13, 15/15, 4/4. Every
  shield item (Apparel_KotORDroidShields.xml 11, _exotic.xml 3,
  Apparel_KotORHvyShields.xml 10) plus the cloak (Apparel_KotORDroidCloak.xml,
  1) activates via `SelfHediffVerb.Verb_SelfHediff` (a self-cast, cooldown-
  gated hediff-apply verb). Neither MVCF nor SelfHediffVerb ships in
  Droidworks' own assembly (SelfHediffVerb exists only as Armoury's OWN C#
  port, JawaArmoury.dll -- a different mod, and depending on it for Droidworks'
  droids to wear a shield is exactly the cross-mod coupling this item's brief
  says to avoid). These 4 slots of the six are therefore BLOCKED wholesale,
  every excluded element logged by defName to the manifest -- not silently
  dropped. What ships this pass: hardware, software and sensor (all three
  share one ParentName chain, guy762_DroidTech/guy762_DroidCraftableTech) plus
  the 3 armor tiers (a stat/coverage item, not one of the six slots, but in
  the same 9 files and apparel by function). A follow-up item can port
  SelfHediffVerb into Droidworks' own namespace (shield/cloak) and/or absorb
  MVCF-driven weapon mounts as their own pass (matches how kotorweapons needed
  its own generator) -- neither is this item's build.

BODY GROUPS: Droidworks races use the vanilla `Human` BodyDef (Races_Base.xml:
`<race><body>Human</body></race>`), never kotorcore's own custom
`Bodies_KotORDroid.xml`/`BodyPartGroups.xml`. The two body-part-group tokens
the surviving families actually use, `guy762BG_Droid_Tech_hardware` and
`_software`, are pure slot-bookkeeping tags in the SOURCE too (declared
standalone in kotorcore's BodyPartGroups.xml, not tied to any `<part>` on a
BodyDef -- confirmed by reading that file) -- RENAMED here to
`RSW_DW_BG_ModuleHardware`/`RSW_DW_BG_ModuleSoftware` rather than referencing
kotorcore's Names (which would be a silent dependency on a donor set to
retire, R4). Sensor items already used vanilla `Eyes` in the source; armor
items already use vanilla FullHead/Neck/Torso/Shoulders/Arms/Hands/Legs/Feet
-- neither needs a repoint.

LOOT-ONLY (design doc B2 + ruling 8): every `<recipeMaker>`, `<costList>`,
`<costStuffCount>`, `<stuffCategories>` is dropped, unconditionally. No
absorbed module is craftable by any means this item builds.

Two more surgical fixes, applied to every KEPT element:
  - `CompProperties_CauseHediff_Apparel`'s `<part>ABF_BodyPart_Synstruct_Core</part>`
    (Artificial Beings Framework's own body-part def -- Droidworks droids
    have a vanilla Human body, not an ABF synstruct body) is stripped, not
    repointed -- the comp applies the hediff to the whole pawn instead, which
    is the vanilla no-`<part>` default and a strictly safer fallback.
  - `<equippedStatOffsets>` entries naming `ABF_Stat_Artificial_*` StatDefs
    (ABF's own framework stats, currently resolvable only because
    Killathon.ArtificialBeings happens to be active) are dropped -- an inert
    stat offset today, a dangling cross-reference the moment ABF retires
    (R2), and never read by anything a Droidworks pawn's own C# touches.

descriptionHyperlinks: `<HediffDef>` entries are renamed alongside their
target (kept 1:1, same item). `<AlienRace.ThingDef_AlienRace>` entries are
repointed to `RSW_DW_Race_<orig>` when that race was actually generated
(checked against the real RSW_DW_Race_guy762_DroidRace_* defNames in
Defs/Races_KotOR.xml, not assumed) and DROPPED, logged, otherwise. No
`<ThingDef>`-type hyperlink survives in the kept content (verified: none of
the 9+5 files carry one outside a dead comment).

Generator shape borrows gen_kotorcore_absorption.py's discipline (verify the
About.xml packageId before trusting a workshop folder id, log every exclusion
by defName+file+reason to a manifest, copy+verify every texPath before
trusting it, defName collision-checked against this generator's own prior
output) but does NOT borrow its "preserve the donor's own abstract ParentName
chain" mechanism -- that would either duplicate Armoury's already-absorbed
`guy762_DroidTech`/`guy762_apparelbase` Name= templates (a Name= collision the
moment both mods are active, RimWorld: "Could not register node ... already
used in this mod") or silently make Droidworks depend on Armoury being active.
Instead every kept element is re-parented onto three small, fully
self-contained abstracts this file also emits (RSW_DW_ModuleApparelBase,
RSW_DW_ModuleBase_Tech, RSW_DW_ModuleBase_Armor) whose fields were hand-
resolved by reading the donor's whole ParentName chain ONCE (documented
inline) rather than replicated as a live inheritance walk.

Does not deploy and does not touch the live game: guy762.mm.kotorcore and
guy762.kotordroids stay active in ModsConfig.xml (retirement is R1/R4, gated
on this item plus B3/C1/C2/C7/D1/A3 per the design doc's §2 table) -- a
defName-preserving copy is not what this generator does (defNames are
renamed, RSW_DW_Module_*), so there is no collision risk either way.
"""
import os
import shutil
import sys
import xml.etree.ElementTree as ET


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


_REPO_ROOT = _find_repo_root(os.path.dirname(__file__))
DW_ROOT = os.path.join(_REPO_ROOT, "src", "RimStarWars", "Droidworks")
DEFS_ROOT = os.path.join(DW_ROOT, "Defs")
TEX_ROOT = os.path.join(DW_ROOT, "Textures")
RACES_KOTOR_PATH = os.path.join(DEFS_ROOT, "Races_KotOR.xml")

KOTORCORE_FOLDER = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3254370945"
KOTORDROIDS_FOLDER = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3047371944"
KOTORCORE_PACKAGE_ID = "guy762.MM.KotORCore"
KOTORDROIDS_PACKAGE_ID = "guy762.KotORDroids"

KC_EQUIP = os.path.join(KOTORCORE_FOLDER, "1.6", "AdditionalMods", "_DroidsBase",
                        "Defs", "ThingDefs_DroidEquipment")
KD_EQUIP = os.path.join(KOTORDROIDS_FOLDER, "1.6", "Defs", "ThingDefs_DroidEquipment")
KC_TEX = os.path.join(KOTORCORE_FOLDER, "Textures")
KD_TEX = os.path.join(KOTORDROIDS_FOLDER, "Textures")

# The 9 files the packet names (kotorcore) -- explicitly NOT the whole folder,
# so ThingDefs_DroidBatteries.xml/ThingDefs_RepairKits.xml (consumables, not
# apparel) are excluded by construction, never by a per-element filter.
KC_FILES = [
    "Apparel_KotORDroidArmor_heavy.xml",
    "Apparel_KotORDroidArmor_light.xml",
    "Apparel_KotORDroidArmor_medium.xml",
    "Apparel_KotORDroidCloak.xml",
    "Apparel_KotORDroidUtilityWeapons.xml",
    "Apparel_KotORDroidWeapons.xml",
    "Apparel_KotORLightCannons.xml",
    "Apparel_SWDroidSensors.xml",
    "Apparel_SWDroidTech.xml",
]
# The packet's "+ kotordroids equipment" input -- kotordroids' OWN
# ThingDefs_DroidEquipment folder, confirmed genuinely additional (see
# module docstring).
KD_FILES = [
    "Apparel_KotORDroidSensors.xml",
    "Apparel_KotORDroidShields.xml",
    "Apparel_KotORDroidShields_exotic.xml",
    "Apparel_KotORDroidTech.xml",
    "Apparel_KotORHvyShields.xml",
]

OUT_SUBDIR = "Absorbed_KotorDroidModules"
OUT_FILE_PREFIX = "Absorbed_KotorDroidModules_"

# Any element (recursively serialized) mentioning one of these is EXCLUDED
# wholesale -- see module docstring. Namespaces are prefix-matched.
BLOCKED_NAMESPACES = (
    "MVCF.",
    "SelfHediffVerb.",
    "AthenaFramework.",
    "VanillaApparelExpanded.",
    "guy762_Ionization.",
)

# ParentName -> our own family. Anything not in either set is out of scope
# (weapon/shield/gadget mount families) and excluded even on the rare chance
# it slips past the blocked-namespace check.
TECH_PARENTS = {"guy762_DroidTech", "guy762_DroidCraftableTech"}
ARMOR_PARENTS = {"guy762_DroidArmorMakeable", "KotORDroidArmor"}
EXCLUDED_PARENT_REASONS = {
    "BaseFilth": "not apparel (Filth ThingDef, a weapon VFX byproduct) -- out of scope",
    "guy762_DroidWeaponBase": "weapon-mount family -- out of B2 scope, needs its own verb/projectile port",
    "guy762_DroidWeaponCraftableBase": "weapon/gadget-mount family -- out of B2 scope, needs its own verb/projectile port",
    "guy762_DroidShieldBase": "shield-mount family -- SelfHediffVerb-driven, out of B2 scope",
    "guy762_DroidShieldCraftableBase": "shield-mount family -- SelfHediffVerb-driven, out of B2 scope",
    "guy762_HvyShieldBase": "heavy-shield family -- SelfHediffVerb-driven, out of B2 scope",
    "guy762_HvyShieldCraftableBase": "heavy-shield family -- SelfHediffVerb-driven, out of B2 scope",
}

BG_RENAME = {
    "guy762BG_Droid_Tech_hardware": "RSW_DW_BG_ModuleHardware",
    "guy762BG_Droid_Tech_software": "RSW_DW_BG_ModuleSoftware",
    "guy762BG_Droid_Tech_sensor": "RSW_DW_BG_ModuleSensor",  # unused by source today, renamed for completeness
}

BLOCKED_STAT_PREFIXES = ("ABF_Stat_Artificial_",)


class Report(object):
    def __init__(self):
        self.notes, self.warns = [], []

    def note(self, msg):
        self.notes.append(msg)
        print("NOTE  " + msg)

    def warn(self, msg):
        self.warns.append(msg)
        print("WARN  " + msg)


R = Report()


def rename_dn(orig):
    if orig.startswith("guy762_"):
        return "RSW_DW_Module_" + orig[len("guy762_"):]
    return "RSW_DW_Module_" + orig


# --------------------------------------------------------- serialization --
def _escape_text(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _escape_attr(s):
    return _escape_text(s).replace('"', "&quot;")


def serialize(el, indent=1):
    pad = "  " * indent
    attrs = "".join(' %s="%s"' % (k, _escape_attr(v)) for k, v in el.attrib.items())
    children = list(el)
    text = (el.text or "").strip()

    if not children and not text:
        return "%s<%s%s />" % (pad, el.tag, attrs)
    if not children:
        return "%s<%s%s>%s</%s>" % (pad, el.tag, attrs, _escape_text(text), el.tag)

    lines = ["%s<%s%s>" % (pad, el.tag, attrs)]
    if text:
        lines.append("%s  %s" % (pad, _escape_text(text)))
    for c in children:
        lines.append(serialize(c, indent + 1))
    lines.append("%s</%s>" % (pad, el.tag))
    return "\n".join(lines)


def matched_blocked_namespace(el):
    blob = ET.tostring(el, encoding="unicode")
    for ns in BLOCKED_NAMESPACES:
        if ns in blob:
            return ns
    return None


# ------------------------------------------------------------- transform --
# statBases entries that are only meaningful alongside a recipeMaker/
# stuffCategories (crafting cost, or a stuff-material stat multiplier) --
# dead weight once those are stripped (loot-only), not an error to keep but
# actively misleading, so they're dropped too.
DEAD_STATBASE_TAGS = ("WorkToMake", "StuffEffectMultiplierArmor")


def strip_recipe_and_cost(el):
    for tag in ("recipeMaker", "costList", "costStuffCount", "stuffCategories", "verbs"):
        child = el.find(tag)
        if child is not None:
            el.remove(child)
    sb = el.find("statBases")
    if sb is not None:
        for child in list(sb):
            if child.tag in DEAD_STATBASE_TAGS:
                sb.remove(child)
        if len(sb) == 0:
            el.remove(sb)


def strip_abf_parts_and_stats(el):
    comps = el.find("comps")
    if comps is not None:
        for li in comps.findall("li"):
            part = li.find("part")
            if part is not None and (part.text or "").strip() == "ABF_BodyPart_Synstruct_Core":
                li.remove(part)
                R.note("stripped <part>ABF_BodyPart_Synstruct_Core</part> from a comp on %s "
                       "-- Droidworks droids have a vanilla Human body, not an ABF synstruct one; "
                       "the hediff now applies to the whole pawn (vanilla no-<part> default)"
                       % (el.find("defName").text if el.find("defName") is not None else "?"))
    eso = el.find("equippedStatOffsets")
    if eso is not None:
        for child in list(eso):
            if any(child.tag.startswith(p) for p in BLOCKED_STAT_PREFIXES):
                eso.remove(child)
                R.note("dropped equippedStatOffsets/%s from %s -- Artificial Beings Framework's own "
                       "StatDef, inert on a non-ABF pawn and a dangling cross-reference once ABF retires"
                       % (child.tag, el.find("defName").text if el.find("defName") is not None else "?"))
        if len(eso) == 0:
            el.remove(eso)


def rewrite_body_part_groups(el):
    apparel = el.find("apparel")
    if apparel is None:
        return
    bpg = apparel.find("bodyPartGroups")
    if bpg is None:
        return
    for li in bpg.findall("li"):
        if li.text and li.text.strip() in BG_RENAME:
            li.text = BG_RENAME[li.text.strip()]


def rewrite_hyperlinks(el, dn, race_defnames, kept_hediff_origs):
    hl = el.find("descriptionHyperlinks")
    if hl is None:
        return
    keep = []
    for child in list(hl):
        if child.tag == "HediffDef":
            orig = (child.text or "").strip()
            if orig in kept_hediff_origs:
                child.text = rename_dn(orig)
                child.attrib.pop("MayRequire", None)
                keep.append(child)
            else:
                R.note("dropped descriptionHyperlinks/HediffDef %r from %s -- its ThingDef was not kept"
                       % (orig, dn))
        elif child.tag == "AlienRace.ThingDef_AlienRace":
            orig = (child.text or "").strip()
            new_race = "RSW_DW_Race_" + orig
            if new_race in race_defnames:
                child.text = new_race
                child.attrib.pop("MayRequire", None)
                keep.append(child)
            else:
                R.note("dropped descriptionHyperlinks/AlienRace.ThingDef_AlienRace %r from %s "
                       "-- %s was not found among Droidworks' generated KotOR races" % (orig, dn, new_race))
        else:
            R.note("dropped descriptionHyperlinks/%s from %s -- unhandled hyperlink shape, not guessed at"
                   % (child.tag, dn))
    hl.clear()
    for c in keep:
        hl.append(c)
    if len(hl) == 0:
        el.remove(hl)


def rewrite_comp_hediff_refs(el):
    comps = el.find("comps")
    if comps is None:
        return
    for li in comps.findall("li"):
        hediff = li.find("hediff")
        if hediff is not None and hediff.text and hediff.text.strip().startswith("guy762_"):
            hediff.text = rename_dn(hediff.text.strip())


def _collect_all_texpaths(el, out):
    if el.tag in ("texPath", "iconPath", "uiIconPath") and el.text and el.text.strip():
        out.add(el.text.strip())
    for c in el:
        _collect_all_texpaths(c, out)


def find_and_copy_texture(tex_path, seen, missing):
    if tex_path in seen or tex_path in missing:
        return
    for root in (KC_TEX, KD_TEX):
        for ext in (".png", ".jpg", ".jpeg"):
            src = os.path.join(root, tex_path.replace("/", os.sep) + ext)
            if os.path.isfile(src):
                dst = os.path.join(TEX_ROOT, tex_path.replace("/", os.sep) + ext)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(src, dst)
                seen.add(tex_path)
                return
    missing.add(tex_path)
    R.warn("texPath %r has no .png/.jpg/.jpeg under either source Textures/ -- reference kept, art NOT copied"
           % tex_path)


def write_defs_file(filename, header_lines, elements):
    if not elements:
        return
    out_dir = os.path.join(DEFS_ROOT, OUT_SUBDIR)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    body = "\n\n".join(serialize(e) for e in elements)
    fh = ['<?xml version="1.0" encoding="utf-8" ?>']
    for line in header_lines:
        fh.append(line)
    fh.append("<Defs>\n")
    fh.append(body)
    fh.append("\n</Defs>\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(fh))
    R.note("wrote %s (%d defs)" % (os.path.relpath(path, _REPO_ROOT), len(elements)))


BASES_HEADER = [
    "<!-- Self-contained module-apparel bases for Absorbed_KotorDroidModules.",
    "     GENERATED by src/RimStarWars/Droidworks/Source/gen_droidworks_modules.py.",
    "     Do not hand-edit; re-run the generator.",
    "",
    "     Hand-resolved ONCE from guy762.mm.kotorcore's own ParentName chain",
    "     (1.6/Defs/ThingDefs_WeaponsArmorsGadgets/_BASE_SWKotORApparel.xml),",
    "     NOT a live inheritance walk; see gen_droidworks_modules.py's module",
    "     docstring for why (avoids a Name= collision with Armoury's own",
    "     already-absorbed copy of the same donor abstracts, and avoids making",
    "     Droidworks depend on Armoury being active).",
    "",
    "     RSW_DW_ModuleApparelBase mirrors guy762_apparelbase (a standalone",
    "     root, no vanilla ParentName in the source either). RSW_DW_ModuleBase_Tech",
    "     mirrors guy762_DroidTech's REAL root, vanilla ApparelNoQualityBase (NOT",
    "     guy762_apparelbase: the utility-item branch in kotorcore's own tree",
    "     chains through guy762_UtilityItemBase, ParentName=\"ApparelNoQualityBase\",",
    "     a different root entirely, confirmed by reading the source file).",
    "     RSW_DW_ModuleBase_Armor adds CompColorable+CompQuality on top of the",
    "     apparel root, matching guy762_apparelmakeable's own addition. -->",
]

BASES_BODY = """  <BodyPartGroupDef>
    <defName>RSW_DW_BG_ModuleHardware</defName>
    <label>hardware upgrade slot</label>
  </BodyPartGroupDef>

  <BodyPartGroupDef>
    <defName>RSW_DW_BG_ModuleSoftware</defName>
    <label>software upgrade slot</label>
  </BodyPartGroupDef>

  <BodyPartGroupDef>
    <defName>RSW_DW_BG_ModuleSensor</defName>
    <label>sensor upgrade slot</label>
  </BodyPartGroupDef>

  <ThingDef Name="RSW_DW_ModuleApparelBase" Abstract="True">
    <thingClass>Apparel</thingClass>
    <category>Item</category>
    <drawerType>MapMeshOnly</drawerType>
    <selectable>True</selectable>
    <pathCost>14</pathCost>
    <useHitPoints>True</useHitPoints>
    <techLevel>Spacer</techLevel>
    <drawGUIOverlay>true</drawGUIOverlay>
    <statBases>
      <MaxHitPoints>100</MaxHitPoints>
      <Flammability>1.0</Flammability>
      <DeteriorationRate>2</DeteriorationRate>
      <Beauty>-3</Beauty>
    </statBases>
    <thingCategories>
      <li>Apparel</li>
    </thingCategories>
    <altitudeLayer>Item</altitudeLayer>
    <alwaysHaulable>True</alwaysHaulable>
    <tickerType>Never</tickerType>
    <burnableByRecipe>true</burnableByRecipe>
    <smeltable>true</smeltable>
    <tradeability>All</tradeability>
    <apparel>
      <canBeDesiredForIdeo>false</canBeDesiredForIdeo>
    </apparel>
    <comps>
      <li Class="CompProperties_Forbiddable" />
      <li Class="CompProperties_Styleable" />
    </comps>
  </ThingDef>

  <ThingDef Name="RSW_DW_ModuleBase_Tech" ParentName="ApparelNoQualityBase" Abstract="True">
    <thingClass>Apparel</thingClass>
    <category>Item</category>
    <techLevel>Spacer</techLevel>
    <resourceReadoutPriority>Middle</resourceReadoutPriority>
    <tradeNeverStack>false</tradeNeverStack>
    <smeltable>false</smeltable>
    <burnableByRecipe>false</burnableByRecipe>
    <drawGUIOverlay>false</drawGUIOverlay>
    <tradeability>All</tradeability>
    <statBases>
      <EquipDelay>38</EquipDelay>
      <MaxHitPoints>80</MaxHitPoints>
    </statBases>
    <thingCategories>
      <li>ApparelUtility</li>
    </thingCategories>
    <apparel>
      <countsAsClothingForNudity>false</countsAsClothingForNudity>
      <careIfWornByCorpse>false</careIfWornByCorpse>
      <careIfDamaged>true</careIfDamaged>
      <ignoredByNonViolent>false</ignoredByNonViolent>
      <wearPerDay>0</wearPerDay>
      <canBeDesiredForIdeo>false</canBeDesiredForIdeo>
      <layers>
        <li>Belt</li>
      </layers>
    </apparel>
    <comps>
      <li Class="CompProperties_Forbiddable" />
      <li>
        <compClass>CompColorable</compClass>
      </li>
      <li Class="CompProperties_Styleable" />
    </comps>
  </ThingDef>

  <ThingDef Name="RSW_DW_ModuleBase_Armor" ParentName="RSW_DW_ModuleApparelBase" Abstract="True">
    <comps>
      <li>
        <compClass>CompColorable</compClass>
      </li>
      <li>
        <compClass>CompQuality</compClass>
      </li>
    </comps>
  </ThingDef>
"""


def main():
    for folder, pkg, label in ((KOTORCORE_FOLDER, KOTORCORE_PACKAGE_ID, "kotorcore"),
                                (KOTORDROIDS_FOLDER, KOTORDROIDS_PACKAGE_ID, "kotordroids")):
        about = os.path.join(folder, "About", "About.xml")
        if not os.path.isfile(about):
            R.warn("About.xml not found at %s -- ABORTING" % about)
            sys.exit(1)
        text = open(about, "r", encoding="utf-8-sig").read()
        if pkg not in text:
            R.warn("About.xml at %s does not contain expected packageId %r -- ABORTING, do not guess the folder"
                   % (about, pkg))
            sys.exit(1)
        R.note("confirmed %s workshop folder is packageId %s" % (label, pkg))

    race_defnames = set()
    if os.path.isfile(RACES_KOTOR_PATH):
        for _, el in ET.iterparse(RACES_KOTOR_PATH):
            if el.tag == "defName" and el.text and el.text.strip().startswith("RSW_DW_Race_"):
                race_defnames.add(el.text.strip())
    R.note("%d Droidworks KotOR race defNames known (Races_KotOR.xml) -- descriptionHyperlinks repoint against these"
           % len(race_defnames))

    src_files = []
    for fn in KC_FILES:
        src_files.append((os.path.join(KC_EQUIP, fn), "kotorcore/" + fn))
    for fn in KD_FILES:
        src_files.append((os.path.join(KD_EQUIP, fn), "kotordroids/" + fn))

    all_thing_els = []       # (dn, el, src_rel) concrete kept ThingDefs
    all_hediff_els = {}      # orig defName -> (el, src_rel), every HediffDef seen
    excluded = []            # (dn, src_rel, reason)
    n_source_things = 0
    referenced_hediffs = set()  # orig hediff defNames a kept ThingDef's <comps>/<hediff> uses
    seen_dn = set()

    for src_path, src_rel in src_files:
        if not os.path.isfile(src_path):
            R.warn("expected source file missing: %s -- SKIPPED" % src_path)
            continue
        tree = ET.parse(src_path)
        root = tree.getroot()
        for el in root:
            if el.tag is ET.Comment or not isinstance(el.tag, str):
                continue
            dn_el = el.find("defName")
            dn = dn_el.text.strip() if dn_el is not None and dn_el.text else None

            if el.tag == "HediffDef":
                if dn:
                    all_hediff_els[dn] = (el, src_rel)
                continue

            if el.tag != "ThingDef":
                continue
            if el.attrib.get("Abstract") == "True":
                continue  # no abstracts expected in these 14 files; guard anyway
            n_source_things += 1

            blocked_ns = matched_blocked_namespace(el)
            parent = el.attrib.get("ParentName")
            if blocked_ns:
                excluded.append((dn or "(no defName)", src_rel,
                                  "references %s (framework Droidworks does not ship)" % blocked_ns))
                continue
            if parent in EXCLUDED_PARENT_REASONS:
                excluded.append((dn or "(no defName)", src_rel, EXCLUDED_PARENT_REASONS[parent]))
                continue
            if parent not in TECH_PARENTS and parent not in ARMOR_PARENTS:
                excluded.append((dn or "(no defName)", src_rel,
                                  "unrecognised ParentName %r -- not in the tech or armor family, not guessed at" % parent))
                continue
            if not dn:
                excluded.append(("(no defName)", src_rel, "concrete ThingDef with no defName"))
                continue
            if dn in seen_dn:
                R.warn("defName %r seen twice across source files (also %s) -- SKIPPED duplicate" % (dn, src_rel))
                continue
            seen_dn.add(dn)

            # find every <hediff> this item's comps reference, before renaming
            comps = el.find("comps")
            if comps is not None:
                for li in comps.findall("li"):
                    h = li.find("hediff")
                    if h is not None and h.text:
                        referenced_hediffs.add(h.text.strip())

            all_thing_els.append((dn, parent, el, src_rel))

    R.note("%d concrete ThingDefs seen across %d source files; %d excluded, %d kept"
           % (n_source_things, len(src_files), len(excluded), len(all_thing_els)))

    # --------------------------------------------------------- transform --
    tex_paths = set()
    tech_elements, armor_elements = [], []
    kept_hediff_origs = set()

    for dn, parent, el, src_rel in all_thing_els:
        new_dn = rename_dn(dn)
        el.attrib.clear()
        el.attrib["ParentName"] = "RSW_DW_ModuleBase_Tech" if parent in TECH_PARENTS else "RSW_DW_ModuleBase_Armor"
        dn_node = el.find("defName")
        dn_node.text = new_dn

        strip_recipe_and_cost(el)
        strip_abf_parts_and_stats(el)
        rewrite_body_part_groups(el)
        rewrite_comp_hediff_refs(el)
        _collect_all_texpaths(el, tex_paths)

        if parent in TECH_PARENTS:
            tech_elements.append((dn, new_dn, el, src_rel))
        else:
            armor_elements.append((dn, new_dn, el, src_rel))

    # HediffDefs: only the ones a KEPT ThingDef actually references.
    hediff_elements = []
    for orig, (el, src_rel) in sorted(all_hediff_els.items()):
        if orig in referenced_hediffs:
            new_dn = rename_dn(orig)
            dn_node = el.find("defName")
            dn_node.text = new_dn
            hediff_elements.append((orig, new_dn, el, src_rel))
            kept_hediff_origs.add(orig)
        # else: orphaned (its ThingDef was excluded) -- silently not ported,
        # already implied by that ThingDef's own manifest entry.

    if referenced_hediffs - kept_hediff_origs:
        R.warn("comps referenced hediffs never found as a HediffDef in the source files: %s"
               % sorted(referenced_hediffs - kept_hediff_origs))

    # Second pass: hyperlinks need to know the FINAL kept-hediff set.
    for dn, new_dn, el, src_rel in tech_elements + armor_elements:
        rewrite_hyperlinks(el, new_dn, race_defnames, kept_hediff_origs)

    # ---------------------------------------------------------- assets ---
    tex_seen, tex_missing = set(), set()
    for t in sorted(tex_paths):
        find_and_copy_texture(t, tex_seen, tex_missing)

    # ------------------------------------------------------------- write --
    # BASES_BODY is written verbatim (hand-authored constant, not run through
    # serialize()) -- write_defs_file's element path is for the absorbed
    # content below; the bases file is emitted directly here instead.
    os.makedirs(os.path.join(DEFS_ROOT, OUT_SUBDIR), exist_ok=True)
    bases_path = os.path.join(DEFS_ROOT, OUT_SUBDIR, OUT_FILE_PREFIX + "Bases.xml")
    with open(bases_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8" ?>\n')
        for line in BASES_HEADER:
            f.write(line + "\n")
        f.write("<Defs>\n\n")
        f.write(BASES_BODY)
        f.write("\n</Defs>\n")
    R.note("wrote %s (3 BodyPartGroupDefs + 3 base ThingDefs)"
           % os.path.relpath(bases_path, _REPO_ROOT))

    tech_header = [
        "<!-- Absorbed from guy762.mm.kotorcore + guy762.KotORDroids (hardware/",
        "     software/sensor module apparel, 3 of the six KotOR slots that",
        "     ship this pass; see gen_droidworks_modules.py's module docstring",
        "     for why weapon/gadget/shield are excluded). GENERATED by",
        "     src/RimStarWars/Droidworks/Source/gen_droidworks_modules.py.",
        "     DROIDWORKS_MODULE_ABSORB_1. No recipeMaker on any: loot-only.",
        "     Do not hand-edit; re-run the generator. -->",
    ]
    armor_header = [
        "<!-- Absorbed from guy762.mm.kotorcore (3 droid armor tiers: light/",
        "     medium/heavy). GENERATED by",
        "     src/RimStarWars/Droidworks/Source/gen_droidworks_modules.py.",
        "     DROIDWORKS_MODULE_ABSORB_1. No recipeMaker on any: loot-only.",
        "     Do not hand-edit; re-run the generator. -->",
    ]
    hediff_header = [
        "<!-- HediffDefs paired with Absorbed_KotorDroidModules_Tech.xml's",
        "     CompProperties_CauseHediff_Apparel comps. GENERATED by",
        "     src/RimStarWars/Droidworks/Source/gen_droidworks_modules.py. -->",
    ]

    write_defs_file(OUT_FILE_PREFIX + "Tech.xml", tech_header, [e for _, _, e, _ in tech_elements])
    write_defs_file(OUT_FILE_PREFIX + "Armor.xml", armor_header, [e for _, _, e, _ in armor_elements])
    write_defs_file(OUT_FILE_PREFIX + "Hediffs.xml", hediff_header, [e for _, _, e, _ in hediff_elements])

    # -------------------------------------------------------------- manifest
    manifest_path = os.path.join(DEFS_ROOT, OUT_SUBDIR, OUT_FILE_PREFIX + "EXCLUDED_manifest.txt")
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(
            "guy762.mm.kotorcore + guy762.KotORDroids equipment classes EXCLUDED from\n"
            "DROIDWORKS_MODULE_ABSORB_1 (packet B2). Every entry references a framework\n"
            "class Droidworks does not ship (MVCF/SelfHediffVerb/AthenaFramework/\n"
            "VanillaApparelExpanded/guy762_Ionization), is a non-apparel VFX byproduct\n"
            "(Filth), or belongs to a weapon/shield/gadget mount family out of this\n"
            "item's scope -- see gen_droidworks_modules.py's module docstring for the\n"
            "full rationale per family. Regenerate by rerunning gen_droidworks_modules.py.\n\n"
            "defName\tsource file\treason\n"
        )
        for dn, rel, reason in excluded:
            f.write("%s\t%s\t%s\n" % (dn, rel, reason))
    R.note("wrote %s (%d excluded elements)" % (os.path.relpath(manifest_path, _REPO_ROOT), len(excluded)))

    # ------------------------------------------------------------ report --
    print("\n=== summary ===")
    print("source ThingDefs seen: %d; kept: %d (tech/software/hardware/sensor: %d, armor: %d); excluded: %d"
          % (n_source_things, len(tech_elements) + len(armor_elements), len(tech_elements),
             len(armor_elements), len(excluded)))
    print("HediffDefs ported: %d (of %d referenced by a kept comp)" % (len(hediff_elements), len(referenced_hediffs)))
    print("textures: %d found+copied, %d MISSING" % (len(tex_seen), len(tex_missing)))
    if tex_missing:
        print("missing textures: %s" % sorted(tex_missing))
    print("notes: %d, warnings: %d" % (len(R.notes), len(R.warns)))
    by_reason = {}
    for _, _, reason in excluded:
        key = reason.split(" -- ")[0].split(" (")[0]
        by_reason[key] = by_reason.get(key, 0) + 1
    print("\n=== excluded, by reason (top-level) ===")
    for k in sorted(by_reason):
        print("  %-70s %d" % (k, by_reason[k]))


if __name__ == "__main__":
    main()
