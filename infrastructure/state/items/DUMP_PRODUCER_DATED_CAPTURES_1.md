## spec
The producer half of `DUMP_STORAGE_LAYOUT_RULING_1`. Owner, 2026-08-21 13:24:
*"Option (a) all the way. Keep last three."*

🔴 **DO NOT START THIS UNTIL THE ARMED CAPTURE HAS LANDED.** `RimDefDump.dll`
(`d7cf154`, the filename-collision fix) is deployed and `dump_request.txt` holds
`all`, so the **next cold load** writes the first capture with no collisions and
closes the 824-def hole. Replacing a proven binary with an unproven one before
that burns the capture everyone is waiting for. **Clean capture first; this on
the load after.**

### The layout
```
DefDump/
  captures/2026-08-21T08-20-20Z/   manifest.json  defs/  animals.json
  captures/2026-08-22T09-11-02Z/   …
  defs.sqlite                      derived; stays at the ROOT, outside any capture
```
⛔ **No `current` or `official` symlink, and this is measured, not a preference.**
A symlink WSL creates under `LocalLow` succeeds from bash and is **unreadable
from Windows** — `Mode d----l`, empty `LinkType`, `PathNotFound` through it — so
the game could never follow one. See `BUILDABLE.md`. The ids are ISO-8601 with
fixed-width fields, so:
- **current** = `max(dirname)`, a plain lexicographic sort that C# and Python
  agree on for free
- **official** = whatever `dumps/REGISTRY.jsonl` freezes

⇒ **Nothing to desync, because there is no pointer.**

### What changes in `src/RimMandrake/RimDefDump/Source/DefDumper.cs`
1. Write into `DefDump/captures/<capturedUtc with ':' -> '-'>/` instead of
   `DefDump/`. The id must be **exactly** `^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z$`
   — `game_paths.captures()` ignores anything else, deliberately, so a partial
   write cannot masquerade as a capture.
2. ⚠️ **Write to a scratch name and rename on completion.** A capture that
   crashed half-way must not be visible as a capture: `captures/.writing/` then
   `Directory.Move` to the id. Rename is atomic on NTFS; a half-written directory
   under the real id is exactly the "0 means measured zero" failure in a new form.
3. **Retention: keep the newest THREE, delete the rest** — after the rename, so
   a failed capture never costs an old one.
4. 🔴 **NEVER delete a capture containing `.keep`.** `refresh.py --freeze --by
   owner` writes that marker into the frozen capture. It is the whole contract
   between retention and the freeze, and it means the game needs no knowledge of
   this repo or its registry. A frozen capture does not count against the three.

### The migration, once the producer is deployed
Move the existing flat capture into `captures/<its capturedUtc>/`, leave
`defs.sqlite` at the root, and re-point `REGISTRY.jsonl`'s frozen entry with a
`capture` field. ⚠️ `refresh.freeze()` already writes that field when the dump
path it is given IS a capture directory — verified by
`selftest_frozen_dumps.t_a_freeze_of_a_dated_capture_records_which_one`.

### Already done and NOT to be redone
`game_paths.DEF_DUMP` already resolves the newest dated capture when `captures/`
exists and falls back to flat `DefDump/` when it does not (`f5592eb`), so **every
reader already works on both layouts** and there is no flag day. `captures()`,
`newest_capture()` and `KEEP_MARKER` are there; six tests cover them.

## verify
1. Two consecutive captures on a quicktest load: the first is left
   **byte-identical** on disk and both appear under `captures/`.
2. `python3 src/RimMandrake/Utils/game_paths.py` names the newer one as
   `current capture`.
3. A fourth capture prunes the oldest — unless it carries `.keep`, which must
   survive with a fifth.
4. `python3 src/RimMandrake/Utils/selftest_frozen_dumps.py` still passes, and
   `measure build` + `measure count AbilityDef` answer off the new layout.
5. A capture killed mid-write leaves nothing that `captures()` will return.

## criteria
A new capture cannot overwrite or delete the frozen one, `defs/` cannot inherit
a file from a previous capture, and no reader needed changing to cope with either.

## notes
Filed by BUILD 2026-08-21 immediately after the owner's ruling, so the sequencing
survives a context loss: the armed capture comes FIRST.

## BUILT, DEPLOYED AND MIGRATED 2026-08-22 — `b9d3e8b0`. Verification is on the load.

**The precondition was checked, not assumed.** The item said do not start until the armed
capture had landed. It has: `captures/2026-08-21T22-44-59Z/manifest.json` carries
`defTypeCollisions` **resolved into separate files** (`AbilityDef.json` 612 *and*
`VEF.Abilities.AbilityDef.json` 18), 533 types, 78,813 defs, mode `all` — that is the
`d7cf154` fix having run.

### Done
- `DefDumper.cs` writes `captures/.writing/`, then an atomic `Directory.Move` to
  `captures/<capturedUtc with ':' -> '-'>/`. Retention keeps the newest three and skips
  any capture holding `.keep`, and runs AFTER the rename so a failed publish never costs
  an old capture. A leftover `.writing` from a dead run is cleared on the next attempt.
- ⚠️ **A latent bug fixed on the way:** `capturedUtc` was a separate `DateTime.UtcNow` in
  the manifest writer and in the animals writer, so they could disagree by seconds. It is
  now stamped once and used for the id, the manifest and `animals.json` alike — the id has
  to equal the manifest's own value or a reader cannot join them.
- The live dump is migrated. `defs.sqlite` stays at the root; the frozen OFFICIAL capture
  carries `.keep`; the registry entry names its `capture`.

### 🔴 Four readers broke on the migration and are fixed with it
| reader | what it did |
|---|---|
| `refresh.frozen_entry` | matched only the dump ROOT, so the migrated dump read as **NOT FROZEN** — it would have demanded a ~23-minute load for nothing. Two regression tests added, and an entry naming a capture still refuses to cover a different one. |
| `dump_projection` · `xenotype_size_audit` | looked for `defs.sqlite` beside the path they were handed, which under `captures/<id>` does not exist and never will |
| `measure build` · `measure verify` (the SKILL, `347295b`) | read `manifest.json` from the root. `split_capture_layout()` now returns `(root, source)`; a flat dump returns the same path twice, so there is no flag day. |
| `measure verify` collision keying (the SKILL) | keyed on the SIMPLE type name, so it asked whether `AbilityDef.json` alone held all 630 AbilityDefs in the db. Reported **22** false disagreements. Now keyed on `capture.source_file` → `full_name`. |

`selftest_frozen_dumps` **32/32**. The skill's own suite went 44/46 with two hard
`FileNotFoundError`s to 45/46 with the layout fix.

### Verified offline
2. ✅ `game_paths.py` names the capture as `current capture`.
4. ✅ selftests pass; `measure count RimWorld.AbilityDef` = 612 off the new layout.
5. ✅ A `captures/.writing/` directory is invisible to `captures()` — tested directly.

### ⏳ NOT verified, and cannot be without a load
1. Two consecutive captures, the first left byte-identical.
3. A fourth capture prunes the oldest — and does NOT prune the one carrying `.keep`.

🔴 **The producer has never run.** Re-gated to `harvest`; the run sheet's first block is
the checklist, and `[RimDefDump] capture published:` is the line that decides whether a
capture happened at all.
