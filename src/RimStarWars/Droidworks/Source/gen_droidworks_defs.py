"""Generate DW_ races + kinds for every droid already captured in
extraction.json — the "unify every droid onto one framework" pass of
DROIDWORKS_DEF_GENERATOR_1.

Emits src/RimStarWars/Droidworks/Defs/Races_<Family>.xml (one HAR
AlienRace.ThingDef_AlienRace per source race, ParentName="DW_Race_Base" —
that base and the shared RSW_DW_HeadType_Blank head live in the hand-authored
Defs/Races_Base.xml, not regenerated here) and
src/RimStarWars/Droidworks/Defs/PawnKinds_<Family>.xml (one PawnKindDef per source
kind, race repointed at the matching DW_Race_<orig>).

Source data has THREE incompatible graphics shapes, discovered by reading
extraction.json and the actual PNGs on disk (never trust a field name
literally — verify against the Textures/ tree):
  - OuterRimDroidDepot (Asimov framework, family Humanlike/Animal): a body
    FOLDER ("OuterRim/Droid/B1/Body/") whose stem is derived by listing the
    folder for a "*_south.png" file — the stem happens to look like it
    encodes a HAR bodyType ("Naked_Male") but isn't: HAR's graphicPaths.path
    is used as a literal {stem}_{rotation}.png, no bodyType token inserted
    (confirmed against guy762's own HK_body_south.png, which has ONE
    bodytype declared but no bodytype token in the filename either). Animal-
    family races (Astromech, Muckraker, ...) have NO Body/Head split — single
    fused sprite, no head layer.
  - KotORDroids (already real HAR): body_path/head_path are already stems,
    but many concrete races declare NEITHER (bodySize/healthScale/moveSpeed/
    graphics all None) and inherit them from a SIBLING concrete race via
    parentName (HK50/HK51 <- HKseries, 3C/IT <- T3series, etc) — resolved
    here by walking races_by_orig, never guessed. A head_path of
    "768blank"/"512blank"/"1024blank" is the source mod's OWN convention for
    "no separate head art" (14 of 22 KotOR races) — treated as headless, not
    as a texture to hunt for.
  - JDS_Separatists (mechanoid framework): flat texPath + rotation, no
    bodyType token and no head layer at all (single full-body sprite,
    matches the stem+rotation pattern directly).

Every derived texture path is VERIFIED against Textures/ before being
written — a path that doesn't resolve to a real file is a loud, printed
miss, never a silently-emitted dead reference (CLAUDE.md: "a number about a
large artifact comes from measure, never a scan" — same discipline, applied
to "does this texPath exist").

Chassis classification (6 buckets, BENCH's own filed spec, verbatim —
not this generator's call to change):
  battle 1.0/0   heavy 1.0/2   gonk-power 0.33/3
  astromech-labour 0.33/0   protocol 0.033/0   probe 1.0/1
(powerFallPerDay/energyDensity). Every one of the 57 races is classified by
label + family + framework + the writer's own judgement of what the droid
actually IS (a battle droid vs a protocol droid vs an astromech) — see
CHASSIS_PLAN below, every entry carries a note explaining the call.

Weapon/apparel gear: RimWorld's PawnKindDef apparelTags/weaponTags are TAG
matching (a tag with zero matching loaded ThingDefs yields no gear, not a
crash) — so a tag-list value captured in extraction.json is carried
VERBATIM, even though it names a mod Droidworks does not depend on (that is
a live-with-later art gap, not a broken cross-reference). What is NEVER
carried: the free-prose "apparelRequired <defName> <defName>..." segments
buried in some KotOR kinds' notes — those are literal defName references
into KotORWeapons/KotORDroids, and re-emitting a defName parsed out of prose
would be exactly the guess this project has been burned by before. Those
kinds get their PARSEABLE "apparelTags: ..." segment carried and the
apparelRequired segment dropped, loudly, per BENCH's "never guess a weapon
defName" rule.

The "4 Jawa_Droid_* kinds keep Jawa_FreeDroidEnclaves" instruction in this
item's brief does not match extraction.json: zero kind defNames, labels or
fields anywhere in the file mention "Jawa" in that sense (grepped the raw
JSON text). Per the item's own fallback ("if you can't find exactly 4
matching that description, say so rather than guessing"), no kind gets a
faction assignment here — see the printed NOTE at the top of the run.
"""
import json
import os
import re
import struct
import sys
import zlib


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
EXTRACTION_PATH = os.path.join(DW_ROOT, "Source", "extraction.json")
TEX_ROOT = os.path.join(DW_ROOT, "Textures")
DEFS_ROOT = os.path.join(DW_ROOT, "Defs")

NS_PREFIX = {
    "KotORDroids": "KotOR/",
    "JDS_Separatists": "JDS/",
    "OuterRimDroidDepot": "",
    "OuterRimGalacticEmpire": "",
}
BLANK_HEAD_RE = re.compile(r"^\d+blank$", re.IGNORECASE)
RGBA_RE = re.compile(r"RGBA\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)\s*weight(\d+)")
RGB_TUPLE_RE = re.compile(r"\((\d+),\s*(\d+),\s*(\d+)\)")

# chassis bucket -> (powerFallPerDay, energyDensity, chassisClass int default)
# int codes per Source/Droidworks/DroidworksModExtension.cs:
#   0 labour  1 protocol  2 astromech  3 battle  4 heavy  5 probe  6 power
CHASSIS_TUNING = {
    "battle":            (1.0, 0, 3),
    "heavy":             (1.0, 2, 4),
    "gonk-power":        (0.33, 3, 6),
    "astromech-labour":  (0.33, 0, 0),   # int refined per-race, see ASTROMECH_SHAPED
    "protocol":          (0.033, 0, 1),
    "probe":             (1.0, 1, 5),
}
# within the astromech-labour bucket: dome/utility-cart shaped droids get the
# "astromech" int (2); everything else in that bucket gets "labour" (0).
# Tuning numbers are identical either way — this only affects the int code.
ASTROMECH_SHAPED = {
    "OuterRim_AstromechDroid", "guy762_DroidRace_T3series",
    "guy762_DroidRace_3Cseries", "guy762_DroidRace_R8009UD",
    "guy762_DroidRace_ITseries",
}

