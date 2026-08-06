# Factory Lore

## RimWorld 1.6 — Vanilla Furniture Expanded: Factory layout research and modular optimization guide

**File:** `Factory_lore.md`  
**Scope:** Vanilla Furniture Expanded — Factory for RimWorld 1.6  
**Compiled:** 2026-08-06

---

## Executive finding

No publicly documented player build was found that can be verified as operating **all 18 factory machines, the full conveyor-routing system, extraction, farming, aquatic production, stock-target bills, heatsinks, and maximum overclocking** in one coherent layout.

The strongest available evidence consists of:

1. The official Workshop description and five official capability infographics.
2. The official release post and promotional screenshots.
3. A complete video rundown that demonstrates the system as a sequence of machines and logistics components.
4. Player-built specialist installations, especially the overclocked drill/reactor loop and chemfuel-generator feed network.
5. Current community reports exposing practical routing limitations, particularly splitter behavior, lack of priority routing, storage integration, heat, and output bursts.

The best all-capability design is therefore a **modular factory campus** rather than a single tangled belt hall. Each cell should have independent inputs, outputs, bill targets, thermal control, and an isolation switch, with a warehouse bus connecting the cells.

**Evidence:** [S1], [S2], [S3], [S4], [S5], [S6], [S7]

---

## Evidence terminology

- **Documented mechanic** — directly stated or shown by the mod authors.
- **Player observation** — reported from an operating player build; useful but not authoritative.
- **Design inference** — an optimization derived from the documented mechanics and player observations. It is not claimed to be an official rule.

---

# 1. System-wide design rules

## 1.1 Prefer cells over one universal belt web

**Documented mechanics**

- Factories are physically large, consume substantial power, and produce increasing heat when overclocked.
- Conveyors automatically form mergers and splitters, support filters and underground sections, and can deposit into hoppers or ordinary shelves.
- Items on belts can still deteriorate or spoil.
- The Factory Floor is required beneath factory buildings and has only **80% movement speed**.

**Observed limitations**

- Players report difficulty predicting automatically formed intersections.
- The current routing system has no reliable priority splitter for “feed the machine first, then send excess to storage.”
- Mixed-resource systems can clog with abundant materials such as steel.
- Long shared chemfuel networks can distribute fuel unevenly.

**Recommended optimization — design inference**

Use one production cell per tightly related process chain. Give each cell:

- A small receiving buffer.
- Filtered input hoppers.
- One or more machines.
- A dedicated output hopper or shelf.
- A short outbound belt to the central warehouse.
- A local power switch.
- Its own heat-management plan.
- Space for at least one future parallel machine.

Avoid a colony-wide belt carrying every material. Use separate trunks for:

1. Raw minerals and chunks.
2. Organic feedstocks and corpses.
3. Food ingredients.
4. Textiles.
5. Components and advanced materials.
6. Finished goods.
7. Chemfuel, unless a pipe-network mod is used.

**Evidence:** [S1], [S2A], [S3], [S6], [S7]

---

## 1.2 Use stock-target bills as the primary flow controller

The factories use the familiar bill interface and support production targets such as **Do until you have X** and **Do forever**.

**Recommended optimization — design inference**

Use stock targets rather than unrestricted continuous production for nearly every finished or intermediate product. This reduces:

- Belt congestion.
- Input starvation in downstream cells.
- Unnecessary heat and power draw.
- Excess wealth from unused manufactured goods.
- Food spoilage and medicine/drug overproduction.

Reserve **Do forever** for true sinks or strategic bulk processes, such as stone-block processing, corpse destruction, or an intentionally continuous resource drill.

**Evidence:** [S1], [S3]

---

## 1.3 Treat 500% overclocking as surge capacity

**Documented mechanics**

- Most factories can normally be overclocked up to 200%.
- Each Factory Booster extends maximum overclock by 100 percentage points.
- A factory can link to as many as three boosters, permitting 500%.
- Work speed rises linearly, but heat and power consumption rise exponentially.
- A Factory Heatsink reduces linked factory heat output by 25%; as many as four can link to a factory.
- Both boosters and heatsinks have a link radius of 9.9 tiles.

**Player observation**

A player ran an Automated Drill Platform at 500% with three boosters and reported approximately 5 kW demand, major heat output, and enough burst production to justify numerous output hoppers. Another player reported that eight 500% drills produced more resources than the colony could practically use.

**Recommended optimization — design inference**

