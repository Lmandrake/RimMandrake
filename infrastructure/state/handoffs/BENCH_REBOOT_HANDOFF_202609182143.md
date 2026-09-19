# BENCH_REBOOT_HANDOFF_202609182143 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609181226`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

**The Lantern Deeps pocket map had NEVER generated correctly under any version — donor
route included — and nothing on disk could have told you.** The quicktest that
`LANTERN_DEEPS_INJECTION_1` sat blocked on since filing found three engine facts (all
MEASURED from decompiled source, all in `Patch_PocketMapGrowthRate.cs` /
`GenStep_LanternstoneRock.cs` headers, commit `201237241`): a pocket map's parent has NO
tile, so (a) `BiomeDef.extraRockTypes` is dead there (`World.RockAllowedInBiome` returns
false for an invalid tile), (b) `Map.FinalizeInit` THROWS for any pocket biome with
grazable wild plants (vanilla's Undercave survives only by having none) and leaves a
half-initialised map that NREs every frame, and (c) without
`pocketMapProperties.tileMutators/UndergroundCave` nothing digs. Also: under a natural
roof vanilla only spawns global `cavePlant` defs, so a Deep grows its flora only through
our own planter. ⇒ **Any future pocket-map biome (the Forge tower floor, a vault) hits
the same four walls. Read those two class headers before designing one.**


## What the owner should see

- **The Deep exists now.** `Transient/_deeps_owner2.png` — first successful generation,
  live on a 10-mod list with the donor ABSENT: 525 lanternstone walls, 21 formations (all
  four sizes), 121 plants / 9 species, 0 exceptions, a colonist walked in. Red floor and
  purple ✕ are missing textures (art below). Blue-veined walls are our generated atlas.
- **LanternDeeps now carries a Harmony patch** (its first) — `About.xml` declares
  `brrainz.harmony`. Deliberate; the alternative (giving pocket maps a fake valid tile)
  changes semantics for 632 mods. Veto-able: revert `Patch_PocketMapGrowthRate.cs` and
  the map dies at FinalizeInit again.
- **Lanternstone density looks LOW and random** across three seeds: 39 → 2 → 21
  formations on 4,356 cells. Mechanically fine; whether that is the Deep he wants is a
  Mod Settings slider (`lanternstoneDensityMultiplier`) and his eye.
- **Two "raw dulcis" items now exist** (`RUT_DeepRawDulcis` vs RotSporeKit's
  `RUT_RawDulcis`) and will not stack. Owed dedup, his call which mod owns it.
- **Art review sitting is nearly ready**: 44/49 Deeps sprites rendered + facts-PASS in
  `infrastructure/artpipe/_artsrc/`, 3 rendered ungated, 1 FAILED (`lanternstonemedium_a`),
  4 in flight (nuitae a/b, yumbulbs a/b). He ruled ONE sheet, one sitting — build it when
  the last 4 land, do not serve partials.
- Peer attribution: `e8aa044f0` (mine) swept the other window's 7 uncommitted Pass-21
  `cast_assignment.csv` rows under my message. Nothing lost; noted on
  `MLIE_FAUNA_ABSORPTION_1`.


## What is half-done, and where it stops

- `CAVERNS_PARITY_BUILD_1` -- doing; Load B (full 632 list, dump ARMED) launched 14:39
  and was still loading at handoff. NEXT: when `Bridge token:` appears in Player.log,
  run `python.exe src/RimMandrake/Utils/harvest_log.py`, then
  `python3 src/RimMandrake/Utils/validate_save_artifact.py "src/Jawa/ideoligion/The Salvation.rid"`
  against the NEW capture (expect 0 dangling, was 1), then regenerate
  `BiomeCast_Ashkarr.xml` via `gen_cast_patch.py` and diff (the old capture lacked
  live RSW_ kinds — `infrastructure/state/EXPECTED_FAILURES_next_load.md` Load B has every
  string). ⚠️ `DefDump/dump_request.txt` is NOT consumed — delete it after the capture.
- `CAVERNS_PARITY_BUILD_1` -- the cut itself. NEXT: after BiomeCast regen, Caverns + Core
  leave ModsConfig (scoping doc §4 step 3); Fossils is MEASURED clean to cut (0 of 95
  defNames in the canonical save). Strip the 3 inert `loadAfter` BiomesCore lines
  (Armoury/Doctrine/PawnFlavor About.xml) in the same change.
- `CAVERNS_PARITY_BUILD_1` -- art wiring. NEXT: once his one-sheet review passes, copy
  approved PNGs from `_artsrc/` to `src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/…`
  per ART_JOBS.md paths (the terrain job ran opaque `#05070d`), redeploy, quicktest.
- `RESEARCH_TRIO_RETIRE_1` -- unblocked on his card ("Port all 17, then cut"), FOUNDRY's.
  NEXT: port the 17 ResearchProjectDefs + GravForge's building, deploy-HOLD them until
  the donors leave ModsConfig (silent defName overwrite otherwise).
- `WORLDMAP_DOCS_PASS_1` -- doing (his sitting). NEXT: post-restart tails only —
  REGIONS_THAT_LIE re-audit, river-endpoint check; card only still-true rows.
- `EXPLOSIVE_PLANT_GROWTH_1`, `VAPOR_EMITTER_PLACEMENT_1`, `FLOOD_WITNESS_EVENT_1`,
  `WORLDMAP_FINAL_REVIEW_1`, `ASSIGNMENT_SHEETS_VERDICT_SITTING_1`, `ART_PIPELINE_DAEMON_1`,
  `DUNGEON_SETPIECE_TEXT_1` -- inherited `doing`, untouched this wave (owner sittings /
  long-running). NEXT: leave them; pick one up only when he opens it.


## Traps learned

- `git commit <path>` commits the WORKTREE file, not a blob staged via `update-index` —
  a peer's uncommitted lines in a shared file ride along (filed: memory
  `pathspec-commit-takes-worktree-not-index`).
