# BROADEN: SEA_FLOOR_AND_CATCH_PASS_1, 2026-11-11

The second opinion came from GPT (`gpt_consult.py --codex wsl`, model gpt-6.1-sol). This is a different model from the one that built the work, and it was given no files.

## The question (verbatim)

Statement owed (RimWorld 1.6 mod): "Every sea describes BOTH its floor (animals you meet by diving) and its catch (fish from the shore)" for four seas (RM_TheScald, RM_GreySea, RM_TwilightSea, RM_TheChill = a propane lake). The gravship is the only way down: it flies to a planet layer RM_SeabedLayer; at startup RM_SeabedFloorLife copies each sea's wildAnimals/fishTypes/plants onto its RM_SeabedFloor_<Sea> biome (animalDensity = sea x factor); a GenStep reasserts. Shore: a Harmony patch makes land tiles beside our seas coastal and lays a per-sea RM_SeaCoast mutator; WaterBody.SetFishTypes is redirected to that sea's catch table.
Tested so far, OFFLINE only (no game available in this lane): an XML census parsing 3009 files says 0 catch species in any of the four seas lacks a living body in that sea's wildAnimals; an independent validator agrees; its selftest goes red on 3 mutants. No live descent has ever succeeded (the proof harness fails on an unrelated pipe def).
Question: what would a real player (new, experienced, adversarial, messy save) try that these offline checks would miss? Name the 5 most revealing things, each with the cheapest OFFLINE check from source/defs that would catch it, if any.

## The answer (verbatim)

Your census proves **catch-to-body coverage**. It does not establish that players can read the promise, reach those bodies, encounter them alive, or obtain the intended catch. These are the five checks I’d prioritize; they are proposed audits, not findings from your source.

1. **New player: “Read each sea’s description and work out what I’ll find.”**  
   Inspect all four seas in the actual information surfaces players use. Does each distinguish floor animals from shore catch, explain gravship access, and describe `RM_TheChill` consistently as a propane lake?

   **Cheapest offline check:** Produce a four-row report of effective descriptions after XML inheritance, patches, and localization overrides. Review the actual prose against the two tables and access route. A keyword check for “fish” and “floor” would be too weak. This directly tests the literal **“describes BOTH”** obligation.

2. **Experienced player: “Fly down to each sea, then fly home.”**  
   Try every sea, an already visited destination, and multiple surface tiles. The dangerous failures are an inaccessible layer, the wrong floor biome, invalid landing terrain, or an outbound route without a usable return.

   **Cheapest offline check:** Trace the complete route through source and defs: destination eligibility → layer creation → surface-to-floor tile mapping → biome selection → map generator → landing → return eligibility. Check all four mappings explicitly, including layer-qualified tile identity and DLC/load-folder requirements.  
   **Limit:** This can expose broken wiring; it cannot certify a successful descent. The pipe-def failure leaves that integration test **blocked**, not passed.

3. **Patient player: “Stay downstairs long enough to meet the advertised wildlife.”**  
   A species can appear in `wildAnimals` yet never spawn, spawn extremely rarely, or die before discovery. The Scald and propane Chill are especially revealing places to test environmental compatibility.

   **Cheapest offline check:** Audit the actual generation and replenishment consumers: nonempty effective tables, positive weights, finite positive density factors, temperature/season filters, eligible spawn terrain, and initial-generation versus later-spawn paths. Compare environmental settings with each animal’s survival requirements; inspect food availability where relevant. Check GenStep ordering for later overwrites.  
   **Limit:** Defs can reveal impossibility and obvious incompatibility; encounter frequency and sustained survival still need play.

