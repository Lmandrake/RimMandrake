#!/usr/bin/env python3
"""selftest_binding_sheet.py — the §5.3 step 4 binding sheet and its enact (ART_SUBJECT_RESOLVER_1).
Temp ledger, store, src and artpipe dir only."""
from __future__ import annotations

# selftest temp containment: every mkdtemp below, and every child process via TMPDIR, lands in one private dir removed at exit
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_binding_sheet_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import json
import os
import struct
import sys
import tempfile
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FAILS = []


def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        FAILS.append(m)


def png(rgba):
    raw = b"".join(b"\x00" + bytes(rgba) * 4 for _ in range(4))
    ch = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
    return b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", 4, 4, 8, 6, 0, 0, 0)) + ch(b"IDAT", zlib.compress(raw)) + ch(b"IEND", b"")


def main():
    tmp = Path(tempfile.mkdtemp(prefix="bsheet-"))
    os.environ.update(ARTSTORE=str(tmp / "store"), ART_LEDGER_DIR=str(tmp / "ledger"), ART_SRC_ROOT=str(tmp / "src"),
                      ARTPIPE_STATE_DIR=str(tmp / "ap"), ARTPIPE_LEGACY_DIR=str(tmp / "nolegacy"), AGENT_SEAT="bench")
    import artledger as L
    import backfill as B
    import binding_sheet as BS
    import render_subjects as RS
    import subject as S
    d = tmp / "src" / "Tier" / "ModX" / "Defs"
    d.mkdir(parents=True)
    (d / "d.xml").write_text("<Defs><ThingDef><defName>RM_Zorbex</defName><label>zorbex</label></ThingDef>"
                             "<ThingDef><defName>RM_Quillback</defName></ThingDef>"
                             "<ThingDef><defName>RM_Plonk</defName></ThingDef><ThingDef><defName>RSW_Plonk</defName></ThingDef></Defs>")
    jobs = {"zorbex_v1_south": (50, 60, 70, 255), "zorbex_v1_east": (51, 60, 70, 255),
            "mystery_thing_v1_south": (200, 5, 5, 255), "mystery_thing_v1_east": (201, 5, 5, 255),
            "mock_hose_v1": (5, 200, 5, 255), "plonk_v1": (5, 5, 200, 255)}
    for name, rgb in jobs.items():
        dd = tmp / "ap" / "_artsrc" / name
        dd.mkdir(parents=True)
        (dd / "x.png").write_bytes(png(rgb))
    B.step_artpipe(budget=60)
    world = lambda: S.World(src_root=tmp / "src", canon_root=tmp / "nocanon", artpipe_root=tmp / "ap", facts_root=tmp / "nofacts")
    res = RS.build(world())
    w = world()
    rows = BS.worklist(res["entries"], w)
    by = {r["id"]: r for r in rows}
    check(set(by) == {"mystery_thing_v1", "mock_hose_v1", "plonk_v1"}, f"one row per open job family ({sorted(by)})")
    check(len(by["mystery_thing_v1"]["renders"]) == 2, "both facings of one job sit on one row")
    check(by["plonk_v1"]["resolution"] == "ambiguous" and by["plonk_v1"]["candidates"] == ["RM_Plonk", "RSW_Plonk"],
          f"ambiguous row lists its candidates ({by['plonk_v1']['candidates']})")
    html = BS.render_html(rows, {})
    check(all(f'data-id="{r}"' in html for r in by) and "RSW_Plonk" in html and "no subject" in html,
          "sheet has a row, candidates and the no-subject choice for every family")
    # canon refs per row: a candidate's own canon entry, else a family token naming a canon dir
    canon = tmp / "canon"
    for slug, rgb in (("plonk", (4, 4, 4, 255)), ("mystery", (1, 2, 3, 255))):
        (canon / slug).mkdir(parents=True)
        (canon / slug / "description.md").write_text(f"# {slug}\n")
        (canon / slug / "ref.png").write_bytes(png(rgb))
    cworld = lambda: S.World(src_root=tmp / "src", canon_root=canon, artpipe_root=tmp / "ap", facts_root=tmp / "nofacts")
    cby = {r["id"]: r for r in BS.worklist(res["entries"], cworld())}
    cref = lambda fam: [(c["slug"], c["match"]) for c in cby[fam]["canon"]]
    check([s for s, _ in cref("plonk_v1")] == ["plonk"] and cref("plonk_v1")[0][1] != "family-token"
          and cby["plonk_v1"]["canon"][0]["images"],
          f"an ambiguous row carries its candidates' canon entry with images ({cref('plonk_v1')})")
    check(cref("mystery_thing_v1") == [("mystery", "family-token")] and cby["mystery_thing_v1"]["canon"][0]["images"],
          f"an unresolved row with no candidate gets the canon entry its family token names ({cref('mystery_thing_v1')})")
    check(cref("mock_hose_v1") == [], f"a row whose family names no canon dir shows none ({cref('mock_hose_v1')})")
    # build(): worklist + sheet + decisions skeleton on disk, every render thumbnailed from the store, canon images copied
    ix = tmp / "ix.json"
    ix.write_text(json.dumps(res))
    real_world = S.World
    S.World = lambda *a, **k: real_world(src_root=tmp / "src", canon_root=canon, artpipe_root=tmp / "ap", facts_root=tmp / "nofacts")
    try:
        out = tmp / "sheet"
        bres = BS.build(ix, out)
    finally:
        S.World = real_world
    n_renders = sum(len(r["renders"]) for r in cby.values())
    check(bres["families"] == 3 and bres["renders"] == n_renders == 4 and bres["ambiguous"] == 1
          and bres["thumbs_missing_from_store"] == 0, f"build counts every open family and render, none missing ({bres})")
    wl = json.loads((out / "binding_sheet.worklist.json").read_text())
    dsk = json.loads((out / "binding_sheet.decisions.json").read_text())
    check({r["id"] for r in wl} == set(cby) and dsk["sheetId"] == "binding_sheet" and dsk["decisions"] == {},
          "build writes the worklist and an empty decisions skeleton")
    bhtml = (out / "binding_sheet.html").read_text()
    thumbs_ok = []
    for r in wl:
        for rr in r["renders"]:
            name = L.store_path(rr["sha"]).name
            thumbs_ok.append(f'<img src="img/{name}" title="{rr["job"]}">' in bhtml and (out / "img" / name).read_bytes()
                             == L.store_path(rr["sha"]).read_bytes())
    check(len(thumbs_ok) == 4 and all(thumbs_ok), f"the sheet shows every render's thumbnail, copied from the store ({thumbs_ok})")
    check(all((out / "img" / f"canon_{s}_0.png").is_file() and f'<img src="img/canon_{s}_0.png">' in bhtml
              for s in ("plonk", "mystery")) and "mystery [family-token]" in bhtml,
          "the sheet shows each row's canon entry and its copied canon image")
    known = set(w.defs)
    ev_count = lambda t: len([e for e in L.read_events() if e.get("type") == t])
    b0, n0 = ev_count("binding"), ev_count("no_subject")
    r = BS.enact({"decisions": {"plonk_v1": {"decision": "bind", "subject": "RM_Nope"},
                                "mock_hose_v1": {"decision": "no-subject", "reason": "liquid-join mock"}}}, rows, "owner", None, known)
    check(r["refused"] and r["written"] == 0 and ev_count("binding") == b0 and ev_count("no_subject") == n0,
          f"an unknown defName refuses the whole file, nothing written ({r['refused']})")
    try:
        BS.enact({"decisions": {}}, rows, "agent", None, known)
        check(False, "an agent pick without --why is refused")
    except ValueError:
        check(True, "an agent pick without --why is refused")
    dec = {"decisions": {"plonk_v1": {"decision": "bind", "subject": "RSW_Plonk"},
                         "mock_hose_v1": {"decision": "no-subject", "reason": "liquid-join mock"},
                         "mystery_thing_v1": {"decision": "skip"}}}
    r = BS.enact(dec, rows, "agent", "single obvious candidate", known)
    check(r["written"] == 2 and not r["refused"], f"agent enact writes one event per render of the picked rows ({r})")
    bev = [e for e in L.read_events() if e.get("type") == "binding" and e.get("job") == "plonk_v1"]
    check(len(bev) == 1 and bev[0]["confidence"] == "name-matched" and bev[0]["evidence"].startswith("delegated: art-binding"),
          "an agent pick is name-matched and logged as delegated")
    r2 = BS.enact(dec, rows, "agent", "single obvious candidate", known)
    check(r2["written"] == 0, "re-enacting the same decisions writes nothing")
    res2 = RS.build(world())
    e = {v["job"]: v for v in res2["entries"].values()}
    check(e["plonk_v1"]["resolution"] == "name-matched" and e["plonk_v1"]["subjects"] == ["RSW_Plonk"],
          f"render_subjects reads an agent's binding as name-matched, not bound ({e['plonk_v1']['resolution']})")
    check(e["mock_hose_v1"]["resolution"] == "no-subject", f"a no_subject event closes the render ({e['mock_hose_v1']['resolution']})")
    check(e["mystery_thing_v1_south"]["resolution"] == "unresolved", "a skipped row stays open")
    RS.write_bindings(res2)
    e3 = {v["job"]: v for v in RS.build(world())["entries"].values()}
    check(e3["zorbex_v1_south"]["resolution"] == "name-matched" and e3["zorbex_v1_south"]["via"] == "binding",
          f"a derived token binding read back stays name-matched (was reported bound) ({e3['zorbex_v1_south']['resolution']})")
    BS.enact({"decisions": {"plonk_v1": {"decision": "bind", "subject": "RM_Plonk"}}}, rows, "owner", None, known)
    e4 = {v["job"]: v for v in RS.build(world())["entries"].values()}
    check(e4["plonk_v1"]["resolution"] == "bound" and e4["plonk_v1"]["subjects"] == ["RM_Plonk"],
          "an owner pick is bound and outranks the agent's name-matched pick")
    print("RESULT", "FAIL" if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
