#!/usr/bin/env python3
"""selftest_relentless_reach_shell_aware.py - REACH_GATE_HARDEN_PARENS_HIDE_THE_TOOL: the reach gate reads a proof the way
the shell will run it, so its prose filters cannot hide what a Marker would run (GPT full-file review, 2026-11-05).

(P) a parenthesised group that starts with a program is a subshell and stays: `(git log -1)`,
    `(python3 code_review_since.py ...)`; a prose aside still goes.
(C) `#` opens a comment only at a word's start outside quotes: a quoted `#` hides nothing, `true;# x` is a comment.
(V) `$VAR` is read with the env at the point of use: a later assignment, a command-local `X=1 tool` and a subshell's
    assignment never reach it; an `export` or a plain assignment before it does.
A fixture walls profile denies /secret and sets ROOT=/secret in the box's env.
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_reach as RR           # noqa: E402

FAILS = []
PROF = {"deny": ["/secret"], "env": {"ROOT": "/secret"}}
GIT_TOOLS = [("src/RimMandrake/Utils/code_review_since.py", "merge-base")]
HIDDEN = ["hidden path: /secret/x"]


def ok(cond, name, got=None):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond or got is None else "  got %r" % (got,)))
    if not cond:
        FAILS.append(name)


def needs(t, **kw):
    return RR.needs(t, PROF, serve=(), **kw)


def t_parens():
    g = needs("(python3 code_review_since.py --after HEAD~1 x.py)", git_tools=GIT_TOOLS)
    ok(any("code_review_since.py" in x for x in g), "P1 a subshell running a git tool stays a git need", g)
    g = needs("(git log -1)")
    ok(any("git log" in x for x in g), "P2 `(git log -1)` is a git need", g)
    ok(needs("(./run.sh /secret/x)") == HIDDEN, "P3 a subshell running a script keeps its path", needs("(./run.sh /secret/x)"))
    ok(needs("(X=1 cat /secret/x)") == HIDDEN, "P4 a subshell with a command environment is a command")
    ok(needs("python3 x.py (the retry cases read /secret/x and prove a dotnet.exe launch)") == [],
       "P5 a prose aside still goes", needs("python3 x.py (the retry cases read /secret/x and prove a dotnet.exe launch)"))
    ok(needs("diff <(cat /secret/x) y") == HIDDEN, "P6 a process substitution is a command")
    ok(needs("x (see (git log -1) for it)") and needs("x (see the log for it)") == [],
       "P7 a group around a subshell stays; nested prose goes")


def t_comments():
    t = "printf ' # label'; python3 code_review_since.py --after HEAD~1 x.py"
    ok(needs(t, git_tools=GIT_TOOLS), "C1 a quoted # truncates nothing", needs(t, git_tools=GIT_TOOLS))
    ok(needs('echo "a # b" && cat /secret/x') == HIDDEN, "C2 a double-quoted # truncates nothing")
    ok(needs("true;# code_review_since.py", git_tools=GIT_TOOLS) == [], "C3 `;#` opens a comment",
       needs("true;# code_review_since.py", git_tools=GIT_TOOLS))
    ok(needs("true &&# cat /secret/x") == [], "C4 `&&#` opens a comment")
    ok(needs("grep -c x#y /secret/x") == HIDDEN, "C5 a # inside a word is no comment")
    ok(needs(r"echo \# && cat /secret/x") == HIDDEN, "C6 an escaped # is no comment")
    ok(needs("python3 x.py  # reads /secret/x\ncat /secret/x") == HIDDEN, "C7 a comment ends at its line")
    ok(needs("echo $# /secret/x") == HIDDEN, "C8 `$#` is a variable, not a comment")
    ok(RR.strip_comments("a 'b # c\n# d") == "a 'b # c\n# d", "C9 an unclosed quote keeps the rest (can only add a need)")


def t_vars():
    ok(needs('cat "$ROOT/x"; ROOT=/tmp') == HIDDEN, "V1 a later assignment does not reach back",
       needs('cat "$ROOT/x"; ROOT=/tmp'))
    ok(needs('ROOT=/tmp cat "$ROOT/x"') == HIDDEN, "V2 a command-local assignment is not seen by its own args")
    ok(needs('ROOT=/tmp true && cat "$ROOT/x"') == HIDDEN, "V3 a command-local assignment does not persist")
    ok(needs('(ROOT=/tmp); cat "$ROOT/x"') == HIDDEN, "V4 a subshell's assignment does not leak out")
    ok(needs('x=$(ROOT=/tmp; echo); cat "$ROOT/x"') == HIDDEN, "V5 a command substitution's assignment does not leak out")
    ok(needs('ROOT=/tmp; cat "$ROOT/x"') == [], "V6 a plain assignment before the use is seen", needs('ROOT=/tmp; cat "$ROOT/x"'))
    ok(needs('export ROOT=/tmp && cat "$ROOT/x"') == [], "V7 an export before the use is seen")
    ok(needs("bash -lc 'ROOT=/tmp; cat $ROOT/x'") == [], "V8 an inner shell's assignment is seen by that shell")
    ok(needs('ROOT=/tmp B=$ROOT; cat $B/x') == [], "V9 assignments chain left to right", needs('ROOT=/tmp B=$ROOT; cat $B/x'))
    ok(needs('(ROOT=/tmp; cat "$ROOT/x")') == [], "V10 inside the subshell its own assignment holds")
    ok(needs('cat ${ROOT}/x') == HIDDEN, "V11 the box's env is the start")


def t_review_two():
    """GPT's second full-file review (2026-11-06): each of these read [] before its fix."""
    hid = lambda t: "hidden path: /secret/x" in needs(t)                     # noqa: E731
    ok(hid('ROOT=$(cat "$ROOT/x")'), "R1 a substitution's RHS reads the old value")
    ok(hid("printf '%s\\n' 'x; ROOT=/tmp;'; cat \"$ROOT/x\""), "R2 quoted text is no assignment")
    ok(hid('false && ROOT=/tmp; cat "$ROOT/x"'), "R3 a skippable assignment keeps the old value too")
    ok(needs('true && ROOT=/tmp; cat "$ROOT/y"') == ["hidden path: /secret/y"], "R3b ... and the new one is checked too")
    ok(hid('ROOT=/tmp | true; cat "$ROOT/x"'), "R4 a pipeline's assignment does not persist")
    ok(hid("bash -c 'ROOT=/tmp'; cat \"$ROOT/x\""), "R4b an inner shell's assignment does not escape it")
    ok(needs('echo "$(printf " # "; ssh host)"'), "R5 a # quoted inside $(...) inside quotes is no comment")
    ok(hid("(tar -cf /tmp/archive.tar /secret/x)"), "R6 an unlisted program with a flag is a subshell")
    ok(needs("/usr/bin/ssh host true"), "R7 a qualified ssh")
    ok(needs("/usr/bin/git log -1"), "R7b a qualified git")
    ok(needs("if ssh host true; then :; fi"), "R7c a command after `if`")
    ok(hid('cat /sec""ret/x'), "R8 quote concatenation")
    ok(needs("cat /tmp/../secret/x") == ["hidden path: /tmp/../secret/x"], "R9 a `..` path resolves before the wall check")
    ok(needs("git ls-remote origin"), "R10 an unlisted git verb")
    ok(RR.needs("git ls-remote origin", PROF, serve=("git_history",)), "R10b ls-remote needs a remote with history served")
    ok(RR.needs("git show origin/main", PROF, serve=("git_history",)), "R11 a ref argument with history served")
    ok(RR.needs("git log --all", PROF, serve=("git_history",)), "R11b --all with history served")
    ok(not RR.needs("git log -1 -- main.py && git diff HEAD~1", PROF, serve=("git_history",)),
       "R11c HEAD ancestry and a file named main.py are served")
    ok(needs("git init /tmp/fx && true") == [], "R10c `git init` needs no history")
    ok(needs("x.py (git clones the tree)") == [], "R10d a word after git that is no git command is prose")
    broken = sorted(v for v in RR._GIT_VERBS if v.endswith("-") or not re.fullmatch(r"[a-z][a-z-]*", v))
    ok(not broken and {"for-each-ref", "commit-graph", "name-rev"} <= RR._GIT_VERBS,
       "R10e the git verb list holds whole hyphenated names (a wrapped line once split for-each-ref)", broken)


