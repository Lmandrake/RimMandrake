## spec
`jawa/texture_audit` resolves a def's `texPath` by vanilla `Graphic_Multi` /
`Graphic_Single` rules — bare path, then `_north`/`_east`/`_south`/`_west`. A mod that
ships its OWN `graphicClass` resolves its own filenames, so the audit reports every one
of those defs as dead art when the art is present and drawing correctly.

**Measured on the 2026-08-21 01:23 first-light run** (`infrastructure/output/
first_light_2026-08-21_0123.md`): 53 rows reported, **39 of them Tribal Furniture**
(`xercaine.tribal.furniture`, workshop 3671245310). All 13 of its flagged defs declare
`<graphicClass>TribalFurniture.Graphic_Appearances_Multi</graphicClass>`, from the mod's
own `TribalFurniture.dll`. The `texPath`
`Things/Building/Furniture/Bed/XERTribalBed/XERTribalBed` is a STEM; the shipped files
are `XERTribalBed_<Stuff>_north.png` etc., and all **138** PNGs are present.
⇒ 74% of the audit's output is noise, which is worse than no audit — it trains the
reader to skim a list that also contains real defects.

Change the tool so a def whose `graphicClass` is not a `Verse.Graphic_*` is reported in
a SEPARATE bucket — "unjudged: custom graphic class" with the class name — rather than
under missing. ⛔ Do not silently drop those defs: a custom class CAN still point at
nothing, and hiding the row would trade a false positive for a false negative.

🔑 The 14 non-Tribal-Furniture rows are all `lifeStages[N].dessicated` and are NOT
covered by this item — they may well be real. ⚠️ One of them is `GRimBullfrog`, and
`GRIMTERRA_TEXPATH_TYPOS_1` is already CLOSED as done; check whether that fix missed the
dessicated variant or whether this is a different path, before assuming either.

## verify
offline: re-run the audit against the same mod list and confirm Tribal Furniture's 39
rows move out of `missing` into the new bucket, `missingCount` drops to 14, and the
`XER_*` rows each carry `TribalFurniture.Graphic_Appearances_Multi` as their reason.

## criteria
a first-light run on the full list reports a `missing` list in which every row, checked
by hand, is a path with no file behind it under that def's OWN resolver.
