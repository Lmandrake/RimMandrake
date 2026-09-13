"""modcheck.selftest -- offline proof of the floor/chain/status/report
contracts. No socket, no game -- see rimdrive/selftest.py's own docstring
for why this discipline exists; modcheck inherits it.

    python3 src/RimMandrake/Utils/modcheck/selftest.py

Picked up automatically by run_selftests.py (glob `selftest*.py` under src/).
"""
import os
import shutil
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
for p in (_HERE, _UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)

import floor  # noqa: E402
import report  # noqa: E402
import runner  # noqa: E402
import status  # noqa: E402
from suite import Suite, TestContext, PASS, FAIL, UNMEASURED  # noqa: E402
from rimdrive import UNVERIFIED  # noqa: E402
from rimdrive.session import Session  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print("  ok   %s" % name)
    else:
        print("  FAIL %s  %s" % (name, detail))
        FAILURES.append(name)


# ------------------------------------------------------------------- floor

def t_floor_uncovered():
    toggles = ["pitsEnabled", "spikesEnabled"]
    components = [{"toggle": "pitsEnabled", "beyond_toggle": False},
                 {"toggle": None, "beyond_toggle": True}]
    missing = floor.uncovered(toggles, components)
    check("floor: an uncovered toggle is reported", missing == ["spikesEnabled"],
         missing)


def t_floor_met_when_every_toggle_has_a_component():
    missing = floor.uncovered(["a"], [{"toggle": "a", "beyond_toggle": False}])
    check("floor: fully covered toggles report nothing missing", missing == [])


# ------------------------------------------------------------ suite/chain

def _fake_session():
    """A bare Session (no socket) with a scripted `.call`, matching
    rimdrive/selftest.py's own `_bare_session` pattern -- reimplemented here
    rather than imported, since it is a test fixture, not library surface."""
    s = Session.__new__(Session)
    s.strict = True
    s.quiet = True
    s.calls = 0
    s.mutations = 0
    s.no_ops = []
    s.unverified = []
    s.litter = []
    s.call = lambda tool, **p: {"success": True}
    return s


def t_chain_happy_path_is_pass():
    suite = Suite("t_mod")

    @suite.chain("c1")
    def c1(t):
        with t.component("comp_a", beyond_toggle=True):
            pass   # no verbs at all -- still a valid, trivially-passing component

    session = _fake_session()
    result = runner.run_suite(suite, session)
    verdicts = [c["verdict"] for chain in result["chains"] for c in chain["components"]]
    check("chain: a clean component passes", verdicts == [PASS], verdicts)
    check("chain: all_green true with no failures", result["all_green"] is True)


def t_chain_failure_marks_downstream_unmeasured_and_continues():
    suite = Suite("t_mod")
    order = []

    @suite.chain("c1")
    def c1(t):
        with t.component("first_ok", beyond_toggle=True):
            order.append("first_ok body ran")
        with t.component("second_fails", beyond_toggle=True):
            order.append("second_fails body ran")
            raise RuntimeError("boom")
        with t.component("third_unreachable_state", beyond_toggle=True):
            order.append("third body ran")   # runs, but every t.* verb no-ops
            t.wait_ticks(60)                  # must be a no-op: upstream_failed

    session = _fake_session()
    result = runner.run_suite(suite, session)
    verdicts = [c["verdict"] for c in result["chains"][0]["components"]]
    check("chain: first component still passes", verdicts[0] == PASS, verdicts)
    check("chain: the raising component is FAIL", verdicts[1] == FAIL, verdicts)
    check("chain: a component after a failure is UNMEASURED",
         verdicts[2] == UNMEASURED, verdicts)
    check("chain: the run continues past a failure (all three bodies ran)",
         order == ["first_ok body ran", "second_fails body ran", "third body ran"],
         order)
    check("chain: a no-op verb after upstream_failed made no bridge call",
         session.calls == 0, session.calls)
    check("chain: a failure is not silently dropped -- it's marked FAIL, not PASS",
         not result["all_green"])
    check("chain: the failing component was handed to on_finding",
         len(result["findings"]) == 1 and result["findings"][0].name == "second_fails")


