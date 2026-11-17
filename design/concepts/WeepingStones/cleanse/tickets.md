# Build handoff — proposal only

These tickets are specifications, not filed ledger items or instructions to build during this pass. Current source and definitions remain untouched. T1–T11, T21 and T23 each switch off a built extra; its code/defs remain resolvable in the tree. New gate names below describe proposed UI behaviour, not claims of existing fields. Read all source callers cited before implementing. Every next-version control defaults off, says **Next version**, declares its dependencies/timing and must not execute through another enabled control.

Gate tests use a fresh disposable map on the existing authored world with otherwise shipped kept defaults and a recorded build/settings fingerprint. Read actual things/jobs/letters/incidents/quest parts and log delta at creation, after the relevant callback/pulse, and after reload. Definitions may still resolve: “absent” means no active objects, offers, producers or effects, not deleted defs. Positive controls explicitly enable parent prerequisites and that extra. These controls prove gating, not full acceptance of the untested next version. Existing saves require non-destructive readable suspension; no unique creature may vanish on disabling. Every fixture uses the capture/restore contract in bars.json; no canonical save and no current destructive suite teardown.

## T1: Suspend cocoon and dewsilk manufacture

Built callers: `Source/RM_DewsilkSwitch.cs`, mirrik shearable comp in `Defs/ThingDefs_Races/RM_WeepingStonesNatives.xml`, `Defs/RecipeDefs/RM_DewsilkRecipes.xml`, `Defs/ThingDefs_Items/RM_Dewsilk.xml` (all under src/RimMandrake/WeepingStones). Current `dewsilkEnabled` startup gate removes the animal comp but is insufficient to promise a hidden/deactivated recipe route. Default off and label next launch. Keep mirrik, normal flight/reproduction/taming and existing art. Decouple any feed text implying cocoon waste is required: feed currently accepts ordinary nutrition. Do not disable mirrik to hide the product.

Acceptance test: On a fresh default load/map with a tamed mirrik and ordinary tailor benches, no cocoon/fabric producer or spin order runs or appears, no related jobs/letters/incidents occur and log delta is clean; after enabling dewsilk and restarting with an otherwise matched fixture, the shearable producer and spin recipe/order are present. Read actual producer, recipe and item state; do not wait for a roll to infer absence.

## T2: Suspend the unique old-gorrask spawn and seasonal letter

Built caller: `Source/RM_WalkingCondenser.cs`, `RM_MapComponent_CondenserSpawner.FinalizeInit`, `RM_CondenserWorld` and `RM_GorraskCondenser` def. Set current `condenserEnabled` off for this version and gate every spawn/choice entry, not just its screen. Keep ordinary `RM_Gorrask` roster. Preserve unique-world state in existing saves, report suspension and do not silently remove the animal or consume its spawn latch. Child gates cannot force a new crab while the parent is off.

Acceptance test: Fresh default map init and reload create no old gorrask, seasonal choice letter, condenser job/incident or active unique-world claim and have a clean log; with Next version walking condenser enabled, a valid authored WeepingStones fixture admits its unique spawn and season-choice callback. Ordinary gorrask remains available in both arms.

## T3: Suspend the moving oasis terrain cycle

Built callers: `RM_CompWalkingCondenser.CompTickRare`, `GrowPool`, drying/death/despawn paths in `Source/RM_WalkingCondenser.cs`, plus `Source/Kernel/RM_CondenserKernel.cs`; quest transfer calls `DryAllNow`. Add an explicit next-version terrain-cycle gate under the deferred parent, including cleanup callbacks. A legacy suspension must preserve a reversible terrain ledger and tell the player what is suspended; do not erase a player floor, natural pool, or living resident to get absence. Normal truce stays active for actual kept water.

Acceptance test: Default fresh map and a controlled inert-old-crab callback fixture show no condenser-owned water edits, drying jobs or associated letters/incidents and a clean log; enabling the walking-condenser and terrain-cycle prerequisites admits recorded growth/drying callback state in the positive fixture. Compare terrain ledger and truce field; ordinary authored pools remain in both arms.

## T4: Suspend the Guide action

Built caller: `RM_ChoiceLetter_Condenser.Choices` → `Choice_Guide` in `Source/RM_WalkingCondenser.cs`; it chooses a home-area/colonist-near site. Gate UI and direct action invocation. This does not gate ordinary caravan routing or farmer pen selection.

