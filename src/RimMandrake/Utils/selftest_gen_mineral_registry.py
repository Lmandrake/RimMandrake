#!/usr/bin/env python3
"""Selftest for gen_mineral_registry.py (MINERALS_WHERE_THEY_BELONG_1 wave R1).

Fixture checks: the bindings grammar and its errors, deep homes, the deep table (no Steel,
CSV column order, retire defs listed with no homes, first binding wins), the registry XML
(well-formed, MayRequire only on non-Core defs, unresolved groups not emitted), the
vanilla-biomes-plus-deep hard error. Real-data checks: the committed CSV analyses with no
hard defect from repo XML alone (no def dump needed), and the committed
src/RimMandrake/DeepDrill/Defs/RM_DeepHomeTable.xml is byte-equal to what --write-deep
would write now (a hand edit or a CSV change without regeneration FAILS here).
Each check has a planted-break probe so a vacuous pass cannot hide.

    python3 selftest_gen_mineral_registry.py
"""
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_mineral_registry as g  # noqa: E402

FAILS = []


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class FakeIndex:
    def __init__(self, known, dump=None):
        self.known, self.dump, self.fingerprint, self.src = known, dump or {}, "fixture", {}

    def resolve(self, name):
        return self.known.get(name)


def row(material, bindings, deep="0", other="0", status="RULED x", **biomes):
    r = {"material": material, "bindings": bindings, "deep_weight": deep, "OTHER_vanilla_biomes": other,
         "status": status, "form": "F1", "unit": "EPM", "units_per_cell_or_find": "40",
         "salvage_per_year": "", "trade_per_year": "", "quarry": "local", "quarry_per_100_jobs": ""}
    r.update({"RM_A": "0", "RM_B": "0", "RUT_C": "0"})
    r.update(biomes)
    return r


def test_grammar():
    gs, errs = g.parse_bindings("Gold", "item:Gold mineable:MineableGold")
    ok(not errs and gs[0]["id"] == "gold" and gs[0]["item"] == ["Gold"], "single group gets slug id")
    gs, errs = g.parse_bindings("x", "id:a item:A | id:b item:B")
    ok(not errs and [x["id"] for x in gs] == ["a", "b"], "split row with ids parses")
    _, errs = g.parse_bindings("x", "item:A | item:B")
    ok(any("needs an id" in e for e in errs), "split row without ids is an error")
    _, errs = g.parse_bindings("x", "itme:A")
    ok(any("bad binding token" in e for e in errs), "unknown role is an error")
    _, errs = g.parse_bindings("x", "item:Bad-Name")
    ok(any("bad binding token" in e for e in errs), "non-defName is an error")
    _, errs = g.parse_bindings("x", "id:a")
    ok(any("empty binding group" in e for e in errs), "id-only group is an error")
    gs, errs = g.parse_bindings("x", "  ")
    ok(gs == [] and errs == [], "empty cell binds nothing")


def test_deep():
    r = row("Gold", "item:Gold", deep="0.5", RM_B="40", RUT_C="deep-only", RM_A="0")
    ok(g.deep_homes(r) == ["RM_B", "RUT_C"], "homes = >0 or deep-only, column order")
    ok(g.deep_homes(row("x", "item:X", deep="0", RM_A="9")) == [], "deep_weight 0 -> no homes")
    rows = [row("steel", "item:Steel", deep="4", other="12000", RM_A="5"),
            r,
            row("beskar", "item:KOTOR_RawBeskar retire:OuterRim_Beskar"),
            row("dup", "id:dup item:Gold", deep="1", RM_A="5")]
    txt = g.emit_deep_table(rows)
    root = ET.fromstring(txt.split("?>", 1)[1])
    things = [(li.findtext("thing"), [h.text for h in li.find("homes")]) for li in root.iter("li") if li.find("thing") is not None]
    ok("Steel" not in [t for t, _ in things], "Steel never listed")
    ok(("Gold", ["RM_B", "RUT_C"]) in things and [t for t, _ in things].count("Gold") == 1, "first binding of Gold wins")
    ok(("OuterRim_Beskar", []) in things and ("KOTOR_RawBeskar", []) in things, "retire and no-deep items listed homeless")
    # planted break: a Steel row that is not first must still be dropped
    txt2 = g.emit_deep_table([row("Gold", "item:Gold item:Steel", deep="1", RM_A="1")])
    ok("<thing>Steel</thing>" not in txt2, "Steel dropped even inside another group (probe)")
    # planted break: '--' in a material name must not reach an XML comment (illegal XML)
    txt3 = g.emit_deep_table([row("a--b-", "item:X")])
    try:
        ET.fromstring(txt3.split("?>", 1)[1])
        ok(True, "'--' in a material name still yields well-formed XML (probe)")
    except ET.ParseError as e:
        ok(False, "'--' in a material name still yields well-formed XML (probe): %s" % e)


