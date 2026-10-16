# Twitching tentacles: greater bulloo and zhool (2026-10-15)

**Ruling.** Owner, by card on `Transient/phase0_p3_questions.md` Q1, 2026-10-15: **"Both twitch"**. The greater bulloo
(`RM_ColossalAerofleet`, The Forge) and the zhool (`RM_OcularJelly`, Contagion) get twitching tentacles on the base
game's own render tree, with no donor code. Cosmetic changes needed for the split art were granted in the same brief.

## 1. Mechanism (proved in the 1.6 source through RimSage)

**`Verse.PawnRenderNodeProperties_Spastic`** is the base game's own random twitch. Its constructor sets
`nodeClass = PawnRenderNode_Spastic` and `workerClass = PawnRenderNodeWorker_Spastic`. On each draw,
`PawnRenderNode_Spastic.CheckAndDoSpasm` picks a new random target (`rotationRange`, `scaleRange`, `offsetRangeX/Z`)
every `nextSpasmTicksRange` and lerps to it over `durationTicksRange`. It holds still when the pawn is dead, in
portraits, in the render cache and on statues. Anomaly's `Toughspike`, `Trispike` and `Fingerspike` trees
(`Defs/Anomaly/PawnRenderTreeDefs/PawnRenderTreeDefs.xml`) use it for their twitching limbs.

The donor's code was `AlphaBehavioursAndEvents.PawnRenderNodeProperties_SpasticScaled`, Alpha Animals' own subclass.
We do not use it. The vanilla class it extended is base game, and every DLC is assumed.

**Why not an `AnimationDef`.** Something has to play an animation (`PawnRenderer.SetAnimation`). An animal can only get
one without code through `RaceProperties.startingAnimation`, which runs once when the renderer is built. Every
`SetAnimation(null)` clears it: an `End` animation finishing, a death, a holding platform. It would also loop in
lockstep, the same motion every cycle. A Spastic node needs nothing to play it, keeps no state that can be lost, and
moves each tentacle at random on its own.

**The one gap, and the code that fills it (zhool only).** A Spastic node's size comes from its own props, never from the
life stage. The bulloo has one life stage, so this does not matter for it. The zhool has three (body drawSize 0.5, 1.25,
1.75), so a baby would wear an adult's tentacles. The fix uses the engine's `PawnRenderSubWorker` hook
(`PawnRenderNodeProperties.subworkerClasses`, applied in `PawnRenderNode.GetTransform`). Our
`RimMandrake.EnvironmentalHazards.PawnRenderSubWorker_KindLifeStageScale`
(`src/RimMandrake/EnvironmentalHazards/Source/RM_PawnRenderSubWorker_KindLifeStageScale.cs`) scales an invisible
`TentacleRig` parent by `current stage drawSize / adult drawSize`. `PawnRenderTree.TryGetMatrix` composes every
ancestor's transform, so the tentacles and their attach points shrink together. Vanilla ships no subworker at all; this
is the only one. It lives in EnvironmentalHazards because Contagion's own assembly is mid-edit by another agent (the haze
work), and EnvironmentalHazards is already Contagion's dependency, composed into the same `RimMandrake.Biomes` mod.

## 2. The split, per creature

