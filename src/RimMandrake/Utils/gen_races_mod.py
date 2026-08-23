#!/usr/bin/env python3
"""Build RimMandrake_StarWarsRaces: a standalone mod that OWNS the Star Wars
species, so Star Wars Xenotypes, Outer Rim Galactic Diversity and BTD Xenotype
REMIX can all be switched off.

The three donor mods collide with each other and BTD ships a Harmony patch whose
only job is to delete the duplicates. Owning the composition removes the
collision at its root. What must be true when this finishes: with all three
donors OFF, every species still resolves and renders -- so every def and every
texture they reach is either copied into our namespace or belongs to a mod we
declare a dependency on.

WHAT IS COPIED           Star Wars Xenotypes + Outer Rim Galactic Diversity only:
                         genes, head types, textures, the name-maker rule packs
                         AND the word lists they read, and the sixteen Galactic
                         Diversity species pawn kinds our factions field.
WHAT IS DEPENDED ON      Biotech, Core, VEF, Outland Genetics, Integrated Genes,
                         LFS Eyes, Big and Small. Their genes are generic and stay
                         where they are.

Also repoints src/Jawa/Jawa_Patches at the copies: verify() fails if any def
there still reaches a departing mod, including through a ParentName, which is a
silent discard rather than an error.

Re-runnable. Reads the live def dump for the species table and the donor mods'
own XML on disk for the def bodies, so the copies are the authors' text rather
than a reconstruction from runtime fields.

  python3 src/RimMandrake/Utils/gen_races_mod.py [--no-textures]
"""
import io
import json
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dump_manifest import dump_db          # noqa: E402
from game_paths import DEF_DUMP, WORKSHOP  # noqa: E402

DUMP = DEF_DUMP
WS = WORKSHOP
BTD = WS + "/3458153185"
OUT = os.path.join(REPO, "src/Jawa/RimMandrake_StarWarsRaces")

# donor tag -> (mod root, texture roots in search order)
#
# Outer Rim's LoadFolders sends 1.6 at `Common`, which holds only an
# AssetBundle; its 1,000+ loose PNGs sit in `Common_Old`, which only <=1.5
# loads. Copying from Common_Old is deliberate and is half the reason this mod
# exists -- as loose files under our own path they load again.
DONORS = {
    "SWX": dict(root=WS + "/2915192253",
                tex=[WS + "/2915192253/Textures"],
                packageId="guy762.starwarsxenotypes",
                prefix="guy762_"),
    "OR": dict(root=WS + "/2980427615",
               tex=[WS + "/2980427615/Common_Old/Textures"],
               packageId="neronix17.outerrim.galacticdiversity",
               prefix="OuterRim_"),
}
DONOR_PIDS = {d["packageId"] for d in DONORS.values()}

PREFIX = "RimMandrake_"
TEXNS = "RimMandrakeSW"          # our texture path namespace
STRNS = "RimMandrakeSWNames"     # our Languages/English/Strings namespace
SPECIES_PREFIX = "RimMandrake"   # xenotype defNames: RimMandrakeTwilek

# A RulePackDef's Rule_File entries name a plain text word list under some
# active mod's `Languages/<lang>/Strings`. Copying the RulePackDef without the
# word lists gives a namer that resolves and produces nothing.
LANG = {
    "SWX": WS + "/2915192253/Languages/English/Strings",
    "OR": WS + "/2980427615/1.6/Mods/ChissXenotype/Languages/English/Strings",
}

# Free-text blocks inside a RulePackDef. A bare word in one is grammar, not a
# def reference and not a texture path, and renaming it corrupts the grammar.
RAWTEXT_TAGS = ("rulesStrings", "rulesFiles", "keyword")

# Outer Rim - Galactic Diversity pawn kinds our FactionDefs field directly.
# Only Galactic Diversity's: the Droid Depot, Galactic Empire, Core, Separatist
# Droid Army and VFE Pirates kinds our factions also name belong to mods that
# stay installed.
RESCUE_KINDS = [
    "OuterRim_Aqualish", "OuterRim_Arkanian", "OuterRim_ArkanianTribal",
    "OuterRim_Geonosian", "OuterRim_GeonosianTribal", "OuterRim_Herglic",
    "OuterRim_Jawa", "OuterRim_JawaTribal", "OuterRim_Kaminoan",
    "OuterRim_MonCalamari", "OuterRim_Nikto", "OuterRim_NiktoTribal",
    "OuterRim_Quarren", "OuterRim_QuarrenTribal", "OuterRim_Wookiee",
    "OuterRim_WookieeTribal",
]
# Their two abstract parents. A ParentName that resolves to nothing is a SILENT
# discard, so these travel and are renamed with them.
RESCUE_KIND_PARENTS = {"OuterRimTestColonyPawnKind": PREFIX + "ColonyPawnKind",
                       "OuterRimTestTribalPawnKind": PREFIX + "TribalPawnKind"}
# Owner ruling 2026-08-14: MandrakeJawa is the ONLY active Jawa xenotype. The
# rescued Jawa kinds roll it, not the BTD-derived RimMandrakeJawa the equivalence
# table would otherwise hand them.
RESCUE_XENOTYPE_OVERRIDE = {"OuterRim_Jawa": "MandrakeJawa"}

# Owner ruling 2026-08-15. Miraluka is not built. It was also the only def in
# the set whose geneClass lived in a donor assembly (OuterRimDiversity.
# Gene_NoEyes), so dropping it leaves this mod with no compiled code at all.
DROP_SPECIES = {"Miraluka"}

# The Jawa move out of Jawa_Patches. Left side is the old defName, right side
# is what the moved def is called here. The gene XML files are hand-moved; this
# map only exists so generated gene lists point at the new names.
JAWA_GENES = {
    "Jawa_Gene_Skittish": PREFIX + "Jawa_Skittish",
    "Jawa_Eyes_HugeOrange": PREFIX + "Jawa_Eyes_HugeOrange",
    "Jawa_Eyes_HugeAmber": PREFIX + "Jawa_Eyes_HugeAmber",
    "Jawa_Head_Plain": PREFIX + "Jawa_Head_Plain",
}

# modExtension classes whose assembly LEAVES with the donor. A def carrying one
# logs "Could not find type named ..." once the donor is off, so the node is
# dropped from the copy. Cosmetic in both cases.
DROP_EXT_CLASSES = {"EyeOffsetSouth.ModExtension_EyeOffsetSouth"}

DEPENDENCIES = [
    ("Ludeon.RimWorld.Biotech", "Biotech", ""),
    ("OskarPotocki.VanillaFactionsExpanded.Core", "Vanilla Expanded Framework",
     "https://steamcommunity.com/sharedfiles/filedetails/?id=2023507013"),
    ("Neronix17.Outland.Genetics", "Outland - Genetics",
     "https://steamcommunity.com/sharedfiles/filedetails/?id=2600618060"),
    ("Turnovus.Biotech.IntegratedGenes", "Integrated Genes",
     "https://steamcommunity.com/sharedfiles/filedetails/?id=2891845502"),
]
# Reached only by a handful of genes or mod extensions, but reached: declared as
# loadAfter so our defs land on top of theirs, without forcing an install.
SOFT_AFTER = [
    "Ludeon.RimWorld",
    "RedMattis.BetterPrerequisites",
    "RedMattis.BigSmall.Core",
    "LazyFridayStudio.GenesExpandedEyes",
    "Neronix17.Toolbox",
    # one DamageDef modExtension, guy762_Ionization.ModExtension_HediffGiver,
    # is compiled into KotOR Core -- not into either donor.
    "guy762.MM.KotORCore",
    "guy762.starwarsxenotypes",
    "neronix17.outerrim.galacticdiversity",
    "btd.xenotyperemix.starwars",
]

# 🔴 THE COPIER IS DRIVEN FROM THESE TWO LISTS. `copy_textures` is fed by
# `texhits`, which only `rewrite` populates -- so a field missing here is not
# merely a path left pointing at a donor, it is art that was NEVER COPIED. The
# symptom is a magenta box, and it appears only once the donor is switched off,
# which is the entire scenario this mod exists for. Adding a field here is
# therefore also the fix for the missing art behind it.
TEXFIELDS = ("texPath", "graphicPath", "iconPath", "path", "uiIconPath",
             "maskPath", "bodyNakedGraphicPath", "bodyDessicatedGraphicPath",
             "headDessicatedGraphicPath", "skullGraphicPath",
             # Added 2026-08-15 (B66/D-CHK2). Gendered and gene-icon fields --
             # `texPathFemale` is why female Chagrians went magenta while males
             # rendered, which reads as intermittent rather than as a missing field.
             "texPathFemale", "backgroundPathEndogenes", "backgroundPathXenogenes")
# Children of these are walked and rewritten. The walk takes EVERY child, not
# just `<li>` -- which is what lets `headPaths` work, whose children are the
# named tags `<Male>` and `<Female>` rather than a list.
TEXCONTAINERS = ("texPaths", "graphicPaths", "bodyTypeGraphicPaths",
                 # Added 2026-08-15 (B66/D-CHK2): `headPaths` (Male/Female --
                 # the Gand and Selkath heads) and `texturePaths` (<li> list --
                 # the Gand's mask_yuun, inside BigAndSmall.GraphicSetDef).
                 "headPaths", "texturePaths")
SUFFIXES = ("", "_north", "_south", "_east", "_west", "_side",
            "_m", "_northm", "_southm", "_eastm", "_westm")


# ---------------------------------------------------------------- utilities

def comment_safe(lines):
    """`--` is illegal INSIDE an XML comment and kills the WHOLE file at load,
    not just the comment. The `<!--` and `-->` delimiters are exempt, and so is
    a rule made of dashes."""
    out = []
    for ln in lines:
        s = ln.strip()
        if s in ("<!--", "-->") or set(s) <= set("-= "):
            out.append(ln)
            continue
        while "--" in ln:
            ln = ln.replace("--", "—", 1)
        out.append(ln)
    return out


def assert_comment_safe(path):
    """Guard, not a habit. Runs over every file we write."""
    t = io.open(path, encoding="utf-8").read()
    for m in re.finditer(r"<!--(.*?)-->", t, re.S):
        if "--" in m.group(1):
            raise SystemExit("ILLEGAL `--` inside an XML comment: %s" % path)
    if "<!--" in t.split("-->")[-1]:
        raise SystemExit("unterminated XML comment: %s" % path)