- Run routine production at the lowest overclock that meets demand.
- Reserve 500% for short, supervised bursts.
- Put boosters on the accessible side of a machine and heatsinks toward the shared utility spine.
- Do not design the base electrical system around every machine operating at 500% simultaneously.
- Give high-output machines larger output buffers before increasing their speed.

**Evidence:** [S2E], [S5]

---

## 1.4 Separate hot, dirty, perishable, and high-value logistics

**Recommended zoning — design inference**

| Zone | Keep together | Keep away from |
|---|---|---|
| Hot industry | Alloy forge, smelter, crematorium, drill | Food storage, hospitals, bedrooms |
| Perishable food | Oven, cannery, refrigerated raw buffers | Crematorium, corpse lines, outdoor belt exposure |
| Chemical production | Biofuel refinery, neutroamine synthesizer, chemfuel storage | Ignition sources and uncontrolled traffic |
| Precision production | Assembler, medicine granulator, machining bay | Shared low-priority bulk-material belts |
| Disposal | Crematorium and rejected-item filters | Any belt that can merge back into production |

Because belt contents remain subject to deterioration and spoilage, refrigerated or roofed staging remains relevant even in an automated factory.

**Evidence:** [S1], [S2A–S2D]

---

# 2. Recommended all-capability campus

```text
                         CENTRAL FINISHED-GOODS WAREHOUSE
                                      ▲
                                      │
       ┌──────────────────────────────┼──────────────────────────────┐
       │                              │                              │
  FOOD CELL                    PRECISION CELL                 TEXTILE/AMMO CELL
 oven/cannery/              assembler/medicine/               autoloom/press
   distillery                  machining bay
       ▲                              ▲                              ▲
       │                              │                              │
 ORGANIC PROCESSING ─────── ADVANCED MATERIALS ───────────── METAL BUFFER
 mincer/refinery/             alloy forge/neutro                 ▲
 crematorium                                                     │
       ▲                                                         │
       │                                                   BULK PROCESSING
 FARM/FISH CELL                                            smelter/masonry
       ▲                                                         ▲
       └────────────────── RAW EXTRACTION CELL ───────────────────┘
                         autofarmer/drill/fishfarm

A parallel UTILITY SPINE carries power switching, boosters, heatsinks,
ventilation access, firebreaks, and maintenance corridors.
```

This topology uses every native production capability while keeping the most failure-prone logistics localized.

---

# 3. Cell-by-cell layout and optimization

## Cell A — Raw extraction and cultivation

### Machines

| Machine | Footprint | Inputs / outputs | Primary capability |
|---|---:|---:|---|
| Autofarmer | 3×7 | Zoned field / rear deposit | Automated sowing and harvesting |
| Automated Drill Platform | 3×3 | 0 / 1 | Stone chunks or random metals |
| Automated Fishfarm | 3×3 | 0 / 1 | Breeds locally present fish; Odyssey required |

### A1. Autofarmer

**Documented mechanics**

- Operates across a configurable rectangular zone.
- Sowing and harvesting can be independently enabled.
- Auto-cycle can trigger when 90% of crops in its zone reach full growth.
- It can sow only plants requiring no Plant skill.
- If rear hoppers are present, harvest is deposited behind the machine.

**Recommended optimization — design inference**

- Orient the machine so its rear deposit edge faces a covered hopper gallery.
- Use long, simple rectangular plots rather than irregular fields.
- Separate sowing-only and harvesting-only behavior when seasonal timing matters.
- Feed harvested crops into filtered trunks: food, hops, textile crops, and chemfuel feedstock should not share one unrestricted belt.
- Leave direct pawn access around the long sides because the required Factory Floor slows movement.

**Current caveat**

Workshop comments report that several common crops may be unavailable to the Autofarmer despite being ordinary outdoor crops. Treat crop compatibility as something to test in the active mod list rather than assume.

**Evidence:** [S2A], [S7]

### A2. Automated Drill Platform

**Documented mechanics**

- Requires no material input and has one output.
- Can drill for a selected stone chunk or random metals.
- Random-metal yield depends on local deep-resource composition.
- Base machine footprint is compact, but overclocking greatly increases power and heat.

**Player-proven optimization**

The “Uroboros” build couples the drill with VFE Power nuclear generation: three boosters permit 500% operation, while multiple hoppers absorb output bursts. The player isolates or exploits the resulting heat.

