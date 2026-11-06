#!/usr/bin/env python3
"""jam_classes.py — every Relentless jam is fixed as a CLASS (JAM_CLASS_BUILD_OPS_DETECTOR_PER_CLASS).

Owner, 2026-11-03: "absolutely, fix the class should be the rule." (design/RimMandrake/relentless_improvement_loop_2026-11-03.md)
The registry is jam_classes.json beside this file. A jam is a row of the belt's journal (store/journal.jsonl) with
do=alarm and a kind the registry lists; its reason is the why, less any "breaker open until <ts>: " prefix.

  lint     every class has a plain name, regexes that compile, an ops_watch target that exists, a remedy function that
           exists (or a stated reason none is safe), a fix stamp that parses, and examples that match it and no other
           class; the two meta targets exist too. Exit 0 clean, 1 with the problems.
  census   the jams in the last window_days: per class, the unnamed ones (no class matches: name the class) and the
           repeats (a class jamming after its fixed.at: the fix did not hold). ops_watch.c_relentless reads this as
           relentless.jam_unnamed and relentless.jam_repeat, whose targets alarm.

Nothing here edits the journal or the registry: a repeat clears when someone fixes the class again and moves fixed.at,
an unnamed jam when its class is added, or either when its row leaves the window.
"""
import argparse
import ast
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
REGISTRY = HERE / "jam_classes.json"
OPS_RULES = REPO / "src/RimMandrake/Utils/ops_watch_rules.json"
BREAKER_PREFIX = re.compile(r"^breaker open until \S+: ")
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def load(path=None):
    with open(path or REGISTRY, encoding="utf-8") as f:
        return json.load(f)


def epoch(s):
    """ISO-8601 (Z or offset) -> epoch seconds, or None."""
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        return None
    return d.timestamp()


def reason(row):
    """The jam's reason: the alarm's why, first 400 chars, without the breaker's 'open until' prefix."""
    return BREAKER_PREFIX.sub("", str(row.get("why") or "")).strip()[:400]


def hits(pattern, text):
    """re.search that reads a pattern which does not compile as no hit: lint names it; a census must not die on it."""
    try:
        return re.search(pattern, text) is not None
    except (re.error, TypeError):
        return False


def matches(reg, text):
    """-> ids of every class whose match list hits text."""
    return [c["id"] for c in reg["classes"] if any(hits(p, text) for p in c.get("match") or [])]


def classify(reg, text):
    """-> the class id for one reason, or None. Several hits take the first listed (lint forbids overlapping examples)."""
    hit = matches(reg, text)
    return hit[0] if hit else None


def defines(path, name):
    """True when the Python file at path defines a function or method `name` at any depth."""
    try:
        tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError):
        return False
    return any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name for n in ast.walk(tree))


def target_names(rules_path=None):
    with open(rules_path or OPS_RULES, encoding="utf-8") as f:
        rules = json.load(f)
    return {t.get("name") for t in rules.get("targets") or [] if isinstance(t, dict) and t.get("name")}


def sha_known(sha, repo=REPO):
    """None when git confirms the commit, else why not."""
    try:
        r = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", "%s^{commit}" % sha], capture_output=True,
                           timeout=30)
    except (OSError, subprocess.SubprocessError) as e:
        return "git could not be asked: %s" % e
    return None if r.returncode == 0 else "no such commit"


