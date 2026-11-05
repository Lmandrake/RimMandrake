# PyrelandsMechanics, Designer turn 1 (stage 1: what is the mod)

Run `rm-role-designer-1793866044`, 2026-11-05. For the Conductor to serve; asks are in `record.json` (`ask_root`),
reviewed by a fresh agent before sending. Everything below is already built; nothing here asks whether to keep any of it.
This mod is the campaign half of the Pyrelands: only what names the Deep Desert Tribes. The fire itself, the fire
clock, the fire-hawk and the furnace-beast are the franchise-free Pyrelands biome (asked about separately).

## Claim

This is the paragraph a builder and a checker would work from:

> **The Deep Desert Tribes are the Pyrelands' fire harvesters. They come into the Pyrelands now and then for their
> fire rite and to reap what the fire leaves, then go home to the deep desert; the Pyre burns with or without them.
> On a Pyrelands map, some of the fire's scheduled burns arrive with people: a small Tribes party walks in off
> the sand and the line catches where they stand; they work the black behind the front picking scorch-fruit without
> stepping into the flames, and leave carrying what they took. When a lot of fire is already standing, a peaceful Tribes group
> may also walk in to the burn. A fire your colony is to blame for (anything of yours that starts one, a tamed
> fire-hawk's twig or a furnace-beast's bed included) counts against you, and the count fades with time; past a limit
> the Tribes take it as arson and their goodwill drops; if that puts them at war, a short, furious raid walks in,
> usually smaller than an ordinary raid. The debt is then cleared, but the Tribes stay at war, and no rite comes while
> they are. A rite party shot at defends itself, and one that turns hostile simply leaves; the rite never turns into an
> attack.**
>
> **What the mod is judged on first:** a rite party seen in ordinary play, lighting the grass, picking scorch-fruit
> in the scar behind the front, and walking off the map with it.

Built from: the freeze ruling R14 (they are fire harvesters, the Deep Tribes, and the Pyre burns with or without
them) with your words there, *"They are not 'farmers,' I have never liked that term."* (`design/Jawa/worldbuilding/biomes/_freeze_rulings_2026-09-07.md` R14); your note that *"the deep tribes DO light fires
in the Pyrelands still... they just don't do it with flamethrowers or industrial firebombs"* (TECHPRINT_FACTION_GATING_1);
and the biome sheet's fire raids (`design/Jawa/worldbuilding/biomes/the_pyrelands.md` §8). The sheet still calls them
"fire-farmers" in §8; R14 struck that word, so the paragraph says harvesters.

## Attack

The strongest case against it: **R14 says the Pyre does not need the Tribes, and arson-justice says the fire is
theirs.** If the fire burns with or without them, a colony's stray torch takes nothing from them, and a raid for it
reads as arbitrary: the player is punished for doing what lightning does every week. The other reading drops the
raid to a goodwill grudge and keeps the Tribes purely as visitors. I hold the raid because the sheet canonised fire
raids and the Sun-Debt reading gives the reason (an unplanned burn spends the land's repayment out of rite), but it is
the costliest sentence here: it makes your own tamed fire-hawk a source of raids, and whether you should see that debt
building is the first thing I would argue next.

The "judged first" line picks the rite party over the raid because it is the only built moment where the Tribes are
seen doing what R14 says they are; a raid alone would show them as just another enemy.

## Picture

- **If the paragraph is right:** on a Pyrelands colony, a letter says the Tribes have come for the fire; three to five
  Tribes walk in, a new line of fire catches where they stand, and a few hours later they are in the black behind it
  picking scorch-fruit, then they walk off. Weeks later, after your fire-hawk has started one fire too many, their
  goodwill drops and a small party arrives angry.
- **If it is wrong (visitors only):** the same rite, but the colony's own fires cost goodwill and nothing more.

## Asks

1. **ask_root:** Is the paragraph above the Deep Tribes in the Pyrelands? Correct any word, or say "yes".

Kept ready, not sent (stage 2): what the peaceful visit party should be doing when it reaches the fire
(`a_harvest_visit_at_the_fire`); whether you should see the arson debt building before the raid (`a_debt_visible`).
