## spec
`design/RimMandrake/standing_rulings.md` §Account and capacity budget (owner 2026-11-20) says: "At an account's soft line
(its line + 2%) no new run starts on it." No program does that. `detached_helper.drain_refusal` refuses only while the
notice has `drain` true, which starts at the line. The allocator's soft notice is advisory.

The concrete case: `lukas` has line 1% and hard line 1% (`max(1, 1 - 2)`). The plan reads soft at 3%, and a new detached
run still starts. At 1% the switch does not wait, because the line is the hard line. The switch kills that run.
`stop_resume.py` brings the run back, but without its prompt cache (the 2026-11-18 stop cost 4.73M weighted for 9 runs).

Measured 2026-11-23: `drain_refusal` with a fresh notice `{"state": "soft", "drain": false, "line": 1, "pct_left": 3}`
returned None.

Decide first whether his 2026-11-02 and 2026-11-04 words (token limits are advisory) leave this refusal out. His words of
2026-11-20 are later. If the refusal stays out, correct the ruling's bullet and `skills/rimflow-operations/SKILL.md` §2.
Keep out of it the soft state that is only a reset lead (`switch_lead_min`) or a reading that cannot prove the line.

## verify
Acceptance test: in `src/RimMandrake/Utils/selftest_switching_plan_drain.py`, a new check
`a-new-launch-waits-at-the-soft-line`: a fresh soft notice with `drain` false and `pct_left` <= `line` + 2 makes
`drain_refusal` return a reason (it returns None today, seen failing as above). The same notice with `pct_left` 20, a
stale notice, an unreadable notice, a continuation and a resume each return None.

## criteria
- A detached run is refused at the soft line, or the ruling bullet and the skill text are corrected to say that none is.
- The new check was seen to fail on the base and passes after the fix.
