The def dump (defs.sqlite) stops at a depth limit and writes the string '<maxdepth:ThingFilter>' in place of a ThingFilter, so any name census over the dump cannot see names inside a filter: Odyssey's RareFishingCatches_* egg options (EggDuckFertilized, ...) were invisible. On the 2026-11-12 dump, 155 of the route defs that vanilla_beast_cut.py reads hold such a field. Count the '<maxdepth:' leaves and read the source XML for those defs before calling a census clean.
item: VANILLA_BEAST_LEAKS_EXCISE_ESCAPEES_AT_LARGE
home: infrastructure/state/facts/instrument_traps.md
