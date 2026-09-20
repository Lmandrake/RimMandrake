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

🔴 **CORRECTED 2026-09-20:** `DESERT_ROUND2_IMPORTS_UNLANDED_1` closed without
porting `AA_SandLion` — it explicitly stayed out of that item's scope because
this item already owned it. Its named successor, `AA_JOE_DESERT_PORT_BATCH_1`,
also explicitly excludes `AA_SandLion` for the same reason. Porting
`AA_SandLion` (already ruled at 0.5 weight, "sand burrower swimmer" role) is
this item's own owed work, not something riding on another item's batch.

Port `AA_SandLion` as the interim strike predator. File the drum-lure
subsurface predator and its egg-trap clutch as their own creature item — it
needs C# (a vibration-lure job, the roster's "mechanic_load" entry). Before
filing that item, check `SARLACC_HABITAT_BUILD_1` — it already owns birth-trap
clutches and may cover the egg-trap half of this.

## Watch out

Do not file the drum-lure predator's clutch mechanic without first confirming
against `SARLACC_HABITAT_BUILD_1` whether it already owns that ground —
filing a duplicate clutch mechanic wastes the work.

## verify

RUT_ExtremeDesert's `wildAnimals` carries a predator matching the "subsurface
strike" role (`AA_SandLion` at minimum); a filed item exists for the
drum-lure predator + egg-trap clutch, cross-referencing
`SARLACC_HABITAT_BUILD_1`'s actual scope.

## criteria

The extreme desert has a real predator matching its design sheet, not just a
giant filling an icon role it wasn't written for.
