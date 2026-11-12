"""selftest_cathedral_reveal_beat.py -- the reveal beat's trigger, once-only gate and text (CATHEDRAL_DESCENT_REVEAL_SITE_1).

Drives gm_blackboard_shadow.ShadowBlackboard.poll() through its FixtureBridge (no game, no bridge) on the ordinary-play
fixture (a colony that climbs WARY -> TOLERATED -> VOUCHED by doing the enclaves' and the Utinni's requests), and
reads the in-game half from its source and defs:
  1 gate matrix     compute_reveal_beat_gate over every posture x restore-choice x opened x revealed
  2 dev-flag matrix VOUCHED without the restore flag = no fire; the flag without VOUCHED = no fire; Regard alone
                    (forced to 1000, no missions) = no fire; both = exactly one opening, then the reveal once the party
                    reaches the bottom; descent off = never
  3 once            after the beat, the trigger set holding again is refused every poll; a demotion and re-climb opens
                    nothing; a descent quest already on the list (dev-opened) is never doubled; an unwalked descent
                    leaves stage 3 shut and is not re-opened
  4 stage 3         effective_stage is 3 from the reveal poll on and on no poll before it; knowledge_revealed is set
                    by the descent quest's success and by nothing else in the blackboard
  5 text            the opening lints clean at stage 2, the address at stage 3 (cathedral_arc_lint), both read > 0
                    strings; the address held to stage 2 is refused (the linter can tell); planted mercy/drill/place
                    lines are refused at stage 3; every [SPEAKER]/[NAME] token is one the C# fills
  6 Oracle-absent   the whole run works with no `claude` on PATH; the in-game beat calls no Oracle and no LLM
  7 player only     the beat's C# writes no faction, goodwill, trader or codex state; its defs are none of the
                    faction-visible def types; string_surface.py sees a planted FactionDef string (so its UNCHANGED
                    verdict on the item's diff means something)
"""
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_cathedral_reveal_beat_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import copy
import importlib.util
import itertools
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", ".."))
UTILS = os.path.join(SRC, "RimMandrake", "Utils")
FIXTURE = os.path.join(UTILS, "fixtures", "cathedral_offers_ordinary_play.json")
LINT_PY = os.path.join(SRC, "RimMandrake", "RustCathedral", "cathedral_arc_lint.py")
DEFS = os.path.join(HERE, "Defs", "CathedralDescent")
OPENING_XML = os.path.join(DEFS, "RUT_CathedralDescent_Opening.xml")
ADDRESS_XML = os.path.join(DEFS, "RUT_CathedralDescent_Address.xml")
CS = os.path.join(HERE, "Source", "CathedralDescent.cs")
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
LINT = _load("cathedral_arc_lint", LINT_PY)
SURF = _load("string_surface", os.path.join(HERE, "string_surface.py"))
CAT = G.load_cathedral_offer_catalogue()

FLAGS = {"assailant_mission_completions": 0, "restore_choice_made": False,
         "misdirection_quest_success": False, "reveal_beat_fired": False}


def ordinary(polls=260, missions="complete", descent="complete", refuses=0):
    with open(FIXTURE, encoding="utf-8") as f:
        fx = json.load(f)
    fx["board"] = {}
    fx["polls"] = polls
    fx.setdefault("player", {})
    fx["player"]["mission_responses"] = [missions]
    fx["player"]["descent_response"] = descent
    fx["player"]["descent_game_refuses"] = refuses
    return fx


def run(fx, restore=False, inject=None, **kw):
    flags = dict(FLAGS, restore_choice_made=restore)
    board = G.ShadowBlackboard(tempfile.mktemp(suffix=".jsonl"), story_flags=flags, offer_catalogue=CAT, **kw)
    rb = G.FixtureBridge(fx)
    recs = []
    for i in range(fx["polls"]):
        if inject:
            inject(board, i + 1)
        r = board.poll(rb)
        rb.observe(r, CAT)
        recs.append(r)
        G.safe_call(rb, "rimworld/step_game_ticks", {"ticks": fx["tick_step"]})
    return board, recs, rb


def events(recs, kind):
    return [(r["poll"], e) for r in recs for e in r["would_fire"] if e["type"] == kind]


def first_poll(recs, pred):
    return next((r["poll"] for r in recs if pred(r)), None)


def summary(label, recs):
    v = first_poll(recs, lambda r: r["conduct_posture"] == 2)
    o = [p for p, _ in events(recs, "cathedral_descent_opening")]
    rv = [p for p, _ in events(recs, "cathedral_reveal_beat")]
    s3 = first_poll(recs, lambda r: r["effective_stage"] == 3)
    gates = sorted({r["reveal_gate"] for r in recs})
    print("      %-34s first VOUCHED poll %-5s openings at %-8s reveal at %-8s first stage-3 poll %-5s gate reasons %s"
          % (label, v, o, rv, s3, gates))
    return v, o, rv, s3


