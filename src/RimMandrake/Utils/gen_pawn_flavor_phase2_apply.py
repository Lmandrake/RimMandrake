#!/usr/bin/env python3
"""Generate the PAWN_FLAVOR_PHASE2_APPLY_1 patches: ship the owner-approved
Phase 2 flavor prose (1,783 rows) as XML patches into the Phase 1 flavor mod
(src/RimUtinni/PawnFlavor).

Inputs (all read-only here):
  * infrastructure/output/pawn_flavor_phase2_prose_draft.json - keyed
    "<defType>::<defName>", the owner-approved replacement prose.
  * design/Jawa/worldbuilding/review/pawn_flavor_phase2_register.decisions.json
    - refuses to run unless this carries the owner's stamp (savedAt+decidedBy).
  * A live def dump capture (--capture, defaults to the newest under DefDump/
    captures) - ground truth for: does this defName still exist, how many
    ThoughtDef stages does it have, which MentalStateDef does a MentalBreakDef
    link to, and which mod (packageId) owns each def. The census CSV's
    defNames are STALE for ~10 rows (this campaign's own NAMING_SCHEME
    migration re-prefixed them after the census was built, e.g.
    RimMandrakeAbednedo -> RSW_RimMandrakeAbednedo) and 3 more were renamed by
    their OWNING third-party mod independently (Humanoid Alien Races,
    Way Better Romance) - ALIASES below resolves every one of those found by
    hand this pass; 2 rows are genuinely dead (their def no longer exists
    anywhere) and are skipped, reported.

Emits three files under src/RimUtinni/PawnFlavor/Patches/:
  PawnFlavorPhase2_ThoughtDef.xml   - stage label/description, per stage index
  PawnFlavorPhase2_MentalBreak.xml  - MentalBreakDef.label + linked
                                       MentalStateDef.beginLetter/recoveryMessage
  PawnFlavorPhase2_Xenotype.xml     - XenotypeDef.label/description

Every field write uses PatchOperationSequence(Remove-then-Add) so it is
correct whether or not the raw XML for that def already defines the field
(Remove no-ops harmlessly if absent; Add always leaves it set) - this sidesteps
needing to know, per def, whether label/description is inherited vs literal.
Only fields with non-empty drafted text are emitted (matches the draft
authors' own convention of leaving a field blank when the vanilla original had
nothing there, e.g. several MentalBreakDefs have no beginLetter at all).

Every def-write group is wrapped in PatchOperationFindMod on the owning mod's
packageId (read from the dump, not guessed), except ludeon.rimworld (Core,
never inactive).
"""
import argparse
import glob
import json
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PROSE_JSON = os.path.join(ROOT, "infrastructure", "output", "pawn_flavor_phase2_prose_draft.json")
DECISIONS_JSON = os.path.join(ROOT, "design", "Jawa", "worldbuilding", "review",
                               "pawn_flavor_phase2_register.decisions.json")
OUT_DIR = os.path.join(ROOT, "src", "RimUtinni", "PawnFlavor", "Patches")
DUMP_ROOT_WIN = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\captures"
DUMP_ROOT_WSL = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/captures"

# Resolved by hand this pass (2026-09-01) - see module docstring. Left explicit
# rather than fuzzy-matched at runtime: fuzzy matching a defName rename is
# exactly the kind of guess CLAUDE.md forbids: every one of these was verified
# against the dump's modName + stage text before being trusted.
THOUGHT_ALIASES = {
    "Jawa_IkeeWatching": "RSW_Jawa_IkeeWatching",
    "RimMandrake_ThoughtDef_PsyHarmonize": "RSW_ThoughtDef_PsyHarmonize",
    "AlienVsXenophobia": "HAR_AlienVsXenophobia",
    "XenophobeVsXenophile": "HAR_XenophobeVsXenophile",
    "XenophobiaVsAlien": "HAR_XenophobiaVsAlien",
    "PassionateLovinAsexualNegative": "LovinAsexualNegative",
    "PassionateLovinAsexualPositive": "LovinAsexualPositive",
}
THOUGHT_DEAD = {"GraffitiMod_HappyArtist"}  # Mlie.GraffitiMod retired; superseded by mandrake.rm.graffiti
XENO_DEAD = {"MandrakeJawa"}  # stale duplicate of the RimMandrakeJawa row; that one lives on as RSW_RimMandrakeJawa


