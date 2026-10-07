#!/usr/bin/env python3
"""selftest_art.py — the art ledger's guarantees, on a disposable fixture (never real Textures).

Proves: snapshot archives every byte; install refuses without an owner ruling, archives
the displaced picture BEFORE writing, and records `live`; purge deletes bytes, is
refused on a live or kept picture, and is honoured by registration; ingest turns only
touched sheet rows into owner rulings and refuses an untouched prefill file.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from io import BytesIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def png(color):
    from PIL import Image
    b = BytesIO()
    Image.new("RGBA", (8, 8), color).save(b, "PNG")
    return b.getvalue()


def main():
    tmp = Path(tempfile.mkdtemp(prefix="artledger-selftest-"))
    os.environ["ARTSTORE"] = str(tmp / "store")
    os.environ["ART_LEDGER_DIR"] = str(tmp / "ledger")
    os.environ["ART_SRC_ROOT"] = str(tmp / "src")
    sys.path.insert(0, str(HERE))
    import artledger as L
    import art

    # seat resolution (ART_LEDGER_SEAT_DEFAULT_1): never a silent BENCH, honours AGENT_SEAT
    saved = {k: os.environ.pop(k, None) for k in
             ("RIMFLOW_SEAT", "ART_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")}
    try:
        try:
            L.seat()
            check(False, "seat() refuses when nothing names a seat")
        except L.NoSeat:
            check(True, "seat() refuses when nothing names a seat")
        try:
            L.Writer(known_ids=set()).add({"type": "probe"})
            check(False, "a ledger write with no seat refuses")
        except L.NoSeat:
            check(True, "a ledger write with no seat refuses")
        os.environ["AGENT_SEAT"] = "foundry"
        check(L.seat() == "FOUNDRY" and L.shard_path().name == "FOUNDRY.jsonl",
              "AGENT_SEAT (the window profile) picks the shard")
        os.environ["RIMFLOW_SEAT"] = "BENCH"
        check(L.seat() == "BENCH", "RIMFLOW_SEAT outranks AGENT_SEAT, as in rimflow")
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v
    os.environ["ART_SEAT"] = "BUILD"          # the fixture writes below need a seat

    mod = "src/FixtureMod"
    tex = tmp / mod / "Textures" / "Things" / "Beast"
    tex.mkdir(parents=True)
    red, blue, green = png((255, 0, 0, 255)), png((0, 0, 255, 255)), png((0, 255, 0, 255))
    (tex / "Beast_south.png").write_bytes(red)
    (tex / "Beast_southm.png").write_bytes(green)
    rel = "Things/Beast/Beast_south.png"
    sred, sblue, sgreen = (L.sha256_bytes(x) for x in (red, blue, green))

    # parse / role
    pt = L.parse_texfile("swanimals/Nuna/Nuna_f_eastm.png")
    check(pt == {"res": "swanimals/Nuna/Nuna_f", "facing": "east", "mask": True}, "parse_texfile reads mask + facing")
    check(L.subject_key("A_Nuna") == "nuna" and L.subject_key("nuna_f") == "nuna", "subject_key normalises sheet keys")
    check(L.normalise_verdict("replace") == "replace-donor", "'replace' is NOT read as reject")

    # phase 0 snapshot
    rc = art.main(["snapshot", "--date", "T"])
    man = (tmp / "ledger" / "snapshots" / "T_textures.tsv").read_text().splitlines()
    check(rc == 0 and len(man) == 3 and L.store_has(sred) and L.store_has(sgreen), "snapshot stores every byte + manifest")

    # backfill disk -> live events
    import backfill
    r = backfill.step_disk(budget=60)
    idx = L.Index()
    check(idx.live.get((mod, rel), {}).get("sha") == sred, f"disk backfill records live ({r})")
    r2 = backfill.step_disk(budget=60)
    check(r2.get("new_events") == 0, "disk backfill is idempotent (deterministic ids)")

    # install refuses without a ruling, and for a bytes-not-in-store sha
    L.store_put_bytes(blue)
    try:
        L.install(mod, rel, sblue)
        check(False, "install without ruling refused")
    except L.Refused:
        check(True, "install without ruling refused")
    agent = L.append({"type": "ruling", "target": {"sha": sblue}, "verdict": "keep", "by": "agent", "trust": "prefill"})
    try:
        L.install(mod, rel, sblue, ruling_id=agent["id"])
        check(False, "install on an agent/prefill ruling refused")
    except L.Refused:
        check(True, "install on an agent/prefill ruling refused")
    # owner keep on the current (red) picture, then install blue on owner's words
    L.append({"type": "ruling", "target": {"sha": sred}, "verdict": "keep", "by": "owner", "trust": "ruled",
              "said": "red is right"})
    check(bool(L.Index().protected(sred)), "owner keep with provenance protects")
    os.unlink(L.store_path(sred))           # prove install re-archives the displaced bytes itself
    res = L.install(mod, rel, sblue, owner_said="blue is better")
    check(res["status"] == "installed" and (tex / "Beast_south.png").read_bytes() == blue, "install wrote the new picture")
    check(L.store_has(sred), "install archived the displaced picture before writing")
    check(L.Index().live[(mod, rel)]["sha"] == sblue, "install recorded live")

    # purge
    try:
        L.purge(sblue, owner_said="bad")
        check(False, "purge of a live picture refused")
    except L.Refused:
        check(True, "purge of a live picture refused")
    try:
        L.purge(sred, owner_said="never mind")
        check(False, "purge of a kept picture refused without release_keep")
    except L.Refused:
        check(True, "purge of a kept picture refused without release_keep")
    pr = L.purge(sred, owner_said="delete that red one", release_keep=True)
    check(pr["bytes_removed"] and not L.store_has(sred) and L.Index().is_purged(sred), "purge removes bytes + records")
    check(not L.Index().protected(sred), "purge with release_keep releases the keep")
    try:
        L.install(mod, rel, sred, owner_said="x")
        check(False, "a purged picture cannot be installed")
    except L.Refused:
        check(True, "a purged picture cannot be installed")

    # ingest: untouched prefill refused; touched rows -> owner rulings + purges
    import ingest
    snap = {"sheetId": "t", "rows": {"Beast": {"columns": {"A": {"south": sblue}, "B": {"south": sgreen}}}}}
    sp = tmp / "t.snapshot.json"
    sp.write_text(json.dumps(snap))
    dec = tmp / "t.decisions.json"
    dec.write_text(json.dumps({"snapshot": str(sp), "reviewStatus": {"state": "prefill"},
                               "decisions": {"Beast": {"decision": "A", "prefill": "A"}}}))
    check(not ingest.ingest(dec)["ok"], "ingest refuses a file the sidecar never wrote")
    dec.write_text(json.dumps({"snapshot": str(sp), "savedBy": "serve_sheet.py", "writeCount": 2,
                               "decisions": {"Beast": {"decision": "B", "prefill": "A", "note": "green",
                                                       "at": "2026-10-04T00:00:00Z", "purge": [sblue]}}}))
    r = ingest.ingest(dec)
    rs = [x for x in L.Index().rulings if x.get("via", "").endswith("t.decisions.json")]
    check(r["ok"] and r["rulings"] == 1 and rs and rs[0]["target"]["shas"] == [sgreen] and rs[0]["trust"] == "ruled",
          f"ingest records the touched row as an owner keep of column B ({r})")
    check(r.get("purge_refused", 0) == 1, "ingest does not purge a live picture even if the sheet asks")
    r_again = ingest.ingest(dec)
    check(r_again["rulings"] == 0, "ingest is idempotent")

    # purge-only touch never turns a prefill into a ruling
    dec.write_text(json.dumps({"snapshot": str(sp), "savedBy": "serve_sheet.py", "writeCount": 3,
                               "decisions": {"Beast": {"decision": "B", "prefill": "B", "at": "2026-10-04T01:00:00Z",
                                                       "purgeTouched": True, "purge": []}}}))
    check(ingest.ingest(dec)["rulings"] == 0, "a row touched only to purge records no keep ruling")

    # the compare-sheet generator on a doubled texPath
    import art_sheet
    art_sheet.SG.SKIP_BROWSER = True
    if (art_sheet.SKILL / "sheet_template.html").exists():
        mod2 = tmp / "src" / "FixtureOverride" / "Textures" / "Things" / "Beast"
        mod2.mkdir(parents=True)
        (mod2 / "Beast_south.png").write_bytes(green)
        backfill.step_disk(budget=60)
        idx = L.Index()
        check(art_sheet.doubles(idx) == ["Things/Beast/Beast"], "doubles() finds the texPath two mods ship differently")
        out = tmp / "sheet" / "t_sheet.html"
        out.parent.mkdir()
        r = art_sheet.generate(art_sheet.doubles(idx), out, "t", "t_sheet", "<p>t</p>")
        d = json.loads((tmp / "sheet" / "t_sheet.decisions.json").read_text())
        snapd = json.loads(Path(r["snapshot"]).read_text())
        check(r["rows"] == 1 and d["reviewStatus"]["state"] == "prefill" and d["decisions"]["Things/Beast/Beast"]["decision"],
              "sheet + prefilled decisions written, reviewStatus=prefill")
        check(set(snapd["rows"]["Things/Beast/Beast"]["columns"]) >= {"A", "B"}, "snapshot names every column's pictures")
        html = out.read_text()
        check('<script id="RENDER">' in html and html.index('<script id="RENDER">') < html.index("FILL IN #3"),
              "row renderer is live, not inside the template's comment")
        chk = subprocess.run([sys.executable, str(art_sheet.SKILL / "check_sheet.py"), str(out), "--decisions",
                              str(tmp / "sheet" / "t_sheet.decisions.json")], capture_output=True, text=True)
        check(chk.returncode == 0, "generated sheet passes check_sheet.py")
        r2 = art_sheet.generate(art_sheet.doubles(idx), out, "t", "t_sheet", "<p>t</p>")
        check(not r2["wrote_decisions"], "regenerating the sheet never overwrites the decisions file")

        # the per-biome sheet (BIOME_FLORAFAUNA_ART_REVIEW_1): canon row + linked stand-in, sit1 prefill, NO ART row
        canon_key = next((d.name for d in sorted(art_sheet.CANON.iterdir()) if d.is_dir()
                          and any(p.suffix in (".png", ".jpg", ".webp") for p in d.iterdir())), None)
        row_a = {"key": "RSW_Beast", "kind": "fauna", "label": "beast", "defNames": ["RSW_Beast"], "port": "RSW_Beast",
                 "placements": [{"layer": "patch", "patch_mod": "mandrake.rut.patches"}], "commonality_max": 0.5,
                 "canon": {"entry": f"design/RimStarWars/canon_references/{canon_key}" if canon_key else None},
                 "twins": [{"defName": "RM_Beast", "relation": "tier_twin_same_stem", "in_this_biome": True}],
                 "art": {"resources": [{"res": "Things/Beast/Beast", "role": "body", "prior_selection": {
                     "decision": "B", "note": "", "picked_label": "x", "picked_faces": {"south": sgreen}}}]},
                 "artpipe_state_jobs": []}
        row_b = {"key": "RM_Beast", "kind": "fauna", "label": "beast", "defNames": ["RM_Beast"], "placements": [],
                 "canon": {"entry": None}, "twins": [], "art": {"resources": []}, "artpipe_state_jobs": []}
        cen = tmp / "census.json"
        cen.write_text(json.dumps({"biome_order": ["RM_Test"], "git_head": "x",
                                   "biomes": {"RM_Test": {"label": "Test", "rows": [row_a, row_b]}}}))
        bout = tmp / "sheet" / "test_sheet.html"
        rb = art_sheet.generate_biome("RM_Test", cen, bout, "T", allow_failing="selftest fixture")
        bh = bout.read_text()
        bitems = json.loads(re.search(r'<script id="ITEMS" type="application/json">(.*?)</script>', bh, re.S).group(1))
        byid = {i["id"]: i for i in bitems}
        check(rb["rows"] == 2 == rb["census_rows"], f"biome sheet: one item per census row ({rb['rows']})")
        check([r["id"] for r in byid["RSW_Beast"]["related"]] == ["RM_Beast"]
              and [r["id"] for r in byid["RM_Beast"]["related"]] == ["RSW_Beast"]
              and byid["RSW_Beast"]["group"] == byid["RM_Beast"]["group"] and byid["RM_Beast"].get("band"),
              "biome sheet: twins linked both ways, same group + colour band")
        check(byid["RM_Beast"]["noArt"] and rb["no_art"] == ["RM_Beast"], "biome sheet: a row with no pictures is NO ART YET")
        bdec = json.loads((tmp / "sheet" / "test_sheet.decisions.json").read_text())
        green_letter = next(c["letter"] for g in byid["RSW_Beast"]["graphics"] for c in g["cols"] if c["faces"].get("south") == sgreen)
        check(byid["RSW_Beast"]["prefillSource"] == "sit1" and bdec["decisions"]["RSW_Beast"]["decision"] == green_letter,
              "biome sheet: desert sitting 1 pick prefills the matching column")
        if canon_key:
            check(bool(byid["RSW_Beast"]["canon"] and byid["RSW_Beast"]["canon"]["imgs"]), "biome sheet: canon row carries reference images")
        chk = subprocess.run([sys.executable, str(art_sheet.SKILL / "check_sheet.py"), str(bout), "--decisions",
                              str(tmp / "sheet" / "test_sheet.decisions.json")], capture_output=True, text=True)
        check(chk.returncode == 0, "biome sheet passes check_sheet.py")
        rb2 = art_sheet.generate_biome("RM_Test", cen, bout, "T", allow_failing="selftest fixture")
        check(rb2["wrote_decisions"] and rb2["snapshotId"] == rb["snapshotId"], "biome rebuild: untouched prefill regenerated, letters stable")
        bdec["savedBy"], bdec["writeCount"] = "serve_sheet.py", 1
        (tmp / "sheet" / "test_sheet.decisions.json").write_text(json.dumps(bdec))
        check(not art_sheet.generate_biome("RM_Test", cen, bout, "T", allow_failing="selftest fixture")["wrote_decisions"],
              "biome rebuild never overwrites a decisions file the sidecar wrote")
        # ART_SHEET_DONOR_JOIN_GAPS_1: a donor-prefixed texPath (RG_Brambles) must still join its finished render
        # `brambles_v1`, and a render that failed the canon gate shows as a candidate badged as such
        import backfill as _bf
        yellow = png((255, 255, 0, 255))
        syellow = L.sha256_bytes(yellow)
        L.store_put_bytes(yellow)
        wr = L.Writer()
        _bf._variant(wr, sha=sgreen, b=green, kind="donor", loc="donor:brambles", rel="Things/Plant/RG_Brambles_south.png",
                     extra={"donor_pkg": "rg.mod", "donor_mod": "RG Mod", "how": "loose"})
        _bf._variant(wr, sha=sblue, b=blue, kind="artpipe", loc="_artsrc/brambles_v1/x.png",
                     extra={"job": "brambles_v1", "facing": "south", "date": "2026-10-05"})
        _bf._variant(wr, sha=syellow, b=yellow, kind="artpipe", loc="_artsrc/foxwing_v1/x.png",
                     extra={"job": "foxwing_v1", "facing": "south", "date": "2026-10-05"})
        frames = {}
        for n in (1, 2, 3):
            for fac in ("east", "south"):
                b_ = png((10 * n, 40 if fac == "east" else 90, 200, 255))
                frames[(n, fac)] = L.sha256_bytes(b_)
                L.store_put_bytes(b_)
                _bf._variant(wr, sha=frames[(n, fac)], b=b_, kind="artpipe", loc=f"_artsrc/x/{n}{fac}.png",
                             extra={"job": f"pyre_foxwing_flight8_{n}_{fac}", "facing": fac, "date": "2026-10-06"})
        wr.flush()
        (tmp / "artpipe" / "failed").mkdir(parents=True)
        (tmp / "artpipe" / "failed" / "foxwing_v1.manifest.json").write_text(json.dumps({"id": "foxwing_v1", "worker_status": "failed_canon"}))
        os.environ["ARTPIPE_STATE_DIR"] = str(tmp / "artpipe")
        row_c = {"key": "RG_Plant_Brambles", "kind": "flora", "label": "thorny bush", "defNames": ["RG_Plant_Brambles"],
                 "placements": [], "canon": {"entry": None}, "twins": [], "artpipe_state_jobs": [],
                 "art": {"resources": [{"res": "Things/Plant/RG_Brambles", "role": "body"}]}}
        row_d = {"key": "RM_Foxwing", "kind": "fauna", "label": "foxwing", "defNames": ["RM_Foxwing"], "placements": [],
                 "canon": {"entry": None}, "twins": [], "art": {"resources": []}, "artpipe_state_jobs": []}
        cen2 = tmp / "census2.json"
        cen2.write_text(json.dumps({"biome_order": ["RM_Test"], "git_head": "x",
                                    "biomes": {"RM_Test": {"label": "Test", "rows": [row_c, row_d]}}}))
        bout2 = tmp / "sheet" / "test2_sheet.html"
        art_sheet.generate_biome("RM_Test", cen2, bout2, "T", allow_failing="selftest fixture")
        items2 = {i["id"]: i for i in json.loads(re.search(r'<script id="ITEMS" type="application/json">(.*?)</script>',
                                                          bout2.read_text(), re.S).group(1))}
        cols_c = [c for g in items2["RG_Plant_Brambles"]["graphics"] for c in g["cols"]]
        check(any(sblue in c["faces"].values() for c in cols_c), "donor-prefixed row RG_Plant_Brambles shows the render brambles_v1")
        cols_d = [c for g in items2["RM_Foxwing"]["graphics"] for c in g["cols"]]
        check(any(syellow in c["faces"].values() and "failed canon check" in c["label"] for c in cols_d),
              "a failed_canon render is a candidate badged 'failed canon check'")
        fg = [g for g in items2["RM_Foxwing"]["graphics"] if g.get("flip")]
        check(len(fg) == 1 and len(fg[0]["cols"]) == 1 and len(fg[0]["cols"][0]["faces"]) == 6
              and fg[0]["nframes"] == 3 and fg[0]["flipFacings"] == ["east", "south"]
              and fg[0]["facings"][:3] == ["1_east", "2_east", "3_east"],
              "flight frames join into ONE flip-book set, a frames x facings grid")
        check(not any(set(frames.values()) & set(c["faces"].values()) for g in items2["RM_Foxwing"]["graphics"]
                      if not g.get("flip") for c in g["cols"]), "flight frames never also show as one-frame name sets")
    else:
        print("review-sheets template absent — sheet checks UNMEASURED, not a pass or a fail")

    # ART_RULING_RENAME_CARRY_1: a redo'd picture can't be resurrected or spread to another creature
    purple, white = png((128, 0, 128, 255)), png((255, 255, 255, 255))
    spurple, swhite = L.sha256_bytes(purple), L.sha256_bytes(white)
    ik = "Things/Pawn/Animal/RM_Ikee/RM_Ikee_south.png"
    L.store_put_bytes(purple), L.store_put_bytes(white)
    L.install(mod, ik, spurple, reason="script:selftest")
    snap2 = {"sheetId": "c", "rows": {"RM_Ikee": {"subject_key": "ikee", "columns": {"A": {"south": spurple}},
                                                  "labels": {"A": "IN GAME — FixtureMod"}}}}
    sp2, dec2 = tmp / "c.snapshot.json", tmp / "c.decisions.json"
    sp2.write_text(json.dumps(snap2))
    dec2.write_text(json.dumps({"snapshot": str(sp2), "savedBy": "serve_sheet.py", "writeCount": 1,
                                "decisions": {"RM_Ikee": {"decision": "redo", "note": "This thing is hideous",
                                                          "at": "2026-10-05T00:00:00Z"}}}))
    r = ingest.ingest(dec2, defer_redo_jobs=True)
    check(r["ok"] and r.get("rejected") == 1 and L.Index().rejection(spurple), f"a redo records the IN GAME bytes as rejected ({r})")

    def refused(rel_, sha_, **kw):
        try:
            L.install(mod, rel_, sha_, **kw)
            return None
        except L.Refused as e:
            return str(e)
    check(refused("Things/Pawn/Animal/RM_Ogleknot/RM_Ogleknot_south.png", spurple, reason="script:selftest"),
          "a redo'd picture cannot be copied onto another creature")
    check(refused("Things/Pawn/Animal/RUT_Ikee/RUT_Ikee_south.png", spurple, reason="script:selftest") is None,
          "the same creature's current picture may still be moved (RUT_ twin)")
    cik = "Things/Pawn/Animal/RM_ContagionIkee/RM_ContagionIkee_south.png"
    check(refused(cik, spurple, reason="script:selftest"), "a renamed def without an alias is another creature")
    (L.ledger_dir() / L.ALIASES_FILE).write_text(json.dumps({"aliases": {"ContagionIkee": "ikee"}}))
    check(refused(cik, spurple, reason="script:selftest") is None and L.canonical_subject("contagionikee") == "ikee",
          "an aliased rename is the same creature")
    check(any(x.get("subject_key") == "ikee" for x in L.Index().subject_rulings({"contagionikee"})),
          "rulings follow a creature through its alias")
    for rel_ in (ik, cik, "Things/Pawn/Animal/RUT_Ikee/RUT_Ikee_south.png"):
        L.install(mod, rel_, swhite, reason="script:selftest")
    msg = refused("Things/Pawn/Animal/RM_Ikee/RM_Ikee_east.png", spurple, reason="script:selftest")
    check(bool(msg) and "resurrects" in msg and "hideous" in msg, "a redo'd picture live nowhere cannot be resurrected, and says why")
    check(refused(ik, spurple, owner_said="actually I like the purple one") is None, "his words still bring it back")
    import art_guard
    check(art_guard._authorized({"type": "live", "sha": None, "prev": spurple, "reason": "retire", "said": "remove it"},
                                L.Index()) is None, "the guard accepts a retire on the owner's words")

    # selftest the CLI entry point end to end (subprocess, not import)
    out = subprocess.run([sys.executable, str(HERE / "art.py"), "status", "Things/Beast/Beast"],
                         capture_output=True, text=True, env=os.environ)
    check(out.returncode == 0 and "LIVE" in out.stdout, "art.py status runs as a CLI")

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{'ALL PASS' if not FAILS else str(len(FAILS)) + ' FAIL'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
