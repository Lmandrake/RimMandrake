#!/usr/bin/env python3
"""selftest_snapshot_id_lane_rename.py — a sheet rebuild keeps the previous snapshotId only when every old letter
still shows the same pictures AND sits in the same lane (SHEET_SNAPSHOTID_FIX_LANE_RENAME).

Until this fix art_sheet.py kept the id whenever the new columns were a superset of the old, even when graphic_of lanes
were renamed or moved, and overwrote the snapshot file under the same id; a record saved against that id then resolved
through today's lanes (the stale slot keys of ENACT_STALE_SLOT_KEY_MIGRATE_PATH: RM_BrineElder keyed by RM_SaltChimney).

  1 unchanged rebuild: id kept
  2 columns added (superset), lanes of the old letters unchanged: id kept
  3 an old letter's lane renamed (same pictures): new id
  4 an old letter moved to another existing lane: new id
  5 an old letter's pictures changed: new id
  6 a row dropped from the rebuild: new id
  7 a previous build with no graphic_of recorded: judged on pictures only (kept)
  8 no previous rows: new id
  9 the biome build path calls keeps_snapshot_id (the old pictures-only superset test is gone)
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import art_sheet as A  # noqa: E402

FAIL = []


def check(name, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'} {name}: got {got}, want {want}")
    if not ok:
        FAIL.append(name)


def row(cols, gof=None):
    r = {"columns": {l: {"single": f} for l, f in cols.items()}}
    if gof is not None:
        r["graphic_of"] = dict(gof)
    return r


prev = {"RM_BrineElder": row({"A": "a.png", "B": "b.png"},
                             {"A": "Things/Building/Natural/RM_SaltChimney", "B": "Things/Building/Natural/RM_SaltChimney"}),
        "RM_Glasmaw": row({"A": "g.png"}, {"A": "Things/Plant/RM_Glasmaw"})}

check("1 unchanged", A.keeps_snapshot_id(prev, {k: dict(v) for k, v in prev.items()}), True)

added = {"RM_BrineElder": row({"A": "a.png", "B": "b.png", "C": "c.png"},
                              {"A": "Things/Building/Natural/RM_SaltChimney", "B": "Things/Building/Natural/RM_SaltChimney",
                               "C": "Things/Building/Natural/RM_SaltChimney"}),
         "RM_Glasmaw": prev["RM_Glasmaw"]}
check("2 superset, lanes same", A.keeps_snapshot_id(prev, added), True)

renamed = {"RM_BrineElder": row({"A": "a.png", "B": "b.png", "C": "c.png"},
                                {"A": "Things/Building/Natural/RM_BrineElder", "B": "Things/Building/Natural/RM_BrineElder",
                                 "C": "Things/Building/Natural/RM_BrineElder"}),
           "RM_Glasmaw": prev["RM_Glasmaw"]}
check("3 lane renamed", A.keeps_snapshot_id(prev, renamed), False)

moved = {"RM_BrineElder": row({"A": "a.png", "B": "b.png"},
                              {"A": "Things/Building/Natural/RM_SaltChimney", "B": "Things/Building/Natural/RM_SaltChimney_j"}),
         "RM_Glasmaw": prev["RM_Glasmaw"]}
check("4 letter moved lanes", A.keeps_snapshot_id(prev, moved), False)

repic = {"RM_BrineElder": row({"A": "a.png", "B": "b2.png"}, prev["RM_BrineElder"]["graphic_of"]),
         "RM_Glasmaw": prev["RM_Glasmaw"]}
check("5 pictures changed", A.keeps_snapshot_id(prev, repic), False)

check("6 row dropped", A.keeps_snapshot_id(prev, {"RM_BrineElder": prev["RM_BrineElder"]}), False)

old_build = {"RM_Glasmaw": row({"A": "g.png"})}
check("7 old build without graphic_of", A.keeps_snapshot_id(old_build, {"RM_Glasmaw": row({"A": "g.png"}, {"A": "X"})}), True)

check("8 no previous rows", A.keeps_snapshot_id({}, prev), False)

src = (HERE / "art_sheet.py").read_text()
check("9 build path uses keeps_snapshot_id",
      ("keeps_snapshot_id(prev_rows, snap_rows)" in src, "superset = bool(prev_rows)" in src), (True, False))

print("RESULT", "FAIL " + ", ".join(FAIL) if FAIL else "PASS")
sys.exit(1 if FAIL else 0)
