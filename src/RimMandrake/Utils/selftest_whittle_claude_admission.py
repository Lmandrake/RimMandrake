#!/usr/bin/env python3
"""Offline selftest of the Whittle ticket admission and the hard stops in infrastructure/whittle_claude (wc.py admit(),
guard_run(), rerun_ok(), limit(); loop.sh wiring). Owner order 2026-11-12: "Yes to Whittle admission script and hard stops."

    python3 src/RimMandrake/Utils/selftest_whittle_claude_admission.py
    WC_UNDER_TEST=<path to a mutated wc.py> python3 ...   (the mutation check: each removed rule must turn a case red)

Cases: admit() refuses each bad kind by name (no item file, no done-line, no source path, no proof route, epic kind, BLOCKED,
open children, doing by another seat, held, target not v1) and admits a good ticket; gate() with admission on refuses with
"admission:" and passes the good one; guard_run kills a real child at the cap with a fake cost feed (exit 90), at the
broaden cap (91), when the item closes (92), leaves a cheap child alone and passes its exit code; rerun_ok allows at most
one rerun, none without new information, none after a hard stop; limits.json holds the defaults; loop.sh runs the Whittle
run under guard and asks rerun-ok. NOT covered: a real model run against the cap (the cost feed here is fake).
"""
import importlib.util
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

TMP = Path(tempfile.mkdtemp(prefix="wc_adm_"))
os.environ["WC_HOME"] = str(TMP / "home")
for k in ("WC_REMOTE", "WC_DIR") + tuple(k for k in os.environ if k.startswith("WC_LIMIT_")):
    os.environ.pop(k, None)

ROOT = Path(__file__).resolve().parents[3]
p = Path(os.environ.get("WC_UNDER_TEST") or ROOT / "infrastructure/whittle_claude/wc.py")
spec = importlib.util.spec_from_file_location("wc_adm", p)
wc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wc)

FAILS = []


def check(name, cond, got=""):
    print("%s %s%s" % ("ok  " if cond else "FAIL", name, "" if cond else "  got: %r" % (got,)))
    if not cond:
        FAILS.append(name)


def index(paths):
    files, suf, dirs = set(paths), {}, set()
    for f in files:
        parts = f.split("/")
        for i in range(len(parts)):
            suf.setdefault("/".join(parts[i:]), []).append(f)
        for i in range(1, len(parts)):
            dirs.add("/".join(parts[:i]))
    return files, suf, dirs


IDX = index(["src/RimMandrake/FlowWorks/Source/Pump.cs", "src/RimMandrake/FlowWorks/Defs/RM_Pump.xml",
             "src/RimMandrake/Utils/selftest_pump.py", "src/RimMandrake/FlowWorks/validation.py",
             "src/RimMandrake/Utils/validate_patch.py"])
GOOD = """# T
## spec
Fix the pump in `src/RimMandrake/FlowWorks/Source/Pump.cs`.
## verify
Run `python3 src/RimMandrake/Utils/run_selftests.py --only pump` and see the idle pump stop drawing power.
"""


def item(**kw):
    d = dict(id="FW_PUMP_FIX_ONE", open=True, state="ready", owner="BENCH", needs="offline", blocked=False,
             kind="bug", target="v1", held=None, criteria=[], title="pump fix", runs=[])
    d.update(kw)
    return SimpleNamespace(**d)


def ctx(text=GOOD, kids=(), admission=True):
    return wc.Ctx(pats=[re.compile("^FW_")], origin={"FW_PUMP_FIX_ONE"}, live=lambda i: True, admission=admission,
                  text=lambda i: text, index=IDX, children=lambda i: list(kids))


def why(v=None, **kw):
    return " | ".join(wc.admit(v or item(), ctx(**kw), "CLAUDE_T"))


check("good ticket admitted", why() == "", why())
check("no item file refused", why(text="").startswith("no item file"), why(text=""))
nodone = GOOD.replace("## verify", "## notes")
check("no done-line refused", "no done-line" in why(text=nodone), why(text=nodone))
check("ledger criteria count as the done-line", "no done-line" not in why(item(criteria=[{"id": "A1", "text": "pump stops"}]),
                                                                           text=nodone))
check("no source path refused", "no named mod/source path" in why(text=GOOD.replace("src/RimMandrake/FlowWorks/Source/Pump.cs", "the pump")),
      why(text=GOOD.replace("src/RimMandrake/FlowWorks/Source/Pump.cs", "the pump")))
check("a path that does not exist is not a source path",
      "no named mod/source path" in why(text=GOOD.replace("Pump.cs", "Ghost.cs")))
check("no proof route refused", "no proof route" in why(text=GOOD.replace("--only pump", "by eye")))
check("a generic tool is not a proof route", "no proof route" in why(text=GOOD.replace("src/RimMandrake/Utils/run_selftests.py --only pump",
                                                                                         "src/RimMandrake/Utils/validate_patch.py")))
check("a named existing proof script is a route", "no proof route" not in why(text=GOOD.replace(
    "src/RimMandrake/Utils/run_selftests.py --only pump", "src/RimMandrake/FlowWorks/validation.py")))
