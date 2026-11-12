# BROADEN — BIOME_SHIP_CONTRIBUTIONS_1

Asked 2026-11-11 21:42 PST, GPT (gpt-6.1-sol) via `src/RimMandrake/Utils/gpt_consult.py --codex wsl`; receipt job consult-20261111-214236-116290-bbfbed.

## The question (verbatim)

> Statement to make true (RimWorld 1.6 + Odyssey mod project): "Every shipped biome mod has at least one ship-buildable contribution or an owner-ruled exemption; the list matches what the mods actually ship." The owner's ask: "how can this biome uniquely add something to the ship? ... What can they take and improve their ship's environment with?" Players fly a gravship (Odyssey); things on substructure travel with it.
> 
> What I built and tested (offline only; no game run in this lane):
> - A checker (ship_contributions.py) that reads the 24 composed biome mods, resolves def inheritance against the game's Data defs, and judges "ship-buildable" the engine's way: on a substructure cell the foundation's affordances (Light/Medium/Heavy/Walkable/Substructure, read from Odyssey defs) decide; player-buildable = designationCategory, or minifiable + something in src hands it to the player (install-only); placeWorkers classified by reading their C# (vent/geyser/pool/tile-mutator/biome-floor-only = site-bound, unknown = fail); plants excluded (fertility 0 on a deck); bringAlongOnGravship=false excluded. It checks the item's running-list table: one row per biome, every named def exists and passes, at least one named def is the biome's own (defined in that mod or costing its material).
> - A selftest that mutates the real list 10 ways (bridge-affordance def, vent-bound def, geyser-bound def, a plant, a nonexistent def, a def from another biome, grow-soil floor, missing row, EXEMPT without ruling, two table rows joined on one line) and requires each to fail with its reason.
> - 4 biomes had nothing; I added XML-only gifts with vanilla comps: a furnace-hide heat bank (CompHeatPusher, unpowered), a fossil display case (beauty), a self-healing gravship hull wall (CompSelfhealHitpoints, Substructure affordance, tickerType Rare), a hex shell floor (FloorBase). Art is being generated.
> 
> Question: what would a real player (new, experienced, adversarial, or a messy real save) try with these ship contributions that this offline testing would NOT catch? Name the 5 most revealing concrete checks I could still do OFFLINE (reading defs/C#/decompiled engine source), most revealing first. Be terse.

## The answer (verbatim)

> 1. **“Build it from a normal survival start.”** Trace acquisition → research → recipe/trader/quest → ingredients → construction or installation. Check quantities, workbench access and DLC gates. A valid def can still be unobtainable; inspect each claimed install-only handoff’s actual conditions.
> 
> 2. **“Put it on my existing deck.”** Trace blueprint, frame, completion and reinstall validation—not just affordances. For the hex floor, inspect terrain-layer replacement and removal: does laying or stripping it preserve substructure, support and ship membership?
> 
> 3. **“Launch, land, then move it again.”** Follow gravship collection, transfer and landing code for buildings, terrain and minified cargo. Check retained hit points, comps, rotation and terrain layers; confirm each gift survives repeated transfers without disappearing or duplicating.
> 
> 4. **“Does it actually improve my ship—and can I abuse it?”** Read the four gifts’ runtime paths: heat-bank temperature/roof limits and stacking; display beauty visibility; hull healing ticks, damage eligibility and repair cost. Trace comp dispatch and required fields, not merely comp presence.
> 
> 5. **“Load my old, heavily modded save.”** Audit final patch order and save/load initialization: existing biome maps, already-generated acquisition sites, missing research unlocks, changed defs and comp state. Check whether existing players can obtain the gifts without generating a fresh world.

## What I tried, and what I found

1. **"Build it from a normal survival start" (answer 1): can a player actually get each gift?** I added an
   `obtainable` check to `src/RimMandrake/Utils/ship_contributions.py`: every research prerequisite of a claimed def
   must be a real ResearchProjectDef, every RM_/RUT_/RSW_ material in its costList must be handed out by something
   (a mention outside every costList and outside About.xml prose: mineableThing, butcherProducts, leatherDef, recipe,
   trader stock, C# spawn) or be crafted by its own recipeMaker, and every install-only gift must likewise have a
   source. **Found a real defect:** `RM_CloudRepulsorShip`, the Contagion's ship hardpoint (the only ship-specific
   Contagion device), was defined but **nothing in the game ever handed it to a player**: no trader stocked it, no
   quest paid with it, no reward tag (only the ground `RM_CloudRepulsor` was wired). Fixed: the Helix curators'
   caravan (`src/RimMandrake/Contagion/Defs/TraderKindDefs/RM_HelixCurators.xml`) now stocks it 0~1, same odds as the
   ground device. The first cut of the heuristic also raised a false alarm on `RM_ToxinSealant` (Greentide's sealed
   floor): it is crafted by its own `recipeMaker`, which the check now counts; both cases are regression checks in
   `src/RimMandrake/Utils/selftest_ship_contributions.py`.
2. **"Does it actually improve my ship" (answer 4): do the vanilla comps the new gifts rely on really run?** Read the
   decompiled 1.6 source. `CompHeatPusher` pushes heat whenever spawned and below `heatPushMaxTemperature`, with no
   power/fuel comp required; its `CompTickRare` pushes 4.17x per call, so I moved the heat bank from the Normal to
   the cheaper Rare ticker at the same heat rate. `CompSelfhealHitpoints` heals in `CompTickRare`, which a `Wall`
   child never gets (Wall sets `tickerType Never`): the pattern hull overrides `tickerType Rare`, so it heals 1 HP per
   500 ticks (120 HP/day). And `Gravship.cs` leaves behind any def with `bringAlongOnGravship false`: now a checker
   rule (none of the 24 rows trips it).
   **Second real defect found on the way:** `Wall` links as `CornerFiller`, so every Wall child draws its texture as
   a link ATLAS. The Forge's `RM_SpunstoneHull` (a claimed ship gift) ships a single 128 px block picture, which the
   game slices into fragments. A proper atlas was commissioned with the pattern hull's; lesson filed
   (`infrastructure/state/lessons/20261112T054215Z-CLAUDE_STEVEDESKTOP_OFFLINE2-wall-parent-needs-link-atlas.md`).

Not tried (offline lane, no game): answer 3 (launch/land/move again with the gifts aboard) and answer 5 (old save
loads). Both are engine behaviour for ordinary buildings and floors on substructure; no gift adds custom gravship
transfer code. The live lane can confirm with one launch.
