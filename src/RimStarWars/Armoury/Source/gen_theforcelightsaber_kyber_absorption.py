"""Generate absorbed defs for lee.theforce.lightsaber's KYBER content (workshop
3466124712, "Star Wars : The Force - Lightsaber") into Jawa_Armoury --
CRYSTAL_INGEST_EXECUTION_1 item 2 (design/Jawa/mods/crystal_mods_inventory.md
ss1/ss3, ratified 2026-09-10). Same generator discipline as
gen_kotorweapons_absorption.py (this generator's template): parse donor XML
directly, defName-preserving, no silent fixes, verify+copy every texPath.

SCOPE CUT, stated up front, not chased blind: this donor mod is a large,
Harmony-backed lightsaber system (its own Lightsaber.dll, melee-parry,
Force-power content, hilt crafting, etc). The item's ask is narrower --
"absorb kyber content" tied to the natural-scatter Deeps gate -- so this
generator absorbs only the MINEABLE kyber chain:
  - Force_CrystalFormation_Base/Small/Medium/Large (ThingDef_Building/
    ForceCrystal_Formations.xml) -- the mineable rock formations.
  - Force_CrystalFormation (ThingDef_Building/CrystalMapGenerator.xml) --
    the GenStepDef that scatters them.
  - Force_KyberCrystal ONLY, from ThingDefs_Misc/Kyber.xml. That file also
    defines Force_CraftSyntheticCrystal (RecipeDef) and Force_SyntheticCrystal/
    Force_BledCrystal/Force_CleansedCrystal (ThingDefs, ParentName=
    "KyberCrystalBase" -- which IS Force_KyberCrystal itself: it carries
    both Name="KyberCrystalBase" for inheritance AND a concrete defName,
    confirmed by direct read, `grep -n KyberCrystalBase Kyber.xml`). Those
    four are a separate downstream dark-side/light-side crafting flavor
    system, not part of "the natural scatter", and are EXCLUDED here --
    logged to BLOCKED_manifest.txt, not silently dropped. Their ParentName
    keeps resolving fine against the donor's own live Force_KyberCrystal
    (rule 5: the donor stays active; nothing here retires it), so excluding
    them from OUR absorbed copy orphans nothing.

Rule-6 DLL check: unlike kotorweapons (zero own DLLs), this donor ships its
OWN Lightsaber.dll and every absorbed element's `comps`/`colorGenerator`
Class= values that reference the `Lightsaber.` namespace
(CompProperties_ColorCrystal, CompProperties_GlowerOptions) are LEFT
UNCHANGED, exactly like gen_kotorweapons_absorption.py left kotorcore-owned
classes unchanged: lee.theforce.lightsaber stays ACTIVE in the live
ModsConfig (rule 5, this is an absorb-alongside pass, not a retirement), so
Lightsaber.dll keeps resolving these classes at runtime for as long as that
mod stays active. Not blocked, not ported -- just verbatim, same as
kotorweapons' classes resolving against kotorcore staying active.

What this generator does NOT do, on purpose:
  - does not deploy. lee.theforce.lightsaber is STILL ACTIVE; a defName-
    preserving copy loaded alongside it collides on every defName
    (Force_KyberCrystal, Force_CrystalFormation_Small, etc). Generated
    dormant, matching gen_kotorcore_absorption.py's precedent.
  - does not absorb the hilt/lightsaber-crafting system, Force powers, melee
    parry, or any Lightsaber.dll Harmony patch -- out of this item's scope.
  - does not build the Lantern-Deeps scatter gate itself -- that patches the
    LIVE donor defs directly (mineableScatterCommonality -> 0 on the three
    Force_CrystalFormation_* ThingDefs, since vanilla GenStep_RocksFromGrid
    reads that field regardless of the dedicated genstep; plus a
    PatchOperationRemove if the dedicated Force_CrystalFormation GenStepDef
    is ever confirmed wired into a MapGeneratorDef's genSteps list -- MEASURED
    0 rows in the live def dump today, so no such removal is needed, see the
    patch file's own header) -- lives under src/RimUtinni/LanternDeeps/Patches/.

Idempotent / re-runnable: wipes and rewrites its own OUT_SUBDIR each run.
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
ARMOURY_ROOT = os.path.join(_REPO_ROOT, "src", "RimStarWars", "Armoury")
DEFS_ROOT = os.path.join(ARMOURY_ROOT, "Defs")
TEX_ROOT = os.path.join(ARMOURY_ROOT, "Textures")

WORKSHOP_FOLDER = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3466124712"
EXPECTED_PACKAGE_ID = "lee.theforce.lightsaber"
SRC_DEFS = os.path.join(WORKSHOP_FOLDER, "1.6", "Defs")
SRC_TEX = os.path.join(WORKSHOP_FOLDER, "Textures")

OUT_SUBDIR = "Absorbed_TheForceLightsaber"
OUT_FILE_PREFIX = "Absorbed_TheForceLightsaber_"

# (relative-to-SRC_DEFS path, {defName-to-keep or None-for-"keep all"})
INCLUDE_FILES = {
    os.path.join("ThingDef_Building", "ForceCrystal_Formations.xml"): None,
    os.path.join("ThingDef_Building", "CrystalMapGenerator.xml"): None,
    os.path.join("ThingDefs_Misc", "Kyber.xml"): {"Force_KyberCrystal"},
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


def existing_defnames_in(defs_root, exclude_dir):
    out = {}
    for dirpath, dirnames, files in os.walk(defs_root):
        ap = os.path.abspath(dirpath)
        if ap == os.path.abspath(exclude_dir) or ap.startswith(os.path.abspath(exclude_dir) + os.sep):
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
        d = os.path.join(SRC_TEX, tex_path.replace("/", os.sep))
        if os.path.isdir(d):
            for fn in os.listdir(d):
                if fn.lower().endswith(ext):
                    dst = os.path.join(TEX_ROOT, tex_path.replace("/", os.sep), fn)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copyfile(os.path.join(d, fn), dst)
                    found = True
    if found:
        seen.add(tex_path)
    else:
        missing.add(tex_path)
        R.warn("texPath %r has no file/folder under %s -- kept, not copied" % (tex_path, SRC_TEX))


def write_defs_file(rel_dir, filename, elements, src_relpath):
    if not elements:
        return
    out_dir = os.path.join(DEFS_ROOT, OUT_SUBDIR, rel_dir)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    body = "\n\n".join(serialize(e) for e in elements)
    header = (
        '<?xml version="1.0" encoding="utf-8" ?>\n'
        "<!-- Absorbed from lee.theforce.lightsaber (workshop %s), source file\n"
        "     1.6/Defs/%s, CRYSTAL_INGEST_EXECUTION_1 item 2. GENERATED by\n"
        "     src/RimStarWars/Armoury/Source/gen_theforcelightsaber_kyber_absorption.py.\n"
        "     defNames preserved verbatim. Lightsaber.* comp/genStep Class= values are\n"
        "     UNCHANGED === lee.theforce.lightsaber must stay active in the live\n"
        "     ModsConfig for these to resolve (see generator module docstring).\n"
        "     Source pack stays active for now; do NOT deploy this file until it\n"
        "     retires, or duplicate defNames result. The Lantern-Deeps scatter gate\n"
        "     lives separately under src/RimUtinni/LanternDeeps/Patches/ === it patches\n"
        "     the LIVE donor def directly since that is what is actually loaded today. -->\n"
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

    existing = existing_defnames_in(DEFS_ROOT, own_out_dir)
    R.note("%d defNames already present in Jawa_Armoury/Defs outside %s -- collision-checking"
           % (len(existing), OUT_SUBDIR))

    buckets = {}
    all_new_defnames = {}
    tex_paths = set()
    n_source_defs = 0
    n_dropped = 0
    n_excluded_by_scope = 0
    excluded_manifest = []

    for rel, keep_set in INCLUDE_FILES.items():
        src_path = os.path.join(SRC_DEFS, rel)
        if not os.path.isfile(src_path):
            R.warn("expected source file missing: %s -- ABORTING" % src_path)
            sys.exit(1)
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

            if keep_set is not None and dn not in keep_set:
                n_excluded_by_scope += 1
                excluded_manifest.append((dn or "(no defName)", rel, el.tag))
                continue

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

    manifest_path = os.path.join(own_out_dir, OUT_FILE_PREFIX + "EXCLUDED_manifest.txt")
    if excluded_manifest:
        os.makedirs(own_out_dir, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(
                "lee.theforce.lightsaber elements EXCLUDED from this absorption pass on\n"
                "purpose (scope cut, see generator module docstring): the downstream dark/\n"
                "light-side crystal crafting chain (Force_CraftSyntheticCrystal recipe and\n"
                "Force_SyntheticCrystal/Force_BledCrystal/Force_CleansedCrystal items), not\n"
                "part of 'the natural scatter' this item gates. Their ParentName\n"
                "(KyberCrystalBase) keeps resolving against the donor's own live\n"
                "Force_KyberCrystal, which stays active -- excluding them here orphans\n"
                "nothing. Not written to any Defs/ file; regenerate this list by rerunning\n"
                "gen_theforcelightsaber_kyber_absorption.py.\n\n"
                "defName\tsource file\telement type\n"
            )
            for dn, rel, tag in excluded_manifest:
                f.write("%s\t%s\t%s\n" % (dn, rel, tag))
        R.note("wrote %s (%d excluded elements)" % (os.path.relpath(manifest_path, _REPO_ROOT), len(excluded_manifest)))

    print("\n=== summary ===")
    print("source elements seen: %d; written: %d; excluded by scope: %d; dropped (collision): %d"
          % (n_source_defs, len(all_new_defnames), n_excluded_by_scope, n_dropped))
    print("textures: %d found+copied, %d MISSING" % (len(tex_seen), len(tex_missing)))
    print("notes: %d, warnings: %d" % (len(R.notes), len(R.warns)))


if __name__ == "__main__":
    main()
