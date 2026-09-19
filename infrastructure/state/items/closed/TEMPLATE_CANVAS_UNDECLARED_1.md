# TEMPLATE_CANVAS_UNDECLARED_1 — a rimplace template's required canvas lives nowhere machine-readable

## Where this came from
`TILE_STRUCTURE_REVIEW_SAVE_1` (BENCH, 2026-09-02) found it live: 4 of 21
templates rendered nothing at a "default 16×12 canvas" because each needs
more room, and each only says so via a runtime `ctx:refuse()` message —
there is no place upstream of actually running the template where a caller
(a `TileMutatorDef` author, a re-export script, a review-sheet build) can
look up "how big does this footprint need to be" without either reading
every template's own Lua by hand or hitting the refusal empirically.

Confirmed this is not new to those 4: audited FOUNDRY's own 7 batch-4/5/6
templates (`bantha_graveyard`, `mynock_roost`, `glass_sea`, `monument`,
`dead_beacon`, `broken_ring`, `imperial_waystation`) — none had a
machine-readable minimum either, only whatever the author happened to test
at export time. Confirmed `GenStep_RimplacePlan.cs` itself is NOT at risk
for anything already wired: it replays the pre-exported flat `.txt` plan
(baked at whatever rect the author ran `rimplace export --rect ...` with),
it does not re-run the Lua at mapgen time, so an already-committed
`GenStepDef` is safe regardless of this gap. The risk is entirely upstream,
at export/re-export time, for a human or agent who doesn't know (or
forgets, or is a different person than the original author) what size a
given template actually needs.

**Interim mitigation already applied, not a fix**: added a `-- MIN_RECT:
WxH` (or `-- MIN_RECT: none - safe at any rect >=1x1`) line to the top of
all 7 FOUNDRY batch-4/5/6 templates, so at least those are grep-able by
eye. This does not make the number machine-readable to a script.

## spec
Pick and build ONE real mechanism (not a comment convention) for a template
to declare its own minimum canvas somewhere a caller can query WITHOUT
running `build()` and catching a refusal:

- **Option A — a `min_rect(params)` function convention**, mirroring
  `build(ctx)` itself: templates that need a size floor define it,
  `rimplace export`/`render`/`lint` call it first (if present) and warn/
  refuse BEFORE running `build()` on an undersized rect, rather than
  relying on the template's own internal `ctx:refuse()` (which still works
  but fires late, mid-build, after floor/prop placement may have already
  partially run).
- **Option B — a structured header this session's own MIN_RECT comment
  already gestures at**, parsed by a small script (`min_rect(template) ->
  (w,h) | None`) that greps for the convention and is called by whatever
  wires templates to GenStepDefs, so the number travels WITH the citation
  even without changing the Lua engine.
- Whichever is chosen, the **exported `.txt` plan itself is where the
  gap is invisible longest** — nothing in `RimplacePlan.Parse`/
  `GenStep_RimplacePlan.cs` records what rect it was exported at, so even
  a machine-readable Lua-side declaration doesn't help a THIRD party who
  only has the `.txt` file and is deciding whether to re-wire it onto a
  different-sized `TileMutatorDef` footprint. Consider whether the flat
  format's own header should carry the export rect it was baked at.

## verify
- Reproduce the exact failure this item is named for: run whatever the new
  mechanism is against `hunting_lodge`/`junkers_cantina_block`/
  `junkers_depot`/`junkers_scrapyard` at a too-small rect and confirm it is
  caught BEFORE `build()` runs, not just as a renamed version of the
  existing `ctx:refuse`.
- Confirm it does NOT regress the 4+ templates that are deliberately
  size-agnostic (this item's own FOUNDRY audit found `bantha_graveyard`/
  `mynock_roost`/`glass_sea`/`broken_ring` have no real minimum — a
  mechanism that forces every template to declare one would be a
  regression, not a fix).

## criteria
Whoever next wires a template to a `TileMutatorDef`/`GenStepDef`, or
re-exports one, can find its required canvas without reading the Lua
source or hitting a runtime refusal first.
