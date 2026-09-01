"""Absorb the gated-open `1.6/AdditionalMods/` content that
gen_kotorcore_absorption.py and gen_kotorweapons_absorption.py both missed
(they only ever walked `1.6/Defs/`) -- found while working
WEAPONS_DONOR_RETIREMENT_1. See that item file for the full LoadFolders.xml
gate analysis: every subfolder listed in PACKS below was confirmed, by
reading each pack's own LoadFolders.xml and cross-checking against the live
593-mod ModsConfig.xml, to actually gate OPEN on this exact mod list --
this is NOT "absorb everything AdditionalMods has", it is exactly the
subfolders that load real content into THIS game today.

Two things this script deliberately does NOT do, and why:
  - `guy762.mm.kotorcore/AdditionalMods/_DroidsBase` and `_BnSDroidsBase`:
    excluded on purpose, same as the main absorption -- Droidworks' territory.
  - `guy762.mm.kotorcore/AdditionalMods/SharedCodeFromShun`
    (taranchuk_homingprojectiles.dll): excluded on purpose, same reason pass 4
    already excluded its two consuming Defs files (Bullets_Special.xml,
    Bullets_HomingProjectiles.xml) -- IgnoresAccessChecksToAttribute, needs a
    live-behavior check this generator can't do offline. Retiring kotorcore
    drops this content; that is a known, accepted loss, not a new one.

Why patches need no xpath rebasing: every absorbed def keeps its EXACT
original defName (the absorption's own rule 1), and a PatchOperation matches
by defName against the post-merge unified tree, not by which mod defined it.
So a Patch file that matched a kotorcore-owned defName before still matches
once that defName is defined by mandrake.rsw.armoury instead -- the only
requirement is that the FILE ITSELF still gets loaded by an active mod, hence
"copy forward verbatim", never "rewrite". Same mechanism
SABER_GUARD_NAMES_WRONG_MOD_1 already established.

`guy762_IonizationABF.dll` (in kotorcore's own MHC subfolder, 6.6 KB, distinct
from the already-ported `guy762_Ionization`) is NOT handled by this script --
it needs a real C# port into JawaArmoury.dll, same discipline as pass 4's 11
DLLs, done separately.
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
# 🔴 gen_kotorcore_absorption.py's own ARMOURY_ROOT constant still points at
# src/Jawa/Jawa_Armoury, which no longer exists (the mod moved to
# src/RimStarWars/Armoury during the naming migration and that constant was
# never updated -- confirmed by directory listing, flagged here rather than
# silently worked around; this script uses the CURRENT, correct path).
ARMOURY_ROOT = os.path.join(_REPO_ROOT, "src", "RimStarWars", "Armoury")
DEFS_ROOT = os.path.join(ARMOURY_ROOT, "Defs")
PATCHES_ROOT = os.path.join(ARMOURY_ROOT, "Patches")
TEX_ROOT = os.path.join(ARMOURY_ROOT, "Textures")

WORKSHOP_ROOT = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"

# (pack label, workshop folder id, expected packageId, [(subfolder, dest label), ...])
PACKS = [
    ("kotorcore", "3254370945", "guy762.MM.KotORCore", [
        ("VEF", "VEF"),
        ("MHC", "MHC"),
        ("ATC", "ATC"),
        ("ShowMeYourHands", "ShowMeYourHands"),
        ("NO_DBH", "NO_DBH"),
        ("AdaptiveStorageFramework", "AdaptiveStorageFramework"),
        ("_BTDKotORGravships", "BTDKotORGravships"),
        ("EBSG", "EBSG"),
        ("ModularWeapons2", "ModularWeapons2"),
    ]),
    ("kotorweapons", "2938932438", "guy762.KotORWeapons", [
        ("ShowMeYourHands", "ShowMeYourHands"),
        ("BiomesCaverns", "BiomesCaverns"),
        ("_TheForceLightsabers", "TheForceLightsabers"),
    ]),
]

OUT_SUBDIR = "Absorbed_AdditionalMods"


class R:
    notes = []

    @staticmethod
    def note(msg):
        print(msg)
        R.notes.append(msg)


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


def _copy_sibling_frames(tex_path, src, base_dir, stem):
    """Copy every file in base_dir whose name is `stem` plus a suffix
    (_east/_north/_a/_b/...) -- Graphic_Multi/Graphic_Random art has no bare
    base file, only these. Established fix, same trap
    WEAPONS_ABSORPTION_WAVE_1's JDS Armory pass already hit and documented."""
    copied = 0
    if os.path.isdir(base_dir):
        for fn in os.listdir(base_dir):
            name, fext = os.path.splitext(fn)
            if fext.lower() in (".png", ".jpg", ".jpeg") and name.startswith(stem + "_") and name != stem:
                rel = tex_path + name[len(stem):]
                d2 = os.path.join(TEX_ROOT, rel.replace("/", os.sep) + fext)
                if not os.path.isfile(d2):
                    os.makedirs(os.path.dirname(d2), exist_ok=True)
                    shutil.copyfile(os.path.join(base_dir, fn), d2)
                copied += 1
    return copied


