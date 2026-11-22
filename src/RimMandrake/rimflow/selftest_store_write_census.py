#!/usr/bin/env python3
"""selftest_store_write_census.py: the cutover's writer clause finds writers of the old mod stores (stage.json,
journal.md, version/stage_record.json) by MEASURING them at run time (store_write_census.py, item
RIMMANDRAKE_NARROW_CUTOVER_WRITER_CHECK_EIGHT_OF_THIRTEEN_READ; the Conductor's decision 2026-11-18 7:35 PM PST: no hand
allowlist, no source-text matching). Offline, on a fixture repo in a temp dir; written before store_write_census.py and
watched failing on the base (the import fails, and the old oracle reads a reader as a writer), then passing.

    python3 src/RimMandrake/rimflow/selftest_store_write_census.py      exit 0 when every check prints PASS

What it proves: a module whose code opens a store for writing under its selftest is a WRITER, whether it opens the file
itself, renames a temp file onto it in a child process, or hands the path to a helper (the module naming the store is
blamed, not the helper); a module that names a store, writes some other file and was exercised is NO WRITE SEEN; a module
no selftest runs, or whose store-naming function never ran, is NOT MEASURED with the function named, never "does not
write"; a selftest's own fixture write blames nobody; a hook that cannot run is COULD NOT LOOK with its cause. And the
oracle (modledger_cutover_accept.py --writers-only) carries the four answers to its exit code: 1 writers, 0 none and all
measured, 2 not measured, 3 could not look.
"""
import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ORACLE = os.path.join(HERE, "acceptance", "modledger_cutover_accept.py")
FAILS, COUNT = [], [0]


def ok(cond, what):
    COUNT[0] += 1
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


