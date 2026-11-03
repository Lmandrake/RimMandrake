#!/usr/bin/env python3
"""Every top chain in validation.py fires a plant whose ROSTER ROW carries that top (EGROWTH_TINDER_HAY_PROVE_COMES_UP_EMPTY).

    python3 src/RimMandrake/ExplosiveGrowth/selftest_explosivegrowth_top_donors.py

The 2026-10-22 northstar run read `tinder_leaves_fuel` FAIL (Hay=0): the chain fired RM_FE_Plant_Quickgrass, whose row
has been top=Churn since the 2026-10-16 C3 ruling, so RM_TopResolver never reached Burst(tinder: true). This pins
validation.TOP_DONORS to the shipped rosters: each name is a non-tree ThingDef in src/ with a roster row of exactly that
top, every _top_chain call names a TOP_DONORS key, and an empty list is allowed only while no non-tree row of that top
exists. A built-in control runs the same check on the pre-fix donor and must FAIL.

It also pins the Tinder bar's NUMBER (blind check 2026-11-02: Hay >= 1 stayed green on a plain Burst's 3-6): the
top_tinder Hay_stack predicate, evaluated over 0..30, must hold exactly on 8..14, and RM_TopResolver.cs must route
OwnTop/Tinder to Burst(tinder: true), the Burst outcome to Burst(tinder: false), and spawn 8-14 hay only when tinder,
as an unconditional statement of Burst's body. The live bar's reader, validation._stack_total, is run against a fake
bridge (it must sum stackCount and raise on a list it cannot fully see), top_tinder must feed Hay_stack from it, and the
committed DLL's .srchash must match the committed sources (the game runs the DLL, not the .cs). Every pin has a control.
"""
import re
import ast
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(REPO, "src")
VALIDATION = os.path.join(HERE, "validation.py")
RESOLVER = os.path.join(HERE, "Source", "RM_TopResolver.cs")
KERNEL = os.path.join(HERE, "Source", "Kernel", "RM_ExplosiveGrowthKernel.cs")
TOPENUM = os.path.join(HERE, "Source", "RM_GrowthTop.cs")
ROSTER_TAG = "RimMandrake.ExplosiveGrowth.RM_ExplosiveGrowthRosterDef"
fails = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


def xml_files():
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in (".git", "Textures", "Assemblies")]
        for f in files:
            if f.endswith(".xml"):
                yield os.path.join(root, f)


def load_xml():
    """-> (rows {plant: set(tops)}, thingdefs {defName: [Element]}) over every Defs XML in src/."""
    rows, defs = {}, {}
    for p in xml_files():
        try:
            with open(p, encoding="utf-8-sig") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        if ROSTER_TAG not in text and "<ThingDef" not in text:
            continue
        try:
            root = ET.fromstring(text)
        except ET.ParseError:
            continue
        if root.tag != "Defs":
            continue
        for el in root:
            if el.tag == ROSTER_TAG:
                for li in el.findall("./plants/li"):
                    plant, top = li.findtext("plant"), li.findtext("top")
                    if plant and top:
                        rows.setdefault(plant.strip(), set()).add(top.strip())
            elif el.tag == "ThingDef" and el.findtext("defName"):
                defs.setdefault(el.findtext("defName").strip(), []).append(el)
    return rows, defs


def is_tree(els):
    for el in els:
        if el.find("./plant/treeCategory") is not None or "Tree" in (el.get("ParentName") or ""):
            return True
    return False


def donor_errors(donors, rows, defs):
    """Every reason `donors` ({top: names}) is wrong against the rosters and defs; [] when right."""
    errs = []
    for top, names in donors.items():
        for n in names:
            if n not in defs:
                errs.append("%s: %s has no ThingDef in src/" % (top, n))
            elif is_tree(defs[n]):
                errs.append("%s: %s is a tree (its forced top is TreeBurst)" % (top, n))
            if rows.get(n) != {top}:
                errs.append("%s: %s's roster top is %s" % (top, n, sorted(rows.get(n, ())) or "absent"))
        if not names:
            live = [p for p, tops in rows.items() if top in tops and p in defs and not is_tree(defs[p])]
            if live:
                errs.append("%s: list is empty but non-tree rows exist: %s" % (top, ", ".join(sorted(live))))
    return errs


