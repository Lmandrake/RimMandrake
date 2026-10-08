#!/usr/bin/env python3
"""northstar_driver judge -- the VISUAL half of a fast-driver run. WSL side, after the run:

  python3 src/RimMandrake/Utils/northstar_driver/judge_cli.py <results.json> [--model opus] [--jobs 8]

Reads the run's results JSON (cli.py writes `components[].screenshots[]` and `bar_text`), asks
`claude -p` the narrow yes/no question per (component, claimed bar) on that component's LAST
screenshot (modcheck/judge.py's prompt and parser, unchanged), and writes the verdicts back:

  - each visual bar becomes PASS / FAIL with evidence beginning "judge:";
  - a state FAIL stays FAIL (the judge never rescues state);
  - a bar any of whose screenshots could not be judged (missing/unreadable image, judge error,
    throttled twice, UNJUDGEABLE, split vote) stays UNMEASURED -- unless another claim already FAILs it.

Cannot-show bars are asked --repeat-cannot times (default 3) and need unanimity; a split vote is
not a verdict. Calls run --jobs at a time (default 8), --timeout s each (default 180); on the first
throttle reply the rest run serially, and every throttled call is retried serially once.
Recorded under `judge`: model asked for, model(s) the CLI reports, prompt-template sha256, and every
call's image + image sha256 + verdict + full raw reply. The LLM never drives (owner, 2026-09-12).
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
for p in (_UTILS, os.path.join(_UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import harness_run                                                       # noqa: E402
import judge                                                              # noqa: E402
from northstar_driver import PASS, FAIL, UNMEASURED                       # noqa: E402
from northstar_driver import bars as B                                    # noqa: E402
from northstar_driver.cli import to_wsl                                   # noqa: E402

PROMPT_SHA256 = hashlib.sha256(judge._PROMPT.encode("utf-8")).hexdigest()
THROTTLE_RE = re.compile(r"rate.?limit|\b429\b|overloaded|usage limit|too many requests|quota", re.I)
SPLIT = "SPLIT"
_MAGIC = (b"\x89PNG\r\n\x1a\n", b"BM", b"\xff\xd8\xff")


def _p(msg):
    print(msg, flush=True)


# ------------------------------------------------------------------ images

def resolve_image(shot):
    """The file to judge for one recorded screenshot. `screenshot_cell_rect` writes the framed crop
    beside the full frame as `<name>__cell_rect.png`; the crop is what the component framed, so it
    wins when it exists. Returns (path, note)."""
    if isinstance(shot, dict):
        cands = [shot.get("wsl"), to_wsl(shot.get("win")), to_wsl(shot.get("path"))]
    else:
        cands = [to_wsl(shot)]
    for c in [c for c in cands if c]:
        stem, ext = os.path.splitext(c)
        crop = stem + "__cell_rect" + (ext or ".png")
        if not stem.endswith("__cell_rect") and os.path.isfile(crop):
            return crop, "cell_rect crop of %s" % os.path.basename(c)
        if os.path.isfile(c):
            return c, "as recorded"
    return (cands[0] or ""), "no such file"


def image_problem(path):
    """None if the file is a readable image; else why not. Checked BEFORE any judge call: a judge
    handed garbage must not get the chance to describe it."""
    if not path or not os.path.isfile(path):
        return "screenshot file does not exist: %s" % path
    try:
        with open(path, "rb") as f:
            head = f.read(16)
    except OSError as ex:
        return "screenshot unreadable: %s" % ex
    if not head:
        return "screenshot is empty (0 bytes)"
    if not any(head.startswith(m) for m in _MAGIC):
        return "screenshot is not a PNG/BMP/JPEG (header %r)" % head[:8]
    try:
        from PIL import Image
        with Image.open(path) as im:
            im.verify()
    except ImportError:
        pass
    except Exception as ex:
        return "screenshot fails to decode: %s" % ex
    return None


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ------------------------------------------------------------------ the real judge

def claude_runner(model, timeout):
    """callable(prompt_for_path, image) -> (ok, raw). The image is copied into a private temp dir
    used as the subprocess cwd, so the CLI's Read tool reads inside its own working directory."""
    def run(prompt_for, image):
        d = tempfile.mkdtemp(prefix="nsjudge_")
        try:
            local = os.path.join(d, "shot" + (os.path.splitext(image)[1] or ".png"))
            shutil.copyfile(image, local)
            cmd = ["claude", "-p", prompt_for(local), "--output-format", "json",
                   "--model", model, "--allowed-tools", "Read"]
            try:
                r = harness_run.run(cmd, timeout, cwd=d)  # rm-harness.slice, not the seat
            except FileNotFoundError:
                return False, "`claude` not found on PATH"
            except subprocess.TimeoutExpired:
                return False, "claude -p timed out after %ds" % timeout
            if r.returncode != 0:
                return False, (r.stderr.strip() or r.stdout.strip() or "claude -p exited %d" % r.returncode)
            return True, r.stdout
        finally:
            shutil.rmtree(d, ignore_errors=True)
    return run


