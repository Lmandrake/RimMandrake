# The Systech Static Blaster lost its distinctive electric projectile

## what happened
`guy762.mm.kotorcore` retired 2026-09-19 (`WEAPONS_DONOR_RETIREMENT_1`). Our
absorbed Systech Static Blaster fired `KotORElectricBolt`, a projectile whose
`Class` comes from **AthenaPort** — which is exactly why absorption excluded it
(`Armoury/Defs/Absorbed_KotorCore/Absorbed_KotorCore_BLOCKED_manifest.txt`,
line 19). It resolved only because the donor was still loaded. The cold load
that retired the donor reported it:

```
Could not resolve cross-reference: No Verse.ThingDef named KotORElectricBolt
found to give to Verse.VerbProperties VerbProperties(Systech Static Blaster)
```

A null `defaultProjectile` is a weapon that cannot fire, so it was repointed the
same day to `KotORIonBolt_default` — the projectile its three sibling ion
weapons in the same file already use, and which IS absorbed. The weapon works;
it just no longer looks different from its siblings.

`src/RimStarWars/Armoury/Defs/Absorbed_KotorWeapons/ThingDefs_Weapons/Absorbed_KotorWeapons_WeaponRanged_KotORIonPistol.xml`

## the actual question, which is a design call
Should the Systech Static Blaster have a distinct electric projectile of our
own — a `ThingDef` under `Absorbed_KotorWeapons` or a new RSW_-named one, with
its own texture and its own `damageDef` — or is riding the standard ion bolt
fine? It is the only "static/electric" weapon in the family, so the flavour was
doing real work.

⛔ Do NOT re-add `KotORElectricBolt`: the donor's version needs an AthenaPort
class we do not ship and did not absorb. A replacement is a NEW def of ours.

## criteria
- [x] Owner (or a design pass) rules: distinct projectile, or ion bolt is fine.
- [ ] If distinct: projectile def + art + damageDef authored, validate_patch
      clean, and the weapon seen firing it in a live load.

## decision, 2026-09-19 (FOUNDRY, autonomous — no owner ruling recorded)
**DISTINCT.** Riding `KotORIonBolt_default` is not a "some other weapon in the
file already does this and it's fine" precedent — it's a category mismatch.
The three sibling ion pistols in the same file (`guy762_ionpistol`,
`_verpine`, `_aratech`) are genuinely ion weapons: their fluff and their
`extraDamages EMP` bonus are about droids. The Systech's own description is
about the opposite target — bypassing a *creature's* (veermok) blaster
resistance — so the EMP bonus it was riding does nothing for its stated
purpose. Reusing the ion bolt wasn't "an acceptable simplification of the same
idea," it was a stopgap that quietly changed what the weapon is about.

Built new, not resurrected:
- `RSW_RangedDamage_electrical` (`src/RimStarWars/Armoury/Defs/DamageDefs/RSW_ElectricalDamage.xml`)
  — `ParentName="guy762_RangedDamage_energy"`, `additionalHediffs` granting
  `guy762_Electrocuted`. This is the RANGED sibling of an already-absorbed
  MELEE damage def, `guy762_MeleeDamage_electrical`
  (`Absorbed_KotorCore_MeleeDamages.xml`) — same shape, just not
  `isRanged=false`. `guy762_Electrocuted` already exists in this mod set and
  the Systech's own `descriptionHyperlinks` already point at it; nothing
  ranged had ever actually applied it before this.
- `RSW_ElectricArcBolt_default` (`src/RimStarWars/Armoury/Defs/ThingDefs/RSW_ElectricArcBolt.xml`)
  — same base as `KotORIonBolt_default` (`guy762_BaseBullet_VehicleDamageReducer`),
  fires `RSW_RangedDamage_electrical`, same order-of-magnitude damage (8) so
  this is an identity fix, not a rebalance.
- **No new art.** `Weapons/Projectiles/zap.png` already ships in this mod's own
  Textures folder (a lightning-bolt sprite) and no def in the pack referenced
  it — confirmed by grep before reuse, same zero-art-cost pattern already used
  by `RSW_Sonic_Cannon.xml`.
- Systech's `defaultProjectile` repointed from `KotORIonBolt_default` to
  `RSW_ElectricArcBolt_default`; verb comment rewritten to record this history.

**Owed, explicitly not attempted here:** "the weapon seen firing it in a live
load" — that's a live-quicktest criterion and this pass did not touch the
bridge. Also owed, separately and NOT decided here: whether Systech's overall
damage should be rebalanced under this mod's own "the verb IS the weapon"
doctrine (`Armoury/Defs/ThingDefs/RSW_Sonic_Cannon.xml`'s header) now that its
fluff describes real anti-creature use rather than a near-zero utility
effect — left at parity with the ion bolt on purpose, a bigger call than this
item asked for.

`validate_patch.py` (both `--defs` across Data/Mods/Workshop and `--live`
against `DefDump/captures/2026-09-19T04-19-13Z`): **0 errors, 0 warnings**
across all three touched files.
