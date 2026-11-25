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

THE ONE SCENE-LOOK JUDGE (RIMMANDRAKE_FOLD_FRAME_JUDGE_INTO_PRELOOK; owner pick 11, 2026-11-12: one item, one judge).
This is the entry point of design/RimMandrake/scene_look_judge_brief.md for north-star frames, both passes:
  pass 1  before any bar is asked, ONE fresh `claude -p` per distinct capture gets the brief's open question and nothing
          else (no bar id, no bar text, no checklist). Its ODD or WRONG is a DOUBT listed on every bar row judged on
          that capture (`doubts[]`, and "pass-1 doubt" in the evidence) and in `judge.open_look`; it stands until the
          owner or a state read answers it. It never changes a bar's status: the bar's promise is what passes or fails
          (standing_rulings.md, "The judge refuses flaws, not polish"). COULD NOT SEE, an unreadable answer or a judge
          that could not run is "could not look", counted with its cause, never a doubt and never a verdict.
  pass 2  the statement prompt above, a DIFFERENT fresh call that never sees pass 1: the bar's text is its one
          expectation sentence. Unchanged, so bar verdicts carry their old meaning.
`--no-open-look` skips pass 1 (recorded as not run, with why).

REFUSAL RECORDS (RIMMANDRAKE_EMIT_REFUSAL_RECORDS_FROM_NORTHSTAR_FRAME_FAILS; standing_rulings.md §A refusal carries its
path to pass). After pass 2, each bar the judge answered NO (a must) or YES (a cannot), or UNJUDGEABLE, gets ONE fresh
follow-up call (RECORD_PROMPT) for its would_pass, smallest_fix and criterion verdict; a YES costs nothing extra. One
contract verdict per run (family scene_look_judge_brief: the passed bars and these refusals, given the bar texts and the
judged captures) goes through refusal_contract.submit and its result is kept as judge.contract. A bar whose judge could
not run (a dead call, a throttle, no image, a split vote) is "could not look" and one whose follow-up could not run is
"could not record": neither is a refusal, a pass or a malformed record, and a run with any bar it could not record
submits nothing. Bar statuses are unchanged by any of this. Known limit: the follow-up is staged with the first refusing
capture only; another capture of the same bar reaches it by name and reason, not by its pixels.
`--no-records` skips it (recorded as not run, with why).
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
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "rimflow"))  # rimflow/effort.py, appended: shadows nothing
import effort as EF  # noqa: E402  the one effort table (RIMMANDRAKE_PASS_EFFORT_ON_EVERY_LAUNCH_STEVEDESKTOP_RAN_MEDIUM)

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
for p in (_UTILS, os.path.join(_UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import harness_run                                                       # noqa: E402
import rmpaths                                                            # noqa: E402
import judge                                                              # noqa: E402
from northstar_driver import PASS, FAIL, UNMEASURED                       # noqa: E402
from northstar_driver import bars as B                                    # noqa: E402
from northstar_driver.cli import to_wsl                                   # noqa: E402

CLAUDE = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")  # systemd's PATH lacks ~/.local/bin (OPS_TIMER_REPAIR_PRXC)

PROMPT_SHA256 = hashlib.sha256(judge._PROMPT.encode("utf-8")).hexdigest()

# Pass 1 of scene_look_judge_brief.md, verbatim in its question (owner, 2026-11-12: "You are human player looking at this
# test from a game playing point of view... first, does anything look odd?"). Bar-blind on purpose.
OPEN_PROMPT = """\
Read the image at this path: {image}

You are a RimWorld player who has just walked up to this part of the map. Does anything look odd?

Describe what you see in plain words, then answer with a single JSON object as the LAST thing you write:

  {{"look": "EXPECTED" | "ODD" | "WRONG" | "COULD NOT SEE", "where": "<the object and where it is>",
    "first_noticed": "<the single thing a player would notice first>"}}

EXPECTED: nothing looks odd. ODD: something looks strange. WRONG: something is clearly broken. COULD NOT SEE: too
small, too zoomed out or covered to tell; that is a real answer, never a guess.
"""
OPEN_PROMPT_SHA256 = hashlib.sha256(OPEN_PROMPT.encode("utf-8")).hexdigest()

# The refusal record's follow-up (scene_look_judge_brief.md "Every refusal is a record"): asked only of a bar a judge
# refused or could not judge, by a fresh call shown the bar, its capture and that judge's reason.
RECORD_PROMPT = """\
Read the image at this path: {image}

A judge looking at this RimWorld screenshot was asked whether this statement is true of it:

  "{bar}"

It answered {verdict}, because: {why}{others}

{goal} Write the refusal's path to pass. Answer with a single JSON object as the LAST thing you write:

  {{"would_pass": "<what a capture that passes would show, concretely>",
    "smallest_fix": {{"what": "<the smallest change to the mod or the capture that would get there>",
                      "attainable": "yes" | "no", "cost": "edit" | "rerun" | "new instrument" | "owner"}},
    "criterion_verdict": "sound" | "flawed" | "unattainable",
    "criterion_why": "<one sentence: is the statement a fair bar a correct mod could pass, that a player would notice?>"}}

When the image could not be judged, the fix is a re-shot capture (cost "rerun") that shows what the statement is about.
"""
RECORD_PROMPT_SHA256 = hashlib.sha256(RECORD_PROMPT.encode("utf-8")).hexdigest()
RECORD_GOAL = {judge.MUST: "The statement is a requirement: a passing capture shows it TRUE.",
               judge.CANNOT: "The statement describes a defect the owner would reject: a passing capture shows it is "
                             "NOT true (the defect is absent)."}
RECORD_FAMILY = "scene_look_judge_brief"
OPEN_LOOKS = ("EXPECTED", "ODD", "WRONG", "COULD NOT SEE")
THROTTLE_RE = re.compile(r"rate.?limit|\b429\b|overloaded|usage limit|too many requests|quota", re.I)
SPLIT = "SPLIT"
# Captures are staged under agent storage, never tempfile's /tmp: on archmagi /tmp is an 18G tmpfs that
# workers' mutation copies filled to 97%, and every judge call died ENOSPC (NSJUDGE_TMPDIR_FIX_TMPFS_FULL_OF_MUTANTS).
MIN_FREE_BYTES = 512 << 20


def stage_root():
    """`<rm data root>/scratch/nsjudge`, created on demand; RmDataRootUnset propagates by name."""
    d = rmpaths.rm_path("scratch", "nsjudge")
    d.mkdir(parents=True, exist_ok=True)
    return str(d)


def stage_problem(root, image, min_free=MIN_FREE_BYTES):
    """None when `root` has room for a copy of `image` plus `min_free`; else the refusal text."""
    try:
        need = os.path.getsize(image) + min_free
        free = shutil.disk_usage(root).free
    except OSError as e:
        return "stage preflight failed on %s: %s" % (root, e)
    if free < need:
        return "ENOSPC preflight: %s has %d MiB free, needs %d MiB" % (root, free >> 20, need >> 20)
    return None
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
        with Image.open(path) as im:             # verify() checks structure only: decode the pixels too (truncated files)
            im.load()
    except ImportError:
        return "cannot decode the screenshot: Pillow is not installed (a header check is not a readable image)"
    except Exception as ex:
        return "screenshot fails to decode: %s" % ex
    return None


def image_px(path):
    """[width, height] of the exact file judged, or None when it cannot be read (no Pillow): its provenance beside the verdict."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            return list(im.size)
    except Exception:                            # noqa: BLE001 - provenance only, never a verdict
        return None


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ------------------------------------------------------------------ the real judge

def claude_runner(model, timeout):
    """callable(prompt_for_path, image) -> (ok, raw). The image is copied into a private dir under
    stage_root() used as the subprocess cwd, so the CLI's Read tool reads inside its own working
    directory. A stage without room refuses before copying (ok=False, never a verdict)."""
    def run(prompt_for, image):
        root = stage_root()
        why = stage_problem(root, image)
        if why:
            return False, why
        d = tempfile.mkdtemp(prefix="nsjudge_", dir=root)
        try:
            local = os.path.join(d, "shot" + (os.path.splitext(image)[1] or ".png"))
            shutil.copyfile(image, local)
            cmd = [CLAUDE, "-p", prompt_for(local), "--output-format", "json",
                   "--model", model, "--dangerously-skip-permissions", "--allowed-tools", "Read"] + EF.effort_args(model)
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
                     "image_sha256": "", "image_px": None, "problem": None, "calls": []}
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
            claim["image_px"] = image_px(img)
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
        try:
            ok, raw = runner(_prompt_for(cl, texts[cl["bar"]]["text"]), cl["image"])
        except rmpaths.RmDataRootUnset:
            raise                                    # the documented by-name failure
        except Exception as ex:                      # noqa: BLE001 - a staging or subprocess error: the judge could not run
            ok, raw = False, "%s: %s" % (type(ex).__name__, ex)
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


# ------------------------------------------------------------------ pass 1: the open look

def _depth_before(text, pos):
    """Open-brace depth at `pos`, counting braces outside JSON strings only."""
    depth, in_str, esc = 0, False, False
    for ch in text[:pos]:
        if in_str:
            esc, in_str = (False, in_str) if esc else (ch == "\\", ch != '"')
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth = max(0, depth - 1)
    return depth


def _final_object(text):
    """-> (the JSON object that ENDS the answer text, None) or (None, why it is unreadable). An earlier object is never
    salvaged: the final answer is the answer."""
    if not isinstance(text, str) or not text.strip():
        return None, "unreadable answer: no result text"
    tail = text.rstrip().rstrip("`").rstrip()            # a closing code fence may follow the object
    if not tail.endswith("}"):
        return None, "unreadable answer: the answer does not end with its JSON object"
    end = len(tail) - 1
    dec = json.JSONDecoder()
    obj = None
    for st in [m.start() for m in re.finditer(r"\{", text[:end + 1])]:
        try:
            o, stop = dec.raw_decode(text, st)
        except ValueError:
            continue
        if stop == end + 1:              # the object that ENDS the answer, decoded string-aware (stop is an absolute index)
            if _depth_before(text, st) == 0:     # and a top-level one: never an inner object of a broken outer answer
                obj = o
            break
    if not isinstance(obj, dict):
        return None, "unreadable answer: the final JSON object does not decode"
    return obj, None


def parse_open(raw):
    """-> (look, where, first_noticed, cause). look is one of OPEN_LOOKS, or None with the cause: an error or throttle
    envelope, no result text, or a LAST JSON object that is missing, unreadable or not a look (an earlier object is never
    salvaged: the final answer is the answer)."""
    try:
        e = json.loads(raw)
    except (ValueError, TypeError):
        return None, "", "", "unreadable answer: the CLI envelope is not JSON"
    if not isinstance(e, dict):
        return None, "", "", "unreadable answer: the CLI envelope is not an object"
    if e.get("is_error") or is_throttle(True, raw):
        return None, "", "", "the judge could not run: %s" % str(e.get("result") or e.get("error") or "error envelope")[:300]
    obj, cause = _final_object(e.get("result"))
    if cause:
        return None, "", "", cause
    look = str(obj.get("look", "")).strip().upper().replace("_", " ")
    if look not in OPEN_LOOKS:
        return None, "", "", "unreadable answer: look %r is not one of %s" % (obj.get("look"), "/".join(OPEN_LOOKS))
    return look, str(obj.get("where") or ""), str(obj.get("first_noticed") or ""), None


def open_look(claims, runner, jobs=8, log=_p):
    """Pass 1 over every distinct capture the claims will judge (one call each, bar-blind). -> the record."""
    by_img = {}
    for cl in claims:
        if cl["problem"] or not cl["image"]:
            continue
        by_img.setdefault(cl["image"], []).append(cl)
    looks = []

    def one(img):
        comps = sorted({c["component"] for c in by_img[img]})
        rec = {"image": img, "image_sha256": by_img[img][0]["image_sha256"], "image_px": by_img[img][0].get("image_px"),
               "image_note": by_img[img][0].get("image_note"), "components": comps,
               "look": None, "where": "", "first_noticed": "", "outcome": None, "cause": None, "ok": None, "raw": "", "ms": 0}
        t0 = time.time()
        try:
            ok, raw = runner(lambda path: OPEN_PROMPT.format(image=path), img)
        except rmpaths.RmDataRootUnset:
            raise                                    # the documented by-name failure, never a "could not look"
        except Exception as ex:                      # noqa: BLE001 - a staging or subprocess error is "could not run"
            ok, raw = False, "%s: %s" % (type(ex).__name__, ex)
        rec["ms"], rec["ok"], rec["raw"] = int((time.time() - t0) * 1000), ok, raw
        if not ok:
            rec["outcome"], rec["cause"] = "could_not_look", "the judge could not run: %s" % str(raw)[:300]
        else:
            look, where, first, cause = parse_open(raw)
            rec["look"], rec["where"], rec["first_noticed"] = look, where, first
            if look is None:
                rec["outcome"], rec["cause"] = "could_not_look", cause
            elif look == "COULD NOT SEE":
                rec["outcome"], rec["cause"] = "could_not_look", "the judge could not see: %s" % (first or where or "no reason given")
            else:
                rec["outcome"] = "doubt" if look in ("ODD", "WRONG") else "expected"
        log("open look %-28s %s%s" % (",".join(comps)[:28], rec["look"] or rec["outcome"], (" -- " + rec["where"])[:80] if rec["where"] else ""))
        return rec

    with ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
        looks = list(ex.map(one, list(by_img)))
    for rec in looks:
        if rec["outcome"] == "doubt":
            for cl in by_img[rec["image"]]:
                cl.setdefault("doubts", []).append("%s: %s: %s%s" % (cl["component"], rec["look"], rec["where"] or "(no place named)",
                                                                     ("; first noticed: " + rec["first_noticed"]) if rec["first_noticed"] else ""))
    return {"status": "ran", "prompt_sha256": OPEN_PROMPT_SHA256, "looks": looks,
            "doubts": sum(1 for r in looks if r["outcome"] == "doubt"),
            "could_not_look": sum(1 for r in looks if r["outcome"] == "could_not_look"),
            "expected": sum(1 for r in looks if r["outcome"] == "expected")}


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


def apply_verdicts(doc, claims, only_claimed=False):
    """only_claimed: a filtered run (--only-chain) rewrites just the bars its selected components claim."""
    by_bar = {}
    for cl in claims:
        cl["outcome"], cl["outcome_why"] = decide_claim(cl)
        by_bar.setdefault(cl["bar"], []).append(cl)
    for row in doc.get("bars") or ():
        if not row.get("visual") or (only_claimed and row["id"] not in by_bar):
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
        # a pass-1 doubt stands beside the verdict until the owner or a state read answers it; it is not the verdict, and a
        # rerun never erases one: earlier doubts are kept and merged (only an explicit resolution may remove one)
        doubts = list(row.get("doubts") or [])
        for d in (d for c in cls for d in c.get("doubts", [])):
            if d not in doubts:
                doubts.append(d)
        if doubts:
            row["doubts"] = doubts
            row["evidence"] += " | pass-1 doubt (bar-blind open look, open until the owner or a state read answers it): " + "; ".join(doubts)[:600]
    doc["summary"] = B.summarize(doc.get("bars") or [])
    doc["all_green"] = B.all_green(doc.get("bars") or [], doc.get("expected") or None)
    return doc


def parse_record(raw):
    """-> ({would_pass, smallest_fix, criterion_verdict, criterion_why} as the follow-up wrote them, None) or (None, why
    the follow-up gave no answer: it could not run or its answer is unreadable). The fields are not judged here: the
    refusal contract judges them."""
    try:
        e = json.loads(raw)
    except (ValueError, TypeError):
        return None, "unreadable answer: the CLI envelope is not JSON"
    if not isinstance(e, dict):
        return None, "unreadable answer: the CLI envelope is not an object"
    if e.get("is_error") or is_throttle(True, raw):
        return None, "the follow-up could not run: %s" % str(e.get("result") or e.get("error") or "error envelope")[:300]
    obj, cause = _final_object(e.get("result"))
    if cause:
        return None, cause
    return {k: obj.get(k) for k in ("would_pass", "smallest_fix", "criterion_verdict", "criterion_why")}, None


def _judged(cl):
    """-> ("pass" | "refuse", None) for a claim its judge decided, or (None, why it could not look)."""
    if cl["problem"]:
        return None, cl["problem"]
    calls = cl["calls"]
    if any(c["throttled"] for c in calls):
        return None, "judge throttled"
    dead = [c for c in calls if not c["ok"]]
    if dead:
        return None, dead[0]["why"] or "judge could not run"
    err = [c for c in calls if _error_envelope(c["raw"])]
    if err:     # the process ran, the CLI says the call failed: no answer of the judge's, never a refusal
        return None, "the judge could not run: %s" % str(err[0]["raw"])[:300]
    if cl.get("outcome") == PASS:
        return "pass", None
    if cl.get("outcome") == FAIL or any(c["verdict"] == judge.UNJUDGEABLE for c in calls):
        return "refuse", None
    return None, cl.get("outcome_why") or "no verdict"   # a split vote


def _rc():
    """refusal_contract (src/RimMandrake/rimflow), imported by its path."""
    rimflow = os.path.join(os.path.dirname(_UTILS), "rimflow")
    if rimflow not in sys.path:
        sys.path.insert(0, rimflow)
    import refusal_contract
    return refusal_contract


def _error_envelope(raw):
    try:
        e = json.loads(raw)
    except (ValueError, TypeError):
        return False
    return isinstance(e, dict) and bool(e.get("is_error"))


def _deciding_call(cl):
    """The call whose answer decided a refused claim: its first UNJUDGEABLE when that left it UNMEASURED, else its
    first (a FAIL is unanimous)."""
    if cl.get("outcome") != FAIL:
        return next((c for c in cl["calls"] if c["verdict"] == judge.UNJUDGEABLE), cl["calls"][0])
    return cl["calls"][0]


def _counters_for(item):
    """-> (the item's counted refusals, {clause: count}) from the refusal store, or (None, why it could not be read)."""
    try:
        RC = _rc()
        it = RC._item(RC.counters(), item)
        return int(it.get("refused") or 0), dict(it.get("clauses") or {})
    except Exception as e:  # noqa: BLE001 - an unreadable store: submit counts the truth
        return None, "the refusal store could not be read: %s" % e


def contract_records(doc, claims, record_runner, submit, log=_p):
    """The run's refusal-contract verdict: passed bars, and one record per refused (or unjudgeable) bar whose follow-up
    answered. -> the judge.contract record."""
    texts = doc.get("bar_text") or {}
    item = str(doc.get("item") or "northstar:%s" % (doc.get("mod") or "?"))
    by_bar = {}
    for cl in claims:
        by_bar.setdefault(cl["bar"], []).append(cl)
    passed, refused, no_look, no_rec = [], [], [], []
    for bar in sorted(by_bar):
        kinds = [(cl, _judged(cl)) for cl in by_bar[bar]]
        bad = [cl for cl, (k, _w) in kinds if k == "refuse"]
        blind = [(cl, w) for cl, (k, w) in kinds if k is None]
        # every claim that could not look is named, whether or not another claim refused the bar
        no_look += [{"clause": bar, "component": cl["component"], "cause": str(w)[:300]} for cl, w in blind]
        if bad:
            refused.append((bar, bad))
        elif not blind:
            passed.append({"clause": bar, "evidence": sorted({cl["image"] for cl in by_bar[bar]})})
    prior, clauses = _counters_for(item)
    recs, followups = [], []
    for bar, bad in refused:
        why_of = [(c, _deciding_call(c)) for c in bad]
        cl, call = why_of[0]
        text = (texts.get(bar) or {}).get("text") or ""
        others = "".join("\nAnother capture of this statement (%s) was answered %s, because: %s" % (
            os.path.basename(c["image"]), k["verdict"], k["why"] or "(no reason given)") for c, k in why_of[1:])
        goal = RECORD_GOAL.get(cl["polarity"], RECORD_GOAL[judge.MUST])
        t0 = time.time()
        try:
            ok, raw = record_runner(lambda path: RECORD_PROMPT.format(
                image=path, bar=text, verdict=call["verdict"], why=call["why"] or "(no reason given)", others=others,
                goal=goal), cl["image"])
        except rmpaths.RmDataRootUnset:
            raise
        except Exception as ex:  # noqa: BLE001 - a staging or subprocess error: the follow-up could not run
            ok, raw = False, "%s: %s" % (type(ex).__name__, ex)
        followups.append({"clause": bar, "image": cl["image"], "image_sha256": cl.get("image_sha256"), "ok": ok,
                          "raw": raw, "ms": int((time.time() - t0) * 1000), "models_reported": reported_models(raw)})
        fields, cause = parse_record(raw) if ok else (None, "the follow-up could not run: %s" % str(raw)[:300])
        if fields is None:
            no_rec.append({"clause": bar, "cause": cause})
            log("record %-32s could not record: %s" % (bar[:32], cause[:80]))
            continue
        rec = dict({"clause": bar, "criterion_hash": _rc().criterion_hash(text),
                    "evidence": sorted({c["image"] for c in bad}),
                    "observed": "; ".join(dict.fromkeys("%s: %s" % (k["verdict"], k["why"]) for _c, k in why_of))},
                   **fields)
        if prior:   # after the item's first counted refusal: a clause refused before is unfixed, a new one is late
            rec["new_since"] = ("unfixed:%s" % bar) if clauses.get(bar) else "late"
        recs.append(rec)
    judged = [p["clause"] for p in passed] + [r["clause"] for r in recs]
    out = {"status": "ran", "prompt_sha256": RECORD_PROMPT_SHA256, "item": item, "records": len(recs),
           "passed": len(passed), "could_not_look": no_look, "could_not_record": no_rec, "followups": followups}
    if prior is None:
        out["counters"] = clauses     # why new_since could not be set; submit reads the store itself
    if no_rec:   # a refusal without its record is no verdict: never submitted as fewer refusals (or an all-pass)
        out.update(submitted=False, why="incomplete: %d refused bar(s) could not be recorded (%s); nothing submitted" % (
            len(no_rec), ", ".join(r["clause"] for r in no_rec)))
        return out
    if not judged:
        out.update(submitted=False, why="no bar was judged: nothing to record")
        return out
    pairs = sorted({"%s=%s" % (c["image"], c.get("image_sha256")) for bar in judged for c in by_bar[bar]})
    sha = hashlib.sha256("\n".join(pairs).encode("utf-8")).hexdigest()[:16]   # which content is at which capture
    inputs = sorted({e for p in passed for e in p["evidence"]} | {e for r in recs for e in r["evidence"]})
    verdict = {"item": item, "family": RECORD_FAMILY, "sha": sha, "passed": passed, "refusals": recs}
    given = {"inputs": inputs, "criteria": {b: (texts.get(b) or {}).get("text") or "" for b in judged}, "sha": sha}
    try:
        res = submit(verdict, given)
    except Exception as ex:  # noqa: BLE001 - the store could not take it: said, never read as submitted
        out.update(submitted=False, why="submit failed: %s: %s" % (type(ex).__name__, ex), verdict=verdict)
        return out
    out.update(submitted=True, sha=sha, **{k: res.get(k) for k in ("ok", "errors", "counted", "advisory", "pointer",
                                                                   "calibration", "repair_due", "alarms")
                                          if k in res})
    log("records: %d refusal(s), %d passed, %d could not look, %d could not record -> %s" % (
        len(recs), len(passed), len(no_look), len(no_rec), res.get("pointer") or res.get("errors")))
    return out


def judge_doc(doc, runner, model="(mock)", jobs=8, repeat_must=1, repeat_cannot=3, timeout=180,
              backoff_s=20.0, log=_p, open_runner=None, open_skip_why=None, record_runner=None, submit=None,
              record_skip_why=None, only_claimed=False):
    """Pass 1 (open_runner, bar-blind) then pass 2 (runner, the bar statement), then the refusal records (record_runner
    asks the follow-ups, submit is refusal_contract.submit). open_runner None = no pass 1; record_runner or submit None =
    no records; each recorded as not run."""
    texts = doc.get("bar_text") or {}
    claims, calls = plan_calls(doc, repeat_must, repeat_cannot)
    log("judge: %d claim(s), %d call(s), %d undecidable before asking; jobs=%d model=%s" % (
        len(claims), len(calls), sum(1 for c in claims if c["problem"]), jobs, model))
    t0 = time.time()
    if open_runner is not None:
        ol = open_look(claims, open_runner, jobs=jobs, log=log)
    else:
        ol = {"status": "not run: %s" % (open_skip_why or "no open runner given (the pass-2-only API)"), "looks": []}
    stats = execute(calls, texts, runner, jobs=jobs, backoff_s=backoff_s, log=log)
    apply_verdicts(doc, claims, only_claimed=only_claimed)
    models = sorted({m for c in calls for m in reported_models(c["raw"])})
    contract = (contract_records(doc, claims, record_runner, submit, log=log)
                if record_runner is not None and submit is not None else
                {"status": "not run: %s" % (record_skip_why or "no record runner or submit given")})
    prev = (doc.get("judge") or {}).get("open_look")
    if prev:                                         # every earlier look is kept, also across a run that skipped pass 1
        ol["earlier"] = (prev.get("earlier") or []) + [{k: v for k, v in prev.items() if k != "earlier"}]
    doc["judge"] = {
        "judged_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model_requested": model, "models_reported": models,
        "prompt_sha256": PROMPT_SHA256, "repeat_must": repeat_must, "repeat_cannot": repeat_cannot,
        "jobs": jobs, "timeout_s": timeout, "wall_s": round(time.time() - t0, 1), "stats": stats, "open_look": ol,
        "contract": contract,
        "claims": [{k: v for k, v in cl.items() if k != "calls"} | {
            "calls": [{"k": c["k"], "verdict": c["verdict"], "why": c["why"], "ok": c["ok"],
                       "throttled": c["throttled"], "attempts": c["attempts"], "ms": c["ms"],
                       "raw": c["raw"]} for c in cl["calls"]]} for cl in claims],
    }
    return doc


def _rc_submit():
    return _rc().submit


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
    ap.add_argument("--no-open-look", action="store_true", help="skip pass 1 (the bar-blind open look); recorded as not run")
    ap.add_argument("--no-records", action="store_true", help="write no refusal-contract records; recorded as not run")
    a = ap.parse_args(argv)
    with open(a.results, encoding="utf-8") as f:
        doc = json.load(f)
    if not doc.get("components"):
        _p("refused: %s carries no components[] -- written by a driver before screenshot recording"
           % a.results)
        return 2
    full = doc
    if a.only_chain:
        # judge a filtered view; the saved file keeps every chain's components (bar rows are shared, so only claimed ones change)
        doc = dict(doc, components=[c for c in doc["components"] if c.get("chain") in a.only_chain])
    judge_doc(doc, claude_runner(a.model, a.timeout), model=a.model, jobs=a.jobs,
              repeat_must=a.repeat_must, repeat_cannot=a.repeat_cannot, timeout=a.timeout,
              open_runner=None if a.no_open_look else claude_runner(a.model, a.timeout),
              open_skip_why="--no-open-look" if a.no_open_look else None,
              record_runner=None if a.no_records else claude_runner(a.model, a.timeout),
              submit=None if a.no_records else _rc_submit(), record_skip_why="--no-records" if a.no_records else None,
              only_claimed=bool(a.only_chain))
    doc["components"] = full["components"]
    out = a.out or a.results
    B.write_results(out, doc)
    s = doc["summary"]
    ol = doc["judge"]["open_look"]
    _p("%s: %s  PASS=%s FAIL=%s UNMEASURED=%s  pass-1 doubts=%s could-not-look=%s  -> %s" % (
        doc.get("mod"), "GREEN" if doc["all_green"] else "NOT GREEN", s[PASS], s[FAIL], s[UNMEASURED],
        ol.get("doubts", "-"), ol.get("could_not_look", "-") if ol.get("status") == "ran" else ol.get("status"), out))
    return 0 if doc["all_green"] else 1


if __name__ == "__main__":
    sys.exit(main())
