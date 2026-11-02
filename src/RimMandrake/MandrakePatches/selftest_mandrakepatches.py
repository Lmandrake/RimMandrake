"""selftest_mandrakepatches.py -- every_fix_is_guarded_static is green on the shipped Patches/ and reddens on
each break it exists to catch (planted in a temp copy, never the shipped files)."""
import importlib.util
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def anima_check():
    """AnimaTree_NoRandomSpawn.xml: the two removals leave no random anima-tree route in Core's own XML
    (skipped, not failed, where the game install is not readable)."""
    try:
        from lxml import etree
    except ImportError:
        print("skip  anima: lxml missing")
        return
    core = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/Core/Defs"
    pairs = [("MapGeneration/BasePlayerMapGenerator.xml", "/Defs/MapGeneratorDef[defName='Base_Player']/genSteps/li[text()='AnimaTrees']"),
             ("Storyteller/Storytellers.xml", "/Defs/StorytellerDef/comps/li[incident='AnimaTreeSpawn']")]
    patch = etree.parse(os.path.join(HERE, "Patches", "AnimaTree_NoRandomSpawn.xml"))
    xps = [x.text.replace('"', "'") for x in patch.iterfind(".//match/xpath")]
    check("anima patch carries both removals", xps == [p[1] for p in pairs], xps)
    for fn, xp in pairs:
        path = os.path.join(core, fn)
        if not os.path.exists(path):
            print("skip  anima: %s not readable" % fn)
            continue
        doc = etree.parse(path)
        before = doc.xpath(xp)
        for n in before:
            n.getparent().remove(n)
        check("anima: %s has the route before and none after" % fn, len(before) >= 1 and doc.xpath(xp) == [], len(before))


def ghost_target_ops(patch_dir):
    """[(file, xpath)] for leaf ops aimed at a MOD-namespaced def class (/Defs/Ns.Class[...]) that are NOT under a
    FindMod ancestor. A Conditional alone does not guard a nomatch Add: the target def is absent when the mod is,
    so the Add matches nothing and logs a red failure on every load (FACE_PATCH_FIX_ADDS_TO_A_GHOST)."""
    import re
    import xml.etree.ElementTree as ET
    out = []

    def walk(e, fn, under_findmod):
        c = (e.get("Class") or "").replace("PatchOperation", "")
        if c in ("Add", "Replace", "Remove", "AddModExtension", "Insert", "SetName"):
            xp = (e.findtext("xpath") or "").strip()
            if re.match(r"^/?Defs/[A-Za-z_]\w*\.\w+", xp) and not under_findmod:
                out.append((fn, xp))
            return
        guard = under_findmod or c == "FindMod"
        for k in ("match", "nomatch"):
            for x in e.findall(k):
                walk(x, fn, guard)
        for li in e.findall("operations/li"):
            walk(li, fn, guard)

    for fn in sorted(os.listdir(patch_dir)):
        if fn.endswith(".xml"):
            for op in ET.parse(os.path.join(patch_dir, fn)).getroot().findall("Operation"):
                walk(op, fn, False)
    return out


# CAI_FOG_SILENCE_FORCED_OFF_BY_US: every CAI 5000 member CaiFogOff.cs binds by name (const name -> member string).
CAI_MEMBERS = {"FinderType": "CombatAI.Finder", "ModType": "CombatAI.CombatAIMod", "FinderSettingsField": "Settings",
               "FinderModField": "Mod", "FogField": "FogOfWar_Enabled", "SightField": "NewSightSystem_Enabled",
               "PrevFogField": "prevFogEnabled", "WriteSettingsMethod": "WriteSettings"}
CAI_DLL = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3673768803/1.6/Assemblies/CombatAI.dll"


# Force()'s if-conditions, in order. Pinned exactly: a flipped guard (e.g. the toggle polarity) keeps every
# SetValue text in place yet stops the forcing, so text presence alone cannot see it.
FORCE_IFS = ["!bound",
             "!RM_PatchesSettings.caiFogForcedOff",
             "settings == null",
             "sight != null && sight.FieldType == typeof(bool)",
             'why != "CAI settings saved" && prevFog != null && prevFog.FieldType == typeof(bool) && Current.Game == null',
             "mod != null",
             "was"]


