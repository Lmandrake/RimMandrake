**My pick: batched A first, D for automation, C for bulk logistics.** B is viable if the owner accepts its vessel interpretation. The review improves the design, but several corrections overreach.

I used the inlined files only. Their project-code measurements remain reported evidence; I could not independently audit those files or certify an installed RimWorld 1.6 build.

**Claims and re-measurements**

- **★1–2, gathering and missing slime containers:** the review’s callee-chain inspection and extension-based XML census are stronger methods. Its findings support the design, but neither establishes runtime behavior. “Any liquid” must mean **any liquid with a compatible container form**, excluding the reportedly unbottled slimes.
- **★3, three jobs per bottle:** plausible for the reported current, unbatched implementation, before hauling. It does **not** describe A after A’s proposed batch washing.
- **★4, traffic arithmetic:** at the requested **3 L/day**, 1.5 L bottles mean two drinks daily, six at sustained 3× heat. Ten pawns therefore require:

| Arrangement | Jobs/day, before hauling |
|---|---:|
| Individual drink/fill/wash | 180 |
| A, washing batches of ten | 126 |
| A, filling and washing batches of ten | 72 |
| Pipe-fed B | 60 |

  These assume full batches and full 1.5 L consumption per drink. The review correctly calculates **2.4 L/day** from a 3 L need capacity falling 0.8/day—also consistent with emptying in 1.25 days. Eight hours at half consumption gives **1.33 bottles/day**. Its 25–30 drinks for ten pawns is plausible under its chosen heat assumptions, but **“overstated 2.4×” compares different scenarios**, not an arithmetic error. An afternoon temperature cannot establish daily demand without the temperature history, clothing, and pawn comfort limits.

  Three stocked bottles equal **4.5 L: 1.5 days at 3 L/day, half a day at 3×**. A 208 L barrel supplies 138 complete 1.5 L drinks plus 1 L, not 139 complete drinks. Procurement and decanting may add jobs.

- **★8, green slime:** reported separate definitions establish that the implementations are distinct. They cannot settle whether the owner intends the substances to become identical.
- **Vanilla names:** `Ascetic`, `Tough`, `Undergrounder`, `Cannibal`, `StrongStomach`, `RobustDigestion`, `Neanderthal`, `Dirtmole`, and `Waster` are valid vanilla identifiers/categories as listed. Published [trait XML](https://raw.githubusercontent.com/RimWorld-zh/RimWorld-Core/master/Core/Defs/TraitDefs/Traits_Singular.xml) and [gene localization data](https://www.madxingjin.tech/git/SiteAdmin/RimWorld-ChineseSimplified/src/commit/d4572c48baf30180baab963e61e83ae2ac2658e3/Biotech/DefInjected/GeneDef/GeneDefs_Misc.xml) corroborate the traits/genes; exact 1.6 xenotype gene membership remains unchecked here.
- **Behavior is separate from existence:** Strong stomach prevents food poisoning; robust digestion concerns raw-food efficiency/taste. Neither automatically implies indifference to taps. Tough concerns damage; Undergrounder concerns underground living. Those exemptions require owner judgment.
- **Claim 6 is misleading:** even if Cannibal alone appears in the inspected XML nullification list, Ascetic bypasses taste thoughts in [FoodUtility](https://raw.githubusercontent.com/josh-m/RW-Decompile/master/RimWorld/FoodUtility.cs). An XML-only census is not a complete behavioral audit.
- **Claim 11 needs narrowing:** hunger can cause ordinary breaks through mood; food binge exists but is not evidence of a direct starvation-threshold trigger. Broader need-driven mental states have precedent: chemical withdrawal selects a hediff stage that supplies [mental-state givers](https://raw.githubusercontent.com/RimWorld-zh/RimWorld-Core/master/Core/Defs/Drugs/Psychite_Yayo.xml). “Vanilla has none” is too broad.

The review’s sprinkler comparison is **wrong**: 350 L divided by its quoted **25–45 L for ten pawns** equals 8–14 *ten-pawn colonies*, or roughly **78–140 pawns**. The reserve recommendation remains sound.

**Options**

**A — bottles capped.** Best initial scope. Batch both filling and washing; count inventory and committed production; use refill hysteresis. A stock cap limits surplus, not steady consumption. Select sources by the complete collection route, rather than blindly preferring the container’s nearest source. Measure walking and work ticks alongside job counts.

**B — stations.** Strong spatial gameplay, with queues, throughput, and outage fallback needing design. **Owner judgment:** cups beside a tap plausibly satisfy the intended “proper drinking vessel” comfort, but extend the literal bottle wording. The review fairly flags that; predicting refusal is unsupported. Actual refillable bottles used at stations would satisfy the wording more directly.

**C — network tiers.** Best bulk framework, compatible with either A, B, or D. Add drinking reserves, explicit authorization for non-potable intake, partial-container conservation, and pressure/outage behavior. Vessel roles should be defaults: emergency exceptions are useful.

**D — bottler.** Strong automation upgrade preserving literal bottles. Its claimed superiority is unmeasured: scattered dirty bottles may prevent efficient hauling batches. Specify empty-bottle supply, washing water, energy, output limits, maintenance, and manual fallback. Count bottled stock when allocating reserves; bottling should not indefinitely drain emergency water.

**Additional options none reached:** a pawn-owned reusable bottle refilled and drunk within one job; tray/crate exchange depots supporting genuine batch returns; scheduled barrel delivery to disconnected outposts; or optional abstract household water service while retaining physical bulk transport.

**Shared corrections:** classification, authorization, and transport should be separate. One source adapter should cover registered liquids, terrain-only slime, and other water items. Temporary reservations must not immediately unlock slime. Recheck potable availability before ingestion. Flammability does not establish nutrition or “fire belly”; contact damage does not establish ingestion effects. Dubs flags alone do not demonstrate compliance across terrain, tanks, thoughts, and fallback behavior.

**Owner judgment:** a pond being debuff-free does not logically require every pawn to prefer a distant pond over a nearby tap. The review’s reordered ladder is a preference proposal, not a textual correction. Likewise, technical separation of green slime leaves its intended identity open.

**Merged owner decisions**

1. Must comfortable drinking use an actual bottle, or do cups and equipped stations qualify? What about ponds, pipe taps, buckets, and barrels?
2. Which traits, active genes, xenotypes, wild people, tribal cultures, or Jawas qualify for exemptions? Do exemptions also soften slime disgust?
3. What counts as available potable water: distance, danger, zones, forbidden stock, temporary reservations, frozen supplies, or water elsewhere on-map?
4. Which slimes—including biome/mod slimes—are drinkable, what does each do, and may they be bottled?
5. Can thirst alone trigger salt drinking? Must potable water be unavailable? Which salt sources qualify, and how should relief, recovery, and repeat episodes work?
6. How should toxic water, cooled boiling water, ice/snow, and blood behave?
7. What rules apply to animals, babies, prisoners, visitors, raiders, and caravans?
8. Do bills, intake settings, or designations authorize continuing non-potable collection and machine loading?
9. Does drinking take priority over crops, washing, and machines, and how large is the reserve?
10. Which adapted crops need watering, what volumes, does brine harm them, and can buckets fight fires?
11. Which rulings must also work with Dubs?
12. Which logistics progression, default settings, labor-time budget, and emergency fallbacks should ship?

I would implement the shared behavior rules and batched A, protect reserves, then add D and C’s ports. Choose B instead of D if the owner accepts station vessels.