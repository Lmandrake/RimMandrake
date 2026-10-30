#!/usr/bin/env python3
"""Token-spend census across every Claude Code transcript on this machine (offline, no model calls).

Answers "does the orchestrator's context strategy even matter?" by measuring the denominator:
total spend per day over the last DAYS days, split by project family and by role
(orchestrator top-level / subagent / headless run), plus compaction events and subagent levers.

Cost unit: Opus-input-token equivalents (ITE). Per call:
  ITE = MODEL_X[model] * (input + 0.1*cache_read + 1.25*write_5m + 2*write_1h + 5*output)
MODEL_X is an ASSUMPTION (relative list prices Opus 1 : Sonnet 0.6 : Haiku 0.2), labelled as such.
Every API call is counted once (deduped by message id across files); sidechain copies inside a
parent transcript are skipped because the subagent's own file carries them.

Writes OUT_DIR/spend_census.json; prints a short summary.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime

PROJECTS = os.path.expanduser("~/.claude/projects")
OUT_DIR = "/mnt/d/ClaudeWork/rimmandrake/perpetual_ctx"
DAYS = 7
MODEL_X = {"opus": 1.0, "sonnet": 0.6, "haiku": 0.2}   # ASSUMPTION: relative list prices
PRICE_IN_PER_MTOK = 5.0                                # ASSUMPTION: Opus-class input $/MTok, display only
READ_RE = re.compile(r'"file_path":\s*"([^"]+)"')


def family(proj: str) -> str:
    if proj == "-home-mandrake-rm-bench":
        return "BENCH"
    if proj.startswith("-home-mandrake-rm-foundry"):
        return "FOUNDRY"
    for key, name in (("art-eval-runs", "art-eval headless runs"), ("fw-art-geometry", "fw-art-geometry runs"),
                      ("seat-tmp", "seat-tmp headless runs"), ("Hestia", "Hestia"), ("EMERGENCY", "EMERGENCY"),
                      ("Lodestar", "Lodestar"), ("pulse", "pulse"), ("testq", "testq"), ("ClaudeWork", "other ClaudeWork runs")):
        if key.lower() in proj.lower():
            return name
    return "other: " + proj[:40]


def model_x(model: str) -> float:
    m = (model or "").lower()
    for k, v in MODEL_X.items():
        if k in m:
            return v
    return 1.0


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def scan_file(path, cutoff, seen, stats=None):
    """Per-call dicts and compaction events for one transcript. `stats` (dict) receives bad_lines (unparseable
    JSON lines, skipped) and cwd (first recorded cwd). A message id enters `seen` only after its usage is counted."""
    stats = stats if stats is not None else {}
    calls, compacts, reads = [], [], []
    res_size = {}            # tool_use_id -> tool_result tokens (chars/4)
    last_t = None
    pending_compact = None
    for line in open(path, errors="replace"):
        try:
            d = json.loads(line)
        except Exception:
            stats["bad_lines"] = stats.get("bad_lines", 0) + 1
            continue
        if not isinstance(d, dict):
            stats["bad_lines"] = stats.get("bad_lines", 0) + 1
            continue
        if d.get("cwd") and "cwd" not in stats:
            stats["cwd"] = d["cwd"]
        t = d.get("type")
        if t == "system" and d.get("subtype") == "compact_boundary":
            md = d.get("compactMetadata") or {}
            pending_compact = {"t": ts(d["timestamp"]) if d.get("timestamp") else None,
                               "pre": md.get("preTokens"), "trigger": md.get("trigger"),
                               "last_call_t": last_t, "call_index": len(calls), "summary_tok": 0}
            compacts.append(pending_compact)
            continue
        if t == "user" and d.get("isCompactSummary") and pending_compact is not None:
            c = d.get("message", {}).get("content")
            pending_compact["summary_tok"] = len(c if isinstance(c, str) else json.dumps(c)) / 4
            continue
        if t == "user" and isinstance(d.get("message", {}).get("content"), list):
            for b in d["message"]["content"]:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    c = b.get("content")
                    res_size[b.get("tool_use_id")] = len(c if isinstance(c, str) else json.dumps(c)) / 4
            continue
        if t != "assistant" or d.get("isSidechain") and "/subagents/" not in path:
            continue
        m = d.get("message", {})
        for c in m.get("content") or []:
            if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "Read":
                fp = (c.get("input") or {}).get("file_path")
                if fp:
                    reads.append((len(calls), fp, c.get("id")))
        u = m.get("usage")
        mid = m.get("id")
        if mid is None and u:     # no message id: key on content so distinct calls never collapse into one
            mid = "nohash:" + hashlib.sha1(json.dumps([d.get("timestamp"), m.get("model"), u],
                                                      sort_keys=True).encode()).hexdigest()
        if not u or not d.get("timestamp") or mid in seen:
            continue
        t0 = ts(d["timestamp"])
        cc = u.get("cache_creation") or {}
        c5 = cc.get("ephemeral_5m_input_tokens")
        c1 = cc.get("ephemeral_1h_input_tokens")
        ccall = u.get("cache_creation_input_tokens") or 0
        if c5 is None and c1 is None:
            c5, c1 = ccall, 0
        c5, c1 = c5 or 0, c1 or 0
        cr = u.get("cache_read_input_tokens") or 0
        it = u.get("input_tokens") or 0
        out = u.get("output_tokens") or 0
        x = model_x(m.get("model"))
        calls.append({"t": t0, "gap": (t0 - last_t) if last_t else None, "model": m.get("model") or "?",
                      "ctx": it + cr + c5 + c1, "cr": cr, "cw": c5 + c1, "out": out,
                      "raw": it + cr + c5 + c1 + out,
                      "ite": x * (it + 0.1 * cr + 1.25 * c5 + 2.0 * c1 + 5.0 * out),
                      "ite_write": x * (1.25 * c5 + 2.0 * c1), "in_window": t0 >= cutoff, "c5": c5, "c1": c1, "x": x,
                      "ep": d.get("entrypoint")})
        seen.add(mid)
        last_t = t0
    return calls, compacts, reads, res_size


def main():
    now = time.time()
    cutoff = now - DAYS * 86400
    seen = set()
    fam = defaultdict(lambda: defaultdict(float))
    model_mix = defaultdict(float)
    sub_rows, compact_rows = [], []
    total = defaultdict(float)
    reread_all = [0, 0]
    for root, _dirs, files in os.walk(PROJECTS):
        for f in files:
            if not f.endswith(".jsonl"):
                continue
            p = os.path.join(root, f)
            if os.path.getmtime(p) < cutoff:
                continue
            proj = os.path.relpath(p, PROJECTS).split(os.sep)[0]
            fname = family(proj)
            is_sub = "/subagents/" in p
            try:
                calls, compacts, reads, res_size = scan_file(p, cutoff, seen)
            except Exception as e:  # unreadable file: count it, never hide it
                total["unreadable_files"] += 1
                print("unreadable", p, e, file=sys.stderr)
                continue
            win = [c for c in calls if c["in_window"]]
            if not win:
                continue
            headless = all(c["ep"] in ("sdk-cli", "sdk-py", "sdk-ts") for c in win)
            role = "subagent" if is_sub else ("headless" if headless else "top-level")
            key = f"{fname} / {role}"
            ite = sum(c["ite"] for c in win)
            fam[key]["ite"] += ite
            fam[key]["raw"] += sum(c["raw"] for c in win)
            fam[key]["calls"] += len(win)
            fam[key]["files"] += 1
            fam[key]["ite_write"] += sum(c["ite_write"] for c in win)
            fam[key]["w5m_tok"] += sum(c["c5"] for c in win)
            fam[key]["w1h_tok"] += sum(c["c1"] for c in win)
            for c in win:
                if c["gap"] is not None and c["cw"] > 0.5 * c["ctx"] and c["ctx"] > 20_000:
                    b = next(n for lo, n in ((3600, ">1h"), (900, "15-60m"), (300, "5-15m"), (60, "1-5m"), (0, "<1m")) if c["gap"] >= lo)
                    fam[key]["rewrite_ite_" + b] += c["ite_write"]
                if c["gap"] is not None:
                    b = next(n for lo, n in ((3600, ">1h"), (300, "5-60m"), (0, "<5m")) if c["gap"] >= lo)
                    fam[key]["calls_gap_" + b] += 1
            fam[key]["ite_rewrite"] += sum(c["ite_write"] for c in win if c["cw"] > 0.5 * c["ctx"] and c["ctx"] > 20_000
                                           and c["gap"] is not None)
            total["ite"] += ite
            total["raw"] += sum(c["raw"] for c in win)
            for c in win:
                model_mix[c["model"]] += c["ite"]
            # re-reads: a Read of a path this same transcript already read
            seen_paths, rr = set(), 0
            rr_tok = 0.0
            for _i, fp, tid in reads:
                if fp in seen_paths:
                    rr += 1
                    rr_tok += res_size.get(tid, 0.0)
                seen_paths.add(fp)
            fam[key]["reread_result_tok"] += rr_tok
            reread_all[0] += rr
            reread_all[1] += len(reads)
            if is_sub or role == "headless":
                main_model = max({c["model"] for c in win}, key=lambda mm: sum(c["ite"] for c in win if c["model"] == mm))
                sub_rows.append({"family": fname, "role": role, "ite": ite, "calls": len(win), "model": main_model,
                                 "first_ctx": win[0]["ctx"], "first_ite": win[0]["ite"],
                                 "peak_ctx": max(c["ctx"] for c in win), "mean_ctx": sum(c["ctx"] for c in win) / len(win),
                                 "dur_s": win[-1]["t"] - win[0]["t"], "reads": len(reads), "rereads": rr,
                                 "ite_reads_over_50k": sum(c["x"] * 0.1 * max(0, c["cr"] - 50_000) for c in win),
                                 "ite_reads_over_100k": sum(c["x"] * 0.1 * max(0, c["cr"] - 100_000) for c in win),
                                 "ite_reads_over_150k": sum(c["x"] * 0.1 * max(0, c["cr"] - 150_000) for c in win),
                                 "reread_tok": rr_tok, "opus": model_x(main_model) == 1.0})   # not the leaked last `c`
            if role == "top-level":
                for cp in compacts:
                    if cp["t"] is None or cp["t"] < cutoff:
                        continue
                    nxt = calls[cp["call_index"]] if cp["call_index"] < len(calls) else None
                    prev = calls[cp["call_index"] - 1] if cp["call_index"] > 0 else None
                    # re-reads in the 40 calls after the boundary of files read before it
                    before = {fp for i, fp, _ in reads if i < cp["call_index"]}
                    after = [fp for i, fp, _ in reads if cp["call_index"] <= i < cp["call_index"] + 40]
                    compact_rows.append({
                        "family": fname, "trigger": cp["trigger"], "pre": cp["pre"], "summary_tok": cp["summary_tok"],
                        "gap_before_compact_s": (cp["t"] - prev["t"]) if prev else None,
                        "gap_resume_s": (nxt["t"] - cp["t"]) if nxt else None,
                        "resume_ctx": nxt["ctx"] if nxt else None, "resume_cr": nxt["cr"] if nxt else None,
                        "resume_ite": nxt["ite"] if nxt else None,
                        # the summarising call is not in the transcript: estimate it (prefix read warm, summary out)
                        "est_compact_ite": (0.1 * (cp["pre"] or 0) + 5 * cp["summary_tok"]) if prev and cp["t"] - prev["t"] < 3600
                        else (2.0 * (cp["pre"] or 0) + 5 * cp["summary_tok"]),
                        "reads_after": len(after), "rereads_after": sum(fp in before for fp in after)})
    out = {"days": DAYS, "now": now, "total": dict(total), "families": {k: dict(v) for k, v in fam.items()},
           "model_mix": dict(model_mix), "subagents": sub_rows, "compactions": compact_rows,
           "reread_all": reread_all, "model_x": MODEL_X}
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(out, open(os.path.join(OUT_DIR, "spend_census.json"), "w"))
    T = total["ite"] or 1
    print(f"total ITE/day {T / DAYS:,.0f}  raw tok/day {total['raw'] / DAYS:,.0f}  (${T / DAYS * PRICE_IN_PER_MTOK / 1e6:,.0f}/day assumed price)")
    for k, v in sorted(fam.items(), key=lambda kv: -kv[1]["ite"])[:25]:
        print(f"{100 * v['ite'] / T:5.1f}%  {k}  files {int(v['files'])} calls {int(v['calls'])}")
    print("compactions in window:", len(compact_rows), "unreadable:", int(total.get("unreadable_files", 0)))


# ---- per-arm metering (architecture_switch_harness §1.6) ------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # Utils/ for gpt_call_log
ARENA_ROOT = os.environ.get("RM_ARENA_ROOT", "/home/mandrake/rm/arena")
HARNESS = "HARNESS"          # judge, gate and anything else run from <ARENA_ROOT>/judge bill here, never to an arm
UNATTRIBUTED = "UNATTRIBUTED"
UNIT_NOTE = ("claude_ite is Opus-input-token equivalents; gpt_ite is RAW codex tokens (gpt_ite_est a chars/4 guess), "
             "NOT ITE. total_ite_mixed adds them 1:1 for convenience only; the GPT->ITE conversion is an open "
             "owner/spec question and no conversion is applied.")


class ArmNameCollision(Exception):
    pass


class ZeroSpendRefused(Exception):
    """An arm that ran shows no spend: the meter is blind (wrong slug/path), so no result is reported."""


def path_slug(path: str) -> str:
    """Claude Code's project slug for a cwd: every non-alphanumeric character becomes '-'."""
    return re.sub(r"[^A-Za-z0-9]", "-", path)