**Recommended optimization — design inference**

- Give the drill a **dedicated output belt** rather than merging directly into a mixed factory bus.
- Provide several hoppers or a large local storage buffer before 500% use.
- Place the drill in a separately vented room or biome-appropriate heat-recovery area.
- Use filters after the first buffer to divide uranium, steel-bearing resources, stone chunks, and other metals.
- Scale power generation before installing the third booster.
- One or two controlled drills are generally easier to exploit than a large permanently overclocked bank.

**Evidence:** [S2A], [S5]

### A3. Automated Fishfarm

**Documented mechanics**

- Must be built on shallow water containing fish.
- Breeds only fish types locally present.
- Stops producing during a gill-rot event.
- Has no input and one output.

**Player/community observations**

- Players report apparent local fish depletion or placement restrictions when adding multiple farms.
- The “Buffs and Tweaks” patch author considered the base fishfarm underpowered even after doubling its process speed.
- A Workshop response suggests using a fish-repopulation machine when local stocks become a problem.

**Recommended optimization — design inference**

- Reserve and validate the whole planned shoreline footprint before starting production.
- Place output hoppers on dry, roofed ground adjacent to the water.
- Route fish directly to a refrigerated buffer, oven, or cannery.
- Treat the fishfarm as a supplemental specialty-food line rather than the sole colony food engine until its throughput is tested.
- Do not share its output belt with unrefrigerated industrial goods.

**Evidence:** [S2C], [S7], [S9]

---

## Cell B — Bulk mineral and waste processing

### Machines

| Machine | Footprint | Inputs / outputs | Primary capability |
|---|---:|---:|---|
| Automated Smelter | 3×4 | 3 / 1 | Slag, weapons, apparel, chunks, mechanoid corpses |
| Automated Masonry Saw | 3×3 | 1 / 1 | Stone chunks to blocks |
| Automated Mincer | 3×3 | 1 / 1 | Corpses to processed mince |
| Conveyor Crematorium | 3×3 | 1 / 0 | Destroys corpses, apparel, weapons, and drugs |
| Automated Biofuel Refinery | 3×4 | 3 / 1 | Wood or organic matter to chemfuel |

### B1. Automated Smelter

**Documented mechanics**

The smelter accepts several distinct input categories and can process slag, weapons, apparel, stone chunks, and mechanoid corpses.

**Recommended optimization — design inference**

- Use separate filtered input spurs for slag/chunks, tainted equipment, and mechanoid corpses.
- Do not feed every category through one uncontrolled mixed trunk.
- Send the output to a metal buffer shared with the assembler and alloy forge.
- Use stock-target bills where applicable so low-value equipment does not monopolize the machine.
- Place it in the hot-industry room; its base heat is higher than most Basic Factory machines.

**Evidence:** [S2B]

### B2. Automated Masonry Saw

**Documented mechanics**

The saw has one input and one output and cuts any accepted stone chunk into blocks.

**Recommended optimization — design inference**

- Give the saw a dedicated chunk hopper.
- Filter the output by block type at the warehouse rather than complicating the input line.
- Use one continuously available machine for ordinary construction demand; add a second only for megaprojects or export.
- Place it close to the drill output and exterior chunk stockpile, not near the finished-goods warehouse.

**Evidence:** [S2B]

### B3. Automated Mincer

**Documented mechanics**

The mincer converts animal, human, or insectoid corpses into processed mince. It has one input and one output.

**Recommended optimization — design inference**

- Create explicit corpse filters before the mincer and crematorium diverge.
- Keep the corpse receiving zone cold until the machine can process it.
- Use a dedicated output hopper because processed mince is food and must not rejoin the corpse belt.
- Route acceptable mince toward the oven or cannery; route forbidden corpses toward the crematorium.
- Verify ideology consequences before enabling human processing.

**Evidence:** [S1], [S2B]

### B4. Conveyor Crematorium

**Documented mechanics**

The crematorium is a terminal machine with one input and no output. It can destroy animal corpses, human corpses, apparel, weapons, and drugs.

**Recommended optimization — design inference**

- Put it at the absolute end of a disposal line.
- Never place it on a belt that can merge back into a production trunk.
- Use filters immediately before the terminal belt.
- Give the disposal cell a manual inspection tile or bypass shelf for valuable items mistakenly routed there.
- Isolate its substantial heat from refrigerated corpse storage.

**Evidence:** [S2C]

