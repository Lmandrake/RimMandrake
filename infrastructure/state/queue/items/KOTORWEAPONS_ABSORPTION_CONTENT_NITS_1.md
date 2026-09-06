# KOTORWEAPONS_ABSORPTION_CONTENT_NITS_1

Low-severity, donor-original content/flavor-text issues found during
DIRTY_CODE_REVIEW_STANDING_LOOP_1's pass over Absorbed_AdditionalMods/
Absorbed_KotorCore/Absorbed_KotorWeapons. None affect functionality — all
are cosmetic (label/description text) — so they did not block marking the
carrying files clean. Bundled here for an optional future flavor-text pass
rather than filed as individual bugs.

- `Absorbed_AdditionalMods/kotorweapons/TheForceLightsabers/Absorbed_Kotorweapons_TheForceLightsabers_HiltPartDefs_KotORColorCrystals.xml`
  — `guy762_SWForceLightsabers_CrystalPart_heart` ("Heart of the Guardian")
  has a description that's a verbatim copy-paste of the sibling
  `guy762_SWForceLightsabers_CrystalPart_mantle`'s ("The Mantle of the
  Force is an item assembled by Suvam Tan...") under the wrong label.
- `Absorbed_KotorWeapons/ThingDefs_Apparel/Absorbed_KotorWeapons_Apparel_ImmortalusSithLords.xml`
  — `guy762_MalgusArmor` description starts with a bare "." before its
  upgrade-slots list; `guy762_MalgusMask` and `guy762_MalgusHood`
  descriptions are literally just ".".
- `Absorbed_KotorWeapons/ThingDefs_Apparel/Absorbed_KotorWeapons_Apparel_KotORHeroApparel.xml`
  — `guy762_VisasHood` description is a bare Steam Workshop URL
  (`https://steamcommunity.com/sharedfiles/filedetails/?id=3378970100`)
  instead of prose; `guy762_VisasRobes` has the same "." placeholder.
- `Absorbed_KotorWeapons/ThingDefs_Weapons/Absorbed_KotorWeapons_WeaponMelee_KotORVibroblade.xml`
  — `guy762_vblade_sanasiki` carries a stray `<MeleeHitChance>1.2</MeleeHitChance>`
  inside `<statBases>`; not a real StatDef for weapons, almost certainly
  inert copy-paste debris rather than harmful, not independently confirmed.
- `Absorbed_KotorWeapons/ThingDefs_Weapons/Absorbed_KotorWeapons_WeaponRanged_KotORBlasterRifle.xml`
  — `guy762_brifle_jurgan` description has a typo: "wanteed" for "wanted".
- `Absorbed_KotorCore/ThingDefs_Buildings/Absorbed_KotorCore_Carpets.xml`
  — the abstract base (unusually doubles as a live `GS_Carpet_big` defName)
  sets label "large carpet"/description "a big carpet"; none of the three
  texture-distinct children (`GS_Carpet_Star`, `GS_Carpet_cult`,
  `GS_Carpet_forge`) override those fields, so all three show identical
  generic label/description in-game despite different art.
- `Absorbed_KotorCore/ProjectileDefs/Absorbed_KotorCore_Bullets_Special.xml`
  — `KotORBlasterBolt_nadd`/`_naddheavy` (~lines 353-357, 374-378) carry a
  donor-author `TO DO: needs DamageWorker that adds neural heat` comment;
  the weapons work, just without the intended extra effect.
- `Absorbed_KotorCore/Absorbed_KotorCore_RulePacks_StormtrooperNameMaker.xml:26`
  — an internal (never player-visible) rule-keyword path contains donor-author
  venting in its literal string. Harmless, just worth a name cleanup someday.
- `Absorbed_KotorWeapons/ThingDefs_Weapons/Absorbed_KotorWeapons_lightsabernames.xml`
  — `NamerWeaponLightsaber` RulePackDef randomly names lightsabers after
  Final Fantasy VI characters (Terra, Locke, Kefka, Bahamut...). Thematically
  odd for a Star Wars pack but functions fine; a design call whether to keep,
  not a bug.

No fix applied. Any of these can be picked up standalone whenever flavor
text is being passed over anyway; none blocks anything else.
