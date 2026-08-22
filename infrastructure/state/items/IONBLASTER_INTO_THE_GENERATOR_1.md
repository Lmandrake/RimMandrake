## spec
`src/Jawa/Jawa_Patches/Patches/JawaIon_FieldOurOwnGun.xml` (CHECK, 2026-08-22, deployed and
verified) adds `JawaIon_Damage` to the `weaponTags` of `Jawa_TradeMoot_Heavy`,
`_Specialist` and `_Leader`, so the campaign's signature weapon is finally fielded by
somebody. **It is a stopgap.**

`Defs/PawnKindDefs/JawaFactionRoster.xml` is emitted by
`src/RimMandrake/Utils/gen_pawnkind_roster.py`. **The next run of that generator will not
know about the patch** — the patch will still apply on top, but the roster table and the
shipped defs will disagree, which is exactly the drift the generator exists to prevent.

## the durable fix
Add `"JawaIon_Damage"` to the tag lists on generator rows **227, 228, 229**:

    227: ("TradeMoot","Heavy","crawler guard",450,130,("max","Normal"),
          ["KotORRanged_ion","Jawa_IonWeapon","KotORRanged_weak"],["guy762_Robes_jawa"]),
    228: ("TradeMoot","Specialist","Scrap-Singer",900,160,("max","Normal"),
          ["Jawa_IonWeapon","KotORRanged_ion"],["guy762_Robes_jawa"]),
    229: ("TradeMoot","Leader","First Bargainer Kiknik the Wealthy",900,250,("max","Good"),
          ["KotORRanged_ion","Jawa_IonWeapon"],["guy762_Robes_jawa"]),

Then re-emit and **delete the patch file** in the same commit, so there is one source again.

⛔ **Row 226, the Grunt, is deliberately excluded** — `weaponMoney` 250-300 against a
420-silver blaster. `PawnWeaponGenerator` filters by market value, so the tag would be a
silent no-op there.

## the second defect, worth fixing in the same pass
`Jawa_TradeMoot_Grunt`'s `Jawa_IonWeaponLight` tag resolves to `IW_Gun_IonPistol` (800) and
`IW_Gun_IonPDW` (1000) — **both far above its 300 ceiling.** Its only affordable ion today
is `guy762_ionpistol` (200) via `KotORRanged_ion`. So the Grunt carries a tag that can never
fire. Either drop `Jawa_IonWeaponLight` from row 226 or raise the ceiling — but note the
guidance doc treats the Jawa's lowest-on-the-map weapon budget as a design feature, not an
accident.

## criteria
`gen_pawnkind_roster.py` re-emitted, the three kinds carry `JawaIon_Damage` in
`JawaFactionRoster.xml` itself, and `JawaIon_FieldOurOwnGun.xml` is gone.

Evidence and the measurement behind it: `design/Jawa/worldbuilding/faction_equipment_clusters.md`.
