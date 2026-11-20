#!/usr/bin/env python3
"""Selftest for the round-4 judge's miner rules (RIMMANDRAKE_FIX_MINER_JUDGE_FAILED_SLACK_EIGHT_OF_TWENTY), on a fixture.

    python3 src/RimMandrake/Utils/run_selftests.py --only modledger_round5

Verdicts: D:\\ClaudeWork\\rimmandrake\\conductor\\mining_samples\\<Mod>_round4.judge.json. All four WRONG entries were
traps that commits overtook: the ticket's own fix (GSS 170), or work filed under other tickets (EK 65, EK 125, FW 451).
The round-4 currency reader saw only later notes on the mod's tickets and commits whose subject names the mod. So the
class fix: a trap sentence is checked against the repo TODAY (the lines that hold the identifiers it names) and against
every later commit that touched a file it names or the mod's own files, the ticket's own fix commits with their
message body. Then the judge's rules 2 to 6, one fixture ticket each, read by a faked reader.
"""
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modledger as M                                            # noqa: E402
import modledger_backfill as B                                   # noqa: E402
import modledger_reader as R                                     # noqa: E402

FAIL = []
MOD = "FixtureMod"


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        FAIL.append(name)


def w(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(obj if isinstance(obj, str) else json.dumps(obj, indent=1))


root = tempfile.mkdtemp(prefix="modledger_r5_")
c = os.path.join(root, "design", "concepts", MOD)
v = os.path.join(c, "version")
src = os.path.join(root, "src", "RimMandrake", MOD)
EVD = os.path.join(root, "infrastructure", "state", "ledger", "events")
w(os.path.join(v, "VERSION.json"), {"mod": MOD, "version": "0.1.0", "state": "locked", "locked_on": "2026-11-13",
                                    "locked_by": "owner", "bars_total": 1, "bars_met": 1})
w(os.path.join(v, "locked_bars.json"), {"ids": ["bar_a"]})
w(os.path.join(v, "test_table.json"), {"bars": [{"id": "bar_a", "kind": "experience", "source": "tree.json",
                                                 "proves_at": "6", "decides": ["sc_a"]}]})
# the repo today: the scene a trap says is missing exists (EK 65); the criterion a trap calls impossible was repaired
# (EK 125); the known-red entry a trap cites drops itself once the cap is 8 (FW 451)
w(os.path.join(src, "Source", "RM_FixtureProof.cs"), 'class RM_FixtureProof {\n    static readonly string[] SceneNames = '
  '{ "sc_a", "blast_kinds" };\n}\n')
w(os.path.join(c, "scenes.json"), {"sc_storeroom_mortar": {"expect": "goods travel from round(1.6 x (kernel - 0.5)) to "
                                                                     "round(1.6 x (kernel + 0.5)) cells, a whole-cell "
                                                                     "band"}})
w(os.path.join(src, "northstar", "validation_v2.py"), 'SHIPPED_SINK_CAP_LEVELS = 8\nKNOWN_MOD_RED = {"X1_pawn_height_'
  'ladder": "PIT_SINK_CAP"} if SHIPPED_SINK_CAP_LEVELS < 8 else {}\n')
w(os.path.join(root, "infrastructure", "state", "items", "closed", "TANK_TALL_FIXTURE_TWICE_THE_DRINK.md"),
  "# TANK_TALL_FIXTURE_TWICE_THE_DRINK\n\n## spec\n\nTall tanks double the storage. Capacity lives in "
  "src/RimMandrake/OtherWorks/Source/Building_LiquidTank.cs; art at Textures/RimMandrake/OtherWorks/Tank/.\n")

T = {k: "RIMMANDRAKE_%s_FIXTUREMOD_%s" % tuple(x.split(":")) for k, x in dict(
    absent="PROVE:OUTERRIM_BLAST_LANES", absent_ok="PROVE:FLIGHT_LANE", mortar="PILOT:BLIND_CHALLENGE",
    sink="WIDEN:LADDER_ROWS", own="UNBEND:RANDOM_BASES_HID_IT", lean="JUDGE:FIVE_BARS", lean2="ADVANCE:OFFLINE_PILOT",
    keep="PROVE:TRACKER_READ", ledger="FIX:SIX_STANDING_FAILS", walk="VALIDATE:NORTH_STAR",
    swim="FIX:LATE_TOGGLE_STAYS_DRY", pipe="CHALLENGE:BLIND_CYCLE_ONE", redo="SKIP:GOODS_WHEN_FLIGHT_OFF",
    poles="FINISH:WALK_LINE_LOOKS").items()}
TANK = "TANK_TALL_FIXTURE_TWICE_THE_DRINK"
FAULT_PIPE, FAULT_MOD = "RIMMANDRAKE_RECORD_FULL_LAST_LINE_IN_FIXTURE_RUNS", "RIMMANDRAKE_THROW_FIXTUREMOD_CRATES_SHORT"
w(os.path.join(v, "blind_challenge", "cycle_1", "lane2", "faults.json"), {"faults": [
    {"id": FAULT_PIPE, "class": "Polish", "bar": "(record format)", "criterion": "a recorded run can be compared",
     "evidence": ["test_table.json runs_today.last is truncated at 200 characters"], "status": "NOTED_FOR_CONDUCTOR",
     "would_pass": "runs_today stores the verdict line whole",
     "smallest_fix": "the steward's recorder keeps stdout's last line whole; the comparer treats a prefix as a match"},
    {"id": FAULT_MOD, "class": "Problem", "bar": "bar_a", "criterion": "a crate near a blast is thrown a short way",
     "evidence": ["sc_a: the crate stayed put"], "status": "OPEN",
     "would_pass": "sc_a reads PASS", "smallest_fix": "apply the knockback to closed crates in RM_FixtureProof"}]})
ttl = {
    "absent": "FixtureMod: prove the two Outer Rim blast lanes",
    "absent_ok": "FixtureMod: prove the flight lane",
    "mortar": "FixtureMod: pilot the blind challenge",
    "sink": "FixtureMod ladder rows widen, still count to two",
    "own": "FixtureMod: seven oracle scenes hid the cord bends",
    "lean": "FixtureMod bars judge: five in one sitting",
    "lean2": "FixtureMod: advance offline beside the pilot",
    "keep": "FixtureMod: prove the tracker read",
    "ledger": "FixtureMod modcheck: fix six standing fails",
    "walk": "Validate the seeded north star and view the sheet once",
    "swim": "FixtureMod RM_Swim.Reapply returns early when swimTerrain is null: a deep-swim toggle mid-game never "
            "recomputes",
    "pipe": "FixtureMod blind cycle one",
    "redo": "FixtureMod: skip goods when flight is off",
    "poles": "FixtureMod: finish the walk's line looks"}
EV = [{"seat": "BENCH", "event": "file", "id": T[k], "title": t, "ts": "2026-10-22T01:00:00Z", "tsn": 100 + i}
      for i, (k, t) in enumerate(sorted(ttl.items()))]
EV += [
    {"seat": "OWNER", "event": "file", "id": TANK, "ts": "2026-10-13T11:56:17Z", "tsn": 190,
     "title": "Tall variants of the liquid tank: same footprint, double the storage"},
    {"seat": "OWNER", "event": "note", "id": TANK, "ts": "2026-10-15T05:32:09Z", "tsn": 191,
     "text": "Owner approved the camera; scope now all four tanks in the four FixtureMod looks.",
     "ownerSaid": "do all four tanks in each of the FixtureMod looks, and regenerate the short ones too"},
    # rule 1, EK 65 / EK 125 / FW 451: traps other tickets' commits overtook
    {"seat": "BENCH", "event": "note", "id": T["absent"], "ts": "2026-11-13T06:00:00Z", "tsn": 200,
     "text": "The item's premise is false: RM_FixtureProof.cs has no blast_kinds scene, so it must be built first."},
    {"seat": "BENCH", "event": "note", "id": T["absent_ok"], "ts": "2026-11-13T06:00:00Z", "tsn": 201,
     "text": "RM_FixtureProof.cs has no flight_lane scene, so the flyer is checked by the tracker read alone."},
    {"seat": "BENCH", "event": "note", "id": T["mortar"], "ts": "2026-11-14T06:00:00Z", "tsn": 202,
     "text": "sc_storeroom_mortar's per-good 1.3-2.0 ratio criterion is impossible in whole cells; a scene-criterion "
             "problem, not a code fault."},
    {"seat": "BENCH", "event": "close", "id": T["sink"], "sha": "abcd5101", "ts": "2026-10-23T05:00:00Z", "tsn": 203,
     "reason": "rows widened to D 8/16. Fill under 25 cm stays UNMEASURED because there is no sub-notch fill tool, and "
               "X1 is known-red on the sink cap."},
    # rule 1, GSS 170: the ticket's own fix commit, its message body, overtook the trap
    {"seat": "BENCH", "event": "note", "id": T["own"], "ts": "2026-11-15T01:00:00Z", "tsn": 210,
     "text": "T_CORE_GEOMETRY_OFFLINE was green because it reads only the 7 oracle scenes."},
    {"seat": "BENCH", "event": "close", "id": T["own"], "sha": "abcd5102", "ts": "2026-11-15T13:00:00Z", "tsn": 211,
     "reason": "cord kernel fixed at abcd5102; the blind cycle's slack and stray Problems pass"},
    {"seat": "BENCH", "event": "note", "id": T["keep"], "ts": "2026-11-15T03:00:00Z", "tsn": 212,
     "text": "The bridge cannot read the pawn's flight tracker while the game is paused; read it on a running tick."},
    # rule 2, FW 72 / GSS 245: a sentence that leans on a dropped one
    {"seat": "BENCH", "event": "note", "id": T["lean"], "ts": "2026-10-22T03:00:00Z", "tsn": 220,
     "text": "The reworded ladder bars' rows still stop at 2 m. The caveat is filed as FIXTURE_ROWS_WIDEN_TO_TWO."},
    {"seat": "BENCH", "event": "note", "id": T["lean2"], "ts": "2026-10-22T03:00:00Z", "tsn": 221,
     "text": "The 26 scene entry points and 10 SC rows are import-checked but UNRUN. Stage 3 'done' does not mean the "
             "scenes pass."},
    # rule 3, FW 94: the build sha is a ledger commit; the text names the fix
    {"seat": "BENCH", "event": "note", "id": T["ledger"], "ts": "2026-10-25T01:08:52Z", "tsn": 230,
     "text": "fixed offline at abcd5103; NEXT: rerun the FixtureMod modcheck after deploy"},
    {"seat": "FOUNDRY", "event": "implemented", "id": T["ledger"], "sha": "abcd5104", "ts": "2026-10-29T20:05:46Z",
     "tsn": 231, "criteria": [{"id": "A1", "text": "six rows PASS"}]},
    {"seat": "FOUNDRY", "event": "verify", "id": T["ledger"], "result": "pass", "sha": "abcd5104", "criterion": "A1",
     "level": "L2", "config": "modcheck run5", "ts": "2026-10-29T20:05:49Z", "tsn": 232},
    # rule 3, GSS 341: the close commit names the mod; a note names an older hose fix; the owner's walk is the test
    {"seat": "BENCH", "event": "note", "id": T["walk"], "ts": "2026-10-06T13:41:50Z", "tsn": 240,
     "text": "hose wall shadows fixed at abcd5105; north star stays DRAFT"},
    {"seat": "OWNER", "event": "note", "id": T["walk"], "ts": "2026-10-16T05:25:42Z", "tsn": 241,
     "text": "Owner walked the 31-station walkthrough save RM_fm_walk_20261015b and verified it in game"},
    {"seat": "OWNER", "event": "close", "id": T["walk"], "sha": "abcd5106", "ts": "2026-10-16T05:27:53Z", "tsn": 242,
     "reason": "North star VALIDATED by modcheck validate after owner walked the save"},
    # rule 3, FW 756: a close that names only a sha
    {"seat": "BENCH", "event": "close", "id": T["swim"], "sha": "abcd5107", "ts": "2026-10-19T05:38:05Z", "tsn": 250,
     "reason": "fixed in abcd5107"},
    # rule 4, FW 661: a pipeline reader's defect
    {"seat": "BENCH", "event": "note", "id": T["pipe"], "ts": "2026-11-15T03:00:00Z", "tsn": 260,
     "text": "The maturation reader had flaws: the faults.json cls key was unread, so fix checks were silently "
             "skipped. Fixed in maturation.py; unclassed faults are now refused."},
    # rule 6, EK 139: how a fix's red was re-demonstrated
    {"seat": "BENCH", "event": "note", "id": T["redo"], "ts": "2026-11-15T03:00:00Z", "tsn": 270,
     "text": "The judge's original red command held the placeholder <parent Source> and ran on an uncommitted "
             "worktree; it was re-demonstrated with named paths in a scratch clone."},
    # rule 5, GSS 378: his words point at a photo the event names
    {"seat": "OWNER", "event": "note", "id": T["poles"], "ts": "2026-11-08T21:15:30Z", "tsn": 280,
     "text": "Owner reference photo for overhead lines: D:\\ClaudeWork\\rimmandrake\\fm_sitting\\refs\\owner_pole.png "
             "(lines rest on top of each insulator, sag only in the span; no bump or kink).",
     "ownerSaid": "here's what power poles really look like up close. Both industrial or scrapper seem to avoid the "
                  "sharp bends much better."}]
os.makedirs(EVD)
for e_ in EV:
    with open(os.path.join(EVD, "%s.jsonl" % e_["seat"]), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(e_) + "\n")

P_PROOF = "src/RimMandrake/%s/Source/RM_FixtureProof.cs" % MOD
P_SCENES = "design/concepts/%s/scenes.json" % MOD
P_V2 = "src/RimMandrake/%s/northstar/validation_v2.py" % MOD
# (date, subject, body, files): commits a fixture root (no git checkout) stands in
GIT = {
    "abcd5001": ("2026-11-14T20:35:56Z", "Stage 3 proof scenes (9 locked entry points), g4 test-only mass pin", "",
                 [P_PROOF, P_SCENES]),
    "abcd5002": ("2026-11-15T10:08:24Z", "storeroom-mortar factor clause repaired to a whole-cell band", "",
                 [P_SCENES]),
    "abcd5003": ("2026-10-23T14:18:54Z", "live-sitting fixes: sink cap to 4 m, trench bar by body size", "",
                 ["src/RimMandrake/%s/Source/RM_PitDrawMath.cs" % MOD, P_V2]),
    "abcd5101": ("2026-10-23T04:50:00Z", "ladder rows widened to D 8/16", "", [P_V2]),
    "abcd5102": ("2026-11-15T12:03:30Z", "cord kernel: cut leads slack and round",
                 "Fixes three of the four blind-cycle-1 cord Problems. CordGeometryChecks now also reads the judge's "
                 "random bases (bends as a ratchet at 4).", ["src/RimMandrake/%s/Source/Core/CordBuilder.cs" % MOD]),
    "abcd5103": ("2026-10-25T01:00:00Z", "RIMMANDRAKE_FIX_FIXTUREMOD_SIX_STANDING_FAILS: six FAIL rows fixed offline",
                 "", ["src/RimMandrake/%s/Source/Pump.cs" % MOD]),
    "abcd5104": ("2026-10-29T20:05:40Z", "ledger: FOUNDRY canary red third repeat", "",
                 ["infrastructure/state/ledger/events/FOUNDRY.jsonl"]),
    "abcd5105": ("2026-10-05T10:00:00Z", "FixtureMod hose: wall shadows no longer cut rectangles", "",
                 ["src/RimMandrake/%s/Source/Hose.cs" % MOD]),
    "abcd5106": ("2026-10-16T05:27:00Z", "Owner verified the FixtureMod walkthrough in game; look A2 passes, item done",
                 "", ["infrastructure/state/ledger/events/OWNER.jsonl"]),
    "abcd5107": ("2026-10-19T05:37:00Z", "HugeThings+FixtureMod: ClearArea spares giants only in NaturalRockOnly; late "
                 "deep-swim toggle recomputes; settings headers use keys", "",
                 ["src/RimMandrake/HugeThings/Source/ClearArea.cs", "src/RimMandrake/%s/Source/Swimming/RM_Swim.cs" %
                  MOD, "src/RimMandrake/%s/Source/SelfTest/SwimChecks.cs" % MOD])}
B.SUBJECT_OF = lambda root_, sha: (GIT.get(sha) or (None, None))[1]
B.COMMITS = lambda root_: sorted((d, s, subj) for s, (d, subj, _b, _f) in GIT.items())
B.COMMIT_DATE = lambda root_, sha: (GIT.get(sha) or (None,))[0]
B.COMMIT_INFO = lambda root_: {s: (b, f) for s, (_d, _s, b, f) in GIT.items()}
B.RELENTLESS_STORE = tempfile.mkdtemp(prefix="modledger_r5_store_")


def tr(text, where):
    return {"text": text, "where": where}


ANS = {
    T["absent"]: {"traps": [tr("The item's premise is false: RM_FixtureProof.cs has no blast_kinds scene, so it must "
                               "be built first.", "RM_FixtureProof.cs SceneNames")]},
    T["absent_ok"]: {"traps": [tr("RM_FixtureProof.cs has no flight_lane scene, so the flyer is checked by the "
                                  "tracker read alone.", "RM_FixtureProof.cs SceneNames")]},
    T["mortar"]: {"traps": [tr("sc_storeroom_mortar's per-good 1.3-2.0 ratio criterion is impossible in whole cells; "
                               "a scene-criterion problem, not a code fault.", "sc_storeroom_mortar")]},
    T["sink"]: {"traps": [tr("Fill under 25 cm stays UNMEASURED because there is no sub-notch fill tool, and X1 is "
                             "known-red on the sink cap.", "northstar/validation_v2.py X1_pawn_height_ladder")]},
    T["own"]: {"traps": [tr("T_CORE_GEOMETRY_OFFLINE was green because it reads only the 7 oracle scenes.",
                            "T_CORE_GEOMETRY_OFFLINE")]},
    T["keep"]: {"traps": [tr("The bridge cannot read the pawn's flight tracker while the game is paused; read it on a "
                             "running tick.", "Pawn_FlightTracker")]},
    T["lean"]: {"traps": [tr("The reworded ladder bars' rows still stop at 2 m. The caveat is filed as "
                             "FIXTURE_ROWS_WIDEN_TO_TWO.", "ladder rows")]},
    T["lean2"]: {"traps": [tr("The 26 scene entry points and 10 SC rows are import-checked but UNRUN. Stage 3 'done' "
                              "does not mean the scenes pass.", "validation.py")]},
    T["pipe"]: {"traps": [tr("The maturation reader had flaws: the faults.json cls key was unread, so fix checks were "
                             "silently skipped. Fixed in maturation.py; unclassed faults are now refused.",
                             "maturation.py")]},
    T["redo"]: {"traps": [tr("The judge's original red command held the placeholder <parent Source> and ran on an "
                             "uncommitted worktree; it was re-demonstrated with named paths in a scratch clone.",
                             "fix_demos/jj_red.txt")]},
    T["swim"]: {"changed": None}}
CURRENT_ASKED = []


def fake_call(prompt, model, system=None):
    ans = {}
    for n in re.findall(r"=== TICKET (\S+)", prompt):
        ans[n] = dict({"defect": "%s is wrong" % ttl.get(next((k for k, x in T.items() if x == n), ""), n),
                       "proposed_fix": "change the thing that is wrong in it", "accept": "selftest exit 0",
                       "class": "problem", "bars": [], "changed": None, "causes_refuted": [], "traps": []},
                      **ANS.get(n, {}))
    for n, block in re.findall(r"=== (?:KEEP|OWNER WORDS) (\S+)\n(.*?)(?=\n=== |\Z)", prompt, re.S):
        ans[n] = [int(i) for i in re.findall(r"^\[(\d+)\]", block, re.M)]
    for n, block in re.findall(r"=== CURRENT (\S+)\n(.*?)(?=\n=== |\Z)", prompt, re.S):   # the currency reader
        CURRENT_ASKED.append(block)
        # a faithful reader: false when the later work or today's repo plainly contradicts the statement
        ans[n] = [int(i) for i, body in re.findall(r"^\[(\d+)\] (.*?)(?=^\[\d+\] |\Z)", block, re.M | re.S) if
                  "whole-cell band" in body or "random bases" in body or "sink cap to 4 m" in body]
    return ans, 0.01


R.CALL = fake_call
res = B.run(root, MOD, read=True, budget_usd=5)
ALL = [e for e in M.read(root, MOD) if e["_shard"] == "BACKFILL"]
F = M.reduce(M.read(root, MOD))["findings"]


def on(k, kinds=None):
    tid = T.get(k, k)
    return [e for e in ALL if "item:" + tid in e["evidence"] and (kinds is None or e["kind"] in kinds)]


def traps(k):
    return [e["body"].get("text") or "" for e in on(k, ("trap.noted",))]


def asked(word):
    return [b for b in CURRENT_ASKED if word in b]


def fin(k, kind):
    f = F.get("finding:" + T.get(k, k)) or {}
    return dict(f, **next((dict(e["body"], code_sha=e.get("code_sha")) for e in on(k, (kind,))), {}))


check("rule 1 (EK 65): a trap saying a named scene is missing leaves when the mod's code holds it today",
      not [t for t in traps("absent") if "blast_kinds" in t], traps("absent"))
check("rule 1 control: a trap saying a scene is missing stays while no file of the mod holds it",
      [t for t in traps("absent_ok") if "flight_lane" in t], traps("absent_ok"))
check("rule 1 (EK 125): the currency reader is handed today's line for the scene a trap names",
      [b for b in asked("sc_storeroom_mortar") if "today:" in b and "whole-cell band" in b], CURRENT_ASKED)
check("rule 1 (EK 125): that trap leaves on the reader's answer", not traps("mortar"), traps("mortar"))
check("rule 1 (FW 451): a later commit of any ticket that touched a file the trap names reaches the reader, though "
      "its subject does not name the mod", asked("abcd5003") and not [t for t in traps("sink") if "sink cap" in t],
      (traps("sink"), CURRENT_ASKED))
check("rule 1 (FW 451): the clause before the overtaken one stays, a fact of its own",
      [t for t in traps("sink") if "sub-notch" in t] or not traps("sink"), traps("sink"))
check("rule 1 (GSS 170): the ticket's own later fix commit reaches the reader with its message body",
      [b for b in asked("T_CORE_GEOMETRY_OFFLINE") if re.search(r"(?m)^ +later: .*random bases", b)], CURRENT_ASKED)
check("rule 1 (GSS 170): that trap leaves on the reader's answer", not traps("own"), traps("own"))
check("rule 1 control: a trap that no later commit or today's line bears on stays and is not asked",
      traps("keep") and not asked("flight tracker"), (traps("keep"), asked("flight tracker")))
check("rule 2 (FW 72): a sentence leaning on a dropped one leaves with it ('The caveat is filed as ...')",
      not [t for t in traps("lean") if "caveat" in t], traps("lean"))
check("rule 2 (GSS 245): 'Stage 3 done does not mean the scenes pass' leaves with the UNRUN sentence it leans on",
      not [t for t in traps("lean2") if "does not mean" in t], traps("lean2"))
fl = fin("ledger", "finding.verified")
check("rule 3 (FW 94): a build sha whose commit is a 'ledger:' commit gives way to the fix sha the text names",
      fl.get("code_sha") == "abcd5103", fl)
fw = fin("walk", "finding.claimed_fixed")
check("rule 3 (GSS 341): a close sha whose commit names the mod stays the code_sha, never an older sha a note names",
      fw.get("code_sha") == "abcd5106", fw)
check("rule 3 (GSS 341): the owner's walk that verified it in game is the test, never 'none recorded'",
      "walked" in str(fw.get("test")) and "none recorded" not in str(fw.get("test")), fw)
fs = fin("swim", "finding.claimed_fixed")
check("rule 3 (FW 756): a close naming only a sha reads that commit: its subject clause about the ticket is the change",
      "deep-swim toggle recomputes" in str(fs.get("text")) and "does not describe" not in str(fs.get("text")), fs)
check("rule 3 (FW 756): a SelfTest file the fix commit touched is the test", "SwimChecks.cs" in str(fs.get("test")), fs)
check("rule 4 (GSS 0): his words on a ticket whose code and art are another mod's are not this mod's decision",
      not on(TANK), [(e["kind"], e["body"]) for e in on(TANK)])
check("rule 4 (EK 8): a blind fault with no mod bar, noted for the Conductor about a pipeline recorder, mines nothing",
      "finding:" + FAULT_PIPE not in F, F.get("finding:" + FAULT_PIPE))
check("rule 4 control: a blind fault on a locked bar stays a finding", "finding:" + FAULT_MOD in F, sorted(F))
check("rule 4 (FW 661): a trap about a pipeline file (maturation.py) is no trap of the mod", not traps("pipe"),
      traps("pipe"))
dp = [e for e in on("poles", ("decision",))]
check("rule 5 (GSS 378): his words that point at a photo cite it, with what the photo shows",
      dp and all("owner_pole.png" in json.dumps(e["evidence"]) and "insulator" in json.dumps(e["body"]) for e in dp),
      [(e["evidence"], e["body"]) for e in dp])
check("rule 6 (EK 139): a note on how a fix's red was re-demonstrated is no trap", not traps("redo"), traps("redo"))
check("the round-5 fixture lints clean and nothing it plans is refused", not M.lint(root, MOD, None)[0] and
      not res["refused"], (M.lint(root, MOD, None)[0][:3], res["refused"][:3]))

# EK 125 in the round-5 re-mine: one currency question read [] in the run and [1] twice when asked again; a statement
# either of two passes found false leaves
_answers = [{"T_X": []}, {"T_X": [1]}]
R.CALL = lambda prompt, model, system=None: (_answers.pop(0) if _answers else {"T_X": []}, 0.01)
_rp = os.path.join(tempfile.mkdtemp(prefix="modledger_r5_rd_"), "r.json")
R.read_tickets(_rp, {"T_X": "=== CURRENT T_X\nTITLE: -\n[1] (stated 2026-11-15) a criterion is impossible"}, [], 5,
               field="current", system=R.CURRENT_SYSTEM, log=lambda *a: None)
with open(_rp, encoding="utf-8") as fh_:
    _got = json.load(fh_)["tickets"]["T_X"].get("current")
check("currency: a statement either of two reader passes found false is false (EK 125, a reader that varies)",
      _got == [1], _got)
shutil.rmtree(os.path.dirname(_rp), ignore_errors=True)

shutil.rmtree(root, ignore_errors=True)
shutil.rmtree(B.RELENTLESS_STORE, ignore_errors=True)
print("selftest_modledger_round5: %d failure%s" % (len(FAIL), "" if len(FAIL) == 1 else "s"))
sys.exit(1 if FAIL else 0)
