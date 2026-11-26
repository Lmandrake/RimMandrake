# DIRECT_SUN_SETTINGS_WIRE_FEWER_KNOBS — Mod Settings rows for Direct Sun

Design: `design/RimMandrake/unified_direct_sun_heat_2026-10-19.md` §5. Blocked on
`DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES` (the fields it binds to). Nothing here is built. Ruled by card
2026-10-19 (*"55 C everywhere"*; *"no biome-specific heat, no biome-specific sun"*).

## spec

Creature Behaviors settings (`RM_CreatureBehaviorsMod.cs`), defaults = shipped behaviour, all-off =
plain vanilla temperature:
- **Direct Sun** master switch (today `sunHeatEnabled`; relabel) and the **strength** dial (exists).
- **Direct Sun at the zenith (°C)**, default 55. New.
- **Weather dims Direct Sun**, default on. New.
- **Direct Sun on worlds with a day/night cycle**: off, labelled "Unsupported: the shipped world has a
  fixed sun". The only option this item builds is off; following the clock is not built.
- **Delete** `kindFromElevationEnabled` and any low-sun threshold slider: there is no regime switch.
- Existing toggles stay: directional shade, sun pathing, sun-load bar, sand glare, glare-blind,
  mirage.
- **Air heat** lives in each biome mod's own settings (the Forge, the Scald, the Fever Wood, the
  Greentide): on/off and a °C slider, labelled "changes the map's temperature; plants feel it too".
  It never switches off with Direct Sun.
- Declare `SettingDependencies` so the master greys its dependents (the kit from
  `SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST`).
- No new cross-biome switch (owner, 2026-10-15).

## criteria

- `python3 src/RimMandrake/Utils/settings_audit.py` reports Creature Behaviors and the four biome mods
  OK, with no "cannot grey" note.
- Each new field round-trips in the selftest (set, read back, restore).
