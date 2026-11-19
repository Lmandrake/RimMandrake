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
}


def fixture(names):
    root = tempfile.mkdtemp(prefix="census_fx_")
    d = os.path.join(root, "src", "RimMandrake", "rimflow")
    os.makedirs(d)
    for n in names:
        body = MODS.get(n) or TESTS.get(n)
        with open(os.path.join(d, n), "w") as f:
            f.write(body)
    return root


def oracle(root, env=None):
    r = subprocess.run([sys.executable, ORACLE, "--writers-only", "--root", root], capture_output=True, text=True,
                       timeout=300, env=dict(os.environ, **(env or {})))
    return r.returncode, r.stdout + r.stderr


ALL = list(MODS) + list(TESTS)
roots = []
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
    blind = C.census(root, workers=2, hook_dir=os.path.join(root, "no_such_hook_dir"))
    ok(blind.get("status") == "could_not_look" and "probe" in (blind.get("cause") or ""),
       "a hook that cannot run is could_not_look with its cause (%r: %r)" % (blind.get("status"), blind.get("cause")))

# the oracle's four answers, by exit code
r1 = fixture(ALL)
r0 = fixture(["fx_reader.py", "selftest_fx_reader.py"])
r2 = fixture(["fx_reader.py", "selftest_fx_reader.py", "fx_unexercised.py"])
roots += [r1, r0, r2]
rc, out = oracle(r1)
ok(rc == 1 and "fx_writer.py" in out and "fx_reader.py" not in out.split("NOT MEASURED")[0].split("WRITER")[-1],
   "oracle: writers measured -> exit 1, names them (exit %s)" % rc)
rc, out = oracle(r0)
ok(rc == 0 and "PASS 1/1" in out, "oracle: a measured reader only -> exit 0, PASS 1/1 (exit %s: %s)"
   % (rc, out.strip().splitlines()[-1:] if out.strip() else ""))
rc, out = oracle(r2)
ok(rc == 2 and "NOT MEASURED" in out and "fx_unexercised.py" in out,
   "oracle: an unexercised module -> exit 2, NOT MEASURED, named (exit %s)" % rc)
rc, out = oracle(r0, env={"RM_STORE_CENSUS_HOOK_DIR": os.path.join(r0, "no_such_hook_dir")})
ok(rc == 3 and "COULD NOT LOOK" in out, "oracle: the hook cannot run -> exit 3, COULD NOT LOOK (exit %s)" % rc)

for r in roots:
    shutil.rmtree(r, ignore_errors=True)
print("%d checks, %d failed" % (COUNT[0], len(FAILS)))
sys.exit(1 if FAILS else 0)
