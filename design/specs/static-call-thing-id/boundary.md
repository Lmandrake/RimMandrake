# Boundary for Thing arguments in `jawa/static_call`

Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchStaticCallThingResolver.cs`.
Selftest: `python3 src/RimMandrake/Utils/selftest_static_call_args_core.py`.

## Accepts

The resolver takes a trimmed exact `ThingID` or a bare decimal `thingIDNumber`. It searches the current map first, then the other maps.

## Does not survive

Things absent from all map listers cannot be resolved by ID.

## Promises

- **thing-ids-resolve.** A Thing whose defName ends in a digit resolves by its exact `ThingID` and by its bare `thingIDNumber`.
