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

## Resolved 2026-09-08 — no fix needed, false alarm from bad --defs paths

- `ModsConfig.xml` (`/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml`)
  lists `adaptive.storage.framework` active in the current (full, 600-mod)
  load list.
- Its real workshop folder is
  `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3033901359`
  (packageId `adaptive.storage.framework`, name "Adaptive Storage Framework"),
  confirmed by grepping every workshop `About.xml` that references
  `adaptive.storage.framework` for the one whose OWN packageId is that string.
  Its `Defs/ThingDefBase.xml` defines `Name="AdaptiveStorageBase"` directly.
- Re-ran `validate_patch.py` against the actual absorbed file (its real path
  is `.../Absorbed_AdditionalMods/kotorcore/AdaptiveStorageFramework/Absorbed_Kotorcore_AdaptiveStorageFramework_HiddenSmugglingCompartmentPanels.xml`
  — the item's original path was missing the `kotorcore/AdaptiveStorageFramework/`
  subdirectory) with the real, resolvable roots:
  `--defs "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"
  --defs "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
  --defs "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"`.
  Result: `load set: 600 active mods, 600 found on disk` → **OK — 0 errors,
  0 warning(s)**.
- The bare `--defs Data --defs Mods --defs workshop/294100` invocation quoted
  in this item's opening finding is not resolvable from any cwd in this repo
  (confirmed: re-running it verbatim now returns `UNMEASURABLE - roots could
  not be read`, not a dangling-ParentName error) — the original finding was
  produced under different, unrecorded conditions (most likely the minimal
  13-mod quicktest list, where Adaptive Storage Framework is inactive and the
  same file genuinely would fail to resolve; see `gen_additionalmods_absorption.py`'s
  own header, which documents this pack's inclusion as already conditional on
  Adaptive Storage Framework being active).
- `gen_additionalmods_absorption.py`'s PACKS entry for
  `AdaptiveStorageFramework` (kotorcore donor, workshop 3254370945) was
  deliberately absorbed as "gate open" content specifically because Adaptive
  Storage Framework was confirmed active at generation time — this file's
  hard dependency on the real ASF mod (its `ParentName`, plus the
  `AdaptiveStorage.GraphicsDef` def type and `AdaptiveStorage.Extension`
  modExtension class it uses, both owned by that mod's C#) is intentional
  design, not an oversight. No `MayRequire` gate was added: this file was
  already unconditionally broken (hard XML-type errors from the
  `AdaptiveStorage.*` classes, not just a silent ParentName drop) if ASF is
  ever deactivated, so the criteria's first branch — "resolves against the
  live mod set" — is the correct closure, not a defensive gate.
- **No file changed under `Absorbed_AdditionalMods/` or the generator.**
  Closing as resolved-by-verification.
