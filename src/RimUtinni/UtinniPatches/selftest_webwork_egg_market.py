#!/usr/bin/env python3
"""Biome card 5 (owner, by card, 2026-10-22): the Hutt Cartel egg black market and the Wildsteam weaver caravan were
ported from the cut mandrake.rut.shokkweaveeconomy into this mod. Offline, XML only: applies the two ported patch
files to the real defs they touch and checks the result is what the original mod produced.

  * RM_OllathrixEgg (Webwork) goes tradeability All, loses ResourcesRaw (the leak fix), keeps RM_Contraband
  * RUT_Jawa_HuttCartel lists RUT_Caravan_HuttCartel_EggMarket beside its Captives kind
  * RUT_Jawa_WildsteamClan gets RUT_Caravan_Wildsteam_Weavers
  * the egg broker sells 1~3 eggs at Expensive, buys RM_Contraband, and both Cartel kinds carry the rare-thrixweave
    generator at 0.125 / 1~2; the Weavers carry Silver 400~1000 and the generator at 0.33 / 1~3 (the original numbers)
  * the generator class named in XML exists in Source/ under that namespace and is compiled by the csproj

Fails on purpose (checked below): with the composed biomes mod inactive the FindMod guard leaves the egg untouched,
and an egg without a tradeability element still ends at All (the nomatch branch)."""
import copy
import os
import re
import sys

from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", ".."))
EGG = os.path.join(SRC, "RimMandrake", "Webwork", "Defs", "ThingDefs_Items", "RM_OllathrixEgg.xml")
DEFS = [EGG,
        os.path.join(HERE, "Defs", "FactionDefs", "JawaHuttCartel.xml"),
        os.path.join(HERE, "Defs", "FactionDefs", "JawaWildsteamClan.xml"),
        os.path.join(HERE, "Defs", "TraderKindDefs", "RUT_HuttCartel_Captives.xml"),
        os.path.join(HERE, "Defs", "TraderKindDefs", "RUT_HuttCartel_EggMarket.xml"),
        os.path.join(HERE, "Defs", "TraderKindDefs", "RUT_Wildsteam_Caravan.xml")]
PATCHES = [os.path.join(HERE, "Patches", "RUT_Webwork_EggBlackMarket.xml"),
           os.path.join(HERE, "Patches", "RUT_Webwork_RareThrixweaveStock.xml")]
GEN_CLASS = "RimMandrake.Utinni.UtinniPatches.RUT_StockGenerator_RareThrixweave"


def load_defs():
    root = etree.Element("Defs")
    for p in DEFS:
        for el in etree.parse(p).getroot():
            if isinstance(el.tag, str):
                root.append(copy.deepcopy(el))
    return etree.ElementTree(root)


def _value_children(op):
    v = op.find("value")
    return [c for c in v if isinstance(c.tag, str)] if v is not None else []


def apply(op, doc, active_names):
    """A small interpreter for the PatchOperation classes the two ported files use. Returns success like vanilla."""
    cls = op.get("Class")
    xp = op.findtext("xpath")
    if xp and not xp.startswith("/"):
        xp = "/" + xp   # RimWorld evaluates a patch xpath from the document node
    if cls == "PatchOperationFindMod":
        names = [li.text for li in op.find("mods")]
        branch = op.find("match") if any(n in active_names for n in names) else op.find("nomatch")
        return True if branch is None else apply(branch, doc, active_names)
    if cls == "PatchOperationSequence":
        return all([apply(li, doc, active_names) for li in op.find("operations") if isinstance(li.tag, str)])
    if cls == "PatchOperationConditional":
        branch = op.find("match") if doc.xpath(xp) else op.find("nomatch")
        return True if branch is None else apply(branch, doc, active_names)
    nodes = doc.xpath(xp)
    if not nodes:
        return False
    for n in nodes:
        if cls == "PatchOperationAdd":
            for c in _value_children(op):
                n.append(copy.deepcopy(c))
        elif cls == "PatchOperationReplace":
            parent = n.getparent()
            i = parent.index(n)
            parent.remove(n)
            for k, c in enumerate(_value_children(op)):
                parent.insert(i + k, copy.deepcopy(c))
        elif cls == "PatchOperationRemove":
            n.getparent().remove(n)
        else:
            raise SystemExit("unhandled PatchOperation class %s" % cls)
    return True


def patched(doc, active_names=("RimMandrake: Baroque Biomes",)):
    bad = []
    for p in PATCHES:
        for op in etree.parse(p).getroot():
            if isinstance(op.tag, str) and op.tag == "Operation" and not apply(op, doc, set(active_names)):
                bad.append("%s: an operation matched nothing" % os.path.basename(p))
    return bad


def one(doc, xp):
    r = doc.xpath(xp)
    return r[0] if len(r) == 1 else None


def gens(doc, kind):
    return doc.xpath('/Defs/TraderKindDef[defName="%s"]/stockGenerators/li' % kind)


def rare(doc, kind):
    return [(g.findtext("chance"), g.findtext("countRange")) for g in gens(doc, kind) if g.get("Class") == GEN_CLASS]


