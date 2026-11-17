# Page one — what the Sump becomes

The Sump is a cold, flat black basin under permanent dry dusk, with solid glassy ground between pools of tar. Its waxy plants feed without sunlight, and its seated animals forage, hunt and can be tamed among the margins. Crossing raw tar slows and dirties workers; choosing routes and supplying solvent lets an established colony keep working without becoming clean everywhere.

Land: readable deep pools, shallow margins, cooled sheets, usable building ground and dusk; no rain or special sun heat.

Life: keep the seated plants and animals, ordinary food/products/taming, native tar movement, home-liquid hydration and real flight. No roster eviction. Plain mice and kethrel stay when their custom systems are off.

Signature: tar exposure creates lasting movement/work costs, answered by routes and supplied worker cleanup. Your experience sentence also promises “hides all”: I consciously defer that playable concealment with archive excavation, the runner-up. Readable deep/shallow land does not fulfil the archive promise. The frozen sheet calls excavation core; I sequence it under your later smaller-first-version instruction, preserving its future rulings.

These are my delegated scope decisions for Design Version 0.1.0. Nothing changes until review and your decision.

Next version, switched off:

- Excavation, traps, archive finds and artifact research.
- Dormant beast, evacuation warning and solvent weapon.
- Military moat, fuse post and special smoke wall.
- Scripted belch and changing ecological clues.
- Mouse tracks, gas/treasure indicators and false floors.
- Custom mound/guard/attraction ecology.
- Kethrel scrap shell, pickup and molt.
- Capstan, friendly towing and salvage winch.
- Vault storage, solvent extraction and pitch-aged food.
- Collected gas, warbling lamps and discovery unlocks.
- Harmless glasswalk slips and scanner payloads.
- Already-deferred Sinking/effigy rites; inhabited additions and visiting-giant proposals.

I recommend retiring the separate duckboards because wooden flooring already provides their behaviour, and the arrival letter because it teaches clues that do not work in this version. Both stay parked off. Active biome scoring/world mutators contradict no-worldgen: never enable them. Tar rain, wick and brommet remain prior cuts. The neighbouring Holy Flame idol is untouched.

Counts: 80 capabilities in the expanded census; 38 kept, including dependencies and instruments; 36 next version; 6 retirement/exclusion rows, including prior cuts. Bars: 0 before, 7 proposed. Live-only bars: 0 before, 4 proposed. Before-bar counts come from the empty concept tree; census totals and all after-counts are in result.json. Bodies and optional behaviours are counted separately.

Gameplay proof is missing or stale: 51 tickets, 13 regression checks, 12 build rules and 9 unknown shared-state meetings. These are not passing bars.

# Page two — what to check

The consequential readings I took:

- “Every action / slow to surrender”: lasting tar costs and real removal, not command vetoes.
- “Slow to burn”: persistent burning once lit, not delayed ignition or instantly spent fuel; shared-fire compatibility needs measurement.
- “Stinking”: oily reek in terrain description, without an odor hazard.
- “Flat black basin”: low skyline, irregular shores and some non-black vegetated margins; tar/sheets dominate.
- “Dusk”: dry visible weather under the fixed world's geometry; Direct Sun stays shared.
- “Chemotroph”: actual growth without a sunlamp, subject to ambient cold and the enabled growth engine.
- “Native life”: bodies/movement stay; shell, clue and trap systems move.
- “Automatic”: standing work policy, physical reachable solvent and no repeated individual medical bills.
- “Cleaned”: clear carried tar as well as the health label; otherwise the next scan reapplies it.
- “Never fouls”: glasswalk rejects floor deposits; it does not magically clean dirty boots.
- “Solvent supply”: current ordinary broodmother wax, not unbuilt mounds or an invented trader.
- “Same reaction”: chemistry can dissipate; bottled gas stays deferred.
- “Off”: stop producers, jobs and delayed callbacks, preserving saved bodies and goods.
- “No moat”: special defence is off; ordinary FlowWorks physics still run.
- “Season”: normal coupled ticking through growth, work and reload; no clear sky or disabled-mechanic shortcut.

