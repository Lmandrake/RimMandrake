# RIMMANDRAKE_FIX_LIVE_PANEL_COUNTS_A_LOG_NOBODY_WRITES

## spec

`src/RimMandrake/Utils/running_now.py` `collect_archmagi_live` (the Archmagi "live testing" panel, its plain-text
twin and the machine row) counts the last 24 h of proof rows from `LIVE_RUNS` =
`/home/mandrake/rm/relentless/live/runs.jsonl`. Only the retired Relentless live round wrote that file; its last
write is 2026-11-06 18:26 PST (measured 2026-11-19, `ls -l`). So the panel shows a measured-looking 0 rows and 0 bugs
every day: an instrument that cannot see, reporting zero. Found by
`RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS` (census row "running_now.py line 594").

Do: read today's live proof runs on Archmagi (the testq lane's own records) instead, or, until one is wired, return
the rows as UNMEASURED with the cause ("no writer since the retired live round") and make every renderer that reads
`rows` (`running_now.py` near lines 847, 1108, 1134, 1601) print UNMEASURED rather than `or {}` zero. The bridge-busy
and game-up shares in the same panel are live and stay. Update `selftest_running_now.py` cases that plant `LIVE_RUNS`.

## verify

Acceptance test (watched failing 2026-11-19 BENCH on `ed3b6ca7a5`: "FAIL: a run log last written 13 days ago reads
as a measured 0 rows: Counter()", rc=1). Run from the repo root; expected `PASS`, rc 0, 1 check:

    python3 - <<'PY'
    import sys, json, time; sys.path.insert(0, "src/RimMandrake/Utils"); import running_now as R
    now = time.time()
    old = json.dumps({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - 13 * 86400)), "item": "A", "criterion": "A1", "outcome": "PASS"}) + "\n"
    class E:
        def read_text(self, p): return old
        def bridge_events(self): return []
    out, why = R.guarded(R.collect_archmagi_live, E(), now, [])
    ok = why is not None or (out or {}).get("rows") is None
    print("PASS" if ok else "FAIL: a run log last written 13 days ago reads as a measured 0 rows: %r" % ((out or {}).get("rows"),))
    sys.exit(0 if ok else 1)
    PY

plus `python3 src/RimMandrake/Utils/selftest_running_now.py` green.

## criteria

- A1: a proof-run log with no row in 13 days is UNMEASURED with its cause, never a count of 0 (the test above).
- A2: the panel's renderers print UNMEASURED for unread rows (selftest_running_now case).

## refs

file: src/RimMandrake/Utils/running_now.py
file: src/RimMandrake/Utils/selftest_running_now.py
