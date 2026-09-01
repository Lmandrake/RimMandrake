"""Generate absorbed defs for Sov.Sith (Rimwars: Pureblood Xenotype,
packageId Sov.Sith -- note the item's own notes and ledger history spell
it lowercase "sov.sith"; the real About.xml packageId is capitalized,
confirmed here, not guessed), workshop folder 3485069256, into
Jawa_Armoury.

This is the third piece of WEAPONS_ABSORPTION_WAVE_1's remaining scope:
the owner ruled 2026-08-30T20:29:22Z ("Port them anyway") to absorb this
pack's 8 defs despite zero measured world-save presence -- reversing the
item's own earlier "propose cut" recommendation. This generator carries
out that ruling; it does not re-litigate it.

Rule-6 DLL check: clean pass, pure content -- zero .dll anywhere under the
mod folder, and every Class= reference in its 4 Defs/*.xml files
(PawnRenderNodeProperties_Eye, Rule_File) is a stock RimWorld class. Its
ParentName references (GeneEyeColor, GeneJawBase, HeavyBoneBase) and its
XenotypeDef's ~20 vanilla gene list entries (Eyes_Red,
Aggression_HyperAggressive, MeleeDamage_Strong, etc.) are all vanilla
Biotech GeneDefs, not from another mod -- no cross-pack coupling of the
kind gen_kotorweapons_absorption.py found for guy762.KotORWeapons.

Same generator shape as gen_jds_armory_absorption.py (its template): parse
source XML directly, generic recursive serializer, defName-preserving, no
silent fixes, verify every texPath/iconPath/graphicPath/texPathFemale
before copying. One addition this pack needs that neither JDS Armory nor
kotorweapons did: its RulePackDef's Rule_File nodes point at plain-text
namer word lists under Languages/English/Strings/Pure/*.txt, not XML defs
or images -- copied verbatim alongside the art, verified to exist first
the same way texPath is.

Does not deploy: Sov.Sith stays active in the live ModsConfig.xml (rule
5); a defName-preserving copy loaded alongside it collides on every
defName. Retirement is gated on the item's own full-list-load check.
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
ARMOURY_ROOT = os.path.join(_REPO_ROOT, "src", "RimStarWars", "Armoury")
DEFS_ROOT = os.path.join(ARMOURY_ROOT, "Defs")
TEX_ROOT = os.path.join(ARMOURY_ROOT, "Textures")
LANG_ROOT = os.path.join(ARMOURY_ROOT, "Languages", "English", "Strings")

WORKSHOP_FOLDER = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3485069256"
EXPECTED_PACKAGE_ID = "Sov.Sith"
SRC_DEFS = os.path.join(WORKSHOP_FOLDER, "Defs")  # no 1.6/ subfolder; root-loaded only
SRC_TEX = os.path.join(WORKSHOP_FOLDER, "Textures")
SRC_LANG = os.path.join(WORKSHOP_FOLDER, "Languages", "English", "Strings")

SOURCE_FILES = {
    "RulePack.xml": "misc",
    "ThingDef_Genes.xml": "genes",
    "ThingDef_HeadTypes.xml": "headtypes",
    "XenoType.xml": "misc",
}

OUT_TARGET = {
    ("misc", "RulePackDef"): ("MiscDefs", "Absorbed_SovSith_Misc.xml"),
    ("misc", "XenotypeDef"): ("MiscDefs", "Absorbed_SovSith_Misc.xml"),
    ("genes", "GeneDef"): ("ThingDefs", "Absorbed_SovSith_Genes.xml"),
    ("headtypes", "HeadTypeDef"): ("ThingDefs", "Absorbed_SovSith_HeadTypes.xml"),
}


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

OWN_OUTPUT_PREFIX = "Absorbed_SovSith_"


def existing_defnames_in(defs_root):
    out = {}
    for dirpath, _, files in os.walk(defs_root):
        for fn in files:
            if not fn.endswith(".xml") or fn.startswith(OWN_OUTPUT_PREFIX):
                continue
            p = os.path.join(dirpath, fn)
            try:
                tree = ET.parse(p)
            except ET.ParseError:
                continue
            for el in tree.getroot():
                dn = el.find("defName")
                if dn is not None and dn.text:
                    out[dn.text.strip()] = os.path.relpath(p, defs_root)
    return out


def _escape_text(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _escape_attr(s):
    return _escape_text(s).replace('"', "&quot;")


def serialize(el, indent=1):
    pad = "  " * indent
    if el.tag is ET.Comment:
        text = (el.text or "").strip("\n")
        return "%s<!--%s-->" % (pad, text)

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


def write_defs_file(rel_dir, filename, elements, src_note):
    if not elements:
        return
    out_dir = os.path.join(DEFS_ROOT, rel_dir)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    body = "\n\n".join(serialize(e) for e in elements)
    fh = (
        '<?xml version="1.0" encoding="utf-8" ?>\n'
        "<!-- Absorbed from Sov.Sith (workshop %s, packageId %s),\n"
        "     WEAPONS_ABSORPTION_WAVE_1, owner ruling 2026-08-30T20:29:22Z\n"
        "     ('Port them anyway', despite zero measured world-save presence).\n"
        "     GENERATED by src/RimStarWars/Armoury/Source/gen_sovsith_absorption.py:\n"
        "     %s. defNames preserved verbatim.\n"
        "     Source pack stays active in the live ModsConfig for now (rule 5):\n"
        "     do NOT deploy this file until it retires. -->\n"
        "<Defs>\n\n" % (os.path.basename(WORKSHOP_FOLDER), EXPECTED_PACKAGE_ID, src_note)
    )
    fh += body + "\n\n</Defs>\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(fh)
    R.note("wrote %s (%d defs)" % (os.path.relpath(path, _REPO_ROOT), len(elements)))


def _copy_one(rel_stem_with_ext, src_root, dst_root):
    src = os.path.join(src_root, rel_stem_with_ext.replace("/", os.sep))
    dst = os.path.join(dst_root, rel_stem_with_ext.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)


def find_and_copy_texture(tex_path, seen, missing):
    if tex_path in seen or tex_path in missing:
        return
    copied_any = False
    for ext in (".png", ".jpg", ".jpeg"):
        if os.path.isfile(os.path.join(SRC_TEX, tex_path.replace("/", os.sep) + ext)):
            _copy_one(tex_path + ext, SRC_TEX, TEX_ROOT)
            copied_any = True
        for rot in ("_south", "_north", "_east", "_west"):
            if os.path.isfile(os.path.join(SRC_TEX, tex_path.replace("/", os.sep) + rot + ext)):
                _copy_one(tex_path + rot + ext, SRC_TEX, TEX_ROOT)
                copied_any = True
    if copied_any:
        seen.add(tex_path)
        return
    missing.add(tex_path)
    R.warn("texture path %r has no .png/.jpg/.jpeg (bare or rotation-suffixed) under %s -- reference kept in XML, art NOT copied" % (tex_path, SRC_TEX))


def collect_paths(el, tag, out):
    if el.tag == tag and el.text and el.text.strip():
        out.add(el.text.strip())
    for c in el:
        collect_paths(c, tag, out)


def collect_rule_file_paths(el, out):
    """RulePackDef <li Class="Rule_File"><path>X</path></li> entries point at
    plain-text namer word lists under Languages/, not images."""
    if el.tag == "li" and el.get("Class") == "Rule_File":
        p = el.find("path")
        if p is not None and p.text and p.text.strip():
            out.add(p.text.strip())
    for c in el:
        collect_rule_file_paths(c, out)


def copy_language_files(rel_path, seen, missing):
    if rel_path in seen or rel_path in missing:
        return
    src = os.path.join(SRC_LANG, rel_path.replace("/", os.sep) + ".txt")
    if os.path.isfile(src):
        dst = os.path.join(LANG_ROOT, rel_path.replace("/", os.sep) + ".txt")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        seen.add(rel_path)
        return
    missing.add(rel_path)
    R.warn("Rule_File path %r has no .txt under %s -- reference kept in XML, word list NOT copied" % (rel_path, SRC_LANG))


def main():
    about = os.path.join(WORKSHOP_FOLDER, "About", "About.xml")
    if not os.path.isfile(about):
        R.warn("About.xml not found at %s -- workshop folder id may be wrong, ABORTING" % about)
        sys.exit(1)
    about_text = open(about, "r", encoding="utf-8-sig").read()
    if EXPECTED_PACKAGE_ID not in about_text:
        R.warn("About.xml at %s does not contain expected packageId %r -- ABORTING, do not guess the folder"
               % (about, EXPECTED_PACKAGE_ID))
        sys.exit(1)
    R.note("confirmed workshop folder %s is packageId %s" % (WORKSHOP_FOLDER, EXPECTED_PACKAGE_ID))

    existing = existing_defnames_in(DEFS_ROOT)
    R.note("%d defNames already present in Jawa_Armoury/Defs -- collision-checking against these" % len(existing))

    buckets = {}
    all_new_defnames = {}
    tex_paths, lang_paths = set(), set()
    n_source_defs = 0
    n_dropped = 0

    for src_fn, category in SOURCE_FILES.items():
        src_path = os.path.join(SRC_DEFS, src_fn)
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        tree = ET.parse(src_path, parser=parser)
        root = tree.getroot()

        for el in root:
            if el.tag is ET.Comment:
                continue
            n_source_defs += 1
            target = OUT_TARGET.get((category, el.tag))
            if target is None:
                R.warn("%s: unhandled def tag <%s> (no OUT_TARGET entry) -- SKIPPED, not emitted" % (src_fn, el.tag))
                n_dropped += 1
                continue

            dn_el = el.find("defName")
            dn = dn_el.text.strip() if dn_el is not None and dn_el.text else None
            if dn:
                if dn in existing:
                    R.warn("defName %r (from %s) COLLIDES with already-absorbed %s -- SKIPPED" % (dn, src_fn, existing[dn]))
                    n_dropped += 1
                    continue
                if dn in all_new_defnames:
                    R.warn("defName %r (from %s) COLLIDES within this pack's own output (also in %s) -- SKIPPED"
                           % (dn, src_fn, all_new_defnames[dn]))
                    n_dropped += 1
                    continue
                all_new_defnames[dn] = src_fn

            collect_paths(el, "texPath", tex_paths)
            collect_paths(el, "texPathFemale", tex_paths)
            collect_paths(el, "iconPath", tex_paths)
            collect_paths(el, "graphicPath", tex_paths)
            collect_rule_file_paths(el, lang_paths)

            buckets.setdefault(target, []).append(el)

    tex_seen, tex_missing = set(), set()
    for t in sorted(tex_paths):
        find_and_copy_texture(t, tex_seen, tex_missing)
    lang_seen, lang_missing = set(), set()
    for p in sorted(lang_paths):
        copy_language_files(p, lang_seen, lang_missing)

    header_note = {
        "Absorbed_SovSith_Misc.xml": "RulePackDef (RulePack.xml) + XenotypeDef (XenoType.xml)",
        "Absorbed_SovSith_Genes.xml": "GeneDefs (ThingDef_Genes.xml)",
        "Absorbed_SovSith_HeadTypes.xml": "HeadTypeDefs (ThingDef_HeadTypes.xml)",
    }
    for (rel_dir, filename), elements in buckets.items():
        write_defs_file(rel_dir, filename, elements, header_note.get(filename, "absorbed content"))

    print("\n=== summary ===")
    n_written = n_source_defs - n_dropped
    n_abstract = n_written - len(all_new_defnames)
    print("source elements seen: %d; written to output: %d; dropped (collision/unhandled tag): %d"
          % (n_source_defs, n_written, n_dropped))
    print("of those written, %d carry a defName, %d are Abstract/parent-only defs with none "
          "(kept for ParentName resolution, not a drop)" % (len(all_new_defnames), n_abstract))
    print("textures: %d found+copied, %d MISSING" % (len(tex_seen), len(tex_missing)))
    print("Rule_File word lists: %d found+copied, %d MISSING" % (len(lang_seen), len(lang_missing)))
    print("notes: %d, warnings: %d" % (len(R.notes), len(R.warns)))
    if tex_missing:
        print("missing textures: %s" % sorted(tex_missing))
    if lang_missing:
        print("missing word lists: %s" % sorted(lang_missing))


if __name__ == "__main__":
    main()
