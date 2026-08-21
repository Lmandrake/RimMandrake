<!-- status: live -->
# Gravship Campaign Design Notes

**Updated:** 2026-08-02  
**Purpose:** Campaign specification, curated mod list, and implementation brief for Claude Cowork.

---

## 1. Campaign Goal

Create a RimWorld 1.6 / Odyssey gravship campaign that feels like a genuine mobile expedition rather than a conventional colony that happens to own a spaceship.

The desired fantasy is closer to:

- *Firefly*
- *Battlestar Galactica*
- *Oregon Trail* in space
- A scientific expedition crossing an unexplored world
- A small crew living inside an irreplaceable automated industrial organism

The core loop should be:

> Land → identify objectives → establish a disposable field camp → explore and complete a milestone quest → acquire feedstock or a unique upgrade → improve the ship → enemy pressure rises → abandon the site → launch → repeat.

---

## 2. Accepted Industrial Concept

The gravship will carry automated production from **Vanilla Furniture Expanded - Factory**.

This is not merely a convenience mod. It defines the crew and ship relationship:

- Colonists are explorers, soldiers, medics, researchers, negotiators, and engineers rather than full-time production specialists.
- The ship performs routine industrial labor.
- The crew is consequently dependent on power, cooling, conveyors, factory rooms, machine integrity, and replacement parts.
- Factory floor area directly competes with cabins, storage, life support, defenses, fuel, and future hull expansion.
- Losing a production line should feel like losing a ship organ, not merely losing a workbench.

The Factory mod already reinforces this concept through large machinery, substantial power demand, heat production, conveyor logistics, and two explicit research tiers. Its source definitions currently identify:

- `VFE_BasicFactories` — 5,000 research, prerequisite `Machining`.
- `VFE_ComplexFactories` — 6,000 research, prerequisites `VFE_BasicFactories` and `Fabrication`.

### Recommended Starting State

Start with **one inherited, already-installed provisioning line** aboard the ship:

- Conveyor oven
- Minimal hoppers and conveyors
- Only enough supporting equipment to produce durable travel food

The crew may operate it but initially cannot construct a replacement because `VFE_BasicFactories` remains locked. This immediately establishes dependence without granting a complete industrial economy.

A harsher alternative is to begin with an automated smelter instead of the oven. The oven creates stronger survival dependence; the smelter creates stronger salvage dependence. Do not begin with both unless the initial deck is extremely constrained.

---

## 3. Core Campaign Rules

- Start from the Odyssey gravship scenario or a lightly modified derivative.
- Begin with a barely functional, tightly packed ship.
- Retain the pursuing-mechanoids mechanic or an equivalent escalating pursuer.
- Never establish a permanent planetary base.
- Temporary camps are allowed but are disposable.
- All permanent colony infrastructure lives aboard the gravship.
- Keep the crew small, approximately 4–8 pawns.
- Every crew member must have a meaningful ship or expedition role.
- Fuel remains strategic; always retain emergency-launch fuel.
- Stay on most maps for approximately 10–15 days unless a quest narrative justifies longer.
- Expand the ship only after explicit milestones.
- Avoid giant static killboxes.
- Keep cargo storage deliberately limited.
- Accept losses during emergency launches.
- End with a major destination, mechhive confrontation, or other final objective rather than indefinite wandering.

### Governing Principle

**Movement should solve problems.**

If remaining indefinitely is always optimal, the gravship has become irrelevant.

Every system should reinforce:

- Mobility
- Scarcity
- Exploration
- Logistical tradeoffs
- Decisions about what must be left behind
- Dependence on the ship
- Visible evolution of the vessel

---

## 4. Curated Mod List with Commentary

### 4.1 Required Foundation

#### Harmony

**Status:** Required dependency.

Required by Vanilla Furniture Expanded - Factory and many other framework mods. Keep it at the top of the mod order after the game itself, according to the mod manager's recommendations.

#### RimWorld Core + Odyssey

**Status:** Required.

Odyssey supplies the gravship, orbital sites, gravcores, field extenders, gravlite construction, the pursuit scenario, and the intended nomadic loop.

#### Royalty

**Status:** Required only for the quick Configurable Techprints implementation.

Vanilla techprints are a Royalty system. A fully custom quest-item implementation could remove this dependency, but there is little reason to avoid Royalty if it is already part of the intended campaign.

#### Vanilla Expanded Framework

**Status:** Required dependency.

Required by Vanilla Furniture Expanded - Factory.

#### Vanilla Furniture Expanded - Factory

**Status:** Accepted; central campaign mod.

Why it belongs:

- Turns the ship into a production system rather than a collection of ordinary benches.
- Replaces pawn crafting specialization with machinery, power, cooling, and logistics dependence.
- Creates genuine deck-space competition.
- Supports an explicit Basic → Complex industrial progression.
- Provides conveyors and production targets without the much larger systems burden of Project RimFactory.

Campaign restrictions:

- All permanent factory equipment must remain aboard the gravship.
- No conventional industrial colony may be built at a landing site.
- Factory overclocking is for emergencies or short production surges, not routine operation.
- Output stockpiles remain small; the vessel carries production capacity rather than years of finished goods.
- Rare-material recipes must not eliminate the need to explore. Neutroamine, plasteel, gravlite, medicine, and advanced-component automation should arrive late and remain feedstock constrained.

#### Configurable Techprints

**Status:** Recommended for the immediate prototype; optional after a dedicated progression mod is complete.

Use it to require quest-obtained techprints for selected research and suppress those techprints from trader inventories.

Recommended gates:

- `VFE_BasicFactories`: 1 techprint
- `VFE_ComplexFactories`: 1 techprint
- Odyssey advanced gravtech / gravlite-fabrication research: 1 techprint after Cowork confirms the installed defName

Advantages:

- Fastest way to prove that quest-gated progression feels good.
- Avoids manually editing every affected research definition.
- Can explicitly prevent configured techprints from appearing in trader stock.

Limitations:

- It produces a generic techprint economy, not necessarily a named authored quest chain.
- It may still allow configured prints through generic quest-reward generation or gifts unless the strict patch also removes those routes.
- It can conflict with mods that heavily replace research or techprint behavior.
- Its settings interface and serialized configuration are less reproducible than a dedicated local compatibility mod.

**Recommendation:** Use it for a one-session balance prototype, then have Cowork create the strict local progression mod described below.

---

### 4.2 Essential Exploration Mods

#### Vanilla Landmarks Expanded

**Status:** Essential.

- Adds named, recognizable destinations.
- Gives travel decisions an identity before landing.
- Strongly supports the question, “Is that site worth fuel and risk?”

#### Smart Odyssey

**Status:** Essential if current compatibility remains clean.

- Exposes tile mutators and useful destination information on the world map.
- Makes route planning intentional without fully revealing the reward.

Desired information standard:

> The player should know why a destination may be interesting, but not exactly what it contains.

#### Geological Landforms

**Status:** Essential.

- Produces structurally distinct maps rather than minor biome recolors.
- Makes temporary camps and tactical landings meaningfully different.

