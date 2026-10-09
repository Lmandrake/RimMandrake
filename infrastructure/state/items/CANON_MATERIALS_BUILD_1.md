# CANON_MATERIALS_BUILD_1 — build the decided canon materials design

## spec
Spec: `design/RimMandrake/canon_materials_design_2026-10-09.md` — §3 (materials, sources, defs), §4 (key
jobs), §5 (build duties). Parent: CANON_MATERIALS_DESIGN_1, closed on the owner's 2026-10-09 rulings (cards,
recorded as decisions taken by question card; one typed: *"Not a great idea, ignore"* on ancient-vs-Empire
incompatibility, so nothing here checks a part's era).

## criteria
- L1 L0: `RSW_Durasteel` exists in the RimStarWars tier with `KOTOR_AlloyDurasteel`'s stats, sharp armor power raised to 0.9; no recipe, mineable or deep-drill producer makes it
- L2 L0: every donor durasteel of §3.2 converts to or yields `RSW_Durasteel` and is no longer produced; donor defs stay loadable for saves
- L3 L0: both recipe audits done and written into this item: fixed `Plasteel` costs untouched where the consumer needs plasteel, durasteel references redirected, broad filters admitting both listed
- L4 L0: no recipe produces `Plasteel`; Odyssey asteroid generation (`SpaceMapGenerator.xml`, `GeneratedLocations.xml` paths) no longer places `MineablePlasteel` or `MineableComponentsIndustrial`, by explicit allowlist
- L5 L0: salvage (ship chunks, crashed ships, B1 remains) yields durasteel, plasteel, duranium and doonium by composition, with no double plasteel route from B1 remains
- L6 L0: `RSW_Phrik`, `RSW_Transparisteel`, `RSW_Stygium`, `RSW_Coaxium` defined as trade goods with canon descriptions, stocked by orbital traders and the Bazaar, with no other source; donor stygium items convert to `RSW_Stygium`
- L7 L1: one minimal-list load with the touched mods shows no config or cross-reference errors naming any def above
- L8 L4: owner confirms the proposed key-job list (§4: hulls and blast doors durasteel, droid shells and prosthetics plasteel, large frames duranium, cores doonium)
- L9 L0: after L8, those jobs take only their material through fixed ingredient lists; every other job still accepts any eligible material; a Mod Settings toggle (default on) turns key-job exclusivity off

## verify
Record each with `rimflow verify CANON_MATERIALS_BUILD_1 --criterion <ID> --result pass|fail|partial --evidence <path>`.
L0 is offline (def parse, validate_patch, selftests); L1 is one minimal-list load read through Player.log; L4 is
the owner in a sitting. L9 waits on L8: do not enforce exclusivity on an unconfirmed list.
