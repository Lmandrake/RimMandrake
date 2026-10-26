#!/usr/bin/env python3
"""Selftest for the known-good gate (modcheck/gate.py, KNOWN_GOOD_BUILD_SKIP_UNCHANGED_PASS; plan
design/RimMandrake/test_orchestration_two_machines_2026-10-25.md section 3). Offline: no game, no bridge, no ledger, no
status write; every file it writes is under a temp dir (the gate index included, via MODCHECK_GATE_HISTORY and a
temp sheet path).

Reds on: editing one chain's body, a constant only another chain uses, or a helper module only another chain imports
changing a chain's key (or the edit not changing the chain that does use it); a chain that reads the filesystem with
no `inputs=` declaration being skippable; a declared input edit not changing the key; a declared glob that matches
nothing not refusing (a "?glob" refusing); `inputs=[]` not being stored; any decide rule letting a chain skip that
must run (no record, a FAIL at the key, a newer non-pass record, a partial record outside a prefix request, an
unresolved manifest, gate off) or not skipping when it may; purpose sweep / shadow mode skipping instead of
would_skip; a skipped chain not carrying freshness reused@<file>; index_run writing a SKIPPED chain or missing a
fresh one; audit_run missing a miss or calling drift a miss; record_misses writing a miss twice or an open miss
not forcing RUN (or clear-miss not re-allowing the skip); run_suite running a skipped chain body or calling such a
run fresh_green.
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
for _p in (UTILS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gate  # noqa: E402
import runner  # noqa: E402

FAILS = []


def ok(cond, what, got=None):
    print(("PASS  " if cond else "FAIL  ") + what + ("" if cond or got is None else "   got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def _w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


VALIDATION = '''"""temp suite for selftest_gate"""
import helper_x
from suite import Suite

suite = Suite("GateT")
LIMIT = 3


def shared():
    return LIMIT


@suite.chain("a")
def a(t):
    with t.component("r1"):
        shared()


@suite.chain("b")
def b(t):
    with t.component("r2"):
        helper_x.f()


@suite.chain("c")
def c(t):
    with t.component("r3"):
        if False:
            open("northstar/x.txt").read()


@suite.chain("d", inputs=["northstar/*.txt"])
def d(t):
    with t.component("r4"):
        if False:
            open("northstar/x.txt").read()


@suite.chain("e", inputs=[])
def e(t):
    with t.component("r5"):
        pass


@suite.chain("f", inputs=["nope/*.x"])
def f(t):
    with t.component("r6"):
        pass


@suite.chain("g", inputs=["?nope/*.x", "@mod_hash"])
def g(t):
    with t.component("r7"):
        pass
'''


class Mod(object):
    """A temp mod folder holding VALIDATION, helper_x.py and northstar/x.txt; load() re-imports the suite."""

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="gate_selftest_")
        self.dir = os.path.join(self.root, "GateT")
        self.hist = os.path.join(self.root, "hist")
        os.makedirs(self.hist)
        _w(os.path.join(self.dir, "validation.py"), VALIDATION)
        _w(os.path.join(self.dir, "helper_x.py"), "def f():\n    return 1\n")
        _w(os.path.join(self.dir, "northstar", "x.txt"), "one\n")
        self.env = {gate.ENV_HISTORY: self.hist}
        self.n = 0

    def edit(self, rel, old, new):
        p = os.path.join(self.dir, rel)
        with open(p, encoding="utf-8") as fh:
            s = fh.read()
        assert old in s, (rel, old)
        _w(p, s.replace(old, new))

    def load(self):
        self.n += 1
        sys.modules.pop("helper_x", None)
        if self.dir not in sys.path:
            sys.path.insert(0, self.dir)
        spec = importlib.util.spec_from_file_location("gate_t_validation_%d" % self.n,
                                                      os.path.join(self.dir, "validation.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m.suite

    def gate(self, env=None, index=None):
        s = self.load()
        e = dict(self.env, **(env or {}))
        return s, gate.Gate(s, "GateT", self.dir, [], {"situational": False}, environ=e, index=index)

    def keys(self):
        s, g = self.gate(index=[])
        return {n: g.manifest(n, fn)["key"] for n, fn in s.chains}

    def close(self):
        if self.dir in sys.path:
            sys.path.remove(self.dir)
        shutil.rmtree(self.root, ignore_errors=True)


def t_slice_isolation(m):
    k0 = m.keys()
    ok(len(set(k0.values())) == len(k0), "every chain has its own key", k0)
    ok(k0 == m.keys(), "keys are stable across a reload")
    m.edit("validation.py", 'with t.component("r2"):\n        helper_x.f()', 'with t.component("r2"):\n        helper_x.f()\n        pass')
    k1 = m.keys()
    ok(k1["b"] != k0["b"] and all(k1[n] == k0[n] for n in k0 if n != "b"),
       "editing chain b's body changes b's key only", sorted(n for n in k0 if k1[n] != k0[n]))
    m.edit("validation.py", "LIMIT = 3", "LIMIT = 4")
    k2 = m.keys()
    ok(k2["a"] != k1["a"] and all(k2[n] == k1[n] for n in k1 if n != "a"),
       "editing a constant only chain a uses (via shared()) changes a's key only",
       sorted(n for n in k1 if k2[n] != k1[n]))
    m.edit("helper_x.py", "return 1", "return 2")
    k3 = m.keys()
    ok(k3["b"] != k2["b"] and k3["a"] == k2["a"] and k3["e"] == k2["e"],
       "editing helper_x (imported in the preamble, used by b) changes b's key, not a's or e's",
       sorted(n for n in k2 if k3[n] != k2[n]))


def t_inputs(m):
    s, g = m.gate(index=[])
    man = {n: g.manifest(n, fn) for n, fn in s.chains}
    ok(not man["c"]["inputs_known"] and any(r.startswith("open@") for r in man["c"]["reads"]),
       "a chain that opens a file with no inputs= is inputs-unknown", man["c"]["reads"])
    ok(man["d"]["inputs_known"] and man["d"]["input_files"] == 1, "a declaration overrides the read scan",
       (man["d"]["inputs_known"], man["d"]["input_files"]))
    ok(s.chain_inputs.get("e") == [] and man["e"]["inputs_known"], "inputs=[] is stored and counts as known",
       s.chain_inputs.get("e"))
    ok(any("matches nothing" in u for u in man["f"]["unresolved"]), "a declared glob matching nothing is unresolved",
       man["f"]["unresolved"])
    ok(not man["g"]["unresolved"], "an optional ?glob matching nothing and @mod_hash resolve", man["g"]["unresolved"])
    d = g.decide("c", dict(s.chains)["c"])
    ok(d["action"] == gate.RUN and "inputs unknown" in d["why"], "decide: inputs unknown runs", d)
    d = g.decide("f", dict(s.chains)["f"])
    ok(d["action"] == gate.RUN and "unresolved" in d["why"], "decide: an unresolved manifest runs", d)
    k0 = {n: man[n]["key"] for n in man}
    m.edit(os.path.join("northstar", "x.txt"), "one", "two")
    k = m.keys()
    ok(k["d"] != k0["d"] and all(k[n] == k0[n] for n in "abcefg"),
       "editing a declared input outside the runtime and mod hash changes the declaring chain only",
       sorted(n for n in k if k[n] != k0[n]))
    m.edit("helper_x.py", "def f", "X = 1\n\n\ndef f")
    k2 = m.keys()
    ok(k2["g"] != k["g"] and k2["b"] != k["b"] and k2["a"] == k["a"],
       "a mod-root .py edit changes the @mod_hash chain and its importer, not a", sorted(n for n in k if k2[n] != k[n]))


def _rec(key, chain, cls="pass", stamp="20261025-100000", partial=False, rows=("r1",), file="GateT_x.json"):
    return {"key": key, "chain": chain, "class": cls, "stamp": stamp, "partial": partial, "rows": list(rows),
            "file": file, "mod": "GateT", "body_s": 12.5}


def t_decide(m):
    s, g = m.gate(index=[])
    fn = dict(s.chains)["a"]
    key = g.manifest("a", fn)["key"]

    def dec(index, env=None, scope=None):
        _, gg = m.gate(env=env, index=index)
        return gg.decide("a", dict(gg.suite.chains)["a"], scope)
    ok(dec([])["action"] == gate.RUN, "no record: run")
    ok(dec([_rec("other", "a")])["action"] == gate.RUN, "a record at another key: run")
    d = dec([_rec(key, "a")])
    ok(d["action"] == gate.SKIP and d["record"]["file"] == "GateT_x.json", "a pass at the key: skip (guard)", d)
    ok(dec([_rec(key, "a")], env={gate.ENV_PURPOSE: "fix"})["action"] == gate.SKIP, "purpose fix: skip")
    for p in gate.ADVISORY_PURPOSES:
        ok(dec([_rec(key, "a")], env={gate.ENV_PURPOSE: p})["action"] == gate.WOULD,
           "purpose %s: would_skip, never skip" % p)
    ok(dec([_rec(key, "a")], env={gate.ENV_MODE: "shadow"})["action"] == gate.WOULD, "shadow: would_skip")
    ok(dec([_rec(key, "a")], env={gate.ENV_MODE: "off"})["action"] == gate.RUN, "gate off: run")
    ok(dec([_rec(key, "a"), _rec(key, "a", cls="fail", stamp="20261024-000000")])["action"] == gate.RUN,
       "any FAIL at the key, even older: run (flake guard)")
    ok(dec([_rec(key, "a"), _rec(key, "a", cls="other", stamp="20261026-000000")])["action"] == gate.RUN,
       "a newer non-pass record at the key: run")
    ok(dec([_rec(key, "a", cls="other", stamp="20261024-000000"), _rec(key, "a")])["action"] == gate.SKIP,
       "an older non-pass record under a newer pass: skip")
    part = [_rec(key, "a", partial=True, rows=("r1",))]
    ok(dec(part)["action"] == gate.RUN, "a partial pass: run for a whole-chain request")
    ok(dec(part, scope={"mode": "prefix", "requested_rows": ["r1"]})["action"] == gate.SKIP,
       "a partial pass covering a prefix request: skip")
    ok(dec(part, scope={"mode": "prefix", "requested_rows": ["r1", "r9"]})["action"] == gate.RUN,
       "a partial pass not covering the prefix request: run")


def _comp(name, verdict="PASS", **kw):
    return dict({"name": name, "verdict": verdict, "detail": "", "execution": "ran", "validity": None}, **kw)


def t_classify():
    ok(gate.classify({"components": [_comp("x")]}) == "pass", "classify: all PASS is pass")
    ok(gate.classify({"components": [_comp("x"), _comp("y", "UNMEASURED", detail="UNMEASURED: live check owed")]})
       == "pass", "classify: PASS plus an owed UNMEASURED is pass")
    ok(gate.classify({"components": [_comp("x"), _comp("y", "UNMEASURED", detail="no map")]}) == "other",
       "classify: PASS plus an unexplained UNMEASURED is other")
    ok(gate.classify({"components": [_comp("x", "FAIL")]}) == "fail", "classify: a FAIL is fail")
    ok(gate.classify({"components": [_comp("x", "FAIL", validity="invalid")]}) == "invalid",
       "classify: a voided FAIL is invalid, not fail")
    ok(gate.classify({"components": [_comp("x")], "situational": {"runValidity": {"verdict": "DISRUPTED"}}})
       == "other", "classify: a disrupted run is other")


def t_index_reuse_audit(m):
    s, g = m.gate(index=[])
    key = g.manifest("a", dict(s.chains)["a"])["key"]
    first = os.path.join(m.hist, "GateT_20261025-100000.json")
    summary = {"chains": [
        {"name": "a", "components": [_comp("r1")], "phase_s": {"body": 7.0},
         "gate": {"action": gate.RUN, "key": key, "purpose": "sweep"}},
        {"name": "b", "components": [_comp("r2")], "gate": {"action": gate.SKIP, "key": "kb"}},
        {"name": "c", "components": [_comp("r3")]}]}
    with open(first, "w", encoding="utf-8") as fh:
        json.dump({"mod": "GateT", "summary": summary}, fh)
    n = gate.index_run("GateT", summary, first)
    idx = [r for _, r in gate.load_index([m.hist])]
    ok(n == 1 and [r["chain"] for r in idx] == ["a"] and idx[0]["class"] == "pass" and idx[0]["body_s"] == 7.0,
       "index_run: only the freshly run chain with a key is indexed", idx)
    with open(os.path.join(m.hist, gate.INDEX), "a", encoding="utf-8") as fh:
        fh.write('{"torn\n')
    ok(len(gate.load_index([m.hist])) == 1, "load_index skips a torn line")
    _, g2 = m.gate()
    d = g2.decide("a", dict(g2.suite.chains)["a"])
    ok(d["action"] == gate.SKIP, "the indexed pass makes the chain skippable from MODCHECK_GATE_HISTORY", d)
    ch = g2.reused_chain("a", d)
    ok(ch is not None and ch["components"][0]["freshness"] == "reused@GateT_20261025-100000.json"
       and ch["gate"]["action"] == gate.SKIP and ch["phase_s"]["body"] == 0.0,
       "reused_chain: rows from the record, freshness reused@<file>", ch)
    rec = {"file": os.path.basename(first)}
    now = {"chains": [
        {"name": "a", "components": [_comp("r1", "FAIL")], "gate": {"action": gate.WOULD, "record": rec}},
        {"name": "b", "components": [_comp("r1", "UNMEASURED")], "gate": {"action": gate.WOULD, "record": rec}},
        {"name": "c", "components": [_comp("r1")], "gate": {"action": gate.RUN}}]}
    au = gate.audit_run({"summary": now}, dirs=[m.hist])
    ok(au["would_skip"] == 2 and len(au["misses"]) == 1 and au["misses"][0].startswith("a/r1: FAIL now"),
       "audit_run: a FAIL now on a would_skip chain is a miss", au)
    ok(au["unreadable"] == [] and au["drift"] == ["b/r1: absent -> UNMEASURED"],
       "audit_run: a row the record lacks, not FAIL now, is drift, not a miss", au)


def t_audit_drift(m):
    p = os.path.join(m.hist, "GateT_20261025-110000.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"summary": {"chains": [{"name": "a", "components": [_comp("r1"), _comp("r2", "UNMEASURED")]}]}}, fh)
    rec = {"file": os.path.basename(p)}
    au = gate.audit_run({"chains": [{"name": "a", "gate": {"action": gate.WOULD, "record": rec},
                                     "components": [_comp("r1", "UNMEASURED"), _comp("r2")]}]}, dirs=[m.hist])
    ok(au["misses"] == ["a/r1: UNMEASURED now, PASS in record"] and au["drift"] == ["a/r2: UNMEASURED -> PASS"],
       "audit_run: PASS lost is a miss, UNMEASURED->PASS is drift", au)
    # the report's rates come from SHADOW runs only; a targeted/on run is informational, and no shadow run says so
    sh = {"summary": {"gate": {"mode": "shadow"}, "chains": [
        {"name": "a", "components": [_comp("r1", "FAIL")], "gate": {"action": gate.WOULD, "record": rec}},
        {"name": "z", "components": [_comp("r1")], "gate": {"action": gate.RUN}}]}}
    on = {"summary": {"gate": {"mode": "on"}, "chains": [
        {"name": "a", "components": [_comp("r1", "FAIL")], "gate": {"action": gate.WOULD, "record": rec}}]}}
    rep = gate.audit_report([("sh.json", sh), ("on.json", on)], dirs=[m.hist])
    ok(rep[0].startswith("runs 2: 1 in shadow, 1 not") and not any(l.startswith("NO SHADOW") for l in rep)
       and "chains 2, would_skip 1 (skip rate 50%), misses 1 in 1 chain(s) (miss rate 100%)" in rep[1]
       and any(l.startswith("OTHER") and "misses 1" in l for l in rep) and any(l.startswith("  shadow miss sh.json: a/r1") for l in rep),
       "audit_report: rates over the shadow runs, other runs apart, a miss labelled 'miss'", rep)
    rep2 = gate.audit_report([("on.json", on)], dirs=[m.hist])
    ok(any(l.startswith("NO SHADOW RUN") for l in rep2) and "would_skip 0 (skip rate 0%)" in rep2[2],
       "audit_report: with no shadow run it says the rates are not the section 9 audit", rep2)
    rep3 = gate.audit_report([("sh1.json", sh), ("sh2.json", sh)], dirs=[m.hist])
    ok("would_skip 2 (skip rate 50%), misses 2 in 2 chain(s) (miss rate 100%)" in rep3[1],
       "audit_report: the same chain missed in two shadow runs is two misses of two would_skips, not 50%", rep3)
    # a deliberate sweep with the gate on and an advisory purpose skips nothing: it measures the gate like shadow
    cm = {"summary": {"gate": {"mode": "on", "purpose": "commission"}, "chains": sh["summary"]["chains"]}}
    rep4 = gate.audit_report([("cm.json", cm)], dirs=[m.hist])
    ok(rep4[0].startswith("runs 1: 1 in shadow") and not any(l.startswith("NO SHADOW") for l in rep4)
       and "would_skip 1 (skip rate 50%)" in rep4[1],
       "audit_report: a gate-on run with purpose commission is a measuring (shadow) run", rep4)


def t_run_suite(m):
    from selftest import _fake_session
    from selftest_reuse import _Sess
    s, g = m.gate(index=[])
    ka = g.manifest("a", dict(s.chains)["a"])["key"]
    p = os.path.join(m.hist, "GateT_20261025-120000.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"summary": {"chains": [{"name": "a", "components": [_comp("r1")]}]}}, fh)
    idx = [_rec(ka, "a", file=os.path.basename(p))]
    for env, skipped in (({}, True), ({gate.ENV_PURPOSE: "sweep"}, False)):
        s2, g2 = m.gate(env=env, index=idx)
        ran = []
        for name, fn in list(s2.chains):
            if name not in ("a", "e"):
                s2.chains.remove((name, fn))
        sess = _fake_session()
        fake = _Sess()
        sess.call, sess.things_at = fake.call, fake.things_at
        with contextlib.redirect_stderr(io.StringIO()):
            res = runner.run_suite(s2, sess, anchor=(5, 5), gate=g2)
        by = {ch["name"]: ch for ch in res["chains"]}
        ran = [n for n, ch in by.items() if (ch.get("phase_s") or {}).get("body")]
        if skipped:
            ok(res["gate"]["skipped"] == ["a"] and res["gate"]["run"] == ["e"]
               and by["a"]["components"][0]["freshness"].startswith("reused@") and not res["fresh_green"],
               "run_suite guard: a known-good chain is skipped, reused, and the run is not fresh_green",
               (res["gate"], res.get("fresh_green")))
        else:
            ok(res["gate"]["would_skip"] == ["a"] and not res["gate"]["skipped"]
               and not str(by["a"]["components"][0].get("freshness") or "").startswith("reused@"),
               "run_suite sweep: the chain runs and is marked would_skip", res["gate"])
        ok(all("gate" in ch for ch in res["chains"]), "run_suite: every chain carries a gate stamp", ran)


def t_misses(m):
    """record_misses writes each audit miss once; an open miss makes decide RUN where it would SKIP; clear_miss
    re-allows the skip and refuses without a reason."""
    s, g = m.gate(index=[])
    ka = g.manifest("a", dict(s.chains)["a"])["key"]
    p = os.path.join(m.hist, "GateT_20261025-130000.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"summary": {"chains": [{"name": "a", "components": [_comp("r1")]}]}}, fh)
    idx = [_rec(ka, "a", file=os.path.basename(p))]
    _, g0 = m.gate(index=idx)
    ok(g0.decide("a", dict(g0.suite.chains)["a"])["action"] == gate.SKIP, "misses: no open miss, the chain skips")
    rec = {"file": os.path.basename(p)}
    now = {"chains": [{"name": "a", "components": [_comp("r1", "FAIL")],
                       "gate": {"action": gate.WOULD, "record": rec, "key": ka}}]}
    jp = os.path.join(m.hist, "GateT_20261025-140000.json")
    w1 = gate.record_misses("GateT", now, jp, dirs=[m.hist])
    w2 = gate.record_misses("GateT", now, jp, dirs=[m.hist])
    om = gate.open_misses([m.hist])
    ok(len(w1) == 1 and w1[0]["key"] == ka and w2 == [] and list(om) == [("GateT", "a")],
       "record_misses: one line per miss, not rewritten on a second call; open_misses sees it", (w1, w2, om))
    _, g1 = m.gate(index=idx)
    d = g1.decide("a", dict(g1.suite.chains)["a"])
    ok(d["action"] == gate.RUN and "miss" in d["why"], "decide: an open miss forces RUN over a usable record", d)
    try:
        gate.clear_miss("GateT", "a", "  ", base=m.hist)
        ok(False, "clear_miss refuses an empty --why")
    except ValueError:
        ok(True, "clear_miss refuses an empty --why")
    gate.clear_miss("GateT", "a", "declared the missing input", base=m.hist)
    ok(gate.open_misses([m.hist]) == {}, "clear_miss closes the open miss")
    _, g2 = m.gate(index=idx)
    ok(g2.decide("a", dict(g2.suite.chains)["a"])["action"] == gate.SKIP, "after clear-miss the chain skips again")


def main():
    # Hermetic: the real MINIMAL list names repo mods whose runtime hash is read from the live tree, so another seat
    # editing one mid-run changed a manifest key between two calls. Pin the list to an id that is no repo mod.
    gate.minimal_ids = lambda path=None: ["ludeon.rimworld"]
    m = Mod()
    try:
        for t in (t_slice_isolation, t_inputs, t_decide, t_classify, t_index_reuse_audit, t_audit_drift, t_misses, t_run_suite):
            try:
                t(m) if t is not t_classify else t()
            except Exception as ex:     # noqa: BLE001 - one broken test must not hide the others
                import traceback
                traceback.print_exc()
                ok(False, "%s raised %s: %s" % (t.__name__, type(ex).__name__, ex))
    finally:
        m.close()
    print("\nSELFTEST %s -- %d failed" % ("FAILED" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
