#!/usr/bin/env python3
"""modcheck -- the scripted mod-functionality validator (pre-playtest).

    python.exe src/RimMandrake/Utils/modcheck/cli.py run <mod> [<mod>...] [--debug]
    python3     src/RimMandrake/Utils/modcheck/cli.py status
    python3     src/RimMandrake/Utils/modcheck/cli.py declare <mod> minor --why "..."
    python3     src/RimMandrake/Utils/modcheck/cli.py rename-key <old> <new> --why "..."
    python3     src/RimMandrake/Utils/modcheck/cli.py forget-key <key> --why "..."
    python3     src/RimMandrake/Utils/modcheck/cli.py validate <mod> [--owner-said "..."]
    python3     src/RimMandrake/Utils/modcheck/cli.py review <mod> --owner-said "..."
    python3     src/RimMandrake/Utils/modcheck/cli.py record <mod> --result <json> [--tier T]

`record` (2026-10-02) records a functional script's LIVE result (e.g.
FlowWorks/northstar/validation_v2.py) through status.record_run WITHOUT
touching ModsConfig.xml -- it refuses a stale result (mod hash moved), a run
whose live mod set is not the declared tier, and an aborted run (record.py).

`run` drives a live bridge session and needs `python.exe` (Windows) for the
same WSL-loopback reason every other bridge driver does
(rimbridge_client.py). `status` and `declare` touch only
`infrastructure/state/modcheck_status.json` and run fine under plain
`python3`.

`rename-key` and `forget-key` are the two verbs `modcheck_status.json` owed
the naming migration (MEASURED 2026-09-17: `FluidCanals` sat GREEN under its
dead pre-rename name while the mod ships as `FlowWorks`) -- the only
sanctioned way to move or drop a key, since hand-editing that file is
forbidden.

`validate` and `review` are the two OWNER-AUTHORISED verbs added 2026-09-15
(design/RimMandrake/north_star_validation_spec.md): `validate` turns a mod's
agent-drafted `## north star` checklist into a binding bar, `review` records
that he has read a run's sheet with his own eyes -- required once, before a
mod's first GREEN. Both take his verbatim `--owner-said` and neither re-derives
his judgement; `validate` with no `--owner-said` prints the bar and writes
nothing, so the lines can be read to him first.
"""
import argparse
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
_UTILS = os.path.dirname(_HERE)
if _UTILS not in sys.path:
    sys.path.insert(0, _UTILS)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    if argv[:1] == ["metrics"]:     # its own argparse (metrics.py --help); listed below for discoverability
        import metrics
        return metrics.main(argv[1:])
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run")
    p_run.add_argument("mods", nargs="+",
                       help="mod folder name(s), e.g. Pits")
    p_run.add_argument("--item", action="append", default=[],
                       help="ITEM_ID: TARGETED run of the chains that item maps to (its rows cite it, or its "
                            "ledger text names a chain/row), recorded against it; refused if nothing maps. "
                            "MOD=ITEM_ID: only the ledger item a run is recorded against (default "
                            "MODCHECK_<MOD>_RUN_1)")
    p_run.add_argument("--chains", default="",
                       help="TARGETED: comma-separated chain names to run (one mod)")
    p_run.add_argument("--rows", default="",
                       help="TARGETED: comma-separated row ids; each row's chain runs as a PREFIX and stops after its "
                            "last requested row, the tail recorded NOT_RUN (one mod)")
    p_run.add_argument("--preview", action="store_true",
                       help="TARGETED: print the per-chain plan (requested -> prerequisites -> executed -> skipped) "
                            "and stop: no mod-list swap, no game")
    p_run.add_argument("--full", action="store_true",
                       help="the whole suite: a scheduled sweep, at most daily (owner 2026-10-25). A run with no "
                            "--chains/--rows/--item ITEM_ID is refused without it")
    # focused_testing_plan option B (all opt-in; without them a run behaves exactly as before)
    p_run.add_argument("--reuse", choices=("off", "report", "on"), default=None,
                       help="external-driver rows with no result at the current mod hash: 'report' (the default when "
                            "unset) tags a result whose runtime+test manifest and DLL still match as reusable@<file> "
                            "and leaves the row UNMEASURED; 'on' takes its status as reused@<file> (never fresh_green); "
                            "'off' does not look (sets MODCHECK_REUSE, modcheck/reuse.py)")
    p_run.add_argument("--drivers", choices=("on", "off"), default=None,
                       help="'on': before the chains, run the suite's external live drivers (suite.live_drivers, e.g. "
                            "FlowWorks northstar/thirst_live.py) whose chains are selected, so their rows are measured at "
                            "this mod hash; the SteveDesktop worker passes it (sets MODCHECK_RUN_DRIVERS, modcheck/drivers.py)")
    p_run.add_argument("--purpose", choices=("fix", "guard", "sweep", "sensitivity", "flake", "commission"),
                       default=None,
                       help="why this run happens (plan 2026-10-25 section 3): fix/guard let the known-good gate skip a "
                            "chain whose recorded PASS still holds; sweep/sensitivity/flake/commission run everything "
                            "and only report would_skip. Default: sweep with --full, guard otherwise "
                            "(sets MODCHECK_PURPOSE, modcheck/gate.py)")
    p_run.add_argument("--gate", choices=("on", "shadow", "off"), default=None,
                       help="the known-good gate: 'on' (default) skips per --purpose, 'shadow' never skips but "
                            "records would_skip, 'off' computes nothing (sets MODCHECK_GATE)")
    p_run.add_argument("--canary", action="store_true",
                       help="run the vanilla canary (Steel spawn/read-back/destroy, a live colonist, Playing) before "
                            "the first chain; red -> every chain records one UNMEASURED HARNESS row, no body runs")
    p_run.add_argument("--validity", action="store_true",
                       help="arm the validity checks (menu drop, colonist count 0, hostile arrival): a FAIL they "
                            "explain becomes UNMEASURED/invalid with the FAIL kept as a lead, no finding")
    p_run.add_argument("--changed", default=None, metavar="RANGE|WORKTREE",
                       help="print the chains a change (git range plus uncommitted files; WORKTREE = uncommitted "
                            "only) SUGGESTS, and stop: nothing runs from a suggestion (one mod)")
    p_run.add_argument("--seat", default=None,
                       help="ledger seat for the run's verify/findings when RIMFLOW_SEAT/AGENT_SEAT do not reach "
                            "this process (Windows python.exe); with none the run is still recorded, ledger skipped")
    p_run.add_argument("--debug", action="store_true")
    p_run.add_argument("--situational", action="store_true",
                       help="wrap every chain in the situational envelope: bland map, python-enforced "
                            "tick budget, detector sweeps, evidence+screenshot on any surprise")
    p_run.add_argument("--policy", choices=["abort", "record"], default="abort",
                       help="what a surprise does: abort the component (UNMEASURED) or just record it")
    p_run.add_argument("--dry-run", action="store_true",
                       help="exercise the orchestration with no game, no "
                            "subprocess side effects (selftest-shaped)")

    p_status = sub.add_parser("status")
    p_status.add_argument("mod", nargs="?")

    p_decl = sub.add_parser("declare")
    p_decl.add_argument("mod")
    p_decl.add_argument("severity", choices=["minor"])
    p_decl.add_argument("--why", required=True)

    p_ren = sub.add_parser("rename-key", help="move a registry entry from an old "
                                              "mod key to its new name")
    p_ren.add_argument("old")
    p_ren.add_argument("new")
    p_ren.add_argument("--why", required=True)

    p_forget = sub.add_parser("forget-key", help="delete a registry entry outright "
                                                 "-- for an orphaned key with no "
                                                 "successor worth preserving")
    p_forget.add_argument("key")
    p_forget.add_argument("--why", required=True)

    p_val = sub.add_parser("validate", help="record the owner's validation of a "
                                            "mod's `## north star` checklist")
    p_val.add_argument("mod")
    p_val.add_argument("--owner-said",
                       help="his verbatim words. Required to WRITE; omit to "
                            "print the lines that would bind and change nothing")
    p_val.add_argument("--by-card", help="a decision he took by question card: "
                       "'<question -> option>'. Stands in for --owner-said")

    p_rev = sub.add_parser("review", help="record that the owner reviewed a "
                                          "mod's sheet -- once, before its first GREEN")
    p_rev.add_argument("mod")
    p_rev.add_argument("--owner-said", required=True)
    p_rev.add_argument("--run-id", help="defaults to the mod's last recorded run")

    p_rec = sub.add_parser("record", help="record a functional script's live result "
                                          "(no ModsConfig swap) -- refuses stale/off-tier runs")
    p_rec.add_argument("mod")
    p_rec.add_argument("--result", required=True, help="the script's result JSON")
    p_rec.add_argument("--tier", default=None,
                       help="modset_builder tier the run must have been on "
                            "(default: the mod name lowercased)")
    p_rec.add_argument("--extensions", default=None,
                       help="step 4's result JSON (northstar/extension_proof.py --live), for a mod that "
                            "ships one; omitted, step 4 records UNMEASURED and the checkout cannot be green")

    p_lint = sub.add_parser("lint", help="every identifier a validation walk "
                                         "names must exist (walklint)")
    p_lint.add_argument("--warn", action="store_true",
                        help="also print WARN findings (UNKNOWN_ID, BAD_FILE), "
                             "which never affect the exit code")

    p_floor = sub.add_parser("floor", help="the visual/settings floor triage "
                                           "-- read-only, no bridge, no "
                                           "ModsConfig.xml write")
    p_floor.add_argument("--all", action="store_true", required=True,
                         help="every mod with a validation walk, one row "
                              "each (the only mode today)")

    sub.add_parser("doctor", help="the five registries keyed on a mod's folder "
                                  "name must agree with disk. Reports and "
                                  "stops -- never repairs; the ownership calls "
                                  "it surfaces are the owner's")

    sub.add_parser("metrics", add_help=False,
                   help="the daily test-orchestration metrics file (WASTE, unclassified share, lanes, gate misses, "
                        "alarms) at <testq>/metrics/<day>.json; `metrics --help` for its flags (modcheck/metrics.py)")

    args = ap.parse_args(argv)

    if args.cmd == "record":
        import record
        code, msg, _ = record.record(args.mod, args.result, args.tier or args.mod.lower(),
                                    ext_path=args.extensions)
        print(msg)
        return code

    if args.cmd == "doctor":
        import doctor
        return doctor.main([])

    if args.cmd == "lint":
        import runner
        import walklint
        findings, counts = walklint.lint(runner.ROOT)
        print("walklint: %d walks, %d packageIds, %d symbols indexed"
              % (counts["walks"], counts["packageids"], counts["symbols"]))
        if not counts["walks"] or not counts["packageids"]:
            print("UNMEASURED: an index came back empty -- this is a query bug, "
                  "not a clean repo. Refusing to report zero findings.")
            return 2
        shown = [f for f in findings
                 if f[0] == walklint.FAIL or args.warn]
        for f in shown:
            print(walklint.format_finding(f))
        n_fail = sum(1 for f in findings if f[0] == walklint.FAIL)
        n_warn = sum(1 for f in findings if f[0] == walklint.WARN)
        print("%d FAIL, %d WARN%s"
              % (n_fail, n_warn, "" if args.warn else "  (--warn to see WARNs)"))

        import readline_registry
        try:
            rl_findings, rl_counts = readline_registry.lint(runner.ROOT)
        except FileNotFoundError as exc:
            print("UNMEASURED: %s" % exc)
            return 2
        print("readline_registry: %d walks, %d registry ids, %d `shared` "
              "citations checked" % (rl_counts["walks"], rl_counts["registry_ids"],
                                     rl_counts["citations"]))
        for f in rl_findings:
            print(readline_registry.format_finding(f))
        print("%d FAIL" % len(rl_findings))

        return 1 if (n_fail or rl_findings) else 0

    if args.cmd == "floor":
        import floor
        import runner
        rows, footer = floor.triage(runner.ROOT)
        if not rows:
            print("UNMEASURED: no validation walks found -- this is a query "
                  "bug, not a clean repo. Refusing to report zero rows.")
            return 2
        print(floor.format_triage(rows, footer))
        return 0

    if args.cmd == "status":
        import status
        data = status.load()
        if args.mod:
            print(status.check(args.mod, _mod_dir_or_die(args.mod)))
            return 0
        if not data:
            print("no mods recorded")
            return 0
        import northstar
        import runner
        # Re-derive per row rather than printing entry["status"]. The stored
        # field is what made this summary disagree with `status <mod>`: it
        # printed `Pits GREEN` while the per-mod view printed STALE, and
        # `FluidCanals GREEN` for a mod renamed away weeks earlier.
        for mod, entry in sorted(data.items()):
            walk = northstar.find_walk(runner.ROOT, mod)
            ns = northstar.parse(walk) if walk else None
            bar = ("checklist %s (%d lines)" % (ns["state"], len(ns["must_show"]))
                   if ns and ns["present"] else "no checklist")
            live = status.check_or_orphaned(mod)
            stored = entry.get("status")
            drift = "" if live.split(" (")[0] == stored else "   [stored: %s]" % stored
            run = ""
            if entry.get("source"):     # a `modcheck record` entry: say what it was run at
                try:
                    cur = status.mod_hash(runner.find_mod_dir(mod))
                    at = "current hash" if cur == entry.get("hash") else "STALE hash"
                except RuntimeError:
                    at = "no mod folder"
                cnt = (entry.get("components") or {}).get("counts") or {}
                try:
                    s4 = status.step4_live(entry, runner.find_mod_dir(mod))
                except RuntimeError:
                    s4 = None
                run = "   [run %s at %s %s; %s%s]" % (
                    entry["source"].get("result", "?").rsplit("/", 1)[-1], at,
                    (entry.get("hash") or "")[:12],
                    " ".join("%s %d" % kv for kv in sorted(cnt.items())),
                    "" if s4 is None else "; step 4 %s" % s4)
            if len(live) > 60:
                live = live[:57] + "..."
            print("%-30s %-22s %s%s%s" % (mod, live, bar, drift, run))
        return 0

    if args.cmd == "declare":
        import status
        entry = status.declare_minor(args.mod, _mod_dir_or_die(args.mod), args.why)
        print("declared minor: %s at %s" % (args.mod, entry["hash"][:12]))
        return 0

    if args.cmd == "rename-key":
        import status
        status.rename_key(args.old, args.new, args.why)
        print("renamed: %s -> %s" % (args.old, args.new))
        return 0

    if args.cmd == "forget-key":
        import status
        status.forget_key(args.key, args.why)
        print("forgotten: %s" % args.key)
        return 0

    if args.cmd == "validate":
        return _validate(args.mod, args.owner_said or ("BY CARD: " + args.by_card if args.by_card else None))

    if args.cmd == "review":
        import status
        entry = status.record_owner_review(args.mod, args.owner_said,
                                          run_id=args.run_id)
        print("%s: owner review recorded against run %s -> %s"
              % (args.mod, entry["owner_review"]["run_id"], entry["status"]))
        return 0

    if args.cmd == "run":
        import runner
        if args.policy != "abort" and not args.situational:
            # MODCHECK_POLICY_FIX_RECORD_NEEDS_SITUATIONAL: only the situational Watch reads --policy; run4 was
            # launched `--policy record` without it and the policy was silently never read.
            print("REFUSED: --policy %s is read only by the situational envelope; add --situational or drop "
                  "--policy" % args.policy)
            return 2
        if args.changed is not None:
            import targeting
            if len(args.mods) != 1:
                print("REFUSED: --changed suggests chains for one mod")
                return 2
            try:
                mod_dir = runner.find_mod_dir(args.mods[0])
                suite = runner.load_validation(mod_dir)
                res = targeting.changed(suite, targeting.changed_files(mod_dir, args.changed), mod_dir)
            except (targeting.TargetError, RuntimeError) as ex:
                print("REFUSED: %s" % ex)
                return 2
            for line in targeting.changed_report(res):
                print(line)
            return 0
        if args.drivers is not None:
            import drivers  # noqa: E402
            os.environ[drivers.ENV] = "1" if args.drivers == "on" else "0"
        if args.reuse is not None:
            os.environ["MODCHECK_REUSE"] = {"off": "0", "report": "report", "on": "1"}[args.reuse]
        if args.gate is not None:
            os.environ["MODCHECK_GATE"] = args.gate
        if args.purpose is not None:
            os.environ["MODCHECK_PURPOSE"] = args.purpose
        elif args.full and not os.environ.get("MODCHECK_PURPOSE"):
            os.environ["MODCHECK_PURPOSE"] = "sweep"   # a sweep bypasses the gate (plan section 3)
        overrides = dict(kv.split("=", 1) for kv in args.item if "=" in kv)
        target_items = [kv for kv in args.item if "=" not in kv]
        chains = [c.strip() for c in args.chains.split(",") if c.strip()]
        rows = [r.strip() for r in args.rows.split(",") if r.strip()]
        targeted = bool(chains or rows or target_items)
        if targeted and args.full:
            print("REFUSED: --full and a target (--chains/--rows/--item ITEM_ID) contradict each other")
            return 2
        if args.preview and not targeted:
            print("REFUSED: --preview previews a TARGETED run; name --chains, --rows or --item ITEM_ID")
            return 2
        if not targeted and not args.full:
            print("REFUSED: a live run is TARGETED (owner 2026-10-25, standing_rulings.md \"Live runs are "
                  "TARGETED\"): name what the change touches with --item ITEM_ID, --chains a,b or --rows r1,r2. "
                  "The whole suite is a scheduled sweep (at most daily): add --full for that.")
            return 2
        targets = {}
        if targeted:
            if len(args.mods) != 1 or len(target_items) > 1:
                print("REFUSED: a targeted run names one mod and at most one --item ITEM_ID")
                return 2
            import targeting
            mod = args.mods[0]
            try:
                suite = runner.load_validation(runner.find_mod_dir(mod))
                text = targeting.item_text(target_items[0]) if target_items else None
                sel = targeting.resolve(suite, chains, rows, target_items[0] if target_items else None, text)
            except (targeting.TargetError, RuntimeError) as ex:
                print("REFUSED: %s" % ex)
                return 2
            for line in targeting.preview(sel):     # the exact plan, per chain, before anything launches
                print(line)
            if args.preview:
                return 0
            targets[mod] = sel
            if target_items and mod not in overrides:
                overrides[mod] = target_items[0]
        mods = [(m, overrides.get(m, "MODCHECK_%s_RUN_1" % m.upper()))
               for m in args.mods]
        results = runner.run(mods, debug=args.debug, dry_run=args.dry_run,
                             situational=args.situational, policy=args.policy,
                             targets=targets, seat=args.seat, canary=args.canary, validity=args.validity)
        bad = [m for m, r in results.items() if not r["all_green"]]
        for m, r in results.items():
            print("%-20s %s" % (m, _verdict_line(r)))
        return 1 if bad else 0

    return 2


