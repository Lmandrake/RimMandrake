# Lantern Deeps proposal tickets

Design only; none has been executed or filed into shared state. Tuning/test repairs are builder work, never extra passing bars. For switch-off tests, “absent” concerns the extra contribution, not retained ordinary animals, definition metadata, or unrelated vanilla jobs. All default tests include every kept mechanic. Next-version experimental switches remain visibly labelled and off until separately validated.

## T1: Switch off Drifter/galuush hot-kill ignition and forced roof fall

Call search: Wave1 XML deathAction -> RM_DeathActionWorker_HotKill; RM_HotKillCompInjector -> RM_CompKillingBlow; RM_HydrocarbonProof.ProofDrifterKill. Gate hot-kill death action and its injector as well as galuush forced roof marks; do not gate mobile glowers, products or ordinary corpse generation. Existing hydrocarbonIgnitionEnabled and galuushRoofFallEnabled default off.

Acceptance test: On a fresh disposable Deep with shipped defaults, state-read no extra-created things, special jobs, hediffs, letters, incidents or modifier writes attributable to this path; ordinary retained animal bodies are allowed. Exercise its natural trigger and advance real ticks; log stays clean. In an otherwise identical fixture enable only this next-version switch and its documented prerequisites: the named effect appears. Disable and reload: no lingering owned effect. Record exact effect identities, not a blanket animal count. Read explosion events and forced-collapse marks after hot/cold kills: no hot-kill explosion or forced mark at defaults; an enabled qualified hot kill produces the existing explosion, with forced roof behaviour tested only when its own experimental switch is enabled.

## T2: Switch off Shared wounds and nearby-kin healing

Call search: Wave1 XML -> CreatureBehaviors.RM_CompWoundLink / RM_HediffComp_KinMending. Add a next-version gate at the LanternDeeps def wiring for wound links and KinMending; do not change the shared CreatureBehaviors engine. Restore neither wounds nor healing when off.

Acceptance test: On a fresh disposable Deep with shipped defaults, state-read no extra-created things, special jobs, hediffs, letters, incidents or modifier writes attributable to this path; ordinary retained animal bodies are allowed. Exercise its natural trigger and advance real ticks; log stays clean. In an otherwise identical fixture enable only this next-version switch and its documented prerequisites: the named effect appears. Disable and reload: no lingering owned effect. Record exact effect identities, not a blanket animal count. Damage an isolated and a neighbouring Shoal: no linked injury transfer or KinMending effect at defaults; enabled wiring propagates the existing shared injury/healing effect. Body/product/diet data remain the same.

## T3: Switch off Accretive crust stalking and engulfing

Call search: RM_LanternDeepGenerator -> RM_DeepCreep.Generate; RM_MapComponent_Creep.MapComponentTick; crust/engulf defs and proof hooks. Default creepEnabled off; gate seed, growth, engulf and stalking letters. Kept minds, formations and Cleavers must not call Creep to function.

Acceptance test: On a fresh disposable Deep with shipped defaults, state-read no extra-created things, special jobs, hediffs, letters, incidents or modifier writes attributable to this path; ordinary retained animal bodies are allowed. Exercise its natural trigger and advance real ticks; log stays clean. In an otherwise identical fixture enable only this next-version switch and its documented prerequisites: the named effect appears. Disable and reload: no lingering owned effect. Record exact effect identities, not a blanket animal count. Read Creep crust instances, engulf hediffs and stalking letters after sleepers wait on suitable native floor: absent at defaults; seeded growth and engulf occur through real hourly ticks when enabled.

## T4: Switch off Aurora glow, Chorus and quicker Cleavers

Call search: RM_LanternDeepGenerator customMapComponents -> RM_MapComponent_DeepAurora; RM_GameCondition_DeepAurora -> Apply -> LightLedger and Cleaver quickening; RM_CompTapper reads aurora condition. Default auroraEnabled off; condition initiation AND active condition effects/cleanup must honor the gate. Keep collapse code, despite sharing RM_AuroraCollapse.cs. No Chorus boost, light multiplier or quickening at defaults; isolate tapper reads.

