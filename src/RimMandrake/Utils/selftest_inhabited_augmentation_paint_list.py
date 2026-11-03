#!/usr/bin/env python3
"""Selftest for INHABITED_AUGMENTATION_BUILD_1 criterion 3: the §8 structure archetypes are placed on Ash'karr at
the one final world painting (BIOME_PAINT_ONCE_AT_THE_END_1). This checks, offline, that the step can be carried
out as written:

  1. the paint list has a section for this item, with a table row for every §8.1-8.14 archetype;
  2. every TileMutatorDef the table names is defined in src/ (as an XML element <defName>, not a text grep),
     and its extraGenSteps start with a GenStepDef that is also defined in src/;
  3. every structure TileMutatorDef in the two StructureInjections mods that replays one of the §8
     templates (Templates/<name>.txt named by its GenStep) appears in the table, so the list misses no
     responder.

Then it runs the same checker on three broken inputs (a row dropped, a misspelt def, a responder the table
leaves out) and requires each to fail, so a green run proves the checker can see a gap.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PAINT = os.path.join(REPO, "infrastructure/state/items/BIOME_PAINT_ONCE_AT_THE_END_1.md")
MOD_DIRS = [os.path.join(REPO, "src/RimStarWars/StructureInjectionsSW"),
            os.path.join(REPO, "src/RimUtinni/StructureInjectionsRUT")]
SECTION = "INHABITED_AUGMENTATION_BUILD_1"
SECTIONS = [f"8.{i}" for i in range(1, 15)]
# The rimplace templates this item built for §8; a responder replaying one of them must be on the list.
TEMPLATES = {"homestead", "homestead_abode", "homestead_compound", "moisture_farm", "moisture_farm_ruined",
             "moisture_homestead", "moisture_vaporator_field", "moisture_walled_compound", "mining_site",
             "trading_post", "road_warehouse", "garrison_tiny", "tar_refinery", "gas_station", "crashed_ship",
             "dead_caravan", "beast_lair", "beast_pens"}


def section_rows(text):
    start = None
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("## ") and SECTION in ln:
            start = i
    if start is None:
        return None
    rows = {}
    for ln in lines[start + 1:]:
        if ln.startswith("## "):
            break
        m = re.match(r"\|\s*(8\.\d+)\s*\|[^|]*\|([^|]*)\|", ln)
        if m:
            rows[m.group(1)] = re.findall(r"`((?:RSW|RUT|RM)_[A-Za-z0-9_]+)`", m.group(2))
    return rows


def load_defs():
    """{defName: (DefType, element)} over both mods' Defs, parsed as XML."""
    out = {}
    for mod in MOD_DIRS:
        for root, _, files in os.walk(os.path.join(mod, "Defs")):
            for f in files:
                if not f.endswith(".xml"):
                    continue
                tree = ET.parse(os.path.join(root, f))
                for el in tree.getroot():
                    dn = el.find("defName")
                    if dn is not None and dn.text:
                        out[dn.text.strip()] = (el.tag, el)
    return out


def responders(defs):
    """{TileMutatorDef: template} for every mutator whose first GenStep replays a §8 template."""
    out = {}
    for name, (tag, el) in defs.items():
        if tag != "TileMutatorDef":
            continue
        steps = [li.text.strip() for li in el.findall("extraGenSteps/li") if li.text]
        if not steps or steps[0] not in defs:
            continue
        gtag, gel = defs[steps[0]]
        blob = ET.tostring(gel, encoding="unicode")
        m = re.search(r"Templates/([A-Za-z0-9_]+)\.txt", blob) or re.search(r"<(?:planFile|plan|file)>\s*([A-Za-z0-9_]+?)(?:\.txt)?\s*<", blob)
        if m and m.group(1) in TEMPLATES:
            out[name] = m.group(1)
    return out


def check(rows, defs, resp):
    errs = []
    if rows is None:
        return [f"paint list has no section naming {SECTION}"]
    for s in SECTIONS:
        if s not in rows:
            errs.append(f"no row for {s}")
    listed = {d for v in rows.values() for d in v}
    for d in sorted(listed):
        if d not in defs or defs[d][0] != "TileMutatorDef":
            errs.append(f"{d} is not a TileMutatorDef in src/")
            continue
        steps = [li.text.strip() for li in defs[d][1].findall("extraGenSteps/li") if li.text]
        if not steps or steps[0] not in defs or defs[steps[0]][0] != "GenStepDef":
            errs.append(f"{d}: first extraGenStep is not a GenStepDef in src/")
    for d in sorted(set(resp) - listed):
        errs.append(f"responder {d} (template {resp[d]}) is missing from the paint list")
    return errs


def main():
    text = open(PAINT, encoding="utf-8").read()
    rows = section_rows(text)
    defs = load_defs()
    resp = responders(defs)
    # Sanity: the instrument must see the responders it is meant to cover.
    if len(resp) < 12:
        print(f"FAIL: only {len(resp)} §8 responders found in src/ — the template matcher is blind")
        return 1
    errs = check(rows, defs, resp)
    if errs:
        for e in errs:
            print("FAIL:", e)
        return 1
    # Negative controls: each must be caught.
    bad = []
    r1 = dict(rows); r1.pop("8.7")
    bad.append(("row dropped", r1))
    r2 = {k: list(v) for k, v in rows.items()}; r2["8.4"] = ["RSW_TradingPots"]
    bad.append(("misspelt def", r2))
    r3 = {k: [d for d in v if d != "RSW_GasStation"] for k, v in rows.items()}
    bad.append(("responder left out", r3))
    for label, r in bad:
        if not check(r, defs, resp):
            print(f"FAIL: negative control '{label}' passed — the checker cannot see")
            return 1
    n = sum(len(v) for v in rows.values())
    print(f"PASS: {len(rows)} §8 rows, {n} TileMutatorDefs listed, {len(resp)} responders in src/ all covered; "
          f"3/3 negative controls caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
