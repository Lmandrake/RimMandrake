# RIMPLACE_LUA_EXECUTION_BUDGET_1 — a template can loop forever and wedge the tool

Code review, 2026-09-02, on the `min_rect` work.

## spec

`src/RimMandrake/Utils/rimplace/luaenv.py` runs template Lua with no instruction
budget and no wall-clock limit. `function min_rect(params) while true do end end`
hangs, and `rimplace minrect all` executes EVERY template in
`design/Jawa/templates/`, so one bad file wedges the whole command with no output
and no indication which template did it.

This matters more than it looks because templates are DATA and the file's own
docstring promises they cannot harm the machine — a hang is a denial of service on
exactly the shared tooling that promise covers.

⚠️ The obvious lever is a `debug.sethook` instruction count, and `debug` is nil'd
inside the sandbox on purpose. Set the hook from the PYTHON side, before the
template chunk runs, so the template still cannot reach `debug` itself.

Related: the sandbox hole closed the same day (`python` was reachable via lupa's
builtins table, `102516c6`) — same file, same promise.

## verify
- A template with `while true do end` in `min_rect` and one in `build` both fail
  with a clear error naming the template, within a bounded time.
- `rimplace minrect all` still completes over the real library, and reports the
  offending template rather than dying silently.
- `rimplace selftest` still passes (34/34 as of 2026-09-02).

## criteria
No template can make a rimplace command run forever, and the failure names which
template did it.
