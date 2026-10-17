# SWBestiary follow-up (dragonsnake toggle + reviews + validation) — BENCH AFK 2026-10-17

## Status
DONE. Shas: 87d0b588bc (toggle), d22b147d11 (review fixes).

## 1. Albino dragonsnake toggle wiring
DONE, PUBLISHED 87d0b588bc. Field + Scribe line + "Albino dragonsnake" group ([next game start]) + csproj Compile line; DLL rebuilt
(0 warnings/errors), DLL+.srchash committed. Toggle verified against vanilla BiomeDef (wildAnimals/pollution/coastal lists and the three caches exist; cache also folds race.wildBiomes, which the toggle clears).

## 2. Code reviews
- RSW_DragonsnakeAlbinoToggle.cs, RSW_BeastMechanicsSettings.cs, Kernel/RSW_BeastKernel.cs, SelfTest/Program.cs: full read, no findings.
- RSW_BeastMechanicsProof.cs: FIX — ProofBrineTank counted (Count vs Sum) and DESTROYED every taozin-brine jar within 4 cells, including pre-existing player jars; now snapshots jars before and only counts/destroys ones it made.
- SelfTest/BestiaryFuzz.cs: FIX — vacuous `Check(... || true, "-")` in kiln removed; brine family now stops at 3 failures like the rest.
- RSW_MlieWaveC_Bodies.xml (10.7k lines, full read + structural check of all 57 BodyDefs: refs resolve, coverages <= 1): FIXES — Bogwing rear-left leg 0.07 -> 0.03 (asymmetry); Pikobis/Scurrier right leg 0.03 -> 0.07 and right ear depth Inside; Kowakian monkey-lizard brain had no depth Inside (hittable from outside); Gutkurr right foot labelled "left", Jakobeast rear-left LEG labelled "paw", Kwi right foot/paw labels; spelling (secong, compund, serated, pheremone, elipsical, quadrapedal, reptillian, bepedal, octupoda, bidpedal, quadrupredal, scaley); header's Dragonsnake text was false after the rebuild.
- RSW_Dragonsnake.xml: header claimed the snake body and a BiomeCypreJungle cast (both false now) — corrected; description grammar/"biolumescent".
- WildAnimals_Greentide.xml: no findings.
- validation.py: FIX — deploy_held matched src-relative keys; DEPLOY_HOLD/deploy tool use Mod/rel. Docstring said TWO DLLs/settings classes (three).
- REAL DEFECT (dragonsnake build): src/DEPLOY_HOLD.txt albino line was `RimStarWars/SWBestiary/...` and held NOTHING — deploy plan showed `+ RSW_DragonsnakeAlbino.xml` (would ship with no art and switch on its Greentide rows). Fixed to `SWBestiary/...`; plan now `H`. Lesson filed.
- All 10 files mark-clean at d22b147d11. Reachability: all reached (DLL csproj, SelfTest csproj via selftest_swbestiary_fuzz.py, defs used by races).

## 3. Static validation + selftests
- `python3 src/RimStarWars/SWBestiary/validation.py` -> STATIC: PASS (0 findings). The 6 scrap-bird/taozin toggle rows are fixed (all 15 settings fields are in suite.toggles, Scribed and drawn).
- run_selftests: selftest_swbestiary, selftest_swbestiary_fuzz, selftest_greentide_spine PASS; selftest_greentide_fuzz SKIPPED unchanged since PASS -> GREEN.

## Owed
- Deploy SWBestiary (DLL, Bodies, RSW_Dragonsnake.xml; albino stays held) + UtinniPatches (WildAnimals_Greentide.xml) + Cuisine (taozin) — game RUNNING, none applied.
- Live rows: SWBestiary dragonsnake_pair, defs_resolve, taozin_brine_tank_infuses_and_whitens, settings_albinoDragonsnakeEnabled_round_trips. Body changes: check Player.log for body-part errors on loaded saves.
- Albino art install, then delete its DEPLOY_HOLD line (dragonsnake_build.md Owed 2).
