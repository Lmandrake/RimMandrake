# BOUNDARY: the footer of a detached brief passes the guiding-prose check, Design Version 0.1.0

Code: the footer text that `src/RimMandrake/rimflow/detached_helper.py` `brief_message` adds after the item packet:
`FOOTER`, `RULE_HOMES`, `SLIM_LINE`, the fixer statement of `src/RimMandrake/rimflow/fixer_rule.py`, the brief line of
`src/RimMandrake/rimflow/form_fault.py`, and the command lines of `src/RimMandrake/rimflow/brief_commands.py` (made from
the help texts of `src/RimMandrake/rimflow/cli.py`, `maturation.py`, `src/RimMandrake/Utils/lessons.py` and
`publish.py`). Item: `RIMMANDRAKE_REWRITE_BRIEF_TEXT_INSIDE_CODE_FOURTEEN_MODULES`. Each promise has a test of its name
in `src/RimMandrake/rimflow/selftest_footer_prose.py`.

Every detached helper reads this footer. The launch check of `design/specs/2026-11-23-guiding-prose-check/boundary.md`
reads a brief before `brief_message` adds the footer. So this test is the only reader of the footer. On 2026-11-26 the
program half of the check read 17 faults in the footer.

## ACCEPTS (the only inputs this is built for)

- **the-footer-as-a-launch-writes-it.** The footer for a filed item, seat `BENCH`, a slim clone, with and without a
  wall-time bound, and no card work. The card work (`card_footer`) is the item's own data, not text of this code.

## DOES NOT SURVIVE (not promised)

- **a-term-only-a-model-can-see.** The test runs the program half only (no model reader). A coined term made of
  ordinary words passes it.
- **the-other-thirteen-modules.** `design/specs/2026-11-19-plain-english-rule-docs/batch_plan.md` §Text inside code
  names 14 modules that build brief text. The other 13 build briefs that `detached_helper.py launch` reads with the
  launch check, which keeps a record of each launch.

## LIMITS (each names the danger that it guards and the evidence)

None.

## PROMISES (each one is owed a test of the same name)

- **the-footer-reads-no-program-fault.** The footer, with and without a wall-time bound, gives no fault of the program
  half of `src/RimMandrake/Utils/guiding_prose.py`, on more than 30 sentences.
- **a-planted-fault-is-seen.** The same footer with one planted sentence that opens with a bare pronoun gives a
  `pronoun` fault. The test exits 3 (UNMEASURED), never 0, when the STE lint `clarify.py` cannot be loaded.
