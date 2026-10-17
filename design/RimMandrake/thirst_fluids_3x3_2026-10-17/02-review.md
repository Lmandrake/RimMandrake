# Thirst and fluids, pass 2: naive review of the pass-1 design (2026-10-17)

Reviews `design/RimMandrake/thirst_fluids_design_2026-10-17.md` ("the design"). My blind solutions, written before
reading it: `design/RimMandrake/thirst_fluids_3x3_2026-10-17/02a-blind-solutions.md` (commit `23669dbfe1`). Paths are
relative to `/home/mandrake/rm/bench` (`D:\Luke\dev\RimMandrake` mirror). Offline review: source read, XML parsed,
nothing run live.

## 1. Starred claims, re-measured by a different method

| # | design's claim and method | my method | result |
|---|---|---|---|
| 1 | `WorkGiver_FillBottle` fills any empty container at any liquid, no target (read the work giver; did *not* read `TryFindFillCell`) | read the callee chain `TryFindFillCell` → `TryFindLiquidCell` → `TryFindLiquidCellUncached` (`Source/LiquidTypes/RM_LiquidBottleUtility.cs:110-117, 255-314`) | **CONFIRMED and sharpened.** The fill call passes `requireFreshWaterOnly: false`; the only filters are "has a bottled form of this size" and the 60-cell radius. The search runs `GenRadial` from the **pawn's** position, so the nearest liquid to the pawn wins, salt or acid alike. `job.count = 1` (`WorkGiver_FillBottle.cs:41`) |
| 2 | no slime bottle/bucket/barrel defs (defName grep) | parsed every `ThingDef` under `src/RimMandrake/**/Defs` and `Patches` and grouped by the `RM_BottledLiquidExtension` `<liquid>` field | **CONFIRMED.** 14 liquids have filled forms, 3 sizes each (Acid, Amber, Boiling, Brine, Chalk, Fresh, Icy, Propane, Rust, Salt, Tar, Toxic, Verdigris, Violet) + 6 empty/dirty defs; no slime |
| 3 | a bottle drink costs 3 jobs with the dirty stage on (from the job list) | read the drivers' outputs | **CONFIRMED.** Fill and wash each produce `stackCount = 1` (`JobDriver_FillBottle.cs:84`, `JobDriver_WashBottle.cs:67`); `bottleDirtyStageEnabled = true` by default (`RimMandrakeFlowWorksMod.cs:327`). Plus hauls, so ≥ 3 |
| 4 | 10 hot colonists ≈ 180 water jobs/day under A, 60-70 under B (3 L/day, ×3 heat) | recomputed from the built constants in `Source/Thirst/RM_ThirstMath.cs:33-39` | **OVERSTATED ~2.4×; the ratio holds.** Built fall is 0.8/day and a full need is 3 L, so **2.4 L/day = 1.6 bottles**, not 2; asleep ×0.5 for ~⅓ day gives ~1.33 drinks/day at 1×. The ×3 is the **cap**, reached only 40 °C above the pawn's `ComfyTemperatureMax` (0.05/°C); a 45 °C desert afternoon is about ×1.9 (vanilla human comfort max not re-read: UNMEASURED). 10 colonists in heat ≈ 25-30 drinks/day ≈ **75-90 jobs under A, 25-30 under B**. A still fails the design's own "≤ 4 water jobs per colonist per day" in heat (≈ 7.5), so the recommendation survives; the alarm is half as loud |
| 8 | "green slime is (or is not) the Gelatinous body" — left to the owner | grepped every mod for references to the slime rows and read the Gelatinous terrain defs | **MEASURED: it is not.** Nothing in `src/RimMandrake/GelatinousSlime` references `RM_Liquid_SlimeGreen`. The Gelatinous body's liquid is its own terrain `RM_Slime_Liquid` (`GelatinousSlime/Defs/TerrainDefs/SlimeTerrain.xml`, tag `RM_SlimeTerrain`, no `Water` tag), which FlowWorks gives only an `RM_LiquidProperties` extension (`Patches/LiquidTypes/RM_LiquidProperties_CompatIndex.xml:149`), **no registry row**. Q-S3's biggest sub-question is answered by measurement; the owner's question becomes "should it be?" |

