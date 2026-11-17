# Proposed implementation and instrument tickets

No ticket is filed, built or executed by this pass. These are reviewable requirements for the later authorized builder. Retain code, defs, assets, paid work and saved objects; never delete them to implement version scope. Existing ledger items are reused as noted, not closed or silently replaced.

For every switch-off ticket below, “default” means the proposed first-version defaults on a fresh-state disposable authored local map, all DLC and retained engines/mechanics active, nothing locked; “on” means the labelled next-version switch explicitly enabled with its legitimate prerequisites. Read actual state, acquisition paths, jobs/effects, letters/incidents and the complete log interval. Zero extra output alone is insufficient: the same eligible inputs must exercise the consumer with the switch on. All such branches end by discarding the disposable copy, restoring exact entry settings and independently reading equality. Existing world and canonical saves are never edited or generated. Runtime acceptance of an ON branch proves availability/gating only, not next-version readiness or passage of that version's old bars.

Each built extra has a separate ticket, even if one master “next version” UI groups its controls. Default-OFF must be consistent in static initializers, Scribe fallback, reset snapshots, UI and loaded consumers. No per-DLC ablation. Acquired legacy things safely persist while off; default fresh state has none. No off operation kills people, deletes gear or silently finishes a paid job. Any added quiet/paused UI explains the retained state. These conventions are part of every acceptance test.

## T0: Quarantine historical planet scoring; recommend permanent retirement

Source/callers: `Source/SlimeBiome.cs` BiomeWorker and `RM_SlimeWorld.BiomeScore`, BiomeDef.workerClass/ranges, `SlimeMod.cs` rarityFactor/UI and reset/serialization. Separate them from retained BiomeDef terrain/roads/life. Keep historical source/defs inert and the planet-rarity control unavailable with an honest removed-from-scope explanation; no next-version opt-in can generate a world. This is my recommendation to retire the capability, not an executed retirement or a ruling change. Current explicit no-worldgen authority controls despite the older universal-planet brief. No world/tile edits and no generator run are needed to make this reviewable.

Acceptance test: Static/loaded state read finds no active alternative-planet scoring/rarity consumer or offered worldgen control; existing authored Slime map still resolves its own BiomeDef, terrain/roads/plants/animals. No worldgen invocation is allowed in either branch; there is no ON test because this is prohibited capability, not a switched extra. Log/load checks clean.

## T1: Switch off greater-gappo channel engineering

Source/callers: `Defs/ThingDefs_Races/Gappo.xml` greater comp -> `RM_CompGappoChannel.CompTickRare` -> SetTerrain and filth Destroy; `gappoChannels` already exists. Default it OFF and label next version. Keep every gappo race, grazing, resistance and roster entry. No kept caller needs its paving/cleaning result.

Acceptance test: Default greater-gappo grazing leaves no gappo-attributed hardened terrain or removed smear; no channel jobs/objects/messages/incidents, log clean. With switch ON the same eligible non-liquid cell hardens/cleans, while liquid control remains; actor/write witness rules out a shared growth change.

## T2: Switch off solvent cuisine, retain raw-slime meals

Source/callers: `SlimeMod.WriteSettings` and static startup -> `PitSolvent.Apply` -> recipeUsers/cache; `SlimePitSolvent.xml` recipes/products. Default pitSolvent OFF/next version; gate acquisition, bill availability and active recipe consumption for toxipotato/twisted-meat/ambrosyx conversions, including cached work/bills. Base RM_Make_SlimeMeal and pit stay available. No kept food loop may call a solvent recipe. Preserve finished legacy meals normally; return reserved inputs on safe cancellation.

Acceptance test: Default fresh map shows no solvent-product acquisition, eligible solvent bill, job, letter or incident and log is clean, while raw-slime meal bill completes. ON shows the same supplied solvent recipes/products and normal work route; OFF mid-bill prevents further solvent work without losing reserved input.

## T3: Switch off farm ruins and their ledger/loot hook

