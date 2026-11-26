# SANGUOPHAGE_KEPT_UNREACHABLE_1: the Sith line (mandrake.rsw.sithline), live acceptance

## spec

The owner replaced "keep the def but make it unreachable" with the Sith line (typed 2026-10-09, cards 2026-10-09; the
ledger notes of this item). The design is `design/RimMandrake/sith_line_design.md`. The mod is
`src/RimStarWars/SithLine`, built at 774adf37de1b. Its offline criteria A1 and A2 passed. The live criteria A3 to A9
were never run: the mod was never in a mod list.

## verify

Deploy the mod with its small list on a free game and run `src/RimStarWars/SithLine/validation.py` live. The walk is
`design/validation_walks/RimStarWars/SithLine.md`.

## criteria

- A3 the mod loads with no red errors; every shipped def resolves.
- A4 the live defs read the relabel, no XenogermReimplanter, the unbuildable Sith buildings and the Anzati copies.
- A5 the settings round trip.
- A6 a Sith prisoner cannot join the player.
- A7 an Empire raid holds an inquisitor; a trader group holds none.
- A8 an Anzati reads as hemogenic and a bloodfeeder.
- A9 the lair rumour makes its site (needs an RM_Abyss tile; the frozen planet has none until the paint-once pass).

## refs

file: src/RimStarWars/SithLine/validation.py
file: src/RimStarWars/SithLine/About/About.xml
file: design/validation_walks/RimStarWars/SithLine.md