def criterion_1():
    print("\n[1] gate matrix (pure function)")
    bad = []
    for posture, restore, opened, revealed, enabled in itertools.product((0, 1, 2), (False, True), (False, True),
                                                                          (False, True), (False, True)):
        may, why = G.compute_reveal_beat_gate(posture, restore, opened, revealed, enabled)
        want = posture == 2 and restore and not opened and not revealed and enabled
        if may != want:
            bad.append((posture, restore, opened, revealed, enabled, may, why))
    check("72 combinations: opens only at VOUCHED + restore choice, unopened, unrevealed, enabled", not bad, bad[:3])
    check("reasons name the missing half", G.compute_reveal_beat_gate(2, False, False, False)[1] ==
          "vouched_without_restore_choice" and G.compute_reveal_beat_gate(1, True, False, False)[1] ==
          "restore_choice_without_vouched")


def criterion_2_and_4():
    print("\n[2] dev-flag matrix on the ordinary-play fixture (missions done as offered; the party walks the descent)")
    _, recs, _ = run(ordinary(), restore=False)
    v, o, rv, s3 = summary("VOUCHED, no restore flag", recs)
    check("VOUCHED without the restore flag: VOUCHED is reached", v is not None)
    check("VOUCHED without the restore flag: no opening, no reveal, never stage 3", not o and not rv and s3 is None)

    _, recs, _ = run(ordinary(missions="ignore"), restore=True)
    v, o, rv, s3 = summary("restore flag, missions ignored", recs)
    check("restore flag without VOUCHED: VOUCHED never reached", v is None)
    check("restore flag without VOUCHED: no opening, no reveal, never stage 3", not o and not rv and s3 is None)

    def regard_alone(board, poll):
        board.cathedral_regard = 1000.0   # labelled injection: Regard as high as it can go, every poll

    _, recs, _ = run(ordinary(missions="ignore"), restore=True, inject=regard_alone)
    v, o, rv, s3 = summary("Regard forced 1000, no missions", recs)
    check("Regard alone (1000, restore flag set, no missions): no opening", not o and s3 is None)

    _, recs, _ = run(ordinary(), restore=True, descent_enabled=False)
    v, o, rv, s3 = summary("both, descent off in settings", recs)
    check("descent off: VOUCHED + flag opens nothing", v is not None and not o and s3 is None)

    board, recs, rb = run(ordinary(), restore=True)
    v, o, rv, s3 = summary("VOUCHED + restore flag", recs)
    check("both: exactly one opening, on the first VOUCHED poll", o == [v], (o, v))
    check("both: exactly one reveal, after the opening", len(rv) == 1 and rv[0] > o[0], rv)
    descent_rows = [q for q in rb.quests if q.get("root") == G.CATHEDRAL_REVEAL_QUEST_ROOT]
    check("both: one descent quest on the list, ended in success", len(descent_rows) == 1
          and descent_rows[0]["state"] == "EndedSuccess", descent_rows)
    rev = next(r for r in recs if r["poll"] == rv[0])
    check("reveal flag published in the poll's record", rev["knowledge_revealed"] and rev["reveal_fired_this_poll"]
          and rev["reveal_fired_tick"] == rev["ticksGame"])

    print("\n[4] stage 3 entered by this beat and only this beat")
    check("effective_stage is 3 from the reveal poll on", all(r["effective_stage"] == 3 for r in recs if r["poll"] >= rv[0]))
    check("effective_stage is never 3 before the reveal poll", all(r["effective_stage"] < 3 for r in recs if r["poll"] < rv[0]))
    check("conduct posture alone never reports 3", all(r["conduct_posture"] in (0, 1, 2) for r in recs))
    src = open(os.path.join(UTILS, "gm_blackboard_shadow.py"), encoding="utf-8").read()
    sets = [m.start() for m in re.finditer(r"self\.knowledge_revealed\s*=", src)]
    contexts = [src[max(0, i - 400):i] for i in sets]
    ok = len(sets) == 2 and "reveal_beat_fired" in src[sets[0]:sets[0] + 120] and \
        'row.get("state") == "EndedSuccess"' in contexts[1]
    check("knowledge_revealed is written in exactly two places: the before-this-run flag and the descent's success",
          ok, len(sets))
    return recs, rv[0]


