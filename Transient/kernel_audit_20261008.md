# Kernel extraction audit - 2026-10-08

Independent auditor (FOUNDRY). Read-only on mods. Scope: the 2026-10-07 kernel extractions.
Method: old call site (`git show <commit>^:path`) vs new kernel + call site; checks for semantics, ordering, numeric type, null/default, tick cadence, Scribe fields, side effects, settings reads, Harmony targets, csproj Compile Include.
Defects the builders already reported and fixed (Transient/validation_<Mod>_20261007.md) are excluded.

Status: DONE. 34 mods across 7 commits audited by 11 parallel read-only auditors; every filed finding re-checked against origin/main source by the lead auditor before filing.

## Summary

Filed (all --for FOUNDRY, kind bug, needs offline; prose under infrastructure/state/items/):
- FLOOD_LEDGER_LOAD_LOSS_1 - FloodedCanyon, 3f5701d45, SAVE-COMPAT: flood ledger lost on load.
- CANYON_FLOOD_ROAR_SILENT_1 - FloodedCanyon, 3f5701d45: flood roar sustainer never started.
- GRIPPER_THEFT_FLOOR_PRECISION_1 - Wasteland, 44de46280: gripper takes one unit fewer.
- CONDENSER_SLOT_SELF_RELATION_1 - WeepingStones, 44de46280: Player.log error on each slot resolve.
- CHANNEL_CADENCE_ROUNDING_DRIFT_1 - TerminalBiomes, d670d2c72 (low): .5 rounding mode changed.

Cross-cutting, not filed: many kernels replace `Rand.Chance(p)` with `p > Rand.Value` style calls that always draw, or reorder draws. Odds unchanged; only same-seed replay differs (Greentide, LeaningScrub, Warcasket, Webwork, Wasteland tipping, Contagion, Abyss, GelatinousSlime). Track only if same-seed reproducibility matters.
No missing csproj Compile Include lines and no Harmony target changes were found in any mod.

## 3f5701d45

### LeaningScrub

Verdict: OK (RNG-order only: lean-fire, walking-stand BFS neighbour order, shed roll; distributions unchanged; not filed).

Auditor notes:

LOW findings only (RNG stream; outcome distributions unchanged):
1. RM_TheLean.cs fire-spread prefix: old :191 Rand.Chance(bias) then tmpDownwind.RandomElement() (Rand.Range int); new :198 always evaluates two Rand.Value args -> extra draw when bias roll fails or bias is 0/1; neighbour order ManualRadialPattern -> NeighbourDx table and pick via (int)(roll*n), so same seed picks a different (uniformly chosen) cell.
2. RM_VenomvineForms.cs Walk: old :888 BFS over GenAdj.AdjacentCells order (N,E,S,W,NE,SE,SW,NW); new RM_FormsKernel.cs:101-107 dx/dz -1..1 loop -> stand member order changes, so Rand.RangeInclusive/Chance draw order and, when walkingMaxCellsPerMap binds mid-stand, WHICH cells get runners differ. Deferred spawn is covered by the kernel's walking set (no duplicate dest).
3. Shed: old :972 Rand.Chance(cellChance) (no draw at 0/1); new :952 + RM_LeanKernel.cs:94 always draws roll(). Only differs at cellChance 0 or 1.
Everything else equivalent: no Scribe lines touched; Harmony patch registration unchanged; RoundRandom draw count/order kept (2 Rand.Value in Rub); guardian Add/Forgive/Reroost, smother pass/claim/yield/stacks, blaze cluster/converge/new-blaze, lash/quench/rear (growth gate already existed old :725), hoard sweep incl. stop-when-full, bloom queue reverse order, scent, alignment all match. csproj 6 Compile lines; SelfTest csproj links 6 kernels.

### Greentide

Verdict: OK (RNG-order only: STELLOCK lace draw now always taken; odds unchanged; not filed).

Auditor notes:

