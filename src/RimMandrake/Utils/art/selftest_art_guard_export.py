#!/usr/bin/env python3
"""selftest_art_guard_export.py — outside a git checkout (a clean export) `art guard worktree` judges the PNGs on disk
against the folded ledger (ROT_CARTOON_VARIANT_REPAINT_1): matching bytes pass; changed bytes, an unrecorded file, a
retired slot still on disk and a recorded-live file gone missing are each refused. And importing artledger needs no
data root (a ledger-only reader never touches the art store)."""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import art_guard  # noqa: E402
import artledger as L  # noqa: E402

FAILS = []
MOD = "src/RimUtinni/Zz"


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def ev(i, rel, sha, prev=None):
    return {"id": i, "type": "live", "mod": MOD, "rel": rel, "sha": sha, "prev": prev,
            "reason": "backfill-observed", "ts": "2026-10-01T00:00:00"}


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        tex = root / MOD / "Textures"
        tex.mkdir(parents=True)
        good, other = b"\x89PNG good", b"\x89PNG other"
        h = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
        (tex / "ok.png").write_bytes(good)
        events = [ev("1", "ok.png", h(good)), ev("2", "gone.png", h(good)),
                  ev("3", "ret.png", h(good)), ev("4", "ret.png", None, h(good))]
        idx = lambda: L.Index(list(events))  # noqa: E731
        out = art_guard.disk_vs_ledger(root, idx(), [MOD + "/Textures/ok.png"])
        check(out == [], f"bytes the ledger records live pass ({out})")
        out = dict(art_guard.disk_vs_ledger(root, idx(), [MOD]))
        check(set(out) == {MOD + "/Textures/gone.png"}, f"a recorded-live file missing from disk is refused ({out})")
        (tex / "ok.png").write_bytes(other)
        (tex / "new.png").write_bytes(other)
        (tex / "ret.png").write_bytes(good)
        out = dict(art_guard.disk_vs_ledger(root, idx(), [MOD]))
        check("records" in out.get(MOD + "/Textures/ok.png", ""), "changed bytes are refused")
        check("no art-ledger record" in out.get(MOD + "/Textures/new.png", ""), "an unrecorded PNG is refused")
        check("retired" in out.get(MOD + "/Textures/ret.png", ""), "a retired slot still on disk is refused")
        check(not art_guard._in_git(root), "a temp dir is not a git checkout")
    env = {k: v for k, v in os.environ.items() if k not in ("RM_DATA_ROOT", "AGENT_STORAGE_ROOT", "ARTSTORE")}
    env["HOME"] = tempfile.gettempdir() + "/no-such-home"
    r = subprocess.run([sys.executable, "-c", f"import sys; sys.path.insert(0, {str(HERE)!r}); import artledger"],
                       env=env, capture_output=True, text=True, timeout=60)
    check(r.returncode == 0, f"artledger imports with no data root ({r.stderr.strip()[-200:]})")
    print(f"{'FAIL' if FAILS else 'PASS'} selftest_art_guard_export: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
