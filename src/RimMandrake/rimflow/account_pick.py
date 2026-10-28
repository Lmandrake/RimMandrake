#!/usr/bin/env python3
"""account_pick.py — the Dispatcher picks the Claude account new work runs on BEFORE it releases the work (item
DISPATCHER_BUILD_PICK_ACCOUNT_FIRST; owner, 2026-10-27: "Dispatch should be able to recognize that the system should
switch to a new account before new work is released (when appropriate)").

A program, not a judgement: pick() applies the schedule's `account_pick` rule to the ops_watch reading
(status.json points accounts.<label>.runway / week_left_pct / hours_to_reset) and returns one of
  KEEP        the account this machine runs on (role_launch.resolve_account) stays: it is not under the rule's
              `switch_when` line, or no other account is fit to take the work (the throttle bands then pace it)
  SWITCH      it is under the line and another account meets `target_min`: the pick names that account. `act` is
              "recommend": the work listed under `hold` (role_launch / ring / recover) is HELD and an alarm says
              which account to switch to. Nothing here switches: a switch is `claude-account use` (one account per
              machine, it closes every Claude window, and the machine ships DISARMED) — the owner's or a seat's call.
  HOLD        the machine is ON a lent account that is off-limits or under `lent_min_draw_pct` and no other
              account is fit: nothing listed under `hold` is released (never burn an off-limits account). The
              dispatcher must alarm it (account_gate alarms SWITCH/UNMEASURED today: item filed).
  UNMEASURED  the machine's own account or its reading is unknown: KEEP it and alarm, never guess. A candidate whose
              points are not in `target_min.m` (MEASURED by default) is not a candidate. On a LENT account (the lent
              rules' set, or the last set read when the rules are unreadable now: `known_lent`) an UNMEASURED pick
              HOLDS (`hold` true) and is alarmed: an unmeasured lent account is never drawn on (review U N1). The
              rules unreadable with no set ever read: the machine's account cannot be told owned, so it holds too
              (fail closed). An unresolved machine account keeps (never guess).

Lent accounts (the owner's rule for an account that belongs to someone else: at most max_used_by_us_pct of his week
only in the first prefer_start_of_week_h after his reset, never under floor_pct_left, off-limits through a date) are DATA in `lent_rules`
(slot_rules.json `lent_accounts`, the one copy the slot allocator reads too) and are judged by the allocator's own
slot_allocator.lent_allowance, never a second copy of the rule. A lent account is a candidate only when no owned
account is (standing_rulings.md §Account and capacity budget: lent only after the owned ones are depleted) and its
allowance is at least `lent_min_draw_pct`; a lent account the machine is ON is switched away from when its
allowance falls under that line. The lent rules unreadable (or the allocator not importable) -> no account can be
told lent from owned, so no switch is recommended at all (fail closed) and that is alarmed.

Ranking among fit candidates: the OWNER'S FIXED PRIORITY, read from the file the switching plan reads (`order` in
src/RimMandrake/Utils/switching_plan.json, or the rule's `priority_plan`): one source of truth (item
ACCOUNTPICK_CORRECT_OWNER_PRIORITY; the owner's words of 2026-10-28 10:15 are quoted in that file's `_owner`). A lent
account in that order is ranked by it too: its lent allowance (his window after a reset, his cap, the floor) already decides whether it is fit
at all, and inside it the owner put it first. Accounts outside the order come after it, owned before lent, by the
schedule's `rank`: "soonest_reset" (the week that ends first) or "most_runway". The plan unreadable -> no switch is
recommended (UNMEASURED, alarmed: fail closed, never a guessed order). Names no account, host or model: labels come
from the reading, rules from data.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import role_launch as RL  # noqa: E402

HOLDABLE = ("role_launch", "ring", "recover")
RANKS = ("soonest_reset", "most_runway")
PRIORITY_PLAN = "src/RimMandrake/Utils/switching_plan.json"  # the switching plan's own rules: its `order` is the priority


def labels_in(status):
    """Every account label the ops_watch reading has a point for."""
    out = set()
    for k in ((status or {}).get("points") or {}):
        parts = k.split(".")
        if len(parts) == 3 and parts[0] == "accounts":
            out.add(parts[1])
    return sorted(out)


def hours_to_reset(status, label):
    p = ((status or {}).get("points") or {}).get("accounts.%s.hours_to_reset" % label) or {}
    if isinstance(p, dict) and p.get("m") in ("MEASURED", "ESTIMATE") and RL.finite(p.get("v")):
        return float(p["v"])
    return None


def lent_view(label, reading, h):
    """The record slot_allocator.lent_allowance reads (all of the week used counted as ours)."""
    return {"account": label, "pct_left": reading["week_left"], "pct_used": 100.0 - reading["week_left"],
            "hours_to_reset": h, "resets_at": None}


def load_lent(rule):
    """-> (slot rules dict | None when unreadable, lent_allowance | None when not importable)."""
    path = (rule or {}).get("lent_rules") or ""
    path = RL.wsl_path(path)
    if path and not os.path.isabs(path):
        path = os.path.join(REPO, path)
    try:
        with open(path, encoding="utf-8") as f:
            rules = json.load(f)
        if not isinstance(rules, dict) or not isinstance(rules.get("lent_accounts", {}), dict):
            rules = None
    except (OSError, ValueError, TypeError):
        rules = None
    utils = os.path.join(REPO, "src", "RimMandrake", "Utils")
    if utils not in sys.path:
        sys.path.append(utils)
    try:
        import slot_allocator
        fn = slot_allocator.lent_allowance
    except Exception:  # noqa: BLE001 - any import failure means the rule cannot be applied: fail closed
        fn = None
    return rules, fn


def load_priority(rule):
    """The owner's account priority: `order` of the switching plan (rule `priority_plan`, default PRIORITY_PLAN).
    -> list of labels, or None when unreadable or not a non-empty list of distinct strings."""
    path = RL.wsl_path((rule or {}).get("priority_plan") or PRIORITY_PLAN)
    if not os.path.isabs(path):
        path = os.path.join(REPO, path)
    try:
        with open(path, encoding="utf-8") as f:
            order = json.load(f).get("order")
    except (OSError, ValueError, TypeError, AttributeError):
        return None
    if (not isinstance(order, list) or not order or not all(isinstance(x, str) and x for x in order)
            or len(set(order)) != len(order)):
        return None
    return order


def lent_set(lent_rules, known_lent=None):
    """The lent account labels: the readable rules' set, else the last set read (`known_lent`), else None (unknown)."""
    if isinstance(lent_rules, dict):
        return set(lent_rules.get("lent_accounts") or {})
    return None if known_lent is None else set(known_lent)


