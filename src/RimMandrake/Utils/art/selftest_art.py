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
