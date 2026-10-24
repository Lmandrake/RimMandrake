# Template: machine (buildings with ports — pumps, tanks, reels, couplers, hoses, cords, masts)

Everything above the JSON block is sent to the reviewer as the class module; the JSON block is read by code.

⚠️ **This template needs an in-game capture.** The part textures can be judged offline, but the **assembled
panel** — the machine with its coupler, hose and cord attached, connected to a neighbour, each rotation — exists
only in the running game: hose geometry is drawn by C#, port offsets and draw-layer order come from comps and
`Altitudes`. A card without `assembled` is `HOLD_INPUT` (never judged, never accepted). Captures come from a
keeper savegame through `rimworld-live-review`, batched, so a re-evaluation never needs the game again.

## Panels you are given

- **facings.png** + each rotation alone (`south.png`, `east.png`, `north.png`; west if it has its own file).
- **scale.png** — on its footprint beside a vanilla human; the footprint is outlined.
- **assembled_*.png** — in-game capture(s) of the machine with every attached part, connected.
- **siblings.png** (when given) — the other parts of its family (the four GSS looks): the style target.

## How to look (owner's past notes and the measured camera)

1. **One camera for every building** — owner 2026-10-14: *"They should be from the same perspective used to look
   at machines and the wall."* Orthographic, about 35 degrees above the horizontal: a round top is an ellipse
   about 0.56 as tall as it is wide with its top face lit and visible; a box shows its lit top plus a front band;
   extra height extends north. A side elevation, or a hatch drawn as a circle facing the camera, is `CAM_WRONG`.
   When the card prints a measured ellipse ratio, trust it for what it measures.
2. **Pipe bore in its true plane** — owner card 2026-10-23: *"Reel_Deployed_north.png shows the inside of the
   pipe, which implies the pipe is "bent up" towards the viewer … Keep the pipe in the proper perspective plane
   please."* An open bore shows only where the pipe really turns toward the camera.
3. **Parts meet their ports**: each coupler, hose and cord meets its port at the same cell, height and plane, in
   every rotation of the assembled view.
4. **Layering**: what is in front draws in front.
5. **Rotations agree**: same machine, same parts, same palette on every rotation.
6. **Material, not paint** — the colour reads as metal, rubber, ceramic; one of the family's looks.
7. **Wall-mounted or wall-leaning things** (ladders, wall taps, wall reels): look at `wall_context.png`, where each
   facing is composed against the wall it stands on. The lean and perspective of each facing must match THAT wall
   side — an east-wall ladder leans like it is on the east wall. — owner 2026-10-23 (live walk): *"They are correctly
   positioned (translation) against the walls, but their perspective rotation is reversed for East and West."*
8. **Ports are drawn where the code puts them**: the card lists each code-defined port (cell side per facing). In
   every facing and in the assembled view, each code port has a drawn connector at that point, and every drawn
   connector is a code port. — owner 2026-10-23 (live walk): *"It connected from the northern connector of the left one
   to the western on the right, overlapping its handle and ignoring where it has an obvious hose connector."*
9. **Fits its footprint**; real alpha (no backdrop; a small attached floor shadow only where the owner allowed
   one, e.g. `RM_LadderPortable` east/west).

```json template
{
  "template": "machine",
  "version": "machine@v3",
  "modules": ["machine", "part", "hose", "coupler", "reel", "tank", "pump", "wall_mounted"],
  "required_panels": {"*": ["south", "facings", "scale", "assembled"],
                      "wall_mounted": ["south", "facings", "scale", "wall_context"]},
  "checklist": [
    {"id": "CAMERA",      "q": "Drawn from the building camera (about 35 degrees; round tops ellipses about 0.56; top face lit)?", "code": "CAM_WRONG"},
    {"id": "BORE",        "q": "Where does each pipe/hose show its open bore? Only where it turns toward the camera?", "code": "BORE_PLANE"},
    {"id": "PORTS",       "q": "In the assembled view, does every coupler/hose/cord meet its port at the same cell, height and plane?", "code": "PORT_MISFIT"},
    {"id": "WALL_LEAN",   "q": "In wall_context, does each facing's lean/perspective match the wall side it stands on?", "code": "WALL_LEAN_WRONG", "modules": ["wall_mounted"]},
    {"id": "WALL_AXIS",   "q": "In wall_context, name the direction each facing's long axis runs on screen. A ladder (or any fixture that climbs a wall) on an EAST or WEST wall must run east-west, from its top at that wall's rim down and away from the wall into the pit; one drawn running north-south along the wall is wrong, however well it leans. Same for north/south walls: the long axis runs up/down the face, never along the rim.", "code": "WALL_AXIS_WRONG", "modules": ["wall_mounted"]},
    {"id": "PORTS_DRAWN", "q": "Does every code port on the card have a drawn connector at that point in that facing, and is every drawn connector a code port?", "code": "PORT_UNDRAWN", "when": "ports"},
    {"id": "LAYERS",      "q": "In the assembled view, does what is in front draw in front?", "code": "LAYER_ORDER"},
    {"id": "ROTATIONS",   "q": "Same machine, parts and palette on every rotation?", "code": "F_INCONSISTENT"},
    {"id": "SIGNATURE",   "q": "Does it show what the description says it is (its working parts recognisable)?", "code": "DESC_MISS"},
    {"id": "MATERIAL",    "q": "Colour reads as material, not a coat of paint?", "code": "MATERIAL_PAINT"},
    {"id": "FOOTPRINT",   "q": "Inside its footprint (extra height going north), not overflowing or floating?", "code": "FOOTPRINT"},
    {"id": "ALPHA",       "q": "Clean cut-out: no backdrop or painted cast shadow (allowed exceptions on the card)?", "code": "ALPHA_HALO"},
    {"id": "OURS",        "q": "Our own art, not a donor stand-in?", "code": "DONOR"},
    {"id": "SIBLINGS",    "q": "Matches its family's kept parts in style and material set?", "code": "SIBLING_MISMATCH", "when": "siblings"},
    {"id": "OWNER_NOTES", "q": "Is every owner note on the card honoured?", "code": "OWNER_NOTE_IGNORED", "when": "owner_notes"},
    {"id": "LEGIBLE",     "q": "Reads at 32 px per cell?", "code": "LEGIB_32"}
  ]
}
```
