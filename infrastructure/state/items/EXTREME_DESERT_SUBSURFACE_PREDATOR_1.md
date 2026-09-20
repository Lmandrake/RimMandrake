# EXTREME_DESERT_SUBSURFACE_PREDATOR_1 — replace AA_Dunealisk with a real predator

## what is wrong

`AA_Dunealisk` — the roster's documented "one legal predator archetype"
(subsurface strike, dune_sea §6) — was correctly removed along with the rest
of the `-lisk` clade (`WYYYSCHOKK_FERALISK_MERGE_1`), and nothing replaced it.
The Krayt dragon fills a "dune-swimmer" icon role but is a giant, not the
drum-lure/sand-strike role the sheet calls for. deep_desert §8's **drum-lure
subsurface predator** and its **egg-trap clutch** sit in `new_defs` with no
item at all.

## why it matters

RUT_ExtremeDesert currently has zero implemented predators matching its own
design sheet's stated archetype.

## the work

Port `AA_SandLion` (already ruled at 0.5 weight, "sand burrower swimmer"
role) via `DESERT_ROUND2_IMPORTS_UNLANDED_1`'s port batch, as the interim
strike predator. File the drum-lure subsurface predator and its egg-trap
clutch as their own creature item — it needs C# (a vibration-lure job, the
roster's "mechanic_load" entry). Before filing that item, check
`SARLACC_HABITAT_BUILD_1` — it already owns birth-trap clutches and may cover
the egg-trap half of this.

## Watch out

This item's interim fix is entirely gated on `DESERT_ROUND2_IMPORTS_UNLANDED_1`
landing `AA_SandLion`. Do not file the drum-lure predator's clutch mechanic
without first confirming against `SARLACC_HABITAT_BUILD_1` whether it already
owns that ground — filing a duplicate clutch mechanic wastes the work.

## verify

RUT_ExtremeDesert's `wildAnimals` carries a predator matching the "subsurface
strike" role (`AA_SandLion` at minimum); a filed item exists for the
drum-lure predator + egg-trap clutch, cross-referencing
`SARLACC_HABITAT_BUILD_1`'s actual scope.

## criteria

The extreme desert has a real predator matching its design sheet, not just a
giant filling an icon role it wasn't written for.
