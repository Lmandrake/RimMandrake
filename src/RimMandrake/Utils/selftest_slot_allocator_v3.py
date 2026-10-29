#!/usr/bin/env python3
"""selftest for slot_allocator.py's v3 split (HELPER_BUDGET_MIGRATE_INTO_DISPATCHER).

v3 has no BENCH seat (design/RimMandrake/rimflow_v3_2026-10-26.md §2): FOUNDRY, the one autonomous builder, gets the
machine's whole helper budget (the pace fit, unchanged); the Conductor (the owner's window, the allocator's internal
key "BENCH") gets helpers only while he is present, and every helper-hour it runs is owed and paid back from FOUNDRY
after he leaves (his rule in slot_rules.json presence._doc). His word (the override) still stands over both.

    python3 src/RimMandrake/Utils/selftest_slot_allocator_v3.py
"""
import copy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import slot_allocator as SA  # noqa: E402

FAILS = []
H = 3600.0
NOW = 1793050000.0


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  {detail}"))
    if not cond:
        FAILS.append(name)


def inp(**kw):
    base = {"seat": "BENCH", "account": "system", "source": "MEASURED", "week_pct_left": 40.0, "week_pct_used": 60.0,
            "hours_to_week_reset": 48.0, "week_resets_at": "2026-10-28T13:00-07:00", "session_pct_used": 18.0,
            "A1": 80, "D1": 32, "owner_window_min": None, "owner_card_min": None, "helpers_running": 2,
            "rate_pct_per_h": None, "mean_helpers": None, "override": None, "spare": []}
    base.update(kw)
    return base


R = copy.deepcopy(SA.load_rules())
R["split"] = {"rule": "v3", "conductor_session_n": 3}


def d(state=None, rules=None, **kw):
    w = kw.get("owner_window_min")
    kw.setdefault("owner_window_t", None if w is None else NOW - w * 60)   # by default his last message was in BENCH
    return SA.decide(inp(**kw), state or {}, rules or R, NOW)


def seats(r):
    return r["seats"]["BENCH"], r["seats"]["FOUNDRY"]


def ov(**kw):
    o = {"ownerSaid": "You may use up to 6 subagents currently", "until": SA.iso_local(NOW + 100 * H),
         "set_at": SA.iso_local(NOW - H), "mode": None}
    o.update(kw)
    return o


# ---- the live rules file is v3
live = SA.load_rules()
check("slot_rules.json ships the v3 split (no 25% share)", (live.get("split") or {}).get("rule") == "v3"
      and "FOUNDRY_share" not in (live.get("split") or {}), live.get("split"))
check("slot_rules.json sets the Conductor's session n", isinstance((live.get("split") or {}).get("conductor_session_n"), int),
      live.get("split"))

# ---- absent: the whole machine budget is FOUNDRY's
r = d(owner_window_min=300.0)
check("absent, CRUISE step 6 total -> CONDUCTOR 0, FOUNDRY 6", seats(r) == (0, 6) and r["n_total"] == 6, (r["seats"], r["why"]))
check("why says the Conductor is session-only", "session-only" in r["why"], r["why"])
check("why no longer speaks of a 25% share", "25%" not in r["why"], r["why"])
r = d(owner_window_min=300.0, rate_pct_per_h=1.2, mean_helpers=6.0)
check("absent, 13:05 baseline fit 4 -> FOUNDRY gets all 4 (v2 gave it 1)", seats(r) == (0, 4), (r["seats"], r["why"]))

# ---- present: Conductor session helpers on top, capped by the fit
r = d(owner_window_min=2.0)
check("present (he wrote 2 min ago), total 6 -> CONDUCTOR 3 (session n), FOUNDRY 6", seats(r) == (3, 6), (r["seats"], r["why"]))
r = d(owner_window_min=2.0, rate_pct_per_h=1.2, mean_helpers=6.0, week_pct_left=10.0, hours_to_week_reset=48.0)
tot = r["seats"]["FOUNDRY"]
check("present, a small fit -> CONDUCTOR never above the fit total", r["seats"]["BENCH"] == min(3, tot), (r["seats"], r["why"]))
r = d(owner_window_min=45.0, owner_card_min=5.0)
check("PHONE (window 45 min ago, card 5 min ago) is not a session -> CONDUCTOR 0", r["seats"]["BENCH"] == 0, (r["seats"], r["presence"]))
r = d(owner_window_min=2.0, week_pct_used=99.0, week_pct_left=1.0)
check("DARK -> nobody gets helpers, present or not", seats(r) == (0, 0), (r["seats"], r["token_mode"]))

