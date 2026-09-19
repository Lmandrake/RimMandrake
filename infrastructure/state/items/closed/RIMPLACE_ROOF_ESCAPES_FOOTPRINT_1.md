# RIMPLACE_ROOF_ESCAPES_FOOTPRINT_1 — ctx:roof escaped the template's own rect, roof_rect always reported success

Thin item (no spec/verify/criteria filed). Decided the scope myself: `ctx:floor`
already refuses a cell outside `self.rect`; `ctx:roof` had no such check and
`ctx:roof_rect` returned a bare `True` regardless of what happened per-cell —
the two roofing primitives silently diverged from the floor primitives they
sit next to in the same file.

## Fix (`src/RimMandrake/Utils/rimplace/luaenv.py`, `Ctx.roof` / `Ctx.roof_rect`)

- `roof(x, z, defName=None)` now checks `self.rect.contains(x, z)` first and
  calls `self.plan.refuse("roof", "outside the footprint", x, z)` + returns
  `False` when it fails, mirroring `floor()` exactly.
- `roof_rect` now counts actual successes (mirroring `floor_rect`) instead of
  an unconditional `return True`.

`ctx:room()` calls `self.roof`/`self.floor` directly per-cell over a rect
built from its own `x,z,w,h` args — no template in `design/Jawa/templates/`
calls `roof`/`roof_rect` directly (checked: zero hits), so this only tightens
behaviour nothing currently depends on being loose.

## Verify — done by hand

- `python3 -m rimplace selftest` (`~/.local/venvs/rimlua/bin/python`):
  36/36, no regression.
- A scratch template calling `ctx:roof(rect.x2+5, rect.z2+5)` (outside the
  declared footprint) returned `false`, and a `ctx:roof_rect` call fully
  outside the rect returned `0` — both silent-success paths are now honest.

## criteria — met

`ctx:roof` cannot roof outside the template's own rect, and `roof_rect`'s
return value reflects what actually happened.