def write_xml(path, header_lines, elements, keep_existing=True):
    """Write a Defs file. 🔑 NEVER SUBTRACT, unless the caller says otherwise.

    ⭐ OWNER'S RULING 2026-08-23: this generator may ADD, it may never SUBTRACT.
    MEASURED that day, on a rebuild whose species count matched perfectly: SW_Genes
    lost **17** defs — `RimMandrake_DevaronianHorns`, `RimMandrake_GeonosianHead`,
    `RimMandrake_Eyes_HugeRed` among them — while gaining 42. The losses are
    APPEARANCE genes the shipped xenotypes still name, so dropping them is a
    cross-reference error and a species losing its face. The gains are inert if
    nothing references them.

    ⇒ Any def already in the file that this run did not produce is CARRIED. The
    asymmetry is deliberate: an unreferenced def costs nothing, a missing one costs
    a face.

    ⚠️ IT RATCHETS. A file only ever grows this way, and a genuinely dead def now
    needs deleting by hand. That is the trade, taken knowingly: the failure it
    prevents is silent and the cost it imposes is visible.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    root = ET.Element("Defs")
    for e in elements:
        root.append(e)
    if keep_existing and os.path.exists(path):
        try:
            old_root = ET.parse(path).getroot()
        except ET.ParseError:
            old_root = None
        if old_root is not None:
            # 🪤 ABSTRACT PARENTS HAVE NO defName — they are keyed by a Name= ATTRIBUTE.
            # Keying this carry on defName alone silently skipped every abstract, and an
            # abstract that vanishes takes its CHILDREN with it: a ParentName that
            # resolves to nothing is a SILENT DISCARD in RimWorld, so the def simply does
            # not exist in game. MEASURED 2026-08-23 — three defs died exactly this way
            # (RimMandrake_GunganEars on RimMandrake_GeneEarsBase, two head types on
            # RimMandrake_HeavyBoneBase) and the only reason it was caught is that the
            # offline validator resolves ParentName.
            def _key(e):
                return e.findtext("defName") or e.get("Name")
            have = {_key(e) for e in root}
            carried = [e for e in old_root if _key(e) and _key(e) not in have]
            if carried:
                print("  %s: carried %d existing def(s) this run did not rebuild"
                      % (os.path.basename(path), len(carried)), file=sys.stderr)
                for e in carried:
                    root.append(e)
            root[:] = sorted(root, key=lambda e: _key(e) or "")
    ET.indent(root, space="  ")
    body = ET.tostring(root, encoding="unicode")
    head = comment_safe(['<?xml version="1.0" encoding="utf-8"?>', "<!--"]
                        + ["  " + l for l in header_lines] + ["-->"])
    io.open(path, "w", encoding="utf-8").write("\n".join(head) + "\n" + body + "\n")
    assert_comment_safe(path)


# ---------------------------------------------------------------- loading

def load_dump():
    def j(n):
        return json.load(io.open(DUMP + "/defs/" + n, encoding="utf-8"))["defs"]
    x = {d["defName"]: d for d in j("XenotypeDef.json")}
    g = {d["defName"]: d for d in j("GeneDef.json")}
    return x, g


def donor_xml_files(root):
    """1.6 load folders only: the mod root and `1.6`. AdditionalMods folders are
    conditional on other mods and are not ours to copy."""
    skip = ("1.4", "1.5", "About", "Languages", "Source", "Assemblies",
            "Common", "Common_Old", "Textures", "Sounds", "BTD_Data")
    out = []
    for dp, dn, fn in os.walk(root):
        rel = os.path.relpath(dp, root).replace("\\", "/")
        if rel.split("/")[0] in skip or "AdditionalMods" in rel:
            continue
        out += [os.path.join(dp, f) for f in fn if f.endswith(".xml")]
    return sorted(set(out))


def index_donors():
    """defName -> (donorTag, element); Name= -> (donorTag, element).

    PawnKindDefs are held apart. Outer Rim names a xenotype and a pawn kind the
    same thing (`OuterRim_Wookiee` is both), and a single defName-keyed index
    silently keeps whichever file was walked last."""
    defs, absts, kinds = {}, {}, {}
    for tag, cfg in DONORS.items():
        for fp in donor_xml_files(cfg["root"]):
            try:
                r = ET.parse(fp).getroot()
            except ET.ParseError:
                continue
            if r.tag != "Defs":
                continue
            for el in r:
                if not isinstance(el.tag, str):
                    continue
                dn = el.findtext("defName")
                if el.tag == "PawnKindDef":
                    if dn:
                        kinds[dn] = (tag, el)
                    if el.get("Name"):
                        kinds["@" + el.get("Name")] = (tag, el)
                    continue
                if dn:
                    defs[dn] = (tag, el)
                if el.get("Name"):
                    absts[el.get("Name")] = (tag, el)
    return defs, absts, kinds


def index_strings():
    """donorTag -> {relative path without .txt (lowercased) -> abs file}."""
    idx = {}
    for tag, root in LANG.items():
        m = {}
        for dp, dn, fn in os.walk(root):
            for f in fn:
                if f.lower().endswith(".txt"):
                    rel = os.path.relpath(os.path.join(dp, f), root)
                    m[rel.replace("\\", "/")[:-4].lower()] = \
                        os.path.join(dp, f)
        idx[tag] = m
    return idx


def rawtext_ids(el):
    """ids of every node inside a RulePackDef's free-text blocks."""
    out = set()
    for parent in el.iter():
        if parent.tag in RAWTEXT_TAGS:
            for d in parent.iter():
                out.add(id(d))
    return out


def index_textures():
    """donorTag -> {relative path without .png (lowercased) -> abs file}."""
    idx = {}
    for tag, cfg in DONORS.items():
        m = {}
        for r in cfg["tex"]:
            for dp, dn, fn in os.walk(r):
                for f in fn:
                    if f.lower().endswith(".png"):
                        rel = os.path.relpath(os.path.join(dp, f), r)
                        m[rel.replace("\\", "/")[:-4].lower()] = \
                            os.path.join(dp, f)
        idx[tag] = m
    return idx


# ---------------------------------------------------------------- species

def species_table(x, donor_defs=None):
    """The roster: every species the donors define, however they are named.

    🔴 THE SECOND LOOP USED TO READ ONLY THE DUMP, AND THAT IS A ONE-WAY LEAK.
    A dump captured with the donors switched off does not contain their
    xenotypes, so every BTD-only species that is not in BTD's own equivalencies
    table simply vanished from the roster — and because the roster is what
    `pick_species` iterates, the generator would then REFUSE TO WRITE rather
    than ship a shrunken mod. Measured 2026-08-19: five species were being lost
    exactly this way (Anzati, Muun, Ortolan, SithZ, Togorian), and the refusal
    they caused is what had blocked D-CHK2's regenerate since 2026-08-15.

    ⇒ Read the donors' XML ON DISK, the same fallback `_gene_exists` already
    has. The dump stays as a secondary source so a species is picked up whether
    the donors are on or off. This permanently removes the dependency on
    donor-mods-active-at-dump-time.
    """
    rows = {}
    root = ET.parse(BTD + "/BTD_Data/XenotypeEquivalencies.xml").getroot()
    for grp in root.findall("EquivalentGroup"):
        rows[grp.findtext("Species")] = (grp.findtext("BTD"),
                                         grp.findtext("SWX"),
                                         grp.findtext("OR"))
    names = list(x)
    if donor_defs:
        names += [n for n, v in donor_defs.items()
                  if v[1].tag == "XenotypeDef" and n not in x]
    for n in names:
        if n.startswith("BTD_") and not any(n == v[0] for v in rows.values()):
            rows.setdefault(n[4:], (n, None, None))
    return rows


def clean_name(species):
    return SPECIES_PREFIX + re.sub(r"[^A-Za-z0-9]", "", species)


def _genes_of(el):
    """Gene list straight off a donor's XML element."""
    node = el.find("genes")
    return [li.text.strip() for li in node] if node is not None else []


def _forces_head(gene, g, donor_defs=None):
    """Does this gene force a head type?

    Checks the dump AND the donors' XML, because neither alone is complete:
    once a donor is switched off its genes vanish from the dump, and a gene
    from a mod we keep is not in the donor XML."""
    f = (g.get(gene) or {}).get("fields") or {}
    if f.get("forcedHeadTypes"):
        return True
    if donor_defs and gene in donor_defs:
        el = donor_defs[gene][1]
        node = el.find("forcedHeadTypes")
        return node is not None and len(node) > 0
    return False


def _gene_exists(gene, g, donor_defs):
    """A gene is real if the live game has it OR a donor's XML defines it.

    🔴 The dump alone is not enough and the reason is subtle: this generator is
    normally re-run AFTER the donors have been switched off, at which point
    their genes are absent from the dump exactly as their xenotypes are. Judging
    'does this gene resolve' from that dump rejects every species the donors
    supplied -- which is the whole catalogue."""
    return gene in g or gene in donor_defs


def _is_donor_gene(gene, g, donor_defs):
    """Is this gene one the donors supply — judged the same way `_gene_exists`
    judges existence, and for the same reason.

    🔴 Added 2026-08-15. `main` used a bare `g[gene]["packageId"]`, which threw
    `KeyError: 'GS_Primitive'` and stopped the generator DEAD once the three
    donors left the mod list: their genes vanish from the dump, so the lookup
    misses entirely rather than returning a non-donor answer. That is the
    chicken-and-egg this whole mod exists to break — the tool that frees us from
    the donors must not itself require them to be loaded.

    Dump first (it is authoritative about attribution when present), then the
    donors' own XML on disk, which survives being switched off."""
    if gene in g:
        return g[gene].get("packageId") in DONOR_PIDS
    return gene in donor_defs


def _is_specific(gene, species):
    """A head gene named for the species beats a generic one.

    `guy762_Head_rodian` gives a Rodian its snoot; `Outland_ScaleSkin` gives it
    a generic reptile head and renders a scaly human. Both force a head, so a
    count of head-forcing genes cannot tell them apart -- the NAME can."""
    key = re.sub(r"[^a-z]", "", species.lower())
    return bool(key) and key in re.sub(r"[^a-z]", "", gene.lower())



def _fields_from_xml(el):
    """The dump's `fields` shape, rebuilt from a donor's XML element.

    🔴 THE SAME ONE-WAY LEAK AS `species_table`, one field set later. `pick_species`
    was given a read-the-donors'-XML fallback for GENES on 2026-08-19, but the
    species' METADATA — description, iconPath, inheritable, canGenerateAsCombatant,
    combatPowerFactor — kept coming from the dump alone. A donor xenotype that is on
    disk but absent from the dump (BTD's Harmony patch deletes the SWX and Outer Rim
    duplicates at load, so most of them are) therefore built with EMPTY metadata:
    blank description, blank icon, `inheritable false`, `canGenerateAsCombatant
    false`. MEASURED 2026-08-23 on Abednedo — `OuterRim_Abednedo` is in the donor XML
    and not in the dump, and regenerating blanked all four.

    Half a fallback is worse than none: it looks like it works.
    """
    def t(tag, default=None):
        v = el.findtext(tag)
        return default if v is None else v
    f = {}
    for tag in ("label", "description", "iconPath", "nameMaker", "nameMakerFemale"):
        v = el.findtext(tag)
        if v is not None:
            f[tag] = v
    for tag in ("inheritable", "canGenerateAsCombatant"):
        v = el.findtext(tag)
        if v is not None:
            f[tag] = (v.strip().lower() == "true")
    for tag in ("combatPowerFactor", "chanceToUseNameMaker"):
        v = el.findtext(tag)
        if v is not None:
            try:
                f[tag] = float(v)
            except ValueError:
                pass
    return f