One LOW finding: RM_StellockLace.cs PostDestroy old 3f5701d45^:51-62 drew Rand only via Rand.Chance after felled+Greentide gates (and Rand.Chance skips the draw for p<=0/p>=1); new 3f5701d45:51-54 passes Rand.Value as an argument to DropsBranch, so every non-felled destroy / non-Greentide fell / chance at 0 or 1 now consumes one extra Rand draw. Outcome identical, RNG stream shifted. Everything else equivalent: Scribe keys/defaults of RM_BuriedCache (cell,thingDef,stuffDef,stackCount,buriedTick) and ladder (rut*) unchanged; Catastrophe only caller is Poll which sets done; mire/vurrak/roil/fever/frenzy/thurrock/biome-score identical; DigOut changes are documented fixes; csproj has 5 Compile lines.

### MovingDunes

Verdict: OK

Auditor notes:

OK. 5 non-SelfTest .cs + csproj compared. Rand order (RandomCell x then z, hop RangeInclusive, filth Chance after deposit) preserved; RoundToInt->Math.Round both banker's; CeilToInt same; IsBurialCandidate/TryBuryAt/AbsorbTick/ShouldReveal/StormFactors/WindLock identical; no Scribe changes; csproj has 3 new Compile lines. TransportParamsCache keyed on def ref: fields never mutated at runtime (grep).

### BlueDesert

Verdict: OK

Auditor notes:

OK. Checked all 10 non-SelfTest .cs + csproj (kernels listed, EnableDefaultCompileItems false). PartKills, ChargeStep, Absorb (only new: refuses positive / <1e-6 steps -- builder-reported hardening), Drip, ThawCounts/ThawStack (Clamp equiv), PickWeighted (Max(0) weights, one Rand.Value), Ablation stage (both steps same tick preserved), DepartAction truth table equiv, RoadCell/CropGrowth equiv, Choir InHorDistOf equiv, NearestVirr last-of-equals preserved, Murrek plan nearest-12 stable order + spacing equiv. Only Rand-consumption ordering and extra FindAmbushPrey/spawnable computation (perf/RNG stream only), not findings. No Scribe changes.

### FloodedCanyon

Verdict: **FINDING** FLOOD_LEDGER_LOAD_LOSS_1 (save-compat: ExposeData scribes the three ledger lists through null locals; mid-flood save reloads with an empty ledger) and CANYON_FLOOD_ROAR_SILENT_1 (MaintainRoar has no caller after the extraction; flood roar never plays). Both verified by the auditor against origin/main.

Auditor notes:

FINDING 1 save-compat: RM_MapComponent_CanyonFlood.ExposeData new 519-538 -- lists are fresh null locals per ExposeData pass; LoadingVars reads them into locals then discards; PostLoadInit pass sees null -> ledger cleared and empty. Old 773-781 scribed fields directly. Mid-flood save/load loses activeFloodCells/raisedFillCells/raisedFillPrior: WaterMovingShallow stays forever, excavated fills never restored, aftermath/recut get empty wetted list.
FINDING 2 behaviour: MaintainRoar() (new 341) never called; old 285 called it every Flooding tick. Roar sustainer (beat 5) never plays. Not fixed on origin/main.
Other files OK: PanSleeper (Check equiv incl. initial-seal return; message em-dash->hyphen only), LedgeRefuge (Decide/IsSeeker/NearestReachable equiv; old unstable sort now stable), FossilStrata (FindFaces==IsFace+BFS, scan order z-outer same), BiomeWorker (lazy ChanceSeeded kept), RecedeAftermath (pure constant moves). Kernel Tick ordering of Sweep vs ChooseSeed swapped but Sweep refreshes its own cells. Inactive-recede = builder-reported fix.

## d670d2c72

### LuminousPigment

Verdict: OK

Auditor notes:

OK. Floor grid label rmDeepfireFloorCoats kept, index z*W+x same; LoadingVars adopt + Finalize == old FinalizeInit. LightBook RebuildBlock/anchor/key packing identical; own-vs-cluster routing & floor maxCoats cap = builder-reported fixes. Rules/Cuisine/WornBlend/OtherLightAt/Cost/Mat/God tables equivalent; Rand.Chance/Range order same; weights cache of const baseWeight.

