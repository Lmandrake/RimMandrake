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

## MEASURED 2026-09-20 — §1's stamp ALREADY EXISTS; what was missing is the refusal

🔴 **Correction to this item's own spec.** §1 asks for a hook that "mechanically
appends explicit per-facing view language". **That half has been built since
2026-09-14** (`PYRELANDS_FACING_REGRESSION_1`): `artpiped.build_job_prompt()` stamps
a full per-facing direction onto every job carrying a `facing` — north *"we see its
BACK, rear haunches and the back of its head. No face, no eyes visible"*, south *"we
see its FACE and chest straight on"*, east/west *"strict side profile with the camera
at the creature's own eye level... NOT a top-down or overhead view"*. Anyone reading
this item and setting out to build the stamp would rebuild what exists.

**The real mechanism, measured over the whole `done/` queue:**

| | |
|---|---|
| jobs carrying a `facing` | **348** |
| jobs with no `facing` at all | 275 |
| 🔴 **jobs where the stamp fired AND the body said "top-down"** | **42** |

So the model was handed the stamp and its contradiction in one prompt and allowed to
choose. The `deeps_*_v2` and `rot_*_v2` families all open *"Top-down pawn sprite,
three facings"* while the stamp underneath says "no face, no eyes". That is the
mechanism behind *"south isn't south, north isn't north"* — **not a missing stamp, a
stamp being argued with**, and no amount of better stamping fixes it.

Separately: **109 of 113 multi-facing job sets were generated from ONE identical
prompt** covering all three facings. That is a risk indicator rather than proof — the
mycoid v2 set came out correct despite it — so art must be MEASURED, never condemned
by its prompt.

## SHIPPED 2026-09-20 — the refusal half of §1

`common.load_job()` now refuses a job that declares a `facing` whose prompt body
contradicts the stamp, naming every offending phrase and what to write instead.
`load_job` is the single chokepoint every route goes through, and it runs *before* a
worker slot is acquired, so a contradicted job can never reach the model or leak a
slot. The escape hatch needs no new field: the gate only fires when a `facing` is
declared, so a genuinely overhead asset — a floor tile, a map icon — simply has none.

Covered by `test_load_job_refuses_a_facing_job_whose_prompt_contradicts_the_stamp`
(8 assertions incl. end-to-end through the daemon). VERIFIED against the live queue:
all 21 queued jobs still load clean, so nothing in flight was broken by the gate.

⚠️ Still open from §2-§4: facings derived from ONE master rather than three
independent prompts; a validator that rejects a `_north` reading as a side-profile
clone; and burning down the installed backlog.

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
