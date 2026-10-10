# First look: before any theory, capture the scene

Map awareness phase 1d (`VISITOR_DETECTORS_MEND_NAME_THE_STRANGER`, 2026-10-10). Protocol from GPT review §6 of
`Transient/foundry_map_awareness_review_gpt_20261010.md` (Transient: ~14-day shelf life; everything that binds is
restated here). It extends, and does not compete with, `rimworld-debug-testing`'s "look before you theorise".

**Why:** Player.log records no incident firing and no pawn arriving (measured over three logs, 2026-10-10). The
only way to know who is on the map, and what we know about why, is to read the map, and to read it **before**
changing it.

## The seven steps

1. **Identity and timing.** Game/load, map, tick, paused?, which companion build is deployed. Take the bridge
   lease first (`rimflow bridge take --for "..."`).
2. **Capture the scene before touching anything.**
   `python.exe src/RimMandrake/Utils/modcheck/scene_report.py --anchor X,Z --out <file>` — every pawn with
   faction, decomposed hostility, target, lord, receipts, and its coverage gaps. Not atomic; it says so.
   A modcheck `Watch` writes one automatically before its timed stage (`<mod>_<chain>_scene_baseline.json`).
3. **Resolve the subject exactly** by its id. Read the ACTUAL kind and race; never repeat the kind you asked for
   (E5: 4 of 80 spawns came back a vanilla Colonist). Spawn receipts carry `requestedKind`, `toolKinds` and an
   independent `readBackKinds`.
4. **Check the receipts and the test's contract.** Was it ours (`ourInvolvement`)? Was it declared
   (`expectation`)? The two are independent: our own fired raid is `confirmedIndirectAction` + `expected`.
5. **State facts and uncertainty separately.** Identity, current aggression, letter association, generation
   evidence and delivery evidence are five different claims. Say **"origin unknown"** where nothing recorded it.
6. **Validity before continuing.** In a validation/north-star run the owner's rule applies (question card
   2026-10-10): an unexpected visitor is **recorded and removed** and the run carries on as **CLEAN** with a note;
   only **evidence** that it attacked, targeted or hunted a colonist or test subject makes it **DISRUPTED** (a
   redo); a failed observation makes it **INDETERMINATE**. `modcheck/watch.py` does this itself.
7. **Only then a hypothesis.** The smallest probe that distinguishes, read back, then a fresh scene report at
   the boundary. Never delete unexplained evidence before step 2 captured it.

## What you may say, and what you may not

| evidence | allowed | forbidden upgrade |
|---|---|---|
| present when recording started | "present at baseline; origin unknown" | "mapgen pawn" |
| no generation tag after a load | "provenance unavailable across load" | "generated before load" |
| raid-style lord/job | "currently organised for assault" | "created by a storyteller raid" |
| named by a letter's look targets | "associated with this letter" | "this letter/incident created it" |
| appeared near an incident | "appeared in this interval; possible association" | "caused by incident X" |
| vanilla kind or texture | "uses a vanilla definition/asset" | "vanilla initiated its arrival" |
| a foreign assembly on the stack | "this assembly participated" | "this mod caused the pawn" |
| bridge context around generation | "generated/selected during our operation" | "newly created and intentionally spawned by us" |
| old id seen after the mark | "newly observed on this map" | "newly created" |
| no event rows | "no retained observations" | "no arrivals occurred" |

## What the report cannot see (yet)

- **Held pawns** (containers, holding platforms, cryptosleep, transporters, caravans, world pawns): not covered.
- **Dormant** pawns are listed when spawned but not marked dormant.
- **Letter association** needs look-target ids from the companion (`letter_list` printed `LookTargets.ToString()`,
  which LookTargets does not override: VERIFIED via RimSage). Until deployed it reads `unavailable`.
- **Origin** needs the origin recorder (`PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN`); until deployed every origin is unknown.