def find_and_copy_texture(tex_path, src_tex_root, seen, missing):
    if tex_path in seen or tex_path in missing:
        return
    base_dir = os.path.join(src_tex_root, os.path.dirname(tex_path).replace("/", os.sep))
    stem = os.path.basename(tex_path)

    for ext in (".png", ".jpg", ".jpeg"):
        src = os.path.join(src_tex_root, tex_path.replace("/", os.sep) + ext)
        if os.path.isfile(src):
            dst = os.path.join(TEX_ROOT, tex_path.replace("/", os.sep) + ext)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            seen.add(tex_path)
            _copy_sibling_frames(tex_path, src, base_dir, stem)
            return

    # Graphic_Multi/Graphic_Random: no bare base file, only rotation/frame
    # siblings (_east.png, _a.png, ...), or texPath names a directory of them.
    src_as_dir = os.path.join(src_tex_root, tex_path.replace("/", os.sep))
    n = _copy_sibling_frames(tex_path, None, base_dir, stem)
    if os.path.isdir(src_as_dir):
        n += _copy_sibling_frames(tex_path, None, src_as_dir, os.path.basename(src_as_dir))
        # a directory-of-frames texPath's siblings live INSIDE that directory,
        # named arbitrarily (not `stem`-prefixed) -- copy every image in it.
        for fn in os.listdir(src_as_dir):
            fext = os.path.splitext(fn)[1].lower()
            if fext in (".png", ".jpg", ".jpeg"):
                d2 = os.path.join(TEX_ROOT, tex_path.replace("/", os.sep), fn)
                if not os.path.isfile(d2):
                    os.makedirs(os.path.dirname(d2), exist_ok=True)
                    shutil.copyfile(os.path.join(src_as_dir, fn), d2)
                n += 1
    if n:
        seen.add(tex_path)
        return
    missing.add(tex_path)


def collect_texpaths(el, out):
    for tag in ("texPath", "iconPath", "uiIconPath"):
        v = el.attrib.get(tag)
        if v:
            out.add(v)
    if el.tag in ("texPath", "iconPath", "uiIconPath") and el.text and el.text.strip():
        out.add(el.text.strip())
    for c in el:
        collect_texpaths(c, out)


def process_pack(label, workshop_id, expected_pkg, subfolders):
    workshop_folder = os.path.join(WORKSHOP_ROOT, workshop_id)
    about = os.path.join(workshop_folder, "About", "About.xml")
    if not os.path.isfile(about):
        sys.exit("REFUSING %s: no About.xml at %s" % (label, about))
    about_txt = open(about, encoding="utf-8-sig").read()
    if expected_pkg.lower() not in about_txt.lower():
        sys.exit("REFUSING %s: expected packageId %s not found in %s" % (label, expected_pkg, about))

    seen_tex, missing_tex = set(), set()
    total_defs, total_patches = 0, 0

    for subfolder, dest_label in subfolders:
        src_root = os.path.join(workshop_folder, "1.6", "AdditionalMods", subfolder)
        if not os.path.isdir(src_root):
            R.note("SKIP %s/%s: source folder does not exist" % (label, subfolder))
            continue
        src_tex_root = os.path.join(workshop_folder, "Textures")

        for dirpath, _, files in os.walk(src_root):
            for fn in sorted(files):
                if not fn.lower().endswith(".xml"):
                    continue
                src_path = os.path.join(dirpath, fn)
                rel_from_sub = os.path.relpath(src_path, src_root)
                is_patch = rel_from_sub.split(os.sep)[0] == "Patches"

                try:
                    tree = ET.parse(src_path)
                except ET.ParseError as e:
                    R.note("SKIP unparseable %s: %s" % (src_path, e))
                    continue
                root = tree.getroot()

                texset = set()
                collect_texpaths(root, texset)
                for t in sorted(texset):
                    find_and_copy_texture(t, src_tex_root, seen_tex, missing_tex)

                elements = list(root)
                if not elements:
                    continue

                out_root = PATCHES_ROOT if is_patch else DEFS_ROOT
                out_dir = os.path.join(out_root, OUT_SUBDIR, label, dest_label)
                os.makedirs(out_dir, exist_ok=True)
                out_name = "Absorbed_%s_%s_%s" % (label.capitalize(), dest_label, fn)
                out_path = os.path.join(out_dir, out_name)

                root_tag = root.tag  # "Defs" or "Patch"
                body = "\n\n".join(serialize(e) for e in elements)
                header = (
                    '<?xml version="1.0" encoding="utf-8" ?>\n'
                    "<!-- Absorbed from %s (workshop %s), source file\n"
                    "     1.6/AdditionalMods/%s/%s, WEAPONS_DONOR_RETIREMENT_1.\n"
                    "     GENERATED by src/RimStarWars/Armoury/Source/gen_additionalmods_absorption.py.\n"
                    "     defNames preserved verbatim. This file's gate condition on this\n"
                    "     mod list was confirmed against the live ModsConfig.xml before\n"
                    "     absorbing: see WEAPONS_DONOR_RETIREMENT_1.md's gate table. -->\n"
                    % (expected_pkg, workshop_id, subfolder, rel_from_sub)
                )
                comment_body = header[len("<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n<!--"):-len("-->\n")]
                if "--" in comment_body:
                    sys.exit("REFUSING to write %s: header comment body contains '--' (illegal in an XML comment)" % out_path)
                header += "<%s>\n\n" % root_tag
                footer = "\n\n</%s>\n" % root_tag
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(header + body + footer)

                if is_patch:
                    total_patches += len(elements)
                else:
                    total_defs += len(elements)
                R.note("wrote %s (%d %s)" % (os.path.relpath(out_path, _REPO_ROOT), len(elements), "ops" if is_patch else "defs"))

    R.note("%s: %d defs, %d patch ops absorbed. Textures: %d copied, %d missing %s"
           % (label, total_defs, total_patches, len(seen_tex), len(missing_tex), sorted(missing_tex) if missing_tex else ""))


def main():
    for label, workshop_id, expected_pkg, subfolders in PACKS:
        process_pack(label, workshop_id, expected_pkg, subfolders)
    print("\n--- summary ---")
    for n in R.notes:
        print(n)


if __name__ == "__main__":
    main()