Acceptance test: On a fresh disposable Deep with shipped defaults, state-read no extra-created things, special jobs, hediffs, letters, incidents or modifier writes attributable to this path; ordinary retained animal bodies are allowed. Exercise its natural trigger and advance real ticks; log stays clean. In an otherwise identical fixture enable only this next-version switch and its documented prerequisites: the named effect appears. Disable and reload: no lingering owned effect. Record exact effect identities, not a blanket animal count. Read active DeepAurora conditions, ld.aurora LightLedger shares, quickening hediffs and Chorus sustainer: no contribution at defaults; enabled natural/parent trigger supplies those effects and disabling removes its shares without altering collapse state.

## T5: Switch off Roof sensing, drumming, flight from danger and tame warning benefit

Call search: Wave2 XML comp tick; RM_MapComponent_DeepCollapse.Filter calls TameKnockerOn. Default knockerAlarmEnabled off; decouple kept collapse window calculation from the tame-knocker presence path so its default is the base warning. Plain knocker spawn stays.

Acceptance test: On a fresh disposable Deep with shipped defaults, state-read no extra-created things, special jobs, hediffs, letters, incidents or modifier writes attributable to this path; ordinary retained animal bodies are allowed. Exercise its natural trigger and advance real ticks; log stays clean. In an otherwise identical fixture enable only this next-version switch and its documented prerequisites: the named effect appears. Disable and reload: no lingering owned effect. Record exact effect identities, not a blanket animal count. At a real pending unsupported roof, default knocker produces no special drum/mark/message or warning extension; with alarm enabled its hearing response appears and tame factor extends only the experimental warning. Base roof warnings work in both forks.

## T6: Switch off Fuel trail on movement

Call search: Wave2 XML -> RM_CompTrailFilth.CompTick. Default slickTrailEnabled off; preserve ordinary injury blood. Test an uninjured moving animal so fuel blood cannot masquerade as the trail.

Acceptance test: On a fresh disposable Deep with shipped defaults, state-read no extra-created things, special jobs, hediffs, letters, incidents or modifier writes attributable to this path; ordinary retained animal bodies are allowed. Exercise its natural trigger and advance real ticks; log stays clean. In an otherwise identical fixture enable only this next-version switch and its documented prerequisites: the named effect appears. Disable and reload: no lingering owned effect. Record exact effect identities, not a blanket animal count. Track an uninjured walking Slick: no path-added Filth_Fuel at defaults; experimental trail produces path fuel when enabled. Injury fuel is separately attributed in both forks.

## T7: Switch off Hush invisibility and special lunge only

Call search: RM_LanternDeepGenerator -> RM_DeepHush -> RM_GenStep_Hush; Wave3 XML -> RM_CompHush. Separate placement from hushHidingEnabled: keep admitted visible Hush placements, but gate invisibility, natural-floor lunge and hide/strike state under a next-version switch. Disabled animals stay visible.

Acceptance test: On a fresh disposable Deep with shipped defaults, state-read no extra-created things, special jobs, hediffs, letters, incidents or modifier writes attributable to this path; ordinary retained animal bodies are allowed. Exercise its natural trigger and advance real ticks; log stays clean. In an otherwise identical fixture enable only this next-version switch and its documented prerequisites: the named effect appears. Disable and reload: no lingering owned effect. Record exact effect identities, not a blanket animal count. Read visibility/targetability, invisibility hediff and special lunge job while a victim approaches on native unlit floor: visible placed animal and no special lunge at defaults; enabled special state hides/strikes as implemented.

## T8: Switch off Sipper light seeking, drain and bespoke vermin pressure

Call search: Wave3 XML -> RM_CompSipper and CreatureBehaviors breeder; global RM_MapComponent_Sippers.Pass -> LightLedger. Default sipperDrinkingEnabled off, gate both local seeker and global radius writer, and separately gate its XML breeder/pressure wiring. Clear only its LightLedger owner share; retain ordinary reproduction settings, where vanilla supplies them.

