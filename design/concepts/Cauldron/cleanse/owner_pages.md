# Page one — what I propose the Cauldron becomes

The Cauldron is a wet mineral forest in permanent dusk, with rainless lightning and chemical pools that cannot simply be drunk. Its vents quiet before a metal-heavy bloom, giving workers time to shelter or seal themselves before exposure leaves lasting harm. Capping that same chemistry turns combustible danger into collected condensate and useful supplies, so preparation earns dependable work while outdoor expeditions remain risky.

Land: distinguishable dark soils, mineral trunks, chemical fog and condensation, rainless storms, acidic air and actually hazardous pools.

Life: mineral-bearing native bodies read at ordinary zoom; owner-kept imports remain exceptions. The cast feeds, breeds, hunts and supplies useful harvests; flyers fly, rhossak bind, and natives drink their environmental water. No evictions.

Signature: heed the vent warning, protect workers, then cap and refine the same dangerous chemistry into useful supplies.

Runner-up: rhossak forest renewal. It is another complete cycle, so seeding and grove-rooting move; binding and edible galls stay.

My next-version list, all switched off:

- Dew beads and weather-swapped plant colours.
- Shore nettle spread and vent flower gardens.
- Fexxil venom and kissaveth toxic leaks.
- Suush and garsulix explosive behaviours; native hush and its suush hover rule.
- Zisska fire-spit and bedbug paralysis.
- Vexxiss water poisoning, fire policing, vent drinking, prying and tracking.
- Dressed ruins, rig-study discovery and Oomo shrine.
- Bespoke plate-only door, upgraded machines and ship corrosion/lining.
- Rhossak seeding/rooting, ossrith uranium refining and the additional trunk-age coat.

Ordinary research, basic tap/Filter-Works, suits, liquid vessels, material protection, truthful timber assay and existing mineral flecks stay. Their code must be separated from the moved features. Your previous keeps remain future promises; these are my version decisions, not your rejection of them.

I recommend retiring the alternative-world scorer/rarity option because worldgen is forbidden in every version; the Cauldron scanner payload because inspection already supplies its information; and periodic manufactured crystalmit bricks because they duplicate stonecutting. Nothing is retired here. The scorer becomes inert; the other recommendations stay off pending your decision. Mineral feeding stays.

Counts: capabilities 82 before, capabilities 83 after splitting hush into its own row; 54 retained, 26 next-version and 3 recommended retirements. The census expands the earlier inventory’s 68 rows by splitting bundled behaviours and naming dependencies [measured: record.json inventory; cleanse/census.json]. Before: 18 bars, all 18 assigned a runtime tier [measured: tree.json]; that old tree does not distinguish bridge-readable from look-only. After: 10 bars, 4 live-only bars, now including mineral-body readability. The rest use causal state reads or calibrated models. There are 12 checks and 15 attackable build rules. No new yield, stat or art-variant count is a passing bar.

# Page two — what to check

These are my defaults, derived from your recorded answers and the source:

- “Dusk” means diffuse dim weather tint, not fixed brightness; “wet” needs fog/dewfall and existing art, not moved decorations. Shared Direct Sun governs heat; vents are chemical.
- “About an hour” measures warning-to-bloom, separately from sky interpolation and first dose. Puffs and timed text suffice; capped/absent sources use text. Native hush/hover moves off. Flight visuals remain owner-present only; no flight images.
- “Sealed” uses the same final vacuum/environmental-resistance stats for acid and bloom; full non-gear sources count too. Item immunity stays a build rule. Direct liquid and smoke remain separate.
- “Persistent” means no natural metal clearance. “Advanced medicine” means industrial or higher for a dedicated purge, including hidden traces: craft from selvix herbal harvest and cloth/neutroamine bought with reagent through ordinary orbital trade. Finite setup stock and trade gaps enter the model; ordinary tending never purges.
- Permanent acid harm means actual lasting facial/sensory consequences after ordinary healing, not a scar label. Exceptional restoration remains possible.
- Toxic and acid water keep their actual chemistry through ordinary transfer. A coloured pool or injected tank proves nothing about delivered water.
- Connected gas crosses water; maintained empty gaps and sealed corners stop combustion. Reload must preserve the active flame front, not merely gas bytes.
- Deferring the ruined rig requires ordinary research to remain reachable. Deferring machine upgrades must leave suits and containers available.
- “Animals are minerals” means visibly mineral-bearing native bodies; imports keep their forms. “Life twists” includes lasting metal/acid harm, not another mutation system. Renewal cannot rescue seasonal ecology.
- “Expeditions” means on-map errands beyond shelter; “runaway gas” means connected gas continually invading normal work routes.

