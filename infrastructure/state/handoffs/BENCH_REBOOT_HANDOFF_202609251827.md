# BENCH_REBOOT_HANDOFF_202609251827 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609251430`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**The shared working tree is not safe for uncommitted work while a peer runs a branch-merge wave.** At 07:54:58 and ~07:57 a peer's merge flow reset every dirty tracked file to HEAD with no stash — it ate the def half of the Scald wiring (4ea2a93f3 shipped PNGs only), three ledger events, the TheRot move's staged deletions and two rebuilt DLLs. This window then did everything from a private worktree (`git worktree add` under the scratchpad, edit + `rimflow` there, `git push origin HEAD:main`) and lost nothing after. If a merge wave is running, do the same. (filed: LESSONS_INBOX)

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **SCALD_REVIEW is loaded in the running game** (map 8, strip at cells 100-144 x 8-38; save `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\SCALD_REVIEW.rws`) — his walk-through verdicts drive the Scald pass. Open review points: cast reads tiny (drawSize 0.25-0.45), wreck shadows are big dark boxes, margin looks identical to shallows.
- **Two crash-class fixes shipped live:** the Scald steam and Greentide roil weather overlays blacked the whole map (MatLoader.LoadMat can't load mod assets; 70607e667, deployed, proven by loading SCALD_REVIEW with steam locked). 77 catch fish drew red-X (file texPath under StackCount; 860b9e0f9 + ad0d0e756, deployed).
- **Rainbow pigment has no use** — his call whether it becomes dye or an art/statue ingredient (asked, unanswered).
- **Styling-station hat preview** will still show the Jawa hood after JAWA_SWIM_HOOD_KEEP_1 — deliberate per his "never", but he may want the preview exempt.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `SCALD_FLOOR_PASS_1` -- doing; showcase staged + saved, steam overlay fixed, art wave 2 queued; NEXT: when the 42 `scald2_*` artpipe jobs render, wire them (StackCount folders `<item>/<item>_a/_b/_c`, wreck `_A/_B/_C` variants, condenser), deploy TerminalBiomes at a game-down, then the owner's SCALD_REVIEW walk verdicts.
- `JAWA_SWIM_HOOD_KEEP_1` -- built (71e013a4f + 580a39c7a), NOT deployed; NEXT: at game-down run `deploy_custom_mods.py --mod JawaRules --apply` and `--mod StarWarsRaces --apply`, restart, look at a swimming and a sleeping Jawa with the owner.
- `SCALD_ART_UPGRADE_WAVE_1` -- 42 jobs pending in `infrastructure/artpipe/pending/scald2_*.json` at 512/1024 canvas; NEXT: contact-sheet them for the owner once rendered, then wire (under SCALD_FLOOR_PASS_1).
- `STATUE_ART_EXPANSION_1` -- scoped (two mods: Utinni statues then flame statues) and all spec questions ruled (design/RimMandrake/statue_mods_spec.md + ledger notes: player must choose the god, 13 subjects, chemfuel, Sh'kaar first); NEXT: revise the spec's rulings section for the player-choice ruling, then queue the 13 subjects' art.
- `SCALD_STEAM_WEATHER_DESIGN_1` -- spec done + ruled (design/RimMandrake/scald_steam_and_hazards_spec.md; ledger notes hold the rulings incl. boil-suit via Industrial research, advanced vacsuits protect, the Royal Rind from the greatbole fruit — no def exists yet, lake-burn toggle allowed); NEXT: fold the rulings into the spec, then build native immunity first (XML-only).
- `SEA_DIVE_MAPS_BUILD_1` -- spec done + ruled (design/RimMandrake/sea_dive_maps_spec.md, ead9bdc84); NEXT: step-2 quicktest proving a surface exit with no entrance building.
- `SEA_SHORE_TILE_MUTATOR_1` -- ruled by the owner, no spec yet; NEXT: brief a design pass (Fable) for the per-sea shore mutator incl. the two-seas pick rule.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A backgrounded artpipe daemon parks itself at a Codex 99% weekly meter and never notices a reset: one trivial `codex exec` per leased worker home writes a fresh reading (filed: LESSONS_INBOX, ARTPIPE_QUOTA_RESET_WEDGE_1).
- A staged review strip with no colonist in sight draws terrain but no things — Real Fog of War (filed: LESSONS_INBOX).
- MatLoader.LoadMat never loads a mod asset; in a static field it blacks the whole map (filed: LESSONS_INBOX).
- A Player.log watcher started right after launch matches the previous session's 'Bridge token:' (filed: LESSONS_INBOX).
- Pawns mid-swim-job on a PAUSED staged scene render head-only/vanish and look like a bug; let time run before judging (see: SHULLA_INVISIBLE_RENDER_1, closed).
- A mod's gene/def naming a workerClass from another of our assemblies discards the whole def when that mod is absent — put the reference in a patch inside the owning mod (see: 580a39c7a).
- `--owner-said` refuses quotes from mid-turn user messages; record those under the seat and name them in the text (see: SHULLA_INVISIBLE_RENDER_1 close).

## Closed since the last handoff (1)

- `SHULLA_INVISIBLE_RENDER_1` — paused-staging transient, closed in ledger 2a227f630 (the recorded close sha 109f54f6b is a peer commit — `close --sha HEAD` trap)

## Filed and still open (9) — the next seat's queue

- `SEA_DIVE_MAPS_BUILD_1` — Dive maps for the four seas: diving opens a small underwater map where the sea-floor cast (wildAnimals) actually spawns. Decision taken by question ca
- `WATERTRUCE_CTOR_BIOME_READ_1` — RM_MapComponent_WaterTruce reads map.Biome in its constructor (line ~51): on save load TileInfo is not resolved yet, WorldGrid index throws, and the c
- `REGROWTH_RECOLOR_MINEABLES_NRE_1` — Every full-list save load logs 'Exception from long event: NullReferenceException at ReGrowthCore.Map_FinalizeInit_Patch RecolorMineables' (09-24 and 
- `SEA_SHORE_TILE_MUTATOR_1` — Sea shores via a tile mutator: a land tile bordering a sea gets that sea's shore + water on its coast. Engine (MEASURED, RimSage): coast water comes f
- `SCALD_ART_UPGRADE_WAVE_1` — Scald art wave 2: high-res lush restyle of the Scald set, 2-3 stack variants per item; shulla catch as a small pile of fish; landspeeder wreck redone 
- `SCALD_STEAM_WEATHER_DESIGN_1` — Design: Scald steam weather beautiful + interesting + deadly without protective gear; the boiling water's danger and the player's protections; natives
- `SALVAGE_WRECKAGE_EVERYWHERE_1` — Salvage wreckage across the planet: wreck families (hulls, tanks, frames, speeders...) scattered in every biome, biome-appropriate weathering, deconst
- `STATUE_ART_EXPANSION_1` — Statue expansion: assess the statue-choice mod (patch vs own), RM statues with flame emergence points, Utinni god/culture statues, flame fuel via Sump
- `JAWA_SWIM_HOOD_KEEP_1` — URGENT (owner, chat 2026-09-25: Jawa must never be seen without a hood): swimming Jawa lose their hood because vanilla 1.6 swim rendering clears the H

## Commits

```
ebcecf44a Ledger: JAWA_SWIM_HOOD_KEEP_1 built, deploy owed
580a39c7a Jawa hood node: move from StarWarsRaces into a JawaRules patch
71e013a4f JAWA_HOOD_ALWAYS_VISIBLE_1: Jawa never render bare-headed, in any state
5275333b3 Ledger: close JAWA_MESS_IMMUNITY_1 (live quicktest + engine verification)
304e32407 Ledger: bridge take/release, no game changes (JAWA_MESS_IMMUNITY_1 live quicktest deferred -- real campaign colony loaded, not a disposable quicktest map)
9b4b9af98 Ledger: close GREATBOLE_BARK_EDGE_ART_1, STACKCOUNT_FILEPATH_REDX_SWEEP_1
b8d6f227c Ledger: close ARTPIPE_QUOTA_RESET_WEDGE_1, note REACTION_MECHANISM_GENERALISE_1 step-2 progress
6d0dbf802 GREATBOLE_BARK_EDGE_ART_1: bark-edge atlas art + linked-tile def wiring + regrowth-rate tunable
c1e246b6f STACKCOUNT_FILEPATH_REDX_SWEEP_1: fix 28 collection-init red-X defs, census the rest
0131ec0ad Ledger: bridge release (BENCH wrap)
c99c25955 Rebuild RimMandrake.CreatureBehaviors.dll: verify REACTION_MECHANISM_GENERALISE_1 step 2 compiles
2a227f630 Ledger: close SHULLA_INVISIBLE_RENDER_1 (paused-staging transient), file JAWA_SWIM_HOOD_KEEP_1
109f54f6b REACTION_MECHANISM_GENERALISE_1 step 2: same-kind propagation under a minimal hostile mobile plant
fa8e676bd chore: regenerated codebase health artifacts (auto, blocking a rebase)
d5d3c8e5b artpiped: weekly quota wedge self-heals via reported reset time (ARTPIPE_QUOTA_RESET_WEDGE_1)
7ced2ec27 Wave 6: mark CLEAN the REACTION_MECHANISM_GENERALISE_1 step-1 cluster (7 files)
e137acf2b Ledger: SHULLA_INVISIBLE_RENDER_1 is not pinned; correct the over-claiming note
7374f9f82 Merge remote-tracking branch 'origin/main'
e580b93d9 Ledger note: SHULLA_INVISIBLE_RENDER_1 re-scoped root cause found
042d41c8f Ledger: statue spec rulings (choice required, 13 subjects, chemfuel, Sh'kaar first)
... 48 more: git log --oneline 5004daa92..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-25T18:24:00Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   health publisher's auto-rebuild — FOUNDRY loop's
 M Transient/codebase_health.json   health publisher's auto-rebuild — FOUNDRY loop's
 M Transient/codebase_health_artifact.html   health publisher's auto-rebuild — FOUNDRY loop's
 M infrastructure/dashboards/hub/data/health.json   health publisher's auto-rebuild — FOUNDRY loop's
 M infrastructure/state/codebase_health_last.json   health publisher's auto-rebuild — FOUNDRY loop's
 M infrastructure/state/queue/BENCH.md   rimflow projection — commits with the next ledger sync
 M infrastructure/state/queue/FOUNDRY.md   rimflow projection — commits with the next ledger sync
?? deployed/config/ModsConfig.before-tier-firehawk.xml   FOUNDRY/owner tier backups — leave alone
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   FOUNDRY/owner tier backups — leave alone
?? infrastructure/artpipe/done/bluedesert_dovvik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_ossagrel.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_ossagrel.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brakkel_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brakkel_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brunnock_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brunnock_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_cundral_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_cundral_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_gorbeleth_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_gorbeleth_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_kaddrath_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_kaddrath_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_maddrick_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_maddrick_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mirrelbole_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mirrelbole_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mourvel_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mourvel_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_wildhealroot.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_wildhealroot.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutbloomcrop_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutbloomcrop_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdarkcrust_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdarkcrust_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdeltaloam_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdeltaloam_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutfuzz_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutfuzz_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutglower_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutglower_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutglowercrust_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutglowercrust_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseed_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseed_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutvaultroot_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutvaultroot_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutwelcomeblanket_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutwelcomeblanket_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_bladderboilcatch_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_bladderboilcatch_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_saalcatch_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_saalcatch_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shullacatch_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shullacatch_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_steamcatchbuilding_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_steamcatchbuilding_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_ventbuilding_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_ventbuilding_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_wreckframe_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_wreckframe_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_wreckhull_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_wreckhull_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_wrecktank_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_wrecktank_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_pellorax_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_pellorax_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_zhool_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_zhool_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/crags_kessik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/crags_kessik_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_kessik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_kessik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_shekkur_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_shekkur_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_shekkur_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_thrizzik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_thrizzik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_thrizzik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ulkhorr_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ulkhorr_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ulkhorr_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_vrakk_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_vrakk_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_vrakk_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zekkra_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zekkra_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zekkra_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zhurrakor_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zhurrakor_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zhurrakor_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_essarn_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_essarn_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_essarn_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_fessk_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_fessk_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_fessk_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_otheska_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_otheska_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_otheska_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_sorruth_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_sorruth_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_sorruth_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_mahllik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_mahllik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_mahllik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_zhissa_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_zhissa_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_zhissa_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_heemin_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_heemin_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_heemin_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_body_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_body_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_body_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_carapacewall_atlas.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_carapacewall_menuicon.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald2_bladderboilcatch_a.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_bladderboilcatch_b.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_bladderboilcatch_c.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_dosscatch_a.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_dosscatch_b.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_dosscatch_c.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_eeshcatch_a.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_eeshcatch_b.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_eeshcatch_c.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_ekkelcatch_a.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_ekkelcatch_b.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_ekkelcatch_c.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_karrashcatch_a.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_karrashcatch_b.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_karrashcatch_c.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_muddalcatch_a.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_muddalcatch_b.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_muddalcatch_c.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_rainbowpigment_a.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_rainbowpigment_b.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_rainbowpigment_c.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_saalcatch_a.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_saalcatch_b.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_saalcatch_c.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_shullacatch_a.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_shullacatch_b.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_shullacatch_c.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_steamcatchbuilding_a.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_thuumcatch_a.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_thuumcatch_b.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_thuumcatch_c.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_ventbuilding_a.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_ventbuilding_b.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_wreckframe_a.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_wreckframe_b.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_wreckframe_c.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_wreckhull_a.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_wreckhull_b.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_wreckhull_c.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_wrecktank_a.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_wrecktank_b.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/scald2_wrecktank_c.json   mine — SCALD_ART_UPGRADE_WAVE_1 jobs; pending/ stays uncommitted by convention
?? infrastructure/artpipe/pending/slime_bezzul_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_bezzul_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_bezzul_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_greateroomb_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_greateroomb_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_greateroomb_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_hennul_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_hennul_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_hennul_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_mubbaro_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_mubbaro_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_mubbaro_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_oomb_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_oomb_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_oomb_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_thummorak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_thummorak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_thummorak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_vohhm_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_vohhm_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_vohhm_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuppik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuppik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuppik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuum_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuum_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuum_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_yollum_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_yollum_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_yollum_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   FOUNDRY/owner tier backups — leave alone
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   FOUNDRY/owner tier backups — leave alone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   FOUNDRY/owner tier backups — leave alone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   FOUNDRY/owner tier backups — leave alone
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   FOUNDRY/owner tier backups — leave alone
?? src/RimMandrake/Utils/firehawk_flight_probe.py   not mine — investigate before touching
```

