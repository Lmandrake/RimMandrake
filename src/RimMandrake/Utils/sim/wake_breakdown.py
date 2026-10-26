#!/usr/bin/env python3
"""Measure a BENCH session's first-API-call context: usage of first turns in transcripts,
and sizes (chars/4, labelled) of the static sources. Usage: wake_breakdown.py [N]"""
import glob, json, os, sys
D = os.path.expanduser("~/.claude/projects/-home-mandrake-rm-bench")
def first_usage(p):
    """first assistant usage + the first 3 attachment/user records' kinds and sizes"""
    recs = []
    with open(p) as f:
        for i, l in enumerate(f):
            try: r = json.loads(l)
            except Exception: continue
            recs.append(r)
            if r.get("type") == "assistant" and r.get("message", {}).get("usage"):
                u = r["message"]["usage"]
                return u, recs
            if i > 80: break
    return None, recs
def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    fs = sorted(glob.glob(D + "/*.jsonl"), key=os.path.getmtime)[-n:]
    for p in fs:
        u, recs = first_usage(p)
        if not u: continue
        kinds = {}
        for r in recs:
            k = r.get("type"); a = r.get("attachment", {}).get("type") if k == "attachment" else None
            kinds[(k, a)] = kinds.get((k, a), 0) + len(json.dumps(r))
        print(os.path.basename(p)[:8], "in=%s cr=%s cw=%s" % (u.get("input_tokens"), u.get("cache_read_input_tokens"), u.get("cache_creation_input_tokens")))
        for k, v in sorted(kinds.items(), key=lambda x: -x[1])[:5]:
            print("    ", k, v // 4, "tok~")
    for f in ["~/.claude/CLAUDE.md", "CLAUDE.md"]:
        t = os.path.expanduser(f); print(f, os.path.getsize(t) // 4, "tok~ (chars/4)")
if __name__ == "__main__": main()
