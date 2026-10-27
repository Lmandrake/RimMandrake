#!/usr/bin/env python3
"""Context-strategy simulator for a perpetual orchestrator seat (BENCH).

Offline and deterministic: no model calls. Two modes:

  --calibrate   measure real BENCH transcripts (usage fields, gaps, rounds,
                tool-output relevance proxy) -> calibration.json
  (default)     simulate strategies S0..S4 on the calibration, write
                sim_results.md + sim.png + sweep, all under OUT_DIR.

Units: cost is in "input-token equivalents" (ITE): 1 uncached input token = 1.
Prices are relative (cache read 0.1x, 5-min write 1.25x, 1-h write 2x,
output 5x input), so the ranking does not depend on the dollar rate.
Dollar figures use PRICE_IN_PER_MTOK, an assumption, not a measurement.

Strategies
  S0  grow until auto-compaction at COMPACT_FRAC of the window (200k or 1M).
  S1  handoff + restart at a fixed fill fraction (0.3 / 0.5 / 0.7).
  S2  supervisor probe every PROBE_EVERY rounds (and on every cache-cold
      wake): the agent estimates, from a relevance-decay model, whether
      handing off now is cheaper over the next HORIZON rounds; probe cost
      is charged. S2i probes ONLY when the cache has gone cold (idle gap >
      TTL), which is when continuing would have to re-write the prefix.
  S3  restart every round (stateless orchestrator reading state from disk).
  S4  context editing: clear tool results older than KEEP_ROUNDS once the
      context passes a trigger; the edit invalidates the cache from the
      first cleared block; compaction still backs it up.
"""
from __future__ import annotations

import argparse
import bisect
import glob
import json
import math
import os
import random
import re
import statistics as st
from datetime import datetime

# ----------------------------------------------------------------- parameters
OUT_DIR = "/mnt/d/ClaudeWork/rimmandrake/perpetual_ctx"
TRANSCRIPTS = os.path.expanduser("~/.claude/projects/-home-mandrake-rm-bench/*.jsonl")
HANDOFF_GLOB = "infrastructure/state/handoffs/*.md"   # relative to repo root

# price ratios (Anthropic prompt caching, relative to base input price)
READ_X = 0.10
WRITE_X = {"5m": 1.25, "1h": 2.0}
OUT_X = 5.0
TTL_S = {"5m": 300, "1h": 3600}
CACHE_TTL = "1h"            # MEASURED: BENCH writes ephemeral_1h (usage.cache_creation), see calibration.json
PRICE_IN_PER_MTOK = 5.0     # ASSUMPTION for $ display only (Opus-class input price)

WINDOW = 200_000
COMPACT_FRAC = 0.75         # Claude Code auto-compacts at ~150k of 200k (the builder brief says 150k)
COMPACT_OUT = 6_000         # summary output tokens (assumption; Claude Code summaries are ~3-10k)
COMPACT_KEEP = 0.60         # share of still-relevant context a compaction summary preserves (assumption)

# MEASURED: cold headless start creates 47,546 cache tokens (two probes 2026-10-26,
# design/RimMandrake/single_primary_design.md section 2.4 / L157; probe_headless_floor.json).
WAKE_TOKENS = 47_546
# MEASURED (this script, 49 BENCH sessions): an interactive BENCH session's first call carries a median
# 76,856-token context, of which only 27,226 is a cache read shared with the previous session; the rest
# (~49.6k: hooks, skills list, first prompt, wake reading) is written fresh. A lean headless restart
# (the 47,546 probe) shares the whole prefix.
WAKE_SHARED = 27_226
HANDOFF_KEEP = 0.75         # share of still-relevant context a written handoff preserves (assumption)
REFETCH_X = 1.0             # lost-but-needed tokens are re-read later as fresh input (x their size)
PROBE_IN = 250              # supervisor question tokens (S2)
PROBE_OUT = 350             # agent's answer incl. thinking (S2)
PROBE_EVERY = 10            # rounds between periodic S2 probes
HORIZON = 30                # rounds the S2 agent looks ahead
S2_NOISE = 0.25             # multiplicative noise (lognormal sigma) on the agent's own estimate
S4_CLEAR_MIN = 20_000       # S4: only clear when at least this much goes (Anthropic's clear_at_least idea)
KEEP_ROUNDS = 3             # S4: tool results younger than this stay
S4_TRIGGER = 100_000       # S4: start clearing above this context (Anthropic default trigger is 100k input tokens)
ROUNDS = 1500               # simulated orchestration rounds per run
SEEDS = 12

# Defaults used when calibration.json is absent; replaced by MEASURED values.
DEFAULT_CAL = {
    "base_ctx": 30_000, "round_delta": [3000], "calls_per_round": [4],
    "out_per_call": [400], "round_gaps_s": [120], "tool_share": 0.6,
    "handoff_tokens": 5_000, "relevance": {"lags": [1, 60], "R": [0.3, 0.0]},
}


# ---------------------------------------------------------------- calibration
PATH_RE = re.compile(r"[\w./-]+\.(?:py|md|cs|xml|jsonl|json|txt|png|sh|yaml|toml)\b")
ID_RE = re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,}\b")
SHA_RE = re.compile(r"\b[0-9a-f]{10}\b")


def _toks(text: str) -> set:
    return set(PATH_RE.findall(text)) | set(ID_RE.findall(text)) | set(SHA_RE.findall(text))


def _text_of(content) -> str:
    if isinstance(content, str):
        return content
    out = []
    for c in content or []:
        if isinstance(c, dict):
            if c.get("type") == "text":
                out.append(c.get("text", ""))
            elif c.get("type") == "tool_use":
                out.append(json.dumps(c.get("input", {})))
            elif c.get("type") == "tool_result":
                out.append(_text_of(c.get("content")))
    return "\n".join(out)


