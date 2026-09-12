# FOUNDRY_REBOOT_HANDOFF_202609121737 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609121425`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

**A species with its own dedicated `mandrake.rsw.<name>artoverride` mod gets
silently regressed by `MLIE_FAUNA_ABSORPTION_1`'s normal pipeline.** Those
override mods ship owner-approved custom art at the SAME relative texPath
the donor uses, deliberately loaded after the donor so they win the
same-path resolution. `mandrake.rsw.swbestiary` (where every ported species
lands) loads AFTER every one of those override mods — so extracting and
shipping donor art for an already-overridden species silently reverts the
verified-live custom art back to donor art, with zero errors or warnings
anywhere. Confirmed live for `RSW_Anooba` tonight (shipped, then fixed
retroactively in `5a8fc8c1c`) and caught before-commit for `RSW_Dragonsnake`
(`8dc279c64`). **Before porting any of `Mynock`, `Kreetle`, `Horax`,
`Fambaa`, `Zakkeg`, `Ronto`** (still in the Wave C worklist), check
`src/RimStarWars/<Name>ArtOverride/About/About.xml` first for which exact
facings it covers — the split isn't uniform (Anooba's exempts only the
corpse texture; Dragonsnake's also exempts the swimming variant) — and
don't ship a competing SWBestiary copy at those paths. Filed as
`MLIE_ARTOVERRIDE_COLLISION_CHECK_1`. Full details in
`infrastructure/state/items/MLIE_FAUNA_ABSORPTION_1.md`'s latest note and
`LESSONS_INBOX.md`.

## What the owner should see

- **`SHEET_ORPHAN_CONSUMPTION_1`'s audit found 5 things that need a real
  decision before the 2026-09-10 assignment sheet's remaining verdicts get
  applied** (`Transient/sheet_orphan_audit_2026-09-12.md` has the full
  table): `flora_move_mapping.md` names a target roster for AG_Gamma/
  AG_Septimum that is MEASURED FALSE (applying it as written would misfile
  or effectively delete 2 plants from the world); the two flora decision
  files disagree with each other on 14/288 rows and a prior item
  (`ART_REGEN_WAVE3_QUEUE_1`) wrongly asserted they were byte-identical;
  a future naive Law-1 sizeBin rescale would silently overwrite 29 of your
  own sheet rulings; the 118-row "new commission" art/def ledger has at
  least 9 slugs that are already-built defs, not new work; and a third
  instrument (`cast_assignment.csv`) still disagrees with the sheet's own
  6-creature fauna cut list, with a later card ruling that widens the cut
  further sitting behind a still-BLOCKED item. Nothing here was applied —
  it's audit-only, gated on these calls.
- Two live/shipped things may not be doing what they look like they do:
  `RUT_CathedralRoach`'s land-cleaning behavior is plausibly dead in the
  currently-running game (filed `CATHEDRAL_ROACH_THINKTREE_GAP_1` — a
  mechanoid think-tree limitation, not confirmed live yet, just a strong
  inference from the engine source), and `RUT_ScarRoach`/
  `RUT_CathedralRoach` both render magenta right now (missing texture
  files, filed `SCARROACH_CATHEDRALROACH_TEXTURES_MISSING_1`).
- The full Rust Cathedral kit (hum-mood, walls, roaches, living bolts,
  eel-fishing, deep-drill response — 6/6 sections) is now offline-complete
  but still shipped DISABLED in `ModsConfig.xml`, same as it's been all
  along — nothing changes for you until someone enables it and quicktests.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `SHEET_ORPHAN_CONSUMPTION_1` — audit done (steps 1-2 of its own spec), no
  writes made. `needs=owner` — see "What the owner should see" above for the
  5 calls it's waiting on. Next action once those land: run
  `apply_assignment_verdicts.py` for real, do the flora hand-edits, file the
  118-row ledger as a real art-queue, freeze both decisions files (spec
  steps 3-5).
- `ASHFALL_SPIRE_LANDMARK_1` — LandmarkDef+RulePackDef+icon authored and
  validated clean offline. `needs=bridge`. Next action: place it on tile
  4299 via `world_landmarks_set` (forcing past `IsValidTile`'s Impassable
  refusal, already understood, not a new problem) and read it back.
- `NINEFOLD_MISSING_EVENT_HOOKS_1` — `jawa/trade_execute` +
  `jawa/transporter_launch` companion tools built, 0 errors, not deployed
  (game was up all session). `needs=deploy`. Next action: deploy once the
  game is down, then a bridge session to trigger one trade + one launch and
  close the last 2/9 gods.