def force_flow_problems(src):
    """[problem] for the body of CaiFogOff.Force: exact guard list, early returns, and the write after the toggle guard."""
    import re
    m = re.search(r"public static bool Force\(string why\)\s*\{", src)
    if not m:
        return ["no `public static bool Force(string why)`"]
    depth, i = 1, m.end()
    while depth and i < len(src):
        depth += {"{": 1, "}": -1}.get(src[i], 0)
        i += 1
    body = src[m.end():i - 1]
    code = re.sub(r"//[^\n]*", "", body)
    out = []
    ifs = [c.strip() for c in re.findall(r"\bif \((.*)\)\s*(?:\{|[A-Za-z_])", code)]
    if ifs != FORCE_IFS:
        out.append("Force() if-conditions %r != FORCE_IFS" % ifs)
    if not re.search(r"if \(!bound\) return false;", code):
        out.append("Force(): `if (!bound) return false;` changed")
    g = re.search(r"if \(!RM_PatchesSettings\.caiFogForcedOff\)\s*\{[^{}]*return false;\s*\}", code)
    if not g:
        out.append("Force(): the toggle guard is not `if (!RM_PatchesSettings.caiFogForcedOff) { ... return false; }`")
    w = code.find("fog.SetValue(settings, false);")
    if w < 0 or (g and w < g.end()):
        out.append("Force(): fog.SetValue(settings, false) is missing or not after the toggle guard")
    elif code[:w].rsplit("\n", 1)[-1].strip() or re.search(r"\{[^{}]*$", code[g.end() if g else 0:w]):
        out.append("Force(): fog.SetValue(settings, false) sits inside a conditional")
    if not re.search(r"fog\.SetValue\(settings, false\);[\s\S]*return true;\s*$", code):
        out.append("Force() does not end `return true;` after the write")
    return out


def cai_fog_problems(src, mod_src, about, srchash, cs_bytes):
    """[problem] for the CAI fog forcer: constants, the forcing writes, the default-on setting, About, and the DLL stamp.
    Pure function of the texts so the break checks can plant each defect."""
    import hashlib
    import re
    import xml.etree.ElementTree as ET
    out = []
    consts = dict(re.findall(r'public const string (\w+) = "([^"]*)";', src))
    if consts != CAI_MEMBERS:
        out.append("CaiFogOff constants %r != CAI_MEMBERS" % consts)
    if "fog.SetValue(settings, false);" not in src:
        out.append("Force() no longer writes FogOfWar_Enabled=false")
    out += force_flow_problems(src)
    if not re.search(r"Patch\(write,\s*prefix: new HarmonyMethod\(typeof\(CaiFogOff\), nameof\(Prefix_WriteSettings\)\)\)", src):
        out.append("no Harmony prefix on CombatAIMod.WriteSettings")
    if "public static void Prefix_WriteSettings() => Force(" not in src:
        out.append("the WriteSettings prefix does not force")
    if not re.search(r"\[StaticConstructorOnStartup\]\s*public static class CaiFogOffStartup", src) or 'CaiFogOff.Force("startup")' not in src:
        out.append("no startup force")
    if "public static bool caiFogForcedOff = true;" not in mod_src or 'Scribe_Values.Look(ref caiFogForcedOff, "caiFogForcedOff", true);' not in mod_src:
        out.append("the setting is not default-on in both the field and the Scribe default")
    if "CaiFogOff.Install();" not in mod_src:
        out.append("the Mod constructor does not install the forcer")
    root = ET.fromstring(about)
    if "brrainz.harmony" not in [e.text for e in root.iterfind("modDependencies/li/packageId")]:
        out.append("About: no Harmony modDependency")
    if "Krkr.rule56" not in [(e.text or "").strip() for e in root.iterfind("loadAfter/li")]:
        out.append("About: no loadAfter Krkr.rule56")
    want = {hashlib.sha256(b).hexdigest() + " " + name for name, b in cs_bytes.items()}
    have = {l.strip() for l in srchash.splitlines() if l.strip() and not l.startswith("#")}
    if want != have:
        out.append("Assemblies/RimMandrakePatches.dll.srchash does not match Source/CaiFogOff/*.cs (rebuild): %s" % sorted(want ^ have))
    return out