def t_review_three():
    """GPT's third full-file review (2026-11-06): each of these read wrong before its fix."""
    hid = lambda t: "hidden path: /secret/x" in needs(t)                     # noqa: E731
    ok(hid('if false; then ROOT=/tmp; fi; cat "$ROOT/x"'), "T1 an assignment after `then` may not run")
    home = RR.relentless_wall.HOME
    kids = {"deny_children": [home + "/rm"], "env": {}}
    ok(RR.needs('cat "${HOME}/rm/relentless/store/journal.jsonl"', kids, serve=()) != [], "T2 ${HOME} is home too")
    ok(RR.needs("cat %s/rm/*/README.md" % home, kids, serve=()) != [], "T3 a glob under a deny_children root is hidden")
    ok(RR.needs("cat %s/rmx/*/README.md /tmp/*.txt" % home, kids, serve=()) == [], "T3b a glob elsewhere is not")
    ok(needs("timeout --kill-after=5s 30s ssh host true") != [], "T4 timeout's options do not hide the program")
    ok(needs("timeout -k 5 30 ssh host true") != [], "T4b nor a split option")
    git = lambda t: RR.needs(t, PROF, serve=("git_history",))                # noqa: E731
    ok(git("git show v1.0.0 -- README.md") != [], "T5 a tag revision is a ref need")
    ok(git("git log --all-match --grep=reach --grep=gate -n 1 HEAD") == [], "T6 --all-match is not --all")
    ok(git("git log --all -n 1") != [], "T6b --all still is")
    ok(needs("git diff --no-index /tmp/a.json /tmp/b.json") == [], "T7 diff --no-index reads no .git")
    ok(needs("git diff HEAD~1") != [], "T7b a plain diff still does")


