# KOTORWEAPONS_ABSORPTION_DANGLING_REFS_1

**CORRECTED 2026-09-06** — the original filing below over-claimed. `mcp__rimsage__search_defs`/`get_def_details`
has ZERO coverage of any `guy762`/kotor content (confirmed: it returns "not found" even for
`guy762_RangedDamage_energy`, a defName independently confirmed live by direct grep of the
active donor mod's own source). The rimsage def dump this filing leaned on is stale/scoped
away from this pool entirely — its "not found" was never real evidence here. Re-verified
everything below directly against the actual Steam Workshop source files on disk instead.

## Re-verified: NOT a current bug (downgraded)

`guy762.mm.kotorcore` (workshop 3254370945) IS active in the live ModsConfig.xml, and its own
`1.6/Defs/ProjectileDefs/Bullets_HomingProjectiles.xml` and `Bullets_Special.xml` DO define
`KotORMissile_seeker`, `KotORMissile_whistlingbird`, `KotORMissile_highex`, `KotORMissile_plasma`,
`KotORMissile_ion`, `KotORMissile_buster`, and `KotORElectricBolt` (confirmed by grep of the
workshop folder directly). Its own `1.6/Defs/ThingDefs_Buildings/Structure_SWDoors.xml` and
`Structure_SWWalls.xml` also define every `guy762_Autodoor1x1_*`/`guy762_DoubleAutodoor_*VerticalA`
defName referenced from our `Absorbed_KotorCore_Structure_SWWalls.xml`'s `relatedBuildCommands`.

So every one of these cross-references resolves fine TODAY via the still-active original mod.
The BLOCKED_manifest.txt exclusion only means these defNames were not copied into OUR absorbed
mirror (because their comp classes weren't ported) — it does not mean they've stopped existing
in the game. This is a LATENT risk only: if/when `guy762.mm.kotorcore` retires without these
comp classes being ported into JawaArmoury.dll first, the following defaultProjectile/
relatedBuildCommands references will start dangling:
- `Absorbed_KotorWeapons/ModularPartDefs/Absorbed_KotorWeapons_ModularPartDefs_Wristgun.xml`
  (KotORMissile_seeker, KotORMissile_whistlingbird)
- `Absorbed_KotorWeapons/ModularPartDefs/Absorbed_KotorWeapons_ModularPartDefs_JetpackMissile.xml`
  (KotORMissile_highex/plasma/ion/buster)
- `Absorbed_KotorWeapons/ThingDefs_Weapons/Absorbed_KotorWeapons_WeaponRanged_KotORIonPistol.xml`
  (KotORElectricBolt)
- `Absorbed_KotorCore/ThingDefs_Buildings/Absorbed_KotorCore_Structure_SWWalls.xml`
  (autodoor relatedBuildCommands — this file also has an unrelated missing-texture defect,
  still tracked in `KOTORCORE_ABSORPTION_MISSING_TEXTURES_1`)

No action needed now. Worth a one-line note wherever `guy762.mm.kotorcore`'s eventual
retirement is tracked (no such item exists yet as of this writing) so whoever retires it
checks these four files first.

## FIXED: generator wrote an excluded, unresolvable comp class anyway

`Absorbed_KotorWeapons/ThingDefs_Weapons/Absorbed_KotorWeapons_WeaponRanged_KotORHeavyRepeater.xml`'s
5 ThingDefs (`guy762_hvyrepeater`, `_mando`, `_massdriver`, `_baragwin`, `_ordo`) each carried
a LIVE, uncommented `<li Class="SWCP.Core.CompProperties_PositionAttributes">`, despite this
pack's own `Absorbed_KotorWeapons_BLOCKED_manifest.txt` listing these exact 5 defNames as
excluded for that same class match. SWCP is confirmed not in the live ModsConfig.xml, so this
would throw a comp-class config error on all 5 weapons. Sibling files
(`WeaponRanged_KotORMiningLaser.xml`, `WeaponRanged_KotORBlasterRifle.xml`) correctly
commented out their own manifest-blocked entries — this was an isolated generator failure in
one file. **FIXED**: commented out the cosmetic-only (held-weapon draw offset) comp block in
all 5 defs, matching the established sibling-file pattern; `validate_patch.py` clean after.

Correction this implies: since these 5 ThingDefs DO in fact exist in this file (the manifest's
"not written to any Defs/ file" claim was wrong for this one), the ShowMeYourHands
`handmodpositioning.xml` references to `guy762_hvyrepeater`+variants below are NOT dangling —
they resolve fine.

## Still a REAL, confirmed-live bug

`guy762.KotORWeapons` (workshop 2938932438) is CONFIRMED ABSENT from the live ModsConfig.xml
(per the closed `WEAPONTAGS_RENORMALISE_STALE_DEFS_1`, itself verified by disk read not a
dump). `guy762_mininglaser` was correctly omitted from `WeaponRanged_KotORMiningLaser.xml`
(consistent with the manifest), and `guy762_brifle_sith`/`guy762_brifle_rohlan` are confirmed
absent everywhere (per the closed item above) — none of these three were absorbed anywhere.
So these three ARE dangling today, live, in:

- `Absorbed_AdditionalMods/kotorweapons/ShowMeYourHands/Absorbed_Kotorweapons_ShowMeYourHands_handmodpositioning.xml`
  — references `guy762_brifle_sith`, `guy762_brifle_rohlan`, `guy762_mininglaser` (plus the
  now-resolved `guy762_hvyrepeater`+variants, see above). Likely a defName-keyed hand-position
  dictionary (ShowMeYourHands mod pattern) that silently no-ops on a dictionary miss rather
  than erroring — NOT verified; if wrong, affected pawns using whatever weapon those keys
  were meant to reposition hands for would use a wrong/default hand pose, not crash.

Also newly found: `Absorbed_KotorWeapons/ModularPartDefs/Absorbed_KotorWeapons_ModularPartDefs_HelmetArmorTech.xml`
line ~302, `guy762_KotORpartArmorTech_kneerocket`'s `<ability><ammoDef>guy762_DroidWeapon_microrocket</ammoDef>`
— this defName is absent from the whole repo and the live def dump (grepped directly, no
rimsage-staleness caveat applies here). Donor is `guy762.KotORWeapons` (retired), so this is a
live dangling ref: the kneerocket upgrade's ammo/reload likely can't resolve. Not fixed — the
right replacement ammoDef isn't obvious without knowing what this ability was meant to fire.

## Not fixed here

Confirming the ShowMeYourHands miss is silent-safe (vs. a real error) needs either reading
ShowMeYourHands' own C# (not available to a Defs-only review) or a live game load with
Player.log capture. Recommend: verify against a real Player.log, or read
ShowMeYourHands' HandModPositioning lookup code if a decompile/source copy is available,
before deciding whether this needs a fix or is cosmetically inert like the door/wall
texture case in the sibling item.
