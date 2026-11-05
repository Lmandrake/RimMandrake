# PyrelandsMechanics, Designer turn 2 (stage 1 closed: the root as you corrected it)

Run `rm-role-designer-1793896435`, 2026-11-05. Your card answer to `ask_root` is applied below. The arson count and
the animal blame are gone; the fruit defence and the raid-back are in. I also dropped the old sentence "the rite never
turns into an attack", because your fruit defence is an attack. Nothing else changed. Undo or reword any of it.

> The Deep Desert Tribes are the Pyrelands' fire harvesters. They come into the Pyrelands now and then for their fire
> rite and to reap what the fire leaves, then go home to the deep desert; the Pyre burns with or without them. On a
> Pyrelands map, some of the fire's scheduled burns arrive with people: a small Tribes party walks in off the sand and
> the line catches where they stand; they work the black behind the front picking scorch-fruit without stepping into
> the flames, and leave carrying what they took. When a lot of fire is already standing, a peaceful Tribes group may
> also walk in to the burn. If your colonists pick scorch-fruit during one of their events, the Tribes warn them, then
> attack to drive them away: a defence of the fruit, not a full-blown raid. The Tribes keep no count of your colony's
> fires (they cannot see you all the time), and they never blame you for anything an animal does. Attack them openly
> and they raid you back, and they may go on raiding you later. Judged first: a rite party seen in ordinary play,
> lighting the grass, picking scorch-fruit in the scar behind the front, and walking off the map with it.

Your words (2026-11-05): *"If you try to pick the scorchfruit during one of their events, they issue warnings, then attack to drive you away (not a full blown raid, just defense of the fruit). Actually just remove the count thing... that's a mechanic we don't even need. They can't see you all the time. And never do they react to an animal doing something to blame the player. Attacking them overtly makes them raid you back of course, and they may continue to do so later."*

What changes in the build (Relentless's work, nothing to decide):
- **Removed:** the arson debt and the arson raid (`RUT_FireRaid`, its two settings), and the arson tally in the
  franchise-free Pyrelands burn kernel that counted fire-hawk twigs and furnace-beast beds against you.
- **New:** the fruit defence. Today a rite party that turns hostile just leaves; it never warns or drives anyone off.
- **Raid-back:** attacking them makes them hostile, and the game's ordinary raids follow; I expect nothing extra to build.

Next (stage 2), one question before the fruit defence can be built (`a_fruit_defence_reach`, reviewed before it reaches
you): which fruit is theirs during a rite (only the scar their party lit, or any scorch-fruit on the map), and whether
being driven off also costs goodwill. Still ready from before: what the peaceful visit party does at the fire
(`a_harvest_visit_at_the_fire`). Struck: whether you should see the arson debt building, since the count is gone.
