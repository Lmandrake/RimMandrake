---
name: rimworld-load-round
description: How to spend a RimWorld cold load — and how to stop needing one. A 13-mod minimal list loads in 22 SECONDS against ~25 minutes on the owner's full list, making a full edit-build-deploy-test cycle about a minute; modlist_swap.py does the swap and restore. Covers what that minimal list cannot prove. Arriving already confident instead of "restart and see", writing the Player.log strings that will decide each item before launching, batching by ambiguity, what ModsConfig.xml is and is not authoritative about, src/RimMandrake/Utils/refresh.py and whether a load is needed at all, the shutdown window where companion DLLs deploy, the doctrine delta at launch, and harvesting the whole log. Use before calling or queueing a restart, when the game is about to close or has just launched, after any mod-list change, and whenever you are tempted to say "restart and see".
---

# The load round

A cold load costs **~23–30 minutes** and there is one game shared by five seats.
So a load is never spent on one question, and never spent to learn something that
could have been read off disk.

## 0. 🟢 FIRST: does this load have to be expensive at all?

**Measured 2026-08-19 — a cold load on a 13-mod MINIMAL list is 22 SECONDS**, against ~25
minutes on the owner's full list (576 as of 2026-08-20 — read
`ModsConfig.FULL.LATEST.xml`, never a number in a doc). The engine's own clock agrees:
`[RimBridge] STARTUP_TIMING phase=bridge-start.total elapsedMs=12364`. A quicktest world on
top costs **5 s**. ⇒ **the whole edit → build → deploy → launch → test cycle is about ONE
MINUTE.** Everything below about hoarding a load still applies to the owner's real stack —
but for *tool and mechanism* work the scarcity is gone. Do not spend a 25-minute load
proving something a 22-second one can prove.

