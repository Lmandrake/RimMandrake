#!/usr/bin/env python3
"""Selftest for polish_door.py, the ./publish block on a helper's polish line about its own changed file.

    python3 src/RimMandrake/Utils/selftest_polish_door.py

Red on a planted line (a helper run adds a polish line that names a file it changed, with no `risk:` part); green on a
line that names an unchanged file, on a line with a `risk:` part, and on a run that is not a helper's. The last case
drives publish.publish() on a throwaway bare repo, so the block is seen at the real door.
"""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_door as D  # noqa: E402
import publish as P  # noqa: E402

os.makedirs(os.path.expanduser("~/.cache/publish-selftest"), exist_ok=True)
P.RM_ROOT = os.environ["PUBLISH_RM_ROOT"] = tempfile.mkdtemp(prefix="lockroot-",
                                                             dir=os.path.expanduser("~/.cache/publish-selftest"))
__import__("atexit").register(shutil.rmtree, P.RM_ROOT, True)
ROOT = os.path.expanduser("~/.cache/publish-selftest")
os.environ.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                   "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null"})
FAILS = []
POLISH = "design/specs/x-part/polish.md"
CODE = "src/tool/x_part.py"
OTHER = "src/tool/y_part.py"


def chk(ok, what):
    print("%s %s" % ("PASS" if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


def sh(cwd, *a):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, timeout=120)  # hang guard; a git call takes <1 s
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr))
    return r.stdout.strip()


def write(repo, path, text):
    full = os.path.join(repo, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(text)


def world():
    d = tempfile.mkdtemp(dir=ROOT)
    bare, a = os.path.join(d, "bare.git"), os.path.join(d, "a")
    sh(d, "init", "-q", "--bare", "-b", "main", bare)
    sh(d, "clone", "-q", bare, a)
    write(a, CODE, "x = 1\n")
    write(a, OTHER, "y = 1\n")
    write(a, POLISH, "# POLISH\n\n- an old line about `x_part.py` stays as it was.\n")
    sh(a, "add", CODE, OTHER, POLISH)
    sh(a, "commit", "-q", "-m", "seed")
    sh(a, "push", "-q", "origin", "HEAD:main")
    return d, a


def run_commit(a, line, code=CODE):
    """One local commit of a run: a change to `code` and one new polish line."""
    write(a, code, open(os.path.join(a, code)).read() + "z = 2\n")
    with open(os.path.join(a, POLISH), "a") as f:
        f.write(line + "\n")
    sh(a, "commit", "-q", "-m", "run", "--", code, POLISH)


def t_a_helper_line_on_its_own_changed_file_is_returned():
    changed = [CODE, POLISH]
    own = [(POLISH, "- `x_part.py` reads the list twice.")]
    chk(len(D.returned(own, changed)) == 1, "pure: a line naming a changed file, no risk part, is returned")
    chk(D.returned([(POLISH, "- `src/tool/x_part.py` reads the list twice.")], changed) != [],
        "pure: a line naming the changed file by its repo path is returned")
    chk(D.returned([(POLISH, "- `y_part.py` reads the list twice.")], changed) == [],
        "pure: a line naming an unchanged file passes")
    chk(D.returned([(POLISH, "- `x_part.py` reads twice. risk: a second read changes the order the tick sees.")],
                   changed) == [], "pure: a line with a risk part passes")
    chk(D.returned([(POLISH, "- `xx_part.py` reads the list twice.")], changed) == [],
        "pure: a longer name that only ends in the changed file's name is not that file")
    chk(D.returned([(POLISH, "- the tick reads the list twice.")], changed) == [],
        "pure: a line that names no file passes")


def t_the_door_reads_only_the_runs_own_commits():
    os.environ["RM_ROLE_UNIT"] = "rm-detached-selftest"
    d, a = world()
    try:
        run_commit(a, "- `x_part.py` adds z twice.")
        msg = D.check(a, "origin/main")
        chk(bool(msg) and "x_part.py adds z twice" in msg.replace("`", "") and "risk:" in msg,
            "git: a helper's new line on its own changed file is returned, with the rule and the repair")
        sh(a, "reset", "-q", "--keep", "origin/main")
        run_commit(a, "- `y_part.py` adds z twice.")
        chk(D.check(a, "origin/main") is None, "git: a line on a file the run did not change passes")
        sh(a, "reset", "-q", "--keep", "origin/main")
        run_commit(a, "- `x_part.py` adds z twice. risk: a fix would move the order the tick reads.")
        chk(D.check(a, "origin/main") is None, "git: a line with a risk part passes")
        sh(a, "reset", "-q", "--keep", "origin/main")
        run_commit(a, "- `x_part.py` adds z twice.")
        os.environ.pop("RM_ROLE_UNIT")
        os.environ.pop("RM_DETACHED_UNIT", None)
        chk(D.check(a, "origin/main") is None, "git: a run that is not a helper's is not checked")
    finally:
        shutil.rmtree(d, True)


def t_a_refused_landing_leaves_the_files_as_written():
    os.environ["RM_ROLE_UNIT"] = "rm-detached-selftest"
    d, a = world()
    try:
        write(a, CODE, "x = 1\nz = 2\n")
        with open(os.path.join(a, POLISH), "a") as f:
            f.write("- `x_part.py` adds z twice.\n")
        err = None
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                P.publish(a, [CODE, POLISH], "run")
        except P.Refuse as e:
            err = str(e)
        chk(err is not None and "polish" in err.lower(), "publish: refuses the planted line (%s)" % (err or "landed")[:90])
        chk(sh(a, "rev-parse", "HEAD") == sh(a, "rev-parse", "origin/main"),
            "publish: the refused commit is taken off HEAD, the files stay as written")
        chk("adds z twice" in open(os.path.join(a, POLISH)).read(), "publish: the working tree keeps the run's line")
        with open(os.path.join(a, POLISH), "w") as f:
            f.write("# POLISH\n\n- an old line about `x_part.py` stays as it was.\n")
        with contextlib.redirect_stdout(buf):
            sha = P.publish(a, [CODE, POLISH], "run, polish done")
        chk(bool(sha), "publish: after the run does the polish (the line gone), the landing passes")
    finally:
        os.environ.pop("RM_ROLE_UNIT", None)
        shutil.rmtree(d, True)


def t_a_line_on_an_unchanged_file_passes():
    chk(D.returned([(POLISH, "- `y_part.py` reads the list twice.")], [CODE]) == [],
        "a line on an unchanged file passes")


def t_a_line_with_a_risk_part_passes():
    chk(D.returned([(POLISH, "- `x_part.py` reads twice. Risk: a second read changes the order the tick sees.")],
                   [CODE]) == [], "a line with a risk part passes (any letter case)")


def t_a_run_that_is_not_a_helper_is_not_checked():
    chk(not D.helper_run({}) and D.helper_run({"RM_ROLE_UNIT": "u"}) and D.helper_run({"RM_DETACHED_UNIT": "u"}),
        "helper_run: true only when RM_ROLE_UNIT or RM_DETACHED_UNIT is set")
    chk(D.check(".", "origin/main", env={}) is None, "a run that is not a helper's is never refused")


def main():
    for k in ("RM_ROLE_UNIT", "RM_DETACHED_UNIT"):
        os.environ.pop(k, None)
    t_a_helper_line_on_its_own_changed_file_is_returned()
    t_a_line_on_an_unchanged_file_passes()
    t_a_line_with_a_risk_part_passes()
    t_a_run_that_is_not_a_helper_is_not_checked()
    t_the_door_reads_only_the_runs_own_commits()
    t_a_refused_landing_leaves_the_files_as_written()
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
