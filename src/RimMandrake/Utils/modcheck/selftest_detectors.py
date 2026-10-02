#!/usr/bin/env python3
"""Selftest for snapshot.py / detectors.py (north-star situational helpers).

Offline and deterministic: every bridge result comes from a fixture under
testdata/ cut from real recorded runs (E1 ShipMemory letters, E2/E3
JawaIonWeapons list_pawns, Antiquities list_things, and the 2026-10-01 live
contract probe).  Fixtures marked DERIVED in their `_source` were edited only
as the test needs (documented there).

Run: python3 src/RimMandrake/Utils/modcheck/selftest_detectors.py
"""

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import detectors as D      # noqa: E402
import snapshot as S       # noqa: E402

PASSED, FAILED = [], []


def ok(cond, label):
    print("%-4s %s" % ("ok" if cond else "FAIL", label))
    (PASSED if cond else FAILED).append(label)


def fx(name):
    with open(os.path.join(HERE, "testdata", name)) as f:
        return json.load(f)


def det(hits, name):
    return [h for h in hits if h.detector == name]


def names(hits):
    return sorted(h.detector for h in hits)


PROBE = fx("contract_probe_2026-10-01.json")["events"]


def probe_raw(prefix, pawns_key=None):
    e = PROBE
    r = {"list_pawns": e[pawns_key or prefix + "/pawns"]["result"],
         "letter_list": e[prefix + "/letters"]["result"],
         "story_stats": e[prefix + "/stats"]["result"],
         "list_things": e[prefix + "/fire"]["result"],
         "time_clock": e[prefix + "/clock"]["result"],
         "_things_query": "Fire"}
    return r


def snap_of(raw):
    return S.normalize(raw)


def base_of(raw):
    return S.Baseline(S.normalize(raw))


# ---- E1: letters ---------------------------------------------------------------------

E1 = fx("e1_letters.json")["result"]


def letters_raw(letters, tick):
    r = copy.deepcopy(E1)
    r["letters"] = [copy.deepcopy(l) for l in letters]
    r["count"] = len(letters)
    r["ticksGame"] = tick
    return {"letter_list": r, "time_clock": {"success": True, "ticksGame": tick}}


def test_e1_seven_deaths():
    base = base_of(letters_raw([l for l in E1["letters"] if l["arrivalTick"] == 0], 100))
    snap = snap_of(letters_raw(E1["letters"], 5693))
    hits = D.sweep(snap, base)
    died = det(hits, "colonist_died")
    ok(len(died) == 7, "E1 sanity: 7 real deaths -> exactly 7 aggregated colonist_died hits (got %d)" % len(died))
    ok(all(h.severity == D.FATAL for h in died), "E1: every colonist_died is FATAL")
    ok(sorted(h.evidence["name"] for h in died) ==
       sorted(["Patel", "Eve", "Dan", "Hairy", "Toad", "Dalton", "Vick"]), "E1: victim names read from 'Death: X' labels")
    ok(not [h for h in hits if h.detector == "letter_unexpected" and h.evidence["defName"] == "Death"],
       "E1: Death letters are consumed by colonist_died, not re-reported")
    ok(not [h for h in det(hits, "letter_unexpected") if "opportunity for" in h.evidence["label"]],
       "E1: companion 'opportunity for X' letters do not become extra hits")
    ok(len(det(hits, "mental_break")) == 1, "E1: 'Insulting spree' -> one mental_break hit")
    dups = [h for h in det(hits, "letter_unexpected") if h.evidence["label"] == "Area revealed"]
    ok(len(dups) == 1 and dups[0].evidence["count"] == 2,
       "same-tick duplicate letters ('Area revealed' x2 at 2105) are BOTH counted")


def test_e1_pre_baseline_letters_do_not_fire():
    pre = [l for l in E1["letters"] if l["arrivalTick"] <= 905]
    base = base_of(letters_raw(pre, 905))
    snap = snap_of(letters_raw(E1["letters"], 5693))
    died = det(D.sweep(snap, base), "colonist_died")
    ok(sorted(h.evidence["name"] for h in died) == ["Dalton", "Hairy", "Toad", "Vick"],
       "E1: deaths already in the baseline (Patel, Eve, Dan) do NOT fire; the 4 later ones do")
    base_all = base_of(letters_raw(E1["letters"], 5693))
    ok(D.sweep(snap_of(letters_raw(E1["letters"], 5693)), base_all) == [],
       "negative control: identical letters vs baseline -> zero hits")


