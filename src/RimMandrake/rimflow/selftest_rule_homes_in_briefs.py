#!/usr/bin/env python3
"""selftest: the rules moved out of CLAUDE.md (item RIMMANDRAKE_MOVE_BIOME_FEATURE_JUDGE_RULES_OUT_POINTERS_STAY) still
reach their readers. Boundary page: design/specs/2026-11-19-rule-homes-in-briefs/boundary.md; one test per promise.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

import detached_helper as DH  # noqa: E402

BIOME = "design/RimMandrake/biome_rulings.md"
RULINGS = "design/RimMandrake/standing_rulings.md"
# CLAUDE.md heading -> its home file
MOVED = {
    "Biomes, rosters and seas": BIOME,
    "Star Wars style naming is not Star Wars IP": BIOME,
    "In-game LLM access is the Claude Code CLI, never a hosted API key": RULINGS,
    "A pit is a superdeep cell, not a building": RULINGS,
    "One Direct Sun, a pure function of geometry": RULINGS,
    "If it flies in the fiction, it flies in the game": RULINGS,
    "The judge refuses flaws, not polish": RULINGS,
    "A refusal carries its path to pass": RULINGS,
}
RULING_HEADS = ("In-game LLM access", "A pit is a SUPERDEEP cell", "Direct Sun", "If it flies in the fiction",
                "The judge refuses flaws, not polish", "A refusal carries its path to pass")
KEPT = ("Every BiomeDef with a roster sets `animalDensity`", "Parse `<wildAnimals>` and `<wildPlants>` as XML elements",
        "An `RM_` twin biome gets its real cast from patches", "Evictions from a roster are stopped",
        "Do not act on the 1127-line spec", "No biome has its own heat kind, number or exception",
        "No animal or pawn ever vanishes without a sign", "Never live-test a flyer's flight without the owner present",
        'binds only "close this hole"', "Only a refusal from a CALIBRATED brief sends work back")
SPEND = re.compile(r"\b(spend|budget|usd|dollars?|cost|cap)\b|\$\d", re.I)
fails = []


def check(ok, what):
    if not ok:
        fails.append(what)


def read(rel, root=ROOT):
    with open(os.path.join(root, rel), encoding="utf-8") as fh:
        return fh.read()


def flat(text):
    return " ".join(text.split())


def sections(md):
    """{heading: body} of the '## ' sections of md."""
    out, cur = {}, None
    for line in md.split("\n"):
        if line.startswith("## "):
            cur = line[3:].strip()
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def heads(md):
    return [l.lstrip("#").strip() for l in md.split("\n") if l.startswith("#")]


def pointer_errors(claude, homes):
    """-> one line per moved heading that is gone, names no home, or names a § heading its home lacks."""
    errs, secs = [], sections(claude)
    for h, home in MOVED.items():
        body = secs.get(h)
        if body is None:
            errs.append("CLAUDE.md lost the heading '%s'" % h)
            continue
        if home not in body:
            errs.append("'%s' names no %s" % (h, home))
        for m in re.finditer(r"`%s`\s+§([\s\S]+?)(?:\. |\.\n|\.$)" % re.escape(home), body):
            want = flat(m.group(1)).replace('"', "")
            if not any(want in x.replace('"', "") for x in heads(homes[home])):
                errs.append("'%s' points at §%s, which %s lacks" % (h, want, home))
    return errs


def t_every_moved_heading_keeps_a_pointer():
    homes = {BIOME: read(BIOME), RULINGS: read(RULINGS)}
    errs = pointer_errors(read("CLAUDE.md"), homes)
    check(not errs, "every-moved-heading-keeps-a-pointer: %s" % errs)
    # the guard sees a loss: a pointer to a heading the home lacks, and a heading that is gone
    broken = read("CLAUDE.md").replace("§Direct Sun.", "§Indirect Moon.").replace(
        "## A pit is a superdeep cell, not a building\n", "## A pit\n")
    got = pointer_errors(broken, homes)
    check(any("Indirect Moon" in e for e in got) and any("A pit is a superdeep" in e for e in got),
          "every-moved-heading-keeps-a-pointer: the guard missed a planted loss: %s" % got)


def t_the_silent_costly_lines_stay():
    claude = flat(read("CLAUDE.md"))
    gone = [k for k in KEPT if flat(k) not in claude]
    check(not gone, "the-silent-costly-lines-stay: CLAUDE.md lost %s" % gone)


def t_the_footer_names_each_rule_home():
    foot = flat(DH.FOOTER.format(clone="/c", item="SOME_ITEM_X", seat="BENCH", bound_text="no wall-time bound"))
    for want in (BIOME, RULINGS, "§The judge refuses flaws, not polish", "§A refusal carries its path to pass"):
        check(want in foot, "the-footer-names-each-rule-home: the footer does not name %s" % want)
    line = flat(getattr(DH, "RULE_HOMES", ""))
    check(line and line in foot, "the-footer-names-each-rule-home: DH.RULE_HOMES is missing or not in the footer")
    check(not SPEND.search(line), "the-footer-names-each-rule-home: the line names a spend word")


def t_the_designer_core_names_each_rule_home():
    core = flat(read("src/RimMandrake/rimflow/roles/designer.md"))
    for want in (BIOME, RULINGS) + RULING_HEADS:
        check(want in core, "the-designer-core-names-each-rule-home: roles/designer.md does not name %s" % want)


def main():
    for t in (t_every_moved_heading_keeps_a_pointer, t_the_silent_costly_lines_stay,
              t_the_footer_names_each_rule_home, t_the_designer_core_names_each_rule_home):
        t()
    if fails:
        print("FAIL selftest_rule_homes_in_briefs: %d" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("PASS selftest_rule_homes_in_briefs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
