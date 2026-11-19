# CLAUDE.md history — measurements and incident detail moved out of the root CLAUDE.md

The root `CLAUDE.md` holds rules and pointers. When a measurement that goes stale, or the story behind a rule, leaves
it and has no better home (a rulings file, a skill, a lesson), it lands here, under the rule it belongs to. The rule
itself stays in `CLAUDE.md`.

## Facts you cannot guess — how long a cold load takes

Moved 2026-11-19 (Crystallize W47, knowledge merge), because the figure grows with the mod list.

- **A cold load is ~15 minutes on the full list; a quicktest map is ~90 s.** *(MEASURED 2026-09-07, second launch
  of a session; a first launch after a reboot may run slower.)*
- An earlier figure: ~25 minutes on the owner's full list against 22 seconds on a 13-mod minimal list (measured
  2026-08-19; the `rimworld-load-round` skill carries it with its method).
- The rule that stays in `CLAUDE.md`: never "restart and see"; a quicktest map is the cheap instrument.