def _verdict_line(result):
    """One line per mod. Names WHICH half failed, because "RED" alone sent the
    pit's real defect -- right state, absent appearance -- unnamed for a month."""
    if result.get("refused"):
        return "REFUSED  %s" % result["refused"]
    tg = result.get("targeted")
    if tg:      # never a bare GREEN/RED for a subset: it would read as the full-suite verdict
        scope = "TARGETED %d/%d chains (%s)" % (len(tg["chains"]), tg.get("of_chains", 0), ",".join(tg["chains"]))
        return scope + " " + _verdict_line(dict(result, targeted=None))
    if result["all_green"]:
        return "GREEN"
    failed = []
    if not result.get("state_all_green", result["all_green"]):
        failed.append("state")
    if result.get("visual") and not result.get("visual_all_green"):
        failed.append("judge: %s" % ", ".join(
            "%s=%s" % (v["id"], v["verdict"])
            for v in result["visual"] if not v["pass"]))
    return "RED" + ("  (%s)" % "; ".join(failed) if failed else "")


def _validate(mod, owner_said):
    """Print the must-show lines about to BIND, then record his validation.

    Refuses to bless silently, exactly as `code_review_status.py mark-clean`
    does: with no `--owner-said` this prints the bar and writes nothing, so the
    lines can be read to him first. That is the whole point of the verb -- an
    agent-drafted checklist becomes a bar only on his word (owner, 2026-09-15:
    'I write vision, agent writes checklist, I validate checklist').
    """
    import northstar
    import runner
    walk = northstar.find_walk(runner.ROOT, mod)
    if not walk:
        print("REFUSED: %s has no validation walk under design/validation_walks/"
              % mod)
        return 2
    ns = northstar.parse(walk)
    if not ns["present"]:
        print("REFUSED: %s has no `## north star` section -- there is nothing "
              "to validate.\n  %s" % (mod, walk))
        return 2

    print("%s — %s" % (mod, walk))
    print("state on disk: %s%s" % (ns["state"],
                                   "" if not ns["reason"] else "  (%s)" % ns["reason"]))

    # A present-but-misformatted section parses to zero bars, and validating
    # that writes VALIDATED against an empty checklist: `bar_for()` then returns
    # nothing, the visual floor finds nothing uncovered, and the mod silently
    # STOPS being refused. Refusing here is the only thing standing between a
    # formatting slip and a validation that means nothing. Both lists empty is
    # the refusal; must-show empty with cannot-show present is a legitimate
    # walk that only forbids things.
    if not ns["must_show"] and not ns["cannot_show"]:
        print("\nREFUSED: the `## north star` section parses to ZERO bars, so "
              "validating it would\nrecord an approval that binds nothing and "
              "silently stops %s being refused." % mod)
        print("  Expected line format:  - [ ] `some_bar_id` — what must be "
              "visible")
        print("  under a `### must show` or `### cannot show` subheading.")
        print("  Copy the shape from a walk that parses: "
              "design/validation_walks/RimMandrake/FlowWorks.md")
        print("  %s" % walk)
        return 2

    print("\nThese lines BIND once validated. Every one of them refuses the mod "
          "until some\ncomponent claims it with `shows=`, and is then judged "
          "against a screenshot:\n")
    for req_id in ns["must_show"]:
        print("  must    %-32s %s" % (req_id, ns["must_show_text"][req_id]))
    for req_id in ns["cannot_show"]:
        print("  cannot  %-32s %s" % (req_id, ns["cannot_show_text"][req_id]))

    if not owner_said:
        print("\n%d must-show + %d cannot-show lines would bind %s."
              % (len(ns["must_show"]), len(ns["cannot_show"]), mod))
        print("Nothing written. Read these to him; then re-run with "
              "--owner-said \"<his verbatim words>\".")
        return 1

    written = northstar.record_validation(walk)
    print("\nVALIDATED at %s\n  owner said: %s" % (written[:12], owner_said))
    print("  %d must-show + %d cannot-show lines now bind %s."
          % (len(ns["must_show"]), len(ns["cannot_show"]), mod))
    print("  Any later edit to the section reverts it to DRAFT by hash "
          "mismatch.")
    return 0


def _mod_dir_or_die(mod):
    import runner
    return runner.find_mod_dir(mod)


if __name__ == "__main__":
    sys.exit(main())
