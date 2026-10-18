# TITANOSLIME_VANISH_DIAGNOSE_GHOST_IN_GRID — BENCH offline pass 2026-10-17

## Status
- [x] read item + gates
- [x] code diagnosis (ilspycmd decompile of LargePawns 0.24.16 + 1.6 Assembly-CSharp)
- [x] fix built (not deployed), gate g8 written (NEVER RUN)
- [x] code review Titanoslime.cs, TitanoslimeProof.cs

## Mechanism
Large Pawns registers a pawn in every cell of a square sized by BodySize at registration and deregisters by the
CURRENT BodySize. Thing.SpawnSetup registers before RM_CompEngulfer.PostSpawnSetup locks the stage, so a lock to a
smaller stage than the generator's random-age roll leaves the outer ring in thingGrid. A dead ghost is skipped by
PawnCollisionTweenerUtility (posture), a vanished one is Standing with pather==null -> NRE. Full text in the item.

## False theories
Huge Things grid; a cached rect in our mod; vanish deregistering differently from kill. See the item.

## Fix / next probe
LockStageReregistering in Titanoslime.cs; ProofGhostScan in TitanoslimeProof.cs; gate g8 in
src/RimMandrake/GelatinousSlime/northstar/titanoslime_gates.py. OWED: deploy mandrake.rm.biomes, run --only g8.

## Review
Both files fully read. Fixed: dead else-branch in ApplyStage (now locks an unlocked same-stage index); misnamed
maxHp (it is a health percent); unguarded parallel-list indexing in the inspect string and DevHeldReport;
ProofFind NRE at the main menu (now ERROR no game). Marked clean after commit.