def find_capture(explicit):
    if explicit:
        return explicit
    root = DUMP_ROOT_WSL if os.path.isdir(DUMP_ROOT_WSL) else DUMP_ROOT_WIN
    caps = sorted(glob.glob(os.path.join(root, "*")))
    caps = [c for c in caps if os.path.isdir(c) and os.path.exists(os.path.join(c, "manifest.json"))]
    if not caps:
        raise SystemExit("REFUSED: no def dump capture found under %s" % root)
    return caps[-1]


def load_deftype(capture_dir, deftype):
    path = os.path.join(capture_dir, "defs", deftype + ".json")
    data = json.load(open(path, encoding="utf-8"))
    return {r["defName"]: r for r in data["defs"]}


def resolve_thought(defname, thoughts):
    if defname in THOUGHT_DEAD:
        return None, "dead (mod retired, no successor found)"
    if defname in thoughts:
        return defname, None
    alias = THOUGHT_ALIASES.get(defname)
    if alias and alias in thoughts:
        return alias, None
    return None, "not found in dump under its census name or a known alias"


def resolve_xeno(defname, xenos):
    if defname in XENO_DEAD:
        return None, "dead (stale duplicate; superseded by RSW_RimMandrakeJawa)"
    if defname in xenos:
        return defname, None
    alias = "RSW_" + defname
    if defname.startswith("RimMandrake") and alias in xenos:
        return alias, None
    return None, "not found in dump under its census name or the RSW_ tier-rename pattern"


def seq_op(parent_xpath, fields):
    """PatchOperationSequence: Remove each field (no-op if absent) then Add
    them all back together as one <li>. `fields` is an ordered dict of
    tag -> text."""
    seq = ET.Element("li", {"Class": "PatchOperationSequence"})
    ops = ET.SubElement(seq, "operations")
    for tag in fields:
        rm = ET.SubElement(ops, "li", {"Class": "PatchOperationRemove"})
        ET.SubElement(rm, "xpath").text = parent_xpath + "/" + tag
    add = ET.SubElement(ops, "li", {"Class": "PatchOperationAdd"})
    ET.SubElement(add, "xpath").text = parent_xpath
    value = ET.SubElement(add, "value")
    for tag, text in fields.items():
        ET.SubElement(value, tag).text = text
    return seq


def build_groups(entries):
    """entries: list of (packageId, <li Class=...> element). Returns the
    top-level list of <Operation>/<li> nodes for the Patch root, grouping
    same-packageId entries under one PatchOperationFindMod each (Core
    ungated)."""
    by_pkg = {}
    order = []
    for pkg, op in entries:
        if pkg not in by_pkg:
            by_pkg[pkg] = []
            order.append(pkg)
        by_pkg[pkg].append(op)
    top = []
    for pkg in order:
        ops = by_pkg[pkg]
        if pkg == "ludeon.rimworld":
            top.extend(ops)
            continue
        fm = ET.Element("Operation", {"Class": "PatchOperationFindMod"})
        mods = ET.SubElement(fm, "mods")
        ET.SubElement(mods, "li").text = pkg
        match = ET.SubElement(fm, "match", {"Class": "PatchOperationSequence"})
        match_ops = ET.SubElement(match, "operations")
        for op in ops:
            op.tag = "li"
            op.set("Class", "PatchOperationSequence")
            match_ops.append(op)
        top.append(fm)
    return top


