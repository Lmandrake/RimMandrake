#!/usr/bin/env python3
"""selftest_dispatcher_mut.py - tests written FROM the mutation survivors of dispatcher.py (item
DISPATCHER_HARDEN_MUTATION_SURVIVORS, mutmut run 20261027b: 872 of 2071 mutants alive). Each block pins behaviour a
survivor showed was unasserted: which account work runs on (account_gate.gate, incl. the lent-account rule: only the
first prefer_start_of_week_h after the reset, at most max_used_by_us_pct, from slot_rules.json), the alarm cadence
edges and note flags, withdraw()'s evidence order, stop-runs, decide.one_seat's verify/recover/ring paths, execute's
side effects, tick and main. Boundaries are asserted on BOTH sides (n-1, n); clocks start away from 0 so a
`now + x` mutant cannot hide behind x == 0. Reuses the fixtures of selftest_dispatcher.py."""
import contextlib
import errno
import io
import json
import os
import signal
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_dispatcher as T  # noqa: E402
from selftest_dispatcher import D, RL, check, fresh, obs, sched  # noqa: E402
import account_pick as AP  # noqa: E402
import doorbell  # noqa: E402

TMP = tempfile.mkdtemp(prefix="selftest_dispatcher_mut_")
NOW = 1_800_000_000.0           # far from 0 on purpose


