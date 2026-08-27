#!/usr/bin/env python3
"""Dispatch a bounded read-only question across many files to cheap NVIDIA workers.

The rules from skills/agent-fanout-research/SKILL.md are ENFORCED here rather than
left to whoever writes the prompt, because every one of them was learned by paying:

  * an abstention clause is appended to every worker prompt      (fabrication 3/7 -> 0-1/7)
  * the question is REFUSED if it states a fact the worker should find
  * workers return CANDIDATES in a fixed row shape, never prose
  * 503 is transient and retried; 429 is a quota wall and is NOT

⛔ Read-only by construction: a worker is handed text and returns text. It has no tools,
no filesystem and no way to write anything.

Usage:
    source ~/.config/secrets/nvidia.env
    nemotron_fanout.py --glob 'src/Jawa/**/*.xml' \\
        --question "Does this file contain a PatchOperationReplace whose xpath targets
                    pawnGroupMakers? If so give the line number." \\
        [--model M] [--workers 8] [--out PATH] [--max-chars 40000]
"""
import argparse, glob as globmod, json, os, re, sys, time
import urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "https://integrate.api.nvidia.com/v1/chat/completions"
# 🔴 Measured 2026-08-26: the binding limit on a cheap worker is COMPLETION tokens spent
# reasoning, never input size. One 400-line repo file at 7.8k INPUT tokens scored 0/3,
# every attempt stopping dead on the completion cap. Give it room, then check whether it
# used all of it - a reply that stopped exactly at the cap is a truncation, not an answer.
MAX_OUT = 8192
ABSTAIN = "NOT IN THE PROVIDED TEXT"

# 🔑 A question that TELLS the worker a fact makes every worker wrong the same way.
# Correlated error comes back looking like consensus - refuse it at the door.
ASSERTS = re.compile(
    r"\b(given|since|because|as we know|note that|recall that|the answer is|"
    r"it is known that|we established|assume)\b", re.I)

PROMPT = """You are one worker in a fan-out. You see ONE file and nothing else.

FILE: {path}
------------------------------------------------------------
{body}
------------------------------------------------------------

QUESTION: {question}

Answer ONLY from the text above. You have no other knowledge of this repository, and
anything you cannot see in that text you do not know.

🔴 If the text above does not contain the answer, reply with exactly this and nothing
else: {abstain}

Otherwise reply in EXACTLY this shape, no prose before or after:
VERDICT: <one line, under 20 words>
EVIDENCE: <line number>: <quote of at most 15 words, copied verbatim from the file>
"""


def post(body, key, timeout=180):
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


