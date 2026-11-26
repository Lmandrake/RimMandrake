#!/usr/bin/env python3
"""Count spawns refused slots_full by a reservation that a spawn refused for its agent type left behind.

    python3 src/RimMandrake/Utils/refused_spawn_slot_holds.py START END [--root ~/.claude/projects]   UTC dates YYYY-MM-DD, by file mtime and record ts

An event: in one session transcript, an Agent tool result says 'runs on an unbounded context' (block_unbounded_agent.py
refused it), and a later Agent tool result within 180 s says slots_full / 'helper(s) running' with 'reserved-' in its
Running list. Prints sessions read, unbounded refusals seen, events. Exit 2 if no transcript could be read.
Made by Crystallize 2026W48: the criterion of its adopted change (commit aec65b3540) is 0 events in 2026-11-26..12-09
with at least 1 refusal seen; baseline 80 events and 171 refusals in 2026-11-12..25. selftest_crystallize_instruments.py.
"""
import glob, json, os, sys, datetime as DT
start, end = sys.argv[1], sys.argv[2]
root = os.path.expanduser(sys.argv[sys.argv.index("--root") + 1]) if "--root" in sys.argv else os.path.expanduser("~/.claude/projects")
def ts(s):
    try: return DT.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception: return None
files = [p for p in glob.glob(root + "/**/*.jsonl", recursive=True)]
UTC = DT.timezone.utc   # START and END are UTC days, as the transcript stamps are
lo = DT.datetime.fromisoformat(start).replace(tzinfo=UTC).timestamp(); hi = DT.datetime.fromisoformat(end).replace(tzinfo=UTC).timestamp() + 86400
read = refused = events = 0; where = []
for p in files:
    try:
        if os.path.getmtime(p) < lo: continue
        last_refused = None; any_rec = False
        with open(p, errors="replace") as f:
            for line in f:
                if "tool_result" not in line: continue
                try: r = json.loads(line)
                except ValueError: continue
                t = ts(r.get("timestamp") or "")
                if t is None or not (lo <= t < hi): continue
                any_rec = True
                txt = line
                if "runs on an unbounded context" in txt:
                    refused += 1; last_refused = t
                elif ("slots_full" in txt or "helper(s) running" in txt) and "reserved-" in txt and last_refused and t - last_refused <= 180:
                    events += 1; where.append(os.path.basename(p))
        read += any_rec
    except OSError:
        continue
if not read:
    print("COULD NOT LOOK: no transcript with records in %s..%s under %s" % (start, end, root)); sys.exit(2)
print("%s..%s: %d transcripts read, %d unbounded-type refusals, %d slots_full by a left reservation %s" % (start, end, read, refused, events, sorted(set(where))[:5]))
