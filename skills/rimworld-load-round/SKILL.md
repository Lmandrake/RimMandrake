---
name: rimworld-load-round
description: How to spend a RimWorld cold load — the ~23–30 minute game restart that is the scarcest resource in this project. Arriving already confident instead of "restart and see", writing the Player.log strings that will decide each item before launching, batching by ambiguity, what ModsConfig.xml is and is not authoritative about, src/RimMandrake/Utils/refresh.py and whether a load is needed at all, the shutdown window where companion DLLs deploy, the doctrine delta at launch, and harvesting the whole log. Use before calling or queueing a restart, when the game is about to close or has just launched, after any mod-list change, and whenever you are tempted to say "restart and see".
---

# The load round

A cold load costs **~23–30 minutes** and there is one game shared by five seats.
So a load is never spent on one question, and never spent to learn something that
could have been read off disk.

## 1. Never "restart and see"

**Arrive already confident.** A restart is where you *confirm* a prediction, not
where you form one. Defs, `About.xml`, `ModsConfig.xml`, the workshop tree and the
live def dump are ordinary files — reading them beats a manager's UI, and beats
launching. If the question truly needs the running game, it goes in your queue for
the next load, not into a launch of its own.

## 2. Write the decision strings BEFORE launching

For **every** item riding the load, write down in advance the exact `Player.log`
string or count that will settle it, its baseline, and what each outcome means. An
item with no named string is not verifiable; it is a hope.

⚠️ **Absence of a line is necessary, not sufficient.** A no-op patch logs nothing,
so "zero hits" and "it worked" are different claims — an item whose success is
silent needs an **expected-present** string too, or an on-screen sighting.

## 3. Batch by ambiguity, not by count

What a load buys you is **attribution**. Batch anything that cannot steal another
item's blame; isolate anything that can.

| change | rides along? |
|---|---|
| config: load order, mod settings, un/subscribes | **free** — no attribution risk |
| a validated XML patch with named log strings | **yes** |
| a new C# assembly · a broad-patching mod | **solo** |

Twenty config changes in one load is fine. Two assemblies in one load is a
bisection you will pay for later.

## 4. Mod-list state on disk: what is authoritative, when

⚠️ **While RimWorld is running, disk state is NOT authoritative.** The game holds
its list in memory and rewrites `ModsConfig.xml` on exit; Steam will not remove a
folder the game holds open. A listed mod may already be unsubscribed, and a present
folder proves nothing.

⚠️ **"Safe after a clean exit" is CONDITIONAL.** A clean exit makes
`ModsConfig.xml` authoritative about **what the game loaded**, never about **what
is on disk now** — RimWorld rewrites it only when the list changes **in-game**, so
an unsubscribe done in Steam or RimSort is invisible to it and the exit writes
nothing. **So check the entry, the folder, and the mtime:**

```bash
# activeMods ONLY. `grep -c "<li>"` over-counts by the expansions: 578 raw vs 573
# activeMods vs 5 knownExpansions.
python3 -c "import xml.etree.ElementTree as ET;print(len(ET.parse(r'.../Config/ModsConfig.xml').getroot().find('activeMods')))"
ls -d ".../workshop/content/294100/<id>"     # what exists
stat -c %y ".../Config/ModsConfig.xml"       # was it rewritten at all?
```

**The mtime is the tell.** If it predates the session, the game wrote nothing and
the list still describes the *previous* state.

**Never assert "your removal didn't land" while the game is up.** Ask whether it is
running, or compare `Player.log`'s mtime to `ModsConfig.xml`'s, and say what each
timestamp implies.

**RimSort being open blocks nothing** — it writes only when the owner clicks Save,
so never ask for it to be closed. The one hazard is the reverse: after an external
edit its view is stale, so say "RimSort is open — hit Refresh".

## 5. Do I need a load at all? `src/RimMandrake/Utils/refresh.py` answers exactly that

Every generated artefact is a snapshot of ONE mod set, load order included. Add a
mod and they do not break — they quietly describe a game that no longer exists.

```bash
python src/RimMandrake/Utils/refresh.py             # changes nothing; prints what is stale and its cost
python src/RimMandrake/Utils/refresh.py --offline   # rebuild everything not needing a load (seconds)
python src/RimMandrake/Utils/refresh.py --all       # offline + patches, in the right order
```

Dependency order: `ModsConfig.xml` → offline scan (**seconds**) → **live dump
(a full load)** → generated patches, `validate_patch.py --live`, `def_diff.py`
(seconds each, but all need a *current* dump). Only the dump is expensive and
everything after depends on it. `refresh.py` **refuses** to regenerate patches
against a stale one; that refusal is the point.

**Take a dump by riding a load you were already paying for:** arm it, then reach
the **main menu** — it writes at startup, no colony needed. Watch for
`[RimDefDump]`; ~27 s and ~1.2 GB. **The marker is not consumed**, so delete it
afterwards or every load pays that again.

```bash
echo all > "%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\dump_request.txt"
```

⚠️ **Never capture a dump during a debug configuration** (mods pulled to isolate a
bug). It is stale the instant they return, and `validate_patch.py --live` reports
the pulled mods' defs as *"does not exist in the live game"* — a wall of confident
false errors. Offline artefacts are cheap and self-correcting; rebuild those freely
with `--offline --note "<why>"`.

## 6. The shutdown window — announce it before the game closes

**A deployed assembly cannot be written while RimWorld runs.** The game holds it
memory-mapped and Windows refuses the copy with `OSError: [WinError 1224] The
requested operation cannot be performed on a file with a user-mapped section open`.
Not "takes effect next restart" — the file cannot be written at all.

So an assembly change is gated on a **shutdown**, not a startup: it lands in the
gap between the game closing and the next launch.

> **Whoever calls a shutdown tells BRIDGE BEFORE the game closes.** Miss the window
> and the work waits a full cycle.

Treat "the repo artifact is ahead of the deployed copy" as the normal mid-session
state, not as drift.

**The same gap is the only time the previous `Player.log` exists** — it is
overwritten at next launch. **Copy it out before you launch**, or the evidence for
everything you just did is gone.

## 7. At launch: take the doctrine delta

A seat reads doctrine once at session start; peers then append traps and file at
its queue and it never learns. The forced idle of a load is when syncing is free.

```bash
python3 src/RimMandrake/Utils/whats_new.py --seat <SEAT> --mark   # your delta, then record HEAD
python3 src/RimMandrake/Utils/whats_new.py --all                  # every seat's staleness
```

**Launch, not close** — close is when work *lands*, so the deltas are not written
yet.

## 8. After the load: harvest the WHOLE log

**You paid for a full load. Do not check only what you changed.**

```bash
python.exe src/RimMandrake/Utils/harvest_log.py                  # every standing check, with baselines
python.exe src/RimMandrake/Utils/harvest_log.py --show crossref  # read the actual lines
```

Exit code 1 means something is above baseline. Triage by consequence, not by
position or volume: dead mods first, then discarded defs, then unresolved
cross-references, then stale Scribe references, then patch no-ops.

**Whoever needs the restart calls it, harvests the log, and writes up for
everyone** — not just its own concerns. Findings go to the per-seat queues;
anything surprising to the matching `traps-*.md`.

## 9. Before you launch

Decision strings written with baselines (§2) · nothing in the batch making another
item unattributable (§3) · `refresh.py` run (§5) · anything needing the shutdown
window handled and BRIDGE told (§6) · the old `Player.log` copied out (§6) ·
everything **deployed**, not merely written (`skills/rimworld-deploy/SKILL.md`).