def ask(path, body, question, model, key, retries=4):
    msg = PROMPT.format(path=path, body=body, question=question, abstain=ABSTAIN)
    for attempt in range(retries):
        st, d = post({"model": model, "max_tokens": MAX_OUT, "temperature": 0,
                      "messages": [{"role": "user", "content": msg}]}, key)
        if st == 200:
            txt = ((d.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
            ct = (d.get("usage") or {}).get("completion_tokens")
            return {"path": path, "http": 200, "raw": txt.strip(),
                    "completion_tokens": ct, "truncated": ct is not None and ct >= MAX_OUT}
        # 🔴 503 is shared-capacity and transient. 429 is a per-model quota wall and
        # retrying it makes it worse - stop and report, so the caller can see a stall.
        if st == 429:
            return {"path": path, "http": 429, "raw": "", "error": "quota wall - not retried"}
        time.sleep(4 * (attempt + 1))
    return {"path": path, "http": st, "raw": "", "error": f"HTTP {st} after {retries}"}


def classify(raw):
    """🔴 Parse the TAIL only. Two defects measured 2026-08-26, both dangerous:

    1. `max_tokens=700` truncated the model mid-reasoning, so a CORRECT analysis never
       reached its own VERDICT line and scored MALFORMED. The worker was right; the
       harness threw the answer away.
    2. Matching the abstention phrase ANYWHERE matched the model merely *considering*
       it while reasoning. That turns "I did not finish" into a confident "nothing
       here" - a false negative that reads exactly like a clean sweep. ⚠️ This is the
       worst failure a census can have, because 57 abstentions look like a result.
    """
    if not raw:
        return "ERROR", "", ""
    lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
    if not lines:
        return "ERROR", "", ""
    tail = "\n".join(lines[-6:])          # the answer block, never the reasoning
    v = re.search(r"VERDICT:\s*(.+)", tail)
    # 🔴 A model that answers the question in the NEGATIVE fills in the VERDICT shape
    # rather than using the abstention token - "VERDICT: No Replace targets
    # pawnGroupMakers" is a correct NO, and scoring it a HIT manufactures a false
    # positive out of a right answer. Measured 2026-08-26: 1 of 60 rows, and it was
    # the only "fabrication" in the sweep.
    if v and re.match(r"\s*(no\b|none\b|does not|doesn't|no such|not present|absent)",
                      v.group(1), re.I):
        return "NEGATIVE", v.group(1).strip()[:120], ""
    e = re.search(r"EVIDENCE:\s*(.+)", tail)
    if v:
        return "HIT", v.group(1).strip()[:120], (e.group(1).strip()[:120] if e else "")
    # abstention counts only as the model's FINAL word, not a passing thought
    if ABSTAIN in lines[-1].upper():
        return "ABSTAIN", "", ""
    if ABSTAIN in tail.upper():
        return "ABSTAIN", "", ""
    return "MALFORMED", lines[-1][:100], ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", required=True)
    ap.add_argument("--question", required=True)
    ap.add_argument("--model", default="nvidia/nemotron-3.5-lightning-30b-a3b",
                    help="default is the fabrication-resistant one, not the fastest")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--max-chars", type=int, default=40000)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--keep-comments", action="store_true",
                    help="do NOT strip XML/# comments. Default strips them: 63%% of a "
                         "real patch file is commentary, and commentary is what the "
                         "worker burns its completion budget narrating.")
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        sys.exit("NVIDIA_API_KEY unset. source ~/.config/secrets/nvidia.env")

    m = ASSERTS.search(a.question)
    if m:
        sys.exit(f"REFUSED: the question asserts a fact ({m.group(0)!r}). A fact stated in "
                 f"a shared fan-out prompt makes every worker wrong the SAME way, and "
                 f"correlated error reads as consensus. Ask, do not tell.")

    paths = sorted(p for p in globmod.glob(a.glob, recursive=True) if os.path.isfile(p))
    if a.limit:
        paths = paths[:a.limit]
    if not paths:
        sys.exit(f"no files matched {a.glob!r}")
    print(f"{len(paths)} files -> {a.model} x{a.workers}", flush=True)

    def one(p):
        with open(p, encoding="utf-8", errors="replace") as f:
            body = f.read(a.max_chars)
        if not a.keep_comments:
            body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
            body = re.sub(r"\n\s*\n+", "\n", body)
        # 1-indexed line numbers so EVIDENCE is checkable against the real file
        body = "\n".join(f"{i+1}: {l}" for i, l in enumerate(body.splitlines()))
        r = ask(p, body, a.question, a.model, key)
        r["verdict_kind"], r["verdict"], r["evidence"] = classify(r["raw"])
        # 🔴 A truncated reply must NEVER be scored as an abstention. "It ran out of
        # budget mid-thought" and "it looked and found nothing" are opposite facts, and
        # conflating them turns an unfinished sweep into a clean bill of health.
        if r.get("truncated") and r["verdict_kind"] != "HIT":
            r["verdict_kind"] = "TRUNCATED"
        print(f"  {r['verdict_kind']:9} {p}", flush=True)
        return r

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        rows = list(ex.map(one, paths))

    counts = {}
    for r in rows:
        counts[r["verdict_kind"]] = counts.get(r["verdict_kind"], 0) + 1
    out = {"model": a.model, "question": a.question, "glob": a.glob,
           "wall_s": round(time.time() - t0, 1), "counts": counts, "rows": rows}
    if a.out:
        with open(a.out, "w") as f:
            json.dump(out, f, indent=2)
    print(f"\n  {json.dumps(counts)}  in {out['wall_s']}s")
    if a.out:
        print(f"  wrote {a.out}")
    print("  ⚠️  These are CANDIDATES. Confirm every row before it lands in a doc.")
    if not a.keep_comments:
        print("  ⚠️  Comments were STRIPPED, so every EVIDENCE line number is relative to "
              "the stripped body and will NOT match the file on disk. Re-locate by the "
              "quoted text, never by the number. --keep-comments preserves the numbers "
              "and costs you the accuracy they were bought with.")


if __name__ == "__main__":
    main()
