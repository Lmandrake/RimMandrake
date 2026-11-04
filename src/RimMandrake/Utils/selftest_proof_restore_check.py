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
5. A waiver is a claim, and the scanner takes it on trust: `restore-check: ok` silences a hit whether or not the restore
   exists (blind check of NIGHTLY_COP_FIX_RED_CYJJIB_ARBP, a real leak with the comment left in stayed green). So the
   waivers that item wrote are proved here. The LeaningScrub repros run their real live() against a fake bridge; every
   touched setting must end at its prior, on a full run, a throw, a refused spawn and a write that did not take. Each C#
   waiver is read structurally: every caller of the waived write sits in a try whose finally writes the captured prior.
6. The mutants of that blind check, and their neighbours, applied to the real sources in memory: each must go red.
"""
import contextlib
import io
import os
import re
import sys
import textwrap
import types

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

# ---------------------------------------------------------------- 5. the waived restores exist and put back the prior
SRC = os.path.normpath(os.path.join(HERE, ".."))
CROWN = os.path.join(SRC, "LeaningScrub", "repro_crown_mob.py")
STALL = os.path.join(SRC, "LeaningScrub", "repro_stall_move.py")
LEAN = os.path.join(SRC, "LeaningScrub", "Source", "RM_TheLeanProof.cs")
LUMINOUS = os.path.join(SRC, "LuminousPigment", "Source", "RM_LuminousFamilySettingsProbe.cs")
VERBS = os.path.join(SRC, "RimProperty", "Source", "RM_SettlementVerbsProof.cs")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class BridgeError(Exception):
    pass


class FakeGame(object):
    """The bridge as far as the repros use it. `fail` = (tool, nth, mode), one shot: 'raise' throws after the call took
    effect (a settings write has landed), 'refuse' answers {} and 'drop' ignores a settings write. A settings tool is
    named 'set' for this count, so a get never spends the shot."""

    def __init__(self, priors, fail=None):
        self.values = dict(priors)
        self.fail, self.seen, self.fired = fail, {}, False
        self.tick, self.next_id, self.pawns = 1000, 1, {}
        self.weather, self.locked = "Clear", False
        self.spawned, self.diverged = 0, set()
        self.priors = dict(priors)

    def call(self, tool, kw):
        name = "set" if tool == "jawa/mod_settings_field" and kw.get("action") == "set" else tool
        self.seen[name] = self.seen.get(name, 0) + 1
        mode = None
        if self.fail and not self.fired and self.fail[0] == name and self.fail[1] == self.seen[name]:
            self.fired, mode = True, self.fail[2]
        if mode == "refuse":
            return {}
        out = self.answer(tool, kw, drop=mode == "drop")
        if mode == "raise":
            raise RuntimeError("fake throw at %s #%d" % (name, self.seen[name]))
        return out

    def answer(self, tool, kw, drop=False):
        if tool == "jawa/mod_settings_field":
            if kw.get("action") == "get":
                return {"success": True, "value": self.values.get(kw["field"])}
            if not drop:
                self.values[kw["field"]] = str(kw["value"])
                if str(kw["value"]) != self.priors.get(kw["field"]):
                    self.diverged.add(kw["field"])
            return {"success": True}
        if tool == "rimworld/get_game_info":
            return {"ticksGame": self.tick}
        if tool == "rimworld/step_game_ticks":
            self.tick += kw["ticks"]
        elif tool == "jawa/map_info":
            return {"sizeX": 250, "sizeZ": 250, "mapBiome": "AridShrubland", "tile": 1}
        elif tool == "jawa/weather_set":
            if kw.get("weather"):
                self.weather = kw["weather"]
            if kw.get("lockWeather"):
                self.locked = True
            if kw.get("unlock"):
                self.locked = False
        elif tool == "jawa/weather_get":
            return {"weather": self.weather}
        elif tool == "jawa/list_things":
            return {"things": [{"def": kw["defName"]}] if kw.get("defName") == "RM_CrownVenomvine" else []}
        elif tool == "jawa/spawn_pawn":
            pid = "p%d" % self.next_id
            self.next_id += 1
            self.spawned += 1
            self.pawns[pid] = {"id": pid, "x": kw["x"], "z": kw["z"], "kindDef": kw["kindDef"], "intelligence": "Animal"}
            return {"pawns": [{"id": pid}]}
        elif tool == "jawa/list_pawns":
            return {"pawns": list(self.pawns.values())}
        elif tool == "jawa/site_state":
            return {"pawns": [{"id": k, "job": "Wait_Wander"} for k in self.pawns]}
        elif tool == "jawa/pawn_force_incapacitate":
            self.pawns.pop(kw["pawn"], None)
        return {"success": True}


def run_live(source, path, game):
    """The file's real live(), from `source` (the file or a mutant of it), on the fake bridge. -> exit code or the throw."""
    fake = types.ModuleType("rimbridge_client")
    fake.RimBridgeError = BridgeError
    fake.resolve_endpoint = lambda: ("fake", 0, "fake")

    class Client(object):
        def __init__(self, **_):
            pass

        def connect(self):
            pass

        def call(self, tool, kw):
            return game.call(tool, kw)

    fake.RimBridge = Client
    mod = types.ModuleType("repro_under_test")
    mod.__file__ = path
    was, path_was = sys.modules.get("rimbridge_client"), list(sys.path)
    sys.modules["rimbridge_client"] = fake
    try:
        exec(compile(source, path, "exec"), mod.__dict__)
        with contextlib.redirect_stdout(io.StringIO()):
            return mod.live(None)
    except RuntimeError as e:
        return e
    finally:
        sys.path[:] = path_was
        if was is None:
            del sys.modules["rimbridge_client"]
        else:
            sys.modules["rimbridge_client"] = was


