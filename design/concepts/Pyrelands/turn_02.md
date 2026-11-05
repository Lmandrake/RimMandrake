# Pyrelands, Designer turn 2 (stage 1 closed: the root as you corrected it)

Run `rm-role-designer-1793896289`, 2026-11-05. Your card answer to `ask_root` made four corrections; all are applied
below and nothing else changed. I read your parentheses as insertion marks and dropped them. Undo or reword any of it.

> The Pyrelands are a genetically engineered grass savanna that has burned for millennia and is burning still.
> Almost all the ground is deep ash, quite fertile wherever water reaches it, carpeted thick in ember grass that
> burns black and is largely green again within about a week, while free-flying ash blows across it like snow. A
> line of grass fire walks the map and never fully goes out for long. Behind it the fire offers some solace: scorch-
> fruit grows only from freshly burned ground and must be picked before it rots, and fresh burns grow crops faster
> for a few days, and black rain compounds that bonus rather than washing it away. The animals are the fire's own
> cast: a fire-hawk carries a burning twig ahead of the blaze to start a new fire, ullai herds graze where it burned
> two days ago, the ashwallow dives underground as the front reaches it and comes through unharmed, and the giant
> furnace-beast warms anyone standing near it and heats a room it shelters in. The sky brings ash fall, cinderfall
> and black rain, and never ordinary rain. Ruins stand blackened. The biome is whole on its own, with no other mod's
> plants or animals, and (built, not yet in your words) a sprayed firebreak line and a firefoam sprayer let a colony
> defend its fields. Judged first: a fresh map in ordinary play where the burn line is visibly walking across deep
> ash with a scorched trail behind it, and a few days later the grass behind it is greening and scorch-fruit stands
> in the scar.

Your words (2026-11-05): *"Substitute "A (genetically engineered) grass savanna..." "never fully goes out (for long)." Correction: black rain should not wash away that benefit but compound it. Reword "Behind it the fire (offers some solace):" (rather than pays)"*

What changes in the build: the ash field today lets a Black Rain fade the fresh-burn bonus (`PyrelandsAshField.cs`,
ash redesign §4). Your word reverses that. Before it goes to Relentless, stage 2 asks one thing: does "compound" mean
the rain adds its own bonus on top of the burn's, or that the burn's bonus stops fading while the ground is wet
(`a_blackrain_compound`, drafted, reviewed before it reaches you).

Next (stage 2): that question, then how far a firebreak must hold (`a_fire_control_scene`) and the regrow pace
(`a_regrow_thresholds`).