Acceptance test: On a fresh disposable Deep with shipped defaults, state-read no extra-created things, special jobs, hediffs, letters, incidents or modifier writes attributable to this path; ordinary retained animal bodies are allowed. Exercise its natural trigger and advance real ticks; log stays clean. In an otherwise identical fixture enable only this next-version switch and its documented prerequisites: the named effect appears. Disable and reload: no lingering owned effect. Record exact effect identities, not a blanket animal count. Read ld.sipper LightLedger ownership, seeker jobs and special breeder events: no contribution at defaults, with ordinary animals still present; enabled Sipper path seeks/drains a suitable lamp and its separately declared breeder switch exercises pressure without requiring a storm.

## T9: Switch off Wild battery drain and tame aurora charge

Call search: Wave3 XML -> RM_CompTapper.Tick -> aurora / battery. Default tapperEnabled off for seeking, drain, charging AND deposit. Keep the animal; aurora off must not be a prerequisite for absence of battery work.

Acceptance test: On a fresh disposable Deep with shipped defaults, state-read no extra-created things, special jobs, hediffs, letters, incidents or modifier writes attributable to this path; ordinary retained animal bodies are allowed. Exercise its natural trigger and advance real ticks; log stays clean. In an otherwise identical fixture enable only this next-version switch and its documented prerequisites: the named effect appears. Disable and reload: no lingering owned effect. Record exact effect identities, not a blanket animal count. Read battery stored energy and tapper charge/targets over ordinary intervals: no special drain, storage or deposit at defaults; enabled wild/tame forks exhibit their configured energy transaction, with aurora explicitly enabled only for the experimental charging branch.

## T10: Switch off Warmth seeking, smothering, chilling and tame firefighting

Call search: Wave3 XML -> RM_CompPooler.Tick/Release; Patch_BuildingHeater_TickRare -> suppression ledger. Default poolerSmotherEnabled off for warm-body chill, extinguishing, immunity branch, fuel burn-down and heater suppression. Gate unconditional fire-removal branches too. Release only suppression this animal owns and respect overlapping owners and pre-existing off state.

Acceptance test: On a fresh disposable Deep with shipped defaults, state-read no extra-created things, special jobs, hediffs, letters, incidents or modifier writes attributable to this path; ordinary retained animal bodies are allowed. Exercise its natural trigger and advance real ticks; log stays clean. In an otherwise identical fixture enable only this next-version switch and its documented prerequisites: the named effect appears. Disable and reload: no lingering owned effect. Record exact effect identities, not a blanket animal count. Read heater enabled/prior state, fuel, fires and target pawn temperature hediffs: no smother/chill/extinguish contribution at defaults; enabled warm-target forks exercise those effects, and overlapping owners cannot restore a heater another owner or the player has disabled.

## T11: Switch off Scanner echoes and hidden-void payload

Call search: PatchOperationFindMod -> Acoustic Scanner payload consumers. Gate the extension payload, including Creep references and hidden-void echoes, behind a next-version setting. Keep owned portal labels and ordinary inspection readable without a scanner.

Acceptance test: On a fresh disposable Deep with shipped defaults, state-read no extra-created things, special jobs, hediffs, letters, incidents or modifier writes attributable to this path; ordinary retained animal bodies are allowed. Exercise its natural trigger and advance real ticks; log stays clean. In an otherwise identical fixture enable only this next-version switch and its documented prerequisites: the named effect appears. Disable and reload: no lingering owned effect. Record exact effect identities, not a blanket animal count. Read scanner payload contributions rather than expecting scanner absence: no Deep-specific mind/chassis/Creep/void echo annotation at defaults; enabled integration supplies its payload without activating Creep itself.

## T12: Switch off Optional Pyrinth scatter and exclusivity patch

Call search: RM_LanternDeepGenerator -> RM_LanternDeepPyrinthScatter; Patches/RM_LanternDeepGatePyrinth.xml changes external commonality. Add next-version gate to both scatter and global commonality/exclusivity patch. Disabled makes no Pyrinth placement or off-biome policy change; leave Minerals policy untouched.

