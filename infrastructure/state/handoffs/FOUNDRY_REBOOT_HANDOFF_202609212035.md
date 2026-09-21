# FOUNDRY_REBOOT_HANDOFF_202609212035 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609210812`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

`BIOME_MOD_SPLIT_EXECUTION_1` is genuinely unblocked now — all ten §7 questions ruled,
23 per-biome `<NAME>_RM_MOD_BUILD_1` items filed with full Phase A specs, and one is
built, live-proven and closed (`FLOODEDCANYON_RM_MOD_BUILD_1`) as the working pattern for
the rest: when a `RM_` twin already exists with its own generic (vanilla-Core) body, do
NOT merge the campaign `RUT_` content into it — build the campaign roster/weather/terrain
as a Utinni-layer `PatchOperationConditional`/`Replace` onto the `RM_` def (mirror
`WildAnimals_Pyrelands.xml`'s exact shape), freeze the `RUT_` twin with one header
comment, and leave the generic body untouched so any non-campaign RimWorld game still
gets ordinary vanilla-core wildlife. This is the shape every remaining twin
(`GREENTIDE_RM_MOD_BUILD_1`, `GELATINOUSSLIME_RM_MOD_BUILD_1`, `PYRELANDS_RM_MOD_BUILD_1`)
should follow — do not re-derive it from scratch.

## What the owner should see

- Answered four question cards this wave (vorrel, yanker, Warscar/Stall/Gale, scrap-nest
  theft shape) — see `STAGGERSEED_SHIPPING_NAME_1`, `ARIDSHRUBLAND_SHIPPING_NAMES_1`,
  `SCARLANDS_RENAME_OURS_1`, `SCRAPNEST_BIRD_BASE_THEFT_1` (closed/items, prose has the
  verbatim rulings) — flagging only because they were answered live in chat, not carded,
  so there's no separate review artifact.
- `BLUE_DESERT_LIFE_AUTHORING_1`'s build left the three pre-existing donor plants
  (`AB_ToxiGrass`/`AB_CrystalHorn`/`PoisonPlantTallGrass`) in `RUT_BlueDesert`'s
  `wildPlants` **unresolved against the sheet's own ban 1** (no water-metabolism life on
  this biome) — deliberately not cut, since removing them wasn't this item's call. Worth
  a ruling: keep them as a stated exception, or cut and replace with more hydrocarbon
  flora.
- Same item's design brief (`blue_desert_hydrocarbon_life.md` §10) has several open
  questions it declined to decide (a `dovvik` 4th resident, corpse warm-reactivity gap,
  juvenile blast radius, tameability, a missing chemfuel-refinery recipe for `RM_ColdWax`)
  — none blocking, all just sitting there for whenever you want to look.
- `SLIME_GENE_ARCHIVE_BUILD_1` built to the FROZEN sheet's real 33 A-list targets, not the
  22 the design brief said — the brief undercounted (missed the "local denizens" table).
  Built correctly against the sheet; flagging only so you know the brief itself has a gap
  if anyone reads it later.

## What is half-done, and where it stops

- `ARIDSHRUBLAND_SHIPPING_NAMES_1` — doing; NEXT: check whether BENCH's in-flight work
  item for "the fuzz" (`RUT_Fuzz`) has landed a name — owner said "wait" on this one
  specific entry, everything else on the card (giant/snake/venomvine/Stall/Gale) is
  already ruled and shipped. Close this item once the fuzz name lands.
- `SCRAPNEST_BIRD_BASE_THEFT_1` — proposed, ruled but not built; NEXT: build the theft
  mechanic per the ruling recorded on the item (stockpiles included, delivered as a
  periodic event-flock incident, player alert required) — relax `JobGiver_HoardScrap`'s
  storage guard for incident-spawned flocks only, keep the home-area nest-siting guard as
  is, add the incident + letter, live-verify on a quicktest.