def test_baseline_tick_boundary():
    tick = 3298
    row = [l for l in E1["letters"] if l["label"]["RawText"] == "Roof collapse" and l["arrivalTick"] == tick][0]
    base = base_of(letters_raw([row], tick))
    same = D.sweep(snap_of(letters_raw([row], tick)), base)
    ok(same == [], "letter at exactly the baseline tick that IS in the baseline does not fire")
    new = copy.deepcopy(row)
    new["label"]["RawText"] = "Roof collapse (second, different)"
    hits = det(D.sweep(snap_of(letters_raw([row, new], tick)), base), "letter_unexpected")
    ok(len(hits) == 1 and "second" in hits[0].evidence["label"], "a NEW letter at the baseline tick does fire")
    twin = copy.deepcopy(row)
    hits = det(D.sweep(snap_of(letters_raw([row, twin], tick)), base), "letter_unexpected")
    ok(len(hits) == 1 and hits[0].evidence["count"] == 1,
       "an identical twin at the baseline tick fires once (multiset: 2 now vs 1 in baseline)")


# ---- E2: Burn on a colonist -----------------------------------------------------------------

E2 = fx("e2_pawns_burn.json")["result"]


def pawns_raw(result, tick=5693):
    return {"list_pawns": result, "time_clock": {"success": True, "ticksGame": tick}}


def test_e2_burn():
    emptied = copy.deepcopy(E2)
    for p in emptied["pawns"]:
        if p["name"] == "Justice":
            p["health"]["hediffs"] = []
    base = base_of(pawns_raw(emptied))
    hits = D.sweep(snap_of(pawns_raw(E2)), base)
    inj = det(hits, "colonist_injured_unexpectedly")
    ok(len(inj) == 1 and inj[0].evidence["name"] == "Justice", "E2 sanity: Burn on Justice -> colonist_injured_unexpectedly")
    ok(inj and inj[0].evidence["cause_hint"] == "fire" and inj[0].severity == D.SURPRISE and
       len(inj[0].evidence["new_hediffs"]) == 6, "E2: cause_hint 'fire', SURPRISE, all 6 burn instances reported")
    ok(not det(hits, "colonist_died") and not det(hits, "hostile_pawns"), "E2: no unrelated hits")
    # same def on a NEW part is a new instance (diff per hediff INSTANCE, not per def)
    one = copy.deepcopy(E2)
    for p in one["pawns"]:
        if p["name"] == "Justice":
            p["health"]["hediffs"] = p["health"]["hediffs"][:5]
    hits = det(D.sweep(snap_of(pawns_raw(E2)), base_of(pawns_raw(one))), "colonist_injured_unexpectedly")
    ok(len(hits) == 1 and len(hits[0].evidence["new_hediffs"]) == 1,
       "E2: diff is per hediff instance (a 6th Burn on a new part is one new injury)")
    grown = copy.deepcopy(E2)
    for p in grown["pawns"]:
        if p["name"] == "Justice":
            p["health"]["hediffs"][1]["severity"] += 1.0
    hp = det(D.sweep(snap_of(pawns_raw(grown)), base_of(pawns_raw(E2))), "health_progression")
    ok(len(hp) == 1, "severity growth on an existing instance -> health_progression")
    unk = copy.deepcopy(E2)
    for p in unk["pawns"]:
        if p["name"] == "Justice":
            p["health"]["hediffs"].append({"def": "ZZ_Unmapped", "label": "x", "severity": 1.0,
                                           "part": "Torso", "partLabel": "torso"})
    h = det(D.sweep(snap_of(pawns_raw(unk)), base_of(pawns_raw(E2))), "colonist_injured_unexpectedly")
    ok(h and h[0].evidence["cause_hint"] == "unknown", "cause_hint is honestly 'unknown' when the table has no answer")
    ok(D.HEDIFF_CAUSE["Burn"] == "fire" and D.HEDIFF_CAUSE["Bite"] == "animal" and
       D.HEDIFF_CAUSE["Malnutrition"] == "starvation", "HEDIFF_CAUSE table carries the planned classes")
    rat = [p for p in S.normalize(pawns_raw(E2))["pawns"] if p["id"].startswith("Rat")]
    ok(rat and not D.is_colonist(rat[0]), "isPlayer is not colonist: the player-faction Rat is excluded")