Acceptance test: On a fresh disposable Deep with shipped defaults, state-read no extra-created things, special jobs, hediffs, letters, incidents or modifier writes attributable to this path; ordinary retained animal bodies are allowed. Exercise its natural trigger and advance real ticks; log stays clean. In an otherwise identical fixture enable only this next-version switch and its documented prerequisites: the named effect appears. Disable and reload: no lingering owned effect. Record exact effect identities, not a blanket animal count. Read Deep scatter contributions and off-biome commonality before/after load: no Pyrinth placement or exclusivity mutation at defaults; enabled integration contributes the located scatter/policy. Ordinary native mineral placement is present in both forks.

## T13: Quarantine and verify Campaign mindstone gallery and mineable source

Locate the companion implementation against the historical inventory before changing it. Add a distinct campaign next-version gate and suppress only this Deep integration, not unrelated campaigns. Free generator and signature may not require it. Companion code is unknown in this checkout.

Acceptance test: With companion installed, default fresh Deep contains no campaign integration additions/jobs/recipes/letters from this path and has a clean log; on, the located contribution resolves and is usable. Without companion, free Deep still works. Until companion source is supplied this test is specified but unrun, not evidence of absence.

## T14: Quarantine and verify Campaign matrix and head recipes

Locate the companion implementation against the historical inventory before changing it. Add a distinct campaign next-version gate and suppress only this Deep integration, not unrelated campaigns. Free generator and signature may not require it. Companion code is unknown in this checkout.

Acceptance test: With companion installed, default fresh Deep contains no campaign integration additions/jobs/recipes/letters from this path and has a clean log; on, the located contribution resolves and is usable. Without companion, free Deep still works. Until companion source is supplied this test is specified but unrun, not evidence of absence.

## T15: Quarantine and verify Campaign kyber and KotOR/stygium integration

Locate the companion implementation against the historical inventory before changing it. Add a distinct campaign next-version gate and suppress only this Deep integration, not unrelated campaigns. Free generator and signature may not require it. Companion code is unknown in this checkout.

Acceptance test: With companion installed, default fresh Deep contains no campaign integration additions/jobs/recipes/letters from this path and has a clean log; on, the located contribution resolves and is usable. Without companion, free Deep still works. Until companion source is supplied this test is specified but unrun, not evidence of absence.

## T16: Switch off Guarded historical Caverns compatibility

Source call search: Patches/RM_LanternDeepEvictCrystalFauna.xml and RM_LanternstoneFictionRename.xml target optional donor definitions and are not required by the owned cave. Recommend owner retirement because obsolete compatibility duplicates retired ownership and donor eviction fights the stopped-evictions ruling. Pending that decision retain code/defs, gate defaults off, and make any experimental enabling of roster-removal code refuse with a readable explanation under the existing ruling. A read-only preview may report its would-be targets; no active roster change is authorized.

Acceptance test: Default fresh composed load has no donor rename or roster mutation from these patches, unchanged actual admission state and a clean log. With experimental compatibility on, a read-only preview identifies legacy targets, permissible fiction-only compatibility may activate, and attempted eviction remains inert with an explicit stopped-evictions notice. Acceptance test for actually enabling eviction: none, the standing stopped-evictions ruling prohibits that action; this proposal does not change it.

## T17: Specify next-version passage giant

Do not choose by body size alone. Before later implementation, select a lore-compatible existing or new candidate through the existing roster sitting; document water-ness, actual passage footprint, entry/exit signs, blocked-exit behaviour and the detour the visitor creates. No new roster edit on this pass.

Acceptance test: Acceptance test deferred to that candidate specification: a real passage redirects the route and leaves by a readable route without erasing occupants; current selection is unknown. This ticket is a specification task, not permission to run HugeThings now.

## T18: Switch off formation volatility

Defs/ThingDefs_Natural/RM_LanternstoneFormations.xml wires vanilla CompExplosive without a local toggle; GenStep_ScatterLanternstone places these same kept forms. Add a next-version gate to explosive behaviour without suppressing mineral placement, glow or extraction. Keep code and defs. No dependency on Creep or galuush ignition.

