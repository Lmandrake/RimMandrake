"""selftest_rustcathedral_offers.py -- the Cathedral's favours (CATHEDRAL_MISSION_BOON_OFFERS_1), offline.

Drives gm_blackboard_shadow.ShadowBlackboard.poll() through its FixtureBridge (no game, no bridge) and prints one
block of rows per criterion of the item:
  1 stage gate     missions only at TOLERATED+, gravtech boons only at VOUCHED, never at WARY (ordinary-play fixture,
                   WARY -> TOLERATED -> VOUCHED); the reveal flag opens nothing by itself
  2 deniable text  every offer string lints clean (cathedral_arc_lint) at each stage it can appear in; planted
                   attributed lines are refused
  3 Heat flip      at VOUCHED a boon is offered at low Heat and withheld after a Heat rise, same stage (paired runs)
  4 go-dark        the poll the go-dark fires closes both: a posted request is withdrawn, boons shut, held shut
  5 Oracle-absent  the offer path runs with no `claude` on PATH, calls no LLM, and every offer carries its def text
  6 K2             N mission completions move Regard, not Heat (paired runs: Heat identical poll for poll)
  7 Regard         a completed mission's Regard gain is in the shadow-log record of the poll it completes
  plus             read-only guard on the quest list, and the two Mod Settings mirrors
"""
# selftest temp containment (same idiom as selftest_gm_cathedral_fall.py)
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_rustcathedral_offers_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import copy
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(HERE, "..", "Utils")
FIXTURE = os.path.join(UTILS, "fixtures", "cathedral_offers_ordinary_play.json")
FAILS, RAN = [], []


def check(name, cond, detail=""):
    RAN.append(name)
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


sys.path.insert(0, UTILS)
G = _load("gm_blackboard_shadow", os.path.join(UTILS, "gm_blackboard_shadow.py"))
LINT = _load("cathedral_arc_lint", os.path.join(HERE, "cathedral_arc_lint.py"))
CAT = G.load_cathedral_offer_catalogue()

BASE = {
    "polls": 60, "tick_step": 15000, "start_tick": 0,
    "state": {"mapBiome": "RM_RustCathedral", "tile": 678, "settlement": "Utinni landing", "trader_present": False,
              "kyber": {"Force_KyberCrystal": 6, "RUT_Mindstone": 0},
              "anomaly": {"RM_BoltShedCuriosity": 0, "RM_CoolantEelCatch": 0},
              "factions": {"Mechanoid": {"goodwill": 0, "hostile": False},
                           "RUT_Jawa_HuttCartel": {"goodwill": 0, "hostile": False}}},
    "changes": {},
    "player": {"mission_responses": ["ignore"], "accept_after_ticks": 30000, "finish_after_ticks": 60000},
}
# Comes back already respected: the §4 restore choice (+30) and three missions from before this run, so VOUCHED is
# reached on poll 6 (TOLERATED needs a 5-poll clean streak) -- a short test, not a staged shortcut past any gate.
VOUCHED_FAST = {"assailant_mission_completions": 3, "restore_choice_made": True,
                "misdirection_quest_success": False, "reveal_beat_fired": False}
NO_FLAGS = {"assailant_mission_completions": 0, "restore_choice_made": False,
            "misdirection_quest_success": False, "reveal_beat_fired": False}


def fixture(**over):
    fx = copy.deepcopy(BASE)
    for k, v in over.items():
        fx[k] = v
    return fx


def run(fx, story_flags=None, inject=None, **board_kw):
    """Poll a board through the fixture; inject(board, poll_no) may touch the board before a poll (labelled)."""
    log = tempfile.mktemp(suffix=".jsonl")
    board = G.ShadowBlackboard(log, story_flags=dict(story_flags or NO_FLAGS), offer_catalogue=CAT, **board_kw)
    rb = G.FixtureBridge(fx)
    rb.calls = []
    real_call = rb.call

    def logged(tool, params, check=True):
        rb.calls.append((tool, dict(params or {})))
        return real_call(tool, params, check)
    rb.call = logged
    recs = []
    for i in range(fx["polls"]):
        if inject:
            inject(board, i + 1)
        r = board.poll(rb)
        rb.observe(r, CAT)
        recs.append(r)
        G.safe_call(rb, "rimworld/step_game_ticks", {"ticks": fx["tick_step"]})
    return board, recs, rb


