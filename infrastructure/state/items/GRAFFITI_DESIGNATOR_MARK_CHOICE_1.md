# GRAFFITI_DESIGNATOR_MARK_CHOICE_1

Caused by `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1` (forks ruled by question card 2026-10-09; rulings in that item and `design/RM_GRAFFITI_SCOPE_WIDENING.md` §7). Code: `src/RimMandrake/Graffiti/`.

## spec
F6 ruled "full designator + bill (choose mark, choose wall)". Today `Designator_PaintGraffitiMark` lets the player choose the wall only; the mark is a weighted random pick from the designator pool. Add the mark choice:
- clicking the designator opens a float menu: "Any mark (painter's pick)" plus every `designatorEligible` mark by label (the same Build-designator shape vanilla uses for stuff).
- the choice is stored per designated cell in a Scribed `MapComponent`; the paint job reads it, falls back to the pool when the order is "any", the def is gone, or the order is stale; the entry clears when painted or when its designation no longer exists.
- the meme gate still applies to tier-C glyphs: a mark whose `requiresAnyMeme` the painter's ideo lacks is not painted by that pawn's hand; the painter's-pick pool is used instead.

## criteria
- O1 L0: Graffiti builds 0 errors with every new .cs in a `<Compile Include>`; selftests no new failure
- A1 L2: live, designating a cell with a named mark gets that mark painted there by a colonist; "any" still paints from the pool; the order survives save/load
