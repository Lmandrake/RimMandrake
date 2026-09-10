"""Generate absorbed defs for det.epochspyrinth ("Epochs - Pyrinth", workshop
3336544632) into a new RimMandrake mod -- CRYSTAL_INGEST_EXECUTION_1 item 1
(design/Jawa/mods/crystal_mods_inventory.md ss1/ss3, ratified 2026-09-10).

Tier: RimMandrake, not RimStarWars/RimUtinni. Test from design/NAMING_SCHEME_
PLAN.md ss1 ("would a medieval-tribe player install this alone and understand
it?"): yes -- a glowing ore, torches/heater/brazier/melee blade, zero Star
Wars content, zero campaign-specific naming. Only the SCATTER GATE (Lantern
Deeps only) is Utinni-specific; that gate is a separate patch living under
src/RimUtinni/LanternDeeps/Patches/, not part of this absorbed content pack.

Rule-6 DLL check: det.epochspyrinth ships ZERO of its own DLLs (measured:
`find <workshop folder> -iname "*.dll"` returns nothing) and every comp/
Class reference in its Defs is a vanilla or DLC (Royalty/Ideology) class.
Clean absorption, no blocked-namespace filter needed (unlike gen_kotorweapons_
absorption.py's kotorweapons pass).

Generator shape: same discipline as gen_kotorweapons_absorption.py (parse
source XML directly, generic recursive serializer, verify+copy every
texPath/iconPath before trusting it, defName-preserving, no silent fixes),
simplified because this pack is small (11 defs across 4 Defs/ files + 2
Patches/ files) and carries none of that generator's DLL-coupling
complications.

What this generator does NOT do, on purpose:
  - does not deploy. det.epochspyrinth is STILL ACTIVE in the live
    ModsConfig.xml; a defName-preserving copy loaded alongside it collides on
    every defName (DV_MineablePyrinth, DV_Pyrinth, DV_PyrinthLamp, etc). This
    absorbed pack is generated dormant, matching the gen_kotorcore_absorption.py
    precedent ("Source pack stays active in the live ModsConfig for now; do
    NOT deploy this file until it retires, or duplicate defNames result").
    Retiring det.epochspyrinth (removing it from ModsConfig, deploying this
    pack instead) is a future PYRINTH_DONOR_RETIREMENT-style item, not this
    one -- CRYSTAL_INGEST_EXECUTION_1 is scoped "offline authoring, no bridge/
    live game needed" and a ModsConfig swap is a live/game-down action.
  - does not touch the two donor Patches/ files' own cross-mod gates
    (MO_Cost_Patch.xml's PatchOperationFindMod "Medieval Overhaul",
    Royalty_Patch.xml's per-element MayRequire) -- copied verbatim, they
    already gate correctly and travel with the content.
  - does not build the Lantern-Deeps scatter gate itself (zeroing
    mineableScatterCommonality on the LIVE donor def + the new Deeps-only
    GenStepDef) -- that patches the ACTIVE donor mod directly and lives under
    src/RimUtinni/LanternDeeps/Patches/ since it is Utinni-specific wiring,
    not part of this RimMandrake content pack. See RUT_LanternDeepGatePyrinth.xml
    and RUT_LanternDeepGenerator.xml's genSteps addition.

Idempotent / re-runnable: wipes and rewrites its own OUT_SUBDIR each run
(small enough not to need collision-exclusion bookkeeping); collision-checks
new defNames against every OTHER def already in the repo before writing.
"""
import os
import shutil
import sys
import xml.etree.ElementTree as ET