def parse_validation():
    tree = ast.parse(open(VALIDATION, encoding="utf-8").read())
    donors, chain_tops, literal_places = None, [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "TOP_DONORS" for x in node.targets):
            donors = ast.literal_eval(node.value)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "_top_chain" and len(node.args) >= 4:
                a = node.args[3]
                chain_tops.append(a.value if isinstance(a, ast.Constant) else ast.dump(a))
            if node.func.id in ("_place", "_top_donor") and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                literal_places.append((node.func.id, node.args[1].value, node.lineno))
    return donors, chain_tops, literal_places


def tinder_predicates():
    """-> {key: predicate} of the expect_on dict of the top_tinder _top_chain call, compiled from validation.py."""
    tree = ast.parse(open(VALIDATION, encoding="utf-8").read())
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_top_chain"
                and len(node.args) >= 7 and isinstance(node.args[3], ast.Constant) and node.args[3].value == "Tinder"):
            out = {}
            for k, v in zip(node.args[6].keys, node.args[6].values):
                lam = v.elts[0]
                out[k.value] = eval(compile(ast.Expression(lam), VALIDATION, "eval"))
            return out
    return {}


def hay_range_errors(pred):
    """Every value of 0..30 where `pred` disagrees with 'Burst(tinder: true) total hay, 8..14'; [] when exact."""
    return [v for v in range(31) if bool(pred(v)) != (8 <= v <= 14)]


def resolver_errors(cs):
    """Every reason RM_TopResolver.cs no longer sends Tinder to an 8-14 hay burst; [] when it does."""
    errs = []
    flat = re.sub(r"\s+", " ", re.sub(r"//[^\n]*", "", cs))
    if not re.search(r"case RM_GrowthTop\.Tinder: Burst\(plant, prof, comp, tinder: true\); break;", flat):
        errs.append("OwnTop/Tinder does not call Burst(..., tinder: true)")
    if not re.search(r"RM_GrowthTop top = Effective\(prof\.top\);", flat) or \
            not re.search(r"ResolveOutcome\(prof\.archetype, \(byte\)top,", flat) or \
            not re.search(r"Effective\(RM_GrowthTop top\) \{ return \(RM_GrowthTop\)RM_ExplosiveGrowthKernel\.EffectiveTop\("
                          r"\(byte\)top, ExplosiveGrowthSettings\.burstEnabled, ExplosiveGrowthSettings\.tinderEnabled,", flat):
        errs.append("Fire does not feed the row's own top through Effective/EffectiveTop(top, burst, tinder, ...) "
                    "into ResolveOutcome")
    if not re.search(r"case RM_Outcome\.OwnTop: switch \(top\) \{[^{}]*?case RM_GrowthTop\.Tinder: "
                       r"Burst\(plant, prof, comp, tinder: true\); break;[^{}]*\} break;", flat):
        errs.append("the Tinder case is not inside 'case RM_Outcome.OwnTop: switch (top) { ... } break;'")
    if not re.search(r"case RM_Outcome\.Burst: Burst\(plant, prof, comp, tinder: false\); break;", flat):
        errs.append("the Burst outcome does not call Burst(..., tinder: false)")
    if not re.search(r"SpawnNear\(ThingDefOf\.Hay, tinder \? Rand\.RangeInclusive\(8, 14\) : Rand\.RangeInclusive\(3, 6\)", flat):
        errs.append("Burst's hay is not 'tinder ? 8-14 : 3-6'")
    errs += burst_body_errors(flat)
    if flat.count("ThingDefOf.Hay") != 1 or re.search(r"\bHay\b", flat.replace("ThingDefOf.Hay", "")):
        errs.append("RM_TopResolver.cs makes hay somewhere besides Burst's one spawn (e.g. in DropProduce)")
    # SpawnNear must place exactly `count` (stacks of at most stackLimit, until none is left)
    if not re.search(r"private static void SpawnNear\(ThingDef def, int count, IntVec3 at, Map map\) \{ while \(count > 0\) "
                     r"\{ Thing t = ThingMaker\.MakeThing\(def\); t\.stackCount = Mathf\.Min\(count, def\.stackLimit\); "
                     r"count -= t\.stackCount; GenPlace\.TryPlaceThing\(t, at, map, ThingPlaceMode\.Near\); \} \}", flat):
        errs.append("SpawnNear no longer places exactly `count` of def")
    return errs