- `INHABITED_AUGMENTATION_BUILD_1` — 14/14 site archetypes now built AND
  wired (was 12/14 at the top of this window). `needs=bridge`. Next action:
  a placement pass once the bridge is free — which tile gets which
  archetype is a decision, not this pass's to invent.
- `RUST_CATHEDRAL_MECHANICS_1` — all 6 kit sections now offline-complete
  (was 2/6 at the top of this window: walls, roaches; added hum-mood,
  living bolts, eel-fishing, deep-drill response tonight). `needs=bridge`.
  Next action: enable the mod in `ModsConfig.xml` and quicktest all 6
  mechanics together — none of them have been live-verified yet.
- `MLIE_FAUNA_ABSORPTION_1` — 17 more Wave C species ported tonight (91 ->
  74 remaining): Anooba, Beldon, Bolotaur, Boma, Borcatu, CanCell, Cannok,
  Clodhopper, Convor, Corinathoth, Dactillion, Dalgo, Dianoga, Dragonsnake,
  Eopie (+2 more from the very first pass before tonight, Iriaz/Mudhorn,
  not part of this window's count). Always "half-done" until the worklist
  hits 0 — that's expected, not a trap. The one real trap is the art-override
  collision described above; everything else follows the established
  pipeline cleanly. Next action: keep porting from the front of
  `infrastructure/state/facts/mlie_wave_c_worklist.json`, 3 species at a
  time, checking the override-collision list first.

## Traps learned

All filed to `LESSONS_INBOX.md` tonight, summarized here:
- **The art-override collision** (see "one thing to carry forward" above) —
  the biggest one, own write-up there.
- Two background subagents this session ran a large batch of tool calls
  and then ended their OWN turn with "I'll wait for the monitor's
  notification" instead of finishing — no notification ever comes to a
  subagent. Had to inspect the actual working-tree diff directly both
  times to recover the real work rather than trust the subagent's final
  message; one of those two recoveries is where the art-override collision
  above was actually caught. Say "run validation in the foreground, never
  background it and wait" explicitly in any prompt dispatching a subagent
  that validates/builds.
- `.git/index.lock` contention recurred twice more tonight (shared tree
  with a concurrent BENCH session). One cleared in 5-10s on its own; one
  persisted 60+ seconds and was confirmed genuinely stale (`ps aux` on WSL
  AND `tasklist.exe` on Windows both showed no holder) before removing it —
  check both sides of the WSL/Windows boundary, a Windows-side `git.exe`
  is invisible to a WSL `ps aux`.
- Re-confirmed, not new: `JawaBench ready: MISSING` right after a fresh
  restart in `harvest_log.py`'s report is a false alarm (lazy init, fires
  on the first bridge tool call, not at assembly load) — don't chase it
  before checking whether any bridge call has happened yet in that log.
- A full post-restart `harvest_log.py` triage this session found 9 RED
  categories above baseline, and EVERY one of them was byte-identical to
  the previous load (`Player-prev.log`) — none were caused by tonight's
  belt-mode work. Worth remembering: a big RED count is not automatically
  a regression; diff against the previous log before assuming so.

## Closed since the last handoff (2)

- `VAPOR_PLACEMENT_CLEANUP_1` — 919d5c1556ed5cf2446d9252a25c3af4d7b5f310
- `PATCH_MAYREQUIRE_OPERATION_SWEEP_1` — 908ffd9df3721f771d206292b11dec6c254d672d

## Filed and still open (9) — the next seat's queue