def _find_repo_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".git")) or os.path.isfile(os.path.join(d, "CLAUDE.md")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError("no repo root above %s" % start)
        d = parent


_REPO_ROOT = _find_repo_root(os.path.dirname(__file__))
MOD_ROOT = os.path.join(_REPO_ROOT, "src", "RimMandrake", "Pyrinth")
DEFS_ROOT = os.path.join(MOD_ROOT, "Defs")
PATCHES_ROOT = os.path.join(MOD_ROOT, "Patches")
TEX_ROOT = os.path.join(MOD_ROOT, "Textures")

WORKSHOP_FOLDER = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3336544632"
EXPECTED_PACKAGE_ID = "det.epochspyrinth"
SRC_DEFS = os.path.join(WORKSHOP_FOLDER, "1.6", "Defs")
SRC_PATCHES = os.path.join(WORKSHOP_FOLDER, "1.6", "Patches")
SRC_TEX = os.path.join(WORKSHOP_FOLDER, "Textures")

OUT_SUBDIR = "Absorbed_EpochsPyrinth"
OUT_FILE_PREFIX = "Absorbed_EpochsPyrinth_"


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


def existing_defnames_excluding(defs_root, exclude_dirs):
    out = {}
    for dirpath, dirnames, files in os.walk(defs_root):
        ap = os.path.abspath(dirpath)
        if any(ap == e or ap.startswith(e + os.sep) for e in exclude_dirs):
            dirnames[:] = []
            continue
        for fn in files:
            if not fn.endswith(".xml"):
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
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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


def collect_paths(el, tag, out):
    if el.tag == tag and el.text and el.text.strip():
        out.add(el.text.strip())
    for c in el:
        collect_paths(c, tag, out)


def find_and_copy_texture(tex_path, seen, missing):
    if tex_path in seen or tex_path in missing:
        return
    found = False
    for ext in (".png", ".jpg", ".jpeg"):
        base = os.path.join(SRC_TEX, tex_path.replace("/", os.sep) + ext)
        if os.path.isfile(base):
            dst = os.path.join(TEX_ROOT, tex_path.replace("/", os.sep) + ext)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(base, dst)
            found = True
        for rot in ("_south", "_north", "_east", "_west"):
            rp = os.path.join(SRC_TEX, tex_path.replace("/", os.sep) + rot + ext)
            if os.path.isfile(rp):
                dst = os.path.join(TEX_ROOT, tex_path.replace("/", os.sep) + rot + ext)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(rp, dst)
                found = True
    if found:
        seen.add(tex_path)
    else:
        missing.add(tex_path)
        R.warn("texPath/iconPath %r has no .png/.jpg/.jpeg under %s -- likely a vanilla/Core "
               "path (e.g. Things/Building/Filth, Things/Mote/SparkThrown), reference kept, "
               "not copied" % (tex_path, SRC_TEX))


def write_defs_file(rel_dir, filename, elements, src_relpath):
    if not elements:
        return
    out_dir = os.path.join(DEFS_ROOT, OUT_SUBDIR, rel_dir)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    body = "\n\n".join(serialize(e) for e in elements)
    header = (
        '<?xml version="1.0" encoding="utf-8" ?>\n'
        "<!-- Absorbed from det.epochspyrinth (\"Epochs - Pyrinth\", workshop %s),\n"
        "     source file 1.6/Defs/%s, CRYSTAL_INGEST_EXECUTION_1 item 1. GENERATED by\n"
        "     src/RimMandrake/Pyrinth/Source/gen_pyrinth_absorption.py.\n"
        "     defNames preserved verbatim. Source pack (det.epochspyrinth) stays active\n"
        "     in the live ModsConfig for now; do NOT deploy this mod until it retires,\n"
        "     or duplicate defNames result (see generator module docstring).\n"
        "     The Lantern-Deeps scatter gate lives separately, under\n"
        "     src/RimUtinni/LanternDeeps/Patches/ === it patches the LIVE donor def\n"
        "     directly since that is what is actually loaded today. -->\n"
        "<Defs>\n\n" % (os.path.basename(WORKSHOP_FOLDER), src_relpath)
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + body + "\n\n</Defs>\n")
    R.note("wrote %s (%d defs)" % (os.path.relpath(path, _REPO_ROOT), len(elements)))


def main():
    about = os.path.join(WORKSHOP_FOLDER, "About", "About.xml")
    if not os.path.isfile(about):
        R.warn("About.xml not found at %s -- ABORTING" % about)
        sys.exit(1)
    about_text = open(about, "r", encoding="utf-8-sig").read()
    if EXPECTED_PACKAGE_ID not in about_text:
        R.warn("About.xml at %s does not contain expected packageId %r -- ABORTING" % (about, EXPECTED_PACKAGE_ID))
        sys.exit(1)
    R.note("confirmed workshop folder %s is packageId %s" % (WORKSHOP_FOLDER, EXPECTED_PACKAGE_ID))

    own_out_dir = os.path.join(DEFS_ROOT, OUT_SUBDIR)
    if os.path.isdir(own_out_dir):
        shutil.rmtree(own_out_dir)
    own_patches_dir = os.path.join(PATCHES_ROOT, OUT_SUBDIR)
    if os.path.isdir(own_patches_dir):
        shutil.rmtree(own_patches_dir)

    existing = existing_defnames_excluding(
        os.path.join(_REPO_ROOT, "src"),
        [os.path.abspath(own_out_dir)],
    )
    R.note("%d defNames already present elsewhere in src/ -- collision-checking against these" % len(existing))

    src_files = []
    for dirpath, _, files in os.walk(SRC_DEFS):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                src_files.append(os.path.join(dirpath, fn))
    src_files.sort()
    R.note("%d source Defs/ XML files under %s" % (len(src_files), SRC_DEFS))

    buckets = {}
    all_new_defnames = {}
    tex_paths = set()
    n_source_defs = 0
    n_dropped = 0

    for src_path in src_files:
        rel = os.path.relpath(src_path, SRC_DEFS)
        rel_dir = os.path.dirname(rel)
        fn = os.path.basename(rel)
        out_filename = OUT_FILE_PREFIX + fn

        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        tree = ET.parse(src_path, parser=parser)
        root = tree.getroot()

        for el in root:
            if el.tag is ET.Comment:
                continue
            n_source_defs += 1
            dn_el = el.find("defName")
            dn = dn_el.text.strip() if dn_el is not None and dn_el.text else None

            if dn:
                if dn in existing:
                    R.warn("defName %r (from %s) COLLIDES with %s -- SKIPPED" % (dn, rel, existing[dn]))
                    n_dropped += 1
                    continue
                if dn in all_new_defnames:
                    R.warn("defName %r (from %s) COLLIDES within this pack (also %s) -- SKIPPED"
                           % (dn, rel, all_new_defnames[dn]))
                    n_dropped += 1
                    continue
                all_new_defnames[dn] = rel

            collect_paths(el, "texPath", tex_paths)
            collect_paths(el, "iconPath", tex_paths)
            collect_paths(el, "uiIconPath", tex_paths)
            buckets.setdefault((rel_dir, out_filename), []).append(el)

    tex_seen, tex_missing = set(), set()
    for t in sorted(tex_paths):
        find_and_copy_texture(t, tex_seen, tex_missing)

    for (rel_dir, filename), elements in sorted(buckets.items()):
        src_relpath = os.path.join(rel_dir, filename[len(OUT_FILE_PREFIX):])
        write_defs_file(rel_dir, filename, elements, src_relpath)

    # ---- Patches/ (copied verbatim, own gates untouched) ----
    n_patches = 0
    if os.path.isdir(SRC_PATCHES):
        for fn in sorted(os.listdir(SRC_PATCHES)):
            if not fn.endswith(".xml"):
                continue
            src_p = os.path.join(SRC_PATCHES, fn)
            out_dir = os.path.join(PATCHES_ROOT, OUT_SUBDIR)
            os.makedirs(out_dir, exist_ok=True)
            dst_p = os.path.join(out_dir, OUT_FILE_PREFIX + fn)
            text = open(src_p, "r", encoding="utf-8-sig").read()
            note = (
                "<!-- Absorbed verbatim from det.epochspyrinth (workshop %s), source\n"
                "     file 1.6/Patches/%s, CRYSTAL_INGEST_EXECUTION_1 item 1. GENERATED\n"
                "     by src/RimMandrake/Pyrinth/Source/gen_pyrinth_absorption.py. Own\n"
                "     cross-mod gate (PatchOperationFindMod/MayRequire) is UNCHANGED. -->\n"

            ) % (os.path.basename(WORKSHOP_FOLDER), fn)
            # Insert the note after the XML declaration line.
            if text.lstrip().startswith("<?xml"):
                decl_end = text.index("?>") + 2
                text = text[:decl_end] + "\n" + note + text[decl_end:]
            else:
                text = note + text
            with open(dst_p, "w", encoding="utf-8") as f:
                f.write(text)
            n_patches += 1
            R.note("wrote %s (verbatim patch)" % os.path.relpath(dst_p, _REPO_ROOT))

    print("\n=== summary ===")
    print("source elements seen: %d; written: %d; dropped (collision): %d; patches copied: %d"
          % (n_source_defs, len(all_new_defnames), n_dropped, n_patches))
    print("textures: %d found+copied, %d not found under this pack's own Textures/ (see warnings)"
          % (len(tex_seen), len(tex_missing)))
    print("notes: %d, warnings: %d" % (len(R.notes), len(R.warns)))


if __name__ == "__main__":
    main()