MODS = {
    # writes stage.json itself
    "fx_writer.py": "import os\n\ndef save(c):\n    with open(os.path.join(c, 'stage.json'), 'w') as f:\n"
                    "        f.write('{}')\n",
    # writes a temp file and renames it onto journal.md, run as a child process by its selftest
    "fx_replace_writer.py": "import os, sys\n\ndef save(c):\n    t = os.path.join(c, 'j.tmp')\n"
                            "    open(t, 'w').write('x')\n    os.replace(t, os.path.join(c, 'journal.md'))\n\n"
                            "if __name__ == '__main__':\n    save(sys.argv[1])\n",
    # a generic helper: names no store
    "fx_helper.py": "def put(p, text):\n    with open(p, 'w') as f:\n        f.write(text)\n",
    # hands version/stage_record.json to the helper
    "fx_via_helper.py": "import os\nimport fx_helper\n\ndef save(c):\n"
                        "    os.makedirs(os.path.join(c, 'version'), exist_ok=True)\n"
                        "    fx_helper.put(os.path.join(c, 'version', 'stage_record.json'), '{}')\n",
    # reads stage.json and writes another file: the old regex called this a writer
    "fx_reader.py": "import os\n\ndef load(c):\n    with open(os.path.join(c, 'stage.json')) as f:\n"
                    "        text = f.read()\n    with open(os.path.join(c, 'notes.txt'), 'w') as f:\n"
                    "        f.write(text)\n    return text\n",
    # names and writes a store; no selftest runs it
    "fx_unexercised.py": "import os\n\ndef save(c):\n    open(os.path.join(c, 'stage.json'), 'w').write('{}')\n",
    # two store functions, only one exercised
    "fx_partly.py": "import os\n\ndef load(c):\n    return open(os.path.join(c, 'journal.md')).read()\n\n"
                    "def save(c):\n    open(os.path.join(c, 'journal.md'), 'a').write('x')\n",
    # hands a store path to a callback: the test's stub writes it, so the module is not a writer
    "fx_callback.py": "import os\n\ndef run(c, cb):\n    return cb(os.path.join(c, 'stage.json'))\n",
    # parks a copy under .git: nothing under .git is a store
    "fx_parker.py": "import os\n\ndef park(c):\n    d = os.path.join(c, '.git', 'parked', 'design', 'concepts', 'M')\n"
                    "    os.makedirs(d)\n    open(os.path.join(d, 'stage.json'), 'w').write('{}')\n",
    # Codex round 1, each a false NO_WRITE_SEEN the first build gave:
    # a def on line 1, only imported (the module body started on line 1 too)
    "fx_lineone.py": "def save(c):\n    import os\n    open(os.path.join(c, 'stage.json'), 'w').write('{}')\n",
    # the store named in a module constant, the open split over two lines, only imported
    "fx_const.py": "import os\nSTORE = 'stage.json'\n\ndef save(c):\n    with open(os.path.join(c, STORE),\n"
                   "              'w') as f:\n        f.write('{}')\n",
    # the write inside a generator nobody iterates
    "fx_gen.py": "STORE = 'stage.json'\n\ndef make(p):\n    return (open(p, 'w') for _ in range(1))\n",
    # a relative open from inside version/
    "fx_reldir.py": "import os\n\ndef save(c):\n    v = os.path.join(c, 'version')\n    os.makedirs(v, exist_ok=True)\n"
                    "    here = os.getcwd()\n    os.chdir(v)\n    try:\n        open('stage_record.json', 'w').write('{}')\n"
                    "    finally:\n        os.chdir(here)\n",
    # stage_record.json outside a version folder is not a store
    "fx_conversion.py": "import os\n\ndef save(c):\n    d = os.path.join(c, 'conversion')\n    os.makedirs(d)\n"
                        "    open(os.path.join(d, 'stage_record.json'), 'w').write('{}')\n",
    # a rename onto version/stage_record.json through a dir_fd
    "fx_dirfd.py": "import os\n\ndef save(c):\n    v = os.path.join(c, 'version')\n    os.makedirs(v, exist_ok=True)\n"
                   "    t = os.path.join(c, 't.tmp')\n    open(t, 'w').write('{}')\n    fd = os.open(v, os.O_RDONLY)\n"
                   "    try:\n        os.replace(t, 'stage_record.json', dst_dir_fd=fd)\n    finally:\n        os.close(fd)\n",
    # Codex round 2: two lambdas on one line, only the clean one called
    "fx_twolambda.py": "STORE = 'stage.json'\ncallbacks = (lambda: None, lambda: open(STORE, 'w'))\n",
    # an attribute open with a mode from a variable, never called
    "fx_attrmode.py": "STORE = 'stage.json'\n\ndef save(p, mode):\n    return p.open(mode)\n",
    # a decorated class naming a store, its body run on import: measured, not a false NOT_MEASURED
    "fx_decorated.py": "def identity(c):\n    return c\n\n\n@identity\nclass Reader:\n    STORE = 'stage.json'\n",
    # starts a Python child with -I: the hook cannot follow it (names stage.json only here)
    "fx_spawner.py": "import subprocess, sys\n\ndef go():\n    # writes 'stage.json' in the child\n"
                     "    subprocess.run([sys.executable, '-I', '-c', 'pass'], check=True)\n",
}
TESTS = {
    "selftest_fx_writer.py": "import fx_writer, tempfile\nfx_writer.save(tempfile.mkdtemp())\n",
    "selftest_fx_replace_writer.py": "import subprocess, sys, os, tempfile\n"
                                     "here = os.path.dirname(os.path.abspath(__file__))\n"
                                     "subprocess.run([sys.executable, os.path.join(here, 'fx_replace_writer.py'),"
                                     " tempfile.mkdtemp()], check=True)\n",
    "selftest_fx_via_helper.py": "import fx_via_helper, tempfile\nfx_via_helper.save(tempfile.mkdtemp())\n",
    # the test's own fixture write of stage.json: blames nobody
    "selftest_fx_reader.py": "import fx_reader, os, tempfile\nd = tempfile.mkdtemp()\n"
                             "open(os.path.join(d, 'stage.json'), 'w').write('{}')\nfx_reader.load(d)\n",
    "selftest_fx_partly.py": "import fx_partly, os, tempfile\nd = tempfile.mkdtemp()\n"
                             "open(os.path.join(d, 'journal.md'), 'w').write('')\nfx_partly.load(d)\n",
    "selftest_fx_callback.py": "import fx_callback, tempfile\n\ndef stub(p):\n    open(p, 'w').write('{}')\n\n"
                               "fx_callback.run(tempfile.mkdtemp(), stub)\n",
    "selftest_fx_parker.py": "import fx_parker, tempfile\nfx_parker.park(tempfile.mkdtemp())\n",
    "selftest_fx_lineone.py": "import fx_lineone\n",
    "selftest_fx_const.py": "import fx_const\n",
    "selftest_fx_gen.py": "import fx_gen, tempfile, os\nfx_gen.make(os.path.join(tempfile.mkdtemp(), fx_gen.STORE))\n",
    "selftest_fx_reldir.py": "import fx_reldir, tempfile\nfx_reldir.save(tempfile.mkdtemp())\n",
    "selftest_fx_conversion.py": "import fx_conversion, tempfile\nfx_conversion.save(tempfile.mkdtemp())\n",
    "selftest_fx_dirfd.py": "import fx_dirfd, tempfile\nfx_dirfd.save(tempfile.mkdtemp())\n",
    "selftest_fx_twolambda.py": "import fx_twolambda\nfx_twolambda.callbacks[0]()\n",
    "selftest_fx_attrmode.py": "import fx_attrmode\n",
    "selftest_fx_decorated.py": "import fx_decorated\n",
    # a copy identical to fx_unexercised.py, loaded (its hash cached), then rewritten clean and called: the rewritten
    # copy must not stand in for the real one
    "selftest_fx_unexercised_reload.py":
        "import importlib.util, os, tempfile\nhere = os.path.dirname(os.path.abspath(__file__))\n"
        "d = tempfile.mkdtemp()\np = os.path.join(d, 'src', 'RimMandrake', 'rimflow', 'fx_unexercised.py')\n"
        "os.makedirs(os.path.dirname(p))\nopen(p, 'w').write(open(os.path.join(here, 'fx_unexercised.py')).read())\n"
        "def load():\n    spec = importlib.util.spec_from_file_location('fxu_copy', p)\n"
        "    m = importlib.util.module_from_spec(spec)\n    spec.loader.exec_module(m)\n    return m\n"
        "load()\nopen(p, 'w').write('import os\\n\\ndef save(c):\\n    return 1  # rewritten clean, longer\\n')\n"
        "load().save(0)\n",
    # strips the hook from its own environment, then starts a child that inherits that
    "selftest_fx_spawner_env.py": "import os, subprocess, sys\nos.environ.pop('PYTHONPATH', None)\n"
                                  "subprocess.run([sys.executable, '-c', 'pass'], check=True)\n",
    # a different copy of fx_unexercised.py, run from elsewhere: it must not stand in for the real one
    "selftest_fx_unexercised_copy.py": "import os, subprocess, sys, tempfile\nd = tempfile.mkdtemp()\n"
                           "p = os.path.join(d, 'src', 'RimMandrake', 'rimflow', 'fx_unexercised.py')\nos.makedirs(os.path.dirname(p))\n"
                           "open(p, 'w').write('import os\\n\\ndef save(c):\\n    return 1\\n\\nsave(0)\\n')\n"
                           "subprocess.run([sys.executable, p], check=True)\n",
    # a failing test whose output is not text
    "selftest_fx_spawner.py": "import fx_spawner\nfx_spawner.go()\n",
    "selftest_fx_reader_noisy.py": "import os\nos.write(1, b'\\xff\\xfe')\nraise SystemExit(1)\n",
}
BYTES = {
    # a valid latin-1 module (coding cookie) that writes stage.json, never run
    "fx_latin1.py": b"# -*- coding: latin-1 -*-\n# caf\xe9\nimport os\n\ndef save(c):\n"
                    b"    open(os.path.join(c, 'stage.json'), 'w').write('{}')\n",
    # a .py no codec reads
    "fx_undecodable.py": b"# -*- coding: utf-8 -*-\nx = '\xff\xfe'\n",
}


