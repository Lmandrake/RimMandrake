#!/usr/bin/env python3
"""Selftest: helpers get their skills by path (item RIMMANDRAKE_NAME_SKILL_PATHS_IN_BRIEFS_AUTOFIRE_IS_OFF).

Owner, 2026-11-19: "since we're not seeming enamored of auto firing skills at the moment, it might be very important to
pass relevant debug skills to the subagents we assign to do related work, yes?" Three checks:

  map         every folder in skills/ with a SKILL.md is named in skills/BY_WORK.md as `skills/<name>/SKILL.md`, and the
              page's registration table says `yes` exactly when .claude/skills/<name> is linked.
  read-first  every path in a "## Read first" list of .claude/agents/rm-*.md or src/RimMandrake/rimflow/roles/*.md exists
              (`~/dev/...` paths expanded; UNMEASURED when ~/dev is not on this machine), and every rm-*.md has one.
  shared      each of them carries .claude/rm_agent_change_block.md too, or (rm-consult, rm-judge) the pointer to it;
              every .claude/agents/rm-*.md carries .claude/rm_agent_shared_block.md verbatim, so the
              block the six agent files share stays one text.

Each check runs on throwaway trees with a planted fault (must go red) before the real tree (must be green).

    python3 src/RimMandrake/Utils/selftest_skills_by_work.py
"""
import glob, os, re, shutil, sys, tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MAP = os.path.join("skills", "BY_WORK.md")
BLOCK = os.path.join(".claude", "rm_agent_shared_block.md")
CHANGE = os.path.join(".claude", "rm_agent_change_block.md")     # the rules of a helper that changes files
NO_CHANGE = ("rm-consult.md", "rm-judge.md")     # they change nothing: they carry POINTER in place of the CHANGE block
POINTER = "First read `.claude/rm_agent_change_block.md`."
AGENTS = os.path.join(".claude", "agents")
ROLES = os.path.join("src", "RimMandrake", "rimflow", "roles")
UNMEASURED_PHRASE = "UNMEASURED, not a pass or a fail"
FAILS, UNMEASURED = [], []


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def skill_folders(root):
    sk = os.path.join(root, "skills")
    return sorted(n for n in os.listdir(sk) if os.path.isfile(os.path.join(sk, n, "SKILL.md")))


def registered_column(text):
    """{name: 'yes'|'no'} from the table under the registration heading."""
    m = re.search(r"^## Every skill folder in this repo.*?$(.*?)(?=^## |\Z)", text, re.S | re.M)
    return dict(re.findall(r"^\|\s*`([\w.-]+)`\s*\|\s*(yes|no)\s*\|", m.group(1), re.M)) if m else {}


def map_problems(root):
    path = os.path.join(root, MAP)
    if not os.path.isfile(path):
        return ["%s is missing" % MAP]
    text = _read(path)
    reg = registered_column(text)
    bad = []
    for n in skill_folders(root):
        if "`skills/%s/SKILL.md`" % n not in text:
            bad.append("%s: not named in %s" % (n, MAP))
        linked = os.path.isfile(os.path.join(root, ".claude", "skills", n, "SKILL.md"))
        want = "yes" if linked else "no"
        if reg.get(n) != want:
            bad.append("%s: registration table says %s, .claude/skills says %s" % (n, reg.get(n, "nothing"), want))
    for n in sorted(set(reg) - set(skill_folders(root))):
        bad.append("%s: in the registration table but no skills/%s/SKILL.md" % (n, n))
    return bad


