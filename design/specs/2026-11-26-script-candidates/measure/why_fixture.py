#!/usr/bin/env python3
"""why_fixture.py <home>: a fake Conductor transcript with one hand read per MECH class of why_sample.py (9 reads).
Test: HOME=<home> SCAN_DAYS=9 SCAN_DIR=<d> python3 -I extract.py; HOME=<home> SCAN_DIR=<d> python3 -I why_sample.py --n 9
must print one read of each class, read_again twice, wake_without_result twice."""
import json, os, sys
home = sys.argv[1]
d = os.path.join(home, ".claude/projects/-home-mandrake-rm-bench"); os.makedirs(d, exist_ok=True)
rows = [{"type": "agent-name", "agentName": "CONDUCTOR"}]
n = [0]
def ts(day, mm): return "2026-11-%02dT%02d:%02d:00.000Z" % (day, 10 + mm // 60, mm % 60)
def turn(day, mm, text, origin="human"):
    rows.append({"type": "user", "timestamp": ts(day, mm), "promptId": "p%d" % len(rows), "turnOrigin": origin,
                 "message": {"content": text}})
def say(day, mm, text):
    rows.append({"type": "assistant", "timestamp": ts(day, mm), "message": {"content": [{"type": "text", "text": text}]}})
def call(day, mm, cmd):
    n[0] += 1; i = "t%d" % n[0]
    rows.append({"type": "assistant", "timestamp": ts(day, mm), "message": {"content": [{"type": "tool_use", "id": i, "name": "Bash", "input": {"command": cmd}}]}})
    rows.append({"type": "user", "timestamp": ts(day, mm + 1), "message": {"content": [{"type": "tool_result", "tool_use_id": i, "content": "ok"}]}})
def rd(unit, extra=""):
    return "python3 -c \"import json; o=json.load(open('/mnt/d/ClaudeWork/rimmandrake/dispatcher/detached/%s.out.json')); print(o['result']%s)\"" % (unit, extra)
OLD = "Stop hook feedback:\n[run_end_wake] [RimFlow] 1 detached run(s) ended (run_end_wake.py): read each result, act on it\n- %s ended success; item X; full result: /p/%s.out.json"
NEW = "Stop hook feedback:\n[run_end_wake] [RimFlow] 1 detached run(s) ended (run_end_wake.py): each run's whole last message is below\n== THE OTHER 1\n----- %s ended success at 1:00 PM; item X; result file: /p/%s.out.json\nits whole last message:\nDone.\n----- end of %s"
# 1 old wake -> wake_without_result
turn(22, 0, OLD % ("u-old", "u-old"), "stop_hook"); say(22, 1, "Reading the result."); call(22, 2, rd("u-old"))
# 2 human turn -> not_after_wake
turn(25, 0, "what did u-new say?"); call(25, 2, rd("u-new"))
# 3 new wake, same unit -> read_again
turn(25, 10, NEW % ("u-a", "u-a", "u-a"), "stop_hook"); say(25, 11, "Check the claim."); call(25, 12, rd("u-a"))
# 4 new wake, cost read -> extra_fields
turn(25, 20, NEW % ("u-b", "u-b", "u-b"), "stop_hook"); call(25, 22, rd("u-b", ", o['total_cost_usd'], o['num_turns']"))
# 5 new wake, other unit -> other_run
turn(25, 30, NEW % ("u-c", "u-c", "u-c"), "stop_hook"); call(25, 32, rd("u-zzz"))
# 6 new wake, compaction, then read -> after_compaction
turn(25, 40, NEW % ("u-d", "u-d", "u-d"), "stop_hook"); rows.append({"type": "system", "subtype": "compact_boundary", "timestamp": ts(25, 41)}); call(25, 42, rd("u-d"))
# 7 new wake, earlier-carried unit u-a read -> read_again (carried by an earlier wake)
turn(25, 50, NEW % ("u-e", "u-e", "u-e"), "stop_hook"); call(25, 52, rd("u-a"))
# 8 glob -> unknown_unit
turn(25, 60, NEW % ("u-f", "u-f", "u-f"), "stop_hook"); call(25, 62, "python3 -c \"import json,glob; [print(json.load(open(f))['result']) for f in glob.glob('/x/*.out.json')]\"")
# 9 human turn, then an old wake queued mid-turn as an attachment -> wake_without_result (seen live: 2c5e1f2d line 666)
turn(22, 10, "how did the cleanup go?"); call(22, 12, "ls")
rows.append({"type": "attachment", "timestamp": ts(22, 14), "attachment": {"type": "queued_command", "prompt": OLD % ("u-q", "u-q")}})
call(22, 15, rd("u-q"))
with open(os.path.join(d, "aaaaaaaa-0000-0000-0000-000000000000.jsonl"), "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