def findings():
    out = []
    doc = load_defs()
    out += patched(doc)
    egg = '/Defs/ThingDef[defName="RM_OllathrixEgg"]'
    if [t.text for t in doc.xpath(egg + "/tradeability")] != ["All"]:
        out.append("egg tradeability is %r, not ['All']" % [t.text for t in doc.xpath(egg + "/tradeability")])
    if doc.xpath(egg + '/thingCategories/li[text()="ResourcesRaw"]'):
        out.append("egg still in ResourcesRaw: five ordinary traders could stock it")
    if "RM_Contraband" not in [t.text for t in doc.xpath(egg + "/tradeTags/li")]:
        out.append("egg lost its RM_Contraband trade tag (the broker's buy side names it)")
    hutt = [li.text for li in doc.xpath('/Defs/FactionDef[defName="RUT_Jawa_HuttCartel"]/caravanTraderKinds/li')]
    if not {"RUT_Caravan_HuttCartel_EggMarket", "RUT_Caravan_HuttCartel_Captives"} <= set(hutt):
        out.append("Hutt Cartel caravan kinds are %r" % hutt)
    wild = [li.text for li in doc.xpath('/Defs/FactionDef[defName="RUT_Jawa_WildsteamClan"]/caravanTraderKinds/li')]
    if wild != ["RUT_Caravan_Wildsteam_Weavers"]:
        out.append("Wildsteam caravan kinds are %r" % wild)
    sd = [(g.findtext("thingDef"), g.findtext("countRange"), g.findtext("price"))
          for g in gens(doc, "RUT_Caravan_HuttCartel_EggMarket") if g.get("Class") == "StockGenerator_SingleDef"]
    if sd != [("RM_OllathrixEgg", "1~3", "Expensive")]:
        out.append("egg broker sell side is %r" % sd)
    buy = [g.findtext("tag") for g in gens(doc, "RUT_Caravan_HuttCartel_EggMarket") if g.get("Class") == "StockGenerator_BuyTradeTag"]
    if buy != ["RM_Contraband"]:
        out.append("egg broker buy side is %r" % buy)
    for kind in ("RUT_Caravan_HuttCartel_EggMarket", "RUT_Caravan_HuttCartel_Captives"):
        if rare(doc, kind) != [("0.125", "1~2")]:
            out.append("%s rare thrixweave is %r, not [('0.125', '1~2')]" % (kind, rare(doc, kind)))
    if rare(doc, "RUT_Caravan_Wildsteam_Weavers") != [("0.33", "1~3")]:
        out.append("Weavers rare thrixweave is %r" % rare(doc, "RUT_Caravan_Wildsteam_Weavers"))
    silver = [(g.findtext("thingDef"), g.findtext("countRange")) for g in gens(doc, "RUT_Caravan_Wildsteam_Weavers")
              if g.get("Class") == "StockGenerator_SingleDef"]
    if silver != [("Silver", "400~1000")]:
        out.append("Weavers silver is %r" % silver)
    for k, (c, l) in {"RUT_Caravan_HuttCartel_EggMarket": ("0.15", "Hutt Cartel egg broker"),
                      "RUT_Caravan_Wildsteam_Weavers": ("0.5", "Wildsteam weave-runners")}.items():
        d = one(doc, '/Defs/TraderKindDef[defName="%s"]' % k)
        if d is None or d.findtext("commonality") != c or d.findtext("label") != l or d.findtext("orbital") != "false":
            out.append("%s commonality/label/orbital drifted" % k)
    ns, cls = GEN_CLASS.rsplit(".", 1)
    cs = open(os.path.join(HERE, "Source", cls + ".cs"), encoding="utf-8").read()
    if "namespace " + ns not in cs or not re.search(r"public class %s : StockGenerator\b" % cls, cs):
        out.append("%s is not a StockGenerator in namespace %s" % (cls, ns))
    if not re.search(r"Stocks\(float chance, float roll\)\s*\{\s*return roll < chance;", cs):
        out.append("the stock roll is no longer 'roll < chance' (the original skipped when Rand.Value >= chance)")
    proj = open(os.path.join(HERE, "Source", "RimMandrake.Utinni.UtinniPatches.csproj"), encoding="utf-8").read()
    if 'Compile Include="%s.cs"' % cls not in proj:
        out.append("%s.cs is not compiled by the csproj" % cls)

    # The checks can fail: with the composed biomes mod absent the guard must leave the egg Sellable.
    off = load_defs()
    patched(off, active_names=())
    if [t.text for t in off.xpath(egg + "/tradeability")] != ["Sellable"]:
        out.append("FindMod guard did not hold the egg patch back with the biomes mod inactive")
    # ...and an egg with no tradeability element still ends at All (the Conditional's nomatch Add).
    bare = load_defs()
    for t in bare.xpath(egg + "/tradeability"):
        t.getparent().remove(t)
    patched(bare)
    if [t.text for t in bare.xpath(egg + "/tradeability")] != ["All"]:
        out.append("an egg without a tradeability element does not end at All")
    return out


if __name__ == "__main__":
    bad = findings()
    for b in bad:
        print("FAIL " + b)
    print("selftest_webwork_egg_market: %s" % ("PASS" if not bad else "FAIL (%d)" % len(bad)))
    sys.exit(1 if bad else 0)
