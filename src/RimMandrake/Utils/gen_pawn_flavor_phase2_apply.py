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

Every field write uses one PatchOperationConditional per field: Replace the
literal node if the raw (pre-patch) XML already has it, Add it if not.
CORRECTED 2026-09-01 (JAWA_PAWN_FLAVOR_PATCH_REGRESSION_1): the original
version of this generator used PatchOperationSequence(Remove-then-Add) on the
theory that "Remove no-ops harmlessly if absent" - that is FALSE.
PatchOperationRemove.ApplyWorker returns false (a genuine failure, not a
no-op) when its xpath matches zero nodes, and one failed step inside a
PatchOperationSequence fails the whole sequence, silently dropping every
field-write behind it. Confirmed live: 123 of 1,781 rows never actually
resolved (vanilla MentalBreakDefs commonly ship with NO <label> at all -
BedroomTantrum's is 3 lines, defName/mentalState only; many ThoughtDef
stages carry <label> but no <description>), even though validate_patch.py
reported the patch XML as structurally clean - it only checks well-formed
XML, never executes a patch against a real def tree. The
Conditional-per-field form sidesteps needing to know in Python, per def,
whether label/description is inherited vs literal vs entirely absent; the
live game's own xpath evaluation against the true raw tree decides.
Only fields with non-empty drafted text are emitted (matches the draft
authors' own convention of leaving a field blank when the vanilla original had
nothing there, e.g. several MentalBreakDefs have no beginLetter at all).

Every def-write group is wrapped in PatchOperationFindMod on the owning mod's
DISPLAY NAME (dump field "modName" - PatchOperationFindMod's <mods> list is
matched against ModMetaData.Name, never packageId; see build_groups()'s
2026-09-02 correction note), except ludeon.rimworld (Core, never inactive).

CORRECTED 2026-09-02 (PAWN_FLAVOR_STAGELESS_ADD_FAIL_1): ThoughtDef stage
writes no longer use seq_op directly - they use stage_op, which handles a
stage li that doesn't exist LITERALLY at all (not just missing a field
child), the common shape for a ThoughtDef that inherits its whole <stages>
via ParentName (e.g. AnyBodyPartButGroinCovered_Disapproved_Female,
EBSG_GeneticDrugDependency - raw-XML-confirmed, both declare only
defName/gender or modExtensions, no <stages> node at all). seq_op's
nomatch branch assumed the stage li already existed and only a FIELD
under it was missing (PatchOperationAdd(xpath=stages/li[N])) - but Add's
xpath must resolve to an existing node, so when li[N] itself is absent
the Add fails the same way Remove did in the first regression. See
stage_op()'s own docstring for the three-way conditional this replaced it
with.
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import CAPTURES  # noqa: E402
from retired_mods import is_retired  # noqa: E402

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
    root = CAPTURES
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
    """PatchOperationSequence of one PatchOperationConditional per field:
    Replace the literal node if it exists in the raw XML, Add it under the
    parent if it doesn't. `fields` is an ordered dict of tag -> text. See the
    module docstring's 2026-09-01 correction for why this replaced a blind
    Remove-then-Add."""
    seq = ET.Element("li", {"Class": "PatchOperationSequence"})
    ops = ET.SubElement(seq, "operations")
    for tag, text in fields.items():
        field_xpath = parent_xpath + "/" + tag
        cond = ET.SubElement(ops, "li", {"Class": "PatchOperationConditional"})
        ET.SubElement(cond, "xpath").text = field_xpath
        match = ET.SubElement(cond, "match", {"Class": "PatchOperationReplace"})
        ET.SubElement(match, "xpath").text = field_xpath
        mvalue = ET.SubElement(match, "value")
        ET.SubElement(mvalue, tag).text = text
        nomatch = ET.SubElement(cond, "nomatch", {"Class": "PatchOperationAdd"})
        ET.SubElement(nomatch, "xpath").text = parent_xpath
        nvalue = ET.SubElement(nomatch, "value")
        ET.SubElement(nvalue, tag).text = text
    return seq


