#!/usr/bin/env python3
"""selftest_force_forecast_text.py -- PSYCHICDRONE_RESKIN_FORECAST_TEXT: every psychic-family GameConditionDef whose
quest/forecast fragment (descriptionFuture, read mid-sentence through [gameConditionDescriptionFuture]) still said
"psychic ..." is relabelled by Patches/PsychicToForceDisturbance.xml in that file's Force vocabulary, keeping every
[placeholder] of the original, lowercase and without a closing full stop. A negative control (the file with those ops
removed) must go red. Offline; the def dump, when present, is only a sanity probe.

    python3 src/RimStarWars/StarWarsPatches/selftest_force_forecast_text.py
"""
import copy
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
PATCH = os.path.join(HERE, "Patches", "PsychicToForceDisturbance.xml")

# Unpatched values, read from the live def dump 2026-10-26T13-58-35Z (GameConditionDef.json).
ORIGINAL = {
    "PsychicDrone": "a [psychicDroneLevel] psychic drone will buzz the area around [map_definite] for "
                    "[gameConditionDuration_duration], pushing all people of the [psychicDroneGender] gender towards insanity",
    "PsychicSuppression": "a psychic suppression wave will reduce the consciousness of all [psychicSuppressorGender]s "
                          "around [map_definite] for [gameConditionDuration_duration]",
    "VREA_PsychicStorm": "a storm of psychic energy will cover the area around [map_definite] for "
                         "[gameConditionDuration_duration], potentially damaging infrastructure and doubling psychic "
                         "sensitivity of every living being.",
}
sys.path.insert(0, os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))
from game_paths import CAPTURES  # noqa: E402
DUMP_GLOB = os.path.join(CAPTURES, "*", "defs", "GameConditionDef.json")
FAILS = []
# "psychic sensitivity" is the real, unrenamed stat and stays (the file's own rule); [placeholders] are stripped first
PSY = re.compile(r"psychic(?! sensitivity)", re.I)


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def ops_with_value(root):
    """Every (xpath, value element) pair, however deeply nested in Conditional/FindMod/Sequence."""
    out = []
    for el in root.iter():
        xp, val = el.find("xpath"), el.find("value")
        if xp is not None and val is not None and el.tag in ("Operation", "match", "li", "nomatch"):
            out.append((xp.text.strip(), val))
    return out


def forecast_problems(root):
    """Problems with the descriptionFuture ops of a parsed patch file (empty list = good)."""
    bad = []
    ops = ops_with_value(root)
    for d, orig in ORIGINAL.items():
        xp = '/Defs/GameConditionDef[defName="%s"]/descriptionFuture' % d
        vals = [v for x, v in ops if x == xp]
        if len(vals) != 1:
            bad.append("%s: %d replace ops on descriptionFuture (want 1)" % (d, len(vals)))
            continue
        node = vals[0].find("descriptionFuture")
        text = (node.text or "") if node is not None else ""
        if not text:
            bad.append("%s: value has no <descriptionFuture> node" % d)
            continue
        if sorted(re.findall(r"\[\w+\]", text)) != sorted(re.findall(r"\[\w+\]", orig)):
            bad.append("%s: placeholders changed: %s" % (d, text))
        if "Force" not in text:
            bad.append("%s: no Force vocabulary: %s" % (d, text))
        if PSY.search(re.sub(r"\[\w+\]", "", text)):
            bad.append("%s: still says psychic outside the stat name: %s" % (d, text))
        if not text[:1].islower() or text.rstrip().endswith("."):
            bad.append("%s: not a mid-sentence fragment (lowercase start, no full stop): %s" % (d, text))
    # nothing else in the file reintroduces the old wording
    for x, v in ops:
        s = "".join(v.itertext())
        if PSY.search(re.sub(r"\[\w+\]", "", s)):
            bad.append("value at %s says psychic outside the stat name" % x)
    return bad


def main():
    root = ET.parse(PATCH).getroot()
    n_ops = len(ops_with_value(root))
    check("sanity: the parser sees the file's ops", n_ops >= 50, "only %d ops parsed" % n_ops)
    probs = forecast_problems(root)
    check("shipped forecast text is Force-flavoured", not probs, "; ".join(probs))

    # negative control: strip the descriptionFuture ops -> must go red for every def
    ctl = copy.deepcopy(root)
    for parent in ctl.iter():
        for child in list(parent):
            xp = child.find("xpath")
            if xp is not None and xp.text.strip().endswith("/descriptionFuture"):
                parent.remove(child)
    cprobs = forecast_problems(ctl)
    check("control: file without the forecast ops is red for all 3 defs", len(cprobs) >= len(ORIGINAL), "; ".join(cprobs))
    # planted break: a value that still says psychic drone
    bad = copy.deepcopy(root)
    for x, v in ops_with_value(bad):
        if x.endswith('"PsychicDrone"]/descriptionFuture'):
            v.find("descriptionFuture").text = ORIGINAL["PsychicDrone"]
    check("control: the old PsychicDrone text is red", any("PsychicDrone" in p for p in forecast_problems(bad)))

    # sanity probe on the instrument: the newest dump holds either the original or the shipped value
    dumps = sorted(glob.glob(DUMP_GLOB))
    if not dumps:
        print("note  no def dump reachable; the dump probe is UNMEASURED (the offline checks above still decide)")
    else:
        live = {x["defName"]: x.get("fields", {}).get("descriptionFuture") for x in json.load(open(dumps[-1]))["defs"]}
        shipped = {d: "".join(v.find("descriptionFuture").itertext()) for x, v in ops_with_value(root)
                   for d in ORIGINAL if x == '/Defs/GameConditionDef[defName="%s"]/descriptionFuture' % d}
        for d, orig in ORIGINAL.items():
            if d not in live:
                print("note  %s absent from %s (its mod not loaded there)" % (d, dumps[-1].split("/captures/")[1]))
                continue
            check("dump probe %s holds the original or the shipped text" % d, live[d] in (orig, shipped.get(d)), repr(live[d]))
    print("force forecast text: %d failure(s) -> %s" % (len(FAILS), "OK" if not FAILS else "FAILED"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
