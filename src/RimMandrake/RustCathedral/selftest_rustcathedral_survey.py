"""selftest_rustcathedral_survey.py -- the Imperial survey on the plates (CATHEDRAL_SURVEY_MISDIRECTION_QUEST_1), offline.

Drives gm_blackboard_shadow.ShadowBlackboard.poll() through its FixtureBridge over the ordinary-play fixture
(fixtures/cathedral_survey_ordinary_play.json: a clan on Rust Cathedral ground sells two kyber crystals on day 5,
two more a month later) with a simulated player answering each hail, and reads the shipped mod
(src/RimUtinni/CathedralPass) for what no fixture can show. One block per line of the item's verify:

  1 pursuit spine  the hail fires only while the Empire is looking (Heat >= the low band) on Cathedral ground; never
                   at low Heat, never off Cathedral ground, never after full discovery; at most one a month. The quest's
                   faction is the pursuit spine's own (EmpirePursuit's PursuitFaction, else vanilla Empire): the mod
                   ships no FactionDef, and the reflection names it binds exist in EmpirePursuit's source.
  2 (b)            the guild's answer: Regard up by the large gain on the poll it is read, Heat identical poll for poll
                   against the same run with the hail left to lapse (K2); read once, however long the row stays
  3 (c)            pointing them at the plates: exposure pressure up on that poll, Heat identical, Regard not raised
  (a)              no answer (refused or lapsed): nothing moves against the survey-disabled control
  4 linter         every string the survey can show passes cathedral_arc_lint at every stage -1..3, the linter read
                   all of them, and planted lines that explain what the clan protected are refused
  5 Oracle-absent  the survey path runs with no `claude` on PATH, starts no process, and every hail carries the
                   shipped def text; every branch ends in a shipped letter
  plus             the C# toggle mirror, hidden quest (no Quests-tab verdict), and the quest's signal wiring
Prints the dialog and each branch's letter exactly as the player reads them (fallback text, no LLM).
"""
# selftest temp containment (same idiom as selftest_rustcathedral_offers.py)
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_rustcathedral_survey_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import copy
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(HERE, "..", "Utils")
FIXTURE = os.path.join(UTILS, "fixtures", "cathedral_survey_ordinary_play.json")
MOD = os.path.join(REPO, "src", "RimUtinni", "CathedralPass")
QUEST_XML = os.path.join(MOD, "Defs", "QuestScriptDefs", "RUT_CathedralSurveyMisdirection.xml")
INCIDENT_XML = os.path.join(MOD, "Defs", "IncidentDefs", "RUT_CathedralSurvey.xml")
LETTER_XML = os.path.join(MOD, "Defs", "LetterDefs", "RUT_CathedralSurvey.xml")
SURVEY_CS = os.path.join(MOD, "Source", "CathedralSurvey.cs")
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
OFFERS = G.load_cathedral_offer_catalogue()
SURVEY = G.load_cathedral_survey_catalogue()
with open(FIXTURE, encoding="utf-8") as _f:
    ORDINARY = json.load(_f)


def fixture(responses=None, changes=None, state=None, polls=None):
    fx = copy.deepcopy(ORDINARY)
    if responses is not None:
        fx["player"]["survey_responses"] = responses
    if changes is not None:
        fx["changes"] = changes
    if state:
        fx["state"].update(state)
    if polls:
        fx["polls"] = polls
    return fx


def run(fx, **board_kw):
    log = tempfile.mktemp(suffix=".jsonl")
    board = G.ShadowBlackboard(log, offer_catalogue=OFFERS, survey_catalogue=SURVEY, **board_kw)
    rb = G.FixtureBridge(fx)
    recs = []
    for _ in range(fx["polls"]):
        r = board.poll(rb)
        rb.observe(r, OFFERS)
        recs.append(r)
        G.safe_call(rb, "rimworld/step_game_ticks", {"ticks": fx["tick_step"]})
    return board, recs


def events(recs, kind):
    return [(r["poll"], e) for r in recs for e in r["would_fire"] if e["type"] == kind]


def series(recs, key):
    return [r[key] for r in recs]


def first_diff(a, b):
    return next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), None)


