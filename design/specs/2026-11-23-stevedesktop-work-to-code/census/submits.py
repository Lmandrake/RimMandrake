#!/usr/bin/env python3
"""submits.py - every `testq.py submit` an agent ran on this machine in the window, with the result text: accepted, refused
(by which words), --help, or text that only names it. Reads the Claude transcripts."""
import collections, glob, json, os, re
from common import START, END
P = os.path.expanduser("~/.claude/projects")
run = re.compile(r"(^|[;&|\n]\s*|\bdo\s+|&&\s*|\$\(|=\s*)(timeout \d+ )?python3 \S*testq\.py submit([^\n;|&]*)")
R = []; seen = set()
for f in glob.glob(P + "/*/*.jsonl") + glob.glob(P + "/*/*/subagents/*.jsonl"):
    if os.path.getmtime(f) < START.timestamp() or "STUDY-STEVEDESKTOP-WORK-SETUP" in f: continue
    calls = {}
    for l in open(f, errors="replace"):
        if "testq.py submit" not in l and not (calls and "tool_result" in l): continue
        try: d = json.loads(l)
        except ValueError: continue
        if not START.isoformat()[:19] <= (d.get("timestamp") or "")[:19] <= END.isoformat()[:19]: continue
        c = (d.get("message") or {}).get("content")
        if not isinstance(c, list): continue
        for x in c:
            if x.get("type") == "tool_use" and x.get("name") == "Bash":
                cmd = (x.get("input") or {}).get("command") or ""
                m = run.search(cmd)
                if m and x["id"] not in seen: calls[x["id"]] = (d["timestamp"], cmd, m.group(3)); seen.add(x["id"])
            elif x.get("type") == "tool_result" and x.get("tool_use_id") in calls:
                t, cmd, args = calls.pop(x["tool_use_id"]); r = x.get("content")
                r = r if isinstance(r, str) else " ".join(y.get("text", "") for y in r or [] if isinstance(y, dict))
                R.append((t, args, r, f, cmd))
C = collections.Counter(); ex = collections.defaultdict(list)
for t, a, r, f, cmd in sorted(R):
    if "--help" in a or "-h " in a + " ": k = "help text"
    elif re.search(r"\bJ2026\d{4}T\d{6}Z-[0-9a-f]{6}\b", r): k = "accepted"
    elif "dry" in a: k = "dry"
    else: k = "refused or no job id"
    C[k] += 1; ex[k].append((t[:16], a.strip()[:150], r.strip()[-330:].replace("\n", " / ")))
print("submit calls", len(R), dict(C))
for k in ("refused or no job id",):
    for e in ex[k]: print("  ", e)
