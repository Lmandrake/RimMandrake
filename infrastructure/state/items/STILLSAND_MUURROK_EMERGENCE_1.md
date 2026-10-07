# STILLSAND_MUURROK_EMERGENCE_1 - Stillsand Muurrok emergence

Filed 2026-10-07 from the GREEN-MIN / L2 sweeps (Transient/*_20261007.md).

## spec
Stillsand `RM_MuurrokEmergence` (src/RimMandrake/Stillsand) sent its letter in the 2026-10-07 GREEN-MIN run but 0 `RM_Muurrok` pawns existed 2600 ticks later. Suspected, UNPROVEN (could be spawn-cell rules, a faction/pawnkind gate, or a harness window too short). Evidence: Transient/green_min_runs2_20261007.md "MOD DEFECT list" 2. Read the incident worker and its spawn path first; decide mod vs harness before changing anything.

## verify
On the smallest tier loading stillsand + creaturebehaviors, force the incident with jawa/fire_incident (dryRun=false), step ticks, count RM_Muurrok via list_pawns/list_things.

## criteria
A1: the cause is established (mod / harness / site) with the evidence line recorded on the item.
A2: after the fix or harness correction, forcing RM_MuurrokEmergence yields >=1 RM_Muurrok within 3000 ticks, with a control case (incident not forced) yielding 0.

## live check
New mechanism never seen: the incident's spawn path has never been seen producing a pawn live.

NEXT: claim this item and start with criterion A1.
