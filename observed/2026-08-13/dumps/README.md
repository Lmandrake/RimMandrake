# `observed/2026-08-13/dumps/` — the def dump's provenance, kept; its bulk, discarded

**What is here:** one `manifest.<modCount>.<date>.json` per game load, ~144 KB
each, plus the script that captures them.

**What is deliberately NOT here:** the dump itself. It is ~1.3 GB across 531
files and `ThingDef.json` alone is **817 MB** — past GitHub's 100 MB per-file
hard limit. Because a push carries every seat's commits, committing it would
hard-fail the push for **all four agents** and stay failed until it was rewritten
out of history.

## The test that separates the two

> **Could a machine regenerate this without a human decision?**

The dump: **yes** — reproducing it is exactly what a game load does. Losing it
costs a rerun (~23 min), not a recreation. It stays local.

`manifest.json`: **no.** It is the only record of what the game *actually
loaded* — every mod's load order, packageId and `rootDir`, plus per-def-type
counts. **The next load overwrites it**, and at that moment the previous stack
becomes permanently unanswerable. So it is committed.

## Why it is worth the 144 KB

The manifest's `modCount` is the gate that **holds** when a timestamp check
silently passes. `src/RimMandrake/Utils/harvest_log.py` compares it against `ModsConfig.xml`
because mtime alone will happily green-light a 10%-loaded log — the game goes
quiet for minutes mid-load and keeps writing at the main menu, so "newer" and
"still growing" are both satisfied by a run that loaded almost nothing. An
undercount then prints as *better* than baseline.

A committed manifest also answers, months later, questions no other file can:
which mods were live for a given run, in what order, and how many defs of each
type they produced.

## Use

```bash
python3 observed/2026-08-13/dumps/capture_manifest.py --check   # report, write nothing
python3 observed/2026-08-13/dumps/capture_manifest.py           # capture, then commit and push
```

Run it **after every load**, before anything overwrites the dump. It finds the
DefDump under both the Windows and the WSL spelling of the same directory, and
refuses to overwrite an existing capture whose size differs rather than silently
replacing it.

⚠️ **Arm the dump before the load or there is nothing to capture** — the request
file is consumed at startup:

```bash
echo all > "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/dump_request.txt"
```
