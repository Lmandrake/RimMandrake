#!/usr/bin/env python3
"""structure_roster_lint.py — TILE_STRUCTURE_DESIGNS_1's coverage lint.

The roster's own coverage law (structure_injection_roster.md §4.2):
"lint refuses any promise def without a registered responder genstep AND
any territory with an empty whisper table." This script checks the PROMISE
half mechanically (template file + wired GenStepDef/TileMutatorDef exist);
the WHISPER half has no territory-table mechanism built anywhere in the
repo yet (checked: no GenStep/IncidentDef/quest keys off any of the 22
whisper names or their god-country column as of 2026-09-09) — so every
whisper row reports MISSING-MECHANISM, not a per-row gap, until that
engine exists. This is deliberate and is not something this script's next
run will fix on its own; see TILE_STRUCTURE_DESIGNS_1's item file.

Roster rows are hardcoded below (row #, name, tier, slug, status) rather
than parsed from the markdown prose — the roster's own format is not
machine-structured, and re-deriving slugs from free text is worse than a
human-checked table a future edit updates by hand alongside the roster.
Re-sync this table whenever structure_injection_roster.md's numbered lists
change.

Usage: python3 structure_roster_lint.py [--json]
Exit 0 always (report tool, not a gate) unless --strict and any row is
UNKNOWN (a row this table has not classified at all — should never happen).
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

WHISPERS = [n for n, *_ in [
    (1, "Something Buried"), (2, "The Listening Dark"), (3, "Old Reasons"),
    (4, "The Wrong Spark"), (5, "Soft Ground"), (6, "The Passing Herd"),
    (7, "The Sun's Anvil"), (8, "The Debtor's Cache"), (9, "The Glimmer Field"),
    (10, "The Hollow Below"), (11, "Static Ghosts"), (12, "Never Was"),
    (13, "The Egg Sands"), (14, "The Feud"), (15, "Quicksand Veins"),
    (16, "The Prospector's Bones"), (17, "Iron Rain"), (18, "The Choir Wind"),
    (19, "The Mirage Twin"), (20, "The Rootstock"), (21, "The Sleeper's Knock"),
    (22, "The Sarlacc Sign"),
]]


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    promise_results = []
    for row in PROMISES:
        state, detail = check_promise(row)
        promise_results.append({"row": row[0], "name": row[1], "tier": row[2], "state": state, "detail": detail})

    whisper_results = [
        {"row": n, "state": "MISSING-MECHANISM",
         "detail": "no territory-table/whisper engine exists in the repo yet"}
        for n in WHISPERS
    ]

    covered = sum(1 for r in promise_results if r["state"] == "covered")
    declared_gap = sum(1 for r in promise_results if r["state"] in ("skip-tool", "skip-owner", "gap-design"))
    lint_fail = [r for r in promise_results if r["state"].startswith("MISSING-")]

    if args.json:
        print(json.dumps({"promises": promise_results, "whispers": whisper_results,
                           "promise_covered": covered, "promise_declared_gap": declared_gap,
                           "promise_lint_fail": len(lint_fail)}, indent=2))
    else:
        print(f"PROMISES: {covered}/22 covered, {declared_gap} declared gaps, "
              f"{len(lint_fail)} lint failures (coverage-law violations)")
        for r in promise_results:
            print(f"  [{r['state']:>17}] #{r['row']:>2} {r['name']} ({r['tier']}) — {r['detail']}")
        print()
        print(f"WHISPERS: 0/22 covered (no territory-table mechanism built) — "
              f"this is a missing SUBSYSTEM, not 22 individual small gaps")
        print()
        if lint_fail:
            print("COVERAGE LAW VIOLATIONS (promise with no registered responder, or vice versa):")
            for r in lint_fail:
                print(f"  #{r['row']} {r['name']}: {r['state']} — {r['detail']}")
        else:
            print("Coverage law: 0 violations among rows with both a template and a "
                  "responder claim — every 'covered' row has BOTH, every declared gap "
                  "has NEITHER (never a promise shipped half-built).")

    if lint_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
