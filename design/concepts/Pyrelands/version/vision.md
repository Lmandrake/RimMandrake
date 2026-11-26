# Pyrelands 0.1.0: the vision

Written only from the root paragraph he approved (`record.json` root, OWNER:1793950669508519029), `sheet.md` and his quoted words there (including his 2026-11-13 grass ruling and card). No sentence is inferred. Convergent and Divergent are measured against this text.

1. The Pyrelands are a genetically engineered grass savanna that has burned for millennia and is burning still.
2. Almost all the ground is deep ash, quite fertile wherever water reaches it (ordinary crops find it sowable dry, about 70%, and very fertile watered, about 140%: the root he approved, his card 2026-11-07 "Keep 70%, sowable", and gap g13's fix that his card 2026-11-15 "Fix all 12 in 0.1.0" took), and a lot of free-flying ash blows across it like snow.
3. A line of grass fire walks the map with a scorched trail behind it and never goes out for long.
4. The biome's own grasses grow swiftly even on dry-looking ash, faster and with a gentle burst where watered, so a burn is largely green again within about a week.
5. Behind the front the fire offers some solace: scorch-fruit comes up rapidly in the fresh scar and rots fast, fresh burns grow crops faster for a few days, and black rain adds to that bonus instead of washing it away.
6. The animals are the fire's own cast: a fire-hawk carries a burning twig ahead of the blaze, ullai herds graze old burns, the ashwallow dives underground as the front arrives, the flamefang's bite carries venom, and the giant furnace-beast warms anyone near it and sets alight the grass it sleeps on.
7. The sky brings ash fall, cinderfall and black rain, never ordinary rain, and ruins stand blackened.
8. The biome is whole on its own, with no other mod's plants or animals, and a firefoam sprayer lets a colonist walk into the burn for the fruit and back out.
9. It is judged first on a fresh map in ordinary play: the burn line walking across deep ash, scorch-fruit coming up right behind it, and the grass greening a few days later.
10. There is no worldgen of our own; the vanilla world-placement switch ships off, labelled unsupported.

## 0.2.0: the vision delta (MINOR, opened 2026-11-26 on his two scope cards)

Divergent additions, each from his own words and taken in by his cards of 2026-11-26, and the conversion that
`GUIDING_PRINCIPLES.md` entry 1 owes now that the mod advances. Lines 1 to 10 above stay as they are. Every 0.1.0 bar is kept.

11. The fire catches and runs (his walk of 0.1.0, 2026-11-24: *"The fire barely catches, to be honest. I had expected faster
    spread."* and *"next version puts more aggressive fire"*). A spark in standing grass takes; on the day it is lit it is a
    front the player must answer; the head walks downwind faster than 0.1.0's, and it is still the walking line of line 3,
    never a flood (bar `fire_catches_and_runs`).
12. Roofed grass goes where the player can see it go (his walk, 2026-11-24: *"the grass just suddenly all dies at the same
    time. Kinda weird. And it doesn't turn into dead grass, just... barren nothing."*). It wilts, the plants die at different
    times, and each leaves dead grass that the colonists can cut and that crumbles away; nothing reaches the error log
    (bar `roofed_grass_declines_visibly`).
13. A choking smoke sometimes comes as its own weather (his walk of 2026-11-13: *"the choking smoke that sometimes come as
    its own weather"*). It reads as smoke, hampers a colonist out in it with a readable sign, spares one under a roof, puts
    out no fire, and black rain stays the only rain of line 7 (bar `pyre_smoke_weather_chokes`).
14. Each mechanic works by its conditions, never by the biome (his cards of 2026-11-21). Mod Settings holds a plain on/off
    for each mechanic, default on, with no biome in it (bar `mechanics_switch_plain_no_biome`).
15. The crestfeather has a look of its own (his words of 2026-11-13: *"That gives a great reason for players to hunt the
    Firehawk."*). A pristine crestfeather from a hunted fire-hawk shows a fire-hawk's feather, never a borrowed horn (bar
    `crestfeather_has_its_own_look`).
16. The grass shows under the ash (his picture of 2026-11-13: *"The grass grows so swiftly, you only barely know what bare
    ash looks like save for right after a fire."*). After ash falls, standing grass is drawn under it, and bare ash shows
    only where no grass stands (bar `grass_still_seen_under_ash`). **The first step of this work is one live look on a
    fresh map after an ash fall**, on the 0.1.0 build, before any code: the first run of `sc_grass_seen_under_ash`. The
    fix, and its size, wait for that look.

### What decided the scope

- His card of 11:50 AM PST 2026-11-26 (OWNER:1795722774284846701): faster fire, roofed grass that dies where the player can see it
  and the smoke weather (his words: *"Certainly all of these and likely more too"*); the conversion goes with them (his
  pick: "With the features (Recommended)").
- His card of 12:44 PM PST 2026-11-26 (OWNER:1795725937729027309): all five polish groups ("All five groups (Recommended)"); the
  crestfeather picture and the grass under the ash ("Both (Recommended)").
- The Conductor's call (brief of this run): the three Problems of the scope page's part one, and its work that adds no
  bar, stay with the open version, because a Problem is a defect.

### Work in 0.2.0 that adds no bar

From the scope page's part one (`next_version/scope_proposal_0.2.0.md`):
- the roofed grass exception (`Exception ticking RM_FE_Plant_EmberGrass`), fixed in the kill path that bar
  `roofed_grass_declines_visibly` rewrites; its scene reads the log;
- the one load warning `Tried to get CurKindLifeStage from humanlike pawn Flea`: first a stack trace on a debug build,
  then a guard in the file the trace names (FlowWorks `RM_Swim.cs` is the guess, about 75%; if so the guard goes in
  FlowWorks with its own test);
- the startup config errors of the Pyrelands small list: a startup logs no `Config error` line. The first (the VEF type
  that dropped `RM_GargantuanLithops`) is fixed; the four weapon-money errors of `RUT_Jawa_Homestead_*` and
  `RUT_Jawa_Junkers_Specialist` are fixed in UtinniPatches' defs (`src/RimUtinni/UtinniPatches`); the three on vanilla defs
  are traced first, and fixed where the trace names ours;
- the three caller scenario tests whose callers the conversion rewrites (`T_SCENARIO_FIRE_DUTY`,
  `T_SCENARIO_FIRE_NO_FLEE`, `T_SCENARIO_BURROWER_FLEES`);
- new words for the season-walk bar `walk_season_on_the_pyre`: the leaf loses its scripted two-week scenario, its
  `oracle_proposed` and `wall_expect_h` (one sentence in `tree.json`; it re-runs the Cold Reader exam once). It is the same
  change as the polish line of 2026-11-24 below.

The Polish list, 23 lines in five groups, by his card. Each line stays on `polish.md`; the builder that does a line
removes it there. Polish never moves a bar.

**The fire and the fire-hawk (3 lines):**
- regrown grass a week after a burn reads nearly all green (`RIMMANDRAKE_TUNE_PYRE_REGREEN_TOWARD_NEARLY_ALL_GREEN`);
- the lone-fire nits of 2026-11-23 (`RIMMANDRAKE_WIDEN_PYRE_LONE_FIRE_INTO_A_FRONT`): diagonal-wind anchor reads, the
  model's rounding of carry ages, a lane read as outermost after a reload, the warning cone, the count of black rains
  the mod calls down;
- the hawk no longer rejects a whole patch because foam lies on its central cell (`hawk_discards_bucket_with_usable_fuel`,
  `RM_FireHawkKernel.cs`).

**The firefoam sprayer (3 lines):**
- the sprayer's description says that a shield belt blocks it;
- the nits of 2026-11-22: an awake check (a colonist in bed foams no fire), the closures per gated tick, the repeated
  Bursting test, an ExposeData on the MapComponent (removing the mod logs no missing class), the checkbox indent;
- an automatic foam shot in its warmup stops when the player switches the foam off (`auto_foam_fires_after_switch_off`,
  `PyrelandsFoamPath.cs`).

**Mod Settings and the words the player reads (2 lines):**
- the watered-ash fertility slider can no longer be set below the dry one (`RIMMANDRAKE_NOTE_PYRE_FERTILITY_CAP_FLATTENS_SLIDER_CORNERS`);
- the giant furnace-beast tooltip stops promising that existing animals keep their size (`giant_tooltip_misstates_existing_animals`).

**Words only a modder reads (2 lines):**
- `MapComponent_BurnLine.cs` comments that a carried fire lights one cell, and `RM_BurnKernel.cs` has two doubled
  `<summary>` blocks (blind cycle 6);
- `FireEcologyHook.cs`'s boot log line says each fire lights one cell downwind.

**Tests that would catch more (13 lines):**
- `RIMMANDRAKE_SHARPEN_BLACK_RAIN_CONTROL_AGAINST_DRY_ASH_WEAR`: `sc_three_skies` gets a clear-sky ash patch as its control;
- `RIMMANDRAKE_TEST_FIREHAWK_PICKS_LARGEST_FUEL`: `sc_firehawk` stages two fuel piles and expects the larger;
- `selftest_pyrelands_burrow_beats_dash.py` joins the test table as support of `ashwallow_dives_unharmed`;
- `T_DEFS_OFFLINE`'s `furnace_spares_its_barn_roof` asserts the extension's MayRequire id;
- the chain `walk_season`, its parts and `selftest_pyrelands_walk_bed_resume.py` are deleted;
- `sc_fire_sense`'s log-clean clause gets a component that reads it;
- `tree.json`'s walk leaf loses its scripted `scenario`, `oracle_proposed` and `wall_expect_h` (the new words above);
- `hawk_drop_can_light_nothing_and_pass`: the hawk scene reads that the drop lit a fire;
- `ullai_scene_bypasses_wild_job_giver`: the ullai scene lets the think tree give the follow-burn job;
- `furnace_inspect_status_can_disappear_and_pass`: a check reads the furnace-beast's inspect line through the game's own call;
- `sc_burn_compounds` reads its control pad C at staging;
- `human_review.py` loses its paved-strip stations (`RIMMANDRAKE_DROP_PYRE_REVIEW_PAVED_STATIONS`);
- the next visit's runner groups short chains instead of reloading the site before each one
  (`RIMMANDRAKE_SHARE_PYRELANDS_SITE_LOAD_BETWEEN_SHORT_CHAINS`).

### Not in 0.2.0

- The black rain that fills the moat and the tanks: FlowWorks work, by his first card
  (`RIMMANDRAKE_BUILD_BLACK_RAIN_FILLS_MOATS_TANKS_STAY_DRY`).
- Every capability of the Deep Desert Tribes (Pyrelands Mechanics). His words on the second card: *"We are not ready to
  do faction work yet. The tribes sleep until we start faction work much later."* Nothing in 0.2.0 needs Pyrelands
  Mechanics; the live check of the "Fire clock" switch waits with that mod.
- The Struck Glass rite, burning a field on purpose and the warmth of a caravan: later, by his second card ("Keep all
  three later (Recommended)").
- Steam over the rivers (FlowWorks) and wind fire for every biome (each biome mod as it advances): not Pyrelands work.
- The two scenario tests whose callers 0.2.0 does not touch (`pyre_wetroots_season`, `pyre_furnace_heat_cap`).

### Each converted mechanic: its conditions, its brake, its load

From `design/specs/2026-11-21-guiding-principles/conversion_list.md`, section Pyrelands. The biome keeps its data: its
weather table, the odds of its standing burn, its roster and the arrivals it keeps out (rows C7, code 6, code 13), read
from its own defs and extensions, never from a list of defNames in code.

| row | mechanic | conditions it reads | in-world brake (entry 3) | load on every map (entry 5) |
|---|---|---|---|---|
| code 2, R14 | an ashwallow dives from fire | a fire front near the ashwallow | none needed (it does not spread) | a job check per ashwallow; nothing where none lives |
| code 3 | the wind carries the fire | a free-standing fire on ash ground or in the biome's own grasses | spent fuel, black rain, bare ground, sand and paved firebreaks, firefoam | one cheap test per fire; vanilla fire elsewhere is untouched |
| code 3 | the standing burn and the fire clock | biome data: the biome's own fire odds, read from its def | the same brakes | nothing on a map whose biome holds no fire odds |
| code 4 | fire ecology (ash, scorch-fruit, the fresh-burn bonus) | a fire that burns out on ash ground or in the biome's grasses | the fruit rots fast; the bonus fades with days | rolls only on such fires |
| code 5 | ash builds up on sand | ash falling on sand | the ash falls only in ash weather; colonists sweep it | only while ash falls |
| code 6 | no ordinary rain | biome data: the weather table | not a spreading mechanic | none |
| code 7 | herd thirst | a herd animal of the cast and the water it can reach | water runs out where it is drunk | a check per such herd |
| code 8 | a person steps away from fire | fire on or next to the person's cell | none needed | a check per person only while a fire burns on the map |
| code 9 | an urgently hungry colonist eats before fire duty | urgent hunger and fire on the map | none needed | a think-tree check only while a fire burns |
| code 10, 11 | the per-biome gate and "Enable outside the Pyrelands biome" | removed; the master "Mod enabled" stays (the Conductor's call of 2026-11-25), and each mechanic has its own plain on/off, default on | | |
| code 12 | the ash field | the ash ground's own terrain extension | | the scan it already runs |

What 0.2.0 does not change: the burn stays the line of line 3 (bars `burn_line_walks`, `fire_walks_with_wind`), and the
grass greens behind it (line 4). The smoke is a real harm with a readable sign (entry 4), and its weather is biome data.
Mod Settings: every 0.1.0 switch stays except the cross-biome switch and its three sub-settings, which go: each
mechanic's own plain on/off takes their place. Most mechanics have one already (`burnLineEnabled`, `windCarriesFireEnabled`,
`burrowOnFireEnabled`, `ashfallAccumulationEnabled` and the others); three get one now: herd thirst, the step away from
fire, and the meal before fire duty (today they ride only the master and the per-biome gate). Also new: a "Fire pace" slider
(default the shipped faster pace, its low end 0.1.0's pace), and the smoke weather's on/off and how often it comes.
Defaults equal the shipped behaviour.
