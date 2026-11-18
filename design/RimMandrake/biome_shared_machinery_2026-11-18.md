# Shared biome machinery, seen from the ship

**A first draft from a light read.** Three biomes were read deeply for this (the Fever Wood, the Greentide, the
Abyss; their designs are in `design/concepts/<Biome>/design.md`). The other twenty were read only as page one of
their two-page cleanse summaries (`design/concepts/*/cleanse/owner_pages.md`); Pyrelands has no such page and was
read from its mod description. "In `src/`" means a file of that name was found by listing or search on 2026-11-18;
it does not mean the code was read or works. Anything marked *(not verified)* is an inference from names.

The owner's framing, 2026-11-18: *"there IS a lot of shared machinery, and a lot of machinery one builds will
actually be active everywhere (just featured and vital in one by design, while more incidental in others... like
wind effect on fire for example)."*

## Built once, active everywhere

| machinery | what it is | featured in | incidental in | in `src/`? |
|---|---|---|---|---|
| **The Empire's clock** | The search that restarts at every landing (probe, spotter, strike, cordon, breach, bombardment), slowed fourfold on listed biomes and sped or slowed by how visible the crew is. | **The Abyss** (the hide is the biome) | Every biome: it sets how long a stop lasts and what a fight there looks like. | Yes: `src/RimUtinni/EmpirePursuit/`, `src/RimMandrake/Visibility/`. Ladder numbers are marked provisional. |
| **Line of sight as cover** | Plants, trunks and Dark that block sight, so the probe and the spotter (who must *see* the ship) fail. | **The Greentide** (sight-blocking understory) | Fever Wood (solid trunks), Abyss (the Dark), Webwork, Leaning Scrub's vine islands *(not verified)* | Yes: `RM_CompSightBlocker`, `RM_MapComponent_SightBlockGrid` in `CreatureBehaviors`. Whether the probe's sighting honours it: not verified. |
| **One sun, and shade** | Heat from the sun's angle at the tile; roofs, parasols and trees as shade. No biome has its own heat. | **Long Shade**, Stillsand | Every dayside map. Nothing on the night side. | Yes: `RM_SunHeat*`, `RM_PlanetSunGeometry`, `RM_MapComponent_ShadeGrid` in `CreatureBehaviors`. |
| **Wind on fire** | Fire that walks with the wind. | **Pyrelands** | Anywhere something burns: the Fever Wood's oil haze, a blaster fight in dry scrub. | **Only inside Pyrelands today** (`MapComponent_BurnLine`, `PyrelandsFireFront`). Not yet a shared engine. |
| **Wind as an event** | Gusts, stalls and gales that creatures, sound and machines read. | Leaning Scrub (wind power, Stall and Gale), **Abyss** (gusts), Stillsand (the dune gale) | Any map with weather. | Three readers found: `RM_GustController` (Abyss), the Scrub's own calendar, `MovingDunes`. Whether they share one reading: not verified. |
| **Growth as pressure** | Wet natives growing fast; a grid that blowers, grazing and paving write to. | **The Greentide** | Fever Wood, Miasma, Webwork (*"the canopy returns"*), Contagion, Leaning Scrub's venomvine, the Cracked Lands' bloom after a flood | Yes: `ExplosiveGrowth`; blower and grazing hooks in `EnvironmentalHazards`. |
| **Ground that holds you, and the rescue** | A pawn trapped by terrain or taken by water, on a clock, freed by a companion onto firm ground. He ruled the rescue rule general on 2026-11-10: it applies *"wherever it occurs"*. | **The Fever Wood** (seized at the pools), **the Greentide** (mired) | The Twilight sea floor (carried to a sink), the Sump (tar), the Slime (swallowed) | Several: `RM_MapComponent_TheTenant`, the Greentide's mire and burial components, tar coating. One shared rescue rule in code: not verified. |
| **A sign, then the event, then a window** | A readable warning, a timed hazard, and a short harvest after it. | Cracked Lands (chimes, flood, mud), Cauldron (vents quiet, bloom), the Forge (fire and rain, crust), Pyrelands (the burn, ash) | Contagion (clear-sky window), Wastes (ash storms), Greentide (Breaklight), Abyss (the Unveiling) | Yes, as parts: `GameCondition_EnvironmentalWeather`, `RM_GameCondition_WeatherPulse`, `RM_GameCondition_GradientSurge`. |
| **Sound that means something** | A chorus that one event silences; a hum that changes; air that muffles. | **The Fever Wood** (silence means the water) | Greentide (silence means a predator), Rust Cathedral (the hum), Abyss (muffling), Webwork (it is the quiet one) | Yes: `RM_MapComponent_SilenceCue`, `RM_MapComponent_ProximitySoundscape`. |
| **Scenery that is an animal** | Ambushers that read as water, bank, bark, shade, sand or ice until weight or nearness wakes them. | Long Shade (the false shade), Greentide (the water three) | Fever Wood (the bark), Stillsand (buried predators), Sleeping Ice (things in the ice) | Yes: `RM_CompAquaticAmbusher`, `RM_CompFalseShadeAmbusher`, `RM_CompSandSwim`; the `Watchers` and `HostileFlora` kits. |
| **You were noticed** | The place answers what the crew does: light, warmth, noise, taking. | Lantern Deeps (light draws the minds), Rust Cathedral (extraction provokes), Webwork (robbing the web brings hunters) | Abyss (light), Sleeping Ice (warmth), Fever Wood (noise) | No shared engine found. Each biome has its own. The visibility dial is the Empire's version of the same idea. |
| **Light as a resource** | Light that grows crops, that things eat, that gives you away. | **The Abyss** | Lantern Deeps, the Rot, the Twilight sea floor | A shared light ledger exists (named in the Abyss census); who else uses it: not verified. |
| **Wrecks and salvage** | What the crew steps outside for in every biome. | Wastes, Sleeping Ice, Rust Cathedral, Blue Desert | Everywhere | Yes: `Wreckage`. Also the ship's own parts: the acoustic sounder (a reading per biome) and the keel hoist. |
| **Natives belong here** | Natives are never trapped, seized or left thirsty by their own home. | — | Every biome | Yes: `RM_HazardNativeExtension`; thirst through `FlowWorks`. |
| **The landing itself** | What the game does when a gravship arrives. | — | Every biome | Yes, by filename, not read: `GravshipLanding` (unfogs outdoor ground so the landing is not blind), `RM_Patch_GravshipArrivalLetter`, `RM_Patch_LaunchHeldColonistWarning` (a launch warns when someone is still held). These are where "the first minutes" of every design would hook in. |

