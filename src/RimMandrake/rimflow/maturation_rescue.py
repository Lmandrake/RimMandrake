#!/usr/bin/env python3
"""maturation_rescue.py: when the Maturation Pipeline PROPOSES a Fable Rescue for a mod that circles. It never launches
one: a proposal is a line for the Conductor, who launches or declines.

Item RIMMANDRAKE_PROPOSE_RESCUE_WHEN_MOD_CIRCLES_BOTH_HAND_LAUNCHED. The owner, 2026-11-16 about 10:10 PM PST, on the
Conductor's criteria: "yup. Then we'll watch stats to see if we need to tune that." Both rescues that night (Gimme Some
Slack, Pyrelands) were hand launches; the criteria are the Rescue brief's "Why you were called"
(the Rescue setting of src/RimMandrake/rimflow/roles/builder.md, "When you are stuck"), each read from a record,
never guessed:

  C1 flip      the same check went PASS on one build and FAIL on a later one, its own file not edited in between
               (blind cycles: lane2/reruns.jsonl then reruns_after_fix.jsonl; in-game visits: rows.jsonl by mod_sha)
  C2 nudge     the same tuning number changed in one direction and then the other (git history of the mod's source
               since its version was seeded: a line whose only change is one numeric literal)
  C3 refused   the same bar refused in two judging rounds running (a blind cycle's Problem faults and red offline bars;
               an in-game visit's last-row FAIL, through the test table's decides)
  C4 ceiling   the tick paused the mod at its stage spend ceiling and the certificate for its next move is not green
  C5 retired   (was: a bar whose every in-game decider ran on a site that switched a mechanic off). Conductor ruling
               2026-11-25 on item RIMMANDRAKE_COMPARE_TEST_PILOT_WITH_FABLE_RESCUER_ONE_MAY_HOLD_BOTH: 19 proposals, none
               launched; such a decider is a wrong scene, repaired at Stage 6 (maturation.WRONG_CHECK_RULE), with a
               Test Pilot sitting if the repaired scene still fails. Its old proposals stay in `status` as retired.
               undo: restore _c5, read_unrun and "C5" in CRITERIA from git.

    python3 src/RimMandrake/rimflow/maturation_rescue.py scan [MOD ...] [--until ISO] [--json]
            a dry run over the records: what would be proposed now (or from the records as they stood at ISO); writes
            nothing
    python3 src/RimMandrake/rimflow/maturation_rescue.py status          per criterion: proposals, launched, solved,
            false alarms (one screen)
    python3 src/RimMandrake/rimflow/maturation_rescue.py list            every proposal with its outcome so far
    python3 src/RimMandrake/rimflow/maturation_rescue.py outcome PID launched --item ID [--unit U]
    python3 src/RimMandrake/rimflow/maturation_rescue.py outcome PID declined --why "..." [--false-alarm]
    python3 src/RimMandrake/rimflow/maturation_rescue.py outcome PID ended --solved yes|no [--usd N] [--tokens N]
            [--false-alarm] [--why "..."]
    python3 src/RimMandrake/rimflow/maturation_rescue.py rescue MOD --item ID --started ISO [--ended ISO]
            [--solved yes|no] [--why "..."]     a rescue launched without a proposal (by hand): its evidence is covered

The tick (maturation_dispatch._tick, applied) calls observe(): new evidence on an advancing mod that is not held by the
owner (mod_owner_hold.json), not under a live rescue and not older than a rescue's end becomes ONE proposal: one row in
<dispatch state dir>/rescue_proposals.jsonl (append only), one `RESCUE PROPOSED:` line in the Conductor log carrying
RAISE FIRST, and a Needs Conductor line in the reading. The same evidence (its key) is proposed once, ever.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# ---- the settings: FIRST GUESSES, to be tuned from `status` (owner, 2026-11-16: "Then we'll watch stats to see if we
# need to tune that."). Each says what it counts; none is a bar.
SETTINGS = {
    "flip_regressions_min": 1,      # C1: PASS on a build, FAIL on a later build, the check's file unchanged: how many
                                    #     such regressions of ONE check propose (a FAIL then PASS is a fix, never one)
    "nudge_reversals_min": 1,       # C2: direction reversals of ONE number (up then down, or down then up)
    "nudge_window_days": 14,        # C2: changes older than this, or older than the version's seed, are not read
    "refused_rounds_running": 2,    # C3: consecutive judging rounds (blind cycles, or in-game visits) refusing one bar
    "rescue_cover_s": 86400,        # a rescue that ended less than this ago: nothing at all is proposed on its mod
}
CRITERIA = ("C1", "C2", "C3", "C4")
# a criterion that no longer proposes: its old proposals still tally and can still take an outcome
RETIRED = {"C5": "no test ran the real mechanic"}
NAMES = dict({"C1": "check flips pass/fail across builds", "C2": "tuning number nudged back and forth",
              "C3": "same bar refused two rounds running", "C4": "stage ceiling without a green certificate"}, **RETIRED)
STATS = "rescue_proposals.jsonl"
RESCUE_RX = re.compile(r"_RESCUE_")       # a rescue item launched by hand before this file existed names RESCUE
SRC_EXT = (".cs", ".py", ".xml")
COMMENT = ("//", "#", "<!--", "*", "\"\"\"")     # a number in a comment line is prose, not a tuning number
# a literal with its C# suffix (0.35f, 2d, 1e-3): without the suffix allowed, "0.30f" read as "0" and every C# float
# change went unseen (found by selftest_maturation_rescue). The group is the number; the suffix is dropped.
NUM_RX = re.compile(r"(?<![A-Za-z_0-9.])(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)[fFdDmM]?(?![A-Za-z_0-9.])")
NEXT_STAGE = {"offline_build": "blind_challenge", "blind_challenge": "in_game", "in_game": "pre_human",
              "pre_human": "his_walk"}


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ts(v):
    """An ISO time (Z or offset) or epoch seconds -> epoch seconds, else None."""
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    if not isinstance(v, str) or not v:
        return None
    try:
        t = dt.datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return t.timestamp()


# ---- readers: records -> one plain dict per mod (all I/O is here) ------------------------------------------------------

def _jsonl(path, errors):
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    r = json.loads(line)
                except ValueError:
                    errors.append("%s line %d does not parse" % (path, i))
                    continue
                if isinstance(r, dict):
                    out.append(r)
    except FileNotFoundError:
        pass
    except OSError as e:
        errors.append("%s: %s" % (path, e))
    return out


def _json(path, errors):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as e:
        errors.append("%s does not read: %s" % (path, e))
        return None


def _rel(root, p):
    return os.path.relpath(p, root)


def _numbers(root, d, rx):
    out = []
    for f in os.listdir(d) if os.path.isdir(d) else []:
        m = re.match(rx, f)
        if m and os.path.isdir(os.path.join(d, f)):
            out.append(int(m.group(1)))
    return sorted(out)


def _bars_split(v):
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return [x.strip() for x in re.split(r"[,;]", str(v or "")) if x.strip()]


def _test_file(cmd):
    """The check's own file in its command (the first path ending .py or .cs), or None."""
    m = re.search(r"([\w./\\-]+\.(?:py|cs))\b", str(cmd or ""))
    return m.group(1).replace("\\", "/") if m else None


