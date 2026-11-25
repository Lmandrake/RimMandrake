#!/usr/bin/env python3
"""work_bundle_monitor.py: the Temporary Work Bundle Monitor. One report a day to the Conductor on Work Bundles.

Item RIMMANDRAKE_BUILD_TEMPORARY_WORK_BUNDLE_MONITOR_DAILY (owner by card, 2026-11-25 about 11:10 AM PST). Page of
promises: design/specs/2026-11-25-temporary-work-bundle-monitor/boundary.md; tests: selftest_work_bundle_monitor.py.
Temporary: it lives while the Work Bundles are evaluated; a lasting monitor is folded into Operations, not grown here.

    work_bundle_monitor.py measure [--since ISO] [--until ISO] [--json]   part 1: no model, no tokens
    work_bundle_monitor.py judge [--since ISO] [--until ISO]              part 2: one Sonnet call per set-down/backward move
    work_bundle_monitor.py calibrate                                      part 2 on the Conductor's 25 labelled set-downs
    work_bundle_monitor.py daily                                          parts 1-3 (rm-work-bundle-monitor.timer)

Every number is a measured count, [] none found, `could not look` with its cause, or `failed` with its cause. A source
that cannot be read makes its numbers UNMEASURED, never 0; a run with no token figure is unpriced, never 0 tokens.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils"), os.path.dirname(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ITEM = "RIMMANDRAKE_BUILD_TEMPORARY_WORK_BUNDLE_MONITOR_DAILY"
SPEC = os.path.join(REPO, "design", "specs", "2026-11-25-temporary-work-bundle-monitor")
LEDGER = os.path.join(REPO, "infrastructure", "state", "ledger", "events")
CONCEPTS = os.path.join(REPO, "design", "concepts")
PROJECTS = os.path.join(os.path.expanduser("~"), ".claude", "projects")
JUDGE_BRIEF = os.path.join(HERE, "work_bundle_monitor_judge.md")
REPORT_BRIEF = os.path.join(HERE, "work_bundle_monitor_report.md")
CLAUDE_BOUNDED = os.path.join(REPO, "src", "RimMandrake", "Utils", "claude_bounded.sh")
UNM = "UNMEASURED"
CNL = "could not look"
DAY = 86400
STAY_DAYS = 3                  # the owner's card: a ticket stays closed when still closed three days after its close
BASELINE_DAYS = 14             # the brief: single-ticket runs of the same system in the 14 days before its first bundle
REOPEN = ("start", "claim", "implemented")
EDIT_TOOLS = ("Edit", "Write", "NotebookEdit", "MultiEdit")
STAGES = ("intake", "designer", "preflight", "offline_build", "blind_challenge", "in_game", "pre_human", "his_walk",
          "passed")                                                   # maturation.STAGES, in order
VERDICTS = ("SINCERE", "NOT SINCERE", "COULD NOT JUDGE")
SECTIONS = ("## The day's numbers", "## The worst pattern", "## Three repairs", "## The recommendation")
# budget: danger=a transcript of several MB overflows the judge's context; the end before the set-down is where the
# budget: attempt shows (the brief: "the part of the run's transcript before the set-down")
EXCERPT_CHARS = 60000
# Hang guards for one judge call and the one report call: time_budget.JUDGE_S, the class=judge (a judge call that never
# returns holds its caller). Measured here: the 50 calibration calls of 2026-11-25 took 14.3 s at most; the report call of
# the first daily run (2026-11-25) took 267 s.
import time_budget as TB  # noqa: E402
JUDGE_TIMEOUT_S = TB.JUDGE_S  # budget: class=judge
REPORT_TIMEOUT_S = TB.JUDGE_S  # budget: class=judge


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ep(s):
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s or "").strip()
    if not s:
        return None
    try:
        d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.timestamp()


def pac(t):
    from zoneinfo import ZoneInfo
    return dt.datetime.fromtimestamp(t, ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d %-I:%M %p PST")


def state_dir():
    import doorbell
    return doorbell.state_dir()


def out_dir(create=False):
    """<agent storage>/rimmandrake/work_bundle_monitor; RM_WBM_OUT redirects it (tests). Fails by name when the agent
    storage root is unset (agent_storage.py), never a fallback."""
    d = os.environ.get("RM_WBM_OUT")
    if not d:
        if os.environ.get("RM_UNDER_SELFTEST"):
            raise RuntimeError("a test process writes no real monitor output: set RM_WBM_OUT")
        r = subprocess.run([sys.executable, os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")],
                           capture_output=True, text=True, timeout=TB.CALL_S)  # budget: class=call
        if r.returncode or not r.stdout.strip():
            raise RuntimeError("agent_storage.py gave no root (%s)" % (r.stderr or "").strip())
        d = os.path.join(r.stdout.strip(), "rimmandrake", "work_bundle_monitor")
    if create:
        os.makedirs(d, exist_ok=True)
    return d


def native(path):
    p = os.path.abspath(path)
    m = re.match(r"^/mnt/([a-z])/(.*)$", p)
    return ("%s:\\%s" % (m.group(1).upper(), m.group(2).replace("/", "\\"))) if m else p


# ------------------------------------------------------------------------------------------------ sources -------

def src(value, state="measured", cause=None, bad=None):
    return {"state": state, "cause": cause, "value": value, "unreadable": list(bad or [])}


def read_runs(d):
    """Detached run records (one dot in the name). -> src({unit: record}); an unparseable record is counted in
    `unreadable` by name and adds no run."""
    if not os.path.isdir(d):
        return src(None, CNL, "the run record folder %s does not exist" % d)
    out, bad = {}, []
    for p in glob.glob(os.path.join(d, "rm-detached-*.json")):
        if os.path.basename(p).count(".") != 1:
            continue
        try:
            with open(p, encoding="utf-8") as f:
                r = json.load(f)
            if not isinstance(r, dict) or not r.get("unit"):
                raise ValueError("no unit")
        except (OSError, ValueError) as e:
            bad.append("%s (%s)" % (os.path.basename(p), type(e).__name__))
            continue
        out[r["unit"]] = r
    return src(out, bad=bad)


def read_role_runs(d):
    """Role run results: {unit: result} (session_id), for the transcript of a role run's set-down."""
    if not os.path.isdir(d):
        return src(None, CNL, "the role run folder %s does not exist" % d)
    out, bad = {}, []
    for p in glob.glob(os.path.join(d, "rm-role-*.json")):
        if os.path.basename(p).count(".") != 1:
            continue
        try:
            with open(p, encoding="utf-8") as f:
                r = json.load(f)
        except (OSError, ValueError) as e:
            bad.append(os.path.basename(p))
            continue
        if isinstance(r, dict):
            out[os.path.basename(p)[:-5]] = r
    return src(out, bad=bad)


