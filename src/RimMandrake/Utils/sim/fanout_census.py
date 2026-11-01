#!/usr/bin/env python3
"""fanout_census.py: real data on parallel helper work, for fanout_sim.py. Item in the design doc
design/RimMandrake/fanout_sim_refit_2026-11-01.md. Offline, read-only. Three steps, each writes a file under OUT:
    fanout_census.py helpers    one row per subagent transcript (seat, start, end, ITE) -> helpers.jsonl
    fanout_census.py ledger     seat events with times from the ledger shards -> ledger.jsonl
    fanout_census.py git        non-bookkeeping commits with their files -> git.jsonl
ITE is spend_census's unit. `helpers` keys a helper to the seat by transcript path; nothing here estimates anything.
"""
import glob
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.environ.get("RM_FANOUT_OUT", "/mnt/d/ClaudeWork/rimmandrake/fanout_sim_2026-11-01")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PROJECTS = os.path.expanduser("~/.claude/projects")
BOOK = ("infrastructure/state/", "conversations/", "Transient/", "observed/")


def epoch(ts):
    return datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).timestamp()


def model_x(m):
    m = (m or "").lower()
    return 0.2 if "haiku" in m else 0.6 if "sonnet" in m else 1.0


def one_helper(path):
    start = end = None
    ite = 0.0
    ids = set()
    msgs = 0
    with open(path, errors="replace") as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            ts = r.get("timestamp")
            if ts:
                t = epoch(ts)
                start = t if start is None else min(start, t)
                end = t if end is None else max(end, t)
            m = r.get("message") or {}
            u = m.get("usage") if isinstance(m, dict) else None
            mid = m.get("id") if isinstance(m, dict) else None
            if u and mid not in ids:
                ids.add(mid)
                msgs += 1
                ite += model_x(m.get("model")) * (u.get("input_tokens", 0) + 0.1 * u.get("cache_read_input_tokens", 0)
                                                  + 1.25 * u.get("cache_creation_input_tokens", 0)
                                                  + 5 * u.get("output_tokens", 0))
    return start, end, ite, msgs


def cmd_helpers():
    rows = 0
    with open(os.path.join(OUT, "helpers.jsonl"), "w") as out:
        for fam, seat in (("-home-mandrake-rm-bench", "BENCH"), ("-home-mandrake-rm-foundry", "FOUNDRY")):
            for p in glob.glob(os.path.join(PROJECTS, fam + "*", "*", "subagents", "**", "*.jsonl"), recursive=True):
                s, e, ite, n = one_helper(p)
                if s is None:
                    continue
                out.write(json.dumps({"seat": seat, "start": s, "end": e, "ite": round(ite), "msgs": n,
                                      "session": p.split(os.sep)[-3] if "subagents" == p.split(os.sep)[-2]
                                      else p.split("subagents")[0][-37:-1]}) + "\n")
                rows += 1
    print("helpers", rows)


def cmd_ledger():
    n = 0
    keep = ("close", "implemented", "verify", "start", "claim", "file", "reclaim", "drop")
    with open(os.path.join(OUT, "ledger.jsonl"), "w") as out:
        for seat in ("BENCH", "FOUNDRY"):
            for line in open(os.path.join(REPO, "infrastructure/state/ledger/events", seat + ".jsonl"), errors="replace"):
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if r.get("event") in keep and r.get("ts"):
                    out.write(json.dumps({k: r.get(k) for k in ("seat", "event", "id", "ts", "sha", "result", "verdict",
                                                                "caused_by", "kind", "status") if r.get(k) is not None})
                              + "\n")
                    n += 1
    print("ledger", n)


def cmd_git(since="2026-10-01"):
    fmt = "--format=\x01%H\x02%P\x02%at\x02%ct\x02%s"
    txt = subprocess.run(["git", "-C", REPO, "log", "--since", since, "--name-only", fmt],
                         capture_output=True, text=True, errors="replace", timeout=500).stdout
    n = 0
    with open(os.path.join(OUT, "git.jsonl"), "w") as out:
        for chunk in txt.split("\x01")[1:]:
            head, *files = chunk.split("\n")
            sha, par, at, ct, subj = head.split("\x02", 4)
            files = [f for f in files if f and not f.startswith(BOOK)]
            if not files:                  # a bookkeeping-only commit is not in the census
                continue
            out.write(json.dumps({"sha": sha[:12], "parents": len(par.split()), "at": int(at), "ct": int(ct),
                                  "subj": subj[:120], "files": files[:200], "nfiles": len(files)}) + "\n")
            n += 1
    print("git", n)


if __name__ == "__main__":
    {"helpers": cmd_helpers, "ledger": cmd_ledger, "git": cmd_git}[sys.argv[1]]()
