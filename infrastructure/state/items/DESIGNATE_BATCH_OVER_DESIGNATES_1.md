## the bug

`jawa/designate_batch`'s THING-designation path
(`JawaBenchMapTools.cs`, `DesignateBatch`) handed EVERY `Thing` sitting in
each cell of the rect straight to `AddDesignation`, not just the one
type-appropriate for the requested `DesignationDef`. e.g. a `Deconstruct`
rect over a cell holding both a wall and a plant would try to designate the
plant for deconstruction too; a `WorkGiver`/`JobDriver` later casting
`(Building)target` on it throws `InvalidCastException`. Pre-existing (the
loop always did this), but only reachable by DEFAULT since `106de82f`'s NRE
fix made `designate_batch` usable without the explicit `onThings=true` flag.

## the ruling

Owner (card, 2026-09-04): "FIX PROPERLY - filter by the designation's own
target rules so bridge automation stops mass-designating bystander Things."

## the fix

Vanilla has no single generic "is this Thing valid for this DesignationDef"
predicate — it lives split across 18 `Designator_*.CanDesignateThing`
overrides (17 THING-targeted `DesignationDef`s in `Designations.xml` +
`Flick`, which has no `Designator_Flick` at all and is filtered instead by
`FlickUtility.UpdateFlickDesignation`'s own `CompFlickable` check). Read
every one of the 18 from 1.6 source (RimSage) rather than guessed, and built
`CanDesignateThingByType(DesignationDef, Thing)` in `JawaBenchMapTools.cs` —
a switch on `dd.defName` reproducing each Designator's actual type/ownership
check. Deliberately NOT copied: each Designator's own
`DesignationOn(t, dd) != null` re-check (the loop already tracks that as
`already`/`alreadyPresent` separately), `DebugSettings.godMode` branches (not
applicable to a headless bridge caller), and UI-only side effects
(`Messages.Message` warnings). Falls open (`true`) for any Thing-targeted
`DesignationDef` this switch has never seen — a modded def should not have
every Thing silently refused just because nobody taught the table about it
yet.

Applied to `add` only — `remove` still accepts any Thing, so a stray
wrong-type designation from before this fix (or from another mod) stays
removable. New `skippedWrongType` counter added to the result payload
alongside `added`/`removed`/`alreadyPresent`/`alreadyAbsent`.

## verify

- `dotnet build` (via `build.py`, Windows python.exe from the repo root):
  0 warnings, 0 errors.
- `--gm` build plan: no tool loss vs the live deployed copy (the earlier
  no-`--gm` plan showing ~40 "LOSES" entries was the DEFAULT-off GM-tools
  flag stripping every GM-gated tool, not a real regression — confirmed by
  re-running with `--gm` and getting a clean plan).
- Full selftest suite: 62/62 passed after the change (no regression;
  `selftest_tool_metadata.py` covers this DLL's tool surface).
- NOT live-tested in game (a `designate_batch` call over a mixed-content
  cell, checking `skippedWrongType` counts the bystander and `added`/`totalNow`
  reflect only the type-correct target) — owed to whoever restarts next.

## needs: deploy

Build succeeded and is staged at
`src/RimMandrake/bridgetools/artifacts/BridgeTools/JawaBench/JawaBench.BridgeTools.dll`,
but `build.py --apply` refused: **RimWorld holds the DLL memory-mapped while
running (WinError 1224) — deploy needs the game DOWN first**, not just a
restart afterward. Deploy is `python.exe src/RimMandrake/bridgetools/build.py
--gm --apply` (run from the repo root; the plain `python3` in WSL cannot
drive `dotnet.exe` against a `/mnt/...` path). Batch this with any other
game-down work already queued rather than restarting solely for this.
