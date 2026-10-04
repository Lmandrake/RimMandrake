# ARMOURY_PROJECTILE_DAMAGE_TOOL_1

Child of NORTHSTAR_PARTIAL_GAPS_FILL_1 (Armoury row: "the weapon-ladder rebalance has no component asserting any
weapon damage value"). The melee half landed in r30 (`573ff19f0`, chain `melee_ladder_landed`). The ranged half
needs a C# bridge tool, and this item specs that tool so a C# window can build it in one sitting.

## why a tool is needed (MEASURED, RimSage 2026-10-03)

`Verse.ProjectileProperties` declares `private int damageAmountBase = -1;` (line 18) and
`private float armorPenetrationBase = -1f;` (line 20). `jawa/get_defs` with `deep=true` reflects PUBLIC fields
only, so `projectile/damageAmountBase` cannot be read. The public accessors are:

- `public int GetDamageAmount(ThingDef weapon, ThingDef weaponStuff, StringBuilder explanation = null)` (line 122)
- `public int GetDamageAmount(float damageMultiplier, Thing weapon, StringBuilder explanation = null)` (line 128):
  uses `damageAmountBase` when it is not -1, else `damageDef.defaultDamage`
- `public float GetArmorPenetration(Thing weapon = null, StringBuilder explanation = null)` (line 160)

## spec

The tool, below.

`jawa/projectile_damage` in a new `JawaBenchProjectileTools.cs` (remember the csproj `<Compile Include>` if that
project lists files explicitly).

- **input** `defs`: ONE semicolon-separated STRING of projectile ThingDef names (the `get_defs` convention; never a
  list). Optional `includeWeapons=true`: also accept weapon ThingDefs and follow
  `Verbs[0].defaultProjectile`.
- **per def, return**: `defName`, `found`, `isProjectile` (`def.projectile != null`), `damageDef` (defName),
  `damageAmountBase` (the raw private field read with `AccessTools.Field(typeof(ProjectileProperties),
  "damageAmountBase")`; -1 means unset), `damageAmount` (`projectile.GetDamageAmount((ThingDef)null, null)`, so
  unset reads as the damageDef default), `armorPenetrationBase` (raw private field), `armorPenetration`
  (`GetArmorPenetration(null)`).
- **top level**: `success`, `foundCount`, `notFound`, exactly as `get_defs`, so `shipped_defs._get_defs`-style
  callers can read the same three fields. A def that exists but is not a projectile is `found: true,
  isProjectile: false` (DATA, never a throw).
- Read-only, no map needed, safe at the main menu.

## the chain it unblocks (Python, no further C#)

`ranged_ladder_landed` in `src/RimStarWars/Armoury/validation.py`, mirroring `melee_ladder_landed`:
parse every `PatchOperationReplace` whose xpath is
`/Defs/ThingDef[defName="X"]/projectile/damageAmountBase` in the GENERATED `Patches/Armoury_RangedDamage.xml`
(86 operations at r31, grouped by `PatchOperationFindMod`), call the tool on the loaded ones, and require
`damageAmountBase == <value>` for each. Our absorbed defs must all be loaded; a donor's defs count only when that
`FindMod` donor is active (same rule as the melee chain). Add the parse and a mock-backed red case to
`selftest_armoury.py` (not_landed / lost / garbage / blind, as the melee half has).

## verify

- Vanilla controls (Core `RangedIndustrial.xml`, RimSage): `Bullet_Revolver` reads `damageAmountBase` 12 and
  `damageAmount` 12; `Bullet_IncendiaryLauncher` authors no base, so it reads `damageAmountBase` -1 and
  `damageAmount` equal to `Flame`'s default; `Gun_Revolver` with `includeWeapons=true` follows to `Bullet_Revolver`.
- `ranged_ladder_landed` PASSes live on the full list, and its selftest reddens on each break.