def read_first_paths(text):
    """The backticked paths in a file's '## Read first' section, or None when it has no such section."""
    m = re.search(r"^## Read first.*?$(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return None
    return re.findall(r"^- `([^`]+)`", m.group(1), re.M)


def read_first_problems(root, home_dev=None):
    """-> (problems, unmeasured). home_dev: where `~/dev/` points (default: the real one)."""
    home_dev = home_dev or os.path.expanduser("~/dev")
    bad, unmeasured = [], []
    files = sorted(glob.glob(os.path.join(root, AGENTS, "rm-*.md"))) + sorted(glob.glob(os.path.join(root, ROLES, "*.md")))
    if not any(os.path.basename(f).startswith("rm-") for f in files):
        bad.append("no agent definitions under %s (blind instrument)" % AGENTS)
    for f in files:
        rel = os.path.relpath(f, root)
        paths = read_first_paths(_read(f))
        if paths is None:
            if os.path.dirname(rel) == AGENTS:
                bad.append("%s: no '## Read first' list" % rel)
            continue
        if not paths:
            bad.append("%s: an empty '## Read first' list" % rel)
        for p in paths:
            if p.startswith("~/dev/"):
                if not os.path.isdir(home_dev):
                    unmeasured.append("%s: %s (~/dev is not on this machine)" % (rel, p))
                elif not os.path.exists(os.path.join(home_dev, p[len("~/dev/"):])):
                    bad.append("%s: %s does not exist" % (rel, p))
            elif not os.path.exists(os.path.join(root, p)):
                bad.append("%s: %s does not exist" % (rel, p))
    return bad, unmeasured


def shared_problems(root):
    blocks = {}
    for rel in (BLOCK, CHANGE):
        src = os.path.join(root, rel)
        if not os.path.isfile(src):
            return ["%s is missing" % rel]
        blocks[rel] = _read(src)
        if len(blocks[rel].splitlines()) < 10:
            return ["%s holds %d lines, not the shared block" % (rel, len(blocks[rel].splitlines()))]
    agents = sorted(glob.glob(os.path.join(root, AGENTS, "rm-*.md")))
    if not agents:
        return ["no agent definitions under %s (blind instrument)" % AGENTS]
    bad = []
    for a in agents:
        rel, text = os.path.relpath(a, root), _read(a)
        if blocks[BLOCK] not in text:
            bad.append("%s: does not carry %s verbatim" % (rel, BLOCK))
        if os.path.basename(a) in NO_CHANGE:
            if POINTER not in text or blocks[CHANGE] in text:
                bad.append("%s: changes nothing, so it carries the pointer to %s and not the block" % (rel, CHANGE))
        elif blocks[CHANGE] not in text:
            bad.append("%s: does not carry %s verbatim" % (rel, CHANGE))
    return bad


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def copy_tree(dst):
    """The parts the three checks read: skills/ (SKILL.md and the map), .claude/skills links, agents, roles, the block."""
    for n in skill_folders(REPO):
        os.makedirs(os.path.join(dst, "skills", n))
        shutil.copy(os.path.join(REPO, "skills", n, "SKILL.md"), os.path.join(dst, "skills", n, "SKILL.md"))
    shutil.copy(os.path.join(REPO, MAP), os.path.join(dst, MAP))
    os.makedirs(os.path.join(dst, ".claude", "skills"))
    for n in os.listdir(os.path.join(REPO, ".claude", "skills")):
        if os.path.isdir(os.path.join(dst, "skills", n)):
            os.symlink(os.path.join("..", "..", "skills", n), os.path.join(dst, ".claude", "skills", n))
    shutil.copytree(os.path.join(REPO, AGENTS), os.path.join(dst, AGENTS))
    shutil.copytree(os.path.join(REPO, ROLES), os.path.join(dst, ROLES))
    os.makedirs(os.path.dirname(os.path.join(dst, BLOCK)), exist_ok=True)
    for rel in (BLOCK, CHANGE):
        shutil.copy(os.path.join(REPO, rel), os.path.join(dst, rel))


def planted(fault):
    tmp = tempfile.mkdtemp(prefix="selftest_skills_by_work_")
    copy_tree(tmp)
    fault(tmp)
    return tmp


def _edit(path, old, new):
    t = _read(path)
    assert old in t, (path, old)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(t.replace(old, new, 1))


def main():
    tmps = []
    try:
        # map: a skill missing from the page, a new folder never mapped, a registration that drifted
        t = planted(lambda r: _edit(os.path.join(r, MAP), "- `skills/telemetry/SKILL.md`: recorded",
                                    "- telemetry: recorded"))
        tmps.append(t)
        _edit(os.path.join(t, MAP), "- `skills/telemetry/SKILL.md`: when", "- telemetry: when")
        check(any("telemetry: not named" in p for p in map_problems(t)), "map: a skill missing from the page is refused")
        t = planted(lambda r: (os.makedirs(os.path.join(r, "skills", "brand-new")),
                               open(os.path.join(r, "skills", "brand-new", "SKILL.md"), "w").close()))
        tmps.append(t)
        check(any("brand-new: not named" in p for p in map_problems(t)), "map: a new skill folder never mapped is refused")
        t = planted(lambda r: os.remove(os.path.join(r, ".claude", "skills", "rimbridge")))
        tmps.append(t)
        check(any("rimbridge: registration table says yes" in p for p in map_problems(t)),
              "map: a registration column that disagrees with .claude/skills is refused")
        # read-first: a dead path in an agent file, an agent file with no list, a dead ~/dev path
        t = planted(lambda r: _edit(os.path.join(r, AGENTS, "rm-fixer.md"), "- `skills/rimworld-deploy/SKILL.md`",
                                    "- `skills/rimworld-deploy-gone/SKILL.md`"))
        tmps.append(t)
        bad, _ = read_first_problems(t)
        check(any("rm-fixer.md: skills/rimworld-deploy-gone/SKILL.md does not exist" in p for p in bad),
              "read-first: a dead path in an agent file is refused")
        t = planted(lambda r: _edit(os.path.join(r, AGENTS, "rm-judge.md"), "## Read first", "## Read later"))
        tmps.append(t)
        bad, _ = read_first_problems(t)
        check(any("rm-judge.md: no '## Read first' list" in p for p in bad), "read-first: an agent file with no list is refused")
        t = planted(lambda r: _edit(os.path.join(r, ROLES, "conductor.md"), "skills/efficient-subagents/SKILL.md",
                                    "skills/efficient-subagents-gone/SKILL.md"))
        tmps.append(t)
        bad, _ = read_first_problems(t)
        check(any("efficient-subagents-gone" in p for p in bad), "read-first: a dead ~/dev path in a role file is refused")
        bad, unm = read_first_problems(t, home_dev=os.path.join(t, "no-dev-here"))
        check(unm and not any("efficient-subagents-gone" in p for p in bad),
              "read-first: with no ~/dev on the machine a ~/dev path is UNMEASURED, never passed or failed")
        # shared: one agent's copy of the block edited, the source edited, the source gone
        t = planted(lambda r: _edit(os.path.join(r, AGENTS, "rm-consult.md"), "Load a skill only when the step needs it, once.",
                                    "Load a skill whenever."))
        tmps.append(t)
        check(shared_problems(t) == ["%s: does not carry %s verbatim" % (os.path.join(AGENTS, "rm-consult.md"), BLOCK)],
              "shared: one agent's edited copy of the block is refused, and only that one")
        t = planted(lambda r: _edit(os.path.join(r, BLOCK), "Load a skill only when", "Load skills only when"))
        tmps.append(t)
        check(len(shared_problems(t)) == 6, "shared: a source edited without its six copies refuses all six")
        t = planted(lambda r: os.remove(os.path.join(r, BLOCK)))
        tmps.append(t)
        check(shared_problems(t) == ["%s is missing" % BLOCK], "shared: a missing source is refused, not passed")
        t = planted(lambda r: _edit(os.path.join(r, CHANGE), "Commit explicit paths only.", "Commit what you like."))
        tmps.append(t)
        check(len(shared_problems(t)) == 4, "shared: an edited change block refuses the four files that carry it")
        t = planted(lambda r: _edit(os.path.join(r, AGENTS, "rm-judge.md"), POINTER, ""))
        tmps.append(t)
        check(shared_problems(t) == ["%s: changes nothing, so it carries the pointer to %s and not the block"
                                     % (os.path.join(AGENTS, "rm-judge.md"), CHANGE)],
              "shared: a helper that changes nothing and lost the pointer is refused")
        t = planted(lambda r: os.remove(os.path.join(r, CHANGE)))
        tmps.append(t)
        check(shared_problems(t) == ["%s is missing" % CHANGE], "shared: a missing change block is refused, not passed")
        # the real tree: must be green
        for name, bad in (("map", map_problems(REPO)), ("shared", shared_problems(REPO))):
            check(not bad, "%s: the real tree is clean%s" % (name, "" if not bad else ": " + "; ".join(bad)))
        bad, unm = read_first_problems(REPO)
        check(not bad, "read-first: the real tree is clean%s" % ("" if not bad else ": " + "; ".join(bad)))
        UNMEASURED.extend(unm)
    finally:
        for t in tmps:
            shutil.rmtree(t, ignore_errors=True)
    if UNMEASURED and not FAILS:
        print("%s: %d ~/dev path(s) could not be checked: %s" % (UNMEASURED_PHRASE, len(UNMEASURED), "; ".join(UNMEASURED)))
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
