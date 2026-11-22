## spec
`visit_cited_items` (src/RimMandrake/rimflow/maturation.py) takes the items that a visit's failed lines name only from a
row's `filed` field. A driver also names an older item as a row's `owner` (the item that owns the repair). Pyrelands
visit 5 (2026-11-22): the `sc_grass_regreens` UNMEASURED row named RIMMANDRAKE_BUILD_PYRE_GRASS_FOIL_SAME_SEED_DENSITY_ONE
(filed 2026-11-21, caused by another item) only in `owner`. The road back cited the other two items and not that one,
so its fixer would not run and visit 6 would have launched with the bar `grass_carpets_and_regreens` still undecided by
construction. The visit-5 steward refiled that item under its road back by hand (4eca75fb66); this item is the
permanent fix: a failed row's `owner` is cited like its `filed`.

## verify
`python3 src/RimMandrake/rimflow/selftest_visit_wait_cited_items.py`

## criteria
- A failed row (verdict not PASS) that names a rimflow item in `owner` cites it; a PASS row's `owner` cites nothing.
- `filed` keeps its meaning; a name that is not a rimflow item name is ignored.

## Acceptance test
`python3 src/RimMandrake/rimflow/selftest_visit_wait_cited_items.py --only t_owner_named_item_is_cited`: red on the base
(the reader ignores `owner`), green on the fix; the whole selftest green.

## refs
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/selftest_visit_wait_cited_items.py
file: design/specs/2026-11-21-visit-wait-cited-items/boundary.md
