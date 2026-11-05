#!/usr/bin/env python3
"""selftest_art_install_dryrun.py — ART_INSTALL_DRYRUN_FIX_STORE_WRITE, on a disposable fixture.

A  `art.py install --file X --dry-run` writes nothing: the art store, the ledger and the Textures tree are
   byte-identical before and after, and the plan it prints still names X's sha (store reads use X's bytes).
   A real `install --file X` still puts X in the store and installs it.
B  `art.py status` / `variants` print a ruling whose verdict/trust is None and a variant whose facing/role is None
   (an `:<N` format of None used to raise TypeError).
"""
from __future__ import annotations

import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_art_install_dryrun_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
FAILS = []
WRITER = "script:src/RimMandrake/Utils/art/art.py"


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def png(color):
    from PIL import Image
    b = io.BytesIO()
    Image.new("RGBA", (8, 8), color).save(b, "PNG")
    return b.getvalue()


def tree_digest(root: Path) -> dict:
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def fixture():
    tmp = Path(tempfile.mkdtemp(prefix="art-install-dryrun-"))
    os.environ["ARTSTORE"] = str(tmp / "store")
    os.environ["ART_LEDGER_DIR"] = str(tmp / "ledger")
    os.environ["ART_SRC_ROOT"] = str(tmp / "src")
    os.environ["ART_SEAT"] = "BUILD"
    (tmp / "ledger" / "events").mkdir(parents=True)
    (tmp / "ledger" / "mod_aliases.json").write_text(json.dumps({"aliases": {}}))
    (tmp / "src" / "RimMandrake" / "FlowWorks" / "Textures").mkdir(parents=True)
    (tmp / "store").mkdir()
    return tmp


def run_art(argv):
    import art
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = art.main(argv)
    return rc, out.getvalue()


def test_a(tmp):
    import artledger as L
    from PIL import Image
    f = tmp / "Transient" / "pick.png"
    f.parent.mkdir()
    # a picture with structure (a flat colour can read as a placeholder)
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    for x in range(64):
        for y in range(64):
            if (x - 32) ** 2 + (y - 32) ** 2 < 600:
                im.putpixel((x, y), (x * 4 % 256, y * 4 % 256, 120, 255))
    b = io.BytesIO(); im.save(b, "PNG"); f.write_bytes(b.getvalue())
    sha = hashlib.sha256(f.read_bytes()).hexdigest()
    mod, rel = "src/RimMandrake/FlowWorks", "Things/Pick/Pick_south.png"
    before = {k: tree_digest(tmp / k) for k in ("store", "ledger", "src")}
    rc, out = run_art(["install", mod, rel, "--file", str(f), "--reason", WRITER, "--dry-run"])
    after = {k: tree_digest(tmp / k) for k in ("store", "ledger", "src")}
    check(rc == 0, f"install --file --dry-run succeeds (rc={rc}: {out.strip()[-200:]})")
    check(sha in out, "the dry run's output names the file's sha")
    check(not L.store_has(sha), "the dry run did not put the file in the store")
    check(before["store"] == after["store"], "the store is byte-identical after a dry run")
    check(before["ledger"] == after["ledger"], "the ledger is byte-identical after a dry run")
    check(before["src"] == after["src"], "the Textures tree is byte-identical after a dry run")
    # the bytes path is the dry-run path only, and the bytes must be the sha's
    try:
        L.install(mod, rel, sha, reason=WRITER, data=f.read_bytes())
        check(False, "install(data=...) without dry_run is refused")
    except L.Refused:
        check(True, "install(data=...) without dry_run is refused")
    try:
        L.install(mod, rel, "0" * 64, reason=WRITER, data=f.read_bytes(), dry_run=True)
        check(False, "install(data=...) whose bytes do not hash to the sha is refused")
    except L.Refused:
        check(True, "install(data=...) whose bytes do not hash to the sha is refused")
    # the real install still puts and installs
    rc, out = run_art(["install", mod, rel, "--file", str(f), "--reason", WRITER])
    target = tmp / mod / "Textures" / rel
    check(rc == 0 and L.store_has(sha), f"a real install --file puts the file in the store (rc={rc})")
    check(target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == sha,
          "a real install --file writes the picture into Textures")


class FakeIndex:
    def __init__(self, res, sha):
        self.live, self.by_res, self.unpurged = {}, {res: {sha}}, set()
        self.variants = {sha: [{"kind": "render", "date": "2026-10-24", "facing": None, "role": None, "loc": None}]}

    def protected(self, sha):
        return False

    def is_purged(self, sha):
        return False

    def subject_rulings(self, keys):
        return [{"at": None, "verdict": None, "trust": None, "source_file": None, "note": None}]


def test_b():
    import art
    import artledger as L
    res, sha = "Things/Pick/Pick", "ab" * 32
    saved = (L.Index, L.scan_def_slots, art._match)
    L.Index = lambda: FakeIndex(res, sha)
    L.scan_def_slots = lambda: {}
    art._match = lambda idx, q, slots: [res]
    try:
        for cmd in ("status", "variants"):
            try:
                rc, out = run_art([cmd, "Pick"])
                check(rc == 0 and "trust=None" in out, f"art.py {cmd} prints a ruling with verdict/trust None")
                if cmd == "variants":
                    check(sha[:12] in out, "art.py variants prints a variant whose facing/role is None")
            except TypeError as e:
                check(False, f"art.py {cmd} crashed on a None field: {e}")
    finally:
        L.Index, L.scan_def_slots, art._match = saved


def main():
    sys.path.insert(0, str(HERE))
    tmp = fixture()
    test_a(tmp)
    test_b()
    print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
