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


def main():
    spec = importlib.util.spec_from_file_location("mp_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    shipped = v.unguarded_ops()
    check("shipped Patches/: every top-level op guarded", shipped == [], shipped)
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
        check("sanity probe: >= 25 leaf ops read incl. Replace/Add/Remove", len(ops) >= 25 and all(kinds[k] for k in ("Replace", "Add", "Remove")), kinds)
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
        wg = first("Replace", "WorkGiverDef")
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
        pk = next(o for o in ops if o["cls"] == "Replace" and o["type"] == "PawnKindDef" and o["gone"] and all(any(g.lower() in active for g in grp) for grp in o["guards"]))
        fx("an old texPath is still live (%s)" % pk["name"], lambda r: r["PawnKindDef"][pk["name"]]["fields"].__setitem__("lifeStages", [{"x": {"texPath": pk["gone"][0]}}]), "replaced-away")
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
    print("\nall MandrakePatches selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
