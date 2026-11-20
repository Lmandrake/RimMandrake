#!/usr/bin/env python3
"""selftest: the owner's ruling of 2026-11-19 (about 6:28 PM PST) reaches every fixer, judge and monitor text.

"TOUCHING code has a COST ... the fixer is you unless you can prove you don't have the resources" and, on the same
card, "Stop rule in every judge brief (Recommended)" (item RIMMANDRAKE_ENACT_TOUCHING_CODE_COSTS_SEE_IT_DO_IT;
design/RimMandrake/standing_rulings.md §Touching code has a cost; if you see it, do it).

- PRESENT: each file carries the words of the two tests, or its stopping level.
- ABSENT: the lines that the ruling made false stay deleted (the auditor's "No fixed count", the CHARTER's "File a
  ticket only for a fix that is not small", the agents' "Do not pick up more work.", designer.md's "The Conductor
  cannot supply these" and "first-touch certification stay his").
- The checker is mutated in place on every run: each PRESENT pin dropped from its text, and each ABSENT line planted
  back, must turn the check red; the real texts must stay green.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

RULE = "Touching code has a cost; if you see it, do it"
AGENTS = [".claude/agents/rm-%s.md" % a for a in ("bridge", "builder", "consult", "fixer", "judge", "testpilot")]
AGENT_PINS = [RULE.split(";")[0], "Test 1, before you touch code", "Test 2: when you judge a finding worth the fix",
              "A real chance to void a run is always a yes", "gets no fix and no ticket"]

PRESENT = {
    "CLAUDE.md": ["## " + RULE, "Test 1 comes before you touch code", "Test 2: if you judge a finding worth the fix",
                  "A real chance to void a run is always worth the fix", "`not worth the touch: <why>`",
                  "the polish route, which files no ticket"],
    "design/RimMandrake/standing_rulings.md": [
        "## " + RULE + " — owner, 2026-11-19", "TOUCHING code has a COST",
        "Vital: OF COURSE you do, no debate. Any real chance of voiding a run is catastrophic.",
        "**Test 1, the worth of the touch, asked before the touch.**", "**Test 2, if you see it, do it.**",
        "**Test 1 comes first.**", "RIMMANDRAKE_CALIBRATE_JUDGE_STOP_RULES_WORDS_UNTIL_RUN",
        "Hand off only with the evidence that §" + RULE + " lists"],
    "infrastructure/agents/CHARTER.md": ["**" + RULE + "**", "is its fixer, small or not"],
    ".claude/agents/rm-fixer.md": ["Report `not worth the touch: <why>` to your parent, and stop."],
    ".claude/agents/rm-builder.md": ["Report `not worth the touch: <why>` to your parent."],
    ".claude/agents/rm-judge.md": ["## When the look is enough, and when to stop", "Never a third look",
                                   "You do not fix the work that you judge."],
    "src/RimMandrake/rimflow/roles/auditor.md": ["**When the audit is enough**", "five picks in a row",
                                                 "The danger the count of five guards",
                                                 "A DEFECT is filed only when it passes test 1"],
    "src/RimMandrake/rimflow/roles/operations.md": ["**When an alarm run is enough:**", "`not worth the touch: <why>`",
                                                    "Test 2: if yes, you make the fix in this run, test first."],
    "src/RimMandrake/rimflow/roles/conductor.md": ["carries the two tests", "NOT WORTH THE TOUCH",
                                                   "**Every judging brief that you write states its stopping level**"],
    "src/RimMandrake/rimflow/roles/designer.md": ["§Touching code has a cost; if you see it, do it. File a repair ticket only"
                                                  " when it passes test 1",
                                                  "Only `his_words` is his alone"],
    "src/RimMandrake/Utils/findings_judge_prompt.md": ["`retire` with `--why \"not worth the touch: <why>\"`",
                                                       "Enough: each signature"],
    "design/RimMandrake/scene_look_judge_brief.md": ["## When the look is enough, and when to stop",
                                                     "There is no third look"],
}
for a in AGENTS:
    PRESENT.setdefault(a, []).extend(AGENT_PINS)

ABSENT = {
    "src/RimMandrake/rimflow/roles/auditor.md": ["No fixed count"],
    "infrastructure/agents/CHARTER.md": ["File a ticket only for a fix that is not small."],
    "src/RimMandrake/rimflow/roles/designer.md": ["The Conductor cannot supply these",
                                                  "first-touch certification stay his"],
}
for a in AGENTS:
    ABSENT.setdefault(a, []).append("Do not pick up more work.")


def flat(s):
    return re.sub(r"\s+", " ", s)


def check(texts):
    """-> list of failures over {path: text}; a missing file is a failure by name, never a pass."""
    fails = []
    for path in sorted(set(PRESENT) | set(ABSENT)):
        t = texts.get(path)
        if t is None:
            fails.append("%s: could not read" % path)
            continue
        t = flat(t)
        fails += ["%s lacks %r" % (path, w) for w in PRESENT.get(path, []) if flat(w) not in t]
        fails += ["%s still says %r" % (path, w) for w in ABSENT.get(path, []) if flat(w) in t]
    return fails


def read_all():
    texts = {}
    for path in set(PRESENT) | set(ABSENT):
        try:
            with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
                texts[path] = fh.read()
        except OSError:
            pass
    return texts


def mutants(texts):
    """-> (name, mutated texts) for every pin: each must turn check() red."""
    for path, words in PRESENT.items():
        for w in words:
            m = dict(texts)
            m[path] = flat(m.get(path, "")).replace(flat(w), "")
            yield "drop %r from %s" % (w[:40], path), m
    for path, words in ABSENT.items():
        for w in words:
            m = dict(texts)
            m[path] = m.get(path, "") + "\n" + w + "\n"
            yield "plant %r in %s" % (w[:40], path), m
    m = dict(texts)
    m.pop("CLAUDE.md", None)
    yield "CLAUDE.md unreadable", m


def main():
    texts = read_all()
    fails = check(texts)
    missed = [name for name, m in mutants(texts) if not check(m)] if not fails else []
    pins = sum(len(v) for v in PRESENT.values()) + sum(len(v) for v in ABSENT.values())
    if fails or missed:
        print("FAIL selftest_touching_code_cost_rule: %d failure(s), %d mutant(s) not caught" % (len(fails), len(missed)))
        for f in fails:
            print("  - " + f)
        for f in missed:
            print("  - NOT CAUGHT: " + f)
        return 1
    print("PASS selftest_touching_code_cost_rule: %d pins over %d files; every mutant caught" % (
        pins, len(set(PRESENT) | set(ABSENT))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
