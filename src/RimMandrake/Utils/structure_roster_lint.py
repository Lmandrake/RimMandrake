#!/usr/bin/env python3
"""structure_roster_lint.py — TILE_STRUCTURE_DESIGNS_1's coverage lint.

The roster's own coverage law (structure_injection_roster.md §4.2):
"lint refuses any promise def without a registered responder genstep AND
any territory with an empty whisper table." This script checks the PROMISE
half mechanically (template file + wired GenStepDef/TileMutatorDef exist).

The WHISPER half had NO territory-table mechanism anywhere in the repo as
of 2026-09-09 (checked: no GenStep/IncidentDef/quest keyed off any of the
22 whisper names or their god-country column) — every row reported
MISSING-MECHANISM. As of the 2026-09-12 whisper batch 1, the mechanism now
EXISTS and is used by 3 rows: a whisper rides an EXISTING TileMutatorDef
(the tile's own territory, patched via a Patches/*.xml operation) whose
extraGenSteps points at a GenStepDef wrapping vanilla
Verse.GenStep_RandomSelector — no new C# for the roll itself, only for the
one "inject nothing" option (GenStep_Whisper_NoOp). Every row not yet
picked up still reports MISSING-MECHANISM, honestly, one row at a time —
this is not a subsystem flip from 0 to done, it is 3/22 rows wired with a
real, working mechanism and 19 still open. See TILE_STRUCTURE_DESIGNS_1's
item file for the running tally.

Roster rows are hardcoded below (row #, name, tier/mutator, slug, status)
rather than parsed from the markdown prose — the roster's own format is
not machine-structured, and re-deriving slugs from free text is worse than
a human-checked table a future edit updates by hand alongside the roster.
Re-sync this table whenever structure_injection_roster.md's numbered lists
change.

Usage: python3 structure_roster_lint.py [--json]
Exit nonzero whenever any promise row is MISSING-RESPONDER, MISSING-TEMPLATE
or MISSING-BOTH, or any whisper row declared "done"/"done-noop" is missing
its template, genstep or patch (a coverage-law violation) — exit 0 on a
clean run. A whisper row still marked "no-mechanism" is NOT a lint failure;
it is the honest, declared, not-yet-attempted default. There is no
--strict flag; every lint failure gates the exit code, always.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TEMPLATES = ROOT / "design/Jawa/templates"
TIER_DIRS = {
    "RM": ROOT / "src/RimMandrake/StructureInjections",
    "RSW": ROOT / "src/RimStarWars/StructureInjectionsSW",
    "RUT": ROOT / "src/RimUtinni/StructureInjectionsRUT",
}

# status: "done" (template + responder both verified present below),
# "skip-tool" (needs a different pipeline than rimplace templates),
# "skip-owner" (contested / needs an owner ruling before authoring),
# "gap" (roster fully specifies a NEW small thing but nobody has built it —
#        candidate for a future mechanical batch),
# "gap-design" (roster names it but leaves the actual content underspecified —
#        NOT safe to fill without inventing).
PROMISES = [
    (1, "The Moisture Farm", "RSW", "moisture_farm", "done"),
    (2, "The Sarlacc", "RSW", None, "gap-design"),  # adopt existing sw_Sarlacc/sw_SarlaccLair + "responder polish" — no template of ours exists; the existing mutator's pit geometry is a different mod's content we've never inspected for a ring-placement, so ring geometry is a real, unmade design choice
    (3, "The Krayt Graveyard", "RSW", "krayt_graveyard", "done"),
    (4, "The Podracer Wreck", "RSW", "podracer_wreck", "done"),
    (5, "The Junkers' Field", "RUT", None, "skip-tool"),  # needs coastal_mesa-style mapsynth pass, not a rimplace template — batch 6 note
    (6, "The Dead Crawler", "RSW", None, "gap-design"),  # "flagship... three interior decks" has no concrete layout anywhere
    (7, "The Signal Mast", "RM", None, "gap-design"),  # "our comms-console room" — room layout never specified
    (8, "The Monument", "RUT", "monument", "done"),
    (9, "The Rakatan Trace", "RUT", "rakatan_trace", "done"),
    (10, "The Oasis Shrine", "RUT", "oasis_shrine", "done"),
    (11, "The Kiln", "RUT", None, "skip-owner"),  # contested per sacred-sites (Ohm vs Sh'kaar) — batch 6 note
    (12, "The Hunting Lodge", "RSW", "hunting_lodge", "done"),
    (13, "The Toll Gap", "RUT", "toll_gap", "done"),
    (14, "The Dead Beacon", "RUT", "dead_beacon", "done"),
    (15, "The Bantha Graveyard", "RSW", "bantha_graveyard", "done"),
    (16, "The Glass Sea", "RUT", "glass_sea", "done"),
    (17, "The Ashfall Battery", "RUT", None, "gap-design"),  # "our fuel-farm room" onto existing AncientLaunchSite — room layout never specified
    (18, "The Mynock Roost", "RSW", "mynock_roost", "done"),
    (19, "The Cistern", "RUT", "cistern", "done"),
    (20, "The Broken Ring", "RUT", "broken_ring", "done"),
    (21, "The Imperial Waystation", "RUT", "imperial_waystation", "done"),
    (22, "The Homestead", "RUT", "homestead", "done"),  # built under INHABITED_AUGMENTATION_BUILD_1 (abode/homestead/compound), not this item's own batches — verified live in-tree, not re-authored here
]

# WHISPERS mirror PROMISES' shape, with a "mutator" column instead of a
# slug: a whisper is not authored per-tile (no owner placement), it rides
# whichever EXISTING TileMutatorDef is already the tile's territory
# (structure_injection_roster.md §3's own parenthetical, or - for rows
# that name an existing PROMISE mutator's own gating, e.g. "monument
# reads" - that promise's own TileMutatorDef). slug=None + mutator set +
# status="done-noop" is the one legal "nothing injected" case (WHISPER #12
# Never Was) - no template file exists for it by design.
#
# status: "done" (template/no-op + wired GenStepDef + patch onto the named
#          mutator, all verified present below), "no-mechanism" (the
#          territory-table/selector engine did not exist for this row as
#          of the batch that built it - the honest default for every row
#          not yet picked up).
WHISPERS = [
    (1, "Something Buried", None, None, "no-mechanism"),
    (2, "The Listening Dark", None, None, "no-mechanism"),
    (3, "Old Reasons", None, None, "no-mechanism"),
    (4, "The Wrong Spark", None, None, "no-mechanism"),
    (5, "Soft Ground", None, None, "no-mechanism"),
    (6, "The Passing Herd", None, None, "no-mechanism"),
    (7, "The Sun's Anvil", None, None, "no-mechanism"),
    (8, "The Debtor's Cache", None, None, "no-mechanism"),
    (9, "The Glimmer Field", None, None, "no-mechanism"),
    (10, "The Hollow Below", None, None, "no-mechanism"),
    (11, "Static Ghosts", None, None, "no-mechanism"),
    (12, "Never Was", None, "Cavern", "done-noop"),
    (13, "The Egg Sands", None, None, "no-mechanism"),
    (14, "The Feud", None, None, "no-mechanism"),
    (15, "Quicksand Veins", None, None, "no-mechanism"),
    (16, "The Prospector's Bones", None, None, "no-mechanism"),
    (17, "Iron Rain", None, None, "no-mechanism"),
    (18, "The Choir Wind", "choir_wind", "RUT_Monument", "done"),
    (19, "The Mirage Twin", None, None, "no-mechanism"),
    (20, "The Rootstock", "rootstock", "DryLake", "done"),
    (21, "The Sleeper's Knock", None, None, "no-mechanism"),
    (22, "The Sarlacc Sign", None, None, "no-mechanism"),
]


def template_exists(slug):
    return slug is not None and (TEMPLATES / f"{slug}.lua").exists()


def responder_exists(tier, slug):
    if slug is None:
        return False
    d = TIER_DIRS.get(tier)
    if d is None or not d.exists():
        return False
    plan_ref = f"Templates/{slug}.txt"
    for genstep_file in (d / "Defs").glob("GenStepDefs*.xml"):
        try:
            text = genstep_file.read_text(encoding="utf-8")
        except OSError:
            continue
        if plan_ref in text:
            return True
    return False


def check_promise(row):
    n, name, tier, slug, status = row
    if status in ("skip-tool", "skip-owner", "gap-design"):
        return status, f"declared {status}, not a lint failure"
    has_tpl = template_exists(slug)
    has_resp = responder_exists(tier, slug)
    if has_tpl and has_resp:
        return "covered", f"{slug}.lua + wired responder in {tier}"
    if has_tpl and not has_resp:
        return "MISSING-RESPONDER", f"{slug}.lua exists, no GenStepDef references Templates/{slug}.txt"
    if has_resp and not has_tpl:
        return "MISSING-TEMPLATE", f"responder wired but design/Jawa/templates/{slug}.lua absent"
    return "MISSING-BOTH", "no template, no responder"


# A whisper's "responder" is a GenStepDef somewhere under any tier's Defs/
# wrapping GenStep_RandomSelector, with an option resolving either to the
# template's compiled plan (Templates/<slug>.txt) or - for a no-op row -
# to GenStep_Whisper_NoOp. Its "wiring" is a Patches/*.xml operation whose
# value/xpath names BOTH the target mutator and that GenStepDef's own
# defName, in any tier (whispers ride an EXISTING mutator, so the
# TileMutatorDef itself was never authored by this program the way a
# promise's is - there is nothing to check under Defs/TileMutatorDefs* for
# a whisper, only the Patches/ file that reaches into the mutator that
# already exists elsewhere).
def whisper_genstep_exists(slug):
    needle = "GenStep_Whisper_NoOp" if slug is None else f"Templates/{slug}.txt"
    for tier_dir in TIER_DIRS.values():
        if not tier_dir.exists():
            continue
        for genstep_file in (tier_dir / "Defs").glob("GenStepDefs*.xml"):
            try:
                text = genstep_file.read_text(encoding="utf-8")
            except OSError:
                continue
            if needle in text and "GenStep_RandomSelector" in text:
                return True
    return False


def whisper_patch_wires_mutator(mutator):
    if mutator is None:
        return False
    for tier_dir in TIER_DIRS.values():
        patches_dir = tier_dir / "Patches"
        if not patches_dir.exists():
            continue
        for patch_file in patches_dir.glob("*.xml"):
            try:
                text = patch_file.read_text(encoding="utf-8")
            except OSError:
                continue
            if f'defName="{mutator}"' in text:
                return True
    return False


def check_whisper(row):
    n, name, slug, mutator, status = row
    if status == "no-mechanism":
        return "MISSING-MECHANISM", "no territory-table/whisper engine wired for this row yet"
    has_genstep = whisper_genstep_exists(slug)
    has_patch = whisper_patch_wires_mutator(mutator)
    if status == "done-noop":
        if has_genstep and has_patch:
            return "covered", f"GenStep_Whisper_NoOp wired onto {mutator} via GenStep_RandomSelector"
        return "MISSING-RESPONDER" if has_patch else "MISSING-PATCH", \
            f"no-op row declared done but genstep={has_genstep} patch={has_patch}"
    # status == "done" (content-bearing)
    has_tpl = template_exists(slug)
    if has_tpl and has_genstep and has_patch:
        return "covered", f"{slug}.lua + selector GenStepDef + patch onto {mutator}"
    missing = []
    if not has_tpl:
        missing.append("template")
    if not has_genstep:
        missing.append("genstep")
    if not has_patch:
        missing.append("patch")
    return "MISSING-" + "+".join(missing).upper(), f"declared done but missing: {', '.join(missing)}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    promise_results = []
    for row in PROMISES:
        state, detail = check_promise(row)
        promise_results.append({"row": row[0], "name": row[1], "tier": row[2], "state": state, "detail": detail})

    whisper_results = []
    for row in WHISPERS:
        state, detail = check_whisper(row)
        whisper_results.append({"row": row[0], "name": row[1], "mutator": row[3], "state": state, "detail": detail})

    covered = sum(1 for r in promise_results if r["state"] == "covered")
    declared_gap = sum(1 for r in promise_results if r["state"] in ("skip-tool", "skip-owner", "gap-design"))
    lint_fail = [r for r in promise_results if r["state"].startswith("MISSING-")]

    w_covered = sum(1 for r in whisper_results if r["state"] == "covered")
    w_no_mechanism = sum(1 for r in whisper_results if r["state"] == "MISSING-MECHANISM")
    w_lint_fail = [r for r in whisper_results if r["state"].startswith("MISSING-") and r["state"] != "MISSING-MECHANISM"]

    if args.json:
        print(json.dumps({"promises": promise_results, "whispers": whisper_results,
                           "promise_covered": covered, "promise_declared_gap": declared_gap,
                           "promise_lint_fail": len(lint_fail),
                           "whisper_covered": w_covered, "whisper_no_mechanism": w_no_mechanism,
                           "whisper_lint_fail": len(w_lint_fail)}, indent=2))
    else:
        print(f"PROMISES: {covered}/22 covered, {declared_gap} declared gaps, "
              f"{len(lint_fail)} lint failures (coverage-law violations)")
        for r in promise_results:
            print(f"  [{r['state']:>17}] #{r['row']:>2} {r['name']} ({r['tier']}) — {r['detail']}")
        print()
        print(f"WHISPERS: {w_covered}/22 covered, {w_no_mechanism} rows with no territory-table "
              f"mechanism wired yet, {len(w_lint_fail)} lint failures among rows claiming 'done'")
        for r in whisper_results:
            print(f"  [{r['state']:>17}] #{r['row']:>2} {r['name']} ({r['mutator']}) — {r['detail']}")
        print()
        if lint_fail or w_lint_fail:
            print("COVERAGE LAW VIOLATIONS (promise/whisper with no registered responder, or vice versa):")
            for r in lint_fail:
                print(f"  PROMISE #{r['row']} {r['name']}: {r['state']} — {r['detail']}")
            for r in w_lint_fail:
                print(f"  WHISPER #{r['row']} {r['name']}: {r['state']} — {r['detail']}")
        else:
            print("Coverage law: 0 violations among rows with both a template and a "
                  "responder claim — every 'covered' row has BOTH, every declared gap "
                  "has NEITHER (never a promise shipped half-built).")

    if lint_fail or w_lint_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