def types(r):
    return [e["type"] for e in r["would_fire"]]


def boon_state(r, short):
    return next(b["state"] for b in r["cathedral_offers"]["boons"] if b["incident_def"].endswith(short))


def row(r, note=""):
    co = r["cathedral_offers"]
    fav = [t.replace("cathedral_", "") for t in types(r) if t.startswith(("cathedral_m", "cathedral_b"))]
    print("      poll %3d  day %5.2f  stage %-9s heat %6.2f  regard %6.2f | missions %-5s %-22s | panels %-14s gravcore %-14s"
          " | %s %s" % (r["poll"], r["ticksGame"] / 60000.0, r["conduct_posture_label"], r["heat_after"],
                        r["cathedral_regard_after"], co["missions"]["open"], co["missions"]["closed_reason"] or "",
                        boon_state(r, "Panels"), boon_state(r, "Gravcore"), fav or "", note))


def criterion_1_stage_gate():
    print("\n[1] Offer appears only at the correct stage (ordinary-play fixture, WARY -> TOLERATED -> VOUCHED)")
    with open(FIXTURE, encoding="utf-8") as f:
        fx = json.load(f)
    fx["board"] = {}            # no go-dark here: criterion 4 owns it
    fx["polls"] = 200
    _, recs, _ = run(fx)
    offers_at = {"WARY": set(), "TOLERATED": set(), "VOUCHED": set()}
    prev = None
    for r in recs:
        st = r["conduct_posture_label"]
        for t in types(r):
            if t in ("cathedral_mission_offer", "cathedral_boon_offer"):
                offers_at[st].add(t)
        if st != prev or set(types(r)) & {"cathedral_mission_offer", "cathedral_boon_offer"}:
            row(r)
        prev = st
    stages = [r["conduct_posture_label"] for r in recs]
    check("1 fixture climbs WARY -> TOLERATED -> VOUCHED", "TOLERATED" in stages and "VOUCHED" in stages
          and stages.index("TOLERATED") < stages.index("VOUCHED"), stages[:3])
    check("1 WARY: no mission and no boon offered on any WARY poll", offers_at["WARY"] == set(), offers_at["WARY"])
    check("1 TOLERATED: missions offered, no boon ever", offers_at["TOLERATED"] == {"cathedral_mission_offer"},
          offers_at["TOLERATED"])
    check("1 VOUCHED: gravtech boons offered", "cathedral_boon_offer" in offers_at["VOUCHED"], offers_at["VOUCHED"])
    check("1 every WARY/TOLERATED poll shows both boons closed_stage",
          all(boon_state(r, "Panels") == boon_state(r, "Gravcore") == "closed_stage"
              for r in recs if r["conduct_posture_label"] != "VOUCHED"))
    # the reveal is knowledge, not standing: a revealed-but-WARY board offers nothing
    flags = dict(NO_FLAGS, reveal_beat_fired=True)
    _, recs2, _ = run(fixture(polls=8), story_flags=flags)
    check("1 reveal flag alone (effective_stage REVEALED, posture WARY) opens no favour",
          recs2[0]["effective_stage_label"] == "REVEALED"
          and not any(t.endswith(("mission_offer", "boon_offer")) for r in recs2 for t in types(r)))


