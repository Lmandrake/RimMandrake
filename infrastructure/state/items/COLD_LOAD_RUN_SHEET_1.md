# COLD_LOAD_RUN_SHEET_1

## Spec

One batched cold load scores everything below, then this item closes and a fresh one
is filed for the next load. This item replaces `NEXT_RELOAD.md` and
`EXPECTED_FAILURES_next_load.md` (both deleted 2026-08-27, owner's ruling — the
hand-kept run-sheet files rotted twice and grew police tooling; git holds their full
text at the parent of this commit). Detail for any named item lives in
`items/<ID>.md`; this sheet is the batch order and the decision strings, nothing else.

## 0 — game DOWN, before anything else (see DOWN_WINDOW_ASSEMBLY_DEPLOY_1)

```
taskkill.exe /F /IM RimWorldWin64.exe
python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py --gm --apply
```
- `--gm` mandatory; a refusal about tool removal means you dropped it — never
  `--allow-tool-removal`. Check the output for the word `deployed`.
- Built clean 2026-08-28: surface **240** (adds `jawa/paint_building` — vanilla
  Building.ChangePaint — and `jawa/export_things`, the identity-grade exporter
  read), 0 warnings. The game copy is at 166 — everything since 2026-08-26 is
  undeployed, so this window pays for all of it.
- New this build: a Harmony prefix on RimBridgeServer (`jawa/bridge_arg_report`);
  if the bridge misbehaves post-deploy, grep `[JawaBench] argument guard` first.
- Same window: `deploy_custom_mods.py --mod RimDefDump --apply` — the 2026-08-28
  build adds `paintable` flags (buildings AND floors) to the dump, which is what
  makes offline template generation able to know what the game will paint.
  After the load's fresh capture + `refresh.py`, `rimplace verify` stops
  answering PAINT: UNMEASURED.
- XML deploys need no window; do them any time.

## 1 — decision strings, written BEFORE launch (a signature invented after reading
the log is a story that fits)

| # | expect to SEE | means if wrong |
|---|---|---|
| 1 | `[JawaBench] ready: <N> tools, build <stamp>` where N matches `build.py tool_surface` on the deployed DLL (238 at `887d4a3d`) | 166/121 = an old DLL loaded; other = run the census, do not guess |
| 2 | `[JawaBench] context: modSet 582/…` (== ModsConfig activeMods count) | 581 = wrong mod list; every reading is against the wrong stack |
| 3 | `defDump ARMED` on the context line | 🔴 the marker is NOT consumed — **delete `dump_request.txt` after harvest** or every load pays ~27 s and 1.2 GB |
| 4 | `[RimBridge] STARTUP_TIMING phase=bridge-start.total` | absent = no bridge; bridge-gated items stay put |

## 2 — the first five minutes, in order

0. If Ash'karr loads and the ideology trial is intended:
   `vivify_world.py --live --out world\ASHKARR_PREREBUILD` **before** leaving the menu.
