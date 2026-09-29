# GASDAMAGING_PARENTNAME_UNRESOLVED_1 — RM_BaseGasDamaging ParentName never resolves

## what was found

Found incidentally during `THEY_MOD_REPLICATION_1`'s live-verify pass, 2026-09-28, on a
full 614-mod `Player.log`:

```
XML error: Could not find parent node named "RM_BaseGasDamaging" for node "ThingDef".
```

One occurrence on the full-list boot. Not chased down that pass — that item fixed three
other instances of the identical defect class (`RM_ChillHeatedSuit`→`Apparel_Vacsuit`,
`RM_SandBusterMound`→`Hive`, `RM_SandBusterTunnel`→`TunnelHiveSpawner`; see its own
2026-09-28 entry for the full root-cause writeup and the RimSage evidence against
`Verse/XmlInheritance.cs`).

## the mechanism (already established, re-stated here so this item is self-contained)

RimWorld's `XmlInheritance.GetBestParentFor` indexes inheritance-parent candidates
**only** by an XML node's own `Name="..."` attribute, never by `<defName>`. A
`ParentName="X"` referencing a def whose node has no `Name="X"` attribute — i.e. any
concrete/playable def, as opposed to an abstract template — silently fails to resolve,
logs `Could not find parent node named "X"`, and leaves every field that node meant to
inherit unset (for a `ThingDef`, most dangerously `thingClass`, which NREs
`ReadingPolicyDatabase.GenerateStartingPolicies()` inside `Game..ctor()` the moment the
def is active for ANY fresh `Game` — new colony, quicktest, or save load).

## what's needed here specifically

1. Find which of our `ThingDef`(s) declare `ParentName="RM_BaseGasDamaging"`
   (`grep -rn 'ParentName="RM_BaseGasDamaging"' src/`).
2. Find where `RM_BaseGasDamaging` itself is meant to be declared — check whether it
   ever carried a `Name="RM_BaseGasDamaging"` attribute (a genuine abstract template
   that regressed) or never did (same authoring mistake as the three fixed in
   `THEY_MOD_REPLICATION_1`).
3. Fix by either adding the missing `Name=` attribute to the intended abstract base (if
   one exists and was meant to be a template), or by restating the fields the child(ren)
   needed directly, same pattern as the three fixed instances.
