# WARLAB_BREAKOUT_BUILD_SEALS_HOLD_THE_LINE — build the war lab's specimen choice, breakout and reinfection

## spec
Build `design/Jawa/worldbuilding/dungeons_arc_spec.md` §2.10 (delegated design, PROVISIONAL
numbers): the core console with five picks, the hyperdrive bay and stasis clock, live
specimens (no PawnKindDef exists yet: confirm one, never guess), three bulkhead seals, the
latching recover/fail check held at game level so it resolves with the map unloaded, the
four lab end states, the Specimen Casket, reinfection nodes as world sites from one
authored list, the threat floor, and a Mod Settings spread-pace knob.

Depends on `ASSAILANT_WARLAB_BUILD_MERGE` (gate order) and the one painting (node tiles).
The node palette stays the Black Hive and VFEI2 rows: no Anomaly content outside the lab.
No tile or biome rewrite, no roll: every failure runs the same list.

## verify
- [ ] Each of the five picks reaches both recover and fail in the mod's functional script.
- [ ] A failure with the map unloaded opens the first node and the next two over two seasons.
