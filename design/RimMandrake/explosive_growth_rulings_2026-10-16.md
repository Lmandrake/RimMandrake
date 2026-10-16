# Explosive growth: owner rulings from the design-pass review (2026-10-16)

Cards put by BENCH from `explosive_growth_consensus_2026-10-16.md` (C/W/T lines),
`explosive_growth_bench_design_pass_2026-10-16.md` (H/SP/HW/WP/EC/BC/PF/GM lines) and the GPT review
`explosive_growth_gpt_review_2026-10-16.md`. His words are verbatim; the "means" line is BENCH's reading.

## Round 1 (11:40 PDT)

| card | his answer | means |
|---|---|---|
| C6 how slow is dry | card: **Tenth speed (×0.1)** | dry ground growth factor 0.1 |
| WP2 dormancy | card: **Yes, age at the slowed rate** | ageing scales with the growth factor below 1 (GPT: adjust age BEFORE the mortality check, never a postfix subtraction) |
| C2 peak maturity | *"When you say "ordinary" what do you mean? A Typical plant on this world's dry biomes will quickly grow, might produce fruit, make many sprouts, and possibly rupture (die impressively). The wet biomes grow less swiftly, fruit prolifically, and then wither with just a few sprouts."* | two archetypes, not one "ordinary" plant. **Dry-biome natives** on water: fast growth, maybe fruit, MANY sprouts, maybe rupture. **Wet-biome natives**: slower growth, prolific fruit, then wither leaving a FEW sprouts. |
| C4 crops and vanilla plants | *"Settable in options. Vanilla crops may function normally, or (default) they simply don't grow unless there's water nearby. But the local plants blow past them in this biome. Our plants should have similar settings: either they simply grow normally in other biomes, or they do the same x10 when watered or x0.1 when dry elsewhere too."* | Mod Setting for vanilla crops: normal, or (DEFAULT) no growth without water nearby; our natives always outgrow them here. A second Mod Setting for our plants outside our biomes: vanilla-normal, or the same ×10 watered / ×0.1 dry rule. |

## Round 2 (12:00 PDT)

| card | his answer | means |
|---|---|---|
| C1 wet jungles at home | card: **×4, always** | wet-biome natives run ×4 at home; "less swiftly" than dry natives on fresh water (×10) |
| WP3 rainy biomes | *"Answer is (1), but Twilight Sea is a sea floor... no rain."* | Webwork and Contagion natives are the wet-biome kind. Twilight Sea's `<Rain>4</Rain>` is a defect, filed `TWILIGHT_SEA_FIX_IT_RAINS_UNDERWATER` (the design pass's "17% rain" was read off that defect) |
| C3 rupture | *"1 in 3. Nobody "irrigates" a field on this world, that's a huge amount of water loss. You share some water, they grow, you leave it there. A rare flood or rainstorm is transformative and crisis-driving. Some plants are 1 in 1. Some plants (groundcover) never rupture, and a few others. So exceptions will be declared as we go forward. That's why we need this on for each biome review. Pyrelands grass does not rupture but does grow violently quickly and spread itself super-fast."* | default rupture chance 1 in 3 for dry-biome natives on fresh water; per-plant override (1 in 1 for some; 0 for groundcover and others), declared at each biome's review sheet (a rupture column there). Watering is SHARING water, not irrigation: small, then left. Floods and storms are the crisis-scale events. Pyrelands grass: no rupture, violent growth and very fast spread |
| H1 hydroponics | card: **Watered, normal vanilla speed** | basins and pots are their own water source: vanilla speed, no bonus |

## Round 3 (12:05 PDT)

| card | his answer | means |
|---|---|---|
| WP1 natural water in dry biomes | *"In the Utinni scenario, only Flooded Canyon has that flood, and only select biomes ever get rain. Otherwise no. Outside of Utinni, that was what my comment centered around previously."* | Utinni campaign: no new desert rain and no flash floods; the Flooded Canyon flood is the only natural flood, and rain stays on the biomes that already have it. Outside Utinni, his round-2 "a rare flood or rainstorm is transformative and crisis-driving" is the frame |
| W3/EC2 when is water fresh again | *"It always counts as fresh as long as it's there. It's continuous."* | NO settle-to-×4 and no re-arm timer: while water is present the ground is fresh, continuously (×10 for dry natives). Retires the consensus's settled-wet state for player water and the burst-vs-steady problem with it |
| W4/HW1 sharing water | *"Hose + carried + sprinklers"* | all three: hose spill, a carried-water job, and sprinklers (source question asked in round 4) |
| W2 riverbank | *"(1) and the plants continuously grow and writhe there"* | only the water and mud cells themselves count; plants there grow and churn continuously |

## Light (12:28 PDT, typed)

*"And of course the plants ONLY grow like this while there is light. On the Utinni world, this is always or never true. On other worlds it will cycle."*

Means: the ×10 (and all water-driven growth) applies only while the cell has light. Ash'karr is tidally locked, so a
cell is permanently lit or permanently dark; on other worlds it follows the day/night cycle. (Vanilla already stops
growth below its light threshold; our factor must not bypass that, and dark-side cells never get the show.)

## Round 4 (12:35 PDT)

| card | his answer | means |
|---|---|---|
| SP1 sprinkler source | *"Let's define what sprinklers should do first, then adapt VFE and our own together. VFE should incorporate some kind of bold automation and enhancement, whereas the native one should be pretty rudimentary (just sprinklers set on pipes)"* | a sprinkler design comes first (filed `SPRINKLERS_DESIGN_PIPES_THEN_PANACHE`); ours is rudimentary (sprinkler heads on FlowWorks pipes); VFE's gets bold automation and enhancement; both adapted together |
| churn | card: **Yes, endlessly while wet and lit** | a dry-biome native on wet, lit ground cycles forever: ×10 to maturity, then fruit + sprouts, or rupture (1 in 3) |
| EC1 wood plants | *"(1) but we need to renormalize EVERYTHING anyway"* | anything yielding logs grows at the slower tree rate; AND a planet-wide yield/growth renormalization is owed (filed `PLANT_ECONOMY_RENORMALIZE_EVERYTHING_AT_ONCE`) |
| PF1 whole-map wave | *"Try (2) then fallback to (3) if we have to "* | first build: every plant on the map puts on the show; if it misses the perf bar, stagger it over about a day |

## Round 5 (12:45 PDT)

| card | his answer | means |
|---|---|---|
| EC3 crop fruit drop | *"A full harvest but the water gets used up. That's the cost."* | a self-fruiting watered crop drops a full harvest, and the cycle CONSUMES the water on its cell; water, not yield, is the price |
| GM1 seeing wet ground | *"Nothing stays wet for long without an obvious reason."* | no overlay and no wet-soil terrain: wet ground is always explained by visible water (a pipe, hose, spill, channel, river, flood); water is used up, so wetness does not linger unexplained |
| T2 other liquids | card: **Only for adapted plants** | clean water works for all; slime, red water etc. only for plants marked to use them, declared per biome at its review sheet |
| C5 Pyrelands refuel | card: **A burnt cell counts as fresh** | ash flush: fire-adapted plants run as freshly watered on burnt ground for a few days |
