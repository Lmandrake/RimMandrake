# TEMPLATE_RECT_PARAM_NOT_ACCEPTED_1 — rimplace compiles a parameter that does not exist

`rimplace calls` emits `{"rect": "171,171,4,8", "terrainDef": "Gravel"}` for
`jawa/set_terrain_batch`, and the same shape for `jawa/set_roof_batch`. **Neither tool has a
`rect` parameter.** Live schemas, read from the running bridge 2026-08-26:

```
jawa/set_terrain_batch  ['layer', 'ops', 'refresh', 'terrainDef']
jawa/set_roof_batch     ['ops', 'refresh', 'roofDef']
```

Measured, not assumed — on a spare cell:
`{"rect":"200,200,2,2","terrainDef":"Gravel"}` → `success: false`,
*"ops is required, e.g. 'Sand:10,20,3,4;Gravel:14,20,2,2'"*, terrain unchanged.
`{"ops":"Gravel:200,200,2,2"}` → `success: true`, *"4 cell(s) changed"*.

⇒ **4 of the dwelling's 13 compiled calls cannot execute**, taking all 112 terrain and 180 roof
cells with them. ✅ The bridge refuses loudly, so this never becomes a silent failure — but the
compiled call list is not runnable as shipped.

**Fix:** `compile_calls` must emit `ops` in the tool's own grammar — `'<Def>:x,z,w,h'`
joined by `;`. One rect becomes one op string; the tools already take w/h.
`src/RimMandrake/Utils/rimplace/plan.py`.

🔑 **Add a contract check to `rimplace selftest`**: for each compiled call, assert every emitted
key is in that tool's live `inputSchema`. 23/23 selftests passed with this defect present, which
means the selftest never compared against the bridge.

Evidence: `infrastructure/state/evidence/template_engine_acceptance_2026-08-26_CHECK.md`
