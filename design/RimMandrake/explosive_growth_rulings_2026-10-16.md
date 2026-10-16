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
