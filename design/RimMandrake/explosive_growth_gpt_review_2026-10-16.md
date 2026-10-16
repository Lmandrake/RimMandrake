Date: 2026-10-16
Model: GPT via gpt_consult.py (codex.exe, default model, effort high)
Inputs: design/RimMandrake/explosive_growth_consensus_2026-10-16.md, design/RimMandrake/explosive_growth_bench_design_pass_2026-10-16.md

**Neither proposal is ready to implement unchanged.** The bench catches important omissions, but its timer arithmetic, aging patch, yield fix and rain cap introduce further problems.

References: **C** = consensus document; **B** = bench design pass. Mod-specific counts and dump results below are accepted as reported, not independently reproduced.

**(1) Findings, ranked**

| Severity | Finding and required correction | Doc citations |
|---|---|---|
| **Critical** | **The moisture state machine is incomplete.** `wetSince` means continuous wetness, but resets only after a qualifying fresh event. Rewatering after a short dry gap therefore retains a broken “continuous” interval. Specify transitions for every wet/dry/source combination; separate continuous wet duration from fresh-event eligibility. | C §§4.3–4.4; B §7 |
| **Critical** | **Fruit and harvest can spend the same crop twice.** Full yield followed by 60% growth preserves substantial harvest value. Bench’s half-yield fix still grants 50% output for only 40% growth loss, bypasses sowing and harvest work, and leaves the jackpot interaction unspecified. Use a shared production budget, or exclude cultivated crops from automatic drops. `harvestedThingDef` also includes medicine, textiles and other products—not just fruit. | C §§3.5–3.6; B §§3,6; EC3 |
| **High** | **Dormancy is needed, but the proposed patch is unsafe.** Subtracting age in a postfix can happen after vanilla has applied old-age damage or destroyed the plant. Adjust the age increment before mortality evaluation; preserve fractional aging. Use the moisture slowdown, never total `GrowthRate`, or darkness/blight could suspend aging. | B §§0.1,4; Δ19 |
| **High** | **Bench overstates its aging evidence.** Its own figures say only 8/358 fail on ideal soil at ×0.25; “most” applies to the poor-ground scenario. Lifespan is the start of deterioration, not necessarily the instant of death. Scaling age to ×0.25 extends finite lifespan fourfold; it does not mean “never wither.” The lifespan formula itself is supported by [PlantProperties](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/PlantProperties.cs). | B §§0.1,4; WP2 |
| **High** | **Pulse arithmetic is wrong, and the fix is underspecified.** Three wet days plus five dry days averages **(30 + 1.25)/8 = ×3.90625**, not ×4.6. Growth-only break-even is **4.8 dry days**, assuming the stated model. Six days is conservative, not the mathematical minimum. The cooldown must gate renewed ×10 **and** tops; fruit/jackpot income requires a separate comparison. A moving average alone proves nothing without equations. | C W3, §4.4; B §§0.3,7 |
| **High** | **Hydroponics needs explicit treatment, but ×4 is another major economy decision.** Bench’s own estimate gives roughly 2.6 basin cells per colonist before practical losses. “Today already does this” does not establish balance. Class inheritance alone also cannot establish whether a grower supplies water; define active/inactive behavior and explicit grower overrides. | C §4.3; B §1; H1 |
| **High** | **The water economy has no enforceable resource budget.** Hand watering receives litres; channels and hoses receive duration without specified consumption. A tiny retained channel volume could sustain many cells indefinitely. Natural banks may intentionally be free, but artificial irrigation needs volume, throughput, coverage and evaporation rules. Dev Soak Zones cannot solve player access. | C §§4.2,5.2; B §§2–3 |
| **High** | **Rain waves are a gameplay hazard, not merely a benchmark.** At 15%, 2,000 eligible plants imply about 300 bursts. An injury ceiling per burst does not prevent overlapping damage, repeated knockdowns or indirect deaths. “Sometimes” needs limits on aggregate exposure and explicit hazardous species. | C §§3.5,4.4; B §§5,9 |
| **High** | **WP3 replaces plant identity with a biome shortcut.** A species can occur in both rainy and dry biomes. Membership in any rainy biome would globally reclassify it; “at home ×10” then reinstates biome-dependent growth. Weather weights also do not establish rainfall frequency or two-day dry intervals. Use explicit species traits and observed wet history. | C §§3.2,6.4; B §§4–5,8 |
| **High** | **“Per plant per event” conflicts with cell-owned `lastTopEvent`.** Replanting, harvesting, sprouts and moved plants distinguish those semantics. Conversely, plant-only eligibility can let replacement crops repeatedly claim one ongoing event. Specify both plant identity and any cell/event production cap; save them deterministically. | C §§3.5,7 Δ4; B §9.1–2 |
| **High** | **Rain cannot be represented correctly by `lastWaterRainTick` plus the current roof alone.** That loses exposure history, dry gaps and overlapping local sources. Unroofing after rain must not retroactively water a previously sheltered cell. Define rain event intervals and roof-change semantics without eagerly writing the whole map. | C §§4.2–4.3; B §9 |
| **High** | **The major performance costs remain.** Plant growth uses `TickLong`; adding plant `Tick`/`TickRare` hooks will not supply the intended cadence. Keep `GrowthRate` reads pure, including inspect-pane reads. Discover eligibility through long ticks; schedule active tells separately. Lazy moisture decay does not remove irrigation/snow scans, arming, mesh rebuilds, item spawning or sprout work. | C §8; B §9 |
| **High** | **Permanent-water caching has precedence and invalidation holes.** A filled channel classified as permanent terrain can immediately suppress its intended fresh event. Removing one source must preserve overlapping sources. Terrain changes, temporary-overlay removal and fluid identity all matter; batch dirty neighbourhoods rather than recomputing them repeatedly during floods. | C §§4.2,5.4; A15; B §9.5 |
| **High** | **The fire flush may expire on empty ground.** Fire kills plants; ×10 does not create replacements. A three-day buff can end before the spawner supplies a sprout. Fuel also depends on growth/biomass, so growth and density are separate controls but not ecologically independent. | C C5, §§6.2–6.4; B §8 |
| **High** | **Wood classification and exemptions conflict.** Bench’s slower wood rate does not fix the reported 43 logs/cell/day fungus. Cave-fungus exemption may also bypass that rate entirely. Define precedence, retain structural tree classification, add explicit wood-product classification, and fix fast-producer yields before release. | C §§3.2–3.3; B §§0.5,6 |
| **Medium** | **Several vanilla claims are too absolute.** Fertility-zero terrain can support plants with `completelyIgnoreFertility`; vanilla explicitly accommodates water plants. Thus “water has no plants,” “fertility-zero grows nothing” and “density zero means no plants ever” need qualifications. Growth can also alter actual standing populations indirectly through mortality and disturbance. [Spawner source](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/WildPlantSpawner.cs). | C §§5.1,5.4,6.2; B §10 |
| **Medium** | **Bench confuses a C# default with vanilla crop definitions.** Rice/potato/corn fertility minimum 0.7 is not evidence of a mod patch from 0.9; the crop XML already overrides the class default. Sand remains unsuitable, but the attribution is wrong. [Crop definitions](https://github.com/RimWorld-zh/RimWorld-Core/blob/master/Core/Defs/ThingDefs_Plants/Plants_Cultivated_Farm.xml). | B §6.1 |
| **Medium** | **Flood and snow sources require survival/cause checks.** Plants have a `destroyedByFlooding` property: hooking the terrain overlay does not guarantee surviving plants to accelerate. Falling snow depth can result from clearing, not melt; air above freezing alone is insufficient evidence. Avoid counting warm snowfall and its later melt twice. [Plant properties](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/PlantProperties.cs). | C §§4.2,5.5; B §§5,10 |
| **Medium** | **Yield and labour figures are idealized upper bounds.** Work amounts are modified by pawn work speed; hauling, collection, failures, cooking, harvest delays and replanting matter. At ×10, daily harvest scheduling can become the bottleneck. Raw nutrition production is not a complete colonist-feeding calculation. | B §§1,3,6 |
| **Medium** | **Density classes are not “slight” tuning.** Gelatinous Slime regrow 6→15 is 2.5× slower; Wasteland 15→25 is 67% slower. Map Designer’s transformed density/regrowth pair is not generally equivalent to the authored pair because density calculations cap locally. Validate authored and effective values separately. | C §§6.4,9 C7; B §8 |
| **Medium** | **Scope and chemistry remain contradictory.** “Our plants” conflicts with automatically including imported crops. Slime waters through fluid/terrain rules but is excluded from bench’s rain list. Contagion bloom/red water and boiling-water classifications differ across sections. Publish one precedence table for species scope, source chemistry and terrain state. | C §§3.2,3.7,4.2,5.3; A4/A14; B §§4–5 |
| **Low** | **Small engineering claims need correction.** A moisture byte still needs timestamps, source persistence and event state. Radius two is 25 cells only for a square neighbourhood. The 10% sparse/dense threshold and 300-plant cap are proposals requiring measurement, not established optima. | B §§7,9 |

