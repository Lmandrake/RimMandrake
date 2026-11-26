# WB-game-campaign-events-20261126-165518: onboarding run of game:campaign-events

State: finished. Every member has its outcome. Nothing is left for a restart.

## Step A, the reality sort (done, 2026-11-26)

| member | class | outcome |
|---|---|---|
| `DUST_SETTLED_LETTER_1` | stale | dropped: built at e60e5519bd; its one owed live check (`horizon_dust_settled_letter`) is in the held Stillsand mod's own record, `design/concepts/Stillsand/record.json` |
| `GM_BLACKBOARD_SHADOW_M4_1` | stale | dropped: built at f0015adbe2d4 and run live 2026-09-13; A1 is replaced by in-game kyber heat (`KyberTrade.cs`, 5e0112a0f0), A2 belongs to RustCathedral cleanse ticket T23 |
| `SEKKULAATH_RISING_DESIGN_CRATER_EVENT` | needs a judge | shaped: effect `sekkulaath_rising_note_check.py` (red today on the judge round only) and a route to a fresh section 4 judge. Stale `RUT_` names in the note, its item and the kit spec fixed at 989a6b58cc06 |
| `FALLZONE_LOST_CARGO_QUESTS_1` | needs the Conductor | shaped: one route, a choice between goals (owed v1 work or a lead only); recommendation Option A of the draft at `git show 3e2aca82:Transient/fallzone_lost_cargo_quests_draft_2026-10-09.md` |
| `SEKKULAATH_RISING_BUILD_THE_LAMPS_GO_OUT` | blocked | `block --on SEKKULAATH_RISING_DESIGN_CRATER_EVENT --on WARLAB_GARRISON_BUILD_TWELVE_MEN_ON_GLASS --until built`; `REFUSED BY BUNDLE:` note. Also touches FeverWood, held by the owner |
| `CRATER_CUTSCENE_BUILD_NOBODY_HELD_THE_REEL` | blocked | the same block on the same two items; `REFUSED BY BUNDLE:` note. No cut-scene design exists beyond the Fever Wood beat; write it first when unblocked |

## Steps B and C

No member was kept, so no check was written and no fix was owed.

## What a later run must know

- The crater chain is: the garrison design's round 3 blind check, then `WARLAB_GARRISON_BUILD_TWELVE_MEN_ON_GLASS`
  (it adds the `Ignited` event, which does not exist in `src/` today), then the sekkulaath judge, then the two builds.
- The cut-scene's own design (a beat for every region, the player, the art) is unwritten. When the block lifts, the
  first act is that design and its judge, not code.
