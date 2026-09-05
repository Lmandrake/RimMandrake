## spec
Found verifying `INHABITED_AUGMENTATION_BUILD_1`'s pilot (commit `ade756fc`,
`design/Jawa/templates/mining_site.lua`). The pilot's own report claimed
"Lint: mining site 0 findings across 12 seeds/rock sides" — a wider sweep
(all 4 `rock_side` values × 12 seeds) found real, reproducible
`footprint-collision`/`room-not-sealed` lint ERRORs at several
seed/rock_side combinations:

```
seed=1 rock=E -> Wall: footprint overlaps ChunkSandstone at (6,3)
seed=1 rock=W -> Wall: footprint overlaps ChunkSandstone at (25,2)
seed=2 rock=W -> Wall: footprint overlaps ChunkSandstone at (25,0)
seed=11 rock=W -> Wall: footprint overlaps ChunkSandstone at (25,2)
seed=23 rock=E -> Wall: footprint overlaps ChunkSandstone at (6,1)
seed=23 rock=W -> Wall: footprint overlaps ChunkSandstone at (25,3)
```

(Reproduce: `~/.local/venvs/rimlua/bin/python -m rimplace lint mining_site
--rect "0,0,32,24" --tech Industrial --param rock_side=<E|W> --seed <N>`
from `src/RimMandrake/Utils/`.)

One specific instance of this class (rock_side=N, seeds 0-1, collision
against the tool-shed's own wall) was found, root-caused and fixed in
`bba9dde9`: the ore-yard heap's `clump()` scatter had no vertical buffer
against the shed's fixed rect. That fix does NOT close the class — the E/W
failures above collide against DIFFERENT fixed elements (most likely the
mining cars, ore dresser, or mud carriage, given the coordinates cluster
near `dresser_u=14`/the rail column/the frame's rotated edges) and are
unaffected by the shed-specific buffer.

## root cause (established, not fixed)
`clump()` (private helper in `mining_site.lua`) scatters chunks by checking
only `in_rect(cx, cz, within)` (stays inside the whole footprint) and
`try_def(...)` (does the exact cell resolve/place at the moment it's
called) — it has NO knowledge of other elements the template places
elsewhere in `build()`, whether placed before OR after the heap loop runs.
A chunk placed early into a cell that's empty AT THAT MOMENT can still be
overwritten by a wall/machine/vehicle `shell()`/`place_local()` call later
in the same `build()` run, and neither side checks the other.

## criteria
- General fix, not another one-off coordinate nudge: either (a) reorder
  `build()` so every fixed-position element (shed, dresser, cars, mud
  carriage, bunk) is placed BEFORE the ore-yard heap scatter, and make
  `clump()` check `not ctx:occupied(cx, cz)` before calling `try_def`, so
  heaps always yield to whatever's already there; or (b) compute an
  explicit exclusion-rect list from those fixed elements' known positions
  and pass it into the heap-anchor picker so a heap can never be centered
  close enough to reach one, whichever the current template structure makes
  cleaner — read the whole file (430 lines) before choosing, this
  assessment is from a partial read.
- Lint clean across all 4 `rock_side` values × at least 20 distinct seeds
  (not just the pilot's own shipped seed=5/rock_side=N config) before
  closing.
- Re-export `Templates/mining_site.txt` at whatever seed/params actually
  ship, after the fix.