def pick_species(x, g, donor_defs):
    """Compose each species from the DONORS' XML ON DISK, unioning head genes.

    🔴 THIS USED TO READ THE LIVE DEF DUMP AND WAS STRUCTURALLY BLIND.
    The preference order was BTD, then SWX, then Outer Rim -- but the dump was
    captured with BTD ACTIVE, and BTD's Harmony patch DELETES the SWX and Outer
    Rim duplicates at load. Those two candidates were already absent from the
    dump, so the fallback could never fire and every species came from BTD.
    BTD's lists carry head-BONE genes without the head-TYPE genes the other
    donors have, so ten species rendered with plain human heads and others got
    a generic reptile head instead of their own.

    ⇒ Choosing between three donors by reading a post-dedup dump cannot work.
    Read the XML on disk, where all three still exist whatever the load order
    did to them.
    """
    built, skipped, stripped = [], [], []
    for species, cand in sorted(species_table(x, donor_defs).items()):
        if species in DROP_SPECIES:
            skipped.append((species, "dropped by owner ruling"))
            continue
        # every donor's version of this species, from DISK
        versions = [(c, donor_defs[c][1]) for c in cand if c and c in donor_defs]
        if not versions:
            skipped.append((species, "no donor XML defines it"))
            continue
        src, base_el = versions[0]
        glist = list(_genes_of(base_el))
        # union the head genes the base is missing
        extra = []
        for name, el in versions[1:]:
            for n in _genes_of(el):
                if (n not in glist
                        and _forces_head(n, g, donor_defs)
                        and _is_specific(n, species)):
                    extra.append(n)
        if extra:
            # a species-specific head wins; drop generic head-forcers so two
            # genes are not fighting over the same head slot
            glist = [n for n in glist
                     if not (_forces_head(n, g, donor_defs)
                             and not _is_specific(n, species))]
            glist += [n for n in extra if n not in glist]
        if not glist:
            skipped.append((species, "source carries no genes"))
            continue
        missing = [n for n in glist if not _gene_exists(n, g, donor_defs)]
        if missing:
            # 🔴 OWNER'S RULING 2026-08-15: "Remove any genes from our implementation
            # of the xenotypes that aren't supported in our mod at this time. We will
            # investigate what to do later."
            # ⇒ A SPECIES IS NEVER DROPPED FOR A GENE. This used to `continue`, which
            # cost six species to four genes — three Force genes that exist in NO donor
            # tree (so no re-dump could ever surface them) and one that lives in a path
            # `donor_xml_files` deliberately skips. Stripping was measured safe before it
            # was written: no species empties and not one loses its head-forcing gene.
            glist = [n for n in glist if n not in missing]
            stripped.append((species, missing))
            if not glist:
                skipped.append((species, "every gene unresolvable: %s" % missing[:3]))
                continue
        # dump first, donor XML second - see _fields_from_xml for why both are needed
        _f = (x.get(src) or {}).get("fields", {}) or _fields_from_xml(base_el)
        built.append(dict(species=species, src=src, f=_f,
                          genes=glist, headless=not [n for n in glist if _forces_head(n, g, donor_defs)]))
    if stripped:
        print("== genes STRIPPED (owner's ruling: never drop a species for a gene)")
        for sp, ms in sorted(stripped):
            print("  %-14s %s" % (sp, ", ".join(ms)))
    return built, skipped


# ---------------------------------------------------------------- closure

def closure(seeds, defs, absts):
    """Everything donor-owned that the seed defs can reach, plus the abstract
    parents they inherit from. A ParentName that resolves to nothing is a SILENT
    discard, so an abstract that is used must travel with the def."""
    seen, abstract = set(), set()
    queue = [("d", n) for n in seeds]
    while queue:
        kind, n = queue.pop()
        if kind == "d":
            if n in seen or n not in defs:
                continue
            seen.add(n)
            el = defs[n][1]
        else:
            if n in abstract or n not in absts:
                continue
            abstract.add(n)
            el = absts[n][1]
        raw = rawtext_ids(el)
        for sub in [el] + list(el.iter()):
            pn = sub.get("ParentName")
            if pn and pn in absts:
                queue.append(("a", pn))
            if id(sub) in raw:
                continue
            t = (sub.text or "").strip()
            if t and re.fullmatch(r"[A-Za-z0-9_.]+", t) and t in defs:
                queue.append(("d", t))
    return seen, abstract


def rename_map(names):
    """Strip the donor prefix so the result carries no trace of it -- otherwise
    a grep for `guy762_` can never come back clean and stops being a check."""
    out, taken = {}, {}
    for n in sorted(names):
        base = n
        for cfg in DONORS.values():
            if base.startswith(cfg["prefix"]):
                base = base[len(cfg["prefix"]):]
                break
        new = PREFIX + base
        if new in taken:
            new = PREFIX + n.replace(".", "_")
        taken[new] = n
        out[n] = new
    return out


# ---------------------------------------------------------------- rewriting

def resolve_tex(path, texidx, home):
    """Which donor owns this texture path, if any. A path that resolves nowhere
    in the donors belongs to Core or Biotech and MUST be left alone."""
    order = [home] + [t for t in DONORS if t != home]
    for tag in order:
        m = texidx[tag]
        low = path.lower()
        if any(low + s in m for s in SUFFIXES):
            return tag
        if any(k.startswith(low + "/") for k in m):     # Graphic_Random dir
            return tag
    return None


def rewrite(el, defmap, absmap, texidx, home, texhits,
            stridx=None, strhits=None):
    """Rename every reference in place. A reference left pointing at a donor
    name still resolves TODAY and breaks silently the moment the donor is
    switched off, which is the entire point of this mod."""
    for parent in list(el.iter()):
        for child in list(parent):
            cls = child.get("Class")
            if cls in DROP_EXT_CLASSES:
                parent.remove(child)
    raw = rawtext_ids(el)
    # Rule_File word lists. Claimed here, before the texture pass, because
    # `path` is also a texture field name and the two must not be confused.
    rulefiles = set()
    if stridx is not None:
        for li in el.iter("li"):
            if li.get("Class") != "Rule_File":
                continue
            p = li.find("path")
            if p is None or not (p.text or "").strip():
                continue
            rulefiles.add(id(p))
            rel = p.text.strip()
            tag = home if rel.lower() in stridx.get(home, {}) else next(
                (t for t in stridx if rel.lower() in stridx[t]), None)
            if tag is None:
                continue
            strhits.add((tag, rel))
            p.text = "%s/%s/%s" % (STRNS, tag, rel)
    nm = el.get("Name")
    if nm in absmap:
        el.set("Name", absmap[nm])
    elif nm in defmap:
        el.set("Name", defmap[nm])
    for sub in [el] + list(el.iter()):
        pn = sub.get("ParentName")
        if pn in absmap:
            sub.set("ParentName", absmap[pn])
        elif pn in defmap:
            sub.set("ParentName", defmap[pn])
        if id(sub) in raw:
            continue
        if sub.tag in defmap:
            sub.tag = defmap[sub.tag]
        t = (sub.text or "").strip()
        if t in defmap:
            sub.text = defmap[t]
        elif t in JAWA_GENES:
            sub.text = JAWA_GENES[t]
    # exclusionTags are free strings, not defs, and the donors namespace theirs.
    # Renaming keeps the grep for a surviving donor prefix meaningful; every
    # user of these tags is in this mod, so mutual exclusion is unaffected.
    for sub in [el] + list(el.iter()):
        if sub.tag not in ("exclusionTags", "styleTags", "styleItemTags"):
            continue
        for c in list(sub) + [sub]:
            t = (c.text or "").strip()
            for cfg in DONORS.values():
                if t.startswith(cfg["prefix"]):
                    c.text = PREFIX + t[len(cfg["prefix"]):]
    # texture paths
    def do_path(node):
        p = (node.text or "").strip()
        if not p:
            return
        tag = resolve_tex(p, texidx, home)
        if tag:
            node.text = "%s/%s/%s" % (TEXNS, tag, p)
            texhits.add((tag, p))
    for sub in [el] + list(el.iter()):
        if id(sub) in rulefiles or id(sub) in raw:
            continue
        if sub.tag in TEXFIELDS:
            do_path(sub)
        elif sub.tag in TEXCONTAINERS:
            for c in sub:
                do_path(c)
    return el


def copy_strings(strhits, stridx):
    """Always copied, even under --no-textures: a few hundred KB of word lists
    is not what that flag exists to skip, and verify() checks them."""
    n = 0
    for tag, rel in sorted(strhits):
        src = stridx[tag].get(rel.lower())
        if not src:
            continue
        dst = os.path.join(OUT, "Languages/English/Strings", STRNS, tag,
                           rel + ".txt")
        n += 1
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
    return n


def apply_overrides(bytype, texhits):
    """Edits we own that used to be PatchOperations against a donor def. Now
    that the def IS ours the patch has nowhere to apply, so the change is made
    at the source.

    The Jawa xenotype rolls between three big-eye colours. Two are authored here
    with the glow sprite; the third is the copied donor gene, whose flat art
    would make one roll in three look painted on rather than lit.
    """
    for e in bytype.get("GeneDef", []):
        if e.findtext("defName") != PREFIX + "Eyes_HugeYellow":
            continue
        for li in e.findall("renderNodeProperties/li"):
            li.find("texPath").text = TEXNS + "/Jawa/jawaeyes_glow"
            if li.find("shaderTypeDef") is None:
                ET.SubElement(li, "shaderTypeDef").text = "MoteGlow"
            ds = li.find("drawSize")
            if ds is not None:
                ds.text = "0.16"
        return True
    return False


