# BENCH_REBOOT_HANDOFF_202609210000 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609202255`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

🔴 **A rule the owner keeps repeating is in the WRONG FILE, not stated too weakly.**

He said, for the third time: *"You have been told this before. Please record this
properly."* The rule — **the planet is painted once at the end, so one of our BiomeDefs
carrying 0 tiles is the EXPECTED state, not a defect** — was already written verbatim in
an agent memory file, complete with the Pyrelands as its worked example and his earlier
line *"You don't need to keep rediscovering this."*

It still failed, and the reason is mechanical: **a memory loads into ONE window's context
and no subagent ever sees it.** Four agents were briefed on biome work that day; not one
could read it. BENCH then filed `PYRELANDS_WRONG_BIOME_DEF_1` on the rediscovered finding
and reported it to him as a headline.

✅ Now in **`CLAUDE.md`** (`a03845d92`), which every window and every subagent reads.

🔑 **The general form, and the question to ask:** when a rule keeps being rediscovered,
do not write a better memory — move the rule to the artifact that the agents who break it
actually load. Ask *who held the wrong belief, and what do THEY read?*

## What the owner should see

- 🔴 **`BIOME_MOD_SPLIT_EXECUTION_1` is blocked on 10 questions that are his** (§7 of
  `design/RimMandrake/biome_mod_architecture.md`). Three change the most work:
  **the two deserts and the shrubland have no ruled names** (the spec's `RM_DeepDesert`
  / `RM_ShadowDesert` / `RM_FogShrubland` are the designer's inventions and are labelled
  as such); **`Scarlands` collides with a vanilla 1.6 biome name** and may be forced to
  rename; and **`RM_FE_Pyrelands` → `RM_Pyrelands`** is cheapest before the split, not
  after.
- ⏸️ **The Fall Line label is ready to apply and needs his eye, not his permission.**
  One field — `maxDrawSizeInTiles` 10 → 26 — then `world_commit` and a screenshot.
  🔑 The finding behind it is worth his attention on its own: **all 71 world features on
  the canonical save sit at `maxDrawSizeInTiles = 10`, the bottom of the engine's size
  curve**, so the 1,692-tile Dune Sea is lettered exactly as large as Notch. The planet
  has no visual hierarchy at all.
- ⚠️ **10 "contaminated" Contagion plants are parked on a plant-trait question**
  (`EXPLOSIVE_PLANT_GROWTH_1`): does burning one kill the charge, or throw spore chaff?
  The designer refused to invent it. It wants to become a plant trait.
- ⚠️ **`DESERT_FAMILY_PORT_EXECUTION_1` is the live retirement gate for 66 MEASURED
  identical-label donor twins** (both the donor's def and our `RSW_` def live at once,
  same label). RE-MEASURED 2026-09-20: its **defs are 85 of 109 done**, 11 rows remain
  unblocked and 12 need the owner. The real gap is **ART — 3 of 84 ported rows carry our
  own texPath; 81 still point at `swanimals/` and `AA_` donor paths.** There is still no
  retirement plan at all for `sarg.alphaanimals`.
  *(This line previously named `MLIE_FAUNA_ABSORPTION_1` as the stalled gate. That item is
  **done**, closed at `0d1313d99` — corrected 2026-09-20.)*

## What is half-done, and where it stops

- `BIOME_MOD_SPLIT_EXECUTION_1` — specified in full, **BLOCKED on his 10 answers**.
  NEXT: put §7 to him as cards; nothing else starts until Q2/Q3/Q5 are ruled.
- `FALL_LINE_MAJOR_REGION_LABEL_1` — offline half DONE and measured; **bridge is FREE and
  the game is DOWN**, so it is ready now.
  NEXT: load the CANONICAL world, one `world_features_set` (Fall Line
  `maxDrawSizeInTiles` → 26), `jawa/world_commit`, screenshot with **no dialog open**
  (an open dialog blanks the frame to black), then hand him the picture.
- `FOUNDERS_EXPORT_TO_REPO_1` — step 1 DONE at `ee8b70911`; 6 founders + 2 named colony
  animals are in the repo.
  NEXT: prove the round trip by re-importing into a throwaway colony. ⚠️ Needs the FULL
  617-mod list — the fragments reference defs across it and are not independently
  loadable.
