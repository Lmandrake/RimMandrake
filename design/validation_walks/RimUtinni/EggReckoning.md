# RimUtinni: The Reckoning (EggReckoning) — validation walk
subject: src/RimUtinni/EggReckoning  (packageId `mandrake.rut.eggreckoning`)
deps: `mandrake.rm.biomes` (the composed biomes mod; Webwork, which ships the egg and the spider, is folded into it), `mandrake.rut.patches` (the Hutt Cartel faction)
list: a tier carrying RimUtinni Patches + the composed biomes mod + The Reckoning, all five DLCs, plain open map; the offer chain also needs a world with a Cartel settlement within 80 tiles
status-hint: WEBWORK_EGG_RECKONING_QUEST_1 — "The Reckoning", a debtor's outpost with three ways to close the debt: pay the Cartel, defeat the outpost, or plant an ollathrix egg undetected. Script: `src/RimUtinni/EggReckoning/validation.py`, first script EGG_RECKONING_FIRST_SCRIPT_1. NEVER RUN LIVE.

Sources: `About/About.xml` (rulings 2, 3, 6, 7 quoted), `Source/EggReckoningSettings.cs`, `Source/RM_QuestPart_EggHatch.cs`, `Source/RM_QuestPart_EggPlantWatcher.cs`, `Source/RM_QuestNode_GetHuttCartelSettlement.cs`, `Defs/QuestScriptDefs/RUT_Reckoning.xml`, `Defs/HistoryEventDefs/`, and Webwork's `RM_OllathrixEgg.xml`.

## must be true
- Every def the mod ships (the rumor and Cartel-offer quest routes, the three history events) resolves in the running game; a nonexistent control reads absent so the probe can say no. → defs_resolve.shipped_defs_resolve, defs_resolve.control_absent_def_reads_absent
- Every def the C# looks up by name resolves (the egg, the spider kind and thing, the Hutt Cartel faction); a missing one is a silent no-op in the mod. → defs_resolve.defs_the_code_looks_up_resolve
- The Mod Settings field `reckoningEnabled` round-trips. → flip_reckoningEnabled.reckoningEnabled_round_trips
- A run leaves every setting at its shipped default. → settings_restored.all_settings_at_shipped_defaults
- With the toggle on, the rumor route sits in the random quest pool at weight 0.15 and the Cartel offer is trader-given, not randomly selectable (the load-time patcher leaves both as shipped). → route_wiring.toggle_on_leaves_the_rumor_route_in_the_pool, route_wiring.toggle_on_leaves_the_cartel_offer_trader_given_and_not_random
- With the toggle off, neither route can be offered again (rumor weight 0, offer given by nobody), and a Reckoning already granted is untouched. → UNCOVERED: the patcher runs only from the mod's WriteSettings and at startup, and no bridge tool calls it after flipping the static field (a companion `[Tool]` calling `EggReckoningPatcher.Apply` is owed); chain route_wiring.toggle_off_removes_both_routes records UNMEASURED
- The Cartel offer generates a quest that offers the egg path, when the world has a Cartel settlement in reach. → quest_offer.cartel_offer_generates_when_the_world_allows
- The egg never hatches outside the quest (rulings 2 and 7: no hatcher on the shared item, nothing but the quest's own part spawns the spider): an egg left on a plain map for an hour is still an egg and no spider exists. → egg_guard.site_ready_egg_and_colonist, egg_guard.egg_stays_an_egg_and_no_spider_appears
- Path 1: paying the Cartel silver through a trade request closes the debt at about twice the base reward. → UNCOVERED: no bridge tool answers a trade request; chain path_pay_the_cartel.trade_request_silver_closes_the_debt records UNMEASURED
- Path 2: defeating the outpost in the open completes the quest and costs the outpost faction 8 goodwill. → UNCOVERED: needs the site map and its garrison killed; chain path_defeat_the_outpost.all_enemies_defeated_completes_and_costs_goodwill records UNMEASURED
- Path 3: an egg planted undetected inside the outpost hatches in the 23:00-02:00 window. → UNCOVERED: needs the outpost map, the plant watcher's signals and a night; chain path_plant_the_egg.undetected_egg_hatches_in_the_night_window records UNMEASURED
- The hatched spider is the one RM_Ollathrix kind at a fixed age of 4.0 years and hostile (manhunter), a real losable animal. → UNCOVERED: needs the hatch part to fire; chain hatch_juvenile_hostile.hatched_spider_is_a_four_year_old_manhunter records UNMEASURED
- Discovery before the hatch (3 percent per hour) costs 25 goodwill and an undiscovered kill costs none (total deniability). → UNCOVERED: needs the live site and a goodwill read; chain discovery_cost.found_egg_costs_goodwill_and_undiscovered_kill_costs_none records UNMEASURED
- The constants the walk quotes (4.0 years, 3 percent, 23-2 night window, route weights) match the source. → UNCOVERED: source facts, checked offline by `static_checks()` rather than in a live chain

## anti-guessing notes
RULED OUT: "flipping `reckoningEnabled` through the bridge zeroes the rumor weight" — the patcher runs from `WriteSettings` and at startup only; `jawa/mod_settings_field` writes the static field without calling either, so the off-state is UNMEASURED, never read as a dead toggle.
RULED OUT: "a quest row with no text proves the egg path is not offered" — a row without description text is UNMEASURED for that line.
RULED OUT: "an egg that vanishes in an hour hatched" — it carries a 15-day rot timer and no hatcher; a missing egg with no spider is UNMEASURED, a spider is the only FAIL.
RULED OUT: "the outpost's target is a real placed pawn" — it is a flavour-only generated villager never placed on the map (About.xml, mechanism gaps); no check looks for it.

## north star
state: DRAFT
validated-hash:

DRAFT, binds nothing. This mod has no owner-ruled experience bars yet; the intended-function lines above are the functional script's coverage and are agent-owned.
