# GPT top-ten review — verdicts (GPT_FULL_REVIEW_TOP10_1)

Every concrete Part-1 (DEBUGGING) claim in the ten GPT reviews beside this file, checked against
the source on disk (2026-10-08, offline only, no game run). GPT claims are evidence, not findings:
a claim is **real** only when the cited code does what GPT says; **false** when the code does not;
**unclear** when it cannot be settled from source (engine behaviour, live state).

Action column: **fixed `<sha>`** (small and clear, done here) · **filed `<ITEM>`** (larger) ·
**none** (false, or real but harmless/by design, reason given).

Parts 2–4 (complications, opportunities, extensions) are not verdicted here.

## CreatureBehaviors

Part 1 only. 32 claims: 31 real (claim 26 is a documented by-design trade-off), 1 false, 0 unclear. 23 fixed in source (some only in part), 4 items to file.

| # | claim (short) | verdict | evidence (file:line, one line) | action |
|---|---|---|---|---|
| 1 | Discharge recurses before cooldown set | real | RM_CompDefensiveDischarge.cs: `attacker.TakeDamage(shock)` ran before `lastDischargeTick = now`; two carriers ping-pong via PostPostApplyDamage | fixed (cooldown set first + static re-entry guard) |
| 2 | Wound link picks wrong "fresh" injury; ignores zero damage | real | RM_CompWoundLink.cs FindFreshInjury: largest `ageTicks<=0` injury; multi-hit/mirrored-in wounds same tick are indistinguishable; totalDamageDealt unread | fixed partly (reject totalDamageDealt<=0); file → WOUNDLINK_INJURY_IDENTITY_1 for per-event identification |
| 3 | Source healed though no kin received a wound | real | RM_CompWoundLink.cs: MirrorInjury returned void on no-equivalent-part, Heal ran unconditionally | fixed (MirrorInjury returns bool; heal only if any mirrored) |
| 4 | Shared amount can exceed source wound | real | shareFraction default 0.6 × settings slider up to 2 (RM_CreatureBehaviorsMod.cs:614) = 1.2 | fixed (Clamp01 on effective fraction) |
| 5 | Equivalent part collapses onto first match (L/R) | real | RM_CompWoundLink.cs FindEquivalentPart matches only `BodyPartDef` | file → WOUNDLINK_INJURY_IDENTITY_1 |
| 6 | Kin mending heals full amount per injury | real | RM_HediffComp_KinMending.cs ApplyMendingBoost: `injury.Heal(healAmount)` in loop over every injury; comment defines heal/day per carrier | fixed (one budget per cycle consumed by actual heal) |
| 7 | Psychic stun cooldown not saved | real | RM_CompProximityPsychicStun.cs: `lastTriggerTick` field, no PostExposeData | fixed (Scribe key `rmPsychicStunLastTriggerTick`) |
| 8 | Cycle counters discard overshoot | real (latent: defaults 2500/15000 divide 250) | KinMending + RM_CompShardArmor.cs reset to full interval | fixed (carry remainder) |
| 9 | Shade grid off freezes burst recovery | real | RM_HediffComp_ShadeDrivenSeverity.cs gated on shadeGridEnabled; tooltip (Mod.cs:659) says grid-off = full sun; sun rate is -0.5/day decay | fixed (gate only on heatDrivenBurstEnabled; ShadeAt returns 0 when grid off) |
| 10 | HostileTo scan misses current hunt target | real (narrow) | GenHostility.IsPredatorHostileTo makes a predator hostile to a FACTION pawn it hunts (≤12 cells), but returns false for factionless wild prey — so Aquatic:100 / HeatBurst:96 / DrumLure:158 never fire on wild prey | file → CREATURE_JOB_INTERRUPTION_POLICY_1 (targeting policy is a design call) |
| 11 | Ambusher re-hides mid-lunge | real | RM_CompAquaticAmbusher.cs Evaluate: BecomeInvisible when scan empty & submerged; mid-lunge guard only inside TriggerLunge | file → CREATURE_JOB_INTERRUPTION_POLICY_1 |
| 12 | Forced jobs override drafted/mental/player orders | real | Aquatic TriggerLunge, DrumLure ForceGotoLure/Ambush, HeatBurst TryRetreatToShade: `StartJob(..InterruptForced)` with no Drafted/InMentalState check (FalseShade:96 has them) | file → CREATURE_JOB_INTERRUPTION_POLICY_1 |
| 13 | False-shade strike ignores LOS/reach | real | RM_CompFalseShadeAmbusher.cs FindVictim: distance only, then TakeDamage | fixed (GenSight.LineOfSight gate on candidates) |
| 14 | False-shade AttackMelee has no leash | real | Seize: AttackMelee expiryInterval 600, no distance fail condition; header claims "no pursuit" | file → CREATURE_JOB_INTERRUPTION_POLICY_1 |
| 15 | Heat retreat treats any Goto as retreat | real | RM_CompHeatBurstPredator.cs TryRetreatToShade: `curJob.def == Goto` returns | fixed (only a Goto whose destination is shaded ≥ threshold counts); "hunt carries it back into sun" half → file → CREATURE_JOB_INTERRUPTION_POLICY_1 |
| 16 | Lure stays assigned after its goto fails | real | RM_CompDrumLure.cs StillLured returns true when luredHediff null; no reachability/timeout | file → CREATURE_JOB_INTERRUPTION_POLICY_1 |
| 17 | Lure cleanup skipped when carrier downed/dead | real | RM_CompDrumLure.cs CompTick: activity guard returned before the disabled-option ClearLure | fixed (option-off ClearLure moved before the activity guard); death/despawn cleanup → file → CREATURE_JOB_INTERRUPTION_POLICY_1 |
| 18 | Tether ropes invisible pawns | real | RM_CompTetherPull.cs FindTarget: LOS only, doc says "visible hostile" | fixed (skip `IsPsychologicallyInvisible()`, InvisibilityUtility.cs:8) |
| 19 | Nearer rescue beats farther hostile | real | FindTarget: single closest over hostile∪rescue; contract "hostile … else rescue" | fixed (separate bests, hostile first) |
| 20 | TryRope bypasses constraints / NRE on null | real (latent) | only callers: CompTick via FindTarget (validated) and RM_Building_TractionLance.cs:289 proof hook | fixed (null guard); unrestricted proof path left as intended |
| 21 | Tether despawn doesn't release host | real | RM_CompTetherPull.cs: no PostDeSpawn; release only from CompTick | fixed (PostDeSpawn(Map, DestroyMode) → Release(null,"off"), ThingComp.cs:39) |
| 22 | SandSwim Submerge with null submergedHediff | real | RM_CompSandSwim.cs Submerge: `MakeHediff(Ext.submergedHediff…)` unguarded; RM_SandSwimExtension.cs:84 only reports a ConfigError | fixed (null guard in Submerge) |
| 23 | Kill signs ignore master switch | real | RM_CompSandSwim.cs Notify_SwimmerKilled: no `sandSwimEnabled` check | fixed (gated on sandSwimEnabled); the "only after a breach" part was left alone (low value) |
| 24 | Rumble volume change ignored while playing | real | RM_CompSandSwim.cs MaintainRumble: volumeFactor only set at spawn | fixed (tracks the setting; recreates the sustainer when it changes) |
| 25 | Cached false shade follows moving/downed pawns | real | RM_FalseShade.cs FalseShadeAt re-checked only Spawned/Map | fixed (re-checks Dead/Downed/Moving per read) |
| 26 | Harvested sight blocker opaque up to 2000 ticks | real, by design | RM_CompSightBlocker.cs:99-101 comment documents the 2000-tick worst case as acceptable for plants | none (documented trade-off; only plants consume it) |
| 27 | Movable sight blockers never refresh on move | false | only consumer is Greentide/Defs/ThingDefs_Plants/RM_Greentide_UnderstoryRoster.xml (plants do not move) | none (no movable consumer) |
| 28 | Ranged hits get the melee rescue roll | real | RM_CompGrappler.cs PostPostApplyDamage: any Pawn instigator; RM_CompProperties_Grappler.cs:19,46 says melee hit | fixed (attacker must be adjacent, same map) |
| 29 | Single-cell adhesive surfaces scan the whole map | real | RM_CompAdhesiveSlick.cs FindPawnsInRange iterated AllPawnsSpawned even at radius 0 | fixed (radius ≤ 0 reads the cell's thing list) |
| 30 | Specimen proof counts attempted, not placed | real | RM_CompResearchSpecimens.cs PostDestroy ignored TryPlaceThing's result, and statics were never reset on early return | fixed (statics reset at entry; counts only a successful placement) |
| 31 | Reel proof skips production cadence | real (proof gap) | RM_CompTetherPull.cs DebugReelNow → ReelStep with no timer or CanWork | file → TETHER_PRODUCTION_REEL_PROOF_1 |
| 32 | Harmony catch reports "guard off" falsely | real | RM_FlightJobStartGuard.cs: one try wrapped both patches | fixed (diagnostic prefix gets its own try and reports that the guard is ON) |

#### Files changed
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_CompDefensiveDischarge.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_CompProximityPsychicStun.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_CompWoundLink.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_HediffComp_KinMending.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_CompShardArmor.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_HediffComp_ShadeDrivenSeverity.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_CompDrumLure.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_CompHeatBurstPredator.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_CompFalseShadeAmbusher.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_CompTetherPull.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_CompSandSwim.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_FalseShade.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_CompGrappler.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_CompAdhesiveSlick.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_CompResearchSpecimens.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Source/RM_FlightJobStartGuard.cs
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Assemblies/RimMandrake.CreatureBehaviors.dll (rebuilt)
- /home/mandrake/rm/foundry/src/RimMandrake/CreatureBehaviors/Assemblies/RimMandrake.CreatureBehaviors.dll.srchash (rebuilt)

#### Items to file
| NAME | title | spec |
|---|---|---|
| CREATURE_JOB_INTERRUPTION_POLICY_1 | One shared targeting and interruption policy for the forced-job creature comps | RM_CompAquaticAmbusher.TriggerLunge, RM_CompDrumLure.ForceGotoLure/Ambush and RM_CompHeatBurstPredator.TryRetreatToShade all `StartJob(InterruptForced)` with no Drafted/InMentalState/player-faction check (RM_CompFalseShadeAmbusher.cs:96 shows the guard shape). Their HostileTo-only scans never target factionless wild prey, because GenHostility.IsPredatorHostileTo returns false for those. Fold in: the ambusher re-hides mid-lunge (Evaluate runs BecomeInvisible before TriggerLunge's own lunge guard); the false-shade AttackMelee has no leash (expiry 600 only); a drum lure with null luredHediff stays assigned forever and has no reachability check, timeout or death/despawn cleanup; heat-retreat does not stop a hunt from carrying the pawn back into the sun. Define the allowed interruption states and the prey policy once, then apply them to all four comps. |
| WOUNDLINK_INJURY_IDENTITY_1 | Wound link should mirror the injury this hit made, onto the matching body part | RM_CompWoundLink.FindFreshInjury takes the largest injury with `ageTicks<=0`, so two hits in one tick, or a wound mirrored in from kin, can be shared again. FindEquivalentPart matches only BodyPartDef, so left/right parts collapse onto the first match. Capture the injuries added by this DamageInfo (diff the hediff set, or a pre-damage snapshot in PreApplyDamage) and match on the body-tree path. The zero-damage guard and the clamp are already in. |
| TETHER_PRODUCTION_REEL_PROOF_1 | Tether proof should run the real production tick | RM_CompTetherPull.DebugReelNow (called from RM_Building_TractionLance.cs:292) calls ReelStep with no timer and no CanWork gate. So the proof never checks cadence, the power/manning gate, stun length or the despawn release (new PostDeSpawn). Add a proof that advances real ticks through CompTick and toggles the host state. |
| (not filed) | — | Claim 26 (2000-tick sight-blocker latency) is a documented trade-off and needs no item. |

#### Build
`winbuild.py CreatureBehaviors`: Build succeeded, 0 warnings, 0 errors. BUILT RimMandrake.CreatureBehaviors.dll (source b31b7ad696d6+dirty). Selftests not run: the SelfTest, SelfTestFuzz, SelfTestTracks and SelfTestSandBuried projects compile only the pure kernels (RM_SunHeatMath, RM_SandSwimKernel, RM_TrackPool and others), and none of those files was edited. No defs changed. Not deployed, and the code review was not marked clean.

## DivingInteraction

Verdicts on design/RimMandrake/gpt_reviews/DivingInteraction.md Part 1. Paths relative to src/RimMandrake/DivingInteraction/Source/ unless stated. Engine facts cited as RimSage were read from the decompiled 1.6 source this pass.

| # | claim (short) | verdict | evidence (file:line, one line) | action |
|---|---|---|---|---|
| 1 | Grey Sea crystallisation + Elder disturbance gate on surface biome defName, never fire on layer floor | real | MapComponent_BrineCrystallisation.cs:70, RM_Building_BrineElder.cs:258 tested `map.Biome.defName == "RM_GreySea"`; layer floor biome is RM_SeabedFloor_*; `RM_SeaFloorIdentity.IsFloorOf` (RM_SeabedSiteParent.cs:86) already exists | fixed (both use IsFloorOf) |
| 2 | Chill drowned-aurora SourceMap only resolves PocketMapParent; layer floors read 0 | real | RM_MapComponent_ChillDrownedAurora.cs SourceMap() cast to PocketMapParent only | fixed (falls back to the loaded surface map at SurfaceTileOf); unloaded-surface behaviour still reads 0 — see item CHILL_AURORA_UNATTENDED_SOURCE_1 |
| 3 | Elder trade commits novelty/treasure and destroys offering before delivery succeeds | real (partly fixed) | RM_ElderTradeUtility.cs Offer: Decide() marks seen + claims treasure, offered.Destroy, TryPlaceThing result ignored | fixed: delivery cell + inputs now validated before anything commits (see 4/5); residual (placement failure after commit) → `file → ELDER_TRADE_TRANSACTIONAL_PAYOUT_1` |
| 4 | "Never underwater" payout falls back to elder.Position (deep brine) | real | RM_ElderTradeUtility.cs FindDeliveryCell final `return elder.Position`; jacket terrain unchecked | fixed (returns IntVec3.Invalid, skips a jacket standing on water; Offer refuses with no dry cell) |
| 5 | Offer() validates nothing (null, spawned, same map, settings) | real | RM_ElderTradeUtility.cs Offer dereferenced elder/offered/Current.Game unguarded | fixed (guards return Accepted=false; Dialog_OfferToElder.ReportResult now shows RM_ElderOfferRefused; key added) |
| 6 | Encasement destroys edifice before validating; no p.Map==map check | real (minor) | BrineEncasementUtility.cs: hard cast after edifice.Destroy; guard lacked p.Map==map | fixed (map guard; jacket made and type-checked before edifice destroyed). Exception-during-GenSpawn rollback not added (speculative) |
| 7 | Jacket Destroy destroys holder before ejecting contents | real | RM_BrineEncasement.cs Destroy: base.Destroy(mode) then TryDropAll, result unchecked; comment says "eject first" | fixed (eject while spawned, Building_Casket order; retry after; Log.Error if anything remains) |
| 8 | Scald discharge foreach over live AllPawnsSpawned while damaging; aurora index loop skips | real | RM_MapComponent_ScaldVentForecast.cs Discharge foreach + TakeDamage (death despawns → list mutates → InvalidOperationException); ChillAuroraSurge ScanShockRisk indexed live list | fixed (snapshots in both, Spawned/Map recheck) |
| 9 | Surge shock check on same tick as warning letter | real | RM_MapComponent_ChillAuroraSurge.cs UpdateSurgeState set ticksUntilShockCheck=1; MapComponentTick decrements and scans same tick | fixed (= ShockCheckIntervalTicks) |
| 10 | Load with active surge: intensity reloads 0 → false end + re-letter | real | ChillDrownedAurora.currentIntensity was deliberately unscribed; Surge scribes surgeActive | fixed (currentIntensity Scribed, key "currentIntensity"; old saves still reconcile once) |
| 11 | Tier-1 arc resets offenseScore so steady offending never reaches tier 2 | real (design) | RM_GardenDefenseKernel.cs Offense: tier1 branch sets offenseScore=0 | file → GARDEN_ESCALATION_PROGRESS_FIX_1 |
| 12 | Tarnn wake can repeat after 60,000 ticks | real (design/text) | RM_GardenDefenseKernel.cs Tier2CooldownTicks=60000, no completion flag | file → GARDEN_ESCALATION_PROGRESS_FIX_1 (decide one-time vs repeatable, align settings text) |
| 13 | Harvest hook counts player crops; heat hook counts zero damage | real | Patch_ChillGardenDefense.cs PlantCollected postfix had no sown check; heat branch ignored totalDamageDealt | fixed (skip Zone_Growing / Building_PlantGrower cells; require totalDamageDealt>0) |
| 173b | (UNVERIFIABLE bullet) garden kill detection | real — and worse than GPT said | Engine (RimSage Thing.TakeDamage): pawn dies in Worker.Apply, so in PostApplyDamage `__instance.Map` is null → kill branch was unreachable | fixed (dead pawn resolved via MapHeld/PositionHeld) |
| 14 | Hatch PlaceWorker accepts any grav engine on the map | real but moot | PlaceWorker_NeedsGravEngine.cs AllowsPlacing only counts GravEngine things; the hatch itself is retired by ruling (ship is the only way down; SEA_DIVE_HATCH_RETIRE_1) | none (retirement removes it) |
| 15 | Missing sea generator silently falls back | real but moot | RM_SeaDiveHatch.cs IsEnterable checks dictionary key only; hatch-only path | none (hatch retiring) |
| 16 | Exit placement ignores failed second search / bounds | real but moot | GenStep_PlaceSeaDiveExit.cs: second TryFindRandomCell result unchecked, radius cells not InBounds-checked; only the hatch's pocket generators use it (layer generators drop it, RM_SeabedSiteParent.cs header) | none (hatch retiring) |
| 17 | Chill animal-count setting does not cap initial population (vanilla Animals also runs) | real | Defs/MapGeneration/RM_SeabedGenerators.xml Chill genSteps list RM_SeaFloorFauna AND Animals; floor density = sea x30 (RM_SeabedFloorExtension) | file → SEABED_FAUNA_SINGLE_SEEDER_1 |
| 18 | Legacy fauna rounding discontinuous | real | GenStep_SeaFloorFauna.cs RoundToInt then rare-chance only when 0 | fixed (stochastic rounding of expected count) |
| 19 | Overlapping rime seeds die on contact; fallback seeds not deduped | real | GenStep_ChillRimeTerraces.cs GrowDistrict `continue` on non-baseFloor incl. existing terrace | fixed (grows through terrace without repainting; fallback excludes existing seeds) |
| 20 | Expired Scald discharge can fire after load / re-enable | real | RM_MapComponent_ScaldVentForecast.cs Discharge ran before the `now >= phaseEnd` advance | fixed (`now < phaseEnd` gate) |
| 21 | Berth heat counts internal partitions | real (design) | RM_MapComponent_ScaldImmersionBerth.cs `room.BorderCellsCardinal.Count()` per room, shared walls counted twice | file → SCALD_BERTH_HULL_FACES_1 |
| 22 | Suit drain/recharge keyed on roof and distance, not shelter/access | real (design) | RM_CompHeatedSuitBattery.cs `!wearer.Position.Roofed(map)` drains; charger = distance + PowerOn | file → CHILL_SUIT_SHELTER_RULE_1 |
| 23 | Floor-light toggle also kills surge + collector | real | RM_MapComponent_ChillDrownedAurora.cs CurrentAuroraIntensity returns 0 when chillDrownedAuroraEnabled off; Surge reads it | file → DIVING_SETTINGS_CONTRACT_1 |
| 24 | Master switch not "fully inert" | real (contract/text) | GenStep_SeaFloorFauna.cs / GenStep_ChillRimeTerraces.cs have no masterEnabled gate; RM_BrineEncasement.TickRare smothers regardless | file → DIVING_SETTINGS_CONTRACT_1 |
| 25 | Gallery solved before reward delivered | real (minor) | RM_ReturnGallery.cs Mark set solved then SpawnRewards, which returns on null map | fixed (Mark refuses unless parent.Spawned); missing reward defs still skip silently — low risk, none |
| 26 | Gallery Mark ignores master switch | real | RM_ReturnGallery.cs Mark had no settings check | fixed (masterEnabled gate in Mark); generation-vs-runtime meaning of scaldReturnGalleryEnabled → DIVING_SETTINGS_CONTRACT_1 |
| 27 | "Day" jam is 15,000 ticks | real | RM_ReturnGallery.cs JamTicks=15000 vs header + messages "a day" | fixed (60000) |
| 28 | Plant-growth finalizer swallows all exceptions on seabed maps | real but deliberate | Patch_SeabedPlantGrowthGuard.cs scoped to IsSeabedTile, documented insurance; logged only type+message | fixed (logs the full exception); keep/remove guard is a live question → none |
| 29 | NaN market value pays MaxSilver | real | RM_ElderEconomyKernel.cs SilverFor `!(scaled < MaxSilver)` true for NaN | fixed (NaN/negative value → 0, earns the floor) |
| 30 | Cosmetic Rand draws depend on camera | real | RM_MapComponent_ChillAuroraSurge.cs ThrowDressingFlecks and RM_MapComponent_ChillBoilShroud.cs draw Rand only when map == CurrentMap | fixed (Rand.PushState(seed)/PopState in finally, both files) |
| 31 | Elder disturbed on Mine job assignment, not at the face | real | RM_Building_BrineElder.cs RM_MapComponent_ElderDisturbance checked jacket-to-Elder distance only | fixed (miner must be AdjacentTo8WayOrInside the jacket) |
| 32 | 48-step charge takes 49 float adds | real (low) | RM_Building_BrineElder.cs TickRare `Min(1f, charge + 1f/48f)` | fixed (snap within 1e-4 to 1f) |
| B1 | Rare-tick dispatch unverified | real for 3 of 5 | RimSage: ThingWithComps calls CompTickRare only from TickRare, and pawns (Normal ticker) never get TickRare, so RM_CompPoolSentinelSquirt (Orruhmu) and RM_CompTarnnRoused never ran. RM_ChillHeatedSuit inherits tickerType Never from ApparelBase (RimSage merged Apparel_Vacsuit shows Never), so its battery comp never ran. Elder (TerminalBiomes RM_BrineElder.xml:146) and jacket (Rare) are fine | fixed (both pawn comps drive CompTickRare from CompTick every 250 by hash; suit def gets `<tickerType>Rare</tickerType>`; worn apparel is ticked through the wearer's holder tree per Thing.DoTick) |
| B2 | Held-pawn death / corpse inside jacket | unclear | Thing.DoTick ticks a holder's contents, so the held pawn does tick; whether RM_Smothered reaches lethal while unspawned and where the corpse goes needs a live/offline harness check | none (owed to a live check) |
| B3 | Garden kill detection | real | see row 173b | fixed |
| B4 | EMP stun on living creatures | unclear | RM_Building_BrineElder.cs discharge relies on vanilla EMP stun eligibility; organic eligibility for EMP stun not read this pass — needs a RimSage DamageWorker/StunHandler read | file → ELDER_DISCHARGE_STUN_LIVING_1 |
| B5 | ThingsOfDef(null) when Elder def missing | real | RM_Building_BrineElder.cs passed GetNamedSilentFail result straight to ThingsOfDef | fixed (both defs resolved and null-checked first) |
| B6 | Harmony targets/overloads unverified | unclear | needs a live Harmony patch inventory | none (live) |

#### Files changed
- under `/home/mandrake/rm/foundry/src/RimMandrake/DivingInteraction/` (seat clone):
  - Source/MapComponent_BrineCrystallisation.cs, Source/RM_Building_BrineElder.cs, Source/RM_MapComponent_ChillDrownedAurora.cs, Source/RM_ElderTradeUtility.cs, Source/Dialog_OfferToElder.cs, Source/BrineEncasementUtility.cs, Source/RM_BrineEncasement.cs, Source/RM_MapComponent_ScaldVentForecast.cs, Source/RM_MapComponent_ChillAuroraSurge.cs, Source/RM_MapComponent_ChillBoilShroud.cs, Source/Patch_ChillGardenDefense.cs, Source/GenStep_SeaFloorFauna.cs, Source/GenStep_ChillRimeTerraces.cs, Source/RM_ReturnGallery.cs, Source/Patch_SeabedPlantGrowthGuard.cs, Source/RM_ElderEconomyKernel.cs, Source/RM_CompPoolSentinelSquirt.cs, Source/RM_CompTarnnRoused.cs
  - Defs/ThingDefs_Items/RM_ChillHeatedSuit.xml, Languages/English/Keyed/RM_DivingInteraction_Keys.xml (new key RM_ElderOfferRefused)
  - Assemblies/RimMandrake.DivingInteraction.dll + .dll.srchash (rebuilt)

#### Items to file
| NAME | title | spec |
|---|---|---|
| ELDER_TRADE_TRANSACTIONAL_PAYOUT_1 | Make the Brine Elder trade commit only after the payout lands | RM_ElderTradeUtility.Offer still calls Decide() (marks novelty, claims a unique treasure) and destroys the offering before GenPlace.TryPlaceThing, whose result is ignored. Inputs and a dry delivery cell are now validated up front, but a failed placement still loses the specimen, novelty and treasure entitlement. Split quote from commit (kernel already pure: RM_ElderEconomyKernel.Decide) and roll back or keep a Scribed pending payout. |
| CHILL_AURORA_UNATTENDED_SOURCE_1 | Drowned aurora on a floor map whose surface map is not loaded | SourceMap() now resolves the loaded surface map above a seabed-layer floor; with none loaded (the normal gravship case) intensity is 0, so surges and the collector stay dormant. Decide the source: world-level condition, the surface tile's weather/latitude, or an intrinsic floor schedule. |
| GARDEN_ESCALATION_PROGRESS_FIX_1 | Garden defense: tier-1 resets tier-2 progress; Tarnn wake repeats | RM_GardenDefenseKernel.Offense zeroes offenseScore on every tier-1 arc, so offending at the tier-1 cadence never reaches tier 2; Tier2CooldownTicks=60000 lets the wake recur though RM_CompTarnnRoused's header says "no repeat wave". Keep a separate escalation accumulator (Scribe-compatible) and decide one-time vs repeatable, then align settings text. The fuzz selftest covers this kernel. |
| SEABED_FAUNA_SINGLE_SEEDER_1 | Chill floor seeds animals twice | RM_SeabedGenerators.xml runs RM_SeaFloorFauna (chillDiveAnimalCount weighted draw) and vanilla Animals on a floor whose animalDensity is the sea's x30, so the setting does not bound the start population. Pick one initial seeder and treat ongoing spawns as a separate budget. |
| SCALD_BERTH_HULL_FACES_1 | Berth heat should count exterior hull faces only | RM_MapComponent_ScaldImmersionBerth counts room.BorderCellsCardinal per room, so internal walls add heat to both rooms and subdividing a fixed hull raises heat load. Count border cells adjacent to an outdoor/sea cell only; retune HeatPerBorderCellPerTick afterwards. |
| CHILL_SUIT_SHELTER_RULE_1 | Heated suit drain/recharge uses roof and straight-line distance | RM_CompHeatedSuitBattery: any roof stops drain; recharge needs only chargerSearchRadius + PowerOn, through walls. Base drain on vanilla temperature at the wearer (no second heat model) and require the charger in the same room. Note the comp only started ticking this pass (tickerType fix) — behaviour should be checked once first. |
| DIVING_SETTINGS_CONTRACT_1 | Define what each DivingInteraction toggle actually turns off | chillDrownedAuroraEnabled (visual) zeroes CurrentAuroraIntensity, which also disables surge damage and collector output; masterEnabled does not gate GenStep_SeaFloorFauna, GenStep_ChillRimeTerraces, RM_SeabedFloorLife reassertion or jacket smothering; scaldReturnGalleryEnabled gates the workgiver though described as generation-affecting. Separate sensing from presentation and make tooltips state the real contract. |
| ELDER_DISCHARGE_STUN_LIVING_1 | Verify the Elder's EMP discharge stuns living pawns | RM_Building_BrineElder discharge uses vanilla EMP; eligibility of organic, implant-free pawns for EMP stun is unverified. Read DamageWorker/StunHandler in RimSage; if organics are immune, add an explicit stun for living creatures. |

#### Build
- `python3 src/RimMandrake/Utils/winbuild.py DivingInteraction` → `BUILT src/RimMandrake/DivingInteraction/Assemblies/RimMandrake.DivingInteraction.dll`, 0 errors (final build after all edits).
- `python3 src/RimMandrake/Utils/selftest_divinginteraction_fuzz.py` → garden 4000, elder 4000, units 302 cases, 0 failures, OK.
- Not deployed; not live-tested; code-review status untouched.

## EnvironmentalHazards

| # | claim (short) | verdict | evidence (file:line, one line) | action |
|---|---|---|---|---|
| 1 | nonlethal venom clamp runs after lethal TakeDamage | real | MapComponent_ContactVenom.cs:268-270; engine Pawn_HealthTracker.PostApplyDamage → AddHediff → CheckForStateChange kills synchronously before ApplyLethalityOption runs | file → CONTACT_VENOM_NONLETHAL_ORDER_1 |
| 2 | primary+secondary aura comps share Scribe label | real | HediffComp_PeriodicAreaAttack.cs:329 "ticksUntilBurst"; Secondary inherits; HediffWithComps scribes every comp into one node | fixed (virtual SaveKey; secondary uses "ticksUntilBurstSecondary") HediffComp_PeriodicAreaAttack.cs, HediffComp_PeriodicAreaAttackSecondary.cs |
| 3 | moat ignition queue not Scribed | real | RM_CompFloodIgniter.cs:72-73 had no PostExposeData | fixed (PostExposeData saves queue as list + accumulator) RM_CompFloodIgniter.cs |
| 4 | repeated ignite duplicates queue | real | RM_CompFloodIgniter.cs:97 no Igniting guard | fixed (BeginIgnition returns while Igniting, gizmo Disabled, terrain re-checked at dequeue) RM_CompFloodIgniter.cs |
| 5 | found-tech records don't follow research aliases | real (latent) | RM_FoundTechStudy.cs:176 string project; :214 compares defName directly | fixed (PostLoadInit canonicalises via RM_DefAliasPatches.Resolve, merges duplicates) RM_FoundTechStudy.cs |
| 6 | terrain alias hash guessed from name | real (latent limitation) | RM_DefAliases.cs:74 StableStringHash%65535 ignores ShortHashGiver collision probing; postfix only fires when __result null | file → DEF_ALIAS_CHAIN_HASH_1 |
| 7 | aliases single-hop, untyped | real (latent) | RM_DefAliases.cs:71 byName[from]=to; Resolve one hop | file → DEF_ALIAS_CHAIN_HASH_1 |
| 8 | multicell Thing hit once per covered cell | real | HediffComp_PeriodicAreaAttack.cs:100/131/168 no cross-cell dedupe | fixed (per-burst HashSet<Thing>) HediffComp_PeriodicAreaAttack.cs |
| 9 | die-off outbreak self-clones without generation bound | real (no consumer today) | RM_CompScriptedDieOff.cs:141 `spreadThingDef ?? parent.def`, each child rerolls budget at PostSpawnSetup; grep finds no XML consumer of CompProperties_ScriptedDieOff | file → SCRIPTED_DIEOFF_GENERATION_BOUND_1 |
| 10a | CrackFall only CompTickRare on Long-ticked trees | real | RM_CompCrackFall.cs:65; sole consumer RM_Mirrelbole (Greentide RM_Greentide_TreeRoster.xml:316) is TreeBase → tickerType Long; Plant only runs CompTickLong — comp never fired | fixed (CompTickRare/CompTickLong both route to Step(elapsedTicks)) RM_CompCrackFall.cs |
| 10b | ScriptedDieOff CompTick-only | real (no consumer) | RM_CompScriptedDieOff.cs:102 | file → SCRIPTED_DIEOFF_GENERATION_BOUND_1 |
| 10c | ActiveGasEmitter ConfigErrors accepts Rare/Long | real | CompProperties_ActiveGasEmitter.cs:88 tested only `== Never`; CompActiveGasEmitter.cs:37 overrides CompTick only | fixed (`!= Normal`) CompProperties_ActiveGasEmitter.cs |
| 11 | batched delta discards remainder | real (minor) | Gas_Damaging.cs:71, Gas_Transmuting.cs:57, HediffComp_PeriodicAreaAttack.cs:52 reset to full interval | fixed (countdown += interval, floor 1) in all three |
| 12 | eater ignores delta, 181-tick bite | real | RM_CompStationEater.cs:231 `delegate {}` discards Toil.tickIntervalAction's int (Action<int>, Verse/AI/Toil.cs:15) | fixed (delegate(int delta), -= delta, += ticksPerBite) RM_CompStationEater.cs |
| 13 | running eat job ignores satiation/disable | real | RM_CompStationEater.cs:188 checks only in job giver | fixed (end job when Satiated or tar-beast option off) RM_CompStationEater.cs |
| 14 | venom sampling iterates live AllPawnsSpawned | real | MapComponent_ContactVenom.cs:129; Scratch can kill → despawn → skip next pawn | fixed (snapshot list) MapComponent_ContactVenom.cs |
| 15 | disabled venom does not freeze clocks | real (comment false) | MapComponent_ContactVenom.cs:104-112 comment said clocks FREEZE; deadlines are absolute ticks | fixed (comment corrected to what the code does) MapComponent_ContactVenom.cs |
| 16 | contact expiry only on prune pass | real, benign | MapComponent_ContactVenom.cs:176/193; overdue lingering row scratches immediately anyway (now >= nextScratch), same outcome as first contact | none (no player-visible difference) |
| 17 | IndexOf O(P·K) | real, perf only | MapComponent_ContactVenom.cs:203; K = pawns touching one stand, tiny | none (not a defect at real scale) |
| 18 | map-wide StoryDanger.High overrides local fear radius | real | RM_CompGatherableCalmGated.cs:133 returns before the Card-3 radius check whose comment says far-side herds stay calm | file → THORNBUG_FEAR_SCOPE_1 (owner card scope) |
| 19 | fear only rescanned every 250 ticks | real, benign | RM_CompGatherableCalmGated.cs:106; ≤250-tick latency | none (latency within scan design) |
| 20 | water-locked mother stranded on land | real | RM_CompWaterLocked.cs CompTick ends every job on land with no route back to water | file → WARDEN_MOTHER_LAND_RECOVERY_1 |
| 21 | vapor wander validator args swapped | real | RM_CompVaporDrifter.cs:112 declared (pawn, root, dest); engine RCellFinder.cs:314/436 calls validator(pawn, c, root) — validated the root | fixed (param order) RM_CompVaporDrifter.cs; same bug found+fixed in RM_JobGiver_DreadAvoidWander.cs:81 |
| 22 | day/night temp offset switches, not lerp | real | GameCondition_EnvironmentalWeather.cs:279 IsDaytime switch vs EnvironmentalWeatherExtension.cs:114 "lerps between them by daylight"; used darkness-patched glow | fixed (Lerp by unpatched GenCelestial.CelestialSunGlow(map, TicksAbs)) GameCondition_EnvironmentalWeather.cs |
| 23 | mechanic gate misses weather/temp/density/electricity | real | GameCondition_EnvironmentalWeather.cs:251-330 virtuals ignore RM_MechanicGates.Enabled | file → ENV_WEATHER_GATE_SCOPE_1 |
| 24 | damage multiplier holes | real (part) | DeathActionWorker_ScaledExplosion.cs:49 left -1 sentinel unscaled; StationEater/lottery explosions never read multiplier | fixed (sentinel resolved to damageDef.defaultDamage before scaling) DeathActionWorker_ScaledExplosion.cs; rest file → HAZARD_MULTIPLIER_COVERAGE_1 |
| 25 | tar pace one-time, 3 bands | real | RM_CompTarBeast.cs:46/88 | file → TAR_BEAST_SETTINGS_CONSISTENCY_1 |
| 26 | tar building limit capped by def limit | real | RM_CompTarBeast.cs:119 `Satiated ||` enforces maxStructuresEaten regardless of setting | file → TAR_BEAST_SETTINGS_CONSISTENCY_1 |
| 27 | pump wake relay ignores tarBeastEnabled | real | RM_CompTarBeast.cs:263-283 RM_CompBulgePumpWake | fixed (relay returns when option off) RM_CompTarBeast.cs |
| 28 | solvent hunt consumed before TryStartMentalState succeeds | real, low | RM_CompTarBeast.cs:53 return ignored | file → TAR_BEAST_SETTINGS_CONSISTENCY_1 |
| 29 | "nobody left" = no free colonists | real (comment vs rule) | RM_CompTarBeast.cs:124 FreeColonistsSpawnedCount | file → TAR_BEAST_SETTINGS_CONSISTENCY_1 |
| 30 | lottery yield depends on call partition | real | RM_CompWorkedLottery.cs:142 one roll per AddWork | fixed (bounded loop ≤64 rolls, destroyed/map check each) RM_CompWorkedLottery.cs |
| 31 | second trap roll postpones armed fuse | real | RM_CompWorkedLottery.cs:201 ArmTrap reset fuse unconditionally | fixed (ArmTrap no-op while TrapArmed) RM_CompWorkedLottery.cs |
| 32 | beast-wake threshold off by one | real | RM_CompWorkedLottery.cs:183 compared post-increment depth vs doc "0-indexed stratum 4" (:45-49) | fixed (compare the stratum just worked) RM_CompWorkedLottery.cs |
| 33 | trap weight overflows to infinity | real | RM_CompWorkedLottery.cs:194 Math.Pow(1.3, unbounded depth) → float inf at depth ≈338 | fixed (factor capped at 1e6) RM_CompWorkedLottery.cs |
| 34 | glow override precedence first-not-newest | false (in shipped content) | BiomeGlowPatches.cs:220-231; only one def carries RM_GlowMultiplierOverrideExtension (Greentide RM_Greentide_Conditions.xml:69), and the comment explicitly accepts the two-override edge | none (no second override exists) |
| 35 | override doesn't lift sunlight suppression | false (in shipped content) | BiomeGlowPatches.cs:293; suppressSunlightStatAffecter only on TheSump biome, override only on a Greentide condition — never co-occur | none (latent; revisit if an override lands on a suppressing biome) |
| 36 | warbling ignores player colour, leaves colour on disable | real, low | RM_Comp_WarblingGlow.cs:103 reads Props.glowColor; CompGlower saves glowColorOverride, so the last animated frame persists when disabled | file → WARBLING_GLOW_BASELINE_1 |
| 37 | warbling registers light twice per update | real | RM_Comp_WarblingGlow.cs:109 GlowColor setter de/re-registers (Verse/CompGlower.SetGlowColorInternal), then :119 ForceRegister again — and ForceRegister registers even when unlit (unpowered/flicked-off lamp re-lit) | fixed (radius first, one register via colour setter, ForceRegister removed) RM_Comp_WarblingGlow.cs |
| 38 | transmute: null entries, destroy-before-spawn | false / low | Gas_Transmuting.cs:128 entries come from XML list (no null rows in practice); spawning a valid ThingDef into a just-vacated cell does not fail; non-plant replacement is a config gap, not a runtime defect | none (config-validation nicety) |
| 39 | clamped surge/recede drifts | real | RM_AxisKernel.cs:48 clamps per apply; :84 recede from requested delta → saturated cells over-recede (0.95+0.10→1.00, −0.09→0.91) | file → AXIS_SURGE_CLAMP_DRIFT_1 |
| 40 | Harmony targets resolved by name | false | BiomeGlowPatches.cs:90/106 — Thing.PostApplyDamage and BackCompatibility.BackCompatibleDefName each have exactly one overload in 1.6 (Verse/Thing.cs:1549, BackCompatibility.cs:117); AccessTools.Method throws on ambiguity rather than silently picking | none |

Extra (not claimed by GPT, same bug class as #21): RM_JobGiver_DreadAvoidWander.cs:81 `DestNotDreaded(pawn, root, dest)` also had the validator arguments swapped (tested the pawn's own cell) — fixed.

Behaviour note for the parent: #10a means RM_Mirrelbole trees crack and fall for the first time — the comp was dead before this fix.

#### Files changed
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/HediffComp_PeriodicAreaAttack.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/HediffComp_PeriodicAreaAttackSecondary.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/RM_CompFloodIgniter.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/RM_FoundTechStudy.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/Gas_Damaging.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/Gas_Transmuting.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/RM_CompCrackFall.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/CompProperties_ActiveGasEmitter.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/RM_CompStationEater.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/RM_CompTarBeast.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/MapComponent_ContactVenom.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/RM_CompVaporDrifter.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/RM_JobGiver_DreadAvoidWander.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/GameCondition_EnvironmentalWeather.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/DeathActionWorker_ScaledExplosion.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/RM_CompWorkedLottery.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Source/RM_Comp_WarblingGlow.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll`
- `/home/mandrake/rm/foundry/src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll.srchash`

#### Items to file
| NAME | title | spec |
|---|---|---|
| CONTACT_VENOM_NONLETHAL_ORDER_1 | Nonlethal venom option clamps after the pawn is already dead | MapComponent_ContactVenom.cs:268 TakeDamage → Pawn_HealthTracker.PostApplyDamage adds additionalHediffs via AddHediff → CheckForStateChange, which kills synchronously; ApplyLethalityOption (:270) runs after. With contactVenomLethal off the clamp must happen before the hediff lands — e.g. apply damage with a DamageDef copy lacking additionalHediffs and add the capped hediff ourselves, or a narrow Harmony prefix. Needs a live/quicktest proof with a near-lethal carrier. |
| DEF_ALIAS_CHAIN_HASH_1 | Def aliases: chain resolution, typed keys, real historical terrain hashes | RM_DefAliases.cs:71 keys aliases by old name only (last writer wins, untyped); Resolve (:83-94) is one hop so A→B→C breaks once B is gone; :74 guesses old terrain shortHash from StableStringHash%65535, which misses ShortHashGiver's collision probing, and the postfix (:110) only fires when the hash resolves to nothing. Add cycle-checked chain resolution, conflict reporting, optional def-type key, and an explicit `fromHash` field for terrain. |
| SCRIPTED_DIEOFF_GENERATION_BOUND_1 | Scripted die-off outbreak needs a generation-wide end and a Long-tick path | RM_CompScriptedDieOff.cs:141 defaults spreadThingDef to parent.def, and each child rerolls a fresh lifetime and spread budget in PostSpawnSetup (:91-98), so an outbreak never ends as a whole; it also overrides CompTick only (:102), which never fires on a Long-ticked plant. No XML consumer today — fix before the first one ships (inherit an absolute expiry/generation counter; add CompTickLong). |
| THORNBUG_FEAR_SCOPE_1 | Map-wide StoryDanger.High bypasses the ruled 40-cell fear radius | RM_CompGatherableCalmGated.cs:133 returns feared for any High-danger map before the Card-3 local-radius check (:139-156) whose own comment says sheltered herds on the far side stay calm. Confirm with the owner's card which rule wins, then drop or narrow the map-wide gate. |
| WARDEN_MOTHER_LAND_RECOVERY_1 | Water-locked pawn on land has no route back to water | RM_CompWaterLocked.cs CompTick (~:85-110) StopDead + EndCurrentJob every checkIntervalTicks whenever the pawn stands on land, including the jobs that would walk it back. Add a recovery job to the nearest reachable water cell (exempt from the interrupt) and only interrupt jobs whose destination is land. |
| ENV_WEATHER_GATE_SCOPE_1 | Environmental weather mechanic gate leaves ambient effects live | GameCondition_EnvironmentalWeather.cs:82/190 gate pawn and cell effects on RM_MechanicGates.Enabled, but ForcedWeather (:251), TemperatureOffset, Animal/PlantDensityFactor, AllowEnjoyableOutsideNow and ElectricityDisabled ignore it. Decide the settings contract (does a biome toggle disable the forced weather/temperature too?) and return neutral values accordingly. |
| HAZARD_MULTIPLIER_COVERAGE_1 | hazardDamageMultiplier does not reach structure eating or lottery explosions | RM_EnvironmentalHazardsMod.cs:47 describes it as a global scalar on every hazard damage, but RM_CompStationEater.cs (eatDamagePerHit) and RM_CompWorkedLottery trap detonation never read it. Either route them through the multiplier or narrow the setting's description. (The ScaledExplosion -1 sentinel hole is fixed.) |
| TAR_BEAST_SETTINGS_CONSISTENCY_1 | Tar-beast settings: pace, building limit, solvent hunt, sink rule | RM_CompTarBeast.cs:46/88 pace applied once and banded to 3 severities (existing beasts ignore later changes); :119 `eater.Satiated ||` means tarBeastMaxBuildings can lower but never raise the def's maxStructuresEaten; :53 solvent wake consumed before TryStartMentalState's result is checked; :124 "nobody left to hunt" is FreeColonistsSpawnedCount==0. Pick one effective limit, refresh pace on settings change (or label it as presets), retry hunt on failure, and align the sink rule with its comment. |
| WARBLING_GLOW_BASELINE_1 | Warbling gaslight overwrites player colour and leaves its last frame when disabled | RM_Comp_WarblingGlow.cs:103 animates around Props.glowColor and writes CompGlower.glowColorOverride (which CompGlower saves), so a player-picked colour is lost and disabling the option (:55) freezes the last animated colour/radius. Keep a per-instance baseline, restore it on disable. |
| AXIS_SURGE_CLAMP_DRIFT_1 | Gradient surge recede over-corrects saturated cells | RM_AxisKernel.cs:48 clamps each apply to [0,1] while RecedeDelta (:84) reverses the requested forward delta, so a cell at 0.95 surged +0.10 (→1.00) recedes −0.09 to 0.91, fresher than before. Track the applied (post-clamp) forward change per cell or a baseline+offset; extend selftest_envhazards_fuzz.py with a saturation case. |

#### Build
- `python3 src/RimMandrake/Utils/winbuild.py EnvironmentalHazards` → `Build succeeded. 0 Warning(s) 0 Error(s)`; `BUILT src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll (source b31b7ad696d6+dirty)`
- `selftest_envhazards_livingmap.py` → 0 failure(s)
- `src/RimMandrake/Utils/selftest_envhazards_fuzz.py` → ENVHAZARDS FUZZ: PASS
- `validation.py` (static) → STATIC: PASS (0 findings)
- Not deployed, not marked clean, nothing committed.

## FeverWood


| # | claim (short) | verdict | evidence (file:line, one line) | action |
|---|---|---|---|---|
| 1 | Moderate eye damage resolves immediately, so severe (85%) only reachable by one big jump | real | Source/RM_CompTentacleEye.cs:59 resolves moderate on the hit; Props header says tiers are judged "before it withdraws" | fixed (RM_CompTentacleEye.cs: moderate resolves at window close; severe/death still immediate) |
| 2 | Light eye retreat leaves the emergence active despite letter | false | letter's "driving off" is the MODERATE row, which calls DriveOffAllLimbs (RM_CompTentacleEye.cs:77 -> TentacleWatch DespawnAllLimbs); light = "ordinary retreat (short cooldown)" per RM_CompProperties_TentacleEye.cs:10 | none (as designed) |
| 3 | Missing lastProducedTick entry makes window 0 forever | real | RM_CompCapturedSpecimen.cs:138 defaults to now; RM_TankKernel.ProductionWindow returns 0; entry only written on success | fixed (missing clock is started, not read as 0-width window) |
| 4 | Limb action timers reset on load | real | RM_CompTentacleLimb.cs:44-55 ignore respawningAfterLoad though ticksUntilAction is scribed (:296) | fixed (timers only set when !respawningAfterLoad; sentinel re-registration unchanged) |
| 5 | Tank teaches/announces even when placement fails | real | RM_CompCapturedSpecimen.cs:147 ignores TryPlaceThing result | fixed (failed placement: no clock advance, no teaching/message) |
| 6 | Escape resolves occupant differently from release | real | :198 reads Props.occupantKindDefName; release uses YoungKind(Props) (follows occupantLikeTank) | fixed (Escape uses YoungKind(Props)) |
| 7 | Null occupant kind still consumes the captive | real (misconfig only) | :354/:392 flip occupied before kind check; :198-205 destroys tank then returns | none (only reachable on a missing PawnKindDef = config error; comment at :207 documents tank-still-breaks intent) |
| 8 | Tamed escapee still installs | real | RM_CompEscapedCaptive.cs:70-91 armed path has no faction check; header :18-20 says a tamed one must not install | fixed (armed escapee with a faction is disarmed) |
| 9 | Released young picks nearest pool then checks reachability only there | real | RM_CompEscapedCaptive.cs:189-227 nearest-by-distance, reach checked only on that cell + 8 neighbours | file → FEVERWOOD_WATER_TOPOLOGY_SERVICE_1 |
| 10 | Arrival via diagonal across blocked corners | real (edge) | RM_CompEscapedCaptive.cs:158-185 any adjacent-8 water counts | none (cosmetic edge: a walled-off pawn beside a pool corner; folded into the water item) |
| 11 | Great Emergence threshold uses total map water, not a cluster | real | TentacleWatch GreatEmergenceEligible passes pools.Count (all registered cells); header says "a pool cluster qualifies" | file → FEVERWOOD_WATER_TOPOLOGY_SERVICE_1 |
| 12 | Great Emergence limbs all spawn on the same cell; bloom on seed | real (worse than claimed) | RandomNearbyPoolCell was deterministic nearest; limbs are 1x1 Impassable buildings (Defs/ThingDefs_Buildings/RM_Sekkulaath_Tentacles.xml:44-48), so GenSpawn wipe kills earlier limbs | fixed (RM_MapComponent_TentacleWatch.cs: random free cell within 8, skip occupied, bloom keeps the seed) |
| 13 | Suppression doesn't withdraw existing limbs; map-wide | real (design mismatch) | SuppressPoolWithRadioactiveMaterial only extends blockedUntilTick; message says "no tentacles"; map-wide scope is documented in the header | file → FOUL_POOL_SUPPRESSION_SCOPE_1 |
| 14 | FoulPool doesn't reserve the cell / recheck designation | real | RM_JobDriver_FoulPool.cs:24 reserved suppressant only; :61 ignored designation state | fixed (reserve cell; spend nothing if designation gone; WorkGiver CanReserve cell) |
| 15 | Suppressant finder ignores forbidden | real | RM_WorkGiver_FoulPool.cs:60 validator lacked IsForbidden | fixed |
| 16 | Lure restraint survives bait leaving the stake | real | RM_CompLureStake.cs:123 tick only notified the map comp; hediff (Moving setMax 0) stayed; nothing else strips RM_LureStaked | fixed (tick calls ReleaseBait when bait not live) |
| 17 | Registry misses reactivation; HasLiveBait accepts any map | real | HasLiveBait :34 checked only Spawned/!Dead | fixed (HasLiveBait requires same map + within 5 cells; dead/away bait is detached, so no silent reactivation) |
| 18 | HaulToStake stakes without confirming the drop | real (low) | RM_JobDriver_HaulToStake.cs:70-74 ignored drop result | fixed (stake only if victim spawned on stake map within 5 cells) |
| 19 | Later first wave overwrites owed second wave | real | RM_MapComponent_TwoFrontLure.cs single pending slot overwritten in LaunchFirstWave | fixed (no new first wave while a second is owed) |
| 20 | Two waves on the same tick | real | MapComponentTick ran TickPendingSecondWave then first-wave roll | fixed (TickPendingSecondWave returns bool; return after a wave) |
| 21 | Displayed timing differs from actual | real (low) | 0.05-day floor, +500 tick min width, 2500-tick check | none (sub-hour drift, cosmetic) |
| 22 | Second-wave direction from stake, no bait objective | real | SpawnRaidWave :196 derives edge from stake position; fallback edge any direction; LordJob_AssaultColony gets no bait target | file → TWO_FRONT_BAIT_TARGETING_1 |
| 23 | Hive generator paints roofs only, no walls/excavation | real | RM_GenStep_AntHiveDungeon.cs PaintRoom/PaintCorridor only SetRoof/SetTerrain | file → ANT_HIVE_REAL_GEOMETRY_1 |
| 24 | Water-distance field is a boolean | real | :121/:172 test only `IsRegisteredWater(center)`, value ignored | file → ANT_HIVE_REAL_GEOMETRY_1 |
| 25 | Room chain loops/duplicates; one-room hive has no queen | real | BuildRoomChain accepts any in-bounds hop; Populate starts at index 1 | fixed (one-room chain skipped, rooms.Count < 2); overlap/backtrack part → ANT_HIVE_REAL_GEOMETRY_1 |
| 26 | Freeing ignores walls; guard test only RM_Kurreth | real | RM_KurrethColumn.cs CanBeFreed Euclidean d<=2, race-name guard | fixed (reach check, Touch); guard-identity part none (hive ext's default worker/queen are RM_Kurreth kinds; widen when another defender ships) |
| 27 | Recovery = "no bound hediff" | real (edge) | CheckFreed :394 `All(!IsBound)` over Living regardless of where they are | file → KURRETH_LOSS_FINALIZE_1 |
| 28 | Camp centre ignores TryFindRandomCellNear failure | real | :296 discarded bool; out param overwritten | fixed (fallback to map.Center on failure) |
| 29 | "Lost forever" doesn't finalize held pawns | unclear | Lose() only letters+signal; Column-phase pawns stay in kurreth kidnap tracker (vanilla kidnapped state), Camp-phase player-faction animals on a closed site map go wherever map removal sends them — needs live check | file → KURRETH_LOSS_FINALIZE_1 |
| 30 | Theft letters batched by time, not column | real | RM_KurrethTheft.cs MapComponentTick one pending list, last theft's exit dir | file → KURRETH_THEFT_PER_COLUMN_1 |
| 31 | Static path cache never removes carriers | real | :119 static dict, only ever added to | fixed (ForgetPath on Notify_PawnLost; path captured first) |
| 32 | Oil-boil condition lags weather by up to 249 ticks | real (low) | RM_OilBoil.cs:248 syncs every 250 ticks; yield patch reads ActiveOn(map) | none (~4 s lag; ActiveOn is already the single predicate for sparks and yield) |
| 33 | Lightning only writes a global timestamp | real | Prefix only set static lastLightningTick; DoStrike is static (strikeLoc, map) per RimSage, explosion may light no Fire thing | fixed (Postfix TrySpark on the struck cell/map; timestamp kept for cause text) |
| 34 | Natural-placement checkbox can't enable placement | real | Defs/BiomeDefs/RM_FeverWood.xml:45 generatesNaturally=false; setting only gates BiomeWorker score (RM_BiomeWorker_FeverWood.cs:39) | file → FEVERWOOD_NATURAL_TOGGLE_1 |
| 35 | Heat extension gated on undeclared mandrake.rm.biomes | false | FeverWood ships only inside the composed "Baroque Biomes" mod whose packageId IS mandrake.rm.biomes (deployed About.xml:4; Biomes.compose.json:35), so the gate is always met | none |
| 36 | Wreck-field GenStep names RimMandrake.Wreckage type with no declared dependency | real | Defs/MapGeneration/RM_FeverWoodWreckField.xml:12 unconditional; neither FeverWood/About nor the composed mod's About declares mandrake.rm.wreckage (composed About also omits creaturebehaviors/environmentalhazards) | file → FEVERWOOD_UNDECLARED_DEPS_1 |
| 37 | Full-map scans for pools / walk targets | real (low) | TentacleWatch PoolCells daily AllCells scan; RM_CompEscapedCaptive.WalkTarget AllCells scan, no throttle after a successful search | file → FEVERWOOD_WATER_TOPOLOGY_SERVICE_1 |

Counts: 37 claims — real 34 (several low/edge; #7 misconfig-only), false 2 (#2, #35), unclear 1 (#29). Fixed 19 (#1,3,4,5,6,8,12,14,15,16,17,18,19,20,25 partial,26 partial,28,31,33). Items to file: 8.

#### Files changed
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Source/RM_CompTentacleEye.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Source/RM_CompCapturedSpecimen.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Source/RM_CompTentacleLimb.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Source/RM_CompEscapedCaptive.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Source/RM_MapComponent_TentacleWatch.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Source/RM_JobDriver_FoulPool.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Source/RM_WorkGiver_FoulPool.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Source/RM_CompLureStake.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Source/RM_JobDriver_HaulToStake.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Source/RM_MapComponent_TwoFrontLure.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Source/RM_GenStep_AntHiveDungeon.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Source/RM_KurrethColumn.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Source/RM_KurrethTheft.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Source/RM_OilBoil.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Assemblies/RimMandrake.FeverWood.dll` (rebuilt)
- `/home/mandrake/rm/foundry/src/RimMandrake/FeverWood/Assemblies/RimMandrake.FeverWood.dll.srchash`

#### Items to file
| NAME | title | spec |
|---|---|---|
| FEVERWOOD_WATER_TOPOLOGY_SERVICE_1 | One registered-water topology (clusters, reachable shore) for FeverWood consumers | TentacleWatch.GreatEmergenceEligible passes the whole map's registered-cell count (RM_MapComponent_TentacleWatch.cs GreatEmergenceEligible), so many tiny pools satisfy "a large pool"; its own header says a cluster qualifies. RM_CompEscapedCaptive.WalkTarget (:189-227) picks the geometrically nearest pool and tests reach only there + 8 neighbours, so an enclosed nearest pool strands the young forever; both scan map.AllCells (TentacleWatch PoolCells daily, WalkTarget unthrottled after success). Build connected clusters from the tenant's registered water once, invalidate on terrain change, choose seeds/targets among eligible/reachable clusters. Also covers #10 (diagonal arrival across walls). |
| FOUL_POOL_SUPPRESSION_SCOPE_1 | Decide what radioactive fouling actually suppresses | SuppressPoolWithRadioactiveMaterial (TentacleWatch) only extends the map-wide blockedUntilTick; limbs already up keep attacking/depositing while the message says "no tentacles", and ForceEmergenceNear (oil-boil) ignores the block by design. Owner/design call: withdraw existing limbs on fouling, and whether fire-forced emergences respect chemical suppression; then align the message. |
| TWO_FRONT_BAIT_TARGETING_1 | Two-front lure: real opposite fronts and a bait objective | RM_MapComponent_TwoFrontLure.SpawnRaidWave (:196-216) derives the second edge from the stake position, not the first wave's actual entry, and its fallback picks any edge; both lords are plain LordJob_AssaultColony/KurrethTheft with no bait target although the message says raiders converge on the lure. Store the first wave's actual edge for the second, and give the lord an initial bait objective. |
| ANT_HIVE_REAL_GEOMETRY_1 | Ant hive genstep builds real enclosed rooms | RM_GenStep_AntHiveDungeon.PaintRoom/PaintCorridor only SetRoof/SetTerrain — no excavation, no walls, so on open ground the "dungeon" is walk-in roof patches and in rock the corridors are not dug. minDistanceFromRegisteredWater (:121,:172) is used only as a boolean on the centre cell. BuildRoomChain accepts overlapping/backtracking hops. Plan footprints with water clearance, excavate/wall them, reject overlaps, validate connectivity. |
| KURRETH_LOSS_FINALIZE_1 | Kurreth column: explicit recovery/loss state per victim | RM_KurrethColumn.CheckFreed (:394) treats "no RM_KurrethBound on any living victim" as recovered, wherever they are; Lose() (:439) only letters/signals — Column-phase victims stay in the kurreth kidnap tracker, Camp-phase bound animals (player faction) are left to whatever site-map removal does, while the hive deadline destroys them (:364). Track per-victim freed/placed state and finalize lost victims consistently; needs a live check of what map removal does to the camp's bound animals. |
| KURRETH_THEFT_PER_COLUMN_1 | Theft letters/quests grouped by column, not time window | RM_MapComponent_KurrethTheft keeps one map-wide pending list and a 600-tick letterAt; two columns inside the window become one quest, one slow column becomes several, and the letter uses the last theft's exit direction for all. Group pending thefts by lordId (already stored on Theft) and finalize per lord. |
| FEVERWOOD_NATURAL_TOGGLE_1 | Remove or relabel the dead natural-placement setting | RM_FeverWood.xml:45 fixes generatesNaturally=false, so RM_FeverWoodSettings.naturalPlacementEnabled (RM_FeverWoodMod.cs:32, read at RM_BiomeWorker_FeverWood.cs:39) can never cause placement. Given the standing no-worldgen ruling, likely remove the toggle (or relabel it as inert); decision is the owner's. |
| FEVERWOOD_UNDECLARED_DEPS_1 | Declare (or gate) FeverWood's Wreckage dependency | Defs/MapGeneration/RM_FeverWoodWreckField.xml:12 unconditionally names RimMandrake.Wreckage.RM_GenStep_WreckField and Patches/RM_FeverWood_WreckField_Register.xml adds it to extraGenSteps, but neither FeverWood/About/About.xml nor the composed mandrake.rm.biomes About.xml declares mandrake.rm.wreckage (the composed About also omits creaturebehaviors/environmentalhazards that FeverWood's own About requires). Add the dependencies to the compose source, or gate the GenStepDef + patch with PatchOperationFindMod. |

#### Build
`winbuild.py FeverWood` → Build succeeded, 0 warnings, 0 errors; `BUILT src/RimMandrake/FeverWood/Assemblies/RimMandrake.FeverWood.dll (source b31b7ad696d6+dirty)`.
Selftests: `selftest_feverwood.py` (all passed), `selftest_feverwood_broodcampaign.py` (0 failures). Kernel files untouched, so the SelfTest fuzz project was not rerun. Not deployed; not marked clean.

## FlowWorks

Verdicts on Part 1 of `design/RimMandrake/gpt_reviews/FlowWorks.md` (32 claims). Rows in working order, not claim order. Offline only, nothing deployed, no file marked review-clean.

| # | claim (short) | verdict | evidence (file:line, one line) | action |
|---|---|---|---|---|
| 4 | covered pit still drowns/poisons | real | RM_PitFillEffects.cs Tick: no RM_PitCoverUtility.IsCovered check, while RM_PitExposure.cs:26 / RM_PitPathing.cs:66 / shooting patch treat cover as ground | fixed (RM_PitFillEffects.cs) |
| 5 | drill discards extracted liquid on refused fill | real | Building_LiquidDrill.cs: pendingUnits debited before TrySetDriverFill result (false on FluidAllowed, Excavation.cs:1328) | fixed (Building_LiquidDrill.cs: debit only on true; FluidAllowed checked before extraction) |
| 10 | sealed sink still drains | real | RM_FlowKernel.cs ResolveComponent sink loop lacked IsSealed; sinkHops (:329) and recipients (:210) honour it; new selftest reproduced F=0 | fixed (RM_FlowKernel.cs + selftest Sealed_sink_does_not_drain) |
| 28 | exactly-at-cap body flagged truncated | real | RM_FlowKernel.cs CollectBody set truncated on collecting cell maxCells without a further cell; new selftest reproduced | fixed (RM_FlowKernel.cs: cap tested before adding the next dequeued cell + selftest CollectBody_exact_cap_not_truncated) |
| 9 | visual bubbles consume gameplay Rand | real | RM_LiquidSurface.cs Bubbles() runs from MapComponentTick with camera-view-dependent Rand draws | fixed (RM_LiquidSurface.cs: Rand.PushState(tick^map) / PopState around the bubble pass) |
| 31 | overflow total in wrong unit | real (labelling only) | Excavation.cs:788 sole caller passes levels; counter/message consistently levels, only the param name + dev log said "fill-units" | fixed (RM_MapComponent_Excavation.cs: renamed/documented as levels) |
| 32 | bubble density inflated/truncated by integer area/16 | real | RM_LiquidSurface.cs: `represented = max(1, area/16)` with 16 samples always | fixed (RM_LiquidSurface.cs samples=min(16,area), float represented; RM_FillEffectMath.cs BubblesThisTick takes float) |
| 14 | queued ignition survives firefoam | real | RM_LiquidFire.cs AdvanceFront ignited without IsSmothered; foam blast branch of NotifyExplosionAt cleared only burning; postfix skipped when BurningCount==0 | fixed (RM_LiquidFire.cs: smother recheck at execution, foam blast cancels pending cell, postfix also runs while PendingCount>0) |
| 15 | internal blasts re-seed zero-hop ignition past source reach | real | RM_LiquidFire.cs NotifyExplosionAt → TryQueue(..., 0); GenExplosion from AdvanceFront is async (Explosion thing), so origin hops are lost | file → LIQUID_FIRE_QUEUE_ORIGIN_1 |
| 16 | earlier ignition cannot advance a queued cell | real | RM_LiquidFire.cs TryQueue: `pendingSet.Contains(i)` returns before comparing due/hops | file → LIQUID_FIRE_QUEUE_ORIGIN_1 (needs a keyed pending map; IndexOf in TryQueue is O(P) per offer from Maintain) |
| 17 | carriedAcc unsaved / no expiry or fluid identity | real-by-design (save) + real (contamination) | RM_LiquidFire.cs:45-50 comment documents "Not saved: on load a moving level restarts its clock once"; entries never expire and are taken by any later ignition on the cell or its 4 neighbours | file → LIQUID_FIRE_QUEUE_ORIGIN_1 |
| 18 | depth engine off → fire harms without burning fuel | real | Excavation.cs MapComponentTick: liquidFire.Tick before the depthEngineEnabled return; BurnPulse only in DoPulse | fixed (RM_MapComponent_Excavation.cs: BurnPulse on pulse cadence when engine off) |
| 19 | exposure recovery stops after last pit filled | real | Excavation.cs MapComponentTick gated RM_PitExposure.Tick on superdeepCellCount>0; Pit_Hediffs.xml RM_PitExposure has no severityPerDay comp | fixed (RM_MapComponent_Excavation.cs: exposure tick ungated) |
| 1 | recession strands sub-cell stock (5-cap pond → 4 units unusable) | real-by-design (consequence) | RM_StockMath.cs SupportedCells documents "Floor, not round: a body pays for a cell in full or gives it up"; residual < PerCellVolume is unreachable until refill | file → LIQUID_RECESSION_TOPOLOGY_1 (owner judgement: floor vs keep-last-cell) |
| 3 | lake restore overwrites a newly dug receded cell | real | RM_LiquidStock.cs Restore pops receded cell and calls RestoreOriginalTerrain regardless of D; RecordOriginalTerrain first-wins so the dig keeps the lake's water entry | fixed (RM_LiquidStock.cs: skip excavated cells; record stays with the excavation) |
| 7 | fill-in displacement bypasses shut sluices | real | Excavation.cs fill-in BFS enqueued every excavated/source neighbour; kernel uses RM_FlowDoorRules.SealsLiquid (:1059) | fixed (RM_MapComponent_Excavation.cs: sealed cells neither credited nor conducted) |
| 29 | recession counts foreign bodies; degree ≠ connectivity | real | RM_LiquidStock.cs PickRecedeCell counts owner.IsSourceCell(n) (any natural liquid); doc claims "never fragments it" with no articulation test | file → LIQUID_RECESSION_TOPOLOGY_1 |
| 30 | recession scan cost unbounded by the 64-removal guard | real | RM_LiquidStock.cs: Centroid + full footprint scan per removal | partially fixed (centroid hoisted out of the loop, behaviour-identical); remaining O(64×cells×8) scan → LIQUID_RECESSION_TOPOLOGY_1 |
| 2 | legacy rehydrated excavation returns after fill-in | real | Excavation.cs RehydrateFromTerrainIfEmpty (:402) records no original terrain; FillIn Surface branch (:632) RestoreOriginalTerrain no-ops, channel terrain stays at D=0, and an all-zero grid re-rehydrates it on reload | file → EXCAVATION_LEGACY_MIGRATION_FLAG_1 |
| 6 | legacy flood and engine fight over temp terrain | real | FluidDef.cs:158 OwnsFillTerrain includes floodTerrain, so ApplyFillTerrain/ClearFillTerrain strip a Flood_FlowWorks.PlaceFluid (:323) placement on an F=0 excavated cell; the legacy QueueRemoveTerrain can strip an engine fill | file → FLOOD_DRIVER_OWNERSHIP_CONTRACT_1 |
| 8 | sourceless equal-depth channel never redistributes | real (documented trade-off, consequence unstated) | RM_StockMath.cs:342 MayFlowBetween(0,0,d,0,0,d) = false; comment :340 notes hops are constant with no source; pump/driver fill is not a source | file → FLOW_ORDER_EXTERNAL_INPUT_1 |
| 11 | component cap partitions large networks permanently | real-by-design | RM_FlowKernel.cs:54 maxComponentCells=6000 bound; CollectComponent stops at cap, sorted seeds repeat the cut | file → FLOW_ORDER_EXTERNAL_INPUT_1 (only bites >6000-cell networks) |
| 12 | fluid-disable enforced only in driver API | real | FluidAllowed called only at Excavation.cs:1328; settings UI (Mod.cs ~836) promises "pump, drill or any other source"; kernel source transfer, rain, displacement unchecked | file → FLUID_DISABLE_ALL_INPUTS_1 |
| 13 | TrySetDriverFill false is overloaded | real | Excavation.cs:1296 doc "FALSE for a cell this engine does not own"; also false for disabled/foreign fluid on an owned cell | file → FLOOD_DRIVER_OWNERSHIP_CONTRACT_1 |
| 20 | pump picks a foreign-liquid recipient and stops | real | Building_LiquidPump.cs TryPour ranked by room only, then TryPourLevel false → "PumpForeign" | fixed (Building_LiquidPump.cs: incompatible cells skipped before ranking) |
| 25 | off-map ingestion loses the container | real | IngestionOutcomeDoer_BottleResidue.cs returned on MapHeld==null and needed pawn.Spawned for inventory | fixed (inventory first regardless of map; map placement fallback) |
| 26 | missing empty def duplicates tank contents | real | JobDriver_EmptyBottleIntoTank.cs credited tank, then returned on emptyDef==null leaving the full container | fixed (emptyDef resolved before TryAddLiquid) |
| 27 | orphan tank units adopt the next liquid | real | Building_LiquidTank.cs: storedLiquid null (def gone) + storedUnits>0 → Empty true → TryAddLiquid += | fixed (PostLoadInit clears orphan units with a warning) |
| 21 | target filter nulls a chosen target instead of re-selecting | real | RM_Patch_SuperdeepShooting.cs:173 postfix on AttackTargetFinder.BestAttackTarget sets `__result = null` after selection | file → SUPERDEEP_TARGET_VALIDATOR_1 |
| 22 | look application mutates shared cached materials | unclear | RM_LiquidLooks.cs Apply: GraphicDatabase.Get keyed by (tex, shader, colour, precedence), then MatSingle mutated (_MaskTex, flow params); a collision needs two looks with the same key and different flow params, which takes a FluidDef/terrain census to show | file → LIQUID_LOOK_MATERIAL_OWNERSHIP_1 (census first) |
| 23 | live Tune does not invalidate surface caches | real (dev/bridge tool path) | RM_LiquidSurface.cs `mats` cached per look, `lookOf` built once; RM_LiquidLooks.cs Tune re-applied terrain graphics only | fixed (RM_LiquidSurface.ForgetLook destroys the look's owned overlay materials and drops the table; Tune calls it) |
| 24 | repeated look application leaks Materials | real (low; Tune/ApplyAll/settings toggles only) | RM_LiquidLooks.cs Apply: `new Material(o.waterDepthMaterial)` each call, never destroyed on Revert/re-apply | file → LIQUID_LOOK_MATERIAL_OWNERSHIP_1 |

UNVERIFIABLE bullets at the end of Part 1 were not claims and are not ruled on.

#### Files changed
- `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source\RM_FlowKernel.cs` (#10, #28)
- `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source\RM_MapComponent_Excavation.cs` (#7, #18, #19, #31)
- `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source\RM_LiquidFire.cs` (#14)
- `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source\RM_LiquidStock.cs` (#3, #30 partial)
- `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source\RM_LiquidSurface.cs` (#9, #23, #32)
- `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source\RM_LiquidLooks.cs` (#23)
- `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source\RM_FillEffectMath.cs` (#32: BubblesThisTick takes float)
- `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source\RM_PitFillEffects.cs` (#4)
- `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source\Drilling\Building_LiquidDrill.cs` (#5)
- `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source\LiquidTypes\Building_LiquidPump.cs` (#20)
- `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source\LiquidTypes\Building_LiquidTank.cs` (#27)
- `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source\LiquidTypes\IngestionOutcomeDoer_BottleResidue.cs` (#25)
- `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source\LiquidTypes\JobDriver_EmptyBottleIntoTank.cs` (#26)
- `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source\SelfTest\FlowKernelFuzz.cs` + `Program.cs` (new cases Sealed_sink_does_not_drain, CollectBody_exact_cap_not_truncated; both FAILED before the kernel fix)
- `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Assemblies\RimMandrakeFlowWorks.dll` + `.dll.srchash` (rebuilt)

#### Items to file
| NAME | title | spec |
|---|---|---|
| LIQUID_FIRE_QUEUE_ORIGIN_1 | Liquid fire queue: carry origin/hops through blasts, let earlier offers advance, scope carried burn | #15/#16/#17. RM_LiquidFire.NotifyExplosionAt queues every blast cell at hops 0, and the detonation's GenExplosion (AdvanceFront) is an async Explosion thing, so a detonation re-seeds zero-hop ignition deeper into a body and SourceFireReach stops binding. TryQueue drops any offer for an already-pending cell (`pendingSet.Contains`), so a direct flame cannot advance a slow fuse; fix needs a keyed pending map (a list IndexOf per offer is O(P) from Maintain). carriedAcc (RM_LiquidFire.cs:45-50) is unsaved by design but has no expiry or fluid identity, so a later ignition anywhere near takes stale progress. |
| LIQUID_RECESSION_TOPOLOGY_1 | Recession: same-body neighbours, no fragmentation, bounded scan, sub-cell residual | #1/#29/#30. RM_LiquidStock.PickRecedeCell counts owner.IsSourceCell(n), which is any natural liquid (another body or fluid), and lowest degree is not an articulation test, so the documented "never fragments it" is unenforced. Each of up to 64 removals rescans the whole footprint ×8 (the centroid is now hoisted). SupportedCells floors (RM_StockMath.cs:150), so a body's last <PerCellVolume units are stranded until refill. Owner call on floor-vs-keep-last-cell. |
| EXCAVATION_LEGACY_MIGRATION_FLAG_1 | Legacy rehydration: schema flag and a restoration policy for cells with no original terrain | #2. RehydrateFromTerrainIfEmpty (RM_MapComponent_Excavation.cs:402) runs whenever the depth grid is all zero and records no original terrain; FillIn's Surface branch (:632) then cannot restore, leaving channel terrain at D=0 that the next load (grid all zero again) re-reads as an excavation. Needs a saved migration flag plus a fallback terrain for unrecorded cells. |
| FLOOD_DRIVER_OWNERSHIP_CONTRACT_1 | Legacy flood vs engine temp terrain; split TrySetDriverFill's false | #6/#13. FluidDef.OwnsFillTerrain includes floodTerrain (FluidDef.cs:158), so ApplyFillTerrain/ClearFillTerrain strip a Flood_FlowWorks.PlaceFluid (:323) placement on an excavated F=0 cell, and the legacy QueueRemoveTerrain can later strip an engine fill. TrySetDriverFill returns false both for "not mine" (documented) and for disabled/foreign fluid on an owned cell, so a driver obeying the doc falls back to terrain writes on an engine cell. Route legacy releases on excavated cells through the driver API; return an outcome enum. |
| FLOW_ORDER_EXTERNAL_INPUT_1 | Flow order for sourceless (pump/drill/rain-fed) channels and >6000-cell networks | #8/#11. MayFlowBetween (RM_StockMath.cs:342) allows only gravity at equal keys, and with no supplying source every key is equal, so a pump-filled equal-depth run never spreads (stays beside the pump). maxComponentCells=6000 (RM_FlowKernel.cs:54) cuts big networks into fixed partitions that never exchange. Needs an ordering seeded from external inputs that keeps FLOWWORKS_CHANNEL_OSCILLATION_1 acyclic; prove with a kernel fixture. |
| FLUID_DISABLE_ALL_INPUTS_1 | Enforce "liquid switched off" on every input, as the settings UI promises | #12. FluidAllowed is checked only in TrySetDriverFill (RM_MapComponent_Excavation.cs:1328, and now the drill); the UI text says "pump, drill or any other source", but kernel source transfers, rain and legacy releases ignore it. Centralise the check on new input; keep "what already stands stays". |
| SUPERDEEP_TARGET_VALIDATOR_1 | Superdeep shooting rule as a target validator, not a post-selection null | #21. RM_Patch_SuperdeepShooting.cs:173 postfixes BestAttackTarget and nulls a forbidden pick, so the finder never tries its next candidate. Wrap the `validator` argument in a prefix with PairAllowed instead. Needs a live check. |
| LIQUID_LOOK_MATERIAL_OWNERSHIP_1 | Liquid looks own their materials | #22/#24. RM_LiquidLooks.Apply mutates the MatSingle of a GraphicDatabase-cached graphic keyed only by (tex, shader, colour, precedence), and allocates `new Material(waterDepthMaterial)` per apply with no Destroy on Revert/re-apply. Census the FluidDefs for key collisions first; then give each look owned materials, destroyed on revert. |

#### Build
- `winbuild.py FlowWorks`: `BUILT src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll (source b31b7ad696d6+dirty)`, 0 warnings, 0 errors.
- Selftests, before and after: `selftest_flowworks_stock.py` 122/122 → 124/124 (2 new cases red before the fix, green after); `selftest_flowworks_kernel_oracle.py` kernel == PulseOracle 3000/3000; cover_breaks, looks_round, rivers, swale, Tools/selftest_liquid_looks: all PASS.
- Not covered by any selftest (adapter code, needs live or offline adapter tests): #3, #4, #5, #7, #9, #14, #18, #19, #20, #23, #25, #26, #27.

## GimmeSomeSlack

Counts: 25 claims — 24 real (several low-severity or probe-only), 1 false (#5), 0 unclear. 17 fixed in source (#7 and #12 partially), 5 items to file (covering #2, #3, #7-sharing, #8, #9, #11, #12-bucketing, #17, #20).

All paths below are relative to `src/RimMandrake/GimmeSomeSlack/Source/`. GPT line numbers matched the current source.

| # | claim (short) | verdict | evidence (file:line, one line) | action |
|---|---|---|---|---|
| 1 | same-frame edits dropped; StaleOffscreen cleared before rebuild can run | real (narrow) | RM_MapComponent_CordGraph.cs:680-684 clears the flag even when `builtFrame == frameCount` skips the rebuild, so a dirty event landing after that frame's rebuild is lost. The on-screen half is false: a dirtied section regenerates in a later frame, whose `PiecesForSection` rebuilds (:48). | fixed (defer, don't clear) |
| 2 | roof change doesn't dirty the owner section of a distant strand | real | static exclusion reads roof at the pin / midpoint (:404-407, :440-446) but `Sig` (:269-273) carries no eligibility, and only the roofed cell's section is dirtied | file → CORD_STATIC_DYNAMIC_HANDOFF_1 |
| 3 | `Prefs.PlantWindSway` toggle never reprints static meshes | real | `SwayOn`/`RipplesNow` read the pref live (:401, :442); grep finds no invalidation on that pref change (only `Notify_SettingsChanged` for mod settings) | file → CORD_STATIC_DYNAMIC_HANDOFF_1 |
| 4 | dynamic culling tests one point; "tip" is the joint | real (low) | whip tests `Pts[cnt-1]`, which `Reverse()` makes `tail[0]` = the joint (:496-499, comment says "outer end"); sway tests only the pin (:534), ripple only the midpoint (:562) | fixed (any point of the drawn polyline in view) |
| 5 | lifted strands have no far-zoom LOD | false | lifted strands are built `OverFace = true` (Core/CordBuilder.cs:793) and the LOD pass deliberately excludes every OverFace strand (SectionLayer_RM_MessyCords.cs:144); moving LOD before the `continue` would print nothing different. Face strands vanishing at far zoom is the LOD design ("one strand per piece, no decals") | none (by design) |
| 6 | far zoom kills downed-wire sparks and selection highlight | real | `DrawMotion` returns on `FarNow` (:471) before `DownedWires` (:578) and `DrawHighlight` (:580), while `Sparks` skips wall ends whenever `downedWire` is on (:359) — so wall ends throw nothing at far zoom | fixed (effects + highlight run before the far-zoom return) |
| 7 | "max sparking ends" not shared; wall ends counted then skipped | real | `Sparks` increments `n` (:358) before skipping wall ends (:359), starving floor ends; `DownedWires` has its own separate cap (:592) | fixed (starvation: skip before counting); sharing → file SPARK_EFFECT_BUDGET_REWORK_1 |
| 8 | spark intensity doesn't scale downed-wire spark count | real (low) | `DownedWireSchedule(seed, now)` and `SparksDue(now)` take no intensity (:594, :606); intensity only scales the flash size (:602) | file → SPARK_EFFECT_BUDGET_REWORK_1 |
| 9 | offscreen ends consume the effect budget first | real (low) | `DrawLiveGlow` (:333-337), `Sparks` (:354-358), `DownedWires` (:587-592) admit in piece order with no view filter | file → SPARK_EFFECT_BUDGET_REWORK_1 |
| 10 | snapshot/style scan outside the try; builder failure publishes empty set | real | `CordWorldAdapter.Snapshot` (:205) and `CellStyles` (:210) are outside the try; the catch publishes `new List<LaidPiece>()` (:217), contradicting the "never leave the map with no cords" comment at :230 | fixed (whole input+build guarded; on failure keep the previous published pieces) |
| 11 | every regenerate in a later frame = whole-map rebuild | real (perf) | `PiecesForSection` rebuilds whenever `frameCount != builtFrame` (:48), so a PollLive flip (:308) dirtying one section reruns Snapshot + CellStyles + seeds + Sig for the whole map | file → CORD_GRAPH_TOPOLOGY_REVISION_1 |
| 12 | per-frame motion rescans all pieces per material | real (perf) | 3 loops × up to 16 material passes over `pieces` (:481, :526, :551); sway loop runs even when sway is off | fixed (sway loop skipped unless CPU sway is on); bucketing → file CORD_GRAPH_TOPOLOGY_REVISION_1 |
| 13 | motion meshes allocated empty, never destroyed | real | `Flush` calls `Fresh` before checking `mv.Count` (:456-458); no `MapRemoved` override (MapComponent has `virtual MapRemoved()`, RimSage) | fixed (allocate only with vertices; destroy in `MapRemoved`) |
| 14 | static draw counters reset by an inactive map | real (probe-only) | counters zeroed (:468, :326) before the `Find.CurrentMap != map` check (:469, :328) | fixed (reset only on the current map) |
| 15 | 65k-vertex cap drops geometry silently | real (low) | `Ribbon`/`Quad` return 0 past `MaxMeshVerts` (SectionLayer_RM_MessyCords.cs:215, :246) with no counter | fixed (overflow counter `OverflowDrops`) |
| 16 | cross-map anchors pass `Verdict` | real (low) | `Verdict` checks spawned/faction/range (Aerial/CompAerialAnchor.cs:247-253) but never `a.Map == b.Map` | fixed |
| 17 | cut point floored to a cell; length measured to exact point | real (low) | `Cut` floors `cut` into `toward` (Aerial/CompAerialAnchor.cs:291) while `length` uses the exact point; consumer re-centres at `+0.5` (Aerial/RM_MapComponent_Aerial.cs:302) | file → AERIAL_CUT_POINT_PRECISION_1 |
| 18 | `LayFallen` emits a different curve from the one it checked | real | pass 1 checks `ground(s, want)`; pass 2 emits `ground(sPos, reach)` (Aerial/AerialMath.cs:390-405) — a different bow when blocked | fixed (emit the checked curve `ground(sPos, want)`) |
| 19 | tap debit can be paid twice | real (1 tick) | engine order (RimSage, TickManager.DoSingleTick): `MapPreTick` (nets) runs BEFORE `ticksGameInt++` and thing ticks, so a debit written at tick T is read by the net at TicksGame=T and AGAIN at T+1 if the tap stopped, via `e.tick >= now - 1` (Aerial/CompPowerTap.cs:158). The "either order" comment is false | fixed (`e.tick == now`) |
| 20 | tap connect guards disagree (net-level vs transmitter-level faction) | real | `NetHasFaction` admits a mixed net (Aerial/CompPowerTap.cs:197-198); `ConnectToTransmitter` guard refuses a foreign transmitter and re-queues (:217-224) → retry every net update | file → POWER_TAP_MIXED_NET_CONNECT_1 |
| 21 | NaN tap rate propagates into power | real (low) | `rateW <= 0` is false for NaN and `Math.Min(NaN, x)` = NaN (Aerial/AerialMath.cs:520-523) | fixed (`!(rateW > 0)` + finite guard) |
| 22 | `sinceEventWd` not saved; victims merged | real (low) | not in `PostExposeData` (Aerial/CompPowerTap.cs:59-63); `TapEvents` has no subscribers yet (:166) | fixed (Scribe); victim attribution none (no subscriber exists) |
| 23 | settings round-trip probe not exception-safe | real (probe-only) | restore at StyleProbe.cs:136-140 is not in `finally` | fixed (try/finally) |
| 24 | "fresh" oracle uses different inputs; ignores stale extras | real (probe-only) | production sets `opt.PileAt` (RM_MapComponent_CordGraph.cs:212), `Fresh` does not (GimmeSomeSlackProbe.cs:214); only fresh keys iterated (:217) | fixed (same PileAt; `extra` count added) |
| 25 | Harmony finalizer decrements an unentered scope | real (rare) | Finalizer always `depth--` (Aerial/AerialPowerPatch.cs:31, :38); a throwing earlier prefix runs our finalizer without our prefix | fixed (`__state` flag) |

#### Files changed
- `/home/mandrake/rm/foundry/src/RimMandrake/GimmeSomeSlack/Source/RM_MapComponent_CordGraph.cs` (#1, #4, #6, #7, #10, #12, #13, #14)
- `/home/mandrake/rm/foundry/src/RimMandrake/GimmeSomeSlack/Source/SectionLayer_RM_MessyCords.cs` (#15)
- `/home/mandrake/rm/foundry/src/RimMandrake/GimmeSomeSlack/Source/Aerial/CompAerialAnchor.cs` (#16)
- `/home/mandrake/rm/foundry/src/RimMandrake/GimmeSomeSlack/Source/Aerial/AerialMath.cs` (#18, #21)
- `/home/mandrake/rm/foundry/src/RimMandrake/GimmeSomeSlack/Source/Aerial/CompPowerTap.cs` (#19, #22)
- `/home/mandrake/rm/foundry/src/RimMandrake/GimmeSomeSlack/Source/Aerial/AerialPowerPatch.cs` (#25)
- `/home/mandrake/rm/foundry/src/RimMandrake/GimmeSomeSlack/Source/StyleProbe.cs` (#23)
- `/home/mandrake/rm/foundry/src/RimMandrake/GimmeSomeSlack/Source/GimmeSomeSlackProbe.cs` (#24; `fresh` JSON gains an `extra` field)
- `/home/mandrake/rm/foundry/src/RimMandrake/GimmeSomeSlack/Assemblies/RimMandrakeGimmeSomeSlack.dll` + `.dll.srchash` (rebuilt)

#### Items to file
| NAME | title | spec |
|---|---|---|
| CORD_STATIC_DYNAMIC_HANDOFF_1 | Static/dynamic cord ownership ignores roof and plant-sway-pref changes | Whether a strand is printed static or drawn per frame depends on the roof at its pin/midpoint (RM_MapComponent_CordGraph.cs `PinRoofed`/`RipplesNow`) and on `Prefs.PlantWindSway` (`SwayOn`), but the owner-section signature `Sig` carries neither, and nothing reprints on a pref toggle. A roof placed on a cell in a different section from the strand's owner, or toggling the vanilla plant-sway option, can leave a strand drawn by neither path or by both. Fix: include per-strand eligibility bits captured at print time in `Sig`, and dirty all sections on a `PlantWindSway` / effective-sway-mode transition. |
| SPARK_EFFECT_BUDGET_REWORK_1 | Spark/glow budget is not shared, ignores the view, and ignores intensity for wall ends | `DrawLiveGlow`, `Sparks` and `DownedWires` (RM_MapComponent_CordGraph.cs) each admit up to `MaxSparkingEnds` in piece order with no viewport priority, so wall + floor ends can reach 2x the setting and offscreen ends starve visible ones. `DownedWireSchedule`/`SparksDue` take no `sparkIntensity`, so the setting changes only the flash size for wall ends. Pick one visible-first endpoint set per frame shared by all three, and scale scheduled emission by intensity with fractional credit. (Wall-ends-counted-then-skipped starvation already fixed.) |
| CORD_GRAPH_TOPOLOGY_REVISION_1 | Cord graph rebuilds the whole map for every section reprint; motion rescans all pieces per material | `PiecesForSection` reruns Snapshot + CellStyles + seeds + Sig whenever any section regenerates in a new frame (RM_MapComponent_CordGraph.cs:48), including a PollLive flip that only needs a reprint. `DrawMotion` scans all pieces up to 16x per pass (whip/sway/ripple). Track a topology revision (bumped by the MapMeshDirty patch) and rebuild only when it moves; bucket pieces by material and section at rebuild. Perf only; needs a live frame-time measurement to prioritise. |
| AERIAL_CUT_POINT_PRECISION_1 | A cut span's fallen halves aim at the cell centre, not the cut point | `CompAerialAnchor.Cut` floors the exact cut point into `FallenCord.toward` (IntVec3) while `length` is measured to the exact point; `RM_MapComponent_Aerial.cs:302` re-centres at +0.5, so a diagonal cut lands up to ~0.71 cell off. Save exact `towardX/towardZ` floats (default NaN → legacy cell centre) and lay toward them. Cosmetic. |
| POWER_TAP_MIXED_NET_CONNECT_1 | Power-tap connect guards disagree on mixed-faction nets | `Patch_TryConnect_TapOwnFaction` allows any net with one own-faction transmitter (CompPowerTap.cs `NetHasFaction`), but `Patch_ConnectToTransmitter_TapGuard` refuses the specific transmitter if foreign and re-queues via `Notify_ConnectorWantsConnect`. If the nearest transmitter of an allowed mixed net is foreign, the clamp re-queues every net update forever. Filter at transmitter level (or pick the nearest own-faction transmitter directly) and stop re-queueing on a refusal the same predicate will repeat. |

#### Build
- `python3 src/RimMandrake/Utils/winbuild.py GimmeSomeSlack` → `Build succeeded. 0 Warning(s) 0 Error(s)`; `BUILT src/RimMandrake/GimmeSomeSlack/Assemblies/RimMandrakeGimmeSomeSlack.dll`.
- `python3 validation.py` (offline tier): 7/8 PASS — O3 core SelfTest 818/818 + aerial 90/90 + hose 120/120, O3n probe 7/7, O4 oracle 44/44, O7 23 fix shapes. **O2_settings_defaults FAIL `sprawlCap != 16f` is pre-existing**: no settings file was edited here and `sprawlCap` does not appear in `GimmeSomeSlackMod.cs` (the validator's SHIPPED table at validation.py:112 is stale or the field moved).
- Not deployed; not code-review marked. #1/#4/#6/#13/#14 are render/frame-path changes only a live pass can confirm visually.

## LuminousPigment

| # | claim (short) | verdict | evidence (file:line, one line) | action |
|---|---|---|---|---|
| 1 | Meal steering metadata merges/splits unprotected | real | CompSkillSteeredOutcome.cs only PostExposeData; RM_MealDeepfire parent MealFineBase stacks | fixed (CompSkillSteeredOutcome.cs: AllowStackWith + PostSplitOff) |
| 2 | CompDeepfire coats/bonusApplied lost on split/merge | real (narrow: stackable injected targets, e.g. modded throwables) | CompDeepfire.cs no AllowStackWith/PostSplitOff; injector takes any IsWeapon/CompColorable | fixed (CompDeepfire.cs: AllowStackWith + PostSplitOff). "Whole stack coated at one unit's cost" left as is (no stackable target in shipped set measured) |
| 3 | Fresh-mat age not preserved across split/merge | real | CompMatVitality.cs no PostSplitOff/PreAbsorbStack; RM_CrowncarpetFresh stackLimit 25 | fixed (CompMatVitality.cs: copy on split, count-weighted age on merge, CompRottable policy) |
| 4 | Apply job: despawned target -> NRE at Target.Map | real | JobDriver_ApplyDeepfire.cs:64 checked only null/Destroyed; :78 Target.Map.designationManager | fixed (JobDriver_ApplyDeepfire.cs: Spawned + CanAddCoat + designation-present checks) |
| 5 | Pigment consumed though target full / nothing carried | real | ApplyDeepfire.cs:74-77, LacquerWornItem.cs:55-56 Destroy then void AddCoat | fixed (both drivers: CanAddCoat + CarriedThing checked before consuming; ApplyDeepfire had no CanAddCoat check). Carried-count-vs-cost not validated: folded into PIGMENT_JOB_PAYMENT_ALLOCATION_1 |
| 6 | Zero-cost settings still need stocked pigment | real | LuminousPigmentMod.cs:302-316 sliders min 0; FindNearbyDeepfire null with no stack | fixed (zero disallowed: whole-target cost sliders min 1, DeepfirePaintUtility.cs CostFor Max(1), DeepfireFloorJobs.cs Max(1) x3; per-extra-cell stays 0-able) |
| 7 | Worn lacquer bypasses paintingEnabled/class toggles | real | DeepfireWornGlow.cs Lacquerable + LacquerWornItem.cs MakeJob checked only CanAddCoat | fixed (new WornGlowUtility.LacquerAllowed used in Lacquerable, MakeJob (covers styling station, DeepfireStylingStationPatches.cs:140), StillValid) |
| 8 | Designator rejects factionless loose items | real | Designator_Deepfire.cs:78 (and remove designator :145) `t.Faction != OfPlayer` on items with null faction | fixed (Designator_Deepfire.cs: faction required for buildings only, both designators) |
| 9 | Hediff lights orphaned on despawn/death/map change | real | MapComponent_DeepfireLights.cs:136 early return when unspawned; bridge also returned on Map null; no death hook | fixed (MapComponent_DeepfireLights.cs RegisterHediffGlow removes key on other maps / all maps when unspawned/dead; HediffComp_DeepfireGlow.cs Notify_PawnDied + bridge passes unspawned pawns) |
| 10 | Hediff lights trail moving pawns, respawn per move | real | HediffComp_DeepfireGlow.cs:71 250-tick poll; MapComponent_DeepfireLights.cs:169 destroy+respawn on cell change | file → HEDIFF_GLOW_MOVING_PROXY_1 |
| 11 | Worn intensity multiplied twice | real (invisible at defaults: coatIntensity[3]=1.0) | DeepfireWornGlow.cs:64 GlowColorFor(..,MaxCoats) + RM_DeepfireRules.cs WornBlend *k | fixed (DeepfirePaintUtility.cs new GlowHueFor; DeepfireWornGlow.cs uses it) |
| 12 | Darkness test subtracts own light at pawn cell, not proxy cell | real (bounded by worn poll interval) | DeepfireWornGlow.cs OtherLightAt(pawn.Position,...) — comment admits off-by-poll | file → WORN_DARKNESS_PROXY_POSITION_1 |
| 13 | Black (zero-RGB) worn light still counts as glowing | real (only with glowMinValue 0) | DeepfireWornGlow.cs IsGlowingInDark no emission check; LuminousPigmentMod.cs:297 slider min 0 | fixed (DeepfireWornGlow.cs: zero RGB / zero radius -> not glowing) |
| 14 | Cluster light can miss a member cell | real | RM_DeepfireLightBook.cs:297-299 radius = coat radius + 1 regardless of spread; (0,0)/(2,2) dist 2.83 > 2.5 | file → CLUSTER_LIGHT_MEMBER_COVERAGE_1 |
| 15 | pulsesWithHeartRate / glowTargetFactorOverride inert | real | read nowhere in Source; set in RM_DeepfireGlowHediffs.xml:372,495,582 | file → HEDIFF_GLOW_TARGETING_PULSE_1 |
| 16 | Ishko stage-3 event gated by visual toggle | real | HediffComp_DeepfireGlow.cs Apply: ishko block inside else-branch of hediffGlowEnabled | fixed (HediffComp_DeepfireGlow.cs: event evaluated before the glow branch; delivery still gated by godsReact in NinefoldDeltaBridge.cs:142) |
| 17 | "Buildable" press gate finishes research permanently | real | LuminousPigmentMod.cs:470 FinishProject; no un-finish on switching back; new games only if ApplySettings reruns | file → PRESS_GATE_BUILDABLE_RESEARCH_1 |
| 18 | Settings apply misses non-building own-light entries | unclear | ApplyClusterBlockToMaps (MapComponent_DeepfireLights.Clusters.cs:217) rebuild scope not traced to own-light items; needs live check of a loose coated item after a radius change | file → DEEPFIRE_SETTINGS_LIGHT_REFRESH_1 |
| 19 | Stockpile-glow toggle doesn't refresh existing glowers | unclear | LuminousPigmentMod.cs:499 mutates CompProperties_Glower.glowRadius only; whether live CompGlower/glow grid re-reads Props needs engine/live check | file → DEEPFIRE_SETTINGS_LIGHT_REFRESH_1 |
| 20 | Coat changes don't invalidate stat caches | unclear | CompDeepfire.cs AddCoat/RemoveAllCoats no cache clear; Beauty/MeleeDodgeChance cacheability needs RimSage StatDef check | none (needs engine evidence) |
| 21 | Glow tank seed never consumed on first sow | real | Building_GlowTank.cs header promises "consumed once, on the first successful sow"; only ConsumeFuel is the blackout branch | file → GLOW_TANK_SEED_CULTURE_1 |
| 22 | Discovery missed if mats removed before a long tick | real (minor) | CompMatDiscovery.cs:30 CompTickLong only, no harvest hook | file → MAT_DISCOVERY_SIGHT_RULE_1 |
| 23 | Discovery counts prisoners, no line of sight | real (minor; spec intent unclear) | CompMatDiscovery.cs:48 FreeColonistsAndPrisonersSpawned + distance only | file → MAT_DISCOVERY_SIGHT_RULE_1 |
| 24 | Mat replacement ignores insert failure, leaves old Thing alive | real | CompMatVitality.cs:87-88 Remove then unchecked TryAdd, parent never destroyed | fixed (CompMatVitality.cs: failed TryAdd places at root position; detached parent destroyed). Spawned-branch order left (TryPlaceThing Near failure negligible) |
| 25 | "Diminish" can increase a reaction | real | RM_DeepfireRules.cs:140 returns ±magnitude even when \|amount\|<magnitude; slider permits 0.25 | file → GOD_DELTA_DIMINISH_CLAMP_1 (fuzz LuminousPigmentFuzz.cs:482 asserts the current ±1 rule, so changing it is a spec decision, not a quiet fix) |
| 26 | Every Ideology role classified as titled | real | SumptuaryEngine.cs:96 any GetRole != null; its own comment says leader/moral-guide | fixed (SumptuaryEngine.cs: leaderRole or IdeoRole_Moralist only) |
| 27 | Queued styling jobs bind the same insufficient stack | real | JobDriver_LacquerWornItem.cs MakeJob picks a concrete stack per job with no cross-job allocation | file → PIGMENT_JOB_PAYMENT_ALLOCATION_1 |
| 28 | Several settings have no controls | real | LuminousPigmentMod.cs:44,46,53-55 pressResearchCost/pressWorkAmount/tankGrowDays/tankYield/tankPower scribed+applied, no slider in DoWindowContents | file → DEEPFIRE_SETTINGS_MISSING_CONTROLS_1 |
| 29 | Family toggles discarded on array length change | real | LuminousPigmentMod.cs:196 positional list accepted only on exact length | file → DEEPFIRE_FAMILY_SETTINGS_KEYED_1 |
| 30 | Unchanged lights re-registered every poll | real | MapComponent_DeepfireLights.cs:176 unconditional ForceRegister | fixed for the shared SetLight path (MapComponent_DeepfireLights.cs: skip when proxy, colour and radius unchanged); worn sweep not touched |

Unverifiable list in the review (reservation arg order, recipe inheritance, cuisine visibility, genstep registration, defs, save compat, validation coverage): not claimed defects; skipped. Note on the reservation one: `pawn.Reserve(thing, job, maxPawns, stackCount, ...)` — `job.count` in the maxPawns slot is GPT's suspicion; not verified here.

#### Files changed
- `D:\Luke\dev\RimMandrake\src\RimMandrake\LuminousPigment\Source\CompSkillSteeredOutcome.cs`
- `D:\Luke\dev\RimMandrake\src\RimMandrake\LuminousPigment\Source\CompDeepfire.cs`
- `D:\Luke\dev\RimMandrake\src\RimMandrake\LuminousPigment\Source\CompMatVitality.cs`
- `D:\Luke\dev\RimMandrake\src\RimMandrake\LuminousPigment\Source\JobDriver_ApplyDeepfire.cs`
- `D:\Luke\dev\RimMandrake\src\RimMandrake\LuminousPigment\Source\JobDriver_LacquerWornItem.cs`
- `D:\Luke\dev\RimMandrake\src\RimMandrake\LuminousPigment\Source\DeepfireWornGlow.cs`
- `D:\Luke\dev\RimMandrake\src\RimMandrake\LuminousPigment\Source\DeepfirePaintUtility.cs`
- `D:\Luke\dev\RimMandrake\src\RimMandrake\LuminousPigment\Source\DeepfireFloorJobs.cs`
- `D:\Luke\dev\RimMandrake\src\RimMandrake\LuminousPigment\Source\LuminousPigmentMod.cs`
- `D:\Luke\dev\RimMandrake\src\RimMandrake\LuminousPigment\Source\Designator_Deepfire.cs`
- `D:\Luke\dev\RimMandrake\src\RimMandrake\LuminousPigment\Source\MapComponent_DeepfireLights.cs`
- `D:\Luke\dev\RimMandrake\src\RimMandrake\LuminousPigment\Source\HediffComp_DeepfireGlow.cs`
- `D:\Luke\dev\RimMandrake\src\RimMandrake\LuminousPigment\Source\SumptuaryEngine.cs`
- `D:\Luke\dev\RimMandrake\src\RimMandrake\LuminousPigment\Assemblies\RimMandrakeLuminousPigment.dll` (+ `.dll.srchash`)

(Working copies are in the foundry seat clone `/home/mandrake/rm/foundry/...`; the D:\ paths are the mirror they land in after the push.)

#### Items to file
| NAME | title | spec |
|---|---|---|
| HEDIFF_GLOW_MOVING_PROXY_1 | Cuisine hediff lights should ride the worn moving-proxy machinery | HediffComp_DeepfireGlow.cs:71 updates every 250 ticks and MapComponent_DeepfireLights.cs SetLight destroys and respawns the proxy on every cell change, so a walking pawn's light lags many cells and churns spawns. Route hediff emission through the per-pawn moving proxy (MapComponent_DeepfireLights.Worn.cs, 15-tick poll, moved by Position) and keep the 250-tick check only for stage/colour changes. |
| WORN_DARKNESS_PROXY_POSITION_1 | Darkness test should subtract our light at the proxy's real cell | DeepfireWornGlow.cs OtherLightAt subtracts the own-light centre contribution at pawn.Position, but the proxy may be up to one poll behind (setting allows 60 ticks). Use the proxy's actual cell and distance falloff, or sync the proxy before evaluating. |
| CLUSTER_LIGHT_MEMBER_COVERAGE_1 | Cluster light radius must cover its farthest member | RM_DeepfireLightBook.cs:297-299 sets radius = coat radius + 1 around a member anchor, so diagonal members in a 3x3 block (dist 2.83) sit outside a 2.5 light. Bound radius by max member distance from the anchor plus coverage, or split the group; add a fuzz property "every member within its cluster light". |
| HEDIFF_GLOW_TARGETING_PULSE_1 | Wire or remove inert hediff glow targeting/pulse fields | `glowTargetFactorOverride` (RM_DeepfireGlowHediffs.xml:372,582) and `pulsesWithHeartRate` (:495) are declared in HediffComp_DeepfireGlow.cs:44,49 and read nowhere; DeepfireDarkness consults worn lights only. Either feed hediff lights + override into the combat darkness model and the pulse, or delete the advertised behaviour. |
| PRESS_GATE_BUILDABLE_RESEARCH_1 | "Buildable" press gate must not finish the research project | LuminousPigmentMod.cs:470 calls FinishProject on RM_DeepfireRefining; switching back to Research leaves it finished, and other consumers (tank) inherit the unlock. Bypass the press's research prerequisite for the setting instead, and apply it per game, not only when ApplySettings happens to run with a game loaded. |
| DEEPFIRE_SETTINGS_LIGHT_REFRESH_1 | Settings changes should refresh every existing deepfire light | ApplySettings (LuminousPigmentMod.cs:523) only rebuilds clusters; own-light loose items/worn lights and RM_Deepfire stack glowers (:499 Props-only mutation) may keep stale radius/intensity until another notify. Measure live first, then refresh all registered owners + resource glowers on affected maps. |
| GLOW_TANK_SEED_CULTURE_1 | Glow tank never consumes its seed culture | Building_GlowTank.cs header promises the seed is consumed on the first successful sow, but nothing calls ConsumeFuel except the blackout branch, so the seed is permanent. Add a scribed "established" state: consume on first sow, clear on blackout; CanAcceptSowNow gates on established-or-fuelled. |
| MAT_DISCOVERY_SIGHT_RULE_1 | Mat discovery: decide who must see it and add a harvest trigger | CompMatDiscovery.cs:48 counts prisoners and uses distance with no line of sight; :30 checks only on long ticks, so a mat harvested first never triggers. Decide the sight rule (colonists only? LOS?) and add discovery on harvest/haul of fresh mat. |
| GOD_DELTA_DIMINISH_CLAMP_1 | Diminish must never enlarge a god reaction | RM_DeepfireRules.cs:140 returns ±magnitude for any non-zero amount after the threshold, so a 0.25 slider value becomes 1. Use sign(a)*min(\|a\|, magnitude), keep 0 as 0, and update the fuzz assertion at LuminousPigmentFuzz.cs:482 as part of the same spec change. |
| PIGMENT_JOB_PAYMENT_ALLOCATION_1 | Deepfire jobs: allocate pigment across queued jobs and validate payment | LacquerWornItemUtility.MakeJob (JobDriver_LacquerWornItem.cs:133) and both WorkGivers pick one concrete stack per job with no cross-job allocation, so queued styling jobs can all target one stack; completion never checks the carried count against the cost. Resolve the stack when the job starts (or allocate), allow multi-stack fetch, and require carried count >= cost before AddCoat. |
| DEEPFIRE_SETTINGS_MISSING_CONTROLS_1 | Expose press/tank settings that have no controls | pressResearchCost, pressWorkAmount, tankGrowDays, tankYield, tankPower (LuminousPigmentMod.cs:44-55) are scribed and applied but DoWindowContents has no slider for them. Add bounded sliders with units. |
| DEEPFIRE_FAMILY_SETTINGS_KEYED_1 | Family toggles should be saved by family key | LuminousPigmentMod.cs:196 keeps the saved familyEnabled list only if its length matches; adding a family resets all toggles and reordering moves them. Serialize by stable family name, migrating the positional legacy list. |

#### Build
`winbuild.py LuminousPigment`: `Build succeeded. 0 Warning(s) 0 Error(s)` -> `BUILT src/RimMandrake/LuminousPigment/Assemblies/RimMandrakeLuminousPigment.dll (source b31b7ad696d6+dirty)`.
Selftests: `selftest_luminouspigment.py` -> ALL OK; `Utils/selftest_luminouspigment_fuzz.py` -> `7500 cases, 1517652 steps ... -> OK`.
Not deployed, not live-tested, not marked code-review clean.

## Scarlands

GPT review: design/RimMandrake/gpt_reviews/Scarlands.md, Part 1 (claims 1-40; claim 4 split a-d). Rows grouped by source file.

| # | claim (short) | verdict | evidence (file:line, one line) | action |
|---|---|---|---|---|
| 1 | Ungoverned map keeps permanent Settling running | real | Source/RM_Settling.cs:368 returns before the cond.End() at :377; GameConditionTick :110 has no governs gate | fixed (RM_Settling.cs: ungoverned map ends the condition; a running sweep still finishes) |
| 2 | liftHit not saved | real (minor) | RM_Settling.cs:195 `readonly HashSet<int> liftHit` absent from ExposeData :210-220 | fixed (RM_Settling.cs: liftHit Scribed; sweep cursor lives in CreatureBehaviors, out of scope) |
| 3 | Reveal spawns into since-built cell | real | RevealCheck :285-287 never rechecks cell c; GenSpawn.Spawn default WipeMode.Vanish wipes a building there | fixed (RM_Settling.cs: skip while an edifice/unwalkable cell, record kept; spawn with WipeMode.VanishOrMoveAside) |
| 10 | Set off from range never shoots | real (design gap) | WorkGiver_TriggerOrdnance :559-560 only checks IsRangedWeapon; driver :594 calls Detonate, no verb/ammo/range | file → ORDNANCE_TRIGGER_REAL_SHOT_1 |
| 11 | Detonate may not explode | false | RM_BuriedOrdnance.xml: HP 60 + CompProperties_Explosive (no requiredDamageType); 200 Bomb >= HP triggers vanilla CompExplosive.PostPreApplyDamage detonation | none |
| 19 | cancelled orders still complete | real | JobDriver_DefuseOrdnance :511 / TriggerOrdnance :587 / SweepWarDust :625 never recheck defuseWanted/triggerWanted/warDustEnabled | fixed (RM_Settling.cs defuse/trigger/sweep FailOn; RM_WarDustUses.cs blight FailOn) |
| 24 | wind thresholds can overlap | real | settings sliders RM_WarscarMod.cs:337 calm<=0.8, :341 end>=0.4; kernel has no ordering | fixed (RM_WarscarMod.cs: endWind clamped >= calm+0.05 in UI and on load) |
| 27 | crater index cached forever | real (minor) | RM_Settling.cs:245 craterIdx built once, never invalidated | fixed (RM_Settling.cs: craterIdx reset at each Settling start) |
| 35 | track-grid reflection drift | false (today) | CreatureBehaviors/Source/RM_MapComponent_TrackGrid.cs:51,142,155 match the reflected names/args exactly, single overloads; hypothetical future drift only | none (no current defect) |
| 36 | no-grid fallback drops lift front | false | intentional, documented fallback RM_Settling.cs:320 ("no grid: film alone, wiped at once"); one-shot pass over cells | none (by design) |
| 7 | chotrix lastVictim not saved | real (documented) | RM_Chotrix.cs:40 comment states the trade-off: a reload forgets one fresh kill's drag | none (documented design trade-off; cosmetic drag sign only) |
| 8 | static registries alias into new game | real | RM_Chotrix.cs:35, RM_Totchak.cs:21, RM_OldTongue.cs:25 are static lists pruned only on PostDeSpawn; a discarded game's things never despawn (contrast AerosolScreen.cs:107-122, GlowerShield.cs:27-36 which guard this) | fixed (RM_WarscarMod.cs: new RM_GameComponent_WarscarRegistryReset clears the three registries; engine builds GameComponents in Game.LoadGame ExposeSmallComponents before maps FinalizeLoading spawns things, RimSage-checked) |
| 9 | panel inspect lists other maps' panels | real | RM_OldTongue.cs:81 no `o.parent.Map == parent.Map` check | fixed (RM_OldTongue.cs: same-map check) |
| 12 | long reveal disables hurt-flee | real | RM_Chotrix.cs:77 returns while now<revealUntil; :79 window is 600 ticks; slider RM_WarscarMod.cs:325 allows 15 s = 900 ticks | fixed (RM_Chotrix.cs: hurt/flee check moved ahead of the reveal-window return) |
| 13 | lone-prey checked only at selection | real (minor) | RM_Chotrix.cs:168 IsLone only in FindPrey; vanilla AttackMelee job runs up to 900 ticks (:146) unchecked | file → CHOTRIX_HUNT_TARGET_REVALIDATE_1 |
| 14 | disabled chotrix still flees/silences | real | JobGiver_ChotrixFlee :209 no chotrixEnabled gate; choir reads CompChotrix.All (RM_GeigerChoir.cs:79) | fixed (RM_Chotrix.cs flee giver gated; RM_GeigerChoir.cs Silenced gated) |
| 15 | disabled totchak keeps gnawing once announced | real | RM_Totchak.cs:44-47 disabled check only inside `d.Awake && !announced`; JobDriver_TotchakGnaw :165 no enabled FailOn | fixed (RM_Totchak.cs: disabled+awake sleeps regardless of announce; gnaw job FailOn) |
| 28 | panel reveal chance retries until quota | real | RM_OldTongue.cs:158-160 tests every shuffled cell until `placed == target`; setting comment RM_WarscarMod.cs:43 says "chance each attempt" | file → WARSCAR_TUNING_SEMANTICS_1 |
| 4a | turret refit destroys wreck before blueprint | false | RM_CompTurretAim.cs:118-119 PlaceBlueprintForBuild always spawns a blueprint; RM_OldLineTurret.xml:21-22 is non-rotatable 2x2, same footprint as the vanilla 2x2 ancient turrets, so North is correct | none |
| 4b | ring salvage destroys before resolving def | real (latent) | RM_WarscarRings.cs:140 Destroy precedes :152 GetNamedSilentFail; def exists today (RM_WarscarProjectors.xml:118) | fixed (RM_WarscarRings.cs: def resolved before Destroy) |
| 4c | walk-in destroyed before chassis placement checked | real (low-prob) | RM_Hospice.cs:126-128 p.Destroy() then unchecked TryPlaceThing | fixed (RM_Hospice.cs: chassis placed first; walker destroyed only on success) |
| 4d | cradle resets even if failed-chassis placement fails | real (negligible) | RM_Hospice.cs:320-323; ThingPlaceMode.Near searches a wide radius, and the wreck is a cosmetic remnant | none (negligible; history only lives on a decorative wreck) |
| 5 | null history crashes cradle | real | RM_Hospice.cs:261 derefs history.oddityText with no null check; :361 derefs history.memories.Count (Reveal :294 guards it, inspect does not); Scribe_Defs of a removed def loads null | fixed (RM_Hospice.cs: oddities requires history; inspect null-checks memories) |
| 6 | stage indexes StageLabels unchecked | false | stage is only ever set to 0 (:219/:343) or incremented from 1..4 (:270); case 5 Wakes and Resets to 0 (:268,:338); no reachable value outside 0..5 | none |
| 20 | walk-in targets unreachable cradle | real | RM_Hospice.cs:105-107 nearest by distance only, no CanReach; an unreachable cradle repeats a failing Goto every 250 ticks forever | fixed (RM_Hospice.cs: only reachable cradles chosen; none reachable -> existing kneel-in-place fallback). Ongoing hospice-disabled gating not added (servitor would just wander) |
| 22 | dead-ring wake stale up to 250 ticks | real (negligible) | RM_WarscarRings.cs:74-75 base.CompTickRare runs before wakeCached refresh | fixed (RM_WarscarRings.cs: wake refreshed before base calibration pass; <=250-tick lag after lift-off remains, by design of TickRare) |
| 23 | guaranteed working ring tied to attempt index | real (edge) | RM_WarscarRings.cs:220,237 use loop index n, not placed.Count | fixed (RM_WarscarRings.cs: index = placed.Count) |
| 16 | pool draw not revalidated at completion | real | RM_ReactionPools.cs:467 checks only pool/poolsEnabled; drawWanted, skipBloom and the MinGap in CanDrawNow (:353-362) are not rechecked | fixed (RM_ReactionPools.cs: FailOn !drawWanted; completion re-runs drawWanted + CanDrawNow) |
| 17 | disabled pools still dissolve corpses | real | MapComponent_ReactionPools.MapComponentTick :214-217 never reads poolsEnabled; tooltip RM_WarscarMod.cs:308 presents pools as one feature | fixed (RM_ReactionPools.cs: dissolve tick gated on poolsEnabled) |
| 18 | ring repair does not validate payment | false | RM_WorkGiver_RepairRing.Make (RM_WarscarSalvage.cs) only targets ComponentIndustrial stacks >=2 with job.count=2, and StartCarryThing(B,false,true,true) fails the job if fewer than 2 can be taken; ring is reserved by the job | none |
| 25 | pool cycle shortened by integer division | real (negligible) | RM_ReactionPools.cs:49 QuarterTicks=CycleTicks/4: at most 3 ticks short on a >=10,000-tick cycle | none (imperceptible) |
| 26 | pool cells stale on terrain change | real (minor) | RM_ReactionPools.cs:98-100 cells captured at SpawnSetup only; draw :161 and dissolve :223 never recheck terrain. Overlap half is false: pools are >=24 apart (:282) with radius <=6, scan radius 10 cannot reach a neighbour's cells | fixed (RM_ReactionPools.cs: draw and dissolve skip cells no longer liquor; newly added liquor still needs a respawn/reload) |
| 31 | choir hum names a non-existent def; no live check | real | Defs/ChoirDefs/RM_GeigerChoirDef.xml `<hum>` lists RM_WarscarProjector, which no def carries (RM_WarscarProjectors.xml:33,74,118 are _Dead/_Live/_Salvaged), so rings never hum; RM_GeigerChoir.cs:156-171 picks the nearest source by distance only, so an unpowered/dead screen hums | fixed (RM_GeigerChoirDef.xml hum lists _Live/_Dead/_Salvaged; RM_GeigerChoir.cs hum layer filters on IsScreenLive incl. current source) |
| 32 | cosmetic sound consumes global Rand | false (SP) | RM_GeigerChoir.cs:188,230,238 use Rand, but vanilla sound playback (SubSoundDef volume/pitch randomisation) already consumes Rand camera-dependently; RimWorld has no determinism contract outside the Multiplayer mod | none |
| 33 | jar sound rescans all glower plants per jar | real (perf, bounded) | RM_GeigerChoir.cs:208-220 JarRate re-Resolves defs and walks every glower plant per audible jar every 6 ticks; only jars within 25 cells of the camera (:226) reach it | fixed (RM_GeigerChoir.cs: plant defs cached per Refresh; JarRate counts ~49 neighbourhood cells instead of every plant) |
| 34 | Wasteland bridge loses nesting / ignores grid identity | false | Wasteland/Source/RM_MapComponent_WastelandStorms.cs DoFall (:131) never recurses and writes only its own map.pollutionGrid (:153); no nested or cross-map SetPolluted path exists | none |
| 21 | glower master switch does not reach plates | real | RM_GlowerShielding.xml RM_GlowerPlate carries ungated equippedStatOffsets; tooltip RM_WarscarMod.cs:425-426 promises "Off: both do nothing" | fixed (RM_WarscarMod.cs tooltip corrected to what ships: plates keep resistance when off) |
| 29 | bileworm acceleration stops at rot start | false | RM_BilewormGas.cs:94-97 caps at TicksToRotStart deliberately: Rotting is the state the drink rule (:99, Dissolves >= TicksToRotStart) consumes; pushing past it only skeletonises a corpse the worm would no longer get to drink. Header comment :11 over-states it, behaviour matches the def's promise | none |
| 30 | interval processing credits one period per crossing | unclear | RM_BilewormGas.cs:64 IsHashIntervalTick(250, delta) + :97 fixed 250-tick credit is exact while delta < 250; needs the engine's max CompTickInterval delta for pawns (RimSage) to rule out larger batches | none (harmless at known deltas) |
| 37 | offline settings check is a hand-kept list | real (test gap) | validation.py:28-51 DEFAULTS omits aerosol/ring/glower/rarity/cross-biome fields; :65-69 substring checks prove no reader | file → WARSCAR_VALIDATION_FIDELITY_1 |
| 38 | claimed compile/Harmony verification absent | real (test gap) | validation.py:17-18 docstring claims "patch targets exist"; :70-91 are text greps, no build or signature resolution | file → WARSCAR_VALIDATION_FIDELITY_1 |
| 39 | restore writes default, not prior value | real | validation.py:502-508 restores DEFAULTS[field]; a failed restore only prints to stderr and the suite still passes | file → WARSCAR_VALIDATION_FIDELITY_1 |
| 40 | proof hooks manufacture the tested state | real (test fidelity) | RM_WarscarMark.cs:151-154 sets floor.armed=true by hand ("the proof reads it now"), so the floor's own tick arming is never proven; ChatrakSnap ProofStage :230-267 and LoosenedPanelProof.ProofWork :210 likewise set state directly | file → WARSCAR_VALIDATION_FIDELITY_1 |

Tally (40 claims, #4 counted as 4 sub-claims = 43 rows): real 33 (5 of them negligible or documented, so no action: #4d, #7, #25, plus #22/#26 partially), false 9, unclear 1 (#30). Fixed 23. Items to file: 4 (covering 7 claims).

#### Files changed
- `/home/mandrake/rm/foundry/src/RimMandrake/Scarlands/Source/RM_Settling.cs` (#1, #2, #3, #19, #27)
- `/home/mandrake/rm/foundry/src/RimMandrake/Scarlands/Source/RM_WarscarMod.cs` (#8 registry-reset GameComponent, #21 tooltip, #24 wind gap)
- `/home/mandrake/rm/foundry/src/RimMandrake/Scarlands/Source/RM_Chotrix.cs` (#12, #14)
- `/home/mandrake/rm/foundry/src/RimMandrake/Scarlands/Source/RM_GeigerChoir.cs` (#14, #31, #33)
- `/home/mandrake/rm/foundry/src/RimMandrake/Scarlands/Source/RM_Totchak.cs` (#15)
- `/home/mandrake/rm/foundry/src/RimMandrake/Scarlands/Source/RM_OldTongue.cs` (#9)
- `/home/mandrake/rm/foundry/src/RimMandrake/Scarlands/Source/RM_Hospice.cs` (#4c, #5, #20)
- `/home/mandrake/rm/foundry/src/RimMandrake/Scarlands/Source/RM_WarscarRings.cs` (#4b, #22, #23)
- `/home/mandrake/rm/foundry/src/RimMandrake/Scarlands/Source/RM_ReactionPools.cs` (#16, #17, #26)
- `/home/mandrake/rm/foundry/src/RimMandrake/Scarlands/Source/RM_WarDustUses.cs` (#19)
- `/home/mandrake/rm/foundry/src/RimMandrake/Scarlands/Defs/ChoirDefs/RM_GeigerChoirDef.xml` (#31)
- `/home/mandrake/rm/foundry/src/RimMandrake/Scarlands/Assemblies/RimMandrake.Warscar.dll` + `.dll.srchash` (rebuilt)

No new .cs file (the GameComponent lives in RM_WarscarMod.cs), so the csproj is unchanged. Nothing deployed; nothing marked clean. All fixes are offline-built only, none live-verified.

#### Items to file
| NAME | title | spec |
|---|---|---|
| ORDNANCE_TRIGGER_REAL_SHOT_1 | "Set off from range" should be a real shot, or be renamed | WorkGiver_TriggerOrdnance (RM_Settling.cs, JobOnThing) only checks `gun.def.IsRangedWeapon`; it picks a cell 9-14 cells out with line of sight and JobDriver_TriggerOrdnance calls `Detonate()` (200 Bomb damage) after a 90-tick wait. No verb is fired, no ammo is spent, and the weapon's real range and min-range are ignored (a 6-cell shotgun qualifies). Decide whether to cast the pawn's primary verb at the shell (a projectile hit detonates it via CompExplosive.PostPreApplyDamage) or to call it "remote detonation" with its own eligibility. |
| CHOTRIX_HUNT_TARGET_REVALIDATE_1 | Chotrix hunt does not re-check "lone prey" after choosing | JobGiver_ChotrixHunt.FindPrey (RM_Chotrix.cs) applies IsLone only at selection; the vanilla AttackMelee job (expiryInterval 900, maxNumMeleeAttacks 1) then runs unchecked, so a second pawn joining the prey does not stop the bite, which breaks "never a group of two or more". Needs a periodic check in CompChotrix.CompTick (end the hunt job when `!IsLone(target)`) or a small custom driver. Left unfixed here because ending vanilla jobs from a comp tick risks cancelling defensive melee. |
| WARSCAR_TUNING_SEMANTICS_1 | Panel "reveal chance" slider barely changes anything | GenStep_InscribedPanels (RM_OldTongue.cs:158-160) rolls the chance on every shuffled wall-adjacent cell until `placed == target`, so with dozens of candidates even 10% almost always fills the quota. The setting comment (RM_WarscarMod.cs:43) says "chance each attempt actually places a panel". Making it per-attempt changes how many panels players get (research sets need 2-3 readings, so fewer panels means more map trips): it needs the owner's choice of semantics before the change, not a silent fix. |
| WARSCAR_VALIDATION_FIDELITY_1 | Warscar validation proves less than it claims | (a) validation.py:28-51 DEFAULTS is hand-kept and omits aerosol, ring, glower, rarity and cross-biome settings; :65-69 pass on any quoted substring. (b) The docstring (:17-18) claims "patch targets exist" while :70-91 are text greps. (c) `_restore` (:502-508) writes DEFAULTS rather than the pre-test value, and a failed restore only prints, so the suite still passes. (d) Proof hooks set the state under test themselves, e.g. RM_WarscarMark.cs ProofAccrue sets `floor.armed = true`, and ChatrakSnap ProofStage/LoosenedPanelProof do the same, so the real tick transitions are never observed. Fix: derive the settings list from the C# fields, read and restore the original values in `finally` and fail on a restore error, and let proofs observe a real tick instead of setting state. |

#### Build
`python3 src/RimMandrake/Utils/winbuild.py Scarlands` → `Build succeeded. 0 Warning(s) 0 Error(s)` / `BUILT src/RimMandrake/Scarlands/Assemblies/RimMandrake.Warscar.dll (source b31b7ad696d6+dirty)`.
Selftests: `python3 validation.py` (offline static_checks) → `STATIC: PASS (0 findings)`. Source/SelfTest/ScarlandsFuzz.cs only covers the Verse-free kernels (Source/Kernel/*), none of which changed, so it was not re-run.

## Stillsand

| # | claim (short) | verdict | evidence (file:line, one line) | action |
|---|---|---|---|---|
| 1 | Gale end returns pawns it just took | real | RM_DuneGale.cs ReturnAllFor picked every record with `c.map == map`; header comment says "returned at the NEXT gale's end" | fixed: record carries `takenTick`; `ReturnAllFor(map, ext, startTick)` only returns `takenTick < startTick` (RM_DuneGale.cs) |
| 2 | One throwing Return loses the rest of the batch | real (exception path only) | Kernel/RM_GaleKernel.cs:156 TakeWhere removes all picked records before any Return runs | fixed: each Return wrapped in `SafeReturn` try/catch + Log.Error (RM_DuneGale.cs). The "removed from WorldPawns before map check" half only bites when the map is gone and no home map exists, which is the intended LostMissing outcome |
| 3 | aliveChance is one game-wide field | real | RM_DuneGale.cs CarryOff overwrote component `aliveChance` per abduction; timed returns used the latest | fixed: per-record `aliveChance` (Scribe default -1, falls back to the old component field for legacy records) |
| 4 | Dead abductees never come back (vs setting text "always comes back, alive or not") | real, low | RM_DuneGale.cs Return: `LostDead` letter + return; settings label RM_DuneGale.cs ~1041 promises return | file → GALE_CARRIED_RETURN_HARDENING_1 (needs a corpse made from a dead world pawn; not a few-line fix) |
| 5 | Fallback `AnyPlayerHomeMap` could be a sea-floor map | unclear | Return: `r.map ?? Find.AnyPlayerHomeMap`; only reached when the origin map was destroyed. Whether an RM_SeabedLayer map is a player home needs a live check | none (engine/live question; folded into GALE_CARRIED_RETURN_HARDENING_1 as a note) |
| 6 | ForcefullyKeptPawns not restored after load | false | RimSage WorldPawns.cs:148 scribes `pawnsForcefullyKeptAsWorldPawns`; :257 RemovePawn clears it. Warning-branch record is caught by Return's `Destroyed/Discarded` check | none |
| 7 | Structure-wear MTB unreachable on big maps | real | RM_DuneGale.cs WearStructures: per-sample chance = interval*perCellShare/mtbTicks saturates >1 (250×62500/30/20000 ≈ 26), so a cell's real rate is capped at samples/N per interval (≈208 h vs 8 h stated) | file → GALE_STRUCTURE_WEAR_RATE_1 |
| 8 | Small successive sand moves never erase a track | real (design) | RM_DuneTrackEraser.cs Postfix compares only one SetDepth call's before/after against 0.08; sub-threshold steps accumulate unseen. Whether Odyssey's dune step is ever <0.08 is unmeasured | file → DUNE_TRACK_ERASE_ACCUMULATE_1 |
| 9 | FieldRefAccess runs outside the guarded ctor | real, low | RM_DuneTrackEraser.cs static field initializer ran before the static ctor's try | fixed: MapRef resolved inside the try; Postfix null-guards it (RM_DuneTrackEraser.cs) |
| 10 | rot.disabled may not survive save | false | RimSage CompRottable.cs:81 scribes `disabled`; frozenThings is scribed by reference | none |
| 11 | vanishAfterTimestamp=0 is never restored | real, low | RimSage Corpse.cs:16 default -1, :131 vanish requires `> 0`, so 0 does disable it (sentinel is right) but RM_CavePlace.cs TryFreeze never restores it on release | file → PRECIOUS_CAVE_PRESERVATION_EDGES_1 |
| 12 | Storage straddling the cave freezes outside items | real | RM_CavePlace.cs Scan enumerates the whole slot group; TryFreeze had no InCave check, so release/refreeze churned every 60 ticks | fixed: TryFreeze requires `InCave(comp, t)` (RM_CavePlace.cs) |
| 13 | Saves predating `caveCells` get an empty footprint | real (legacy saves only) | RM_PreciousCaves.cs ExposeData: caveCells defaults to empty; carve hand-off fields are [Unsaved] | none (pre-ship; map state is disposable debug, world remake is the last step) |
| 14 | Diagonal ray steps leave corner-only tunnel links | real | RM_PreciousCaveGeometry.cs RayToOpen rounds x and z independently at 0.5 steps → (x,z)->(x+1,z+1); r<3 caves get no side widening | fixed: diagonal step carves the orthogonal bridge cell (or exits there if it is open) (RM_PreciousCaveGeometry.cs). Widening-uses-shadow-direction sub-claim real but cosmetic, not changed |
| 15 | Re-picking LargestOutcrop after shaping can switch outcrops but keep the old rock | real | RM_PreciousCaves.cs: `rock` computed before ShapeYardang, outcrop re-selected after | fixed: rock recomputed from the re-selected outcrop (+ empty guard) (RM_PreciousCaves.cs) |
| 16 | Multi-cell building placement checks centre only | real | RM_PreciousCaves.cs item element: `ctx.Pick(place, FreeForItem)` on one cell, then GenSpawn (default WipeMode.Vanish clears overlaps) | fixed: footprint `GenAdj.OccupiedRect(...).Cells.All(FreeForItem)` for size>1 (RM_PreciousCaves.cs) |
| 17 | IsNaturalRock queries out of bounds | real | RM_CavePlace.cs WallMark tests `c + d` neighbours; IsNaturalRock called GetEdifice with no InBounds | fixed: null-map/InBounds guard in IsNaturalRock (RM_CavePlace.cs) |
| 18 | Den quest can pick a wandering animal of the kind anywhere on the map | real | RM_EventRemainder.cs TryFindDen: `AllPawnsSpawned.FirstOrDefault(kind && Faction==null)` with no cave-footprint or recorded-occupant test | file → PRECIOUS_CAVE_DEN_OCCUPANT_1 |
| 19 | 30-mound cap is only a precondition | real | RM_IncidentWorker_SandBusterEruption.cs: cap checked in CanFireNowSub only; TryExecuteWorker scheduled points/MoundPoints tunnels unclamped | fixed: count clamped to `MaxMoundsPerMap - mounds - pending tunnels`, refuse at 0 (RM_IncidentWorker_SandBusterEruption.cs) |
| 20 | Leviathan retarget fires every 750 ticks, not 250 | real | Kernel/RM_LeviathanKernel.cs:22,24 Interval 30 vs `now % 250 == 0` → lcm 750 | fixed: `now % 250 < Interval` (Kernel/RM_LeviathanKernel.cs) + fuzz oracle updated to match (SelfTest/Fuzz/StillsandFuzz.cs:234) |
| 21 | Fed leviathan can delete someone else's fresh corpse | real | RM_SandLeviathan.cs TakeTheBody fell back to any corpse <600 ticks old within 6.9 cells | fixed: fallback is now the leviathan's own `mindState.lastAttackedTarget` if dead; radius scan removed (RM_SandLeviathan.cs) |
| 22 | Lost pawn ref re-classifies an arrived visit as a new arrival | real (narrow window) | RM_SandLeviathan.cs Classify was fed `hasPawn = v.pawn != null`; a ref nulled on load (destroyed pawn, `saveDestroyedThings` false) re-spawned a fresh leviathan; null visits unfiltered | fixed: saved `arrived` phase; arrived + null pawn → Drop; PostLoadInit strips null visits (RM_SandLeviathan.cs) |
| 23 | Thumper switched off still draws leviathans | real | RM_SandLeviathan.cs ChargedThumper read only `Charged`; RM_Thumper.cs:110 beat gate reads `thumperEnabled` | fixed: ChargedThumper also requires `RM_SandSwimRemSettings.thumperEnabled` (RM_SandLeviathan.cs) |
| 24 | Swimmer call destination ignores reachability | real | RM_Thumper.cs CellNear picked nearest standable cell; Goto forced with InterruptForced | fixed: candidate must pass `p.CanReach(c, OnCell, Deadly)` (checked only when nearer than current best) (RM_Thumper.cs). "Retain existing call job" sub-claim not changed |
| 25 | Gale clears wet cells but keeps the pour draw point | real | RM_StillsandWater.cs ClearAll cleared `wetUntil` only; `LatestPourCell` reads lastPourCell/drawUntilTick | fixed: ClearAll also resets lastPourCell/drawUntilTick (RM_StillsandWater.cs) |
| 26 | Still discards cycle overshoot | real, deliberate | Kernel/RM_SunKernel.cs:121-122 returns 0 on fire; the fuzz oracle asserts it (SelfTest/Fuzz/StillsandFuzz.cs ~815 "progress not reset after a cycle"); loss < one rare-tick step | none (spec'd quantisation; changing it means changing the fuzz contract — owner/design call) |
| 27 | Still consumes feed before output is known; books ledger on failed output | real, low | RM_SolarStill.cs Consume: feed destroyed first, Notify_Drawn unconditional even if WaterDef null or TryPlaceThing fails | fixed (ledger half): Notify_Drawn only when the water was actually placed (RM_SolarStill.cs). Feed-before-output half left: WaterDef falls back to our own RM_StilledWater, so only a boxed-in still loses feed |
| 28 | Still output water is charged again when drunk | real (design ambiguity) | RM_SolarStill.cs Consume books litres; Defs/ThingDefs_Items/RM_StilledWater.xml:31 gives the output RM_CompWaterVolume (1 L) whose PostIngested (RM_StillsandWater.cs:84-92) books again | file → WATER_LEDGER_DOUBLE_CHARGE_1 |
| 29 | "Witness" thought hits every colonist map-wide | false (as a defect) | Defs/ThoughtDefs/RM_Thought_DeadDistilled.xml:11 label "the dead were wrung for water" is a knowledge thought, same shape as vanilla KnowButcheredHumanlikeCorpse; only the method name says Witness | none |
| 30 | Beam does not save pathCells/hitCells | real, vanilla-parity | RM_Verb_MirrorBeam.cs ExposeData is a verbatim copy of vanilla Verb_ShootBeam.ExposeData (RimSage Verb_ShootBeam.cs:347-357), which saves neither; our BeamDamage kernel already floors the divisor | none (inherited vanilla behaviour; mid-burst save is a one-burst glitch) |
| 31 | Curvature multiplies radians by 57.29578 | false (as a regression) | RimSage Verb_ShootBeam.cs:266 has the identical `MathF.PI * 57.29578f`; our beam (curvature 0.6 Muurrok / 0.3 SunLance) matches vanilla's look | none (keeps vanilla parity; changing it would change every beam's shape) |
| 32 | beamTotalDamage is per unique path cell, not a burst budget | false (as a defect) | RimSage Verb_ShootBeam.cs:323 `beamTotalDamage / pathCells.Count` — same semantics as vanilla | none |
| 33 | Beam visuals LOS lacks InBounds guard | real (also in vanilla) | RM_Verb_MirrorBeam.cs BurstingTick predicate `c => c.CanBeSeenOverFast(map)` (vanilla Verb_ShootBeam.cs:189 same); TryGetHitCell has the guard | fixed: predicate adds `c.InBounds(caster.Map)` (RM_Verb_MirrorBeam.cs) |
| 34 | Pawn and turret beams use different sun policies | real (design divergence) | RM_Verb_MirrorBeam.cs SunFactor: turret → RM_SunPower.FactorAt (shade grid); pawn → celestial glow + roof/weather only | file → MIRROR_BEAM_SUN_POLICY_1 |
| 35 | Zuurrik burial watches only swarm[0] | real | RM_MapComponent_Zuurrik.cs TryBury: `HasWorkNear(swarm[0].Position)` then destroys all | fixed: quiet only when no spawned member has work near it (RM_MapComponent_Zuurrik.cs). Per-member burial not done |
| 36 | Fatness grows from blood-at-wake, not food eaten | real | RM_MapComponent_Zuurrik.cs TryBury: `fatness + Max(1, bloodAtWake/5)`; header line 26 says "fatter by what this one ate" | file → ZUURRIK_GROWTH_BY_FEEDING_1 |
| 37 | Blood scan cap doesn't cap work; O(n^2) cluster | real, low | RM_MapComponent_Zuurrik.cs BloodCellsOnSand used List.Contains (O(n) per add); cluster pass is 600x600 per 600-tick poll only while off cooldown | fixed (dedup): HashSet for seen cells (RM_MapComponent_Zuurrik.cs). Cluster pass left (bounded, 360k int compares per 10 s worst case) |
| 38 | Main settings panel has no scroll view | real (likely) | RM_StillsandMod.cs DoWindowContents: one Listing_Standard over inRect, five feature blocks appended, no scroll/maxOneColumn; actual overflow height needs an in-game look | file → STILLSAND_SETTINGS_SCROLL_1 |
| 39 | Horizon warning moves drop-pod raids to the edge | real | RM_HorizonWarning.cs TryFirePrefix presets `spawnCenter` from TryFindRandomPawnEntryCell for every Raid worker; RimSage PawnsArrivalModeWorker_CenterDrop.TryResolveRaidSpawnCenter only picks a drop centre when `!spawnCenter.IsValid` | file → HORIZON_WARNING_DROP_RAIDS_1 |
| 40 | Thread-static forced entry is not re-entrant | real, low | RM_HorizonWarning.cs TryExecutePrefix/Finalizer unconditionally cleared the context, so a nested TryExecute wiped the outer passer's bearing | fixed: prefix saves previous context in `__state`, finalizer restores it (RM_HorizonWarning.cs) |
| 41 | Horizon patches unguarded at startup | real, low | RM_HorizonWarning.cs static ctor patched three targets with no null check / try | fixed: targets null-checked up front; patches applied in a try with `UnpatchAll(own id)` rollback; TryFire (the deferring patch) now applied last (RM_HorizonWarning.cs). Exact-overload selection not changed (name resolution is unambiguous today — build + startup would show otherwise) |

Trailing "cannot be closed from this bundle" bullets in the review are not defect claims; not judged.

#### Files changed
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Assemblies/RimMandrake.Stillsand.dll`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Assemblies/RimMandrake.Stillsand.dll.srchash`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Source/Kernel/RM_LeviathanKernel.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Source/RM_CavePlace.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Source/RM_DuneGale.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Source/RM_DuneTrackEraser.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Source/RM_HorizonWarning.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Source/RM_IncidentWorker_SandBusterEruption.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Source/RM_MapComponent_Zuurrik.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Source/RM_PreciousCaveGeometry.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Source/RM_PreciousCaves.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Source/RM_SandLeviathan.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Source/RM_SolarStill.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Source/RM_StillsandWater.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Source/RM_Thumper.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Source/RM_Verb_MirrorBeam.cs`
- `/home/mandrake/rm/foundry/src/RimMandrake/Stillsand/Source/SelfTest/Fuzz/StillsandFuzz.cs`

#### Items to file
| NAME | title | spec |
|---|---|---|
| GALE_CARRIED_RETURN_HARDENING_1 | Gale-carried pawns: dead ones should come back as bodies; safe fallback map | RM_DuneGale.cs Return: `LostDead` drops the record with a letter, contradicting the carry setting's "always comes back, alive or not" (RM_DuneGale.cs ~1041). Return a corpse for a world pawn that died while carried. Also `r.map ?? Find.AnyPlayerHomeMap` may pick a sea-floor (RM_SeabedLayer) home, violating ship-only access — restrict to surface maps. |
| GALE_STRUCTURE_WEAR_RATE_1 | Dune gale structure wear runs ~25x slower than its stated MTB | RM_DuneGale.cs WearStructures scales `structureMtbHours / (NumGridCells/samples)`, which saturates the per-sample chance above 1 on any normal map; each cell is effectively capped at samples/N per interval (≈208 h on 250², vs 8 h configured). Roll the hazard per eligible light building (staggered) instead of compensating through sampled cells. |
| DUNE_TRACK_ERASE_ACCUMULATE_1 | Dune track erasure misses gradual sand movement | RM_DuneTrackEraser.cs Postfix compares one SetDepth call's before/after against 0.08; repeated sub-threshold steps never erase. Record depth at print time (RM_MapComponent_TrackGrid) and erase on cumulative displacement. Measure Odyssey's per-call dune step first — if always ≥0.08, drop this. |
| PRECIOUS_CAVE_PRESERVATION_EDGES_1 | Cave preservation leaves animal corpses permanently non-vanishing | RM_CavePlace.cs TryFreeze sets Corpse.vanishAfterTimestamp=0 (RimSage Corpse.cs:131: 0 disables vanish) and release never restores it. Save the original value per frozen corpse and restore on release. |
| PRECIOUS_CAVE_DEN_OCCUPANT_1 | Den quest can target any wild animal of the kind on the map | RM_EventRemainder.cs TryFindDen picks the first spawned unfactioned pawn of the kind map-wide. Save the den occupant reference at cave generation (RM_MapComponent_PreciousCave) or require it be within caveCells. |
| WATER_LEDGER_DOUBLE_CHARGE_1 | Still water is booked to the ledger twice | RM_SolarStill.cs Consume books `litres` on production; its output RM_StilledWater carries RM_CompWaterVolume (Defs/ThingDefs_Items/RM_StilledWater.xml:31) whose PostIngested books again (RM_StillsandWater.cs:84-92). Decide the one charge event (design) and drop the other. |
| MIRROR_BEAM_SUN_POLICY_1 | Pawn mirror beams ignore cast shade; turret beams don't | RM_Verb_MirrorBeam.cs SunFactor: turret routes through RM_SunPower.FactorAt (shade grid, pinned sun); pawn uses celestial glow + roof/weather. Decide whether the muurrok's beam should share the sun-lance policy. |
| ZUURRIK_GROWTH_BY_FEEDING_1 | Zuurrik fatness grows from blood seen at wake, not what it ate | RM_MapComponent_Zuurrik.cs TryBury adds `Max(1, bloodAtWake/5)` even if colonists cleaned all the blood; header (line 26) says growth is "by what this one ate". Accumulate actual filth/corpse consumption and grow by that. |
| STILLSAND_SETTINGS_SCROLL_1 | Stillsand main settings panel needs a scroll view | RM_StillsandMod.cs DoWindowContents appends zuurrik + caves + water + swim + tracks into one non-scrolling Listing_Standard; overflow wraps to an off-screen column. Use the scroll pattern already in the glass-chain/skeleton settings; same check for the gale and event panels. |
| HORIZON_WARNING_DROP_RAIDS_1 | Horizon warning turns centre/drop raids into edge drops | RM_HorizonWarning.cs TryFirePrefix presets `parms.spawnCenter` to an edge entry cell for every IncidentWorker_Raid; CenterDrop honours a preset centre (RimSage PawnsArrivalModeWorker_CenterDrop.TryResolveRaidSpawnCenter). Restrict the warning to walk-in arrivals (resolve/force arrival mode first) or skip drop modes. |

#### Build
- `winbuild.py Stillsand` → `Build succeeded. 0 Warning(s)` / `BUILT src/RimMandrake/Stillsand/Assemblies/RimMandrake.Stillsand.dll` (twice; final after all edits).
- `src/RimMandrake/Utils/selftest_stillsand_fuzz.py` → `stillsand fuzz: 16501 cases ... -> OK` (oracle for ShouldRetarget updated with the fix).
- `src/RimMandrake/Utils/selftest_stillsand_lint.py` → 28/28 ok.
- `src/RimMandrake/Stillsand/selftest_stillsand.py` → healthy PASS 106/106; 66 of 66 breaks red; exit 0.
- Not deployed; not marked code-review clean.

#### Tally
41 claims: real 35 (incl. low/design/vanilla-parity/deliberate), false 5 (#6, #10, #29, #31, #32), unclear 1 (#5); #26 real-but-deliberate, #13 legacy-only. Fixed 22 (#1,2,3,9,12,14,15,16,17,19,20,21,22,23,24,25,27,33,35,37,40,41 — #27/#37 partial). Items to file 10.

## TerminalBiomes

| # | claim (short) | verdict | evidence (file:line, one line) | action |
|---|---|---|---|---|
| 1 | Wax timer resets to full period when overdue while moving | real | Source/Kernel/RM_TerminalMiscKernel.cs:23-26 — expired value goes negative while moving, next call treats <0 as uninitialised | fixed (hold at 0 while moving) |
| 2 | Sun-sphere RecomputeVisual undoes suulk grazing | real | Source/RM_Building_SunSphere.cs:98-113 rewrites GlowRadius from culture every 60 ticks; RM_JobDriver_FeedOnGlow.cs:84 subtracts from same field | file → SUN_SPHERE_GRAZE_PERSIST_1 |
| 3 | Salted doors stay locked with hull-crust mechanic off | real | Source/RM_GreyHullCrust.cs:346 PawnCanOpen postfix never checked RM_GreyCrust.Active | fixed (gate postfix + inspect line on Active) |
| 4 | Current moves a thing that transferred to another map | real | Source/RM_MapComponent_ChannelCurrent.cs ProcessOccupants checked Spawned but not t.Map == map | fixed (drop occupants whose Map differs) |
| 5 | Sink arrival not terminal (re-registration, repeat Sunk) | real | RM_GenStep_TwilightChannels.cs:75 path runs into the sink, so sink cells carry lanes; ScanForOccupants re-registered them | fixed (scan + StepOne skip sink cells) |
| 6 | FreeSinkCell can leave the basin / returns unchecked centre | real | RM_MapComponent_ChannelCurrent.cs FreeSinkCell: radial search lacked IsSinkCell, fallback `return centre` unchecked | fixed (require IsSinkCell; fallback only if standable, else Invalid) |
| 7 | StepOne does not recheck ford/weir exemption | real | RM_MapComponent_ChannelCurrent.cs StepOne read only HasCurrent via kernel | fixed (recheck IsExempt/IsArrestedCell/IsSinkCell before moving) |
| 8 | Current entry can be missed between 250-tick scans; centre escapable | real (design tolerance) | ScanIntervalTicks=250 registration; nothing restricts walking out | file → CHANNEL_CURRENT_CADENCE_FIDELITY_1 |
| 9 | 15-tick processor quantises cadence (22→30, 44→45) | real | StepOne re-registers from processing tick `now`, not `due`; ProcessIntervalTicks=15 | file → CHANNEL_CURRENT_CADENCE_FIDELITY_1 (speed change wants a tuning look) |
| 10 | Surge grab crosses wall, ignores arrest and activation | real | Kernel/RM_ChannelKernel.cs GrabTarget tested only the destination; GrabPawnsOnWidenedBand had no Active/arrest check | fixed (kernel requires standable middle cell; grab gated on ChannelCurrentActive and source arrest; fuzz spec updated) |
| 11 | Channel and bank markers can overlap | real | Kernel/RM_ChannelKernel.cs SetFlow kept Band; SetBankBand banded lane cells (GenStep bank offsets of later path cells hit earlier lanes) | fixed (SetFlow clears Band; SetBankBand skips lane cells; fuzz asserts) |
| 12 | Full-map costs on maps with no channels | real | MapComponentTick allocated grids and scanned every map | fixed (early-out when no sink and no lane cell; cache invalidated in SetFlow) |
| 13 | "Load and launch" neither loads nearby nor launches | real | Source/RM_Thing_CargoFloat.cs:105-126 loads only Position's own cell; header (l.12) promises "within one cell" and a push into current | file → CARGO_FLOAT_LAUNCH_PUSH_1 |
| 14 | Cargo transfer can orphan items; unload reports success with contents held | real | RM_Thing_CargoFloat.cs:117-118 DeSpawn before unchecked TryAdd; :83-85 ignores leftovers | fixed (re-place on failed TryAdd; stay loaded until empty) |
| 15 | GetChildHolders claims leaf but accepts holder cargo | real | RM_Thing_CargoFloat.cs:38-42 empty; :115 accepts any EverHaulable (MinifiedThing, other floats) | fixed (ThingOwnerUtility.AppendThingHoldersFromThings) |
| 16 | Several lamps dispatch the same giant; dispatch latched as answered | real | Source/RM_GreyLampResponse.cs TryAnswer giant query did not exclude a giant already on RM_BreakGlow; Answered latches on dispatch | fixed (exclude giants already breaking a lamp); interrupted-job retry → file → GREY_LAMP_ANSWER_RETRY_1 |
| 17 | Unreachable lamp marked answered permanently | real (deliberate-looking, but latches until burn reset) | RM_GreyLampResponse.cs:206-214 returns true when giant cannot reach | file → GREY_LAMP_ANSWER_RETRY_1 |
| 18 | Disabling both responses leaves stale latches | real | RM_GreyLampResponse.cs:70 cleared Lit only; Kernel/RM_LampWatchKernel.cs prunes latches via Lit.Keys | fixed (clear Lit/Watched/Scraped/Answered + warning latch) |
| 19 | Watcher warning consumed before watcher is ordered | real | RM_GreyLampResponse.cs:120 `first = watched.Add` before cooldown/job/rim checks | fixed (separate Scribed `warnedWatch` latch set only when the order is given) |
| 20 | Burn is sampled every 250 ticks, not tracked | real (minor; 250-tick tolerance) | RM_GreyLampResponse.cs:58-60 Interval=250 sampling | none (4-second tolerance on an hours-long clock; settings wording only) |
| 21 | Settings do not stop running FeedOnGlow/BreakGlow | real | RM_JobDriver_FeedOnGlow.cs MakeNewToils and RM_JobDriver_BreakGlow had no settings FailOn | fixed (FailOn SuulkActive / GreyLampGiantActive) |
| 22 | Lid-dark dimming overwritten by well updates, not persisted | real | Source/RM_MapComponent_WellLedger.cs:314-327 writes GlowRadius once; ApplyVisualState (:226) restores it on every Opening/Waning update; no Scribed dim flag | file → TWILIGHT_WELL_LIGHT_STATE_1 |
| 23 | Gardener cannot advance pending openings when no wells exist | real | Kernel/RM_WellKernel.cs GardenerAdvance `if (Wells.Count == 0) return;` + RM_MapComponent_WellLedger.cs:290 same guard | fixed (both guards removed; fuzz's "empty ledger unchanged" assertion dropped) |
| 24 | Closure warning attempted only once | real | Kernel/RM_WellKernel.cs:129-133 warn() called only on the transition into Waning | fixed (retry each tick through Waning until delivered) |
| 25 | Final waning colour step unreachable | real | Kernel/RM_WellKernel.cs:46-50 into < WaningTicks while remaining>0, so step ≤ 2 (factor ≥ 0.6, colour ≤ 2/3) | file → TWILIGHT_WELL_LIGHT_STATE_1 (needs a ruling on intended steps) |
| 26 | Frozen cadence does not freeze gardener / lid-dark aging | real | RM_MapComponent_WellLedger.cs:138 freezes the ticker only; NotifyGardenerPassAdvance/NotifyLidDarkEnded ignore twilightDriftCadence | file → TWILIGHT_WELL_LIGHT_STATE_1 (behaviour vs wording choice) |
| 27 | Cage crop transport loses plant state; offsets not rotated | real | Source/RM_CompCageCropSnapshot.cs:98-104 keeps def/offset/growth only; :127-129 makes a fresh plant; offsets are world-space | file → CAGE_CROP_SNAPSHOT_FIDELITY_1 |
| 28 | Cryoponics patches affect any plant in the vat | false (by design) | Source/RM_Patch_ChillGrowers.cs:16-18 header scopes temperature to an active vat and terrain-tag relief to either Chill grower; what can be sown is already limited by the grower's sow tags | none (documented intent) |
| 29 | Pane-strike frequency only scales harmless flake litter | real | only consumer is Source/RM_MapComponent_VeilFall.cs:79; RM_IncidentWorker_PaneStrike never reads it | file → TERMINAL_SETTINGS_CONSUMERS_WIRE_1 |
| 30 | Suulk scaling ignores its switch, counts unlit glowers, saturates | real | twilightSuulkPressureScalingEnabled has no reader; RM_IncidentWorker_SuulkArrival.cs:45-46 min(1,…) saturates at 4 glowers; CountPlayerGlowers tests GlowRadius>0, not Glows | file → TERMINAL_SETTINGS_CONSUMERS_WIRE_1 |
| 31 | twilightChainAvailability / twilightChartsAgeEnabled have no consumer | real | grep over src/ and design/: only RM_TerminalBiomesMod.cs declares/draws/Scribes them | file → TERMINAL_SETTINGS_CONSUMERS_WIRE_1 |
| 32 | Cage passability change does not invalidate map caches | real | RM_TerminalBiomesMod.cs:590 + RM_TwilightPassabilityApplier.Apply mutate ThingDef.passability per frame; no pathing/region dirtying for already-spawned cages | file → TERMINAL_SETTINGS_CONSUMERS_WIRE_1 |
| 33 | Mobile-light interval is 4 s, comment says quarter-second | real | Source/RM_CompGlowerMobile.cs:63 IsHashIntervalTick(250) | fixed (60 ticks; comment corrected) |
| 34 | Lure's long-tick proximity check misses passing pawns | real | Source/RM_Comp_VaeuliskLure.cs:67 CompTickLong (2000 ticks) vs 1.9-cell revealRadius | file → VAULISK_LURE_REVEAL_TRIGGER_1 |
| 35 | Hatch exclusion not enforced for basin/weir/stakes | real but moot | RM_GenStep_TwilightChannels.cs:81 RegisterSink and PlaceEddies get no exclusion list; the excluded thing is RM_SeaDiveHatch, a retired leftover (SEA_DIVE_HATCH_RETIRE_1) — the ship flies to RM_SeabedLayer | none (delete with the hatch retirement, not patch) |
| 36 | Crust capped at hull/3, settings promise whole hull | real (wording vs mechanic) | Kernel/RM_CrustKernel.cs:31 CrustCap = hullCells/3; RM_TerminalBiomesMod.cs:482-483 "whole hull by about a quadrum" | file → TERMINAL_SETTINGS_CONSUMERS_WIRE_1 |
| 37 | Scatter guard's static state unsafe under reentrancy | unclear (latent) | RM_Patch_ScatterThingsClusterCenterGuard.cs:67 static int?; TryFindScatterCell is not recursive and mapgen is single-threaded — no nesting caller known | none (needs a real nested caller to matter) |
| 38 | Scatter postfix can overturn another patch's refusal | real (narrow) | RM_Patch_ScatterThingsClusterCenterGuard.cs Postfix checked only result.IsValid before `__result = true` | fixed (treat `!__result` as failure too) |
| 39 | Scald adds a separate protection kind vs "one kind of heat" | unclear (owner judgement) | Defs/DamageDefs/RUT_Scald.xml:42 RM_ScaldArmor; RUT_ScaldExposure.xml:127 RM_ScaldProtection; the ruling (2026-09-29/30) is about temperature heat; scald is a Burn injury and predates it | file → SCALD_HEAT_RULING_QUESTION_1 (BENCH question, not a code fix) |
| 40 | Validation flips restore shipped default, not prior value | real | validation.py:504-518 `_put(t, field, default)` in body and finally; settings_restored (:771) asserts defaults | file → VALIDATION_SETTINGS_SNAPSHOT_1 |
| 41 | Settings round trip never tests Scribe persistence | real | validation.py:504 bridge write/read only, no save/reload | file → VALIDATION_SETTINGS_SNAPSHOT_1 |
| 42 | Offline entry omits sea-catch check; compile-list scan not recursive | real (2 of 4 parts) | validation.py:782 aggregate lacked sea_catch_alive_checks(); :346 listed only top-level Source/*.cs. Kernel tests already run via Utils/selftest_terminalbiomes_fuzz.py; stale-DLL is DLL_SOURCE_STAMP_GUARD_1's .srchash job | fixed (aggregate + recursive scan excluding SelfTest/obj/bin) |
| 43 | catch_checks crashes on missing rare table; `_ok` accepts {} | real (first part) | validation.py:128 `rare[0]` after only recording the defName mismatch | fixed (guard empty table); `_ok` laxity left (tools without a success field would start failing) — none |
| 44 | Two refuelable comps on the sun-sphere may confuse vanilla | unclear | RM_Building_SunSphere.cs seedComp/foodComp; needs a live refuel + save/load round trip | none (live check) |
| 45 | Deep-Scribed struct crop snapshot | unclear | RM_CompCageCropSnapshot.cs:31 `struct PlantSnapshot : IExposable` under LookMode.Deep; ScribeExtractor boxes, so likely fine, but unproven | file → CAGE_CROP_SNAPSHOT_FIDELITY_1 (make it a class while there) |
| 46 | S7-off does not stop existing scald exposure | unclear | Defs/HediffDefs/RUT_ScaldExposure.xml:123-128 comp config carries no settings gate; comp lives in EnvironmentalHazards (out of this mod) | none (read HediffComp_EnvironmentalExposure in EnvironmentalHazards) |

#### Files changed
- `/home/mandrake/rm/foundry/src/RimMandrake/TerminalBiomes/Source/Kernel/RM_TerminalMiscKernel.cs` (1)
- `/home/mandrake/rm/foundry/src/RimMandrake/TerminalBiomes/Source/RM_GreyHullCrust.cs` (3)
- `/home/mandrake/rm/foundry/src/RimMandrake/TerminalBiomes/Source/RM_MapComponent_ChannelCurrent.cs` (4, 5, 6, 7, 10, 12)
- `/home/mandrake/rm/foundry/src/RimMandrake/TerminalBiomes/Source/Kernel/RM_ChannelKernel.cs` (10, 11)
- `/home/mandrake/rm/foundry/src/RimMandrake/TerminalBiomes/Source/RM_Thing_CargoFloat.cs` (14, 15)
- `/home/mandrake/rm/foundry/src/RimMandrake/TerminalBiomes/Source/RM_GreyLampResponse.cs` (16, 18, 19, 21; new Scribed key `warnedWatch`)
- `/home/mandrake/rm/foundry/src/RimMandrake/TerminalBiomes/Source/RM_JobDriver_FeedOnGlow.cs` (21)
- `/home/mandrake/rm/foundry/src/RimMandrake/TerminalBiomes/Source/Kernel/RM_WellKernel.cs` (23, 24)
- `/home/mandrake/rm/foundry/src/RimMandrake/TerminalBiomes/Source/RM_MapComponent_WellLedger.cs` (23)
- `/home/mandrake/rm/foundry/src/RimMandrake/TerminalBiomes/Source/RM_CompGlowerMobile.cs` (33)
- `/home/mandrake/rm/foundry/src/RimMandrake/TerminalBiomes/Source/RM_Patch_ScatterThingsClusterCenterGuard.cs` (38)
- `/home/mandrake/rm/foundry/src/RimMandrake/TerminalBiomes/Source/SelfTest/TerminalBiomesFuzz.cs` (fuzz spec follows 10, 11, 23)
- `/home/mandrake/rm/foundry/src/RimMandrake/TerminalBiomes/validation.py` (42, 43)
- `/home/mandrake/rm/foundry/src/RimMandrake/TerminalBiomes/Assemblies/RimMandrake.TerminalBiomes.dll` + `.dll.srchash` (rebuilt)

#### Items to file
| NAME | title | spec |
|---|---|---|
| SUN_SPHERE_GRAZE_PERSIST_1 | Suulk grazing on a sun-sphere is undone every 60 ticks | RM_Building_SunSphere.cs:98-113 RecomputeVisual sets GlowRadius purely from culture state each 60-tick culture step, while RM_JobDriver_FeedOnGlow.cs:84 subtracts graze loss from the same field. A mature sphere snaps back to 6 and is never fed out unless loss per feed outruns 60 ticks. Store graze damage as its own Scribed field and compose it with the culture radius in one place. |
| CHANNEL_CURRENT_CADENCE_FIDELITY_1 | Channel current runs slower than its kernel says and can be crossed unseen | RM_MapComponent_ChannelCurrent.cs StepOne re-arms from the 15-tick processing tick (`now + cadence`), quantising 22→30 and 44→45 (items no longer half pawn speed). Registration only happens on the 250-tick scan, so a pawn can cross current with no drift, and nothing makes the centre inescapable. Re-arm from `due` (clamped against pauses) and decide whether entry detection should be per-move; speeds visibly change, so take it with a tuning look. |
| CARGO_FLOAT_LAUNCH_PUSH_1 | "Load and launch" does not launch and loads only its own cell | RM_Thing_CargoFloat.cs:105-126 loads haulables from Position only (header l.12 promises within one cell) and never moves the float into current; a float built on the bank stays put. Scan the promised radius, find an adjacent current cell and push it there, rejecting with a message when none exists. |
| GREY_LAMP_ANSWER_RETRY_1 | Grey lamp giant response latches on dispatch, not on completion | RM_GreyLampResponse.cs TryAnswer returns true (kernel latches Answered) when the giant cannot reach the lamp (:206-214) and when a job is merely started (:216); an interrupted RM_BreakGlow never retries until the lamp's burn resets. Distinguish assigned/completed/failed, retry failures with a cooldown. (Same-giant double dispatch already fixed by excluding giants on RM_BreakGlow.) |
| TWILIGHT_WELL_LIGHT_STATE_1 | Twilight wells: dimming not composed or saved, last waning step unreachable, frozen not frozen | SetLidDarkDimming (RM_MapComponent_WellLedger.cs:314) writes GlowRadius once and ApplyVisualState (:226) overwrites it; no Scribed dim flag, new wells open bright. RM_WellKernel.WaningStep (:46) never reaches 3 while the well lives (factor floor 0.6, colour ≤ 2/3). Frozen cadence (:138) does not stop the gardener close or lid-dark aging. Needs a ruling on intended steps and frozen semantics, then one composed visual calculation. |
| CAGE_CROP_SNAPSHOT_FIDELITY_1 | Cage crop transport keeps only def+growth and world-space offsets | RM_CompCageCropSnapshot.cs:98-129 destroys the plants and recreates fresh ones (health/age lost) at world-space offsets that are wrong if the cage is reinstalled rotated; the snapshot is a struct under LookMode.Deep (:31,:50). Make the record a class, store cage-local (rotation-normalised) offsets plus the plant state that matters, and prove with a save made while minified. |
| TERMINAL_SETTINGS_CONSUMERS_WIRE_1 | TerminalBiomes settings that do nothing or say the wrong thing | twilightPaneStrikeFrequency only scales flake litter (RM_MapComponent_VeilFall.cs:79), not the pane-strike incident; twilightSuulkPressureScalingEnabled, twilightChainAvailability, twilightChartsAgeEnabled have no reader; suulk chance saturates at 4 glowers and counts unlit glowers (RM_IncidentWorker_SuulkArrival.cs:45); cage passability flips the def per frame with no map cache invalidation (RM_TerminalBiomesMod.cs:590); crust text says "whole hull" against a hull/3 cap (RM_CrustKernel.cs:31). Wire each control or relabel it honestly. |
| VAULISK_LURE_REVEAL_TRIGGER_1 | Vaulisk lure reveal can miss a passing pawn entirely | RM_Comp_VaeuliskLure.cs:67 checks a 1.9-cell radius only on CompTickLong (2000 ticks), so walking past rarely triggers and a harvest job start is not detected despite the comment. Add a direct harvest/interaction trigger and a cheaper, more frequent proximity check. |
| VALIDATION_SETTINGS_SNAPSHOT_1 | TerminalBiomes live validation resets the owner's settings and never tests Scribe | validation.py:504-518 restores each flipped field to its shipped default rather than its prior value, and settings_restored (:771) asserts that; nothing saves/reloads, so a missing Scribe call passes. Snapshot all fields before the suite and restore in a suite-level finally; add a settings ExposeData round trip. |
| SCALD_HEAT_RULING_QUESTION_1 | Does scald protection conflict with "one kind of heat"? (owner question) | RUT_Scald.xml:42 uses its own RM_ScaldArmor category and RUT_ScaldExposure.xml:127 its own RM_ScaldProtection stat, predating the 2026-09-29/30 heat ruling. Scald is a Burn injury from steam, not temperature, so it may be outside the ruling; ask the owner before changing anything. |

#### Build
- `winbuild.py TerminalBiomes`: `Build succeeded. 0 Warning(s) 0 Error(s)` — `BUILT src/RimMandrake/TerminalBiomes/Assemblies/RimMandrake.TerminalBiomes.dll (source b31b7ad696d6+dirty)`
- `Utils/selftest_terminalbiomes_fuzz.py`: 13950 cases, 4,890,273 steps, 0 failures -> OK
- `TerminalBiomes/validation.py` (offline, now incl. sea_catch_alive): STATIC: PASS (0 findings)
- `TerminalBiomes/selftest_sea_catch_alive.py`: ALL OK
- Not deployed; not marked code-review clean. Saves: new Scribe key `warnedWatch` on RM_MapComponent_GreyLampWatch defaults to empty (old saves load clean).
