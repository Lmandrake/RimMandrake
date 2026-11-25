#!/usr/bin/env python3
"""Evidence for findings.md: price each continuation's start from its transcript, in weighted_v2.
Read-only. Usage: python3 measure_pairs.py > pairs.json"""
import glob, json, os, re, sys, calendar, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "RimMandrake", "rimflow"))
import role_launch as RL
D = "/mnt/d/ClaudeWork/rimmandrake/dispatcher/detached"
P = os.path.expanduser("~/.claude/projects")
REF = RL.MODEL_PRICES[RL.REF_MODEL]["input_tokens"]
ACT = re.compile(r"\./publish|git commit|cli\.py (note|close|file|wait|verify)|lessons\.py add|waitalive\.py run|deploy_custom_mods\.py.*--apply")

def w(model, u):
    p = RL.MODEL_PRICES.get(model)
    if not p:
        return None
    cc = u.get("cache_creation") or {}
    c1h = cc.get("ephemeral_1h_input_tokens"); c5 = cc.get("ephemeral_5m_input_tokens")
    if c1h is None and c5 is None:
        c1h, c5 = 0, u.get("cache_creation_input_tokens") or 0
    v = (u.get("input_tokens", 0) * p["input_tokens"] + c5 * p["cache_write_5m"] + c1h * p["cache_write_1h"]
         + u.get("cache_read_input_tokens", 0) * p["cache_read_input_tokens"] + u.get("output_tokens", 0) * p["output_tokens"])
    return float(v / REF)

def ts(s):
    return calendar.timegm(time.strptime(s[:19], "%Y-%m-%dT%H:%M:%S"))

def requests(path, t0=None):
    """-> main-thread requests at or after t0: [{t, model, u, acts}] (one per message id)."""
    out, seen = [], {}
    with open(path, errors="replace") as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("type") != "assistant" or e.get("isSidechain"):
                continue
            m = e.get("message") or {}
            if m.get("model") == "<synthetic>":    # an error stub the CLI writes: no request was made
                continue
            if t0 and e.get("timestamp") and ts(e["timestamp"]) < t0 - 5:
                continue
            mid = m.get("id")
            if mid not in seen:
                seen[mid] = {"t": e.get("timestamp"), "model": m.get("model"), "u": m.get("usage") or {}, "act": None}
                out.append(seen[mid])
            for b in m.get("content") or []:
                if b.get("type") == "tool_use" and seen[mid]["act"] is None:
                    n, i = b.get("name"), b.get("input") or {}
                    if n in ("Edit", "Write", "NotebookEdit") or (n == "Bash" and ACT.search(i.get("command", ""))):
                        seen[mid]["act"] = n + ":" + (i.get("command") or i.get("file_path") or "")[:80]
    return out

def ctx(u):
    return sum(int(u.get(k) or 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))

def summary(reqs):
    if not reqs:
        return None
    f = reqs[0]; cum = 0.0; act = None
    for i, r in enumerate(reqs):
        cum += w(r["model"], r["u"]) or 0
        if r["act"]:
            act = {"n_req": i + 1, "w_before_act": round(cum), "act": r["act"]}
            break
    return {"model": f["model"], "first_ctx": ctx(f["u"]), "first_write": f["u"].get("cache_creation_input_tokens", 0),
            "first_read": f["u"].get("cache_read_input_tokens", 0), "first_w": round(w(f["model"], f["u"]) or 0),
            "first_act": act, "n_req": len(reqs), "w_total": round(sum(w(r["model"], r["u"]) or 0 for r in reqs)),
            "end_ctx": ctx(reqs[-1]["u"]), "first_t": f["t"],
            "act_ctx": ctx(reqs[act["n_req"] - 1]["u"]) if act else None,
            "n_after_act": len(reqs) - act["n_req"] if act else None,
            "w_read_after_act": round(sum(float(RL.MODEL_PRICES[r["model"]]["cache_read_input_tokens"] / REF)
                                          * r["u"].get("cache_read_input_tokens", 0) for r in reqs[act["n_req"]:])) if act else None}

def tpath(sid):
    h = glob.glob(os.path.join(P, "*", (sid or "x") + ".jsonl"))
    return max(h, key=os.path.getmtime) if h else None

recs = {}
for p in glob.glob(os.path.join(D, "*.json")):
    if p.endswith((".out.json", ".alive.json")):
        continue
    try:
        r = json.load(open(p)); recs[r["unit"]] = r
    except (ValueError, KeyError, OSError):
        pass
by_session = {}
for r in recs.values():
    if r.get("session"):
        by_session.setdefault(r["session"], []).append(r)
rows = []
seen_keys = set()
for r in sorted(recs.values(), key=lambda r: r["at"]):
    par = recs.get(r.get("continued_from") or "")
    kind = "resume" if r.get("resume_session") else ("fresh" if par else None)
    if kind == "resume" and not par:   # a manual resume: its parent is the run before it on the same session
        prev = [x for x in by_session.get(r["resume_session"], []) if x.get("ended") and x["at"] < r["at"]]
        par = max(prev, key=lambda x: x["at"]) if prev else None
    if not kind:
        continue
    row = {"unit": r["unit"], "item": r["item"], "kind": kind, "how": r.get("continue_how") or "manual",
           "parent": par and par["unit"], "gap_min": round((r["at"] - par["ended"]) / 60, 1) if par and par.get("ended") else None}
    pt = tpath(par.get("session")) if par else None
    if pt:
        pr = requests(pt, par["at"]) if kind == "resume" else requests(pt)
        if kind == "resume":
            pr = [x for x in pr if ts(x["t"]) <= (par.get("ended") or 1e12) + 5]
        row["parent_end_ctx"] = ctx(pr[-1]["u"]) if pr else None
        row["parent_model"] = pr[-1]["model"] if pr else None
    ct = tpath(r.get("session"))
    row["child"] = summary(requests(ct, r["at"])) if ct else None
    key = (r.get("session"), row["child"] and row["child"]["first_t"])
    if row["child"] and key in seen_keys:
        continue                       # a launch that died before its first request: the same requests, counted once
    seen_keys.add(key)
    rows.append(row)
json.dump(rows, sys.stdout, indent=1)