def criterion_2_text():
    print("\n[2] Never attributed to the Cathedral before stage 3 (cathedral_arc_lint on every offer string)")
    n = 0
    for m in CAT["missions"]:
        strings = [m["quest_description"], m["arrival_letter"]["label"], m["arrival_letter"]["text"],
                   m["success_letter"]["label"], m["success_letter"]["text"], m["offer_letter_label"]] + m["quest_names"]
        for stage in (-1, 1, 2):        # missions appear at TOLERATED and VOUCHED; -1 = the strictest pre-reveal set
            bad = [(s[:40], LINT.findings(s, stage)) for s in strings if LINT.findings(s, stage)]
            check("2 %s clean at stage %d (%d strings)" % (m["quest_def"], stage, len(strings)), not bad, bad)
        n += len(strings)
    for b in CAT["boons"]:
        strings = [b["letter_label"], b["letter_text"]]
        for stage in (-1, 2):           # boons appear at VOUCHED only
            bad = [(s[:40], LINT.findings(s, stage)) for s in strings if LINT.findings(s, stage)]
            check("2 %s clean at stage %d" % (b["incident_def"], stage), not bad, bad)
        n += len(strings)
    player_text = []
    for m in CAT["missions"]:
        player_text += [m["quest_description"], m["arrival_letter"]["label"], m["arrival_letter"]["text"],
                        m["success_letter"]["label"], m["success_letter"]["text"], m["offer_letter_label"]] + m["quest_names"]
    for b in CAT["boons"]:
        player_text += [b["letter_label"], b["letter_text"]]
    all_text = " ".join(player_text).lower()
    check("2 no player-facing offer string names the place, the Assailant, or an asker (%d strings)" % len(player_text),
          len(player_text) == n and not re.search(r"cathedral|assailant|asker|\[\w+\]", all_text))
    print("      %d offer strings linted across %d missions and %d boons" % (n, len(CAT["missions"]), len(CAT["boons"])))
    # planted: the shipped def files, one attributed line each, in a temp copy
    for label, path, old, new, rule in (
        ("quest description names the place", G.CATHEDRAL_FAVOUR_DEFS[0], "The runner would not say who asked the enclaves.",
         "The Cathedral asked the enclaves.", "names-the-place"),
        ("boon letter gives the gift agency", G.CATHEDRAL_FAVOUR_DEFS[1], "There was no patrol overhead last night.",
         "It knows when the patrols are gone.", "agency before the reveal"),
        ("quest name leaks the Assailant", G.CATHEDRAL_FAVOUR_DEFS[0], "questName->The shrine-road",
         "questName->Against the Assailant", "§GM truth"),
    ):
        tmp = tempfile.mkdtemp()
        p = os.path.join(tmp, os.path.basename(path))
        with open(path, encoding="utf-8") as f:
            text = f.read()
        assert old in text, old
        with open(p, "w", encoding="utf-8") as f:
            f.write(text.replace(old, new, 1))
        got = LINT.xml_findings(p, 1)
        check("2 planted: %s -> refused (%s)" % (label, rule), any(rule in g for g in got), got)
        cli = subprocess.run([sys.executable, os.path.join(HERE, "cathedral_arc_lint.py"), "--xml", p, "--stage", "1"],
                             capture_output=True, text=True)
        check("2 planted: %s -> lint CLI exits 1" % label, cli.returncode == 1, cli.stdout[-200:])


def _fast_vouched(**over):
    return fixture(polls=over.pop("polls", 40), **over)


