#!/usr/bin/env python3
"""Selftest for the stream series and the Streams panel (STREAM_METRICS_UNIFY_ONE_SERIES,
MODCHECK_METRICS_RETIRE_INTO_HOURLY, RIMPULSE_STREAMS_BUILD_VS_TIME).

Fixtures only, touching no live state: the nightly-file reader, unowned reds (O2), the modcheck fold (O4), useful vs
filler busy (G2), the steward.json reader, the whose-move badges and the remote / in-person split (no rule fires on
UNMEASURED), hourly bucketing, the 45-min stale rule, the tail reader on a large file, the backfill rewrite order,
and the panel itself: an UNMEASURED value draws hollow with its reason and never as 0.
"""
import atexit
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace as NS

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_streams_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)
os.environ["RM_PULSE_STATE"] = tempfile.mkdtemp(prefix="ss_state_")
os.environ["RM_STREAMS_DIR"] = tempfile.mkdtemp(prefix="ss_dir_")
HERE = Path(__file__).resolve().parent
# A frozen rules fixture, never the live slot_rules.json: an owner retune of the live file turned pacing() red twice
# (SELFTEST_FIX_STREAMS_FQCB; guard selftest_streams_rules_drift.py). Set before slot_allocator is imported.
os.environ["RM_SLOT_RULES"] = str(HERE / "fixtures" / "slot_rules_streams.json")
sys.path.insert(0, str(HERE))
import streams as S  # noqa: E402
import testing_metrics as T  # noqa: E402

FAILS = []
NOW = 1_792_000_000.0
H = 3600.0


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)


# ---- nightly reader (O1) and unowned reds (O2)
nf = Path(tempfile.mkdtemp()) / "selftests_nightly.last"
nf.write_text("PASS     1.2s  src/a/selftest_ok.py\nFAIL     3.0s  src/a/selftest_alpha.py\nCRASH    0.5s  src/b/selftest_beta.py\n"
              "UNMEASURED 1.0s  src/b/selftest_gamma.py\n\nPASS 7/10  FAIL 1/10  UNMEASURED 1/10  CRASH 1/10  SKIPPED 0/10\n"
              "RESULT: RED\n")
ny = S.nightly(nf)
check("nightly: counts and verdict", (ny.get("fail"), ny.get("crash"), ny.get("passed"), ny.get("verdict")) == (1, 1, 7, "RED"), ny)
check("nightly: reds are FAIL + CRASH only, not UNMEASURED", ny["reds"] == ["src/a/selftest_alpha.py", "src/b/selftest_beta.py"], ny["reds"])
check("nightly: a missing file is a reason, not zero reds", "why" in S.nightly(nf.parent / "nope"))
half = nf.parent / "half.last"
half.write_text("FAIL     3.0s  src/a/selftest_alpha.py\n")
check("nightly: a run in progress (no summary) is a reason", "why" in S.nightly(half))

world = NS(items={"FIX_ALPHA_1": NS(open=True, title="fix selftest_alpha crash"), "OLD_1": NS(open=False, title="selftest_beta")})
evs = [{"id": "FIX_ALPHA_1", "reason": "x"}, {"id": "OLD_1", "reason": "selftest_beta"}]
o = S.offline_measures(evs, world, NOW, ny=ny, crs=S.M(3, NOW), mx={"O4": S.U("fixture")})
check("O1 = FAIL + CRASH", o["O1"]["v"] == 2, o["O1"])
check("O2: a red named only by a CLOSED item is unowned", o["O2"]["v"] == 1 and o["O2"]["x"]["tests"] == ["src/b/selftest_beta.py"], o["O2"])
o = S.offline_measures(evs, world, NOW, ny={"why": "no file"}, crs=S.M(3, NOW), mx={"O4": S.U("fixture")})
check("O1/O2 UNMEASURED when the nightly file is unreadable", o["O1"]["m"] == o["O2"]["m"] == "UNMEASURED")

# ---- modcheck fold (item 2): O4 never a 0 standing for "no minutes"
real_compute = S.MX.compute


def fake(ex, off):
    return lambda *a, **k: {"day": "2026-10-26", "all_work": {"executed_min": ex}, "targeted": {}, "by_lane": {},
                            "alarms": [], "waste_top": [{"chain": "c", "why": "offline chain run in the live slot", "min": off}],
                            "gate": {}}


S.MX.compute = fake(0.2, 0.0)
m = S.modcheck_today(NOW)
check("O4 UNMEASURED with under a minute of classified live work", m["O4"]["m"] == "UNMEASURED", m["O4"])
check("the modcheck fold is kept in the record even when O4 is unmeasured", m["fold"]["day"] == "2026-10-26")
S.MX.compute = fake(10.0, 2.0)
check("O4 = offline minutes / executed minutes", S.modcheck_today(NOW)["O4"]["v"] == 20.0)
S.MX.compute = real_compute