def pick(rule, status, current, lent_rules, allowance, now, known_lent=None):
    """Pure. -> {"state", "account", "to", "hold", "why", "key", "candidates"}. known_lent: the lent labels last read
    (the caller's cache), used only while the lent rules are unreadable."""
    lents = lent_set(lent_rules, known_lent)

    def out(state, why, to=None, cands=()):
        # act "recommend" (the only one built): the work waits for the switch. HOLD: the machine is on a lent
        # account that is off-limits / under its draw line and nothing else is fit: never burn it, wait.
        # UNMEASURED on a lent account (or one that cannot be told owned) holds as well (review U N1).
        hold = state in ("SWITCH", "HOLD")
        if state == "UNMEASURED" and current and (lents is None or current in lents):
            hold = True
            why = "HELD (%s): %s" % ("lent account" if lents is not None else
                                     "no lent-account set was ever read, the account cannot be told owned", why)
        key = "%s%s %s%s" % (state, "/held" if state == "UNMEASURED" and hold else "", current or "?",
                             (" -> " + to) if to else "")
        return {"state": state, "account": current, "to": to, "hold": hold, "why": why, "key": key,
                "candidates": list(cands)}

    cur = RL.ops_reading(status, current, now, rule.get("ops_stale_s", RL.OPS_STALE_S))
    if cur["state"] != "MEASURED":
        return out("UNMEASURED", "keep the current account, its reading is UNMEASURED: %s" % cur["why"])
    if lent_rules is None or allowance is None:
        return out("UNMEASURED", "keep %s: the lent-account rules (%s) are %s, so no account can be told lent from "
                   "owned and no switch is recommended" % (current, rule.get("lent_rules"),
                                                           "unreadable" if lent_rules is None
                                                           else "not applicable (slot_allocator not importable)"))
    lent = lent_rules.get("lent_accounts") or {}
    sw = rule.get("switch_when") or {}
    tgt = rule.get("target_min") or {}
    min_draw = rule.get("lent_min_draw_pct", 0)
    under = []
    if "runway_lt" in sw and cur["runway"] < sw["runway_lt"]:
        under.append("runway %.2f %s < %s" % (cur["runway"], cur["runway_m"], sw["runway_lt"]))
    if "week_left_pct_lt" in sw and cur["week_left"] < sw["week_left_pct_lt"]:
        under.append("week left %.0f%% < %s%%" % (cur["week_left"], sw["week_left_pct_lt"]))
    if current in lent:
        cap, cwhy = allowance(lent_view(current, cur, hours_to_reset(status, current)), lent_rules, now)
        if cap is None or cap <= 0 or cap < min_draw:  # 0 is off-limits whatever the line says
            under.append("lent account allowance %s%% < %s%% (%s)" % (
                "?" if cap is None else "%.0f" % cap, min_draw, cwhy))
    here = "%s: runway %.2f %s, week left %.0f%%" % (current, cur["runway"], cur["runway_m"], cur["week_left"])
    if not under:
        return out("KEEP", "keep %s (not under the switch line)" % here)
    owned, lent_ok, refused = [], [], []
    for label in labels_in(status):
        if label == current:
            continue
        r = RL.ops_reading(status, label, now, rule.get("ops_stale_s", RL.OPS_STALE_S))
        if r["state"] != "MEASURED":
            refused.append("%s unmeasured" % label)
            continue
        if r["runway_m"] not in tgt.get("m", ["MEASURED"]) or r["week_left_m"] not in tgt.get("m", ["MEASURED"]):
            refused.append("%s %s/%s, not %s" % (label, r["runway_m"], r["week_left_m"], "/".join(
                tgt.get("m", ["MEASURED"]))))
            continue
        if r["runway"] < tgt.get("runway_ge", 0) or r["week_left"] < tgt.get("week_left_pct_ge", 0):
            refused.append("%s runway %.2f, week left %.0f%%: under target" % (label, r["runway"], r["week_left"]))
            continue
        h = hours_to_reset(status, label)
        c = {"account": label, "runway": r["runway"], "week_left": r["week_left"], "hours_to_reset": h}
        if label in lent:
            cap, lwhy = allowance(lent_view(label, r, h), lent_rules, now)
            if cap is None or cap <= 0 or cap < min_draw:
                refused.append("%s lent, allowance %s%% < %s%% (%s)" % (
                    label, "?" if cap is None else "%.0f" % cap, min_draw, lwhy))
                continue
            c["lent_allowance_pct"] = round(cap, 1)
            lent_ok.append(c)
        else:
            owned.append(c)
    rank = rule.get("rank", "soonest_reset")
    if rank not in RANKS:
        return out("UNMEASURED", "keep %s: rank %r is not one of %s" % (current, rank, ", ".join(RANKS)))

    prio = load_priority(rule)
    if prio is None and (owned or lent_ok):
        return out("UNMEASURED", "keep %s although under the switch line (%s): the owner's account priority (%s "
                   "`order`) is unreadable, so no switch is recommended" % (
                       here, ", ".join(under), rule.get("priority_plan") or PRIORITY_PLAN))
    prio = prio or []

    def order(c):
        a = c["account"]
        if a in prio:  # the owner's order decides, lent or owned
            return (prio.index(a), 0, 0.0, a)
        tie = -c["runway"] if rank == "most_runway" else (
            c["hours_to_reset"] if c["hours_to_reset"] is not None else float("inf"))
        return (len(prio), 1 if "lent_allowance_pct" in c else 0, tie, a)

    pool = sorted(owned + lent_ok, key=order)
    tail = ("; not fit: " + "; ".join(refused)) if refused else ""
    lent_blocked = current in lent and any(u.startswith("lent account allowance") for u in under)
    if not pool and lent_blocked:
        return out("HOLD", "hold: %s is a lent account under its limit (%s) and no other account is fit, so no work "
                   "is released on it%s" % (here, ", ".join(under), tail))
    if not pool:
        return out("KEEP", "keep %s although under the switch line (%s): no other account is fit%s" % (
            here, ", ".join(under), tail))
    best = pool[0]
    return out("SWITCH", "switch from %s (%s) to %s: runway %.2f, week left %.0f%%%s%s, by %s%s" % (
        here, ", ".join(under), best["account"], best["runway"], best["week_left"],
        (", resets in %.0f h" % best["hours_to_reset"]) if best["hours_to_reset"] is not None else "",
        (", lent: may draw %.0f%%" % best["lent_allowance_pct"]) if "lent_allowance_pct" in best else "",
        "the owner's priority (%s)" % " > ".join(prio) if best["account"] in prio else "rank " + rank, tail),
        to=best["account"], cands=pool)


def validate(rule):
    """-> list of problems with the schedule's account_pick block (empty when usable)."""
    bad = []
    if rule.get("act", "recommend") != "recommend":
        bad.append("act %r: only 'recommend' is built (a switch closes every window: the owner's call)"
                   % rule.get("act"))
    for h in rule.get("hold") or []:
        if h not in HOLDABLE:
            bad.append("hold %r is not one of %s" % (h, ", ".join(HOLDABLE)))
    if rule.get("rank", "soonest_reset") not in RANKS:
        bad.append("rank %r is not one of %s" % (rule.get("rank"), ", ".join(RANKS)))
    if not (rule.get("switch_when") or {}):
        bad.append("no switch_when line")
    return bad
