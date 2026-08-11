# How Mr Samuel Streamer Builds Worlds — Technique Analysis

_Built 2026-08-02 from direct inspection of his downloaded config archives and mod-lists (not from video/description hearsay). Every claim below is tagged: **[evidence]** = read directly from his files, **[inference]** = reasoned from the evidence, **[speculation]** = plausible but unconfirmed._

This studies three questions: (1) what he does *mechanically* to build custom worlds, characters, races, and scenarios; (2) the storytelling themes and tricks underneath; (3) how our Jawa gravship run can borrow the method without breaking our pillars.

---

## Part 1 — The mechanical toolkit

The central discovery: **Samuel almost never writes new content. He curates and re-weights existing content using a small, stable set of "director" mods, then hand-authors a thin layer of custom pawns and lore on top.** The same ~10 control mods recur across 20+ of his packs regardless of theme. That stability is the actual skill — the theme changes, the machinery doesn't.

### 1a. Faction control — *Sensible Factions* ("Faction Filter", WS 3531306011)

**[evidence]** In Gravtasm his config lists exactly 24 `allowedFactionDefNames` (SpacerRough, CannibalPirate, Empire, various tribal/pirate/xenohuman defs) and one `selectedFactionDefName` (SpacerRough) as the player faction. Every faction *not* on the allow-list is suppressed from world generation.

**[inference]** This is his primary "who lives in this world" lever. Rather than accept RimWorld's default faction soup, he decides the cast of the world up front and filters to it. A pirate-heavy world, a spacer world, an empire-dominated world — all the same mod, different allow-list.

### 1b. Content removal — *Cherry Picker* (WS 3521312241)

**[evidence]** Gravtasm's CherryPicker config deletes **62 defs**: 26 XenotypeDefs, 21 FactionDefs, 12 ScenarioDefs, plus a few Thing/Recipe/Gene defs. He strips out xenotypes and factions that don't fit (Dirtmole, Sanguophage, Neanderthal, Pigskin, various Alpha Genes races) and even removes 12 scenario definitions so the scenario picker only offers what he wants.

**[inference]** This is the counterpart to Faction Filter: Faction Filter controls spawns, Cherry Picker removes the *option* from menus and generation entirely. Together they turn a 587-mod kitchen into a curated menu. Removing ScenarioDefs is notable — he narrows the player's starting choices to force the intended experience.

**[inference — this is the key discipline]** He runs 300–680 mods but the world doesn't *feel* like 680 mods because Cherry Picker + Faction Filter prune the combinatorial explosion back down to a coherent set. **Big library, small curated surface.**

### 1c. Worldgen shaping — *Map Designer* (WS 2111424996) + *Choose Biome Commonality* (WS 2582875043) + *Choose Wild Animal Spawns* (WS 2564042934)

**[evidence — Map Designer, Warlock pack]** He directly edits terrain generation: `densityRuins = 0`, `densityDanger = 0` (no ancient danger/ruins), `densityAnimal ≈ 0.98`, `densityOre ≈ 1.21`, plus per-ore commonality tables. He's sculpting what the local map physically contains.

**[evidence — Choose Biome Commonality, League of Villains]** He re-weights *which biomes exist on the planet*. Values range from `0.42` (Space, suppressed) up to `4.7` (Lake), `4.3` (Orbit/IdyllicMeadows), `4.2` (Glowforest). Default is 1.0, so anything above is amplified and below is rarefied. He's tilting the whole planet toward the biomes that serve the theme.

**[inference]** Worldgen is a three-layer stack for him: planet biome mix (Choose Biome Commonality) → faction placement (Sensible Factions) → local map contents (Map Designer). He tunes all three per pack.

### 1d. Custom characters — *Backstory Constructor* (WS 2907131508)

**[evidence]** This is how he authors *named characters with lore*. In Gravtasm he defines backstory templates like **"Twenty-Five Star General"** with hand-written prose ("a high-ranking member of the Star Federation, earnt through shocking levels of valor, wit, and old-fashioned elbow grease... usually confers a captaincy, ship, and crew") plus a full `skillGains` table and `workDisables` map. He controls exactly what each character is good at and forbidden from doing.

**[inference]** His "characters" aren't random colonists — they're pre-written personas dropped into a starting save. The backstory carries both narrative (the prose) *and* mechanics (skills/work-disables), so a character *reads* like their role and *plays* like it too. This is the single most transferable technique for us.

### 1e. Custom races — *saved Xenotype* files (native RimWorld export)

