## spec

🔴 **OWNER RULING, 2026-08-21, verbatim:** *"We need to just freeze the world for now
as-is and move on to v1. I have to totally rethink how we create that planet. It's
really messy and horrible compared to what I was hoping for originally."*

Asked as `REFMATCH_CANCELLED_NOT_GATED_1` — whether `refmatch.py` was cancelled or
wanted. He answered something larger than the question, so the ruling is recorded here
in full rather than folded into that item.

## What it decides

1. ⛔ **The world is FROZEN AS-IS for v1.** Planet authoring stops. Not "finish the
   pass then stop" — stop. The map that exists is the v1 map.
2. ⛔ **`refmatch.py` is NOT built for v1.** The 08-20 globe-map acceptance
   (`canon.yml > ORTHO_GLOBE_MAP_ACCEPTED_1`) STANDS; *"I like your new globes"* was
   never a reversal of it. `REFMATCH_THRESHOLDS_CALIBRATE_1` drops.
   🔑 And it is moot twice over now — measuring the current planet against the
   reference photographs buys nothing when the owner is discarding the method that
   produced it.
3. 🔮 **Planet creation is to be RETHOUGHT WHOLESALE — and not now.** He is dissatisfied
   with the result against his original intent. That rethink is post-v1 work.
   ⚠️ **This is NOT a worldgen item and must not become one.** CLAUDE.md's standing
   ruling holds unchanged: there is no worldgen feature in any version, the world is
   hand-made and frozen, and v2 is not a parking space for it. "Rethink how we create
   the planet" means rethinking **the owner's own hand-authoring method**, not building
   a generator.

## What DECIDE does with it

- **Triage every open world/paint/planet item against (1).** Anything whose purpose is
  to improve the map's shape, realism or reference-match is dead for v1 — drop it with
  this ruling as the reason, do not silently leave it `ready`.
  ⚠️ Distinguish **authoring** (dead) from **correctness** — a link CSV emitted
  backwards or a lint excluding the wrong tiles is a defect in an artifact we still
  ship, and those still get fixed.
- **Propagate into the files that say otherwise.** `deciding-and-superseding` applies:
  a doc that still instructs someone to keep painting, or that carries a gate a later
  reader can decide has lifted, is the exact defect this ruling will otherwise repeat.
  Known carriers: `TRANSIENT_upgrade_plan.md` (W7), `canon.yml >
  ORTHO_GLOBE_MAP_ACCEPTED_1`, `CANON_RULINGS_OWED_OWNER_1`'s refmatch gate line.
- 🔑 **Write the rethink down where he will find it, and mark it post-v1.** He will
  come back to this with a method in mind; the record of *what he disliked* is worth
  more then than now. `design/V2_DREAMS.md` is the place, named per the ID convention.

## Not DECIDE's, stated so nobody waits on it

`REFMATCH_THRESHOLDS_CALIBRATE_1` belongs to BUILD and REP was refused when she tried
to drop it — correctly. Either BUILD drops it, or the owner does with `--seat OWNER`.

## verify

- `REFMATCH_THRESHOLDS_CALIBRATE_1` is `dropped`, and `src/RimMandrake/Utils/refmatch.py`
  does not exist.
- No open item's purpose is to improve the planet's shape, realism or reference-match.
- `grep -rn "does not start until the owner has looked" design infrastructure` returns
  nothing — no gate a later reader can decide has lifted.
- `canon.yml > ORTHO_GLOBE_MAP_ACCEPTED_1` carries a line saying the acceptance was
  RE-AFFIRMED 2026-08-21 and the world is frozen, not a superseding line saying it lifted.
- `design/V2_DREAMS.md` carries the rethink, named per the ID convention, marked post-v1
  and explicitly NOT a worldgen item.

## criteria

The world is frozen and every file agrees it is frozen. A seat arriving cold on any
world, paint or planet doc learns from that doc that authoring stopped on 2026-08-21 —
without having to find this item.