def read_bundles(d):
    if not os.path.isdir(d):
        return src(None, CNL, "the bundle store %s does not exist" % d)
    out, bad = {}, []
    for p in glob.glob(os.path.join(d, "*.json")):
        try:
            with open(p, encoding="utf-8") as f:
                r = json.load(f)
            out[r["id"]] = r
        except (OSError, ValueError, KeyError, TypeError) as e:
            bad.append("%s (%s)" % (os.path.basename(p), type(e).__name__))
    return src(out, bad=bad)


def read_ledger(d):
    import evidence_metrics as EM
    ev = EM.ledger_events(d)
    return src(None, CNL, "the ledger folder %s does not exist" % d) if ev is None else src(ev)


def read_moves(concepts):
    """Stage moves of every mod: [{mod, from, to, at, by, unit, why}], deduplicated over the stage_record files."""
    if not os.path.isdir(concepts):
        return src(None, CNL, "the concepts folder %s does not exist" % concepts)
    seen, out, bad = set(), [], []
    for p in sorted(glob.glob(os.path.join(concepts, "*", "version", "stage_record*.json"))):
        mod = p.split(os.sep)[-3]
        try:
            with open(p, encoding="utf-8") as f:
                moves = (json.load(f) or {}).get("moves") or []
        except (OSError, ValueError, AttributeError) as e:
            bad.append("%s (%s)" % (os.path.relpath(p, REPO), type(e).__name__))
            continue
        for m in moves:
            k = (mod, m.get("from"), m.get("to"), m.get("at"))
            if k in seen or ep(m.get("at")) is None:
                continue
            seen.add(k)
            out.append(dict(m, mod=mod, t=ep(m.get("at"))))
    return src(out, bad=bad)


def read_live_rows(concepts):
    """{"early": [...], "unrun": [...]} rows of every mod's version/in_game/ (maturation.record_early_row, record_unrun)."""
    if not os.path.isdir(concepts):
        return src(None, CNL, "the concepts folder %s does not exist" % concepts)
    out, bad = {"early": [], "unrun": []}, []
    for kind, name in (("early", "early_rows.jsonl"), ("unrun", "unrun.jsonl")):
        for p in glob.glob(os.path.join(concepts, "*", "version", "in_game", name)):
            with open(p, encoding="utf-8", errors="replace") as f:
                for ln in f:
                    if not ln.strip():
                        continue
                    try:
                        out[kind].append(json.loads(ln))
                    except ValueError:
                        bad.append(os.path.relpath(p, REPO))
    return src(out, bad=bad)


def mods_list(concepts=CONCEPTS):
    """The mods (design/concepts/<Mod>/version/VERSION.json). Raises when the folder cannot be listed: an unknown mod
    list would class every run as workshop work."""
    return sorted(f for f in os.listdir(concepts) if not f.startswith("_")
                  and os.path.exists(os.path.join(concepts, f, "version", "VERSION.json")))


def gather(root_state=None, ledger=LEDGER, concepts=CONCEPTS):
    st = root_state or state_dir()
    return {"runs": read_runs(os.path.join(st, "detached")), "roles": read_role_runs(os.path.join(st, "roles")),
            "bundles": read_bundles(os.path.join(st, "work_bundle", "bundles")), "ledger": read_ledger(ledger),
            "moves": read_moves(concepts), "live": read_live_rows(concepts), "mods": mods_list(concepts)}


# ------------------------------------------------------------------------------------------------ part 1 --------

def unit_bundles(bundles):
    """-> {unit: bundle record}: each unit a bundle record lists. A record's units are its launch and its restarts."""
    out = {}
    for b in (bundles or {}).values():
        for u in b.get("units") or []:
            if isinstance(u, dict) and u.get("unit"):
                out[u["unit"]] = b
    return out


def bundle_of(rec, ub, bundles):
    """The bundle record of a run: by its unit in a bundle record, else by RM_WORK_BUNDLE in its env; else None."""
    b = ub.get(rec.get("unit"))
    if b is None:
        bid = (rec.get("env") or {}).get("RM_WORK_BUNDLE") if isinstance(rec.get("env"), dict) else None
        b = (bundles or {}).get(bid) if bid else None
    return b


def kind_of(rec, ub, bundles):
    """'bundle' (a bundle record with 2+ members), 'bundle_of_one', or 'single'."""
    b = bundle_of(rec, ub, bundles)
    if b is None:
        return "single"
    return "bundle" if len(b.get("members") or []) >= 2 else "bundle_of_one"


def item_title(events):
    t = {}
    for e in events:
        if e.get("event") in ("file", "spawn") and e.get("title"):
            t[e.get("id") or e.get("name")] = e["title"]
    return t


def pipeline_of(rec, b, titles, mods):
    """A multi-member bundle's own pipeline; else the item's: maturation when it names a mod (the page's one rule)."""
    if b is not None and b.get("pipeline") and len(b.get("members") or []) >= 2:
        return b["pipeline"]
    import maturation_nonmod as MNM
    return "maturation" if MNM.classify(rec.get("item"), titles.get(rec.get("item")), mods, set()) == "mod" \
        else "workshop"


def mod_of(item, title, mods):
    from item_identity import named_mod
    hit, mod = named_mod([w for w in str(item or "").upper().split("_") if w], mods)
    if not hit:
        hit, mod = named_mod(re.findall(r"[A-Z0-9]+", str(title or "").upper()), mods, words_too=False)
    return mod if hit else None


def tokens_of(rec):
    """-> (weighted_v2 tokens or None, why-unpriced or None)."""
    import role_launch as RL
    try:
        n, basis = RL.tokens_v2(rec)
    except RL.UnknownModel as e:
        return None, str(e)
    if n is None:
        return None, "no token figure (%s)" % basis
    return n, None


