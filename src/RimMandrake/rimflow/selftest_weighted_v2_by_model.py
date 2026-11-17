#!/usr/bin/env python3
"""Weighted tokens are weighted by model too (RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT).

The owner, 2026-11-16: "I want you to properly weight tokens by the model as well so they are more comparable."
Unit weighted_v2 (role_launch.TOKEN_UNIT): each usage field weighted by that model's own list price for it, divided by
the list price of one uncached Opus 5.5 input token (role_launch.MODEL_PRICES, REF_MODEL). Cases:
  V1 the reference: an Opus 5.5 input token weighs exactly 1.
  V2 identical raw usage on Fable 5.2 and Opus 5.5 gives figures in the ratio of their list prices; and on four real
     run results (two Opus 5.5, two Fable 5.2, costBasis "list") the figure is proportional to the CLI's own costUSD:
     one weighted-tokens-per-dollar constant fits all four (the table is checked against Anthropic's bill, not only
     against itself).
  V3 an unknown model raises, naming the model; there is no fallback weight. An alias with no env var raises too.
  V4 a provider-prefixed, dated, versioned or [1m] model id resolves to its table row.
  V5 a weighted_v1 record is converted (from its stored per-model usage when it has one, else as a marked upper
     bound), and a weighted_v2 record is returned as it is, never weighted twice.
  V6 zero and missing usage: all-zero usage is a measured 0; a missing field is UNMEASURED (None); an all-zero entry
     of a model not in the table (the CLI's "<synthetic>") weighs 0 without raising; a cache write with no TTL split
     is weighed at the dearer 1h rate.
  V7 modelUsage (the whole process, subagents included) is preferred over the main thread's usage.
"""
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import role_launch as RL  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def raises(fn, *a):
    try:
        fn(*a)
    except RL.UnknownModel as e:
        return str(e)
    return None


OPUS, FABLE = "claude-opus-5-5", "claude-fable-5-2"

# V1
w = RL.model_weights(OPUS)
check(w["input_tokens"] == 1 and RL.REF_MODEL == OPUS, "V1 Opus 5.5 input weighs 1 (got %r)" % (w["input_tokens"],))
check(RL.run_tokens({"usage": {"input_tokens": 1000, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
                               "output_tokens": 0}}, OPUS) == 1000, "V1 1,000 Opus input tokens weigh 1,000")
check(RL.TOKEN_UNIT == "weighted_v2", "V1 TOKEN_UNIT is weighted_v2 (got %r)" % RL.TOKEN_UNIT)

# V2 identical usage, two models: the ratio of list prices
U = {"input_tokens": 300, "cache_creation_input_tokens": 5000, "cache_read_input_tokens": 400000,
     "output_tokens": 9000, "cache_creation": {"ephemeral_5m_input_tokens": 1000, "ephemeral_1h_input_tokens": 4000}}
fo, ff = RL.run_tokens({"usage": U}, OPUS), RL.run_tokens({"usage": U}, FABLE)
po, pf = RL.MODEL_PRICES[OPUS], RL.MODEL_PRICES[FABLE]
cost = lambda p: (300 * p["input_tokens"] + 1000 * p["cache_write_5m"] + 4000 * p["cache_write_1h"]  # noqa: E731
                  + 400000 * p["cache_read_input_tokens"] + 9000 * p["output_tokens"])
check(Fraction(ff, fo) == cost(pf) / cost(po), "V2 Fable/Opus on identical usage = list-price ratio %s (got %d/%d)"
      % (cost(pf) / cost(po), ff, fo))
check(ff != fo, "V2 the two models do not weigh the same")
# four real results (D:\ClaudeWork\rimmandrake\dispatcher\detached\*.out.json, 2026-11-16, costBasis "list")
REAL = [  # (model, input, cw1h, cache read, output, costUSD)
    (OPUS, 342, 360603, 40509703, 154142, 14.0709726),           # finish-slack-tonight-two-dec-1794878614
    (OPUS, 228, 223575, 18350114, 75515, 6.9698348),             # repin-graffiti-ugliness-bar-1794889468
    (FABLE, 416, 585535, 78985970, 281417, 36.425762),           # invent-slack-live-end-green-1794885421
    (FABLE, 224, 450791, 35672050, 190342, 21.962538),           # rescue-pyrelands-black-rain-1794889288
]
per_usd = []
for m, i, c1, r, o, usd in REAL:
    res = {"modelUsage": {m: {"inputTokens": i, "outputTokens": o, "cacheReadInputTokens": r,
                              "cacheCreationInputTokens": c1, "cacheCreationEphemeral5mInputTokens": 0,
                              "cacheCreationEphemeral1hInputTokens": c1, "costUSD": usd}}}
    per_usd.append(RL.run_tokens(res) / usd)
spread = max(per_usd) / min(per_usd) - 1
print("     V2 weighted tokens per costUSD over %d real results: min %.1f max %.1f, spread %.2e (limit 1e-6)"
      % (len(per_usd), min(per_usd), max(per_usd), spread))
check(spread < 1e-6, "V2 one tokens-per-dollar constant fits all four real results (spread %.2e)" % spread)