def lint(reg, targets, repo=REPO, check_sha=True):
    """-> problems (strings); [] is clean."""
    bad = []
    if not isinstance(reg.get("kinds"), list) or not reg["kinds"]:
        bad.append("kinds: a non-empty list of journal alarm kinds")
    if not isinstance(reg.get("window_days"), (int, float)) or reg["window_days"] <= 0:
        bad.append("window_days: a positive number")
    for m in reg.get("meta_targets") or []:
        if m not in targets:
            bad.append("meta target %s: no ops_watch_rules.json target has that name" % m)
    if len(reg.get("meta_targets") or []) != 2:
        bad.append("meta_targets: the unnamed-jam target and the repeat target, both")
    classes = reg.get("classes")
    if not isinstance(classes, list) or not classes:
        return bad + ["classes: a non-empty list"]
    seen = set()
    for c in classes:
        cid = c.get("id")
        at = "class %s" % cid
        if not isinstance(cid, str) or not ID_RE.match(cid):
            bad.append("%s: id is lower snake case" % at)
        if cid in seen:
            bad.append("%s: id used twice" % at)
        seen.add(cid)
        plain = c.get("plain")
        if not isinstance(plain, str) or not plain.strip():
            bad.append("%s: no plain name" % at)
        elif len(plain) > 160 or plain.count(". ") or not plain.endswith("."):
            bad.append("%s: plain is one short sentence a cold reader understands (<=160 chars, one full stop)" % at)
        pats = c.get("match")
        if not isinstance(pats, list) or not pats:
            bad.append("%s: match is a non-empty list of regexes" % at)
            pats = []
        for p in pats:
            try:
                re.compile(p)
            except (re.error, TypeError) as e:
                bad.append("%s: match %r does not compile: %s" % (at, p, e))
        det = c.get("detector") or {}
        if det.get("target") not in targets:
            bad.append("%s: detector target %r is no ops_watch_rules.json target" % (at, det.get("target")))
        if not str(det.get("how") or "").strip():
            bad.append("%s: detector.how says what reading sees it" % at)
        rem = c.get("remedy") or {}
        if ("auto" in rem) == ("none" in rem):
            bad.append("%s: remedy is exactly one of auto (path::function) or none (why no remedy is safe)" % at)
        elif "auto" in rem:
            path, _, fn = str(rem["auto"]).partition("::")
            if not fn or not defines(Path(repo) / path, fn):
                bad.append("%s: remedy %r: %s defines no function %s" % (at, rem["auto"], path, fn or "(none named)"))
            if not str(rem.get("what") or "").strip():
                bad.append("%s: remedy.what says what the remedy does" % at)
        elif len(str(rem["none"]).strip()) < 40:
            bad.append("%s: remedy.none gives the reason no automatic remedy is safe" % at)
        fx = c.get("fixed", "absent")
        if fx == "absent":
            bad.append("%s: fixed is null (no fix yet) or {at, sha and/or item}" % at)
        elif fx is not None:
            if not isinstance(fx, dict) or epoch(fx.get("at")) is None:
                bad.append("%s: fixed.at is an ISO time with a zone" % at)
            elif not (fx.get("sha") or fx.get("item")):
                bad.append("%s: fixed names the sha or the item that fixed it" % at)
            elif fx.get("sha") and check_sha:
                why = sha_known(fx["sha"], repo)
                if why:
                    bad.append("%s: fixed.sha %s: %s" % (at, fx["sha"], why))
        ex = c.get("examples")
        if not isinstance(ex, list) or not ex:
            bad.append("%s: examples: at least one reason the belt really journaled" % at)
            ex = []
        for e in ex:
            hit = matches(reg, e)
            if hit != [cid]:
                bad.append("%s: example %r matches %s, not this class alone" % (at, e[:80], hit or "nothing"))
    return bad


# OPSWATCH_BUILD_ALARMS_KEYED_BY_CAUSE (owner 2026-11-06: "Merging duplicate alarms just seems like common sense"):
# an ops_watch alarm's CAUSE, the key its one repair item is filed under (rimflow/cause_book.py). Arena's removal
# (1f0e666566) left three alarms reading red on tests that no longer exist, and they filed 9 items in 13 minutes.
TEST_PATH = re.compile(r"(?<![\w./-])((?:[\w.-]+/)+[\w.-]+\.(?:py|cs|sh))(?![\w])")


def alarm_paths(pt):
    """The test/source paths an alarm's reading names (x.news, x.said, x.subject): repo-relative, sorted, unique."""
    x = (pt or {}).get("x") if isinstance((pt or {}).get("x"), dict) else (pt or {})
    bits = []
    for f in ("news", "said", "subject"):
        v = x.get(f) if isinstance(x, dict) else None
        bits.extend(v if isinstance(v, list) else [v] if v else [])
    return sorted({m.group(1) for b in bits for m in TEST_PATH.finditer(str(b))})


def gone_root(path, exists):
    """The topmost ancestor of `path` that no longer exists (the subtree removed), else the path itself."""
    parts = path.split("/")
    for i in range(1, len(parts) + 1):
        head = "/".join(parts[:i])
        if not exists(head):
            return head
    return path


def tree_exists(clone):
    """-> exists(path) over the COMMITTED tree at `clone`'s HEAD (git cat-file: a sparse checkout is not a deletion).
    A clone git cannot read judges nothing gone (every path exists), so no alarm merges on a blind tree."""
    def git(*a):
        return subprocess.run(["git", "-C", str(clone)] + list(a), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              timeout=20).returncode
    try:
        if not clone or git("rev-parse", "--verify", "-q", "HEAD") != 0:
            return lambda p: True
    except (OSError, subprocess.SubprocessError):
        return lambda p: True
    seen = {}

    def exists(p):
        if p not in seen:
            try:
                seen[p] = git("cat-file", "-e", "HEAD:" + p) == 0
            except (OSError, subprocess.SubprocessError):
                seen[p] = True
        return seen[p]
    return exists


