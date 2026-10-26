#!/usr/bin/env python3
"""Selftest for proof_restore_check.py: a live proof must undo every def / Mod Settings poke on EVERY exit path,
putting back the value it found (never a hard-coded default).

1. The two proofs fixed at 0a6567cce8 (RM_KineticArmsProof, RM_KnockbackProof) are flagged as they were before the
   fix and are clean as fixed (fixtures under selftest_fixtures/proof_restore/).
2. The Python detector on small synthetic drivers: unguarded write, try/finally restore of the captured prior,
   DEFAULTS restore, Settings("reset") with and without t.remember_settings, a static-call write the suite cannot
   see, a waiver, a captured prior that starts as None.
3. modcheck/suite.py itself, with a fake session: a chain that writes settings through set_setting AND through a
   script's own t.session.call, then fails a component and throws, leaves every field at the player's value.
4. The whole repo: no hit outside proof_restore_check.BASELINE (each baseline key names its filed item).
"""
import os
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import proof_restore_check as prc  # noqa: E402

FIX = os.path.join(HERE, "selftest_fixtures", "proof_restore")
fails = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name, ("  -- %s" % detail) if detail and not ok else ""))
    if not ok:
        fails.append(name)


def kinds(hits):
    return sorted({h["kind"] for h in hits})


