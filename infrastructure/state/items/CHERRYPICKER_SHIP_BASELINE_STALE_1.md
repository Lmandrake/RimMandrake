# CHERRYPICKER_SHIP_BASELINE_STALE_1

## What was found (offline research, 2026-09-10)

`cherrypicker_swap.py --status` reports the live Cherry Picker config
(`Mod_3521312241_Mod_CherryPicker.xml`, edited only through the mod's own
in-game UI) as **UNRECOGNISED** — it matches neither tracked snapshot:

- **SHIP** (`infrastructure/state/cherrypicker/CherryPicker.SHIP.xml`,
  captured 2026-09-02): 1,509 keys — the campaign's real, ratified cut list.
- **REVIEW** (0 keys): deliberately empty, used to make everything
  spawnable for review/def-dump sheets.
- **LIVE**: 1,948 keys, dated 2026-09-09 22:26 (this same session's evening)
  — not a superset or subset of SHIP.

## The drift, broken down

- **+617 keys** (mostly ResearchProjectDef 120, RecipeDef 81, ThingDef 354)
  — almost entirely `AM_*`/`Administer_AM_*` keys belonging to
  `sarg.alphamechs` (active in the live modlist). This maps cleanly onto
  tonight's droid/mech consolidation work — looks like real, deliberate
  curation.
- **−178 keys** (un-cut) — most strikingly, `BackstoryDef` went from 141
  cuts in SHIP down to 10 in LIVE: **essentially all of SHIP's backstory
  cuts were reversed.** Plus ~30 ThingDef un-cuts, mostly turret mods
  (`BMAD_GrowthTurret`, `FT_AutoCannon`, `Turret_AncientArmoredTurret`,
  `Metalhorror`, `Trispike`, etc.) and a few PawnKindDef/TraitDef.

## Why this wasn't auto-resolved

`cherrypicker_swap.py --capture-ship --apply` would pass the tool's own
safety guard (1,948 is nowhere near <50% of 1,509) — mechanically safe to
run. **Not run**, because the drift bundles at least two distinct decisions
this pass could not independently confirm are both final:
1. The Alpha Mechs research/recipe additions — plausibly a clean, intended
   cut from tonight's work.
2. The near-total backstory un-cut — this could be a deliberate reversal,
   OR an in-progress review-window artifact (someone testing something in
   Cherry Picker's live UI and not finished), OR accidental. SHIP is a
   curated, ratified artifact under this project's frozen-artifact
   doctrine — re-baselining it should not bundle in an unconfirmed reversal.

## What needs to happen

Someone (owner or whoever did the backstory work, if it was deliberate)
confirms:
- The backstory un-cut is intentional and final → then
  `python3 src/RimMandrake/Utils/cherrypicker_swap.py --capture-ship --apply`
  adopts LIVE as the new SHIP baseline, closing this item.
- The backstory un-cut was NOT intentional (a review-window leftover) →
  fix it back via Cherry Picker's own UI first, THEN capture.

## verify

`cherrypicker_swap.py --status` reports LIVE == SHIP (or a fresh,
deliberate SHIP) with no UNRECOGNISED state.
