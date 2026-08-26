#!/usr/bin/env python3
"""Sweep every model on the NVIDIA API catalog for availability and throttle shape.

Answers one question: is the 429 wall we hit on moonshotai/kimi-k3 specific to that
model, or does the whole free tier behave that way?

Guards against the obvious confound - an account-level bucket draining mid-sweep and
making late models look throttled - by interleaving a control model every CONTROL_EVERY
models and recording its status alongside.

Usage:  NVIDIA_API_KEY=nvapi-... python3 nvidia_model_sweep.py [--out PATH] [--burst N]
"""
import argparse, json, os, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://integrate.api.nvidia.com/v1"
CONTROL = "meta/llama-3.1-8b-instruct"
CONTROL_EVERY = 8
WORKERS = 4

def call(model, key, max_tokens=8, timeout=45):
    """Return (http_status, latency_s, note). status 0 means transport failure."""
    body = json.dumps({
        "model": model, "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": "hi"}],
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            r.read()
            return r.status, round(time.time() - t0, 2), ""
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = json.loads(e.read().decode()).get("detail", "")[:120]
        except Exception:
            pass
        return e.code, round(time.time() - t0, 2), detail
    except Exception as e:
        return 0, round(time.time() - t0, 2), type(e).__name__

def list_models(key):
    req = urllib.request.Request(f"{BASE}/models",
                                 headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return sorted(m["id"] for m in json.load(r).get("data", []))

def probe(model, key, burst):
    """One availability call; if it lands, burst to measure the throttle."""
    status, lat, note = call(model, key)
    rec = {"model": model, "first": status, "latency_s": lat, "note": note,
           "burst_200": None, "burst_429": None, "burst_other": None}
    if status == 200 and burst > 1:
        ok, bad, other = 1, 0, 0
        for _ in range(burst - 1):
            s, _l, _n = call(model, key)
            if s == 200: ok += 1
            elif s == 429: bad += 1
            else: other += 1
        rec.update(burst_200=ok, burst_429=bad, burst_other=other)
    return rec

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="nvidia_model_sweep.json")
    ap.add_argument("--burst", type=int, default=5,
                    help="calls per available model, to measure throttle")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        sys.exit("NVIDIA_API_KEY unset - source ~/.config/secrets/nvidia.env")

    models = list_models(key)
    if a.limit:
        models = models[:a.limit]
    print(f"{len(models)} models on the catalog; burst={a.burst}", flush=True)

    results, controls = [], []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(probe, m, key, a.burst): m for m in models}
        for i, f in enumerate(as_completed(futs), 1):
            rec = f.result()
            results.append(rec)
            if i % CONTROL_EVERY == 0:
                cs, cl, _ = call(CONTROL, key)
                controls.append({"after_n": i, "control_status": cs})
                print(f"  [{i}/{len(models)}] control {CONTROL} -> {cs}", flush=True)

    results.sort(key=lambda r: r["model"])
    avail = [r for r in results if r["first"] == 200]
    drained = [c for c in controls if c["control_status"] != 200]

    out = {
        "base_url": BASE, "burst": a.burst, "n_models": len(models),
        "control_model": CONTROL, "control_readings": controls,
        "control_ever_failed": bool(drained),
        "summary": {
            "available_200": len(avail),
            "throttled_429": sum(1 for r in results if r["first"] == 429),
            "not_found_404": sum(1 for r in results if r["first"] == 404),
            "other": sum(1 for r in results if r["first"] not in (200, 429, 404)),
        },
        "results": results,
    }
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=2)

    s = out["summary"]
    print(f"\n200={s['available_200']}  429={s['throttled_429']}  "
          f"404={s['not_found_404']}  other={s['other']}")
    if drained:
        print(f"WARNING: control model failed {len(drained)}x - "
              f"account-level drain may confound late results")
    clean = [r for r in avail if r["burst_429"] == 0]
    print(f"of {len(avail)} available, {len(clean)} sustained a {a.burst}-call burst "
          f"with zero 429")
    print(f"-> {a.out}")

if __name__ == "__main__":
    main()