**(2–3) One recommendation per card line**

Option numbers refer to the original card. **Δ** explicitly marks a difference from Bench. For C/W/T cards, Bench sometimes leaves the consensus recommendation standing rather than expressly endorsing it.

| Card | Recommended option | One-line reason / difference from Bench |
|---|---|---|
| C1 | **2 — permanently wet ×4, including jungles** | **Δ:** removes the permanent ×10 home-biome exception and gives “reduced” a consistent meaning. |
| C2 | **Custom — opt-in fruiting species survive; explicit drop budget** | **Δ:** no universal `harvestedThingDef` payout or arbitrary 60% reset. |
| C3 | **Custom — explicitly named burst species; bounded overlapping harm** | **Δ:** reject blanket 15% rolls across all dry-adapted flora. |
| C4 | **3 — imported plants/crops remain vanilla by default** | **Δ:** preserves native-plant scope and a playable standalone start; broader rules remain opt-in. |
| C5 | **2, refined — fire-adapted species retain ×4; tune refill separately** | **Δ:** avoids spending a short fire-triggered buff on empty cells. |
| C6 | **2 — ×0.25, with proper dormancy** | Retains visible waiting without making the still-slower ×0.1 the default. |
| C7 | **2 — classes initially apply to new biomes only** | **Δ:** audit existing biomes against presets before changing established ecology. |
| W1 | **1, refined — liquid water rain can create fresh events** | Growth responds everywhere exposed; hazardous outcomes follow species and event limits. |
| W2 | **2, refined — two-cell fresh-water bank radius** | Explicit geometry and source precedence prevent channels becoming instantly permanent. |
| W3 | **Custom — three-day fresh window, six dry days to renew it** | **Δ:** use explicit timers; eligibility gates both ×10 renewal and tops. |
| W4 | **1 — metered hose watering** | Implements a concrete source with actual water consumption and bounded coverage. |
| T1 | **1 — moisture state, no terrain substitution** | Keeps fertility/pathing stable; use the overlay for visibility. |
| T2 | **Custom — species-specific liquid compatibility** | **Δ:** plain water defaults yes; slime/red water require explicit adaptation, hot liquids temperature checks. |
| H1 | **Custom — supplied growers self-water at ×1 mod multiplier** | **Δ:** retain vanilla fertility benefits without automatically quadrupling basin output. |
| SP1 | **1 — no automatic moisture integration** | Keep VFE behavior separate; explain the interaction in its tooltip. |
| HW1 | **1, refined — zone watering with measured consumption** | Agree on the job shape; litres and labour figures remain tuning hypotheses. |
| WP1 | **3 — local natural watering event** | **Δ:** showcases wild awakening without changing every desert’s weather. |
| WP2 | **1, corrected — dormancy adjusts age before mortality** | Agree on intent; reject postfix age subtraction and indefinite-life wording. |
| WP3 | **Custom — explicit species traits, independent of native-biome lists** | **Δ:** rainy weather does not automatically make every native species permanently ×10. |
| EC1 | **1, refined — tree OR explicit woody-product classification** | Retain tree handling, fix exemptions, and complete fast-fungus yield corrections before shipping. |
| EC2 | **3 — six-day re-arm using explicit timers** | **Δ:** simpler and testable; additionally gate speed renewal and audit total yield. |
| EC3 | **3 — cultivated crops never auto-drop harvests** | **Δ:** eliminates free crop harvesting; farmers still see accelerated growth and tells. |
| BC1 | **Custom — descriptive water-regime labels only** | **Δ:** labels validate content; they do not determine genetics or veto actual weather. |
| BC2 | **1 — authored values checked against shared presets** | Also validate effective values after Map Designer and other startup patches. |
| PF1 | **Custom — bounded, deterministic spatial sample** | **Δ:** cap actual rain tops independently of colony buildings; budget cosmetic work separately. |
| GM1 | **1 — moisture overlay plus inspect explanation** | Show source, remaining duration, fresh eligibility and effective growth multiplier. |
| GM2 | **1, corrected — actual natural melt waters ground once** | Exclude clearing and double counting; budget detection rather than scanning indiscriminately. |