check("epic kind refused", "epic/design" in why(item(kind="epic")))
check("design kind refused", "epic/design" in why(item(kind="design")))
check("BLOCKED refused", "BLOCKED" in why(item(blocked=True)))
check("open children refused", "open children" in why(kids=["FW_CHILD"]))
check("doing by another seat refused", "doing" in why(item(state="doing", owner="CLAUDE_OTHER")))
check("doing by this worker is fine", "doing" not in why(item(state="doing", owner="CLAUDE_T")))
check("held refused", "held" in why(item(held={"by": "x"})))
check("closed refused", "closed" in why(item(open=False, state="done")))
check("target v2 refused", "not v1" in why(item(target="v2")))
check("target None refused", "not v1" in why(item(target=None)))

# gate() carries admission
ok, reason, _ = wc.gate(item(), "CLAUDE_T", "fwlive", ctx())
check("gate passes the good ticket", ok, reason)
ok, reason, _ = wc.gate(item(), "CLAUDE_T", "fwlive", ctx(text=GOOD.replace("--only pump", "by eye")))
check("gate refuses with 'admission:' and the reason", not ok and reason.startswith("admission: ") and "proof route" in reason,
      reason)
ok, reason, _ = wc.gate(item(), "CLAUDE_T", "fwlive", ctx(text=nodone, admission=False))
check("admission off (a hand-built Ctx) leaves the older gate alone", ok, reason)

# limits
check("round cap default is $20", wc.limit("round_usd") == 20.0, wc.limit("round_usd"))
check("broaden cap default is $3", wc.limit("broaden_usd") == 3.0, wc.limit("broaden_usd"))
check("one rerun: max_runs 2", wc.limit("max_runs") == 2, wc.limit("max_runs"))
os.environ["WC_LIMIT_ROUND_USD"] = "7.5"
check("env overrides the config value", wc.limit("round_usd") == 7.5, wc.limit("round_usd"))
os.environ.pop("WC_LIMIT_ROUND_USD")


# guard_run on a real child with a fake cost feed
def run_guard(cost, closed=lambda: False, broaden=lambda: False, cap=20.0, bcap=3.0, cmd=("sleep", "30")):
    t = time.time()
    seen = []
    rc = wc.guard_run(list(cmd), cost, closed, broaden, cap, bcap, 0.05, note=seen.append, sleep_grace=3)
    return rc, time.time() - t, seen


feed = iter([1, 5, 12, 19, 21, 30, 40])
rc, dt, seen = run_guard(lambda: next(feed))
check("killed at the cap: exit 90, and quickly", rc == 90 and dt < 10, (rc, dt))
check("the reading that stopped it is recorded", seen and seen[-1]["stop"] and "$21.00" in seen[-1]["stop"], seen[-1:])
rc, dt, _ = run_guard(lambda: 3.0, cmd=("sh", "-c", "sleep 0.5; exit 3"))
check("under the cap: the child's own exit code", rc == 3, rc)
rc, dt, _ = run_guard(lambda: 19.99, cmd=("sh", "-c", "sleep 0.5; exit 0"))
check("19.99 of 20 is not capped", rc == 0, rc)
state = {"b": False}
costs = iter([5, 6, 7, 8.5, 9, 9.5, 10, 11])


def bro():
    state["b"] = state["b"] or True
    return state["b"]


rc, dt, _ = run_guard(lambda: next(costs), broaden=bro)
check("broaden cap: killed $3 after the stage began: exit 91", rc == 91, rc)
n = {"i": 0}


def closed():
    n["i"] += 1
    return n["i"] > 3


rc, dt, _ = run_guard(lambda: 1.0, closed=closed)
check("the item closing ends the round: exit 92", rc == 92 and dt < 10, (rc, dt))

# rerun limit
check("first failure with new information: one rerun", wc.rerun_ok(1, 1, "a", "b", False, 2)[0])
check("second failure: no third run", not wc.rerun_ok(2, 1, "a", "b", False, 2)[0])
check("no new information: no rerun", not wc.rerun_ok(1, 1, "a", "a", False, 2)[0])
check("BLOCKED: no rerun", not wc.rerun_ok(1, 1, "a", "b", True, 2)[0])
check("after a hard stop: no rerun", not wc.rerun_ok(1, 90, "a", "b", False, 2)[0] and not wc.rerun_ok(1, 92, "a", "b", False, 2)[0])

# loop.sh wiring
sh = (ROOT / "infrastructure/whittle_claude/loop.sh").read_text(encoding="utf-8")
check("loop.sh starts the Whittle run under wc.py guard", re.search(r"\$WC guard .*--\s*\\\s*\n\s*timeout.*run\.py|\$WC guard", sh) is not None)
check("loop.sh asks rerun-ok before a second run", "$WC rerun-ok" in sh)
check("loop.sh no longer allows three runs", 'TRIES" -ge 3 ] && setcur phase=wrapup' not in sh and "of 3\"" not in sh.split("whittle)")[1].split("wrapup)")[0])
check("loop.sh parks a capped round and ends a closed one", "whittle_rc=capped" in sh and "whittle_rc=closed" in sh)
check("wc.py wrapup parks a capped round", '"capped"' in p.read_text(encoding="utf-8") and "parked by a hard stop" in p.read_text(encoding="utf-8"))

print("PASS" if not FAILS else "FAILED %d: %s" % (len(FAILS), ", ".join(FAILS)))
sys.exit(1 if FAILS else 0)
