# RIMMANDRAKE_REQUIRE_HELPER_SPEND_CAP_FIFTEEN_STOPPED_FOUR_RUNS

## spec

`src/RimMandrake/rimflow/detached_helper.py` sets `DEFAULT_BUDGET_USD = 15.0` and `launch --budget-usd` defaults to it.
Under §No limit without the danger it guards (`design/RimMandrake/standing_rulings.md`, owner 2026-11-16: *"Each
element must defend precisely what it's protecting against and have evidence that it actually happens"*) the per-run
spend stop has its danger and evidence (a runaway unattended burn, *"not burn 90M tokens overnight by itself"* and
*"Don't let any burn go to 90M this time ok?"*, 2026-11-12/13, the stop he ordered), but the default LEVEL of $15 has
none: nothing measured says a run past $15 is a runaway, and the level stopped at least four legitimate runs, recorded
in three lessons: an eleven-item batch (`infrastructure/state/lessons/20261117T142459Z-BENCH-relaunch-keeps-default-budget.md`),
the GSS Fable relaunch whose `--resume` came back under the default after a `--budget-usd 0` launch
(`20261117T142459Z-BENCH-relaunch-keeps-default-budget.md`), and the old-ticket sweep and the second-wave builds lane
(`20261117T142459Z-BENCH-relaunch-keeps-default-budget.md`).

Do: make `--budget-usd` REQUIRED on `detached_helper.py launch` (no default), as `maturation.py launch` already is
(`REFUSED: a spend cap is required (--budget-usd > 0); there is no default`). The launcher picks the cap for the job it
is launching, and `--budget-usd 0` stays the explicit "no cap". Then fix every caller that relied on the default
(code: `grep -rn "detached_helper.py.*launch\|detached_helper.launch" src/`; docs that show a launch line without
`--budget-usd`, e.g. `src/RimMandrake/rimflow/roles/conductor.md`). Callers that already pass a cap (`red_dispatch.py`,
`maturation_autonomy.py`, `maturation.py`, `left_open_continue.py` from the run record) are unchanged. Do not pick a
new default number: a default with no evidence is the defect. The spend watchdog itself is not touched.

## verify

Acceptance test, run from the repo root (3 cases: no flag refuses before launching, `0` passes through, `40` passes
through):

    python3 -c "
    import sys; sys.path.insert(0,'src/RimMandrake/rimflow'); import detached_helper as d
    calls=[]; d.launch=lambda *a,**k: calls.append(a) or (0,'stub')
    def run(extra):
        calls.clear()
        try: rc=d.main(['launch','--seat','BENCH','--item','X','--brief','b']+extra)
        except SystemExit as e: rc=e.code
        return rc, [c[5] for c in calls]
    r=[run([])==(2,[]), run(['--budget-usd','0'])==(0,[0.0]), run(['--budget-usd','40'])==(0,[40.0])]
    print('%d of 3 PASS' % sum(r), r); sys.exit(0 if all(r) else 1)" 2>/dev/null

Expected: `3 of 3 PASS`, exit 0. Watched failing 2026-11-19 (BENCH, at `338b3cae50`): `2 of 3 PASS [False, True,
True]`, exit 1 (the bare launch reached `launch` with 15.0). Watched passing on a copy of the module with only
`required=True` on `--budget-usd`: `3 of 3 PASS`. Also run `python3 src/RimMandrake/rimflow/selftest_detached_helper.py`
(it must stay green).

## criteria

- A1: a `detached_helper.py launch` without `--budget-usd` is refused before anything launches (test case 1).
- A2: an explicit cap, `0` included, is carried unchanged (cases 2 and 3).
- A3: no caller in `src/` or a role file shows a launch line without `--budget-usd`.

## refs

file: src/RimMandrake/rimflow/detached_helper.py
file: src/RimMandrake/rimflow/roles/conductor.md