def _exit_reds(text):
    """The bars the Exit block's offline_bars marks red (maturation.exit_block's reading)."""
    import maturation as M
    got = M.exit_block(text) or {}
    return [b for b, v in (got.get("offline_bars") or {}).items() if v == "red"]


def read_blind(root, mod, until, errors):
    """-> (check runs [{test, result, build, at, path, file}], rounds [{kind, n, refused {bar: [why]}, at, path}])."""
    import maturation as M
    rec = M.load(root, mod) or {}
    opened = {k: ts(v) for k, v in M.cycle_openings(rec).items()}
    base = os.path.join(root, "design", "concepts", mod, "version", "blind_challenge")
    runs, rounds = [], []
    for n in _numbers(root, base, r"cycle_(\d+)$"):
        at = opened.get(n)
        if until is not None and at is not None and at > until:
            continue
        d = os.path.join(base, "cycle_%d" % n)
        edited = _json(os.path.join(d, "tests_edited.json"), errors)      # a list, or {"edited": [...]} (both on disk)
        edited = edited.get("edited", edited.get("tests_edited")) if isinstance(edited, dict) else edited
        ed = {str(x.get("path", "")).replace("\\", "/") for x in edited if isinstance(x, dict)} \
            if isinstance(edited, list) else set()
        for j, name in enumerate(("reruns.jsonl", "reruns_after_fix.jsonl")):
            p = os.path.join(d, "lane2", name)
            last = {}
            for r in _jsonl(p, errors):
                if r.get("test") and str(r.get("result")).upper() in ("PASS", "FAIL"):
                    last[r["test"]] = r
            for t, r in last.items():
                f = _test_file(r.get("command"))
                runs.append({"test": t, "result": str(r["result"]).upper(), "build": "cycle_%d%s" % (n, "+fix" if j else ""),
                             "at": (at or 0) + j, "path": _rel(root, p), "file": f,
                             "edited": bool(f and f in ed)})
        refused = {}
        faults = _json(os.path.join(d, "lane2", "faults.json"), errors)
        for x in (faults.get("faults") if isinstance(faults, dict) else faults if isinstance(faults, list) else []) or []:
            if isinstance(x, dict) and str(x.get("class", "")).lower() == "problem":
                for b in _bars_split(x.get("bar") or x.get("bars")):
                    refused.setdefault(b, []).append("Problem %s" % x.get("id", "?"))
        sp = os.path.join(d, "SUMMARY.md")
        try:
            with open(sp, encoding="utf-8") as f:
                for b in _exit_reds(f.read()):
                    refused.setdefault(b, []).append("Exit block red")
        except OSError:
            pass
        rounds.append({"kind": "blind", "n": n, "refused": refused, "at": at, "path": _rel(root, d)})
    return runs, rounds


