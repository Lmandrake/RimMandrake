# Work bundle state: WB-game-direct-sun-20261127-034701

Onboarding run of the old tickets of home game:direct-sun (2 members), 2026-11-26 evening (PST). Steps A, B and C done.

## Step A

Kept 2, closed 0, dropped 0. Both read true against today's code.

## Outcomes

| ticket | outcome | commit | evidence |
|---|---|---|---|
| RIMMANDRAKE_GREY_TWO_LEGACY_MASTERS_THE_KIT_NAMES_EVERY_ROW | closed (fixed) | ada1b57cd754 (screens), 1f1efc51961f (selftest) | settings_audit: Greentide and TerminalBiomes 'declared', no cannot-grey note; selftest_settings_screens.py 866/866 (the masters plants caught on both screens); a planted unclassified key went FAIL |
| DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME | L1 done, L2 routed to the owner | 2beb5f8abea5 (scene, tier, bridge), a57737ec715a (PASS record) | `live_direct_sun_angle.py --verdict`: L1a, L1b, L1c PASS (run 6 on ArchBig); `design/specs/2026-11-26-direct-sun/live_angle_ArchBig_2026-11-26.log` |

The item DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME stays open on its route: L2 is the owner's tuning sitting (zenith,
weather sun factors, air-heat offsets, rest-dash strictness) and his look at the tree shade (T3). It resumes on his
words recorded on the item.

## Built on the way

- `src/RimMandrake/CreatureBehaviors/live_direct_sun_angle.py`: the L1 scene (Kind A, three rows), with its false
  starts written in its docstring.
- Tier `direct_sun_fixed` in `src/RimMandrake/Utils/modset_builder.py`: the pyrelands tier plus the Weather Suite and
  Ash'karr's PlanetGeometryDef, so a quicktest world has a fixed sun. ArchBig is left on it.
- `jawa/static_call` takes a MapComponent argument ('current' or a map index); deployed to ArchBig's BridgeTools.
- `selftest_settings_screens.py` plants from the first Declare that has a pure dependent.

## Lessons filed

`infrastructure/state/lessons/20261127T045602Z-BENCH-safe-advance-stops-every-hurt-pawn.md`,
`...-cell-temperature-lags-lazy-sun-fields.md`, `...-hold-pawn-sky-still-sun-scenes.md`.

## Not done, by design

- The fresh reader of the changed files (builder.md step 4) did not run: this brief forbids starting a helper or a
  subagent. The changed screens are covered by the masters contract and its planted faults; the scene by its planted
  deciders and six live runs.
- The live open of the two settings screens did not run (the offline contract decides it; the kit's drawer is the one
  Pyrelands uses live). Command, if wanted: `rimworld/open_mod_settings` with each mod's id, on a list that loads it
  (tier direct_sun_fixed loads both, inside mandrake.rm.biomes).

## Next

Nothing owed by this bundle.
