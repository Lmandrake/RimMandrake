#!/usr/bin/env python3
"""selftest_enact_stale_lane.py — `art.py enact` never installs a pick at a lane path from an OLDER build of the sheet
(ENACT_STALE_SLOT_KEY_MIGRATE_PATH, SHEET_SCHEMA1_FIX_MOVED_LETTER).

A rebuild that only adds columns keeps the snapshotId while lanes (graphic_of) can be renamed or moved, so the record's
slot key, or the lane a letter had, can name an old texPath — in the real records an RM_BrineElder pick keyed by
RM_SaltChimney's texPath. Enact reads the snapshot revision he clicked on (built at or before his click) and either
resolves the lane through it (a proved rename) or refuses by name. The decisions record is never rewritten.

  1 a slot key that is ANOTHER def's live path (swanimals/Fan/Fan) and no older snapshot shows it on this row: refused
    by name; nothing lands on Fan_east.png, and the letter does not install through `decision` either;
  2 a slot key from an older build where the same pictures sat under that key and today sit under one NEW lane (a
    rename): installs at today's lane, reported in lane_resolved, no conflict, the record file unchanged;
  3 a slot key whose pictures moved into a lane that already existed on the sheet he clicked on (not a rename): refused;
  4 schema 1: `decision` Y was the adult lane's set on the sheet he clicked on, today's rebuild files Y under the young
    lane: installs at the adult path (the sheet he saw), never at the young path;
  6 a pick whose pictures all ship already (an enacted row, whose def was then repointed): no copy and no conflict;
  7 his lane was a DONOR's (nothing of ours ships there) and today's lane is new: routed as before (the install step
    sends a donor-lane pick to the row's own path), no refusal, nothing written at the donor path;
  5 schema 1 with today's snapshot built BEFORE his click: routed by today's snapshot as before (no lookup, no change).
Fixture under /home/mandrake/rm/scratch/BENCH (never /tmp), from selftest_enact_ws; git history is replaced by a list.
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
    F = W.build(T.SCRATCH / f"enact_stalelane_{os.getpid()}")
    import artledger as L
    import enact as E
    ys = {"ye": L.store_put_bytes(T.noise_png(900))}
    doc = json.loads(F["decisions"].read_text())
    sp = Path(doc["snapshot"])
    snap = json.loads(sp.read_text())
    AD, KY, OLD = "swanimals/Kite/Kite", "swanimals/Kite/Kite_young", "oldfolder/Kite/Kite"
    kr = snap["rows"]["RSW_Kite"]
    kr["columns"]["Y"] = {"east": ys["ye"]}
    kr["graphic_of"]["Y"] = KY
    kr["labels"]["Y"] = "render kite_y"
    at = "2026-10-10T10:00:00.000Z"
    snap["built"] = "2026-10-12T00:00:00-0700"          # today's build is AFTER his click
    sp.write_text(json.dumps(snap))
    os.environ["ART_BIOME_SHEETS_DIR"] = str(F["root"] / "biomes")
    history: list = []
    E.snapshot_revisions = lambda p: [snap] + history     # stands in for disk + git revisions

    def older(gof: dict) -> dict:
        s = json.loads(json.dumps(snap))
        s["built"] = "2026-10-10T02:00:00-0700"         # 09:00Z, before the click at 10:00Z
        s["rows"]["RSW_Kite"]["graphic_of"] = gof
        return s

    def plan(rec):
        d = json.loads(json.dumps(doc))
        d["decisions"] = {"RSW_Kite": {k: x for k, x in dict({"schema": 2, "at": at, "decidedAt": at, "note": ""},
                                                             **rec).items() if x is not None}}   # schema None: a v1 record
        p = F["root"] / f"case_{len(FAILS)}_{abs(hash(json.dumps(rec, sort_keys=True)))}.decisions.json"
        p.write_text(json.dumps(d))
        before = p.read_bytes()
        E.reset_caches()
        r = E.enact(p, apply=False, no_deploy=True)
        check(r["ok"], f"dry run ok ({r.get('error')})")
        check(p.read_bytes() == before, "the decisions record is not rewritten")
        return r, [i for i in r["plan"]["install"] if i["row"] == "RSW_Kite"]

    def slot(L_):
        return {"state": "pick", "pick": L_, "slot_id": "RSW_Kite/lifeStages[2].bodyGraphicData", "at": at}
    try:
        history[:] = []
        r, inst = plan({"decision": "B", "slots": {"swanimals/Fan/Fan": slot("B")}})
        check(not any(i["rel"].startswith("swanimals/Fan/") for i in inst),
              f"1 a stale key naming another def's live path installs nothing there ({inst})")
        check(not any(i["letter"] == "B" for i in inst), f"1 ...nor anywhere through `decision` ({inst})")
        check(any(c.startswith("RSW_Kite: slot swanimals/Fan/Fan pick B names a lane today's sheet does not have")
                  for c in r["conflicts"]), f"1 ...and is refused BY NAME, full stale key ({r['conflicts']})")

        history[:] = [older({"A": OLD, "B": OLD, "C": OLD, "Y": KY})]
        r, inst = plan({"decision": "B", "slots": {OLD: slot("B")}})
        check(any(i["letter"] == "B" and i["rel"] == "swanimals/Kite/Kite_east.png" for i in inst)
              and not any(i["rel"].startswith("oldfolder/") for i in inst),
              f"2 a renamed lane installs at today's path, never the old one ({inst})")
        check(any(x.startswith(f"RSW_Kite: slot {OLD} pick B -> {AD}") for x in r["plan"].get("lane_resolved", []))
              and not any("RSW_Kite:" in c for c in r["conflicts"]),
              f"2 ...reported as resolved, no conflict ({r["plan"].get("lane_resolved", [])} / {r['conflicts']})")

        history[:] = [older({"A": AD, "B": OLD, "C": AD, "Y": KY})]
        r, inst = plan({"decision": "B", "slots": {OLD: slot("B")}})
        check(not any(i["letter"] == "B" for i in inst) and any(
            c.startswith(f"RSW_Kite: slot {OLD} pick B names a lane") and "not a rename" in c for c in r["conflicts"]),
              f"3 pictures moved into a lane that already existed: refused ({inst} / {r['conflicts']})")

        history[:] = [older({"A": AD, "B": AD, "C": AD, "Y": AD})]
        r, inst = plan({"schema": None, "decision": "Y"})
        check(any(i["letter"] == "Y" and i["rel"] == "swanimals/Kite/Kite_east.png" for i in inst)
              and not any(i["rel"].startswith("swanimals/Kite/Kite_young") for i in inst),
              f"4 schema 1: Y installs in the lane it had on the sheet he clicked on, not today's ({inst})")
        check(not any("RSW_Kite: pick Y" in c for c in r["conflicts"])
              and any(x.startswith("RSW_Kite: pick Y -> swanimals/Kite/Kite,") for x in r["plan"].get("lane_resolved", [])),
              f"4 ...reported in lane_resolved ({r["plan"].get("lane_resolved", [])} / {r['conflicts']})")

        history[:] = []
        shas_b = {x for x in kr["columns"]["B"].values() if x}
        live0 = L.Index.live_anywhere
        L.Index.live_anywhere = lambda self, s: ["swanimals/Kite/Kite_east.png"] if s in shas_b else live0(self, s)
        try:
            r, inst = plan({"decision": "B", "slots": {"swanimals/Fan/Fan": slot("B")}})
            r1, _ = plan({"schema": None, "picks": {OLD: "B"}})
        finally:
            L.Index.live_anywhere = live0
        check(not any(i["rel"].startswith("swanimals/Fan/") for i in inst)
              and not any("RSW_Kite:" in c for c in r["conflicts"] + r1["conflicts"]),
              f"6 an already-shipping pick under an old lane name copies nothing and asks nothing (an enacted row) "
              f"({inst} / {r['conflicts'] + r1['conflicts']})")

        DON = "Things/Pawn/Animal/Donorbeast/Donorbeast"    # a donor lane: nothing of ours ships there
        h = older({"A": DON, "B": DON, "C": DON, "Y": KY, "Z": DON})
        h["rows"]["RSW_Kite"]["columns"]["Z"] = {"east": "0" * 64}   # a set gone today: no rename can be proved
        history[:] = [h]
        r, inst = plan({"schema": None, "decision": "B"})
        check(any(i["letter"] == "B" and i["rel"] == "swanimals/Kite/Kite_east.png" for i in inst)
              and not any("RSW_Kite:" in c for c in r["conflicts"]),
              f"7 schema 1: his lane was a donor's (ships nothing of ours), today's lane is new: routed as before, "
              f"no refusal ({inst} / {r['conflicts']})")
        r, inst = plan({"decision": "B", "slots": {DON: slot("B")}})
        check(not any(i["rel"].startswith("Things/Pawn/Animal/Donorbeast/") for i in inst)
              and not any("RSW_Kite:" in c and "names a lane" in c for c in r["conflicts"]),
              f"7 ...a slot keyed by that donor lane: no refusal, nothing written at the donor path "
              f"({inst} / {r['conflicts']})")

        snap["built"] = "2026-10-09T00:00:00-0700"       # today's build is BEFORE his click: it is the sheet he saw
        sp.write_text(json.dumps(snap))
        r, inst = plan({"schema": None, "decision": "B"})
        check(any(i["letter"] == "B" and i["rel"] == "swanimals/Kite/Kite_east.png" for i in inst)
              and not r["plan"].get("lane_resolved", []), f"5 an unrebuilt sheet routes as before ({inst})")
    finally:
        os.environ.pop("ART_BIOME_SHEETS_DIR", None)
    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
