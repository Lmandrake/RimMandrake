#!/usr/bin/env python3
"""Selftest of the page design/specs/2026-11-27-red-seen-plant-record/boundary.md: a planted fault never outlives the
`red-seen` that planted it; a leftover is restored and named by the next act on that clone (item
RIMMANDRAKE_RESTORE_TREE_WHEN_RED_SEEN_IS_KILLED_PLANT_STAYED_APPLIED). A fake mod tree and a fake deciding test; real
signals, a real SIGKILL, a real throwaway git origin for the publish case. No game, no model.

    python3 src/RimMandrake/rimflow/selftest_red_seen_restore.py
"""
import contextlib
import io
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import judge_certificate as JC  # noqa: E402
import plant_record as PR  # noqa: E402
import selftest_red_seen as SR  # noqa: E402

MOD = SR.MOD
KERNEL = "src/kernel.py"
RESULTS = []
# budget: danger=a child that never ends hangs the selftest; longest=about 1 s (a red-seen restore, 2026-11-27)
WAIT_S = 60


def ok(c, what):
    RESULTS.append(bool(c))
    print(("PASS  " if c else "FAIL  ") + what)


def world():
    root = tempfile.mkdtemp(prefix="redseen_restore_")
    P = SR.fixture(root)
    tt = json.load(open(JC.tpath(root, MOD)))
    tt["tests"]["T_SLOW"] = dict(tt["tests"]["T_GOOD"], command="%s -c \"import time; time.sleep(120)\"" % sys.executable)
    with open(JC.tpath(root, MOD), "w") as f:
        json.dump(tt, f)
    return root, P


def kernel(root):
    with open(os.path.join(root, KERNEL), "rb") as f:
        return f.read()


def no_record(root):
    return not os.path.exists(PR.path(root))


def planted_child(root, P):
    """-> a red-seen of T_SLOW running in its own session, once its fault is in the tree (None: never planted)."""
    before = kernel(root)
    code = ("import sys; sys.path.insert(0, %r); import judge_certificate as JC; "
            "JC.red_seen(%r, %r, 'T_SLOW', patch=%r)" % (HERE, root, MOD, P["fault"]))
    child = subprocess.Popen([sys.executable, "-c", code], start_new_session=True, stderr=subprocess.DEVNULL)
    t0 = time.time()
    while time.time() - t0 < WAIT_S and kernel(root) == before:
        time.sleep(0.05)
    time.sleep(0.3)
    return child if kernel(root) != before else None


def end(child, sig, group=False):
    (os.killpg(child.pid, sig) if group else child.send_signal(sig))
    try:
        child.wait(timeout=WAIT_S)
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGKILL)
        child.wait()


def killed_leftover():
    """-> (root, P, original bytes, planted bytes): a red-seen SIGKILLed with its whole session while planted."""
    root, P = world()
    before = kernel(root)
    child = planted_child(root, P)
    if child is None:
        return root, P, before, None
    end(child, signal.SIGKILL, group=True)
    return root, P, before, kernel(root)