def _root(arena_root=None) -> str:
    return (arena_root or ARENA_ROOT).rstrip("/") or "/"


def _desc_exists(base: str, rem: str, depth=0) -> bool:
    """Does a directory chain under `base` exist whose slugs spell `rem` (without its leading '-')?"""
    if not rem or depth > 12:
        return True
    try:
        kids = [k for k in os.listdir(base) if os.path.isdir(os.path.join(base, k))]
    except OSError:
        return False
    for k in kids:
        sk = path_slug(k)
        if rem == sk or (rem.startswith(sk + "-") and _desc_exists(os.path.join(base, k), rem[len(sk) + 1:], depth + 1)):
            return True
    return False


def classify_slug(slug: str, arms=(), arena_root: str = None):
    """-> (arm, reason). arm is a directory name directly under the arena root, HARNESS, or UNATTRIBUTED.
    The slug must start with the arena root's slug + '-' EXACTLY; the arm is then the NEXT path component:
    matched against the real directory listing under the root when it exists, else the explicit `arms` list
    ('judge' is always the harness). A slug that fits several names (ralph/a vs ralph-a) is settled by the
    real tree when possible, else UNATTRIBUTED with reason 'ambiguous'; a name not listed is 'unlisted'."""
    root = _root(arena_root)
    pre = path_slug(root) + "-"
    if not slug.startswith(pre):
        return UNATTRIBUTED, "outside"
    rest = slug[len(pre):]
    have_fs = os.path.isdir(root)
    names = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))) if have_fs else \
        sorted({a.strip("/") for a in arms if a})
    names = sorted(set(names) | {"judge"})
    cands = [n for n in names if rest == path_slug(n) or rest.startswith(path_slug(n) + "-")]
    if len(cands) > 1 and have_fs:
        ok = [n for n in cands if (rest == path_slug(n)) or
              _desc_exists(os.path.join(root, n), rest[len(path_slug(n)) + 1:])]
        if ok:
            cands = ok
    if len(cands) > 1:
        # several directories spell the same slug (arm-3 / arm_3) or one is a prefix of another (ralph, ralph-a)
        return UNATTRIBUTED, "ambiguous"
    if not cands:
        return UNATTRIBUTED, "unlisted"
    return (HARNESS if cands[0] == "judge" else cands[0]), ""