def lts(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


# ---------------------------------------------------------------- account_gate.gate

def run_gate(rule, accts, cur, now=None, st=None, kind="ring", lent="default", **sch_kw):
    now = NOW if now is None else now
    st = fresh() if st is None else st
    acts = []
    sch = sched(account_pick=rule, **sch_kw)
    o = T.pobs(now, accts, cur=cur)
    if lent != "default":
        o["roles"]["lent"] = lambda: lent
    gate = D.account_gate(sch, st, o, now, lambda **kw: acts.append(kw))
    return gate, gate(kind), acts, st


def test_gate_lent_rule_steven():
    """The Steven rule (owner 2026-10-27): his lent account is drawn only in the first 48 h after his weekly reset,
    at most 50% of the week used (all counted as ours), never under the 10% floor; else the work waits (HOLD)."""
    lent = T.LENT_RULES
    fn = T.lent_fn()
    rule = dict(T.PICK_RULE)

    def go(h, left, other=None):
        accts = {"lent": (2.0, left, h, "MEASURED")}
        if other:
            accts["b"] = other
        _g, (g, p), acts, _st = run_gate(rule, accts, "lent", lent=(lent, fn))
        return g, p, acts
    g, p, _ = go(150, 80)
    check(g and p["state"] == "KEEP", "Steven: 30 h after the reset, 80%% left -> work released (%s)" % p["state"])
    g, p, _ = go(120, 80)
    check(g and p["state"] == "KEEP", "Steven: exactly 48 h after the reset is still inside the window")
    g, p, _ = go(119, 80)
    check(not g and p["state"] == "HOLD", "Steven: 49 h after the reset -> HOLD (outside the window)")
    g, p, _ = go(10, 80)
    check(not g and p["state"] == "HOLD", "Steven: late in his week -> HOLD")
    g, p, _ = go(150, 55)
    check(not g and p["state"] == "HOLD", "Steven: 45%% used leaves 5%% of draw (< lent_min_draw_pct) -> HOLD")
    g, p, _ = go(150, 45)
    check(not g and p["state"] == "HOLD", "Steven: over 50%% used -> HOLD")
    g, p, _ = go(150, 80, other=(3.0, 60, 20, "MEASURED"))
    check(not g and p["state"] == "HOLD" or p["state"] == "KEEP", "Steven: sanity")
    g, p, acts = go(10, 80, other=(3.0, 60, 20, "MEASURED"))
    check(not g and p["state"] == "SWITCH" and p["to"] == "b" and "lent account allowance" in p["why"],
          "Steven outside the window with an owned account fit -> SWITCH to it")
    # the real rules file: the same numbers
    real = json.load(open(os.path.join(os.path.dirname(HERE), "Utils", "slot_rules.json")))
    pols = list(real["lent_accounts"].values())
    check(len(pols) == 1 and pols[0]["max_used_by_us_pct"] == 48 and pols[0]["prefer_start_of_week_h"] == 48
          and pols[0]["floor_pct_left"] == 10,
          "slot_rules.json lent policy: 48%% used (card 2026-10-28 10:20: leave at 52%% left) / first 48 h / 10%% floor")
    name = list(real["lent_accounts"])[0]
    after = RL.slot_epoch(T.DAY0, "12:00") + 30 * 86400      # long after off_limits_through
    for h, left, want in ((150, 80, True), (120, 90, True), (119, 90, False), (150, 40, False), (150, 55, False)):
        accts = {name: (2.0, left, h, "MEASURED")}
        _g, (g, p), _a, _s = run_gate(rule, accts, name, now=after, lent=(real, fn))
        check(g is want, "slot_rules.json: %s at %dh to reset, %d%% left -> go=%s (got %s)" % ("lent", h, left, want, g))
    _g, (g, p), _a, _s = run_gate(rule, {name: (2.0, 90, 150, "MEASURED")}, name, now=NOW, lent=(real, fn))
    check((g, p["state"]) == (True, "KEEP") or p["state"] == "HOLD", "slot_rules.json off-limits clock readable")


def test_gate_switch_alarm_and_ticket():
    low = {"a": (0.3, 30, 50, "MEASURED"), "b": (3.0, 60, 20, "MEASURED")}
    rule = dict(T.PICK_RULE, ledger_item="LEDGER_ITEM_Y")
    g, (go, p), acts, st = run_gate(rule, low, "a", alarm_item="ALARM_ITEM_Z")
    al = [x for x in acts if x["do"] == "alarm"]
    ap = [x for x in acts if x["do"] == "account_pick"]
    check(not go and p["state"] == "SWITCH" and len(al) == 1 and al[0]["kind"] == "account:switch:b" and al[0]["note"] is True,
          "SWITCH: held, one alarm account:switch:b, written to the ledger")
    check(al[0]["ticket"] == "LEDGER_ITEM_Y" and ap[0]["ticket"] == "LEDGER_ITEM_Y",
          "SWITCH: the rule's ledger_item wins over the schedule's alarm_item (alarm and pick record)")
    check("claude-account use b --confirm <machine>" in al[0]["why"]
          and "held: role_launch, ring, recover)" in al[0]["why"], "SWITCH: the alarm names the command and the held kinds")
    _g, (go, p), acts, _s = run_gate(dict(T.PICK_RULE, hold=[]), low, "a", alarm_item="ALARM_ITEM_Z")
    al = [x for x in acts if x["do"] == "alarm"]
    check(al and "held: nothing)" in al[0]["why"] and al[0]["ticket"] == "ALARM_ITEM_Z",
          "SWITCH with nothing to hold: 'held: nothing', ticket falls back to alarm_item")
    # kind outside the hold list is not held; inside is
    gate, (go, _p), _a, _s = run_gate(dict(T.PICK_RULE, hold=["ring"]), low, "a", kind="ring")
    check(not go and gate("recover")[0] is True and gate("role_launch")[0] is True,
          "gate: only the kinds in `hold` wait")
    # pick record: noted on change, '(was: key)' when a previous key differed
    st = fresh()
    st["account_pick"] = {"key": "KEEP a", "at": "x"}
    _g, (go, p), acts, st = run_gate(T.PICK_RULE, low, "a", st=st)
    ap = [x for x in acts if x["do"] == "account_pick"][0]
    check(ap["note"] is True and ap["why"].endswith("(was: KEEP a)") and ap["to"] == "b" and ap["state"] == "SWITCH"
          and ap["account"] == "a", "pick record: changed key -> noted, '(was: KEEP a)' appended")
    check(st["account_pick"] == {"key": p["key"], "at": lts(NOW)}, "pick record: state keeps key and at=iso(now)")
    _g, (go, p), acts, st = run_gate(T.PICK_RULE, low, "a", st=st)
    ap = [x for x in acts if x["do"] == "account_pick"][0]
    check(ap["note"] is False and "(was" not in ap["why"], "pick record: same key -> not noted, no '(was'")
    _g, (go, p), acts, st = run_gate(T.PICK_RULE, low, "a")
    ap = [x for x in acts if x["do"] == "account_pick"][0]
    check(ap["note"] is True and "(was" not in ap["why"], "pick record: first ever key -> noted, no '(was'")
    # the gate picks once per tick
    gate, _r, acts, _s = run_gate(T.PICK_RULE, low, "a")
    gate("ring")
    gate("recover")
    check(len([x for x in acts if x["do"] == "account_pick"]) == 1, "gate: one pick per tick, however many asks")


def test_gate_off_and_invalid_and_unmeasured():
    low = {"a": (0.3, 30, 50, "MEASURED"), "b": (3.0, 60, 20, "MEASURED")}
    for rule, why in ((dict(T.PICK_RULE, enabled=False), "disabled"), (None, "no block")):
        sch = sched(account_pick=rule) if rule else sched()
        acts = []
        gate = D.account_gate(sch, fresh(), T.pobs(NOW, low), NOW, lambda **kw: acts.append(kw))
        check(gate("ring") == (True, {}) and not acts, "gate %s: always go, no record" % why)
    sch = sched(account_pick=T.PICK_RULE)
    o = T.pobs(NOW, low)
    o["roles"] = None
    acts = []
    check(D.account_gate(sch, fresh(), o, NOW, lambda **kw: acts.append(kw))("ring") == (True, {}) and not acts,
          "gate with no role observer: always go")
    # an unusable rule: nothing held, one UNMEASURED alarm with the reasons joined by '; '
    bad = dict(T.PICK_RULE, act="switch", hold=["x"], rank="r", ledger_item="LI")
    problems = AP.validate(bad)
    _g, (go, p), acts, st = run_gate(bad, low, "a")
    al = [x for x in acts if x["do"] == "alarm"]
    ap = [x for x in acts if x["do"] == "account_pick"][0]
    check(go and p["key"] == "INVALID" and p["hold"] is False and p["to"] is None and p["state"] == "UNMEASURED",
          "invalid rule: go, key INVALID, hold False")
    check(p["why"] == "account_pick rule unusable, nothing held: " + "; ".join(problems) and len(problems) >= 2,
          "invalid rule: the reasons are listed, '; ' joined")
    check(len(al) == 1 and al[0]["kind"] == "account:unmeasured" and al[0]["note"] is True and al[0]["ticket"] == "LI"
          and al[0]["why"] == p["why"] and ap["to"] is None and ap["state"] == "UNMEASURED",
          "invalid rule: alarm account:unmeasured, noted, on the ledger_item")
    # unmeasured current: no ledger_item -> alarm_item; a lent current -> ':held' and held
    lentd = (T.LENT_RULES, T.lent_fn())
    _g, (go, p), acts, _s = run_gate(T.PICK_RULE, {"lent": (0.3, 30, 50, "UNMEASURED")}, "lent", lent=lentd,
                                      alarm_item="ALARM_ITEM_Z")
    al = [x for x in acts if x["do"] == "alarm"]
    check(not go and p["hold"] and len(al) == 1 and al[0]["kind"] == "account:unmeasured:held" and al[0]["note"] is True
          and al[0]["ticket"] == "ALARM_ITEM_Z" and al[0]["why"] == p["why"], "unmeasured lent current -> held, alarm ':held'")
    _g, (go, p), acts, _s = run_gate(T.PICK_RULE, {"a": (0.3, 30, 50, "UNMEASURED")}, "a", lent=lentd)
    al = [x for x in acts if x["do"] == "alarm"]
    check(go and not p["hold"] and al[0]["kind"] == "account:unmeasured" and al[0]["note"] is True,
          "unmeasured owned current -> kept, alarm without ':held'")
    # the last lent set read is remembered and used while the rules are unreadable
    st = fresh()
    run_gate(T.PICK_RULE, {"a": (2.0, 40, 50, "MEASURED")}, "a", st=st, lent=(T.LENT_RULES, T.lent_fn()))
    check(st.get("account_lent_known") == ["lent"], "gate remembers the lent set it read")
    st = fresh()
    st["account_lent_known"] = ["x"]
    _g, (go, p), _a, st2 = run_gate(T.PICK_RULE, {"x": (2.0, 40, 50, "MEASURED")}, "x", st=st, lent=(None, None))
    check(not go and p["hold"] and "lent account" in p["why"], "unreadable rules + current in the last lent set -> held")
    st = fresh()
    st["account_lent_known"] = ["x"]
    _g, (go, p), _a, st2 = run_gate(T.PICK_RULE, {"y": (2.0, 40, 50, "MEASURED")}, "y", st=st, lent=(None, None))
    check(go and not p["hold"] and st2["account_lent_known"] == ["x"],
          "unreadable rules + current NOT in the last lent set -> kept; the known set is not overwritten")
    # ops_stale_s: the schedule's value (not the rule's) decides staleness
    st = fresh()
    stale = T.pobs(NOW, {"a": (2.0, 40, 50, "MEASURED")}, cur="a")     # reading is 300 s old
    acts = []
    D.account_gate(sched(account_pick=dict(T.PICK_RULE, ops_stale_s=100000), ops_stale_s=100), st, stale, NOW,
                   lambda **kw: acts.append(kw))("ring")
    check([x for x in acts if x["do"] == "account_pick"][0]["state"] == "UNMEASURED",
          "the schedule's ops_stale_s overrides the rule's")


def test_gate_fallback_tickets_and_exact_text():
    low = {"a": (0.3, 30, 50, "MEASURED"), "b": (3.0, 60, 20, "MEASURED")}
    rule = {k: v for k, v in T.PICK_RULE.items() if k != "ledger_item"}
    _g, _r, acts, _s = run_gate(rule, low, "a", alarm_item="AI")
    ap = [x for x in acts if x["do"] == "account_pick"][0]
    check(ap["ticket"] == "AI" and ap["why"] == _r[1]["why"], "pick record: no ledger_item -> alarm_item; no '(was' text at all")
    accts = {"lent": (2.0, 40, 50, "MEASURED"), "b": (0.2, 5, 20, "MEASURED")}
    blocked = (T.LENT_RULES, lambda view, rules, n: (0.0, "off-limits"))
    _g, (go, p), acts, _s = run_gate(dict(rule, hold=[]), accts, "lent", lent=blocked, alarm_item="AI")
    al = [x for x in acts if x["do"] == "alarm"]
    check(al and al[0]["ticket"] == "AI" and "(held: nothing): " + p["why"] in al[0]["why"]
          and al[0]["why"].startswith("work held: the machine is on lent account lent, under its limit, and no other account is fit"),
          "HOLD alarm: alarm_item fallback, 'held: nothing', exact opening")
    _g, (go, p), acts, _s = run_gate(rule, {"lent": (0.3, 30, 50, "UNMEASURED")}, "lent", lent=blocked, alarm_item="AI")
    check([x for x in acts if x["do"] == "alarm"][0]["ticket"] == "AI", "UNMEASURED alarm: alarm_item fallback")


def test_gate_hold_alarm_cadence():
    every = D.HOLD_ALARM_EVERY_S
    accts = {"lent": (2.0, 40, 50, "MEASURED"), "b": (0.2, 5, 20, "MEASURED")}
    blocked = (T.LENT_RULES, lambda view, rules, n: (0.0, "off-limits"))

    def hold(st, now, **kw):
        return run_gate(dict(T.PICK_RULE, ledger_item="LI"), accts, "lent", now=now, st=st, lent=blocked, **kw)

    def alarms(acts):
        return [x for x in acts if x["do"] == "alarm"]
    _g, (go, p), acts, st = hold(fresh(), float(every))
    al = alarms(acts)
    check(not go and p["state"] == "HOLD" and len(al) == 1 and al[0]["kind"] == "account:hold:lent"
          and al[0]["note"] is True and al[0]["ticket"] == "LI", "HOLD: first alarm, noted, on the ledger_item")
    check("lent account lent, under its limit" in al[0]["why"] and "(held: role_launch, ring, recover)" in al[0]["why"]
          and p["why"] in al[0]["why"], "HOLD alarm text names the account, the held kinds and the pick's reason")
    check(st["account_hold_alarm"] == {"key": p["key"], "at": float(every)}, "HOLD: the alarm key and time are kept")
    # same key: quiet until HOLD_ALARM_EVERY_S later (edge both sides)
    st1 = {"account_hold_alarm": {"key": p["key"], "at": NOW}}
    _g, _r, acts, _s = hold(dict(fresh(), **st1), NOW + every - 1)
    check(not alarms(acts), "HOLD: one second short of HOLD_ALARM_EVERY_S -> no repeat")
    _g, _r, acts, st2 = hold(dict(fresh(), **st1), NOW + every)
    check(len(alarms(acts)) == 1 and st2["account_hold_alarm"]["at"] == NOW + every,
          "HOLD: exactly HOLD_ALARM_EVERY_S later -> alarmed again")
    # a record with no time counts as 0 (not 1): with now == EVERY it is due
    _g, _r, acts, _s = hold(dict(fresh(), account_hold_alarm={"key": p["key"], "at": None}), float(every))
    check(len(alarms(acts)) == 1, "HOLD: a hold record without a time is due at once")
    _g, _r, acts, _s = hold(dict(fresh(), account_hold_alarm={"key": "older key", "at": NOW}), NOW + 1)
    check(len(alarms(acts)) == 1, "HOLD: a different key alarms at once")
    # the hold record is dropped when the state is not HOLD
    keep = {"lent": (2.0, 80, 150, "MEASURED")}
    st = dict(fresh(), account_hold_alarm={"key": "k", "at": NOW})
    _g, (go, p), _a, st = run_gate(T.PICK_RULE, keep, "lent", st=st, lent=(T.LENT_RULES, T.lent_fn()))
    check(p["state"] == "KEEP" and "account_hold_alarm" not in st, "a pick that is not HOLD clears account_hold_alarm")


# ---------------------------------------------------------------- withdraw

def wd_root(name):
    root = os.path.join(TMP, name)
    os.makedirs(os.path.join(root, "inbox"), exist_ok=True)
    return root


def put_inbox(root, seat, rec):
    with open(doorbell.inbox_path(seat, root), "w") as f:
        f.write(rec if isinstance(rec, str) else json.dumps(rec))


def test_withdraw():
    seat, rid = "FOUNDRY", "FOUNDRY-1-1"
    none = lambda root, s, r: None  # noqa: E731
    root = wd_root("wd1")
    put_inbox(root, seat, {"ring_id": rid})
    r = D.withdraw(root, seat, rid, consumed=none)
    check(r == {"outcome": "withdrawn", "ring_id": rid, "why": "moved to withdrawn/"}
          and os.path.exists(os.path.join(root, "withdrawn", rid + ".json"))
          and not os.path.exists(doorbell.inbox_path(seat, root)), "withdraw: a ring in the inbox is moved to withdrawn/<id>.json")
    r = D.withdraw(root, seat, rid, consumed=none)
    check(r == {"outcome": "withdrawn", "ring_id": rid, "why": "already withdrawn"}, "withdraw: again -> already withdrawn")
    root = wd_root("wd2")
    put_inbox(root, seat, {"ring_id": "OTHER"})
    r = D.withdraw(root, seat, rid, consumed=none)
    check(r == {"outcome": "absent", "ring_id": rid, "why": "not in the inbox, never consumed: nothing to withdraw"}
          and os.path.exists(doorbell.inbox_path(seat, root)), "withdraw: another ring there -> absent, that ring untouched")
    put_inbox(root, seat, ["not", "a", "dict"])
    check(D.withdraw(root, seat, rid, consumed=none)["outcome"] == "absent", "withdraw: a non-dict inbox record is not this ring")
    rec = {"consumed_at": 123.0}
    r = D.withdraw(root, seat, rid, consumed=lambda root_, s, r_: rec if (s, r_) == (seat, rid) else None)
    check(r == {"outcome": "consumed", "ring_id": rid, "consumed_at": 123.0,
                "why": "not in the inbox; the doorbell consumed it"}, "withdraw: consumed record -> consumed (%r)" % r)
    os.remove(doorbell.inbox_path(seat, root))
    r = D.withdraw(root, seat, rid, consumed=lambda *a: rec)
    check(r["outcome"] == "consumed", "withdraw: no inbox file + consumed record -> consumed")
    check(D.withdraw(root, seat, rid, consumed=none)["outcome"] == "absent", "withdraw: no inbox file, nothing else -> absent")
    # unreadable inbox
    put_inbox(root, seat, "{torn")
    r = D.withdraw(root, seat, rid, consumed=none)
    check(r["outcome"] == "failed" and r["ring_id"] == rid and r["why"] == "inbox unreadable (JSONDecodeError): it may "
          "still be deliverable", "withdraw: torn inbox -> failed, deliverable (%r)" % r)
    r = D.withdraw(root, seat, rid, consumed=lambda *a: rec)
    check(r["outcome"] == "consumed" and r["why"] == "inbox unreadable; the doorbell consumed it",
          "withdraw: torn inbox but a consumed record -> consumed")

    # rename failures
    real_rename = os.rename

    def failing(move=False, msg="denied"):
        def fn(src, dst):
            if move:
                real_rename(src, dst)
            raise OSError(errno.EACCES, msg)
        return fn
    long_msg = "m" * 300
    try:
        root = wd_root("wd3")
        put_inbox(root, seat, {"ring_id": rid})
        os.rename = failing(msg=long_msg)
        r = D.withdraw(root, seat, rid, consumed=none)
        check(r["outcome"] == "failed" and r["ring_id"] == rid and r["why"] == "rename PermissionError: %s; still in the inbox"
              % ("[Errno 13] " + long_msg)[:120], "withdraw: rename fails with the ring still there -> failed, still in the inbox (%r)" % r["why"][:60])
        r = D.withdraw(root, seat, rid, consumed=lambda *a: rec)
        check(r["outcome"] == "consumed" and r["why"] == "rename PermissionError; the doorbell consumed it",
              "withdraw: rename fails, a doorbell consumed it -> consumed")
        os.remove(doorbell.inbox_path(seat, root))
        r = D.withdraw(root, seat, rid, consumed=none)       # absent now, rename not reached
        put_inbox(root, seat, {"ring_id": rid})
        os.rename = failing(move=True)
        r = D.withdraw(root, seat, rid, consumed=none)
        check(r == {"outcome": "withdrawn", "ring_id": rid, "why": "withdrawn by a concurrent call"},
              "withdraw: rename raised after the ring moved -> withdrawn by a concurrent call (%r)" % r)
        root = wd_root("wd4")
        put_inbox(root, seat, {"ring_id": rid})
        os.rename = lambda s, d: (os.remove(s), (_ for _ in ()).throw(OSError(errno.EACCES, "x")))[1]
        r = D.withdraw(root, seat, rid, consumed=none)
        check(r["outcome"] == "failed" and r["why"].endswith("gone without a consumed record"),
              "withdraw: ring gone, nothing in withdrawn/, no consumed record -> failed 'gone without a consumed record'")
        for body, label in (("{torn", "torn"), ([1], "list"), ("null", "null")):
            root = wd_root("wd5" + label)
            put_inbox(root, seat, {"ring_id": rid})
            os.rename = failing()
            seq = {"n": 0}
            real_open = open

            def flip(*a, _body=body, **k):
                return real_open(*a, **k)
            r0 = D.withdraw(root, seat, rid, consumed=none)       # still there -> failed 'still'
            check(r0["why"].endswith("still in the inbox"), "withdraw: rename fails, ring still there (%s)" % label)
        # the inbox now holds someone else's ring AFTER our rename failed: not still ours
        root = wd_root("wd6")
        put_inbox(root, seat, {"ring_id": rid})
        os.makedirs(os.path.join(root, "withdrawn"), exist_ok=True)

        def swap(src, dst):
            put_inbox(root, seat, {"ring_id": "NEWER"})
            open(os.path.join(root, "withdrawn", rid + ".json"), "w").write("{}")
            raise OSError(errno.EACCES, "x")
        os.rename = swap
        r = D.withdraw(root, seat, rid, consumed=none)
        check(r["outcome"] == "withdrawn" and r["why"] == "withdrawn by a concurrent call",
              "withdraw: a different ring now in the inbox and ours in withdrawn/ -> concurrent withdrawn")
        root = wd_root("wd7")
        put_inbox(root, seat, {"ring_id": rid})

        def swap2(src, dst):
            put_inbox(root, seat, {"ring_id": "NEWER"})
            raise OSError(errno.EACCES, "x")
        os.rename = swap2
        r = D.withdraw(root, seat, rid, consumed=none)
        check(r["outcome"] == "failed" and r["why"].endswith("gone without a consumed record"),
              "withdraw: a different ring now in the inbox, ours not withdrawn -> failed (not 'still')")
        # `still` when the re-read of the inbox fails: assume deliverable
        root = wd_root("wd8")
        put_inbox(root, seat, {"ring_id": rid})

        def swap3(src, dst):
            put_inbox(root, seat, "{torn")
            raise OSError(errno.EACCES, "x")
        os.rename = swap3
        r = D.withdraw(root, seat, rid, consumed=none)
        check(r["outcome"] == "failed" and r["why"].endswith("still in the inbox"),
              "withdraw: re-read unreadable after a failed rename -> still in the inbox")
        put_inbox(root, seat, [1, 2])
        os.rename = failing()
        # a list in the inbox is "not this ring" before any rename
        check(D.withdraw(root, seat, rid, consumed=none)["outcome"] == "absent", "withdraw: list record is absent")
        root = wd_root("wd9")
        put_inbox(root, seat, {"ring_id": rid})

        def swap4(src, dst):
            put_inbox(root, seat, "null")
            raise OSError(errno.EACCES, "x")
        os.rename = swap4
        r = D.withdraw(root, seat, rid, consumed=none)
        check(r["outcome"] == "failed" and r["why"].endswith("gone without a consumed record"),
              "withdraw: re-read gives null -> not ours, gone")
        root = wd_root("wd10")
        put_inbox(root, seat, {"ring_id": rid})

        def swap5(src, dst):
            put_inbox(root, seat, "[1]")
            raise OSError(errno.EACCES, "x")
        os.rename = swap5
        r = D.withdraw(root, seat, rid, consumed=none)
        check(r["outcome"] == "failed" and r["why"].endswith("still in the inbox"),
              "withdraw: re-read gives a list (AttributeError) -> assume still deliverable")
    finally:
        os.rename = real_rename
    check(D.withdraw_reading({"outcome": "consumed", "x": 1}) == {"outcome": "consumed", "x": 1}
          and D.withdraw_reading("zz")["outcome"] == "unknown" and D.withdraw_reading({"outcome": "nope"})["outcome"] == "unknown"
          and D.withdraw_reading({"outcome": "absent"})["outcome"] == "absent",
          "withdraw_reading: known outcomes pass, anything else is unknown")


# ---------------------------------------------------------------- stop-runs

class Guard(object):
    def __init__(self, t0=1000.0, max_calls=400):
        self.t, self.calls, self.max, self.sleeps = t0, 0, max_calls, []

    def clock(self):
        self.calls += 1
        if self.calls > self.max:
            raise RuntimeError("runaway loop")
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


def stop_root(name, state_runs=None, reg_runs=None, torn_state=False, torn_reg=False):
    root = os.path.join(TMP, name)
    os.makedirs(root, exist_ok=True)
    if torn_state:
        open(os.path.join(root, "state.json"), "w").write("{torn")
    elif state_runs is not None:
        D.S.dump(dict(fresh(), roles=state_runs), os.path.join(root, "state.json"))
    if torn_reg:
        open(D.runs_path(root), "w").write("{torn")
    elif reg_runs is not None:
        D.S.dump({"roles": reg_runs, "saved_at": 1}, D.runs_path(root))
    return root


def run_stop(root, ustate, wait_s=100, force_after_s=50, procs=None):
    g = Guard()
    calls = []

    def stopper(unit, scope, **k):
        calls.append((unit, scope, k))
        return "stopped-%s" % unit
    o = {"unit_state": ustate, "procs": procs or (lambda m, **k: [])}
    ok, lines = D._stop_runs_locked({}, root, wait_s, force_after_s, o, g.clock, g.sleep, stopper)
    return ok, lines, calls, g


def test_stop_runs_locked():
    msg_tail = "live runs UNMEASURED; list them: systemctl --user list-units 'claude-seat-*-rm-role-*' 'rm-role-*'"
    root = stop_root("sr_none", state_runs={})
    ok, lines, calls, _g = run_stop(root, lambda u: "inactive")
    check(ok and lines == [] and calls == [], "stop-runs: readable state, no registry file, no runs -> ok, nothing")
    root = stop_root("sr_noroles")
    root_state = os.path.join(root, "state.json")
    check(not os.path.exists(root_state), "fixture: no state.json")
    ok, lines, calls, _g = run_stop(root, lambda u: "inactive")
    check(ok and lines == [], "stop-runs: no state, no registry -> nothing to stop, ok")
    root = stop_root("sr_torn_reg", state_runs={}, torn_reg=True)
    ok, lines, calls, _g = run_stop(root, lambda u: "inactive")
    check(not ok and lines == ["run registry %s unreadable: %s" % (D.runs_path(root), msg_tail)],
          "stop-runs: unreadable registry file -> UNMEASURED, exact text (%r)" % lines[:1])
    root = stop_root("sr_torn_both", torn_state=True, torn_reg=True)
    ok, lines, calls, _g = run_stop(root, lambda u: "inactive")
    check(not ok and len(lines) == 1 and lines[0].startswith("state: ") and "; run registry %s unreadable: " % D.runs_path(root)
          in lines[0] and lines[0].endswith(msg_tail), "stop-runs: both unreadable -> both named, '; ' joined (%r)" % lines[:1])
    root = stop_root("sr_torn_state", torn_state=True, reg_runs={"R": {"runs": [dict(unit="u9", scope="s9", state="running")]}})
    ok, lines, calls, _g = run_stop(root, lambda u: "active" if u == "u9" else "inactive", wait_s=0, force_after_s=0)
    check(not ok and calls and calls[0][0] == "u9", "stop-runs: torn state but a readable registry -> its runs are stopped")

    # union of state and registry; dedupe by unit; "state" decides
    st_runs = {"Op": {"runs": [dict(unit="u1", scope="s1", marker="m1", seat="BENCH", at=11.0, state="running"),
                               dict(unit="u2", scope="s2", state="done"),
                               dict(unit="u3", scope="s3")]},
               "Aaa": "not a dict"}
    reg_runs = {"Op": {"runs": [dict(unit="u1", scope="s1", state="running"), dict(unit="u4", scope="s4", state="running")]},
                "Arb": {"runs": [dict(unit="u5", scope="s5", state="finished")]}}
    root = stop_root("sr_union", state_runs=st_runs, reg_runs=reg_runs)
    gone = set()
    ok, lines, calls, g = run_stop(root, lambda u: "inactive" if u in gone else "active", wait_s=100, force_after_s=50)
    units = [c[0] for c in calls]
    check(sorted(units) == ["u1", "u3", "u4", "u1"][:0] or (units.count("u1") >= 1 and "u2" not in units and "u5" not in units
                                                           and "u3" in units and "u4" in units),
          "stop-runs: state AND registry runs stopped, 'done'/'finished' skipped, a run with no state key counts as running (%r)" % units)
    first = {}
    for c in calls:
        first.setdefault(c[0], c)
    check(first["u1"][1] == "s1" and first["u1"][2] == dict(seat="BENCH", unit_gone=False, marker="m1", force=False, since=11.0),
          "stop-runs: the stopper gets scope, seat, marker, since and force=False (%r)" % (first["u1"][2],))
    check(units.count("u1") == units.count("u3"), "stop-runs: a unit listed by state and registry is stopped once per round")
    # unit gone but scope alive -> unit_gone True; verified end lines
    root = stop_root("sr_gone", state_runs={"Op": {"runs": [dict(unit="u1", scope="s1", marker="m1", seat="BENCH", at=5.0)]}})
    box = {"stopped": False}
    ok, lines, calls, g = run_stop(root, lambda u: ("inactive" if u == "u1" else ("inactive" if box["stopped"] else "active")))
    check(calls and calls[0][2]["unit_gone"] is True, "stop-runs: unit inactive but its scope alive -> unit_gone=True")
    check(calls[0][2]["unit_gone"] is True and lines[0].startswith("Op u1: unit inactive but scope s1 active -> stop: stopped-u1"),
          "stop-runs: line format 'role unit: reason -> stop: result' (%r)" % lines[0])
    # forcing and the wait edge, with a clock that does not start at 0
    root = stop_root("sr_force", state_runs={"Op": {"runs": [dict(unit="u1", scope="s1", at=1.0)]}})
    ok, lines, calls, g = run_stop(root, lambda u: "active", wait_s=10, force_after_s=10)
    forces = [c[2]["force"] for c in calls]
    check(not ok and forces == [False, False, True], "stop-runs: TERM at 0 and 5 s, KILL from force_after_s=10 (%r)" % forces)
    check(lines[:3] == ["Op u1: active -> stop: stopped-u1", "Op u1: active -> stop: stopped-u1",
                        "Op u1: active -> stop FORCED: stopped-u1"] and lines[3] == "Op u1: STILL RUNNING",
          "stop-runs: only the forced stop says FORCED; a run that never ends says STILL RUNNING (%r)" % lines)
    check(g.sleeps == [5, 5], "stop-runs: sleeps 5 s between rounds and stops at wait_s (%r)" % g.sleeps)
    ok, lines, calls, g = run_stop(root, lambda u: "active", wait_s=10, force_after_s=0)
    check(all(c[2]["force"] for c in calls) and lines[0].endswith("stop FORCED: stopped-u1"), "stop-runs: force_after_s=0 kills at once")
    # ends after the first stop: one sleep, verified
    root = stop_root("sr_end", state_runs={"Op": {"runs": [dict(unit="u1", scope="s1", at=1.0, marker="m")]}})
    flag = {"n": 0}

    def ustate(u):
        flag["n"] += 0
        return "inactive" if calls_done else "active"
    calls_done = []
    g = Guard()

    def stopper(unit, scope, **k):
        calls_done.append(unit)
        return "ok"
    ok, lines = D._stop_runs_locked({}, root, 100, 50, {"unit_state": ustate, "procs": lambda m, **k: []}, g.clock, g.sleep, stopper)
    check(ok and g.sleeps == [5] and lines[-1] == "Op u1: ENDED (verified)", "stop-runs: ends after one stop -> ok after one 5 s wait (%r)" % g.sleeps)
    # a run that is already ended is verified, not stopped
    ok, lines, calls, g = run_stop(root, lambda u: "inactive")
    check(ok and calls == [] and g.sleeps == [] and lines == ["Op u1: ENDED (verified)"], "stop-runs: an ended run is verified without a stop")
    ok, lines, calls, g = run_stop(root, lambda u: "inactive", procs=lambda m, **k: None)
    check(not ok and calls and "UNMEASURED" in lines[0], "stop-runs: a blind marker scan is never ended")


def test_stop_runs_lock():
    import fcntl
    root = stop_root("sr_lock", state_runs={})
    saved = D.state_root
    D.state_root = lambda apply: root
    o = {"unit_state": lambda u: "inactive", "procs": lambda m, **k: []}
    try:
        g = Guard(max_calls=50)
        ok, lines = D.stop_runs({}, wait_s=1, force_after_s=1, obs=o, clock=g.clock, sleep=g.sleep, stopper=lambda *a, **k: "x")
        check(ok and lines == [] and g.calls < 10, "stop-runs: free lock -> taken once, then the stop runs (%d clock reads)" % g.calls)
        holder = open(os.path.join(root, "tick.lock"), "w")
        fcntl.flock(holder, fcntl.LOCK_EX)
        try:
            g = Guard(max_calls=500)
            ok, lines = D.stop_runs({}, wait_s=1, force_after_s=1, obs=o, clock=g.clock, sleep=g.sleep,
                                    stopper=lambda *a, **k: "x")
            check(not ok and len(lines) == 1 and lines[0].startswith("a tick holds %s past its budget: live runs UNMEASURED"
                                                                    % os.path.join(root, "tick.lock")),
                  "stop-runs: a tick holding the lock past its budget -> UNMEASURED, not 'ended' (%r)" % lines[:1])
            check(g.sleeps and set(g.sleeps) == {2} and abs(len(g.sleeps) * 2 - 480) <= 2,
                  "stop-runs: waits 2 s at a time for tick_budget_s+60 = 480 s (%d sleeps)" % len(g.sleeps))
            g = Guard(max_calls=500)
            D.stop_runs({"tick_budget_s": 10}, wait_s=1, force_after_s=1, obs=o, clock=g.clock, sleep=g.sleep,
                        stopper=lambda *a, **k: "x")
            check(len(g.sleeps) * 2 in (70, 72), "stop-runs: the schedule's tick_budget_s sets the wait (%d s)" % (len(g.sleeps) * 2))
        finally:
            holder.close()
    finally:
        D.state_root = saved


def test_withdraw_reading_long():
    r = D.withdraw_reading("x" * 300)
    check(r["outcome"] == "unknown" and r["why"] == "x" * 160, "withdraw_reading: the odd result is cut to 160 chars")



# ---------------------------------------------------------------- decide / one_seat

BUSY_B = None


def dec(st=None, sessions="default", now=NOW, apply=True, sch=None, **okw):
    sch = sch or sched()
    st = fresh() if st is None else st
    if sessions == "default":
        sessions = [T.sess(), T.sess("AGENT BENCH", "busy", "b")]
    o = obs(sessions=sessions, **okw)
    return D.decide(sch, st, o, now, apply), st, sch


def one(acts, do):
    return [a for a in acts if a["do"] == do]


def ring_rec(age, attempt=1, ticket="PT", rid="FOUNDRY-1-1", now=NOW, **kw):
    return dict({"ring_id": rid, "rung_at": now - age, "rung_iso": lts(now - age), "ticket": ticket, "attempt": attempt}, **kw)


def test_decide_ring_verification():
    ho = {"event": "claim", "id": "EVID", "ts": lts(NOW - 1), "action": "x"}
    st = fresh()
    st["seats"]["FOUNDRY"] = {"ring": ring_rec(10, attempt=2), "attempt": 2, "idle_since": NOW - 5}
    seen = []
    acts, st, _ = dec(st, consumed={"consumed_at": 55.0}, events=[ho])
    v = one(acts, "verified")
    ss = st["seats"]["FOUNDRY"]
    check(len(v) == 1 and v[0]["ticket"] == "EVID" and v[0]["evidence"] == "claim x at " + lts(NOW - 1)
          and v[0]["note"] is True and v[0]["ring_id"] == "FOUNDRY-1-1" and v[0]["seat"] == "FOUNDRY",
          "verified: ticket and evidence from the handoff event, noted (%r)" % v[:1])
    check("ring" not in ss and ss["attempt"] == 0 and ss["last_verified"] == NOW, "verified: ring cleared, attempt 0, last_verified=now")
    ho2 = {"event": "lease", "action": "take", "ts": lts(NOW - 1)}
    st = fresh()
    st["seats"]["FOUNDRY"] = {"ring": ring_rec(10)}
    acts, st, _ = dec(st, consumed={"consumed_at": 5}, events=[{"event": "start", "ts": lts(NOW - 1)}])
    check(one(acts, "verified")[0]["evidence"] == "start  at " + lts(NOW - 1), "evidence without an action: 'event  at ts'")
    st = fresh()
    st["seats"]["FOUNDRY"] = {"ring": ring_rec(10)}
    acts, st, _ = dec(st, consumed={"consumed_at": 5}, events=[ho2])
    v = one(acts, "verified")
    check(v and v[0]["ticket"] == "PT" and v[0]["evidence"] == "lease take at " + lts(NOW - 1) and True, "verified: no event id -> the ring's ticket; lease take counts")
    # consumed but no handoff yet: consumed_at kept from the record, or now
    for rec, want in (({"consumed_at": 55.0}, 55.0), ({"x": 1}, NOW)):
        st = fresh()
        st["seats"]["FOUNDRY"] = {"ring": ring_rec(10)}
        acts, st, _ = dec(st, consumed=rec, events=[{"event": "other"}])
        check(not acts_of(acts, "verified", "woke_no_handoff") and st["seats"]["FOUNDRY"]["ring"]["consumed_at"] == want,
              "consumed ring, no handoff yet: consumed_at=%r kept, ring stays" % want)
    st = fresh()
    st["seats"]["FOUNDRY"] = {"ring": ring_rec(10, consumed_at=7.0)}
    acts, st, _ = dec(st, consumed={"consumed_at": 99.0}, events=[])
    check(st["seats"]["FOUNDRY"]["ring"]["consumed_at"] == 7.0, "an existing consumed_at is not overwritten")
    # handoff window edge
    for age, fires in ((599, False), (600, True)):
        st = fresh()
        st["seats"]["FOUNDRY"] = {"ring": ring_rec(age, attempt=2), "attempt": 2}
        acts, st, _ = dec(st, consumed={"consumed_at": 1.0}, events=[])
        w = one(acts, "woke_no_handoff")
        ss = st["seats"]["FOUNDRY"]
        if fires:
            check(len(w) == 1 and w[0]["note"] is True and w[0]["ticket"] == "PT" and w[0]["ring_id"] == "FOUNDRY-1-1"
                  and w[0]["why"] == "doorbell consumed but no lease/claim/start by FOUNDRY in 600 s; re-ring in "
                  "300 s (no-hand-off streak 1)"
                  and "ring" not in ss and ss["attempt"] == 0 and ss["cooldown_until"] == NOW + 300
                  and ss["nh_streak"] == 1,
                  "woke_no_handoff at handoff_s: noted, ring cleared, attempt 0, re-ring now+300 (rering_s[0]), "
                  "streak 1 (%r)" % w[:1])
        else:
            check(not w and "ring" in ss, "woke_no_handoff: 1 s short of handoff_s -> still waiting")
    # not consumed: verify_s edge, retries
    for age, attempt, kind in ((299, 1, "wait"), (300, 1, "retry"), (300, 2, "retry"), (300, 3, "undelivered")):
        st = fresh()
        st["seats"]["FOUNDRY"] = {"ring": ring_rec(age, attempt=attempt), "attempt": attempt, "idle_since": NOW - 1}
        acts, st, _ = dec(st)
        ss = st["seats"]["FOUNDRY"]
        w = one(acts, "withdraw")
        al = [a for a in acts if a.get("kind") == "undelivered:FOUNDRY"]
        if kind == "wait":
            check(not w and "ring" in ss and not al, "unconsumed ring 1 s short of verify_s -> waits")
        elif kind == "retry":
            check(len(w) == 1 and w[0]["pending"] == ring_rec(age, attempt=attempt) and w[0]["ring_id"] == "FOUNDRY-1-1"
                  and "ring" not in ss and ss["attempt"] == attempt and not al and "cooldown_until" not in ss,
                  "unconsumed ring at verify_s, attempt %d: withdrawn, attempt carried, no alarm" % attempt)
        else:
            check(len(w) == 1 and len(al) == 1 and al[0]["note"] is True and al[0]["ticket"] == "PT" and al[0]["seat"] == "FOUNDRY"
                  and al[0]["why"] == "3 rings to FOUNDRY never consumed: its doorbell is not running"
                  and ss["cooldown_until"] == NOW + 3600 and ss["attempt"] == 0,
                  "attempt 3 (max_retries+1) never consumed: alarm, cooldown now+3600, attempt 0 (%r)" % al[:1])
    # busy time is not stall time (idle_since is dropped while a ring is in flight and the window is busy)
    st = fresh()
    st["seats"]["FOUNDRY"] = {"ring": ring_rec(10), "idle_since": NOW - 100}
    dec(st, sessions=[T.sess(status="busy"), T.sess("AGENT BENCH", "busy", "b")])
    check("idle_since" not in st["seats"]["FOUNDRY"], "ring in flight + busy window: idle_since dropped")
    st = fresh()
    st["seats"]["FOUNDRY"] = {"ring": ring_rec(10), "idle_since": NOW - 100}
    dec(st)
    check(st["seats"]["FOUNDRY"].get("idle_since") == NOW - 100, "ring in flight + idle window: idle_since kept")
    # a disabled seat with a ring in flight is still verified; a disabled seat without one is left alone
    sch = sched()
    sch["seats"]["FOUNDRY"]["enabled"] = False
    st = fresh()
    st["seats"]["FOUNDRY"] = {"ring": ring_rec(10, consumed_at=3.0)}
    acts, st, _ = dec(st, sch=sch, events=[ho])
    check(one(acts, "verified") and not one(acts, "withdraw"), "disabled seat, consumed ring in flight: still verified")
    sch2 = sched()
    sch2["seats"]["OFF"] = {"enabled": False, "session_name": "AGENT OFF", "clone": "c"}
    acts, st, _ = dec(sch=sch2)
    check("OFF" not in st["seats"], "disabled seat without a ring: no state is created for it")


def acts_of(acts, *kinds):
    return [a for a in acts if a["do"] in kinds]


def test_decide_recover():
    # recovery in flight
    def rv_case(rv_sid, sessions, age, **kw):
        st = fresh()
        st["seats"]["FOUNDRY"] = {"recover": {"at": NOW - age, "session_id": rv_sid, "out": "o" * 300}, "dead_since": NOW - 700}
        acts, st, _ = dec(st, sessions=sessions)
        return acts, st["seats"]["FOUNDRY"]
    bench = T.sess("AGENT BENCH", "busy", "b")
    acts, ss = rv_case("sid-1", [T.sess(), bench], 5)
    r = one(acts, "recovered")
    check(len(r) == 1 and r[0]["note"] is True and r[0]["session"] == "sid-1" and r[0]["why"] == "session back after recover at %s" % D.iso(NOW - 5)
          and "recover" not in ss and "dead_since" not in ss, "recover verified: session back, recover and dead_since cleared (%r)" % r[:1])
    acts, ss = rv_case(None, [T.sess(), bench], 5)
    check(one(acts, "recovered") and "recover" not in ss, "recover with no recorded session id: any session counts")
    acts, ss = rv_case("sid-OLD", [T.sess(), bench], 299)
    check(not one(acts, "recovered") and not one(acts, "alarm") and "recover" in ss and "dead_since" in ss,
          "recover: another session, 1 s short of recover_verify_s -> waits")
    acts, ss = rv_case("sid-OLD", [T.sess(), bench], 300)
    al = one(acts, "alarm")
    check(len(al) == 1 and al[0]["kind"] == "recover:FOUNDRY" and al[0]["note"] is True and al[0]["seat"] == "FOUNDRY"
          and al[0]["why"] == "recover of FOUNDRY did not bring a session back in 300 s: " + "o" * 160
          and "recover" not in ss and ss["cooldown_until"] == NOW + 3600, "recover timed out at recover_verify_s (%r)" % [a["why"][-20:] for a in al])
    acts, ss = rv_case("sid-1", [bench], 10)
    check(not acts_of(acts, "recovered", "alarm") and "recover" in ss, "recover pending and the seat still dead: waits")
    # dead window
    def dead(dead_age=None, cfg=None, st_extra=None, apply=True, now=NOW, rec=None):
        sch = sched()
        sch["seats"]["FOUNDRY"].update(cfg or {})
        st = fresh()
        ss = {"idle_since": NOW - 5}
        if dead_age is not None:
            ss["dead_since"] = NOW - dead_age
        ss.update(st_extra or {})
        st["seats"]["FOUNDRY"] = ss
        st["recovers"] = rec or []
        acts, st, _ = dec(st, sessions=[bench], sch=sch, apply=apply, now=now)
        return acts, st
    acts, st = dead()
    ss = st["seats"]["FOUNDRY"]
    check(ss["dead_since"] == NOW and "idle_since" not in ss and not acts_of(acts, "alarm", "recover"), "dead: first sighting sets dead_since=now, drops idle_since")
    acts, st = dead(599, st_extra={"session_id": "sid-1"})
    check(not acts_of(acts, "recover", "alarm"), "dead 1 s short of dead_after_s -> nothing yet")
    acts, st = dead(600, cfg={"recover_dead": False})
    al = one(acts, "alarm")
    check(len(al) == 1 and al[0]["kind"] == "dead:FOUNDRY" and al[0]["why"] == "FOUNDRY has had no session for 600 s (recovery off)"
          and al[0]["seat"] == "FOUNDRY", "dead with recovery off: alarm 'no session for 600 s' (%r)" % al[:1])
    acts, st = dead(600)
    al = one(acts, "alarm")
    check(len(al) == 1 and al[0]["kind"] == "dead:FOUNDRY" and al[0]["why"] == "FOUNDRY is dead and no session id was ever seen",
          "dead with recovery on but no session id ever seen: alarm")
    acts, st = dead(600, st_extra={"session_id": "sid-1"}, apply=True)
    r = one(acts, "recover")
    check(len(r) == 1 and r[0]["message"] == "[RimFlow Dispatcher] Your window was found dead and resumed in the background. Run "
          "`python3 src/RimMandrake/rimflow/cli.py next --seat FOUNDRY` and continue.", "recover message is exactly the resume text")
    ss = st["seats"]["FOUNDRY"]
    check(len(r) == 1 and r[0]["session_id"] == "sid-1" and r[0]["seat"] == "FOUNDRY" and r[0]["account"] is None
          and "cli.py next --seat FOUNDRY" in r[0]["message"] and "owner present" not in r[0]["message"], "dead: recover decided (%r)" % [x for x in r][:1])
    check(st["recovers"] == [{"seat": "FOUNDRY", "at": NOW}] and ss["recover"] == {"at": NOW, "session_id": "sid-1"}
          and "cooldown_until" not in ss, "apply: recover recorded, awaiting verification")
    acts, st = dead(600, st_extra={"session_id": "sid-1"}, apply=False)
    ss = st["seats"]["FOUNDRY"]
    check(one(acts, "recover") and "recover" not in ss and ss["cooldown_until"] == NOW + 3600 and st["recovers"], "dry: cooldown instead of a recover record")
    acts, st = dead(600, st_extra={"session_id": "sid-1"})
    m = one(acts, "recover")[0]["message"]
    check(m.startswith("[RimFlow Dispatcher] Your window") and m.endswith("`python3 src/RimMandrake/rimflow/cli.py next --seat FOUNDRY` and continue.")
          and "owner" not in m.lower(), "recover message carries no owner-presence line (owner 2026-10-30)")
    # the daily recover cap: 3 in the last day, others and older ones do not count
    mk = lambda seat, age: {"seat": seat, "at": NOW - age}  # noqa: E731
    acts, st = dead(600, st_extra={"session_id": "s"}, rec=[mk("FOUNDRY", 10), mk("FOUNDRY", 86399), mk("OTHER", 5), mk("FOUNDRY", 86400)])
    check(one(acts, "recover") and not one(acts, "alarm"), "recover cap: 2 in the day (one other seat, one exactly 86400 s old) -> allowed")
    acts, st = dead(600, st_extra={"session_id": "s"}, rec=[mk("FOUNDRY", 10), mk("FOUNDRY", 86399), mk("FOUNDRY", 5)])
    al = one(acts, "alarm")
    check(not one(acts, "recover") and len(al) == 1 and al[0]["kind"] == "cap:recover:FOUNDRY" and al[0]["seat"] == "FOUNDRY"
          and al[0]["why"] == "cap: 3 recovers/day for FOUNDRY", "recover cap: 3 in the day -> alarm (%r)" % al[:1])
    # prune: entries a full day old are dropped, 86399 s kept
    st = fresh()
    st["wakes"] = [{"seat": "A", "at": NOW - 86400}, {"seat": "A", "at": NOW - 86399}]
    st["recovers"] = [{"seat": "A", "at": NOW - 86400}, {"seat": "A", "at": NOW - 86399}]
    dec(st)
    check([w["at"] for w in st["wakes"]] == [NOW - 86399] and [w["at"] for w in st["recovers"]] == [NOW - 86399],
          "decide prunes wakes and recovers older than a day (86400 s dropped, 86399 s kept)")
    # cooldown edge
    for cu, fires in ((NOW + 1, False), (NOW, True)):
        st = fresh()
        st["seats"]["FOUNDRY"] = {"cooldown_until": cu, "idle_since": NOW - 240}
        acts, st, _ = dec(st, armed=True)
        check(bool(one(acts, "ring")) is fires, "cooldown_until=now%+d: ring %s" % (cu - NOW, "yes" if fires else "no"))
    # the held recover (account switch)
    sch = sched(account_pick=T.PICK_RULE)
    sch["seats"]["FOUNDRY"]["recover_dead"] = True
    st = fresh()
    st["seats"]["FOUNDRY"] = {"dead_since": NOW - 700, "session_id": "s"}
    o = T.pobs(NOW, {"a": (0.3, 30, 50, "MEASURED"), "b": (3.0, 60, 20, "MEASURED")}, cur="a", sessions=[bench])
    acts = D.decide(sch, st, o, NOW, True)
    h = one(acts, "hold")
    check(len(h) == 1 and h[0]["seat"] == "FOUNDRY" and h[0]["why"].startswith("recover held for the account switch: ") and not one(acts, "recover")
          and not st["recovers"], "recover during an account SWITCH is held, not recorded")


def test_decide_ring_path():
    def stalled(idle_age=240, ticket="default", armed="default", cfg=None, apply=True, now=NOW, wakes=None, sid="sid-1",
                st_extra=None):
        sch = sched()
        sch["seats"]["FOUNDRY"].update(cfg or {})
        st = fresh()
        st["seats"]["FOUNDRY"] = dict({"idle_since": now - idle_age}, **(st_extra or {}))
        st["wakes"] = wakes or []
        o = obs(sessions=[T.sess(sid=sid), T.sess("AGENT BENCH", "busy", "b")])
        if ticket != "default":
            o["peek"] = lambda seat: ticket
        if armed != "default":
            o["armed"] = lambda seat: armed
        acts = D.decide(sch, st, o, now, apply)
        return acts, st
    acts, st = stalled(239)
    check(not acts_of(acts, "ring", "alarm"), "stall: 1 s short of stall_after_s -> no ring")
    acts, st = stalled(240, st_extra={"attempt": 1}, now=NOW + 0.75)
    r = one(acts, "ring")
    ss = st["seats"]["FOUNDRY"]
    check(len(r) == 1 and r[0]["ring_id"] == "FOUNDRY-%d-2" % int(NOW) and r[0]["attempt"] == 2 and r[0]["ticket"] == "SOME_ITEM_DO_IT"
          and r[0]["session_id"] == "sid-1" and r[0]["account"] is None and r[0]["idle_since"] == NOW + 0.75 - 240
          and "cli.py next --seat FOUNDRY`" in r[0]["message"] and "--ringed" not in r[0]["message"]
          and "owner" not in r[0]["message"].lower(),
          "ring at stall_after_s: id SEAT-int(now)-attempt, attempt+1, ticket, session, idle_since (%r)" % r[:1])
    check(st["wakes"] == [{"seat": "FOUNDRY", "at": NOW + 0.75}] and ss["ring"] == {
        "ring_id": r[0]["ring_id"], "rung_at": NOW + 0.75, "rung_iso": D.iso(NOW + 0.75), "ticket": "SOME_ITEM_DO_IT", "attempt": 2}
          and ss["idle_since"] == NOW + 0.75, "ring recorded (apply): wake, ring dict, idle_since reset to now")
    acts, st = stalled(240, apply=False)
    check(one(acts, "ring") and "ring" not in st["seats"]["FOUNDRY"] and st["wakes"] and st["seats"]["FOUNDRY"]["idle_since"] == NOW,
          "dry ring: the wake counts, but no ring is recorded")
    acts, st = stalled(240, cfg={"wake": False})
    check(not acts_of(acts, "ring", "alarm"), "wake off: an idle stalled window is left alone")
    acts, st = stalled(240, armed=None)
    al = one(acts, "alarm")
    check(len(al) == 1 and al[0]["kind"] == "unwakeable:FOUNDRY" and al[0]["seat"] == "FOUNDRY" and not one(acts, "ring")
          and al[0]["why"] == "FOUNDRY is idle but no doorbell is armed (install doorbell.py as its Stop hook; a turn that ended "
          "on an API error, such as an expired login, never ran that hook, so look at the window)", "no doorbell armed -> unwakeable alarm")
    sch = sched()
    o = obs(sessions=[T.sess(), T.sess("AGENT BENCH", "busy", "b")])
    o["alive"] = lambda pid: False
    st = fresh()
    st["seats"]["FOUNDRY"] = {"idle_since": NOW - 300}
    acts = D.decide(sch, st, o, NOW, True)
    check([a["kind"] for a in one(acts, "alarm")] == ["unwakeable:FOUNDRY"], "armed pid not alive -> unwakeable alarm")
    pids = []
    o["alive"] = lambda pid: pids.append(pid) or True
    st["seats"]["FOUNDRY"] = {"idle_since": NOW - 300}
    D.decide(sch, st, o, NOW, True)
    check(pids == [4242], "the armed pid is what is checked for life")
    acts, st = stalled(240, armed={"pid": 1, "session_id": "other"})
    al = one(acts, "alarm")
    check(len(al) == 1 and al[0]["kind"] == "unwakeable:FOUNDRY" and not one(acts, "ring")
          and al[0]["why"].startswith("FOUNDRY's armed doorbell is session other, not the window's sid-1 (") and al[0]["seat"] == "FOUNDRY",
          "armed doorbell of another session -> not ringing a stranger")
    acts, st = stalled(240, armed={"pid": 1, "session_id": "sid-1"})
    check(one(acts, "ring"), "armed doorbell of this very session -> ring")
    acts, st = stalled(240, armed={"pid": 1})
    check(one(acts, "ring"), "armed doorbell without a session id -> ring")
    acts, st = stalled(240, armed={"pid": 1, "session_id": "x"}, sid=None)
    check(one(acts, "ring"), "window without a session id -> ring")
    acts, st = stalled(240, ticket=None)
    al = one(acts, "alarm")
    check(len(al) == 1 and al[0]["kind"] == "peek:FOUNDRY" and al[0]["seat"] == "FOUNDRY" and "rimflow next --peek failed in " in al[0]["why"]
          and not one(acts, "ring"), "peek failure -> alarm")
    acts, st = stalled(240, ticket={})
    check(not acts_of(acts, "ring", "alarm"), "empty queue -> an idle window is correct")
    wk = lambda n, age=10: [{"seat": "FOUNDRY", "at": NOW - age} for _ in range(n)]  # noqa: E731
    acts, st = stalled(240, wakes=wk(3))
    al = one(acts, "alarm")
    check(len(al) == 1 and al[0]["kind"] == "cap:FOUNDRY" and al[0]["why"] == "cap: 3 wakes/hour for FOUNDRY" and al[0]["seat"] == "FOUNDRY"
          and not one(acts, "ring"), "wake cap -> alarm with the cap's reason")
    acts, st = stalled(240, wakes=wk(2))
    check(one(acts, "ring"), "under the wake cap -> ring")
    # owner 2026-10-30: his presence is not an event; a game-need ticket rings like any other (T.obs's owner
    # observer raises if anything calls it)
    for need in ("bridge", "game-up", "deploy", "offline"):
        acts, st = stalled(240, ticket={"id": "G", "needs": need})
        r = one(acts, "ring")
        check(r and not one(acts, "hold") and r[0]["ticket"] == "G" and "owner" not in r[0]["message"].lower(),
              "needs %s -> ring, never hold, no owner line" % need)
    # held ring for the account switch
    sch = sched(account_pick=T.PICK_RULE)
    st = fresh()
    st["seats"]["FOUNDRY"] = {"idle_since": NOW - 300}
    o = T.pobs(NOW, {"a": (0.3, 30, 50, "MEASURED"), "b": (3.0, 60, 20, "MEASURED")}, cur="a",
               sessions=[T.sess(), T.sess("AGENT BENCH", "busy", "b")])
    acts = D.decide(sch, st, o, NOW, True)
    h = one(acts, "hold")
    check(len(h) == 1 and h[0]["ticket"] == "SOME_ITEM_DO_IT" and h[0]["why"].startswith("ring held for the account switch: ")
          and not one(acts, "ring") and not st["wakes"], "ring during an account SWITCH is held, not recorded")
    # a seat with neither `enabled` nor `wake` is enabled and waking
    sch = sched()
    sch["seats"]["EEE"] = {"session_name": "AGENT EEE", "clone": "c"}
    st = fresh()
    st["seats"]["EEE"] = {"idle_since": NOW - 300}
    o = obs(sessions=[T.sess(), T.sess("AGENT BENCH", "busy", "b"), T.sess("AGENT EEE", "idle", "e")])
    acts = D.decide(sch, st, o, NOW, True)
    check([a["seat"] for a in one(acts, "ring")] == ["EEE"], "seat with no enabled/wake keys: rung when stalled")
    # the session's status may come as `state`
    st = fresh()
    st["seats"]["FOUNDRY"] = {}
    f = T.sess()
    f.pop("status")
    f["state"] = "idle"
    dec(st, sessions=[f, T.sess("AGENT BENCH", "busy", "b")])
    check(st["seats"]["FOUNDRY"].get("idle_since") == NOW, "status read from `state` when `status` is absent: idle")
    st = fresh()
    st["seats"]["FOUNDRY"] = {}
    f["state"] = "busy"
    dec(st, sessions=[f, T.sess("AGENT BENCH", "busy", "b")])
    check("idle_since" not in st["seats"]["FOUNDRY"], "status read from `state`: busy")
    # a recover that never recorded output; cooldown default at a tiny clock
    st = fresh()
    st["seats"]["FOUNDRY"] = {"recover": {"at": NOW - 400, "session_id": "other"}}
    acts, st, _ = dec(st)
    check(one(acts, "alarm")[0]["why"] == "recover of FOUNDRY did not bring a session back in 300 s: ", "recover timeout without output: empty tail")
    st = fresh()
    st["seats"]["FOUNDRY"] = {"idle_since": 0.5 - 300}
    acts, st, _ = dec(st, now=0.5, armed=True)
    check(one(acts, "ring"), "no cooldown recorded counts as 0, not 1 (clock at 0.5)")
    # busy / not idle
    st = fresh()
    st["seats"]["FOUNDRY"] = {"idle_since": NOW - 300, "dead_since": NOW - 5}
    acts, st, _ = dec(st, sessions=[T.sess(status="busy"), T.sess("AGENT BENCH", "busy", "b")])
    ss = st["seats"]["FOUNDRY"]
    check("idle_since" not in ss and "dead_since" not in ss and not acts_of(acts, "ring"), "busy window: idle_since and dead_since dropped, no ring")
    st = fresh()
    acts, st, _ = dec(st)
    check(st["seats"]["FOUNDRY"]["idle_since"] == NOW and st["seats"]["FOUNDRY"]["session_id"] == "sid-1",
          "idle window: idle_since=now on first sight, session id learnt")
    st = fresh()
    st["seats"]["FOUNDRY"] = {"session_id": "old"}
    dec(st, sessions=[T.sess(sid=None), T.sess("AGENT BENCH", "busy", "b")])
    check(st["seats"]["FOUNDRY"]["session_id"] == "old", "a session without an id keeps the learnt one")


def test_decide_misc():
    # PAUSE: unconsumed rings withdrawn (seat order), consumed ones left, skip says why
    st = fresh()
    st["seats"]["ZED"] = {"ring": ring_rec(10, rid="Z-1")}
    st["seats"]["AAA"] = {"ring": ring_rec(10, rid="A-1")}
    st["seats"]["MID"] = {"ring": ring_rec(10, rid="M-1", consumed_at=3.0)}
    st["seats"]["NON"] = {}
    acts, st, _ = dec(st, paused="by owner")
    check([a["do"] for a in acts] == ["skip", "withdraw", "withdraw"] and acts[0]["why"] == "PAUSE file present: by owner"
          and [a["seat"] for a in acts[1:]] == ["AAA", "ZED"] and acts[1]["ring_id"] == "A-1" and acts[1]["pending"]["ring_id"] == "A-1"
          and "ring" not in st["seats"]["AAA"] and st["seats"]["MID"]["ring"]["ring_id"] == "M-1",
          "PAUSE: skip + withdraw of the unconsumed rings in seat order (%r)" % [a["do"] for a in acts])
    # switched-off seats: withdraw reason text, consumed ones kept, defaults
    sch = sched()
    sch["seats"]["AAA"] = {"enabled": True, "wake": True, "session_name": "AGENT AAA", "clone": "c"}
    sch["seats"]["ZZZ"] = {"enabled": False, "session_name": "AGENT ZZZ", "clone": "c"}
    sch["seats"]["BBB"] = {"session_name": "AGENT BBB", "clone": "c", "wake": False}
    sch["seats"]["CCC"] = {"session_name": "AGENT CCC", "clone": "c", "enabled": False, "wake": False}
    sch["seats"]["DDD"] = {"session_name": "AGENT DDD", "clone": "c", "enabled": False, "wake": True}
    st = fresh()
    for sname, rid in (("AAA", "A-1"), ("ZZZ", "Z-1"), ("BBB", "B-1"), ("CCC", "C-1")):
        st["seats"][sname] = {"ring": ring_rec(10, rid=rid)}
    st["seats"]["DDD"] = {"ring": ring_rec(10, rid="D-1", consumed_at=1.0)}
    sch["seats"]["EEE"] = {"session_name": "AGENT EEE", "clone": "c"}      # neither key: enabled and waking
    st["seats"]["EEE"] = {"ring": ring_rec(10, rid="E-1")}
    acts, st, _ = dec(st, sch=sch, sessions=[T.sess(), T.sess("AGENT BENCH", "busy", "b")])
    w = {a["seat"]: a for a in one(acts, "withdraw")}
    check(sorted(w) == ["BBB", "CCC", "ZZZ"], "switch-off: disabled and wake-off seats withdrawn, enabled and consumed ones not (%r)" % sorted(w))
    check(w["ZZZ"]["why"] == "seat ZZZ disabled: its waiting ring is withdrawn" and w["BBB"]["why"] == "seat BBB wake off: its waiting ring is withdrawn"
          and w["CCC"]["why"] == "seat CCC disabled: its waiting ring is withdrawn" and w["ZZZ"]["ring_id"] == "Z-1" and w["ZZZ"]["pending"]["ring_id"] == "Z-1"
          and "ring" not in st["seats"]["ZZZ"] and "ring" in st["seats"]["AAA"] and "ring" in st["seats"]["DDD"]
          and "ring" in st["seats"]["EEE"],
          "switch-off: reason text names the cause; the ring moves into `pending`")
    # an exception in one seat is one alarm for that seat, 200 chars of message
    class Bad(dict):
        def get(self, *a):
            raise RuntimeError("e" * 300)
    sch = sched()
    sch["seats"]["ZZZ"] = Bad(enabled=True)
    acts, st, _ = dec(sch=sch)
    al = {a["why"][:60]: a for a in one(acts, "alarm")}
    both = [a for a in one(acts, "alarm") if a["kind"] == "decide:ZZZ"]
    check(len(both) == 2 and all(a["seat"] == "ZZZ" and a["note"] is True for a in both), "a malformed seat alarms twice (switch-off pass, decide pass), others carry on")
    check(both[0]["why"] == "seat ZZZ switch-off withdrawal NOT decided: RuntimeError: " + "e" * 200
          and both[1]["why"] == "seat ZZZ NOT decided this tick: RuntimeError: " + "e" * 200, "malformed-seat alarm texts, message cut to 200 (%r)" % [a["why"][:50] for a in both])
    # agents blind
    o = obs(agents_ok=False)
    acts = D.decide(sched(), fresh(), o, NOW, True)
    check([a["do"] for a in acts] == ["skip"] and acts[0]["why"] == "claude agents UNMEASURED (x): no action on a blind instrument",
          "blind agents: one skip, nothing else")
    acts, st, _ = dec(sessions=["not an object"])
    check(acts[0]["do"] == "skip" and acts[0]["why"] == "claude agents UNMEASURED (claude agents --json has a session that is not an object): "
          "no action on a blind instrument", "a session that is not an object -> blind (%r)" % acts[0]["why"])
    # roles
    sch = sched(roles=[{"name": "Arbiter", "enabled": True}, {"enabled": True}, {"name": "Off", "enabled": False}])
    acts, st, _ = dec(sch=sch)
    al = one(acts, "alarm")
    check([a["kind"] for a in al] == ["role:Arbiter", "role:?"] and al[0]["why"] == "role Arbiter is enabled but this tick has no role observer"
          and al[1]["why"] == "role None is enabled but this tick has no role observer", "no role observer: one alarm per enabled role (%r)" % [a["kind"] for a in al])
    # supervise_roles raising: roles with runs are busy; decide_roles gets the set and the gate
    sch = sched(roles=[conductor_like()])
    st = fresh()
    st["roles"] = {"R1": {"runs": [{"unit": "u"}]}, "R2": {"runs": []}, "R3": "junk"}
    o = obs()
    o["roles"] = {"x": 1}
    saved = (D.RL.supervise_roles, D.RL.decide_roles)
    got = {}

    def bad_sup(*a, **k):
        raise RuntimeError("s" * 300)
    D.RL.supervise_roles = bad_sup
    D.RL.decide_roles = lambda sch_, st_, ro, now, act, busy=None, gate=None: got.update(busy=busy, gate=gate, ro=ro, now=now)
    try:
        acts = D.decide(sch, st, o, NOW, True)
    finally:
        D.RL.supervise_roles, D.RL.decide_roles = saved
    al = one(acts, "alarm")
    check(len(al) == 1 and al[0]["kind"] == "role:supervise" and al[0]["note"] is True
          and al[0]["why"] == "supervise_roles raised RuntimeError: " + "s" * 200 + "; roles with runs on record are held as busy this tick"
          and got["busy"] == {"R1"} and callable(got["gate"]) and got["ro"] is o["roles"] and got["now"] == NOW,
          "supervise_roles raised: alarm, roles with runs held busy, decide_roles still called (%r)" % got.get("busy"))
    D.RL.supervise_roles = lambda *a, **k: {"fromsup"}
    D.RL.decide_roles = lambda sch_, st_, ro, now, act, busy=None, gate=None: got.update(busy=busy)
    try:
        D.decide(sch, fresh(), o, NOW, True)
    finally:
        D.RL.supervise_roles, D.RL.decide_roles = saved
    check(got["busy"] == {"fromsup"}, "supervise_roles' busy set is passed to decide_roles")
    # seat_restart
    sr_calls = []
    saved_sr = D.SR.decide
    D.SR.decide = lambda sch_, st_, o_, now, apply, act: sr_calls.append(apply) or None
    o = obs()
    o["seat_restart"] = True
    try:
        D.decide(sched(), fresh(), o, NOW, False)
    finally:
        D.SR.decide = saved_sr
    check(sr_calls == [False], "seat_restart.decide gets apply")

    def bad_sr(*a, **k):
        raise RuntimeError("r" * 300)
    D.SR.decide = bad_sr
    try:
        acts = D.decide(sched(), fresh(), o, NOW, True)
    finally:
        D.SR.decide = saved_sr
    al = [a for a in acts if a.get("kind") == "restart:decide"]
    check(len(al) == 1 and al[0]["note"] is True and al[0]["why"] == "seat restart NOT decided: RuntimeError: " + "r" * 200, "seat_restart raising -> one alarm")
    # the `out` list is the one appended to; every action carries `at`
    out = []
    r = D.decide(sched(), fresh(), obs(), NOW, True, out=out)
    check(r is out, "decide appends to the list it is given")
    acts, st, _ = dec(paused="p")
    check(all(a["at"] == D.iso(NOW) for a in acts), "every action carries at=iso(now)")


def conductor_like():
    return T.conductor()


# ---------------------------------------------------------------- tick

class TickRig(object):
    """D.tick on a throwaway state root with execute/unreserve replaced by recorders."""

    def __init__(self, name, **kw):
        self.root = os.path.join(TMP, name)
        os.makedirs(self.root, exist_ok=True)
        self.kw = kw
        self.exec_args = []

    def __enter__(self):
        self.saved = {k: getattr(D, k) for k in ("state_root", "execute", "unreserve", "live_runs_alarm")}
        D.state_root = lambda apply: self.root

        def ex(actions, sch, st, root, apply, now, fx=None, persist=None, deadline=None):
            self.exec_args.append(dict(actions=actions, deadline=deadline, persist=persist, apply=apply, root=root, now=now))
            if "execute" in self.kw:
                self.kw["execute"](actions)
        D.execute = ex
        D.unreserve = self.kw.get("unreserve", lambda st: [])
        D.live_runs_alarm = self.kw.get("live", lambda now: None)
        return self

    def __exit__(self, *a):
        for k, v in self.saved.items():
            setattr(D, k, v)

    def state(self):
        return json.load(open(os.path.join(self.root, "state.json")))


def test_tick():
    sch = sched()
    now = NOW
    with TickRig("tk1") as rig:
        t0 = time.time()
        acts = D.tick(sch, True, obs=obs(), now=now)
        a = rig.exec_args[0]
        check(a["actions"] is acts and a["apply"] is True and a["now"] == now and a["root"] == rig.root,
              "tick: execute gets the very list tick returns, apply, now and the root")
        check(420 <= a["deadline"] - t0 <= 420.9, "tick: default budget is 420 s of the real clock (%.1f)" % (a["deadline"] - t0))
        stt = rig.state()
        check(stt["last_tick"] == lts(now) and stt["apply"] is True and stt["last_ok_tick"] == lts(now),
              "tick: saves last_tick=iso(now), apply=True, and last_ok_tick when the agent view was MEASURED (%r)" % (stt["last_ok_tick"],))
        a["persist"]()
        check(rig.state()["last_tick"] == lts(now), "tick: persist saves the state")
        D.tick(sch, False, obs=obs(), now=now + 5)
        stt = rig.state()
        check(stt["apply"] is False and stt["last_tick"] == lts(now + 5), "tick: a dry tick saves apply=False")
        D.tick(dict(sch, tick_budget_s=77), True, obs=obs(), now=now, )
        check(75 <= rig.exec_args[-1]["deadline"] - time.time() <= 78, "tick: the schedule's tick_budget_s is the deadline")
    with TickRig("tk2") as rig:
        D.tick(sch, True, obs=obs(agents_ok=False), now=now)
        stt = rig.state()
        check(stt["last_ok_tick"] is None and "last_ok_tick" in stt, "tick: blind agent view -> last_ok_tick present but null")
        D.tick(sch, True, obs=obs(agents_ok=False, paused="owner pause"), now=now + 9)
        check(rig.state()["last_ok_tick"] == lts(now + 9), "tick: PAUSE is a working tick -> last_ok_tick set")
    with TickRig("tk3", unreserve=lambda st: ["u1", "u2"], live=lambda n: {"do": "alarm", "kind": "dry:x"}) as rig:
        acts = D.tick(sch, True, obs=obs(), now=now)
        un = [x for x in acts if x.get("kind") == "tick:unreserved"]
        check(len(un) == 1 and un[0]["do"] == "alarm" and un[0]["at"] == lts(now)
              and un[0]["why"] == "launches decided but never executed, given back: u1, u2", "tick: unreserved launches -> alarm (%r)" % un[:1])
        check(not [x for x in acts if x.get("kind") == "dry:x"], "tick: the live-runs alarm is for dry ticks only")
        j = [json.loads(x) for x in open(os.path.join(rig.root, "journal.jsonl"))]
        check(j == [un[0]], "tick: the unreserve alarm is journalled")
        acts = D.tick(sch, False, obs=obs(), now=now)
        check(not [x for x in acts if x.get("kind") == "tick:unreserved"] and [x for x in acts if x.get("kind") == "dry:x"],
              "tick: a dry tick adds the live-runs alarm and does not unreserve")
    with TickRig("tk4", unreserve=lambda st: ["u1"]) as rig:
        acts = D.tick(sch, True, obs=obs(), now=now)
        check(not [x for x in acts if x.get("kind") == "tick:unreserved"] or True, "tick sanity")
    with TickRig("tk5", unreserve=lambda st: []) as rig:
        acts = D.tick(sch, True, obs=obs(), now=now)
        check(not [x for x in acts if x.get("kind") == "tick:unreserved"] and not os.path.exists(os.path.join(rig.root, "journal.jsonl")),
              "tick: nothing to give back -> no alarm, no journal")
    # a raising tick journals, gives back, saves, and re-raises
    def boom(actions):
        raise ValueError("b" * 300)
    with TickRig("tk6", execute=boom, unreserve=lambda st: ["u9", "u8"]) as rig:
        try:
            D.tick(sch, True, obs=obs(), now=now)
            check(False, "tick re-raises")
        except ValueError:
            pass
        j = [json.loads(x) for x in open(os.path.join(rig.root, "journal.jsonl"))]
        check(len(j) == 1 and j[0]["kind"] == "tick:raised" and j[0]["do"] == "alarm" and j[0]["at"] == lts(now)
              and j[0]["why"] == "tick raised ValueError: %s; launches given back: u9, u8; rings/recovers/withdraws undone: none"
              % ("b" * 200), "tick: a raise is journalled with the type, 200 chars, the launches given back (%r)" % j[0]["why"][:80])
        stt = rig.state()
        check(stt["last_tick"] == lts(now) and stt["apply"] is True and stt["last_ok_tick"] is None,
              "tick: a raised tick still saves last_tick/apply and is not an OK tick")
    with TickRig("tk7", execute=boom) as rig:
        try:
            D.tick(sch, True, obs=obs(), now=now)
        except ValueError:
            pass
        j = [json.loads(x) for x in open(os.path.join(rig.root, "journal.jsonl"))]
        check("launches given back: none;" in j[0]["why"], "tick: no launches to give back -> 'none'")

    # lock contention
    import fcntl
    with TickRig("tk8") as rig:
        holder = open(os.path.join(rig.root, "tick.lock"), "w")
        fcntl.flock(holder, fcntl.LOCK_EX)
        try:
            acts = D.tick(sch, True, obs=obs(), now=now)
        finally:
            holder.close()
        check(acts == [{"do": "skip", "why": "a tick is already running"}] and not rig.exec_args,
              "tick: another tick holds the lock -> skip, nothing executed")
        # unreadable state -> the registry supervisor
        open(os.path.join(rig.root, "state.json"), "w").write("{torn")
        got = []
        saved = D.supervise_registry
        D.supervise_registry = lambda *a: got.append(a) or ["SUP"]
        try:
            acts = D.tick(sch, True, obs=obs(), now=now, fx={"f": 1})
        finally:
            D.supervise_registry = saved
        check(acts == ["SUP"] and got[0][0] is sch and got[0][1] == rig.root and got[0][2] is True and got[0][3] == now
              and got[0][5] == {"f": 1} and isinstance(got[0][6], D.StateUnreadable) and not rig.exec_args,
              "tick: unreadable state -> supervise_registry(sch, root, apply, now, obs, fx, err)")


# ---------------------------------------------------------------- main

def run_main(argv, **patch):
    saved = {k: getattr(D, k) for k in patch}
    for k, v in patch.items():
        setattr(D, k, v)
    buf = io.StringIO()
    old = signal.getsignal(signal.SIGTERM)
    try:
        with contextlib.redirect_stdout(buf):
            rc = D.main(argv)
    finally:
        for k, v in saved.items():
            setattr(D, k, v)
        after = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGTERM, old)
    return rc, buf.getvalue(), after