def closes_index(events):
    """-> [{item, t, unit, signals: [(t, kind)]}] in ledger order; a signal is a reopen of that item after the close
    (start/claim/implemented, a verify fail after close, a live broken), up to its next close."""
    out, open_c = [], {}
    for e in events:
        t, i, k = ep(e.get("ts")), e.get("id"), e.get("event")
        if t is None or not i:
            continue
        c = open_c.get(i)
        if c is not None and t > c["t"]:
            if k in REOPEN:
                c["signals"].append((t, "reopened"))
            elif k == "verify" and e.get("result") == "fail" and e.get("afterClose"):
                c["signals"].append((t, "failed_after_close"))
            elif k == "live" and e.get("result") == "broken":
                c["signals"].append((t, "broke_live"))
        if k == "close":
            c = {"item": i, "t": t, "unit": e.get("role_unit"), "signals": []}
            out.append(c)
            open_c[i] = c
    return out


def stayed(c, now, days=STAY_DAYS):
    """-> 'stayed' | 'reopened' | 'pending' for one close."""
    w = days * DAY
    if any(t - c["t"] <= w for t, _s in c["signals"]):
        return "reopened"
    if now - c["t"] < w:
        return "pending"
    return "stayed"


def run_closes(rec, b, closes):
    """The closes a run made: role_unit is its unit; for a bundle run, also each member close after the launch."""
    unit = rec.get("unit")
    mine = [c for c in closes if c["unit"] == unit]
    if b is not None:
        members, t0 = set(b.get("members") or []), b.get("at") or 0
        ids = {id(c) for c in mine}
        mine += [c for c in closes if c["item"] in members and c["t"] >= t0 and id(c) not in ids
                 and (c["unit"] is None or not str(c["unit"]).startswith("rm-detached-") or c["unit"] == unit)]
    return mine


