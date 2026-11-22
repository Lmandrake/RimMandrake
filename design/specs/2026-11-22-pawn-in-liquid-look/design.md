# How a colonist looks in, and coated by, a FlowWorks liquid

Item: `RIMMANDRAKE_DESIGN_PAWN_IN_LIQUID_LOOK_WATER_SHEET_IS_A_MISTAKE`. Date: 2026-11-22. Status: a design for the
owner to pick from. Nothing in the mod is changed.

**His words** (FlowWorks walk, 2026-11-22): *"This whole "water sheet" idea is a mistake. It looks TERRIBLE. It's not
even aligned with a body. We need a much better way to cover a colonist with the image of being slicked with various
liquids. [...] Don't just play with the mask or layering of the current implementation. Come up with radical new
concepts to consider."* Earlier, at station 33: *"clearly placeholder"*.

The mockups are in `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_DESIGN_PAWN_IN_LIQUID_LOOK_WATER_SHEET_IS_A_MISTAKE\`
(full size, uncompressed). Smaller copies are in `mockups/` beside this page. `mockups.py` beside this page makes them.

## 1. What the game draws today, and why it is out of line

The code is `RM_SubmergeDraw.CoverPawn` (`src/RimMandrake/FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs`, lines 559 to
618). It runs after vanilla draws a pawn that wades, lies or is dead in a wet pit.

1. `CoverPawn` takes `r.SilhouetteGraphic` and draws it in the liquid's colour over the pawn.
2. For a human, vanilla sets `SilhouetteGraphic` to the **life stage's** picture, not the pawn's picture
   (`PawnRenderer.RenderPawnAt`, read from RimSage: `pawn.ageTracker.CurLifeStage.silhouetteGraphicData.Graphic`).
3. For an adult that picture is `Things/Pawn/Humanlike/Silhouettes/Silhouette_HumanAdult`: one 64-pixel icon, a round
   head above a pill-shaped torso. It is a `Graphic_Single` with `drawSize` 1. Vanilla uses it to show a pawn that is
   behind a tree. [measured: the def in `LifeStages.xml`, and the texture, opened]
4. A pawn's real body is drawn at size 1.5. The head, the hair and the clothes are separate pictures with their own
   offsets. The icon has one facing only.

So the "water sheet" is a small generic head-and-torso icon, centred on the body's position. This explains each fault
in his capture [measured from code and texture; not run live]:

| What he saw | Cause |
|---|---|
| Two blue blobs | The icon's round head and its torso. |
| The blobs are smaller than her | Icon size 1, body size 1.5. |
| The blobs sit off her body | The icon's head is at its own centre-top. Her real head is drawn at the body's head offset. The icon's head lands on her chest. |
| The blobs do not follow her facing | The icon has one facing. Her body has three. |
| Her hair, face and dress stay bright | The icon covers a torso shape only. |

A second path exists (`TryCoverWithOwnPicture`). It covers a lying, wholly drowned pawn with the pawn's own cached
picture. It runs only when vanilla has a cached frame for that pawn, and vanilla uses that cache only at far zoom
(`ZoomRootSize > 18`). At the zoom of his capture the icon path ran. [guess ~85%: read from code, not run live]

The fault is not the mask and not the layer order. The drawn picture is the wrong picture. Any concept below that
starts from **the pawn's own picture** cannot have this fault.

A second fault is in the law, not in the draw. The law maps metres to the sprite in a straight line
(`RM_UnderLiquid.Share`). A RimWorld colonist has a head that is half of the sprite's height. So 1 m of water on a
1.75 m colonist puts the line at the chin. The player expects 1 m at the waist. The fix is in §5 (body landmarks).

## 2. The liquids

Read from the defs on 2026-11-22: `Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml` (23 LiquidDefs),
`Cauldron/Defs/LiquidDefs/RM_Liquid_VentCondensate.xml` (1), and the canal FluidDefs in
`Defs/Canals/FluidDefs/` (16). "Clear" and "opaque" come from the `seeThrough` field of each liquid's surface look.
The class of a single liquid in a family is [guess ~80%] where I did not open its own look.

| Family | Liquids in the defs | Sight | Coats a pawn today | What makes it different on a pawn |
|---|---|---|---|---|
| Plain water | fresh water, salt water, brine | clear | no (water and icy water wash a coat off) | wet cloth, drops |
| Tinted water | rust-tinted, verdigris, amber, violet, chalky water; vent condensate (Cauldron) | clear, coloured | no | the same as water, in its colour |
| Hot and cold water | boiling water, icy water | boiling: clear; icy: opaque white | no | steam; frost |
| Harmful water | toxic water / poison, acid water, reaction liquor | clear, green or pale | no | fizz, smoke, a sick colour |
| Fuels | chemfuel, astrofuel, liquid propane | part clear | no | a rainbow sheen; it can burn on the pawn |
| Thick and dark | tar, oil | opaque | yes (`coats`) | glossy black, strings, slow |
| Slimes | red, green, white, yellow slime; living slime (no colour yet) | opaque | yes | thick, bright colour, slippery |
| Blood | blood | opaque | yes | dark red, dries brown |
| Lava | `RM_Liquid_Lava` (a def with no colour and no canal fluid: planned, item `LAVA_LIQUID_BUILD_PROMISED_BY_CARD`) | opaque, glows | not built | light from below, fire |

There is no mud def. `RM_Liquid_NotDrinkable` is a marker, not a liquid.

## 3. The states a player must be able to read

| State | What the player must know |
|---|---|
| Ankle, knee, waist, chest deep | how deep she is, and which liquid |
| Swimming | she is afloat (vanilla draws the head only) |
| Fully under, standing or lying | she is there, where she is, and that she is in danger |
| Lying in a shallow liquid | she is down in it, not on dry ground |
| Carried | the carrier's state; the carried pawn keeps its own coat |
| Out on dry ground, coated | which liquid is on her, how much, and that it wears off or washes off |

`standing_rulings.md` says that no pawn vanishes without a sign that the player can read. A pawn under an opaque
liquid has no picture. So each concept needs a sign for that case.

## 4. The concepts

Each concept is a different kind of answer. A to D have mockups. For each: what the player sees, how it stays in line
with the body, what it costs, and where it fails. Costs are [guess ~60%]; none is built.

### A. Cut at the line (mockup `concept_cut.png`)

The pawn's **own picture** is cut at the surface. Above the line it is drawn as usual. Below the line, in a clear
liquid, it is drawn under the liquid's real surface, so the real water tints it. In an opaque liquid the lower part is
not drawn. A ring sits where the body meets the surface.

- Water: head and shoulders plain; the dress dim and blue below the ring. Tar: a head and shoulders that stand in
  black; nothing below. Lava: the same as tar, with a bright ring. Lying under 2 m of water: her whole picture, dim.
- In line: always. It is her own picture, cut by a straight line in world space. It follows facing, lying, a child,
  an animal and a mech, because all of them are drawn by the same render tree.
- Cost: draw the wet pawn once into a small private texture with vanilla's own call
  (`Find.PawnCacheRenderer.RenderPawn`, the call that vanilla uses for its far-zoom cache). Then draw two cut quads.
  One texture per wet pawn. It is drawn again when the facing, the clothes or the pose changes. No art.
- Fails: a pawn that plays an animation needs a new texture each frame. A weapon in the hand is drawn outside the
  picture, so it is not cut. A lying pawn has no line (see §5). Under an opaque liquid it shows nothing, so it needs C
  or E for the sign.

### B. The tide mark (mockup `concept_coat.png`)

The liquid is painted on the pawn's **own pixels**, up to the highest line that the liquid reached. She keeps it on
dry ground. It wears off with time and washes off in water. This is the look that the coat condition
(`RM_LiquidCoat`) does not have today.

- Water: the cloth is darker below the line, with a little sheen; it dries in a short time. Tar: glossy black to the
  line, with a ragged edge and a rim of light. Lava: not a coat; burns and soot (the vanilla burn look) take its place.
- In line: always. Each part of the pawn (body, clothes, head, hair) is drawn a second time with its own texture as
  the mask. Vanilla does this for firefoam (`PawnFirefoamDrawer`: a splatter texture masked by the body texture, drawn
  over the clothes).
- Cost: one more draw for each coated part. One small shader that paints below a height, or the cut texture from A
  with a second tint. Art: one tiling "wet" pattern and one "thick" pattern; the colour comes from the LiquidDef.
- Fails: black tar on a black-outlined sprite loses the shape without the rim of light. At default zoom a water coat
  is hard to see (the mockup shows this). It is a second system to keep true: the picture must match the condition.

### C. The surface answers (mockup `concept_surface.png`)

The pawn is drawn plain. The **liquid** shows that she is there. Water makes rings and a lip that follows her outline.
A walker leaves a wake. A thick liquid keeps an open furrow behind the walker, and the furrow closes at a rate that
the liquid's thickness sets: fast in oil, slow in tar. On dry ground she leaves wet prints and drops in the liquid's
colour, and they fade as the coat wears off.

- Water: rings. Tar: a rolled lip and a dark track back to where she came in. Lava: a bright lip and sparks.
- In line: the lip is made from her own outline. The rings and prints need only her position.
- Cost: flecks and a few quads for each wet pawn. Vanilla has the ripple fleck (`PawnWaterRippleMaker`). The furrow
  is new: a short list of past positions for each wader. Prints can be filth, which is also a real effect in the
  colony.
- Fails: it does not hide the legs, so alone it does not say how deep she is. A still pawn makes no wake. Many waders
  make many flecks.

### D. The body under the surface (mockup `concept_under.png`)

The drowned part is drawn as the eye sees it through a liquid: bent by the surface, dimmer, with less colour, with
moving light lines, and with a shadow on the floor. The shadow moves away from the body as the liquid gets deeper.
That offset is how the player reads depth. In a shallow opaque liquid a lying body shows as her own shape, draped in
the liquid.

- Water: a clear picture of her, wobbling, with a shadow below. Tar: nothing for a deep body; a draped shape for a
  shallow one. Lava: nothing.
- In line: yes; it is her own picture. The wobble is small, and it is the point.
- Cost: the texture from A, plus one shader for wobble and light lines. One more quad for the shadow.
- Fails: it helps only in clear liquids. A wobble can read as a draw fault if it is too strong. At default zoom the
  wobble is lost; the dim colour and the shadow carry it.

### E. The liquid's tell (no mockup)

Each liquid has one moving sign on the pawn, during and after: steam for boiling water, fizz and thin smoke for acid,
frost for icy water, a rainbow sheen for fuel and oil, slow strings for tar and slime, flies for old blood, heat
shimmer and sparks for lava.

- In line: it needs only the pawn's position and height.
- Cost: one fleck or mote set for each family (about eight). Low cost per pawn.
- Fails: it says which liquid, not how deep. `GUIDING_PRINCIPLES.md` entry 4 binds here: a sign that implies harm
  (steam, smoke, fizz) must appear only where the harm is real.

### F. A change of pose (no mockup)

No overlay. The pawn takes a pose that belongs to the liquid. A downed pawn in deep clear water floats face up at the
surface. A corpse floats face down. A swimmer keeps vanilla's head-only pose, with a faint picture of the body below
in a clear liquid. A pawn in tar leans and lifts its arms.

- In line: yes; it is the pawn's own picture in a new place and angle.
- Cost: code for the float poses; new body art for the tar pose, for each body type and facing.
- Fails: a floating body says "afloat", but the drowning law says she is on the floor. The pose must not lie about
  the mechanic. New art for each body type is the largest art cost on this page.

### G. The liquid as a garment (no mockup)

Painted art, made like clothes: for each body type and facing, a "socks", a "trousers" and a "whole body" layer of
liquid with a dripping edge. One grey set, tinted for each liquid.

- In line: by art, the same way that a shirt is in line with a body.
- Cost: 5 body types x 3 facings x 3 levels = 45 textures, and a second set for thick liquids.
- Fails: it does not cover a coat or armour that is wider than the body. It has no answer for a child, an animal or a
  mech without more art.

### H. The tar statue (no mockup)

A pawn that is wholly coated in a thick liquid is drawn through vanilla's statue path (`PawnRenderFlags.Statue`, with
a stuff colour) in the liquid's colour, with the eyes left bright.

- In line: yes; vanilla draws it. Cost: low, but it turns off the far-zoom cache for that pawn.
- Fails: it fits only the wholly coated case, and it can look comic.

### I. A ring on the ground (no mockup)

A disc in the liquid's colour under the feet, and an icon.

- Cost: the lowest. Fails: it does not answer his words ("the image of being slicked").
  `GUIDING_PRINCIPLES.md` entry 2 also argues against a marked region with no physical meaning.

### What other top-down games do

From memory, not checked [guess ~70% each]. The GPT consult that was to add to this list did not run (§9).

- *The Legend of Zelda: A Link to the Past*, *Stardew Valley*, *Don't Starve*: the lower body is not drawn in shallow
  water, and a ripple sits at the cut. This is concept A.
- *Noita*: a wet, oily or bloody character is stained with the liquid's colour, drips it, and has a named status.
  This is concept B with E.
- *Hyper Light Drifter* and the *Pokémon* games: a reflection or a dim picture of the character in the water. This is
  near concept D.
- *Oxygen Not Included*: a status ("soggy feet") and drops, with no change to the body. This is concept E.

## 5. Two rules that every concept needs

**Depth maps to body landmarks.** The line sits at the ankle, knee, waist, chest and neck of the sprite, not at a
straight share of its height. Each life stage and each animal gives its landmarks as shares of its picture. For a
vanilla adult the waist is near 40% of the body picture's height from the feet [guess ~70%, read from the texture by
eye]; the straight law puts 1 m on a 1.75 m pawn at 57% of the whole sprite, which is the chin (the pawn's height in
the law is `RM_Drowning.HeightOf`, not read here). This moves no bar: the bar `pawn_height_follows_depth` says only that a pawn
sinks with depth.

**A lying body has no line.** A lying body is a low round shape. A shallow liquid covers its rim first and its middle
last. So the cover for a lying pawn grows inward from her own outline (the mockups do this). When the liquid is over
the body's height, the whole picture is under.

## 6. The ranking and the pick

| Rank | Concept | Why |
|---|---|---|
| 1 | A. Cut at the line | It removes the fault he saw, because it draws her own picture. It says how deep she is. It needs no art. |
| 2 | D. The body under the surface | It is the lower half of A for a clear liquid. With A it is the full answer for water. |
| 3 | B. The tide mark | It is the only concept that shows a coat on dry ground, which is what he asked for ("slicked"). |
| 4 | C. The surface answers | It gives the sign for a pawn under an opaque liquid, and it makes tar look thick. |
| 5 | E. The liquid's tell | Low cost. It separates liquids that share a colour (water, boiling water, acid). |
| 6 | F. A change of pose | Strong for a corpse that floats. It costs the most art and can disagree with the drowning law. |
| 7 | H. The tar statue | A cheap special case of B. |
| 8 | G. The liquid as a garment | The same result as B, by hand, with 45 or more textures. |
| 9 | I. A ring on the ground | It does not answer his words. |

**The pick is A + D + C + B together** (mockup `concept_pick.png`, and the last rows of `comparison_sheet.png`). One
texture of the wet pawn serves A, D and B. In a liquid: her own picture, cut at a body landmark, with the lower part
seen through a clear surface, and the surface answering round her. On dry ground: the tide mark, with drops and
prints. E is added for each liquid that can harm.

The trade-offs:

- The private texture is one more picture for each wet pawn. Few pawns are wet at one time, except in the moat raid
  (vision line 4), where many raiders swim. A swimmer keeps vanilla's head-only draw and needs no texture.
- A pawn under a deep opaque liquid still shows only a dimple and bubbles (see the "tar: lying under 2 m" panels).
  That is honest: tar is opaque. If it is too weak a sign, her name label stays, or H is used for the moment she
  comes out.
- B is weak for water at default zoom. That is acceptable if water dries in a short time; the drops and prints carry
  it.

Load on every map (`GUIDING_PRINCIPLES.md` entry 5): nothing is drawn or ticked for a pawn that is not in a liquid and
has no coat. The new reading load is one idea: "the line on the body is the depth". Each part gets an on/off Mod
Setting, default on.

## 7. Convergent or Divergent: the owner rules on this split

Proposed, for FlowWorks 0.1.0 (current) and the next version:

| Part | Proposed class | Reason |
|---|---|---|
| Stop drawing the generic icon; draw the pawn's own picture, cut at the line (A), and whole when she lies under | **Convergent, a Problem, 0.1.0** | It is the misaligned placeholder that he rejected. It serves the locked bar `pawn_height_follows_depth`. |
| Body landmarks in place of straight metres (§5) | Convergent, 0.1.0 | Without it, 1 m of water reads as chin deep. No bar pins a number. |
| The ring at the line | Convergent, Polish | It helps A; A passes without it. |
| D: wobble, light lines, floor shadow | Divergent, next version | New look; not needed to remove the fault. |
| B: the tide mark on the body | Divergent, next version | The bar `inv_liquid_coating` asks for a named condition with "a clean, not crude, look" and a wash. The condition exists and has no picture by design (`RM_LiquidCoating.cs` header). A picture for it is an addition. |
| C: furrow, lip, prints | Divergent, next version | New effects. |
| E, F, H | Divergent, next version or later | New effects and art. |

## 8. The first build step (after he picks)

1. A test first, red today: an offline selftest that fails while `CoverPawn` reads `SilhouetteGraphic`, and a live
   look row (a naive judge reads a zoomed capture of a standing and a lying pawn in 0.5, 1 and 2 m of water and of tar).
2. In `RM_SubmergeDraw`: for a wet pawn, draw the pawn into a private texture with `PawnCacheRenderer.RenderPawn` and
   draw it as two cut quads in place of vanilla's draw: the upper quad with the usual shader, the lower quad with the
   under-sheet material that the file already has (`UnderSheetMat`) for a clear liquid, and no lower quad for an
   opaque liquid. Delete the icon cover and `TryCoverWithOwnPicture`.
3. Add the landmark table for the human life stages. Animals and mechs keep the straight law until each has a table.

This design replaces the item `RIMMANDRAKE_REDRAW_FLOWWORKS_SUNK_PAWN_NOT_TWO_BLUE_PATCHES` (its open question, which
path drew his pawn, is answered in §1). I did not find an item named
`RIMMANDRAKE_REPORT_SUBMERGE_SHADOW_QUEUE_JUDGE_CANNOT_SEE_ORDER` in `infrastructure/state/items/` or `items/closed/`.

## 9. What is not tested

- Nothing here ran in the game. §1 is read from our code, vanilla's code and the texture. The mockups are Python
  pictures made from vanilla textures; they are not captures.
- The costs are estimates. The private texture's cost with many wet pawns is not measured.
- Whether vanilla's `PawnCacheRenderer` can be called for a pawn at close zoom without a side effect is not tried.
- The mockups show one colonist (female body, shirt, bob hair), facing south and lying. They do not show east or
  north, a child, an animal, a mech, a carried pawn, a held weapon, lava or a slime.
- **The GPT consult did not run: UNRUN.** `gpt_consult.py` returned `VERDICT=AUTH exit=20` on the WSL Codex and on the
  Windows Codex (`--codex win`) at 2:43 PM PST: "your refresh token was revoked. Please log out and sign in again."
  The Codex login is an interactive act. The prompt is saved as `gpt_consult_prompt.md` beside this page. The command
  to run it after a sign-in:
  `python3 src/RimMandrake/Utils/gpt_consult.py --prompt-file design/specs/2026-11-22-pawn-in-liquid-look/gpt_consult_prompt.md -i <comparison_sheet.png> -m gpt-6.1-sol --effort high --out design/specs/2026-11-22-pawn-in-liquid-look/gpt_consult_answer.md`
  So the ranking has had no skeptical second read.
