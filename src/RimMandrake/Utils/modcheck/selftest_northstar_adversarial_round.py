"""Mutation proofs for NORTHSTAR_ADVERSARIAL_REVIEW_1 rounds. Each fixed predicate is driven with the input that fooled
the old one; each test goes RED if the old predicate comes back (the round record says how that was checked).
The round record itself is read: every finding names its class, evidence and what changed, and a changed row names a
test here or a file that exists. Run: python3 selftest_northstar_adversarial_round.py"""
import io
import os
import re
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(UTILS)))
sys.path[:0] = [HERE, UTILS]
import suite as S          # noqa: E402
import vacuity             # noqa: E402
from northstar_driver import bars as B, PASS, FAIL, UNMEASURED  # noqa: E402

RECORDS = os.path.join(REPO, "design", "RimMandrake", "northstar_adversarial_rounds")
FAILS = []


def ok(cond, what):
    if not cond:
        FAILS.append(what)


class Sess(object):
    """Just enough session: a roster, cells, a log, and a clock that can be blinded."""

    def __init__(self, pawns=(), cells=None, log=(), clock=True):
        self.pawns, self.cells, self.log, self.clock = list(pawns), cells or {}, list(log), clock
        self.ticks, self.tools = 100, []

    def call(self, tool, **kw):
        if tool == "jawa/list_pawns":
            return {"pawns": self.pawns}
        if tool == "jawa/drain_log":
            return {"messages": [{"text": x} for x in self.log if kw.get("contains", "") in x]}
        return {"success": True}

    def things_at(self, x, z):
        return list(self.cells.get((x, z), []))

    def _ticks(self):
        return self.ticks if self.clock else None

    def track(self, *a, **k):
        pass


def ctx(sess):
    t = S.TestContext(sess, anchor=(50, 50))
    t._log_base = {}
    return t


def verdict(sess, body):
    t = ctx(sess)
    with t.component("row"):
        body(t)
    return t.components[-1]


def t_not_in_cell_of_vanished_pawn():
    s = Sess(pawns=[{"id": "a", "x": 1, "z": 1}], cells={(1, 1): ["Other"]})
    ok(verdict(s, lambda t: t.expect_not_in_cell_of("a", "Thing")).verdict == PASS, "a pawn clear of the def still passes")
    s.cells[(1, 1)] = ["Thing"]
    ok(verdict(s, lambda t: t.expect_not_in_cell_of("a", "Thing")).verdict == FAIL, "a pawn on the def still fails")
    ok(verdict(Sess(), lambda t: t.expect_not_in_cell_of("gone", "Thing")).verdict == UNMEASURED,
       "a vanished pawn must be UNMEASURED, it passed before")


def t_log_field_is_a_token():
    for line, want in (("[X] n=12", False), ("[X] subn=1", False), ("[X] n=1.5", False), ("[X] a.n=1", False),
                       ("[X] n=1", True), ("[X] n=1 m=2", True), ("[X] m=2, n=1.", True)):
        got = verdict(Sess(log=[line]), lambda t: t.expect_log_contains("[X]", field="n", value="1")).verdict
        ok(got == (PASS if want else FAIL), "n=1 against %r read %s" % (line, got))


def t_reached_past_both_directions():
    west = [(20, 5), (15, 5), (10, 5)]
    pawn = lambda x: Sess(pawns=[{"id": "a", "x": x, "z": 5}])
    ok(verdict(pawn(8), lambda t: t.expect_reached_past("a", west)).verdict == PASS, "a walk toward -x reached past failed")
    ok(verdict(pawn(30), lambda t: t.expect_reached_past("a", west)).verdict == FAIL, "behind the start is not past")
    east = list(reversed(west))
    ok(verdict(pawn(30), lambda t: t.expect_reached_past("a", east)).verdict == PASS, "a walk toward +x still passes")
    ok(verdict(pawn(8), lambda t: t.expect_reached_past("a", east)).verdict == FAIL, "short of the line is not past")


def t_blind_clock_is_not_a_finished_wait():
    import clockgate
    keep = clockgate.advance_chunk
    clockgate.advance_chunk = lambda session, step: step
    try:
        c = verdict(Sess(clock=False), lambda t: t.wait_ticks(10000))
    finally:
        clockgate.advance_chunk = keep
    ok(c.verdict == UNMEASURED, "an unreadable clock must not pass a wait, read %s" % c.verdict)