def show_row(r, note=""):
    s = r["cathedral_survey"]
    print("      poll %3d  day %5.2f  heat %6.2f  regard %6.2f  exposure %6.2f  survey %-5s %-26s %s"
          % (r["poll"], r["ticksGame"] / 60000.0, r["heat_after"], r["cathedral_regard_after"],
             r["exposure_pressure_after"], s["open"], s["closed_reason"] or "", note))


def criterion_1_pursuit_spine():
    print("\n[1] fires from the pursuit spine dressing, without inventing a faction")
    board, recs = run(fixture(["dull", "lapse"]))
    offers = events(recs, "cathedral_survey_offer")
    for p, _ in offers:
        show_row(recs[p - 1], "<- hail fired")
    check("1a the ordinary-play clan is hailed twice in 40 days (day 5 and a month later)", len(offers) == 2,
          [p for p, _ in offers])
    check("1b every hail fires with Heat at or over the pursuit band, on Cathedral ground",
          all(e["heat_at_offer"] >= G.CATHEDRAL_SURVEY_MIN_HEAT and recs[p - 1]["cathedral_ground_presence"]
              for p, e in offers))
    before = [r for r in recs if r["poll"] < offers[0][0]]
    check("1c before the sale (Heat under the band) no hail, closed as heat_below_pursuit_band",
          before and all(r["cathedral_survey"]["closed_reason"] == "heat_below_pursuit_band" for r in before))
    gap = (recs[offers[1][0] - 1]["ticksGame"] - recs[offers[0][0] - 1]["ticksGame"]) / 60000.0
    check("1d the second hail waits out the month (%.1f days apart)" % gap, gap >= 30)
    check("1e the hail fires the shipped GiveQuest incident for the shipped quest",
          all(e["incident_def"] == "RUT_GiveQuest_CathedralSurveyMisdirection"
              and e["quest_def"] == "RUT_CathedralSurveyMisdirection" for _, e in offers))

    _, quiet = run(fixture(["dull"], changes={}))
    check("1f no kyber sale = Heat never over the band = no survey, all 40 days",
          not events(quiet, "cathedral_survey_offer"))
    _, away = run(fixture(["dull"], state={"mapBiome": "RM_BlackDunes", "settlement": "Utinni landing (dunes)"}))
    check("1g the same sale off Cathedral ground: no survey (it works Cathedral-adjacent ground)",
          not events(away, "cathedral_survey_offer")
          and any(r["cathedral_survey"]["closed_reason"] == "not_on_cathedral_ground" for r in away))
    _, off = run(fixture(["dull"]), survey_enabled=False)
    check("1h the survey toggle off: never fires", not events(off, "cathedral_survey_offer"))

    log = tempfile.mktemp(suffix=".jsonl")
    b = G.ShadowBlackboard(log, offer_catalogue=OFFERS, survey_catalogue=SURVEY)
    b.full_discovery = True   # the Empire has already found the place: there is nothing left to steer it from
    rb = G.FixtureBridge(fixture(["dull"]))
    fired = 0
    for _ in range(40):
        r = b.poll(rb)
        fired += len([e for e in r["would_fire"] if e["type"] == "cathedral_survey_offer"])
        G.safe_call(rb, "rimworld/step_game_ticks", {"ticks": 15000})
    check("1i after full discovery: no survey (closed full_discovery)", fired == 0
          and r["cathedral_survey"]["closed_reason"] in ("full_discovery", "heat_below_pursuit_band"))

    # no faction is invented: the mod ships no FactionDef, and the C# resolves the pursuit spine's own faction
    factiondefs = [os.path.join(d, f) for d, _, fs in os.walk(os.path.join(MOD, "Defs")) for f in fs
                   if f.endswith(".xml") and "<FactionDef" in open(os.path.join(d, f), encoding="utf-8").read()]
    check("1j CathedralPass ships no FactionDef", not factiondefs, factiondefs)
    cs = open(SURVEY_CS, encoding="utf-8").read()
    ladder = open(os.path.join(REPO, "src", "RimUtinni", "EmpirePursuit", "Source", "EmpireLadder.cs"), encoding="utf-8").read()
    pursuit = open(os.path.join(REPO, "src", "RimUtinni", "EmpirePursuit", "Source", "RuthlessPursuingMechanoids.cs"),
                   encoding="utf-8").read()
    check("1k the C# binds EmpireSearch.Part / ScenPart_RuthlessPursuingMechanoids.PursuitFaction, falls back to Faction.OfEmpire",
          '"RuthlessPursuingMechanoids.EmpireSearch"' in cs and '"Part"' in cs and '"PursuitFaction"' in cs
          and "Faction.OfEmpire" in cs)
    check("1l those names exist in EmpirePursuit's source (a renamed member would silently fall back)",
          re.search(r"public static class EmpireSearch\b", ladder) is not None
          and re.search(r"public static ScenPart_RuthlessPursuingMechanoids Part\b", ladder) is not None
          and re.search(r"class ScenPart_RuthlessPursuingMechanoids\b", pursuit) is not None
          and re.search(r"\bFaction PursuitFaction\b", pursuit) is not None
          and "namespace RuthlessPursuingMechanoids" in ladder)
    return recs