⛔ **An XML-only change is proven by a MINIMAL-LIST RESTART, not by hot-reload
(owner's ruling 2026-09-03).** Deploy → restart minimal (22 s) → read back with
`jawa/get_defs`. **`jawa/hot_reload_defs` is retired as unstable** — it hung a
589-mod game for 5 minutes and left it unable to generate any pawn while every
health flag still read green. ⚠️ Its clean minimal-list pass (0.04 s, 2026-09-02)
was real and is *why* it is retired rather than gated: a call that behaves on 19
mods and destroys pawn generation on 589 cannot be trusted by the seat deciding
which case it is in. Canonical entry: `skills/rimworld-modding/SKILL.md` §2;
evidence: `infrastructure/state/items/HOT_RELOAD_DEFS_BREAKS_PAWNGEN_1.md`.

```
python3 src/RimMandrake/Utils/modlist_swap.py --status
python3 src/RimMandrake/Utils/modlist_swap.py --minimal --restore   # add --apply
```
Plan-only by default; it archives the live file before every write. The owner's real list
is frozen at `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`.

**The 13 and why each one is there:** harmony · core + all five expansions · VEF (Alpha
Biomes' hard dep) · `brrainz.rimbridgeserver` · alienworlds + tidallylocked · alphabiomes ·
mylittleplanet.
🔴 **Odyssey is NOT optional** — `Tile.Landmark` returns null without `OdysseyActive`, and
PlanetLayer/Orbit are Odyssey types. A leaner list silently has no landmarks.
🔴 **`brrainz.rimbridgeserver` is not optional** — without it there is no bridge at all,
however the companion DLL is deployed.

### ⚠️ What the minimal list CANNOT do

* **It cannot reproduce the 21,872-tile geometry.** `ferny.Worldbuilder` is absent, and
  Worldbuilder is what loads the TidallyLocked preset. A quicktest comes out 119,904 tiles.
  Anything depending on real tile IDs needs the full list.
* **It does not have the content mods.** A 21,872-row import validated at 81.6% on it, and
  **every** mismatch was one of 8 biome defs the 13-mod list lacks — not a tool defect.
* 🔴 **While it is installed, the live `ModsConfig.xml` is NOT evidence about the owner's
  stack.** A research thread read it and reported Gravship Exporter inactive; it is active
  in the real 578. Read `ModsConfig.FULL.LATEST.xml` instead.
* 🔴 **Restore before the owner plays.** `--status` prints a loud warning while minimal is
  live. Leaving his machine on 13 mods is the one unacceptable outcome.

---

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

🔴 **The owner's three-assembly waiver STANDS — "batch it" — on one mandatory
condition: write the three expected-failure signatures down BEFORE launching.**
Batching is only affordable because the assemblies fail in *distinguishable*
places, and that property is worthless unless the distinctions are on paper
before the log exists. **A signature invented after reading the log is not
evidence, it is a story that fits.** One signature per assembly, in
`infrastructure/state/EXPECTED_FAILURES_next_load.md`, before the game starts.
Do not re-litigate the waiver, and do not quietly split the load out of caution.

## 4. Mod-list state on disk: what is authoritative, when

⚠️ **While RimWorld is running, disk state is NOT authoritative.** The game holds
its list in memory; Steam will not remove a folder the game holds open. A listed
mod may already be unsubscribed, and a present folder proves nothing.

🔴 **RimWorld does NOT rewrite `ModsConfig.xml` on exit.** This line used to say it
did, and contradicted the paragraph directly below it — a reader could leave with
either belief. Measured 2026-08-13: at exit `Player.log`'s last write was 10:04:55
while the config's mtime was 10:01, *older than the exit*, and the file moved again
at 16:41:39 with no game running at all.
**Before reasoning about the list or the order at all, read
`skills/rimworld-start-prep/SKILL.md`** — three uncoordinated writers own different
columns of this, and that skill is where they are set out.

⚠️ **"Safe after a clean exit" is CONDITIONAL.** A clean exit makes
`ModsConfig.xml` authoritative about **what the game loaded**, never about **what
is on disk now** — RimWorld rewrites it only when the list changes **in-game**, so
an unsubscribe done in Steam or RimSort is invisible to it and the exit writes
nothing. **So check the entry, the folder, and the mtime:**

```bash
# activeMods ONLY. `grep -c "<li>"` counts LINES and returns 6, not a count of mods;
# `grep -o "<li>" | wc -l` returns activeMods + the 5 knownExpansions. Parse it.
# Never quote a remembered total — print it, and quote the command with it.
python3 -c "import xml.etree.ElementTree as ET;print(len(ET.parse(r'.../Config/ModsConfig.xml').getroot().find('activeMods')))"
ls -d ".../workshop/content/294100/<id>"     # what exists
stat -c %y ".../Config/ModsConfig.xml"       # was it rewritten at all?
```

**The mtime is the tell.** If it predates the session, the game wrote nothing and
the list still describes the *previous* state.

**Never assert "your removal didn't land" while the game is up.** Ask whether it is
running, or compare `Player.log`'s mtime to `ModsConfig.xml`'s, and say what each
timestamp implies.

🔴 **No config file waits for anything. Owner's ruling, 2026-08-15:** *"You NEVER
have to ask if RimSort is open. It does not autosave, and I will never save without
asking. Nobody blocks on RimSort or game close for config files of any kind."*
`ModsConfig.xml`, load order and user rules are writable at any moment, game up or
down, RimSort open or shut — **never ask, never hold an item for a window.** The
down-window exists for **assemblies**, which the OS locks while the game runs; that
is a file lock, not a policy, and it is the only thing it covers. The one hazard is
the reverse of the old one: after an external edit RimSort's view is stale, so say
"RimSort is open — hit Refresh".

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

## 5a. ⏳ Delete throw-away saves WHILE THE GAME RUNS — expires when the campaign starts

**Owner's ruling, 2026-08-14.** Deleting savegames with the game DOWN does not
stick: Steam Cloud reconciles at the next launch and restores them. Measured — 26
`.rws`, 701 MB, back with their **original mtimes**, after a deletion that had
already been recorded as done.

> **The window where a deletion survives is while the game is RUNNING.**

So when a debugging world is being thrown away, delete the saves **and** the
screenshots **after the game is live**, not after it exits. **Do not disable Steam
Cloud** — that is no longer the fix and nobody asked for it.

🔴 **A post-`rm` count is NOT verification. Say "deleted, UNVERIFIED".** `Saves/`
read empty last time too, and Cloud restored all 26 with original mtimes at the next
launch. **The only meaningful check is a count taken AFTER the game next starts** —
until then the ledger says *deleted, unverified*, never *gone*.

⚠️ **And check the delete actually deleted.** A compound `rm` with an unmatched glob
removes **nothing** under zsh — `nomatch` aborts the whole command, so
`rm -f a/*.rws b/*.bak c/*.png` with no `.bak` present deletes zero files and prints
one warning that reads like a nit. **Use `find … -delete`, or print before/after
counts.** Measured 2026-08-14; it nearly produced a "deleted 734 MB" report that was
fiction.

🔴 **This rule has an EXPIRY, and the expiry is part of it: it GOES the day the real
campaign starts.** It exists only for throw-away debugging worlds. A standing
"delete the saves" habit pointed at a live campaign is destructive, and a rule that
should have died is exactly how that happens.

⚠️ **Anything still saying re-deletion "needs Steam Cloud disabled first" is wrong.**
It needs the game *running*.

## 6. The shutdown window — announce it before the game closes

**A deployed assembly cannot be written while RimWorld runs.** The game holds it
memory-mapped and Windows refuses the copy with `OSError: [WinError 1224] The
requested operation cannot be performed on a file with a user-mapped section open`.
Not "takes effect next restart" — the file cannot be written at all.

So an assembly change is gated on a **shutdown**, not a startup: it lands in the
gap between the game closing and the next launch.

> **Whoever calls a shutdown tells CHECK BEFORE the game closes.** Miss the window
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
window handled and CHECK told (§6) · the old `Player.log` copied out (§6) ·
everything **deployed**, not merely written (`skills/rimworld-deploy/SKILL.md`).

## 10. 🔴 Launch through Steam, never the bare `.exe` — bypassing it intermittently corrupts assembly loading

Measured 2026-08-30. A cold load launched normally (through Steam) worked cleanly
on a 19-mod minimal list: bridge up, 301 companion tools, full mod content loaded.
Immediately after, closing that process (`Stop-Process -Force` on `RimWorldWin64`)
and relaunching by starting `RimWorldWin64.exe` directly —
`Start-Process -FilePath '...\RimWorldWin64.exe'` — produced RimWorld's own
**"Recovered from incompatible or corrupted mods errors"** dialog on the very
next launch, **three times in a row**, with the identical unchanged mod list and
unchanged mod DLLs. The actual exception (`Player.log`, `RebindAllDefOfs` →
`GenTypes.AllTypesWithAttribute`): `System.TypeLoadException: Could not resolve
type with token ... from typeref (expected class 'HarmonyLib.HarmonyPatch' in
assembly '0Harmony, Version=2.4.1.0...')` — a Harmony-assembly-version
resolution failure during the full-type reflection pass, not a content/def
problem. RimWorld's own recovery caught it and reset `ModsConfig.xml` to
Core-only (6 mods) each time.

**Isolated properly, not guessed:** reverted the two content files that had
changed between the working and failing launches (`git stash`), redeployed,
relaunched via the bare `.exe` again — **same crash**, byte-identical content
that had worked minutes earlier. This ruled out the content/def changes
entirely. The one variable that actually differed: the working launch went
through Steam; every failing relaunch used the bare executable.

**Fix, confirmed:** launch via Steam instead —
`Start-Process -FilePath '...\Steam\steam.exe' -ArgumentList '-applaunch','294100'`.
Immediate clean load: bridge up, 19 mods held, 301 tools, first try.

⇒ **Bypassing Steam's own launch path — even though the same `.exe` file runs
either way — skips whatever Steam does to mount/validate Workshop content
(`steamapps/workshop/content/294100/*`) before handing off to the game.** A
raw `.exe` launch can silently pick up a stale, partially-synced, or
inconsistently-cached copy of a Workshop mod's bundled `0Harmony.dll`,
producing exactly this class of intermittent assembly-version collision.
**Always launch (or relaunch, including a driver-initiated restart for a
def/content change) via `steam.exe -applaunch 294100`, never the bare
`RimWorldWin64.exe` path**, even though the latter looks like the more direct
and reliable route.
