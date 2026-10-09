# FOUNDRY_HANDOFF_202610091641 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610091006`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Landing is by plumbing (`land.sh`), so the shared clone drifts behind origin within hours and blocks `git pull`; run `python3 src/RimMandrake/Utils/reconcile_clone.py` when no helper is mid-edit (it backs up first), and use the `rimflow` command on PATH, never `R="python3 ..."; $R` (zsh does not word-split).

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Rulings by card (all recorded as notes): sets 2-9 of `Transient/morning_cards_20261009.md` answered; typed ones: Q3.3 (duranium + doonium + beskar all exist -> `CANON_MATERIALS_DESIGN_1`), vexxith uses (`VEXXITH_USES_1`), Throat cask radiation, both Junker kinds, donor-code sheet (7 port / 10 rebuild / 3 replace), Trade UI + VTE retire NOW (candidate list prepared, NOT applied), mapgen folded into two design thrusts.
- Read first: `design/RimMandrake/canon_materials_design_2026-10-09.md` (six designs + GPT critique; six decisions left; Odyssey asteroid maps mine plasteel/components against the never-mined ruling).
- Canon creature sheet is yours to grade: `D:\Luke\dev\RimMandrake\Transient\canon_regen_wave4_2026-09-23\sheet.html`. Own-render keep sheet and junk reskin sheet are built; serve via the new non-art route in `serve_gated.py`.
- Canonical save was edited with your approval (label curve + drawCenters, 62+60 tags); backup `CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-labelcurve-drawcenter-20261009`.
- Load order: `mandrake.rut.patches` (554) loads before `mandrake.rm.biomes` (609), against its own loadAfter; not changed.
- `mandrake.rm.warcasket` is not on your full list, so the Junker caravan/cask cannot be measured there.
- All new numbers are PROVISIONAL.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `GLOOMCAST_FOLLOW_RECHECK_1` — two sittings disagree (3 of 3 vs 1 of 3 follow); NEXT: run ProofJob for all three on one map over several samples.
- `DONOR_CODE_PLAIN_PORTS_1`, `DONOR_CODE_SHAPE_REBUILD_1`, `DONOR_CODE_REPLACE_CAST_1` — filed, not built (art-heavy / needs live render look); NEXT: build the 7 plain ports starting with Radyak and Thermadon.
- `CANON_MATERIALS_DESIGN_1` — design ready, needs owner; NEXT: put its six decisions to him as cards.
- `BAZAAR_DISPLACEMENT_PASS_1` — retirement candidate `infrastructure/state/modlists/ModsConfig.FULL.CANDIDATE_NO_TRADEUI_VTE.xml` prepared; NEXT: apply it at the next game-down and run the VTE unwind rehearsal on a save copy.
- `FIREHAWK_FLIGHT_BEHAVIOR_1` — waits for a joint session; NEXT: spawn ~20 with him watching.
- `CRUST_NEVER_STRANDS_1` — A2 needs a Grey Sea floor map with a parked gravship; NEXT: build that scene and call ProofTearFree.
- `WEBWORK ProofHarvest` hook fix `756cf2812` — built, not deployed; NEXT: deploy Webwork and rerun SHOKKWEAVE_SOLE_SOURCE_1 A1.
- `RUT_DyingCreep` ConfigErrors fix and the two Silooth SWBestiary files — in src, not yet deployed; NEXT: deploy at the next game-down.
- `LANDING` — game UP on the owner's full list (622 mods incl. 8 new artoverride mods); NEXT: nothing, leave it up unless he asks.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- `land.sh` leaves the clone behind origin; plain `git pull --rebase` then dies on untracked collisions (filed: `src/RimMandrake/Utils/reconcile_clone.py`)
- `git restore -- a b c` aborts the whole chunk on one bad pathspec, leaving the tree dirty (filed: `reconcile_clone.py`, per-path fallback)
- A helper's `--prune` deploy can delete game-folder files that a just-landed commit adds; check `git log --all -- <file>` before calling a loss real (see: Transient/belt_deploy2_20261009.md)
- A dump of a different mod set must never replace the canonical def dump; the def dump is written only at startup with `dump_request.txt` armed (see: Transient/belt_dump_refresh_20261009.md)
- Helper reports of `rimflow implemented ... moved to closed/` can be wrong; check `rimflow show` (filed: this handoff)
- Two live sittings gave opposite answers on follower count; one reading is not evidence (filed: GLOOMCAST_FOLLOW_RECHECK_1)

## Commits

