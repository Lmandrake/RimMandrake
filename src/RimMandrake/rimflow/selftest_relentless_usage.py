#!/usr/bin/env python3
"""selftest_relentless_usage.py - RELENTLESS_USAGE_MEASURE_NO_FLAT_GUESSES: every run's usage is measured (result,
else transcript), a flat reserve is labelled estimated, and only Relentless's own OOM kills step staffing down."""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import relentless as R          # noqa: E402
import relentless_usage as U    # noqa: E402
import role_launch as RL        # noqa: E402

FAILS = []


def check(name, ok, got=None):
    print("%s %s" % ("ok  " if ok else "FAIL", name))
    if not ok:
        FAILS.append((name, got))


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(t))


def msg(mid, t, inp, cw, cr, out):
    return json.dumps({"type": "assistant", "timestamp": iso(t), "uuid": mid + str(out), "message": {
        "id": mid, "usage": {"input_tokens": inp, "cache_creation_input_tokens": cw, "cache_read_input_tokens": cr,
                             "output_tokens": out,
                             "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": cw}}}})


class Store:
    def __init__(self, d):
        self.dir = d

    def p(self, *a):
        return os.path.join(self.dir, *a)

    def _write(self, path, text):
        Path(path).write_text(text)


def main():
    tmp = tempfile.mkdtemp()
    os.environ["HOME"] = tmp
    now = time.time()
    clone = os.path.join(tmp, "clones", "ITEM")
    proj = U.project_dir(clone)
    os.makedirs(os.path.join(proj, "sess", "subagents"))
    Path(proj, "a.jsonl").write_text("\n".join([
        msg("m1", now - 50, 2, 1000, 0, 100),
        msg("m1", now - 50, 2, 1000, 0, 400),          # the same message again, longer: counted once, at its largest
        msg("m2", now - 40, 2, 0, 1000, 50),
        msg("old", now - 9000, 9, 9999999, 0, 9),      # before the run began
    ]) + "\n")
    Path(proj, "sess", "subagents", "b.jsonl").write_text(msg("s1", now - 30, 1, 0, 0, 10) + "\n")
    out = os.path.join(tmp, "runs", "u.json")
    run = {"unit": "u", "at": now - 100, "out": out, "err": out + ".err"}
    U.note_clone(run, clone)
    check("the clone is remembered beside the result", U.clone_of(run) == clone)
    tr = U.transcript_result(clone, run["at"])
    u = tr["usage"]
    check("one message counts once, at its largest; before-the-run and subagents handled",
          (u["input_tokens"], u["cache_creation_input_tokens"], u["cache_read_input_tokens"], u["output_tokens"]) ==
          (5, 1000, 1000, 460), u)
    want = RL.run_tokens(tr)
    tok, basis = U.measure(RL, run)
    check("a killed run (no result) is charged its transcript, not the flat reserve", (tok, basis) == (want, "transcript") and 0 < tok < 100000, (tok, basis))
    Path(out).write_text(json.dumps({"session_id": "a", "usage": {"input_tokens": 1, "cache_creation_input_tokens": 0,
                                                "cache_read_input_tokens": 0, "output_tokens": 1}}))
    check("a result object wins", U.measure(RL, run) == (6, "result"), U.measure(RL, run))
    zero = {"input_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 0}
    Path(out).write_text(json.dumps({"session_id": "nosuch", "is_error": True, "duration_api_ms": 0, "usage": zero}))
    check("a measured all-zero result (API 429) is measured 0 from the result, not estimated",
          U.measure(RL, run) == (0, "result"), U.measure(RL, run))
    Path(proj, "sess.jsonl").write_text(msg("z1", now - 20, 3, 0, 0, 7) + "\n")
    Path(out).write_text(json.dumps({"session_id": "sess", "usage": zero}))
    check("a zero result whose own session transcript spent is charged the dearer transcript",
          U.measure(RL, run) == (RL.run_tokens(U.transcript_result(clone, run["at"], session="sess")), "transcript")
          and 0 < U.measure(RL, run)[0] < want, (U.measure(RL, run), want))
    os.unlink(os.path.join(proj, "sess.jsonl"))
    os.unlink(out)
    ghost = {"unit": "g", "at": now, "out": os.path.join(tmp, "runs", "g.json"), "err": ""}
    check("nothing anywhere is labelled estimated, never a number", U.measure(RL, ghost) == (0, "estimated"))

    st = Store(tmp)
    rules = {"run_reserve": 1200000}
    s = {"spent": 0}
    check("an unmeasurable run still costs the reserve", R.charge(st, s, 0, now, rules, "g", "estimated") == 1200000)
    check("a measured all-zero result is charged 0, not the reserve",
          R.charge(st, s, 0, now, rules, "z", "result") == 0)
    check("a zero with no basis still costs the reserve", R.charge(st, s, 0, now, rules, "y") == 1200000)
    R.charge(st, s, 77, now, rules, "u", "transcript")
    R.charge(st, s, 5, now, rules, "v", "result")
    day = json.loads(Path(st.p("spend-%s.json" % R.day_key(now))).read_text())
    check("the day file says which charges were not read from a result",
          day["basis"] == {"g": "estimated", "u": "transcript"} and day["runs"]["z"] == 0 and day["runs"]["u"] == 77, day)
    check("and the spend record is still readable as before", R.spent_today(st, now) == 2400082, R.spent_today(st, now))

    lines = ["x oom-kill:constraint=CONSTRAINT_MEMCG,oom_memcg=/a/rm-harness-1-2.scope,task=python3",
             "oom-kill:constraint=CONSTRAINT_MEMCG,oom_memcg=/a/claude-seat-BENCH-123.scope/claude-code-bash",
             "oom-kill:constraint=CONSTRAINT_MEMCG,oom_memcg=/a/claude-seat-BENCH-rm-relentless-work-ab-g3.scope/claude-code-bash",
             "python3 invoked oom-killer: rm-relentless"]
    check("only a kill inside a Relentless cgroup is Relentless's", U.own_oom_kills(lines) == 1, U.own_oom_kills(lines))
    rules_all = json.loads((HERE / "relentless_rules.json").read_text())
    stages = [x for x in rules_all["staffing"]["stages"] if x != "budget"]
    check("staffing top stage is 3-8 workers, under max_workers, and with its checks and a consult fits the 16-clone pool"
          " (owner card 2026-11-02: 8 workers, 16 clones / 70 GB)",
          stages and 3 <= max(stages) <= 8 and max(stages) <= rules_all["max_workers"] <= 8
          and rules_all["max_workers"] + rules_all["staffing"]["check_backlog_max"] + 1 <= 16, rules_all["staffing"]["stages"])
    print("selftest_relentless_usage: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
