#!/usr/bin/env python3
"""Offline test: the Dispatch step launches the pilot holder runs the Conductor started by hand on 2026-11-15/16 (item
RIMMANDRAKE_DISPATCH_PILOT_HOLDER_RUN_ITSELF_HAND_LAUNCHED_TWICE). Temp root, fake launcher and filer: no unit starts,
nothing in the repo is written. Written before the code and watched failing on the base.

    python3 src/RimMandrake/rimflow/selftest_dispatch_pilot_holder.py      # "ALL PASS"

1. a Conductor decision recorded on the move that opened blind cycle N lets the tick launch cycle N, though the visit's
   automatic cycles are spent (GimmeSomeSlack read "auto_spent (cycle 2, 3, 4)" after cycle 6 was opened, 1:34 AM PST);
   never a second automatic try at that cycle; with no decision it stays auto_spent.
2. a pilot whose road-back fixers are spent, ledger ready and nothing live gets ONE holder run on all its open road-back
   items from the tick; again only when the open set shrank; a non-pilot stays fixer_spent.
3. a mod at the offline build waiting on its certificate with red deciders and no open item gets one item filed per red
   decider and one builder on them; never a second try at the same reds; stale stamps alone get no builder
   (their one zero-token rerun is selftest_maturation_dispatch.py --cert-rerun).
4. the ledger part of a launch (packet plus holder lines) fits packet_budget_tokens (trimmed), and a packet that cannot
   fit is refused with its lease revoked (FlowWorks launched at 15,093 tokens against 15,000, 12:15 AM PST).
5. a blind judge on a pilot writes as JUDGE.<run>, not as the holder: its verdicts append (a) with no lease to lapse (b);
   its brief carries none of the ledger's findings (c) and points at `judge-verify` for the claimed-fixed list, which
   leaves out the holder's story; its run end seals its shard, never flags NO_CHECKPOINT and records no holder session;
   the holder's session is never resumed for a judge. A holder brief says how to renew its lease.
"""
import datetime as dt
import json
import os
import shutil
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modledger as ML              # noqa: E402
import maturation as M              # noqa: E402
import maturation_dispatch as MD    # noqa: E402

res = []


def check(name, ok, detail=""):
    res.append(bool(ok))
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)[:600]))


def section(fn):
    try:
        fn()
    except Exception as e:      # noqa: BLE001  a missing function on the base is a FAIL, not a crash
        check("%s ran" % fn.__name__, False, "%s: %s\n%s" % (type(e).__name__, e, traceback.format_exc()[-800:]))


NOW = 1794822000.0              # 2026-11-16 ~1:40 AM PST, pinned
CFG = {"advancing": ["GimmeSomeSlack"], "cap_usd": 15, "blind_cap_usd": 20, "blind_enabled": True, "max_live": 4,
       "blind_auto_cycles_per_visit": 3, "settle_s": 180, "launch_tries": 3, "stage_ceiling_usd": 100, "seat": "BENCH",
       "model": "opus"}


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat()


def put_for(row):
    def put(decision, why, need=None):
        row["decision"], row["why"] = decision, why
        if need:
            row["need"] = need
    put.row = row
    return put


# ---- 1. a Conductor decision allows the cycle it opened ------------------------------------------------------------

def blind_case(decision, mine=None):
    rec = {"stage": "blind_challenge", "cycles": {"visit": 5, "total": 6}, "moves": [
        {"from": "offline_build", "to": "blind_challenge", "at": iso(NOW - 90000), "confirmed": {}},
        {"from": "blind_challenge", "to": "blind_challenge", "at": iso(NOW - 600),
         "confirmed": {"conductor_decision": "allow blind cycle 6"} if decision else {"steward_confirms": "x"}}]}
    vid = "0.1.0#2"
    s = {"blind_auto": [{"visit_id": vid, "cycle": c, "unit": "u-c%d" % c, "at": NOW - 20000 + c, "tries": 1}
                        for c in (2, 3, 4)] + (mine or [])}
    f = {"mod": "GimmeSomeSlack", "stage": "blind_challenge", "version": "0.1.0", "visit_first": 2, "cycle": 6,
         "owed": "cycle", "exit": {"state": "absent"}, "live_units": [], "last_end": NOW - 3000, "blind_runs": [],
         "killed": {}, "certificate": {"ok": True, "rows": []}, "box_runs": {}, "run_usd": {}}
    f["cycle_decision"] = MD.cycle_decision(rec)
    row = {"mod": "GimmeSomeSlack", "stage": "blind_challenge"}
    go = MD.decide_blind(CFG, s, f, row, put_for(row), NOW, (True, "acct ok"), 0, releases=[])
    return go, row, f


