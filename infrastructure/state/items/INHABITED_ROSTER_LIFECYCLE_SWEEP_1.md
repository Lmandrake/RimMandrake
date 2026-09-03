# INHABITED_ROSTER_LIFECYCLE_SWEEP_1

Opus code review of the whole Inhabited mod (2026-09-02), alongside
`INHABITED_SETTLEMENT_MAPPARENT_GAP_1` (the architectural finding, filed
separately) and two already-fixed bugs (gender mutation, factionless
destroy — commit `3e251b5b`). These 6 real findings plus 3 doc-vs-code
gaps are not yet fixed or independently re-verified. One candidate finding
(`Patch_BeggarsFromPool` "ignoring addToGeneratedPawns") was checked
against real engine source and found NOT a bug — the actual third
parameter is `ensureNonNumericName`, and the original method calls
`AddToGeneratedPawns`/`PassToWorld` unconditionally regardless of it, so
there's nothing this patch needs to respect. Not included below.

## spec

**Bugs:**
1. `GenSteps_InhabitedSettlement.xml`'s `Inhabited_ComposeSettlementDistrict`
   shares `order 850` with vanilla `FindPlayerStartSpot` in the same
   generator's step list — a tie the mod doesn't control decides whether
   the district is stamped before or after the player's arrival cell is
   chosen, risking the caravan arriving inside a sealed room. Fix: `order
   840` (before start-spot selection), matching the comment's own stated
   intent. (Blocked on `INHABITED_SETTLEMENT_MAPPARENT_GAP_1` resolving —
   this generator step may currently be unreachable dead code.)
2. `DisplacedPool.Draw`/`DrawAny` (`DisplacedPool.cs:176-187,212-223`)
   remove a pawn from the pool and return it — if the caller then fails to
   place it (roster full, an exception, a debug action logging "ROSTER
   REFUSED"), the pawn is orphaned: not in the pool, not in a roster, not
   spawned, not a world pawn, so it is simply never saved. Three call
   sites affected: `WorldObject_Inhabited.cs:191` (roster.TryAdd failure
   isn't even logged), `Patch_BeggarsFromPool.cs:76-91`, `DebugActions_
   Inhabited.cs:219-222`. Fix: return the pawn to the pool on any failure,
   or make Draw/DrawAny take the destination and transfer atomically.
3. Pool-drawn pawns fill `wanted[0..fromPool]` (the trim logic's own
   comment says trimming happens from the BACK specifically to protect
   "leaders and traders — written first"), while `nextCharacter` still
   starts at 0 — so a place receiving displaced people quietly loses its
   authored leader/trader pawnkind and misaligns authored characters
   against roles, silently. If pool-into-lead-roles is intentional, the
   trim comment is wrong; if not, draw the pool into the TAIL of `wanted`
   instead.
4. `Patch_MapRemoval.cs:59-64`'s recall only rescues pawns still spawned
   AND still under a `LordJob_Inhabited` lord. A downed resident being
   carried, or one who left the lord for any reason, falls through to
   `MapDeiniter.PassPawnsToWorld` and becomes an ordinary world pawn
   eligible for `WorldPawnGC` — permanently off the roster with no log
   line, indistinguishable from the recorded-dead case. Given "the roster
   IS the survivors," consider routing non-matching non-player-faction
   pawns into `DisplacedPool` (`DisplacedReason.Enslaved` or similar)
   instead.

**Doc-vs-code gaps** (the project's "entries state what IS" rule applies —
either implement or correct the claim):
5. `InhabitedStock` is filled (`WorldObject_Inhabited.cs:239-240`) and
   persisted, but nothing ever spawns its contents onto a generated map,
   and nothing collects it back at teardown. `InhabitedPlaceDef.cs:67-79`'s
   doc comment ("visible, stealable and destroyable... burn the granary
   and they leave, that is FATE firing, with no new code at all") asserts
   behavior that doesn't exist — `InhabitedFate` (`InhabitedPlaceDef.cs:12,53`)
   is read by nothing anywhere in the codebase.
6. `CharacterDef.cs:125-148` declares authored `weapon`/`apparel`/`items`/
   `skills`/`xenotype`, but `CharacterApplier.ApplyTo` only ever applies
   name, traits and gender — all of that authored kit (18 weapons, 15
   apparel sets, 27 item lists, 101 skills lines per the file's own
   comment) is parsed, validated, and then inert. `CharacterApplier`'s own
   header states name-and-traits-only as deliberate, but `CharacterDef.cs:130-135`
   says the carried-vs-installed call "is CharacterApplier's job, not the
   parser's" — the two files disagree about whose job this is. Needs an
   explicit ruling either way.

**Lower-priority hardening** (cheap, below the reporting bar individually):
7. `SettlementManifestDef.cs:114-118`'s `ConfigErrors` yields "no
   districts" for a null list then dereferences `.Count` on the next line
   — an NRE inside def validation, near-unreachable (needs `districts`
   genuinely null via `IsNull="True"`) but a one-line `yield break` fix.
   Same shape in `InhabitedCastDef.cs:82-96` and `CharacterDef.cs:168`.
8. `GenStep_ComposeSettlementDistrict.cs:116-132` binds a manifest via
   case-sensitive `== settlement.Label`, which falls back to the
   WorldObjectDef's generic label when unnamed — an unnamed settlement can
   never match. Already logs the STUB path (not fully silent), but doesn't
   say WHY it missed; log the searched-for label too.
9. `Patch_MapRemoval` and `Patch_SettlementDeparture` both prefix
   `Game.DeinitAndRemoveMap` at default Harmony priority with no specified
   relative order — harmless today (GateSearchHook only reads the
   manifest), but worth an explicit `[HarmonyPriority]` before a future
   gate-search wants to know who's leaving, since the recall may have
   already emptied the map by then.

## verify

Each fix compiles (`Inhabited.csproj`). 1-4 and 8-9 want a live check once
the bridge/settlement question above resolves; 5-6 are pure decisions
(implement or correct the doc) with no live check needed either way; 7 is
offline-verifiable (trigger the null-list ConfigErrors path directly or by
inspection).

## criteria

All 9 fixed, corrected, or explicitly deferred with a reason — same rigor
as the already-fixed findings: verify against engine source before
trusting the review's prose.
