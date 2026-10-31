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
check("owner escalation reads incident.owner_item", S.steward_escalated({"incident": {"owner_item": "X_1"}})
      and not S.steward_escalated({"incident": {"owner_item": None}}))


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
                           "steward": {"state": "BRAKED", "fault": True, "incident": {"owner_item": None}}}, NOW)
check("a steward fault before the owner rung -> steward badge, no remote signal",
      b["live"] == "steward" and not any(r["signal"] == "Steward escalation" for r in nd["remote"]), (b, nd["remote"]))
nd, b = S.needs_and_badges(ms, [], [], {"state": "BRAKED", "down_min": 0, "steward": {
    "state": "BRAKED", "fault": True, "incident": {"owner_item": "STEVE_OWNER_1"}}}, NOW)
check("a steward escalation to him is a remote decision with its item link",
      any(r["signal"] == "Steward escalation" and r["items"][0]["link"] == "/item/STEVE_OWNER_1" for r in nd["remote"]), nd["remote"])


# ---- hourly bucketing and staleness
def rec(t, **kw):
    return dict({"schema": S.SCHEMA, "t": t, "at": S.iso(t), "measures": {}, "badges": {}, "needed": {}, "steve": {},
                 "archmagi": {}, "brief": "b"}, **kw)


top = (NOW // H) * H
series = [rec(top - 2 * H + 60, measures={"A1": S.M(5, NOW)}), rec(top - 2 * H + 3000, measures={"A1": S.M(7, NOW)}),
          rec(top + 10, measures={"A1": S.U("blind")}), rec(top - 200 * H)]
sl = S.hourly(series, NOW)
check("hourly: 168 slots, the last record of an hour wins", len(sl) == 168 and sl[-3]["measures"]["A1"]["v"] == 7, sl[-3])
check("hourly: records older than 7 d are dropped, empty hours are None", sl[-2] is None and sum(1 for x in sl if x) == 2)
check("stale: latest real record 2 min old is fresh", not S.stale([rec(NOW - 120)], NOW))
check("stale: 46 min old greys the panel", S.stale([rec(NOW - 46 * 60)], NOW))
check("stale: a backfill record does not count as fresh", S.stale([rec(NOW - 60, backfill=True)], NOW))

# ---- the panel
live = rec(NOW - 120, measures={"A1": S.U("art queue unreadable: fixture"), "D1": S.M(4, NOW - 120, n=9, oldest_d=12.0, unit="waits over 3 d"),
                                "G2": S.M(0, NOW - 120, unit="% busy, 2 h")},
           badges={"art": "build the instrument", "design": "YOU (remote)"}, needed={"remote": [], "in_person": [], "asks": {}},
           steve={"state": "IDLE"}, archmagi={"state": "UP"})
page = S.render([rec(NOW - 3 * H, measures={"A1": S.M(50, NOW - 3 * H)}), live], NOW)
art = page[page.index("<h3>Art"):page.index("<h3>Design")]
check("panel: UNMEASURED lead draws hollow with its reason", "UNMEASURED" in art and "art queue unreadable: fixture" in art, art[:400])
check("panel: an UNMEASURED lead never shows a number", "<span class='v'>0" not in art and "<span class='v'>50" not in art)
check("panel: a MEASURED 0 does show 0", "<span class='v'>0<small>" in page)
check("panel: every measured value carries AS OF", page.count("AS OF") >= 3)
check("panel: fresh is not greyed", "class=stale" not in page)
check("panel: per-stream split absent draws hollow, not zero slots", "No per-stream split recorded" in page and "hollowbox" in page)
check("panel: no pacing record draws the Pacing tile hollow with its reason", "<h2>Pacing</h2>" in page
      and "No pacing recorded" in page, page[page.find("Pacing"):][:300])
pac = {"at": S.iso(NOW - 120), "mode": "CRUISE", "token_mode": "CRUISE", "queue_mode": "PAYDOWN", "presence": "BENCH",
       "seats": {"BENCH": 3, "FOUNDRY": 1}, "n_total": 4, "running": {"BENCH": 2, "FOUNDRY": 1},
       "overage": {"owed_h": 3.2, "paying": True, "cut": 1, "plan": "owes 3.2 helper-h: N lowered by 1 (wanted 1) for about 3 h, due within 20 h"},
       "why": "system 40% left, 1.99 d to reset -> P 1.40; fits 4.1",
       "accounts": [{"name": "system", "pct_left": 40.0, "hours_to_reset": 48.0, "source": "MEASURED", "burn": True},
                    {"name": "steven", "pct_left": 31.0, "hours_to_reset": 50.0, "source": "ESTIMATE", "burn": False,
                     "rule": "steven: off-limits until 2026-10-28T15:00:00-07:00"},
                    {"name": "lukas", "pct_left": None, "hours_to_reset": None, "source": "UNMEASURED", "burn": False}]}
pg = S.render([dict(live, pacing=pac)], NOW)
tile = pg[pg.index("<h2>Pacing</h2>"):pg.index("<h2>Builder slots</h2>")]
check("pacing tile: mode and N per seat", "CRUISE" in tile and "BENCH <b>3</b>" in tile and "FOUNDRY <b>1</b>" in tile
      and "2 running" in tile, tile[:600])
check("pacing tile: the overage owed and the payback plan", "overage owed" in tile and "3.2 helper-h" in tile
      and "lowered by 1" in tile, tile[:900])
check("pacing tile: no debt says so", "overage owed: <b>0 helper-h</b>" in S.pacing_tile(dict(pac, overage={"owed_h": 0}), NOW))
check("pacing tile: why the allocator chose it", "fits 4.1" in tile, tile[:600])
check("pacing tile: each account's % left against the share of the week left before its reset",
      "system" in tile and "40% left" in tile and "29% of the week" in tile and "31% left" in tile, tile[:900])
check("pacing tile: the burn account is marked and a lent account shows its rule", "seats burn this" in tile
      and "off-limits" in tile, tile[:900])
check("pacing tile: an unmeasured account is hollow, never 0%", "lukas" in tile and "UNMEASURED" in tile
      and "lukas 0%" not in tile, tile[:900])
check("pacing tile: the override flag is named", "--owner-said" in tile, tile[-400:])
check("panel: unrecorded hours in a state band are hollow", "class='hollow'" in page)
old = S.render([dict(live, t=NOW - 50 * 60)], NOW)
check("panel: a 50-min-old record greys the whole panel and says STALE", "class=stale" in old and "STALE" in old)
check("panel: no series at all says so", "No stream record yet" in S.render([], NOW))

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
                  RM_SLOT_OWNER_LEDGER=str(fx / "none.jsonl"))
