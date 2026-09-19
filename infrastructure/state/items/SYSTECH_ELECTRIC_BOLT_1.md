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
- [ ] Owner (or a design pass) rules: distinct projectile, or ion bolt is fine.
- [ ] If distinct: projectile def + art + damageDef authored, validate_patch
      clean, and the weapon seen firing it in a live load.
