# TESTPILOT_FIX_DRAIN_CHECKS_EVERY_SEALED

Blind GPT review F8 of src/RimMandrake/Utils/arena/testpilot.py, probe p_sealed_deadlines. Evidence /mnt/d/ClaudeWork/rimmandrake/arena_testpilot/gpt_blind/ (gpt_round2.md, probes.py, probes_out.txt).

## spec
decide() checked the R3 drain of sealed[0] only, so a newer cheap repair past its 900 s maximum acceptance delay
waited behind an older expensive repair still inside its 3600 s. Fix: every sealed repair's drain is computed with
its own measured cost class; the R3 target is the one whose maximum acceptance delay is most overdue, else the
first whose cheap test budget is spent. The decision's drain record names that repair.

## criteria
- A1 L0: selftest t_drain_every_sealed: expensive repair 1100 s old, cheap repair 1000 s old, valuable tests left: decide returns R3 for the cheap repair (red before: test)
