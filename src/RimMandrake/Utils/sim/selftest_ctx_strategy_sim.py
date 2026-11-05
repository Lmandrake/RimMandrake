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

print("FAIL" if FAILS else "PASS", f"{len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