4. Deploy, restart (minimal tier is fine — this doesn't need the full list to prove),
   confirm the specific "Could not find parent node named" line is gone and no
   null-`thingClass` Config error appears for the affected def(s).

## why this matters

Same severity class as what blocked `THEY_MOD_REPLICATION_1`'s own live verify: a def in
this state can crash `Game..ctor()` for ANY fresh game construction once it's active,
silently, with no Config-error line naming it directly (the crash is generic — "has null
thingClass" only fires from `ConfigErrors()`, which is a separate check from the
`Game..ctor()` crash path and may not always catch it depending on which field is
missing).

## a broader sweep is probably owed, not chased here

Given this is the **fourth** live instance of this exact defect class found in one day
(three in `THEY_MOD_REPLICATION_1`, this one), a repo-wide grep for `ParentName="X"`
where `X` has no matching `Name="X"` anywhere in an active mod's defs (ours or vanilla)
would likely find more. That sweep is bigger than this one def and is scoped out of this
item — worth its own item if the owner wants it done proactively rather than reactively
(one crash at a time, discovered only when something happens to construct a `Game` with
the bad def active).

## RESOLVED 2026-09-28 (FOUNDRY, found while live-verifying BMT_FAUNA_ABSORPTION_1) — NOT the
## authoring mistake this item assumed

The abstract base **does** carry `Name="RM_BaseGasDamaging"` correctly — MEASURED by reading
the deployed `RimMandrake.Biomes/Biomes/_Kits/EnvironmentalHazards/Defs/ThingDefs/RM_GasBases.xml`
directly (line 39: `<ThingDef Name="RM_BaseGasDamaging" ParentName="RM_BaseGas" Abstract="True">`).
So this is a **different** defect from the three `THEY_MOD_REPLICATION_1` fixed (which really were
missing `Name=`). The real mechanism, confirmed by the crash log (`GenTypes.SameOrSubclassOf`
NREing on a null `thingClass` inside `ReadingPolicyDatabase.GenerateStartingPolicies()`, per
`Verse/ThingDef.cs ConfigErrors()`'s own `"has null thingClass."` line, which DOES appear for
`RUT_ChokingSpores` specifically — `Config error in RUT_ChokingSpores: has null thingClass.`):

**Load order.** `BAROQUE_BIOMES_WAVE2_FOLD_1` (2026-09-28) folded four previously-standalone
mods into `mandrake.rm.biomes`'s `LoadFolders.xml` (`Biomes/_Kits/CreatureBehaviors`,
`Biomes/_Kits/EnvironmentalHazards`, etc.) but **left four dependent mods' `About.xml`
`loadAfter`/`modDependencies` still naming the now-defunct standalone packageIds**
(`mandrake.rm.creaturebehaviors`, `mandrake.rm.environmentalhazards`) — which don't exist in
the active list any more, so the constraint is a silent no-op (same class of defect as
`GASDAMAGING`'s own sibling note elsewhere in this repo about inert `MayRequire`). Measured via
`ModsConfig.xml` index comparison: `mandrake.rut.rotsporekit` (467), `mandrake.rm.shipvermin`
(547), `mandrake.rsw.swbestiary` (544) and `mandrake.rm.explosivegrowth` (566) all sat well
**before** `mandrake.rm.biomes` (612) in the live 614-mod load order. For an XML `ParentName`
(RotSporeKit's `RUT_ChokingSpores` → `RM_BaseGasDamaging`) and for C# typerefs alike
(ShipVermin's whole assembly failed `Assembly.GetTypes()` — `ReflectionTypeLoadException`
because `RimMandrake.CreatureBehaviors.RM_Alert_VerminPopulationBase` couldn't resolve, which
poisoned every type in `RimMandrake.ShipVermin.dll` including `RM_CompProperties_VerminNest`,
breaking `WreckVerminNest_ShipChunk.xml`'s patch too), resolution against a same-mod-list
target that hasn't loaded yet fails — same shape, two different resolution mechanisms.

**Fix (commit pending in this session):**
- `src/RimMandrake/ShipVermin/About/About.xml`, `src/RimStarWars/SWBestiary/About/About.xml`,
  `src/RimMandrake/ExplosiveGrowth/About/About.xml`: repointed `loadAfter`/`modDependencies`
  from the defunct `mandrake.rm.creaturebehaviors`/`mandrake.rm.environmentalhazards` to
  `mandrake.rm.biomes`, deployed.
- `RotSporeKit`'s deployed `About/About.xml` hand-edited the same way (**no repo source tracks
  this mod at all** — not in `deploy_custom_mods.py`'s known-mods list, no `src/` folder found;
  see the note this leaves below).
- Live `ModsConfig.xml` reordered (backed up first:
  `infrastructure/state/modlists/ModsConfig_BACKUP_before_loadorder_fix_shipvermin_rotsporekit_20260928T220532Z.xml`
  and `..._swbestiary_explosivegrowth_20260928T220805Z.xml`) to move all four affected
  packageIds to immediately after `mandrake.rm.biomes`.
- `mandrake.rm.flowworks`'s deployed DLL was ALSO stale (missing `RM_NoRecreationalSwimExtension`,
  a `ManyWaters` class merged in by the same wave) — rebuilt from committed source
  (`dll_source_stamp.py check` now MATCHes) and redeployed.
- **VERIFIED on a fresh full-list cold load, 2026-09-28~21:49-21:59 PDT**: zero
  `"has null thingClass"`, zero `"Could not find parent node named"`, zero ShipVermin
  `ReflectionTypeLoadException`, zero `"Could not find type named"` for either fixed class.
  The canonical save subsequently loaded all the way to `programState: Playing` (not just
  `mapData`) — first time this session a fresh `Game` construction succeeded at all.

**Left open, not this item's fix:** `RotSporeKit` (`mandrake.rut.rotsporekit`, 151 files per
`TheRot/About.xml`'s "absorbs" note) has **zero repo source** — it's not in
`deploy_custom_mods.py`'s mod list and no `src/` folder matches it. Its own `RUT_ChokingSpores`
def (with `RUT_` tier defNames, distinct from `TheRot`'s absorbed `RM_ChokingSpores` twin) isn't
reproducible from anything in this repo. Whether it should be captured into the repo, or
whether `TheRot`'s absorption means it should finally be retired (its own About.xml suggests
absorption already happened design-wise, but the mod is still active and shipping seemingly
duplicate RUT-tier content), is a BENCH/owner call — not decided or acted on here, only the
load-order symptom was fixed. Also unswept: the broader "`ParentName="X"` where no active mod
declares `Name="X"`" sweep this item's own text already flagged as owed.
