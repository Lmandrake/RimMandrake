# Pyrelands 0.2.0: what we might put into it (a proposal for the owner)

Written 2026-11-26 by the Designer run of item `RIMMANDRAKE_OPEN_PYRELANDS_NEXT_VERSION_HE_ASKED_FASTER_FIRE`, on the
Conductor's order. **Pyrelands 0.2.0 was opened on 2026-11-26 with what he kept** (his two cards, 11:50 AM and 12:44 PM
PST; `../VERSION.json`). Each block below now says what was decided. His words of 10:41 AM PST 2026-11-26: *"If we're opening 0.2.0 for Pyrelands, I want to review what we might put
into it, ok? That's not an automatic decision"*.

## His answers (question card, 11:50 AM PST 2026-11-26)

- **Decided by him, 2026-11-26:** faster fire, roofed grass that dies where the player can see it, and the smoke weather
  go into 0.2.0. His words: *"Certainly all of these and likely more too"*.
- **Decided by him, 2026-11-26:** the conversion to mechanics that work by their conditions goes into 0.2.0, with those
  three (his pick: "With the features (Recommended)").
- **Decided by him, 2026-11-26:** the black rain that fills the moat and the tanks leaves the Pyrelands scope. It is
  FlowWorks work. His words: *"Filling a moat is soundly a flowworks ticket not a pyrelands ticket. It should fill
  precisely the same as any heavy rain so there’s no special pyrelands code except to make sure they black rain is
  treated as rain in terms of making ground water and that the biomes are configured correctly for ground water level
  and porosity and other parameters like evaporation. Still all flowworks."*
- **What he asked next, about 11:55 AM PST 2026-11-26:** *"I would like to see options to add more to the next version of.
  Pyrelands 0.2.0. Sweep up all the polish items and add them for instance. But show me the other deferred capabilities
  too. Like the ones split off in mechanics right now."* The answer is the part "More that could go into 0.2.0" at the
  end of this page.

Each block below is one candidate change. "Size" is the build and test work in one word. Every entry of
`design/concepts/Pyrelands/version/next_version/README.md` is here, read against the code of 2026-11-26.

In short: **he took** faster fire, roofed grass that dies where the player can see it (this fixes an error in the log
too), the smoke weather and the switch to mechanics that work by their conditions. **Recommended with them** are the
one-line log error at load, three cheap offline tests and one bar sentence that needs new words. **Gone to FlowWorks** is
the rain that fills the moat and the tanks. **Later** are two offline tests. **Dropped** are the coverage re-judge (it is
done already) and the startup config errors (they belong to another mod).

---

## Problems (defects the player would notice)

### Roofed grass writes an error into the log each time a plant dies
- **Decided:** in 0.2.0, by the Conductor's call of 2026-11-26 (a Problem is a defect, and a defect stays with the open version); fixed with bar `roofed_grass_declines_visibly`.
- **What the player would see:** nothing in play. A player who opens the log (or a mod-list debugger) sees one red
  error for each roofed grass plant that dies. On his walk save there were 25 on every load.
