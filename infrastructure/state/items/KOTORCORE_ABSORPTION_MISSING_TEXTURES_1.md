# KOTORCORE_ABSORPTION_MISSING_TEXTURES_1

Found during DIRTY_CODE_REVIEW_STANDING_LOOP_1 pass over the
Absorbed_AdditionalMods/Absorbed_KotorCore/Absorbed_KotorWeapons pool.
`skills/rimworld-modding/scripts/validate_patch.py` run against all 235 XML
files in that pool with `--defs` pointed at the real Data + Workshop + Mods
folders (596 active mods, 596 found on disk — matches the live
ModsConfig.xml, confirmed by grep, 2026-09-06) returned 13 ERROR-level
findings across 8 files: a `texPath`/`uiIconPath` in the mod's OWN
`Things/` texture namespace that resolves nowhere the tool scanned, which the
tool distinguishes sharply from an unresolvable `Other/` or vanilla-shaped
path (10 separate WARN findings on `guy762_EShield*`'s `Other/ShieldBubble`
in `Absorbed_KotorWeapons_Hediff_Shields.xml` — NOT filed here, those are
correctly flagged as ambiguous-not-confirmed since vanilla textures live in
Unity asset bundles the tool cannot see).

Checked and RULED OUT as the cause: generator/source desync
(ARMOURY_LEATHER_GEN_DESYNC_1's pattern). Every affected file's `GENERATED
by src/RimStarWars/Armoury/Source/gen_*_absorption.py` header was checked
against the actual donor workshop folder mtimes: workshop 3254370945
(guy762.mm.kotorcore) and 2938932438 (guy762.KotORWeapons) both have their
newest file dated 2026-08-09/08-10, while the Absorbed_* files were
committed 2026-09-05 — the absorption ran AFTER the donor content was last
touched, so this is not a stale-generator-input case. These texPath values
were carried over verbatim from the donor mod's own (already broken, or
differently-versioned) XML.

## The 8 files / 13 findings

- `Absorbed_AdditionalMods/kotorcore/VEF/Absorbed_Kotorcore_VEF_Ysalamiri.xml`
  — PawnKindDef `SWPotF_ysalamir`, `dessicatedBodyGraphicData.texPath`
  `Things/Pawn/Animal/Iguana/Dessicated_Iguana` (x3, one per life stage).
  Confirmed this exact relative file DOES exist under workshop 1511926373 but
  only inside that mod's `v1.0/Textures/...Animal/Iguana/...` folder; its
  root `Textures/` and `v1.1/Textures/...` both use `AnimalCCP` instead of
  `Animal` — if RimWorld's per-version folder resolution picks the newest
  version <=1.6 (v1.1, not v1.0), the `Animal` path never loads. Whether
  1511926373 is even in the currently active 596-mod list is unconfirmed —
  check before assuming the fix is a path rename.
- `Absorbed_KotorCore/Absorbed_KotorCore_MotesAndFlecks.xml` — ThingDef
  `guy762_OrbMote`, `texPath` `Things/Mote/Smoke`.
- `Absorbed_KotorCore/DamageDefs/Absorbed_KotorCore_DamageAndProjectileDefs_KotORDroidUtilityWeapons.xml`
  — ThingDef `guy762_throwngrenade_foam`, `texPath` `Things/Mote/FoamSpray`.
- `Absorbed_KotorCore/ProjectileDefs/Absorbed_KotorCore_Bullets_Kinetics.xml`
  — ThingDefs `KotORDart_stun`/`_toxic`/`_saber`, `texPath`
  `Things/Projectile/Needle` (x3).
- `Absorbed_KotorCore/ThingDefs_Buildings/Absorbed_KotorCore_Structure_SWDoors.xml`
  — abstract ThingDef `Name="guy762_DoubleAutoDoorBase"`, `texPath`
  `Things/Building/OrnateDoor/OrnateDoor_MenuIcon`. It is an ABSTRACT
  ParentName base — check whether every concrete child overrides this field
  before treating it as a live pink placeholder; if a child inherits it
  unmodified, that child renders broken too.
- `Absorbed_KotorCore/ThingDefs_Buildings/Absorbed_KotorCore_Structure_SWWalls.xml`
  — abstract ThingDef `guy762_PoweredWallBase`: `uiIconPath`
  `Things/Building/Linked/WallSmooth_MenuIcon` AND `texPath`
  `Things/Building/Linked/Wall_Blueprint_Atlas`. Same abstract-base caveat as
  above. (This file also carries the dangling `relatedBuildCommands`
  autodoor references filed separately under
  `KOTORWEAPONS_ABSORPTION_DANGLING_REFS_1` — two independent defects in one
  file.)
- `Absorbed_KotorCore/ThingDefs_Resources/Absorbed_KotorCore_KotORResource_Metals2.xml`
  — ThingDef `KOTOR_Mineable`, `texPath`
  `Things/Building/Linked/RockFlecked_Atlas`.
- `Absorbed_KotorCore/ThingDefs_WeaponsArmorsGadgets/Absorbed_KotorCore__BASE_SWKotORWeapons.xml`
  — ThingDef `BulletDeflected`, `texPath` `Things/Projectile/Bullet_Small`.

## Not fixed here

Correcting a texPath needs either (a) finding the actual asset the donor mod
ships under a different name/case/folder, (b) confirming the abstract-base
cases are dead paths never inherited unmodified, or (c) generating new art
via the `generating-rimworld-sprites` skill if the donor mod itself always
shipped broken/placeholder content here — none of which is a bounded
one-line fix without doing that investigation per file. Recommend triage in
order: abstract-base overrides first (may be no-ops), then the two ambient
Mote/foam textures (probably need real assets or a stock-vanilla substitute),
then the ysalamir version-folder mismatch, then the remaining weapon/door
textures.
