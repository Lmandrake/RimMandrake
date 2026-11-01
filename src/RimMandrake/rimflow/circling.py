#!/usr/bin/env python3
"""RW2: circling read from outside a relentless run, from tool records and the run's clone, never the worker's words.

Named at each tick: test_share (a), no_change (b), oscillation (c, A-B-A), trivial_churn. A `learn` line is no finding:
every worker is told to write one every 20 minutes, a circling one included. A finding is a NEW read target.
Report-only. Stopping needs `stop` on AND a replay verdict from this code on these thresholds under `false_stop_limit`
(stop_gate). Thresholds: relentless_rules.json `circling`. Design: operating_requirements_2026-11-01.md RW2.
    python3 circling.py replay --labels <file.json> [--write]
"""
import argparse
import datetime
import difflib
import hashlib
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UNTRACKED_MAX = 5 * 10**6
MARKS_MAX = 20000       # lines of one file past which a move is read as the whole file, not line by line
VERDICT = os.path.join(HERE, "circling_replay.json")
LIMITS = ("test_share_limit", "test_share_min", "no_change_min", "finding_min_new", "oscillation_limit",
          "churn_min", "churn_moves", "churn_max_lines")

# anchored on what a shell segment RUNS: a grep of a selftest file is reading, a heredoc writing one is editing
TEST_RX = re.compile(r"((python3?|bash|sh)\s+)?\S*(run_selftests\.py|selftest_\w+\.py)|pytest\b|python3? -m (pytest|unittest)\b")
LIVE_RX = re.compile(r"(\./game|\./bridge|modcheck)\b|((python3?)\s+)?\S*(proof_\w+|validation\w*)\.py")
BUILD_RX = re.compile(r"((python3?)\s+)?\S*(winbuild|deploy_custom_mods)\.py|dotnet\b|msbuild\b|\./publish\b")
WAIT_RX = re.compile(r"(sleep|waitfor)\b")
EDIT_RX = re.compile(r"sed\s+-i|git\s+(commit|add)\b|(cat|echo|printf|tee)\b.*>\s*[\w./~-]+")
READ_RX = re.compile(r"(grep|rg|cat|head|tail|sed|awk|ls|find|wc|diff|jq|git\s+(-C\s+\S+\s+)?(log|show|diff|grep|blame|status))\b")
REPORT_RX = re.compile(r"\brelentless\.py\b")    # a worker's beat and learn lines: every run writes them
HEREDOC_RX = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\s*\1\b", re.S)
PREFIX_RX = re.compile(r"^(\s*(timeout\s+\S+|\w+=\S*|cd\s+\S+|set\s+-o\s+\w+)\s+)+")
COMMENT = {".py": "#", ".sh": "#", ".yml": "#", ".yaml": "#", ".toml": "#", ".cs": "//", ".js": "//", ".ts": "//",
           ".xml": "<!--", ".html": "<!--"}


def classify(name, inp):
    """-> (kind, target). RW1's six kinds; `target` names what was looked at or run, None when it says nothing."""
    inp = inp if isinstance(inp, dict) else {}
    if name in ("Edit", "Write", "NotebookEdit"):
        return "editing", None
    if name == "Read":
        return "reading", "read:%s:%s" % (inp.get("file_path"), inp.get("offset") or 0)
    if name in ("Grep", "Glob"):
        return "reading", "search:%s:%s" % (inp.get("pattern"), inp.get("path") or "")
    if name != "Bash":
        return "reading" if name in ("WebFetch", "WebSearch", "ToolSearch") else "other", None
    cmd = str(inp.get("command") or "")
    segs = [PREFIX_RX.sub("", x.strip()) for x in re.split(r"[;&|\n]+", HEREDOC_RX.sub("", cmd))]
    target = " ".join(cmd.split())
    for kind, rx in (("selftest", TEST_RX), ("live", LIVE_RX), ("build", BUILD_RX), ("waiting", WAIT_RX),
                     ("editing", EDIT_RX)):
        if any(rx.match(x) for x in segs):
            return kind, target
    if "<<" in cmd:
        return "editing", None
    if any(READ_RX.match(x) for x in segs):
        return "reading", target
    return "other", None if REPORT_RX.search(cmd) else target


