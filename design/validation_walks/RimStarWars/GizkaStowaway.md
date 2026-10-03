# RimStarWars: Gizka Stowaway — validation walk
subject: src/RimStarWars/GizkaStowaway  (packageId `mandrake.rsw.gizkastowaway`)
deps: `brrainz.harmony` (hard); the creature is the donor's `Gizka` (`mlie.starwarsanimalcollection`) or SWBestiary's `RSW_Gizka` — loadAfter, soft, and the donor patches are FindMod-guarded
list: minimal tier plus a gizka source
status-hint: GIZKA_STOWAWAY_FIRST_SCRIPT_1 — first script drafted, never run live

Sources: `src/RimStarWars/GizkaStowaway/About/About.xml` description, `Defs/**`, `Patches/RSW_GizkaDonorPatches.xml`, `Source/*.cs`.

## must be true
- Every def the mod ships (fecundity and bait-poison hediffs, bait item and recipe, cull thought) loads and resolves; a bogus name reads notFound. → defs_resolve.every_shipped_def_resolves
- The fecundity hediff's custom comp type loaded rather than being dropped. → defs_resolve.fecundity_comp_type_loaded
- Every Mod Settings field (`stowawayEventsEnabled`, `discoveryFrequency`, `triggerGravship`, `triggerSalvage`, `triggerTrade`, `triggerQuest`, `breedingRate`, `populationCap`, `chewingEnabled`, `cullGuiltEnabled`, `globalBreedingRate`) round-trips. → settings_roundtrip.stowawayEventsEnabled_round_trips, settings_roundtrip.discoveryFrequency_round_trips, settings_roundtrip.triggerGravship_round_trips, settings_roundtrip.triggerSalvage_round_trips, settings_roundtrip.triggerTrade_round_trips, settings_roundtrip.triggerQuest_round_trips, settings_roundtrip.breedingRate_round_trips, settings_roundtrip.populationCap_round_trips, settings_roundtrip.chewingEnabled_round_trips, settings_roundtrip.cullGuiltEnabled_round_trips, settings_roundtrip.globalBreedingRate_round_trips
- The four discovery hooks (gravship landing, wreck deconstruction, completed trade, quest end) and the cull hook are attached to the engine methods by this mod. → harmony_wiring.Scenario_PostGravshipLanded_patched_by_this_mod, harmony_wiring.Thing_Destroy_patched_by_this_mod, harmony_wiring.TradeDeal_TryExecute_patched_by_this_mod, harmony_wiring.Quest_End_patched_by_this_mod, harmony_wiring.Pawn_Kill_patched_by_this_mod
- A gizka given the fecundity hediff carries it; one not given it does not (event lineage is per pawn, not per def). → fecundity_state.gizka_with_fecundity_carries_it_control_does_not
- The poison bait's payload hediff advances on a gizka. → bait_poison.poison_hediff_advances_on_a_gizka (defs: bait_poison.bait_item_and_recipe_resolve)
- The donor gizka's MarketValue is flattened to 15 so the scam never becomes income. → donor_patch.gizka_market_value_flattened_to_15
- A gravship landing delivers exactly one tame gizka with a letter. → mechanics_unmeasured.gravship_landing_delivers_one_tame_gizka (UNMEASURED: needs a real landing)
- Salvage, trade and quest completion each can deliver one. → mechanics_unmeasured.salvage_trade_quest_hooks_deliver (UNMEASURED: driven events and rolls)
- Event-lineage gizka replicate only while fed and warm. → mechanics_unmeasured.fecundity_replicates_while_fed_and_warm (UNMEASURED: game days)
- Replication stops at the population cap. → mechanics_unmeasured.population_cap_stops_breeding (UNMEASURED: needs a grown colony)
- The Infestation stage chews powered buildings in a shared room. → mechanics_unmeasured.infestation_stage_chews_powered_buildings (UNMEASURED: needs the stage)
- Venting the room below the breeding gate stalls replication. → mechanics_unmeasured.cold_below_breeding_gate_stalls_replication (UNMEASURED: no verb sets room temperature)
- Culling weighs on witnesses. → mechanics_unmeasured.cull_weighs_on_watching_colonists (UNMEASURED: needs a slaughter with witnesses)
- The global breeding slider rescales the donor's egg-layer fields from a captured baseline. → mechanics_unmeasured.global_breeding_slider_rescales_donor_fields (UNMEASURED: no reader for the live fields)
- The creature art and sounds. → UNCOVERED: owned by the donor mod, not this one

## the walk
1. [D] `jawa/get_defs` over every def derived from `Defs/**/*.xml`: `foundCount` equals the request, `notFound` empty; a bogus def reads notFound   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on every public field of `RSW_GizkaSettings` (instance fields)   # settings_roundtrip
3. [D] `jawa/harmony_patches` for each of the five patched methods, owner `mandrake.rsw.gizkastowaway`   # harmony_wiring
4. [B] spawn a gizka at the live map centre, `jawa/pawn_health add` the hediff, `jawa/pawn_get`; a control gizka   # fecundity_state, bait_poison
5. [D] `jawa/get_defs ThingDef/<gizka> statBases deep`: MarketValue 15   # donor_patch
X. [S] (human pass) the first stowaway letter and the swarm at each stage read as funny and then as a problem; owner decides.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "gizka reproduction runs on gestationPeriodDays / litterSizeCurve" — the donor is an egg layer and PawnUtility.Mated routes it to CompEggLayer.Fertilize; those race fields are inert (Patches/RSW_GizkaDonorPatches.xml header). No check reads them.
RULED OUT: "a stowaway is a storyteller incident" — the design rejects it; static_checks fails if any IncidentDef ships.
RULED OUT: "the gizka def exists in every tier" — the donor is a soft dependency; the donor-patch and state checks read UNMEASURED when no gizka PawnKindDef resolves, never PASS.