- `DESERT_PORT_PLACEHOLDER_ART_1` — doing (from a prior sitting, untouched this wave
  except for a priority bump); NEXT: once the artpipe daemon clears its quota block
  (~2026-09-26T19:52 UTC), check `infrastructure/artpipe/registry.jsonl` for
  `generated`/`validated` events on the 13 still-pending desert species
  (`RSW_Sandstrider`, `RSW_Spineroller`, `RSW_Sandhorn`, `RSW_Dunestalker`,
  `RSW_Ferroclaw`, `RSW_Sandmaw`, `RSW_Tuskcoil`, `RSW_Cindermite`, `RSW_Stareling`,
  `RSW_Voltmaw`, `RSW_Dunegrass`, `RSW_VellaraBloom`, `RSW_SweetbarkTree`), land whatever
  has rendered, wire texPaths, deploy.
- `TITANOSLIME_SLIME_BIOME_1` — doing; NEXT: same as above, art job `rmtitanoslime_v1`
  (south/east/north, 1024px) is queued at priority 100 and waiting on the same
  quota-blocked daemon — land it once it renders. Mechanics (items 1-6 of the item's own
  build list) are already live-verified; only art (item 7) remains.
- `SCARLANDS_STANDALONE_MOD_1` — proposed, not started; NEXT: this is the actual
  `RM_Warscar` defName move + `mandrake.rut.scarlandsladder` absorption (the label-only
  collision fix already shipped separately). Full spec is in the item; follow the same
  twin-merge pattern as `FLOODEDCANYON_RM_MOD_BUILD_1` (see "one thing to carry forward"
  above) once picked up.
- `BIOME_MOD_SPLIT_EXECUTION_1` — doing, umbrella item; NEXT: claim the remaining 22
  `<NAME>_RM_MOD_BUILD_1` items one at a time (listed under "filed and still open" below)
  following the Flooded Canyon twin-merge pattern; each needs its own bridge-driven
  quicktest proof, so dispatch them one at a time or coordinate bridge access if running
  several in parallel.

## Traps learned

- `deploy_custom_mods.py`'s "no packageId in About.xml" can mean the file failed to
  parse at all (a raw unescaped `<`/`<=` in description text), not that the packageId
  is missing — check the file parses before chasing the wrong field (filed: LESSONS_INBOX).
- `rimflow close --sha` records whatever sha you hand it; close AFTER committing the fix,
  never before, or the event's provenance points at a commit that predates the actual fix
  (filed: LESSONS_INBOX).
- A background-dispatched subagent will sometimes background its own `run_selftests.py`
  despite an explicit foreground-only instruction and report an interim "waiting on my
  own background task" — not a deadlock, the harness auto-resumes and re-notifies, but
  budget for the extra round trip (filed: LESSONS_INBOX).
- The artpipe daemon is quota-blocked until ~2026-09-26T19:52 UTC (both meters hit
  ~89-91% used right before it stopped) — confirmed via `throughput.jsonl`'s own
  `secondary_resets_at`, not guessed (filed: LESSONS_INBOX). Don't expect new renders
  before then; the process itself (PID stays alive) is not the signal, `done/`/
  `throughput.jsonl` mtime is.

## Closed since the last handoff (22)