def kernel_errors(kernel, enum):
    """Every reason the kernel no longer takes an enabled Tinder (=3) to RM_Outcome.OwnTop; [] when it does."""
    errs = []
    flat = re.sub(r"\s+", " ", re.sub(r"//[^\n]*", "", kernel))
    if not re.search(r"\bTinder = 3,", re.sub(r"//[^\n]*", "", enum)):
        errs.append("RM_GrowthTop.Tinder is not 3")
    if not re.search(r"case 3: return tinder \? top : fallback;", flat):
        errs.append("EffectiveTop does not keep an enabled Tinder (case 3: return tinder ? top : fallback;)")
    m = re.search(r"public static RM_Outcome ResolveOutcome\([^)]*\) \{(.*?)return RM_Outcome\.OwnTop;", flat)
    if not m:
        return errs + ["ResolveOutcome has no OwnTop return"]
    body = m.group(1)
    head, _, cond = body.rpartition("if (")
    if not re.fullmatch(r"(?:top == \d \|\| )*top == \d\) ", cond) or "top == 3" not in cond:
        errs.append("the OwnTop return's condition does not take top == 3: %r" % cond)
    pre = [x.strip() for x in head.split(";") if x.strip()]
    if pre != ["if (top == 6) return RM_Outcome.None", "if (nativeCrop && cropSelfFruit) return RM_Outcome.SelfFruit"]:
        errs.append("ResolveOutcome can return before OwnTop on other paths: %r" % pre)
    return errs


def committed_errors(paths):
    """Every C# file read here whose worktree text is not its HEAD blob: the DLL stamp is checked at HEAD, so the
    source the regexes read must be that same commit's."""
    import subprocess
    errs = []
    for p in paths:
        rel = os.path.relpath(p, REPO).replace(os.sep, "/")
        r = subprocess.run(["git", "-C", REPO, "show", "HEAD:" + rel], capture_output=True, timeout=30)
        if r.returncode != 0 or r.stdout != open(p, "rb").read():
            errs.append(rel)
    return errs


HAY_CALL = "SpawnNear(ThingDefOf.Hay,"


def burst_body_errors(flat):
    """The hay spawn must RUN on every Burst: a statement at the method body's own level (brace depth 1, not the
    unbraced arm of an if/for/else), with no return before it (GPT review 2026-11-02: text presence is not execution)."""
    m = re.search(r"private static void Burst\(Plant plant, RM_PlantProfile prof, RM_MapComponent_ExplosiveGrowth comp, "
                  r"bool tinder\) \{", flat)
    if not m:
        return ["Burst(Plant, RM_PlantProfile, comp, bool tinder) not found"]
    i = flat.find(HAY_CALL, m.end())
    if i < 0:
        return ["Burst has no hay SpawnNear"]
    pre = flat[m.end():i]
    depth = 1 + pre.count("{") - pre.count("}")
    errs = []
    if depth != 1:
        errs.append("the hay spawn sits inside a block (depth %d)" % depth)
    if pre.count("{") != pre.count("}") or depth < 1:
        errs.append("Burst closes before its hay spawn")
    last = pre.rstrip()[-1:] if pre.strip() else "{"
    if last not in (";", "{", "}"):
        errs.append("the hay spawn is the unbraced arm of a statement (preceded by %r)" % pre.rstrip()[-20:])
    if re.search(r"\breturn\b|\bgoto\b|\bthrow\b", pre):
        errs.append("Burst can leave before its hay spawn")
    if re.search(r"\btinder\s*(?:[-+*/%&|^]?=(?!=)|\+\+|--)|\b(?:ref|out)\s+tinder\b", pre):
        errs.append("Burst reassigns tinder before its hay spawn")
    nxt = re.search(r"\b(?:private|public|internal|protected) static ", flat[m.end():])
    whole = flat[m.end():m.end() + nxt.start()] if nxt else flat[m.end():]
    if whole.count("ThingDefOf.Hay") != 1:
        errs.append("Burst names ThingDefOf.Hay %d times (exactly one spawn of 8-14)" % whole.count("ThingDefOf.Hay"))
    return errs