#### Biome Transitions

**Status:** Essential.

- Creates mixed-biome landing sites.
- Supports the feeling of moving through a geographically coherent planet.

---

### 4.3 Strong Additions

#### Ancient Urban Ruins

**Status:** Strong recommendation.

- Supports multi-day salvage expeditions.
- Creates destinations large enough to justify landing and risking pursuit.
- Better matches a mobile archaeological expedition than repeated tiny ancient dangers.

Balance requirement:

- Reduce loot if necessary.
- Unique progression items must not be added to its general loot pools.

#### RimWorld Exploration Mode

**Status:** Strong recommendation if compatible with the selected world-map mods.

- Introduces gradual world discovery.
- Makes orbital or long-range reconnaissance valuable.
- Prevents the campaign from becoming a solved map-routing exercise at game start.

#### Go Explore!

**Status:** Strong recommendation, but inspect overlap with Odyssey and other quest mods.

- Adds signals, lost cities, captures, and expedition objectives.
- Provides reasons to divert from the shortest route.

Important restriction:

- Its generic sites may provide ordinary loot, but must never provide the custom industrial techprints or expansion authorizations.

---

### 4.4 Optional Flavor — Choose Conservatively

#### Alpha Biomes

**Use when:** A stranger, more alien planetary ecology is wanted.

Pros:

- Strong visual and biological identity.
- Excellent science-fiction expedition atmosphere.

Cons:

- More fantastical.
- Larger systemic and balance changes.
- Can make the carefully curated destination set feel noisy.

#### Real Ruins

**Use when:** Archaeology and authentic abandoned colonies matter more than strict balance.

Pros:

- Memorable salvage sites.
- Strong material-history feeling.

Cons:

- Loot can destabilize progression.
- Must be configured aggressively.
- Custom milestone items must be excluded from imported ruins and general loot.

Choose **Alpha Biomes or Real Ruins initially, not both**.

---

### 4.5 Deliberate Exclusions

#### Project RimFactory

**Status:** Do not include in the first campaign.

It is powerful, but its deeper logistics and automation systems risk turning the campaign into a stationary factory-engineering game. Vanilla Furniture Expanded - Factory better preserves the nomadic expedition as the main game.

#### Randomized Research / Major Research Overhauls

**Status:** Avoid.

They can interfere with deterministic quest gates and may conflict with Configurable Techprints. The campaign needs authored scarcity, not another layer of random access.

#### Custom Quest Framework

**Status:** Experimental only; not a core dependency.

Its in-game quest editor and custom-map features are attractive, but it is a broad framework with uncertain interaction surfaces. A small dedicated compatibility mod is easier to audit, reproduce, and remove.

#### Microelectronics Chip Quest

**Status:** Do not install merely for this campaign; use as an implementation pattern.

Its design is directly relevant: a world-site quest contains a chip that must be studied to unlock research. Cowork can inspect it as an example of the desired behavior, but the campaign should have its own named progression and dependencies.

#### Vanilla Quests Expanded modules

**Status:** Optional content, not required for progression.

The source code is useful as a model for staged quest chains. Install a module only if its actual quest content is wanted; do not add a large unrelated module merely to obtain its framework behavior.

---

## 5. Recommended Quest-Gated Progression

### 5.1 Why Two Different Gates Are Needed

Use two separate mechanisms:

1. **Knowledge gates:** A specific quest-earned techprint or data core is required before the research can begin.
2. **Capacity gates:** A specific quest-earned physical authorization/core is consumed when a major ship expansion is built.

This closes two different loopholes:

- A knowledge gate prevents ordinary research labor from producing advanced capability out of nowhere.
- A capacity gate prevents a lucky cache, trader, or large resource haul from allowing unlimited physical growth after the technology is known.

### 5.2 Recommended Milestones

| Stage | Quest | Reward | Unlock / Effect | Design Function |
|---|---|---|---|---|
| Start | Inherited Provisioning Line | Existing conveyor oven line | Can operate, but cannot replace | Establishes immediate machine dependence |
| I | **The Dead Foundry** | Basic Automation Techprint | Unlocks `VFE_BasicFactories` | Enables basic conveyors, smelting, food, textiles, and routine processing |
| II | **The Silent Assembly Line** | Precision Fabrication Techprint | Unlocks `VFE_ComplexFactories` | Enables components, advanced components, medicine, neutroamine, alloys, and advanced machining |
| III | **The Gravlite Equation** | Gravtech Fabrication Techprint | Unlocks advanced gravtech / gravlite-panel fabrication | Allows deliberate hull rebuilding rather than depending only on salvage |
| IV+ | **Field Harmonics** repeatable chain | 1 Expansion Authorization per quest | Required in addition to normal resources for one grav-field extender | Makes every increase in supported deck area an earned expedition milestone |
| Optional | **Industrial Control Recovery** | 1 Industrial Control Core | Required for one selected late-game complex production line | Forces a choice among medicine, electronics, alloys, or munitions |

### 5.3 Quest Design Requirements

Each milestone quest should:

- Appear only after the prior milestone is complete.
- Spawn far enough away to require an intentional flight or caravan/shuttle expedition.
- Clearly announce the category of reward without revealing every site detail.
- Require interaction with the site, not merely accepting a timed hospitality request.
- Use a fixed, authored reward rather than a generic reward value budget.
- Never allow the milestone item to substitute into generic reward pools.
- Ideally include a reason to abandon the map quickly after recovery: pursuer escalation, reactor instability, orbital decay, reinforcements, toxic release, or a fixed extraction timer.

### 5.4 Suggested Quest Forms

#### The Dead Foundry

- Destination: Abandoned industrial landmark or ruined factory district.
- Threat: Dormant defenses activate as machinery is powered.
- Objective: Restore power to a data terminal, hold the site during extraction, recover the Basic Automation Techprint.
- Outcome: The ship can now build or replace basic factory equipment.

#### The Silent Assembly Line

- Destination: Orbital wreck, mechanitor facility, or sealed urban fabrication plant.
- Threat: Mechanoids, vacuum, heat, and narrow industrial corridors.
- Objective: Bring the inherited data core to several calibration stations, then extract the precision fabrication schema.
- Outcome: Complex factories become researchable.

#### The Gravlite Equation

- Destination: Asteroid foundry or ancient gravtech laboratory.
- Threat: Vacuum, unstable geometry, hostile salvagers, and limited extraction time.
- Objective: Survey several gravlite-processing nodes and recover the fabrication matrix.
- Outcome: Advanced gravtech / gravlite fabrication becomes researchable.

#### Field Harmonics

- Destination varies: insect megahive, frozen wreck, allied engineering crisis, ancient structure, or mech platform.
- Reward: Exactly one **Expansion Authorization**.
- Construction rule: Each grav-field extender requires one authorization plus its normal gravcore and materials.
- Repeatability: One authored quest per extender, with threat scaled to current ship wealth or prior extenders.

This is superior to merely removing gravcores from trade. Even if a gravcore is found through another Odyssey activity, it can be used for a power cell or other system but cannot enlarge the ship without the quest-earned authorization.