Acceptance test: Default fresh map and a forced choice-view query contain no Guide order, guide job, letter or destination mutation and log is clean; with parent/choice prerequisites and Next version Guide on, the option and its valid destination action are present, with a no-site rejection control. The gate-off direct invocation is inert even if a stale letter object exists.

## T5: Suspend the destination sale

Built caller: choice letter → `Choice_Sell`, buyer/payout/expiry fields in `RM_WalkingCondenser.cs`. Gate payout, goodwill, letter, right and choice together, including repeat-click callbacks. Keep vanilla trade/carrier wiring. The unsatisfied delivery promise is preserved in T22; a gate test does not certify the existing payout as fulfilment.

Acceptance test: At defaults no Sell action, buyer-state mutation, payment/goodwill/rights, letter or incident appears and log is clean on fresh/reloaded fixtures; with parent prerequisites and Next version sale on, the action and pending-sale/payment path become available exactly through that gate. Repeated stale off-state invocation produces no payment. Enabled functionality beyond availability still owes T22.

## T6: Suspend extracting the machine from the crab

Built caller: choice letter → `Choice_Cut` creates/minifies the plant, calls drying, ends the world state and kills the crab. Gate every part atomically under the deferred extraction control. Do not expose a kill-only fallback when output cannot be placed. Extraction's old first-strike/truce consequence is debt in next-version design, not a reason to retain it now.

Acceptance test: Default fresh map/stale-letter invocation creates no extraction job, plant, kill, pool edit, letter or incident and log is clean; with walking-condenser prerequisites and Next version extraction on, its action becomes present and can enter its explicitly gated conversion path in a disposable fixture. Failure to place output does not remove the animal. No retained farm action calls this path.

## T7: Suspend portable condenser flask production

Built callers: `Source/RM_AncientCondenserPlant.cs`, its comp in `Defs/ThingDefs_Buildings/RM_AncientCondenserPlant.xml`, water item `Defs/ThingDefs_Items/RM_CondenserWater.xml`; extraction supplies the machine. A root crab switch alone does not stop a building already placed or acquired by another route. Add next-version production gate at its tick callback; keep defs/minification resolvable. Do not redesign OasisMaker or add a thirst/ship-life-support consumer.

Acceptance test: Default fresh map contains no plant/water producer or related order/job/letter/incident and log is clean; a controlled placed legacy plant remains recognisable but produces no water when off; with Next version portable condenser production on, that same producer's accumulator advances and produces its water item. Scanner can report a real placed object but cannot spawn one.

## T8: Suspend the collector capture quest

Built callers: `Defs/QuestScriptDefs/RM_CondenserQuests.xml` (`RM_CondenserCapture`), `Source/RM_CondenserQuests.cs` crab gate, claim/subdued/taken nodes, history events and transfer/despawn. Current `condenserQuestsEnabled` is default true; make the whole quest family next-version/off, with a branch gate if branches are separately exposed. Prevent random and direct offer generation while off. Preserve readable active legacy quests according to the explicit suspension policy, not new rewards or silent crab transfer.

Acceptance test: Fresh defaults have no capture offer, quest-part callback, buyer party/transfer, related job/letter/incident or reward and a clean log; with parent, claim and Next version capture prerequisites enabled a valid live-crab fixture admits the offer and its claim part. Gate-off dev/direct generation rejects cleanly, rather than proving only random rarity.

## T9: Suspend the keep-free quest

Built callers: `RM_CondenserKeepFree` graph and `RM_QuestNode_CondenserHunters` raid/attack-target callbacks in `RM_CondenserQuests.cs`. Gate offers, scheduled hunters, delayed letters/rewards and claims. Vanilla raids/truce remain unaffected. Later freedom means an available exit and actual voluntary departure plus access to the promised season's water; survival inside permanent confinement alone is not fulfilment. No additional AI/diplomacy design is commissioned now.

Acceptance test: Fresh/reloaded defaults and direct offer query produce no keep-free offer, hunters, attack-target job, letter, incident or reward and log is clean; with parent/claim/Next version keep-free controls on, a valid fixture exposes that offer and its scheduled hunter parts. A queued legacy callback while suspended cannot generate a new hunter raid.