def read_ingame(root, mod, tt, until, errors):
    """-> (check runs, rounds)."""
    import maturation as M
    rec = M.load(root, mod) or {}
    opened = {k: ts(v) for k, v in M.ingame_openings(rec).items()}
    decides = {}
    for b in (tt or {}).get("bars") or []:
        if isinstance(b, dict) and b.get("id"):
            for t in b.get("decides") or []:
                decides.setdefault(t, []).append(b["id"])
    base = os.path.join(root, "design", "concepts", mod, "version", "in_game")
    runs, rounds = [], []
    for v in _numbers(root, base, r"visit_(\d+)$"):
        at0 = opened.get(v)
        if until is not None and at0 is not None and at0 > until:
            continue
        p = os.path.join(base, "visit_%d" % v, "rows.jsonl")
        # a spoiled run and a random miss are no verdict about the mod (live_kinds.py)
        import live_kinds as LK
        rows = [r for r in _jsonl(p, errors) if r.get("test") and not LK.no_verdict(r)]
        if until is not None:
            rows = [r for r in rows if ts(r.get("at")) is None or ts(r["at"]) <= until]
        by = {}
        for r in rows:          # the last row per (test, build) counts; order is the order of that last row
            k = (r["test"], str(r.get("mod_sha") or "visit_%d" % v))
            by.pop(k, None)
            by[k] = r
        for (t, b), r in by.items():
            res = str(r.get("verdict")).upper()
            if res in ("PASS", "FAIL"):
                runs.append({"test": t, "result": res, "build": "visit_%d@%s" % (v, b[:10]),
                             "at": ts(r.get("at")) or at0 or 0, "path": _rel(root, p),
                             "file": _test_file(r.get("command")), "edited": False})
        last = {}
        for r in rows:
            last[r["test"]] = r
        refused = {}
        for t, r in last.items():
            if str(r.get("verdict")).upper() == "FAIL":
                for b in decides.get(t, []):
                    refused.setdefault(b, []).append("%s FAIL" % t)
        rounds.append({"kind": "visit", "n": v, "refused": refused, "at": at0, "path": _rel(root, os.path.dirname(p))})
    return runs, rounds


def _git(root, args, runner=subprocess.run):
    if runner is subprocess.run:    # log -p of a mod's fourteen days reads 350 to 650 MB of pack
        import own_cgroup
        runner = own_cgroup.run
    r = runner(["git", "-C", root] + args, capture_output=True, text=True, timeout=120)
    return r.stdout if r.returncode == 0 else ""


def _template(line):
    return NUM_RX.sub("#", line.strip())


def read_nudges(root, mod, since, until=None, runner=subprocess.run):
    """C2's reading -> [{file, line, slot, old, new, sha, at}] oldest first: one row per numeric literal that a commit
    changed on a line whose text is otherwise the same, in the mod's source (.cs .py .xml) since `since`."""
    src = "src/RimMandrake/%s" % mod
    if not os.path.isdir(os.path.join(root, src)):
        return []
    args = ["log", "--reverse", "-p", "--unified=0", "--no-renames", "--format=@@C %H %ct",
            "--since=%d" % int(since)]
    if until is not None:
        args.append("--until=%d" % int(until))
    out = _git(root, args + ["--", src], runner)
    rows, sha, at, path, minus, plus = [], None, None, None, [], []

    def flush():
        if path and path.endswith(SRC_EXT) and minus and len(minus) == len(plus):
            for a, b in zip(minus, plus):
                if a == b or _template(a) != _template(b) or a.strip().startswith(COMMENT):
                    continue
                na, nb = NUM_RX.findall(a), NUM_RX.findall(b)
                for i, (x, y) in enumerate(zip(na, nb)):
                    if x != y:
                        try:
                            rows.append({"file": path, "line": _template(b), "slot": i, "old": float(x),
                                         "new": float(y), "sha": sha, "at": at})
                        except ValueError:
                            pass
        minus.clear()
        plus.clear()

    for ln in out.split("\n"):
        if ln.startswith("@@C "):
            flush()
            parts = ln.split()
            sha, at = parts[1], float(parts[2]) if len(parts) > 2 else None
        elif ln.startswith("+++ "):
            flush()
            path = ln[6:] if ln.startswith("+++ b/") else None
        elif ln.startswith("@@"):
            flush()
        elif ln.startswith("-") and not ln.startswith("---"):
            minus.append(ln[1:])
        elif ln.startswith("+") and not ln.startswith("+++"):
            plus.append(ln[1:])
    flush()
    return rows


