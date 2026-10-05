# belt_flowworksA 2026-10-05 — FOUNDRY FlowWorks builder

## 1 FLOWWORKS_BUILD_PROGRAM_1
(pending)

## 2 LIQUID_BODY_FLUID_IDENTITY_1 step 3
(pending)

## 3 PIT_FILL_EFFECTS_1
(pending)

## 4 FLOWWORKS_NORTHSTAR_SHIP_1 offline
(pending)

## 2 step 3: BUILT (stock reads body.fluid, debit unit per source, null-palette warning, ProofFillWithFluid + debug fill). Build 0 err; selftests 179/181 (UtinniPatches dump env + northstar flake, passes alone). Committing.

## 1 FLOWWORKS_BUILD_PROGRAM_1 -> Phase 6 Fire (next unbuilt; only a ships-OFF adjacent-Fire spike existed). Building RM_LiquidFire: per-cell burn state on the excavation grid, fuse/detonation front, burn = 1 tier/day canal, 1 level/5 days source (ruling 7), RM_LiquidFlame non-ticking visual, Fire.SpawnSetup hook for ignition.
- Phase 6 built: build 0 err, C# selftest 75/75 via dotnet.exe on D:\_rmbuild (it CAN run from WSL that way), northstar selftest PASS. Committing.

## 3 PIT_FILL_EFFECTS_1: building RM_PitFillEffects (drowning F>0@D=4 non-swimmers via swimmingGraphicData; poison FluidDef toxin x F/D; oil FluidDef = fuse via Phase 6 fire).
- PIT_FILL_EFFECTS_1 built: drowning/poison/oil defs, 77/77 C# selftest, northstar PASS. Committing.

## 4 FLOWWORKS_NORTHSTAR_SHIP_1 offline: reading item.
- Ship audit committed a0a8b8420. DONE: 85c1c0cce+82d36676c (step 3), db4dbf632 (Phase 6 fire), eabc44700 (PIT_FILL_EFFECTS_1), a0a8b8420 (ship audit). All offline; no live proof. C# selftest runs via dotnet.exe from D:\Luke\dev\_rmbuild (77/77).