def t_unverified_write_taints_pass_but_is_not_a_failure():
    suite = Suite("t_mod")

    @suite.chain("c1")
    def c1(t):
        with t.component("channel_less_write", beyond_toggle=True):
            t._record("some write with no read-back", UNVERIFIED)

    session = _fake_session()
    result = runner.run_suite(suite, session)
    verdict = result["chains"][0]["components"][0]["verdict"]
    check("UNVERIFIED: component still passes overall",
         str(verdict).startswith("PASS"), verdict)
    check("UNVERIFIED: the count is visible in the verdict, never hidden",
         verdict == "PASS(UNVERIFIED 1)", verdict)
    check("UNVERIFIED: an unverified pass still counts toward all_green",
         result["all_green"] is True)


def t_expect_pawn_despawned():
    suite = Suite("t_mod")

    @suite.chain("c1")
    def c1(t):
        with t.component("captured", beyond_toggle=True):
            t.expect_pawn_despawned("Pawn_1")

    session = _fake_session()
    session.call = lambda tool, **p: (
        {"pawns": []} if tool == "jawa/list_pawns" else {"success": True})
    result = runner.run_suite(suite, session)
    check("expect_pawn_despawned: passes when the pawn is gone from list_pawns",
         result["all_green"] is True)

    session2 = _fake_session()
    session2.call = lambda tool, **p: (
        {"pawns": [{"id": "Pawn_1", "x": 5, "z": 5}]}
        if tool == "jawa/list_pawns" else {"success": True})
    result2 = runner.run_suite(suite, session2)
    verdict = result2["chains"][0]["components"][0]["verdict"]
    check("expect_pawn_despawned: fails when the pawn is still on the map",
         verdict == FAIL, verdict)


def t_expect_log_contains():
    suite = Suite("t_mod")

    @suite.chain("c1")
    def c1(t):
        with t.component("scan", beyond_toggle=True):
            t.expect_log_contains("RMPitsDebug", field="sprung", value="True")

    session = _fake_session()
    session.call = lambda tool, **p: (
        {"messages": [{"text": "[RMPitsDebug] SCAN_DONE RM_OpenPit_Bare "
                              "covered=True sprung=True"}]}
        if tool == "jawa/drain_log" else {"success": True})
    result = runner.run_suite(suite, session)
    check("expect_log_contains: passes when the field=value substring matches",
         result["all_green"] is True)

    session2 = _fake_session()
    session2.call = lambda tool, **p: (
        {"messages": [{"text": "[RMPitsDebug] SCAN_DONE RM_OpenPit_Bare "
                              "covered=True sprung=False"}]}
        if tool == "jawa/drain_log" else {"success": True})
    result2 = runner.run_suite(suite, session2)
    verdict = result2["chains"][0]["components"][0]["verdict"]
    check("expect_log_contains: fails when the log shows the wrong value",
         verdict == FAIL, verdict)


def t_set_setting():
    suite = Suite("t_mod")

    @suite.chain("c1")
    def c1(t):
        with t.component("toggle_off", toggle="fooEnabled"):
            t.set_setting("some.mod", {"fooEnabled": False})

    session = _fake_session()
    session.call = lambda tool, **p: (
        {"settings": {"fooEnabled": False}}
        if tool == "rimworld/get_mod_settings" else {"success": True})
    result = runner.run_suite(suite, session)
    check("set_setting: passes when the read-back matches",
         result["all_green"] is True)

    session2 = _fake_session()
    session2.call = lambda tool, **p: (
        {"settings": {"fooEnabled": True}}   # did not take
        if tool == "rimworld/get_mod_settings" else {"success": True})
    result2 = runner.run_suite(suite, session2)
    verdict = result2["chains"][0]["components"][0]["verdict"]
    check("set_setting: fails when the setting did not actually take",
         verdict == FAIL, verdict)


