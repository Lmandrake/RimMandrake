# FOUNDRY_HANDOFF_202610181652 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610180431`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Sun 2026-10-18 morning the owner ruled by question card (all recorded as notes on FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG, pushed): shallow drowning stays default-on; pit room = 3.0 m scaled by body size (reach plus jump; replaces the flat "superdeep only"); hose leftover spills as REAL water (wets ground, feeds plants), not just filth; lakes: river or off-map always limitless, else limitless above a per-biome wetness cell cutoff (about 600 wet, 5000 temperate, never by size in dry), the rest self-refill from groundwater, limitless means no sloped floor; dig cost curve kept (V1); falls by metres and deep falls CAN kill (V3); shooting blocked by ground above a person's height (V5); spikes at sheer 2 m drops (V4); red alert for a colonist stuck in a pit; delete sourceBudgetMultiplier (D4); readout "Hole 7 m (ledge 4 m) · Water 2.37 m (4,740 L)" (V8); fish in dug water yes; NO beach ring (drained = dry; remove the 0.5 m ring default). None of this is coded yet. Disk hit 100% on / this morning (scratch clones are 16-23 GB each, 370 GB total): delete finished clones under /home/mandrake/rm/scratch/FOUNDRY/ before any build.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Six open questions at the end of `D:\Luke\dev\RimMandrake\design\RimMandrake\big_creatures_walls_and_slots_2026-10-18.md` (design pass plus GPT review, published d9ecc1312).
- Art he must LOOK at: the water art candidates sheet and lake-floor panels (paths in the previous handoff); V7 (floor bands, wall looks) waits on that.
- Re-validate five north-star bars in one sitting (FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING); still_water_one_surface_height needs a covering walk row first.
- Still unasked: D3 (one burn rate), shallow-lake depth ruling, Q9 plants on dug ground, donor rulings (DONOR_ROSTER_GUARDS_FIX_WRONG_PACKAGE_ID, DONOR_SUCCULENT_ART_DECIDE_A_STAND_IN).
- Overnight offline code review (published ca292442f, 26a47408f, ea44bf795): 5 real bugs fixed (dig scan collection-modified, pump-circle warning, very-shallow tier check, swept-away letter pronoun, northstar proof reset bound). Open doubt: Building_LiquidPump.TryPour checks room in whole notches while TryDraw and Outlet use decilitres, so exact-level mode may skip pond and outflow routes.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `LAKE_GROUNDWATER_REFILL_BUILD_WETNESS_CUT` — filed, design ruled; NEXT: claim it, read the real pump rate from Building_LiquidPump / RM_PumpMath, then set the per-biome wetness cutoffs and groundwater refill.
- `FALL_GUARDRAILS_BUILD_REAL_OBJECT` — filed; NEXT: claim it and make deep falls lethal (V3) plus a guardrail building with existing fences acting as rails.
- `RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP` — filed, needs bridge; NEXT: claim it when the bridge is free and build go-around, breach, jump-pack and pre-built-ladder raider behaviour.
- `PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS` — filed; NEXT: claim it and design the wall ladder, carryable ladder, climbing gear, wall scaling and jump/teleport entry.
- `BIG_CREATURES_DESIGN_WALLS_AND_SLOTS` — design published d9ecc1312; NEXT: put its six owner questions to him as cards, then file build children.
- `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` — rulings above not yet coded (3.0 m scaled pit room, spill-as-water hose leftover, delete sourceBudgetMultiplier, drop beach ring, stuck alert); NEXT: file one child per ruling and build them.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — Hose/ all CLEAN and about 32 more marked CLEAN; NEXT: second-review the 7 fixed files, fix stale flat-D=4 pit-rule comments in about 10 files, review RM_MapComponent_Excavation.cs, RimMandrakeFlowWorksMod.cs and Swimming/RM_Swim.cs.
- Pointers from `FOUNDRY_HANDOFF_202610180431` not listed above (VALIDATION_V2_RECONCILE_AFTER_THE_BIG_DIG, WATER_SCENES_S5_JUDGE_THIRD_DRAFT, PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH, CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES, RIVER_SCENES_BUILD_WALKTHROUGH_WITH_CAPTIONS, DONOR_PHASE0_FINISH_AWAITING_HIS_RULINGS) are unchanged; NEXT: wake them from that file.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- Disk filled to 100% silently (git: "sha1 file write error. Out of diskspace", commits refused): scratch clones are 16-23 GB each; delete finished ones at once and use `--depth 1` for new ones (filed: LESSONS).
- A scratch clone's origin is the seat clone, which refuses pushes to its checked-out branch: repoint origin to git@github.com:Lmandrake/RimMandrake.git before ./publish (see: Transient/fw_scenes/review_night_core_log.md).
- The AskUserQuestion hook rejects a question that does not END in "?" (a trailing parenthesis fails) and headers over 12 characters (filed: LESSONS).

## Commits