CROWN_FIELDS = ("crownMobEnabled", "runwayBloomEnabled", "leanScentEnabled", "stallFreezeEnabled")
STALL_FIELDS = ("leanScentEnabled",)
# where a run can go wrong after the first poke: (tool, nth, mode, expected end). 'throws' must propagate as the throw.
CROWN_ENDS = [("set", 1, "raise", "throws"), ("set", 3, "raise", "throws"), ("set", 6, "raise", "throws"),
              ("rimworld/step_game_ticks", 1, "raise", "throws"), ("rimworld/step_game_ticks", 90, "raise", "throws"),
              ("jawa/spawn_pawn", 1, "raise", "throws"), ("jawa/spawn_pawn", 8, "raise", "throws"),
              ("jawa/pawn_force_incapacitate", 1, "raise", "throws"),
              ("jawa/spawn_pawn", 2, "refuse", "code2"), ("set", 5, "drop", "code2")]     # #5 is mob_off's crownMob=False
STALL_ENDS = [("set", 1, "raise", "throws"), ("set", 2, "raise", "throws"),
              ("rimworld/step_game_ticks", 1, "raise", "throws"), ("rimworld/step_game_ticks", 15, "raise", "throws"),
              ("jawa/spawn_pawn", 1, "raise", "throws"), ("jawa/spawn_pawn", 3, "raise", "throws"),
              ("jawa/spawn_pawn", 2, "refuse", "code2"), ("set", 2, "drop", "returns")]   # the OFF arm did not take: ON's verdict stands


def live_problems(source, path, fields, ends, full_spawns):
    """Every way the repro left the game not as it found it, on every prior and exit path. [] = it held."""
    out = []
    for prior in ("False", "True"):
        priors = dict((f, prior) for f in fields)
        for end in [None] + ends:
            game = FakeGame(priors, end[:3] if end else None)
            got = run_live(source, path, game)
            tag = "prior=%s %s" % (prior, "full run" if end is None else "%s #%d %s" % end[:3])
            if end is None:
                if isinstance(got, Exception):
                    out.append("%s: threw %s" % (tag, got))
                if game.spawned != full_spawns:          # the fake must have driven every arm, or this row is blind
                    out.append("%s: %d spawns, want %d" % (tag, game.spawned, full_spawns))
            elif not game.fired:
                out.append("%s: the failure never fired, so this row proved nothing" % tag)
            elif end[3] == "throws" and not isinstance(got, Exception):
                out.append("%s: the throw did not propagate (%r)" % (tag, got))
            elif end[3] == "code2" and got != 2:
                out.append("%s: exit %r, want 2 (UNMEASURED)" % (tag, got))
            elif end[3] == "returns" and isinstance(got, Exception):
                out.append("%s: threw %s" % (tag, got))
            if game.values != priors:
                out.append("%s: settings left at %s" % (tag, game.values))
            if game.locked:
                out.append("%s: weather left locked" % tag)
            if prior == "False" and not game.diverged:
                out.append("%s: no setting ever left its prior, so this row proved nothing" % tag)
    return out


def crown_problems(source):
    return live_problems(source, CROWN, CROWN_FIELDS, CROWN_ENDS, 15)


