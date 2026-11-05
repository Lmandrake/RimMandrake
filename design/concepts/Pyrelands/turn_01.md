# Pyrelands, Designer turn 1 (stage 1: what is the biome)

Run `rm-role-designer-1793865628`, 2026-11-05. For the Conductor to serve; asks are in `record.json` (`ask_root`),
reviewed by a fresh agent before sending. Everything below is already built; nothing here asks whether to keep any of it.

## Claim

This is the paragraph a builder and a checker would work from:

> **The Pyrelands are a grass savanna that has burned for millennia and is burning still. Almost all the ground is
> deep ash, quite fertile wherever water reaches it, carpeted thick in ember grass that burns black and is largely
> green again within about a week, while free-flying ash blows across it like snow. A line of grass fire walks the
> map and never fully goes out. Behind it the fire pays: scorch-fruit grows only from freshly burned ground and must
> be picked before it rots, and fresh burns grow crops faster for a few days, and black rain washes the bonus away early. The animals are
> the fire's own cast: a fire-hawk carries a burning twig ahead of the blaze to start a new fire, ullai herds graze
> where it burned two days ago, the ashwallow dives underground as the front reaches it and comes through unharmed,
> and the giant furnace-beast warms anyone standing near it and heats a room it shelters in. The sky brings ash fall, cinderfall and black rain, and
> never ordinary rain. Ruins stand blackened. The biome is whole on its own, with no other mod's plants or animals,
> and (built, not yet in your words) a sprayed firebreak line and a firefoam sprayer let a colony defend its fields.**
>
> **What the biome is judged on first:** a fresh map in ordinary play where the burn line is visibly walking across
> deep ash with a scorched trail behind it, and a few days later the grass behind it is greening and scorch-fruit
> stands in the scar.

Built from your words: *"the Pyrelands have burned for milennia, so most places should already have deep ash"*, *"the
ash should be QUITE fertile with water added"*, *"there should also be a LOT of free-flying ash blowing around like
snow"* (2026-10-12), *"Correct animal and plant distributions"* (2026-09-17), and the north star you validated (20 must-show bars in populations, fire ecology, fire cast and weather, and one forbidden sight: ordinary rain).

## Attack

The strongest case against it: the paragraph says **the fire pays**, and that makes the burn line a partner, not a
hazard. If that is the root, a colony that loses its fields to a smoulder that relit by itself is a reason to reject
the biome, not bad luck, and the firebreak and firefoam become core rather than optional (no bar of yours says what
they must do yet, and nothing has proven them). The other reading is a hard biome where living means surviving the
fire, and the payoffs are consolations. I hold "the fire pays" because your ash ruling makes the burned ground fertile
on purpose, but it is the costliest sentence here and you should see it.

The "judged first" line puts the burn line and what grows behind it before the creatures, because the creatures read
as the fire's cast only when there is a fire to follow; the fire-hawk's flight cannot be watched without you anyway.

## Picture

- **If the paragraph is right:** a tester lands on a fresh map, finds the fire front within minutes, and five days
  later walks the scar: grass a third green, ripe scorch-fruit standing in it, and a field planted on the fresh burn
  ahead of an identical field on old ash.
- **If it is wrong (hazard first):** the same map, but the test is whether a colony can keep its buildings and fields
  out of the fire's path, and scorch-fruit is a footnote.

## Asks

1. **ask_root:** Is the paragraph above the Pyrelands? Correct any word, or say "yes".

Kept ready, not sent (stage 2): what a firebreak must do for you to trust it (`a_fire_control_scene`); whether
regrowth of a third by day 3 and 60% by day 7 reads right (`a_regrow_thresholds`).
