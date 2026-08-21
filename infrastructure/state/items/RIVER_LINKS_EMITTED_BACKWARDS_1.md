# RIVER_LINKS_EMITTED_BACKWARDS_1
`ashkarr_paint.py` emits river links by tile id, not mouth-first; the importer applies file order

Filed by CHECK, 2026-08-21, from an offline pre-flight of `world/ASHKARR_WORLDMAP_links.csv`.
The ARTIFACT is already corrected (`89029b7`); this item is about the PRODUCER, so a
future regeneration does not reintroduce it.

## spec

`src/RimMandrake/Utils/ashkarr_paint.py:988-991` writes the river links as:

```python
for t in np.nonzero(w["chan"])[0]:      # ← ascending TILE ID
    d = w["down"][t]
    ...
    wr.writerow(["river", int(t), int(d), ...])   # ← a = upstream, b = downhill
```

Two things are wrong for the only consumer that exists:

| what the producer does | what `jawa/world_links_import` requires |
|---|---|
| rows ordered by ascending tile id | *"rivers are applied **IN FILE ORDER** so the file must already be mouth-first"* |
| `a` = upstream, `b` = downstream | mouth first, then upstream — so `a` must be the **downstream** end |

🔴 **And it fails silently, which is the whole reason this is worth an item.**
`WorldGrid.OverlayRiver` sets `riverDist = max(riverDist, previous + 1)`. Applied in
tile-id order with the ends swapped, every one of the 238 river links still *lays* —
the importer refuses nothing, logs nothing, and `world_lint` has no rule for it. The
planet simply comes back with wrong `riverDist` on every river, which is the class of
failure `skills/rimbridge/references/traps.md` exists to catalogue.

**Measured before and after the corrective pass**, over the same 238 links:

| reading | before | after |
|---|---|---|
| rows running `a → b` uphill (mouth-first expects a majority) | **22 / 238** | **157 / 238** |
| river chains starting at a tile with no water on or beside it | 122 | 9, **all `Creek`** — legal |

The 9 are not defects: owner, 2026-08-17 — *"High-accumulation trunks MUST reach a sea;
low-accumulation rivers MAY die in playas / salt pans. So 'reaches no sea' is a defect
only above the trunk threshold — the linter must know which."* `lint_links.py` encodes
that: it checks the outlet on `LargeRiver`/`HugeRiver` only.

⛔ **Do NOT fix this by re-running `ashkarr_paint.py`.** `world/ASHKARR_WORLDMAP_tiles.csv`
is frozen (`.frozen.json` beside it) and the map was accepted for v1 on 2026-08-20
(`canon.yml: accepted_for_v1: true`, `977aa75`). Regenerating the bundle to fix a row
ordering would repaint an accepted planet. The corrective pass was written to change
**order and orientation only**, and that the SET of links is unchanged is proved, not
asserted — sorting both files' `(min(a,b), max(a,b), kind, def)` tuples gives byte
equality at 1,075 rows.

## verify

Offline, no game load.

1. `python3 src/RimMandrake/Utils/lint_links.py` — must print `PASS`.
2. Change `ashkarr_paint.py` to emit mouth-first, then confirm a freshly produced
   links CSV lints clean **without** `--fix`.
3. Prove the emitter change did not alter the link set, the same way: compare sorted
   `(min(a,b), max(a,b), kind, def)` tuples against `world/ASHKARR_WORLDMAP_links.csv`.

## criteria

- ✅ **PASS** when `ashkarr_paint.py` emits a links CSV that lints clean with no
  corrective pass, and the link set is provably identical to the accepted one.
- ❌ **FAIL** if the emitter is "fixed" by regenerating the bundle, or if the link set
  changes by even one row — that is a repaint of an accepted planet, not a bug fix.
- ⛔ **NOT in scope:** the road links. 837 of them, order-independent — `OverlayRoad`
  carries no distance accumulator, so file order does not affect them and they were
  left untouched.
