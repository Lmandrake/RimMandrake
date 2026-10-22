# BENCH_REBOOT_HANDOFF_202610220912 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610220122`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Review sheets and the art ledger can disagree about what the owner already approved: the ledger holds his keeps (`art.py status <name>` shows PROTECTED + rulings), but a sheet row is built from ONE graphic slot, so his approved sibling art (other sex, colour variants, lifestages, desiccated corpses) never appears and he gets re-asked (Varactyl tonight; the "dessicated" sheet showed 0 corpses). Before showing him ANY creature row, run `art.py status <species>` and read his rulings across all slots (`ART_SHEET_FIX_SIBLING_KEEPS_UNSEEN`, owner memory every-sheet-shown-must-be-truly-new).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **The walkthrough is up**: game UP on save `RM_fw_walkthrough_20261022` (map C: 10 composite scenarios, signs current; key sheet `src/RimMandrake/FlowWorks/northstar/review/scenarios/keysheet.html`). Built on origin 5ebfd259b2 — it LACKS `d5481252ae` (pipe-pole span draws the look's pipe) and `ba1c8d16ab` (hose aimed at a tank ends on a free side); redeploy from origin + rebuild to include them. Map R (C1 Thirsty Terraces, C11 Prospector's Creek) not built; C4 and C10 hoses fail to lay (C4 needs a ramp/ladder on dug ground; C10 waits on Q1).
- **Morning questions Q1-Q5**: `Transient/pile_2026-10-22/morning_questions.md` — reel outlet always west (D2, ties to `HOSE_REEL_FIX_TURNS_WITH_THE_SHIP`), joint fittings + pipe-meets-tank (D3/D4/D8), the "liquid tap" that is a ground well (`LIQUID_TAP_RENAME_NOT_A_FAUCET`), brown-on-brown Scrapper hose (D7), permission to draft pipe-crossing/end-cap/pump-look art (D9-D11).
- **Sheets waiting**: picks-1 redo (11 rows) http://localhost:37495/?t=TxhsPwIYJZhtR7WkMIQMog ; facings round 2 (Strill S, Whisperbird flight, Yobshrimp) http://localhost:44053/?t=fmT782QX4Bri3cqfETIM2A ; desiccated-corpse sheet not yet built (`DESSICATED_CORPSES_JUDGE_THE_ONES_HE_MISSED`).
- **One card owed**: 20 ✕ deletions on picks-1 held because protected/live (Taozin 5, Silooth 3, Snoruuk 3, JungleRancor 3, KwazelMaw 2, Akk/HarvesterBeetle/LothWolf/FrogDog 1) — list in `Transient/pile_2026-10-21/picks1_enact.md`.
- **Open owner questions**: walking freely under covered parts of a partly-covered pit (on `PIT_COVER_FIX_OCCUPANT_STAYS_BELOW`, closed with the conservative rule); with looks loaded the Scrapper look's pictures win over his Timber/Steel drawbridge picks (same as suspension); drill/tap placement on an empty survey is allowed (red hint) — refuse it?; canal-overflow D10 temp-slot priority unasked.
- **Shipped with a flag**: hose thickness is now 0.18 flat (2x the thin pass, his order) — not yet seen by him live at that girth beyond the C3 reel park; the C2 moat drops one level unattended (`MOAT_LEVEL_DIAGNOSE_HALF_METRE_VANISHES`, unproven cause).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `BRIDGE_ART_REDRAW_CABINETS_GROW_SADDLES` — all 97 picks + 12 held installed (b4e8c918ea), drawbridge art wired in code (c14b94ca0d), Scrapper timber gate closed art missing; NEXT: show the suspension + drawbridge art to the owner on the walkthrough and install the two missing Scrapper gate pictures he picked on 2026-10-20
- `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL` — colonist 2 m cap + machine dig built (5d79fd1e96), machines-off order kept (9aef556eff), probe rows 1/2/4 PASS live, real dig UNMEASURED (Tunneler had no mechanitor); NEXT: run the live dig with a mechanitor-controlled Tunneler and a colonist with Mining enabled per Transient/pile_2026-10-21/machine_dig.md
- `HOSE_GIRTH_TUNE_MUCH_THINNER` — hose now 0.18 flat / 0.23 plump per owner's 2x ruling (f256450686), deployed in the walkthrough; NEXT: get the owner's verdict on hose girth during the walkthrough and close or retune
- `HOSE_PLUMP_FIX_SKINNIER_WHEN_FULL` — plump strands refilled (5ebfd259b2), seen fat on the C3 reel park; NEXT: confirm on the walkthrough that a flowing hose reads fatter than an empty one in all four looks and close
- `PIPE_GIRTH_TUNE_HALF_AS_THICK` — half-width atlas (8d5b94b0e1) deployed in the walkthrough; NEXT: get the owner's verdict on pipe width during the walkthrough and close
- `PIT_SPIKES_REDRAW_SPOKES_NOT_LOGS` — B/C/D random pool installed (1b9fef6b35), deployed; NEXT: owner judges the spikes in game on the walkthrough, then close
- `RAIL_LADDER_REDRAW_CLIMB_NOT_CRAWL` — set B + raised pictures installed (0a587c4cc3), deployed; NEXT: owner judges the ladder lowered and raised on every facing in game, then close
- `REACH_MAP_BUILD_WALLS_AND_DEPTH_AGREE` — option 3 built and live 5/5 at b5e399067a; residual counter in; owner asked to MEASURE how often the residual case fires; NEXT: run the residual soak (ProofReachReset, long session on a dug walled colony on the full list, read ProofReach) and report failures per 1000 ticks
- `REACH_WINCH_FIX_GHOST_ROAD_RETURNS` — fixed offline (3810af4e5f: wall/door/fence changes now invalidate the reach map at once), state built; NEXT: re-run reach_map_proof.py WITHOUT --fresh-map on the deployed build and close on PASS

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `./publish` is refused whenever any other agent leaves a FlowWorks DLL or a ledger line uncommitted in the shared clone; helpers recovered via a throwaway clone/export — commit peers' ledger shards by explicit path first (filed: lessons)
- A live proof that passes on `--fresh-map` can fail on a reused map: the reach map only invalidated on the next path request (filed: lessons)
- Every "hose walk" screenshot from 10-18..10-21 was a MOCK frame, not a capture — check images are real before judging art (filed: lessons)
- The 1.6 pathfinder sees new walls/depth only after the map ticks; stage, then tick 10 before reading (filed: lessons)
- Sapper duty goes only to pawns that qualify as sappers; Mercenary_Gunners never get the winch giver (filed: lessons)
- A review sheet must let per-look variants be accepted together; the line-joins sheet forced one pick across looks (filed: lessons)
- `rimflow file --owner-said` refuses a question as authority — use --why for an owner question (see: tool output)

