#!/usr/bin/env python3
"""Selftest for the round-3 judge's miner rules (RIMMANDRAKE_FIX_MINER_JUDGE_FAILED_SLACK_EIGHT_OF_TWENTY), on a fixture.

    python3 src/RimMandrake/Utils/run_selftests.py --only modledger_round4

Verdicts: D:\\ClaudeWork\\rimmandrake\\conductor\\mining_samples\\<Mod>_round3.judge.json. All three WRONG entries were
traps later work overtook, so the class is fixed: a trap or a "cannot / until X" statement is mined only while it is
still true against the repo and the ledger (a later commit, a later close of a ticket of the mod, the reworded text
now in the mod's files), and a verify or close reason cut in the ledger is read whole from the relentless item store
before anything is mined from it. Then the judge's rules 1 to 6, one fixture ticket each, read by a faked reader.
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
        fh.write(obj if isinstance(obj, str) else json.dumps(obj))


root = tempfile.mkdtemp(prefix="modledger_r4_")
store = tempfile.mkdtemp(prefix="modledger_r4_store_")
c = os.path.join(root, "design", "concepts", MOD)
v = os.path.join(c, "version")
EVD = os.path.join(root, "infrastructure", "state", "ledger", "events")
w(os.path.join(v, "VERSION.json"), {"mod": MOD, "version": "0.1.0", "state": "locked", "locked_on": "2026-11-13",
                                    "locked_by": "owner", "bars_total": 1, "bars_met": 1})
w(os.path.join(v, "locked_bars.json"), {"ids": ["bar_a"]})
w(os.path.join(v, "test_table.json"), {"bars": [{"id": "bar_a", "kind": "experience", "source": "tree.json",
                                                 "proves_at": "6", "decides": ["sc_a"]}]})
# the reworded bar text, landed in the mod's own files (EK 51)
w(os.path.join(c, "scenes.json"), {"sc_closed": {"expect": "a closed container near a blast is thrown a short way"}})

T = {k: "RIMMANDRAKE_%s_FIXTUREMOD_%s" % tuple(x.split(":")) for k, x in dict(
    cut="FIX:CORD_LOOPS_INTO_DOORS", until="BUILD:STAGE_THREE_BARS", cannot="DRIVE:IN_GAME_FIRST",
    stage="STAGE:HEAVY_LOCKER_LANE", gas="TRACE:GAS_CHAIN_DOOR", keep="PROVE:FLIGHT_TRACKER_READ",
    quar="PROVE:LAST_FOUR_SWITCHES", style="RUN:MIXED_LOOKS", tap="FIX:TAP_MIXED_NET",
    utils="FIX:SELFTEST_ROW_NAMES", bridge="BUILD:MOAT_WITH_MANNERS").items()}
PIPE = "LIVEROUND_FIX_FIXTUREMOD_LESS_SELFTEST_RED_ALONE"
CUT_HEAD = ("Built and ran the FixtureMod selftest from this tree. The script's own launch of the test exe fails here "
            "with 'dotnet.exe: Invalid argument' because its cwd /mnt/d/scratch/fm_cwd is not visible ")
CUT_FULL = (CUT_HEAD + "to Windows inside the box; that is the environment, not the commit. Running the staged DLL "
            "directly with dotnet.exe: 933/933 checks passed, exit 0. Mutant: removed the door check at line 541; the "
            "door-loop row went FAIL.")
w(os.path.join(store, "items", T["cut"], "state.json"), {"check": {"reasons": CUT_FULL}, "status": "done"})
ttl = {
    "cut": "FixtureMod cord loops spread into doors",
    "until": "FixtureMod Stage 3: build the eleven bars' scenes",
    "cannot": "FixtureMod: drive the in-game acceptance first",
    "stage": "FixtureMod sc_closed UNMEASURED: its 76-249 kg closed-locker lane cannot be staged; stage a closed "
             "container that legitimately reaches the band",
    "gas": "FixtureMod sc_gas: the chain stops at a vent door",
    "keep": "FixtureMod: prove the flight tracker read",
    "quar": "FixtureMod switches: prove the last four standing",
    "style": "FixtureMod one-run-one-style: mixed looks after a default change (D1), conduit gaps (D8)",
    "tap": "FixtureMod: power-tap connect guards disagree on mixed-faction nets",
    "utils": "FixtureMod selftest rows: name the door-loop rows",
    "bridge": "FixtureMod drawbridge: a moat with manners"}
EV = [{"seat": "BENCH", "event": "file", "id": T[k], "title": t, "ts": "2026-11-15T01:00:00Z", "tsn": 100 + i}
      for i, (k, t) in enumerate(sorted(ttl.items()))]
EV[[e["id"] for e in EV].index(T["tap"])]["spec"] = (
    "`Patch_TryConnect_TapOwnFaction` allows any net with one own-faction transmitter, but "
    "`Patch_ConnectToTransmitter_TapGuard` refuses the specific transmitter if foreign and re-queues. If the nearest "
    "transmitter of an allowed mixed net is foreign, the clamp re-queues every net update forever. Filter at "
    "transmitter level and stop re-queueing on a refusal the same predicate will repeat.")
EV[[e["id"] for e in EV].index(T["stage"])]["ts"] = "2026-11-15T16:33:29Z"
EV += [
    # rule 1 (GSS 119): a blind close reason the ledger cut at ~300 chars; the store holds it whole
    {"seat": "RUNNER", "event": "verify", "id": T["cut"], "result": "pass", "config": "marker:blind-check",
     "sha": "abcd2001", "ts": "2026-11-15T02:00:00Z", "tsn": 200},
    {"seat": "RELENTLESS", "event": "close", "id": T["cut"], "sha": "abcd2001", "ts": "2026-11-15T02:00:01Z",
     "tsn": 201, "reason": "relentless: blind PASS at abcd2001 after 0 return(s): " + CUT_HEAD,
     "why": "relentless: blind check passed"},
    # rule 2 (EK 51): a card question's premise, overtaken by the rewording he ordered
    {"seat": "OWNER", "event": "note", "id": T["until"], "ts": "2026-11-15T05:48:09Z", "tsn": 210,
     "text": "Owner by card 2026-11-14 (question 12).", "byCard": "Closed container near a blast: slide one cell as "
     "the locked bar says, or thrown as built? → Throw it, as built; the locked bar's wording changes from 'slides one "
     "cell' to 'thrown a short way', and the test follows"},
    {"seat": "BENCH", "event": "note", "id": T["until"], "ts": "2026-11-15T05:50:00Z", "tsn": 211,
     "text": "The census reads a cached count until its 'fresh census' flag is passed."},
    # rule 2 (EK 119): 'cannot be staged', overtaken by a later close of another of the mod's tickets
    {"seat": "OWNER", "event": "note", "id": T["cannot"], "ts": "2026-11-15T13:20:00Z", "tsn": 220,
     "text": "visit 1: the heavy-locker lane cannot be staged because no closed LWM container weighs 76-249 kg; the "
             "heavy locker caps at 58 kg."},
    {"seat": "BENCH", "event": "close", "id": T["stage"], "sha": "abcd2002", "ts": "2026-11-15T16:53:52Z", "tsn": 221,
     "reason": "heavy closed-locker lane now stageable at 76-249 kg on LWM (filter set, maxTotalMass raised for the "
               "scene)"},
    {"seat": "BENCH", "event": "note", "id": T["gas"], "ts": "2026-11-15T03:00:00Z", "tsn": 230,
     "text": "The gas chain cannot pass a closed vent door, so sc_gas stops at five vents."},
    {"seat": "BENCH", "event": "note", "id": T["keep"], "ts": "2026-11-15T03:00:00Z", "tsn": 231,
     "text": "The bridge cannot read the pawn's flight tracker while the game is paused; read it on a running tick."},
    # rule 3 (GSS 74): a test-queue quarantine note is pipeline lifecycle
    {"seat": "RUNNER", "event": "note", "id": T["quar"], "ts": "2026-11-12T14:42:56Z", "tsn": 240,
     "text": "testq J20261112T144256Z-a08f37 quarantined: ran inside Steve SIMD fault window (2026-11-08T00:57:39Z "
             "onward); no verdict recorded; re-queued"},
    # rule 5 (GSS 246): the close names PASS rows and fix shas; its own sha is an unrelated landed commit
    {"seat": "BENCH", "event": "note", "id": T["style"], "ts": "2026-10-15T10:00:00Z", "tsn": 250,
     "text": "BENCH abcd3001: D8 fixed (RunOf walks through a non-stylable conduit, never painting it)."},
    {"seat": "BENCH", "event": "note", "id": T["style"], "ts": "2026-10-15T12:00:00Z", "tsn": 251,
     "text": "D1 fixed at abcd3002: a run whose winner is legacy stays legacy; joiners are cleared, not stamped."},
    {"seat": "BENCH", "event": "close", "id": T["style"], "sha": "abcd3009", "ts": "2026-10-24T10:00:00Z", "tsn": 252,
     "why": "bridge run 1: live pass on current code: d4_save S12d_D4_pending_queue_save PASS, S7 PASS; style block "
            "S12a D1, S12b D7, S12c D5 PASS; D8 fixed abcd3001. Evidence Transient/bridge_run_1/gss_B.log"},
    # rule 4 (GSS 361): a rimflow selftest that names the mod in a case title; a mod selftest under Utils/ stays
    {"seat": "RELENTLESS", "event": "file", "id": PIPE, "ts": "2026-11-06T01:00:00Z", "tsn": 260,
     "title": "selftest_proof_sha_cited_mods reds on 'a FixtureMod-less game: UNMEASURED before any slot'",
     "spec": "src/RimMandrake/rimflow/selftest_proof_sha_cited_mods.py fails its 'a FixtureMod-less game' case. Done "
             "when the selftest passes."},
    {"seat": "RELENTLESS", "event": "close", "id": PIPE, "sha": "abcd2003", "ts": "2026-11-06T02:00:00Z", "tsn": 261,
     "reason": "relentless: blind PASS at abcd2003 after 0 return(s): selftest green"},
    {"seat": "BENCH", "event": "note", "id": T["utils"], "ts": "2026-11-06T01:00:00Z", "tsn": 262,
     "text": "Rows live in src/RimMandrake/Utils/selftest_fixturemod.py; name each door-loop row."},
    # FlowWorks 1043: validated with an owner-look criterion unmet
    {"seat": "BENCH", "event": "implemented", "id": T["bridge"], "sha": "abcd2004", "ts": "2026-10-22T01:00:00Z",
     "tsn": 270, "criteria": [{"id": "A2", "text": "12/12 live rows pass"},
                              {"id": "A3", "text": "the owner looks at timber and steel drawbridges in game"}]},
    {"seat": "BENCH", "event": "verify", "id": T["bridge"], "result": "pass", "sha": "abcd2004", "criterion": "A2",
     "level": "L2", "config": "fw_gss_sitting-14", "ts": "2026-10-22T02:00:00Z", "tsn": 271}]
os.makedirs(EVD)
for e_ in EV:
    with open(os.path.join(EVD, "%s.jsonl" % e_["seat"]), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(e_) + "\n")

# the hooks a fixture root (no git checkout, no store) stands in: commit subjects and dates, the relentless store
SUBJ = {"abcd2001": "FixtureMod: door loops refuse door cells", "abcd2002": "knockback proof: heavy closed-locker lane",
        "abcd2003": "rimflow: selftest_proof_sha_cited_mods answers UNMEASURED", "abcd2004": "drawbridge phases",
        "abcd3001": "FixtureMod style: RunOf walks through non-stylable conduit",
        "abcd3002": "FixtureMod style: a legacy winner's run stays legacy",
        "abcd3009": "rm-* helpers: omitClaudeMd + tools allowlist", "abcd4001": "FixtureMod: gas chain passes closed "
        "vent doors"}
DATES = {"abcd2001": "2026-11-15T02:00:00Z", "abcd2002": "2026-11-15T16:52:00Z", "abcd2003": "2026-11-06T02:00:00Z",
         "abcd2004": "2026-10-22T01:00:00Z", "abcd3001": "2026-10-15T09:00:00Z", "abcd3002": "2026-10-15T11:30:00Z",
         "abcd3009": "2026-10-24T09:00:00Z", "abcd4001": "2026-11-15T09:00:00Z"}
B.SUBJECT_OF = lambda root_, sha: SUBJ.get(sha)
B.COMMITS = lambda root_: sorted((DATES[s], s, SUBJ[s]) for s in SUBJ)
B.RELENTLESS_STORE = store

ANS = {
    T["cut"]: {"traps": [{"text": "The blind pass ran the FixtureMod selftest in a degraded environment. The pass is "
                                  "weaker than it reads.", "where": "fm_cwd"}]},
    T["until"]: {"traps": [{"text": "The in-game test checks exactly one cell and fails the shipped code until the bar "
                                    "and test are reworded to 'thrown a short way'.", "where": "closed-container scene"},
                           {"text": "The census reads a cached count until its 'fresh census' flag is passed.",
                            "where": "census"}]},
    T["cannot"]: {"traps": [{"text": "The heavy-locker lane cannot be staged because no closed LWM container weighs "
                                     "76-249 kg; heavy locker caps at 58 kg.", "where": "closed_containers heavy lane"}]},
    T["gas"]: {"traps": [{"text": "The gas chain cannot pass a closed vent door, so sc_gas stops at five vents.",
                          "where": "sc_gas"}]},
    T["keep"]: {"traps": [{"text": "The bridge cannot read the pawn's flight tracker while the game is paused; read it "
                                   "on a running tick.", "where": "Pawn_FlightTracker"}]},
    T["quar"]: {"traps": [{"text": "Runs inside the Steve SIMD fault window (2026-11-08T00:57:39Z onward) were "
                                   "quarantined with no verdict; they are not passes or fails.", "where": "testq"}]},
    T["style"]: {"changed": "D1 fixed at abcd3002: a legacy winner's run stays legacy. D8 fixed at abcd3001: RunOf "
                            "walks through non-stylable conduit without painting it."},
    T["tap"]: {"proposed_fix": None, "defect": "Power-tap connect guards disagree on mixed nets, so a tap beside a foreign conduit is refused "
                         "or misconnects."}}


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
        ans[n] = [int(i) for i, t in re.findall(r"^\[(\d+)\] (.*)$", block, re.M) if "gas chain" in t]
    return ans, 0.01


CURRENT_ASKED = []
R.CALL = fake_call
res = B.run(root, MOD, read=True, budget_usd=5)
ALL = [e for e in M.read(root, MOD) if e["_shard"] == "BACKFILL"]
F = M.reduce(M.read(root, MOD))["findings"]


def on(k, kinds=None):
    tid = T.get(k, k)
    return [e for e in ALL if "item:" + tid in e["evidence"] and (kinds is None or e["kind"] in kinds)]


def traps(k):
    return [e["body"].get("text") or "" for e in on(k, ("trap.noted",))]


rec = B.RECORDS.get(MOD, {})
check("rule 1 (GSS 119): a close reason the ledger cut is read whole from the relentless item store before mining",
      "933/933" in rec.get(T["cut"], "") and "that is the environment, not the commit" in rec.get(T["cut"], ""),
      rec.get(T["cut"], "")[-400:])
check("rule 1 (GSS 119): a trap sentence stating a judgement the record does not state is not mined",
      not [t for t in traps("cut") if "weaker than it reads" in t], traps("cut"))
check("rule 2 (EK 51): a trap 'until <X>' is not mined once X (the reworded text) is in the mod's files",
      not [t for t in traps("until") if "exactly one cell" in t], traps("until"))
check("rule 2 control: a trap 'until <X>' whose X is nowhere in the mod's files stays",
      [t for t in traps("until") if "fresh census" in t], traps("until"))
check("rule 2 (EK 119): a 'cannot' trap is not mined once a later close of one of the mod's tickets did it",
      not traps("cannot"), traps("cannot"))
check("rule 2: a 'cannot' trap a later commit naming the mod may have lifted goes to the currency reader, with the "
      "commit; its answer 'lifted' drops it", not traps("gas") and any("abcd4001" in b for b in CURRENT_ASKED),
      (traps("gas"), CURRENT_ASKED))
check("rule 2 control: a 'cannot' trap no later commit or close touches stays", traps("keep"), traps("keep"))
check("rule 3 (GSS 74): a test-queue quarantine / re-queue note is no trap, and the reader is never handed it",
      not traps("quar") and "quarantined" not in rec.get(T["quar"], ""), (traps("quar"), rec.get(T["quar"], "")[-300:]))
check("rule 4 (GSS 361): a ticket whose every path is pipeline code (rimflow/, Utils/) mines nothing for the mod",
      not on(PIPE) and PIPE not in rec, [e["kind"] for e in on(PIPE)])
check("rule 4 control: a ticket naming the mod's own selftest under Utils/ stays the mod's",
      "finding:" + T["utils"] in F, sorted(F))
fs = F.get("finding:" + T["style"]) or {}
fs = dict(fs, **next((e["body"] for e in on("style", ("finding.claimed_fixed",))), {}))
check("rule 5 (GSS 246): the close's PASS rows are the test (row ids and evidence path), never 'none recorded'",
      "S12a" in str(fs.get("test")) and "PASS" in str(fs.get("test")) and "gss_B.log" in str(fs.get("test")), fs)
check("rule 5 (GSS 246): a close sha whose subject does not name the ticket gives way to the last fix sha the text "
      "names", fs.get("code_sha") == "abcd3002", fs.get("code_sha"))
check("rule 6 (GSS 260): a ledger-only ticket's spec reaches the reader (the failure mechanism is in its record)",
      "re-queues every net update forever" in rec.get(T["tap"], ""), rec.get(T["tap"], "")[:600])
check("rule 6 (GSS 260, FW 705): the reader is asked for the failure mechanism, not a paraphrase of the title",
      re.search(r"(?i)mechanism", R.SYSTEM) and re.search(r"title", R.SYSTEM.split("defect:", 1)[-1].split("\n- ", 1)[0]),
      R.SYSTEM.split("defect:", 1)[-1][:300])
ft = F.get("finding:" + T["tap"]) or {}
check("rule 6: an unread ledger-only ticket's spec is its proposed fix, never 'not written by its filer'",
      "not written by its filer" not in str(ft.get("proposed_fix")), ft)
fb = F.get("finding:" + T["bridge"]) or {}
fb = dict(fb, **next((e["body"] for e in on("bridge", ("finding.verified",))), {}))
check("FW 1043: a built ticket verified on some criteria names the criterion still unverified",
      fb.get("status") == "verified" and "A3" in str(fb.get("text")), fb)
check("the round-4 fixture lints clean and nothing it plans is refused", not M.lint(root, MOD, None)[0] and
      not res["refused"], (M.lint(root, MOD, None)[0][:3], res["refused"][:3]))

shutil.rmtree(root, ignore_errors=True)
shutil.rmtree(store, ignore_errors=True)
print("selftest_modledger_round4: %d failure%s" % (len(FAIL), "" if len(FAIL) == 1 else "s"))
sys.exit(1 if FAIL else 0)