### GelatinousSlime

Verdict: OK

Auditor notes:

OK. No Scribe changes. Slimification tick: rate now computed before EndHostile/Dissolve but SeverityChangePerDay is side-effect free; announce latch identical. Titan kernel (stage/hysteresis/announce/mass/engulf/digest/decay/burst/shed) equivalent; shed guards kept in caller. Dose floor, Pay plan, RollMass zero-weight = builder-reported fixes. ShelfTicks rounding banker's->AwayFromZero (unreachable midpoint). ConversionAttempts always draws Rand.Value (old Rand.Chance skipped draw at p<=0) - RNG stream only.

### TerminalBiomes

Verdict: **FINDING (low)** CHANNEL_CADENCE_ROUNDING_DRIFT_1: Mathf.RoundToInt (half-to-even) became Math.Round AwayFromZero in RM_ChannelKernel.CadenceFor; strength 2.0 centre lane 22 -> 23 ticks.

Auditor notes:

OK. WellLedger Scribe labels/defaults identical (position via property shim, enum moved to namespace - name-serialized, fine); Rand order same; pending-open change = builder-reported fix. ChannelCurrent grids same index (z*W+x), labels same, Adopt at LoadingVars == old PostLoadInit resize. SunSphere/Wax/Veil/Sunk/Crust/LampWatch equivalent (lamp reset now before SendHomeIdleGiants - independent). LOW: CadenceFor Mathf.RoundToInt(banker's) -> Math.Round AwayFromZero; differs only at exact .5, e.g. strength slider exactly 2.0 -> centre 22 vs 23 ticks. LampWatch ThresholdTicks same rounding change (practically unreachable).

## d01f9729a

### ExplosiveGrowth

Verdict: OK

Auditor notes:

OK. MapComponent pass vs RM_EgLedger.Pass line-by-line: same arm/charge/tell/fire order, Rand order (clockFactor before filth; puff Rand.Chance), Scribe labels identical (ledger fields), ChargeTicks/PassDelta/InverseLerp/Hue/VisualScale equivalent, EffectiveTop byte literals match enum (Churn0..None6), SliceRange/InSurgeBand identical, csproj Compile line present. Only change = reported+fixed disabled-top-still-arms defect.

### EmpirePursuit

Verdict: OK

Auditor notes:

OK. Scribe labels/defaults identical via ref st.x; fields->properties, no external reflection on them; FireGate/Begin/Resolve/Probe/Spotter (memo only on gone)/Cordon (nextIonTick set before IonVolley, which doesn't read it)/Strike/Bombardment equivalent; letters after state reset don't read state; Schedule: RandomInRange moved after NextRungDef (no Rand in it) same count; TimerIntervalTick/ShouldWarn/ShouldFire/ShouldEndless identical; TickInterval 2500; LowerRung revive = reported fix; later c76c4119c only adds ion slider.

### KeelHoist

Verdict: OK

Auditor notes:

OK. Checked KeelHoist.cs (sched Tick/ArriveAllNow/PadTo/Soonest, Scribe labels arriveAt/goingUp/fromLabel same), Arrive plan, TryDrop-fail Defer (reported fix; RimSage confirms TryDrop leaves thing in owner on failure), CaptureFor, CradleTakesPawn, reach, DialogHidesPawn, IsLowerableCaptive (args now eager; harmless), OpenLine, chute RollMultiplier Rand order, NextRollAt, CrateSilver floor, HoistFrame KeepersBuying/HolderRefusal/GateOpen, PitBuyer IsFighter/Price (Arena now eager: ChanceSeeded, no global Rand effect)/SilverStacks, csproj line.

### TheSump

Verdict: OK

Auditor notes:

OK. Kethrel Decide probe order identical to old CompTickRare; Wanted args eager but side-effect-free; CoaxMolt BestHandler first-of-equals same; FailChance clamp same; vault Scan/ExtractOne/ScanDue identical, Scribe key sealedThings kept; mere GrowBlob N/E/S/W order == GenAdj.CardinalDirections, OOB skipped before Rand both old/new, Rand draw order same (RangeInclusive then frontier picks); rim set equal. csproj line present.

## 210639c82

### Droidworks

Verdict: OK

Auditor notes:

OK. All 16 changed .cs diffed vs DroidworksKernel.cs. csproj lists kernel; SelfTest links it. Enums moved same namespace/names (save + XML compat). Scribe hunks: none changed. Harmony patch targets unchanged (bodies only). Deliberate fixes (rounding 2.5, NotifyWiped on deformat, OfRace, damage saturate) reported by builder. Detonation scale<=0 early-return differs only at detonationSize=0, unreachable (slider min 0.25). WeightedPick vs RandomElementByWeight: 1 Rand.Value either way.

### Abyss

Verdict: OK

Auditor notes:

OK. 11 changed .cs diffed vs RM_AbyssKernel.cs + RM_AbyssStateKernel.cs. All Scribe labels/defaults preserved (nextRumbleTick, pendingFlashTick, pendingSummCome, average, gustStartTick, gustEndTick, gustCount, cover, coveredTicks, cooldownUntil, nextProbeTick, lastGustCount). csproj + fuzz csproj list both kernels. Cadences unchanged (SampleInterval 10, Interval 250, ScanInterval 60, now%60 grain, CheckInterval). Side effects kept (message, letter, flash, rumble, summ, clatter, sounds). Rand.Range(0.8,1.3)==0.8+0.5*Rand.Value. Radial 2.9 offsets == GenRadial set. Deliberate fixes (stale shrunk entry, exchange overflow) reported. Low/info: ShipCover probe spawn now draws Rand.Range for nextProbeTick BEFORE SpawnProbe (old after) - RNG order only, no behaviour change.

### Miasma

Verdict: OK

Auditor notes:

OK. Checked all 9 callers vs RM_MiasmaKernel.cs: pickers (tie/bound semantics identical), CrecheLedger (null checks kept, Scribe labels/defaults identical), SelfTameStep (Rand order kept, null ledger not barred), BuyerPoll (Rand.Range int overload, same order), DecayObserve, OutputFraction, RotStep (target encoding reset path correct; RotDown does not read rotTicks), StackSplit, FlotsamStep/Want/Pick (Math.Round == Mathf.RoundToInt), BalmScar, BiomeScore (gate order identical). csproj Compile line present.

### TheRot

Verdict: OK

Auditor notes:

OK. Checked 7 callers vs RM_TheRotKernel.cs: GutSweep/OverCap/RotBoost, SwallowState (Scribe labels+defaults identical, Fresh() keeps nextKnockTick=-1), Tick event order, KnockNext/KnockKindFor (null inside -> not scrabbling, same), BeginStranger Rand call unchanged, GutMother burn/tick/accept/rest, Claim (overCap only on first claim, No leaves carrier untouched), PingDue, DropsRuined/RangeFactor, LogReads/EntriesDue/CutLogOnDeath/CampaignTileIndex, Unjoin Sort/PurgeTicks/ScarSeverity, BiomeScore. Only diff: FinishDigestion now also zeroes damageSinceSwallow via Clear (benign: only read while Holding; Begin resets it). RotBoost adds 0f instead of continue (no-op). csproj Compile line present.

## 44de46280

### Wasteland

Verdict: **FINDING** GRIPPER_THEFT_FLOOR_PRECISION_1: byMass floor moved float -> double in RM_DoseKernel.cs:36; 3/0.6f floors to 4 instead of 5 (verified numerically).

Auditor notes:

FINDING GRIPPER_THEFT_FLOOR_PRECISION_1 (behaviour, low-med): RM_GripperTheft.cs old :248 Mathf.FloorToInt(maxCarryMass/unitMass) float quotient; new Kernel/RM_DoseKernel.cs:36 floors (double)maxCarryMass/unitMass. With maxCarryMass=3 (RM_Gripper.xml:88): unit mass 0.6 (component) old 5 new 4; 0.3 old 10 new 9; 0.1 old 30 new 29. Gripper steals one unit fewer whenever quotient is an exact float integer.
low: RM_TippingKernel.Discovers evaluates roll() (Rand.Value) before Chance short-circuit -> consumes Rand when chance<=0 or >=1 (old Rand.Chance did not). RNG stream only.
Checked: dose, processor fullness, storms layer gating, named-storm phase machine (End/Begin/Unleash/Disabled order equal), tipping (TryDeliver guard = builder-reported fix), cask/bay, CheckShip; no Scribe changes; csproj has 4 kernels.

### WeepingStones

Verdict: **FINDING** CONDENSER_SLOT_SELF_RELATION_1: Resolve() reads PlayerGoodwill/HostileTo on the player faction itself; red 'relation with itself' error every resolve; choice unchanged.

Auditor notes:

FINDING CONDENSER_SLOT_SELF_RELATION_1 (behaviour, low-med): RM_CondenserQuests.cs new :35-43 builds FactionInfo for EVERY faction incl. the player, reading f.PlayerGoodwill -> GoodwillWith(OfPlayer) -> RelationWith(self) -> Log.Error 'Tried to get relation between faction X and itself' (Faction.cs:487-493). Old :31-36 Usable() rejected IsPlayer before any goodwill read. Result unchanged, but every Resolve() now writes a red error to Player.log.
Not findings: pool decisions draw Rand before the starve Kill (old drew emerge after Kill) -> RNG order only; OffersOpen/QuestPartTick now always run ClaimStillHeld (releases stale claim) - harmless. Drying rewrite, dryStartCount Scribe (default -1, adopts), no-grow-while-drying, arrival-keeps-drying, rival withdraw on accept = builder-reported.
Checked: PoolStock Decide/ClassifyState/enum move (same namespace), PoolBody feed clock, walking condenser phase machine/letters order, ancient condenser plant accumulator, claim/slot kernel; ExposeData labels unchanged except the added dryStartCount; csproj has 3 kernels.

### Contagion

Verdict: OK

Auditor notes:

OK. Checked sky clock (Tick flags, tells, StartBurn, RollGap), Coalescence gate (burnEnabled = builder-reported change), burn Pressure/Classify/TryDive (first-4 sheltered preserved), repulsor warm-up, StretchBurn (setter no-op when equal; canBePermanent false), Coalescence building stage/emit/samples, amoeba plan/batch, draftprint ExtremeStat/WorstLimb/Matches (limbs never null)/Reward/FeatureCount, Unfinished spawner. Only RNG-order shift (RollGap before MTB). No Scribe changes. csproj + SelfTest csproj link all 3 kernels; EnableDefaultCompileItems=false in all three mods.

### FeverWood

Verdict: OK

Auditor notes:

OK. Checked BroodRansom, CompCapturedSpecimen, FoulPool, TentacleWatch vs 3 kernels. Pressure +2 forced path same (SpawnEncounterAt +1). Scribe labels unchanged; RepairQueues same result. FoulPool toggle-off and PickLimb changes are builder-reported fixes. csproj has 3 Compile lines.

### TheForge

Verdict: OK (one low, unfiled): RM_DhokkurKernel.Shove returns Damaged for pct>0 even when MaxHitPoints is 0 (old returned false on dmg<=0); needs a destroyable 0-HP edifice on a trail cell, reachability unproven, so recorded not filed.

Auditor notes:

OK except LOW: Shove() old RM_ForgeDhokkurWays.cs (44de46280^) returned false when MaxHitPoints*pct<=0; new returns Damaged/true when pct>0 even if MaxHitPoints==0 (closure skips damage) -> StatShoves++, dust, 'has shoved' message with nothing done. Reachability unsure (destroyable building w/ 0 MaxHP). Scribe keys dhokkurWear/dhokkurLastWorn kept (public fields). Cycle/crust/melt/dormancy/voices/plume/sky identical.

### Cauldron

Verdict: OK

Auditor notes:

OK. Vents (weather rows now shortHash-matched: unique per def type, equivalent), Vexxiss drink/ward/igniter/fire, MetalYield, BloomExposure, Dewfall, CondensateGardens, Prints ledger (key rmVexxissPrints kept via ref ledger.Entries). Approximately restated exactly. csproj 3 lines; SelfTest links kernels.

## df37296d5

### Oracle

Verdict: OK

Auditor notes:

OK. Checked OracleClient RunWithRetry/RunOnce/Candidates/Classify/Invoke pin, GameComponent Admit order, Resolve/Deliver, queue drain; csproj default glob + SelfTest exclude. Only diffs: reported timeout saturation + candidate dedupe; SafeDefault path logs one combined line instead of two (log-only).

### Pyrelands

Verdict: OK

Auditor notes:

OK. All 11 changed Source files vs 4 kernels: furnace charge/rest/bed cells/size ratio/herd legs+BFS, enum FurnaceHerdLeg moved same namespace+assembly (Scribe by name, safe), burn-line measure cadence/centroid/history/arson/keep-alive/lawful cell, fire clock (FrontTick schedule order, Rand.Range==min+Value*span with 2<4), breaker section BFS/battery partition/blast, fire-eco biome score/fulgurite/fire-tick gate/ash rate. No Scribe/Harmony/tick changes; csproj has 4 Compile lines. Behaviour changes all reported: master-off fireFront.Tick, zero ash rate -> 0 attempts, FrontLine geometry (diagonal fronts wider).

### PyrelandsMechanics

Verdict: OK

Auditor notes:

OK. FireRaid CanFire/TryExecute (plan, insult, points incl. DefaultThreatPointsNow only when <=0), FlameHarvest gate, rite roll (one Rand.Value), party range, harvest ticks rounding, rite retry. Slider max 2000->ArsonDebtCap + EffectiveRaidThreshold = reported fix.

### RimProperty

Verdict: OK

Auditor notes:

OK. Checked all 17 call-site diffs vs RM_PropertyKernel: rounding (Math.Round == Mathf.RoundToInt banker's), Lerp clamp, comparator, IsAuthorized/IsKept/IsGhost, SpineWrite+AuthorizedAfter order, perception gate moved out of RollPerception (single caller), Rand draw count in TheftRollPasses, Dampen, recognizability (Legendary=6), csproj + net472 selftest Compile lines. Only change is reported TryPaySilver click-time recheck (fix).

### SolarMirrors

Verdict: OK

Auditor notes:

OK. Checked CompMirror.Reflectivity, MirrorMath facade, MirrorLight Pass/Fire/relay/hash/SpotCells/FirstBlocker/BlindGain vs kernel; csproj Compile lines present. Low note: FirstBlocker returns null (clear) without walking when mirror not in mirrorList (old always walked) - preview only, registered on spawn.

### Stillsand

Verdict: OK

Auditor notes:

OK. Checked DuneGale (bearing, wind index, carry walk+filth order, exit/return edge, WalkIn, Decide, carried-book scans, emergence filter), SandLeviathan (classify, rumble, dive machine, hunt gates, WaterScore, BeatsBest), SolarStill, SunPowered.FactorAt/Intensity, Thumper SelectCalls, MirrorBeam sun/damage, WaterLedger book (Scribe keys identical, AffectGoodwill(0) is a no-op). Notes: gale `carried` diag counter no longer counts zero-move carries (log line only, deliberate); Arrive-fail now posts a Message (deliberate fix); Emerge filter now eagerly evaluates FindRockFace (no Rand; perf only); StartDive reason string casing changed but unused.

### Warcasket

Verdict: OK

Auditor notes:

OK. Checked CaskBay (shielding, IsShielded, CoreDose cadence/falloff), Integrity (hazard count, FailureChance, damage, severity), Immersion (CheckDue cadence, delta incl Dead gating, HazardousCell), Sarcophagus (seal, crack option, CrackTicks, salvage). Low: Rand.Chance(chance)->Chance(chance, Rand.Value) always draws Rand.Value even when chance is 0/1 (RNG stream only). NextSalvageStack Max(1,..) deliberate.

### Webwork

Verdict: OK

Auditor notes:

OK. Checked BiomeWorker score, EggClutchRelay plan (nearby check hoisted from TryRelay, sole caller; Spawned guard prevents null map), Emergent gate, GenStep nest tests, Urraveth (Adjacent, load/heavy, Step creak machine incl effects order, Examine, weave, chapters, outline, collapse damage RoundRandom, RollSite, SiteInMargin), StartupGate ScaledInterval. Deliberate: hind-leg LimbPile layout z1->z2 (builder report validation_Webwork_20261007.md:12). Low: Emergent Fires/RollSite now draw Rand.Value eagerly even when disabled/non-Vanish/chance 0 or 1 (RNG stream only).

### Armoury

Verdict: OK

Auditor notes:

OK. Ion workers x3 (stun parity incl. Ionization override->StunsVictim; no other OnAppliedTo overrides in src), yield (drop/pick reported fixes; Rand.Value count unchanged, pick mapping reversed but same distribution), credits miner, kolto (enum 0/1/2 matches, ticksBetweenHealing not scribed, init 2500), WillHeal, blocker precedence, mine defuse, cooldown, settings, TCED pre/postfix, jumppack (lost godMode-only DebugPoint 'no jump verb' - debug only). Compile line added.

### SWBestiary

Verdict: OK

Auditor notes:

OK. FuelSpew cone (SignedAngle(v,right,up)==atan2(dz,dx); DeltaAngle==Mathf), innate ability steps, EatMetal chew (HP min-1 reported fix), priority/hungry/dig, hoard Eligible/NearestNest/validator/Takeable order, GetFood prefix (signature+attribute unchanged), toxin need/stage, ikee (tolerantXenotypes initialised, radius compare), kiln Register/Cool (ledger clear+cooldown moved before Fire; Fire reads only spaced), moornak (NextUnsettled = reported fix). No Scribe/tick/Harmony target lines changed. Kernel Compile lines in BeastMechanics+Livestock csprojs; JawaIkee EnableDefaultCompileItems=true; SelfTest links all 3.

### JawaRules

Verdict: OK

Auditor notes:

OK. IsJawa, sow postfix (lazy IsJawa), relations tracker, pet name gates, redress kind/xenotype, world-label Current; swim-hood postfix (early return/finally/reentry unchanged, exception path leaves __result), fallback worker (eager base, log+fail-open preserved via rethrow), RealHoodIsDrawing (EffectiveParms == EffectiveFlags). csproj Compile added.

### JawaIonWeapons

Verdict: OK

Auditor notes:

OK. DamageWorker_IonBuildup flesh gates/severity, machine tier, shield break; settings BodySizeDivisor (Mathf.Pow==(float)Math.Pow); StatPart; VehicleIonPatches (RoundToInt==Math.Round, ReadFloatField now read earlier but pure). csproj x3 + SelfTest include kernel; VehicleTier Remove precedes Include. Only theoretical: MachineAmount NaN->0 (old NaN passed) unreachable.

## a33f7ffaf

### ShipVermin

Verdict: OK (note: settings keys spawnMynock/Scavrat/WompRat/Fuelmite replaced by the new species keys in a33f7ffaf; the species themselves changed by design, so a prior off-toggle does not carry over; not filed).

Auditor notes:

OK on mechanics: RSW_Mynock breeder/pressure/seek/gnaw block moved byte-for-byte (numbers identical) into SWBestiary Patches/ShipVermin/RSW_ShipVermin_CanonCast.xml under FindMod "RimMandrake: Ship Vermin" (matches About name; no LoadFolders.xml in SWBestiary so subfolder loads). All speciesWeights users (RUT_FallWrecks.xml) name RSW_ kinds, which RosterAllows still gates via Resolve(slot) swap. Alert: label/text only. CompProperties: comment only. csproj lists 3 new .cs.
LOW settings: ExposeData old spawnMynock/spawnScavrat/spawnWompRat/spawnFuelmite keys replaced by spawnSkivvik/... -- a player's prior OFF choice silently resets to ON (no error). Donor-name fallbacks (Mynock/Scavrat/WompRat/VFEI2_Fuelmite) dropped -- intentional per item.
