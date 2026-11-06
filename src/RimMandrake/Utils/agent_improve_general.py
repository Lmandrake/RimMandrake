#!/usr/bin/env python3
"""Generalization check for agent_improve (design section 4.3): does a change to a role or skill help on task KINDS it
did not come from?

Design: design/RimMandrake/daily_agent_improvement_2026-11-02.md section 4.3 (item AGENT_IMPROVE_BUILD_GENERALIZATION_CHECK).

    python3 src/RimMandrake/Utils/agent_improve.py general <target> v<N> [--days 14] [--seed S]
    python3 src/RimMandrake/Utils/agent_improve.py general-show <target> v<N>

Sample, fresh each time, from closed items of the last DAYS days: HELD_OUT items whose kind (the intent word of the id)
is not one of the change's source kinds, and SOURCE items whose kind is. For each, two fresh tool-less agents get the
item's spec, one with the old text of the target and one with the new, and each writes a plan and its first step. A
blind judge sees the spec, what actually closed the item, and the two answers as A and B in a random order (never which
is old or new) and picks the better or calls a tie.

Null control: on every judged pair the old text runs a second time and the same kind of blind judge compares the two old
answers, so each check measures, on its own sample, how far this judge drifts when there is nothing to find. Each pair
record holds it under `null`; the result holds its tallies beside the real ones (null_held_out, null_source).

Verdict (the Conductor's 2026-11-02 rule with a noise floor, AGENT_IMPROVE_HARDEN_NOISE_CALLED_OVERFIT). A sample shows
harm or gain only past BOTH bars: |wins - losses| exceeds the null's |wins - losses| plus its failed null pairs (each one
could have gone either way), and an exact one-sided sign test on the win/loss pairs gives p <= SIGN_ALPHA. At 6 pairs
that means 5-0 or 6-0; at 12 with none tied, 10-2 or better.
    harm on held-out                  -> overfit   (revert)
    gain on held-out, no harm         -> general   (keep)
    gain on the source kind only      -> narrow    (keep, flagged)
    neither past the bars             -> no_signal (keep None: neither reverts nor keeps as general)
    no held-out pair judged           -> unmeasured (source pairs alone never keep a change)
Every run writes its pairs to infrastructure/state/agent_improve/general/<target>_v<N>_<stamp>.json and appends a
summary to the change record's `generalization` list (never rewritten). A hand run records a revert verdict; agent_improve_cadence runs
the check on its cadence and enacts one.

Departure from the design's wording, on purpose: the two agents are tool-less `claude -p` runs with the target text
inlined, not agents in scratch clones (a clone per run would spend the whole 16-clone pool on a plan and a first step).
"""
import concurrent.futures
import fcntl
import glob
import hashlib
import json
import math
import os
import random
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import agent_improve as A  # noqa: E402
import model  # noqa: E402  (agent_improve put rimflow on the path)

EVENTS = os.path.join(A.REPO, "infrastructure", "state", "ledger", "events")
ITEMS = os.path.join(A.REPO, "infrastructure", "state", "items")
GENERAL = os.path.join(A.REPO, "infrastructure", "state", "agent_improve", "general")
# 12 held-out, AGENT_IMPROVE_TUNE_L2_GATE_SAMPLE_POWER (design 4.3): at 6 a change winning 80% of decided pairs read
# general 20% and a harmful one (20%) read overfit 20%; at 12, 46% each. 5 is the fewest that can pass the sign test:
# fewer source pairs make narrow dead.
DAYS, HELD_OUT, SOURCE = 14, 12, 6
GATE_MIN_JUDGED = 6   # the L2 gate passes narrow or no_signal on no fewer judged held-out pairs than this
RUN_MODEL, JUDGE_MODEL = "sonnet", "opus"
WORKERS = 8   # pairs run side by side: 8 sequential pairs of three model calls overrun a 540 s foreground budget
SPEC_CHARS, ANSWER_CHARS = 3000, 4000
SIGN_ALPHA = 0.05
RULE = "noise_floor_v1: harm/gain need |net| > |null net| + null errors and a one-sided sign test at p <= %s" % SIGN_ALPHA
VERDICTS = ("overfit", "general", "narrow", "no_signal", "unmeasured")
KEEP = {"general": True, "narrow": True, "overfit": False, "no_signal": None, "unmeasured": None}


def item_kind(iid):
    """The intent word of an item id (BUILD, REPAIR, ...), else None (a legacy id has none)."""
    p = model.parse_name(re.sub(r"_\d+$", "", iid or ""))
    return p[1] if p else None


