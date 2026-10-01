#!/usr/bin/env python3
"""northstar_driver CLI.  LIVE work runs under Windows Python, repo-relative paths:

  python.exe src/RimMandrake/Utils/northstar_driver/cli.py preflight --mod Graffiti
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Graffiti --plan <plan.py> [--pipeline]
  python3    src/RimMandrake/Utils/northstar_driver/cli.py run --mock --plan <plan.py>   # offline

Never touches ModsConfig.xml (read-only fingerprint), never launches the game, never takes the
bridge lock (you hold it: `rimflow bridge who`). Output is JSON (LF) at --out, default
Transient/northstar/<Mod>_<utc>.json, shaped for modcheck: {mod, mode, preflight[], bars[], summary,
expected, all_green, timing}. Exit 0 = ran and all_green, 1 = ran not green, 2 = refused (dirty site).
"""
import argparse
import importlib.util
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_UTILS)))
for p in (_UTILS, os.path.join(_UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

from northstar_driver import PASS, FAIL, UNMEASURED                       # noqa: E402
from northstar_driver import preflight as pf, bars as B                   # noqa: E402
from northstar_driver.session import FastSession                          # noqa: E402
from northstar_driver.transport import MockTransport, MockGame            # noqa: E402


def _rel(*parts):
    return os.path.join(ROOT, *parts)


def load_plan(path):
    spec = importlib.util.spec_from_file_location("ns_plan_" + os.path.basename(path)[:-3], path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def expected_bars(mod):
    """Must-show + cannot-show ids from the mod's walk, ONLY when VALIDATED (else binds nothing)."""
    try:
        import northstar
        w = northstar.find_walk(ROOT, mod)
        if not w:
            return [], "no walk"
        ns = northstar.parse(w)
        if ns["state"] != northstar.VALIDATED:
            return [], "walk is DRAFT (%s)" % ns["reason"]
        return list(ns["must_show"]) + list(ns["cannot_show"]), "VALIDATED walk %s" % os.path.basename(w)
    except Exception as ex:
        return [], "walk unreadable: %s" % ex


def mod_dirs_for(mod):
    if not mod:
        return []
    import game_paths
    out = []
    for tier in ("RimMandrake", "RimStarWars", "RimUtinni"):
        d = _rel("src", tier, mod)
        if os.path.isfile(os.path.join(d, "About", "About.xml")):
            # the deployed folder is named like the repo folder (deploy_custom_mods.py is the authority)
            out.append((d, os.path.join(game_paths.STEAM, "common", "RimWorld", "Mods", mod)))
    return out


def mock_config(ids):
    """Hermetic ModsConfig for mock runs -- the real one is never read or written."""
    import tempfile
    d = tempfile.mkdtemp(prefix="ns_mock_")
    p = os.path.join(d, "ModsConfig.xml")
    with open(p, "w") as f:
        f.write("<ModsConfigData><activeMods>%s</activeMods></ModsConfigData>" %
                "".join("<li>%s</li>" % i for i in ["ludeon.rimworld"] + list(ids)))
    return p


def open_session(args):
    if args.mock:
        game = MockGame(faults=[f for f in (args.fault or "").split(",") if f])
        return FastSession(transport=MockTransport(game), strict=False), game
    return FastSession(pipeline=args.pipeline, strict=False), None


def cmd_preflight(args):
    s, _ = open_session(args)
    with s:
        cs = pf.run_preflight(s, mod_dirs=[] if args.mock and not args.mod else mod_dirs_for(args.mod),
                              expect_ids=args.expect_id or (), need_god=args.god, rect=args.rect,
                              fix=args.fix, extra_tools=(),
                              config_path=mock_config(args.expect_id or ()) if args.mock else None)
    ok, bad, unk = pf.verdict(cs, args.allow_unmeasured)
    for c in cs:
        print("%-11s %-24s %s" % (c.status, c.name, c.evidence))
    print("PREFLIGHT %s" % ("OK" if ok else "REFUSED: %d FAIL, %d UNMEASURED" % (len(bad), len(unk))))
    return 0 if ok else 2


def cmd_run(args):
    plan = load_plan(args.plan) if args.plan else None
    s, game = open_session(args)
    mod = args.mod or (getattr(plan, "MOD", None) if plan else None) or "adhoc"
    exp, why = expected_bars(mod)
    doc = {"mod": mod, "mode": "mock" if args.mock else "live", "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "expected": exp, "expected_source": why, "bars": [], "preflight": []}
    with s:
        cs = pf.run_preflight(s, mod_dirs=[] if args.mock else mod_dirs_for(mod),
                              expect_ids=getattr(plan, "EXPECT_MODS", ()) or args.expect_id or (),
                              need_god=args.god or getattr(plan, "NEED_GOD", False),
                              rect=args.rect or getattr(plan, "RECT", None), fix=args.fix,
                              config_path=mock_config(getattr(plan, "EXPECT_MODS", ()) or args.expect_id or ()) if args.mock else None)
        # mod-supplied site check: plan.preflight(s) -> [failed precondition, ...] (plan 3.13)
        if getattr(plan, "preflight", None) and not args.mock_skip_site:
            try:
                for msg in plan.preflight(s) or []:
                    cs.append(pf.Check("site:" + msg.split(":")[0][:40], FAIL, msg))
            except Exception as ex:
                cs.append(pf.Check("site_preflight", UNMEASURED, "%s: %s" % (type(ex).__name__, ex)))
        # cannot-show enforcement (plan 6.10): a VALIDATED walk's cannot-show id that no component claims
        if getattr(plan, "USE_SUITE", False):
            miss = unclaimed_cannot_show(mod)
            if miss:
                cs.append(pf.Check("cannot_show_claimed", FAIL,
                                   "cannot-show id(s) no component claims via shows=: %s" % miss))
        doc["preflight"] = [c.as_dict() for c in cs]
        ok, bad, unk = pf.verdict(cs, args.allow_unmeasured)
        if not ok:
            doc.update(refused="; ".join("%s %s" % (c.name, c.status) for c in bad + unk),
                       all_green=False, summary=B.summarize([]))
            code = 2
        else:
            wanted = [b for b in B.REGISTRY.values() if b.mod in (None, mod)]
            rows = [B.run_bar(b, s) for b in wanted]
            if getattr(plan, "USE_SUITE", False):
                rows += _suite_rows(s, mod, exp)
            doc["bars"] = rows
            doc["summary"] = B.summarize(rows)
            doc["all_green"] = B.all_green(rows, exp or None)
            code = 0 if doc["all_green"] else 1
        doc["timing"] = s.timing
    out = args.out or _rel("Transient", "northstar", "%s_%s.json" % (mod, time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())))
    B.write_results(out, doc)
    print("%s: %s  PASS=%s FAIL=%s UNMEASURED=%s  calls=%d mean=%.3fms  -> %s" % (
        mod, "REFUSED" if code == 2 else ("GREEN" if code == 0 else "NOT GREEN"),
        doc["summary"][PASS], doc["summary"][FAIL], doc["summary"][UNMEASURED],
        doc["timing"]["n"], doc["timing"]["mean_ms"], out))
    return code


def unclaimed_cannot_show(mod):
    """Cannot-show ids of a VALIDATED walk that no component's `shows=` claims. [] when no walk."""
    try:
        import northstar
        import runner
        w = northstar.find_walk(ROOT, mod)
        ns = northstar.parse(w) if w else None
        if not ns or ns["state"] != northstar.VALIDATED:
            return []
        claimed = set()
        for c in runner.load_validation(runner.find_mod_dir(mod)).components_declared():
            claimed.update(c.get("shows") or ())
        return [i for i in ns["cannot_show"] if i not in claimed]
    except Exception as ex:
        return ["(unreadable: %s)" % ex]


def _suite_rows(s, mod, expected):
    import runner
    suite = runner.load_validation(runner.find_mod_dir(mod))
    res = runner.run_suite(suite, s, anchor=None, mod=None)   # judge/visual half is separate
    for ch in res["chains"]:
        for c in ch["components"]:
            if not str(c.get("verdict", "")).startswith("PASS"):
                print("component %s/%s: %s" % (ch.get("name"), c.get("name"),
                                               json.dumps({k: v for k, v in c.items() if k != "name"}, default=str)[:600]))
    return B.rollup_components(res["chains"], expected)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("preflight", cmd_preflight), ("run", cmd_run)):
        p = sub.add_parser(name)
        p.set_defaults(fn=fn)
        p.add_argument("--mod")
        p.add_argument("--mock", action="store_true", help="in-memory game; no bridge")
        p.add_argument("--fault", help="mock faults, comma list: zombie,modal,pause_lies,dev_off,god_off,dirty,unfrozen")
        p.add_argument("--god", action="store_true", help="require god mode")
        p.add_argument("--rect", help="x,z,w,h test area that must be empty")
        p.add_argument("--fix", action="store_true", help="pause / enable god, each proved by re-read")
        p.add_argument("--expect-id", action="append", help="packageId that must be active (repeat)")
        p.add_argument("--allow-unmeasured", action="store_true")
        p.add_argument("--mock-skip-site", action="store_true", help="skip plan.preflight (offline selftests)")
        p.add_argument("--pipeline", action="store_true", help="pipelined call_many (UNPROVEN live)")
        if name == "run":
            p.add_argument("--plan", help="python plan module registering @bar functions")
            p.add_argument("--out")
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
