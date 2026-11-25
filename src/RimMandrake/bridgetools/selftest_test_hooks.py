#!/usr/bin/env python3
"""Selftest: the mods' test hooks of BRIDGE v2.0, found by reflection (JawaBenchModHooksCore.cs, the run's watch in
JawaBenchSceneTickCore.cs, and src/RimMandrake/_Shared/TestHooks/RMTestHooks.cs). Page: design/specs/2026-11-23-bridge-v2-mod-hooks/boundary.md;
one test per promise, the 8 checks of RIMMANDRAKE_BUILD_MOD_TRACE_AND_RESET_HOOKS_BY_REFLECTION. The harness
(bridgetools/TestHooksSelfTest) builds seven net472 fixture mods with the SHIPPED hooks file and loads them by path. Each plant breaks
one rule of a copy of a production file and must turn its named check red; the item's wrong code (a Digest that answers a constant) is
two plants: the core that accepts it, and a good mod whose Digest is made constant. No game, no bridge. Without dotnet.exe it FAILS as
UNMEASURED.
Run: python3 src/RimMandrake/bridgetools/selftest_test_hooks.py [--no-plants]"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

CS = os.path.join(HERE, "JawaBench.BridgeTools")
CORES = ["JawaBenchSceneTickCore.cs", "JawaBenchModHooksCore.cs"]
HOOKS = os.path.join(REPO, "src", "RimMandrake", "_Shared", "TestHooks", "RMTestHooks.cs")
PROJ = os.path.join(HERE, "TestHooksSelfTest", "TestHooksSelfTest.csproj")
FIXTURES = os.path.join(HERE, "TestHooksSelfTest", "Fixtures")
FIXTURE_SRC = os.path.join(FIXTURES, "Fixtures.cs")
N_UNITS = 8                     # fewer printed = the harness did not run whole


class Unmeasured(Exception):
    pass


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def clean_texts():
    t = {n: read(os.path.join(CS, n)) for n in CORES}
    t["hooks"] = read(HOOKS)
    t["fixtures"] = read(FIXTURE_SRC)
    return t


def units(texts):
    """Build the harness and its fixture mods with these texts, run it -> {unit: "ok" | "FAIL why"}."""
    import winbuild
    d = tempfile.mkdtemp(prefix="TestHooksCore_", dir=winbuild.BUILD_ROOT)
    log = os.path.join(winbuild.BUILD_ROOT, "selftest_test_hooks.log")
    try:
        for n in CORES:
            with open(os.path.join(d, n), "w", encoding="utf-8") as f:
                f.write(texts[n])
        for n, key in (("RMTestHooks.cs", "hooks"), ("Fixtures.cs", "fixtures")):
            with open(os.path.join(d, n), "w", encoding="utf-8") as f:
                f.write(texts[key])
        props = ("-p:CoreDir=" + winbuild.win(d) + "\\", "-p:HooksFile=" + winbuild.win(os.path.join(d, "RMTestHooks.cs")),
                 "-p:FixtureSrc=" + winbuild.win(os.path.join(d, "Fixtures.cs")))
        with open(log, "w") as lf:
            sys.stdout.flush()
            saved = os.dup(1)
            os.dup2(lf.fileno(), 1)
            try:
                rc, rec = winbuild.stage_build(PROJ, stage_name="TestHooksSelfTest", extra=props,
                                               extra_dirs=(os.path.dirname(HOOKS),))
            finally:
                sys.stdout.flush()
                os.dup2(saved, 1)
                os.close(saved)
    except (OSError, SystemExit) as e:
        raise Unmeasured("the harness could not be built: %s" % e)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    if rc:
        raise Unmeasured("the harness build failed (rc %s), log %s" % (rc, log))
    stage_proj = winbuild.staged_win(rec, os.path.dirname(PROJ))
    dll = stage_proj + "\\bin\\Release\\net8.0\\TestHooksSelfTest.dll"
    # hang guard, far above a real run (the 8 units take seconds): a harness that never returns would hold the selftest forever
    pr = winbuild.run_interop_captured([winbuild.dotnet_exe(), dll, stage_proj + "\\Fixtures"], capture_output=True, text=True,
                                       cwd="/mnt/d/Luke/dev", timeout=300)
    out = {}
    for ln in pr.stdout.splitlines():
        if ln.startswith("U ") and not ln.startswith("U-count"):
            name, _, rest = ln[2:].strip().partition(" ")
            out[name] = rest
    if "U-count %d" % N_UNITS not in pr.stdout or len(out) != N_UNITS:
        raise Unmeasured("the harness printed %d units, want %d: %s %s" % (len(out), N_UNITS, pr.stdout[-400:], pr.stderr[-400:]))
    return out


_CLEAN = [None]


def unit(name):
    if _CLEAN[0] is None:
        _CLEAN[0] = units(clean_texts())
    return _CLEAN[0].get(name, "FAIL did not run")


def t_a_mod_with_no_hook_is_listed_as_such():
    return unit("a_mod_with_no_hook_is_listed_as_such")


def t_a_hook_of_the_wrong_shape_is_a_named_problem():
    return unit("a_hook_of_the_wrong_shape_is_a_named_problem")


def t_emit_with_a_null_sink_allocates_nothing():
    return unit("emit_with_a_null_sink_allocates_nothing")


def t_the_sink_is_cleared_at_the_end_also_after_a_thrown_tick():
    return unit("the_sink_is_cleared_at_the_end_also_after_a_thrown_tick")


def t_two_mods_hooks_do_not_collide():
    return unit("two_mods_hooks_do_not_collide")


def t_a_proof_build_hook_is_refused_for_an_acceptance_run():
    return unit("a_proof_build_hook_is_refused_for_an_acceptance_run")


def t_a_release_dll_with_hooks_names_no_companion_type():
    # its red case runs in every pass: the Leak fixture names the companion's type, and the unit fails unless that is seen
    return unit("a_release_dll_with_hooks_names_no_companion_type")


def t_a_digest_is_accepted_only_after_it_was_seen_to_differ():
    return unit("a_digest_is_accepted_only_after_it_was_seen_to_differ")


# (what the plant breaks, the check that must turn red, the file key, [(old, new)])
PLANTS = [
    ("a mod with no hook is not listed", "a_mod_with_no_hook_is_listed_as_such", "JawaBenchModHooksCore.cs",
     [("if (build == null && trace == null && !name.StartsWith(NamePrefix, StringComparison.Ordinal)) continue;",
       "if (build == null && trace == null) continue;")]),
    ("any shape is taken", "a_hook_of_the_wrong_shape_is_a_named_problem", "JawaBenchModHooksCore.cs",
     [("return wrong.Count == 0 ? null : string.Join(\", \", wrong);", "return null;")]),
    ("Emit formats its value before the null test", "emit_with_a_null_sink_allocates_nothing", "hooks",
     [("            var s = Sink;\n            if (s != null) s(name, key, value.ToString(CultureInfo.InvariantCulture));",
       "            string t = value.ToString(CultureInfo.InvariantCulture);\n            var s = Sink;\n            if (s != null) s(name, key, t);")]),
    ("the run's end does not call the watch", "the_sink_is_cleared_at_the_end_also_after_a_thrown_tick", "JawaBenchSceneTickCore.cs",
     [("try { wl.Ended(this, tick); }", "try { }")]),
    ("the leave does not clear the sinks", "the_sink_is_cleared_at_the_end_also_after_a_thrown_tick", "JawaBenchModHooksCore.cs",
     [("try { m.Sink.SetValue(null, null); n++; }", "try { n++; }"),
      ("foreach (var m in Mods) if (m.Sink != null && m.Sink.GetValue(null) != null) m.Sink.SetValue(null, null);", "")]),
    ("every sink says it is the first mod", "two_mods_hooks_do_not_collide", "JawaBenchModHooksCore.cs",
     [("string mod = m.Name;", "string mod = Mods[0].Name;")]),
    ("a PROOF build is admitted", "a_proof_build_hook_is_refused_for_an_acceptance_run", "JawaBenchModHooksCore.cs",
     [("if (m.Build == \"RELEASE\") continue;", "if (m.Build != \"none\") continue;")]),
    ("* the core accepts a digest that did not change", "a_digest_is_accepted_only_after_it_was_seen_to_differ", "JawaBenchModHooksCore.cs",
     [("else if (d == m.Clean) {", "else if (d == null) {")]),
    ("* a good mod's Digest answers a constant (GPT's case)", "a_digest_is_accepted_only_after_it_was_seen_to_differ", "fixtures",
     [("return State.Counter + \":\" + State.Pending.Count;", "return \"0:0\";")]),
]


def plants():
    good = True
    base = clean_texts()
    for name, must, key, subs in PLANTS:
        texts = dict(base)
        text = texts[key]
        for old, new in subs:
            if text.count(old) != 1:
                print("FAIL plant %r: its text is in %s %d times, want 1: %r" % (name, key, text.count(old), old[:70]))
                good = False
            text = text.replace(old, new)
        texts[key] = text
        red = sorted(u for u, v in units(texts).items() if v != "ok")
        hit = must in red
        good = good and hit
        print("%s plant %r turns red: %s" % ("ok  " if hit else "FAIL", name, red))
    return good


def main(argv):
    bad = 0
    tests = [t_a_mod_with_no_hook_is_listed_as_such, t_a_hook_of_the_wrong_shape_is_a_named_problem, t_emit_with_a_null_sink_allocates_nothing,
             t_the_sink_is_cleared_at_the_end_also_after_a_thrown_tick, t_two_mods_hooks_do_not_collide,
             t_a_proof_build_hook_is_refused_for_an_acceptance_run, t_a_release_dll_with_hooks_names_no_companion_type,
             t_a_digest_is_accepted_only_after_it_was_seen_to_differ]
    try:
        for t in tests:
            v = t()
            bad += v != "ok"
            print("%s %s%s" % ("ok  " if v == "ok" else "FAIL", t.__name__[2:], "" if v == "ok" else ": " + v))
        good = True if "--no-plants" in argv else plants()
    except Unmeasured as e:
        print("FAIL test hooks UNMEASURED: %s" % e)
        return 1
    print("test hooks: %d of %d checks passed%s" % (len(tests) - bad, len(tests), "" if "--no-plants" in argv else ", plants %s" % ("all red" if good else "NOT all red")))
    return 0 if not bad and good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