def t_harness_errors_are_no_finding():
    def boom(exc):
        def body(t):
            raise exc
        return body
    for exc in (KeyError("rows"), TypeError("x"), ConnectionError("x"), TimeoutError("x"), AttributeError("x")):
        seen = []
        t = ctx(Sess())
        t._on_finding = seen.append
        with t.component("row"):
            boom(exc)(t)
        c = t.components[-1]
        ok(c.verdict == UNMEASURED and c.suspected_cause == "HARNESS" and not seen,
           "%s read %s with %d finding(s)" % (type(exc).__name__, c.verdict, len(seen)))
    ok(verdict(Sess(), boom(AssertionError("no"))).verdict == FAIL, "an assert still fails")
    ok(verdict(Sess(), boom(S.ExpectationFailed("no"))).verdict == FAIL, "an expectation still fails")


def t_trial_wait_without_a_clock_tool():
    b = B.Bar("x", lambda t: (t.wait_ticks(600), True)[1])
    row = B.run_bar(b, type("Nt", (), {"tools": [], "call": lambda self, *a, **k: {}})())
    ok(row["status"] == UNMEASURED, "a wait with no step tool read %s" % row["status"])


def t_visual_needs_a_judge_verdict_not_the_word():
    b = B.Bar("x", lambda t: B.passed("no judge: available"), visual=True)
    ok(B.run_bar(b, Sess())["status"] == UNMEASURED, "a mention of judge: greened a visual bar")
    b = B.Bar("x", lambda t: B.passed("judge: holds"), visual=True)
    ok(B.run_bar(b, Sess())["status"] == PASS, "a real judge verdict still passes")


def t_duplicate_rows_keep_the_worst():
    ok(not B.all_green([{"id": "x", "status": FAIL}, {"id": "x", "status": PASS}], ["x"]), "a later PASS erased a FAIL")
    ok(not B.all_green([{"id": "x", "status": PASS}, {"id": "x", "status": UNMEASURED}], ["x"]), "a later row lost")
    ok(B.all_green([{"id": "x", "status": PASS}, {"id": "x", "status": PASS}], ["x"]), "two passes pass")


LINT = '''
from modcheck import Suite, ExpectationFailed
suite = Suite("X")

@suite.chain("c")
def c(t):
    with t.component("defined_only"):
        def unused():
            assert False
    with t.component("dead_branch"):
        if False:
            raise ExpectationFailed("x")
    with t.component("checkpoint_only"):
        t.checkpoint("x")
    with t.component("alarm_only"):
        t.expect("letter", {})
        t.check_surroundings()
    with t.component("%s_computed" % "x"):
        t.screenshot()
    with t.component("honest_stub"):
        t.upstream_failed = True
    with t.component("real"):
        t.expect_pawn_despawned("x")
'''


def t_lint_gives_no_credit_for_what_cannot_fail():
    import tempfile
    p = os.path.join(tempfile.mkdtemp(prefix="st_nsadv_"), "validation.py")
    with open(p, "w") as f:
        f.write(LINT)
    rows = dict((r["component"], r["asserts"]) for r in vacuity.analyse(p))
    for n in ("defined_only", "dead_branch", "checkpoint_only", "alarm_only"):
        ok(rows.get(n) == [], "%s earned credit: %r" % (n, rows.get(n)))
    ok(rows.get("'%s_computed' % 'x'") == [], "a computed component name was skipped: %r" % sorted(rows))
    ok(rows.get("honest_stub") and rows.get("real"), "an UNMEASURED stub or a real assert lost credit")


def t_no_new_vacuous_component():
    new, stale, total = vacuity.new_vacuous()
    ok(total > 500, "the scan saw only %d components, the instrument is blind" % total)
    ok(not new, "components that assert nothing, outside the baseline: %s" % new)
    ok(not stale, "baseline rows that no longer exist: %s" % stale)


# A13 to A15 live in mod scripts, not the verdict core, so each is proved by running the mod's REAL chain on a scripted
# session. Each `*_problems(mutate)` returns what is wrong with the script as shipped (mutate=None) or with the old text
# put back; `t_old_text_goes_red` holds that the old text IS caught, so the proof cannot rot into one that never fails.
EH = "src/RimMandrake/EnvironmentalHazards/validation.py"
GL = "src/RimMandrake/GravshipLanding/validation.py"
DI = "src/RimMandrake/DivingInteraction/validation.py"
RP = "src/RimMandrake/RimProperty/validation.py"
NO_ANSWER = ('            elif _live(t):\n'
             '                raise ExpectationFailed("UNMEASURED: the control never got an answer, so it proved nothing: %s" % str(r)[:160])\n')
SCALD_SEEN = ('        if "RM_SeaDiveGenerator_TheScald" not in names:\n'
              '            raise ExpectationFailed("the Scald generator is not in the file, so the listing was never checked: %s" % names)\n')
