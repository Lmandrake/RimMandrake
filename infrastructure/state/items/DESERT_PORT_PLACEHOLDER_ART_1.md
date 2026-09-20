# DESERT_PORT_PLACEHOLDER_ART_1 — 16 desert species still carry donor texPaths

## what is wrong

13 of 62 wired species across both desert biomes (8 fauna + 5 plants in
RUT_Desert; 4 fauna + 1 plant in RUT_ExtremeDesert; **16 unique defNames
total**) still carry donor texPaths (`Things/Pawn/Animal/AA_*`,
`Things/Plants/AB_*`, `swplants/*`). They render correctly only while Alpha
Animals, Alpha Biomes, or mlie stay subscribed, and go magenta the day any
donor mod is retired.

One is worse than fragile: **`RSW_Dunegrass` (surra grass) points at
`Things/Plants/AB_Aaklac`** — the def's own code comment admits this is the
wrong plant's art, so surra grass currently renders as an aaklac, today, with
every donor mod still present.

## why it matters

16 species are one donor-mod retirement away from rendering as magenta error
sprites, and one of them is already visibly wrong right now.

## the work

Queue all 16 through `fill_queue.py` — never hand-write the art. Land the
art, wire the new texPaths, deploy. Do surra grass first: it is the
top-weighted plant in RUT_Desert and is visibly wrong today, not just
fragile. Check `infrastructure/artpipe/done/` before queueing any of the 16
— per the standing rule (commit `96696811d`), some may already be rendered
and waiting.

## Watch out

This is the item other rows point at when they say "placeholder art, not
this item" — e.g. `DESERT_TABLES_DEPLOYED_AHEAD_OF_SPECIES_1` explicitly
defers 78 SWBestiary defs with no art at all to this item and the artpipe
queue. Do not fold that broader 78-def backlog into this item's scope; this
item is specifically the **16 donor-texPath species** named above, which
already have art (someone else's) rather than none.

## verify

All 16 defNames' texPath fields point at RSW_/RUT_-tier art, not a donor
path; a rendered contact sheet shows no magenta/placeholder sprites for any
of the 16; surra grass no longer renders as an aaklac.

## criteria

No shipped desert species depends on a donor mod remaining subscribed in
order to render correctly.
