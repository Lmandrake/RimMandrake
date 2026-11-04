#!/usr/bin/env python3
"""selftest_relentless_subagent_cap.py - RELENTLESS_SUBAGENT_DECIDE_THREE_PER_BUILDER: a builder run's subagents are
charged with it (their transcripts are added to a result-basis measure, so charge() sees them), and only then may a
builder start them: at most three, said in the worker brief from relentless_rules.json worker_subagent_cap, none for
a pilot sitting, and rm-builder carries the Agent tool."""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
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


def msg(mid, t, inp, out):
    return json.dumps({"type": "assistant", "timestamp": iso(t), "uuid": mid, "message": {
        "id": mid, "usage": {"input_tokens": inp, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
                             "output_tokens": out}}})


def usage(inp, out):
    return {"input_tokens": inp, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": out}


class Store:
    def __init__(self, d):
        self.dir = d

    def p(self, *a):
        return os.path.join(self.dir, *a)

    def _write(self, path, text):
        Path(path).write_text(text)


def measuring():
    tmp = tempfile.mkdtemp()
    os.environ["HOME"] = tmp
    now = time.time()
    clone = os.path.join(tmp, "clones", "ITEM")
    proj = U.project_dir(clone)
    os.makedirs(os.path.join(proj, "S1", "subagents"))
    os.makedirs(os.path.join(proj, "S0", "subagents"))
    Path(proj, "S1.jsonl").write_text(msg("main", now - 50, 1000, 100) + "\n")     # the main session: in the result
    Path(proj, "S1", "subagents", "agent-a.jsonl").write_text(
        "\n".join([msg("a1", now - 40, 500, 50), msg("a2", now - 30, 300, 20)]) + "\n")
    Path(proj, "S1", "subagents", "agent-b.jsonl").write_text(msg("b1", now - 20, 200, 10) + "\n")
    Path(proj, "S0", "subagents", "agent-z.jsonl").write_text(msg("z1", now - 45, 9000, 900) + "\n")   # another session
    out = os.path.join(tmp, "runs", "u.json")
    os.makedirs(os.path.dirname(out))
    run = {"unit": "u", "at": now - 100, "out": out, "err": out + ".err"}
    U.note_clone(run, clone)
    res = {"session_id": "S1", "usage": usage(1000, 100)}
    Path(out).write_text(json.dumps(res))
    main = RL.run_tokens(res)
    subs = RL.run_tokens({"usage": usage(1000, 80)})
    tok, basis = U.measure(RL, run)
    check("a result run is charged its own session's subagents too, not another session's",
          (tok, basis) == (main + subs, "result+subagents") and subs > 0, (tok, basis, main, subs))
    st = Store(tmp)
    s = {"spent": 0}
    R.charge(st, s, tok, now, {"run_reserve": 1200000}, "u", basis)
    day = json.loads(Path(st.p("spend-%s.json" % R.day_key(now))).read_text())
    check("charge() books the subagents' spend and says how it was reached",
          day["runs"]["u"] == main + subs and day["basis"].get("u") == "result+subagents", day)

    Path(out).write_text(json.dumps({"usage": usage(1000, 100)}))     # no session id: every subagent since the run began
    allsubs = RL.run_tokens({"usage": usage(10000, 980)})
    check("with no session id, every subagent in the clone since the run began is charged (dear, never cheap)",
          U.measure(RL, run) == (main + allsubs, "result+subagents"), U.measure(RL, run))
    Path(out).write_text(json.dumps({"session_id": "S9", "usage": usage(1000, 100)}))
    check("a run with no subagents is charged its result alone", U.measure(RL, run) == (main, "result"), U.measure(RL, run))
    run2 = dict(run, at=now - 10)
    Path(out).write_text(json.dumps(res))
    check("subagent messages from before the run are not charged", U.measure(RL, run2) == (main, "result"),
          U.measure(RL, run2))


def briefing():
    rules = json.loads((HERE / "relentless_rules.json").read_text())
    check("rules allow three subagents per builder", rules.get("worker_subagent_cap") == 3, rules.get("worker_subagent_cap"))
    st = R.new_state("X", 0, "t")
    st["approach"] = "build"
    p = R.worker_prompt(st, "item text", "", rules)
    check("the worker brief says at most three subagents, and no longer says none",
          "at most three subagents" in p and "no subagents" not in p, None)
    check("a cap above three is held at three", "at most three subagents" in R.subagent_rule(st, dict(rules, worker_subagent_cap=9)))
    check("cap 0, a missing or a bad cap says none",
          all(R.subagent_rule(st, x) == "no subagents" for x in
              (dict(rules, worker_subagent_cap=0), {k: v for k, v in rules.items() if k != "worker_subagent_cap"},
               dict(rules, worker_subagent_cap="3"), dict(rules, worker_subagent_cap=True))))
    check("one is said in the singular", "at most one subagent in" in R.subagent_rule(st, dict(rules, worker_subagent_cap=1)))
    pilot = dict(st, approach="pilot")
    if R.piloting(pilot):
        check("a pilot sitting (rm-testpilot, no Agent tool) is told none", R.subagent_rule(pilot, rules) == "no subagents")
    else:
        FAILS.append(("pilot fixture does not read as piloting; fix the fixture", pilot))
    head = (REPO / ".claude" / "agents" / "rm-builder.md").read_text().split("---")[1]
    tools = [t.strip() for t in next(x for x in head.splitlines() if x.startswith("tools:"))[6:].split(",")]
    check("rm-builder, the worker agent, carries the Agent tool", rules["worker_agent"] == "rm-builder" and "Agent" in tools, tools)
    check("rm-builder no longer forbids every subagent", "- No subagents." not in
          (REPO / ".claude" / "agents" / "rm-builder.md").read_text())


def main():
    measuring()
    briefing()
    print("selftest_relentless_subagent_cap: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    for f in FAILS:
        print("  ", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
