# RIMMANDRAKE_REPIN_GRAFFITI_UGLINESS_BAR_STAT_NOBODY_INSPECTS

## spec
Bar `ugliness_visible` (Graffiti 0.1.0, tree.json, locked): experience "a Beauty -15 vandal scrawl look worse than a Beauty -3
tally"; oracle control "the beauty stats read -15 and -3 from the defs". The game does not use those numbers for any mark a
pawn painted: Filth_Mark.NetBeauty returns RM_GraffitiKernel.CraftBeauty(craft) when hasCraft (the def's Beauty is read only
for a mark with no craft), and the inspect line (Filth_Mark.cs:520, WallInspectPatch.cs:33) shows that craft beauty. With the
scrawl capped at Poor and the tally (Glyph) at Normal, a same-hand scrawl and tally read equal at Awful (-6/-6) and Poor
(-2.5/-2.5): the stat a player inspects does not say the scrawl is worse. The control passes on the defs while the inspected
stat can disagree with the picture. The bar also pins stat values, which the 2026-11-16 ruling ("A passing bar is an
experience, never a tuning number") bars. Held statement row 5 (walk_defects_2026-11-14) saw the same: "Beauty -2".
NOTED_FOR_CONDUCTOR: the criterion is wrong while the bar keeps its meaning (stat and picture agree), so the steward re-pins
it, and the neutral fixer rewords the bar's numbers. Whether a same-hand scrawl must inspect strictly uglier than a tally is
then a code question for the re-pinned bar.

## verify
Acceptance test: none, a bar re-pin is the steward's and the neutral fixer's call (bar text is locked to the blind judge).

## criteria
- ugliness_visible names no stat value and is checked on the beauty a player inspects.