# --------------------------------------------------- DROIDWORKS_FAMILY_LAYER_1
# OWNER RULING 2026-08-29 (ledger DROIDWORKS_FAMILY_LAYER_1): insert 7
# chassis-family abstracts between DW_Race_Base and the 57 concrete races —
# DW_Race_Base -> DW_Family_{Labour,Protocol,Astromech,Battle,Heavy,Probe,
# Power} -> concrete races. The 6 CHASSIS_TUNING buckets above become 7
# families by splitting "astromech-labour" exactly along ASTROMECH_SHAPED
# (already computed above, for the chassisClass int) — the ruling's own
# family list order (Labour, Protocol, Astromech, Battle, Heavy, Probe,
# Power) matches DroidworksModExtension.cs's own int-code order (0..6)
# verbatim, confirming this split IS the intended 7th family, not a guess.
FAMILY_BY_BUCKET = {
    "battle": "battle", "heavy": "heavy", "gonk-power": "power",
    "protocol": "protocol", "probe": "probe",
}
FAMILY_DISPLAY = {
    "labour": "Labour", "protocol": "Protocol", "astromech": "Astromech",
    "battle": "Battle", "heavy": "Heavy", "probe": "Probe", "power": "Power",
}
FAMILY_TUNING = {
    "battle":    (1.0, 0, 3),
    "heavy":     (1.0, 2, 4),
    "power":     (0.33, 3, 6),
    "astromech": (0.33, 0, 2),
    "labour":    (0.33, 0, 0),
    "protocol":  (0.033, 0, 1),
    "probe":     (1.0, 1, 5),
}


def family_for(orig, bucket):
    if bucket == "astromech-labour":
        return "astromech" if orig in ASTROMECH_SHAPED else "labour"
    return FAMILY_BY_BUCKET[bucket]


def family_dn(family_key):
    return "DW_Family_" + FAMILY_DISPLAY[family_key]


# 🔴 FIXED, DROIDWORKS_DETONATION_ROLLOUT_1 (2026-09-02): this was emitting
# "Droidworks.CompProperties_DroidDetonation" — the class's real namespace is
# RimMandrake.StarWars.Droidworks (CompDroidDetonation.cs:5, verified against
# source, not guessed) per this project's own naming-scheme rule (C# namespaces
# nest RimMandrake[.StarWars|.Utinni].<Mod>). A blind regenerate under the old
# string would have silently broken GNK's Class resolution the moment this
# generator was next run — caught here because the DW_ROOT path bug (below)
# forced a real re-run to prove it, not because anyone was looking for it.
DETONATION_COMP_LI = '      <li Class="RimMandrake.StarWars.Droidworks.CompProperties_DroidDetonation" />'

# Races whose generated def must carry a <comps> block the generator does
# not otherwise derive from extraction.json — GNK's hand-wired
# CompDroidDetonation (DROIDWORKS_PILOT_GONK_1: "the gonk detonates by
# nature") plus its own explanatory comment, kept verbatim as history.
COMPS_OVERRIDE = {
    "OuterRim_GNKDroid": [
        '      <!-- "the gonk detonates by nature" (BENCH). Pilot wiring: no other\n'
        '           DW race attaches this comp yet, despite Heavy/Power/Probe carrying\n'
        '           energyDensity > 0 on their family abstract (DROIDWORKS_FAMILY_LAYER_1) —\n'
        '           the mechanic was built (CompDroidDetonation.cs) but never wired to any\n'
        "           other def. This is the first race to prove the wiring works end to\n"
        "           end; rolling it out to the rest is a follow-up, not this item. -->",
        DETONATION_COMP_LI,
    ],
}

# 🔴 DROIDWORKS_DETONATION_ROLLOUT_1: the rollout itself, computed rather than
# hand-listed. Every race whose FAMILY carries energyDensity > 0 (Heavy,
# Power, Probe — see FAMILY_TUNING) gets the same comp GNK proved, applied at
# render time in main() rather than as a second hardcoded defName list that
# could drift from FAMILY_TUNING/CHASSIS_PLAN the moment either changes.
DETONATION_ROLLOUT_COMP = [
    "      <!-- CompDroidDetonation, DROIDWORKS_DETONATION_ROLLOUT_1 (2026-09-02):",
    "           every energyDensity>0 race gets this, per its own family's",
    "           DroidworksExtension tuning (DROIDWORKS_FAMILY_LAYER_1). GNK proved",
    "           the wiring end to end; this is the rollout. -->",
    DETONATION_COMP_LI,
]

