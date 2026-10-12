# IDEO_DEITY_HUNT_GOD_WITH_NO_NAME

## Symptom
Every debug quicktest worldgen on the 23-mod ratchet_pilot+patches tier logs one
`Error in WorldGenStep: System.NullReferenceException` from
`IdeoFoundation_Deity.GenerateTextSymbols` → `SetupFromSymbolPack`, reached via
`IdeoGenerator.MakeFixedIdeo` ← `FactionGenerator.NewGeneratedFaction` (VEF postfix on the stack).
Measured 2026-10-12d: 3 worldgens, 3 hits (`Transient/bench_live_20261012d/Player.pilot_tier.log` lines 309/411/474).
The same trace is in the 20261011, 20261012, 20261012b and 20261012c pilot/prev-session logs; no item named it.

## Attribution: UNMEASURED
A FIXED ideo (a FactionDef with a fixed ideo / `IdeoGenerationParms.fixedIdeo`) whose deity foundation has no
usable symbol pack for its culture or memes. Which faction is unknown: the trace does not name the FactionDef.
It may be ours (an RM/RSW/RUT faction or culture) or a donor's.

## NEXT
List the FactionDefs on the 23-mod tier that generate a fixed ideo with a deity structure, and check each one's
culture/meme symbol packs (RimSage + the def dump); or log the facDef at `CreateFactionAndAddToManager` on one
quicktest. Fix it if ours; record the owner mod if not.