def copy_textures(texhits, texidx, dry=False):
    """Every directional variant, not just the base name -- a body or head that
    ships only `_south` here renders from nothing in three of four facings."""
    n_files = 0
    for tag, p in sorted(texhits):
        m = texidx[tag]
        low = p.lower()
        srcs = [m[low + s] for s in SUFFIXES if low + s in m]
        srcs += [v for k, v in m.items() if k.startswith(low + "/")]
        if not srcs:
            for other in DONORS:
                mm = texidx[other]
                srcs = [mm[low + s] for s in SUFFIXES if low + s in mm]
                srcs += [v for k, v in mm.items() if k.startswith(low + "/")]
                if srcs:
                    break
        for s in srcs:
            base = next(r for cfg in DONORS.values() for r in cfg["tex"]
                        if s.startswith(r))
            rel = os.path.relpath(s, base).replace("\\", "/")
            dst = os.path.join(OUT, "Textures", TEXNS, tag, rel)
            n_files += 1
            if dry:
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.isfile(dst) or \
                    os.path.getsize(dst) != os.path.getsize(s):
                shutil.copyfile(s, dst)
    return n_files


# ---------------------------------------------------------------- emitters

ABOUT = """<?xml version="1.0" encoding="utf-8"?>
<ModMetaData>
  <packageId>mandrake.starwarsraces</packageId>
  <name>RimMandrake - Star Wars Races</name>
  <author>mandrake</author>
  <supportedVersions>
    <li>1.6</li>
  </supportedVersions>
  <description>{DESC}</description>
  <modDependencies>
{DEPS}  </modDependencies>
  <loadAfter>
{AFTER}  </loadAfter>
</ModMetaData>
"""

DESC = """{N} Star Wars species, owned outright, so the three colliding xenotype mods can be switched off.

Star Wars Xenotypes, Outer Rim - Galactic Diversity and [BTD] Xenotype REMIX each ship an overlapping set of the same species. They collide, and BTD carries a Harmony assembly whose only job is to delete the duplicates and keep its own. This mod ends that by owning the composition: the species, their genes, their head types and their art live here, and none of the three donors needs to be installed.

CREDIT. The art and the gene design are not ours.
- Star Wars Xenotypes, by guy762 - Workshop 2915192253. {SWX} genes and their textures are copied from it.
- Outer Rim - Galactic Diversity, by Neronix17 - Workshop 2980427615. {OR} genes, the head types and the species icons are copied from it. Its 1.6 release routes loading at a folder that no longer holds its loose art; the sprites here are recovered from the folder it left behind, which is why they render again.
- [BTD] Xenotype REMIX, by beeteedubs - Workshop 3458153185. The species reconciliation is its work. Its hand-curated equivalence table is what decides which donor supplies each species, and the gene lists are inherited from it.

Species NAMES come with them. 48 name-generating rule packs and the word lists they read are copied too - a rule pack without its Languages/English/Strings word lists resolves and produces nothing - so a Twi'lek is still named like a Twi'lek with every donor off. Four namers that Star Wars Xenotypes had commented out are wired back up here; they were disabled to avoid overriding forced names on another mod's hero pawnkinds, which reference that mod's xenotypes and not ours.

Outer Rim's sixteen species pawn kinds are copied as well, with both of their abstract parents, because a faction that fields them directly loses those raids and caravans outright when that mod leaves.

The MandrakeJawa xenotype and its four genes - skittish, hooded face, and the orange and amber big-eye colours with their glow sprite - are authored here rather than copied, and live in this mod because the Jawa are a species like any other.

Nothing generic was copied. Genes that belong to Biotech, Core, Outland Genetics, Integrated Genes, LFS Genes Expanded - Eyes and Big and Small remain theirs; those mods are dependencies and must stay installed.

Contains no compiled code."""


def write_about(n_species, n_swx, n_or):
    deps = ""
    for pid, name, url in DEPENDENCIES:
        deps += "    <li>\n      <packageId>%s</packageId>\n" % pid
        deps += "      <displayName>%s</displayName>\n" % name
        if url:
            deps += "      <steamWorkshopUrl>%s</steamWorkshopUrl>\n" % url
        deps += "    </li>\n"
    after = "".join("    <li>%s</li>\n" % p
                    for p in [d[0] for d in DEPENDENCIES] + SOFT_AFTER)
    # 🔑 Count what the mod SHIPS, not what this run rebuilt. Six species have no
    # donor and are carried verbatim (ORPHAN_XENOTYPES), so `n_species` is 63 and the
    # catalogue is 69 - and an About.xml advertising 63 is simply a false claim on the
    # mod page. Same rule as everywhere else here: the shipped artifact is the answer.
    desc = DESC.format(N=(_shipped_species_count() or n_species), SWX=n_swx, OR=n_or)
    desc = desc.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    p = os.path.join(OUT, "About/About.xml")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(
        ABOUT.format(DESC=desc, DEPS=deps, AFTER=after))
    assert_comment_safe(p)


RULE = "=" * 76


def header(title, body):
    return ([RULE, title, RULE, "",
             "GENERATED by src/RimMandrake/Utils/gen_races_mod.py. "
             "Do not hand-edit.", ""]
            + body.split("\n") + [RULE])


def namemaker_for(b, x, tbl, defmap):
    """(nameMaker, nameMakerFemale, chance) for one species, already renamed.

    First choice is whatever the donors put on this species, taken from any of
    the three candidate xenotypes -- the source we build the gene list from does
    not always carry the namer. Second choice is the namer whose name IS the
    species, which recovers the ones the donors left commented out: guy762
    disabled Twi'lek, Cathar, Echani and Miraluka because their namers fought
    the forced names on KotOR Weapons & Armor's hero pawnkinds. Those hero kinds
    reference guy762's xenotypes, not ours, so the conflict does not reach here
    and a Twi'lek gets a Twi'lek name."""
    for cand in tbl.get(b["species"], ()):
        if not cand or cand not in x:
            continue
        f = x[cand]["fields"]
        if f.get("nameMaker"):
            return (defmap.get(f["nameMaker"], f["nameMaker"]),
                    defmap.get(f.get("nameMakerFemale"),
                               f.get("nameMakerFemale")),
                    f.get("chanceToUseNameMaker"))
    bare = re.sub(r"[^A-Za-z0-9]", "", b["species"]).lower()
    for donor, ours in defmap.items():
        if donor.lower() == "kotor_namer" + bare:
            return ours, None, None
    return None, None, None


_SHIPPED_GENES = {}


def _shipped_kind_count():
    p = os.path.join(OUT, "Defs/PawnKindDefs/RimMandrakePawnKinds.xml")
    if not os.path.exists(p):
        return 0
    try:
        return len(ET.parse(p).getroot().findall("PawnKindDef"))
    except ET.ParseError:
        return 0


def _shipped_meta():
    """The per-species metadata the mod on disk ships, keyed by our defName.

    Same rule as `_shipped_gene_lists`, same reason: what is live and playtested
    wins over what today's donor resolution happens to produce. `description`,
    `iconPath`, `label`, `inheritable`, `canGenerateAsCombatant`,
    `combatPowerFactor` and the nameMaker fields all differed on a rebuild - in
    BOTH directions - because the donor a species resolves to now is not the one
    it was built from in August.
    """
    p = os.path.join(OUT, "Defs/XenotypeDefs/RimMandrakeXenotypes.xml")
    if not os.path.exists(p):
        return {}
    try:
        root = ET.parse(p).getroot()
    except ET.ParseError:
        return {}
    out = {}
    for xd in root.findall("XenotypeDef"):
        dn = xd.findtext("defName")
        if not dn:
            continue
        out[dn] = {c.tag: (c.text or "") for c in xd if c.tag != "genes"}
    return out


_SHIPPED_META = {}




def write_xenotypes(built, defmap, x, tbl):
    global _SHIPPED_GENES, _SHIPPED_META
    # Read the catalogue we currently ship BEFORE overwriting it. This IS the
    # never-subtract rule; without it the write below is the lossy one.
    # ⚠️ IT RATCHETS: this reads the file the last run WROTE, so one bad run
    # becomes the new floor. Always restore from git before testing a change here.
    _SHIPPED_GENES = _shipped_gene_lists()
    _SHIPPED_META = _shipped_meta()
    els = []
    unnamed = []
    for b in built:
        f = b["f"]
        e = ET.Element("XenotypeDef")
        _dn = clean_name(b["species"])
        _meta = _SHIPPED_META.get(_dn)
        if _meta:
            # ⭐ SHIPPED METADATA WINS, exactly as the gene list does. Rebuilt values
            # differed in BOTH directions on 2026-08-23 - blanked descriptions and
            # icons where the dump lacked the donor, and changed labels and
            # combatPowerFactors where it had a different one. What is live and
            # playtested is the answer; a regeneration is not the place to relitigate
            # 69 species' identities.
            for _t, _v in _meta.items():
                ET.SubElement(e, _t).text = _v
            gl = ET.SubElement(e, "genes")
            for gn in _SHIPPED_GENES.get(_dn, []):
                ET.SubElement(gl, "li").text = gn
            els.append(e)
            continue
        ET.SubElement(e, "defName").text = _dn
        ET.SubElement(e, "label").text = f.get("label") or b["species"]
        ET.SubElement(e, "description").text = f.get("description") or ""
        icon = f.get("iconPath") or ""
        ET.SubElement(e, "iconPath").text = icon
        ET.SubElement(e, "inheritable").text = \
            "true" if f.get("inheritable") else "false"
        ET.SubElement(e, "canGenerateAsCombatant").text = \
            "true" if f.get("canGenerateAsCombatant") else "false"
        # 0 keeps them out of the random-wanderer pool; our factions name the
        # species they field, which is the point of owning them.
        ET.SubElement(e, "factionlessGenerationWeight").text = "0"
        cpf = f.get("combatPowerFactor")
        if cpf and cpf != 1:
            ET.SubElement(e, "combatPowerFactor").text = str(cpf)
        nm, nmf, chance = namemaker_for(b, x, tbl, defmap)
        if nm:
            ET.SubElement(e, "nameMaker").text = nm
            if nmf:
                ET.SubElement(e, "nameMakerFemale").text = nmf
            if chance is not None and chance != 1:
                ET.SubElement(e, "chanceToUseNameMaker").text = str(chance)
        else:
            unnamed.append(b["species"])
        gl = ET.SubElement(e, "genes")
        # map first, then union with what we already ship — see _shipped_gene_lists.
        mapped = [defmap.get(gn, JAWA_GENES.get(gn, gn)) for gn in b["genes"]]
        keep = _SHIPPED_GENES.get(clean_name(b["species"]))
        if keep:
            # ⭐ THE SHIPPED LIST WINS OUTRIGHT. Not a union - measured 2026-08-23,
            # unioning ADDED 435 genes across the 69 species, because today's donor
            # resolution differs from August's. Nothing was lost, but a species
            # quietly gaining Aggression_Aggressive, a second skin colour or a
            # second head-forcer is an untested appearance and balance change to
            # every pawn in the mod - and it would arrive disguised as a no-op
            # regeneration. The shipped lists are the curated, playtested state.
            # ⇒ The generator preserves them verbatim and proposes nothing.
            # A genuinely new gene for a species is a deliberate edit, made here.
            names = list(keep)
        else:
            names = mapped
        for gn in names:
            ET.SubElement(gl, "li").text = gn
        els.append(e)
    # 🔑 The six species no donor defines. They are parsed from their verbatim XML
    # and merged into the SAME sorted order the rest come out in, so the file reads
    # as one catalogue rather than 63 plus an appendix. See ORPHAN_XENOTYPES for why
    # they cannot simply be built like the others.
    # ⛔ This is the step whose absence made the guard pass on a 63-species output.
    for _name, _xml in ORPHAN_XENOTYPES.items():
        els.append(ET.fromstring(_xml))
    els.sort(key=lambda el: el.findtext("defName") or "")
    # ⭐ THE GENE GUARD, against what is ACTUALLY ABOUT TO BE WRITTEN.
    # The never-subtract union should make loss impossible; this proves it rather
    # than assuming it. If it ever fires, the union broke - do not raise the
    # threshold to get a build out.
    _have_g = sum(len(e.find("genes").findall("li"))
                  for e in els if e.find("genes") is not None)
    _want_g = _shipped_gene_count()
    if _want_g and _have_g < _want_g:
        raise SystemExit(
            "REFUSING TO WRITE: %d gene entries about to be written against the %d "
            "the mod ships - %d would be LOST.\n"
            "The never-subtract union in _shipped_gene_lists should make this "
            "impossible, so if you are reading this it is broken. Fix the union; "
            "do NOT lower this number."
            % (_have_g, _want_g, _want_g - _have_g))

    write_xml(os.path.join(OUT, "Defs/XenotypeDefs/RimMandrakeXenotypes.xml"),
              header("RimMandrakeXenotypes.xml",
                     "One XenotypeDef per species. Gene lists are inherited from "
                     "the best\navailable donor so a pawn looks exactly as it did "
                     "before; every gene that\ncame from a departing mod has been "
                     "rewritten to our copy of it.\n\nnameMaker points at our copy "
                     "of the donor RulePackDef, whose word lists\nship under "
                     "Languages/English/Strings."),
              els)
    return unnamed


