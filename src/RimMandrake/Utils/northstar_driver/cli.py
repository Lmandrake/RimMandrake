#!/usr/bin/env python3
"""northstar_driver CLI.  LIVE work runs under Windows Python, repo-relative paths:

  python.exe src/RimMandrake/Utils/northstar_driver/cli.py preflight --mod Graffiti
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Graffiti --plan <plan.py> [--pipeline]
  python3    src/RimMandrake/Utils/northstar_driver/cli.py run --mock --plan <plan.py>   # offline
  python3    src/RimMandrake/Utils/northstar_driver/judge_cli.py <results.json>           # visual half, WSL

Suite bars (`shows=`) are visual: a state PASS reads UNMEASURED until judge_cli.py writes a verdict.

Never touches ModsConfig.xml (read-only fingerprint), never launches the game, never takes the
bridge lock (you hold it: `rimflow bridge who`). Output is JSON (LF) at --out, default
Transient/northstar/<Mod>_<utc>.json, shaped for modcheck: {mod, mode, preflight[], bars[], summary,
expected, all_green, timing, mod_hash}. A LIVE run is then recorded through
modcheck.status.record_run (`modcheck status` shows it); --no-record skips that. Exit 0 = ran and all_green, 1 = ran not green, 2 = refused (dirty site).
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


def _folded_into_composed(src_dir):
    try:
        import biomes_compose
        return os.path.basename(os.path.abspath(src_dir)) in biomes_compose.folded_sources(_rel("src"))
    except Exception:
        return False


def mod_dirs_for(mod):
    if not mod:
        return []
    import game_paths
    out = []
    for tier in ("RimMandrake", "RimStarWars", "RimUtinni"):
        d = _rel("src", tier, mod)
        if _folded_into_composed(d):
            continue            # deployed inside RimMandrake.Biomes; that composed deploy is gated by the mod's own preflight
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


def open_session(args, plan=None):
    if args.mock:
        game = MockGame(faults=[f for f in (args.fault or "").split(",") if f])
        game.ext = getattr(plan, "mock_extension", None)   # a plan may bring its own in-memory mod model
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
    s, game = open_session(args, plan)
    mod = args.mod or (getattr(plan, "MOD", None) if plan else None) or "adhoc"
    exp, why = expected_bars(mod)
    mod_dir, start_hash = mod_hash_now(mod)
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
                rows += _suite_rows(s, mod, exp, doc)
            doc["bars"] = rows
            doc["summary"] = B.summarize(rows)
            doc["all_green"] = run_all_green(rows, exp)
            code = 0 if doc["all_green"] else 1
        doc["timing"] = s.timing
    out = args.out or _rel("Transient", "northstar", "%s_%s.json" % (mod, time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())))
    if mod_dir:
        doc["mod_hash"] = start_hash
    B.write_results(out, doc)
    if not args.mock and not args.no_record:
        _entry, msg = record_result(doc, mod, out, start_hash, mod_dir)
        print(msg)
    print("%s: %s  PASS=%s FAIL=%s UNMEASURED=%s  calls=%d mean=%.3fms  -> %s" % (
        mod, "REFUSED" if code == 2 else ("GREEN" if code == 0 else "NOT GREEN"),
        doc["summary"][PASS], doc["summary"][FAIL], doc["summary"][UNMEASURED],
        doc["timing"]["n"], doc["timing"]["mean_ms"], out))
    return code


def mod_hash_now(mod):
    """(mod_dir, modcheck.status.mod_hash) for a repo mod, or (None, None) for an ad-hoc run."""
    try:
        import runner
        import status
        d = runner.find_mod_dir(mod)
        return d, status.mod_hash(d)
    except Exception:
        return None, None


def record_result(doc, mod, out, start_hash, mod_dir, _record=None):
    """Record a finished run through modcheck.status.record_run (the only writer of
    modcheck_status.json), as runner.py does after `modcheck run`. Returns (entry|None, message).
    Not recorded, by design: a mock run (cmd_run never calls this for one), a preflight refusal
    (the SITE was refused, the mod never ran), a run with no rows, an ad-hoc mod with no repo
    folder, and a run during which the mod's files changed (its verdict would describe neither
    hash). The verdict is the run's own all_green: any FAIL or UNMEASURED row is not GREEN."""
    import northstar
    import status
    if not mod_dir or not start_hash:
        return None, "not recorded: %s has no repo mod folder" % mod
    if doc.get("refused"):
        return None, "not recorded: refused at preflight (%s) -- a site verdict, not the mod's" % doc["refused"][:160]
    rows = doc.get("bars") or []
    if not rows:
        return None, "not recorded: the run produced no rows"
    now = status.mod_hash(mod_dir)
    if now != start_hash:
        return None, "not recorded: %s changed during the run (%s -> %s)" % (mod, start_hash[:12], now[:12])
    rel = os.path.relpath(os.path.abspath(out), ROOT).replace(os.sep, "/")
    by = {}
    for r in rows:
        by.setdefault(r["status"], []).append(r["id"])
    extra = {"components": {"counts": {k: len(v) for k, v in by.items()},
                            "not_ok": [i for k, v in by.items() if k != PASS for i in v]},
             "bars": {r["id"]: r["status"] for r in rows},
             "source": {"verb": "northstar_driver run", "result": rel, "mode": doc.get("mode"),
                        "started": doc.get("started_utc"), "expected_source": doc.get("expected_source")}}
    run_id = "%s/northstar_driver@%s" % (mod, os.path.basename(out))
    entry = (_record or status.record_run)(mod, mod_dir, run_id, bool(doc.get("all_green")),
                                           walk=northstar.find_walk(ROOT, mod), extra=extra)
    return entry, "recorded %s: %s at %s (%s)" % (mod, entry["status"], entry["hash"][:12], run_id)


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


