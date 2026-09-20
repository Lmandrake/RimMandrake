# DESERT_DEF_HEADER_STALE_COUNTS_1 — def header comments carry stale counts and donor names

## what is wrong

RUT_Desert's def header comment states "3,932 tiles" and RUT_ExtremeDesert's
states "3,172 tiles"; the current worldmap CSV gives **2,390 tiles for
RUT_Desert** and **3,969 tiles for RUT_ExtremeDesert** — both figures are
wrong, and they get the two biomes' relative sizes backwards. Plant row
comments in the same files still name the old donor identities — "hardy
grass", "aaklac", "dessert tree" — against the plants' actual ruled names,
**surra grass / vellara bloom / dommo tree**. This is false text shipped in
a live def file.

## why it matters

Per the standing rule that correctness outranks seat ownership, false text
in a shipped file is wrong the moment it's read, regardless of who owns the
file — and these particular numbers get the two biomes' relative sizes
backwards, which misleads anyone reasoning from the comment instead of the
CSV.

## the work

Delete the tile-count figures from both header comments entirely and point
at the CSV as the source of truth instead of restating a number that will go
stale again. Fix the three plant-name comments to read surra grass / vellara
bloom / dommo tree. One commit, explicit paths (both `RUT_Desert.xml` and
`RUT_ExtremeDesert.xml`).

## Watch out

Do not just update the numbers to 2,390/3,969 — those will go stale again
the next time the CSV is repainted (as it apparently already has been at
least once). Point at the CSV, don't restate its content.

## verify

Neither def header comment contains a tile count; both files' plant comments
use the three ruled names, not the donor identities.

## criteria

No def file comment states a fact that can go stale without the def itself
changing.