def t1_decision_opens_cycle():
    go, row, f = blind_case(True)
    check("1 the move's Conductor decision is read from the stage record", (f.get("cycle_decision") or {}).get(
        "text") == "allow blind cycle 6", f.get("cycle_decision"))
    check("1 a Conductor decision that opened cycle 6 launches it though cycles 2-4 spent the visit's three",
          go and row.get("decision") == "launch", row)
    go, row, _ = blind_case(False)
    check("1 control: with no decision on that move the visit stays auto_spent", not go and row.get("decision") ==
          "auto_spent", row)
    go, row, _ = blind_case(True, mine=[{"visit_id": "0.1.0#2", "cycle": 6, "unit": "u-c6", "at": NOW - 300,
                                        "tries": 1}])
    check("1 the decided cycle's own automatic run ended with no record: never a second try", not go and
          row.get("decision") == "stopped", row)
    check("1 no record or a stage elsewhere reads no decision", MD.cycle_decision({}) is None and MD.cycle_decision(
        {"stage": "offline_build", "moves": [{"to": "blind_challenge", "confirmed": {"conductor_decision": "x"}}]})
        is None)


# ---- temp ledger root --------------------------------------------------------------------------------------------

tmp = tempfile.mkdtemp(prefix="pilot_holder_")
root = os.path.join(tmp, "repo")
PILOT = ML.config()["pilot_mods"][0]
os.makedirs(os.path.join(root, "design", "concepts", PILOT, "ledger"))
os.environ["MATURATION_BRIEF_DIR"] = os.path.join(tmp, "briefs")
os.makedirs(os.environ["MATURATION_BRIEF_DIR"])
os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(tmp, "dispatch")
os.makedirs(os.environ["RM_MATURATION_DISPATCH_DIR"])
os.environ["RM_WORK_BUNDLE_DIR"] = os.path.join(tmp, "bundles")     # the holder's work-bundle record stays here
SENT = "SENTINEL_EARLIER_CYCLE_FINDING_TEXT"
CLAIM = "SENTINEL_HOLDER_STORY_OF_THE_FIX"
F1 = "finding:RIMMANDRAKE_TRACE_PILOT_HOLDER_FIXTURE_FINDING"
ML.append(root, PILOT, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0")
ML.append(root, PILOT, "JUDGE.J1", "finding.open", F1, run="J1", evidence=["run:J1"],
          body={"class": "problem", "bars": [], "tags": ["code"], "text": SENT + " the comp does not tick",
                "proposed_fix": "tick the comp from CompTickLong", "accept": "python3 t.py exits 0"})
TOK0 = ML.grant(root, PILOT, "H0")
ML.append(root, PILOT, "HOLDER.H0", "finding.claimed_fixed", F1, token=TOK0, code_sha="abc1234",
          body={"text": CLAIM, "test": "python3 t.py"})
ML.record_session(root, PILOT, "0a1b2c3d-1111-2222-3333-444455556666", 120000, lease="H0")
landed = []
FX = {"land_ledger": lambda paths: landed.append(paths) or "landed", "ready": lambda r, m: (True, "ready"),
      "bundle_extra": lambda mod, exclude: []}


# ---- 5. a blind judge writes as JUDGE.<run> ------------------------------------------------------------------------

def t5_judge():
    seen = {}

    def fake_launch(root_, mod, cap, item, **kw):
        seen.update(kw, item=item)
        return 0, "DETACHED rm-detached-bench-judge-1", "rm-detached-bench-judge-1"
    old = M.load
    M.load = lambda r, m: {"stage": "blind_challenge", "version": "0.1.0"} if m == PILOT else old(r, m)
    old_ready = MD.pilot_ledger
    MD.pilot_ledger = lambda r, m: m == PILOT
    try:
        st = {"mods": {PILOT: {}}}
        rc, text, unit = MD.launch_stage(root, CFG, st, PILOT, 20, "RIMMANDRAKE_JUDGE_X_BLIND_CYCLE_SIX", NOW, FX,
                                         launch=fake_launch)
        env = seen.get("env") or {}
        w = env.get("RM_MODLEDGER_WRITER", "")
        check("5a the judge's unit writes as JUDGE.<run>, not as the holder", rc == 0 and w.startswith("JUDGE."), env)
        run = w.split(".", 1)[1] if "." in w else None
        ev = ML.read(root, PILOT)
        starts = [e for e in ev if e.get("kind") == "run.start" and (e.get("body") or {}).get("run") == run]
        check("5a its run.start names role blind_judge and the JUDGE writer, and grants no holder lease",
              starts and starts[-1]["body"].get("role") == "blind_judge" and starts[-1]["body"].get("writer") == w
              and not [e for e in ev if e.get("kind") == "lease.grant" and (e.get("body") or {}).get("lease") == run],
              starts)
        try:
            eid, made = ML.append(root, PILOT, w, "finding.verified", F1, run=run, code_sha="abc1234",
                                  body={"text": "reran t.py on abc1234: PASS"}, env_writer=w,
                                  now=iso(NOW + 3 * 3600))
            ok, why = made, eid
        except Exception as e:      # noqa: BLE001
            ok, why = False, "%s: %s" % (type(e).__name__, e)
        check("5a+b its verdict appends three hours in (no lease to lapse)", ok, why)
        stt = ML.reduce(ML.read(root, PILOT))
        check("5a the verdict turns the finding green", stt["findings"][F1]["status"] == "verified", stt["findings"][F1])
        b = seen.get("preface") or ""
        check("5c the judge's brief carries no earlier finding and no holder story", b and SENT not in b and
              CLAIM not in b and "tick the comp" not in b, b[:400])
        check("5c the brief names how it writes verdicts and the judge-verify list", "judge-verify" in b and
              "--writer %s" % w in b and "--run %s" % run in b, b[:600])
        rec = st["mods"][PILOT].get("ledger_runs") or []
        check("5 the started judge run is remembered for its end", rec and rec[-1].get("writer") == w, rec)
        MD._write(os.path.join(MD.sdir(), "state.json"), st)
        rc2, t2 = MD.pilot_launch(root, CFG, PILOT, "selftest", item="RIMMANDRAKE_JUDGE_X_AGAIN", fx=dict(
            FX, record=lambda u: {"status": "running"}, launch=fake_launch), now=NOW + 60)
        check("5 a hand pilot-launch on a mod with a ledger run live is refused (two cycle-6 judges, 01:53 and 01:54 "
              "PST 2026-11-16)", rc2 == 2 and "rm-detached-bench-judge-1" in t2, t2)
        sessions = []
        fx = dict(FX, record=lambda u: {"status": "finished", "result": "success"},
                  session_of=lambda u: sessions.append(u) or ("ffffffff-judge", 90000))
        out = MD.end_ledger_runs(root, st, {}, NOW + 4 * 3600, fx)
        ev = ML.read(root, PILOT)
        ends = [e for e in ev if e.get("kind") == "run.end" and (e.get("body") or {}).get("run") == run]
        check("5 the judge's run end seals its shard", w in ML.seals(ev), out)
        check("5b the judge's run end is not flagged NO_CHECKPOINT", ends and "NO_CHECKPOINT" not in
              (ends[-1]["body"].get("flags") or []), ends)
        S = ML.reduce(ev)["session"] or {}
        check("5 the judge's session is never recorded as the holder's", S.get("session_id") ==
              "0a1b2c3d-1111-2222-3333-444455556666" and not sessions, (S, sessions))
        vt = MD.judge_verify_text(root, PILOT)
        check("5c judge-verify lists nothing once the claim is verified", F1 not in vt, vt[:300])
    finally:
        M.load, MD.pilot_ledger = old, old_ready


def t5_verify_list_and_resume():
    F2 = "finding:RIMMANDRAKE_TRACE_PILOT_SECOND_FIXTURE_FINDING"
    ML.append(root, PILOT, "JUDGE.J2", "finding.open", F2, run="J2", evidence=["run:J2"],
              body={"class": "problem", "bars": [], "tags": ["code"], "text": "the hose shows in the menu",
                    "proposed_fix": "drop the hose label in Settings.cs", "accept": "python3 nohose.py exits 0"})
    tok = ML.grant(root, PILOT, "H2")
    ML.append(root, PILOT, "HOLDER.H2", "finding.claimed_fixed", F2, token=tok, code_sha="def5678",
              body={"text": CLAIM + " two", "test": "python3 nohose.py"})
    vt = MD.judge_verify_text(root, PILOT)
    check("5c judge-verify lists a claimed-fixed finding, its reproduction and its test", F2 in vt and
          "the hose shows in the menu" in vt and "python3 nohose.py" in vt, vt[:400])
    check("5c judge-verify leaves out the holder's story", CLAIM not in vt, vt[:400])
    old = MD.pilot_ledger
    MD.pilot_ledger = lambda r, m: m == PILOT
    try:
        row = {"mod": PILOT, "stage": "blind_challenge", "stage_usd": 10}
        cap, kw = MD.holder_launch(root, CFG, {}, row, 20, FX)
        check("5 a blind judge never resumes the holder's session", "session" not in kw, kw)
        row = {"mod": PILOT, "stage": "offline_build", "stage_usd": 10}
        cap, kw = MD.holder_launch(root, CFG, {}, row, 15, FX)
        check("5 control: a holder at the offline build still resumes it", kw.get("session"), kw)
    finally:
        MD.pilot_ledger = old


# ---- 4. the packet line ------------------------------------------------------------------------------------------

def t4_packet_line():
    F3 = "finding:RIMMANDRAKE_TRACE_PILOT_THIRD_OPEN_FIXTURE"
    ML.append(root, PILOT, "JUDGE.J3", "finding.open", F3, run="J3", evidence=["run:J3"],
              body={"class": "problem", "bars": [], "tags": ["code"], "text": "SENTINELOPENTEXT the pit floods dry",
                    "proposed_fix": "flood the pit in Flood.cs", "accept": "python3 flood.py exits 0"})
    t, _ = ML.packet_from(PILOT, ML.read(root, PILOT), budget=1)
    check("4 the briefest packet names every open finding but prints none of its text (FlowWorks' 246 open findings "
          "held the packet at 14,694 tokens)", F3[len("finding:"):] in t and "SENTINELOPENTEXT" not in t, t[-500:])
    budget = 2000     # real tokens (chars / 1.8): the fixture's packet and holder lines need ~1.8k
    out = ML.launch(root, PILOT, "run-fit", "builder", stage="offline_build", budget=budget)
    check("4 the ledger part of a launch (packet and holder lines) fits the line", ML.tokens(out["brief"]) <= budget,
          ML.tokens(out["brief"]))
    try:
        ML.launch(root, PILOT, "run-over", "builder", stage="offline_build", budget=120)
        ok, why = False, "launched"
    except ML.ModLedgerError as e:
        ok, why = "over" in str(e).lower() or "budget" in str(e).lower(), str(e)
    check("4 a packet that cannot fit the line is refused", ok, why)
    by, cur = ML.leases(ML.read(root, PILOT))
    check("4 the refused launch's lease is revoked, so no stale holder holds the mod",
          by.get("run-over", {}).get("released") is True, by.get("run-over"))
    ev = ML.read(root, PILOT)
    check("4 the refused launch records no run.start", not [e for e in ev if e.get("kind") == "run.start" and
                                                           (e.get("body") or {}).get("run") == "run-over"])
    old = ML.config()["packet_budget_tokens"]
    try:
        led = MD.ledger_open(root, PILOT, "builder", "stage brief", stage="offline_build", now=NOW + 50, fx=FX)
        check("4 the dispatcher's launch counts packet and holder lines against packet_budget_tokens",
              ML.tokens(led["packet"]) <= old, ML.tokens(led["packet"]))
        check("5b a holder's brief says how to renew its lease", "lease.renew" in led["brief"], led["brief"][-600:])
        w = led["env"]["RM_MODLEDGER_WRITER"]
        try:
            ML.append(root, PILOT, w, "lease.renew", "lease", token=int(led["env"]["RM_MODLEDGER_TOKEN"]),
                      body={}, env_writer=w)
            ok, why = True, ""
        except Exception as e:      # noqa: BLE001
            ok, why = False, "%s: %s" % (type(e).__name__, e)
        check("5b the renewal the brief names is accepted", ok, why)
    finally:
        ML.config()["packet_budget_tokens"] = old


# ---- 2. the road-back holder from the tick -----------------------------------------------------------------------

def t2_road_back_holder():
    launched = []

    def fake_brief(item, text, model, cap, seat="BENCH", env=None, session=None, **k):
        launched.append({"item": item, "text": text, "env": env, "session": session})
        return 0, "DETACHED rm-holder-%d" % len(launched), "rm-holder-%d" % len(launched)
    open_now = [{"id": "RIMMANDRAKE_FIX_A_ONE", "needs": "offline"}, {"id": "RIMMANDRAKE_FIX_B_TWO", "needs": "offline"}]
    fx = dict(FX, launch_brief=fake_brief, open_items=lambda ids: list(open_now))
    cfg = dict(CFG, advancing=[PILOT, "Pyrelands"])
    st = {"mods": {PILOT: {"road_back": {"caused_by": "RIMMANDRAKE_STEWARD_X", "at": NOW - 900, "had_items": True},
                           "fixers": {"RIMMANDRAKE_FIX_A_ONE": {}, "RIMMANDRAKE_FIX_B_TWO": {}}},
                   "Pyrelands": {"road_back": {"caused_by": "RIMMANDRAKE_STEWARD_Y", "at": NOW - 900}}}}
    facts = {PILOT: {"stage": "offline_build", "live_units": []}, "Pyrelands": {"stage": "offline_build",
                                                                                "live_units": []}}

    def rows():
        return [{"mod": PILOT, "stage": "offline_build", "decision": "fixer_spent", "why": "spent", "live": []},
                {"mod": "Pyrelands", "stage": "offline_build", "decision": "fixer_spent", "why": "spent", "live": []}]
    old = MD.pilot_ledger
    MD.pilot_ledger = lambda r, m: m == PILOT
    try:
        rs, la = MD.pilot_holders(root, cfg, st, facts, rows(), [], NOW, fx)
        by = {r["mod"]: r for r in rs}
        check("2 a pilot with its fixers spent, ledger ready and nothing live gets a holder launch from the tick",
              PILOT in la and by[PILOT]["decision"] == "launch" and not by[PILOT].get("aut"), by[PILOT])
        check("2 a non-pilot stays fixer_spent", "Pyrelands" not in la and by["Pyrelands"]["decision"] ==
              "fixer_spent", by["Pyrelands"])
        MD.execute(root, cfg, st, rs, la, NOW, dict(fx, known=lambda: set()))
        check("2 one holder run is started on all the open road-back items together", len(launched) == 1 and
              "RIMMANDRAKE_FIX_A_ONE" in launched[0]["text"] and "RIMMANDRAKE_FIX_B_TWO" in launched[0]["text"] and
              (launched[0]["env"] or {}).get("RM_MODLEDGER_WRITER", "").startswith("HOLDER."), launched)
        check("2 the holder run is the mod's work bundle: RM_WORK_BUNDLE in its env, the bundle named in its brief",
              (launched[0]["env"] or {}).get("RM_WORK_BUNDLE", "").startswith("WB-mod-") and
              launched[0]["env"]["RM_WORK_BUNDLE"] in launched[0]["text"], launched[0].get("env"))
        check("2 the launch is booked on the mod with its item set", (st["mods"][PILOT].get("holder_road_back") or [{}])
              [-1].get("ids") == ["RIMMANDRAKE_FIX_A_ONE", "RIMMANDRAKE_FIX_B_TWO"], st["mods"][PILOT])
        facts[PILOT]["live_units"] = ["rm-holder-1"]
        rs, la = MD.pilot_holders(root, cfg, st, facts, [dict(rows()[0], decision="live", live=["rm-holder-1"])], [],
                                  NOW + 60, fx)
        check("2 nothing more while it is live", PILOT not in la, rs[0])
        facts[PILOT]["live_units"] = []
        rs, la = MD.pilot_holders(root, cfg, st, facts, rows()[:1], [], NOW + 7200, fx)
        check("2 it ended with the same items open: never a second holder run on them", PILOT not in la and
              rs[0]["decision"] == "holder_spent" and rs[0].get("need"), rs[0])
        del open_now[0]
        rs, la = MD.pilot_holders(root, cfg, st, facts, rows()[:1], [], NOW + 7300, fx)
        check("2 once the open set shrank, the next holder run starts", PILOT in la, rs[0])
        st2 = {"mods": {PILOT: {"road_back": {"caused_by": "RIMMANDRAKE_STEWARD_X", "at": NOW - 900},
                                "pilot_launches": [{"at": NOW - 100, "item": "RIMMANDRAKE_FIX_B_TWO", "unit": "rm-h",
                                                    "stage": "offline_build"}]}}}
        rs, la = MD.pilot_holders(root, cfg, st2, facts, rows()[:1], [], NOW + 60, fx)
        check("2 a hand pilot-launch on the same open item counts as that holder run", PILOT not in la and
              rs[0]["decision"] == "holder_spent", rs[0])
        full = dict(cfg, max_live=1)
        facts2 = dict(facts, Pyrelands={"stage": "offline_build", "live_units": ["rm-other"]})
        st3 = {"mods": {PILOT: {"road_back": {"caused_by": "RIMMANDRAKE_STEWARD_X", "at": NOW - 900}}}}
        rs, la = MD.pilot_holders(root, full, st3, facts2, rows()[:1], [], NOW, fx)
        check("2 no holder launch past max_live", PILOT not in la and rs[0]["decision"] == "slots_full", rs[0])
    finally:
        MD.pilot_ledger = old


# ---- 3. red deciders get their item and builder ------------------------------------------------------------------

def cert(reds, stale=()):
    rows = []
    for t in reds:
        rows.append({"bar": "bar_" + t.lower(), "test": t, "clause": "green", "status": "REFUSED",
                     "observed": "rc 1, result None", "smallest_fix": "fix the mod or the test"})
    for t in stale:
        rows.append({"bar": "bar_" + t.lower(), "test": t, "clause": "ran_on_this_build", "status": "REFUSED",
                     "observed": "no build", "smallest_fix": "certificate --run"})
    return {"ok": not rows, "rows": rows}


def off_facts(c, live=()):
    return {"FlowWorks": {"stage": "offline_build", "owed": "certificate", "live_units": list(live),
                          "certificate": c, "certificate_why": "refused", "certificate_fix": "certificate --run",
                          "stage_runs": {}, "run_usd": {}, "bar_fp": "fp"}}


def t3_cert_reds():
    cfg = dict(CFG, advancing=["FlowWorks"])
    st = {"mods": {}}
    c = cert(["T_FETCH_FALLEN_OFFLINE", "T_TOSS_FLAME_OFFLINE"], stale=["PY_A"])
    rows, la = MD.decide(cfg, st, off_facts(c), NOW, (True, "ok"), releases=[])
    check("3 red deciders with no open item: the tick launches on them", la == ["FlowWorks"] and
          rows[0].get("cert_reds") == ["T_FETCH_FALLEN_OFFLINE", "T_TOSS_FLAME_OFFLINE"], rows[0])
    rows2, la2 = MD.decide(cfg, {"mods": {}}, off_facts(cert([], stale=["PY_A"])), NOW, (True, "ok"), releases=[])
    check("3 control: stale stamps alone get no builder, only the zero-token certificate rerun "
          "(RIMMANDRAKE_RERUN_STALE_CERTIFICATE_STAMPS_NOBODY_OWNS_IT)", not rows2[0].get("cert_reds")
          and rows2[0].get("cert_rerun_key") and la2 == ["FlowWorks"], rows2[0])
    filed, launched = [], []

    def fake_file(item, title, why, needs="offline", spec=None):
        filed.append({"item": item, "title": title, "needs": needs})
        return True, "filed %s" % item

    def fake_brief(item, text, model, cap, seat="BENCH", env=None, session=None, **k):
        launched.append({"item": item, "text": text, "cap": cap})
        return 0, "DETACHED rm-cert-1", "rm-cert-1"
    fx = dict(FX, file=fake_file, launch_brief=fake_brief, known=lambda: set(), ended=lambda ids: set())
    MD.execute(root, cfg, st, rows, la, NOW, fx)
    names = [x["item"] for x in filed]
    check("3 one item is filed per red decider, each naming it", len(filed) == 2 and all(
        t in " ".join(x["title"] for x in filed) for t in ("T_FETCH_FALLEN_OFFLINE", "T_TOSS_FLAME_OFFLINE")), filed)
    import subprocess
    bad = [n for n in names if subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), "namecheck", n],
                                              capture_output=True, text=True, timeout=60).returncode]
    check("3 every filed name passes rimflow namecheck", names and not bad, bad)
    check("3 one builder is launched on all of them, told to rerun the certificate first", len(launched) == 1 and
          all(n in launched[0]["text"] for n in names) and "certificate FlowWorks --run" in launched[0]["text"],
          launched)
    check("3 the run is booked against the reds", (st["mods"]["FlowWorks"].get("cert_red") or {}).get("tests") ==
          ["T_FETCH_FALLEN_OFFLINE", "T_TOSS_FLAME_OFFLINE"] and rows[0].get("decision") == "launched", (
              st["mods"]["FlowWorks"], rows[0]))
    rows, la = MD.decide(cfg, st, off_facts(c), NOW + 7200, (True, "ok"), releases=[])
    check("3 the builder ended with the same reds: never a second try, a Needs Conductor line", not la and
          rows[0]["decision"] == "stopped" and rows[0].get("need"), rows[0])
    rows, la = MD.decide(cfg, st, off_facts(cert(["T_TOSS_FLAME_OFFLINE"])), NOW + 7300, (True, "ok"), releases=[])
    check("3 once the reds shrank, the next builder may launch", la == ["FlowWorks"], rows[0])
    filed.clear()
    MD.execute(root, cfg, st, rows, la, NOW + 7300, fx)
    check("3 a red decider whose item is still open is not filed again", not filed and launched[-1]["text"].count(
        names[1]) >= 1, (filed, launched[-1]["text"][:300]))
    failed = {"mods": {"FlowWorks": {"cert_red": {"tests": ["T_FETCH_FALLEN_OFFLINE", "T_TOSS_FLAME_OFFLINE"],
                                                 "unit": None, "at": NOW - 600, "failed": "REFUSED: packet over the line",
                                                 "tries": 1, "code": "tree-a"}}}}
    rows, la = MD.decide(dict(cfg, _code="tree-a"), failed, off_facts(c), NOW, (True, "ok"), releases=[])
    check("3 a launch refused on a defect is not retried on the same code", not la and rows[0]["decision"] ==
          "stopped", rows[0])
    rows, la = MD.decide(dict(cfg, _code="tree-b"), failed, off_facts(c), NOW, (True, "ok"), releases=[])
    check("3 it is retried once the pipeline's code has changed", la == ["FlowWorks"], rows[0])
    rows, la = MD.decide(cfg, {"mods": {}}, off_facts(c, live=["rm-x"]), NOW, (True, "ok"), releases=[])
    check("3 nothing while a run is live on the mod", not la and rows[0]["decision"] == "live", rows[0])


for fn in (t1_decision_opens_cycle, t5_judge, t5_verify_list_and_resume, t4_packet_line, t2_road_back_holder,
           t3_cert_reds):
    section(fn)
shutil.rmtree(tmp, ignore_errors=True)
print("ALL PASS" if all(res) else "FAILED %d of %d" % (res.count(False), len(res)))
sys.exit(0 if all(res) else 1)
