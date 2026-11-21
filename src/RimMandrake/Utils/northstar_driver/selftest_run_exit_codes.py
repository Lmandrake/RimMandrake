#!/usr/bin/env python3
"""selftest_run_exit_codes: the exit-code contract of `northstar_driver/cli.py run` (its page:
design/specs/2026-11-21-northstar-run-exit-codes/boundary.md). Offline: mock runs, and one real (non-mock) run aimed at
a port where no game listens, so no game is reached. Exit 0 = every promise holds, 1 = one does not (named)."""
import os
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
for p in (_UTILS, os.path.join(_UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)
from northstar_driver import bars as B, cli  # noqa: E402

DEAD_PORT = "5999"   # no game instance listens there (game_instance.py: game a 5174, game b 5175)
TMP = tempfile.mkdtemp(prefix="ns_exit_")
PLAN = os.path.join(TMP, "plan.py")
with open(PLAN, "w") as f:
    f.write("from northstar_driver import bars as B\nMOD='SelftestMod'\nRECT='90,90,20,20'\n"
            "@B.bar('st.1', mod='SelftestMod')\ndef f(t):\n    return B.passed('hi')\n")


def _run(argv, env=None):
    """-> (exit code or 'raised', the reason text). An exception escaping main() is what Python turns into exit 1."""
    B.REGISTRY.clear()
    keep = {k: os.environ.get(k) for k in (env or {})}
    os.environ.update(env or {})
    try:
        code = cli.main(argv)
        return code, "code=%s" % code
    except BaseException as ex:  # noqa: BLE001 - the defect under test: an escape out of main()
        return "raised", "%s: %s" % (type(ex).__name__, str(ex)[:160])
    finally:
        for k, v in keep.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)


def t_clean_run_exits_0():
    out = os.path.join(TMP, "clean.json")
    code, why = _run(["run", "--mock", "--plan", PLAN, "--out", out, "--mod", "SelftestMod"])
    return code == 0 and os.path.isfile(out), why


def t_dirty_site_is_refused():
    out = os.path.join(TMP, "dirty.json")
    code, why = _run(["run", "--mock", "--fault", "modal", "--plan", PLAN, "--out", out, "--mod", "SelftestMod"])
    import json
    return code == 2 and os.path.isfile(out) and json.load(open(out))["bars"] == [], why


def t_unreachable_bridge_is_refused():
    # RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START: with the game down this run exited 1 (a traceback,
    # measured 2026-11-21 4:35 AM PST), so red_seen and a Stage 6 reader read "no game" as a failed bar.
    out = os.path.join(TMP, "dead.json")
    code, why = _run(["run", "--plan", PLAN, "--out", out, "--mod", "SelftestMod", "--no-record"],
                     env={"GABP_SERVER_PORT": DEAD_PORT, "GABP_TOKEN": "selftest", "RIMBRIDGE_HOST": "127.0.0.1",
                          "RM_GAME_INSTANCE": ""})
    return code == 2 and not os.path.exists(out), why


def main():
    res = []
    for name, fn in (("clean-run-exits-0", t_clean_run_exits_0), ("dirty-site-is-refused", t_dirty_site_is_refused),
                     ("unreachable-bridge-is-refused", t_unreachable_bridge_is_refused)):
        ok, why = fn()
        res.append(ok)
        print("%s  %s  %s" % ("ok  " if ok else "FAIL", name, why))
    print("selftest_run_exit_codes: %s (%d of %d)" % ("PASS" if all(res) else "FAIL", sum(res), len(res)))
    return 0 if all(res) else 1


if __name__ == "__main__":
    sys.exit(main())
