# DESERT_FORAGEDFOOD_INERT_1 — RUT_Desert forageability is inert, no foragedFood set

## what is wrong

RUT_Desert.xml sets `forageability 0.25` but has no `foragedFood` entry.
MEASURED (engine): `GetForagedFoodCountPerInterval` returns 0 whenever
`foragedFood` is unset, regardless of the `forageability` value. Caravans
forage nothing across the biome's 2,390 tiles, and the World tab gives no
signal that anything is wrong — the mechanic just silently does nothing.

## why it matters

A stated, weighted biome mechanic produces zero effect across every tile of
the biome, with no UI indication of the failure.

## the work

Set `<foragedFood>RSW_RawHubbaGourd</foragedFood>` in RUT_Desert.xml — the
wild gourd's own harvest item, already present in the roster; no new def
needed. In the same edit add
`<wildPlantsCareAboutLocalFertility>false</wildPlantsCareAboutLocalFertility>`
and `<lakeBeachTerrain>Sand</lakeBeachTerrain>` to match vanilla Core Desert's
fields.

## Watch out

This gap is documented for RUT_Desert only. Check whether RUT_ExtremeDesert
has the same `forageability`/`foragedFood` mismatch before assuming it is
fine — it was not checked in the source review.

## verify

RUT_Desert.xml has a non-empty `foragedFood` entry; a quicktest or debug
caravan on a Desert tile forages a nonzero amount.

## criteria

Caravans on RUT_Desert actually forage food; the mechanic the biome claims to
have is real.