# ---- E3: truncation --------------------------------------------------------------------------

E3 = fx("e3_pawns_truncated.json")["result"]
THINGS_B = fx("things_before.json")["result"]
THINGS_A = fx("things_after_urn_gone.json")["result"]


def test_e3_truncation():
    full = copy.deepcopy(E2)
    ghost = copy.deepcopy([p for p in full["pawns"] if p["name"] == "Justice"][0])
    ghost["id"], ghost["name"] = "Human53729", "Ghost"
    full["pawns"].append(ghost)
    base = base_of(pawns_raw(full))
    hits = D.sweep(snap_of(pawns_raw(E3)), base)
    lt = det(hits, "listing_truncated")
    ok(len(lt) == 1 and lt[0].severity == D.WARN, "E3 sanity: '3 beyond the limit' -> listing_truncated WARN")
    ok(not det(hits, "pawn_roster_transition") and not det(hits, "expected_contract_broken"),
       "E3: NO 'pawn missing' hit from a truncated listing")
    ok(D.sweep(snap_of(pawns_raw(E2)), base_of(pawns_raw(full)))[0].detector == "pawn_roster_transition",
       "E3 control: the same absence on a COMPLETE listing does fire pawn_roster_transition")
    msg_only = copy.deepcopy(E2)
    msg_only["message"], msg_only["truncated"] = "7 pawn(s), 2 beyond the limit.", 0
    ok(det(D.sweep(snap_of(pawns_raw(msg_only)), base), "listing_truncated"), "truncation recognised from the message alone")
    cnt_only = copy.deepcopy(E2)
    cnt_only["truncated"] = 2
    ok(det(D.sweep(snap_of(pawns_raw(cnt_only)), base), "listing_truncated"), "truncation recognised from truncated>0 alone")
    # items: truncated things listing must not report vanishing
    tb = {"list_things": THINGS_B, "_things_query": "x", "time_clock": {"ticksGame": 2698}}
    cur = copy.deepcopy(THINGS_A)
    cur["isCompleteList"] = False
    h = D.sweep(snap_of({"list_things": cur, "_things_query": "x", "time_clock": {"ticksGame": 2698}}), base_of(tb))
    ok(not det(h, "item_vanished") and det(h, "listing_truncated"), "E3: truncated things listing -> no item_vanished")
    h = D.sweep(snap_of({"list_things": THINGS_A, "_things_query": "x", "time_clock": {"ticksGame": 2698}}), base_of(tb))
    iv = det(h, "item_vanished")
    ok(len(iv) == 1 and iv[0].evidence["def"] == "RUT_Antiquity_Urn" and iv[0].evidence["after"] == 0,
       "item_vanished fires on a complete listing (total quantity per def dropped)")
    merged = copy.deepcopy(THINGS_B)
    merged["things"] = [copy.deepcopy(merged["things"][0])] * 1 + merged["things"][1:]
    merged["things"][0]["id"] = "SteamGeyser99999"      # id changed (stack merge); total unchanged
    h = D.sweep(snap_of({"list_things": merged, "_things_query": "x", "time_clock": {"ticksGame": 2698}}), base_of(tb))
    ok(not det(h, "item_vanished"), "an item ID vanishing is not a quantity vanishing (total per def unchanged)")
    q = D.sweep(snap_of({"list_things": THINGS_A, "_things_query": "y", "time_clock": {"ticksGame": 2698}}), base_of(tb))
    ok(not det(q, "item_vanished"), "item totals from different queries are never compared")


# ---- live probe (2026-10-01) ----------------------------------------------------------------------

def probe_baseline_t0():
    r = probe_raw("t0")
    r["list_pawns"] = PROBE["C_immediate_pawns"]["result"]         # post-damage health as the baseline
    return r


