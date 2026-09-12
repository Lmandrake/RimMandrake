# EXPLOSIVE_PLANT_GROWTH_1 — visible plant growth as a world mechanic

Born in the Cracked Lands enrichment (`biomes/the_cracked_lands.md` §10b), ruled
**world-wide** by the owner (verbatim on the filing event): water-soaked plants grow
VISIBLY — the player watches them get bigger, not animal-motion but growth — and it
should feel intimidating anywhere water soaks a plant. The jungles should visibly
grow.

## The two design questions before any code

1. **What DOES happen at the top?** It can't grow forever; the terminal moment is a
   designed event meant to recur ("a great moment again and again") — burst, bloom,
   collapse, seed-storm, something ruled with the owner, possibly per-biome.
2. **What are the custom mod actions** that let players "experience and play with
   it" — trigger it, harvest it, survive it, weaponize it?

## Engine notes for whoever builds

- Vanilla growth is tick-slow and visually stepped; visible real-time growth needs
  graphic scaling per tick or staged swaps — measure the perf cost on a jungle map
  before promising density.
- Consumers already waiting: Cracked Lands flood-weeks (§10b), the jungles
  (AB_MycoticJungle, BiomeCypreJungle sheets when they come), any biome with
  soaking events.
- `FLOOD_WITNESS_EVENT_1` is the plot's guaranteed showcase of this mechanic.

## Design state 2026-09-12 (corrected)
The design already existed:
`design/Jawa/worldbuilding/explosive_plant_growth_design.md` (2026-09-10,
soak/charge/burst + per-biome terminal moments, provenance-traced to ruled
sheets; its Burst default and variant table are marked INVENTED, awaiting the
owner). A duplicate draft made 2026-09-12 in ignorance of it was deleted after
a salvage pass; four small proposals from it were carried into the canonical
file's 2026-09-12 addendum. Terminal-moment ruling still awaits the owner's
cards, drawn from the CANONICAL file.
