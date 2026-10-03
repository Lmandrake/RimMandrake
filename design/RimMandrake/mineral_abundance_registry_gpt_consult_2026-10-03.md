# GPT consult, mineral abundance registry (2026-10-03)

gpt-6.1-sol, effort high, one consult. What was taken and rejected: `design/RimMandrake/mineral_abundance_registry_design_2026-10-03.md` §9.

**1. UNIT**

**1.1. Keep EPM as the player-facing surface unit; reject the claimed exact conversion.** “Enough steel for a base” is understandable. But EPM divided by nominal lump yield gives an attempted deposit count, not expected recovered inventory. Your 600-gold setting becomes 0.5 nominal deposits: deterministic rounding destroys the expectation. Placement failure, clipping, overlapping deposits, drop probability, difficulty and miner yield further change recovery. “Expected” and “up to” are different contracts. Use stochastic rounding, reference mining conditions, and measured generation distributions. The [scatter implementation](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/GenStep_ScatterLumpsMineable.cs) and [mining implementation](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/Mineable.cs) support these objections.

**1.2. Hilliness is a scaling policy, not available geology.** Scale by actual map area, then account for eligible substrate and maximum ore occupancy. Otherwise absolute rows become coupled through finite space and placement order. Rockless custom maps can deliver zero regardless of hilliness. Ore output per 1,000 eligible rock cells is a useful internal density and diagnostic; deposits/map is a useful secondary display. Neither handles walls, crystals and salvage seams uniformly. Value-weighted abundance creates circular dependence on your market-value normalization. Item counts also need conversion ratios before comparing raw ore, cut gems and finished metals.

**1.3. Deep and quarry need absolute units too.** A deep share says composition, not abundance; multiplying every share equally changes nothing. Display selection probability plus expected units/find and finds per reference scanner-work period. Give quarry units/100 completed jobs with explicit batch sizes. Surface EPM cannot specify quarry richness independently. EPM/year needs habitat and harvesting assumptions; salvage/trade UPY needs a defined encounter rate, travel effort and purchasing assumption.

**Recommendation:** Keep reference EPM, show a contextual map estimate, and add independent deep/quarry throughput fields. Present annual sources as conditional production or offered stock, not guaranteed acquisition.

**2. ABSORPTION**

**2.1. The strongest case for absorption is reducing the behaviour you must control.** Owning selected content lets you remove autonomous spawners, incidental drops and competing settings, stabilize defNames, and define canonical yields directly. With 634 mods, maintaining adapters around changing donor internals can cost more than maintaining a small port. “Absorption buys nothing” is therefore wrong. However, absorption closes only those donors’ paths; it cannot eliminate integrations with other consumers.

**2.2. My verdict is selective absorption:**

- **Jewelry:** control wins while its jewellery gameplay remains wanted. Absorb just the gems if retiring that dependency materially simplifies the stack. BY-NC-SA permits adaptation subject to attribution, noncommercial use and ShareAlike; renaming does not remove those obligations. [Licence terms](https://creativecommons.org/licenses/by-nc-sa/4.0/).
- **Minerals Framework/Rock/Sparkle:** control wins for the full overhaul. Its variable size, multiple products, skill-sensitive yields and environmental spawning require a substantial adapter. Small Sparkle ports win only if they actually eliminate that dependency. Rock/Sparkle permissions do not automatically license Framework code. [Framework description](https://github.com/zachary-foster/MineralsFramework), [BY-SA terms](https://creativecommons.org/licenses/by-sa/4.0/).
- **Glowstone:** control wins absent permission. No licence establishes no redistribution grant; alternatively create independent content. [GitHub licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).
- **Biomes! Fossils:** selective absorption wins if only amber/fossil seams are wanted and its exact asset/code licence permits it. Keep the donor if its broader mechanics matter.

**Recommendation:** Replace “absorb only renamed/merged materials” with “absorb small subsets that retire substantial integration burden,” with per-file licence provenance.

**3. ARCHITECTURE**

**3.1. The draft is not executable registry data.** `defs` contains prose, wildcards and promised names; `OTHER_vanilla_biomes` is not a BiomeDef. The components row omits mineables that its notes promise to disable. Combined salt/gem/material rows prevent independent settings. Introduce stable material IDs and separate exact bindings for items, producers, yields and source permissions; keep unresolved proposals outside emitted runtime defs.

**3.2. Startup zeroing plus postfixes is brittle.** Static initialization does not establish ordering against other mods’ constructors and cached dictionaries. The scanner’s original global draw still executes before your postfix, and its caller dereferences the result immediately. Use a prefix that replaces selection and explicitly handles an empty pool before deposit creation. [Scanner code](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/CompDeepScanner.cs). Quarry’s postfix is viable, but chunk fallback must reset `singleSpawn`; it also cannot prevent failure inside the original draw. Prefer replacing that specific draw call. [Quarry code](https://raw.githubusercontent.com/Ogliss/Quarry/master/1.6/Source/Quarry/Buildings/Building_Quarry.cs).

**3.3. One GenStep does not control all generation.** Forced scatter bypasses weights; later steps can add or overwrite ores. Minerals Rock can alter substrate and yields. Explicit-count scatter bypasses vanilla’s nomadic multiplier branch; gravship maps also have contextual value rules. Respect generator intent and apply factors once. [Generation code](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/GenStep_RocksFromGrid.cs). Long-range targets also need compatible destination selection.

**3.4. Coverage is not enforcement.** A dump fingerprint validates that build only. Leaving unknown minerals at vanilla behaviour contradicts exclusion guarantees. Runtime validation needs an explicit unsupported-source policy; miscellaneous stuff categories cannot prove every production path is covered.

**3.5. Preserve saves and define settings semantics.** Keep old defNames until migrating stacks, stuff references and deep grids. Existing deposits remain unchanged. Cache pools by biome/channel/settings revision; rebuild live pools on edits. Def/cache mutation may require restart. Sparse absolute overrides preserve edited values; arithmetic deltas do not.

**Recommendation:** Keep CSV → XML, but build one policy service with explicit source adapters. Pilot surface/deep/quarry across representative seeds and save reloads before claiming universal coverage.