- `PYRELANDS_DEFNAME_RENAME_1` — bf43fce41cd50ae1f7dbc5d17c8cbd29aecd772f
- `BARREN_REGIONS_NAME_NOTHING_1` — b02c2690a2c8aeca326fc5ec8b80b38d18ab1339
- `SHEET_REVIEWED_FLAG_UNIFORM_1` — 632cfb6273a8a8318956b4946200e8d52e82648b
- `SWEETLINE_WOOL_HARVEST_1` — 5f35f97970c801cdb8c196ec7f1296306aadda6f
- `TUNNELSNAKE_VIOLATES_SIZE_LADDER_1` — c0c3009776465bd68470910532371c5ab7eb5a40
- `PATCH_FILES_UNDER_DEFS_INERT_1` — f2c5556d1e883d27587e69002259bb7449af82d7
- `GELATINOUSSLIME_FIRST_LOAD_ERRORS_1` — 91d57b4039cad16d24eebd7cbeba161d8946d702
- `TITANOSLIME_PERMANENT_GROWTH_LIVE_1` — 501aeeade
- `UMBRA_IS_A_REGION_NOT_A_BIOME_1` — a7331975865612c754e43c35f841eeac4f7d80e5
- `SCARLANDS_RENAME_OURS_1` — 72c7e5fa4741273cc74ca8f78ccb6dea62634c07
- `STAGGERSEED_SHIPPING_NAME_1` — 56ffc5d17
- `DESERT_STAGGERSEED_BUILD_1` — 56ffc5d17
- `ROT_SIZE_REJUDGE_APPLY_1` — 32fd86e7d
- `ROT_ROSTER_DEAD_DONOR_NAMES_1` — 87073b902
- `SWBESTIARY_UNPREFIXED_DONOR_DEFS_1` — 3cbf9cff0
- `FLOODEDCANYON_RM_MOD_BUILD_1` — 962ee9a80
- `DIRTY_CODE_REVIEW_LOOP_RESTART_16` — a9149daab
- `DIRTY_CODE_REVIEW_LOOP_RESTART_17` — a9149daab
- `RIMTHEMES_VBE_BACKGROUND_CONFLICT_1` — a9149daab
- `BLUE_DESERT_LIFE_AUTHORING_1` — 4299f9262
- `LIVE_ITEM_GLOB_DRIFT_1` — 8871bf937
- `SLIME_GENE_ARCHIVE_BUILD_1` — 990a0f50f

## Filed and still open (26) — the next seat's queue

