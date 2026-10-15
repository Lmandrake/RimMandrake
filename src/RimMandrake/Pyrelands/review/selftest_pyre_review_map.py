"""selftest_pyre_review_map.py -- offline checks of the Pyrelands review map's PLAN (no bridge, no game, writes nothing).

    python3 src/RimMandrake/Pyrelands/review/selftest_pyre_review_map.py

  1. layout_check over the real station list is clean, and so is coverage_check over FEATURES
  2. can fail: a creature pen moved next to the fire row, two stations within 2 cells, grass planted on a firebreak
     ring, a 30-character in-world title, an item placed outside its footprint -- each is reported
  3. sanity probe for the def check: every def the stations name is found (vanilla list or a <defName> under src/), and
     a misspelt def is reported
  4. coverage can fail: a feature with neither station nor reason, and one pointing at station 99, are both reported
  5. every numbered station is shown by at least one feature (no orphan station), and every pen's kind is named
  6. no flight is planned: both flyers stand in roofed pens, every flight feature has no station and a reason
  7. station_verdict: a full match passes; a missing def, a short pawn count, too little terrain each fail
  8. ops_counts reads get_terrain_batch's 'Def:x,z,w,h' ops; parse_kv reads ProbeCell's 'k=v;' text
  9. the in-world labels carry each station number exactly once; the ruin label appears only when a ruin is known
 10. COVERAGE text carries the build command, every feature, and the no-station list with reasons
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import human_review as H  # noqa: E402

fails = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


S = H.station_list()
lp, cp = H.layout_check(S), H.coverage_check(S)
check(not lp and not cp, "layout and coverage clean over %d stations / %d features%s" % (
    len(S), len(H.FEATURES), (": " + "; ".join((lp + cp)[:4])) if lp or cp else ""))

# 2 can fail
pen = next(s for s in S if s["row"] == "E")
fire = next(s for s in S if s["setup"].get("burn"))
bad = copy.deepcopy(S)
next(s for s in bad if s["n"] == pen["n"])["origin"] = (fire["origin"][0], fire["origin"][1] - 16)
got = H.layout_check(bad)
check(any("pen %d" % pen["n"] in p and "from fire station" in p for p in got),
      "can fail: pen %d moved under the fire row is reported (%d problems)" % (pen["n"], len(got)))
bad = copy.deepcopy(S)
bad[1]["origin"] = (bad[0]["origin"][0] + 13, bad[0]["origin"][1])
check(any("stations 1 and 2 closer" in p for p in H.layout_check(bad)), "can fail: two stations 1 cell apart are reported")
bad = copy.deepcopy(S)
ringed = next(s for s in bad if s["setup"].get("ring"))
ringed["setup"]["plants"] = [(H.EMBER, 0, 0, 12, 12, 1.0, 1.0)]
check(any("on its firebreak ring" in p for p in H.layout_check(bad)), "can fail: grass on a firebreak ring is reported")
bad = copy.deepcopy(S)
bad[0]["short"] = "X" * 30
check(any("title too long" in p for p in H.layout_check(bad)), "can fail: a 30-character title is reported")
bad = copy.deepcopy(S)
item_st = next(s for s in bad if s["setup"].get("items"))
item_st["setup"]["items"] = [("Steel", 10, 14, 3)]
check(any("outside its footprint" in p for p in H.layout_check(bad)), "can fail: an item at x 14 is reported")

# 3 def check
known = H.known_defs(S)
names = set().union(*[H.station_def_names(s) for s in S])
check(names and names <= known, "sanity probe: all %d station defs are known (missing: %s)" % (len(names), sorted(names - known)))
bad = copy.deepcopy(S)
bad[0]["setup"]["terrain"].append(("RM_FE_Ash_Deeep", 2, 2, 1, 1))
check(any("RM_FE_Ash_Deeep" in p for p in H.layout_check(bad, H.known_defs(bad))), "can fail: a misspelt terrain def is reported")

# 4 coverage can fail
fx = list(H.FEATURES) + [("plant", "a thing with nothing", "x", None), ("plant", "a thing at 99", "x", "99")]
got = H.coverage_check(S, fx)
check(any("neither a station nor a reason" in p for p in got) and any("99" in p for p in got),
      "can fail: an unexplained feature and a pointer to station 99 are reported")

# 5 no orphan station; every pen kind named
ref = set()
for f in H.FEATURES:
    for k in (f[3] or "").split():
        if "-" in k and k.replace("-", "").isdigit():
            a, b = k.split("-")
            ref.update(range(int(a), int(b) + 1))
        elif k.isdigit():
            ref.add(int(k))
orphans = sorted(s["n"] for s in S if s["n"] not in ref)
check(not orphans, "every station is shown by a feature (orphans: %s)" % orphans)
kinds = {k for s in S for k, *_ in s["setup"].get("pawns", [])}
want = {"RM_FireHawk", "RM_FireWasp", "RM_FurnaceBeast", "RM_Ullai", "RM_Ashwallow", "RM_Emberscythe", "RM_Sytheclaw",
        "RM_Barbslinger", "RM_Flamefang"} | set(H.CAMPAIGN)
check(want <= kinds, "the whole roster stands in a pen: 9 fire cast + %d campaign (missing %s)" % (len(H.CAMPAIGN), sorted(want - kinds)))

# 6 no flight
flyers = [s for s in S if s["setup"].get("flyer")]
check(len(flyers) == 2 and all(s["setup"].get("room") for s in flyers),
      "both flyers (%s) stand in roofed pens" % [s["short"] for s in flyers])
flight = [f for f in H.FEATURES if "flight" in f[1].lower() or "flying" in f[1].lower() or "fly frames" in f[1].lower()]
check(flight and all(not f[3] and len(f) > 4 and "owner" in f[4] for f in flight),
      "every flight feature (%d) has no station and an owner-present reason" % len(flight))

# 7 verdict
V = H.station_verdict
check(V(["A"], {"A", "B"}, ["k", "k"], ["k", "k", "j"], {"T": 5}, {"T": 9}) is True, "verdict: a full match passes")
check(not V(["A"], {"B"}, [], [], {}, {}), "verdict: a missing def fails")
check(not V([], set(), ["k", "k", "k"], ["k", "k"], {}, {}), "verdict: two of three pawns fails")
check(not V([], set(), [], [], {"T": 5}, {"T": 4}), "verdict: 4 of 5 terrain cells fails")

# 8 parsers
oc = H.ops_counts("RM_FE_Ash_Deep:0,0,4,3;WaterShallow:5,5\nRM_FE_Ash_Deep:9,9,2,1")
check(oc == {"RM_FE_Ash_Deep": 14, "WaterShallow": 1}, "ops_counts: %s" % oc)
kv = H.parse_kv("terrain=RM_FE_Ash_Deep;fertility=0.9;bonus=0.5;watered=False")
check(kv.get("fertility") == "0.9" and kv.get("terrain") == "RM_FE_Ash_Deep", "parse_kv: %s" % kv)

# 9 labels
ops = H.label_ops(S).split("\n")
titles = [ln.split("|")[2] for ln in ops]
dup = [s["n"] for s in S if sum(1 for t in titles if t.startswith("%d  " % s["n"])) != 1]
check(not dup, "each station number titles exactly one label (bad: %s)" % dup)
check(not any("SCORCHED RUIN" in t for t in titles) and
      any("SCORCHED RUIN" in ln for ln in H.label_ops(S, ruin=[30, 200, "Wall"]).split("\n")),
      "the ruin label appears only when a ruin is known")

# 10 coverage text
md = H.coverage_md(S)
nost = [f for f in H.FEATURES if not f[3]]
check(H.build_command() in md and all(f[1].replace("|", "/") in md for f in H.FEATURES)
      and "Features with no station (%d)" % len(nost) in md and all(f[4] in md for f in nost),
      "COVERAGE carries the build command, all %d features and the %d no-station reasons" % (len(H.FEATURES), len(nost)))

print("\n%d FAIL" % len(fails) if fails else "\nALL PASS")
sys.exit(1 if fails else 0)