No questions: the contrary evidence concerns construction and unrun measurement, rather than a reason to choose a different experience.

Models specified, first-to-build first:

- Situation generator: enumerate reachable states, transitions, controls and recovery.
- Gas geometry and save walk: expose corner leaks and lost active fronts.
- Coupled season and work model: find gas, ecology, illness and labour feedback failures.
- Liquid ledger and interruption walk: find chemistry changes and missing/duplicated stock.
- Exposure and treatment state walk: separate prevention, persistent load, real purge and lasting acid injury.

There are 6 unknown grouped interactions, covered by those 5 models; the 39 tickets cover switch-offs, missing mechanics and instruments. Models are predictions until checked against actual game traces. The complete system must still run through a season, reload midway and repeat the main work in another order with weather, needs and damage active.

Unsettled delivery: natural metal decay, sealing, warning timing, pool binding, active combustion saves, and coupled seasonal balance need implementation or measurement. No live proof was performed. These convergence fixes await verification. The whole bar now explicitly refuses goods relocation without a visible gas explosion and visible throwing. Nothing changes the mod until the review and your application decision; the build hold stays.

## Still refused after the second look (the reviewer's words)

The proposal cannot be applied until each of these is resolved or you accept it.

- the converge fix broke an entry it changed (the verifier's words) (bars.json bars/living_cast). range.varies now says 'Mineral-body reading covers the retained native forms at ordinary zoom under the declared weather; admitted owner-kept imports are explicit appearance exceptions'. Reject[2] fails the bar when 'The native cast looks like ordinary unmineralised fauna'. But several retained natives that are not named as imports have no mineral body in their own defs. Suush is 'A translucent globe that floats above the ground' (RM_CauldronFauna.xml:112). Eskith is 'A knee-high animal with broad, feathered foot pads' (:493). Rhossak is 'grown from tightly wound living roots' (RM_Rhossak.xml:101). The bedbug is 'An oversized insect' (RM_BedBug.xml:22). The new ambiguity entry rules out 'a promised new art system', and definition.md says 'this proposal makes no import eviction or art redo'. So the range demands mineral bodies on forms that, by their own design, have none. The bar would then need new art, which the proposal forbids, or it cannot pass. That breaks the changed entry under cannot_hold_together. Would pass: living_cast declares which retained natives carry the mineral-body reading (for example zisska, vexxiss, crystalmit, ossrith) and which natives keep non-mineral forms as stated exceptions alongside the imports, or it scopes the reading to the cast as a whole, with no new art required. Smallest fix: Rewrite the range sentence to name the mineral-bodied natives, and list suush, eskith, rhossak and bedbug (or whichever apply) as non-mineral exceptions with a reason, matching the figurative stands_for.
- the converge fix broke an entry it changed (the verifier's words) (tickets.md T39: Switch off native_hush). The eskith's shipped in-game description says 'Their sudden silence is a good reason to get under a roof.' (RM_CauldronFauna.xml:493). With faunaHushEnabled off by default, eskith no longer fall silent before a bloom, so the default game tells the player about a warning that never comes. T39's Work gates only 'the call, count and hush inspect wording'. It never mentions this description, and the census eskith row keeps 'ordinary animal behaviour/art' unchanged. Hush is now a moved extra, but the shipped lore text still promises it. That fits contradicts_ruling_or_lore (and moved_extra_relied_on, in player-facing text). Would pass: With hush off at defaults, no shipped description or tooltip promises native silence before a bloom; the hush wording returns only with the opt-in. Smallest fix: Add to T39's Work and acceptance test: make the eskith description's silence clause conditional on faunaHushEnabled, or reword it for the default.
