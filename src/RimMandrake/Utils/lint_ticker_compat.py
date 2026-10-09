#!/usr/bin/env python3
"""lint_ticker_compat.py - MOD_TICKER_COMPAT_LINT_1 (design pass EH-2): a ThingComp that can never tick.

RimWorld calls exactly one comp tick method per ThingDef.tickerType:
    Normal -> CompTick     Rare -> CompTickRare     Long -> CompTickLong     Never -> none
(ThingWithComps.Tick / TickRare / TickLong each loop only their own method.) A comp that overrides only a
method its parent def's tickerType never calls loads clean and silently does nothing. This bug class bit
three times: RM_CompCrackFall, a Plant comp overriding CompTick (plants only tick Long), and the weir.

Offline, no game, no build. Reads every Defs XML and C# under src/:
  * resolves each concrete ThingDef's ParentName chain INSIDE src/ (comps lists concatenate, tickerType is
    first-explicit-wins up the chain); a chain that leaves src/ is resolved only for the vanilla roots in
    VANILLA_TICKER (PlantBase/TreeBase -> Long, pawn bases -> Normal); anything else is counted UNRESOLVED,
    never guessed;
  * maps each <li Class="PropsClass"> to its comp class (<compClass> in XML, else `compClass = typeof(X)`
    in the CompProperties constructor), then to the tick methods that class overrides, through its src/
    base classes.
Findings (ERROR): NEVER_TICKS (comp overrides tick methods but none of them is the def's), NEVER_TICKER (the def
is tickerType Never yet carries a ticking comp). Counts are printed so a lint that looked at nothing cannot pass.

    python3 src/RimMandrake/Utils/lint_ticker_compat.py [--quiet]      exit 1 on any ERROR
    python3 src/RimMandrake/Utils/lint_ticker_compat.py --selftest     synthetic fixtures, must flag each mutant
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SKIP = {"bin", "obj", "__pycache__", ".git", "Textures", "Sounds", "Assemblies", "SelfTest", "node_modules"}

METHOD_FOR = {"Normal": "CompTick", "Rare": "CompTickRare", "Long": "CompTickLong"}
VANILLA_TICKER = {"PlantBase": "Long", "TreeBase": "Long", "BasePawn": "Normal", "BaseHumanlike": "Normal",
                  "AnimalThingBase": "Normal", "BaseAnimal": "Normal"}
PAWN_ROOTS = {"BasePawn", "BaseHumanlike", "AnimalThingBase", "BaseAnimal"}
# Pawn.Tick (decompiled 1.6, RimSage) also calls TickRare every 250 ticks, so a pawn def with tickerType Normal
# runs BOTH CompTick and CompTickRare. Every other thing runs only the one method its tickerType names.
# Known-exempt (def, comp) pairs: a thing whose ticker is Never but whose comp is driven by something else.
ALLOW = set()

OVERRIDE = re.compile(r"override\s+void\s+(CompTick|CompTickRare|CompTickLong)\s*\(")
CLASS = re.compile(r"\bclass\s+(\w+)\s*(?:<[^>{]*>)?\s*(?::\s*([\w.<>, ]+?))?\s*(?:where\b[^{]*)?\{")
TYPEOF = re.compile(r"compClass\s*=\s*typeof\s*\(\s*([\w.]+)\s*\)")


def _walk(root, exts):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP]
        for f in fn:
            if f.endswith(exts):
                yield os.path.join(dp, f)


def _strip_comments(t):
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    return re.sub(r"//[^\n]*", "", t)


def _simple(n):
    return n.split(".")[-1].split("<")[0].strip()


def parse_cs(texts):
    """-> (bases: class -> [base simple names], ticks: class -> set(methods it overrides), comp_of: props class -> comp class)"""
    bases, ticks, comp_of = {}, {}, {}
    for path, text in texts:
        t = _strip_comments(text)
        spans = [(m.start(), m.group(1), m.group(2)) for m in CLASS.finditer(t)]
        for i, (pos, name, base) in enumerate(spans):
            end = spans[i + 1][0] if i + 1 < len(spans) else len(t)
            body = t[pos:end]
            bases.setdefault(name, [])
            if base:
                bases[name] += [_simple(b) for b in base.split(",")]
            ticks.setdefault(name, set()).update(OVERRIDE.findall(body))
            m = TYPEOF.search(body)
            if m:
                comp_of[name] = _simple(m.group(1))
    return bases, ticks, comp_of


def effective_ticks(cls, bases, ticks, seen=None):
    """tick methods a comp class overrides, itself or through a src/ base class."""
    seen = seen or set()
    if cls in seen:
        return set()
    seen.add(cls)
    out = set(ticks.get(cls, ()))
    for b in bases.get(cls, ()):
        out |= effective_ticks(b, bases, ticks, seen)
    return out


def parse_defs(xml_texts):
    """-> {defName_or_ParentKey: dict(parent, abstract, ticker, comps[(cls, compClass|None)], path)} for ThingDef nodes"""
    defs = []
    for path, text in xml_texts:
        try:
            root = ET.fromstring(text.encode("utf-8") if isinstance(text, str) else text)
        except ET.ParseError:
            continue
        for el in root.iter("ThingDef"):
            name = el.findtext("defName")
            nm = el.get("Name")
            comps = []
            cn = el.find("comps")
            if cn is not None:
                for li in cn.findall("li"):
                    comps.append((li.get("Class"), li.findtext("compClass")))
            defs.append(dict(race=el.find("race") is not None, name=name, xname=nm, parent=el.get("ParentName"), abstract=(el.get("Abstract") or "").lower() == "true",
                             ticker=el.findtext("tickerType"), comps=comps, path=path))
    return defs


def resolve(defs):
    by_x = {d["xname"]: d for d in defs if d["xname"]}
    by_n = {d["name"]: d for d in defs if d["name"]}

    def chain(d):
        out, cur, guard = [d], d, 0
        while cur and cur["parent"] and guard < 40:
            guard += 1
            nxt = by_x.get(cur["parent"]) or by_n.get(cur["parent"])
            if nxt is None:
                out.append({"root": cur["parent"]})
                break
            out.append(nxt)
            cur = nxt
        return out

    res = []
    for d in defs:
        if d["abstract"] or not d["name"]:
            continue
        ch = chain(d)
        ticker, unresolved, comps = None, False, []
        for node in ch:
            if "root" in node:
                if ticker is None:
                    ticker = VANILLA_TICKER.get(node["root"])
                    unresolved = ticker is None
                continue
        for node in reversed([n for n in ch if "root" not in n]):
            comps += node["comps"]
        for node in [n for n in ch if "root" not in n]:
            if node["ticker"]:
                ticker = node["ticker"]
                unresolved = False
                break
        pawn = any(n.get("race") for n in ch if "root" not in n) or any(n.get("root") in PAWN_ROOTS for n in ch if "root" in n)
        res.append(dict(pawn=pawn, name=d["name"], path=d["path"], ticker=ticker, unresolved=unresolved and ticker is None,
                        root_is_src=not any("root" in n for n in ch), comps=comps))
    return res


def lint(cs_texts, xml_texts):
    bases, ticks, comp_of = parse_cs(cs_texts)
    res = resolve(parse_defs(xml_texts))
    findings, c = [], dict(defs=len(res), comps=0, ticking_comps=0, unresolved_ticker=0, unresolved_comp=0)
    for d in res:
        t = d["ticker"]
        if t is None and d["root_is_src"]:
            t = "Never"          # a src/-rooted chain with no tickerType anywhere uses the engine default
        if t is None:
            c["unresolved_ticker"] += 1
            continue
        for cls, comp_class_xml in d["comps"]:
            c["comps"] += 1
            comp = _simple(comp_class_xml) if comp_class_xml else comp_of.get(_simple(cls)) if cls else None
            if not comp or comp not in bases:
                c["unresolved_comp"] += 1       # engine/vanilla comp, or a class outside src/: not judged
                continue
            eff = effective_ticks(comp, bases, ticks)
            if not eff:
                continue
            c["ticking_comps"] += 1
            if (d["name"], comp) in ALLOW:
                continue
            want = METHOD_FOR.get(t)
            if d["pawn"] and t == "Normal" and "CompTickRare" in eff:
                continue
            if t == "Never":
                findings.append(("NEVER_TICKER", d["path"], "%s is tickerType Never but carries %s (overrides %s): it never ticks"
                                 % (d["name"], comp, "/".join(sorted(eff)))))
            elif want not in eff:
                findings.append(("NEVER_TICKS", d["path"], "%s is tickerType %s (calls %s) but %s overrides only %s: it never ticks"
                                 % (d["name"], t, want, comp, "/".join(sorted(eff)))))
    return findings, c


def load_repo():
    src = os.path.join(REPO, "src")
    cs = [(p, open(p, encoding="utf-8-sig", errors="replace").read()) for p in _walk(src, (".cs",))]
    xml = []
    for p in _walk(src, (".xml",)):
        if os.sep + "Defs" + os.sep in p or p.endswith(os.sep + "Defs"):
            xml.append((p, open(p, encoding="utf-8-sig", errors="replace").read()))
    return cs, xml


def selftest():
    cs = [("a.cs", """
