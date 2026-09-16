#!/usr/bin/env python3
"""modcheck -- the scripted mod-functionality validator (pre-playtest).

    python.exe src/RimMandrake/Utils/modcheck/cli.py run <mod> [<mod>...] [--debug]
    python3     src/RimMandrake/Utils/modcheck/cli.py status
    python3     src/RimMandrake/Utils/modcheck/cli.py declare <mod> minor --why "..."
    python3     src/RimMandrake/Utils/modcheck/cli.py validate <mod> [--owner-said "..."]
    python3     src/RimMandrake/Utils/modcheck/cli.py review <mod> --owner-said "..."

`run` drives a live bridge session and needs `python.exe` (Windows) for the
same WSL-loopback reason every other bridge driver does
(rimbridge_client.py). `status` and `declare` touch only
`infrastructure/state/modcheck_status.json` and run fine under plain
`python3`.

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

    args = ap.parse_args(argv)

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
        for mod, entry in sorted(data.items()):
            walk = northstar.find_walk(runner.ROOT, mod)
            ns = northstar.parse(walk) if walk else None
            bar = ("checklist %s (%d lines)" % (ns["state"], len(ns["must_show"]))
                   if ns and ns["present"] else "no checklist")
            print("%-30s %-22s %s" % (mod, entry.get("status"), bar))
        return 0

    if args.cmd == "declare":
        import status
        entry = status.declare_minor(args.mod, _mod_dir_or_die(args.mod), args.why)
        print("declared minor: %s at %s" % (args.mod, entry["hash"][:12]))
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
    print("\nThese lines BIND once validated. Every one of them refuses the mod "
          "until some\ncomponent claims it with `shows=`, and is then judged "
          "against a screenshot:\n")
    for req_id in ns["must_show"]:
        print("  must    %-32s %s" % (req_id, ns["must_show_text"][req_id]))
    for req_id in ns["cannot_show"]:
        print("  cannot  %-32s %s" % (req_id, ns["cannot_show_text"][req_id]))

    if not owner_said:
        print("\nNothing written. Read these to him; then re-run with "
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
