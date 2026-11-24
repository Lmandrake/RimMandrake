#!/usr/bin/env python3
"""Selftest: the companion guards every canonical world save. Page: design/specs/2026-11-23-canonical-save-guard/boundary.md;
one test per promise. The C# promises run the PRODUCTION files in LiveToolsSelfTest, clean (all green) and with planted faults
(red). No game, no bridge. Without dotnet.exe it FAILS as UNMEASURED."""
import contextlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "bridgetools"))
import canonical_saves as CS                      # noqa: E402
import live_tools_units as L                      # noqa: E402
import selftest_canonical_saves_current as CUR    # noqa: E402


def say(ok, what):
    print(("ok    " if ok else "FAIL  ") + what)
    return bool(ok)


def t_the_current_start_is_guarded():
    return L.group("gstart", ["lacks_r3"])


def t_every_form_of_the_name_is_guarded():
    return L.group("gforms", ["lacks_r3", "no_starts"])


def t_a_non_canonical_save_stays_free():
    return L.group("gfree", ["starts_too_wide"])


def t_an_unreadable_save_is_guarded():
    return L.group("gblind", ["unknown_reads_as_new_game", "hook_assumed"])


def t_the_profile_file_only_adds():
    return L.group("gfile", ["file_names_dropped", "lacks_r3"])


def t_the_list_is_what_the_document_says():
    return say(CUR.main() == 0, "the committed list is current, and each planted fault was seen")


def t_a_document_it_cannot_read_is_not_an_empty_list():
    good = "x\n```guard\nWORLD_A\nCANON_*\n```\nSee `B_1.rws`, `C.rws.bak-old`, \u2026R3.rws.\n"
    ok = say(CS.rule(good) == (["B_1", "WORLD_A"], ["CANON_"]), "a good document reads: %r" % (CS.rule(good),))
    cases = {"no block": "text", "an empty block": "```guard\n```\n", "two blocks": good + good, "only a name start": "```guard\nX_*\n```\n",
             "a .rws ending": "```guard\nA.rws\n```\n", "a path": "```guard\nSaves/A\n```\n", "a lone star": "```guard\n*\n```\n",
             "a star inside": "```guard\nA*B\n```\n", "a bullet": "```guard\n- A\n```\n"}
    for what, text in cases.items():
        try:
            got = CS.rule(text)
        except CS.Unreadable:
            got = None
        ok &= say(got is None, "%s is refused by name (got %r)" % (what, got))
    with tempfile.TemporaryDirectory() as d:
        try:
            CS.write(d)
            refused = False
        except CS.Unreadable:
            refused = True
        ok &= say(refused and not os.listdir(d), "an absent document is refused, and nothing is written")
    return ok


def t_a_companion_build_brings_the_list_up_to_date():
    import build
    real = build.REPO_ROOT
    with tempfile.TemporaryDirectory() as d:
        for rel, text in ((CS.DOC, "```guard\nWORLD_A\n```\n"), (CS.GENERATED, "old\n")):
            p = os.path.join(d, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(text)
        out = io.StringIO()
        try:
            build.REPO_ROOT = d
            with contextlib.redirect_stdout(out):
                build.regenerate_canonical_saves()
                first = CS.committed(d)
                build.regenerate_canonical_saves()
            ok = say(first == CS.source(["WORLD_A"], []) and "written again" in out.getvalue() and "list is current" in out.getvalue(),
                     "a stale list is written again, said once; a current one is left")
            os.remove(os.path.join(d, *CS.DOC.split("/")))
            try:
                build.regenerate_canonical_saves()
                stop = ""
            except SystemExit as e:
                stop = str(e.code)
            ok &= say("UNREADABLE" in stop, "a build without a readable document stops: %r" % stop[:60])
        finally:
            build.REPO_ROOT = real
    # main() calls it before the sources are judged and compiled
    seen, keep = [], {}
    for name, ret in (("regenerate_canonical_saves", None), ("source_dirty", []), ("build", "x"), ("aim", None), ("verify_bundle", None),
                      ("verify_src_hash", None), ("verify_gm_gate", None), ("verify_shared_closures", None), ("plan_deploy", None)):
        keep[name] = getattr(build, name)
        setattr(build, name, lambda *a, _n=name, _r=ret, **k: (seen.append(_n), _r)[1])
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            build.main([])
    finally:
        for name, f in keep.items():
            setattr(build, name, f)
    return say("regenerate_canonical_saves" in seen and seen.index("regenerate_canonical_saves") < min(seen.index("source_dirty"), seen.index("build")),
               "build.main writes the list before it judges and compiles the sources: %s" % seen[:4]) and ok


def main():
    try:
        res = [t_the_current_start_is_guarded(), t_every_form_of_the_name_is_guarded(), t_a_non_canonical_save_stays_free(),
               t_an_unreadable_save_is_guarded(), t_the_profile_file_only_adds(), t_the_list_is_what_the_document_says(),
               t_a_document_it_cannot_read_is_not_an_empty_list(), t_a_companion_build_brings_the_list_up_to_date()]
    except L.Unmeasured as e:
        print("FAIL canonical save guard UNMEASURED: %s" % e)
        return 1
    print("canonical save guard: %d of %d promises hold" % (sum(map(bool, res)), len(res)))
    return 0 if all(res) else 1


if __name__ == "__main__":
    sys.exit(main())