Source/callers: `GenStep_SlimeFarmRuins` in `FarmRuins.cs`, its mapgen patch/GenStepDef, `MapComponent_SlimeFarmRuins.ruinSites`, `FarmLedger.xml`. Default farmRuinsEnabled OFF/next version and make local setup hook inert; keep code/defs. Gate ledger/associated custom loot acquisition independently of setup. Existing saved structures/items remain. No extra generation is built, and ordinary crop conversion has no dependency on ruin sites or ledger reading.

Acceptance test: Default fresh local-map content/state has no new farm-ruin sites, farm ledger, custom loot/job/letter/incident and log is clean; ON diagnostic local fixture exposes the scoped setup/content route without any planet generation. Ordinary field conversion still occurs OFF; existing saved ruin identities survive disable/reload.

## T4: Switch off target/rider archive selection

Source/callers: `GeneArchive.cs` Active/Dialog; `CompGeneSeeker` gizmo; `SlimeMod.WriteSettings` cache invalidation; default and campaign GeneArchiveDefs. Add/route next-version gene journey master OFF, with target archive selection unavailable. Retain data/classes so existing saved genes and companion mods load. No current contact, resistance check, poison cure, antidote or basic workbench depends on choosing an archive.

This also defers the archive's RM_Gene_SlimeResistance acquisition, with T5–T7 gating its seeker/injection route. No replacement acquisition is promised in 0.1.0. The loss conflicts with law 1 and is presented in owner_pages.md Q1 before application. Preserve existing active resistance genes and RM_SlimeResistant race-extension checks independently of archive availability.

Acceptance test: Default normal player cannot open a target/rider selection action or obtain its output/job/letter/incident; no new selection state and clean log. Existing active resistance genes and race-extension resistance still block film with the archive OFF. ON with ordinary blank seeker and loaded archive opens the real list, including RM_Gene_SlimeResistance, and preserves chosen identity; campaign-priority selection remains data-driven.

## T5: Switch off seeker acquisition and gene localisation

Source/callers: `GeneSeeker.xml` recipeMaker/usable comps; `CompGeneSeeker` inspect/gizmos/float menu/world-tile search/mark in `GeneSeeker.cs`. Same labelled gene master default OFF. Gate recipes/trades/rewards plus scanning/gizmo/mark refresh, not just UI drawing. Pause existing primed/loaded legacy samples without silently expiring them while their whole system is disabled; save remaining lifetime and chosen identity. This decouples availability from core resistance and cure primitives. There is no new home console.

Acceptance test: Default fresh state has no normally acquirable seeker, beacon mark, scan job, gene letter/incident or seeker output, log clean. ON ordinary acquisition/scan produces the chosen target mark with a visible lifetime. Disable a legacy primed sample, reload and re-enable: identity/remaining enabled-time lifetime preserved, no automatic scan or use while OFF.

## T6: Switch off marked-current extraction work

Source/callers: `CompGeneSeeker` float menu -> `RM_ExtractSlimeSample` in SlimeJobs -> `JobDriver_ExtractSlimeSample`, input destruction and loaded output. Default the extraction consumer OFF even if an old seeker or queued job exists. Cancel/release reservations and preserve or return the actual blank/source, with no loaded output. Core harvest uses vanilla plant/forage jobs and must remain independent.

Acceptance test: Default eligible current cannot start/finish extraction, no loaded injectable/extraction job/letter/incident appears, log clean. ON with normal selected mark and carried seeker completes real work/consumption into a chosen dose. OFF mid-extraction preserves accounted source/reservations without duplicate output; expired/invalid mark does not yield a dose.

## T7: Switch off gene injection, coma and accelerated film

Source/callers: loaded seeker target comp -> `CompTargetEffect_InjectSlimeGenes` -> AddGene, SlimeMarked, XenogerminationComa, StartFastClock, Destroy. Gate the effect and normal target action with the default-OFF gene master, including previously acquired items. Keep ordinary antidote, generic RM_SlimeLadder/SlimeUtility and resistance-gene identity lookup usable without enabling this. No new default acquisition of resistance is promised via the disabled archive; existing resistance/mycoid route and ordinary floors/cure remain legitimate.

Acceptance test: Default fresh state has no injected target/rider, injected flag, gene coma/job/letter/incident and clean log; a legacy loaded item cannot execute the effect OFF. ON ordinary use consumes a field-extracted dose and exposes target/rider/coma/fast film and available normal friend treatment. Those ON outcomes retain the old source constraints; they do not prove the deferred version passed.

