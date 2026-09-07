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
