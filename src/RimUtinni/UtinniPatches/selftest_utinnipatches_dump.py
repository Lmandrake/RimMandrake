#!/usr/bin/env python3
"""selftest_utinnipatches_dump.py -- UTINNIPATCHES_COVERAGE_GAPS_1 offline half (round 41): defs_vs_dump_static is
green on the shipped mod and go red on every planted break (in-memory copies of the parsed
inputs; the shipped files and the dump are never written)."""
import copy
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def main():
    spec = importlib.util.spec_from_file_location("up_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)

    # ---- shipped defs against the dump
    try:
        base, active = v._dump_inputs()
        rows_defs = v.shipped_def_rows()
        dump = v._dump_types(base, sorted(set(r[0] for r in rows_defs)))
    except Exception as e:
        print("UNMEASURED  defs vs dump: %s" % e)
        dump = None
    held = v.held_globs()
    if dump:
        checked, skipped, bad = v.dump_presence_findings(rows_defs, dump, active, held, v.changed_after_dump(base))
        check("sanity probe: >= 300 defs checked, hold globs read, patches mod active", checked >= 300 and len(held) >= 5 and "mandrake.rut.patches" in active, (checked, len(held)))
        check("shipped defs vs the load-14 dump: all %d present with their labels (skipped %s)" % (checked, skipped), bad == [], bad[:3])
        check("held files are named, not passed (>= 5 held, >= 1 inactive guard)", skipped["held"] >= 5 and skipped["guard inactive"] >= 1, skipped)
        ty, name = next((r[0], r[1]) for r in rows_defs if r[0] == "ThingDef" and not r[3] and r[4] not in [] and r[1] in dump["ThingDef"])
        d2 = dict((k, dict(x) if x else x) for k, x in dump.items())
        del d2["ThingDef"][name]
        got = v.dump_presence_findings(rows_defs, d2, active, held, v.changed_after_dump(base))[2]
        check("break: a def dropped from the dump is named (%s)" % name, len(got) == 1 and name in got[0], got)
        got = v.dump_presence_findings(rows_defs, d2, active, held, lambda rel: True)
        check("a missing def whose file changed after the dump is skipped, not lost (%s)" % name, got[2] == [] and got[1]["changed after dump"] >= 1, got[1:])
        got = v.dump_presence_findings(rows_defs, d2, active, held, lambda rel: False)[2]
        check("break: the same missing def with its file older than the dump is still lost", any(name in b for b in got), got)
        d3 = dict((k, dict(x) if x else x) for k, x in dump.items())
        lab = next(r for r in rows_defs if r[0] == "ThingDef" and r[2] and r[1] in dump["ThingDef"])
        d3["ThingDef"][lab[1]] = dict(d3["ThingDef"][lab[1]], label="something else")
        got = v.dump_presence_findings(rows_defs, d3, active, held, lambda rel: True)
        check("a label that differs because the file changed after the dump is skipped, not lost (%s)" % lab[1], got[2] == [] and got[1]["changed after dump"] >= 1, got[1:])
        got = v.dump_presence_findings(rows_defs, d3, active, held, v.changed_after_dump(base))[2]
        check("break: a label that drifted is named (%s)" % lab[1], len(got) == 1 and "label" in got[0], got)
        got = v.dump_presence_findings(rows_defs, d2, active, held + ["*"])[2]
        check("break: a blanket hold glob would hide the loss, so the sanity floor (checked >= 300) is what polices it", v.dump_presence_findings(rows_defs, dump, active, ["*"])[0] == 0)
        held_def = next(r for r in rows_defs if any(__import__("fnmatch").fnmatch(r[4], g) for g in held))
        check("a held def absent from the dump is skipped, not a finding (%s)" % held_def[1], all(held_def[1] not in b for b in bad))
        inact = next(r for r in rows_defs if r[3] and not all(x in active for x in r[3]) and not r[5])
        got = v.dump_presence_findings([inact], {inact[0]: {}}, active, [])
        check("a def whose guard mod is inactive is skipped (%s needs %s)" % (inact[1], inact[3]), got[0] == 0 and got[1]["guard inactive"] == 1, got)
        got = v.dump_presence_findings([inact], {inact[0]: {}}, active | set(inact[3]), [])
        check("break: the same def with its guard ACTIVE and absent is lost", got[0] == 1 and len(got[2]) == 1, got)

        # the chains through their own Suite
        import runner
        from northstar_driver.session import FastSession
        from northstar_driver.transport import MockGame, MockTransport

        def run(chain_name, patch=None):
            saved = {}
            for k, fn in (patch or {}).items():
                saved[k] = getattr(v, k)
                setattr(v, k, fn)
            try:
                own = v.Suite("UtinniPatches")
                own.toggles = list(v.suite.toggles)
                own.chains = [(n, f) for n, f in v.suite.chains if n == chain_name]
                with FastSession(transport=MockTransport(MockGame()), strict=False) as s:
                    res = runner.run_suite(own, s, anchor=None, mod=None)
            finally:
                for k, fn in saved.items():
                    setattr(v, k, fn)
            return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])
        got = run("defs_vs_dump_static")
        check("chain defs_vs_dump_static PASSes on the shipped mod", list(got.values()) == ["PASS"], got)
        got = run("defs_vs_dump_static", {"_dump_types": lambda b, w: d2})
        check("chain: a def missing from the dump reddens it", list(got.values()) == ["FAIL"], got)

    if FAILS:
        print("\n%d UtinniPatches dump selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall UtinniPatches dump selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
