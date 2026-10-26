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
    VANILLA_TICKER (PlantBase/TreeBase -> Long, pawn bases -> Normal, BuildingBase/BenchBase -> Never); anything else is counted UNRESOLVED,
    never guessed;
  * maps each <li Class="PropsClass"> to its comp class (<compClass> in XML, else `compClass = typeof(X)`
    in the CompProperties constructor), then to the tick methods that class overrides, through its src/
    base classes.
Findings (ERROR): NEVER_TICKS (comp overrides tick methods but none of them is the def's), NEVER_TICKER (the def
is tickerType Never yet carries a ticking comp), PAWN_DOUBLE_PUSH (HEATPUSHER_FIX_PAWN_DOUBLE_PUSH: a pawn def carries a
CompProperties_HeatPusher whose comp class is vanilla CompHeatPusher/CompHeatPusherPowered, or a src/ subclass whose
CompTickRare does not skip a Pawn: vanilla pushes from CompTick AND CompTickRare, a pawn runs both, so it heats at twice
heatPerSecond). A CompTickRare override is pawn-safe when it never calls base.CompTickRare, or when its body names Pawn
(the `if (parent is Pawn) return;` guard); one that calls base.CompTickRare without naming Pawn passes the push through
to the next override up the chain. Comps a Patches/ PatchOperationAdd puts on a src/ ThingDef by defName count as that def's comps.
Counts are printed so a lint that looked at nothing cannot pass.

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
                  "AnimalThingBase": "Normal", "BaseAnimal": "Normal",
                  # TICKERLINT_BUILDINGBASE_WIDEN_VANILLA_NEVER: vanilla 1.6 Core Buildings_Base.xml BuildingBase and
                  # Buildings_Production.xml BenchBase (ParentName BuildingBase) set no tickerType, and ThingDef.tickerType
                  # defaults to TickerType.Never (decompiled Verse/ThingDef.cs, Verse/TickerType.cs).
                  "BuildingBase": "Never", "BenchBase": "Never",
                  # LACQUERCLOAK_TICKER_REPAIR_NEVER_HIDES: Core Apparel_Various.xml ApparelBase and ApparelMakeableBase set
                  # no tickerType either; a worn thing ticks only on its own Normal (Thing.DoTick), so a CompTick on
                  # apparel needs an explicit <tickerType>Normal</tickerType>, as vanilla belts and packs carry.
                  "ApparelBase": "Never", "ApparelMakeableBase": "Never"}
PAWN_ROOTS = {"BasePawn", "BaseHumanlike", "AnimalThingBase", "BaseAnimal"}
# Pawn.Tick (decompiled 1.6, RimSage) also calls TickRare every 250 ticks, so a pawn def with tickerType Normal
# runs BOTH CompTick and CompTickRare. Every other thing runs only the one method its tickerType names.
# Known-exempt (def, comp) pairs: a thing whose ticker is Never but whose comp is driven by something else.
ALLOW = set()

# Vanilla heat pushers that push from both CompTick and CompTickRare (decompiled 1.6 Verse/CompHeatPusher.cs; Powered
# inherits both), and CompProperties_HeatPusher's default compClass.
VANILLA_HEAT_PUSHERS = {"CompHeatPusher", "CompHeatPusherPowered"}
HEAT_PROPS = "CompProperties_HeatPusher"
PATCH_DEFNAME = re.compile(r"""defName\s*=\s*["']([^"']+)["']""")

OVERRIDE = re.compile(r"override\s+void\s+(CompTick|CompTickRare|CompTickLong)\s*\(")
CLASS = re.compile(r"\bclass\s+(\w+)\s*(?:<[^>{]*>)?\s*(?::\s*([\w.<>, ]+?))?\s*(?:where\b[^{]*)?\{")
TYPEOF = re.compile(r"compClass\s*=\s*typeof\s*\(\s*([\w.]+)\s*\)")
RARE_OVERRIDE = re.compile(r"override\s+void\s+CompTickRare\s*\(\s*\)")
CALLS_BASE_RARE = re.compile(r"\bbase\s*\.\s*CompTickRare\s*\(")
NAMES_PAWN = re.compile(r"\bPawn\b")


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