### B5. Automated Biofuel Refinery

**Documented mechanics**

The refinery converts wood or organic material into chemfuel and has three input positions and one output.

**Player observations**

- A large branched belt feeding many chemfuel generators can require flooding the line before every generator receives fuel.
- Players report inconsistent refueling and power fluctuation when production is not overwhelming.
- A conveyor becomes a refueling port when it terminates directly against a refuelable building; players report that corner terminations may not work reliably.
- Several players recommend Vanilla Chemfuel Expanded pipes as a lower-friction alternative for generator distribution.

**Recommended optimization — design inference**

- Use a short chemfuel output line into a secure buffer.
- For native conveyor refueling, terminate **straight belt stubs** directly against each consumer.
- Avoid one long equal-split tree serving many generators.
- Prefer several small, independent generator branches over a single massive network.
- Where permitted by the mod list, a chemfuel pipe system is the cleaner bulk-distribution layer; retain belts for solid feedstock.
- Keep chemfuel production and storage physically separated from the hottest machines.

**Evidence:** [S2B], [S6]

---

## Cell C — Food production and preservation

### Machines

| Machine | Footprint | Inputs / outputs | Primary capability |
|---|---:|---:|---|
| Conveyor Oven | 3×5 | 3 / 1 | Mass-produced meals |
| Automated Cannery | 3×5 | 2 / 1 | Long-life canned food |
| Automated Distillery | 3×3 | 1 / 1 | Beer and supported brewing recipes |

### C1. Conveyor Oven

**Documented mechanics**

The oven can mass-produce kibble, pemmican, packaged survival meals, mass-produced meals, and baby food.

**Recommended optimization — design inference**

- Use three dedicated ingredient hoppers rather than a mixed warehouse feed.
- Keep raw-food belts short, roofed, and refrigerated where possible.
- Use stock targets independently for colony meals, travel food, baby food, and animal food.
- Put the output hopper adjacent to the dining/freezer logistics line, not on the industrial output bus.
- Avoid permanent high overclock unless the input freezer and output storage can absorb the burst.

**Evidence:** [S1], [S2B]

### C2. Automated Cannery

**Documented mechanics**

The cannery can preserve meat, produce, fruit, and simple soup. Canning extends shelf life almost indefinitely; canned ingredients may be reused in other recipes.

**Recommended optimization — design inference**

- Place the cannery between the refrigerated raw buffer and the long-term warehouse.
- Use it as the overflow destination when freezers approach capacity.
- Separate meat, produce, fruit, and soup input filters so the desired recipe does not stall behind the wrong material.
- Store canned output in ordinary covered storage rather than consuming refrigerated capacity.
- Preserve strategic reserves using a target bill rather than converting every fresh ingredient automatically.

**Evidence:** [S2D]

### C3. Automated Distillery

**Documented mechanics**

The distillery converts hops into beer and can inherit supported recipes from Vanilla Brewing Expanded.

**Recommended optimization — design inference**

- Place it downstream of a dedicated hop-growing Autofarmer zone.
- Use one input hopper and a stock-target bill.
- Route output directly to controlled beverage storage.
- Keep the distillery out of the main meal line because it competes for agricultural throughput without feeding colonists efficiently.

**Evidence:** [S2D]

---

## Cell D — Textiles and ammunition

### Machines

| Machine | Footprint | Inputs / outputs | Primary capability |
|---|---:|---:|---|
| Autoloom | 3×5 | 2 / 1 | Patchleather, synthread, and apparel |
| Automated Ammunition Press | 3×4 | 2 / 1 | Artillery shells |

### D1. Autoloom

**Documented mechanics**

The Autoloom can make patchleather, synththread, and selected apparel, but finished apparel is restricted to **normal quality**.

**Recommended optimization — design inference**

- Use it for uniforms, disposable workwear, prisoner clothing, trade basics, and intermediate textiles.
- Keep high-quality or prestige apparel on pawn-operated benches.
- Provide distinct cloth/leather and secondary-material hoppers.
- Route normal-quality apparel to a dedicated clothing shelf so it does not clutter the general warehouse.
- Use stock targets per apparel item to avoid wealth and storage bloat.

**Evidence:** [S2C]

### D2. Automated Ammunition Press

**Documented mechanics**

The press manufactures high-explosive, incendiary, EMP, firefoam, smoke, tox, and supported specialty shells according to installed DLC/mod content.

