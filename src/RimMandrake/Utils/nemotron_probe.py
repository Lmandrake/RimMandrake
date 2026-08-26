#!/usr/bin/env python3
"""Probe the NVIDIA nemotron family for the three things a delegated seat needs.

The availability question is already answered (nvidia_model_sweep.py): the free-tier
429 wall is MODEL-scoped, and moonshotai/kimi-k3 specifically cannot carry sustained
traffic. This asks the next question of the nemotron family instead:

  1. TOOL CALLING  - does it emit finish_reason=tool_calls with parseable arguments?
                     Without this a model cannot drive a Claude Code seat at all.
  2. SUSTAINED RATE - 20 rapid calls. This is the exact shape that returned 200x5 /
                     429x15 on kimi-k3, so it is directly comparable.
  3. COMPETENCE    - one RimWorld question with a known answer, to catch a model that
                     is fast and available and useless.

Usage:  source ~/.config/secrets/nvidia.env; python3 nemotron_probe.py [--out PATH]
"""
import argparse, json, os, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "https://integrate.api.nvidia.com/v1/chat/completions"
BURST = 20

TOOL = [{"type": "function", "function": {
    "name": "lookup_def",
    "description": "Look up a RimWorld def by defName",
    "parameters": {"type": "object",
                   "properties": {"defName": {"type": "string"},
                                  "defType": {"type": "string"}},
                   "required": ["defName"]}}}]

# A question whose answer is checkable offline: Gun_Autopistol is a ThingDef.
COMPETENCE_Q = ("In RimWorld 1.6, what is the def TYPE (the XML element name) of the "
                "def named Gun_Autopistol? Answer with the type name only.")
COMPETENCE_OK = "thingdef"


def post(body, key, timeout=90):
    req = urllib.request.Request(
        BASE, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.load(r), round(time.time() - t0, 2)
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode()), round(time.time() - t0, 2)
        except Exception:
            return e.code, {}, round(time.time() - t0, 2)
    except Exception as e:
        return 0, {"detail": type(e).__name__}, round(time.time() - t0, 2)


def test_tools(model, key):
    st, d, lat = post({"model": model, "max_tokens": 2048, "tool_choice": "auto",
                       "tools": TOOL,
                       "messages": [{"role": "user", "content":
                                     "Look up the RimWorld def named Gun_Autopistol. "
                                     "You must use the lookup_def tool; do not answer "
                                     "from memory."}]}, key)
    if st != 200:
        return {"status": st, "tool_calls": None,
                "detail": str(d.get("detail", d))[:140], "latency_s": lat}
    ch = (d.get("choices") or [{}])[0]
    msg = ch.get("message") or {}
    calls = msg.get("tool_calls") or []
    args_ok = False
    if calls:
        try:
            a = json.loads(calls[0]["function"]["arguments"])
            args_ok = a.get("defName") == "Gun_Autopistol"
        except Exception:
            args_ok = False
    return {"status": 200, "finish_reason": ch.get("finish_reason"),
            "tool_calls": len(calls), "args_correct": args_ok,
            "reasoning_field": "reasoning_content" in msg,
            "latency_s": lat}


def test_competence(model, key):
    st, d, lat = post({"model": model, "max_tokens": 4096,
                       "messages": [{"role": "user", "content": COMPETENCE_Q}]}, key)
    if st != 200:
        return {"status": st, "detail": str(d.get("detail", d))[:140]}
    msg = ((d.get("choices") or [{}])[0].get("message") or {})
    txt = (msg.get("content") or "")
    return {"status": 200, "answer": txt.strip()[:120],
            "correct": COMPETENCE_OK in txt.lower(),
            "empty_content_thinking_model": txt.strip() == "" and
                                            bool(msg.get("reasoning_content")),
            "latency_s": lat}


def test_burst(model, key, n=BURST):
    ok = bad = other = 0
    first_429_at = None
    for i in range(n):
        st, _d, _l = post({"model": model, "max_tokens": 8,
                           "messages": [{"role": "user", "content": "hi"}]}, key, timeout=45)
        if st == 200:
            ok += 1
        elif st == 429:
            bad += 1
            if first_429_at is None:
                first_429_at = i + 1
        else:
            other += 1
    return {"n": n, "http_200": ok, "http_429": bad, "http_other": other,
            "first_429_at_call": first_429_at}


def probe(model, key):
    rec = {"model": model}
    rec["tools"] = test_tools(model, key)
    if rec["tools"]["status"] != 200:
        rec["verdict"] = "UNAVAILABLE"
        return rec
    rec["competence"] = test_competence(model, key)
    rec["burst"] = test_burst(model, key)
    tc = rec["tools"].get("tool_calls") or 0
    b = rec["burst"]
    if tc == 0:
        rec["verdict"] = "NO_TOOL_CALLING"
    elif b["http_429"] > b["http_200"]:
        rec["verdict"] = "THROTTLED"
    elif not rec["competence"].get("correct"):
        rec["verdict"] = "USABLE_LOW_ACCURACY"
    else:
        rec["verdict"] = "USABLE"
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="research/nemotron_probe.json")
    ap.add_argument("--models", nargs="*", help="override the candidate list")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        sys.exit("NVIDIA_API_KEY unset. source ~/.config/secrets/nvidia.env")

    models = a.models or [
        "nvidia/nemotron-3-ultra-550b-a55b",
        "nvidia/nemotron-3-super-120b-a12b",
        "nvidia/nemotron-3.5-lightning-30b-a3b",
        "nvidia/nemotron-3-nano-30b-a3b",
        "nvidia/nemotron-nano-3-30b-a3b",
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
        "nvidia/llama-3.1-nemotron-ultra-253b-v1",
        "nvidia/llama-3.1-nemotron-70b-instruct",
        "mistralai/mistral-nemotron",
    ]
    out = {"base_url": BASE, "burst": BURST, "candidates": len(models), "results": []}
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for rec in ex.map(lambda m: probe(m, key), models):
            out["results"].append(rec)
            print(f"{rec['verdict']:<20} {rec['model']}", flush=True)
    out["results"].sort(key=lambda r: r["model"])
    with open(a.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