def criterion_2_dull_answer():
    print("\n[2] (b) the guild's answer: Regard up in shadow mode, Heat not at all (K2)")
    _, dull = run(fixture(["dull", "dull"]))
    _, lapse = run(fixture(["lapse", "lapse"]))
    ans = events(dull, "cathedral_survey_answered")
    p = ans[0][0]
    for r in dull[p - 2:p + 1]:
        show_row(r, "<- answered: guild's answer" if r["poll"] == p else "")
    check("2a the answer is read off the quest list as EndedSuccess = dull_answer",
          ans and ans[0][1]["state"] == "EndedSuccess" and ans[0][1]["outcome"] == "dull_answer")
    check("2b that poll's record carries the Regard gain (%.1f)" % G.CATHEDRAL_REGARD_GAIN_MISDIRECTION_SUCCESS,
          dull[p - 1]["survey_regard_gain_this_poll"] == G.CATHEDRAL_REGARD_GAIN_MISDIRECTION_SUCCESS)
    d = first_diff(series(dull, "cathedral_regard_after"), series(lapse, "cathedral_regard_after"))
    check("2c Regard first differs from the lapse run on that same poll, by +%.1f"
          % G.CATHEDRAL_REGARD_GAIN_MISDIRECTION_SUCCESS,
          d == p - 1 and abs(dull[d]["cathedral_regard_after"] - lapse[d]["cathedral_regard_after"]
                             - G.CATHEDRAL_REGARD_GAIN_MISDIRECTION_SUCCESS) < 1e-6,
          (d, p))
    check("2d the gain is 'large': at least two missions' worth and more than the TOLERATED gap a sale opens",
          G.CATHEDRAL_REGARD_GAIN_MISDIRECTION_SUCCESS >= 2 * G.CATHEDRAL_REGARD_GAIN_MISSION_COMPLETION
          and G.CATHEDRAL_REGARD_GAIN_MISDIRECTION_SUCCESS > 2 * G.CATHEDRAL_REGARD_LOSS_PER_KYBER_SALE)
    check("2e K2: Imperial Heat identical poll for poll, all %d polls" % len(dull),
          series(dull, "heat_after") == series(lapse, "heat_after"))
    check("2f K2: Hutt Interest and the orbital timer identical too",
          series(dull, "hutt_interest_after") == series(lapse, "hutt_interest_after")
          and series(dull, "orbital_timer_after") == series(lapse, "orbital_timer_after"))
    check("2g the two dull answers are credited exactly twice over 160 polls (an ended row is read once)",
          len(ans) == 2 and sum(r["survey_regard_gain_this_poll"] for r in dull)
          == 2 * G.CATHEDRAL_REGARD_GAIN_MISDIRECTION_SUCCESS)
    # a save that already holds an answered survey, with the story flag saying so: credited once, not twice
    fx = fixture(["lapse"])
    fx["existing_quests"] = [{"id": 5, "name": "An Imperial Survey On The Plates",
                              "root": "RUT_CathedralSurveyMisdirection", "state": "EndedSuccess", "historical": True}]
    flags = {"assailant_mission_completions": 0, "restore_choice_made": False,
             "misdirection_quest_success": True, "reveal_beat_fired": False}
    b, recs = run(fx, story_flags=flags)
    check("2h an answer from before the run is credited once (story flag), never again off the quest list",
          b.survey_history_seeded == 1 and sum(r["survey_regard_gain_this_poll"] for r in recs) == 0
          and recs[0]["story_beat_gain_this_poll"] == G.CATHEDRAL_REGARD_GAIN_MISDIRECTION_SUCCESS)