# orig race defName -> (bucket, note-or-None). Every one of the 57 races.
CHASSIS_PLAN = {
    # --- OuterRimDroidDepot, family Humanlike ---
    "OuterRim_BattleDroid":        ("battle", None),
    "OuterRim_BattleDroidAdvanced": ("battle", None),
    "OuterRim_CommandoDroid":      ("battle", None),
    "OuterRim_HKDroid":            ("battle", "assassin droid classed battle (combat-optimized), not protocol, despite the 'HK' naming echo"),
    "OuterRim_ImperialLaborDroid": ("astromech-labour", None),
    "OuterRim_KXSecurityDroid":    ("battle", None),
    "OuterRim_MagnaGuardDroid":    ("heavy", "bodyguard/elite melee unit judged heavier-chassis than a standard battle droid"),
    "OuterRim_ProtocolDroid":      ("protocol", None),
    "OuterRim_SuperBattleDroid":   ("heavy", "B2: larger/armored than B1, judged heavy"),
    "OuterRim_SuperTacticalDroid": ("heavy", None),
    "OuterRim_TacticalDroid":      ("heavy", "T-series tactical droid: canonically a large, slow command unit"),
    # --- OuterRimDroidDepot, family Animal ---
    "OuterRim_AstromechDroid":     ("astromech-labour", None),
    "OuterRim_MuckrakerDroid":     ("astromech-labour", "crab-shaped utility/mining droid, judged labour"),
    "OuterRim_DestroyerDroid":     ("battle", "droideka: elite combat unit despite the source mod's Animal-family tagging"),
    "OuterRim_DUMDroid":           ("astromech-labour", None),
    "OuterRim_FX7Droid":           ("astromech-labour", "medical droid has no dedicated bucket in BENCH's 6; judged closest to labour/utility"),
    "OuterRim_GNKDroid":           ("gonk-power", None),
    "OuterRim_MSEDroid":           ("astromech-labour", None),
    "OuterRim_SalvageAssistDroid": ("astromech-labour", None),
    # --- KotORDroids ---
    "guy762_DroidRace_HKseries":   ("battle", "labelled 'protocol droid' cover story, but inherentSkills show Shooting 20 / Melee 16 — classified by mechanism, not the cover label"),
    "guy762_DroidRace_HK50series": ("battle", "same HK-series combat lineage as HKseries"),
    "guy762_DroidRace_HK51series": ("battle", "explicitly an assassin droid"),
    "guy762_DroidRace_GE3PD":      ("protocol", None),
    "guy762_DroidRace_GE3LD":      ("astromech-labour", None),
    "guy762_DroidRace_GOTO":       ("protocol", "G0-T0 superintelligence droid, no combat stats; judged closest to the protocol/intelligence bucket"),
    "guy762_DroidRace_KM1MD":      ("astromech-labour", None),
    "guy762_DroidRace_KM1HMD":     ("astromech-labour", None),
    "guy762_DroidRace_KX12UPD":    ("probe", None),
    "guy762_DroidRace_KX12APD":    ("probe", "assassin-role variant of the K-X12 probe chassis; chassis form kept, role differs"),
    "guy762_DroidRace_MPDMkI":     ("battle", "patrol/security droid"),
    "guy762_DroidRace_R8009UD":    ("astromech-labour", None),
    "guy762_DroidRace_T3series":   ("astromech-labour", None),
    "guy762_DroidRace_3Cseries":   ("astromech-labour", None),
    "guy762_DroidRace_ITseries":   ("astromech-labour", "labelled 'utility droid' in extraction; judged by that label, not by IT-O's canon interrogation-droid role"),
    "guy762_DroidRace_DevWD":      ("heavy", None),
    "guy762_DroidRace_DevAD":      ("heavy", None),
    "guy762_DroidRace_SentWD":     ("heavy", None),
    "guy762_DroidRace_ADMkI":      ("heavy", None),
    "guy762_DroidRace_ADMkI_sf":   ("heavy", None),
    "guy762_DroidRace_ADMkIV":     ("heavy", None),
    "guy762_DroidRace_ADMkIV_sith": ("heavy", None),
    # --- JDS_Separatists ---
    "JDSCIS_Pistoeka_Sotage_Droid": ("astromech-labour", "sabotage/utility droid, judged labour"),
    "JDSCIS_B1_Battle_Droid":      ("battle", None),
    "JDSCIS_B1_Security_Droid":    ("battle", None),
    "JDSCIS_B1_Commander_Droid":   ("battle", None),
    "JDSCIS_BX_Commando_Droid":    ("battle", None),
    "JDSCIS_IG-100_MagnaGuards":   ("heavy", "consistent with OuterRim_MagnaGuardDroid = heavy"),
    "JDSCIS_T1_Tactical_Droid":    ("heavy", "consistent with OuterRim_TacticalDroid = heavy"),
    "JDSCIS_ST_Super_Tactical_Droid": ("heavy", None),
    "JDSCIS_B2_Super_Battle_Droid": ("heavy", "consistent with OuterRim_SuperBattleDroid = heavy"),
    "JDSCIS_B2_HA_Super_Battle_Droid": ("heavy", "'HA' heavy-assault variant of B2"),
    "JDSCIS_AQ_Battle_Droid":      ("battle", None),
    "JDSCIS_Droideka_Droid":       ("battle", "consistent with OuterRim_DestroyerDroid (droideka) = battle"),
    "JDSCIS_Droideka_Sharpshooter_Droid": ("battle", None),
    "JDSCIS_Demolition_Droid":     ("heavy", "ordnance/armor judged heavier than a standard battle chassis"),
    "JDSCIS_DSD1_Dwarf_Spider_Droid": ("heavy", "large walker chassis"),
    "JDSCIS_LR-57_Combat_Droid":   ("battle", "explicitly a combat droid"),
}


class Report(object):
    def __init__(self):
        self.notes = []
        self.warns = []
        self.skips = []

    def note(self, msg):
        self.notes.append(msg)
        print("NOTE  " + msg)

    def warn(self, msg):
        self.warns.append(msg)
        print("WARN  " + msg)

    def skip(self, what, why):
        self.skips.append((what, why))
        print("SKIP  %s: %s" % (what, why))


R = Report()


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def strip_parenthetical(s):
    """'stem (from PawnKindDef bodyGraphicData, drawSize 1.7)' -> 'stem'"""
    if s is None:
        return None
    return re.split(r"\s*\(", s, maxsplit=1)[0].strip() or None


def first_token(s):
    if not s:
        return None
    parts = s.split()
    return parts[0] if parts else None


# --------------------------------------------------------------- textures --
def _write_transparent_png(path, size=64):
    if os.path.exists(path):
        return
    w = h = size

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)  # 8-bit RGBA, no interlace
    row = b"\x00" + b"\x00\x00\x00\x00" * w
    raw = row * h
    idat = zlib.compress(raw, 9)
    png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)


def ensure_blank_head_texture():
    for rot in ("south", "north", "east"):
        _write_transparent_png(os.path.join(TEX_ROOT, "DW", "blank_%s.png" % rot))
    R.note("DW/blank_{south,north,east}.png: generated transparent stub head "
           "(64x64 RGBA, fully alpha-0) — technical rendering stub, not art")


def tex_exists(rel_stem, rotation):
    for ext in (".png", ".jpg", ".jpeg"):
        p = os.path.join(TEX_ROOT, rel_stem + "_" + rotation + ext)
        if os.path.isfile(p):
            return True
    return False


def verify_stem(candidates):
    """First candidate stem with at least one rotation file on disk, else None."""
    for c in candidates:
        if c is None:
            continue
        c = c.replace("\\", "/")
        for rot in ("south", "east", "north"):
            if tex_exists(c, rot):
                return c
    return None


def find_stem_in_folder(folder_rel):
    """List folder_rel under TEX_ROOT, return 'folder_rel/STEM' if exactly one
    '*_south.png' stem is present, else None."""
    folder_abs = os.path.join(TEX_ROOT, folder_rel)
    if not os.path.isdir(folder_abs):
        return None
    stems = set()
    for n in os.listdir(folder_abs):
        low = n.lower()
        for suf in ("_south.png", "_south.jpg", "_south.jpeg"):
            if low.endswith(suf):
                stems.add(n[: -len(suf)])
    if len(stems) == 1:
        return folder_rel.rstrip("/") + "/" + next(iter(stems))
    return None


# ------------------------------------------------------------ color parse --
def parse_rgba_weight(s):
    if not s:
        return None
    m = RGBA_RE.match(s.strip())
    if not m:
        return None
    r, g, b, a, w = (int(x) for x in m.groups())
    return [((r, g, b, a), w)]