def t_review_four():
    """GPT's fourth full-file review (2026-11-06)."""
    ok(needs("bash -c 'ROOT=/tmp; cat \"$ROOT/y\"'; cat \"$ROOT/x\"") == ["hidden path: /secret/x"],
       "F1 an inner shell's closing quote ends its scope", needs("bash -c 'ROOT=/tmp; cat \"$ROOT/y\"'; cat \"$ROOT/x\""))
    git = lambda t: RR.needs(t, PROF, serve=("git_history",))                # noqa: E731
    ok(git("git log HEAD..origin/main --oneline") != [], "F2 a range's far end is a ref")
    ok(git('git diff "main...HEAD" --stat') != [], "F2b a quoted range too")
    ok(git("git log -n 3 --oneline HEAD~2..HEAD") == [], "F2c a HEAD-only range is none")
    exe = needs('"/mnt/c/Program Files/dotnet/dotnet.exe" --info')
    ok(any(x.startswith("a Windows program") for x in exe), "F3 a quoted .exe path with spaces", exe)
    ok(needs('echo "run dotnet.exe later"') == [], "F3b an .exe named inside an echo is no program")


def t_review_five():
    """GPT's fifth full-file review (2026-11-06): the outer shell expands a double-quoted script before it runs."""
    dq = needs('bash -c "ROOT=/tmp; cat $ROOT/x"')
    ok(dq == ["hidden path: /secret/x"], "V1 a double-quoted script's $VAR is the outer value", dq)
    sq = needs("bash -c 'ROOT=/tmp; cat $ROOT/x'")
    ok(sq == [], "V1b a single-quoted script's $VAR is the inner value", sq)


def t_review_six():
    """GPT's sixth full-file review (2026-11-06): reading a git tool is not running it; a search value and a pathspec name no ref."""
    tool = lambda t: needs(t, git_tools=GIT_TOOLS)                           # noqa: E731
    for read in ("grep -q merge-base src/RimMandrake/Utils/code_review_since.py", "test -f code_review_since.py",
                 "python3 code_review_status.py check src/RimMandrake/Utils/code_review_since.py",
                 "git_free=1 cat code_review_since.py"):
        ok(tool(read) == [], "S1 reading the tool is no need: " + read, tool(read))
    for run in ("python3 src/RimMandrake/Utils/code_review_since.py --after a x.py", "python3 -u code_review_since.py",
                "true && ./code_review_since.py", "A=1 timeout 60 python3 code_review_since.py", "grep -q x y | python3 code_review_since.py",
                "bash -c 'python3 code_review_since.py'"):
        ok(tool(run) != [], "S1b running it is: " + run, tool(run))
    git = lambda t: RR.needs(t, PROF, serve=("git_history",))                # noqa: E731
    for fine in ("git log -1 HEAD --grep='origin/main'", 'git log --grep "origin/main" -1', "git log -1 --format='%H main'",
                 "git diff HEAD~1 -- src/refs/config.py", "git log -1 -- origin/x.py", "git log -S'refs/heads' -1"):
        ok(git(fine) == [], "S2 no ref: " + fine, git(fine))
    for ref in ("git log --grep=x origin/main", "git diff origin/main -- src/x.py", "git log --all --format=%H"):
        ok(git(ref) != [], "S2b a ref: " + ref, git(ref))


def t_review_seven():
    """GPT's seventh full-file review (2026-11-06): a command-local assignment before a substitution stays command-local."""
    h = needs('ROOT=/tmp P=$(pwd) python3 run.py && test -f "$ROOT/x"')
    ok(h == ["hidden path: /secret/x"], "W1 `$(...)` does not make the prefix persist", h)
    b = needs('ROOT=/tmp P=`pwd` python3 run.py && test -f "$ROOT/x"')
    ok(b == ["hidden path: /secret/x"], "W1b nor do backticks", b)
    ok(needs('ROOT=/tmp; P=$(pwd) python3 run.py && test -f "$ROOT/x"') == [], "W2 a real assignment before it still persists")


def main():
    t_parens()
    t_comments()
    t_vars()
    t_review_two()
    t_review_three()
    t_review_four()
    t_review_five()
    t_review_six()
    t_review_seven()
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
