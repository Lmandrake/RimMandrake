#!/usr/bin/env python3
"""Token-spend census across every Claude Code transcript on this machine (offline, no model calls).

Answers "does the orchestrator's context strategy even matter?" by measuring the denominator:
total spend per day over the last DAYS days, split by project family and by role
(orchestrator top-level / subagent / headless run), plus compaction events and subagent levers.

Cost unit: Opus-input-token equivalents (ITE). Per call:
  ITE = MODEL_X[model] * (input + 0.1*cache_read + 1.25*write_5m + 2*write_1h + 5*output)
MODEL_X is an ASSUMPTION (relative list prices Opus 1 : Sonnet 0.6 : Haiku 0.2), labelled as such.
Every API call is counted once (deduped by message id across files); sidechain copies inside a
parent transcript are skipped because the subagent's own file carries them.

Writes OUT_DIR/spend_census.json; prints a short summary.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime

PROJECTS = os.path.expanduser("~/.claude/projects")
OUT_DIR = "/mnt/d/ClaudeWork/rimmandrake/perpetual_ctx"
DAYS = 7
MODEL_X = {"opus": 1.0, "sonnet": 0.6, "haiku": 0.2}   # ASSUMPTION: relative list prices
PRICE_IN_PER_MTOK = 5.0                                # ASSUMPTION: Opus-class input $/MTok, display only
READ_RE = re.compile(r'"file_path":\s*"([^"]+)"')


def family(proj: str) -> str:
    if proj == "-home-mandrake-rm-bench":
        return "BENCH"
    if proj.startswith("-home-mandrake-rm-foundry"):
        return "FOUNDRY"
    for key, name in (("art-eval-runs", "art-eval headless runs"), ("fw-art-geometry", "fw-art-geometry runs"),
                      ("seat-tmp", "seat-tmp headless runs"), ("Hestia", "Hestia"), ("EMERGENCY", "EMERGENCY"),
                      ("Lodestar", "Lodestar"), ("pulse", "pulse"), ("testq", "testq"), ("ClaudeWork", "other ClaudeWork runs")):
        if key.lower() in proj.lower():
            return name
    return "other: " + proj[:40]


def model_x(model: str) -> float:
    m = (model or "").lower()
    for k, v in MODEL_X.items():
        if k in m:
            return v
    return 1.0


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def scan_file(path, cutoff, seen):
    """Yield per-call dicts and compaction events for one transcript."""
    calls, compacts, reads = [], [], []
    res_size = {}            # tool_use_id -> tool_result tokens (chars/4)
    last_t = None
    pending_compact = None
    for line in open(path, errors="replace"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        t = d.get("type")
        if t == "system" and d.get("subtype") == "compact_boundary":
            md = d.get("compactMetadata") or {}
            pending_compact = {"t": ts(d["timestamp"]) if d.get("timestamp") else None,
                               "pre": md.get("preTokens"), "trigger": md.get("trigger"),
                               "last_call_t": last_t, "call_index": len(calls), "summary_tok": 0}
            compacts.append(pending_compact)
            continue
        if t == "user" and d.get("isCompactSummary") and pending_compact is not None:
            c = d.get("message", {}).get("content")
            pending_compact["summary_tok"] = len(c if isinstance(c, str) else json.dumps(c)) / 4
            continue
        if t == "user" and isinstance(d.get("message", {}).get("content"), list):
            for b in d["message"]["content"]:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    c = b.get("content")
                    res_size[b.get("tool_use_id")] = len(c if isinstance(c, str) else json.dumps(c)) / 4
            continue
        if t != "assistant" or d.get("isSidechain") and "/subagents/" not in path:
            continue
        m = d.get("message", {})
        for c in m.get("content") or []:
            if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "Read":
                fp = (c.get("input") or {}).get("file_path")
                if fp:
                    reads.append((len(calls), fp, c.get("id")))
        u = m.get("usage")
        mid = m.get("id")
        if not u or not d.get("timestamp") or mid in seen:
            continue
        seen.add(mid)
        t0 = ts(d["timestamp"])
        cc = u.get("cache_creation") or {}
        c5 = cc.get("ephemeral_5m_input_tokens")
        c1 = cc.get("ephemeral_1h_input_tokens")
        ccall = u.get("cache_creation_input_tokens") or 0
        if c5 is None and c1 is None:
            c5, c1 = ccall, 0
        c5, c1 = c5 or 0, c1 or 0
        cr = u.get("cache_read_input_tokens") or 0
        it = u.get("input_tokens") or 0
        out = u.get("output_tokens") or 0
        x = model_x(m.get("model"))
        calls.append({"t": t0, "gap": (t0 - last_t) if last_t else None, "model": m.get("model") or "?",
                      "ctx": it + cr + c5 + c1, "cr": cr, "cw": c5 + c1, "out": out,
                      "raw": it + cr + c5 + c1 + out,
                      "ite": x * (it + 0.1 * cr + 1.25 * c5 + 2.0 * c1 + 5.0 * out),
                      "ite_write": x * (1.25 * c5 + 2.0 * c1), "in_window": t0 >= cutoff, "c5": c5, "c1": c1, "x": x,
                      "ep": d.get("entrypoint")})
        last_t = t0
    return calls, compacts, reads, res_size


def main():
    now = time.time()
    cutoff = now - DAYS * 86400
    seen = set()
    fam = defaultdict(lambda: defaultdict(float))
    model_mix = defaultdict(float)
    sub_rows, compact_rows = [], []
    total = defaultdict(float)
    reread_all = [0, 0]
    for root, _dirs, files in os.walk(PROJECTS):
        for f in files:
            if not f.endswith(".jsonl"):
                continue
            p = os.path.join(root, f)
            if os.path.getmtime(p) < cutoff:
                continue
            proj = os.path.relpath(p, PROJECTS).split(os.sep)[0]
            fname = family(proj)
            is_sub = "/subagents/" in p
            try:
                calls, compacts, reads, res_size = scan_file(p, cutoff, seen)
            except Exception as e:  # unreadable file: count it, never hide it
                total["unreadable_files"] += 1
                print("unreadable", p, e, file=sys.stderr)
                continue
            win = [c for c in calls if c["in_window"]]
            if not win:
                continue
            headless = all(c["ep"] in ("sdk-cli", "sdk-py", "sdk-ts") for c in win)
            role = "subagent" if is_sub else ("headless" if headless else "top-level")
            key = f"{fname} / {role}"
            ite = sum(c["ite"] for c in win)
            fam[key]["ite"] += ite
            fam[key]["raw"] += sum(c["raw"] for c in win)
            fam[key]["calls"] += len(win)
            fam[key]["files"] += 1
            fam[key]["ite_write"] += sum(c["ite_write"] for c in win)
            fam[key]["w5m_tok"] += sum(c["c5"] for c in win)
            fam[key]["w1h_tok"] += sum(c["c1"] for c in win)
            for c in win:
                if c["gap"] is not None and c["cw"] > 0.5 * c["ctx"] and c["ctx"] > 20_000:
                    b = next(n for lo, n in ((3600, ">1h"), (900, "15-60m"), (300, "5-15m"), (60, "1-5m"), (0, "<1m")) if c["gap"] >= lo)
                    fam[key]["rewrite_ite_" + b] += c["ite_write"]
                if c["gap"] is not None:
                    b = next(n for lo, n in ((3600, ">1h"), (300, "5-60m"), (0, "<5m")) if c["gap"] >= lo)
                    fam[key]["calls_gap_" + b] += 1
            fam[key]["ite_rewrite"] += sum(c["ite_write"] for c in win if c["cw"] > 0.5 * c["ctx"] and c["ctx"] > 20_000
                                           and c["gap"] is not None)
            total["ite"] += ite
            total["raw"] += sum(c["raw"] for c in win)
            for c in win:
                model_mix[c["model"]] += c["ite"]
            # re-reads: a Read of a path this same transcript already read
            seen_paths, rr = set(), 0
            rr_tok = 0.0
            for _i, fp, tid in reads:
                if fp in seen_paths:
                    rr += 1
                    rr_tok += res_size.get(tid, 0.0)
                seen_paths.add(fp)
            fam[key]["reread_result_tok"] += rr_tok
            reread_all[0] += rr
            reread_all[1] += len(reads)
            if is_sub or role == "headless":
                sub_rows.append({"family": fname, "role": role, "ite": ite, "calls": len(win),
                                 "model": max({c["model"] for c in win}, key=lambda mm: sum(c["ite"] for c in win if c["model"] == mm)),
                                 "first_ctx": win[0]["ctx"], "first_ite": win[0]["ite"],
                                 "peak_ctx": max(c["ctx"] for c in win), "mean_ctx": sum(c["ctx"] for c in win) / len(win),
                                 "dur_s": win[-1]["t"] - win[0]["t"], "reads": len(reads), "rereads": rr,
                                 "ite_reads_over_50k": sum(c["x"] * 0.1 * max(0, c["cr"] - 50_000) for c in win),
                                 "ite_reads_over_100k": sum(c["x"] * 0.1 * max(0, c["cr"] - 100_000) for c in win),
                                 "ite_reads_over_150k": sum(c["x"] * 0.1 * max(0, c["cr"] - 150_000) for c in win),
                                 "reread_tok": rr_tok, "opus": c["x"] == 1.0})
            if role == "top-level":
                for cp in compacts:
                    if cp["t"] is None or cp["t"] < cutoff:
                        continue
                    nxt = calls[cp["call_index"]] if cp["call_index"] < len(calls) else None
                    prev = calls[cp["call_index"] - 1] if cp["call_index"] > 0 else None
                    # re-reads in the 40 calls after the boundary of files read before it
                    before = {fp for i, fp, _ in reads if i < cp["call_index"]}
                    after = [fp for i, fp, _ in reads if cp["call_index"] <= i < cp["call_index"] + 40]
                    compact_rows.append({
                        "family": fname, "trigger": cp["trigger"], "pre": cp["pre"], "summary_tok": cp["summary_tok"],
                        "gap_before_compact_s": (cp["t"] - prev["t"]) if prev else None,
                        "gap_resume_s": (nxt["t"] - cp["t"]) if nxt else None,
                        "resume_ctx": nxt["ctx"] if nxt else None, "resume_cr": nxt["cr"] if nxt else None,
                        "resume_ite": nxt["ite"] if nxt else None,
                        # the summarising call is not in the transcript: estimate it (prefix read warm, summary out)
                        "est_compact_ite": (0.1 * (cp["pre"] or 0) + 5 * cp["summary_tok"]) if prev and cp["t"] - prev["t"] < 3600
                        else (2.0 * (cp["pre"] or 0) + 5 * cp["summary_tok"]),
                        "reads_after": len(after), "rereads_after": sum(fp in before for fp in after)})
    out = {"days": DAYS, "now": now, "total": dict(total), "families": {k: dict(v) for k, v in fam.items()},
           "model_mix": dict(model_mix), "subagents": sub_rows, "compactions": compact_rows,
           "reread_all": reread_all, "model_x": MODEL_X}
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(out, open(os.path.join(OUT_DIR, "spend_census.json"), "w"))
    T = total["ite"] or 1
    print(f"total ITE/day {T / DAYS:,.0f}  raw tok/day {total['raw'] / DAYS:,.0f}  (${T / DAYS * PRICE_IN_PER_MTOK / 1e6:,.0f}/day assumed price)")
    for k, v in sorted(fam.items(), key=lambda kv: -kv[1]["ite"])[:25]:
        print(f"{100 * v['ite'] / T:5.1f}%  {k}  files {int(v['files'])} calls {int(v['calls'])}")
    print("compactions in window:", len(compact_rows), "unreadable:", int(total.get("unreadable_files", 0)))


if __name__ == "__main__":
    main()
