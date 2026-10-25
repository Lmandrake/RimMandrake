"""Offline checks for work_bar.py (WORK_PRIORITY_FIX_ZERO_IGNORED_UNMANUAL): a bar that did not take must read as a failure,
and the live runners must route their work-priority writes through it. No bridge."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import work_bar as W  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []


def check(name, cond):
    print("%-4s  %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        fails.append(name)


good = {"success": True, "requested": 0, "readBack": 0, "manualPrioritiesOn": True}
check("manual on + readBack 0 -> ok", W.check_reply(good, 0)[0])
check("manual OFF (old DLL / flag unset) -> not ok even if readBack matches", not W.check_reply(dict(good, manualPrioritiesOn=False), 0)[0])
check("manual OFF with readBack 3 for a requested 1 -> not ok", not W.check_reply({"success": True, "readBack": 3, "manualPrioritiesOn": False}, 1)[0])
check("readBack != requested -> not ok", not W.check_reply(dict(good, readBack=3), 0)[0])
check("refused reply -> not ok", not W.check_reply({"success": False, "error": "disabled"}, 1)[0])
check("None reply -> not ok", not W.check_reply(None, 0)[0])

sent = []


def fake(tool, **kw):
    sent.append((tool, kw))
    return {"success": True, "readBack": kw["priority"], "manualPrioritiesOn": bool(kw.get("manualPriorities"))}


ok, _ = W.set_all(fake, "P1", [("Mining", 1), ("Hauling", 0)])
check("set_all passes manualPriorities=True on every call", ok and len(sent) == 2 and all(k.get("manualPriorities") is True for _, k in sent))
bad = lambda tool, **kw: {"success": True, "readBack": 3, "manualPrioritiesOn": False}  # noqa: E731
ok, why = W.set_all(bad, "P1", [("Mining", 1), ("Hauling", 0)])
check("set_all stops and reports on the first bar that did not take", (not ok) and "Mining" in why)

for fn in ("shovels_live.py", "gravel_live.py"):
    src = open(os.path.join(HERE, fn), encoding="utf-8").read()
    check("%s imports work_bar" % fn, "import work_bar" in src)
    check("%s has no raw set_work_priority call left" % fn, not re.search(r'["\']jawa/set_work_priority["\']', src))
print("%d failed" % len(fails))
sys.exit(1 if fails else 0)
