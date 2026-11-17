# Page one — what the Wastes becomes

The Wastes is dry, poisoned ground where old wrecks outlast the people who came to strip them. You keep a habitable refuge while ash storms move contamination and expose or bury useful remains. Tough native life endures the poison, and its radiotrophs help you compare dangerous ground while slowly binding contamination beneath a recovering crust.

Land: salt, ash, broken asphalt, brine and preserved remains, with cleaner reachable construction ground; no rain or snow.

Life: current residents stay, with ordinary feeding, breeding, taming, milk and eggs; tough survivors, environmental danger first. No species is evicted.

Signature: ash moves and adds mobile contamination, so settlers must read changed ground and maintain a habitable refuge while radiotrophs bind poison beneath the crust.

I chose this from your November refuge-maintenance answer. The living furnace was the runner-up: a good heat-for-dose bargain, but another management system. The giant is the strongest spectacle; it does not make the quiet day consequential.

Next version, switched off:

- Living furnace heat and animal radiation auras.
- Pollution-fed herd products, animal cleaning and excretor bezoars.
- Gripper theft, carried junk and special drops.
- Deadlight Halo and Cinderwire, including their warnings and effects.
- Brine beds, raw-brine shock and plate processing.
- Middenshell arrival, crushing, grabs, lure, trail and quarry; separate native titan passage.
- Waste casks, bays, processing, special launch veto and reburial.
- Rite of Tipping, evidence requests, grants and discovery penalties.
- Targeted Grimewing circling, real sealed-Junker corpse scatter and bespoke root-vault fuel extraction.

I recommend retiring the custom raw-milk mood bonus because ordinary food quality already does that job, and special raw-pusberry poisoning because ordinary food handling suffices. The berry currently yields ordinary berries; no global poisoning change is proposed. These are recommendations, not retirements.

Census capabilities: 71; kept in this first version: 35; next version: 34; recommended retirements: 2. The census includes dependencies and unbuilt promises. Review added initial buried salvage and regime/horizon light. Previously locked bars: 0; proposed bars: 8; live-only bars: 2. The two human looks concern land/light and readable route comparisons; other experiences use state evidence with game-calibrated instruments. Existing art remains accepted.

# Page two — what to check

My consequential defaults:

- Refuge needs clean ground, roof and upkeep. Warm-basin wastepacks use a powered freezer, margin stores need verified freezing with powered fallback, and cold-scour stores stay frozen away from heat. Vanilla atomizers or actual off-map hauling provide final disposal when available.
- “Nothing leaves” means no natural flushing outlet, not a ban on cleanup, hauling or tracked boundary flows.
- Bare ground is not a safety certificate. Recent fall, buried/dead markers and loaded roots require honest existing inspection.
- Vegetation and visible ground must rank comparable routes with vanilla pollution overlay and cell readout hidden. Inspection refines the choice. Radmoss follows projected pollution that actually doses, with visible weather/cover supplying airborne context. Hidden subthreshold stock cannot invent a danger difference.
- Ash moves old contamination as well as adding fallout.
- Outside grid writes enter the account once, including cleanup, dissolution, ash fall and Biotech sinks/sources. Projection cannot undo completed cleanup without new inflow.
- Plants retain bound poison; destroying loaded roots releases it once, including fire and shared growth-system death. No extra ore economy is needed.
- Preservation covers ordinary rot in warm basins too. Wastepacks still dissolve by vanilla rules and return pollution when unfrozen.
- Resident species stay when their special behaviour moves. Native drinking and real flight remain standing requirements.
- The all-biome scanner payload stays as a dependency, without new authority to certify safe routes.
- The building Middenshell is separate from a titan pawn pool. Its ruled width is preserved for later.
- A finite buried hoard exists before settlement. Natural storms must expose its original finds in the entry season. A saved once-only initializer also handles legacy adoption. Reload and exhaustion never refill it.
- The permanent cold-scour stormwall horizon is retained land light. Its missing directional binding is ticketed, independent of electrical weather and heat.
- Deferred contract liability still ends with its term; physical pollution persists.
- “Off” stops callbacks, jobs, effects and active schedules, not merely menu visibility. Existing saved things suspend readably rather than vanish.

No questions. These are my delegated decisions. The reviewer identified these gaps, and I repaired their definitions and evidence requirements.

Models, first to build first:

- Supported-situation generator covers grid writers, native-cache manifests, dissolution, destruction, reloads and reordered work.
- Full-map contamination/refuge season includes real wastepack dissolution, climate-specific storage, power/hauling failures and natural exhumation.
- Exposure geometry/readable-ground sweep tests landscape-led route choice and directional horizon light against actual game views.
- Food/rot/salvage balance: verify residents can live, ordinary husbandry works, warm supplies persist and salvage protection matters.

Still empirical are whole-map viability, real sensing/storage/transfer adapters, warm preservation, authored shelter and horizon light. Models test ash hiding indicators, root death releasing stock and cleanup waste dissolving back into the refuge. Instruments and tickets cover these risks.

Checks: 10; rules: 9; unknown meetings: 7; models: 4; tickets: 37; questions: 0. The whole bar requires a complete occupied season, natural unlocked weather, a middle save/reload and reordered work. Models are predictions until their records agree with the game. This pass ran no game, bridge, build or art production.

Application awaits your reading and approval plus completion of review. The reviewer’s second look is still pending.

## Still refused after the second look (the reviewer's words)

The proposal cannot be applied until each of these is resolved or you accept it.

