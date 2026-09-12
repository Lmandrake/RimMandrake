#!/usr/bin/env python3
"""modcheck -- the scripted mod-functionality validator (pre-playtest).

    python.exe src/RimMandrake/Utils/modcheck/cli.py run <mod> [<mod>...] [--debug]
    python3     src/RimMandrake/Utils/modcheck/cli.py status
    python3     src/RimMandrake/Utils/modcheck/cli.py declare <mod> minor --why "..."

`run` drives a live bridge session and needs `python.exe` (Windows) for the
same WSL-loopback reason every other bridge driver does
(rimbridge_client.py). `status` and `declare` touch only
`infrastructure/state/modcheck_status.json` and run fine under plain
`python3`.
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
        for mod, entry in sorted(data.items()):
            print("%-30s %s" % (mod, entry.get("status")))
        return 0

    if args.cmd == "declare":
        import status
        entry = status.declare_minor(args.mod, _mod_dir_or_die(args.mod), args.why)
        print("declared minor: %s at %s" % (args.mod, entry["hash"][:12]))
        return 0

    if args.cmd == "run":
        import runner
        overrides = dict(kv.split("=", 1) for kv in args.item)
        mods = [(m, overrides.get(m, "MODCHECK_%s_RUN_1" % m.upper()))
               for m in args.mods]
        results = runner.run(mods, debug=args.debug, dry_run=args.dry_run)
        bad = [m for m, r in results.items() if not r["all_green"]]
        for m, r in results.items():
            print("%-20s %s" % (m, "GREEN" if r["all_green"] else "RED"))
        return 1 if bad else 0

    return 2


def _mod_dir_or_die(mod):
    import runner
    return runner.find_mod_dir(mod)


if __name__ == "__main__":
    sys.exit(main())
