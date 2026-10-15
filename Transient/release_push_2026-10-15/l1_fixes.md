# L1 fixes — BENCH builder, 2026-10-15

Source: `Transient/test_site_saves_2026-10-15/SITTING.md` (live session L1). Release-day: fixes only. No deploy, no bridge:
every fix is offline-proven only; each close names its live proof command.

| # | item | class | cause | fix | offline test (red on old) | sha |
|---|---|---|---|---|---|---|
| 1 | GSS_RESTRING_DIAGNOSE_FIXER_GETS_ZAPPED | MOD | design 2.6 sends the worker to the cut cell where the live half lies; the fallen-wire shock knocked him out | `AerialMath.ShockTakes`: the pawn on RM_RestringSpan is exempt; design 2.6 shock row corrected | SelfTest gpt-prerelease re-string rows + O7 shape | 21f2604349 |
| 2 | GSS_SESSION_RESET_REPAIR_SNEAKS_INTO_SAVES | MOD | GssSessionReset is a GameComponent, so every save named it | prefix on Game.ExposeSmallComponents drops it while saving; class kept, old saves load | validation.py O7 `unsaved_component_problems` + planted probe | 4f470f7c57 |
| 3 | BOTTLE_DIRTY_OFF_REPAIR_EMPTY_GOES_MISSING | HARNESS | the reused drinker walked off plot F in the wash row; residue lands beside the drinker (residueAt=148,130) | fresh drinker at the bottle; off-plot drinker = UNMEASURED | selftest_extensions stateful bottle fake | 1f00ca73c7 |
| 4 | PYRE_FIREBORN_DIAGNOSE_TWENTYONE_RETURN | HARNESS | the cap-budget clear only cleared 40x40 around pads; 21 off-pad fruit (source presumed stray fire, unproven) kept eating the per-map cap | extinguish whole map, destroy every ScorchFruit by cell | selftest_pyrelands_fruit_clear | 0b6132dcd0 |
| 5 | TESTENV_SWEPT_BRUISE_REPAIR_SLIPS_ITS_PASS | HARNESS | clockgate resumed declared stops only while ticks remained; a bruise on the chunk's last tick ("10 of 10") raised | resumable stop with nothing left completes the chunk | selftest_clockgate (exact L1 message) | 1bfc3301dc |
| 6 | WATER_NUTRITION_JUDGE_DRINKING_DINNER | owner card | water containers had Nutrition 0.05/0.25 | Nutrition 0 + NeverForNutrition, regenerated from the table | Tools/selftest_water_not_food.py | cfdd8d4023 |
| 7 | cross-biome-label settings files (00dbc3384b) | review | Greentide: canopy swarm switch dead + text said krannock in no roster (it is, 0.3); Warscar/TerminalBiomes: false comments; Warscar reset missed the list | krannock row removed at startup when off ([next game start]); comments corrected | selftest_settings_screens 822/822 | f361ad2843 |

Review: Greentide/Warscar/TerminalBiomes settings files full-file reviewed, CLEAN after fixes (Pyrelands was already CLEAN).
Other changed files had a same-day clean mark with only these fixes since: reviewed in full context of the change, CLEAN.
`FlowWorks/Tools/generate_liquid_suite.py` left DIRTY: it also carries the fuel-moat builder's b0ec1721ff since its mark.