---

## 6. What Must Be Removed from Trade and Random Discovery

The strict progression mod should make all milestone items:

- Non-tradeable
- Absent from trader stock generators
- Absent from faction gifts
- Absent from ancient-danger loot
- Absent from sealed-crate and general Odyssey loot tables
- Absent from Real Ruins imports
- Absent from generic quest reward generation
- Absent from random thing-set makers
- Obtainable only through their named `QuestScriptDef`

Do not rely only on market value zero. A zero-value item can still leak through a poorly scoped generator. Remove all relevant trade tags, reward tags, and loot-generation references, then test actual generation paths.

### Do Not Over-Gate Raw Hull Panels

Quest-gating every gravlite panel would create administrative tedium rather than meaningful progression.

Recommended balance:

- The crew may salvage or manufacture ordinary gravlite panels after the gravtech milestone.
- The total supported ship area remains hard-capped by grav-field extenders.
- Every extender consumes a quest-only Expansion Authorization.

This permits internal redesign and repair while preserving quest-gated growth.

---

## 7. Cowork Implementation Strategy

### 7.1 Verdict

**Yes: Cowork is well suited to building and maintaining this configuration.** It can read and write connected local folders, inspect installed mod definitions, create a separate local mod, compare source files, run validation scripts, and—using desktop computer control—open development tools or RimWorld and inspect logs.

The correct approach is **not** to have Cowork edit Workshop or DLC files directly.

Create a standalone local compatibility mod:

> `Gravship Expedition Progression`

Load it after Odyssey, Vanilla Expanded Framework, Vanilla Furniture Expanded - Factory, and any quest/research mods it patches.

### 7.2 Folder Access

Give Cowork access only to the folders needed for this task:

**Read/reference access**

- RimWorld installation `Data` folder, especially Odyssey definitions
- Workshop folder for Vanilla Furniture Expanded - Factory
- Workshop folder for Configurable Techprints, if used
- Example quest mods selected for inspection
- Current RimWorld configuration and `Player.log`

**Read/write access**

- A dedicated staging folder for the new mod
- The local RimWorld `Mods/GravshipExpeditionProgression` folder, or a mirrored deployment folder

Do not grant unrelated personal folders. Do not let Cowork alter Workshop content because Steam updates will overwrite those changes.

### 7.3 Expected Mod Structure

```text
GravshipExpeditionProgression/
├── About/
│   └── About.xml
├── Defs/
│   ├── ThingDefs_Items/
│   │   └── ProgressionItems.xml
│   └── QuestScriptDefs/
│       └── GravshipProgressionQuests.xml
├── Patches/
│   ├── FactoryResearchGates.xml
│   ├── GravshipExpansionGate.xml
│   ├── TradeAndLootExclusions.xml
│   └── ScenarioStart.xml
├── Languages/
│   └── English/
│       └── Keyed/
│           └── GravshipProgression.xml
├── Source/                 # Only if a small C# component is required
└── Assemblies/             # Compiled DLL, only if required
```

### 7.4 Prefer XML First

Cowork should first attempt an XML-only implementation using:

- Research-project patches
- Techprint requirements
- Custom non-tradeable ThingDefs
- QuestScriptDefs with fixed rewards
- Construction-cost patches
- Scenario starting-things patches
- `PatchOperationFindMod` and conditional patches for compatibility

Add C# only if the installed quest system cannot cleanly perform one required behavior, such as a custom study interaction or a milestone condition unavailable through existing QuestNodes.

### 7.5 Non-Negotiable Engineering Rules for Cowork

- Inspect installed files and confirm every `defName`; never guess.
- Never modify Core, DLC, or Workshop files.
- Create a timestamped backup before changing an existing local mod.
- Use XPath patches rather than copied replacement definitions wherever possible.
- Make patches conditional on the target mod being active.
- Keep each gameplay concern in a separate patch file.
- Add comments explaining why each patch exists.
- Parse every XML file before deployment.
- Search the resulting mod for unresolved placeholder names.
- Launch RimWorld with only the minimum test list first.
- Read `Player.log` and resolve every red XML, missing-def, and patch-operation error.
- Produce a final manifest of changed defs and acquisition routes.
- Produce an uninstall note and save-compatibility warning.

---

## 8. Copy-Paste Cowork Task Brief

```text
Build a local RimWorld 1.6 compatibility mod named “Gravship Expedition Progression.”

Goal:
Create deterministic quest-gated progression for a nomadic Odyssey gravship campaign using Vanilla Furniture Expanded - Factory. Production upgrades and gravship field expansion must not be obtainable through traders, gifts, generic loot, random research, or generic quest reward pools.

Safety and file rules:
1. Read the installed RimWorld, Odyssey, Vanilla Expanded Framework, Vanilla Furniture Expanded - Factory, and Configurable Techprints definitions to discover exact current defNames and schemas.
2. Do not edit Core, DLC, Steam Workshop, or existing mod files.
3. Write only to the connected staging folder and the new local mod folder.
4. Back up the local mod before every revision.
5. Do not guess XPath targets or defNames. Verify them from the installed files.

Required campaign behavior:
1. The starting gravship receives one installed legacy provisioning line centered on a conveyor oven with the minimum required hoppers/conveyors. It operates immediately, but the crew cannot build replacement factory equipment until the first milestone is unlocked.
2. Lock VFE_BasicFactories behind one specific quest-only techprint/data core.
3. Lock VFE_ComplexFactories behind a second specific quest-only techprint/data core and preserve its normal research prerequisites.
4. Lock Odyssey advanced gravtech or gravlite-panel fabrication behind a third specific quest-only techprint/data core. Determine the exact installed research defName before patching.
5. Add an untradeable item named Expansion Authorization. Every grav-field extender must consume exactly one authorization in addition to its normal costs.
6. Add a staged quest chain that awards exactly one required milestone item at each stage. The fourth stage may repeat to provide one Expansion Authorization per completed expansion quest.
7. Milestone items must have no trader stock, trade tags, gift generation, generic reward commonality, random loot tags, sealed-crate generation, ancient-site generation, or Real Ruins/general thing-set generation.
8. Fixed quest rewards must be referenced explicitly by defName rather than selected from a reward-value pool.
9. A gravcore obtained elsewhere may still be used for non-expansion purposes, but it must not bypass the Expansion Authorization requirement for a field extender.
10. Ordinary gravlite panels may be salvaged or manufactured after the gravtech milestone. Do not require one quest per floor tile.

Quest sequence:
- The Dead Foundry → Basic Automation Techprint → VFE_BasicFactories
- The Silent Assembly Line → Precision Fabrication Techprint → VFE_ComplexFactories
- The Gravlite Equation → Gravtech Fabrication Techprint → advanced gravtech/gravlite fabrication
- Field Harmonics → one Expansion Authorization → one grav-field extender

Implementation preferences:
- Prefer XML and standard QuestScriptDefs.
- Use PatchOperationFindMod and conditional patches.
- Add C# only if a required interaction cannot be implemented safely in XML.
- If using Configurable Techprints, inspect and document its generated defs/settings. Do not depend on its UI configuration as the sole source of truth if a reproducible XML patch is possible.
- Use the source of Microelectronics Chip Quest as a behavioral reference for a quest-site research unlock, and Vanilla Quests Expanded source as a structural reference for staged quest chains. Do not add either as a dependency unless technically necessary.

Validation:
- Parse all XML.
- Confirm all patched XPath targets match exactly once unless multiple matches are intentional.
- Launch a minimal test mod list and inspect Player.log.
- In developer mode, generate at least 20 relevant traders and 50 generic rewards/loot sets and verify no milestone item appears.
- Verify each quest appears only after its prerequisite stage.
- Verify each fixed quest grants the intended item.
- Verify research cannot begin before its required item is applied.
- Verify a field extender cannot be constructed without one Expansion Authorization and that construction consumes it.
- Verify the starting legacy factory works but cannot be rebuilt before Stage I.
- Produce README.md, CHANGELOG.md, a manifest of exact patched defNames, load-order instructions, and save-compatibility notes.
```