def t_precondition_from_outside_the_script_is_refused():
    # spec §1: "a component whose preconditions came from outside the script
    # is a lint error" -- modelled here as the chain itself raising
    # Precondition before any component opens; the runner does not catch
    # that specially, so it propagates as a script bug, same as any other
    # exception raised outside a `with t.component()` block.
    from suite import Precondition
    suite = Suite("t_mod")

    @suite.chain("c1")
    def c1(t):
        raise Precondition("this chain assumed a pawn already existed")

    session = _fake_session()
    try:
        runner.run_suite(suite, session)
        check("a Precondition violation outside any component propagates", False)
    except Precondition:
        check("a Precondition violation outside any component propagates", True)


# ------------------------------------------------------------------ status

def t_mod_hash_changes_with_content():
    d = tempfile.mkdtemp()
    try:
        with open(os.path.join(d, "Foo.xml"), "w") as f:
            f.write("<A/>")
        h1 = status.mod_hash(d)
        with open(os.path.join(d, "Foo.xml"), "w") as f:
            f.write("<B/>")
        h2 = status.mod_hash(d)
        check("mod_hash: changes when a file's content changes", h1 != h2)
    finally:
        shutil.rmtree(d)


def t_mod_hash_ignores_validation_py():
    d = tempfile.mkdtemp()
    try:
        with open(os.path.join(d, "Foo.xml"), "w") as f:
            f.write("<A/>")
        h1 = status.mod_hash(d)
        with open(os.path.join(d, "validation.py"), "w") as f:
            f.write("from modcheck import Suite\n")
        h2 = status.mod_hash(d)
        check("mod_hash: unaffected by validation.py (editing the test "
             "harness is not a mod behaviour change)", h1 == h2)
    finally:
        shutil.rmtree(d)


def t_status_registry_roundtrip_and_staleness():
    d = tempfile.mkdtemp()
    real_log, real_lock = status.LOG_PATH, status.LOCK_PATH
    status.LOG_PATH = os.path.join(d, "modcheck_status.json")
    status.LOCK_PATH = status.LOG_PATH + ".lock"
    try:
        mod_dir = os.path.join(d, "mod")
        os.makedirs(mod_dir)
        with open(os.path.join(mod_dir, "Foo.xml"), "w") as f:
            f.write("<A/>")
        check("status: NEVER RUN before any record", status.check("T", mod_dir) == "NEVER RUN")
        status.record_run("T", mod_dir, "run1", all_green=True)
        check("status: GREEN right after a clean run", status.check("T", mod_dir) == "GREEN")
        with open(os.path.join(mod_dir, "Foo.xml"), "w") as f:
            f.write("<B/>")
        check("status: an undeclared edit goes STALE", status.check("T", mod_dir) == "STALE")
        try:
            status.declare_minor("U", mod_dir, "typo fix")
            check("status: declare_minor refuses a mod never run green", False)
        except RuntimeError:
            check("status: declare_minor refuses a mod never run green", True)
        status.declare_minor("T", mod_dir, "typo fix")
        check("status: declare_minor re-greens at the new hash",
             status.check("T", mod_dir) == "GREEN")
    finally:
        status.LOG_PATH, status.LOCK_PATH = real_log, real_lock
        shutil.rmtree(d)


# ------------------------------------------------------------------ report

def t_report_renders_verdict_and_mod_name():
    summary = {"all_green": False, "chains": [
        {"name": "c1", "components": [
            {"name": "comp_a", "toggle": None, "beyond_toggle": True,
            "verdict": "FAIL", "detail": "boom", "evidence": [], "screenshots": []}]}]}
    out = report.render("RM_PitTraps", summary)
    check("report: mod name appears", "RM_PitTraps" in out)
    check("report: RED shown for a non-green run", "RED" in out)
    check("report: the failing component's name appears", "comp_a" in out)
    check("report: is well-formed enough to open (has html/body tags)",
         "<html>" in out and "</html>" in out)


# ------------------------------------------------------------------ runner

def t_run_dry_run_never_calls_subprocess():
    import subprocess
    calls = []
    real_run = subprocess.run
    subprocess.run = lambda *a, **k: calls.append(a) or real_run(
        ["true"] if os.name != "nt" else ["cmd", "/c", "exit 0"],
        capture_output=True)
    try:
        results = runner.run([("NoSuchMod", "SOME_ITEM_1")], dry_run=True)
        check("runner: dry_run makes no subprocess calls", calls == [], calls)
        check("runner: dry_run still returns a per-mod result shape",
             "NoSuchMod" in results and results["NoSuchMod"]["dry_run"] is True)
    finally:
        subprocess.run = real_run