def criterion_3_heat():
    print("\n[3] Boon availability flips with a shadow-mode Heat change (same stage, paired runs)")
    calm = _fast_vouched()
    hot = _fast_vouched(changes={"16": {"kyber": {"Force_KyberCrystal": 4}, "trader_present": True},
                                 "17": {"trader_present": False}})
    _, L, _ = run(calm, story_flags=VOUCHED_FAST)
    _, H, _ = run(hot, story_flags=VOUCHED_FAST)
    g_l = next(r for r in L if "cathedral_boon_offer" in types(r) and boon_state(r, "Gravcore") == "open"
               and any(e.get("incident_def", "").endswith("Gravcore") for e in r["would_fire"]))
    k = g_l["poll"]
    print("    calm run (no sale):")
    for r in L[k - 4:k + 1]:
        row(r)
    print("    hot run (two kyber sold on poll 16, everything else identical):")
    for r in H[13:k + 4]:
        row(r)
    g_h = H[k - 1]
    reopen = next((r for r in H[k:] if any(e.get("incident_def", "").endswith("Gravcore") for e in r["would_fire"])), None)
    check("3 calm run: gravcore offered on poll %d at low Heat (%.2f <= ceiling 10), VOUCHED" % (k, g_l["heat_after"]),
          g_l["conduct_posture_label"] == "VOUCHED" and g_l["heat_after"] <= 10)
    check("3 hot run, same poll %d, same stage: gravcore withheld for Heat %.2f, not offered" % (k, g_h["heat_after"]),
          g_h["conduct_posture_label"] == "VOUCHED" and boon_state(g_h, "Gravcore") == "withheld_heat"
          and not any(e.get("incident_def", "").endswith("Gravcore") for e in g_h["would_fire"]))
    check("3 hot run: stage never left VOUCHED across the Heat rise",
          all(r["conduct_posture_label"] == "VOUCHED" for r in H[5:k + 4]))
    check("3 hot run: panels (ceiling 25) stay open at the same Heat",
          all(boon_state(r, "Panels") == "open" for r in H[15:k]))
    check("3 hot run: gravcore offered again once Heat cools under 10 (poll %s, Heat %s)"
          % (reopen and reopen["poll"], reopen and reopen["heat_after"]),
          reopen is not None and reopen["heat_after"] <= 10 and reopen["conduct_posture_label"] == "VOUCHED")

    # Heat in the HIGH band (>= 40): a kyber sale that size would also cost far more Regard than VOUCHED holds, so
    # this row sets Heat directly on the board (SYNTHETIC, labelled) to show what the gate does there.
    def spike(board, poll):
        if poll == 12:
            board.heat = 45.0
    _, S, _ = run(_fast_vouched(polls=14), story_flags=VOUCHED_FAST, inject=spike)
    row(S[11], "<- SYNTHETIC: board.heat set to 45 before this poll")
    check("3 synthetic high Heat (>= HEAT_HIGH_BAND) at VOUCHED: both boons withheld",
          S[11]["heat_after"] >= G.HEAT_HIGH_BAND and boon_state(S[11], "Panels") == boon_state(S[11], "Gravcore")
          == "withheld_heat" and "cathedral_boon_offer" not in types(S[11]))


def criterion_4_go_dark():
    print("\n[4] The dark flip closes both (pursuit event on Cathedral ground, go-dark threshold 15)")
    fx = _fast_vouched(polls=60)
    _, R, _ = run(fx, story_flags=VOUCHED_FAST, pursuit_event_on_poll=10, exposure_godark_threshold=15.0)
    for r in R[7:12] + R[46:52]:
        row(r)
    before, dark = R[8], R[9]
    check("4 the poll before: VOUCHED, a request posted, both boons open", before["conduct_posture_label"] == "VOUCHED"
          and before["cathedral_offers"]["missions"]["current"]["status"] == "posted"
          and boon_state(before, "Panels") == boon_state(before, "Gravcore") == "open")
    check("4 go-dark poll %d: go_dark fired" % dark["poll"], dark["go_dark_fired_this_poll"])
    check("4 go-dark poll: missions closed (reason go_dark) and the posted request withdrawn",
          dark["cathedral_offers"]["missions"]["open"] is False
          and dark["cathedral_offers"]["missions"]["closed_reason"] == "go_dark"
          and "cathedral_mission_offer_withdrawn" in types(dark)
          and dark["cathedral_offers"]["missions"]["current"] is None)
    check("4 go-dark poll: both boons closed_go_dark, nothing offered",
          boon_state(dark, "Panels") == boon_state(dark, "Gravcore") == "closed_go_dark"
          and not {"cathedral_mission_offer", "cathedral_boon_offer"} & set(types(dark)))
    hold = [r for r in R[10:] if r["ticksGame"] - dark["ticksGame"] < G.CATHEDRAL_FAVOURS_DARK_HOLD_TICKS]
    check("4 dark hold: %d polls (%.0f days) with no offer, though posture re-climbs to %s" % (
        len(hold), G.CATHEDRAL_FAVOURS_DARK_HOLD_TICKS / 60000, hold[-1]["conduct_posture_label"]),
        hold and not any(t.endswith(("mission_offer", "boon_offer")) for r in hold for t in types(r)))
    after = R[10 + len(hold):]
    check("4 after the hold, favours reopen", any("cathedral_mission_offer" in types(r) for r in after))
    check("4 the withdrawn request lapsed in the quest list too (no letter)",
          any(q["state"] == "EndedOfferExpired" for q in dark["mission_quests"]) or
          any(q["state"] == "EndedOfferExpired" for q in R[10]["mission_quests"]))


