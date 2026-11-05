#!/usr/bin/env python3
"""ops_watch's metronome mode (OPS_METRONOME_MIGRATE_CLOCKS_FENCED): `run --compose` carries every family it did not
measure from its last series record, files alarms only on the pass that measures COMPOSE_ALARM_FAMILY, and the
ownership fence (`--metronome-gen`, still_owner) stops a pass from publishing. Fixture-only: stub collectors, temp dirs."""
import json
import os
import sys
import tempfile as _tf
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_TMP = Path(_tf.mkdtemp(prefix="selftest_ops_watch_compose_"))
os.environ["RM_OPS_WATCH_DIR"] = str(_TMP / "ops")
import ops_watch as OW  # noqa: E402
import metronome  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


calls = []


def stub(fam):
    def c(now, rules, ctx):
        calls.append(fam)
        return {"%s.stub" % fam: OW.M(len(calls), "n")}
    return c


OW.COLLECTORS = {f: stub(f) for f in OW.ORDER}
alarm_runs = []
_real_alarms = OW.run_alarms
OW.run_alarms = lambda *a, **k: (alarm_runs.append(1), {})[1]
rules = OW.load_rules()
t0 = time.time() - 600

OW.run(now=t0, rules=rules)                                  # a whole pass seeds every series
check("a whole pass runs every collector", sorted(calls) == sorted(OW.ORDER), calls)
check("a whole pass runs the alarms", len(alarm_runs) == 1)
calls.clear()
alarm_runs.clear()
OW.run(now=t0 + 60, rules=rules, families=["accounts", "codex"], compose=True)
st = json.loads((_TMP / "ops" / "status.json").read_text())
check("compose: only its own families are measured", calls == ["accounts", "codex"], calls)
check("compose: the status holds every family", all("%s.stub" % f in st["points"] for f in OW.ORDER),
      sorted(k for k in st["points"] if k.endswith(".stub")))
check("compose: a carried reading says when it was observed",
      (st["points"]["flow.stub"].get("x") or {}).get("observed_at") == OW.iso(t0), st["points"]["flow.stub"])
check("compose: its own reading is this pass's", "observed_at" not in (st["points"]["accounts.stub"].get("x") or {}))
check("compose: the health verdict is written", "health.state" in st["points"], sorted(st["points"])[:5])
check("compose: no alarm pass without %s" % OW.COMPOSE_ALARM_FAMILY, alarm_runs == [], alarm_runs)
OW.run(now=t0 + 120, rules=rules, families=["flow", "testing"], compose=True)
check("compose: the pass measuring %s runs the alarms" % OW.COMPOSE_ALARM_FAMILY, alarm_runs == [1], alarm_runs)
OW.run(now=t0 + 180, rules=rules, families=["flow"])
st = json.loads((_TMP / "ops" / "status.json").read_text())
check("a limited pass without --compose still writes no verdict", "health.state" not in st["points"])

late = t0 + 120 + OW.COMPOSE_MAX_AGE_S + 60
OW.run(now=late, rules=rules, families=["accounts"], compose=True)
st = json.loads((_TMP / "ops" / "status.json").read_text())
check("compose: a family older than the round robin allows reads UNMEASURED",
      st["points"]["disk.stub"]["m"] == "UNMEASURED" and st["points"]["disk._collector"]["m"] == "UNMEASURED",
      st["points"].get("disk.stub"))
check("compose: a family measured recently enough still carries", st["points"]["flow.stub"]["m"] == "MEASURED",
      st["points"]["flow.stub"])
check("carry_family: no record reads UNMEASURED", OW.carry_family("x", [], late, 60)["x._collector"]["m"] == "UNMEASURED")
check("carry_family: a future record is not carried",
      OW.carry_family("x", [{"t": late + 3600, "at": "z", "points": {"x.a": OW.M(1)}}], late, 60)["x._collector"]["m"]
      == "UNMEASURED")

# --- the health verdict: made by the alarm pass, carried by the others, aged from the pass that made it ---------------
_ph = OW.publish_health
made = []
OW.publish_health = lambda points, prev, ctx, rules, now: (made.append(now), {"health.state": OW.M("ok")})[1]
h0 = late + 1000
OW.run(now=h0, rules=rules, families=["flow"], compose=True)
OW.run(now=h0 + 60, rules=rules, families=["accounts"], compose=True)
st = json.loads((_TMP / "ops" / "status.json").read_text())
check("health: the alarm pass makes the verdict, the next pass carries it", made == [h0], made)
check("health: the carried verdict says when it was made", st["points"]["health.state"]["x"]["observed_at"] == OW.iso(h0),
      st["points"]["health.state"])