ORIGIN_READ = ('        if t._guard() and STEAL_ITEM_DEF in t.session.things_at(*item_cells[0]):\n'
               '            raise ExpectationFailed("%s is still on its origin cell %s" % (STEAL_ITEM_DEF, item_cells[0]))\n')
OLD_THIEF = '    thief = t.spawn_pawn(THIEF_KIND, hostile=False, beyond=item_cells)\n'
OLD_ORIGIN = '        t.expect_not_in_cell_of(sentinel, STEAL_ITEM_DEF)   # left its origin\n'


def load(rel, mutate=None):
    """The mod's validation.py as shipped, or with `mutate` [(new text, old text)] put back. __file__ stays the real path."""
    path = os.path.join(REPO, rel)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    for now, was in mutate or ():
        if now not in text:
            raise AssertionError("%s no longer holds the text this mutant reverts: %r" % (rel, now[:60]))
        text = text.replace(now, was)
    mod = types.ModuleType("nsadv_" + rel.split("/")[-2])
    mod.__file__ = path
    exec(compile(text, path, "exec"), mod.__dict__)
    return mod


def run_chain(mod, name, sess):
    """{row: Component} of one real chain on a scripted session; a screenshot needs Windows and judges nothing here."""
    t = ctx(sess)
    t.screenshot = lambda *a, **k: None
    try:
        dict(mod.suite.chains)[name](t)
    except S.ExpectationFailed:
        pass
    return dict((c.name, c) for c in t.components)


class HarmonySess(Sess):
    def __init__(self, reply):
        Sess.__init__(self)
        self.reply = reply

    def call(self, tool, **kw):
        return self.reply if tool == "jawa/harmony_patches" else Sess.call(self, tool, **kw)


def control_problems(rel, row, chain, mutate=None):
    mod = load(rel, mutate)
    owned = {"success": True, "methods": [{"postfixes": [{"owner": mod.HARMONY_ID}]}]}
    out = []
    for reply, want in ((None, UNMEASURED), ({"success": False, "error": "refused"}, UNMEASURED),
                        ({"success": True, "harmonyError": "x"}, UNMEASURED), ("garbled", UNMEASURED),
                        ({"success": True, "methods": []}, PASS), (owned, FAIL)):
        got = run_chain(mod, chain, HarmonySess(reply))[row].verdict
        if got != want:
            out.append("%s %s on %r read %s, want %s" % (rel, row, reply, got, want))
    return out


def eh_problems(mutate=None):
    return control_problems(EH, "control_unpatched_method_has_no_owner", "harmony_rules_armed", mutate)


def gl_problems(mutate=None):
    return control_problems(GL, "control_nonexistent_method_has_no_owner", "reveal_gate_armed", mutate)


GEN = "<MapGeneratorDef><defName>%s</defName>%s</MapGeneratorDef>"
GALLERY = "<li>RM_ScaldReturnGallery</li>"
SCALD, GREY = "RM_SeaDiveGenerator_TheScald", "RM_SeaDiveGenerator_GreySea"


def scald_problems(mutate=None):
    real = os.path.join(REPO, os.path.dirname(DI), "Defs", "MapGeneration", "RM_SeaDiveGenerators.xml")
    with open(real, encoding="utf-8") as f:
        shipped = f.read()
    out = []
    for label, xml, want in (("the shipped file", shipped, PASS),
                             ("a reshaped file", shipped.replace("<MapGeneratorDef>", '<MapGeneratorDef Abstract="False">'), FAIL),
                             ("no Scald generator", GEN % (GREY, ""), FAIL),
                             ("an empty file", "<Defs/>", FAIL),
                             ("a Scald without the gallery", GEN % (SCALD, ""), FAIL),
                             ("the gallery off the Scald", GEN % (SCALD, GALLERY) + GEN % (GREY, GALLERY), FAIL)):
        mod = load(DI, mutate)
        builtin = open

        def fake(path, *a, _xml=xml, **k):
            return io.StringIO(_xml) if str(path).endswith("RM_SeaDiveGenerators.xml") else builtin(path, *a, **k)
        mod.open = fake
        got = run_chain(mod, "scald_return_gallery", Sess())["scald_generator_lists_gallery_only"].verdict
        if got != want:
            out.append("the listing row on %s read %s, want %s" % (label, got, want))
    return out


