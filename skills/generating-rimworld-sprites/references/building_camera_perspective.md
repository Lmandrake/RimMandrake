# The building camera — what perspective RimWorld buildings are drawn in

Measured 2026-10-14 from 27 shipped buildings (Core, Odyssey, Vanilla Expanded, other mods) and 4 wall atlases.
Full table, method and contact sheet: `design/RimMandrake/building_camera_perspective_2026-10-14.md`.
Why it exists: the owner rejected two tall tanks drawn as side elevations — *"They should be from the same
perspective used to look at machines and the wall."*

## The numbers to draw to

- **Orthographic.** Vertical edges stay parallel; nothing converges.
- **~35° above horizontal** (measured band 29–38°).
- **A round thing's top rim is an ellipse 0.56 tall for its width** (measured 0.48–0.64: Core DeepDrill 0.55,
  Core BiofuelRefinery centre tank 0.57, VFE Props tanks 0.58–0.60, VHGE gas tank 0.61, Spaceports tank 0.48).
  The top face is fully visible and is the brightest surface. A hatch, lid or flange on top lies IN that ellipse —
  never a full circle facing the camera.
- **Light from overhead and in front:** highlight down the centre / centre-left of the front face, darker sides.
  Paint no cast shadow; the engine draws building shadows.
- **A wall's front face is a light band 30–39 % of its drawn depth**; the top face is the rest. Box machines read
  the same way: lit top, a front band about a third of the depth.
- **Height lives in the footprint first.** Ludeon and VE fit the whole drawing inside `size` (`drawSize` = `size`,
  overhang ≈ 0). A thing taller than its footprint is deep extends NORTH: `drawSize.y > size.z`,
  `drawOffset.z = (drawSize.y − size.z) / 2`, base on the footprint's south edge.

⚠️ Walls and round machines do not share one consistent camera: the ground grid stays unforeshortened and vertical
faces are a stylised band. For round things the 0.56 ellipse binds; for boxes, the lit top plus a ~⅓ front band.

## How to get it out of the image model

A prompt that names an angle is not enough — the 2026-10-14 tanks were prompted for game art and came back as side
elevations. **Anchor the camera with a geometry guide as image 1 of an edit**: a grey blockout drawn at the right
ellipse ratio, with the family's real sprite as image 2 for materials. `src/RimMandrake/FlowWorks/art_source/
TankTall/v2/guide.py` draws one for an upright cylinder (`guide.py <out> W H cx a top_y bottom_y [ratio]`). Both
tanks landed at 0.56–0.57 on the first pass this way.

## Checking it

```bash
python3 skills/generating-rimworld-sprites/scripts/validate_sprite.py --reference tank.png --upright-cylinder
python3 skills/generating-rimworld-sprites/scripts/validate_sprite.py --reference old.png --candidate new.png --upright-cylinder
```

Fits the silhouette's top arc (each half separately, so a pipe on one side is tolerated) and WARNs outside
0.46–0.66 or when the fit is unreliable (rms > 3 px: lugs or valves cross the rim). **How it lies:** a domed head
drawn in pure side elevation is also an ellipse arc in silhouette and can pass — the check proves the rim's shape,
never that a top face is painted. Look at the picture beside a vanilla machine at game scale.
