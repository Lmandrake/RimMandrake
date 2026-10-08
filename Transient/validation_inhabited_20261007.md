# Inhabited offline validation, 2026-10-07 (FOUNDRY, uncommitted, no bridge)

## 1. Survey (4.9k lines, 30 files)
Chosen kernels, and why:
1. **Custody of people** (DisplacedPool, WorldObject_Inhabited.InstantiateCast/EvacuateRoster, InhabitedFateWorker.Apply, Patch_MapRemoval recall):
   a person moves between the displaced pool, a place's roster and the map; the mod's central promise is that nobody is ever held by
   nothing (a pawn held by no ThingOwner is not saved and is eaten by WorldPawnGC). Dense hand-over/put-back/refusal bookkeeping plus a
   per-person metadata book (reason, origin, queue order) that must track pool membership exactly across save/load.
2. **Fate + stock + routine** (InhabitedFateWorker.DetectCause, InhabitedStock.Fill/IsPlaceGoods, Patch_MapRemoval state rules,
   LordToil stance): a four-way cause precedence with lazy engine scans, a stack-splitting rule, the "is this the place's goods" predicate
   (corpses must never qualify), and the Inhabited -> Abandoned/Looted state machine.
Rejected as kernels:
- GenStep_ComposeSettlementDistrict, StructureInjectionsBridge, GenStep_InhabitedCast/Stock anchor finding, JobGiver_SleepAtNight cell search:
  almost entirely engine calls (CellFinder, MapGenerator vars, reflection into another mod, Reserve/Forbidden). Nothing to extract that is not a mock.
- CharacterApplier (489 lines): applies authored traits/skills/gear onto a Pawn through engine setters; no state to fuzz.
- CharacterDef/CastDef/ManifestDef ConfigErrors: static validation of XML, covered by the lint instead.
- GateSearchHook / SettlementCasing: a Rand.Chance and four assignments; the lint checks the Scribe coverage.
- DebugActions_Inhabited (620 lines), InhabitedReport: debug UI and report writing.

