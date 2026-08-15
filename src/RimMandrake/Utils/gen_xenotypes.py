#!/usr/bin/env python3
"""Generate the RimMandrake* xenotype and pawnkind defs for every Star Wars
species the installed mods can supply.

WHY THIS EXISTS
===============
Three mods ship overlapping Star Wars xenotypes -- BTD Xenotype REMIX (70),
Star Wars Xenotypes (58) and Outer Rim Galactic Diversity (44). They collide,
and BTD's own Harmony assembly exists purely to delete the duplicates and keep
its own. Owning the composition removes the collision at its root instead of
patching around it, and it is the only way to control the label and description
text a player actually reads.

WHAT IT DOES NOT DO
===================
It does NOT invent genes. Every gene here already ships in Alpha Genes, Outland
Genetics, Biotech, Integrated Genes and friends -- those mods stay installed and
are the ingredients. Only the RECIPE becomes ours. That is the same job BTD was
doing; we are replacing the recipe book, not the pantry.

THE ICON IS THE GRAPHICS GATE
=============================
A xenotype's look comes from its GENES, which carry their own art, plus one
`iconPath` for the UI. Genes are inherited from the source def verbatim, so the
in-game appearance is unchanged by construction. `iconPath` is the one asset we
must confirm resolves, because a missing icon is a visible hole in the pawn
screen rather than a silent no-op.

SOURCE PREFERENCE: BTD, then SWX, then Outer Rim. BTD is the most curated of the
three -- it exists specifically to reconcile the other two -- so its gene list is
the best available starting point.
"""
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

DUMP = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump"
WS = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
BTD = WS + "/3458153185"
GAME = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld"
OUTDIR = "src/Jawa/Jawa_Patches/Defs/XenotypeDefs"
KINDDIR = "src/Jawa/Jawa_Patches/Defs/PawnKindDefs"
PREFIX = "RimMandrake"

# packageIds that supply GENES and must stay installed. The three xenotype
# layers are a separate list and are the ones being stood down.
GENE_MODS_KEPT = ("Alpha Genes", "Outland - Genetics", "Biotech",
                  "Integrated Genes", "Big and Small - Genes & More",
                  "Star Wars Xenotypes", "Outer Rim - Galactic Diversity")


def load():
    x = {d["defName"]: d for d in json.load(
        io.open(DUMP + "/defs/XenotypeDef.json", encoding="utf-8"))["defs"]}
    g = {d["defName"]: d for d in json.load(
        io.open(DUMP + "/defs/GeneDef.json", encoding="utf-8"))["defs"]}
    return x, g


def species_table():
    """Species -> (BTD, SWX, OR) from BTD's own hand-curated equivalence file,
    plus any BTD xenotype the table forgot."""
    rows = {}
    root = ET.parse(BTD + "/BTD_Data/XenotypeEquivalencies.xml").getroot()
    for grp in root.findall("EquivalentGroup"):
        rows[grp.findtext("Species")] = (grp.findtext("BTD"),
                                         grp.findtext("SWX"),
                                         grp.findtext("OR"))
    return rows


def clean_name(species):
    """RimMandrakeTwilek. No dot: a dot in a defName is legal but reads as a
    type-qualified name (VFEPirates.WarcasketDef) and invites confusion."""
    return PREFIX + re.sub(r"[^A-Za-z0-9]", "", species)


def build_icon_index():
    """Index every texture BASENAME once, via a single `find`.

    The obvious implementation -- walk for Textures/ roots, then stat each
    candidate path -- takes many minutes here, because the workshop tree is
    1,246 mods on a Windows mount and Python's os.walk pays a syscall per entry.
    One `find` pass is dramatically faster, and basename is enough: a xenotype
    icon filename (Xenotype_Twilek) is distinctive, and we only need to answer
    "does this art exist at all", not "which mod owns it".
    """
    import subprocess
    cache = "/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/texture_index.json"
    if os.path.isfile(cache):
        try:
            return json.load(io.open(cache, encoding="utf-8"))
        except ValueError:
            pass
    idx = {}
    r = subprocess.run(
        ["find", WS, GAME + "/Data", GAME + "/Mods", "-type", "f",
         "-name", "*.png"], capture_output=True, text=True, timeout=1800)
    for line in r.stdout.splitlines():
        idx.setdefault(os.path.basename(line)[:-4].lower(), []).append(line)
    try:
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        json.dump(idx, io.open(cache, "w", encoding="utf-8"))
    except OSError:
        pass
    return idx