def test_probe_clean_control():
    raw = probe_raw("t0")
    ok(D.sweep(snap_of(raw), base_of(raw)) == [], "negative control: clean bland snapshot (live t0) vs itself -> zero hits")
    s = snap_of(raw)
    ok(len([p for p in s["pawns"] if D.is_colonist(p)]) == 3,
       "live: colonist = isPlayer AND Humanlike (the Husky is isPlayer but not a colonist)")
    ok(s["sources"]["list_pawns"]["complete"] and s["map_id"] is None, "live t0: complete listing; map_id None when not supplied")
    ok(snap_of(dict(raw, map_info=fx("contract_probe_2026-10-01.json")["baseline"]["map_info"]["result"]))["map_id"] == 0,
       "map_info.mapId feeds Snapshot.map_id")


def test_probe_kill():
    base = base_of(dict(probe_raw("t0"), list_pawns=PROBE["C_immediate_pawns"]["result"]))
    hits = D.sweep(snap_of(probe_raw("D_after_kill_nostep")), base)
    died = det(hits, "colonist_died")
    ok(len(died) == 1 and died[0].severity == D.FATAL and died[0].evidence["name"] == "Burdee",
       "probe kill: ONE colonist_died for Burdee (not three hits)")
    ok(set(died[0].evidence["sources"]) == {"pawn_row_dead", "death_letter"} and
       died[0].evidence["colonistsKilled_delta"] == 1,
       "probe kill: row + Death letter aggregated, story_stats colonistsKilled delta corroborates")
    ok(not det(hits, "letter_unexpected"), "probe kill: 'Mourning of Nature opportunity' companion letter is deduped")
    ok(not det(hits, "hostile_pawns") and not det(hits, "raid_arrived"), "probe kill: no spurious raid/hostile hits")
    litter = D.Expectations()
    litter.expect("litter", {"id": "Human696"})
    litter.expect("litter", {"name": "Burdee"})
    ok(not det(D.sweep(snap_of(probe_raw("D_after_kill_nostep")), base, litter), "colonist_died"),
       "probe kill: a declared sacrificial pawn (litter) does not fire")


def test_probe_fire():
    base = base_of(probe_raw("t0"))
    hits = D.sweep(snap_of(probe_raw("B_after60")), base)
    fire = det(hits, "fire_on_map")
    ok(len(fire) == 1 and fire[0].severity == D.SURPRISE and fire[0].focus is not None,
       "probe fire: list_things defName=Fire (4 fires) -> fire_on_map SURPRISE with a focus cell")
    ex = D.Expectations()
    ex.expect("fire", lambda t: True)
    ok(not det(D.sweep(snap_of(probe_raw("B_after60")), base, ex), "fire_on_map"), "probe fire: an expected fire is not reported")


def test_probe_damage():
    base = base_of(probe_raw("t0"))
    snap = snap_of(dict(probe_raw("t0"), list_pawns=PROBE["C_immediate_pawns"]["result"]))
    inj = det(D.sweep(snap, base), "colonist_injured_unexpectedly")
    ok(len(inj) == 1 and inj[0].evidence["name"] == "Fu" and inj[0].evidence["cause_hint"] == "weapon",
       "probe damage: jawa/damage Cut on Fu -> injured, cause_hint 'weapon' (no hostile near)")