def _ts(s: str) -> float:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def parse_session(path: str):
    """Return (calls, rounds) for one top-level transcript.

    calls: dicts {t, ctx, cc, cr, out, c1h, c5m, round}
    rounds: dicts {t0, tool_blocks:[(size_tok, tokset)], said:set}
    A round starts at every user entry carrying non-tool_result content
    (owner message or task notification)."""
    calls, rounds, seen_ids = [], [], set()
    agent_calls = 0
    cur = None
    for line in open(path, errors="replace"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        t = d.get("type")
        if d.get("isSidechain"):
            continue
        if t == "user":
            content = d.get("message", {}).get("content")
            blocks = content if isinstance(content, list) else [{"type": "text", "text": content or ""}]
            human = any(isinstance(b, dict) and b.get("type") != "tool_result" for b in blocks)
            if human or cur is None:
                cur = {"t0": _ts(d["timestamp"]) if d.get("timestamp") else None,
                       "tool_blocks": [], "said": set()}
                rounds.append(cur)
            for b in blocks:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    txt = _text_of(b.get("content"))
                    cur["tool_blocks"].append((len(txt) / 4.0, _toks(txt)))
        elif t == "assistant":
            m = d.get("message", {})
            if cur is None:
                cur = {"t0": None, "tool_blocks": [], "said": set()}
                rounds.append(cur)
            for c in m.get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") in ("Agent", "Task"):
                    agent_calls += 1
            cur["said"] |= _toks(_text_of(m.get("content")))
            u = m.get("usage")
            mid = m.get("id")
            if not u or mid in seen_ids or not d.get("timestamp"):
                continue
            seen_ids.add(mid)
            cc = u.get("cache_creation_input_tokens") or 0
            cr = u.get("cache_read_input_tokens") or 0
            it = u.get("input_tokens") or 0
            ccd = u.get("cache_creation") or {}
            calls.append({"t": _ts(d["timestamp"]), "ctx": it + cc + cr, "cc": cc + it, "cr": cr,
                          "out": u.get("output_tokens") or 0,
                          "c1h": ccd.get("ephemeral_1h_input_tokens") or 0,
                          "c5m": ccd.get("ephemeral_5m_input_tokens") or 0,
                          "round": len(rounds) - 1})
    return calls, rounds, agent_calls


def _pct(v, ps=(10, 25, 50, 75, 90, 99)):
    v = sorted(v)
    if not v:
        return {}
    return {f"p{p}": v[min(len(v) - 1, int(p / 100 * len(v)))] for p in ps} | {"mean": sum(v) / len(v), "n": len(v)}


GAP_BUCKETS = [(0, 60, "<1 min"), (60, 300, "1-5 min"), (300, 900, "5-15 min"), (900, 3600, "15-60 min"),
               (3600, 7200, "1-2 h"), (7200, 1e12, ">2 h")]


def warm_window_table(per_call) -> dict:
    """MEASURED warm/cold split per API call by gap since the previous call (same session).

    warm = most of the prefix was a cache read; full re-write = cache_creation > 50% of the context.
    ITE at the harness's real 1-h prices; the 5-min counterfactual re-prices every call whose gap
    exceeds 300 s as a full prefix write at 1.25x (and every other write at 1.25x)."""
    rows = []
    tot = sum(READ_X * cr + WRITE_X["1h"] * cc + OUT_X * o for _, _, cr, cc, o, _, _ in per_call) or 1.0
    tot5 = 0.0
    for g, ctx, cr, cc, o, rw, first in per_call:
        if g > TTL_S["5m"] and not rw:
            tot5 += WRITE_X["5m"] * ctx + OUT_X * o
        else:
            tot5 += READ_X * cr + WRITE_X["5m"] * cc + OUT_X * o
    for lo, hi, name in GAP_BUCKETS:
        sel = [x for x in per_call if lo <= x[0] < hi]
        if not sel:
            continue
        n = len(sel)
        rw = [x for x in sel if x[5]]
        rows.append({
            "bucket": name, "calls": n, "share_calls": n / len(per_call),
            "share_first_of_round": sum(x[6] for x in sel) / n,
            "warm": sum(x[2] >= 0.5 * x[1] for x in sel) / n,
            "full_rewrite": len(rw) / n,
            "mean_ctx": sum(x[1] for x in sel) / n,
            "ite_share": sum(READ_X * x[2] + WRITE_X["1h"] * x[3] + OUT_X * x[4] for x in sel) / tot,
            "rewrite_ite_share": sum(WRITE_X["1h"] * x[3] for x in rw) / tot,
        })
    inround = [x for x in per_call if not x[6]]
    return {"rows": rows, "calls": len(per_call),
            "rewrite_ite_share_total": sum(WRITE_X["1h"] * x[3] for x in per_call if x[5]) / tot,
            "share_gap_over_5m": sum(x[0] > 300 for x in per_call) / len(per_call),
            "share_gap_over_1h": sum(x[0] > 3600 for x in per_call) / len(per_call),
            "inround_share_over_5m": sum(x[0] > 300 for x in inround) / max(1, len(inround)),
            "inround_share_over_1h": sum(x[0] > 3600 for x in inround) / max(1, len(inround)),
            "ite_1h_measured": tot, "ite_5m_counterfactual": tot5}


def calibrate(repo: str) -> dict:
    files = sorted(glob.glob(TRANSCRIPTS))
    real_ite, real_ctx, real_rounds = 0.0, [], 0
    per_call = []   # (gap_s, ctx, cache_read, cache_write, out, full_rewrite, first_call_of_round)
    used, base_ctx, deltas, cpr, outs, gaps, call_gaps = [], [], [], [], [], [], []
    round_dur = []          # wall seconds from a round's first call to its last (gaps are idle time between rounds)
    miss_events, max_ctx, c1h, c5m, tool_tok = [], [], 0, 0, 0.0
    lags = [1, 2, 3, 5, 8, 12, 20, 30, 50, 80, 120]
    H = 30          # look-ahead window of the proxy: referenced in [r+lag, r+lag+H)
    rel_num = [0.0] * len(lags)
    rel_den = [0.0] * len(lags)
    rel_cov = [0.0, 0.0]
    for f in files:
        try:
            calls, rounds, agents = parse_session(f)
        except Exception:
            continue
        if len(calls) < 50 or agents < 3:       # orchestrator sessions only
            continue
        used.append(os.path.basename(f)[:8])
        w_real = WRITE_X["1h"]
        real_ite += sum(READ_X * c["cr"] + w_real * c["cc"] + OUT_X * c["out"] for c in calls)
        real_ctx += [c["ctx"] for c in calls]
        real_rounds += len({c["round"] for c in calls})
        base_ctx.append(calls[0]["ctx"])
        max_ctx.append(max(c["ctx"] for c in calls))
        for a, b in zip(calls, calls[1:]):
            g = b["t"] - a["t"]
            call_gaps.append(g)
            rewrite = b["cc"] > 0.5 * b["ctx"] and b["ctx"] > 20_000
            if rewrite:
                miss_events.append(g)
            per_call.append((g, b["ctx"], b["cr"], b["cc"], b["out"], rewrite, b["round"] != a["round"]))
        c1h += sum(c["c1h"] for c in calls)
        c5m += sum(c["c5m"] for c in calls)
        by_round = {}
        for c in calls:
            by_round.setdefault(c["round"], []).append(c)
        ridx = sorted(by_round)
        for r0, r1 in zip(ridx, ridx[1:]):
            a, b = by_round[r0], by_round[r1]
            dlt = b[0]["ctx"] - a[0]["ctx"]
            if 0 <= dlt < 150_000:
                deltas.append(dlt)
            gaps.append(max(0.0, b[0]["t"] - a[-1]["t"]))
            round_dur.append(max(0.0, a[-1]["t"] - a[0]["t"]))
        for r in ridx:
            cpr.append(len(by_round[r]))
            outs.extend(c["out"] for c in by_round[r])
        # composition and relevance proxy
        seen = set()
        nr = len(rounds)
        said_idx = {}
        for i, r in enumerate(rounds):
            for tk in r["said"]:
                said_idx.setdefault(tk, []).append(i)
        tool_tok += sum(s for r in rounds for s, _ in r["tool_blocks"])
        for i, r in enumerate(rounds):
            for size, tks in r["tool_blocks"]:
                novel = tks - seen
                seen |= tks
                rel_cov[1] += size
                if not novel:
                    continue
                rel_cov[0] += size
                for j, lag in enumerate(lags):
                    if i + lag + H > nr:
                        break
                    rel_den[j] += size
                    hit = False
                    for tk in novel:
                        lst = said_idx.get(tk, [])
                        k = bisect.bisect_left(lst, i + lag)
                        if k < len(lst) and lst[k] < i + lag + H:
                            hit = True
                            break
                    if hit:
                        rel_num[j] += size
    R = [n / d if d else 0.0 for n, d in zip(rel_num, rel_den)]
    # handoff sizes
    hsz = [os.path.getsize(p) / 4.0 for p in glob.glob(os.path.join(repo, HANDOFF_GLOB))]
    # tool share of per-round growth: tool_result tokens vs usage growth
    ctx_growth = sum(deltas)
    cal = {
        "real_ite_per_round": real_ite / max(1, real_rounds), "real_mean_ctx_per_call": st.mean(real_ctx) if real_ctx else None,
        "real_rounds": real_rounds,
        "sessions_used": len(used), "session_ids": used,
        "base_ctx": st.median(base_ctx), "base_ctx_pct": _pct(base_ctx),
        "max_ctx_pct": _pct(max_ctx),
        "round_delta": deltas, "round_delta_pct": _pct(deltas),
        "calls_per_round": cpr, "calls_per_round_pct": _pct(cpr),
        "out_per_call": outs, "out_per_call_pct": _pct(outs),
        "round_gaps_s": gaps, "round_gaps_pct": _pct(gaps),
        "round_dur_s": round_dur, "round_dur_pct": _pct(round_dur),
        "call_gaps_pct": _pct(call_gaps),
        "warm_window": warm_window_table(per_call),
        "share_round_gaps_over_5m": sum(g > 300 for g in gaps) / max(1, len(gaps)),
        "share_round_gaps_over_1h": sum(g > 3600 for g in gaps) / max(1, len(gaps)),
        "full_rewrite_events": len(miss_events), "full_rewrite_gap_pct": _pct(miss_events),
        "cache_write_1h_tokens": c1h, "cache_write_5m_tokens": c5m,
        "tool_share": min(1.0, tool_tok / ctx_growth) if ctx_growth else None,
        "tool_result_tokens_est": tool_tok, "usage_growth_tokens": ctx_growth,
        "handoff_tokens": st.median(hsz) if hsz else None, "handoff_pct": _pct(hsz),
        "relevance": {"lags": lags, "R": R, "window": H, "den_tokens": rel_den,
                      "coverage_share_of_tool_tokens_with_novel_ids": rel_cov[0] / rel_cov[1] if rel_cov[1] else None,
                      "label": "PROXY: size-weighted share of tool-result blocks whose first-seen path/ID/sha "
                               "is mentioned by the assistant in rounds [r+lag, r+lag+30)"},
    }
    return cal


# ----------------------------------------------------------------- simulation
NEED_FRAC = 0.30            # of a "referenced" block, the share actually needed again (assumption; proxy can't see it)
REL_SCALE = 1.0             # sweep knob: scales the measured relevance curve (1.0 = measured proxy)
GAP_SCALE = 1.0             # sweep knob: multiplies every measured idle gap
NIGHT_IDLE_EVERY = 0        # sweep knob: insert an owner-away gap of NIGHT_IDLE_S every N rounds (0 = measured gaps only)
NIGHT_IDLE_S = 8 * 3600
STATE_OUT = 600             # S3: tokens the stateless orchestrator writes to disk per round (assumption)
STUB = 40                   # S4: tokens a cleared tool result leaves behind
SOFT_DELAY = 3              # S6: rounds the seat keeps working after the soft limit before it hands off (assumption)


def load_cal() -> dict:
    p = os.path.join(OUT_DIR, "calibration.json")
    if os.path.exists(p):
        return json.load(open(p))
    return DEFAULT_CAL


def rel(cal, age: float) -> float:
    """Proxy relevance of a block of age `age` rounds over the next HORIZON rounds (interpolated, measured)."""
    lags, R = cal["relevance"]["lags"], cal["relevance"]["R"]
    pts = [(l, r) for l, r in zip(lags, R) if r > 0]
    if age <= pts[0][0]:
        v = pts[0][1]
    elif age >= pts[-1][0]:
        v = pts[-1][1]
    else:
        for (l0, r0), (l1, r1) in zip(pts, pts[1:]):
            if l0 <= age <= l1:
                v = r0 + (r1 - r0) * (age - l0) / (l1 - l0)
                break
    return min(1.0, v * REL_SCALE)


class Seat:
    """One orchestrator conversation: blocks of context plus cache bookkeeping."""

    def __init__(self, cal, P, base_cached):
        self.cal, self.P = cal, P
        self.blocks = []            # [size, born_round, is_tool]
        self.base = P["BASE_CTX"]
        self.cost = 0.0
        self.cold_prefix = 0 if base_cached else self.base   # tokens that the next call must write

    @property
    def ctx(self):
        return self.base + sum(b[0] for b in self.blocks)

    def relevant(self, r):
        return sum(b[0] * rel(self.cal, r - b[1]) for b in self.blocks) * NEED_FRAC


def simulate(strategy: str, P: dict, seed: int, cal: dict) -> dict:
    rng = random.Random(seed)
    nrng = random.Random(seed + 1_000_003)     # S2 noise on its own stream: paired comparisons stay paired
    crng = random.Random(seed + 2_000_003)     # in-round cache expiry on its own stream
    drng = random.Random(seed + 3_000_003)     # S5 round durations on their own stream
    p_in = P["P_INROUND_COLD"]
    w = WRITE_X[P["TTL"]]
    ttl = TTL_S[P["TTL"]]
    deltas, cprs, outs, gaps = cal["round_delta"], cal["calls_per_round"], cal["out_per_call"], cal["round_gaps_s"]
    tool_share = P["TOOL_SHARE"]
    W = P["WINDOW"]
    kind, arg = strategy.split(":") if ":" in strategy else (strategy, None)

    tot = {"cost": 0.0, "ctx_sum": 0.0, "calls": 0, "lost": 0.0, "restarts": 0, "compactions": 0,
           "probes": 0, "cold_rewrites": 0.0, "wake": 0.0, "max_ctx": 0}
    seat = Seat(cal, P, base_cached=False)

    def charge(x):
        tot["cost"] += x

    def restart(r, cold):
        """Handoff + fresh session. The shared wake prefix is a cache read unless the cache is cold."""
        lost = seat.relevant(r) * (1 - P["HANDOFF_KEEP"])
        charge(OUT_X * P["HANDOFF"])                          # write the handoff
        lean = kind == "S3" or P.get("LEAN_WAKE")
        base = WAKE_TOKENS if lean else P["BASE_CTX"]
        shared = WAKE_TOKENS if lean else P["WAKE_SHARED"]
        wake = shared * (w if cold else READ_X) + w * (base - shared)
        seat.base = base
        charge(wake)
        tot["wake"] += wake
        seat.blocks = [[P["HANDOFF"], r, False]]
        charge(w * P["HANDOFF"])                              # read the handoff in
        if lost > 0:
            seat.blocks.append([lost * REFETCH_X, r, True])    # re-read what the handoff dropped
            charge(w * lost * REFETCH_X)
        seat.cold_prefix = 0
        tot["lost"] += lost
        tot["restarts"] += 1

    def compact(r, cold):
        C = seat.ctx
        charge((w if cold else READ_X) * C + OUT_X * COMPACT_OUT)
        lost = seat.relevant(r) * (1 - P["COMPACT_KEEP"])
        seat.blocks = [[COMPACT_OUT, r, False]]
        charge(w * (seat.base + COMPACT_OUT))                 # new prefix written
        if lost > 0:
            seat.blocks.append([lost * REFETCH_X, r, True])
            charge(w * lost * REFETCH_X)
        seat.cold_prefix = 0
        tot["lost"] += lost
        tot["compactions"] += 1

    def s2_should_handoff(r, cold, noise):
        C = seat.ctx
        rel_tok = seat.relevant(r)
        C_new = P["BASE_CTX"] + P["HANDOFF"] + rel_tok * (1 - P["HANDOFF_KEEP"]) * REFETCH_X
        if C_new >= C:
            return False
        kbar = P["KBAR"]
        p_cold = P["P_COLD"]
        per_round_saving = (C - C_new) * (kbar * READ_X + p_cold * (w - READ_X))
        saving = HORIZON * per_round_saving + (C * (w - READ_X) if cold else 0.0)
        base = WAKE_TOKENS if P.get("LEAN_WAKE") else P["BASE_CTX"]
        shared = WAKE_TOKENS if P.get("LEAN_WAKE") else P["WAKE_SHARED"]
        C_new += base - P["BASE_CTX"]
        cost = (OUT_X * P["HANDOFF"] + shared * (w if cold else READ_X)
                + w * (base - shared) + w * (C_new - base))
        return saving * noise > cost

    durs = cal.get("round_dur_s") or [0.0]
    t_sess = 0.0            # S5: wall seconds since the current session began
    soft_left = None        # S6: rounds left before the soft-limit handoff
    for r in range(P["ROUNDS"]):
        g = rng.choice(gaps) * GAP_SCALE
        if NIGHT_IDLE_EVERY and r % NIGHT_IDLE_EVERY == NIGHT_IDLE_EVERY - 1:
            g += NIGHT_IDLE_S
        cold = g > ttl
        t_sess += g + drng.choice(durs) if kind == "S5" else 0.0
        D = rng.choice(deltas)
        k = rng.choice(cprs)
        o = [rng.choice(outs) for _ in range(k)]

        # ---- strategy decisions at the start of a round (an inbound message wakes the seat)
        restarts_before = tot["restarts"]
        if kind == "S3":
            restart(r, cold)
        elif kind == "S1" and seat.ctx > (float(arg) * W if float(arg) <= 1 else float(arg)):
            restart(r, cold)
        elif kind == "S5" and (t_sess > float(arg) or cold):
            # owner's smart batching: a session never outlives the 1-h cache of its wake; it also hands
            # off early whenever the seat wakes cold (batch finished, idle) instead of re-writing context
            restart(r, cold)
            t_sess = 0.0
        elif kind == "S6":
            # owner's soft limit: past the size, finish the work in hand and hand off SOFT_DELAY rounds later
            if soft_left is None and seat.ctx > float(arg):
                soft_left = SOFT_DELAY
            if soft_left is not None:
                if soft_left <= 0 or cold:
                    restart(r, cold)
                    soft_left = None
                else:
                    soft_left -= 1
        elif kind in ("S2", "S2i"):
            probe = (kind == "S2" and r % PROBE_EVERY == 0) or cold
            if probe:
                tot["probes"] += 1
                charge(w * PROBE_IN + OUT_X * PROBE_OUT)          # the question and answer themselves
                if not cold:
                    charge(READ_X * seat.ctx)                     # the probe turn reads the prefix
                noise = math.exp(nrng.gauss(0, S2_NOISE))
                if s2_should_handoff(r, cold, noise):
                    restart(r, cold)
                    cold = False
                else:
                    seat.blocks.append([PROBE_IN + PROBE_OUT, r, False])
        elif kind == "S4" and seat.ctx > S4_TRIGGER:
            elig = [b for b in seat.blocks if b[2] and r - b[1] >= KEEP_ROUNDS and b[0] > STUB]
            cleared = sum(b[0] - STUB for b in elig)
            lost = 0.0
            if cleared >= S4_CLEAR_MIN:
                for b in elig:
                    lost += b[0] * rel(cal, r - b[1]) * NEED_FRAC
                    b[0] = STUB
                if lost > 0:
                    seat.blocks.append([lost * REFETCH_X, r, True])
                seat.cold_prefix = seat.ctx - seat.base       # cache broken after the base: re-write the rest
                tot["lost"] += lost
        if tot["restarts"] > restarts_before:
            cold = False        # restart() already paid the fresh prefix: the round reads it (no second w*C)
        if kind in ("S0", "S2", "S2i", "S4") and seat.ctx > COMPACT_FRAC * W:
            compact(r, cold)
            cold = False
        if kind in ("S1", "S5", "S6") and seat.ctx > COMPACT_FRAC * W:   # safety net; rare below the window
            compact(r, cold)
            cold = False

        # ---- the round itself: k calls
        C = seat.ctx
        if cold:
            charge(w * C)
            tot["cold_rewrites"] += w * C
        else:
            charge(w * seat.cold_prefix + READ_X * (C - seat.cold_prefix))
        seat.cold_prefix = 0
        new_in = max(0.0, D - sum(o)) / k
        prev_out = 0
        for i in range(k):
            if i > 0:
                # MEASURED: share of in-round call gaps longer than the TTL (foreground waits)
                charge(w * C if crng.random() < p_in else READ_X * C)
            charge(w * (new_in + prev_out) + OUT_X * o[i])
            tot["ctx_sum"] += C
            tot["calls"] += 1
            C += new_in + prev_out
            prev_out = o[i]
        tot["max_ctx"] = max(tot["max_ctx"], C)
        if kind == "S3":
            charge(OUT_X * STATE_OUT)
        seat.blocks.append([D * tool_share, r, True])
        seat.blocks.append([D * (1 - tool_share), r, False])
    n = P["ROUNDS"]
    return {"cost_per_round": tot["cost"] / n, "mean_ctx": tot["ctx_sum"] / tot["calls"],
            "lost_per_100": 100 * tot["lost"] / n, "restarts": tot["restarts"],
            "compactions": tot["compactions"], "probes": tot["probes"],
            "cold_share": tot["cold_rewrites"] / tot["cost"], "max_ctx": tot["max_ctx"]}


def params(cal, **over) -> dict:
    gaps = cal["round_gaps_s"]
    P = {"TTL": CACHE_TTL, "WINDOW": WINDOW, "BASE_CTX": cal["base_ctx"], "HANDOFF": cal["handoff_tokens"] or 5000,
         "HANDOFF_KEEP": HANDOFF_KEEP, "COMPACT_KEEP": COMPACT_KEEP, "ROUNDS": ROUNDS,
         "TOOL_SHARE": cal["tool_share"] or 0.2, "WAKE_SHARED": WAKE_SHARED, "KBAR": sum(cal["calls_per_round"]) / len(cal["calls_per_round"])}
    P.update(over)
    ttl = TTL_S[P["TTL"]]
    ww = cal.get("warm_window", {})
    P["P_INROUND_COLD"] = (ww.get("inround_share_over_5m", 0.0) if P["TTL"] == "5m"
                           else ww.get("inround_share_over_1h", 0.0)) * (1 if GAP_SCALE <= 1 else min(4.0, GAP_SCALE))
    P["P_COLD"] = sum(g * GAP_SCALE > ttl for g in gaps) / len(gaps) + (1 / NIGHT_IDLE_EVERY if NIGHT_IDLE_EVERY else 0)
    return P


STRATS = ["S0", "S1:0.3", "S1:0.5", "S1:0.7", "S2", "S2i", "S3", "S4"]


def run_all(cal, strats=STRATS, seeds=SEEDS, **over) -> dict:
    P = params(cal, **over)
    res = {}
    for s in strats:
        rows = [simulate(s, P, seed, cal) for seed in range(seeds)]
        res[s] = {k: sum(r[k] for r in rows) / len(rows) for k in rows[0]}
        cs = [r["cost_per_round"] for r in rows]
        res[s]["cost_sd"] = st.pstdev(cs)
    return res


# --------------------------------------------------------------------- report
S1_GRID = [60_000, 75_000, 90_000, 100_000, 125_000, 150_000, 200_000, 250_000, 350_000, 500_000]


def best_fixed(cal, seeds, **over):
    res = run_all(cal, strats=[f"S1:{t}" for t in S1_GRID], seeds=seeds, **over)
    k = min(res, key=lambda s: res[s]["cost_per_round"])
    return k, res[k]


SCENARIOS = [
    # name, globals override, params override
    ("base (measured)", {}, {}),
    ("TTL 5 min", {}, {"TTL": "5m"}),
    ("gaps x0.25", {"GAP_SCALE": 0.25}, {}),
    ("gaps x4", {"GAP_SCALE": 4.0}, {}),
    ("+8h owner idle every 40 rounds", {"NIGHT_IDLE_EVERY": 40}, {}),
    ("TTL 5m + 8h idle /40", {"NIGHT_IDLE_EVERY": 40}, {"TTL": "5m"}),
    ("lean wake (47.5k all cached)", {}, {"LEAN_WAKE": True}),
    ("wake x1.5 (115k, headless 71k)", {"WAKE_TOKENS": 71_319}, {"BASE_CTX": 115_284}),
    ("wake x0.5 (38k, headless 24k)", {"WAKE_TOKENS": 23_773, "WAKE_SHARED": 13_613}, {"BASE_CTX": 38_428, "WAKE_SHARED": 13_613}),
    ("handoff 16k (p75)", {}, {"HANDOFF": 16_474}),
    ("S2 agent misjudges (sigma 1.0)", {"S2_NOISE": 1.0}, {}),
    ("relevance x0.3 (fast decay)", {"REL_SCALE": 0.3}, {}),
    ("relevance x2 (sticky)", {"REL_SCALE": 2.0}, {}),
    ("need frac 0.8", {"NEED_FRAC": 0.8}, {}),
    ("handoff keeps 40%", {}, {"HANDOFF_KEEP": 0.4}),
    ("tool share 0.6 (S4 friendly)", {}, {"TOOL_SHARE": 0.6}),
]
SWEEP_STRATS = ["S0", "S2", "S2i", "S3", "S4"]


MATTER_STRATS = [  # (label, strategy, window)
    ("measured practice (mimic: hand off near 347k on a 1M window)", "S1:347000", 1_000_000),
    ("(3) let it compact, 1M window (auto-compaction at 750k)", "S0", 1_000_000),
    ("(3') let it compact, 200k window", "S0", 200_000),
    ("best fixed size threshold, 125k", "S1:125000", 1_000_000),
    ("(1) smart batching: session <= 55 min, early handoff when cold", "S5:3300", 1_000_000),
    ("(1) smart batching: session <= 30 min, early handoff when cold", "S5:1800", 1_000_000),
    ("(2) soft limit 100k, hand off 3 rounds later", "S6:100000", 1_000_000),
    ("(2) soft limit 150k, hand off 3 rounds later", "S6:150000", 1_000_000),
    ("(2) soft limit 250k, hand off 3 rounds later", "S6:250000", 1_000_000),
    ("restart every round (S3)", "S3", 1_000_000),
]


def does_it_matter(cal, seeds):
    """Each orchestrator strategy's saving vs measured practice, as a % of ALL spend (spend_census.json)."""
    cen = json.load(open(os.path.join(OUT_DIR, "spend_census.json")))
    T = cen["total"]["ite"]
    orch = sum(v["ite"] for k, v in cen["families"].items() if k.endswith("/ top-level")) / T
    rows = []
    for label, strat, W in MATTER_STRATS:
        r = run_all(cal, strats=[strat], seeds=seeds, WINDOW=W)[strat]
        rows.append((label, strat, W, r))
    base = rows[0][3]["cost_per_round"]
    out = [f"orchestrator (top-level) share of total spend: {100 * orch:.1f}% "
           f"(census over {cen['days']} days, {T / cen['days'] / 1e6:,.1f}M ITE/day)", "",
           "| strategy | sim ITE/round | vs measured practice | % of TOTAL spend | mean ctx | restarts/1k rounds | compactions/1k |",
           "|---|---|---|---|---|---|---|"]
    for label, strat, W, r in rows:
        rel_ = r["cost_per_round"] / base - 1
        out.append(f"| {label} (`{strat}`@{W // 1000}k) | {r['cost_per_round']:,.0f} | {100 * rel_:+.1f}% | "
                   f"{100 * rel_ * orch:+.2f}% | {r['mean_ctx']:,.0f} | {1000 * r['restarts'] / ROUNDS:.0f} | "
                   f"{1000 * r['compactions'] / ROUNDS:.0f} |")
    rd = cal.get("round_dur_pct") or {}
    out += ["", f"round wall duration (first to last call) p50 {rd.get('p50', 0):,.0f} s, p90 {rd.get('p90', 0):,.0f} s; "
            f"seeds {seeds}, rounds {ROUNDS}"]
    txt = "\n".join(out)
    open(os.path.join(OUT_DIR, "matter.md"), "w").write(txt + "\n")
    print(txt)


def _with_globals(g):
    old = {k: globals()[k] for k in g}
    globals().update(g)
    return old


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--repo", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
    ap.add_argument("--seeds", type=int, default=SEEDS)
    ap.add_argument("--sweep-seeds", type=int, default=6)
    ap.add_argument("--matter", action="store_true",
                    help="express each strategy's saving as a share of TOTAL spend (needs spend_census.json)")
    a = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    if a.matter:
        does_it_matter(load_cal(), a.seeds)
        return
    if a.calibrate:
        cal = calibrate(a.repo)
        json.dump(cal, open(os.path.join(OUT_DIR, "calibration.json"), "w"))
        print("calibration.json written:", cal["sessions_used"], "sessions")
        return
    cal = load_cal()
    md = os.path.join(OUT_DIR, "sim_results.md")
    out = [f"# Perpetual orchestrator context-strategy sim (generated by {os.path.basename(__file__)})", "",
           "Cost unit: input-token equivalents (ITE) per orchestration round; $ at "
           f"${PRICE_IN_PER_MTOK}/MTok input (assumed). Rounds = inbound messages (owner or task notification).", ""]
    # ---- calibration summary
    c = cal
    out += ["## Measured calibration (BENCH transcripts; calibration.json)", "",
            f"- sessions: {c['sessions_used']} orchestrator sessions (>=50 API calls, >=3 Agent calls)",
            f"- first-call context p50 {c['base_ctx_pct']['p50']:,} (p90 {c['base_ctx_pct']['p90']:,}); "
            f"shared cache read at wake p50 {WAKE_SHARED:,}",
            f"- per-round context growth p50 {c['round_delta_pct']['p50']:,} mean {c['round_delta_pct']['mean']:,.0f} "
            f"p90 {c['round_delta_pct']['p90']:,}",
            f"- API calls per round mean {c['calls_per_round_pct']['mean']:.2f}; output per call p50 "
            f"{c['out_per_call_pct']['p50']} mean {c['out_per_call_pct']['mean']:.0f}",
            f"- inter-round gap p50 {c['round_gaps_pct']['p50']:.0f}s p90 {c['round_gaps_pct']['p90']:.0f}s "
            f"p99 {c['round_gaps_pct']['p99']:.0f}s; >5 min {100*c['share_round_gaps_over_5m']:.1f}%, "
            f">1 h {100*c['share_round_gaps_over_1h']:.1f}%",
            f"- cache writes: 1h {c['cache_write_1h_tokens']:,} tok, 5m {c['cache_write_5m_tokens']:,} tok "
            f"(BENCH runs on the 1-hour TTL); {c['full_rewrite_events']} full-prefix rewrites, gap p50 "
            f"{c['full_rewrite_gap_pct'].get('p50', 0):.0f}s",
            f"- session peak context p50 {c['max_ctx_pct']['p50']:,} p90 {c['max_ctx_pct']['p90']:,}",
            f"- tool-result share of context growth {c['tool_share']:.2f} (chars/4 estimate)",
            f"- handoff size p50 {c['handoff_tokens']:,.0f} tok (bytes/4, {c['handoff_pct']['n']} files) "
            f"p90 {c['handoff_pct']['p90']:,.0f}",
            "- relevance PROXY R(lag) = " + ", ".join(f"{l}:{r:.2f}" for l, r in zip(c['relevance']['lags'], c['relevance']['R']) if r)
            + f" (coverage {c['relevance']['coverage_share_of_tool_tokens_with_novel_ids']:.2f} of tool tokens)",
            "  " + c["relevance"]["label"], ""]
    ww = c.get("warm_window")
    if ww:
        out += ["## Warm-window census (owner's question: how often is a call inside the cache window?)", "",
                f"Every main-thread API call of the {c['sessions_used']} sessions ({ww['calls']:,} calls), by gap since "
                "the previous call. The harness writes 1-hour cache (5-min writes measured: "
                f"{c['cache_write_5m_tokens']:,} tokens). 'warm' = cache read >= half the context; 'full re-write' = "
                "cache write > half the context. Spend shares at 1-h prices.", "",
                "| gap since previous call | calls | share of calls | of which round-opening | warm | full re-write | mean ctx | share of spend | spend on re-writes |",
                "|---|---|---|---|---|---|---|---|---|"]
        for r in ww["rows"]:
            out.append(f"| {r['bucket']} | {r['calls']:,} | {100*r['share_calls']:.1f}% | {100*r['share_first_of_round']:.0f}% | "
                       f"{100*r['warm']:.1f}% | {100*r['full_rewrite']:.1f}% | {r['mean_ctx']:,.0f} | "
                       f"{100*r['ite_share']:.1f}% | {100*r['rewrite_ite_share']:.1f}% |")
        out += ["", f"- Re-writes are {100*ww['rewrite_ite_share_total']:.1f}% of measured spend. Calls with a gap > 5 min: "
                f"{100*ww['share_gap_over_5m']:.1f}% of all calls, {100*c['share_round_gaps_over_5m']:.0f}% of round-opening "
                f"calls, {100*ww['inround_share_over_5m']:.1f}% of in-round calls; > 1 h: {100*ww['share_gap_over_1h']:.2f}%.",
                f"- Counterfactual on the same calls with a 5-min TTL: {ww['ite_5m_counterfactual']/ww['ite_1h_measured']:.2f}x "
                "the measured 1-h spend. The owner's suspicion holds for the 5-min window (a third of the orchestrator's "
                "wake-ups would miss it); the 1-h TTL BENCH already uses absorbs nearly all of them.",
                "- The sim uses these measured rates: round-opening gaps are bootstrapped from the measured distribution, and "
                f"in-round calls go cold with the measured probability ({100*ww['inround_share_over_1h']:.2f}% at 1 h, "
                f"{100*ww['inround_share_over_5m']:.1f}% at 5 min).", ""]
    # ---- base table
    rows = []
    for W in (200_000, 1_000_000):
        res = run_all(cal, strats=STRATS, seeds=a.seeds, WINDOW=W)
        bk, bv = best_fixed(cal, a.seeds, WINDOW=W)
        res[f"S1 best fixed ({bk.split(':')[1]})"] = bv
        if W == 1_000_000:
            res["S1:347000 (mimics measured practice)"] = run_all(cal, strats=["S1:347000"], seeds=a.seeds, WINDOW=W)["S1:347000"]
        rows.append((W, res))
    ref = rows[0][1]["S0"]["cost_per_round"]
    out += ["## Base scenario", "",
            "| window | strategy | ITE/round | $/1000 rounds | vs S0@200k | mean ctx/call | peak ctx | restarts | compactions | lost-relevant tok/100 rounds |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for W, res in rows:
        for s, v in res.items():
            out.append(f"| {W//1000}k | {s} | {v['cost_per_round']:,.0f} ± {v['cost_sd']:,.0f} | "
                       f"{v['cost_per_round']*1000*PRICE_IN_PER_MTOK/1e6:,.0f} | {100*(v['cost_per_round']/ref-1):+.1f}% | "
                       f"{v['mean_ctx']:,.0f} | {v['max_ctx']:,.0f} | {v['restarts']:.0f} | {v['compactions']:.0f} | {v['lost_per_100']:,.0f} |")
    if c.get("real_ite_per_round"):
        out.append(f"| 1000k | MEASURED real BENCH ({c['real_rounds']} rounds) | {c['real_ite_per_round']:,.0f} | "
                   f"{c['real_ite_per_round']*1000*PRICE_IN_PER_MTOK/1e6:,.0f} | {100*(c['real_ite_per_round']/ref-1):+.1f}% | "
                   f"{c['real_mean_ctx_per_call']:,.0f} | {c['max_ctx_pct']['p50']:,} (p50) | - | - | - |")
    out += ["", f"(± = sd across {a.seeds} seeds of {ROUNDS} rounds; strategies share random streams, so differences are paired.)", ""]
    open(md, "w").write("\n".join(out) + "\n\n## Sensitivity sweep\n\n(running)\n")
    # ---- sweep
    sweep = []
    for name, g, po in SCENARIOS:
        old = _with_globals(g)
        try:
            res = run_all(cal, strats=SWEEP_STRATS, seeds=a.sweep_seeds, **po)
            bk, bv = best_fixed(cal, a.sweep_seeds, **po)
            res["S1*"] = bv
            res["S1*"]["thr"] = bk.split(":")[1]
            res["S0@1M"] = run_all(cal, strats=["S0"], seeds=a.sweep_seeds, WINDOW=1_000_000, **po)["S0"]
        finally:
            globals().update(old)
        sweep.append((name, res))
        print("sweep", name, flush=True)
    keys = ["S0", "S0@1M", "S1*", "S2", "S2i", "S3", "S4"]
    sw = ["| scenario | " + " | ".join(keys) + " | cheapest | S1* threshold |", "|---" * (len(keys) + 3) + "|"]
    for name, res in sweep:
        base = res["S0"]["cost_per_round"]
        best = min(keys, key=lambda k: res[k]["cost_per_round"])
        sw.append(f"| {name} | " + " | ".join(
            f"{res[k]['cost_per_round']/1000:,.0f}k ({100*(res[k]['cost_per_round']/base-1):+.0f}%)" for k in keys)
            + f" | {best} | {int(res['S1*']['thr'])//1000}k |")
    text = open(md).read().replace("(running)\n", "Cells: ITE/round (vs S0 at 200k in the same scenario); 200k window unless noted. "
                                   "S1* = best fixed absolute threshold from the grid, chosen with hindsight per scenario.\n\n"
                                   + "\n".join(sw) + "\n")
    open(md, "w").write(text)
    plot(rows, sweep, keys)
    json.dump({"base": [(W, r) for W, r in rows], "sweep": sweep}, open(os.path.join(OUT_DIR, "sim_raw.json"), "w"))
    print("wrote", md)


def plot(rows, sweep, keys):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [1, 1.25]})
    for W, res, mk in ((200_000, rows[0][1], "o"), (1_000_000, rows[1][1], "s")):
        for s, v in res.items():
            ax1.scatter(v["mean_ctx"] / 1000, v["cost_per_round"] / 1000, marker=mk, color="#1f6f8b" if W == 200_000 else "#c2410c")
            if v["cost_per_round"] < 120_000 and s not in ("S0", "S3") and not s.startswith("S1 best"):
                continue                                    # crowded corner: label only the anchors
            ax1.annotate(s.replace("S1 best fixed", "S1*"), (v["mean_ctx"] / 1000, v["cost_per_round"] / 1000),
                         fontsize=7, xytext=(4, 2), textcoords="offset points")
    cal = load_cal()
    if cal.get("real_ite_per_round"):
        ax1.scatter(cal["real_mean_ctx_per_call"] / 1000, cal["real_ite_per_round"] / 1000, marker="*", s=160, color="black")
        ax1.annotate("MEASURED real BENCH", (cal["real_mean_ctx_per_call"] / 1000, cal["real_ite_per_round"] / 1000),
                     fontsize=8, xytext=(6, -10), textcoords="offset points")
    ax1.set_xlabel("mean context per API call (k tokens) - lower = less context rot")
    ax1.set_ylabel("cost per round (k input-token equivalents)")
    ax1.set_title("Base scenario: circles 200k window, squares 1M window", fontsize=10)
    ax1.grid(alpha=0.3)
    names = [n for n, _ in sweep]
    show = ["S0@1M", "S1*", "S2", "S2i", "S3", "S4"]
    colors = ["#c2410c", "#555555", "#1f6f8b", "#6aa84f", "#8e44ad", "#b8860b"]
    for j, (k, col) in enumerate(zip(show, colors)):
        ys = [100 * (res[k]["cost_per_round"] / res["S0"]["cost_per_round"] - 1) for _, res in sweep]
        ax2.scatter(ys, [i + (j - 2.5) * 0.11 for i in range(len(names))], color=col, label=k, s=18)
    ax2.axvline(0, color="black", lw=0.8)
    ax2.set_yticks(range(len(names)))
    ax2.set_yticklabels(names, fontsize=8)
    ax2.invert_yaxis()
    ax2.set_xlabel("cost vs S0 (200k auto-compaction), % - left is cheaper")
    ax2.set_xlim(-60, 150)
    ax2.legend(fontsize=8, loc="center", bbox_to_anchor=(0.66, 0.42))
    ax2.grid(axis="x", alpha=0.3)
    ax2.set_title("Sensitivity sweep (values beyond +150% clipped)", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "sim.png"), dpi=110)


if __name__ == "__main__":
    main()