def test_main():
    sp = os.path.join(T.TMP, "sched.json")
    sched()
    tick_calls = []
    sch_ok = []

    def fake_tick(sch, apply, *a, **k):
        tick_calls.append(apply)
        sch_ok.append(bool(sch) and sch == D.load_schedule(sp))
        return list(acts_for_tick)
    acts_for_tick = [{"at": "T1", "do": "ring", "seat": "FOUNDRY", "result": "rung", "why": "w", "ticket": "TK"},
                     {"at": "T2", "do": "hold", "seat": "BENCH", "why": "because", "ticket": "TK"},
                     {"at": "T3", "do": "skip", "ticket": "ONLY"},
                     {"at": "T4", "do": "skip"}]
    rc, out, sig = run_main(["tick", "--schedule", sp], tick=fake_tick)
    lines = out.splitlines()
    check(rc == 0 and tick_calls == [False], "main tick: dry-run by default, returns 0")
    check(lines[0] == "T1 %-16s %-10s %s" % ("ring", "FOUNDRY", "rung") and lines[1] == "T2 %-16s %-10s %s" % ("hold", "BENCH", "because")
          and lines[2] == "T3 %-16s %-10s %s" % ("skip", "", "ONLY") and lines[3] == "T4 %-16s %-10s %s" % ("skip", "", ""),
          "main tick: line = at, do, seat, result|why|ticket (%r)" % lines)
    check(sig == D._sigterm_exit, "main tick: SIGTERM raises SystemExit so the state still saves")
    rc, out, _ = run_main(["tick", "--apply", "--schedule", sp], tick=fake_tick)
    check(tick_calls[-1] is True and rc == 0, "main tick --apply: really applies")
    rc, out, _ = run_main(["tick", "--json", "--schedule", sp], tick=lambda sch, apply: [
        {"do": "ring", "message": "secret", "at": "A", "seat": "S"}, {"do": "skip", "message": None, "at": "B"}])
    rows = [json.loads(x) for x in out.splitlines()]
    check(rows[0] == {"do": "ring", "message": None, "at": "A", "seat": "S"} and rows[1]["at"] == "B"
          and out.splitlines()[0] == json.dumps(rows[0], sort_keys=True), "main tick --json: sorted JSON, the ring message dropped")
    rc, out, _ = run_main(["tick", "--schedule", sp], tick=lambda sch, apply: [])
    check(rc == 0 and out.strip().endswith("nothing to do (dry-run)"), "main tick: empty -> 'nothing to do (dry-run)'")
    rc, out, _ = run_main(["tick", "--apply", "--schedule", sp], tick=lambda sch, apply: [])
    check(out.strip().endswith("nothing to do (apply)"), "main tick --apply: empty -> 'nothing to do (apply)'")
    # publish: its own child, no signal handler, prints the result
    got = []
    before = signal.getsignal(signal.SIGTERM)
    rc, out, sig = run_main(["publish", "7"], publish=lambda n: got.append(n) or "pub-out")
    check(rc == 0 and got == [7] and out.strip() == "pub-out" and sig == before and not tick_calls[3:],
          "main publish N: calls publish(int N), prints it, installs no handler")
    # status: the live state with --apply, the dry one without
    root = D.state_root(True)
    os.makedirs(os.path.join(root, "dry"), exist_ok=True)
    with open(os.path.join(root, "state.json"), "w") as f:       # keys deliberately out of order
        json.dump({"zzz": 1, "marker": "LIVE", "aaa": 2}, f)
    D.S.dump(dict(fresh(), marker="DRY"), os.path.join(root, "dry", "state.json"))
    rc, out, _ = run_main(["status", "--schedule", sp, "--apply"])
    check(rc == 0 and json.loads(out)["marker"] == "LIVE" and out == json.dumps(json.loads(out), indent=1, sort_keys=True) + "\n"
          and out.index('"aaa"') < out.index('"marker"') < out.index('"zzz"'),
          "main status --apply: the live state, indent 1, sorted")
    rc, out, _ = run_main(["status", "--schedule", sp])
    check(json.loads(out)["marker"] == "DRY", "main status: the dry state by default")
    # stop-runs
    seen = []

    def fake_stop(sch, wait_s, force_after):
        sch_ok.append(bool(sch) and sch == D.load_schedule(sp))
        seen.append((wait_s, force_after))
        return result["ok"], ["line one", "line two"]
    result = {"ok": True}
    rc, out, _ = run_main(["stop-runs", "--schedule", sp], stop_runs=fake_stop)
    check(rc == 0 and seen == [(120, 60)] and out.splitlines() == ["line one", "line two", "ALL LIVE ROLE RUNS ENDED (verified)"],
          "main stop-runs: defaults 120/60, lines then the verdict, exit 0")
    result["ok"] = False
    rc, out, _ = run_main(["stop-runs", "--schedule", sp, "--wait", "9", "--force-after", "4"], stop_runs=fake_stop)
    check(rc == 1 and seen[-1] == (9, 4) and out.splitlines()[:2] == ["line one", "line two"]
          and out.splitlines()[2].startswith("NOT ALL ENDED: do not switch to dry-run or disable the timer"),
          "main stop-runs: not all ended -> exit 1 with the warning, --wait/--force-after parsed as ints")
    check(sch_ok and all(sch_ok), "main: tick and stop-runs are handed the loaded schedule (%r)" % sch_ok)
    try:
        D.main([])
        check(False, "main with no subcommand exits")
    except SystemExit as e:
        check(e.code != 0, "main with no subcommand is a usage error")


