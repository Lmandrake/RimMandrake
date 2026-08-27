#!/usr/bin/env python3
"""Find the LARGEST job a cheap model still does reliably - not whether it fails at a big one.

Owner's reframe, 2026-08-26: "determine the max job size these lesser agents can handle,
rather than watching them fail at something big." A pass/fail on one hard task tells you
nothing actionable. A ceiling tells you how to SIZE every future worker prompt.

Two axes, each with exact ground truth taken from this repo's own def XML:

  --axis haystack   ONE question, growing input.  How much text can it read?
  --axis questions  Fixed small input, growing K.  How many demands per call?

A size PASSES if every repeat at that size is exactly right. The ceiling is the largest
passing size, and the first failing size is reported beside it - a ceiling with no
failure above it has not been established.

Usage:  source ~/.config/secrets/nvidia.env
        nemotron_ceiling.py --axis questions [--model M] [--repeats 3]
"""
import argparse, json, os, random, re, sys, time
import urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "https://integrate.api.nvidia.com/v1/chat/completions"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
SRC = "src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml"

HAYSTACK_SIZES = [8000, 20000, 50000, 120000]
QUESTION_SIZES = [2, 4, 8, 16, 24]
# 🔑 Retrieving ONE needle from 120k chars passed; classifying EVERY element of a
# 400-line file failed. Those are different jobs. This axis grows the number of items
# that must ALL be examined - the shape that actually broke.
ENUMERATE_SIZES = [4, 8, 16, 24, 32]


def load_pairs():
    t = open(os.path.join(ROOT, SRC), encoding="utf-8").read()
    return re.findall(r"<defName>(\w+)</defName>.*?<combatPower>([0-9]+)</combatPower>",
                      t, re.S), t


def post(body, key, timeout=240):
    req = urllib.request.Request(
        BASE, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"detail": type(e).__name__}


