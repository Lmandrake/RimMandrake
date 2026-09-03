# BRIDGE_PAWNTOOLS_SILENT_SUCCESS_SWEEP_1

Deep opus code review (`feature-dev:code-reviewer`, 2026-09-02) of
`JawaBenchPawnTools.cs`/`JawaBenchPawnKitTools.cs` hunting this project's
most costly recurring bug class — a `[Tool]` reporting `success: true` while
changing nothing. Found 13 real candidates. The 3 CRITICAL ones were
verified against decompiled engine source and fixed same-session (commit
message names them: off-map equip/wear/inventory silent no-op newly
reachable via today's caravan-pawn `FindPawn` fallback, `pawn_gear
action=inventory` reporting success on a 0/partial move, `start_inspiration`
destroying the pawn's existing inspiration before checking whether the new
one can even start).

## spec

The remaining 10 findings, not yet fixed or independently re-verified —
each needs the same treatment (read the cited lines, verify against engine
source before trusting the review, then fix):

**Important:**
4. `otherPawn` lookup errors discarded in `jawa/pawn_need` (`JawaBenchPawnTools.cs:896`)
   and `jawa/pawn_mental` (`:1621`) — a mistyped `otherPawn` silently proceeds
   with `other: null` instead of failing. Two sibling call sites in the same
   file (`PawnRelations:1096`, `PawnRomance:1688`) already get this right —
   match them.
5. `DefDatabase<T>.GetNamedSilentFail` has no null guard and throws
   `ArgumentNullException` on an omitted def parameter — 4 sites in
   `JawaBenchPawnKitTools.cs` (`:109` skill, `:236` ability, `:291`
   inspiration, `:710` thingDef) skip the `IsNullOrEmpty` guard every other
   lookup in this codebase uses.
6. `jawa/lock_apparel all=true` on a pawn wearing nothing returns
   `success: true` with an empty list — can't distinguish "locked
   everything" from "nothing to lock." The single-item path 30 lines below
   (`:576-578`) already does this right.
7. `jawa/set_pawn_backstory` with neither `childhood` nor `adulthood` set
   reports success having written nothing (`JawaBenchPawnTools.cs:302-357`).
   Two sibling tools (`SetPawnIdentity:271`, `SetPawnAppearance:584`) already
   guard this with `if (changed.Count == 0) return Fail(...)`.
8. `jawa/inventory_transfer` add-mode's leak-rescue (`JawaBenchPawnKitTools.cs:677-691`)
   only fires via `p.Map`, which is null for the `WorldPawns` pawns today's
   fallback newly exposes — the rescue never fires for a caravan member, and
   the `Fail` message claims the container merely "refused it" when the item
   may actually have been orphaned. Needs `p.MapHeld`/`p.PositionHeld` fallback,
   or an explicit `Destroy()` + honest message if there's truly no map.

**Worth a look (lower confidence per the review, cheap to verify):**
- `JawaBenchPawnTools.cs:75-91` — the `WorldPawns` name-match pass has no
  ambiguity detection (`FirstOrDefault` over a much larger population than
  the spawned-only pass); a nickname collision now silently routes a write
  tool onto the wrong pawn.
- `JawaBenchPawnKitTools.cs:52-55` + `:655-679` — `inventory_transfer`
  add-mode has no `found is Pawn` guard; confusing the id parameter for a
  pawn id could `SplitOff(1)` a PAWN into another pawn's inventory pack.
- `JawaBenchPawnTools.cs:1423` — `pawn_psychic action=remove` reports
  success removing an ability that may be hediff/apparel/role-granted and
  therefore not actually removable by this call.
- `JawaBenchPawnTools.cs:671-677` — `clear` mode on a pawn missing the
  named tracker returns the generic "clearWhat must be..." usage error
  instead of naming the actual missing-tracker cause.
- `JawaBenchPawnTools.cs:728` — bare `catch {}` around
  `PawnApparelGenerator.GenerateApparelOfDefFor`; a silent degrade to
  unstuffed/uncoloured/no-quality `ThingMaker.MakeThing` is never surfaced.

## verify

Each fix compiles (`build.py --gm`), and — since these are bridge tool
behavior changes — the next live bridge session spot-checks at least the
`otherPawn`-discard and `set_pawn_backstory` no-op fixes with a real call.

## criteria

All 10 remaining findings fixed or explicitly triaged (confirmed not a bug,
with the check that ruled it out named), matching the rigor applied to the
3 already-fixed CRITICAL findings — verify against engine source before
trusting the review's prose, the way the parent session did.

## Closed 2026-09-02 (FOUNDRY)

Fixed 7 of 10:
- Findings 4, 5, 6, 7, 8 (all 5 numbered "Important" items) — otherPawn
  lookup errors now Fail() instead of silently proceeding as null (2
  sites), the 4 missing null guards before GetNamedSilentFail (would throw
  ArgumentNullException, not Fail cleanly), lock_apparel all=true on empty
  apparel now Fails, inventory_transfer's leak rescue now falls back to
  MapHeld/PositionHeld for off-map pawns and destroys+says-so only if
  there's truly no map anywhere.
- 2 of 5 "worth a look" items: inventory_transfer add-mode now refuses a
  `thing` id that resolves to a Pawn (was reachable via
  FindLiveThingById's map-things scan, would SplitOff(1) a pawn into
  another pawn's inventory); pawn_psychic remove now distinguishes an
  ability that was actually in the directly-granted list from one that
  wasn't (hediff/apparel/role-granted, which RemoveAbility cannot touch)
  instead of always saying "removed."

Deliberately deferred, not fixed this pass:
- **WorldPawns name-match ambiguity** (no refusal on >1 match) — the fix
  needs `FindPawn`'s return contract to change (report ambiguity, not just
  a single Pawn or null), and it's a shared helper ~20 tools call. Bigger,
  riskier change than the others here; wants its own pass, not a rushed
  addition to this one.
- **clear-mode wrong error message** on a pawn missing the named tracker —
  cosmetic (still refuses correctly, just names the wrong reason).
- **Bare `catch {}` around `PawnApparelGenerator.GenerateApparelOfDefFor`**
  — a silent degrade to unstuffed/uncoloured gear, never surfaced. Real
  but low-frequency; a `catch (Exception e)` that adds a `notes` line
  costs nothing to add whenever this file is touched next.

Compiles clean (`build.py --gm`, 0/0). Deploy owed to the next game-DOWN
window (game holds the companion DLL open).
