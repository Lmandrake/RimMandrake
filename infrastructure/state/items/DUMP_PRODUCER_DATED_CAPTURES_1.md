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
