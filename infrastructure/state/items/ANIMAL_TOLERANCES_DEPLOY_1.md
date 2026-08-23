## spec
🔴 **DECIDE authored the renormalization; the deploy is BUILD's** — owner's ruling 2026-08-23.

**Deploy `src/Jawa/Jawa_Patches/Patches/AnimalTolerances_Ashkarr.xml`** (committed `ab02fa2c`).
456 cast animals refitted onto the biome each was cast into. Rule and reasoning:
`design/Jawa/fauna/animal_tolerances.py`.

🔴 **Temperature is a HARD SPAWN GATE for animals, not a comfort stat.** `WildAnimalSpawner.cs:47`
and `:111` filter the biome roster through `SeasonAcceptableFor(race)`, and `MapTemperature.cs:91`
requires `ComfyTemperatureMin < SeasonalTemp < ComfyTemperatureMax` with **buffer 0**. An animal
whose band misses its biome is not uncomfortable — it is **never spawned, and nothing is logged.**

⛔ **THE DEPENDENCY, and it is the whole risk on this item: this assumes `BiomeCast_Ashkarr.xml`
SHIPS.** Every band is fitted to the biome that cast puts the creature in. If the cast does not
deploy, the shipped `wildAnimals` lists put these animals in different biomes and the bands are
fitted for the wrong climate. **Deploy both or neither** — the cast is `BIOME_CAST_APPLY_1`,
yours and in flight.

## Watch out
⚠️ **Both tolerance passes are WIDEN-ONLY, and that is deliberate.** An earlier version re-centred
each band and stripped `GR_ParagonIguana` of 45 °C of shipped heat tolerance for no gain.
Narrowing can only ever CAUSE the bug being closed, and buys nothing, because the roster decides
where a thing may appear and temperature only removes it. ⛔ Do not "tidy" this into a re-centre.
⚠️ **Some shipped ceilings are absurd** (`352.222 °C` across the Biomes! Polluted Lands stock).
They are left untouched on purpose — lowering one would be narrowing.
⚠️ **`SWING = 15.0` is a JUDGEMENT**, shared with the plant pass. The tiles CSV holds one annual
`temp_c` per tile while the gate reads the tile's *seasonal* temperature, which we do not hold.

## verify
**Proved offline against the engine gates, not by eye:** 0 of 621 cast animals fail the strict
spawn gate; 0 of 604 plants fail coverage or hold an inverted optimal band.
**In game:** `AB_PropaneLakes` (median −59.8 °C) and `AB_MechanoidIntrusion` (+62.5 °C) — generate
a map at each and count living animals. Zero red errors naming `AnimalTolerances_Ashkarr`.

## criteria
- [ ] Deployed together with `BiomeCast_Ashkarr.xml`.
- [ ] Both extreme biomes hold living animals.
- [ ] No red errors.
