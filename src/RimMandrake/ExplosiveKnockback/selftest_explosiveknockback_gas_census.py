#!/usr/bin/env python3
"""Offline gas-source census for Explosive Knockback (bar our_gases_burn / inv_gas_tags, test T_GAS_TAG_CENSUS).

The census is taken over gas SOURCES, not Defs alone: every Gas ThingDef in our mods' Defs, every gas map grid of our own
(a MapComponent class named *Gas*), and every C# call site in our mods that adds gas (GasUtility.AddGas / gasGrid.AddGas).
Each must appear in gas_census.json, tagged flammable or untagged with its reason; no census row may name a source that
is gone. The tagged rows must equal the sources the code actually registers with the gas chain (a grid whose Ignite is
patched in RM_KnockbackCompat, or a def carrying the RM_KnockbackFlammableGas extension), and the Cauldron's vent gas must
be among them. Planted faults are run in memory and must go red.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_gas_census.py [--emit]
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)                       # src/RimMandrake
REPO = os.path.dirname(os.path.dirname(SRC))
CENSUS = os.path.join(HERE, "gas_census.json")
COMPAT = os.path.join(HERE, "Source", "RM_KnockbackCompat.cs")
SKIP = ("/bridgetools/", "/SelfTest/", "/obj/", "/bin/")
VENT = "grid:RimMandrake.Cauldron.RM_MapComponent_VentGas"


def rel(p):
    return os.path.relpath(p, REPO).replace(os.sep, "/")


def strip_comments(t):
    return re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", t, flags=re.S))


def read_tree():
    """{relpath: text} for our mods' C# and Defs XML (dev tooling skipped)."""
    out = {}
    for f in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True) + glob.glob(os.path.join(SRC, "**", "Defs", "**", "*.xml"), recursive=True):
        if not any(s in f.replace(os.sep, "/") for s in SKIP):
            out[rel(f)] = open(f, encoding="utf-8", errors="replace").read()
    return out


def sources(tree):
    """{source id: (kind, where, flammable tag present)}"""
    found = {}
    # Gas ThingDefs: concrete defs whose ParentName chain reaches a <category>Gas</category> base, or that say it themselves
    defs = {}
    for f, t in tree.items():
        if not f.endswith(".xml"):
            continue
        for m in re.finditer(r"<ThingDef\b([^>]*)>(.*?)</ThingDef>", t, re.S):
            a, body = m.group(1), m.group(2)
            name = re.search(r'\bName="(\w+)"', a)
            parent = re.search(r'\bParentName="(\w+)"', a)
            dn = re.search(r"<defName>(\w+)</defName>", body)
            defs[(name.group(1) if name else None, dn.group(1) if dn else None, f)] = (
                parent.group(1) if parent else None, "<category>Gas</category>" in body, 'Abstract="True"' in a,
                "RM_KnockbackFlammableGas" in body)
    by_name = {k[0]: v for k, v in defs.items() if k[0]}

    def is_gas(parent, own):
        seen = set()
        while not own and parent and parent not in seen:
            seen.add(parent)
            if parent in ("GasBase", "BaseGas"):
                return True
            p = by_name.get(parent)
            if not p:
                return False
            parent, own = p[0], p[1]
        return own
    for (name, dn, f), (parent, own, abstract, tag) in defs.items():
        if dn and not abstract and is_gas(parent, own):
            found["def:" + dn] = ("def", f, tag)
    # gas map grids of our own, and the grids RM_KnockbackCompat registers (Ignite patched with the chain's postfix)
    compat = strip_comments(tree.get(rel(COMPAT), ""))
    registered = set()
    for m in re.finditer(r'(\w+)\s*=\s*AccessTools\.TypeByName\("([\w.]+)"\)', compat):
        var, tname = m.group(1), m.group(2)
        if re.search(r"AccessTools\.Method\(\s*%s\s*,\s*\"Ignite\"" % var, compat) and "VentGasIgnitePostfix" in compat \
                and re.search(r"\.Patch\(\s*ignite", compat):
            registered.add(tname)
    for f, t in tree.items():
        if not f.endswith(".cs"):
            continue
        ns = re.search(r"namespace\s+([\w.]+)", t)
        for m in re.finditer(r"class\s+(\w*Gas\w*)\s*:\s*MapComponent\b", strip_comments(t)):
            full = (ns.group(1) + "." if ns else "") + m.group(1)
            found["grid:" + full] = ("grid", f, full in registered)
    # call sites that add gas: file + the gas-type argument (line numbers drift, the pair does not)
    for f, t in tree.items():
        if not f.endswith(".cs") or f.startswith("src/RimMandrake/ExplosiveKnockback/"):
            continue
        for m in re.finditer(r"(?:GasUtility|gasGrid)\s*\.\s*AddGas\(\s*([^;]*?)\)\s*;", strip_comments(t)):
            args = [a.strip() for a in m.group(1).split(",")]
            gas = args[1] if m.group(0).lstrip().startswith("gasGrid") else (args[2] if len(args) > 2 else "?")
            found["call:%s::%s" % (f, gas)] = ("call_site", f, False)
    return found


