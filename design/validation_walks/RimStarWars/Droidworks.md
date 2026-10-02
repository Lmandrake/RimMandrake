# Droidworks — validation walk
subject: src/RimStarWars/Droidworks  (packageId mandrake.rsw.droidworks)
deps: erdelf.HumanoidAlienRaces (Humanoid Alien Races), brrainz.harmony (hard); Jawa Ion Weapons (mandrake local, soft — FindMod-gated patch, see check 4)
list: minimal+HumanoidAlienRaces   # HAR is a hard modDependency; Jawa Ion Weapons only needed to exercise check 4
status-hint: the one droid platform — five states (functional/ion-stunned/powered-down/unbootable/detonation), shop-centric repair, restraining bolts, faction-keyed data spikes, absorbing KotOR/Outer Rim/JDS droid rosters onto one framework

## must be true
- Every RSW_DW_ droid PawnKindDef (KotOR/JDS/OuterRim rosters, ~80 kinds across the three files) loads with no HAR cross-ref error and no "initial resistance/will range is undefined" Config error (PawnKind_HumanoidDroidResistanceWill.xml patches both onto every RSW_DW_ humanlike kind).
- RSW_DW_Power (NeedDef) exists and a spawned droid pawn carries it.
- The four core HediffDefs (RSW_DW_PoweredDown, RSW_DW_IonOverload, RSW_DW_RestrainingBolt, RSW_DW_BoltResentment) and RSW_DW_FormatTier read back with their defined stages/comps.
- RSW_DW_RebootDroid, RSW_DW_InstallRestrainingBolt, RSW_DW_RemoveRestrainingBolt, RSW_DW_MemoryWipe RecipeDefs exist with their documented workerClasses.
- The three charging buildings (RSW_DW_ChargeSocket/ChargeDock/ChargeNimbus) exist as CompPowerTrader buildings at their documented basePowerConsumption (100/150/800).
- IonBuildup_PowersDownDroid.xml is a FindMod-gated no-op when Jawa Ion Weapons is absent, and adds HediffCompProperties_IonOverloadsDroid onto RSW_JawaIon_Stun's comps when present.
- Two DEAD ends are known and NOT bugs to "fix" in this walk: RSW_DW_ClampBolt (JobDef) has no WorkGiver/float-menu that ever issues it (JobDefs_Droidworks.xml's own header says so), and CompDroidDetonation is built but never wired onto any race (Races_OuterRim.xml:1034 says so directly).

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.droidworks" and no XML error naming HediffDefs_Droidworks.xml, JobDefs_Droidworks.xml, NeedDefs_Droidworks.xml, RecipeDefs_Droidworks.xml, Races_Base.xml, Races_JDS.xml, Races_KotOR.xml, Races_OuterRim.xml, or Races_Families.xml
2. [L] on a load WITHOUT Jawa Ion Weapons active, Player.log does NOT show either PatchOperationFindMod match line for IonBuildup_PowersDownDroid.xml being applied (only the two PawnKind_HumanoidDroidResistanceWill.xml PatchOperationAdd lines should touch this mod's patches)
3. [D] def read-back: HediffDef RSW_DW_FormatTier exists; comps includes a CompProperties_DWFormatTier entry (Races_Base.xml wires CompDWFormatTier onto the droid race directly, not via the hediff)
4. [D] def read-back (only with Jawa Ion Weapons active): HediffDef RSW_JawaIon_Stun's comps list includes an `<li Class="RimMandrake.StarWars.Droidworks.HediffCompProperties_IonOverloadsDroid" />` entry (proves the FindMod patch actually matched and applied, since a non-matching patch logs nothing)
5. [D] def read-back: PawnKindDef entries under Defs/PawnKinds_KotOR.xml (44), Defs/PawnKinds_JDS.xml (16), Defs/PawnKinds_OuterRim.xml (20) whose race resolves and whose initialResistanceRange = "10~20" and initialWillRange = "5~10" (the PawnKind_HumanoidDroidResistanceWill.xml patch's flat placeholder values)
6. [D] def read-back: ThingDef RSW_DW_ChargeSocket/RSW_DW_ChargeDock/RSW_DW_ChargeNimbus each carry a CompPowerTrader comp with basePowerConsumption 100/150/800 respectively
7. [B] jawa/spawn_pawn {kind: one real RSW_DW_ PawnKindDef defName from PawnKinds_JDS.xml} → expect a live pawn of the droid race, fleshType RSW_DW_FleshType_Droid
8. [B] jawa/pawn_need {pawn: <spawned above>, need: RSW_DW_Power} → expect the need to exist and report a level (proves Patch_ShouldHaveNeed_Power's Harmony gate granted the need to this non-flesh-Humanlike pawn instead of silently skipping it)
9. [D] def read-back: RecipeDef RSW_DW_RebootDroid, RSW_DW_InstallRestrainingBolt, RSW_DW_RemoveRestrainingBolt, RSW_DW_MemoryWipe each resolve with workerClass RimMandrake.StarWars.Droidworks.Recipe_RebootDroid / Recipe_InstallRestrainingBolt / Recipe_RemoveRestrainingBolt / Recipe_DWMemoryWipe
X. [S] (human pass) droid five-state visual read (functional/ion-stunned/powered-down/unbootable/detonation) — icon/overlay legibility is out of scope here

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

**Droids**
- [ ] `droidworks_droids_read_as_droids` — a line-up of droid kinds (B1, HK,
      protocol, KX, Magnaguard) reads as machines, each recognisable as its chassis.
- [ ] `droidworks_droid_facings_hold` — each droid reads as the same chassis from
      north, east and south.

**The five states**
- [ ] `droidworks_states_distinguishable` — a functional droid, an ion-stunned
      one and a powered-down one (`RSW_DW_PoweredDown`) are distinguishable at a
      glance, without a tooltip. (guess: may need an overlay or posture)
- [ ] `droidworks_bolt_visible` — a droid fitted with a restraining bolt
      (`RSW_DW_RestrainingBolt`) shows it, or shows a readable marker. (guess)

**Charging**
- [ ] `droidworks_chargers_read_as_chargers` — `RSW_DW_ChargeSocket`,
      `RSW_DW_ChargeDock` and `RSW_DW_ChargeNimbus` read as three sizes of charging
      station, with a droid visibly docked at one.

### cannot show

- [ ] `droidworks_never_downed_like_flesh` — a powered-down droid drawn as a
      bleeding, collapsed flesh pawn. (guess)
- [ ] `droidworks_never_magenta` — a missing-texture square on any droid or droid
      building.