## Closed since the last handoff (19)

- `LADDER_HOSE_DIAGNOSE_SIPS_NOTHING` — b8d9bd5d41
- `FALLEN_CORD_DIAGNOSE_LIVE_BUT_HARMLESS` — b8d9bd5d41
- `WINCH_REACH_DIAGNOSE_CANREACH_FIBS` — 93cdbdc40ac1
- `DRAWBRIDGE_RAID_DIAGNOSE_LOITERING_AT_MOAT` — d722e97f1170
- `FALLEN_CORD_BUILD_RUBBLE_IS_NO_SHIELD` — f76aafe3ac76
- `SLUICE_OUTLINE_FIX_GREY_NORTH_LIP` — c922fd3a3f00
- `FLOWWORKS_PITCOVER_FIX_BURNS_PAWN_UNHARMED` — 18d7683341fa
- `FLOWWORKS_PITFALL_FIX_HISTORY_NOT_SAVED` — 18d7683341fa
- `LINE_JOINS_JUDGE_GPT_SEES_FIRST` — 052122d5bea5
- `DRAWBRIDGE_LOOKS_WIRE_PICTURES_IN_WINGS` — 1336ffdd98
- `PIT_COVER_FIX_PLANKS_DRAWN_AS_DIRT` — 9a82ae98f4d7
- `FLOWWORKS_SETTINGS_UNTANGLE_THE_JUNK_DRAWER` — 9544ea0571
- `SLUICE_GATE_SETTINGS_EXCISE_KNOBS_ON_NOTHING` — 747c9290c9
- `HOSE_FITTING_RENAME_CAP_IS_NOT_CAPPED` — 11aec7495c
- `HOSE_ENDS_FIX_MISSES_THE_PORTS` — 7b57a2ecf6
- `PIT_COVER_FIX_OCCUPANT_STAYS_BELOW` — 7b57a2ecf6
- `DEEP_DIG_EXPLAIN_WAITING_ON_NO_DROID` — 5c92b4a9cf
- `DRILL_SURVEY_EXPLAIN_BEFORE_STEEL_IS_SPENT` — 4e090d7ba1
- `FLOWWORKS_SETTINGS_POLISH_SUPERDEEP_LEAKS` — b5e1142258

