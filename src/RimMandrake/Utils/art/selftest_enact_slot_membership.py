#!/usr/bin/env python3
"""selftest_enact_slot_membership.py — `art.py enact` refuses a schema-2 slot pick whose letter is a set of ANOTHER lane
of the snapshot (ENACT_SLOT_PICK_VERIFY_MEMBERSHIP, defence in depth behind c3a382b9e0).

A sheet hotkey once reached the primary slot with any letter of the row: the record said slots[adult].pick = Y where Y is
a picture of the YOUNG lane, and enact installed Y's bytes at the adult texPath (wrong texture in game).

  1 slots[adult].pick = Y (a young-lane set): refused by name in conflicts; Y installs nowhere (not at the adult path, and
    not at the young path either, which `decision` = Y would otherwise route it to);
  2 slots[adult].pick = B (a set of the adult lane): still installs at the adult path, no refusal;
  3 a render assigned to the adult slot (assign[R] = adult) and picked there: allowed;
  5 a by-name render NOT assigned to the adult slot (row has two lanes) picked there: refused by name;
  4 a slot key the snapshot does not know (an older build's path) where nothing of ours ships: not membership-checked, no
    refusal, and nothing written under the old path (ENACT_STALE_SLOT_KEY_MIGRATE_PATH: a stale key that ships is
    refused, a rename is resolved — selftest_enact_stale_lane).
Fixture under /home/mandrake/rm/scratch/BENCH (never /tmp), from selftest_enact_ws.
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
    F = W.build(T.SCRATCH / f"enact_slotmem_{os.getpid()}")
    import artledger as L
    import enact as E
    s = F["s"]
    ys = {k: L.store_put_bytes(T.noise_png(700 + i)) for i, k in enumerate(("ye", "re"))}
    doc = json.loads(F["decisions"].read_text())
    sp = Path(doc["snapshot"])
    snap = json.loads(sp.read_text())
    AD, KY = "swanimals/Kite/Kite", "swanimals/Kite/Kite_young"
    kr = snap["rows"]["RSW_Kite"]
    kr["columns"].update({"Y": {"east": ys["ye"]}, "R": {"east": ys["re"]}})
    kr["graphic_of"].update({"Y": KY, "R": "_byname"})
    kr["labels"].update({"Y": "IN GAME — young", "R": "render kite_r"})
    sp.write_text(json.dumps(snap))
    at = "2026-10-10T10:00:00.000Z"
    os.environ["ART_BIOME_SHEETS_DIR"] = str(F["root"] / "biomes")

    def plan(rec):
        d = json.loads(json.dumps(doc))
        d["decisions"] = {"RSW_Kite": dict({"schema": 2, "at": at, "decidedAt": at, "note": ""}, **rec)}
        p = F["root"] / f"case_{len(FAILS)}_{abs(hash(json.dumps(rec, sort_keys=True)))}.decisions.json"
        p.write_text(json.dumps(d))
        E.reset_caches()
        r = E.enact(p, apply=False, no_deploy=True)
        check(r["ok"], f"dry run ok ({r.get('error')})")
        return r

    def slot(L_):
        return {"state": "pick", "pick": L_, "slot_id": "RSW_Kite/lifeStages[2].bodyGraphicData", "at": at}
    try:
        r = plan({"decision": "Y", "slots": {AD: slot("Y")}})
        inst = [i for i in r["plan"]["install"] if i["row"] == "RSW_Kite"]
        check(not any(i["letter"] == "Y" for i in inst), f"1 a young-lane letter picked in the adult slot installs nowhere ({inst})")
        check(any(c.startswith("RSW_Kite: slot Kite pick Y is a set of Kite_young") for c in r["conflicts"]),
              f"1 ...and is refused BY NAME (row, slot, letter, its own lane) ({r['conflicts']})")
        r = plan({"decision": "B", "slots": {AD: slot("B")}})
        inst = [i for i in r["plan"]["install"] if i["row"] == "RSW_Kite"]
        check(any(i["letter"] == "B" and i["rel"] == "swanimals/Kite/Kite_east.png" for i in inst)
              and not any("RSW_Kite: slot" in c for c in r["conflicts"]), f"2 an adult-lane letter still installs ({inst})")
        r = plan({"decision": "R", "assign": {"R": AD}, "slots": {AD: slot("R")}})
        inst = [i for i in r["plan"]["install"] if i["row"] == "RSW_Kite"]
        check(any(i["letter"] == "R" and i["rel"] == "swanimals/Kite/Kite_east.png" for i in inst)
              and not any("RSW_Kite: slot" in c for c in r["conflicts"]),
              f"3 a render he assigned to the adult slot and picked there is allowed ({inst})")
        r = plan({"decision": "R", "slots": {AD: slot("R")}})
        inst = [i for i in r["plan"]["install"] if i["row"] == "RSW_Kite"]
        check(not any(i["letter"] == "R" for i in inst)
              and any(c.startswith("RSW_Kite: slot Kite pick R is an unassigned render") for c in r["conflicts"]),
              f"5 a by-name render never assigned to the adult slot (two lanes) is refused by name ({r['conflicts']})")
        r = plan({"decision": "B", "slots": {"oldfolder/Kite/Kite": slot("B")}})
        inst = [i for i in r["plan"]["install"] if i["row"] == "RSW_Kite"]
        check(not any(i["rel"].startswith("oldfolder/") for i in inst)
              and not any("RSW_Kite: slot" in c for c in r["conflicts"]),
              f"4 a slot key the snapshot does not know, shipping nothing: no refusal, nothing at the old path "
              f"({inst} / {r['conflicts']})")
    finally:
        os.environ.pop("ART_BIOME_SHEETS_DIR", None)
    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
