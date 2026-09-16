# FIREHAWK_FLIGHT_BEHAVIOR_1 — donor-style wing flap

Owner: FireHawk (and flying fauna generally) should "actually flap around
like the other native creatures do from our donor mods." BLOCKED-ON-ART —
left unwired this pass, honestly, rather than wiring something broken.
Mechanism identified and verified; see below for exactly what is missing.

## donor mechanism found, and verified against the actual DLL/XML

Active flying-fauna mods in the current `ModsConfig.xml`: `sarg.alphaanimals`
(Alpha Animals) — its `PawnRenderTreeDefs` folder was swept for any winged
creature. `AA_SmallButterfly`
(`.../workshop/content/294100/1541721856/1.6/Defs/PawnRenderTreeDefs/PawnRenderTreeDefs_SmallButterfly.xml`)
is the one that visibly flaps: four wing pieces, each its own
`<li Class="PawnRenderNodeProperties_Spastic">` node with a
`texPath`/`linkedBodyPartsGroup`/small `offsetRangeX`/`offsetRangeZ` jiggle.

**`PawnRenderNodeProperties_Spastic` is a plain VANILLA RimWorld class**
(RimSage, `Verse/PawnRenderNodeProperties_Spastic.cs`) — confirmed by reading
it directly: `nodeClass = PawnRenderNode_Spastic`,
`workerClass = PawnRenderNodeWorker_Spastic`, fields `offsetRangeX/Z`,
`rotationRange`, `scaleRange`, `durationTicksRange`, `nextSpasmTicksRange`.
Anomaly's own `Bulbfreak` tentacle-sway (already ported into this repo as
`RSW_Beldon`'s render tree, `src/RimStarWars/SWBestiary/Defs/PawnRenderTreeDefs/RSW_MlieWaveC_RenderTree.xml`)
derives from the same base class. So the actual flap mechanism costs **zero
new C#** — it is XML-only, riding an engine class that already ships. Alpha
Animals' own DLL (`AlphaBehavioursAndEvents.dll`, strings-checked directly)
adds only `PawnRenderNodeProperties_Spastic`/`_SpasticScaled` on top of the
vanilla base and an unrelated `PawnFlyer`/ability-jump helper — nothing
FireHawk would need beyond the vanilla class itself.

## why it is NOT wired this pass

Wiring `Spastic` onto a wing means each wing is its own **separately layered,
independently-offsettable texture**, attached via a `linkedBodyPartsGroup` to
a body part that exists purely to anchor that render node. Confirmed by
reading the donor's own supporting defs, not assumed:

- `AA_SmallButterflyA` (linkedBodyPartsGroup) is a bare `BodyPartGroupDef`
  with no health meaning (`Defs/Bodies/BodyPartGroups_AlphaPredators.xml`) —
  and the butterfly's `BodyDef` (`Defs/Bodies/Bodies_Butterflies.xml`) is a
  **wholly custom body** with duplicate near-zero-relevance parts, one per
  wing piece, each tagged into its own group. This is not a comp you drop
  onto an existing body — it is a body redesign plus new render tree.
- **FireHawk's `<race><body>` is vanilla `Bird`** (RimSage,
  `RimWorld/BodyDefOf`/`get_def_details Bird`) — confirmed Bird's `corePart`
  has no wing part and no wing-capable `BodyPartGroupDef` at all (Tail,
  Spine, internal organs, Neck/Head/Beak, two Legs/Feet — nothing else).
  There is no existing anchor to hang a wing render node on.
- **FireHawk's current art is a single flattened sprite per direction**
  (`src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_{north,east,south}.png`)
  — body and wings baked into one image, `Graphic_Multi`, no render tree at
  all today. The donor mechanism needs the wing **as its own transparent PNG
  layer**, separate from the body, one per wing piece the render tree
  addresses independently (the butterfly ships 4: `...One/Two/Four/Five`).
  We have no such layer for FireHawk and extracting one from the flattened
  sprite is image editing/generation — explicitly out of scope for this pass
  per the brief ("do NOT generate art... leave firehawk unwired rather than
  wiring something broken").

**What wiring this for real requires, so it can be picked up cleanly:**
1. A custom `BodyDef` for FireHawk (or a wing-bearing variant of `Bird`) with
   1-2 new near-zero-coverage parts, each tagged into a new, purely-cosmetic
   `BodyPartGroupDef` (`RUT_FireHawkWingLeft`/`Right` or similar) — coverage
   low enough not to skew combat/downing odds versus the existing Bird stats
   already tuned for FireHawk's tools.
2. A `PawnRenderTreeDef` (new file, alongside `RSW_MlieWaveC_RenderTree.xml`
   as precedent) with one `PawnRenderNodeProperties_Spastic` child per wing,
   `linkedBodyPartsGroup` pointing at the groups from (1), small
   `offsetRangeX/Z` (butterfly ships ±0.15) or `rotationRange` for a
   sweep-style flap, referenced from FireHawk's `<race><renderTree>`.
3. **New art**: one transparent-background wing PNG per wing piece per
   direction needed (at minimum a single symmetric wing pair, matching
   FireHawk's existing 3-direction N/E/S set), sized and pivoted to overlay
   correctly on the existing flattened body art OR a full re-split of
   FireHawk's body art into separate body-only + wing-only layers so the
   flattened look does not double up wings. Either route is art generation,
   which this pass was told not to do.

## sweep — other flying Pyrelands/Ashkarr roster kinds (list only, not wired)

Checked `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PyrelandsFauna.xml`
(the only Pyrelands custom-fauna file) and Ash'karr's biome `wildAnimals`
lists (`RUT_Desert.xml`, `RUT_AridShrubland.xml`, `RUT_CrackedLands.xml`,
`RUT_ForsakenCrags.xml`, `RUT_ExtremeDesert.xml`, `RUT_GreySea.xml`,
`RUT_BlueDesert.xml`, `RUT_Greentide.xml`, `RUT_FeverWood.xml`,
`RUT_Contagion.xml`):

- **`RUT_FireHawk`** — the only wholly-authored (`<body>Bird</body>`, custom
  art) flying creature in the Pyrelands roster. `RUT_FurnaceBeast` in the
  same file is a quadruped, not a flier.
- Ash'karr's biome `wildAnimals` lists reference vanilla/other-mod bird
  species by defName (their own donor art, not ours to rewire here) — no
  wholly-owned RUT_/RM_ flying creature turned up in those lists. This is a
  defName-list sweep, not a full census of every donor bird those lists
  admit; a thorough donor-bird flap audit (which of THEM already flap, via
  what mechanism) is its own item if wanted.

## not done

- FireHawk left with its current static 3-direction sprite and no
  `renderTree` — behaviorally unchanged this pass.
- No C# was written for this task (none was needed for the mechanism itself
  — confirmed vanilla-class-only — but the body/render-tree/art plumbing
  above was not built either, since it terminates on missing art).
