## spec
Re-filed from UNPROVEN_LIVE_LEGS_TRIAGE_1 (triage of FORGE_ENRICHMENT_QUICKTEST_1 A3 voices and A4 dhuvvox clock,
verdict PARTLY BRIDGE-MEASURABLE NOW, the rest NEEDS A TOOL).
Measurable today with `src/RimMandrake/TheForge/validation.py` on a Forge map (northstar driver, chains voices and
dormancy): `voices.voices_off_no_cue`, `voices.visual_cue_message_names_phase` (the Rain cue only),
`dormancy.dhuvvox_clock_shows_countdown_and_slows`, `dormancy.clock_off_removes_slowing`. These are named as live
proofs on UNPROVEN_LIVE_LEGS_TRIAGE_1 for the supervisor's live round.
Not covered by any component (the reason both legs read `partial` on 2026-10-08):
- A3: a cue for EACH of the four phases (only Rain is read), and "no sustainer survives leaving the map".
  The stinger is audio and never judged; the visual-cue message per phase is the state proxy.
- A4: at window end the dhuvvox SEALS with a dust puff and ONE "curling back" message per map, and the dhuvvox
  count is the same before and after (`jawa/list_things`), i.e. the slowing never removes a pawn.

Build: extend the voices chain to step all four phases reading each phase's CUE_TEXT message, plus a sustainer read
after leaving the map; extend the dormancy chain with `dhuvvox_seals_at_window_end_count_unchanged` (count before /
after, one curling-back message, sealed line in the inspect string).

## criteria
A1 L0: the extended components exist and the mock suite lists them; selftest_theforge green.
A2 L2: live on a Forge map, the extended voices and dormancy rows read PASS, proving FORGE_ENRICHMENT_QUICKTEST_1 A3 and A4.