## T8: Switch off new gene social marks; retain generic existing gene effects

Source/callers: injection -> `SlimeMarked`/MarkIncrement; `ThoughtWorker_SlimeMarked` in GeneArchive; `GeneConditions.cs`; campaign gene defs name public condition classes. Gate new mark/opinion acquisition through the gene master OFF and stop deferred mark-only processing where appropriate. Existing marked pawns/genes retain identity and historically authored effects; do not remove public gene classes or make already-existing campaign carriers invalid. Preserve Reek/charm exceptions, heritable endogene and felt-rider obligations for the next version.

Acceptance test: Default fresh map gains no Slime-marked/rider-specific social state, gene letter/incident/job or artifact and log is clean. ON normal acquisition yields its authored visible/felt rider and mark outcome with exceptions; already marked legacy pawns remain stable through OFF/reload, and core poison/film doers resolve without calling selection/injection.

## T9: Switch off last-touch archive recording and decouple contact

Source/callers: `MapComponent_SlimeExposure` and `RM_CompEngulfer.Engulf` call `SlimeArchiveUtility.Touch`; `ArchiveResurrection.cs` gates Files/Touch and owns GameComponent records. Set archiveResurrection OFF/next version, keep saved entries, gate all new recording regardless of source. Contact and engulf must execute normally when Touch is no-op; their calling this extra is coupling only. Retain the archived life requirements: last eligible touch, not death-time data; health/memory/contact omissions remain next-version reconciliation, not waiver.

Acceptance test: Default fresh exposed and engulfed colonists acquire ordinary outcomes but no new archive entry, snapshot job/artifact/letter/incident and clean log. ON the same actual contacts update the corresponding entry/version. OFF legacy entries survive reload unchanged while ordinary exposure and giant feeding keep working.

## T10: Switch off paid archive growth and safely pause legacy vats

Source/callers: `SlimeArchiveVat.xml` Building_SlimeArchiveVat menu/Begin/TickRare -> payment/Grow; ArchiveGrowing research/thoughts. Gate normal vat acquisition and all active paid progress default OFF/next version. Pause retains entry, exclusive person reservation, paid inputs/progress and power state, no fee/refund exploit or automatic completion while OFF. Keep code/defs/save compatibility. Existing source ticker omission, duplicate-vat reservation, completion returned-state, health/memory fields and changed-family restoration remain in the deferred delivery backlog. OWNER last-touch/expensive Helix and prior remarriage/grief answer remain binding. Reuse archive-last-touch ledger item as next-version work rather than pretending it is fixed.

Acceptance test: Default fresh state offers no normal vat/growth acquisition, returned pawn, growth job/letter/incident and log is clean. ON with legitimate dead recorded person and paid/powered process offers and advances ordinary growth. Disable part-way and reload: no progress/return/new fee, original paid progress and reservation retained; re-enable resumes once without marriage rewind or duplicate person.

## T11: Switch off wounded-titan gelatid shedding

Source/callers: `RM_CompEngulfer.PostPostApplyDamage` -> `RM_TitanKernel.ShedStep` -> ShedOne and negative AddMass; titanoslimeSheds setting. Default OFF/next version. Keep wounding, natural engulf/rescue, all gelatids in the roster and default permanent growth; no kept mechanic may require a shed for feeding or prey release.

Acceptance test: Default wounded eligible giant produces no shed-created animal/item/job/letter/incident and log is clean; source damage does not reduce default earned stage. ON same wound regime can produce traced shed gelatids under its cooldown. Presence of an ordinary roster gelatid is not evidence shedding ran.

## T12: Switch off chunk acquisition and thrown bomb

Source/callers: Titanoslime.xml butcherProducts -> RM_TitanoslimeChunk in SlimeSealBreach.xml -> projectile class -> `Projectile_SlimeChunk.Impact`/Burst. Default chunkBomb OFF/next version AND gate chunk generation/butchery/recipes/rewards/equipping/use, so a fresh map cannot acquire it merely by killing the kept giant. Legacy chunk remains inert/readable with all extra switches OFF; no default burst/drench. Keep ordinary raw slime and giant corpse-size hooks independent. Preserve future immediate movement/fighting impairment, nearby ally danger and finite real release expenditure. A direct Burst helper never proves normal throwing.