def _ts(s):
    try:
        return datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def tool_rows(paths, since=0):
    """Claude transcripts -> time-ordered {t0, t1, kind, target}. t1 None: the tool is still running."""
    rows, by_id = [], {}
    for path in paths:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError:
            continue
        for line in lines:
            try:
                d = json.loads(line)
            except ValueError:      # the live end of a transcript may be half a line
                continue
            c = (d.get("message") or {}).get("content") if isinstance(d.get("message"), dict) else None
            t = _ts(d.get("timestamp"))
            if not isinstance(c, list) or t is None or t < since:
                continue
            for b in c:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use":
                    kind, target = classify(b.get("name"), b.get("input"))
                    row = {"t0": t, "t1": None, "kind": kind, "target": target}
                    rows.append(row)
                    by_id[b.get("id")] = row
                elif b.get("type") == "tool_result" and b.get("tool_use_id") in by_id:
                    by_id[b["tool_use_id"]]["t1"] = t
    return sorted(rows, key=lambda x: x["t0"])


def _collapse(xs):
    out = []
    for x in xs:
        if not out or out[-1] != x:
            out.append(x)
    return out


def _window(samples, start):
    """The samples covering [start, now], the last one before `start` included; [] when the run is younger or any
    reading in the window failed: a tree nobody could read is not an unchanged tree."""
    if not samples or samples[0]["at"] > start:
        return []
    at = max(i for i, s in enumerate(samples) if s["at"] <= start)
    return samples[at:] if all(s.get("raw") for s in samples[at:]) else []


def _spots(win, limit):
    """The distinct changed-line positions the moves in `win` landed on, counted to just past `limit`. None when a move
    in the window was not measured line by line: unknown is no hit."""
    spots = set()
    for a, b in zip(win, win[1:]):
        if a["raw"] == b["raw"]:
            continue
        if b.get("touched") is None:
            return None
        for path, first, end in b["touched"]:
            spots.update((path, i) for i in range(first, min(end, first + limit + 1)))
    return spots


def judge(samples, tools, c, now):
    """Pure. samples: time-ordered {at, raw, sub, lines, touched}, or {at, unmeasured}.
    Churn is where the moves landed, not how big the diff is: a real diff of stable size moves too, on fresh lines. -> [{kind, reading}]. A window the samples
    do not cover says nothing: too young is not clean, and not a hit."""
    hits = []
    tools = [t for t in tools if t["t0"] <= now]

    w = c["test_share_min"] * 60
    win = _window(samples, now - w)
    if win and len({s["sub"] for s in win}) == 1:
        spent, seen = 0.0, set()
        for t in tools:
            if t["kind"] != "selftest":
                continue
            cut = max(0.0, min(t["t1"] or now, now) - max(t["t0"], now - w))
            spent += cut * (2 if cut and t["target"] in seen else 1)    # the tree held still: a rerun's answer was known
            if cut:
                seen.add(t["target"])
        if spent / w > c["test_share_limit"]:
            hits.append({"kind": "test_share", "reading": "%d of %d min testing, tree unchanged" % (spent / 60, w / 60)})

    w = c["no_change_min"] * 60
    win = _window(samples, now - w)
    if win and len({s["sub"] for s in win}) == 1:
        looks = [t for t in tools if t["kind"] in ("reading", "other") and t["target"]]     # a script call reads too
        old = {t["target"] for t in looks if t["t0"] < now - w}
        new = {t["target"] for t in looks if t["t0"] >= now - w} - old
        if len(new) < c["finding_min_new"]:
            hits.append({"kind": "no_change",
                         "reading": "%d min, tree unchanged, %d new things read" % (w / 60, len(new))})

    series = _collapse([s["sub"] for s in samples if s.get("raw")])
    returns = sum(1 for i, h in enumerate(series) if h in series[:i])
    if returns >= c["oscillation_limit"]:
        hits.append({"kind": "oscillation", "reading": "diff returned to an earlier hash %d times" % returns})

    win = _window(samples, now - c["churn_min"] * 60)
    if win:
        moves = len(_collapse([s["raw"] for s in win])) - 1
        spots = _spots(win, c["churn_max_lines"])
        if moves >= c["churn_moves"] and spots is not None and len(spots) <= c["churn_max_lines"]:
            hits.append({"kind": "trivial_churn", "reading": "diff moved %d times in %d min, all in %d changed lines"
                         % (moves, c["churn_min"], len(spots))})
    return hits