# ---- guard: a crashing instrument blanks only its own measures, with the error as the reason
g = S.guard(lambda: 1 / 0, ("X1", "X2"))
check("guard: crash -> UNMEASURED with the exception", g["X1"]["m"] == "UNMEASURED" and "ZeroDivisionError" in g["X1"]["why"], g)

# ---- G2: useful vs filler busy (requested_by BENCH.filler)
atts = [{"started": NOW - 100 * 60, "finished": NOW - 70 * 60, "requested_by": "BENCH"},
        {"started": NOW - 60 * 60, "finished": NOW - 30 * 60, "requested_by": "BENCH.filler"}]
tot = T.length(S._spans(atts, [], NOW - 2 * H, NOW, NOW))
use = T.length(S._spans(atts, [], NOW - 2 * H, NOW, NOW, keep=lambda a: a.get("requested_by") != S.FILLER))
check("G2: busy splits into useful and filler", (tot, use) == (3600.0, 1800.0), (tot, use))

# ---- steward.json reader (§6.2), defensive on its key names
check("unowned from incident.unowned_s", S.steward_unowned_min({"incident": {"unowned_s": 600}}) == 10.0)
check("unowned from unowned_min", S.steward_unowned_min({"unowned_min": 4}) == 4)
check("no fault and no incident = 0 unowned", S.steward_unowned_min({"fault": False}) == 0)
check("unknown shape = None (UNMEASURED), not 0", S.steward_unowned_min({}) is None)
sr = tempfile.mkdtemp()
sp = os.path.join(sr, "steward.json")
json.dump({"state": "BRAKED", "fault": True}, open(sp, "w"))
os.utime(sp, (NOW - 60, NOW - 60))
check("fresh steward.json is read", (S.steward_now(NOW, sr)[0] or {}).get("state") == "BRAKED")
os.utime(sp, (NOW - 600, NOW - 600))
st, why = S.steward_now(NOW, sr)
check("a steward.json older than 5 min is STALE_HEARTBEAT, not read", st is None and "STALE_HEARTBEAT" in why, why)
check("no steward.json names the build item", "STEVE_STEWARD_BUILD_NO_LLM_OWNER" in S.steward_now(NOW, tempfile.mkdtemp())[1])


# ---- badges and where-you're-needed (§5): no rule fires on UNMEASURED
def base_ms(**over):
    ms = {k: S.U("fixture") for k in ("A1", "D1", "D4", "V0", "O1", "G1", "G2", "W1")}
    ms.update(over)
    return ms


steve_ok = {"state": "IDLE", "down_min": 0, "steward": {}}
nd, b = S.needs_and_badges(base_ms(), [], [], steve_ok, NOW)
check("all lead measures UNMEASURED: every badge says build the instrument, nothing asked of him",
      set(b.values()) == {"build the instrument"} and not nd["remote"] and not nd["in_person"], (b, nd))
ms = base_ms(A1=S.M(40, NOW, oldest_d=2.0, oldest_sheet="s", top_sheets=[{"sheet": "s", "rows": 40}]),
             D1=S.M(3, NOW, n=9, oldest_d=12.0), V0=S.M(5, NOW), O1=S.M(0, NOW), G2=S.M(80, NOW), W1=S.M(2, NOW))
rem = [{"id": "OLD_ASK_1", "label": "old", "class": "rule", "age_d": 9.0, "link": "/item/OLD_ASK_1"},
       {"id": "NEW_ASK_1", "label": "new", "class": "look", "age_d": 1.0, "link": "/item/NEW_ASK_1"}]
inp = [{"id": "HANDS_1", "label": "plug it", "class": "hands", "age_d": 1.0, "link": "/item/HANDS_1"},
       {"id": "WALK_1", "label": "walk", "class": "walk", "age_d": 1.0, "link": "/item/WALK_1"}]
nd, b = S.needs_and_badges(ms, rem, inp, steve_ok, NOW)
sig = {r["signal"]: r for r in nd["remote"]}
check("A1 over 30 -> remote pick signal and art badge YOU (remote)", "Pick queue" in sig and b["art"] == "YOU (remote)", b)
check("D1 > 0 -> design YOU (remote), listing only asks over 3 d",
      b["design"] == "YOU (remote)" and [i["id"] for i in sig["Waiting on you"]["items"]] == ["OLD_ASK_1"], sig.get("Waiting on you"))
