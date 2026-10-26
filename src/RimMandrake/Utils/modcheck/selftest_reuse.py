#!/usr/bin/env python3
"""Selftest for option B of design/RimMandrake/focused_testing_plan_2026-10-25.md §4: run manifests (status.run_manifest),
reuse of external live driver results (reuse.py, FlowWorks validation.py readers), freshness / validity on components
(suite.py, record.py, runner summary), the validity checks and canary (validity.py, runner.run_suite), `--changed`
suggestions (targeting.changed) and the stale-row audit (reuse_audit.classify). Offline: no game, no bridge, no ledger
write, no status write; every file it writes is under a temp dir.

Reds on: a doc / C# Source / mod-root .py edit changing the runtime hash, or a Defs edit not changing it; a helper or
data-file edit not changing the test hash, or an unrelated .py changing it; a non-literal import_module not making the
manifest unresolved; any why_not gate letting a result through; MODCHECK_REUSE parsing; a reusable row changing its
verdict in report mode, or not taking the reused status in reuse mode; a fresh row being displaced by a reused one; a
FAIL that a validity check voids still publishing a finding or losing its text; a red canary running a live chain body,
or skipping an offline chain; a reused PASS counting as fresh green; --changed missing a defName / input / basename hit.
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
FW = os.path.join(os.path.dirname(UTILS), "FlowWorks")
for _p in (os.path.join(FW, "northstar"), FW, UTILS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import record  # noqa: E402
import reuse  # noqa: E402
import reuse_audit  # noqa: E402
import runner  # noqa: E402
import status  # noqa: E402
import targeting  # noqa: E402
import validity  # noqa: E402
from suite import Suite, TestContext, ExpectationFailed  # noqa: E402

FAILS = []


def ok(cond, what, got=None):
    print(("PASS  " if cond else "FAIL  ") + what + ("" if cond or got is None else "   got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def _w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


@contextlib.contextmanager
def _env(value):
    old = os.environ.get(reuse.ENV)
    if value is None:
        os.environ.pop(reuse.ENV, None)
    else:
        os.environ[reuse.ENV] = value
    try:
        yield
    finally:
        if old is None:
            os.environ.pop(reuse.ENV, None)
        else:
            os.environ[reuse.ENV] = old


def _tmp_mod():
    """tmp/Mod (Defs, Source, a doc, a mod-root selftest, northstar/drv.py importing helper_x and naming spec.json) and
    tmp/Utils/modcheck/shared_y.py, which helper_x imports."""
    root = tempfile.mkdtemp(prefix="rm_reuse_")
    mod = os.path.join(root, "Mod")
    _w(os.path.join(mod, "About", "About.xml"), "<ModMetaData/>")
    _w(os.path.join(mod, "Defs", "a.xml"), "<Defs><ThingDef><defName>RM_A</defName></ThingDef></Defs>")
    _w(os.path.join(mod, "Source", "A.cs"), "class A {}")
    _w(os.path.join(mod, "notes.md"), "doc")
    _w(os.path.join(mod, "selftest_mod.py"), "x = 1")
    _w(os.path.join(mod, "northstar", "drv.py"),
       "import json\nimport helper_x\nSPEC = 'spec.json'\n\ndef main():\n    from os import path\n")
    _w(os.path.join(mod, "northstar", "helper_x.py"), "import shared_y\n")
    _w(os.path.join(mod, "northstar", "spec.json"), "{}")
    _w(os.path.join(mod, "northstar", "unrelated.py"), "y = 2")
    _w(os.path.join(root, "Utils", "modcheck", "shared_y.py"), "z = 3")
    return root, mod


def t_manifest():
    root, mod = _tmp_mod()
    drv = os.path.join(mod, "northstar", "drv.py")
    try:
        m0 = status.run_manifest(mod, drv)
        ok(m0["schema"] == status.MANIFEST_SCHEMA and m0["script"] == "northstar/drv.py" and not m0["unresolved"]
           and m0["runtime"] and m0["test"], "manifest: schema, script relative to the mod, both hashes, nothing unresolved", m0)
        want = {"Mod/northstar/drv.py", "Mod/northstar/helper_x.py", "Mod/northstar/spec.json", "Utils/modcheck/shared_y.py"}
        ok(set(m0["test_files"]) == want, "test closure: script + transitive local imports (Utils/modcheck too) + named data file",
           m0["test_files"])

        def again():
            return status.run_manifest(mod, drv)
        for rel, text in (("Source/A.cs", "class A { int b; }"), ("notes.md", "doc 2"), ("selftest_mod.py", "x = 2"),
                          ("northstar/unrelated.py", "y = 3")):
            _w(os.path.join(mod, rel), text)
            m = again()
            ok(m["runtime"] == m0["runtime"] and m["test"] == m0["test"],
               "manifest: editing %s changes neither hash" % rel, (m["runtime"][:8], m["test"][:8]))
        _w(os.path.join(mod, "Defs", "a.xml"), "<Defs><ThingDef><defName>RM_B</defName></ThingDef></Defs>")
        m1 = again()
        ok(m1["runtime"] != m0["runtime"] and m1["test"] == m0["test"], "manifest: a Defs edit changes runtime only")
        _w(os.path.join(root, "Utils", "modcheck", "shared_y.py"), "z = 4")
        m2 = again()
        ok(m2["test"] != m1["test"] and m2["runtime"] == m1["runtime"], "manifest: a transitive helper edit changes test only")
        _w(os.path.join(mod, "northstar", "spec.json"), '{"a": 1}')
        m3 = again()
        ok(m3["test"] != m2["test"], "manifest: a named data-file edit changes test")
        ok(status.mod_hash(mod) != "" and isinstance(status.mod_hash(mod), str), "mod_hash still computes beside the manifest")
        _w(os.path.join(mod, "northstar", "helper_x.py"), "import importlib\nimportlib.import_module(NAME)\n")
        m4 = again()
        ok(any("non-literal import_module" in u for u in m4["unresolved"]), "manifest: a non-literal import_module is unresolved",
           m4["unresolved"])
        _w(os.path.join(mod, "northstar", "helper_x.py"), "import shared_y\n")
        _w(os.path.join(mod, "northstar", "pkg", "__init__.py"), "A = 1")
        _w(os.path.join(mod, "northstar", "pkg", "worker.py"), "from .oracle import expected\nfrom . import peer\n")
        _w(os.path.join(mod, "northstar", "pkg", "oracle.py"), "expected = 1")
        _w(os.path.join(mod, "northstar", "pkg", "peer.py"), "p = 1")
        _w(os.path.join(mod, "northstar", "specs", "deep.json"), "{}")
        _w(drv, "import json\nimport helper_x\nimport pkg.worker\nimport os\nP = os.path.join('specs', 'deep.json')\n")
        m6 = again()
        names = set(m6["test_files"])
        ok({"Mod/northstar/pkg/__init__.py", "Mod/northstar/pkg/worker.py", "Mod/northstar/pkg/oracle.py",
            "Mod/northstar/pkg/peer.py", "Mod/northstar/specs/deep.json"} <= names and not m6["unresolved"],
           "test closure: package __init__, relative imports and a data file one dir down are hashed", (sorted(names), m6["unresolved"]))
        _w(os.path.join(mod, "northstar", "pkg", "worker.py"), "from .gone import x\n")
        m7 = again()
        ok(any("relative import .gone" in u for u in m7["unresolved"]), "test closure: an unresolvable relative import is unresolved",
           m7["unresolved"])
        m5 = status.run_manifest(os.path.join(root, "missing"), os.path.join(root, "missing", "x.py"))
        ok(isinstance(m5, dict) and m5["unresolved"], "manifest: a missing script never raises, it is unresolved", m5)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _good(cur):
    return {"mode": "live", "certifiable": True, "manifest": dict(cur), "env": {"assembly_sha256": "ABC"}, "rows": []}


def t_why_not():
    cur = {"schema": status.MANIFEST_SCHEMA, "script": "northstar/drv.py", "runtime": "r1", "test": "t1", "unresolved": []}
    why = lambda d, cert=False, c=cur: reuse.why_not(d, "/nowhere", "abc", cert, _current=c)  # noqa: E731
    ok(why(_good(cur)) is None, "why_not: matching manifest + DLL (case-insensitive) is reusable", why(_good(cur)))
    cases = [("not live", lambda d: d.update(mode="mock")), ("aborted", lambda d: d.update(aborted="x")),
             ("no manifest", lambda d: d.pop("manifest")),
             ("manifest schema", lambda d: d["manifest"].update(schema=0)),
             ("manifest unresolved", lambda d: d["manifest"].update(unresolved=["x"])),
             ("manifest incomplete", lambda d: d["manifest"].update(test=None)),
             ("runtime changed", lambda d: d["manifest"].update(runtime="r0")),
             ("test code changed", lambda d: d["manifest"].update(test="t0")),
             ("no DLL identity", lambda d: d.pop("env")),
             ("DLL other", lambda d: d["env"].update(assembly_sha256="def"))]
    for want, mut in cases:
        d = _good(cur)
        mut(d)
        got = why(d) or ""
        ok(want in got, "why_not: %s is refused" % want, got)
    d = _good(cur)
    d["certifiable"] = False
    ok(why(d) is None and "not certifiable" in (why(d, True) or ""), "why_not: certifiable only where the reader demands it")
    ok("current manifest unresolved" in (why(_good(cur), c=dict(cur, unresolved=["y"])) or ""),
       "why_not: an unprovable CURRENT closure never reuses")
    ok("no DLL identity" in (reuse.why_not(_good(cur), "/nowhere", None, _current=cur) or ""),
       "why_not: no repo DLL sha refuses")


def t_mode_and_tags():
    ok(reuse.mode({}) == reuse.REPORT and reuse.mode({reuse.ENV: "1"}) == reuse.REUSE
       and reuse.mode({reuse.ENV: "0"}) == reuse.OFF and reuse.mode({reuse.ENV: "junk"}) == reuse.REPORT,
       "mode: unset/junk report, 1 reuse, 0 off")
    ok(reuse.tag("f.json", reuse.REUSE) == "reused@f.json" and reuse.tag("f.json", reuse.REPORT) == "reusable@f.json", "tag")
    s = reuse.summarize([{"name": "c", "components": [{"name": "a", "freshness": "reused@x"},
                                                      {"name": "b", "freshness": "reusable@y"}, {"name": "d"}]}])
    ok(s == {"reused": ["c/a"], "reusable": ["c/b"]}, "summarize: reused and reusable rows named chain/row", s)


def t_rows_and_newest():
    root, mod = _tmp_mod()
    ns = os.path.join(mod, "northstar")
    try:
        reuse._CURRENT.clear()
        cur = status.run_manifest(mod, os.path.join(ns, "drv.py"))
        base = {"mode": "live", "manifest": cur, "env": {"assembly_sha256": "abc"}}
        _w(os.path.join(ns, "r_1.json"), json.dumps(dict(base, started="1", rows=[{"id": "A", "status": "FAIL"},
                                                                                     {"id": "B", "status": "PASS"}])))
        _w(os.path.join(ns, "r_2.json"), json.dumps(dict(base, started="2", rows=[{"id": "A", "status": "PASS"}])))
        _w(os.path.join(ns, "r_3.json"), json.dumps(dict(base, started="3", manifest=dict(cur, test="old"),
                                                         rows=[{"id": "A", "status": "FAIL"}])))
        _w(os.path.join(ns, "r_4.json"), "{broken")
        got = reuse.rows(("r_*.json",), ns, mod, "abc")
        ok({k: (v[0]["status"], v[1]) for k, v in got.items()} == {"A": ("PASS", "r_2.json"), "B": ("PASS", "r_1.json")},
           "rows: newest reusable per id; a stale-test-manifest result and a broken file are not read", got)
        ok("A" not in reuse.rows(("r_*.json",), ns, mod, "abc", exclude={"A"}), "rows: fresh ids excluded")
        n = reuse.newest(sorted(os.path.join(ns, "r_%d.json" % i) for i in range(1, 5)), mod, "abc")
        ok(n is not None and os.path.basename(n[0]) == "r_2.json", "newest: the newest reusable result", n and n[0])
        ok(reuse.rows(("r_*.json",), ns, mod, "zzz") == {}, "rows: a DLL other than the repo's reuses nothing")
    finally:
        reuse._CURRENT.clear()
        shutil.rmtree(root, ignore_errors=True)


class _T(TestContext):
    def __init__(self):
        TestContext.__init__(self, None)

    def _guard(self):
        return True


def t_validation_integration():
    """FlowWorks validation.py readers in report vs reuse mode, on a temp northstar with a real current manifest."""
    import validation as V
    from modcheck import reuse as PR
    from modcheck import status as PST
    tmp = tempfile.mkdtemp(prefix="rm_reuse_ns_")
    saved = (V.NS, V.repo_dll_sha256, V.latest_core_result, V.driver_rows_at, PST.mod_hash)
    try:
        V.NS = tmp
        V.repo_dll_sha256 = lambda: "abc"
        V.latest_core_result = lambda h: None
        PST.mod_hash = lambda d: "now"
        env = {"assembly_sha256": "abc"}
        m_thirst = status.run_manifest(V.HERE, os.path.join(V.HERE, "northstar", "thirst_live.py"))
        ok(not m_thirst["unresolved"], "the real thirst_live.py closure resolves (else reuse can never fire)",
           m_thirst["unresolved"])
        rid = V.THIRST_LIVE[0][0]
        rid2 = V.THIRST_LIVE[1][0]
        _w(os.path.join(tmp, "thirst_live_result_old.json"), json.dumps(
            {"mode": "live", "mod_hash": "then", "started": "1", "manifest": m_thirst, "env": env,
             "rows": [{"id": rid, "status": "PASS", "class": "MOD", "detail": "old pass"},
                      {"id": rid2, "status": "PASS", "detail": "old pass 2"}]}))
        fresh = {rid2: ({"id": rid2, "status": "FAIL", "class": "MOD", "detail": "fresh fail"}, "fresh.json")}
        V.driver_rows_at = lambda h, ns=None, dll_sha=None: dict(fresh)
        for val, want_v, want_f in ((None, "UNMEASURED", "reusable@"), ("1", "PASS", "reused@"), ("0", "UNMEASURED", "fresh")):
            with _env(val):
                PR._CURRENT.clear()
                t = _T()
                V._driver_live_report(t, V.THIRST_LIVE[:2], "thirst_live.py", "ITEM")
                c, c2 = t.components[0], t.components[1]
                ok(c.verdict == want_v and c.freshness.startswith(want_f),
                   "driver rows, MODCHECK_REUSE=%s: missing row %s, freshness %s" % (val, want_v, want_f),
                   (c.verdict, c.freshness, c.detail[:80]))
                ok(c2.verdict == "FAIL" and c2.freshness == "fresh",
                   "driver rows, MODCHECK_REUSE=%s: a FRESH FAIL is never displaced by an old PASS" % val, (c2.verdict, c2.freshness))
        # core_live_rows: v2 result reusable
        m_v2 = status.run_manifest(V.HERE, os.path.join(V.HERE, "northstar", "validation_v2.py"))
        _w(os.path.join(tmp, "validation_v2_result_x.json"), json.dumps(
            {"mode": "live", "mod_hash": "then", "manifest": m_v2, "env": env,
             "rows": [{"id": i, "status": "PASS", "detail": "ok"} for i in V.CORE_LIVE_IDS]}))
        for val, want in ((None, "UNMEASURED"), ("1", "PASS")):
            with _env(val):
                PR._CURRENT.clear()
                t = _T()
                V.core_live_rows.__wrapped__(t) if hasattr(V.core_live_rows, "__wrapped__") else V.core_live_rows(t)
                rows = [c for c in t.components if c.name in set(V.CORE_LIVE_IDS)]
                ok(rows and all(c.verdict == want for c in rows) and all(c.freshness.startswith("reus") for c in rows),
                   "core_live_rows, MODCHECK_REUSE=%s: every v2 row %s and tagged" % (val, want),
                   sorted({(c.verdict, c.freshness) for c in rows})[:3])
        if m_v2["unresolved"]:
            ok(False, "the real validation_v2.py closure resolves", m_v2["unresolved"])
    finally:
        V.NS, V.repo_dll_sha256, V.latest_core_result, V.driver_rows_at, PST.mod_hash = saved
        PR._CURRENT.clear()
        shutil.rmtree(tmp, ignore_errors=True)


def t_suite_validity_hook():
    t = TestContext(None)
    pub = []
    t._on_finding = pub.append
    t.validity_checks = [lambda ctx, comp: 1 / 0, lambda ctx, comp: ("map gone", "UNKNOWN", "high")]
    with t.component("row_a"):
        raise ExpectationFailed("pipe empty")
    with t.component("row_b"):
        pass
    a, b = t.components
    ok(a.verdict == "UNMEASURED" and a.validity == "invalid" and a.suspected_cause == "UNKNOWN"
       and a.cause_confidence == "high" and "pipe empty" in (a.lead or "") and not pub,
       "validity: a voided FAIL is UNMEASURED/invalid, keeps its text as lead, publishes no finding", a.as_dict())
    ok(any("ZeroDivisionError" in str(e.get("result")) for e in a.evidence), "validity: a check that raises is evidence")
    ok(b.verdict == "UNMEASURED", "validity: the rows after an invalid row are UNMEASURED (chain state unknown)", b.verdict)
    d = a.as_dict()
    ok(all(k in d for k in ("freshness", "validity", "suspected_cause", "cause_confidence", "lead")), "as_dict carries the fields")
    t2 = TestContext(None)
    t2._on_finding = pub.append
    t2.validity_checks = [lambda ctx, comp: None]
    with t2.component("row_c"):
        raise ExpectationFailed("real bug")
    c = t2.components[0]
    ok(c.verdict == "FAIL" and c.validity == "valid" and c.suspected_cause == "MOD" and pub == [c],
       "validity: checks armed and clean -> FAIL stands, valid/MOD, finding published", (c.verdict, c.validity))
    t3 = TestContext(None)
    with t3.component("row_d"):
        raise ExpectationFailed("bug")
    ok(t3.components[0].validity is None and t3.components[0].freshness == "fresh",
       "validity: unarmed -> no validity claim (behaviour unchanged)")


class _Sess(object):
    def __init__(self, state="Playing", colonists=1, readback=True, occupied=(), spawn_ok=True):
        self.state, self.n, self.readback, self.calls, self.spawn_ok = state, colonists, readback, [], spawn_ok
        self.cells = {c: ["Steel"] for c in occupied}
        self.destroyed = []

    @staticmethod
    def _xz(spec):
        x, z = spec.split(":")[-1].split(",")[:2]
        return int(x), int(z)

    def call(self, tool, **p):
        self.calls.append(tool)
        if tool == "rimworld/get_ui_state":
            return {"programState": self.state}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [{"id": "c%d" % i, "isPlayer": True, "intelligence": "Humanlike"}
                                               for i in range(self.n)] + [{"id": "h1", "hostile": True}]}
        if tool == "jawa/spawn_batch":
            if self.readback:
                self.cells.setdefault(self._xz(p["ops"]), []).append("Steel")
            return {"success": self.spawn_ok}
        if tool == "jawa/destroy_batch":
            c = self._xz(p["rects"])
            self.destroyed.append(c)
            self.cells[c] = []
            return {"success": True}
        return {"success": True}

    def things_at(self, x, z):
        return list(self.cells.get((x, z), []))


def t_validity_module():
    s = _Sess()
    g = validity.canary(s, (10, 10))
    ok(g["ok"] and s.cells.get((10, 10)) == [] and s.destroyed == [(10, 10)], "canary: green on a sane session, cleans up", g)
    s = _Sess(occupied=[(10, 10)])
    g = validity.canary(s, (10, 10))
    ok(g["ok"] and s.cells[(10, 10)] == ["Steel"] and (10, 10) not in s.destroyed and len(s.destroyed) == 1,
       "canary: an occupied anchor is left alone; it spawns and destroys on an empty neighbour only", (g, s.destroyed))
    r = validity.canary(_Sess(spawn_ok=False), (10, 10))
    ok(not r["ok"] and any("did not report success" in p for p in r["problems"]), "canary: a spawn without success is red", r)
    full = [(x, z) for x in range(-3, 24) for z in range(-3, 24)]
    s = _Sess(occupied=full)
    r = validity.canary(s, (10, 10))
    ok(not r["ok"] and "jawa/spawn_batch" not in s.calls and not s.destroyed,
       "canary: no empty cell near the anchor -> red, nothing spawned or destroyed", r)
    r = validity.canary(_Sess(readback=False), (10, 10))
    ok(not r["ok"] and any("did not read back" in p for p in r["problems"]), "canary: red when the spawn does not read back", r)
    r = validity.canary(_Sess(state="Entry"), (10, 10))
    ok(not r["ok"] and "jawa/spawn_batch" not in _Sess().calls, "canary: red off-map, spawns nothing", r)
    r = validity.canary(_Sess(), None)
    ok(not r["ok"] and r["problems"], "canary: a bad anchor is red, never a raise", r)
    ctx = TestContext(None)
    ctx.session = _Sess(state="Entry")
    ok(validity.menu_drop(ctx, None)[1:] == ("UNKNOWN", "high"), "menu_drop fires off Playing")
    ctx.session = _Sess(colonists=0)
    ok(validity.colonists_zero(ctx, None)[1] == "UNKNOWN", "colonists_zero fires on an empty roster")
    ctx.session = _Sess()
    ok(validity.colonists_zero(ctx, None) is None, "colonists_zero quiet with a colonist")
    ok(validity.hostile_arrival()(ctx, None)[1] == "SITE", "hostile_arrival fires on an undeclared hostile")
    ok(validity.hostile_arrival(fixtures=["h1"])(ctx, None) is None, "hostile_arrival quiet for a declared fixture")
    ctx.fixture_ids = {"h1"}
    ok(validity.hostile_arrival()(ctx, None) is None, "hostile_arrival quiet for a pawn this chain spawned")
    cc = validity.canary_component({"problems": ["x"]}).as_dict()
    ok(cc["verdict"] == "UNMEASURED" and cc["validity"] == "invalid" and cc["suspected_cause"] == "HARNESS",
       "canary_component: UNMEASURED invalid HARNESS", cc)


def _suite(ran):
    s = Suite("ReuseT")

    @s.chain("live_one")
    def live_one(t):
        ran.append("live_one")
        with t.component("a"):
            pass

    @s.chain("off_one", offline=True)
    def off_one(t):
        ran.append("off_one")
        with t.component("b"):
            pass
    return s


def t_run_suite_validity_scope():
    """--validity arms the game-reading checks on LIVE chains only; run_suite clears the current-manifest caches."""
    from selftest import _fake_session
    s = Suite("ValT")
    armed = {}

    @s.chain("live_x")
    def live_x(t):
        armed["live_x"] = len(t.validity_checks)

    @s.chain("off_x", offline=True)
    def off_x(t):
        armed["off_x"] = len(t.validity_checks)
    reuse._CURRENT[("x", "y")] = {}
    sess = _fake_session()
    fake = _Sess()
    sess.call, sess.things_at = fake.call, fake.things_at
    with contextlib.redirect_stderr(io.StringIO()):
        runner.run_suite(s, sess, anchor=(5, 5), validity=True)
    ok(armed.get("live_x") == 3 and armed.get("off_x") == 0, "run_suite --validity: live chain armed, offline chain not", armed)
    ok(not reuse._CURRENT, "run_suite: the current-manifest cache is cleared per suite run")


def t_run_suite_canary():
    from selftest import _fake_session
    for good in (False, True):
        ran = []
        sess = _fake_session()
        fake = _Sess(readback=good)
        sess.call = fake.call
        sess.things_at = fake.things_at
        with contextlib.redirect_stderr(io.StringIO()):
            res = runner.run_suite(_suite(ran), sess, anchor=(5, 5), canary=True, validity=True)
        names = {ch["name"]: [c["name"] for c in ch["components"]] for ch in res["chains"]}
        if good:
            ok(ran == ["live_one", "off_one"] and res["canary"]["ok"] and res["fresh_green"] and res["all_green"],
               "run_suite: green canary runs every chain; fresh_green", (ran, res.get("fresh_green")))
        else:
            ok(ran == ["off_one"] and names["live_one"] == [validity.CANARY_ROW] and not res["all_green"]
               and res["invalid"] == ["live_one/%s" % validity.CANARY_ROW],
               "run_suite: red canary runs no live chain body, still runs the offline chain", (ran, names, res["invalid"]))


def t_record_and_summary():
    rows = [{"id": "a", "status": "PASS"}, {"id": "b", "status": "PASS", "freshness": "reused@f.json"},
            {"id": "c", "status": "UNMEASURED", "validity": "invalid"}]
    res = {"rows": rows, "mode": "live", "mod": "M", "mod_hash": "h"}
    _, green, _, comps = record.judge(res, "M", "h", None)
    ok(not green and comps["reused"] == ["b"] and comps["invalid"] == ["c"] and "b" in comps["not_ok"],
       "record.judge: a reused PASS is not a fresh green; invalid and reused listed", comps)
    ext = {"mod_hash": "h", "all_green": True, "chains_declared": ["x"], "chains_run": ["x"],
           "chains": [{"name": "x", "components": [{"name": "a", "verdict": "PASS"},
                                                   {"name": "b", "verdict": "PASS", "freshness": "reused@f"}]}]}
    _, s4 = record.judge_step4(ext, "M", "h", None)
    ok(s4["status"] == "UNMEASURED" and s4["reused"] == ["x/b"] and s4["pass"] == 1,
       "record.judge_step4: a reused PASS counts unmeasured", s4)
    ext["chains"][0]["components"][1] = {"name": "b", "verdict": "PASS", "validity": "invalid"}
    _, s4 = record.judge_step4(ext, "M", "h", None)
    ok(s4["status"] == "UNMEASURED" and s4["invalid"] == ["x/b"], "record.judge_step4: an invalid PASS counts unmeasured", s4)


def t_changed():
    s = Suite("ChT")

    @s.chain("pumps", inputs=["Defs/Shared/*.xml"])
    def pumps(t):
        """reads RM_PumpBig and pump_helper.py"""
        return "RM_PumpBig", "pump_helper.py"

    @s.chain("other")
    def other(t):
        return None
    files = [("Defs/Pumps.xml", "<defName>RM_PumpBig</defName>"), ("Defs/Shared/base.xml", None),
             ("northstar/pump_helper.py", None), ("Textures/x.png", None), ("Defs/Other.xml", "<defName>RM_Zed</defName>")]
    res = targeting.changed(s, files)
    why = res["suggest"].get("pumps") or []
    ok(len(why) == 3 and "other" not in res["suggest"], "changed: defName, declared input and basename map to the chain", res)
    ok(res["unknown"] == ["Textures/x.png", "Defs/Other.xml"], "changed: unmapped files are impact unknown", res["unknown"])
    lines = targeting.changed_report(res)
    ok(any("impact unknown" in l for l in lines) and any("--chains pumps" in l for l in lines), "changed_report lines", lines)


def t_audit_classify():
    cur = {"schema": status.MANIFEST_SCHEMA, "script": "s.py", "runtime": "r", "test": "t", "unresolved": []}
    res = [("a.json", {"rows": []}, {"A"}), ("b.json", {"manifest": cur}, {"B"}), ("c.json", {"manifest": cur}, {"C"})]
    why = lambda d: None if d.get("manifest") and d is res[2][1] else ("runtime changed" if d.get("manifest") else "no manifest")  # noqa: E731
    got = [reuse_audit.classify([i], res, "/m", "abc", False, _why=why)[0] for i in ("Z", "A", "B", "C")]
    ok(got == ["never measured", "no manifest", "relevant change", "reusable"], "reuse_audit.classify: the four classes", got)
    part = reuse_audit.classify(["C", "D"], res, "/m", "abc", False, _why=why)
    ok(part[0] != "reusable", "reuse_audit.classify: a bar whose rows are only partly reusable is not reusable", part)
    res2 = res + [("d.json", {"manifest": cur}, {"D"})]
    why2 = lambda d: None if d is res2[2][1] or d is res2[3][1] else "no manifest"  # noqa: E731
    ok(reuse_audit.classify(["C", "D"], res2, "/m", "abc", False, _why=why2)[0] == "reusable",
       "reuse_audit.classify: a bar covered across two reusable results is reusable")


def t_driver_stamp():
    import driver_stamp
    m = driver_stamp.manifest(FW, os.path.join(FW, "northstar", "thirst_live.py"))
    ok(m.get("schema") == status.MANIFEST_SCHEMA and m.get("script") == "northstar/thirst_live.py",
       "driver_stamp.manifest: a run manifest keyed to the driver", {k: m.get(k) for k in ("schema", "script", "unresolved")})
    ok(driver_stamp.manifest(FW, "/no/such/x.py").get("unresolved"), "driver_stamp.manifest: an unknown script is unresolved")


def main():
    for t in (t_manifest, t_why_not, t_mode_and_tags, t_rows_and_newest, t_validation_integration, t_suite_validity_hook,
              t_validity_module, t_run_suite_validity_scope, t_run_suite_canary, t_record_and_summary, t_changed, t_audit_classify, t_driver_stamp):
        try:
            t()
        except Exception as ex:     # noqa: BLE001 - one broken test must not hide the others
            import traceback
            traceback.print_exc()
            ok(False, "%s raised %s: %s" % (t.__name__, type(ex).__name__, ex))
    print("\nSELFTEST %s -- %d failed" % ("FAILED" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