# ---- his word
r = d(owner_window_min=300.0, override=ov(seats={"BENCH": 6}))
check("his word BENCH 6 while absent -> CONDUCTOR 6 (his word stands over session-only), FOUNDRY keeps 6", seats(r) == (6, 6), (r["seats"], r["why"]))
check("his words quoted in why", "up to 6 subagents" in r["why"], r["why"])
r = d(owner_window_min=300.0, override=ov(seats={"CONDUCTOR": 4}))
check("override keyed CONDUCTOR folds to the Conductor seat", seats(r) == (4, 6), r["seats"])
r = d(owner_window_min=300.0, override=ov(n=5))
check("override n (no seats) speaks for the Conductor", seats(r) == (5, 6), r["seats"])
r = d(owner_window_min=300.0, override=ov(seats={"FOUNDRY": 2}))
check("override FOUNDRY 2 -> FOUNDRY 2, CONDUCTOR still session-only 0", seats(r) == (0, 2), r["seats"])

# ---- review r2 (Codex 2026-10-28): the Conductor's session is HIS window, not any window
r = d(owner_window_min=2.0, owner_window_t=NOW - 5 * H)
check("r2#2 a message 2 min ago in FOUNDRY's window (Conductor window quiet 5 h) -> CONDUCTOR 0, FOUNDRY 6",
      seats(r) == (0, 6), (r["seats"], r["why"]))
r = d(owner_window_min=2.0, owner_window_t=None)
check("r2#2 no Conductor-window message at all -> CONDUCTOR 0", r["seats"]["BENCH"] == 0, r["seats"])

# ---- review r1 (Codex 2026-10-28)
r = d(owner_window_min=2.0)
check("r1#1 the remembered machine total is the fit (FOUNDRY 6), not FOUNDRY + the Conductor's session helpers (9)",
      r["state"]["total"] == 6, r["state"].get("total"))
r = d(owner_window_min=2.0, week_pct_used=99.0, week_pct_left=1.0, override=ov(mode="CRUISE"))
check("r1#3 his word lifting DARK to CRUISE while he is present gives the Conductor its session helpers too",
      r["seats"]["BENCH"] == 3 and r["seats"]["FOUNDRY"] == 6, (r["seats"], r["mode"]))

# ---- overage: the Conductor's helpers are owed, paid back from FOUNDRY after he leaves
r = d({"overage_t": NOW - H}, owner_window_min=2.0, helpers_running={"BENCH": 2, "FOUNDRY": 0},
      helper_spans=None)
check("present, CONDUCTOR ran 2 helpers for 1 h -> 2 helper-h owed (its base is 0)",
      abs(r["overage"]["owed_h"] - 2.0) < 1e-6 and r["state"]["overage_base"].get("BENCH") == 0, (r["overage"], r["state"].get("overage_base")))
r = d({"overage_t": NOW, "overage_h": 40.0, "overage_base": {"BENCH": 0, "FOUNDRY": 6}}, owner_window_min=300.0,
      helpers_running={"BENCH": 0, "FOUNDRY": 0}, helper_spans=None)
check("absent, 40 helper-h owed, 42 h window -> FOUNDRY lowered by 1, CONDUCTOR stays 0",
      seats(r) == (0, 5) and r["overage"]["cut"] == 1, (r["seats"], r["overage"]))

# ---- the legacy rule still works when named (rollback = set split.rule "share")
L = copy.deepcopy(R)
L["split"] = {"rule": "share", "FOUNDRY_share": 0.25}
r = d(rules=L)
check("legacy share rule: total 6 -> BENCH 5, FOUNDRY 1", seats(r) == (5, 1), r["seats"])

# ---- the published names
check("seat_label maps the allocator key to v3 names", SA.seat_label("BENCH") == "CONDUCTOR" and SA.seat_label("FOUNDRY") == "FOUNDRY")
check("seat_key maps v3 names and the old window name to the allocator key",
      SA.seat_key("CONDUCTOR") == "BENCH" and SA.seat_key("bench") == "BENCH" and SA.seat_key("FOUNDRY") == "FOUNDRY")

print(f"\n{'GREEN' if not FAILS else 'RED'}: {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