## T10: Suspend quest claim/slot transactions and campaign mapping effects

Built callers: both quest graphs → `RM_QuestPart_CondenserClaim`, `RM_ClaimKernel`, `RM_CondenserWorld` and faction-slot nodes/defs, plus `src/RimUtinni/UtinniPatches/Patches/RUT_CondenserQuestSlots.xml`. Gate active claim/withdraw/reoffer/reward behaviour with the deferred quest family. Leave faction slot definitions and additive mapping resolvable without executing a quest. No campaign name enters free-tier text. No kept job requires these helpers.

Acceptance test: Default free/campaign fixtures contain no active condenser claim, rival-withdrawal letter, reoffer, buyer-state effect, job or incident and log is clean; with the quest prerequisites enabled a valid simultaneous-offer fixture admits a claim and uses the resolved free/campaign faction mapping. Disabling one branch cannot let it seize or end the other's claim. No static def needs deletion to pass the off arm.

## T11: Suspend rendered huldu fat and the proposed quality extension

Built callers: `RM_RenderHulduFat` recipe in `Defs/RecipeDefs/RM_StockedPoolRecipes.xml`, product in `Defs/ThingDefs_Items/RM_StockedPoolCuisine.xml`, both-stove patch `Patches/RM_StockedPoolRecipeWiring.xml`. Add next-version recipe/product-production gate. No generic quality-improvement callback was found; do not build it as a fix. Decouple the shared recipe list so murrin broth, pool-fry, iaala paste and cull dish still work. Huldu meat, fur and doubt thoughts remain ordinary kept outputs.

Acceptance test: Fresh defaults and both stove order lists have no huldu-fat producer/order, fat job/product, bonus-quality effect, related letter/incident or log error; with Next version huldu-fat on, the fat recipe/product route is present. Kept recipes and huldu ingredient memories operate in both arms. Quality-extension acceptance test: none, that extension is unbuilt and is not commissioned.

## T12: Make the on-water health gauge usable

Existing inspect source: `Source/RM_PoolBody.cs`, `RM_Zone_PoolPen.GetInspectString`, PoolStock census; no water overlay renderer is present in the project/source/texture census. Specify productive, hungry/thin, crowded, empty and vhorrin cues with distinguishable shapes plus cause text. Reuse accepted assets/cheap presentation where possible; no count of animation variants. Warning precedes avoidable loss by an ordinary intervention opportunity; reconcile this timing with the season model. Read the committed post-action census, not the pre-pulse state. Empty state must be distinguishable from missing overlay.

Acceptance test: B5's shuffled unselected-pen live glance pictures sort correctly at normal zoom across clear/fog/sandstorm and pen geometries; independent state reads show current cause/census after feed, emergence, harvest, edit, cull and reload. A disabled/missing-overlay negative control cannot count as an empty-pen pass. No film-only test with frozen weather is accepted.

## T13: Complete minimal renewable farm intent, feeding and failure/recovery

Existing callers: all `RM_WorkGiver_*`/`RM_JobDriver_*PoolPen`, `RM_MapComponent_PoolStock.Pulse`, `RM_PoolKernel`. Present gaps: harvest is unthrottled, nearest-pen stocking lacks intent, feed resets a clock independent of real nutritional needs, reproduction/residency is unproven and vhorrin has no demonstrated stock-consumption route. Build the season model first. Add minimal destination/reserve/request controls, valid connected water footprint, real safe-bank nutrition delivery, preserved debt, deliberate cull and warning before damage. Verify vanilla mating before adding any local integration; do not commission a shared engine rewrite. Emergence from stressed stock and additional predator stock-pressure must be shown causally. Keep uncertainty about normal neutral-pawn reproduction until measured.

Acceptance test: B3/B6 using ordinary work priorities and no replacement wild captures after founding show repeated surplus production with viable breeders, real feeding, warned deliberate overdraw/neglect, causal emergence and stock pressure, then cull/care/restock recovery. Forty-colonist parallel work and pen edit/reload cases conserve inputs and preserve the selected reserve/debt. Tiny or unsuitable pens reject with a reason. A forced-job-only green and debug-spawned cull do not pass.

## T14: Make animal/item jobs and escapes readable and conserved