def write_rescued_kinds(kinds, tbl, built, texidx):
    """The Outer Rim - Galactic Diversity pawn kinds our FactionDefs field.

    Copied rather than depended on because Galactic Diversity is one of the
    three mods this whole exercise switches off. Their `xenotypeChances` keys
    are repointed at our species; the two abstract parents travel with them."""
    orname = {}
    for b in built:
        for cand in tbl.get(b["species"], ()):
            if cand:
                orname[cand] = clean_name(b["species"])
    # 🔴 THE ORPHANS BELONG IN THIS MAP TOO, and leaving them out was a HARD STOP.
    # `built` excludes the six species no donor can rebuild, but they ARE in our
    # output (ORPHAN_XENOTYPES) — so a rescued pawn kind pointing at, say,
    # OuterRim_Herglic had nothing to repoint to and line ~1065 raised SystemExit.
    # ⚠️ That exit is BEFORE copy_textures, so the whole texture pass never ran, and
    # THAT is why the 42 genes this generator adds had no art and failed validation
    # with 64 errors. The missing art was never the bug; an early exit was.
    for _sp in ORPHAN_XENOTYPES:
        for cand in tbl.get(_sp, ()):
            if cand and cand not in orname:
                orname[cand] = clean_name(_sp)
        orname.setdefault("OuterRim_" + _sp, clean_name(_sp))
    els, missing = [], []
    for name, new in sorted(RESCUE_KIND_PARENTS.items()):
        if "@" + name not in kinds:
            missing.append(name)
            continue
        c = ET.fromstring(ET.tostring(kinds["@" + name][1]))
        c.set("Name", new)
        c.set("Abstract", "True")
        els.append(c)
    for dn in RESCUE_KINDS:
        if dn not in kinds:
            missing.append(dn)
            continue
        c = ET.fromstring(ET.tostring(kinds[dn][1]))
        c.find("defName").text = PREFIX + dn.split("_", 1)[1]
        pn = c.get("ParentName")
        if pn in RESCUE_KIND_PARENTS:
            c.set("ParentName", RESCUE_KIND_PARENTS[pn])
        # DICTIONARY-KEYED by defName: the xenotype is the ELEMENT NAME.
        for chances in c.iter("xenotypeChances"):
            for k in chances:
                if k.tag in RESCUE_XENOTYPE_OVERRIDE:
                    k.tag = RESCUE_XENOTYPE_OVERRIDE[k.tag]
                elif k.tag in orname:
                    k.tag = orname[k.tag]
                elif k.tag.startswith("OuterRim_"):
                    missing.append("%s -> xenotype %s" % (dn, k.tag))
        els.append(c)
    if missing:
        raise SystemExit("rescued pawn kinds unresolved: %s" % missing)
    # ⛔ HAND-OWNED, like RimMandrakePawnKinds.xml, and for a reason write_xml cannot
    # catch. Its never-subtract rule works at DEF level: it carries whole defs a run
    # did not rebuild. This file's curation is at FIELD level — the Jawa robes and
    # hoods (e479d8ae) and the faction colours (9bb5a5bb) sit INSIDE defs the run DOES
    # rebuild, so regenerating keeps all 16 defNames and quietly strips the equipment.
    # MEASURED 2026-08-23: 16 -> 16 defs, 0 lost, and apparelRequired, apparelTags and
    # apparelColor gone from the Jawa kinds. "Nothing lost" at the def level is not
    # "nothing lost".
    # 🔑 Delete the file to force a fresh build.
    _rk = os.path.join(OUT, "Defs/PawnKindDefs/SW_RescuedKinds.xml")
    if os.path.exists(_rk):
        print("  RescuedKinds: preserved (hand-owned equipment the generator cannot "
              "derive). Delete the file to rebuild from scratch.", file=sys.stderr)
        return
    write_xml(_rk,
              header("SW_RescuedKinds.xml",
                     "Outer Rim Galactic Diversity's own species pawn kinds, "
                     "copied and renamed\nbecause our FactionDefs field them "
                     "directly and that mod is switched off.\nBoth abstract "
                     "parents travel with them: a ParentName that resolves to\n"
                     "nothing discards the child silently."),
              els)
    return els


def write_pawnkinds(built):
    els = []
    for b in built:
        dn = clean_name(b["species"])
        e = ET.Element("PawnKindDef", ParentName="BasePlayerPawnKind")
        ET.SubElement(e, "defName").text = dn + "_Kind"
        ET.SubElement(e, "label").text = b["f"].get("label") or b["species"]
        ET.SubElement(e, "defaultFactionDef").text = "PlayerColony"
        at = ET.SubElement(e, "apparelTags")
        ET.SubElement(at, "li").text = "IndustrialBasic"
        ET.SubElement(e, "apparelMoney").text = "350~600"
        # `BasePlayerPawnKind` does not supply this, and without it every one of
        # these kinds throws `initial resistance range is undefined for humanlike
        # pawn kind` at load -- 69 lines, three quarters of the stack's config
        # errors. It is also what a prisoner's recruitment resistance rolls from,
        # so leaving it unset breaks the capture path, not just the log.
        # `10~20` is vanilla's humanlike value. It is not a balance knob; do not
        # retune it here.
        ET.SubElement(e, "initialResistanceRange").text = "10~20"
        xs = ET.SubElement(e, "xenotypeSet")
        xc = ET.SubElement(xs, "xenotypeChances")
        # DICTIONARY-KEYED by defName. An <li> here silently discards the def.
        ET.SubElement(xc, dn).text = "1.0"
        els.append(e)
    # ⛔ THIS FILE IS HAND-OWNED AND THE GENERATOR MUST NOT REWRITE IT.
    # It carries three days of edits this generator cannot derive - robes and hoods
    # (e479d8ae), faction colours across 31 kinds (9bb5a5bb), and
    # initialResistanceRange on all 69 (this morning). A rebuild produces 63 kinds,
    # so running it DELETES SIX and silently reverts the rest; that happened on
    # 2026-08-23 and was recovered from git.
    # 🔑 The generator still OWNS the file - it creates it if it is missing - it just
    # does not overwrite a curated one. Delete the file to force a fresh build.
    _pk = os.path.join(OUT, "Defs/PawnKindDefs/RimMandrakePawnKinds.xml")
    if os.path.exists(_pk):
        print("  PawnKinds: preserved (hand-owned, %d kinds). Delete the file to "
              "rebuild from scratch." % _shipped_kind_count(), file=sys.stderr)
        return
    write_xml(_pk,
              header("RimMandrakePawnKinds.xml",
                     "One colonist-grade kind per species. A XenotypeDef cannot be "
                     "spawned on\nits own -- pawn generation takes a PawnKindDef -- "
                     "so without these the\nspecies cannot be verified in game."),
              els)


# ---------------------------------------------------------------- main


def _shipped_gene_lists():
    """Every gene list the mod ON DISK currently ships, keyed by our defName.

    ⭐ OWNER'S RULING 2026-08-23: **the generator may ADD, it may never SUBTRACT.**

    Measured that day: a clean rebuild came back 356 gene entries lighter than the
    catalogue on disk — 1073 against 1429 — dropping whole families (`Outland_*`
    skins, `Outland_EggLayer`, `Outland_ThickSkin`, `Outland_DeceleratedPregnancy`).
    ⇒ Not stale references. `neronix17.outland.genetics` is ACTIVE and every one of
    those genes resolves in the live def set. The rebuild was discarding valid
    appearance, because the donor a species resolves to today is not the donor it
    was built from in August.

    🔑 So our own previous output becomes the DONOR OF LAST RESORT. A gene this mod
    already ships, which still resolves, is kept — in the order it already has, so
    the file barely moves — and anything the current donors newly offer is appended.
    A pawn can gain an attribute from a regeneration; it can never silently lose its
    face.

    ⚠️ These names are ALREADY REWRITTEN to our copies (`defmap` was applied when
    they were written), so this must be unioned at WRITE time, after mapping — never
    into `pick_species`'s pre-map list, where every name would miss.
    """
    p = os.path.join(OUT, "Defs/XenotypeDefs/RimMandrakeXenotypes.xml")
    if not os.path.exists(p):
        return {}
    try:
        root = ET.parse(p).getroot()
    except ET.ParseError:
        return {}
    out = {}
    for xd in root.findall("XenotypeDef"):
        dn = xd.findtext("defName")
        gl = xd.find("genes")
        if dn and gl is not None:
            out[dn] = [li.text for li in gl.findall("li") if li.text]
    return out