def criterion_3_pointed():
    print("\n[3] (c) pointing them at the plates moves exposure pressure")
    _, pt = run(fixture(["pointed", "lapse"]))
    _, lapse = run(fixture(["lapse", "lapse"]))
    ans = events(pt, "cathedral_survey_answered")
    p = ans[0][0]
    for r in pt[p - 2:p + 1]:
        show_row(r, "<- answered: told them" if r["poll"] == p else "")
    check("3a read as EndedFailed = pointed_at_anomaly",
          ans[0][1]["state"] == "EndedFailed" and ans[0][1]["outcome"] == "pointed_at_anomaly")
    d = first_diff(series(pt, "exposure_pressure_after"), series(lapse, "exposure_pressure_after"))
    rise = pt[p - 1]["exposure_pressure_after"] - lapse[p - 1]["exposure_pressure_after"]
    check("3b exposure pressure first differs on that poll, up by %.1f" % G.CATHEDRAL_EXPOSURE_GAIN_SURVEY_POINTED,
          d == p - 1 and abs(rise - G.CATHEDRAL_EXPOSURE_GAIN_SURVEY_POINTED) < 1e-6, (d, p, rise))
    check("3c it is §6.1's own number: the go-dark threshold is reachable from it",
          G.CATHEDRAL_EXPOSURE_GAIN_SURVEY_POINTED > 0 and G.CATHEDRAL_EXPOSURE_GODARK_THRESHOLD
          <= 3 * G.CATHEDRAL_EXPOSURE_GAIN_SURVEY_POINTED)
    check("3d Heat identical poll for poll", series(pt, "heat_after") == series(lapse, "heat_after"))
    check("3e Regard is not raised by it (identical while no go-dark)",
          series(pt, "cathedral_regard_after") == series(lapse, "cathedral_regard_after"))
    # a clan that points every survey it meets, with the default threshold: the place goes dark
    fx = fixture(["pointed"], polls=160)
    b, recs = run(fx, exposure_godark_threshold=15.0)
    check("3f with a low go-dark threshold one pointed survey flips the place dark (the §6.1 door opens)",
          any(r["go_dark_fired_this_poll"] for r in recs) and b.go_dark_flip_count >= 1)

    print("\n[a] no answer: refused, or left to lapse -- nothing moves")
    _, silent = run(fixture(["silent", "silent"]))
    _, off = run(fixture(["silent"]), survey_enabled=False)
    sa = events(silent, "cathedral_survey_answered")
    check("a1 a refused hail reads EndedUnknownOutcome = no_answer", sa and sa[0][1]["outcome"] == "no_answer")
    la = events(lapse, "cathedral_survey_answered")
    lp = la[0][0]
    check("a2 an ignored hail ends itself after its 2 days (%.2f days after firing)"
          % ((lapse[lp - 1]["ticksGame"] - lapse[events(lapse, "cathedral_survey_offer")[0][0] - 1]["ticksGame"]) / 60000.0),
          la and la[0][1]["outcome"] == "no_answer")
    for key in ("cathedral_regard_after", "exposure_pressure_after", "heat_after"):
        check("a3 %s identical to the survey-disabled run (refused and lapsed)" % key,
              series(silent, key) == series(off, key) == series(lapse, key))


def _strings():
    seen = []
    bad = []
    for path in (QUEST_XML, INCIDENT_XML, LETTER_XML):
        for st in (-1, 0, 1, 2, 3):
            got = []
            bad += LINT.xml_findings(path, st, got)
            if st == -1:
                seen += got
    return seen, bad