def test_probe_raid_and_expectations():
    base = base_of(probe_raw("D_after_kill_nostep"))
    raw = probe_raw("E_after_raid_nostep")
    hits = D.sweep(snap_of(raw), base)
    raid = det(hits, "raid_arrived")
    ok(len(raid) == 1 and raid[0].evidence["hostiles_seen"] == 2 and not raid[0].evidence["open"] and
       len(raid[0].evidence["signals"]) == 2,
       "probe raid: ThreatBig letter + numRaidsEnemy delta aggregate into ONE raid_arrived, hostiles seen")
    ok(len(det(hits, "hostile_pawns")) == 1 and len(det(hits, "hostile_pawns")[0].evidence["pawns"]) == 2,
       "probe raid: 2 hostile rows -> hostile_pawns")
    ok(not det(hits, "letter_unexpected"), "probe raid: the 'Raid: Buton' letter is not double-reported")
    # a raid letter with no hostiles yet stays OPEN inside the window, closed after it
    nohost = copy.deepcopy(raw)
    nohost["list_pawns"] = copy.deepcopy(raw["list_pawns"])
    nohost["list_pawns"]["pawns"] = [p for p in nohost["list_pawns"]["pawns"] if not p["hostile"]]
    r = det(D.sweep(snap_of(nohost), base), "raid_arrived")
    ok(r and r[0].evidence["open"], "raid_arrived stays open until hostiles are seen (inside the window)")
    late = copy.deepcopy(nohost)
    late_tick = 71 + D.RAID_WINDOW_TICKS + 5
    late["time_clock"] = {"success": True, "ticksGame": late_tick}
    for k in ("list_pawns", "letter_list", "story_stats", "list_things"):
        late[k] = dict(late[k], ticksGame=late_tick)
    r = det(D.sweep(snap_of(late), base), "raid_arrived")
    ok(r and not r[0].evidence["open"], "raid_arrived closes once the window passes with no hostiles")
    # expected hostile: no presence alarm; contract broken if it then dies
    ex = D.Expectations()
    ex.expect("hostile", lambda p: p.get("hostile"))
    h1 = D.sweep(snap_of(raw), base, ex)
    ok(not det(h1, "hostile_pawns") and not det(h1, "expected_contract_broken"),
       "an expected hostile yields no hostile_pawns and no contract hit while alive")
    dead = copy.deepcopy(raw)
    for p in dead["list_pawns"]["pawns"]:
        if p["id"] == "Human45786":
            p["dead"], p["spawned"] = True, False
    h2 = D.sweep(snap_of(dead), base, ex)
    ecb = det(h2, "expected_contract_broken")
    ok(len(ecb) == 1 and ecb[0].evidence["why"] == "died", "an expected hostile that DIES fires expected_contract_broken")
    ex2 = D.Expectations()
    ex2.expect("hostile", lambda p: p.get("hostile"))
    flip = copy.deepcopy(raw)
    for p in flip["list_pawns"]["pawns"]:
        if p["id"] == "Human45788":
            p["faction"] = "PlayerColony"
    D.sweep(snap_of(raw), base, ex2)      # binds the faction at first sight
    ecb = det(D.sweep(snap_of(flip), base, ex2), "expected_contract_broken")
    ok(len(ecb) == 1 and "changed faction" in ecb[0].evidence["why"],
       "an expected hostile that changes faction fires expected_contract_broken")
    exl = D.Expectations()
    exl.expect("hostile", lambda p: p.get("hostile"), until_tick=10)
    ok(det(D.sweep(snap_of(raw), base, exl), "hostile_pawns"), "an expired expectation (until_tick) suppresses nothing")
    exp_ph = D.Expectations()
    exp_ph.expect("hostile", lambda p: p.get("hostile"), phase="act")
    exp_ph.set_phase("other")
    ok(det(D.sweep(snap_of(raw), base, exp_ph), "hostile_pawns"), "an expectation for another phase suppresses nothing")


def test_probe_mental_break():
    base = base_of(probe_raw("E_after_raid_300"))
    hits = D.sweep(snap_of(probe_raw("F_after_break")), base)
    mb = det(hits, "mental_break")
    ok(len(mb) == 1 and "Sad wander: Vas" in mb[0].evidence["label"],
       "probe mental break: NegativeEvent 'Sad wander: Vas' -> mental_break")
    ok(not det(hits, "letter_unexpected"), "probe mental break: letter consumed, not double-reported")
    ps = snap_of(probe_raw("F_after_break"))
    ok(all(p["mentalState"] is None for p in ps["pawns"]), "list_pawns rows carry no mentalState (read as None, not 'ok')")


def test_declared_raid_and_phase_bounded_hostiles():
    """A chain that fires a raid itself declares it ('raid', unbounded) and bounds its raiders by phase, so
    killing them afterwards is not a broken contract; the same raid undeclared is still a signal."""
    base = base_of(probe_raw("D_after_kill_nostep"))
    raw = probe_raw("E_after_raid_nostep")
    ex = D.Expectations()
    ex.expect("raid", {})
    ex.expect("hostile", lambda p: p.get("hostile"), phase="raid")
    ex.set_phase("raid")
    h = D.sweep(snap_of(raw), base, ex)
    ok(not det(h, "raid_arrived"), "declared raid: raid_arrived (letter + counter) is not a signal")
    ok(not det(h, "hostile_pawns"), "declared raid: the raiders are expected hostiles while the phase is open")
    ok(not det(h, "letter_unexpected"), "declared raid: its threat letter is consumed, not re-reported")
    dead = copy.deepcopy(raw)
    for p in dead["list_pawns"]["pawns"]:
        if p["hostile"]:
            p["dead"] = True
    ex.set_phase("after")
    h2 = D.sweep(snap_of(dead), base, ex)
    ok(not det(h2, "expected_contract_broken"), "killing the raiders after the phase closes is not a broken contract")
    ok(not det(h2, "raid_arrived"), "the raid stays declared after the phase moves on (the counter never resets)")
    ok(len(det(D.sweep(snap_of(raw), base), "raid_arrived")) == 1, "the same raid undeclared is still raid_arrived")


