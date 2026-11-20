#!/usr/bin/env python3
"""Per Conductor window transcript (~/.claude/projects/-home-mandrake-rm-bench/*.jsonl, last N days): turns, turns over
the hard context limit (seat_restart backstop_hard_tokens, 200000), their weighted_v2, the part of it that is the
context above the limit re-read (excess x the cache-read weight, plus excess x the 1 h write weight on a cache miss),
cache misses, run-end wakes (Stop hook feedback naming run_end_wake.py), and the window's orientation: weighted_v2 and
minutes before its first act (Edit/Write, a commit or publish, a rimflow write, an Agent launch).
Usage: measure_conductor.py [--days 3] [--limit 200000]"""
import glob, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measure_orientation as M
import role_launch as RL

ACT_WORDS = ("./publish", "git commit", "cli.py note", "cli.py file", "cli.py close", "rimflow note", "rimflow file",
             "rimflow close", "detached_helper.py launch")


def act(c):
    if c.get("type") != "tool_use":
        return False
    n, i = c.get("name"), c.get("input") or {}
    if n in ("Edit", "Write", "NotebookEdit", "Agent"):
        return True
    return n == "Bash" and any(w in str(i.get("command") or "") for w in ACT_WORDS)


def main():
    days = float(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 3
    lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 200000
    print("first_pst\tlast_pst\tsession\tturns\twakes\tturns_over\tweighted_total\tweighted_over\texcess_weighted"
          "\tmisses\tmiss_weighted\tpeak_ctx\tfirst_ctx\tweighted_before_first_act\tmin_before_first_act")
    for f in sorted(glob.glob(os.path.join(M.PROJ, "-home-mandrake-rm-bench", "*.jsonl")), key=os.path.getmtime):
        if time.time() - os.path.getmtime(f) > days * 86400:
            continue
        per, t0, t1, wakes, first_act = {}, None, None, 0, None
        for line in open(f, errors="replace"):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if not e.get("timestamp"):
                continue
            t = M.ts(e["timestamp"])
            t0, t1 = t0 or t, t
            if e.get("type") == "user":
                c = e["message"].get("content")
                s = c if isinstance(c, str) else json.dumps(c)
                if "Stop hook" in s[:300] and "run_end_wake" in s:
                    wakes += 1
            m = e.get("message") if e.get("type") == "assistant" else None
            if isinstance(m, dict) and isinstance(m.get("usage"), dict) and m.get("id") and m.get("model") != "<synthetic>":
                per.setdefault(m["id"], [m["usage"], m["model"], t])[:2] = [m["usage"], m["model"]]
                if first_act is None and any(act(c) for c in m.get("content") or [] if isinstance(c, dict)):
                    first_act = t
        if not per:
            continue
        tot = over_w = excess = miss_w = 0.0
        over = misses = 0
        peak = 0
        first_ctx = None
        pre = 0.0
        for u, model, t in sorted(per.values(), key=lambda x: x[2]):
            w = M.weigh(u, model)
            cw, cr = u.get("cache_creation_input_tokens") or 0, u.get("cache_read_input_tokens") or 0
            ctx = (u.get("input_tokens") or 0) + cw + cr
            first_ctx = first_ctx or ctx
            peak = max(peak, ctx)
            tot += w
            if first_act is None or t <= first_act:
                pre += w
            W = RL.model_weights(model)
            if cw > cr and ctx > 50000:
                misses += 1
                miss_w += w
            if ctx > lim:
                over += 1
                over_w += w
                ex = ctx - lim
                excess += ex * float(W["cache_read_input_tokens"]) if cr >= cw else ex * float(W["cache_write_1h"])
        print("\t".join(str(x) for x in (
            time.strftime("%m-%d %H:%M", time.localtime(t0)), time.strftime("%m-%d %H:%M", time.localtime(t1)),
            os.path.basename(f)[:8], len(per), wakes, over, round(tot), round(over_w), round(excess), misses,
            round(miss_w), peak, first_ctx, round(pre) if first_act else "NO_ACT",
            round((first_act - t0) / 60, 1) if first_act else "NO_ACT")))


if __name__ == "__main__":
    main()