1. `python.exe …\bridgetools\prove_stat_and_room.py --census` — everything depends on it.
2. `harvest_log.py` — the whole log; it is destroyed at the next launch. (The previous
   session's log died at `Reached max messages limit` — this load restores logging.)
3. Rebuild `defs.sqlite` from the fresh capture; **delete `dump_request.txt`**.
4. The newest def dump predates the 2026-08-26 20:59 `BiomeCast_Ashkarr.xml` deploy —
   biome items are unscoreable until this load's capture exists.

## 3 — log greps, with baselines

| item | expect | baseline |
|---|---|---|
| (hood, closed — regression only) | `required apparel can't be worn together` → **0** | 3 |
| BIOME_DUPLICATES_STILL_LIVE_1 | `same key has already been added` → 0; DEAD MODS → 0; then `biome_animal_conflicts.py` → 0 pairs; then commonalities **744/744 non-zero** (was 563) — if pairs→0 but zeros stay, the diagnosis is wrong and BIOME_CAST_COMMONALITIES_ZEROED is a real second defect | 12 keys · 2 dead mods |
| (genes, deployed) | DEFS DISCARDED → 2 (the benign VFE torches); `SW_Genes.xml` → 0; four `RimMandrake_tattooGene_*` present in the capture | 6 · 4 |
| unattached | `Could not resolve cross-reference` ~25 · `Races_Eyeling`/`JawaFactionRoster`/`JawaIkee`/`XenotypeDef` load errors → 0 | prior load |

## 4 — bridge readings, per open item (detail on each item)

| item | reading |
|---|---|
| SIX_FACTIONS_NEVER_RAID_1 | the biggest open defect; settlement-count lead already refuted in the item |
| AUTHORED_FACTION_RAID_SPAWNS_NOTHING_1 | retry ×3 before recording any raid negative |
| FIRE_RAID_ECHOES_REQUESTED_FACTION_1 | `fire_raid {faction: Jawa_FreeDroidEnclaves}` must say *substituted* and name the actual in `actual`/`arrived[]` |
| BUILD_BATCH_OVERWRITES_SILENTLY_1 | rebuild the dwelling; assert `survived == requested`, expect 0 `displaced` |
| BRIDGE_ARG_SHAPES_INCONSISTENT_1 | any `Thing_`-prefixed pawn id resolves; gear rows carry `defName` beside `def` |
| BRIDGE_DROPS_UNKNOWN_PARAMS_1 | `world_tile_export` no-flags returns **10** columns, 10th `pollution`; read the header, a stale companion looks correct otherwise |
| ANCIENT_SCATTERBOW_TAG_SEVER_1 | `MA_CapryakScatterbow` weaponTags: `Gun` GONE, `NeolithicRangedAdvanced` remains |
| ROLE_KINDS_ARMED_5_OF_5_1 | `roll_arm_harvest.py --rolls 5` AFTER-half vs BEFORE (21/285 bare, 16/49 kinds); ⛔ never score with `pawnkind_audit` — it cannot see a roll |
| THOROUGH_RETAG_WEAPONS_ARMOUR_1 | 10× Empire_Grunt: cuirass+helmet, E-11-class rifles, 0 bare · Jawas robe+hood only · Junkers full warcasket · trooper plate own art · Blackstar Leader 997 / Specialist 718 holding a KotOR legendary |
| SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1 | census requested-vs-actual kind on every spawn used above |
| JAWA_SCENARIO_PARTS_1 | `Jawa_UtinniStart` spawns exactly one Ikee, Obedience-trained, Bonded |
| BLACKSTAR_NAME_MUST_NOT_LEAK_1 | one "Blackstar Company" in the faction list; pirate kinds carry generated names |
| DUMP_PRODUCER_DATED_CAPTURES_1 | a dump taken after a Cherry Picker cut must NOT still show the cut defs (baseline: 1210/1342 still present) |
| TEMPLATE_ENGINE_ACCEPTANCE_1 | criteria 1–2: `room_get` reads Bedroom/DiningRoom/Storeroom roles; nursery ≤ 32 °C on a hot tile |
| CAST_LIVE_SPAWN_CHECK_1 · ION_TIERS_MEASURED_LIVE_1 | as filed, need the fresh dump first |
| EXPORTER round trip — FIRST, before any repaint (owner's sequencing, 2026-08-28) | `export_structure.py --rect 83,59,86,133 --out world/_ship/exports/corrosion_halo.plan.json` on the CURRENT megabone ship; rimplace-lint and contract-check the plan offline. A clean export of the unpainted ship is the baseline proving nothing painted can ever be lost |
| hull repaint (owner's call, 2026-08-28) | ONLY after the export round trip: census (`repaint_hull.py --census "83,59,86,133"`), optionally rebuild the hull in an honest material, `repaint_hull.py --plan … --apply`, then RE-EXPORT and confirm the plan carries the paint. Once verified live, `apply_wall_colors.py` and `apply_wall_stuff.py` are superseded and deletable |

Look-at (owner's eyes, no command): adult bantha/eopie carry the new art (juvenile-only
was the bug — deployed files proved nothing); world labels sit clear of the limb
(`world-label-lift` W5 expects **exactly four** substitutions — read the error line,
not `armed`; if 1.5 doesn't clear it, find what draws above `Radius`, don't raise it);
23 creatures visibly smaller, Zakkeg/Thrumbungus bigger; the Ikee reads as a creepy
eye, slime trail + nuzzle + mood pair.

## 5 — traps that cost sessions (full text: `as per the trap file`)

Score off read-backs, never `success` · a raid census right after firing reads zero —
step ticks · `pawn_get` nests under `pawns[0]`, equipment keyed `def` · a deployed DLL
registers NOTHING until the game restarts · `set_faction_relation` cannot flip
hostility — use `faction_relations_set` · T2 temperature is ungraded until
JAWA_TEMP_RANGE_TWO_CRITERIA is answered (criterion picked after looking tests nothing).