def fixture(names):
    root = tempfile.mkdtemp(prefix="census_fx_")
    d = os.path.join(root, "src", "RimMandrake", "rimflow")
    os.makedirs(d)
    for n in names:
        if n in BYTES:
            with open(os.path.join(d, n), "wb") as f:
                f.write(BYTES[n])
            continue
        body = MODS.get(n) or TESTS.get(n)
        with open(os.path.join(d, n), "w") as f:
            f.write(body)
    return root


def oracle(root, env=None, args=("--writers-only",)):
    r = subprocess.run([sys.executable, ORACLE] + list(args) + ["--root", root], capture_output=True, text=True,
                       timeout=300, env=dict(os.environ, **(env or {})))
    return r.returncode, r.stdout + r.stderr


def writer_lines(out):
    """-> the set of module basenames on the oracle's WRITER lines."""
    return {ln.split()[1].split("/")[-1] for ln in out.splitlines() if ln.strip().startswith("WRITER ")}


def tail(out):
    return out.strip().splitlines()[-3:] if out.strip() else "(no output)"


ALL = list(MODS) + list(TESTS) + list(BYTES)
roots = []
atexit.register(lambda: [shutil.rmtree(r, ignore_errors=True) for r in roots])
try:
    import store_write_census as C
except Exception as e:                                        # the base: the census does not exist yet
    C = None
    ok(False, "store_write_census imports (%s: %s)" % (type(e).__name__, e))