---

## 9. Validation Matrix

| Test | Expected Result |
|---|---|
| Open research tree at campaign start | Basic and Complex Factory research visibly blocked by milestone requirement |
| Operate inherited conveyor oven | Functions despite missing construction research |
| Attempt to build replacement oven before Stage I | Not permitted |
| Generate bulk/exotic/orbital traders | No milestone item or configured milestone techprint appears |
| Generate generic quest rewards | No milestone item appears except in its authored quest |
| Search ancient sites, crates, ruins, imported Real Ruins | No milestone item appears |
| Complete The Dead Foundry | Correct Basic Automation item awarded |
| Apply/study item | `VFE_BasicFactories` becomes researchable, not automatically completed unless deliberately designed that way |
| Complete The Silent Assembly Line | Complex Factory gate opens while normal prerequisites remain intact |
| Acquire spare gravcore before Field Harmonics | Cannot build extender without Expansion Authorization |
| Complete Field Harmonics | Exactly one authorization awarded |
| Build extender | Authorization consumed; supported ship area increases normally |
| Reload save | All stage state and quest state persist |
| Update Factory mod | Compatibility patch either continues to match or emits an obvious log error rather than silently failing |

---

## 10. Recommended Load Order

Use RimSort/RimPy or the game's dependency resolver for the exact ordering, but the conceptual order is:

1. Harmony
2. Core
3. DLCs, including Royalty and Odyssey
4. Vanilla Expanded Framework
5. Vanilla Furniture Expanded - Factory
6. World-generation and exploration mods
7. Configurable Techprints, if retained
8. Other quest/content mods
9. **Gravship Expedition Progression** local compatibility mod

The local progression mod should load after every mod whose definitions it patches.

---

## 11. Final Recommendation

Use a two-phase implementation:

### Phase A — Playtest the Economy

- Install Vanilla Furniture Expanded - Factory.
- Install Configurable Techprints.
- Gate Basic Factories, Complex Factories, and advanced gravtech behind quest-only techprints with trader stock disabled.
- Play enough to determine whether three industrial milestones are sufficient and how frequently expansion quests should occur.

### Phase B — Make It Deterministic

Have Cowork build the standalone **Gravship Expedition Progression** mod.

The final design should use:

- Named authored quest gates for production knowledge
- One consumed authorization per grav-field extender
- Fixed rewards rather than generic reward pools
- Explicit exclusion from trade, gifts, loot, imported ruins, and generic quests
- A fragile inherited production line at campaign start
- No quest requirement for every individual floor panel

This preserves the desired balance: the ship can be repaired and rearranged, but every qualitative industrial leap and every increase in supported deck area must be earned by taking the gravship somewhere dangerous.

---

## Sources and Implementation References

- Ludeon Studios, “Odyssey preview #2: Gravships and space”: https://ludeon.com/blog/2025/06/odyssey-preview-2-gravships-and-space/
- Vanilla Furniture Expanded - Factory source: https://github.com/Vanilla-Expanded/VanillaFurnitureExpanded-Factory
- Factory research definitions: https://github.com/Vanilla-Expanded/VanillaFurnitureExpanded-Factory/blob/main/1.6/Defs/ResearchProjectDefs/ResearchProjects_Various.xml
- Factory building definitions: https://github.com/Vanilla-Expanded/VanillaFurnitureExpanded-Factory/blob/main/1.6/Defs/ThingDefs_Buildings/Buildings_Factories.xml
- Configurable Techprints: https://steamcommunity.com/sharedfiles/filedetails/?id=2876747024
- Microelectronics Chip Quest: https://steamcommunity.com/sharedfiles/filedetails/?id=3573473727
- Custom Quest Framework: https://steamcommunity.com/sharedfiles/filedetails/?id=2978572782
- Vanilla Quests Expanded - Ancients source: https://github.com/Vanilla-Expanded/VanillaQuestsExpanded-Ancients
- Claude Cowork getting started: https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork
- Claude Cowork local/computer access: https://support.claude.com/en/articles/14128542-let-claude-use-your-computer-in-cowork
- Claude Cowork safety: https://support.claude.com/en/articles/13364135-use-claude-cowork-safely


---

# 12. Advancement Architecture: Preventing Exponential Success

## 12.1 Accepted Design Principle

The campaign should not expose every RimWorld advancement system as an independent route to power.

Research, factories, psycasts, xenogenetics, mechanitors, ideology specialists, royal permits, artifacts, bionics, and anomaly powers do not merely add options. They interact multiplicatively:

- Better researchers unlock better production.
- Better production equips stronger fighters.
- Stronger fighters acquire more artifacts and quest rewards.
- Psycasts bypass tactical and logistical constraints.
- Genes remove pawn weaknesses.
- Mechanitors eliminate labor scarcity.
- Ideology roles multiply production or combat competence.
- Royal permits provide external solutions without consuming ship capacity.

When several of these systems mature together, the player ceases to face meaningful dependencies. The gravship becomes one powerful tool among many rather than the center of the campaign.

### Governing Rule

> **The gravship and its onboard industrial system are the campaign’s only scalable progression trees.**

Other systems may still exist, but they should function as:

- Fixed character backgrounds
- Cultural constraints
- Singular quest-earned exceptions
- Irreplaceable story assets
- New vulnerabilities
- Mutually exclusive choices

They should not become additional repeatable optimization economies.

## 12.2 Evaluation Test for Any New System

Before adding a mod, DLC subsystem, or reward type, ask:

1. Does it deepen the gravship/industrial progression, or create a parallel progression ladder?
2. Does it impose a dependency, or merely remove an existing limitation?
3. Can it scale indefinitely through trade, research, breeding, crafting, or repeated quests?
4. Does it make recruitment and crew composition less important?
5. Does it bypass fuel, deck space, expedition risk, production time, injuries, mood, or scarcity?
6. Can it be reduced to a single authored exception rather than a general system?
7. Does it make the ship more important, or make the ship less necessary?

If the answer points toward broad optionality and self-sufficiency, the system should be restricted or excluded.