class _FakeT:
    """The least of a northstar `t` that validation._stack_total / _count read: a live session and one canned reply."""
    def __init__(self, reply):
        self.session, self.upstream_failed, self.reply, self.calls = object(), False, reply, []

    def bridge_call(self, tool, **kw):
        self.calls.append((tool, kw))
        return self.reply if tool == "jawa/list_things" else {"success": False, "error": "no such tool %s" % tool}


def _hay_reply(stacks, complete=True):
    return {"success": True, "scanned": 100, "isCompleteList": complete, "countMatched": len(stacks),
            "things": [{"id": "Hay%d" % i, "stackCount": s} for i, s in enumerate(stacks)]}


def stack_total_errors(fn, failed_exc):
    """Every way `fn(t, defName, rect)` is not 'sum of stackCount, loud on an unreadable list'; [] when it is."""
    errs = []
    for stacks, want in (([11], 11), ([5, 3], 8), ([14], 14), ([4], 4), ([], 0)):
        t = _FakeT(_hay_reply(stacks))
        try:
            got = fn(t, "Hay", "0,0,10,10")
        except Exception as e:      # noqa: BLE001 - any raise on a readable list is a defect
            errs.append("%r raised %r" % (stacks, e))
            continue
        if got != want:
            errs.append("%r read %r, want %d" % (stacks, got, want))
        if not t.calls or t.calls[0][0] != "jawa/list_things" or t.calls[0][1].get("rect") != "0,0,10,10" \
                or t.calls[0][1].get("defName") != "Hay":
            errs.append("%r: did not read Hay over the given rect: %r" % (stacks, t.calls))
    for label, reply in (("incomplete list", _hay_reply([11], complete=False)),
                         ("scanned 0", dict(_hay_reply([11]), scanned=0)),
                         ("stackCount missing", dict(_hay_reply([11]), things=[{"id": "Hay0"}])),
                         ("failed call", {"success": False})):
        try:
            got = fn(_FakeT(reply), "Hay", "0,0,10,10")
            errs.append("%s read %r instead of raising" % (label, got))
        except failed_exc:
            pass
        except Exception as e:      # noqa: BLE001
            errs.append("%s raised %r, not ExpectationFailed" % (label, e))
    return errs


def tinder_obs_errors(src):
    """Every reason top_tinder's observer no longer feeds Hay_stack from _stack_total over the 10x10 Hay rect."""
    m = re.search(r'@suite\.chain\("top_tinder"\)\s*\ndef top_tinder\(t\):(.*?)(?=\n@suite\.chain|\Z)', src, re.S)
    body = m.group(1) if m and m.group(1) else ""
    errs = []
    if not body:
        errs.append("top_tinder chain not found")
    if not re.search(r'o\["Hay_stack"\]\s*=\s*_stack_total\(t,\s*"Hay",\s*"%d,%d,10,10"\s*%\s*\(x - 5, z - 5\)\)', body):
        errs.append('observer does not set o["Hay_stack"] = _stack_total(t, "Hay", <10x10 around the plant>)')
    # that read must be what reaches the predicate: the one write to the key, and nothing else touches o after it
    writes = re.findall(r'o\[\s*["\']Hay_stack["\']\s*\]', body)
    binds = re.findall(r"(?m)^\s*o\s*(?:\|=|=(?!=))", body)     # the one `o = _obs_common(...)` only
    if len(writes) != 1 or len(binds) != 1 or re.search(r"\bo\.(update|setdefault|__setitem__)\b", body):
        errs.append("Hay_stack is written %d time(s) or o is rebound/updated in the observer" % len(writes))
    tail = body[body.find('o["Hay_stack"]'):] if writes else ""
    if not re.match(r'o\["Hay_stack"\] = _stack_total\([^\n]*\)\n\s*return o\n', tail):
        errs.append("the observer does not return o straight after the Hay_stack read")
    return errs


