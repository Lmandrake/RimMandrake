#!/usr/bin/env python3
"""Selftest for ASTEROID_DESERT_ORES_1: a live "defs loaded" row reads only defs that its run's mod list carries.

UtinniPatches' phrikite_defs_loaded and zersium_defs_loaded read ThingDef/RSW_Phrik and ThingDef/RSW_Zersium, which
mandrake.rsw.armoury defines. modcheck composed UtinniPatches with its hard dependencies only (WeatherSuite and the
composed biomes; SteveDesktop job J20261114T130255Z-e4cfd1, worker.log "deploy: with the mods of ours its composed list
names: WeatherSuite, RimMandrake.Biomes"), so both rows read FAIL "def did not load" three times (2026-11-13/14). The
mod was right: its GenSteps carry MayRequire="mandrake.rsw.armoury". The list was wrong, and the bar stayed undecided.

  1. the instance: every def that a `jawa/get_defs` literal in UtinniPatches' validation.py names is defined by a mod
     whose packageId runner.composed_ids("UtinniPatches") composes (the run's own list)
  2. the guard can see: with the closure taken away (the pre-fix list), it names RSW_Phrik and RSW_Zersium
Offline: reads src/ only; nothing is deployed and no game is touched."""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import runner  # noqa: E402

REPO = runner.ROOT
TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")
FAILS = []
# The literal def specs a validation.py hands to jawa/get_defs in a loop: for d in ("Type/Name", ...)
LOOP = re.compile(r'for\s+\w+\s+in\s+\(([^)]*)\)\s*:\s*\n\s*r\s*=\s*t\.bridge_call\("jawa/get_defs"')
SPEC = re.compile(r'"(\w+)/(\w+)"')


def ok(cond, what, got=None):
    print(("PASS  " if cond else "FAIL  ") + what + ("" if cond or got is None else "   got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def asked_defs(validation_py):
    """[(defType, defName)] that the file's def-load loops read live."""
    with open(validation_py, encoding="utf-8") as f:
        text = f.read()
    return [m for block in LOOP.findall(text) for m in SPEC.findall(block)]


def def_homes():
    """{(defType, defName): set of mod folder names under src/ that define it}."""
    out = {}
    for tier in TIERS:
        base = os.path.join(REPO, "src", tier)
        for mod in sorted(os.listdir(base)):
            ddir = os.path.join(base, mod, "Defs")
            if not os.path.isdir(ddir):
                continue
            for dp, _dn, fns in os.walk(ddir):
                for fn in fns:
                    if not fn.endswith(".xml"):
                        continue
                    try:
                        root = ET.parse(os.path.join(dp, fn)).getroot()
                    except ET.ParseError:
                        continue
                    for e in root:
                        name = (e.findtext("defName") or "").strip()
                        if name:
                            out.setdefault((e.tag, name), set()).add(mod)
    return out


def pid_of(mod):
    folded = runner.composed_into(mod)
    return folded[1] if folded else runner.mod_package_id(runner.find_mod_dir(mod)).lower()


def off_list(mod, composed, homes):
    """The asked defs whose every defining mod is missing from `composed` (lowercase packageIds)."""
    vpy = os.path.join(runner.find_mod_dir(mod), "validation.py")
    bad = []
    for spec in asked_defs(vpy):
        where = homes.get(spec, set())
        if not where:
            continue        # a def of a donor or of the game: not ours to place on the list
        if not any(pid_of(m) in composed for m in where):
            bad.append("%s/%s (%s)" % (spec[0], spec[1], ",".join(sorted(where))))
    return bad


def main():
    homes = def_homes()
    asked = asked_defs(os.path.join(runner.find_mod_dir("UtinniPatches"), "validation.py"))
    ok(("ThingDef", "RSW_Phrik") in asked and ("ThingDef", "RSW_Zersium") in asked,
       "the reader finds the phrikite and zersium def-load rows in UtinniPatches' validation.py", asked)
    composed = {p.lower() for p in runner.composed_ids("UtinniPatches")}
    bad = off_list("UtinniPatches", composed, homes)
    ok(not bad, "every def UtinniPatches' live def-load rows read is on its modcheck list", bad)
    pre_fix = {p.lower() for p in runner.with_own_dependencies(
        list(runner.mod_dependency_ids(runner.find_mod_dir("UtinniPatches"))) + ["mandrake.rut.patches"])}
    seen = off_list("UtinniPatches", pre_fix, homes)
    ok(any("RSW_Phrik " in s for s in seen) and any("RSW_Zersium " in s for s in seen),
       "the guard can see: on the pre-fix list (hard dependencies only) it names RSW_Phrik and RSW_Zersium", seen)
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