def test_induced_mental_break_is_declarable():
    """A chain that induces a break on purpose declares it; the same break unannounced is still a hit."""
    base = base_of(probe_raw("E_after_raid_300"))
    raw = probe_raw("F_after_break")
    exp = D.Expectations()
    exp.expect("mental", lambda e: "Vas" in (e.get("label") or "") or e.get("name") == "Vas")
    hits = D.sweep(snap_of(raw), base, exp)
    ok(not det(hits, "mental_break"), "declared mental: the induced break's letter is not a surprise")
    ok(not det(hits, "letter_unexpected"), "declared mental: letter consumed, not re-reported as unexpected")
    other = D.Expectations()
    other.expect("mental", lambda e: "Nobody" in (e.get("label") or ""))
    ok(len(det(D.sweep(snap_of(raw), base, other), "mental_break")) == 1,
       "a mental declaration for someone else suppresses nothing")
    ps = snap_of(raw)
    ps["pawns"] = [dict(ps["pawns"][0], id="Human9", name="Vas", mentalState="Wander_Sad")] if ps["pawns"] else \
        [{"id": "Human9", "name": "Vas", "mentalState": "Wander_Sad", "colonist": True, "faction": "PlayerColony"}]
    st = D.mental_break(ps, base, exp, {"consumed": set(), "suppressed": set()})
    ok(not [h for h in st if h.evidence.get("mentalState")], "declared mental: the induced STATE is not a hit either")
    st2 = D.mental_break(ps, base, D.Expectations(), {"consumed": set(), "suppressed": set()})
    ok([h for h in st2 if h.evidence.get("mentalState")], "undeclared: the same state is a hit")


# ---- snapshot behaviour -------------------------------------------------------------------------

class FakeSession(object):
    def __init__(self, tools, fail=()):
        self.tools, self.fail, self.calls = tools, set(fail), []

    def call(self, tool, **params):
        self.calls.append((tool, params))
        if tool in self.fail:
            raise RuntimeError("bridge down")
        return self.tools[tool]


def test_take_snapshot():
    r = probe_raw("D_after_kill_nostep")
    tools = {"jawa/" + k: v for k, v in r.items() if not k.startswith("_")}
    trip = S.take_snapshot(FakeSession(tools), "tripwire")
    ok(trip["sources"]["list_pawns"]["read"] and not trip["sources"]["alerts_list"]["read"], "tripwire tier reads only the 4 cheap sources")
    sess = FakeSession(tools)
    S.take_snapshot(sess, "tripwire")
    ok(dict(sess.calls)["jawa/list_pawns"]["includeHealth"] is False, "tripwire list_pawns is requested WITHOUT health")
    fail = S.take_snapshot(FakeSession(tools, fail={"jawa/letter_list"}), "tripwire")
    s = fail["sources"]["letter_list"]
    ok(s["read"] and not s["complete"] and "bridge down" in s["error"], "a failed read is marked complete=False + error, never raised")
    base = base_of(dict(probe_raw("t0"), list_pawns=PROBE["C_immediate_pawns"]["result"]))
    hits = D.sweep(fail, base)
    ok(det(hits, "evidence_stale") and not det(hits, "letter_unexpected"),
       "a failed letters read is never treated as 'no letters': evidence_stale, no letter hits")
    ok(S.take_snapshot(FakeSession({}, fail={"jawa/" + t for t in S.TOOLS_FULL}), "full")["tick"] is None,
       "even if every read fails take_snapshot returns (tick None) instead of raising")


