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
- [x] All five mods deployed XML+assembly in one `--apply` each, game down (2026-08-31,
      FOUNDRY): `Inhabited` (4 files), `Droidworks` (11), `JawaIkee` (2), `JawaIonWeapons`
      (5), `EmpirePursuit` (1 — rebuild-only, XML already correct). The nine other rebuilt
      assemblies went out in the same window.
- [x] The DEPLOY_HOLD block deleted (both the namespace-pair block and the EmpirePursuit
      block, lines 154-213), not commented out. Commit `9e0629cb`.
- [x] Next load's log carries zero `Could not find type named` for any of our namespaces
      — confirmed twice (a first restart, then a second after two further regressions
      the same load surfaced — see below). `grep -c "Could not find type named"` = 2,
      both pre-existing `VanillaFurnitureExpanded` hits, unrelated to us.

## Also caught on the confirming loads — not this item's own scope, but found here
Three more genuine regressions surfaced by `harvest_log.py`'s standing checks on the
post-deploy loads, all fixed and re-verified clean (final load: every standing check
and queued check at baseline, 0 deltas):
1. `SelfHediffVerb`'s ported Harmony patch targeted `Verb.EquipmentSource` as a plain
   method; it's a property — needed `MethodType.Getter`. Was a dead mod (static-ctor
   RED). Commit `315332f3`.
2. The rename's find-replace hit the literal string "Burn" wherever it appeared as a
   VALUE, not just our own defName declarations — corrupting 8 genuine references to
   vanilla's `Burn` DamageDef into a name nothing defines (`cross-reference` RED, +8
   over baseline), plus 2 prose labels and a live bridge tool's validation set. Same
   commit.
3. Two DEPLOYED patches referenced `RSW_Gun_ArchotechChargeBlasterHeavyTurret` /
   `RSW_Bullet_ArchotechChargeBlasterHeavy` — our own eweb/opturret absorbed defNames,
   which are HELD/undeployed pending retirement — instead of the still-live
   third-party originals (`Gun_ArchotechChargeBlasterHeavyTurret` /
   `Bullet_ArchotechChargeBlasterHeavy`, mod "Archotech Blaster Turret"). Both patch
   operations were silently failing live (`patch operations failed` RED, +2). Commit
   `6d50a65b`.

Checked the sibling JDS Armory / kotorweapons `RSW_JDSA_*` references live via the
bridge before assuming the same bug: those absorbed copies ARE deployed now, so those
patches correctly target them — not a regression, confirmed not touched.
