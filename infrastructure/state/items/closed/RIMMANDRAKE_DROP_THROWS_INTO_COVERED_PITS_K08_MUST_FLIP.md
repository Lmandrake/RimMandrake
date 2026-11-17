# RIMMANDRAKE_DROP_THROWS_INTO_COVERED_PITS_K08_MUST_FLIP

ExplosiveKnockback 0.1.0, bar `thrown_into_pit_falls`, blind cycle 5 Problem PENDING (judge-1794890427). Replaces
RIMMANDRAKE_STOP_THROWS_OVER_COVERED_PITS_K08_SAYS_GROUND (filed by the judge under its own item, so the Dispatch road
back could not see it); the mod-ledger finding keeps that old id as its subject: claim it fixed under that subject.

## spec

The kernel treats a covered pit cell as ground: `RM_KnockbackMath.Resolve` lets a throw planned beyond a covered pit fly
over it, and `LandingBreaksCover` excludes pawns, so a blast-thrown colonist never breaks a cover. The locked scene
`sc_pit_fall` (scenes.json) says: "on the covered cell the colonist and the stack fall through, one descent each, and the
cover is broken". The scene text stands; the code changes to match it (trap `the-scene-text-stands-and-the-code-must`).

Smallest fix (design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_5/lane2/faults.json):
- `RM_KnockbackMath.Resolve`: a CoveredPit cell stops the throw IN it when `intoPits` (a wall when off), as an open pit.
- `LandingBreaksCover`: drop the Pawn exclusion for blast ids (id >= 0); a gas shove (negative id) still never breaks one.
- `RM_MapComponent_Knockback.ThrowPawn` remembers the explosion id per pawn; `RM_Patch_PawnFlyer_KnockbackLanding`
  breaks the cover under a landed pawn through `RM_KnockbackCompat.BreakCoverUnder` when that id >= 0.
- K-08 in `Source/SelfTest/Program.cs` ("cover is ground") becomes "a throw over a cover ends in it". This flips a
  builder assertion: list it in the cycle's tests_edited.json with the reason (it follows the locked scene sc_pit_fall),
  so the next blind judge sees it.
- `RM_KnockbackProof` `pit_colonist` gains the covered lane, the planned-beyond-the-rim assertion and the filled-pit
  control as sc_pit_fall writes them.
- Rebuild release and proof DLLs (`winbuild.py`) with their `.srchash`.

Unchanged by this fix: gas bursts never break pit covers (his earlier answer, trap `gas-bursts-never-break-pit-covers`).

## refs
file: src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackMath.cs
file: src/RimMandrake/ExplosiveKnockback/Source/SelfTest/Program.cs
file: src/RimMandrake/ExplosiveKnockback/Source/RM_MapComponent_Knockback.cs
file: src/RimMandrake/ExplosiveKnockback/Source/RM_PawnFlyerPatches.cs
file: src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs

## criteria

Acceptance test: `python3 design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_5/lane2/accept_covered_pit.py`
-> rc 0, "covered pit acceptance: 6 of 6". Watched failing on 10abd71ff0 (2026-11-16 22:15 PST, steward run): rc 1, 2 of 6
(A1-A4 FAIL, A5 and A6 hold). T_KERNEL stays green with K-08 flipped. Live half, UNRUN until
Stage 6: sc_pit_fall's covered lane.

## verify

Rerun the acceptance test (rc 0, 6 of 6), `python3 src/RimMandrake/Utils/run_selftests.py --only` the kernel suite
(T_KERNEL) and the cycle-5 `lane2/check_pit_pawn.py` (still 6 of 6: K-25 must not regress).

## launch-checks
must-fail: python3 design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_5/lane2/accept_covered_pit.py