def first_edit_tokens(rec, projects=PROJECTS):
    """-> (weighted_v2 tokens of the main-thread turns before the first Edit/Write tool call, None) | ("no edit", None)
    | (None, cause)."""
    import role_launch as RL
    files = [f for f in RL._transcript_files(rec, projects) if os.sep + "subagents" + os.sep not in f]
    if not files:
        return None, "no transcript for session %s" % rec.get("session")
    per, edited = {}, False
    try:
        with open(files[0], encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"assistant"' not in line:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("type") != "assistant" or e.get("isSidechain"):
                    continue
                m = e.get("message") or {}
                c = m.get("content") if isinstance(m.get("content"), list) else []
                if any(isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in EDIT_TOOLS for b in c):
                    edited = True
                    break
                if isinstance(m.get("usage"), dict) and m.get("id"):
                    per[m["id"]] = (m["usage"], m.get("model"))
    except OSError as e:
        return None, "transcript %s: %s" % (files[0], e)
    if not edited:
        return "no edit", None
    if not per:
        return 0, None
    u = RL._sum_usage(per.values())
    if u is None:
        return None, "a usage field in the transcript is not a whole number"
    try:
        return RL.run_tokens({"modelUsage": u["model_usage"]}), None
    except RL.UnknownModel as e:
        return None, str(e)


ROLE_MARKS = (("You are the worker of work bundle", "bundle worker"), ("Shape list item", "workshop shape"),
              ("You are resumed in your own session", "resumed helper"),
              ("This instruction is from the Conductor", "Conductor's hand brief"))


def role_of(unit, runs):
    """The role of the run that acted: rm-role-<role>; a Maturation stage run by RM_CONTROL_STAGE; else the first mark
    its brief carries (ROLE_MARKS), the first roles/<name>.md it names, its launcher; else 'detached helper'."""
    m = re.match(r"rm-role-([a-z_]+)-\d+", unit or "")
    if m:
        return m.group(1)
    if not unit:
        return "no run (a window)"
    rec = (runs or {}).get(unit) or {}
    env = rec.get("env") if isinstance(rec.get("env"), dict) else {}
    if env.get("RM_CONTROL_STAGE"):
        return "maturation %s" % env["RM_CONTROL_STAGE"]
    for k in ("brief_src", "brief_file"):
        try:
            with open(rec.get(k), encoding="utf-8", errors="replace") as f:
                text = f.read(20000)
        except (OSError, TypeError):
            continue
        for mark, role in ROLE_MARKS:
            if mark in text[:4000]:
                return role
        r = re.search(r"roles/([a-z_]+)\.md", text)
        if r:
            return r.group(1).replace("_", " ")
        break
    if rec.get("next_act_owner"):
        return "launched by %s" % rec["next_act_owner"]
    return "detached helper"


def setdowns(events, t0, t1):
    """-> ([set-down rows], program filings count) in [t0, t1)."""
    rows, prog = [], 0
    for e in events:
        t = ep(e.get("ts"))
        if t is None or not (t0 <= t < t1) or e.get("event") not in ("file", "spawn"):
            continue
        nn = e.get("not_now")
        if not isinstance(nn, dict):
            continue
        if not nn.get("class"):
            prog += 1
            continue
        rows.append({"id": e.get("id") or e.get("name"), "ts": e.get("ts"), "t": t, "class": nn.get("class"),
                     "evidence": nn.get("evidence") or "", "unit": e.get("role_unit") or "", "title": e.get("title") or "",
                     "seat": e.get("seat"), "kind": "set-down"})
    return rows, prog


def move_kind(m):
    try:
        a, b = STAGES.index(m.get("from")), STAGES.index(m.get("to"))
    except ValueError:
        return "unknown"
    return "forward" if b > a else "backward"


def waits_naming_conductor(events, now, t0, t1):
    """Open waits whose reason names the Conductor: open now, and filed in the window."""
    last, closed = {}, set()
    for e in events:
        i, k = e.get("id"), e.get("event")
        if not i:
            continue
        if k == "wait":
            last[i] = e
            closed.discard(i)
        elif k in ("unwait",):
            last.pop(i, None)
        elif k in ("close", "drop", "supersede"):
            closed.add(i)
            last.pop(i, None)
    open_now, new = [], 0
    for i, e in last.items():
        if i in closed or not re.search(r"(?i)conductor", str(e.get("reason") or "")):
            continue
        u = ep(e.get("until"))
        if u is not None and u > now:
            open_now.append(i)
            t = ep(e.get("ts"))
            if t is not None and t0 <= t < t1:
                new += 1
    return sorted(open_now), new


def _ratio(tok, n):
    return round(tok / n) if n else None


def kind_numbers(rows, now):
    """rows: the day's runs of one kind -> runs, closes, tokens, tokens per close, headline and its counts."""
    priced = [r for r in rows if r["tokens"] is not None]
    tok = sum(r["tokens"] for r in priced)
    closes = [c for r in priced for c in r["closes"]]
    st = [stayed(c, now) for c in closes]
    pre = [r["first_edit"] for r in rows if isinstance(r["first_edit"], int)]
    return {"runs": len(rows), "priced_runs": len(priced), "unpriced_runs": len(rows) - len(priced),
            "closes": sum(len(r["closes"]) for r in rows), "tokens": tok if priced else UNM,
            "tokens_per_close": _ratio(tok, len(closes)) if priced else UNM,
            "stayed": st.count("stayed"), "reopened": st.count("reopened"), "pending": st.count("pending"),
            "tokens_per_stayed_close": (_ratio(tok, st.count("stayed")) if priced and not st.count("pending") else
                                        ("pending" if st.count("pending") else UNM)),
            "provisional_tokens_per_unreopened_close": _ratio(tok, st.count("stayed") + st.count("pending"))
            if priced else UNM,
            "first_edit_median": int(statistics.median(pre)) if pre else (UNM if not rows else "none measured"),
            "first_edit_runs": len(pre), "no_edit_runs": sum(1 for r in rows if r["first_edit"] == "no edit"),
            "first_edit_unmeasured": sum(1 for r in rows if r["first_edit"] is None)}


NOTES = {
    "share": "per pipeline and kind: bundle = a bundle record with 2+ members; bundle_of_one = a bundle record with 1 "
             "member; single = every other detached run. Runs are the detached runs that ENDED in the window.",
    "efficiency": "efficiency.*.single counts single-ticket runs AND bundles of one together (the comparison is "
                  "multi-member bundles against everything else); efficiency.today.bundle_of_one shows the bundles of "
                  "one alone. headline_window is the 24 hours that ended 3 days before the window's end: its closes are "
                  "old enough to say whether they stayed closed.",
    "first_edit": "weighted tokens of the main-thread turns before the first Edit/Write/NotebookEdit; 'no edit' runs "
                  "made none (not 0 tokens).",
    "deferral.set_downs": "file/spawn events whose not_now carries a class (an agent's words)",
    "deferral.program_filings": "file/spawn events whose not_now carries only a program name: a program filed them, "
                                "so they are not set-downs and are not judged",
    "deferral.runs_ending_with_work_owed": "detached runs that ended in the window whose record has an owed close or a "
                                           "continue plan (left_open_continue) other than none",
    "moves.backward": "a move to an earlier stage, or to the same stage: a road back that opens a new cycle "
                      "(maturation.ROADS_BACK has in_game -> in_game and blind_challenge -> blind_challenge); by design, "
                      "not a defect of the reader",
    "live": "per bundle: bundle_live_ran/unrun from the bundle record's live_runs (work_bundle.py live); early_rows and "
            "unrun_rows from the mod's version/in_game files for the members while the bundle lived. 0 and 0 does not "
            "say whether the bundle owed a live check.",
}


def measure(S, t0, t1, now, projects=PROJECTS, transcripts=True):
    """Part 1. S: gather(). -> the day's reading (a dict, JSON-safe)."""
    sources = {k: {"state": v["state"], "cause": v["cause"], "unreadable": v["unreadable"]}
               for k, v in S.items() if isinstance(v, dict) and "state" in v}
    R = {"window": {"since": iso(t0), "until": iso(t1)}, "made": iso(now), "sources": sources, "unit": "weighted_v2",
         "notes": NOTES}
    ev = S["ledger"]["value"]
    runs = S["runs"]["value"]
    bundles = S["bundles"]["value"]
    titles = item_title(ev or [])
    closes = closes_index(ev) if ev is not None else None
    ub = unit_bundles(bundles) if bundles is not None else {}

    def day_rows(t_lo, t_hi):
        rows = []
        for u, rec in sorted((runs or {}).items()):
            e = ep(rec.get("ended"))
            if e is None or not (t_lo <= e < t_hi):
                continue
            b = bundle_of(rec, ub, bundles)
            tok, why = tokens_of(rec)
            fe = (None, "not read") if not transcripts else first_edit_tokens(rec, projects)
            rows.append({"unit": u, "item": rec.get("item"), "kind": kind_of(rec, ub, bundles),
                         "bundle": b["id"] if b else None, "system": b.get("system") if b else None,
                         "pipeline": pipeline_of(rec, b, titles, S["mods"]), "tokens": tok, "unpriced_why": why,
                         "closes": run_closes(rec, b, closes) if closes is not None else [],
                         "first_edit": fe[0], "first_edit_why": fe[1], "result": rec.get("result"),
                         "mod": mod_of(rec.get("item"), titles.get(rec.get("item")), S["mods"]),
                         "at": rec.get("at"), "ended": e, "model": rec.get("model")})
        return rows

    if runs is None or closes is None:
        why = S["runs"]["cause"] if runs is None else S["ledger"]["cause"]
        R["share"] = R["efficiency"] = {"state": CNL, "cause": why}
        rows = []
    else:
        rows = day_rows(t0, t1)
        running = sum(1 for rec in runs.values() if ep(rec.get("ended")) is None and rec.get("status") == "running")
        share = {"state": "measured", "still_running": running}
        for pl in ("maturation", "workshop"):
            share[pl] = {k: {"runs": sum(1 for r in rows if r["pipeline"] == pl and r["kind"] == k),
                             "closes": sum(len(r["closes"]) for r in rows if r["pipeline"] == pl and r["kind"] == k),
                             "tokens": sum(r["tokens"] or 0 for r in rows if r["pipeline"] == pl and r["kind"] == k),
                             "unpriced": sum(1 for r in rows if r["pipeline"] == pl and r["kind"] == k
                                             and r["tokens"] is None)}
                         for k in ("bundle", "bundle_of_one", "single")}
        R["share"] = share
        ripe = day_rows(t0 - STAY_DAYS * DAY, t1 - STAY_DAYS * DAY)
        R["efficiency"] = {
            "state": "measured",
            "today": {"bundle": kind_numbers([r for r in rows if r["kind"] == "bundle"], now),
                      "single": kind_numbers([r for r in rows if r["kind"] != "bundle"], now),
                      "bundle_of_one": kind_numbers([r for r in rows if r["kind"] == "bundle_of_one"], now)},
            "headline_window": {"since": iso(t0 - STAY_DAYS * DAY), "until": iso(t1 - STAY_DAYS * DAY),
                                "bundle": kind_numbers([r for r in ripe if r["kind"] == "bundle"], now),
                                "single": kind_numbers([r for r in ripe if r["kind"] != "bundle"], now)},
            "baseline": baseline(S, rows, bundles, ub, titles, closes, now),
            "first_bundle": iso(min(b.get("at") for b in bundles.values())) if bundles else None}
        R["runs"] = [{k: v for k, v in r.items() if k != "closes"} | {"closes": [c["item"] for c in r["closes"]]}
                     for r in rows]
    # stage moves
    mv = S["moves"]["value"]
    if mv is None:
        R["moves"] = {"state": CNL, "cause": S["moves"]["cause"]}
    else:
        day = [m for m in mv if t0 <= m["t"] < t1]
        per = {}
        for m in day:
            per.setdefault(m["mod"], {"forward": 0, "backward": 0, "unknown": 0})[move_kind(m)] += 1
        R["moves"] = {"state": "measured", "per_mod": per,
                      "backward": [{k: m.get(k) for k in ("mod", "from", "to", "at", "by", "unit", "why")}
                                   for m in day if move_kind(m) == "backward"]}
    # deferral
    if ev is None:
        R["deferral"] = {"state": CNL, "cause": S["ledger"]["cause"]}
    else:
        sd, prog = setdowns(ev, t0, t1)
        for r in sd:
            r["role"] = role_of(r["unit"], runs)
        by_class, by_role = {}, {}
        for r in sd:
            by_class[r["class"]] = by_class.get(r["class"], 0) + 1
            by_role[r["role"]] = by_role.get(r["role"], 0) + 1
        waits, new_waits = waits_naming_conductor(ev, now, t0, t1)
        day_ev = [e for e in ev if ep(e.get("ts")) is not None and t0 <= ep(e["ts"]) < t1]
        left = [e.get("id") for e in day_ev if e.get("event") == "note" and str(e.get("text") or "").lstrip()
                .startswith("LEFT OPEN:")]
        owed = ([u for u, rec in (runs or {}).items() if ep(rec.get("ended")) is not None and t0 <= ep(rec["ended"]) < t1
                 and (str(rec.get("owed_close") or "").strip() or (rec.get("continue_plan") or {}).get("act")
                      not in (None, "none"))] if runs is not None else None)
        R["deferral"] = {"state": "measured", "set_downs": len(sd), "by_class": by_class, "by_role": by_role,
                         "program_filings": prog, "rows": [{k: v for k, v in r.items() if k != "t"} for r in sd],
                         "waits_naming_conductor_open": len(waits), "waits_naming_conductor_new": new_waits,
                         "waits_items": waits, "left_open_notes": len(left), "left_open_items": sorted(set(left)),
                         "runs_ending_with_work_owed": UNM if owed is None else len(owed),
                         "filed": sum(1 for e in day_ev if e.get("event") in ("file", "spawn")),
                         "closed": sum(1 for e in day_ev if e.get("event") == "close")}
    R["live"] = live_work(S, t0, t1)
    return R


def baseline(S, rows, bundles, ub, titles, closes, now):
    """For each multi-member bundle system of the day: the single-ticket runs of the same system in the 14 days before
    its first bundle. Only a mod system can be named (item_identity.named_mod); other homes read could not look."""
    out = {}
    runs = S["runs"]["value"] or {}
    systems = sorted({r["system"] for r in rows if r["kind"] == "bundle" and r["system"]})
    for sysname in systems:
        first = min(b.get("at") or 0 for b in bundles.values() if b.get("system") == sysname)
        if not sysname.startswith("mod:"):
            out[sysname] = {"state": CNL, "cause": "only a mod system can be named for past runs (list_home holds the "
                                                   "homes of open tickets only)"}
            continue
        mod = sysname[4:]
        sel = []
        for u, rec in runs.items():
            e = ep(rec.get("ended"))
            if e is None or not (first - BASELINE_DAYS * DAY <= e < first) or kind_of(rec, ub, bundles) == "bundle":
                continue
            if mod_of(rec.get("item"), titles.get(rec.get("item")), S["mods"]) != mod:
                continue
            tok, _w = tokens_of(rec)
            sel.append({"tokens": tok, "closes": run_closes(rec, None, closes), "first_edit": "not read"})
        out[sysname] = dict(kind_numbers(sel, now), state="measured", since=iso(first - BASELINE_DAYS * DAY),
                            until=iso(first))
    return out


def live_work(S, t0, t1):
    """For each bundle with a run in or after the window start: live checks run and UNRUN, from its record's live_runs
    and the mod's early_rows/unrun rows of its members while it lived."""
    b, lv = S["bundles"]["value"], S["live"]["value"]
    if b is None:
        return {"state": CNL, "cause": S["bundles"]["cause"]}
    out = {}
    for bid, rec in sorted(b.items()):
        units = rec.get("units") or []
        if not units or max(u.get("at") or 0 for u in units) < t0 - DAY and (rec.get("at") or 0) < t0:
            continue
        lr = rec.get("live_runs") or []
        row = {"members": len(rec.get("members") or []), "member_ids": list(rec.get("members") or []),
               "state": rec.get("state"),
               "bundle_live_ran": sum(1 for x in lr if not x.get("unrun")),
               "bundle_live_unrun": sum(1 for x in lr if x.get("unrun"))}
        if lv is None:
            row["mod_rows"] = CNL + ": " + str(S["live"]["cause"])
        else:
            mem, lo = set(rec.get("members") or []), rec.get("at") or 0
            for kind in ("early", "unrun"):
                mine = [x for x in lv[kind] if x.get("item") in mem]
                ts = [ep(x.get("at") or x.get("ts")) for x in mine]
                row[kind + "_rows"] = sum(1 for t in ts if t is not None and t >= lo)
                row[kind + "_rows_undated"] = sum(1 for t in ts if t is None)
        out[bid] = row
    return {"state": "measured", "bundles": out}


# ------------------------------------------------------------------------------------------------ part 2 --------

def transcript_of(unit, runs, roles, projects=PROJECTS):
    """-> (main transcript path, brief text) or (None, cause)."""
    import role_launch as RL
    rec = (runs or {}).get(unit)
    sid = None
    if rec:
        sid = rec.get("session")
    elif roles and unit in roles:
        sid = roles[unit].get("session_id")
    if not sid:
        return None, "no run record with a session for %r" % unit
    files = [f for f in RL._transcript_files({"session": sid}, projects) if os.sep + "subagents" + os.sep not in f]
    return (files[0], None) if files else (None, "no transcript for session %s" % sid)


def excerpt(path, before_t, chars=EXCERPT_CHARS):
    """-> (the brief's head, the run's acts before `before_t` as text, at most `chars` from the end)."""
    acts, brief = [], ""
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("isSidechain"):
                continue
            t = ep(e.get("timestamp"))
            if t is not None and t >= before_t:
                break
            m = e.get("message") or {}
            c = m.get("content")
            if e.get("type") == "user" and not brief and isinstance(c, str):
                brief = c[:6000]
                continue
            for b in c if isinstance(c, list) else []:
                if not isinstance(b, dict):
                    continue
                ty = b.get("type")
                if ty == "text" and e.get("type") == "assistant":
                    acts.append("ASSISTANT: " + b["text"][:1500])
                elif ty == "text" and e.get("type") == "user" and not brief:
                    brief = b["text"][:6000]
                elif ty == "tool_use":
                    inp = b.get("input") or {}
                    what = inp.get("command") or inp.get("file_path") or inp.get("pattern") or json.dumps(inp)[:300]
                    acts.append("TOOL %s: %s" % (b.get("name"), str(what)[:800]))
                elif ty == "tool_result":
                    cc = b.get("content")
                    s = cc if isinstance(cc, str) else " ".join(x.get("text", "") for x in cc or [] if isinstance(x, dict))
                    acts.append("RESULT: " + s[:400])
    text = "\n".join(acts)
    return brief, text[-chars:]


def judge_prompt(row, brief, acts, template=None, transcript="read"):
    template = template or open(JUDGE_BRIEF, encoding="utf-8").read()
    state = ("(the transcript was read)" if transcript == "read" else
             "(the transcript could not be read: %s)" % transcript)
    return (template.replace("{KIND}", row.get("kind", "set-down")).replace("{TRANSCRIPT_STATE}", state)
            .replace("{TICKET}", "%s\n%s" % (row.get("id"), row.get("title") or ""))
            .replace("{REASON}", "%s: %s" % (row.get("class") or "", row.get("evidence") or row.get("why") or ""))
            .replace("{BRIEF}", brief or "(the brief was not found in the transcript)")
            .replace("{ACTS}", acts or "(no act before this point)"))


def call_model(prompt, tier, timeout, name, runner=None):
    """One headless `claude -p` through claude_bounded.sh (the door rm-findings-judge uses), the prompt on stdin, no
    tools, no budget flag. The model is the tier's id from the environment (role_launch.launch_model). -> (result
    text or None, cause or None, weighted tokens or None, seconds)."""
    import role_launch as RL
    argv = [CLAUDE_BOUNDED, "-p", "--model", RL.launch_model(tier), "--output-format", "json", "--tools", "",
            "--no-session-persistence", "--name", name]
    cwd = out_dir(create=True)
    t = time.time()
    try:
        r = (runner or subprocess.run)(argv, input=prompt, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    except subprocess.TimeoutExpired:
        return None, "timed out after %d s (hang guard)" % timeout, None, time.time() - t
    sec = time.time() - t
    try:
        res = json.loads(r.stdout or "")
    except ValueError:
        return None, "exit %s, no JSON result: %s" % (r.returncode, ((r.stderr or "") + (r.stdout or ""))[-300:]), \
            None, sec
    try:
        tok = RL.run_tokens(res, tier)
    except RL.UnknownModel:
        tok = None
    if r.returncode or res.get("is_error"):
        return None, "exit %s: %s" % (r.returncode, str(res.get("result") or res.get("subtype"))[:300]), tok, sec
    return str(res.get("result") or ""), None, tok, sec


def parse_verdict(text):
    """-> {verdict, evidence, cause} from the judge's last JSON line, or None."""
    for ln in reversed((text or "").strip().splitlines()):
        ln = ln.strip().strip("`")
        if ln.startswith("{"):
            try:
                v = json.loads(ln)
            except ValueError:
                continue
            if v.get("verdict") in VERDICTS:
                return {"verdict": v["verdict"], "evidence": str(v.get("evidence") or ""),
                        "cause": str(v.get("cause") or "")}
    return None


def judge_row(row, runs, roles, projects=PROJECTS, caller=None):
    """One judge call on one set-down or backward move. -> the row's verdict record (never raises)."""
    out = {"id": row.get("id"), "ts": row.get("ts"), "kind": row.get("kind"), "unit": row.get("unit"),
           "class": row.get("class"), "role": row.get("role")}
    path, why = transcript_of(row.get("unit"), runs, roles, projects) if row.get("unit") else (None, "no run unit")
    if path is None:
        brief, acts, out["transcript"] = "", "", "could not look: %s" % why
    else:
        brief, acts = excerpt(path, ep(row.get("ts")) or time.time())
        out["transcript"] = path
    if not brief:
        brief = brief_head((runs or {}).get(row.get("unit")) or {})
    prompt = judge_prompt(row, brief, acts, transcript="read" if path else why)
    text, err, tok, sec = (caller or call_model)(prompt, "sonnet", JUDGE_TIMEOUT_S, "WBM JUDGE %s" % row.get("id"))
    out.update(tokens=tok, seconds=round(sec, 1))
    if err:
        return dict(out, verdict="COULD NOT JUDGE", evidence="", cause="the judge call failed: " + err)
    v = parse_verdict(text)
    if v is None:
        return dict(out, verdict="COULD NOT JUDGE", evidence="", cause="the judge gave no verdict line: " +
                    (text or "")[-200:])
    return dict(out, **v)


def brief_head(rec, n=6000):
    """The head of a detached run's brief from its record (brief_src, else brief_file), or ''."""
    for k in ("brief_src", "brief_file"):
        try:
            with open(rec.get(k), encoding="utf-8", errors="replace") as f:
                return f.read(n)
        except (OSError, TypeError):
            continue
    return ""


def judge_day(R, S, caller=None):
    rows = [dict(r) for r in (R.get("deferral") or {}).get("rows") or []]
    for m in (R.get("moves") or {}).get("backward") or []:
        rows.append({"id": "%s %s->%s" % (m["mod"], m["from"], m["to"]), "ts": m["at"], "kind": "backward move",
                     "unit": m.get("unit") or "", "class": "backward", "evidence": m.get("why") or "",
                     "title": "the mod %s moved from %s back to %s" % (m["mod"], m["from"], m["to"]),
                     "role": role_of(m.get("unit"), S["runs"]["value"])})
    return [judge_row(r, S["runs"]["value"], S["roles"]["value"], caller=caller) for r in rows]


def calibrate(S, caller=None, labels_path=None):
    """Run the judge on the 25 set-downs the Conductor classed. -> (table rows, disagreements)."""
    labels = json.load(open(labels_path or os.path.join(SPEC, "calibration_labels.json"), encoding="utf-8"))
    ev = S["ledger"]["value"]
    sd, _p = setdowns(ev, ep(labels["window"]["since"]), ep(labels["window"]["until"]))
    by = {(r["id"], r["ts"]): r for r in sd}
    out = []
    for lab in labels["rows"]:
        r = by.get((lab["id"], lab["ts"]))
        if r is None:
            out.append(dict(lab, judge="COULD NOT JUDGE", why="the set-down is not in the ledger"))
            continue
        r["role"] = role_of(r["unit"], S["runs"]["value"])
        v = judge_row(r, S["runs"]["value"], S["roles"]["value"], caller=caller)
        out.append(dict(lab, judge=v["verdict"], judge_evidence=v["evidence"], judge_cause=v["cause"],
                        seconds=v.get("seconds"), tokens=v.get("tokens")))
    dis = sum(1 for x in out if x["judge"] != x["label"])
    return out, dis


# ------------------------------------------------------------------------------------------------ part 3 --------

def report_prompt(R, V, date, template=None):
    template = template or open(REPORT_BRIEF, encoding="utf-8").read()
    slim = {k: v for k, v in R.items() if k != "runs"}
    V = [{k: v for k, v in x.items() if k not in ("tokens", "seconds")} for x in V]     # the monitor's own spend: never
    return (template.replace("{DATE}", date).replace("{READING}", json.dumps(slim, indent=1, default=str))
            .replace("{RUNS}", json.dumps(R.get("runs") or [], default=str))
            .replace("{VERDICTS}", json.dumps(V, indent=1, default=str)))


def report_ok(text):
    """-> None, or the first of the four sections the report lacks."""
    for s in SECTIONS:
        if s not in (text or ""):
            return s
    return None


def summary(R, V, report_path, report_state, date):
    """The few closed figures the page and the digest read (latest.json): counts only, no token figure."""
    sh = R.get("share") or {}
    d = R.get("deferral") or {}

    def cnt(pl, k, f):
        return ((sh.get(pl) or {}).get(k) or {}).get(f, UNM) if sh.get("state") == "measured" else UNM
    vc = {v: sum(1 for x in V if x.get("verdict") == v) for v in VERDICTS} if V is not None else None
    return {"date": date, "window": R.get("window"), "made": R.get("made"),
            "share": {pl: {k: {"runs": cnt(pl, k, "runs"), "closes": cnt(pl, k, "closes")}
                           for k in ("bundle", "bundle_of_one", "single")} for pl in ("maturation", "workshop")},
            "share_state": sh.get("state"), "share_cause": sh.get("cause"),
            "deferral": ({k: d.get(k) for k in ("set_downs", "by_class", "by_role", "program_filings",
                                                  "waits_naming_conductor_open", "left_open_notes",
                                                  "runs_ending_with_work_owed", "filed", "closed")}
                         if d.get("state") == "measured" else {"state": CNL, "cause": d.get("cause")}),
            "backward_moves": len((R.get("moves") or {}).get("backward") or []) if (R.get("moves") or {}).get(
                "state") == "measured" else UNM,
            "verdicts": vc if vc is not None else UNM,
            "not_sincere_by_role": _by_role(V), "report": native(report_path) if report_path else None,
            "report_state": report_state}


def _by_role(V):
    out = {}
    for x in V or []:
        if x.get("verdict") == "NOT SINCERE":
            out[x.get("role") or "?"] = out.get(x.get("role") or "?", 0) + 1
    return out


def write_json(path, obj):
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, default=str, ensure_ascii=False)
    os.replace(path + ".tmp", path)


def daily(now=None, caller=None, S=None, say=None):
    """Parts 1-3 for the 24 hours before now. -> exit code (0 report written, 1 report failed, 2 could not look)."""
    now = time.time() if now is None else now
    t0, t1 = now - DAY, now
    date = dt.datetime.fromtimestamp(now, dt.timezone.utc).astimezone().strftime("%Y-%m-%d")
    od = out_dir(create=True)
    S = S or gather()
    R = measure(S, t0, t1, now)
    write_json(os.path.join(od, "reading_%s.json" % date), R)
    V = judge_day(R, S, caller=caller)
    with open(os.path.join(od, "verdicts_%s.jsonl" % date), "w", encoding="utf-8") as f:
        for v in V:
            f.write(json.dumps(v, default=str) + "\n")
    prev = latest(od)
    prev = ({"date": prev.get("date"), "set_downs": (prev.get("deferral") or {}).get("set_downs")}
            if prev.get("state") == "measured" and prev.get("date") != date else (prev.get("previous") or {}))
    text, err, tok, sec = (caller or call_model)(report_prompt(R, V, date), "opus", REPORT_TIMEOUT_S,
                                                 "WBM REPORT %s" % date)
    rp = os.path.join(od, "report_%s.md" % date)
    bad = err or (report_ok(text) and "the report lacks the section %r" % report_ok(text))
    if bad:
        fp = os.path.join(od, "report_%s.FAILED.md" % date)
        with open(fp, "w", encoding="utf-8") as f:
            f.write("# Temporary Work Bundle Monitor %s: REPORT FAILED\n\nCause: %s\n\nThe reading and the verdicts "
                    "were written: %s, %s.\n" % (date, bad, native(os.path.join(od, "reading_%s.json" % date)),
                                                 native(os.path.join(od, "verdicts_%s.jsonl" % date))))
        write_json(os.path.join(od, "latest.json"), dict(summary(R, V, None, "failed: " + bad, date),
                                                          monitor_tokens=_spend(V, tok), previous=prev))
        (say or _say)("REPORT FAILED (%s); the reading and verdicts are in %s" % (bad, native(od)), time.time())
        return 1
    with open(rp + ".tmp", "w", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")
    os.replace(rp + ".tmp", rp)
    write_json(os.path.join(od, "latest.json"), dict(summary(R, V, rp, "written", date), monitor_tokens=_spend(V, tok),
                                                      previous=prev, report_seconds=round(sec, 1)))
    (say or _say)("the report of %s is written: %s" % (date, native(rp)), time.time())
    print("WROTE %s" % native(rp))
    return 0


def _spend(V, report_tok):
    js = [x.get("tokens") for x in V if isinstance(x.get("tokens"), int)]
    return {"judge_calls": len(V), "judge_tokens": sum(js), "judge_unpriced": len(V) - len(js),
            "report_tokens": report_tok if isinstance(report_tok, int) else UNM, "unit": "weighted_v2"}


def _say(text, now):
    import detached_helper as DH
    DH.conductor_line(text, now, head="TEMPORARY WORK BUNDLE MONITOR")


# ------------------------------------------------------------------------------------------------ readers -------

def latest(od=None):
    """-> the newest summary (latest.json) or {"state": could not look, "cause"}; for the page and the digest."""
    try:
        p = os.path.join(od or out_dir(), "latest.json")
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        return dict(d, state="measured", path=p)
    except (OSError, ValueError, RuntimeError) as e:
        return {"state": CNL, "cause": "%s: %s" % (type(e).__name__, e)}


def digest_fields(L):
    """latest() -> the closed counts the daily digest's blind line takes (contracts.blind.project_monitor): no token
    figure. A count that is not a whole number stays out (the line reads UNMEASURED)."""
    if L.get("state") != "measured":
        return {"state": "unmeasured"}
    sh, d, v = L.get("share") or {}, L.get("deferral") or {}, L.get("verdicts")

    def tot(k):
        xs = [((sh.get(pl) or {}).get(k) or {}).get("runs") for pl in ("maturation", "workshop")]
        return sum(xs) if all(type(x) is int for x in xs) else None
    out = {"state": "measured", "date": L.get("date"), "bundle_runs": tot("bundle"),
           "bundle_of_one_runs": tot("bundle_of_one"), "single_runs": tot("single"),
           "set_downs": d.get("set_downs"), "prev_set_downs": (L.get("previous") or {}).get("set_downs"),
           "backward_moves": L.get("backward_moves"), "report": L.get("report")}
    if isinstance(v, dict):
        out.update(not_sincere=v.get("NOT SINCERE"), sincere=v.get("SINCERE"), could_not_judge=v.get("COULD NOT JUDGE"))
    return {k: x for k, x in out.items() if x is not None}


PAGE_TITLE = "Temporary Work Bundle Monitor"


def page_md(L):
    """The page section: shares, deferral counts and sincerity verdicts. No token and no spend figure."""
    out = ["## " + PAGE_TITLE, ""]
    if L.get("state") != "measured":
        return out + ["Could not look: %s. These numbers are UNMEASURED, not 0." % L.get("cause"), ""]
    w = L.get("window") or {}
    out.append("Day %s to %s (UTC), made %s. The Conductor reads the report: `%s` (%s)." % (
        w.get("since"), w.get("until"), L.get("made"), L.get("report") or "no report", L.get("report_state")))
    out.append("")
    if L.get("share_state") == "measured":
        out += ["| pipeline | bundle runs (closes) | bundles of one (closes) | single-ticket runs (closes) |",
                "|---|---|---|---|"]
        for pl in ("maturation", "workshop"):
            s = L["share"][pl]
            out.append("| %s | %s (%s) | %s (%s) | %s (%s) |" % (
                pl, s["bundle"]["runs"], s["bundle"]["closes"], s["bundle_of_one"]["runs"],
                s["bundle_of_one"]["closes"], s["single"]["runs"], s["single"]["closes"]))
    else:
        out.append("Share: could not look: %s." % L.get("share_cause"))
    out.append("")
    d = L.get("deferral") or {}
    if d.get("state") == CNL:
        out.append("Deferral: could not look: %s." % d.get("cause"))
    else:
        out.append("Set-downs %s (by class: %s; by role: %s); program filings %s; backward moves %s; open waits that "
                   "name the Conductor %s; LEFT OPEN notes %s; runs that ended with work owed %s; filed %s, closed %s."
                   % (d.get("set_downs"), _kv(d.get("by_class")), _kv(d.get("by_role")), d.get("program_filings"),
                      L.get("backward_moves"), d.get("waits_naming_conductor_open"), d.get("left_open_notes"),
                      d.get("runs_ending_with_work_owed"), d.get("filed"), d.get("closed")))
    v = L.get("verdicts")
    out.append("")
    out.append("Sincerity (a Sonnet judge, each set-down and backward move): %s; not sincere by role: %s." % (
        _kv(v) if isinstance(v, dict) else v, _kv(L.get("not_sincere_by_role")) or "none"))
    return out + [""]


def _kv(d):
    return ", ".join("%s %s" % (k, v) for k, v in sorted((d or {}).items())) or "none"


def page_html(L):
    import html
    rows = page_md(L)[2:]
    body = []
    for ln in rows:
        if ln.startswith("|---"):
            continue
        if ln.startswith("|"):
            cells = [c.strip() for c in ln.strip("|").split("|")]
            tag = "th" if "pipeline" in cells[0] else "td"
            body.append("<tr>%s</tr>" % "".join("<%s>%s</%s>" % (tag, html.escape(c), tag) for c in cells))
        elif ln:
            body.append("<p class='m'>%s</p>" % html.escape(ln).replace("`", ""))
    tbl = "".join(b for b in body if b.startswith("<tr>"))
    ps = "".join(b for b in body if b.startswith("<p"))
    return "<h2>%s</h2>%s%s" % (html.escape(PAGE_TITLE), ("<table>%s</table>" % tbl) if tbl else "", ps)


# ------------------------------------------------------------------------------------------------ cli -----------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=("measure", "judge", "calibrate", "daily", "page"))
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--json", action="store_true")
    o = ap.parse_args(argv)
    now = time.time()
    t1 = ep(o.until) or now
    t0 = ep(o.since) or (t1 - DAY)
    if o.cmd == "daily":
        return daily(now)
    if o.cmd == "page":
        print("\n".join(page_md(latest())))
        return 0
    S = gather()
    if o.cmd == "calibrate":
        rows, dis = calibrate(S)
        p = os.path.join(out_dir(create=True), "calibration_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
        write_json(p, {"rows": rows, "disagreements": dis})
        print("CALIBRATION %d of %d agree; %d disagree; rows in %s" % (len(rows) - dis, len(rows), dis, p))
        return 0
    R = measure(S, t0, t1, now)
    if o.cmd == "judge":
        for v in judge_day(R, S):
            print(json.dumps(v, default=str))
        return 0
    print(json.dumps(R, indent=1, default=str) if o.json else json.dumps(
        {k: R[k] for k in ("window", "sources", "share", "deferral", "moves", "live") if k in R}, indent=1,
        default=str)[:20000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
