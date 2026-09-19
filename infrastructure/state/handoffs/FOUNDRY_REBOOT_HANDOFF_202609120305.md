# FOUNDRY_REBOOT_HANDOFF_202609120305 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609112355`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

Enabling a new mod that leans on a SIBLING mod's C# (a shared "engine"
assembly) is not safe until you deploy BOTH mods — `deploy_custom_mods.py
--mod <X>` only deploys that one mod, never its dependencies. Tonight,
enabling `RustCathedralRoaches` (which references
`RimMandrake.CreatureBehaviors.RM_EatCleanableExtension`) while the
rebuilt `CreatureBehaviors.dll` sat undeployed threw a TypeLoadException
severe enough to trip RimWorld's own "Resetting mods config and trying
again" recovery reset — ModsConfig silently fell back to 6 mods mid-load.
Diagnosed by comparing deployed-vs-repo DLL mtimes (6 hours stale), fixed
by deploying `CreatureBehaviors` explicitly, confirmed clean on relaunch.
Filed to `LESSONS_INBOX.md` already. Check dependency-mod deploy state
before enabling anything new in `ModsConfig.xml`, not just the new mod's
own files.

## What the owner should see

**The canonical Ash'karr save (`CANONICAL_ASHKARR_2026-09-09`) doesn't load
clean against the current full mod list.** It was saved with 573 mods; the
live full list has drifted to 592 (9 gone, 28 added across many waves).
Loading it anyway (`ignoreModCompatibility`) produces **1,842 Scribe "Could
not load reference to" lines across 409 distinct defNames** — overwhelmingly
Megafauna fossil/skeleton scatter (`MA_*`, 744+ hits), plus smaller hits from
Erin's Final Fantasy Animals and two chicken mods. 2 of the 9 missing mods
(Cephaloids, VAEWaste) match a deliberate donor-retirement already in this
repo; the other 7 (Better Crossbreeding, Erin's FF Animals, Little Critters,
Megafauna, Mythic Ages Megafauna Bestiary, R-Hen-G Chaos Chickens) don't have
an obvious explanation I could find. **Needs a ruling**: was dropping these
7 deliberate (in which case the frozen worldbuilding sheet may need a pass
to stop describing scatter that's no longer there), or accidental drift (in
which case they should go back on the full list)? Full detail in
`infrastructure/state/items/WORLDMAP_AUDIT_LIVE_CHECKS_1.md`'s "check 3"
section. Did not touch/fix this myself — flagged only, save file confirmed
untouched (mtime unchanged both times I loaded it).

## What is half-done, and where it stops

- `COMPANION_SILENT_FAILURE_HARDENING_1` — 22 of ~26 lower-value audit
  findings fixed in batch 4, independently re-reviewed (one real regression
  caught and fixed: `jawa/set_stuff` had been accidentally gutted to a
  no-op mid-fix), and the item's own core verify criterion (a known no-op
  write returns `success:false`) confirmed live tonight
  (`jawa/world_tile_set` with no tiles/range). Next action: spot-check a
  couple of batch-4's OTHER read-backs (royal_title, room_get) if someone
  wants full confidence, or just close it — #9 (FindPawn ambiguity) and 4
  documented skips stay DEFERRED regardless, that's not blocking. Not
  closed because I didn't want to close an item I hadn't personally
  finished verifying end-to-end.
- `HUB_TAB_PUBLISHER_MIGRATION_1` — codebase-health publisher wired,
  verified, closed out via `DASHBOARD_HUB_ARTIFACT_1`. artpipe and
  maturity publishers still unwired (their own `data/art.json`/
  `data/maturity.json` republish steps). Next action: pick one, same
  pattern as the health one.
- `RUST_CATHEDRAL_MECHANICS_1` — §2 (wall-tier mining defs) and §6 (roaches)
  built, independently reviewed (including adversarial scrutiny of a new
  Harmony postfix on `CompDeepScanner.ChooseLumpThingDef` — clean), and
  BOTH roach races confirmed spawning live tonight. §1 (hum-mood
  MapComponent + Def type), §3 (living bolts), §4 (eel-fishing), §5
  (deep-drill response) are completely untouched. Next action: §1 is the
  architectural linchpin — bolts read its band, eel-fishing rides its
  ledger coupling — build that next in its own dedicated session, not a
  tack-on.