def criterion_5_oracle_absent():
    print("\n[5] Every beat completes Oracle-absent (no claude on PATH, no LLM call in the offer path)")
    empty_bin = tempfile.mkdtemp()
    env = dict(os.environ, PATH=empty_bin)
    check("5 child PATH resolves no `claude`", shutil.which("claude", path=env["PATH"]) is None)
    log = tempfile.mktemp(suffix=".jsonl")
    p = subprocess.run([sys.executable, os.path.join(UTILS, "gm_blackboard_shadow.py"), "--fixture", FIXTURE,
                        "--log", log], env=env, capture_output=True, text=True, timeout=300)
    check("5 fixture run exits 0 with the Oracle absent", p.returncode == 0, p.stderr[-400:])
    recs = [json.loads(ln) for ln in open(log, encoding="utf-8")] if os.path.exists(log) else []
    offers = [e for r in recs for e in r["would_fire"] if e["type"] in ("cathedral_mission_offer", "cathedral_boon_offer")]
    texts = {m["quest_description"] for m in CAT["missions"]} | {b["letter_text"] for b in CAT["boons"]}
    check("5 %d offers logged, every one carrying its full shipped def text" % len(offers),
          offers and all(e["letter"]["text"] in texts and e["letter"]["label"] for e in offers))
    src = open(os.path.join(UTILS, "gm_blackboard_shadow.py"), encoding="utf-8").read()
    cs = open(os.path.join(HERE, "..", "..", "RimUtinni", "CathedralPass", "Source", "CathedralFavours.cs"),
              encoding="utf-8").read()
    check("5 blackboard source: no subprocess/Popen/os.system/claude call",
          not re.search(r"\bimport subprocess\b|Popen|os\.system|claude\s+-p", src))
    check("5 in-game C# (CathedralFavours.cs): no Process/claude call", not re.search(r"Process|claude", cs))
    print("      %d polls, %d offers, PATH=%s" % (len(recs), len(offers), env["PATH"]))