def t_sigterm_restores_the_tree():
    root, P = world()
    try:
        before = kernel(root)
        for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
            child = planted_child(root, P)
            if child is not None:
                end(child, sig)
            ok(child is not None and kernel(root) == before and "T_SLOW" not in SR.red_record(root) and no_record(root),
               "a red-seen that gets %s while planted ends with the original bytes, no red and no plant record "
               "(planted %s, restored %s, record left %s)" % (signal.Signals(sig).name, child is not None,
                                                              kernel(root) == before, not no_record(root)))
            with open(os.path.join(root, KERNEL), "wb") as f:
                f.write(before)
            PR.clear(root)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_sigkill_leftover_is_restored_by_the_next_red_seen():
    root, P, before, planted = killed_leftover()
    try:
        left = planted is not None and planted != before and not no_record(root)
        r = JC.red_seen(root, MOD, "T_GOOD", patch=P["fault"])
        ok(left and r["ok"] is True and "restored" in (r.get("plant") or "") and KERNEL in r["plant"]
           and kernel(root) == before and no_record(root) and SR.red_record(root).get("T_GOOD", {}).get("rc") == 1,
           "after a SIGKILL left its plant (%s), the next red-seen restores and names it, then runs as usual (%s | %s)"
           % (left, r.get("plant"), r["why"][:60]))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_sigkill_leftover_is_restored_by_the_certificate():
    root, P, before, planted = killed_leftover()
    try:
        left = planted is not None and planted != before
        v = JC.certify(root, MOD)
        buf = []
        JC.print_certificate(v, out=buf.append)
        pl = v.get("plant") or {}
        ok(left and pl.get("state") == PR.RESTORED and KERNEL in pl.get("line", "") and kernel(root) == before
           and no_record(root) and any("plant: restored" in x for x in buf),
           "after a SIGKILL left its plant (%s), the certificate restores it and prints the line (%s)" % (left, pl))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_sigkill_leftover_is_restored_by_publish():
    sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
    import selftest_publish as SP   # its import points publish's push lock at a temp root
    d, a, _b = SP.world()
    try:
        patch = os.path.join(d, "plant.patch")
        with open(os.path.join(a, "f.txt"), "rb") as f:
            orig = f.read()
        SP.write(a, "f.txt", SP.LINES.replace("line 1\n", "line ONE planted\n", 1))
        with open(patch, "w") as f:
            f.write(SP.sh(a, "diff", "--", "f.txt") + "\n")
        SP.sh(a, "checkout", "--", "f.txt")
        PR.write(a, "Fix", "T_X", open(patch).read(), {"f.txt": orig})
        subprocess.run(["git", "apply", patch], cwd=a, check=True)
        planted = open(os.path.join(a, "f.txt"), "rb").read() != orig
        SP.write(a, "g.txt", "g changed\n")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            SP.P.publish(a, ["f.txt", "g.txt"], "mine")
        ok(planted and SP.show(a, "f.txt") == SP.LINES and SP.show(a, "g.txt") == "g changed\n" and no_record(a)
           and "plant: restored" in buf.getvalue() and "f.txt" in buf.getvalue(),
           "a leftover plant in a named path is restored and named by ./publish before it commits (planted %s)" % planted)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_normal_run_records_as_before():
    root, P = world()
    try:
        before = kernel(root)
        r = JC.red_seen(root, MOD, "T_GOOD", patch=P["fault"])
        rec = SR.red_record(root).get("T_GOOD", {})
        ok(r["ok"] is True and kernel(root) == before and no_record(root) and not r.get("plant")
           and sorted(rec) == ["at", "command", "file", "last", "patch", "patch_files", "patch_sha", "rc", "test_blob"],
           "a normal red run restores the tree, records the same fields as before, and leaves no plant record (%s)"
           % sorted(rec))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_four_answers_stay_apart():
    root, P = world()
    sleeper = None
    try:
        before = kernel(root)
        patch_text = open(P["fault"]).read()
        c = PR.check(root)
        ok(c["state"] == PR.CLEAN and c["line"] == "", "no record reads clean, silently (%s)" % c)
        PR.write(root, MOD, "T_GOOD", patch_text, {KERNEL: before})
        c = PR.check(root)
        ok(c["state"] == PR.CLEAN and "already holds the original bytes" in c["line"] and no_record(root),
           "a record whose file holds its original bytes reads clean, says so, and is removed (%s)" % c["line"][:70])
        PR.write(root, MOD, "T_GOOD", patch_text, {KERNEL: before})
        subprocess.run(["git", "apply", P["fault"]], cwd=root, check=True)
        c = PR.check(root)
        ok(c["state"] == PR.RESTORED and kernel(root) == before and no_record(root), "a leftover plant reads restored")
        # not restored: the planted file was changed again after the kill, so the reverse does not apply
        PR.write(root, MOD, "T_GOOD", patch_text, {KERNEL: before})
        with open(os.path.join(root, KERNEL), "w") as f:
            f.write("LIMIT = 7\n")
        c = PR.check(root)
        r = JC.red_seen(root, MOD, "T_GOOD", patch=P["fault"])
        v = JC.certify(root, MOD)
        ok(c["state"] == PR.NOT_RESTORED and KERNEL in c["line"] and not no_record(root)
           and r["ok"] is False and r["why"].startswith("did not run") and "not restored" in r["why"]
           and v["ok"] is False and any(x["clause"] == "plant_left" and x["status"] == "REFUSED" for x in v["rows"]),
           "a plant that cannot be reversed is a stop naming the file, in red-seen and the certificate (%s)" % c["line"][:90])
        with open(os.path.join(root, KERNEL), "wb") as f:
            f.write(before)
        # could not look: a damaged record is never clean, and is left for a person
        with open(PR.path(root), "w") as f:
            f.write("{ damaged")
        c = PR.check(root)
        r = JC.red_seen(root, MOD, "T_GOOD", patch=P["fault"])
        v = JC.certify(root, MOD)
        ok(c["state"] == PR.COULD_NOT_LOOK and "could not look" in c["line"] and open(PR.path(root)).read() == "{ damaged"
           and r["ok"] is False and "could not look" in r["why"] and v["ok"] is False,
           "a damaged record reads could not look, never clean, and stops red-seen and the certificate (%s)" % c["line"][:90])
        # running: the record's pid is alive, so its plant is in the tree on purpose
        sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
        rec = {"pid": sleeper.pid, "pid_start": PR._start_time(sleeper.pid), "mod": MOD, "test": "T_GOOD", "at": "now",
               "patch": patch_text, "files": {KERNEL: __import__("base64").b64encode(before).decode()}}
        with open(PR.path(root), "w") as f:
            json.dump(rec, f)
        c = PR.check(root)
        r = JC.red_seen(root, MOD, "T_GOOD", patch=P["fault"])
        ok(c["state"] == PR.RUNNING and r["ok"] is False and "running" in r["why"] and not no_record(root),
           "a record of a live pid reads running, and red-seen does not plant over it (%s)" % c["line"][:80])
        states = {PR.CLEAN, PR.RESTORED, PR.NOT_RESTORED, PR.COULD_NOT_LOOK, PR.RUNNING}
        ok(len(states) == 5 and set(PR.STOPS) == {PR.NOT_RESTORED, PR.COULD_NOT_LOOK, PR.RUNNING},
           "the five states are distinct words, and the three stops are not restored, could not look and running")
    finally:
        if sleeper is not None:
            sleeper.kill()
            sleeper.wait()
        shutil.rmtree(root, ignore_errors=True)


def main():
    t_sigterm_restores_the_tree()
    t_sigkill_leftover_is_restored_by_the_next_red_seen()
    t_sigkill_leftover_is_restored_by_the_certificate()
    t_sigkill_leftover_is_restored_by_publish()
    t_normal_run_records_as_before()
    t_four_answers_stay_apart()
    n = sum(RESULTS)
    print("%s %d/%d" % ("PASS" if n == len(RESULTS) else "FAIL", n, len(RESULTS)))
    return 0 if n == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