def _substance(path, text):
    """The lines of a -U0 -w diff of `path` that are not blank and not a comment."""
    mark = COMMENT.get(os.path.splitext(path)[1].lower())
    t = text.strip()
    return bool(t) and not (mark and t.startswith(mark))


def _mark(marks, path, sign, text):
    marks.setdefault(path, []).append(hashlib.sha256((sign + " ".join(text.split())).encode()).hexdigest()[:8])


def touched(old, new):
    """Two samples' marks -> [[path, first, end]], the changed-line positions that moved, on the new side."""
    out = []
    for path in sorted(set(old) | set(new)):
        a, b = old.get(path, []), new.get(path, [])
        if a == b:
            continue
        if max(len(a), len(b)) > MARKS_MAX:
            out.append([path, 0, max(len(a), len(b))])
            continue
        for tag, _i1, _i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if tag != "equal":
                out.append([path, j1, max(j2, j1 + 1)])
    return out


def _git(clone, *args):
    r = subprocess.run(["git", "--no-optional-locks", "-c", "core.quotepath=off", *args], cwd=clone,
                       capture_output=True, timeout=60, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise RuntimeError(r.stderr.decode("utf-8", "replace")[-200:])
    return r.stdout


def tree_reading(clone, base, noise=()):
    """Read-only (no index refresh, no objects). -> {raw, sub, lines, marks} of the clone against `base`, untracked
    files included: raw moves on any byte, sub only on a line that is neither whitespace nor comment. marks: per file, a
    short hash of each such line in order, what the next sample is compared to; watch keeps them out of the sample."""
    spec = ["--", "."] + [":(exclude)%s" % n.rstrip("/") for n in noise]
    raw = hashlib.sha256(_git(clone, "diff", "--no-ext-diff", "--binary", base, *spec))
    sub, lines, path, head, marks = hashlib.sha256(), 0, "", False, {}
    for ln in _git(clone, "diff", "--no-ext-diff", "-w", "--ignore-blank-lines", "-U0", base, *spec) \
            .decode("utf-8", "replace").split("\n"):
        if ln.startswith("diff --git "):
            head = True
        elif ln.startswith("@@"):
            head = False
        elif head and ln[:4] in ("+++ ", "--- "):       # past the header, "--- x" is a removed "-- x"
            name = ln[4:].strip()
            path = name.split("/", 1)[-1] if name != "/dev/null" else path
        elif head and ln.startswith("Binary files "):
            sub.update(hashlib.sha256(ln.encode()).digest())
            lines += 1
            _mark(marks, path or ln, "", ln)
        elif not head and ln[:1] in "+-" and ln and _substance(path, ln[1:]):
            sub.update((path + ":" + ln).encode())
            lines += 1
            _mark(marks, path, ln[0], ln[1:])
    for rel in _git(clone, "ls-files", "-z", "--others", "--exclude-standard", *spec).decode("utf-8", "replace").split("\0"):
        if not rel:
            continue
        full = os.path.join(clone, rel)
        if os.path.getsize(full) > UNTRACKED_MAX:       # a stray dump: its size and time say whether it moved
            stamp = "%s %s %s" % (rel, os.path.getsize(full), os.path.getmtime(full))
            raw.update(stamp.encode())
            sub.update(stamp.encode())
            _mark(marks, rel, "", stamp)
            continue
        with open(full, "rb") as f:
            data = f.read()
        raw.update(rel.encode() + b"\0" + data)
        sub.update(rel.encode() + b"\0")
        for ln in data.decode("utf-8", "replace").split("\n"):
            if _substance(rel, ln):
                sub.update(" ".join(ln.split()).encode() + b"\n")
                lines += 1
                _mark(marks, rel, "+", ln)      # as the diff will read it once the file is added
    return {"raw": raw.hexdigest()[:16], "sub": sub.hexdigest()[:16], "lines": lines, "marks": marks}


def transcript_paths(clone, since=0):
    d = os.path.expanduser("~/.claude/projects/" + re.sub(r"[^A-Za-z0-9]", "-", clone or ""))
    try:
        return sorted(e.path for e in os.scandir(d) if e.name.endswith(".jsonl") and e.stat().st_mtime >= since)
    except OSError:
        return []


def with_touched(store, item, gen, one):
    """A reading -> its sample: marks swapped for `touched`, against the last readable tree of this run. They live in
    one file per item, rewritten each tick, so the sample stays small. `touched` stays absent with nothing to compare."""
    path = os.path.join(store.item_dir(item), "circling_marks.json")
    try:
        with open(path, encoding="utf-8") as f:
            last = json.load(f)
    except (OSError, ValueError):
        last = {}
    one = dict(one)
    marks = one.pop("marks", None)
    if marks is None:
        return one
    if last.get("gen") == gen:
        one["touched"] = touched(last["marks"], marks)
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump({"gen": gen, "marks": marks}, f)
    os.replace(path + ".tmp", path)
    return one


def samples_of(store, item, gen):
    try:
        with open(os.path.join(store.item_dir(item), "circling.jsonl"), encoding="utf-8") as f:
            rows = [json.loads(x) for x in f if x.strip()]
    except OSError:
        return []
    return [s for s in rows if s.get("gen") == gen]


def hits_seen(store):
    try:
        with open(store.p("circling.jsonl"), encoding="utf-8") as f:
            return [json.loads(x) for x in f if x.strip()]
    except OSError:
        return []


def fingerprint(c):
    with open(os.path.abspath(__file__), "rb") as f:
        code = f.read()
    return hashlib.sha256(code + json.dumps({k: c.get(k) for k in LIMITS}, sort_keys=True).encode()).hexdigest()[:16]


def stop_gate(c, path=None):
    """-> (may stop, why). A flag alone never stops. Only a replay of THIS code on THESE thresholds with enough labelled
    runs, strictly under false_stop_limit. A changed threshold or a changed file voids the verdict."""
    if not c.get("stop"):
        return False, "report-only: stop is off"
    try:
        with open(path or VERDICT, encoding="utf-8") as f:
            v = json.load(f)
    except (OSError, ValueError):
        return False, "report-only: no replay verdict"
    if v.get("fingerprint") != fingerprint(c):
        return False, "report-only: the replay was of other code or thresholds"
    if v.get("measured", 0) < c["replay_min_runs"] or not v.get("fine") or not v.get("circling"):
        return False, "report-only: replay holds %s runs, %s needed, both labels" % (v.get("measured"), c["replay_min_runs"])
    if v["wrongful"] / v["fine"] >= c["false_stop_limit"]:
        return False, "report-only: %s wrongful of %s" % (v["wrongful"], v["fine"])
    return True, "replay passed"


def watch(store, fx, r, now, acts, fail):
    """Tick side: sample every running worker, name what fires, once per run and kind. Stops only past stop_gate."""
    c = r.get("circling")
    if not c or not c.get("enabled"):
        return
    seen = {(h["item"], h["gen"], h["kind"]) for h in hits_seen(store)}
    may_stop, why = stop_gate(c)
    for st in store.states():
        if st["status"] != "running" or st.get("reserving") or not st.get("run") or not st.get("clone"):
            continue
        item, gen = st["item"], st["gen"]
        try:
            one = fx.circling_tree(st)
        except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as e:
            one = {"unmeasured": str(e)[:200]}
        store._append(os.path.join(store.item_dir(item), "circling.jsonl"),
                      json.dumps(dict(with_touched(store, item, gen, one), at=now, gen=gen, clone=st["clone"])))
        samples = samples_of(store, item, gen)
        tools = tool_rows(fx.transcripts(st), st["started_at"])
        hits = judge(samples, tools, c, now)
        for h in hits:
            if (item, gen, h["kind"]) not in seen:
                store._append(store.p("circling.jsonl"), json.dumps(dict(h, item=item, gen=gen, at=now, stopped=may_stop,
                                                                         gate=why), sort_keys=True))
                acts.append({"do": "circling", "item": item, "kind": h["kind"], "stopped": may_stop})
        if hits and may_stop:
            text = "; ".join("%s: %s" % (h["kind"], h["reading"]) for h in hits)
            run = st["run"]
            with store.lock():
                st = store.load(item)
                if st["status"] != "running" or st["gen"] != gen:
                    continue
                # a hit is a forced change of approach: fail() turns on the limit
                st["failures"]["circling"] = r["same_failure_limit"] - 1
                fail(store, st, "circling", text, r, now)
            fx.stop(run, force=False)


def summary(store, r, now):
    """What Operations reads in reading.json."""
    c = r.get("circling")
    if not c:
        return None
    day = [h for h in hits_seen(store) if now - h["at"] < 86400]
    kinds = {}
    for h in day:
        kinds[h["kind"]] = kinds.get(h["kind"], 0) + 1
    return {"gate": stop_gate(c)[1], "hits_24h": kinds, "last": day[-5:]}


def replay(store, labels, c):
    """labels: [{item, gen, label: circling|fine, ...}]. The real judge walked over each run's stored samples at each
    sample time. A run with no samples or no transcript is UNMEASURED, never counted as clean; so is a run labelled both
    ways. A run listed twice counts once: replay_min_runs means distinct runs."""
    out = {"fine": 0, "circling": 0, "wrongful": 0, "missed": 0, "unmeasured": [], "runs": []}
    said = {}
    for row in labels:
        said.setdefault((row["item"], row["gen"]), set()).add(row["label"])
    done = set()
    for row in labels:
        run = (row["item"], row["gen"])
        if run in done:
            continue
        done.add(run)
        if len(said[run]) > 1:
            out["unmeasured"].append("%s gen %s: labelled both ways" % run)
            continue
        samples = samples_of(store, row["item"], row["gen"])
        tools = tool_rows(transcript_paths(samples[0]["clone"]), samples[0]["at"] - 3600) if samples else []
        if not samples or not tools:
            out["unmeasured"].append("%s gen %s" % (row["item"], row["gen"]))
            continue
        fired = sorted({h["kind"] for i, s in enumerate(samples)
                        for h in judge(samples[:i + 1], [t for t in tools if s["at"] >= t["t0"]], c, s["at"])})
        label = row["label"]
        out[label] += 1
        out["wrongful"] += 1 if label == "fine" and fired else 0
        out["missed"] += 1 if label == "circling" and not fired else 0
        out["runs"].append({"item": row["item"], "gen": row["gen"], "label": label, "fired": fired})
    out["measured"] = out["fine"] + out["circling"]
    out["fingerprint"] = fingerprint(c)
    return out


def main(argv=None):
    import relentless as R
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("replay")
    p.add_argument("--labels", required=True)
    p.add_argument("--write", action="store_true", help="write the verdict stop_gate reads")
    a = ap.parse_args(argv)
    c = R.rules()["circling"]
    with open(a.labels, encoding="utf-8") as f:
        v = replay(R.Store(), json.load(f), c)
    print(json.dumps({k: x for k, x in v.items() if k != "runs"}, indent=1))
    if a.write:
        with open(VERDICT, "w", encoding="utf-8") as f:
            json.dump(v, f, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
