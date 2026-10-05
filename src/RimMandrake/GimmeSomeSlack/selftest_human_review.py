"""selftest_human_review.py -- offline checks of the Gimme Some Slack review map's LAYOUT (no bridge, no game).

    python3 src/RimMandrake/GimmeSomeSlack/selftest_human_review.py

Round 4 (owner 2026-10-04, station 26: "battery having no connection to local power pole for some reason, perhaps only
graphically. Do devices connect to power poles when not touching over some distance (as usual)?"): a Battery is a power
TRANSMITTER, and vanilla joins transmitters only by touching; the 6-cell reach (PowerConnectionMaker.ConnectMaxDist) is for
consumers. Four stations (round-2 numbers 19, 20, 26, 28; now 18, 19, 25, 27) had batteries standing off their pole or
conduit: separate, unwired nets.
  1. layout_check(station_list()) is clean (every station inside its region, spacing, links in range, batteries touching)
  2. can fail: the round-3 station 26 (now 25) battery (x 1, a one-cell gap to the mast at x 3) is reported
  3. sanity probe: a battery touching only ANOTHER battery that touches the conduit counts as joined
  4. station 20 (round-2 21) is the round-4 "over the unknown" layout: two masts in range, a solid fogged, mountain-roofed block
     between them that the straight line between the masts crosses, and no conduit through it

Style per build (owner 2026-10-04: "We should be reviewing that design, not keep doing this one."):
  5. densified 2026-10-05 (design/RimMandrake/gimmesomeslack_verification_consolidation_2026-10-05.md section 4): 33
     stations numbered 1..33, the style gallery 1-12 unmoved, every 47-map number 1-47 in the prev -> new table exactly once,
     every cut one naming live stations that still show it; can fail: a cut pointing at another cut renders '?'
     5b. HOSE STATES (16) is three parallel hoses two cells apart, flat / filling / plump; U_motion_look is a note on 1 and
     U_style_missing_art a note on M; every station has an in-world sub line (SHORT)
  6. every styled piece uses a real menu key: conduit keys from ConduitStylePicker.MenuKeys, switch/anchor/reel looks from the
     four looks; 1-4 one ground station per look; 5 covers every Modern colour entry; 6 masts, lamp masts, brackets in all
     four looks; 11 a laid and a reeled-in reel per look; 12 stores nothing
  7. merge/tie stations: the after row's runs (python twin of ConduitStyles.Components) give the expected winner (bigger run;
     tie -> older); can fail: the 7 layout with the run sizes swapped flips the winner
  8. split station: deconstructing the action cell leaves two runs of the same look; the restyle demo has NO pre-applied action
  9. art board: a slot known on disk reads own, the span cable reads fallback today; can fail: an empty texture dir makes
     every slot fall back
 10. can fail: the layout check catches a style station moved onto its neighbour and a styled cell placed on a battery
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import human_review as HR  # noqa: E402

fails = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


S = HR.station_list()
probs = HR.layout_check(S)
check(not probs, "layout_check clean over %d stations%s" % (len(S), (": " + "; ".join(probs[:4])) if probs else ""))

s26 = next(s for s in S if s["n"] == 25 and s["prev"] == 38)
old = dict(s26, devs=[("Battery", (1, 9), 0, 1.0)] + [d for d in s26["devs"] if d[0] != "Battery"])
bad = HR.battery_touch([old])
check(len(bad) == 1 and "station 25" in bad[0], "can fail: the round-3 station-26 (now 25) battery (one cell off the mast) is reported: %s" % bad)

probe = dict(n=99, conduit=[(5, 5)], wconduit=[], masts=[],
             devs=[("Battery", (4, 4), 0, 1.0), ("Battery", (3, 4), 0, 1.0), ("Battery", (0, 0), 0, 1.0)])
pb = HR.battery_touch([probe])
check(len(pb) == 1 and "(0, 0)" in pb[0], "sanity probe: chained batteries join, a lone one is reported (%s)" % pb)

s21 = next(s for s in S if s["n"] == 20 and s["prev"] == 33)
(ax, az), (bx, bz) = s21["masts"][0][1], s21["masts"][1][1]
rock = set(s21["rock"])
line = [(round(ax + (bx - ax) * t / 100.0), round(az + (bz - az) * t / 100.0)) for t in range(101)]
crosses = sum(1 for c in set(line) if c in rock)
in_range = (ax - bx) ** 2 + (az - bz) ** 2 <= HR.SPAN_RANGE ** 2
fogged = s21.get("fog", {}).get("refog") and not s21["fog"].get("unfog")
roofed = any(rd == "RoofRockThick" for rd, _ in s21.get("roof", []))
through = [c for c in s21["conduit"] if c in rock]
check(in_range and crosses >= 10 and fogged and roofed and not through and (ax, az) not in rock and (bx, bz) not in rock,
      "station 20: masts %s-%s in range %s, the line crosses %d block cells, fogged %s, mountain roof %s, conduit through it %d"
      % ((ax, az), (bx, bz), in_range, crosses, bool(fogged), roofed, len(through)))

# ---------------------------------------------------------------------------------------------- style per build
N_CHECKS = 4
new = [s for s in S if s["n"] <= 12]
check([s["n"] for s in S] == list(range(1, 34)) and [s["n"] for s in new] == list(range(1, 13)) and
      all(s.get("style_station") and s["prev"] == s["n"] for s in new),
      "33 stations numbered 1..33; the style gallery is 1-12 and kept its numbers")
KEPT = list(range(1, 13)) + [18, 22, 23, None, 30] + list(range(31, 47))
CUT = {13, 14, 15, 16, 17, 19, 20, 21, 24, 25, 26, 27, 28, 29, 47}          # the doc's section-4 list (15 stations)
check([s["prev"] for s in S] == KEPT and set(HR.CUTS) == CUT and S[15]["title"] == "HOSE STATES",
      "kept 47-map stations in order %s..., 16 is the new HOSE STATES, CUTS == the doc's 15" % KEPT[12:18])
tab = HR.renumber_table(S)
olds = [o for o, _, _ in tab if o]
cut_rows = [(o, txt) for o, n, txt in tab if o and not n]
check(olds == list(range(1, 48)) and {o for o, _ in cut_rows} == CUT and
      all(("removed -> covered by " in x or "merged into " in x) and "?" not in x.split("(")[0] for _, x in cut_rows)
      and [n for o, n, _ in tab if not o] == [16],
      "prev -> new table: every 47-map number once, %d cut rows each naming live stations, one new row (16)" % len(cut_rows))
txt = dict((o, x) for o, _, x in tab)
check(txt[47].startswith("merged into 30") and txt[24].startswith("merged into 16") and txt[28].startswith("removed -> covered by 17"),
      "47 -> merged into 30, 24 -> merged into 16, 28 -> covered by 17 (the hose grid)")
saved = HR.CUTS[13]
HR.CUTS[13] = ("removed", [14], "probe")
bad_tab = dict((o, x) for o, _, x in HR.renumber_table(S))
HR.CUTS[13] = saved
check(bad_tab[13].startswith("removed -> covered by ?"), "can fail: a cut pointing at another cut station renders '?' (%s)" % bad_tab[13][:40])
by = {s["n"]: s for s in S}
s16 = by[16]
zs = [h["reel"][1] for h in s16["hoses"]]
check([h["state"] for h in s16["hoses"]] == ["Flat", "Filling", "Plump"] and sorted(zs) == [1, 3, 5] and
      all(h["reel"][0] == 0 and h["far"][1] == h["reel"][1] for h in s16["hoses"]) and len({h["far"][0] for h in s16["hoses"]}) == 1,
      "16 HOSE STATES: three parallel hoses two cells apart, flat / filling / plump")
check(any("U_motion_look" in x for x in by[1]["notes"]) and not any(by[n]["notes"] for n in range(2, 34)) and
      any("U_style_missing_art" in x for x in HR.BOARD_NOTES) and set(HR.SHORT) == set(by),
      "U_motion_look is a note on 1 only, U_style_missing_art on M; every station has an in-world sub line")
check(HR.REGION[0] > 8 and HR.STALE_WEST[0] + HR.STALE_WEST[2] == HR.REGION[0] and
      by[13]["origin"] == (HR.COL_X, HR.COL_Z[13]) and by[13]["title"] == "WALL + ROCK ENTRIES",
      "south region shrank to x %d+ (the old west strip is still cleared); 13 WALL + ROCK in the new column" % HR.REGION[0])
N_CHECKS += 8

bad_keys = []
for s in new:
    for kind, d, key, c in s["styled"]:
        ok = key in HR.CONDUIT_KEYS if d == "PowerConduit" else (d == "PowerSwitch" and key in HR.LOOKS)
        if not ok:
            bad_keys.append((s["n"], d, key))
    for m in s["masts"]:
        if len(m) > 3 and m[3] not in HR.LOOKS:
            bad_keys.append((s["n"], m[0], m[3]))
    for h in s["hoses"]:
        if h.get("look") and h["look"] not in HR.LOOKS:
            bad_keys.append((s["n"], "reel", h["look"]))
check(not bad_keys, "every styled piece uses a real menu key / look (%s)" % bad_keys[:3])
check([s.get("look") for s in new[:4]] == list(HR.LOOKS) and
      all({k for _, d, k, _ in s["styled"] if d == "PowerConduit"} == {HR.GROUND_KEY[s["look"]]} for s in new[:4]),
      "1-4: one ground station per look, each built in its own key only")
s5 = new[4]
check({k for _, _, k, _ in s5["styled"]} == {k for k in HR.CONDUIT_KEYS if k.startswith("Modern_")},
      "5: every Modern colour entry of the conduit menu (mix, one per run, 5 colours)")
s6 = new[5]
per = {}
for m in s6["masts"]:
    per.setdefault(m[0], set()).add(m[3])
check(per == {d: set(HR.LOOKS) for d in ("RM_AerialMast", "RM_AerialLampMast", "RM_AerialWallBracket")} and len(s6["links"]) == 12,
      "6: mast, lamp mast and bracket in all four looks, 12 spans")
s11 = new[10]
check({h["look"] for h in s11["hoses"] if not h.get("reelin")} == set(HR.LOOKS) and
      {h["look"] for h in s11["hoses"] if h.get("reelin")} == set(HR.LOOKS), "11: a laid and a reeled-in reel per look")
s12 = new[11]
check(s12.get("legacy_set") and not s12["styled"] and all(len(m) < 4 for m in s12["masts"]) and not any(h.get("look") for h in s12["hoses"]),
      "12: the older-save set stores nothing (no styled piece)")
N_CHECKS += 6

s7, s8 = new[6], new[7]
for st_, want in ((s7, "Industrial"), (s8, "Scrapper")):
    runs = HR.runs_before_action(st_, 0)
    w = HR.bridge_winner(runs)
    check(len(runs) == 2 and HR.look_of_key(w["keys"][0]) == want == st_["expect"]["winner"],
          "%d: after row joins runs %s -> %s wins" % (st_["n"], sorted(r["size"] for r in runs), HR.look_of_key(w["keys"][0])))
sizes = sorted(r["size"] for r in HR.runs_before_action(s8, 0))
check(sizes[0] == sizes[1], "8 is a real tie (%s)" % sizes)
swapped = dict(s7, styled=[(k, d, "Modern_Orange" if key == "Industrial" else "Industrial" if key == "Modern_Orange" else key, c)
                           for k, d, key, c in s7["styled"]])
check(HR.look_of_key(HR.bridge_winner(HR.runs_before_action(swapped, 0))["keys"][0]) == "Modern",
      "can fail: 7 with the looks swapped between the two run sizes flips the winner to Modern")
N_CHECKS += 4

s9, s10 = new[8], new[9]
cut = s9["actions"][0][1]
cells = [(c, k, i) for i, (_, _, k, c) in enumerate(s9["styled"]) if c[1] == 0 and c != cut]
halves = HR.plan_runs(cells)
check(s9["actions"][0][0] == "D" and len(halves) == 2 and all(r["keys"] == ["Industrial"] for r in halves),
      "9: deconstructing %s leaves %d runs, all Industrial" % (cut, len(halves)))
check(not s10["actions"] and len({k for _, _, k, _ in s10["styled"]}) == 1 and any(len(m) > 3 for m in s10["masts"]),
      "10: restyle demo is one Scrapper run with a styled pole and NO pre-applied action")
N_CHECKS += 2

slots = dict(HR.art_slots())
check(slots["power mast"]["Scrapper"][0] == "own" and slots["hose reel, laid"]["Futuristic"][0] == "own",
      "art board sanity probe: Scrapper mast and Futuristic laid reel art read own")
check(slots["overhead span cable"]["Industrial"][0].startswith("fallback") and HR.art_missing(HR.art_slots()),
      "art board: the span cable falls back today and the board is not empty")
import tempfile  # noqa: E402
empty = HR.art_slots(tempfile.mkdtemp())
check(all(v[0] != "own" for _, r in empty for v in r.values()), "can fail: an empty texture dir makes every slot fall back")
N_CHECKS += 3

moved = [dict(s, origin=(s["origin"][0] - 4, s["origin"][1])) if s["n"] == 2 else s for s in S]
pr = HR.layout_check(moved)
check(any("stations 1 and 2" in p for p in pr), "can fail: station 2 moved 4 cells toward 1 is reported (%s)" % pr[:1])
s1 = dict(new[0], styled=new[0]["styled"] + [("C", "PowerConduit", "Scrapper", (0, 4))])
pr = HR.layout_check([s1 if s["n"] == 1 else s for s in S])
check(any("sits on a device" in p for p in pr), "can fail: a styled cell on station 1's battery is reported")
N_CHECKS += 2

# ---------------------------------------------------------------------------------------------- carry stations 30-33 (S5)
carry = [by.get(n) for n in range(30, 34)]
check(all(carry) and [s["title"] for s in carry] == ["DEPLOY BY HAND, THEN WIND IT IN", "DROPPED HALFWAY", "INTO THE POND", "ON THEIR TANK"]
      and all(s["row"] == "G" and s.get("region") == 2 for s in carry) and max(by) == 33 and [s["prev"] for s in carry] == [43, 44, 45, 46],
      "carry stations 30-33 (were 43-46) follow the relay (29) in row G, region 2, in the design's order")
check(by[30].get("hook") == "hose_by_hand_hook" and by[30].get("deploy_order") and "press Retract" in by[30]["what"]
      and any("Stored" in x for x in by[30]["notice"]) and by[31].get("hook") == "hose_dropped_hook"
      and all(by[n].get("hook") in HR.HOOKS for n in (21, 22, 30, 31)),
      "30 stands a colonist, orders the deploy and carries 47's Retract half; 31 stages the dropped end; every hook name resolves")
check(by[32]["terrain"] and by[32]["hoses"][0]["far"][0] >= by[32]["terrain"][0][1][0]
      and any(h[0] == "RM_LiquidTank" for h in by[33]["hostile"]),
      "32 lays into water, 33 ends at a hostile-faction tank")
bad = dict(by[32], hoses=[dict(by[32]["hoses"][0], far=(0, 0))], terrain=by[32]["terrain"])
check(not (bad["hoses"][0]["far"][0] >= bad["terrain"][0][1][0]),
      "can fail: station 32 with its hose end back on the bank is not 'in the water'")
N_CHECKS += 4

print("%d/%d checks passed" % (N_CHECKS - len(fails), N_CHECKS))
sys.exit(1 if fails else 0)
