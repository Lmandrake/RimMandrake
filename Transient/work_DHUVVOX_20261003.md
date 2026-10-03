# FORGE_DHUVVOX_SWARM_REMAINDER_1 work log (2026-10-03)
- claimed + started. TheForge folder only. Clock already exists (runClock in RM_CompForgeCycleDormancy.cs, RM_DhuvvoxRunSlowing, RM_DhuvvoxNoduleClick, toggle dhuvvoxClockEnabled). No artpipe art needed (no new art).
- DESIGN CALLS (flag for OWNER VETO):
  1. Nodules: KEEP pawn-as-nodule (sealed dhuvvox is drawn as its nodule). Spec words "none vanishes ... persistent nodule" and the criterion "no dhuvvox disappears without a trace" are satisfied by a pawn that never despawns; converting to Things would despawn and respawn pawns, losing hediffs/identity and breaking "curls back where they stand". Not built: nodule Things.
  2. Swarm aggregation: NOT built. No measured performance problem; comp tick is hash-gated at 250 ticks. Instead: a debug log of awake dhuvvox count per map at each wake (data for a later call).
  3. Slowing sound: BUILT. RM_DhuvvoxScuttle (vanilla clip UI/TickHigh), a per-dhuvvox scuttle tick while awake whose gap stretches x4 across the final quarter-hour. New toggle dhuvvoxRunSoundEnabled.