- `FEATURE_DRAWCENTER_UNVERIFIED_1` — Only 2 of 71 world features have a verified drawCenter, and growing labels make a wrong one worse
- `SCARLANDS_STANDALONE_MOD_1` — Scarlands biome-mod split: RM_Warscar, absorb ScarlandsLadder
- `STILLSAND_RM_MOD_BUILD_1` — Phase A: build RM_Stillsand as its own RimMandrake mod (mandrake.rm.stillsand) — the Stillsand (extreme desert; campaign label "the Dune Sea" stays a 
- `LONGSHADE_RM_MOD_BUILD_1` — Phase A: build RM_LongShade as its own RimMandrake mod (mandrake.rm.longshade) — the Long Shade (the livable desert)
- `THEROT_RM_MOD_BUILD_1` — Phase A: build RM_TheRot as its own RimMandrake mod (mandrake.rm.therot) — the Rot - absorbs mandrake.rut.rotsporekit (151 files)
- `WASTELAND_RM_MOD_BUILD_1` — Phase A: build RM_Wasteland as its own RimMandrake mod (mandrake.rm.wasteland) — the Wasteland - owns the RUT_WastelandBrine terrain family
- `NIGHTSIDEICE_RM_MOD_BUILD_1` — Phase A: build RM_NightsideIce as its own RimMandrake mod (mandrake.rm.nightsideice) — the Nightside Ice - thin by design, but a Lantern Deeps host su
- `FORSAKENCRAGS_RM_MOD_BUILD_1` — Phase A: build RM_ForsakenCrags as its own RimMandrake mod (mandrake.rm.forsakencrags) — the Forsaken Crags
- `BLUEDESERT_RM_MOD_BUILD_1` — Phase A: build RM_BlueDesert as its own RimMandrake mod (mandrake.rm.bluedesert) — the Blue Desert - BLUE_DESERT_LIFE_AUTHORING_1 builds INTO this mod
- `LEANINGSCRUB_RM_MOD_BUILD_1` — Phase A: build RM_LeaningScrub as its own RimMandrake mod (mandrake.rm.leaningscrub) — the Leaning Scrub (was arid shrubland, a vanilla label)
- `POISONFOREST_RM_MOD_BUILD_1` — Phase A: build RM_PoisonForest as its own RimMandrake mod (mandrake.rm.poisonforest) — the Poison Forest
- `RUSTCATHEDRAL_RM_MOD_BUILD_1` — Phase A: build RM_RustCathedral as its own RimMandrake mod (mandrake.rm.rustcathedral) — the Rust Cathedral - absorbs rustcathedralhum/roaches/walls
- `GREENTIDE_RM_MOD_BUILD_1` — Phase A: build RM_Greentide as its own RimMandrake mod (mandrake.rm.greentide) — the Greentide - twin pair, mod EXISTS (123 vs 287 lines)
- `WEEPINGSTONES_RM_MOD_BUILD_1` — Phase A: build RM_WeepingStones as its own RimMandrake mod (mandrake.rm.weepingstones) — the Weeping Stones
- `PYRELANDS_RM_MOD_BUILD_1` — Phase A: build RM_Pyrelands as its own RimMandrake mod (mandrake.rm.pyrelands) — the Pyrelands - twin pair, mod EXISTS; defName rename done at 84d42c6
- `CONTAGION_RM_MOD_BUILD_1` — Phase A: build RM_Contagion as its own RimMandrake mod (mandrake.rm.contagion) — the Contagion
- `WEBWORK_RM_MOD_BUILD_1` — Phase A: build RM_Webwork as its own RimMandrake mod (mandrake.rm.webwork) — the Webwork
- `GELATINOUSSLIME_RM_MOD_BUILD_1` — Phase A: build RM_GelatinousSlime as its own RimMandrake mod (mandrake.rm.gelatinousslime) — the Slime - twin pair, mod EXISTS; TITANOSLIME_SLIME_BIOM
- `MIASMA_RM_MOD_BUILD_1` — Phase A: build RM_Miasma as its own RimMandrake mod (mandrake.rm.miasma) — the Miasma
- `THEFORGE_RM_MOD_BUILD_1` — Phase A: build RM_TheForge as its own RimMandrake mod (mandrake.rm.theforge) — the Forge
- `FEVERWOOD_RM_MOD_BUILD_1` — Phase A: build RM_FeverWood as its own RimMandrake mod (mandrake.rm.feverwood) — the Fever Wood
- `THESUMP_RM_MOD_BUILD_1` — Phase A: build RM_TheSump as its own RimMandrake mod (mandrake.rm.thesump) — the Sump
- `TERMINALBIOMES_RM_MOD_BUILD_1` — Phase A: build RM_TheScald/RM_PropaneLake/RM_TwilightSea/RM_GreySea as its own RimMandrake mod (mandrake.rm.terminalbiomes) — FOUR biomes in ONE mod, 
- `LANTERNDEEPS_RM_MOD_BUILD_1` — Phase A: build RM_LanternDeeps as its own RimMandrake mod (mandrake.rm.lanterndeeps) — the Lantern Deeps - an INJECTION layer, no RUT_ twin; skips Pha
- `MIASMA_FEVERWOOD_GREENTIDE_BMT_1` — Miasma/FeverWood/Greentide rosters carry live BMT_ (Biomes! Caverns) fauna rows, same defect as the Rot/Forge
- `FURNACEBEAST_WORLD_MIGRATION_1` — Furnace-beast world-scale thermal migration: herd crosses biomes off-map (world leg, split from FURNACEBEAST_THERMAL_CYCLE_1)

## Commits

```
f8304235e rimflow: close SLIME_GENE_ARCHIVE_BUILD_1, move prose to items/closed/
990a0f50f SLIME_GENE_ARCHIVE_BUILD_1: build the campaign gene archive, replace placeholder content
c7bba0344 ledger sync: close LIVE_ITEM_GLOB_DRIFT_1 at 8871bf937
8871bf937 LIVE_ITEM_GLOB_DRIFT_1: triage the 8 items/*.md with no ledger row
e2903f911 LIVE_ITEM_GLOB_DRIFT_1: move 79 closed-but-present items into items/closed/
ba6922edc rimflow: close/drop/supersede now MOVE prose to items/closed/ (LIVE_ITEM_GLOB_DRIFT_1)
e510ef282 rimflow: close BLUE_DESERT_LIFE_AUTHORING_1 at 4299f9262
4299f9262 BLUE_DESERT_LIFE_AUTHORING_1 steps 2-5: build dorrak/krissek/vekkit and the transparent fractal flora
a9149daab rimflow: close FLOODEDCANYON_RM_MOD_BUILD_1 at 962ee9a80
962ee9a80 FLOODEDCANYON_RM_MOD_BUILD_1: merge RUT_CrackedLands into RM_FloodedCanyon
dd7d58287 EXPLOSIVE_PLANT_GROWTH_1: roster regenerated; four stale statements corrected
c9efa4eeb ledger sync: EXPLOSIVE_PLANT_GROWTH_1 owner sitting 2026-09-21
fe1bf2e21 EXPLOSIVE_PLANT_GROWTH_1: owner reshaped the mechanic - Churn default, Burst rare
7569fc4ec SWBESTIARY_UNPREFIXED_DONOR_DEFS_1: move closed item to items/closed/
d438eb35b rimflow: sync ledger for SWBESTIARY_UNPREFIXED_DONOR_DEFS_1 claim/start/close
45e0bdb22 SWBESTIARY_MISSING_BODYPART_DEFS_1: finish the closed-item move to items/closed/
3cbf9cff0 SWBESTIARY_UNPREFIXED_DONOR_DEFS_1: dedup donor body/body-part defs, fix live collision
ab95ad95b BLUE_DESERT_LIFE_AUTHORING_1: step 1 design brief — dorrak, krissek, vekkit, flora spec
9783ac74a rimflow: sync ledger for ROT_ROSTER_DEAD_DONOR_NAMES_1 close + MIASMA_FEVERWOOD_GREENTIDE_BMT_1 file
87073b902 ROT_ROSTER_DEAD_DONOR_NAMES_1: DROP MA_Sporemole, the last open call
... 56 more: git log --oneline c397bf8a6..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-21T18:30:17Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   automated health publisher (rimflow-triggered regen) -- not this session
 M Transient/codebase_health.json   automated health publisher -- not this session
 M Transient/codebase_health_artifact.html   automated health publisher -- not this session
 M design/Jawa/fauna/cast_assignment.csv   BENCH, concurrent EXPLOSIVE_PLANT_GROWTH_1 work -- not mine to commit
 M infrastructure/artpipe/registry.jsonl   artpipe daemon's own write (job registrations, incl. my rmtitanoslime_v1 queue) -- self-writing, not a manual edit
 M infrastructure/dashboards/hub/data/health.json   automated health publisher -- not this session
 M infrastructure/state/codebase_health_last.json   automated health publisher -- not this session
 M infrastructure/state/queue/BENCH.md   rimflow's own queue-snapshot regen, not hand-edited -- not this session
 M infrastructure/state/queue/FOUNDRY.md   rimflow's own queue-snapshot regen, not hand-edited -- not this session
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\claude-1000\\-mnt-d-Luke-dev-Rimworld\\84f9b274-abd5-4c73-81fd-7f936a8b3cc9\\scratchpad\\check_tile.py"   pre-existing bogus escaped-Windows-path artifact, flagged in the prior handoff too -- not ours to interpret
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   same as above -- not ours to interpret
?? infrastructure/state/.rimflow_conc_97j8px_9/   rimflow's own concurrency-lock scratch dir, self-cleaning -- not a real edit
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing untracked backup from 2026-09-11 -- not this session
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   FOUNDRY subagent's own pre-quicktest ModsConfig backup (FLOODEDCANYON_RM_MOD_BUILD_1) -- safe to leave as a record, item is closed
```

