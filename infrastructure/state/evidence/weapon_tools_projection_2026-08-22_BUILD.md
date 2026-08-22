# weapon_affordability and weapon_tag_audit now project — WEAPON_TOOLS_PROJECT_NOT_LOAD_1

_Measured 2026-08-22 by BUILD against `DefDump` capture `9a204707f6dc183d`
(578 mods, game 1.6.4871 rev591, captured 2026-08-21T22:44:59Z). Every number
below is `/usr/bin/time -v` on this machine, same capture, back to back._

## THE RESULT

| tool | before | after, with `defs.sqlite` | after, no db (fallback) |
|---|---|---|---|
| `weapon_tag_audit.py` | 3.54 s · **1502 MB** | **2.45 s · 30 MB** | 4.30 s · 1503 MB |
| `weapon_affordability.py` | 2.74 s · **1501 MB** | **0.98 s · 47 MB** | 3.09 s · 1502 MB |

**stdout is byte-identical in all six runs.** `diff` reports no difference for
either tool, on either path — the one exception being the affordability tool's
first line, which echoes the `--dump` path it was given and therefore differs
when it is pointed at a different folder to force the fallback. Nothing else.

## 🔴 THE ITEM'S PREMISE WAS HALF RIGHT, AND THE HALF THAT WAS WRONG IS THE INTERESTING ONE

It said *"the db wins on projections and joins, not on graph loads."* The joins
half is right and bigger than it claimed. The projections half is **false as
stated**, and measuring it was most of the work:

```
json.load defs/ThingDef.json                       3.2 s   1500 MB
SELECT json_extract(json,'$.fields.techLevel') …   6.7 s     16 MB   <- SLOWER
the same with 3 json_extract columns               6.8 s     16 MB   <- no worse
```

⇒ **`json_extract` re-parses the whole row's JSON.** Asking the db for one field
of every row is twice as slow as reading the file: memory collapses by 90× and
the clock gets worse. A "projection" is only a win when the query never has to
touch most rows.

⛔ **And the multi-path form is a trap.** `json_extract(json,'$.a','$.b')` returns
one JSON array and looks like a single-parse win. SQLite **omits** missing paths
instead of yielding null, so the array's positions shift per row. Measured: it
reported **535** defs carrying `weaponTags` where the truth is **721**. Slower
and wrong.

## WHAT ACTUALLY WON, PER QUESTION

| question | shape | why it is cheap |
|---|---|---|
| `tag -> {all, kept}` over every ThingDef | `def_tags` join | pre-extracted and indexed; **no JSON parsed at all** |
| `eligible()` inputs | `json_extract` over the **771** `weapon`-flagged rows | an indexed predicate throws away 24,133 rows before any parsing |
| `ingestible` | `def_flags` | pre-extracted |
| `label` | `defs.label` | a plain column |
| which cut defs are neutered | `defs_by_name` over the ~200 cut names | the question was never about 24,904 defs |
| the market-value cost graph | `_LazyCostIndex`, fetch by name on the miss | the recursion reaches a few hundred defs, not all of them |

🔑 **`_LazyCostIndex` is the one that needed a new shape.** `base_market_value`
recurses through `costList` into arbitrary materials, so it cannot know its
working set in advance — which is exactly the "graph load" the item said would
not port. Projecting all 24,904 rows for it measured **7.3 s**. Fetching by name
on the cache miss measures **0.98 s** end to end, because the recursion only ever
asks for a few hundred names.

## 🔑 ONE MEASURED EQUIVALENCE THE RESTRICTION RESTS ON

`weapon_defs()` returns only defs the engine flags `weapon`. That is safe here
because **0 ThingDefs carry a non-empty `weaponClasses` without also being
flagged `weapon`** (771 are flagged), and every branch of `eligible()` requires a
non-empty `weaponClasses` — so a def outside the set could never have been
returned. ⚠️ **That is a measured fact about one capture, not a guarantee from the
engine.** The count is written into `dump_projection.weapon_defs`'s docstring so
the next reader can re-run it rather than trust it.

## THE FALLBACK, AND A REGRESSION IT NEARLY SHIPPED

`defs.sqlite` is built by `measuring-large-artifacts`, which lives outside this
repo, so a machine can have the dump and no db. Both tools fall back to the JSON
and produce identical output — proven above.

⚠️ **The first port made that machine WORSE.** Three questions meant three
`json.load`s of the same 316 MB file: **7.9 s** against the 3.5 s the tool cost
before being touched. `_load_json_defs` now memoises, which brings it to 4.30 s.
That is still ~20% above the original, because the ported code asks a third
question the old code answered inline; it is a real cost and it is paid only on
machines that have no db.

## CRITERIA, CHECKED

1. ✅ **Neither tool loads `defs/ThingDef.json` whole** — on the db path. On the
   fallback it does, because there is nothing else there to read.
2. ✅ **Both still run with no `measuring-large-artifacts` and no `defs.sqlite`**,
   byte-identical, measured by stubbing `sqlite_path` to `None`.
3. ✅ **`weapon_tag_audit`'s "emptied by the cut" line is untouched** — the
   `WEAPON_TAGS_MATCH_NOTHING_1` correction and its comment are unchanged, and
   byte-identical stdout proves the line still says what a dump can and cannot
   attribute.