def read_records(root, mod, until=None, ceiling=None, certificate=None, runner=subprocess.run, git_root=None):
    """-> the records detect() reads for one mod. ceiling: the tick's pause {at, why, stage} or None. certificate:
    {ok, to} or None (then judge_certificate is read when the mod is at its ceiling)."""
    import maturation as M
    import judge_certificate as JC
    errors = []
    rec = M.load(root, mod)
    if not isinstance(rec, dict):
        errors.append("design/concepts/%s/version/stage_record.json does not read" % mod)
        rec = {}
    tt, err = JC.read_table(root, mod)
    if tt is None:
        errors.append(err)
    b_runs, b_rounds = read_blind(root, mod, until, errors)
    i_runs, i_rounds = read_ingame(root, mod, tt, until, errors)
    seed = ts((rec.get("seeded") or {}).get("at"))
    now = until if until is not None else time.time()
    since = max(x for x in (seed, now - SETTINGS["nudge_window_days"] * 86400) if x is not None)
    try:
        nudges = read_nudges(git_root or root, mod, since, until, runner)
    except (OSError, subprocess.SubprocessError) as e:
        nudges, _ = [], errors.append("git history: %s" % e)
    stage = rec.get("stage")
    if ceiling and certificate is None and stage in NEXT_STAGE:
        c = M.certificate(root, mod, NEXT_STAGE[stage])
        certificate = {"ok": bool(c.get("ok")) and not c.get("did_not_run"), "to": NEXT_STAGE[stage],
                       "refused": sum(1 for r in c.get("rows") or [] if r.get("status") == "REFUSED")}
    return {"mod": mod, "stage": stage, "stage_since": ts(rec.get("since")), "checks": b_runs + i_runs,
            "rounds": b_rounds + i_rounds, "nudges": nudges, "ceiling": ceiling, "certificate": certificate,
            "errors": errors}


def last_ceilings(path, until=None):
    """The tick history (ticks.jsonl rows {at, decisions {mod: [decision, ...]}}) -> {mod: {at, why, stage}} for each mod
    whose decision in the last tick at or before `until` was `ceiling`."""
    last, bad = None, []
    for r in _jsonl(path, bad):
        if isinstance(r.get("at"), (int, float)) and (until is None or r["at"] <= until):
            last = r
    out = {}
    for mod, d in ((last or {}).get("decisions") or {}).items():
        if isinstance(d, list) and d and d[0] == "ceiling":
            out[mod] = {"at": last["at"], "why": "the tick of %s paused it at its stage ceiling" % iso(last["at"]),
                        "stage": None}
    return out


# ---- the detector: a pure function over the records ----------------------------------------------------------------

def _c1(r, s):
    out, seqs = [], {}
    for x in r.get("checks") or []:
        seqs.setdefault(x["test"], []).append(x)
    for t, seq in seqs.items():
        seq = sorted(seq, key=lambda x: x.get("at") or 0)
        regs = [(a, b) for a, b in zip(seq, seq[1:]) if a["result"] == "PASS" and b["result"] == "FAIL"
                and not b.get("edited")]
        if len(regs) >= s["flip_regressions_min"]:
            a, b = regs[-1]
            out.append({"criterion": "C1", "key": "C1:%s:%s" % (t, b["build"]), "since": b.get("at"),
                        "evidence": {"check": t, "regressions": len(regs), "min": s["flip_regressions_min"],
                                     "pass_on": a["build"], "fail_on": b["build"], "paths": [a["path"], b["path"]],
                                     "runs": " ".join("%s:%s" % (x["build"], x["result"][0]) for x in seq[-8:])}})
    return out


def _c2(r, s):
    # One number is a chain of values: a change a->b continues the chain (same file, line text, slot) whose value is
    # now a, else starts its own. Lines that share a text (`<min>#</min>` in one file) stay apart by their values.
    chains = {}
    for x in r.get("nudges") or []:
        cs = chains.setdefault((x["file"], x["line"][:160], x["slot"]), [])  # cut-ok: existing nudge chain and dedup key
        c = next((c for c in reversed(cs) if c[-1]["new"] == x["old"] and c[-1]["sha"] != x["sha"]), None)
        if c is None:
            cs.append([x])
        else:
            c.append(x)
    out = []
    for (f, line, slot), cs in chains.items():
        for seq in cs:
            out += _c2_chain(f, line, slot, seq, s)
    return out


def _c2_chain(f, line, slot, seq, s):
    out = []
    if len(seq) > 1:
        dirs = [(1 if x["new"] > x["old"] else -1, x) for x in seq if x["new"] != x["old"]]
        revs = [b for (da, _), (db, b) in zip(dirs, dirs[1:]) if da != db]
        if len(revs) >= s["nudge_reversals_min"]:
            last = revs[-1]
            out.append({"criterion": "C2", "key": "C2:%s:%s:%d:%s" % (f, line, slot, last["sha"][:12]),
                        "since": last.get("at"),
                        "evidence": {"file": f, "line": last["line"], "reversals": len(revs), "min": s["nudge_reversals_min"],
                                     "values": " -> ".join([("%g" % seq[0]["old"])] + ["%g" % x["new"] for x in seq]),
                                     "shas": [x["sha"][:12] for x in seq]}})
    return out