def closed_items(now, days=DAYS, events_dir=None):
    """-> {id: {id, kind, ledger_kind, title, closed_at, close_text, sha}} for items whose LAST close falls in the
    window (a reopened item's later close counts; a drop is not a close)."""
    lo = now - days * 86400
    filed, closes = {}, {}
    for p in sorted(glob.glob(os.path.join(events_dir or EVENTS, "*.jsonl"))):
        with open(p, encoding="utf-8", errors="replace") as f:
            for ln in f:
                try:
                    e = json.loads(ln)
                except ValueError:
                    continue
                iid, ev = e.get("id"), e.get("event")
                if not iid:
                    continue
                if ev == "file":
                    filed[iid] = e
                elif ev == "close":
                    t = A.epoch(e.get("ts"))
                    if t is not None and (iid not in closes or t >= closes[iid][0]):
                        closes[iid] = (t, e)
    out = {}
    for iid, (t, e) in closes.items():
        if not (lo <= t <= now):
            continue
        k = item_kind(iid)
        if not k:
            continue
        fe = filed.get(iid, {})
        out[iid] = {"id": iid, "kind": k, "ledger_kind": fe.get("kind"), "title": str(fe.get("title") or ""),
                    "closed_at": e.get("ts"), "sha": e.get("sha"),
                    "close_text": " ".join(str(e.get(x) or "") for x in ("reason", "why", "ownerSaid")).strip()}
    return out


def spec_of(it, items_dir=None):
    """The item's spec as filed: its title plus its prose (items/closed/<ID>.md, or items/<ID>.md if reopened)."""
    d = items_dir or ITEMS
    for p in (os.path.join(d, "closed", it["id"] + ".md"), os.path.join(d, it["id"] + ".md")):
        if os.path.isfile(p):
            return (it["title"] + "\n\n" + open(p, encoding="utf-8", errors="replace").read()).strip()[:SPEC_CHARS]
    return it["title"][:SPEC_CHARS]


def sample(items, source_kinds, rng, held_out=HELD_OUT, source=SOURCE, need_spec=None):
    """-> (held, src): held-out items spread over as many kinds as there are (one per kind round-robin, kinds and
    items shuffled by rng), and source-kind items. need_spec(it) -> bool drops items with no usable spec."""
    src_k = set(source_kinds or ())
    pool = [it for it in sorted(items.values(), key=lambda x: x["id"]) if not need_spec or need_spec(it)]
    by_kind = {}
    for it in pool:
        if it["kind"] not in src_k:
            by_kind.setdefault(it["kind"], []).append(it)
    kinds = sorted(by_kind)
    rng.shuffle(kinds)
    for k in kinds:
        rng.shuffle(by_kind[k])
    held = []
    while len(held) < held_out and any(by_kind[k] for k in kinds):
        for k in kinds:
            if by_kind[k] and len(held) < held_out:
                held.append(by_kind[k].pop())
    srcs = [it for it in pool if it["kind"] in src_k]
    rng.shuffle(srcs)
    return held, srcs[:source]


RUN_PROMPT = """You are a builder agent in the RimMandrake project (RimWorld mods). Below are your working instructions
(%s), then a task. Do not do the task. Write:
1. PLAN: at most 8 numbered lines, the steps you would take, naming the files, tools and checks you would use.
2. FIRST STEP: the exact first command or edit you would make, and what you expect it to show.
Keep it under 350 words. Follow your instructions where they apply.

===== INSTRUCTIONS =====
%s
===== TASK =====
%s
"""

JUDGE_PROMPT = """You are a blind judge. Two agents, A and B, were given the same task and each wrote a plan and a
first step. You also see what actually closed the task. Pick the answer whose plan and first step would more surely and
cheaply have reached that close: correct files and tools, no wrong facts, no wasted or risky step. Call a tie when
neither is clearly better. Do not prefer length.

===== TASK =====
%s
===== WHAT ACTUALLY CLOSED IT =====
%s
===== ANSWER A =====
%s
===== ANSWER B =====
%s
===== REPLY =====
ONE JSON object and nothing else: {"better": "A" | "B" | "tie", "why": "one or two sentences"}
"""


def judge_two(spec, close, first, second, first_is_a, judge):
    """One blind judgment of two answers -> (outcome for `first`: win/loss/tie, the judge's reply, a, b).
    A failure raises; a reply with no usable pick raises ValueError."""
    a, b = (first, second) if first_is_a else (second, first)
    jv = A.parse_json_reply(judge(JUDGE_PROMPT % (spec, close[:1500], a, b)))
    better = str(jv.get("better") or "").strip().upper()
    if better not in ("A", "B", "TIE"):
        raise ValueError("better=%r" % jv.get("better"))
    return ("tie" if better == "TIE" else ("win" if (better == "A") == first_is_a else "loss")), better, jv, a, b