def stage_op(defname, stage_index, fields):
    """Write into ThoughtDef stages/li[stage_index]. Unlike seq_op's callers
    (MentalBreakDef/MentalStateDef/XenotypeDef top-level def nodes, which
    always exist once resolved against the dump), a stage li is not
    guaranteed to exist literally: a ThoughtDef that inherits its whole
    <stages> list via ParentName (never overriding it) has NEITHER a literal
    <stages> nor any <li> child of its own. PAWN_FLAVOR_STAGELESS_ADD_FAIL_1,
    IL/raw-XML-confirmed on AnyBodyPartButGroinCovered_Disapproved_Female
    (Ideology) and EBSG_GeneticDrugDependency (EBSG Framework): seq_op's
    nomatch branch did PatchOperationAdd(xpath=stages/li[N]) to add a missing
    FIELD under an existing li - but PatchOperationAdd's xpath must resolve
    to an EXISTING node to insert under, so when li[N] itself doesn't exist
    the Add fails the same way PatchOperationRemove did in the earlier
    regression (JAWA_PAWN_FLAVOR_PATCH_REGRESSION_1).

    Three-way conditional, each branch decided by the live game's own xpath
    evaluation against the true pre-patch tree (never guessed in Python):
      1. li[stage_index] exists literally -> per-field Replace-or-Add, the
         same shape seq_op already uses (kept identical for the common case).
      2. li[stage_index] missing but <stages> exists -> Add a whole fresh
         <li> under <stages> (appended at the end - PatchOperationAdd has no
         positional insert, so a partially-declared stages list with a gap
         before stage_index is not exactly addressable; unseen in practice
         so far, both known cases have zero literal stages).
      3. <stages> itself missing (the common inherited-wholesale case) -> Add
         a whole fresh <stages><li>...</li></stages> under the ThoughtDef.
    """
    def_xpath = 'Defs/ThoughtDef[defName="%s"]' % defname
    stages_xpath = def_xpath + "/stages"
    li_xpath = stages_xpath + "/li[%d]" % stage_index

    def fresh_li():
        el = ET.Element("li")
        for tag, text in fields.items():
            ET.SubElement(el, tag).text = text
        return el

    # Branch 1: li exists -> identical per-field Replace/Add shape as seq_op.
    li_exists = ET.Element("op", {"Class": "PatchOperationSequence"})
    li_exists_ops = ET.SubElement(li_exists, "operations")
    for tag, text in fields.items():
        field_xpath = li_xpath + "/" + tag
        cond = ET.SubElement(li_exists_ops, "li", {"Class": "PatchOperationConditional"})
        ET.SubElement(cond, "xpath").text = field_xpath
        match = ET.SubElement(cond, "match", {"Class": "PatchOperationReplace"})
        ET.SubElement(match, "xpath").text = field_xpath
        mvalue = ET.SubElement(match, "value")
        ET.SubElement(mvalue, tag).text = text
        nomatch = ET.SubElement(cond, "nomatch", {"Class": "PatchOperationAdd"})
        ET.SubElement(nomatch, "xpath").text = li_xpath
        nvalue = ET.SubElement(nomatch, "value")
        ET.SubElement(nvalue, tag).text = text

    # Branch 2: <stages> exists, li[stage_index] doesn't -> add a fresh li under it.
    stages_exist_add = ET.Element("op", {"Class": "PatchOperationAdd"})
    ET.SubElement(stages_exist_add, "xpath").text = stages_xpath
    sv = ET.SubElement(stages_exist_add, "value")
    sv.append(fresh_li())

    # Branch 3: <stages> itself missing -> add a fresh <stages><li>...</li></stages>.
    stages_missing_add = ET.Element("op", {"Class": "PatchOperationAdd"})
    ET.SubElement(stages_missing_add, "xpath").text = def_xpath
    dv = ET.SubElement(stages_missing_add, "value")
    stages_el = ET.SubElement(dv, "stages")
    stages_el.append(fresh_li())

    stages_exist_add.tag = "match"
    stages_missing_add.tag = "nomatch"
    stages_cond = ET.Element("op", {"Class": "PatchOperationConditional"})
    ET.SubElement(stages_cond, "xpath").text = stages_xpath
    stages_cond.append(stages_exist_add)
    stages_cond.append(stages_missing_add)

    li_exists.tag = "match"
    stages_cond.tag = "nomatch"
    outer = ET.Element("li", {"Class": "PatchOperationConditional"})
    ET.SubElement(outer, "xpath").text = li_xpath
    outer.append(li_exists)
    outer.append(stages_cond)
    return outer