def criterion_4_linter():
    print("\n[4] all dialog passes item 3's linter; no line explains what the player protected")
    seen, bad = _strings()
    check("4a every survey string lints clean at stages -1, 0, 1, 2 and 3", not bad, bad[:3])
    hail = SURVEY["hail"]
    after = SURVEY["after"]
    want = [hail[k] for k in hail] + [a[k] for a in after.values() for k in ("label", "text")]
    norm = lambda t: re.sub(r"\s+", " ", t.replace("\\n", "\n")).strip()
    seen_n = {norm(s) for s in seen}
    check("4b the linter read all %d strings the player can be shown (hail, 3 answers, 4 letters)" % len(want),
          len(want) == 13 and all(norm(w) in seen_n for w in want), [w[:40] for w in want if norm(w) not in seen_n])
    planted = ["You kept the secret, and the Empire will never find what lies beneath.",
               "The guild's answer covered for the old works.",
               "Your misdirection worked: the survey was misled.",
               "The Cathedral is grateful.",
               "It protected you, so you protected it.",
               "The surveyors were thrown off; whatever is down there stays hidden from them.",
               "Something down there is alive, and it is pleased with you."]
    caught = [t for t in planted if LINT.findings(t, -1)]
    check("4c planted lines that explain the concealment are refused (%d/%d)" % (len(caught), len(planted)),
          len(caught) == len(planted), [t for t in planted if t not in caught])
    words = " ".join(want).lower()
    check("4d the (b) letter says what the surveyors did, never why: no 'because', 'so that', 'for its sake'",
          not re.search(r"\bbecause\b|\bso that\b|\bfor (its|their) sake\b|\bin return\b|\bgrateful\b|\bthank",
                        norm(after["AnsweredDull"]["text"]).lower()))
    check("4e no string names the place, the Empire's Heat, or a reward for loyalty",
          not re.search(r"\bcathedral\b|\bheat\b|\breward\b|\bloyal", words))


def criterion_5_oracle_absent(recs):
    print("\n[5] completes Oracle-absent with prescribed fallback text")
    env = dict(os.environ, PATH=os.pathsep.join(p for p in os.environ.get("PATH", "").split(os.pathsep)
                                                if not os.path.exists(os.path.join(p, "claude"))))
    log = tempfile.mktemp(suffix=".jsonl")
    out = subprocess.run([sys.executable, os.path.join(UTILS, "gm_blackboard_shadow.py"), "--fixture", FIXTURE,
                          "--log", log], env=env, capture_output=True, text=True, timeout=240)
    check("5a the blackboard runs the ordinary-play fixture with no `claude` on PATH",
          out.returncode == 0 and "Survey: 2 hail(s) fired" in out.stdout, (out.returncode, out.stdout[-300:],
                                                                             out.stderr[-300:]))
    src = open(os.path.join(UTILS, "gm_blackboard_shadow.py"), encoding="utf-8").read()
    survey_src = src[src.index("def observe_survey_quests"):src.index("def advance_cathedral_offers")]
    check("5b the survey path calls no LLM and starts no process",
          not re.search(r"subprocess|claude|os\.system|Popen|gpt_consult|oracle", survey_src, re.I))
    offers = events(recs, "cathedral_survey_offer")
    check("5c every hail the blackboard logs carries the shipped def text",
          offers and all(e["letter"] == SURVEY["hail"] for _, e in offers))
    q = ET.parse(QUEST_XML).getroot().find("QuestScriptDef")
    nodes = q.find("root/nodes")
    ends = {(n.findtext("inSignal") or "").strip(): (n.findtext("outcome") or "").strip()
            for n in nodes if n.get("Class") == "QuestNode_End"}
    letters = {(n.findtext("inSignal") or "").strip() for n in nodes if n.get("Class") == "QuestNode_Letter"}
    hail = next(n for n in nodes if (n.get("Class") or "").endswith("RUT_QuestNode_SurveyHail"))
    delay = next(n for n in nodes if n.get("Class") == "QuestNode_Delay")
    sig = {k: hail.findtext(k).strip() for k in ("outSignalDull", "outSignalPointed", "outSignalSilent")}
    sig["lapse"] = delay.findtext("outSignalComplete").strip()
    check("5d every branch ends the quest with its outcome: dull=Success, pointed=Fail, silent/lapse=Unknown",
          ends.get(sig["outSignalDull"]) == "Success" and ends.get(sig["outSignalPointed"]) == "Fail"
          and ends.get(sig["outSignalSilent"]) == "Unknown" and ends.get(sig["lapse"]) == "Unknown", (ends, sig))
    check("5e and each of the four sends its own shipped letter", set(sig.values()) <= letters, (sig, letters))
    check("5f the outcome names match the blackboard's reading (Success/Fail/Unknown -> dull/pointed/none)",
          G.CATHEDRAL_SURVEY_OUTCOMES == {"EndedSuccess": "dull_answer", "EndedFailed": "pointed_at_anomaly",
                                          "EndedUnknownOutcome": "no_answer"})
    check("5g the lapse delay is the 2 days the fixture and the letters assume",
          int(delay.findtext("delayTicks")) == 120000)
    check("5h hidden, auto-accepted, no 'quest available' letter: no Quests-tab row prints a verdict",
          q.findtext("defaultHidden") == "true" and q.findtext("autoAccept") == "true"
          and q.findtext("sendAvailableLetter") == "false" and q.find("expireDaysRange") is None)


