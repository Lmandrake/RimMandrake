# RIMPLACE_LUA_EXECUTION_BUDGET_1 — a template can loop forever and wedge the tool

## Fix

`_sandboxed_runtime()` in `src/RimMandrake/Utils/rimplace/luaenv.py` now installs
a `debug.sethook` instruction-count hook — 5,000,000 instructions — before
`_SANDBOX_PRELUDE` nils `debug` out of `_G`. The hook is a Lua closure that
calls `error(...)`, not a Python callback: `debug.sethook` requires a real
Lua function (`LUA_TFUNCTION`), and lupa exposes a Python callable to Lua as
userdata with a `__call` metamethod, which fails that check with `"function
expected, got POBJECT"` (confirmed by hand before settling on this shape).
Because `sethook` is a VM-level registration rather than a name in the
global table, nilling `debug` afterward stops a template from reaching
`debug.sethook` itself without touching the hook already installed.

5,000,000 instructions trips a runaway loop in ~10-20ms and does not touch
any real workload — the largest measured legitimate build (a 500x500 nested
loop, far bigger than any template's actual footprint) finishes in ~2ms.

## Verify — all done by hand, not just read

- `debug.sethook(function() error("...") end, "", 5000000)` (mask `""`,
  count-only) tripped a `while true do end` chunk in 0.010s, in an isolated
  lupa/Lua 5.5 runtime, before touching `luaenv.py` at all.
- After the edit: a template with `while true do end` in `min_rect(params)`
  failed via `rimplace minrect <template>` — `min_rect() raised: ... exceeded
  5000000 Lua instructions ...` — naming the template, exit 0 (a reported
  error, not a hang).
- A template with `while true do end` in `build(ctx)` failed the same way via
  `rimplace render <template>` — `build() raised: ... exceeded 5000000 Lua
  instructions ...` — exit 1.
- `python3 -m rimplace selftest` (via `~/.local/venvs/rimlua/bin/python`):
  **36/36 passed** (the file's docstring said 34/34 as of 2026-09-02; the
  suite has since grown to 36 — no regression either way).

## criteria — met

No template can make a rimplace command run forever; the failure names which
template did it and arrives in well under a second.
