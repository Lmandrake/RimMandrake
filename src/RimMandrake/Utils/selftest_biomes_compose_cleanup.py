#!/usr/bin/env python3
"""biomes_compose.build() strands no temp tree when it fails after its mkdtemp (BIOMESCOMPOSE_FIX_TEMPDIR_LEAK:
the compose_<mod>_* dir, ~470 MB each, was never removed on a failed copy; 3 piled up in the seat TMPDIR).
Success still hands the caller the dir (the caller deletes its parent). Offline; real manifest, private TMPDIR."""
import atexit
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_priv = tempfile.mkdtemp(prefix="st_biomes_compose_cleanup_")
atexit.register(shutil.rmtree, _priv, True)
tempfile.tempdir = os.environ["TMPDIR"] = _priv

import biomes_compose as BC  # noqa: E402
import deploy_custom_mods as D  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (" " + str(detail) if not cond else ""))
    if not cond:
        FAILS.append(name)


def left():
    return sorted(os.listdir(_priv))


holds = D.load_holds()

# sanity probe: the instrument can see a stranded dir -- a good build leaves exactly one compose_ dir
name, out, extra = BC.build(D.SRC_ROOT, D.tree, holds, log=lambda *a, **k: None)
parent = os.path.dirname(out)
check("sanity: a successful build leaves its dir for the caller", os.path.isdir(out) and
      [d for d in left() if d.startswith("compose_")] == [os.path.basename(parent)], left())
shutil.rmtree(parent, ignore_errors=True)
check("sanity: caller's rmtree of the parent empties the temp dir", left() == [], left())

# failure after mkdtemp: a copy that dies must not strand the tree
real = BC.shutil.copy2
n = {"c": 0}


def boom(*a, **k):
    n["c"] += 1
    if n["c"] > 3:
        raise OSError("injected copy failure")
    return real(*a, **k)


BC.shutil.copy2 = boom
try:
    BC.build(D.SRC_ROOT, D.tree, holds, log=lambda *a, **k: None)
    check("injected failure propagates", False, "build returned")
except OSError:
    check("injected failure propagates", True)
finally:
    BC.shutil.copy2 = real
check("failed build strands no compose_ dir", left() == [], left())

print("ALL PASS" if not FAILS else "FAILED: %s" % FAILS)
sys.exit(1 if FAILS else 0)