---

# 13. Psychic Powers

## 13.1 Accepted Decision

**No player psycasting.**

Psychic powers fit RimWorld’s setting and could support a “psychic navigator” fantasy, but mechanically they create a highly flexible parallel advancement tree. Even modest psycasts can bypass exactly the problems this campaign is designed to preserve:

- Tactical positioning
- Fire and heat emergencies
- Hauling
- Extraction
- Crowd control
- Recruitment and social difficulty
- Light and environmental constraints
- Travel or return logistics

A powerful caster would also shift the campaign’s narrative center away from the gravship. The extraordinary object should be the ship, not a wizard who can repeatedly solve unrelated problems.

## 13.2 Campaign Restrictions

Prohibit:

- Accepting psylink neuroformers
- Purchasing or using psytrainers
- Anima-tree linking
- Royal-title advancement pursued for psylinks
- Quest rewards that grant psychic progression
- Vanilla Psycasts Expanded
- Any mod that turns meditation into a broad experience-and-leveling system

Royalty may remain installed for factions, equipment, enemies, and quests, but the player does not use its psychic advancement path.

## 13.3 Possible Future Exception

A singular non-scaling psychic character could be reconsidered only if later playtesting shows that the campaign needs a specific narrative role.

Example:

> **The Listener** has one fixed sensing or minor control ability, cannot gain psylink levels, cannot learn new powers, and is acquired through a major authored quest.

This is not currently part of the accepted ruleset. It remains a possible story device, not a planned progression system.

---

# 14. Genetics and Xenotypes

## 14.1 Accepted Decision

**Interesting xenotypes are welcome, but each individual or population has a fixed biological identity.**

Genetics should enrich recruitment, faction identity, environmental adaptation, and crew tension. It should not become a player-operated optimization laboratory.

A pawn’s biology is part of the decision to recruit and retain them. The player must accept both advantages and liabilities.

Examples:

- A powerful combat xenotype with a chemical dependency
- A technically brilliant but physically delicate xenotype
- A cold-adapted population poorly suited to tropical expeditions
- A nocturnal or sunlight-sensitive salvage specialist
- A high-metabolism pawn who consumes disproportionate ship provisions
- A resilient xenotype that is socially or medically difficult to support

## 14.2 Prohibited Active Genetics Systems

Do not build or operate:

- Gene extractors
- Gene assemblers
- Gene processors
- Gene banks
- A genepack economy
- Custom xenogerms
- Archite-capsule optimization
- Routine purchase of genetic upgrades
- Breeding programs intended to optimize the crew

This prevents genetics from erasing recruitment tradeoffs and turning pawn weaknesses into temporary engineering defects.

## 14.3 Genetics as Story Content

Genetics may appear through:

- Distinct fixed xenotype factions
- Rescue quests
- Refugee groups
- A rare recruit with valuable but burdensome adaptations
- Populations biologically adapted to unusual biomes
- A single irreversible late-game treatment with a major drawback

Any exceptional genetic intervention should be:

- Quest-authored
- Limited to one pawn or one decision
- Irreversible
- A genuine tradeoff
- Mutually exclusive with another valuable reward
- Not the beginning of a repeatable genetics program

---

# 15. Ideology, Religion, and Ship Culture

## 15.1 Accepted Direction

**Religion/ideology should be present as a fixed constitution, not a leveling system.**

Ideology is valuable because it can define obligations, taboos, rituals, and identity. It should tell the crew what they refuse to do and what the ship means to them. It should not generate an additional stream of specialists, recruits, powers, discoveries, or optimized production.

## 15.2 Fixed Rather Than Fluid

Use a fixed ideology.

Do not use fluid-ideology development, because development points and newly added memes create another progression ladder.

Suggested identity:

> **The Articles of Passage**  
> The gravship is the crew’s only permanent home. No planetary settlement may claim them. Every expedition is temporary, every crew member carries part of the vessel, and every journey must ultimately return to the ship.

This can be treated as:

- A religion
- A naval tradition
- A survival charter
- A quasi-religious ship culture
- A constitutional compact among refugees

The supernatural truth of the doctrine need not be resolved.

## 15.3 Recommended Meme Structure

Use **Shipborn** as the principal or only strong meme.

Avoid stacking numerous mechanically efficient memes. The goal is identity and constraint, not another optimization puzzle.

Potential values:

- Indoor and shipboard life is normal or preferred
- Nutrient paste or industrial food is acceptable
- Permanent planetary settlement is disfavored
- Leaving crew behind is culturally grave
- Recovering ship components and bodies is a duty
- Limited personal possessions are expected
- Major hull expansions are communal milestones
- The vessel’s continuity matters more than any temporary camp

Some of these may remain campaign rules rather than formal precepts.

## 15.4 Roles

Permitted:

- **Captain** as leader
- **Keeper of the Articles**, Steward, or Chaplain as moral guide

Avoid specialist roles that multiply:

- Production
- Research
- Shooting
- Plants
- Animals
- Medical work
- General labor efficiency

Factories already replace routine production labor. Ideology specialists would create another source of superhuman specialization and accelerate the economy.

## 15.5 Rituals

Use only two or three rituals.

Suitable rituals:

- **First Lift** — after a major field expansion or first successful launch
- **The Empty Chair** — funeral for a crew member whose body was unrecoverable
- **Crossing the Dark** — before the first orbital or exceptionally dangerous voyage
- **Return to Deck** — after a catastrophic expedition
- **The Joining** — when a new crew member permanently joins the ship

Routine rituals should have **no material reward**.

Do not use rituals to generate:

- Recruits
- Animals
- Goodwill
- Quest locations
- Ancient-complex discoveries
- Psylinks
- Valuable artifacts
- Repeated economic benefits

Mood and social cohesion are acceptable outcomes. Material advancement is not.

## 15.6 Relics

Use at most one major relic.

Possible relics:

- The original flight recorder
- The first captain’s key
- A fragment of the first grav engine
- The lost navigation core
- A plate carrying the names of the original crew

The relic may anchor a multi-stage recovery quest, but should provide modest mechanical value. It belongs on the bridge or in a memorial compartment because it matters culturally, not because it produces a gift or pilgrim economy.

---

# 16. Adjacent Advancement Systems

## 16.1 Royalty and Permits

Royal nobility should not become a player progression route.

Avoid:

- Building a royal court aboard the ship
- Pursuing titles for permits
- Repeated permit-based solutions
- Honor farming
- Royal bedroom and throne-room escalation

The Empire may remain an external faction, patron, rival, or source of difficult political quests.

## 16.2 Mechanitors

Current recommendation:

**No mechanitor progression.**

The gravship already contains an automated production system. A mechanitor labor force would add a second automation tree capable of solving:

- Hauling
- Construction
- Mining
- Cleaning
- Agriculture
- Combat
- Manufacturing support

Possible future exception:

- One inherited utility mech
- Fixed task set
- No gestation
- No bandwidth expansion
- No resurrection or replacement
- No combat-mech army

This would be an irreplaceable ship asset rather than a scalable workforce.

