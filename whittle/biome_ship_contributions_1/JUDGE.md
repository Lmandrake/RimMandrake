# Judge: BIOME_SHIP_CONTRIBUTIONS_1

Judge: claude-opus-5-5, fresh, blind to DONE.md / BROADEN.md. Date 2026-11-12. Clone /home/mandrake/rm/claude-offline2.

## What I checked myself

- Reran `python3 src/RimMandrake/Utils/ship_contributions.py` at HEAD d262fe3b2d: exit 0, 24/24 biomes PASS, 0 problems.
  Output matches `evidence/ship_contributions_run.txt` line for line, except the header (that run was at HEAD 047ba6f2ae).
  My copy: `D:\ClaudeWork\rimmandrake\judge_bsc1\run.txt`.
- Read the checker's docstring. It reads the substructure affordances from the Odyssey defs and checks build category,
  placeWorkers, bringAlongOnGravship, obtainability, and whether each gift is the biome's own. Its selftest log says it
  rejects 12 mutated false lists. That is a real instrument for the verify line's first half.
- Checked the row claims against the defs:
  - Pattern hull 120 HP/day: CompSelfhealHitpoints, ticksPerHeal 500 on a Rare ticker. Consistent.
  - Hexplate Cleanliness 0.6 and furnace bank heatPerSecond 10: both in the defs.
  - Long-shade mast lee, capped at 16 cells: the lee mode exists in `RM_ShadeGear.cs` / `RM_MapComponent_ShadeGrid.cs`.
- Art: opened `evidence/art2/contact_sheet_96ppc.png`. All 20 pictures read as their things at a consistent house style.
  Every final PNG is installed byte-identical in the mod Textures folder (the great bone under the name
  `SummGreatBone.png`, which is the def's texPath).

## Statement line

**"Every-biome pass ... is done as the item file says, shown by fresh evidence." FALSE.**

- What holds: coverage (24/24 shipped biome mods each have a row naming a real, deck-buildable def that is the biome's
  own), the distinctness sweep, the design-judge fixes, the art, and the owner card. The checker reproduces.
- What fails: the item's verify is "the list here matches what the mods actually ship", and it does not.
  - The Cracked Lands row says the fossil case is "(beauty 14)".
  - `src/RimMandrake/CrackedLands/Defs/ThingDefs_Buildings/RM_FossilCase.xml:44` ships `<Beauty>40</Beauty>`.
  - The item file's own preamble says the change to Beauty 40 was applied.
  - The stale "beauty 14" is also in `evidence/owner_card.md:22`, the matrix going to the owner. So the card would hand
    him a number that is wrong for the def it describes. The checker cannot catch this because it checks def names,
    not the numbers in the prose.
  - The fix is one edit in the list row and one in the card. Until then the list does not match the mod.

## Where the evidence is flattering or cannot show

- No live play: nothing shows a gift placed, flown or used. The README says so plainly. These behaviours are claimed
  from defs and C# reading only: the great bone's imprint, the drive core's range multiplier, the waste-bay launch
  refusal, and the mast's lee on a real deck.
  - For a list-and-design item whose verify is def-level, I do not count this against it.
  - The criteria line ("the gravship becomes a scrapbook") is a play feel that no still or def check can show.
- The contact sheets are clean isolated renders on a flat ground, not in-game on a deck. They show legibility, not fit
  beside vanilla things.
- The row numbers are prose the checker does not verify. A spot check of five found one wrong. Nothing has checked
  the other rows' numbers ("beauty 14" for the gaslight, "radius 10", etc.) against their defs either.

## What would settle it

Correct the Cracked Lands row and `owner_card.md` to Beauty 40. Better still, the other rows' prose numbers should be
diffed against their defs, or the numbers dropped from the prose.

would show: no
