#!/usr/bin/env python3
"""selftest_enact_x_archives.py — a ✕ never PURGES a picture he once kept or that is in the game (ENACT_X_FIX_PURGE_OF_KEPT_ART).

Owner card 2026-10-26 19:06 "Newest mark wins, X archives"; delegation_policy 2.3. Cases (each purged on the old enact):
  * a picture live inside a Graphic_Random folder -> ARCHIVED (file gone, bytes kept, restorable), sibling untouched;
  * a picture kept only by an OLDER keep of the same row (another decisions file) -> ARCHIVED, keep released, bytes kept;
  * a picture that is the ONLY texture a def draws, with no replacement pick -> PENDING: file stays, nothing archived,
    nothing purged, listed in the digest; it archives once a replacement is live.
Fixture under the scratch tree (never /tmp)."""
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
    F = T.build(T.SCRATCH / f"enact_xarch_{os.getpid()}")
    import artledger as L
    import enact as E
    import ingest as I
    L.MARK_ROOT = F["root"]
    try:
        s = {k: L.store_put_bytes(T.noise_png(400 + i)) for i, k in enumerate(("fa", "fb", "kd", "solo", "rep", "rb"))}
        mt = F["src"] / "RimMandrake/TestMod"
        (mt / "Defs/ThingDefs_Races/Xarch.xml").write_text(
            "<Defs><ThingDef><defName>RM_Fol</defName><graphicData><graphicClass>Graphic_Random</graphicClass>"
            "<texPath>Things/Plant/RM_Fol</texPath></graphicData></ThingDef>"
            "<ThingDef><defName>RM_Solo</defName><graphicData><texPath>Things/Plant/RM_Solo/RM_Solo</texPath>"
            "</graphicData></ThingDef></Defs>")
        evf = F["led"] / "events" / "TEST.jsonl"
        rels = {"fa": "Things/Plant/RM_Fol/RM_Fol_a.png", "fb": "Things/Plant/RM_Fol/RM_Fol_b.png",
                "solo": "Things/Plant/RM_Solo/RM_Solo_east.png"}
        with open(evf, "a") as fh:
            for k, rel in rels.items():
                p = mt / "Textures" / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(L.store_get(s[k]))
                fh.write(json.dumps({"type": "live", "id": "live_" + k, "mod": T.MOD, "rel": rel, "sha": s[k],
                                     "prev": None, "reason": "fixture", "ts": "2026-10-01T00:00:00"}) + "\n")
            # kd was kept by RM_Old in an OLDER decisions file (10-01); not in any game file
            fh.write(json.dumps({"type": "ruling", "id": "oldownkeep", "target": {"shas": [s["kd"]], "row": "RM_Old",
                                 "column": "B"}, "verdict": "keep", "by": "owner", "trust": "ruled",
                                 "at": "2026-10-01T00:00:00Z", "via": "older_sheet.decisions.json"}) + "\n")
        gf, go, gs = "Things/Plant/RM_Fol", "Things/Plant/RM_Old/RM_Old", "Things/Plant/RM_Solo/RM_Solo"
        spth = Path(json.loads(F["decisions"].read_text())["snapshot"])
        snap = json.loads(spth.read_text())
        snap["rows"] = {
            "RM_Fol": {"columns": {"A": {"east": s["fa"]}, "B": {"east": s["fb"]}}, "graphic_of": {"A": gf, "B": gf},
                       "labels": {"A": "IN GAME — TestMod", "B": "IN GAME — TestMod"}, "res": gf, "subject_key": "fol"},
            "RM_Old": {"columns": {"B": {"east": s["kd"]}}, "graphic_of": {"B": go}, "labels": {"B": "render old"},
                       "res": go, "subject_key": "old"},
            "RM_Solo": {"columns": {"A": {"east": s["solo"]}}, "graphic_of": {"A": gs},
                        "labels": {"A": "IN GAME — TestMod"}, "res": gs, "subject_key": "solo"}}
        spth.write_text(json.dumps(snap))
        at = "2026-10-09T14:20:00.000Z"
        doc = json.loads(F["decisions"].read_text())
        doc["decisions"] = {
            "RM_Fol": {"decision": "A", "at": at, "decidedAt": at, "note": "", "purge": [s["fb"]], "purgeTouched": True},
            "RM_Old": {"decision": "redo", "at": at, "decidedAt": at, "note": "", "purge": [s["kd"]], "purgeTouched": True},
            "RM_Solo": {"decision": "redo", "at": at, "decidedAt": at, "note": "", "purge": [s["solo"]], "purgeTouched": True}}
        F["decisions"].write_text(json.dumps(doc))

        R0 = E.enact(F["decisions"], apply=False, no_deploy=True)
        P = R0["plan"]
        planned_arch = {a["sha"] for a in P["archive"]}
        check(not P["purge"], f"the dry run plans NO purge at all (planned {[p['sha'][:8] for p in P['purge']]})")
        check(s["fb"] in planned_arch, "(a) the picture live in a Graphic_Random folder is planned for the archive")
        check(s["kd"] in planned_arch, "(b) the picture kept only by an older keep of the same row is planned for the archive")
        check(s["solo"] not in planned_arch and any(s["solo"][:12] in x for x in P["x_pending"]),
              "(c) the sole texture of a def with no replacement is PENDING, not archived")
        check(not any(r["sha"] == s["fb"] for r in P["retire"]), "the folder picture is not retired-and-purged")

        R1 = E.enact(F["decisions"], apply=True, no_deploy=True, redo_jobs_out=F["root"] / "jobs.json")
        idx = L.Index()
        check(R1["purged"] == 0 and not any(idx.is_purged(s[k]) for k in s), "--apply purges nothing")
        check(not (mt / "Textures" / rels["fb"]).exists() and L.store_has(s["fb"]) and s["fb"] in L.archived_shas(idx),
              "(a) the folder picture left the game, bytes kept, in the archive (restorable)")
        check((mt / "Textures" / rels["fa"]).exists(), "(a) the folder's other picture stays")
        check(L.store_has(s["kd"]) and not idx.protected(s["kd"]) and not idx.is_purged(s["kd"]),
              "(b) the older-kept picture: bytes kept, his old keep released, not purged")
        check((mt / "Textures" / rels["solo"]).is_file() and L.store_has(s["solo"]) and not idx.is_purged(s["solo"]),
              "(c) the sole texture stays in the game (no hole), is not purged")
        check(s["solo"] not in L.archived_shas(idx), "(c) nothing was archived for it yet")
        out = E.report(R1)
        check("X PENDING" in out and s["solo"][:12] in out, "(c) the digest lists the pending ✕")
        # the owner now ALSO picks a replacement (column B) in the same slot: the ✕ no longer leaves a hole -> archived
        snap["rows"]["RM_Solo"]["columns"]["B"] = {"east": s["rep"]}
        snap["rows"]["RM_Solo"]["graphic_of"]["B"] = gs
        snap["rows"]["RM_Solo"]["labels"]["B"] = "render solo_v2"
        spth.write_text(json.dumps(snap))
        doc["decisions"]["RM_Solo"]["decision"] = "B"
        F["decisions"].write_text(json.dumps(doc))
        R2 = E.enact(F["decisions"], apply=True, no_deploy=True, redo_jobs_out=F["root"] / "jobs.json")
        idx = L.Index()
        check(R2["purged"] == 0 and not idx.is_purged(s["solo"]) and L.store_has(s["solo"]),
              "with a replacement pick the old sole texture is still never purged (bytes kept)")
        check(not any(s["solo"][:12] in c for c in R2["conflicts"]) and
              (mt / "Textures" / rels["solo"]).read_bytes() == L.store_get(s["rep"]),
              "the replacement landed in the slot and the ✕ raised no pending/conflict")
    finally:
        shutil.rmtree(F["root"], ignore_errors=True)
    print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAILED'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
