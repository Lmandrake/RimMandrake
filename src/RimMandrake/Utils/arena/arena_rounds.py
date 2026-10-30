#!/usr/bin/env python3
"""arena_rounds.py — sibling order for every arena planner (ARENA_PLANNERS_ENFORCE_SIBLING_ORDER).

A pool task whose base already holds another pool task's fix must be judged STRICTLY after it: worked earlier or
alongside, the arm could read the other task's answer from its own history (arena_tasks.base_contains, 854 of 861
pairs in the 42-task pool, because history is linear). arena_tasks owns the relation and the static check
(base_contains, schedule_conflicts, check_schedule); this module is what a planner calls, in one of two shapes:

  static   a planner that lays out an order up front (arena_replay.schedule) builds it with chrono_order, a seeded
           random linear extension of the relation (random wherever the relation leaves a choice), and passes it
           through check_rounds before running it.
  dynamic  a planner that hands out tasks one at a time to members working concurrently (ralph_c_loop.Board.assign,
           arena_judge assignment) asks may_give / guard_give before it gives a task: a task is refused while any
           pool task its base contains is not yet done (held by someone else counts as not done, which is what makes
           "same round" a refusal too).

contains maps task id -> [pool task ids whose fix is in its base]; build it with contains_for (git) or pass
arena_tasks.base_contains output. Ids outside the planner's task set are ignored: they are not being judged.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import arena_tasks as T  # noqa: E402  (owns base_contains / check_schedule; this module only calls them)

TaskRefused = T.TaskRefused


def contains_for(tasks: dict, repo) -> dict:
    """tasks = {id: {"base_sha":..., "fix_sha":...}} -> arena_tasks.base_contains over them, computed in `repo`."""
    pool = [({"id": tid, "base_sha": t["base_sha"]}, {"fix_sha": t["fix_sha"]}) for tid, t in sorted(tasks.items())]
    return T.base_contains(pool, Path(repo))


def _within(contains: dict, ids) -> dict:
    ids = set(ids)
    return {t: sorted(set(contains.get(t, [])) & ids - {t}) for t in ids}


def chrono_order(ids, contains: dict, seed=None) -> list[str]:
    """A linear extension of `contains` over `ids`: every contained task before the task containing it. With `seed`
    the choice among tasks that are free at the same time is a seeded shuffle (deterministic); without, sorted.
    Raises TaskRefused on a cycle (two bases containing each other's fix: the relation is corrupt)."""
    need = _within(contains, ids)
    rng = random.Random(seed) if seed is not None else None
    placed: list[str] = []
    done: set = set()
    left = set(need)
    while left:
        free = sorted(t for t in left if set(need[t]) <= done)
        if not free:
            raise TaskRefused("sibling relation has a cycle among: %s" % ", ".join(sorted(left)))
        pick = rng.choice(free) if rng else free[0]
        placed.append(pick)
        done.add(pick)
        left.discard(pick)
    check_rounds(placed, contains)
    return placed


def check_rounds(order, contains: dict) -> None:
    """arena_tasks.check_schedule: `order` is a list of ids (one per round) or of rounds (ids judged together)."""
    T.check_schedule(order, contains)


def blocked_by(tid: str, contains: dict, done, pool) -> list[str]:
    """The pool tasks contained in tid's base that are not yet done (empty: tid may be given)."""
    pool, done = set(pool), set(done)
    return sorted(c for c in contains.get(tid, []) if c in pool and c != tid and c not in done)


def may_give(tid: str, contains: dict, done, pool) -> bool:
    return not blocked_by(tid, contains, done, pool)


def guard_give(tid: str, contains: dict, done, pool) -> None:
    """Raise TaskRefused when giving tid now would let an arm work it no later than a task whose fix its base holds."""
    b = blocked_by(tid, contains, done, pool)
    if b:
        raise TaskRefused("task %s not given: its base already contains the fix of %d pool task(s) not yet done: %s"
                          % (tid, len(b), ", ".join(b[:5])))


def first_givable(candidates, contains: dict, done, pool):
    """-> (task id or None, {skipped id: blockers}). The first candidate (in the planner's own order) that may be given."""
    skipped = {}
    for tid in candidates:
        b = blocked_by(tid, contains, done, pool)
        if not b:
            return tid, skipped
        skipped[tid] = b
    return None, skipped
