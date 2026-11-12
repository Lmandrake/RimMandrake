#!/usr/bin/env python3
"""Offline: validation.sea_catch_alive_checks() is green on the shipped defs and goes red when a sea loses a
floor body, a catch breaks the RM_<X>Catch pairing, or a body is wired but never defined.

    python3 src/RimMandrake/TerminalBiomes/selftest_sea_catch_alive.py
"""
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
import validation as V  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def mutated(rel, old, new):
    tmp = tempfile.mkdtemp(prefix="seacatch_")
    dst = os.path.join(tmp, "Defs")
    shutil.copytree(os.path.join(HERE, "Defs"), dst)
    p = os.path.join(dst, rel)
    s = open(p, encoding="utf-8").read()
    assert old in s, (rel, old)
    open(p, "w", encoding="utf-8").write(s.replace(old, new, 1))
    return tmp, dst


shipped = V.sea_catch_alive_checks()
check("shipped: every catch in the four seas has a living floor body", not shipped, str(shipped[:5]))
for label, rel, old, new in [
    ("twilight niim body unwired", "BiomeDefs/RM_TwilightSea.xml", "<RM_Niim>1.0</RM_Niim>", ""),
    ("grey body unwired", "BiomeDefs/RM_GreySea.xml", "<RM_Nissik>0.9</RM_Nissik>", ""),
    ("catch breaks pairing", "BiomeDefs/RM_TwilightSea.xml", "<RM_KelluCatch>1</RM_KelluCatch>", "<RM_Kellu_Item>1</RM_Kellu_Item>"),
    ("body wired but undefined", "ThingDefs_Races/RM_TwilightSeaFloorLife.xml", "<defName>RM_Liiru</defName>\n    <label>", "<defName>RM_LiiruGone</defName>\n    <label>"),
]:
    tmp, dst = mutated(rel, old, new)
    try:
        bad = V.sea_catch_alive_checks(dst)
    finally:
        shutil.rmtree(tmp)
    check("mutant %-26s goes red" % label, bool(bad), "")
desc = V.sea_description_checks()
check("shipped: every sea's description names its floor and its catch", not desc, str(desc[:5]))
for label, rel, old, new in [
    ("scald floor sentence cut", "BiomeDefs/RM_TheScald.xml", " On its floor, where only a gravship", " Where only a"),
    ("chill shore cut", "BiomeDefs/RM_TheChill.xml", "a line dropped from the crust's edge", "a line dropped"),
    ("grey names no catch", "BiomeDefs/RM_GreySea.xml", "nissik, grusk and essarn graze the salt beds under the slow shadow of reefbacks; its shore yields essarn, nissik, thollim and grusk", "reefbacks pass; its shore yields salt"),
]:
    tmp, dst = mutated(rel, old, new)
    try:
        bad = V.sea_description_checks(dst)
    finally:
        shutil.rmtree(tmp)
    check("mutant %-26s goes red" % label, bool(bad), "")
ref = V.chill_refinery_checks()
check("shipped: every hydrocarbon Chill catch has a refinery bill", not ref, str(ref[:5]))
tmp, dst = mutated("RecipeDefs/RM_TheChillFuelChain.xml", "        <li>RM_ZhiilCatch</li>\n      </thingDefs>\n    </fixedIngredientFilter>", "      </thingDefs>\n    </fixedIngredientFilter>")
try:
    check("mutant %-26s goes red" % "zhiil dropped from the bill", bool(V.chill_refinery_checks(dst)), "")
finally:
    shutil.rmtree(tmp)
print("\n%s" % ("ALL OK" if not FAILS else "FAILED: %s" % FAILS))
sys.exit(1 if FAILS else 0)
