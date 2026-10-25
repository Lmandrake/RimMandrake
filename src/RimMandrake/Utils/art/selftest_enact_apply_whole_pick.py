#!/usr/bin/env python3
"""selftest_enact_apply_whole_pick.py — enact apply lands a pick WHOLE or not at all (ENACT_APPLY_REFUSED_HARDEN_PARTIAL_PICK):
one refused facing keeps its siblings out, the rebind of that group is not made, and a folder shed is gated on the
folder pick's own install, not on any install of the row."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
FAILS = []


def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        FAILS.append(m)


def main():
    root = Path(tempfile.mkdtemp())
    for d in ("ledger/events", "store", "src"):
        (root / d).mkdir(parents=True)
    os.environ.update(ART_LEDGER_DIR=str(root / "ledger"), ARTSTORE=str(root / "store"), ART_SRC_ROOT=str(root / "src"),
                      RIMFLOW_SEAT="TEST")
    import enact as E
    L = E.L
    dec = root / "d.json"
    dec.write_text('{"decisions": {}}')
    ins = lambda row, letter, rel, **k: {"row": row, "letter": letter, "mod": "RimMandrake/M", "rel": rel, "sha": "s" + rel,
                                         "ruling": "r1", "kind": "slot", "rebind": None, "names": {row}, **k}
    P = {"sheet": "t", "biome": "b", "conflicts": [], "todo": [], "withdraw": [], "queue": [], "refile": [], "purge": [],
         "cuts": [], "followed": {}, "asks": [], "done": [], "blocked": [], "installed_already": [], "in_game_not_ours": 0,
         "install": [ins("RM_A", "B", "Things/A_east.png", rebind={"old": "o", "new": "n"}), ins("RM_A", "B", "Things/A_north.png"),
                     ins("RM_F", "V", "Things/F/v_1.png"),
                     ins("RM_F", "P", "Things/F/p_1.png")],
         "retire": [{"row": "RM_F", "mod": "RimMandrake/M", "rel": "Things/F/old.png", "sha": "x", "gate": ["P"]}]}
    landed, retired = [], []

    def fake_install(mod, rel, sha, *, ruling_id=None, dry_run=False, **k):
        if rel.endswith("A_north.png") or rel.endswith("p_1.png"):
            raise L.Refused("owner-kept live file")
        if not dry_run:
            landed.append(rel)
        return {"status": "installed"}

    E.build_plan = lambda *a, **k: P
    E.I.ingest = lambda *a, **k: {"ok": True}
    rebinds = []
    E.rebind_defs = lambda src, names, old, new: rebinds.append((old, new)) or []
    L.install = fake_install
    L.retire = lambda path, reason=None: retired.append(str(path))
    R = E.enact(dec, apply=True, no_deploy=True)
    check(R["ok"], "apply ran")
    check("Things/A_east.png" not in landed and "Things/A_north.png" not in landed,
          f"a pick with one refused facing lands none of its facings ({landed})")
    check(not rebinds, "no def is rebound onto a half-landed pick")
    check("Things/F/v_1.png" in landed and not retired, f"folder pick refused: variant lands, folder does not shed ({retired})")
    check(any("A_north.png" in c for c in R["conflicts"]), "the refusal is listed")
    sys.exit(1 if FAILS else 0)


main()
