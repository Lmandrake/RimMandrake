# NORTH_STAR_PIT_PILOT_1 — the pit proves the design, or the design is wrong

Filed by BENCH 2026-09-15. Successor to `MOD_VALIDATION_PIT_PILOT_1`, which is
closed `done` having "run it green" — that green is the defect this item exists
to overturn. Design: `design/RimMandrake/north_star_validation_spec.md`.

## Where this stands

- The pit's walk (`design/validation_walks/RimMandrake/Pits.md`) already carries a
  **DRAFT** `## north star` section, drafted 2026-09-15 from the owner's own
  recorded words (his 2026-09-15 "shocked and appalled" statement and his
  2026-09-13 "we need a big dark pit"). 12 must-show lines across five mechanic
  groups, plus one `cannot show` line.
- It is DRAFT, so it binds nothing. That is deliberate and correct.
- The walk's old claim that "nothing here is visual-only" is deleted.

## spec

1. **The owner reads the DRAFT section and validates, edits, or rejects it.**
   This is the step he named as missing: *"I validate checklist before it's fully
   filed."* ~5 minutes. Everything else waits on it and nothing else needs him.
   His `### the experience` prose is quoted rather than authored — if the quotes
   do not say what he means, his own statement replaces them.
2. `modcheck validate Pits --owner-said "<his words>"` records the hash.
3. **Wire `shows=` into `src/RimMandrake/Pits/validation.py`**, mapping each
   validated must-show id onto the component whose screenshot is evidence for it.
   Expect some lines to have NO natural component — that is a finding, not a
   problem to paper over: it means the suite never looks at that part of the
   experience, which is the whole discovery.
4. **Run it and expect it to fail.** See below.

## verify — this is the falsification test for the whole design

```
PROVE   Pits moves off GREEN once its checklist is VALIDATED
EXPECT  first REFUSED on the visual floor (validated lines no component claims),
        then RED on the judge once components claim them — specifically NO on
        `pit_occupant_below_floor` and `pit_reads_as_hole` against the current
        64px vanilla TrapSpikeArmed placeholder with a pawn drawn standing on it
LIES    a GREEN Pits after validation; a judge returning YES on
        `pit_occupant_below_floor` against today's art; any run that passes every
        line on its first outing
```

⚠️ **A first run that passes everything is the most likely sign the bar was
written to be passed.** Check the pit first precisely because the answer is
already known: the owner looked at it and rejected it, so the correct verdict is
not in doubt. A system that cannot reproduce his judgement here will not be
trusted anywhere else.

## criteria

Either the pit is RED/REFUSED with the judge's reasons matching what the owner
said when he looked at it — in which case the design works and
`NORTH_STAR_WALK_AUTHORING_1` can proceed — or it is GREEN, in which case the
design has failed its own test and needs rework before any of the 77 walks are
authored.

## not chasing

Fixing the pit's art. That was `PIT_TRAP_VISUAL_REDESIGN_1`, superseded
2026-09-19 by `PIT_SUPERDEEP_COLLAPSE_1` — a pit is now ruled a SUPERDEEP
excavated cell, not a trap with covered/sprung/occupied states, and the
four-depth legibility question that item still owed is answered there by
ruling 33 (the depth read comes from the wall faces, not the occupant). This
item proves the *validation* catches the defect; it does not repair it.

## Watch out

- Needs the bridge and a live game for step 4 — not runnable from the Mac.
- `NORTH_STAR_RUNNER_WIRING_1` must land first: the modules exist but `runner.py`
  does not consult them yet, so a run today would still report the old GREEN.
- Two of the pit's toggles have no covering component at all (noted in
  `Pits/validation.py`'s own header). The visual floor will not report those —
  that is the settings floor's job, and it is a separate pre-existing gap.