def judge(tree, census):
    src, rows, faults = sources(tree), {r["id"]: r for r in census["sources"]}, []
    for k, (kind, where, tag) in sorted(src.items()):
        r = rows.get(k)
        if r is None:
            faults.append("gas source not in the census: %s (%s, %s)" % (k, kind, where))
            continue
        if bool(r.get("tagged")) != bool(tag):
            faults.append("%s: census says tagged=%s, the code says %s" % (k, r.get("tagged"), tag))
        if not r.get("tagged") and not (r.get("reason") or "").strip():
            faults.append("%s: untagged with no reason" % k)
    for k in rows:
        if k not in src:
            faults.append("census row names a source that is gone: %s" % k)
    if not (VENT in src and src[VENT][2] and rows.get(VENT, {}).get("tagged")):
        faults.append("the Cauldron's vent gas is not tagged flammable (the leaf's red build)")
    if not src:
        faults.append("no gas source found at all: the reader is blind")
    return faults


def main():
    tree = read_tree()
    if "--emit" in sys.argv:
        for k, v in sorted(sources(tree).items()):
            print(k, v)
        return 0
    if not os.path.exists(CENSUS):
        print("FAIL no census file %s" % rel(CENSUS))
        return 1
    census = json.load(open(CENSUS))
    faults = judge(tree, census)
    for f in faults:
        print("FAIL", f)
    c = rel(COMPAT)
    mutants = {
        "the Cauldron hook removed": lambda t, cs: (dict(t, **{c: t[c].replace("nameof(VentGasIgnitePostfix)", "nameof(Nothing)")
                                                               .replace("VentGasIgnitePostfix", "Nothing")}), cs),
        "a new untracked call site": lambda t, cs: (dict(t, **{"src/RimMandrake/Planted/Source/X.cs":
                                                                "class X { void F(Map map) { GasUtility.AddGas(c, map, GasType.ToxGas, 3); } }"}), cs),
        "the Cauldron row untagged": lambda t, cs: (t, dict(cs, sources=[dict(r, tagged=False) if r["id"] == VENT else r for r in cs["sources"]])),
        "a stale census row": lambda t, cs: (t, dict(cs, sources=cs["sources"] + [{"id": "def:RM_GoneGas", "tagged": False, "reason": "x"}])),
        "an untagged row with no reason": lambda t, cs: (t, dict(cs, sources=[dict(r, reason="") if not r.get("tagged") else r for r in cs["sources"]])),
    }
    missed = 0
    for label, fn in mutants.items():
        mt, mc = fn(tree, census)
        if not judge(mt, mc):
            print("FAIL planted fault NOT CAUGHT:", label)
            missed += 1
    n = len(sources(tree))
    tagged = sorted(r["id"] for r in census["sources"] if r.get("tagged"))
    ok = not faults and not missed
    print("explosive knockback gas census: %s (%d sources, tagged %s; %d faults; %d/%d planted faults caught)"
          % ("PASS" if ok else "FAIL", n, ",".join(tagged) or "none", len(faults), len(mutants) - missed, len(mutants)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