pc_ = S.pacing(tn)
al = json.loads((Path(os.environ["RM_STREAMS_DIR"]) / "allocation.json").read_text()) \
    if (Path(os.environ["RM_STREAMS_DIR"]) / "allocation.json").exists() else {}
check("pacing(): runs the allocator and writes allocation.json for the hook", al.get("seats") == pc_.get("seats")
      and pc_.get("seats") == {"BENCH": 0, "FOUNDRY": 6}, (pc_, al.get("seats")))
check("pacing(): carries the accounts with % left and hours to reset", any(a["name"] == "system" and a["burn"]
      and a["pct_left"] == 40.0 for a in pc_.get("accounts") or []), pc_.get("accounts"))
check("collect() records pacing every 15 min", "pacing" in S.collect.__code__.co_names or "pacing(" in
      Path(S.__file__).read_text().split("def collect")[1].split("def series_path")[0])

os.environ["RM_STREAMS_DIR"] = str(Path(tempfile.mkdtemp()))
S.DIR = Path(os.environ["RM_STREAMS_DIR"])
S.append(dict(live, t=time.time() - 60, at=S.iso(time.time() - 60)))
import brief  # noqa: E402
code, ctype, body = brief.page("/streams", lambda: {}, Path(tempfile.mkdtemp()))
check("brief.page serves /streams (loopback and tailnet share it)", code == 200 and b"Where you're needed" in body, code)
code, ctype, body = brief.page("/streams.json", lambda: {}, Path(tempfile.mkdtemp()))
check("/streams.json gives the latest record and the stale flag", code == 200 and json.loads(body)["stale"] is False)
check("the brief carries the streams line", "streams</a>" in brief.streams_line(time.time()))

print("\nselftest_streams: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
