# FOUNDRY_REBOOT_HANDOFF_202609281913 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609280425`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

BIOME_MOD_UNIFICATION_1 is EXECUTED — all 29 biome/kit mods now live inside one
player-facing `mandrake.rm.biomes` ("RimMandrake: Baroque Biomes") mod, live list
631 -> 614 (one ADD then a single 17-packageId swap), 3 clean cold loads. Read
`design/RimMandrake/biome_mod_unification_spec.md`'s "EXECUTED" section before
touching anything biome-related — it names what's fixed, what's deliberately left
alone (2 pre-existing "Phase B" defName collisions), and what's still genuinely
owed (a functional toggle-off test, tracked nowhere yet — file it if it matters).
Any doc/tool that still names a folded packageId standalone
(`mandrake.rm.<biome>` on its own, or `deploy_custom_mods.py --mod <FoldedBiome>`)
is stale prose, not an instruction — that command now REFUSES for all 29.

## What the owner should see

- **The Baroque Biomes merge is live on his actual mod list**, deliberately, this
  session (he confirmed the game was idle before each of 3 restarts). 631 -> 614
  mods; nothing removed except the 17 packageIds whose content now ships inside
  `mandrake.rm.biomes` instead.
- **He asked mid-session for a "Pit" biome renamed to "The Stenchlands."** No
  biome is currently named/defName'd "Pit" (measured, grepped every label) —
  filed as `PIT_RENAME_STENCHLANDS_1` for FOUNDRY, needs him to confirm which
  biome he means before it executes.
- **One design call he already made, via question card:** kept the Miasma-mod
  version of a duplicated hediff (`RUT_StrandedDeformation`) over the campaign
  patch layer's older version. Recorded on `STRANDED_DEFORMATION_DEFNAME_CLASH_1`.
- Nothing else here needs his eye — the rest is mechanical (dead-code retirement,
  stale packageId retargeting) or already-ruled work being executed.

## What is half-done, and where it stops

- `PIT_RENAME_STENCHLANDS_1` -- proposed, unclaimed; NEXT: ask the owner which
  biome he means by "The Pit" (no def currently matches), then rename
  label+defName per the Cauldron/Black Crags precedent (live-tile check first).
- `BAROQUE_BIOMES_TOGGLE_LIVE_VERIFY_1` -- proposed, unclaimed; NEXT: flip one
  biome's Mod Settings toggle off, generate a new world, confirm its BiomeDef
  places zero tiles, flip back on. The startup wiring is proven; an actual
  off-and-regenerate cycle is not.
- `BLUEDESERT_MOD_DEPENDENCY_DECISION_1`'s causal descendants
  (`BLUEDESERT_RULED_CONTENT_1`, `BLUEDESERT_MECHANICS_BUILD_1`,
  `WASTELAND_RULED_CONTENT_1`, `WASTELAND_MECHANICS_BUILD_1`,
  `CONTAGION_RULED_CONTENT_1`, `CONTAGION_MECHANICS_BUILD_1`) are untouched by
  this wave -- content/mechanics build work, unrelated to the unification,
  filed and ready; NEXT: pick one and build per its own spec.

## Traps learned

- A collision sweep scoped to "the set being changed" misses the real collision
  class — must walk every mod root that could reference it, not just the
  candidate set (filed: LESSONS_INBOX).
- A committed fix is not a deployed one — re-run `deploy_custom_mods.py --mod
  <X>` for every mod touched, even ones outside the compose target, before
  trusting a cold-load's "clean" as evidence for that fix (filed: LESSONS_INBOX).
- `Verse.Mod.GetSettings<T>()` tracks only ONE settings type per `Mod` instance
  — a second call for a different `T` logs an error and returns null, no
  exception; three `GetSettings<>()` calls on one constructor silently broke
  two of three settings sections (filed: LESSONS_INBOX).
- `git commit <new-untracked-path>` fails ("did not match any file(s)") unless
  `git add`ed first — plain `git commit <path>` only works for already-tracked
  paths (filed: LESSONS_INBOX).
- `.git/index.lock` contention from a peer window is transient — wait a few
  seconds and retry, never remove it blind (see: LESSONS_INBOX, same pattern
  recorded 2026-09-28 earlier in the day).

## Closed since the last handoff (27)

