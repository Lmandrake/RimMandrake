# BENCH_REBOOT_HANDOFF_202610042057 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610030757`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Art versions were racing, and the art ledger now exists to stop it. Never write a texture except through `art install` (design `design/RimMandrake/art_ledger_design_2026-10-04.md`; snapshot of every PNG in `D:\Luke\dev\_artstore`, tag `art-snapshot-2026-10-04`). The owner's art rulings live in `infrastructure/state/art_rulings/`. Every art review sheet shows canon references beside each row (CLAUDE.md, 2026-10-04). The commit-blocking guard is NOT built yet; until it is, any hand-copy can still overwrite kept art.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. **Desert sitting 1 is 101 of 102 rows decided** (`Transient/desert_sitting1_2026-10-04.decisions.json`, snapshot `2b7fc48c4`), and nothing is applied yet. Its sheet predates the 2026-10-04 canon gap-fill, so its rows lack the new canon images.
2. **Nuna B is installed in the repo but the game still shows the old copy** until FOUNDRY redeploys SWBestiary with prune.
3. **16 canon-briefed redo jobs** (bantha bull and cow, dalgo, eopie, iriaz) are rendering and will come back to him on a sheet.
4. **116 creatures matched no wiki page by name.** Re-check them by description before calling them invented (`CANON_ENTRY_BRIEFS_OWED_1`).
5. Mirror-light visibility in Solar Mirrors needs a live look with him present.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `ART_VERSION_WRANGLING_1` — desert sitting 1 decided (101/102); NEXT: ingest `Transient/desert_sitting1_2026-10-04.decisions.json` into the art ledger, `art install` the keeps, run the purges, queue the redos with canon briefs, and show him the result.
- `ART_VERSION_WRANGLING_1` — ledger phases 0-2 built (`79f4d9e44`); NEXT: rewire the art writers (artpipe collect, port_fauna, per-mod scripts, deploy) through `art install`, then build the commit-blocking guard he ruled for.
- `DESERT_FAMILY_PORT_EXECUTION_1` — held, no desertport render may be wired; NEXT: build desert sitting 2 (deep desert, 13 rows) from `Transient/desert_sittings_plan_2026-10-04.md` with canon images, and serve it to him.
- `CANON_ENTRY_BRIEFS_OWED_1` — 62 new canon entries have images only; NEXT: write each entry's visual brief and Must-show list, and re-check the 116 unmatched by description.
- `GIT_WORKFLOW_MIGRATION_1` — waiting on its date; NEXT: on 2026-10-05, measure manual rebases per day and Claude writes to D:\ over 3 days, record them in the plan's section 4, and close it.
- `UTINNI_DISCOVERY_ACHIEVEMENTS_1` — with FOUNDRY; NEXT: hold the writing sitting on its 24 texts once FOUNDRY's live run is green.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A sheet's "current art" taken from a def's last texture path shows the corpse texture (filed: lessons).
- `--owner-said` was refused for text he typed into a card's free text, so record it as typed in the note instead (filed: lessons).
- Art jobs render within minutes; fix the template before queueing, because pulling them afterwards is too late (filed: lessons).
- `rimflow close --sha HEAD` records the literal string "HEAD" (see: the correction note on ARIDSHRUBLAND_SHIPPING_NAMES_1).
- `pkill -f <pattern>` killed this shell again (see: memory pkill-f-matches-my-own-shell).

## Closed since the last handoff (3)

- `DROID_CANON_LIBRARY_1` — eb24acd1c
- `PROPANE_LANDS_RENAME_1` — 0287b61d0
- `ARIDSHRUBLAND_SHIPPING_NAMES_1` — HEAD

## Filed and still open (12) — the next seat's queue