Acceptance test: Fresh default formations can be mined and damaged without explosive comp effects or a log error; the same forms still glow and yield native stone. Next-version switch on: damage can trigger the existing blast. Off again: no armed countdown survives.

## T19: Switch off Cleaver splitting and shard trail

RM_CreepCleavers.cs RM_CompCleave handles damage splitting AND movement shards. Default cleavingEnabled off; gate the movement branch as well, or give it its own next-version switch. Ordinary predatory pawn and its current roster admission stay.

Acceptance test: Default moving/struck Cleavers leave no bespoke shard trail, split children or split letters; ordinary wounds and motion work and log is clean. On: qualified nonlethal damage can split and motion can shed shards; off/load clears queued work without destroying animals.

## T20: Switch off dormant soulchime powers

Fauna race/support XML wires CreatureBehaviors stun/soothe/shard-armor comps to RM_FacetMothLarvae. Gate only this species wiring behind a next-version switch; keep shared engine and defined animal. Do not add a wildAnimals row.

Acceptance test: Manually place the defined animal in a disposable default fixture: no special stun, soothe or shard armor changes/letters/jobs and log clean. On: existing comp effects can occur. Loaded natural roster identical before and after switch.

## T21: Switch off study reward ladder and ritual-like inscription

RM_OrunGhal.cs CompleteSession emits configurable lore letters and XP; keep completion/standing and actual greeting. Gate bonus XP, scripted lore letters and cousins-terms rite inscription in Building_RM_WorkingDead.GetInspectString behind a next-version switch. Plain identity/relationship inspect text and a single essential explanation of crystal control stay.

Acceptance test: Default real study completes and affects later greeting without extra XP, lore-rung letters or a rite-discovery inscription; log clean. On: the reward/lore path becomes available. Toggling cannot reset friendship or reveal campaign Cathedral secrets.

## T22: Build bounded remote defence

Owner answer: OWNER:1794375005355305543. Current Building_RM_WorkingDead only turns and raises dust; no defence path found. Implement definition.md encounter states and R4/R5: mark protected living galleries, warn on designation, react to actual extraction/damage with finite existing dead bodies, stop at retreat, preserve bodies and controller identity through save/load. Orun-Ghal never fights. Retain ordinary safe harvesting and remote-control sign.

Acceptance test: Through ordinary mining/attack jobs with all kept mechanics on, designation shows the territorial warning before work; actual protected extraction triggers visible, controller-linked defence by existing chassis. Cancelled designation does not. Retreat releases pursuit, reload preserves the same participants, destroyed minds cease control with readable collapse, and no new defender is manufactured. Ordinary stone mining outside a marked gallery does not trigger it.

## T23: Make remembered greeting real

RM_OrunGhal.cs currently changes rounds and inspect tier; no distinctive greeting gesture/state identified. Implement the peaceful greeting specified in definition.md, driven by real saved study visits. Keep current study work path but handle downed/dead/blocked suit, interrupted reservation, replacement studier and reload. No reward ladder dependency.

Acceptance test: Ordinary completed study visits followed by departure and return cause the saved suit to approach, stop facing visitors and give its distinctive nonviolent greeting. Interrupted study grants no progress; simultaneous workers cannot duplicate credit; new studier inherits colony acquaintance; dead suit remains a corpse, never respawns. No direct ProofStudy grants count as evidence.

## T24: Make cave entry and initial life satisfy the land

Inspect GenStep_ScatterCavePortal.cs, GenStep_ScatterMineshaftPortal.cs and RM_LanternDeepGenerator.xml. Resolve default cold hosts against loaded RM names, preserve an empty selected host list across reload, enforce fixed host climate eligibility, put shafts inside local technological ruins, guarantee reachable exit/mind/body encounter space. Current generator has no explicit Animals step: establish initial ordinary cast placement and sustainable use of existing spawning APIs. Separate Hush placement from its disabled power. Add a natural safe Lantern source without farming the surface. Do not author world tiles.

Acceptance test: Situation generator finds no inaccessible accepted entrance, orphan return, empty required encounter or safe-Lantern acquisition dead end across its declared range. State reads confirm actual animals/plants and navigable cave after ordinary portal entry, not just a populated roster. Warm hosts reject default injection; no world/save painting occurs.