if C is not None:
    root = fixture(ALL)
    roots.append(root)
    rec = C.census(root, workers=4)
    v = {m.split("/")[-1]: c["verdict"] for m, c in rec.get("modules", {}).items()}
    ok(rec.get("status") == "ok" and rec.get("probe", {}).get("caught") is True,
       "the planted probe write is caught before the record is trusted (status %r, probe %r)"
       % (rec.get("status"), rec.get("probe")))
    ok(v.get("fx_writer.py") == "WRITER", "a module opening stage.json for writing is a WRITER (%r)" % v.get("fx_writer.py"))
    ok(v.get("fx_replace_writer.py") == "WRITER",
       "an os.replace onto journal.md in a child process is a WRITER (%r)" % v.get("fx_replace_writer.py"))
    ok(v.get("fx_via_helper.py") == "WRITER" and v.get("fx_helper.py") != "WRITER",
       "a write through a helper blames the module naming the store, not the helper (%r, %r)"
       % (v.get("fx_via_helper.py"), v.get("fx_helper.py")))
    ok(v.get("fx_reader.py") == "NO_WRITE_SEEN", "a reader that writes another file is NO_WRITE_SEEN (%r)"
       % v.get("fx_reader.py"))
    ok(v.get("fx_callback.py") == "NO_WRITE_SEEN",
       "a store write by the test's own stub, called back by the module, blames nobody (%r)" % v.get("fx_callback.py"))
    ok(v.get("fx_parker.py") == "NO_WRITE_SEEN", "a copy parked under .git is not a store (%r)" % v.get("fx_parker.py"))
    ok(v.get("fx_unexercised.py") == "NOT_MEASURED", "a module no selftest runs is NOT_MEASURED (%r)"
       % v.get("fx_unexercised.py"))
    part = rec.get("modules", {}).get("src/RimMandrake/rimflow/fx_partly.py", {})
    ok(part.get("verdict") == "NOT_MEASURED" and any("save" in x for x in part.get("never_ran", [])),
       "a store function that never ran is NOT_MEASURED and named (%r, %r)" % (part.get("verdict"),
                                                                              part.get("never_ran")))
    ok(rec.get("fixture_writes", 0) >= 3 and not any("selftest_" in m for m, c in rec.get("modules", {}).items()
                                                     if c["verdict"] == "WRITER"),
       "a selftest's own fixture writes blame nobody (%r fixture writes)" % rec.get("fixture_writes"))
    M = rec.get("modules", {})

    def nm(name, needle):
        m = M.get("src/RimMandrake/rimflow/" + name, {})
        return m.get("verdict") == "NOT_MEASURED" and any(needle in x for x in m.get("never_ran", []))
    ok(nm("fx_lineone.py", "save"), "a def on line 1 that never ran is NOT_MEASURED, the module body is no stand-in (%r)"
       % M.get("src/RimMandrake/rimflow/fx_lineone.py"))
    ok(nm("fx_const.py", "save"), "a two-line open of a module-constant store that never ran is NOT_MEASURED (%r)"
       % M.get("src/RimMandrake/rimflow/fx_const.py"))
    ok(nm("fx_gen.py", "<genexpr>"), "a writing generator nobody iterated is NOT_MEASURED (%r)"
       % M.get("src/RimMandrake/rimflow/fx_gen.py"))
    ok(v.get("fx_reldir.py") == "WRITER", "a relative open of stage_record.json inside version/ is a WRITER (%r)"
       % v.get("fx_reldir.py"))
    ok(v.get("fx_conversion.py") == "NO_WRITE_SEEN", "conversion/stage_record.json is not a store (%r)"
       % v.get("fx_conversion.py"))
    ok(v.get("fx_dirfd.py") == "WRITER", "a rename onto version/stage_record.json through a dir_fd is a WRITER (%r)"
       % v.get("fx_dirfd.py"))
    un = rec.get("unhooked_children", [])
    ok(any("-I" in (u.get("why") or "") and any("fx_spawner" in c for c in u.get("chain", [])) for u in un),
       "a Python child started with -I is listed as unhooked, with who started it (%r)" % un[:2])
    ok(nm("fx_unexercised.py", "save"), "a differing copy run elsewhere does not stand in for the real module (%r)"
       % M.get("src/RimMandrake/rimflow/fx_unexercised.py"))
    ok(nm("fx_latin1.py", "save"), "a latin-1 module is read by its coding cookie and is a candidate (%r)"
       % M.get("src/RimMandrake/rimflow/fx_latin1.py"))
    ok(nm("fx_undecodable.py", "decoded"), "an undecodable .py is a candidate never measured, not skipped (%r)"
       % M.get("src/RimMandrake/rimflow/fx_undecodable.py"))
    ok(nm("fx_twolambda.py", "shares its line"), "two lambdas on one line, one called: the other is NOT_MEASURED (%r)"
       % M.get("src/RimMandrake/rimflow/fx_twolambda.py"))
    ok(nm("fx_attrmode.py", "save"), "p.open(mode_var) never called is NOT_MEASURED (%r)"
       % M.get("src/RimMandrake/rimflow/fx_attrmode.py"))
    ok(v.get("fx_decorated.py") == "NO_WRITE_SEEN", "a decorated class body run on import is measured (%r)"
       % M.get("src/RimMandrake/rimflow/fx_decorated.py"))
    ran = {t["test"].split("/")[-1]: t["rc"] for t in rec.get("tests", [])}
    ok(ran.get("selftest_fx_unexercised_copy.py") == 0 and ran.get("selftest_fx_unexercised_reload.py") == 0,
       "the two copy tests ran and passed, so the copy checks above saw a copy run (%r)"
       % {k: ran.get(k) for k in ("selftest_fx_unexercised_copy.py", "selftest_fx_unexercised_reload.py")})
    ok(any("drops the hook" in (u.get("why") or "") and u.get("test", "").endswith("selftest_fx_spawner_env.py")
           for u in un), "a child inheriting an env stripped of the hook is listed as unhooked (%r)" % un[:3])
    noisy = [t for t in rec.get("tests", []) if t["test"].endswith("selftest_fx_reader_noisy.py")]
    ok(noisy and noisy[0]["rc"] == 1, "a red test printing bytes that are not text is counted, not a crash (%r)" % noisy)
    blind = C.census(root, workers=2, hook_dir=os.path.join(root, "no_such_hook_dir"))
    ok(blind.get("status") == "could_not_look" and "probe" in (blind.get("cause") or ""),
       "a hook that cannot run is could_not_look with its cause (%r: %r)" % (blind.get("status"), blind.get("cause")))

    def utils(root, text):
        d = os.path.join(root, "src", "RimMandrake", "Utils")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "pipeline_tests.json"), "w") as f:
            f.write(text)
    rm = fixture(["fx_helper.py"])
    utils(rm, json.dumps({"tests": [{"test": "src/RimMandrake/Utils/selftest_gone.py"}]}))
    rb = fixture(["fx_reader.py", "selftest_fx_reader.py"])
    utils(rb, "{not json")
    roots += [rm, rb]
    a, b = C.census(rm, workers=2), C.census(rb, workers=2)
    ok(a.get("status") == "could_not_look" and "missing" in (a.get("cause") or ""),
       "a configured test that does not exist, and nothing else to run, is could_not_look (%r)" % a.get("cause"))
    ok(b.get("status") == "could_not_look" and "test list" in (b.get("cause") or ""),
       "an unreadable pipeline_tests.json is could_not_look, not a crash (%r)" % b.get("cause"))

