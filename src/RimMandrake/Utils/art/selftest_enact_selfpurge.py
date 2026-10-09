#!/usr/bin/env python3
"""selftest_enact_selfpurge.py — a ✕ on a picture of the row's OWN pick/variant column is carried out.

Bug (Cauldron sheet, 2026-10-09): the dry run planned 3 purges, the --apply purged 0 and listed them as
"owner-kept (cauldron_sheet…)". Ingest ran first on --apply and recorded a keep for the row's pick column
(GR_Beetlefleet: pick B, ✕ B's north) or for its DEFAULT variant column on a redo row (AA_InfectedAerofleet:
variants [B], every B picture ✕'d); step 4 then read that fresh keep as protection. Checks:
  * ingest records no keep for a ✕'d picture of the same row (pick, per-graphic pick, variant);
  * dry run and --apply agree: the ✕'s are purged, not CONFLICTS; the ✕'d facing is not installed;
  * a keep the same row of the same file ALREADY wrote (the pre-fix ledger) is released by the purge;
  * a keep from ANOTHER row still protects (CONFLICT, nothing deleted).
Fixture under /home/mandrake/rm/scratch/BENCH (never /tmp).
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

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main():
    F = T.build(T.SCRATCH / f"enact_selfpurge_{os.getpid()}")
    import artledger as L
    import enact as E
    import ingest as I
    try:
        s = {k: L.store_put_bytes(T.noise_png(100 + i)) for i, k in enumerate(
            ("bA_e", "bB_e", "bB_n", "aA_e", "aB_e", "aB_n", "oB_e", "oX"))}
        tex = F["src"] / "RimMandrake/TestMod/Textures/Things/Pawn/Animal/RM_Beet/RM_Beet_east.png"
        tex.parent.mkdir(parents=True, exist_ok=True)
        tex.write_bytes(L.store_get(s["bA_e"]))
        evf = F["led"] / "events" / "TEST.jsonl"
        with open(evf, "a") as fh:
            fh.write(json.dumps({"type": "live", "id": "beetlive", "mod": T.MOD,
                                 "rel": "Things/Pawn/Animal/RM_Beet/RM_Beet_east.png", "sha": s["bA_e"], "prev": None,
                                 "reason": "fixture", "ts": "2026-10-01T00:00:00"}) + "\n")
            # another row's keep of oX: must still protect it
            fh.write(json.dumps({"type": "ruling", "id": "otherrowkeep", "target": {"shas": [s["oX"]], "row": "RM_Else",
                                 "column": "B"}, "verdict": "keep", "by": "owner", "trust": "ruled",
                                 "at": "2026-10-01T00:00:00Z", "via": "x.decisions.json"}) + "\n")
        gb, ga = "Things/Pawn/Animal/RM_Beet/RM_Beet", "Things/Pawn/Animal/RM_Aero/RM_Aero"
        snap = json.loads(Path(json.loads(F["decisions"].read_text())["snapshot"]).read_text())
        snap["rows"] = {
            "RM_Beet": {"columns": {"A": {"east": s["bA_e"]}, "B": {"east": s["bB_e"], "north": s["bB_n"]}},
                        "graphic_of": {"A": gb, "B": gb}, "labels": {"A": "IN GAME — TestMod", "B": "render beet_v1"},
                        "res": gb, "subject_key": "beet"},
            "RM_Aero": {"columns": {"A": {"east": s["aA_e"]}, "B": {"east": s["aB_e"], "north": s["aB_n"]}},
                        "graphic_of": {"A": ga, "B": ga}, "labels": {"A": "IN GAME — Alpha", "B": "render aero_v1"},
                        "res": ga, "subject_key": "aero"},
            "RM_Other": {"columns": {"B": {"east": s["oB_e"]}}, "graphic_of": {"B": "x/o"}, "labels": {"B": "render"},
                         "subject_key": "other"}}
        sp = Path(json.loads(F["decisions"].read_text())["snapshot"])
        sp.write_text(json.dumps(snap))
        at = "2026-10-09T14:20:00.000Z"
        doc = json.loads(F["decisions"].read_text())
        doc["decisions"] = {
            "RM_Beet": {"decision": "B", "at": at, "decidedAt": at, "note": "", "purge": [s["bB_n"]],
                        "purgeTouched": True, "variants": ["B"], "variantsDefault": True},
            "RM_Aero": {"decision": "redo", "at": at, "decidedAt": at, "note": "", "purgeTouched": True,
                        "purge": [s["aB_e"], s["aB_n"]], "variants": ["B"], "variantsDefault": True},
            "RM_Other": {"decision": "B", "at": at, "decidedAt": at, "note": "", "purge": [s["oX"]]}}
        F["decisions"].write_text(json.dumps(doc))

        R0 = E.enact(F["decisions"], apply=False, no_deploy=True)
        planned = sorted(p["sha"] for p in R0["plan"]["purge"])
        check(planned == sorted([s["bB_n"], s["aB_e"], s["aB_n"]]), "dry run plans the 3 same-row ✕ purges")
        check(any(s["oX"][:12] in c and "owner-kept" in c for c in R0["conflicts"]),
              "a ✕ kept by ANOTHER row is still a CONFLICT")
        check(not any(i["sha"] == s["bB_n"] for i in R0["plan"]["install"]), "the ✕'d facing of the pick is not installed")

        R1 = E.enact(F["decisions"], apply=True, no_deploy=True, redo_jobs_out=F["root"] / "jobs.json")
        check(R1["purged"] == 3, f"--apply purges what the dry run planned ({R1['purged']} of 3)")
        check(not any(x in c for c in R1["conflicts"] for x in (s["bB_n"][:12], s["aB_e"][:12], s["aB_n"][:12])),
              "no same-row ✕ is reported as owner-kept")
        check(L.store_has(s["oX"]) and not L.store_has(s["bB_n"]), "other-row keep untouched; same-row ✕ bytes gone")
        idx = L.Index()
        for r in idx.rulings:
            t = r.get("target") or {}
            if t.get("row") in ("RM_Beet", "RM_Aero") and r.get("verdict") == "keep":
                check(not set(t.get("shas") or []) & {s["bB_n"], s["aB_e"], s["aB_n"]},
                      f"ingest's keep {t.get('row')}/{t.get('column')} names no ✕'d picture")
        check(not any((r.get("target") or {}).get("row") == "RM_Aero" and r.get("verdict") == "keep" for r in idx.rulings),
              "a redo row whose default variant column is wholly ✕'d records no keep")

        # the pre-fix ledger: a same-row same-file keep naming the ✕'d bytes already exists -> purge releases it
        s2 = L.store_put_bytes(T.noise_png(200))
        snap["rows"]["RM_Beet"]["columns"]["B"]["south"] = s2
        sp.write_text(json.dumps(snap))
        with open(evf, "a") as fh:
            fh.write(json.dumps({"type": "ruling", "id": "prefixkeep", "target": {"shas": [s2], "row": "RM_Beet",
                                 "column": "B"}, "verdict": "keep", "by": "owner", "trust": "ruled", "at": at,
                                 "via": I.rel_via(F["decisions"])}) + "\n")
        doc["decisions"]["RM_Beet"]["purge"].append(s2)
        F["decisions"].write_text(json.dumps(doc))
        R2 = E.enact(F["decisions"], apply=True, no_deploy=True, redo_jobs_out=F["root"] / "jobs.json")
        check(R2["purged"] == 1 and not L.store_has(s2) and not L.Index().protected(s2),
              "a keep the same row of the same file already wrote is released and the ✕ purged")
        R3 = E.enact(F["decisions"], apply=True, no_deploy=True, redo_jobs_out=F["root"] / "jobs.json")
        check(R3["purged"] == 0 and R3["plan"]["purged_already"] == 4, "second --apply is a no-op (4 already purged)")
    finally:
        shutil.rmtree(F["root"], ignore_errors=True)
    print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAILED'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