def is_throttle(ok, raw):
    if ok:
        try:
            env = json.loads(raw)
            if not (isinstance(env, dict) and env.get("is_error")):
                return False
        except (ValueError, TypeError):
            return False
    return bool(THROTTLE_RE.search(str(raw or "")))


def reported_models(raw):
    try:
        env = json.loads(raw)
        return sorted((env.get("modelUsage") or {}).keys()) if isinstance(env, dict) else []
    except (ValueError, TypeError):
        return []


# ------------------------------------------------------------------ planning

def plan_calls(doc, repeat_must=1, repeat_cannot=3):
    """-> (claims, calls). One claim per (component, claimed bar); each claim owns N calls, or none
    when its image is missing/unreadable (the claim is then decided without asking anyone)."""
    texts = doc.get("bar_text") or {}
    claims, calls = [], []
    for c in doc.get("components") or ():
        shots = c.get("screenshots") or []
        for bid in c.get("shows") or ():
            t = texts.get(bid)
            claim = {"component": c.get("name"), "chain": c.get("chain"), "bar": bid,
                     "polarity": (t or {}).get("polarity", "must"), "image": "", "image_note": "",
                     "image_sha256": "", "problem": None, "calls": []}
            claims.append(claim)
            if not t:
                claim["problem"] = "bar not in the validated checklist (bar_text) -- orphaned shows="
                continue
            if not shots:
                claim["problem"] = "component claims this bar but recorded no screenshot"
                continue
            img, note = resolve_image(shots[-1])   # the LAST shot: judge.py's rule
            claim["image"], claim["image_note"] = img, note
            claim["problem"] = image_problem(img)
            if claim["problem"]:
                continue
            claim["image_sha256"] = sha256_file(img)
            n = repeat_cannot if claim["polarity"] == judge.CANNOT else repeat_must
            for k in range(max(1, n)):
                call = {"claim": claim, "k": k, "ok": None, "raw": "", "verdict": None, "why": "",
                        "throttled": False, "attempts": 0, "ms": 0}
                claim["calls"].append(call)
                calls.append(call)
    return claims, calls


def _prompt_for(claim, text):
    framing = judge._FRAMING[claim["polarity"]]

    def f(path):
        return judge._PROMPT.format(image=path, req_id=claim["bar"], req_text=text, framing=framing)
    return f


# ------------------------------------------------------------------ execution

def execute(calls, texts, runner, jobs=8, backoff_s=20.0, log=_p):
    """Parallel first; the first throttle switches the rest to serial; throttled calls get one
    serial retry each. Returns {"parallel", "serial", "throttled", "fallback"}."""
    stop = threading.Event()
    total = len(calls)
    done = [0]
    lock = threading.Lock()
    stats = {"parallel": 0, "serial": 0, "throttled": 0, "fallback": False}

    def one(call, mode):
        cl = call["claim"]
        t0 = time.time()
        call["attempts"] += 1
        ok, raw = runner(_prompt_for(cl, texts[cl["bar"]]["text"]), cl["image"])
        call["ms"] = int((time.time() - t0) * 1000)
        call["ok"], call["raw"] = ok, raw
        call["throttled"] = is_throttle(ok, raw)
        if call["throttled"]:
            stop.set()
            call["verdict"], call["why"] = None, "throttled"
        elif not ok:
            call["verdict"], call["why"] = judge.UNJUDGEABLE, "judge could not run: %s" % str(raw)[:300]
        else:
            call["verdict"], call["why"] = judge._parse_verdict(raw)
        with lock:
            stats[mode] += 1
            if call["throttled"]:
                stats["throttled"] += 1
            done[0] += 1
            log("judge %3d/%d %-8s %-28s %-32s k=%d %s (%.0fs)" % (
                done[0], total, mode, cl["component"][:28], cl["bar"][:32], call["k"],
                call["verdict"] or "THROTTLED", call["ms"] / 1000.0))

    def guarded(call):
        if stop.is_set():
            return call            # deferred: never started, runs serially below
        one(call, "parallel")
        return None

    deferred = []
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
        for f in as_completed([ex.submit(guarded, c) for c in calls]):
            if f.result() is not None:
                deferred.append(f.result())
    retry = [c for c in calls if c["throttled"]]
    if deferred or retry:
        stats["fallback"] = True
        log("judge: throttled -- %d deferred + %d throttled calls now run SERIALLY" % (len(deferred), len(retry)))
        for c in deferred:
            one(c, "serial")
        for c in [c for c in calls if c["throttled"]]:
            if backoff_s:
                time.sleep(backoff_s)
            one(c, "serial")
    return stats


# ------------------------------------------------------------------ verdicts

