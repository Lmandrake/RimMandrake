#!/usr/bin/env python3
"""Per continuation run (record field continued_from) of the last N days: the gap from its predecessor's end, the
predecessor's last context size (cache read + write + input of its last turn), the continuation's own weighted_v2 and
minutes before its first edit (runs_orientation.tsv's measure), and what a warm --resume would have paid on turn one
(the predecessor's context at the cache-read weight, when the gap is under the 1 h cache TTL; else a full rewrite at
the 1 h cache-write weight). Usage: measure_continue_gap.py [--days 3]"""
import glob, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measure_orientation as M
import role_launch as RL


def last_ctx(tp, lo, hi):
    ctx = None
    for line in open(tp, errors="replace"):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if not e.get("timestamp"):
            continue
        t = M.ts(e["timestamp"])
        if t < lo or t > hi:
            continue
        m = e.get("message") if e.get("type") == "assistant" else None
        if isinstance(m, dict) and isinstance(m.get("usage"), dict) and m.get("model") != "<synthetic>":
            u = m["usage"]
            ctx = ((u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0)
                   + (u.get("cache_creation_input_tokens") or 0), m["model"])
    return ctx


def tpath(d):
    s = d.get("session") or d.get("resume_session")
    if not s:
        try:
            o = json.load(open(d.get("out") or ""))
            s = (o[-1] if isinstance(o, list) else o).get("session_id")
        except (OSError, ValueError, AttributeError, IndexError):
            s = None
    p = os.path.join(M.PROJ, M.esc(d.get("clone") or ""), "%s.jsonl" % s) if s else None
    return p if p and os.path.exists(p) else None


def main():
    days = float(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 3
    recs = {}
    for f in glob.glob(M.DET + "/*.json"):
        if f.endswith(".out.json"):
            continue
        try:
            d = json.load(open(f))
        except ValueError:
            continue
        recs[d.get("unit")] = d
    pre = {}
    for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs_orientation.tsv")):
        c = line.rstrip("\n").split("\t")
        pre[(c[0], c[1])] = (c[7], c[8])
    print("start_pst\titem\tkind\tgap_min\tpred_context\tfresh_weighted_before_first_edit\tfresh_min_before_first_edit"
          "\twarm_resume_turn_one_weighted")
    for d in sorted(recs.values(), key=lambda d: float(d.get("at") or 0)):
        at = float(d.get("at") or 0)
        if time.time() - at > days * 86400 or not d.get("continued_from"):
            continue
        p = recs.get(d["continued_from"]) or {}
        gap = (at - float(p["ended"])) / 60 if isinstance(p.get("ended"), (int, float)) else None
        tp = tpath(p)
        ctx = last_ctx(tp, float(p.get("at") or 0) - 60, float(p.get("ended") or 9e12) + 60) if tp else None
        warm = "UNMEASURED"
        if ctx and gap is not None:
            W = RL.model_weights(ctx[1])
            warm = round(ctx[0] * float(W["cache_read_input_tokens"] if gap < 60 else W["cache_write_1h"]))
        st = time.strftime("%m-%d %H:%M", time.localtime(at))
        f, m = pre.get((st, d["item"]), ("UNMEASURED", "UNMEASURED"))
        kind = "cap" if int(d.get("cap_continues_used") or 0) > int(p.get("cap_continues_used") or 0) else (
            d.get("continue_kind") or ("lane" if d["item"] != p.get("item") else "left_open"))
        print("\t".join(str(x) for x in (st, d["item"], kind, "UNMEASURED" if gap is None else round(gap, 1),
                                         ctx[0] if ctx else "UNMEASURED", f, m, warm)))


if __name__ == "__main__":
    main()