def icon_exists(path, idx):
    if not path:
        return False
    base = path.rsplit("/", 1)[-1].lower()
    if base in idx:
        return True
    # directional variants -- some icons ship only as _south etc.
    return any(base + s in idx for s in ("_north", "_south", "_east", "_west"))


def comment_safe(lines):
    """`--` is illegal INSIDE an XML comment and breaks the ENTIRE file, not
    just the comment. Our own generator header tripped this twice: once in the
    prose, and once when a naive guard ate the `<!--` delimiter itself. So the
    delimiters are exempt and only body text is rewritten.
    """
    out = []
    for ln in lines:
        if ln.strip() in ("<!--", "-->"):
            out.append(ln)
            continue
        # a rule made of = or - is fine; only prose gets the em dash
        if set(ln.strip()) <= set("-= "):
            out.append(ln)
            continue
        while "--" in ln:
            ln = ln.replace("--", "\u2014", 1)
        out.append(ln)
    return out


def esc(s):
    if s is None:
        return ""
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main():
    x, genes = load()
    rows = species_table()
    # BTD xenotypes the equivalence table omits
    for n in x:
        if n.startswith("BTD_") and not any(n == v[0] for v in rows.values()):
            rows[n[4:]] = (n, None, None)

    print("indexing textures (one find pass) ...", file=sys.stderr)
    roots = build_icon_index()
    print("  %d distinct texture basenames" % len(roots), file=sys.stderr)

    built, skipped = [], []
    for species in sorted(rows):
        btd, swx, orr = rows[species]
        src = next((c for c in (btd, swx, orr) if c and c in x), None)
        if src is None:
            skipped.append((species, "no source xenotype resolves"))
            continue
        f = x[src]["fields"]
        glist = f.get("genes") or []
        missing = [gn for gn in glist if gn not in genes]
        if missing:
            skipped.append((species, "genes do not resolve: %s" % missing[:3]))
            continue
        if not glist:
            skipped.append((species, "source carries no genes"))
            continue
        icon = f.get("iconPath")
        if not icon_exists(icon, roots):
            skipped.append((species, "icon not on disk: %s" % icon))
            continue
        built.append((species, src, f, glist, icon))

    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(KINDDIR, exist_ok=True)
    write_xenotypes(built)
    write_pawnkinds(built)

    print("\n  BUILT   %d" % len(built))
    print("  SKIPPED %d" % len(skipped))
    for s, why in skipped:
        print("     %-24s %s" % (s, why))


