#!/usr/bin/env python3
"""ENACT_OLDSHEET_FIX_FORTY_FIVE_NEAR_MISSES: `art.py enact` on an OLD sheet (the 10-05 Weeping Stones one) after later
work moved on. On a fixture:
  A ✕ OF A PICTURE ALREADY PURGED (his 2026-10-10 reject+purge took the bytes) is planned BAN-ONLY: reported on its
    own "✕ ban" line, never counted under "✕ delete ... deleted for ever", and it names no game file (no deploy).
  B A CATCH'S CREATURE IS SETTLED when a render bound to its redraw job in the ledger is live, even though the job's
    _artsrc PNG is gone (the 2026-10-18 bulk accept installed RM_Huldu's redraw; the catch read "being redrawn").
  C A CATCH ALREADY DRAWN from that creature (a ledger binding names it source_creature, made after his note) is
    reported done: not withdrawn, re-filed or queued again. One not drawn yet is queued.
  D A Graphic_Single def gets ONE picture: its queued job carries no facings (the sheet's donor lane had three), and
    a failed facing job beside a done one is not re-filed (stray RM_IvvolCatch_east).
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


DEFS = """<?xml version="1.0" encoding="utf-8"?>
<Defs>
  <PawnKindDef ParentName="AnimalKindBase">
    <defName>RM_Hul</defName>
    <lifeStages><li><bodyGraphicData><texPath>Things/Pawn/Animal/RM_Hul/RM_Hul</texPath></bodyGraphicData></li></lifeStages>
  </PawnKindDef>
  <PawnKindDef ParentName="AnimalKindBase">
    <defName>RM_Gul</defName>
    <lifeStages><li><bodyGraphicData><texPath>Things/Pawn/Animal/RM_Gul/RM_Gul</texPath></bodyGraphicData></li></lifeStages>
  </PawnKindDef>
  <ThingDef ParentName="ResourceBase">
    <defName>RM_HulCatch</defName>
    <graphicData><texPath>Things/Item/Fish/RM_HulCatch</texPath><graphicClass>Graphic_Single</graphicClass></graphicData>
  </ThingDef>
  <ThingDef ParentName="ResourceBase">
    <defName>RM_GulCatch</defName>
    <graphicData><texPath>Things/Item/Fish/RM_GulCatch</texPath><graphicClass>Graphic_Single</graphicClass></graphicData>
  </ThingDef>
  <ThingDef ParentName="ResourceBase">
    <defName>RM_Sing</defName>
    <graphicData><texPath>Things/Item/RM_Sing</texPath><graphicClass>Graphic_Single</graphicClass></graphicData>
  </ThingDef>
  <ThingDef ParentName="ResourceBase">
    <defName>RM_Xed</defName>
    <graphicData><texPath>Things/Item/RM_Xed</texPath><graphicClass>Graphic_Single</graphicClass></graphicData>
  </ThingDef>
