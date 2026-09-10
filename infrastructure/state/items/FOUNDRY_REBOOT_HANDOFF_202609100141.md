# FOUNDRY_REBOOT_HANDOFF_202609100141 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609091727`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

RimWorld's own crash-recovery silently resets `ModsConfig.xml` to 6 mods (vanilla+DLCs)
and relaunches on ANY unhandled exception during `Game..ctor()` — campaign load, new
colony, and quicktest all crash through the identical path. The same fingerprint
([Ref 24E2AAB2]) appears in a log from **2026-09-08 18:30**, a full day before this
was finally diagnosed tonight — every session in between, including several passes
this window, misread the resulting bare ModsConfig as "an agent left it on a minimal
list." Diagnose with `harvest_log.py` refusing + a `Resetting mods config` log line,
never by trusting the live mod count alone. Root causes found tonight: (1) 7 of our
own C# types were in the repo build but never redeployed after a consolidation
rebuild — a missing comp type discards its whole ThingDef, orphans the PawnKindDef,
and Alpha Genes NREs on the null race; (2) separately, ManyWaters shipped 5 defs with
a null `thingClass`, which crashes `ReadingPolicyDatabase.GenerateStartingPolicies()`
unconditionally. Both fixed tonight; ManyWaters' donor is excluded from the live list
pending its own repair (`MANYWATERS_COLOR_SUPPORT_1`).

Second-most-expensive lesson, same night: a donor retirement's whole-mod-list
dependency check is NOT sufficient — the campaign SAVE can hold direct Scribe
references (or just a bare `<meta><modIds>` entry) that no mod-graph check sees.
Two separate retirements (`lumi.doorsexpanded`, the droid-donor trio) each passed a
careful dependency census and still broke the save load. Check the save directly
before calling any retirement safe — see `LESSONS_INBOX.md` for the full list of
what else broke tonight (`MayRequire` on a bare `<Operation>` doing nothing, Steam's
own stuck launch-lock, illegal `--` in an XML comment discarding a whole file).

## What the owner should see

- `STAT_NORMALIZATION_AUDIT_1` — full census + 4-wave plan on 587 active mods for
  what conflicts with a future stat-normalization pass (fauna/flora/weapons/apparel/
  work-speed, widened by his own ruling this session). Wave 1 (13 mods) already
  executed and closed. Waves 2-4 need his ruling — top items: `fluxilis.germanquality`
  already gone (a silent 0.5x-10x global HP multiplier), and a reconfirmation
  question on `redmattis.*` (Big and Small) — an existing "deliberate scaling
  experiment" ruling that a blanket "own our whole loadout" instruction should not
  silently override. Full doc: `design/Jawa/mods/stat_normalization_audit_2026-09-09.md`.
- Art candidates awaiting his pick, none wired: `Transient/DESERT_WRAPS_ART_COMMISSION_1_candidates_2026-09-09.png`
  (4 wrap styles + 2 head shapes), `Transient/planetary_beauty_loadscreens/candidate_{1,2}_*.png`
  (space beauty shots), `Transient/mapgen_v3/comparator_sheet.png` (map-generator
  terrain painter, keep/cut mark owed).
- `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1` — a Fable design draft widening base RM graffiti
  scope, awaiting his ruling before any build starts.
- `LANDMARK_NAMING_PASS_1` — an 18-name hand list ready for his skim
  (`LANDMARK_NAMING_PASS_1.names.md`), batchable with `GAPING_DOOM_SITE_1` and
  `OASIS_LANDMARK_PLACEMENT_1` once he's looked.
- Two save-compat regressions from tonight are both fully root-caused and scoped
  to a specific, narrow fix (see the half-done list below) — worth his awareness
  since both donors got reverted-live mid-session rather than staying retired.
- `MOVING_DUNES_BUILD_1`'s engine is built and loading clean live, but the
  shader-tint quicktest (does the dune-height tint survive the game's rendering,
  or does it need the texture-recolour fallback) is still unrun — his eventual
  look is the actual gate per the item's own criteria.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `BIOME_ENRICHMENT_DESERT_WASTELAND_1` — measured fresh (57.4%/63.7% zero-mutator),
  placed NOTHING: the biome sheets give narrative "kit" descriptions with zero
  concrete defNames, and the one doc that pairs this register with real defNames
  (`structure_injection_roster.md`) gates every entry to specific narrative arcs —
  using them here would be re-allocating curated content. Next action: owner/BENCH
  names concrete defNames, or rules that density-topping with already-legal existing
  mutators satisfies the ask. Do not re-attempt without one of those.