## 16.3 Transhumanism, Biosculpting, and Bionics

Avoid the Transhumanist meme and routine biosculpting.

Ordinary prosthetics and selected bionics may remain, but advanced replacements should generally be:

- Salvaged
- Quest-earned
- Rare
- Difficult to install
- Difficult to replace

The ship should not become a mass-production clinic for perfect bodies.

---

# 17. Accepted Campaign Systems Map

## Scalable Progression

**The gravship and its industrial plant**

- Factory tiers
- Gravtech
- Field extenders
- Power
- Cooling
- Logistics
- Hull capacity
- Quest-earned schematics
- Rare industrial control cores

## Fixed Identity

**Ideology and ship culture**

- Obligations
- Taboos
- Rituals
- Leadership
- Crew cohesion
- Relationship to the ship

## Fixed Variation

**Xenotypes**

- Individual advantages
- Individual dependencies
- Recruitment dilemmas
- Faction identity
- Environmental adaptation

## Singular Story Assets

Possible, but deliberately non-scalable:

- One relic
- One utility mech
- One unusual recruit
- One irreversible biological intervention
- One unique recovered weapon or ship system

## Excluded Player Progression

- Psycasting
- Fluid ideology
- Genetics laboratory
- Royal permits
- Mechanitor armies
- Broad transhumanist optimization
- Multiple independent “hero power” systems

---

# 18. Additional Technology Expansion: Planning Direction

This remains an active planning topic rather than a finalized mod list.

## 18.1 Central Concern

A large technology expansion can easily reproduce the “too many ways to succeed” problem even without psychic or genetic systems.

The danger is not merely having more research projects. It is that broad technology mods often provide several interchangeable answers to every constraint:

- Multiple power systems
- Multiple armor tiers
- Multiple turret families
- Multiple medical solutions
- Multiple automation systems
- Multiple transportation systems
- Multiple resource synthesizers
- Multiple defensive shields
- Multiple forms of orbital fire support

This can make exploration rewards irrelevant because the research bench eventually manufactures an answer to everything.

## 18.2 Preferred Technology Philosophy

Additional technology should do one of three things:

1. **Deepen an existing ship dependency**  
   Example: better cooling that demands more deck space and rare coolant.

2. **Create mutually exclusive ship specializations**  
   Example: choose a medical laboratory, munitions plant, or advanced sensor suite because the hull cannot support all three.

3. **Enable a quest-earned capability that remains feedstock constrained**  
   Example: unlock advanced armor production, but only from rare alloys recovered at dangerous sites.

Technology should not:

- Create resources from nothing
- Remove fuel as a meaningful cost
- Eliminate heat or power management
- Replace all crew skills
- Make planetary expeditions optional
- Add a second complete automation framework
- Add several redundant weapon tiers with no meaningful tradeoffs
- Provide universal shields that trivialize tactical positioning
- Allow the player to research every branch without sacrifice

## 18.3 Candidate Structural Rule

Every major advanced technology could require both:

- A quest-earned schematic
- A permanent ship module or industrial control core

This makes research knowledge insufficient by itself. The crew must also dedicate physical space and scarce hardware to the capability.

Possible mutually exclusive advanced modules:

- Advanced medical synthesis
- Precision electronics
- Heavy munitions
- Exotic alloy processing
- Long-range sensor analysis
- Drone reconnaissance
- Environmental adaptation
- Gravship defensive systems

The campaign should not assume all of these fit aboard one vessel.

## 18.4 Open Technology Questions

Cowork should preserve these as discussion questions:

- How many advanced industrial branches should be available in one campaign?
- Should some branches be permanently mutually exclusive?
- Should the player see all branch options early, or discover them through quests?
- Is advanced armor a factory branch, a salvage-only asset, or both?
- Should high-end weapons be manufactured, reconstructed from recovered parts, or unique?
- Which technologies should consume rare expedition-only feedstocks?
- Which technologies increase power and cooling demand enough to reshape the vessel?
- Should ship expansion and industrial specialization compete for the same quest rewards?
- Should the campaign culminate in one final technological identity rather than universal mastery?

---

# 19. Making Enemies Truly Dangerous: Planning Framework

This is the next major design discussion. Specific enemy and combat mods have not yet been finalized.

## 19.1 Problem Statement

Vanilla RimWorld difficulty often scales through:

- More bodies
- More total raid points
- More hit points
- More simultaneous attackers
- Larger cleanup burden

That can create spectacle and attrition, but not necessarily a sense of facing an intelligent, highly capable opponent.

The target is:

> **Fewer enemies with dangerous capabilities, coherent tactics, clear objectives, and consequences that cannot be solved by one universal defensive pattern.**

The campaign should produce fights worth choosing, avoiding, or preparing for.

## 19.2 Desired Sources of Danger

### Capability

Enemies should possess tools that change the problem:

- Breaching
- Smoke
- EMP
- Shielding
- Suppression
- Long-range fire
- Area denial
- Fire
- Toxic or biological hazards
- Sensor disruption
- Kidnapping
- Sabotage
- Anti-armor weapons
- Counter-battery fire
- Mobile cover
- Jump or drop insertion
- Ship-system attacks

### Behavior

Enemies should act coherently:

- Use cover
- Concentrate fire
- Protect specialists
- Retreat when appropriate
- Flank fixed defenses
- Breach weak points
- Suppress while another group advances
- Target power, cooling, conveyors, fuel, or engines
- Attempt to steal a quest object rather than merely kill everyone
- Delay the crew while reinforcements approach
- Withdraw after accomplishing their objective

### Objectives

Not every battle should be extermination.

Possible enemy objectives:

- Destroy one field extender
- Disable the reactor
- Ignite the factory deck
- Steal an industrial control core
- Kidnap the engineer
- Prevent launch for a fixed period
- Hold a quest terminal
- Extract a valuable prisoner
- Mark the gravship for a later strike
- Force the crew to abandon cargo
- Delay evacuation until the pursuing mechanoids arrive

### Consequences

Failure should have intermediate states:

- Lose a module
- Lose cargo
- Lose a quest reward
- Launch with damage
- Abandon a pawn
- Accept a new pursuer
- Suffer a temporary systems penalty
- Lose access to one production branch
- Reveal the ship’s position
- Trigger a future revenge encounter

This is preferable to every fight ending in either total victory or colony destruction.

## 19.3 Encounter Design Principles

### Telegraph the Threat

Dangerous capabilities should be visible enough to permit preparation.

Examples:

- Reconnaissance identifies an enemy anti-armor team.
- A quest description warns of artillery.
- Sensor logs indicate breachers.
- A faction is known for fire weapons.
- A mech platform broadcasts EMP interference.

Surprise is useful, but completely opaque counters feel arbitrary.

### Preserve Counterplay

Every dangerous enemy capability needs at least two plausible responses.

Example:

**Enemy artillery**

Possible responses:

- Rapid assault
- Counter-battery weapon
- Sabotage expedition
- Launch before calibration completes
- Decoy position
- Shielded compartmentalization

No single response should work against every enemy archetype.

