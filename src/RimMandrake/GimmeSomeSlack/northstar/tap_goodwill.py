#!/usr/bin/env python3
"""The goodwill half of sc_tap_theft (bar tap_steals_and_costs_goodwill): ONE daily call of the goodwill code, read three times.

Design: design/specs/2026-11-24-oversized-scenes/table.md, the sc_tap_theft row. The scene's old text read goodwill daily for two played
days, and no live row of it read goodwill at all. Here the clamp's own counter of draining ticks is put one day ahead (jawa/comp_set on
CompPowerTap.drainTicksSinceEvent), and the mod's own next event (every 250 ticks, PowerTheftConsequences.OnDrained) makes the daily
call by itself. Nothing else is forced: the mod decides who saw the clamp, whom to charge and how much.

  PT_daily_call_unseen_costs_nothing   the control: a full day owed, nobody of theirs saw the clamp; no goodwill moves
  PT_daily_call_seen_costs_goodwill    a villager of theirs saw it, a full day owed: their goodwill falls by the per-day setting, our
                                       charge counter by the same, and every other faction's goodwill is as it was
  PT_daily_call_removed_costs_nothing  a full day owed again, the clamp removed before the event: no goodwill moves

proof_all.py runs it as the block "tap_goodwill". Offline: selftest_gss_small_scenes.py plays it against a fake game and planted faults.
"""
ORIGIN = (16, 212)                  # its own plot: north of the scenes block (z to 203), clear of save_wire_down's plot (x from 60)
DAY = 60000
WINDOW = 300                        # ticks: one 250-tick event of the clamp always falls inside
COMP = "CompPowerTap"
FIELD = "drainTicksSinceEvent"
ROWS = ["PT_daily_call_unseen_costs_nothing", "PT_daily_call_seen_costs_goodwill", "PT_daily_call_removed_costs_nothing"]


def goodwills(reply):
    """{faction: goodwill} of every faction but ours, or None when the list could not be read."""
    if reply.get("success") is not True or not reply.get("factions"):
        return None
    return {"%s/%s" % (f.get("defName"), f.get("name")): f.get("goodwill") for f in reply["factions"] if not f.get("isPlayer")}


def moved(a, b):
    """{faction: [before, after]} of every goodwill that differs, or None when either read is missing."""
    if a is None or b is None:
        return None
    return {k: [a.get(k), b.get(k)] for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)}


def verdict(want, mv, charged, armed, ready, stood):
    """-> (status, class). want: {faction: fall} the read must show and nothing else. `armed`: the day was put on the clamp (read back);
    `ready`: the scene stood as staged before it (drain, witness); `stood`: the scene kept its point to the end of the window."""
    if not (ready and stood):
        return "UNMEASURED", "SITE"
    if not armed or mv is None or charged is None:
        return "UNMEASURED", "HARNESS"
    ok = {k: a - b for k, (a, b) in mv.items() if isinstance(a, int) and isinstance(b, int)} == want and len(mv) == len(want)
    return ("PASS" if ok and charged == -sum(want.values()) else "FAIL"), "MOD"