- an extra left in the first version without its needed_by deletion argument (design/concepts/Wastes/cleanse/census.json row initial_buried_hoard (fate "signature", built "absent"); bars.json B5 says/range/control; R2 hoard clauses; C4; T40 second paragraph). The one-sentence signature on owner_pages.md line 9 and in result.json is "ash moves and adds mobile contamination, so settlers must read changed ground and maintain a habitable refuge while radiotrophs bind poison beneath the crust". It says nothing about exhumation or salvage. Yet the hoard row is filed as `signature`, with an empty `needed_by`. It is an unbuilt new system: a versioned once-only initializer with a saved manifest, legacy-map migration and partial-commit retry (definition.md 'Using it'; T40). Its 'why' says deleting it defeats "the sourced changed-map promise". But the changed danger map is already carried by the kept `redistribution` row, and the reason to venture out is carried by Wreckage salvage (B7). B5 then turns the hoard into a passing condition ("naturally exhumed pre-settlement finds"). wastes.md §7 lists "the exhumation lottery" among the 'uniquely available' items, next to excretor refining, the living furnace and the tipping fee, which this same pass deferred. Would pass: Either the census row is `needed_by` with a real deletion argument naming the kept bar that fails without it, citing wastes.md §4b's doctrine-grade note ("what's out there is a live question twice a season"), and the signature sentence on his pages names exhumation as part of the one chain. Or the initializer/manifest machinery moves to the next version and B5 no longer requires pre-settlement finds. Smallest fix: Move initial_buried_hoard to next_version.md with a spec-only ticket. Strike "and naturally exhumed pre-settlement finds" from B5 says, its accept picture 5 clause and reject picture 3. Drop the entry-season arms from the B5 and B8 ranges and controls, and the hoard clauses from R2, C4 and T40.
- a kept mechanic with no definition (census.json row initial_ground (built "unknown", fate "land"); definition.md 'Using it' first sentence; bars.json R5 ("Initial local ground must already express native danger and construction choice"); T40 ("First inventory actual inherited ground")). B1, B3 and B4 all depend on a fresh map that already carries a native contamination pattern with cleaner construction ground. The definition asserts "the map already contains native mobile pollution", but no file says where that pollution comes from. RM_BiomeWorker_Wastes.cs has no pollution code. RM_Wastes_Biome.xml has no pollution initializer. The census evidence itself says "no explicit native-stock initializer". Two very different builds fit the words: (a) vanilla Biotech pollution inherited from the world tile, which is set only at the final paint (paint_plan row: "not executed here"); or (b) a new local-map GenStep with some unstated pattern relative to ash, wrecks and brine. Neither the pattern nor its source is defined, so a builder and a judge would build and test different mods. Would pass: definition.md and R5 name the source of initial native contamination. Either it is inherited tile pollution, stating what a test map uses before the final paint, or it is a named local initializer, stating which terrain or features it correlates with, how cleaner ground is left, and that it runs once per map. T40 carries its acceptance test. Smallest fix: Add one paragraph to definition.md 'Costs and state transitions' and one clause to R5 choosing (a) or (b) and stating the spatial rule in words without numbers. Change initial_ground's ticket scope in T40 from 'inventory' to 'implement the stated source'.
- two bars, or a bar and a rule, that cannot hold together (bars.json B1 (says "recognizably different basin, margin and cold-scour light"; range "Tile lighting uses actual fixed-world position, never a region-name override"; start "no debug light overrides") and B8 range (warm/margin/cold full maps), against the paint-once-at-the-end ruling (CLAUDE.md; biome_rulings.md) and the one-def ruling (wastes.md §0: the wastelands vary "only by the mutators and Inhabited injections assigned to each family")). definition.md 'Neighbours' says the regimes "vary by existing authored local settings, mutators and injections". Those family assignments are part of the final planet paint (census paint_plan row: dependency, not executed here), and until then an RM_ biome on zero tiles is expected. The only existing site instrument, src/RimMandrake/Wastes/northstar_site.py ensure_wasteland_map, re-tiles one scratch-world tile near the colony and runs `world_mutators_set action=clear`, with a written SITE_TEMPERATURE. So it yields neither a family's mutators nor a chosen arc. With actual fixed-world positions and no overrides required, B1 and B8 have no sanctioned starting state before the final paint. The mod could not pass the pipeline until the planet is painted, which defeats the purpose of the pass. Would pass: B1 and B8 `start` name a sanctioned disposable-site recipe that yields each regime before the paint: a scratch tile at a stated arc with that family's mutators applied, light coming from tile geometry. Or B1's regime clause is limited to what tile geometry gives, with family-specific mutator content declared outside the range until the paint. Smallest fix: Add to B1 and B8 `start`: "regime sites come from a scratch-world tile at the family's arc with that family's mutators applied in the disposable save (extend northstar_site.py; ticket under T44), never the canonical world". Add to `left_out`: "family content that exists only after the final paint".
- a figurative word unmarked (bars.json B8 says ("uniformly lethal", "overwhelmed by errors"); figurative: []). B8 says "without the map becoming uniformly lethal, harmless, stalled or overwhelmed by errors". Its own control defines these as something else: "Flood means all reachable refuge/work choices become untenable under ordinary maintained play" and "error storm means repeated faults". Neither is literal lethality everywhere or being literally overwhelmed. A literal reader could pass a map that is untenable but not lethal everywhere, or refuse a run over a single recurring error. Yet `figurative` is empty. Would pass: B8 `figurative` lists "uniformly lethal" (stands for: no maintainable refuge or work choice remains under ordinary maintained play) and "overwhelmed by errors" (stands for: repeating faults that stop or corrupt ordinary play), each with one accept picture that departs from the literal reading. Smallest fix: Fill B8's `figurative` with those two entries, reusing the control's definitions, and add one accept picture each (for example, a run where some outside cells are lethal but a maintainable refuge and work route remain).