## Filed and still open (19) — the next seat's queue

- `TESTENV_PREFLIGHT_HARDEN_TRISPIKE_AT_ARM` — Test environment: FlowWorks lines_proof and drawbridge_proof preflights never call validation_core.site_calm (jawa/quiet_site), so map-gen hostiles st
- `PIT_SPIKES_REDRAW_SPOKES_NOT_LOGS` — Pit spikes look far too chonky (solid logs filling the pit with cones on top). Redraw as thin spokes pointing UP that you could slide down, spread ove
- `RAIL_LADDER_REDRAW_CLIMB_NOT_CRAWL` — Rail-ladder facings wrong on the live walk: NORTH must hug the wall tighter and rise along it (compress the north/south perspective); EAST/WEST are dr
- `PIPE_GIRTH_TUNE_HALF_AS_THICK` — Pipes are drawn crazy thick: make every pipe half as thick (all four looks), joints/flanges scaled to match; also the end of a pipe segment draws wron
- `HOSE_GIRTH_TUNE_MUCH_THINNER` — Flexible hoses must be much thinner, and the hose reels look bizarre — redraw the reel (owner walk 2026-10-21, screenshot Transient/pile_2026-10-21/wa
- `REACH_MAP_BUILD_WALLS_AND_DEPTH_AGREE` — Reachability option 3: a second, wall-aware reach map per climb band, keyed by coarse pawn classes (opens doors / fence-blocked / swims), drawbridge g
- `REVIEW_SCENARIOS_BUILD_ALL_TWELVE_AT_ONCE` — Build all 12 composite FlowWorks review scenarios (C1-C12 of the 2026-10-21 design) as ONE labelled review map for one owner walk: in-world signs per 
- `LADDER_HOSE_DIAGNOSE_RETRACTS_ON_A_WHIM` — lines_proof LADDER_HOSE_DRAINS_RAISED_STAYS failed once in a full --fresh-map run (2026-10-22): pump powered after 30 ticks, drained only 10000 dl, an
- `BRIDGE_ART_REDRAW_CABINETS_GROW_SADDLES` — Bridge art: redraw all 12 ranked items from GPT's all-bridge-art review + the 26 drawbridge renders that never arrived; one review sheet, install noth
- `MOAT_LEVEL_DIAGNOSE_HALF_METRE_VANISHES` — Review scenario C2 (Drowned Keep): the moat fell from 2 m to 1.5 m on its own (351 cells) during the 2-hour unattended soak, even after a refill post-
- `REEL_TAP_CAMERA_REDRAW_STILL_SIDE_ON` — Hose reels (4 looks x stored/laid) and the liquid tap were accepted side-on; redraw from the building camera, then regenerate the reel hose geometry (
- `DESSICATED_CORPSES_JUDGE_THE_ONES_HE_MISSED` — picks_dessicated sheet showed 0 of the 58 dessic_* corpse renders (art_sheet dropped NOT_BODY_JOB renders; fixed: corpse_lane_texpaths). Build a dessi
- `ART_SHEET_FIX_SIBLING_KEEPS_UNSEEN` — Review sheets show only the one graphic slot a row was built for, never the species' other approved art: facings_regen_picks_sheet_2026-10-18 row RSW_
- `REACH_WINCH_FIX_GHOST_ROAD_RETURNS` — reach_map_proof REACH_WINCH_SITE regressed: was PASS (5/5 at b5e399067a, 10-21 21:59), now FAIL on HEAD 2038122711 (DLL a237375d): far colonist (7,0)-
- `HOSE_PLUMP_FIX_SKINNIER_WHEN_FULL` — A flowing (plump) hose draws ~1/4 width, thinner and darker than the empty one: HoseMath.PlumpBand assumes 62/64 opaque rows but every installed Stran
- `REEL_OUTLET_DECIDE_ALWAYS_GOES_WEST` — Every hose leaves its reel WEST (HosePortCandidate.Outward const (-1,0); reel rotatable=false; Graphic_HoseReel ignores rot) and U-loops (~1.5-cell ra
- `PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID` — Pipe -> 2x2 tank: the pipe arm ends under the skid on the tank's lower row (a cell centre cannot reach the mid-height flange where the hose now ends),
- `PIPE_POLE_REDRAW_NOT_A_POWER_LINE` — Pipe poles read as an electric line: GSS AerialMast placeholder art (insulators), span drawn as GSS's dark aerial cord instead of the look's pipe, and
- `LIQUID_TAP_RENAME_NOT_A_FAUCET` — RM_LiquidTap ('Liquid tap') is a ground bleed well (RM_LiquidDrillExtension, not on the pipe net) yet scenario C7 stages 'a fountain line of three tap

## Commits

```
06ab2043c1 conversations: catch-up 1 record(s)
4b2dc59c4c Grated base deck atlas outputs (bridge enact rebuild); OWNER game stamps
59b3e90859 night fixer: final progress; lesson on publish vs a shared ledger line
d303dd7216 night fixer: progress + morning questions (pinned Transient)
db4c4aa9e5 ledger: BENCH holds the bridge for the morning walkthrough
63480c05f0 FlowWorks walkthrough save RM_fw_walkthrough_20261022 built on 5ebfd259b2: keysheet regenerated; joints study final notes; 2 lessons
ba1c8d16ab Hose deploy aimed at a tank/pump/machine lands on its free side nearest the reel (was refused 'target blocked') Joints study UI note; same idea as aiming at another reel.
3ca8353bee ledger: file FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING (from the FlowWorks review pass)
966c5afa05 code_review shard: review L marks (24 FlowWorks .cs, shared_sync.py)
cda3b0f940 FlowWorks scenarios + design: girth text was false after tonight's fixes (plump hose no longer thinner; pipes/hoses not 'being redrawn')
d5481252ae Pipe poles D5: the span draws the look's own pipe (PipeSpan.png derived from each pipe atlas) and a ground pipe beside a pole runs its arm to it Was GSS's power wire on every look and a capped pipe half a cell short. Pole art itself stays the stand-in (owner's).
82c4e3779f code_review shard: review K batch 2
3b05671304 gen_pyrinth_absorption deleted its committed output before checking the donor Defs were readable; gen_droidworks_modules rewrote committed files from 0 kept defs. Both now abort first
290c39824d grab_source_art: a refused sheet.make is reported, not swallowed
61563d069e archetype_seed: 0 rosters or an unknown --biome is REFUSED (was a quiet all-Vanilla / empty-sheet success)
b82b99c947 validate_skills: a missing companion source dir is an ERROR (the jawa/ tool-name check silently did not run)
3c65348f6f gen_turret_register read its inputs from the read-only mirror's Transient (never there) and could write an all-cut register from an empty canon roster; fauna sheet generator refuses to overwrite an unreadable decisions file and warns on dropped roster rows (51 today)
be49c7588c code_review shard: review J marks
8eb63c4f65 gen_creature_register: override prefill now drops savedBy/writeCount (weapon/vehicle siblings already did)
9d34af2ed2 code_review shard: review K batch 1
... 247 more: git log --oneline c4cc68e4f7..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     holding for the morning walkthrough: game UP on RM_fw_walkthrough_20261022

Uncommitted: only `deployed/config/ModsConfig.swap-active.json` — the night live helper's tier-swap marker; KEEP it: the game is on tier fw_gss_sitting for the walkthrough, and `modset_builder.py --restore` uses it to put the owner's 325-mod list back after the walk (plus Transient/ untracked scratch, per the Transient rule).