def test_analyse_and_registry():
    known = {"Gold": "ludeon.rimworld", "MineableGold": "ludeon.rimworld", "DV_Pyrinth": "mandrake.rm.pyrinth"}
    rows = [row("Gold", "item:Gold mineable:MineableGold", deep="0.5", RM_B="40"),
            row("pyrinth", "item:DV_Pyrinth", status="BUILT gate"),
            row("ghost", "item:Nope_Missing"),
            row("unruled", "item:Gold2", status="PROPOSED")]
    a = g.analyse(rows, FakeIndex(known))
    ok(a["hard"] == [], "fixture analyses with no hard defect: %s" % a["hard"])
    ok([x[1]["id"] for x in a["emit"]] == ["gold", "pyrinth"], "only resolved RULED/BUILT groups emit")
    ok(any("Nope_Missing" in s for s in a["soft"]), "unresolved def is a soft finding")
    xml = g.emit_registry(a["emit"], FakeIndex(known))
    root = ET.fromstring(xml.split("?>", 1)[1])
    defs = root.findall("RimMandrake.Minerals.RM_MineralRegistryDef")
    ok(len(defs) == 2 and defs[0].findtext("defName") == "RM_Mineral_Gold", "registry XML well-formed, 2 defs")
    lis = {li.text: li.get("MayRequire") for d in defs for li in d.iter("li") if li.text}
    ok(lis.get("Gold") is None and lis.get("DV_Pyrinth") == "mandrake.rm.pyrinth", "MayRequire only off-Core")
    ok(defs[0].find("biomes/li/biome").text == "RM_B", "zero biome cells omitted, non-zero kept")
    # a RUT_ biome with no cell reads its RM_ twin (kernel RegistryValue): an explicit 0 there must survive emission
    twin = dict(row("Gold", "item:Gold", RM_B="40"), RUT_B="0", RUT_C="0.0")
    tx = ET.fromstring(g.emit_registry([(twin, g.parse_bindings("Gold", "item:Gold")[0][0])], FakeIndex(known)).split("?>", 1)[1])
    cells = {li.findtext("biome"): li.findtext("value") for li in tx.iter("li") if li.find("biome") is not None}
    ok(cells.get("RUT_B") == "0", "explicit 0 in a RUT_ column with an RM_ twin is emitted (else the twin's 40 leaks in): %s" % cells)
    ok("RUT_C" not in cells and "RM_A" not in cells, "zeros with no twin column stay omitted (0.0 included): %s" % cells)
    bad = g.analyse([row("x", "item:Gold", deep="1", other="5")], FakeIndex(known))
    ok(any("OTHER_vanilla_biomes" in h for h in bad["hard"]), "vanilla biomes + deep weight is hard")
    twice = g.analyse([row("a", "item:Gold"), row("b", "item:Gold")], FakeIndex(known))
    ok(any("bound twice" in h for h in twice["hard"]), "a def bound by two rows is hard")
    a2 = g.analyse(rows, FakeIndex(known, dump={"MineableX": {"pkg": "p", "mineableThing": "XOre", "deep": 0,
                                                             "resourceRock": True}}))
    ok(any("MineableX" in u for u in a2["uncovered"]), "coverage sees an unbound resource mineable (probe)")


def test_real_csv():
    rows = g.load()
    ok(len(rows) >= 40, "real CSV has rows (%d)" % len(rows))
    a = g.analyse(rows, g.DefIndex(dump=None))
    ok(a["hard"] == [], "real CSV: no hard defect from repo XML alone %s" % a["hard"][:3])
    ok(len(a["groups"]) >= len([r for r in rows if r["bindings"].strip()]), "every bound row yields a group")
    committed = open(g.DEEP_TABLE, encoding="utf-8").read()
    ok(committed == g.emit_deep_table(rows),
       "committed RM_DeepHomeTable.xml == --write-deep output (regenerate after a CSV change)")
    for must in ("Gold", "Jade", "RM_Lanternstone", "RM_LivePatternMetal"):
        ok(f"<thing>{must}</thing>" in committed, f"deep table lists {must}")


def main():
    test_grammar()
    test_deep()
    test_analyse_and_registry()
    test_real_csv()
    print(("FAIL %d" % len(FAILS)) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