def _body_at(t, pos):
    """the brace-balanced block starting at the first '{' at or after pos ('' if none)."""
    i = t.find("{", pos)
    if i < 0:
        return ""
    depth = 0
    for j in range(i, len(t)):
        if t[j] == "{":
            depth += 1
        elif t[j] == "}":
            depth -= 1
            if depth == 0:
                return t[i:j + 1]
    return t[i:]


def _rare_kind(body):
    """how a class's own CompTickRare override treats a pawn: None (no override), 'skip' (never calls base),
    'pawn' (calls base but names Pawn: the guard), 'base' (calls base, names no Pawn: passes the push through)."""
    m = RARE_OVERRIDE.search(body)
    if not m:
        return None
    mb = _body_at(body, m.end())
    if not CALLS_BASE_RARE.search(mb):
        return "skip"
    return "pawn" if NAMES_PAWN.search(mb) else "base"


def parse_cs(texts):
    """-> (bases: class -> [base simple names], ticks: class -> set(methods it overrides), comp_of: props class -> comp class,
    rare: class -> _rare_kind of its own CompTickRare override)"""
    bases, ticks, comp_of, rare = {}, {}, {}, {}
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
            k = _rare_kind(body)
            if k:
                rare[name] = k
            m = TYPEOF.search(body)
            if m:
                comp_of[name] = _simple(m.group(1))
    return bases, ticks, comp_of, rare


def rare_pawn_safe(cls, bases, rare, seen=None):
    """True if the CompTickRare a pawn runs on cls stops before vanilla's push: the nearest override up the src/ chain
    skips base or guards on Pawn. An override that only calls base defers to its own base; reaching a class with no
    src/ override (vanilla CompHeatPusher) is unsafe."""
    seen = seen or set()
    if cls in seen:
        return False
    seen.add(cls)
    k = rare.get(cls)
    if k in ("skip", "pawn"):
        return True
    return any(rare_pawn_safe(b, bases, rare, seen) for b in bases.get(cls, ()))


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


def parse_patch_comps(xml_texts):
    """-> ({defName: [(cls, compClass|None, path)]}, {defName: tickerType}) from PatchOperationAdd whose xpath names ThingDef
    defName(s) and whose value is a <comps> block (xpath ends at the def) or comp <li>s (xpath ends in /comps), and from any
    PatchOperationAdd/Replace on those defs whose value carries a <tickerType> (a patch that turns the ticker on). Other
    shapes are not read."""
    out, tick = {}, {}
    for path, text in xml_texts:
        try:
            root = ET.fromstring(text.encode("utf-8") if isinstance(text, str) else text)
        except ET.ParseError:
            continue
        for op in root.iter():
            kind = (op.get("Class") or "").split(".")[-1]
            if kind not in ("PatchOperationAdd", "PatchOperationReplace"):
                continue
            xp, val = (op.findtext("xpath") or "").strip(), op.find("value")
            if val is None or "ThingDef" not in xp:
                continue
            tt = val.findtext("tickerType")
            if tt:
                for name in PATCH_DEFNAME.findall(xp):
                    tick[name] = tt.strip()
            if kind != "PatchOperationAdd":
                continue
            if xp.endswith("/comps"):
                lis = val.findall("li")
            elif xp.endswith("]"):
                lis = [li for cn in val.findall("comps") for li in cn.findall("li")]
            else:
                continue
            for name in PATCH_DEFNAME.findall(xp):
                out.setdefault(name, []).extend((li.get("Class"), li.findtext("compClass"), path) for li in lis)
    return out, tick


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


def reaches(cls, targets, bases, seen=None):
    """True if cls is one of targets or derives from one through src/ base classes."""
    seen = seen or set()
    if cls in targets:
        return True
    if cls in seen:
        return False
    seen.add(cls)
    return any(reaches(b, targets, bases, seen) for b in bases.get(cls, ()))