def build_groups(entries):
    """entries: list of (packageId, modName, <li Class=...> element). Returns
    the top-level list of <Operation>/<li> nodes for the Patch root, grouping
    same-packageId entries under one PatchOperationFindMod each (Core
    ungated).

    CORRECTED 2026-09-02 (PAWN_FLAVOR_SILENT_NONAPPLY_1): PatchOperationFindMod's
    <mods> list is matched by ModLister.HasActiveModWithName, which compares
    against ModMetaData.Name (the mod's DISPLAY name - "Ideology", "Caravan
    Adventures") via exact string equality (Verse source, IL-confirmed via
    ilprobe) - never the packageId. The prior version of this generator wrote
    the raw packageId (e.g. "ludeon.rimworld.ideology") into <li>, which can
    never equal a display name, so HasActiveModWithName always returned false
    and every non-Core FindMod block's <match> silently never ran - a much
    larger blast radius than the two rows (TreesDesired, TravelCompanions)
    that first surfaced it: every DLC- and workshop-mod-owned row across all
    1,781 was affected, only Core-owned (ungated) rows ever actually landed.
    Fixed by writing modName (already present per-def in the dump capture,
    ModMetaData.get_Name's own DLC special case - Expansion.label when the
    mod is a DLC, About.xml's <name> otherwise) instead of packageId. The
    grouping key stays packageId (a stable identity), only the emitted <li>
    text changes."""
    by_pkg = {}
    names = {}
    order = []
    for pkg, modname, op in entries:
        if pkg not in by_pkg:
            by_pkg[pkg] = []
            order.append(pkg)
        by_pkg[pkg].append(op)
        names.setdefault(pkg, modname)
    top = []
    for pkg in order:
        ops = by_pkg[pkg]
        if pkg == "ludeon.rimworld":
            top.extend(ops)
            continue
        fm = ET.Element("Operation", {"Class": "PatchOperationFindMod"})
        mods = ET.SubElement(fm, "mods")
        ET.SubElement(mods, "li").text = names[pkg]
        match = ET.SubElement(fm, "match", {"Class": "PatchOperationSequence"})
        match_ops = ET.SubElement(match, "operations")
        for op in ops:
            # op is already a correctly-classed <li> (PatchOperationSequence
            # from seq_op(), PatchOperationConditional from stage_op()) -
            # blindly overwriting Class here corrupted every stage_op()
            # entry's outer wrapper to the wrong class (2026-09-02 incident,
            # confirmed live: "doesn't correspond to any field in type
            # PatchOperationSequence" on AM_TerribleDreadnought/
            # FailedConvertAbilityInitiator/TrialFailed, which cascaded into
            # every other FindMod gate in the file reporting failed too).
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
    ap.add_argument("--out", help="override OUT_DIR, so a re-run can be diffed instead of overwriting what you wanted to compare against")
    args = ap.parse_args()
    out_dir = args.out or OUT_DIR

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
            modname = rec["modName"]
            if is_retired(pkg) or is_retired(modname):
                skipped.append((key, "retired mod (%s)" % modname))
                continue
            stages = rec["fields"].get("stages") or []
            label = (p.get("label") or "").strip()
            desc = (p.get("description") or "").strip()
            if not stages:
                skipped.append((key, "resolved def has zero stages (unexpected shape)"))
                continue
            for i in range(len(stages)):
                fields = {}
                if label:
                    fields["label"] = label
                if desc:
                    fields["description"] = desc
                if fields:
                    thought_entries.append((pkg, modname, stage_op(real, i + 1, fields)))
            stats["ThoughtDef"] += 1

        elif deftype == "MentalBreakDef":
            if defname not in mentalbreaks:
                skipped.append((key, "not found in dump"))
                continue
            rec = mentalbreaks[defname]
            pkg = rec["packageId"]
            modname = rec["modName"]
            if is_retired(pkg) or is_retired(modname):
                skipped.append((key, "retired mod (%s)" % modname))
                continue
            label = (p.get("label") or "").strip()
            if label:
                xp = 'Defs/MentalBreakDef[defName="%s"]' % defname
                mb_entries.append((pkg, modname, seq_op(xp, {"label": label})))
            ms_name = rec["fields"].get("mentalState")
            begin = (p.get("beginLetter") or "").strip()
            recov = (p.get("recoveryMessage") or "").strip()
            if ms_name and (begin or recov):
                if ms_name not in mentalstates:
                    skipped.append((key, "linked MentalStateDef %s not found in dump" % ms_name))
                else:
                    ms_pkg = mentalstates[ms_name]["packageId"]
                    ms_modname = mentalstates[ms_name]["modName"]
                    if is_retired(ms_pkg) or is_retired(ms_modname):
                        skipped.append((key, "linked MentalStateDef's mod retired (%s)" % ms_modname))
                    else:
                        xp = 'Defs/MentalStateDef[defName="%s"]' % ms_name
                        fields = {}
                        if begin:
                            fields["beginLetter"] = begin
                        if recov:
                            fields["recoveryMessage"] = recov
                        mb_entries.append((ms_pkg, ms_modname, seq_op(xp, fields)))
            stats["MentalBreakDef"] += 1

        elif deftype == "XenotypeDef":
            real, why = resolve_xeno(defname, xenotypes)
            if not real:
                skipped.append((key, why))
                continue
            rec = xenotypes[real]
            pkg = rec["packageId"]
            modname = rec["modName"]
            if is_retired(pkg) or is_retired(modname):
                skipped.append((key, "retired mod (%s)" % modname))
                continue
            label = (p.get("label") or "").strip()
            desc = (p.get("description") or "").strip()
            fields = {}
            if label:
                fields["label"] = label
            if desc:
                fields["description"] = desc
            if fields:
                xp = 'Defs/XenotypeDef[defName="%s"]' % real
                xeno_entries.append((pkg, modname, seq_op(xp, fields)))
            stats["XenotypeDef"] += 1

        else:
            skipped.append((key, "unknown defType"))

    write_patch(os.path.join(out_dir, "PawnFlavorPhase2_ThoughtDef.xml"), build_groups(thought_entries))
    write_patch(os.path.join(out_dir, "PawnFlavorPhase2_MentalBreak.xml"), build_groups(mb_entries))
    write_patch(os.path.join(out_dir, "PawnFlavorPhase2_Xenotype.xml"), build_groups(xeno_entries))

    print("rows applied: ThoughtDef=%d MentalBreakDef=%d XenotypeDef=%d (total %d of %d)"
          % (stats["ThoughtDef"], stats["MentalBreakDef"], stats["XenotypeDef"],
             sum(stats.values()), len(prose)))
    print("thought stage-write ops:", len(thought_entries))
    print("skipped (%d):" % len(skipped))
    for k, why in skipped:
        print("  ", k, "-", why)


if __name__ == "__main__":
    sys.exit(main())