# ---------------------------------------------------------------- 1. C# fixtures: old flagged, fixed clean
def cs(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return prc.check_cs(name, f.read())


ka_pre, ka_at = cs("RM_KineticArmsProof_pre0a6567cce8.cs.fixture"), cs("RM_KineticArmsProof_at0a6567cce8.cs.fixture")
kb_pre, kb_at = cs("RM_KnockbackProof_pre0a6567cce8.cs.fixture"), cs("RM_KnockbackProof_at0a6567cce8.cs.fixture")
check("KineticArms pre-fix: pokes flagged (>= 5)", len(ka_pre) >= 5, [h["line"] for h in ka_pre])
check("KineticArms pre-fix: strength 0 unrestored on throw",
      any(h["kind"] == "unrestored-on-throw" and "kineticStrength" in h["target"] for h in ka_pre), ka_pre)
check("KineticArms fixed: clean", not ka_at, ka_at)
check("Knockback pre-fix: flagged (>= 4)", len(kb_pre) >= 4, [h["line"] for h in kb_pre])
check("Knockback pre-fix: hard-coded restore (=60 / =true) flagged",
      sum(h["kind"] == "restores-fixed-value" for h in kb_pre) >= 2, kinds(kb_pre))
check("Knockback pre-fix: restore delegate never run on a throw",
      any(h["kind"] == "restore-delegate-not-run-on-throw" for h in kb_pre), kinds(kb_pre))
check("Knockback fixed: clean", not kb_at, kb_at)

# a minimal C# poke: before the try it leaks; inside a try whose finally writes it back it does not
LEAK_CS = textwrap.dedent("""
    public static class P {
        public static string Run() {
            bool was = FooSettings.enabled;
            FooSettings.enabled = false;
            Build();
            try { Check(); } finally { FooSettings.enabled = was; }
            return "";
        }
    }""")
OK_CS = LEAK_CS.replace("FooSettings.enabled = false;\n        Build();\n        try { Check(); }",
                        "try { FooSettings.enabled = false; Build(); Check(); }")
assert OK_CS != LEAK_CS
check("C#: poke followed by a call before the try is a leak", kinds(prc.check_cs("x.cs", LEAK_CS)) == ["unrestored-on-throw"],
      prc.check_cs("x.cs", LEAK_CS))
check("C#: poke inside the try is clean", prc.check_cs("x.cs", OK_CS) == [], prc.check_cs("x.cs", OK_CS))


# ---------------------------------------------------------------- 2. Python detector
def py(src, harness=True, tracks=True):
    src = textwrap.dedent(src)
    return [h for h in prc.check_py("x.py", src, harness, tracks) if not prc.waived(src, h["line"])]


RAW = 'b.call("jawa/mod_settings_field", typeName=T, action="set", field="on", value="false")'
check("py: raw write outside any try is unrestored",
      kinds(py("def run(b):\n    %s\n    scenes(b)\n" % RAW)) == ["unrestored-on-throw"])
check("py: write inside try whose finally restores the captured prior is clean",
      py('''
         def run(b):
             old = b.call("jawa/mod_settings_field", typeName=T, action="get", field="on")["value"]
             try:
                 %s
                 scenes(b)
             finally:
                 b.call("jawa/mod_settings_field", typeName=T, action="set", field="on", value=str(old))
         ''' % RAW) == [])
check("py: a finally that writes DEFAULTS[...] restores a fixed value",
      kinds(py('''
         def run(b):
             try:
                 %s
             finally:
                 b.call("jawa/mod_settings_field", typeName=T, action="set", field="on", value=str(DEFAULTS["on"]))
         ''' % RAW)) == ["restores-fixed-value"])
check("py: a local bound to DEFAULTS is still a fixed restore",
      kinds(py('''
         def restore(b, f):
             want = P.DEFAULTS[f]
             b.call("jawa/mod_settings_field", typeName=T, action="set", field=f, value=str(want))
         ''')) == ["restores-fixed-value"])
check("py: `prior if prior is not None else DEFAULT` restores the prior",
      py('''
         def restore(b, changed):
             for f, before in changed.items():
                 want = before if before is not None else P.DEFAULTS[f]
                 b.call("jawa/mod_settings_field", typeName=T, action="set", field=f, value=str(want))
         ''') == [])
check("py: a prior that starts as None and is then read is not fixed",
      py('''
         def run(b):
             old = None
             try:
                 old = b.call("jawa/mod_settings_field", typeName=T, action="get", field="on").get("value")
                 %s
             finally:
                 if old is not None:
                     b.call("jawa/mod_settings_field", typeName=T, action="set", field="on", value=str(old))
         ''' % RAW) == [])
check("py: setter wrapper call sites are the pokes",
      [h["line"] for h in py('''
         def _sset(b, field, value):
             b.call("jawa/mod_settings_field", typeName=T, action="set", field=field, value=str(value))
         def run(b):
             _sset(b, "on", False)
             scenes(b)
         ''')] == [5])
check("py: a setter-wrapper poke restored by a setter-wrapper call in the finally is clean; without the finally it is a hit",
      [py('''
         def _sset(b, field, value):
             b.call("jawa/mod_settings_field", typeName=T, action="set", field=field, value=str(value))
         def run(b, prior):
             try:
                 _sset(b, "on", False)
                 scenes(b)
             finally:
                 _sset(b, "on", prior)
         '''), [h["line"] for h in py('''
         def _sset(b, field, value):
             b.call("jawa/mod_settings_field", typeName=T, action="set", field=field, value=str(value))
         def run(b, prior):
             _sset(b, "on", False)
             scenes(b)
             _sset(b, "on", prior)
         ''')]] == [[], [5, 7]])
check("py: the mailbox field `request` is not a setting",
      py('def run(b):\n    b.call("jawa/mod_settings_field", typeName=T, action="set", field="request", value="x")\n') == [])
check("py: Settings(\"reset\") outside any guard loses the player's values",
      kinds(py('def run(b):\n    call(b, "Settings", "reset")\n')) == ["reset-loses-player-values"])
SUITE_SRC = '''
    from modcheck import Suite
    suite = Suite("x")
    @suite.chain("c")
    def c(t):
        %s
        _call(t, "Settings", "reset")
    '''
check("py: reset in a suite chain without remember_settings is flagged",
      kinds(py(SUITE_SRC % "pass")) == ["reset-loses-player-values"])
check("py: reset after t.remember_settings in a suite chain is clean",
      py(SUITE_SRC % 't.remember_settings("T", ["on"])') == [])
T_RAW = '''
    from modcheck import Suite
    suite = Suite("x")
    def _put(t, f, v):
        t.session.call("jawa/mod_settings_field", typeName=T, action="set", field=f, value=v)
    @suite.chain("c")
    def c(t):
        t.session.call("jawa/mod_settings_field", typeName=T, action="set", field="on", value="false")
        _put(t, "on", "true")
    '''
check("py: a settings write through t in a suite chain is restored by the harness", py(T_RAW) == [], py(T_RAW))
check("py: ... and is a leak when the harness does not track it", len(py(T_RAW, tracks=False)) == 2,
      py(T_RAW, tracks=False))
check("py: a static-call Settings(\"f=v\") through t is invisible to the harness: still flagged",
      kinds(py(SUITE_SRC.replace('_call(t, "Settings", "reset")', '_call(t, "Settings", "enabled=false")') % "pass"))
      == ["unrestored-on-throw"])
check("py: harness set_setting is guarded only when suite.py restores",
      py("def c(t):\n    t.set_setting(T, {'on': False})\n") == [] and
      kinds(py("def c(t):\n    t.set_setting(T, {'on': False})\n", harness=False)) == ["unrestored-on-throw"])
check("py: a `restore-check: ok` waiver on the line above silences one hit",
      py("def run(b):\n    # restore-check: ok -- caller restores\n    %s\n" % RAW) == [])

# ---------------------------------------------------------------- 3. suite.py restores the PRIOR value
from modcheck import suite as S  # noqa: E402


class FakeSession(object):
    def __init__(self, values):
        self.values = dict(values)
        self.calls = []

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool == "jawa/mod_settings_field":
            key = (kw["typeName"], kw["field"])
            if kw.get("action") == "set":
                self.values[key] = str(kw["value"])
                return {"success": True}
            return {"success": True, "value": self.values.get(key)}
        return {"success": True}


check("suite.py source: restore in chain's finally + tracking session",
      prc.suite_restores(open(S.__file__, encoding="utf-8").read()) and
      prc.suite_tracks(open(S.__file__, encoding="utf-8").read()))
sess = FakeSession({("T", "a"): "7", ("T", "b"): "True", ("T", "c"): "0.5", ("U", "r"): "3"})
st = S.Suite("restore_selftest")


@st.chain("pokes_then_throws")
def _chain(t):
    t.set_setting("T", {"a": 1})
    t.session.call("jawa/mod_settings_field", typeName="T", action="set", field="b", value="False")
    t.bridge_call("jawa/mod_settings_field", typeName="T", action="set", field="c", value="9")
    t.remember_settings("U", ["r"])
    sess.values[("U", "r")] = "0"                     # a proof's Settings("reset") rewriting it behind the bridge
    t.upstream_failed = True                          # a failed component: every later verb is a no-op ...
    raise RuntimeError("scene threw")                 # ... and then the script throws


ctx = S.TestContext(sess)
try:
    st.chains[0][1](ctx)
    check("suite: chain threw", False)
except RuntimeError:
    pass
want = {("T", "a"): "7", ("T", "b"): "True", ("T", "c"): "0.5", ("U", "r"): "3"}
check("suite: every field the chain touched is back at the player's value", sess.values == want, sess.values)
check("suite: the context's session is the caller's again", ctx.session is sess)
sess2 = FakeSession({("T", "a"): "7"})
ctx2 = S.TestContext(sess2)
ctx2._restore_touched_settings()
check("suite: nothing touched, nothing written", not any(k.get("action") == "set" for _, k in sess2.calls))

# ---------------------------------------------------------------- 4. the repo
hits, seen, harness = prc.scan()
new = prc.new_hits(hits)
check("repo: the scanner sees proofs (sanity: >= 40 C#, >= 100 py)", seen["cs"] >= 40 and seen["py"] >= 100, seen)
check("repo: no restore-leak outside the filed baseline", not new,
      "; ".join("%s:%d %s" % (h["path"], h["line"], h["kind"]) for h in new[:10]))
have = {}
for h in hits:
    have[prc.key(h)] = have.get(prc.key(h), 0) + 1
stale = sorted(k for k, (_, n) in prc.BASELINE.items() if have.get(k, 0) < n)
check("repo: no stale baseline entry (a fixed hit lowers or removes its count)", not stale, stale)
fake = [{"path": "a.py", "kind": "unrestored-on-throw", "target": "raw", "line": i} for i in (3, 9, 12)]
check("baseline: a filed key hides only as many hits as it had when filed",
      [h["line"] for h in prc.new_hits(fake, {"a.py::unrestored-on-throw::raw": ("X", 2)})] == [12])

print("selftest_proof_restore_check: %s (%d failure(s))" % ("PASS" if not fails else "FAIL", len(fails)))
sys.exit(1 if fails else 0)
