# BROADEN: FASCINATING_WORLD_JUNK_1

Asked 2026-11-11 22:20 -0800, GPT (gpt-6.1-sol via src/RimMandrake/Utils/gpt_consult.py --codex wsl), a different model from the builder (Claude Opus 5.5).

## The question, verbatim

> You are reviewing testing for a RimWorld 1.6 mod change. Statement to make true (owner's words): reskin and re-text every map-scatter wreck (tanks, trucks, cars, ancient junk) into Star Wars scavenger wreckage; census what exists and what spawns it; rule the roster per region; re-graphic and re-text. Verify section: a real arrival map at Zeddo's Yard (the player's start, on a Fall Line tile) screenshotted with ZERO tanks/trucks/cars visible, every wreck on it resolving to a def in junk_roster.json (measured over the whole map); one Fall Line map whose wrecks read fresh, not old; full load with zero new config errors.
> 
> What was built:
> 1. 24 vanilla vehicle/war-machine junk defs (AncientRustedCar, AncientTank, AncientRustedTruck, warwalker parts, dropships, ...) reskinned with Graphic_Random Star Wars wreck art and new labels/descriptions (an earlier item); this round removed the last "tank"/"truck" words from labels/descriptions.
> 2. junk_roster.json: 8 kept kinds (speeder hulks, military hulks, walker remains, starship wreckage, droid/drive scrap, ship chunks, cargo, yard structure) with was/yields/risks, and a cut list of 21 defs (shopping cart, ATM, kitchen appliances, toilet, bed, operating table, industrial truck, chemtruck, wind turbine, tailor benches, plant pot) + 3 prefabs (ancient road short/long, container forklift).
> 3. A generated XML patch removes the cut defs from GenStep_ScatterGroup tables AncientJunkClusters / ScarlandsJunkClusters and the prefabs from ScarlandsJunkPrefabs, gated by a Mod Setting (default on).
> 4. The RUT_FallLine tile mutator gets junkDensityFactor 0 at runtime (setting noOldJunk, default on): every vanilla isJunk scatterer, road debris, ancient fences, ancient mechs multiply their count by it, so no old junk on Fall Line tiles.
> 5. Offline tests: a selftest checks roster well-formedness, patch == generator, every cut xpath hits its GenStep, no group emptied, no car/truck/tank in kept labels, a static census (parses vanilla GenSteps incl. hard-coded C# lists + our Zeddo's Yard template) diffed against the roster, DLL/source hash. No live game was available (offline lane); live map counts are not yet measured.
> 
> Question: what would a real player (new, experienced, someone trying to break it, a messy real save) actually see or try that these tests miss? Name the 5 most likely ways the statement is still false in real play, most likely first, each with the one cheap check (offline preferred) that would reveal it.

## The answer, verbatim

> Based on the implementation described, I’d rank these five risks highest:
> 
> 1. **Fall Line becomes empty instead of looking freshly wrecked.**  
>    Multiplying old-junk generation by zero establishes absence; it doesn’t establish fresh wreckage. A player could arrive at a convincing yard template while every ordinary Fall Line map is barren.  
>    **Cheap check:** Trace one ordinary Fall Line generation path and calculate which wreck placements remain after the density multiplier. Require a positive source of fresh wrecks, with appropriate art and text. No surviving source means this fails offline.
> 
> 2. **The roster isn’t actually ruled per region.**  
>    A global cut list plus one region-wide suppression switch doesn’t demonstrate regional rosters. The current census might correctly enumerate everything while allowing the wrong kept wrecks in a region—or overlooking additions from the player’s actual mod stack.  
>    **Cheap check:** Extend the census into a **def × region × spawning-source matrix**, compared against explicit regional allowlists. Include the actual Zeddo’s Yard placement path and fallback paths. A roster of broad kinds alone cannot prove every spawned def belongs.
> 
> 3. **Players still recognize tanks, trucks, cars—or ancient wreckage—in the replacement graphics.**  
>    Removing words from labels proves little about silhouettes, weathering, or every `Graphic_Random` variant. One overlooked variant can spoil the arrival screenshot; uniformly ancient-looking replacement art can also fail “fresh.”  
>    **Cheap check:** Produce a contact sheet of **every texture variant referenced by the replacement graphics**, displayed at normal map viewing size, with its def and texture path underneath. Review recognizable vehicle shapes and apparent age. Sampling one image per def is insufficient.
> 
> 4. **An existing save retains forbidden wrecks that generation patches never touch.**  
>    An experienced player can load an already-generated Fall Line map containing cut objects. Reskinning retained defs can update their appearance, but removing entries from scatter tables does not remove existing instances. Persisted settings can also differ from today’s defaults.  
>    **Cheap check:** Audit one established save’s serialized map objects against the roster and regional rules, alongside its saved settings. Include an already-generated Fall Line map. This reveals whether the promise needs migration behavior or an explicit new-map scope.
> 
> 5. **The installed mod fails during real loading or first graphic use.**  
>    Source hashes and successful XPath matching don’t establish that the assembled mod loads cleanly. Missing packaged textures, invalid graphic configuration, setting initialization, or patch interactions can still produce errors or visibly broken wrecks.  
>    **Cheap check:** One dev-mode launch through the **actual Zeddo’s Yard arrival**, comparing its log against the same setup without this change. This check needs the game; offline validation cannot establish “zero new config errors.”
> 
> The decisive arrival check should export a whole-map inventory of wreck **instances and exact defNames**, including authored placements, then compare it with the roster. A clean screenshot and a census of possible spawns do not establish that result.

## What I tried, and what it found

**1. The region rules were thinner than they looked (GPT's #2). I checked them, found a real hole and fixed it.**
The Fall Line lever I had built was `junkDensityFactor = 0` on `RUT_FallLine`. I read which vanilla steps actually
multiply by that factor (`GenStep_Scatterer.GetPlacementFactor` only when `isJunk`; `GenStep_ScatterRoadDebris`,
`GenStep_ScatterAncientFences` and `GenStep_ScatterAncientMechs` by their own override). The base game's step defs
show seven steps that ignore it entirely: ScatterRuinsSimple, ScatterCaveDebris, AncientUtilityBuilding,
MechanoidRemains, AncientTurret, AncientLandingPad and AncientPipelineSection. So a Fall Line map would still have had
old ruins, turrets and landing pads, which breaks "Nothing here is old".
Fix: `RUT_FallLine_NoOldJunk`, a no-op GenStepDef whose `preventsGenSteps` names all 14 vanilla junk steps. It is
added at runtime to `RUT_FallLine.extraGenSteps` by the same setting. I read `MapGenerator`: mutator `extraGenSteps`
are joined in before the `preventsGenSteps` filter, so this works.
`selftest_junk_roster.py` now checks per region:
- every Zeddo's Yard template def (17) sits in a kind ruled for `zeddos_yard`;
- the prevent list covers every vanilla source the census reads (14 of 14).

**2. A messy real case: a map that already exists (GPT's #4).** The repo copy of the dev start save
(`world/ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws`) holds one generated map. I counted every thing on it
(`evidence/dev_start_save_existing_map_inventory.txt`) and diffed its junk against the roster
(`evidence/dev_start_save_map_vs_roster.txt`). Old maps are not migrated, so this pre-change map still shows 58
instances the roster no longer places:
- 29 industrial trucks;
- 16 chem trucks;
- 4 lampposts;
- 3 cardboard boxes;
- 3 plant pots;
- 2 forklifts;
- 1 electric stove.

It also confirms the cut list on real data: every one of those defs is on the cut list or arrives only inside a cut
prefab, and nothing on that map falls outside both the kept and cut lists. The consequence is that the promise holds
for maps generated after this change. An already-generated map, including whichever arrival map the shipped save will
carry, has to be generated fresh. The world is painted and frozen once, at the end (BIOME_PAINT_ONCE_AT_THE_END_1),
so that is the live step.

**3. GPT's #1 (Fall Line empty rather than fresh):** this is by design, not a defect. The frozen Fall Line sheet and
SALVAGE_WRECKAGE_EVERYWHERE_1 deliver its wreckage by falling (`RUT_FallLineWreckFall`, `RUT_WreckList_FallLine`),
"never a field". The map starts clean of OLD junk, and fresh wrecks arrive over time. A screenshot of a brand-new Fall
Line map will show few wrecks, all fresh.

**4. GPT's #3 (every variant at play size):** `evidence/roster_contact_sheet.png` shows every installed RSW_Junk
variant (179 PNGs across the 24 reskinned defs) with the label the player reads. These variants were judged per
picture on STARWARS_JUNK_RESKIN_1. I looked at the sheet: no picture reads as an earth car, truck or tank.

**5. GPT's #5 (real load):** this needs the game, which my lane does not have. It is the live step, together with the
Zeddo's Yard arrival map inventory.

## After the first judge (would show: no) and a fresh code review

The code reviewer (a fresh Opus that did not build it) and the judge raised these; what changed:
- **Two more old-relic steps on player maps were not prevented** (`ScatterShrines` and `AncientExostriderRemains`,
  both in `Base_Player`). Both are now in `RUT_FallLine_NoOldJunk`. Also, the selftest's "prevents every source" check
  had been circular: it compared against the census's own hand list. It now derives the old-junk steps independently,
  from the base game's own `MapCommonBase` and `Base_Player` generator lists (14 found; all prevented).
- **The "no group left empty" check could never fail** (it ran after the sweep). It now measures before the sweep.
- **A null guard on `RUT_FallLine.extraGenSteps`.**
- **Re-text was incomplete:** about 45 kept defs that keep their vanilla picture still read vanilla. Each now gets a
  scavenger label and description (generated `Patches/AncientJunk_RosterText.xml`, junkReskin gate). Fourteen are
  exempt, each with a stated reason in the roster: ship chunks, slag chunks, and the player-buildable ruin walls,
  doors and tables.
- **The roster lacked the biome extras and the Fall Line's fresh kind.** Added: `fresh_fall` (the Fall Line's own
  wrecks), `biome_wrecks` (31 wreck children of the Wreckage layer across the biome mods), `rakatan_relic` and
  `injection_wrecks`. Five biome wrecks and the Fall Line fuel wreck were labelled "... tank"; they are now
  "... cylinder", and the selftest's noun check reads our own defs' labels too.
- **Per-region switches:** each region in the roster now names its switch. Zeddo's Yard has none on purpose: its junk
  is the start site itself.