def stall_problems(source):
    return live_problems(source, STALL, STALL_FIELDS, STALL_ENDS, 4)


def method_of(f, p):
    """The method body around position p: the outermost enclosing block with a parameter list."""
    return next((b for b in f.enclosing(p) if re.search(r"\b(static|private|public|internal)\b.*\(", b[2])), None)


def caller_restore_problems(text, callee, field, prior, also=()):
    """Every call of `callee` sits in a try whose finally writes `field = prior`; `prior` is captured once from `field`
    before that try and never reassigned. `also`: regexes that finally must match too. Comments and strings are blanked
    first, so a commented-out restore is no restore."""
    f = prc.CsFile(text)
    sites = [m for m in re.finditer(r"(?<![\w.])%s\s*\(" % re.escape(callee), f.s)
             if not re.search(r"\b(void|string|bool|int)\s+$", f.s[max(0, m.start() - 12):m.start()])]
    out = [] if sites else ["%s: no call site" % callee]
    write = r"(?<![\w.])%s\s*=(?!=)\s*%s\s*;" % (re.escape(field), re.escape(prior))
    for m in sites:
        at = f.line(m.start())
        guard = None
        for b in reversed(f.enclosing(m.start())):
            if b[2] == "try":
                fin = f.after_try(b[1])[1]
                if fin and re.search(write, f.s[fin[0]:fin[1]]):
                    guard = (b, fin)
                    break
        if guard is None:
            out.append("%s at line %d: no enclosing try whose finally writes %s = %s" % (callee, at, field, prior))
            continue
        tail = f.s[guard[1][0]:guard[1][1]]
        out += ["%s at line %d: the finally lacks %s" % (callee, at, rx) for rx in also if not re.search(rx, tail)]
        meth = method_of(f, m.start())
        body = f.s[meth[0]:meth[1]]
        capture = r"(?<![\w.])%s\s*=\s*(?:\([^)]*\)\s*)?%s\b" % (re.escape(prior), re.escape(field))
        if not re.search(capture, f.s[meth[0]:guard[0][0]]):
            out.append("%s at line %d: %s is not captured from %s before the try" % (callee, at, prior, field))
        if len(re.findall(r"(?<![\w.])%s\s*(?:=(?!=)|\+=|-=)" % re.escape(prior), body)) != 1:
            out.append("%s at line %d: %s is written more than once" % (callee, at, prior))
    return out


def lean_problems(text):
    return caller_restore_problems(text, "Arm", "RM_LeaningScrubSettings.leanFireEnabled", "savedFire")


def luminous_problems(text):
    return caller_restore_problems(text, "SetAllOnExcept", "LuminousPigmentSettings.familyEnabled", "snapshot",
                                   also=[r"File\.WriteAllText\(\s*file\s*,\s*pre\s*\)",
                                         r"LoadedModManager\.ReadModSettings<LuminousPigmentSettings>\(",
                                         r"LuminousPigmentMod\.settings\.Write\(\s*\)"])


VERB_FIELDS = {"salvageClaimFeeEnabled", "walkableCommerceEnabled", "pickpocketEnabled", "bribeEnabled"}


def verbs_problems(text):
    """The setter lambdas only reach ToggleOff, paired with a getter of the SAME field; ToggleOff captures on entry,
    writes false, and its finally puts back what it captured."""
    f = prc.CsFile(text)
    calls = re.findall(r"(?<![\w.])ToggleOff\(\s*\(\)\s*=>\s*PropertySettings\.(\w+)\s*,\s*v\s*=>\s*PropertySettings\.(\w+)"
                       r"\s*=\s*v\s*,", f.s)
    out = ["ToggleOff getter %s paired with setter %s" % c for c in calls if c[0] != c[1]]
    if {c[1] for c in calls} != VERB_FIELDS or len(calls) != len(VERB_FIELDS):
        out.append("ToggleOff callers are %s, want one each of %s" % (calls, sorted(VERB_FIELDS)))
    if len(re.findall(r"=>\s*PropertySettings\.\w+\s*=", f.s)) != len(calls):
        out.append("a setter lambda exists outside a ToggleOff call")
    d = re.search(r"\bstring\s+ToggleOff\s*\(\s*Func<bool>\s+get\s*,\s*Action<bool>\s+set\b[^{]*\{", f.s)
    meth = f.block_at(d.end() - 1) if d else None
    if meth is None:
        return out + ["ToggleOff's definition is gone"]
    body = f.s[meth[0]:meth[1]]
    t = re.search(r"\btry\s*\{", body)
    fin = f.after_try(f.block_at(meth[0] + t.end() - 1)[1])[1] if t else None
    if fin is None:
        return out + ["ToggleOff has no try/finally"]
    before = body[:t.start()]
    if not re.search(r"\bbool\s+was\s*=\s*get\(\s*\)\s*;", before):
        out.append("ToggleOff does not capture get() before the try")
    if not re.search(r"(?<![\w.])set\(\s*was\s*\)\s*;", f.s[fin[0]:fin[1]]):
        out.append("ToggleOff's finally does not set(was)")
    sets = re.findall(r"(?<![\w.])set\(\s*(\w+)\s*\)", body)
    if sorted(sets) != ["false", "was"]:
        out.append("ToggleOff's writes are %s, want false then was" % sets)
    if re.search(r"(?<![\w.])was\s*=(?!=)", body.replace("bool was =", "")):
        out.append("ToggleOff reassigns was")
    return out