def _shipped_species_count():
    """How many species the mod on disk currently ships. 0 if it is absent."""
    p = os.path.join(OUT, "Defs/XenotypeDefs/RimMandrakeXenotypes.xml")
    if not os.path.exists(p):
        return 0
    try:
        return len(ET.parse(p).getroot().findall("XenotypeDef"))
    except ET.ParseError:
        return 0


def _shipped_gene_count():
    """How many GENE entries the shipped xenotypes carry, in total.

    🔴 A COUNT OF SPECIES IS NOT A ROSTER, and this is the proof. On 2026-08-23 the
    species guard was satisfied — 69 in, 69 out — and the regeneration was STILL
    lossy: the shipped catalogue carries **1429** gene entries and the rebuild
    produced **1073**. 356 genes gone, whole families with them (every `Outland_*`
    skin, `Outland_EggLayer`, `Outland_DeceleratedPregnancy`, `Outland_ThickSkin`),
    because the donor a species resolves to today is not the donor it was built
    from in August.

    A species that survives with half its genes is exactly the silent loss the
    species guard exists to prevent, and counting species could never see it.
    """
    p = os.path.join(OUT, "Defs/XenotypeDefs/RimMandrakeXenotypes.xml")
    if not os.path.exists(p):
        return 0
    try:
        root = ET.parse(p).getroot()
    except ET.ParseError:
        return 0
    return sum(len(gl.findall("li"))
               for xd in root.findall("XenotypeDef")
               for gl in xd.findall("genes"))



# ============================================================================
# ORPHAN SPECIES — RACES_GENERATOR_DIVERGED_1, reconciled 2026-08-23
# ============================================================================
#
# 🔴 SIX SPECIES THIS GENERATOR CANNOT REBUILD, AND THE REFUSAL IT CAUSED.
#
# `_guard_species_regression` has refused every regeneration since 2026-08-15
# with "would ship 63 species, but the mod on disk has 69". Its stated cause —
# "the dump was captured with the donors switched off, so their xenotypes are
# absent" — is WRONG, and was repeated into two items and a commit before it
# was checked. MEASURED 2026-08-23: all three captures contain the guy762
# donor xenotypes and all report 578 mods. Re-taking the dump never would have
# lifted it.
#
# The real cause: **no donor defines these six at all.** They exist ONLY in
# RimMandrakeXenotypes.xml — the generator's own output. Searched all 97 donor
# XenotypeDefs on disk: zero hits, and zero near-matches for four of them.
# Anzati, Muun, Ortolan and Togorian have no source anywhere; Herglic's donor
# "carries no genes"; Miraluka was dropped by owner ruling and is correctly
# absent from disk.
#
#     63 built + these 6 = 69 = what the mod ships. The arithmetic closes.
#
# 🔑 THIS IS THE FROZEN-ARTIFACT FAILURE, exactly: a generated file quietly
# accumulated entries its generator can no longer derive, so regenerating would
# delete them for good and report success. The guard is what stopped that, and
# it was right every single time it fired. ⛔ DO NOT WEAKEN THE GUARD — it is
# satisfied here by making the six genuinely present, not by lowering the bar.
#
# Carried VERBATIM, gene lists and all, because there is nothing to derive them
# from.
#
# ⛔ THIS TABLE IS NOT YET WIRED INTO THE WRITER, so the generator STILL REFUSES
# and that is correct. Adding the table and making the guard count it - without
# emitting them - was tried on 2026-08-23 and silently shipped a 63-species mod
# over the live 69. Reverted from git. To finish this properly:
#   1. emit these six into Defs/XenotypeDefs/RimMandrakeXenotypes.xml,
#   2. work out what to do about `OuterRim_Herglic -> xenotype OuterRim_Herglic`,
#      which the rescued-pawnkind pass reports the moment the guard stops firing,
#   3. THEN diff a full regeneration against git and confirm the other 63 species,
#      the head types, the genes and the 69 pawn kinds all come back byte-identical.
# Step 3 is the whole job. Steps 1-2 are the easy part.
# ============================================================================

ORPHAN_XENOTYPES = {
 'Anzati': """  <XenotypeDef>
    <defName>RimMandrakeAnzati</defName>
    <label>Anzati</label>
    <description>Anzati were a long-lived humanoid species that hailed from the Mid Rim Territories planet of Anzat. They were feared and hated as they fed on the life force of other sentient species.</description>
    <iconPath>UI/Icons/Xenotypes/Sanguophage</iconPath>
    <inheritable>true</inheritable>
    <canGenerateAsCombatant>true</canGenerateAsCombatant>
    <factionlessGenerationWeight>0</factionlessGenerationWeight>
    <genes>
      <li>ArchiteMetabolism</li>
      <li>DiseaseFree</li>
      <li>PerfectImmunity</li>
      <li>TotalHealing</li>
      <li>RimMandrake_Beard_chintendril</li>
      <li>Hemogenic</li>
      <li>HemogenDrain</li>
      <li>Bloodfeeder</li>
      <li>Coagulate</li>
      <li>Deathrest</li>
      <li>LongjumpLegs</li>
      <li>WoundHealing_Fast</li>
      <li>Superclotting</li>
      <li>PsychicAbility_Enhanced</li>
      <li>LowSleep</li>
      <li>Robust</li>
      <li>Body_Standard</li>
      <li>Hair_SnowWhite</li>
      <li>Hair_DarkReddish</li>
      <li>Hair_MidBlack</li>
      <li>Hair_DarkBlack</li>
      <li>RimMandrake_Skin_MidGray</li>
      <li>Skin_LightGray</li>
      <li>DarkVision</li>
      <li>Hair_Grayless</li>
      <li>AptitudeStrong_Melee</li>
      <li>AptitudeStrong_Social</li>
      <li>AptitudeStrong_Intellectual</li>
    </genes>
  </XenotypeDef>""",
 'Herglic': """  <XenotypeDef>
    <defName>RimMandrakeHerglic</defName>
    <label>Herglic</label>
    <description>Herglics are a hulking species with black skin, a wide mouth and oily eyes. They are a rare sight in the galaxy and can hit like a wrecking ball. Their thick skin allows them to shake off most blunt attacks.</description>
    <iconPath>RimMandrakeSW/OR/OuterRim/XenotypeIcons/Xenotype_Herglic</iconPath>
    <inheritable>true</inheritable>
    <canGenerateAsCombatant>true</canGenerateAsCombatant>
    <factionlessGenerationWeight>0</factionlessGenerationWeight>
    <genes>
      <li>MeleeDamage_Strong</li>
      <li>Hair_BaldOnly</li>
      <li>Beard_NoBeardOnly</li>
      <li>RimMandrake_HerglicHead</li>
      <li>Body_Hulk</li>
      <li>Skin_InkBlack</li>
      <li>Skin_SlateGray</li>
      <li>Outland_ThickSkin</li>
      <li>Outland_BodyScale_Large</li>
      <li>AptitudeStrong_Melee</li>
      <li>AptitudePoor_Medicine</li>
      <li>AptitudePoor_Social</li>
      <li>AptitudePoor_Intellectual</li>
    </genes>
  </XenotypeDef>""",
 'Muun': """  <XenotypeDef>
    <defName>RimMandrakeMuun</defName>
    <label>Muun</label>
    <description>Tall thin humanoids known for running the InterGalactic Ganking Clan.</description>
    <iconPath>UI/Icons/Xenotypes/Genie</iconPath>
    <inheritable>true</inheritable>
    <canGenerateAsCombatant>true</canGenerateAsCombatant>
    <factionlessGenerationWeight>0</factionlessGenerationWeight>
    <combatPowerFactor>0.800000011920929</combatPowerFactor>
    <genes>
      <li>RimMandrake_Head_quarren</li>
      <li>RimMandrake_Body_gaunt</li>
      <li>RimMandrake_BodySizeGene_bigger</li>
      <li>Immunity_Weak</li>
      <li>WoundHealing_Slow</li>
      <li>Delicate</li>
      <li>Hair_BaldOnly</li>
      <li>Beard_NoBeardOnly</li>
      <li>Body_Thin</li>
      <li>Outland_Skin_Sandstone</li>
      <li>Outland_Skin_Granite</li>
      <li>ElongatedFingers</li>
      <li>AptitudePoor_Shooting</li>
      <li>AptitudePoor_Melee</li>
      <li>AptitudeRemarkable_Crafting</li>
      <li>AptitudeStrong_Medicine</li>
      <li>AptitudeRemarkable_Intellectual</li>
    </genes>
  </XenotypeDef>""",
 'Ortolan': """  <XenotypeDef>
    <defName>RimMandrakeOrtolan</defName>
    <label>Ortolan</label>
    <description>A sentient elephantine species of squad, blue-skinned bipeds with large, floppy ears.</description>
    <iconPath>UI/Icons/Xenotypes/Pigskin</iconPath>
    <inheritable>true</inheritable>
    <canGenerateAsCombatant>true</canGenerateAsCombatant>
    <factionlessGenerationWeight>0</factionlessGenerationWeight>
    <genes>
      <li>RimMandrake_Eyes_Big</li>
      <li>RimMandrake_Head_kubaz</li>
      <li>Immunity_Strong</li>
      <li>MinTemp_LargeDecrease</li>
      <li>Hair_BaldOnly</li>
      <li>Beard_NoBeardOnly</li>
      <li>Body_Fat</li>
      <li>Body_Hulk</li>
      <li>Skin_Blue</li>
      <li>Outland_Skin_PaleAzure</li>
      <li>Ears_Floppy</li>
      <li>Hands_Pig</li>
      <li>StrongStomach</li>
      <li>RobustDigestion</li>
      <li>Learning_Slow</li>
      <li>Nearsighted</li>
      <li>AptitudePoor_Cooking</li>
    </genes>
  </XenotypeDef>""",
 'SithZ': """  <XenotypeDef>
    <defName>RimMandrakeSithZ</defName>
    <label>Sith Zugurak (Pureblood)</label>
    <description>Zugurak  were the caste of engineers within the Sith species known for constructing burial mounds and starships.</description>
    <iconPath>RimMandrakeSW/OR/OuterRim/XenotypeIcons/Xenotype_Sith</iconPath>
    <inheritable>true</inheritable>
    <canGenerateAsCombatant>true</canGenerateAsCombatant>
    <factionlessGenerationWeight>0</factionlessGenerationWeight>
    <genes>
      <li>RimMandrake_FacialRidges_bumpy</li>
      <li>RimMandrake_Beard_chintendril</li>
      <li>Aggression_Aggressive</li>
      <li>Hair_BaldOnly</li>
      <li>Beard_NoBeardOnly</li>
      <li>Head_Gaunt</li>
      <li>Body_Standard</li>
      <li>Outland_Skin_DeepOrange</li>
      <li>Skin_Orange</li>
      <li>Outland_Skin_Brown</li>
      <li>Outland_Skin_PaleBrown</li>
      <li>Outland_Eye_Yellow</li>
      <li>ElongatedFingers</li>
      <li>Outland_RidgedSkin</li>
      <li>Outland_FamiliarScent</li>
      <li>AptitudeStrong_Construction</li>
      <li>AptitudeStrong_Mining</li>
      <li>AptitudeStrong_Cooking</li>
      <li>AptitudePoor_Artistic</li>
      <li>AptitudePoor_Social</li>
    </genes>
  </XenotypeDef>""",
 'Togorian': """  <XenotypeDef>
    <defName>RimMandrakeTogorian</defName>
    <label>Togorian</label>
    <description>Togirian were a sentient species of large, feline beings with digitgrade feet.</description>
    <iconPath>RimMandrakeSW/OR/OuterRim/XenotypeIcons/Xenotype_Cathar</iconPath>
    <inheritable>true</inheritable>
    <canGenerateAsCombatant>true</canGenerateAsCombatant>
    <factionlessGenerationWeight>0</factionlessGenerationWeight>
    <genes>
      <li>RimMandrake_Furskin_shortfur</li>
      <li>RimMandrake_statgene_predator</li>
      <li>RimMandrake_BodySizeGene_big</li>
      <li>Immunity_Strong</li>
      <li>NakedSpeed</li>
      <li>MaxTemp_SmallIncrease</li>
      <li>BS_Diet_Carnivore</li>
      <li>Aggression_Aggressive</li>
      <li>MeleeDamage_Strong</li>
      <li>Robust</li>
      <li>Pain_Reduced</li>
      <li>Hair_BaldOnly</li>
      <li>Beard_NoBeardOnly</li>
      <li>Body_Standard</li>
      <li>Body_Hulk</li>
      <li>Hair_LightOrange</li>
      <li>Hair_ReddishBrown</li>
      <li>Hair_MidBlack</li>
      <li>Hair_BrightRed</li>
      <li>Outland_HairColor_DarkOrange</li>
      <li>Ears_Cat</li>
      <li>Hair_Grayless</li>
      <li>AptitudePoor_Shooting</li>
      <li>AptitudePoor_Social</li>
      <li>AptitudePoor_Intellectual</li>
    </genes>
  </XenotypeDef>""",
}