def parse_rgb_pairs(pairs, key):
    """OuterRim skinColorPairs: list of {colorOne,colorTwo,weight,comment}."""
    out = []
    for p in pairs:
        s = p.get(key)
        w = p.get("weight", 100)
        if not s:
            continue
        m = RGB_TUPLE_RE.search(s)
        if not m:
            continue
        r, g, b = (int(x) for x in m.groups())
        out.append(((r, g, b, 255), int(w)))
    return out or None


# ----------------------------------------------------------- field resolve
def resolve_field(races_by_orig, orig, getter, seen=None):
    seen = seen if seen is not None else set()
    if orig in seen or orig not in races_by_orig:
        return None
    seen.add(orig)
    r = races_by_orig[orig]
    v = getter(r)
    if v is not None:
        return v
    parent = r.get("parentName")
    if parent and parent in races_by_orig:
        return resolve_field(races_by_orig, parent, getter, seen)
    return None


# ------------------------------------------------------------------ XML ---
def render_color_gen(slot, entries):
    lines = ['              <%s Class="ColorGenerator_Options">' % slot,
             "                <options>"]
    for (r, g, b, a), w in entries:
        lines.append("                  <li>")
        lines.append("                    <weight>%d</weight>" % w)
        lines.append("                    <only>RGBA(%d,%d,%d,%d)</only>" % (r, g, b, a))
        lines.append("                  </li>")
    lines.append("                </options>")
    lines.append("              </%s>" % slot)
    return "\n".join(lines)


def render_headtype(dn, path):
    return ("  <HeadTypeDef>\n"
            "    <defName>%s</defName>\n"
            "    <graphicPath>%s</graphicPath>\n"
            "    <gender>None</gender>\n"
            "  </HeadTypeDef>" % (dn, esc(path)))


def render_race(rd):
    p = []
    p.append('  <AlienRace.ThingDef_AlienRace ParentName="%s">' % rd["family_dn"])
    p.append("    <defName>%s</defName>" % rd["dn"])
    p.append("    <label>%s</label>" % esc(rd["label"]))
    p.append("    <description>%s</description>" % esc(rd["description"]))
    # bodySize/healthScale are only emitted here when they DIFFER from the
    # family abstract's default (DROIDWORKS_FAMILY_LAYER_1: "models override
    # only where the source race genuinely differed" — computed in main() by
    # comparing against the per-family mode, never averaged away silently).
    if rd["bodySize"] is not None or rd["healthScale"] is not None:
        p.append("    <race>")
        if rd["bodySize"] is not None:
            p.append("      <baseBodySize>%s</baseBodySize>" % rd["bodySize"])
        if rd["healthScale"] is not None:
            p.append("      <baseHealthScale>%s</baseHealthScale>" % rd["healthScale"])
        p.append("    </race>")
    if rd["moveSpeed"] is not None:
        p.append("    <statBases>")
        p.append("      <MoveSpeed>%s</MoveSpeed>" % rd["moveSpeed"])
        p.append("    </statBases>")
    p.append("    <alienRace>")
    p.append("      <graphicPaths>")
    p.append("        <skinShader>%s</skinShader>" % esc(rd["shaderType"]))
    if rd["body_stem"]:
        p.append("        <body>")
        p.append("          <path>%s</path>" % esc(rd["body_stem"]))
        p.append("        </body>")
    if rd["head_stem"]:
        p.append("        <head>")
        p.append("          <path>%s</path>" % esc(rd["head_stem"]))
        p.append("        </head>")
    p.append("      </graphicPaths>")
    p.append("      <generalSettings>")
    p.append("        <alienPartGenerator>")
    p.append('          <headTypes Inherit="False">')
    p.append("            <li>%s</li>" % rd["head_defname"])
    p.append("          </headTypes>")
    p.append('          <bodyTypes Inherit="False">')
    for bt in rd["bodyTypes"]:
        p.append("            <li>%s</li>" % esc(bt))
    p.append("          </bodyTypes>")
    if rd.get("customDrawSize"):
        p.append("          <customDrawSize>%s</customDrawSize>" % esc(rd["customDrawSize"]))
    if rd.get("colorChannels"):
        first, second = rd["colorChannels"]
        p.append('          <colorChannels Inherit="False">')
        p.append("            <li>")
        p.append("              <name>skin</name>")
        p.append(render_color_gen("first", first))
        if second:
            p.append(render_color_gen("second", second))
        p.append("            </li>")
        p.append("          </colorChannels>")
    p.append("        </alienPartGenerator>")
    p.append("      </generalSettings>")
    p.append("    </alienRace>")
    # DroidworksExtension (powerFallPerDay/energyDensity/chassisClass) moved
    # DOWN onto the family abstract (DROIDWORKS_FAMILY_LAYER_1) — every race
    # in a family shares identical tuning by construction (the family split
    # IS the tuning boundary), so there is never a per-race override to keep.
    comps_lines = rd.get("comps_lines")
    if comps_lines:
        p.append("    <comps>")
        p.extend(comps_lines)
        p.append("    </comps>")
    p.append("  </AlienRace.ThingDef_AlienRace>")
    return "\n".join(p)


def render_family_base(family_key, body_default, health_default):
    power_fall, energy_density, class_int = FAMILY_TUNING[family_key]
    p = []
    p.append('  <AlienRace.ThingDef_AlienRace Name="%s" ParentName="DW_Race_Base" Abstract="True">'
              % family_dn(family_key))
    if body_default is not None or health_default is not None:
        p.append("    <race>")
        if body_default is not None:
            p.append("      <baseBodySize>%s</baseBodySize>" % body_default)
        if health_default is not None:
            p.append("      <baseHealthScale>%s</baseHealthScale>" % health_default)
        p.append("    </race>")
    p.append("    <modExtensions>")
    # Same stale-namespace bug as DETONATION_COMP_LI above - real namespace is
    # RimMandrake.StarWars.Droidworks (DroidworksModExtension.cs:3). The
    # COMMITTED Races_Families.xml already had the correct string (someone
    # hand-fixed it after a prior regen, or fixed it and never re-ran this);
    # this generator would have reverted it back to broken the next time
    # anyone regenerated for an unrelated reason. Caught by diffing this run
    # against HEAD rather than trusting a clean exit code.
    p.append('      <li Class="RimMandrake.StarWars.Droidworks.DroidworksExtension">')
    p.append("        <powerFallPerDay>%s</powerFallPerDay>" % power_fall)
    p.append("        <energyDensity>%s</energyDensity>" % energy_density)
    p.append("        <chassisClass>%d</chassisClass>" % class_int)
    p.append("      </li>")
    p.append("    </modExtensions>")
    p.append("  </AlienRace.ThingDef_AlienRace>")
    return "\n".join(p)