- **His words:** none on this point. It was found in the log of his walk of 2026-11-24.
- **Needs:** Pyrelands code only (`src/RimMandrake/Pyrelands/Source/CompWithersUnderRoof.cs`: the roof deals the last
  hit point inside the game's own plant tick, and the game then reads the dead plant). A live check, kind A: a roofed
  plant at its last hit point dies, and the log has no new error.
- **Size:** small. The fix is in the same few lines that the next block rewrites.
- **Recommendation:** in 0.2.0, done together with "Roofed grass declines where the player can see it".

### One warning at load: "Tried to get CurKindLifeStage from humanlike pawn Flea"
- **Decided:** in 0.2.0 as work that adds no bar, by the Conductor's call of 2026-11-26 (a Problem is a defect, and a defect stays with the open version).
- **What the player would see:** nothing in play. One yellow line in the log on each load of a save.
- **His words:** none. Found in the log of his walk of 2026-11-24.
- **Needs:** first a stack trace on a debug build, to find which code asks. The best guess (about 75%) is FlowWorks'
  swimming code, not Pyrelands. The fix is then a one-line guard in the file the trace names. A live check, kind A: a
  reload of the walk save logs the line no more. It needs a game for one load.
- **Size:** small.
- **Recommendation:** in 0.2.0 as work that adds no bar. It keeps the log clean, which every version must. If the trace
  names FlowWorks, the guard goes in FlowWorks with its own test.

### Startup config errors on the Pyrelands mod list
- **Decided:** in 0.2.0 as work that adds no bar, by the Conductor's call of 2026-11-26 (a Problem is a defect, and a defect stays with the open version): the check is a startup of the Pyrelands small list with no config error, and the fix lands in UtinniPatches' defs.
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
- **Decided:** in 0.2.0, by his card of 2026-11-26 (11:50 AM PST).
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
- **Decided:** in 0.2.0, by his card of 2026-11-26 (11:50 AM PST).
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
- **Decided:** in 0.2.0, by his card of 2026-11-26 (11:50 AM PST).
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
- **Decided:** out of the Pyrelands scope, by his card of 2026-11-26. Its new home is FlowWorks (`mod:FlowWorks`, ticket
  `RIMMANDRAKE_BUILD_BLACK_RAIN_FILLS_MOATS_TANKS_STAY_DRY`, with his words).

---

## Work that adds no bar

### Three offline tests of the code that the conversion rewrites
- **Decided:** in 0.2.0, by the Conductor's call of 2026-11-26 (part one's work that adds no bar goes in).
- **What the player would see:** nothing. These tests run our real code for three behaviours outside the game: a hungry
  colonist eats before fire duty, a colonist steps off burning ground, an ashwallow dives from a front.
- **His words:** he adopted this kind of test by card on 2026-11-08 ("Policy plus real-types pilot").
- **Needs:** test code only. One of the three is written already. Each is shown red on a planted fault, then green.
- **Size:** small.
- **Recommendation:** in 0.2.0 for these three, because the conversion below rewrites the code they test. The other two
  (wet roots in the heat, the furnace-beast's warmth) stay later: 0.2.0 does not touch their code.

### Re-judge the mod's test coverage under the calibrated judge
- **Decided:** dropped: it was done on 2026-11-17 (the coverage judge read Pyrelands covered under a calibrated brief).
- **Recommendation:** drop. It is done already: the coverage judge read Pyrelands as covered under a calibrated brief on
  2026-11-17 (measured 2026-11-26).

### New words for the whole-season walk bar
- **Decided:** in 0.2.0, by the Conductor's call of 2026-11-26 (part one's work that adds no bar goes in).
- **What the player would see:** nothing in play. The bar `walk_season_on_the_pyre` still says that the player plays a
  fresh colony "through about two weeks on the full list". By the ruling that season-long play is play testing, those
  words cannot be passed by any test, and the bar is decided by its short scenes.
- **His words:** none on this bar. The ruling is `design/specs/2026-11-24-oversized-scenes/long_play_bars.md`.
- **Needs:** a change of one sentence in `tree.json`, which is the Conductor's act. The change makes the Cold Reader exam
  run again (one fresh judge).
- **Size:** small.
- **Recommendation:** in 0.2.0, because the sentence today promises what no test can show.

### The Polish list
- **Decided:** in 0.2.0, by his card of 12:44 PM PST 2026-11-26 ("All five groups (Recommended)").
He asked on 2026-11-26 to sweep the Polish list into 0.2.0. Every line is sorted in the part "More that could go into
0.2.0", section one, at the end of this page.

---

## The conversion: each mechanic works by its conditions, not by the biome
- **Decided:** in 0.2.0, by his card of 2026-11-26 (11:50 AM PST).

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
(commit `faa90e801d`), before his word of 10:41 AM PST reached it. The Conductor took that draft out of the live files the
same day. After his two cards, the opening run of 2026-11-26 put the draft back into `record.json`, `scenes.json`,
`version/test_table.json` and `version/vision.md`, read against his cards, and added the two bars of his second card.

## The bars proposed here (all four are in 0.2.0, by his card of 11:50 AM PST 2026-11-26)

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

---

# More that could go into 0.2.0

Written 2026-11-26 after his question of about 11:55 AM PST. His card of 12:44 PM PST 2026-11-26 decided it; each block's
"Decided" line says how.
Every count below was measured in this run, on origin/main of 12:00 PM PST 2026-11-26.

