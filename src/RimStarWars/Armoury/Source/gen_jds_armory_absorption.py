"""Generate absorbed defs for JDS Armory ([JDS] StarWars - Armory,
packageId m3.continued.jangodsoul.starwars.bti, workshop folder
3511954303) into Jawa_Armoury -- the smallest of the three remaining
packs in WEAPONS_ABSORPTION_WAVE_1, run first to prove the Droidworks-
pattern generator approach before the two much larger packs
(guy762.kotorweapons 679 defs, guy762.mm.kotorcore 1235 defs).

Unlike gen_droidworks_defs.py (which builds output from a curated
extraction.json because its source spans three incompatible art
frameworks needing real classification work), JDS Armory's source is
flat: 5 raw Defs/*.xml files, no C# (measured -- zero .dll anywhere
under the mod folder, and every Class=/compClass=/verbClass=/
workerClass= reference in its 1.6 Defs is a stock RimWorld class; rule-6
DLL check is a clean pass, nothing to port). So this generator parses
the source XML directly and re-emits it through a generic recursive
serializer, rather than hand-writing a renderer per field the way
gen_droidworks_defs.py does -- there is no dedup/family-layer/graphics-
resolution work to do here, just defName-preserving transcription plus
asset-path verification, which is exactly the "generator, not hand-
porting" the item asked for once a pack is too large to hand-port
(74-estimated/71-measured defs, above the ~10-def hand-port cutoff used
for maincrep.eweb and rpgwanderer.opturret).

What this generator does NOT do, on purpose:
  - does not silently fix source bugs. Buildings_Production.xml's
    abstract JDS_Blaster_Worbench carries `Parant="BuildingBase"` (typo
    for ParentName) -- preserved verbatim, flagged loudly in the report,
    not corrected. A generator that "fixes" prose it wasn't asked to
    fix is exactly the kind of invention CLAUDE.md rules out.
  - does not resolve the ThingDefs_Hediff.xml HediffDef whose defName was
    plain "Burn" (now renamed to RSW_Burn by the naming migration) --
    that defName already collided with vanilla Core (BurnBase-derived)
    before the migration. JDS Armory already overrides it today, live,
    with this generator or without it; absorbing the defName-preserving
    copy perpetuates exactly the same override once the source pack
    retires, it does not introduce a NEW collision. Flagged, not fixed.
  - does not deploy. Every output file's header says so and the file is
    left undeployed in Jawa_Armoury's live mod folder (identical
    discipline to Absorbed_Eweb.xml/Absorbed_OPTurret.xml): the source
    pack (m3.continued.jangodsoul.starwars.bti) is still active in the
    live ModsConfig.xml, so a defName-preserving copy loaded alongside
    it collides on every single defName. Retirement is a separate later
    step gated on a full-list load proving zero missing-def errors
    (item's own rule 5).

Idempotent / re-runnable: re-running overwrites the same 4 generated
Defs/ files and re-copies (never deletes) the same asset files; nothing
here reads its own prior output.
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
SOUND_ROOT = os.path.join(ARMOURY_ROOT, "Sounds")

WORKSHOP_FOLDER = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3511954303"
EXPECTED_PACKAGE_ID = "m3.continued.jangodsoul.starwars.bti"
SRC_DEFS = os.path.join(WORKSHOP_FOLDER, "1.6", "Defs")
SRC_TEX = os.path.join(WORKSHOP_FOLDER, "Common", "Textures")
SRC_SOUND = os.path.join(WORKSHOP_FOLDER, "Common", "Sounds")

# source file -> (category key, target basename)
SOURCE_FILES = {
    "ThingDefs_Weapon.xml": "weapon",
    "ThingDefs_Projectile.xml": "projectile",
    "ThingDefs_Hediff.xml": "hediff",
    "Buildings_Production.xml": "building",
    "LaserSounds.xml": "sound",
}

# (source category, element tag) -> output (subdir, filename)
OUT_TARGET = {
    ("weapon", "ThingDef"): ("ThingDefs", "Absorbed_JDSArmory_Weapons.xml"),
    ("projectile", "ThingDef"): ("ThingDefs", "Absorbed_JDSArmory_Projectiles.xml"),
    ("projectile", "DamageDef"): ("DamageDefs", "Absorbed_JDSArmory_Damage.xml"),
    ("projectile", "HediffDef"): ("HediffDefs", "Absorbed_JDSArmory_Hediff.xml"),
    ("hediff", "HediffDef"): ("HediffDefs", "Absorbed_JDSArmory_Hediff.xml"),
    ("building", "ThingDef"): ("ThingDefs", "Absorbed_JDSArmory_Buildings.xml"),
    ("building", "WorkGiverDef"): ("ThingDefs", "Absorbed_JDSArmory_Buildings.xml"),
    ("sound", "SoundDef"): ("SoundDefs", "Absorbed_JDSArmory_Sounds.xml"),
}

HEADER_BY_FILE = {
    "Absorbed_JDSArmory_Weapons.xml": "melee and ranged weapon ThingDefs (ThingDefs_Weapon.xml)",
    "Absorbed_JDSArmory_Projectiles.xml": "projectile ThingDefs (ThingDefs_Projectile.xml)",
    "Absorbed_JDSArmory_Damage.xml": "the RSW_Blaster_Damage DamageDef (ThingDefs_Projectile.xml)",
    "Absorbed_JDSArmory_Hediff.xml": "HediffDefs (ThingDefs_Projectile.xml + ThingDefs_Hediff.xml)",
    "Absorbed_JDSArmory_Buildings.xml": "the Blastech Workbench ThingDef + its WorkGiverDef (Buildings_Production.xml)",
    "Absorbed_JDSArmory_Sounds.xml": "weapon-fire SoundDefs (LaserSounds.xml)",
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


OWN_OUTPUT_PREFIX = "Absorbed_JDSArmory_"


def existing_defnames_in(defs_root):
    """defName -> source file, for every def already under defs_root EXCEPT
    this generator's own prior output (files named Absorbed_JDSArmory_*) --
    a rerun must not treat its own last run as a foreign pack to collide
    against, or every rerun after the first wipes itself out. What remains
    is genuinely foreign absorbed content (the 2 hand-ported packs today)."""
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


# --------------------------------------------------------- serialization --
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
        "<!-- Absorbed from JDS Armory (workshop %s, packageId %s),\n"
        "     WEAPONS_ABSORPTION_WAVE_1. GENERATED by\n"
        "     src/RimStarWars/Armoury/Source/gen_jds_armory_absorption.py:\n"
        "     %s. defNames preserved verbatim.\n"
        "     Source pack stays active in the live ModsConfig for now (rule 5):\n"
        "     do NOT deploy this file until it retires, or duplicate defNames\n"
        "     result (measured: m3.continued.jangodsoul.starwars.bti IS active\n"
        "     today). -->\n"
        "<Defs>\n\n" % (os.path.basename(WORKSHOP_FOLDER), EXPECTED_PACKAGE_ID, src_note)
    )
    fh += body + "\n\n</Defs>\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(fh)
    R.note("wrote %s (%d defs)" % (os.path.relpath(path, _REPO_ROOT), len(elements)))


# ----------------------------------------------------------- asset copy --
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
        # bare texPath (Graphic_Single, or the base file some Graphic_Multi
        # packs also ship alongside their rotation set)
        if os.path.isfile(os.path.join(SRC_TEX, tex_path.replace("/", os.sep) + ext)):
            _copy_one(tex_path + ext, SRC_TEX, TEX_ROOT)
            copied_any = True
        # rotation-suffixed siblings (Graphic_Multi: texPath_south/_north/
        # _east.ext) -- copied whenever present regardless of the def's own
        # declared graphicClass, since a rotation set with no base file (or
        # a base file with no rotation set) both happen in this source pack
        # and neither should be dropped silently.
        for rot in ("_south", "_north", "_east", "_west"):
            if os.path.isfile(os.path.join(SRC_TEX, tex_path.replace("/", os.sep) + rot + ext)):
                _copy_one(tex_path + rot + ext, SRC_TEX, TEX_ROOT)
                copied_any = True
    if copied_any:
        seen.add(tex_path)
        return
    missing.add(tex_path)
    R.warn("texPath %r has no .png/.jpg/.jpeg (bare or rotation-suffixed) under %s -- reference kept in XML, art NOT copied" % (tex_path, SRC_TEX))


def find_and_copy_sound(clip_path, seen, missing):
    if clip_path in seen or clip_path in missing:
        return
    for ext in (".ogg", ".wav"):
        src = os.path.join(SRC_SOUND, clip_path.replace("/", os.sep) + ext)
        if os.path.isfile(src):
            dst = os.path.join(SOUND_ROOT, clip_path.replace("/", os.sep) + ext)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            seen.add(clip_path)
            return
    missing.add(clip_path)
    R.warn("clipPath %r has no .ogg/.wav under %s -- reference kept in XML, audio NOT copied" % (clip_path, SRC_SOUND))


def collect_paths(el, tag, out):
    if el.tag == tag and el.text and el.text.strip():
        out.add(el.text.strip())
    for c in el:
        collect_paths(c, tag, out)


def main():
    # ------------------------------------------------------- guard rails --
    about = os.path.join(WORKSHOP_FOLDER, "About", "About.xml")
    if not os.path.isfile(about):
        R.warn("About.xml not found at %s -- workshop folder id may be wrong, ABORTING" % about)
        sys.exit(1)
    about_text = open(about, "r", encoding="utf-8-sig").read()
    if EXPECTED_PACKAGE_ID not in about_text.lower():
        R.warn("About.xml at %s does not contain expected packageId %r -- ABORTING, do not guess the folder"
               % (about, EXPECTED_PACKAGE_ID))
        sys.exit(1)
    R.note("confirmed workshop folder %s is packageId %s" % (WORKSHOP_FOLDER, EXPECTED_PACKAGE_ID))

    existing = existing_defnames_in(DEFS_ROOT)
    R.note("%d defNames already present in Jawa_Armoury/Defs (the 2 hand-ported packs) -- collision-checking against these" % len(existing))

    buckets = {}  # (rel_dir, filename) -> list[Element]
    all_new_defnames = {}  # defName -> source file
    tex_paths, sound_paths = set(), set()
    n_source_defs = 0
    n_dropped = 0  # real drops: collision or unhandled tag (never "no defName")

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
                if dn == "RSW_Burn":
                    R.warn("HediffDef 'RSW_Burn' (from %s) was plain 'Burn' before the naming migration, "
                           "a vanilla Core defName (BurnBase-derived) -- JDS Armory already overrides it "
                           "today while active; absorbing preserves that override verbatim, does not "
                           "introduce a new one. Flagged, not fixed." % src_fn)

            collect_paths(el, "texPath", tex_paths)
            collect_paths(el, "uiIconPath", tex_paths)
            collect_paths(el, "clipPath", sound_paths)

            buckets.setdefault(target, []).append(el)

    sound_elements = buckets.get(("SoundDefs", "Absorbed_JDSArmory_Sounds.xml"), [])
    n_bad_class = sum(1 for el in sound_elements if 'AudioGrain_clip' in ET.tostring(el, encoding="unicode"))
    if n_bad_class:
        R.warn('LaserSounds.xml: %d SoundDef(s) use Class="AudioGrain_clip" (lowercase "clip") -- the real '
               'engine class is AudioGrain_Clip (capital C, confirmed against Absorbed_Eweb_Sounds.xml and '
               "validate_patch.py --defs). RimWorld's Class attribute is case-sensitive: every one of these "
               "SoundDefs silently fails to resolve and the WHOLE parent def is discarded -- in the SOURCE "
               "pack too, today, not a defect this absorption introduces. Preserved verbatim per this "
               "generator's own no-silent-fix rule; a BENCH decision on whether to correct it belongs to the "
               "item, not this script." % n_bad_class)

    if 'Parant="BuildingBase"' in open(os.path.join(SRC_DEFS, "Buildings_Production.xml"), encoding="utf-8-sig").read():
        R.warn("Buildings_Production.xml: abstract JDS_Blaster_Worbench carries Parant=\"BuildingBase\" "
               "(typo for ParentName) in the SOURCE -- preserved verbatim, not silently corrected. "
               "Effect: the abstract does not actually inherit BuildingBase; RSW_JDS_Blastech_Workbench (the "
               "only concrete child) still gets BuildingBase's fields ONLY where it re-declares them itself.")

    # ---------------------------------------------------------- assets ---
    tex_seen, tex_missing = set(), set()
    for t in sorted(tex_paths):
        find_and_copy_texture(t, tex_seen, tex_missing)
    sound_seen, sound_missing = set(), set()
    for s in sorted(sound_paths):
        find_and_copy_sound(s, sound_seen, sound_missing)

    # ------------------------------------------------------------- write --
    for (rel_dir, filename), elements in buckets.items():
        write_defs_file(rel_dir, filename, elements, HEADER_BY_FILE.get(filename, "absorbed content"))

    # ------------------------------------------------------------ report --
    print("\n=== summary ===")
    n_written = n_source_defs - n_dropped
    n_abstract = n_written - len(all_new_defnames)
    print("source elements seen: %d; written to output: %d; dropped (collision/unhandled tag): %d"
          % (n_source_defs, n_written, n_dropped))
    print("of those written, %d carry a defName, %d are Abstract parent-only defs with none "
          "(kept for ParentName resolution, not a drop)" % (len(all_new_defnames), n_abstract))
    print("textures: %d found+copied, %d MISSING" % (len(tex_seen), len(tex_missing)))
    print("sounds: %d found+copied, %d MISSING" % (len(sound_seen), len(sound_missing)))
    print("notes: %d, warnings: %d" % (len(R.notes), len(R.warns)))
    if tex_missing:
        print("missing textures: %s" % sorted(tex_missing))
    if sound_missing:
        print("missing sounds: %s" % sorted(sound_missing))


if __name__ == "__main__":
    main()
