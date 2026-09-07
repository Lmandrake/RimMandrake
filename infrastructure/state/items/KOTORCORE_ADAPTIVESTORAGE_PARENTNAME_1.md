## Found while closing KOTORCORE_ABSORPTION_MISSING_TEXTURES_1

`validate_patch.py` against `src/RimStarWars/Armoury/Defs/Absorbed_AdditionalMods/`
with `--defs Data --defs Mods --defs workshop/294100` reports:

```
Absorbed_Kotorcore_AdaptiveStorageFramework_HiddenSmugglingCompartmentPanels.xml
  ThingDef 'Name=guy762_SecretFloorPanel_BASE': ParentName="AdaptiveStorageBase"
  resolves to no def carrying Name="AdaptiveStorageBase", in this mod or anywhere
  in the load set. The def fails to resolve and is DISCARDED - it will not exist
  in game.
```

This is a different defect class than the texPath/pink-placeholder findings that
item was scoped to (it's a dangling `ParentName`, not a missing texture), so it
was left untouched and filed here instead of folded into that close.

## Not yet investigated
- Whether `AdaptiveStorageBase` is a real `Name=` shipped by the "Adaptive
  Storage Framework" workshop mod itself (likely — the absorbed file's own
  directory name is `AdaptiveStorageFramework`) and whether that mod is active
  in the current ModsConfig.xml. If it is NOT active, this may be the same
  shape of bug as `KOTORWEAPONS_ABSORPTION_DANGLING_REFS_1` (latent-only,
  resolves fine today because the original donor pack is still active) — or it
  may be genuinely broken right now if Adaptive Storage Framework isn't active
  either.
- Whether the generator (`gen_additionalmods_absorption.py`) should have
  emitted its own `AdaptiveStorageBase` def, absorbed one from the Adaptive
  Storage Framework mod, or MayRequire-gated this file entirely.

## Criteria
Either: guy762_SecretFloorPanel_BASE resolves against the live mod set (confirm
by reading ModsConfig.xml and/or a def dump), or a real fix is applied and
validate_patch.py against this file drops to 0 errors.