namespace N { public class CompP : CompProperties { public CompP() { compClass = typeof(CompLongOnly); } }
public class CompLongOnly : ThingComp { public override void CompTickLong() {} }
public class CompNormalOnly : ThingComp { public override void CompTick() {} }
public class DerivedLong : CompLongOnly { }
public class CompPN : CompProperties { public CompPN() { compClass = typeof(CompNormalOnly); } } }""")]
    D = lambda body: [("d.xml", "<Defs>%s</Defs>" % body)]
    ok = '<ThingDef ParentName="PlantBase"><defName>P</defName><comps><li Class="CompP"/></comps></ThingDef>'
    bad_plant = '<ThingDef ParentName="PlantBase"><defName>P</defName><comps><li Class="CompPN"/></comps></ThingDef>'
    bad_never = '<ThingDef><defName>B</defName><comps><li Class="CompP"/></comps></ThingDef>'
    inherited = ('<ThingDef Abstract="True" Name="A"><tickerType>Rare</tickerType><comps><li Class="CompP"/></comps></ThingDef>'
                 '<ThingDef ParentName="A"><defName>C</defName></ThingDef>')
    ok_normal = '<ThingDef><defName>N</defName><tickerType>Normal</tickerType><comps><li Class="CompPN"/></comps></ThingDef>'
    fails = []
    f, c = lint(cs, D(ok))
    if f or c["ticking_comps"] != 1:
        fails.append("clean plant+CompTickLong flagged or unseen: %r %r" % (f, c))
    f, c = lint(cs, D(bad_plant))
    if [x[0] for x in f] != ["NEVER_TICKS"]:
        fails.append("plant + CompTick-only comp not flagged: %r" % (f,))
    f, c = lint(cs, D(bad_never))
    if [x[0] for x in f] != ["NEVER_TICKER"]:
        fails.append("ticker Never + ticking comp not flagged: %r" % (f,))
    f, c = lint(cs, D(inherited))
    if [x[0] for x in f] != ["NEVER_TICKS"]:
        fails.append("abstract-parent Rare + Long-only comp not flagged: %r" % (f,))
    f, c = lint(cs, D(ok_normal))
    if f:
        fails.append("Normal + CompTick comp flagged: %r" % (f,))
    f, c = lint(cs + [("b.cs", "class CompDer : CompLongOnly {} class PD : CompProperties { public PD() { compClass = typeof(CompDer); } }")],
                D('<ThingDef ParentName="PlantBase"><defName>Q</defName><comps><li Class="PD"/></comps></ThingDef>'))
    if f or c["ticking_comps"] != 1:
        fails.append("comp inheriting CompTickLong from a src/ base not credited: %r %r" % (f, c))
    f, c = lint([("p.cs", "class CompR : ThingComp { public override void CompTickRare() {} } class PR : CompProperties { public PR() { compClass = typeof(CompR); } }")],
                D('<ThingDef ParentName="BasePawn"><defName>Z</defName><comps><li Class="PR"/></comps></ThingDef>'
                  '<ThingDef><defName>Y</defName><tickerType>Normal</tickerType><comps><li Class="PR"/></comps></ThingDef>'))
    if [x[0] for x in f] != ["NEVER_TICKS"] or "Y" not in f[0][2]:
        fails.append("pawn Normal+CompTickRare must pass, building Normal+CompTickRare must fail: %r" % (f,))
    if fails:
        print("lint_ticker_compat selftest FAILED:\n  " + "\n  ".join(fails))
        return 1
    print("lint_ticker_compat selftest: 7/7 cases OK")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    cs, xml = load_repo()
    findings, c = lint(cs, xml)
    if not c["defs"] or not c["ticking_comps"]:
        print("lint_ticker_compat: UNMEASURED - looked at %(defs)d defs and %(ticking_comps)d ticking comps" % c)
        return 2
    if "--quiet" not in argv:
        for k, p, m in findings:
            print("ERROR %s %s: %s" % (k, os.path.relpath(p, REPO), m))
    print("lint_ticker_compat: %(defs)d concrete ThingDefs, %(comps)d comp entries, %(ticking_comps)d ticking src comps judged, "
          "%(unresolved_ticker)d defs with unresolved ticker (vanilla parent), %(unresolved_comp)d engine/non-src comps skipped" % c
          + ", %d ERROR" % len(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