## T25: Repair safe-light provenance and readable attention

Replace radius-only LitOnlyByLanterns classification with contributions matching the engine glow calculation, including occlusion, terrain, mobile light, roof caps and mixed sources. Keep shared light owners intact. Surface no new Direct Sun model. Expose current risk/cooldown and causal draw sign on inspect/motes, with no letter spam. Naturally reachable finite predators; no spawn inside sealed occupied rooms.

Acceptance test: Geometry sweep agrees with game contribution reads as models.md requires. Ordinary lit, equal-brightness Lantern-only, blocked ordinary lamp, mixed source, harvested Lantern and glowing floor cases sort correctly at defaults; sustained bright work draws danger through a legal visible approach, while dim/only-Lantern work can avoid it. Natural timer is advanced, not forced.

## T26: Resolve shipped products and engine boundaries

Find RM_ColdWax provider in the actual composed artifact or supply the already-promised ordinary fuel item at its rightful owner; do not redesign warm-reactive wax. Verify shared LightLedger/SettingsKit/HarmonyResilience compile inputs referenced by RM_LanternDeeps.csproj are supplied in the build checkout; they are outside this proposal checkout. Verify Wreckage and SleepingIce wreck children are packaged; About only declares CreatureBehaviors today. Verify native drinking and fictional flyers through existing engine state; no DLC-absent fallback.

Acceptance test: Composed default load resolves milk/butcher products, wreck genstep classes and child defs, with all DLC and no franchise companion required. Real milking yields usable fuel. Native fauna do not dehydrate beside native shallow water, and fictional flyers use Pawn_FlightTracker; visual flight only with owner present. Log clean.

## T27: Build Situation generator instrument

Implement models.md Situation generator using real production decisions and fixture ownership journaling. Extend existing collapse fuzz rather than treating it as engine proof. Repair validation.py any-True generator test, stale roster assertions and forced-success checks. RM_DeepHarness.LeaveDeep must not destroy an unowned reused Deep; keep-return is the default evidence path.

Acceptance test: Seeded output covers the declared partitions and both action orders, prints minimal counterexamples and instrument/production fingerprints. Deliberately wrong glow provenance, orphan portal and duplicate study credit are detected. Cleanup cannot delete a reused or occupied unowned map; abort/recovery journal restores owned fixture settings and current-map selection.

## T28: Build Light geometry instrument

Implement models.md Light geometry sweep and its game calibration, using real occlusion/contribution state. The existing Sipper kernel models radii only and cannot answer provenance.

Acceptance test: Calibration meets the model agreement contract; blocked-source and mixed-light mutants are refused. Emit per-cell source map and first divergent case. An unavailable engine field is reported unmeasured and escalated to instrument repair, never guessed.

## T29: Build Encounter state instrument

Implement models.md Encounter walk including real mining/study jobs, body identity and controller links. Existing ProofAnimate and ProofStudy calls cannot prove defence, greeting or natural study.

Acceptance test: Walk catches static-only chassis defence, invisible body replacement, job interruption credit, infinite defenders, Orun attack and lost cooldown on reload; matched game traces agree on state transitions and target identity.

## T30: Build Whole cave instrument

Implement models.md Whole cave season, including full-map state reads, normal time intervals and owned save/reload. Read all kept mechanics at defaults concurrently; never stage proof with fauna or risk disabled. Capture native-weather state without locking it clear. Existing A2 only checks prerequisites.

Acceptance test: Run baseline and reversed main-action order for a season with mid-save reload; produce cause-tagged population, flora, light, roof, job and encounter traces, worst case per bar and exception/log attribution. Detect injected population flood, pasture desert, stalled encounter and repeating exception. No forced helper successes accepted.

## T31: Complete discriminating live readings

Schedule future land/body/greeting looks for the declared ranges in bars.json using instrument-owned disposable fixtures, all kept features on. This ticket provides instruments, not a new art commission or permission to start game on this pass.