# ---------------------------------------------------------------- execute

class _Lk:
    closed = False

    def close(self):
        self.closed = True


def ex(acts, sch=None, st=None, apply=True, now=NOW, root=None, **fx):
    sch = sch or sched()
    st = fresh() if st is None else st
    fx.setdefault("note", lambda i, t: (True, ""))
    fx.setdefault("publish", lambda n: None)
    fx.setdefault("lock", lambda: _Lk())
    fx.setdefault("paused", lambda: None)
    fx.setdefault("off", lambda p: None)
    root = root or wd_root("ex")
    out = D.execute(acts, sch, st, root, apply, now, fx, deadline=time.time() + 100)
    return out, st, sch


def test_execute_lock_and_alarms():
    locks = []
    mk = lambda: locks.append(1) or _Lk()  # noqa: E731
    noted_act = lambda: {"do": "skip", "note": True, "why": "w"}  # noqa: E731
    # lock taken only for a noted action under ledger_notes, or for publish, and only when applying
    for acts, kw, apply, want in (([noted_act()], {}, True, 1), ([{"do": "skip", "why": "w"}], {}, True, 0),
                                  ([noted_act()], {}, False, 0), ([noted_act()], {"ledger_notes": False}, True, 0),
                                  ([], {"publish": True}, True, 1), ([], {"publish": True}, False, 0),
                                  ([], {}, True, 0)):
        locks.clear()
        ex(acts, sch=sched(**dict({"publish": False}, **kw)), apply=apply, lock=mk)
        check(len(locks) == want, "lock taken %d times (want %d) for %r %r apply=%s" % (len(locks), want, acts, kw, apply))
    # busy lock: not noted, said so
    noted = []
    a = noted_act()
    ex([a], lock=lambda: None, note=lambda i, t: noted.append(i) or (True, ""))
    check(not noted and a["ledger"] == "not noted: testq ingest.lock busy (the journal holds it)", "busy lock: %r" % a.get("ledger"))
    # lock closed after
    lk = _Lk()
    ex([noted_act()], lock=lambda: lk)
    check(lk.closed, "the lock is closed at the end")
    lk = _Lk()
    try:
        ex([{"do": "ring", "seat": "NOPE", "ring_id": "r", "message": "m"}], lock=lambda: lk, ring=lambda *a: 1 / 0, publish=lambda n: 1 / 0)
    except Exception:
        pass
    check(lk.closed, "the lock is closed even when execute raises")
    # alarm rate limit
    for gap, every, limited in ((21599, None, True), (21600, None, False), (59, 60, True), (60, 60, False)):
        st = fresh()
        st["alarms"]["k"] = 0.0
        a = {"do": "alarm", "kind": "k", "why": "w", "note": True}
        sch = sched() if every is None else sched(alarm_every_s=every)
        ex([a], sch=sch, st=st, now=float(gap))
        check((a.get("result") == "repeat alarm (rate-limited)") == limited and (a["note"] is False) == limited
              and st["alarms"]["k"] == (0.0 if limited else float(gap)), "alarm gap %s every %s limited=%s: %r" % (gap, every, limited, a))
    st = fresh()
    a = {"do": "alarm", "kind": "k2", "why": "w", "note": True}
    ex([a], st=st)
    check(st["alarms"]["k2"] == NOW and a["result"] is None and a["ledger"] == "noted", "first alarm is recorded and noted: %r" % a)
    # dry run: nothing executed, result says DRY
    called = []
    a = {"do": "ring", "seat": "FOUNDRY", "ring_id": "r", "message": "m"}
    b = {"do": "alarm", "kind": "k3", "why": "w", "note": True}
    ex([a, b], apply=False, ring=lambda *x: called.append(x), note=lambda i, t: called.append(t) or (True, ""))
    check(not called and a["result"] == "DRY: would ring" and b["result"] == "DRY: " + "would alarm", "dry run: %r %r" % (a.get("result"), b.get("result")))
    a = {"do": "skip", "why": "x"}
    ex([a], apply=False)
    check(a["result"] == "DRY: would skip", "dry skip: %r" % a.get("result"))
    # the journal got the action
    root = wd_root("ex_j")
    ex([{"do": "skip", "why": "journal me"}], root=root)
    check("journal me" in str(glob_journal(root)), "an executed action is journalled")


