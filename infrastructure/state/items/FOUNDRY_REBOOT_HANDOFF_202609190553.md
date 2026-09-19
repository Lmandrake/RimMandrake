# FOUNDRY_REBOOT_HANDOFF_202609190553 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609190051`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**Two live biomes are both named "the Pyrelands"** — one is the populated Ash'karr biome (222 tiles), the other (`ZBiome_Grasslands`-descended, whatever RIVER_STEAM_ANIMATION_1's original patches targeted) has **zero tiles anywhere on the frozen world**. Both `RiverSteamBiomeExtension` and the new drill-buildings' subsurface-liquid patch were silently wired to the empty one — confirmed by scanning all 21,872 surface tiles — and every doc and `get_def` call agreed with the wrong biome because nothing ever cross-checked tile count against a def name. Both patches are now retargeted to the real, populated Pyrelands. If a future feature "does nothing in the real campaign but works in isolated tests," check which of the two Pyrelands it actually targets before assuming the mechanism is broken.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **`CANONICAL_SAVE_MODLIST_DIVERGENCE_1` is bigger than first measured: 19 mods, not 16.** He authorized "scrub it now" for the 5 confirmed-deliberate absences (GravTech trio + ResearchReinvented SteppingStones + Biomes! Polluted Lands) — that scrub is done, backed up, byte-verified, zero cross-reference regressions. But the canonical save **still refuses to load**: 14 absences remain — Biomes! Caverns + 10 ArtOverride mods (his restore/scrub/force-load route choice, still open) plus **3 newly found and untraced**: `badoaks.meatonastick` (on disk, oddly resolves to two different Steam workshop folders), `badoaks.meatonastick.expansion` (not on disk at all — a Steam action to fix), `guy762.mm.kotorcore` (on disk, was just live-retired this session per his own approval — so this one may resolve itself once the save is regenerated after that retirement, but wasn't re-checked).
- **Orray south regen (his ruling, executed and closed)**: north/east untouched, south re-composed to match north's proportions and camera framing. One thing he didn't explicitly ask for: the head is now at the bottom of frame (receding from camera) instead of the top — matches north's composition and was necessary for the fix, but it's a visible change beyond "less fat." Review sheet: `D:\Luke\dev\Rimworld\Transient\orray_south_regen_2026-09-19.png`. Needs a game restart to see it in-game.
- **`jawa/map_drop` crashed the game this session** (Mono stack ends in the bridge's own JSON serialization). No work was lost — it happened cleanly before anything else — but treat that bridge call as session-ending until someone fixes it.
- **`RIVER_STEAM_ANIMATION_1` fully diagnosed, still blocked**: the wrong-biome bug (see "one thing to carry forward") is fixed, but the actual steam visual is blocked on an unrelated render-void bug in fresh map generation. Both previously-recorded workarounds were tried and falsified this session. Cheapest remaining path: he glances at a real Pyrelands river tile in the live campaign next time he's in it, rather than more bridge-side debugging of a repro that may not even be needed there.
- Minor ledger gap, not urgent: `biomesteam.biomespollutedlands`'s retirement was never added to `infrastructure/state/facts/retired_mods.json` even though the mod itself is correctly gone and its item is closed.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `TILEGEN_SILENT_REUSE_1` — fifth offline trace pass this session, extended the call-graph audit one layer deeper (MapGenerator/Game.FindMap/WorldObjectsHolder), found nothing new — the deterministic source is clean, blocked on `COLD_LOAD_RUN_SHEET_4` for a live repro; NEXT: when next doing a companion-DLL deploy cycle, re-repro the original two-distinct-tile case but check BOTH `jawa/world_tile_get` (terrain) AND `jawa/world_objects_get` (WorldObject occupancy) before trusting "tile is empty" — the 2026-09-10 finding says the original repro only checked the former.
- `CANONICAL_SAVE_MODLIST_DIVERGENCE_1` — 5 of 19 absences scrubbed from the save's `<meta>` mod list (backed up, byte-verified, zero cross-reference regressions); save still refused, 14 absences remain; NEXT: get the owner's restore/scrub/force-load ruling on the Caverns+10-ArtOverride route, then trace the 3 newly-found untraced entries (`badoaks.meatonastick` x2 variants, `guy762.mm.kotorcore`) before any further save edits.
- `VAULT_THAW_QUEST_FAMILY_1` — still BLOCKED; the mod-list scrub above does NOT unblock its live-fire test (V1/V6 siteTiles are real Ash'karr tile ids, no substitute save works); NEXT: once `CANONICAL_SAVE_MODLIST_DIVERGENCE_1`'s remaining 14 are resolved, bridge-fire `RUT_GiveQuest_VaultThaw_V1_RustCathedral` and `_V6_Umbra` on the real canonical save and confirm a Site WorldObject appears both times.
- `RIVER_STEAM_ANIMATION_1` — root cause found and fixed this session (wrong-biome targeting, see "one thing to carry forward"), both known render-void workarounds tried and falsified; NEXT: either fix the render-void bug in fresh map generation, or catch a live Pyrelands river tile during ordinary play and confirm the steam visual now fires.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — standing loop, waves 16/17/18 run this session, backlog went from ~15-20 DIRTY down to 4 (all live WIP on files another agent is actively editing, correctly left alone); the repo is essentially caught up for the first time; NEXT: re-run `code_review_status.py list` next session and continue at wave 19 whenever new DIRTY files accumulate.
- `DROIDWORKS_WIPE_SEVERITY_1` — retest still inconclusive; discovered THIS session that the reason is structural, not a fluke — no bridge tool can force-assign a DoBill job at all (see `BRIDGE_DOBILL_FORCE_TOOL_1` below); NEXT: do not attempt another live retest until that tool is built — it will fail the same way a fourth time.
- `BRIDGE_DOBILL_FORCE_TOOL_1` — filed this session with the exact fix already designed (call the real `WorkGiver_DoBill.JobOnThing` instead of hand-building a Job); NEXT: build `jawa/do_bill_now` per the `rimbridge-companion` skill next time the game is down for a companion-DLL deploy — this has now cost 3 separate live passes across 3 different sessions.
- `SYSTECH_ELECTRIC_BOLT_1` — filed this session; the Systech Static Blaster lost its distinctive electric projectile when `guy762.mm.kotorcore` was retired; NEXT: implement the projectile effect natively in Armoury rather than depending on the donor mod's asset.
- `DRILL_IMPASSABLE_FILLPERCENT_1` — filed this session from a live cold-load error diff; NEXT: read the config-error text on `RM_LiquidDrill` (impassable-but-shootable-over conflict) and fix the ThingDef's `passability`/`fillPercent` combination.
- `KCSG_PAWNKIND_COLONIST_FALLBACK_1` — filed and then corrected same-day (it's a `PawnGenerator` fallback bug reaching raids/rosters too, not KCSG-specific); NEXT: read the item fresh (it was corrected after filing) before scoping the fix.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `rimflow close --sha <hand-typed-sha>` can silently misattribute in a shared worktree: if the flag isn't actually captured by the shell (typo, wrong quoting), `cli.py` falls back to `head_sha()` at call time and grabs whatever a concurrent peer just pushed. Always pass it as `--sha $(git rev-parse HEAD)`, never a literal string (filed: LESSONS_INBOX).
- `selftest_tool_metadata` was a stale instrument, not a real regression: it subtracted `build.GM_TOOLS` (the build script's own comment calls it a two-name spot check) as if it were the WHOLE `#if`-gated tool set, so a healthy 284/284 build read as "41 tools missing" — a scanner reading `#if` regions line-by-line also returns a false 0-gated count, since `[Tool(` and its name sit on separate lines (filed: LESSONS_INBOX, see `SELFTEST_FAILURE_TRIAGE_1`).
- `validate_sprite.py`'s reference-vs-candidate REJECT is out of scope for a `Graphic_Random` sibling variant — those are MEANT to differ in span/aspect/origin from a reference. Use the reference-INDEPENDENT checks (canvas, alpha, corners, fringe, duplicate pixel-hash) for that class of art instead (filed: LESSONS_INBOX).
- LANCZOS resampling on a sprite with sub-visible alpha dust amplifies it via ringing (measured 1055→3452px on one Zeer facing) — worse than the defect being fixed. BOX (area-averaging) was the only one of 4 resamplers tested that never made a file worse than it found it (filed: LESSONS_INBOX).
- An `art_checks.py` "must NOT flag" pin can pass vacuously if the pinned file is later deleted — it never actually re-asserts the file still exists and is clean. Any such pin needs a paired assertion the file is present, proved by pointing it at a nonexistent name and confirming that fails (filed: LESSONS_INBOX).
- Subagent background-wait deadlock hit again this session (code-review wave 17 backgrounded its own command and then waited passively for a notification it would never get as a subagent) — nudge with SendMessage telling it to poll its own job directly, per the existing lesson (see: memory `subagent-background-wait-deadlock-brief-line`).

## Closed since the last handoff (15)

- `BIOME_FLORA_GENERATOR_REPAIR_1` — 366c278d6830249b0ae39522371eaf810d9fa297
- `PROPANE_LAKES_ROSTER_STALE_1` — 9350e29a33a276cd190ef1ce0806f5f523e01389
- `POLLUTED_LANDS_FLORA_PORT_1` — e4ab343f3d3abf7ed5a57f8cef391429af0dd0f4
- `FLUID_SOURCE_STOCK_MODEL_1` — d029ea4f9
- `CANAL_FILL_IN_DISPLACEMENT_1` — 7680d6ab4
- `MLIE_FAUNA_ABSORPTION_1` — 0d1313d99
- `TAR_VISCOUS_SURFACE_ART_1` — 3f9a899d9ae8e2166b67c04470ba0477af9d921c
- `EMBERGRASS_LEAFLESS_ALTS_1` — 2687b48b614fc5798793b9c779d309eb6506afca
- `SELFTEST_FAILURE_TRIAGE_1` — 695e87683cb90d52bb5f0f7d26e0d8fef844b833
- `ZEER_EAST_TOP_CLIP_1` — af9a1f94b3e6446e489c7f4bae503a63cd1eaa65
- `ASHFALL_RESEARCH_BASE_1` — 47a724ca5f02d3966fa1cfcc8a65a21c8bf4d437
- `ART_SELFTEST_CORPUS_IN_TRANSIENT_1` — fff24a4d49d4cb34f8b901cb5301d488e8c735b3
- `STICK_FOOD_INGEST_1` — b4bb02cd2ea6ec65762b4591b76dd5a2a45d5489
- `WEAPONS_DONOR_RETIREMENT_1` — db2d7888285c223d55ad7440d25cb54d9e5c5dff
- `MANY_WATERS_DRILL_BUILDINGS_1` — 19b1f7f3a7efa8ba021a6ec2432c0d0ce5bc5d4d

## Filed and still open (11) — the next seat's queue

- `CANONICAL_SAVE_CUT_RESIDUE_1` — The start save loads on the 621 list but drops content: MEASURED Load C 2026-09-19 (load_game with ignoreModCompatibility) 4,828 'Could not load refer
- `CUT_FALLOUT_GENERATED_DATA_1` — Load C fallout from the Caverns + Polluted Lands cuts (MEASURED 2026-09-19, Transient/harvest_loadC_triage_2026-09-19.md): ~90 new patch failures and 
- `MLIE_GENERATED_BIOME_COLLISIONS_1` — AnimalBiomeDuplicates_Generated.xml still carries bare-donor duplicate-animal collisions for GraniteSlug x ExtremeDesert, Cannok/Sketto x AridShrublan
- `SWBESTIARY_DEPLOY_STALE_1` — deployed/Mods/SWBestiary is stale - 26 files behind src/, missing RSW_Scurrier/RSW_WarWyrm/RSW_Urusai and likely other recently-ported Mlie species en
- `BIOME_CONFIGERRORS_NRE_1` — NullReferenceException inside BiomeDef.ConfigErrors() on 5 biomes at startup (AridShrubland, Desert, ExtremeDesert since 2026-09-06; +AB_MiasmicMangro
- `CANONICAL_SAVE_MODLIST_DIVERGENCE_1` — CANONICAL_ASHKARR_START_2026-09-12.rws records 635 mods; the live list is 621 and lacks 16 of them - Biomes! Caverns and 10 mandrake.rut.*ArtOverride 
- `BRIDGE_DOBILL_FORCE_TOOL_1` — No bridge tool can start a DoBill job, so no recipe's ApplyOnPawn can ever be force-verified. MEASURED offline 2026-09-19 by reading JawaBenchZoneTool
- `KCSG_PAWNKIND_COLONIST_FALLBACK_1` — KCSG pawn symbols silently fall back to vanilla Colonist, so a layout's pawn roster is nondeterministic
- `ROT_FAUNA_KIN_WIRING_1` — Wire the ruled Rot fauna kin/alarm table onto the 16 race defs (UtinniPatches, FindMod-gated) — AFTER BMT_FAUNA_ABSORPTION_1 renames the BMT_ rows
- `SYSTECH_ELECTRIC_BOLT_1` — The Systech Static Blaster lost its distinctive electric projectile when kotorcore retired
- `DRILL_IMPASSABLE_FILLPERCENT_1` — RM_LiquidDrill logs a config error: impassable but shootable over

## Commits

```
9636b3347 rimflow: bridge released, game state corrected to UP
993b6786c Correct KCSG_PAWNKIND_COLONIST_FALLBACK_1: it is not a KCSG bug
57d4be074 rimflow: wave 2 sync — 4 closed, river steam blocked on the render void
19b1f7f3a File DRILL_IMPASSABLE_FILLPERCENT_1 from the live load's error diff
db2d78882 Two defs the kotorcore retirement broke, caught by the cold load
495d6b3c2 CANONICAL_SAVE_MODLIST_DIVERGENCE_1: record the scrub, correct the absence set to 19
a1616da5e rimflow: sync ledger (CANONICAL_SAVE_MODLIST_DIVERGENCE_1 scrub + VAULT_THAW_QUEST_FAMILY_1 still blocked)
32f1d34c2 CANONICAL_SAVE_MODLIST_DIVERGENCE_1: scrub 5 retired packageIds from the canonical save's meta mod list
c2912bcde rimflow: sync ledger (ORRAY_FACING_HEIGHT_REGRESSION_1 closed at b4bb02cd2)
b4bb02cd2 ORRAY_FACING_HEIGHT_REGRESSION_1: regen Orray south on the owner's ruling
8c5c734e1 ROT_HEALTH_SHARING_1: kin-mending heal scales with body size (owner ruling)
2ae43cf20 rimflow: sync ledger (ART_SELFTEST_CORPUS_IN_TRANSIENT_1 closed at fff24a4d4)
139598a68 CANONICAL_SAVE_MODLIST_DIVERGENCE_1: trace the 5 unexplained mod absences
fff24a4d4 art_checks.py: selftest corpus declared in-repo, not staged in Transient/
772dc215a rimflow: sync ledger (ORRAY_FACING_HEIGHT_REGRESSION_1 note — sheet built)
c962f1f1d Transient: Orray facing-height review sheet for the owner to LOOK at
7440686fc FlowWorks: correct the river-steam hook's stale biome comment
5789a3de5 rimflow: ASHFALL_RESEARCH_BASE_1 closed; KCSG pawnkind fallback filed
47a724ca5 lessons: map_drop crashes the game; biome gates need a tile count
f7e2bd21c Pyrelands wiring pointed at a biome with ZERO tiles; kotorcore retired
... 101 more: git log --oneline 6cd51f64b..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-19T05:52:02Z

Uncommitted (replace each UNVERIFIED - not mine, not traced further with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   health-publisher daemon, not mine
 M Transient/codebase_health.json   health-publisher daemon, not mine
 M Transient/codebase_health_artifact.html   health-publisher daemon, not mine
D  infrastructure/artpipe/pending/crystalcap_b_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/crystaltipbrambles_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/crystaltipbrambles_b_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/dulciscropitem_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/dulcisgrown_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/dulcisharvested_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/dulcisimmature_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/fungusfern_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/fungusfern_b_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/fungusfern_c_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/fungusfern_d_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/gleamtip_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/gleamtip_b_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/greyladygrown_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/greyladygrown_b_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/greyladygrown_c_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/greyladyimmature_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonechunk_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonechunk_b_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonechunk_c_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonechunk_d_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonehuge_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonehuge_b_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstoneitem_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstoneitem_b_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstoneitem_c_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonelarge_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonelarge_b_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonemedium_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonemedium_b_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonemedium_c_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonesmall_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonesmall_b_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonesmall_c_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonesowableimmature_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstoneterrain_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/lanternstonewallicon_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/luminousspout_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/luminousspout_b_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/mycelium_a_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/mycelium_b_v1.json   artpipe daemon queue/output, not mine
D  infrastructure/artpipe/pending/mycelium_c_v1.json   artpipe daemon queue/output, not mine
 D infrastructure/artpipe/pending/nuitae_a_v1.json   artpipe daemon queue/output, not mine
 D infrastructure/artpipe/pending/nuitae_b_v1.json   artpipe daemon queue/output, not mine
 D infrastructure/artpipe/pending/yumbulbs_a_v1.json   artpipe daemon queue/output, not mine
 D infrastructure/artpipe/pending/yumbulbs_b_v1.json   artpipe daemon queue/output, not mine
 M infrastructure/artpipe/registry.jsonl   artpipe daemon bookkeeping, not mine
 M infrastructure/artpipe/throughput.jsonl   artpipe daemon bookkeeping, not mine
 M infrastructure/dashboards/hub/data/health.json   health-publisher daemon, not mine
 M infrastructure/state/codebase_health_last.json   health-publisher daemon, not mine
 M src/RimMandrake/CreatureBehaviors/Assemblies/RimMandrake.CreatureBehaviors.dll   build artifact, UNVERIFIED - not mine, not traced further
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   stray tool-call artifact, not mine, safe to ignore
?? defs.sqlite   UNVERIFIED - not mine, not traced further
?? deployed/config/ModsConfig.before-tier-oracle.xml   BENCH's pre-deploy ModsConfig backups, not mine
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   BENCH's pre-deploy ModsConfig backups, not mine
?? deployed/config/ModsConfig.before-tier-warlab.xml   BENCH's pre-deploy ModsConfig backups, not mine
?? infrastructure/artpipe/daemon_run_20260916_bench_restart.log   artpipe daemon log, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_east.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_north.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_south.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_east.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_north.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_south.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/nuitae_a_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/nuitae_a_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/nuitae_b_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/nuitae_b_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/twistingthornweed_v1_r2.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/yumbulbs_a_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/yumbulbs_a_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/yumbulbs_b_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/done/yumbulbs_b_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/codexcal_mantrap_r4.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/nysyllin_v1_r2.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_agelesscap_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_agelesscap_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_brewingvessel_v1_south.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_brewingvessel_v1_south.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_euphoriccrown_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_euphoriccrown_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_falsefruit_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_falsefruit_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_furnacecap_plant_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_furnacecap_plant_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_gene_furnaceblood_icon_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_gene_furnaceblood_icon_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_grownfurnace_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_grownfurnace_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_liveingredient_agelesscap_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_liveingredient_agelesscap_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_liveingredient_euphoriccrown_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_liveingredient_euphoriccrown_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_liveingredient_regenerantveil_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_liveingredient_regenerantveil_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_liveprep_toxicinjection_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_liveprep_toxicinjection_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_livingfurnacecap_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_livingfurnacecap_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_palemoss_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_palemoss_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_paletree_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_paletree_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_regenerantveil_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_regenerantveil_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_symbiont_mycoid_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_symbiont_mycoid_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_symbiont_nightwake_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_symbiont_nightwake_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_symbiont_quickflesh_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_symbiont_quickflesh_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_symbiont_sheenblood_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_symbiont_sheenblood_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_tea_agereversal_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_tea_agereversal_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_tea_bioregeneration_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_tea_bioregeneration_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_tea_pleasure_v1.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/rut_tea_pleasure_v1.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine
?? infrastructure/state/.rimflow_conc_97j8px_9/   rimflow concurrency scratch dir, not mine
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing since 2026-09-11, not mine
?? infrastructure/state/modlists/ModsConfig.FULL.PRECAPTURE.20260918_213026.xml   BENCH's dump-capture snapshot, not mine
?? src/RimUtinni/LanternDeeps/build_species_sheet.py   BENCH mid-edit scratch script, not mine, left alone
?? src/RimUtinni/RotSporeKit/build_review_sheet.py   BENCH mid-edit scratch script, not mine, left alone
```