# the oracle's four answers, by exit code
r1 = fixture(ALL)
r0 = fixture(["fx_reader.py", "selftest_fx_reader.py"])
r2 = fixture(["fx_reader.py", "selftest_fx_reader.py", "fx_unexercised.py"])
roots += [r1, r0, r2]
rc, out = oracle(r1)
want = {"fx_writer.py", "fx_replace_writer.py", "fx_via_helper.py", "fx_reldir.py", "fx_dirfd.py"}
ok(rc == 1 and writer_lines(out) == want, "oracle: writers measured -> exit 1, names exactly them (exit %s, %r)"
   % (rc, sorted(writer_lines(out) ^ want)))
rc, out = oracle(r0)
ok(rc == 0 and "PASS 1/1" in out, "oracle: a measured reader only -> exit 0, PASS 1/1 (exit %s: %s)"
   % (rc, out.strip().splitlines()[-1:] if out.strip() else ""))
rc, out = oracle(r2)
ok(rc == 2 and "NOT MEASURED" in out and "fx_unexercised.py" in out,
   "oracle: an unexercised module -> exit 2, NOT MEASURED, named (exit %s: %s)" % (rc, tail(out)))
r3 = fixture(["fx_reader.py", "selftest_fx_reader.py", "fx_spawner.py", "selftest_fx_spawner.py"])
roots.append(r3)
rc, out = oracle(r3)
ok(rc == 2 and "without the hook" in out, "oracle: a Python child that ran without the hook -> exit 2, NOT MEASURED "
   "(exit %s: %s)" % (rc, tail(out)))