**Recommended optimization — design inference**

- Give steel, chemfuel, components, or specialty feedstocks dedicated hoppers.
- Store completed shells in a secure magazine rather than beside the hot utility spine.
- Use separate target bills for combat stock, firefoam reserve, and specialty ammunition.
- Do not assume it supports every ammunition mod; community requests indicate that some modded ammunition systems require explicit patches.

**Evidence:** [S2C], [S7]

---

## Cell E — Advanced materials

### Machines

| Machine | Footprint | Inputs / outputs | Primary capability |
|---|---:|---:|---|
| Automated Assembler | 5×5 | 4 / 1 | Components and advanced components |
| Automated Alloy Forge | 5×5 | 3 / 1 | Plasteel and supported exotic alloys |
| Neutroamine Synthesizer | 5×3 | 2 / 1 | Chemfuel plus rendered animal fat to neutroamine |

### E1. Automated Assembler

**Documented mechanics**

The assembler makes components and advanced components, has four input positions, and occupies a large 5×5 footprint.

**Recommended optimization — design inference**

- Place it immediately downstream of the metal buffer.
- Dedicate its four input positions rather than feeding it from one unsorted belt.
- Maintain separate component and advanced-component target bills.
- Reserve a local component buffer so the machining bay and construction projects do not drain the assembler’s own advanced-component recipe.
- Give it direct access to the finished precision-parts warehouse.

**Evidence:** [S2C]

### E2. Automated Alloy Forge

**Documented mechanics**

The forge can make plasteel from steel, chemfuel, and gold and supports additional alloy recipes under relevant content. Its official stat block shows the highest base heat generation among the listed machines and a 5×5 footprint.

**Recommended optimization — design inference**

- Give the forge its own hot room or the outermost bay of the industrial hall.
- Link heatsinks before increasing overclock.
- Provide three dedicated feed hoppers.
- Buffer plasteel locally for the assembler and machining bay.
- Avoid sharing its steel feed with the assembler through an unprioritized splitter; use independent storage allocations.
- Leave room for fire suppression and maintenance access.

**Evidence:** [S2D], [S2E]

### E3. Neutroamine Synthesizer

**Documented mechanics**

The synthesizer converts chemfuel and rendered animal fat into neutroamine. It uses two inputs and one output and has a relatively high base electrical demand.

**Recommended optimization — design inference**

- Place it between the chemical-material buffer and medicine cell.
- Use two dedicated input hoppers; do not mix organic feedstocks with the chemfuel line.
- Maintain a target reserve of neutroamine rather than continuous unlimited synthesis.
- Send output directly to a locked medical/chemical buffer.
- If a pipe mod is used for chemfuel, validate compatibility before designing the room around direct pipe input; current Workshop comments show uncertainty around cross-mod pipe integration.

**Evidence:** [S2C], [S7]

---

## Cell F — Precision medicine and equipment

### Machines

| Machine | Footprint | Inputs / outputs | Primary capability |
|---|---:|---:|---|
| Medicine Granulator | 5×3 | 3 / 1 | Medicine, drugs, antibiotics, and supported pharmaceuticals |
| Automated Machining Bay | 5×5 | 3 / 1 | Normal-quality weapons, armor, complex equipment, and mechanoid shredding |

### F1. Medicine Granulator

**Documented mechanics**

The granulator supports medicine, smokeleaf joints, flake, yayo, psychite tea, go-juice, penoxycyline, wake-up, antibiotics, and related recipes according to installed content.

**Recommended optimization — design inference**

- Provide separate filtered hoppers for textiles, herbal medicine, neutroamine, psychoid products, and other recipe-specific materials.
- Place it adjacent to the neutroamine output and hospital/drug storage.
- Use tightly bounded stock targets for every drug.
- Prevent the output belt from depositing controlled drugs into unrestricted colony storage.
- Keep chemical inputs independent from meal and textile trunks despite overlapping ingredients.

**Evidence:** [S2D]

### F2. Automated Machining Bay

**Documented mechanics**

The machining bay can create supported weapons, armor, and complex equipment and can shred mechanoids or drones. Manufactured equipment is restricted to **normal quality**.

**Recommended optimization — design inference**

- Use the bay for standardized utility gear and mass replacement equipment.
- Preserve pawn-operated crafting for quality-sensitive weapons and armor.
- Separate the mechanoid-corpse intake from the equipment-material intake.
- Route finished goods directly to an armory shelf.
- Use item-specific targets to prevent the bay from consuming the colony’s entire component reserve.
- Place it near the assembler, but do not share all input hoppers because both machines compete for components and advanced materials.

