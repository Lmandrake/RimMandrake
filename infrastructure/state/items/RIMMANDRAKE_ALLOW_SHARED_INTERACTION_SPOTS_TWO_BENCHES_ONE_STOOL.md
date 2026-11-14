# RIMMANDRAKE_ALLOW_SHARED_INTERACTION_SPOTS_TWO_BENCHES_ONE_STOOL

## spec

Owner, live look 2026-11-14 about 11:30 AM to 12:10 PM PST (finding 2, `D:\ClaudeWork\rimmandrake\conductor\sitting_20261114\OWNER_LOOK_WORDS.md`):

> "I noted that you couldn't overlap two interaction spots for furniture. Could we patch it so that you can? This would be put in some other RimMandrake mod I presume."

What blocks it in vanilla. RimSage was unavailable, so this was read from the decompile at `D:\ClaudeWork\rimmandrake\decomp\rw16\all\RimWorld`:
- `RimWorld.PlaceWorker_PreventInteractionSpotOverlap.AllowsPlacing` refuses with "InteractionSpotOverlaps" or "InteractionSpotWillOverlap" when the new building's interaction cell equals the interaction cell of an existing (or blueprinted) building. It scans the things within 1 cell of each interaction cell.
- The official def dump (August 2026) shows that placeworker on 476 ThingDefs. A sanity probe found 16108 ThingDefs carrying some `PlaceWorker_`. Examples are TableButcher, HandTailoringBench and CraftingSpot.
- `GenConstruct` adds two more rules that are not this one and stay:
  - `InteractionCellStandable`: nothing impassable may sit on an interaction cell.
  - `NotBlockingAnyInteractionCells`: a new building may not stand on another's spot.

Likely fix: a Harmony prefix that makes `PlaceWorker_PreventInteractionSpotOverlap.AllowsPlacing` return Accepted (behind a setting, default on). Removing the placeworker from 476 defs by XML patch would be the wrong route.
- Then check that two pawns working benches that share one spot queue rather than stack. The vanilla reservation is on the bench, not the cell, so two workers can stand on one cell; this needs a live look.

Home mod: his words say "some other RimMandrake mod". Which one is not decided here; it is not FlowWorks.

Design Version class: PROPOSED Polish (an owner call).

Build effort: small.

Acceptance test (offline, a local model could run it): a selftest loads the patched assembly's Harmony targets and asserts a prefix on `RimWorld.PlaceWorker_PreventInteractionSpotOverlap.AllowsPlacing` that returns Accepted while the setting is on and defers to vanilla while it is off. The vanilla `InteractionCellStandable` refusal must stay unpatched.