def write_xenotypes(built):
    out = [
        '<?xml version="1.0" encoding="utf-8"?>',
        "<!--",
        "  ============================================================================",
        "  RimMandrakeXenotypes.xml       GENERATED by src/RimMandrake/Utils/gen_xenotypes.py",
        "  ============================================================================",
        "",
        "  Do not hand-edit; re-run the generator.",
        "",
        "  Every Star Wars species the installed mods can supply, composed as OUR defs",
        "  so the three colliding xenotype layers can be stood down. The genes are not",
        "  ours and are not copied -- they are referenced, and their mods stay",
        "  installed. Only the recipe is ours.",
        "",
        "  Gene lists are inherited verbatim from the best available source, so a pawn",
        "  looks exactly as it did before. `iconPath` was confirmed present on disk for",
        "  every entry below; any species whose icon was missing is reported by the",
        "  generator and NOT written.",
        "  ============================================================================",
        "-->",
        "<Defs>",
        "",
    ]
    out = comment_safe(out)
    for species, src, f, glist, icon in built:
        dn = clean_name(species)
        label = f.get("label") or species
        desc = f.get("description") or f.get("descriptionShort") or ""
        out.append("  <!-- %s  (genes from %s) -->" % (species, src))
        out.append("  <XenotypeDef>")
        out.append("    <defName>%s</defName>" % dn)
        out.append("    <label>%s</label>" % esc(label))
        out.append("    <description>%s</description>" % esc(desc))
        out.append("    <iconPath>%s</iconPath>" % icon)
        out.append("    <inheritable>%s</inheritable>"
                   % ("true" if f.get("inheritable") else "false"))
        cgc = f.get("canGenerateAsCombatant")
        out.append("    <canGenerateAsCombatant>%s</canGenerateAsCombatant>"
                   % ("true" if cgc else "false"))
        # 0 keeps them out of the random-wanderer pool; our factions name the
        # species they field explicitly, which is the whole point of owning them.
        out.append("    <factionlessGenerationWeight>0</factionlessGenerationWeight>")
        cpf = f.get("combatPowerFactor")
        if cpf and cpf != 1:
            out.append("    <combatPowerFactor>%s</combatPowerFactor>" % cpf)
        out.append("    <genes>")
        for gn in glist:
            out.append("      <li>%s</li>" % gn)
        out.append("    </genes>")
        out.append("  </XenotypeDef>")
        out.append("")
    out.append("</Defs>")
    io.open(os.path.join(OUTDIR, "RimMandrakeXenotypes.xml"), "w",
            encoding="utf-8").write("\n".join(out) + "\n")


def write_pawnkinds(built):
    """One colonist-grade kind per species so CHECK can spawn and read each one
    back live. Without a PawnKindDef there is no way to ask the game for a pawn
    of a given xenotype, so verification would have no handle."""
    out = [
        '<?xml version="1.0" encoding="utf-8"?>',
        "<!--",
        "  ============================================================================",
        "  RimMandrakePawnKinds.xml       GENERATED by src/RimMandrake/Utils/gen_xenotypes.py",
        "  ============================================================================",
        "",
        "  Do not hand-edit; re-run the generator.",
        "",
        "  One kind per species, existing so a live check can SPAWN each xenotype and",
        "  read it back. A XenotypeDef on its own cannot be spawned -- pawn generation",
        "  takes a PawnKindDef -- so without these the 70 xenotypes are unverifiable",
        "  in game.",
        "",
        "  ParentName is `BasePlayerPawnKind`, which resolves: it is Core's abstract",
        "  with a Name= attribute. Colonist itself carries no Name= and cannot be a",
        "  parent, so the fields it would have supplied are restated here.",
        "  ============================================================================",
        "-->",
        "<Defs>",
        "",
    ]
    out = comment_safe(out)
    for species, src, f, glist, icon in built:
        dn = clean_name(species)
        label = f.get("label") or species
        out.append("  <PawnKindDef ParentName=\"BasePlayerPawnKind\">")
        out.append("    <defName>%s_Kind</defName>" % dn)
        out.append("    <label>%s</label>" % esc(label))
        out.append("    <defaultFactionDef>PlayerColony</defaultFactionDef>")
        out.append("    <apparelTags>")
        out.append("      <li>IndustrialBasic</li>")
        out.append("    </apparelTags>")
        out.append("    <apparelMoney>350~600</apparelMoney>")
        out.append("    <xenotypeSet>")
        out.append("      <xenotypeChances>")
        # dictionary-keyed by defName. An <li> here is a silent whole-def discard.
        out.append("        <%s>1.0</%s>" % (dn, dn))
        out.append("      </xenotypeChances>")
        out.append("    </xenotypeSet>")
        out.append("  </PawnKindDef>")
        out.append("")
    out.append("</Defs>")
    io.open(os.path.join(KINDDIR, "RimMandrakePawnKinds.xml"), "w",
            encoding="utf-8").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
