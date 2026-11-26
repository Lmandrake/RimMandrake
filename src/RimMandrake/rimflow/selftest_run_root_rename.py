#!/usr/bin/env python3
"""selftest_run_root_rename.py -- the promises of design/specs/2026-11-26-run-root-rename/boundary.md.

Offline: temp dirs only, one child process (`sleep`) for the /proc cwd reading."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))

import detached_helper as DH  # noqa: E402
import run_store  # noqa: E402
import scratch_clone as SC  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        FAILS.append(name)


def t_the_run_root_is_neutral():
    home = os.path.expanduser("~")
    saved = {k: os.environ.pop(k, None) for k in ("RM_RUNS_ROOT", "RM_DETACHED_POOL", "RM_POOL_ROOT")}
    try:
        roots = [run_store.DEFAULT_ROOT, DH.pool_root(), str(SC.pool_root())]
        check("the-run-root-is-neutral: the defaults name ~/rm/runs",
              roots == ["/home/mandrake/rm/runs", os.path.join(home, "rm", "runs"), str(SC.RM / "runs" / "clones")],
              roots)
        with tempfile.TemporaryDirectory() as t:
            os.environ["RM_RUNS_ROOT"] = t
            check("the-run-root-is-neutral: RM_RUNS_ROOT moves the store", run_store.store_dir() == os.path.join(t, "store"),
                  run_store.store_dir())
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v


def _tree(t):
    real = os.path.join(t, "runs")
    os.makedirs(os.path.join(real, "clones", "ITEM.det"))
    os.symlink("runs", os.path.join(t, "old"))
    return real, os.path.join(t, "old")


def t_a_symlinked_pool_clone_is_seen_in_use():
    with tempfile.TemporaryDirectory() as t:
        real, old = _tree(t)
        p = subprocess.Popen(["sleep", "30"], cwd=os.path.join(old, "clones", "ITEM.det"))
        try:
            check("a-symlinked-pool-clone-is-seen-in-use",
                  SC.clone_in_use(SC.Path(os.path.join(old, "clones", "ITEM.det"))) is True
                  and SC.clone_in_use(SC.Path(os.path.join(real, "clones", "ITEM.det"))) is True)
        finally:
            p.kill()
            p.wait()


def t_a_record_by_the_old_path_is_the_same_clone():
    with tempfile.TemporaryDirectory() as t:
        real, old = _tree(t)
        saved = os.environ.get("RM_DETACHED_POOL")
        os.environ["RM_DETACHED_POOL"] = real
        try:
            rec = {"item": "ITEM", "clone_how": "made by scratch_clone", "clone": os.path.join(old, "clones", "ITEM.det")}
            check("a-record-by-the-old-path-is-the-same-clone: owns_clone", DH.owns_clone(rec) is True)
            check("a-record-by-the-old-path-is-the-same-clone: same_path",
                  DH.same_path(rec["clone"], os.path.join(real, "clones", "ITEM.det"))
                  and not DH.same_path(rec["clone"], os.path.join(real, "clones")) and not DH.same_path("", ""))
            rd = os.path.join(t, "state")
            DH.runs_dir(rd)
            import json
            with open(DH.record_path("rm-detached-x", rd), "w") as f:
                json.dump(dict(rec, unit="rm-detached-x", status="running"), f)
            seen = DH.clone_holders(os.path.join(real, "clones", "ITEM.det"), root=rd,
                                    runner=lambda *a, **k: subprocess.CompletedProcess(a, 0, "", ""))
            check("a-record-by-the-old-path-is-the-same-clone: clone_holders lists the record", [u for u, _, _ in seen] == ["rm-detached-x"], seen)
        finally:
            os.environ.pop("RM_DETACHED_POOL", None)
            if saved is not None:
                os.environ["RM_DETACHED_POOL"] = saved


def t_a_transcript_folder_is_found_by_either_path():
    with tempfile.TemporaryDirectory() as t:
        real, old = _tree(t)
        projects = os.path.join(t, "projects")
        clone_real = os.path.realpath(os.path.join(real, "clones", "ITEM.det"))
        key = os.path.join(projects, "".join(c if c.isalnum() else "-" for c in clone_real))
        os.makedirs(key)
        check("a-transcript-folder-is-found-by-either-path: the real path's folder",
              DH.project_dir(os.path.join(old, "clones", "ITEM.det"), projects) == key,
              DH.project_dir(os.path.join(old, "clones", "ITEM.det"), projects))
        given = os.path.join(projects, "".join(c if c.isalnum() else "-" for c in os.path.join(old, "clones", "ITEM.det")))
        os.makedirs(given)
        check("a-transcript-folder-is-found-by-either-path: the given path's folder first",
              DH.project_dir(os.path.join(old, "clones", "ITEM.det"), projects) == given)


def _real_pool_clone(pool, item):
    """A real git clone inside <pool>/clones with one unlanded commit and one dirty file. -> its real path."""
    def git(c, *a):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=c, check=True,
                              capture_output=True, text=True).stdout
    os.makedirs(os.path.join(pool, "clones"), exist_ok=True)
    o = os.path.join(pool, "o.git")
    git(pool, "init", "-q", "--bare", o, "-b", "main")
    c = os.path.join(pool, "clones", item + ".det")
    git(pool, "clone", "-q", o, c)
    for name, text, commit in (("base.txt", "base\n", True), ("work.cs", "committed work\n", True),
                               ("dirty.cs", "not committed\n", False)):
        with open(os.path.join(c, name), "w") as f:
            f.write(text)
        if commit:
            git(c, "add", name)
            git(c, "commit", "-qm", name)
            if name == "base.txt":
                git(c, "push", "-q", "origin", "HEAD")
    return c


def t_a_clone_named_through_the_old_pool_name_is_bundled_and_returned():
    import tarfile
    with tempfile.TemporaryDirectory() as t:
        real, old = _tree(t)
        c = _real_pool_clone(real, "SYMLINKED_CLONE")
        named = os.path.join(old, "clones", "SYMLINKED_CLONE.det")
        fx = run_store.Effects(run_store.rules(), run_store.Store(real))
        out = fx.remove_clone({"clone": named, "item": "SYMLINKED_CLONE"})
        held = []
        for f in (os.listdir(out) if out and os.path.isdir(out) else []):
            if f.endswith(".tar"):
                with tarfile.open(os.path.join(out, f)) as tf:
                    held += tf.getnames()
        left = os.listdir(os.path.join(real, "clones"))
        check("a-clone-named-through-the-old-pool-name-is-bundled-and-returned",
              bool(out) and os.path.exists(os.path.join(out, "commits.bundle")) and any(n.endswith("dirty.cs") for n in held)
              and not os.path.exists(c) and any(n.startswith("warm") for n in left), (out, held, left))


def t_a_clone_outside_the_pool_is_refused_with_an_alarm_line():
    with tempfile.TemporaryDirectory() as t:
        pool, elsewhere = os.path.join(t, "pool"), os.path.join(t, "elsewhere", "OUTSIDE.det")
        os.makedirs(pool)
        os.makedirs(elsewhere)
        store = run_store.Store(pool)
        out = run_store.Effects(run_store.rules(), store).remove_clone({"clone": elsewhere, "item": "OUTSIDE"})
        lines = []
        if os.path.exists(store.p("journal.jsonl")):
            with open(store.p("journal.jsonl")) as f:
                lines = [json.loads(x) for x in f if x.strip()]
        mine = [x for x in lines if x.get("do") == "alarm" and x.get("clone") == elsewhere]
        check("a-clone-outside-the-pool-is-refused-with-an-alarm-line",
              out is None and os.path.isdir(elsewhere) and len(mine) == 1 and bool(mine[0].get("why")), lines)


def main():
    for fn in (t_the_run_root_is_neutral, t_a_symlinked_pool_clone_is_seen_in_use,
               t_a_record_by_the_old_path_is_the_same_clone, t_a_transcript_folder_is_found_by_either_path,
               t_a_clone_named_through_the_old_pool_name_is_bundled_and_returned,
               t_a_clone_outside_the_pool_is_refused_with_an_alarm_line):
        try:
            fn()
        except Exception as e:  # noqa: BLE001 - a crash is a failed promise, named
            check(fn.__name__, False, repr(e))
    print("%d FAILED" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