</Defs>
"""

CLICK = "2026-10-10T14:00:00.000Z"
CATCH_NOTE = "Make it look like a dead one of these. Of course generate AFTER the source is settled"


def build(root: Path) -> dict:
    F = T.build(root)
    import artledger as L
    src, led, ap = F["src"], F["led"], F["ap"]
    (src / "RimMandrake/TestMod/Defs/ThingDefs_Items").mkdir(parents=True, exist_ok=True)
    (src / "RimMandrake/TestMod/Defs/ThingDefs_Items/Near.xml").write_text(DEFS)
    keys = ("ha", "hulr", "ga", "gulr", "hce", "hcn", "hcs", "hulc", "gce", "gcn", "gcs", "sa", "xa", "xp")
    s = {k: L.store_put_bytes(T.noise_png(300 + i)) for i, k in enumerate(keys)}
    tex = src / "RimMandrake/TestMod/Textures"
    evs = []

    def live(rel, k, ts):
        p = tex / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(L.store_get(s[k]))
        evs.append({"type": "live", "id": L.det_id("live", rel), "mod": T.MOD, "rel": rel, "sha": s[k], "prev": None,
                    "reason": "fixture", "ts": ts})
    # B: the creatures' redraws went live on 2026-10-18 (bulk accept); each is bound to its job in the ledger
    live("Things/Pawn/Animal/RM_Hul/RM_Hul_east.png", "hulr", "2026-10-18T18:43:54-0700")
    live("Things/Pawn/Animal/RM_Gul/RM_Gul_east.png", "gulr", "2026-10-18T18:43:54-0700")
    for k, job, subj in (("hulr", "enact_hul_v1_east", "RM_Hul"), ("gulr", "enact_gul_v1_east", "RM_Gul")):
        evs.append({"type": "binding", "id": L.det_id("bind", job), "sha": s[k], "job": job, "subject": subj,
                    "confidence": "bound", "ts": "2026-10-10T10:05:13-0700"})
    # C: RM_HulCatch was drawn from the settled RM_Hul by hand (binding names the source creature); RM_GulCatch was not
    live("Things/Item/Fish/RM_HulCatch.png", "hulc", "2026-11-01T12:18:23-0800")
    evs.append({"type": "binding", "id": L.det_id("bind", "hulcatch"), "sha": s["hulc"], "job": "dead_catches",
                "subject": "RM_HulCatch", "source_creature": "RM_Hul", "source_sha": s["hulr"],
                "confidence": "bound", "ts": "2026-11-01T12:18:23-0800"})
    live("Things/Item/RM_Sing.png", "sa", "2026-10-01T00:00:00")
    live("Things/Item/RM_Xed.png", "xa", "2026-10-01T00:00:00")
    # A: xp was ✕'d on the sheet and purged on 2026-10-10 under the old reject+purge rule: bytes gone, no ban
    evs.append({"type": "purge", "id": L.det_id("purge", s["xp"]), "sha": s["xp"], "by": "owner",
                "said": "reject+purge on sheet", "bytes_removed": True, "ts": "2026-10-10T07:58:35-0700",
                "via": "fixture"})
    with open(led / "events" / "TEST.jsonl", "a") as fh:
        for e in evs:
            fh.write(json.dumps(e) + "\n")
    L.store_path(s["xp"]).unlink()
    IG = "IN GAME — TestMod"
    three = lambda a, b, c: {"east": s[a], "north": s[b], "south": s[c]}  # noqa: E731
    rows = {
        "RM_Hul": {"columns": {"A": {"east": s["ha"]}}, "graphic_of": {"A": "Things/Pawn/Animal/RM_Hul/RM_Hul"},
                   "labels": {"A": IG}, "res": "Things/Pawn/Animal/RM_Hul/RM_Hul", "subject_key": "hul"},
        "RM_Gul": {"columns": {"A": {"east": s["ga"]}}, "graphic_of": {"A": "Things/Pawn/Animal/RM_Gul/RM_Gul"},
                   "labels": {"A": IG}, "res": "Things/Pawn/Animal/RM_Gul/RM_Gul", "subject_key": "gul"},
        # the sheet showed a three-facing donor lane for each catch, though the def is Graphic_Single
        "RM_HulCatch": {"columns": {"A": three("hce", "hcn", "hcs")}, "graphic_of": {"A": "Things/Item/Fish/RM_HulCatch"},
                        "labels": {"A": "donor"}, "res": "Things/Item/Fish/RM_HulCatch", "subject_key": "hulcatch"},
        "RM_GulCatch": {"columns": {"A": three("gce", "gcn", "gcs")}, "graphic_of": {"A": "Things/Item/Fish/RM_GulCatch"},
                        "labels": {"A": "donor"}, "res": "Things/Item/Fish/RM_GulCatch", "subject_key": "gulcatch"},
        "RM_Sing": {"columns": {"A": {"single": s["sa"]}}, "graphic_of": {"A": "Things/Item/RM_Sing"},
                    "labels": {"A": IG}, "res": "Things/Item/RM_Sing", "subject_key": "sing"},
        "RM_Xed": {"columns": {"A": {"single": s["xa"]}, "B": {"single": s["xp"]}},
                   "graphic_of": {"A": "Things/Item/RM_Xed", "B": "Things/Item/RM_Xed"},
                   "labels": {"A": IG, "B": "render xed_v1"}, "res": "Things/Item/RM_Xed", "subject_key": "xed"},
    }
    sp = Path(json.loads(F["decisions"].read_text())["snapshot"])
    snap = json.loads(sp.read_text())
    snap["rows"].update(rows)
    sp.write_text(json.dumps(snap))

    def d(dec, note="", **kw):
        return dict({"decision": dec, "at": CLICK, "decidedAt": CLICK, "note": note}, **kw)
    doc = json.loads(F["decisions"].read_text())
    doc["decisions"].update({
        "RM_Hul": d("redo", "An alien otter with a whale tail."),
        "RM_Gul": d("redo", "A sleeker gul."),
        "RM_HulCatch": d("redo", CATCH_NOTE),
        "RM_GulCatch": d("redo", CATCH_NOTE),
        "RM_Sing": d("redo", "Brighter sing."),
        "RM_Xed": d("A", purge=[s["xp"]]),
    })
    F["decisions"].write_text(json.dumps(doc))
    # done redraw jobs whose _artsrc PNG is gone (only the ledger binding says what they drew)
    for jid, tdef, note in (("enact_hul_v1_east", "RM_Hul", "An alien otter with a whale tail."),
                            ("enact_gul_v1_east", "RM_Gul", "A sleeker gul.")):
        (ap / "done" / f"{jid}.json").write_text(json.dumps(
            {"id": jid, "target_def": tdef, "facing": "east", "prompt": "x", "created": "2026-10-10T15:12:01Z",
             "owner_note": note, "canon_reference": []}))
    # D: a Graphic_Single def with one facing done and a sibling facing failed
    for jid, state in (("enact_sing_v1_east", "done"), ("enact_sing_v1_north", "failed")):
        (ap / state).mkdir(parents=True, exist_ok=True)
        (ap / state / f"{jid}.json").write_text(json.dumps(
            {"id": jid, "target_def": "RM_Sing", "facing": jid.rsplit("_", 1)[1], "prompt": "x",
             "created": "2026-10-10T15:12:01Z", "owner_note": "Brighter sing.", "canon_reference": []}))
    F["s"] = s
    return F


def main():
    root = T.SCRATCH / f"enact_oldsheet_{os.getpid()}"
    F = build(root)
    import enact as E
    s = F["s"]
    try:
        if hasattr(E, "reset_caches"):
            E.reset_caches()
        R = E.enact(F["decisions"], apply=False, no_deploy=True)
        check(R.get("ok"), f"enact dry run ran ({R.get('error')})")
        P = R["plan"]
        rep = E.report(R)
        # A
        xs = [x for x in P["x_delete"] if x["sha"] == s["xp"]]
        check(len(xs) == 1 and xs[0].get("ban_only") and not xs[0]["slots"],
              "A a ✕ on a picture already purged is planned ban-only, naming no game file")
        ndel = len([x for x in P["x_delete"] if not x.get("ban_only")])     # selftest_enact's own free ✕s
        check(f"✕ delete   {ndel} picture(s)" in rep and "✕ ban      1 picture(s)" in rep,
              "A the report counts it under '✕ ban', not '✕ delete ... deleted for ever'")
        # B
        blocked = " | ".join(P.get("blocked") or [])
        check("RM_HulCatch" not in blocked and "RM_GulCatch" not in blocked and "being redrawn" not in blocked,
              "B a creature whose bound redraw is live counts as settled (no 'being redrawn' block)")
        ok, ref, why = E.source_settled("RM_Gul", json.loads(F["decisions"].read_text())["decisions"],
                                        json.loads(Path(json.loads(F["decisions"].read_text())["snapshot"]).read_text()),
                                        E.load_jobs(), E.L.Index(), {})
        check(ok and ref == s["gulr"], f"B ...its reference is the live bound render ({why})")
        # C
        done = " | ".join(P.get("done") or [])
        check("RM_HulCatch: catch already carried out" in done and "RM_HulCatch" in P["followed"],
              "C a catch drawn from its settled creature is done and its note followed")
        qrows = {q["row"] for q in P["queue"]}
        check("RM_HulCatch" not in qrows and not any(r["row"] == "RM_HulCatch" for r in P["refile"])
              and not any(w["row"] == "RM_HulCatch" for w in P["withdraw"]),
              "C ...and is not queued, re-filed or withdrawn")
        q = [x for x in P["queue"] if x["row"] == "RM_GulCatch"]
        check(len(q) == 1 and q[0].get("ref_shas") == [s["gulr"]],
              "C a catch not drawn yet is queued with the settled creature's picture as its reference")
        # D
        rows = [r for r in E.job_rows(P) if r["target_def"] == "RM_GulCatch"]
        check(len(rows) == 1 and rows[0]["facings"] == [],
              "D the Graphic_Single catch's job asks for one picture (facings []), not the donor lane's three")
        check(not any(r["job"]["id"] == "enact_sing_v1_north" for r in P["refile"])
              and "enact_sing_v1_north not re-filed" in done,
              "D a failed facing job of a Graphic_Single def beside a done one is not re-filed")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("ok" if not FAILS else f"{len(FAILS)} failed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
