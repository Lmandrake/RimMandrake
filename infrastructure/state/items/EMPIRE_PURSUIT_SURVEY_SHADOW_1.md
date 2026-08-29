# EMPIRE_PURSUIT_SURVEY_SHADOW_1 — poorly-surveyed biomes slow the Empire's pursuit

Owner, 2026-08-28 (verbatim, on the pursuit cadence): "Matching the initial fast
timeline... it takes them that long to 'relocate' the ship on the dayside. But any
area that's poorly surveyed (e.g. forsaken crags, or possibly some others, and even
in distant v2 maybe on the ocean floor for a sealed ship) it's more like 20-30 days"

## spec
Ruthless Faction Pursuit has one global `raidDelayHours`. Fork the bundled source
(MIT-style, credit required — workshop 3621784437 ships Source/) to add a
biome-keyed delay multiplier on `ScenPart_RuthlessPursuingMechanoids`: settled-map
biome in a "survey shadow" list ⇒ raidDelay × ~4 (156h → ~600±150h ≈ 20-30 days).
The list is owner data (starts with the Forsaken Crags biome def; he says "possibly
some others"), kept as a def/field he can read, per owner-rules-must-be-data.
v2 note: ocean-floor sealed-ship idea rides the same mechanism.

## verify
Scratch game, part active with tiny delays: normal biome raids on the fast clock;
a survey-shadow biome map gets the multiplied clock (read the part's scribed
mapRaidTimers in a save).

## criteria
- [ ] Global cadence 156±36h ships in the campaign scenario part.
- [ ] Survey-shadow biomes get ~4x delay, from an owner-editable list.
- [ ] Mod author credited per license.
