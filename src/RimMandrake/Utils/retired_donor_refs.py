#!/usr/bin/env python3
"""retired_donor_refs.py -- does any XML of ours still name a def that only a RETIRED donor defines?

    python3 src/RimMandrake/Utils/retired_donor_refs.py inventory --pid sarg.alphabiomes --root <donor mod dir>
    python3 src/RimMandrake/Utils/retired_donor_refs.py check [--pid sarg.alphabiomes] [--json OUT]

Item ALPHA_BIOMES_RETIRE_THE_LAST_PLANT_DONOR, plan step 5 ("references"). A retired donor's defs are gone from
the game, so every patch op of ours that targets one matches nothing (and a patch matching nothing logs nothing),
and every Defs reference to one is a cross-reference the game cannot resolve. Both are dead material: delete it,
never repoint our content at a donor def.

inventory  reads every XML under a `Defs` folder of the donor's install (all versions, all Mods/ subfolders) and
           writes infrastructure/state/facts/retired_donor_defs/<pid>.json: every concrete defName and every
           abstract Name="" (a ParentName of ours pointing at one is just as dead), minus every name a def dump
           capture taken WITHOUT the donor still defines (vanilla DebrisStoneA, Alpha Memes' GU_RedWood: those
           are live, and land in `alsoLive`). Run it ONCE while the donor is still on disk; the committed file
           is the record after it is unsubscribed.
check      walks src/**/*.xml as ELEMENTS (comments never count) and reports, per file, each donor name found as
             - an xpath target:  defName="X" inside any element text, or X as a step of an <xpath>
                                 (race/wildBiomes/X)
             - a whole value:    element text or attribute value exactly X (ParentName, li, thing, biome...)
             - a tag:            an element named X (wildBiomes/X, baseWeatherCommonalities/X rows)
             - a parent:         ParentName="X" where X is a donor ABSTRACT; abstract names match nowhere
                                 else, since the donor reuses live names for them (Name="Plant_Bush")
           Texture paths (values containing '/' without defName=) are not references and are skipped.
           A name some src/ XML defines itself (a port that kept the donor's name) is ours, not a hit.
           ALLOW below lists hits that are deliberate, each with its reason. Exit 1 on any other hit.

WHY BY NAME, NOT BY PREFIX: `AB_` is not Alpha Biomes' alone -- measured on the donor-off capture
2026-10-26T02-33-49Z, sarg.alphamemes (live) defines PreceptDef AB_MiningYield_VeryHigh. A prefix rule would
flag a live def; the inventory cannot.

SANITY: check refuses (exit 2, UNMEASURED) if an inventory is missing or holds fewer than 50 names -- a blind
instrument must not print a clean zero.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
FACTS = os.path.join(REPO, "infrastructure", "state", "facts", "retired_donor_defs")
SRC = os.path.join(REPO, "src")
MIN_NAMES = 50

# (repo-relative path, donor name) -> why the hit is deliberate. Keep it short and owned.
ALLOW = {
    ("src/RimMandrake/DeepDrill/Defs/RM_DeepHomeTable.xml", "AB_AlcyoniteChunk"):
        "generated from the mineral registry CSV's `retire:` binding with no homes; RM_DeepHomeRow.thing is a "
        "plain string (no cross-reference), so the row is inert. Minerals owns the CSV.",
}

DEFNAME_RE = re.compile(r'defName\s*=\s*["\']([^"\']+)["\']')
TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def _xml_files(root):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in ("obj", "bin", ".git")]
        for f in fns:
            if f.lower().endswith(".xml"):
                yield os.path.join(dp, f)


def _parse(path):
    try:
        return ET.parse(path).getroot()
    except (ET.ParseError, OSError, UnicodeDecodeError):
        return None


def inventory(pid, root):
    """{defs: sorted concrete defNames, abstracts: sorted Name= of abstract defs, files: n}."""
    defs, abstracts, files, unparsed = set(), set(), 0, []
    for p in _xml_files(root):
        rel = os.path.relpath(p, root).replace(os.sep, "/")
        if "/Defs/" not in "/" + rel:
            continue
        r = _parse(p)
        if r is None:
            unparsed.append(rel)
            continue
        files += 1
        for d in list(r):
            if not isinstance(d.tag, str):
                continue
            name = d.get("Name")
            if name:
                abstracts.add(name)
            dn = d.findtext("defName")
            if dn and dn.strip() and str(d.get("Abstract", "")).lower() != "true":
                defs.add(dn.strip())
    return {"packageId": pid, "source": root.replace(os.sep, "/"),
            "measuredUtc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "defFiles": files, "unparsed": sorted(unparsed),
            "defs": sorted(defs), "abstracts": sorted(abstracts - defs)}


def live_defnames(capture):
    """{defName: packageId} from a def dump capture taken WITHOUT the donor, or None if unreadable."""
    d = os.path.join(capture, "defs")
    if not os.path.isdir(d):
        return None
    live = {}
    for f in os.listdir(d):
        if not f.endswith(".json"):
            continue
        try:
            with open(os.path.join(d, f), encoding="utf-8") as fh:
                rows = json.load(fh).get("defs", [])
        except (OSError, ValueError, AttributeError):
            continue
        for r in rows:
            if isinstance(r, dict) and r.get("defName"):
                live[r["defName"]] = r.get("packageId")
    return live or None


def drop_live(inv, live, capture_name):
    """A name the donor-off game still defines (vanilla DebrisStoneA, Alpha Memes' GU_RedWood) is not dead."""
    also = {n: live[n] for n in inv["defs"] if n in live}
    inv["defs"] = [n for n in inv["defs"] if n not in also]
    inv["alsoLive"] = dict(sorted(also.items()))
    inv["liveCapture"] = capture_name
    return inv


def load_inventories(pid=None, facts=FACTS):
    out = {}
    if not os.path.isdir(facts):
        return out
    for f in sorted(os.listdir(facts)):
        if not f.endswith(".json"):
            continue
        with open(os.path.join(facts, f), encoding="utf-8") as fh:
            inv = json.load(fh)
        if pid and inv.get("packageId") != pid:
            continue
        out[inv["packageId"]] = inv
    return out


def defined_in(src):
    """Every defName and Name= that our own XML declares (a port that kept the donor name is ours)."""
    names = set()
    for p in _xml_files(src):
        r = _parse(p)
        if r is None:
            continue
        for d in r.iter():
            if not isinstance(d.tag, str):
                continue
            if d.get("Name"):
                names.add(d.get("Name"))
            dn = d.find("defName") if len(d) else None
            if dn is not None and dn.text and dn.text.strip():
                names.add(dn.text.strip())
    return names


def scan(src, donor_names, ours=frozenset(), repo=REPO, abstracts=frozenset()):
    """[(relpath, form, name)] for every live reference to a donor name in src XML.

    `donor_names` are concrete defNames (matched as xpath targets, path steps, tags and whole values);
    `abstracts` are the donor's abstract Name="" and match ONLY as a ParentName -- the donor reuses vanilla
    defNames as abstract names (Name="Plant_Bush" in its Odyssey desserts file), so anywhere else the same
    string means the live vanilla def."""
    hits = []
    for p in _xml_files(src):
        r = _parse(p)
        if r is None:
            continue
        rel = os.path.relpath(p, repo).replace(os.sep, "/")
        seen = set()

        def dead(name):
            return name in donor_names and name not in ours

        for el in r.iter():
            if not isinstance(el.tag, str):
                continue
            parent = el.get("ParentName")
            if parent and parent in abstracts and parent not in ours:
                seen.add(("parent", parent))
            vals = [(el.text or "").strip()] + list(el.attrib.values())
            if dead(el.tag):
                seen.add(("tag", el.tag))
            for v in vals:
                if not v:
                    continue
                for m in DEFNAME_RE.findall(v):
                    if dead(m):
                        seen.add(("xpath", m))
                if el.tag == "xpath" or "defName" in v:
                    # a path step names a def too: race/wildBiomes/AB_X, baseWeatherCommonalities/AB_Y
                    for m in TOKEN_RE.findall(v):
                        if dead(m):
                            seen.add(("xpath", m))
                if dead(v):
                    seen.add(("value", v))
        hits.extend((rel, form, name) for form, name in sorted(seen))
    return hits


def check(pid=None, src=SRC, facts=FACTS, allow=None, repo=REPO):
    """(status, rows). status: 'UNMEASURED' | 'CLEAN' | 'HITS'. rows: dicts with file/form/name/donor/allowed."""
    allow = ALLOW if allow is None else allow
    invs = load_inventories(pid, facts)
    if not invs or any(len(i["defs"]) + len(i["abstracts"]) < MIN_NAMES for i in invs.values()):
        return "UNMEASURED", [{"why": "no inventory, or one under %d names: %s" % (
            MIN_NAMES, {k: len(v["defs"]) + len(v["abstracts"]) for k, v in invs.items()})}]
    owner, defs, abstracts = {}, set(), set()
    for pkg, inv in invs.items():
        for n in inv["defs"] + inv["abstracts"]:
            owner.setdefault(n, pkg)
        defs.update(inv["defs"])
        abstracts.update(inv["abstracts"])
    ours = defined_in(src)
    rows = []
    for rel, form, name in scan(src, defs, ours, repo, abstracts):
        why = allow.get((rel, name))
        rows.append({"file": rel, "form": form, "name": name, "donor": owner[name], "allowed": why})
    live = [r for r in rows if not r["allowed"]]
    return ("HITS" if live else "CLEAN"), rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a_inv = sub.add_parser("inventory")
    a_inv.add_argument("--pid", required=True)
    a_inv.add_argument("--root", required=True)
    a_inv.add_argument("--out", default=None)
    a_inv.add_argument("--live-capture", default=None,
                       help="def dump capture taken without the donor (default: newest capture)")
    a_chk = sub.add_parser("check")
    a_chk.add_argument("--pid", default=None)
    a_chk.add_argument("--json", default=None)
    a = ap.parse_args(argv)

    if a.cmd == "inventory":
        if not os.path.isdir(a.root):
            print("UNMEASURED: donor root not found: " + a.root)
            return 2
        cap = a.live_capture
        if not cap:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from biome_animal_conflicts import newest_capture
            cap = newest_capture()
        live = live_defnames(cap) if cap else None
        if live is None:
            print("UNMEASURED: no readable donor-off def dump capture (--live-capture); without one a name "
                  "vanilla or a live mod also defines would be reported as dead")
            return 2
        if a.pid in set(live.values()):
            print("UNMEASURED: capture %s still loads %s -- it cannot say which names are dead" % (cap, a.pid))
            return 2
        inv = drop_live(inventory(a.pid, a.root), live, os.path.basename(cap.rstrip("/")))
        n = len(inv["defs"]) + len(inv["abstracts"])
        if n < MIN_NAMES:
            print("UNMEASURED: only %d names under %s -- wrong root?" % (n, a.root))
            return 2
        out = a.out or os.path.join(FACTS, a.pid + ".json")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(inv, fh, indent=1)
            fh.write("\n")
        print("%s: %d defs + %d abstracts from %d Defs files (%d unparsed; %d still live in %s, dropped) -> %s"
              % (a.pid, len(inv["defs"]), len(inv["abstracts"]), inv["defFiles"], len(inv["unparsed"]),
                 len(inv["alsoLive"]), inv["liveCapture"], out))
        return 0

    status, rows = check(a.pid)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump({"status": status, "rows": rows}, fh, indent=1)
    if status == "UNMEASURED":
        print("UNMEASURED: " + rows[0]["why"])
        return 2
    live = [r for r in rows if not r["allowed"]]
    for r in rows:
        tag = "ALLOWED" if r["allowed"] else "DEAD   "
        print("%s %-6s %-40s %s  (%s)" % (tag, r["form"], r["name"], r["file"], r["donor"]))
    print("%s: %d live reference(s) to retired-donor defs, %d allowed" % (
        status, len(live), len(rows) - len(live)))
    return 1 if live else 0


if __name__ == "__main__":
    sys.exit(main())