def cai_fog_check():
    import glob
    rd = lambda *p: open(os.path.join(HERE, *p), encoding="utf-8").read()
    src, mod_src, about = rd("Source", "CaiFogOff", "CaiFogOff.cs"), rd("Source", "CaiFogOff", "RM_PatchesMod.cs"), rd("About", "About.xml")
    srchash = rd("Assemblies", "RimMandrakePatches.dll.srchash")
    cs = {"CaiFogOff/" + os.path.basename(f): open(f, "rb").read() for f in sorted(glob.glob(os.path.join(HERE, "Source", "CaiFogOff", "*.cs")))}
    check("CAI fog forcer: shipped source, About and DLL stamp", cai_fog_problems(src, mod_src, about, srchash, cs) == [],
          cai_fog_problems(src, mod_src, about, srchash, cs))
    check("CAI fog forcer: RimMandrakePatches.dll is shipped", os.path.getsize(os.path.join(HERE, "Assemblies", "RimMandrakePatches.dll")) > 0)
    breaks = [("a renamed CAI member", src.replace('"FogOfWar_Enabled"', '"FogOfWar_On"'), mod_src, about, srchash),
              ("Force stops writing false", src.replace("fog.SetValue(settings, false);", "fog.SetValue(settings, was);"), mod_src, about, srchash),
              ("the WriteSettings prefix is dropped", src.replace("prefix: new HarmonyMethod", "postfix: new HarmonyMethod"), mod_src, about, srchash),
              ("the setting defaults off", src, mod_src.replace("caiFogForcedOff = true;", "caiFogForcedOff = false;"), about, srchash),
              ("loadAfter Krkr.rule56 removed", src, mod_src, about.replace("<li>Krkr.rule56</li>", ""), srchash),
              ("stale DLL stamp", src, mod_src, about, srchash.replace(srchash.splitlines()[-1][:8], "00000000")),
              ("the toggle guard is inverted", src.replace("if (!RM_PatchesSettings.caiFogForcedOff)",
                                                           "if (RM_PatchesSettings.caiFogForcedOff)"), mod_src, about, srchash),
              ("the bound guard is inverted", src.replace("if (!bound) return false;", "if (bound) return false;"),
               mod_src, about, srchash),
              ("the write is made conditional on fog already on", src.replace("fog.SetValue(settings, false);",
                                                                              "if (!was) fog.SetValue(settings, false);"),
               mod_src, about, srchash),
              ("the toggle guard stops returning", src.replace(
                  'its fog is left to CAI\'s own checkbox.";\n                return false;',
                  'its fog is left to CAI\'s own checkbox.";'), mod_src, about, srchash)]
    for name, a, *_ in breaks[-4:]:
        check("break: planted %s actually changed the source" % name, a != src)
    for name, a, b, c, d in breaks:
        check("break: %s is reported" % name, len(cai_fog_problems(a, b, c, d, cs)) >= 1)
    if not os.path.exists(CAI_DLL):
        print("skip  CAI members vs installed CombatAI.dll: %s not readable (UNMEASURED)" % CAI_DLL)
        return
    try:
        import lint_harmony_targets as lht       # ECMA-335 tables via dnfile, never a string grep
        index = {"types": lht.index_dll(CAI_DLL)}
    except ImportError:
        print("skip  CAI members vs installed CombatAI.dll: dnfile missing (UNMEASURED)")
        return
    m = CAI_MEMBERS
    want = [(m["FinderType"], "field", m["FinderSettingsField"]), (m["FinderType"], "field", m["FinderModField"]),
            ("CombatAI.Settings", "field", m["FogField"]), ("CombatAI.Settings", "field", m["SightField"]),
            (m["ModType"], "field", m["PrevFogField"]), (m["ModType"], "method", m["WriteSettingsMethod"])]
    bad = [(w, lht.has_member(index, *w)) for w in want if lht.has_member(index, *w)[0] != "OK"]
    check("CAI members still exist in the installed CombatAI.dll", bad == [], bad)
    check("sanity: the CombatAI.dll probe can miss a member",
          lht.has_member(index, "CombatAI.Settings", "field", "FogOfWar_NoSuchName")[0] == "MISSING_MEMBER")


