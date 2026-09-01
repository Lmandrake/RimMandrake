"""Generate absorbed defs for guy762.KotORWeapons ([SW] KotOR Weapons and
Armor, packageId guy762.KotORWeapons, workshop folder 2938932438) into
Jawa_Armoury -- the second of the two remaining large packs in
WEAPONS_ABSORPTION_WAVE_1 (JDS Armory, 74 defs, was proven first; see
gen_jds_armory_absorption.py, this generator's template).

Unlike JDS Armory, this pack is NOT pure content, on two independent axes
-- both measured, neither guessed:

1. Rule-6 DLL check: kotorweapons ships ZERO of its own DLLs (the lone
   TheForce_LightsaberForms.dll under 1.5/AdditionalMods/_NO_ForceLightsabers
   is a disabled legacy shim, not loaded in 1.6). But its Defs reference
   compClass/Class values from a DOZEN external namespaces. Of those, most
   belong to independent framework mods that are not part of this
   absorption wave and stay active regardless (EBSGFramework.*,
   ModularWeapons2.*, AthenaFramework.*, MVCF.Comps.*,
   VanillaApparelExpanded.*, ArtificialBeings.*,
   FalloutCurrencies_NonReplacement.*, IgnoreConfigErrors.*, and
   Lightsaber.ModExtension_Conductive -- confirmed by DLL location to
   belong to lee.theforce.lightsaber, workshop 3466124712, a wholly
   separate mod, NOT guy762.mm.kotorcore as an earlier note guessed it
   might be). Four namespaces, however, are confirmed (by DLL filename
   match) to live in guy762.mm.kotorcore's OWN bundled Assemblies --
   CompExtraSounds, MentalBreakBlocker, SecondaryMineableYield,
   SelfHediffVerb -- a subset of the 7 load-bearing DLLs the WEAPONS_
   ABSORPTION_WAVE_1 ledger already flagged for kotorcore. Any element
   referencing one of these 4 depends on a DLL that retires alongside
   kotorcore's Defs/, so per the item's instruction this generator does
   NOT guess a resolution: those elements are EXCLUDED from the written
   output and logged verbatim (defName, source file, matched class) to
   Absorbed_KotorWeapons_BLOCKED_manifest.txt for a future comp-porting
   decision.

2. A second, larger coupling this pass discovered (not previously
   recorded in the item): measured 77 unique ParentName references across
   kotorweapons' own Defs, of which only 7 resolve to abstracts DEFINED
   INSIDE kotorweapons itself -- the other 70 (nearly every concrete
   weapon/apparel/gadget def in the pack) resolve to abstract ThingDefs
   that live in guy762.mm.kotorcore (confirmed: KotORRangedMakeable_
   OffHand and friends are defined in kotorcore's
   _BASE_SWKotORWeapons.xml, not anywhere in kotorweapons). This means
   kotorweapons is thin content sitting on kotorcore's abstract base
   layer, not an independently self-contained pack the way JDS Armory
   was. It does NOT block writing this pass's output -- kotorcore stays
   active in the live ModsConfig throughout (rule 5), so the ParentName
   references keep resolving against the live source pack exactly as
   they do today. It DOES mean kotorweapons cannot fully retire until
   kotorcore's corresponding abstract defs are also absorbed (item
   criterion 2, 1235 defs, not yet started) -- documented here, not
   solved here.

Generator shape: same discipline as gen_jds_armory_absorption.py (parse
source XML directly, generic recursive serializer, verify+copy every
texPath/iconPath before trusting it, defName-preserving, no silent
fixes), adapted in two ways justified above:
  - source spans ~78 files across 8 subfolders (not 5 flat files), so
    output mirrors the source's own subfolder layout under
    Defs/Absorbed_KotorWeapons/<subfolder>/ rather than JDS's manual
    per-(category,tag) OUT_TARGET table -- it does not scale past a
    handful of files and the source's own grouping is already sensible.
  - a per-element blocked-class filter (see point 1) that JDS never
    needed, because JDS's rule-6 check came back clean.

What this generator does NOT do, on purpose:
  - does not port or stub the 4 kotorcore-owned comp classes -- flagged,
    not guessed (see BLOCKED_manifest).
  - does not absorb kotorcore's abstract ParentName targets -- that is
    item criterion 2, a separate ~1235-def pass.
  - does not deploy. Source pack (guy762.KotORWeapons) is still active in
    the live ModsConfig.xml; a defName-preserving copy loaded alongside it
    collides on every defName (item rule 5).

Idempotent / re-runnable: collision-checks against existing defNames
EXCLUDE this generator's own output directory (Defs/Absorbed_KotorWeapons/),
so a rerun never treats its own prior run as a foreign pack -- the same
self-collision bug gen_jds_armory_absorption.py's Watch-out note warns
about.
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

WORKSHOP_FOLDER = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/2938932438"
EXPECTED_PACKAGE_ID = "guy762.KotORWeapons"
SRC_DEFS = os.path.join(WORKSHOP_FOLDER, "1.6", "Defs")
SRC_TEX = os.path.join(WORKSHOP_FOLDER, "Textures")

# guy762.mm.kotorcore, folder 3254370945 -- kotorweapons shares its
# UI/SWApparel/Items/Weapons/Other texture NAMESPACE with kotorcore
# (confirmed: validate_patch.py --defs against the full live mod set found
# Power_Blast/CombatHelmet/crystal_N/etc under kotorcore's own Textures/,
# not kotorweapons'). Checked as a fallback source, same as the ParentName
# and 4-comp-class coupling this generator's docstring already documents --
# a first pass over just kotorweapons' own Textures/ reported 68 "missing"
# textures; most of those actually live in kotorcore, only ~10 are
# genuinely absent anywhere (a real pre-existing source defect, preserved
# verbatim per this generator's no-silent-fix discipline).
KOTORCORE_FOLDER = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3254370945"
SRC_TEX_FALLBACK = os.path.join(KOTORCORE_FOLDER, "Textures")

OUT_SUBDIR = "Absorbed_KotorWeapons"  # under DEFS_ROOT; this generator's own output tree
OUT_FILE_PREFIX = "Absorbed_KotorWeapons_"

# UPDATED post-comp-porting-decision (WEAPONS_ABSORPTION_WAVE_1, kotorcore pass,
# reconciled after a same-session concurrent-agent collision on
# gen_kotorcore_absorption.py -- see that script's own docstring and the item's
# ledger note for the full account). The surviving comp-porting implementation
# is JawaArmoury.csproj (Source/<Component>/*.cs, one class per file), which
# kept every ported class NAMESPACE-IDENTICAL to its kotorcore source DLL --
# unlike this generator's own first-draft REWRITE_NAMESPACES approach (since
# discarded), a namespace-identical port needs ZERO XML rewriting: Class=/
# compClass=/verbClass=/driverClass= values already resolve correctly once
# JawaArmoury.dll is the assembly on the load path. So the 4 namespaces below
# are simply no longer blocked (not rewritten either) -- CompExtraSounds.,
# MentalBreakBlocker., SecondaryMineableYield., SelfHediffVerb.
#
# Two more namespaces are NEWLY blocked here, a real classification correction:
# the earlier kotorweapons pass (and this generator's own first draft) treated
# AthenaPort.*/SWCP.Core.*/SWCP.Currencies.*/SWCP.RimframeGrineerDoors.*/
# taranchuk_homingprojectiles.* as independent external-framework references
# that "stay active regardless" -- WRONG, confirmed against the rule-6 DLL
# inventory: AthenaPort.dll, SWCP_Core.dll, SWCP_Currencies.dll, SWCP_
# RimframeGrineerDoors.dll all live in guy762.mm.kotorcore's OWN 1.6/Assemblies/,
# and taranchuk_homingprojectiles.dll in kotorcore's own AdditionalMods/
# SharedCodeFromShun/ (not a separate workshop-subscribed mod). They retire
# alongside kotorcore's Defs/ exactly like the other 11 now-ported/blocked
# classes -- measured (grep against WeaponRanged_KotORBlasterRifle.xml and
# WeaponRanged_KotORHeavyRepeater.xml: both reference SWCP.Core.
# CompProperties_PositionAttributes, not in JawaArmoury's ported set), not
# guessed at. SWCP.Core is the only one of the 5 actually referenced by
# kotorweapons' own Defs (measured); the rest are named for completeness/
# consistency with gen_kotorcore_absorption.py's own block list.
BLOCKED_NAMESPACES = (
    "AthenaPort.",
    "SWCP.Core.",
    "SWCP.Currencies.",
    "SWCP.RimframeGrineerDoors.",
    "taranchuk_homingprojectiles.",
)


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
    """defName -> source file, for every def already under defs_root EXCEPT
    this generator's own output tree (exclude_dir) -- a rerun must not
    treat its own last run as a foreign pack to collide against."""
    out = {}
    for dirpath, dirnames, files in os.walk(defs_root):
        if os.path.abspath(dirpath) == os.path.abspath(exclude_dir) or \
           os.path.abspath(dirpath).startswith(os.path.abspath(exclude_dir) + os.sep):
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


def matched_blocked_namespace(el):
    """Return the first BLOCKED_NAMESPACES entry found anywhere in el's
    serialized form (any attribute value, any depth), or None."""
    blob = ET.tostring(el, encoding="unicode")
    for ns in BLOCKED_NAMESPACES:
        if ns in blob:
            return ns
    return None


def write_defs_file(rel_dir, filename, elements, src_relpath):
    if not elements:
        return
    out_dir = os.path.join(DEFS_ROOT, OUT_SUBDIR, rel_dir)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    body = "\n\n".join(serialize(e) for e in elements)
    fh = (
        '<?xml version="1.0" encoding="utf-8" ?>\n'
        "<!-- Absorbed from guy762.KotORWeapons (workshop %s, packageId %s),\n"
        "     source file 1.6/Defs/%s, WEAPONS_ABSORPTION_WAVE_1. GENERATED by\n"
        "     src/RimStarWars/Armoury/Source/gen_kotorweapons_absorption.py.\n"
        "     defNames preserved verbatim. Most ParentName references here\n"
        "     resolve to abstract defs that live in guy762.mm.kotorcore, NOT\n"
        "     in this file or this pack; kotorcore must stay active (or its\n"
        "     own abstracts must be absorbed, item criterion 2) for these to\n"
        "     resolve; see the generator's module docstring.\n"
        "     Source pack stays active in the live ModsConfig for now (rule 5);\n"
        "     do NOT deploy this file until it retires, or duplicate defNames\n"
        "     result. -->\n"
        "<Defs>\n\n" % (os.path.basename(WORKSHOP_FOLDER), EXPECTED_PACKAGE_ID, src_relpath)
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


def find_and_copy_texture(tex_path, seen, missing, from_fallback):
    if tex_path in seen or tex_path in missing:
        return
    copied_any = False
    used_fallback = False
    for src_root, is_fallback in ((SRC_TEX, False), (SRC_TEX_FALLBACK, True)):
        found_here = False
        for ext in (".png", ".jpg", ".jpeg"):
            if os.path.isfile(os.path.join(src_root, tex_path.replace("/", os.sep) + ext)):
                _copy_one(tex_path + ext, src_root, TEX_ROOT)
                found_here = True
            for rot in ("_south", "_north", "_east", "_west"):
                if os.path.isfile(os.path.join(src_root, tex_path.replace("/", os.sep) + rot + ext)):
                    _copy_one(tex_path + rot + ext, src_root, TEX_ROOT)
                    found_here = True
        if found_here:
            copied_any = True
            used_fallback = is_fallback
            break  # prefer kotorweapons' own copy over kotorcore's if both exist
    if copied_any:
        seen.add(tex_path)
        if used_fallback:
            from_fallback.add(tex_path)
        return
    missing.add(tex_path)
    R.warn("texPath/iconPath %r has no .png/.jpg/.jpeg (bare or rotation-suffixed) under this pack's own %s "
           "OR kotorcore's %s -- reference kept in XML, art NOT copied, genuinely absent from both packs' art trees"
           % (tex_path, SRC_TEX, SRC_TEX_FALLBACK))


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
    if EXPECTED_PACKAGE_ID not in about_text:
        R.warn("About.xml at %s does not contain expected packageId %r -- ABORTING, do not guess the folder"
               % (about, EXPECTED_PACKAGE_ID))
        sys.exit(1)
    R.note("confirmed workshop folder %s is packageId %s" % (WORKSHOP_FOLDER, EXPECTED_PACKAGE_ID))

    own_out_dir = os.path.join(DEFS_ROOT, OUT_SUBDIR)
    existing = existing_defnames_in(DEFS_ROOT, own_out_dir)
    R.note("%d defNames already present in Jawa_Armoury/Defs outside %s -- collision-checking against these"
           % (len(existing), OUT_SUBDIR))

    src_files = []
    for dirpath, _, files in os.walk(SRC_DEFS):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                src_files.append(os.path.join(dirpath, fn))
    src_files.sort()
    R.note("%d source XML files under %s" % (len(src_files), SRC_DEFS))

    buckets = {}  # (rel_dir, filename) -> list[Element]
    all_new_defnames = {}  # defName -> source file
    tex_paths = set()
    n_source_defs = 0
    n_dropped = 0       # collision drops
    n_blocked = 0        # excluded: references a kotorcore-owned comp class
    blocked_manifest = []

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

            blocked_ns = matched_blocked_namespace(el)
            if blocked_ns:
                n_blocked += 1
                blocked_manifest.append((dn or "(no defName)", rel, blocked_ns))
                continue

            if dn:
                if dn in existing:
                    R.warn("defName %r (from %s) COLLIDES with already-absorbed %s -- SKIPPED" % (dn, rel, existing[dn]))
                    n_dropped += 1
                    continue
                if dn in all_new_defnames:
                    R.warn("defName %r (from %s) COLLIDES within this pack's own output (also in %s) -- SKIPPED"
                           % (dn, rel, all_new_defnames[dn]))
                    n_dropped += 1
                    continue
                all_new_defnames[dn] = rel

            collect_paths(el, "texPath", tex_paths)
            collect_paths(el, "iconPath", tex_paths)

            buckets.setdefault((rel_dir, out_filename), []).append(el)

    # ---------------------------------------------------------- assets ---
    tex_seen, tex_missing, tex_from_fallback = set(), set(), set()
    for t in sorted(tex_paths):
        find_and_copy_texture(t, tex_seen, tex_missing, tex_from_fallback)
    if tex_from_fallback:
        R.note("%d texPath/iconPath references resolved via kotorcore's shared Textures/ namespace, not kotorweapons' own -- %s"
               % (len(tex_from_fallback), sorted(tex_from_fallback)))

    # ------------------------------------------------------------- write --
    for (rel_dir, filename), elements in sorted(buckets.items()):
        src_relpath = os.path.join(rel_dir, filename[len(OUT_FILE_PREFIX):])
        write_defs_file(rel_dir, filename, elements, src_relpath)

    manifest_path = os.path.join(own_out_dir, OUT_FILE_PREFIX + "BLOCKED_manifest.txt")
    if not blocked_manifest:
        # Stale-file cleanup: a prior run's manifest (from before the
        # comp-porting decision) must not survive a rerun that no longer
        # blocks anything, or it reads as "still blocked" when it isn't.
        if os.path.isfile(manifest_path):
            os.remove(manifest_path)
            R.note("removed stale %s (nothing blocked this run)" % os.path.relpath(manifest_path, _REPO_ROOT))
    if blocked_manifest:
        os.makedirs(own_out_dir, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(
                "guy762.KotORWeapons elements EXCLUDED from absorption -- each references a\n"
                "comp class confirmed to live in guy762.mm.kotorcore's own bundled DLLs\n"
                "(CompExtraSounds / MentalBreakBlocker / SecondaryMineableYield /\n"
                "SelfHediffVerb), which retire alongside kotorcore's Defs/. Absorbing these\n"
                "verbatim today would silently break once kotorcore's C# is gone, unless\n"
                "kotorcore's DLLs are kept active standalone or these classes are ported\n"
                "into Jawa_Armoury's own assembly -- WEAPONS_ABSORPTION_WAVE_1's undecided\n"
                "comp-porting fork. Not written to any Defs/ file; regenerate this list by\n"
                "rerunning gen_kotorweapons_absorption.py.\n\n"
                "defName\tsource file\tmatched class\n"
            )
            for dn, rel, ns in blocked_manifest:
                f.write("%s\t%s\t%s\n" % (dn, rel, ns))
        R.note("wrote %s (%d blocked elements)" % (os.path.relpath(manifest_path, _REPO_ROOT), len(blocked_manifest)))

    # ------------------------------------------------------------ report --
    print("\n=== summary ===")
    n_written = n_source_defs - n_dropped - n_blocked
    n_abstract = n_written - len(all_new_defnames)
    print("source elements seen: %d; written to output: %d; blocked (kotorcore comp dependency): %d; dropped (collision): %d"
          % (n_source_defs, n_written, n_blocked, n_dropped))
    print("of those written, %d carry a defName, %d are Abstract/parent-only defs with none "
          "(kept for ParentName resolution, not a drop)" % (len(all_new_defnames), n_abstract))
    print("textures/icons: %d found+copied (%d from kotorcore's shared namespace), %d genuinely MISSING"
          % (len(tex_seen), len(tex_from_fallback), len(tex_missing)))
    print("notes: %d, warnings: %d" % (len(R.notes), len(R.warns)))
    if tex_missing:
        print("missing textures: %s" % sorted(tex_missing))


if __name__ == "__main__":
    main()