```
e600c0f05 ledger: owner card V8 readout kept
2759d3c42 ledger: owner cards 2026-10-18 (D4, dug fish, no beach ring)
67a345f3e lesson: look at a review sheet before offering it
38b235690 Tree art jobs for TREE_TIERS_JUDGE_FORTY_FOUR_TRUNKS (20 jobs, owner tree-tier notes)
231b7a7de ledger: tree-tier sheet enactment ordered; Dulloth canopy note carried
3a4812fdd Dragonsnake canon variants review sheet (4 JFO renders, no picks); ledger note
d9ecc1312 BIG_CREATURES_DESIGN_WALLS_AND_SLOTS: walls/slots/roofs design pass + GPT review
28f403aed Dragonsnake: canon art off the white serpent; four JFO variants via alternateGraphics RSW_Dragonsnake now draws DragonsnakeCanon/Dragonsnake_A..D (stand-in render dragonsnake_jfo_v1 in all four until jobs dragonsnake_jfo_var{a..d}_v1 install); the white art stays only on RSW_DragonsnakeAlbino. Donor fold repointed too.
95a624b18 ledger: dragonsnake split clarified by owner
ae88df220 ledger: owner cards 2026-10-18 (big creatures, rescue access, alert, spikes)
279d1b405 Dragonsnake JFO pick sheet (6 owner-kept slots), no picks
b72a4cb5b ledger: file SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING (thirst/sprinkler regression at ea44bf7957) for FOUNDRY; ModsConfig restored to the 11-mod list
fa441daef ledger: owner cards 2026-10-18 (dig cost, falls, shooting, raiders)
29c6982b6 TREE_TIERS_JUDGE_FORTY_FOUR_TRUNKS: tier sheet (44 rows) + owner ruling in tree size proposal
d6e3b5286 BENCH helper rerun2: thirst+sprinkler at FlowWorks HEAD, not credited (T5, sprinkler regressions)
2d5c6e6a2 Canopy ruling: zoom-gated canopy (option A), zoom-only art scales to its zoom; build filed for FOUNDRY
4d2584f73 ledger: file LAKE_GROUNDWATER_REFILL_BUILD_WETNESS_CUT per owner card
3c039d6a8 ledger: drop BIOME_SPECIFIC_FAUNA_LAW_1 (owner, by card); canopy zoom investigation noted
a9ef6975a CANOPY_ZOOM_DIAGNOSE_SEE_THE_FOREST: canopy-zoom feasibility investigation, no code
872e462d2 ledger: tree size ruling (four role tiers), tier sitting and canopy zoom items filed
... 21 more: git log --oneline 54f5c85bf..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/biome_ffar/abyss_sheet_2026-10-04.html   generated/other (sheet tooling, backups, conversation records; not this session)
 M Transient/biome_ffar/aiwha_wingfirst_sheet_2026-10-15.html   generated/other (sheet tooling, backups, conversation records; not this session)
 M Transient/biome_ffar/phase0_remaining_art_sheet_2026-10-16.decisions.json   generated/other (sheet tooling, backups, conversation records; not this session)
 M Transient/biome_ffar/scale_ground_measured.json   generated/other (sheet tooling, backups, conversation records; not this session)
 M Transient/mc_human_review/KEYSHEET.md   generated/other (sheet tooling, backups, conversation records; not this session)
 M Transient/mc_human_review/keysheet.html   generated/other (sheet tooling, backups, conversation records; not this session)
 M Transient/modcheck/fixtures.json   generated/other (sheet tooling, backups, conversation records; not this session)
 M Transient/phase0_p6_save_renames.md   generated/other (sheet tooling, backups, conversation records; not this session)
 M conversations/2026-10-16-0549-c453ca3a.md   generated/other (sheet tooling, backups, conversation records; not this session)
 M conversations/2026-10-16-1218-9a5985c9.md   generated/other (sheet tooling, backups, conversation records; not this session)
 M conversations/2026-10-16-1839-6972cfb2.md   generated/other (sheet tooling, backups, conversation records; not this session)
?? Transient/ModsConfig.owner.547.bak   generated/other (sheet tooling, backups, conversation records; not this session)
?? Transient/biome_ffar/img/00063bfc98bbf60c00c9.webp   generated/other (sheet tooling, backups, conversation records; not this session)
?? Transient/biome_ffar/img/004678d5bc522129f222.webp   generated/other (sheet tooling, backups, conversation records; not this session)
?? Transient/biome_ffar/img/0052887ea95ee55cb4ce_full.png   generated/other (sheet tooling, backups, conversation records; not this session)
?? Transient/biome_ffar/img/0099e32f18695cf71e35.webp   generated/other (sheet tooling, backups, conversation records; not this session)
?? Transient/biome_ffar/img/012b0e9de80257c66cba.webp   generated/other (sheet tooling, backups, conversation records; not this session)
?? Transient/biome_ffar/img/012c446f56fabd4bd893_full.png   generated/other (sheet tooling, backups, conversation records; not this session)
?? Transient/biome_ffar/img/0139244f2dcf4a25b9e9.webp   generated/other (sheet tooling, backups, conversation records; not this session)
?? Transient/biome_ffar/img/0172b49133d12ef1a9d8.webp   generated/other (sheet tooling, backups, conversation records; not this session)
... 1535 more uncommitted paths (by top-level dir: Transient 1524, deployed 6, src 2, (root) 1, conversations 1, infrastructure 1): git status --short
```

