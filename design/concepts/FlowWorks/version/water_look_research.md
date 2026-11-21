# FlowWorks water look: how 2D top-down art makes water read as water

Item: `RIMMANDRAKE_RESEARCH_FLOWWORKS_WATER_LOOK_FIRM_ALREADY_PICKED` (owner by card, 2026-11-20 evening: "Maybe dry
and wet have different colors too. Also feel free to look online or creative resources on how to portray that water.
Maybe more aggressive distortions on the surface will make it look more like water. There has to be some artistic
resources out there for guidance.").

Scope: a pit of standing fresh water seen from straight above, at RimWorld's camera, with the floor, walls and things
under it. Written 2026-11-21. Each source is marked **read** (the page was opened and its text read), or **seen in a
search result only** (not opened; it is not evidence). Candidates drawn from this page:
`src/RimMandrake/FlowWorks/model/water_mockup.py` (WET, RIPPLE, BLEND), pick page
`Transient/flowworks_water_look_second_pass/`.

## What the sources say

1. **From straight above you see through water, not a reflection.** Reflections need a low angle; looking down, the
   eye sees what lies under the surface. So a top-down game must say "water" through colour, motion and edges, not
   through mirrored scenery.
   - Clip Studio Tips, "Drawing Water: Basic and Fundamentals" (read):
     https://tips.clip-studio.com/en-us/articles/6224 ("When viewing from directly above, you most likely not see any
     reflection, rather you would instead be able to look through the water to see what is beneath it." It also says
     moving water distorts what it shows: "The more the water moves, the greater the distortion.")