**(4) Missing options/card lines**

| Add | Decision needed |
|---|---|
| **Authority / scope** | Explicitly supersede earlier ×4/×10 rulings; separate native-flora behavior from imported-crop settings. |
| **Rate matrix / precedence** | Every class × moisture state × grower state; resolve exemptions, wood factors, home habitat and contamination. |
| **Top lifecycle** | Maturity crossing versus already mature; plants born during an event; harvest/cut/destruction cancellation; pending tops after drying. |
| **Production budget** | Shared harvest/top accounting, difficulty and yield modifiers, jackpot interaction, product eligibility and sprout costs. |
| **Burst safety** | Damage stacking, repeat stun immunity, friendly fields, fire chains, buildings and maximum local event density. |
| **Water budget / access** | Litres, retained volume, evaporation, pipe throughput and a viable standalone watering route without FlowWorks. |
| **Drought integration** | Stack, replace or exempt by moisture source; patch the drought factor directly rather than dividing the final growth result. |
| **Suppression semantics** | Separate growth suppression from physical drying; grazing beside a river should not silently erase the river’s water supply. |
| **Save migration / determinism** | Convert existing soak/charge saves; preserve event identities and rolls; define settings changes and master-switch behavior. |
| **Performance acceptance** | Fixed-seed paired benchmarks covering TPS, frame stalls, mesh work, item/sprout counts, source churn and save/load size on multiple map sizes. |