Art contract for every tentacle piece: **the root sits at the TOP CENTRE of a 128x128 canvas and the piece hangs straight
down.** Every node uses mesh 1x1 (drawSize 1, so Spastic's mesh size and scale do not square each other) and
`pivot (0.5, 0.05)`. `PawnRenderNodeWorker.PivotFor` gives `-(pivot - 0.5)` = 0.45 above the mesh centre, which is the
root. So the root stays fixed through every twitch and every `drawData.scale`, and `offset.z = attach.z - 0.45`.
`drawData.scale` sets the hanging length.

Draw order: the tentacles draw behind the body (layer -5 or -6, body 0), so the bell's rim hides each root seam. The one
exception is the zhool's oral arms, which hang in front of the mouth on the south face (+5). West mirrors east: offsets
mirror on their own (`DrawData.OffsetForRot`), while flip and rotation are given explicitly, as Toughspike does. Every
piece carries `linkedBodyPartsGroup Arms`, so the tentacles vanish once every feeler is lost. `rotDrawMode Fresh, Rotting`
hides them on the desiccated corpse, which uses vanilla art.

### Greater bulloo (`RM_ColossalAerofleet_Twitch`, staged; body drawSize 2.5, one stage)

| picture | look | nodes | attach (south, cells) | length |
|---|---|---|---|---|
| `RM_ColossalAerofleet_Bell` | the bell, gel sacs, drips and escort bulloos; no feelers | body | - | 2.5 |
| `Feelers/..._FeelerA` | long, thick, curled tip | outer left and right | (∓0.80, -0.25) | 1.0 |
| `Feelers/..._FeelerB` | short, stubby | inner left and right | (∓0.35, -0.38) | 0.75 |
| `Feelers/..._FeelerC` | forked grasping tip | front centre, under the head | (0, -0.42) | 0.85 |
| `Feelers/..._FeelerD` | thin whip, S-curve | back | (0.15, -0.30) | 1.0 |

East: the roots run along the underside from -0.95 (back) to +0.45 (front) and trail back 6 to 28 degrees. The twitch is
slow and gentle for a creature this size: ±10 to 16 degrees, 25 to 90 ticks per move.

### Zhool (`RM_OcularJelly_Twitch`, staged; body drawSize 0.5 / 1.25 / 1.75, numbers are the adult's)

| picture | look | nodes | attach (south, cells) | length |
|---|---|---|---|---|
| `RM_OcularJelly_Bell` | the veined dome, eye-spots and mouth; no tentacles, no oral arms, **no painted haze puff** | body | - | 1.75 |
| `Tentacles/..._TentacleA` | long wavy ribbon, dark red to pale pink | outer left and right | (∓0.38, -0.12) | 0.8 |
| `Tentacles/..._TentacleB` | shorter, curled tip | inner left and right | (∓0.18, -0.18) | 0.65 |
| `Tentacles/..._TentacleC` | thin whip | back centre | (0.05, -0.10) | 0.75 |
| `Tentacles/..._TentacleD` | frilled oral-arm cluster | under the mouth; in front on the south face | (0, -0.22) | 0.55 |

East: the roots run from -0.50 to +0.45 and trail back 10 to 45 degrees (it drifts mouth-first). It twitches faster than
the bulloo: ±10 to 24 degrees, 10 to 50 ticks per move.

The bell drops the reddish puff painted into the picked render. The haze is becoming a real in-game effect (separate
work, Q2), and a painted puff would double it and would turn with the body.

## 3. Fallback until the art lands

- Everything for the twitch is **staged** in `src/RimMandrake/TheForge/Staged/TentacleTwitch/` and
  `src/RimMandrake/Contagion/Staged/TentacleTwitch/`. Each holds the tree (`Defs/PawnRenderTreeDefs/<creature>_Twitch.xml`)
  and the wiring patch (`Patches/<creature>_TwitchWiring.xml`, which adds `race/renderTree` and repoints the body `texPath`
  to the bell). The game never loads a `Staged/` folder, and both are held in `src/DEPLOY_HOLD.txt`.
- **Why staged and not just unreferenced:** `texture_gap_lint.py` fails every shipped texPath with no picture, and its
  allowlist is frozen and shrink-only. A tree in `Defs/` naming ten undrawn pictures would be ten new gaps. The first
  filing (commit 5c28d32a8) put them in `Defs/` and `Patches/`; the same day they moved here.
- The race defs are untouched, so both creatures keep vanilla's Animal tree and their one whole-body picture.
- **Go-live, per creature,** once the owner accepts its split art and `art.py install` has placed it at the `install_to`
  paths:
  1. Move the tree into the mod's `Defs/PawnRenderTreeDefs/`.
  2. Fold the wiring patch's two operations into the race def (`renderTree` in `race`; the bell `texPath` in every life
     stage), then delete the patch.
  3. Delete that mod's `Staged/*` hold line, and deploy.

  The zhool also needs the EnvironmentalHazards DLL carrying the subworker, which is already committed. With the art
  missing, the wiring would draw pink squares.

## 4. Art rows

`design/RimMandrake/tentacle_twitch_art_rows_2026-10-15.json` holds 30 jobs, filed 2026-10-15 under
`DONOR_DEFS_PORT_TO_OURS_1`: per creature, the bell plus 4 pieces, each in east, north and south. Each job is
`derive_from` the **matching facing** of the owner's picked render (`gapall_AA_ColossalAerofleet_v1_<facing>`,
`gapall_AA_OcularJelly_v1_<facing>`). That is the artpipe's edit-of-an-accepted-render contract: same individual, same
palette, no donor pixels. `reference` was rejected because it arms reskin validation, whose ±6% span gate fails by
design once the tentacles leave the body. Job ids are `tt_bulloo_{bell,feelera..d}_v1_{east,north,south}` and
`tt_zhool_{bell,tentaclea..d}_v1_{east,north,south}`.

Known risks in the filing:
- The derive prefix says "same scale". A single piece on a 128 canvas is not at the master's scale, but the row prompt
  says so explicitly.
- The bulloo's feelers are small, so its feeler-less bell may land close to the master. The daemon's
  near-duplicate gate (distance < 4.0) would then fail it, and it would need refiling with a stronger prompt.

## 5. What needs a live look (joint sitting or bridge, after the art is installed)

Every attach point, rotation and length above is a first guess from the picked renders. Check them in
`Dialog_DebugRenderTree` (dev mode, which edits offset, pivot and layer live), then write the numbers back:
1. The roots sit under the rim on all four facings, and west mirrors east correctly. Flip handling for
   `Graphic_Multi` on Spastic nodes copies Toughspike and has not been seen with our art.
2. Twitch speed and amplitude read as alive rather than frantic, at the zoom the owner plays at.
3. A baby and a juvenile zhool wear proportionate tentacles (the life-stage subworker).
4. Layering: no tentacle draws over the bell, except the zhool's oral arms on the south face.

Not built: a Mod Settings switch for the twitch. The standing rule asks for on/off per major feature. This one is
cosmetic and needs C# to swap the tree at startup; it is owed when the wiring lifts, if wanted.
