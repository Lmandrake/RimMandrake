# BOUNDARY: the filled commands in each detached brief (brief_commands.py), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/brief_commands.py` (all of it), `detached_helper.brief_message`, and `build_parser()` of
`src/RimMandrake/rimflow/maturation.py`, `src/RimMandrake/Utils/lessons.py` and `src/RimMandrake/Utils/publish.py`.
Item: `RIMMANDRAKE_FILL_COMMANDS_INTO_BRIEFS_HELP_ASKED_2807_TIMES`. Why: agents asked for help text in 2,807 turns of the
week to 2026-11-23, and the launcher held four hand-written copies of the commands. Each promise has a test of its name
in `src/RimMandrake/rimflow/selftest_brief_commands.py`. Acceptance:
`design/specs/2026-11-23-agent-work-to-code/acceptance/rank3_filled_commands_accept.py`.

## ACCEPTS (the only inputs this is built for)

- **an-item-and-a-seat.** Two non-empty strings. Anything else is a `ValueError`.
- **an-argparse-parser-for-each-tool.** `rimflow` (`cli.py`), `maturation` and `lessons` with subparsers, `publish`
  without. `parsers={"rimflow": ...}` replaces one of them, for a test. The default is each tool's `build_parser()`.

## DOES NOT SURVIVE (not promised)

- **a-clone-on-another-commit.** The lines come from the tools of the clone that launches. A run whose clone is on a
  later commit can have a later parser. The two are seconds apart on origin/main in normal use.
- **a-rule-that-is-not-in-the-parser.** A refusal inside a command's function (a `close` with no `--sha` and no
  `--no-code`) is not seen. The wanted flags of `SPEC` carry those.
- **a-required-group.** A required mutually exclusive group is not read. No tool of `SPEC` has one.
- **a-run-that-is-not-detached.** A window, a subagent and a role run do not get the lines.

## PROMISES (each one is owed a test of the same name)

- **lines-come-from-the-parser.** Each line holds every required positional and every required flag of the parser it is
  made from, at call time. A new required flag shows, with a blank, with no edit of the module. Every flag in a line is
  in the parser.
- **could-not-look-is-said.** A parser that cannot be read, a verb that the parser lost and a wanted flag that the parser
  lost are each named in `could_not_look` and in the text, with the `--help` command to run. The other lines stay.
- **item-and-seat-are-filled.** Each ledger line holds the item and the seat. An empty item or seat is a `ValueError`.
- **judgement-stays-a-blank.** The evidence, the reason, the result, the level, the class and the text are named blanks
  (`"<...>"`), quoted so that a pasted line is one shell command.
- **no-owner-flag.** No line and no list of other flags names `--owner-said`, `--by-card` or `--per-ruling`.
- **no-spend-in-the-text.** The text states no spend, token figure, budget, cap or price. A flag or a help text that does
  is left out.
- **the-text-stays-short.** The text is at most `MAX_CHARS` characters. The help texts of the flags go first, then
  the lists of other flags. A filled line is never cut.
- **every-detached-launch-carries-the-lines.** `detached_helper.brief_message` holds `filled()["text"]`, and
  `_launch_locked` makes its message with it. `FOOTER` holds no second copy of a command that `SPEC` fills.
- **a-launch-never-fails-on-the-lines.** When `filled` raises, the brief still goes out, and it says could not look, with
  the cause and the `--help` command.

## LIMITS

- `MAX_CHARS = 12000`. Danger: the text is read again on every turn of a run (the first load of a run is 83k weighted
  tokens on average, census of 2026-11-23).
- `HELP_CHARS = 300`, the cut of one flag's help. Danger: the same; the help of `cli.py` whole is over 12,000
  characters.

Later lists beside this page: `polish.md`.
