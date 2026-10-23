#!/usr/bin/env python3
"""Token census of Claude Code transcripts: who burned what, and why.

Reads ~/.claude/projects/*/ transcripts (main sessions and subagents), dedupes by message
id, and reports totals by project, main vs subagent, model, hour, the top helpers (calls,
peak context, opening brief), base context at a helper's first call, and what compaction
at a given window would have saved. Built 2026-10-23 when one morning cost 2.18B tokens
(Transient/token_burn_20261023/).

    python3 src/RimMandrake/Utils/token_census.py --since 2026-10-23T07:00 > out.txt
"""
import argparse, collections, glob, json, os

ROOT = os.path.expanduser("~/.claude/projects")


def bucket(proj):
    if "art-eval" in proj: return "art-eval claude -p"
    if proj.endswith("rm-bench"): return "bench"
    if proj.endswith("rm-foundry"): return "foundry"
    return proj


def load(since):
    calls, agents = [], []
    for f in glob.glob(ROOT + "/**/*.jsonl", recursive=True):
        proj = f[len(ROOT) + 1:].split("/")[0]
        sub = "/subagents/" in f
        seen, ctx, brief = set(), [], None
        for line in open(f, errors="ignore"):
            try: d = json.loads(line)
            except ValueError: continue
            if brief is None and d.get("type") == "user":
                c = d["message"]["content"]
                brief = (c if isinstance(c, str) else " ".join(x.get("text", "") for x in c if isinstance(x, dict)))[:100].replace("\n", " ")
            if d.get("type") != "assistant" or d.get("timestamp", "") < since: continue
            m = d.get("message", {}); key = (m.get("id"), d.get("requestId"))
            if key in seen: continue
            seen.add(key); u = m.get("usage") or {}
            row = dict(proj=bucket(proj), sub=sub, model=m.get("model", "?"), hour=d["timestamp"][:13],
                       inp=u.get("input_tokens", 0), cw=u.get("cache_creation_input_tokens", 0),
                       cr=u.get("cache_read_input_tokens", 0), out=u.get("output_tokens", 0))
            calls.append(row); ctx.append(row["inp"] + row["cw"] + row["cr"])
        if sub and ctx and proj.startswith("-home-mandrake-rm-"):
            agents.append(dict(proj=bucket(proj), ctx=ctx, brief=brief or "", model=calls[-1]["model"]))
    return calls, agents


def table(calls, keyf, title, n=15):
    a = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
    for r in calls:
        x = a[keyf(r)]; x[0] += r["inp"]; x[1] += r["cw"]; x[2] += r["cr"]; x[3] += r["out"]; x[4] += 1
    tot = sum(sum(v[:4]) for v in a.values()) or 1
    print(f"\n## {title} (total {tot/1e6:.1f}M tokens, {len(calls)} calls)")
    for k, v in sorted(a.items(), key=lambda kv: -sum(kv[1][:4]))[:n]:
        print(f"  {str(k)[:50]:50} calls={v[4]:6} cwrite={v[1]/1e6:6.1f}M cread={v[2]/1e6:7.1f}M out={v[3]/1e3:6.0f}k {100*sum(v[:4])/tot:5.1f}%")


def simulate(agents, window, keep=25000):
    tot = 0
    for a in agents:
        base, off = a["ctx"][0], 0
        for x in a["ctx"]:
            g = x - off
            if g > window: off = x - (base + keep); g = base + keep
            tot += g
    return tot


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since", required=True, help="UTC ISO stamp, e.g. 2026-10-23T07:00")
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()
    calls, agents = load(args.since)
    table(calls, lambda r: r["proj"], "by project")
    table(calls, lambda r: (r["proj"], "sub" if r["sub"] else "main"), "main vs subagent")
    table(calls, lambda r: r["model"], "by model")
    table(calls, lambda r: r["hour"], "by UTC hour", 24)
    actual = sum(sum(a["ctx"]) for a in agents) or 1
    bases = sorted(a["ctx"][0] for a in agents)
    print(f"\n## helpers: {len(agents)}; context re-read {actual/1e6:.0f}M; base at first call median {bases[len(bases)//2]//1000}k" if bases else "\n## no helpers")
    print(f"  base re-read alone {sum(len(a['ctx'])*a['ctx'][0] for a in agents)/1e6:.0f}M")
    for w in (400000, 200000, 150000, 100000):
        print(f"  compaction at {w//1000}k would have cost {simulate(agents, w)/1e6:.0f}M ({100*(1-simulate(agents, w)/actual):.0f}% less)")
    print("\n## top helpers")
    for a in sorted(agents, key=lambda a: -sum(a["ctx"]))[:args.top]:
        print(f"  {sum(a['ctx'])/1e6:5.0f}M {a['proj']:8} {a['model'][7:13]:6} calls={len(a['ctx']):3} peak={max(a['ctx'])//1000}k | {a['brief']}")


if __name__ == "__main__":
    main()
