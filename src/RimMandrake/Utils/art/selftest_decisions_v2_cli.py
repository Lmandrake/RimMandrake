#!/usr/bin/env python3
"""selftest_decisions_v2_cli.py — `decisions_v2.py` exits non-zero when a file it was asked to write was NOT written
(review wave 90). The old CLI printed "lost 4 races with the sheet's sidecar; not migrated" or a `lost_race` list and
still exited 0, so a caller (or an agent reading only the exit code) took an unwritten file for a migrated one.

The real migration and fold run on a temp decisions file; the lost race is forced by a file that changes on every
read-back (the sidecar saving his clicks in between), so the code path is the shipped one, not a stub.
"""
from __future__ import annotations

import atexit
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_selftest_decisions_v2_cli_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FAILS = []


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:400]}]"))
    if not cond:
        FAILS.append(msg)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="dv2cli-"))
    biomes = tmp / "biomes"
    biomes.mkdir()
    os.environ["ART_BIOME_SHEETS_DIR"] = str(biomes)
    os.environ["ART_OLD_TICKS_CONFIRM"] = str(tmp / "old.decisions.json")
    import decisions_v2 as D

    dec = biomes / "S1.decisions.json"
    dec.write_text(json.dumps({"sheetId": "S1", "decisions": {"RowA": {"legacyVariants": ["B"], "variants": ["B"],
                                                                        "at": "2026-10-10T00:00:00"}}}))
    (tmp / "old.decisions.json").write_text(json.dumps(
        {"decisions": {"S1|RowA|B": {"decision": "confirm", "decidedAt": "2026-10-10T00:00:00"}}}))
    D.ruled_snapshot = lambda doc, path: {"snapshotId": "x", "rows": {"RowA": {"columns": {"B": {"south": "b.png"}}}}}
    D.snapshot_versions = lambda doc: []

    # control: nothing racing -> both write and exit 0
    with contextlib.redirect_stdout(io.StringIO()):
        rc_fold = D.main(["--fold-old-ticks", "--apply"])
    check(rc_fold == 0 and json.loads(dec.read_text())["decisions"]["RowA"].get("legacyRuled", {}).get("B", {}).get("v")
          == "confirm", "control: an uncontested fold writes and exits 0", rc_fold)
    dec.write_text(json.dumps({"sheetId": "S1", "decisions": {"RowA": {"legacyVariants": ["B"], "variants": ["B"],
                                                                        "at": "2026-10-10T00:00:00"}}}))
    with contextlib.redirect_stdout(io.StringIO()):
        rc_mig = D.main([str(dec), "--apply"])
    check(rc_mig == 0 and json.loads(dec.read_text()).get("schema") == 2,
          "control: an uncontested migration writes and exits 0", rc_mig)

    # the sidecar saves on every read-back: every attempt loses, nothing is written
    dec.write_text(json.dumps({"sheetId": "S1", "decisions": {"RowA": {"legacyVariants": ["B"], "variants": ["B"],
                                                                        "at": "2026-10-10T00:00:00"}}}))
    real_read = Path.read_bytes
    n = {"reads": 0}

    def racing_read(self):
        b = real_read(self)
        if self == dec:
            n["reads"] += 1
            if n["reads"] % 2 == 0:            # the compare-before-replace read sees a fresh save
                self.write_bytes(b + b" ")
                return b + b" "
        return b
    Path.read_bytes = racing_read
    try:
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc_mig = D.main([str(dec), "--apply"])
        check("not migrated" in out.getvalue() and rc_mig != 0,
              "a migration that lost every race exits non-zero", (rc_mig, out.getvalue()[-200:]))
        n["reads"] = 0
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc_fold = D.main(["--fold-old-ticks", "--apply"])
        check("lost_race" in out.getvalue() and rc_fold != 0,
              "a fold that lost every race exits non-zero", (rc_fold, out.getvalue()[-200:]))
    finally:
        Path.read_bytes = real_read
    check(json.loads(dec.read_text())["decisions"]["RowA"].get("schema") is None,
          "sanity: the raced file really was never migrated")
    print("ALL PASS" if not FAILS else f"{len(FAILS)} FAIL")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
