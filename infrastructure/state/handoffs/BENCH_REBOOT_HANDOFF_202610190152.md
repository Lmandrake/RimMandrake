# BENCH_REBOOT_HANDOFF_202610190152 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610181718`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**Next BENCH session = force-finish FlowWorks** (owner 2026-10-18: *"set notes to prepare for finishing FlowWorks in Bench. We will be force advancing it as quickly as possible"*). Open `design/RimMandrake/flowworks_finish_board_2026-10-18.md` first: the depth rebuild is mostly BUILT and live-proven by FOUNDRY but the ledger still says `proposed`, so step 1 is a ledger truth pass, not code; the one big unbuilt package is P14 (`POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD`). Biome art no longer blocks anything (standing_rulings.md "Biome art never blocks").

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Four FlowWorks-finish questions are drafted as cards on the finish board (scope of "finished"; ship with borrowed art — 97 of 100 textures, MEASURED 2026-10-05; who goes down into a pit; keep V2/V7/D3 defaults). Ask them first thing.
- Five art sheets stay open for LATER (not blocking): Dragonsnake swim, creature facings (FACINGS_REDRAW_NORTHS_ABOUT_FACE), xeno heads (new heads are oversized full-colour paintings — need redraw in grey tintable style before wiring), brine crown/elder, Leaning Scrub open rows. Servers die with this session; rebuild with serve_gated.py.
- Ugnaught lifespan is now 320 y (quad gene) vs canon "200+"; no 2.5x gene exists — his call if he wants a custom gene.
- Deploy owed: `--compose biomes` plan is 492 files, mostly FOUNDRY's Alpha Biomes stand-in retirement; also carries BENCH's Grey Sea sallik removal, the salt-snow crown swap DLL and the Cauldron gas-centroid readout. Not applied this session.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `ALPHA_BIOMES_MIGRATE_DISEASES_AND_CODE` — handed back to FOUNDRY (its uncommitted retirement edits were in flight); NEXT: FOUNDRY ports the 3 AB_ diseases per design/RimMandrake/alpha_biomes_retirement_2026-10-16.md.
- `ALPHA_BIOMES_MIGRATE_PLANTS_TO_RM_TWINS` — handed back to FOUNDRY; NEXT: FOUNDRY ports the 14 AB_ plants (donor-copy stand-in art allowed, owner 2026-10-18).
- `ALPHA_BIOMES_RETIRE_THE_LAST_PLANT_DONOR` — FOUNDRY's, in flight; NEXT: FOUNDRY commits its About.xml/loadAfter strip, then runs DONOR_OFF_LOAD_PROVE_AFTER_BENCH.
- `CONTAGION_DIVE_HARDEN_WANDERERS_WELCOME` — rows hardened + no-Burn control, offline selftest green (e54e234aca); NEXT: run native_dives_for_roof and native_no_dive_without_burn live, then close.
- `LEANINGSCRUB_SHEET_ART_REDO_1` — open-rows sheet built (83b1bca0cc), art now non-blocking; NEXT: leave for the later art pass; only Venomvine B install is mechanical (`art.py enact --apply` once VENOMVINE_BUILD_SCRUB_GROWS_TEETH settles).
- `FLOWWORKS_FINISH_BOARD` (no item; loop rimworld-flowworks-finish) — board written ae5a9ae8b5; NEXT: do the ledger truth pass in step 1 of design/RimMandrake/flowworks_finish_board_2026-10-18.md.
- `GREYSEA_FLOOR_PASS_1` — sallik removed (3c42ca79fa), crown swap built (3bfb9232b/c56cb90504), not deployed; NEXT: deploy `--compose biomes` with FOUNDRY's agreement, then install the crown pick when art is reviewed.
- `CAULDRON_SUITE_WIDEN_RUINS_STILL_UNREAD` — 10 rows + gas centroid readout (f9f651c9a6, 34356da287), not deployed; NEXT: deploy biomes, then run the ruins/works/drift chains live.
- `DRAGONSNAKE_PAIR_BUILD_ONE_PALE_ONE_PROPER` — four variants pooled + deployed (d8f5cfbf43); NEXT: install the swim picks when the art pass reaches it, then close.
- `XENOTYPE_CANON_CORRECTION_1` — gene/lifespan rulings applied + deployed (55f9b4ff2c); NEXT: redraw the four heads in grey tintable style at vanilla size before any wiring (art pass).
- `BUILDUP_BUILD_CLONES_STOP_BREEDING` — filed for FOUNDRY, owner answers recorded; NEXT: FOUNDRY builds the reaper/untracking per design/RimMandrake/buildup_prevention_design_2026-10-18.md (Transient untracking appears already landed).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- rimflow writes with --owner-said/--by-card land in OWNER.jsonl, not the seat shard — commit it too (filed: lessons)
- `rimflow close --sha HEAD` records the literal string "HEAD" (see: using-rimflow skill; corrected by note on CAULDRON_BIOME_FIX_DRY_STORM_LEFTOVER)
- gen_races_mod.py wrote files before its loss guard refused; now atomic with a regeneration selftest (see: RACES_GEN_REPAIR_STOP_SHREDDING_FIRST)
- art enact named new pool files by sheet letter and could overwrite a kept picture; fixed with selftest_enact_free_letter (see: afbd112603)
- zsh does not word-split $VAR in a git pathspec — list paths literally (see: instrument_traps.md)

## Closed since the last handoff (5)

