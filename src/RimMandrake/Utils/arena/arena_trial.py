#!/usr/bin/env python3
"""arena_trial.py — the trial's task population: an explicit list of N frozen tasks over all three eras
(ARENA_TRIAL_TASKS_FIX_DEFAULT_ALL_FROZEN, Conductor ruling 2026-10-30, owner authority). N is a parameter
(`build --n`, default DEFAULT_N); nothing caps it (ARENA_TRIAL_SCHEDULE_FIX_STOPS_SHORT).

Why a list and why the default size: under the era gate (arena_analysis.py) a look may neither stop nor drop until every arm in
contention has completed the newest era of the TRIAL's tasks, and planners run oldest first (sibling order,
arena_rounds.py), so decisions land only at the full trial size. With every frozen task (241) as the population
the newest era is 80 tasks and the gate never opens within budget (about 50 tasks per arm); a list that size or smaller fits, hence the default.
A larger --n is allowed (a bigger budget); the replay must then run every listed task per arm.

THE SELECTION (deterministic, no randomness):
  - the frozen bank (arena_analysis.load_tasks) with chronology keys (arena_analysis.chrono_keys: `git rev-list
    --count base_sha`); a bank task with no key refuses the build (the gate could not name eras);
  - C# tasks (kind csharp) in proportion by default: the owner dropped ARENA_SANDBOX_HARDEN_INTEROP_STEP_LEGACY
    ("C# tasks stay in the pool", OWNER ledger 2026-10-30). --no-csharp leaves them out;
  - the eligible bank is split into ERAS=3 eras with arena_analysis.era_map; the n slots are split as evenly as
    possible (remainder to the newest eras); within an era the C# share of its slots is the era's own C# share
    (rounded), and each kind group is sampled evenly spaced over its chronological rank (slot j of q takes rank
    floor((j + 0.5) * len / q));
  - the list is written oldest first (chrono, then id), which is a linear extension of the sibling relation on
    linear history (a base containing another task's fix has strictly more commits behind it); `build` also checks it
    with arena_rounds.check_rounds against arena_tasks.base_contains (fix shas from the judge's hidden files) unless
    --no-check.

The committed default (trial_tasks.json beside this file) is what `arena_analysis.py run` uses with no
--trial-tasks. Rebuild it after the frozen pool changes (another builder vets the pool): a list naming a task with
no frozen spec makes the analysis UNMEASURED (fail closed), never a silent shrink.

EXCLUSIONS, applied to the bank BEFORE the era split (so N stays N wherever the bank allows):
  - the pool exclusions (arena_tasks.load_pool_exclusions, pool_exclusions.json: e.g. the four provisional Clean
    labels, Conductor ruling 2026-10-30), matched on each task file's source_item; a re-census drops them from the
    pool too, this only keeps a list built before that re-census honest;
  - the reader pass (arena_reader_pass.py apply): its exclusion file (default READER_EXCLUSIONS, i.e.
    <arena root>/judge/reader/exclusions.json, judge-only) names tasks to DROP and checks to UNSCORE. A dropped task
    is left out. A task with an unscored check STAYS and is scored on its remaining checks: arena_judge.judge reads
    the same default file and leaves those checks out (ARENA_JUDGE_HONOUR_UNSCORE_DOWNSTREAM). It is left out only
    when no scored check is left (every fix_test of its hidden file unscored, or no hidden file), when an unscored
    path is not one of its scored checks (a typo: the judge refuses such a task), or when the file
    is an explicit --reader-exclusions path other than the default (the judge reads only the default, so it could
    not honour that unscore). Absent default file: not applied, and
    the doc says so (`reader: null`); an explicit --reader-exclusions path that is missing refuses; --no-reader skips;
  - ONE task per bundled commit (ARENA_POOL_FIX_BUNDLED_WRONG_REASON): tasks sharing a fix sha (the judge's hidden
    files) are siblings of one commit; only the first by id is eligible (after the other exclusions, so a dropped
    sibling hands the slot to the next). --allow-bundled turns this off.

usage: arena_trial.py build [--n N] [--no-csharp] [--no-check] [--out PATH]   (default out: trial_tasks.json)
                            [--reader-exclusions PATH | --no-reader] [--allow-bundled]
       arena_trial.py show [PATH]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_analysis as AA  # noqa: E402
import arena_tasks as A  # noqa: E402

SCHEMA = "arena_trial_tasks/1"
DEFAULT_PATH = HERE / "trial_tasks.json"
DEFAULT_N = 50          # the default trial size, NOT a cap: `build --n` takes any positive int
CSHARP = "csharp"
READER_SCHEMA = "arena_reader_exclusions/1"


def reader_exclusions_path(p=None) -> Path:
    """Default reader-pass exclusion file: <arena root>/judge/reader/exclusions.json (beside the judge's hidden
    files: it quotes hidden check paths, so never arm-readable)."""
    return (p or A.paths())["freeze"].parent / "reader" / "exclusions.json"


def read_reader_exclusions(path) -> dict:
    """{"drop": {task: reason}, "unscore": {task: [check path, ...]}} from an arena_reader_pass `apply` file."""
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if not (isinstance(doc, dict) and doc.get("schema") == READER_SCHEMA and isinstance(doc.get("drop"), dict)
            and isinstance(doc.get("unscore"), dict)):
        raise TrialError("%s: not an %s document" % (path, READER_SCHEMA))
    return {"drop": dict(doc["drop"]), "unscore": {t: list(v) for t, v in doc["unscore"].items()}}


def exclude(tasks: dict, drop=(), fixes=None, bundled=False) -> tuple[dict, dict]:
    """-> (eligible tasks, {task: why left out}). `drop`: {task: reason} left out first; then, unless `bundled`,
    one task per fix sha (`fixes` {task: fix_sha}; a task with no fix sha is its own group): the first by id. Pure."""
    out, why = {}, {}
    for t in sorted(tasks):
        if t in drop:
            why[t] = drop[t]
        else:
            out[t] = tasks[t]
    if not bundled and fixes:
        first = {}
        for t in sorted(out):
            g = fixes.get(t) or ("task:" + t)
            if g in first:
                why[t] = "bundled commit %s: sibling %s is the eligible one" % (str(g)[:12], first[g])
                del out[t]
            else:
                first[g] = t
    return out, why


class TrialError(Exception):
    pass


def _spread(group, q):
    """q items of `group` (already in chronological order), evenly spaced over its ranks."""
    if q <= 0:
        return []
    if q >= len(group):
        return list(group)
    return [group[int((j + 0.5) * len(group) / q)] for j in range(q)]


def _quotas(total, sizes):
    """Split `total` over len(sizes) bins as evenly as possible, remainder to the LAST (newest) bins, capped by size."""
    m = len(sizes)
    q = [total // m + (1 if i >= m - total % m else 0) for i in range(m)]
    q = [min(a, s) for a, s in zip(q, sizes)]
    left = min(total, sum(sizes)) - sum(q)
    while left > 0:                    # a capped bin's slots go to the newest bins with room
        for i in reversed(range(m)):
            if left and q[i] < sizes[i]:
                q[i] += 1
                left -= 1
    return q


def select(tasks: dict, n: int = DEFAULT_N, csharp: bool = True) -> list[str]:
    """tasks: {id: {"kind":..., "chrono": int}} -> at most n ids over all ERAS eras, oldest first. Pure."""
    if not (isinstance(n, int) and not isinstance(n, bool) and n > 0):
        raise TrialError("n must be a positive int (got %r)" % (n,))
    pool = {t: s for t, s in tasks.items() if csharp or s.get("kind") != CSHARP}
    eras, why = AA.era_map(pool)
    if eras is None:
        raise TrialError("no era map over the bank: %s" % why)
    rank = sorted(pool, key=lambda t: (pool[t]["chrono"], t))
    by_era = [[t for t in rank if eras[t] == e] for e in range(AA.ERAS)]
    if any(not g for g in by_era):
        raise TrialError("an era is empty (%s): the trial could not span all three" % [len(g) for g in by_era])
    out = []
    for g, q in zip(by_era, _quotas(min(n, len(pool)), [len(g) for g in by_era])):
        cs = [t for t in g if pool[t].get("kind") == CSHARP]
        other = [t for t in g if pool[t].get("kind") != CSHARP]
        qc = min(len(cs), int(q * len(cs) / len(g) + 0.5))
        qc = max(qc, q - len(other))
        out += _spread(cs, qc) + _spread(other, q - qc)
    return sorted(out, key=lambda t: (pool[t]["chrono"], t))


def hidden_fix_shas(p=None) -> dict:
    """{task id: fix_sha} from the judge's hidden files (read for the sibling check only; nothing is copied out)."""
    p = p or A.paths()
    out = {}
    for f in sorted(Path(p["judge"]).glob("*.json")):
        try:
            h = json.loads(f.read_text(encoding="utf-8"))
            out[h["task"]] = h["fix_sha"]
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return out