# V3
msg = raises(RL.run_tokens, {"usage": U}, "claude-nonesuch-9-9")
check(msg is not None and "claude-nonesuch-9-9" in msg, "V3 an unknown model raises by name (%r)" % msg)
msg = raises(RL.run_tokens, {"modelUsage": {"claude-nonesuch-9-9": {"inputTokens": 5, "outputTokens": 1}}})
check(msg is not None and "claude-nonesuch-9-9" in msg, "V3 an unknown model in modelUsage raises by name (%r)" % msg)
msg = raises(RL.run_tokens, {"usage": U}, None)
check(msg is not None, "V3 usage with no model raises, never a fallback weight (%r)" % msg)
saved = os.environ.pop(RL.MODEL_VARS["opus"], None)
try:
    msg = raises(RL.resolve_model, "opus")
    check(msg is not None and "opus" in msg, "V3 an alias with its env var unset raises by name (%r)" % msg)
    os.environ[RL.MODEL_VARS["opus"]] = "xx.anthropic.claude-opus-5-5-v1:0"
    check(RL.resolve_model("opus") == OPUS, "V3 an alias resolves through its env var")
finally:
    os.environ.pop(RL.MODEL_VARS["opus"], None)
    if saved is not None:
        os.environ[RL.MODEL_VARS["opus"]] = saved

# V4
for mid, want in (("xx.anthropic.claude-opus-5-5-v1:0", OPUS), ("anthropic.claude-fable-5-2", FABLE),
                  ("claude-opus-5-5@20261101", OPUS), ("claude-opus-5-5[1m]", OPUS),
                  ("claude-sonnet-4-5-20250929", "claude-sonnet-4-5"), ("CLAUDE-OPUS-5-5", OPUS)):
    got = None
    try:
        got = RL.resolve_model(mid)
    except RL.UnknownModel as e:
        got = "raised %s" % e
    check(got == want, "V4 %s resolves to %s (got %r)" % (mid, want, got))

# V5
v1_fable = {"tokens": 1000, "token_unit": "weighted_v1", "model": FABLE}
t, basis = RL.tokens_v2(v1_fable)
check((t, basis) == (2000, "v1_bound"), "V5 a v1 Fable record with no usage converts to the input-ratio bound (%r)"
      % ((t, basis),))
rec = {"tokens": fo, "token_unit": "weighted_v2", "model": OPUS}
check(RL.tokens_v2(rec) == (fo, "v2"), "V5 a v2 record is returned as it is, not weighted again (%r)"
      % (RL.tokens_v2(rec),))
mu = {OPUS: {"inputTokens": 300, "outputTokens": 9000, "cacheReadInputTokens": 400000,
             "cacheCreationInputTokens": 5000, "cacheCreationEphemeral5mInputTokens": 1000,
             "cacheCreationEphemeral1hInputTokens": 4000}}
t, basis = RL.tokens_v2({"tokens": 123456, "token_unit": "weighted_v1", "model": "opus", "model_usage": mu})
check((t, basis) == (fo, "v1_usage"), "V5 a v1 record with stored per-model usage is recomputed from it (%r, want %d)"
      % ((t, basis), fo))
check(RL.tokens_v2({"tokens": None, "token_unit": "weighted_v1", "model": OPUS}) == (None, "unmeasured"),
      "V5 an UNMEASURED v1 record stays UNMEASURED")
msg = raises(RL.tokens_v2, {"tokens": 10, "token_unit": "weighted_v1", "model": "claude-nonesuch-9-9"})
check(msg is not None and "claude-nonesuch-9-9" in msg, "V5 a v1 record of an unknown model raises by name")

# V6
Z = {"input_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 0}
check(RL.run_tokens({"usage": Z}, OPUS) == 0, "V6 all-zero usage is a measured 0")
check(RL.run_tokens({"usage": dict(Z, input_tokens=None)}, OPUS) is None, "V6 a missing usage field is UNMEASURED")
check(RL.run_tokens({"usage": {"input_tokens": 5}}, OPUS) is None, "V6 an absent usage field is UNMEASURED")
check(RL.run_tokens(None) is None and RL.run_tokens({}) is None, "V6 no usage block -> UNMEASURED")
zsyn = {"<synthetic>": {"inputTokens": 0, "outputTokens": 0, "cacheReadInputTokens": 0, "cacheCreationInputTokens": 0}}
check(RL.run_tokens({"modelUsage": dict(zsyn, **mu)}) == fo, "V6 an all-zero <synthetic> entry weighs 0, no raise")
nosplit = {OPUS: {"inputTokens": 0, "outputTokens": 0, "cacheReadInputTokens": 0, "cacheCreationInputTokens": 1000}}
check(RL.run_tokens({"modelUsage": nosplit}) == 2000, "V6 an unsplit cache write weighs at the 1h rate (%r)"
      % RL.run_tokens({"modelUsage": nosplit}))
check(RL.run_tokens({"modelUsage": {OPUS: {"inputTokens": "x"}}}) is None, "V6 a malformed modelUsage is UNMEASURED")

# V7
res = {"usage": dict(Z, input_tokens=300), "modelUsage": mu}
check(RL.run_tokens(res, OPUS) == fo, "V7 modelUsage (whole process) is preferred over the main thread's usage")

print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