**Evidence:** [S2D]

---

# 4. Warehouse and conveyor control cell

## 4.1 Hopper rules

**Documented mechanics**

- A factory requires hoppers at its input and output positions.
- Hopper color changes automatically according to whether it is acting as input or output.
- Hoppers can be configured to prohibit deposits or prohibit removal.
- Conveyors can pull from factory hoppers and transfer into other factories, hoppers, shelves, or the ground.

**Recommended optimization — design inference**

- Lock input hoppers against casual pawn deposits when the belt system is authoritative.
- Lock output hoppers against machine re-intake where loops are possible.
- Use ordinary shelves as final destinations only after a filtered branch.
- Put a small inspection buffer before high-value inputs such as advanced components, gold, plasteel, and neutroamine.

**Evidence:** [S2A]

## 4.2 Intersections and filters

**Documented mechanics**

- Intersections auto-form mergers and equal splitters.
- Selecting a splitter and changing its filter creates a filtered intersection.
- Underground belts cross short distances and emerge automatically.
- Belts ending against refuelable buildings can become refueling ports.

**Observed limitations**

- Automatic intersections can be hard to predict while building.
- There is no dependable native priority splitter.
- Excessive steel or another high-volume item can clog autonomous systems.
- Shared refueling networks can be inconsistent.

**Recommended optimization — design inference**

- Build and test one intersection at a time.
- Keep filtered branches at least one tile apart until the topology is confirmed.
- Use underground segments primarily for crossings, not for hiding long uninspectable lines.
- Provide overflow shelves before a belt rejoins the warehouse.
- Never rely on equal splitters where one consumer must have priority.
- Where priority is essential, use separate source hoppers or separate production runs.

**Evidence:** [S2A], [S6], [S7]

## 4.3 Optional storage-extractor patch

The third-party **Belt Extractors — VFE Factory Patch** lets a belt pull automatically from adjacent standard storage buildings. Native Factory hoppers are excluded because they already integrate with belts.

**Benefits**

- Makes warehouse shelves or chests act as belt sources.
- Reduces pawn hauling between storage and the receiving line.

**Risks reported in comments**

- A source container may be emptied without a quantity limit.
- Unwanted materials can enter a shared line and jam it.
- Some modded storage buildings are incompatible.
- At least one user reported extractors stopping until rebuilt.

**Recommended use — design inference**

Use extractors only on **single-material, quantity-bounded storage**, not on the colony’s general critical stockpile.

**Evidence:** [S8]

---

# 5. Thermal and power utility spine

## Native linkables

| Linkable | Footprint | Link radius | Maximum linked | Effect |
|---|---:|---:|---:|---|
| Factory Booster | 3×1 | 9.9 | 3 | +100 percentage points to maximum overclock |
| Factory Heatsink | 2×2 | 9.9 | 4 | −25% factory heat generation |

## Recommended utility-spine layout — design inference

```text
maintenance corridor
────────────────────────────────────────────────────────

 [heatsink] [booster]   [heatsink] [booster]   [heatsink]
      ╲        ╲             ╲        ╲             ╲
       MACHINE A              MACHINE B              MACHINE C

──────────── power conduits / switches / firebreak ────────────

          production belts on the opposite machine face
```

Place logistics on one face of each machine and utilities on the other. This prevents boosters, heatsinks, hoppers, and belts from competing for the same adjacency space.

## Operating policy

- One local switch per cell.
- Normal production at modest overclock.
- High overclock only when the cell’s output storage has free capacity.
- Disable cells during power emergencies rather than allowing all factories to brown out simultaneously.
- Place the alloy forge, crematorium, and smelter in the strongest cooling zone.
- Use exterior walls, vents, or biome heat as appropriate.
- Do not assume four heatsinks make 500% overclock thermally trivial; the official curve shows exponential heat growth.

**Evidence:** [S2E], [S3], [S5]

---

# 6. Practical build order