Colonists drink carried FlowWorks fresh-water bottles/barrels, filled off-site and transported by caravan. Budget finite stock for the entire run; continued residence requires player-arranged imports. No local water source or guaranteed trader is promised.

Imported non-native livestock cannot be sustained: the frozen Sump bans water terrain, and the owner’s thirst ruling requires animals to drink terrain only (thirst_bottles_design_2026-10-16.md, OQ-5). I retain both rulings; native tame animals drink tar. Non-native dehydration must remain visible. This limits the reviewer’s requested water fix.

No new questions; no waiver or earlier trap/evacuation answer is reopened.

Models specified, first to build first:

- Situation walk: enumerate contact, dirty boots, recovery, reservations, death, disable and save boundaries; expose false cures and late callbacks.
- Whole map: couple land/life/work, finite drinking-water cargo and persistent tar fire; calibrate against an actual complete run.
- Route geometry: sweep legal placements/bearings, connected margins, path cost and accepting cleanup surfaces.
- Solvent queue: locate supply and labour regimes where recovery helps or monopolizes the colony.

Models need agreement with actual game records. Ordinary AI, complete colony operation, terrain/sky legibility and native animal/flight state still require game readings.

Growth/populations, solvent throughput, recovery across glasswalk/reload and source-fed fire remain unknown meetings with instruments. Native hydration needs tar binding; growth needs resolved-profile reads; tracking is campaign-patched; the cleaning recipe leaves carried tar. Water provenance, transport capacity and the full-duration budget need proof. Missing proof cannot count as a pass.

The fresh review found omitted experience phrases, undefined water supply and unmarked figurative words. This revision addresses them and records the non-native water conflict. Second-look acceptance and gameplay remain unclaimed.

## Still refused after the second look (the reviewer's words)

The proposal cannot be applied until each of these is resolved or you accept it.

