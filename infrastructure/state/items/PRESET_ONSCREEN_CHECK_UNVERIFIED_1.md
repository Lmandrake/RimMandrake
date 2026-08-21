## spec
🔴 **I closed `worldbuilder-preset-is-wiped-at-every-launch-not-just-on-steam-updates-6b1e4d`
tonight against the wrong half of its own criteria.** That item asked for two things:

1. *"on the world-creation page, Configure Planet reads **Scale 7** and **Coverage 100%**.
   🔴 If Scale reads 10, the preset lost its parameters — ABORT, do not generate."*
2. *"after the next launch: the LocalLow file is still intact and unchanged."*

I verified (2) — the file is 3,895 bytes, dated 2026-08-20 00:59, still carrying
`myLittlePlanetSubcount 7`, `planetCoverage 1`, `saveGenerationParameters True`, and it is
STILL intact right now after the whole session. I closed the item on that.

**(1) is the half that matters, and it failed.** The owner, remaking the world later in the
session: *"it had lost the scale 7 coverage 100% settings I need."*

⇒ **The file being intact does not mean the game read it.** Those are two different claims
and I treated the cheap one as evidence for the expensive one.

WHAT IS KNOWN, measured:
- LocalLow preset: intact, unchanged, correct values. ✅
- The **workshop stub was regenerated at 01:18**, during this session's launch — 683 bytes,
  parameterless. AWF's `[StaticConstructorOnStartup] Refresh()` does this every launch and
  that part is expected.
- `TryLoadPreset` is documented as first-wins with LocalLow scanned before mod folders,
  which is why the LocalLow copy was supposed to outrank the stub.
- ⚠️ The owner's world-creation page nevertheless came up without the parameters.

So either the scan order is not what we believe, or the game will not re-read the preset for
a SECOND world created inside one session, or the broken session state
(`PAINT_UNDER_MAP_DESTROYS_GAME_1`) took the preset loader with it. **All three are
untested.** ⛔ Do not write any of them down as the cause.

## verify
On the next launch, BEFORE generating anything: reach the world-creation page and read
Scale and Coverage off the screen. Then, without leaving the session, generate a second
world and read them again — that isolates "first world only" from "never".

## criteria
- Configure Planet reads **Scale 7 / Coverage 100%** on the FIRST world of a session
- and again on a SECOND world created in the same session
- if either reads 10, the preset route is not reliable and the parameters must be set some
  other way before the one-shot run — this is the click that decides 21,872 tiles

## notes
Filed by CHECK, 2026-08-21, correcting my own close from earlier the same session. The
closed item stays closed — a run is immutable and a later failure does not reopen it — but
its evidence covered the file and not the screen, and this item is the descendant that
covers the screen. ⚠️ The lesson generalises: **a file being correct on disk is never
evidence that the program read it.**
