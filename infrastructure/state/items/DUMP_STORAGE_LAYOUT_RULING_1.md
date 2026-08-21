## spec
🔴 **This is the ruling the 2026-08-21 work stop is waiting on.** The owner said
*"we are changing how we store and access dump files"* and *"BUILD is on it"*.
The **access** half is done and needs nothing from him. The **storage** half is
one decision, below.

### What is actually wrong, measured 2026-08-21

🔴 **1. A capture overwrites the previous one in place, so a freeze cannot hold.**
`DefDumper.cs` writes to one fixed directory —
`Path.Combine(GenFilePaths.SaveDataFolderPath, "DefDump")` — never dated, never
versioned, never cleaned. Both `REGISTRY.jsonl` entries name **the same path**,
so `OFFICIAL-2026-08-20` **no longer exists on disk**; the 08-21 capture wrote
over it. ⇒ *"Frozen means do not re-capture over this"* is a rule the storage
layout cannot enforce, and did not.

🔴 **2. `defs/` accumulates and nothing prunes it.** 536 files, of which **19 are
dated 2026-08-10…15** from captures whose mods are long uninstalled. Any reader
that walks the directory ingests them: measured, that put **154 dead defNames**
into two index builders, so a reference to a REMOVED def graded as PROVIDED —
fail-toward-success. Fixed in those two readers by going through `defs.sqlite`,
which excludes orphans by construction; **not** fixed for anything that still
walks the directory.

⚠️ **3. The derived db lives inside the frozen path.** `defs.sqlite` is 734 MB
and `dumps/README.md` already rules it explicitly outside the freeze — but it
sits inside the frozen directory, so "the freeze covers this folder" and "the
freeze covers the capture" are two readings of one layout.

### The choice

**(a) IMMUTABLE DATED CAPTURES — BUILD recommends this.**
```
DefDump/
  captures/2026-08-21T08-20-20Z/    manifest.json  defs/  animals.json
  current   -> captures/<newest>              what the producer just wrote
  official  -> captures/<frozen>              the design target; only he moves it
  db/<capture-id>.sqlite                      derived, outside the freeze
```
Kills all three at once: a new capture cannot overwrite an old one, a fresh
directory cannot inherit 19 stragglers, and the derived db is outside by
position rather than by a paragraph. Costs a `DefDumper.cs` change, a build and
a deploy.

**(b) KEEP ONE LIVE DIRECTORY**, and accept that the freeze is a note about a
capture that may already be gone. Cheaper today; the failure it permits has
already happened once and was found by accident.

🔴 **SEQUENCING, AND THIS IS THE PART TO GET RIGHT WHATEVER HE PICKS.**
`RimDefDump.dll` (`d7cf154`, the collision fix) is **deployed and armed** —
`DefDump/dump_request.txt` holds `all`, so the next cold load writes the first
capture with no filename collisions and closes the 824-def hole. ⛔ **Do not
touch `DefDumper.cs` before that load.** Replacing a proven binary with an
unproven one burns the capture everyone is waiting for. **Take the clean capture
first; restructure on the load after it.**

### Already done, and it does not depend on this ruling
- `DUMP_PATH_ONE_SEAM_1` — 34 literals across 21 files now resolve through
  `game_paths.py`, with `selftest_one_path_seam.py` holding it there. **A layout
  change is now a one-file change**, which is why it went first.
- `DUMP_READERS_USE_THE_DB_1` — three readers moved to `defs.sqlite`; two
  measured better off on JSON and were left alone.
- `FREEZE_SHA_UNREPRODUCIBLE_1` — `refresh.py --freeze --by owner` exists, and
  the sha it writes is recomputable.

## verify
The owner picks (a) or (b). If (a), BUILD writes the layout change, and the
verify is that a second capture leaves the first byte-identical on disk and
`refresh.py` still finds the official one.

## criteria
Closed when the owner has ruled. ⛔ **No agent may pick for him** — this decides
where the design target lives, and a target that moves without a decision is the
failure `dumps/README.md` exists to prevent.

## notes
Filed by BUILD 2026-08-21 from a measured survey of the dump's on-disk shape and
all 40 of its consumers. Nothing here is urgent enough to justify guessing:
option (b) is the status quo, so a slow answer costs nothing but a fast wrong one
costs a capture.