### Make Retreat Legitimate

The gravship campaign is unusually suited to retreat.

A fight can be “won” by:

- Recovering the objective and launching
- Saving most of the crew
- Denying the enemy the key item
- Buying enough time to finish repairs
- Leaving behind replaceable cargo
- Refusing an unfavorable battle

Enemy mods and encounter designs should not assume that wiping every attacker is the intended outcome.

### Attack the Ship as a System

The most interesting enemies should understand that the gravship is not merely a building cluster.

Priority targets may include:

- Power generation
- Cooling
- Fuel
- Conveyor junctions
- Factory control systems
- Grav engines
- Field extenders
- Life support
- Medical bay
- Cargo doors
- Sensor mast
- Bridge

This creates tactical defense-in-depth and makes internal layout meaningful.

## 19.4 Enemy Archetypes Worth Developing

### Elite Hunter Team

- Small number of highly trained enemies
- Specialized weapons
- Good armor
- Smoke and breaching tools
- Clear retreat behavior
- Objective: kill or capture one named crew member

### Industrial Saboteurs

- Avoid direct confrontation
- Plant charges
- Ignite fuel or conveyors
- Hack factory controls
- Objective: disable production and escape

### Anti-Ship Mech Cell

- EMP specialists
- Shielded heavy unit
- Repair/support unit
- Long-range targeting unit
- Objective: immobilize the gravship for the pursuing force

### Siege and Counter-Siege Force

- Artillery
- Spotters
- Mobile defenses
- Ammunition logistics
- Objective: force the crew to leave cover and attack

### Breach-and-Board Assault

- Multiple insertion points
- Heavy breacher
- Suppression team
- Fast interior assault unit
- Objective: seize the bridge, reactor, or quest cargo

### Biological Hazard Force

- Not merely large insects
- Contaminating attacks
- Nest growth in machinery spaces
- Crew isolation requirements
- Objective: make part of the ship uninhabitable until purged

### Rival Salvage Crew

- Comparable small expedition
- Competes for the same quest objective
- May negotiate, betray, retreat, or return later
- Objective: take the artifact rather than destroy the colony

### Pursuer Vanguard

- Arrives ahead of the main pursuing force
- Marks targets and disables launch systems
- Weak enough to defeat, but dangerous if allowed to complete its mission
- Objective: delay rather than annihilate

## 19.5 What to Avoid

- Simply multiplying raid points
- Huge bullet-sponge enemies
- Untelegraphed one-shot attacks
- Universal shield enemies with no counterplay
- Permanent immunity stacks
- Endless drop-pod spam
- Enemies that ignore all terrain and defenses without explanation
- Enemies whose only distinction is higher armor and damage
- Raids so large that performance degradation becomes the primary challenge
- Combat mods that make every weapon instantly lethal without supporting retreat, medical play, or readable tactics
- A single “best” defensive geometry that solves every encounter

## 19.6 Combat Difficulty Should Be Selective

Not every raid should be a set-piece battle.

Suggested distribution:

- Many minor threats that consume time and supplies
- Occasional dangerous specialist encounters
- Rare campaign-defining battles
- Some threats best avoided
- Some battles voluntarily accepted for unique progression
- Some enemies that remain frightening throughout the campaign

The player should recognize certain factions, units, or signals and think:

> “We are not ready to fight that yet.”

That reaction is more valuable than constantly increasing enemy quantity.

## 19.7 Relationship to Technology Expansion

Enemy escalation and player technology must be designed together.

If enemies gain:

- Heavy armor, the campaign needs limited anti-armor tools.
- Artillery, the campaign needs reconnaissance and rapid assault options.
- Shields, the campaign needs disruption or positional counterplay.
- Sabotage, the ship needs compartmentalization and repair capacity.
- Boarding, internal corridors and security doors become meaningful.
- Electronic warfare, sensors and manual backup systems matter.

The response should not always be “research a better gun.” Ideally, enemy capability forces:

- A ship redesign
- A new expedition
- A specialized module
- A difficult recruitment decision
- A change in route
- A willingness to retreat

## 19.8 Evaluation Criteria for Enemy Mods

Before accepting an enemy or combat mod, evaluate:

1. Does it create new behavior or merely larger numbers?
2. Are dangerous capabilities legible?
3. Does the player have multiple counters?
4. Can enemies pursue objectives other than extermination?
5. Do enemies threaten ship systems intelligently?
6. Can a small elite group remain dangerous at high wealth?
7. Does it support retreat and partial failure?
8. Does it create unavoidable one-shots or opaque immunity?
9. Does it preserve performance with a small crew?
10. Does it integrate with Odyssey, gravships, and temporary maps?
11. Does it require a broad weapons mod that adds excessive player power?
12. Can its rewards be prevented from bypassing quest-gated progression?

## 19.9 Discussion Conclusions (2026-08-02) — lever framework + mod mapping

**Core reframe — THREE orthogonal levers, usually conflated:**
1. **AI behavior** — how enemies fight with the bodies they have (cover, flanking, suppression, retreat).
2. **Roster / capability** — what enemies exist and what tools they carry.
3. **Encounter framing** — frequency, telegraphing, objective, consequence.
Vanilla difficulty scaling only pushes lever 2.5 (more bodies/points). The "we are not ready to fight *that* yet" feeling lives mostly in levers 1 and 3 — where most modlists under-invest. **Biggest qualitative gain per unit cost is smarter AI + disciplined storyteller settings, NOT a content pack.**

**Zero-cost foundation (stock 1.6, established):** vanilla **Custom difficulty** already exposes the key dials — lower raid *frequency* while raising raid *points*, turn off adaptation decay. (⛔ There is no "enemies flee at X%" dial — `DifficultyDef` has no such field and fleeing is decided in code.) This alone produces the §19.6 "fewer, heavier" distribution before any mod loads. DO THIS FIRST; tune mods on top.

