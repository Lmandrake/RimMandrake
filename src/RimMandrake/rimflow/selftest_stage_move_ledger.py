#!/usr/bin/env python3
"""A stage move (maturation.advance) keeps the mod ledger's stage equal to the stage record's: ExplosiveKnockback moved to
in_game after its backfill and the ledger kept saying offline_build, so modledger_backfill_accept.py failed 1 of 7 and
every pilot-launch for it was refused. maturation.ledger_stage_move is the one writer of that event."""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maturation as MT   # noqa: E402
import modledger as L     # noqa: E402

FAIL = []


def check(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)[:300]))
    if not ok:
        FAIL.append(name)


root = tempfile.mkdtemp(prefix="stage_move_ledger_")
MOD = "ExplosiveKnockback"
try:
    check("a mod with no ledger: the move writes nothing and does not fail",
          MT.ledger_stage_move(root, MOD, "offline_build", "in_game", "BENCH") is None)
    os.makedirs(os.path.join(root, "design", "concepts", MOD))
    L.append(root, MOD, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0")
    L.append(root, MOD, "DISPATCH", "stage.enter", "stage", body={"stage": "offline_build"})
    check("setup: the ledger starts at offline_build", L.reduce(L.read(root, MOD))["stage"] == "offline_build")
    MT.ledger_stage_move(root, MOD, "offline_build", "in_game", "BENCH")
    check("after a move the ledger's stage is the record's", L.reduce(L.read(root, MOD))["stage"] == "in_game",
          L.reduce(L.read(root, MOD))["stage"])
    MT.ledger_stage_move(root, MOD, "in_game", "offline_build", "BENCH")
    check("a road back moves it back", L.reduce(L.read(root, MOD))["stage"] == "offline_build")
    check("the ledger still lints clean", not L.lint(root, MOD, None)[0], L.lint(root, MOD, None)[0][:2])
finally:
    shutil.rmtree(root, ignore_errors=True)
print("selftest_stage_move_ledger: %d failure%s" % (len(FAIL), "" if len(FAIL) == 1 else "s"))
sys.exit(1 if FAIL else 0)
