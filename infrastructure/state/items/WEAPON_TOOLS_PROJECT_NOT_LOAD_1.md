## spec
Split off `DUMP_READERS_USE_THE_DB_1` after the measurement below contradicted its
premise. Evidence:
`observed/build/DUMP_READERS_USE_THE_DB_1_2026-08-21.md`.

🔴 **These two must NOT be ported the way the other three were.** Measured
2026-08-21 against `OFFICIAL-2026-08-21`: `db.records('ThingDef')` costs
**10.88 s / 1347 MB** where `json.load` of `defs/ThingDef.json` costs
**3.17 s / 1497 MB** — same 24,904 records. Both parse the same ~316 MB of JSON
text and the db adds a per-row trip to reach it. A loader that wants whole
RECORDS is right to read the file; the db wins on **projections and joins**, not
on graph loads.

  `src/RimMandrake/Utils/weapon_tag_audit.py:124  load_dump()`
      builds `tag -> {all, kept}` from every ThingDef. **That index alone is a
      join** — `def_tags` answers it at **0.18 s / 23 MB**, measured:
        SELECT t.tag, d.def_name FROM def_tags t JOIN defs d ON d.id=t.def_id
        WHERE t.kind='weaponTags' AND d.def_type='ThingDef'    -> 390 tags, 1901 pairs
      ⚠️ But `neutered`, `disarmed` and `eligible()` all still walk the records:
      `eligible()` reads `techLevel`, `weaponClasses` and `ingestible` per def.
      So the tag index can move and the record loop cannot — and a tool reading
      two sources for one answer is worse than one reading the slow source.
      ⇒ Either move BOTH (projection + `json_extract` for those three fields) or
      move NEITHER. Do not leave it half-ported.
  `src/RimMandrake/Utils/weapon_affordability.py:171  load_weapons()`
      `base_market_value()` RECURSES through `costList` and `stuff`, so it needs
      the whole ThingDef index in memory. A projection has to carry the cost
      graph or the recursion cannot run.

🔑 **This is a rewrite of what these tools ASK, not a port of how they read.**
That is why it is a separate item: `DUMP_READERS_USE_THE_DB_1`'s verify was
"byte-identical output", and this one cannot promise that until it is proven.

⛔ Do not reach for `def_flags.IsWeapon` as a shortcut for `eligible()` without
filing it as its own decision. It is the engine's own computed classification
and almost certainly BETTER than the tool's hand-rolled heuristic — which is
exactly why swapping it in silently would change what the audit measures.

## verify
both tools run before and after against the same capture, producing
byte-identical stdout, plus wall-clock and peak RSS for each. If output is not
identical, every differing line attributed to a named cause — the standard the
parent item's evidence file set.

## criteria
neither tool loads `defs/ThingDef.json` whole, both still run on a machine with
no `measuring-large-artifacts` and no `defs.sqlite`, and `weapon_tag_audit`'s
"emptied by the cut" line still says what a dump alone can and cannot attribute.

## notes
Filed by BUILD 2026-08-21. Not urgent: neither tool is broken, and the parent
item measured that a port would make them 3.4× slower.

## ✅ CLOSED 2026-08-22 by BUILD — at `18d98d66`

Evidence: `infrastructure/state/evidence/weapon_tools_projection_2026-08-22_BUILD.md`.

| tool | before | after (db) | after (no db) |
|---|---|---|---|
| `weapon_tag_audit.py` | 3.54 s · 1502 MB | **2.45 s · 30 MB** | 4.30 s · 1503 MB |
| `weapon_affordability.py` | 2.74 s · 1501 MB | **0.98 s · 47 MB** | 3.09 s · 1502 MB |

**stdout byte-identical on every path.** All three criteria met; see the evidence
file's last section for each, checked one by one.

## 🔴 THE SPEC ABOVE IS HALF WRONG AND THE HALF THAT IS WRONG IS THE USEFUL ONE

*"the db wins on projections and joins"* — the **joins** half is right and the
`def_tags` number in the spec (0.18 s) holds. The **projections** half is false as
written: `json_extract` re-parses each row's JSON, so projecting one field off
every ThingDef measures **6.7 s** against `json.load`'s 3.2 s. Memory collapses
90×; the clock gets worse. A projection only wins when the query never touches
most rows.

⇒ The spec's instruction *"move BOTH (projection + `json_extract` for those three
fields) or move NEITHER"* would, taken literally, have made `weapon_tag_audit`
**slower**. What worked instead: `def_flags.weapon` is an indexed predicate that
drops 24,133 of 24,904 rows before any JSON is parsed, and 0 defs carry a
non-empty `weaponClasses` without that flag — measured, and written into the
docstring so it can be re-measured rather than trusted.

⇒ And `weapon_affordability`'s cost recursion — the one the spec said *"has to
carry the cost graph or the recursion cannot run"* — did not need the graph. It
needed a **by-name lazy index**: the recursion reaches a few hundred defs, not
24,904. Projecting all of them measured 7.3 s; fetching on the cache miss measures
0.98 s end to end.

⛔ `def_flags.IsWeapon` was NOT swapped in for `eligible()`, per the spec's own
prohibition. The flag is used only to decide **which rows to read**, never to
decide whether a def is eligible — `eligible()` is byte-for-byte the function it
was, which is what makes the identical output meaningful.

⚠️ **One cost, paid only where there is no db.** The first port made that machine
worse — three questions meant three `json.load`s of the same 316 MB file, 7.9 s
against the original 3.5 s. `_load_json_defs` now memoises, bringing it to 4.30 s,
still ~20% above the original because the ported code asks a third question the
old code answered inline.