def call(msg, model, key, retries=3):
    for i in range(retries):
        st, d = post({"model": model, "max_tokens": 8192, "temperature": 0,
                      "messages": [{"role": "user", "content": msg}]}, key)
        if st == 200:
            c = ((d.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
            u = d.get("usage", {})
            return c, u.get("prompt_tokens"), u.get("completion_tokens")
        if st == 429:
            return "", None, None            # quota wall - never retried
        time.sleep(4 * (i + 1))
    return "", None, None


# 🔑 The answer must come LAST and be machine-shaped, or a reasoning model's
# chain-of-thought buries it. Measured: a correct analysis that never reaches its own
# answer line scores as a failure, and that is the harness lying, not the model.
# ⚠️ Defect measured 2026-08-26: a shape written as "<1> | <2>" was ECHOED BACK
# LITERALLY by the model instead of filled in - scoring as a capability failure when
# the prompt was at fault. Describe the shape in words; never hand it angle brackets.
TAIL = ("\n\nThink first if you must, but your LAST line must be exactly:\n"
        "ANSWER: {shape}\n"
        "Substitute real numbers. Do not copy this template. Nothing after that line.")


def q_haystack(pairs, text, size, rng):
    body = text[:size]
    inside = [(d, p) for d, p in pairs if f"<defName>{d}</defName>" in body]
    if not inside:
        return None
    d, p = rng.choice(inside)
    return (f"XML follows.\n---\n{body}\n---\n"
            f"What is the <combatPower> of the PawnKindDef whose defName is {d}?"
            + TAIL.format(shape="the number"), [p], size, d)


def q_questions(pairs, text, k, rng):
    body = text[:20000]
    inside = [(d, p) for d, p in pairs if f"<defName>{d}</defName>" in body]
    if len(inside) < k:
        return None
    picked = rng.sample(inside, k)
    names = "\n".join(f"  {i+1}. {d}" for i, (d, _) in enumerate(picked))
    shape = " | ".join("the number for #%d" % (i + 1) for i in range(k))
    return (f"XML follows.\n---\n{body}\n---\n"
            f"Give the <combatPower> of each of these {k} PawnKindDefs, in this order:\n"
            f"{names}" + TAIL.format(shape=shape),
            [p for _, p in picked], k, f"{k} defs")


def q_enumerate(pairs, text, n, rng):
    """EXHAUSTIVE: every one of n defs must be examined, and the answer is a COUNT.
    A miss anywhere changes the number, so partial credit is impossible - which is
    exactly the property a census needs and a retrieval test does not have."""
    picked = pairs[:n]
    if len(picked) < n:
        return None
    block = "\n".join(f"  <PawnKindDef><defName>{d}</defName>"
                       f"<combatPower>{p}</combatPower></PawnKindDef>" for d, p in picked)
    thresh = 120
    truth = sum(1 for _, p in picked if int(p) > thresh)
    return (f"Below are {n} PawnKindDef entries.\n---\n{block}\n---\n"
            f"How many of these {n} entries have a combatPower strictly greater than "
            f"{thresh}? Examine every entry."
            + TAIL.format(shape="the count"), [str(truth)], n, f"{n} entries")


def grade(raw, expect):
    m = None
    for line in reversed([l.strip() for l in (raw or "").splitlines() if l.strip()]):
        m = re.search(r"ANSWER:\s*(.+)", line)
        if m:
            break
    if not m:
        return False, "no ANSWER line", ""
    got = re.findall(r"\d+", m.group(1))
    return (got == expect), ("ok" if got == expect else "wrong"), m.group(1)[:90]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--axis", choices=("haystack", "questions", "enumerate"),
                    default="questions")
    ap.add_argument("--model", default="nvidia/nemotron-3.5-lightning-30b-a3b")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        sys.exit("NVIDIA_API_KEY unset. source ~/.config/secrets/nvidia.env")

    pairs, text = load_pairs()
    sizes = {"haystack": HAYSTACK_SIZES, "questions": QUESTION_SIZES,
             "enumerate": ENUMERATE_SIZES}[a.axis]
    build = {"haystack": q_haystack, "questions": q_questions,
             "enumerate": q_enumerate}[a.axis]

    jobs = []
    for size in sizes:
        for r in range(a.repeats):
            spec = build(pairs, text, size, random.Random(1000 + size * 10 + r))
            if spec:
                jobs.append((size, r, spec))

    def run(job):
        size, r, (msg, expect, _s, label) = job
        raw, pt, ct = call(msg, a.model, key)
        ok, why, got = grade(raw, expect)
        print(f"  size {str(size).rjust(6)}  rep {r}  "
              f"{'PASS' if ok else 'FAIL'}  {why:12} prompt_tok={pt} got={got[:40]!r}",
              flush=True)
        return {"size": size, "rep": r, "ok": ok, "why": why, "label": label,
                "expect": expect, "got": got, "prompt_tokens": pt,
                "completion_tokens": ct}

    print(f"{a.model}  axis={a.axis}  {len(jobs)} calls", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=6) as ex:
        rows = list(ex.map(run, jobs))

    by = {}
    for r in rows:
        by.setdefault(r["size"], []).append(r["ok"])
    ceiling, first_fail = None, None
    for s in sizes:
        v = by.get(s, [])
        if v and all(v):
            ceiling = s
        elif v and first_fail is None:
            first_fail = s
    # 🔑 A ceiling only means something if failure is MONOTONIC. Passing above a size
    # you failed below means the failures are noise, and there is no ceiling to report.
    monotonic = (first_fail is None or ceiling is None or ceiling < first_fail)
    print(f"\n  {a.model}  axis={a.axis}  wall {round(time.time()-t0,1)}s")
    for s in sizes:
        v = by.get(s, [])
        # 🔴 no jobs built != tested and passed. Saying 0/0 is the instrument reporting
        # ignorance as a measurement, which is the whole failure this repo keeps paying
        # for. Name it UNMEASURED and say why.
        print(f"    size {str(s).rjust(6)}: "
              + (f"{sum(v)}/{len(v)}" if v else "UNMEASURED (corpus too small at this size)"))
    print(f"\n  CEILING (largest all-pass): {ceiling}")
    print(f"  first failing size:         {first_fail}")
    if not monotonic:
        print("  🔴 NOT A CEILING - a larger size passed after a smaller one failed, so "
              "the failures are NOISE, not a size limit. Raise --repeats and re-run "
              "before reporting any number from this.")
    if first_fail is None:
        print("  ⚠️  NO FAILURE OBSERVED - the ceiling is at or above the largest size "
              "tested, and is therefore NOT established. Raise the sizes.")
    if a.out:
        with open(os.path.join(ROOT, a.out), "w") as f:
            json.dump({"model": a.model, "axis": a.axis, "ceiling": ceiling,
                       "first_fail": first_fail, "rows": rows}, f, indent=2)
        print(f"  wrote {a.out}")


if __name__ == "__main__":
    main()
