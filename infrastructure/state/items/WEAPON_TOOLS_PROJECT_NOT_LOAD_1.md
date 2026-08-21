## spec
Split off `DUMP_READERS_USE_THE_DB_1` after the measurement below contradicted its
premise. Evidence:
`infrastructure/state/observed/build/DUMP_READERS_USE_THE_DB_1_2026-08-21.md`.

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