```
b71f58a7e ledger: GLOOMCAST_FOLLOW_RECHECK_1 filed; two sittings disagree on follower count
756cf2812 Acceptance sweep 4: seal/burst/sleeper reads; ProofHarvest picks a cell beside a colonist (map-centre cell read non-designatable)
bc7c1d814 Belt build r4: no offline build items ready
92acb2d92 Belt deploy sitting 2: full-list cold load (622), settings smoke 80/80, ProofHarvest, harvest delta; fix RUT_DyingCreep ConfigError
76dea3676 Cauldron re-audit: 13 of 16 PASS, 3 FAIL are deploy regressions (UtinniPatches/SWBestiary overwritten)
95ce5edbd Exotic materials census: 685 material defs in src/, 244 non-food clustered, unify/differentiate proposals
9e1c9775d Canon metal fabrication: what the factory ship can forge, with canon ore sources
acc91cb8f Cauldron audit fixes: selftest result recorded (2 pre-existing FAILs, unrelated)
0917fe9a2 HelixienArtOverride: the Cauldron's AA_Helixien gets its B picture; bedbug/neebray/silooth/silkie redos re-filed
c09fdaea5 Cauldron audit: radyak renamed ossrith, new infected-aerofleet description, silooth 8 cells + acid spit the AI uses
985bf6b18 Independent audit of the Cauldron sheet follow-through: 30 PASS, 15 FAIL, 1 UNMEASURED
4ba121909 Load-error triage 2026-10-09 notes; ledger events for MOD_OPTIONS_RETROFIT_1 implemented
99b1b94d4 RSW_ZakkroEgg art installed via the ledger as swresource/RSW_ZakkroEgg/RSW_ZakkroEgg_a.png: Graphic_StackCount needs a folder, the def's texPath had no art at all (job rsw_zakkroegg_v1 validated pass)
2afb0540f RM_SettingsOpenSmoke: static_call hook (RimMandrake.RimDefDump.RM_SettingsOpenSmoke.Run, ';' args) that draws each RimMandrake mod's settings page from a real OnGUI pass and reports opened/failed; MOD_OPTIONS_RETROFIT_1.A1 needs it. Not yet run in game.
37c11ed24 Giant skeletons: set Graphic_Single per skeleton (the earlier base-level edit was wrong, base keeps Random for its RubblePile folder fallback); 7 children each name one PNG and logged 'Collection cannot init'
dca4b7b2a RM_GiantSkeletonBase graphicClass Graphic_Random -> Graphic_Single: each skeleton is one PNG, Random wants a folder, so all 7 logged 'Collection cannot init' and drew nothing
7f5454576 Cauldron sheet: 4 ✕ purged with the fixed enact, notes marked done, sheet rebuilt (0 TODO, 0 conflict); legacy unqueued rulings measured (229)
58c34c79a RM_Illisk bite uses HeadAttackTool: body Snake has no Teeth part group (config error on every load)
41a77e868 Move RUT_FoundrySalvageCache into TerminalBiomes: its ParentName (RM_WreckFamily_Carapace) is in the biomes mod, which loads after UtinniPatches, so the def lost its parent (null thingClass, 3 config errors). Deploy must delete the old UtinniPatches copy.
f8f24187e Lift DeadCreep/DyingCreep deploy holds: art present, and RUT_ContagionRingScatter deployed without DeadCreep (dangling filthDef cross-ref)
... 126 more: git log --oneline 1443f8948..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
?? Transient/acc_d_checks.py   helper scratch from the 2026-10-09 belt (generated)
?? Transient/acc_d_checks2.py   helper scratch from the 2026-10-09 belt (generated)
?? Transient/acc_d_gloom.py   helper scratch from the 2026-10-09 belt (generated)
?? conversations/   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-acc_20261009.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-acc_20261009b.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-acc_20261009d.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-acc_biomes.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-acc_green_min.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-acc_green_min2.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-acc_harness.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-acc_l1x.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-ishko.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-live_20261008.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-live_20261008b.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.before-tier-watchers_live.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T142015.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T161529.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ModsConfig.pre-session.20261007T135600.xml   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ns_flowworks_backup.20261002T070221.json   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ns_flowworks_backup.20261005T142015.json   helper scratch from the 2026-10-09 belt (generated)
?? deployed/config/ns_flowworks_backup.20261005T161529.json   helper scratch from the 2026-10-09 belt (generated)
?? infrastructure/state/items/PLASTEEL_DURASTEEL_MERGE_1.md   helper scratch from the 2026-10-09 belt (generated)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261008T212615.json   helper scratch from the 2026-10-09 belt (generated)
```