4. **Adversarial player: “Fish at the awkward coast.”**  
   Choose land beside two different custom seas, beside a custom sea and vanilla water, and a coastal map containing a river or pond. Fish each accessible body. Look for the wrong sea’s catch, unintended inland overrides, or “coastal” tiles with no usable fishing shore.

   **Cheapest offline check:** Exercise the **actual sea-selection helper**, where separable, with synthetic neighbor lists: each sea, mixed seas, vanilla-only, no sea, and reversed neighbor order. Require an explicit tie policy and agreement between coast mutator selection and catch selection. Trace water-body classification, terrain generation, and later fish-table writes. Verify patch registration and the exact target overload; Harmony annotations require an application call such as `PatchAll`. [Harmony documentation](https://harmony.pardeike.net/v2/articles/annotations.html)  
   **Limit:** A coastal flag alone cannot prove usable shoreline geometry.

5. **Messy-save player: “Update, reload, revisit, then start another world without restarting.”**  
   Include an old world lacking the layer or mutators, an existing coast map, an existing floor map, and newly generated maps. Alternate visits between all four seas to expose shared state.

   **Cheapest offline check:** Make a lifecycle matrix covering startup, new-world generation, save loading, existing-map loading, and new-map generation. For each, locate the code that establishes the layer, mutator, floor tables, and water-body catch. Audit missing-def handling, cache rebuilding, repeated initialization, and collection ownership. Confirm updates do not compound density or let one sea overwrite another.  
   **Critical distinction:** Reasserting through a GenStep covers maps that execute that step; it does not by itself repair existing maps or serialized water bodies.

## What I tried, and what it showed

**1. A new player reads each sea (its item 1).** This turned up a real gap, and I fixed it.
- I read the four RM_ sea descriptions as the game would show them. None of them mentioned a single floor animal, the catch, the gravship or the shore. A player reading the Scald learned it "boils where it is shallow" and nothing about the eesh or doss beneath it, so the statement's word *describes* was false in the one place a player reads it.
- The fix was one added sentence per sea, written from the measured cast and catch:
  - the floor animals, named by their in-game labels;
  - "reached only by gravship";
  - what a line from the shore brings up.
- To stop it drifting, I added `validation.sea_description_checks()` to `selftest_sea_catch_alive.py`, with 3 mutants that must go red. Each sea must name an animal of its wildAnimals, a fish of its fishTypes, the gravship, and the shore.
- Evidence: `evidence/per_sea_verdict.txt` (the description lines) and `evidence/offline_checks.txt`.

**2. A player with a messy save: update, then reload (its item 5).** This turned up a real defect, and I fixed it.
- An independent offline audit (`evidence/offline_chain_audit.md`, F1) found that `RM_SeabedLayer` mirrors the floor **once**, when a save first builds the layer. A save built before the per-sea floor wiring therefore keeps the empty generic floor under every sea. A surface repainted on an existing save (the planned paint-once) also leaves its floor as it was, which is impassable wherever the tile used to be land.
- Players receive a frozen save and never a fresh world, so this is the ordinary case, not an edge case.
- Fix: `ResyncStaleFloors` re-derives, on every load, each floor tile whose biome disagrees with the surface above it. It skips any tile that carries a world object. It is in commit 42f7c52ebb (published as 6039084c72).
- To stop it drifting, `selftest_seabed_descent_wiring.py` gained check 8 and 3 mutants. The DLL was rebuilt (0 errors, 0 warnings), and check 6 confirms that its .srchash covers the new source.

**3. Items 2, 3 and 4 (fly down and back, stay and meet the wildlife, the awkward coast)** were covered by the same audit's offline trace, with no defect found. In detail:
- The four sea-to-floor mappings resolve.
- Descent and climb are arithmetic tile twins with no hard-coded sea list.
- The floor animalDensity is the sea's value × 30, and every race's comfort range contains its floor's constant temperature.
- The fauna genstep is on all four generators, and there is standable floor ground.
- The Scald's freshwater bands are served on its saltwater shore through the empty-band fallback.
- The Chill's propane shore is Saltwater with providesCatch on.

**Not tried, and only a live game can show it:**
- an actual descent and return;
- how often animals are actually encountered and whether they survive;
- the shoreline geometry on a real coast map.

The descent proof is blocked by a harness fault: `prove_gravship.py` lays a VGE pipe on a game without VGE (PROVEGRAVSHIP_FIX_PIPES_FOR_ABSENT_VGE). That proof belongs to the live lane.
