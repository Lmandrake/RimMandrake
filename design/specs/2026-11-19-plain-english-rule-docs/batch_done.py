#!/usr/bin/env python3
"""batch_done.py: the outcome check of one batch (or one session) of the plain-English rewrite.

Item RIMMANDRAKE_LAUNCH_REMAINING_PLAIN_ENGLISH_BATCHES_ELEVEN_LEFT. Plan: batch_plan.md beside this file.

    python3 design/specs/2026-11-19-plain-english-rule-docs/batch_done.py check ITEM PATH... [--need-heading WORD]...
    python3 design/specs/2026-11-19-plain-english-rule-docs/batch_done.py selftest

`check` holds (exit 0) when all of these are true:
  - the result file results/<ITEM>.md exists;
  - the result file has a line `Base: <commit>` (the commit that the batch started from), and git knows the commit;
  - the result file has a heading that contains "meaning read" (step 6 of the plan, the fresh reader);
  - the result file has a heading that contains each --need-heading WORD (for example "calibration");
  - each PATH differs from its text at the base commit (the batch rewrote it);
  - for each PATH, `rule_doc_lint.py keep git:<base>:<PATH> <PATH>` loses nothing. The result file may name the home
    files of moved rules on one line `Also: <path>, <path>`; those go to `keep` as --also.
Exit 1: a condition is false; each false condition is one line. Exit 2: the check could not look (git or the lint tool
did not run). Exit 2 is never a pass and never a fail.
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LINT = os.path.join(HERE, "rule_doc_lint.py")
BASE_RX = re.compile(r"^\s*[-*]?\s*\**Base\**:\**\s*`?([0-9a-f]{7,40})`?", re.I | re.M)
ALSO_RX = re.compile(r"^\s*[-*]?\s*\**Also\**:\**\s*(.+)$", re.I | re.M)
HEAD_RX = re.compile(r"^#{1,6}\s+(.*)$", re.M)


class Blind(Exception):
    """The check could not look."""


def git(root, *args):
    try:
        r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise Blind("git %s did not run: %s" % (" ".join(args), e))
    return r


def check(root, item, paths, need=(), lint=LINT):
    """-> (code, lines). code 0 holds, 1 fails, 2 could not look."""
    bad = []
    res = os.path.join(root, "design/specs/2026-11-19-plain-english-rule-docs/results", item + ".md")
    if not os.path.isfile(res):
        return 1, ["no result file %s" % os.path.relpath(res, root)]
    with open(res, encoding="utf-8", errors="replace") as f:
        text = f.read()
    heads = [h.lower() for h in HEAD_RX.findall(text)]
    for word in ("meaning read",) + tuple(need):
        if not any(word.lower() in h for h in heads):
            bad.append("the result file has no heading with %r" % word)
    m = BASE_RX.search(text)
    if not m:
        bad.append("the result file has no line `Base: <commit>`")
        return 1, bad
    base = m.group(1)
    try:
        r = git(root, "rev-parse", "--verify", "--quiet", base + "^{commit}")
        if r.returncode:
            bad.append("git does not know the base commit %s" % base)
            return 1, bad
        also = []
        a = ALSO_RX.search(text)
        if a:
            also = [p.strip().strip("`") for p in a.group(1).split(",") if p.strip().strip("`")]
        for p in paths:
            old = git(root, "show", "%s:%s" % (base, p))
            if old.returncode:
                bad.append("%s is not in the base commit %s" % (p, base))
                continue
            full = os.path.join(root, p)
            if not os.path.isfile(full):
                bad.append("%s does not exist" % p)
                continue
            with open(full, encoding="utf-8", errors="replace") as f:
                if f.read() == old.stdout:
                    bad.append("%s is the same as at the base commit %s: not rewritten" % (p, base))
                    continue
            argv = [sys.executable, lint, "keep", "git:%s:%s" % (base, p), p]
            for x in also:
                argv += ["--also", x]
            try:
                k = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=300)
            except (OSError, subprocess.TimeoutExpired) as e:
                raise Blind("rule_doc_lint.py keep did not run on %s: %s" % (p, e))
            if k.returncode == 1:
                tail = (k.stdout + k.stderr).strip().splitlines()[-5:]
                bad.append("%s lost spans against %s: %s" % (p, base, " | ".join(tail)))
            elif k.returncode:
                raise Blind("rule_doc_lint.py keep exit %d on %s: %s" % (k.returncode, p, (k.stdout + k.stderr)[-300:]))
    except Blind as e:
        return 2, bad + ["could not look: %s" % e]
    return (1 if bad else 0), bad


def selftest():
    """Planted cases in a temporary git repo. Each case must read as expected."""
    fails = []
    with tempfile.TemporaryDirectory() as d:
        def run(*a):
            subprocess.run(["git", "-C", d] + list(a), check=True, capture_output=True)
        run("init", "-q", "-b", "main")
        run("config", "user.email", "t@t")
        run("config", "user.name", "t")
        os.makedirs(os.path.join(d, "design/specs/2026-11-19-plain-english-rule-docs/results"))
        doc = os.path.join(d, "doc.md")
        old = "- Keep `RM_Thing` at 45 minutes; see `a/b.py` (RIMMANDRAKE_KEEP_THIS_NAME_OR_LOSE_IT).\n"
        with open(doc, "w") as f:
            f.write(old)
        run("add", "doc.md")
        run("commit", "-q", "-m", "base")
        base = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        res = os.path.join(d, "design/specs/2026-11-19-plain-english-rule-docs/results/ITEM.md")

        def case(name, want, new_doc=None, result=None, need=()):
            if new_doc is not None:
                with open(doc, "w") as f:
                    f.write(new_doc)
            if result is None:
                if os.path.exists(res):
                    os.remove(res)
            else:
                with open(res, "w") as f:
                    f.write(result)
            code, lines = check(d, "ITEM", ["doc.md"], need)
            if code != want:
                fails.append("%s: want %d, got %d %s" % (name, want, code, lines))

        good_new = ("- Keep `RM_Thing` at 45 minutes.\n- The code is in `a/b.py`. The item is "
                    "RIMMANDRAKE_KEEP_THIS_NAME_OR_LOSE_IT.\n")
        good_res = "# Result\n\nBase: `%s`\n\n## What the meaning read found\n\nNothing.\n" % base
        case("no result file", 1, good_new, None)
        case("no base line", 1, good_new, "# Result\n\n## Meaning read\n")
        case("unknown base", 1, good_new, good_res.replace(base, "0" * 40))
        case("no meaning read heading", 1, good_new, "# Result\n\nBase: %s\n\n## Scores\n" % base)
        case("file not rewritten", 1, old, good_res)
        case("lost number", 1, good_new.replace("45", "some"), good_res)
        case("lost code span", 1, good_new.replace("`RM_Thing`", "the thing"), good_res)
        case("missing needed heading", 1, good_new, good_res, ("calibration",))
        case("good rewrite", 0, good_new, good_res)
        case("good rewrite with calibration", 0, good_new, good_res + "\n## Calibration\n\nRan.\n", ("calibration",))
        moved = "- Keep `RM_Thing` at 45 minutes.\n- See home.md.\n"
        with open(os.path.join(d, "home.md"), "w") as f:
            f.write("The code is in `a/b.py` (RIMMANDRAKE_KEEP_THIS_NAME_OR_LOSE_IT).\n")
        case("moved rule without Also", 1, moved, good_res)
        case("moved rule with Also", 0, moved, good_res + "\nAlso: `home.md`\n")
    if fails:
        print("RED: %d failed" % len(fails))
        for x in fails:
            print("  " + x)
        return 1
    print("GREEN: 0 failed (12 planted cases)")
    return 0


def main(argv):
    if argv[:1] == ["selftest"]:
        return selftest()
    if len(argv) < 3 or argv[0] != "check":
        print(__doc__)
        return 2
    need, paths, rest = [], [], argv[2:]
    i = 0
    while i < len(rest):
        if rest[i] == "--need-heading" and i + 1 < len(rest):
            need.append(rest[i + 1])
            i += 2
            continue
        paths.append(rest[i])
        i += 1
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    code, lines = check(root, argv[1], paths, need)
    for x in lines:
        print(x)
    print("%s %s" % ({0: "HOLDS", 1: "FAILS", 2: "UNMEASURED"}[code], argv[1]))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