- a kept mechanic with no definition (definition.md §Using it / §What changes in the colony's story; bars.json B6; tickets.md T40; census.json row routine_cleaning). routine_cleaning is built: absent, fate needed_by signature, and B6 depends on it. It is defined only as "the player's standing cleaning/work priorities and solvent-reserve policy" (definition.md) and "an enable/reserve policy" (T40). Several things are left open. Which work type does the job. What triggers it: carried tar, or a given RM_Tarred stage. Whether the tarred pawn cleans itself or "an available helper/pawn" does it. Where it happens: definition.md says "a stocked cleanup station matter[s]", but no census row, ticket or building is a station. What the "reserve policy" actually is: a Mod Setting, a stockpile or a per-pawn toggle. The source answer this cites (design/RimMandrake/designer_codex_2026-11-09/TheSump/ANSWERS_OWNER.md: "workers clean ... on their own; he plans routes ... and spends scarce solvent") splits what workers do unprompted from what he spends, and the proposal never says on which side automatic solvent use falls. Two builders would make two different mods: a self-queued scrub surgery, or a new WorkGiver at a station. Would pass: One paragraph that fixes the routine's work type, trigger, actor (self or helper), place (any clean accepting cell, or a named building) and the player control that decides when scarce solvent is spent as opposed to ordinary unprompted cleaning, mirrored in T40's specification and acceptance test. Smallest fix: Add that paragraph to definition.md §Using it and to T40. Delete "stocked cleanup station" unless a building is commissioned, and state which side of his ANSWERS_OWNER split automatic solvent use sits on.
- a sourced core promise omitted or weakened (bars.json B3 says and range; definition.md §When it goes wrong ("Natural deep tar is impassable to ordinary ground walkers")). The owner-starred mouse promise is "run easily over the tar without a thought" (the_sump.md §4), "Mice run the black" (§5), and "Mice run the tar without a thought. Nothing else touches it" (§1, repeated in the RM_TheSump BiomeDef description). B3 narrows this to "mice cross shallow tar without colonist mire". Its range lists only "mouse shallow crossings", while the definition makes deep tar impassable and gives mice no exception. Census native_tar_crossing even names a "tar-cost/entry exemption", entry being what deep tar needs. Deferring the mouse-line instrument (T23) does not require shrinking where mice run. Would pass: B3 and its range cover mice crossing the tar, deep pools included, at their ordinary pace while colonists cannot. Or a marked, delegated argument for excluding deep tar, with the biome description corrected so it does not promise more. Smallest fix: Change B3's "shallow tar" to "the tar, shallow and deep", add deep-pool mouse crossings to B3's range and T44's acceptance test, and add a mouse exception to the definition's deep-tar sentence.
- a contradiction with a standing ruling or the lore (census.json row dusk_weather (fate land); bars.json R10; ambiguities.md row "Permanent dusk" ("No special sun value")). The kept land row includes a "biome glow multiplier and sunlight-stat suppression". The BiomeDef sets BiomeGlowMultiplierExtension glowMultiplier 0.55 and suppressSunlightStatAffecter true (RM_TheSump_Biome.xml:175-177). EnvironmentalHazards' BiomeGlowMultiplierExtension.cs describes the flag as making a biome "permanently sunless rather than merely dim". That is a per-biome sun override. Standing ruling, 2026-10-19 card (standing_rulings.md:156): "no biome-specific heat, no biome-specific sun. It's a matter of geometry". The proposal also says "No special sun value" and "under the fixed world's geometry" while keeping both biome-specific sun fields unexamined. The site's sun is already −10.6° below the horizon (the_sump.md §0), so geometry alone may give the dusk. Would pass: Either the dusk is defined as coming from the fixed site's geometric sun angle, with the glow multiplier and sunlight suppression moved out of land; or a written argument that a light-only multiplier is not a "sun" under that ruling, with the suppress flag's effect named and shown to touch no Direct Sun or heat path. Smallest fix: Name both fields in dusk_weather and R10 and decide each: drop them, or argue them past the Direct Sun ruling. Remove "No special sun value" if they stay.
- a rule or check dressed as a bar (bars.json B7 accept picture "Settlers drink carried fresh water ... the declared expedition stock lasts through the run ..."; B3 accept picture "... settlers drink carried fresh-water bottles or draw from imported fresh-water barrels"). "The declared expedition stock lasts through the run" holds by construction: T51 and B7's range tell the tester to budget cargo for "the complete 60-day-or-longer declared horizon ... contingency reserve" and to "Extend the finite budget if the run extends". That is R12, our provisioning rule, and C10's debit reconciliation. It is a test-setup condition, not something the player experiences, and it cannot fail because of the mod. B3 is an animal bar, and its says names no humanlike drinking, yet its accept picture puts settler bottle drinking in as a pass condition. Would pass: Water provisioning sits in R12, B7's sees.start and C10. B7's picture keeps only what the player sees: settlers drink carried water with thirst on and no pond, while natives drink at the tar. B3's pictures are about animals only, with the humanlike case kept as a sees.control. Smallest fix: Cut "the declared expedition stock lasts through the run" from B7's accept picture. Cut the settler clause from B3's accept picture and move it to B3's sees.control.
- a figurative word unmarked (bars.json B4 says ("carries tar home"); B6 says ("standing work orders")). "home" in B4 is not literal: the accept picture means any accepting floor, not RimWorld's Home area or the base. "standing work orders" in B6 is not a RimWorld object: vanilla has work priorities and bills, and a reader could take a single repeating bill as a standing order. Neither word is in its bar's figurative list. B4 lists only "burden", B6 lists only "burden". Would pass: Each word is either listed as figurative, with what it stands for and an accept picture that departs from the literal reading, or replaced with literal words. Smallest fix: In B4 write "carries tar onto accepting floors". In B6 write "following work priorities and the colony's solvent setting", or add both words to the figurative lists with stands_for and accept pictures.
