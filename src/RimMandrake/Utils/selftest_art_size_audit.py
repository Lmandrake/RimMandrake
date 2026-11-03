#!/usr/bin/env python3
"""selftest_art_size_audit.py -- offline checks of art_size_audit.py's judging rules on fixtures,
plus the owner-order readers on the repo's real sheets. No load set, no game; a few seconds."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import art_size_audit as A  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  " + str(detail)))
    if not cond:
        FAILS.append(name)


def plant(dn, cells, tree=False, ours=True, **kw):
    r = {"defName": dn, "package": "mandrake.rm.x" if ours else "ludeon.rimworld", "ours": ours,
         "label": kw.pop("label", dn.lower()), "description": kw.pop("description", ""),
         "kind": "plant", "drawSize": [1.0], "visualSizeRange": [cells * 0.7, cells], "tree": tree,
         "cells": cells, "texPath": kw.pop("texPath", "Things/Plant/" + dn), "texWhere": "own",
         "graphicClass": "Graphic_Single"}
    r.update(kw)
    return r


def animal(dn, body, cells, ours=True, **kw):
    r = {"defName": dn, "package": "mandrake.rm.x" if ours else "ludeon.rimworld", "ours": ours,
         "label": kw.pop("label", dn.lower()), "description": kw.pop("description", ""),
         "kind": "animal", "body": body, "kindDef": dn, "drawSize": [cells], "cells": cells,
         "texPath": kw.pop("texPath", "Things/Pawn/Animal/" + dn), "texWhere": "own",
         "graphicClass": "Graphic_Multi"}
    r.update(kw)
    return r


def fixture():
    ref = [animal("V%d" % i, b, 1.9 * b ** 0.42 * f, ours=False, texPath="Things/Pawn/Animal/V%d" % i)
           for i, (b, f) in enumerate([(0.2, 1.0), (0.5, 1.1), (1.0, 0.9), (2.0, 1.0), (4.0, 1.05),
                                       (0.3, 0.95), (3.0, 1.0), (1.5, 1.1)])]
    ref += [plant("VTree%d" % i, c, tree=True, ours=False) for i, c in enumerate((1.5, 2.0, 3.0))]
    ref += [plant("VPlant%d" % i, c, ours=False) for i, c in enumerate((0.4, 1.0, 2.2))]
    ours = [
        plant("RM_TierOk", 10.0, tree=True),
        plant("RM_TierSmall", 4.0, tree=True),                       # tiered giant, drawn 4
        plant("RM_Ordered", 3.0),                                    # owner: 7 cells
        plant("RM_OrderedOk", 6.8),                                  # owner: 7 cells, within 1.25x
        plant("RM_Titch", 0.1),                                      # under every vanilla plant
        animal("RM_Normal", 1.0, 1.9, texPath="Things/Pawn/Animal/RM_Normal", texWhere="own"),
        animal("RM_Tiny", 1.0, 0.5),                                 # x0.26 of the fit
        animal("RM_Vanillart", 1.0, 1.9, texPath="Things/Pawn/Animal/V2", texWhere=None),
        animal("RM_Lost", 1.0, 1.9, texPath="Things/Pawn/Animal/Nowhere", texWhere=None),
        animal("RM_Bigword", 1.0, 1.9, description="A towering beast, nine metres tall."),
        animal("RM_Padded", 1.0, 1.9, fill=[0.4, 0.3]),
        animal("RM_Waived", 1.0, 1.9, texPath="Things/Pawn/Animal/Gone", texWhere=None),
        animal("RM_BlankWaiver", 1.0, 1.9, texPath="Things/Pawn/Animal/Gone2", texWhere=None),
        plant("RM_NoTex", 1.0, texPath=None),
        animal("RM_NoTexAnimal", 1.0, 1.9, texPath=None),
        animal("RM_ZeroSize", 1.0, 0.0),
        animal("RM_ItemArt", 1.0, 1.9, texPath="Things/Item/Vanilla", texWhere=None),
    ]
    return ref + ours


def flags(rows, dn):
    return [(f[0], f[1]) for r in rows if r["defName"] == dn for f in r["flags"]]


def main():
    rows = fixture()
    st = {"patchOps": 1, "vanillaTex": ["Things/Item/Vanilla"]}
    orders = {"AB_Ordered": [{"cells": 7.0, "note": "7 cells", "at": "2026-09-11T00:00", "file": "x"}],
              "RM_OrderedOk": [{"cells": 7.0, "note": "7 cells", "at": "2026-09-11T00:00", "file": "x"}]}
    tiers = {"RM_TierOk": "giant", "RM_TierSmall": "giant"}
    waivers = {"RM_Waived": {"NO_SPRITE": "fixture"}, "RM_BlankWaiver": {"NO_SPRITE": "  "}}
    rows, st = A.finish(rows, st, tiers=tiers, orders=orders, waivers=waivers)
    fit = st["fit"]
    check("vanilla fit recovers the fixture's exponent", abs(fit["b"] - 0.42) < 0.06, fit)
    check("tier inside: no flag", not [f for f in flags(rows, "RM_TierOk") if f[0] == "HIGH"])
    check("tier outside: HIGH TREE_TIER", ("HIGH", "TREE_TIER") in flags(rows, "RM_TierSmall"))
    check("donor-stem order matched and off: HIGH OWNER_ORDER",
          ("HIGH", "OWNER_ORDER") in flags(rows, "RM_Ordered"), flags(rows, "RM_Ordered"))
    check("order within 1.25x: INFO ORDER_MATCHED", ("INFO", "ORDER_MATCHED") in flags(rows, "RM_OrderedOk"))
    check("below the vanilla plant floor: MEDIUM PLANT_ENVELOPE",
          ("MEDIUM", "PLANT_ENVELOPE") in flags(rows, "RM_Titch"))
    check("on the vanilla curve: no animal flag", not flags(rows, "RM_Normal"), flags(rows, "RM_Normal"))
    check("far under the curve: REVIEW, never a gate", ("REVIEW", "ANIMAL_ENVELOPE") in flags(rows, "RM_Tiny"))
    check("vanilla texPath: MEDIUM VANILLA_TEXTURE, not NO_SPRITE",
          flags(rows, "RM_Vanillart") == [("MEDIUM", "VANILLA_TEXTURE")], flags(rows, "RM_Vanillart"))
    check("unresolvable texPath: HIGH NO_SPRITE", ("HIGH", "NO_SPRITE") in flags(rows, "RM_Lost"))
    check("fiction: 'nine metres tall' drawn 1.9 cells is flagged",
          ("MEDIUM", "FICTION") in flags(rows, "RM_Bigword"), flags(rows, "RM_Bigword"))
    check("padded sprite flagged", ("MEDIUM", "SPRITE_PADDED") in flags(rows, "RM_Padded"))
    check("waiver turns HIGH into WAIVED", flags(rows, "RM_Waived") == [("WAIVED", "NO_SPRITE")],
          flags(rows, "RM_Waived"))
    check("blank waiver reason waives nothing", ("HIGH", "NO_SPRITE") in flags(rows, "RM_BlankWaiver"))
    check("plant with no texPath: HIGH NO_SPRITE", ("HIGH", "NO_SPRITE") in flags(rows, "RM_NoTex"))
    check("vanilla item art (index from every vanilla def): VANILLA_TEXTURE",
          flags(rows, "RM_ItemArt") == [("MEDIUM", "VANILLA_TEXTURE")], flags(rows, "RM_ItemArt"))
    check("animal with no texPath: HIGH NO_SPRITE", ("HIGH", "NO_SPRITE") in flags(rows, "RM_NoTexAnimal"))
    check("zero drawn size: HIGH BAD_SIZE, no crash", flags(rows, "RM_ZeroSize") == [("HIGH", "BAD_SIZE")],
          flags(rows, "RM_ZeroSize"))
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "Things", "Dir"))
        open(os.path.join(td, "Things", "Dir", "a.png"), "wb").close()
        open(os.path.join(td, "Things", "Multi_south.png"), "wb").close()
        check("Graphic_Single never resolves a directory or a facing suffix",
              A._candidates(td, "Things/Dir", "Graphic_Single", "east") == [] and
              A._candidates(td, "Things/Multi", "Graphic_Single", "east") == [])
        check("Graphic_Random resolves a directory; Graphic_Multi a facing",
              len(A._candidates(td, "Things/Dir", "Graphic_Random", "east")) == 1 and
              len(A._candidates(td, "Things/Multi", "Graphic_Multi", "east")) == 1)
    bad = A.check(rows, st)
    check("check() gates exactly the unwaived HIGHs (plus the blind-scan floors)",
          sorted(b.split()[0] for b in bad if not b.startswith("instrument")) ==
          ["RM_BlankWaiver", "RM_Lost", "RM_NoTex", "RM_NoTexAnimal", "RM_Ordered", "RM_TierSmall",
           "RM_ZeroSize"], bad)
    check("check() refuses a blind scan", any(b.startswith("instrument blind") for b in bad))
    st2 = dict(st, missing=["some.mod"], xpathErrors=2,
               unsupportedSizeOps=[["f.xml", "PatchOperationMath", "Defs/ThingDef/graphicData/drawSize"]])
    bad2 = " | ".join(A.check(rows, st2))
    check("check() refuses an incomplete load set, xpath errors and unrunnable size patches",
          "incomplete load set" in bad2 and "xpath error" in bad2 and "cannot apply" in bad2, bad2)
    md = A.md_report(rows, st)
    check("report lists every HIGH row", all(("`%s`" % d) in md for d in ("RM_Lost", "RM_Ordered", "RM_TierSmall")))

    # owner-note parsing
    oc = A.order_cells
    check("parse '10 cells wide'", oc("10 cells wide") == 10.0)
    check("parse 'half a cell'", oc("This should only be half a cell") == 0.5)
    check("parse '.8 cells'", oc(".8 cells, propane lakes") == 0.8)
    check("parse 'three cells wide'", oc("make it three cells wide") == 3.0)
    check("parse 'Size 12.'", oc("glowing mushrooms. Size 12.") == 12.0)
    check("bare number only on a resize row", oc("6 still", "resize") == 6.0 and oc("6 still") is None)
    check("no number, no order", oc("map cells are fine") is None)

    # sheet reader: an unsaved row's prefill note is agent text; an `ok` restating a number confirms it
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "s.decisions.json")
        json.dump({"frozen_at": "2026-09-19", "decisions": {
            "AB_Saved": {"at": "2026-09-19T16:00:00Z", "decision": "resize", "note": "2"},
            "AB_Prefill": {"decision": "", "note": "you judged this against a false number"},
            "AB_Ok": {"decision": "ok", "note": "the current number (7 cells) IS your own ruling from x"},
            "flora:b:AB_Bin": {"at": "2026-09-10T00:00:00Z", "sizeBin": "small", "sizeBinPrefill": "medium",
                               "note": ""}}}, open(p, "w"))
        o = A.owner_orders([p])
        check("saved resize row read", [x["cells"] for x in o.get("AB_Saved", [])] == [2.0], o)
        check("unsaved prefill note ignored", "AB_Prefill" not in o, o)
        check("ok row confirms its restated number", [x["cells"] for x in o.get("AB_Ok", [])] == [7.0], o)
        check("bin rescale read, sheet key stripped to its defName",
              [x.get("bin") for x in o.get("AB_Bin", [])] == ["small"], o)
        t = os.path.join(td, "t.md")
        open(t, "w").write("| # | defName | ruled width (cells) | current |\n|---|---|---|---|\n"
                           "| 1 | `AB_X` | 7 | 2 |\n| 2 | `AB_Y` | — | 1 |\n\nprose\n")
        to = A.table_orders([(t, "ruled width (cells)", "2026-09-19T12:00:00")])
        check("rulings table read, dashes skipped", list(to) == ["AB_X"] and to["AB_X"][0]["cells"] == 7.0, to)

    check("stem matches donor to port", A.stem("AB_GiantAgarilux") == A.stem("RM_GiantAgarilux"))
    check("stem matches wild canon plant", A.stem("Plant_HydenockTree_Wild") == A.stem("RSW_Plant_HydenockTree_Wild"))

    # the real sheets: the readers see the owner's orders that motivated the item
    real = A.owner_orders()
    check("real sheets: Hydenock's '6 cells wide' is read", any(x.get("cells") == 6.0 for x in
                                                               real.get("Plant_HydenockTree_Wild", [])))
    check("real sheets: dozens of orders, not zero", len(real) >= 40, len(real))
    tt = A.tree_tiers()
    check("real tree tiers: hydenock giant, jogan big",
          tt.get("RSW_Plant_HydenockTree_Wild") == "giant" and tt.get("RSW_Plant_JoganTree_Wild") == "big", tt)
    w = json.load(open(A.WAIVERS))
    check("every waiver carries a reason", all(isinstance(v, dict) and all(isinstance(x, str) and x for x in v.values())
                                               for k, v in w.items() if not k.startswith("_")))
    print("RESULT: %s (%d fail)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