class TheftSess(Sess):
    """A map where `after` decides, when the steal is ordered, where everything ends up. Any bystander has walked off."""

    def __init__(self, after):
        Sess.__init__(self, cells={})
        self.after, self.kinds = after, {}

    def call(self, tool, **kw):
        if tool == "jawa/spawn_batch":
            for op in kw["ops"].split(";"):
                d, at = op.split(":")
                self.cells.setdefault(tuple(int(v) for v in at.split(",")), []).append(d)
        elif tool == "jawa/spawn_pawn":
            pid = "p%d" % len(self.pawns)
            self.kinds[pid] = kw["kindDef"]
            self.pawns.append({"id": pid, "x": kw["x"], "z": kw["z"], "kindDef": kw["kindDef"]})
            return {"success": True, "pawns": [{"id": pid, "name": pid, "kindDef": kw["kindDef"]}]}
        elif tool == "jawa/list_things":
            return {"success": True, "things": [{"def": d, "id": "item1"} for v in self.cells.values() for d in v]}
        elif tool == "jawa/ordered_job":
            thief = [p for p in self.pawns if p["id"] == kw["pawnId"]][0]
            for p in self.pawns:
                if p is not thief:
                    p["x"], p["z"] = 1, 1
            self.after(self, thief)
        return Sess.call(self, tool, **kw)


def never_lifted(s, thief):
    (thief["x"], thief["z"]) = list(s.cells)[0]        # the thief stands on the item, which never moved


def carried_off(s, thief):
    defs = s.cells.pop(list(s.cells)[0])
    thief["x"], thief["z"] = 60, 60
    s.cells[(60, 60)] = defs


def destroyed(s, thief):
    s.cells.clear()


def theft_problems(mutate=None):
    import clockgate
    mod = load(RP, mutate)
    out = []
    keep = clockgate.advance_chunk
    try:
        for label, after, want in (("an item that never moved, a bystander gone", never_lifted, FAIL),
                                   ("an item carried off", carried_off, PASS), ("an item destroyed", destroyed, FAIL)):
            s = TheftSess(after)

            def advance(session, step, _s=s):
                _s.ticks += step
                return step
            clockgate.advance_chunk = advance
            got = run_chain(mod, "animal_theft_take", s)["take_and_relocate"].verdict
            if got != want:
                out.append("take_and_relocate on %s read %s, want %s" % (label, got, want))
    finally:
        clockgate.advance_chunk = keep
    return out


def t_no_answer_control_is_unmeasured():
    for x in eh_problems() + gl_problems():
        ok(False, x)


def t_scald_listing_needs_the_scald_seen():
    for x in scald_problems():
        ok(False, x)


def t_stolen_item_is_read_at_its_origin():
    for x in theft_problems():
        ok(False, x)


def t_old_text_goes_red():
    """The round's old component bodies, put back one at a time: each must be caught, on the input that fooled it."""
    def caught(problems, mutate, what):
        try:
            ok(problems(mutate), "the old %s was not caught" % what)
        except AssertionError as ex:          # the shipped text moved: the mutant is stale, or the fix itself was undone
            ok(False, str(ex))
    caught(eh_problems, [(NO_ANSWER, "")], "EnvironmentalHazards control")
    caught(gl_problems, [(NO_ANSWER, "")], "GravshipLanding control")
    caught(scald_problems, [(SCALD_SEEN, "")], "Scald listing")
    caught(theft_problems, [(OLD_THIEF, '    sentinel = t.spawn_pawn("Colonist", hostile=False)\n' + OLD_THIEF),
                            (ORIGIN_READ, OLD_ORIGIN)], "sentinel origin read")


def t_every_round_is_recorded():
    names = [n for n in sorted(os.listdir(RECORDS)) if n.startswith("round_") and n.endswith(".md")]
    ok(names, "no round record")
    for n in names:
        with open(os.path.join(RECORDS, n), encoding="utf-8") as f:
            text = f.read()
        rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in text.splitlines()
                if re.match(r"\|\s*[A-Z]\d+\s*\|", l)]
        ok(rows, "%s has no finding rows" % n)
        for r in rows:
            ok(len(r) == 4 and all(r), "%s: row %r lacks class, evidence or change" % (n, r[0]))
            ok(re.search(r"`t_\w+`|`[A-Z][A-Z0-9_]{5,}`", r[-1]), "%s: %s changed something with no test and no filed item" % (n, r[0]))
            for name in re.findall(r"`(t_\w+)`", r[-1]):
                ok(name in globals(), "%s: %s names a test that does not exist: %s" % (n, r[0], name))
            for path in re.findall(r"`(src/[^`]+)`", r[-1]):
                ok(os.path.exists(os.path.join(REPO, path)), "%s: %s names a missing file: %s" % (n, r[0], path))


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("t_") and callable(fn):
            try:
                fn()
            except Exception as ex:           # one crash must not hide what the other tests read
                FAILS.append("%s crashed: %s: %s" % (name, type(ex).__name__, ex))
    for x in FAILS:
        print("FAIL " + x)
    print("selftest_northstar_adversarial_round: %s" % ("FAIL" if FAILS else "OK"))
    sys.exit(1 if FAILS else 0)