for i in range(2, 40):      # pass after pass without the alarm family: the verdict ages out, never made without it
    OW.run(now=h0 + 60 * i, rules=rules, families=["accounts"], compose=True)
st = json.loads((_TMP / "ops" / "status.json").read_text())
check("health: past the round robin's age the verdict reads UNMEASURED, never made without the ledger",
      made == [h0] and st["points"]["health.state"]["m"] == "UNMEASURED", (made, st["points"]["health.state"]))
OW.publish_health = _ph

# --- review fixes: flow joins testing; a carried reading counts once in the alarms; honest freshness ---------------
calls.clear()
OW.run(now=h0 + 3000, rules=rules, families=["testing", "disk"], compose=True)
check("compose: testing brings flow (its ctx) into the pass", calls[:1] == ["flow"] and "testing" in calls, calls)
seen_pts = []
OW.run_alarms = lambda points, *a, **k: (seen_pts.append(set(points)), {})[1]
t1 = h0 + 3100
OW.run(now=t1, rules=rules, families=["disk", "timers"], compose=True)          # disk measured after the alarm pass
OW.run(now=t1 + 60, rules=rules, families=["flow"], compose=True)
OW.run(now=t1 + 120, rules=rules, families=["flow"], compose=True)
check("alarms: a reading observed since the last alarm pass is in it", "disk.stub" in seen_pts[0], sorted(seen_pts[0])[:8])
check("alarms: the same carried reading is held on the next alarm pass", "disk.stub" not in seen_pts[1]
      and "flow.stub" in seen_pts[1], sorted(seen_pts[1])[:8])
st = json.loads((_TMP / "ops" / "status.json").read_text())
check("status: names what it measured and as of when each family reads",
      st.get("measured") == ["flow"] and st["observed"].get("disk") == OW.iso(t1) and st.get("oldest_observed_at"),
      {k: st.get(k) for k in ("measured", "oldest_observed_at")})
lm = json.loads((_TMP / "ops" / "last_measured.json").read_text())["t"]
check("last_measured: a carried reading is not stamped as measured now", lm.get("disk.stub", 0) < t1 + 120
      and lm.get("flow.stub") == t1 + 120, (lm.get("disk.stub"), lm.get("flow.stub"), t1 + 120))
OW.run_alarms = lambda *a, **k: (alarm_runs.append(1), {})[1]

# --- the ownership fence ----------------------------------------------------------------------------------------------
before = (_TMP / "ops" / "status.json").read_text()
asked = []
try:
    OW.run(now=late + 60, rules=rules, families=["accounts"], compose=True,
           still_owner=lambda what: (asked.append(what), False)[1])
    check("fence: a fenced pass raises Fenced", False)
except OW.Fenced:
    check("fence: a fenced pass raises Fenced", True)
check("fence: it is asked before the series are written", asked and asked[0].startswith("writing"), asked)
check("fence: a fenced pass writes no status", (_TMP / "ops" / "status.json").read_text() == before)
asked.clear()
OW.run(now=late + 120, rules=rules, families=["flow"], compose=True, still_owner=lambda what: (asked.append(what), True)[1])
check("fence: asked before the series, the alarms and the status",
      any(a.startswith("writing") for a in asked) and "the alarms" in asked and "the status" in asked, asked)

_owner = metronome.owner_of
metronome.owner_of = lambda timer, table_path=None: "sense" if timer == OW.OLD_TIMER else None
calls.clear()
rc = OW.main(["run", "--file-alarms"])
check("an owned clock: --file-alarms without --metronome-gen does nothing", rc == 0 and calls == [], (rc, calls))
mdir = _TMP / "metronome"
mdir.mkdir()
os.environ["METRONOME_DIR"] = str(mdir)
calls.clear()
rc = OW.main(["run", "--compose", "--family", "accounts", "--metronome-gen", "999"])
check("a stale generation refuses with EXIT_FENCED and measures nothing", rc == OW.EXIT_FENCED and calls == [], (rc, calls))
metronome.owner_of = _owner
OW.run_alarms = _real_alarms

print("selftest_ops_watch_compose: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