def criterion_3(recs, reveal_poll):
    print("\n[3] once: re-trigger attempts refused")
    after = [r for r in recs if r["poll"] > reveal_poll]
    check("after the beat, the trigger set still holds and is refused (already_revealed) every later VOUCHED poll",
          after and all(r["reveal_gate"] == "already_revealed" for r in after if r["conduct_posture"] == 2)
          and after[-1]["reveal_retrigger_refused_polls"] > 0, after[-1]["reveal_retrigger_refused_polls"] if after else None)

    def demote_and_reclimb(board, poll):
        if poll == reveal_poll + 5:
            board.cathedral_regard = -50.0   # labelled: a collapse in standing, then the colony earns it back

    _, recs2, _ = run(ordinary(polls=420), restore=True, inject=demote_and_reclimb)
    post = [r for r in recs2 if r["poll"] > reveal_poll + 5]
    reclimbed = any(r["conduct_posture"] < 2 for r in post) and post[-1]["conduct_posture"] == 2
    o = events(recs2, "cathedral_descent_opening")
    print("      demotion at poll %d: lowest posture after %s, last posture %s, openings %s"
          % (reveal_poll + 5, min(r["conduct_posture"] for r in post), post[-1]["conduct_posture"], [p for p, _ in o]))
    check("demote and re-climb to VOUCHED: still one opening, stage 3 never lost",
          reclimbed and len(o) == 1 and all(r["effective_stage"] == 3 for r in post), (reclimbed, len(o)))

    fx = ordinary()
    fx["existing_quests"] = [{"id": 7, "name": "The Way Down", "root": G.CATHEDRAL_REVEAL_QUEST_ROOT,
                              "state": "Ongoing"}]
    _, recs3, _ = run(fx, restore=True)
    o = events(recs3, "cathedral_descent_opening")
    el = events(recs3, "cathedral_descent_opened_elsewhere")
    check("a descent already on the quest list (dev-opened): never opened a second time", not o and len(el) == 1,
          (len(o), len(el)))

    _, recs4, _ = run(ordinary(descent="never"), restore=True)
    o = events(recs4, "cathedral_descent_opening")
    check("descent opened but never walked: one opening, no reveal, stage 3 shut",
          len(o) == 1 and not events(recs4, "cathedral_reveal_beat")
          and all(r["effective_stage"] < 3 for r in recs4) and recs4[-1]["reveal_gate"] == "already_opened")

    _, recs5, rb5 = run(ordinary(refuses=1), restore=True)
    o = [p for p, _ in events(recs5, "cathedral_descent_opening")]
    un = [p for p, _ in events(recs5, "cathedral_descent_opening_unconfirmed")]
    rows5 = [q for q in rb5.quests if q.get("root") == G.CATHEDRAL_REVEAL_QUEST_ROOT]
    print("      game refuses the first opening: openings at %s, unconfirmed at %s, descent quests %d, reveals %d"
          % (o, un, len(rows5), len(events(recs5, "cathedral_reveal_beat"))))
    check("the game refuses the first opening: the gate re-arms once unconfirmed, the second is delivered, one quest, "
          "one reveal", len(o) == 2 and len(un) == 1 and un[0] <= o[1] and len(rows5) == 1
          and len(events(recs5, "cathedral_reveal_beat")) == 1, (o, un, len(rows5)))

    fx = ordinary()
    fx["existing_quests"] = [{"id": 9, "name": "The Way Down", "state": "EndedSuccess"}]   # no root: some other quest
    _, recs6, _ = run(fx, restore=False)
    check("a quest merely NAMED like the descent (no root) sets no reveal flag",
          not events(recs6, "cathedral_reveal_beat") and all(r["effective_stage"] < 3 for r in recs6))

    cs = open(CS, encoding="utf-8").read()
    check("source lint: a second opening is refused by the save's once-flag and by an existing descent quest",
          'if (st.opened) return "the descent has already opened' in cs and "if (st.revealed) return" in cs
          and "DescentQuests().Any()" in cs and "OpeningRefusal() == null && CathedralDescent.TryFindTile" in cs)
    check("source lint: the incident marks opened only once its quest has a site",
          "if (ok && hasSite)" in cs)
    check("source lint: the address ends THIS site's quest before it sets the flag, and refuses without one",
          cs.index("quest.End(QuestEndOutcome.Success") < cs.index("st.revealed = true;")
          and "QuestOfSite(listener.Map?.Parent)" in cs)
    check("source lint: only an awake clan colonist/droid with a clear line to the terminus hears it",
          "CathedralDescent.CanHear(p)" in cs and "GenSight.LineOfSight" in cs and "p.CanReach(terminus" in cs
          and "p.RaceProps.Humanlike || p.RaceProps.IsMechanoid" in cs)
    check("in game (source lint): a second opening is refused by the save's once-flag (OpeningRefusal checks opened and revealed)",
          'if (st.opened) return "the descent has already opened' in cs and "if (st.revealed) return" in cs
          and "CanFireNowSub" in cs and "OpeningRefusal() == null" in cs)
    check("source lint: the address is spoken once (SpeakAddress returns on revealed before it sets it)",
          re.search(r"if \(st == null \|\| st\.revealed\) return false;\s*RUT_CathedralDescentText txt", cs) is not None)


