## Spec
The next batched window scores everything below, then this closes and a fresh sheet is
filed. Predecessor COLD_LOAD_RUN_SHEET_1 was scored 2026-08-29 (see its notes); detail
for any named item lives in items/<ID>.md.

## 0 — game DOWN, before anything else ✅ DONE 2026-08-29 (BENCH, second sitting)
```
taskkill.exe /F /IM RimWorldWin64.exe
python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py --gm --apply
```
- ✅ Deployed at 81610f55: carries the scenario tools AND everything since
  (gravship skipCutscene, GM pair). Surface MEASURED 254 upper bound via
  tool_surface (was "expected 246" when only the scenario pair was pending —
  drift is later commits, not a leak; the launch ready-line derives its own
  gate from EXPECTED_TOOLS).
- ✅ sync_mod_state --apply: 7 files, every record now 1.6.4871 rev591 / 585
  mods, verified; backups alongside as *.bak-sync_mod_state.
- ✅ defDump RE-ARMED (dump_request.txt = all): the PAWN_FLAVOR and ISEKAI
  checks below need a fresh 585 capture from this load.

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
- ~~Frozen OFFICIAL capture gone~~ RESOLVED before this line was read: registry
  carries OFFICIAL-2026-08-29 (capture 2026-08-29T13-30-02Z, 584 mods, by owner),
  superseding the lost 2026-08-21 entry. Owner confirmed 2026-08-29: newer one is
  right.
- ~~'Galactic Empire' names TWO factions~~ NOT OPEN — ruled 2026-08-28 (canon.yml
  `empire.outerrim_faction_excluded`, does not reopen): OuterRim FactionDef cut in
  Cherry Picker (verified `present` in live settings 2026-08-29), mod stays active.
  The double reading was BENCH_console_fixed.rws, initiated pre-cut — residual only.
  WORLDMAP_V1_original.rws verified clean 2026-08-29 (0 hits both copies, literal
  scan w/ control; vanilla Empire present).
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
  (`measure count BackstoryDef` should read 1225+50+5=1280 against a 585
  capture — round 5 added 5 Deepwater backstories 2026-08-29:
  `Jawa_CisternHatched` present, and Jawa_DeepwaterCompact's merged
  backstoryFilters carry `JawaBSC_Deepwater`),
  AND one spawned pawn of Homestead Defense League or Deep Desert Tribes shows a
  Jawa_* backstory title in its Bio tab (bridge: spawn via faction pawnkind,
  screenshot the card). Filter merge means roughly 1-in-3 pawns draw our
  category — check several pawns before calling absence.
- Also due at next game-DOWN: sync_mod_state (saves record 584, list is 585).

## PAWN_FLAVOR cut pass — Cherry Picker verification (added 2026-08-29, BENCH)
143 new keys written to Mod_CherryPicker.xml (1342 -> 1485; backup
`.bak-20260829-pawnflavor`): 141 BackstoryDefs (Minotaur/Medieval/VQE-Ancients/
Archon) + TraitDef/RBM_Herculean_Trait + TraitDef/VQE_IdealPatient. Decision
strings, written BEFORE the launch:
- PASS: `[Cherry Picker]` removal list in Player.log contains
  `- BackstoryDef/RBM_Akabeko,` (sentinel for the whole class) and the two
  TraitDef lines. ⚠️ BackstoryDef is UNPRECEDENTED in this config — if the log
  shows the ThingDef cuts but NO BackstoryDef lines, Cherry Picker does not
  process that def type: revert nothing, file the spawnCategories-neutering
  patch fallback instead.
- EXPECTED noise, not failure: up to one `No shuffled ... Choosing random`
  error per VQE-quest patient or stray consumer pawn (10 mod-private categories
  emptied on purpose; engine falls back benignly — verified in source).
- The two save-carried exclusions (`RBM_Roamer`, `SH_MED_MedievalAlchemist`)
  must NOT appear in the removal list.

## ISEKAI reflavor first load (added 2026-08-29, BENCH)
IsekaiTraits_StarWarsReflavor.xml deployed (validate_patch: 30 ops, 1 match
each). Decision strings:
- PASS: next def dump (post-patch) reads TraitDef `Isekai_Protagonist` degree
  label as `chosen one` and `Isekai_Rank_F` as `guild rating F`
  (`measure record`); no `Patch operation ... failed` naming
  IsekaiTraits_StarWarsReflavor in Player.log.
- Remember: a patch that matches nothing logs nothing — the dump read is the
  positive check, the log only catches structural failure.

## EMPIRE_PURSUIT_SURVEY_SHADOW_1 — fork swap first load (added 2026-08-29, BENCH)
Owner asked for it at the bench. `mandrake.empirepursuit` (survey-shadow fork)
deployed and swapped into upstream's exact ModsConfig slot (295;
matathias.ruthlessmechanoids OUT; snapshot
`infrastructure/state/modlists/ModsConfig_2026-08-29_pre_empirepursuit_swap.xml`;
saves re-synced to the new 585). Decision strings:
- FAIL: `ReflectionTypeLoadException` or `Could not resolve type` naming
  RuthlessPursuingMechanoids; or the campaign load raising a scenario/ScenPart
  error (`Could not load reference` on the scribed pursuit part) — the fork
  keeps upstream's defName+class precisely so the save resolves.
- PASS positive: campaign loads clean AND (bridge, game-up) the item's own
  verify — scratch game, tiny delays: normal-biome map on the fast clock, an
  `AB_RockyCrags` (Forsaken Crags) map on the ~4x clock, read from the part's
  scribed mapRaidTimers in a save.
- ⚠ RimSort is possibly open: its view is now stale — hit Refresh, don't Save
  over this.

## SALVAGERS_FOLD_JUNKERS — campaign load check (added 2026-08-29, BENCH)
WORLDMAP_V1_original.rws edited: Salvagers ("The Comet Party") scribed
`defeated=True` (backup `.pre_salvager_fold_2026-08-29.rws`). On the next
CAMPAIGN load: no Scribe error naming `Faction_24` or `Salvagers`; The Comet
Party absent from the faction/comms UI (or listed defeated); Junkers unchanged.
