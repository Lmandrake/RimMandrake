#!/usr/bin/env python3
"""the-lint-refuses-a-new-counter: failure_counter_lint refuses a planted counter and passes the real tree
(design/specs/2026-11-23-one-failure-classifier/boundary.md)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import failure_counter_lint as L  # noqa: E402

FAILS = []


def check(ok, what, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, "" if ok else "  -- %s" % (got,)))
    if not ok:
        FAILS.append(what)


bad, n = L.check()
check(not bad and n >= 40, "the real tree passes (%d listed counters seen)" % n, bad[:5])
rels = L.files()
check(all(p in rels for p in ("src/RimMandrake/Utils/testq/visit_feed.py", "src/RimMandrake/rimflow/list_dispatch.py",
                              "src/RimMandrake/rimflow/maturation_dispatch.py", "infrastructure/stevedesktop/worker.py")),
      "the scan sees the visit feed, the Workshop Pipeline, the dispatch tick and the SteveDesktop worker", len(rels))
NEW = "src/RimMandrake/Utils/testq/new_feed.py"
PLANTS = {
    "the visit feed's own counter of 2026-11-22": "FAILS_TO_STOP = 2\ndef waiting(fails, m, c):\n"
        "    return [x for x in c if fails.get(m, {}).get(x, 0) >= FAILS_TO_STOP]\n",
    "a tries cap": "MAX_TRIES = 6\ndef step(rec):\n    if rec['tries'] < MAX_TRIES:\n        return 'again'\n    return 'given up'\n",
    "a length of failures": "def stop(dead):\n    return len(dead) >= 3\n",
    "a config limit": "def stop(cfg, n_failed):\n    return n_failed > int(cfg.get('most', 2))\n",
    "the limit on the left": "def stop(strikes):\n    return 3 <= strikes\n",
    "a retry loop": "TRIES = 3\ndef go(do):\n    for attempt in range(TRIES):\n        if do():\n            return True\n    return False\n",
    "a run cap": "def stop(work, max_runs):\n    return len(work) >= max_runs\n",
    "a counter in a class": "class A:\n    def stop(self):\n        return self.attempts >= 2\n",
    "a counter beside a function that does call it": "def a(r):\n    return FC.read(r).counts\ndef b(fails):\n    return fails >= 2\n",
}
for what, text in PLANTS.items():
    bad, _ = L.check(extra={NEW: text}, only=[NEW])
    check(len(bad) == 1 and NEW in bad[0] and "failure_class" in bad[0], "a planted counter is refused by name: " + what, bad[:3])
GREEN = {
    "it calls failure_class": "import failure_class as FC\ndef stop(rs):\n    n, left = FC.count(FC.of_run(r) for r in rs)\n    fails = n\n    return fails >= 2\n",
    "a time": "def due(now, failed_at, wait_s):\n    return now - failed_at >= wait_s\n",
    "any at all": "def red(fails):\n    return 1 if fails > 0 else 0\n",
    "no failure word": "def big(rows):\n    return len(rows) > 40\n",
}
for what, text in GREEN.items():
    bad, _ = L.check(extra={NEW: text}, only=[NEW])
    check(not bad, "must stay green: " + what, bad[:2])
lst = L.load_list()
bad, _ = L.check(listed=dict(lst, **{"src/RimMandrake/Utils/publish.py::land::gone >= 3": 1}))
check(len(bad) == 1 and "stale" in bad[0], "a stale list entry is refused", bad[:2])
k = "src/RimMandrake/rimflow/dispatcher.py::one_seat::streak >= n"
bad, _ = L.check(listed=dict(lst, **{k: lst[k] - 1}))
check(len(bad) == 1 and "dispatcher.py" in bad[0], "one more of a listed counter in the same function is refused", bad[:2])
v = "src/RimMandrake/Utils/testq/visit_feed.py"
text = (HERE / "testq" / "visit_feed.py").read_text(encoding="utf-8")
cut = text.replace("FC.of_testq(rec, c)", "1").replace("FC.count(r for _, r in rs)", "(len(rs), {})").replace("FC = _failure_class()", "FC = None")
bad, _ = L.check(extra={v: cut}, only=[v])
check(len(bad) == 1 and "FAILS_TO_STOP" in bad[0], "the real visit feed without its call is refused", bad[:2])
print("selftest_failure_counter_lint: %s" % ("FAIL %d" % len(FAILS) if FAILS else "OK"))
sys.exit(1 if FAILS else 0)
