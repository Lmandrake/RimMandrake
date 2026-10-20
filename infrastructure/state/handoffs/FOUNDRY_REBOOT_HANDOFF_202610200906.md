# FOUNDRY_REBOOT_HANDOFF_202610200906 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610200157`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Order (owner, 2026-10-19 ~11:25 PM, asleep): "Keep going until we are finally free and the world is repainted. I'd like to start tomorrow able to continue developing mods rather than retiring them." It is DONE and stands until he writes again: Waves 1-3 retired (live list = ModsConfig.FULL.LATEST = 374 mods), the dev world ASHKARR_DEV_START_2026-10-20.rws was painted on the 83-mod PAINT list and loads on the 374 list (live proof 05c140eae), scratch dirs moved to D:\ClaudeWork (rmpaths.py / RM_DATA_ROOT). Tomorrow starts at Transient/live_testing_2026-10-20e/RESULTS.md line 1. The one trap that cost hours: Alien Worlds starts every PAINT launch on the Default planet unless set_planet_type.py ran first; and the landing-site page cannot save a world (the stamper must not close it).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- 7 faction pop-ups on loading the dev start save on 374 (Gamorrean Clan, VFE Pirates x2, Splinter colony, Dungeon Pack x2, Roaming monstrosities): add them or never-ask is his call.
- Rock/slag chunks lost on 374 load (cosmetic, permanent at first save on 374).
- Dev start tile 17011 (17007 and 1621 border Zeddo's Toll 17006); moving that settlement 2 tiles frees 17007: his settlement, his call.
- Two ideoligions named The Salvation; a PAINT-clean variant exists beside the original; which to load is his call.
- Xeno heads: gene ears/eyes still draw over painted heads; Lasat/Nelvaanian/Ortolan heads still skin-tinted; fixes 2ff061f6e unverified live (XENO_HEADS_VERIFY_BALD_AND_BLUSHING).
- Rhossak sleep-pause default changed (agent default, his to overrule); A3 still unresolved.
- Aurora light fix and curtain art unverified live; real curtain textures were queued (RM_WS_AuroraCurtainA, AuroraGlowBand); his in-game look is owed.
- Brine crown undecided on his sheet; Deep Orbit in PAINT while AREAFIX2 fixtures live? (his call); 155 kept renders untouched.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `FORGE_SNAILHOLE_FILL_EMPTY_SHELL_LEFT_BEHIND` — Ummisk built (RM_Ummisk), frostbite fixed, art installed; live rows owed; NEXT: run the Ummisk steam/needs rows in the next live window
- `WORLD_LAYERS_RESCUE_THE_SAVE_HAS_MORE` — exporter built and used for the dev world; NEXT: close it with the dev-start proof sha 05c140eae
- `AURORAL_UMBRA_RENAME_BACK_TO_DARK` — aurora light patches built not deployed; NEXT: deploy at a game-down window and run checks V1-V7
- `RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD` — A3 unresolved, probes added; NEXT: redeploy Cauldron DLL and rerun A3 with the new probes
- `DEV_SCRATCH_DIRS_MIGRATE_OFF_LODESTARS_LAWN` — six dirs moved to D:\ClaudeWork; NEXT: tell BENCH to pull (177 behind) and decide Rimworld/reference/rimtools/govee_scan.ps1 with the owner
- `CAI_FOG_SILENCE_FORCED_OFF_BY_US` — filed; NEXT: measure CAI fresh-install fog default then force it off from one of our mods
- `XENO_HEADS_VERIFY_BALD_AND_BLUSHING` — fixes 2ff061f6e unverified; NEXT: spawn fresh pawns of the four xenotypes and check hair, Mimbanese colour, Ortolan east
- `GEO_LANDMARKS_SKETCH_BEFORE_THE_PAINT_DRIES` — filed (dev world exists; landmarks may be added later); NEXT: sketch hand-placed geological landmarks

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Alien Worlds defaults every PAINT launch to the Default planet without Worldbuilder (filed: lessons; see: Transient/world_remake_run_2026-10-20/RESULTS.md)
- Closing the landing-site page throws away the unsaved world (filed: lessons; see: commit 9c151fb92)
- Composed mods (Baroque Biomes) need deploy --compose biomes; a flat plan misses them (filed: lessons; see: Transient/live_testing_2026-10-20a/RESULTS.md)
- Prepatcher loads some DLLs twice: bridge type lookup hit the stale copy (see: 8c20f7577)
- Game conditions can only darken sky glow (LerpDarken min): ground light needs Harmony (see: design/RimMandrake/aurora_research_2026-10-20.md)
- Never put agent files in ~/dev: root is D:\ClaudeWork (see: ~/.claude/CLAUDE.md agent-storage rule)
- Codex image generation rate-limits bursts with HTTP 429 (see: Transient/art_regen_status_2026-10-20.md)

## Closed since the last handoff (1)

- `CAULDRON_YIELD_LIVE_RERUN_1` — e9d3ca356

## Filed and still open (10) — the next seat's queue

- `MINERALS_FW_RETIRE_ITS_MAPGEN_IN_HOUSE` — Retire MineralsFramework; reproduce whatever map step of it we rely on inside our own mods
- `PAINT_LIST_BUILD_ONLY_THE_NEEDED_MODS` — Define the minimal PAINT mod list: only mods needed to represent world, gravship, player characters (ours included)
- `BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND` — Each biome names its stones; basalt for volcanic biomes
- `PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS` — Superdeep pit cells reach a deeper stone stratum
- `STONE_BUILDSTATS_TUNE_GRANITE_GETS_RIVALS` — Stones that build differently (per-stone stuff stats)
- `GEO_LANDMARKS_SKETCH_BEFORE_THE_PAINT_DRIES` — Hand-placed geological landmarks planned for the paint (before-paint gate)
- `CAI_FOG_SILENCE_FORCED_OFF_BY_US` — Keep CAI 5000; force its fog setting off from one of our mods (measure CAI's fresh-install default first)
- `AURORAL_UMBRA_RENAME_BACK_TO_DARK` — Auroral Umbra: RUT_FuelSnows back to RUT_Umbra, perpetual aurora, propane rain, no snow
- `XENO_HEADS_SCENE_PROVE_ALIENS_WEAR_THEM` — Install the four picked xeno heads and screenshot aliens wearing them (owner wants to see; high-detail coloured heads untested)
- `XENO_HEADS_VERIFY_BALD_AND_BLUSHING` — Xeno heads polish: verify live (Lasat/Nelvaanian bald, Mimbanese red body + untinted head, Ortolan east head lowered)

## Commits

```
21ed2a447 conversations: catch-up 2 record(s)
19b041f4a Docs: last prose references to the old D:\Luke\dev runtime dirs
db2dd6361 Runtime dirs leave D:\Luke\dev for the data root: rmpaths.py, ~130 refs repointed
05c140eae live_testing_2026-10-20e: DEV_START healthy on 374 (UP, paused); 7 VEF new-faction dialogs, chunk loss, DewbackPack
0113f736e set_planet_type: keep sibling settings in the block, refuse a non-defName --type
afff19808 lessons: six from the 2026-10-20 world remake run
01704f8ae 06/15 remake docs: drop checkpoint C4, scenario defName RUT_Jawa_UtinniStart, start tile 17011 and why, AW planet-type trap, stage-6 label outcome
a0bf82250 start_site_select: re-assert selection until both read back; report selectionWrites
bca2d5cd0 live_testing_2026-10-20e: pin RESULTS (dev start save on 374; skeleton + offline censuses)
c3d94704b remake/set_planet_type.py: persist Alien Worlds planet type (TidallyLocked) in its Config file
d0601bcd5 RUT_GreentideAntFaction: make it generate at page-driven worldgen
854706fad The Salvation (PAINT-clean).rid: dev variant with off-PAINT memes/precepts/rituals stripped
d43794419 Remake run 2026-10-20: dev world start save (NOT promoted), runbook results, run log
9c151fb92 w9_run: stamp at the landing-site page; never clear_ui there
fcc49908d G5: guard 75 kept refs to non-PAINT mods (def-exists Conditionals, MayRequire, retag prereq guard shape)
629468943 code review: mark StartFlow + head_facing_fix files clean
0b4fb79c9 StartFlow ideo_load_rid: reflect before mutating, null-Game guard; head_facing_fix shift refuses faint-alpha clipping
ec6b21554 lesson: active mod != defs exist; fixtures need Deep Orbit
e50897eb3 Remake rehearsal R1-R4 on PAINT: G13/G17/G18 PASS, G2 FAIL for the fixture route (needs broms.deeporbit)
e53fa1dae JawaBench: scenario_select, start_site_select, ideo_load_rid (remake S4/S10/S5); built --gm, NOT deployed
... 67 more: git log --oneline 9027de7bf..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-20T09:05:47Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/flowworks_owner_walk_art_sheet_2026-10-11.decisions.json — FOUNDRY (this window, generated or helper scratch)
 M Transient/biome_ffar/phase0_remaining_art_sheet_2026-10-16.decisions.json — FOUNDRY (this window, generated or helper scratch)
 M Transient/forge_creature_concepts_sheet_2026-10-20.decisions.json — FOUNDRY (this window, generated or helper scratch)
 M Transient/modcheck/fixtures.json — FOUNDRY (this window, generated or helper scratch)
 M Transient/retirement_keepcut_sheet_2026-10-20.decisions.json — FOUNDRY (this window, generated or helper scratch)
 M deployed/config/ModsConfig.before-tier-fw_gss_sitting.xml — FOUNDRY (this window, generated or helper scratch)
 M infrastructure/state/code_review/FOUNDRY.jsonl — FOUNDRY (this window, generated or helper scratch)
 M infrastructure/state/ledger/events/FOUNDRY.jsonl — FOUNDRY (this window, generated or helper scratch)
 M infrastructure/state/ledger/events/OWNER.jsonl — FOUNDRY (this window, generated or helper scratch)
?? deployed/config/ModsConfig.before-tier-biomes_sprint.xml — FOUNDRY (this window, generated or helper scratch)
?? deployed/config/ModsConfig.before-tier-donor_off_phase0.xml — FOUNDRY (this window, generated or helper scratch)
?? deployed/config/ModsConfig.before-tier-donor_off_w4.xml — FOUNDRY (this window, generated or helper scratch)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261016T192502.json — FOUNDRY (this window, generated or helper scratch)
```