Also everywhere, and nobody's feature: real flight for anything that flies, bone from butchery, calm-gated
gathering, a settings switch per feature.

## Biomes that read alike under the lens

A crew that lands at two of these in a row may feel it has seen the second one already. Each group needs its
members told apart by what the *crew does*, not by palette.

- **The wet green ones:** Fever Wood, Greentide, Webwork, Miasma. Trapping ground, a punishment for touching, giant
  plants. Told apart today by sound (loud, loudest, silent) and by what moves (nothing, everything, the spiders).
- **The dark ones lit by what grows:** Abyss, Lantern Deeps, the Rot, the Twilight sea floor. In all four, light
  matters and something answers it.
- **The salvage fields with a tax:** Wastes (poison), Warscar (what it does to the mind), Rust Cathedral (the
  machines), Sleeping Ice (cold and what warmth wakes), Blue Desert (fuel that blasts).
- **The warned cycles:** Cracked Lands, Cauldron, the Forge, Contagion, Pyrelands. Sign, event, window.
- **The open crossings:** Long Shade, Stillsand, Leaning Scrub. These are closest to the crew's home desert. His
  lens says the Jawa are *"adapted only to their parent desert biomes"*, so here the joke cannot be that they are
  out of their depth. These three need a different source of "did you see that".

## Build order, in one line

The Empire's clock comes first because every design leans on how long a stop lasts and what a probe can see; then
the general rescue rule; then growth and its suppression. The Fever Wood and the Greentide share the most groundwork
(painted root routes, mineable living trunks, the silence cue, ground that holds you) and should be built as a
pair; the Abyss shares almost nothing with them and pairs with the Lantern Deeps.

## Two questions that are really one question each, across all the biomes

Both came up separately in each of the three deep reads. Each is cheaper to rule once than twenty-three times.

1. **What counts as cover from orbit?** His 2026-08-05 ruling pauses the orbital clock on dark or covered tiles.
   Only the Abyss is on the built list. Canopy (Fever Wood, Greentide, Webwork), steam, caves (Lantern Deeps), ice
   and the sea floors each need a yes, a no or a "partly".
2. **Which biomes are fuel stops?** Fuel is the ship's leash. Sources that name a local fuel: the Fever Wood's
   seep-oil, the Greentide's resin, the Abyss's tholin (built: it refines to chemfuel), the Blue Desert's native
   fuel, the Sump's tar, the Chill's dark fuel, Lantern Deeps' hydrocarbon animals. Which of these feed the ship
   decides where a crew must land, which is most of the campaign.
