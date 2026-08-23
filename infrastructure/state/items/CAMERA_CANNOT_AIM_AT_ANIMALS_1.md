## spec

**Nothing can point the camera at a spawned animal, so nothing can photograph one.**
Measured 2026-08-23 01:0x on a live dev quicktest map:

| call | result |
|---|---|
| `rimworld/jump_camera_to_pawn` `pawnName="Jet"` (a colonist) | ✅ `success: true` |
| `rimworld/jump_camera_to_pawn` `pawnName="Colorful tortoise"` | ❌ `success: false`, no message |
| `rimworld/jump_camera_to_pawn` `pawnName="Pinkbird"` | ❌ `success: false`, no message |
| `rimworld/jump_camera_to_pawn` `pawnId="GRimTortoise41415"` | ❌ `success: false`, no message |
| `jawa/list_pawns` → cell coordinates | ❌ `x` and `z` read **0** for every pawn on the map |

🔑 **The two failures compound into a dead end.** `screenshot_cell_rect` is the other
way to frame a subject, and it takes `x`/`z` — which is exactly what `list_pawns` will
not give. So an animal can be spawned, aged, and confirmed error-free, and still never
be *looked at*.

⚠️ **`success: false` with no message is its own defect.** It does not say whether the
name did not resolve, whether animals are excluded deliberately, or whether the pawn was
not found on the current map. The schema's own hint points at
`rimworld/list_colonists` for ids, which suggests the tool may be colonist-scoped by
design — in which case it should SAY so rather than returning a bare false.

## Why it blocks real work

`QUICKTEST_VISUAL_ROUND_1` exists to answer "does this thing DRAW", and its whole method
is spawn → look → describe. The spawn half now passes for `GRimTortoise` and
`GRimPinkbird` — zero log lines on spawn and zero on ageing to juvenile — and the look
half cannot be reached at all. The same wall stands in front of every future
spawn-and-look item, including `RAKATA_SLEEPERS_LOOK_RIGHT_1` and
`PHYTOKIN_BARK_EAST_LOOK_1`.

## Two things the fix must not lose

⛔ **Do not "solve" this by describing the def instead of the render.** A texPath that
resolves is not a sprite that draws; that distinction is the entire point of a look
round.

🔴 **Whatever aims the camera, the capture still needs a settling frame.** Measured the
same night: a screenshot taken immediately after `rimworld/set_camera_zoom` catches
pawns mid-texture-swap and renders them as blank white silhouettes — body and head solid
white with black outlines, while their weapons, gear and the terrain draw perfectly. It
reads as a catastrophic missing-texture bug and is not one; a second capture after the
camera settles shows the same pawns with hair, faces and clothing. **Take a throwaway
shot, then screenshot the second one.**

## verify

- `rimworld/jump_camera_to_pawn` succeeds for an animal by name and by id, or refuses
  with a message that says which of the three reasons applies.
- `jawa/list_pawns` returns real cell coordinates, so `screenshot_cell_rect` can frame
  any pawn without the camera at all.
- A juvenile `GRimTortoise` and a juvenile `GRimPinkbird` are photographed and described.

## criteria

Any spawned thing on the map can be framed and photographed from the bridge, and the
resulting PNG is verified to differ from the previous one before anybody reads it.
