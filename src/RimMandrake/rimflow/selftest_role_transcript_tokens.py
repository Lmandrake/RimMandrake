#!/usr/bin/env python3
"""A role run with no result is measured from its transcript, never charged its budget
(OPS_ROLE_DIAGNOSE_STARVED_AT_FOUR_RUNS, 2026-11-02).

rm-role-operations-1793618968 was frozen by the 03:34 PST emergency stop and killed at run_max_s: its out file was
empty, so it was charged "UNMEASURED (counted at its budget)" = 450,000 against the daily cap. Its transcript
(session 869e5e3a) held 12 API messages weighing 261,105. The fix pins `--session-id` at launch and reads the
transcript when the result is missing:
  T1 launch_argv carries --session-id when given; launch() makes one and returns it for the run record.
  T2 transcript_usage sums each message id ONCE (a message is logged once per content block with the same usage),
     with the cache TTL split, and includes the session's subagent transcripts.
  T3 a run launched before the pin (no `session`) is found by its unit in the first lines of a recent transcript;
     an older transcript naming the same unit is not taken.
  T4 no transcript, or one with no assistant turn -> None (UNMEASURED, still counted at its budget).
  T5 _supervise_one: a dead run with no result but a transcript is FAILED and counted at its measured tokens,
     token_source "transcript", its role_done saying so; with no transcript it is still UNMEASURED.
"""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import role_launch as RL  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def msg_lines(mid, usage, blocks=2):
    """One API message as the transcript logs it: one line per content block, the same usage on each."""
    return [json.dumps({"type": "assistant", "message": {"id": mid, "usage": usage,
                                                         "content": [{"type": "text", "text": "b%d" % i}]}})
            for i in range(blocks)]


U1 = {"input_tokens": 10, "cache_creation_input_tokens": 1000, "cache_read_input_tokens": 5000, "output_tokens": 100,
      "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 1000}}
U2 = {"input_tokens": 2, "cache_creation_input_tokens": 200, "cache_read_input_tokens": 6000, "output_tokens": 50,
      "cache_creation": {"ephemeral_5m_input_tokens": 200, "ephemeral_1h_input_tokens": 0}}
US = {"input_tokens": 1, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 100, "output_tokens": 10,
      "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 0}}
WANT = {"input_tokens": 13, "cache_creation_input_tokens": 1200, "cache_read_input_tokens": 11100, "output_tokens": 160,
        "cache_creation": {"ephemeral_5m_input_tokens": 200, "ephemeral_1h_input_tokens": 1000}}


def write(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    # T1
    role = {"name": "Operations", "seat": "BENCH", "clone": "/c", "model": "opus", "run_max_s": 100}
    a = RL.launch_argv(role, "U", "MSG", "/o", "/e", "/bin/claude", "11111111-2222-3333-4444-555555555555")
    check(a[a.index("--session-id") + 1] == "11111111-2222-3333-4444-555555555555", "T1 argv carries --session-id")
    check("--session-id" not in RL.launch_argv(role, "U", "MSG", "/o", "/e", "/bin/claude"), "T1 no session, no flag")
    seen = {}

    class R:
        returncode, stdout, stderr = 0, "", ""

    def runner(argv, **kw):
        seen["argv"] = argv
        return R()
    with tempfile.TemporaryDirectory() as root:
        ok, _, rec = RL.launch(role, "rm-role-operations-9", "M", root, "/bin/claude", runner=runner)
        sid = rec.get("session")
        check(ok and sid and seen["argv"][seen["argv"].index("--session-id") + 1] == sid,
              "T1 launch makes a session id, passes it and returns it (%r)" % sid)

    with tempfile.TemporaryDirectory() as proj:
        sid = "aaaaaaaa-0000-0000-0000-000000000001"
        user = json.dumps({"type": "user", "message": {"content": "[RimFlow Dispatcher; role launch rm-role-x-5] go"}})
        write(os.path.join(proj, "-c", sid + ".jsonl"), [user] + msg_lines("m1", U1, 3) + ["not json"]
              + msg_lines("m2", U2, 1) + [json.dumps({"type": "user", "message": {"content": "r"}})])
        write(os.path.join(proj, "-c", sid, "subagents", "agent-1.jsonl"), msg_lines("s1", US, 2))
        # T2
        got = RL.transcript_usage({"session": sid, "unit": "rm-role-x-5", "at": 0}, proj)
        check(got == WANT, "T2 each message id once, TTL split summed, subagents included (%r)" % (got,))
        check(RL.run_tokens({"usage": got}) == 13 + 200 * 1.25 + 1000 * 2 + 1110 + 800,
              "T2 weighs as a result would (%r)" % RL.run_tokens({"usage": got}))
        # T3
        got3 = RL.transcript_usage({"unit": "rm-role-x-5", "at": time.time() - 30}, proj)
        check(got3 is not None and got3["output_tokens"] == 150, "T3 found by unit without a session (%r)" % (got3,))
        check(RL.transcript_usage({"unit": "rm-role-x-5", "at": time.time() + 3600}, proj) is None,
              "T3 a transcript older than the run is not taken")
        check(RL.transcript_usage({"unit": "rm-role-x-6", "at": 0}, proj) is None, "T3 another unit is not taken")
        # T4
        check(RL.transcript_usage({"session": "nope", "unit": "u", "at": 0}, proj) is None, "T4 no transcript -> None")
        write(os.path.join(proj, "-c", "empty.jsonl"), [user.replace("rm-role-x-5", "rm-role-x-7")])
        check(RL.transcript_usage({"session": "empty", "unit": "u", "at": 0}, proj) is None,
              "T4 no assistant turn -> None")

        # T5
        def supervise(transcript):
            acts = []
            obs = {"unit_state": lambda u: "inactive", "result": lambda r: None, "procs": lambda *a, **k: []}
            if transcript is not None:
                obs["transcript"] = transcript
            rs = {"runs": [{"state": "running", "unit": "rm-role-x-5", "at": 0, "scope": "S.scope", "marker": "M",
                            "item": "I", "budget": 450000, "mode": "alarm", "session": sid, "day": "2026-11-02"}]}
            RL._supervise_one("Operations", rs, {"run_max_s": 100, "seat": "S"}, obs, 50,
                              lambda **kw: acts.append(kw), set())
            return acts, rs["runs"][0]
        acts, run = supervise(lambda r: RL.transcript_usage(r, proj))
        done = [x for x in acts if x["do"] == "role_done"]
        check(run["state"] == "failed" and run["tokens"] == RL.run_tokens({"usage": WANT})
              and run.get("token_source") == "transcript", "T5 no result: failed, measured from transcript (%r)" % (
                  {k: run.get(k) for k in ("state", "tokens", "token_source")},))
        check(done and "from its transcript" in done[0]["why"] and "UNMEASURED" not in done[0]["why"],
              "T5 role_done says where the count came from")
        check(RL.spent_today({"runs": [run]}, 0) == run["tokens"] or run.get("day") != RL.day_of(0),
              "T5 the day's spend reads the measured tokens")
        acts, run = supervise(lambda r: None)
        check(run["tokens"] is None and "UNMEASURED (counted at its budget)" in
              [x for x in acts if x["do"] == "role_done"][0]["why"], "T5 no transcript: still UNMEASURED")
        acts, run = supervise(None)
        check(run["tokens"] is None, "T5 no transcript reader (old obs): unchanged")
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