def render_kind(kd):
    p = []
    p.append("  <PawnKindDef>")
    p.append("    <defName>%s</defName>" % kd["dn"])
    p.append("    <label>%s</label>" % esc(kd["label"]))
    p.append("    <race>%s</race>" % kd["race_dn"])
    p.append("    <combatPower>%s</combatPower>" % kd["combatPower"])
    if kd.get("apparelTags"):
        p.append("    <apparelTags>")
        for t in kd["apparelTags"]:
            p.append("      <li>%s</li>" % esc(t))
        p.append("    </apparelTags>")
    if kd.get("weaponTags"):
        p.append("    <weaponTags>")
        for t in kd["weaponTags"]:
            p.append("      <li>%s</li>" % esc(t))
        p.append("    </weaponTags>")
    # DROIDWORKS_FLESHTYPE_NEEDS_GAP_1 (2026-08-30): a droid has no business
    # getting a random human xenotype at spawn. XenotypeSet has a CUSTOM
    # loader (XenotypeChance.LoadDataFromXmlCustom) -- the field is
    # xenotypeChances and each entry's TAG NAME is read as the xenotype
    # defName itself (xmlRoot.Name), with the chance as the node's own text.
    # A naive <li><xenotype>..</xenotype><chance>..</chance></li> shape is
    # the <li>-in-a-custom-loader trap (rimworld-custom-loader-li-trap) and
    # would silently discard the whole PawnKindDef, not just misparse this
    # field.
    p.append("    <xenotypeSet>")
    p.append("      <xenotypeChances>")
    p.append("        <Baseliner>1</Baseliner>")
    p.append("      </xenotypeChances>")
    p.append("    </xenotypeSet>")
    p.append("  </PawnKindDef>")
    return "\n".join(p)