def criterion_5():
    print("\n[5] text: the linter, at the stage each string speaks in")
    for path, stage in ((OPENING_XML, 2), (ADDRESS_XML, 3)):
        seen = []
        bad = LINT.xml_findings(path, stage, seen)
        print("      %s at stage %d: %d strings read, %d findings" % (os.path.basename(path), stage, len(seen), len(bad)))
        check("%s lints clean at stage %d (%d strings)" % (os.path.basename(path), stage, len(seen)),
              not bad and len(seen) >= (3 if stage == 2 else 8), bad)
    bad2 = LINT.xml_findings(ADDRESS_XML, 2, [])
    check("the address held to the pre-reveal rules is refused (linter discriminates)", len(bad2) >= 1, bad2)
    for planted in ("The droids are spared because they are mine.", "I answer the drill from below.",
                    "This is the Cathedral speaking.", "My factory is dark."):
        check("planted line refused at stage 3: %r" % planted, LINT.findings(planted, 3) != [])
    text = open(ADDRESS_XML, encoding="utf-8").read() + open(OPENING_XML, encoding="utf-8").read()
    tokens = set(re.findall(r"\[([A-Z]+)\]", text))
    check("every [TOKEN] in the text is one the C# fills", tokens <= {"SPEAKER", "NAME"}, tokens)
    cs = open(CS, encoding="utf-8").read()
    hard = re.findall(r'(?:ListenOption|CloseOption) = "([^"]+)"', cs) + \
        [" ".join(re.findall(r'"([^"]*)"', re.search(r"EscortBrokenMessage\(string name\) => (.*);", cs).group(1)))] + \
        re.findall(r'return p\.LabelShort \+ "([^"]+)"', cs) + re.findall(r'return "(the comms set on )"', cs)
    bad = [(h, LINT.findings(h, 3)) for h in hard if LINT.findings(h, 3)]
    print("      hardcoded C# strings linted at stage 3: %r" % hard)
    check("the C#'s own player-facing strings (dialog options, escort message, speaker phrase) lint clean at stage 3",
          len(hard) >= 5 and not bad, (len(hard), bad))


def criterion_6():
    print("\n[6] Oracle-absent end to end")
    old = os.environ.get("PATH", "")
    os.environ["PATH"] = os.pathsep.join(p for p in old.split(os.pathsep)
                                         if not os.path.exists(os.path.join(p, "claude")))
    try:
        _, recs, _ = run(ordinary(), restore=True)
    finally:
        os.environ["PATH"] = old
    check("no `claude` on PATH: opening and reveal both happen", events(recs, "cathedral_descent_opening")
          and events(recs, "cathedral_reveal_beat"))
    cs = open(CS, encoding="utf-8").read()
    check("source lint: the in-game beat calls no Oracle, no process, no LLM",
          not re.search(r"Oracle\w*\.|Process\.Start|claude", cs.replace("Oracle is not called", "")), "")
    check("source lint: the address pages are the def's fallback lines", "txt.lines.Select" in cs)


def criterion_7():
    print("\n[7] scoped to the player")
    cs = open(CS, encoding="utf-8").read()
    code = "\n".join(l for l in cs.split("\n") if not l.strip().startswith("//") and not l.strip().startswith("///"))
    hits = re.findall(r"TryAffectGoodwill\w*|Goodwill\w*\(|TraderKind\w*|\.Name\s*=|EntityCodex\w*|SetRelation\w*"
                      r"|Faction\.Notify\w*|Find\.Archive\.Add|ResearchManager", code)
    check("source lint: CathedralDescent.cs writes no faction, goodwill, trader, codex or research state", not hits, hits)
    import xml.etree.ElementTree as ET
    types = set()
    for p in (OPENING_XML, ADDRESS_XML):
        types |= {d.tag.split(".")[-1] for d in ET.parse(p).getroot() if isinstance(d.tag, str)}
    check("the beat's defs are none of the faction-visible types", not (types & SURF.FACTION_VISIBLE), types)
    planted = b"<Defs><FactionDef><defName>X</defName><description>a planted faction line</description></FactionDef></Defs>"
    check("string_surface.py sees a planted FactionDef string",
          SURF.surface_of("src/X/Defs/x.xml", planted) == [("FactionDef/X", "description", "a planted faction line")])
    keyed = b"<LanguageData><RUT_X>trader chatter</RUT_X></LanguageData>"
    check("string_surface.py sees a Keyed string", SURF.surface_of("src/X/Languages/English/Keyed/k.xml", keyed) != [])


def main():
    criterion_1()
    recs, reveal_poll = criterion_2_and_4()
    criterion_3(recs, reveal_poll)
    criterion_5()
    criterion_6()
    criterion_7()
    print("\n%d/%d checks passed" % (len(RAN) - len(FAILS), len(RAN)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