**Mod → archetype mapping (thematic + technical fit; all Odyssey-1.6 compat pending Fetcher verification — knowledge cutoff May 2025):**
- **Combat-AI mod (e.g. CAI-5000)** → delivers §19.2 "Behavior" wholesale (dynamic cover, flanking, suppression, retreat). Makes a 6-pawn elite team scary with NO extra bodies → directly serves criterion 6. **Recommended FIRST adoption.** *(Inference — regarded well at cutoff; verify live.)*
<!-- canon-ok: "criterion 11" is a criterion number, not a faction count. -->
- **Combat Extended** → **❌ FORBIDDEN (2026-08-02, user's call).** Compat surface + over-arms the player (tension w/ §19.5 + criterion 11) + temp-map risk. Recorded in forbidden_mods.md. Keep base game vanilla-lethal; danger comes from AI + factions + difficulty tuning, NOT a lethality overhaul.
- **VFE-Mechanoids** → "Anti-Ship Mech Cell" + "Pursuer Vanguard"; dovetails with the Odyssey pursuing-mechanoid premise the campaign is built on.
- **VFE-Pirates** → "Elite Hunter Team" (warcasket heavy-armor elites).
- **VFE-Insectoids 2** → "Biological Hazard Force"; nest growth = part of ship uninhabitable-until-purged = a SYSTEM attack, not a body count.
- **VFE-Deserters** → stealth/oppression questline w/ targeted strikes.
  (All four ride on VEF which is already IN → near-zero friction; qualitative; support non-extermination objectives; rewards checkable vs criterion 12 → THIS is why their source is in the local library.)
- **Alpha Animals** → qualitative wildlife danger (teleport/acid/EMP-like attacks = "capability changes the problem"). Rides FREE on the already-IN Alpha Biomes decision (same author, designed to pair).
- **Manhunter packs (vanilla)** → the "many minor threats that consume time+supplies" tier (§19.6); ignore defensive geometry → punish a single turtled layout. The exploration loop (crew OFF the ship) is structurally exposed to stalking predators — danger vanilla already does well, amplified by this campaign.

**⚠️ HONEST GAP (load-bearing):** the most DISTINCTIVE archetypes — Industrial Saboteurs ("plant charges, hack factory controls, disable production and escape") and Pursuer Vanguard ("disable launch systems") — are the HARDEST to source. RimWorld raider AI targets *pawns and walls*; it does NOT natively understand "ignite the conveyor deck" or "hack the reactor." Sappers/breachers approximate ship-as-system (weak-point/interior routing); mechanoids can be pointed at structures better than humans. But true objective-driven sabotage is a **scripted-quest/event** capability, not emergent AI. → This tier needs either a specific EVENTS mod (evaluate Vanilla Events Expanded et al.) OR small custom quest scripting (same Phase-B territory as the progression mod). **Status: ASPIRATIONAL-PENDING-MECHANISM — do NOT assume a mod delivers it.**

**Layered recommendation:** (1) tuned Custom difficulty + smarter-AI = foundation; (2) VFE-Mechanoids/Pirates/Insectoids-2 = 4 of 8 archetypes, clean fit; (3) Alpha Animals = free with Alpha Biomes; (4) saboteur/launch-denial = parked as scripted-event question, NOT pretended-solved. **Principal risks:** CE's compat + player-power problem (→ defer); performance if faction packs stack raid variety on regenerated maps (→ mitigated by small crew + frequency-down dial).

**✅ ACCEPTED (2026-08-02, user):** the layered recommendation as written — tuned Custom difficulty + CAI-5000 foundation, VFE-Mechanoids/Pirates/Insectoids-2/Deserters for archetypes, Alpha Animals free on Alpha Biomes, manhunter attrition tier. **Combat Extended = FORBIDDEN** (keep vanilla-lethal). Source repos for all five enemy mods downloaded for §19.8 checklist evaluation (`mod_sources/`, Fetcher `2026-08-02_enemy_faction_mod_sources`).
**STILL OPEN:** (a) which lever to lean hardest on — AI/behavior vs roster variety vs encounter scripting; (b) the saboteur/launch-denial archetypes' mechanism (events mod vs custom scripting — ASPIRATIONAL-PENDING); (c) per-mod checklist verdicts once sources are read.

---

# 20. Current Accepted Decisions

These are considered accepted unless later playtesting overturns them:

- The campaign is a nomadic gravship expedition.
- The entire permanent colony lives aboard the ship.
- Vanilla Furniture Expanded - Factory is the central production system.
- Production and hull growth are quest-gated.
- One inherited provisioning line exists at campaign start.
- The ship and factory are the only scalable advancement trees.
- No player psycasting.
- Xenotypes are welcome, but biology is fixed per individual or population.
- No player genetics laboratory.
- Ideology is fixed, likely Shipborn-centered, and functions as a constitution.
- No ideology production or combat specialists.
- Rituals create cohesion, not material rewards.
- At most one culturally important relic.
- Royal titles and permits are not a player progression route.
- Mechanitor progression is excluded.
- Broad transhumanist optimization is excluded.
- Dangerous enemies should rely on capability, behavior, and objectives rather than numbers alone.

---

# 21. Provisional Decisions

These remain plausible but unconfirmed:

- One irreplaceable utility mech may exist.
- One non-scaling psychic story character could exist, though current preference is none.
- One irreversible genetic intervention may occur as a major quest choice.
- Advanced technologies may require both schematics and installed control modules.
- Some advanced industrial branches may be permanently mutually exclusive.
- A single major relic quest may anchor the ship’s cultural history.
- Enemy factions may receive strongly differentiated tactical doctrines.
- Certain battles may be designed around disabling or escaping rather than annihilation.

---

# 22. Open Planning Agenda for Cowork

Cowork should use this document as discussion context and help continue analysis on the following topics rather than immediately implementing them:

1. Identify a small set of compatible technology expansion mods that deepen ship dependencies without creating universal self-sufficiency.
2. Identify combat-AI and enemy-faction mods that create qualitatively dangerous opponents rather than merely increasing raid size.
3. Determine whether a combat overhaul is necessary, and what problems it would solve or create.
4. Design three to five enemy doctrines with distinct capabilities, objectives, and counters.
5. Determine how enemy escalation should relate to factory milestones and field extenders.
6. Determine which player weapon and armor technologies are necessary responses, and prevent unrelated technology bloat.
7. Determine how shipboard combat, boarding, sabotage, and module damage can work within Odyssey’s actual mechanics.
8. Determine whether authored quests, incident patches, scenario rules, or custom C# are required for non-extermination enemy objectives.
9. Preserve the possibility of retreat, partial victory, lost cargo, damaged modules, and recurring enemies.
10. Produce recommendations with explicit tradeoffs and compatibility risks rather than a single undifferentiated mod dump.

---

# 23. Cowork Discussion Prompt

```text
Treat the attached Gravship Campaign Planning Discussion as an evolving design document, not a frozen implementation specification.

Continue the planning discussion around two connected questions:

1. Which additional technology mods, if any, deepen the gravship’s industrial and logistical identity without creating several parallel ways to become self-sufficient?
2. Which enemy, faction, combat-AI, and encounter mods can create genuinely dangerous opponents through capabilities, tactics, objectives, and attacks on ship systems rather than simply increasing raid size?

Preserve the accepted constraints:
- The gravship and onboard factory are the only scalable progression trees.
- No player psycasting.
- Xenotypes are fixed for each person or population; no genetics laboratory.
- Ideology is fixed and restrictive, not fluid or economically productive.
- No royal-permit progression, mechanitor army, or broad transhumanist optimization.
- Production upgrades and ship expansion are quest-gated.
- The player should sometimes avoid, escape, or partially lose encounters.
- Small elite enemies should remain threatening.
- Avoid mod combinations that give the player more power than the enemies or make expeditions unnecessary.

For every proposed mod or design:
- Explain what problem it solves.
- Explain what new power it gives the player.
- Explain what new danger it gives enemies.
- Identify overlap with existing systems.
- Identify compatibility and performance risks.
- State whether it should be included, conditionally included, or rejected.
- Prefer a compact curated package over a large mod list.
- Distinguish verified current mod behavior from speculation.
- Keep open questions visible where evidence or playtesting is still needed.
```