Acceptance test: Default fresh normal giant butchery yields no chunk, throwable job/projectile, burst letter/incident or chunk-induced film/terrain; log clean. ON legitimate butchery exposes a real finite chunk and ordinary throw creates its effect. Switching OFF with a queued/held legacy chunk blocks the effect and conserves the item; no silent pawn/item loss.

## T13: Switch off temporary burst terrain; conserve legacy ownership

Source/callers: `ChunkBombUtility.Burst` -> `MapComponent_ChunkBurst.Convert`, expiry tick and saved cells/terrain/until lists in ChunkBomb.cs. Default follow OFF chunk master. No default caller from ordinary growth or rain may use this extra's converter. If an old save contains a pending temporary patch, retain its exact prior terrain/remaining lifetime and pause its extra timer while OFF; it is flagged legacy, not silently overwritten. Re-enable restores according to owned layer with overlap handling; another engine's later terrain write must not be undone blindly. T23 includes this legacy transition, outside fresh default acceptance.

Acceptance test: Default fresh state has no chunk-burst patch/expiry job/letter/incident and clean log, while ordinary growth/rain terrain works. ON a real chunk use creates a traced temporary patch with later owned restoration. OFF/reload legacy patch retains identities/provenance and remaining lifetime without clobbering later foreign/FlowWorks writes or using it to pass default rain.

## T14: Switch off chunk shelf consumer and preserve old chunks

Source/callers: `CompChunkShelf` and `MapComponent_ChunkShelf` stack/spawned-inventory/equipment sweep. Default OFF with chunk system. Do not run an expiry sweep on absent or retained legacy chunks while disabled. Preserve remaining enabled-time lifetime and readable paused state. On re-enable use full holder coverage (carry/container/caravan/ship as actually supported), retaining the historical expiry/accounting backlog rather than equating the current map-only sweep to complete implementation.

Acceptance test: Default fresh state has no chunk/shelf-produced slime, shelf work/letter/incident and log is clean. ON an actual acquired chunk shows and reaches finite expiry under enabled-time accounting. OFF/reload leaves a retained legacy chunk accounted and paused, never destroys its carrier; duplicate stack/holder transitions cannot reset enabled age.

## T15: Switch off universal targeted seal breach

Source/callers: RM_TitanoslimeChunk targetable/effect comps -> `CompTargetEffect_SlimeBreach` -> RM_SlimeBreachable target destruction/filth and piece expenditure. Default sealBreach OFF/next version. Gate action and direct effect, even if a legacy chunk is present or bomb feature ON. Do not infer campaign integration: actual campaign component is different. Current body floors and ordinary traversal cannot require this API.

Acceptance test: Default fresh state has no normal breach-capable chunk/action/breach job/letter/incident and log is clean; a retained extended target is unchanged by an OFF effect attempt. ON with normal acquired chunk and an eligible authored target exposes/executes the action with a real piece cost and hazard; unrelated buildings remain unchanged.

## T16: Switch off actual campaign chunk-to-vault interaction

Source/callers: `StructureInjectionsRUT/Defs/VaultDungeons/ThingDefs_Buildings/RUT_VaultFleshSeal.xml` -> `Source/VaultDungeons/CompFleshSeal.cs` proximity scan naming RM_TitanoslimeChunk. This consumer bypasses the generic API; gate its slime interaction with the labelled next-version setting through an appropriate scenario adapter. Do not edit that layer on this pass or remove/open the existing campaign structure. Its actual vault, plug, hazard and finite consumption integration are next-version obligations under the existing vault item; default absence means no newly acquired slime mechanism or automatic dissolution, not deleting the owner's vault.

Acceptance test: Default fresh no chunk, slime-breach job/letter/incident or proximity opening and log clean; on a disposable copy of an existing actual vault, a legacy chunk nearby cannot open the plug OFF. ON the normal advertised route is present at the actual plug, with chunk spent once, blocked path opened and contamination accounted. A substituted generic dummy cannot pass this ticket.

