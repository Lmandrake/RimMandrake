# NEXT_LOAD_LOG_HARVEST_1
Everything the next Player.log must be asked, in one pass

Created by CHECK 2026-08-21 to absorb three items that each wanted the SAME artifact —
one `Player.log` from one load — and each of which would otherwise have parked
separately waiting for it.

## spec

🔑 **These are log GREPS, not interactions.** Nothing here needs the bridge, a map, or a
pawn. They need a load to have happened and its log to be unmined, which is exactly what
`needs: harvest` means. Filing them apart made three items look like three loads.

**Absorbed, with every original clause carried — a merge that loses a criterion is a cut
wearing a merge's name:**

| absorbed | what its log line must show |
|---|---|
| `B59` (the MegafaunaYield fix) | Megafauna butcher yields are the intended ones, AND the ~50 patch operations sequenced after the previously-aborted one apply again |
| `PRELOAD_PREDICTIONS_578_1` | JawaBench and Inhabited each print their init line; a failure is attributable to the right assembly rather than to "the load broke" |
| `BIOMESKIT_SNOWY_DESERT_TEXTURES_1` | the 148 missing-texture errors are ReGrowth's absent snow variants, NOT damage our repaint caused |

⚠️ **`RT_PROBE_LOAD_ABORTS_ON_578_1` is NOT absorbed and must not be.** It is also
`needs: harvest`, but it is a live blocker with its own fail run on the record, and
folding a blocker into a routine harvest is how a blocker stops being visible.

⛔ **Do not add "and also check…" to this item at collection time.** It is a fixed list
written before the load. An item that grows while the log is being read is an item whose
criteria were chosen after seeing the answer.

## verify

One pass over the newest `Player.log` after the next load, recording the three readings
above together. Harvest the whole log at once — `skills/rimworld-load-round`.

## criteria

- ✅ **PASS** when all three readings are recorded with their actual log lines quoted.
- ❌ **FAIL** if any one of the three cannot be answered from the log — that is a real
  answer about that clause, not a reason to defer the item.
- ⛔ **NOT in scope:** fixing anything the log reveals. A finding here spawns work; it
  does not reopen this item.