def _c3(r, s):
    out, need = [], s["refused_rounds_running"]
    for kind in ("blind", "visit"):
        rs = sorted([x for x in r.get("rounds") or [] if x.get("kind") == kind], key=lambda x: x["n"])
        bars = sorted({b for x in rs for b in x.get("refused") or {}})
        for b in bars:
            run, best = [], []      # the latest run of consecutive rounds refusing b that reaches `need`
            for x in rs:
                if b not in (x.get("refused") or {}):
                    run = []
                    continue
                run = run + [x] if run and run[-1]["n"] == x["n"] - 1 else [x]
                if len(run) >= need:
                    best = list(run)
            run = best
            if len(run) >= need:
                ns = [x["n"] for x in run]
                out.append({"criterion": "C3", "key": "C3:%s:%s:%d" % (kind, b, ns[-1]), "since": run[-1].get("at"),
                            "evidence": {"bar": b, "rounds": "%s %s" % (kind, ",".join(map(str, ns))), "min": need,
                                         "why": run[-1]["refused"][b][:3], "paths": [x["path"] for x in run[-need:]]}})
    return out


def _c4(r, s):
    c, cert = r.get("ceiling"), r.get("certificate")
    if not c or (isinstance(cert, dict) and cert.get("ok") is True):
        return []
    stage = c.get("stage") or r.get("stage")
    return [{"criterion": "C4", "key": "C4:%s:%s" % (stage, int(r.get("stage_since") or 0)), "since": c.get("at"),
             "evidence": {"stage": stage, "why": str(c.get("why") or ""),
                          "certificate": "unread" if not isinstance(cert, dict) else "%s, %s REFUSED row(s), to %s" % (
                              "green" if cert.get("ok") else "not green", cert.get("refused", "?"), cert.get("to")),
                          "paths": ["design/concepts/%s/version/stage_record.json" % r.get("mod"),
                                    "<dispatch state dir>/reading.json"]}}]


def unmeasured(r):
    """-> {criterion: why} for what this mod's records cannot show today."""
    out = {}
    if not r.get("checks"):
        out["C1"] = "no blind rerun or in-game row with a PASS or FAIL"
    if not (r.get("rounds") or []):
        out["C3"] = "no blind cycle or in-game visit folder"
    return out


def covered(mod, since, rescues, now, cover_s):
    """Why this evidence is not proposed because of a rescue on the mod, or ''."""
    for x in rescues or []:
        if x.get("mod") != mod:
            continue
        if x.get("live"):
            return "a rescue is live on it (%s)" % x.get("item")
        end = x.get("ended")
        if end is not None and now - end < cover_s:
            return "a rescue (%s) ended %.1f h ago" % (x.get("item"), (now - end) / 3600.0)
        if end is not None and (since is None or since <= end):
            return "the rescue %s, ended %s, had this evidence" % (x.get("item"), iso(end))
    return ""


def detect(records, settings=None, now=None, holds=(), rescues=(), seen=()):
    """-> (proposals [{mod, criteria, evidence [...], since, keys}], skipped [{mod, why}]): pure, over read_records'
    dicts. holds: owner-held mod keys (lower case); rescues: [{mod, item, live, ended}]; seen: evidence keys already
    proposed. One proposal per mod, carrying every criterion that has new evidence."""
    s = dict(SETTINGS, **(settings or {}))
    now = time.time() if now is None else now
    seen, out, skipped = set(seen), [], []
    for r in records:
        mod = r.get("mod")
        if not mod:
            continue
        if str(mod).lower() in {str(h).lower() for h in holds}:
            skipped.append({"mod": mod, "why": "held by the owner"})
            continue
        found = []
        for fn in (_c1, _c2, _c3, _c4):
            try:
                found += fn(r, s)
            except (KeyError, TypeError, ValueError, AttributeError) as e:
                skipped.append({"mod": mod, "why": "%s did not read: %s: %s" % (fn.__name__[1:].upper(),
                                                                              type(e).__name__, e)})
        new = []
        for f in found:
            if f["key"] in seen:
                continue
            why = covered(mod, f.get("since"), rescues, now, s["rescue_cover_s"])
            if why:
                skipped.append({"mod": mod, "why": "%s: %s" % (f["key"], why)})
                continue
            new.append(f)
        if new:
            times = [f["since"] for f in new if f.get("since") is not None]
            out.append({"mod": mod, "criteria": sorted({f["criterion"] for f in new}), "evidence": new,
                        "keys": [f["key"] for f in new], "since": max(times) if times else None})
    return out, skipped


# ---- stats: append-only, in the Dispatch state dir ------------------------------------------------------------------

def stats_path():
    import maturation_dispatch as MD
    return os.path.join(MD.sdir(), STATS)


def read_stats(path=None):
    rows, bad = [], []
    for r in _jsonl(path or stats_path(), bad):
        if r.get("kind") in ("proposal", "outcome", "rescue"):
            rows.append(r)
    return rows