- `SHOKKWEAVE_SOLE_SOURCE_1` — build-order step 1 (rename, tradeability
  strip, tag strips, commonality) shipped and confirmed live via direct
  `jawa/get_def` reads. The item's own stated verify line — live
  trader-GENERATION proof across all 11 named `TraderKindDef`s — is NOT
  done: no bridge tool exists to generate a specific trader kind's stock
  list on demand (checked `rimbridge/run_lua`'s capability surface, it only
  composes existing tools). Next action: either build that tool
  (`rimbridge-companion` cycle) or a BENCH/owner call that the def-state +
  RimSage source-analysis proof already in the patch file's own comments is
  sufficient without it.
- `WORLDMAP_AUDIT_LIVE_CHECKS_1` — check 3 (loads clean) done, FAILED, see
  "what the owner should see" above. Check 1 (river tiles) done: settled at
  **320 visible / 335 potential** via a full-range `jawa/world_links_get`
  scan, replacing the old four-way ambiguity (217/254/298/326) — whoever
  owns the frozen CSV/audit artifact should adopt this number. Checks 2
  (shortHash provenance — needs the EXACT historical 573-mod list, not
  today's 592, so it's a deliberate separate modlist reconstruction) and 4
  (full tile→mutator decode — `jawa/world_lint` gave a partial signal, 104
  stale marine mutators among 128 total findings, but that's a lint pass
  not the full decode) are not done.

## Traps learned

- The corrupted-mods-reset/undeployed-sibling-DLL trap above — filed to
  `LESSONS_INBOX.md`.
- `jawa/spawn_batch` throws an unhandled `NullReferenceException` (not a
  clean refusal) when given a pawn-race `ThingDef` — it's built for
  buildings/filth/chunks via `GenSpawn`, not pawns. `jawa/spawn_pawn` (by
  `PawnKindDef`, not `ThingDef`) is the right tool for any creature. Noted
  in `COMPANION_SILENT_FAILURE_HARDENING_1` as a candidate for a future
  hardening pass; not yet in `LESSONS_INBOX.md` — adding it there too since
  it's a general "wrong tool for pawns" trap, not specific to this item.
- The huge pile of untracked `infrastructure/artpipe/{done,pending,failed}/*`
  files in `git status` are the art daemon's own working state, not mine —
  left untouched deliberately, not an oversight.

## Closed since the last handoff (4)

- `ART_REGEN_WAVE8_QUEUE_1` — 0221f34fb9d42bb6e6f736fa7386d307bc45e322
- `REMBG_CONCURRENCY_CAP_1` — 2f8d4a99afe03553cee5dd2fbefb9fb4cd3cbd46
- `ART_REGEN_WAVE9_QUEUE_1` — daff602314e50ec965cb9a7b57651c656c7274fe
- `NONDIV4_TEXTURE_FIX_1` — 79715b3d2d7405715c8a947e7cb15adc419d0772

## Filed and still open (7) — the next seat's queue

- `WORLDMAP_AUDIT_LIVE_CHECKS_1` — Four worldmap audit checks needing the live game — batch into next game-up window
- `HUB_TAB_PUBLISHER_MIGRATION_1` — Repoint artpipe/health/maturity publishers to the hub URL; completes the two-seat no-clobber proof
- `MOD_OPTIONS_RETROFIT_1` — Superb mod-options support across ALL our mods: retrofit every shipped RimMandrake/RimStarWars/RimUtinni mod with Mod Settings toggles for its major b
- `VAPOR_TERMINATOR_GEYSER_FIX_1` — Remove/relocate the 21 SteamGeysers_Increased world tiles at/past the terminator (arc>=90) — direct violation of the ruled zero-before-the-terminator 
- `FLOOD_CANYON_BIOME_1` — Standalone RimMandrake-tier biome mod: periodically flooded canyons — chime warning mechanic, flood events (wall of water + explosive growth), not Sta
- `MUDSWALLOW_LIVE_LIST_FIX_1` — Greentide MudSwallow Scan() iterates the LIVE ThingsInGroup list and Destroys mid-loop — skips the shifted haulable and wrongly resets its swallow tim
- `HUB_LAMP_TIME_FIX_1` — Hub lamps mislabel local time as UTC (every age off by the UTC offset — the recorded 'health 7.0 h' was minutes-old data) + hub_check GREY doesn't fai

## Commits

