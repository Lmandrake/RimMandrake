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

## Partial progress 2026-09-02 (FOUNDRY)

- **7 fixed**: all three `ConfigErrors()` NREs (SettlementManifestDef,
  InhabitedCastDef, CharacterDef) guarded against a genuinely-null list.
- **8 checked, no change made**: the STUB log line already prints
  `settlement.LabelCap`, exactly what `ResolveManifestByName` matches
  against — re-reading the code, this is already adequately diagnosable;
  no missing log detail identified.

Still open: 1-4 (pool-draw orphaning, GenStep order collision — blocked
on `INHABITED_SETTLEMENT_MAPPARENT_GAP_1`, role misalignment, recall
gap), 5-6 (stock/fate and authored-kit doc-vs-code gaps, need an explicit
ruling), 9 (Harmony priority hardening, low urgency).

## Closing pass 2026-09-02 (FOUNDRY)

2-6 and 9 done; 1 stays deferred. `Inhabited.csproj` builds Release
clean, 0 warnings 0 errors, after every change. ⚠️ NOTHING HERE HAS BEEN
SEEN RUNNING — this pass was compile-verified only, no deploy and no
game. The live settlement-visit check the `## verify` section wants is
still owed for 2, 3, 4 and 9, and now for 6 as well.

**2 fixed — pool-draw orphaning, closed at the source.** Took the
"atomic transfer" option rather than patching three call sites.
`DisplacedPool.Draw`/`DrawAny` are GONE and cannot be called again;
`DrawInto(faction, count, ThingOwner<Pawn>, arrived)` and
`DrawAnyInto(Func<Pawn,bool>)` replace them. Both go through one private
`TryHandOver`, which removes from the pool, runs the destination, and
puts the pawn back — reason, origin and queue position intact, because
the metadata is cleared only on success — on a refusal *or an exception*.
There is now no instant in which a drawn person belongs nowhere. All
three call sites converted (`WorldObject_Inhabited.InstantiateCast`,
`Patch_BeggarsFromPool`, `DebugActions_Inhabited`); the debug action's
"ROSTER REFUSED" line is gone because a refusal now just leaves them in
the pool and shows as a smaller count.

**3 fixed — the pool fills the TAIL.** The generation loop runs
`for (i = 0; i < wanted.Count - fromPool; i++)` instead of
`for (i = fromPool; ...)`. `InhabitedCastDef.roles`' own doc says leaders
and traders are written first and the trim cuts from the back to protect
them, so the front of `wanted` is exactly the part that must still be
generated. `nextCharacter` correctly stays at 0 — the authored characters
were always meant to land on the freshly generated pawns, and that half
was never the bug.

**4 fixed — but NOT the way the review's prose proposed.** Verified two
things in the 1.6 source first: `LordJob.ShouldRemovePawn` returns `true`
by default and `LordJob_Inhabited` does not override it, so
`Lord.Notify_PawnLost` drops any merely-DOWNED resident out of the lord;
and `MapPawns.AllPawnsSpawned` excludes a carried pawn, which is why
`MapDeiniter.PassPawnsToWorld` itself walks `AllPawns`. So the finding is
real and it is the COMMON case (any firefight casualty), not an edge.

⛔ The suggested fix — "route non-matching non-player-faction pawns into
`DisplacedPool`" — was rejected as over-broad: at `DeinitAndRemoveMap`
the map still holds raiders, traders, visitors and wildlife, and that
rule would have absorbed all of them. Instead the place now keeps a
`List<int> onTheGround` ledger of thingIDNumbers, written by
`GenStep_InhabitedCast` as it spawns each resident (the roster EMPTIES on
spawn, so while a map exists nothing else records who belongs here) and
cleared by the recall. `Patch_MapRemoval` walks `AllPawns`, matches by
that ledger, and uses `TryAddOrTransfer` (a carried pawn already has a
`holdingOwner`, which plain `TryAdd` refuses). Carve-outs match
`PassPawnsToWorld`'s own: a resident recruited or held prisoner by the
player is NOT taken back. A save written before the ledger existed falls
back to the old lord test. The pool is still the last resort if the
roster refuses, and that path logs.

**5 ruled: correct the docs, do not build the feature.** Confirmed
`InhabitedFate` is read by nothing anywhere in the mod, and `stock` is
filled and scribed but never spawned or collected. Spawning stock onto a
map and firing FATE off its destruction is a gameplay feature with its
own map-generation and teardown halves, not a bug fix, so it is out of
scope here and filed as `INHABITED_STOCK_ONTO_MAP_AND_FATE_1`. Four doc
comments that asserted the unbuilt behaviour now state what IS:
`InhabitedPlaceDef.larder`, the `InhabitedFate` enum,
`WorldObject_Inhabited.stock` and the `InhabitedStock` class header, each
naming the new item.

**6 ruled: wire most of it, defer the one part that needs a live check.**
The two files did contradict each other, and the data is real
(`OuterRim_A280Blaster`, `guy762_TuskenMask`, `Crafting 16`), so
"deliberate simplification" was not credible. `CharacterApplier.ApplyTo`
now applies `skills` (set the named outliers only, skip
`TotallyDisabled`), `weapon` (`DestroyAllEquipment` first —
`AddEquipment` does not replace a primary, it logs an error), `apparel`
(`ApparelUtility.HasPartsToWear` checked so the warning can name the
CHARACTER, `dropReplacedApparel: false` since the pawn is off-map), and
the CARRIED half of `items`.

⛔ Deferred: the INSTALLED half. `items` mixes Beer and Ambrosia with
`BionicLeg`/`BionicArm`/`BionicJaw`, split here on `ThingDef.isTechHediff`.
Installing one means resolving a ThingDef → RecipeDef → BodyPartRecord on
that particular body, which fails silently when it fails and cannot be
verified without a game — exactly the shape this item exists to stop
shipping. Filed as `INHABITED_AUTHORED_BIONICS_INSTALL_1`; the skip is
documented in both files. `xenotype` stays unapplied and is now
documented as such — it is null on all 294, so an applier would be dead
code.

**9 fixed.** `Patch_SettlementDeparture.FireGateSearch` takes
`[HarmonyPriority(Priority.First)]` and `Patch_MapRemoval.RecallInhabitants`
takes `[HarmonyPriority(Priority.Last)]` — Harmony runs the higher
priority first, so the gate search sees the cast still standing and the
recall (which empties the map) runs after it. Both class comments
updated; the SettlementDeparture one said "order between them does not
matter here", which is no longer the contract.

**1 still deferred, untouched**, exactly as recorded above: it needs the
scope call on `INHABITED_SETTLEMENT_MAPPARENT_GAP_1` before anyone knows
whether the GenStep is reachable at all.
