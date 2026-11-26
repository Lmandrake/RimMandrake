#!/usr/bin/env python3
"""selftest: the sweep of the account plan (RIMMANDRAKE_SWEEP_ACCOUNT_BURN_REGIMES_TWO_FAULTS_ONE_DAY; page
design/specs/2026-11-25-account-plan-sweep/boundary.md). One check per promise, by its name. The two faults of
2026-11-25 (fixed at 391283b692 and d469f03d9d) are planted again in a copy of the code, and the sweep's quick part must
name each one; the published code must read green.

    python3 src/RimMandrake/Utils/selftest_account_plan_sweep.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
sys.path.insert(0, str(HERE))
import account_plan_sweep as S  # noqa: E402

FAILS = []
P = "Utils/account_plan.py"
# the fault of 391283b692: a soft decision only because the live level is not read was a pending switch
UNREAD = [(P, '            return {**base, "do": "soft", "unread": True,   # no switch is pending: the level is only unread',
           '            return {**base, "do": "soft",   # planted: the unread mark is gone'),
          (P, '        return {**base, "do": "soft", "unread": True,       # no switch is pending: the level is only unconfirmed',
           '        return {**base, "do": "soft",       # planted: the unread mark is gone')]
# the fault of d469f03d9d: a machine on an account that no step uses was switched only at its line
NO_STEP = [(P, '    if not (n.get("account_end") or finished):', '    if not n.get("account_end"):')]


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok or not detail else ": " + str(detail)[:600]))
    if not ok:
        FAILS.append(name)


def quick_in_copy(plants):
    """-> ({region name: {check: count}}, output) of `account_plan_sweep.py quick` in a copy of the code, plants in."""
    tmp = Path(tempfile.mkdtemp(prefix="account_plan_sweep_selftest_"))
    try:
        root = tmp / "src" / "RimMandrake"
        for d in ("Utils", "rimflow", "contracts"):
            shutil.copytree(SRC / d, root / d, ignore=shutil.ignore_patterns("__pycache__", "*.png", "*.dll"))
        hooks = tmp / ".claude" / "hooks"
        hooks.mkdir(parents=True)
        shutil.copy(S.HOOK, hooks / S.HOOK.name)
        for rel, old, new in plants:
            p = root / rel
            text = p.read_text(encoding="utf-8")
            if text.count(old) != 1:
                return None, "the plant's anchor is found %d times in %s: %s" % (text.count(old), rel, old.strip()[:80])
            p.write_text(text.replace(old, new), encoding="utf-8")
        out = tmp / "quick.json"
        r = subprocess.run([sys.executable, str(root / "Utils" / "account_plan_sweep.py"), "quick", "--json", str(out)],
                           capture_output=True, text=True, timeout=900,   # budget: class=call (a hang guard)
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=""))
        if not out.exists():
            return None, r.stdout[-1500:] + r.stderr[-1500:]
        res = json.loads(out.read_text())
        return {x["name"]: {c: (v["count"], v["detail"]) for c, v in x["violations"].items()} for x in res}, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_the_sweep_runs_the_real_pass():
    n = "the_sweep_runs_the_real_pass"
    src = (HERE / "account_plan_sweep.py").read_text()
    check(n + ": each pass is account_plan.tick with seams", "AP.tick(seams=seams)" in src)
    for word in ("def decide(", "def notice_of(", "def new_run_gate(", "def machine_notice(", "def drained("):
        check(n + ": the sweep defines no %s of its own" % word.strip("("), word not in src)


def t_the_sweep_is_deterministic():
    n = "the_sweep_is_deterministic"
    reg = S.realize(S.QUICK[0][1], 3, 8)
    a, b = S.run_regime(reg), S.run_regime(reg)
    keep = lambda r: (r["violations"], r["measures"], r["bound"])   # noqa: E731
    check(n + ": the same regime and seed give the same violations, measures and bound", keep(a) == keep(b),
          (keep(a), keep(b)))
    check(n + ": a regime is drawn the same from its spec and seed", S.realize(S.QUICK[1][1], 2) == S.realize(
        S.QUICK[1][1], 2))


def t_the_sweep_touches_no_live_folder():
    n = "the_sweep_touches_no_live_folder"
    import subprocess as sp
    calls = []
    real = sp.run, sp.Popen

    def no_process(*a, **k):
        calls.append(a[0] if a else k.get("args"))
        raise AssertionError("the sweep started a process: %s" % (a[0] if a else k))
    sp.run, sp.Popen = no_process, no_process
    try:
        r = S.run_regime(S.realize(S.QUICK[2][1], 1, 6))
    finally:
        sp.run, sp.Popen = real
    check(n + ": a regime starts no process (no switcher, ssh, systemd, meter or ledger call)", not calls, calls[:3])
    check(n + ": and it ran its passes", r["passes"] >= 70, r["passes"])
    check(n + ": its folders are the scratch world's", str(S.ROOT).startswith(tempfile.gettempdir())
          and str(S.SP.OUT).startswith(str(S.ROOT)) and S.SP.OUT != S.SP.LIVE_OUT
          and str(S.AP.plan_dir()).startswith(str(S.ROOT)) and str(S.AP.notice_dir()).startswith(str(S.ROOT)))
    check(n + ": a live folder set for the scratch world is refused", _refuses_live())


def _refuses_live():
    saved = S.SP.LIVE_OUT
    try:
        S.SP.LIVE_OUT = S.ROOT / "out"
        S.fresh_dirs()
    except AssertionError:
        return True
    finally:
        S.SP.LIVE_OUT = saved
    return False


def t_the_quick_part_is_green_on_this_code():
    n = "the_quick_part_is_green_on_this_code"
    got, out = quick_in_copy([])
    check(n + ": the quick part reads no VIOLATES on the published code", got is not None and not any(got.values()),
          got if got is not None else out)


def t_the_sweep_finds_the_fault_of_391283b692():
    n = "the_sweep_finds_the_fault_of_391283b692"
    got, out = quick_in_copy(UNREAD)
    hit = (got or {}).get("quick: the live account's reset passes with no level read for 20-60 min", {})
    check(n + ": with the unread mark gone, FALSE_PENDING in the region of a reset passed with no level",
          "FALSE_PENDING" in hit, got if got is not None else out)


def t_the_sweep_finds_the_fault_of_d469f03d9d():
    n = "the_sweep_finds_the_fault_of_d469f03d9d"
    got, out = quick_in_copy(NO_STEP)
    hit = (got or {}).get("quick: SteveDesktop on an account that no step uses", {})
    check(n + ": with the machine switched only at its line, STUCK on SteveDesktop in that region",
          "STUCK" in hit and hit["STUCK"][1].get("machine") == S.STEVE, got if got is not None else out)


def main():
    try:
        for t in (t_the_sweep_runs_the_real_pass, t_the_sweep_is_deterministic, t_the_sweep_touches_no_live_folder,
                  t_the_quick_part_is_green_on_this_code, t_the_sweep_finds_the_fault_of_391283b692,
                  t_the_sweep_finds_the_fault_of_d469f03d9d):
            try:
                t()
            except Exception as e:  # noqa: BLE001  a check that broke is a FAIL of its promise, by name
                import traceback
                check(t.__name__[2:] + ": the check itself broke", False, "%s: %s | %s" % (
                    type(e).__name__, e, traceback.format_exc().strip().splitlines()[-3:]))
    finally:
        shutil.rmtree(S.ROOT, ignore_errors=True)
    print("\n%s: %d FAIL" % ("selftest_account_plan_sweep", len(FAILS)))
    for f in FAILS:
        print("  FAIL " + f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
