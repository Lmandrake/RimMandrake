#!/usr/bin/env python3
"""validate_save_artifact.py — resolve every def reference in a RimWorld
save-side artifact (`.rid` ideoligion, `.xtp` xenotype) against a def dump.

WHY THIS EXISTS
    `validate_ideoligion.py` reads IdeoPresetDef / FactionDef **XML you author**.
    It answers `no religions found` on a `.rid`, because a `.rid` is Scribe output
    from a running game, not a def file. So the artifacts that matter most had no
    offline validator at all — and an ideoligion BAKES AT WORLD CREATION and
    cannot be retrofitted. Getting this wrong is unrecoverable, not annoying.

THE TRAP THIS TOOL EXISTS TO AVOID (CHECK, 2026-08-15)
    A hand-rolled scrape of `<def>` elements reported 71 missing PreceptDefs.
    Every one was false. A precept `<li>` NESTS other def types inside itself:

        <li Class="Precept_Ritual">
          <def>AM_FuneralNoCorpse</def>              <-- PreceptDef
          <behavior><def>Funeral</def></behavior>    <-- RitualBehaviorDef
          <outcomeEffect><def>AttendedFuneral</def>  <-- RitualOutcomeEffectDef
          <obligationTargetFilter><def>AnyEmptyGrave</def>   <-- ...TargetFilterDef

    Flattening those into one namespace and checking them all against PreceptDef
    produces a wall of confident nonsense.

THE DESIGN RULE THAT PREVENTS IT
    A reference is reported MISSING only when it resolves against **NO def type at
    all**. Expected-type knowledge is used ONLY to raise a separate, softer
    TYPE-MISMATCH class. A wrong guess in the type map can therefore never
    manufacture a false "missing" — the worst it can do is add a mismatch note.
    Absence of evidence gets its own exit path, too: see UNMEASURED below.

WHAT IT DOES NOT DO
    It cannot tell you the ideo LOADS. RimWorld may drop a reference for reasons
    that are invisible on disk (a mod present but failing, a def whose parent
    chain broke). A clean run here means "no dangling names", which is necessary,
    not sufficient. The live check is still one dialog on a scratch map.

USAGE
    python3 src/RimMandrake/Utils/validate_save_artifact.py <file> [<file> ...]
    python3 src/RimMandrake/Utils/validate_save_artifact.py <file> --json
    python3 src/RimMandrake/Utils/validate_save_artifact.py <file> --rebuild-index

EXIT
    0  every reference resolved
    1  at least one reference resolved against no def type  (a real dangling name)
    2  could not measure — no dump, unreadable artifact, empty index
       NEVER conflate 2 with 0. An unmeasured artifact is not a passing one.
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dump_manifest import dump_db          # noqa: E402
from game_paths import DEF_DUMP            # noqa: E402

DUMP = Path(DEF_DUMP)
CACHE = Path(
    os.environ.get("TMPDIR", "/tmp")
) / "rimworld_defindex.json"

# ⚠️ Bump whenever the SHAPE or SOURCE of the index changes. The cache used to
# be keyed on `capturedUtc` alone, which is right for "has the dump moved" and
# wrong for "was this index built by the code now running" — switching between
# the db and the JSON scan against one capture would silently serve the other
# one's index. v2 = db-first, both def_type and concrete_type recorded.
INDEX_VERSION = 2

# ---------------------------------------------------------------------------
# Reference paths, discovered by walking real artifacts rather than guessed.
# The VALUE is advisory only — it can raise a mismatch, never a missing.
# ---------------------------------------------------------------------------
EXPECTED = {
    "/ideo/culture": "CultureDef",
    "/ideo/memes/li": "MemeDef",
    "/ideo/iconDef": "IdeoIconDef",
    "/ideo/colorDef": "ColorDef",
    "/ideo/precepts/li/def": "PreceptDef",
    "/ideo/precepts/li/behavior/def": "RitualBehaviorDef",
    "/ideo/precepts/li/outcomeEffect/def": "RitualOutcomeEffectDef",
    "/ideo/precepts/li/obligationTargetFilter/def": "RitualObligationTargetFilterDef",
    # NOT RitualObligationTargetFilterDef — a different type with near-identical
    # name and overlapping members. Guessing by name cost a run of 11 mismatches.
    "/ideo/precepts/li/targetFilter/def": "RitualTargetFilterDef",
    "/ideo/precepts/li/sourcePattern": "RitualPatternDef",
    "/ideo/precepts/li/nameMaker": "RulePackDef",
    "/ideo/precepts/li/thingDef": "ThingDef",
    "/ideo/precepts/li/apparelDef": "ThingDef",
    "/ideo/precepts/li/attachableOutcomeEffect": "RitualAttachableOutcomeEffectDef",
    "/ideo/precepts/li/chosenPawn/abilities/li/def": "AbilityDef",
    "/ideo/thingStyleCategories/li/category": "StyleCategoryDef",
    "/ideo/style/styleForThingDef/keys/li": "ThingDef",
    "/ideo/style/styleForThingDef/values/li/category": "StyleCategoryDef",
    "/ideo/style/styleForThingDef/values/li/styleDef": "ThingStyleDef",
    "/xenotype/genes/li": "GeneDef",
    "/xenotype/iconDef": "XenotypeIconDef",
}

# Paths whose values LOOK like defNames and are not. Everything here was
# confirmed by eye against a real artifact; do not add on suspicion.
NOT_A_REFERENCE = {
    "/meta/modIds/li",            # provenance manifest, reported separately
    "/meta/modNames/li",          # ditto, human-readable
    "/meta/PrisonLaborVersion",
    "/ideo/adjective",
    "/ideo/memberName",
    "/ideo/name",
    "/ideo/description",
    "/ideo/usedSymbols/li",       # grammar symbols, not defs
    "/ideo/usedSymbolPacks/li",
    "/ideo/foundation/place",     # generated place name
    "/xenotype/name",
    "/xenotype/inheritable",
    # 🔴 The precept's DISPLAY NAME, not its def. "population", "trading",
    # "junk" are single lowercase words that pass every defName shape test and
    # resolve against nothing. Treating them as references produced 73 confident
    # false positives on the first run of this very tool.
    "/ideo/precepts/li/name",
    "/ideo/precepts/li/labelKey",
    "/ideo/precepts/li/presenceDemand/roomRequirements/li/labelKey",
    "/ideo/precepts/li/presenceDemand/roomRequirements/li/buildingTags/li",
    "/ideo/precepts/li/patternGroupTag",   # a tag, not a def
}

# Value patterns that are never a def reference regardless of path.
ENUMS = {
    "True", "False", "null", "Any", "Male", "Female", "None",
    "Never", "Rare", "Uncommon", "Normal", "Frequent", "Always",
    "MaleUsually", "FemaleUsually", "MaleOnly", "FemaleOnly",
    "Neolithic", "Medieval", "Industrial", "Spacer", "Ultra", "Archotech",
    "Low", "Medium", "High", "VeryLow", "VeryHigh", "Ranged", "Melee",
}
# Runtime object handles Scribe writes as cross-references — internal, not defs.
HANDLE = re.compile(r"^(Precept_|Ability_|Thing_|Pawn_)\d+")
DEFNAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]{2,}$")


def _index_from_db():
    """(index, blind_types) off `defs.sqlite`, or None when the db is unusable.

    ⭐ Preferred over the JSON scan for two reasons, and the second is a bug fix:

      * the JSON path reads every `defs/*.json` — 641 MB, `ThingDef.json` alone
        is 316 MB — where this is a single indexed query
      * 🔴 **`defs/` ACCUMULATES.** Nothing prunes it, so it still holds 19 files
        from captures on 2026-08-10…15 whose def types this capture never wrote.
        The JSON scan ingests those dead defNames and a reference to a REMOVED
        def then grades as PROVIDED — fail-toward-success, the one direction
        this tool must never fail in. The db carries `capture.coverage`, so a
        type the manifest never declared is `orphan` and excluded by construction.

    🔑 **`blind` is drawn where the instrument draws it**, not by a heuristic:
    `coverage NOT IN ('complete','ambiguous')`. An `ambiguous` type loaded all
    its rows and is only uncross-checkable by COUNT, so grading a name by
    PRESENCE against it is sound; `shadowed`/`orphan`/`absent`/`failed` are the
    27 that can neither confirm nor deny. The old heuristic — `'"defs":[]'` in
    the first 200 bytes — could only ever see the empty-file case.
    """
    with dump_db(DUMP) as db:
        if db is None:
            return None
        index = {}
        for name, dtype, conc, pkg in db.sql(
                "SELECT def_name, def_type, concrete_type, package_id FROM defs"):
            bucket = index.setdefault(name, [])
            # ⚠️ BOTH types, because they answer different questions and a
            # reference can legitimately name either. `def_type` is the database
            # the def lives in (what a cross-reference resolves against);
            # `concrete_type` is the record's own class, which differs on 1115
            # rows — an AlienBackstoryDef is still in the BackstoryDef database.
            # Keeping only one turns the other into a spurious typeMismatch.
            for t in (dtype, conc):
                entry = [t, pkg or ""]
                if t and entry not in bucket:
                    bucket.append(entry)
        blind = [r[0] for r in db.sql(
            "SELECT def_type FROM capture "
            "WHERE coverage NOT IN ('complete','ambiguous') ORDER BY def_type")]
        return index, blind


def _index_from_json():
    """(index, blind_types) by scanning `defs/*.json`. The fallback, kept so the
    tool still runs where `measuring-large-artifacts` or the db is absent."""
    # Compact single-line JSON — a bounded regex over raw text is ~40x faster
    # than json.load across 663 MB, and we only need four fields per record.
    rec = re.compile(
        r'"defName":"([^"]+)","defType":"([^"]+)",'
        r'"defTypeFull":"[^"]*","label":(?:"(?:[^"\\]|\\.)*"|null),'
        r'"shortHash":-?\d+,"modName":"[^"]*","packageId":"([^"]*)"'
    )
    index, empty_types = {}, []
    for path in sorted((DUMP / "defs").glob("*.json")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        found = rec.findall(text)
        # 🔴 A chunk of the def-type files are EMPTY, so "absent from the dump"
        # does NOT mean "absent from the game" for those types, and grading
        # against them would invent failures. Record them so the report can say
        # UNMEASURABLE instead.
        #
        # === WHY AbilityDef WAS ONE OF THEM ===
        # Not sparsity. RimDefDump keyed defs/<file>.json on the def type's
        # SIMPLE name, and 13 simple names are claimed by two or three unrelated
        # types on this 578-mod stack; the last one written won. Three types are
        # called AbilityDef here (612, 18 and 0 defs) and the empty one went
        # last, so 612 vanilla psycasts and Ideology abilities were written and
        # then overwritten. Fixed 2026-08-21 in RimDefDump/Source/DefDumper.cs
        # (DEFDUMP_ABILITYDEF_BLIND_1) — colliding types now get <FullName>.json
        # and manifest.json carries a defTypes index. ⚠️ Any dump captured
        # BEFORE that fix reaches this machine still has the hole, and its
        # UNMEASURABLE lines are collisions rather than absences.
        if not found and '"defs":[]' in text[:200]:
            empty_types.append(path.stem)
        for name, dtype, pkg in found:
            index.setdefault(name, [])
            entry = [dtype, pkg]
            if entry not in index[name]:
                index[name].append(entry)
    return index, empty_types


def build_index(rebuild=False):
    """defName -> sorted list of (defType, packageId). Cached against the dump's
    own capturedUtc, so a fresh dump invalidates it automatically — never a
    wall-clock TTL, which is the mistake this project has already paid for."""
    manifest = DUMP / "manifest.json"
    if not manifest.exists():
        return None, None
    with open(manifest, encoding="utf-8") as fh:
        meta = json.load(fh)
    stamp = meta.get("capturedUtc", "")

    if CACHE.exists() and not rebuild:
        try:
            with open(CACHE, encoding="utf-8") as fh:
                cached = json.load(fh)
            if (cached.get("capturedUtc") == stamp
                    and cached.get("indexVersion") == INDEX_VERSION):
                # Carry the blind-spot list through the cache too. Dropping it
                # here silently downgrades UNMEASURABLE to MISSING on every
                # cached run — the failure mode this whole tool is against.
                meta["_emptyDefTypes"] = cached.get("emptyDefTypes", [])
                return cached["index"], meta
        except (json.JSONDecodeError, KeyError):
            pass  # corrupt cache is not an error, just rebuild

    built, source = _index_from_db(), "db"
    if built is None:
        built, source = _index_from_json(), "json"
    index, empty_types = built

    meta["_emptyDefTypes"] = sorted(empty_types)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as fh:
        json.dump(
            {"capturedUtc": stamp, "indexVersion": INDEX_VERSION,
             "source": source, "index": index,
             "emptyDefTypes": sorted(empty_types)},
            fh,
        )
    return index, meta


def collect(path):
    """Walk the artifact, returning (refs, empties, mod_ids).

    refs is a list of (xpath, value, occurrence_count-safe order)."""
    tree = ET.parse(path)
    root = tree.getroot()
    refs, empties, mod_ids = [], [], []

    def walk(node, prefix):
        for child in node:
            here = prefix + "/" + child.tag
            text = (child.text or "").strip()
            if here == "/meta/modIds/li" and text:
                mod_ids.append(text.lower())
            if len(child) == 0:
                if not text and prefix.endswith(("Frequencies/vals", "/keys", "/values")):
                    empties.append(here)
                elif (
                    text
                    and here not in NOT_A_REFERENCE
                    and text not in ENUMS
                    and not HANDLE.match(text)
                    and DEFNAME.match(text)
                ):
                    refs.append((here, text))
            walk(child, here)

    walk(root, "")
    return refs, empties, mod_ids


def active_mods():
    cfg = (
        DUMP.parent / "Config" / "ModsConfig.xml"
    )
    if not cfg.exists():
        return None
    text = cfg.read_text(encoding="utf-8-sig", errors="replace")
    # Scope to <activeMods>. A bare <li> count also swallows <knownExpansions>,
    # which duplicates the DLC ids and overcounts by exactly the DLC count.
    block = re.search(r"<activeMods>(.*?)</activeMods>", text, re.S)
    if not block:
        return None
    return {m.strip().lower() for m in re.findall(r"<li>(.*?)</li>", block.group(1))}


def report(path, index, meta, as_json=False):
    try:
        refs, empties, mod_ids = collect(path)
    except (ET.ParseError, OSError) as exc:
        print(f"UNMEASURED  {path}: {exc}", file=sys.stderr)
        return 2, None

    blind = set(meta.get("_emptyDefTypes", []))
    missing, mismatch, unmeasurable, ok = [], [], [], 0
    for xpath, value in refs:
        want = EXPECTED.get(xpath)
        hits = index.get(value)
        # The dump carries no rows at all for this type, so it can neither
        # confirm nor deny. Not a pass, not a failure — a hole in the evidence.
        if want in blind:
            unmeasurable.append({"path": xpath, "name": value, "type": want})
            continue
        if not hits:
            missing.append({"path": xpath, "name": value})
            continue
        ok += 1
        if want and not any(h[0] == want for h in hits):
            mismatch.append(
                {"path": xpath, "name": value, "expected": want,
                 "found": [h[0] for h in hits]}
            )

    live = active_mods()
    dropped = sorted(set(mod_ids) - live) if (live and mod_ids) else []

    result = {
        "file": str(path),
        "dumpCapturedUtc": meta.get("capturedUtc"),
        "referencesChecked": len(refs),
        "resolved": ok,
        "missing": missing,
        "typeMismatch": mismatch,
        "unmeasurable": unmeasurable,
        "dumpEmptyDefTypes": len(meta.get("_emptyDefTypes", [])),
        "emptyListEntries": len(empties),
        "provenanceModIds": len(mod_ids),
        "provenanceNoLongerActive": dropped,
    }
    if as_json:
        return (1 if missing else 0), result

    name = Path(path).name
    print(f"\n=== {name}")
    print(f"    dump captured {meta.get('capturedUtc')}  ({len(index)} defNames indexed)")
    print(f"    {ok}/{len(refs)} references resolve")
    if missing:
        print(f"    🔴 {len(missing)} RESOLVE AGAINST NO DEF TYPE — dangling:")
        for m in missing:
            print(f"        {m['name']}   at {m['path']}")
    if mismatch:
        print(f"    ⚠️  {len(mismatch)} resolve but not as the expected type:")
        for m in mismatch:
            print(f"        {m['name']}  expected {m['expected']}, found {m['found']}  at {m['path']}")
    if unmeasurable:
        by_type = {}
        for u in unmeasurable:
            by_type.setdefault(u["type"], []).append(u["name"])
        print(f"    ⬜ {len(unmeasurable)} UNMEASURABLE — the dump carries zero rows for their type.")
        print("       Not a pass and not a failure. Only a live check settles these.")
        for t, names in sorted(by_type.items()):
            print(f"        {t}: {', '.join(sorted(set(names)))}")
    if empties:
        # NOT a warning. Vanilla `Technocracy.rid` shows the same shape (22 empty
        # in hairFrequencies, 11 in beardFrequencies) — Scribe writes `<li />`
        # for a default-valued entry. Reported as a count only, so nobody
        # re-investigates it. CHECK confirmed 2026-08-15 by direct comparison.
        print(f"    ·  {len(empties)} empty <li> (normal Scribe output — vanilla ideos "
              f"have them too; not a defect)")
    if mod_ids:
        print(f"    provenance: {len(mod_ids)} modIds captured at save time")
        if dropped:
            print(f"                {len(dropped)} no longer active — PROVENANCE ONLY,")
            print(f"                not a defect unless a reference above is missing:")
            for d in dropped:
                print(f"                    {d}")
    if not missing:
        print("    ✅ no dangling names")
    return (1 if missing else 0), result


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="+", help=".rid / .xtp artifacts to check")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--rebuild-index", action="store_true")
    args = ap.parse_args()

    index, meta = build_index(rebuild=args.rebuild_index)
    if not index:
        print(
            f"UNMEASURED: no usable def dump at {DUMP}. "
            "Arm one with `echo all > .../DefDump/dump_request.txt` and load the game. "
            "This is exit 2, NOT a pass.",
            file=sys.stderr,
        )
        return 2

    worst, blobs = 0, []
    for f in args.files:
        code, blob = report(Path(f), index, meta, as_json=args.json)
        worst = max(worst, code)
        if blob:
            blobs.append(blob)
    if args.json:
        print(json.dumps(blobs, indent=2))
    return worst


if __name__ == "__main__":
    sys.exit(main())