def write_patch(path, top_ops):
    root = ET.Element("Patch")
    for op in top_ops:
        if op.tag == "Operation":
            root.append(op)
        else:
            op.tag = "Operation"
            root.append(op)
    ET.indent(root, space="  ")
    tree = ET.ElementTree(root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", help="explicit DefDump capture dir (defaults to newest)")
    args = ap.parse_args()

    dec = json.load(open(DECISIONS_JSON, encoding="utf-8"))
    if not dec.get("savedAt") or not dec.get("decidedBy"):
        raise SystemExit("REFUSED: %s carries no owner stamp (savedAt/decidedBy) - "
                          "this pass may not run until the owner has actually decided." % DECISIONS_JSON)
    rows = dec.get("rows", {})
    not_all_approved = [k for k, v in rows.items() if v.get("d") != "approve"]
    print("decisions stamp OK: decidedBy=%s savedAt=%s (%d rows, %d not approve)"
          % (dec["decidedBy"], dec["savedAt"], len(rows), len(not_all_approved)))

    capture = find_capture(args.capture)
    print("using capture:", capture)
    thoughts = load_deftype(capture, "ThoughtDef")
    mentalbreaks = load_deftype(capture, "MentalBreakDef")
    mentalstates = load_deftype(capture, "MentalStateDef")
    xenotypes = load_deftype(capture, "XenotypeDef")

    prose = json.load(open(PROSE_JSON, encoding="utf-8"))

    skipped = []
    stats = {"ThoughtDef": 0, "MentalBreakDef": 0, "XenotypeDef": 0}

    thought_entries = []
    mb_entries = []
    xeno_entries = []

    for key in sorted(prose):
        deftype, defname = key.split("::", 1)
        p = prose[key]

        if deftype == "ThoughtDef":
            real, why = resolve_thought(defname, thoughts)
            if not real:
                skipped.append((key, why))
                continue
            rec = thoughts[real]
            pkg = rec["packageId"]
            stages = rec["fields"].get("stages") or []
            label = (p.get("label") or "").strip()
            desc = (p.get("description") or "").strip()
            if not stages:
                skipped.append((key, "resolved def has zero stages (unexpected shape)"))
                continue
            for i in range(len(stages)):
                xp = 'Defs/ThoughtDef[defName="%s"]/stages/li[%d]' % (real, i + 1)
                fields = {}
                if label:
                    fields["label"] = label
                if desc:
                    fields["description"] = desc
                if fields:
                    thought_entries.append((pkg, seq_op(xp, fields)))
            stats["ThoughtDef"] += 1

        elif deftype == "MentalBreakDef":
            if defname not in mentalbreaks:
                skipped.append((key, "not found in dump"))
                continue
            rec = mentalbreaks[defname]
            pkg = rec["packageId"]
            label = (p.get("label") or "").strip()
            if label:
                xp = 'Defs/MentalBreakDef[defName="%s"]' % defname
                mb_entries.append((pkg, seq_op(xp, {"label": label})))
            ms_name = rec["fields"].get("mentalState")
            begin = (p.get("beginLetter") or "").strip()
            recov = (p.get("recoveryMessage") or "").strip()
            if ms_name and (begin or recov):
                if ms_name not in mentalstates:
                    skipped.append((key, "linked MentalStateDef %s not found in dump" % ms_name))
                else:
                    ms_pkg = mentalstates[ms_name]["packageId"]
                    xp = 'Defs/MentalStateDef[defName="%s"]' % ms_name
                    fields = {}
                    if begin:
                        fields["beginLetter"] = begin
                    if recov:
                        fields["recoveryMessage"] = recov
                    mb_entries.append((ms_pkg, seq_op(xp, fields)))
            stats["MentalBreakDef"] += 1

        elif deftype == "XenotypeDef":
            real, why = resolve_xeno(defname, xenotypes)
            if not real:
                skipped.append((key, why))
                continue
            rec = xenotypes[real]
            pkg = rec["packageId"]
            label = (p.get("label") or "").strip()
            desc = (p.get("description") or "").strip()
            fields = {}
            if label:
                fields["label"] = label
            if desc:
                fields["description"] = desc
            if fields:
                xp = 'Defs/XenotypeDef[defName="%s"]' % real
                xeno_entries.append((pkg, seq_op(xp, fields)))
            stats["XenotypeDef"] += 1

        else:
            skipped.append((key, "unknown defType"))

    write_patch(os.path.join(OUT_DIR, "PawnFlavorPhase2_ThoughtDef.xml"), build_groups(thought_entries))
    write_patch(os.path.join(OUT_DIR, "PawnFlavorPhase2_MentalBreak.xml"), build_groups(mb_entries))
    write_patch(os.path.join(OUT_DIR, "PawnFlavorPhase2_Xenotype.xml"), build_groups(xeno_entries))

    print("rows applied: ThoughtDef=%d MentalBreakDef=%d XenotypeDef=%d (total %d of %d)"
          % (stats["ThoughtDef"], stats["MentalBreakDef"], stats["XenotypeDef"],
             sum(stats.values()), len(prose)))
    print("thought stage-write ops:", len(thought_entries))
    print("skipped (%d):" % len(skipped))
    for k, why in skipped:
        print("  ", k, "-", why)


if __name__ == "__main__":
    sys.exit(main())
