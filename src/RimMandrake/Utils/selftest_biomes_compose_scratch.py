#!/usr/bin/env python3
"""biomes_compose's scratch never lands on a tmpfs (TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK: on 2026-11-03T17:28Z
four live proofs died with ENOSPC in its compose_ mkdtemp under the 18 GB /tmp tmpfs). With TMPDIR=/tmp, a real
build() and stage_rewritten() put their dirs under ~/.seat-tmp/compose (HOME pointed at a private dir); an off-tmpfs
TMPDIR (a run_tmp run dir) is used as-is; RM_COMPOSE_TMP wins over both. Offline; real manifest."""
import atexit
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_priv = os.path.realpath(tempfile.mkdtemp(prefix="st_biomes_compose_scratch_", dir=os.path.expanduser("~")))
atexit.register(shutil.rmtree, _priv, True)
os.environ.pop("RM_COMPOSE_TMP", None)

import biomes_compose as BC  # noqa: E402
import deploy_custom_mods as D  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (" " + str(detail) if not cond else ""))
    if not cond:
        FAILS.append(name)


def with_tmp(tmpdir, home=None, override=None):
    tempfile.tempdir = tmpdir
    os.environ["HOME"] = home or os.environ["HOME"]
    if override:
        os.environ["RM_COMPOSE_TMP"] = override
    else:
        os.environ.pop("RM_COMPOSE_TMP", None)


home = os.path.join(_priv, "home")
os.makedirs(home)
want = os.path.join(home, ".seat-tmp", "compose")

# sanity probe: the instrument sees a tmpfs — /tmp is one, a dir under HOME is not
check("sanity: /tmp reads as tmpfs", BC._on_tmpfs("/tmp") and BC._on_tmpfs("/tmp/x/y"))
check("sanity: an ext4 dir does not", not BC._on_tmpfs(_priv) and not BC._on_tmpfs("/tmpfoo"))

# the 2026-11-03 case: TMPDIR is /tmp -> the scratch goes to ~/.seat-tmp/compose
with_tmp("/tmp", home)
check("TMPDIR=/tmp -> ~/.seat-tmp/compose", BC.scratch_dir() == want, BC.scratch_dir())
holds = D.load_holds()
name, out, extra = BC.build(D.SRC_ROOT, D.tree, holds, log=lambda *a, **k: None)
parent = os.path.dirname(out)
try:
    check("build() scratch is off tmpfs", not BC._on_tmpfs(out) and os.path.dirname(parent) == want, out)
finally:
    shutil.rmtree(parent, ignore_errors=True)

# stage_rewritten (mrfix_) uses the same parent
src = os.path.join(_priv, "Mod")
os.makedirs(os.path.join(src, "Defs"))
with open(os.path.join(src, "Defs", "a.xml"), "w") as f:
    f.write('<Defs><ThingDef MayRequire="old.pkg"/></Defs>')
got = BC.stage_rewritten(src, {"old.pkg": "new.pkg"}, log=lambda *a, **k: None)
gp = got[0] if isinstance(got, tuple) else got
check("stage_rewritten() rewrote something (probe)", bool(gp), got)
if gp:
    check("stage_rewritten() scratch under ~/.seat-tmp/compose", os.path.realpath(gp).startswith(want + "/"), gp)
    shutil.rmtree(os.path.dirname(gp) if os.path.basename(os.path.dirname(gp)).startswith("mrfix_") else gp, True)

# an off-tmpfs TMPDIR (run_tmp's ~/.seat-tmp/runs/<unit>) is honoured as-is
run = os.path.join(_priv, "runs", "u1")
os.makedirs(run)
with_tmp(run, home)
check("off-tmpfs TMPDIR is used as-is", BC.scratch_dir() == run, BC.scratch_dir())

# RM_COMPOSE_TMP wins
ov = os.path.join(_priv, "ov")
with_tmp("/tmp", home, ov)
check("RM_COMPOSE_TMP overrides", BC.scratch_dir() == ov and os.path.isdir(ov), BC.scratch_dir())

print("FAIL" if FAILS else "ALL PASS", len(FAILS))
sys.exit(1 if FAILS else 0)
