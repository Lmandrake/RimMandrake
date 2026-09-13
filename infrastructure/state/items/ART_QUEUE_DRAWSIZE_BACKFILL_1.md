# ART_QUEUE_DRAWSIZE_BACKFILL_1 — drawsize onto every art target, then regate at true sizes

Filed by BENCH, 2026-09-13, out of the owner's question "are large animals
being given more pixels?" MEASURED state: the queue holds mixed canvases
(137×256², 177×512², few 384/320) chosen by wave-author judgment, but ZERO
jobs record drawSize — the canvas=drawSize×128 law and the gate's tier
scaling both now consume a `drawsize` field that old rows do not have.

## spec

Join every art target/queue row (art_status perTarget, pending/ rows, wave
queue CSVs) against the frozen dump's per-ThingDef `graphicData.drawSize`
(post-inheritance leaf; fall back to the mod XML where the dump lacks the
field — the dump drops some graphic fields). Write `drawsize` onto the rows
(fill_queue now stores it into jobs; artpiped passes it to the gate). Then
regate the 353-sprite backlog at true sizes (the tooling exists:
`art_legibility.py gate --drawsize`) and report how the pass/borderline/regen
split moves vs the 1-cell-blind split (153/16+5/179 on 2026-09-13).

## verify

Every row either has a dump-sourced drawsize or is explicitly listed as
UNRESOLVED with why (defName not in dump, decor with no def). Spot-check 5
known-large creatures (e.g. thermadon-class) flip band when regated. No row
gets a GUESSED drawsize — unresolved beats invented.

## Watch out

- The def dump drops whole fields (no statBases; some graphic fields) — where
  drawSize is absent, read the mod's own XML, and mark which source answered.
- drawSize can be a vector (x,y) — use the max dimension in cells.
- The fitted model was calibrated at 1-cell tiers; regated verdicts for large
  creatures are the principled approximation — flag any absurd flips for the
  owner rather than auto-accepting.