- `STARWARS_JUNK_RESKIN_1` — Reskin vanilla ancient junk (cars, tanks, walkers, dropships) as Star-Wars-adjacent wrecks: Graphic_Random folders of many variants, patch in mandrake
- `BIOME_VISUAL_BEDAZZLE_PASS_1` — Visual bedazzle pass on every biome (ground, colour, density), AFTER all biomes are green-code, art-complete, in the single biome mod, with basic Nort
- `WEEPINGSTONES_NET_TARGET_FLEES_1` — Weeping Stones NET: wild skarrin outruns the handler and leaves the map before the 200-tick net finishes - how should capture work?
- `ROT_NAVIGATOR_CAMPAIGN_TILES_1` — Swallowed Navigator campaign tiles: name the carrier's Rot tile and the log's salvage-site tiles, then patch
- `FLOWWORKS_QUARRY_DIGGING_1` — Design pass: extend FlowWorks with the quarry concept - digging a canal can uncover local materials (local biome availability by default, configurable
- `NONSW_XENOTYPES_SCOPE_1` — Owner: the cut-the-twelve ruling says only Star Wars xenotypes belong, but the load has 32 more non-SW XenotypeDefs (AlphaGenes 15, Phytokin 3, det.* 
- `SANGUOPHAGE_KEPT_UNREACHABLE_1` — Owner card: Sanguophage cannot be deleted (XenotypeDefOf binding) - keep the def but make it unreachable (suppress Sanguophages faction, Sanguophage s
- `ART_VERSION_WRANGLING_1` — Art wrangling: find every art variant per creature (artpipe, review sheets, deployed, git history, donor), what is live and why, what replaced what, a
- `SOLAR_MIRRORS_MOD_DESIGN_1` — Design pass: Solar Mirrors, a RimMandrake mod (heliostats, static mirrors) that edits the shade/light map; feasibility in the 1.6 engine by Claude and
- `JAWABENCH_DLL_STALE_REBUILD_1` — Rebuild/deploy the JawaBench companion DLL: deployed build is 2026-10-02 05:37 and lacks 8 tools added since (jawa/flowworks_pulse, jawa/static_call, 
- `SELFTEST_RUNNER_SILENT_OOM_1` — run_selftests.py: three patch selftests (StarWars/Utinni/Mandrake) pass alone but fail or get OOM-killed (rc=137) in the parallel run, and the runner 
- `CANON_ENTRY_BRIEFS_OWED_1` — Write the visual brief + Must-show list for the 62 canon library creature entries created 2026-10-04 with images only (gorg and longtail gorg done); a

## Commits

```
fcc232235 ledger: file CANON_ENTRY_BRIEFS_OWED_1
269147275 canon library: gap-fill batch 2 (M-Z creatures), ysalamiri/reek aliases, index, art ledger canon images
fc8cb90b5 canon library: gorg as a multi-look species + gap-fill batch 1 (B-M creatures)
ea1b92de1 canon library: gorg + longtail gorg entries; canon_gapfill.py sweep tool
1d091110e MessyConduit matrix: --no-shots, --sweep-shots, per-phase timing, async PNG copy, faster polls
805138e09 MessyConduit aerial save-load: poll for anchors after load (first read raced, state was intact)
89b5fc140 ledger: ART_VERSION_WRANGLING_1 desert sitting 1 note
ba2983e43 ART_VERSION_WRANGLING_1: desert sitting 1 sheet + biome split for sittings 2-3
a5befe450 ledger: file JAWABENCH_DLL_STALE_REBUILD_1, SELFTEST_RUNNER_SILENT_OOM_1
aa37287c8 selftest failures 2026-10-04: stale JawaBench DLL + 3 dump-load flakes
e4e2668e4 ledger: ART_VERSION_WRANGLING_1 doubles follow-up note
8dd5b0271 art: queue doubles redos (Bantha x2, Dalgo, Eopie+calf, Iriaz edit of B); canon entries carry his rulings
aa5a1d233 MessyConduit walk: removal check (M9) paused — owner does not want it run regularly
6f7e3498f art: ingest doubles decisions; Nuna B owned by NunaArtOverride, SWBestiary copies retired
bc95463b9 CLAUDE.md: art sheets always show canon references; art goes through the art ledger
601664936 art doubles sheet: owner decisions (Nuna keep B both sexes; Bantha, Dalgo, Eopie, Iriaz redo from canon)
79f4d9e44 ledger: ART_VERSION_WRANGLING_1 phases 0-2 built note
5637a3384 ART_VERSION_WRANGLING_1: all-versions compare sheet + the doubles sheet
7214cff81 ART_VERSION_WRANGLING_1: phase 1 art ledger backfill
a4fb64010 ART_VERSION_WRANGLING_1: phase 0 art snapshot + art ledger tools
... 766 more: git log --oneline 0a1c4eb04..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-04T11:25:17Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
(committed at 2b7fc48c4; the live sidecar may write further rows: the owner's)
?? conversations/   session transcript exports written by a hook; deliberately untracked, not BENCH work
```

