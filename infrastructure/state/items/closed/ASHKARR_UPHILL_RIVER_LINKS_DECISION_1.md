# ASHKARR_UPHILL_RIVER_LINKS_DECISION_1 — 🔴 one call from the owner (frozen planet)

Surfaced while diagnosing a failing selftest (`selftest_river_link_order.py`),
2026-09-03, BENCH. The selftest failure is NOT tonight's work and NOT the rename
migration — that was the first guess and it is wrong (verified: the migration
`aa759446` did not touch these rows; the Kiln edit `171aab4e` removed exactly one
unrelated line). What it actually surfaced is worth your eyes.

## the finding (verified, non-destructive — nothing repainted)

`world/ASHKARR_WORLDMAP_links.csv` was substantially rewritten **after** the
mouth-first order-test froze on 2026-08-21 (`6f96adfd`): three commits on
2026-08-22 — `2b0e9031` (+57 rows), `68aa7ef2` (236-row rewrite, "four independent
reviews… climate hiding a lookup table"), `20e492bf` (+46). The accepted file is
no longer a round-trip fixed-point of `ashkarr_paint.river_link_rows`, which is why
the test fails.

Checking the accepted rows against `tiles.csv` `elev_m` (downstream end `a` vs
upstream end `b`): **292 river rows — 253 run downhill (correct), 25 flat, 14 run
UPHILL.** Ten of the fourteen are ≤7 m (hex-averaged-elevation noise). **Four are
not:**

| def | downstream→upstream | climbs |
|---|---|---|
| LargeRiver | 14571 → 6470 | **304 m** |
| LargeRiver | 11334 → 675 | **294 m** |
| Creek | 3180 → 16645 | 273 m |
| HugeRiver | 8501 → 19400 | **254 m** |

A LargeRiver/HugeRiver whose mouth sits 254–304 m ABOVE its source is either a
genuine backwards link (the `89029b76` "links CSV was upside-down" failure mode,
recurred on these rows) or a legitimate case where authored drainage diverges from
raw hex elevation (a canyon/depression the painter routed deliberately). **I cannot
tell which without your eye — and I must not repaint to find out**, because
`RIVER_LINKS_EMITTED_BACKWARDS_1` names repainting the accepted planet an outright
FAIL.

## the call

- **DO** (2 min): look at the four segments above on `worldview.py` and rule
  keep-as-authored vs fix. If any are backwards, they are the real defect and the
  selftest was catching it.
- **DON'T** rerun `ashkarr_paint.py` to "correct" them — that repaints an accepted
  v1 planet (`canon.yml accepted_for_v1: true`) and is the exact FAIL condition of
  `RIVER_LINKS_EMITTED_BACKWARDS_1`. A backwards link is fixed by editing the four
  named rows in `links.csv` by hand, not by regenerating.

## after your ruling

`RIVER_LINK_ORDER_SELFTEST_DRIFT_1` (FOUNDRY) then resolves one of two ways:
either the accepted file is right and the order-test's frozen expectation is rebased
to the current file, or the four rows are fixed and the test passes again as-is.
Either path is a one-liner once you have ruled.

## verify
The four segments are eyeballed on the render and each is ruled keep or fix.

## criteria
No LargeRiver/HugeRiver on the shipped planet runs materially uphill unless you have
said it does so on purpose.

## ruling — owner, 2026-09-03: "Just accept the river item for now please."

**KEEP AS AUTHORED, all four segments.** Not backwards links, not a repaint
candidate. `world/ASHKARR_WORLDMAP_links.csv` stands as-is; none of the four
named rows (LargeRiver 14571→6470, LargeRiver 11334→675, Creek 3180→16645,
HugeRiver 8501→19400) get hand-edited.
