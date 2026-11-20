#!/usr/bin/env python3
"""Offline: maturation.run_diff survives a diffed file that is not UTF-8 (RIMMANDRAKE_DECODE_RUN_DIFF_CP1252_DASH_CRASHED_NEXT).

FlowWorks in-game visit 2 (2026-11-19): `maturation.py next FlowWorks` died with UnicodeDecodeError (byte 0x97, a cp1252 dash in
a Windows-written evidence log) inside run_diff, so the exit reader printed no reason at all. A temp git repo with an
origin/main ref, one committed file and a working-tree change holding byte 0x97; the run record is faked. PASS: run_diff returns
the diff text and the item, and the text names the file."""
import os
import subprocess
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation as M  # noqa: E402


def main():
    tmp = tempfile.mkdtemp(prefix="run_diff_bytes_")
    g = lambda *a: subprocess.run(["git", "-C", tmp] + list(a), capture_output=True, check=True)  # noqa: E731
    g("init", "-q", "-b", "main")
    g("config", "user.email", "t@t"); g("config", "user.name", "t")
    p = os.path.join(tmp, "design", "concepts", "Foo", "evidence.log")
    os.makedirs(os.path.dirname(p))
    open(p, "w").write("start\n")
    g("add", "-A"); g("commit", "-q", "-m", "base")
    g("update-ref", "refs/remotes/origin/main", "HEAD")
    with open(p, "ab") as f:
        f.write(b"Pit, 1.0 m \x97 Hole 4 m\n")
    sys.modules["detached_helper"] = types.SimpleNamespace(read_record=lambda unit: {"at": time.time() + 60, "item": "X_ITEM"})
    os.environ["RM_DETACHED_UNIT"] = "fake-unit"
    try:
        text, item = M.run_diff(tmp, "Foo")
    except Exception as e:  # noqa: BLE001
        print("FAIL run_diff raised %s: %s" % (type(e).__name__, e))
        return 1
    ok = isinstance(text, str) and "evidence.log" in text and item == "X_ITEM"
    print("PASS" if ok else "FAIL run_diff returned %r, %r" % (str(text)[:200], item))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