def test_dedup_and_severity():
    h = D._hit("fire_on_map", "x", {"n": 1}, fp="fire:1")
    dd = D.Dedup(cooldown_ticks=600)
    ok(dd.should_capture(h, 100) and not dd.should_capture(h, 200), "Dedup: repeat of an unchanged hit inside cooldown -> no screenshot")
    ok(not dd.should_capture(h, 5000), "Dedup: unchanged hit after cooldown -> still no screenshot")
    h2 = D._hit("fire_on_map", "x", {"n": 2}, fp="fire:1")
    ok(dd.should_capture(h2, 5000), "Dedup: evidence changed after cooldown -> capture again")
    ok(dd.should_capture(D._hit("fire_on_map", "y", {}, fp="fire:2"), 5001), "Dedup: new fingerprint -> capture")
    ok(all(v in D.SEV_RANK for v in list(D.SEVERITY.values()) + list(D.LETTER_SEVERITY.values())), "SEVERITY table values are valid levels")
    ok(D.LETTER_SEVERITY["Death"] == D.SURPRISE and D.LETTER_SEVERITY["NeutralEvent"] == D.INFO, "letter severities per LetterDef")


def test_context_and_misc():
    base = base_of(probe_raw("t0"))
    cur = probe_raw("D_after_kill_nostep")
    s = S.normalize(dict(cur, _epoch=1))
    hits = D.sweep(s, base)
    ok([h.detector for h in hits] == ["map_context_changed"], "an epoch change reports only map_context_changed (baseline diffs off)")
    back = probe_raw("t0")
    back["time_clock"] = {"success": True, "ticksGame": 0}
    b2 = base_of(probe_raw("D_after_kill_nostep"))
    ok(det(D.sweep(snap_of(back), b2), "map_context_changed"), "tick going backwards is a map_context_changed (new epoch)")
    ws = fx("contract_probe_2026-10-01.json")["baseline"]["windows"]["result"]
    ws2 = copy.deepcopy(ws)
    ws2["windows"][0]["forcePause"] = True
    h = det(D.sweep(snap_of(dict(probe_raw("t0"), window_list_close=ws2)), base), "modal_open")
    ok(len(h) == 1 and not det(D.sweep(snap_of(dict(probe_raw("t0"), window_list_close=ws)), base), "modal_open"),
       "modal_open fires on a non-debug forcePause window only (the debug palette is ignored)")
    w = fx("contract_probe_2026-10-01.json")["baseline"]["weather"]["result"]
    w2 = copy.deepcopy(w)
    w2["conditions"] = [{"def": "ToxicFallout", "scope": "Map", "affectsThisMap": True, "permanent": False}]
    c = det(D.sweep(snap_of(dict(probe_raw("t0"), weather_get=w2)), base_of(dict(probe_raw("t0"), weather_get=w))), "condition_unexpected")
    ok(len(c) == 1 and c[0].severity == D.SURPRISE, "condition_unexpected: new ToxicFallout -> SURPRISE")
    w3 = copy.deepcopy(w2)
    w3["readErrors"] = ["boom"]
    ok(not det(D.sweep(snap_of(dict(probe_raw("t0"), weather_get=w3)), base_of(dict(probe_raw("t0"), weather_get=w))), "condition_unexpected"),
       "weather readErrors != empty: unread, not zero (no condition hit)")
    st = D.sweep(snap_of(dict(probe_raw("t0"), _settings={"enableStoryteller": False})),
                 base_of(dict(probe_raw("t0"), _settings={"enableStoryteller": True})))
    ok(det(st, "settings_drift"), "settings_drift fires when a recorded debug setting changed")
    anchor = (241, 177)      # the factionless Timber wolf's cell in the live probe
    h = det(D.sweep(snap_of(probe_raw("t0")), base, anchor=anchor), "strangers_near_anchor")
    ok(len(h) == 1, "strangers_near_anchor: the wolf at the anchor -> WARN (and the colony 100+ cells away is not a stranger)")
    hp = det(D.sweep(snap_of(probe_raw("E_after_raid_nostep")), base_of(probe_raw("D_after_kill_nostep")), anchor=(0, 0)), "hostile_pawns")
    ok(hp and hp[0].severity == D.SURPRISE, "hostiles near a far anchor that were not parked in the baseline stay SURPRISE")
    lg = {"success": True, "messages": [{"type": "Error", "text": "NRE in X", "repeats": 3}], "totalInBuffer": 1}
    h = det(D.sweep(snap_of(dict(probe_raw("t0"), drain_log=lg)), base), "log_errors")
    ok(len(h) == 1 and h[0].severity == D.WARN, "log_errors: a new Error message -> WARN")
    ok(S.normalize({})["tick"] is None and D.sweep(S.normalize({}), S.Baseline(S.normalize({}))) == [],
       "an all-unread snapshot yields no hits (unread is silence, not alarm)")