def hidden_scored_paths(p=None) -> dict:
    """{task id: [path of every scored fix_test]} from the judge's hidden files (judge side; nothing is copied out)."""
    p = p or A.paths()
    out = {}
    for f in sorted(Path(p["judge"]).glob("*.json")):
        try:
            h = json.loads(f.read_text(encoding="utf-8"))
            out[h["task"]] = [c["path"] for c in h.get("checks") or [] if c.get("type") == "fix_test"]
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            continue
    return out


def check_order(ids, bank: dict, fixes: dict, repo) -> None:
    """Raise TaskRefused (arena_rounds) when `ids` puts a task no later than a listed task whose fix its base holds."""
    import arena_rounds as RD
    miss = [t for t in ids if t not in fixes or not bank.get(t, {}).get("base_sha")]
    if miss:
        raise TrialError("no base/fix sha for %d listed task(s) (e.g. %s): sibling order unchecked" % (len(miss), miss[0]))
    contains = RD.contains_for({t: {"base_sha": bank[t]["base_sha"], "fix_sha": fixes[t]} for t in ids}, repo)
    RD.check_rounds(list(ids), contains)


def _source_items(p=None) -> dict:
    """{task id: source_item} from the task files (the pool exclusions are keyed by source item)."""
    out = {}
    for f in sorted(Path((p or A.paths())["tasks"]).glob("*.json")):
        try:
            t = json.loads(f.read_text(encoding="utf-8"))
            out[t["id"]] = t.get("source_item")
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return out