# A waiver is only audited where the row above reads its restore: a new one in these files must be audited too, not
# copied. path -> the code each waiver must sit directly above.
WAIVERS = {CROWN: [r"if not setting\(f, v\):"],
           STALL: [r'action="set", field="leanScentEnabled", value=str\(scent\)'],
           LEAN: [r"RM_LeaningScrubSettings\.leanFireEnabled = leanOn;"],
           LUMINOUS: [r"LuminousPigmentSettings\.familyEnabled = arr;"],
           VERBS: [r"ToggleOff\(\(\) => PropertySettings\.%s," % n for n in
                   ("salvageClaimFeeEnabled", "walkableCommerceEnabled", "pickpocketEnabled", "bribeEnabled")]}


def waiver_problems(path, text):
    lines = text.split("\n")
    at = [i for i, ln in enumerate(lines) if prc.WAIVER in ln]
    want = WAIVERS[path]
    if len(at) != len(want):
        return ["%s: %d waivers, %d audited" % (os.path.basename(path), len(at), len(want))]
    return ["%s line %d: the waiver is not on %s" % (os.path.basename(path), i + 1, rx)
            for i, rx in zip(at, want) if not (i + 1 < len(lines) and re.search(rx, lines[i + 1]))]


TEXT = dict((p, read(p)) for p in (CROWN, STALL, LEAN, LUMINOUS, VERBS))
for label, got in (("crown repro: every touched field back at its prior, on every prior and exit path",
                    crown_problems(TEXT[CROWN])),
                   ("stall repro: leanScentEnabled back at its prior, on every prior and exit path",
                    stall_problems(TEXT[STALL])),
                   ("RM_TheLeanProof: every Arm call inside a try whose finally writes the captured savedFire",
                    lean_problems(TEXT[LEAN])),
                   ("RM_LuminousFamilySettingsProbe: every SetAllOnExcept inside the try that reloads the file and "
                    "writes snapshot", luminous_problems(TEXT[LUMINOUS])),
                   ("RM_SettlementVerbsProof: 4 same-field lambdas reach only ToggleOff, whose finally does set(was)",
                    verbs_problems(TEXT[VERBS]))):
    check(label, not got, "; ".join(got[:6]))
for path in TEXT:
    got = waiver_problems(path, TEXT[path])
    check("waivers in %s are the audited ones" % os.path.basename(path), not got, "; ".join(got))


# ---------------------------------------------------------------- 6. each row above goes red when its clause is broken
def red(name, audit, path, old, new):
    """Apply one mutant to the real source; a mutant that no longer applies fails too, so it can never rot into a pass."""
    text = TEXT[path]
    if text.count(old) != 1:
        check("mutant %s applies" % name, False, "%d matches of %r in %s" % (text.count(old), old, path))
        return
    got = audit(text.replace(old, new))
    check("mutant %s goes red" % name, bool(got), "the audit stayed green")


CROWN_RESTORE = "            setting(f, was)\n"
check("the blind check's stall restore line is where the mutants expect it",
      TEXT[STALL].count('value=str(prior_scent))') == 1)
red("crown: finally restore -> pass", crown_problems, CROWN, CROWN_RESTORE, "            pass\n")
red("crown: finally restore -> setting(f, True)", crown_problems, CROWN, CROWN_RESTORE, "            setting(f, True)\n")
red("crown: finally restore -> setting(f, False)", crown_problems, CROWN, CROWN_RESTORE, "            setting(f, False)\n")
red("crown: restore runs only when no arm threw", crown_problems, CROWN,
    "    finally:\n        for f, was in priors.items():",
    "    except ZeroDivisionError:\n        pass\n    if True:\n        for f, was in priors.items():")
