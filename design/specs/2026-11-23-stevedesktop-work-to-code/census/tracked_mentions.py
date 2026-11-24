#!/usr/bin/env python3
"""tracked.py - for each job a person-or-agent asked for (not the filler): where is its job id written?
Looks in: the ledger event shards (by seat), item prose, design/ (visit folders), git commit messages, and the Claude
transcripts of THIS machine after the job finished. A job id found nowhere = no record that its result was read."""
import collections, glob, json, os, re, subprocess, sys
from common import records
ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
R, _ = records(("done", "quarantined"))
J = {d["job"]["id"]: d for d in R if "filler" not in str(d["job"]["requested_by"])}
pat = re.compile(r"J2026\d{4}T\d{6}Z-[0-9a-f]{6}")
where = collections.defaultdict(lambda: collections.defaultdict(int))
for f in glob.glob(ROOT + "/infrastructure/state/ledger/events/*.jsonl") + glob.glob(ROOT + "/infrastructure/state/ledger/events/**/*.jsonl"):
    for l in open(f, errors="replace"):
        for j in set(pat.findall(l)):
            if j in J: where[j]["ledger:" + os.path.basename(f)[:-6]] += 1
for base in ("infrastructure/state/items", "design", "infrastructure/state/lessons", "infrastructure/state/facts"):
    for dp, dn, fn in os.walk(os.path.join(ROOT, base)):
        for n in fn:
            if n.endswith((".md", ".json", ".jsonl", ".csv")):
                try: t = open(os.path.join(dp, n), errors="replace").read()
                except OSError: continue
                for j in set(pat.findall(t)):
                    if j in J: where[j][base.split("/")[-1]] += 1
for j in set(pat.findall(subprocess.run(["git", "-C", ROOT, "log", "--since=2026-11-02", "--format=%B"], capture_output=True, text=True).stdout)):
    if j in J: where[j]["git"] += 1
n = 0
for f in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")) + glob.glob(os.path.expanduser("~/.claude/projects/*/*/subagents/*.jsonl")):
    if os.path.getmtime(f) < 1793600000 or "STUDY-STEVEDESKTOP-WORK-SETUP" in f: continue
    n += 1
    with open(f, errors="replace") as fh:
        for l in fh:
            if "J2026" not in l: continue
            try: t = json.loads(l).get("timestamp") or ""
            except ValueError: t = ""
            for j in set(pat.findall(l)):
                d = J.get(j)
                if d and t and t[:19] >= d["_fin"].strftime("%Y-%m-%dT%H:%M:%S"):
                    where[j]["transcript_after_finish"] += 1
print("jobs not filler:", len(J), "transcripts read:", n)
C = collections.Counter()
rows = []
for j, d in J.items():
    w = where[j]
    led = [k for k in w if k.startswith("ledger:")]
    human = any(k != "ledger:RUNNER" for k in led)
    kind = "proofs" if d["job"]["selector"].get("proofs") else "visit" if d["job"]["requested_by"] == "BENCH.visit" else "modcheck"
    cls = ("ledger by a seat" if human else "ledger by RUNNER program only" if led else "docs/items/git only" if any(k in w for k in ("items", "design", "lessons", "facts", "git")) else "transcript only" if w.get("transcript_after_finish") else "nowhere")
    C[(d["_state"], kind, cls, bool(w.get("transcript_after_finish")))] += 1
    rows.append((j, d["_state"], kind, cls, d["result"]["outcome"], d["job"]["requested_by"], d["job"]["mod"], d["job"].get("item")))
for k, v in sorted(C.items()): print(v, k)

for r in rows:
    if r[3] == "nowhere" or (r[3] == "transcript only"): print(r)
