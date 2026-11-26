# Pyrelands 0.2.0: what we might put into it (a proposal for the owner)

Written 2026-11-26 by the Designer run of item `RIMMANDRAKE_OPEN_PYRELANDS_NEXT_VERSION_HE_ASKED_FASTER_FIRE`, on the
Conductor's order. **Nothing here is opened or locked.** Pyrelands stays at 0.1.0 (passed at his walk, 2026-11-24) until he
answers. His words of 10:41 AM PST 2026-11-26: *"If we're opening 0.2.0 for Pyrelands, I want to review what we might put
into it, ok? That's not an automatic decision"*.

Each block below is one candidate change. "Size" is the build and test work in one word. Every entry of
`design/concepts/Pyrelands/version/next_version/README.md` is here, read against the code of 2026-11-26.

In short, the recommendation: **in 0.2.0** are faster fire, roofed grass that dies where the player can see it (this
fixes an error in the log too), the smoke weather, the switch to mechanics that work by their conditions, the one-line
log error at load, three cheap offline tests and one bar sentence that needs new words. **Later** are the rain that fills
the moat and the tanks (it needs FlowWorks first) and two offline tests. **Dropped** are the coverage re-judge (it is done
already) and the startup config errors (they belong to another mod).

---

## Problems (defects the player would notice)

### Roofed grass writes an error into the log each time a plant dies
- **What the player would see:** nothing in play. A player who opens the log (or a mod-list debugger) sees one red
  error for each roofed grass plant that dies. On his walk save there were 25 on every load.