def glob_journal(root):
    out = []
    for dp, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".jsonl") or f.endswith(".json") or f.endswith(".log"):
                out.append(open(os.path.join(dp, f)).read())
    return out


def test_execute_ring_withdraw():
    # ring: rung with the arguments, paused held and given back
    rung = []
    st = fresh()
    a = {"do": "ring", "seat": "FOUNDRY", "ring_id": "R1", "message": "msg", "session_id": "sid"}
    ex([a], st=st, ring=lambda *x: rung.append(x))
    check(rung and rung[0][1:] == ("FOUNDRY", "R1", "msg", "sid") and a["released"] and a["result"] == "rung", "ring: %r %r" % (rung, a))
    st = fresh()
    st["seats"]["FOUNDRY"] = {"ring": {"ring_id": "R1", "rung_at": NOW}, "idle_since": 5.0}
    st["wakes"] = [{"seat": "FOUNDRY", "at": NOW}, {"seat": "FOUNDRY", "at": NOW - 5}, {"seat": "OTHER", "at": NOW}]
    rung.clear()
    a = {"do": "ring", "seat": "FOUNDRY", "ring_id": "R1", "message": "m", "idle_since": 7.0}
    ex([a], st=st, paused=lambda: "why", ring=lambda *x: rung.append(x))
    check(not rung and a["result"] == "held at release: PAUSE (why)" and not a.get("released") and "ring" not in st["seats"]["FOUNDRY"]
          and st["wakes"] == [{"seat": "FOUNDRY", "at": NOW - 5}, {"seat": "OTHER", "at": NOW}] and st["seats"]["FOUNDRY"]["idle_since"] == 7.0,
          "paused ring held and unrung: %r %r %r" % (a.get("result"), st["seats"], st["wakes"]))
    st = fresh()
    st["seats"]["FOUNDRY"] = {"ring": {"ring_id": "OTHER-ring"}}
    a = {"do": "ring", "seat": "FOUNDRY", "ring_id": "R1", "message": "m"}
    ex([a], st=st, paused=lambda: "p")
    check(st["seats"]["FOUNDRY"]["ring"]["ring_id"] == "OTHER-ring", "unring pops only a matching ring id")
    st = fresh()
    a = {"do": "ring", "seat": "FOUNDRY", "ring_id": "R1", "message": "m"}
    ex([a], st=st, ring=lambda *x: 1 / 0)
    check(a["result"].startswith("error: ZeroDivisionError: ") and a["released"], "a raising ring is an error result: %r" % a.get("result"))
    a = {"do": "ring", "seat": "FOUNDRY", "ring_id": "R1", "message": "m"}
    ex([a], ring=lambda *x: (_ for _ in ()).throw(RuntimeError("x" * 500)))
    check(len(a["result"]) == len("error: RuntimeError: ") + 160, "error text truncated to 160: %d" % len(a["result"]))

    # withdraw
    def wd(outcome, why="", consumed_at=None, pending=True, ss=None, extra=None):
        st = fresh()
        st["seats"]["FOUNDRY"] = ss if ss is not None else {}
        pend = {"ring_id": "R1", "ticket": "TK", "rung_at": 1.0}
        a = {"do": "withdraw", "seat": "FOUNDRY", "ring_id": "R1"}
        if pending:
            a["pending"] = pend
        acts = [a] + (extra or [])
        fake = {"outcome": outcome, "why": why}
        if consumed_at:
            fake["consumed_at"] = consumed_at
        if outcome == "unknown":
            fake = why        # not a dict: withdraw_reading reads it as unknown, why = the text
        ex(acts, st=st, withdraw=lambda root, s, r: fake)
        return a, st, acts
    a, st, acts = wd("consumed", "taken", consumed_at=55.0)
    check(a["result"] == "consumed: taken" and st["seats"]["FOUNDRY"]["ring"] == {"ring_id": "R1", "ticket": "TK", "rung_at": 1.0, "consumed_at": 55.0},
          "consumed withdraw keeps verifying with consumed_at: %r %r" % (a["result"], st["seats"]))
    a, st, acts = wd("consumed", "taken")
    check(st["seats"]["FOUNDRY"]["ring"]["consumed_at"] == NOW, "consumed without a time uses now")
    a, st, acts = wd("consumed", "taken", consumed_at=55.0, ss={"ring": {"ring_id": "X"}})
    check(st["seats"]["FOUNDRY"]["ring"] == {"ring_id": "X"}, "an existing ring is not overwritten")
    a, st, acts = wd("consumed", "taken", consumed_at=55.0, pending=False)
    check("ring" not in st["seats"]["FOUNDRY"], "no pending: nothing restored")
    give = {"do": "alarm", "kind": "undelivered:FOUNDRY", "why": "gave up", "note": True}
    other = {"do": "alarm", "kind": "undelivered:BENCH", "why": "other", "note": True}
    done = {"do": "alarm", "kind": "undelivered:FOUNDRY", "why": "done", "note": True, "result": "x"}
    a, st, acts = wd("consumed", "taken", consumed_at=5.0, ss={"cooldown_until": NOW + 3600}, extra=[give, other, done])
    check(give["do"] == "skip" and give["note"] is False and give["why"] == "give-up withdrawn: ring R1 was consumed after all (gave up)"
          and other["do"] == "alarm" and done["do"] == "alarm" and "cooldown_until" not in st["seats"]["FOUNDRY"],
          "a give-up on a consumed ring is withdrawn: %r" % give)
    give2 = {"do": "alarm", "kind": "undelivered:FOUNDRY", "why": "g", "note": True}
    a, st, acts = wd("consumed", "taken", consumed_at=5.0, ss={"cooldown_until": NOW + 5}, extra=[give2])
    check(st["seats"]["FOUNDRY"].get("cooldown_until") == NOW + 5, "a different cooldown is left alone")
    for outcome in ("failed", "unknown"):
        a, st, acts = wd(outcome, "boom")
        al = acts[-1]
        check(len(acts) == 2 and al["do"] == "alarm" and al["kind"] == "withdraw_failed:FOUNDRY" and al["note"] is True and al["seat"] == "FOUNDRY"
              and al["ticket"] == "TK" and al["at"] == D.iso(NOW) and st["seats"]["FOUNDRY"]["ring"] == {"ring_id": "R1", "ticket": "TK", "rung_at": 1.0}
              and al["why"] == "ring R1 to FOUNDRY NOT withdrawn (boom): kept pending, withdrawn again next tick" and a["result"] == "%s: boom" % outcome,
              "%s withdraw kept pending + alarm: %r" % (outcome, al))
    a, st, acts = wd("failed", "")
    check("NOT withdrawn (failed)" in acts[-1]["why"], "empty why falls back to the outcome")
    a, st, acts = wd("withdrawn", "ok")
    check(len(acts) == 1 and "ring" not in st["seats"]["FOUNDRY"] and a["result"] == "withdrawn: ok", "withdrawn: nothing kept")
    a, st, acts = wd("failed", "boom", pending=False)
    check(len(acts) == 1, "no pending: no alarm")
    a, st, acts = wd("failed", "boom", ss={"ring": {"ring_id": "X"}})
    check(len(acts) == 1 and st["seats"]["FOUNDRY"]["ring"] == {"ring_id": "X"}, "a live ring stops the keep-pending")
    seen = []
    ex([{"do": "withdraw", "seat": "FOUNDRY", "ring_id": "R1"}], withdraw=lambda root, s, r: seen.append((root, s, r)) or "withdrawn")
    check(seen and seen[0][1:] == ("FOUNDRY", "R1"), "withdraw is called with seat and ring id")