def _suite_rows(s, mod, expected, doc):
    import runner
    suite = runner.load_validation(runner.find_mod_dir(mod))
    res = runner.run_suite(suite, s, anchor=None, mod=None)   # visual half: judge_cli.py, after the run
    for ch in res["chains"]:
        for c in ch["components"]:
            if not str(c.get("verdict", "")).startswith("PASS"):
                print("component %s/%s: %s" % (ch.get("name"), c.get("name"),
                                               json.dumps({k: v for k, v in c.items() if k != "name"}, default=str)[:600]))
    doc["components"] = component_records(res["chains"])
    doc["bar_text"], doc["bar_text_source"] = bar_text(mod)
    return mark_visual(B.rollup_components(res["chains"], expected), doc["bar_text"]) + \
        functional_rows(res["chains"])


def functional_rows(chains):
    """One row per suite component that claims no `shows=` bar: the mod's functional script
    (debug_process.md section 2). Without these a suite FAIL never reached the summary or the verdict,
    and a mod with no north star could never be GREEN (zero rows). Status is the component's own."""
    out = []
    for ch in chains:
        for c in ch["components"]:
            if c.get("shows"):
                continue
            v = str(c.get("verdict", ""))
            st = PASS if v.startswith("PASS") else (FAIL if v == "FAIL" else UNMEASURED)
            out.append({"id": "%s.%s" % (ch.get("name"), c.get("name")), "status": st, "functional": True,
                        "evidence": str(c.get("detail") or v)[:300]})
    return out


def run_all_green(rows, expected):
    """Every expected north-star bar PASS (bars.all_green) AND every functional row PASS."""
    return B.all_green(rows, expected or None) and all(r["status"] == PASS for r in rows if r.get("functional"))


def to_wsl(p):
    """`C:\\x\\y.png` -> `/mnt/c/x/y.png`; a POSIX path is returned unchanged."""
    p = str(p or "")
    if len(p) > 2 and p[1] == ":" and p[0].isalpha():
        return "/mnt/%s/%s" % (p[0].lower(), p[2:].replace("\\", "/").lstrip("/"))
    return p


def to_win(p):
    """`/mnt/c/x/y.png` -> `C:\\x\\y.png`; a Windows path is returned unchanged."""
    p = str(p or "")
    if p.startswith("/mnt/") and len(p) > 6 and p[6] == "/":
        return "%s:\\%s" % (p[5].upper(), p[7:].replace("/", "\\"))
    return p


def component_records(chains):
    """Every component, with each screenshot as {path (as the bridge returned it), win, wsl}, so the
    WSL-side judge can find the image without re-deriving anything."""
    out = []
    for ch in chains:
        for c in ch["components"]:
            out.append({"chain": ch.get("name"), "name": c.get("name"), "verdict": c.get("verdict"),
                        "shows": list(c.get("shows") or ()),
                        "screenshots": [{"path": p, "win": to_win(p), "wsl": to_wsl(p)}
                                        for p in (c.get("screenshots") or ()) if p]})
    return out


def bar_text(mod):
    """{bar id: {polarity, text}} from the VALIDATED walk -- the narrow question the judge asks."""
    try:
        import northstar
        w = northstar.find_walk(ROOT, mod)
        ns = northstar.parse(w) if w else None
        if not ns or ns["state"] != northstar.VALIDATED:
            return {}, "no VALIDATED walk"
        out = {i: {"polarity": "must", "text": ns["must_show_text"].get(i, "")} for i in ns["must_show"]}
        out.update({i: {"polarity": "cannot", "text": ns["cannot_show_text"].get(i, "")}
                    for i in ns["cannot_show"]})
        return out, "%s (hash %s)" % (os.path.relpath(w, ROOT), ns.get("recorded_hash", ""))
    except Exception as ex:
        return {}, "walk unreadable: %s" % ex


def mark_visual(rows, texts):
    """Every `shows=` bar is judged on its screenshots, so state alone cannot PASS it: a state PASS
    reads UNMEASURED until judge_cli.py writes a verdict. The state result is kept in `state_status`."""
    for r in rows:
        r["visual"] = True
        r["polarity"] = (texts.get(r["id"]) or {}).get("polarity", "must")
        r["state_status"], r["state_evidence"] = r["status"], r["evidence"]
        if r["status"] == PASS:
            r["status"] = UNMEASURED
            r["evidence"] = "visual bar: state PASS, not yet judged (run judge_cli.py) [%s]" % r["evidence"]
    return rows


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
            p.add_argument("--no-record", action="store_true",
                           help="live run only: do not record it in modcheck_status.json")
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
