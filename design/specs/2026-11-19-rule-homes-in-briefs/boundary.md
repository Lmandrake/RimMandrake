# BOUNDARY: the rule homes that every detached brief and the Designer core name, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/detached_helper.py` (the `RULE_HOMES` line inside `FOOTER`), and the section "Read first:
the rules that live outside CLAUDE.md" of `src/RimMandrake/rimflow/roles/designer.md`. Item:
`RIMMANDRAKE_MOVE_BIOME_FEATURE_JUDGE_RULES_OUT_POINTERS_STAY`, written 2026-11-19. The Conductor accepted three moves
from `design/specs/2026-11-19-plain-english-rule-docs/claude_md_review.md` §Choices for the Conductor: "biome and naming
rules", "feature rules" and "judge rules". `CLAUDE.md` keeps one pointer section for each moved topic. A subagent does
not load `CLAUDE.md`, and a pointer is read only by an agent that searches for it. So the brief of each detached
helper, and the core of each Designer run, names the home file of each moved group. Each promise has a test of its name
in `src/RimMandrake/rimflow/selftest_rule_homes_in_briefs.py`. This page covers only those lines.

## ACCEPTS (the only inputs this is built for)

- **the-footer-format-fields.** `FOOTER.format(clone=, item=, seat=, bound_text=)`, as `launch` calls it. The new line
  adds no field.

## DOES NOT SURVIVE (not promised)

- **a-renamed-home-heading.** A home heading renamed in `standing_rulings.md` or `biome_rulings.md` is caught by the
  test, not by the launch. The launch reads no disk for this line.
- **a-brief-that-is-not-detached.** A run that is not launched by `detached_helper.py` (a window, a subagent, a
  `claude -p` judge call) does not get the line. A judge prompt carries its own rules.

## PROMISES (each one is owed a test of the same name)

- **every-moved-heading-keeps-a-pointer.** `CLAUDE.md` keeps each of the eight moved headings. Each of those sections
  names its home file, and each `§` heading it names exists in that home file.
- **the-silent-costly-lines-stay.** `CLAUDE.md` still holds each line whose breach is silent and costly: the
  `animalDensity` line, the XML-element parse line, the `RM_` twin line, the evictions line, the 1127-line spec line,
  the heat-kind line, the "vanishes without a sign" line, the flight-test line, the "close this hole" line and the
  CALIBRATED line.
- **the-footer-names-each-rule-home.** The formatted `FOOTER` names `design/RimMandrake/biome_rulings.md`,
  `design/RimMandrake/standing_rulings.md`, §The judge refuses flaws, not polish and §A refusal carries its path to
  pass. It names no spend word (`selftest_spend_blind_agents.py` reads the same text).
- **the-designer-core-names-each-rule-home.** `roles/designer.md` names the same two files and each moved heading of
  `standing_rulings.md`.

Later lists beside this page: none yet.