## T17: Decouple oomb promotion/fission from kept refuse feeding

Source/callers: `RM_Oomb.xml` uses the SAME VEF EatWeirdFood comp for customThingToEat, advanceLifeStage/advanceAfterXFeedings/defToAdvanceTo and greater fission flags. Add labelled OFF next-version control for only promotion/fission. Configure/guard local advancement/fission while leaving refuse eating and its nutrition/AI normal; do not redesign VEF or remove lesser/ordinary/greater roster entries. Refresh effective existing comp/def state when changed; saved counters pause safely. Animal replacement when enabled must provide a readable sign under no-vanishing, not silently lose a tame named identity.

Acceptance test: Default eligible oombs eat actual refuse with no promotion/replacement/offspring, promotion job/letter/incident and clean log; all roster forms still exist. ON sufficient real feeding exposes the authored advancement and tame-only split, with readable old/new identity accounting. OFF mid-count/reload preserves counters and living animal, no hidden offspring.

## T18: Next version — specify warm-ground passage marks

Deferred unbuilt presentation, with nothing to switch off and no first-version delivery obligation. `SlimeTerrain.xml` documents snow-only takeFootprints; bounded cross-source footprint/decal/Slime search found no warm-ground provider. Firm shelves, soft mats and channels remain readable without marks. If commissioned in the next version, specify the smallest transient passage-mark route using existing rendering/terrain facilities, respecting ground/floor/water ownership, visibility, save/reload and bounded buildup.

Acceptance test: none, no warm-ground renderer exists and no first-version bar needs it. A next-version commission must supply warm snow-free walk/no-walk and floor controls, reload and buildup witnesses before enabling it.

## T19: Keep the optional body overlay as a future presentation specification

Promised but absent: `Slimification.xml` explicitly leaves render-node wiring out. It is OFF/next version, not a missing default mechanic. If commissioned later, define stage/animal/humanlike/apparel layering with film/tint/drip, no eyes/buds/new limbs, and performance/visibility/reload contexts. Retain health/alert legibility independent of its renderer. Do not queue art in this pass.

Acceptance test: none, no overlay implementation or approved detailed renderer exists; current version is judged using health/alerts/impairments without it. A later commission must supply contrasting visibility/layering witnesses before enabling it.

## T20: Trace and specify deferred specialized Helix access

Promised scenario hook, delivery unknown in bounded read: `the_slime.md` Helix vendor and the universal mod brief's campaign boundary. Search existing faction/trade/research source before declaring it absent. Keep the special gene/return seller OFF/next version; do not disable ordinary Helix/vanilla traders, name a new faction, create an incident or invent a vendor prerequisite for first-version pit/compressor. Future spec must state acquisition/pricing/availability/what happens with seller absent and preserve expensive return gating.

Acceptance test: Agent trace identifies actual existing hooks or records precise absence; default fresh state has no new slime-specific Helix gene/return offer/job/letter/incident and clean log while ordinary trade remains. If built consumer is found, add an OFF gate and ON state-read contrast before enabling; until traced its ON behavioural test is unknown, not passed.

## T21: Leave the Throat experiment deferred; require a real future interaction spec

Lore promise in `the_slime.md` §7, implementation unknown after bounded local source search. This is not ordinary harvesting, a shared-engine requirement or a reason to add a planet-scale simulator. Future design must identify actual carried material, transfer/use action, possible outcomes, ownership of hazard response and legible loss; the lore intentionally does not settle its result. Keep OFF/next version with no action/quest generated by the current Slime system.

Acceptance test: none, the cross-biome experiment has no settled executable outcome or local consumer in the inspected source; no model can credibly predict its fictional result. Default source/offer state must still show no newly introduced experiment action, job, letter or incident.

## T22: Trace and deliver the retained rain-water chain