check("hands chores are in person; walks are an info line, not a request",
      [r["signal"] for r in nd["in_person"]] == ["A login or a physical action"] and nd["walk_note"]
      and [i["id"] for i in nd["in_person"][0]["items"]] == ["HANDS_1"], nd)
check("dev / offline / walk stay with agents", (b["dev"], b["offline"], b["walk"]) == ("agents",) * 3, b)
nd, b = S.needs_and_badges(dict(ms, A1=S.M(10, NOW, oldest_d=2.0)), rem, [], {"state": "DOWN", "down_min": 45, "steward": {}}, NOW)
check("Steve unreachable 45 min -> in person and live badge YOU (in person)",
      b["live"] == "YOU (in person)" and nd["in_person"][0]["signal"] == "Machine unreachable" and b["art"] == "agents", (b, nd))
nd, b = S.needs_and_badges(ms, [], [], {"state": "DOWN", "down_min": 10, "steward": {}}, NOW)
check("Steve down 10 min is not yet his move", b["live"] == "agents" and not nd["in_person"], b)
nd, b = S.needs_and_badges(dict(ms, G1=S.M(12, NOW)), [], [], {"state": "BRAKED", "down_min": 0,
                           "steward": {"state": "BRAKED", "fault": True, "incident": {"told": None}}}, NOW)
check("a steward fault -> steward badge, no remote signal",
      b["live"] == "steward" and not any(r["signal"] == "Steward escalation" for r in nd["remote"]), (b, nd["remote"]))
nd, b = S.needs_and_badges(ms, [], [], {"state": "BRAKED", "down_min": 0, "steward": {
    "state": "BRAKED", "fault": True, "incident": {"level": 3, "told": "2026-11-05T00:00:00Z"}}}, NOW)
check("the steward's T+120 rung tells Operations, never his remote queue (STEWARD_RUNG_FIX_ASKS_THE_WRONG_GROWNUP)",
      not any(r["signal"] == "Steward escalation" for r in nd["remote"]), nd["remote"])


# ---- a series record
def rec(t, **kw):
    return dict({"schema": S.SCHEMA, "t": t, "at": S.iso(t), "measures": {}, "badges": {}, "needed": {}, "steve": {},
                 "archmagi": {}, "brief": "b"}, **kw)


# ---- write, tail-read, backfill order, routes
sfile = Path(os.environ["RM_STREAMS_DIR"]) / "series.jsonl"
pad = "x" * 4000
for i in range(900):   # ~3.6 MB: more than the first 2 MB block, so the tail reader must widen
    S.append(rec(NOW - (900 - i) * 600, pad=pad), sfile)