Acceptance test: Cold reader sorts all accept/reject pictures as specified, using ordinary zoom plus inspection. Mineral versus aware crystal, skeleton suit, controller sign, warning route and peaceful greeting are readable; state controls rule out preposed art and unrelated raids. Flight visuals obey owner-present rule. Dispose only positively owned fixtures.


## T32: Specify the later psychological Chorus

The frozen sheet names a psychological effect, while current DeepAmbience is audio only. Keep the ordinary hum now. Before later build, define the affected pawns, range, image/mood authority, stacking, recovery, save/load and player-facing sign; do not treat an audio loop as the effect or add Force powers.

Acceptance test: none, this is a deferred specification task; no defined psychological transition exists to test. Current defaults must nevertheless have no Chorus psychological hediff, job, letter or incident and a clean log.

## T33: Locate and specify later warm-wax behaviour

Current Wave1 milk/butcher references do not locate the RM_ColdWax provider or any warming comp. Resolve ordinary fuel product ownership for the kept life ticket first. Before next-version heat spoilage is built, locate existing behaviour or define storage, warming threshold/cadence, conversion/loss, readable sign, overlapping heaters and saved progress. Use existing environmental engines, without a new Direct Sun/heat kind.

Acceptance test: none, the provider and existing warm-reactive transition are unknown in available source. After locating them, write a fresh-map default-no-reaction/next-version-on-reaction comparison before enabling it; ordinary resolved fuel milking remains required now.


## T34: Specify later growing formations mature into parents that cleave offspring

Specify parent/offspring maturation, conservation of material, placement failure, cycle signs, population cap and saved growth before later build; consult existing growth engine rather than design a replacement. The feature remains next version, off; no kept bar may call it.

Acceptance test: none, this is a deferred specification/ownership task and its current runnable transition is not present in the available production path. Before later enabling, replace this with a default fresh-map absence/clean-log and enabled presence comparison against the located implementation.


## T35: Specify later machines leave galleries wiped, rogue and changed in allegiance

Locate any companion implementation first; later specification must distinguish controlled dead shells, player droids and Kindled heads, preserve readable departure/identity, obey wipe immunity, define reversibility and resolve interrupted travel/reload. Do not redesign the Droidworks engine. The feature remains next version, off; no kept bar may call it.

Acceptance test: none, this is a deferred specification/ownership task and its current runnable transition is unknown in the available checkout. Before later enabling, replace this with a default fresh-map absence/clean-log and enabled presence comparison against the located implementation.


## T36: Specify later talking cousins, cathedral testimony and production-facility story

Locate the campaign owner and current implementation; specify only the later discovery route and strict knowledge gate before adding any dialogue/quest. Never declare the Kindled already known or an active current crystal-mining war. Leave facility production design to its existing owner. The feature remains next version, off; no kept bar may call it.

Acceptance test: none, this is a deferred specification/ownership task and its current runnable transition is unknown in the available checkout. Before later enabling, replace this with a default fresh-map absence/clean-log and enabled presence comparison against the located implementation.


## T37: Specify later illegal kyber sales, imperial heat, hutt interest and donation/smuggling plot

Locate existing trade/blackboard owners and specification first; define cave integration gate, causal sale accounting, readable consequences, repeat sales, reload and quest boundaries. No new trade engine or help-the-Rebellion-here route. The feature remains next version, off; no kept bar may call it.

Acceptance test: none, this is a deferred specification/ownership task and its current runnable transition is unknown in the available checkout. Before later enabling, replace this with a default fresh-map absence/clean-log and enabled presence comparison against the located implementation.


## T38: Specify later additional imported orange crystal source and unified harvest integration

Identify the real provider and existing implementation before specification; settle native/campaign tier, acquisition/harvest and scarcity ownership, then provide a distinct default-off integration. Do not infer provider from colour or a donor name. The feature remains next version, off; no kept bar may call it.

Acceptance test: none, this is a deferred specification/ownership task and its current runnable transition is unknown in the available checkout. Before later enabling, replace this with a default fresh-map absence/clean-log and enabled presence comparison against the located implementation.
