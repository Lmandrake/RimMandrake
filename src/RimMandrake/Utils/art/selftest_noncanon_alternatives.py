#!/usr/bin/env python3
"""The non-canon alternative of every canon row (BIOME_FLORAFAUNA_ART_REVIEW_1): the table is spelled out and coined,
and art_sheet.noncanon_option prefers a real stand-in, falls back to the table, and returns None otherwise."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import art_sheet as A               # noqa: E402
import check_pseudo_sw_name as PS   # noqa: E402

MODS = {"young", "pale", "feral", "longtail", "greater", "alpha", "wild", "plant", "gourd", "trap-backed"}


def main() -> int:
    fails = []
    alts = json.loads(A.NONCANON_ALTS.read_text())["alternatives"]
    canon = PS.canon_names()
    stems = {}
    for k, a in alts.items():
        nm, br = (a.get("name") or "").strip(), (a.get("brief") or "").strip()
        st = [w for w in nm.split() if w not in MODS]
        if not k.startswith("RSW_") or not nm or len(br) < 20 or len(st) != 1:
            fails.append(f"{k}: not spelled out ({nm!r}, {br!r})")
            continue
        ok, problems, _ = PS.check(st[0], canon)
        if not ok:
            fails.append(f"{k}: {st[0]} {problems}")
        stems.setdefault(st[0], []).append(k)
    for s, ks in stems.items():           # one stem per species; a shared stem only for a named variant (pale X, young X)
        if len(ks) > 1 and sum(1 for k in ks if alts[k]["name"].strip() == s) > 1:
            fails.append(f"stem {s} is the bare name of {ks}")
    if len(alts) < 100:
        fails.append(f"only {len(alts)} alternatives: the table did not load")
    # noncanon_option: real stand-in first, then the table, else None
    o = A.noncanon_option({"key": "RSW_Bantha", "noncanon_twin": ["RM_Ommok", "RSW_Other"]})
    if o != {"kind": "standin", "defs": ["RM_Ommok"]}:
        fails.append(f"stand-in case {o}")
    o = A.noncanon_option({"key": "RSW_Bantha", "noncanon_twin": []})
    if not o or o["kind"] != "drafted" or o["name"] != alts["RSW_Bantha"]["name"] or not o["brief"]:
        fails.append(f"drafted case {o}")
    if A.noncanon_option({"key": "RSW_NoSuchBeast"}) is not None:
        fails.append("unknown canon row got an option")
    if not re.search(r"data-act=\"ncset\"", open(A.__file__, encoding="utf-8").read()):
        fails.append("the sheet renders no ncset control")
    print("FAIL " + "; ".join(fails[:20]) if fails else f"PASS selftest_noncanon_alternatives ({len(alts)} alternatives)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
