<!-- status: live -->
# worldgen_interactive_build_concepts.md — new content the world painting asks for

> 🔴 **THE PLANET IS FROZEN — owner's ruling, 2026-08-21. Do not paint, repaint, re-render
> or reference-match it.** Verbatim: *"We need to just freeze the world for now as-is and
> move on to v1. I have to totally rethink how we create that planet. It's really messy and
> horrible compared to what I was hoping for originally."*
>
> ⛔ **Every instruction in this file to edit the paint, re-run the painter, render and judge
> the map by eye, or clear a pre-worldgen gate is DEAD FOR V1** — whether or not it is struck
> below, and whether or not it reads as merely "not started yet". The map that exists IS the
> v1 map. `refmatch.py` is cancelled, not gated, and does not exist.
> ✅ **What survives is CORRECTNESS** in artifacts and tools we still ship — a link CSV
> emitted backwards, a lint excluding the wrong tiles. Fix those.
> 🔮 The rethink of the authoring METHOD is post-v1: `design/V2_DREAMS.md >
> PLANET_METHOD_RETHINK_1`. ⛔ It is **not worldgen**, which is out of every version.
> Ruling: `WORLD_FROZEN_RETHINK_PLANET_1` · canon: `ORTHO_GLOBE_MAP_ACCEPTED_1`.


Parking file. Anything that emerges from the worldgen sessions and needs something
**BUILT** — a def, a biome, an assembly, art, a patch — lands here as a one-line bullet
and is **not processed further during low-token time**. It is not a queue and nothing in
it is scheduled.

Painting existing biomes onto existing tiles is not a build concept and does not belong
here.

## Axis 1 — biome layout, temperature, rainfall

Owner, 2026-08-16, with the standing instruction that everything discussed in these
sessions be recorded here for DESIGN to pick up later.

- **v2 — Imperial pursuit onto the nightside.** In v1 the hunt simply lapses there. In v2
  the Empire should still be able to follow, just take far longer — possibly modelled as a
  **radius from the central Imperial holdings on the planet**, so the deep dark is safer
  than the fringe. Needs a mechanism; none exists.
- **The nightside as the endgame frontier.** It stands in for space and asteroids, which
  are Empire-held in this campaign. Staying and farming there is meant to be **achievable
  but gated on a very heavily equipped ship** — heaters, weapons, survival gear. Whether
  that gate is real (equipment checks, temperature mechanics) or diegetic needs deciding.
- **Nightside chemistry cycle.** Methane / propane / ammonia replace water entirely. Needs
  thing defs, weather and probably a resource: propane liquid −188…−42 °C, ammonia
  −78…−33, ethane −183…−87. The antistellar core carries solid ammonia ice and solid CO₂.
- **Ammonia / propane / ethane precipitation** as rain and snow on the nightside — new
  WeatherDefs. Water snow and rain must never occur there.
- **Strange lake formations, mined for fuel.** The nightside's frozen chemistry lakes as a
  located, minable resource — an Exotic axis for those tiles.
- **Mineral ice.** The nightside's frozen seas are deadlocked ice outside the water cycle;
  if they are to be mined or drilled, that is content.
- **Fog and dew at the terminator.** The terminator's only moisture. No vanilla weather
  represents fog that descends at night and lifts by morning — and on a tidally locked
  world there is no night to hang it on, so this needs its own mechanism.
- **Violent high-altitude mountain rain on the dayside** — the planet's only true rainfall,
  in the strange biomes at the peaks. Probably a weather restriction plus biome placement.
- **Breathable everywhere** is a deliberate scope CUT, recorded so nobody adds vac suits:
  all other atmospheric gases stay gaseous across the frozen range. Insulation only.
- ⛔ ~~**TOOLING: `worldmap.py` cannot write tile mutators** … Painting `WindyMutator` for
  the high-wind belts needs that pair implemented. Small job, blocks the wind half of
  Axis 1.~~ **DEAD 2026-08-19 — do not implement this.** The owner killed savegame writing
  on 2026-08-18 and `worldmap.py` now refuses to write; nine save-writers were deleted.
  The encodings named are still correct as a description of the SAVE FORMAT.
  ⭐ **The live route:** mutators are written into the running world through the
  companion's batch tile setter, like every other tile field — `ASHKARR_WORLD_DEFINITION.md`
  §12.2. And ⚠️ vanilla's Mutators step (700) has already run by then (§12.3), so ours go
  on after a clear-and-re-roll, not into a generator slot. **Nothing is blocked.**
- **The Rust Cathedral at the substellar centre** — already ruled as the one mega-structure
  (`the_forgotten_war.md`, 2026-08-15). Now sited: the Rakatan terraforming works, irregular
  but one solid mass, surviving at higher elevation where sand never buried it. The map
  content itself — acid lakes, charged floors, foundry leavings, its defenders — is that
  doc's job, not the repaint's.

## Axis 2 — elevation and the spine

- **v2 — cryovolcanism on the nightside.** Explicitly not in v1: the dark half has no active
  volcanism now, but ice volcanism is wanted later. Owner, 2026-08-16.
- **Orbital war as surface history.** The nightside's craters are not only impacts — it was
  fought over from orbit. Whether that produces findable wreck sites, a landmark type, or
  stays back-story is undecided.
- **Trenches, canyons and chemical deltas.** Carved deep by flowing non-water chemistry.
  Vanilla elevation plus hilliness cannot express a canyon; whether Odyssey tile mutators
  can, or whether this needs its own landform content, is unresolved.
- **The Rust Cathedral is losing to the sand.** The intrusion is being progressively buried.
  If that burial is to be visible as partial coverage rather than a hard biome edge, it may
  want a transitional treatment the biome array alone cannot give.

## Horror Wastes — lore, owner 2026-08-17

Areas where an active bioweapon is **still going on**. They leave behind no natural life:
only scarred, dangerous, weaponised biocells forming themselves into **hostile organs of
destruction**, slowly degrading into pointlessness.

⭐ No longer able to adapt to the temperature extremes, they have been **forced back by the
hostility of the world** to a smattering of scattered holdings in the **rotting Twilight** —
of what was once a much more lush and beautiful world.

⇒ Placement consequence: Horror Wastes belong in the **terminator band**, in scattered small
holdings rather than a contiguous region, and they should read as **retreating**, not
spreading. They are also one of the biological horrors the **Ascendant Helix** came to study.
