#!/usr/bin/env python3
"""Per detached run of the last N days: its weighted_v2 tokens and wall minutes BEFORE its first file edit (the
first Edit/Write/NotebookEdit tool call, or the first Bash call that commits or publishes), from its transcript.
That is the run's orientation: reading the brief, the item, the code and the evidence the run before it already held.
Usage: measure_orientation.py [--days 3] > rows.tsv   (UNMEASURED: no transcript; NO_EDIT: the run never edited)"""
import glob, json, os, sys, time
from datetime import datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "src", "RimMandrake", "rimflow"))
import role_launch as RL

DET = "/mnt/d/ClaudeWork/rimmandrake/dispatcher/detached"
PROJ = os.path.expanduser("~/.claude/projects")


def esc(p):
    return "".join(c if c.isalnum() else "-" for c in p)


def ts(s):
    return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()


def weigh(u, model):
    cw = u.get("cache_creation_input_tokens") or 0
    cc = u.get("cache_creation") or {}
    w5, w1 = RL._split(cw, cc.get("ephemeral_5m_input_tokens"), cc.get("ephemeral_1h_input_tokens"))
    return float(RL._weigh(model, u.get("input_tokens") or 0, w5, w1, u.get("cache_read_input_tokens") or 0,
                           u.get("output_tokens") or 0))


def first_ts(path):
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("timestamp"):
            return ts(e["timestamp"])
    return -1e12


def edit_call(c):
    if c.get("type") != "tool_use":
        return False
    n, i = c.get("name"), c.get("input") or {}
    if n in ("Edit", "Write", "NotebookEdit"):
        return True
    cmd = str(i.get("command") or "") if n == "Bash" else ""
    return "./publish" in cmd or "git commit" in cmd


def measure(path, lo=None, hi=None):
    """Only the turns inside [lo, hi] (a resumed session's file also holds the runs before and after it)."""
    per, first_edit, t0 = {}, None, None
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if not e.get("timestamp"):
            continue
        at = ts(e["timestamp"])
        if (lo is not None and at < lo) or (hi is not None and at > hi):
            continue
        if t0 is None:
            t0 = at
        m = e.get("message") if e.get("type") == "assistant" else None
        if not isinstance(m, dict) or not m.get("id"):
            continue
        if isinstance(m.get("usage"), dict):
            per.setdefault(m["id"], [None, None, None])[:2] = [m["usage"], m.get("model")]
            if per[m["id"]][2] is None:
                per[m["id"]][2] = ts(e["timestamp"])
        if first_edit is None and any(edit_call(c) for c in m.get("content") or [] if isinstance(c, dict)):
            first_edit = (m["id"], ts(e["timestamp"]))
    if not per:
        return None
    tot = pre = 0.0
    for mid, (u, model, at) in per.items():
        w = weigh(u, model) if model and model != "<synthetic>" else 0.0
        tot += w
        if first_edit is None or at < first_edit[1] or mid == first_edit[0]:
            pre += w
    return tot, (pre if first_edit else None), ((first_edit[1] - t0) / 60 if first_edit else None)


def main():
    days = float(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 3
    now = time.time()
    print("start_pst\titem\tmodel\tresult\twall_min\trecord_weighted\ttranscript_weighted\tweighted_before_first_edit\tmin_before_first_edit"
          "\tresumed\tcontinued_from")
    for f in sorted(glob.glob(os.path.join(DET, "*.json"))):
        if f.endswith(".out.json"):
            continue
        try:
            d = json.load(open(f))
        except ValueError:
            continue
        at = float(d.get("at") or 0)
        if now - at > days * 86400:
            continue
        wall = (float(d["ended"]) - at) / 60 if isinstance(d.get("ended"), (int, float)) else None
        sess = d.get("session")
        if not sess:
            try:
                o = json.load(open(d.get("out") or ""))
                sess = (o[-1] if isinstance(o, list) else o).get("session_id")
            except (OSError, ValueError, AttributeError, IndexError):
                sess = None
        tp = os.path.join(PROJ, esc(d.get("clone") or ""), "%s.jsonl" % sess) if sess else None
        if not (tp and os.path.exists(tp)):
            # one transcript per run's clone dir, by start time: the jsonl opened within 10 min of the launch
            cands = [c for c in glob.glob(os.path.join(PROJ, esc(d.get("clone") or ""), "*.jsonl"))
                     if 0 <= os.path.getctime(c) - at < 86400]
            cands = [c for c in cands if abs(first_ts(c) - at) < 600]
            tp = cands[0] if len(cands) == 1 else None
        r = measure(tp, at - 60, (float(d["ended"]) + 60) if isinstance(d.get("ended"), (int, float)) else None) if tp and os.path.exists(tp) else None
        if r is None:
            tot = pre = mins = "UNMEASURED"
        else:
            tot, pre, mins = round(r[0]), ("NO_EDIT" if r[1] is None else round(r[1])), (
                "NO_EDIT" if r[2] is None else round(r[2], 1))
        print("\t".join(str(x) for x in (time.strftime("%m-%d %H:%M", time.localtime(at)), d.get("item"),
                                         d.get("model"), d.get("result"), "" if wall is None else round(wall, 1),
                                         d.get("tokens"), tot, pre, mins, "Y" if d.get("resume_session") else "",
                                         d.get("continued_from") or "")))


if __name__ == "__main__":
    main()
