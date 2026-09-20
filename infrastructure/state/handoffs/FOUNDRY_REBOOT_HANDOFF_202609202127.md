# FOUNDRY_REBOOT_HANDOFF_202609202127 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609201828`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

`rimworld/spawn_thing` and the `Spawn Pawn...` debug action currently NPE on
EVERY pawn defName (vanilla Muffalo/Thrumbo/Chicken and our own RSW_Sketto all
confirmed) -- on both a reduced test tier AND the owner's real 618-mod list,
same dedup'd stack trace (`[Ref D3D588D]`) both times, inside
`VEF.Apparels.CompShieldField`'s `SpawnSetup` Harmony postfix. Non-pawn Things
spawn fine. **This breaks the standard `rimworld-debug-testing` "spawn many,
screenshot, observe" method project-wide** until `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1`
closes -- do not plan a quicktest pawn-spawn verification without checking that
item first. Also do not "fix" it by removing `sarg.alphaanimals`: tried and
ruled out this session, it breaks `ScenPart_StartingAnimal` instead (a
different NPE), because some of our own SWBestiary defs lean on an
Alpha-Animals-sourced parent/field.

## What the owner should see

- `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1` (see above) -- asked him mid-session to try
  a manual dev-mode "Spawn Pawn..." click himself, to tell us whether this is a
  bridge-only gap or hits his own manual play too. He had not answered before
  "handoff" arrived -- worth following up.
- He personally confirmed the vanilla flip-book flying animation (Chicken)
  works live, twice (his own two screenshots + a live sighting) -- that part
  of the "modern flapping flight" question is settled. Confirming it on one of
  OUR OWN creatures (`RSW_Sketto`, real flip-book frames already on disk) is
  what the spawn-crash bug blocked; not yet seen working on our own art.
- Mid-session he also told BENCH "Continue and take bridge" for
  `XENOTYPE_CANON_CORRECTION_1`'s skin-colour pass -- that is BENCH's thread,
  not reported on here.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `DESERT_PORT_PLACEHOLDER_ART_1` — 3 of 16 donor-texPath species rewired+deployed (already-rendered art found unused); remaining 13 (incl. `RSW_Dunegrass`, still visibly wrong) already queued under `DESERT_FAMILY_PORT_EXECUTION_1`, awaiting the daemon; NEXT: check `infrastructure/artpipe/registry.jsonl` for those 13 job_ids' `generated`/`validated` events, wire+deploy whichever have finished art, close once all 16 are real art.