**[evidence]** War on Christmas shipped a `savedXenotype` XML (game's native format, `<savedXenotype>` root with `<gameVersion>` and gene list) alongside its configs. This is RimWorld's built-in xenotype editor output — no special mod required.

**[inference]** For custom races he uses the vanilla Character Editor / xenotype export, saves the `.xml`, and distributes it so players can import the same custom xenotype. Simple, mod-free, portable.

### 1f. Scenario definition — starting saves + ScenarioDef pruning

**[evidence]** His master index repeatedly ships a **"starting save"** per collection, and Cherry Picker removes competing ScenarioDefs. The index text itself warns that "starting saves may contain hidden setup work: scenario parts, world generation, factions, custom pawns, xenotypes, and map edits."

**[inference]** The *scenario* isn't authored as a distributable ScenPart mod — it's baked into a **starting save** that already contains the generated world, the placed factions, the custom pawns (with their Backstory Constructor identities), and the map. The configs + mod-list reproduce the *rules*; the save reproduces the *authored starting state*. This is why he says configs are essential, not cosmetic — the save assumes them.

### 1g. His own glue mod — *MrSamuelStreamer Flavour Pack* (MSSFP, appears in 14 packs)

**[evidence]** A custom C# mod he wrote, with bespoke narrative knobs: `EnableGraveHaunts`/`ShowHaunts` (dead colonists haunt), `EnableLoversRetreat`, `FactionLeaderRaidChance ≈ 0.20`, `AnnualReformationPoints`, `WanderDelayTicks`, `DaysForFission = 20`. Also `DrawByMrStreamer` (his art).

**[inference]** Where an off-the-shelf mod doesn't exist for a narrative beat he wants (ghosts of the dead, faction leaders personally leading raids), he built a small mod to supply it. Most of us won't write C#, but the lesson stands: identify the *specific* narrative mechanic your story needs and find/make the one mod that delivers it, rather than adding ten generic ones.

---

## Part 2 — Storytelling themes and tricks

### Trick 1: One-sentence premise, then subtract everything that contradicts it
**[inference from evidence]** Every pack has a single legible hook (Mafia City = contraband empire; Twilight = permanent darkness, 10 humans left; Degeneration = technology runs *backwards*). The config work is overwhelmingly *subtractive* — Cherry Picker removes off-theme xenotypes/factions/scenarios, Faction Filter removes off-theme spawns. The theme is defined as much by what he *deletes* as what he adds.

### Trick 2: Constraint as narrative engine
**[evidence]** Twilight = "10 colonists are the planet's only humans, every death is permanent to the species." Thirst = "clean water is the primary strategic resource." Degeneration = "6 embryos, a star erasing technology." **[inference]** He picks one scarce resource or one hard rule and lets the storyteller generate drama against it. The mechanic *is* the story. (This is exactly our anti-exponential instinct.)

### Trick 3: Faction alignment as casting, not accident
**[inference from 1a/1b]** He treats the faction roster like casting a show. Villain packs foreground pirate/hostile factions; the character-driven Gravtasm keeps civil spacers and outlanders (social partners, trade, romance) and one Empire antagonist. The *emotional* register of a playthrough (paranoid? social? besieged?) is set by which factions he allows to exist.

### Trick 4: Immersion by amputation of the vanilla baseline
**[evidence]** Gravtasm runs **NoVanillaWeapons** + **NoVanillaApparel**. **[inference]** Removing vanilla guns/clothes forces the modded, theme-appropriate content to be the *only* content, so the world stops feeling like "RimWorld plus a mod" and starts feeling like its own setting. Powerful, and risky (can gut the item economy if done carelessly).

### Trick 5: Named characters carry both lore and mechanics
**[evidence, 1d]** The "Twenty-Five Star General" reads as a character and plays as one (specific skills, specific work-disables). **[inference]** A recurring cast the audience recognizes across episodes is his signature; the Backstory Constructor is the mechanism. Characters, not colonists.

### Trick 6: A stable "foundation" underneath every theme
**[evidence]** His 1.6 Foundation Pack (167 mods) and Bare Essentials (35 mods) exist as reusable substrates; the QoL/UI/performance mods (PerformanceOptimizer, FacialAnimation, DubsMintMenus, SmartSpeed, ShowMeYourHands) recur in 22–26 of 26 packs. **[inference]** He separates the *invariant plumbing* from the *variable theme*. He builds a new world by swapping the theme layer on top of a frozen foundation — which is why he can ship a new pack often.

---

## Part 3 — What this means for the Jawa / crashed-Factory-ship gravship run

Bottom line up front: **Samuel's method is a near-perfect fit for our pillars, because his core discipline (big library, small curated surface, subtractive theming) is mechanically identical to our anti-exponential principle. We should adopt his *method* wholesale while keeping our *content* far leaner than his 300–680-mod packs.**

### Directly reusable, high confidence

**Bounty Hunter (#24) is a gift.** **[evidence]** Its mod-list uses the *exact* Outer Rim modules we've already selected — `outerrim.core`, `droiddepot`, `galacticdiversity`, `separatists`, `mandalore`, `oldrepublic`, `galacticrepublic`, `csilla` — plus `starwars.music`, `starwarsanimalcollection`, `theforce.psycast`, and a nomad stack (CaravanAdventures, SetupCamp, SaveOurShip2, VanillaVehiclesExpanded, WanderingCaravans). **[inference]** He has already solved the "assemble a coherent Star Wars faction roster from Outer Rim" problem we were about to tackle from scratch. His load-order for those modules is a validated reference — we can diff our intended order against his. (Note the divergences we must preserve: he uses The Force psycast and SaveOurShip2; we've *forbidden* both — The Force violates the psycast ban, SoS2 competes with VGE. So we borrow his faction/nomad layer, not his ship/psycast layer.)

**Adopt his three-layer worldgen for our run:**
- *Choose Biome Commonality* → tilt the planet toward the biomes that suit a scavenger-nomad gravship story (rarefy lush/safe biomes, amplify desert/wasteland/harsh so scarcity is baked into the map). **[fits scarcity pillar]**
- *Sensible Factions (Faction Filter)* → hand-pick the cast: the Outer Rim factions we want as live enemies (Empire, Separatists) + a couple of trade/neutral outlanders, and suppress the rest. This is our "Empire-as-pursuer" casting done cleanly. **[directly serves the Empire-pursuer decision already in context]**
- *Map Designer* → set `densityDanger`/`densityRuins` deliberately (we may want ruins *up*, not zeroed like Warlock — a crashed-ship scavenger world should be littered with salvage), boost ore/component density to feed the Factory, tune animals.

**Cherry Picker is our anti-bloat enforcer.** **[inference]** This is the single most pillar-aligned tool he uses. We can delete every off-theme xenotype and faction the Outer Rim/HAR stack drags in, prune the scenario picker to only our crashed-Factory-ship start, and thereby keep the *curated surface* tiny even though the *library* is large. This is the mechanical embodiment of our 7-question test — Cherry Picker is how we enforce "this doesn't belong in our world" without uninstalling the mod that provides a needed dependency.

**Backstory Constructor for the Jawa crew.** **[inference — highest-value creative borrow]** Author each starting Jawa (or human survivor) as a named character with hand-written lore tying them to the crashed Factory ship, plus skill/work-disable tables that make them *play* their role. E.g., a "Salvage-Chief" persona with high Crafting/Mining and disabled Social; a "Ship's Ghost" former engineer. This gives us the recurring-cast feel with zero C#.

**Bake the scenario into a starting save.** **[inference]** Rather than fighting the scenario editor, generate the world once with our filters/biomes applied, place the crashed Factory gravship, drop the authored crew, then save. The save + our mod-list + our configs = a reproducible, shareable starting state. This is his distribution model and it sidesteps the "agonizing native mod UI" you mentioned.

### Borrow with caution
- **NoVanillaWeapons/Apparel (Trick 4):** tempting for Star Wars immersion (blasters only, no assault rifles), but it can gut the early item/trade economy and interacts with our Outer Rim weapon-balance audit (still open in context §19.5). **[recommendation]** Defer until after the weapon audit; test in a throwaway save first.
- **His scale:** 587 mods is the *opposite* of our brief. **[recommendation]** Take his *control mods* (the ~10 directors) and his *method*, explicitly **not** his content volume.

### Does NOT transfer / must diverge
- **The Force psycast** — violates our psycast ban. Skip.
- **SaveOurShip2** — competes with VGE (our sole gravship layer). Skip; VGE is our ship.
- **MSSFP haunts/reformation-points** — his personal flavor; not our theme.

### Recommended next actions (decision-ready)
1. **Diff exercise:** compare our intended Outer Rim load-order against Bounty Hunter's `.rml` to validate/borrow his ordering. Low effort, high confidence payoff.
2. **Draft a Cherry Picker kill-list** for our stack (off-theme xenotypes/factions/scenarios) — this operationalizes the anti-exponential test.
3. **Draft 3–5 Backstory Constructor personas** for the founding Jawa crew (lore + skill tables).
4. **Draft a Choose Biome Commonality + Map Designer profile** for a scavenger-scarcity planet (harsh biomes up, salvage/ruins up, safe biomes down).
5. **Decide** whether the scenario ships as a starting-save (his model) or a lighter scenario-only definition (more portable, less authored).

**Principal risk:** copying his *content* instead of his *method* would blow straight through the anti-exponential pillar. The value here is the curation machinery, not the mod haul.

**Missing information that would help:** his actual *starting saves* (not downloaded — you asked for lists/configs only) would show exactly how scenario parts, custom pawns, and map edits are assembled. If we commit to the save-based scenario model, pulling Bounty Hunter's and Gravtasm's starting saves would be the highest-value next download.
