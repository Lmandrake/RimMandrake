# MOISTURE_VAPORATOR_WALL_CLIP_1 — fixed offline, live verification owed

Moisture vaporator graphic extends/clips through an adjacent wall instead of
sitting flush.

## 2026-09-05 (FOUNDRY, offline while BENCH held the bridge)

**Def**: `src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/ThingDefs_Buildings/
Absorbed_KotorCore_Building_MoistureVaporators.xml`, `KotOR_MoistureVaporator_big`
— 1x1 footprint, `Graphic_Single`, `drawSize=(3,3)`.

**Cause**: it followed sibling `KotOR_watertank`'s `drawOffset` formula
(`offset_z = drawSize/2 - 0.5`, anchoring flush on the south edge) verbatim,
but that formula assumes the art fills 100% of its canvas — the watertank's
does, measured via `PIL.Image.getbbox` alpha-bbox. The vaporator's real
content only fills ~90% of canvas height, with the padding entirely on the
north side, so on paper the offset looked correct (`1.5-0.5=1`) while the
actual opaque pixels overhung **1.71 tiles north, 0 tiles south** — enough to
draw straight through a wall placed on the north side.

**Fix**: `drawOffset` re-centered to `(0,0,0)` (drawSize left at `(3,3)` — the
tower's scale is intentional, not the bug). New overhang, from the same
alpha-bbox measurement: **0.71 tiles north, 0.99 tiles south** — both at or
under the watertank's own established 1.0-tile norm.

The asset itself is not broken — it's a legitimately tall multi-part device
(base, tower, cross-struts, propeller), not padding pretending to be content.

## criteria
- [x] Root cause identified and measured (not guessed): uncompensated
      drawOffset vs. actual alpha-bbox content bounds.
- [x] Fix applied, arithmetic shown, XML well-formed.
- [ ] **Live verification owed** — place one against a wall on the north
      side and the south side in a quicktest and screenshot; picking "center
      the offset" over some other split was a judgment call made without a
      bridge to check it against. Whoever next holds the bridge should
      confirm the reduced overhang actually reads as flush.