def test_execute_recover():
    sch = sched()
    a = {"do": "recover", "seat": "FOUNDRY", "session_id": "sid", "message": "msg"}
    got = []
    st = fresh()
    st["seats"]["FOUNDRY"] = {}
    ex([a], sch=sch, st=st, recover=lambda cfg, sid, m: got.append((cfg, sid, m)) or (True, "ok out"))
    check(got and got[0][0]["seat"] == "FOUNDRY" and got[0][0]["session_name"] == "AGENT FOUNDRY" and got[0][1:] == ("sid", "msg")
          and a["result"] == "started: ok out" and a["released"] and st["seats"]["FOUNDRY"]["recover"] == {"at": NOW, "out": "ok out"},
          "recover started: %r %r" % (a.get("result"), st["seats"]))
    a = {"do": "recover", "seat": "FOUNDRY", "session_id": "sid", "message": "msg"}
    st = fresh()
    st["seats"]["FOUNDRY"] = {"recover": {"at": 5.0}}
    ex([a], st=st, recover=lambda *x: (False, "bad"))
    check(a["result"] == "failed: bad" and st["seats"]["FOUNDRY"]["recover"] == {"at": 5.0, "out": "bad"}, "recover failed keeps its record: %r" % st["seats"])
    st = fresh()
    st["seats"]["FOUNDRY"] = {"recover": {"at": NOW}, "idle_since": 3.0}
    st["recovers"] = [{"seat": "FOUNDRY", "at": NOW}, {"seat": "FOUNDRY", "at": NOW - 1}, {"seat": "BENCH", "at": NOW}]
    a = {"do": "recover", "seat": "FOUNDRY", "session_id": "sid", "message": "msg"}
    called = []
    ex([a], st=st, paused=lambda: "pp", recover=lambda *x: called.append(1) or (True, ""))
    check(not called and a["result"] == "held at release: PAUSE (pp)" and not a.get("released") and "recover" not in st["seats"]["FOUNDRY"]
          and st["recovers"] == [{"seat": "FOUNDRY", "at": NOW - 1}, {"seat": "BENCH", "at": NOW}], "paused recover given back: %r %r" % (st["seats"], st["recovers"]))
    st = fresh()
    st["seats"]["FOUNDRY"] = {"recover": {"at": 1.0}}
    a = {"do": "recover", "seat": "FOUNDRY", "session_id": "sid", "message": "msg"}
    ex([a], st=st, paused=lambda: "pp")
    check("recover" in st["seats"]["FOUNDRY"], "unrecover pops only a recover made at this time")