def null_pair(ans_old, rerun, spec, close, rerun_is_a, judge):
    """The null control for one item: ans_old against a second run of the same old text. outcome is win/loss/tie for
    the rerun (it stands where the new text stands in the real pair), or error; it never harms the real pair."""
    rec = {"rerun_is_a": rerun_is_a}
    try:
        outcome, better, jv, a, b = judge_two(spec, close, rerun(), ans_old, rerun_is_a, judge)
    except Exception as e:
        rec.update(outcome="error", error=str(e)[:300])
        return rec
    rec.update(outcome=outcome, better=better, why=str(jv.get("why") or "")[:500], a=a, b=b)
    return rec


def run_pair(it, spec, old_text, new_text, what, new_is_a, runner, judge, rerun_is_a=False):
    """One item: two runs, one blind judgment -> a pair record; outcome is win/loss/tie for the NEW text, or error.
    A judged pair also carries its null control under `null`, so null pairs and judged pairs correspond one to one."""
    rec = {"id": it["id"], "kind": it["kind"], "ledger_kind": it.get("ledger_kind"), "closed_at": it.get("closed_at")}
    try:
        ans_old = str(runner(RUN_PROMPT % (what, old_text, spec)))[:ANSWER_CHARS]
        ans_new = str(runner(RUN_PROMPT % (what, new_text, spec)))[:ANSWER_CHARS]
    except Exception as e:   # any failure is this pair's error, never the whole check's crash
        rec.update(outcome="error", error="run: %s" % str(e)[:300])
        return rec
    close = it.get("close_text") or "(no close reason recorded)"
    if it.get("sha"):
        close += "\nclosing commit: %s" % it["sha"]
    try:
        outcome, better, jv, a, b = judge_two(spec, close, ans_new, ans_old, new_is_a, judge)
    except Exception as e:
        a, b = (ans_new, ans_old) if new_is_a else (ans_old, ans_new)
        rec.update(outcome="error", error="judge: %s" % str(e)[:300], new_is_a=new_is_a, a=a, b=b)
        return rec
    rec.update(outcome=outcome, better=better, new_is_a=new_is_a, why=str(jv.get("why") or "")[:500], a=a, b=b)
    rerun = lambda: str(runner(RUN_PROMPT % (what, old_text, spec)))[:ANSWER_CHARS]   # noqa: E731
    rec["null"] = null_pair(ans_old, rerun, spec, close, rerun_is_a, judge)
    return rec


def tally(pairs, side):
    t = {"win": 0, "loss": 0, "tie": 0, "error": 0}
    for p in pairs:
        if p["side"] == side:
            t[p["outcome"]] += 1
    return t


def null_tally(pairs, side):
    t = {"win": 0, "loss": 0, "tie": 0, "error": 0}
    for p in pairs:
        if p["side"] == side and p.get("null"):
            t[p["null"]["outcome"]] += 1
    return t


def sign_p(wins, losses):
    """Exact one-sided sign test: the chance of at least max(wins, losses) of the win/loss pairs falling one way when
    each is a fair coin. No pairs -> 1.0."""
    n = wins + losses
    return sum(math.comb(n, i) for i in range(max(wins, losses), n + 1)) / 2 ** n if n else 1.0


def noise_margin(null):
    """The net the null control reached on this sample; a failed null pair counts as one that went the far way."""
    return abs(null["win"] - null["loss"]) + null["error"]


def signal(t, null):
    """One sample against its null -> {net, margin, sign_p, alpha, call}; call is gain, harm or None."""
    net, margin, p = t["win"] - t["loss"], noise_margin(null), sign_p(t["win"], t["loss"])
    call = None
    if abs(net) > margin and p <= SIGN_ALPHA:
        call = "gain" if net > 0 else "harm"
    return {"net": net, "margin": margin, "sign_p": round(p, 4), "alpha": SIGN_ALPHA, "call": call}


def verdict(held, src, null_held, null_src):
    """held, src: tallies; null_held, null_src: their null tallies -> one of VERDICTS (see the module docstring)."""
    if held["win"] + held["loss"] + held["tie"] == 0:   # "held out, no harm" needs held-out evidence
        return "unmeasured"
    call = signal(held, null_held)["call"]
    if call == "harm":
        return "overfit"
    if call == "gain":
        return "general"
    if signal(src, null_src)["call"] == "gain":   # source losses alone are not harm: the rule judges held-out kinds
        return "narrow"
    return "no_signal"