def stamp_errors(rev_cat):
    """-> (status, detail) of the committed ExplosiveGrowth DLL's .srchash against the committed sources at HEAD."""
    import dll_source_stamp as d   # main() puts src/RimMandrake/Utils on sys.path
    stamp = "src/RimMandrake/ExplosiveGrowth/Assemblies/RimMandrake.ExplosiveGrowth.dll.srchash"
    r = d.recompute_stamp(rev_cat, "HEAD", stamp, REPO)
    return r.status, r.detail


class _MutCat:
    """A git cat that serves one path's HEAD blob altered: a stale DLL against an edited RM_TopResolver.cs."""
    def __init__(self, real, path, fn):
        self.real, self.key, self.fn = real, "HEAD:" + path, fn

    def get(self, key):
        b = self.real.get(key)
        return self.fn(b) if key == self.key and b is not None else b


def main():
    rows, defs = load_xml()
    check("sanity: the rosters parse (rows found)", len(rows) >= 20, len(rows))
    check("sanity: ScorchFruit is a Tinder row", rows.get("RM_FE_Plant_ScorchFruit") == {"Tinder"},
          rows.get("RM_FE_Plant_ScorchFruit"))
    check("sanity: Quickgrass is a Churn row", rows.get("RM_FE_Plant_Quickgrass") == {"Churn"},
          rows.get("RM_FE_Plant_Quickgrass"))
    donors, chain_tops, literal_places = parse_validation()
    check("validation.py defines TOP_DONORS", isinstance(donors, dict), donors)
    if not isinstance(donors, dict):
        return 1
    check("TOP_DONORS covers the five own-odds tops", set(donors) == {"Burst", "Tinder", "Slime", "Rupture", "Flush"},
          sorted(donors))
    errs = donor_errors(donors, rows, defs)
    check("every TOP_DONORS name is a non-tree row of its own top", not errs, "; ".join(errs))
    check("the Tinder chain's donor is RM_FE_Plant_ScorchFruit", tuple(donors.get("Tinder", ()))[:1] == ("RM_FE_Plant_ScorchFruit",),
          donors.get("Tinder"))
    check("five _top_chain calls, each naming a TOP_DONORS key", len(chain_tops) == 5 and all(c in donors for c in chain_tops),
          chain_tops)
    placed = [p for p in literal_places if p[0] == "_place" and p[1] in rows]
    check("no chain places a hard-coded roster plant", not placed, placed)
    control = donor_errors({"Tinder": ("RM_FE_Plant_Quickgrass",)}, rows, defs)
    check("control: the pre-fix Tinder donor (Quickgrass) is refused", bool(control), control)
    preds = tinder_predicates()
    check("top_tinder's ON arm has a Hay_stack predicate", "Hay_stack" in preds, sorted(preds))
    if "Hay_stack" in preds:
        bad = hay_range_errors(preds["Hay_stack"])
        check("Hay_stack holds exactly on 8..14 (a plain Burst's 3..6 is red)", not bad, bad)
    check("control: the pre-fix predicate (Hay >= 1) is refused", bool(hay_range_errors(lambda v: v >= 1)))
    cs = open(RESOLVER, encoding="utf-8").read()
    rerr = resolver_errors(cs)
    check("RM_TopResolver sends Tinder to Burst(tinder: true), 8-14 hay", not rerr, "; ".join(rerr))
    mut = cs.replace("case RM_GrowthTop.Tinder: Burst(plant, prof, comp, tinder: true)",
                     "case RM_GrowthTop.Tinder: Burst(plant, prof, comp, tinder: false)")
    check("control: a Tinder routed to Burst(tinder: false) is refused", mut != cs and bool(resolver_errors(mut)))
    for label, a, b in (("tinder hay 8-14 -> 3-6", "tinder ? Rand.RangeInclusive(8, 14)", "tinder ? Rand.RangeInclusive(3, 6)"),
                        ("the Burst outcome -> tinder: true", "case RM_Outcome.Burst: Burst(plant, prof, comp, tinder: false)",
                         "case RM_Outcome.Burst: Burst(plant, prof, comp, tinder: true)")):
        m2 = cs.replace(a, b)
        check("control: resolver mutant '%s' is refused" % label, m2 != cs and bool(resolver_errors(m2)))
    line = "SpawnNear(ThingDefOf.Hay, tinder ? Rand.RangeInclusive(8, 14) : Rand.RangeInclusive(3, 6), c, map);"
    m6 = cs.replace("            while (count > 0)", "            count /= 2;\n            while (count > 0)", 1)
    check("control: resolver mutant 'SpawnNear halves count' is refused", m6 != cs and bool(resolver_errors(m6)))
    m7 = cs.replace("private static void SpawnNear(", "private static void Chaff(Plant p) { SpawnNear(ThingDefOf.Hay, 3, "
                    "p.Position, p.Map); }\n        private static void SpawnNear(", 1)
    check("control: resolver mutant 'a second Hay spawn outside Burst' is refused", m7 != cs and bool(resolver_errors(m7)))
    k = cs.find("{", cs.find("RM_MapComponent_ExplosiveGrowth comp, bool tinder)")) + 1
    m8 = cs[:k] + " tinder = false; " + cs[k:] if k > 0 else cs
    check("control: resolver mutant 'tinder = false at the top of Burst' is refused", m8 != cs and bool(resolver_errors(m8)))
    m5 = cs.replace(line, line + " " + line, 1)
    check("control: resolver mutant 'hay spawned twice' is refused", m5 != cs and bool(resolver_errors(m5)))
    hay = "SpawnNear(ThingDefOf.Hay, tinder ?"
    for label, b in (("hay spawn guarded by if (!tinder)", "if (!tinder) " + hay),
                     ("hay spawn inside if (!tinder) { }", "if (!tinder) { " + hay),
                     ("early return when tinder", "if (tinder) return; " + hay)):
        m2 = cs.replace(hay, b, 1)
        if "{ " + hay in b:   # close the block after the statement so the C# stays balanced
            j = m2.find(";", m2.find(hay)) + 1
            m2 = m2[:j] + " }" + m2[j:]
        check("control: resolver mutant '%s' is refused" % label, m2 != cs and bool(resolver_errors(m2)), resolver_errors(m2))

    for label, a, b in (("Fire feeds Churn, not the row's top", "RM_GrowthTop top = Effective(prof.top);",
                         "RM_GrowthTop top = Effective(RM_GrowthTop.Churn);"),
                        ("ResolveOutcome gets prof.top raw", "ResolveOutcome(prof.archetype, (byte)top,",
                         "ResolveOutcome(prof.archetype, (byte)prof.top,"),
                        ("Effective swaps the burst/tinder switches",
                         "ExplosiveGrowthSettings.burstEnabled, ExplosiveGrowthSettings.tinderEnabled,",
                         "ExplosiveGrowthSettings.tinderEnabled, ExplosiveGrowthSettings.burstEnabled,")):
        m4 = cs.replace(a, b)
        check("control: resolver mutant '%s' is refused" % label, m4 != cs and bool(resolver_errors(m4)))
    m3 = cs.replace("case RM_Outcome.OwnTop:", "case RM_Outcome.None:")
    check("control: the Tinder switch moved out of OwnTop is refused", m3 != cs and bool(resolver_errors(m3)))
    kcs, ecs = open(KERNEL, encoding="utf-8").read(), open(TOPENUM, encoding="utf-8").read()
    kerr = kernel_errors(kcs, ecs)
    check("the kernel takes an enabled Tinder (3) straight to OwnTop", not kerr, "; ".join(kerr))
    for label, k2, e2 in (("OwnTop drops top == 3", kcs.replace("top == 2 || top == 3 ||", "top == 2 ||"), ecs),
                          ("EffectiveTop drops an enabled Tinder", kcs.replace("case 3: return tinder ? top : fallback;",
                                                                              "case 3: return fallback;"), ecs),
                          ("a Burst roll before OwnTop", kcs.replace("if (top == 2 || top == 3",
                                                                    "if (roll < 0.5f) return RM_Outcome.Burst; if (top == 2 || top == 3"), ecs),
                          ("Tinder renumbered", kcs, ecs.replace("Tinder = 3,", "Tinder = 7,"))):
        check("control: kernel mutant '%s' is refused" % label, (k2, e2) != (kcs, ecs) and bool(kernel_errors(k2, e2)))
    cerr = committed_errors([RESOLVER, KERNEL, TOPENUM])
    check("the C# read here is HEAD's (the commit whose DLL stamp is checked)", not cerr, cerr)

    # the live bar reads Hay_stack through validation._stack_total: pin that it sums stackCount (one 8-14 stack must
    # not read 1, which _count / countMatched would) and is loud on a list it cannot fully see
    sys.path.insert(0, HERE)
    import validation as V
    serr = stack_total_errors(V._stack_total, V.ExpectationFailed)
    check("validation._stack_total sums stackCount over the rect and raises on an unreadable list", not serr, "; ".join(serr))
    check("control: a countMatched reader (validation._count) is refused as a stack total",
          bool(stack_total_errors(lambda t, d, r: V._count(t, d, r), V.ExpectationFailed)))
    def no_complete(t, d, r):    # the real reader with ONLY the isCompleteList test dropped
        x = V._ok(t.bridge_call("jawa/list_things", defName=d, rect=r, limit=200), "list_things")
        if not x.get("scanned"):
            V._fail("scanned 0")
        if any(not isinstance(y.get("stackCount"), int) for y in x.get("things") or []):
            V._fail("no stackCount")
        return sum(y["stackCount"] for y in x.get("things") or [])
    nc = stack_total_errors(no_complete, V.ExpectationFailed)
    check("control: a total that ignores only isCompleteList is refused, on that case alone",
          len(nc) == 1 and nc[0].startswith("incomplete list"), nc)
    vsrc = open(VALIDATION, encoding="utf-8").read()
    oerr = tinder_obs_errors(vsrc)
    check("top_tinder feeds Hay_stack from _stack_total over the 10x10 around the plant", not oerr, "; ".join(oerr))
    om = vsrc.replace('o["Hay_stack"] = _stack_total(t, "Hay"', 'o["Hay_stack"] = _count(t, "Hay"')
    check("control: a Hay_stack fed by _count is refused", om != vsrc and bool(tinder_obs_errors(om)))
    hs = 'o["Hay_stack"] = _stack_total(t, "Hay", "%d,%d,10,10" % (x - 5, z - 5))'
    for label, b in (("a constant written after the read", hs + '\n        o["Hay_stack"] = 11'),
                     ("o rebound after the read", hs + "\n        o = dict(o, Hay_stack=11)")):
        om = vsrc.replace(hs, b)
        check("control: top_tinder observer mutant '%s' is refused" % label, om != vsrc and bool(tinder_obs_errors(om)))

    # the game runs the committed DLL, not RM_TopResolver.cs: its .srchash must match the committed Source/
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    import dll_source_stamp as D
    cat = D.BatchCat(REPO)
    try:
        st, det = stamp_errors(cat)
        check("the committed ExplosiveGrowth DLL is built from the committed Source/ (srchash MATCH)", st == "MATCH",
              "%s %s" % (st, det))
        stamp_txt = open(os.path.join(HERE, "Assemblies", "RimMandrake.ExplosiveGrowth.dll.srchash"), encoding="utf-8").read()
        check("the DLL stamp covers Source/RM_TopResolver.cs", "RM_TopResolver.cs" in stamp_txt)
        rpath = "src/RimMandrake/ExplosiveGrowth/Source/RM_TopResolver.cs"
        mst, _ = stamp_errors(_MutCat(cat, rpath, lambda b: b.replace(b"RangeInclusive(8, 14)", b"RangeInclusive(3, 6)")))
        check("control: an RM_TopResolver.cs edited without a rebuild reads MISMATCH", mst == "MISMATCH", mst)
    finally:
        cat.close()
    print("%d check(s) failed" % len(fails) if fails else "ALL PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