def decide_claim(claim):
    """-> (outcome, why). outcome: PASS / FAIL / UNMEASURED for this one (component, bar)."""
    if claim["problem"]:
        return UNMEASURED, claim["problem"]
    vs = [c["verdict"] for c in claim["calls"]]
    if any(c["throttled"] for c in claim["calls"]):
        return UNMEASURED, "judge throttled (after serial retry)"
    if any(v == judge.UNJUDGEABLE for v in vs):
        why = next(c["why"] for c in claim["calls"] if c["verdict"] == judge.UNJUDGEABLE)
        return UNMEASURED, "UNJUDGEABLE: %s" % why
    if len(set(vs)) != 1:
        claim["verdict"] = SPLIT
        return UNMEASURED, "split vote %s -- unanimity required" % vs
    v = vs[0]
    claim["verdict"] = v
    why = claim["calls"][0]["why"]
    return (PASS if judge.passes(v, claim["polarity"]) else FAIL), "%s x%d: %s" % (v, len(vs), why)


def apply_verdicts(doc, claims):
    by_bar = {}
    for cl in claims:
        cl["outcome"], cl["outcome_why"] = decide_claim(cl)
        by_bar.setdefault(cl["bar"], []).append(cl)
    for row in doc.get("bars") or ():
        if not row.get("visual"):
            continue
        st0 = row.get("state_status", row["status"])
        sev = row.get("state_evidence", row["evidence"])
        row.setdefault("state_status", st0)
        row.setdefault("state_evidence", sev)
        cls = by_bar.get(row["id"], [])
        parts = ["%s=%s (%s)" % (c["component"], c["outcome"], c["outcome_why"][:200]) for c in cls]
        outs = [c["outcome"] for c in cls]
        if st0 == FAIL:
            row["status"] = FAIL
            row["evidence"] = "state FAIL [%s]; judge: %s" % (sev, "; ".join(parts) or "not asked")
        elif not cls:
            row["status"] = UNMEASURED
            row["evidence"] = "judge: no component claim to judge [%s]" % sev
        elif FAIL in outs:
            row["status"] = FAIL
            row["evidence"] = "judge: " + "; ".join(parts)
        elif UNMEASURED in outs or st0 != PASS:
            row["status"] = UNMEASURED
            row["evidence"] = "judge: incomplete -- " + "; ".join(parts) + (
                "" if st0 == PASS else " [state %s: %s]" % (st0, sev))
        else:
            row["status"] = PASS
            row["evidence"] = "judge: " + "; ".join(parts)
    doc["summary"] = B.summarize(doc.get("bars") or [])
    doc["all_green"] = B.all_green(doc.get("bars") or [], doc.get("expected") or None)
    return doc


def judge_doc(doc, runner, model="(mock)", jobs=8, repeat_must=1, repeat_cannot=3, timeout=180,
              backoff_s=20.0, log=_p):
    texts = doc.get("bar_text") or {}
    claims, calls = plan_calls(doc, repeat_must, repeat_cannot)
    log("judge: %d claim(s), %d call(s), %d undecidable before asking; jobs=%d model=%s" % (
        len(claims), len(calls), sum(1 for c in claims if c["problem"]), jobs, model))
    t0 = time.time()
    stats = execute(calls, texts, runner, jobs=jobs, backoff_s=backoff_s, log=log)
    apply_verdicts(doc, claims)
    models = sorted({m for c in calls for m in reported_models(c["raw"])})
    doc["judge"] = {
        "judged_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model_requested": model, "models_reported": models,
        "prompt_sha256": PROMPT_SHA256, "repeat_must": repeat_must, "repeat_cannot": repeat_cannot,
        "jobs": jobs, "timeout_s": timeout, "wall_s": round(time.time() - t0, 1), "stats": stats,
        "claims": [{k: v for k, v in cl.items() if k != "calls"} | {
            "calls": [{"k": c["k"], "verdict": c["verdict"], "why": c["why"], "ok": c["ok"],
                       "throttled": c["throttled"], "attempts": c["attempts"], "ms": c["ms"],
                       "raw": c["raw"]} for c in cl["calls"]]} for cl in claims],
    }
    return doc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("results")
    ap.add_argument("--out", help="default: rewrite the results file in place")
    ap.add_argument("--model", default="opus", help="pinned judge model (claude --model)")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--repeat-must", type=int, default=1)
    ap.add_argument("--repeat-cannot", type=int, default=3)
    ap.add_argument("--only-chain", action="append", help="judge only these chains (repeatable)")
    a = ap.parse_args(argv)
    with open(a.results, encoding="utf-8") as f:
        doc = json.load(f)
    if not doc.get("components"):
        _p("refused: %s carries no components[] -- written by a driver before screenshot recording"
           % a.results)
        return 2
    if a.only_chain:
        doc["components"] = [c for c in doc["components"] if c.get("chain") in a.only_chain]
    judge_doc(doc, claude_runner(a.model, a.timeout), model=a.model, jobs=a.jobs,
              repeat_must=a.repeat_must, repeat_cannot=a.repeat_cannot, timeout=a.timeout)
    out = a.out or a.results
    B.write_results(out, doc)
    s = doc["summary"]
    _p("%s: %s  PASS=%s FAIL=%s UNMEASURED=%s  -> %s" % (
        doc.get("mod"), "GREEN" if doc["all_green"] else "NOT GREEN", s[PASS], s[FAIL], s[UNMEASURED], out))
    return 0 if doc["all_green"] else 1


if __name__ == "__main__":
    sys.exit(main())
