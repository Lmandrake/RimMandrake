#!/usr/bin/env python3
"""Selftest for ctx_strategy_sim.py pricing (CTX_SIM_FIX_UNCACHED_INPUT_PRICE).

Uncached usage.input_tokens is base-price input (1x), never a 1-h cache write (2x). A synthetic
orchestrator transcript (60 calls, 3 Agent calls, known usage) goes through calibrate(); the
measured ITE per round and the warm-window table must match a hand price. Nothing real read or written."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ctx_strategy_sim as C  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  -- " + str(detail)))
    if not ok:
        FAILS.append(name)


N, IT, CC, CR, OUT = 60, 1000, 500, 30_000, 200


def write_transcript(path):
    with open(path, "w") as f:
        for i in range(N):
            ts = f"2026-11-05T10:{i // 60:02d}:{i % 60:02d}.000Z"
            f.write(json.dumps({"type": "user", "timestamp": ts,
                                "message": {"content": [{"type": "text", "text": f"go {i}"}]}}) + "\n")
            content = [{"type": "text", "text": "ok"}]
            if i < 3:
                content.append({"type": "tool_use", "name": "Agent", "input": {}})
            f.write(json.dumps({"type": "assistant", "timestamp": ts, "message": {
                "id": f"m{i}", "content": content,
                "usage": {"input_tokens": IT, "cache_creation_input_tokens": CC, "cache_read_input_tokens": CR,
                          "output_tokens": OUT, "cache_creation": {"ephemeral_1h_input_tokens": CC}}}}) + "\n")


with tempfile.TemporaryDirectory() as d:
    write_transcript(os.path.join(d, "s1.jsonl"))
    C.TRANSCRIPTS = os.path.join(d, "*.jsonl")
    cal = C.calibrate(d)

per_call = C.READ_X * CR + C.WRITE_X["1h"] * CC + 1.0 * IT + C.OUT_X * OUT
wrong = C.READ_X * CR + C.WRITE_X["1h"] * (CC + IT) + C.OUT_X * OUT
check("one session used", cal["sessions_used"] == 1, cal["sessions_used"])
check("real_ite_per_round prices uncached input at 1x",
      abs(cal["real_ite_per_round"] - per_call) < 1e-6, (cal["real_ite_per_round"], per_call, wrong))
ww = cal["warm_window"]
check("warm_window ITE prices uncached input at 1x",
      abs(ww["ite_1h_measured"] - per_call * (N - 1)) < 1e-6, (ww["ite_1h_measured"], per_call * (N - 1)))
five = C.READ_X * CR + C.WRITE_X["5m"] * CC + IT + C.OUT_X * OUT
check("5-min counterfactual prices uncached input at 1x",
      abs(ww["ite_5m_counterfactual"] - five * (N - 1)) < 1e-6, (ww["ite_5m_counterfactual"], five * (N - 1)))
check("cache-write tokens count only cache_creation", cal["cache_write_1h_tokens"] == CC * N, cal["cache_write_1h_tokens"])
check("context still sums all three input kinds", cal["real_mean_ctx_per_call"] == IT + CC + CR, cal["real_mean_ctx_per_call"])

# Cold paths: the same 60 warm calls 1 s apart, then one warm call after a 10-min gap (the 5-min
# counterfactual's cold branch, not a rewrite) and one call after a >2 h gap that rewrites the prefix
# mostly as UNCACHED input (it 31k, cc 1k, cr 0): a full rewrite only if uncached input counts.
RW_IT, RW_CC, GAP_COLD, GAP_RW = 31_000, 1_000, 600, 7_500


def write_cold_transcript(path):
    t = [float(i) for i in range(N)] + [N - 1 + GAP_COLD, N - 1 + GAP_COLD + GAP_RW]
    usage = [(IT, CC, CR)] * (N + 1) + [(RW_IT, RW_CC, 0)]
    with open(path, "w") as f:
        for i, (ti, (it, cc, cr)) in enumerate(zip(t, usage)):
            ts = f"2026-11-05T{10 + int(ti) // 3600:02d}:{int(ti) % 3600 // 60:02d}:{int(ti) % 60:02d}.000Z"
            f.write(json.dumps({"type": "user", "timestamp": ts,
                                "message": {"content": [{"type": "text", "text": f"go {i}"}]}}) + "\n")
            content = [{"type": "text", "text": "ok"}]
            if i < 3:
                content.append({"type": "tool_use", "name": "Agent", "input": {}})
            f.write(json.dumps({"type": "assistant", "timestamp": ts, "message": {
                "id": f"c{i}", "content": content,
                "usage": {"input_tokens": it, "cache_creation_input_tokens": cc, "cache_read_input_tokens": cr,
                          "output_tokens": OUT, "cache_creation": {"ephemeral_1h_input_tokens": cc}}}}) + "\n")


with tempfile.TemporaryDirectory() as d:
    write_cold_transcript(os.path.join(d, "s2.jsonl"))
    C.TRANSCRIPTS = os.path.join(d, "*.jsonl")
    cw = C.calibrate(d)["warm_window"]

ctx = IT + CC + CR
rw_1h = C.WRITE_X["1h"] * RW_CC + RW_IT + C.OUT_X * OUT                     # 34000
rw_5m = C.WRITE_X["5m"] * RW_CC + RW_IT + C.OUT_X * OUT                     # rewrite: priced as written
cold_5m = C.WRITE_X["5m"] * (ctx - IT) + IT + C.OUT_X * OUT                 # >5 min, not a rewrite
tot = per_call * N + rw_1h
tot5 = five * (N - 1) + cold_5m + rw_5m
rows = {r["bucket"]: r for r in cw["rows"]}
check("cold transcript: 62 calls -> 61 priced", cw["calls"] == N + 1, cw["calls"])
check("cold ite_1h_measured prices uncached rewrite input at 1x",
      abs(cw["ite_1h_measured"] - tot) < 1e-6, (cw["ite_1h_measured"], tot))
check("cold 5-min counterfactual: >5 min re-write excludes uncached input from the 1.25x",
      abs(cw["ite_5m_counterfactual"] - tot5) < 1e-6, (cw["ite_5m_counterfactual"], tot5))
check("buckets seen", sorted(rows) == sorted(["<1 min", "5-15 min", ">2 h"]), sorted(rows))
for name, want in (("<1 min", per_call * (N - 1) / tot), ("5-15 min", per_call / tot), (">2 h", rw_1h / tot)):
    got = rows.get(name, {}).get("ite_share")
    check(f"row {name} ite_share prices uncached input at 1x", got is not None and abs(got - want) < 1e-9,
          (got, want))
check("rows' ite_share sum to 1", abs(sum(r["ite_share"] for r in cw["rows"]) - 1.0) < 1e-9)
check(">2 h call is a full rewrite (uncached input counts toward it)",
      rows.get(">2 h", {}).get("full_rewrite") == 1.0, rows.get(">2 h"))
want_rw = (C.WRITE_X["1h"] * RW_CC + RW_IT) / tot
check("rewrite_ite_share_total includes uncached input at 1x",
      abs(cw["rewrite_ite_share_total"] - want_rw) < 1e-9, (cw["rewrite_ite_share_total"], want_rw))
check(">2 h row rewrite_ite_share includes uncached input at 1x",
      abs(rows.get(">2 h", {}).get("rewrite_ite_share", -1) - want_rw) < 1e-9, rows.get(">2 h"))

print("FAIL" if FAILS else "PASS", f"{len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