- `RONTO_PACK_TEXTURE_REPAIR_SADDLEBAGS_MISSING` — 422c72944e
- `TREE_TIERS_JUDGE_FORTY_FOUR_TRUNKS` — afbd112603
- `RACES_GEN_REPAIR_STOP_SHREDDING_FIRST` — 399406fa5e
- `FLOWWORKS_BRIDGES_DESIGN_SPAN_ANYTHING` — fe4b9d8152
- `CANAL_COVER_DESIGN_WET_FOXHOLE` — fe4b9d8152

## Filed and still open (2) — the next seat's queue

- `FACINGS_REDRAW_NORTHS_ABOUT_FACE` — Regenerate the wrong north/east facings (Dragonsnake A-D + swim, Varactyl_m, Strill, OpeeSeaKiller, Yobshrimp, Whisperbird, Lothcat_f, TeeMuss) from a
- `TEXREGEN_SWBESTIARY_DECIDE_NO_ROSTER_OWNS_IT` — 394 SWBestiary defs ship donor bytes and sit in no biome roster: decide which get regenerated

## Commits

```
ae5a9ae8b5 FlowWorks finish board: items, split, owner cards, critical path
167558b24b ledger: TEXREGEN_STANDINS_INSTALL_RENDERS_WAITING bulk-accepted and closed (owner words, relayed)
9d355d678a WeepingStones, Bacta, Cuisine, UtinniPatches: bulk-accept renders; borrowed vanilla animals repointed
659122dfcb Biome mods M-W + SolarMirrors: bulk-accept renders; vanilla-path defs repointed to own textures
432f75f30c Biome mods A-L: bulk-accept finished artpipe renders over donor/placeholder art
323fcac4bd SWBestiary: bulk-accept finished artpipe renders over donor art (2/2)
25b9dc7c6c SWBestiary: bulk-accept finished artpipe renders over donor art (1/2)
555dae093b conversations: catch-up commit at BENCH handoff (owner 2026-10-18: the handoff commits them)
51b156afe5 lesson: owner-provenance ledger writes land in OWNER.jsonl
30e52696d2 Owner ruling: biome art accepted as-is, art review secondary; FlowWorks force-finish next
c9e5f59e84 StructureInjectionsRUT: vault green goo -> RM_Wuum, black jelly wall -> VFEI2_InsectJellyWall, war-lab slurrypede cell emptied
7318dceb99 RUT twin biomes: repoint every Alpha Biomes row/terrain/weather/disease to our ports
83fbafd289 Alpha Biomes retirement: RM_ ports of the donor plants/terrains/weathers the frozen RUT twins still name
0ddbfb87e0 UtinniPatches: drop dead Alpha Biomes rows (planet biome mix, rime-nodule echo)
bf9bf04f5c Alpha Biomes retirement: Abyss sands ported, Cauldron chunk rows and explosive-growth donor rows cleared
20f2c5c98d CrackedLands: owner-kept art moves out of the FloodedCanyon stub; stub folder and compose entry CrackedLandsKeptArt deleted
4bb89a74d3 DivingInteraction: commit the ledgered removal of a composed-duplicate SnakePlant stand-in
b28a7414fe Donor retirement: delete 9 top-level FindMod blocks on Alpha Biomes / Alpha Animals (can never match again)
03f9dcf364 TheSump: port Alpha Biomes grassy sand/lush grass; RustCathedral terrains get StandIn art copies
cfc9d28f9c Miasma: port Alpha Biomes fertile mud and its three diseases as RM_ defs
... 118 more: git log --oneline 422c72944e..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : UP  → corrected to DOWN, measured now
- Bridge: FREE    since 2026-10-19T00:07:40Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/liquid_containers_four_styles_sheet_2026-10-16.decisions.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
 M Transient/modcheck/fixtures.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
 M deployed/config/ModsConfig.before-tier-bridge.xml   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
 M infrastructure/state/art/events/BENCH.jsonl   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
 M src/RimMandrake/FlowWorks/northstar/review/map/KEYSHEET.md   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
 M src/RimMandrake/FlowWorks/northstar/review/map/keysheet.html   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
 M src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchPawnKitTools.cs   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? deployed/config/ModsConfig.before-gss-restore-20261010.xml   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? deployed/config/ModsConfig.before-tier-flowworks_vepipe.xml   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? deployed/config/ModsConfig.before-tier-ratchet_pilot.xml   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? deployed/config/ModsConfig.swap-active.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/out/   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/guides/   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/out/   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_east.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_north.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_south.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.png   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.png   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.png   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.png   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.png   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.png   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runA.out   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runB.out   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runC.out   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/gen.out   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Futuristic/   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Industrial/   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Modern/   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_east.png   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_north.png   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_south.png   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_west.png   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Scrapper/   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Futuristic.png   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Industrial.png   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Modern.png   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Scrapper.png   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_cap.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_h_spill.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_h_upstream.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_v_east.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_cap.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_h_spill.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_h_upstream.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_v_east.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_cap.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_h_spill.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_h_upstream.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_v_east.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_cap.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_h_spill.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_h_upstream.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_v_east.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/foam_toe.log   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T125537.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T130318.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T144034.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T161200.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T162747.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T034753.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T040637.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T041535.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T042312.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T050823.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/sprinkler_live_result_20261017T155357.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T135834.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T135854.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T135923.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T140243.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T140307.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T140728.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T141144.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T141624.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T141722.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T141802.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T141913.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T141941.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T142026.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T142323.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T142428.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T142939.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T144343.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261011T052325.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261016T125532.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/GSS   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T220702.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T230453.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261011T033650.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230218.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230455.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230639.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T231027.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T231203.json   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   BENCH clone, earlier sessions (derived output / backups / generated art; untouched this session; disposal owed by BUILDUP_BUILD_CLONES_STOP_BREEDING)
```

