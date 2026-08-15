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

WHAT IS COPIED           Star Wars Xenotypes + Outer Rim Galactic Diversity only.
WHAT IS DEPENDED ON      Biotech, Core, VEF, Outland Genetics, Integrated Genes,
                         LFS Eyes, Big and Small. Their genes are generic and stay
                         where they are.

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
DUMP = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios/DefDump")
WS = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
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

TEXFIELDS = ("texPath", "graphicPath", "iconPath", "path", "uiIconPath",
             "maskPath", "bodyNakedGraphicPath", "bodyDessicatedGraphicPath",
             "headDessicatedGraphicPath", "skullGraphicPath")
TEXCONTAINERS = ("texPaths", "graphicPaths", "bodyTypeGraphicPaths")
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


def write_xml(path, header_lines, elements):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    root = ET.Element("Defs")
    for e in elements:
        root.append(e)
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

def species_table(x):
    rows = {}
    root = ET.parse(BTD + "/BTD_Data/XenotypeEquivalencies.xml").getroot()
    for grp in root.findall("EquivalentGroup"):
        rows[grp.findtext("Species")] = (grp.findtext("BTD"),
                                         grp.findtext("SWX"),
                                         grp.findtext("OR"))
    for n in x:
        if n.startswith("BTD_") and not any(n == v[0] for v in rows.values()):
            rows[n[4:]] = (n, None, None)
    return rows


def clean_name(species):
    return SPECIES_PREFIX + re.sub(r"[^A-Za-z0-9]", "", species)


def pick_species(x, g):
    """Source preference BTD, then SWX, then Outer Rim. BTD exists specifically
    to reconcile the other two, so its gene list is the best starting point."""
    built, skipped = [], []
    for species, cand in sorted(species_table(x).items()):
        if species in DROP_SPECIES:
            skipped.append((species, "dropped by owner ruling"))
            continue
        src = next((c for c in cand if c and c in x), None)
        if src is None:
            skipped.append((species, "no source xenotype resolves"))
            continue
        f = x[src]["fields"]
        glist = f.get("genes") or []
        if not glist:
            skipped.append((species, "source carries no genes"))
            continue
        missing = [n for n in glist if n not in g]
        if missing:
            skipped.append((species, "genes do not resolve: %s" % missing[:3]))
            continue
        built.append(dict(species=species, src=src, f=f, genes=glist))
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
    desc = DESC.format(N=n_species, SWX=n_swx, OR=n_or)
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


def write_xenotypes(built, defmap, x, tbl):
    els = []
    unnamed = []
    for b in built:
        f = b["f"]
        e = ET.Element("XenotypeDef")
        ET.SubElement(e, "defName").text = clean_name(b["species"])
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
        for gn in b["genes"]:
            ET.SubElement(gl, "li").text = \
                defmap.get(gn, JAWA_GENES.get(gn, gn))
        els.append(e)
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
    write_xml(os.path.join(OUT, "Defs/PawnKindDefs/SW_RescuedKinds.xml"),
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
        xs = ET.SubElement(e, "xenotypeSet")
        xc = ET.SubElement(xs, "xenotypeChances")
        # DICTIONARY-KEYED by defName. An <li> here silently discards the def.
        ET.SubElement(xc, dn).text = "1.0"
        els.append(e)
    write_xml(os.path.join(OUT, "Defs/PawnKindDefs/RimMandrakePawnKinds.xml"),
              header("RimMandrakePawnKinds.xml",
                     "One colonist-grade kind per species. A XenotypeDef cannot be "
                     "spawned on\nits own -- pawn generation takes a PawnKindDef -- "
                     "so without these the\nspecies cannot be verified in game."),
              els)


# ---------------------------------------------------------------- main

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

    built, skipped = pick_species(x, g)
    tbl = species_table(x)
    used = sorted({n for b in built for n in b["genes"]})
    seeds = [n for n in used
             if g[n].get("packageId") in DONOR_PIDS]
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


def verify():
    """The acceptance test, and the only one that answers the question the mod
    exists for: with the three donors OFF, does everything still resolve?

    validate_patch.py does not answer it -- it checks against the CURRENT load
    set, where the donors are still installed and every stale reference still
    resolves. That is exactly the failure this mod is built to prevent, so it
    has to be checked against the surviving set instead."""
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
    expect = {clean_name(sp) for sp, cand in species_table(x).items()
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