rc, out = oracle(r0, env={"RM_STORE_CENSUS_HOOK_DIR": os.path.join(r0, "no_such_hook_dir")})
ok(rc == 3 and "COULD NOT LOOK" in out, "oracle: the hook cannot run -> exit 3, COULD NOT LOOK (exit %s)" % rc)

# a record read with --census must be whole: a forged "ok" with nothing in it is refused
if C is not None:
    forged = os.path.join(r2, "forged.json")
    good = C.census(r2, workers=2)
    for label, rec in (("empty modules, probe not caught", dict(good, modules={}, probe={"caught": False})),
                       ("a current candidate missing", dict(good, modules={k: v for k, v in good["modules"].items()
                                                                             if "fx_unexercised" not in k})),
                       ("an unknown verdict", dict(good, modules=dict(good["modules"], **{
                           "src/RimMandrake/rimflow/fx_unexercised.py": {"verdict": "FINE"}}))),
                       ("no tests", dict(good, tests=[]))):
        with open(forged, "w") as f:
            json.dump(rec, f)
        rc, out = oracle(r2, args=("--writers-only", "--census", forged))
        ok(rc == 3 and "COULD NOT LOOK" in out, "oracle --census: a record with %s is COULD NOT LOOK (exit %s: %s)"
           % (label, rc, tail(out)))
    with open(forged, "w") as f:
        json.dump(good, f)
    rc, out = oracle(r2, args=("--writers-only", "--census", forged))
    ok(rc == 2, "oracle --census: a whole record of this tree is read as measured (exit %s: %s)" % (rc, tail(out)))
    utils(r2, json.dumps({"tests": [{"test": "src/RimMandrake/rimflow/selftest_fx_reader.py"}]}))
    rc, out = oracle(r2, args=("--writers-only", "--census", forged))
    ok(rc == 3 and "other code" in out, "oracle --census: a record taken before pipeline_tests.json changed is "
       "COULD NOT LOOK (exit %s: %s)" % (rc, tail(out)))

# the store clauses: a JSON view must be an object, an archive must be a file
rv = tempfile.mkdtemp(prefix="census_view_")
roots.append(rv)
c = os.path.join(rv, "design", "concepts", "Xv")
os.makedirs(os.path.join(c, "archive_pre_ledger", "journal.md"))
os.makedirs(os.path.join(c, "version"))
with open(os.path.join(c, "stage.json"), "w") as f:
    f.write('["_view"]')
with open(os.path.join(c, "version", "stage_record.json"), "w") as f:
    f.write('"_view"')
os.chmod(os.path.join(c, "archive_pre_ledger", "journal.md"), 0o555)
rc, out = oracle(rv, args=("Xv",))
os.chmod(os.path.join(c, "archive_pre_ledger", "journal.md"), 0o755)
# stage.json left the cutover contract in a0409779a5 (the packet reads the Designer step from it): two stores remain
for rel in ("journal.md", "version/stage_record.json"):
    ok(("FAIL  Xv: %s is a generated view" % rel) in out, "oracle: %s as a JSON non-object or an archived folder is "
       "no view and no archive (%s)" % (rel, [ln for ln in out.splitlines() if rel in ln][:1]))

print("%d checks, %d failed" % (COUNT[0], len(FAILS)))
sys.exit(1 if FAILS else 0)
