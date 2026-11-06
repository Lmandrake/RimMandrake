#!/usr/bin/env python3
"""selftest_prooflint_at_filing.py: PROOFLINT_WIRE_AT_FILING_NOT_AT_RUN.

The live lane refused 146 rows in 3.5 days on checks that need no game (a criterion cut at 160 chars, `$`/backtick/eval,
flyer wording, his ledger), and a line naming a script the tree lacks can only end UNMEASURED. The checks are asked
where a line is written: `rimflow file` / `implemented` / `close` print them, `rimflow lint --proofs <ID>` exits 1 on
them, `finish` refuses them at the finished sha, and the game phase's preflight refuses them before a slot.
1. proof_scripts(): names the scripts a line runs (`python3 x.py`, `python.exe -u x.py`, `./x.sh`, `--plan x.py`,
   `--plan=x.py`, after `&&`/`;`/`|`), and not a redirect target, an absolute or Windows path, `-c` code or a VAR=.
2. missing_scripts(): names only what `has` lacks; None when all are there.
3. lint_lines(): `$`, backtick, eval, brace list, a load, flyer wording, OWNER.jsonl and a missing script each named;
   a literal line with its scripts present is clean; has=None skips the script check.
4. lint_item(): a live clause at the 160-char cap with no prose is named; prose holding the whole line clears it; a
   clause not outstanding, or an L0 one, is not named.
5. preflight(): a missing script is refused (kind "refused") before a slot; a script absent from a lagging books tree
   but present at the built sha is not.
6. finish gate: relentless.proof_text_owed refuses a sha whose proof line names a script the sha lacks, and passes once
   the script is committed (a throwaway git repo).
7. cli: prooflint() reads live_proofs/<ID>.txt under a root and names the bad lines; _prooflint_say prints them and
   never raises; `lint --proofs` is a parser option.
8. Sanity: the lane's own refused_proof still refuses the `$` line, so 3 measures the lane's rule, not a copy.

No ledger, clone or game is touched; temp files under TMPDIR.

    python3 src/RimMandrake/rimflow/selftest_prooflint_at_filing.py
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import relentless_live as L         # noqa: E402

FAILS = []
LR = L.live_rules({})
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


# 1. proof_scripts
ps = L.proof_scripts
ok(ps("python3 src/a/x.py --k v && python.exe -u src/b/y.py --plan src/c/plan.py > /mnt/d/out.txt")
   == ["src/a/x.py", "src/b/y.py", "src/c/plan.py"], "1 python3, python.exe -u, --plan, past &&")
ok(ps("./src/a/run.sh; FOO=1 python3 src/a/z.py --plan=src/c/p.py | tail -3") == ["src/a/run.sh", "src/a/z.py", "src/c/p.py"],
   "1 ./x.sh, VAR= prefix, --plan=, past ; and |")
ok(ps("python3 /mnt/d/ClaudeWork/x.py < src/in.py > src/out.py") == [], "1 absolute script and redirect targets not named")
ok(ps('python3 -c "import src.a"') == [] and ps("python3 -m pytest") == [], "1 -c and -m name no script")
ok(ps("python.exe D:/x/y.py") == [], "1 a Windows path is another tree's")
ok(ps("python3 'unclosed") == [], "1 an unsplittable line names none")
ok(ps("python3 src/a/x.py && python3 src/a/x.py") == ["src/a/x.py"], "1 each script once")

# 2. missing_scripts
have = {"src/a/x.py"}
ok(L.missing_scripts("python3 src/a/x.py", have.__contains__) is None, "2 present script: None")
w = L.missing_scripts("python3 src/a/x.py && python3 src/a/gone.py", have.__contains__)
ok(bool(w) and "src/a/gone.py" in w and "src/a/x.py" not in w, "2 names only the missing one: %r" % w)

# 3. lint_lines
lines = {"A1": "python3 src/a/x.py --at $(date)", "A2": "python3 src/a/x.py `whoami`", "A3": "eval python3 src/a/x.py",
         "A4": "python3 src/a/x.py --{a,b}", "A5": "python3 src/RimMandrake/Utils/modcheck/x.py && modcheck run Foo",
         "A6": "python3 src/a/x.py --pawn flies", "A7": "grep k infrastructure/state/ledger/events/OWNER.jsonl",
         "A8": "python3 src/a/gone.py --k v", "A9": "python3 src/a/x.py --k 'lit$eral'"}
got = dict(L.lint_lines(LR, "a title", lines, have.__contains__))
for cid in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"):
    ok(cid in got, "3 %s named: %s" % (cid, (got.get(cid) or "")[:70]))
ok("A9" not in got, "3 a literal line with its script present is clean")
ok(got.get("A6", "").startswith("flyer:") and got.get("A7", "").startswith("owner act:"), "3 flyer and owner act keep the lane's words")
ok("does not hold" in got.get("A8", ""), "3 the missing script is the NEW check's words")
ok("A8" not in dict(L.lint_lines(LR, "", {"A8": lines["A8"]}, None)), "3 has=None skips the script check")

# 4. lint_item
cut = "x" * L.CUT_AT
item = {"criteria": [{"id": "A1", "level": "L1", "text": cut}, {"id": "A2", "level": "L1", "text": cut},
                     {"id": "A3", "level": "L0", "text": cut}, {"id": "A4", "level": "L2", "text": "short"}],
        "outstanding": ["A1", "A3", "A4"]}
got = dict(L.lint_item(LR, item, "t", {}, None, ""))
ok("A1" in got and "cut at" in got["A1"], "4 an owed live clause at the cap with no prose is named")
ok("A2" not in got and "A3" not in got and "A4" not in got, "4 not outstanding / L0 / short: not named (%s)" % sorted(got))
prose = "- A1 L1: " + cut + " and the rest of the line\n"
ok("A1" not in dict(L.lint_item(LR, item, "t", {}, None, prose)), "4 prose holding the whole line clears it")
ok(dict(L.lint_item(LR, dict(item, outstanding=None), "t", {}, None, "")).keys() >= {"A1", "A2"},
   "4 no ledger state: every live clause read")


# 5. preflight
class Fx(object):
    def __init__(self, books_has, built_has):
        self.books_has, self.built_has = books_has, built_has

    def item(self, _iid):
        return {"id": "I0", "state": "built", "built_sha": "abc123", "title": "t",
                "criteria": [{"id": "A1", "level": "L1", "text": "a clause"}, {"id": "A2", "level": "L1", "text": "b"}],
                "outstanding": ["A1", "A2"]}

    def has_file(self, rel, sha=None):
        return rel in (self.built_has if sha else self.books_has)


L.stale_build, _stale = (lambda fx, sha, iid: (None, [])), L.stale_build
try:
    pl = {"A1": "python3 src/a/gone.py", "A2": "python3 src/a/lag.py"}
    out = L.preflight(Fx(set(), {"src/a/lag.py"}), LR, "I0", pl)
    byc = {o["cid"]: o for o in out}
    ok("A1" in byc and byc["A1"]["kind"] == "refused" and "src/a/gone.py" in byc["A1"]["why"],
       "5 a script missing from books and build is refused before a slot")
    ok("A2" not in byc, "5 absent from a lagging books tree but in the build: not refused")
    ok(bool(byc.get("A1", {}).get("fp")), "5 the refusal carries a fingerprint (the second identical one holds the item)")
finally:
    L.stale_build = _stale


# 6. finish gate on a throwaway repo
def git(repo, *a):
    return subprocess.run(["git", *a], cwd=repo, env=ENV, capture_output=True, text=True, check=True).stdout.strip()


import relentless as RL              # noqa: E402
with tempfile.TemporaryDirectory() as repo:
    git(repo, "init", "-q", "-b", "main")
    os.makedirs(os.path.join(repo, "infrastructure/state/live_proofs"))
    with open(os.path.join(repo, "infrastructure/state/live_proofs/I0.txt"), "w") as f:
        f.write("live-proof A1: python3 src/a/proof.py --k v\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "I0: line")
    sha1 = git(repo, "rev-parse", "HEAD")
    why = RL.proof_text_owed(repo, "I0", sha1, {})
    ok(bool(why) and "src/a/proof.py" in why, "6 finish refuses a sha whose line names a script it lacks: %r" % (why or "")[:90])
    os.makedirs(os.path.join(repo, "src/a"))
    with open(os.path.join(repo, "src/a/proof.py"), "w") as f:
        f.write("print(1)\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "I0: script")
    ok(RL.proof_text_owed(repo, "I0", git(repo, "rev-parse", "HEAD"), {}) is None, "6 the sha holding the script finishes")

# 7. cli
import cli as C                     # noqa: E402
with tempfile.TemporaryDirectory() as root:
    os.makedirs(os.path.join(root, "infrastructure/state/live_proofs"))
    os.makedirs(os.path.join(root, "src/a"))
    open(os.path.join(root, "src/a/x.py"), "w").close()
    with open(os.path.join(root, "infrastructure/state/live_proofs/I0.txt"), "w") as f:
        f.write("live-proof A1: python3 src/a/x.py\nlive-proof A2: python3 src/a/x.py $HOME\n"
                "live-proof A3: python3 src/a/gone.py\n")
    bad = C.prooflint("I0", None, root=root)
    ok(len(bad) == 2 and bad[0].startswith("A2:") and bad[1].startswith("A3:"), "7 prooflint names A2 and A3 only: %r" % bad)
    _real, buf = C.prooflint, io.StringIO()
    C.prooflint = lambda iid, it=None: bad
    with contextlib.redirect_stdout(buf):
        C._prooflint_say("I0", None, "filed")
    ok("live lane would refuse" in buf.getvalue() and "A3:" in buf.getvalue(), "7 _prooflint_say prints the lines")
    C.prooflint, buf = (lambda iid, it=None: 1 / 0), io.StringIO()
    with contextlib.redirect_stdout(buf):
        C._prooflint_say("I0")
    ok("could not run" in buf.getvalue(), "7 a broken lint is said, never raised")
    C.prooflint = _real
with open(C.__file__, encoding="utf-8") as f:
    src = f.read()
ok('"--proofs"' in src and src.count("_prooflint_say(args.id") == 3, "7 `lint --proofs` exists; file, implemented, close call the lint")

# 8. sanity
ok(bool(L.refused_proof(LR, "", "", lines["A1"])), "8 the lane's refused_proof still refuses the `$` line")

print("\n%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
