## spec

Design Version: FlowWorks 0.1.0 (current, a Problem against the locked bars). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks pit rescue: a colonist stranded in a pit reads untrapped, and the rescue picks a spare ladder nobody can reach.

## merged tickets

- `RIMMANDRAKE_FIX_STRANDED_COLONIST_READS_UNTRAPPED_NO_RESCUE` (proposed): A colonist stranded in a sealed 4 m pit reads trapped=False; no rescue queues
  - sweep reading: failure seen live 2026-11-12 (run18, save RM_PitExposure_Review_20261112T032231): colonist in a sealed 4 m pit, trapped=False, cannot leave, no rescue; still true on HEAD: RM_PitAccess.cs:92 needsHelp = downed || IsTrapped, and IsTrapped is captures-only (the same root ee89172bf8 fixed for exposure via HasNoWayOut)
  - its check: a colonist with no way out of a sealed 4 m pit gets a rescue ladder job (selftest: needsHelp reads HasNoWayOut; live: the review save queues a ladder and he walks out)
  - files: `src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitAccess.cs`, `src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs`, `src/RimMandrake/FlowWorks/Source/SelfTest/PitAccessChecks.cs`
- `PIT_RESCUE_FIX_UNREACHABLE_SPARE_LADDER` (proposed): [MINOR] An inaccessible stored ladder can permanently stall automatic pit rescue
  - sweep reading: still true on HEAD: RM_PitAccess.cs:270-285 SparePortable has no reachability check; an unreachable stored ladder stalls auto rescue for good (GPT MINOR, verified)
  - its check: selftest: with the only spare ladder unreachable, SparePortable returns null and the rescue builds a new ladder
  - files: `src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitAccess.cs`, `src/RimMandrake/FlowWorks/Source/SelfTest/PitAccessChecks.cs`

## his words (as recorded on the merged tickets)

- none recorded on these tickets

## verify

Acceptance test: none as one command, each half names a SelfTest case above; neither is written yet.

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: RIMMANDRAKE_FIX_STRANDED_COLONIST_READS_UNTRAPPED_NO_RESCUE
item: PIT_RESCUE_FIX_UNREACHABLE_SPARE_LADDER
