# The flagship moat: decision (for the Conductor), 2026-11-23

Item `RIMMANDRAKE_DECIDE_MOAT_RAID_BAR_TEXT_SAYS_D4_SCENE_NEEDS_SIX`. Map: `sweep_result.md` (made by `sweep.py`;
`drain_model.py` is the kernel's Python twin, equal to the recorded live drain to 1 dL; `raiders.json` is 21 recorded runs).

**Decision.** The flagship moat is 4 squares wide, dug 4 m (the bar's D4), with 3 m of water: a metre of wall above the water.
The drain pit is 20 m deep. No bar changes: `tree.json`'s "one deep D4 water moat" already says it. The scene's 3 m moat, full
to its rim, was the mismatch.

Why, from the map:
- **Level.** A person climbs 1 m. A moat full to its rim lets raiders out until its level fell more than 1 m; that takes 4 to 6
  pulses (1,000 to 1,500 ticks) and a raider swims 4 squares in about 360. With the water a metre down, raiders swim in and out,
  and the first fall of the level holds everyone in the water. With more wall than that nobody enters.
- **Width.** Two squares is about 130 ticks of swimming against a 250-tick tiredness check. Four is about 360 (every raider
  tires), the longest timber leaf, and the widest ring whose every square is within capture reach (6) of the inner rim.
- **Depth.** A drained floor is a prison only from 3 m down.

Share of simulated raids with two or more held and a raider tired, the sluice opened with two in the water: today's geometry
played in game time 0%; the pick 99% (96% without the climb cost, 92% one pulse late).

**The scene.** It drained the moat with bare flow pulses: 2,000 ticks of draining in no game time, the raiders standing still. A
moat that holds nobody in play passed it. It now drains in game ticks with the raid going on.

**The mod.** No mod fault found. Tiredness is added in 250-tick steps, so a short swim tires a raider by chance, right on average;
the flagship moat is wide enough that the step does not matter.