def arm_of_slug(slug: str, arms=(), arena_root: str = None) -> str:
    return classify_slug(slug, arms, arena_root)[0]


class _Seen(set):
    """Message-id set that also notes an id met under two different arm folders (deterministic order is the
    caller's job: files are fed earliest mtime first)."""
    def __init__(self):
        super().__init__()
        self.owner, self.cur, self.conflicts, self.mark = {}, None, {}, None
        self.added = []

    def __contains__(self, mid):
        hit = super().__contains__(mid)
        if hit and self.owner.get(mid) not in (None, self.cur):
            self.conflicts[mid] = (self.owner[mid], self.cur)
        return hit

    def add(self, mid):
        super().add(mid)
        self.owner.setdefault(mid, self.cur)
        self.added.append(mid)

    def begin_file(self, arm):
        self.cur, self.added = arm, []

    def rollback(self):
        """Forget every id added since the last begin_file(): the file failed, so its ids were never counted."""
        for mid in self.added:
            self.discard(mid); self.owner.pop(mid, None)
        self.added = []


def _cwd_under(cwd: str, arena_root, arm: str) -> bool:
    """Real path comparison (not slugs: /arena/solo and /arena-solo share a slug but not a path)."""
    base, c = _root(arena_root) + "/" + arm, str(cwd).rstrip("/")
    return c == base or c.startswith(base + "/")


