# BOUNDARY: the vanilla beast route-leak census and its strike patch, Design Version 0.1.0

Code: `src/RimMandrake/Utils/vanilla_beast_cut.py` (`route_leaks`, `struck_pairs`, `struck_pairs_text`, `load`, the
`leaks:` line of `main`) and `src/RimUtinni/UtinniPatches/Patches/VanillaBeastExcision_RouteStrikes.xml`.
Item: `VANILLA_BEAST_LEAKS_EXCISE_ESCAPEES_AT_LARGE`, written 2026-11-26 by work bundle
WB-game-creatures-20261126-184717. Tests: `src/RimMandrake/Utils/selftest_vanilla_beast_cut.py`.

A Cherry Picker ThingDef cut neuters an official animal. It does not delete it, so a def that names the race, its kind
or its fertilized egg still spawns it. The census lists those defs. The strike patch removes the names we cannot cut.

## ACCEPTS (the only inputs this is built for)

- **a-def-dump.** `defs.sqlite` from RimDefDump, with `ThingDef`, `PawnKindDef`, `BiomeDef`, `FactionDef` and the
  `ROUTE_TYPES` rows.
- **the-ship-list.** `infrastructure/state/cherrypicker/CherryPicker.SHIP.xml`, which is the cut set. The dump is
  taken before Cherry Picker runs, so it cannot show a cut.
- **a-strike-patch-of-one-shape.** Each op is `PatchOperationConditional` on an xpath
  `/Defs/<Type>[defName="X"]/<path>/li[<field>="N" or ...]` with a `PatchOperationRemove` of the same xpath.

## DOES NOT SURVIVE (not promised)

- **a-field-below-the-dump-depth.** The dump writes `<maxdepth:ThingFilter>` where it stops, so a name inside a
  ThingFilter (the rare-catch eggs, for example) is not seen. The run prints the count of route defs with such a
  field. Their source XML decides.
- **a-route-chosen-in-csharp.** A route that picks its kind in code is seen only when `CSHARP_ROUTES` names it. The
  module docstring lists each C# worker that was read and its rule.
- **a-strike-xpath-that-matches-nothing.** The census counts a struck pair as closed from the xpath text. A dump that
  is taken after the patch ships shows the truth (`--strikes ''`).
- **a-machine-without-the-dump.** The dump half of the selftest reads UNMEASURED where no dump exists; run with
  `--offline` there.

## PROMISES

- **the-classifier-holds-back-what-waits.** An official race on an uncut roster, a faction carrier or a family (dryad,
  insect, Anomaly) is not cut now; a race that only a route def names is cut now, with the route listed.
- **a-cut-race-stays-watched-in-every-wave.** An uncut route def that names a race cut in any earlier wave, by its
  kind or its egg, is a leak; a RecipeDef mention, a cut route def and an uncut race are not; a struck pair closes
  only that pair.
- **a-cut-pack-animal-leaks-through-the-caravan-route-until-it-is-cut.** Each cut pack animal is a leak of
  `IncidentDef/VEE_CaravanAnimalsWanderIn` while that def is in the dump and not in the cut set; an owned pack animal
  never is.
- **a-strike-is-counted-only-in-the-shape-it-models.** `struck_pairs` reads each name of a conditional remove, and
  raises on any other op shape, so an unread strike is never counted as closed.
- **every-measured-leak-is-closed.** Each leak measured on the 2026-11-12 dump is struck by the strike patch, cut in
  SHIP, or gone from our own def's source; the patch strikes nothing that was not measured.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