- Two subagents parked "waiting for the notification" on a background command; none
  reaches them. Brief: FOREGROUND only, explicit timeout, never run_in_background/Monitor;
  `SendMessage` "poll it yourself" resumes a parked one (filed: memory
  `subagent-background-wait-deadlock-brief-line`).
- `rimworld/take_screenshot` ignores x/z/zoom; `rimworld/clear_log` empties but does not
  CLOSE the debug window — `jawa/window_list_close typeName=EditWindow_Log` does. LOOK at
  the PNG before sending it (filed: LESSONS_INBOX).
- `rimbridge_client.py` scraped a token the bridge rejected while the log held the right
  one; passing `token=` explicitly works. `$(cat token)` on the CLI also failed — use the
  library from `python.exe` (see: Transient/_deeps_*.py, throwaway).
- `/mnt/c` reads of Player.log can be stale (17 KB frozen); read it with `python.exe`
  when a number looks stuck (see: memory `drvfs-stale-reads-mimic-revert`).
- `biome_flora.py` cannot regenerate its own output (80 baseline check failures: FAMILIES
  keys on pre-rename biome names) — every edit since the rename was a hand-edit the
  generator would revert (see: `BIOME_FLORA_GENERATOR_REPAIR_1`).


## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (3) — the next seat's queue