def append(row, path=None):
    with open(path or stats_path(), "a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")


def seen_keys(rows):
    return {k for r in rows if r.get("kind") == "proposal" for k in r.get("keys") or []}


def rescues_of(rows, runs_seen=None):
    """-> [{mod, item, live, ended}] from the stats (launched outcomes and hand rescue rows) and, for a run whose item
    names a recorded rescue item or _RESCUE_, its live state from the tick's runs_seen ({mod: [{item, end}]})."""
    props = {r["id"]: r for r in rows if r.get("kind") == "proposal"}
    out = {}
    for r in rows:
        if r.get("kind") == "rescue":
            out[r["item"]] = {"mod": r["mod"], "item": r["item"], "live": r.get("ended") is None,
                              "ended": ts(r.get("ended"))}
        elif r.get("kind") == "outcome" and r.get("pid") in props and r.get("item"):
            if r.get("outcome") == "launched":
                out.setdefault(r["item"], {"mod": props[r["pid"]]["mod"], "item": r["item"], "live": True,
                                           "ended": None})
            elif r.get("outcome") == "ended" and r["item"] in out:
                out[r["item"]].update(live=False, ended=ts(r.get("at")))
    for mod, runs in (runs_seen or {}).items():
        for x in runs or []:
            item = str(x.get("item") or "")
            if item in out or RESCUE_RX.search(item):
                end = x.get("end")
                cur = out.setdefault(item, {"mod": mod, "item": item, "live": end is None, "ended": end})
                if end is None:
                    cur["live"] = True
                elif cur.get("ended") is None or end > cur["ended"]:
                    cur.update(live=False, ended=end)
    return list(out.values())


def pid_of(mod, now):
    return "rp-%s-%d" % (re.sub(r"[^a-z0-9]", "", mod.lower())[:24], int(now))


def log_line(p, pid, now):
    ev = p["evidence"]
    parts = []
    for c in p["criteria"]:
        mine = [e for e in ev if e["criterion"] == c]
        e0 = mine[0]["evidence"]
        what = e0.get("check") or e0.get("bar") or e0.get("file") or e0.get("stage") or "?"
        parts.append("%s %s x%d (%s)" % (c, NAMES[c], len(mine), what))
    path = next((e["evidence"].get("paths", [None])[-1] for e in ev if e["evidence"].get("paths")), None)
    return ("RESCUE PROPOSED: %s %s — %s; evidence %s; `python3 src/RimMandrake/rimflow/maturation_rescue.py list` — "
            "RAISE FIRST: read it, then launch a builder in the Rescue setting (roles/builder.md) and record `maturation_rescue.py "
            "outcome %s launched --item ID`, or `outcome %s declined --why \"...\"`; nothing was launched\n" % (
                iso(now), p["mod"], "; ".join(parts), path or "(see list)", pid, pid))


def conductor_log_path(fx=None):
    if fx and fx.get("conductor_log"):
        return fx["conductor_log"]
    with open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8") as f:
        return json.load(f)["no_handoff"]["conductor_log"]


def write_log(line, fx=None):
    try:
        p = conductor_log_path(fx)
        import conductor_log_guard
        conductor_log_guard.refuse_if_test(p)
        with open(p, "a", encoding="utf-8") as f:
            f.write("\n" + line)
        return "logged"
    except (OSError, ValueError, KeyError, TypeError) as e:
        return "conductor log failed: %s" % e


def observe(root, cfg, st, facts, rows, now, rd, fx=None):
    """The tick's pass (applied ticks only; the caller guards it): read each advancing, not held mod's records, detect,
    and write each new proposal once (stats row, Conductor log line, Needs Conductor line). -> rd with rd['rescue']."""
    import mod_owner_hold as OH
    fx = fx or {}
    path = fx.get("stats") or stats_path()
    rows_s = read_stats(path)
    holds = set(fx["holds"]()) if "holds" in fx else set(OH.load())
    mods = [m for m in cfg.get("advancing") or []]
    ceil = {r["mod"]: {"at": now, "why": r.get("why"), "stage": r.get("stage")} for r in rows or []
            if r.get("decision") == "ceiling"}
    if "records" in fx:
        recs = fx["records"](mods, ceil)
    else:
        recs = []
        for m in mods:
            if OH.key(m) in holds:
                recs.append({"mod": m})
                continue
            cert = (facts.get(m) or {}).get("certificate")
            cert = {"ok": bool(cert.get("ok")) and not cert.get("did_not_run"), "to": cert.get("to"),
                    "refused": sum(1 for x in cert.get("rows") or [] if x.get("status") == "REFUSED")} if (
                isinstance(cert, dict) and m in ceil and cert.get("to") == NEXT_STAGE.get((facts.get(m) or {}).get(
                    "stage"))) else None
            recs.append(read_records(root, m, ceiling=ceil.get(m), certificate=cert))
    runs_seen = {m: (facts.get(m) or {}).get("runs_seen") for m in facts or {}}
    props, skipped = detect(recs, fx.get("settings"), now, holds, rescues_of(rows_s, runs_seen), seen_keys(rows_s))
    told = []
    for p in props:
        pid = pid_of(p["mod"], now)
        append({"kind": "proposal", "id": pid, "at": iso(now), "mod": p["mod"], "criteria": p["criteria"],
                "keys": p["keys"], "since": iso(p["since"]) if p.get("since") else None,
                "evidence": p["evidence"], "settings": dict(SETTINGS, **(fx.get("settings") or {}))}, path)
        line = log_line(p, pid, now)
        told.append({"id": pid, "mod": p["mod"], "criteria": p["criteria"], "log": write_log(line, fx)})
        rd.setdefault("needs_conductor", []).append(line.strip())
    rd["rescue"] = {"at": now, "mods_read": len(recs), "proposed": told, "skipped": skipped[:12],
                    "proposals_ever": sum(1 for r in rows_s if r.get("kind") == "proposal") + len(told),
                    "stats": path}
    return rd


