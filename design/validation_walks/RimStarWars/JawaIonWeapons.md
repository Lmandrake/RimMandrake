# JawaIonWeapons — validation walk
subject: src/RimStarWars/JawaIonWeapons  (packageId mandrake.rsw.ionweapons)
deps: Neronix17.OuterRim.Core (hard dep, for ion bolt sprite + blaster audio + pulls VEF/Tabula Rasa); loadAfter brrainz.harmony, SmashPhil.VehicleFramework (soft, VEF vehicle tier self-disables if absent)
list: minimal+Neronix17.OuterRim.Core   # Vehicle Framework only needed to also validate VehicleTier/
status-hint: capture-not-kill ion blaster — RSW_JawaIon_Damage EMP-stuns mechs/droids near-instantly (empAmountMachine 60 / empAmountDroid 24) and, via DamageWorker_IonBuildup.cs, builds RSW_JawaIon_Stun severity on flesh pawns until they collapse alive with zero injuries.

## must be true
- DamageDef RSW_JawaIon_Damage exists: harmsHealth=false, makesBlood=false, workerClass=RimMandrake.StarWars.JawaIonWeapons.DamageWorker_IonBuildup, empAmountMachine=60, empAmountDroid=24, additionalHediffs has RSW_JawaIon_Stun at severityPerDamageDealt 0.03.
- ThingDef RSW_JawaIon_Blaster exists with weaponTags [RSW_JawaIon_Damage], recipeMaker.researchPrerequisite=RSW_JawaIon_Weaponry, statBases WorkToMake=16000/Mass=2.6/MarketValue=420, and verb defaultProjectile=RSW_JawaIon_Bullet.
- ThingDef RSW_JawaIon_Bullet exists, projectile.damageDef=RSW_JawaIon_Damage, damageAmountBase=8.
- HediffDef RSW_JawaIon_Stun exists: initialSeverity=0 (NOT the HediffDef default 0.5), maxSeverity=1.0, severityPerDay=-0.3, top stage ("overloaded", minSeverity 0.9) sets Consciousness setMax 0.10, and stages list is ascending (0, 0.35, 0.5, 0.9) with no duplicate/unreachable entry.
- ResearchProjectDef RSW_JawaIon_Weaponry exists, techLevel=Industrial, prerequisites=[Smithing], baseCost=400.
- Applying RSW_JawaIon_Damage to a mechanoid stuns it near-instantly (per the DamageDefs_JawaIon.xml history comment, mechs cannot be stunned by causeStun directly — only via the worker re-issuing vanilla EMP); applying it repeatedly to a flesh pawn downs it alive with zero injuries (harmsHealth=false holds).
- The mod's own README/About text calls DamageWorker_IonBuildup.cs "load-bearing" and "SILENT" (no Log calls) — its correctness can ONLY be checked via def read-back or live damage behavior, never via Player.log.
- VEHICLE_ION_TIER_1: VehicleIonPatches.cs self-disables with a Log.Warning (not a hard error) when SmashPhil.VehicleFramework is absent, and Log.Error's by name if reflection targets (VehiclePawn.PreApplyDamage, VehicleStatHandler.OverrideStunPatch) go missing.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.ionweapons" and no XML error naming DamageDefs_JawaIon.xml, HediffDefs_JawaIon.xml, ResearchProjectDefs_JawaIon.xml, StatDefs_JawaIon.xml, or ThingDefs_JawaIonBlaster.xml   # load-time
2. [D] jawa/get_def defType=DamageDef defName=RSW_JawaIon_Damage → workerClass="RimMandrake.StarWars.JawaIonWeapons.DamageWorker_IonBuildup", harmsHealth=false, makesBlood=false, empAmountMachine=60, empAmountDroid=24
3. [D] jawa/get_def defType=HediffDef defName=RSW_JawaIon_Stun → initialSeverity=0, comps include HediffCompProperties_SeverityPerDay severityPerDay=-0.3, stages ascending ending at minSeverity 0.9
4. [D] jawa/get_def defType=ThingDef defName=RSW_JawaIon_Blaster → recipeMaker.researchPrerequisite="RSW_JawaIon_Weaponry", weaponTags contains "RSW_JawaIon_Damage", statBases.WorkToMake=16000
5. [D] jawa/get_def defType=ThingDef defName=RSW_JawaIon_Bullet → projectile.damageDef="RSW_JawaIon_Damage", damageAmountBase=8
6. [D] jawa/get_def defType=ResearchProjectDef defName=RSW_JawaIon_Weaponry → techLevel=Industrial, prerequisites contains "Smithing"
7. [B] jawa/spawn_pawn kindDef=Mech_Scyther faction=hostile at (x,z) then jawa/damage damageDef=RSW_JawaIon_Damage amount=20 thingId=<pawn> → jawa/pawn_get shows the mech stunned (matches the 2026-08-22 measured baseline in the def's own history comment)
8. [B] jawa/spawn_pawn kindDef=<a flesh PawnKindDef, e.g. a Tribal warrior> faction=hostile at (x,z) then jawa/damage damageDef=RSW_JawaIon_Damage amount=8 thingId=<pawn> repeated ~6x → jawa/pawn_get shows the pawn downed, alive, hediffs contain RSW_JawaIon_Stun, and no injury hediffs (health log clean of wounds)
9. [D] jawa/get_def defType=ThingDef defName=BaseHumanMakeableGun (parent check only if RSW_JawaIon_Blaster fails to resolve — confirms the parent template itself still exists in the current mod set)
X. [S] (human pass) the blaster's bundled sprite (Textures/JawaIon/Weapon_JawaIonBlaster.png) and the fired-bolt look reusing Outer Rim Core's blue ion sprite/audio, read correctly in-game

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

**The weapon and its bolt**
- [ ] `ion_blaster_reads_in_hand` — `RSW_JawaIon_Blaster` held by a drafted Jawa
      reads as a blaster at a sensible scale.
- [ ] `ion_bolt_reads_as_ion` — `RSW_JawaIon_Bullet` in flight reads as a blue ion
      bolt, distinct from an ordinary blaster bolt. (guess)

**Capture, not kill**
- [ ] `ion_target_collapses_unhurt` — a flesh pawn shot down by ion fire lies
      downed with no blood pool and no wounds on its health tab.
- [ ] `ion_machine_stunned` — a mech or droid hit by ion fire shows the vanilla
      stun/EMP effect and stops moving.

### cannot show

- [ ] `ion_never_bloody` — blood splatter or bleeding wounds from an ion hit.