Unstarred but worth a correction: §1 says the build drinks "Fouled/Toxic when desperate". Only Toxic is gated on
Parched (`RM_ThirstMath.Acceptable`, line 136). Fouled is ranked purely by quality then distance (`Better`, line
142), so **a thirsty pawn (< 0.3) beside the sea with no potable source drinks salt water as routine today.** That is
a second live ruling violation in built code, beside the fill bug, and belongs in the "ship A now" list.

## 2. What the design missed (found by this pass)

1. **The slime biome's own slime is outside the system.** `RM_Slime_Liquid` (Gelatinous) and `AB_LiquidSlime` (Alpha
   Biomes, listed in `RM_LiquidProperties_CompatIndex.xml:24`) have no `LiquidDef` row, so `LiquidAt` returns null and
   no `drinkClass` can reach them. The Gelatinous biome is the place a colonist is most likely to face "slime and no
   water", and the last-resort rule would never fire there. Fix: put `drinkClass` (and `ingestEffects`) on
   `RM_LiquidProperties` as well, so a terrain-only liquid is classified by the same data, and route a Gelatinous
   slime drink through `IngestionOutcomeDoer_SlimeDose` (soft reference) as its per-kind effect.
2. **Other mods' water items are invisible to "is potable water available".** `RM_DistilledWater`
   (`TerminalBiomes/Defs/ThingDefs_Items/RM_DistilledWater.xml`) and `RM_StilledWater`
   (`Stillsand/Defs/ThingDefs_Items/RM_StilledWater.xml`) are not referenced anywhere in `FlowWorks/Source/Thirst`.
   Under §3.3 a pawn could drink slime with distilled water in the stockpile. Fix: the potable test reads a marker
   extension, not a defName family; those two items get it.
3. **Salt-only colonies need a named potable route.** With salt now break-only, a coast camp lives on stills. They
   exist: `RM_SunPanStill`, `RM_DripFilter`, `RM_FueledStill` (`FlowWorks/Defs/Machinery/RM_LiquidStills.xml`) and
   `RM_SolarStill` (Stillsand). But ruling 1 forbids auto-gathering the brine a still eats. The design should say
   **a still's bill is the order** (a bill on a still that consumes brine authorises fetching brine for it), or the
   coast colony starts with a dead machine. This generalises Q-G1 from "machine burns fuel" to "machine consumes
   any non-potable input".
4. **Partial draws from buckets and barrels need a contents state that does not exist.** `RM_BottledLiquidExtension`
   holds `liquid`, `dirty`, `size` only; containers are full or empty, and filled buckets stack to 10, barrels to 4
   (`RM_LiquidBottles_Base.xml:189, 288`). "Takes 1.5 L from the vessel" needs a saved litres comp, a split before
   the draw, and a no-merge rule for part-filled vessels. Not hard, but it is the main new code in ruling 2 and §3.2
   does not name it.
5. **Tier order is inverted against the ruling's wording.** §3.2 lists tap (B) before potable terrain (C). The ruling
   debuffs a tap only when the pawn "has no bottles"; a pond is not a tap. So the debuff-free sources (bottle, pond)
   should be compared by distance first, and the tap taken only when neither is in reach. Otherwise a river colony
   with no bottles drinks from a tank with a debuff instead of from the river 10 cells away.
6. **Salt break re-entry.** The need "truly fills", then drains ×3, so a pawn can re-enter the break within hours.
   The break should be ineligible while `RM_SaltPoisoning` is above 0, or the second visit should be rarer.
   Also eligibility asks only that salt is reachable; I would add "no potable source reachable" for the thirst
   route (a madness break with a full bottle in the stockpile reads as a bug, not as madness).
7. **Crops dwarf drinking.** Ruled sprinkler use is 0.5 L/cell-hour, ~350 L/day per native head
   (`sprinklers_design_2026-10-16.md` §1.4); 10 colonists drink ~25-45 L/day by the corrected arithmetic. **One
   sprinkler head drinks what 8-14 colonists drink.** The design's traffic section treats crops and drinking as
   neighbours; they are not. A per-net **drinking reserve** (the sprinkler design's VFE "reserve floor", made
   universal for every consumer that is not a drinker) is needed before sprinklers ship, not after.

## 3. Comparison with my blind solutions

| my blind | nearest in the design | difference |
|---|---|---|
| shared core: `drinkClass` Routine/LastResort/BreakOnly/Never | §3.1, identical in substance | convergent; good sign the model is forced by the rulings |
| A ladder + `CompLiquidLitres` + potable census | its A + §3.3 | I named the litres comp and the census; it named the stock target and batch wash |
| B plumbing: pipe tap + **drinking reserve** | its B (stations, cup rack) | it has no reserve; I had no cup rack. The reserve is the stronger idea (§2.7) |
| C use-policy filters on containers | partly its C (one vessel, one job) | its C is by vessel size, mine by stockpile filter. Its rule is simpler to learn; mine handles "this barrel is the farm's". Neither is needed first |

