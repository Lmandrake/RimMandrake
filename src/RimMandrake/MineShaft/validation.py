"""validation.py -- first script for Mandrake Mine Shaft (mandrake.rm.mineshaft).

Our replacement for Mines 2.0 (Cain.Mineshaft), design/RimMandrake/mines_mod_assessment_20261011.md. NEVER RUN LIVE YET:
every live shape that is absent reads UNMEASURED, never PASS.

OFFLINE (no game): `python3 src/RimMandrake/MineShaft/validation.py`
  * static_checks(): defs parse, settings defaults in the C# match this script and are Scribed, every .cs is in the csproj,
    a DLL is built, About.xml declares no dependency, the base policy bars components, the Armoury canon policy is guarded.
  * replay(): runs the generator's rule (MineShaftRecipes.Generate) over the newest DefDump capture: which bills the shaft
    would make, and that no barred product (base + canon policy) is among them. SANITY probes: steel and gold bills must
    appear, or "nothing barred got through" means nothing.
LIVE (modcheck): defs_resolve, bills (generated recipes exist, barred ones do not), settings_roundtrip.
UNMEASURED: the vein rule's per-map answer (no bridge tool reads RecipeWorker.AvailableOnNow; first poke below).
First poke for the vein rule: on a quicktest map, spawn RM_MineShaft, `jawa/list_bills`-style read of the bill menu if a tool
exists, else open the bills tab and screenshot: a map with no gold rock and no gold deep deposit must not offer "mine for gold".
"""
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SETTINGS_TYPE = "RimMandrake.MineShaft.MineShaftSettings"
MOD_CS = os.path.join(HERE, "Source", "MineShaftMod.cs")
KERNEL_CS = os.path.join(HERE, "Source", "Kernel", "RM_MineShaftKernel.cs")
CSPROJ = os.path.join(HERE, "Source", "RM_MineShaft.csproj")
BASE_POLICY = os.path.join(HERE, "Defs", "MineShaftPolicies", "RM_MineShaftPolicy_Base.xml")
CANON_POLICY = os.path.join(REPO, "src", "RimStarWars", "Armoury", "Defs", "ThingDefs", "RSW_MineShaftCanonPolicy.xml")
WALK = os.path.join(REPO, "design", "validation_walks", "RimMandrake", "MineShaft.md")
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
from game_paths import LOCALLOW  # noqa: E402  (the one-path seam: never a LocalLow literal here)
CAPTURES = os.path.join(LOCALLOW, "DefDump", "captures")
POLICY_TAG = "RimMandrake.MineShaft.MineShaftPolicyDef"
PREFIX = "RM_MineShaft_"

DEFAULTS = {"shaftBills": True, "onlyMapVeins": True, "stoneBills": True, "yieldMultiplier": 1.0, "workMultiplier": 1.0}
ALT = {"shaftBills": False, "onlyMapVeins": False, "stoneBills": False, "yieldMultiplier": 2.0, "workMultiplier": 0.5}
DEFS = ["ThingDef/RM_MineShaft", "ResearchProjectDef/RM_Research_MineShaft", "WorkGiverDef/RM_DoBillsMineShaft",
        "RimMandrake.MineShaft.MineShaftPolicyDef/RM_MineShaftPolicy_Base"]
CONTROL_ABSENT = "ThingDef/RM_MineShaft_NoSuchDef_Control"
MUST_BILL = ("MineableSteel", "MineableGold")          # sanity: the rule must be able to make a bill
BARRED_ROCKS = ("MineableComponentsIndustrial", "MineablePlasteel")   # vanilla rocks whose products are barred


def _cs(path):
    return re.sub(r"//[^\n]*", "", open(path, encoding="utf-8").read())


def settings_from_cs():
    body = _cs(MOD_CS).split("class MineShaftSettings", 1)[1].split("public override void ExposeData", 1)[0]
    return {m.group(2): (m.group(1), m.group(3).strip())
            for m in re.finditer(r"public\s+static\s+(bool|float|int)\s+(\w+)\s*=\s*([^;]+);", body)}


def _literal(kind, raw):
    return raw == "true" if kind == "bool" else (float(raw.rstrip("f")) if kind == "float" else int(raw))


def policy_products(path):
    root = ET.parse(path).getroot()
    return [li.text for p in root if p.tag == POLICY_TAG for li in p.findall("bannedProducts/li")]


