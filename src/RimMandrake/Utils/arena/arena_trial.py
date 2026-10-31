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

usage: arena_trial.py build [--n N] [--no-csharp] [--no-check] [--out PATH]   (default out: trial_tasks.json)
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


def check_order(ids, bank: dict, fixes: dict, repo) -> None:
    """Raise TaskRefused (arena_rounds) when `ids` puts a task no later than a listed task whose fix its base holds."""
    import arena_rounds as RD
    miss = [t for t in ids if t not in fixes or not bank.get(t, {}).get("base_sha")]
    if miss:
        raise TrialError("no base/fix sha for %d listed task(s) (e.g. %s): sibling order unchecked" % (len(miss), miss[0]))
    contains = RD.contains_for({t: {"base_sha": bank[t]["base_sha"], "fix_sha": fixes[t]} for t in ids}, repo)
    RD.check_rounds(list(ids), contains)


def build(n=DEFAULT_N, csharp=True, check=True, repo=None, p=None) -> dict:
    bank = AA.load_tasks(p)
    nokey = AA.chrono_keys(bank, repo)
    if nokey:
        raise TrialError("%d frozen task(s) have no chronology key (e.g. %s): no eras, no list" %
                         (len(nokey), sorted(nokey.items())[0]))
    ids = select(bank, n, csharp)
    if check:
        check_order(ids, bank, hidden_fix_shas(p), repo or A.REPO)
    eras, _ = AA.era_map({t: bank[t] for t in ids})
    kinds = {}
    for t in ids:
        kinds[bank[t]["kind"]] = kinds.get(bank[t]["kind"], 0) + 1
    return {"schema": SCHEMA, "n": len(ids), "csharp": csharp, "frozen_bank": len(bank),
            "bank_csharp": sum(1 for s in bank.values() if s.get("kind") == CSHARP),
            "eras_in_trial": [sum(1 for t in ids if eras[t] == e) for e in range(AA.ERAS)], "kinds": kinds,
            "order": "oldest first: chrono (git rev-list --count base_sha), then id"
                     + ("; checked with arena_rounds.check_rounds" if check else "; sibling order NOT checked"),
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
    s = sub.add_parser("show")
    s.add_argument("path", nargs="?", default=str(DEFAULT_PATH))
    a = ap.parse_args(argv)
    if a.cmd == "show":
        ids = read_list(a.path)
        print("%d task(s): %s ... %s" % (len(ids), ids[:3], ids[-3:]))
        return 0
    try:
        doc = build(a.n, not a.no_csharp, not a.no_check, a.repo)
    except (TrialError, A.TaskRefused) as e:
        print("REFUSED: %s" % e)
        return 2
    Path(a.out).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in doc.items() if k != "tasks"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