```
0001bce2d Code review: RustCathedralWalls (RUST_CATHEDRAL_MECHANICS_1 §2), all 14 files CLEAN
67cbd7f5a HUB_LAMP_TIME_FIX_1: lamp ages off by UTC offset (confirmed; the recorded 7.0h was the artifact) + hub_check gate holes; caveat on DASHBOARD_HUB_ARTIFACT_1's numbers
077eb2502 MUDSWALLOW_LIVE_LIST_FIX_1 filed (live-list mutation bug, confirmed); GIZKA recon: Tribble module read, gizka already in SW Animal Collection
bfec1a970 FLOOD_CANYON_BIOME_1: flooded-canyons standalone RimMandrake biome mod (owner 2026-09-12); FLOOD_WITNESS_EVENT_1 narrows to the campaign beat
d04712072 Ledger: file VAPOR_TERMINATOR_GEYSER_FIX_1; belt-wave item states
7881bed55 VAPOR_EMITTER_PLACEMENT_1: emitter inventory + rule proposals + frozen-map audit (21 geysers violate terminator rule)
65b9ab9ad Batched live verification round 2: roach spawn confirmed, companion no-op check confirmed, river-tile count settled
241c9caca MOD_OPTIONS_RETROFIT_1: superb mod-options required on every mod (owner 2026-09-12); doctrine in CLAUDE.md
00cf6bedf FLOOD_WITNESS_EVENT_1: witness-event design draft + owner cards (4 routes)
a5bd2278b RUST_CATHEDRAL_MECHANICS_1 §2: wall-tier mining defs (the wall ladder)
ec5a6a510 CSV_REGION_SYNC_1: patched candidate (5 renames, 775 rows) + diff; Abandoned Mines blocked on per-tile authority
175e6e80f EXPLOSIVE_PLANT_GROWTH_1: terminal-moment design draft + owner cards (no build before ruling)
f1106a60b Ledger: close DUNGEON_DESIGN_RESEARCH_1
78234b27a DUNGEON_DESIGN_RESEARCH_1: dungeon design research corpus — sources, metrics catalog, canon experiences, map templates, skill sketches
9b2971f5b MUTATION_MODIFIERS_SURVEY_1: mutation-systems survey table + draft deck (owner rules the deck)
fb20bb12c Mark RUT_Greentide.xml CLEAN: donor GRiNDTerra Biomes references verified
02bca50d1 Lesson: a new mod referencing a sibling mod's not-yet-redeployed class tripped RimWorld's corrupted-mods recovery reset
e15f05a0e Ledger: close RECORD_HUB_HEALTH_PROOF_1; belt-wave claims
286790738 DASHBOARD_HUB_ARTIFACT_1: land FOUNDRY's publisher-side no-clobber proof (RECORD_HUB_HEALTH_PROOF_1)
484da7647 Mark batch-4 companion hardening files CLEAN after independent review
ef1525da6 Fix jawa/set_stuff regression from batch 4: SetStuffDirect call was deleted
8f4e8a0be Companion hardening batch 4: ~27 lower-value silent-failure findings (build-clean --gm, deployed)
a201115a5 Ledger: close NONDIV4_TEXTURE_FIX_1
79715b3d2 NONDIV4_TEXTURE_FIX_1: record our-mods phase done
cf3aee40b NONDIV4_TEXTURE_FIX_1: pad 87 non-%4 textures in our own mods (transparent, centered)
c593d594f HUB_TAB_PUBLISHER_MIGRATION_1: codebase-health hook now regenerates hub/data/health.json
eb27deefd Close DASHBOARD_HUB_ARTIFACT_1 — all verify boxes proven
e4c0e9acd DASHBOARD_HUB_ARTIFACT_1 verify complete: two-seat no-clobber proven live (peer republished health+art, shell+other tabs kept)
feec8c4fa Ledger: claim+start 3 offline items (companion hardening, texture padding, hub publisher migration)
0f08526fc Code review: RUST_CATHEDRAL_MECHANICS_1 §6 (roaches) marked CLEAN, no fixes needed
99a9e5cbc BENCH handoff 202609111830: hub live+pinned, worldmap verified clean, 10 specs drafted, ~25 cards queued, 9 items routed to FOUNDRY
ee63c889f FAUNA_TOLERANCE_NORMALIZATION_1 offline half: Law 5 drafted linter-checkable, census MEASURED (196/297 violate pre-patch)
e264be46b CATHEDRAL_PLAYER_CONCEALMENT_ARC_1 spec drafted: WARY->TOLERATED->VOUCHED->REVEALED on existing machinery; 5 cards
3009765f9 RUST_CATHEDRAL_MECHANICS_1: record §6 (roaches) progress, note the rest of the kit is untouched
4747b1a6d RUST_CATHEDRAL_MECHANICS_1 §6: the roaches (land cleaners)
cb5714c0d Ledger: game DOWN (measured), bridge released after Shokkweave/worldmap live verification session
c4d2e635c Live verification session: Shokkweave confirmed live (partial proof), major worldmap finding — canonical save missing 9 recorded mods
b2827f0f4 Ledger sync: queue drained — card-gated items blocked, companion+ninefold to FOUNDRY, final two lanes claimed
12e6262c0 RIMWORLD_MEMORY_FOOTPRINT_AUDIT_1 delivered: 18.82GB steady-state, crash not OOM, real lever is non-%4 textures
c0ba80ec7 POISON_FOREST_REPASS_1: MEASURED block, weather table, R13 venting written through, struck phrasing deleted
5040448b5 Ledger sync: rust kit to FOUNDRY (build-ready), memory audit + poison repass claimed
cb83fd4f0 Mark 5 rename patches, 2 StatNorm patches, BiomeDescriptions_Ashkarr CLEAN
7c80850cb TIBANNA_EMBARGO_PLOT_1 spec drafted; T1 live contradiction carded (stack ships non-beldon routes vs hard ban)
46ad6e252 SCALD_MECHANICS_1 kit spec drafted; 2 cards to the sitting
6d0f35679 FORGE_MECHANICS_1 kit spec drafted; 3 cards to the sitting; RimSage-era discrepancy logged
3f6cee799 SUMP_MECHANICS_1 kit spec drafted; cards routed to MECHANICS_CARDS_SITTING_1; INDEX kits table completed
ac6174936 Ledger sync: wave-3 claims, ocular/liquid blocked on cards, kyber to FOUNDRY
2d8c2f6ed Close ART_REGEN_WAVE9_QUEUE_1
daff60231 File/claim/start ART_REGEN_WAVE9_QUEUE_1: queue Dactillion/Fanback/Grank art
b28819cd1 Fan-out wave 2 landed: fever wood + rust cathedral kit specs, liquid types mod design; worldmap tab GREEN
cc99988fe Mark Absorbed_Cephaloids (defs+patch) and Absorbed_VAEWasteMegatardi_Defs CLEAN
a7f8208ac Fix miscounted def tally in Absorbed_Cephaloids_Defs.xml header
10043b10d Ledger: claim+start SHOKKWEAVE_SOLE_SOURCE_1
5f994de1e MIASMA_MECHANICS_1 kit spec drafted; POST_FREEZE_WORLDMAP_AUDIT_1 offline verification
2d7f48e28 Mark 4 files CLEAN: rembg concurrency fix, artpiped/artreg spend-tracking changes reviewed
15645eb3c Mark RUT_FurnaceHide and Absorbed_VESucculents (defs+2 patches) CLEAN
f4b18455a Mark 10 Greentide XML/About files clean
661843c1a Guard reflection lookup failure in JawaBenchLoreStageTools
6879314fc Mark 27 SW def/patch files CLEAN (Armoury/Shokk/StructureInjectionsSW/SWBestiary/ArtOverride)
187bf0389 PyrelandsMechanics: fix stale isBad comment, drop dead FlameHarvestExitTicks
f1c842a86 Mark 9 Greentide C# source files and 9 LoreStages files clean
abd4e611d Mark group-D RUT files clean (RM_AftermathRuleDefs, RotSporeKit MantisScythe, About.xml, JawaFactionRoster, Scenario_Utinni)
2f8d4a99a REMBG_CONCURRENCY_CAP_1: move the ONNX-concurrency flock into rembg_cut.py itself
9cbfc8c2d Mark 20 BrainWorms mod files CLEAN (full first-ever review, no findings)
472e00004 LOCAL_IMAGEGEN_TRACK_PARKED_1: last criterion ruled (rembg exempt+capped) — parking record complete
e2fec3c99 RUT group D review: About.xml loadAfter gap, stale MantisScythe comment
b709d5cdf Fix stale MantisScythe comment: costList already points at RSW_FungalMantisClaw
30c69747d No codex dollar estimates (owner 2026-09-11): spend = window % for codex, real $ for gemini history
349152ba4 RUT_Scarlands: gate the whole BiomeDef behind MayRequire Odyssey
f4c56cd19 Mark 6 files CLEAN: PyrelandsWeather_RuledTable, ScarlandsLadder, WarLab crater comp
972818c70 Guard null li entries in LoreStages debug action and ConfigErrors
2c8762586 Fix silent item loss in RM_MapComponent_MudSwallow.DigOut
c993b1af2 Art channels: Gemini OFF (owner 2026-09-11) — budget gate baseline to $0, Codex only
6aa3fd517 Mark CreatureBehaviors JobDefs/ThinkTree XML clean (reviewed, no findings)
ab37da311 Mark 10 ArtOverride files CLEAN (Frostmite/Grithe/Grutt/Kroffa/Puffmite/Spidercat)
3621ca51c Code review: mark RUT_Contagion CLEAN
8da0c5c8e Hub v3 + artreg: renders vs attempts, true 7-day spend window, grouped facing rows
ea0108daa RUT_Greentide: guard TorrentialRain with the Odyssey MayRequire
008faba7b Code review: mark 5 RUT patch/race files CLEAN
774ed90f1 Hub v2: per-target iteration tracking on the art tab; worldmap tab names the freeze gap
7a89cb576 Mark 4 RUT BiomeDefs clean; prune stale MiasmaNurseryJuveniles entry
4b2d5854a Mark 3 XML def files CLEAN
5565905d1 Ledger: file and close ART_REGEN_WAVE8_QUEUE_1 (3 creatures queued by art-pipeline agent, paperwork completed)
54ac7d7ee Mark 5 Python utility/tooling files CLEAN
0221f34fb Ledger: SHOKKWEAVE_SOLE_SOURCE_1 to FOUNDRY — spec build-ready, no cards open
607d64946 Code review: GelatinousSlime mod CLEAN (25 files)
c1fc08412 Card sitting: shokkweave commonality 0.05, K1 deep-time mines, K2 heat unchanged, rembg exempt+capped
3505dc594 Fix stale --selftest usage line in apply_assignment_verdicts.py
9510b7b12 ART_REGEN_WAVE8_QUEUE_1: queue 3 more SW-canon creatures from the owner-approved art:improve pool
6d971c6a8 Mark 6 Aftermath rule-engine C# files CLEAN
92b9cb7b3 Fix NRE risk in AftermathRuleRunner.ResolveTargetFaction
2b12dad59 Code review: EnvironmentalHazards mod CLEAN (20 files)
2eee1995f SHOKKWEAVE_SOLE_SOURCE_1: economy spec drafted — rename, trader strip, four harvest routes
06a473ac6 Fan-out wave 1: kyber trade spec, Ashfall Research Base doc, imagegen-park propagation
32772ab75 DASHBOARD_HUB_ARTIFACT_1: publish the tabbed status hub (shell, generator, checker)
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-12T02:51:46Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml
 M infrastructure/state/queue/BENCH.md
?? defs.sqlite
?? deployed/config/ModsConfig.before-tier-stagedlore.xml
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
?? design/Jawa/worldbuilding/review/serve_homeless.log
?? infrastructure/artpipe/daemon_run_20260911_105041.log
?? infrastructure/artpipe/done/aa_frostmite_v1_east.json
?? infrastructure/artpipe/done/aa_frostmite_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.manifest.json
?? infrastructure/artpipe/done/boma_v1_east.json
?? infrastructure/artpipe/done/boma_v1_east.manifest.json
?? infrastructure/artpipe/done/boma_v1_north.json
?? infrastructure/artpipe/done/boma_v1_north.manifest.json
?? infrastructure/artpipe/done/boma_v1_south.json
?? infrastructure/artpipe/done/boma_v1_south.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_east.json
?? infrastructure/artpipe/done/borcatu_v1_east.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_north.json
?? infrastructure/artpipe/done/borcatu_v1_north.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_south.json
?? infrastructure/artpipe/done/borcatu_v1_south.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_east.json
?? infrastructure/artpipe/done/cinderwing_v1_east.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_north.json
?? infrastructure/artpipe/done/cinderwing_v1_north.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_south.json
?? infrastructure/artpipe/done/cinderwing_v1_south.manifest.json
?? infrastructure/artpipe/done/duskram_v1_east.json
?? infrastructure/artpipe/done/duskram_v1_east.manifest.json
?? infrastructure/artpipe/done/duskram_v1_north.json
?? infrastructure/artpipe/done/duskram_v1_north.manifest.json
?? infrastructure/artpipe/done/duskram_v1_south.json
?? infrastructure/artpipe/done/duskram_v1_south.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_east.json
?? infrastructure/artpipe/done/emberscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_north.json
?? infrastructure/artpipe/done/emberscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_south.json
?? infrastructure/artpipe/done/emberscythe_v1_south.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_east.json
?? infrastructure/artpipe/done/featherfeel_v1_east.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_north.json
?? infrastructure/artpipe/done/featherfeel_v1_north.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_south.json
?? infrastructure/artpipe/done/featherfeel_v1_south.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_east.json
?? infrastructure/artpipe/done/fenshear_v1_east.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_south.json
?? infrastructure/artpipe/done/fenshear_v1_south.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_east.json
?? infrastructure/artpipe/done/grubhorn_v1_east.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_north.json
?? infrastructure/artpipe/done/grubhorn_v1_north.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_south.json
?? infrastructure/artpipe/done/grubhorn_v1_south.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_east.json
?? infrastructure/artpipe/done/hawkbat_v1_east.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_north.json
?? infrastructure/artpipe/done/hawkbat_v1_north.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_south.json
?? infrastructure/artpipe/done/hawkbat_v1_south.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_east.json
?? infrastructure/artpipe/done/insectomorph_v1_east.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_north.json
?? infrastructure/artpipe/done/insectomorph_v1_north.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_south.json
?? infrastructure/artpipe/done/insectomorph_v1_south.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_east.json
?? infrastructure/artpipe/done/kinrath_v1_east.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_north.json
?? infrastructure/artpipe/done/kinrath_v1_north.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_south.json
?? infrastructure/artpipe/done/kinrath_v1_south.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_east.json
?? infrastructure/artpipe/done/mycolith_v1_east.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_north.json
?? infrastructure/artpipe/done/mycolith_v1_north.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_south.json
?? infrastructure/artpipe/done/mycolith_v1_south.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_east.json
?? infrastructure/artpipe/done/ollopom_v1_east.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_north.json
?? infrastructure/artpipe/done/ollopom_v1_north.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_south.json
?? infrastructure/artpipe/done/ollopom_v1_south.manifest.json
?? infrastructure/artpipe/done/orray_v1_east.json
?? infrastructure/artpipe/done/orray_v1_east.manifest.json
?? infrastructure/artpipe/done/orray_v1_north.json
?? infrastructure/artpipe/done/orray_v1_north.manifest.json
?? infrastructure/artpipe/done/orray_v1_south.json
?? infrastructure/artpipe/done/orray_v1_south.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_east.json
?? infrastructure/artpipe/done/pekopeko_v1_east.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_north.json
?? infrastructure/artpipe/done/pekopeko_v1_north.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_south.json
?? infrastructure/artpipe/done/pekopeko_v1_south.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_east.json
?? infrastructure/artpipe/done/scarrend_v1_east.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_north.json
?? infrastructure/artpipe/done/scarrend_v1_north.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_south.json
?? infrastructure/artpipe/done/scarrend_v1_south.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_east.json
?? infrastructure/artpipe/done/slagmaw_v1_east.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_north.json
?? infrastructure/artpipe/done/slagmaw_v1_north.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_south.json
?? infrastructure/artpipe/done/slagmaw_v1_south.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_east.json
?? infrastructure/artpipe/done/sludrin_v1_east.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_north.json
?? infrastructure/artpipe/done/sludrin_v1_north.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_south.json
?? infrastructure/artpipe/done/sludrin_v1_south.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_east.json
?? infrastructure/artpipe/done/verdaunt_v1_east.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_north.json
?? infrastructure/artpipe/done/verdaunt_v1_north.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_south.json
?? infrastructure/artpipe/done/verdaunt_v1_south.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_east.json
?? infrastructure/artpipe/done/vornskyr_v1_east.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_north.json
?? infrastructure/artpipe/done/vornskyr_v1_north.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_south.json
?? infrastructure/artpipe/done/vornskyr_v1_south.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_east.json
?? infrastructure/artpipe/done/whisperbird_v1_east.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_north.json
?? infrastructure/artpipe/done/whisperbird_v1_north.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_south.json
?? infrastructure/artpipe/done/whisperbird_v1_south.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.manifest.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.manifest.json
?? infrastructure/artpipe/failed/fenshear_v1_north.json
?? infrastructure/artpipe/failed/fenshear_v1_north.manifest.json
?? infrastructure/artpipe/pending/shiro_v1_east.json
?? infrastructure/artpipe/pending/shiro_v1_north.json
?? infrastructure/artpipe/pending/shiro_v1_south.json
?? infrastructure/artpipe/registry.jsonl.lock
```

