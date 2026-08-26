# TEMPLATE_ENGINE_ACCEPTANCE_1 — the engine placed its first cells in a live game

2026-08-26, seat CHECK, full 582-mod list, one map, bridge held. `dwelling` built at
`rect 170,170,18,10`, 3 rooms, 4 occupants, seed 1. Plan: **112 terrain · 81 things · 180 roof**,
`refusals: []`, `notes: []`. Working files in `world/_lf/tpl_*.json`.

## 🔴 Found BEFORE the run: 4 of the 13 compiled calls cannot execute at all

`rimplace` compiles `jawa/set_terrain_batch` and `jawa/set_roof_batch` with a **`rect`**
parameter. Neither tool has one.

```
jawa/set_terrain_batch  accepted keys: ['layer', 'ops', 'refresh', 'terrainDef']
jawa/set_roof_batch     accepted keys: ['ops', 'refresh', 'roofDef']
jawa/build_batch        accepted keys: ['faction','hitPoints','ops','quality','readBack','stuff','wipeExisting']
```

Proven live on a spare cell rather than assumed:

```
before                 : Sandstone_Rough
{"rect":"200,200,2,2","terrainDef":"Gravel"}  -> success=False  "ops is required, e.g. 'Sand:10,20,3,4;…'"
after rect form        : Sandstone_Rough          <- nothing happened
{"ops":"Gravel:200,200,2,2"}                  -> success=True   "4 cell(s) changed"
after ops form         : Gravel
```

✅ **The bridge refuses loudly — `success: false` with the right message.** This is not a silent
failure; it is a compiler that is out of sync with the tool contract. 3 terrain calls and 1 roof
call would each have failed, losing all 112 terrain and 180 roof cells.

⇒ The run below used a `rect → ops` translation so the rest of the item could still be answered.
Filed as `TEMPLATE_RECT_PARAM_NOT_ACCEPTED_1`.

## Criterion 3 — nothing was silently refused, at the CALL level: PASS

Eight `build_batch` calls reported `placed` 4 + 1 + 1 + 3 + 3 + 1 + 3 + 65 = **81**, exactly the
81 build ops, with **`failed: []` on every one**. Terrain: 32 + 32 + 48 = **112 cells changed**,
"0 already correct". Roof: **180 cells across 1 op**. No 6×6-took-11-cells behaviour.

## Criterion 4 — the plan and the map DISAGREE on 3 of 81 things: FAIL

Every planned cell re-read out of the engine with `rimworld/get_cells_info`:

```
terrain planned 112 | mismatched   0
roof    planned 180 | roofed now 180
things  planned  81 | missing/wrong 3
   (176,172) want DiningChair  got Table1x2c
   (181,171) want Shelf        got (nothing)
   (182,171) want Shelf        got (nothing)
```

🔑 **All three are one bug: the template treats multi-cell buildings as 1×1.**
Read back cell by cell, `Table1x2c` occupies (176,171)+(176,172) — so the chair the plan puts at
(176,172) is inside the table's own footprint. `Shelf` occupies two cells, so shelves compiled at
181, 182 and 183 overlap: 183 survives holding (183,171)+(184,171) and the first two are gone.

🔴 **And `jawa/build_batch` reported `placed` for every one of them.** The chair reported placed
and was then destroyed by the table; two shelves reported placed and were destroyed by the third.
⇒ **A later op in the same run silently destroys an earlier building and both report success.**
That is a new entry in the silent-failure catalogue, separate from the template's own defect.
Filed as `TEMPLATE_FOOTPRINT_IGNORES_SIZE_1` and `BUILD_BATCH_OVERWRITES_SILENTLY_1`.

## Criteria 1 and 2 — UNMEASURED, no instrument

**1. Room roles.** No bridge tool reads `Room.Role`. `rimworld/get_cell_info` returns terrain,
roof, fog, walkability, zone, areas, designations and things — and **no room object at all**.
Checked the full 246-tool list for `room`: nothing.

**2. Shell holds temperature.** No tool reads a room's temperature either, and the map is paused
at `ticksGame 1174` so no time has passed for a shell to hold anything.

⛔ Neither is passed. Filed as `ROOM_ROLE_AND_TEMP_HAVE_NO_TOOL_1`, the same class of gap as
`PAWN_STAT_READ_HAS_NO_TOOL_1`.

## Noted and NOT stopped for, as the item instructed

The palette is placeholder — the hut is built from `WoodLog`, spec §11 open decision #1. It built.
