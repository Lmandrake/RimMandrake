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

## 0.2.0: the vision delta (MINOR, opened 2026-11-26)

Divergent additions, each from his own words, and the conversion that `GUIDING_PRINCIPLES.md` entry 1 owes now that the
mod advances. Lines 1 to 10 above stay as they are. Every 0.1.0 bar is kept.

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
