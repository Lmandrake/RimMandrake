## spec
found-by: BENCH bridge run (2026-10-23, run 1, build fed77f423a, 14-mod tier, `suspension_bridge_proof.py --fresh-map`).
**PRIOR PASS NOW FAIL (STOP).** Row GRATE_fire_burns_people_above -> SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP A1.
- 2026-10-22 belt (41fb948b5e, `src/RimMandrake/FlowWorks/northstar/suspension_result_20261022T0925_belt.json`): PASS,
  grate riders 15 Burn hediffs, solid-deck control 3.
- 2026-10-23 (fed77f423a, `Transient/bridge_run_1_20261023/suspension_bridge.json`): FAIL, grate 5, SOLID 6. All four
  chemfuel fills FILLED F=2 on both pits, both LIT, health read present, every rider in the after-read. Solid pit read
  "burned levels 8 ... GRATE grated=False deck=True fire=False attach=0.35"; grate pit "burned levels 0 ... fire=True".
Repro: `python.exe src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py <out.json> --fresh-map` (scene GRATE_fire,
plot origin+(1..4, 20/24), pits 2 m, 3 drafted riders per deck, 2500 ticks).
Class: MOD presumed, unproven. Leads (commits between the two runs touching fire): 4b8630aece (every liquid spills as a
sheet, fuel spreads and burns, D5), 4d833ad1bd (channel fire lights adjacent spills), 27543e58c3 (pool-fire burn rates),
c963216c28. Two readings to separate: (a) burning fuel now spreads onto/around the solid deck and burns its riders (control
broken by D5 spread — then the row needs the scenes further apart or the bar restated), (b) the grate scene burns less
(grate burns fell 15 -> 5). Check where the solid riders' burns came from (fire cells adjacent to them at tick 2500).