def build(n=DEFAULT_N, csharp=True, check=True, repo=None, p=None, reader=None, use_reader=True,
          bundled=False) -> dict:
    """`reader`: the reader exclusion file (None: the default path, applied only if it exists)."""
    bank = AA.load_tasks(p)
    nokey = AA.chrono_keys(bank, repo)
    if nokey:
        raise TrialError("%d frozen task(s) have no chronology key (e.g. %s): no eras, no list" %
                         (len(nokey), sorted(nokey.items())[0]))
    fixes = hidden_fix_shas(p)
    pex = A.load_pool_exclusions()
    src = _source_items(p)
    drop = {t: "pool exclusion: " + pex[src[t]] for t in bank if src.get(t) in pex}
    rinfo = None
    if use_reader:
        rp = Path(reader) if reader else reader_exclusions_path(p)
        if reader and not rp.is_file():
            raise TrialError("reader exclusion file %s does not exist" % rp)
        if rp.is_file():
            rx = read_reader_exclusions(rp)
            for t, why in rx["drop"].items():
                drop.setdefault(t, "reader pass: " + str(why))
            honoured = rp.resolve() == reader_exclusions_path(p).resolve()   # the file the judge reads
            scored = hidden_scored_paths(p) if rx["unscore"] else {}
            kept = 0
            for t, cks in rx["unscore"].items():
                if not honoured:
                    drop.setdefault(t, "reader pass unscored %d check(s) in %s, which the judge does not read"
                                       % (len(cks), rp))
                elif not set(scored.get(t) or ()) - set(cks):    # no hidden file reads as nothing left: fail closed
                    drop.setdefault(t, "reader pass unscored every scored check (%d)" % len(cks))
                elif set(cks) - set(scored.get(t) or ()):        # a typo/stale path: the judge refuses the task
                    drop.setdefault(t, "reader pass unscores %d check(s) the task's hidden file does not hold "
                                       "(the judge refuses it, ARENA_JUDGE_REPAIR_MISSING_EXCLUSIONS_OPEN)"
                                       % len(set(cks) - set(scored.get(t) or ())))
                else:
                    kept += 1
            rinfo = {"path": str(rp), "drop": len(rx["drop"]), "unscore": len(rx["unscore"]),
                     "unscore_kept": kept, "judge_honours": honoured}
    eligible, left_out = exclude(bank, drop, fixes, bundled)
    ids = select(eligible, n, csharp)
    if check:
        check_order(ids, bank, fixes, repo or A.REPO)
    eras, _ = AA.era_map({t: bank[t] for t in ids})
    kinds = {}
    for t in ids:
        kinds[bank[t]["kind"]] = kinds.get(bank[t]["kind"], 0) + 1
    return {"schema": SCHEMA, "n": len(ids), "csharp": csharp, "frozen_bank": len(bank),
            "bank_csharp": sum(1 for s in bank.values() if s.get("kind") == CSHARP),
            "eras_in_trial": [sum(1 for t in ids if eras[t] == e) for e in range(AA.ERAS)], "kinds": kinds,
            "order": "oldest first: chrono (git rev-list --count base_sha), then id"
                     + ("; checked with arena_rounds.check_rounds" if check else "; sibling order NOT checked"),
            "one_per_bundled_commit": not bundled, "reader": rinfo, "left_out": left_out,
            "tasks": ids}