def main():
    spec = importlib.util.spec_from_file_location("mp_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    shipped = v.unguarded_ops()
    check("shipped Patches/: every top-level op guarded", shipped == [], shipped)
    anima_check()
    cai_fog_check()
    ghosts = ghost_target_ops(os.path.join(HERE, "Patches"))
    check("shipped Patches/: no op on a mod-namespaced def sits outside a FindMod", ghosts == [], ghosts)
    fa = open(os.path.join(HERE, "Patches", "HeadSetForFA_Revive.xml"), encoding="utf-8").read()
    check("FA revive is wrapped in FindMod on the Facial Animation Compatability Project",
          'PatchOperationFindMod' in fa and '<li>Facial Animation Compatability Project</li>' in fa)
    tmp0 = tempfile.mkdtemp()
    try:
        open(os.path.join(tmp0, "Ghost.xml"), "w").write(
            '<Patch><Operation Class="PatchOperationConditional"><xpath>/Defs/FA.D[defName="X"]/P</xpath>'
            '<nomatch Class="PatchOperationAdd"><xpath>/Defs/FA.D[defName="X"]</xpath><value><P></P></value></nomatch></Operation></Patch>')
        got = ghost_target_ops(tmp0)
        check("break: an unguarded Conditional/nomatch Add on a mod def is reported", len(got) == 1, got)
        open(os.path.join(tmp0, "Ghost.xml"), "w").write(
            '<Patch><Operation Class="PatchOperationFindMod"><mods><li>M</li></mods><match Class="PatchOperationConditional">'
            '<xpath>/Defs/FA.D[defName="X"]/P</xpath><nomatch Class="PatchOperationAdd"><xpath>/Defs/FA.D[defName="X"]</xpath>'
            '<value><P></P></value></nomatch></match></Operation></Patch>')
        check("the FindMod-wrapped form is clean", ghost_target_ops(tmp0) == [])
    finally:
        shutil.rmtree(tmp0, ignore_errors=True)
    tmp = tempfile.mkdtemp()
    try:
        pd = os.path.join(tmp, "Patches")
        shutil.copytree(os.path.join(HERE, "Patches"), pd)
        f = os.path.join(pd, "ThirdPartySignConfigErrors_Fix.xml")
        s = open(f, encoding="utf-8").read()
        brk = s.replace('<Operation Class="PatchOperationFindMod">', '<Operation Class="PatchOperationFindMod" MayRequire="Dark.Signs">', 1)
        open(f, "w", encoding="utf-8").write(brk)
        got = v.unguarded_ops(pd)
        check("break: top-level MayRequire is reported as inert", len(got) == 1 and "inert" in got[0][2], got)
        open(f, "w", encoding="utf-8").write(s)
        open(os.path.join(pd, "Bare.xml"), "w").write(
            '<Patch><Operation Class="PatchOperationReplace"><xpath>Defs/X</xpath><value><a/></value></Operation></Patch>')
        got = v.unguarded_ops(pd)
        check("break: a bare Replace is reported unguarded", got == [("Bare.xml", 0, "unguarded PatchOperationReplace")], got)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # ---- fix_effects_vs_dump_static (MANDRAKEPATCHES_COVERAGE_GAPS_1 offline half) ----
    import copy
    ops = v.leaf_ops()
    try:
        rows, active = v._dump_inputs(sorted(set(o["type"] for o in ops)))
        installed = v._installed_names()
    except Exception as e:
        rows = None
        print("UNMEASURED  fix effects vs dump: %s" % e)
    if rows:
        import collections
        kinds = collections.Counter(o["cls"] for o in ops)
        check("sanity probe: >= 15 leaf ops read (22 after the 2026-10-18 donor retirements) incl. Replace/Add/Remove", len(ops) >= 15 and all(kinds[k] for k in ("Replace", "Add", "Remove")), kinds)
        checked, skipped, bad = v.effect_findings(ops, rows, active, installed)
        check("shipped fixes vs the load-14 dump: %d checked, all show their effect (skipped %s)" % (checked, skipped), checked >= 15 and bad == [], bad[:3])
        check("inactive donors are named, not passed", skipped["donor mod inactive"] >= 1, skipped)

        def fx(tag, mut, must, ops_=None, active_=None, installed_=None, expect_n=1):
            r2 = copy.deepcopy(rows)
            mut(r2)
            got = v.effect_findings(ops_ or ops, r2, active_ if active_ is not None else active, installed_ if installed_ is not None else installed)[2]
            check("break fix: %-52s -> %s" % (tag, must[:30]), any(must in g for g in got), got)

        def first(cls, ty):
            return next(o for o in ops if o["cls"] == cls and o["type"] == ty and all(any(g.lower() in active for g in grp) for grp in o["guards"]))
        try:
            wg = first("Replace", "WorkGiverDef")
        except StopIteration:
            # the dump's mod set decides which donors are active; with the DrillTurret donor absent from it none of the break
            # fixtures below can bite -- say so aloud (UNMEASURED), never crash and never pass.
            print("UNMEASURED  fix-effect breaks: no ACTIVE-donor WorkGiverDef Replace in the current dump's mod set (MiningCo. DrillTurret not in it)")
            wg = None
        if wg is None:
            print("\nUNMEASURED, not a pass or a fail" if not FAILS else "\n%d MandrakePatches selftest(s) FAILED" % len(FAILS))
            return 1 if FAILS else 0
        fx("turret job reverts to Mining", lambda r: r["WorkGiverDef"][wg["name"]]["fields"].__setitem__("workType", "Mining"), "workType")
        sg = first("Add", "ThingDef")
        fx("a sign loses its config-error field", lambda r: r["ThingDef"][sg["name"]]["fields"].__setitem__(sg["pairs"][0][0], False), sg["pairs"][0][0])
        wo = first("Replace", "WorldObjectDef")
        fx("settlement icon back to 1", lambda r: r["WorldObjectDef"][wo["name"]]["fields"].__setitem__("expandingIconDrawSize", 1.0), "expandingIconDrawSize")
        rm = first("Remove", "BiomeDef")
        last = rm["rest"].rstrip("/").split("/")[-1]
        fx("a removed animal reappears in the biome (%s)" % last, lambda r: r["BiomeDef"][rm["name"]]["fields"].__setitem__("wildAnimals", [{"animal": last, "commonality": 1}]), "still in the dump")
        rp = first("Replace", "RulePackDef")
        fx("the doubled apostrophe rule comes back", lambda r: r["RulePackDef"][rp["name"]]["fields"].__setitem__("rulePack", {"rulesStrings": ["maybeApostrophe->''"]}), "replaced-away")
        # GRiNDTerra's tex-path fixes were this break's fixture; they retired with that donor (2026-10-18). Any other active
        # PawnKindDef Replace with a `gone` texPath serves; none left means this break has nothing to bite, said aloud.
        pk = next((o for o in ops if o["cls"] == "Replace" and o["type"] == "PawnKindDef" and o["gone"] and all(any(g.lower() in active for g in grp) for grp in o["guards"])), None)
        if pk is not None:
            fx("an old texPath is still live (%s)" % pk["name"], lambda r: r["PawnKindDef"][pk["name"]]["fields"].__setitem__("lifeStages", [{"x": {"texPath": pk["gone"][0]}}]), "replaced-away")
        else:
            print("  skip break: no active PawnKindDef texPath Replace remains to break (UNMEASURED, not passed)")
        fx("an active donor's def vanishes (%s)" % wg["name"], lambda r: r["WorkGiverDef"].pop(wg["name"]), "not in the dump")
        fx("a FindMod name that no installed mod has", lambda r: None, "no installed mod is called", installed_=installed - {g.lower() for g in wg["guards"][0]})
        gone_names = {g.lower() for grp in wg["guards"] for g in grp}
        ck = v.effect_findings([wg], rows, active - gone_names, installed)
        check("break: the same op with its donor INACTIVE is skipped, not flagged", ck[0] == 0 and ck[1]["donor mod inactive"] == 1 and ck[2] == [], ck)
        ck = v.effect_findings([dict(wg, type="NoSuchDumpedType")], dict(rows, NoSuchDumpedType=None), active, installed)
        check("an undumped type is skipped and named", ck[0] == 0 and ck[1]["type not dumped"] == 1, ck)

        import runner
        from northstar_driver.session import FastSession
        from northstar_driver.transport import MockGame, MockTransport

        def chain(r_):
            saved = v._dump_inputs
            v._dump_inputs = lambda types: (r_, active)
            try:
                own = v.Suite("MandrakePatches")
                own.toggles = []
                own.chains = [(n, f) for n, f in v.suite.chains if n == "fix_effects_vs_dump_static"]
                with FastSession(transport=MockTransport(MockGame()), strict=False) as sess:
                    res = runner.run_suite(own, sess, anchor=None, mod=None)
            finally:
                v._dump_inputs = saved
            return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])
        check("chain PASSes on the shipped patches", list(chain(rows).values()) == ["PASS"], chain(rows))
        r9 = copy.deepcopy(rows)
        r9["WorkGiverDef"][wg["name"]]["fields"]["workType"] = "Mining"
        check("chain reddens when a fix did not take", list(chain(r9).values()) == ["FAIL"], chain(r9))
    if FAILS:
        print("\n%d MandrakePatches selftest(s) FAILED" % len(FAILS))
        return 1
    if not rows:
        # the dump half never ran (unreadable dump, or an empty one): say so in the runner's own
        # phrase, never "all passed" - a skipped check is not a pass.
        print("\nUNMEASURED, not a pass or a fail (fix effects vs dump did not run)")
        return 0
    print("\nall MandrakePatches selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
