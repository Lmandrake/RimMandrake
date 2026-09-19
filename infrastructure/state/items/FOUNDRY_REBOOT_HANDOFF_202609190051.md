# FOUNDRY_REBOOT_HANDOFF_202609190051 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609181937`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
`RimWorld.QuestGen.QuestNode_SendSignals` has no settable `<inSignal>` XML field — it
parses clean and is silently discarded, and the node fires on whatever the AMBIENT
slate signal happens to be, not the one the author wrote. Any signal-forwarding quest
node in this repo needs `QuestNode_SignalActivable` wrapping instead (the LEAVE branch
already does this correctly; WAKE/LOOT didn't, and it cost a full live-fire pass to
find). Filed to LESSONS_INBOX.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **A real, permanent change landed on the actual campaign save** (Autosave-4, not a
  scratch test): two research projects, `RUT_Antiq_Cartography` and `RUT_Antiq_Voice`,
  were force-finished via `jawa/research_finish_project` to test whether the vault-thaw
  quests could fire. This was deliberate and logged, not an accident — but it is a real
  advance of your game state that you did not ask for, done to prove a bug existed.
- Desert-wrap apparel art generation hit a hard Codex imagegen quota wall after 4 of 60
  jobs (resets ~3.5h from 2026-09-18 14:18) — you ruled "wait for reset" over switching
  to Gemini mid-matrix to avoid a style seam. Nobody has resumed it since; only Spiral's
  Male (3 directions) + Female south/north exist so far.
- Ruled this session and now built: NINEFOLD_ENGINE_M0_1 closes on the 9 first-contact
  letters alone (your call); the bigger narrator-corpus voice-bible in
  `design/Jawa/narrator_corpus/` (~1,500 lines, judgement/council + 3 triad rite-voice
  files) is real, unbuilt, and has no item filed for it yet.
- Also ruled: Fever Wood's mirror pools are 3-6 small (2x2-4x4), scattered, minimum
  spacing, never a landmark pool — built and live-verified (18 pool-terrain runs on a
  generated map). No further ruling owed there.
- `TECHPRINT_FACTION_GATING_1` stays BLOCKED on a real design gap only you can close:
  which factions hold which research domains. No such mapping exists in any design doc;
  the item's own investigation is exhaustive.
- A brand-new dungeon item spun out of tonight's work: `ASHFALL_RESEARCH_BASE_1` (the
  Spire, holding the Rakatan command codes that unlock the war lab's two-key gate) — a
  full design doc already existed unfiled; first build increment is in, not yet
  deployed or quicktested.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `MLIE_FAUNA_ABSORPTION_1` — still RUNNING in the background as of this handoff (agent
  `a6c76b1ebb1199a50`, Pass 21+, front species Runyip/Scavrat/Scurrier uncommitted right
  now, ~23 of 89 species remaining); NEXT: check whether that background agent survived
  the reboot — if not, resume porting from wherever `cast_assignment.csv`/`git log`
  shows it stopped.
- `ASHFALL_RESEARCH_BASE_1` — first build increment landed (61x61 KCSG layout, defs,
  C# quest-flag mechanism linking to the war lab gate), compiles clean, not deployed or
  quicktested; NEXT: `kcsg_place` it live and confirm the offline BFS reachability
  proof holds in a real generated map.
- `VAULT_THAW_QUEST_FAMILY_1` — 3 real defects found and fixed (V1's ocean site tile
  re-sited, V6's broken signal wiring fixed, the dual-fire-route ConfigError fixed on
  all 6 vault quests), deployed, validators clean; NEXT: bridge-fire
  `RUT_GiveQuest_VaultThaw_V1_RustCathedral` and `_V6_Umbra` on the real Ash'karr
  campaign save (not a scratch quicktest) and confirm a Site WorldObject actually
  appears both times.
- `COLONY_VISIBILITY_BUILD_1` — threat-point Prefix confirmed already-correct via a DLL
  checksum match, no re-fire needed; tile-memory round trip still unverified because it
  needs a fully-built, flyable gravship; NEXT: build one via the `gravship-layout`
  skill on a test save, then confirm tile-memory persists across a real departure/arrival.
- `DROIDWORKS_WIPE_SEVERITY_1` — per-step diagnostic logging added to
  `Recipe_DWMemoryWipe.ApplyOnPawn` so a failure will now name its exact step; retest
  still inconclusive because the quicktest harness's AI never naturally assigns the
  DoBill job even after ~43,000 ticks; NEXT: force-assign the bill directly via the
  bridge instead of waiting on natural AI pickup, then retest.
- `RIVER_STEAM_ANIMATION_1` — still BLOCKED, live-observe verify owed; the known
  blocker is `world_tile_map_generate` rendering a blank void for a fresh Pyrelands
  test map; NEXT: either load the real Ash'karr Pyrelands region (not a generated
  scratch map) or fix the render-void trap first.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — self-continuing, 15 waves this session
  (~103 files reviewed, 6 real bugs fixed), backlog currently down to 15 DIRTY files
  and all of them locked to the in-progress SWBestiary fauna port; NEXT: re-run
  `code_review_status.py list` once that port lands and pick up wave 16.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `QuestNode_SendSignals`'s fake `<inSignal>` field and the incident/random dual-fire
  `ConfigError` (filed: LESSONS_INBOX).
