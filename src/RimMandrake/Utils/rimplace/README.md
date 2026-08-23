# rimplace — run a Lua structure template offline and see the house

**Owner, 2026-08-22:** *"we will need something like lua for rapid prototyping and
debugging without constant game reloads."*

That is exactly what this is. A template is a `.lua` file; changing it and seeing the new
house is **one command and a few milliseconds** — no build, no deploy, no game.

## Setup (once)

```bash
python3 -m venv ~/.local/venvs/rimlua
~/.local/venvs/rimlua/bin/pip install lupa
```

## Use

```bash
cd /mnt/d/Luke/dev/Rimworld/src/RimMandrake/Utils
P=~/.local/venvs/rimlua/bin/python

$P -m rimplace render  dwelling --rect 0,0,18,10 --rooms 3 --occupants 4
$P -m rimplace lint    dwelling --rect 0,0,18,10 --rooms 3
$P -m rimplace calls   dwelling --rect 0,0,18,10          # the jawa/* calls it would make
$P -m rimplace verify  dwelling                           # every defName vs the live dump
$P -m rimplace selftest
```

## What it is

```
  design/Jawa/templates/*.lua  ──►  BuildPlan (pure data)  ──►  jawa/* bridge calls
        the author's file            lintable, diffable,          grouped by stuff,
                                     renderable, no game          map_commit last
```

| file | what it owns |
|---|---|
| `core.py` | the `BuildPlan` IR, `Rect`, the seeded RNG, the `Palette` |
| `luaenv.py` | the Lua runtime, **the sandbox**, and the `ctx` API templates call |
| `plan.py` | `lint()`, `render()`, `compile_calls()` |
| `cli.py` | the five commands |
| `palette.json` | role → defName. 🔴 **UNVERIFIED until `verify` says otherwise** |
| `selftest.py` | 23 cases, over half of them **negative controls** |

## Three properties worth knowing

🔴 **It refuses to trust its own palette.** `verify` checks every defName against the live
def dump (`DefDump/defs.sqlite`), validating its query shape against a known answer first.
If the dump is unreadable it reports **UNMEASURED** — never a pass.

🔴 **The sandbox is real.** `os`, `io`, `require`, `dofile`, `loadfile`, `load` and friends
are removed before a template runs, and three selftest cases prove it. Templates are data,
and data we might one day ship.

🔴 **Every check has a negative control.** A linter that cannot fail is worse than none,
because it reads like a pass. `selftest` asserts each check FIRES on a plan built to break it.

## The API a template gets

```lua
function build(ctx)
  ctx:room("Bedroom", x, z, w, h)     -- declares, floors and roofs a room
  ctx:wall_rect(x, z, w, h)           -- perimeter walls (NEVER roofs - see below)
  ctx:door(x, z)                      -- replaces the wall in that cell
  ctx:wall_mount("COOLER", x, z)      -- a cooler/vent sits IN the wall, like a door
  ctx:place_role("BED", x, z)         -- palette-resolved
  ctx:place("Wall", x, z, rot, stuff) -- explicit defName
  ctx:has_role("BED")                 -- branch on what this faction actually has
  ctx:occupied(x, z)                  -- do not stack furniture
  ctx:refuse(what, why)               -- a refusal is a RESULT, not a failure
  note("...")                         -- goes into the plan for a human to read
  rng.int(a,b) / rng.chance(p)        -- seeded: same seed, same house
end
```

⚠️ **`wall_rect` deliberately does not roof.** `jawa/build_batch` says it outright: *WALLS
CREATE NO ROOF*. `ctx:room()` roofs; walls alone do not.