def read_list(path) -> list[str]:
    """A trial list file: this module's JSON object, a JSON list of ids, or one id per line."""
    raw = Path(path).read_text(encoding="utf-8")
    s = raw.lstrip()
    if s.startswith("{"):
        doc = json.loads(raw)
        if doc.get("schema") != SCHEMA or not isinstance(doc.get("tasks"), list):
            raise ValueError("not an %s document" % SCHEMA)
        ids = doc["tasks"]
    elif s.startswith("["):
        ids = json.loads(raw)
    else:
        ids = [x.strip() for x in raw.splitlines() if x.strip()]
    if not all(isinstance(t, str) for t in ids) or len(set(ids)) != len(ids):
        raise ValueError("task ids must be distinct strings")
    return ids


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--n", type=int, default=DEFAULT_N, help="trial size (default %(default)s; no cap)")
    b.add_argument("--no-csharp", action="store_true", help="leave C# tasks out (default: in proportion)")
    b.add_argument("--no-check", action="store_true", help="skip the git sibling-order check")
    b.add_argument("--repo", help="git repo holding the base shas (default %s)" % A.REPO)
    b.add_argument("--out", default=str(DEFAULT_PATH))
    b.add_argument("--reader-exclusions", help="arena_reader_pass apply output (default: %s if it exists)"
                   % "<arena root>/judge/reader/exclusions.json")
    b.add_argument("--no-reader", action="store_true", help="ignore the reader-pass exclusions")
    b.add_argument("--allow-bundled", action="store_true", help="allow several tasks of one bundled commit")
    s = sub.add_parser("show")
    s.add_argument("path", nargs="?", default=str(DEFAULT_PATH))
    a = ap.parse_args(argv)
    if a.cmd == "show":
        ids = read_list(a.path)
        print("%d task(s): %s ... %s" % (len(ids), ids[:3], ids[-3:]))
        return 0
    try:
        doc = build(a.n, not a.no_csharp, not a.no_check, a.repo, reader=a.reader_exclusions,
                    use_reader=not a.no_reader, bundled=a.allow_bundled)
    except (TrialError, A.ArenaError, ValueError) as e:
        print("REFUSED: %s" % e)
        return 2
    Path(a.out).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: (len(v) if k == "left_out" else v) for k, v in doc.items() if k != "tasks"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