## Section one: the Polish list

`design/concepts/Pyrelands/version/polish.md` held **54 lines**: 3 proposed entries, 43 bullet lines and 8 sub-lines (the
bullet that only introduces the sub-lines is not counted). Each was read against the code of 2026-11-26.

- **Deleted, 1 line** (stale): the line that said `sc_fire_sense` was removed from the test table and "decided no bar".
  Today `sc_fire_sense` is back in `version/test_table.json` and decides the bar `walk_season_on_the_pyre`.
- **Stay, 53 lines.** Of these, 23 name a change, 29 only record a decision already taken, and 1 is another mod's file.

### The fire and the fire-hawk (3 lines)
- **Decided:** in 0.2.0, by his card of 12:44 PM PST 2026-11-26 ("All five groups (Recommended)").
- **What the player would see:** regrown grass a week after a burn reads nearly all green, not about 60% green; a
  fire-hawk next to a burn no longer gives up on a patch of grass because a firefoam shot once landed in its middle; and
  the small fire-edge details of the walking front (how a lone fire fans out, how far the warning cone reaches, how often
  the fire calls down black rain) are re-tuned.
- **Lines:** the regrowth entry (`RIMMANDRAKE_TUNE_PYRE_REGREEN_TOWARD_NEARLY_ALL_GREEN`), the lone-fire nits of
  2026-11-23, the Codex finding `hawk_discards_bucket_with_usable_fuel`.
- **Size:** small. All three sit in the burn and hawk code that faster fire rewrites anyway.

### The firefoam sprayer (3 lines)
- **Decided:** in 0.2.0, by his card of 12:44 PM PST 2026-11-26 ("All five groups (Recommended)").
- **What the player would see:** a colonist asleep in bed no longer foams a fire beside the bed; an automatic foam shot
  stops when the player switches the foam off; the sprayer's description says that a shield belt blocks it, as it does
  every gun; removing the mod no longer logs a missing class.
- **Lines:** the three sprayer lines of 2026-11-22 and the switch-off finding of the Codex review of 2026-11-24
  (`auto_foam_fires_after_switch_off`; the code is unchanged since `3acf1ad82b`, so it is still true).
- **Size:** small.

### Mod Settings and the words the player reads (2 lines)
- **Decided:** in 0.2.0, by his card of 12:44 PM PST 2026-11-26 ("All five groups (Recommended)").
- **What the player would see:** the watered-ash fertility slider can no longer be set below the dry one; the giant
  furnace-beast tooltip stops promising that existing animals keep their size (they do not: the race def is shared).
- **Size:** small. The conversion rewrites the settings page in any case.

### Words only a modder reads (2 lines)
- **Decided:** in 0.2.0, by his card of 12:44 PM PST 2026-11-26 ("All five groups (Recommended)").
- **What the player would see:** nothing. A code comment and one boot log line still say that each fire lights one cell
  downwind (a fire can light two now), and one comment block is doubled in `RM_BurnKernel.cs`.
- **Size:** small (minutes, inside the faster-fire change).

### Tests that would catch more (13 lines)
- **Decided:** in 0.2.0, by his card of 12:44 PM PST 2026-11-26 ("All five groups (Recommended)").
- **What the player would see:** nothing directly. These make the checks catch faults that today pass unseen: the
  three-skies scene gets a clear-sky ash patch as a control; the fire-hawk scene checks that the hawk picks the larger
  fuel; the burrow test joins the test table; the barn-roof check reads its mod guard; the old season-walk chain and its
  test are deleted; the fire-sense scene reads the log; the season-walk bar's leaf loses its scripted two-week scenario
  (this is the "new words" item above); three scenes stop passing on a build that is broken in a way Codex found (a hawk
  that lights nothing, ullai that never get their job by themselves, a lost inspect line on the furnace-beast); the
  burn-compounds scene reads its control pad at staging; the review script loses its paved-strip stations; a visit's runner
  stops reloading the site before every short check.
- **Lines:** the two proposed entries `RIMMANDRAKE_SHARPEN_BLACK_RAIN_CONTROL_AGAINST_DRY_ASH_WEAR` and
  `RIMMANDRAKE_TEST_FIREHAWK_PICKS_LARGEST_FUEL` (each acceptance test reads exit 1 today, so neither is done), and
  11 lines of 2026-11-21 to 2026-11-25.