def run(B, V, rows, VA=None):
    if VA is None:
        import validation_aerial as VA
    res = {"origin": list(ORIGIN)}
    before_bulk = B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
    st = VA.theft_stage(B, rows, res, ROWS[0], clear_clamps=False)
    if st is None:
        for rid in ROWS[1:]:
            V.row(rows, rid, "UNMEASURED", "SITE", "the theft scene did not stage: see %s" % ROWS[0])
        return
    S, nf = st["scene"], st["faction"]
    clamp = (st["clamp"] or [None])[0]
    per = VA.counter_value(res["settings"].get("theftGoodwillPerDay"))
    gw = lambda: goodwills(B.call("jawa/list_factions"))                      # noqa: E731
    charged = lambda: VA._pt_stat(B, "goodwillCharged")                       # noqa: E731
    caught = lambda: VA._pt_stat(B, "caughtCount")                            # noqa: E731
    victim = "%s/%s" % (nf, (res.get("victim") or {}).get("name"))

    def tap():
        t = next((t for t in B.ap("census").get("taps") or [] if clamp is not None and str(clamp).endswith(str(t.get("id")))), None) or {}
        return float(t.get("lastStolenW") or 0)

    def arm():
        r = B.call("jawa/comp_set", thing=str(clamp), comp=COMP, member=FIELD, value=str(DAY)) if clamp is not None else {}
        return {"ok": r.get("success") is True and str(r.get("after")) == str(DAY), "reply": {k: r.get(k) for k in ("success", "before", "after", "message", "error")}}

    def read(step):
        """The daily call: the state, a day owed, `step` (a removal, or nothing), the window, the state again."""
        g0, c0, n0 = gw(), charged(), caught()
        a = arm()
        left = step()
        B.ticks(WINDOW)
        g1, c1, n1 = gw(), charged(), caught()
        return {"moved": moved(g0, g1), "charged": None if c0 is None or c1 is None else c1 - c0, "armed": a, "step": left,
                "caught": None if n0 is None or n1 is None else n1 - n0}

    try:
        # 1. nobody of theirs on the map: a full day owed and no witness
        B.ticks(60)
        w0 = tap()
        r = read(lambda: None)
        s, c = verdict({}, r["moved"], r["charged"], r["armed"]["ok"], w0 > 0, True)
        if r["caught"] and s == "PASS":
            s, c = "FAIL", "MOD"                    # no pawn of theirs stands on the map: a clamp that is caught anyway is the mod's
        V.row(rows, ROWS[0], s, c, dict(r, victim=victim, perDay=per, stolenW=w0, cleared=before_bulk.get("destroyed") is not None))
        # 2. a villager of theirs sees the clamp, then a full day owed
        n0 = caught()
        wids = VA.theft_witness(B, res, S, nf)
        B.ticks(WINDOW)
        n1, w1 = caught(), tap()
        seen = n0 is not None and n1 == n0 + 1
        # the witnesses stand in sight range and awake on their feet (read, not assumed); the mod decides whether they catch it
        reach = float(res["settings"].get("theftSightRange") or 0)
        near = [p.get("id") for p in B.call("jawa/pawn_census").get("pawns") or [] if p.get("id") in wids and not p.get("downed") and p.get("x") is not None
                and ((p["x"] - S["clamp"][0]) ** 2 + (p["z"] - S["clamp"][1]) ** 2) ** 0.5 <= reach]
        r = read(lambda: None)
        s, c = verdict({victim: per or 0}, r["moved"], r["charged"], r["armed"]["ok"] and bool(per), w1 > 0 and bool(near), True)
        V.row(rows, ROWS[1], s, c, dict(r, victim=victim, perDay=per, stolenW=w1, seenOnce=seen, witnesses=wids, witnessesInSight=near, lord=res.get("witnessLord")))
        # 3. a full day owed once more, and the clamp gone before the event
        def remove():
            B.call("jawa/destroy_batch", rects="%d,%d,1,1" % tuple(S["clamp"]), categories="All")
            return VA._pt_ids(B, "RM_PowerTapClamp", S["rect"])
        w2 = tap()
        r = read(remove)
        s, c = verdict({}, r["moved"], r["charged"], r["armed"]["ok"], w2 > 0, r["step"] == [])
        if s == "PASS" and rows[-1]["status"] != "PASS":
            s, c = "UNMEASURED", "HARNESS"          # a clamp that never charged cannot show that its removal stops the charge
        V.row(rows, ROWS[2], s, c, dict(r, victim=victim, perDay=per, stolenW=w2, clampLeft=r["step"]))
    finally:
        # the witnesses, their grid and the goodwill go back as they were
        B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % tuple(S["rect"]), categories="All")
        if isinstance(st["goodwill0"], int):
            B.call("jawa/set_faction_relation", faction=nf, goodwill=st["goodwill0"])
        B.call("jawa/map_commit")