def gate_passes(result):
    """The L2 pre-apply reading of a check (AGENT_IMPROVE_TUNE_L2_GATE_SAMPLE_POWER) -> (ok, why). general passes;
    overfit and unmeasured refuse; narrow and no_signal pass only when the held-out pairs do not lean against the change
    on enough judged pairs. The check at this size cannot prove most real gains (design 4.3), so at L2, behind the
    recurrence bar, the Judge and the recheck, it refuses what leans to harm instead of waiting for a proof. A source
    gain never buys off held-out losses. The verdict itself is left as it read."""
    v = result.get("verdict")
    if v == "general":
        return True, v
    if v not in ("narrow", "no_signal"):
        return False, v
    h = result.get("held_out") or {}
    wins, losses, judged = h.get("win", 0), h.get("loss", 0), h.get("win", 0) + h.get("loss", 0) + h.get("tie", 0)
    if judged < GATE_MIN_JUDGED:
        return False, "%s on %d judged held-out pairs, under %d" % (v, judged, GATE_MIN_JUDGED)
    if losses > wins:
        return False, "%s leaning to harm on held-out kinds, %d-%d" % (v, wins, losses)
    return True, "%s, no lean to harm, %d-%d" % (v, wins, losses)


def view(res, text):
    """The part of the target an agent reads: the whole file, or the editable region (relentless' worker brief)."""
    return text[slice(*A.region_of(text, res["region"]))]


def check(t, old_text, new_text, source_kinds, now=None, seed=None, runner=None, judge=None, events_dir=None,
          items_dir=None, days=DAYS, workers=WORKERS):
    """The check on two texts of target t -> result dict (pairs, tallies, verdict, keep). Writes nothing."""
    res = A.resolve_target(t)
    if not res:
        raise ValueError("%s is not an editable target" % t)
    now = time.time() if now is None else now
    seed = seed if seed is not None else int.from_bytes(os.urandom(4), "big")
    rng = random.Random(seed)
    runner = runner or (lambda p: A.claude_fresh(p, model_name=RUN_MODEL))
    judge = judge or (lambda p: A.claude_fresh(p, model_name=JUDGE_MODEL))
    items = closed_items(now, days, events_dir)
    specs = {}

    def has_spec(it):
        specs[it["id"]] = spec_of(it, items_dir)
        return len(specs[it["id"]]) >= 40
    held, src = sample(items, source_kinds, rng, need_spec=has_spec)
    old_v, new_v = view(res, old_text), view(res, new_text)
    jobs = [(side, it, rng.random() < 0.5, rng.random() < 0.5) for side, group in (("held_out", held), ("source", src))
            for it in group]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futs = [ex.submit(run_pair, it, specs[it["id"]], old_v, new_v, res["what"], nia, runner, judge, ria)
                for _, it, nia, ria in jobs]
        pairs = [dict(f.result(), side=job[0]) for f, job in zip(futs, jobs)]
    th, ts = tally(pairs, "held_out"), tally(pairs, "source")
    nh, ns = null_tally(pairs, "held_out"), null_tally(pairs, "source")
    v = verdict(th, ts, nh, ns)
    return {"target": t, "path": res["path"], "seed": seed, "days": days,
            "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "source_kinds": sorted(source_kinds or ()),
            "pool": {"closed_items": len(items), "kinds": sorted({i["kind"] for i in items.values()})},
            "held_out": th, "source": ts, "null_held_out": nh, "null_source": ns, "rule": RULE,
            "signal": {"held_out": signal(th, nh), "source": signal(ts, ns)}, "verdict": v, "keep": KEEP[v],
            "pairs": pairs,
            "old_sha256": hashlib.sha256(old_v.encode()).hexdigest()[:16],
            "new_sha256": hashlib.sha256(new_v.encode()).hexdigest()[:16]}


def version_texts(t, n, repo=None):
    """-> (old_text, new_text, old_ref, new_ref) for agent/<t>/v<n>: new at that tag, old at the tag's parent commit
    (the text the change was made against, so no other edit between versions is judged as part of it)."""
    repo = repo or A.REPO
    res = A.resolve_target(t)
    new_ref = "agent/%s/v%d" % (t, n)
    old_ref = new_ref + "^"
    show = lambda ref: A.git("show", "%s:%s" % (ref, res["path"]), cwd=repo)   # noqa: E731
    return show(old_ref), show(new_ref), old_ref, new_ref


