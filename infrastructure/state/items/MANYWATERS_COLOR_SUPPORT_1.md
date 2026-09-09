## spec (design proposal, Fable subagent, 2026-09-09 — awaiting owner ruling)

**Reading the brief.** ManyWaters' own About.xml says it "gathers all water
effects/*types*", so the coherent reading is: **ManyWaters becomes the
RimMandrake-tier roster of coloured liquid TerrainDefs (water and slime),
FluidCanals consumes them** (`FluidDef.floodTerrain` is already just "which
TerrainDef"), and Utinni patches decide which biome/canal gets which colour.
Slime is not a conflation: FluidCanals' About names slime as a fluid it will
carry, and the only slime water in the stack today is Alpha Biomes'
`AB_LiquidSlime` (third-party, `WaterShallowBase` + its own `AB_SlimeRamp`
texture + `Map/WaterDepth`) — i.e. slime already IS "water with a different
texture". Colour lives entirely in the terrain; neither engine has a colour
field anywhere today.

**1. Many colours of water — mechanism.** Recommend **(a): N pre-authored
TerrainDef variants sharing one texture, differing only in `<color>`.** That
is vanilla's own colour convention (`Terrain_Floors_StoneTile.xml`: one
texture, six `<color>` defs) and this repo's own (`AshLadder.xml` four rungs
on one texture, `ScorchableGround.xml`, `JawaSaltCrust.xml`). `TerrainDef
.DrawColor` is passed straight into `GraphicDatabase.Get<Graphic_Terrain>
(texturePath, Shader, …, DrawColor)` for every edgeType including
`TerrainWater` (`Verse/TerrainDef.cs:433`). No runtime tint exists —
`TerrainGrid` stores a def per cell, nothing per-cell for colour — so a
runtime-tintable-material approach (b) means a Harmony draw patch plus a
per-colour material and buys nothing the owner can see that (a) doesn't.
Cost per colour: one ~10-line def (ParentName `WaterShallowBase`, clone
`WaterShallow`, add `<color>`), zero art.

⚠️ One gate before authoring twelve: **no vanilla water def uses `<color>`**,
and water draws twice — the base `TerrainWater` material (tinted) plus the
`Map/WaterDepth` overlay material, which is created with no colour at all
(`TerrainDef.cs:448`). Whether the tint reads through the depth overlay is
UNVERIFIED. Test ONE coloured def on a quicktest first. Fallback if it
washes out: a recoloured copy of `WaterShallowRamp.png` per colour (still
XML-only, no shader work) — exactly Alpha Biomes' own route.

**2. Many colours of slime — whose feature.** Split, along the line already
drawn today:
- **FluidCanals owns identity**: one `FluidDef` per (fluid, colour) → one
  **temporary** slime TerrainDef (`FluidDef.ConfigErrors` refuses
  non-temporary; `ShallowFloodwater` is the model). `ticksPerTile` makes it
  viscous; nothing else changes.
- **ManyWaters owns the terrain roster and the ambient effect.** Two
  findings make the effect cheaper than expected: (i) the Steam fleck uses
  the `Mote` shader and `FleckCreationData.instanceColor` tints it at spawn
  (`FleckStatic.cs:86,145`), so the existing hook gains a `fleckColor` field
  on the extension with no new art; (ii) vanilla 1.6 already has
  **`TerrainDef.throwFleckChance` + `fleckData`** consumed by
  `SteadyEnvironmentEffects.cs:171` — per-terrain ambient flecks in pure
  XML. So coloured slime bubbles need a tinted `Steam` FleckDef clone
  (`graphicData.color`) and a `fleckData` block on the slime def: **zero
  C#**. ManyWaters' C# extension would move from biome-scope to
  terrain-scope only if the owner wants river-style timing control per
  fluid; not needed for v1.
- Slime standing pools vs canal slime are **two defs per colour**
  (non-temporary + temporary), because the flood layer demands
  `temporary=true` and a permanent pool must not.

**3. v1 slice — one sitting, one look.** A quicktest map, saved per the
"options he must LOOK at ship as a savegame" rule with a grid key:
- Row A: `WaterShallow` untinted control + 5 tinted `RM_Water_<Colour>` defs
  (colour on `WaterShallowRamp`).
- Row B: `AB_LiquidSlime` control + 5 tinted `RM_Slime_<Colour>` defs
  (colour on `AB_SlimeRamp`, texture referenced by path; AB must be active),
  each with `fleckData` pointing at a matching `RM_Fleck_Steam_<Colour>`.
- Palette entry per colour: name, RGB, base ramp, intended fluid, one-line
  lore hook — a `Palettes/*.md` OPTIONS list per this repo's material-palette
  convention, not a ruling.

Author count: **12 TerrainDefs + 5 FleckDefs**, all XML, all in ManyWaters.
No FluidDefs yet — the temporary siblings and canal wiring follow once the
owner picks colours. Painted via `jawa/set_terrain`, 4×4 patches, ~6-cell
pitch, night lighting available for `glowColor` if wanted.

## verify
Owner looks at the saved v1 quicktest (grid key names which cell is which
colour/fluid) and picks: which water colours stay, which slime colours
stay, whether the fleck-tint effect reads right, and whether the
runtime-tint gate (water colour surviving the WaterDepth overlay) needs the
texture-recolour fallback instead.

## criteria
Not yet ruled — this item stays a design proposal until the owner reviews
the v1 slice and rules on colour count/palette. Do not author the full
roster past the single quicktest-gate check without that ruling.

## Open questions the design could not resolve
- Whether `<color>` survives the `WaterDepth` overlay material (gates
  whether (a) needs the texture-recolour fallback) — UNVERIFIED, needs a
  live quicktest check, one tinted def is enough to answer it.
- Whether `jawa/set_terrain` can lay a `temporary` def for a look-test (it
  calls `SetTerrain`, not `SetTempTerrain`, per FluidCanals' own notes) — v1
  sidesteps by testing standing (non-temporary) variants only.
- `AB_LiquidSlime` ships from Alpha Biomes' `1.5/` folder only; not
  confirmed it loads under 1.6.
- Whether Dubs Bad Hygiene treats a tinted clone as drinkable depends on
  tags copied, not colour — copy the parent's tags verbatim and it is
  unchanged.
- `SteadyEnvironmentEffects.throwFleckChance` was only read as firing on
  outdoor unroofed cells (line 171) — worth confirming for roofed canal
  cells if that matters to the design.
