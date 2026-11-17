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

## What the card said

<!-- answered 2026-11-17T04:23:54Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** Mon Nov 16, 8:22 PM PST. Graffiti is held on one bar's wording, and only you can change a bar. The bar says a vandal scrawl must look worse than a tally mark, and its test checks two fixed beauty numbers written in the mod's definitions (-15 and -3). The judge found two faults. First, the game never shows those numbers for a painted mark: the beauty a player sees when inspecting a wall comes from the painter's skill, so a scrawl and a tally by the same poor painter read identical (-6 and -6). Second, your ruling this morning says a bar is an experience, never a tuning number. Every judge cycle will reopen this until the bar is reworded. How should the ugliness bar read?
**Picked:** Look and stat agree (Recommended)
**Its description:** Why: a player trusts both eyes and the inspect line. The bar says a scrawl looks worse than a tally AND inspects as uglier when the same hand made both, with no numbers named. Costs a small code change so a scrawl always reads uglier. Recommended because it keeps the bar's meaning and obeys your no-numbers ruling.
**Other options:** Picture only · Inspected stat only · Keep it as written