def write_evidence(result, name, general_dir=None, repo=None, **extra):
    """Write one check's full result as <general_dir>/<name>_<stamp>_<seed>[_k].json (never over another file) and
    -> (absolute path, the path as recorded: repo-relative when inside repo)."""
    repo = os.path.abspath(repo or A.REPO)
    gdir = general_dir or GENERAL
    os.makedirs(gdir, exist_ok=True)
    stem = "%s_%s_%s" % (name, result["at"].replace("-", "").replace(":", ""), result["seed"])
    for k in range(100):
        epath = os.path.join(gdir, stem + (".json" if k == 0 else "_%d.json" % k))
        try:
            f = open(epath, "x", encoding="utf-8")
        except FileExistsError:
            continue
        with f:
            json.dump(dict(result, **extra), f, indent=1)
        ab = os.path.abspath(epath)
        return epath, (os.path.relpath(ab, repo) if os.path.commonpath([ab, repo]) == repo else ab)
    raise RuntimeError("no free evidence name for %s" % stem)


def summary(result, evidence, refs):
    return {"at": result["at"], "verdict": result["verdict"], "keep": result["keep"], "held_out": result["held_out"],
            "source": result["source"], "null_held_out": result.get("null_held_out"),
            "null_source": result.get("null_source"), "signal": result.get("signal"), "rule": result.get("rule"),
            "seed": result["seed"], "evidence": evidence, "refs": refs or {}}


def record(result, t, n, changes_dir=None, general_dir=None, repo=None, refs=None):
    """Write the evidence file and append its summary to <t>_v<n>.json under a lock, by a temp file and rename, so a
    concurrent run or a crash never loses an entry -> (evidence path, change record path)."""
    cpath = os.path.join(changes_dir or A.CHANGES, "%s_v%d.json" % (t, n))
    epath, rel = write_evidence(result, "%s_v%d" % (t, n), general_dir, repo, version=n, refs=refs or {})
    # Lock the changes folder itself: a lock FILE would sit untracked in the repo, and deleting one breaks the lock.
    dfd = os.open(os.path.dirname(os.path.abspath(cpath)), os.O_RDONLY)
    try:
        fcntl.flock(dfd, fcntl.LOCK_EX)
        rec = json.load(open(cpath, encoding="utf-8"))
        rec.setdefault("generalization", []).append(summary(result, rel, refs))
        tmp = "%s.%d.tmp" % (cpath, os.getpid())
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1)
        os.replace(tmp, cpath)
    finally:
        os.close(dfd)
    return epath, cpath


def run_for_version(t, version, repo=None, seed=None, runner=None, judge=None, days=DAYS, changes_dir=None,
                    general_dir=None, now=None, events_dir=None, items_dir=None):
    n = int(str(version).lstrip("v"))
    repo = repo or A.REPO
    cpath = os.path.join(changes_dir or A.CHANGES, "%s_v%d.json" % (t, n))
    src_kinds = json.load(open(cpath, encoding="utf-8")).get("source_kinds") or []
    old, new, old_ref, new_ref = version_texts(t, n, repo)
    result = check(t, old, new, src_kinds, now=now, seed=seed, runner=runner, judge=judge, days=days,
                   events_dir=events_dir, items_dir=items_dir)
    return result, record(result, t, n, changes_dir, general_dir, repo, {"old": old_ref, "new": new_ref})


def show(t, version, changes_dir=None, repo=None):
    """-> (exit code, lines): 0 when the change record holds a generalization entry whose evidence file exists and
    judged at least one pair; 1 otherwise."""
    n = int(str(version).lstrip("v"))
    repo = repo or A.REPO
    cpath = os.path.join(changes_dir or A.CHANGES, "%s_v%d.json" % (t, n))
    try:
        gens = json.load(open(cpath, encoding="utf-8")).get("generalization") or []
    except (OSError, ValueError) as e:
        return 1, ["%s: %s" % (cpath, e)]
    lines, good = [], 0
    for g in gens:
        ep = g.get("evidence") or ""
        ep = ep if os.path.isabs(ep) else os.path.join(repo, ep)
        judged = None
        if os.path.isfile(ep):
            body = json.load(open(ep, encoding="utf-8"))
            judged = sum(1 for p in body.get("pairs", []) if p.get("outcome") in ("win", "loss", "tie"))
        good += 1 if judged else 0
        lines.append("%s %s keep=%s held_out=%s null_held_out=%s source=%s null_source=%s judged=%s evidence=%s" % (
            g.get("at"), g.get("verdict"), g.get("keep"), g.get("held_out"), g.get("null_held_out"), g.get("source"),
            g.get("null_source"), judged, g.get("evidence")))
    if not gens:
        lines.append("%s: no generalization entry" % cpath)
    return (0 if good else 1), lines