def lint(cs_texts, xml_texts, patch_texts=()):
    bases, ticks, comp_of, rare = parse_cs(cs_texts)
    defs = parse_defs(xml_texts)
    patched, patched_ticker = parse_patch_comps(patch_texts)
    for d in defs:
        if d["name"] in patched:
            d["comps"] = d["comps"] + [(cls, cc) for cls, cc, _ in patched[d["name"]]]
        if d["name"] in patched_ticker:
            d["ticker"] = patched_ticker[d["name"]]
    res = resolve(defs)
    findings, c = [], dict(defs=len(res), comps=0, ticking_comps=0, unresolved_ticker=0, unresolved_comp=0,
                           patched_comps=sum(len(v) for v in patched.values()), pawn_heat_pushers=0)
    for d in res:
        if d["pawn"]:
            for cls, comp_class_xml in d["comps"]:
                if _simple(cls or "") != HEAT_PROPS:
                    continue
                c["pawn_heat_pushers"] += 1
                comp = _simple(comp_class_xml) if comp_class_xml else "CompHeatPusher"
                if comp in VANILLA_HEAT_PUSHERS:
                    why = "vanilla %s" % comp
                elif comp in bases and reaches(comp, VANILLA_HEAT_PUSHERS, bases) and not rare_pawn_safe(comp, bases, rare):
                    why = "%s (a CompHeatPusher subclass whose CompTickRare does not skip a Pawn)" % comp
                else:
                    continue
                findings.append(("PAWN_DOUBLE_PUSH", d["path"], "%s is a pawn carrying %s: it pushes from CompTick AND CompTickRare, "
                                 "so it heats at twice heatPerSecond; use a compClass that skips CompTickRare on a Pawn" % (d["name"], why)))
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
    xml, patches = [], []
    for p in _walk(src, (".xml",)):
        if os.sep + "Defs" + os.sep in p or p.endswith(os.sep + "Defs"):
            xml.append((p, open(p, encoding="utf-8-sig", errors="replace").read()))
        elif os.sep + "Patches" + os.sep in p:
            patches.append((p, open(p, encoding="utf-8-sig", errors="replace").read()))
    return cs, xml, patches


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
    hcs = [("h.cs", "class CompSafe : CompHeatPusher { public override void CompTickRare() {} } class CompGatedOnly : CompHeatPusher { }"
                    " class CompPassThru : CompHeatPusher { public override void CompTickRare() { base.CompTickRare(); } }"
                    " class CompGuard : CompHeatPusher { public override void CompTickRare() { if (parent is Pawn) { return; } base.CompTickRare(); } }"
                    " class CompGuardKid : CompGuard { } class CompGuardKidPass : CompGuard { public override void CompTickRare() { base.CompTickRare(); } }"
                    " class CompCommentOnly : CompHeatPusher { public override void CompTickRare() { /* Pawn */ base.CompTickRare(); } }")]
    hp = lambda cc: '<li Class="CompProperties_HeatPusher">%s<heatPerSecond>9</heatPerSecond></li>' % (
        "<compClass>%s</compClass>" % cc if cc else "")
    pawn = lambda li: D('<ThingDef ParentName="AnimalThingBase"><defName>H</defName><comps>%s</comps></ThingDef>' % li)
    for label, li, want in (("default class", hp(None), ["PAWN_DOUBLE_PUSH"]), ("vanilla Powered", hp("CompHeatPusherPowered"), ["PAWN_DOUBLE_PUSH"]),
                            ("subclass without CompTickRare", hp("N.CompGatedOnly"), ["PAWN_DOUBLE_PUSH"]), ("pawn-safe subclass", hp("N.CompSafe"), []),
                            ("override that only calls base", hp("N.CompPassThru"), ["PAWN_DOUBLE_PUSH"]), ("Pawn guard", hp("N.CompGuard"), []),
                            ("child of a guard", hp("N.CompGuardKid"), []), ("pass-through child of a guard", hp("N.CompGuardKidPass"), []),
                            ("Pawn only in a comment", hp("N.CompCommentOnly"), ["PAWN_DOUBLE_PUSH"])):
        f, c = lint(hcs, pawn(li))
        if [x[0] for x in f] != want or c["pawn_heat_pushers"] != 1:
            fails.append("pawn heat pusher, %s: want %r got %r %r" % (label, want, f, c))
    f, c = lint(hcs, D('<ThingDef ParentName="BuildingBase"><defName>Fire</defName><comps>%s</comps></ThingDef>' % hp(None)))
    if f or c["pawn_heat_pushers"]:
        fails.append("building with vanilla heat pusher flagged: %r" % (f,))
    patch = [("p.xml", '<Patch><Operation Class="PatchOperationSequence"><operations><li Class="PatchOperationAdd">'
                       '<xpath>Defs/ThingDef[defName="H"]</xpath><value><comps>%s</comps></value></li></operations></Operation></Patch>' % hp(None))]
    f, c = lint(hcs, D('<ThingDef ParentName="AnimalThingBase"><defName>H</defName></ThingDef>'), patch)
    if [x[0] for x in f] != ["PAWN_DOUBLE_PUSH"] or c["patched_comps"] != 1:
        fails.append("vanilla heat pusher patched onto a pawn not flagged: %r %r" % (f, c))
    tpatch = [("t.xml", '<Patch><Operation Class="PatchOperationSequence"><operations>'
                        '<li Class="PatchOperationReplace"><xpath>Defs/ThingDef[defName="B"]/tickerType</xpath><value><tickerType>Long</tickerType></value></li>'
                        '<li Class="PatchOperationAdd"><xpath>Defs/ThingDef[defName="B"]/comps</xpath><value><li Class="CompP"/></value></li>'
                        '</operations></Operation></Patch>')]
    f, c = lint(cs, D('<ThingDef><defName>B</defName><tickerType>Never</tickerType><comps/></ThingDef>'), tpatch)
    if f or c["ticking_comps"] != 1:
        fails.append("patch that sets tickerType Long and adds a Long comp flagged or unseen: %r %r" % (f, c))
    # TICKERLINT_BUILDINGBASE_WIDEN_VANILLA_NEVER: vanilla BuildingBase/BenchBase resolve to Never, not UNRESOLVED.
    for root in ("BuildingBase", "BenchBase"):
        f, c = lint(cs, D('<ThingDef ParentName="%s"><defName>W</defName><comps><li Class="CompPN"/></comps></ThingDef>' % root))
        if [x[0] for x in f] != ["NEVER_TICKER"] or c["unresolved_ticker"]:
            fails.append("%s child with a CompTick comp and no tickerType not flagged NEVER_TICKER: %r %r" % (root, f, c))
        f, c = lint(cs, D('<ThingDef ParentName="%s"><defName>W</defName><tickerType>Normal</tickerType><comps><li Class="CompPN"/></comps></ThingDef>' % root))
        if f or c["ticking_comps"] != 1:
            fails.append("%s child with tickerType Normal + CompTick comp flagged or unseen: %r %r" % (root, f, c))
    if fails:
        print("lint_ticker_compat selftest FAILED:\n  " + "\n  ".join(fails))
        return 1
    print("lint_ticker_compat selftest: 18/18 cases OK")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    cs, xml, patches = load_repo()
    findings, c = lint(cs, xml, patches)
    if not c["defs"] or not c["ticking_comps"]:
        print("lint_ticker_compat: UNMEASURED - looked at %(defs)d defs and %(ticking_comps)d ticking comps" % c)
        return 2
    if "--quiet" not in argv:
        for k, p, m in findings:
            print("ERROR %s %s: %s" % (k, os.path.relpath(p, REPO), m))
    print("lint_ticker_compat: %(defs)d concrete ThingDefs, %(comps)d comp entries, %(ticking_comps)d ticking src comps judged, "
          "%(unresolved_ticker)d defs with unresolved ticker (vanilla parent), %(unresolved_comp)d engine/non-src comps skipped, "
          "%(patched_comps)d comps added by patches, %(pawn_heat_pushers)d pawn heat pushers checked" % c
          + ", %d ERROR" % len(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
