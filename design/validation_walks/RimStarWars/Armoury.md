# Armoury — validation walk
subject: src/RimStarWars/Armoury  (packageId mandrake.rsw.armoury)
deps: brrainz.harmony, guy762.mm.kotorcore, oskarpotocki.vanillafactionsexpanded.core, adaptive.storage.framework, ebsg.framework, neronix17.outerrim.core (all hard per About.xml — absorbed content's Class= refs resolve to these frameworks with no MayRequire gate)
list: full     # About.xml's own note: without VEF/AdaptiveStorageFramework/EBSG present, several absorbed defs (SWPotF_RaceDef_ysalamir, guy762_SecretFloorPanel_BASE, guy762 implants) fail to load at all
status-hint: rebalances the whole mod list's weapon/armor damage ladder to setting physics via generated FindMod patches, plus a large absorbed KotOR content library and several small standalone C# comps (KoltoTank, MentalBreakBlocker, SecondaryMineableYield, MinePocket, JumppackForMeleeAI).

## must be true
- Generated ranged/armor/melee patches (Armoury_RangedDamage.xml, Armour_Ratings.xml, Armoury_MeleePower.xml, Armour_Penetration.xml) write their recorded values onto matched third-party defs when those source mods are active — result, not "applied" log text.
- RSW_Sonic_Cannon (native, not absorbed) loads as a working two-handed ranged weapon firing KotORSonicWave_heavy.
- The absorbed KotOR content trees (Defs/Absorbed_KotorCore, Absorbed_KotorWeapons, Absorbed_AdditionalMods) load with zero Config errors given the required frameworks are present.
- KoltoTankBase (thingClass KoltoTank.Building_KoltoTank) is a real, resolvable comp-backed building, not an inert defName.
- MentalBreakBlocker and SecondaryMineableYield's Harmony patches apply cleanly at startup.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.armoury" and no XML error naming any Absorbed_KotorCore/Absorbed_KotorWeapons/Absorbed_AdditionalMods file   # load-time
2. [D] def read-back: ThingDef RSW_Sonic_Cannon exists; ParentName=KotORRangedMakeable_TwoHand, statBases/MarketValue=2600, verbs/li/defaultProjectile=KotORSonicWave_heavy
3. [D] def read-back: ThingDef KoltoTankBase exists; thingClass=KoltoTank.Building_KoltoTank
4. [D] patch result (requires Alpha Mechs active): ThingDef AM_Bullet_SniperTurret/projectile/damageAmountBase = 200 (Armoury_RangedDamage.xml's generated value)
5. [D] patch result (requires Alpha Genes active): ThingDef AG_Forsaken_Hood/statBases/ArmorRating_Sharp = 1.40 (Armour_Ratings.xml's generated value)
6. [L] Player.log contains "[MentalBreakBlocker] Harmony patch complete!"
7. [L] Player.log contains "[SecondaryMineableYield] Harmony patch complete!"
8. [B] jawa/get_def {defName: "RSW_Sonic_Cannon"} → returns a ThingDef with the same statBases as check 2, confirming it resolves at runtime not just on disk
9. [S] (human pass) sonic cannon sprite (reused kotorsonrifle_arkanian) and GenStep_ScatterLightsaberCrystals placement — visual only

## north star
state: DRAFT
validated-hash:

Seeded 2026-10-01 by an agent (NORTH_STAR_WALK_AUTHORING_1) from this walk's
`## must be true` and the mod's shipped sprites, defs and settings, on the owner's
ruling that day: *"You are mostly seeding the field right now with reasonable
initial guesses for refinement later through debugging needs or live feedback."*
Every line is an agent guess for him to accept, edit or cut; `(guess)` marks the
least certain. `### the experience` is his to dictate.

### the experience  (OWNER'S WORDS)
(not yet dictated)

### must show

**Worn armour and outfits**
- [ ] `armoury_outfits_read_star_wars` — a colonist in an absorbed outfit (Sith
      trooper, Republic trooper, Mandalorian, Jedi tunic) reads at play zoom as that
      faction's look, not generic rimworld armour.
- [ ] `armoury_worn_art_all_facings` — worn armour is drawn on the body from north,
      east and south, with no facing going bare or showing the front art on the
      back.
- [ ] `armoury_outfit_fits_body_types` — the same outfit sits on thin, fat and
      hulk bodies without floating off or clipping wildly. (guess)

**Weapons in hand and in flight**
- [ ] `armoury_weapon_drawn_in_hand` — a drafted pawn holds a blaster or
      `RSW_Sonic_Cannon` drawn at a sensible scale and angle.
- [ ] `armoury_bolts_read_as_blaster_fire` — a firefight shows coloured bolts or
      waves, not vanilla bullets. (guess)

**Buildings**
- [ ] `armoury_kolto_tank_reads_as_tank` — a built `KoltoTankBase` reads as a
      medical tank a pawn floats in. (guess)

### cannot show

- [ ] `armoury_never_magenta` — a magenta or missing-texture square on any worn,
      held or placed Armoury item.
- [ ] `armoury_never_floating_gear` — apparel drawn detached from the pawn
      (offset off the body), the classic absorbed-art offset defect. (guess)
