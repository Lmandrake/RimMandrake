#!/usr/bin/env python3
"""selftest_check_once.py - the ticket lane's outcome checks run once per window for both timers, in parallel under a
bound, and a result is kept until a file that the check read has changed.

Item RIMMANDRAKE_RUN_LANE_CHECKS_ONCE_193_OF_218_SECONDS; page design/specs/2026-11-27-check-once/boundary.md (each t_
function is one promise of it). Offline: a throwaway check root with fake checks that count their runs (each appends
one line to its own counter file), a throwaway state dir. Written before check_once.py; seen failing on the base (the
module absent).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"

FAILS = []
X = {}


def chk(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def CO():
    import check_once
    return check_once


def put(rel, text):
    p = os.path.join(X["root"], rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


COUNTER = """import os, sys, time
here = os.path.dirname(os.path.abspath(__file__))
name = os.path.splitext(os.path.basename(__file__))[0]
with open(os.path.join(here, "counts", name), "a") as f:
    f.write("%d %f %f\\n" % (os.getpid(), time.time(), 0))
"""


def fake(name, body="", sleep=0.0):
    """A check script that counts its runs in counts/<name>, sleeps, then runs body (which sets rc)."""
    put("counts/.keep", "")
    src = COUNTER + "t0 = time.time()\ntime.sleep(%r)\nrc = 0\n%s\n" % (sleep, body)
    src += ("with open(os.path.join(here, 'counts', name + '.span'), 'a') as f:\n"
            "    f.write('%f %f\\n' % (t0, time.time()))\nsys.exit(rc)\n")
    put("%s.py" % name, src)
    return "cmd:python3 %s.py" % name


def runs(name):
    try:
        with open(os.path.join(X["root"], "counts", name)) as f:
            return len(f.read().splitlines())
    except OSError:
        return 0


def fresh_store():
    d = tempfile.mkdtemp(prefix="kept_", dir=X["top"])
    return d


def t_both_timers_in_one_window_run_each_check_once():
    """Two beats (one per timer) in one window, on one store: each check runs once; the second beat reads it kept.
    Two beats at the same moment also run each check once (the second waits on the first's lock)."""
    co = CO()
    store = fresh_store()
    a, b = fake("both_a"), fake("both_b", "rc = 1")
    r1, s1 = co.run_many([a, b, a], X["root"], store=store)
    r2, s2 = co.run_many([b, a], X["root"], store=store)
    chk(runs("both_a") == 1 and runs("both_b") == 1, "both-timers: each check ran once over two beats "
        "(a %d, b %d)" % (runs("both_a"), runs("both_b")))
    chk(r1[a][0] == r2[a][0] == "holds" and r1[b][0] == r2[b][0] == "fails",
        "both-timers: the second beat gives the same verdicts (%s, %s)" % (r2[a][0], r2[b][0]))
    chk(s2.get("kept") == 2 and not s2.get("ran"), "both-timers: the second beat ran nothing (%s)" % s2)
    store = fresh_store()
    c = fake("both_c", sleep=0.6)
    out = []
    ts = [threading.Thread(target=lambda: out.append(co.run_many([c], X["root"], store=store))) for _ in range(2)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    chk(runs("both_c") == 1 and all(o[0][c][0] == "holds" for o in out),
        "both-timers: two beats at once ran the check once (%d runs)" % runs("both_c"))


def t_checks_run_in_parallel_under_a_bound():
    """Six checks of 0.8 s with a bound of 3: at most 3 run at once, and more than one does."""
    co = CO()
    names = ["par_%d" % i for i in range(6)]
    texts = [fake(n, sleep=0.8) for n in names]
    t0 = time.time()
    co.run_many(texts, X["root"], store=fresh_store(), workers=3)
    wall = time.time() - t0
    spans = []
    for n in names:
        with open(os.path.join(X["root"], "counts", n + ".span")) as f:
            spans += [tuple(map(float, ln.split())) for ln in f]
    most = max(sum(1 for s in spans if s[0] <= t < s[1]) for t in [s[0] + 1e-6 for s in spans])
    chk(1 < most <= 3, "parallel: at most 3 at once and more than 1 (%d at most)" % most)
    chk(wall < 6 * 0.8, "parallel: six 0.8 s checks took %.1f s, under the %.1f s of one after the other" % (wall, 4.8))
    chk(co.WORKERS >= 2, "parallel: the beat's own bound runs more than one at a time (%d)" % co.WORKERS)


def t_a_result_is_kept_until_a_read_file_changes():
    co = CO()
    store = fresh_store()
    put("data/flag.txt", "no")
    t = fake("keep_a", "rc = 0 if open(os.path.join(here, 'data', 'flag.txt')).read().strip() == 'yes' else 1")
    v1 = co.run_many([t], X["root"], store=store)[0][t][0]
    v2 = co.run_many([t], X["root"], store=store)[0][t][0]
    chk(v1 == v2 == "fails" and runs("keep_a") == 1, "kept: an unchanged read keeps the result (%s %s, %d run)" % (
        v1, v2, runs("keep_a")))
    time.sleep(0.01)
    put("data/flag.txt", "yes")
    v3 = co.run_many([t], X["root"], store=store)[0][t][0]
    chk(v3 == "holds" and runs("keep_a") == 2, "kept: a changed read file runs it again (%s, %d runs)" % (
        v3, runs("keep_a")))
    # a file found by stat only (os.path.exists), never opened
    t = fake("keep_b", "rc = 0 if os.path.exists(os.path.join(here, 'data', 'appears.txt')) else 1")
    v1 = co.run_many([t], X["root"], store=store)[0][t][0]
    put("data/appears.txt", "")
    v2 = co.run_many([t], X["root"], store=store)[0][t][0]
    chk((v1, v2) == ("fails", "holds") and runs("keep_b") == 2, "kept: a file that appears where the check "
        "looked runs it again (%s %s, %d runs)" % (v1, v2, runs("keep_b")))
    # a file in a listed folder
    put("data/list/a", "")
    t = fake("keep_c", "rc = 0 if len(os.listdir(os.path.join(here, 'data', 'list'))) == 2 else 1")
    v1 = co.run_many([t], X["root"], store=store)[0][t][0]
    put("data/list/b", "")
    v2 = co.run_many([t], X["root"], store=store)[0][t][0]
    chk((v1, v2) == ("fails", "holds"), "kept: a new file in a listed folder runs it again (%s %s)" % (v1, v2))
    # an atomic replace of another file in a listed folder keeps the result (the names are the same)
    put("data/list2/a", "1")
    t = fake("keep_h", "rc = 0 if len(os.listdir(os.path.join(here, 'data', 'list2'))) == 1 else 1")
    co.run_many([t], X["root"], store=store)
    put("data/list2/a.tmp", "2")
    os.replace(os.path.join(X["root"], "data/list2/a.tmp"), os.path.join(X["root"], "data/list2/a"))
    co.run_many([t], X["root"], store=store)
    chk(runs("keep_h") == 1, "kept: a replace that keeps a listed folder's names keeps the result (%d run)" % (
        runs("keep_h")))
    # the common form: the selftest does not exist yet, then it does
    t = "cmd:test -f keep_d.py && python3 keep_d.py"
    v1 = co.run_many([t], X["root"], store=store)[0][t][0]
    v1b = co.run_many([t], X["root"], store=store)[0][t][0]
    fake("keep_d")
    v2 = co.run_many([t], X["root"], store=store)[0][t][0]
    chk((v1, v1b, v2) == ("fails", "fails", "holds") and runs("keep_d") == 1,
        "kept: `test -f S && python3 S` keeps fails until S appears (%s %s %s)" % (v1, v1b, v2))
    # a module the check imports changes
    put("mods/helper_mod.py", "OK = False\n")
    put("keep_e.py", "import sys, os\nsys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "
        "'mods'))\nimport helper_mod\nsys.exit(0 if helper_mod.OK else 1)\n")
    t = "cmd:python3 keep_e.py"
    v1 = co.run_many([t], X["root"], store=store)[0][t][0]
    time.sleep(0.01)
    put("mods/helper_mod.py", "OK = True\n")
    v2 = co.run_many([t], X["root"], store=store)[0][t][0]
    chk((v1, v2) == ("fails", "holds"), "kept: a changed imported module runs it again (%s %s)" % (v1, v2))
    # the same, when the module's .pyc already exists before the first recorded run (the repo's modules have one):
    # python then opens only the .pyc and stats the source without an audit event
    put("mods2/helper_pyc.py", "OK = False\n")
    put("keep_i.py", "import sys, os\nsys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "
        "'mods2'))\nimport helper_pyc\nsys.exit(0 if helper_pyc.OK else 1)\n")
    subprocess.run([sys.executable, os.path.join(X["root"], "keep_i.py")], capture_output=True)
    had_pyc = os.path.isdir(os.path.join(X["root"], "mods2", "__pycache__"))
    t = "cmd:python3 keep_i.py"
    v1 = co.run_many([t], X["root"], store=store)[0][t][0]
    time.sleep(0.01)
    put("mods2/helper_pyc.py", "OK = True\n")
    v2 = co.run_many([t], X["root"], store=store)[0][t][0]
    chk(had_pyc and (v1, v2) == ("fails", "holds"), "kept: a changed imported module whose .pyc existed runs it "
        "again (pyc %s, %s %s)" % (had_pyc, v1, v2))
    # a python child that records its own reads
    put("data/kid.txt", "no")
    put("kid.py", "import sys, os\nh = os.path.dirname(os.path.abspath(__file__))\n"
        "sys.exit(0 if open(os.path.join(h, 'data', 'kid.txt')).read() == 'yes' else 1)\n")
    put("keep_f.py", "import subprocess, sys, os\nh = os.path.dirname(os.path.abspath(__file__))\n"
        "sys.exit(subprocess.run([sys.executable, os.path.join(h, 'kid.py')]).returncode)\n")
    t = "cmd:python3 keep_f.py"
    v1 = co.run_many([t], X["root"], store=store)[0][t][0]
    put("data/kid.txt", "yes")
    v2 = co.run_many([t], X["root"], store=store)[0][t][0]
    chk((v1, v2) == ("fails", "holds"), "kept: a file read by a python child runs it again (%s %s)" % (v1, v2))
    # the refresh
    t = fake("keep_g")
    co.run_many([t], X["root"], store=store)
    old = co.KEEP_S
    try:
        co.KEEP_S = 0
        co.run_many([t], X["root"], store=store)
    finally:
        co.KEEP_S = old
    chk(runs("keep_g") == 2, "kept: a result older than KEEP_S runs again (%d runs)" % runs("keep_g"))


def t_a_check_whose_reads_cannot_be_named_runs_every_time():
    co = CO()
    store = fresh_store()
    put("data/plain.txt", "yes\n")
    cases = {
        "pipe": "cmd:python3 un_pipe.py | grep -q .",
        "other program": "cmd:python3 un_other.py",
        "isolated python": "cmd:python3 -I un_iso.py",
        "expansion": "cmd:test -f $HOME/x || python3 un_exp.py",
        "child without record": "cmd:python3 un_env.py",
        "os._exit": "cmd:python3 un_exit.py",
    }
    fake("un_pipe", "print('x')")
    fake("un_other", "import subprocess; subprocess.run(['true'])")
    fake("un_iso")
    fake("un_exp")
    fake("un_env", "import subprocess; subprocess.run([sys.executable, '-c', 'pass'], env={'PATH': '/usr/bin'})")
    fake("un_exit", "os._exit(0)")
    for why, t in cases.items():
        name = t.split("un_")[1].split(".py")[0]
        for _ in range(2):
            co.run_many([t], X["root"], store=store)
        chk(runs("un_" + name) == 2, "unnamed: %s runs every time (%d runs of 2)" % (why, runs("un_" + name)))
    chk(co.plan("python3 a.py")[0] is not None and co.plan("test -f a && python3 a.py --x 1")[0] is not None,
        "unnamed: the simple forms are named")
    chk(co.plan('python3 -c "import sys;sys.path[:0]=[1]; print(2*3)"')[0] is not None
        and co.plan("python3 -c 'a$b' && test ! -d x")[0] is not None, "unnamed: quoted code that bash does not expand "
        "is named")
    for bad in ("python3 a.py > out", "python3 a.py; true", "FOO=1 python3 a.py", "python3 a.py `x`", "git status",
                "test -f a -a -f b", "python3 -I a.py", 'python3 -c "x$HOME"', "python3 a*.py", "(python3 a.py)",
                "python3 a.py & python3 b.py", "python3 'a.py"):
        chk(co.plan(bad)[0] is None, "unnamed: %r is not named" % bad)
    # a path check is not kept: it reads one file, and is cheap
    p = "path-has:data/plain.txt::yes"
    r, s = co.run_many([p, p], X["root"], store=store)
    chk(r[p][0] == "holds" and s.get("path") == 1 and not s.get("kept"), "unnamed: a path check runs (%s)" % s)


def t_unmeasured_stays_unmeasured():
    co = CO()
    store = fresh_store()
    t = fake("unm_a", "rc = 2")
    r1 = co.run_many([t], X["root"], store=store)[0][t]
    r2 = co.run_many([t], X["root"], store=store)[0][t]
    chk(r1[0] == r2[0] == "unmeasured" and runs("unm_a") == 2,
        "unmeasured: exit 2 is unmeasured both times and never kept (%s %s, %d runs)" % (r1[0], r2[0], runs("unm_a")))
    chk(not [n for n in os.listdir(store) if n.endswith(".json")], "unmeasured: nothing kept for it")
    # a store that cannot be used: the check still runs and gives its own verdict
    bad = os.path.join(X["top"], "not_a_dir")
    with open(bad, "w") as f:
        f.write("")
    t = fake("unm_b", "rc = 1")
    r = co.run_many([t], X["root"], store=bad)[0][t]
    chk(r[0] == "fails", "unmeasured: an unusable store still gives the check's own verdict (%s)" % r[0])
    # a kept result whose read can no longer be read is not used
    t = fake("unm_c")
    co.run_many([t], X["root"], store=store)
    f = [n for n in os.listdir(store) if n.endswith(".json")]
    with open(os.path.join(store, f[0])) as fh:
        e = json.load(fh)
    e["reads"][os.path.join(X["root"], "unm_c.py")] = ["error", 13]
    with open(os.path.join(store, f[0]), "w") as fh:
        json.dump(e, fh)
    co.run_many([t], X["root"], store=store)
    chk(runs("unm_c") == 2, "unmeasured: a kept read that no longer matches runs the check again (%d)" % runs("unm_c"))
    # a check that dies on its deadline is unmeasured and never kept
    t = fake("unm_d", sleep=3)
    import list_effect as LE
    old = LE.CMD_TIMEOUT_S
    try:
        LE.CMD_TIMEOUT_S = 1  # budget: fixture
        r = co.run_many([t], X["root"], store=store)[0][t]
    finally:
        LE.CMD_TIMEOUT_S = old
    chk(r[0] == "unmeasured", "unmeasured: a check past its deadline is unmeasured (%s)" % r[0])
    # a dry beat keeps nothing new
    store2 = fresh_store()
    t = fake("unm_e")
    co.run_many([t], X["root"], store=store2, write=False)
    chk(not [n for n in os.listdir(store2) if n.endswith(".json")], "unmeasured: a dry beat keeps nothing")


def t_a_shape_check_is_answered_in_the_beat_with_its_parts_in_the_batch():
    """`list_shape.py holds <ID>` with the beat's world: the same text and verdict as the command, no ledger read."""
    co = CO()
    import list_shape as LS
    store = fresh_store()
    a, b = fake("shp_a"), fake("shp_b", "rc = 1")
    item = types.SimpleNamespace(shape={"parts": [{"name": "one", "effect": a}, {"name": "two", "effect": b}]})
    world = types.SimpleNamespace(items={"SOME_ITEM_X": item})
    t = "cmd:python3 src/RimMandrake/rimflow/list_shape.py holds SOME_ITEM_X"
    res, st = co.run_many([t, a], X["root"], world=world, store=store)
    code, text = LS.holds_text("SOME_ITEM_X", world, X["root"])
    chk(res[t] == ("fails", text) and code == 1, "shape: in the beat, the verdict and text of holds_text (%s)" % (
        res[t][0],))
    chk(runs("shp_a") == 2 and st.get("in_process") == 1, "shape: its part ran once in the batch (%d runs incl. the "
        "direct holds_text call)" % runs("shp_a"))
    # the command prints the same text as holds_text gives
    chk(text.splitlines()[-1] == "FAILS: SOME_ITEM_X", "shape: the last line is the verdict (%s)" % text.splitlines()[-1])
    # an id the world lacks is unmeasured, as the command says
    t2 = "cmd:python3 src/RimMandrake/rimflow/list_shape.py holds NO_SUCH_ITEM_X"
    world2 = types.SimpleNamespace(items={})
    c2, x2 = LS.holds_text("NO_SUCH_ITEM_X", world2, X["root"])
    chk(c2 == 2 and x2.startswith("UNMEASURED"), "shape: an item never filed is unmeasured")
    chk(co.shape_id(t) == "SOME_ITEM_X" and co.shape_id(t2 + " extra") is None, "shape: only the exact form is taken")
    # a part that is the item's own check is not run (it would start itself without end)
    loop = types.SimpleNamespace(shape={"parts": [{"name": "self", "effect": t.replace("SOME_ITEM_X", "LOOP_ITEM_X")}]})
    world3 = types.SimpleNamespace(items={"LOOP_ITEM_X": loop})
    t3 = "cmd:python3 src/RimMandrake/rimflow/list_shape.py holds LOOP_ITEM_X"
    t0 = time.time()
    r3 = co.run_many([t3], X["root"], world=world3, store=store)[0][t3]
    chk(r3[0] == "unmeasured" and "its own item's check" in r3[1] and time.time() - t0 < 30,
        "shape: a part that is its own item's check is unmeasured, not run (%s)" % r3[0])


def t_the_hook_and_the_beat_key_a_path_alike():
    """The hook keys a path at first read; the beat keys it again to decide: both must give the same for no change."""
    co = CO()
    store = fresh_store()
    put("data/alike/f.txt", "x")
    t = fake("alike", "open(os.path.join(here, 'data', 'alike', 'f.txt')).read(); os.listdir(os.path.join(here, 'data',"
                      " 'alike')); os.path.exists(os.path.join(here, 'nope'))")
    co.run_many([t], X["root"], store=store)
    f = [n for n in os.listdir(store) if n.endswith(".json")]
    with open(os.path.join(store, f[0])) as fh:
        reads = json.load(fh)["reads"]
    want = [os.path.join(X["root"], p) for p in ("data/alike/f.txt", "data/alike", "nope")]
    chk(all(p in reads for p in want), "alike: the hook named the file, the folder and the missing path")
    chk(all(reads[p] == co.sig(p) for p in want) and reads[want[1]][0] == "dir" and reads[want[2]] == ["missing"],
        "alike: each kept key equals the beat's key now (%s)" % [reads.get(p) for p in want])


def t_the_ticks_run_their_checks_through_one_batch():
    """Both ticks call check_once.run_many (one batch per beat), not list_effect.run one by one."""
    for f in ("list_effect.py", "list_dispatch.py"):
        with open(os.path.join(HERE, f), encoding="utf-8") as fh:
            src = fh.read()
        tick_part = src.split("def _tick(")[1] if f == "list_effect.py" else src.split("def gather(")[1].split("\ndef ")[0]
        if f == "list_dispatch.py":
            chk('"checks": facts.get("checks")' in src, "ticks: list_dispatch's reading carries the batch's counts")
        else:
            chk('"checks": cstats' in src, "ticks: list_effect's reading carries the batch's counts")
        chk("check_once.run_many" in tick_part and "LE.run(d[\"effect\"]" not in tick_part and "verdict, out = run(eff" not in
            tick_part, "ticks: %s runs its checks in one batch" % f)


def main():
    top = tempfile.mkdtemp(prefix="selftest_check_once_")
    X.update(top=top, root=os.path.join(top, "root"))
    os.makedirs(X["root"])
    saved = {k: os.environ.get(k) for k in ("RM_RUN_TMP_ROOT",)}
    os.environ["RM_RUN_TMP_ROOT"] = os.path.join(top, "runs")
    try:
        try:
            CO()
        except Exception as e:  # noqa: BLE001
            chk(False, "check_once imports (%s: %s)" % (type(e).__name__, e))
            return 1
        for t in (t_both_timers_in_one_window_run_each_check_once, t_checks_run_in_parallel_under_a_bound,
                  t_a_result_is_kept_until_a_read_file_changes, t_a_check_whose_reads_cannot_be_named_runs_every_time,
                  t_unmeasured_stays_unmeasured, t_the_hook_and_the_beat_key_a_path_alike,
                  t_a_shape_check_is_answered_in_the_beat_with_its_parts_in_the_batch,
                  t_the_ticks_run_their_checks_through_one_batch):
            try:
                t()
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                chk(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(top, ignore_errors=True)
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