def t_restore_full_runs_even_when_a_mod_load_fails():
    """The `finally: restore_full()` in `run()` is the load-bearing safety
    property here: a mod that fails to even LOAD (bad validation.py, no
    suite) must not leave the owner's list on MINIMAL."""
    import subprocess
    calls = []
    real_run = subprocess.run

    def fake_run(cmd, **kw):
        calls.append(cmd)
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()

    subprocess.run = fake_run
    try:
        try:
            runner.run([("Definitely_Not_A_Real_Mod_Folder", "X_1")], dry_run=False)
        except RuntimeError:
            pass
        restore_calls = [c for c in calls if "--restore" in c]
        check("runner: restore_full is called even after a load failure",
             len(restore_calls) == 1, calls)
    finally:
        subprocess.run = real_run


# --------------------------------------------------------- deploy skip rule

def t_deploy_tool_already_skips_python_files():
    """Spec §1: 'validation.py ... Never deployed -- deploy_custom_mods.py
    must skip it by name.' Found, not built: `.py` is already in that
    tool's wholesale EXCLUDE_EXTS -- this locks the finding in as a
    regression guard rather than adding redundant logic."""
    sys.path.insert(0, _UTILS)
    import deploy_custom_mods
    check("deploy_custom_mods.py already excludes .py wholesale "
         "(validation.py needs no special-case rule)",
         ".py" in deploy_custom_mods.EXCLUDE_EXTS)


def t_compose_test_list_appends_once_and_reads_back():
    """`compose_test_list` appends each mod under test to <activeMods>
    exactly once (an id already live is left alone), writes atomically,
    and FAILS LOUDLY if the read-back is missing an id -- it edits the
    owner's live ModsConfig, so it earns its own test against a temp file."""
    import tempfile
    xml = ("<ModsConfigData><activeMods>\n"
           "    <li>ludeon.rimworld</li>\n"
           "    <li>mandrake.rm.pits</li>\n"
           "  </activeMods></ModsConfigData>")
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False,
                                     encoding="utf-8") as f:
        f.write(xml)
        path = f.name
    try:
        added = runner.compose_test_list(
            ["mandrake.rm.pits", "mandrake.rut.antiquities"], config_path=path)
        check("compose: only the missing id is appended",
             added == ["mandrake.rut.antiquities"], added)
        with open(path, encoding="utf-8") as f:
            out = f.read()
        check("compose: no duplicate for an already-live id",
             out.count("mandrake.rm.pits") == 1, out)
        check("compose: appended id sits inside activeMods",
             out.index("mandrake.rut.antiquities") < out.index("</activeMods>"))
    finally:
        os.unlink(path)


TESTS = [
    t_floor_uncovered,
    t_compose_test_list_appends_once_and_reads_back,
    t_floor_met_when_every_toggle_has_a_component,
    t_chain_happy_path_is_pass,
    t_chain_failure_marks_downstream_unmeasured_and_continues,
    t_unverified_write_taints_pass_but_is_not_a_failure,
    t_expect_pawn_despawned,
    t_expect_log_contains,
    t_set_setting,
    t_precondition_from_outside_the_script_is_refused,
    t_mod_hash_changes_with_content,
    t_mod_hash_ignores_validation_py,
    t_status_registry_roundtrip_and_staleness,
    t_report_renders_verdict_and_mod_name,
    t_run_dry_run_never_calls_subprocess,
    t_restore_full_runs_even_when_a_mod_load_fails,
    t_deploy_tool_already_skips_python_files,
]


def main():
    for t in TESTS:
        t()
    passed = len(TESTS) - len(FAILURES)
    print("\nSELFTEST %s -- %d/%d passed"
         % ("FAILED" if FAILURES else "OK", passed, len(TESTS)))
    if FAILURES:
        print("  failed: %s" % ", ".join(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