Reuse `GELATINOUSSLIME_RAIN_COLLECTION_AND_DRAINAGE_RECONCILE` for retained core, narrowed to this definition. WeatherDef/pool/campaign strip, actual loaded weather eligibility and FlowWorks `ApplyRain`, collection/storage/fluid/thirst/drainage adapters are the trace. Identify each real owned route before saying built/absent. At zero authored rainfall organism rain must be naturally eligible without changing planet rainfall or permitting meteorological Rain/FoggyRain in campaign. Deliver only missing local provider/hooks for the flood picture in definition.md: shallow accounted potable surface water on all exposed unbuilt natural slime land, including fields and crust, with normal in-place drinking and collection. No standing flood layer on floors, edifices, roofed cells, imported substrate or existing liquid channels. Retain the underlying terrain, movement/build support and contact; water alone does not kill crops or change fertility. Roof/floor additions stop further input and drain event water safely. Recession removes event water, retaining collected water and independent terrain conversion/growth writes. If shared engine APIs cannot represent this without an engine change, report the specific dependency gap rather than building a parallel solver or substituting a tint. Supply event-on/off, storage-full, layer, reload and drain semantics as in definition/M3.

Acceptance test: On authored zero-rainfall and nonzero-rainfall local fixtures the natural unlocked process can select organism rain. Read the declared flood-cell mask, visible standing water and actual water accounts before/during/after rain: exposed natural slime land, including crust and fields, holds potable water; floors, edifices, roofs, imported substrate and existing channels receive no ambient layer. Actual open collectors gain potable fluid; roof/no-event controls do not. Normal direct drinking debits the surface account and reduces thirst without an ingestion film dose; independent bare-ground contact remains active. Movement/build support and plants remain; floor/roof additions safely stop input, and recession leaves prior terrain intact except separately logged conversion/growth writes. Stored water survives. Log clean; pending-rain save/reload neither duplicates nor loses volume. Tint-only, terrain-swap, contact-shield and crop-drowning mutants fail; event forcing alone is not proof.

## T23: Implement truthful core settings and safe active-state defaults

Reuse existing settings-active-consumers ledger item, remove its current-version dependence on paid-vat acceptance except safe OFF legacy handling. `SlimeMod.cs` serialization/static reset defaults and all `SlimeSettings` consumers require a coverage map. Add absent per-major-feature core rain/production/native-special controls via existing settings toolkit; core defaults ON, each moved capability OFF/labelled next version. Hazard OFF prevents new contact and raw/liquid film doses, clears existing advanced/fast film safely; engulf OFF releases; growth OFF retains stage; no stale Dwommo pawn stat cache; farm OFF no new conversions. Production OFF stops new bills/safely cancels and returns reserved input; rain OFF prevents/ends new wetting and drains active inundation without deleting stored water; native-special OFF retains animals and stops new special actions. Preserve unrelated acquired genes/coma and paused legacy paid/temporary states. Scope labels must match actual consumers now versus local setup; no new unsupported-biome switch.

Acceptance test: Actual consumer state reads before use and mid-state for each major switch, search/reset and save/reload agree with proposed defaults. All-off leaves usable land/life baseline with no new special effects, no active extra job/letter/incident and clean log. Custom entry settings restore exactly, not to defaults. Legacy paid-vat/chunk/sample/held/film states preserve identities/resources; turning OFF never kills a person at a boundary.

## T24: Map packaged legacy ground and flora to the retained contract

Reuse the legacy-contact portion of the existing settings item. `RM_GelatinousSlime_DonorPorts.xml` has owned RM_Slime/RM_RichSlime and flora alongside the primary suite; bounded read finds no RM_SlimeTerrain tag there. Enumerate each actual inherited/loaded surface, harvested product and consumer; explicitly classify body ground versus constructed inert floor. Restore intended contact/field/forage semantics for owned authored-map surfaces without renaming saved defs or auto-tagging arbitrary third-party slime. Preserve source compatibility and later wood rule; no roster eviction or donor resurrection.

Acceptance test: Owned legacy authored-map cell/plant records produce the declared land/life/contact/harvest outcome in the same situation sweep as primary content; ordinary foreign slime-label negative remains outside guarantee. Save ids unchanged, default extras absent and clean log. A loaded tag/field read is a regression receipt, not sufficient without causal contact/crop/harvest calibration.

## T25: Make reverted-ground crop attempts fail beside productive controls