def check_arm_names(names):
    """Refuse declared arm names whose project slugs collide (/arena/solo vs /arena-solo encode the same)."""
    by = {}
    for n in names:
        n = n.strip("/")
        by.setdefault(path_slug(n), set()).add(n)
    bad = ["%s" % " and ".join(sorted(v)) for v in by.values() if len(v) > 1]
    if bad:
        raise ArmNameCollision("arm names with the same project slug cannot be told apart by the meter: %s -- rename one"
                               % "; ".join(bad))


def claude_spend_by_arm(projects=None, arms=(), arena_root=None, since=0.0, until=None, diag=None):
    """{arm: {"ite","calls","files"}} over every transcript (subagents included), each API call once, only calls
    with since <= t < until. UNATTRIBUTED carries "reasons" {reason: ite}. `diag` (dict) receives
    unreadable_files and id_conflicts (message ids found under two arm folders: earliest transcript mtime wins,
    then lexicographic path)."""
    projects = projects or PROJECTS
    until = float("inf") if until is None else until
    diag = diag if diag is not None else {}
    diag.setdefault("unreadable_files", [])
    out, seen = defaultdict(lambda: {"ite": 0.0, "calls": 0, "files": 0}), _Seen()
    paths = []
    for root, _d, files in os.walk(projects):
        for f in files:
            if f.endswith(".jsonl"):
                p = os.path.join(root, f)
                try:
                    mt = os.path.getmtime(p)
                except OSError:
                    mt = 0.0
                paths.append((mt, p))
    for _mt, p in sorted(paths):
        arm, why = classify_slug(os.path.relpath(p, projects).split(os.sep)[0], arms, arena_root)
        seen.begin_file(arm)
        st = {}
        try:
            calls = scan_file(p, since, seen, st)[0]
        except Exception as e:                              # noqa: BLE001  unreadable: counted, flagged
            seen.rollback()                                 # its ids were not counted: a copy elsewhere must count
            diag["unreadable_files"].append("%s: %s" % (p, e))
            continue
        if st.get("bad_lines"):
            diag.setdefault("bad_lines", {})[p] = st["bad_lines"]
        if arm not in (UNATTRIBUTED, HARNESS) and st.get("cwd") and not _cwd_under(st["cwd"], arena_root, arm):
            diag.setdefault("cwd_mismatch", []).append("%s: recorded cwd %s is not under arm %s" % (p, st["cwd"], arm))
            arm, why = UNATTRIBUTED, "cwd_mismatch"
        calls = [c for c in calls if since <= c["t"] < until]
        if calls:
            r = out[arm]
            r["ite"] += sum(c["ite"] for c in calls)
            r["calls"] += len(calls)
            r["files"] += 1
            if arm == UNATTRIBUTED:
                rs = r.setdefault("reasons", {})
                rs[why] = rs.get(why, 0.0) + sum(c["ite"] for c in calls)
    diag["id_conflicts"] = dict(seen.conflicts)
    return dict(out)


