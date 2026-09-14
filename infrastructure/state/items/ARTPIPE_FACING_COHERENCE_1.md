# ARTPIPE_FACING_COHERENCE_1 — facing sets must actually face

Filed by BENCH 2026-09-14 from the owner's own eyes, five minutes into the first
in-game art walk. Two defects, one root:

1. Every facing job's prompt carries the lawset's "pure flat side profile" with
   NO view direction — so `_north` renders show a face (proved on
   RazorjackArtOverride and ZeerArtOverride norths: both side profiles), and a
   north-walking creature stares at the camera.
2. Each facing is an independent generation — east/north/south drift apart in
   style, so a turning creature flips art styles (owner: "The Furnace Beast is
   showing MANY art styles as it turns").

## Owner ruling, 2026-09-14, verbatim — the acceptance bar

> "You definitely need to have a hook in the art regeneration pass for items
> that have N,S,E,W facing to ensure that N 'faces away from' the camera and S
> 'faces towards' the camera... it's broken everywhere. Write that in the
> graphic ticket: can't call it done until that's true."

**This item is NOT done until every multi-facing set in the pipeline satisfies:
N = rear view (faces away, no face visible), S = front view (faces toward
camera), E = side profile.** The hook is mandatory, not advisory.

## spec

1. **The hook lives in the regeneration pass itself** (`fill_queue.py` /
   `build_job_prompt` territory): any job with a facing MUST get explicit,
   per-facing view language appended mechanically — north: "seen directly from
   behind, rear view, face NOT visible, tail toward viewer"; south: "seen
   head-on from the front, face toward viewer"; east: the existing side
   profile. A facing job the hook has not stamped is refused, the same way the
   canvas ceiling refuses.
2. **Coherence across facings**: north/south generated as DERIVATIONS of the
   accepted east master (editing-images flow — same figure, same palette, same
   keyline weight, rotated view), never as fresh prompts. Style drift between
   facings of one creature is a validator FAIL.
3. **A facing validator** at the gate: reject a `_north` whose face/eye region
   reads as present (heuristic: high similarity to the east profile is the
   cheap first check; a north near-duplicate of east = side-profile clone =
   FAIL).
4. **The backlog is broken everywhere** (owner's words): every multi-facing set
   installed to date fails this bar. Audit installed sets, list the regen debt,
   and burn it down through the fixed pipeline — worst-seen-first (FurnaceBeast
   and the Pyrelands roster are the owner-visible cases).

## verify

- The hook refuses an unstamped facing job (negative test).
- One creature regenerated through the fixed pass shows: north = back of head
  in the PNG, south = face in the PNG, and in game a north-walking pawn shows
  its back. Owner (or a screenshot he accepts) confirms the in-game half.
- Audit list of remaining broken sets exists and shrinks.