- `SHEET_ORPHAN_CONSUMPTION_1` — Consume the 5 orphaned verdict channels of the 2026-09-10 assignment sheets (fauna out x6, flora move x15, flora out x4, 118-row NEW-ART/DEF ledger, f
- `BIOME_WORLD_SWITCH_WAVE_1` — World-switch every donor/vanilla-painted tile to its owned RUT_ successor: MEASURED 2026-09-12 live export, 17,889 of 21,872 tiles (82%) still on 23 d
- `CATHEDRAL_ROACH_THINKTREE_GAP_1` — RUT_CathedralRoach's EatCleanable think node likely never fires: BaseMechanoidWalker has no insertTag for the Animal_PreMain route mandrake.rm.creatur
- `UTINNI_WORLDMAP_FLIGHT_ICON_1` — Replace the gravship's world-map flight icon with a Utinni-specific sprite: vanilla WorldObjectDef Gravship draws World/WorldObjects/Expanding/Gravshi
- `GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1` — Giddy-Up's BuildAnimalBiomeCache throws 'same key already added: RSW_Iriaz' and skips its whole animal-biome cache. Root cause partially traced: RSW_I
- `MEGAFAUNAYIELD_DEAD_GR_TARGETS_1` — Doctrine's MegafaunaYield.xml patches GR_Elasmobearium/GR_Mantistanis (Genetic Rim ThingDefs) gated behind FindMod(Vanilla Genetics Expanded), but tho
- `SCARROACH_CATHEDRALROACH_TEXTURES_MISSING_1` — RUT_ScarRoach and RUT_CathedralRoach render magenta live right now - 'Failed to find any textures at Things/Pawn/Animal/RUT_ScarRoach/RUT_ScarRoach' (
- `FASCINATING_WORLD_JUNK_1` — Reskin and re-text every map-scatter wreck (tanks, trucks, cars, ancient junk) into Star Wars scavenger wreckage: census what exists and what spawns i
- `MLIE_ARTOVERRIDE_COLLISION_CHECK_1` — 6 species still in the MLIE Wave C worklist (Mynock, Kreetle, Horax, Fambaa, Zakkeg, Ronto) each have a dedicated mandrake.rsw.<name>artoverride mod s

## Commits

```
7908f1a0e rimflow: sync ledger/queue views, file MLIE_ARTOVERRIDE_COLLISION_CHECK_1
8dc279c64 MLIE_FAUNA_ABSORPTION_1: port Dianoga, Dragonsnake, Eopie (77 -> 74 remaining)
5a8fc8c1c Fix: remove RSW_Anooba art files that silently regressed the verified-live AnoobaArtOverride
9b0b9ff91 BENCH reboot handoff 202609121722: canonical START save registered, landing-fog fix shipped, three owner tickets filed
5fddd399d Transient: ModsConfig + Player.log backups from the GravshipLanding restart
352723f00 CANONICAL START SAVEGAME registered: CANONICAL_ASHKARR_START_2026-09-12.rws (owner, 2026-09-12)
92b256a75 File CAMPAIGN_STORY_SITTING_1: the formal campaign-story pass (owner, 2026-09-12)
47e332615 rimflow: close GRAVSHIP_LANDING_FOG_REVEAL_1
19d212ce8 GRAVSHIP_LANDING_FOG_REVEAL_1: proven live at 17007 (62500 -> 5465 fogged), close notes
a4671ea2e File FASCINATING_WORLD_JUNK_1: the scav-flavoured wreck reskin programme (owner, 2026-09-12)
997dc73c3 MLIE_FAUNA_ABSORPTION_1: port Corinathoth, Dactillion, Dalgo (80 -> 77 remaining)
37182c7a7 rimflow: file 3 items from post-restart Player.log triage (GiddyUp wildBiomes duplicate, dead MegafaunaYield GR_* targets, ScarRoach/CathedralRoach missing textures) - all pre-existing, none caused by tonight's belt-mode work
3a608276a MLIE_FAUNA_ABSORPTION_1: port Cannok, Clodhopper, Convor (83 -> 80 remaining)
6e92224b4 RimMandrake: Gravship Landing Reveal — unfog the outdoors on gravship-arrival maps before the landing picker (GRAVSHIP_LANDING_FOG_REVEAL_1)
95023f57f rimflow: sync ledger/queue views after belt-mode wave 4 (PATCH_MAYREQUIRE_OPERATION_SWEEP_1 closed)
4565d5796 Closes: PATCH_MAYREQUIRE_OPERATION_SWEEP_1
908ffd9df File GRAVSHIP_LANDING_FOG_REVEAL_1: landing picker fogged to one room (start-spot flood + NWN on non-colony maps)
c9bfed75a rimflow: sync ledger/queue views after belt-mode wave 3 (RUST_CATHEDRAL/PATCH_MAYREQUIRE filed+needs, code-review mark-clean wave)
c8b696e32 MLIE_FAUNA_ABSORPTION_1: port Boma, Borcatu, CanCell (86 -> 83 remaining)
2c9e20736 RUST_CATHEDRAL_MECHANICS_1: build §4 eel-fishing + §5 deep-drill response (6/6 sections offline-complete); file PATCH_MAYREQUIRE_OPERATION_SWEEP_1
8c4731b5e UTINNI_WORLDMAP_FLIGHT_ICON_1: record what the vanilla icon looks like in play (pale blue dome)
6749e2092 File UTINNI_WORLDMAP_FLIGHT_ICON_1: own the gravship's world-map flight icon (owner, 2026-09-12)
92b7ddef3 mark-clean: 4 fauna-wave files after diff-scoped review (BiomeCast_Ashkarr x2, RSW_Bantha_Thoughts, AnimalBiomeDuplicates_Fix)
1c0a5dcdb SHEET_ORPHAN_CONSUMPTION_1: addendum, 9 (not 5) confirmed already-built dupes in the 118-row ledger
af78ab87b Sea landmark cleanup (owner ruling 2026-09-12): shoreline-only, capped ~7% — 533 of 613 sea landmarks removed live, plan + replay script committed
1176b77a9 SHEET_ORPHAN_CONSUMPTION_1: audit table for 5 orphaned sheet-verdict channels, no writes
c88a886a9 RUST_CATHEDRAL_MECHANICS_1: build §3 living bolts (3/6 sections); file CATHEDRAL_ROACH_THINKTREE_GAP_1
678f0bdac File BIOME_WORLD_SWITCH_WAVE_1: 82% of tiles still on donor/vanilla biome defs (MEASURED live); the ownership wave closed on def authoring only
9808b920b INHABITED_AUGMENTATION_BUILD_1: wire 8.9 crashed_ship + 8.11 beast_lair (14/14 built+wired, 0/14 placed)
e62125946 MLIE_FAUNA_ABSORPTION_1: port Anooba, Beldon, Bolotaur (89 -> 86 remaining)
765cdb3f4 Gravship v2 'The Utinni' ring layout: owner's first size cut (booms removed), exported live 2026-09-12
ccdd2e1ba rimflow: sync ledger/queue views after belt-mode wave (VAPOR close, ASHFALL/NINEFOLD needs routing)
3469346f3 NINEFOLD_MISSING_EVENT_HOOKS_1: rimbridge-companion tools to trigger trade + launch
6e94a8845 ASHFALL_SPIRE_LANDMARK_1: author The Spire LandmarkDef, fixed-name RulePackDef, procedural icon
3af86502e Closes: VAPOR_PLACEMENT_CLEANUP_1
919d5c155 Plot sitting 2026-09-12: Ashfall campaign function ruled (the Key to the war lab), Archon name, Mechanoid-pass mechanics, sheet-orphan item
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-12T17:21:58Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 D infrastructure/artpipe/pending/dactillion_v1_east.json
 D infrastructure/artpipe/pending/dactillion_v1_north.json
 D infrastructure/artpipe/pending/dactillion_v1_south.json
 D infrastructure/artpipe/pending/fanback_v1_east.json
 D infrastructure/artpipe/pending/fanback_v1_north.json
 D infrastructure/artpipe/pending/fanback_v1_south.json
 D infrastructure/artpipe/pending/grank_v1_east.json
 D infrastructure/artpipe/pending/grank_v1_north.json
 D infrastructure/artpipe/pending/grank_v1_south.json
 M infrastructure/artpipe/registry.jsonl
 M infrastructure/artpipe/throughput.jsonl
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
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
?? infrastructure/artpipe/done/dactillion_v1_east.json
?? infrastructure/artpipe/done/dactillion_v1_east.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_north.json
?? infrastructure/artpipe/done/dactillion_v1_north.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_south.json
?? infrastructure/artpipe/done/dactillion_v1_south.manifest.json
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
?? infrastructure/artpipe/done/fanback_v1_east.json
?? infrastructure/artpipe/done/fanback_v1_east.manifest.json
?? infrastructure/artpipe/done/fanback_v1_north.json
?? infrastructure/artpipe/done/fanback_v1_north.manifest.json
?? infrastructure/artpipe/done/fanback_v1_south.json
?? infrastructure/artpipe/done/fanback_v1_south.manifest.json
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
?? infrastructure/artpipe/done/grank_v1_east.json
?? infrastructure/artpipe/done/grank_v1_east.manifest.json
?? infrastructure/artpipe/done/grank_v1_north.json
?? infrastructure/artpipe/done/grank_v1_north.manifest.json
?? infrastructure/artpipe/done/grank_v1_south.json
?? infrastructure/artpipe/done/grank_v1_south.manifest.json
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
?? infrastructure/artpipe/done/shiro_v1_east.json
?? infrastructure/artpipe/done/shiro_v1_east.manifest.json
?? infrastructure/artpipe/done/shiro_v1_north.json
?? infrastructure/artpipe/done/shiro_v1_north.manifest.json
?? infrastructure/artpipe/done/shiro_v1_south.json
?? infrastructure/artpipe/done/shiro_v1_south.manifest.json
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
?? infrastructure/artpipe/registry.jsonl.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml
```