- **Size:** medium, as a group: each line is small, and there are thirteen.

### Records of a decision already taken (29 lines)
- **Decided:** nothing to sweep; his card of 12:44 PM PST 2026-11-26 took the five groups that name a change.
- **What the player would see:** nothing. Each line records a check that was removed because no bar needs it, or a
  ticket that was dropped as not worth the touch, with the measurement behind it. There is no change to sweep in. One
  line of this group (the donor grasslands biome name in `PyrelandsTuning.cs`) goes away by itself with the conversion.
  One (the ullai's south view) is his kept art, and his words at his walk were *"They should not be brought up again."*
- **Size:** none.

### Not Pyrelands' file (1 line)
- **Decided:** not swept into Pyrelands; his card of 12:44 PM PST 2026-11-26 took the five groups that name a change.
- The Codex finding `natural_water_never_arms_gentle_burst` is in `src/RimMandrake/ExplosiveGrowth/`. It stays on this
  list until Explosive Growth's own polish list takes it; it is not swept into Pyrelands.

**Recommendation for section one:** sweep in all five groups that name a change (23 lines). Polish never moves a bar, so
none of them adds a pass bar.

## Section two: the deferred capabilities

### Where this run looked, and what each place held

| place | what it held (measured) | deferred capabilities found |
|---|---|---|
| Pyrelands Mechanics (`design/concepts/PyrelandsMechanics/`) | 11 capabilities in `record.json`, 11 bars in `tree.json`, 0 entries in its `version/next_version/README.md`; `./pipe show` reads it OFF | 9 blocks below (the 11 capabilities, with its plumbing in one block) |
| `design/concepts/Pyrelands/version/gaps_sorted.md` | 32 judge gaps in two rounds (14 and 18) and 3 other lines; 0 sorted NEXT VERSION | 0 |
| The vision's list of extras moved later | `vision.md` has no such list (10 lines, none an extra). `record.json` holds 1 scope line that defers (`s_rituals_v2`: the rituals of the Nine go to v2) and 2 capabilities cut (`out`) | 2 blocks (the Struck Glass rite; the cut firebreak and lightning breaker) |
| Open tickets with home `mod:Pyrelands` (`list_home.py list`, run once at 12:05 PM PST, kept in a file) | 4 tickets; also 2 with home `mod:PyrelandsMechanics` | the trade ticket, the fire-clock switch; the black rain ticket (gone to FlowWorks); 2 Mechanics bug tickets (folded into the rite block) |
| Other open tickets whose title names the Pyrelands (queue titles) | 5 capability-shaped: crestfeather art, grass unseen under ash, river steam, wind fire for every biome, Struck Glass rite | 4 blocks (the rite is counted above) |
| The biome sheet, `design/Jawa/worldbuilding/biomes/the_pyrelands.md` | its "Owed" list: 5 lines, all built or bookkeeping; §7 and §8 hold 3 ideas that are not built | 2 blocks (warmth on the hoof; burning a field on purpose); the third, carried fire, is in the Impid block |
| His walk words of 2026-11-13 and 2026-11-24 (OWNER events `1794595450335992387`, `1795575596337863702`, `1795575810695997798`) | 2026-11-13: 10 things he pictured; 7 are built or in 0.2.0, 1 went to FlowWorks, 2 are Tribes blocks (the rite party, trade). 2026-11-24: the walk's points; the pens he asked for are a walk method, not a capability | the rite party and trade blocks |
| `design/RimMandrake/validation_holding/` | 14 files; 0 lines about the Pyrelands | 0 |

His sweep of the ash from the paths (2026-11-13: *"I won't miss having to sweep the ash away from all my paths"*) is
built: ash is vanilla sand on this map, it slows walking, and the vanilla clear-sand job sweeps it.

### From Pyrelands Mechanics (the Deep Desert Tribes)

**Why none of these goes inside Pyrelands 0.2.0.** The Deep Desert Tribes are a campaign faction of the Utinni tier
(a vanilla tribe reskinned by `src/RimUtinni/UtinniPatches`). Pyrelands is a RimMandrake-tier biome that must be whole on
its own, with no other mod's people (vision line 8). So every Tribes capability needs the separate mod. His card of
2026-11-13 started that mod only after Pyrelands 0.1.0 passed: *"Own mod, own version, later"*. Pyrelands 0.1.0 passed on
2026-11-24, so that condition is met; the mod is switched off by `./pipe` today.

#### The rite party: the Tribes come with a burn, light it, harvest behind it and leave
- **Decided:** not in 0.2.0, by his card of 12:44 PM PST 2026-11-26; his words: *"We are not ready to do faction work yet. The tribes sleep until we start faction work much later."*.
- **What the player would see:** now and then a scheduled burn arrives with a small file of Tribes walking in off the
  sand, with a letter that names them; the grass catches where they stand; they pick scorch-fruit only on burned ground,
  never in the flames, and walk off the map with what they picked.
- **His words:** 2026-11-05, by card, the face of the Tribes: "The rite party".
- **Needs:** the separate mod. The code exists (`PyrelandsFireRite.cs`, `LordJob_RUT_FireRite.cs`, the harvest duty) but
  has never been proven live, and two open tickets name faults in it (`FIRE_RITE_FIX_DEFENDERS_MISS_THE_WAR`,
  `RITE_HARVEST_FIX_PICKS_PAST_FULL`). The scenes are scripted small since 2026-11-24.
- **Size:** large: a whole mod's first live proof.
- **Recommendation:** later, as Pyrelands Mechanics 0.1.0, beside or after Pyrelands 0.2.0, with its own walk.

#### The flame-harvest visit
- **Decided:** not in 0.2.0, by his card of 12:44 PM PST 2026-11-26; his words: *"We are not ready to do faction work yet. The tribes sleep until we start faction work much later."*.
- **What the player would see:** with a big fire already standing, a peaceful Tribes group walks in to the burn, picks
  in the black and carries it off.
- **His words:** 2026-11-05, by card: "Pick and carry off".
- **Needs:** the separate mod; built, not proven.
- **Size:** medium.
- **Recommendation:** later, with Pyrelands Mechanics 0.1.0.

#### The fruit defence: warned, then driven off
- **Decided:** not in 0.2.0, by his card of 12:44 PM PST 2026-11-26; his words: *"We are not ready to do faction work yet. The tribes sleep until we start faction work much later."*.
- **What the player would see:** a colonist who picks scorch-fruit in the scar the Tribes are harvesting gets a message
  naming them, then is attacked until it leaves; no goodwill is lost and no raid comes. Fruit elsewhere is not defended.
- **His words:** 2026-11-05: *"If you try to pick the scorchfruit during one of their events, they issue warnings, then
  attack to drive you away (not a full blown raid, just defense of the fruit)."*
- **Needs:** the separate mod; not built.
- **Size:** medium.
- **Recommendation:** later, with Pyrelands Mechanics 0.1.0.

#### Attack them and they raid you back
- **Decided:** not in 0.2.0, by his card of 12:44 PM PST 2026-11-26; his words: *"We are not ready to do faction work yet. The tribes sleep until we start faction work much later."*.
- **What the player would see:** an open attack on the Tribes turns them hostile, and their raids come in the days after,
  maybe again later.
- **His words:** 2026-11-05: *"Attacking them overtly makes them raid you back of course, and they may continue to do so
  later."*
- **Needs:** nothing new: vanilla faction hostility. Only its bar and its check, in the separate mod.
- **Size:** small.
- **Recommendation:** later, with Pyrelands Mechanics 0.1.0.

#### The arson-justice raid, and the rule that nothing an animal does is blamed on you
- **Decided:** not in 0.2.0, by his card of 12:44 PM PST 2026-11-26; his words: *"We are not ready to do faction work yet. The tribes sleep until we start faction work much later."*.
- **What the player would see today:** the built code counts the colony's own fires and sends a short Tribes raid when
  the count is high. His words remove it: no count, no blame.
- **His words:** 2026-11-05: *"Actually just remove the count thing... that's a mechanic we don't even need. They can't see
  you all the time. And never do they react to an animal doing something to blame the player."*
- **Needs:** the removal of the raid in the separate mod (`IncidentWorker_FireRaid.cs`).
- **Size:** small.
- **Recommendation:** drop the raid; the removal and the no-blame bar go with Pyrelands Mechanics 0.1.0.

#### Trade with the Tribes, and their share
- **Decided:** not in 0.2.0, by his card of 12:44 PM PST 2026-11-26; his words: *"We are not ready to do faction work yet. The tribes sleep until we start faction work much later."*.
- **What the player would see:** the Tribes offer trade, and leaving them their share of the burn keeps the peace;
  taking it costs something the player can read.
- **His words:** 2026-11-13: *"But then the Deep Tribes come: learning to watch rather than confront. Offer trade and leave
  them their share, and you'll be ok."*
- **Needs:** a design pass first (what they buy and sell, what "their share" is, what taking it costs), then the build in
  the separate mod (ticket `RIMMANDRAKE_BUILD_DEEP_TRIBES_TRADE_CODE_SAYS_NO_TRADE`; the code today says "No trade, no quest
  hook, no scorch-fruit handout").
- **Size:** large: an economy design and a build.
- **Recommendation:** later, as Pyrelands Mechanics 0.2.0, after its 0.1.0 shows the rite working.

#### The Impid fire-callers, sacred fire carried home, the cairns and the harvest camps
- **Decided:** not in 0.2.0, by his card of 12:44 PM PST 2026-11-26; his words: *"We are not ready to do faction work yet. The tribes sleep until we start faction work much later."*.
- **What the player would see:** the Tribes' fire-callers lead the burns; the Tribes carry living fire away to their
  hearths; burn-scheduling cairns and moving harvest camps stand on the map.
- **His words:** none of his own. These are the biome sheet's canon (§8) and Mechanics' capability `inv_impid_fire_callers`.
- **Needs:** the separate mod; new pawns' roles, new buildings, new art; not built.
- **Size:** large.
- **Recommendation:** later, in a later Pyrelands Mechanics version.

#### The furnace-beast may eat thornvine
- **Decided:** not in 0.2.0, by his card of 12:44 PM PST 2026-11-26; his words: *"We are not ready to do faction work yet. The tribes sleep until we start faction work much later."*.
- **What the player would see:** nothing today. The patch makes a plant named `Plant_Thornvine` edible for the
  furnace-beast. No file under `src/` defines that plant, and the Pyrelands roster does not hold it.
- **Needs:** nothing.
- **Size:** none.
- **Recommendation:** drop the patch when Pyrelands Mechanics is next built.

#### The plumbing: finding the Tribes, their letters, their Mod Settings, the rite door in Pyrelands
- **Decided:** not in 0.2.0, by his card of 12:44 PM PST 2026-11-26; his words: *"We are not ready to do faction work yet. The tribes sleep until we start faction work much later."*.
- **What the player would see:** the letters that name the Tribes, and three switches (rite, visit, fruit defence) in the
  separate mod's Mod Settings. Pyrelands keeps its one door for the rite (`PyrelandsFireRiteHook`), already in 0.1.0.
- **Needs:** the separate mod; built.
- **Size:** small.
- **Recommendation:** later, with Pyrelands Mechanics 0.1.0.

### From the Pyrelands' own record, tickets and sheet

#### The crestfeather gets its own picture
- **Decided:** in 0.2.0, by his card of 12:44 PM PST 2026-11-26 ("Both (Recommended)"), bar `crestfeather_has_its_own_look`.
- **What the player would see:** the pristine crestfeather from a hunted fire-hawk shows a picture of its own. Today it
  borrows vanilla's thrumbo horn, tinted (`RM_PristineFirehawkCrestfeather.xml` reads `Things/Item/Special/ThrumboHorn`).
- **His words:** 2026-11-13: *"That gives a great reason for players to hunt the Firehawk."*
- **Needs:** one render from the art list that exists, a judge, `art install`, and a texture path change. The same ticket
  (`RIMMANDRAKE_JUDGE_PYRE_POST_SHEET_ART_CRESTFEATHER_A_HORN`) also has the 17 pictures added since his art sheet of
  2026-10-16 judged.
- **Size:** small.
- **Recommendation:** in 0.2.0. It is the reward of a hunt he wanted, and it shows a borrowed horn today.
- **PROPOSED bar `crestfeather_has_its_own_look`:** A pristine crestfeather taken from a hunted fire-hawk shows a picture
  of its own, a fire-hawk's feather, never a borrowed horn.

#### The grass is still drawn under the ash
- **Decided:** in 0.2.0, by his card of 12:44 PM PST 2026-11-26 ("Both (Recommended)"), bar `grass_still_seen_under_ash`; the first step is one live look on a fresh map after an ash fall.
- **What the player would see:** after ash falls, the grass that still stands shows under the ash. The open ticket
  (`RIMMANDRAKE_SHOW_PYRE_GRASS_UNDER_ASH_COVER_COUNTED_UNSEEN`, filed 2026-11-17) says that the map then read as bare grey
  ash while 81% of open ground held grass.
- **His words:** none on this point. His picture of 2026-11-13: *"The grass grows so swiftly, you only barely know what
  bare ash looks like save for right after a fire."*
- **Needs:** first one live look on a fresh map after an ash fall, because nobody has checked it since his walk; then a
  fix in the ash-cover drawing if it is still true.
- **Size:** small to look; the fix is UNMEASURED until the look.
- **Recommendation:** in 0.2.0, the look first. If it is still true, it is a defect against his own picture.
- **PROPOSED bar `grass_still_seen_under_ash`:** After ash falls on a Pyrelands map, the grass that still stands is drawn
  under the ash, so the player sees grass where it grows and bare ash only where it does not.

#### The "Fire clock" switch does what its tooltip says
- **Decided:** not in 0.2.0: its live check waits with Pyrelands Mechanics, which sleeps by his card of 12:44 PM PST 2026-11-26.
- **What the player would see:** with the Pyrelands "Fire clock" switch off, no Tribes fire raid, flame harvest or fire rite
  comes, as the tooltip promises. The ticket `FIRE_CLOCK_FIX_RAIDS_IGNORE_THE_SWITCH` (home `mod:Pyrelands`) found that only
  the fire front read the switch. The fix is built: the raid and the harvest now read it
  (`IncidentWorker_FireRaid.cs:41`, `IncidentWorker_FlameHarvest.cs:40`, read 2026-11-26). Only its live check was never run.
- **Needs:** one live check, on a map with Pyrelands Mechanics loaded. It belongs with Pyrelands Mechanics 0.1.0, which
  loads the Tribes; Pyrelands' own small list does not.
- **Size:** small.
- **Recommendation:** later, as a check in Pyrelands Mechanics 0.1.0. Nothing is left to build in Pyrelands.

#### The Struck Glass rite
- **Decided:** later, not in 0.2.0, by his card of 12:44 PM PST 2026-11-26 ("Keep all three later (Recommended)").
- **What the player would see:** a ring of glass sand stamped apart in a lightning storm calls down one huge strike at a
  random place on the map.
- **His words:** in its ticket (`PYRELANDS_STRUCK_GLASS_RITE_BUILD_1`): *"Struck Glass. Make a ~ring of the lightning
  glass, and then during any lightning storm step on them violently to break them."*
- **Needs:** it was built, then removed (`f100b170dc`, "Defer the Nine's biome rituals to v2"); `record.json` scope
  `s_rituals_v2` defers all such rituals to v2. Its rite lives in the Rites mod of the Utinni tier.
- **Size:** medium.
- **Recommendation:** later, with the other rituals of the Nine.

#### Animated steam over the rivers
- **Decided:** not in 0.2.0 and not Pyrelands work (FlowWorks); his card of 12:44 PM PST 2026-11-26 took none of the five ideas in.
- **What the player would see:** steam rises from the rivers of the Pyrelands, as decoration.
- **His words:** 2026-09-02: *"could we add animated steam rising from the river? That is an amazing idea, file a ticket on
  that alone!"*
- **Needs:** nothing in Pyrelands. It is built in FlowWorks (`src/RimMandrake/FlowWorks/Source/ManyWaters/RiverSteamHook.cs`)
  with a Utinni patch; its ticket `RIVER_STEAM_ANIMATION_1` waits on a live proof.
- **Size:** none here.
- **Recommendation:** later, with FlowWorks.

#### The wind-driven fire for every biome
- **Decided:** not in 0.2.0 and not Pyrelands work; his card of 12:44 PM PST 2026-11-26 took none of the five ideas in.
- **What the player would see:** a grass fire in any of our biomes walks with the wind, as on the Pyrelands.
- **Needs:** ticket `RIMMANDRAKE_GENERALIZE_WIND_FIRE_ALL_BAROQUE_BIOMES_NEXT_VERSION`. The conversion in 0.2.0 already
  makes the Pyrelands' carry act wherever its own grasses or ash burn. Other biomes are held, and each takes the rule when
  it advances.
- **Size:** medium, and outside this mod.
- **Recommendation:** later.

#### Warmth on the hoof: furnace-beasts as a caravan's hearth
- **Decided:** later, not in 0.2.0, by his card of 12:44 PM PST 2026-11-26 ("Keep all three later (Recommended)").
- **What the player would see:** a caravan that travels with furnace-beasts keeps warm on the way to the cold country.
- **His words:** none of his own; the biome sheet §7: *"a furnace-beast herd is a walking hearth; caravans route with them
  toward the cold country."*
- **Needs:** world-map caravan code (new), and a cold country to travel to; the cold biomes are held today.
- **Size:** large.
- **Recommendation:** later.

#### Burning a field on purpose ("ash-flush farming")
- **Decided:** later, not in 0.2.0, by his card of 12:44 PM PST 2026-11-26 ("Keep all three later (Recommended)").
- **What the player would see:** an order to burn a field, so it regrows fast with the fresh-burn bonus that already exists.
- **His words:** none of his own; the biome sheet §7.
- **Needs:** a burn order and a way to hold the fire's edge. The firebreak floor that held the edge was cut (below), so a
  burn order today would have no brake but the colony's own walls (`GUIDING_PRINCIPLES.md` entry 3 asks for a brake the
  player can build).
- **Size:** medium.
- **Recommendation:** later, and only with a design of its brake.

#### The firebreak floor and the lightning breakers (cut)
- **Decided:** they stay cut; no card raised them.
- These were built and then cut: the firebreak by a delegated call he asked for, the lightning breakers and fulgurite by
  his word, 2026-10-16: "Drop both".
- **Recommendation:** drop (they stay cut). Listed only so that nothing deferred is left out.

## The table

| candidate | size | recommendation |
|---|---|---|
| Polish: the fire and the fire-hawk | small | in 0.2.0 |
| Polish: the firefoam sprayer | small | in 0.2.0 |
| Polish: Mod Settings and the words the player reads | small | in 0.2.0 |
| Polish: words only a modder reads | small | in 0.2.0 |
| Polish: tests that would catch more | medium | in 0.2.0 |
| Polish: records of a decision already taken | none | nothing to do |
| Polish: the Explosive Growth line | n/a | not Pyrelands' |
| The crestfeather's own picture | small | in 0.2.0 |
| Grass still drawn under the ash | small (look first) | in 0.2.0 |
| The "Fire clock" switch's live check | small | later, Pyrelands Mechanics 0.1.0 |
| Tribes: the rite party | large | later, Pyrelands Mechanics 0.1.0 |
| Tribes: the flame-harvest visit | medium | later, Pyrelands Mechanics 0.1.0 |
| Tribes: the fruit defence | medium | later, Pyrelands Mechanics 0.1.0 |
| Tribes: they raid back when attacked | small | later, Pyrelands Mechanics 0.1.0 |
| Tribes: the arson-justice raid | small | drop (his word); its removal with Pyrelands Mechanics 0.1.0 |
| Tribes: trade and their share | large | later, Pyrelands Mechanics 0.2.0 |
| Tribes: Impids, carried fire, cairns, camps | large | later |
| Tribes: the thornvine patch | none | drop |
| Tribes: the plumbing | small | later, Pyrelands Mechanics 0.1.0 |
| The Struck Glass rite | medium | later, with the rituals of the Nine |
| Steam over the rivers | none here | later, FlowWorks |
| Wind fire for every biome | medium | later |
| Warmth on the hoof | large | later |
| Burning a field on purpose | medium | later, with its brake |
| The firebreak and the lightning breakers | none | drop (cut) |

**How large 0.2.0 becomes:** what he took (three medium changes and one large) plus the three small items recommended in
part one, then everything recommended here: four small and one medium group of polish, and two small capabilities. That
is about a quarter more work than what he took [guess ~60%]. It is still one version and one walk, and the two new pass
bars proposed here are small to show.