- `PORTED_BEAST_MECHANICS_REBUILD_1` (FOUNDRY's) — criteria 2 and 3 **CONFIRMED LIVE** by
  FOUNDRY (ferroclaw ate steel, 75 → 60, exactly 1/5). Criteria 4–6 blocked on a real
  capability gap, now filed as `BRIDGE_SELECT_NONCOLONIST_PAWN_1`.
  NEXT: that item — a companion `[Tool]` that selects/drives a non-colonist pawn. ⚠️ A
  companion DLL cannot be written while RimWorld runs; it lands in a shutdown window.
- `TITANOSLIME_SLIME_BIOME_1` — his fresh ask (devour-whole, grows-as-it-eats), design
  started, not finished.
  NEXT: answer his actual question — *can a creature get larger as it eats?* — against
  the engine, then design to that answer rather than around it.
- `STALE_VIVIFIED_WORLDMAP_CITED_1` — filed, untouched.
  NEXT: reconcile `fall_line.md` to the canonical worldmap's names. ⚠️ **With him** — a
  biome sheet's names are a worldmap-doc pass, not a solo edit.

## Traps learned

- 🔴 **`world/ASHKARR_WORLDMAP_tiles.csv` is a RECORD exported from the savegame
  (2026-09-12), not the planet.** Its own freeze stamp says so — *"It is a RECORD of the
  planet, not a rival to it"* — and adds the lesson already paid for once: *"any future
  live-vs-CSV validate must state which direction it is evidence for."* BENCH read it as
  the live state and reported a false finding to the owner. A live read on 2026-09-19
  contradicts it outright about the Pyrelands. ⛔ Never call a CSV-derived tile count
  MEASURED about the live world. (see: `CLAUDE.md`, "A BIOME WITH ZERO TILES IS NOT A DEFECT", `a03845d92`)
- 🔴 **A subagent inherits none of your memory.** Everything a briefed agent must not get
  wrong has to be IN THE BRIEF or in `CLAUDE.md`. Two agents this session were sent
  corrections mid-run because the brief carried a BENCH error (`Lantern Deeps is
  RUT_PropaneLake` — it is not; and it *does* have our own def, `RUT_LanternDeeps`,
  178 lines, live). (filed: LESSONS_INBOX.md 2026-09-20)
- 🔴 **A `workerClass` is inert on this world.** `BiomeDef.Worker.GetScore` is called only
  from `WorldGenStep_Terrain` (MEASURED, RimSage), and there is no worldgen. That is why
  `RM_FE_Pyrelands` was built well and reached nobody. (filed: LESSONS_INBOX.md 2026-09-20; see: `infrastructure/state/items/BIOME_MOD_SPLIT_EXECUTION_1.md`)
- ⚠️ **Check for art already generated AND already ruled on before queueing a regen.**
  `PYRELANDS_SOUTH_TOPDOWN_REGEN_1` was one step from three fresh jobs that would have
  discarded the owner's 2026-09-17 "Yes". The three deployed PNGs were byte-identical to
  the repo. The rule earned its keep on its first outing. (see: `CLAUDE.md`, "Check for existing regenerated art before queuing more")
- ⚠️ **`git commit <path>` fails on a file git does not track yet** — "did not match any
  file(s) known to git". Stage it first, then commit by explicit path. (filed: LESSONS_INBOX.md 2026-09-20)
- ⚠️ **zsh does not word-split unquoted variables.** Putting a tool's path in a variable
  and expecting it to split gives "no such file or directory" with the whole string as
  the name. (filed: LESSONS_INBOX.md 2026-09-20)
- ⚠️ **`rimflow unblock` refuses another seat's in-flight item** and tells you the right
  move: correct the false prose in their item file and commit it. Use `note` to nudge. (filed: LESSONS_INBOX.md 2026-09-20)

## Closed since the last handoff (3)

- `DESERT_TABLES_DEPLOYED_AHEAD_OF_SPECIES_1` — 22abdbd8d7b5f4a3728c4c0b87a554f611563e4f
- `PYRELANDS_SOUTH_TOPDOWN_REGEN_1` — a356ca4efa93e275fdf31fcb91bf56cd5f2ddd01
- `PYRELANDS_WRONG_BIOME_DEF_1` — 41700160fab3a8ea715cb8e700945961ed4c2633

## Filed and still open (6) — the next seat's queue

- `TITANOSLIME_SLIME_BIOME_1` — Owner ask: a Titanoslime for RUT_Slime, devour-whole + grows-as-it-eats
- `STALE_VIVIFIED_WORLDMAP_CITED_1` — design/Jawa/worldbuilding/biomes/fall_line.md and other biome docs cite ASHKARR_VIVIFIED_2026-08-24_tiles.csv, which is a pre-rename artifact: it disa
- `FALL_LINE_MAJOR_REGION_LABEL_1` — Owner directive 2026-09-20: make the Fall Line a major world region with a beautiful clear label - all 71 Ash'karr world features sit at maxDrawSizeIn
- `BIOME_PAINT_ONCE_AT_THE_END_1` — Owner ruling 2026-09-20: the worldmap is painted ONCE, after every biome is its own RimMandrake mod - no per-biome repaint, no work gated on a tile co
- `BRIDGE_SELECT_NONCOLONIST_PAWN_1` — rimworld/select_pawn and ToolMapForPawns both REFUSE a non-colonist pawn, so no wild or hostile creature's ability can be fired on demand - the sole b
- `BIOME_MOD_SPLIT_EXECUTION_1` — Execute the biome mod split: 27 painted BiomeDefs into 26 RimMandrake mods per design/RimMandrake/biome_mod_architecture.md - BLOCKED on 10 owner ques

## Commits

```
2a65dbc20 BIOME_MOD_SPLIT_EXECUTION_1: the split is specified and blocked on 10 owner questions
5c4c78b91 Biome mod architecture: 27 painted defs to 26 RimMandrake mods, paint once at the end
558de037a Lesson: a rule that keeps being rediscovered is in the wrong FILE
a03845d92 A biome with zero tiles is not a defect: put the owner's ruling where agents read it
deaed4580 FOUNDRY reboot handoff 2026-09-20 2354
41700160f BIOME_PAINT_ONCE_AT_THE_END_1: owner rules the planet is painted once, at the end
e07eca2d0 PYRELANDS_WRONG_BIOME_DEF_1: put the ash storm on our own def, not the donor's
dd11b99f8 rimflow sync: bridge release after live verification session
9f153e8fd rimflow sync: close BRIDGE_PAWN_SPAWN_CRASHES_VEF_1 + DRUM_LURE_PREDATOR_BUILD_1, re-block PORTED_BEAST_MECHANICS_REBUILD_1
eaf288a21 Live bridge re-verify: VEF crash fix holds, drum-lure mechanics confirmed, ferroclaw eating confirmed
0298fddbd Biome work triage: what is workable with no game and no bridge
f738b745a ledger: TITANOSLIME_SLIME_BIOME_1 claimed and started (BENCH, design pass)
dd1adf4f6 TITANOSLIME_SLIME_BIOME_1: design spec for the Titanoslime (RM_GelatinousSlime apex)
78b63a979 DONOR_DEFS_PORT_TO_OURS_1: census the 66 live donor/port label twins
556403f99 READ_LINE_REGISTRY_SHARED_1: shared read-line ids get a registry and a lint
f53094e0b rimflow: close SHEET_ORPHAN_CONSUMPTION_1 at 3c57dff4a
04a0b78c9 FALL_LINE_MAJOR_REGION_LABEL_1: why no Ash'karr label reads as major, and the fix
3c57dff4a SHEET_ORPHAN_CONSUMPTION_1: apply the 12 sizeBin grading corrections, resolve the dusk-rat register conflict, freeze both decisions files
9ee72eb02 STALE_VIVIFIED_WORLDMAP_CITED_1: file the stale-worldmap citation defect
4f8f16a2e FALL_LINE_ARRIVAL_MECHANISM_1: the arrival spec, with the region name corrected
... 9 more: git log --oneline 69e99a9f2..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-20T23:52:32Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   — code_review_status.py's health publisher — regenerated on every prune/list; not a seat's
MM Transient/codebase_health.json   — code_review_status.py's health publisher — regenerated on every prune/list; not a seat's
 M Transient/codebase_health_artifact.html   — code_review_status.py's health publisher — regenerated on every prune/list; not a seat's
 M deployed/config/ModsConfig.before-tier-pits.xml   — modset_builder.py tier backup — FOUNDRY's live-test tooling, left untouched
 M design/Jawa/fauna/cast_assignment.csv   — another window — left untouched deliberately
A  infrastructure/artpipe/daemon_run_20260916_bench_restart.log   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kinrath_v1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kinrath_v1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kinrath_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kreetle_v1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kreetle_v1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kreetle_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/nuitae_a_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/nuitae_a_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/nuitae_b_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/nuitae_b_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/rut_agelesscap_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/rut_agelesscap_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/yumbulbs_a_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/yumbulbs_a_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/yumbulbs_b_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/done/yumbulbs_b_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/nysyllin_v1_r2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/failed/orray_v3_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
A  infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_dewback_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_grmolebear_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_kreetle_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_megatardi_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_orray_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_rutcathedralroach_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_rutscarroach_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/facingrepair_wyyyschokk_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_scratches_p1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_scratches_p2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_scratches_p3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_tally_p1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_tally_p2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_tally_p3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_0.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_4.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_5.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_warn_p1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/graffiti_warn_p2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/offbiome_fulgurite_v3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/rslpn_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/rswollim_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 D infrastructure/artpipe/pending/rswollimwood_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/pending/xeno_head_lasat_v1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/pending/xeno_head_lasat_v1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/pending/xeno_head_lasat_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/pending/xeno_head_mimbanese_v1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/pending/xeno_head_mimbanese_v1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/pending/xeno_head_mimbanese_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/pending/xeno_head_nelvaanian_v1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/pending/xeno_head_nelvaanian_v1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/pending/xeno_head_nelvaanian_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/pending/xeno_head_ortolan_v1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/pending/xeno_head_ortolan_v1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/pending/xeno_head_ortolan_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/artpipe/registry.jsonl   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
MM infrastructure/artpipe/throughput.jsonl   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
 M infrastructure/dashboards/hub/data/health.json   — another window — left untouched deliberately
 M infrastructure/state/ledger/events.jsonl   — another window — left untouched deliberately
 M infrastructure/state/queue/BENCH.md   — another window — left untouched deliberately
 M infrastructure/state/queue/FOUNDRY.md   — another window — left untouched deliberately
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\claude-1000\\-mnt-d-Luke-dev-Rimworld\\84f9b274-abd5-4c73-81fd-7f936a8b3cc9\\scratchpad\\check_tile.py"   — another window — left untouched deliberately
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   — another window — left untouched deliberately
?? deployed/config/ModsConfig.before-tier-beastmechanics.xml   — modset_builder.py tier backup — FOUNDRY's live-test tooling, left untouched
?? deployed/config/ModsConfig.before-tier-bridge.xml   — modset_builder.py tier backup — FOUNDRY's live-test tooling, left untouched
?? deployed/config/ModsConfig.before-tier-diving.xml   — modset_builder.py tier backup — FOUNDRY's live-test tooling, left untouched
?? deployed/config/ModsConfig.before-tier-fish.xml   — modset_builder.py tier backup — FOUNDRY's live-test tooling, left untouched
?? deployed/config/ModsConfig.before-tier-oracle.xml   — modset_builder.py tier backup — FOUNDRY's live-test tooling, left untouched
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   — modset_builder.py tier backup — FOUNDRY's live-test tooling, left untouched
?? deployed/config/ModsConfig.before-tier-visibility.xml   — modset_builder.py tier backup — FOUNDRY's live-test tooling, left untouched
?? deployed/config/ModsConfig.before-tier-warlab.xml   — modset_builder.py tier backup — FOUNDRY's live-test tooling, left untouched
?? deployed/config/ModsConfig.before-tier-xenotypes.xml   — modset_builder.py tier backup — FOUNDRY's live-test tooling, left untouched
?? infrastructure/artpipe/done/barbslinger_redesign_v1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/barbslinger_redesign_v1_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/barbslinger_redesign_v1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/barbslinger_redesign_v1_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/barbslinger_redesign_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/barbslinger_redesign_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_drinker_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_drinker_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_drinker_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_drinker_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_drinker_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_drinker_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_gembug_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_gembug_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_gembug_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_gembug_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_gembug_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_gembug_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_glowbulb_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_glowbulb_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_glowbulb_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_glowbulb_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_glowbulb_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_glowbulb_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_grabber_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_grabber_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_grabber_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_grabber_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_grabber_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_grabber_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_megapleura_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_megapleura_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_megapleura_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_megapleura_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_megapleura_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_megapleura_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_soulchime_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_soulchime_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_soulchime_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_soulchime_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_soulchime_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/deeps_soulchime_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_anooba_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_anooba_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_anooba_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_anooba_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_anooba_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_anooba_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_bantha_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_bantha_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_bantha_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_bantha_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_bantha_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_bantha_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_corinathoth_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_corinathoth_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_corinathoth_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_corinathoth_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_corinathoth_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_corinathoth_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_eopie_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_eopie_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_eopie_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_eopie_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_eopie_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_eopie_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_frilledgorg_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gizka_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gizka_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gizka_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gizka_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gizka_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gizka_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gorg_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gorg_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gorg_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gorg_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gorg_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gorg_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gutkurr_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gutkurr_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gutkurr_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gutkurr_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gutkurr_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_gutkurr_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_hrumph_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_hrumph_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_hrumph_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_hrumph_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_hrumph_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_hrumph_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_igitz_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_igitz_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_igitz_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_igitz_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_igitz_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_igitz_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iriaz_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iriaz_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iriaz_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iriaz_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iriaz_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iriaz_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_iridonianreek_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jamel_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jamel_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jamel_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jamel_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jamel_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jamel_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jimvu_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jimvu_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jimvu_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jimvu_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jimvu_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_jimvu_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kreetle_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kreetle_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kreetle_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kreetle_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kreetle_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kreetle_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kwi_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kwi_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kwi_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kwi_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kwi_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kwi_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kybuck_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kybuck_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kybuck_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_kybuck_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_longtailgorg_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_lothcat_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_lothcat_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_lothcat_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_lothcat_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_lothcat_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_lothcat_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_massiff_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_massiff_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_massiff_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_massiff_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_massiff_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_massiff_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mudhorn_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mudhorn_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mudhorn_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mudhorn_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mudhorn_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mudhorn_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mynock_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mynock_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mynock_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mynock_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mynock_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_mynock_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_nuna_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_nuna_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_nuna_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_nuna_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_nuna_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_nuna_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_pufferpig_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_pufferpig_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_pufferpig_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_pufferpig_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_pufferpig_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/desert_swaca_pufferpig_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_dewback_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_dewback_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_grmolebear_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_grmolebear_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_kreetle_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_kreetle_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_megatardi_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_megatardi_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_orray_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_orray_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_rutcathedralroach_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_rutcathedralroach_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_rutscarroach_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_rutscarroach_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_wyyyschokk_v1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/facingrepair_wyyyschokk_v1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_scratches_p1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_scratches_p1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_scratches_p2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_scratches_p2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_scratches_p3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_scratches_p3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_tally_p1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_tally_p1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_tally_p2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_tally_p2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_tally_p3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_tally_p3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_0.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_0.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_4.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_4.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_5.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_5.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_warn_p1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_warn_p1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_warn_p2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/graffiti_warn_p2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_fulgurite_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_fulgurite_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_fulgurite_v3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_fulgurite_v3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v3_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v3_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v3_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/offbiome_gualaar_v3_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_deep_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_deep_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_heavy_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_heavy_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_light_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_light_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_trace_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/pyrelands_ash_trace_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agarilux_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agarilux_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agariluxprime_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agariluxprime_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agariluxprime_v3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agariluxprime_v3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agelesscap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_agelesscap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_arpeau_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_arpeau_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_brightbell_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_brightbell_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_bryolux_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_bryolux_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_crimsoncap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_crimsoncap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_dewshrooms_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_dewshrooms_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_dribblingcap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_dribblingcap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_dulcisplant_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_dulcisplant_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_falsefruit_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_falsefruit_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_furnacecap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_furnacecap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_giantagarilux_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_giantagarilux_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_glowstool_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_glowstool_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_greylady_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_greylady_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_greylady_v3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_greylady_v3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_nogtyl_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_nogtyl_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_nuitae_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_nuitae_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_palemoss_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_palemoss_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_paletree_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_paletree_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_paletree_v3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_paletree_v3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_pusmelon_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_pusmelon_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_recurvedstropharia_v3.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_recurvedstropharia_v3.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_regenerantveil_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_regenerantveil_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_rustpuff_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_rustpuff_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_sagecrust_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_sagecrust_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_shinecap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_shinecap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_skulltop_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_skulltop_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_slimypholiota_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_slimypholiota_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_swarmling_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_swarmling_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_swarmling_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_swarmling_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_swarmling_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_swarmling_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_violetwimple_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_violetwimple_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpawn_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpawn_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpawn_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpawn_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpawn_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpawn_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpod_v2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpod_v2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpod_v2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpod_v2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpod_v2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wildpod_v2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_witchesoyster_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_witchesoyster_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wrinklecap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rot_wrinklecap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rslpn_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rslpn_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rswollim_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rswollim_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rswollimwood_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rswollimwood_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_agelesscap_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_agelesscap_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_falsefruit_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_falsefruit_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_1_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_1_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_1_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_1_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_1_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_1_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_2_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_2_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_2_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_2_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_2_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_2_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_3_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_3_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_3_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_3_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_3_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_3_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_4_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_4_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_4_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_4_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_4_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_4_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_5_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_5_east.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_5_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_5_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_5_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_firehawk_flying_5_south.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_furnacecap_plant_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_furnacecap_plant_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_gene_furnaceblood_icon_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_gene_furnaceblood_icon_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_grownfurnace_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_grownfurnace_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveingredient_agelesscap_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveingredient_agelesscap_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveingredient_euphoriccrown_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveingredient_euphoriccrown_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveingredient_regenerantveil_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveingredient_regenerantveil_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveprep_toxicinjection_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_liveprep_toxicinjection_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_livingfurnacecap_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_livingfurnacecap_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_palemoss_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_palemoss_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_paletree_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_paletree_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_regenerantveil_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_regenerantveil_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_mycoid_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_mycoid_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_nightwake_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_nightwake_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_quickflesh_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_quickflesh_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_sheenblood_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_symbiont_sheenblood_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_tea_agereversal_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_tea_agereversal_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_tea_bioregeneration_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_tea_bioregeneration_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_tea_pleasure_v1.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/done/rut_tea_pleasure_v1.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/failed/desert_swaca_kybuck_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/failed/desert_swaca_kybuck_north.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.manifest.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Ashworm_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Ashworm_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Ashworm_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Barbthorn_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Barbthorn_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Barbthorn_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Cindermite_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Cindermite_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Cindermite_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Dunegrass.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Dunestalker_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Dunestalker_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Dunestalker_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_EmberCarpet.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Ferroclaw_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Ferroclaw_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Ferroclaw_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandhorn_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandhorn_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandhorn_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandmaw_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandmaw_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandmaw_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandstrider_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandstrider_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sandstrider_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Scrubgrass.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Spinerat_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Spinerat_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Spinerat_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Spineroller_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Spineroller_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Spineroller_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sporemass_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sporemass_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sporemass_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sporepaw_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sporepaw_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Sporepaw_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Stareling_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Stareling_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Stareling_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Starvine.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Stoneback_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Stoneback_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Stoneback_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_SweetbarkTree.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Tuskcoil_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Tuskcoil_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Tuskcoil_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_VellaraBloom.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Voltmaw_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Voltmaw_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Voltmaw_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/RSW_Whirlbloom.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_ronto_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_ronto_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_ronto_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_scavrat_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_scavrat_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_scavrat_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_scurrier_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_scurrier_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_scurrier_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_shyrack_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_shyrack_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_shyrack_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_skalder_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_skalder_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_skalder_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_sketto_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_sketto_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_sketto_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_urusai_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_urusai_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_urusai_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_womprat_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_womprat_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_womprat_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_worrt_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_worrt_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_worrt_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_wraid_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_wraid_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desert_swaca_wraid_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_bolotaur_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_bolotaur_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_bolotaur_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_cannok_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_cannok_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_cannok_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_clodhopper_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_clodhopper_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_clodhopper_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_convor_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_convor_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_convor_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_falumpaset_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_falumpaset_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_falumpaset_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_feralgrazer_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_feralgrazer_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_feralgrazer_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_feralnerf_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_feralnerf_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_feralnerf_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_graniteslug_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_graniteslug_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_graniteslug_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_grank_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_grank_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_grank_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_horax_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_horax_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_horax_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_jakobeast_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_jakobeast_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_jakobeast_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_krykna_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_krykna_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_krykna_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_nerf_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_nerf_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_nerf_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_pikobis_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_pikobis_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_pikobis_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_plant_bloddle.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_porg_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_porg_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_porg_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_qormot_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_qormot_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_qormot_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_runyip_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_runyip_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_runyip_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_shaak_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_shaak_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_shaak_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_strill_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_strill_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_strill_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_teemuss_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_teemuss_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_teemuss_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_uvak_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_uvak_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_uvak_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_varactyl_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_varactyl_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_varactyl_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_voorpak_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_voorpak_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_voorpak_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_vulptex_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_vulptex_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_vulptex_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_warwyrm_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_warwyrm_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_warwyrm_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_whisperbird_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_whisperbird_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_whisperbird_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_zeer_east.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_zeer_north.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/artpipe/pending/desertportb_zeer_south.json   — artpipe daemon (live, pid 605) — continuous output, NOT a seat's; never hand-commit
?? infrastructure/state/.rimflow_conc_97j8px_9/   — another window — left untouched deliberately
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   — another window — left untouched deliberately
```