## 2. Kernels + fuzz
Extracted (behaviour preserving, call sites call the kernels, Scribe names unchanged; Verse-free so the net8 selftest compiles the production files):
- `src/RimMandrake/Inhabited/Source/InhabitedCustodyKernel.cs`: enum DisplacedReason (moved), DisplacementBook (the pool's reasons/origins/displacedAt/nextOrder),
  InhabitedCustody.{Absorb, Order, HandOver, DrawInto, DrawAny, MoveRosterToPool, Recall, BuildWanted, GenerateCount, UpcomingCharacter}, generic over the
  holder type with the engine container calls passed as delegates. DisplacedPool, EvacuateRoster, Apply, RecallInhabitants and InstantiateCast call them.
  (EvacuateRoster and Apply were two copies of one loop; both now call MoveRosterToPool.)
- `src/RimMandrake/Inhabited/Source/InhabitedFateKernel.cs`: enums InhabitedFate/InhabitedState/RouteStance (moved), Cause (decision order with lazy scan delegates),
  ShouldApply, StateAfterFate, StateAfterRecall, SplitStacks, IsPlaceGoods, IsSleepingHour, Stance. InhabitedFateWorker, InhabitedStock, LordToil call them.
Defect found by the extraction + fuzz (FIXED in the kernel, tiny behaviour change):
- **Dangling metadata for a person the pool could not take back**: when a draw's destination refused a person and the pool then refused to take
  them back, the pawn is held by nothing (logged as an error) but their reason, origin and queue slot stayed in the three Scribed dictionaries forever.
  `Restore` now drops the metadata with them. Rare (needs a ThingOwner.TryAdd refusal), found by the book-equals-pool-members invariant.
Observations not changed (engine-side, flagged for a human):
- `DisplacedPool.Absorb` despawns / leaves WorldPawns / changes faction BEFORE the ThingOwner add; if the add then refuses, the pawn has been despawned
  and re-factioned. Callers re-add them to the roster, but Recall's last branch ("left to the world") leaves a despawned, non-world pawn that nothing holds.
  Needs both the roster and the pool to refuse; cannot be fixed without the engine's add order.
- InstantiateCast now rolls `castSize` before the empty-wanted early return (it used to roll only when wanted was non-empty): one extra Rand call in map gen.
Fuzz: `src/RimMandrake/Inhabited/SelfTest/{InhabitedFuzz.cs,Program.cs,RimMandrakeInhabited.SelfTest.csproj}` (beside Source/, not in it, because Inhabited.csproj
uses default compile globbing), wrapper `src/RimMandrake/Utils/selftest_inhabited_fuzz.py` (families pool | place | cause | units; knobs --fuzz-scale/--fuzz-seed/--fuzz-only).
Invariants:
- pool: every person held by exactly the holder their record names, never two; dead never in the pool; the book's three dictionaries have exactly the pool
  members as keys, with reason/origin/queue slot equal to what absorb recorded (oracle is the model's own sequence, not the kernel's ordering);
  nextOrder equals successful absorbs, no two people share a slot; absorb refuses the dead and anyone already held; a draw takes the longest-waiting first
  among the right faction, stops at count, a refused or throwing destination leaves the person in the pool with reason and slot unchanged (exceptions propagate);
  nobody is lost unless a refusal was injected into that very action, and the lost count equals the injected double refusals; evacuate moves all living,
  skips the dead, returns a refused person to the roster; recall order roster -> pool -> world.
- place (cast + visit + fate + leave): wanted list = authored order trimmed from the back; drawn people are the right faction and the pool never exceeds the
  wanted count; the pool fills the TAIL (generated kinds are the head of wanted); authored characters are used in order with no gap or repeat; cast <= castSize;
  stock splits sum to the count, 1..limit each, minimal stack count; collected goods = exactly the units the oracle calls ours (corpses, the colony's items,
  dead stacks never; ledger or stock area otherwise), split/merged/hauled stacks included; Resident places never fire or scan; Transient fires at once and
  the place empties; a fired fate empties the roster into the pool (unless the pool refused) and reads Looted iff the larder is empty; a place never returns to
  Inhabited; Looted never appears without a fate; Squatted never written.
- cause: 4-way precedence burn > hostile > harmed > robbed against an independent oracle over 500k random vectors incl. the exact threshold boundary
  (`left == spawned*fraction` is not robbed) AND laziness (a scan delegate runs exactly when no earlier cause made it unnecessary).
- units: IsSleepingHour over all 576 (start, wake) pairs x 24 hours against a modular-arithmetic oracle; stance boundary; legacy save (null dictionaries) reads Fled/unknown/last.
Seeds: default scale 28,001 cases / 676k steps in 2.8 s; `--fuzz-scale 25`: 700,001 cases / 16.9M steps in 50 s, all green; replayed --fuzz-seed 7, 4242, 99991 green.
Mutations (each planted, caught, reverted; md5 of both kernels verified identical afterwards; slept 5 s before each run):
- M1 draw no longer forgets metadata on success: pool FAIL "book keys ... differ from pool members" (seed 1, 2 actions).
- M2 the ORIGINAL bug (put-back failure keeps metadata): pool FAIL same message, seed 1, 2 actions.
- M3 trim wanted from the FRONT: place FAIL "wanted list is not the authored order trimmed from the back".
- M4 longest-waiting becomes newest-first: pool FAIL "draw order 100 != longest-waiting-first 101" (first attempt was NOT caught: the oracle reused the kernel's
  ordering; oracle made independent, then caught on 5 seeds).
- M5 IsPlaceGoods stops excluding corpses: place FAIL "IsPlaceGoods disagrees for item 1000".
- M6 hostile checked before the burning granary: cause FAIL "cause Hostile, expected Burned" + laziness failure.
- M7 MoveRosterToPool stops returning a refused person to the roster: pool FAIL "evacuate lost 1, expected 0".
- M8 SplitStacks off by one: place FAIL "split of 334 at -3 has a stack outside 1..1".
- M9 robbed threshold `<` -> `<=`: first NOT caught (boundary too rare); added boundary vectors, then caught.
- M10 defend window `<` -> `<=`: units FAIL "old harm still defends".

## 3. Lint
`src/RimMandrake/Utils/selftest_inhabited_lint.py` (run_selftests.py discovers selftest*.py): 304 XML class refs (tags, Class=, *Class elements) resolve; 3,985 field
children are public fields; 4 enum-valued fields hold members (def-valued fields: armed, count 0 - no shipped def sets one yet, explicitly exempt from the
looked-at-nothing rule); 14 translate keys (literal .Translate() and the six fate-cause constants the watch component translates dynamically) have Keyed entries;
37 Scribe calls: names unique per class and every own public field of WorldObject_Inhabited/WorldObject_InhabitedSettlement/SettlementCasing/DisplacementBook is
Scribed (25 checked; DisplacedPool scribes the book's four fields under their own names); csproj default-compile ON and no .cs below Source/; both kernels free of
Verse/RimWorld/UnityEngine/HarmonyLib usings; 1 DefOf field resolves. Findings on the unmodified tree: 0 (after fixing two lint false positives of my own: expression-bodied
properties read as fields, inherited fields demanded of the subclass).
Mutations (each caught, file restored): misspelled `<stockLabl>` in Places_Inhabited.xml; `<fate>FleeIfThreaten</fate>`; deleted the `stockRadius` Scribe line;
renamed Keyed `InhabitedFateRobbed`; `using Verse;` in the fate kernel; deleted the `nextOrder` Scribe in DisplacedPool.

## 4. Build
`python3 src/RimMandrake/Utils/winbuild.py src/RimMandrake/Inhabited/Source/Inhabited.csproj`: 0 warnings, 0 errors. No `<Compile Include>` lines needed (Inhabited.csproj uses default
globbing, which is why the selftest lives in `Inhabited/SelfTest/`, outside Source/). DLL + .srchash rewritten in the working tree, NOT committed (source stamp is +dirty).
Not run in game: the extraction preserves the call shapes but no live pass was made.

## Run
- `python3 src/RimMandrake/Utils/selftest_inhabited_fuzz.py [--fuzz-scale 25] [--fuzz-seed N] [--fuzz-only pool|place|cause|units]`
- `python3 src/RimMandrake/Utils/selftest_inhabited_lint.py`