def gpt_ite_of(d):
    """(ite, is_estimate). Real codex 'tokens used' when logged (counted 1:1, labelled gpt_ite);
    else chars/4 in + 5*out (labelled gpt_ite_est)."""
    tu = d.get("tokens_used")
    if isinstance(tu, (int, float)) and tu > 0:
        return float(tu), False
    return float((d.get("in_tok_est") or 0) + 5 * (d.get("out_tok_est") or 0)), True


def gpt_spend_by_arm(log=None, since=0.0, until=None, diag=None):
    """{arm: {"ite","ite_est","calls","est_calls"}} from the gpt call log (file and/or per-call directory),
    only calls with since <= t < until. "ite" is REAL codex tokens; "ite_est" the chars/4 fallback. Untagged
    calls stay under UNTAGGED; unreadable lines are counted into diag["gpt_unreadable"] and arm UNREADABLE."""
    import gpt_call_log
    until = float("inf") if until is None else until
    out = defaultdict(lambda: {"ite": 0.0, "ite_est": 0.0, "calls": 0, "est_calls": 0})
    recs, bad = gpt_call_log.read_records(log)
    if diag is not None:
        diag["gpt_unreadable"] = bad
    if bad:
        out["UNREADABLE"]["calls"] += bad
    for d in recs:
        t = d.get("t")
        if isinstance(t, bool) or not isinstance(t, (int, float)) or t != t:
            bad += 1                                   # no numeric time: cannot be placed in the window
            out["UNREADABLE"]["calls"] += 1
            if diag is not None:
                diag["gpt_unreadable"] = bad
            continue
        if not (since <= t < until):
            continue
        arm = (d.get("arm") or "").strip() or "UNTAGGED"
        ite, est = gpt_ite_of(d)
        out[arm]["ite_est" if est else "ite"] += ite
        out[arm]["est_calls"] += est
        out[arm]["calls"] += 1
    return dict(out)


