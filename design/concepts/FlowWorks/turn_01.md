# FlowWorks, Designer turn 1 (stage 1: what is the mod)

Run `rm-role-designer-1793793891`, 2026-11-04. For the Conductor to serve; asks are in `record.json` (`ask_root`,
`ask_defense_story`, `ask_irrigation`), reviewed by a fresh agent before sending.

## Claim

This is the paragraph a builder and a checker would work from. Everything else in FlowWorks hangs off it:

> **FlowWorks lets you dig into the ground, and the liquids already on the map (water, tar, fuel, slime) flow into
> what you dug and settle at one level, drawn from a real supply that visibly shrinks and refills slowly. Its main job is
> defence: an empty canal slows raiders, a water canal makes them wade, a fuel canal can be set alight and burns for
> a long time, and a slime canal is nearly impossible to cross. Deciding when to open the canal is the player's call (my reading of the spec, not your words; ask 2 tests it).
> Watering crops, the plumbing (pipes, pumps, tanks, hoses, bottles) and reshaping the land all use the same liquids
> and the same supply.**
>
> **What the mod is judged on first:** digging, liquid flowing to one level, a supply that pays for every litre, and
> the four defensive canals (empty, water, burning, slime) working in a real raid. The plumbing, pits, bridges and the
> rest are built, they are yours, and they stay; this line only says which scene a tester stages first.

## Attack

The strongest case against this paragraph is that it is out of date. FlowWorks now holds pits, ladders, bridges,
drawbridges, sluice gates, swimming, rivers, hoses, pipes, thirst and sprinklers. An agent building or testing from it, reading "defence first"
might treat all of that as extra, even though it is built and you asked for it. The other risk is "the smallest
version": if the plumbing breaks and you would reject the mod anyway, then the plumbing belongs in the first-judged core too.

## Picture

- **If the paragraph is right:** a tester first stages one raid against a filled or burning canal and judges the mod
  on that. A broken hose is a bug, but it does not sink the mod.
- **If it is wrong:** FlowWorks is a liquids-and-earthworks toolkit with no centre. A tester gives every system equal
  weight, and the raid scene is one test among dozens. (When the test list was last marked passed, 4 of its 43 tests
  actually proved anything; that list has since been rewritten.)

## Asks (at most three, each answerable in a phrase)

1. **ask_root:** Is the paragraph above FlowWorks? Correct any word, or say "yes".
2. **ask_defense_story:** Picture the raid FlowWorks must win. My guess at the scene: a tar canal crosses the raiders'
   approach and stays empty until they are spotted. Then you open it, it fills, and you light it
   as they cross. Is that the scene? Or is it a canal that stays full all the time (water or slime), or something else?
3. **ask_irrigation:** On 2026-09-16 you wrote that plants near a canal act *"as though watered"*, and ruling 36
   said that effect stays, just not drawn. It is not built in FlowWorks yet (with default settings nothing in FlowWorks
   waters crops; CrackedLands has a version we can copy). How far from the bank should a full canal water crops:
   1, 3 or 5 squares?