- `BIOME_ENRICHMENT_POISON_FOREST_1` — DIFFERENT from its sibling above: real
  defNames WERE confirmed and a plan verified, but execution was blocked by the
  live crash before any write landed (see `dabe8418`/`26f2387d`). Next action:
  bridge free + game up → execute the already-verified plan directly, no new
  scoping needed.
- `DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1` — root cause found: NOT placed content
  (zero placed instances confirmed), the block is the save's own bare
  `<meta><modIds>` entry naming the donor — an unconditional metadata gate, not a
  content dependency. The original 2026-09-09 crash's exact exception could not be
  recovered (log overwritten by later restarts). Next action: re-save the campaign
  once with the donor active (clears the meta entry + registry residue on its own)
  OR hand-edit `<meta>` to drop the `<li>`, THEN retire and cold-load-verify — but
  get a clean crash repro first, since the item's own note doesn't rule out a
  recurrence for an unrelated reason.
- `DROIDWORKS_PERSONALITY_VERIFY_1` — this is the item whose live-verify attempt
  triggered tonight's whole crash-recovery cascade (three reboots). The actual ask
  (20 spawns per family showing forced traits + protocol pedantry) was NEVER
  completed — the mechanism itself was independently re-verified correct by code
  reading (`DROIDWORKS_FORMAT_TIERS_1`'s own pass tonight), but no live spawn test
  has succeeded. Next action: once the game is confirmed stable again, retry the
  spawn test on a throwaway quicktest colony — the mechanics are not suspected of
  being the problem, tonight's crashes were unrelated engine bugs found and fixed.
- `DROID_DONOR_SAVE_COMPAT_REGRESSION_1` — root cause found: DroidDepot and
  MSEDroidFix have ZERO placed content (pure registry noise); Asimov has 78 real
  live `Class="Asimov.Need_Energy"` Scribe blocks on ordinary pawns (no droids
  involved) + 1 `WorldComp_EnergyNeed`. A scrub script already proven on two OTHER
  saves (`DROID_ASIMOV_SAVE_SCRUB_1`) was simply never run against
  `CANONICAL_ASHKARR`. Next action: apply that same scrub to this save, then
  re-retire all three donors and cold-load-verify. No pawnkind/building porting
  needed — this is narrower than the item's own title suggests.
- `DROID_RETIRE_ABF_SYNCORE_1` — STOPPED, not executed: `guy762.kotordroids`'s 12
  race defs inherit via `ParentName` from an ABF-owned abstract def, which no patch
  can gate around — confirmed live against `retirement_order.py`, not guessed.
  This is `DROID_DONOR_PATCH_GATE_1`'s Site 1, already tracked there. Next action:
  none until that gate item resolves; do not re-attempt this retirement standalone.
- `DROID_RETIRE_DEPOT_ASIMOV_1` — executed once (`f6116f97`), then REVERTED live
  the same night (`7982a712`) when it turned out to be one of the two save-compat
  regressions above. Currently live again (restored). Next action: same as
  `DROID_DONOR_SAVE_COMPAT_REGRESSION_1` above — apply the Asimov scrub, THEN
  re-retire via this item, cold-load-verify.
- `LANDMARK_NAMING_PASS_1` — the rename tool (`jawa/world_landmark_rename`) is
  source-committed and was very likely included in tonight's BridgeTools GM-pair
  redeploy (not individually confirmed live). An 18-name hand list already exists
  (`LANDMARK_NAMING_PASS_1.names.md`), matching what "Review B2" actually asked
  for. Next action: confirm the rename tool answers live, get the owner's skim of
  the 18 names, execute — batch with `GAPING_DOOM_SITE_1`/`OASIS_LANDMARK_PLACEMENT_1`
  per the item's own note. "Namer variety" for the remaining ~14 reused names has
  no automated route (no RulePack wired to landmarks) — flagged as its own owner
  decision, not invented.
- `MODLIST_RESTORE_AND_BATCH_DEPLOY_1` — the big one. Campaign IS restored and was
  confirmed loaded/playable tonight (`Playing`, 5 colonists, clean `harvest_log.py`).
  3 of 4 new mods (MovingDunes, FluidCanals, Oracle, +ProximityHatch) landed live
  and cold-load-verified; ManyWaters was excluded due to its thingClass bug (see
  "one thing to carry forward"). Two live crashes happened AFTER this item's own
  successful load, during separate unrelated quicktest attempts (see
  `DROIDWORKS_PERSONALITY_VERIFY_1` and `PITCELL_PRISONER_BED_BRIDGE_GAP_1`) — the
  GAME IS CURRENTLY DOWN again as of this handoff, collateral from those, not a
  regression in this item's own work. Next action: once `MANYWATERS_COLOR_SUPPORT_1`
  gets its thingClass fix, re-add it and do one more clean verify pass; otherwise
  this item's core work is done, just needs closing once that last mod lands.
- `MOVING_DUNES_BUILD_1` — engine built (2,672 lines), loads clean live (confirmed
  as part of the batch above). The item's own criteria still requires the
  shader-tint quicktest (does dune-height tint survive the WaterDepth-style
  overlay) — never run, game went down before it could happen. Next action: bridge
  + game up → run the one-def gate check, or just look at a dune map directly
  since both tint modes are already implemented behind one field.
- `SEA_ENRICHMENT_LANDMARKS_1` — plan fully verified and freshly re-measured
  (Grey Sea 429→472 tiles, Twilight 479→607, both currently 0% landmarked,
  post-`WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1`), but the game went down before any
  write landed — zero mutation made. Next action: bridge + game up → execute the
  already-verified plan directly (`Transient/seal_apply.py`, `seal_measure_before.json`
  exist from the prep work).
- `STAT_NORMALIZATION_AUDIT_1` — plan delivered by design (see "what the owner
  should see"), stays `doing` until he rules on waves 2-4. Wave 1 executed and
  closed separately as `STAT_NORM_WAVE1_RETIRE_1`. No next action until his ruling.

## Traps learned

All filed to `LESSONS_INBOX.md` this window (2026-09-09/10 entries). Highlights:
RimWorld's own silent `ModsConfig.xml`-reset-to-6-mods crash recovery (the single
biggest misdiagnosis of the night, see "one thing to carry forward"); a donor
retirement's mod-list dependency check is not sufficient, the save itself needs
checking too (two real incidents); `MayRequire` on a bare `<Operation>` does
nothing, only `PatchOperationFindMod` gates; a null `thingClass` anywhere crashes
every route to a `Game` object; Steam's own "already running" launch lock gets
stuck after a silent crash (fix: restart the Steam client, not the game); a
quicktest crash kills the whole shared process including an already-stable
campaign; illegal `--` inside an XML comment silently discards the whole file
(hit twice, two different mods). Also newly built and pre-authorized tonight:
`src/RimMandrake/Utils/system_screenshot.py`/`system_click.py` — OS-level
screenshot/click, always OK to use when state is in doubt, no asking first
(owner ruling 2026-09-09).

## Closed since the last handoff (16)

- `BRIDGETOOLS_DLL_GM_DRIFT_1` — 4f550f29 (closed at handoff time — redeployed live as part of `MODLIST_RESTORE_AND_BATCH_DEPLOY_1`, cold-load verified)
- `STAT_NORM_WAVE1_RETIRE_1` — 05d846f7 (closed at handoff time — all 13 mods confirmed removed from the live, cold-load-verified list)
- `INHABITED_INJECTIONS_DECOUPLE_1` — f23f11cda6e59097d84ba83ff4fed88d6f89dce6
- `WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1` — ec8e467028c371a92421dc60f1bab0eb3c09437c
- `PYRELANDS_LORE_NAMING_DRIFT_1` — b2ebdfdb9618cffa2cd266d4a4970185dcd33b1b
- `GRAFFITI_FRAMEWORK_BUILD_1` — 4f3b67a3681e3028a17363940b67d67dfda359d4
- `BIOMESKIT_RENDER_LAYER_MISSING_1` — dace71e05171a8f09156958f27be4dc8477a1234
- `DISTRICT_TEMPLATE_LIBRARY_1` — a0816bec056d1a7f7238e1454d6142bac040b794
- `SANDWORM_MYTHOS_BUILD_1` — cd50911a1453058e1a9f9154d766fa091c8f60ab
- `DROID_FDE_GOODWILL_CAP_1` — 61789b97086798ba0d4406a3060c0551798a493a
- `DROID_HUTT_CAPTIVES_1` — 41c5c7f3
- `W9_RUN_STAGE_RESULTS_UNCHECKED_1` — 9f0dd8975aa8a836b08d1d9df3da9d93d549e46b
- `SYSTEM_TOOLS_SELFTEST_1` — ea283906bac3016596969c24f0b1b0778e33828a
- `SELFTEST_RENDER_FLAKE_1` — bff84af8b8ccff3064274aa3ecd5ebf018eebcfe
- `WORLD_FEATURE_LABELS_OVERSIZED_1` — 2fbb797333112cea80b948ad3805f59ded0fcd20
- `CODEX_EDIT_TIMEOUT_1` — 5d58e484

## Filed and still open (3) — the next seat's queue

- `DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1` — lumi.doorsexpanded retirement broke CANONICAL_ASHKARR save load; mod restored, real fix still owed
- `DROID_DONOR_SAVE_COMPAT_REGRESSION_1` — Asimov/DroidDepot/MSEDroidFix retirement broke CANONICAL_ASHKARR save load; mods restored, real fix still owed
- `STAT_NORMALIZATION_AUDIT_1` — Census third-party mods that adjust animal/plant stats, rarity, appearance, size, growth before a self-owned-content normalization pass

(`STAT_NORM_WAVE1_RETIRE_1` closed this window — see above. `MODLIST_RESTORE_AND_BATCH_DEPLOY_1` stays open, its own status is in the half-done list below.)

## Commits

```
c4f3510c Ledger sync: DROIDWORKS_PRIMITIVE_TIER_1 note (G2 art landed, stays doing)
69476f42 DROIDWORKS_PRIMITIVE_TIER_1: real G2 sprite art (goose-neck droid), placeholder retired
f4b76f73 BENCH reboot handoff 202609100128: art pipeline built+hardened, review loop converged, sittings staged
16192667 artpipe: fifth review fixes — gemini budget/billing edge cases (7e874fdd)
d4a7c902 Ledger sync: flush pending events ahead of reboot
dc933df1 INHABITED_AUGMENTATION_BUILD_1: build structure_procedural_spec §8.14 (storage cache)
f0db7609 DROID_ORACLE_VOICE_DESIGN_1: reconcile the four droid consumers against the built claude -p client
a0af9567 TILEGEN_SILENT_REUSE_1: closed-source SDK/transport layers read directly, no root cause found
24dedc40 Lesson: throwaway codex homes queue UAC prompts despite the seed template
65fef933 Ledger: CODEX_UAC_STORM_1 filed (calibration's throwaway homes queued ~30 UAC prompts past the seed template)
5cd78cb9 PLANETARY_BEAUTY_LOADSCREENS_1: mechanism identified, two beauty-shot candidates
fc43a426 SHIELD_MODS_LEVERAGE_1: bespoke building-scale shield generator v1 slice
b9520e45 INHABITED_STOCK_ONTO_MAP_AND_FATE_1: reachability gaps confirmed closed, fate live-check still owed
d810ddb9 Ledger sync: CODEX_EDIT_TIMEOUT_1 close + bridge release + concurrent FOUNDRY note
6b62f3de PLOT_MECHANISM_MODS_WAVE_1: wire Aftermath rule 6 (Zizzik's aftermath) trigger
5d58e484 CODEX_EDIT_TIMEOUT_1: root-cause the 3/3 edit-mode timeouts, fix orphan leak
bb95160c PITCELL_PRISONER_BED_BRIDGE_GAP_1: live-proof attempt crashed the game before the tool could be called
7e874fdd ART_PIPELINE_DAEMON_1: fix fourth review's 4 findings + 2 lower notes
dfb22d9a DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1: scope root cause (metadata gate, not placed doors)
9001d4bd Ledger sync: WORLD_FEATURE_LABELS_OVERSIZED_1 closed
2fbb7973 WORLD_FEATURE_LABELS_OVERSIZED_1: visual verify -- labels read fine, closing
b12222a7 Ledger sync: flush pending close/note events
bff84af8 SELFTEST_RENDER_FLAKE_1: decouple render bench()'s wall-clock budget from selftest correctness
b7e7d6af DROID_DONOR_SAVE_COMPAT_REGRESSION_1: root-cause found — Asimov Need_Energy on 78 non-droid pawns, not placed droid content
ea283906 SYSTEM_TOOLS_SELFTEST_1: guard ctypes.windll behind a Windows check
05d846f7 MODLIST_RESTORE_AND_BATCH_DEPLOY_1: campaign restored and LOADED on 581; ManyWaters excluded, its blocker filed
de58a58f ART_PIPELINE_DAEMON_1: fix third review's 7 findings + 4 lower notes
0791bc3d code_review_status.py marked CLEAN after 12 adversarial waves; 181 dead entries pruned
a3b2ffc2 Rerun codebase health visualization
85b206bd code_review_status: eleventh review wave — phantom reason wins, NUL-safe census
6fac2cd1 Add system_screenshot.py/system_click.py: OS-level desktop capture and click tools
2005115a code_review_status: tenth review wave — reopen refuses on canonicalization ignorance
e626969c Ledger: GEMINI_WORKER_BACKEND_1 closed at 477dfb06
477dfb06 ART_PIPELINE_DAEMON_1: fix fresh review's 9 findings; add GEMINI_WORKER_BACKEND_1
ae1cfa3c Ledger: DUMPDB_MANIFEST_SHORTFALL_1 reassigned to BENCH and closed
d09744bd Ledger: DUMPDB_MANIFEST_SHORTFALL_1 closed (rebuild + full_name split, both live cases pass)
f5637051 code_review_status: ninth review wave — check's last ignorance-as-absence, precheck traceback
e3aff63c code_review_status: eighth review wave — prune never drops on ignorance
9224996a Ledger: DUMPDB_MANIFEST_SHORTFALL_1 root-caused, live db rebuilt; GEMINI_WORKER_BACKEND_1 to BENCH
a0dca2d9 code_review_status: seventh review wave — decode degradation, check/list agree on dirs
2e70b29b gitignore artpipe worker codex-homes: they seed auth.json (public repo)
4f550f29 MODLIST_RESTORE_AND_BATCH_DEPLOY_1: full-list cold load was failing on STALE DEPLOYED DLLs, not the mod list
be65992d Ledger: Gemini billing decision closed on contrast proof; GEMINI_WORKER_BACKEND_1 filed
e97591ce Gemini image-conditioned contrast batch for ART_PIPELINE_DAEMON_1
3ef38055 Owner ruling: art route = Gemini billing + Codex edit-mode debug in parallel
4d3f22b5 Codex calibration: linear to N=4 (95 img/h), native alpha YES, ~526 img/week ceiling at $20; edit mode dead 3/3
53e7097b Ledger sync: artpipe state note; SELFTEST_RENDER_FLAKE_1 + DUMPDB_MANIFEST_SHORTFALL_1 filed
25dd46e6 File MODLIST_RESTORE_AND_BATCH_DEPLOY_1: the campaign has been abandoned at a 6-mod vanilla menu for 80+ minutes
0705b62f STAT_NORM_WAVE1_RETIRE_1: checks pass, execution blocked on a vanilla-only modlist
cf488dd8 ART_PIPELINE_DAEMON_1: fix all 10 ultra-review findings plus below-cap notes
13584e06 NINEFOLD_ENGINE_M0_1: wire 7/9 first-contact chains on owner's own provisional-text authority
86d55a3e MAPGEN_PAINTER_V1_1 round 3: point hydrology was stamped inside its own rock, not just too small
8f4bdbef STAT_NORM_WAVE1_RETIRE_1: fresh dependency + save re-checks, all 13 pass
2b62fc0b code_review_status: sixth review wave — prune --apply actually drops phantoms
e6d79ac2 code_review_status: fifth review wave — drvfs case-rename phantoms killed
99839340 ART_PIPELINE_DAEMON_1: art-pipeline daemon, worker contract, and mock-driven selftest
4dedcfba selftest: enforce the one hook-log path across both writers
5a70ad9e File STAT_NORM_WAVE1_RETIRE_1: execute Wave 1 of the stat-normalization mod audit (owner go-ahead)
8cd6d041 rimflow: note MLIE_FAUNA_ABSORPTION_1 Wave B pass
a68df824 code_review_status: fourth review wave — literal pathspecs, honest unreadable answer
d75b0609 MLIE_FAUNA_ABSORPTION_1: Wave B (Dewback/Vulptex/Porg/Nuna/Wampa/Acklay), Wave A wiring fix, license verified
62e60697 Fleet: add the Artist window (purple, top-right above EMERGENCY)
fe9bf2c2 code_review_status: third review wave — quoted paths, sandbox escape, honest list reasons
93917385 File ART_PIPELINE_DAEMON_1: constant background art pipeline (owner directive), replaces CODEX_PARALLEL_WORKERS_1
bad5c469 rimflow: note on STAT_NORMALIZATION_AUDIT_1 (census delivered, stays doing)
f1485451 STAT_NORMALIZATION_AUDIT_1: full-stack stat-conflict census + 4 waves (plan only)
a45e4cd0 code_review_status: second review wave — 7 more findings fixed
233503ae gen_flora_distribution_portfolio: DEFDB via game_paths, not a LocalLow literal
8aecef33 code_review_status: fix wave from the adversarial full-file review
6c9287cb STAT_NORMALIZATION_AUDIT_1: record owner rulings (widen scope, split cosmetic/content-adding buckets) and the temp-minimal-modlist hazard
aea71526 ANCIENT_WAR_LAB_1: three-band KCSG dungeon authored offline (approach/lab interior/core)
05f67a48 LANTERN_DEEPS_INJECTION_1: crystal-fauna eviction patch, kyber verified inherited
5579e3db File STAT_NORMALIZATION_AUDIT_1: census third-party fauna/flora balance mods before the owned-content normalization pass
c7b8515d rimflow close W9_RUN_STAGE_RESULTS_UNCHECKED_1: fix already landed, ledger wasn't updated
9f0dd897 NINEFOLD_FIRE_HOOK_RATELIMITED_1: offline re-verify, rate-limit logic confirmed correct
a18db8d4 SETTLEMENT_VERBS_WAVE_1: offline re-verify after Sprint wave A merge, still doing
4a0fc3a2 LIVESTOCK_STARTER_TRIO_1: onnik built and offline-verified, karrask Mass fix
bf669503 File DROID_DONOR_SAVE_COMPAT_REGRESSION_1: droid donor retirement broke the canonical save load
3020dd6a VAULT_THAW_QUEST_FAMILY_1: re-verified offline, no rebuild, left doing
7982a712 Revert DROID_RETIRE_DEPOT_ASIMOV_1: restore MSEDroidFix + related patches
e696e277 BUILDING_THEFT_HAULER_1: re-verify offline after RimProperty merge, Droidworks now live
dabe8418 BIOME_ENRICHMENT_POISON_FOREST_1: doorsexpanded fixed, but 3 more mods missing on retry
f90feb8b SETTLEMENT_VISIT_LOOP_1: offline re-verify after sibling-item fixes, still doing
03d45d31 Ledger sync: HELIX_TELLUROX_BUILD_1 offline re-verification note
bfb1f47f HELIX_TELLUROX_BUILD_1: offline re-verification, no rebuild needed
5edacb13 DROID_REPAIR_FOR_PROFIT_EVENTS_1: re-verify offline, record ModsConfig drop
4a9dc230 VAULT_DUNGEON_BUILD_1: author V5's landmark offline, fix stale item-file path
4b7a16a1 File DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1: donor retirement broke the canonical save load
26f2387d BIOME_ENRICHMENT_POISON_FOREST_1: real defNames confirmed + verified plan; blocked by a live crash, not content
aa2bcc91 Closes: DROID_HUTT_CAPTIVES_1
41c5c7f3 DROID_HUTT_CAPTIVES_1: re-verify offline on current main, close
c54d9d14 Ledger sync: DROID_FDE_GOODWILL_CAP_1 verify+close, plus queued prior writes
61789b97 DROID_FDE_GOODWILL_CAP_1: re-verify offline, close
169574cb SANDWORM_MYTHOS_BUILD_1: re-verify and close the Long Hunger (v1)
cd50911a PITCELL_PRISONER_BED_BRIDGE_GAP_1: write item file, confirm still blocked on live proof
cdb773ab MACRO_GENERATOR_V0_1: re-verify pipeline end-to-end (offline), leave doing pending owner grade
ce04b993 JAWA_PATCHES_SPLIT_1: re-verify, 0 files remain (tombstone confirmed)
63d09a03 DROIDWORKS_FORMAT_TIERS_1: independently re-confirm root cause, offline verify clean
78cf5b09 FLUID_CANAL_MECHANIC_1: rework reservoir to drip+re-flood per owner ruling
70c4af42 rimflow ledger sync: TILE_STRUCTURE_DESIGNS_1 note + queue re-render
f6116f97 DROID_RETIRE_DEPOT_ASIMOV_1 (wave R3): retire Droid Depot + Asimov + MSEDroidFix
e528a153 TILE_STRUCTURE_DESIGNS_1: coverage lint built, precise 16/22 promise state
10b0a793 rimflow: close DISTRICT_TEMPLATE_LIBRARY_1
a0816bec DISTRICT_TEMPLATE_LIBRARY_1: fix real aisle-blocked bug in junkers_dwelling_cluster, close v1
2423eac8 DROID_RETIRE_ABF_SYNCORE_1: blocked on Site 1's ParentName chain, no mod-list change made
355ab188 LANDMARK_NAMING_PASS_1: confirmed tool+names already built, checked namer-variety route
79b599d8 SEA_ENRICHMENT_LANDMARKS_1: verified plan, measured fresh, game went down before any write
b9344a89 Closes: BIOMESKIT_RENDER_LAYER_MISSING_1
dace71e0 BIOMESKIT_RENDER_LAYER_MISSING_1: worldmap decoration icons traced to ReGrowthCore, non-issue
cbc6f8f1 Lesson: a gate needing an unloaded mod is a load round, not a quicktest
2847f418 rimflow ledger sync: MOVING_DUNES_BUILD_1 note + pending queue events
11115218 MOVING_DUNES_BUILD_1: the dunes engine — Werner transport on Odyssey's sandGrid
781732a6 Ledger sync: GRAFFITI_FRAMEWORK_BUILD_1 close event
4f3b67a3 GRAFFITI_FRAMEWORK_BUILD_1: reconcile against R7/R8, close
663465cf BIOME_ENRICHMENT_DESERT_WASTELAND_1: measured, left doing — no concrete kit
865cd609 FUNGALFOREST_RAID_MERGE_1 offline half: ingest the spore kit, discover the merge already painted
d9b909c8 ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1: re-verify claude -p transport, rebuild clean, live verify owed
d85c26c2 BRIDGETOOLS_DLL_GM_DRIFT_1: rebuild companion with --gm, confirm 41-tool gap closed (plan-only, no deploy)
58abbd44 MANYWATERS_COLOR_SUPPORT_1: record the mod-activation blocker found live
49195cc4 Ledger sync: flush pending close/note events (BELT fanout wave)
b2ebdfdb Fix Pyrelands doc naming drift: RSW_FE_ -> RM_FE_
d672d781 rimflow: close WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1
ec8e4670 WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1: fix 181 landBiomeSubmerged tiles, real defect confirmed live
448e87d7 MANYWATERS_COLOR_SUPPORT_1: v1 coloured water/slime offline slice, live step owed
620bc909 DESERT_WRAPS_ART_COMMISSION_1: candidate contact sheet (4 wrap styles, 2 head shapes)
31df09de WORLD_FEATURE_LABELS_OVERSIZED_1: reconcile the duplicate maxDrawSizeInTiles formula
f23f11cd INHABITED_INJECTIONS_DECOUPLE_1: Inhabited decoupled from StructureInjections via reflection
5854de5b Lesson: stash pop over foreign dirty state dropped two waves; fsck recovered both
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-10T01:02:42Z

All resolved before this handoff closed:

- `Transient/codebase_health.*` + `infrastructure/state/codebase_health_last.json` —
  mine (rerun per owner request), already committed (`a3b2ffc2`).
- `src/RimMandrake/{Graffiti,Inhabited,SacredGraffiti}/Assemblies/*.dll` —
  non-deterministic rebuild-only byte diffs (no source change), reverted with
  `git checkout` rather than committing noise, matching the pattern several
  agents used tonight.
- `infrastructure/state/modlists/ModsConfig_before_doorsexpanded_fix_2026-09-09.xml`
  — a real backup snapshot from tonight's doorsexpanded work, committed (`e714e7b0`).
- `src/RimUtinni/StructureInjectionsRUT/Source/Defs/` — real Vault-related content
  (SitePartDef/IncidentDef/HistoryEventDef/QuestScriptDef) dated today but not
  attributed to any of this window's own agent reports. Committed rather than
  risked through the reboot (`e714e7b0`) — **next seat: verify this against
  `VAULT_THAW_QUEST_FAMILY_1`'s actual current scope before assuming it's wired
  in; provenance is genuinely unconfirmed.**

A large volume of untracked `Transient/*.py`/`*.log`/`*.csv` scratch files predates
this window entirely (matches the session-start git status) — not touched, not this
handoff's concern, sweep candidates for `rimflow sweep --transient` in a future pass.

