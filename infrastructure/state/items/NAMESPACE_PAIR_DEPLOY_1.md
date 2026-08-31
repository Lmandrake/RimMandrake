# NAMESPACE_PAIR_DEPLOY_1 — the held XML+assembly pairs go out together

Phase 2a of the three-tier rename moved every C# namespace under the `RimMandrake.*`
root and left the XML that names those types on the old bare namespace. Found and
fixed in the repo by `RENAME_VERIFY_WINDOW_1`; the deploy could not happen because the
game was UP and the OS holds every `Mods/**/Assemblies/*.dll` open.

## spec
At the next **game-down** window, lift the block headed
`# --- The C# namespace rename: XML and ASSEMBLY must land together ---` in
`src/DEPLOY_HOLD.txt` and deploy each mod in one `--apply`:

```
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Inhabited       --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Droidworks      --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod JawaIkee        --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod JawaIonWeapons  --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod EmpirePursuit   --apply
```

The nine other rebuilt assemblies (Armoury, Pits, SacredGraffiti, JawaRules, Doctrine,
PlanetPresetPrime, RimDefDump, DesertVehicleReskin, PlantGrowth) are not held and go
out in the same pass.

⛔ **Never deploy one half.** `new XML + old DLL` and `old XML + new DLL` both produce
`Could not find type named …`, and a def that cannot resolve a
`Class`/`compClass`/`workerClass` is discarded or loses its comp — silently.

## verify
On the next load, `harvest_log.py` must show **zero** `Could not find type named` lines
naming `Droidworks.`, `Inhabited.`, `JawaIkee.`, `JawaIonWeapons.` or any
`RimMandrake.*`, and the Droidworks charger/recipe/job defs must still exist. The
EmpirePursuit ScenPartDef must load (its `scenPartClass` was already repaired and
deployed ahead of this item, because the deployed assembly never carried the broken
name).

## criteria
- [ ] All five mods deployed XML+assembly in one `--apply` each, game down.
- [ ] The DEPLOY_HOLD block deleted, not just commented out.
- [ ] Next load's log carries no `Could not find type named` for any of our namespaces.