def static_checks():
    bad = []
    cs = settings_from_cs()
    if not cs:
        return ["settings regex found 0 fields in MineShaftMod.cs: the probe is blind"]
    for f, (kind, raw) in cs.items():
        if f not in DEFAULTS:
            bad.append("C# settings field %s is not in DEFAULTS" % f)
        elif _literal(kind, raw) != DEFAULTS[f]:
            bad.append("default drift on %s: C# %s vs script %r" % (f, raw, DEFAULTS[f]))
    mod = open(MOD_CS, encoding="utf-8").read()
    for f in DEFAULTS:
        if f not in cs:
            bad.append("DEFAULTS field %s is gone from the C#" % f)
        if not re.search(r'Scribe_Values\.Look\(ref %s, "%s", %s' % (f, f, str(DEFAULTS[f]).lower() if isinstance(DEFAULTS[f], bool) else r"1f"), mod):
            bad.append("settings field %s is not Scribed with its default" % f)
        if ALT[f] == DEFAULTS[f]:
            bad.append("ALT for %s equals its default" % f)
    proj = open(CSPROJ, encoding="utf-8").read()
    for dp, _, fns in os.walk(os.path.join(HERE, "Source")):
        if "SelfTest" in dp or os.sep + "obj" in dp or os.sep + "bin" in dp:
            continue
        for fn in fns:
            if fn.endswith(".cs"):
                rel = os.path.relpath(os.path.join(dp, fn), os.path.join(HERE, "Source")).replace("/", "\\")
                if 'Compile Include="%s"' % rel not in proj:
                    bad.append("%s is not in the csproj (compiles into nothing)" % rel)
    if not os.path.isfile(os.path.join(HERE, "Assemblies", "RimMandrake.MineShaft.dll")):
        bad.append("no DLL in Assemblies")
    about = ET.parse(os.path.join(HERE, "About", "About.xml")).getroot()
    if about.findtext("packageId") != "mandrake.rm.mineshaft":
        bad.append("packageId is %r" % about.findtext("packageId"))
    if about.find("modDependencies") is not None and len(about.find("modDependencies")):
        bad.append("About.xml declares a dependency; the shaft must stand alone")
    code = _cs(MOD_CS) + _cs(KERNEL_CS)          # comments stripped: the header may name the donor it replaces
    if "Cain.Mineshaft" in code or "MinesAutomated" in code:
        bad.append("the C# names the donor (Mines 2.0): no donor dependency allowed")
    root = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_MineShaft.xml")).getroot()
    got = {(e.tag, e.findtext("defName")) for e in root}
    for want in [("ThingDef", "RM_MineShaft"), ("ResearchProjectDef", "RM_Research_MineShaft"), ("WorkGiverDef", "RM_DoBillsMineShaft")]:
        if want not in got:
            bad.append("def missing: %s/%s" % want)
    shaft = [e for e in root if e.findtext("defName") == "RM_MineShaft"][0]
    if [li.text for li in shaft.findall("researchPrerequisites/li")] != ["RM_Research_MineShaft"]:
        bad.append("the shaft is not gated by RM_Research_MineShaft")
    wg = [e for e in root if e.findtext("defName") == "RM_DoBillsMineShaft"][0]
    if wg.findtext("workType") != "Mining" or [li.text for li in wg.findall("fixedBillGiverDefs/li")] != ["RM_MineShaft"]:
        bad.append("the work giver does not give Mining work at RM_MineShaft")
    base = policy_products(BASE_POLICY)
    for p in ("ComponentIndustrial", "ComponentSpacer"):
        if p not in base:
            bad.append("base policy does not bar %s" % p)
    if not os.path.isfile(CANON_POLICY):
        bad.append("Armoury canon policy missing: %s" % CANON_POLICY)
    else:
        croot = ET.parse(CANON_POLICY).getroot()
        for p in croot:
            if p.tag == POLICY_TAG and p.get("MayRequire") != "mandrake.rm.mineshaft":
                bad.append("canon policy def is not guarded by MayRequire=\"mandrake.rm.mineshaft\"")
        kern = open(os.path.join(REPO, "src", "RimStarWars", "Armoury", "Source", "Kernel", "RSW_ArmouryKernel.cs"), encoding="utf-8").read()
        m = re.search(r"MineShaftBanned\s*=\s*\{([^}]*)\}", kern)
        gate = re.findall(r'"([^"]+)"', m.group(1)) if m else []
        if not gate:
            bad.append("could not read RSW_MaterialsKernel.MineShaftBanned (the Mines 2.0 gate) to cross-check")
        for p in gate:
            if p not in policy_products(CANON_POLICY):
                bad.append("canon policy lacks %s, which the Mines 2.0 gate bars" % p)
    if os.path.isfile(WALK):
        w = open(WALK, encoding="utf-8").read().split("## must be true", 1)[-1].split("\n## ", 1)[0]
        for ln in w.splitlines():
            if ln.startswith("- ") and "→" not in ln:
                bad.append("walk line has no coverage arrow: %s" % ln[:70])
    else:
        bad.append("walk missing: %s" % WALK)
    return bad