Existing callers: `RM_JobDriver_NetPoolBreeder`, `RM_Projectile_PoolNet`, `RM_JobDriver_StockPoolPen`, `RM_JobDriver_HarvestPoolPen`, `RM_JobDriver_CullVhorrin`, `PoolStock.TrySpawnVhorrin/TryEscapeVizhik`. Input is currently removed before silent-fail output lookup/placement on several paths; escape uses despawn/respawn and only dev logging. Build/validate output before input removal, preserve equivalent breeding-relevant state, serialize pending ownership, handle handler death/target loss and output blocking safely. Escape must traverse a real reachable moist route with an ordinary cue; a route failure leaves the resident. Keep aim/landing-dependent misses and no prethrow freeze. No new catch verb/equipment catalogue.

Acceptance test: B4/B6 boundary generator, calibrated to real before/after/save traces, shows conserved animal-equivalent inputs/outputs for successful, cancelled, concurrent and reloaded work; missing output defs/full placement cannot erase the input. Moving-target coverage controls distinguish hit/miss; no-job handler control stays accounted for. Escape cannot cross closed walls or leave the map invisibly, and its traveller can be recaptured. Ordinary players can identify starvation, emergence, capture, harvest and escape reasons without a dev log.

## T15: Supply actual wet-land habitat and preserve the authored Oasis handoff

Existing source: biome terrain/roster/weather data, `Patches/RM_OasisMutatorFlora.xml` and `Source/RM_TileMutatorWorker_Oasis.cs`. These define native bonus plants but do not prove wet faces or shade-keyed placement. Build the geometry audit and inspect naturally created local maps on existing tiles before inventing a humidity engine. Define eligible exposed rock faces, native wet/shade placement, pool-edge bands and the hot-flat-seep exception. Preserve usable dry shoulders. No planet generator, worker-score feature, painter or random landmark authoring. The current flora switch is a new-local-map/spawn-list effect and must be labelled truthfully, not as alternative-planet generation.

Acceptance test: B1 real map views and B2 useful plants agree with the cell masks in both source regimes and all stated geometry classes, including reload/use; ordinary desert Oasis retains its own flora and no Earth palm/grass injection returns to this biome. Positive maps have no debug water/plant placements. Full-map growth does not replace dry ground with undifferentiated green.

## T16: Reconcile ordinary native life with effective spawns, flight and shared-plant ownership

Source: `Defs/ThingDefs_Races/RM_WeepingStonesNatives.xml`, `RM_StockedPoolFauna.xml`, biome `wildAnimals/wildPlants`, additive Utinni fauna patch. Mirrik def exists but is absent from the current inline roster; determine its actual loaded spawn route and make the retained native available without assuming a missing inline row is the only possible route. Keep dewglider/mirrik real flight and inspect flight-tracker state. Record every effective multi-home creature; evict none. The current `RM_Dewshrooms` cross-biome identity must follow the standing duplicate/diverge ruling; normal placement stays while content ownership is repaired. No aura/climbing/swarm/terrain-dig invention is authorised.

Acceptance test: B2 ordinary lifecycle demonstrates useful forage, medicine, timber, actual dewgourd growth/storage, native tame/caravan use, applicable environmental-water drinking and real flight tracker transitions; source and runtime roster/catch/variant mappings reconcile with no eviction or missing-reference log. Flying visual work only with owner present; state-based evidence is explicit. Missing-def negative probes fail honestly. A current loaded spawn/needs read, not an old item closure, establishes ordinary native availability.

## T17: Verify the kept farm food and actual doubt economy

Existing defs: `RM_StockedPoolMeats`, `RM_StockedPoolCatchItems`, `RM_StockedPoolCuisine`, `RM_StockedPoolThoughts`, recipes and stove wiring. Keep existing minimal preparations and exact ingredient/trait routes; remove present-tense promises of absent keeper/quality/cooperative mechanics from default player text. No new C# thought system and no third-party cuisine dependency. Resolve huldu's food unease consistently with later animal prose without overriding picked art.

Acceptance test: B7 matched real eaters receive the correct direct/ingredient memories and trait exceptions; ordinary fish is the negative control; both stoves produce accessible kept food, and the cull dish follows actual cull output. Existing rot/keeping properties actually tick. Fat/ideology/keeper extensions cannot run at defaults; source/category presence or total mood alone is insufficient evidence.

