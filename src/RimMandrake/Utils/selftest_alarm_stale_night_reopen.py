#!/usr/bin/env python3
"""selftest_alarm_stale_night_reopen.py -- NIGHTLY_COP_FIX_RED_ENVEHB_GOEW: a closed alarm item reopens only on a
reading taken AFTER it closed.

The instance: NIGHTLY_RED:testing.red_envehb's item closed 2026-11-04T13:31Z on its fix; no night ran after it, and
at 2026-11-05T05:22Z ops_watch reopened it ("reopen_closed_still_crossed") on the 2026-11-04T11:00Z night, which ran
before the fix existed. A reading that predates the close is not evidence the fix died. Real rules, real
ops_watch.run_alarms, with the ledger's close times (ctx["closes"], {item: [epoch, ...]}) handed in as closed_at:
- a closed item, reading's night before its last close: held, no reopen;
- the same item, a night after the close still crossed: reopened (OPS_ALARM_FIX_CLOSED_TICKET_SILENCES_FAULT stands);
- a reading with no night: unchanged (reopens), and no close times known: unchanged (reopens).
Second instance (NIGHTLY_COP_FIX_RED_BCBOSB_PWDD): NIGHTLY_RED:testing.red_bcbosb's item closed 2026-11-04T22:18:40Z on
a green rerun; at 2026-11-05T05:22Z the same 11-04T11:00Z night reopened it (alarms_log "reopen_closed_still_crossed").

  python3 selftest_alarm_stale_night_reopen.py --blob REV:PATH   replay ops_watch.py as it stood at REV (git), e.g.
      --blob 618deb68f3^:src/RimMandrake/Utils/ops_watch.py, the code that reopened both instances: it must FAIL.
"""
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
TMP = Path(tempfile.mkdtemp(prefix="selftest_alarm_stale_night_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RM_DATA_ROOT"] = str(TMP / "data")
(TMP / "ops").mkdir()
if "--blob" in sys.argv:        # replay a past ops_watch.py, run under the real file's name so its HERE paths hold
    import subprocess
    import types
    _blob = sys.argv[sys.argv.index("--blob") + 1]
    _src = subprocess.run(["git", "show", _blob], cwd=str(HERE.parents[2]), capture_output=True, text=True, check=True).stdout
    OW = types.ModuleType("ops_watch")
    OW.__file__ = str(HERE / "ops_watch.py")
    sys.modules["ops_watch"] = OW
    exec(compile(_src, OW.__file__, "exec"), OW.__dict__)
    print("replaying ops_watch.py from %s" % _blob)
else:
    import ops_watch as OW      # noqa: E402

FAILS = []
RULES = OW.load_rules()
for _t in RULES["targets"]:     # never the real Conductor log
    if _t.get("conductor_log"):
        _t["conductor_log"] = str(TMP / "conductor_log.md")
OW.mint_name = lambda tag, known, prefix: prefix if prefix.count("_") >= 2 else prefix + "_TEST"
AID = "NIGHTLY_RED:testing.red_envehb"
KEY = AID.split(":", 1)[1]
NIGHT1 = "2026-11-04T11:00:00Z"
NIGHT2 = "2026-11-05T11:00:00Z"
CLOSE = OW.epoch("2026-11-04T13:31:48Z")


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def reset():
    for n in ("alarms.json", "alarms_log.jsonl"):
        p = OW.ops_dir() / n
        if p.exists():
            p.unlink()


def point(night):
    x = {"said": "1 red", "news": ["src/selftest_x.py (due 2026-11-05T17:07:20Z)"],
         "titled": {"src/selftest_x.py (due 2026-11-05T17:07:20Z)": "selftest_x.py"}}
    if night:
        x["night"] = night
    return OW.M(1, "nightly reds with one first error line, no entry parking them", **x)


class Bench:
    def __init__(self, t):
        self.t, self.sent, self.filed = t, [], set()

    def filer(self, todo, conf):
        self.sent = list(todo)
        self.filed |= {a["name"] for a in todo if not a.get("note_only")}
        return {a["name"]: None for a in todo}

    def read(self, pt, open_ids, closed_at=None):
        self.t += 900
        self.sent = []
        try:
            kw = {} if closed_at is None else {"closed_at": closed_at}
            return OW.run_alarms({KEY: pt}, RULES, self.t, self.filed | {"SOME_ITEM"}, self.filer, open_ids, **kw)
        except TypeError as e:
            ok(False, "run_alarms takes the ledger's close times (closed_at): %s" % e)
            return None


def reopened(b, item):
    return any(a["name"] == item and a.get("reopen") and not a.get("note_only") for a in b.sent)


def filed_item(b, night):
    st = b.read(point(night), None)
    cur = (st or {}).get(AID) or {}
    ok(cur.get("state") == "OPEN" and cur.get("item"), "the red group files an item")
    return cur.get("item")


def test_stale_night_holds():
    reset()
    b = Bench(CLOSE - 7200)
    item = filed_item(b, NIGHT1)
    b.t = CLOSE + 60000         # 2026-11-05 ~05:00Z: the item closed, still only the 11-04 night to read
    st = b.read(point(NIGHT1), set(), closed_at={item: [CLOSE]})
    ok(st is not None and not reopened(b, item),
       "closed at 13:31Z, the only night is 11:00Z the same day (before the fix): no reopen (the instance)")
    st = b.read(point(NIGHT2), set(), closed_at={item: [CLOSE]})
    ok(st is not None and reopened(b, item), "the next night, still red after the close: reopened")


def test_bcbosb_instance():
    """NIGHTLY_COP_FIX_RED_BCBOSB_PWDD: closed 22:18:40Z on a green rerun, read again at 05:22Z on the 11:00Z night."""
    global AID, KEY
    saved = AID, KEY
    AID = "NIGHTLY_RED:testing.red_bcbosb"
    KEY = AID.split(":", 1)[1]
    try:
        reset()
        close = OW.epoch("2026-11-04T22:18:40Z")
        b = Bench(OW.epoch("2026-11-04T11:52:00Z") - 900)
        item = filed_item(b, NIGHT1)
        b.t = OW.epoch("2026-11-05T05:22:00Z") - 900
        st = b.read(point(NIGHT1), set(), closed_at={item: [close]})
        ok(st is not None and not reopened(b, item),
           "red_bcbosb closed 22:18:40Z, read at 05:22Z on the 11:00Z night: no reopen (the second instance)")
    finally:
        AID, KEY = saved


def test_unchanged_without_a_night_or_close_times():
    reset()
    b = Bench(CLOSE - 7200)
    item = filed_item(b, None)
    b.read(point(None), set(), closed_at={item: [CLOSE]})
    ok(reopened(b, item), "a reading with no night: a closed item still reopens, as before")
    reset()
    b = Bench(CLOSE - 7200)
    item = filed_item(b, NIGHT1)
    b.read(point(NIGHT1), set(), closed_at={})
    ok(reopened(b, item), "no close time known for the item: reopens, as before")


if __name__ == "__main__":
    for fn in (test_stale_night_holds, test_bcbosb_instance, test_unchanged_without_a_night_or_close_times):
        fn()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    sys.exit(1 if FAILS else 0)