def replay(capdir=None):
    """(problems, info): the generator's rule over the newest DefDump capture."""
    if capdir is None:
        caps = sorted(glob.glob(os.path.join(CAPTURES, "*", "defs")))
        if not caps:
            return ["UNMEASURED: no DefDump capture"], []
        capdir = caps[-1]
    T = json.load(open(os.path.join(capdir, "ThingDef.json"), encoding="utf-8"))["defs"]
    by = {t["defName"]: t for t in T}
    banned = set(policy_products(BASE_POLICY)) | set(policy_products(CANON_POLICY))
    rocks = []
    for t in T:
        f = t.get("fields") or {}
        b = f.get("building") or {}
        if not f.get("mineable") or not b.get("mineableThing"):
            continue
        res, nat = bool(b.get("isResourceRock")), bool(b.get("isNaturalRock"))
        if not (res or (DEFAULTS["stoneBills"] and nat)):
            continue
        hp = 0
        rocks.append((0 if res else 1, 0 if (b.get("mineableScatterCommonality") or 0) > 0 else 1,
                      -(b.get("mineableScatterCommonality") or 0), hp, t["defName"], b["mineableThing"]))
    rocks.sort()
    bills, covered, barred = {}, set(), []
    for _, _, _, _, rock, product in rocks:
        if product in banned:
            barred.append(rock)
            continue
        if product in covered:
            continue
        covered.add(product)
        bills[PREFIX + rock] = product
    bad, info = [], []
    if not rocks:
        return ["SANITY: no mineable rock read from the capture (field names changed?)"], info
    for r in MUST_BILL:
        if PREFIX + r not in bills:
            bad.append("SANITY: no bill for %s (the rule cannot make the bills it must)" % r)
    for r in BARRED_ROCKS:
        if PREFIX + r in bills:
            bad.append("barred rock %s still gets a bill" % r)
    leak = sorted(n for n, p in bills.items() if p in banned)
    if leak:
        bad.append("bills for barred products: %s" % leak)
    unknown = sorted(p for p in banned if p not in by)
    info.append("capture %s: %d eligible rock(s), %d bill(s), %d rock(s) barred by policy (%s); barred names absent from "
                "this capture: %s" % (os.path.basename(os.path.dirname(capdir)), len(rocks), len(bills), len(barred),
                                      ", ".join(sorted(barred)), unknown or "none"))
    return bad, info


def _build_suite():
    from modcheck import Suite, ExpectationFailed
    suite = Suite("MineShaft")
    suite.toggles = ["shaftBills", "onlyMapVeins", "stoneBills"]

    def _live(t):
        return t.session is not None

    def _same(got, want):
        if isinstance(want, bool):
            return str(got).strip().lower() == str(want).lower()
        try:
            return abs(float(got) - float(want)) < 1e-6
        except (TypeError, ValueError):
            return False

    def _defs(t, defs):
        r = t.bridge_call("jawa/get_defs", defs=";".join(defs), limit=50)
        if not isinstance(r, dict) or r.get("success") is False:
            raise ExpectationFailed("get_defs could not ask: %r" % (r,))
        return r

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("defs_resolve", beyond_toggle=True):
            if not _live(t):
                return
            r = _defs(t, DEFS)
            if r.get("notFound") or int(r.get("foundCount", 0)) != len(DEFS):
                raise ExpectationFailed("shipped defs did not resolve: found %r notFound %r" % (r.get("foundCount"), r.get("notFound")))
        with t.component("probe_can_say_absent", beyond_toggle=True):
            if not _live(t):
                return
            r = _defs(t, [CONTROL_ABSENT])
            if int(r.get("foundCount", 0)) != 0:
                raise ExpectationFailed("control: a def that does not exist did not read absent: %r" % (r,))

    @suite.chain("bills")
    def bills(t):
        with t.component("bills_generated", beyond_toggle=True):
            if not _live(t):
                return
            want = ["RecipeDef/%s%s" % (PREFIX, r) for r in MUST_BILL]
            r = _defs(t, want)
            if r.get("notFound") or int(r.get("foundCount", 0)) != len(want):
                raise ExpectationFailed("generated bills missing: %r" % (r.get("notFound"),))
        with t.component("barred_not_generated", beyond_toggle=True):
            if not _live(t):
                return
            want = ["RecipeDef/%s%s" % (PREFIX, r) for r in BARRED_ROCKS]
            r = _defs(t, want)
            if int(r.get("foundCount", 0)) != 0:
                raise ExpectationFailed("a barred product got a bill: %r" % (r.get("defs"),))
        with t.component("vein_rule", toggle="onlyMapVeins"):
            if not _live(t):
                return
            t.upstream_reason = "UNMEASURED: no bridge tool reads RecipeWorker.AvailableOnNow (see the module docstring's first poke)"
            t.upstream_failed = True

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        for field in sorted(DEFAULTS):
            with t.component("%s_roundtrip" % field, beyond_toggle=True):
                if not _live(t):
                    continue
                get = lambda: (t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="get", field=field) or {}).get("value")
                try:
                    if not _same(get(), DEFAULTS[field]):
                        raise ExpectationFailed("%s does not read its default %r: %r" % (field, DEFAULTS[field], get()))
                    t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="set", field=field, value=str(ALT[field]))
                    if not _same(get(), ALT[field]):
                        raise ExpectationFailed("%s write did not take" % field)
                finally:
                    if t.session is not None:
                        t.session.call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="set", field=field, value=str(DEFAULTS[field]))
    return suite


try:
    suite = _build_suite()
except ImportError:
    suite = None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    rp, info = replay()
    for i in info:
        print("REPLAY: " + i)
    print("REPLAY: %s" % ("PASS" if not rp else "FAIL"))
    for p in rp:
        print("  - " + p)
    sys.exit(1 if (problems or rp) else 0)