Retained specification reconciliation: `MapComponent_SlimeFieldConversion` changes zoned primary grass to rich; `SlimeTerrain.xml` rich fertility is .85, not a guarantee of failed farms. Enumerate loaded ordinary food crops and productive legacy surfaces, then attack the local terrain/zone/conversion choices to deliver the frozen no-permanent-farmland law. Choose a local conversion/substrate compatibility rule that makes an ordinary post-reversion sow-to-harvest attempt fail through substrate-caused sowing refusal or growth stop while the same crop reaches harvest on managed substrate. A lower fertility or delayed but completed harvest is insufficient; do not invent a fixed harvest/yield threshold or redesign shared growth. Preserve unzoned native forage and growth rings and avoid damage to floors/hydroponics. Growing-zone designation, not current crop presence, is the selected trigger; labels must say so.

Acceptance test: Across M2’s loaded ordinary food-crop compatibility and field/terrain regimes, read each post-reversion sow-to-harvest attempt beside the same crop on compatible imported substrate or hydroponics. The reverted plot shows substrate-caused sow refusal or growth stop and no harvest; the managed control actually reaches harvest within the observed stretch, while unzoned native forage regrows and floors remain. Incomplete comparisons are unknown: a timeout without a recorded substrate cause cannot pass. Calibrate model outcomes against T25 real crop/job/terrain/harvest receipts; a renamed or slower still-harvestable field, shared weather failure or missing sowing labour must fail. A crop already present at conversion may finish. Default growth/rain all ON, de-zoning does not restore ground, no error storm. Exact rates/yields remain checks.

## T26: Repair existing art resolver and retain necessary look witnesses

Reuse kit-numbered-animation ledger item. `check_kit_art.py` currently treats numbered Dwommo flying prefix as unresolved; actual numbered frames exist in Textures. Resolve the existing animation convention instead of requiring duplicate/nonexistent art. No art generation or blanket new style commission. Ground/life bar witnesses cover ordinary kit at play scale; exact variants/counts remain checks. Preserve the specifically owed owner in-game Titanoslime early/late-stage visual review without claiming it done or initiating unattended flight visuals.

Acceptance test: Offline resolver passes actual numbered prefix/facings and fails a planted missing frame/path; no invented asset requirement. Later authorized normal-play ground/life witness can discriminate crust/soft/liquid and ordinary organisms with real affordances; existing owner giant review remains labelled owed until actually supplied. Default extra assets need not be displayed.

## T27: Supply causal normal-action and recovery observers

Instrument required by use_body/residents/mouth/water/whole; reuse and narrow acceptance-scenes-assert-control-recover item and current validation/northstar readers. State rows need scene/tick/id/content/settings fingerprints, health/rate/sign payloads, real job start/cancel/finish and consumed ingredient ancestry, spawned/carried/held/corpse/caravan inventory, actual occupied cells, flight tracker and drink/collector/liquid ownership. Complete lossless log interval and independent entry-state restoration; missing read is UNKNOWN. Existing mock sensitivity and helper probes remain component checks, not runtime outcomes.

Acceptance test: Planted cancelled-job-as-completion, missing read, wrong id/assembly, silent death, consumed-item duplication, failed classified Titan gate, unobserved log gap and wrong restore each fail/return unknown. Authorized live branch can link normal inputs/actions to real outputs and restore exact recorded entry state independently; no direct spawn/effect helper can accept a bar.

## T28: Build the situation and clinical instrument

Implement M1 using existing production kernels/shrinker and T27 records. Include all declared early/advanced/drying/cure/raw/resistance/holder/caravan/OFF transitions and their own signs/item accounting; invalid/unsupported holders are unknown until grounded. This is an offline model plus calibration reader, not new game behaviour.

Before any M1 output counts for escape, collect running-game treatment rows separately for walking on map, in bed, downed on map bare ground, held/released and caravan. Each row records actual ordinary targeting/action availability, reach/travel, start/cancel/finish, same patient alive with cleared film, consumed antidote identity and toxic cost. For held prey, read targeting while held and, if required, witness release and subsequent ordinary helper completion. Caravan treatment must use its actual supported action, never an assumed map job. Direct effect calls and another class's success cannot fill a missing row; every uncalibrated class is UNKNOWN and blocks full-range acceptance.