- A generator's own "regen is a no-op" header claim can be false — verify with a real
  diff, not the exit code; this exact gap would have reverted a naming migration
  (filed: LESSONS_INBOX).
- `TileMutatorDef Oasis`'s biome whitelist silently blocks an auto-rolled companion
  mutator even on an already-whitelisted biome; `Tile.AddMutator` bypasses it. A spec's
  own tile-count header can also be stale (236 claimed vs 223 measured) (filed:
  LESSONS_INBOX).
- `git commit <path>` on a shared file commits the WORKTREE content at that path, not a
  staged subset — a peer's uncommitted lines on the same shared file ride into your
  commit under your message. Hit LIVE again this session (Mlie fauna's Pass 21 CSV
  rows swept by a BENCH commit; nothing lost, just misattributed) even though this is
  already recorded (see: memory `pathspec-commit-takes-worktree-not-index`).

## Closed since the last handoff (2)

- `OASIS_LANDMARK_PLACEMENT_1` — 43172ff44
- `CHRONICLE_NINEFOLD_DECOUPLE_1` — 4e41e0f742e9b490a091e87ca0c74912b78644b1

## Filed and still open (7) — the next seat's queue

- `DEEPCALM_AMBIENT_SOUND_1` — Lantern Deeps ambient sound: RUT_DeepCalm ships silent - author/source an owned cave-hum SoundDef (the sheet's 'hum rising to a Chorus'), donor .ogg d
- `POLLUTED_LANDS_FLORA_PORT_1` — Polluted Lands cut step 2: port-or-cut its ~40 injected plants (21 BMT_ rows still live in BiomeFlora_Ashkarr with no RUT twin) + inert-check the 52 W
- `BIOME_FLORA_GENERATOR_REPAIR_1` — biome_flora.py cannot regenerate BiomeFlora_Ashkarr.xml: FAMILIES still keys on pre-rename biome defNames (AB_MycoticJungle, ZBiome_Badlands, Wastelan
- `ASHFALL_RESEARCH_BASE_1` — The Ashfall Research Base (the Spire): Rakatan command codes, the war lab's two-key gate
- `DEEP_DULCIS_DEDUP_1` — LanternDeeps: drop RUT_DeepRawDulcis, harvest yields RotSporeKit's RUT_RawDulcis (owner ruled 2026-09-18: RotSporeKit owns it); add mandrake.rut.rotsp
- `CAVERNS_LOADAFTER_STRIP_1` — Biomes! Caverns left ModsConfig 2026-09-18 (Core stays until POLLUTED_LANDS_FLORA_PORT_1): strip the now-inert loadAfter BiomesTeam.BiomesCaverns line
- `CANONICAL_SAVE_CAVERNS_SCRUB_1` — CANONICAL_ASHKARR_START_2026-09-12.rws holds 5 pawns carrying BMT_CaveSpiderHead (Biomes! Caverns weapon, MEASURED 5 <def> + 13 peq refs) - Caverns le

## Commits

```
3c1295879 rimflow: sync ledger (COLONY_VISIBILITY_BUILD_1 live-verification note+block)
cdb33b6d2 rimflow: VAULT_THAW_QUEST_FAMILY_1 now needs bridge (deploy done)
2bbe189a5 rimflow: sync ledger (VAULT_THAW_QUEST_FAMILY_1 notes, bridge take/release)
6ab5526c2 Fix VAULT_THAW_FIXED_TILES_UNFIREABLE_1: re-site V1, fix V6 signal wiring, fix quest firing route
ad081e791 CODE_REVIEW_STATUS: mark DEPLOY_HOLD.txt + Pyrelands.xml CLEAN (wave 15)
d0639c8e6 CODE_REVIEW_STATUS: mark 10 RimUtinni files CLEAN (wave 14)
4e41e0f74 CODE_REVIEW_STATUS: mark biome_flora.py CLEAN (wave 13)
2247c176e CODE_REVIEW_STATUS: mark FlowWorks LiquidTypes cluster's 20 dirty files CLEAN (wave 12)
336688eb2 rimflow note: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 11
77fd0cb6b CODE_REVIEW_STATUS: mark StructureInjectionsRUT/WarLab's 3 dirty files CLEAN (wave 11)
6e9893f19 CODE_REVIEW_STATUS: mark LanternDeeps' 3 dirty files CLEAN (wave 11)
177be573d LanternDeeps csproj: fix stale "no Harmony" comment
4360e99c3 CODE_REVIEW_STATUS: mark EnvironmentalHazards kit's 6 dirty files CLEAN (wave 11)
aeb8d6f40 rimflow note: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 10
eafb18413 CODE_REVIEW_STATUS: mark 6 more files CLEAN (wave 10)
dd0d313eb rimflow note: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 9
1a14d9fb8 CODE_REVIEW_STATUS: mark 6 more files CLEAN (wave 9)
38a129f28 rimflow note: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 8
bb924f14d CODE_REVIEW_STATUS: mark 6 more files CLEAN (wave 8)
48b321e95 rimflow note: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 7
... 75 more: git log --oneline a5f0d97ed..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-19T00:49:59Z

Uncommitted (replace each UNVERIFIED - not mine, not traced further with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   auto-triggered health-publisher daemon, not mine
 M Transient/codebase_health.json   auto-triggered health-publisher daemon, not mine
 M Transient/codebase_health_artifact.html   auto-triggered health-publisher daemon, not mine
D  infrastructure/artpipe/pending/crystalcap_b_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/crystaltipbrambles_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/crystaltipbrambles_b_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/dulciscropitem_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/dulcisgrown_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/dulcisharvested_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/dulcisimmature_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/fungusfern_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/fungusfern_b_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/fungusfern_c_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/fungusfern_d_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/gleamtip_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/gleamtip_b_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/greyladygrown_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/greyladygrown_b_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/greyladygrown_c_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/greyladyimmature_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonechunk_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonechunk_b_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonechunk_c_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonechunk_d_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonehuge_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonehuge_b_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstoneitem_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstoneitem_b_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstoneitem_c_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonelarge_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonelarge_b_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonemedium_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonemedium_b_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonemedium_c_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonesmall_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonesmall_b_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonesmall_c_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonesowableimmature_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstoneterrain_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/lanternstonewallicon_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/luminousspout_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/luminousspout_b_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/mycelium_a_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/mycelium_b_v1.json   artpipe daemon consuming its own queue, not mine
D  infrastructure/artpipe/pending/mycelium_c_v1.json   artpipe daemon consuming its own queue, not mine
 M infrastructure/artpipe/registry.jsonl   artpipe daemon bookkeeping, not mine
 M infrastructure/artpipe/throughput.jsonl   artpipe daemon bookkeeping, not mine
 M infrastructure/dashboards/hub/data/health.json   health-publisher daemon, not mine
 M infrastructure/state/MODE   MINE - set belt this session per owner instruction
 M infrastructure/state/codebase_health_last.json   health-publisher daemon, not mine
 M infrastructure/state/facts/mlie_wave_c_worklist.json   Mlie fauna agent's own tracking file, still running
 M infrastructure/state/ledger/events.jsonl   shared ledger, mixed mine + BENCH + subagents - do not blind-commit, diff first
 M infrastructure/state/queue/BENCH.md   shared ledger, mixed mine + BENCH + subagents - do not blind-commit, diff first
 M infrastructure/state/queue/FOUNDRY.md   shared ledger, mixed mine + BENCH + subagents - do not blind-commit, diff first
 M src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml   Mlie fauna agent, actively mid-edit right now
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   stray tool-call artifact, not mine, safe to ignore
?? defs.sqlite   UNVERIFIED - not mine, not traced further
?? deployed/config/ModsConfig.before-tier-oracle.xml   BENCH's pre-deploy ModsConfig backups (tier-oracle/stagedlore/warlab), not mine
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   BENCH's pre-deploy ModsConfig backups (tier-oracle/stagedlore/warlab), not mine
?? deployed/config/ModsConfig.before-tier-warlab.xml   BENCH's pre-deploy ModsConfig backups (tier-oracle/stagedlore/warlab), not mine
?? infrastructure/artpipe/active/rut_agelesscap_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_brewingvessel_v1_south.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_euphoriccrown_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_falsefruit_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_furnacecap_plant_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_gene_furnaceblood_icon_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_grownfurnace_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_liveingredient_agelesscap_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_liveingredient_euphoriccrown_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_liveingredient_regenerantveil_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_liveprep_toxicinjection_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_livingfurnacecap_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_palemoss_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_paletree_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_regenerantveil_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_symbiont_mycoid_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_symbiont_nightwake_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_symbiont_quickflesh_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_symbiont_sheenblood_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_tea_agereversal_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_tea_bioregeneration_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/active/rut_tea_pleasure_v1.json   artpipe daemon in-progress job, not mine
?? infrastructure/artpipe/daemon_run_20260916_bench_restart.log   pre-existing daemon log from 09-16, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_east.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_north.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_south.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_east.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_north.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_south.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/twistingthornweed_v1_r2.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/failed/codexcal_mantrap_r4.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/failed/nysyllin_v1_r2.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   artpipe daemon completed/failed job output, not mine
?? infrastructure/state/.rimflow_conc_97j8px_9/   rimflow concurrency scratch dir, not mine
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing since 2026-09-11, not mine
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Runyip.xml   Mlie fauna agent, actively mid-edit right now
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Scavrat.xml   Mlie fauna agent, actively mid-edit right now
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Scurrier.xml   Mlie fauna agent, actively mid-edit right now
?? src/RimStarWars/SWBestiary/Textures/swanimals/Runyip/   Mlie fauna agent, actively mid-edit right now
?? src/RimStarWars/SWBestiary/Textures/swanimals/Scavrat/   Mlie fauna agent, actively mid-edit right now
?? src/RimStarWars/SWBestiary/Textures/swanimals/Scurrier/   Mlie fauna agent, actively mid-edit right now
```