def _guard_species_regression(built, skipped):
    """🔴 REFUSE to regenerate a SMALLER catalogue than the one we ship.

    Added 2026-08-15 after this nearly shipped silently. `pick_species` reads
    its species from the DUMP (`x`), and unlike `_gene_exists` it has no
    on-disk fallback. Once the three donors left the mod list their xenotypes
    left the dump with them, so the generator quietly built **57** species where
    the mod ships **69** — dropping Herglic, Defel, Ithorian, KelDor and eight
    others. Nothing failed; the output was simply twelve species smaller, and it
    would have been deployed over a live mod sitting in `ModsConfig.xml`.

    The old `KeyError: 'GS_Primitive'` crash was accidentally the only thing
    preventing that. Fixing the crash removed the accident, so the protection
    has to be deliberate. This guard is that protection — do not weaken it to
    'just get a build out'.

    ⚠️ THE TWO SENTENCES THAT USED TO END THIS DOCSTRING WERE BOTH WRONG, and
    they were quoted into two queue items and a commit before anyone checked.
    They said the repair was a disk fallback for `pick_species`, and that until
    then a regenerate needed a dump taken with the donors ACTIVE.

      * `pick_species` HAS had that fallback since 2026-08-19 — it reads the
        donors' XML on disk and says so in its own docstring.
      * The dump was never the problem. MEASURED 2026-08-23: all three captures
        contain the guy762 donor xenotypes and all report 578 mods. Re-taking it
        would never have lifted this.

    🔑 THE ACTUAL CAUSE: six species have NO DONOR AT ALL. Anzati, Muun, Ortolan
    and Togorian appear in none of the 97 donor XenotypeDefs on disk, with no
    near-matches; Herglic's donor carries no genes. They exist ONLY in this
    generator's own output. 63 built + 6 = 69 = what the mod ships.

    ⇒ This is the frozen-artifact failure: a generated file quietly accumulated
    entries its generator cannot derive. The fix is to CARRY them (see
    ORPHAN_XENOTYPES) and EMIT them — not to relax this guard. Making the guard
    count the table without emitting it was tried on 2026-08-23 and deleted six
    species and six pawn kinds from the live mod. Reverted from git."""
    # ⚠️ The +len(ORPHAN_XENOTYPES) is legitimate ONLY because write_xenotypes now
    # actually emits them, and it was NOT on 2026-08-23: the table existed, the
    # guard counted it, nothing wrote it, and the generator deleted 6 species and
    # 6 pawn kinds from the live mod while reporting success. Caught by diffing,
    # reverted from git.
    # 🔑 THE RULE THAT COST: a guard must count what was WRITTEN, never what is
    # merely on hand to write. If you ever split these two again, delete this term.
    have, want = len(built) + len(ORPHAN_XENOTYPES), _shipped_species_count()

    # ⭐ THE GENE GUARD. Added 2026-08-23 after the species guard passed on a
    # rebuild that was still 356 genes lighter. Checked FIRST because it is the
    # one that catches the subtler loss, and a message about species would send
    # the reader down the wrong path entirely.
    # 🔑 The GENE loss check does NOT live here. It cannot: this runs before the
    # defmap exists, so it could only count the rebuild, and the rebuild alone is
    # legitimately smaller than the union the writer now emits. Counting it here
    # would refuse forever while nothing was being lost.
    # ⇒ It lives in write_xenotypes, against the elements about to be written.
    # A guard must count what gets WRITTEN — that is the whole lesson of the
    # 2026-08-23 near-miss, and putting this one in the wrong place would repeat it.

    if want and have < want:
        lost = "\n  ".join("%-14s %s" % (s, why) for s, why in skipped)
        raise SystemExit(
            "REFUSING TO WRITE: would ship %d species, but the mod on disk has "
            "%d.\n"
            "Regenerating now would DELETE %d species from a mod that is live "
            "in ModsConfig.xml.\n"
            "Cause: pick_species reads species from the def dump, and the dump "
            "at\n  %s\nwas captured with the donors switched off, so their "
            "xenotypes are absent.\n"
            "Fix pick_species to fall back to the donors' XML on disk (as "
            "_gene_exists does),\nor regenerate from a dump taken with %s "
            "active.\n"
            "Skipped:\n  %s"
            % (have, want, want - have, DUMP, " + ".join(sorted(DONOR_PIDS)),
               lost))


def main():
    dry = "--no-textures" in sys.argv
    x, g = load_dump()
    defs, absts, kinds = index_donors()
    texidx = index_textures()
    stridx = index_strings()
    print("donor defs indexed %d, abstracts %d, kinds %d, textures %d/%d, "
          "word lists %d/%d"
          % (len(defs), len(absts), len(kinds),
             len(texidx["SWX"]), len(texidx["OR"]),
             len(stridx["SWX"]), len(stridx["OR"])), file=sys.stderr)

    built, skipped = pick_species(x, g, defs)
    _guard_species_regression(built, skipped)
    # 🔴 `defs` IS NOT OPTIONAL HERE. species_table grew a read-the-donors'-XML
    # fallback on 2026-08-19 precisely so a dump captured with the donors deduped
    # away could not shrink the roster - and pick_species was updated to pass it
    # while THESE TWO call sites were not. The function was fixed; its callers
    # were not. Measured 2026-08-23: without it the roster came back 6 species
    # short and _guard_species_regression refused to write, blocking every
    # regeneration since 2026-08-15 with a message naming the wrong cause.
    tbl = species_table(x, defs)
    used = sorted({n for b in built for n in b["genes"]})
    seeds = [n for n in used if _is_donor_gene(n, g, defs)]
    # Every donor RulePackDef, not only the ones a xenotype currently names.
    # Owner's ruling: start from theirs. `include` is followed by the closure,
    # so a namer that delegates to another namer brings it along.
    seeds += [n for n, (t, el) in defs.items() if el.tag == "RulePackDef"]
    # forcedHeadTypes are reached through the genes, but seed them explicitly so
    # a head type that only a dropped species used never enters the closure.
    keep, abstract = closure(seeds, defs, absts)

    defmap = rename_map(keep)
    absmap = rename_map(abstract)

    texhits, strhits = set(), set()
    bytype = {}
    for n in sorted(keep):
        tag, el = defs[n]
        c = rewrite(ET.fromstring(ET.tostring(el)), defmap, absmap, texidx,
                    tag, texhits, stridx, strhits)
        bytype.setdefault(c.tag, []).append(c)
    for a in sorted(abstract):
        tag, el = absts[a]
        c = rewrite(ET.fromstring(ET.tostring(el)), defmap, absmap, texidx,
                    tag, texhits, stridx, strhits)
        c.set("Abstract", "True")
        bytype.setdefault(c.tag, []).append(c)

    ok = apply_overrides(bytype, texhits)

    FILEMAP = {"GeneDef": "Defs/GeneDefs/SW_Genes.xml",
               "RulePackDef": "Defs/RulePackDefs/SW_NameMakers.xml",
               "HeadTypeDef": "Defs/HeadTypeDefs/SW_HeadTypes.xml",
               "GeneCategoryDef": "Defs/Misc/SW_Categories.xml",
               "StyleItemCategoryDef": "Defs/Misc/SW_Categories.xml",
               "FurDef": "Defs/Misc/SW_Categories.xml"}
    groups = {}
    for t, els in bytype.items():
        groups.setdefault(FILEMAP.get(t, "Defs/Misc/SW_Support.xml"),
                          []).extend(els)
    counts = {}
    for rel, els in sorted(groups.items()):
        els.sort(key=lambda e: (e.tag, e.findtext("defName") or e.get("Name")))
        write_xml(os.path.join(OUT, rel),
                  header(os.path.basename(rel),
                         "Copied from Star Wars Xenotypes (guy762) and Outer Rim "
                         "Galactic\nDiversity (Neronix17) and renamed into our "
                         "namespace, so this mod stands\nwithout either of them "
                         "installed."),
                  els)
        counts[rel] = len(els)

    inv = {v: k for k, v in defmap.items()}
    genes_out = [e.findtext("defName") for e in bytype.get("GeneDef", [])]
    origins = [defs[inv[d]][0] for d in genes_out if d in inv]
    n_swx = origins.count("SWX")
    n_or = origins.count("OR")
    write_about(len(built), n_swx, n_or)
    unnamed = write_xenotypes(built, defmap, x, tbl)
    write_pawnkinds(built)
    rescued = write_rescued_kinds(kinds, tbl, built, texidx)

    # xenotype icons live on the xenotype defs, which are ours, not copies --
    # rewrite them the same way.
    fix_xenotype_icons(texidx, texhits)
    n_files = copy_textures(texhits, texidx, dry)
    n_str = copy_strings(strhits, stridx)

    print("\n== species built %d  skipped %d" % (len(built), len(skipped)))
    for s, why in skipped:
        print("     %-24s %s" % (s, why))
    print("== genes referenced %d, of which copied %d"
          % (len(used), sum(1 for e in bytype.get("GeneDef", []))))
    print("== defs emitted")
    for t in sorted(bytype):
        print("     %-26s %d" % (t, len(bytype[t])))
    print("== abstracts %d" % len(abstract))
    print("== files")
    for rel, n in sorted(counts.items()):
        print("     %-40s %d defs" % (rel, n))
    print("== texture paths rewritten %d -> %d png files%s"
          % (len(texhits), n_files, " (dry)" if dry else ""))
    print("== word lists %d -> %d txt files" % (len(strhits), n_str))
    print("== rescued Galactic Diversity pawn kinds %d" % len(rescued))
    print("== eye-glow override applied: %s" % ok)
    print("== species with no name maker %d%s"
          % (len(unnamed), (": " + ", ".join(unnamed)) if unnamed else ""))
    if not verify():
        raise SystemExit(1)


