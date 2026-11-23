# Result: the three kinds of live test are in the rule files

Item `RIMMANDRAKE_ENACT_THREE_TEST_KINDS_FORCED_COUNTED_HUNTED_NOT_STARS_ALIGNED`, 2026-11-23.

## Where the rule is now
- Full text: `design/RimMandrake/standing_rulings.md` §Live tests have three kinds (1c0c69b300; wording 74a20abf7c).
- The Principle of Impactful Evidence: top of `infrastructure/agents/CHARTER.md`; pointer and §A live test declares its
  kind in `CLAUDE.md` (74a20abf7c, 3f90d2fca6).
- Agent and role files (3f90d2fca6): `.claude/agents/rm-testpilot.md`, `.claude/agents/rm-bridge.md`,
  `src/RimMandrake/rimflow/roles/fable_rescue.md`, `src/RimMandrake/rimflow/roles/conductor.md`,
  `src/RimMandrake/rimflow/testpilot_route.py`.
- Skills (ceccc4ac93): `skills/live-debugging-proof-harness/SKILL.md` §The scene contract, with Minimum Force;
  `skills/rimworld-live-review/SKILL.md` §Minimum Force. MandrakeWorkflows be14b66:
  `skills/test-pilot-sitting/SKILL.md` §Minimum Force.
- The in-game driver's brief: `maturation.LIVE_KINDS_RULE` (ceccc4ac93; the brief test was red first).

## Lines that said otherwise (old, then new)
1. standing_rulings §Touching code: "in a visit, every check is re-run on that build" -> "the checks that the fix touches
   run again on that build".
2. Maturation spec Stage 6, Road back: "every check re-run on the fixed build" -> "the checks that the fix touches".
3. `maturation.py` driver brief: "re-run EVERY check on the fixed build (one visit judges one build ... the rows before the
   fix count for nothing)" -> "re-run the checks that the fix touches ... every other row still counts".
4. `maturation.py` comment in read_ingame_exit: "one visit judges ONE build" -> deleted (the next lines said otherwise).
5. `selftest_maturation.py`: the brief test pinned "re-run EVERY check on the fixed build" -> the touched checks.
6. Maturation spec Stage 6, Exit: "Every in-game line item passes" -> a passing verdict that still stands, from any visit;
   no exit asks for every scene in one visit or one scene several times in a row.
7. Maturation spec Stage 6, Road back: a spoiled run was one of three classes -> an ENVIRONMENT FAULT is none of them.
8. standing_rulings §Retest only after a code change: "tested once per code version" -> except kind B budget and hunt steps.
9. Same section: "A flaky chain is reported, not repeated" -> classed by outcome, reported, not repeated.
10. debug_process §3: "Until he or a review says so, coverage grows. Nobody cuts a test for speed." -> a live test earns its
    place. His sentence "We can ablate unnecessary testing later" left with it; it is in git.
11. debug_process Rung 5: "rerun until green" -> one valid run decides; never repeat an unchanged run to get a green.
12. debug_process §4: "intermittent, statistical: none yet" -> kind B scene or kind C hunt.
13. debug_process §8: "intermittent ... defects out of scope" -> only performance.
14. debug_process §Test disturbances: a spoiled row had no outcome -> ENVIRONMENT FAULT only with a record, else UNRESOLVED.
15. focused_testing_plan: "the catalogue of checks stays and keeps growing" -> a check stays while it earns its place.
16. rm-testpilot and `testpilot_route.py`: "Unexplained is not an ending" -> a hunt that stopped unresolved with its record is.
17. CLAUDE.md §How we debug: a check for one fault had no end -> it stays live only while the fault is likely to return.

"Three counted runs in a row" was in no rule file: it stood in briefs and in visit records only (history).

## Not changed on purpose
- `testpilot_route.py` "3 non-pass runs in a row" sends an item to a Test Pilot. It is a route, not an exit.
- `testq/retest.py` refuses a second run on one code version without `--retest-why`: on the ticket.

## Code
`RIMMANDRAKE_TEACH_EXIT_READER_KINDS_KNOWS_THREE_WORDS_ONLY`, acceptance test
`design/specs/2026-11-23-three-test-kinds/accept_exit_reader_kinds.py`: 14 of 16 rows red on the base, 13 after the brief.

## Scenes
`scenes_FlowWorks.md`, `scenes_Pyrelands.md`, `scenes_ExplosiveKnockback.md`, `scenes_GimmeSomeSlack.md`. B is proposed for
one scene (Pyrelands `sc_flamefang_venom`) and for one row (FlowWorks `sc_hung_bridge`, GRATE_fire_burns_people_above).
Pyrelands `sc_burn_compounds` holds an UNRESOLVED run that someone must class.

## The fresh reader
A new Opus agent that did not see the approved text: 10 of 10 acts agree with the rule. Two gaps were repaired in the skill (where X
and Y come from; which item the HUNT OPENED note goes on).

## Untested
- The HUNT OPENED log line was run against a temp log only. No live hunt has used it.
- Nobody has run a live scene under the new wording. The exit reader does not read the outcomes (the ticket).
- The scene tables were read from rows and summaries, not from every evidence file; no second agent read them.
