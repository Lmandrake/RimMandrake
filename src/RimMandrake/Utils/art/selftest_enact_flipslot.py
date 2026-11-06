#!/usr/bin/env python3
"""selftest_enact_flipslot.py — SHEET_ENACT_FLIPSLOT_REDRAW_FIX_EMPTY_NOTE: a redraw on a `_flip:` flight slot.

The instance (enact_e8de0861_firewasp_v1, 2026-11-01): he picked body B, retired body A and flight set F, set the
`_flip:` slot to redraw with no note. enact filed ONE artpipe job: facings [] (flip columns are keyed 1_east...), an
empty note, and the retired body A attached as its reference.

  A a `_flip:` slot set to redraw (and an asks.more / asks.facings naming a `_flip:` slot) files NO artpipe job;
  B ...it is a TODO in plan["asks"] naming the flyer pipeline, until `--mark-done <row> --ask flipbook`;
  C a non-flip slot redraw on a row whose body letter he retired never attaches that retired picture as reference;
  D a non-flip slot redraw on a row with nothing retired still attaches the in-game picture (unchanged behaviour).
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
    F = W.build(T.SCRATCH / f"enact_flipslot_{os.getpid()}")
    import artledger as L
    import enact as E
    s = F["s"]
    doc = json.loads(F["decisions"].read_text())
    sp = Path(doc["snapshot"])
    snap = json.loads(sp.read_text())
    FL = "_flip:swanimals/Strill/Strill_Flying_"
    BODY = "swanimals/Strill/Strill"
    KY = "swanimals/Kite/Kite_young"
    ky = L.store_put_bytes(T.noise_png(911))
    kr = snap["rows"]["RSW_Kite"]
    kr["columns"]["Y"] = {"east": ky}
    kr["graphic_of"]["Y"] = KY
    kr["labels"]["Y"] = "IN GAME — young"
    fr = snap["rows"]["RSW_Fan"]
    fr["columns"]["Y"] = {"east": L.store_put_bytes(T.noise_png(912))}
    fr["graphic_of"]["Y"] = "swanimals/Fan/Fan_young"
    fr["labels"]["Y"] = "IN GAME — young"
    sp.write_text(json.dumps(snap))
    at = "2026-11-01T04:12:50.186Z"

    def d(dec, **kw):
        return dict({"schema": 2, "decision": dec, "at": at, "decidedAt": at, "note": ""}, **kw)
    D = doc["decisions"]
    for k in list(D):
        D.pop(k)
    # the firewasp shape: body picked, body A and flight E retired, flight slot set to redraw, empty note
    D["RSW_Strill"] = d("A", slots={FL: {"state": "redraw"}}, retire={BODY: ["A"], FL: ["E"]},
                        asks={"more": [{"slot": FL, "n": 2}], "facings": {"slot": FL, "faces": ["north"]}})
    # a young-slot redraw on a row whose IN GAME body letter A he retired
    D["RSW_Kite"] = d("B", slots={KY: {"state": "redraw"}}, retire={"swanimals/Kite/Kite": ["A"]})
    # the same with nothing retired
    D["RSW_Fan"] = d("B", slots={"swanimals/Fan/Fan_young": {"state": "redraw"}})
    F["decisions"].write_text(json.dumps(doc))
    os.environ["ART_OLD_TICKS_CONFIRM"] = str(F["root"] / "old_ticks_confirm.decisions.json")
    os.environ["ART_BIOME_SHEETS_DIR"] = str(F["root"] / "biomes")
    E.reset_caches()
    R = E.enact(F["decisions"], apply=False, no_deploy=True)
    check(R["ok"], f"dry run ok ({R.get('error')})")
    P = R["plan"]
    jr = E.job_rows(P)
    check(not any(str(q.get("slot") or "").startswith("_flip:") for q in P["queue"])
          and not any(j["target_def"] == "RSW_Strill" for j in jr),
          "A a _flip: slot redraw / more / facings files no artpipe job (no single sprite, no empty-note prompt)")
    fa = [x for x in P["asks"] if x.startswith("RSW_Strill: ask flipbook")]
    check(len(fa) == 1 and "Strill_Flying_" in fa[0] and "--ask flipbook" in fa[0],
          f"B ...one flipbook TODO naming the set and the mark-done ({fa})")
    kj = [j for j in jr if j["target_def"] == "RSW_Kite"]
    check(len(kj) == 1 and str(L.store_path(s["ta"])) not in kj[0]["canon_reference"],
          f"C a slot redraw never carries the body picture he retired ({kj and kj[0]['canon_reference']})")
    fj = [j for j in jr if j["target_def"] == "RSW_Fan"]
    check(len(fj) == 1 and fj[0]["canon_reference"] == [str(L.store_path(s["fa"]))],
          "D with nothing retired the in-game picture is still the reference")
    E.enact(F["decisions"], apply=False, no_deploy=True, mark_done=["RSW_Strill"], ask="flipbook")
    E.reset_caches()
    R2 = E.enact(F["decisions"], apply=False, no_deploy=True)
    check(not any(x.startswith("RSW_Strill: ask flipbook") for x in R2["plan"]["asks"])
          and not any(j["target_def"] == "RSW_Strill" for j in E.job_rows(R2["plan"])),
          "B --mark-done --ask flipbook closes the TODO and still files no job")
    R3 = E.enact(F["decisions"], apply=False, no_deploy=True, mark_done=["RSW_Fan"], ask="flipbook")
    check(any("RSW_Fan --ask flipbook" in c for c in R3["conflicts"]), "B --ask flipbook on a row with no flip ask is refused")
    print(f"{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
