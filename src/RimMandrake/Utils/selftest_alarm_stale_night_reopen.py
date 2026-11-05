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
Third instance (NIGHTLY_COP_FIX_RED_BGMSKV_VSAQ): NIGHTLY_RED:testing.red_bgmskv's item closed 2026-11-04T22:18:44Z on a
green rerun (its red, selftest_bridge_hooks RootFinalizer, cured at cbfcc52bc7); reopened 05:23:45Z on the same night.
Fourth instance (NIGHTLY_COP_FIX_RED_PJLJVQ_TTXI): NIGHTLY_RED:testing.red_pjljvq's item (the enrichment plan's PLAN
DRIFT, cured at cbfcc52bc7) closed 2026-11-04T22:19:21Z on a green rerun; reopened 05:22Z on the same night.
Fifth instance (NIGHTLY_COP_FIX_RED_QHQXLR_JQBT): NIGHTLY_RED:testing.red_qhqxlr's item (selftest_conductor_reset_mode
"and only that one", cured at 40de8bea3d) closed 2026-11-04T22:19:24Z on a green rerun; reopened 05:22Z, same night.
Sixth instance (NIGHTLY_COP_FIX_RED_UQUVZZ_AYSU): NIGHTLY_RED:testing.red_uquvzz's item (selftest_deploy_deleted's
compare_then_vanish stub, cured at 2026-11-04 14:04Z) closed 2026-11-04T22:19:34Z on a green rerun; reopened 05:26:15Z.
Seventh instance (NIGHTLY_COP_FIX_RED_WABGHY_BUUY): NIGHTLY_RED:testing.red_wabghy's item (selftest_shipped_defs, the
StarWarsPatches def floor 30 over 29 real, cured at 40de8bea3d) closed 2026-11-04T22:19:37Z on a green rerun; reopened
05:22Z (alarms_log "reopen_closed_still_crossed") on the same night.
Eighth instance (SELFTEST_FIX_LIVE_QUEUE_QBHV), a second ROUTE: NIGHTLY_RED:testing.red_hnpuya's item closed
2026-11-05T13:05:45Z on its fix; the dispatch clone's ledger read lacked the item, so its alarm went PENDING
(open_without_item), then at 14:49:55Z "found_closed" re-armed it as a reopen with no stale_for_close check, and a light
beat (file_held) filed it 16:26:25Z on the 2026-11-05T11:00Z night, which ran before the fix.
Ninth instance (SELFTEST_FIX_EXTRA_ART_COMMISSION_UBZM), the same route with no crossed reading that pass: red_znpqoq's
item closed 13:34:26Z; at 14:49:55Z a compose pass had dropped the carried reading (crossed None), found_closed marked a
reopen with no stale check, and file_held filed it 16:23:46Z on the same pre-close night.
Tenth instance (SELFTEST_FIX_RELENTLESS_TICK_STAMP_DVDQ), the eighth's route: red_hooqkv's item closed 13:05:57Z on its
fix (selftest_relentless_tick_stamp's fake folded(), cured at 021255da88); reopened 16:29:05Z and 16:32:52Z on the
2026-11-05T11:00Z night, before bc25b60bda landed. Replaying bc25b60bda^ FAILs.

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


def closed_instance(aid, closed, read_at, what):
    """One live instance: its item filed on the 11-04T11:00Z night, closed at `closed`, read again at `read_at` with
    only that night to read. It must not reopen."""
    global AID, KEY
    saved = AID, KEY
    AID = aid
    KEY = AID.split(":", 1)[1]
    try:
        reset()
        b = Bench(OW.epoch("2026-11-04T11:52:00Z") - 900)
        item = filed_item(b, NIGHT1)
        b.t = OW.epoch(read_at) - 900
        st = b.read(point(NIGHT1), set(), closed_at={item: [OW.epoch(closed)]})
        ok(st is not None and not reopened(b, item), what)
    finally:
        AID, KEY = saved


def test_bcbosb_instance():
    """NIGHTLY_COP_FIX_RED_BCBOSB_PWDD: closed 22:18:40Z on a green rerun, read again at 05:22Z on the 11:00Z night."""
    closed_instance("NIGHTLY_RED:testing.red_bcbosb", "2026-11-04T22:18:40Z", "2026-11-05T05:22:00Z",
                    "red_bcbosb closed 22:18:40Z, read at 05:22Z on the 11:00Z night: no reopen (the second instance)")


def test_bgmskv_instance():
    """NIGHTLY_COP_FIX_RED_BGMSKV_VSAQ: closed 22:18:44Z on a green rerun (its RootFinalizer red cured at cbfcc52bc7),
    reopened 05:23:45Z ("live broken") on the 11:00Z night, which ran before that fix."""
    closed_instance("NIGHTLY_RED:testing.red_bgmskv", "2026-11-04T22:18:44Z", "2026-11-05T05:23:45Z",
                    "red_bgmskv closed 22:18:44Z, read at 05:23:45Z on the 11:00Z night: no reopen (the third instance)")


def test_pjljvq_instance():
    """NIGHTLY_COP_FIX_RED_PJLJVQ_TTXI: closed 22:19:21Z on a green rerun (its PLAN DRIFT red cured at cbfcc52bc7),
    reopened 05:22Z (alarms_log "reopen_closed_still_crossed") on the 11:00Z night, which ran before that fix."""
    closed_instance("NIGHTLY_RED:testing.red_pjljvq", "2026-11-04T22:19:21Z", "2026-11-05T05:22:00Z",
                    "red_pjljvq closed 22:19:21Z, read at 05:22Z on the 11:00Z night: no reopen (the fourth instance)")


def test_qhqxlr_instance():
    """NIGHTLY_COP_FIX_RED_QHQXLR_JQBT: closed 22:19:24Z on a green rerun (its reset-mode "and only that one" red cured at
    40de8bea3d, 14:04Z), reopened 05:22Z (alarms_log "reopen_closed_still_crossed") on the 11:00Z night before that fix."""
    closed_instance("NIGHTLY_RED:testing.red_qhqxlr", "2026-11-04T22:19:24Z", "2026-11-05T05:22:00Z",
                    "red_qhqxlr closed 22:19:24Z, read at 05:22Z on the 11:00Z night: no reopen (the fifth instance)")


def test_uquvzz_instance():
    """NIGHTLY_COP_FIX_RED_UQUVZZ_AYSU: closed 22:19:34Z on a green rerun (selftest_deploy_deleted's compare stub, cured
    14:04Z), reopened 05:26:15Z ("live broken") on the 11:00Z night, which ran before that fix."""
    closed_instance("NIGHTLY_RED:testing.red_uquvzz", "2026-11-04T22:19:34Z", "2026-11-05T05:26:15Z",
                    "red_uquvzz closed 22:19:34Z, read at 05:26:15Z on the 11:00Z night: no reopen (the sixth instance)")


def test_wabghy_instance():
    """NIGHTLY_COP_FIX_RED_WABGHY_BUUY: closed 22:19:37Z on a green rerun (selftest_shipped_defs' StarWarsPatches floor,
    cured at 40de8bea3d, 14:04Z), reopened 05:22Z (alarms_log "reopen_closed_still_crossed") on the 11:00Z night."""
    closed_instance("NIGHTLY_RED:testing.red_wabghy", "2026-11-04T22:19:37Z", "2026-11-05T05:22:00Z",
                    "red_wabghy closed 22:19:37Z, read at 05:22Z on the 11:00Z night: no reopen (the seventh instance)")


def test_found_closed_route():
    """SELFTEST_FIX_LIVE_QUEUE_QBHV: a PENDING alarm (open_without_item) whose item the ledger shows closed is re-armed
    only on a night after that close; on the stale night it stays acknowledged on its item."""
    global AID, KEY
    saved = AID, KEY
    AID = "NIGHTLY_RED:testing.red_hnpuya"
    KEY = AID.split(":", 1)[1]
    try:
        reset()
        b = Bench(OW.epoch("2026-11-05T12:22:00Z") - 900)
        item = filed_item(b, NIGHT2)
        closed = {item: [OW.epoch("2026-11-05T13:05:45Z")]}
        p = OW.ops_dir() / "alarms.json"
        st = OW.read_json(p)
        st[AID].update(state="PENDING", item=None, deferred_at="2026-11-05T14:12:49Z")    # after open_without_item
        OW.atomic_json(p, st)
        b.t = OW.epoch("2026-11-05T14:49:55Z") - 900
        st = b.read(point(NIGHT2), set(), closed_at=closed)
        cur = (st or {}).get(AID) or {}
        ok(st is not None and not reopened(b, item) and not cur.get("reopen"),
           "red_hnpuya closed 13:05:45Z, found closed at 14:49:55Z on the 11:00Z night: not re-armed (the eighth instance)")
        ok(cur.get("state") == "OPEN" and cur.get("item") == item, "the stale found_closed alarm stays OPEN on its item")
        held = OW.file_held(b.filer, RULES, b.t + 60) or {}
        ok(not reopened(b, item) and not (held.get(AID) or {}).get("reopen"), "a light beat files nothing for it")
        st = b.read(point("2026-11-06T11:00:00Z"), set(), closed_at=closed)
        ok(st is not None and reopened(b, item), "the next night, still red after the close: reopened")
    finally:
        AID, KEY = saved


def test_znpqoq_instance():
    """SELFTEST_FIX_EXTRA_ART_COMMISSION_UBZM: the found_closed route with NO crossed reading that pass. Its item closed
    2026-11-05T13:34:26Z; at 14:49:55Z the compose pass had dropped the carried 11:00Z reading (crossed None), so
    QBHV's stale_for_close never ran, "found_closed" marked a reopen, and file_held filed it at 16:23:46Z."""
    global AID, KEY
    saved = AID, KEY
    AID = "NIGHTLY_RED:testing.red_znpqoq"
    KEY = AID.split(":", 1)[1]
    try:
        reset()
        b = Bench(OW.epoch("2026-11-05T12:37:00Z") - 900)
        item = filed_item(b, NIGHT2)
        closed = {item: [OW.epoch("2026-11-05T13:34:26Z")]}
        p = OW.ops_dir() / "alarms.json"
        st = OW.read_json(p)
        st[AID].update(state="PENDING", item=None, deferred_at="2026-11-05T14:39:40Z")    # after open_without_item
        OW.atomic_json(p, st)
        b.t = OW.epoch("2026-11-05T14:49:55Z")
        b.sent = []
        st = OW.run_alarms({}, RULES, b.t, b.filed | {"SOME_ITEM"}, b.filer, set(), closed_at=closed)   # reading dropped
        cur = (st or {}).get(AID) or {}
        ok(not reopened(b, item) and not cur.get("reopen"),
           "red_znpqoq closed 13:34:26Z, found closed at 14:49:55Z with no reading this pass: not re-armed (the ninth instance)")
        held = OW.file_held(b.filer, RULES, b.t + 60) or {}
        ok(not reopened(b, item) and not (held.get(AID) or {}).get("reopen"), "a light beat files nothing for it")
        st = b.read(point("2026-11-06T11:00:00Z"), set(), closed_at=closed)
        ok(st is not None and reopened(b, item), "the next night, still red after the close: reopened")
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
    for fn in (test_stale_night_holds, test_bcbosb_instance, test_bgmskv_instance, test_pjljvq_instance, test_qhqxlr_instance,
               test_uquvzz_instance, test_wabghy_instance, test_found_closed_route, test_znpqoq_instance,
               test_unchanged_without_a_night_or_close_times):
        fn()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    sys.exit(1 if FAILS else 0)
