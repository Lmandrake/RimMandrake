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
SPECIES_PREFIX = "RimMandrake"   # xenotype defNames: RimMandrakeTwilek

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
    "beeteedubs.xenotyperemix",
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
    """defName -> (donorTag, element); Name= -> (donorTag, element)."""
    defs, absts = {}, {}
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
                if dn:
                    defs[dn] = (tag, el)
                if el.get("Name"):
                    absts[el.get("Name")] = (tag, el)
    return defs, absts


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
    seen, abstract, queue = set(), set(), list(seeds)
    while queue:
        n = queue.pop()
        if n in seen or n not in defs:
            continue
        seen.add(n)
        _, el = defs[n]
        pn = el.get("ParentName")
        if pn and pn in absts and pn not in abstract:
            abstract.add(pn)
            queue.append("@" + pn)
        for sub in el.iter():
            t = (sub.text or "").strip()
            if t and re.fullmatch(r"[A-Za-z0-9_.]+", t) and t in defs:
                queue.append(t)
    changed = True
    while changed:
        changed = False
        for a in list(abstract):
            _, el = absts[a]
            pn = el.get("ParentName")
            if pn and pn in absts and pn not in abstract:
                abstract.add(pn)
                changed = True
            for sub in el.iter():
                t = (sub.text or "").strip()
                if t and re.fullmatch(r"[A-Za-z0-9_.]+", t) and t in defs \
                        and t not in seen:
                    seen.add(t)
                    changed = True
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


def rewrite(el, defmap, absmap, texidx, home, texhits):
    """Rename every reference in place. A reference left pointing at a donor
    name still resolves TODAY and breaks silently the moment the donor is
    switched off, which is the entire point of this mod."""
    for parent in list(el.iter()):
        for child in list(parent):
            cls = child.get("Class")
            if cls in DROP_EXT_CLASSES:
                parent.remove(child)
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
        if sub.tag in TEXFIELDS:
            do_path(sub)
        elif sub.tag in TEXCONTAINERS:
            for c in sub:
                do_path(c)
    return el


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


def write_xenotypes(built, defmap):
    els = []
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
                     "rewritten to our copy of it."),
              els)


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
    defs, absts = index_donors()
    texidx = index_textures()
    print("donor defs indexed %d, abstracts %d, textures %d/%d"
          % (len(defs), len(absts),
             len(texidx["SWX"]), len(texidx["OR"])), file=sys.stderr)

    built, skipped = pick_species(x, g)
    used = sorted({n for b in built for n in b["genes"]})
    seeds = [n for n in used
             if g[n].get("packageId") in DONOR_PIDS]
    # forcedHeadTypes are reached through the genes, but seed them explicitly so
    # a head type that only a dropped species used never enters the closure.
    keep, abstract = closure(seeds, defs, absts)

    defmap = rename_map(keep)
    absmap = rename_map(abstract)

    texhits = set()
    bytype = {}
    for n in sorted(keep):
        tag, el = defs[n]
        c = rewrite(ET.fromstring(ET.tostring(el)), defmap, absmap, texidx,
                    tag, texhits)
        bytype.setdefault(c.tag, []).append(c)
    for a in sorted(abstract):
        tag, el = absts[a]
        c = rewrite(ET.fromstring(ET.tostring(el)), defmap, absmap, texidx,
                    tag, texhits)
        c.set("Abstract", "True")
        bytype.setdefault(c.tag, []).append(c)

    FILEMAP = {"GeneDef": "Defs/GeneDefs/SW_Genes.xml",
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

    n_swx = sum(1 for n in keep if defs[n][0] == "SWX")
    n_or = len(keep) - n_swx
    write_about(len(built), n_swx, n_or)
    write_xenotypes(built, defmap)
    write_pawnkinds(built)

    # xenotype icons live on the xenotype defs, which are ours, not copies --
    # rewrite them the same way.
    fix_xenotype_icons(texidx, texhits)
    n_files = copy_textures(texhits, texidx, dry)

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