def plus_wiring():
    print("\n[+] the in-game half")
    cs = open(SURVEY_CS, encoding="utf-8").read()
    mod = open(os.path.join(MOD, "Source", "CathedralPassMod.cs"), encoding="utf-8").read()
    csproj = open(os.path.join(MOD, "Source", "RimMandrake.Utinni.CathedralPass.csproj"), encoding="utf-8").read()
    check("+a CathedralSurvey.cs is compiled (csproj lists it)", '<Compile Include="CathedralSurvey.cs" />' in csproj)
    check("+b the toggle exists, is saved, shown, and gates the incident",
          "public static bool cathedralSurveyEnabled = true" in mod and '"cathedralSurveyEnabled"' in mod
          and "ref cathedralSurveyEnabled" in mod and "CathedralPassSettings.cathedralSurveyEnabled" in cs)
    inc = ET.parse(INCIDENT_XML).getroot().find("IncidentDef")
    check("+c the incident is baseChance 0, targets the home map, uses the gated worker",
          inc.findtext("baseChance") == "0" and [li.text for li in inc.findall("targetTags/li")] == ["Map_PlayerHome"]
          and inc.findtext("workerClass").endswith("IncidentWorker_GiveQuest_CathedralSurvey"))
    let = ET.parse(LETTER_XML).getroot().find("LetterDef")
    check("+d the hail's LetterDef names the class the C# defines and the part fetches it by name",
          let.findtext("letterClass") == "RimMandrake.Utinni.CathedralPass.RUT_ChoiceLetter_SurveyHail"
          and "class RUT_ChoiceLetter_SurveyHail : ChoiceLetter" in cs
          and 'GetNamed("RUT_CathedralSurveyHail")' in cs and let.findtext("defName") == "RUT_CathedralSurveyHail")
    check("+e an answer is taken once, and only while the quest runs",
          "if (answered || quest == null || quest.State != QuestState.Ongoing) return;" in cs)
    code_only = re.sub(r"//[^\n]*|/\*.*?\*/", "", cs, flags=re.S)   # comments may say what it does NOT touch
    check("+f nothing in the survey C# touches Heat, visibility or goodwill",
          not re.search(r"AdjustVisibility|Goodwill|heat|visibility", code_only, re.I))
    dll = os.path.join(MOD, "Assemblies", "RimMandrake.Utinni.CathedralPass.dll")
    blob = open(dll, "rb").read()
    check("+g the committed DLL carries the survey types",
          all(n.encode() in blob for n in ("RUT_QuestNode_SurveyHail", "RUT_QuestPart_SurveyHail",
                                           "RUT_ChoiceLetter_SurveyHail", "IncidentWorker_GiveQuest_CathedralSurvey")))


def show_player_view():
    print("\n[what the player reads] (shipped fallback text; {FACTION} is the pursuing faction's name)")
    h = SURVEY["hail"]
    print("  LETTER  %s\n  %s" % (h["letterLabel"], h["letterText"].replace("\n", "\n  ")))
    for k in ("answerDullLabel", "answerPointedLabel", "answerSilentLabel"):
        print("    [ %s ]" % h[k])
    print("    [ Postpone ]")
    for sig, branch in (("AnsweredDull", "(b)"), ("PointedThem", "(c)"), ("LeftSilent", "(a) refused"),
                        ("HailLapsed", "(a) lapsed")):
        a = SURVEY["after"][sig]
        print("\n  %s  %s\n  %s" % (branch, a["label"], a["text"].replace("\n", "\n  ")))


def main():
    recs = criterion_1_pursuit_spine()
    criterion_2_dull_answer()
    criterion_3_pointed()
    criterion_4_linter()
    criterion_5_oracle_absent(recs)
    plus_wiring()
    show_player_view()
    print("\n%d checks, %d failed" % (len(RAN), len(FAILS)))
    if FAILS:
        print("FAILED: " + ", ".join(FAILS))
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