red("crown: stallFreezeEnabled dropped from TOUCHED", crown_problems, CROWN,
    '"leanScentEnabled", "stallFreezeEnabled")\n\n', '"leanScentEnabled")\n\n')
red("crown: weather left locked", crown_problems, CROWN,
    '        setting(f, was)\n        call("jawa/weather_set", weather="Clear", lockWeather=True)\n'
    '        call("jawa/weather_set", unlock=True)\n',
    '        setting(f, was)\n        call("jawa/weather_set", weather="Clear", lockWeather=True)\n')
STALL_RESTORE = '        call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="leanScentEnabled", value=str(prior_scent))\n'
red("stall: finally restore -> pass", stall_problems, STALL, STALL_RESTORE, "        pass\n")
red("stall: finally restore -> value='True'", stall_problems, STALL, STALL_RESTORE,
    STALL_RESTORE.replace("str(prior_scent)", '"True"'))
red("stall: restore runs only when no arm threw", stall_problems, STALL,
    "    finally:\n" + STALL_RESTORE, "    except ZeroDivisionError:\n        pass\n    if True:\n" + STALL_RESTORE)
LEAN_RESTORE = "                RM_LeaningScrubSettings.leanFireEnabled = savedFire;\n"
red("Lean: the finally's savedFire write deleted", lean_problems, LEAN, LEAN_RESTORE, "")
red("Lean: the finally's write commented out", lean_problems, LEAN, LEAN_RESTORE, "                //" + LEAN_RESTORE.lstrip())
red("Lean: the finally writes true", lean_problems, LEAN, LEAN_RESTORE, LEAN_RESTORE.replace("savedFire", "true"))
red("Lean: savedFire captured from the wrong field", lean_problems, LEAN,
    "savedFire = RM_LeaningScrubSettings.leanFireEnabled;", "savedFire = RM_LeaningScrubSettings.leanEnabled;")
red("Lean: an Arm call before the try", lean_problems, LEAN, "            List<Thing> bed = new List<Thing>();\n",
    "            List<Thing> bed = new List<Thing>();\n            Arm(map, at, dir, true, out int a1, out int a2, out int a3);\n")
LUM_RESTORE = "                LuminousPigmentSettings.familyEnabled = snapshot;\n"
red("Luminous: the finally's snapshot write deleted", luminous_problems, LUMINOUS, LUM_RESTORE, "")
red("Luminous: the file is not put back", luminous_problems, LUMINOUS, "                    File.WriteAllText(file, pre);\n", "")
red("Luminous: the settings are not re-read", luminous_problems, LUMINOUS,
    "File.WriteAllText(file, pre);\n                    LoadedModManager.ReadModSettings<LuminousPigmentSettings>(folder, handle);",
    "File.WriteAllText(file, pre);")
red("Luminous: a SetAllOnExcept after the finally", luminous_problems, LUMINOUS,
    "            // the file as left must carry exactly the pre-test toggles, by key\n", "            SetAllOnExcept(-1);\n")
red("Verbs: ToggleOff's finally does nothing", verbs_problems, VERBS, "                set(was);\n", "")
red("Verbs: ToggleOff's finally writes true", verbs_problems, VERBS, "                set(was);\n", "                set(true);\n")
red("Verbs: a getter reads another field", verbs_problems, VERBS,
    "ToggleOff(() => PropertySettings.bribeEnabled,", "ToggleOff(() => PropertySettings.pickpocketEnabled,")
red("Verbs: a setter lambda outside ToggleOff", verbs_problems, VERBS,
    "        private static string ToggleOff(",
    "        private static Action<bool> Leak = v => PropertySettings.bribeEnabled = v;\n        private static string ToggleOff(")
for path, anchor in ((LEAN, "            List<Thing> bed = new List<Thing>();\n"),):
    red("a copied waiver in %s" % os.path.basename(path), lambda t: waiver_problems(path, t), path, anchor,
        anchor + "            // restore-check: ok copied\n")
check("a waiver moved off its write is caught",
      bool(waiver_problems(LEAN, TEXT[LEAN].replace("RM_LeaningScrubSettings.leanFireEnabled = leanOn;", "Other();"))))

print("selftest_proof_restore_check: %s (%d failure(s))" % ("PASS" if not fails else "FAIL", len(fails)))
sys.exit(1 if fails else 0)