def arm_report(ran=(), arms=None, projects=None, arena_root=None, gpt_log=None, since=None, until=None,
               gpt_only_arms=(), idle_arms=()):
    """Combined per-arm ITE within [since, until). Declared arms: `ran` (must show Claude spend), `gpt_only_arms`
    (ran, GPT only: must show GPT spend), `idle_arms` (ran, legitimately did nothing: zero accepted). A declared arm
    that fails its test, or no declared arms at all, raises ZeroSpendRefused. Flags report untagged GPT,
    unattributed / unreadable spend and ids found under two arm folders -- nothing is silently dropped."""
    ran, gpt_only_arms, idle_arms = list(ran), list(gpt_only_arms), list(idle_arms)
    if not (ran or gpt_only_arms or idle_arms):
        raise ZeroSpendRefused("no arms declared (--ran / --gpt-only-arms / --idle-arms): nothing to check, so no "
                               "result is reported -- an empty arm list must not pass")
    if ran and since is None:
        raise ZeroSpendRefused("--ran needs an explicit window (--since): with no lower bound old spend would satisfy "
                               "an arm that did nothing this run")
    arms = list(arms or (ran + gpt_only_arms + idle_arms))
    check_arm_names(set(arms) | set(ran) | set(gpt_only_arms) | set(idle_arms))
    since = 0.0 if since is None else since
    diag = {}
    cl = claude_spend_by_arm(projects, arms, arena_root, since, until, diag)
    gp = gpt_spend_by_arm(gpt_log, since, until, diag)
    rep = {}
    for k in set(cl) | set(gp):
        c, g = cl.get(k, {}), gp.get(k, {})
        rep[k] = {"claude_ite": c.get("ite", 0.0), "gpt_ite": g.get("ite", 0.0), "gpt_ite_est": g.get("ite_est", 0.0),
                  "claude_calls": c.get("calls", 0), "gpt_calls": g.get("calls", 0),
                  "gpt_calls_estimated": g.get("est_calls", 0)}
        rep[k]["total_ite_mixed"] = rep[k]["claude_ite"] + rep[k]["gpt_ite"] + rep[k]["gpt_ite_est"]
        rep[k]["unit_note"] = UNIT_NOTE
    dead = [a for a in ran if rep.get(a, {}).get("claude_ite", 0) <= 0]
    dead += ["%s (declared GPT-only)" % a for a in gpt_only_arms if rep.get(a, {}).get("gpt_ite", 0) + rep.get(a, {}).get("gpt_ite_est", 0) <= 0]
    if dead:
        raise ZeroSpendRefused("arm(s) ran but the meter sees zero spend in the window: %s -- a zero is not a result "
                               "(GPT rows alone do not satisfy a Claude arm; declare --gpt-only-arms / --idle-arms)"
                               % ", ".join(dead))
    flags = []
    if "UNTAGGED" in rep:
        flags.append("%d untagged gpt_consult call(s)" % rep["UNTAGGED"]["gpt_calls"])
    if UNATTRIBUTED in cl:
        flags.append("UNATTRIBUTED claude spend %.0f ITE in %d call(s), by reason %s" % (
            cl[UNATTRIBUTED]["ite"], cl[UNATTRIBUTED]["calls"], json.dumps(cl[UNATTRIBUTED].get("reasons", {}))))
    if diag.get("unreadable_files"):
        flags.append("%d unreadable transcript file(s): %s" % (len(diag["unreadable_files"]), diag["unreadable_files"][:3]))
    if diag.get("gpt_unreadable"):
        flags.append("%d unreadable gpt call log line(s)/file(s)" % diag["gpt_unreadable"])
    if diag.get("bad_lines"):
        flags.append("%d transcript file(s) had unparseable lines (skipped)" % len(diag["bad_lines"]))
    for m in diag.get("cwd_mismatch", [])[:3]:
        flags.append("UNATTRIBUTED (cwd mismatch): " + m)
    if diag.get("id_conflicts"):
        flags.append("%d message id(s) found under two arm folders (earliest transcript mtime won)" % len(diag["id_conflicts"]))
    for a in idle_arms:
        if rep.get(a, {}).get("total_ite_mixed", 0) > 0:
            flags.append("arm %s declared idle but shows %.0f (mixed units)" % (a, rep[a]["total_ite_mixed"]))
    known = set(arms) | {"UNTAGGED", "UNREADABLE", HARNESS, UNATTRIBUTED}
    for k in sorted(set(gp) - known):
        flags.append("gpt arm %r is not a declared/listed arm" % k)
    if gpt_only_arms:
        flags.append("GPT-only arms (declared): %s" % ", ".join(gpt_only_arms))
    return {"arms": rep, "flags": flags, "since": since, "until": until, "unit_note": UNIT_NOTE}


