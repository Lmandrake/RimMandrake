#!/usr/bin/env python3
"""selftest_backfill_bind.py — backfill.step_artpipe reads a job's target_def/install_to (ART_SUBJECT_RESOLVER_1 §5.2).
Temp ledger, store and artpipe dir only."""
from __future__ import annotations

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
    tmp = Path(tempfile.mkdtemp(prefix="bfbind-"))
    os.environ.update(ARTSTORE=str(tmp / "store"), ART_LEDGER_DIR=str(tmp / "ledger"), ART_SRC_ROOT=str(tmp / "src"),
                      ARTPIPE_STATE_DIR=str(tmp / "ap"), ARTPIPE_LEGACY_DIR=str(tmp / "nolegacy"), AGENT_SEAT="bench")
    import artledger as L
    import backfill as B
    for name, rgb, man in (("a_v1", (1, 2, 3, 255), {"id": "a_v1", "target_def": "RM_Aaa", "target_original": ["AA_Aaa"],
                                                      "install_to": "Mod/Textures/Things/Aaa/Aaa_south.png"}),
                           ("b_v1", (9, 8, 7, 255), {"id": "b_v1"})):
        d = tmp / "ap" / "_artsrc" / name
        d.mkdir(parents=True)
        (d / "x.png").write_bytes(png(rgb))
        (tmp / "ap" / "done").mkdir(exist_ok=True)
        (tmp / "ap" / "done" / f"{name}.json").write_text(json.dumps(man))
    r = B.step_artpipe(budget=60)
    ev = L.read_events()
    va = [e for e in ev if e.get("type") == "variant" and e.get("job") == "a_v1"]
    bd = [e for e in ev if e.get("type") == "binding"]
    check(len(va) == 1 and va[0].get("target_def") == "RM_Aaa" and va[0].get("install_to", "").endswith("Aaa_south.png"),
          f"variant carries target_def/install_to ({r})")
    check(len(bd) == 1 and bd[0]["subject"] == "RM_Aaa" and bd[0]["confidence"] == "bound" and bd[0]["originals"] == ["AA_Aaa"],
          "one bound binding event; the job with no target_def gets none")
    idx = L.Index()
    check(len(idx.bindings_by_subject["RM_Aaa"]) == 1 and va[0]["sha"] in idx.bindings, "Index folds bindings")
    r2 = B.step_artpipe(budget=60)
    check(r2.get("new_events") == 0, f"idempotent ({r2})")
    # derived subject index: a fixture src + a render with no target_def
    d = tmp / "src" / "Tier" / "ModX" / "Defs"
    d.mkdir(parents=True)
    (d / "d.xml").write_text("<Defs><ThingDef><defName>RM_Zorbex</defName><label>zorbex</label></ThingDef>"
                             "<ThingDef><defName>RM_Quillback</defName></ThingDef></Defs>")
    for name, rgb in (("zorbex_v1", (50, 60, 70, 255)), ("mystery_thing_v1", (200, 5, 5, 255))):
        dd = tmp / "ap" / "_artsrc" / name
        dd.mkdir(parents=True)
        (dd / "x.png").write_bytes(png(rgb))
    B.step_artpipe(budget=60)
    import render_subjects as RS
    import subject as S
    res = RS.build(S.World(src_root=tmp / "src", canon_root=tmp / "nocanon", artpipe_root=tmp / "ap", facts_root=tmp / "nofacts"))
    e = {v["job"]: v for v in res["entries"].values()}
    check(e["a_v1"]["resolution"] == "bound" and e["a_v1"]["via"] == "binding", "bound by the job's binding event")
    check(e["zorbex_v1"]["resolution"] == "name-matched" and e["zorbex_v1"]["subjects"] == ["RM_Zorbex"],
          f"whole-token family match names one subject ({e['zorbex_v1']})")
    check(e["mystery_thing_v1"]["resolution"] == "unresolved", "no evidence -> unresolved, not guessed")
    before = len([x for x in L.read_events() if x.get("type") == "binding"])
    n1 = RS.write_bindings(res)
    n2 = RS.write_bindings(res)
    check(n1 == 1 and n2 == 0 and before + 1 == len([x for x in L.read_events() if x.get("type") == "binding"]),
          f"derived bindings written once, idempotent ({n1},{n2})")
    check(not any(p.name.endswith(".json") and "binding" in p.read_text() for p in (tmp / "ap" / "done").glob("*.json")),
          "no job file in the artpipe state dir was touched")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
