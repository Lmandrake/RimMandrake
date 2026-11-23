## spec

Design Version: FlowWorks 0.1.0 (current, a Problem against the locked bars). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks raiders and ladders: four faults on one path (leaning ladders skipped, the chop never lands, climber def names that left, no short ladder tried at a 4 m pit).

## merged tickets

- `LADDER_PARITY_FIX_RAIDERS_SKIP_LEANING` (proposed): [MINOR] Ladderless raiders cannot use a ladder already leaning against a wall
  - sweep reading: breaks the owner's 2026-10-23 parity promise 'Both sides should be able to use each other's ladders'; at HEAD RM_LadderParity.MightClimb (line 277) still returns p.Faction == Faction.OfPlayer || CarriedLadder(p) != null, so a ladderless raider never reaches CanClimbAt for a leaning ladder (verified GPT finding FC_pits_superdeep_2.4)
  - its check: new LadderParityChecks SelfTest: a hostile with no ladder passes MightClimb at a cell with a standing ladder (red before the fix)
  - files: `src/RimMandrake/FlowWorks/Source/Superdeep/RM_LadderParity.cs`, `src/RimMandrake/FlowWorks/Source/Superdeep/RM_WallClimb.cs`
- `RAIDER_CHOP_FIX_AXE_NEVER_LANDS` (proposed): FlowWorks MOD: ladderless raiders take RM_RaiderChopForLadder jobs for ~8000 ticks and never fell an oak (raid_trench r55: 6 of 6 Plant_TreeOak standing, no stump). LADDER_PARITY_RAIDER_FELLS_TREE now reads FAIL on this (was a false PASS on chopSeen). Evidence D:\ClaudeWork\rimmandrake\scratch\br1g_caps\r55.json
  - sweep reading: a failure happened live: raid_trench r55, ladderless raiders hold RM_RaiderChopForLadder jobs ~8000 ticks and fell 0 of 6 oaks; row LADDER_PARITY_RAIDER_FELLS_TREE reads FAIL; breaks the owner's card answer 'they look for something to chop down, get the wood, then build it' (2026-10-23); no fix commit since
  - its check: raid_trench_proof.py --direct --depth 4 with trees near the east bank: LADDER_PARITY_RAIDER_FELLS_TREE PASS (a stump appears)
  - files: `src/RimMandrake/FlowWorks/Source/Superdeep/RM_LadderParity.cs`, `src/RimMandrake/FlowWorks/Defs/Canals/JobDefs/FlowWorks_RaiderTrench.xml`
- `FLOWWORKS_CLIMBERS_REWIRE_NAMES_THAT_LEFT` (proposed): FlowWorks_LadderClimbers.xml still names RSW_ creatures that moved to the RM tier as RM_ (batch 3: RSW_Diplocaulus/Holcorobeus/Platyhystrix/Protosolpuga -> RM_; more follow as SWB_RM_FAUNA_DECIDE_HOME_LIKE_CHIKKA batches land). Repoint the defName= list; BENCH owns FlowWorks so FOUNDRY's mover skipped it. Old names now match nothing (silent no-op).
  - sweep reading: at HEAD Patches/Canals/FlowWorks_LadderClimbers.xml still names RSW_Diplocaulus/Holcorobeus/Platyhystrix/Protosolpuga; no RSW_ def of these exists, each RM_ def does (grep), so the patch silently skips them and they never climb ladders; Karrask is in neither form
  - its check: python3 src/RimMandrake/Utils/validate_patch.py --live --defs on FlowWorks_LadderClimbers.xml: every defName= matches a loaded def
  - files: `src/RimMandrake/FlowWorks/Patches/Canals/FlowWorks_LadderClimbers.xml`
- `RIMMANDRAKE_BUILD_RAIDERS_TRY_SHORT_LADDER_AT_FOUR_METRE_PIT` (proposed): FlowWorks: at a 4 m (8 level) prison pit that holds a fallen comrade, free raiders fetch a portable ladder, set it at the pit, and the player can see it is too short (it reaches 3 m); they do not bring the man out, they can be driven off, and the fallen stay prisoners. A 3 m pit keeps the working rescue. Acceptance test: concept_scenes.py _pit_trap(depth=8) with the FETCH rows: red today (ProofFetchPlan slots=null, no ladder job); green when a ladder job starts at the 4 m pit, a ladder stands at the lip, no held raider leaves the pit, and sc_fetch_fallen (3 m) still passes; plus an offline case in RaiderTrenchChecks for 'attempt at 8 levels, no exit'. Convergent: the locked showcase scene sc_pit_trap_raid already expects it.
  - sweep reading: his card 2026-11-21 picked 'Try, and fall short'; not built: RM_RaiderFetchFallen.cs (last 58cfa254e8, 2026-11-21) returns null when ladders cannot reach, so at 4 m raiders do nothing; the showcase sentence (vision line 5) is unkept
  - its check: at a 4 m prison pit holding a fallen raider, free raiders carry a portable ladder to the edge, it visibly falls short (3 m reach), the fallen stays a prisoner, and the raiders can be driven off
  - files: `src/RimMandrake/FlowWorks/Source/Superdeep/RM_RaiderFetchFallen.cs`

## his words (as recorded on the merged tickets)

- on `RAIDER_CHOP_FIX_AXE_NEVER_LANDS`: They don't carry wood, they look for something to chop down, get the wood, then build it. Destructive. (owner, ladder card 2026-10-23)
- on `RIMMANDRAKE_BUILD_RAIDERS_TRY_SHORT_LADDER_AT_FOUR_METRE_PIT`: Picked: Try, and fall short (Recommended) - card 2026-11-21T19:48:54Z

## verify

Acceptance test: none as one command, the raider behaviour is live; the parity gate and the def names each take an offline check (each merged ticket above names its check).

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: LADDER_PARITY_FIX_RAIDERS_SKIP_LEANING
item: RAIDER_CHOP_FIX_AXE_NEVER_LANDS
item: FLOWWORKS_CLIMBERS_REWIRE_NAMES_THAT_LEFT
item: RIMMANDRAKE_BUILD_RAIDERS_TRY_SHORT_LADDER_AT_FOUR_METRE_PIT