1. **Build the warehouse and utility spine first.**
2. Add the **drill and masonry saw** to establish raw construction throughput.
3. Add the **smelter and assembler** to automate components.
4. Add the **autofarmer, oven, and cannery** once refrigerated routing is ready.
5. Add the **biofuel refinery**, but initially buffer chemfuel rather than feeding a large generator tree.
6. Add the **alloy forge and neutroamine synthesizer** only after power and cooling reserves are proven.
7. Add the **medicine granulator and machining bay** with strict target bills.
8. Add the **autoloom and ammunition press** for standardized gear and shells.
9. Add the **mincer and crematorium** with explicit corpse filters.
10. Add the **fishfarm and distillery** as specialty lines.
11. Install boosters last. Test each machine at baseline before designing around 500%.

This order builds the factory’s enabling materials before its optional or high-consumption outputs.

---

# 7. Failure modes and mitigations

| Failure mode | Likely cause | Mitigation |
|---|---|---|
| Machine starves while excess goes to storage | No priority routing | Independent source hopper; separate belt; scheduled production |
| Belt clogs with steel or another bulk item | Mixed trunk plus equal splitters | Filter at source; local buffers; separate trunks |
| Some chemfuel generators remain empty | Shared equal-split network or corner termination | Straight terminal refuel ports; short branches; pipe mod |
| Factory overheats during surge | Exponential heat at high overclock | Lower clock; heatsinks; isolated room; burst operation |
| Output spills or backs up | Too little buffering for overclocked machine | Multiple hoppers; larger output shelf; lower clock |
| Food spoils on belts | Long or exposed food routing | Short roofed/refrigerated routes; stock targets |
| Valuable items are destroyed | Disposal line merged with production | Terminal-only crematorium line; final filter and inspection buffer |
| Extractor empties critical storage | Unbounded third-party extraction | Single-item source bins; reserve stock elsewhere |
| Fishfarm cannot be placed or expanded | Local fish/water condition or depletion behavior | Validate complete footprint before operation; repopulate/test |
| Normal-quality gear displaces skilled crafting | Autoloom/machining limitation overlooked | Automate bulk basics; retain pawn benches for quality work |

**Evidence:** [S1], [S2A–S2E], [S5], [S6], [S7], [S8]

---

# 8. Capability-completeness checklist

A factory campus engages the complete native mod when it includes:

## Logistics

- [ ] Factory Floor beneath every factory building.
- [ ] Input and output Factory Hoppers.
- [ ] Straight and turning conveyors.
- [ ] At least one automatic merger.
- [ ] At least one automatic splitter.
- [ ] At least one configured filter.
- [ ] At least one underground crossing.
- [ ] Direct deposition into a hopper or shelf.
- [ ] A demonstrated refueling port, where relevant.
- [ ] Stock-target factory bills.

## Basic factories

- [ ] Autofarmer.
- [ ] Automated Drill Platform.
- [ ] Conveyor Oven.
- [ ] Automated Smelter.
- [ ] Automated Biofuel Refinery.
- [ ] Automated Masonry Saw.
- [ ] Automated Mincer.
- [ ] Conveyor Crematorium.
- [ ] Automated Ammunition Press.
- [ ] Autoloom.
- [ ] Automated Fishfarm, when Odyssey is installed.

## Complex factories

- [ ] Automated Assembler.
- [ ] Neutroamine Synthesizer.
- [ ] Automated Alloy Forge.
- [ ] Automated Distillery.
- [ ] Medicine Granulator.
- [ ] Automated Machining Bay.
- [ ] Automated Cannery.

## Performance systems

- [ ] Factory Booster.
- [ ] Factory Heatsink.
- [ ] A machine tested above normal overclock.
- [ ] A controlled 500% demonstration with three boosters.
- [ ] Heat and power monitoring during surge operation.
- [ ] Adequate output buffering for the surge machine.

**Evidence:** [S2A–S2E], [S3]

---

# 9. Optional extensions discovered during research

These are not required for a native all-capability build.

- **Belt Extractors — VFE Factory Patch:** belts pull from adjacent storage. Useful for disciplined single-item warehouses; risky on mixed stockpiles. [S8]
- **VFE Factories: Buffs and Tweaks:** balance changes, expanded recipes, faster drill and fishfarm processes, configurable Autofarmer limits, and additional integrations. [S9]
- **VFE Factory — Drill Metals in Space:** permits metal drilling on Odyssey asteroid maps. [S10]
- **Vanilla Chemfuel Expanded:** repeatedly recommended by players as a more reliable generator-fueling layer than a large shared solid-item belt network. [S6]

---

# 10. Source register

## Primary sources

