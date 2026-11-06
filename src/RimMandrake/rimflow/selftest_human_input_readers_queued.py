#!/usr/bin/env python3
"""HUMAN_INPUT_READERS_AUDIT_QUEUED_PROMPTS: every "did he type / his last message" reader sees a queued prompt.

A message the owner types WHILE a turn runs lands in the transcript ONLY as {type: attachment, attachment: {type:
queued_command, commandMode: prompt, origin: {kind: human}, prompt}} (440 of 444 never echoed as a user record,
MEASURED 2026-10-29; lesson infrastructure/state/lessons/20261029T205957Z-BENCH-queued-prompt-attachment-only.md).

Audit 2026-11-06 of every transcript reader that keeps type=user records (grep over src/ and .claude/hooks/):

  reader                                            asks "did he type?"   verdict
  seat_restart.scan_records / tx_summary / last_human / last_goodbye / human_since_offset / owed
                                                    yes                   already fixed (a64eaede64, _queued_as_user)
  .claude/hooks/block_agent_over_slots.last_typed   yes (20-min window)   covered: reads seat_restart.tx_summary
  owner_interaction.last_chat (OWNER bridge hold)   yes                   covered: tx_summary + last_human
  cli._owner_verdict                                yes                   covered: owner_interaction
  Utils/restart_reconcile.py goodbye scan           yes                   covered: seat_restart.scan_records
  helper_budget.py                                  no transcript read    n/a
  seat_restart.wake_digest (_tx_tail "what he said") yes                  FIXED here: _tx_tail maps the attachment
  slot_allocator.owner_last_window / owner_window_times (sitting, overage)
                                                    yes                   FIXED here: _is_owner_text maps it
  slot_allocator.helper_state ("work resumed")      input after the end   FIXED here: a queued_command is input
  Utils/v3_vs_v2.py owner_msgs                      yes (report)          FIXED here (not tested: a report)
  conductor_closeout, Utils/sim/friction_census     yes                   already read queued_command
  helper_checkpoint.first_prompt, token_census      the spawn brief       n/a: not his input
  raise_ladder, relentless_account, login_watch     the ending error      n/a: not his input

Each check below holds a CONTROL (the same transcript, prompt typed as a plain user record) so a blind instrument
cannot pass.
"""
import importlib.util
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import seat_restart as SR  # noqa: E402
import slot_allocator as SA  # noqa: E402

FAILS = []
NOW = time.time()
WAIT = "wait, stop before you push that"


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(t))


def recs(queued=True):
    typed = {"type": "user", "timestamp": iso(NOW - 50 * 60), "uuid": "u1", "origin": {"kind": "human"},
             "message": {"role": "user", "content": "build the thing"}}
    tool = {"type": "assistant", "timestamp": iso(NOW - 49 * 60), "uuid": "a1",
            "message": {"role": "assistant", "id": "m1", "stop_reason": "tool_use",
                        "content": [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {}}]}}
    late = (NOW - 5 * 60)
    if queued:
        wait = {"type": "attachment", "timestamp": iso(late), "uuid": "att1",
                "attachment": {"type": "queued_command", "commandMode": "prompt", "prompt": WAIT,
                               "origin": {"kind": "human"}}}
    else:
        wait = {"type": "user", "timestamp": iso(late), "uuid": "u2", "origin": {"kind": "human"},
                "message": {"role": "user", "content": WAIT}}
    end = {"type": "assistant", "timestamp": iso(NOW - 4 * 60), "uuid": "a2",
           "message": {"role": "assistant", "id": "m2", "stop_reason": "end_turn",
                       "content": [{"type": "text", "text": "stopped"}]}}
    return [typed, tool, wait, end]


def write(d, name, rs):
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with open(p, "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in rs))
    return p


def near(t, minutes):
    return t is not None and abs((NOW - t) / 60 - minutes) < 0.2


def main():
    tmp = tempfile.mkdtemp(prefix="hq_readers_")
    for queued in (False, True):
        tag = "queued attachment" if queued else "CONTROL typed user record"
        proj = os.path.join(tmp, "q" if queued else "c")
        p = write(proj, "sess.jsonl", recs(queued))

        s = SR.tx_summary(p, peers=set())
        check(near((s or {}).get("last_user_at"), 5), "%s: seat_restart.tx_summary last_user_at is the wait (%s)"
              % (tag, s and s.get("last_user_at")))
        lh = SR.last_human(p, peers=set())
        check(lh is not None and near(lh[0], 5), "%s: seat_restart.last_human is the wait" % tag)

        spec = importlib.util.spec_from_file_location(
            "baos", os.path.join(REPO, ".claude", "hooks", "block_agent_over_slots.py"))
        baos = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(baos)
        check(near(baos.last_typed({"transcript_path": p}), 5),
              "%s: block_agent_over_slots.last_typed (20-min Conductor window) is the wait" % tag)

        os.environ["RIMFLOW_OWNER_CHAT_DIRS"] = proj
        from rimflow import owner_interaction as OI
        t, prob = OI.last_chat(now=NOW)
        check(near(t, 5) and not prob, "%s: owner_interaction.last_chat (OWNER hold) is the wait (%s, %s)"
              % (tag, t, prob))

        dg = "\n".join(SR.wake_digest({"tx_path": p, "session_id": "s"}, tree=[]) or [])
        check(WAIT in dg, "%s: seat_restart.wake_digest lists the wait among what he said" % tag)

        check(near(SA.owner_last_window([proj], NOW), 5),
              "%s: slot_allocator.owner_last_window is the wait" % tag)
        ts = SA.owner_window_times([proj], NOW, 3 * 3600)
        check(len(ts) == 2 and near(ts[-1], 5), "%s: slot_allocator.owner_window_times lists both prompts (%s)"
              % (tag, ts))

    # helper_state: a follow-up delivered after the helper's end_turn exists only as a queued_command; it runs on it
    rs = recs(True)
    h = [rs[0], rs[3], dict(rs[2], timestamp=iso(NOW - 60))]
    hp = write(os.path.join(tmp, "h"), "agent-x.jsonl", h)
    rules = {"helpers": {"live_window_s": 900}}
    run, why = SA.helper_state(hp, time.time(), rules)
    check(run, "slot_allocator.helper_state: a queued follow-up after end_turn is running (%s)" % why)
    hc = write(os.path.join(tmp, "h"), "agent-y.jsonl", [rs[0], rs[3]])
    run, why = SA.helper_state(hc, time.time(), rules)
    check(not run, "slot_allocator.helper_state CONTROL: ended with nothing after is finished (%s)" % why)

    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