- `DEEPCALM_AMBIENT_SOUND_1` — Lantern Deeps ambient sound: RUT_DeepCalm ships silent - author/source an owned cave-hum SoundDef (the sheet's 'hum rising to a Chorus'), donor .ogg d
- `POLLUTED_LANDS_FLORA_PORT_1` — Polluted Lands cut step 2: port-or-cut its ~40 injected plants (21 BMT_ rows still live in BiomeFlora_Ashkarr with no RUT twin) + inert-check the 52 W
- `BIOME_FLORA_GENERATOR_REPAIR_1` — biome_flora.py cannot regenerate BiomeFlora_Ashkarr.xml: FAMILIES still keys on pre-rename biome defNames (AB_MycoticJungle, ZBiome_Badlands, Wastelan

## Commits

```
 M Transient/codebase_health.html   <<< health publisher (auto, _trigger_health_rebuild) >>>
 M Transient/codebase_health.json   <<< health publisher (auto, _trigger_health_rebuild) >>>
 M Transient/codebase_health_artifact.html   <<< health publisher (auto, _trigger_health_rebuild) >>>
D  infrastructure/artpipe/pending/crystalcap_b_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/crystaltipbrambles_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/crystaltipbrambles_b_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/dulciscropitem_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/dulcisgrown_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/dulcisharvested_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/dulcisimmature_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/fungusfern_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/fungusfern_b_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/fungusfern_c_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/fungusfern_d_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/gleamtip_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/gleamtip_b_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/greyladygrown_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/greyladygrown_b_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/greyladygrown_c_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/greyladyimmature_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonechunk_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonechunk_b_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonechunk_c_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonechunk_d_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonehuge_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonehuge_b_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstoneitem_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstoneitem_b_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstoneitem_c_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonelarge_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonelarge_b_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonemedium_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonemedium_b_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonemedium_c_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonesmall_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonesmall_b_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonesmall_c_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonesowableimmature_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstoneterrain_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonewallicon_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/luminousspout_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/luminousspout_b_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/mycelium_a_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/mycelium_b_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/mycelium_c_v1.json   <<< unknown — check `git log -1 -- <path>` >>>
 M infrastructure/artpipe/registry.jsonl   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
 M infrastructure/artpipe/throughput.jsonl   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
 M infrastructure/dashboards/hub/data/health.json   <<< health publisher (auto, _trigger_health_rebuild) >>>
 M infrastructure/state/MODE   <<< owner's mode file — not mine >>>
 M infrastructure/state/codebase_health_last.json   <<< health publisher (auto, _trigger_health_rebuild) >>>
 M infrastructure/state/facts/mlie_wave_c_worklist.json   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
 M infrastructure/state/ledger/events.jsonl   <<< ledger appends after my last commit — either seat; commit with the next note >>>
 M infrastructure/state/queue/BENCH.md   <<< ledger appends after my last commit — either seat; commit with the next note >>>
 M infrastructure/state/queue/FOUNDRY.md   <<< ledger appends after my last commit — either seat; commit with the next note >>>
 M src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
?? Transient/CANONICAL_ASHKARR_2026-09-09.rws.bak-pre-landmark-rename-2026-09-10   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/ModsConfig.pre_enable_2mods_2026-09-18.xml   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/Player.log.deeps_quicktest_loadA_2026-09-18   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/Player.log.gridload_worldgen_crash_2026-09-17   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/Player.log.pre_caverns_window_2026-09-18   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/Player.log.pre_fullload_2026-09-17   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/Player.log.pre_gridload_2026-09-17   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/Player.log.pre_restart_enable_injections_2026-09-18   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/Player.log.pre_rotwave_20260918   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/Player.log.rotwave_session_2026-09-17   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_biome_names.txt   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_bridge_token.txt   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/_col_test.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_deeps_a.py   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/_deeps_b.py   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/_deeps_c.py   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/_deeps_d.py   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/_deeps_e.py   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/_deeps_f.py   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/_deeps_g.py   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/_deeps_h.py   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/_deeps_loadA_screen.bmp   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/_deeps_loadA_screen.png   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/_deeps_parity.png   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/_destroy_dialog.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_destroy_dialog.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_dialog_check.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_dialog_check.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_dialog_check2.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_dialog_check2.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_fh_cellrect.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_fh_close2.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_fh_close3.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_fh_deliverable.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_fh_deliverable2.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_fh_final.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_fh_full.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_fh_lit.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_fh_lit2.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_fh_sand.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_fh_v1.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_fh_wide.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_focus_check.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_focus_check.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_focus_now.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_focus_now.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_gridload_state.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_gridload_state.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_gridload_state2.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_gridload_state2.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_lanterndeeps_atlas_work/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_logread.py   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/_pits_demo.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_pits_demo.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_pits_demo2.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_pits_demo2.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_pits_sprung.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_pyre_v2.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_pyre_v3.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_pyre_v4.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_pyre_wake_state.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_pyre_wake_state.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_rot/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_tools_451.txt   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/_tools_now.txt   <<< MINE — throwaway bridge scripts/logs from the Deeps quicktest; bin freely >>>
?? Transient/apparel_gate/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/art_gen/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/art_review_generic_marks/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/biomes_caverns_deepscan_2026-09-18.md   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/c4_trade/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/check1.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/check2.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/decay_batch_A_2026-09-18.md   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/decay_batch_B_2026-09-18.md   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/decay_batch_C_2026-09-18.md   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T141934Z.bak   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T142307Z.bak   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T142518Z.bak   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T143755Z.bak   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T150644Z.bak   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T161224Z.bak   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T163101Z.bak   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T165007Z.bak   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T165327Z.bak   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T165526Z.bak   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T165614Z.bak   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T170108Z.bak   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T173327Z.bak   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T173627Z.bak   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/flap_check.py   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/flapchk_A.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/flapchk_ABC.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/flapchk_B.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/flapchk_C.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/flapzoom_A.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/flapzoom_B.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/flapzoom_C.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/foundry_state_check.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/git_efficiency_audit_2026-09-13.md   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/graffiti_variants/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/harvest_crossref_2026-09-18_1035.txt   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/harvest_discarded_2026-09-18_1035.txt   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/harvest_patchfail_2026-09-18_1035.txt   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/harvest_rotwave_session_2026-09-17.txt   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/harvest_scribe_2026-09-18_1035.txt   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/hawk1_A.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/hawk1_AB.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/hawk1_B.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/hawk2_A.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/hawk2_AB.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/hawk2_B.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/hawk_center_A.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/hawk_center_B.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/hawk_close_A.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/hawk_close_B.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/load_stall2_2026-09-11.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/load_stall_2026-09-11.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/loadercaps/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/mapgen_gl/apparelmoney2/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/mapgen_gl3/shots/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/meshfuse_multiview/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/mlie_pass9_extract/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/mlie_waveb_extract/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/modcheck/Pits_20260913T203104Z.html   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/modcheck/Pits_20260913T203625Z.html   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/modcheck/Pits_20260913T203959Z.html   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/modcheck/Pits_20260913T204215Z.html   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/mw2_disentanglement_review_2026-09-13.md   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_anim_wide.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_anim_wide_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_animals_grass.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_animals_grass_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_animals_over.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_animals_over_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_artgrid.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_artgrid_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_ashfall_live.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_ashfall_live_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_choked_grass.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_choked_grass_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_choked_v2.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_choked_v2_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_daylight_grid.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_daylight_grid_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_defread.py   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_density155_A.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_density155_A_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_density155_center.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_density155_center_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_faced.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_faced_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_fix2.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_fix_overview.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_flapA.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_flapA2.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_flapB.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_flapB2.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143618.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143618_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143619.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143619_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143620.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143620_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143621.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143621_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_hawk_rectA__cell_rect.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_hawk_rectB__cell_rect.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_live1_ashfall_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_live1_clear_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_mech_check.py   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_stage_test.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyre_stage_test_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150446.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150446_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150448.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150448_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150449.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150449_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150450.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150450_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyregrid2_145955.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyregrid2_145957.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyregrid2_145958.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyregrid2_145958_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyregrid2_145959.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyrelands_live_first_look.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyrelands_live_first_look_sm.png   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/pyrelands_quicktest_2026-09-13/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/research_trio_briefing_2026-09-18.md   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/rimworld_state_check.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/rot_fauna_assignment_draft_20260918.md   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/sea_raw/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/system_screenshot_2026-09-09.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/triposr_prototype/   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/verify1.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/verify2.bmp   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/world_neighbors_2026-09-18.csv   <<< unknown — check `git log -1 -- <path>` >>>
?? Transient/worldmap_docs_pass_agenda_2026-09-18.md   <<< unknown — check `git log -1 -- <path>` >>>
?? "\\wsl.localhost\Ubuntu\tmp\tools_dump.txt"   <<< stray/scratch from an earlier session — not mine, safe to ignore >>>
?? defs.sqlite   <<< stray/scratch from an earlier session — not mine, safe to ignore >>>
?? deployed/config/ModsConfig.before-tier-oracle.xml   <<< stray/scratch from an earlier session — not mine, safe to ignore >>>
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   <<< stray/scratch from an earlier session — not mine, safe to ignore >>>
?? deployed/config/ModsConfig.before-tier-warlab.xml   <<< stray/scratch from an earlier session — not mine, safe to ignore >>>
?? infrastructure/artpipe/active/rut_agelesscap_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_brewingvessel_v1_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_euphoriccrown_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_falsefruit_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_furnacecap_plant_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_gene_furnaceblood_icon_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_grownfurnace_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_liveingredient_agelesscap_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_liveingredient_euphoriccrown_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_liveingredient_regenerantveil_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_liveprep_toxicinjection_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_livingfurnacecap_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_palemoss_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_paletree_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_regenerantveil_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_symbiont_mycoid_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_symbiont_nightwake_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_symbiont_quickflesh_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_symbiont_sheenblood_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_tea_agereversal_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_tea_bioregeneration_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_tea_pleasure_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/daemon_run_20260916_bench_restart.log   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kinrath_v1_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kinrath_v1_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kinrath_v1_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kreetle_v1_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kreetle_v1_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kreetle_v1_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/twistingthornweed_v1_r2.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/codexcal_mantrap_r4.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/nysyllin_v1_r2.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/state/.rimflow_conc_97j8px_9/   <<< stray/scratch from an earlier session — not mine, safe to ignore >>>
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   <<< stray/scratch from an earlier session — not mine, safe to ignore >>>
?? infrastructure/state/items/BENCH_REBOOT_HANDOFF_202609182143.md   <<< unknown — check `git log -1 -- <path>` >>>
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Runyip.xml   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Scavrat.xml   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Scurrier.xml   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
?? src/RimStarWars/SWBestiary/Textures/swanimals/Runyip/   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
?? src/RimStarWars/SWBestiary/Textures/swanimals/Scavrat/   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
?? src/RimStarWars/SWBestiary/Textures/swanimals/Scurrier/   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
```

## Game / bridge / tree state at wrap

- **Game LOADING the full 632 list** (launched 14:39 via Steam, dump marker ARMED,
  `EXPECTED_FAILURES_next_load.md` Load B holds the decision strings). At handoff the
  bridge had not yet answered; a bare `./game` reads LOADING as a DEFAULT. ⛔ Nothing
  is loaded that must be saved — a quicktest or restart is always safe.
- **Bridge FREE** — I released it at handoff (owner had handed it to me: "You have the
  bridge."). Whoever harvests Load B takes it.
- **ModsConfig = FULL.LATEST = 632 active (MEASURED)**; the minimal list is NOT live.
  Old FULL (630) archived as `ModsConfig.FULL.PRECAPTURE.20260918_141403.xml`.
- **Deployed this window**: LanternDeeps whole (hold lifted), UtinniPatches (precept def
  + sweep), `Ideos/The Salvation.rid` (backup `The Salvation.pre_precept_swap_20260918.rid.bak`).
- Copied-out logs: `Transient/Player.log.pre_caverns_window_2026-09-18` (his session),
  `Transient/Player.log.deeps_quicktest_loadA_2026-09-18` (the 10-mod proof).

Uncommitted at wrap (359 paths), attributed:

```
 M Transient/codebase_health.html   <<< health publisher (auto) >>>
 M Transient/codebase_health.json   <<< health publisher (auto) >>>
 M Transient/codebase_health_artifact.html   <<< health publisher (auto) >>>
D  infrastructure/artpipe/pending/crystalcap_b_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/crystaltipbrambles_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/crystaltipbrambles_b_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/dulciscropitem_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/dulcisgrown_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/dulcisharvested_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/dulcisimmature_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/fungusfern_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/fungusfern_b_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/fungusfern_c_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/fungusfern_d_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/gleamtip_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/gleamtip_b_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/greyladygrown_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/greyladygrown_b_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/greyladygrown_c_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/greyladyimmature_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonechunk_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonechunk_b_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonechunk_c_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonechunk_d_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonehuge_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonehuge_b_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstoneitem_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstoneitem_b_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstoneitem_c_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonelarge_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonelarge_b_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonemedium_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonemedium_b_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonemedium_c_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonesmall_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonesmall_b_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonesmall_c_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonesowableimmature_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstoneterrain_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/lanternstonewallicon_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/luminousspout_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/luminousspout_b_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/mycelium_a_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/mycelium_b_v1.json   <<< unknown — `git log -1 -- <path>` >>>
D  infrastructure/artpipe/pending/mycelium_c_v1.json   <<< unknown — `git log -1 -- <path>` >>>
 M infrastructure/artpipe/registry.jsonl   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
 M infrastructure/artpipe/throughput.jsonl   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
 M infrastructure/dashboards/hub/data/health.json   <<< health publisher (auto) >>>
 M infrastructure/state/MODE   <<< owner's mode file >>>
 M infrastructure/state/codebase_health_last.json   <<< health publisher (auto) >>>
 M infrastructure/state/facts/mlie_wave_c_worklist.json   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
 M infrastructure/state/ledger/events.jsonl   <<< ledger appends since my last commit — commit with the next note >>>
 M infrastructure/state/queue/BENCH.md   <<< ledger appends since my last commit — commit with the next note >>>
 M infrastructure/state/queue/FOUNDRY.md   <<< ledger appends since my last commit — commit with the next note >>>
 M src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
?? Transient/CANONICAL_ASHKARR_2026-09-09.rws.bak-pre-landmark-rename-2026-09-10   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/ModsConfig.pre_enable_2mods_2026-09-18.xml   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/Player.log.deeps_quicktest_loadA_2026-09-18   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/Player.log.gridload_worldgen_crash_2026-09-17   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/Player.log.pre_caverns_window_2026-09-18   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/Player.log.pre_fullload_2026-09-17   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/Player.log.pre_gridload_2026-09-17   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/Player.log.pre_restart_enable_injections_2026-09-18   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/Player.log.pre_rotwave_20260918   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/Player.log.rotwave_session_2026-09-17   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_biome_names.txt   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_bridge_token.txt   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/_col_test.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_deeps_a.py   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/_deeps_b.py   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/_deeps_c.py   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/_deeps_d.py   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/_deeps_e.py   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/_deeps_f.py   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/_deeps_g.py   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/_deeps_h.py   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/_deeps_loadA_screen.bmp   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/_deeps_loadA_screen.png   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/_deeps_parity.png   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/_destroy_dialog.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_destroy_dialog.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_dialog_check.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_dialog_check.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_dialog_check2.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_dialog_check2.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_fh_cellrect.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_fh_close2.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_fh_close3.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_fh_deliverable.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_fh_deliverable2.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_fh_final.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_fh_full.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_fh_lit.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_fh_lit2.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_fh_sand.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_fh_v1.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_fh_wide.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_focus_check.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_focus_check.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_focus_now.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_focus_now.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_gridload_state.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_gridload_state.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_gridload_state2.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_gridload_state2.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_lanterndeeps_atlas_work/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_logread.py   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/_pits_demo.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_pits_demo.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_pits_demo2.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_pits_demo2.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_pits_sprung.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_pyre_v2.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_pyre_v3.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_pyre_v4.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_pyre_wake_state.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_pyre_wake_state.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_rot/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_tools_451.txt   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/_tools_now.txt   <<< MINE — throwaway quicktest scripts/logs; bin freely >>>
?? Transient/apparel_gate/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/art_gen/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/art_review_generic_marks/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/biomes_caverns_deepscan_2026-09-18.md   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/c4_trade/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/check1.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/check2.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/decay_batch_A_2026-09-18.md   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/decay_batch_B_2026-09-18.md   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/decay_batch_C_2026-09-18.md   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T141934Z.bak   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T142307Z.bak   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T142518Z.bak   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T143755Z.bak   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T150644Z.bak   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T161224Z.bak   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T163101Z.bak   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T165007Z.bak   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T165327Z.bak   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T165526Z.bak   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T165614Z.bak   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T170108Z.bak   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T173327Z.bak   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/events.jsonl.pre-repair-20260918T173627Z.bak   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/flap_check.py   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/flapchk_A.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/flapchk_ABC.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/flapchk_B.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/flapchk_C.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/flapzoom_A.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/flapzoom_B.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/flapzoom_C.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/foundry_state_check.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/git_efficiency_audit_2026-09-13.md   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/graffiti_variants/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/harvest_crossref_2026-09-18_1035.txt   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/harvest_discarded_2026-09-18_1035.txt   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/harvest_patchfail_2026-09-18_1035.txt   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/harvest_rotwave_session_2026-09-17.txt   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/harvest_scribe_2026-09-18_1035.txt   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/hawk1_A.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/hawk1_AB.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/hawk1_B.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/hawk2_A.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/hawk2_AB.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/hawk2_B.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/hawk_center_A.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/hawk_center_B.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/hawk_close_A.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/hawk_close_B.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/load_stall2_2026-09-11.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/load_stall_2026-09-11.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/loadercaps/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/mapgen_gl/apparelmoney2/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/mapgen_gl3/shots/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/meshfuse_multiview/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/mlie_pass9_extract/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/mlie_waveb_extract/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/modcheck/Pits_20260913T203104Z.html   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/modcheck/Pits_20260913T203625Z.html   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/modcheck/Pits_20260913T203959Z.html   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/modcheck/Pits_20260913T204215Z.html   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/mw2_disentanglement_review_2026-09-13.md   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_anim_wide.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_anim_wide_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_animals_grass.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_animals_grass_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_animals_over.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_animals_over_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_artgrid.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_artgrid_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_ashfall_live.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_ashfall_live_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_choked_grass.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_choked_grass_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_choked_v2.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_choked_v2_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_daylight_grid.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_daylight_grid_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_defread.py   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_density155_A.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_density155_A_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_density155_center.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_density155_center_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_faced.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_faced_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_fix2.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_fix_overview.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_flapA.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_flapA2.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_flapB.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_flapB2.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143618.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143618_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143619.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143619_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143620.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143620_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143621.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_grid_143621_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_hawk_rectA__cell_rect.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_hawk_rectB__cell_rect.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_live1_ashfall_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_live1_clear_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_mech_check.py   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_stage_test.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyre_stage_test_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150446.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150446_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150448.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150448_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150449.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150449_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150450.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyrefinal_150450_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyregrid2_145955.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyregrid2_145957.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyregrid2_145958.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyregrid2_145958_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyregrid2_145959.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyrelands_live_first_look.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyrelands_live_first_look_sm.png   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/pyrelands_quicktest_2026-09-13/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/research_trio_briefing_2026-09-18.md   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/rimworld_state_check.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/rot_fauna_assignment_draft_20260918.md   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/sea_raw/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/system_screenshot_2026-09-09.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/triposr_prototype/   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/verify1.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/verify2.bmp   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/world_neighbors_2026-09-18.csv   <<< unknown — `git log -1 -- <path>` >>>
?? Transient/worldmap_docs_pass_agenda_2026-09-18.md   <<< unknown — `git log -1 -- <path>` >>>
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   <<< stray from an earlier session — not mine >>>
?? defs.sqlite   <<< stray from an earlier session — not mine >>>
?? deployed/config/ModsConfig.before-tier-oracle.xml   <<< stray from an earlier session — not mine >>>
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   <<< stray from an earlier session — not mine >>>
?? deployed/config/ModsConfig.before-tier-warlab.xml   <<< stray from an earlier session — not mine >>>
?? infrastructure/artpipe/active/rut_agelesscap_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_brewingvessel_v1_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_euphoriccrown_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_falsefruit_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_furnacecap_plant_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_gene_furnaceblood_icon_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_grownfurnace_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_liveingredient_agelesscap_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_liveingredient_euphoriccrown_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_liveingredient_regenerantveil_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_liveprep_toxicinjection_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_livingfurnacecap_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_palemoss_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_paletree_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_regenerantveil_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_symbiont_mycoid_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_symbiont_nightwake_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_symbiont_quickflesh_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_symbiont_sheenblood_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_tea_agereversal_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_tea_bioregeneration_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/active/rut_tea_pleasure_v1.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/daemon_run_20260916_bench_restart.log   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kinrath_v1_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kinrath_v1_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kinrath_v1_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kreetle_v1_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kreetle_v1_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kreetle_v1_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/twistingthornweed_v1_r2.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/codexcal_mantrap_r4.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/nysyllin_v1_r2.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   <<< artpipe daemon (owner's tool) — other waves' jobs; not mine >>>
?? infrastructure/state/.rimflow_conc_97j8px_9/   <<< stray from an earlier session — not mine >>>
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   <<< stray from an earlier session — not mine >>>
?? infrastructure/state/items/BENCH_REBOOT_HANDOFF_202609182143.md   <<< unknown — `git log -1 -- <path>` >>>
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Runyip.xml   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Scavrat.xml   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Scurrier.xml   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
?? src/RimStarWars/SWBestiary/Textures/swanimals/Runyip/   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
?? src/RimStarWars/SWBestiary/Textures/swanimals/Scavrat/   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
?? src/RimStarWars/SWBestiary/Textures/swanimals/Scurrier/   <<< the OTHER window — MLIE_FAUNA_ABSORPTION_1 Pass 21, mid-flight, LEAVE >>>
```
