#!/usr/bin/env python3
"""LONGSHADE_BEDAZZLE_MECHANICS_1 ash act (ash pulse + sand-lock): the shipped wiring passes ash_act_problems and
each planted defect is caught by name."""
import os, sys
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as v

FAILS = []
def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else "  " + detail))
    if not ok:
        FAILS.append(name)

XML = open(os.path.join(HERE, "Defs", "IncidentDefs", "RM_SmokeHaze.xml"), encoding="utf-8").read()
CB = os.path.join(HERE, "..", "CreatureBehaviors", "Source")
def cb(n):
    return open(os.path.join(CB, n), encoding="utf-8").read()

check("ash act: shipped defs and wiring pass", v.ash_act_problems() == [], str(v.ash_act_problems()))
def planted(xml_from, xml_to=None, src=None):
    root = ET.fromstring(XML.replace(xml_from, xml_to)) if xml_to is not None else None
    return v.ash_act_problems(root, src)
check("planted: a growth factor below 1 fails",
      any("not a surge" in x for x in planted("<growthRateFactor>1.5", "<growthRateFactor>0.8")))
check("planted: the haze reverting to a plain GameCondition fails",
      any("no longer chains" in x for x in planted(
          "<conditionClass>RimMandrake.LongShade.RM_GameCondition_SmokeHaze", "<conditionClass>GameCondition")))
check("planted: a sand-lock without its extension fails",
      any("sand never locks" in x for x in planted('<li Class="RimMandrake.CreatureBehaviors.RM_SandLockExtension" />', "")))
check("planted: swim test that ignores the lock fails",
      any("swimmers ignore it" in x for x in v.ash_act_problems(None, {
          "RM_CompSandSwim.cs": cb("RM_CompSandSwim.cs").replace("RM_ConditionGround.SandLocked(c, map)", "false")})))
check("planted: AshPulse.cs dropped from the csproj fails",
      any("compiles into nothing" in x for x in v.ash_act_problems(None, {
          "RM_CreatureBehaviors.csproj": cb("RM_CreatureBehaviors.csproj").replace('<Compile Include="RM_AshPulse.cs" />', "")})))
check("planted: growth patch removed fails",
      any("Plant.get_GrowthRate" in x for x in v.ash_act_problems(None, {
          "RM_AshPulse.cs": cb("RM_AshPulse.cs").replace("nameof(Plant.GrowthRate)", "nameof(Plant.Growth)")})))
SAR = open(os.path.join(HERE, "..", "..", "RimStarWars", "Sarlacc", "Source", "RSW_SwimmerRoad.cs"), encoding="utf-8").read()
def sp(a, b):
    return v.ash_act_problems(None, {"RSW_SwimmerRoad.cs": SAR.replace(a, b)})
check("planted: halt that ignores the lock test fails",
      any("halt missing" in x for x in sp("RM_ConditionGround.SandLocked(pawn.Position, pawn.Map)", "false")))
check("planted: job giver no longer halting fails",
      any("keeps travelling" in x for x in sp("RSW_SandLockHalt.Halted(pawn))\n            {\n                return", "false)\n            {\n                return")))
check("planted: in-flight Goto never interrupted fails",
      any("never interrupted" in x for x in sp("RSW_SandLockHalt.Tick(this);", "")))
check("planted: silent halt (no message) fails",
      any("no readable sign" in x for x in sp('Messages.Message(', 'Log.Message(')))
print("%d FAILED" % len(FAILS) if FAILS else "all ok")
sys.exit(1 if FAILS else 0)