**[S1] Vanilla Furniture Expanded — Factory, Steam Workshop**  
Official description of bill targets, 500% overclocking, heat and power trade-offs, conveyors, filters, underground routing, shelf/hopper deposition, performance, and spoilage/deterioration behavior.  
https://steamcommunity.com/sharedfiles/filedetails/?id=3686924415

**[S2] Official GitHub repository**  
Repository containing the official infographics and mod source.  
https://github.com/Vanilla-Expanded/VanillaFurnitureExpanded-Factory

**[S2A] Official infographic — Factory infrastructure, Autofarmer, and Drill**  
https://raw.githubusercontent.com/Vanilla-Expanded/VanillaFurnitureExpanded-Factory/refs/heads/main/About/Factory.png

**[S2B] Official infographic — Oven, Smelter, Biofuel Refinery, Masonry Saw, and Mincer**  
https://raw.githubusercontent.com/Vanilla-Expanded/VanillaFurnitureExpanded-Factory/refs/heads/main/About/Factory2.png

**[S2C] Official infographic — Crematorium, Ammunition Press, Autoloom, Fishfarm, Assembler, and Neutroamine Synthesizer**  
https://raw.githubusercontent.com/Vanilla-Expanded/VanillaFurnitureExpanded-Factory/refs/heads/main/About/Factory3.png

**[S2D] Official infographic — Alloy Forge, Distillery, Medicine Granulator, Machining Bay, and Cannery**  
https://raw.githubusercontent.com/Vanilla-Expanded/VanillaFurnitureExpanded-Factory/refs/heads/main/About/Factory4.png

**[S2E] Official infographic — Factory Heatsink, Factory Booster, and overclock curve**  
https://raw.githubusercontent.com/Vanilla-Expanded/VanillaFurnitureExpanded-Factory/refs/heads/main/About/Factory5.png

**[S3] Official release post by Oskar Potocki**  
Concise official statement of the mod’s intended systems and trade-offs.  
https://www.reddit.com/r/RimWorld/comments/1rwj3rm/vanilla_furniture_expanded_factory_is_out_now/

**[S4] MysteriousFawx — Factory Module mod rundown for RimWorld 1.6**  
Useful visual walkthrough of the mod’s construction and operating sequence.  
https://www.youtube.com/watch?v=pLrD9guqnPM

## Player builds and community observations

**[S5] “Uroboros setup” — overclocked drill and nuclear-power loop**  
Documents three boosters, 500% drill operation, approximately 5 kW demand, heat concerns, and multiple output hoppers for burst production.  
https://www.reddit.com/r/RimWorld/comments/1uaa9mu/uroboros_setup/

**[S6] “How do I make it work” — chemfuel-generator conveyor network**  
Documents splitter construction confusion, uneven generator fueling, straight-ending refueling ports, corner problems, and community preference for chemfuel pipes.  
https://www.reddit.com/r/RimWorld/comments/1sdaso1/how_do_i_make_it_work/

**[S7] Steam Workshop comments**  
Current reports concerning unpredictable intersections, absence of priority routing, steel clogs, fishfarm placement/depletion concerns, crop compatibility, storage endpoints, and cross-mod integration. These are reports, not official specifications.  
https://steamcommunity.com/sharedfiles/filedetails/comments/3686924415

## Optional patches

**[S8] Belt Extractors — VFE Factory Patch**  
https://steamcommunity.com/sharedfiles/filedetails/?id=3694555789

**[S9] VFE Factories: Buffs and Tweaks**  
https://steamcommunity.com/sharedfiles/filedetails/?id=3708068232

**[S10] VFE Factory — Drill Metals in Space**  
https://steamcommunity.com/sharedfiles/filedetails/?id=3697323721

---

## Bottom line

The most robust “uses everything” factory is not one monolithic room. It is an **eight-cell industrial campus** connected by filtered warehouse trunks and a separate utility spine. The decisive optimizations are:

1. Local buffers before shared logistics.
2. Dedicated belts for high-volume or hazardous materials.
3. Stock-target bills instead of unrestricted production.
4. Straight, short chemfuel delivery branches or a pipe network.
5. Explicit disposal filters.
6. Burst-only 500% overclocking.
7. Heat isolation around the forge, smelter, crematorium, and drill.
8. Separate pawn-crafted quality goods from normal-quality automated output.

That architecture exercises every native capability while containing the routing, heat, power, spoilage, and storage problems repeatedly exposed by the available player evidence.