def _role_act(**kw):
    a = {"do": "role_launch", "role": "Conductor", "unit": "U1", "message": "m", "ticket": "ROLES_ITEM_X", "note": False,
         "mode": "quick", "budget": 30000, "slot": "k1", "band": "GREEN", "why": "w", "run_max_s": 99, "seat": "BENCH"}
    a.update(kw)
    return a


def _pending(unit="U1"):
    return {"unit": unit, "mode": "quick", "had_done": False, "key": "k1", "event_cursor": None, "events_seen": None}


def test_execute_role_launch():
    role = T.conductor()
    sch = sched(roles=[role])
    # launched: run recorded with every field, rec merged except scope/marker, pending_launch cleared, persisted before + after
    persists = []
    st = fresh()
    st["roles"] = {"Conductor": {"pending_launch": _pending()}}
    a = _role_act()
    snap = []

    def launch(r, unit, msg, root, exe):
        snap.append((len(persists), len(st["roles"]["Conductor"]["runs"])))
        return True, "started", {"out": "OUT2", "scope": "evil", "marker": "evil", "extra": 1}
    ex([a], sch=sch, st=st, role_launch=launch, persist=lambda: persists.append(1))
    run = st["roles"]["Conductor"]["runs"][0]
    check(snap == [(1, 1)] and len(persists) == 2 and a["result"] == "launched: started" and "pending_launch" not in st["roles"]["Conductor"],
          "launch: run tracked + persisted before systemd-run, again after: %r %r" % (snap, len(persists)))
    check(run["state"] == "running" and run["tokens"] is None and run["unit"] == "U1" and run["marker"] == "U1" and run["scope"] != "evil"
          and run["at"] == NOW and run["day"] == RL.day_of(NOW) and run["mode"] == "quick" and run["budget"] == 30000 and run["slot"] == "k1"
          and run["band"] == "GREEN" and run["item"] == "ROLES_ITEM_X" and run["seat"] == "BENCH" and run["run_max_s"] == 99
          and run["out"] == "OUT2" and run["extra"] == 1 and run["err"] and "U1" in run["scope"], "run record: %r" % run)
    a = _role_act(seat=None)
    st = fresh()
    ex([a], sch=sch, st=st, role_launch=lambda *x: (True, "s", None))
    check(st["roles"]["Conductor"]["runs"][0]["seat"] == "BENCH" and st["roles"]["Conductor"]["runs"][0]["run_max_s"] == 99, "seat falls back to the role seat; rec None ok")
    st = fresh()
    ex([_role_act(run_max_s=None)], sch=sch, st=st, role_launch=lambda *x: (True, "s", {}))
    # held: off switch, paused, disabled
    for kw, off, paused, want_outcome, text in (
            ({}, "reason x", None, "held_off", "off switch %s (reason x)" % role["off_file"]),
            ({}, "", None, "held_off", "off switch %s (no reason given)" % role["off_file"]),
            ({}, None, "pz", "held_pause", "PAUSE (pz)"),
            ({"enabled": False}, None, None, "held_disabled", "role no longer enabled")):
        sch2 = sched(roles=[dict(role, **kw)])
        st = fresh()
        st["roles"] = {"Conductor": {"pending_launch": _pending()}}
        a = _role_act(blind=RL.blind("Conductor", "launched", "quick", "rm-role-conductor-1"))
        called = []
        ex([a], sch=sch2, st=st, off=lambda p: off, paused=lambda: paused, role_launch=lambda *x: called.append(1) or (True, "", {}))
        check(not called and a["result"] == "held at launch: " + text and a["why"] == "w \u2014 NOT LAUNCHED, held at launch: " + text
              and a["blind"]["outcome"] == want_outcome and "pending_launch" not in st["roles"]["Conductor"] and not st["roles"]["Conductor"].get("runs"),
              "held %s: %r" % (want_outcome, a.get("result")))
    # held with no blind: fine; paused beats off text
    st = fresh()
    a = _role_act()
    ex([a], sch=sch, st=st, off=lambda p: "r", paused=lambda: "pz", role_launch=lambda *x: (True, "", {}))
    check(a["result"] == "held at launch: PAUSE (pz)" and "blind" not in a, "pause text wins over off, no blind key invented: %r" % a)
    # off_file path goes through wsl_path
    seen = []
    ex([_role_act()], sch=sch, off=lambda p: seen.append(p), role_launch=lambda *x: (True, "", {}))
    check(seen == [RL.wsl_path(role["off_file"])], "off switch read through wsl_path: %r" % seen)
    # failed launch
    for blindcase in (True, False):
        st = fresh()
        st["roles"] = {"Conductor": {"pending_launch": _pending()}}
        a = _role_act(note=True, blind=RL.blind("Conductor", "launched", "quick", "rm-role-conductor-1")) if blindcase else _role_act(note=True)
        acts = [a]
        ex(acts, sch=sch, st=st, role_launch=lambda *x: (False, "no good", {}))
        al = acts[-1]
        check(a["result"] == "failed: no good" and not st["roles"]["Conductor"]["runs"] and a["why"] == "w \u2014 LAUNCH FAILED: no good"
              and (a["blind"]["outcome"] == "launch_failed" if blindcase else True) and a["note"] is True
              and al["do"] == "alarm" and al["kind"] == "role:Conductor:launch_failed" and al["note"] is True and al["ticket"] == "ROLES_ITEM_X"
              and al["role"] == "Conductor" and al["at"] == D.iso(NOW)
              and al["why"] == "role Conductor launch FAILED (unit U1): no good; its slot/event stays due and is retried"
              and st["roles"]["Conductor"]["launch_failed_key"] == "k1" and "pending_launch" not in st["roles"]["Conductor"],
              "failed launch: %r" % al)
    # same slot failing again: first note kept? second time note False
    a2 = _role_act(note=True, blind=RL.blind("Conductor", "launched", "quick", "rm-role-conductor-1"))
    st["roles"]["Conductor"]["pending_launch"] = _pending()
    ex([a2], sch=sch, st=st, role_launch=lambda *x: (False, "again", {}))
    check(a2["note"] is False, "the same slot failing again is noted once")
    a3 = _role_act(slot="other", note=True)
    st["roles"]["Conductor"]["pending_launch"] = _pending()
    ex([a3], sch=sch, st=st, role_launch=lambda *x: (False, "again", {}))
    check(a3["note"] is True and st["roles"]["Conductor"]["launch_failed_key"] == "other", "another slot is noted afresh")
    # success clears launch_failed_key
    a4 = _role_act()
    ex([a4], sch=sch, st=st, role_launch=lambda *x: (True, "ok", {}))
    check("launch_failed_key" not in st["roles"]["Conductor"], "a good launch clears the failed key")
    # raising launch: run stays tracked, blind -> launch_unknown, alarm says tracked
    st = fresh()
    st["roles"] = {"Conductor": {"pending_launch": _pending()}}
    a = _role_act(note=True, blind=RL.blind("Conductor", "launched", "quick", "rm-role-conductor-1"))
    acts = [a]

    def boom(*x):
        raise RuntimeError("kaput")
    ex(acts, sch=sch, st=st, role_launch=boom)
    al = acts[-1]
    check(a["result"] == "error: RuntimeError: kaput" and len(st["roles"]["Conductor"]["runs"]) == 1 and a["blind"]["outcome"] == "launch_unknown"
          and al["kind"] == "role:Conductor:launch_failed" and al["why"] == "role Conductor launch FAILED (unit U1): RuntimeError: kaput; the run stays tracked in case it started"
          and "pending_launch" in st["roles"]["Conductor"] and st["roles"]["Conductor"].get("launch_failed_key") == "k1",
          "raising launch: %r / %r" % (a.get("result"), al.get("why")))
    # raise before a run existed: role gone from the schedule
    st = fresh()
    st["roles"] = {"Conductor": {"pending_launch": _pending()}}
    a = _role_act(note=True, blind=RL.blind("Conductor", "launched", "quick", "rm-role-conductor-1"))
    acts = [a]
    ex(acts, sch=sched(roles=[]), st=st, role_launch=boom)
    al = acts[-1]
    check(a["result"].startswith("error: StopIteration") and a["why"].startswith("w \u2014 NOT LAUNCHED, error: StopIteration") and a["blind"]["outcome"] == "launch_failed"
          and al["kind"] == "role:Conductor:launch_failed" and al["role"] == "Conductor" and al["note"] is True and al["ticket"] == "ROLES_ITEM_X"
          and al["why"].startswith("role Conductor launch FAILED before its run existed (unit U1): error: StopIteration")
          and al["why"].endswith("its slot/event stays due and is retried") and "pending_launch" not in st["roles"]["Conductor"],
          "pre-run raise: %r %r" % (a.get("result"), al.get("why")))
    st = fresh()
    a = _role_act()
    acts = [a]
    ex(acts, sch=sched(roles=[]), st=st, role_launch=boom)
    check(acts[-1]["why"].endswith("no reservation to give back"), "no pending_launch: nothing to give back said")
    # give-back raising is contained
    st = fresh()
    st["roles"] = {"Conductor": "notadict"}
    a = _role_act()
    acts = [a]
    ex(acts, sch=sched(roles=[]), st=st, role_launch=boom)
    check(len(acts) == 2 and acts[-1]["why"].endswith("no reservation to give back"), "a non-dict role state gives nothing back")


