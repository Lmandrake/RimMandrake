#!/usr/bin/env python3
"""selftest_enact_v2.py — `art.py enact` on SCHEMA-2 decisions (DESIGN 2026-10-10 §3.5/§3.6, decisions_v2.py):

  A an unknown schema (3) is refused by enact and by ingest — never read as schema 1;
  B a legacy schema-1 variant tick ships NOTHING until he says keep in its sheet row (and is not retired from
    the folder meanwhile); once confirmed it ships into the folder; once dropped it neither ships nor protects;
  C pool.remove takes a picture out of a folder pool (retired, archived) — and is refused when the pool moved since he
    edited it (baseline), or when it would empty the pool;
  D a slot set to `redraw` (a young graphic) files ONE job for that slot: its texPath named, its own facings, `slot` on
    the job; the row's open note is not marked followed by it;
  E asks.more on a catch row waits for its creature; asks.more elsewhere files N jobs referencing the base letter;
  F a def-side ask (rename) is a TODO until --mark-done <row> --ask rename;
  G migration: a schema-1 record migrates with its letters resolved to set ids, `variants` moved to legacyVariants and a
    variantsDefault list to legacyVariantsDefault (never his); decision_letters still sees every letter.
Fixture under /home/mandrake/rm/scratch/BENCH (never /tmp).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import selftest_enact as T  # noqa: E402
import selftest_enact_ws as W  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main():
    F = W.build(T.SCRATCH / f"enact_v2_{os.getpid()}")
    import artledger as L
    import decisions_v2 as DV
    import enact as E
    import ingest as I
    src, s = F["src"], F["s"]
    tex = src / "RimMandrake/TestMod/Textures"
    # a second live picture in the Quill folder (a pool of two)
    extra = {k: L.store_put_bytes(T.noise_png(300 + i)) for i, k in enumerate(("qc", "ky", "kz"))}
    rel = "Things/Plant/RM_Quill/RM_Quill_c.png"
    (tex / rel).write_bytes(L.store_get(extra["qc"]))
    with open(F["led"] / "events" / "TEST.jsonl", "a") as fh:
        fh.write(json.dumps({"type": "live", "id": L.det_id("live", rel), "mod": T.MOD, "rel": rel, "sha": extra["qc"],
                             "prev": None, "reason": "fixture", "ts": "2026-10-01T00:00:00"}) + "\n")
    doc = json.loads(F["decisions"].read_text())
    sp = Path(doc["snapshot"])
    snap = json.loads(sp.read_text())
    Q = "Things/Plant/RM_Quill"
    snap["rows"]["RM_Quill"] = {"columns": {"A": {"single": s["pa"]}, "B": {"single": s["pb"]}, "C": {"single": extra["qc"]}},
                                "graphic_of": {"A": Q, "B": Q, "C": Q}, "pools": [Q], "res": Q, "subject_key": "quill",
                                "labels": {"A": "IN GAME — random variant a (1 of 2)", "B": "render quill_v1",
                                           "C": "IN GAME — random variant c (2 of 2)"}}
    KY = "swanimals/Kite/Kite_young"
    kr = snap["rows"]["RSW_Kite"]
    kr["columns"].update({"Y": {"east": extra["ky"], "south": extra["kz"]}})
    kr["graphic_of"]["Y"] = KY
    kr["labels"]["Y"] = "IN GAME — young"
    sp.write_text(json.dumps(snap))
    at = "2026-10-10T10:00:00.000Z"
    base = [DV.SL.set_id({"single": s["pa"]}), DV.SL.set_id({"single": extra["qc"]})]

    def d(dec, **kw):
        return dict({"schema": 2, "decision": dec, "at": at, "decidedAt": at, "note": ""}, **kw)
    D = doc["decisions"]
    D["RM_Dew"] = d("A", legacyVariants=["B"])                                   # B: an old tick, unruled
    D["RM_Quill"] = d("A", pool={Q: {"remove": ["C"], "baseline": sorted(base)}})
    D["RSW_Kite"] = d("A", note="keep the wings", slots={KY: {"state": "redraw"}})
    D["RM_HulCatch"] = d("redo", note=D["RM_HulCatch"]["note"], asks={"more": [{"slot": "Things/Item/RM_HulCatch", "n": 1}]})
    D["RSW_Fan"] = d("B", asks={"more": [{"slot": "swanimals/Fan/Fan", "n": 2, "base": "C", "how": "more realistic"}]})
    D["RM_Lum"] = d("A", asks={"rename": {"name": "Gloamling", "suggest": False}})
    for k in ("RM_Bur", "RM_Kir", "RM_Amb", "RM_Vel", "RM_Viz", "RSW_Strill"):
        D.pop(k, None)
    F["decisions"].write_text(json.dumps(doc))
    conf_path = F["root"] / "old_ticks_confirm.decisions.json"
    os.environ["ART_OLD_TICKS_CONFIRM"] = str(conf_path)
    os.environ["ART_BIOME_SHEETS_DIR"] = str(F["root"] / "biomes")      # never the live biome sheets
    try:
        E.reset_caches()
        # A unknown schema refused
        bad = json.loads(F["decisions"].read_text())
        bad["decisions"]["RM_Lum"]["schema"] = 3
        bp = F["root"] / "bad.decisions.json"
        bp.write_text(json.dumps(bad))
        rb = E.enact(bp, apply=False, no_deploy=True)
        check(not rb["ok"] and "schema" in str(rb.get("error")), "A enact refuses a schema-3 record")
        ib = I.ingest(bp, dry_run=True, defer_redo_jobs=True, purge=False)
        check(not ib["ok"] and "schema" in str(ib.get("error")), "A ingest refuses a schema-3 record")

        R = E.enact(F["decisions"], apply=False, no_deploy=True)
        check(R["ok"], f"dry run ok ({R.get('error')})")
        P = R["plan"]
        inst = {(i["row"], i["rel"]) for i in P["install"]}
        # B legacy tick
        check(not any(i["row"] == "RM_Dew" and i.get("variant") for i in P["install"]),
              "B an unconfirmed legacy tick ships nothing")
        check(any(x.startswith("RM_Dew: old variant tick B") for x in P["legacy_unconfirmed"]),
              "B ...and is listed as waiting on keep/drop in its row")
        # C pool remove
        check(any(rt["row"] == "RM_Quill" and rt["rel"].endswith("RM_Quill_c.png") for rt in P["retire"]),
              "C pool.remove C plans C out of the Quill folder")
        # D slot redraw
        kq = [q for q in P["queue"] if q["row"] == "RSW_Kite"]
        check(len(kq) == 1 and kq[0].get("slot") == KY, "D a young slot set to redraw queues ONE job for that slot")
        jr = [j for j in E.job_rows(P) if j["target_def"] == "RSW_Kite"]
        check(len(jr) == 1 and jr[0].get("slot") == KY and "Kite_young" in jr[0]["prompt"]
              and jr[0]["facings"] == ["east", "south"], "D ...the job names the slot's texPath and carries its own facings")
        # E asks.more
        check(not any(q["row"] == "RM_HulCatch" and q.get("ask_id") for q in P["queue"])
              and any(b.startswith("RM_HulCatch: more not filed") for b in P["blocked"]),
              "E asks.more on a catch row waits for its creature")
        fq = [j for j in E.job_rows(P) if j["target_def"] == "RSW_Fan" and j.get("ask") == "more"]
        check(len(fq) == 2 and all(str(L.store_path(s["fc"])) in j["canon_reference"] for j in fq),
              "E asks.more n=2 based on C files two jobs referencing C")
        # F def ask
        check(any(x.startswith("RM_Lum: ask rename") for x in P["asks"]), "F a rename ask is listed until marked done")
        R2 = E.enact(F["decisions"], apply=False, no_deploy=True, mark_done=["RM_Lum"], ask="rename")
        R3 = E.enact(F["decisions"], apply=False, no_deploy=True)
        check(not any(x.startswith("RM_Lum: ask rename") for x in R3["plan"]["asks"]), "F --mark-done --ask rename closes it")

        # apply: legacy B stays out of the folder, pool remove happens
        R = E.enact(F["decisions"], apply=True, no_deploy=True, redo_jobs_out=F["root"] / "jobs.json")
        check(R["ok"], "apply ok")
        dew = sorted(p.name for p in (tex / "Things/Plant/RM_Dew").iterdir())
        check(dew == ["RM_Dew_a.png"], f"B nothing shipped from the unconfirmed tick ({dew})")
        quill = sorted(p.name for p in (tex / Q).iterdir())
        check(quill == ["RM_Quill_a.png"] and L.store_has(extra["qc"]), f"C C left the pool, archived ({quill})")
        jobs = W.jobs_written(F)
        kj = jobs.get("RSW_Kite", [])
        check(len({j["id"].rsplit("_", 1)[0] for j in kj}) == 1 and sorted(j["facing"] for j in kj) == ["east", "south"]
              and all(j.get("slot") == KY for j in kj), "D one Kite slot job (per facing) in pending/, `slot` carried")
        dk = json.loads(F["decisions"].read_text())["decisions"]["RSW_Kite"]
        check(dk.get("note") == "keep the wings", "D the slot job did not mark the row's note followed")
        # B confirmed -> ships
        conf_path.write_text(json.dumps({"decisions": {
            DV.confirm_key("test_sheet", "RM_Dew", "B"): {"decision": "confirm", "decidedAt": at, "at": at}}}))
        E.reset_caches()
        R = E.enact(F["decisions"], apply=False, no_deploy=True)
        check(("RM_Dew", "Things/Plant/RM_Dew/RM_Dew_b.png") in {(i["row"], i["rel"]) for i in R["plan"]["install"]},
              "B a CONFIRMED legacy tick ships into the folder")
        # B' an answer clicked IN the biome sheet row (legacyRuled) — the standalone old-ticks sheet is retired
        conf_path.write_text(json.dumps({"decisions": {}}))
        bdir = F["root"] / "biomes"
        bdir.mkdir(exist_ok=True)
        os.environ["ART_BIOME_SHEETS_DIR"] = str(bdir)
        dr = json.loads(F["decisions"].read_text())
        dr["decisions"]["RM_Dew"]["legacyRuled"] = {"B": {"v": "confirm", "at": at}}
        pr = F["root"] / "rowkeep.decisions.json"
        pr.write_text(json.dumps(dr))
        E.reset_caches()
        R = E.enact(pr, apply=False, no_deploy=True)
        check(("RM_Dew", "Things/Plant/RM_Dew/RM_Dew_b.png") in {(i["row"], i["rel"]) for i in R["plan"]["install"]}
              and not any(x.startswith("RM_Dew:") for x in R["plan"]["legacy_unconfirmed"]),
              "B' keep clicked in the biome sheet row ships the legacy tick")
        conf_path.write_text(json.dumps({"decisions": {
            DV.confirm_key("test_sheet", "RM_Dew", "B"): {"decision": "confirm", "decidedAt": at, "at": at}}}))
        dr["decisions"]["RM_Dew"]["legacyRuled"] = {"B": {"v": "drop", "at": at}}
        pr.write_text(json.dumps(dr))
        E.reset_caches()
        R = E.enact(pr, apply=False, no_deploy=True)
        check(not any(i["row"] == "RM_Dew" and i["rel"].endswith("_b.png") for i in R["plan"]["install"])
              and not any(x.startswith("RM_Dew:") for x in R["plan"]["legacy_unconfirmed"]),
              "B' drop in the row wins over an old-sheet confirm: ships nothing, no longer waiting")
        # confirmations() reads the biome decisions files; the fold copies old-sheet answers into rows, never over his
        (bdir / "bx_sheet.decisions.json").write_text(json.dumps({"sheetId": "bx_sheet", "decisions": {
            "RM_A": {"legacyVariants": ["B", "C"], "legacyRuled": {"B": {"v": "drop", "at": at}}},
            "RM_Z": {"legacyVariants": ["C"]}}}))
        cf = DV.confirmations()
        check(cf.get(("bx_sheet", "RM_A")) == {"confirm": set(), "drop": {"B"}}
              and cf.get(("test_sheet", "RM_Dew")) == {"confirm": {"B"}, "drop": set()},
              "confirmations() reads in-row answers from the biome decisions files AND the old sheet's answers")
        conf_path.write_text(json.dumps({"decisions": {
            DV.confirm_key("bx_sheet", "RM_A", "B"): {"decision": "confirm", "decidedAt": at},
            DV.confirm_key("bx_sheet", "RM_A", "C"): {"decision": "confirm", "decidedAt": at},
            DV.confirm_key("bx_sheet", "RM_Z", "C"): {"decision": "drop"}}}))          # a prefill: not his, not folded
        before = (bdir / "bx_sheet.decisions.json").read_text()
        dry = DV.fold_old_sheet_answers(apply=False)
        check(dry["folded"] == 1 and before == (bdir / "bx_sheet.decisions.json").read_text(), f"fold dry run counts and writes nothing")
        fo = DV.fold_old_sheet_answers(apply=True)
        fd = json.loads((bdir / "bx_sheet.decisions.json").read_text())["decisions"]
        check(fo["folded"] == 1 and fo["already"] == 1 and fd["RM_A"]["legacyRuled"]["B"]["v"] == "drop"
              and fd["RM_A"]["legacyRuled"]["C"]["v"] == "confirm" and "legacyRuled" not in fd["RM_Z"],
              "fold: an old-sheet answer lands in its row; his in-row answer is never overwritten; a prefill is not folded")
        conf_path.write_text(json.dumps({"decisions": {
            DV.confirm_key("test_sheet", "RM_Dew", "B"): {"decision": "confirm", "decidedAt": at, "at": at}}}))
        E.reset_caches()
        # C baseline drift refused
        d2 = json.loads(F["decisions"].read_text())
        d2["decisions"]["RM_Quill"]["pool"][Q]["baseline"] = ["0000000000000000"]
        p2 = F["root"] / "drift.decisions.json"
        p2.write_text(json.dumps(d2))
        R = E.enact(p2, apply=False, no_deploy=True)
        check(any("changed since you edited it" in c for c in R["conflicts"]) and
              not any(rt["row"] == "RM_Quill" for rt in R["plan"]["retire"]), "C a pool that moved since his edit is refused")

        # G migration
        v1 = {"decision": "B", "at": at, "decidedAt": at, "note": "x", "variants": ["C"], "picks": {"g2": "D"}}
        row = {"columns": {"B": {"east": "b1"}, "C": {"east": "c1"}, "D": {"east": "d1"}},
               "graphic_of": {"B": "g1", "C": "g1", "D": "g2"}, "res": "g1"}
        nv, rep = DV.migrate_record(v1, row, "s1")
        check(nv["schema"] == 2 and nv["legacyVariants"] == ["C"] and "variants" not in nv
              and nv["setIds"]["B"] == DV.SL.set_id({"east": "b1"}) and nv["slots"]["g1"]["pick"] == "B"
              and nv["slots"]["g2"]["pick"] == "D", "G schema-1 record migrates: set ids, slots, legacy ticks")
        nd, _ = DV.migrate_record({"decision": "B", "at": at, "variants": ["B", "C"], "variantsDefault": True}, row, "s1")
        check(nd.get("legacyVariantsDefault") == ["B", "C"] and not nd.get("legacyVariants")
              and DV.owner_pool_adds(nd) == [], "G a machine-default list migrates as the machine's, never his")
        check(L.decision_letters(nv) == {"B", "C", "D"}, "G decision_letters still sees every letter of a migrated record")
    finally:
        os.environ.pop("ART_OLD_TICKS_CONFIRM", None)
        os.environ.pop("ART_BIOME_SHEETS_DIR", None)
    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