def test_wildlife_near_colonist():
    base = base_of(probe_raw("t0"))
    # after the wolf spawn (E_spawn_wolf put a wolf 8 cells from a colonist; a second wild wolf pre-existed)
    snap = snap_of(probe_raw("E_after_raid_300"))
    h = det(D.sweep(snap, base), "wildlife_near_colonist")
    ok(len(h) == 1, "wildlife_near_colonist fires on the live wolf spawn")
    ok(h[0].severity == D.SURPRISE and any(a["new"] for a in h[0].evidence["animals"]),
       "a wolf that arrived after the baseline escalates to SURPRISE")
    ok(not det(D.sweep(snap_of(probe_raw("t0")), base), "wildlife_near_colonist") or
       all(not a["new"] for a in det(D.sweep(snap_of(probe_raw("t0")), base), "wildlife_near_colonist")[0].evidence["animals"]),
       "pre-existing wildlife is never 'new' (no SURPRISE on the baseline itself)")
    wolf = [p for p in snap["pawns"] if p["kindDef"] == "Wolf_Timber" and p["faction"] is None][0]
    ok(wolf["hostile"] is False, "sanity: the wolf reads hostile:false, so hostile_pawns cannot be what caught it")
    exps = D.Expectations()
    exps.expect("pawn", {"id": wolf["id"]})
    h2 = det(D.sweep(snap, base, exps), "wildlife_near_colonist")
    ok(all(a["id"] != wolf["id"] for x in h2 for a in x.evidence["animals"]), "an expected animal is not reported")


def test_fixture_exempt():
    base = base_of(probe_raw("t0"))
    snap = snap_of(probe_raw("E_after_raid_300"))
    col = [p for p in snap["pawns"] if D.is_colonist(p) and not p["dead"]][0]
    before = det(D.sweep(snap_of(probe_raw("D_after_kill_nostep")), base), "colonist_died")
    ok(len(before) == 1, "sanity: the live kill fires colonist_died when nothing is expected")
    exps = D.Expectations()
    dead = [p for p in snap_of(probe_raw("D_after_kill_nostep"))["pawns"] if D.is_colonist(p) and p["dead"]][0]
    exps.expect("fixture", {"id": dead["id"]})
    exps.expect("fixture", {"name": dead["name"]})     # the Death LETTER names the pawn, not its id
    after = D.sweep(snap_of(probe_raw("D_after_kill_nostep")), base, exps)
    ok(not det(after, "colonist_died"), "a test-spawned fixture pawn's death is not a surprise")
    ok(not det(after, "expected_contract_broken"), "a fixture has no contract: its death never breaks one")
    bleed_snap = snap_of(probe_raw("B_after60", pawns_key="C_immediate_pawns"))
    bled = det(D.sweep(bleed_snap, base), "colonist_downed")
    ok(len(bled) >= 1, "sanity: the live Cut makes a colonist bleed -> colonist_downed fires")
    exps2 = D.Expectations()
    for h in bled:
        exps2.expect("fixture", {"id": h.evidence["id"]})
    ok(not det(D.sweep(bleed_snap, base, exps2), "colonist_downed"), "a fixture colonist's bleeding is not reported")


def main():
    tests = (test_e1_seven_deaths, test_e1_pre_baseline_letters_do_not_fire, test_baseline_tick_boundary,
             test_e2_burn, test_e3_truncation, test_probe_clean_control, test_probe_kill, test_probe_fire,
             test_probe_damage, test_probe_raid_and_expectations, test_probe_mental_break, test_induced_mental_break_is_declarable, test_declared_raid_and_phase_bounded_hostiles, test_wildlife_near_colonist, test_fixture_exempt,
             test_take_snapshot, test_dedup_and_severity, test_context_and_misc)
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            ok(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    n = len(PASSED) + len(FAILED)
    print()
    print("%d/%d passed" % (len(PASSED), n))
    if FAILED:
        for f in FAILED:
            print("  FAILED:", f)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
