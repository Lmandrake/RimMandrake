## Spec
The next batched window scores everything below, then this closes and a fresh sheet is
filed. Predecessor COLD_LOAD_RUN_SHEET_1 was scored 2026-08-29 (see its notes); detail
for any named item lives in items/<ID>.md.

## 0 — game DOWN, before anything else
```
taskkill.exe /F /IM RimWorldWin64.exe
python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py --gm --apply
```
- Deploys jawa/scenario_part_add + scenario_parts_get (d53bac44). Expected surface **246**
  (measure with tool_surface minus the jawa/revoke phantom; never quote).
- NO defDump arming needed unless a capture is wanted: dump_request.txt was deleted
  2026-08-29 after harvest, as designed.

## 1 — decision strings at launch
| # | expect | means if wrong |
|---|---|---|
| 1 | `[JawaBench] ready: 245 tools` (246 surface - 1 phantom... MEASURE, do not trust this literal) | old DLL loaded |
| 2 | `[JawaBench] context: modSet 582/…` | wrong mod list |
| 3 | NO `defDump ARMED` on the context line | a stray dump_request.txt re-appeared |

## 2 — with the bridge, campaign/scratch map
| item | reading |
|---|---|
| EMPIRE_PURSUIT_SCENPART_INSTALL_1 | the one-call install + scratch proof; exact call in the item note (2026-08-29). initCalls REQUIRED. |
| SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1 | mechanism still unread; substitution measured again 2026-08-29 (5/39 battery, 6/245 harvest, always vanilla Colonist, always bare) |
| SIX_FACTIONS_NEVER_RAID_1 | re-run ONLY on an aged colony with >600-tick census windows; identify the raid-deferring Harmony patch first (see 2026-08-29 note) |
| JAWA_SCENARIO_PARTS_1 | Jawa_UtinniStart spawns exactly one Ikee, Obedience-trained, Bonded — needs a NEW game start, could not run 2026-08-29 without tearing down the owner's loaded session |

## 3 — needs the GRAVSHIP SAVE loaded (BENCH_console_fixed.rws or successor)
| item | reading |
|---|---|
| EXPORTER round trip (owner sequencing: FIRST) | export_structure.py --rect 83,59,86,133 on the real megabone ship; the 2026-08-29 attempt exported desert rock — the ship is NOT on the fresh-start Ash'karr map |
| hull repaint | ONLY after the round trip: repaint_hull.py --census, --plan world/_ship/v2/plan_corrosion_halo.json --apply, RE-EXPORT, confirm paint carries; then apply_wall_colors.py/apply_wall_stuff.py are superseded and deletable |

## 4 — owner decisions surfaced 2026-08-29, still open
- Frozen OFFICIAL capture 2026-08-21T22-44-59Z is GONE from disk; re-freeze
  2026-08-29T05-18-06Z or restore from a backup nobody could find.
- 'Galactic Empire' names TWO factions on the live world (vanilla Empire reskin +
  OuterRim_GalacticEmpire) — BLACKSTAR_NAME_MUST_NOT_LEAK_1 criteria fail on the Empire half.
- WILD_ANIMALS_PADDED_LISTS_1: cast biomes are not exclusive (145 non-cast animals at >0 in
  Desert); 10 Anomaly-entity cast entries can never wild-spawn.

## 5 — look-at (owner's eyes, unchanged from sheet 1)
Adult bantha/eopie carry the new art; world labels clear of the limb (W5 exactly four
substitutions); 23 creatures visibly smaller, Zakkeg/Thrumbungus bigger; the Ikee reads as
a creepy eye with slime trail + nuzzle + mood pair. Plus NEW: the test dwelling stands at
rect 25,25,18,10 on the current map (disposable).

## PAWN_FLAVOR_STARWARS_1 — Jawa_PawnFlavor first load (added 2026-08-29, BENCH)
Deployed and active at position 581 (after mandrake.jawa.patches). Decision
strings for the next full-list load, written BEFORE the launch:
- FAIL if Player.log contains `Config error in Jawa_` or
  `Could not resolve cross-reference` naming any `Jawa_` or `JawaBSC_` id, or
  `Could not find parent node` after our mod loads.
- PASS positive observation (not mere silence): the post-load def dump contains
  BackstoryDef `Jawa_FarmFostered` and TraitDef `Jawa_WaterDiscipline`
  (`measure count BackstoryDef` should read 1225+50=1275 against a 585 capture),
  AND one spawned pawn of Homestead Defense League or Deep Desert Tribes shows a
  Jawa_* backstory title in its Bio tab (bridge: spawn via faction pawnkind,
  screenshot the card). Filter merge means roughly 1-in-3 pawns draw our
  category — check several pawns before calling absence.
- Also due at next game-DOWN: sync_mod_state (saves record 584, list is 585).
