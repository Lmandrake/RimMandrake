# Pond chain build — BENCH night helper, 2026-10-13

Order of build (offline only; stop at "built, ready for a short live check"; no deploy). RETURN_LEG goes before
BED because BED's own title says "after the return leg and volume unify".

| item | state | sha | selftests | left |
|---|---|---|---|---|
| POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK | built (offline) | a9ecaad78dcb | C# 288/288, trips 13/13 | short live check; tank family art |
| POND_RETURN_LEG_BUILD_WATER_GOES_HOME | built (offline) | (this commit) | C# 291/291, trips 13/13 (trip 6 now a full round trip) | live L3/L6 + dug-bed check |
| POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE | pending | - | - | - |
| POND_ELEVATION_BUILD_LAKES_RUN_DEEP | pending | - | - | - |

## POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK
Built: RM_Volume (one square = 4 levels = 20 units), pond capacity = Σ bed (deep 4 / shallow 2), 5:1 field deleted
(C# + 13 XML rows), tanks sized by footprint (2x2 = 80, cargo tank tall = 160), versioned save migration, overfull
tanks keep every unit. Selftests: C# 288/288 (4 new Volume_* cases), conservation 13/13 (trips 7, 11-13).
FlowWorks --only sweep 23/23 GREEN. Owed: tank footprint family + tall twins need art (owner/art ledger).
Prose: `infrastructure/state/items/POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK.md`.

## POND_RETURN_LEG_BUILD_WATER_GOES_HOME
Built: pump Pour and hose outflow ends return whole levels to a pond or its dried bed (new RM_OutletKind.Body, one
OutletLeg for all three sites); honest pond round-trip selftest; refill waits for pawns/buildings, items wash ashore
(skip-and-requeue); checked Restore; dug dry bed leaves its pond and returns on fill-in (G5 fixed); truncated-index
persistence; L0 ledger dev action. 3 new Mod Settings. Prose: `infrastructure/state/items/POND_RETURN_LEG_BUILD_WATER_GOES_HOME.md`.

## POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE
(pending)

## POND_ELEVATION_BUILD_LAKES_RUN_DEEP
(pending)
