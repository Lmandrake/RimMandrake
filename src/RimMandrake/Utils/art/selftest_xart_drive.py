#!/usr/bin/env python3
"""selftest_xart_drive.py — the def edits xart_drive.py writes (pure text, no repo state).

A wired look must be read by the game the way the commission means it: a variant as the kind's one alternateGraphic,
a female look as the adult stage's femaleGraphicData (a full GraphicData copied from the body), a young look on the baby
and juvenile stages only (the adult untouched, no female adult picture left on a young stage), a facing set as
Graphic_Multi on the bodies that draw that texPath. Every edit must leave the XML parseable and the other kinds alone.
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import xart_drive as X  # noqa: E402

FAILS = []


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:300]}]"))
    if not cond:
        FAILS.append(msg)


DOC = """<?xml version="1.0" encoding="utf-8"?>
<Defs>
  <!-- a comment that must survive -->
  <PawnKindDef ParentName="AnimalKindBase">
    <defName>RM_Foo</defName>
    <race>RM_Foo</race>
    <lifeStages>
      <li>
        <bodyGraphicData>
          <texPath>Things/Pawn/Animal/RM_Foo/RM_Foo</texPath>
          <graphicClass>Graphic_Multi</graphicClass>
          <drawSize>1.1</drawSize>
        </bodyGraphicData>
        <femaleGraphicData>
          <texPath>Things/Pawn/Animal/RM_Foo/RM_FooFemale</texPath>
          <graphicClass>Graphic_Multi</graphicClass>
          <drawSize>1.1</drawSize>
        </femaleGraphicData>
        <dessicatedBodyGraphicData><texPath>Things/Pawn/Animal/Dessicated/X</texPath></dessicatedBodyGraphicData>
      </li>
      <li>
        <bodyGraphicData>
          <texPath>Things/Pawn/Animal/RM_Foo/RM_Foo</texPath>
          <graphicClass>Graphic_Multi</graphicClass>
          <drawSize>1.6</drawSize>
        </bodyGraphicData>
      </li>
      <li>
        <bodyGraphicData>
          <texPath>Things/Pawn/Animal/RM_Foo/RM_Foo</texPath>
          <graphicClass>Graphic_Multi</graphicClass>
          <drawSize>2.2</drawSize>
          <shadowData><volume>(0.3, 0.3, 0.3)</volume></shadowData>
        </bodyGraphicData>
      </li>
    </lifeStages>
  </PawnKindDef>
  <PawnKindDef ParentName="AnimalKindBase">
    <defName>RM_Bar</defName>
    <race>RM_Bar</race>
    <alternateGraphicChance>0.5</alternateGraphicChance>
    <alternateGraphics>
      <li><texPath>Things/Pawn/Animal/RM_Bar/RM_BarOld</texPath></li>
    </alternateGraphics>
    <lifeStages>
      <li><bodyGraphicData><texPath>Things/Pawn/Animal/RM_Bar/RM_Bar</texPath><graphicClass>Graphic_Single</graphicClass></bodyGraphicData></li>
    </lifeStages>
  </PawnKindDef>
</Defs>
"""


def kind(text, dn):
    for d in ET.fromstring(text.split("?>", 1)[1]):
        if d.findtext("defName") == dn:
            return d
    raise KeyError(dn)


def bodies(d):
    return [li.find("bodyGraphicData") for li in d.find("lifeStages")]


def main() -> int:
    v = X.wire_variant(DOC, "RM_Foo", "T/RM_FooVariant")
    k = kind(v, "RM_Foo")
    alts = [li.findtext("texPath") for li in k.find("alternateGraphics")]
    check(alts == ["T/RM_FooVariant"] and k.findtext("alternateGraphicChance") == X.VARIANT_CHANCE,
          "variant: the kind gets one alternateGraphic and a chance", alts)
    check(kind(v, "RM_Bar").findtext("alternateGraphicChance") == "0.5", "variant: another kind is untouched")
    check("a comment that must survive" in v, "variant: comments survive")
    check(X.wire_variant(v, "RM_Foo", "T/RM_FooVariant") == v, "variant: wiring twice changes nothing")
    v2 = X.wire_variant(DOC, "RM_Bar", "T/RM_BarVariant")
    check([li.findtext("texPath") for li in kind(v2, "RM_Bar").find("alternateGraphics")]
          == ["Things/Pawn/Animal/RM_Bar/RM_BarOld", "T/RM_BarVariant"] and
          kind(v2, "RM_Bar").findtext("alternateGraphicChance") == "0.5",
          "variant: an existing list gains the look, its chance kept")

    y = X.wire_young(DOC, "RM_Foo", "T/RM_FooYoung")
    b = bodies(kind(y, "RM_Foo"))
    check([g.findtext("texPath") for g in b] == ["T/RM_FooYoung", "T/RM_FooYoung", "Things/Pawn/Animal/RM_Foo/RM_Foo"],
          "young: baby and juvenile draw the young look, the adult stays", [g.findtext("texPath") for g in b])
    check([g.findtext("drawSize") for g in b] == ["1.1", "1.6", "2.2"], "young: each stage keeps its own drawSize")
    ls = kind(y, "RM_Foo").find("lifeStages")
    check(ls[0].find("femaleGraphicData") is None, "young: no female adult picture is left on a young stage")
    check(ls[0].find("dessicatedBodyGraphicData") is not None, "young: the dessicated graphic stays")
    try:
        X.wire_young(DOC, "RM_Bar", "T/X")
        check(False, "young: a one-stage kind is refused")
    except ValueError:
        check(True, "young: a one-stage kind is refused")

    f = X.wire_female(DOC, "RM_Foo", "T/RM_FooFemaleNew")
    ad = kind(f, "RM_Foo").find("lifeStages")[-1]
    fg = ad.find("femaleGraphicData")
    check(fg is not None and fg.findtext("texPath") == "T/RM_FooFemaleNew" and fg.findtext("graphicClass") == "Graphic_Multi"
          and fg.findtext("drawSize") == "2.2" and fg.find("shadowData") is not None,
          "female: the adult stage gets a full femaleGraphicData copied from its body", ET.tostring(ad)[:300])
    check(ad.find("bodyGraphicData").findtext("texPath") == "Things/Pawn/Animal/RM_Foo/RM_Foo", "female: the body stays")
    f2 = X.wire_female(f, "RM_Foo", "T/RM_FooFemaleNewer")
    check(kind(f2, "RM_Foo").find("lifeStages")[-1].find("femaleGraphicData").findtext("texPath") == "T/RM_FooFemaleNewer"
          and f2.count("<femaleGraphicData>") == f.count("<femaleGraphicData>"),
          "female: an existing femaleGraphicData is repointed, not doubled")

    m = X.wire_multi(DOC, "RM_Bar", "Things/Pawn/Animal/RM_Bar/RM_Bar")
    check(bodies(kind(m, "RM_Bar"))[0].findtext("graphicClass") == "Graphic_Multi", "faces: the body turns Graphic_Multi")
    check(X.wire_multi(DOC, "RM_Bar", "Things/Other") == DOC, "faces: a body drawing another texPath is untouched")
    print(f"{'OK' if not FAILS else 'FAILED'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
