#!/usr/bin/env python3
"""Selftest for RIMMANDRAKE_READ_FABLE_WEEKLY_METER_USAGE_LINE_NEVER_SHOWED: every per-model weekly limit /usage
shows ("Current week (Fable)") is printed as LEFT on each account's status line, and a run of that model sees the
LOWER of the all-models and the model's own limit, in account_usage.week_left_for, the ops_watch points, the launch
reading (role_launch.ops_reading), the slot allocator's gather and the switching plan's levelled meter.

The owner's 2026-11-18 5:10 PM PST panel for steven: all models 39% used, Fable 60% used -> 61% left and 40% left.
Fixture files only; no network, no claude, no credentials."""
import atexit
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(tempfile.mkdtemp(prefix="st_model_weeks_"))
atexit.register(shutil.rmtree, ROOT, True)
os.environ["RM_ACCOUNTS_DIR"] = str(ROOT / "acc")
os.environ["RM_ACCOUNT_USAGE_DIR"] = str(ROOT / "data")
os.environ["RM_ACCOUNT_USAGE_CONF"] = str(ROOT / "conf.json")
os.environ["RM_LIVE_CLAUDE_JSON"] = str(ROOT / "live.claude.json")
os.environ["RM_PULSE_STATE"] = str(ROOT / "pulse")
os.environ["RM_CLAUDE_ACCOUNT"] = str(ROOT / "no-such-claude-account")
os.environ["RM_SLOT_MACHINE"] = "testhost"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
import account_usage as au  # noqa: E402

FAILS = []
NOW = 1795050000.0  # 2026-11-18 17:00 PST (2026-11-19T01:00Z)


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)


TEXT = ("Current session: 5% used · resets Nov 18, 9pm (America/Los_Angeles)\n"
        "Current week (all models): 39% used · resets Nov 25, 2pm (America/Los_Angeles)\n"
        "Current week (Fable): 60% used · resets Nov 25, 2pm (America/Los_Angeles)\n")


def rec(name, text, machine="testhost"):
    fig = au.parse_usage(text, NOW)
    r = au.record(name, NOW, "MEASURED", "live login", machine, fig, measured_at=au.iso(NOW))
    return r


# ---------------------------------------------------------------- account_usage: the reading and the status line
r = rec("steven", TEXT)
d = au.derive_record(r, NOW)
check("all-models figure is 61% left", d.get("week_pct_left") == 61.0, d.get("week_pct_left"))
mw = d.get("model_weeks") or {}
check("Fable limit is read as 40% left", (mw.get("Fable") or {}).get("pct_left") == 40.0, mw)
line = au._fmt(d)
check("status line shows the all-models figure as 61% left", "61% left" in line, line)
check("status line shows the Fable limit as 40% left", "Fable week 40% left" in line, line)
check("status line never shows a figure as used", " used" not in line, line)

check("a Fable launch sees 40% (alias)", au.week_left_for(d, "fable")[:2] == (40.0, "Fable"), au.week_left_for(d, "fable"))
check("a Fable launch sees 40% (full id)", au.week_left_for(d, "claude-fable-5-2")[0] == 40.0)
check("an Opus launch sees the all-models 61%", au.week_left_for(d, "opus")[:2] == (61.0, "all models"))
check("no model reads the all-models 61%", au.week_left_for(d, None)[:2] == (61.0, "all models"))

# input kinds: no per-model line; per-model higher than all-models; the model window reset since; all-models unknown
d0 = au.derive_record(rec("lukas", "Current week (all models): 20% used · resets Nov 25, 3pm (America/Los_Angeles)\n"), NOW)
check("no per-model line: model_weeks is empty, not absent", d0.get("model_weeks") == {}, d0.get("model_weeks"))
check("no per-model line: a Fable launch reads all-models", au.week_left_for(d0, "fable")[:2] == (80.0, "all models"))
check("no per-model line: the status line has no model part", "Fable" not in au._fmt(d0), au._fmt(d0))
dh = au.derive_record(rec("system", "Current week (all models): 70% used · resets Nov 25, 12pm (America/Los_Angeles)\n"
                                    "Current week (Fable): 10% used · resets Nov 25, 12pm (America/Los_Angeles)\n"), NOW)
check("model limit higher than all-models: the lower (all-models) wins", au.week_left_for(dh, "fable")[:2] == (30.0, "all models"))
gone = dict(r, other_weeks={"Fable": {"pct_used": 60.0, "resets_at": au.iso(NOW - 60)}})
dg = au.derive_record(gone, NOW)
check("model window reset since the reading: pct_left is unknown (None), never 0 or 100",
      dg["model_weeks"]["Fable"]["pct_left"] is None, dg["model_weeks"])
check("model window reset since: a Fable launch reads all-models", au.week_left_for(dg, "fable")[:2] == (61.0, "all models"))
check("model window reset since: the line says unknown", "Fable week ?" in au._fmt(dg), au._fmt(dg))
du = dict(d, week_pct_left=None)
check("all-models unknown: the level is unknown (None), not the model's figure", au.week_left_for(du, "fable")[0] is None)
check("scope match is by word: 'opusplan' is not Fable", au.scope_for("opusplan", ["Fable"]) is None)
check("scope match: an empty model matches nothing", au.scope_for("", ["Fable"]) is None)

# a RimPulse endpoint reading (all-models only) replacing a /usage reading keeps the Fable limit, marked carried
cw = au.carry_model_weeks(r, NOW + 600)
check("RimPulse fallback: the Fable limit is carried, stamped with when it was read",
      cw.get("Fable", {}).get("pct_used") == 60.0 and cw["Fable"].get("carried_from") == r["measured_at"], cw)