Acceptance test: M1 output covers the declared state/transition regions, shrinks a failing sequence and rejects all named planted clinical mutants. Recorded actual contact/UseItem/caravan/terminal/save receipts meet M1 calibration bounds before any offline acceptance. Treatment has successful ordinary-action and delayed/cancelled controls per holder class; an omitted class or a class where treatment cannot be completed cannot be accepted by model prediction. M1 covers timing and severity only between calibrated classes; an uncalibrated wrapper branch stays UNKNOWN.

## T29: Build rain route, conservation and geometry readers

Implement M3 by reusing actual FlowWorks ownership/unit/ledger read surfaces discovered by T22. Do not assume absent undug flood behaviour; read the route and calibration first. This instrument is separate from any retained core delivery gap.

Acceptance test: M3 outputs exact composition/ownership and integral water accounting for all stated catchment/roof/storage/disable/reload regimes, matches real calibration receipts and rejects double-applied rain, wrong potable type, sky-only wetting and terrain overwrite mutants. Include direct-drink debits, exact declared flood-cell eligibility and mid-event roof/floor changes; compare retained substrate/contact/build support and live crop state through recession, accounting independent conversion/growth. Reject contact-shield, excluded-cell flooding and crop-drowning mutants. Unknown physical route stays unknown.

## T30: Build the whole-season normal-action runner

Instrument for whole: disposable existing authored full-map save, all retained settings and shared mechanics ON/defaults, natural sky/unlocked events, moved extras OFF. Use real colony work, current-world/tile fingerprints, inventory/population/terrain/liquid/log ledger, mid-compound-state save/reload and second main-action order. Source has planned scenes but not these complete normal-action assertions; search/reuse observers before adding new harness machinery. Normal tick acceleration preserves all jobs/needs/random/pulses; no rate multiplier or clear-sky shortcut.

Acceptance test: Runner rejects planted locked-sky, growth-off, immortal-colony, injected outputs, no-repeat/no-reload, missing log and incomplete recovery cases. Valid run records the full season and continuing managed routine at declared scale/orders; absence of a slow/rare cycle extends observation rather than fabricating a pass. M2 forecast alone cannot satisfy whole.

## T31: Build the coupled seasonal instrument

Implement M2 from authored-map state, production conversion and growth interfaces, M3 water receipts and M5 demand. This is the whole-mod offline model distinct from T30 real-job runner. Include native/outsider cap semantics, clone pressure, giant feeding, fields, terrain-ring connectivity and shared wet-top produce. It may not simulate different planets.

Acceptance test: M2 reproduces preregistered real event/terrain/item/population calibration and correctly flags synthetic forage desert, area takeover and population-suppressed arrivals. Include the fields bar’s paired failed post-reversion attempt, successful same-crop managed harvest and native regrowth, with real substrate-cause records; no indefinite-farming extrapolation or mere timeout can certify it. Source/settings/save fingerprints and uncertainty envelopes appear on every output; uncalibrated rainfall/AI blocks forecast acceptance, not silently assumed balance.

## T32: Build occupied-cell and held-prey transition sweep

Implement M4 against existing size/drop algorithms and source prey gates, consuming real occupied-cell/holder records from T27 and existing Titanoslime gates. No sprite-radius approximation and no shared engine redesign. Define blocked-release safety before any unsupported swallow can strand a pawn.

Acceptance test: All declared legal geometry/stage/capacity/holder/order regimes have exact occupancy and identity accounting, calibrated as M4 states. Stale registration, out-of-bounds drop, early corpse conversion and container disposal fail with a replay witness; blocked release never counts missing prey as released.

## T33: Build ordinary work and material envelope

Implement M5 from real recipe/cost/produce and T27 ordinary job records, linked to M2. Document bootstrap imports explicitly, including source wood/steel needs and no thumbstalk wood promise. A material-feasible envelope is not evidence normal jobs complete.

Acceptance test: M5 conserves actual integer materials and recorded work within calibration bounds in both action orders, flags deliberately insufficient supplies and double-counted wet-top produce, and emits the bottleneck changed by local tuning. No fixed yield/colony-size approval threshold or default hidden supply is introduced.