## T18: Prove the shared truce/heat boundary and correct dangerous advice

Existing callers: biome's sun/arrival extensions, `EnvironmentalHazards/Source/RM_MapComponent_WaterTruce.cs`, `RM_WaterTruceHuntSuppression.cs` and shared Direct Sun. Correct local obsolete heat fields/advice to the existing shared rule; do not redesign either engine. Use actual guilt/field/hunt state, including tame predators, repeated damage, water edits and handler-injury callbacks. Required warnings explain the field and effects; no quest/diplomacy layer. The current v1 source makes compatibility plausible because handling damage has factionless stock as instigator and farm conversions use no guilty hit, but only real callback evidence settles it.

Acceptance test: B8's active-hunger inside/outside/guilty/non-guilty/zero-damage controls and ordinary care jobs read the expected shared predator/retaliation state across reload and terrain changes; no handler is incriminated by a manufactured player damage event. Equal geometry uses equal Direct Sun under this biome and the ordinary control, with roofs/parasols recognised and ambient heat unchanged by shade. Correct on-map advice names those actual protections. If a shared-engine conflict is measured, report the exact trace; do not silently add a second truce or biome heat rule.

## T19: Ship truthful settings and non-destructive suspension

Existing caller: `Source/RM_WeepingStonesSettings.cs`, shared SettingsKit, EnvironmentalHazards truce controls and composed biome/carrier gates. Complete safe on/off at real feature entry points, next-version labels/defaults, dependency disable reasons and real effect timing. Persist/clamp settings and keep search/reset usable. Settings do not remove needed types or instantly discard carried inputs. Current-off and legacy-save cases differ: suspend old unique content readably, preserve state/identity and use an explicit reversible cleanup path for its owned temporary terrain if required. No silent animal deletion. Keep shared engine screens authoritative rather than duplicate values.

Acceptance test: Fresh default, all-off, single-feature off, parent-off/child-on and persisted reload/startup cases have the stated actual effects, ordinary land/fishing still works, pending transactions stop safely, log is clean and reset restores this proposal's defaults. Legacy old-crab/plant/quest fixtures remain readable and conserved on disable. UI scope says immediate/next pulse/next launch/new local map as the actual caller requires. Corrupt numeric values cannot produce an error storm or invalid job range.

## T20: Build and calibrate missing proof surfaces and restore safely

Existing instruments: `validation.py`, `northstar_plan.py`, `northstar_site.py`, `selftest_weepingstones.py`, `prove_job_net.py`, `Source/SelfTest/Program.cs` and `WeepingStonesFuzz.cs`. They already cover useful reads and pure branches, but the current suite has no convincing whole season, autonomous breeding/feed-reserve proof, visual gauge, habitat or full truce causal test. Some routines explicitly report UNMEASURED, lock weather or clear prior state destructively. Replace only the necessary acceptance adapters, keep honest regression checks and don't make all old counts into bars.

Provide read-only snapshots of zone identity/eligible cells/reserve/feed due/debt/post-mutation gauge; actual carried items/animal references; job offer and state transitions; needs/mating/birth/escape/emergence/death reason; damage guilty/source/faction; actual flight tracker and field membership. No claimed existing tool name is invented here. Define the three models in models.md, with their calibration probes and fingerprint; build the season model first. Implement an unconditional fixture begin/restore verification journal and an interrupted-run recovery command. Use current schema lint before any later real bridge call.

Acceptance test: Each B1–B9 instrument discriminates its own accept/reject with all kept systems on, known-wrong/missing controls fail and unknown tool fields yield UNMEASURED. Calibrated models meet their named real-game agreement requirements. The full B9 season includes actual reload and second action order, plus recorded activation/lock snapshots and log delta; deliberate instrument faults are classified separately. Restoring a completed or interrupted fixture matches its saved before-state digest and restores the actual captured settings/terrain/zones/pawns/weather locks, not guessed defaults. The new instruments are specifications until built, not fabricated proof results.

## T21: Suspend special seep-stone/silver angling loot