# ---- status: per criterion, one screen -------------------------------------------------------------------------------

def tally(rows):
    """-> {criterion: {proposals, launched, declined, solved, unsolved, false_alarms, usd}} from the stats rows."""
    props = {r["id"]: r for r in rows if r.get("kind") == "proposal"}
    last = {}
    for r in rows:
        if r.get("kind") == "outcome" and r.get("pid") in props:
            last.setdefault(r["pid"], []).append(r)
    out = {c: {"proposals": 0, "launched": 0, "declined": 0, "solved": 0, "unsolved": 0, "false_alarms": 0,
               "open": 0, "usd": 0.0} for c in CRITERIA + tuple(RETIRED)}
    for pid, p in props.items():
        outs = last.get(pid, [])
        kinds = {o.get("outcome") for o in outs}
        for c in p.get("criteria") or []:
            if c not in out:
                continue
            t = out[c]
            t["proposals"] += 1
            t["launched"] += "launched" in kinds
            t["declined"] += "declined" in kinds
            t["solved"] += any(o.get("outcome") == "ended" and o.get("solved") is True for o in outs)
            t["unsolved"] += any(o.get("outcome") == "ended" and o.get("solved") is False for o in outs)
            t["false_alarms"] += any(o.get("false_alarm") for o in outs)
            t["open"] += not kinds
            t["usd"] += sum(float(o.get("usd") or 0) for o in outs if o.get("outcome") == "ended")
    return out


def status_text(rows):
    t = tally(rows)
    lines = ["Rescue proposals by criterion (first-guess thresholds; tune from this):",
             "  %-3s %-44s %5s %5s %5s %5s %5s %5s %8s" % ("", "criterion", "prop", "open", "launc", "solvd", "decl",
                                                          "false", "usd")]
    for c in CRITERIA + tuple(RETIRED):
        x = t[c]
        lines.append("  %-3s %-44s %5d %5d %5d %5d %5d %5d %8.2f" % (
            c, "retired: " + NAMES[c] if c in RETIRED else NAMES[c], x["proposals"], x["open"], x["launched"], x["solved"], x["declined"], x["false_alarms"],
            x["usd"]))
    hand = [r for r in rows if r.get("kind") == "rescue"]
    lines.append("  hand rescues (no proposal): %d; settings: %s" % (len(hand), ", ".join(
        "%s=%s" % kv for kv in sorted(SETTINGS.items()))))
    return "\n".join(lines)