- `EXTREME_DESERT_SIGNATURE_FLORA_1` — `RSW_LightPipeNub`/`RSW_Ollim`/`RSW_OllimWood` authored and wired into `RUT_ExtremeDesert`; art queued (`rslpn_v1`, `rswollim_v1`, `rswollimwood_v1`) but NOT yet rendered (item's own verify requires real art, so left open); NEXT: check `infrastructure/artpipe/done/` for those 3 job outputs, wire the resulting texPaths, take a contact-sheet screenshot, close.
- `PORTED_BEAST_MECHANICS_REBUILD_1` — BLOCKED (not a fresh claim -- C# already built/deployed by a prior session, 0 errors); NEXT: once `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1` closes, quicktest-spawn `RSW_Ferroclaw`/`RSW_Voltmaw`/`RSW_Cindermite` and confirm the 5 remaining criteria, then close.
- `DRUM_LURE_PREDATOR_BUILD_1` — BLOCKED (code+defs complete, built, deployed; a peer agent correctly declined to force-take the bridge from this window); NEXT: once `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1` closes, quicktest `RSW_Drazzik` (lure draw-in) + `RSW_DrazzikEggFertilized` (ambush hatch), then close.
- `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1` — filed this session, not yet worked; NEXT: get the owner's manual dev-mode spawn-click result (see "What the owner should see"), then decide whether this is a VEF regression to report upstream or something fixable in our own Harmony load order.

## Traps learned

- `rimworld/spawn_thing`/`Spawn Pawn...` NPE on every pawn right now (VEF `CompShieldField.SpawnSetup` postfix) — see "the one thing to carry forward" above (filed: LESSONS_INBOX, item: `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1`).
- Five `items/*.md` -> `items/closed/` moves were left as staged/unstaged deletions, uncommitted, by a concurrent-session git-mv race (same shape a peer agent hit and named earlier this session) — the closed/ copies were already correct; just finish the commit rather than re-investigating (see: commit `c3db844e4`).
- `handoff.py --check`'s own WHOSE-tag/TODO-marker gate has a known false-positive on the instructional line spelling out the literal marker, already worked around in this file's template (filed: LESSONS_INBOX).
- `git commit <paths>` stages the WORKTREE content at those paths, not a saved diff — three concurrent BELT agents editing the same `RUT_Desert.xml`/`RUT_ExtremeDesert.xml` this session each had their fix land in whichever commit happened first, and correctly cited the shared sha afterward rather than re-doing the edit (see: `pathspec-commit-takes-worktree-not-index` memory; matched live this session, no new finding).

## Closed since the last handoff (15)

- `PLANT_TOLERANCE_VERIFY_STALE_CLIMATE_KEYS_1` — a9222beead6e5bd2e2a01542d4113e017a226d2c
- `DESERT_FORAGEDFOOD_INERT_1` — ba753d6e1
- `DESERT_ROUND2_IMPORTS_UNLANDED_1` — dbf42c53f
- `BLODDLE_DUNE_SEA_EYE_TEST_1` — 5b57f0eeb8a63e9e2f51c65b926124a5894799a8
- `DESERT_DEF_HEADER_STALE_COUNTS_1` — dbf42c53f7b606e8830d66beb9608f778c105949
- `PAINTED_TILES_WITH_NO_CAST_1` — 0b8dca280
- `DESERT_SHADE_GRID_KEYSTONE_1` — 50c022770
- `PLANT_TOLERANCE_REGEN_AFTER_KEY_FIX_1` — 46ef96ae9
- `DESERT_SIGNATURE_FLORA_1` — a74a7a4fb
- `EXTREME_DESERT_GIANT_COMMENSALS_1` — 9120f45ab
- `EXTREME_DESERT_SUBSURFACE_PREDATOR_1` — 1a0c8969c
- `DESERT_BURST_PREDATOR_FLAGSHIP_1` — 1d9360a71a4a3ea473b9e253c68fad41b8fe6237
- `MYNOCK_FLIGHT_ART_FIRST_1` — c75ee26b8dabca8843cdd95b4728b4594a618e9a
- `EXTREME_DESERT_CAVERN_BEAST_1` — 684cbc2f2
- `AA_JOE_DESERT_PORT_BATCH_1` — b28d674ef

## Filed and still open (5) — the next seat's queue

- `DESERT_STAGGERSEED_BUILD_1` — Author the staggerseed cycle plant (corpse-dispersal + euphoric prepared-seed dish)
- `DESERT_SHADE_PLANTS_DESIGN_1` — Design pass: desert's defending shade plants (thorn/contact damage, no native CompProperties)
- `DRUM_LURE_PREDATOR_BUILD_1` — Drum-lure subsurface predator (vibration-lure ambush) + egg-trap clutch
- `ROSTER_VALIDATOR_STALE_REFS_1` — All 38 remaining roster-validator red errors are instrument staleness, not data defects - every flagged def resolves live; plant_pool.csv is from Aug 
- `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1` — rimworld/spawn_thing and Spawn Pawn... debug action NPE on ANY pawn spawn (VEF CompShieldField SpawnSetup postfix)

## Commits

```
740f4158b File BRIDGE_PAWN_SPAWN_CRASHES_VEF_1, block PORTED_BEAST_MECHANICS_REBUILD_1 on it
2aa93993b Owner skin rulings become data with a test; Umbaran ruled grey-blue
f50c9b682 Two items corrected: SWBestiary IS deployed, and step 2 of the xenotype sequence is done
427acdbae Canon colours re-verified against the live web; 3 library claims were wrong
4cdd1b5a9 rimflow: sync ledger (AA_JOE_DESERT_PORT_BATCH_1 close + concurrent appends)
b28d674ef AA_JOE_DESERT_PORT_BATCH_1: port AA_GreatDevourer/Groundrunner/MatureFleshbeast, wire JOE_Cephalope
b29056d11 BENCH handoff 202609202015: the wave where four instruments lied
cb934fa00 rimflow: sync ledger (owner rulings wave, validator fix, roster cuts)
941d63059 rimflow: claim/start/block DRUM_LURE_PREDATOR_BUILD_1 (live verification owed)
c2403b3f2 DRUM_LURE_PREDATOR_BUILD_1: the deep desert's drum-lure predator + egg-trap clutch
a46ca5b69 File ROSTER_VALIDATOR_STALE_REFS_1: 38 of the 43 remaining errors are false
bd69008f6 Roster validator: derive the painted-biome set from the world CSV, not a literal
4c4f342d5 rimflow: remove closed EXTREME_DESERT_CAVERN_BEAST_1 from items/ (moved to closed/)
efdcd4b2e rimflow: move EXTREME_DESERT_CAVERN_BEAST_1 prose to items/closed/
72e5f6631 rimflow: sync ledger (MYNOCK_FLIGHT_ART_FIRST_1 close + concurrent FOUNDRY activity)
370fedce5 rimflow: close MYNOCK_FLIGHT_ART_FIRST_1, move prose to items/closed/
ef4500918 SHEET_ORPHAN_CONSUMPTION_1: purge the 4 flora, owner ruling 2026-09-20
684cbc2f2 EXTREME_DESERT_CAVERN_BEAST_1: author the zakkro cave-beast and its water egg
c75ee26b8 RSW_Mynock: give it the flight stat, and correct a stale "no art" comment
b416de522 SHEET_ORPHAN_CONSUMPTION_1: apply 9 of the 15 approved flora moves
... 51 more: git log --oneline d7fd0c37f..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     skin-colour pass then the naked-races grid screenshot (XENOTYPE_CANON_CORRECTION_1 step 4); owner: 'Continue and take bridge', FOUNDRY idle 60min

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   resolved this session, committed c3db844e4 (closed/ copies already existed, tracked, clean -- just finished the interrupted git-mv)
MM Transient/codebase_health.json   automated health publisher (rimflow-triggered regen) -- not this session
 M Transient/codebase_health_artifact.html   automated health publisher (rimflow-triggered regen) -- not this session
 M deployed/config/ModsConfig.before-tier-pits.xml   pre-existing untracked test-tier backup from an earlier session -- not this session
A  infrastructure/artpipe/daemon_run_20260916_bench_restart.log   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kinrath_v1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kinrath_v1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kinrath_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kreetle_v1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kreetle_v1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kreetle_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/nuitae_a_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/nuitae_a_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/nuitae_b_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/nuitae_b_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/rut_agelesscap_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/rut_agelesscap_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/yumbulbs_a_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/yumbulbs_a_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/yumbulbs_b_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/done/yumbulbs_b_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/nysyllin_v1_r2.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/failed/orray_v3_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
A  infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_dewback_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_grmolebear_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_kreetle_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_megatardi_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_orray_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_rutcathedralroach_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_rutscarroach_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/facingrepair_wyyyschokk_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_scratches_p1.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_scratches_p2.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_scratches_p3.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_tally_p1.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_tally_p2.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_tally_p3.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_0.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_2.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_3.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_4.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_5.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_warn_p1.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/graffiti_warn_p2.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/offbiome_fulgurite_v3.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_east.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/rslpn_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/rswollim_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
 D infrastructure/artpipe/pending/rswollimwood_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/artpipe/registry.jsonl   artpipe daemon (autonomous, continuous output) -- not this session
MM infrastructure/artpipe/throughput.jsonl   artpipe daemon (autonomous, continuous output) -- not this session
 M infrastructure/dashboards/hub/data/health.json   automated health publisher (rimflow-triggered regen) -- not this session
 M infrastructure/state/CODE_REVIEW_STATUS.json   automated health publisher (rimflow-triggered regen) -- not this session
 M infrastructure/state/codebase_health_last.json   automated health publisher (rimflow-triggered regen) -- not this session
D  infrastructure/state/items/DESERT_BURST_PREDATOR_FLAGSHIP_1.md   resolved this session, committed c3db844e4 (closed/ copies already existed, tracked, clean -- just finished the interrupted git-mv)
D  infrastructure/state/items/DROID_TILES_SOURED_TERRAIN_1.md   resolved this session, committed c3db844e4 (closed/ copies already existed, tracked, clean -- just finished the interrupted git-mv)
 D infrastructure/state/items/MYCOID_COLOSSUS_ART_MISROUTE_1.md   resolved this session, committed c3db844e4 (closed/ copies already existed, tracked, clean -- just finished the interrupted git-mv)
D  infrastructure/state/items/RESEARCH_TRIO_RETIRE_1.md   resolved this session, committed c3db844e4 (closed/ copies already existed, tracked, clean -- just finished the interrupted git-mv)
D  infrastructure/state/items/TWILIGHT_DEEP_WATER_LAYER_1.md   resolved this session, committed c3db844e4 (closed/ copies already existed, tracked, clean -- just finished the interrupted git-mv)
 M infrastructure/state/queue/BENCH.md   auto-regenerated by rimflow render on any write -- not specifically this session
 M src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml   BENCH (concurrent session, XENOTYPE_CANON_CORRECTION_1, in progress)
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\claude-1000\\-mnt-d-Luke-dev-Rimworld\\84f9b274-abd5-4c73-81fd-7f936a8b3cc9\\scratchpad\\check_tile.py"   scratch/tmp path outside the repo tree -- not a real tracked file
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   scratch/tmp path outside the repo tree -- not a real tracked file
?? deployed/config/ModsConfig.before-tier-bridge.xml   pre-existing untracked test-tier backup from an earlier session -- not this session
?? deployed/config/ModsConfig.before-tier-diving.xml   pre-existing untracked test-tier backup from an earlier session -- not this session
?? deployed/config/ModsConfig.before-tier-fish.xml   this session (modset_builder.py --tier fish --apply, for the flight-animation live test)
?? deployed/config/ModsConfig.before-tier-oracle.xml   pre-existing untracked test-tier backup from an earlier session -- not this session
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   pre-existing untracked test-tier backup from an earlier session -- not this session
?? deployed/config/ModsConfig.before-tier-visibility.xml   pre-existing untracked test-tier backup from an earlier session -- not this session
?? deployed/config/ModsConfig.before-tier-warlab.xml   pre-existing untracked test-tier backup from an earlier session -- not this session
?? infrastructure/artpipe/active/desert_swaca_igitz_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/barbslinger_redesign_v1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/barbslinger_redesign_v1_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/barbslinger_redesign_v1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/barbslinger_redesign_v1_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/barbslinger_redesign_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/barbslinger_redesign_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_drinker_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_drinker_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_drinker_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_drinker_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_drinker_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_drinker_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_gembug_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_gembug_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_gembug_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_gembug_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_gembug_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_gembug_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_glowbulb_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_glowbulb_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_glowbulb_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_glowbulb_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_glowbulb_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_glowbulb_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_grabber_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_grabber_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_grabber_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_grabber_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_grabber_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_grabber_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_megapleura_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_megapleura_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_megapleura_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_megapleura_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_megapleura_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_megapleura_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_soulchime_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_soulchime_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_soulchime_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_soulchime_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_soulchime_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/deeps_soulchime_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_anooba_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_anooba_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_anooba_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_anooba_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_anooba_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_anooba_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_bantha_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_bantha_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_bantha_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_bantha_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_bantha_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_bantha_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_corinathoth_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_corinathoth_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_corinathoth_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_corinathoth_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_corinathoth_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_corinathoth_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_eopie_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_eopie_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_eopie_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_eopie_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_eopie_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_eopie_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gizka_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gizka_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gizka_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gizka_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gizka_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gizka_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gorg_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gorg_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gorg_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gorg_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gorg_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gorg_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gutkurr_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gutkurr_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gutkurr_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gutkurr_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gutkurr_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_gutkurr_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_hrumph_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_hrumph_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_hrumph_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_hrumph_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_hrumph_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/desert_swaca_hrumph_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_dewback_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_dewback_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_grmolebear_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_grmolebear_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_kreetle_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_kreetle_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_megatardi_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_megatardi_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_orray_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_orray_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_rutcathedralroach_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_rutcathedralroach_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_rutscarroach_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_rutscarroach_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_wyyyschokk_v1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/facingrepair_wyyyschokk_v1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_scratches_p1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_scratches_p1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_scratches_p2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_scratches_p2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_scratches_p3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_scratches_p3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_tally_p1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_tally_p1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_tally_p2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_tally_p2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_tally_p3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_tally_p3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_0.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_0.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_4.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_4.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_5.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_5.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_warn_p1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_warn_p1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_warn_p2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/graffiti_warn_p2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_fulgurite_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_fulgurite_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_fulgurite_v3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_fulgurite_v3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v3_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v3_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v3_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/offbiome_gualaar_v3_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_deep_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_deep_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_heavy_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_heavy_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_light_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_light_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_trace_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/pyrelands_ash_trace_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agarilux_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agarilux_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agariluxprime_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agariluxprime_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agariluxprime_v3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agariluxprime_v3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agelesscap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_agelesscap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_arpeau_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_arpeau_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_brightbell_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_brightbell_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_bryolux_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_bryolux_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_crimsoncap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_crimsoncap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_dewshrooms_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_dewshrooms_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_dribblingcap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_dribblingcap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_dulcisplant_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_dulcisplant_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_falsefruit_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_falsefruit_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_furnacecap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_furnacecap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_giantagarilux_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_giantagarilux_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_glowstool_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_glowstool_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_greylady_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_greylady_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_greylady_v3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_greylady_v3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_nogtyl_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_nogtyl_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_nuitae_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_nuitae_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_palemoss_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_palemoss_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_paletree_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_paletree_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_paletree_v3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_paletree_v3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_pusmelon_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_pusmelon_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_recurvedstropharia_v3.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_recurvedstropharia_v3.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_regenerantveil_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_regenerantveil_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_rustpuff_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_rustpuff_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_sagecrust_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_sagecrust_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_shinecap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_shinecap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_skulltop_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_skulltop_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_slimypholiota_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_slimypholiota_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_swarmling_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_swarmling_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_swarmling_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_swarmling_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_swarmling_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_swarmling_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_violetwimple_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_violetwimple_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpawn_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpawn_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpawn_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpawn_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpawn_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpawn_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpod_v2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpod_v2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpod_v2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpod_v2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpod_v2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wildpod_v2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_witchesoyster_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_witchesoyster_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wrinklecap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rot_wrinklecap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rslpn_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rslpn_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rswollim_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rswollim_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rswollimwood_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rswollimwood_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_agelesscap_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_agelesscap_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_falsefruit_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_falsefruit_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_1_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_1_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_1_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_1_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_1_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_1_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_2_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_2_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_2_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_2_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_2_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_2_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_3_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_3_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_3_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_3_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_3_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_3_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_4_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_4_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_4_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_4_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_4_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_4_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_5_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_5_east.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_5_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_5_north.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_5_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_firehawk_flying_5_south.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_furnacecap_plant_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_furnacecap_plant_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_gene_furnaceblood_icon_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_gene_furnaceblood_icon_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_grownfurnace_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_grownfurnace_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveingredient_agelesscap_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveingredient_agelesscap_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveingredient_euphoriccrown_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveingredient_euphoriccrown_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveingredient_regenerantveil_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveingredient_regenerantveil_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveprep_toxicinjection_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_liveprep_toxicinjection_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_livingfurnacecap_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_livingfurnacecap_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_palemoss_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_palemoss_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_paletree_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_paletree_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_regenerantveil_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_regenerantveil_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_mycoid_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_mycoid_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_nightwake_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_nightwake_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_quickflesh_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_quickflesh_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_sheenblood_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_symbiont_sheenblood_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_tea_agereversal_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_tea_agereversal_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_tea_bioregeneration_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_tea_bioregeneration_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_tea_pleasure_v1.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/done/rut_tea_pleasure_v1.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.manifest.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Ashworm_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Ashworm_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Ashworm_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Barbthorn_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Barbthorn_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Barbthorn_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Cindermite_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Cindermite_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Cindermite_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Dunegrass.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Dunestalker_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Dunestalker_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Dunestalker_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_EmberCarpet.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Ferroclaw_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Ferroclaw_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Ferroclaw_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandhorn_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandhorn_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandhorn_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandmaw_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandmaw_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandmaw_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandstrider_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandstrider_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sandstrider_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Scrubgrass.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Spinerat_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Spinerat_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Spinerat_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Spineroller_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Spineroller_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Spineroller_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sporemass_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sporemass_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sporemass_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sporepaw_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sporepaw_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Sporepaw_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Stareling_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Stareling_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Stareling_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Starvine.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Stoneback_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Stoneback_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Stoneback_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_SweetbarkTree.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Tuskcoil_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Tuskcoil_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Tuskcoil_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_VellaraBloom.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Voltmaw_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Voltmaw_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Voltmaw_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/RSW_Whirlbloom.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_igitz_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_igitz_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_iriaz_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_iriaz_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_iriaz_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_iridonianreek_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_iridonianreek_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_iridonianreek_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_jamel_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_jamel_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_jamel_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_jimvu_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_jimvu_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_jimvu_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_kreetle_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_kreetle_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_kreetle_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_kwi_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_kwi_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_kwi_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_kybuck_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_kybuck_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_kybuck_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_longtailgorg_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_longtailgorg_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_longtailgorg_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_lothcat_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_lothcat_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_lothcat_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_massiff_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_massiff_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_massiff_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_mudhorn_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_mudhorn_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_mudhorn_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_mynock_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_mynock_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_mynock_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_nuna_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_nuna_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_nuna_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_pufferpig_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_pufferpig_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_pufferpig_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_ronto_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_ronto_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_ronto_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_scavrat_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_scavrat_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_scavrat_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_scurrier_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_scurrier_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_scurrier_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_shyrack_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_shyrack_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_shyrack_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_skalder_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_skalder_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_skalder_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_sketto_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_sketto_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_sketto_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_urusai_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_urusai_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_urusai_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_womprat_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_womprat_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_womprat_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_worrt_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_worrt_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_worrt_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_wraid_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_wraid_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desert_swaca_wraid_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_bolotaur_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_bolotaur_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_bolotaur_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_cannok_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_cannok_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_cannok_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_clodhopper_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_clodhopper_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_clodhopper_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_convor_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_convor_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_convor_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_falumpaset_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_falumpaset_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_falumpaset_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_feralgrazer_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_feralgrazer_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_feralgrazer_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_feralnerf_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_feralnerf_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_feralnerf_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_graniteslug_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_graniteslug_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_graniteslug_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_grank_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_grank_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_grank_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_horax_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_horax_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_horax_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_jakobeast_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_jakobeast_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_jakobeast_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_krykna_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_krykna_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_krykna_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_nerf_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_nerf_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_nerf_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_pikobis_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_pikobis_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_pikobis_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_plant_bloddle.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_porg_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_porg_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_porg_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_qormot_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_qormot_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_qormot_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_runyip_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_runyip_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_runyip_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_shaak_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_shaak_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_shaak_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_strill_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_strill_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_strill_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_teemuss_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_teemuss_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_teemuss_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_uvak_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_uvak_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_uvak_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_varactyl_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_varactyl_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_varactyl_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_voorpak_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_voorpak_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_voorpak_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_vulptex_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_vulptex_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_vulptex_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_warwyrm_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_warwyrm_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_warwyrm_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_whisperbird_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_whisperbird_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_whisperbird_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_zeer_east.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_zeer_north.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/artpipe/pending/desertportb_zeer_south.json   artpipe daemon (autonomous, continuous output) -- not this session
?? infrastructure/state/.rimflow_conc_97j8px_9/   rimflow's own concurrency-lock scratch dir -- not a real edit
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing untracked backup from 2026-09-11 -- not this session
```