def cause_key(aid, pt=None, exists=None):
    """-> the alarm's cause key. Every path its reading names is gone from the tree `exists` reads (tree_exists):
    "gone|<removed root(s)>", one cause however many alarms (groups, overdue chases) read the removed subtree.
    Anything else is its exact signature, the alarm id: two faults with different first error lines stay two items,
    and so does an alarm with no reading, or any alarm when no tree is given (exists None: nothing is judged gone)."""
    paths = alarm_paths(pt) if exists else []
    if paths and not any(exists(p) for p in paths):
        return "gone|" + ",".join(sorted({gone_root(p, exists) for p in paths}))
    return aid


def jam_rows(journal, kinds, since):
    """-> (rows, None) or (None, why): the journal's jam alarms at or after `since`, one per (at, reason)."""
    out, keys = [], set()
    try:
        with open(journal, encoding="utf-8") as f:
            for line in f:
                if '"alarm"' not in line:
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue        # a torn last line from a killed tick: the rest still reads
                if d.get("do") != "alarm" or d.get("kind") not in kinds:
                    continue
                t = epoch(d.get("at"))
                if t is None or t < since:
                    continue
                why = reason(d)
                if (d.get("at"), why) in keys:
                    continue        # a breaker emergency writes one row per road
                keys.add((d.get("at"), why))
                out.append({"at": d["at"], "t": t, "kind": d["kind"], "why": why})
    except OSError as e:
        return None, "journal unreadable: %s" % e
    return out, None


def census(reg, journal, now):
    """-> {window_days, jams, by_class, unnamed: [rows], repeats: [rows + class], open: [class ids]} or {error}."""
    since = now - reg["window_days"] * 86400
    rows, why = jam_rows(journal, set(reg["kinds"]), since)
    if rows is None:
        return {"error": why}
    fixed = {c["id"]: epoch((c.get("fixed") or {}).get("at")) for c in reg["classes"]}
    by_class, unnamed, repeats = {}, [], []
    for r in rows:
        cid = classify(reg, r["why"])
        if cid is None:
            unnamed.append(r)
            continue
        by_class[cid] = by_class.get(cid, 0) + 1
        if fixed.get(cid) is not None and r["t"] >= fixed[cid]:
            repeats.append(dict(r, cls=cid))
    return {"window_days": reg["window_days"], "jams": len(rows), "by_class": by_class, "unnamed": unnamed,
            "repeats": repeats, "open": [c["id"] for c in reg["classes"] if c.get("fixed") is None]}


def default_journal():
    root = os.environ.get("RELENTLESS_ROOT")
    if not root:
        with open(OPS_RULES, encoding="utf-8") as f:
            root = (json.load(f).get("relentless") or {}).get("root")
    if not root:
        raise SystemExit("jam_classes: no RELENTLESS_ROOT and ops_watch_rules.json relentless.root is unset")
    return Path(root) / "store" / "journal.jsonl"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    lp = sub.add_parser("lint")
    lp.add_argument("--registry")
    lp.add_argument("--rules")
    cp = sub.add_parser("census")
    cp.add_argument("--registry")
    cp.add_argument("--journal")
    cp.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    reg = load(a.registry)
    if a.cmd == "lint":
        bad = lint(reg, target_names(a.rules))
        for b in bad:
            print("JAM_CLASS_LINT: %s" % b)
        print("jam_classes lint: %d classes, %s" % (len(reg.get("classes") or []), "clean" if not bad else "%d problem(s)" % len(bad)))
        return 1 if bad else 0
    now = datetime.now(timezone.utc).timestamp()
    c = census(reg, a.journal or default_journal(), now)
    if a.json:
        print(json.dumps(c, indent=1, sort_keys=True))
        return 1 if "error" in c else 0
    if "error" in c:
        print("jam census UNMEASURED: %s" % c["error"])
        return 1
    print("jams in %s days: %d; by class %s; unnamed %d; repeats after a fix %d; classes with no fix yet %s" % (
        c["window_days"], c["jams"], json.dumps(c["by_class"], sort_keys=True), len(c["unnamed"]), len(c["repeats"]),
        ", ".join(c["open"]) or "none"))
    for r in c["unnamed"]:
        print("  UNNAMED %s %s: %s" % (r["at"], r["kind"], r["why"][:160].replace("\n", " ")))
    for r in c["repeats"]:
        print("  REPEAT  %s %s: %s" % (r["at"], r["cls"], r["why"][:160].replace("\n", " ")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