def write_defs(path, header, race_blocks, headtype_blocks, kind_blocks):
    body = []
    if headtype_blocks:
        body.extend(headtype_blocks)
        body.append("")
    if race_blocks:
        body.extend(race_blocks)
        body.append("")
    if kind_blocks:
        body.extend(kind_blocks)
    fh = ["<?xml version=\"1.0\" encoding=\"utf-8\"?>",
          "<!-- %s" % header,
          "     GENERATED by src/RimStarWars/Droidworks/Source/gen_droidworks_defs.py.",
          "     Do not hand-edit; re-run the generator. -->",
          "<Defs>", ""]
    fh.extend(body)
    fh.append("</Defs>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(fh) + "\n")


# ------------------------------------------------------------------ main --
def label_for_race(race, kinds_by_race_orig):
    lbl = race.get("label")
    if lbl:
        return lbl, None
    # JDS races carry no label of their own; borrow the paired kind's label
    # (same defName for JDS 1:1) rather than mechanically mangling defName.
    k = kinds_by_race_orig.get(race["defName"])
    if k and k.get("label"):
        return k["label"], "label borrowed from paired PawnKindDef (JDS races carry none of their own)"
    return race["defName"], "no label anywhere in extraction; defName used verbatim"


def resolve_graphics(race, races_by_orig):
    orig = race["defName"]
    mod = race["mod"]
    prefix = NS_PREFIX.get(mod, "")

    def g(key):
        return lambda r: r.get("graphics", {}).get(key)

    if mod in ("OuterRimDroidDepot", "OuterRimGalacticEmpire"):
        body_path = resolve_field(races_by_orig, orig, g("bodyPath"))
        tex_path = resolve_field(races_by_orig, orig, g("texPath"))
        shader = resolve_field(races_by_orig, orig, g("shaderType")) or "Cutout"
        head_wl = resolve_field(races_by_orig, orig, g("headTypeWhitelist"))
        body_wl = resolve_field(races_by_orig, orig, g("bodyTypeWhitelist")) or ["Male"]

        body_stem = None
        head_stem = None
        if body_path:
            body_stem = find_stem_in_folder(body_path)
            if body_stem is None:
                R.warn("%s: bodyPath folder %s has no single *_south.png stem — body texPath left unset" % (orig, body_path))
            else:
                head_folder = body_path.replace("/Body/", "/Head/").replace("/Body", "/Head")
                if head_folder != body_path:
                    head_stem = find_stem_in_folder(head_folder)
        elif tex_path:
            stem = strip_parenthetical(tex_path)
            body_stem = verify_stem([stem])
            if body_stem is None:
                R.warn("%s: texPath %r does not resolve to any *_south/_east/_north.png under Textures/" % (orig, stem))
        else:
            # Sole known gap: OuterRim_AstromechDroid captured NEITHER bodyPath
            # nor texPath (extraction's own note: art lives on the paired kind,
            # which the kind schema doesn't carry either). Resolved here by
            # folder-name inference against the real Textures/OuterRim/Droid/
            # tree and VERIFIED on disk before use — not a blind guess.
            guess = "OuterRim/Droid/Astromech/R2"
            if verify_stem([guess]):
                body_stem = guess
                R.note("%s: extraction captured no body texture path at all (art lives on the paired kind, "
                       "not on this race); inferred %s from the Textures/OuterRim/Droid folder tree and "
                       "verified *_south.png exists" % (orig, guess))
            else:
                R.warn("%s: no body texture path in extraction and no folder-name inference verified — body texPath left unset" % orig)

        return {
            "shaderType": shader,
            "bodyTypes": body_wl,
            "body_stem": body_stem,
            "head_stem": head_stem,
            "colorChannels": None,  # filled by caller from skinColorPairs
            "customDrawSize": None,
        }

    if mod == "KotORDroids":
        body_path = resolve_field(races_by_orig, orig, g("body_path"))
        head_path = resolve_field(races_by_orig, orig, g("head_path"))
        shader = resolve_field(races_by_orig, orig, g("skinShader")) or "Cutout"
        head_types = resolve_field(races_by_orig, orig, g("headTypes"))
        draw_size = resolve_field(races_by_orig, orig, g("customDrawSize"))

        body_stem = None
        if body_path:
            cand = strip_parenthetical(body_path)
            body_stem = verify_stem([prefix + cand, cand])
            if body_stem is None:
                R.warn("%s: body_path %r (mod %s) does not resolve under Textures/ with prefix %r" % (orig, cand, mod, prefix))

        head_stem = None
        if head_path and not BLANK_HEAD_RE.match(head_path.strip()):
            cand = strip_parenthetical(head_path)
            head_stem = verify_stem([prefix + cand, cand])
            if head_stem is None:
                R.warn("%s: head_path %r does not resolve under Textures/ with prefix %r — treated as headless" % (orig, cand, prefix))

        return {
            "shaderType": shader,
            "bodyTypes": resolve_field(races_by_orig, orig, g("bodyTypes")) or ["Male"],
            "body_stem": body_stem,
            "head_stem": head_stem,
            "colorChannels": None,
            "customDrawSize": draw_size,
        }

    if mod == "JDS_Separatists":
        tex_path = race.get("graphics", {}).get("texPath")
        body_stem = None
        if tex_path:
            cand = strip_parenthetical(tex_path)
            body_stem = verify_stem([prefix + cand, cand])
            if body_stem is None:
                R.warn("%s: texPath %r does not resolve under Textures/JDS/" % (orig, cand))
        return {
            "shaderType": "Cutout",
            "bodyTypes": ["Male"],
            "body_stem": body_stem,
            "head_stem": None,  # JDS: single fused sprite, no head layer captured
            "colorChannels": None,
            "customDrawSize": None,
        }

    raise RuntimeError("unhandled mod/framework %r for %s" % (mod, orig))


def build_color_channels(race, mod):
    if mod in ("OuterRimDroidDepot", "OuterRimGalacticEmpire"):
        pairs = race.get("graphics", {}).get("skinColorPairs")
        if not pairs:
            return None
        first = parse_rgb_pairs(pairs, "colorOne")
        second = parse_rgb_pairs(pairs, "colorTwo")
        if not first:
            return None
        return (first, second)
    if mod == "KotORDroids":
        g = race.get("graphics", {})
        first = parse_rgba_weight(g.get("colorChannels_skin_first"))
        second_raw = g.get("colorChannels_skin_second")
        second = parse_rgba_weight(second_raw)
        if second_raw and second is None:
            R.note("%s: colorChannels_skin_second %r is unstructured prose, not a single RGBA/weight pair — second channel omitted" % (race["defName"], second_raw[:60]))
        if not first:
            return None
        return (first, second)
    return None


_PARENTNAME_RE = re.compile(r"ParentName=(\w+)")


def label_for_kind(kind, kinds_by_defname):
    """-> (label, note-or-None).

    extraction.json sometimes captures a literal note like
    "(inherits HK-51 unit label)" as a kind's own `label` field, when the
    source PawnKindDef declares no <label> of its own and inherits one via
    ParentName in the donor mod. Emitting that note VERBATIM (as happened
    before this fix, KotORMIBColonist_HK51AD) puts extraction bookkeeping
    text on screen as the droid's actual in-game name. Resolved by reading
    the ParentName out of the kind's own `notes` field and borrowing that
    parent kind's real label — never guessed, and never left as a literal
    parenthetical note.
    """
    lbl = kind.get("label")
    if lbl and not lbl.strip().startswith("("):
        return lbl, None
    m = _PARENTNAME_RE.search(kind.get("notes") or "")
    if m and m.group(1) in kinds_by_defname:
        parent = kinds_by_defname[m.group(1)]
        parent_label = parent.get("label")
        if parent_label and not parent_label.strip().startswith("("):
            return parent_label, ("label resolved from ParentName=%s (extraction captured a "
                                   "placeholder note, not real text: %r)" % (m.group(1), lbl))
    return kind["defName"], "label unresolved (%r) — defName used verbatim" % lbl


def parse_kind_gear(kind):
    """-> (apparelTags-or-None, weaponTags-or-None, note-or-None)."""
    dn = kind["defName"]
    apparel = kind.get("apparelTags")
    weapon = kind.get("weaponTags")
    gear = kind.get("gear_or_weapons")
    combo = kind.get("apparelTags_or_gear")

    if isinstance(gear, dict) and gear.get("mechanism") == "weaponTags":
        wl = gear.get("weaponTags") or []
        if wl:
            return None, wl, None
        return None, None, "weaponTags explicitly empty (gear/weapons: %r) — no ranged weapon by design, not a data gap" % gear

    if isinstance(apparel, list) or isinstance(weapon, list):
        a = apparel if isinstance(apparel, list) else None
        w = weapon if isinstance(weapon, list) else None
        if not a and not w:
            return None, None, "apparelTags/weaponTags both explicitly empty lists — no gear by design"
        return (a or None), (w or None), None

    if isinstance(combo, str):
        m = re.search(r"apparelTags(?:\s+OVERRIDDEN)?:\s*([^;]+)", combo)
        if m:
            tags = [t.strip() for t in m.group(1).split(",") if t.strip()]
            extra = ""
            if "apparelRequired" in combo:
                extra = " (this kind's extraction also names explicit apparelRequired defNames from KotORWeapons/KotORDroids — NOT carried forward, those mods are not a Droidworks dependency and re-emitting a parsed-out defName is exactly the guess this project avoids)"
            return tags, None, ("apparelTags parsed from free-text extraction field%s" % extra) if extra else None
        return None, None, "apparelTags_or_gear has no parseable 'apparelTags:' segment (%r) — kind uses race-level apparelList only, not a gap" % combo[:60]

    if isinstance(apparel, str) or isinstance(weapon, str):
        reason = apparel if isinstance(apparel, str) else weapon
        return None, None, "apparelTags/weaponTags UNCERTAIN in extraction (%r) — marked UNARMED, not guessed" % reason[:80]

    return None, None, "no gear field of any recognised shape on this kind — marked UNARMED"


def main():
    with open(EXTRACTION_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    races = data["races"]
    kinds = data["kinds"]
    races_by_orig = {r["defName"]: r for r in races}
    kinds_by_race_orig = {k["defName"]: k for k in kinds}  # JDS: race==defName

    print("=== Droidworks def generator: %d races, %d kinds in extraction.json ===" % (len(races), len(kinds)))

    jawa_kinds = [k for k in kinds if "jawa" in json.dumps(k).lower()]
    if len(jawa_kinds) == 4:
        R.note("found exactly 4 Jawa_Droid_* kinds as the brief expects — wiring Jawa_FreeDroidEnclaves onto them")
    else:
        R.note("brief says '4 Jawa_Droid_* kinds keep Jawa_FreeDroidEnclaves' but extraction.json has %d kind entries "
               "mentioning 'jawa' anywhere at all — no kind defName, label or field matches that description. "
               "Per the item's own fallback, NO kind gets a faction assignment in this run; every DW_ PawnKindDef "
               "is generated with faction unset. This needs a BENCH decision, not a generator guess." % len(jawa_kinds))

    ensure_blank_head_texture()

    if not os.path.isfile(os.path.join(DEFS_ROOT, "Races_Base.xml")):
        R.warn("Defs/Races_Base.xml is missing — DW_Race_Base and RSW_DW_HeadType_Blank will not resolve. Create it before shipping.")

    # ---------------------------------------------------------- races ----
    race_out = {"OuterRim": [], "KotOR": [], "JDS": []}
    headtype_out = {"OuterRim": [], "KotOR": [], "JDS": []}
    race_dn = {}          # orig -> DW_Race_<orig>
    chassis_counts = {}

    family_for_mod = {
        "OuterRimDroidDepot": "OuterRim", "OuterRimGalacticEmpire": "OuterRim",
        "KotORDroids": "KotOR", "JDS_Separatists": "JDS",
    }

    all_defnames = []

    # Pass 1: resolve every race's data (unchanged from the pre-family-layer
    # logic) WITHOUT rendering yet — DROIDWORKS_FAMILY_LAYER_1 needs the full
    # per-family population of bodySize/healthScale values before it can
    # decide which values are common enough to move onto the family abstract.
    resolved = []
    for race in races:
        orig = race["defName"]
        mod = race["mod"]
        src_family = family_for_mod.get(mod)
        if src_family is None:
            R.skip(orig, "unrecognised source mod %r" % mod)
            continue

        bucket, cnote = CHASSIS_PLAN.get(orig, (None, None))
        if bucket is None:
            R.skip(orig, "no chassis classification in CHASSIS_PLAN — cannot attach DroidworksExtension, hard stop for this race")
            continue
        chassis_family = family_for(orig, bucket)
        chassis_counts[bucket] = chassis_counts.get(bucket, 0) + 1
        if cnote:
            R.note("chassis %s -> %s (family %s): %s" % (orig, bucket, chassis_family, cnote))

        bodySize = resolve_field(races_by_orig, orig, lambda r: r.get("bodySize"))
        healthScale = resolve_field(races_by_orig, orig, lambda r: r.get("baseHealthScale"))
        moveSpeed = resolve_field(races_by_orig, orig, lambda r: r.get("moveSpeed"))
        if healthScale is None and mod == "JDS_Separatists":
            # Verified, not guessed: read the abstract parent directly
            # (workshop 3276499495, 1.6/Defs/ThingDefs_Race.xml) — JDSSWCIS_Droids
            # declares baseBodySize=0.7 but no baseHealthScale at all, for any
            # of these 8 races. RimWorld's own ThingDef default (1f) is the
            # genuine effective value, not a filled-in guess.
            healthScale = 1.0
            R.note("%s: baseHealthScale not declared anywhere (checked the abstract JDSSWCIS_Droids "
                   "parent directly in workshop 3276499495) — using RimWorld's own engine default 1.0" % orig)
        if bodySize is None or healthScale is None:
            R.skip(orig, "bodySize/baseHealthScale unresolved even after walking parentName — hard stop, not guessed")
            continue

        label, lnote = label_for_race(race, kinds_by_race_orig)
        if lnote:
            R.note("%s: %s" % (orig, lnote))

        gfx = resolve_graphics(race, races_by_orig)
        colors = build_color_channels(race, mod)

        # 🔴 FIXED, DROIDWORKS_GENERATOR_NAMING_DRIFT_1 (2026-09-02): these three
        # "DW_..." builds (here, the kind dn below) never carried the RSW_
        # prefix the committed output actually uses. Root cause found via git
        # log: commit aa759446 "Rename Phase 2a: text migration - 4904
        # defName... replacements" rewrote every ALREADY-COMMITTED defName
        # literal across the repo for the naming-scheme migration, but a
        # generator that BUILDS a defName by string concatenation has no
        # defName literal for a text-replace pass to find - so the source
        # code silently fell out of sync with its own already-migrated
        # output. A regen before this fix would have silently renamed every
        # race/kind/custom-headtype defName back to the pre-scheme form.
        dn = "RSW_DW_Race_" + orig
        race_dn[orig] = dn
        all_defnames.append(dn)

        head_defname = "RSW_DW_HeadType_Blank"
        headtype_block = None
        if gfx["head_stem"]:
            head_defname = "RSW_DW_HeadType_" + orig
            headtype_block = render_headtype(head_defname, gfx["head_stem"])
            all_defnames.append(head_defname)
        if headtype_block:
            headtype_out[src_family].append(headtype_block)

        if gfx["body_stem"] is None:
            R.warn("%s: emitted WITHOUT a resolved body texPath — will render with HAR's default/missing-texture body" % orig)

        resolved.append({
            "orig": orig, "src_family": src_family, "chassis_family": chassis_family,
            "dn": dn,
            "label": label,
            "description": "A DW-unified %s. Absorbed from %s (%s)." % (label, mod, orig),
            "bodySize": bodySize,
            "healthScale": healthScale,
            "moveSpeed": moveSpeed,
            "shaderType": gfx["shaderType"],
            "bodyTypes": gfx["bodyTypes"],
            "body_stem": gfx["body_stem"],
            "head_stem": gfx["head_stem"],
            "head_defname": head_defname,
            "colorChannels": colors,
            "customDrawSize": gfx.get("customDrawSize"),
        })

    # Per-family mode for bodySize/healthScale — a "genuinely common" value
    # needs at least 2 members sharing it (n=1 or all-distinct means no real
    # majority, so nothing is moved and every race keeps its explicit value,
    # unchanged from pre-family-layer behaviour: never averaged, never a
    # singleton picked arbitrarily). MoveSpeed is deliberately EXCLUDED from
    # this dedup: many races carry no MoveSpeed override at all today (fall
    # through to Human's engine default via DW_Race_Base) — moving a family
    # default onto MoveSpeed would silently change THEIR effective speed too,
    # not just the races that genuinely share a value. Left per-race, as-is.
    from collections import Counter

    def family_mode(field):
        by_fam = {}
        for r in resolved:
            by_fam.setdefault(r["chassis_family"], []).append(r[field])
        modes = {}
        for fam, vals in by_fam.items():
            c = Counter(vals)
            val, count = c.most_common(1)[0]
            modes[fam] = val if count >= 2 else None
        return modes

    body_defaults = family_mode("bodySize")
    health_defaults = family_mode("healthScale")

    family_blocks = []
    override_counts = {}
    for fam in sorted(FAMILY_TUNING):
        family_blocks.append(render_family_base(fam, body_defaults.get(fam), health_defaults.get(fam)))

    # Pass 2: render, now that each race knows whether its bodySize/
    # healthScale matches its family's default (omit -> inherit) or not
    # (keep an explicit override — every kept override is counted/printed
    # below, per the ruling's "list every override the generator keeps").
    for r in resolved:
        fam = r["chassis_family"]
        body_override = r["bodySize"] if r["bodySize"] != body_defaults.get(fam) else None
        health_override = r["healthScale"] if r["healthScale"] != health_defaults.get(fam) else None
        if body_override is not None:
            override_counts["bodySize/" + fam] = override_counts.get("bodySize/" + fam, 0) + 1
        if health_override is not None:
            override_counts["healthScale/" + fam] = override_counts.get("healthScale/" + fam, 0) + 1

        rd = dict(r)
        rd["bodySize"] = body_override
        rd["healthScale"] = health_override
        rd["family_dn"] = family_dn(fam)
        if r["orig"] in COMPS_OVERRIDE:
            rd["comps_lines"] = COMPS_OVERRIDE[r["orig"]]
        elif FAMILY_TUNING[fam][1] > 0:
            rd["comps_lines"] = DETONATION_ROLLOUT_COMP
        else:
            rd["comps_lines"] = None

        race_out[r["src_family"]].append(render_race(rd))

    # ---------------------------------------------------------- kinds ----
    kind_out = {"OuterRim": [], "KotOR": [], "JDS": []}
    kind_defnames = []
    unarmed = []
    for kind in kinds:
        orig = kind["defName"]
        dn = "RSW_DW_" + orig  # DROIDWORKS_GENERATOR_NAMING_DRIFT_1, see the race dn comment above
        mod = kind["mod"]
        family = family_for_mod.get(mod)
        if family is None:
            R.skip(orig, "unrecognised kind mod %r" % mod)
            continue

        race_ref = first_token(kind.get("race"))
        if race_ref is None or race_ref not in race_dn:
            R.skip(orig, "race pointer %r does not resolve to a generated DW_Race_* — hard stop" % kind.get("race"))
            continue

        combat_power = kind.get("combatPower")
        if combat_power is None:
            R.skip(orig, "no combatPower in extraction — hard stop, required field")
            continue

        apparel, weapon, gnote = parse_kind_gear(kind)
        if gnote:
            R.note("%s gear: %s" % (orig, gnote))
        if apparel is None and weapon is None:
            unarmed.append(orig)

        label, lnote = label_for_kind(kind, kinds_by_race_orig)
        if lnote:
            R.note("%s: %s" % (orig, lnote))

        kind_defnames.append(dn)
        kd = {
            "dn": dn,
            "label": label,
            "race_dn": race_dn[race_ref],
            "combatPower": combat_power,
            "apparelTags": apparel,
            "weaponTags": weapon,
        }
        kind_out[family].append(render_kind(kd))

    # -------------------------------------------------------- write out --
    write_defs(
        os.path.join(DEFS_ROOT, "Races_Families.xml"),
        "Droidworks chassis-family abstracts (DROIDWORKS_FAMILY_LAYER_1) — "
        "DW_Race_Base -> DW_Family_<Name> -> concrete DW_Race_<orig>.",
        family_blocks, [], [])
    for family in ("OuterRim", "KotOR", "JDS"):
        if race_out[family] or headtype_out[family]:
            write_defs(
                os.path.join(DEFS_ROOT, "Races_%s.xml" % family),
                "Droidworks races absorbed from %s." % family,
                race_out[family], headtype_out[family], [])
        if kind_out[family]:
            write_defs(
                os.path.join(DEFS_ROOT, "PawnKinds_%s.xml" % family),
                "Droidworks pawn kinds absorbed from %s." % family,
                [], [], kind_out[family])

    # ---------------------------------------------------------- report ---
    dup = set(x for x in all_defnames if all_defnames.count(x) > 1)
    family_defnames = [family_dn(f) for f in FAMILY_TUNING]
    all_defnames_full = (all_defnames + kind_defnames + family_defnames +
                          ["DW_Race_Base", "RSW_DW_HeadType_Blank"])
    seen = set()
    dupes = set()
    for x in all_defnames_full:
        if x in seen:
            dupes.add(x)
        seen.add(x)
    if dupes:
        R.warn("defName collisions across generated output: %s" % sorted(dupes))
    else:
        print("defName uniqueness: PASS — %d distinct defNames (%d races + %d headtypes + %d kinds + %d family abstracts + 2 base)"
              % (len(all_defnames_full), len(race_dn),
                 len(all_defnames) - len(race_dn), len(kind_defnames), len(family_defnames)))

    print("\n=== chassis classification counts (bucket) ===")
    for b in sorted(chassis_counts):
        print("  %-18s %d" % (b, chassis_counts[b]))
    print("\n=== family abstracts (7) ===")
    fam_race_counts = {}
    for r in resolved:
        fam_race_counts[r["chassis_family"]] = fam_race_counts.get(r["chassis_family"], 0) + 1
    for fam in sorted(FAMILY_TUNING):
        pf, ed, ci = FAMILY_TUNING[fam]
        print("  %-20s %2d races  powerFallPerDay=%s energyDensity=%s chassisClass=%d  "
              "bodySize default=%s  healthScale default=%s"
              % (family_dn(fam), fam_race_counts.get(fam, 0), pf, ed, ci,
                 body_defaults.get(fam), health_defaults.get(fam)))
    print("\n=== per-race overrides kept (value differs from family default) ===")
    for k in sorted(override_counts):
        print("  %-24s %d" % (k, override_counts[k]))
    print("\n=== summary ===")
    print("races emitted: %d / %d source" % (len(race_dn), len(races)))
    print("kinds emitted: %d / %d source" % (len(kind_defnames), len(kinds)))
    print("kinds UNARMED (no apparel/weapon tags carried): %d -> %s" % (len(unarmed), unarmed))
    print("notes: %d, warnings: %d, skips: %d" % (len(R.notes), len(R.warns), len(R.skips)))


if __name__ == "__main__":
    main()