2. **Depth reads as a colour ramp and a loss of the bottom.** Shallow water shows the bottom; deep water hides it.
   Game shaders blend a shallow colour into a deep colour by depth.
   - Godot Shaders, "Pixel Art Water" (read): https://godotshaders.com/shader/pixel-art-water/ (a
     `waterDepthGradient` uniform, deep colour to shallow colour; separate caustic, foam and shoreline settings).
   - OpenGameArt LPC water thread (read): https://opengameart.org/comment/79716 (an artist with "two shallows, a
     'normal,' and a 'deep' water"; Dwarf Fortress's StoneSense stacks "semi-transparent blocks ... it gives a foggy
     effect of deeper getting water"; one variant has "little dots ... aligned with the pebbles underneath. At low
     transparencies this one makes it seem as if there's some kind of refraction going on").
   - **Conflict with an owner ruling:** most game ramps go LIGHT in the shallows. The owner refused a light jump on
     2026-11-12 ("pits are quite dark when dry, then suddenly become light for some reason with just a little water.
     That should not be."), and the first judge refused AQUA for it. So every new candidate keeps FIRM's dark colour and
     strength; the research is applied to the ground and the surface only.

3. **Wet ground is darker and a little more saturated than dry.** Rough and porous materials (sand, clay, soil) darken
   when wet because water lowers the reflection at the surface, so more light reaches the pigment and is absorbed.
   Glossy surfaces barely change.
   - Jensen, Legakis, Dorsey, "Rendering of Wet Materials", MIT, EGWR 1999 (read, the PDF's first pages):
     https://groups.csail.mit.edu/graphics/pubs/wet_materials_egwr99.pdf ("most rough or powdered materials, such as
     sand, asphalt, and clay, become darker when wet").
   - University of Illinois Physics Van, "Why are wet things darker?" (read):
     https://van.physics.illinois.edu/ask/listing/21080 (water's intermediate index of refraction lowers reflection,
     "allowing more light to get to the dye where it's absorbed"; "particularly effective on porous materials").
   - The same OpenGameArt thread (read) cites wet contrast: "things being wet makes the contrast on them higher".
   - Applied: WET and BLEND darken the floor and walls under the water (value x0.70, saturation x1.30) and lay a wet
     band on the ground just above the waterline. A desert pit is dug in sand, soil and mud, all porous: the effect is
     strong there. Rough granite darkens less in reality [guess ~70%]; the mockup treats all grounds alike.

4. **The edge where water meets land carries the most "water" signal.** Games mark it with foam, a pale line, or a
   ragged band, and make waves most visible in the shallows.
   - gamedevserj, "2D water shader tutorial" (read): https://gamedevserj.github.io/posts/2d-water-shader-tutorial
     (features: "distortion, reflection, shoreline foam, and waves"; foam from scrolling noise at the shoreline).
   - Godot Shaders, "Pixel Art Water" (read, above): "foamColor – The color of the foam on the shore".
   - Applied: a thin pale waterline (WET, BLEND), not foam: still water in a pit has no surf.

5. **Motion and distortion make water read as alive.** Scrolling a noise texture to offset what is seen under the
   surface is the standard 2D refraction trick. Distortion is weaker in shallow water.
   - gamedevserj (read, above): distortion by a scrolling noise texture that offsets the screen texture.
   - Godot Shaders, "2D water for topdown games" (read): https://godotshaders.com/shader/2d-water-for-topdown-games/
     (a `clarity` uniform, a base water colour blended with what is under it, and wave highlights).
   - 80.lv, "Caustic surface production guide" (read): https://80.lv/articles/caustic-surface-production-guide
     ("water should look and feel alive ... even a single colored ocean like the one in Zelda: Windwaker looks
     believable. Vertex displacement or scrolling two normal maps across each other are also a good starting point.
     Add in some refraction").
   - Raymond Schlitter (SLYNYRD), "Pixelblog 10: Water in Motion" (read):
     https://www.slynyrd.com/blog/2018/10/12/pixelblog-10-water-in-motion (sine-wave motion as the base of water
     animation; "it all starts with good art. If your scene looks bad without animation, it won't look any better
     with it").
   - Applied: RIPPLE displaces the floor and walls under the water (up to 6 px at 64 px a cell, growing with depth);
     BLEND at half that.

6. **Caustics (net-shaped light on the bottom) say "shallow, clear water".** They come from a curved surface focusing
   sunlight; they are strongest in shallow water.
   - 80.lv caustics guide (read, above): caustics "appear when the light gets refracted by a curved surface and
     projected onto everything behind it ... the surface of the swimming pool getting hit by sunlight".
   - Godot "Pixel Art Water" (read, above): caustic colour, caustic texture and a fade noise as uniforms.
   - OpenGameArt thread (read): in a pool "the waves just causing a sparkle in the water. These sparkles are also
     more-or-less static, but they 'blink'".
   - **Caution from our own history:** on 2026-10-05 the owner refused the overlay's drifting white specks on water
     ("Can't we make the water just look like Shallow water?", `RM_LiquidSurface.cs`, `overlay` field). Ripple light
     must read as light on the bottom, not as specks on top: RIPPLE and BLEND use a thin net that fades by 2 m.

Seen in search results only (not opened; not evidence): Godot "Absorption Based Stylized Water"; the Godot
"realtime caustics" port of Alex Ameye's article; Alexander Ameye's "Stylized water shader" notes; Unity forum "2D water
shader pixel art help"; the Godot asset "Pixel Water" (a `shallow_width` band of lighter water along the coast); 80.lv
"How to build stylized water shader for Nimue". A fetch of alexlaverty.github.io "Making water look wet" returned
HTTP 404: could not look.

## What vanilla RimWorld does (read through RimSage and the texture extract)

- Vanilla shallow water (`TerrainDef WaterShallow`) is an opaque terrain: texture `Terrain/Surfaces/WaterShallowRamp`,
  a near-flat grey-blue 64 px ramp (mean RGB 0.34, 0.38, 0.39, measured), with a second pass
  `waterDepthShader Map/WaterDepth` drawn into the `WaterDepth` subcamera. It does not show the bottom.
- The motion and shine come from global textures set in `TexGame` and `WaterInfo.SetTextures`: `Other/Ripples`
  (`_RippleTex`, a soft 1024 px noise), `Other/Noise` (`_NoiseTex`), and `Other/WaterReflection`
  (`_WaterReflectionTex`, a cloud-like sky picture). Rivers also get a flow texture (`_WaterOffsetTex`).
- The shader code itself is compiled in the game's asset bundles: could not look. What it does with these textures
  is known only from seeing the game: slow drifting light ripples and a moving sky sheen [guess ~80%].
- Lesson: vanilla says "water" with a flat cool colour, a soft edge blend (`edgeType Water`) and slow drifting light.
  It never shows the bottom. FlowWorks pits must show the bottom (owner 2026-10-06: "Is it possible to still show the
  pit walls/floor beneath the translucent water?"), so we need the extra cues above.

## What the mod can draw (from the code, 2026-11-21)

- The pit's floor and drowned walls are FlowWorks' own quads (`RM_ExcavationWalls.SeeThrough`), opaque, under one
  sheet of the water's body colour (`RM_FaceMaterial.SheetMat`, alpha `1 - RM_UnderLiquid.Seen`). `TintMat` and
  `ShadeMat` are VertexColor quads already used for the floor shade and the walls' light. So a wet tint, a wet band
  and a waterline are more quads of the same kind: cheap and static.
- Distortion: the mod ships no shader of its own (no AssetBundle). Vanilla's `Map/TerrainLavaShallow` distorts its
  own texture by `_DistortionAmplitude`, `_DistortionFrequency`, `_DistortionSpeed` (`RM_LiquidLooks` already sets
  them for tar). Drawing the drowned floor and wall quads with it, one material per depth band, would move the bottom
  [guess ~60% that it draws a plain ground texture without its own lava glow; needs a live look].
- Ripple light: `RM_LiquidSurface`'s overlay (MoteGlow, additive, two layers drifting by material offset) exists; a
  caustic-net texture in place of its ripple texture, limited to pit water cells and faded by depth.
- **Cannot:** displace or wet a pawn, an item, a corpse, the table or the ladder. Vanilla's renderer draws them; the
  mod only lays a one-colour cover over their drowned part (`RM_SubmergeDraw`). On a rippled floor they stay sharp.

## The candidates this produced

| key | adds to FIRM | sources |
|---|---|---|
| WET | drowned floor and walls darker and more saturated; a ragged wet band on the ground just above the line; a thin pale waterline | 3, 4 |
| RIPPLE | the floor and walls under the water displaced by moving waves (more with depth); ripple light on the bottom in the shallows; 3 frames | 5, 6 |
| BLEND | WET's ground and line, with RIPPLE's motion and light at about half strength; 3 frames | 3 to 6 |

All three keep FIRM's colour and strength by depth (sources 2's conflict with the owner's 11-12 ruling).