def criterion_6_7_k2_and_regard():
    print("\n[6] K2 anti-laundering + [7] Regard feedback (paired runs: the player completes every request vs ignores it)")
    base = fixture(polls=200, changes={"100": {"kyber": {"Force_KyberCrystal": 3}, "trader_present": True},
                                       "101": {"trader_present": False}})
    done = copy.deepcopy(base)
    done["player"]["mission_responses"] = ["complete"]
    _, C, _ = run(done)
    _, I, _ = run(base)
    comp = [r for r in C if r["mission_completions_this_poll"]]
    print("      %-5s %-9s %-11s %-11s %-11s %-11s %-12s %-12s %s" % (
        "poll", "stage", "heat before", "heat after", "heat(ctrl)", "from comp.", "regard(comp)", "regard(ctrl)", "event"))
    for r in comp:
        i, prev = I[r["poll"] - 1], C[r["poll"] - 2]
        print("      %-5d %-9s %-11.3f %-11.3f %-11.3f %-11.3f %-12.2f %-12.2f +%d completion, Regard gain %.1f in this "
              "poll's record" % (r["poll"], r["conduct_posture_label"], prev["heat_after"], r["heat_after"],
                                 i["heat_after"], r["heat_after"] - i["heat_after"], r["cathedral_regard_after"],
                                 i["cathedral_regard_after"], r["mission_completions_this_poll"],
                                 r["mission_completion_regard_gain_this_poll"]))
    print("      (heat(ctrl) = the same poll in the run where every request is ignored; 'from comp.' = the Heat the "
          "completions themselves added. Heat before -> after moves only by the %.1f/poll decay both runs share.)"
          % G.HEAT_DECAY_PER_POLL)
    n = sum(r["mission_completions_this_poll"] for r in C)
    check("6 %d missions completed, with Heat non-zero during at least one (a sale on poll 100)" % n,
          n >= 3 and any(r["heat_after"] > 0 for r in comp))
    check("6 Heat identical poll for poll across the paired runs (completions scrub zero Heat)",
          all(abs(c["heat_after"] - i["heat_after"]) < 1e-9 for c, i in zip(C, I)))
    check("6 on every completion poll the Heat change equals the no-mission run's (decay only)",
          all(abs((r["heat_after"] - C[r["poll"] - 2]["heat_after"]) - (I[r["poll"] - 1]["heat_after"]
                  - I[r["poll"] - 2]["heat_after"])) < 1e-9 for r in comp))
    gap = C[-1]["cathedral_regard_after"] - I[-1]["cathedral_regard_after"]
    check("6 Regard rose: completing run ends %.2f Regard above the ignoring run" % gap, gap > 0)
    first = comp[0]
    i_first = I[first["poll"] - 1]
    check("7 completion poll %d record: mission_completions_this_poll=1, gain %.1f = CATHEDRAL_REGARD_GAIN_MISSION_COMPLETION"
          % (first["poll"], first["mission_completion_regard_gain_this_poll"]),
          first["mission_completions_this_poll"] == 1
          and first["mission_completion_regard_gain_this_poll"] == G.CATHEDRAL_REGARD_GAIN_MISSION_COMPLETION
          and "cathedral_mission_completed" in types(first))
    d = first["cathedral_regard_delta_this_poll"] - i_first["cathedral_regard_delta_this_poll"]
    check("7 that poll's Regard delta exceeds the ignoring run's by exactly the gain (%.3f)" % d,
          abs(d - G.CATHEDRAL_REGARD_GAIN_MISSION_COMPLETION) < 1e-9)
    check("7 the completions also count toward VOUCHED (mission_completions_total)",
          C[-1]["mission_completions_total"] == n)


def guards():
    print("\n[+] read-only guard and the Mod Settings mirrors")
    rb = G.FixtureBridge(fixture())
    for action in ("accept", "end", None):
        try:
            G.safe_call(rb, "jawa/quest_lifecycle", {"action": action} if action else {})
            ok = False
        except RuntimeError:
            ok = True
        check("+ safe_call refuses jawa/quest_lifecycle action=%r" % action, ok)
    try:
        G.safe_call(rb, "jawa/storyteller_fire", {"incidentDef": CAT["boons"][0]["incident_def"]})
        ok = False
    except RuntimeError:
        ok = True
    check("+ safe_call refuses jawa/storyteller_fire (shadow mode fires nothing)", ok)
    _, R, rb2 = run(_fast_vouched(polls=40), story_flags=VOUCHED_FAST, missions_enabled=False)
    check("+ missions disabled: no request ever offered", not any("cathedral_mission_offer" in types(r) for r in R))
    check("+ shadow run made no acting call", not any(t not in G.ALLOWED_TOOLS for t, _ in rb2.calls))
    _, R, _ = run(_fast_vouched(polls=40), story_flags=VOUCHED_FAST, boons_enabled=False)
    check("+ boons disabled: no gift ever offered", not any("cathedral_boon_offer" in types(r) for r in R))


def main():
    criterion_1_stage_gate()
    criterion_2_text()
    criterion_3_heat()
    criterion_4_go_dark()
    criterion_5_oracle_absent()
    criterion_6_7_k2_and_regard()
    guards()
    print("\n%d/%d checks passed" % (len(RAN) - len(FAILS), len(RAN)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
