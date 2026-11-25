#!/usr/bin/env python3
"""selftest: the owner's ruling of 2026-11-19 (about 6:28 PM PST) reaches every fixer, judge and monitor text.

"TOUCHING code has a COST ... the fixer is you unless you can prove you don't have the resources" and, on the same
card, "Stop rule in every judge brief (Recommended)" (item RIMMANDRAKE_ENACT_TOUCHING_CODE_COSTS_SEE_IT_DO_IT;
design/RimMandrake/standing_rulings.md §Touching code has a cost; if you see it, do it).

- PRESENT: each file carries the words of the two tests, or its stopping level.
- The extension of 2026-11-20 (a wrong check is repaired or removed in the sitting) is pinned the same way (WRONG).
- ABSENT: the lines that the ruling made false stay deleted (the CHARTER's "File a
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
AGENT_PINS = [RULE.split(";")[0], "Test 1, before you touch code", "Test 2: ",
              "A real chance to void a run is always a yes", "gets no fix and no ticket"]

PRESENT = {
    "CLAUDE.md": ["## " + RULE, "Test 1 comes before you touch code", "Test 2: You are the fixer.",
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

# the extension of 2026-11-20 (RIMMANDRAKE_ENACT_WRONG_CHECK_FIXED_IN_SITTING_NOT_RETURNED): a wrong check is repaired or
# removed in the sitting and never sends the mod back; selftest_wrong_check_fixed_in_sitting.py tests the code
WRONG = {
    "CLAUDE.md": ["Fix a fault in the sitting. Repair or remove a wrong check in the sitting. Neither sends the mod back",
                  "seen to FAIL on a planted fault", "Remove a check that no bar needs from the test table",
                  "one fresh reader, a run that did not make the fix, reads only that fix, once",
                  "Any role that needs the live game to finish a fix does this, a judge included",
                  "records its red run with `maturation.py red-seen` before it closes"],
    "design/RimMandrake/standing_rulings.md": [
        "**A fault is fixed in the sitting; a wrong check is repaired or removed there; neither sends the mod back**",
        "We need to stop treating all agents as corrupt.", "include your extension",
        "judging events are still being used to slowly improve testing definitions rather than game content",
        "The guard that replaces distrust", "How does that help if there's a needless test present?",
        "I agree with your blind judge -> fresh reader argument.", "IT's an unused resource otherwise",
        "These loops are TOO LONG AND SLOW.",
        "**Any role that needs the live game to finish a fix takes it when it is free**"],
    "infrastructure/agents/CHARTER.md": ["A wrong check or scene is repaired in the same sitting",
                                         "or removed from the test table when no bar needs it"],
    "design/specs/2026-11-13-maturation-pipeline.md": ["A wrong check or scene never goes back",
                                                       "a fixed mod owes ONE fresh reader of each fix"],
}
for k, v in WRONG.items():
    PRESENT.setdefault(k, []).extend(v)

ABSENT = {
    "infrastructure/agents/CHARTER.md": ["File a ticket only for a fix that is not small."],
    "src/RimMandrake/rimflow/roles/designer.md": ["The Conductor cannot supply these",
                                                  "first-touch certification stay his"],
}
for a in AGENTS:
    ABSENT.setdefault(a, []).append("Do not pick up more work.")
ABSENT.update({
    "src/RimMandrake/rimflow/maturation.py": ["a check you judge wrong is a note to the",
                                             "files each failed line as a named item"],
    "src/RimMandrake/rimflow/maturation_autonomy.py": ["File EACH failed or UNMEASURED line as a",
                                                      "A failed or UNMEASURED line is filed as a NAMED item"],
    "src/RimMandrake/rimflow/maturation_dispatch.py": ["each failed line item down its road back"],
})
# the follow-up ruling of 2026-11-20 deleted "set aside" for a check no bar needs ("The next judge will hit it again")
for path, words in {"CLAUDE.md": ["A wrong check is repaired or set aside in the sitting"],
                    "design/RimMandrake/standing_rulings.md": ["set it aside as not counted, with one line on the polish"],
                    "infrastructure/agents/CHARTER.md": ["or set aside with one polish line when no bar needs it"],
                    "design/specs/2026-11-13-maturation-pipeline.md": ["it is set aside with one polish line"]}.items():
    ABSENT.setdefault(path, []).extend(words)


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