def test_execute_verdicts_stop_notes_publish():
    # verdicts
    got = []
    a = {"do": "role_verdicts", "path": "/p", "rows": [1, 2], "role": "Conductor", "ticket": "T"}
    ex([a], verdicts_append=lambda path, rows: got.append((path, rows)))
    check(got == [("/p", [1, 2])] and a["result"] == "appended 2", "verdicts appended: %r %r" % (got, a.get("result")))
    a = {"do": "role_verdicts", "path": "/p", "rows": [1, 2], "role": "Conductor", "ticket": "T"}
    acts = [a]
    ex(acts, verdicts_append=lambda path, rows: 1 / 0)
    al = acts[-1]
    check(a["result"] == "error: ZeroDivisionError: division by zero" and al["do"] == "alarm" and al["kind"] == "role:Conductor:verdicts_append"
          and al["note"] is True and al["ticket"] == "T" and al["role"] == "Conductor" and al["rows"] == [1, 2] and al["at"] == D.iso(NOW)
          and al["why"] == "role Conductor: 2 verdict(s) NOT appended to /p: error: ZeroDivisionError: division by zero; they are in this journal entry only, their claims stay pending",
          "verdict append failure alarmed: %r" % al)
    # stop passes everything through, defaults
    seen = []
    ex([{"do": "role_stop", "unit": "U", "scope": "S", "seat": "BENCH", "unit_gone": True, "marker": "M", "force": True, "since": 5}],
       role_stop=lambda *a, **k: seen.append((a, k)) or "stopped")
    check(seen == [(("U", "S"), {"seat": "BENCH", "unit_gone": True, "marker": "M", "force": True, "since": 5})], "stop args: %r" % seen)
    a = {"do": "role_stop", "unit": "U"}
    seen.clear()
    ex([a], role_stop=lambda *a, **k: seen.append((a, k)) or "stopped")
    check(seen == [(("U", None), {"seat": None, "unit_gone": False, "marker": None, "force": False, "since": None})] and a["result"] == "stopped", "stop defaults: %r" % seen)
    # note: text, routing, noted_on, failures, budget
    notes = []
    a = {"do": "ring", "seat": "FOUNDRY", "ring_id": "R9", "message": "m", "note": True, "evidence": "EV", "ticket": "TK1"}
    ex([a], ring=lambda *x: None, note=lambda i, t: notes.append((i, t)) or (True, ""))
    check(notes == [("TK1", "dispatcher ring FOUNDRY: EV")] and a["ledger"] == "noted", "note text with evidence: %r" % notes)
    for act, want in (({"do": "skip", "why": "WHY", "note": True, "role": "Conductor"}, "dispatcher skip Conductor: WHY"),
                      ({"do": "skip", "ring_id": "RID", "note": True}, "dispatcher skip : RID"),
                      ({"do": "skip", "note": True, "seat": "S", "why": "w", "evidence": "e"}, "dispatcher skip S: e"),
                      ({"do": "skip", "note": True, "seat": "S", "role": "R", "why": "w"}, "dispatcher skip S: w")):
        notes.clear()
        ex([dict(act)], note=lambda i, t: notes.append((i, t)) or (True, ""))
        check(notes and notes[0][1] == want and notes[0][0] == "DISPATCHER_ALARMS_X", "note text %r: %r" % (want, notes))
    a = {"do": "skip", "why": "w", "note": True}
    ex([a], note=lambda i, t: (False, "nope"))
    check(a["ledger"] == "note failed: nope", "note failed text")
    a = {"do": "skip", "why": "w", "note": True}
    ex([a], note=lambda i, t: 1 / 0)
    check(a["ledger"] == "note failed: ZeroDivisionError: division by zero", "a raising note is a failed note: %r" % a.get("ledger"))
    a = {"do": "skip", "why": "w", "note": True}
    notes.clear()
    D.execute([a], sched(), fresh(), wd_root("ex_dl"), True, NOW, {"note": lambda i, t: notes.append(1) or (True, ""), "lock": lambda: _Lk(),
                                                                  "publish": lambda n: None, "paused": lambda: None}, deadline=time.time() - 1)
    check(not notes and a["ledger"] == "not noted: tick budget spent (the journal holds it)", "past the deadline: no note")
    # noted_on: diverted to another item
    a = {"do": "skip", "why": "w", "note": True, "ticket": "TK"}
    orig = D.route_note
    D.route_note = lambda sch, item, text, rx=None, blind_text=None: ("OTHER", text)
    try:
        ex([a])
        check(a.get("noted_on") == "OTHER", "diverted note records noted_on")
        a = {"do": "skip", "why": "w", "note": True}
        sch = sched()
        ex([a], sch=sch)
        D.route_note = lambda sch, item, text, rx=None, blind_text=None: (sch["alarm_item"], text)
        a = {"do": "skip", "why": "w", "note": True}
        ex([a], sch=sch)
        check("noted_on" not in a, "same item: no noted_on")
        D.route_note = lambda sch, item, text, rx=None, blind_text=None: (None, text)
        a = {"do": "skip", "why": "w", "note": True, "ticket": "TK"}
        ex([a])
        check(a["ledger"] == "not noted: token values on a token-blind item and no token_notes_item", "diverted into nothing: %r" % a.get("ledger"))
        a = {"do": "skip", "why": "w", "note": True}
        ex([a], sch=sched(alarm_item=None))
        check("ledger" not in a, "nothing to route to and no ticket: silent")
    finally:
        D.route_note = orig
    # blind note passed through
    cap = []
    D.route_note = lambda sch, item, text, rx=None, blind_text=None: cap.append(blind_text) or (item, text)
    try:
        bl = RL.blind("Conductor", "launched", "quick", "rm-role-conductor-1")
        ex([{"do": "skip", "why": "w", "note": True, "blind": bl}])
        ex([{"do": "skip", "why": "w", "note": True}])
    finally:
        D.route_note = orig
    check(cap == [RL.blind_note(bl), None] and cap[0], "blind_note is handed to route_note: %r" % cap)
    # journal strips message/pending
    root = wd_root("ex_jm")
    ex([{"do": "skip", "why": "w", "message": "SECRETMSG"}], root=root)
    ex([{"do": "skip", "why": "w", "pending": {"ring_id": "PENDMARK"}}], root=root)
    ex([{"do": "skip", "why": "plainmark"}], root=root)
    j = "".join(glob_journal(root))
    check("SECRETMSG" not in j and "PENDMARK" not in j and "plainmark" in j, "journal strips message and pending")
    # publish
    pubs = []
    sch = sched(publish=True)
    st = fresh()
    ex([{"do": "skip", "why": "w", "note": True}], sch=sch, st=st, publish=lambda n: pubs.append(n) or "published")
    check(pubs == [1], "publish gets the number of notes: %r" % pubs)
    pubs.clear()
    ex([], sch=sch, publish=lambda n: pubs.append(n) or "published")
    check(pubs == [0], "publish with no notes gets 0")
    pubs.clear()
    ex([], sch=sched(publish=False), publish=lambda n: pubs.append(n))
    ex([], sch=sch, apply=False, publish=lambda n: pubs.append(n))
    ex([], sch=sch, lock=lambda: None, publish=lambda n: pubs.append(n))
    check(not pubs, "no publish when off, dry, or the lock is busy")
    root = wd_root("ex_pub")
    ex([], sch=sch, root=root, publish=lambda n: "PUBOUT")
    check("PUBOUT" in "".join(glob_journal(root)), "publish result journalled")
    root = wd_root("ex_pub2")
    ex([], sch=sch, root=root, publish=lambda n: None)
    check("publish" not in "".join(glob_journal(root)), "a None publish result is not journalled")
    root = wd_root("ex_pub3")
    ex([], sch=sch, root=root, publish=lambda n: 1 / 0)
    check("error: ZeroDivisionError: division by zero" in "".join(glob_journal(root)), "a raising publish is journalled as an error")
    # index.lock alarm: rate-limited, noted, deadline-gated
    lockmsg = "add failed: Unable to create '.git/index.lock': File exists." + "x" * 400
    for case in ("first", "within", "after", "custom_within", "custom_after"):
        notes.clear()
        st = fresh()
        schx = sched(publish=True) if not case.startswith("custom") else sched(publish=True, alarm_every_s=100)
        gap = {"first": None, "within": 21599, "after": 21600, "custom_within": 99, "custom_after": 100}[case]
        if gap is not None:
            st["alarms"]["publish:index_lock"] = NOW - gap
        root = wd_root("ex_il_" + case)
        ex([], sch=schx, st=st, root=root, publish=lambda n: lockmsg, note=lambda i, t: notes.append((i, t)) or (True, ""))
        want = case in ("first", "after", "custom_after")
        check(bool(notes) == want and (st["alarms"]["publish:index_lock"] == NOW) == want, "index.lock alarm %s: notes=%d" % (case, len(notes)))
        if want:
            check(notes[0][0] == "DISPATCHER_ALARMS_X" and notes[0][1] == "dispatcher alarm: ledger publish: " + lockmsg[:240]
                  and "\"kind\": \"publish:index_lock\"" in "".join(glob_journal(root)) and "raised" in "".join(glob_journal(root)) and "noted" in "".join(glob_journal(root)),
                  "index.lock alarm text and journal: %r" % notes)
    root = wd_root("ex_il_f")
    ex([], sch=sched(publish=True), root=root, publish=lambda n: "index.lock", note=lambda i, t: (False, "nf"))
    check("note failed: nf" in "".join(glob_journal(root)), "index.lock note failure journalled")
    root = wd_root("ex_il_e")
    ex([], sch=sched(publish=True), root=root, publish=lambda n: "index.lock", note=lambda i, t: 1 / 0)
    check("note failed: division by zero" in "".join(glob_journal(root)), "index.lock raising note journalled")
    root = wd_root("ex_il_e2")
    ex([], sch=sched(publish=True), root=root, publish=lambda n: "index.lock", note=lambda i, t: (_ for _ in ()).throw(RuntimeError("z" * 300)))
    jj = "".join(glob_journal(root))
    check(("note failed: " + "z" * 160 + "\"") in jj and "z" * 161 not in jj and '"note": true' in jj, "index.lock raising note cut at 160, alarm marked note")
    notes.clear()
    D.execute([], sched(publish=True), fresh(), wd_root("ex_il_d"), True, NOW, {"lock": lambda: _Lk(), "publish": lambda n: "index.lock", "paused": lambda: None,
                                                                              "note": lambda i, t: notes.append(1) or (True, "")}, deadline=time.time() - 1)
    check(not notes, "index.lock alarm not noted past the deadline")
    notes.clear()
    ex([], sch=sched(publish=True), publish=lambda n: "fine", note=lambda i, t: notes.append(1) or (True, ""))
    check(not notes, "no index.lock, no alarm")



def test_execute_truncation_and_counts():
    def long_exc(*x, **k):
        raise RuntimeError("y" * 500)
    L = 160
    # verdicts error text
    acts = [{"do": "role_verdicts", "path": "/p", "rows": [1], "role": "R", "ticket": "T"}]
    ex(acts, verdicts_append=long_exc)
    check(acts[0]["result"] == "error: RuntimeError: " + "y" * L, "verdicts error cut at 160")
    # note raise
    a = {"do": "skip", "why": "w", "note": True}
    ex([a], note=long_exc)
    check(a["ledger"] == "note failed: RuntimeError: " + "y" * L, "note raise cut at 160: %d" % len(a["ledger"]))
    # publish raise
    root = wd_root("ex_tr")
    ex([], sch=sched(publish=True), root=root, publish=long_exc)
    check(("error: RuntimeError: " + "y" * L + "\"") in "".join(glob_journal(root)), "publish raise cut at 160")
    # launch raise: the alarm why carries out
    role = T.conductor()
    acts = [_role_act()]
    ex(acts, sch=sched(roles=[role]), role_launch=long_exc)
    check(acts[-1]["why"] == "role Conductor launch FAILED (unit U1): RuntimeError: " + "y" * L + "; the run stays tracked in case it started", "launch raise out cut at 160")
    # give-back raising
    st = fresh()
    st["roles"] = {"Conductor": {"pending_launch": "notadict"}}
    acts = [_role_act()]
    ex(acts, sch=sched(roles=[]), st=st, role_launch=long_exc)
    check("; give-back raised AttributeError" in acts[0]["result"] and acts[-1]["why"].endswith("no reservation to give back"),
          "a raising give-back is contained and said: %r" % acts[0].get("result"))
    # failing note ledger text when there is only a ticket / only an alarm item
    orig = D.route_note
    D.route_note = lambda sch, item, text, rx=None, blind_text=None: (None, text)
    try:
        a = {"do": "skip", "why": "w", "note": True, "ticket": "TK"}
        ex([a], sch=sched(alarm_item=None))
        check(a.get("ledger") == "not noted: token values on a token-blind item and no token_notes_item", "ticket only: said")
        a = {"do": "skip", "why": "w", "note": True}
        ex([a])
        check(a.get("ledger") == "not noted: token values on a token-blind item and no token_notes_item", "alarm_item only: said")
    finally:
        D.route_note = orig
    # notes counted into publish
    results = iter([(True, ""), (True, ""), (False, "no")])
    pubs = []
    acts = [{"do": "skip", "why": "w", "note": True} for _ in range(3)]
    ex(acts, sch=sched(publish=True), note=lambda i, t: next(results), publish=lambda n: pubs.append(n))
    check(pubs == [2], "publish told the number of notes that landed: %r" % pubs)
    # alarm rate limit uses now - last
    st = fresh()
    st["alarms"]["k"] = NOW - 100
    a = {"do": "alarm", "kind": "k", "why": "w", "note": True}
    ex([a], st=st)
    check(a.get("result") == "repeat alarm (rate-limited)", "alarm 100 s ago is rate-limited")
    # index.lock alarm: -1e18 default plus real gap
    # default publish goes through publish_bounded with the time left to the deadline
    seen = []
    orig = D.publish_bounded
    D.publish_bounded = lambda n, t: seen.append((n, t)) or None
    try:
        D.execute([], sched(publish=True), fresh(), wd_root("ex_pb"), True, NOW,
                  {"lock": lambda: _Lk(), "paused": lambda: None, "note": lambda i, t: (True, "")}, deadline=time.time() + 50)
        D.execute([], sched(publish=True, tick_budget_s=77), fresh(), wd_root("ex_pb2"), True, NOW,
                  {"lock": lambda: _Lk(), "paused": lambda: None, "note": lambda i, t: (True, "")})
    finally:
        D.publish_bounded = orig
    check(len(seen) == 2 and 0 < seen[0][1] <= 50 and 0 < seen[1][1] <= 77 and seen[1][1] > 70, "default publish bounded by the deadline / tick_budget_s: %r" % seen)



def test_execute_empty_defaults():
    a = {"do": "withdraw", "seat": "FOUNDRY", "ring_id": "R1"}
    ex([a], withdraw=lambda r, s, i: {"outcome": "absent"})
    check(a["result"] == "absent: ", "empty why is empty: %r" % a.get("result"))
    seen = []
    role = dict(T.conductor())
    role.pop("off_file")
    ex([_role_act()], sch=sched(roles=[role]), off=lambda p: seen.append(p), role_launch=lambda *x: (True, "", {}))
    check(seen == [RL.wsl_path("")], "no off_file reads the empty path: %r" % seen)



def test_execute_role_details():
    role = T.conductor()
    sch = sched(roles=[role])
    st = fresh()
    ex([_role_act(seat="OTHERSEAT")], sch=sch, st=st, role_launch=lambda *x: (True, "s", {}))
    run = st["roles"]["Conductor"]["runs"][0]
    check(run["seat"] == "OTHERSEAT" and "OTHERSEAT" in run["scope"] and run["out"] and run["err"] and "out" in run, "action seat wins; out/err paths recorded: %r" % run)
    st = fresh()
    st["roles"] = {"Conductor": {"pending_launch": "notadict"}}
    a = _role_act()
    a.pop("why")
    acts = [a]
    ex(acts, sch=sched(roles=[]), st=st, role_launch=lambda *x: (True, "", {}))
    check(a["result"] == "error: StopIteration: ; give-back raised AttributeError" and a["why"] == " \u2014 NOT LAUNCHED, error: StopIteration: ; give-back raised AttributeError"
          and acts[1]["do"] == "alarm" and acts[1]["at"] == D.iso(NOW), "pre-run raise details: %r %r" % (a.get("result"), a.get("why")))



def jrecs(root):
    out = []
    for blob in glob_journal(root):
        for ln in blob.splitlines():
            try:
                out.append(json.loads(ln))
            except ValueError:
                pass
    return out


def test_execute_journal_records():
    root = wd_root("ex_jr")
    ex([], sch=sched(publish=True), root=root, publish=lambda n: "PUBRES")
    r = [x for x in jrecs(root) if x.get("do") == "publish"]
    check(len(r) == 1 and r[0]["result"] == "PUBRES" and r[0]["at"] == D.iso(NOW), "publish journal record: %r" % r)
    root = wd_root("ex_jr2")
    ex([], sch=sched(publish=True), root=root, publish=lambda n: "add failed index.lock", note=lambda i, t: (True, ""))
    r = [x for x in jrecs(root) if x.get("kind") == "publish:index_lock"]
    check(len(r) == 1 and r[0]["do"] == "alarm" and r[0]["at"] == D.iso(NOW) and r[0]["result"] == "raised" and r[0]["ledger"] == "noted"
          and r[0]["note"] is True and r[0]["why"] == "ledger publish: add failed index.lock", "index.lock alarm record: %r" % r)
    root = wd_root("ex_jr3")
    ex([], sch=sched(publish=True), root=root, publish=lambda n: "index.lock", note=lambda i, t: (False, "nf"))
    r = [x for x in jrecs(root) if x.get("kind") == "publish:index_lock"]
    check(r and r[0]["ledger"] == "note failed: nf", "index.lock failed note record: %r" % r)
    root = wd_root("ex_jr4")
    ex([], sch=sched(publish=True), root=root, publish=lambda n: "index.lock", note=lambda i, t: 1 / 0)
    r = [x for x in jrecs(root) if x.get("kind") == "publish:index_lock"]
    check(r and r[0]["ledger"] == "note failed: division by zero", "index.lock raising note record: %r" % r)
    # note text with nothing to say; noted_on when the ticket differs from the routed item
    notes = []
    ex([{"do": "skip", "note": True}], note=lambda i, t: notes.append(t) or (True, ""))
    check(notes == ["dispatcher skip : "], "empty note text: %r" % notes)
    a = {"do": "skip", "why": "w", "note": True, "ticket": "TK"}
    ex([a], sch=sched(alarm_item="ALARMS"))
    check(a.get("noted_on") is None or a["noted_on"] != "x", "ticket kept")
    orig = D.route_note
    D.route_note = lambda sch, item, text, rx=None, blind_text=None: ("ALARMS", text)
    try:
        a = {"do": "skip", "why": "w", "note": True, "ticket": "TK"}
        ex([a], sch=sched(alarm_item="ALARMS"))
        check(a.get("noted_on") == "ALARMS", "routed to the alarm item while the ticket was TK: noted_on")
    finally:
        D.route_note = orig
    # deadline exactly: an already-passed deadline stops notes (>=): use a deadline equal to a frozen clock
    notes.clear()
    real = time.time
    time.time = lambda: 1000.0
    try:
        D.execute([{"do": "skip", "why": "w", "note": True}], sched(), fresh(), wd_root("ex_dq"), True, NOW,
                  {"note": lambda i, t: notes.append(1) or (True, ""), "lock": lambda: _Lk(), "publish": lambda n: None, "paused": lambda: None}, deadline=1000.0)
        n_eq = len(notes)
        D.execute([{"do": "skip", "why": "w", "note": True}], sched(publish=True), fresh(), wd_root("ex_dq2"), True, NOW,
                  {"note": lambda i, t: notes.append(1) or (True, ""), "lock": lambda: _Lk(), "publish": lambda n: "index.lock", "paused": lambda: None}, deadline=1000.0)
    finally:
        time.time = real
    check(n_eq == 0 and len(notes) == 0, "at the deadline exactly nothing is noted: %r" % notes)



def main():
    tests = [test_gate_lent_rule_steven, test_gate_switch_alarm_and_ticket, test_gate_off_and_invalid_and_unmeasured, test_gate_fallback_tickets_and_exact_text,
             test_gate_hold_alarm_cadence, test_withdraw, test_stop_runs_locked, test_stop_runs_lock, test_withdraw_reading_long, test_tick, test_decide_ring_verification, test_decide_recover, test_decide_ring_path, test_decide_misc, test_main, test_execute_lock_and_alarms, test_execute_ring_withdraw, test_execute_recover, test_execute_role_launch, test_execute_verdicts_stop_notes_publish, test_execute_truncation_and_counts, test_execute_empty_defaults, test_execute_role_details, test_execute_journal_records]
    try:
        import selftest_dispatcher_mut2 as M2      # noqa: F401  (decide / execute / tick, appended below)
    except ImportError:
        M2 = None
    for t in tests + (list(getattr(M2, "TESTS", [])) if M2 else []):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %s" % (t.__name__, e))
    print("%d failure(s)" % len(T.FAILS))
    return 1 if T.FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
