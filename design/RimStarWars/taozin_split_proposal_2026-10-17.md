# Taozin split — proposal (2026-10-17, not built)

**Owner, facings needs-eyes sheet 2026-10-17 (verbatim):** "This needs to be redone into two creatures. The first is a
huge, deadly predator (see canon image of a very small man beside a worm at least ten times his height). This should be a
major predator placed in the Crags Biome we have. The second creature is the Taozin Grub, a much smaller creature as
large as an arm that is a major component of Star Wars Cuisine mod and can be found only in Taozin nests. See canon as to
why they are sought after. They too should be findable as treasure in the Crags. Please make two such creatures now and
regenerate their art accordingly, removing the existing art as unacceptable. Regenerate the Canon image requirements
based on this input."

**Colour ruling (canon_references/taozin/description.md `## ruling`, verbatim):** "I would suggest the grub to be terra
cotta in coloration until it is soaked in the brine for a long period, whereupon it turns white"

Today there is ONE def, `RSW_Taozin` (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Taozin.xml`, bodySize 6, the
grub is only its first life stage, label "taozin grub"), plus its eggs, `RSW_TaozinNodule`, `RSW_WoolTaozin` and four
sounds. Two redraw jobs from the enact are queued against that one def's art.

## Creature 1 — `RSW_Taozin`, the Legends "force dragon" (keeps the defName)

- **What it is:** a giant segmented annelid/centipede of the Legends painting, at least ten times a man's height: long
  ringed armoured body in red-brown and cream bands, many short legs and arms, a mandibled head with green eyes.
- **Canon traits to carry:** spits silken webbing to trap prey; shell almost proof against blasters and lightsabers
  (translucent body diffuses energy); invisible in the Force.
- **Game shape:** a major predator, wild only in the Crags (`RM_ForsakenCrags`, the name the design docs use; no
  BiomeDef exists yet, so its roster line waits for that biome). Adult only — no grub life stage (the grub becomes
  creature 2). Body size and draw size set to "ten times a man's height" lengthways (draw size around 10+ cells; check
  against the true-scale panel). Strong armour against Sharp and Heat; a web-spit ability that slows or roots (reuse an
  existing spit ability if one fits — search `src/` first). Butchering yields `RSW_WoolTaozin` silk and
  `RSW_TaozinNodule` as now.
- **Breeding:** it does not lay grubs on the map at random. Its lair is a nest (below).

## Creature 2 — `RSW_TaozinGrub` (new)

- **What it is:** the canon grub, about as long as a forearm: a long segmented body with eight pairs of legs clustered
  at the head end, black eyes, a banded collar mid-body, and a long smooth tapering tail (owner photo
  `owner_supplied_grub_hanging.png`).
- **Colour:** terracotta by default; a grub kept long in brine turns white (owner ruling). Two looks of one creature:
  a terracotta picture, and a white picture that only a brine-kept grub shows.
- **Why it is sought:** kept in brine, a grub infuses the liquid with a delicacy said to strengthen the mind (canon and
  Bloggathehutt). That brine is its link to the Cuisine mod (`src/RimStarWars/Cuisine`, which holds no taozin content
  today).
- **Game shape:** a tiny, harmless animal (body size about 0.1), tameable, never wild on the open map. Found only in
  taozin nests in the Crags, as treasure: a nest is a lair the adult guards, holding a few grubs and silk.
- **Brine:** a grub kept in a brine tank produces taozin brine over time (a Cuisine ingredient with a mood or
  mental-break-resistance effect). After long enough in the tank it switches to its white look.

## Art and canon work

- Retire the existing taozin art (owner: "removing the existing art as unacceptable"); withdraw or retarget the two
  queued enact jobs so that one draws the adult and one draws the grub.
- Split `design/RimStarWars/canon_references/taozin/` into two entries (`taozin/` for the adult, `taozin_grub/` for the
  grub) and rewrite each one's `## Must show` from the note above: adult = Legends painting and its scale; grub = the
  owner photo, with terracotta as the default and white for brine-kept.

## Open questions for the owner

1. Nest as treasure: a map feature the adult spawns in (like `RSW_PreciousCave_KraytDen`), or a quest site?
2. Can a colony keep an adult, or is it wild-only?
3. The brine effect in Cuisine: a mood buff, a mental-break resistance, or both?
