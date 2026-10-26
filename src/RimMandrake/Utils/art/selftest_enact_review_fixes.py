#!/usr/bin/env python3
"""Selftest for two enact.py findings from the ENACT_STALE_KEY_FIX_UNREVIEWED full-file review.

  1 SHARED-FILE CLASH READ AS REFLECTED: two rows whose picks go to ONE file get a single conflict line prefixed
    "RowA, RowB: ..."; ruling_status matched a conflict to a row by the text before the first colon, so neither row
    matched, and with the clash installs dropped both rows read "reflected" although neither pick was installed.
  2 CUT LEFT A FOLDER'S TEXTURES: a cut def whose texPath is a Graphic_Random folder (Things/Plant/RM_X) has its
    files at Things/Plant/RM_X/RM_X_a.png, whose parsed res is the file's own stem, never the folder; the cut step
    compared res to the texPath only, so the files in the folder stayed in the game.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import selftest_enact as T  # noqa: E402
import selftest_enact_ws as W  # noqa: E402

FAILS = T.FAILS
check = T.check


def case_clash_status():
    F = W.build(T.SCRATCH / f"enact_reviewfix1_{os.getpid()}")
    try:
        import artledger as L
        import enact as E
        doc = json.loads(F["decisions"].read_text())
        sp = Path(doc["snapshot"])
        snap = json.loads(sp.read_text())
        os.environ["ART_BIOME_SHEETS_DIR"] = str(F["root"] / "biomes")
        saved = E.snapshot_revisions
        E.snapshot_revisions = lambda p: [snap]
        try:
            kr = snap["rows"]["RSW_Kite"]
            k2 = json.loads(json.dumps(kr))
            k2["columns"]["B"] = {f: L.store_put_bytes(T.noise_png(1950 + n))
                                  for n, f in enumerate(sorted(kr["columns"]["B"]))}
            snap["rows"]["RSW_Kite2"] = k2
            snap["built"] = "2026-10-12T00:00:00-0700"
            sp.write_text(json.dumps(snap))
            at = "2026-10-12T10:00:00.000Z"
            rec = {"schema": 2, "at": at, "decidedAt": at, "note": "", "decision": "B"}
            d = json.loads(json.dumps(doc))
            d["decisions"] = {"RSW_Kite": dict(rec), "RSW_Kite2": dict(rec)}
            p = F["root"] / "clash.decisions.json"
            p.write_text(json.dumps(d))
            E.reset_caches()
            r = E.enact(p, apply=False, no_deploy=True)
            clash = [c for c in r["conflicts"] if "ONE file" in c]
            check(bool(clash), f"1 fixture: the two rows' picks clash on one file ({r['conflicts']})")
            E.reset_caches()
            st = E.ruling_status(p)["rows"]
            check(st.get("RSW_Kite", {}).get("state") == "conflict" and st.get("RSW_Kite2", {}).get("state") == "conflict",
                  f"1 both rows of a shared-file clash read 'conflict', never 'reflected' ({st.get('RSW_Kite')} / "
                  f"{st.get('RSW_Kite2')})")
            check("ONE file" in st.get("RSW_Kite", {}).get("detail", ""),
                  "1 ...and the row's detail names the clash")
        finally:
            E.snapshot_revisions = saved
            os.environ.pop("ART_BIOME_SHEETS_DIR", None)
    finally:
        shutil.rmtree(F["root"], ignore_errors=True)


def case_cut_folder():
    F = T.build(T.SCRATCH / f"enact_reviewfix2_{os.getpid()}")
    try:
        import artledger as L
        import enact as E
        src = F["src"]
        races = src / "RimMandrake/TestMod/Defs/ThingDefs_Races/Races.xml"
        folder = "Things/Plant/RM_CutVine"
        races.write_text(races.read_text().replace("Things/Pawn/Animal/RM_Cut/RM_Cut", folder))
        tex = src / "RimMandrake/TestMod/Textures"
        evs, files = [], []
        for n, leaf in enumerate(("RM_CutVine_a.png", "RM_CutVine_b.png")):
            rel = f"{folder}/{leaf}"
            sha = L.store_put_bytes(T.noise_png(2100 + n))
            f = tex / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(L.store_get(sha))
            files.append(f)
            evs.append({"type": "live", "id": L.det_id("live", rel), "mod": T.MOD, "rel": rel, "sha": sha,
                        "prev": None, "reason": "fixture", "ts": "2026-10-01T00:00:00"})
        # a sibling folder whose name merely starts with the cut one: not part of the cut def's graphic
        other_rel = "Things/Plant/RM_CutVineTall/RM_CutVineTall_a.png"
        osha = L.store_put_bytes(T.noise_png(2200))
        other = tex / other_rel
        other.parent.mkdir(parents=True, exist_ok=True)
        other.write_bytes(L.store_get(osha))
        evs.append({"type": "live", "id": L.det_id("live", other_rel), "mod": T.MOD, "rel": other_rel, "sha": osha,
                    "prev": None, "reason": "fixture", "ts": "2026-10-01T00:00:00"})
        with open(F["led"] / "events" / "TEST.jsonl", "a") as fh:
            for e in evs:
                fh.write(json.dumps(e) + "\n")
        E.reset_caches()
        R = E.enact(F["decisions"], apply=False, holds=["vine"], no_deploy=True)
        cuts = {c["row"]: c["plan"] for c in R["plan"]["cuts"]}
        check(cuts.get("RM_Cut", {}).get("tex_retire") == [folder],
              f"2 fixture: the cut plans to retire the def's folder texPath ({cuts.get('RM_Cut', {}).get('tex_retire')})")
        E.reset_caches()
        R = E.enact(F["decisions"], apply=True, holds=["vine"], no_deploy=True, redo_jobs_out=F["root"] / "jobs.json")
        check(R["ok"], f"2 apply ok ({R.get('error')})")
        check(not any(f.exists() for f in files),
              f"2 a cut def's Graphic_Random folder files are retired ({[f.name for f in files if f.exists()]})")
        check(other.exists(), "2 ...a sibling folder that only shares the name prefix is left alone")
    finally:
        shutil.rmtree(F["root"], ignore_errors=True)


def main():
    case_clash_status()
    case_cut_folder()
    print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAIL'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
