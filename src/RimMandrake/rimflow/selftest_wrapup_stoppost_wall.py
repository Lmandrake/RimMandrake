#!/usr/bin/env python3
"""selftest_wrapup_stoppost_wall.py — a walled unit's wrap-up ExecStopPost really runs (RELENTLESS_WRAPUP_FIX_STOPPOST_NAMESPACE).

Against the real user systemd manager, no fakes: a transient unit carrying the two wall properties that broke the old
"-+python3" post (BindPaths=, TemporaryFileSystem=; relentless_wall.props always adds the first) and an InaccessiblePaths=
over a folder, with ExecStopPost = role_launch.stoppost_handoff(...) of a probe that echoes a nonce and lists the hidden
folder. The probe's own unit must log the nonce and see the hidden file: it ran, and outside the wall.

  S0  the instrument can see: a plain unit's echo reaches `journalctl --user -u`
  S1  the old "-+" form on the same properties logs 'Failed to set up mount namespacing' (the instance this fixes)
  S2  the handoff form on the same properties: the probe ran, outside the wall
  S3  the handoff never fails the unit: a handoff whose command does not exist leaves the unit's result success
  S4  role_launch.wrapup_argv is that handoff
  S5  end to end: wrapup.py unit, handed off from a walled unit, appends its runs.jsonl row (env carried across)

    python3 src/RimMandrake/rimflow/selftest_wrapup_stoppost_wall.py
"""
import os
import shlex
import subprocess
import sys
import tempfile
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import role_launch  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def run_unit(name, props):
    r = subprocess.run(["systemd-run", "--user", "--quiet", "--wait", "--unit", name]
                       + sum((["-p", p] for p in props), []) + ["/usr/bin/true"],
                       capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    return r.returncode, (r.stdout + r.stderr)[-300:]


def journal(*units, want=None, wait_s=15):
    """-> the units' journal text; polls until `want` shows (a --no-block handoff runs after the stop returns)."""
    end, txt = time.time() + wait_s, ""
    while True:
        r = subprocess.run(["journalctl", "--user", "-o", "cat", "--no-pager"] + sum((["-u", u] for u in units), []),
                           capture_output=True, text=True, timeout=30)
        txt = r.stdout
        if want is None or want in txt or time.time() > end:
            return txt
        time.sleep(0.5)


def main():
    base = tempfile.mkdtemp(prefix="stoppost_wall_", dir=os.path.expanduser("~"))
    hidden, tmpfs, bind_src = (os.path.join(base, n) for n in ("hidden", "tmpfs", "bindsrc"))
    for d in (hidden, tmpfs, bind_src):
        os.makedirs(d)
    open(os.path.join(hidden, "seen_outside_wall"), "w").close()
    wall = ["InaccessiblePaths=" + hidden, "TemporaryFileSystem=" + tmpfs, "BindPaths=%s:%s" % (bind_src, tmpfs)]
    tag = uuid.uuid4().hex[:10]
    try:
        u0, n0 = "rm-selftest-stoppost-%s-s0" % tag, "S0NONCE" + tag
        rc, out = run_unit(u0, ["ExecStopPost=/bin/echo " + n0])
        check(rc == 0 and n0 in journal(u0, want=n0), "S0 a plain unit's post output reaches the journal (rc=%d %s)" % (rc, out))

        u1 = "rm-selftest-stoppost-%s-s1" % tag
        rc, out = run_unit(u1, wall + ["ExecStopPost=-+/bin/echo old"])
        j1 = journal(u1, want="namespac")
        check(rc == 0 and "Failed to set up mount namespacing" in j1,
              "S1 the old '-+' post on the wall's properties fails its NAMESPACE step (the instance), unit not failed")

        u2, n2 = "rm-selftest-stoppost-%s-s2" % tag, "S2NONCE" + tag
        probe = ["/bin/sh", "-c", "echo %s; ls %s" % (n2, shlex.quote(hidden))]
        rc, out = run_unit(u2, wall + ["ExecStopPost=" + role_launch.stoppost_handoff(u2 + "-wrapup", probe)])
        j2 = journal(u2 + "-wrapup", want="seen_outside_wall")
        check(rc == 0 and n2 in j2, "S2 the handed-off post ran (rc=%d %s)" % (rc, out))
        check("seen_outside_wall" in j2, "S2 and it ran outside the wall: it lists the InaccessiblePaths folder")
        check("namespac" not in journal(u2), "S2 the walled unit logged no namespace failure")

        u3 = "rm-selftest-stoppost-%s-s3" % tag
        rc, out = run_unit(u3, wall + ["ExecStopPost=" + role_launch.stoppost_handoff(u3 + "-wrapup", ["/nonexistent/x"])])
        check(rc == 0, "S3 a handoff whose command is missing never fails the unit (rc=%d %s)" % (rc, out))

        w = role_launch.wrapup_argv({"name": "relentless", "seat": "BENCH", "clone": "/x/c"}, "rm-relentless-check-z-g1-c1")
        words = shlex.split(w[1:])
        check(w.startswith("-/usr/bin/systemd-run --user ") and "rm-relentless-check-z-g1-c1-wrapup" in words
              and "RIMFLOW_BRIDGE_SEAT" in words and words[words.index("--") + 1:][:2] ==
              ["/usr/bin/python3", os.path.join(HERE, "wrapup.py")] and "--carried" in words,
              "S4 role_launch.wrapup_argv is that handoff, carrying the holder's env and the launcher's wrapup.py")

        u5, wd = "rm-selftest-stoppost-%s-s5" % tag, os.path.join(base, "wrapupdir")
        post = role_launch.wrapup_argv({"name": "relentless", "seat": "BENCH", "clone": bind_src}, u5)
        rc, out = run_unit(u5, wall + ["Environment=RM_WRAPUP_DIR=" + wd, "Environment=RM_UNDER_SELFTEST=1",
                                       "ExecStopPost=" + post])
        runs, end = os.path.join(wd, "runs.jsonl"), time.time() + 30
        while not (os.path.isfile(runs) and u5 in open(runs).read()) and time.time() < end:
            time.sleep(0.5)
        check(rc == 0 and os.path.isfile(runs) and u5 in open(runs).read(),
              "S5 the real wrap-up runs from a walled unit and writes its census row where the unit's env said")
    finally:
        subprocess.run(["rm", "-rf", base])
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
