#!/usr/bin/env python3
"""selftest_helper_receipts.py — a dead window's helpers reach the next window (HELPER_REGISTRY_BUILD_DURABLE_RECEIPTS).

The death here is real: a child process owns a session file, writes its transcript line by line and is SIGKILLed
mid-line, so nothing of it runs after the kill. The records use the shapes MEASURED in real transcripts on 2026-11-01
(the bg Bash result text, the three notice shapes). Negatives: a live parent is never read, a helper whose notice the
parent saw is no finding, a window with no helpers leaves nothing open."""
import json
import os
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="receipts_")
os.environ["CLAUDE_CONFIG_DIR"] = os.path.join(TMP, "home")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
import doorbell  # noqa: E402
import helper_receipts as HR  # noqa: E402
import seat_restart as SR  # noqa: E402

CLONE = os.path.join(TMP, "clone")
SEAT = "BENCH"
FAILS = []
T0 = "2026-11-01T10:00:00Z"


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def tx(sid):
    return SR.transcript_path(CLONE, sid)


def write(path, recs, tail=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("".join(json.dumps(r, separators=(",", ":")) + "\n" for r in recs) + tail)


def age(path, s):
    os.utime(path, (time.time() - s, time.time() - s))


def user(text):
    return {"type": "user", "timestamp": T0, "message": {"role": "user", "content": text}}


def asst(text="ok", stop="end_turn", blocks=()):
    return {"type": "assistant", "timestamp": T0, "message": {
        "role": "assistant", "stop_reason": stop, "content": [{"type": "text", "text": text}] + list(blocks)}}


def bg_call(tu, cmd):
    return asst("", "tool_use", [{"type": "tool_use", "id": tu, "name": "Bash",
                                  "input": {"command": cmd, "run_in_background": True}}])


def bg_result(tu, tid):
    return {"type": "user", "timestamp": T0, "message": {"role": "user", "content": [{
        "type": "tool_result", "tool_use_id": tu,
        "content": "Command running in background with ID: %s. Output is being written to: /t/tasks/%s.output." % (tid, tid)}]}}


def notice(tid, status="completed"):
    return user("<task-notification>\n<task-id>%s</task-id>\n<tool-use-id>t</tool-use-id>\n<output-file>/t</output-file>\n"
                "<status>%s</status>\n<summary>s</summary>\n</task-notification>" % (tid, status))


def helper(sid, aid, recs, desc="a job", tool_use=None):
    f = os.path.join(tx(sid)[:-len(".jsonl")], "subagents", "agent-%s.jsonl" % aid)
    write(f, recs)
    with open(f[:-len(".jsonl")] + ".meta.json", "w") as m:
        json.dump({"description": desc, "toolUseId": tool_use}, m)


RUNNING = [dict(user("go"), cwd=CLONE), asst("", "tool_use", [{"type": "tool_use", "id": "x", "name": "Bash",
                                                                 "input": {"command": "pytest -k thirst"}}])]
FINISHED = [dict(user("go"), cwd=CLONE), asst("THE FINAL REPORT: all green")]

PARENT = r"""
import json, os, sys, time
session_file, path = sys.argv[1:3]
json.dump({"pid": os.getpid(), "sessionId": os.path.basename(path)[:-6]}, open(session_file, "w"))
rec = {"type": "assistant", "timestamp": "2026-11-01T10:00:00Z", "message": {"role": "assistant", "content": [
    {"type": "tool_use", "id": "b1", "name": "Bash", "input": {"command": "until done; do sleep 300; done", "run_in_background": True}}]}}
res = {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "b1",
    "content": "Command running in background with ID: bwatch. Output is being written to: /t/tasks/bwatch.output."}]}}
with open(path, "a") as f:
    f.write(json.dumps(rec, separators=(",", ":")) + "\n" + json.dumps(res, separators=(",", ":")) + "\n")
    f.flush()
    print("ready", flush=True)
    while True:                      # torn on purpose: the kill lands inside a record, as a real one can
        f.write('{"type":"assistant","message":{"content":[{"type":"text","te')
        f.flush()
        time.sleep(30)
"""


def real_kill():
    sid = "aaaa0000-kill"
    os.makedirs(os.path.dirname(tx(sid)), exist_ok=True)
    sessions = os.path.join(SR.claude_home(), "sessions")
    os.makedirs(sessions, exist_ok=True)
    helper(sid, "dead1", RUNNING, "Harden thirst rows")
    sf = os.path.join(sessions, "1.json")
    p = subprocess.Popen([sys.executable, "-c", PARENT, sf, tx(sid)], stdout=subprocess.PIPE, text=True)
    check(p.stdout.readline().strip() == "ready", "the real parent is up")

    age(tx(sid), 2 * HR.SETTLE_S)        # silent long enough: only the live pid protects it
    check(sid in HR.live_sessions(), "live parent: its session reads live")
    check(HR.collect(SEAT, CLONE) == [] and not os.path.exists(HR.receipt_path(SEAT, sid)),
          "NEGATIVE: a live parent with a running helper gets no receipt, however quiet")

    p.send_signal(signal.SIGKILL)
    p.wait()
    check(sid not in HR.live_sessions(), "SIGKILLed parent: its session no longer reads live")
    new = HR.collect(SEAT, CLONE, force=[sid])
    check(len(new) == 1, "after SIGKILL the dead window gets one receipt (%r)" % new)
    rec = new[0] if new else {"died": [], "bash": [], "unread": []}
    check([h["id"] for h in rec["died"]] == ["dead1"], "the running helper reads DIED (%r)" % rec["died"])
    check([b["id"] for b in rec["bash"]] == ["bwatch"], "the background command reads no-reader (%r)" % rec["bash"])
    check(rec["died"] and rec["died"][0]["last_cmd"] == "pytest -k thirst", "the receipt names its last command")
    check("quit or a crash" in str(rec.get("ended")), "a kill with no record reads as a crash (%r)" % rec.get("ended"))
    check(HR.collect(SEAT, CLONE, force=[sid]) == [], "read once: a second collect adds nothing")
    return sid


def scenarios():
    # finished, notice never came: the report is only in its transcript
    a = "bbbb0000-unread"
    write(tx(a), [user("hi"), asst("spawned")])
    helper(a, "rep1", FINISHED, "Sum the census")
    age(tx(a), 2 * HR.SETTLE_S)
    # notice came, but no turn after it: the parent died with the report in its queue
    b = "cccc0000-unseen"
    write(tx(b), [user("hi"), asst("spawned"), notice("rep2")])
    helper(b, "rep2", FINISHED, "Sum again")
    age(tx(b), 2 * HR.SETTLE_S)
    # the normal case, all three notice shapes: no finding
    c = "dddd0000-clean"
    enq = {"type": "queue-operation", "operation": "enqueue", "timestamp": T0,
           "content": notice("ok2")["message"]["content"]}
    deq = {"type": "queue-operation", "operation": "remove", "timestamp": T0}
    att = {"type": "attachment", "timestamp": T0, "attachment": {
        "commandMode": "task-notification", "prompt": notice("ok3")["message"]["content"]}}
    write(tx(c), [user("hi"), asst("spawned"), notice("ok1"), enq, deq, att, asst("read them")])
    for h in ("ok1", "ok2", "ok3"):
        helper(c, h, FINISHED)
    age(tx(c), 2 * HR.SETTLE_S)
    # a foreground helper: its report is its tool result
    d = "eeee0000-fg"
    write(tx(d), [user("hi"), asst("x", "tool_use"), {"type": "user", "timestamp": T0, "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "tu9", "content": "report"}]}}, asst("done")])
    helper(d, "fg1", FINISHED, tool_use="tu9")
    age(tx(d), 2 * HR.SETTLE_S)
    # /clear: no restart record, no wake, the file just stops
    e = "ffff0000-clear"
    write(tx(e), [user("hi"), asst("spawned"), {"type": "queue-operation", "operation": "enqueue", "timestamp": T0,
                                                "content": "/clear"}])
    helper(e, "clr1", RUNNING, "Rain swim burst")
    age(tx(e), 2 * HR.SETTLE_S)
    # no helpers at all: one marker, no parse, nothing open
    f = "0000aaaa-plain"
    write(tx(f), [user("hi"), asst("bye")])
    age(tx(f), 2 * HR.SETTLE_S)
    # too fresh with no live process: it may be starting; it waits for the settle
    g = "1111aaaa-fresh"
    write(tx(g), [user("hi"), asst("spawned")])
    helper(g, "fr1", RUNNING)
    # a killed window named by the restart record reads with its source
    h = "2222aaaa-goodbye"
    write(tx(h), [user("hi"), bg_call("b2", "ssh steve 'until hashes.done'"), bg_result("b2", "bgood"),
                  notice("bgood", "killed")])
    SR._write_json(SR.killed_path(SEAT), {"session_id": h, "source": "goodbye"})
    age(tx(h), 2 * HR.SETTLE_S)

    new = {r["session"]: r for r in HR.collect(SEAT, CLONE, max_reads=20)}
    check(a in new and [x["id"] for x in new[a]["unread"]] == ["rep1"], "a finished helper with no notice reads UNREAD")
    check(a in new and "THE FINAL REPORT" in new[a]["unread"][0]["report"], "the unread report itself is in the receipt")
    check(b in new and [x["id"] for x in new[b]["unread"]] == ["rep2"], "a notice with no later turn reads UNREAD")
    check(c not in new, "NEGATIVE: three read notices, no finding (%r)" % new.get(c))
    check(d not in new, "NEGATIVE: a foreground helper's tool result is its read report")
    check(e in new and new[e]["ended"] == "/clear" and [x["id"] for x in new[e]["died"]] == ["clr1"],
          "the /clear route: the helper reads DIED, the end reads /clear (%r)" % new.get(e))
    check(f not in new and SR._read_json(HR.receipt_path(SEAT, f)) == {"session": f, "empty": True},
          "NEGATIVE: no helpers, an empty marker")
    check(g not in new and not os.path.exists(HR.receipt_path(SEAT, g)), "NEGATIVE: a fresh window is not read yet")
    check(h in new and new[h]["ended"] == "restart kill (goodbye)" and [x["id"] for x in new[h]["bash"]] == ["bgood"],
          "the goodbye route: the watcher with an unseen killed notice reads no-reader (%r)" % new.get(h))
    return new, a, e


def readers(a, e):
    lines = HR.wake_lines(SEAT, CLONE)
    body = "\n".join(lines)
    for want in ("RECEIPTS from dead windows", "DIED MID-WORK clr1", "REPORT NOBODY READ rep1", "THE FINAL REPORT",
                 "BACKGROUND COMMAND WITH NO READER bwatch", "start it again", "ack --seat BENCH"):
        check(want in body, "the wake prints %r" % want)

    import dispatcher as D
    acts = []
    fn = lambda: [{"seat": SEAT, "session": e, "line": "L"}]    # noqa: E731
    D.helper_lost_alarms({"alarm_item": "ITEM"}, {"helper_receipts": fn}, lambda **k: acts.append(k))
    check([x["kind"] for x in acts] == ["helper_lost:ffff0000"] and acts[0]["conductor_log"] and acts[0]["ticket"] == "ITEM",
          "an open receipt raises one alarm to the Conductor (%r)" % acts)
    acts.clear()
    D.helper_lost_alarms({"helper_receipts": {"enabled": False}}, {"helper_receipts": fn}, lambda **k: acts.append(k))
    check(acts == [], "NEGATIVE: helper_receipts.enabled false is silent")

    def boom():
        raise OSError("no sessions dir")
    D.helper_lost_alarms({}, {"helper_receipts": boom}, lambda **k: acts.append(k))
    check([x["kind"] for x in acts] == ["helper_lost:reader"], "a failing reader alarms, it never reads as nothing lost")
    sch = {"seat_restart": {"enabled": True, "seats": {SEAT: {"clone": CLONE}}}, "seats": {SEAT: {"clone": CLONE}}}
    got = D.helper_receipts_obs(sch)
    check(SR._read_json(os.path.join(doorbell.state_dir(), "receipts", "last_read.json"))["seats"] == [SEAT],
          "a tick leaves the reading the --live promise watches")
    check(sorted(x["session"] for x in got) == sorted(r["session"] for r in HR.open_receipts(SEAT)) and len(got) >= 5,
          "the Dispatcher's reader returns every open receipt (%d)" % len(got))

    check(HR.ack(SEAT, e[:8]) == [e] and e not in [r["session"] for r in HR.open_receipts(SEAT)], "ack closes one receipt")
    HR.ack(SEAT, "all")
    check(HR.open_receipts(SEAT) == [] and HR.wake_lines(SEAT, CLONE) == [], "after ack all the wake prints nothing")
    check(D.helper_receipts_obs(sch) == [], "NEGATIVE: an acked receipt no longer alarms")


def unreadable():
    os.rename(os.path.join(SR.claude_home(), "sessions"), os.path.join(SR.claude_home(), "sessions.gone"))
    try:
        HR.live_sessions()
        check(False, "an unreadable sessions dir must raise, not read as nobody alive")
    except OSError:
        check(True, "an unreadable sessions dir raises, it never reads as nobody alive")


def main():
    os.makedirs(CLONE)
    real_kill()
    _, a, e = scenarios()
    readers(a, e)
    unreadable()
    print("FAILED %d" % len(FAILS) if FAILS else "ALL OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