- `PYRELANDS_DEDICATED_GRAZER_1` — 56010ad03e673c64776e458659dd63b9d4f74dde
- `DEEP_SAND_WALKABLE_TERRAIN_1` — eb5a35214
- `BAROQUE_BIOMES_COMPOSE_1` — d72017bd5
- `TERMINALBIOMES_LIQUID_RETARGET_1` — 6d3dbb2e4
- `LONGSHADE_RULED_CONTENT_1` — 3bf918d54
- `STILLSAND_RULED_CONTENT_1` — 9c9ed72e2
- `SANDBUSTER_CASTES_BUILD_1` — 0c6e84064
- `DESERT_CAVERN_BEAST_EGGS_1` — dac89fd18
- `CHILL_RENAME_FULL_1` — a2184ac5c
- `CHILL_FIRE_BAN_1` — ca7a60c97
- `CHILL_THERMAL_ENGINE_1` — d23e31584
- `CHILL_HEATED_SUIT_1` — 5eaa306e4
- `CHILL_GARDEN_DEFENSE_1` — 0c11dd089
- `CHILL_FLORA_BUILD_1` — 3815690b5
- `CHILL_THERMAL_FOOTPRINTS_1` — 2684ac857
- `CHILL_RIME_TERRACES_1` — c2c1ace03
- `CHILL_WORLD_CRATER_1` — 4c2ecaca1
- `CHILL_VWAKE_WIRING_VERIFY_1` — 5c82fe04a
- `CHILL_FLOOR_LIGHT_1` — 917dadfac
- `CHILL_AURORA_SURGE_1` — d2ab077fa
- `STRANDED_DEFORMATION_DEFNAME_CLASH_1` — 504ff915e
- `RUSTCATHEDRAL_SETTINGS_DOUBLE_READ_BUG_1` — 75f39d310
- `BAROQUE_BIOMES_WAVE1_JOIN_1` — be2a6c77e24e0318b6f35efb2773bb5a44bd3871
- `BAROQUE_BIOMES_WAVE2_FOLD_1` — c3a1e3fd1ca0caaf0fc830be68791fae051521b3
- `BAROQUE_BIOMES_WAVE3_RETARGET_1` — d202a4f6b4dbd54c45cd82ab28ba33d2bff554fe
- `LANTERNDEEPS_TIER_COLLISION_1` — 59408ed0109b6526808146574b78910f5f02aa95
- `LONGSHADE_RM_MOD_BUILD_1` — 8d1104bdfb43068735266ce426fa366e49530732

## Filed and still open (10) — the next seat's queue

- `CONTAGION_RULED_CONTENT_1` — Build the Contagion grotesque cast: 35 RM_ defs replacing the donor roster outright (no patches), 8 new species, 4 real flyers, Wombpod wired to the b
- `CONTAGION_MECHANICS_BUILD_1` — Build the Contagion mechanics: Burn/Bloom weather + tells, the Coalescence (one growing organism), Cloud Repulsor + gravship hardpoint, Sunbeam + arre
- `WARLAB_CRATER_ACCIDENTAL_TRIGGER_1` — RUT_WarLabReactorCore's CompIgniteCraterOnDestroy fires the planet-wide Chill crater swap on ANY destruction of that core, not only deliberate Route-1
- `JAWA_MAP_INFO_BIOME_DIVERGE_DOCSTRING_WRONG_1` — jawa/map_info's tool description claims map and tile biome 'diverge after a live world_tile_set' -- false per vanilla source (Map.Biome reads the tile
- `WARCASKET_SUIT_CLASS_1` — Warcaskets as a cross-cutting suit class (ruled 2026-09-28): extreme-temp + vacuum + toxin rated, the alternative to space suits; very slow, bulky, co
- `PIT_RENAME_STENCHLANDS_1` — Rename The Pit biome to The Stenchlands (owner request, this session) - no biome is currently labeled/defName'd 'Pit' (measured: grepped every BiomeDe
- `WASTELAND_RULED_CONTENT_1` — Build the Wasteland survivor cast: full RM_ donor replacement - 8 fauna ports, 3 new processors, 6 flora, bezoar/soot items, brine label renames, texP
- `WASTELAND_MECHANICS_BUILD_1` — Build the Wasteland mechanics: 20-cell Middenshell on TitanicCreatures, processor gatherable comps, ambient-dose comp, three storm WeatherDefs + Movin
- `BLUEDESERT_RULED_CONTENT_1` — Build the Blue Desert ruled cast: depth cast (zhaaz/vrisk/dovvik/utikka) + bedazzle four (Vhaulk/Murrek/Ossivel/Virr) + RM_BlueIce + water-plant cut +
- `BLUEDESERT_MECHANICS_BUILD_1` — Build the Blue Desert mechanics: vhaulk trigger-gated detonation (EMP-on-hit trap), Warnings study ladder + cold-cutting, blue-ice thaw rolls, three w

