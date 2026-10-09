# Thurlsponge wreck colonisation — 2026-10-09 (BENCH helper)

## Status
started

## Design text

## Existing mechanisms found

## Implementation

## Build / selftests

## Live checks owed
- design §4 (the_scald_underwater_flora_pass_2026-09-27.md): "They colonize the wrecks for the iron — a hull the pan swallowed wears a coat of them within a generation". Placement section names no mechanism for wrecks (thurlsponge is Route A only).
- wrecks: RUT_ScaldWreck{Hull,Tank,Frame} placed by Wreckage's RM_GenStep_WreckField RM_WreckField_Scald (order 965) via RM_TheScald/RUT_TheScald extraGenSteps, shallow band only (RUT_ScaldShallow, radius 2). No wrecks on the floor map.
- reuse: Twilight RM_GenStep_TwilightFloraDressing host-adjacent pattern (33846bde3) — but its TrySpawnPlant rejects water terrain, Scald shallows ARE water, so a Scald copy of the loop with its own spawn check. Registration: same extraGenSteps patch file as the wreck field.
- Hull crust (Grey) is a runtime ship-crust clock, wrong shape. Wreckage has no plant-dressing hook.
- wrote Source/RM_ScaldThurlspongeWrecks.cs (genstep 966), setting scaldThurlspongeWrecksEnabled (Scald section), GenStepDef Defs/MapGeneration/RM_ScaldThurlspongeWrecks.xml, registered in Patches/RUT_ScaldWreckScatter_Register.xml; XML parses. next: build
- build: winbuild OK, 0 warnings/0 errors
- selftests: PASS 279/347, FAIL 1 = selftest_utinnipatches_dump.py (known stale dump, filed) — not ours
## Live checks owed
- new Scald surface map: thurlsponge present on cells touching RUT_ScaldWreck* (CanSpawnAt on shallow water not proven live); toggle off -> none. Runtime wreck-falls (RM_IncidentWorker_WreckFall) are not colonised (design names map-gen coat only).
- not deployed.