Both passes missed the same thing at first: **the job count is caused by `count = 1` on fill and wash, not by
bottles.** That changes the solution ranking (§4, §5).

## 4. Critique and improvement of each solution

**A — bottles first, demand-capped.** Right first step; it is the only one that fixes built violations. Improve:
- *Batch the fill*, not only the wash. A pawn carries a stack of empties to a tank or shore and fills up to N
  (PROPOSED 10) in one job, the way vanilla hauls a stack. With fill and wash both batched at 10, a bottle drink costs
  ~1.2 jobs, close to B, with no reading of the ruling changed.
- Fill target counts bottles in pawn inventories (packed bottles exist, `JobGiver_RM_PackBottles`), or packing
  causes refills.
- Search origin: fill from the nearest **potable** source to the *container*, tank first, then terrain; today's
  radial-from-pawn search must change with the filter anyway.

**B — drinking stations with a cup rack.** The job saving is real, but "cups count as bottles" rewrites the owner's
words: he said a small debuff when pawns *"have no bottles to drink from and must drink from a tap"*. A cup rack is
a bottle by another name, which is either the same thing as bottles (then it is A) or a dodge (then it needs a card
and is likely to be refused). Improve: keep stations but make them **bottle points** (see D) so the ruling is met
literally; drop the cup reinterpretation.

**C — network-first vessel tiers.** The most coherent long-term shape, and its "port first, then refuel job, never
bottles" rule for machines is right. Improve: add the drinking reserve (§2.7) as a C-level rule, since C is where
pipes feed everything; and state that a still's or machine's bill is the order for its non-potable input (§2.3).
"Barrel: never drinking (except the ruled fallback)" is consistent with ruling 2.

## 5. A fourth solution that beats B: D — the bottler

A **bottler**: a small FlowWorks machine on the liquid net (pump pressure, like the sprinkler head) with a shelf.
It fills empty bottles from the net to a stock target and washes dirty ones (the residue doer drops dirty bottles
where the pawn drank; a stockpile beside the bottler pulls them back in ordinary hauling). Pawns drink **bottles**:
no debuff, ruling read literally. Pawn jobs per drink: 1 ingest + a share of one haul (dirties are hauled in stacks).

- **Beats B** on fidelity (no "cups are bottles") at about B's job load; **beats A** in a piped base; falls back to
  A (batched) before pipes exist, so A's work is not wasted.
- Fits what is built: `CompLiquidConverter` already consumes from the net through `DrawPlan`/`Move`; the bottler is a
  converter whose output is filled-bottle items. The machine draws only potable liquid (`drinkClass == Potable`), so
  ruling 1 holds without a new check.
- Cost: one building, art in the four looks, a converter-to-item output path (UNMEASURED whether
  `CompLiquidConverter` can emit items today).
- The drinking reserve (§2.7) protects it: sprinklers and machines stop above the reserve, the bottler does not.

## 6. The recommendation

**Agree** with "A now": the fill bug and routine salt drinking are live violations, and the `drinkClass` field is the
right single lever. **Disagree** with "B next": its saving comes from the cup reinterpretation, which the ruling
does not support. Proposed sequence:

1. **A + batched fill/wash + corrected tier order** (fixes both violations; brings A near 1.2 jobs/drink).
2. `drinkClass` on `RM_LiquidProperties` too (Gelatinous/Alpha slime), a potable marker for the
   distilled/stilled water items, "a still's bill is the order".
3. **Per-net drinking reserve** before sprinklers ship.
4. **D, the bottler**, as the first logistics building.
5. C's machine ports when the first liquid-burning machine needs one.

What would change it: if the owner answers Q-V1 "yes, cups count", B and D cost about the same and B needs no
item output path; then B.

## 7. Questions to add to the design's §11

- **Q-R2** Is a still's or machine's bill an "order" that lets pawns fetch brine (or slime) for it?
- **Q-R3** Does drinking water take priority over sprinklers and machines on a shared net (a reserve)?
- **Q-S5** Should the Gelatinous biome's own liquid slime be drinkable as a last resort (with the slime-dose effect)?
