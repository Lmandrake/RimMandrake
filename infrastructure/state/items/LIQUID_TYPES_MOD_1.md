# LIQUID_TYPES_MOD_1 — one liquid system, many liquids

Owner, at the Rust Cathedral sitting 2026-09-06 (verbatim on the filing event).
A mod defining liquid VARIETIES as data: per-liquid **viscosity (move cost),
damage type on contact/immersion, acidity vs basicity, color, opacity,
sediment/fine-sand and oil variants** — on tile maps AND the worldmap.

## The roster he named, plus candidates

Boiling water · frigid water · normal water · liquid propane · slime · ooze ·
tar · acid · poison · mineralized · **coolant** — plus made-up extensions:
brine (the Greentide's river graves), rainbow reaction-liquor (Scarlands
pools), fuel-sap liquor (Greentide stills), blood/ichor (Webwork nests?),
cryo-ammonia (the Flats), mud grades (churnmud).

## Consumers already ruled — this is why it pays

- Rust Cathedral **coolant canals** (this sitting) — the 8 river tiles.
- Scarlands **rainbow pools** (hot, acid, deadly) + all-toxic water variants.
- Propane Lakes (liquid fuel sea, ignition rules), Tar Pits, the Slime.
- Greentide salinity gradient (fresh → brackish → brine → salt grave).
- Terminator seas / boiling shores (`the_seas.md`), nightside frigid water.

## The trick (his words): indexing into every other mod

Vanilla + mods hard-reference `WaterShallow`/`WaterDeep` etc. in terrains,
biomes, gen-steps, pathing, fishing, swimming. Approach to evaluate first:
per-liquid TerrainDefs cloned off vanilla water (so engine water logic holds)
+ a property comp/def-extension the damage/pH/viscosity systems read; patch
index built by a generator, not by hand. Check what Vanilla Expanded / Biomes!
already do for custom waters (BMT/AB toxic waters exist — learn, don't
duplicate). Worldmap layer ties `LIQUID_BIOMES_MAP_1`.