DEPARTING = {"guy762.starwarsxenotypes",
             "neronix17.outerrim.galacticdiversity",
             "btd.xenotyperemix.starwars"}
PROSE = {"label", "description", "labelShortAdj", "labelNoun", "labelPlural",
         "title", "jobString", "symbol", "customLabel",
         # a PatchOperation xpath names a def in a mod it EDITS. Every such
         # operation here is Conditional or FindMod guarded, so the mod leaving
         # makes it a no-op, not a dead reference.
         "xpath", "keyword"}
# Only the DEFS. A PatchOperation naming a donor def is guarded by
# PatchOperationConditional or PatchOperationFindMod and becomes a no-op when
# that mod leaves; a def is not.
PATCHES = os.path.join(REPO, "src/Jawa/Jawa_Patches/Defs")


def scan_defs(root):
    """(defined names, referenced name -> definers). `@X` is a Name= attribute,
    which is a second and separate global namespace."""
    trees = []
    for dp, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".xml"):
                try:
                    trees.append((os.path.join(dp, f),
                                  ET.parse(os.path.join(dp, f)).getroot()))
                except ET.ParseError:
                    pass
    ours, refs, parents = set(), {}, set()
    for fp, r in trees:
        for el in r.iter():
            if not isinstance(el.tag, str):
                continue
            if el.findtext("defName"):
                ours.add(el.findtext("defName"))
            if el.get("Name"):
                ours.add("@" + el.get("Name"))
    for fp, r in trees:
        for el in r:
            if not isinstance(el.tag, str):
                continue
            who = el.findtext("defName") or el.get("Name") or \
                os.path.basename(fp)
            raw = rawtext_ids(el)
            for sub in [el] + list(el.iter()):
                if sub.get("ParentName"):
                    parents.add(sub.get("ParentName"))
                if sub.tag in PROSE or id(sub) in raw:
                    continue
                for t in ((sub.text or "").strip(), sub.tag):
                    if t and re.fullmatch(r"[A-Za-z0-9_.]+", t):
                        refs.setdefault(t, set()).add(who)
    return ours, refs, parents, trees


def _owner_index():
    """defName -> {packageId…}, over the WHOLE capture.

    ⭐ One indexed query where this used to `json.load` every `defs/*.json` in
    turn — 641 MB, and the only whole-graph load left in the repo. It is a pure
    projection of two columns, which is the shape the db is fast at; a loader
    that wants the RECORDS is better off with the JSON file, measured.

    🔴 It also drops the ORPHANS. `defs/` accumulates — nothing prunes it — so
    the directory walk ingested def types from captures on 2026-08-10…15 whose
    mods are long gone. Every dead defName in this index makes a reference to a
    REMOVED def look owned, and this function's whole job is finding references
    that will NOT resolve once the donors are off. Fail-toward-success, in the
    one function built to prevent exactly that.

    Falls back to the directory walk when the db or the skill is absent.
    """
    with dump_db(DUMP) as db:
        if db is not None:
            owner = {}
            for name, pkg in db.sql("SELECT def_name, package_id FROM defs"):
                owner.setdefault(name, set()).add((pkg or "").lower())
            return owner

    owner = {}
    for fn in os.listdir(DUMP + "/defs"):
        if not fn.endswith(".json"):
            continue
        try:
            d = json.load(io.open(DUMP + "/defs/" + fn, encoding="utf-8"))
        except ValueError:
            continue
        if not isinstance(d, dict) or "defs" not in d:
            continue
        for x in d["defs"]:
            owner.setdefault(x["defName"], set()).add(
                (x.get("packageId") or "").lower())
    return owner


def verify():
    """The acceptance test, and the only one that answers the question the mod
    exists for: with the three donors OFF, does everything still resolve?

    validate_patch.py does not answer it -- it checks against the CURRENT load
    set, where the donors are still installed and every stale reference still
    resolves. That is exactly the failure this mod is built to prevent, so it
    has to be checked against the surviving set instead."""
    owner = _owner_index()

    ours, refs, parents, trees = scan_defs(OUT + "/Defs")
    files = [fp for fp, _ in trees]
    pours, prefs, pparents, _ = scan_defs(PATCHES)
    known = ours | pours

    dead = {t: v for t, v in refs.items()
            if t not in ours and t in owner and owner[t] <= DEPARTING}
    pdead = {t: v for t, v in prefs.items()
             if t not in known and t in owner and owner[t] <= DEPARTING}
    dead.update({t: {"Jawa_Patches/" + w for w in v}
                 for t, v in pdead.items()})
    ext_parents = sorted(p for p in parents if "@" + p not in ours)
    # A ParentName names a Name= attribute, which never appears in the def dump
    # -- so the dump cannot say who owns one. The donors' own XML can. A patch
    # inheriting from a departing abstract is a SILENT discard, not an error.
    _, dabs, dkinds = index_donors()
    donor_names = set(dabs) | {k[1:] for k in dkinds if k.startswith("@")}
    dead_parents = sorted(p for p in pparents
                          if "@" + p not in known and p in donor_names)

    have = set()
    for dp, _, fs in os.walk(OUT + "/Textures"):
        for f in fs:
            if f.lower().endswith(".png"):
                have.add(os.path.relpath(os.path.join(dp, f),
                                         OUT + "/Textures")
                         .replace("\\", "/")[:-4].lower())
    dangling = set()
    for fp in files:
        for p in re.findall(r">(%s/[^<]+)<" % TEXNS,
                            io.open(fp, encoding="utf-8").read()):
            lp = p.lower()
            if any(lp + s in have for s in SUFFIXES) or \
                    any(k.startswith(lp + "/") for k in have):
                continue
            dangling.add(p)

    # Rule_File word lists. A namer whose word list is absent produces a blank
    # name, which is not an error and is invisible until a pawn is generated.
    words = set()
    for dp, _, fs in os.walk(OUT + "/Languages"):
        for f in fs:
            if f.lower().endswith(".txt"):
                words.add(os.path.relpath(os.path.join(dp, f),
                                          OUT + "/Languages/English/Strings")
                          .replace("\\", "/")[:-4].lower())
    dangling_words = set()
    for fp in files:
        for p in re.findall(r"<path>(%s/[^<]+)</path>" % STRNS,
                            io.open(fp, encoding="utf-8").read()):
            if p.lower() not in words:
                dangling_words.add(p)

    # Every species the donors NAMED must still be named. Species the donors
    # never named fall through to vanilla name generation, exactly as they do
    # today with the donors installed; that is not a regression and not a fail.
    x, _ = load_dump()
    _dd, _, _ = index_donors()          # same reason as main(): see species_table
    expect = {clean_name(sp) for sp, cand in species_table(x, _dd).items()
              if sp not in DROP_SPECIES
              and any(c and c in x and x[c]["fields"].get("nameMaker")
                      for c in cand)}
    xd = os.path.join(OUT, "Defs/XenotypeDefs")
    named, namers = set(), set()
    for f in sorted(os.listdir(xd)):
        if not f.endswith(".xml"):
            continue
        for el in ET.parse(os.path.join(xd, f)).getroot():
            if el.findtext("nameMaker"):
                named.add(el.findtext("defName"))
                namers.add(el.findtext("nameMaker"))
    lost = sorted(expect - named)
    bad_namers = sorted(n for n in namers if n not in ours)

    print("\n== VERIFY (donors switched OFF)")
    print("   defs defined here      %d + %d abstracts"
          % (len([o for o in ours if not o.startswith("@")]),
             len([o for o in ours if o.startswith("@")])))
    print("   references that die    %d" % len(dead))
    for t, v in sorted(dead.items()):
        print("        %-40s <- %s" % (t, sorted(v)[:3]))
    print("   dangling texture paths %d" % len(dangling))
    for p in sorted(dangling)[:10]:
        print("        %s" % p)
    print("   dangling word lists    %d" % len(dangling_words))
    for p in sorted(dangling_words)[:10]:
        print("        %s" % p)
    print("   species named          %d (donors named %d)"
          % (len(named), len(expect)))
    print("   species that lost a name %d %s" % (len(lost), ", ".join(lost)))
    print("   namers that do not resolve %d %s"
          % (len(bad_namers), ", ".join(bad_namers[:10])))
    print("   ParentName from a departing mod (silent discard) %d %s"
          % (len(dead_parents), ", ".join(dead_parents)))
    print("   ParentName from elsewhere (must be a mod we keep): %s"
          % ", ".join(ext_parents))
    return not (dead or dangling or dangling_words or lost or bad_namers
                or dead_parents)


def fix_xenotype_icons(texidx, texhits):
    p = os.path.join(OUT, "Defs/XenotypeDefs/RimMandrakeXenotypes.xml")
    t = io.open(p, encoding="utf-8").read()

    def sub(m):
        path = m.group(1)
        tag = resolve_tex(path, texidx, "OR")
        if not tag:
            return m.group(0)
        texhits.add((tag, path))
        return "<iconPath>%s/%s/%s</iconPath>" % (TEXNS, tag, path)
    t = re.sub(r"<iconPath>([^<]+)</iconPath>", sub, t)
    io.open(p, "w", encoding="utf-8").write(t)
    assert_comment_safe(p)


if __name__ == "__main__":
    main()