got = S.read_series(sfile, since=NOW - 7 * 86400)
want = sum(1 for i in range(900) if NOW - (900 - i) * 600 >= NOW - 7 * 86400)
check("tail reader returns exactly the records since the cut on a multi-MB file", len(got) == want, (len(got), want))
check("tail reader with no cut reads them all", len(S.read_series(sfile)) == 900)
bfile = Path(tempfile.mkdtemp()) / "series.jsonl"
S.append(rec(NOW - 30), bfile)
n = S.backfill(days=0.25, path=bfile, events=[], src={"why": "fixture", "attempts": [], "running": [], "pending": []}, now=NOW)
bs = S.read_series(bfile)
check("backfill adds the missing past hours, marked backfill", n >= 5 and sum(1 for r in bs if r.get("backfill")) == n, n)
ts = [json.loads(ln)["t"] for ln in bfile.read_text().splitlines()]
check("backfill rewrites the file in time order (the tail reader relies on it)", ts == sorted(ts))
check("backfill never invents a present-only measure", all(r["measures"]["A1"]["m"] == "UNMEASURED" for r in bs if r.get("backfill")))
check("backfill skips an hour a real record already covers", len({int(r["t"] // H) for r in bs}) == len(bs))

# ---- the 15-min re-check: pacing() runs the allocator, writes allocation.json, returns the tile record
import slot_allocator as SA  # noqa: E402
import account_live as AL  # noqa: E402
fx = Path(tempfile.mkdtemp(prefix="ss_pace_"))
(fx / "projects" / "-home-mandrake-rm-bench").mkdir(parents=True)
(fx / "projects" / "-home-mandrake-rm-foundry").mkdir(parents=True)
(fx / "au").mkdir()
tn = time.time()
(fx / "au" / "latest.json").write_text(json.dumps({"schema": 1, "updated": SA.iso_local(tn), "accounts": {
    "system": {"account": "system", "machine": "testhost", "source": "MEASURED", "ts": SA.iso_local(tn),
               "measured_at": SA.iso_local(tn - 60), "week_pct_used": 60.0, "week_resets_at": SA.iso_local(tn + 48 * H),
               "session_pct_used": 18.0, "session_resets_at": SA.iso_local(tn + 3 * H)}}}))
(fx / "au" / "series.jsonl").write_text("")
os.environ.update(RM_SLOT_PROJECTS=str(fx / "projects"), RM_ACCOUNT_USAGE_DIR=str(fx / "au"), RM_SLOT_MACHINE="testhost",
                  RM_SLOT_OWNER_LEDGER=str(fx / "none.jsonl"),
                  RM_CLAUDE_ACCOUNT=AL.fake_switcher(fx, "system"))  # hermetic: never the real claude-account
pc_ = S.pacing(tn)
al = json.loads((Path(os.environ["RM_STREAMS_DIR"]) / "allocation.json").read_text()) \
    if (Path(os.environ["RM_STREAMS_DIR"]) / "allocation.json").exists() else {}
check("pacing(): reads the frozen rules fixture, not the live slot_rules.json", SA.RULES == Path(os.environ["RM_SLOT_RULES"])
      and SA.RULES.parent.name == "fixtures", SA.RULES)
_adv = SA.load_rules().get("advisory") or {}   # the fixture's advisory: the placed total is the floor (owner 2026-11-02/04)
_want = max(6, _adv.get("n_total", 0)) if _adv.get("enabled") is True else 6   # 6 = CRUISE's pace on this fixture
check("pacing(): runs the allocator and writes allocation.json for the hook", al.get("seats") == pc_.get("seats")
      and pc_.get("seats") == {"BENCH": 0, "RELENTLESS": _want}, (pc_, al.get("seats"), _want))
check("pacing(): carries the accounts with % left and hours to reset", any(a["name"] == "system" and a["burn"]
      and a["pct_left"] == 40.0 for a in pc_.get("accounts") or []), pc_.get("accounts"))
check("collect() records pacing every 15 min", "pacing" in S.collect.__code__.co_names or "pacing(" in
      Path(S.__file__).read_text().split("def collect")[1].split("def series_path")[0])

# ---- game state and budget come from live readers, each with its age (WIRE_STREAMS_GAME_STATE_OFF_A_FROZEN_SNAPSHOT)
gr = lambda implies, at=NOW - 30, **kw: S.game_reading({"implies": implies, "evidence": "probe says " + str(implies), "at": at}, **kw)  # noqa: E731
check("game: probe UP is UP with its reading time", gr("UP")[0] == "UP" and gr("UP")[2] == S.iso(NOW - 30), gr("UP"))
check("game: probe DOWN is DOWN", gr("DOWN")[0] == "DOWN", gr("DOWN"))
check("game: LOADING is not UP", gr("LOADING")[0] == "LOADING", gr("LOADING"))
check("game: a probe that could not look is UNKNOWN with its evidence, never DOWN", gr(None)[0] == "UNKNOWN" and "probe says" in gr(None)[1], gr(None))
check("game: UP with a bridge call in the last 15 min is DRIVING", gr("UP", last=NOW - 60, now=NOW)[0] == "DRIVING", gr("UP", last=NOW - 60, now=NOW))
check("game: UP with a stale bridge call stays UP", gr("UP", last=NOW - 3600, now=NOW)[0] == "UP")
check("game: DOWN is never DRIVING", gr("DOWN", last=NOW - 60, now=NOW)[0] == "DOWN")
acc = {"lukas": {"week_pct_left": 100.0, "age_min": 8.5, "measured_at": S.iso(NOW - 510), "hours_to_week_reset": 140.0, "stale": False},
       "steven": {"week_pct_left": 51.0, "age_min": 8.5, "measured_at": S.iso(NOW - 510), "hours_to_week_reset": 142.0, "stale": False},
       "system": {"week_pct_left": None, "age_min": None, "measured_at": None, "hours_to_week_reset": None, "stale": True}}
b = S.budget(NOW, acc)
check("budget: the lowest LEFT among measured accounts, with its age", b["m"] == "MEASURED" and b["v"] == 51.0 and "LEFT" in b["x"]["unit"], b)
check("budget: an unmeasured account is listed unmeasured, not 0 left", any(r["name"] == "system" and r["pct_left"] is None for r in b["x"]["accounts"]), b)
check("budget: no account measured is UNMEASURED", S.budget(NOW, {"x": {"week_pct_left": None}})["m"] == "UNMEASURED")
check("budget: no readings at all is UNMEASURED", S.budget(NOW, {})["m"] == "UNMEASURED")
src_text = Path(S.__file__).read_text()
check("streams reads neither pulse_now.json nor the rm-dashboard usage.json", "pulse_now.json" not in src_text and 'STATE_DIR / "usage.json"' not in src_text)

print("\nselftest_streams: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