check("RimPulse fallback: a reset model window is dropped, never carried", au.carry_model_weeks(gone, NOW) == {})
check("RimPulse fallback: nothing to carry from an UNMEASURED reading is empty", au.carry_model_weeks({"source": "UNMEASURED"}, NOW) == {})
dc = au.derive_record(dict(r, other_weeks=cw), NOW + 600)
check("RimPulse fallback: the status line says the carried figure's reading time", "(read " in au._fmt(dc), au._fmt(dc))
os.environ["RM_PULSE_STATE"] = str(ROOT / "pulse")
(ROOT / "pulse").mkdir(exist_ok=True)
(ROOT / "pulse" / "usage.json").write_text(json.dumps({"accounts": {"steven": {
    "measured_at": NOW + 500, "week": {"pct": 41.0, "resets_at": NOW + 6 * 86400}, "five": {}}}}))
au.PULSE_USAGE = ROOT / "pulse" / "usage.json"
(ROOT / "acc").mkdir(exist_ok=True)
(ROOT / "acc" / "accounts.tsv").write_text("steven steven@example.invalid\n")
au.write({"steven": r}, NOW)
au.probe_local = lambda *a, **k: (None, "test: no live login")
au.config = lambda: {"remotes": []}
au.vault_token_valid_until = lambda name: None
got = au.poll(NOW + 600)
check("poll via RimPulse keeps steven's Fable limit (carried)",
      (got["steven"].get("other_weeks") or {}).get("Fable", {}).get("carried_from") == r["measured_at"],
      {k: got["steven"].get(k) for k in ("method", "other_weeks")})

# ---------------------------------------------------------------- the file every consumer reads
au.write({"steven": r, "lukas": rec("lukas", "Current week (all models): 0% used · resets Nov 25, 3pm (America/Los_Angeles)\n"
                                             "Current week (Fable): 0% used · resets Nov 25, 3pm (America/Los_Angeles)\n")}, NOW)
st = au.read_now(NOW)
check("read_now (the --json reader) carries model_weeks as LEFT",
      st["accounts"]["steven"]["model_weeks"]["Fable"]["pct_left"] == 40.0, st["accounts"]["steven"].get("model_weeks"))

# ---------------------------------------------------------------- ops_watch points and the launch reading
import ops_watch as OW  # noqa: E402
pts = OW.c_accounts(NOW, {"accounts_fit": None}, {})
p = pts.get("accounts.steven.model_week_left_pct.Fable") or {}
check("ops_watch emits the Fable limit as a point, 40% left", p.get("v") == 40.0 and p.get("m") == "MEASURED", p)
check("ops_watch keeps the all-models point at 61%", (pts.get("accounts.steven.week_left_pct") or {}).get("v") == 61.0)
import role_launch as RL  # noqa: E402
status = {"at": __import__("datetime").datetime.fromtimestamp(NOW, __import__("datetime").timezone.utc)
          .strftime("%Y-%m-%dT%H:%M:%SZ"), "points": pts}
rf = RL.ops_reading(status, "steven", NOW, model="fable")
check("a Fable role launch reads week_left 40 (its Fable limit)",
      rf.get("state") == "MEASURED" and rf.get("week_left") == 40.0 and rf.get("week_limit") == "Fable", rf)
ro = RL.ops_reading(status, "steven", NOW, model="sonnet")
check("a Sonnet role launch reads the all-models 61", ro.get("week_left") == 61.0 and ro.get("week_limit") == "all models", ro)
rn = RL.ops_reading(status, "steven", NOW)
check("no model: the launch reading is unchanged (61)", rn.get("week_left") == 61.0, rn)

# ---------------------------------------------------------------- the slot allocator and the switching plan
import account_live as AL  # noqa: E402
os.environ["RM_CLAUDE_ACCOUNT"] = AL.fake_switcher(ROOT, "steven")  # account_usage already holds its no-such path
import slot_allocator as SA  # noqa: E402
gf = SA.gather(NOW, model="fable")
check("allocator for a Fable run: the level is 40% of its Fable limit",
      gf.get("week_pct_left") == 40.0 and gf.get("week_limit") == "Fable", {k: gf.get(k) for k in ("week_pct_left", "week_limit", "account")})
check("allocator carries every per-model limit as LEFT", gf.get("model_weeks_left") == {"Fable": 40.0}, gf.get("model_weeks_left"))
ga = SA.gather(NOW)
check("allocator with no model: all-models 61%, unchanged", ga.get("week_pct_left") == 61.0 and ga.get("week_limit") == "all models")
import switching_plan as SP  # noqa: E402
lv = SP.levelled(st["accounts"], "fable")
check("switching plan, a Fable run: steven's level is 40", lv["steven"]["week_pct_left"] == 40.0 and lv["steven"]["week_limit"] == "Fable")
check("switching plan, a Fable run: lukas stays 100 (its Fable limit is not lower)", lv["lukas"]["week_pct_left"] == 100.0)
l0 = SP.levelled(st["accounts"], None)
check("switching plan, no level_model: every figure unchanged", l0["steven"]["week_pct_left"] == 61.0)
check("switching plan: levelled never mutates the meter it was given", st["accounts"]["steven"]["week_pct_left"] == 61.0)

print(f"\n{'ALL PASS' if not FAILS else 'FAILED: ' + ', '.join(FAILS)}")
sys.exit(1 if FAILS else 0)
