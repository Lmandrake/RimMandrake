"""Selftest for LongShade/validation.py's package-gate check: it follows Biomes.compose.json, and a wrong id still fails."""
import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ls_validation", os.path.join(HERE, "validation.py"))
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

FAILS = []


def check(name, ok, detail=""):
    print("%-5s %s %s" % ("ok" if ok else "FAIL", name, "" if ok else detail))
    if not ok:
        FAILS.append(name)


host = v.loaded_host_package()
check("sanity probe: host read from the compose manifest is mandrake.rm.biomes", host == "mandrake.rm.biomes", host)
check("the true gate (the host package) passes", v.gate_findings("mandrake.rm.biomes") == [])
check("planted defect: the folded member id fails", bool(v.gate_findings("mandrake.rm.longshade")))
check("planted defect: a nonexistent id fails", bool(v.gate_findings("mandrake.rm.nosuchmod")))
check("planted defect: a missing gate fails", bool(v.gate_findings(None)))
with tempfile.TemporaryDirectory() as d:
    m = json.load(open(v.COMPOSE, encoding="utf-8"))
    m["entries"] = [e for e in m["entries"] if e.get("source") != "LongShade"]
    p = os.path.join(d, "c.json")
    json.dump(m, open(p, "w"))
    check("planted defect: a manifest that no longer composes LongShade is not silently passed",
          bool(v.gate_findings("mandrake.rm.biomes", p)))
check("the shipped def passes the whole static suite on the gate", not [x for x in v.static_checks() if "RUT_JawaReturnTow" in x])
check("haze: shipped defs and wiring pass", v.haze_problems() == [], str(v.haze_problems()))
import xml.etree.ElementTree as ET
bad = ET.fromstring(open(os.path.join(HERE, "Defs", "IncidentDefs", "RM_SmokeHaze.xml"), encoding="utf-8").read().replace("<shadowLengthFactor>1.6", "<shadowLengthFactor>0.5"))
check("planted defect: a haze that shortens shadows fails", any("lengthening" in x for x in v.haze_problems(bad)))
print("%d FAILED" % len(FAILS) if FAILS else "all ok")
sys.exit(1 if FAILS else 0)