- **His words:** none on this point. It was found in the log of his walk of 2026-11-24.
- **Needs:** Pyrelands code only (`src/RimMandrake/Pyrelands/Source/CompWithersUnderRoof.cs`: the roof deals the last
  hit point inside the game's own plant tick, and the game then reads the dead plant). A live check, kind A: a roofed
  plant at its last hit point dies, and the log has no new error.
- **Size:** small. The fix is in the same few lines that the next block rewrites.
- **Recommendation:** in 0.2.0, done together with "Roofed grass declines where the player can see it".

### One warning at load: "Tried to get CurKindLifeStage from humanlike pawn Flea"
- **What the player would see:** nothing in play. One yellow line in the log on each load of a save.
- **His words:** none. Found in the log of his walk of 2026-11-24.
- **Needs:** first a stack trace on a debug build, to find which code asks. The best guess (about 75%) is FlowWorks'
  swimming code, not Pyrelands. The fix is then a one-line guard in the file the trace names. A live check, kind A: a
  reload of the walk save logs the line no more. It needs a game for one load.
- **Size:** small.
- **Recommendation:** in 0.2.0 as work that adds no bar. It keeps the log clean, which every version must. If the trace
  names FlowWorks, the guard goes in FlowWorks with its own test.

### Startup config errors on the Pyrelands mod list
- **What the player would see:** red lines at game start. The first one (a missing framework that dropped a whole
  plant) is fixed already. The four left are about Jawa weapon money in another mod (UtinniPatches); three more are not
  proven ours.
- **His words:** none.
- **Needs:** UtinniPatches' defs, not Pyrelands'. That work is filed as its own item.
- **Size:** small, in the other mod.
- **Recommendation:** drop from 0.2.0. It is not Pyrelands' to fix.

---

## Divergent changes (they extend what the mod is for)

### Faster fire: the fire catches and runs
- **What the player would see:** a spark in standing grass (lightning, a fire-hawk's twig, a furnace-beast, a torch) takes
  hold instead of guttering out. On the same day, one burning spot grows into a front that the player must answer. The
  head of the front walks downwind clearly faster than in 0.1.0, so a front seen far upwind reaches the colony before the
  player can just wait it out. It is still a walking line with black ground behind it and grass greening behind that; it
  never sets most of the map alight at once. Today the carry is about 43 cells a day, so a front takes several days to
  cross a map.
- **His words:** walk of 2026-11-24, *"The fire barely catches, to be honest. I had expected faster spread."* and *"Yes,
  slow fire is a pass for this version, next version puts more aggressive fire."* Also his picture of 2026-11-13: *"Fire is
  always coming, you never should "wait for a calm stretch when you can..." The beasts start fires."*
- **What "more aggressive" means, as an experience:** the spark takes, a front forms the same day, and the front's head
  outruns 0.1.0's. It does not mean a bigger fire: the 0.1.0 bars that keep the fire a line stay.
- **Needs:** Pyrelands code only (the burn kernel's pace and how readily a lit cell spreads). A "Fire pace" slider in Mod
  Settings, its default the new pace, its low end 0.1.0's pace. No art. Tests: an offline model of the burn from one lit
  cell (kind A, deterministic), then one live staged spark in open grass on a Pyrelands map with the weather held clear
  (kind B, because whether a given spark takes is random by design; its run budget is written before the first run).
- **Size:** medium. The pace numbers are easy; holding the "never a flood" bars at the new pace is the real work.
- **Recommendation:** in 0.2.0. He asked for it at his walk.

### Roofed grass declines where the player can see it, and leaves dead grass
- **What the player would see:** when the player roofs over grass, each plant visibly wilts as it weakens, and its
  inspect pane says that it withers under the roof. The plants of one roofed patch die over a spread of time, not in one
  moment. Each dead plant leaves dead grass that the player can see; colonists can cut it, and it crumbles away by
  itself. Today the whole patch dies at the same moment and leaves bare ground.
- **His words:** walk of 2026-11-24, *"OMG, the grass just suddenly all dies at the same time. Kinda weird. And it
  doesn't turn into dead grass, just... barren nothing. You can't see grass health, so it was quite abrupt. But for this
  version, that's a pass."*
- **Needs:** Pyrelands code (the same file as the log error above). Art: a wilted look of the shipped grass and a dead
  grass look. Existing regenerated art is searched first; any new picture goes through the art judge and `art install`.
  Tests: an offline check of the wither rule over a roofed patch (kind A), then one live roofed patch watched through its
  wither time, with the log read for the error (kind A).
- **Size:** medium. The code is small; the two new looks are the cost.
- **Recommendation:** in 0.2.0. He asked for it at his walk, and it fixes the log error above.

### A choking smoke that comes as its own weather
- **What the player would see:** now and then a thick smoke rolls over the Pyrelands as a weather of its own. The sky
  and the screen read as smoke, not as ash fall and not as rain. A colonist out in it is hampered (breathes, moves and
  works worse) and shows a readable reason; a colonist under a roof is spared. The smoke puts out no fire, and black rain
  stays the only rain.
- **His words:** walk of 2026-11-13, *"And I won't miss having to sweep the ash away from all my paths to keep walking
  clear, or the choking smoke that sometimes come as its own weather..."* By card of 2026-11-17 he put it in the next
  version because 0.1.0 had first to pass what it promised. 0.1.0 has now passed.
- **Needs:** Pyrelands code and defs: a new weather, its place in the biome's weather table, a harm on pawns out in it.
  The look reuses a weather overlay; new art only if the judge finds the reuse does not read as smoke. Mod Settings: an
  on/off and how often it comes. Tests: its offline acceptance script exists (`pyre_smoke_weather_accept.py`, 2 of 6
  today, kind A), then one live check with the smoke forced on, one colonist outdoors and one under a roof (kind A).
- **Size:** medium. It is a whole new weather with a harm.
- **Recommendation:** in 0.2.0. His reason to wait is spent, and it is his own picture of the place.

### Black rain fills the moat and the water tanks
- **What the player would see:** a black rain partly fills an open-sky water tank and a dug moat, so the player can store
  water against the next fire.
- **His words:** walk of 2026-11-13, *"The Black Ash rain: a violent time with violent plenty right after, and a rare
  chance to fill your moat against the fire and fill your water tanks."* By card of 2026-11-17: next version.
- **Needs:** FlowWorks' water code. Rain filling a tank or a channel is a water mechanic, so by the rule that mechanics
  work by their conditions it must work for any heavy rain, in FlowWorks. FlowWorks 0.1.0 has not passed. **The
  Pyrelands half cannot stand alone:** all it would add is "black rain counts as heavy rain", and black rain already is
  the rain of the Pyrelands weather table.
- **Size:** large, and most of it in another mod.
- **Recommendation:** later, with FlowWorks' next version.

---

## Work that adds no bar

### Three offline tests of the code that the conversion rewrites
- **What the player would see:** nothing. These tests run our real code for three behaviours outside the game: a hungry
  colonist eats before fire duty, a colonist steps off burning ground, an ashwallow dives from a front.
- **His words:** he adopted this kind of test by card on 2026-11-08 ("Policy plus real-types pilot").
- **Needs:** test code only. One of the three is written already. Each is shown red on a planted fault, then green.
- **Size:** small.
- **Recommendation:** in 0.2.0 for these three, because the conversion below rewrites the code they test. The other two
  (wet roots in the heat, the furnace-beast's warmth) stay later: 0.2.0 does not touch their code.

### Re-judge the mod's test coverage under the calibrated judge
- **Recommendation:** drop. It is done already: the coverage judge read Pyrelands as covered under a calibrated brief on
  2026-11-17 (measured 2026-11-26).

### New words for the whole-season walk bar
- **What the player would see:** nothing in play. The bar `walk_season_on_the_pyre` still says that the player plays a
  fresh colony "through about two weeks on the full list". By the ruling that season-long play is play testing, those
  words cannot be passed by any test, and the bar is decided by its short scenes.
- **His words:** none on this bar. The ruling is `design/specs/2026-11-24-oversized-scenes/long_play_bars.md`.
- **Needs:** a change of one sentence in `tree.json`, which is the Conductor's act. The change makes the Cold Reader exam
  run again (one fresh judge).
- **Size:** small.
- **Recommendation:** in 0.2.0, because the sentence today promises what no test can show.

### On the Polish list, not proposed
Three lines on `design/concepts/Pyrelands/version/polish.md` wait on his confirmation: a clear-sky ash patch as a
control in the three-skies scene, greener regrowth after a week, and a check that the fire-hawk picks the largest fuel.
Polish is not part of passing. None is proposed for 0.2.0.

---

## The conversion: each mechanic works by its conditions, not by the biome

- **What the player would see:** on a Pyrelands map, nothing changes. In Mod Settings the player finds a plain on/off for
  each Pyrelands mechanic, each on by default, and no switch names a biome. The "Enable outside the Pyrelands biome"
  switch and its three sub-settings are gone. On another map, a mechanic acts only where its conditions are, which in
  practice is rarely, because the conditions are the Pyrelands' own grasses and ash ground.
- **His words:** his cards of 2026-11-21, "What becomes of the six 'Enable outside this biome' switches? -> Turn each into
  a plain on/off (Recommended)" and "Are dangerous mechanics on by default on every map? -> On everywhere; conditions
  decide (Recommended)". These are the card labels that he picked, not typed words. The rule says a mod converts when it
  next advances.
- **What changes, row by row** (from `design/specs/2026-11-21-guiding-principles/conversion_list.md`, section Pyrelands):
  - The ashwallow dives from fire wherever a fire front comes near it, not only on a Pyrelands map.
  - The wind carries a fire, and the burn line is measured, wherever a free fire burns on ash ground or in the
    Pyrelands' grasses. Vanilla fire elsewhere is untouched.
  - Fire ecology (ash, scorch-fruit, the fresh-burn bonus) follows a fire that burns out on ash ground or in those grasses.
  - Ash builds up on sand wherever ash falls on sand.
  - Herd thirst works for any herd animal of the Pyrelands cast, wherever it lives.
  - A person steps away from fire, and a hungry colonist eats before fire duty, on any map where a fire burns.
  - The per-biome gate and the cross-biome switch go. The "Mod enabled" master stays.
  - Each mechanic has its own plain on/off, default on. Most have one already; three get one now: herd thirst, the step
    away from fire, and the meal before fire duty.
  - The biome keeps its data as data: no ordinary rain in its weather table, the odds of its standing burn, its animal
    roster, and the foreign animals that it keeps out. These are read from the biome's own defs, never from a list of
    names in code.
- **Needs:** Pyrelands code in about a dozen places, and its Mod Settings page. Tests: an offline read that no mechanic
  gate names the biome (kind A), the existing offline settings checks, and the existing live scenes of each mechanic
  that the change touches, run again on a Pyrelands map (kind A). No test on another biome's map is owed.
- **Size:** large. Many small edits, each with a scene that must still pass.
- **Recommendation:** in 0.2.0. It is owed by his ruling when the mod advances.

---

## What is already written down as a draft

An earlier Designer run of this item wrote the four bars below, their test rows and a vision section into the repo
(commit `faa90e801d`), before his word of 10:41 AM PST reached it. They are a draft, not an open version:
`VERSION.json` still reads 0.1.0, and nothing builds them. This run marked the four draft bars in
`design/concepts/Pyrelands/record.json` as open questions, so that no stage can take them as work. When he answers, the
Designer opens 0.2.0 with what he keeps, and takes out the draft rows and the vision lines of what he cuts. The heading
of the draft section in `design/concepts/Pyrelands/version/vision.md` says "opened 2026-11-26"; that word is wrong until
he answers, and the Designer corrects it when the version opens.

## The proposed bars (each one PROPOSED, none locked)

- **PROPOSED `fire_catches_and_runs`:** A spark that lands in standing Pyrelands grass takes hold, grows into a front that
  the player must answer on the same day, and its head walks downwind visibly faster than the fire of 0.1.0, while it
  stays a walking line that never sets most of the map alight at once.
- **PROPOSED `roofed_grass_declines_visibly`:** Roofed Pyrelands grass visibly wilts and says why, the plants of one patch
  die at different times, each dead plant leaves dead grass that colonists can cut and that crumbles away, and nothing
  reaches the error log.
- **PROPOSED `pyre_smoke_weather_chokes`:** Now and then a choking smoke comes over the Pyrelands as its own weather, reads
  as smoke, hampers a colonist out in it with a readable reason, spares a colonist under a roof, and puts out no fire.
- **PROPOSED `mechanics_switch_plain_no_biome`:** Mod Settings holds a plain on/off for each Pyrelands mechanic, each on by
  default and none naming a biome; on a Pyrelands map everything plays as before, and with every switch off the game
  still runs clean.
