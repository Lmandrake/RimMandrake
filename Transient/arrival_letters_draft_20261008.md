# Arrival letters — DRAFT for the owner's review (2026-10-08)

Item: `BIOME_ARRIVAL_LETTERS_ALL_1` (DESIGN_PASS X-6 / FV-5). **Every text below is a PLACEHOLDER written by an
agent**, shipped so the machinery is live, and flagged for your review. Nothing here is new lore: each line is
read off the biome's own description, its definition sheet's "always true" list, or a mechanic that ships. Edit
freely; the shipped copy is the `<letterText>` in each BiomeDef (search `BIOME_ARRIVAL_LETTERS_ALL_1`).

RM tier: plain reads, no narrator, no campaign names. The Utinni voice layer can replace any of them later, the
way `BiomeArrivalLetters_TheSump.xml` does for the Sump. Fires once per save, the first time a gravship lands in
the biome (EnvironmentalHazards setting `biomeArrivalLettersEnabled`).

**Which biomes.** Only biomes that declare a heat kind (`RM_SunHeatExtension`) AND have a bedazzle review on
file. That is 10 of the 11 with a heat kind. **Left out: the Scald** (`RM_TheScald`): only a floor sitting
*agenda* exists (`the_scald_floor_sitting_agenda_2026-10-02.md`), no held sitting. The Sump already has its letter.

**The heat line** in each letter follows the biome's heat kind and names the gear that answers it
(`SHADE_GEAR_FAMILY_1`: parasol, shade tent, sun shield):
- overhead: shade from above works (roof, parasol, shade tent).
- low sun: a roof does nothing; only a lee shadow works (wall, rock, sun shield); a parasol barely helps.
- ambient: no shade helps; insulation or a closed room.

---

## The Fever Wood (`RM_FeverWood`, ambient) — first, per FV-5
Read the water before you read anything else. The still black pools are one creature, not many: whatever rises
from one has come from all of them. A tentacle that sets down a gift and goes is no danger until you hit it; hit
it and the pools remember. The kurreth carry off anything they can lift, so leave nothing light outside. When
the oil-boil haze hangs over the water, one spark flashes it. The heat here is in the wet air itself: shade does
nothing, so dress against it or stay in a closed room.

Sources: DESIGN_PASS FV-5 reads; `RM_MapComponent_TentacleWatch` (porter angered forever), `RM_KurrethTheft`,
`RM_OilBoil`; heat kind ambient.

## The Rust Cathedral (`RM_RustCathedral`, overhead)
The walls are the treasure here, and the maze is built on purpose. The machines that garrison it guard their
ground and do not hunt; give them room and they give you yours. The hum is everywhere, and it changes as you
work: listen to it, because it is reacting to you. Take from the sacred walls and the place turns against you.
Dig too deep and very bad things happen. The heat comes straight down: a roof, a parasol or a shade tent answers it.

Sources: `the_rust_cathedral.md` §5 always-true, §P; settings (hum-mood system, sacred wall tier, sacrilege).

## The Webwork (`RM_Webwork`, overhead)
The silence is not peace; it means something owns this jungle. The web is a nervous system: touch it anywhere
and you are felt everywhere near it. The things that hunt here cannot stand direct sun, so clearings are the
only safe ground, and fire is the only thing that drives them back. There is no surface water: the river is
inside the plants. The heat comes straight down: a roof, a parasol or a shade tent answers it.

Sources: `the_webwork.md` always-true; BiomeDef description.

## The Forge (`RM_TheForge`, ambient)
The mountain runs on a cycle of fire and water, and the warning comes before each turn. Rain here falls
boiling. Gas washes down and catches. Lava cools into a crust you can walk, until the melt comes back and takes
whatever stands on it. The heat is in the air and the steam: shade does nothing here, so dress against it or
stay in a closed room.

Sources: TheForge settings (weather-pulse bursts, grand cycle, gas wash, boiling-rain flooding, crust,
melt-back, warning letters); BiomeDef description.

## The Cracked Lands (`RM_FloodedCanyon`, low sun)
Water comes rarely and it comes down the canyon as a wall: it drowns what stands in its path. Chimes ring ahead
of it in stages; when you hear them, get out of the cut. When it drains it leaves real soil in the shade, the
one dryland ground you can farm. The sun owns the flats. It sits low, so a roof does nothing here: only a
lee shadow helps, a canyon wall, a rock face, or a sun shield to stand behind. A parasol barely helps.

Sources: `the_cracked_lands.md` always-true; FloodedCanyon settings (chimes in stages, wall of water hurts).

## The Long Shade (`RM_LongShade`, overhead)
Nothing lives in the light here and nothing survives long out of shelter. Every stone throws a long shadow;
cross between them as a sprint, rest, then dash. The gaps between the shadows are the only map that matters.
When you must go out into the sun, for graves or salvage, take shade with you. The heat comes from above:
a roof, a rock's shadow, a parasol or a shade tent all answer it.

Sources: BiomeDef description; LongShade settings (the Long Carry); heat kind overhead (roofs AND cast shade).

## The Weeping Stones (`RM_WeepingStones`, low sun)
Water is on the cold, shaded faces: follow the black streaks down the pale rock. Every pool is a working thing,
part stone, part machine, part crowd of everything that drinks, and the truce at the water holds only while
there is enough. The ridges are bright and dry and the sun sits low: a roof does nothing here, only a lee
shadow does, a rock face or a sun shield to stand behind. A parasol barely helps.

Sources: `weeping_stones.md` always-true; BiomeDef description.

## The Pyrelands (`RM_Pyrelands`, overhead)
This grass burns on its own schedule, and somewhere on this ground it is always burning. It grows back faster
than anything can eat it and dries within days, and the first dry storm sets it off. Keep a firebreak. The
ash falls for days after a big burn and the rain comes down black with it. Scorch-fruit opens only in the burn
and spoils within a day: the harvest belongs to whoever walks the flame line. The heat comes straight down: a
roof, a parasol or a shade tent answers it.

Sources: `the_pyrelands.md` always-true; BiomeDef description; Pyrelands settings (standing burn line).

## The Stillsand (`RM_Stillsand`, low sun; overhead when the sun stands high)
The sun here never moves, so nothing tracks it: everything owns a shadow, is buried, or carries its own. Do
not spill blood on the sand. Water poured out here makes things bloom. Where the sun sits low a roof does
nothing: only a lee shadow helps, a rock or a sun shield to stand behind. Nearer the point under the sun, where
it stands high, a roof works again. A parasol barely helps out on the low-sun sand.

Sources: BiomeDef description; Stillsand settings (blood on the sand wakes the zuurrik, poured water blooms);
`STILLSAND_SUN_FROM_LATITUDE_1` (overhead above 55 degrees elevation).

## The Greentide (`RM_Greentide`, ambient)
The steam never lifts and everything grows fast enough to watch: the green will grow into your doors, and the
mud is deep enough to swallow a boot, a crate or a careless step. Dark brings roots, light brings leaves, and
only dry heat pushes them back. Something patient waits in the mud. The heat is in the wet air itself: shade
does nothing, so dress against it, run a dry-air blower, or stay in a closed room.

Sources: `the_greentide.md` always-true; BiomeDef description; Greentide settings (mire hazard, vurrak ambush);
`RM_DryAirBlower`.
