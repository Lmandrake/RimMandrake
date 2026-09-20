#!/usr/bin/env python3
"""modcheck -- the scripted mod-functionality validator (pre-playtest).

    python.exe src/RimMandrake/Utils/modcheck/cli.py run <mod> [<mod>...] [--debug]
    python3     src/RimMandrake/Utils/modcheck/cli.py status
    python3     src/RimMandrake/Utils/modcheck/cli.py declare <mod> minor --why "..."
    python3     src/RimMandrake/Utils/modcheck/cli.py rename-key <old> <new> --why "..."
    python3     src/RimMandrake/Utils/modcheck/cli.py forget-key <key> --why "..."
    python3     src/RimMandrake/Utils/modcheck/cli.py validate <mod> [--owner-said "..."]
    python3     src/RimMandrake/Utils/modcheck/cli.py review <mod> --owner-said "..."

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
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run")
    p_run.add_argument("mods", nargs="+",
                       help="mod folder name(s), e.g. Pits")
    p_run.add_argument("--item", action="append", default=[],
                       help="rimflow item id for a mod, MOD=ITEM_ID; "
                            "defaults to MODCHECK_<MOD>_RUN_1")
    p_run.add_argument("--debug", action="store_true")
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

    p_rev = sub.add_parser("review", help="record that the owner reviewed a "
                                          "mod's sheet -- once, before its first GREEN")
    p_rev.add_argument("mod")
    p_rev.add_argument("--owner-said", required=True)
    p_rev.add_argument("--run-id", help="defaults to the mod's last recorded run")

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

    args = ap.parse_args(argv)

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
        return 1 if n_fail else 0

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
            print("%-30s %-22s %s%s" % (mod, live, bar, drift))
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
        return _validate(args.mod, args.owner_said)

    if args.cmd == "review":
        import status
        entry = status.record_owner_review(args.mod, args.owner_said,
                                          run_id=args.run_id)
        print("%s: owner review recorded against run %s -> %s"
              % (args.mod, entry["owner_review"]["run_id"], entry["status"]))
        return 0

    if args.cmd == "run":
        import runner
        overrides = dict(kv.split("=", 1) for kv in args.item)
        mods = [(m, overrides.get(m, "MODCHECK_%s_RUN_1" % m.upper()))
               for m in args.mods]
        results = runner.run(mods, debug=args.debug, dry_run=args.dry_run)
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