Built caller: biome `fishTypes.rareCatchesSetMaker` → `Defs/ThingSetMakerDefs/RM_RareOasisCatches.xml` → seep-stone/silver outputs. Add next-version special-loot gate to this route without disabling ordinary wild catch or needing to delete resource defs. No kept farm action or recipe consumes seep-stone (korrim is the broth spice); decouple any stale description implying otherwise. Do not remove ordinary vanilla fishing behaviour elsewhere.

Acceptance test: Default loaded catch-source state and deterministic draw control expose no WeepingStones special-loot route, seep-stone/silver special output, related job/letter/incident or log error; with Next version special oasis loot on the set-maker route and its output are present. Ordinary six/stocked catches remain available in both arms. A short run with no rare roll is not an off-gate proof.

## T22: Specify deferred sale fulfilment before enabling it for play

Promised but absent: buyer-settlement destination, actual delivered seasonal pool/access, rights/expiry and failure/refund. Source search for `buyerPoolUntilTick` and buyer use in `RM_WalkingCondenser.cs` finds declaration, scribing and assignment, not delivery. Default design for the next-version ticket: an inhabited buyer destination must exist; price is earned on actual arrival and usable pool/access, and failure before that cancels without payment. If prepaid, hold refundable escrow and return it on death/path/map failure. Never sell absentee toll rights. Extraction at water retains the already promised first-strike consequence; keep-free success requires actual freedom/departure and the promised farmers' access. These are deferred contract debts, not current bars or new quest commissions.

Acceptance test: Before this next-version feature may be enabled for ordinary play, a contract state walk plus real destination state demonstrates offer→commit→arrival→usable season→expiry and failure/cancellation in either order with competing capture/protect/extract actions and reload; money and rights conserve, and no non-inhabited water toll is created. For this version, T5/T8/T9 off-gate tests establish absence only; no live fulfilment proof is claimed.

## T23: Suspend local plant found-tech study hooks

Built external caller found during cross-source search: `src/RimMandrake/EnvironmentalHazards/Patches/RM_ShadeLessons_Sources.xml` injects `CompProperties_FoundTechStudy` into `RM_Dripfringe` and `RM_Shadefern`, gated by `EnvironmentalHazards.ShadeLessons`. Give those local content hookups a next-version default-off gate, at patch/application or callback as appropriate; retain shared engine capability elsewhere. Decouple ordinary plant placement, native harvest, warnings and roofs from research progression. Existing plant defs and legitimate already-earned research are not deleted to fake an off state.

Acceptance test: Fresh default WeepingStones map with both plants produces no local study order/job, knowledge/project reveal, study letter/incident or log error; with Next version native study hooks enabled their study comp/action and progress are present. Native plant life and shared shade remain active in both arms, while an independently enabled neighbour's study mechanism is unaffected. A globally disabled shared feature is not the negative control.

## T24: Bound deferred unbuilt promises; no hidden commissioning

The following are absent from the local runtime path or remain drafts: recapture ladder/servo vents and ruin progression (the owner-redirected OasisMaker stays separate); pilgrim routing/tokens; courtship choreography; sillik climbing/face feeding and ssurr aura; mirrik swarm/pollination; burrak terrain basins; multi-cell gorrask; separate species catch methods; coordinated cull; annual crash lockout; keeper/roast/ideology/global-feast extensions; unique aeolian chords. The Refused Toll is already deferred by the owner and has its own campaign spec; no new work or owner re-question follows. Ivvol immunity is recommended for retirement, and its present-tense guarantee must become attributed farmer belief if still mentioned.

For any later commissioning, require a finite state/transition spec, real callers/dependencies, failure/reload case and positive/negative instrument before switching on. Defaults here are the smallest stated boundaries in definition.md and ambiguities.md: these systems have no autonomous effect. Update player-facing text so vanilla actions do not claim these unimplemented powers. Do not revive the killed wind-hour, born-and-dying-water or superseded four-state vane proposal; do not reopen recorded close misses (fish walk, pilgrim passage, dewsilk casket, lying fish). Normal lore, existing ruins and ordinary reproduction do not promise those systems.

Acceptance test: A source/loaded-effect inventory at default reconciles each listed promise to an absent local runtime caller or an inactive explicit next-version gate, and default player text promises only ordinary current actions. Retained life does not invoke their absent systems. Enabled-mechanic acceptance test: none, these unbuilt extras are explicitly uncommissioned; a future scoped design must provide that test before activation. No art or game code is written by this proposal ticket.