def _iso(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def arm_main(argv):
    import argparse
    ap = argparse.ArgumentParser(description="per-arm ITE by clone path (harness 1.6)")
    ap.add_argument("--arm-report", action="store_true", required=True)
    ap.add_argument("--ran", nargs="*", default=[], help="arms that ran; zero Claude spend for one is refused")
    ap.add_argument("--gpt-only-arms", nargs="*", default=[], help="arms that ran with GPT calls only")
    ap.add_argument("--idle-arms", nargs="*", default=[], help="arms that ran and legitimately did nothing")
    ap.add_argument("--arms", nargs="*", default=None, help="explicit arm names when the arena root has no directory")
    ap.add_argument("--since", help="ISO UTC start of the run window (REQUIRED with --ran)")
    ap.add_argument("--until", help="ISO UTC end of the run window")
    ap.add_argument("--projects"); ap.add_argument("--arena-root"); ap.add_argument("--gpt-log")
    a = ap.parse_args(argv)
    try:
        r = arm_report(ran=a.ran, arms=a.arms, projects=a.projects, arena_root=a.arena_root, gpt_log=a.gpt_log,
                       since=_iso(a.since) if a.since else None, until=_iso(a.until) if a.until else None,
                       gpt_only_arms=a.gpt_only_arms, idle_arms=a.idle_arms)
    except (ZeroSpendRefused, ArmNameCollision) as e:
        print("REFUSED:", e)
        return 2
    print(json.dumps(r, indent=1))
    return 0


if __name__ == "__main__":
    if "--arm-report" in sys.argv:
        sys.exit(arm_main(sys.argv[1:]))
    main()