## Commits

```
33408ba72 Record BIOME_MOD_UNIFICATION_1's execution in its own spec
440b20316 GREENTIDE_HUMMING_GROVE_1: deploy step done via the biome fold, needs -> owner
a4d0635b0 rimflow: close LONGSHADE_RM_MOD_BUILD_1 - step 5 proven by unification
8d1104bdf rimflow: close LANTERNDEEPS_TIER_COLLISION_1 - swap verified complete
37bb40e74 FLOODEDCANYON_BEDAZZLE_SITTING_1 movement 1: Cracked Lands nine-mark review
59408ed01 Note Q17 execution complete in the architecture doc
afbfa81e1 Retire test tiers that wanted now-folded biomes standalone
dff88d3e0 Fix 6 small RimUtinni mods' hard modDependencies on folded packageIds
25fa5c2db rimflow: note BIOME_MOD_UNIFICATION_1 with wave completion status
46564d867 rimflow: close BAROQUE_BIOMES_WAVE3_RETARGET_1, release bridge
d202a4f6b BAROQUE_BIOMES_WAVE3_RETARGET_1: consolidate loadAfter into mandrake.rm.biomes
9e555d7d7 BLUEDESERT_BEDAZZLE_SITTING_1 movement 4: cast bible + art commission
88a4339a9 rimflow: close BAROQUE_BIOMES_WAVE2_FOLD_1, release bridge
c3a1e3fd1 BAROQUE_BIOMES_WAVE2_FOLD_1: capture 614-mod list as new FULL.LATEST
163a374cf Blue Desert sitting ticketed out: sheet amendment + two FOUNDRY builds
fef76f0f6 BAROQUE_BIOMES_WAVE2_FOLD_1: snapshot ModsConfig before the swap
1bc4a589a Wave 2 prep: retarget compound MayRequire="a,b" values too
40a1a59dc Blue Desert volley turn 2 rulings recorded on review + ledger
dae6a3ab1 BAROQUE_BIOMES_WAVE2_FOLD_1 prep: retarget refs naming folded packageIds
f0b7f7447 Delete dead orphan TerminalBiomes/RUT_RareGreyCatches.xml
... 72 more: git log --oneline f8082f4b0..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-28T17:18:40Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M  Transient/codebase_health.html   ambient -- codebase_review_status.py's own health rebuild, re-triggered by any queue render
 M Transient/codebase_health.json   ambient -- codebase_review_status.py's own health rebuild, re-triggered by any queue render
 M Transient/codebase_health_artifact.html   ambient -- codebase_review_status.py's own health rebuild, re-triggered by any queue render
 M design/Jawa/worldbuilding/biomes/_def_bindings_2026-09-09.md   pre-existing -- dirty at session start, not touched this session (see initial git status)
 M design/Jawa/worldbuilding/biomes/rosters/the_propane_lakes.json   pre-existing -- dirty at session start, not touched this session (see initial git status)
 M design/Jawa/worldbuilding/biomes/terminal_seas_cast_proposal_2026-09-25.md   pre-existing -- dirty at session start, not touched this session (see initial git status)
 M design/RimMandrake/flowworks_liquid_matrix.md   pre-existing -- dirty at session start, not touched this session (see initial git status)
 M design/RimMandrake/sea_dive_maps_spec.md   pre-existing -- dirty at session start, not touched this session (see initial git status)
 M design/RimMandrake/sea_shore_mutator_spec.md   pre-existing -- dirty at session start, not touched this session (see initial git status)
 M design/RimUtinni/vanilla_beast_excision_census.md   pre-existing -- dirty at session start, not touched this session (see initial git status)
 M infrastructure/artpipe/daemon_run_20260927_derivefacings.log   ambient -- artpipe daemon output, continuously running, predates and outlives this session
 D infrastructure/artpipe/pending/RM_Oorrik_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
 D infrastructure/artpipe/pending/RM_Oorrik_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
 D infrastructure/artpipe/pending/RM_Oorrik_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
 D infrastructure/artpipe/pending/RM_Ruukka_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
 D infrastructure/artpipe/pending/RM_Ruukka_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
 D infrastructure/artpipe/pending/RM_Ruukka_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
 D infrastructure/artpipe/pending/RM_SandBusterMound_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
 M infrastructure/artpipe/registry.jsonl   ambient -- artpipe daemon output, continuously running, predates and outlives this session
 M infrastructure/artpipe/throughput.jsonl   ambient -- artpipe daemon output, continuously running, predates and outlives this session
 M infrastructure/dashboards/hub/data/health.json   ambient -- codebase_review_status.py's own health rebuild, re-triggered by any queue render
 M infrastructure/state/codebase_health_last.json   ambient -- codebase_review_status.py's own health rebuild, re-triggered by any queue render
 M infrastructure/state/ledger/events/BENCH.jsonl   BENCH's own shard -- not mine to touch
?? deployed/config/ModsConfig.before-tier-baroque_wave0.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-baroque_wave0_control.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-firehawk.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-leaningscrub.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_bluedesert.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_contagion.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_feverwood.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_floodedcanyon.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_forsakencrags.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_gelatinousslime.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_greentide.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_leaningscrub.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_longshade.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_miasma.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_nightsideice.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_poisonforest.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_pyrelands.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_rustcathedral.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_stillsand.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_terminalbiomes.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_theforge.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_therot.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_thesump.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_wasteland.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_webwork.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-proof_weepingstones.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   pre-existing -- an earlier session's modset_builder.py tier snapshots, not touched this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Bleedleaf.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Bleedleaf.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Blisterfloat_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Blisterfloat_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Blisterfloat_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Blisterfloat_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Blisterfloat_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Blisterfloat_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Bloodlurk_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Bloodlurk_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Bloodlurk_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Bloodlurk_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Bloodlurk_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Bloodlurk_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_BloodyFist.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_BloodyFist.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_BloodyMess_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_BloodyMess_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_BloodyMess_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_BloodyMess_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_BloodyMess_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_BloodyMess_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_BlueIce.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_BlueIce.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Boilbulb.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Boilbulb.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Boilhide_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Boilhide_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Boilhide_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Boilhide_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Boilhide_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Boilhide_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_BrinePlate.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_BrinePlate.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Cinderfelt.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Cinderfelt.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_CloudRepulsor.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_CloudRepulsor.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Crispling_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Crispling_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Crispling_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Crispling_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Crispling_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Crispling_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dakkra_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dakkra_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dakkra_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dakkra_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dakkra_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dakkra_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Danglemaw_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Danglemaw_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Danglemaw_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Danglemaw_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Danglemaw_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Danglemaw_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dewfringe.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dewfringe.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Doublemaw_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Doublemaw_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Doublemaw_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Doublemaw_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Doublemaw_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Doublemaw_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Drazz.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Drazz.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Duumma_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Duumma_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Duumma_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Duumma_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Duumma_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Duumma_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Eyebark.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Eyebark.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Eyestinger_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Eyestinger_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Eyestinger_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Eyestinger_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Eyestinger_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Eyestinger_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Fleshsop_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Fleshsop_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Fleshsop_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Fleshsop_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Fleshsop_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Fleshsop_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_b_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_b_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_b_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_b_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_b_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_b_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gawpsack_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gawpsack_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gawpsack_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gawpsack_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gawpsack_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gawpsack_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_b_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_b_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_b_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_b_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_b_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_b_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Glasscrust.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Glasscrust.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gnashling_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gnashling_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gnashling_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gnashling_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gnashling_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gnashling_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gorekite_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gorekite_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gorekite_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gorekite_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gorekite_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gorekite_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gorestalk.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gorestalk.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gravelgut_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gravelgut_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gravelgut_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gravelgut_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gravelgut_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gravelgut_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Grimewing_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Grimewing_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Grimewing_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Grimewing_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Grimewing_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Grimewing_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gristleswarm_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gristleswarm_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gristleswarm_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gristleswarm_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gristleswarm_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gristleswarm_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_HalfmadeTree.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_HalfmadeTree.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_HalfmadeTreeBlighted.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_HalfmadeTreeBlighted.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Hourbloom.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Hourbloom.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ikee_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ikee_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ikee_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ikee_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ikee_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ikee_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_KneelOllim.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_KneelOllim.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_KneelOllim_b.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_KneelOllim_b.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Lashgrass.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Lashgrass.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Liikka_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Liikka_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Liikka_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Liikka_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Liikka_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Liikka_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_b_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_b_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_b_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_b_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_b_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_b_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Meatvine.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Meatvine.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Meltgut_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Meltgut_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Meltgut_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Meltgut_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Meltgut_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Meltgut_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Middenbeetle_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Middenbeetle_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Middenbeetle_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Middenbeetle_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Middenbeetle_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Middenbeetle_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Middenshell_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Middenshell_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Middenshell_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Middenshell_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Middenshell_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Middenshell_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Murrek_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Murrek_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Murrek_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Murrek_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Murrek_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Murrek_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Oorrik_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Oorrik_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Oorrik_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Oorrik_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Oorrik_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Oorrik_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_b_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_b_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_b_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_b_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_b_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_b_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ossivel_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ossivel_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ossivel_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ossivel_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ossivel_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ossivel_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Peeper_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Peeper_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Peeper_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Peeper_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Peeper_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Peeper_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_b_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_b_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_b_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_b_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_b_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_b_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pusberry.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pusberry.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Qorrax_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Qorrax_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Qorrax_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Qorrax_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Qorrax_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Qorrax_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Rattlegrope.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Rattlegrope.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ruukka_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ruukka_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ruukka_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ruukka_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ruukka_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Ruukka_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_SandBusterMound_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_SandBusterMound_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sapblister.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sapblister.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scabspinner_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scabspinner_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scabspinner_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scabspinner_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scabspinner_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scabspinner_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scaldhide_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scaldhide_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scaldhide_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scaldhide_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scaldhide_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scaldhide_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scorchpod_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scorchpod_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scorchpod_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scorchpod_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scorchpod_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scorchpod_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scumgrass.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scumgrass.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scumrat_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scumrat_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scumrat_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scumrat_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scumrat_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Scumrat_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Shambles_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Shambles_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Shambles_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Shambles_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Shambles_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Shambles_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Skinflap_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Skinflap_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Skinflap_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Skinflap_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Skinflap_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Skinflap_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Slagmole_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Slagmole_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Slagmole_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Slagmole_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Slagmole_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Slagmole_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sloghog_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sloghog_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sloghog_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sloghog_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sloghog_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sloghog_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sloshbelly_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sloshbelly_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sloshbelly_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sloshbelly_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sloshbelly_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sloshbelly_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Smolderback_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Smolderback_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Smolderback_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Smolderback_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Smolderback_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Smolderback_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_b_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_b_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_b_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_b_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_b_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_b_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_b_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_b_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_b_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_b_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_b_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_b_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_SootGristleswarm_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_SootGristleswarm_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_SootGristleswarm_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_SootGristleswarm_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_SootGristleswarm_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_SootGristleswarm_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sootgrazer_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sootgrazer_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sootgrazer_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sootgrazer_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sootgrazer_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sootgrazer_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_SparkleechGrub_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_SparkleechGrub_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_SparkleechGrub_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_SparkleechGrub_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_SparkleechGrub_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_SparkleechGrub_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sparkleech_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sparkleech_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sparkleech_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sparkleech_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sparkleech_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sparkleech_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sunbeam.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sunbeam.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_TallScumgrass.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_TallScumgrass.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_b_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_b_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_b_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_b_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_b_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_b_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tekk.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tekk.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Toothmoss.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Toothmoss.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_UltracactusPad.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_UltracactusPad.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Veessa_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Veessa_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Veessa_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Veessa_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Veessa_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Veessa_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Vhaulk_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Vhaulk_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Vhaulk_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Vhaulk_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Vhaulk_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Vhaulk_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Virr.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Virr.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Wartshrub.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Wartshrub.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Wombpod.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Wombpod.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_eldspar.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_eldspar.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_fuselight.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_fuselight.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_ghostpane.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_ghostpane.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_keelgrass.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_keelgrass.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_pitchpearl.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_pitchpearl.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_skyharp.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_skyharp.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_slackwax.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_slackwax.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_stillbloom.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_stillbloom.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_stonewater.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_stonewater.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_tarspool.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_tarspool.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/coalescence_stage1.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/coalescence_stage1.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/coalescence_stage2.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/coalescence_stage2.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/coalescence_stage3.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/coalescence_stage3.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/rm_chillauroracollector_v1.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/rm_chillauroracollector_v1.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/rmshademite_v2_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/rmshademite_v2_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/rmshademite_v2_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/rmshademite_v2_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/rmshademite_v2_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/rmshademite_v2_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/failed/rmshademite_v1_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/failed/rmshademite_v1_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/failed/rmshademite_v1_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/failed/rmshademite_v1_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/failed/rmshademite_v1_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/failed/rmshademite_v1_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/dashboards/hub/tabs/maturity.html   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it
?? infrastructure/dashboards/hub/utinni_control_room_standalone.html   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it
?? infrastructure/state/logs/harvested/   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it
?? infrastructure/state/modlists/ModsConfig.FULL.PRECAPTURE.20260926_142047.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_restoring_seashores_bacta_2026-09-25T175356.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_seashores_enable_2026-09-25T133443.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/modlists/ModsConfig_before_miasma_predation_proof_2026-09-27.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/rescued/LanternDeeps_RUT/Assemblies/   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it
?? src/RimMandrake/Utils/firehawk_flight_probe.py   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it
```

