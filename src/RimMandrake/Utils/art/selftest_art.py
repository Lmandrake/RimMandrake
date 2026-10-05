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
        rb = art_sheet.generate_biome("RM_Test", cen, bout, "T")
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
        rb2 = art_sheet.generate_biome("RM_Test", cen, bout, "T")
        check(rb2["wrote_decisions"] and rb2["snapshotId"] == rb["snapshotId"], "biome rebuild: untouched prefill regenerated, letters stable")
        bdec["savedBy"], bdec["writeCount"] = "serve_sheet.py", 1
        (tmp / "sheet" / "test_sheet.decisions.json").write_text(json.dumps(bdec))
        check(not art_sheet.generate_biome("RM_Test", cen, bout, "T")["wrote_decisions"],
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
        art_sheet.generate_biome("RM_Test", cen2, bout2, "T")
        items2 = {i["id"]: i for i in json.loads(re.search(r'<script id="ITEMS" type="application/json">(.*?)</script>',
                                                          bout2.read_text(), re.S).group(1))}
        cols_c = [c for g in items2["RG_Plant_Brambles"]["graphics"] for c in g["cols"]]
        check(any(sblue in c["faces"].values() for c in cols_c), "donor-prefixed row RG_Plant_Brambles shows the render brambles_v1")
        cols_d = [c for g in items2["RM_Foxwing"]["graphics"] for c in g["cols"]]
        check(any(syellow in c["faces"].values() and "failed canon check" in c["label"] for c in cols_d),
              "a failed_canon render is a candidate badged 'failed canon check'")
    else:
        print("review-sheets template absent — sheet checks UNMEASURED, not a pass or a fail")

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
