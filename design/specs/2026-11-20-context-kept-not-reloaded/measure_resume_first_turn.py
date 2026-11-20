#!/usr/bin/env python3
"""Per resumed detached run of the last N days: the first turn's cache write, cache read and weighted_v2 cost, and the
gap since the session's previous turn. A cache miss on resume (cache write ~ the whole context, read ~ the system
prompt) means the resumed run paid to reload its whole context. Usage: measure_resume_first_turn.py [--days 3]"""
import glob, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measure_orientation as M


def main():
    days = float(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 3
    print("start_pst\titem\tgap_min\tcache_write\tcache_read\tfirst_turn_weighted\tcache")
    for f in sorted(glob.glob(M.DET + "/*.json")):
        if f.endswith(".out.json"):
            continue
        try:
            d = json.load(open(f))
        except ValueError:
            continue
        at = float(d.get("at") or 0)
        if time.time() - at > days * 86400 or not d.get("resume_session"):
            continue
        tp = os.path.join(M.PROJ, M.esc(d["clone"]), d["resume_session"] + ".jsonl")
        if not os.path.exists(tp):
            print("%s\t%s\tUNMEASURED: no transcript" % (time.strftime("%m-%d %H:%M", time.localtime(at)), d["item"]))
            continue
        last_before, row = None, None
        for line in open(tp, errors="replace"):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if not e.get("timestamp"):
                continue
            t = M.ts(e["timestamp"])
            m = e.get("message") if e.get("type") == "assistant" else None
            ok = isinstance(m, dict) and isinstance(m.get("usage"), dict) and m.get("model") != "<synthetic>"
            if t < at - 60:
                if ok:
                    last_before = t
                continue
            if ok:
                u = m["usage"]
                row = (u.get("cache_creation_input_tokens") or 0, u.get("cache_read_input_tokens") or 0,
                       round(M.weigh(u, m["model"])))
                break
        if not row:
            continue
        gap = round((at - last_before) / 60) if last_before else "UNMEASURED"
        print("\t".join(str(x) for x in (time.strftime("%m-%d %H:%M", time.localtime(at)), d["item"], gap) + row
                        + ("MISS" if row[0] > row[1] else "hit",)))


if __name__ == "__main__":
    main()