def _bool(v):
    return {"yes": True, "no": False}[v]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("scan")
    sc.add_argument("mods", nargs="*")
    sc.add_argument("--until", help="read the records as they stood at this ISO time (git history, row times)")
    sc.add_argument("--json", action="store_true")
    sc.add_argument("--root", default=REPO, help="read design/concepts from here (a `git archive` of an older commit "
                                                 "for a replay); the git history is always this clone's")
    sub.add_parser("status")
    sub.add_parser("list")
    oc = sub.add_parser("outcome")
    oc.add_argument("pid")
    oc.add_argument("outcome", choices=("launched", "declined", "ended"))
    oc.add_argument("--item")
    oc.add_argument("--unit")
    oc.add_argument("--why", default="")
    oc.add_argument("--solved", choices=("yes", "no"))
    oc.add_argument("--usd", type=float)
    oc.add_argument("--tokens", type=int)
    oc.add_argument("--false-alarm", action="store_true")
    rs = sub.add_parser("rescue")
    rs.add_argument("mod")
    rs.add_argument("--item", required=True)
    rs.add_argument("--started", required=True)
    rs.add_argument("--ended")
    rs.add_argument("--solved", choices=("yes", "no"))
    rs.add_argument("--why", default="")
    a = ap.parse_args(argv)
    if a.cmd == "scan":
        import mod_owner_hold as OH
        mods = a.mods or sorted(m for m in os.listdir(os.path.join(a.root, "design", "concepts"))
                                if os.path.isfile(os.path.join(a.root, "design", "concepts", m, "version",
                                                               "stage_record.json")))
        until = ts(a.until) if a.until else None
        if a.until and until is None:
            ap.error("--until %r is not an ISO time" % a.until)
        rows = read_stats() if os.path.isdir(os.path.dirname(stats_path())) else []
        import maturation_dispatch as MD
        ceil = last_ceilings(os.path.join(MD.sdir(), "ticks.jsonl"), until)
        recs = [read_records(a.root, m, until=until, ceiling=ceil.get(m), git_root=REPO) for m in mods]
        props, skipped = detect(recs, None, until or time.time(), set(OH.load()), rescues_of(rows) if not until else
                                [], set() if until else seen_keys(rows))
        if a.json:
            print(json.dumps({"proposals": props, "skipped": skipped,
                              "unmeasured": {r["mod"]: unmeasured(r) for r in recs},
                              "errors": {r["mod"]: r["errors"] for r in recs if r["errors"]}}, indent=1, default=str))
            return 0
        print("scan of %d mod(s)%s: %d proposal(s); dry run, nothing written" % (
            len(recs), " as of %s" % a.until if a.until else "", len(props)))
        for p in props:
            print("  %s: %s" % (p["mod"], ", ".join(p["criteria"])))
            for e in p["evidence"][:12]:
                print("    %s %s" % (e["criterion"], json.dumps(e["evidence"], default=str)[:260]))  # cut-ok: terminal display
        for r in recs:
            u = unmeasured(r)
            if u or r["errors"]:
                print("  %s unmeasured: %s%s" % (r["mod"], "; ".join("%s %s" % kv for kv in sorted(u.items())) or "-",
                                                 "; errors: %s" % "; ".join(r["errors"][:3]) if r["errors"] else ""))
        for s in skipped[:20]:
            print("  skipped %s: %s" % (s["mod"], s["why"]))
        return 0
    rows = read_stats()
    if a.cmd == "status":
        print(status_text(rows))
        try:
            import maturation_dispatch as MD
            with open(os.path.join(MD.sdir(), "reading.json"), encoding="utf-8") as f:
                rb = json.load(f).get("rescue")
            print("  last tick pass: %s" % ("none in reading.json" if not rb else "%s, %d mod(s) read, %d proposed now"
                                            % (iso(rb["at"]), rb.get("mods_read", 0), len(rb.get("proposed") or []))))
        except (OSError, ValueError, KeyError, TypeError) as e:
            print("  last tick pass: reading.json does not read (%s)" % e)
        print("  stats: %s" % stats_path())
        return 0
    if a.cmd == "list":
        outs = {}
        for r in rows:
            if r.get("kind") == "outcome":
                outs.setdefault(r.get("pid"), []).append(r.get("outcome"))
        for r in rows:
            if r.get("kind") == "proposal":
                print("%s %s %s %s [%s]" % (r["id"], r["at"], r["mod"], ",".join(r["criteria"]),
                                            ",".join(outs.get(r["id"], [])) or "open"))
                for e in r.get("evidence") or []:
                    print("    %s %s" % (e["criterion"], json.dumps(e["evidence"], default=str)[:220]))  # cut-ok: terminal display
            elif r.get("kind") == "rescue":
                print("rescue %s %s started %s ended %s" % (r["mod"], r["item"], r.get("started"), r.get("ended")))
        return 0
    if a.cmd == "outcome":
        if a.pid not in {r["id"] for r in rows if r.get("kind") == "proposal"}:
            ap.error("no proposal %s in %s" % (a.pid, stats_path()))
        if a.outcome == "launched" and not a.item:
            ap.error("launched needs --item")
        if a.outcome == "declined" and not a.why:
            ap.error("declined needs --why")
        if a.outcome == "ended" and not a.solved:
            ap.error("ended needs --solved yes|no")
        item = a.item or next((r.get("item") for r in rows if r.get("kind") == "outcome" and r.get("pid") == a.pid
                               and r.get("item")), None)
        row = {"kind": "outcome", "pid": a.pid, "at": iso(time.time()), "outcome": a.outcome, "item": item,
               "unit": a.unit, "why": a.why, "false_alarm": a.false_alarm}
        if a.solved:
            row["solved"] = _bool(a.solved)
        if a.usd is not None:
            row["usd"] = a.usd
        if a.tokens is not None:
            row["tokens"] = a.tokens
        append(row)
        print("recorded %s %s" % (a.pid, a.outcome))
        return 0
    if a.cmd == "rescue":
        if ts(a.started) is None or (a.ended and ts(a.ended) is None):
            ap.error("--started/--ended must be ISO times")
        row = {"kind": "rescue", "mod": a.mod, "item": a.item, "started": a.started, "ended": a.ended,
               "why": a.why, "at": iso(time.time())}
        if a.solved:
            row["solved"] = _bool(a.solved)
        append(row)
        print("recorded hand rescue %s on %s" % (a.item, a.mod))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
