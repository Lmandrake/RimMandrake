#!/usr/bin/env python3
"""selftest_stop_resume: a fleet stop (an account switch or a hard stop) never leaves a detached run dead and
unresumed (RIMMANDRAKE_CHECKPOINT_HARD_STOP_NOT_KILL, 2026-11-17: the 03:35 hard stop killed a 3 h 40 min Fable run
and nothing brought it back until a hand relaunch at 05:57).

Hermetic: a temp run-record dir, plan log, claude-account log, plan notice, repo (items, maturation books), projects
dir and conductor log; a fake launch and a fake systemctl. Cases:
  A  resumable run killed by a switch           -> relaunched once, same session, note names the stop and the bundle
  B  run with no transcript, brief saved        -> relaunched from its brief plus the note, no session
  C  run that finished normally (result JSON)   -> never relaunched
  D  run killed but already relaunched by hand  -> not relaunched; marked resumed_by the later run
  E  hard stop, no headroom                     -> parked (one conductor line), then resumed by a pass with headroom
  F  a second sweep                             -> launches nothing (no double launch)
  G  maturation-owned run, closed item, kill not on a stop, stop before the cutoff -> never relaunched
  H  no spend, cap or remainder in any note; unit dead with finish never run counts as killed
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_stop_resume_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
sys.path.insert(0, HERE)
import detached_helper as DH  # noqa: E402
import stop_resume as SR  # noqa: E402

FAILS = []
T_STOP = 1_800_000_000.0          # the switch's fleet stop
PLAN_DIR = os.path.join(TMP, "plan")
ACCT_LOG = os.path.join(TMP, "accounts_log.jsonl")
REPO = os.path.join(TMP, "repo")
PROJECTS = os.path.join(TMP, "projects")
STATE = os.environ["RM_DISPATCHER_STATE"]


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (": " + detail if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


class R:
    def __init__(self, rc=0, out=""):
        self.returncode, self.stdout, self.stderr = rc, out, ""


def systemctl(argv, **kw):
    """every unit is gone (the fleet stop killed them all) but the one that outlived it"""
    if argv[:1] != ["systemctl"]:
        return R(1, "")
    return R(0, "active\n" if any("alive" in a for a in argv) else "inactive\n")


def iso(t):
    return DH.iso(t)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def rec(name, item, at, **kw):
    unit = "rm-detached-bench-%s-%d" % (name, int(at))
    r = {"seat": "BENCH", "item": item, "clone": os.path.join(TMP, "clones", item + ".det"), "model": "opus",
         "max_s": None, "budget_usd": 20.0, "at": at, "state": STATE, "status": "finished", "unit": unit,
         "out": os.path.join(DH.runs_dir(STATE), unit + ".out.json"), "err": os.path.join(DH.runs_dir(STATE), unit + ".err")}
    r.update(kw)
    DH.write_record(r, STATE)
    return unit


def plan_line(do, at, acted=False, rc=0, to=None):
    res = {}
    if acted and do == "switch":
        res = {"use": [rc, "archmagi now on %s; stopped 4 Claude process(es)" % to]}
    elif acted and do == "stop":
        res = {"fleet-stop": [rc, "stopped 4, survivors []"]}
    return json.dumps({"acted": acted, "at": iso(at), "do": do, "live": "lukas", "to": to, "why": "test",
                       **({"result": res} if res else {})}) + "\n"


def set_plan(lines, notice_state="none", notice_at=None):
    write(os.path.join(PLAN_DIR, "log.jsonl"), "".join(lines))
    write(os.path.join(PLAN_DIR, "notice.json"), json.dumps({"state": notice_state, "at": iso(notice_at or T_STOP)}))


class Launcher:
    def __init__(self):
        self.calls = []

    def __call__(self, seat, item, brief, model, max_s, budget, **kw):
        n = len(self.calls)
        self.calls.append({"seat": seat, "item": item, "brief": brief, "model": model, "max_s": max_s, "budget": budget,
                           **kw})
        new = rec("relaunch%d" % n, item, kw.get("now") + n, status="running")
        return 0, "DETACHED %s\nclone x" % new


def sweep(launcher, now, **kw):
    return SR.sweep(now=now, root=STATE, plan_dir=PLAN_DIR, acct_log=ACCT_LOG, repo=REPO, projects=PROJECTS,
                    launch_fn=launcher, runner=systemctl, cutoff=T_STOP - 86400, **kw)


def main():
    os.makedirs(DH.runs_dir(STATE), exist_ok=True)
    write(os.path.join(REPO, "infrastructure/state/items/ITEM_A.md"), "## spec\nA\n")
    write(os.path.join(REPO, "infrastructure/state/items/closed/ITEM_CLOSED.md"), "## spec\nshut\n")
    at = T_STOP - 3600
    # A: resumable (its session id on the record)
    a = rec("a", "ITEM_A", at, resume_session="11111111-aaaa-bbbb-cccc-000000000001", ended=T_STOP - 3,
            result="killed: exit-code (exited 143)", returned=T_STOP + 20, bundle="/bundles/20261117-ITEM_A.det")
    write(os.path.join(PROJECTS, "-x", "11111111-aaaa-bbbb-cccc-000000000001.jsonl"), '{"type":"user"}\n')
    # A2: resumable by its clone's transcript only (no resume_session on the record)
    a2_clone = os.path.join(TMP, "clones", "ITEM_A2.det")
    a2 = rec("a2", "ITEM_A2", at + 5, ended=T_STOP - 2, result="killed: exit-code (exited 143)", returned=T_STOP + 20)
    write(os.path.join(DH.project_dir(a2_clone, PROJECTS), "22222222-aaaa-bbbb-cccc-000000000002.jsonl"),
          json.dumps({"type": "user", "timestamp": iso(at + 8), "sessionId": "22222222-aaaa-bbbb-cccc-000000000002",
                      "message": {"role": "user", "content": "Do it.\n\nItem: ITEM_A2"}}) + "\n")
    write(os.path.join(DH.project_dir(a2_clone, PROJECTS), "33333333-aaaa-bbbb-cccc-000000000003.jsonl"),
          json.dumps({"type": "user", "timestamp": iso(at - 20000), "sessionId": "33333333-aaaa-bbbb-cccc-000000000003"}) + "\n")
    # B: no transcript, brief saved
    bsrc = os.path.join(DH.runs_dir(STATE), "b.brief.src.md")
    write(bsrc, "Build item B: the original brief.\n")
    b = rec("b", "ITEM_B", at + 10, brief_src=bsrc, ended=T_STOP - 2, result="killed: exit-code (exited 143)",
            returned=T_STOP + 20)
    # B2: no transcript, no brief -> refused, said so
    b2 = rec("b2", "ITEM_B2", at + 11, ended=T_STOP - 2, result="killed: exit-code (exited 143)", returned=T_STOP + 20)
    # C: finished normally (its result JSON exists)
    c = rec("c", "ITEM_C", at + 20, ended=T_STOP - 2, result="ok", returned=T_STOP + 20)
    write(os.path.join(DH.runs_dir(STATE), c + ".out.json"), json.dumps({"result": "done", "usage": {}}))
    # D: killed, already relaunched by hand (a later record of the same item)
    d = rec("d", "ITEM_D", at + 30, resume_session="44444444-aaaa-bbbb-cccc-000000000004", ended=T_STOP - 2,
            result="killed: exit-code (exited 143)", returned=T_STOP + 20)
    d_new = rec("dnew", "ITEM_D", T_STOP + 100, status="running")
    write(os.path.join(PROJECTS, "-x", "44444444-aaaa-bbbb-cccc-000000000004.jsonl"), '{"type":"user"}\n')
    # H: unit dead, finish never ran (status running, no ended)
    h = rec("h", "ITEM_H", at + 40, status="running", resume_session="55555555-aaaa-bbbb-cccc-000000000005")
    write(os.path.join(PROJECTS, "-x", "55555555-aaaa-bbbb-cccc-000000000005.jsonl"), '{"type":"user"}\n')
    # G: never relaunched
    g_mat = rec("gmat", "RIMMANDRAKE_JUDGE_X_BLIND_CYCLE", at + 50, ended=T_STOP - 2, result="killed: x", returned=T_STOP)
    write(os.path.join(REPO, "design/concepts/ModX/version/stage_record.json"), json.dumps({"boxes": {"b": {"runs": [
        {"unit": g_mat}]}}}))
    g_closed = rec("gclosed", "ITEM_CLOSED", at + 51, ended=T_STOP - 2, result="killed: x", returned=T_STOP)
    g_off = rec("goff", "ITEM_OFF", at + 52, ended=T_STOP - 5000, result="killed: x", returned=T_STOP - 4000)
    g_old = rec("gold", "ITEM_OLD", T_STOP - 200000, ended=T_STOP - 190000, result="killed: x", returned=T_STOP - 189000)
    # T: two runs of one item (a builder and its judge) both killed at the stop: the later one is no relaunch of the first
    tsrc = os.path.join(DH.runs_dir(STATE), "t.brief.src.md")
    write(tsrc, "Build item T.\n")
    t1 = rec("t1", "ITEM_T", at + 60, brief_src=tsrc, ended=T_STOP - 2, result="killed: x", returned=T_STOP + 20)
    t2 = rec("t2", "ITEM_T", at + 61, brief_src=tsrc, ended=T_STOP - 2, result="killed: x", returned=T_STOP + 20)
    # V: a run that outlived the stop (its unit is still active) is left alone
    v = rec("alive", "ITEM_V", at + 65, status="running", brief_src=tsrc)
    # K: a run handed its clone (--clone): resumed in that same clone, which its return kept
    kept = os.path.join(TMP, "kept", "K.clone")
    os.makedirs(kept, exist_ok=True)
    k = rec("k", "ITEM_K", at + 70, brief_src=tsrc, clone=kept, clone_how="given " + kept, ended=T_STOP - 2,
            result="killed: x", returned=T_STOP + 20)

    # the switch: the plan's acted line and claude-account's use line; an older stop before the cutoff
    set_plan([plan_line("stop", T_STOP - 190000 + 2, acted=True),
              plan_line("switch", T_STOP + 5, acted=True, to="steven"), plan_line("normal", T_STOP + 300)])
    write(ACCT_LOG, json.dumps({"op": "use", "from": "lukas", "to": "steven", "changed": True, "ts": iso(T_STOP + 4)}) + "\n")

    # base: the scan sees the dead runs as owed
    owed = SR.scan(now=T_STOP + 310, root=STATE, plan_dir=PLAN_DIR, acct_log=ACCT_LOG, repo=REPO, projects=PROJECTS,
                   runner=systemctl, cutoff=T_STOP - 86400)
    owe_units = {x["unit"] for x in owed if x["act"] in ("resume", "park")}
    check("scan: the killed runs are owed a resume", {a, a2, b, h} <= owe_units, sorted(owe_units))

    L = Launcher()
    acts = sweep(L, T_STOP + 310)
    by = {x["unit"]: x for x in acts}
    launched = {c["item"]: c for c in L.calls}
    check("A: resumed once", list(launched).count("ITEM_A") == 1 and by.get(a, {}).get("act") == "resumed", str(by.get(a)))
    ca = launched.get("ITEM_A") or {}
    check("A: same session", ca.get("resume_session") == "11111111-aaaa-bbbb-cccc-000000000001", str(ca.get("resume_session")))
    check("A: same model, seat, budget", (ca.get("model"), ca.get("seat"), ca.get("budget")) == ("opus", "BENCH", 20.0))
    check("A: note names the stop and the bundle", "account switch" in (ca.get("brief") or "")
          and "/bundles/20261117-ITEM_A.det" in (ca.get("brief") or ""), (ca.get("brief") or "")[:300])
    ra = DH.read_record(a, STATE)
    check("A: old record names its successor", (ra or {}).get("resumed_by", "").startswith("rm-detached-bench-relaunch"))
    c2 = launched.get("ITEM_A2") or {}
    check("A2: session found by its clone's transcript", c2.get("resume_session") == "22222222-aaaa-bbbb-cccc-000000000002",
          str(c2.get("resume_session")))
    cb = launched.get("ITEM_B") or {}
    check("B: relaunched from its brief, no session", not cb.get("resume_session")
          and "Build item B: the original brief." in (cb.get("brief") or ""), str(cb)[:200])
    check("B2: no brief, no session -> refused and said so", "ITEM_B2" not in launched
          and by.get(b2, {}).get("act") == "refused", str(by.get(b2)))
    check("C: a run that finished is never relaunched", "ITEM_C" not in launched)
    check("T: two runs of one item killed together are both resumed",
          [c["item"] for c in L.calls].count("ITEM_T") == 2 and by.get(t1, {}).get("act") == by.get(t2, {}).get("act")
          == "resumed", "%s %s" % (by.get(t1, {}).get("act"), by.get(t2, {}).get("act")))
    check("V: a run whose unit outlived the stop is not relaunched", "ITEM_V" not in launched and v not in by, str(by.get(v)))
    ck = launched.get("ITEM_K") or {}
    check("K: a given clone is resumed in that clone", ck.get("clone") == kept and kept in (ck.get("brief") or ""),
          str(ck.get("clone")))
    check("A: a pool clone is synced afresh (no clone handed in)", ca.get("clone") is None, str(ca.get("clone")))
    check("D: a run relaunched by hand is not relaunched", "ITEM_D" not in launched)
    check("D: marked resumed_by the later run", (DH.read_record(d, STATE) or {}).get("resumed_by") == d_new)
    check("H: dead unit, finish never ran -> resumed", "ITEM_H" in launched)
    for u, why in ((g_mat, "maturation-owned"), (g_closed, "closed item"), (g_off, "kill not on a stop"),
                   (g_old, "stop before the cutoff")):
        it = (DH.read_record(u, STATE) or {}).get("item")
        check("G: %s never relaunched" % why, it not in launched)
    words = ("$", "usd", "budget", "spend", "remain", "cap")
    bad = [c["item"] for c in L.calls if any(w in c["brief"].lower() for w in words)]
    check("H: no spend, cap or remainder in any note", not bad, str(bad))
    with open(os.environ["RM_CONDUCTOR_LOG"], encoding="utf-8") as f:
        clog = f.read()
    check("conductor log: one line per resume and refusal", clog.count(a) >= 1 and clog.count(b2) >= 1, clog[-400:])

    n = len(L.calls)
    sweep(L, T_STOP + 620)
    check("F: a second sweep launches nothing", len(L.calls) == n, str([c["item"] for c in L.calls[n:]]))

    # E: hard stop, no headroom -> parked, then resumed once headroom returns
    T2 = T_STOP + 40000
    e = rec("e", "ITEM_E", T2 - 3000, resume_session="66666666-aaaa-bbbb-cccc-000000000006", ended=T2 - 2,
            result="killed: exit-code (exited 143)", returned=T2 + 20)
    write(os.path.join(PROJECTS, "-x", "66666666-aaaa-bbbb-cccc-000000000006.jsonl"), '{"type":"user"}\n')
    set_plan([plan_line("stop", T2, acted=True), plan_line("stopped", T2 + 300)], notice_state="stop", notice_at=T2 + 300)
    L2 = Launcher()
    acts = sweep(L2, T2 + 310)
    check("E: no headroom -> nothing launched", L2.calls == [], str(L2.calls)[:200])
    check("E: parked on its record", bool((DH.read_record(e, STATE) or {}).get("parked")), str(DH.read_record(e, STATE))[:200])
    sweep(L2, T2 + 610)
    with open(os.environ["RM_CONDUCTOR_LOG"], encoding="utf-8") as f:
        check("E: parked is said once", f.read().count("parked " + e) == 1)
    set_plan([plan_line("stop", T2, acted=True), plan_line("stopped", T2 + 300),
              plan_line("start", T2 + 9000, acted=True), plan_line("normal", T2 + 9300)])
    sweep(L2, T2 + 9310)
    ce = [c for c in L2.calls if c["item"] == "ITEM_E"]
    check("E: resumed once headroom returns, same session", len(ce) == 1
          and ce[0].get("resume_session") == "66666666-aaaa-bbbb-cccc-000000000006", str(ce)[:200])
    check("E: its note says hard stop", ce and "hard stop" in ce[0]["brief"], (ce[0]["brief"] if ce else "")[:200])

    # a refused launch counts tries and stops at the cap
    T3 = T_STOP + 80000
    rf = rec("rf", "ITEM_RF", T3 - 3000, resume_session="77777777-aaaa-bbbb-cccc-000000000007", ended=T3 - 2,
             result="killed: exit-code (exited 143)", returned=T3 + 20)
    write(os.path.join(PROJECTS, "-x", "77777777-aaaa-bbbb-cccc-000000000007.jsonl"), '{"type":"user"}\n')
    set_plan([plan_line("switch", T3, acted=True, to="system"), plan_line("normal", T3 + 300)])
    tries = []

    def refuse(*a_, **kw):
        tries.append(1)
        return 2, "refused: test"
    for k in range(SR.MAX_TRIES + 2):
        sweep(refuse, T3 + 310 + k * 300)
    check("a refused resume is tried at most MAX_TRIES times", len(tries) == SR.MAX_TRIES,
          "%d tries, cap %d" % (len(tries), SR.MAX_TRIES))
    review_cases()

    wiring()
    print("%d checks failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


def review_cases():
    """The 2026-11-17 review's counterexamples, each a case."""
    def items(L):
        return [c["item"] for c in L.calls]

    # TW: a twin launched 30 s before the stop, both killed by it, is no relaunch of the older one
    T4 = T_STOP + 120000
    tsrc = os.path.join(DH.runs_dir(STATE), "tw.brief.src.md")
    write(tsrc, "Build item TW.\n")
    tw1 = rec("tw1", "ITEM_TW", T4 - 3600, brief_src=tsrc, ended=T4 - 2, result="killed: x", returned=T4 + 20)
    tw2 = rec("tw2", "ITEM_TW", T4 - 30, brief_src=tsrc, ended=T4 - 2, result="killed: x", returned=T4 + 20)
    # S: a given clone where another session began during the run: the run's own transcript is the one resumed
    s_clone = os.path.join(TMP, "kept", "S.clone")
    os.makedirs(s_clone, exist_ok=True)
    s = rec("s", "ITEM_S", T4 - 3000, clone=s_clone, clone_how="given " + s_clone, ended=T4 - 2, result="killed: x",
            returned=T4 + 20)
    # (and a window opened there by hand as the launch prepared: an interactive session, entrypoint "cli")
    for sid, t, ep in (("88888888-aaaa-bbbb-cccc-000000000008", T4 - 3000 + 4, "sdk-cli"),
                       ("99999999-aaaa-bbbb-cccc-000000000009", T4 - 1000, "sdk-cli"),
                       ("12121212-aaaa-bbbb-cccc-000000000012", T4 - 3000 + 1, "cli")):
        write(os.path.join(DH.project_dir(s_clone, PROJECTS), sid + ".jsonl"),
              json.dumps({"type": "user", "timestamp": iso(t), "sessionId": sid, "entrypoint": ep,
                          "message": {"role": "user", "content": [{"type": "text", "text": "Work on ITEM_S."}]}}) + "\n")
    set_plan([plan_line("switch", T4, acted=True, to="system"), plan_line("normal", T4 + 300)])
    L = Launcher()
    by = {x["unit"]: x for x in sweep(L, T4 + 310)}
    check("TW: a twin launched just before the stop does not stand in for the older run's resume",
          items(L).count("ITEM_TW") == 2 and by.get(tw1, {}).get("act") == by.get(tw2, {}).get("act") == "resumed",
          "%s %s" % (by.get(tw1, {}).get("act"), by.get(tw2, {}).get("act")))
    cs = [c for c in L.calls if c["item"] == "ITEM_S"]
    check("S: the session begun at the launch is resumed, not a later one in the same clone",
          len(cs) == 1 and cs[0].get("resume_session") == "88888888-aaaa-bbbb-cccc-000000000008",
          str([c.get("resume_session") for c in cs]))

    # BR: a failed switch off a spent account whose fallback fleet stop is logged under `brake`
    T5 = T_STOP + 160000
    br = rec("br", "ITEM_BR", T5 - 3000, brief_src=tsrc, ended=T5 - 2, result="killed: x", returned=T5 + 20)
    write(os.path.join(PLAN_DIR, "log.jsonl"), json.dumps({
        "acted": True, "at": iso(T5), "do": "switch", "live": "lukas", "to": "steven", "why": "test",
        "result": {"use": [1, "failed"]}, "brake": {"fleet-stop": [0, "stopped 4"]}}) + "\n")
    got = {x["unit"]: x for x in SR.scan(now=T5 + 60, root=STATE, plan_dir=PLAN_DIR, acct_log=ACCT_LOG, repo=REPO,
                                         projects=PROJECTS, runner=systemctl, cutoff=T_STOP - 86400)}
    check("BR: a fallback fleet stop is a stop (the run is parked: the switch failed)",
          got.get(br, {}).get("act") == "park" and got.get(br, {}).get("stop", {}).get("kind") == "stop", str(got.get(br)))

    # R: decided afresh before each act: a plan stop and a hand relaunch that land while the first resume launches
    T6 = T_STOP + 200000
    rx = rec("rx", "ITEM_RX", T6 - 3000, brief_src=tsrc, ended=T6 - 2, result="killed: x", returned=T6 + 20)
    ry = rec("ry", "ITEM_RY", T6 - 2990, brief_src=tsrc, ended=T6 - 2, result="killed: x", returned=T6 + 20)
    rz = rec("rz", "ITEM_RZ", T6 - 2980, brief_src=tsrc, ended=T6 - 2, result="killed: x", returned=T6 + 20)
    set_plan([plan_line("switch", T6, acted=True, to="system"), plan_line("normal", T6 + 300)])
    hand = []

    class Racing(Launcher):
        def __call__(self, *a_, **kw):
            if not self.calls:
                with open(os.path.join(PLAN_DIR, "log.jsonl"), "a", encoding="utf-8") as f:
                    f.write(plan_line("stop", T6 + 330, acted=True))
                hand.append(rec("rzhand", "ITEM_RZ", T6 + 320, status="running"))
            return Launcher.__call__(self, *a_, **kw)
    L = Racing()
    by = {x["unit"]: x for x in sweep(L, T6 + 310)}
    check("R: the first run resumed", items(L).count("ITEM_RX") == 1, str(items(L)))
    check("R: a stop that lands mid-sweep parks the rest", "ITEM_RY" not in items(L) and by.get(ry, {}).get("act") == "park",
          str(by.get(ry)))
    check("R: a hand relaunch that lands mid-sweep is not doubled", "ITEM_RZ" not in items(L)
          and (DH.read_record(rz, STATE) or {}).get("resumed_by") == (hand or [None])[0], str(by.get(rz)))

    # P: parked by a hard stop that stands six days (all accounts spent), resumed on the first pass with headroom
    T7 = T_STOP + 260000
    p = rec("p", "ITEM_P", T7 - 3000, brief_src=tsrc, ended=T7 - 2, result="killed: x", returned=T7 + 20)
    set_plan([plan_line("stop", T7, acted=True), plan_line("stopped", T7 + 300)], notice_state="stop", notice_at=T7 + 300)
    L = Launcher()
    sweep(L, T7 + 310)
    parked = bool((DH.read_record(p, STATE) or {}).get("parked"))
    late = T7 + 6 * 86400
    set_plan([plan_line("stop", T7, acted=True), plan_line("start", late - 300, acted=True), plan_line("normal", late)])
    sweep(L, late + 10)
    check("P: parked six days, resumed on the first pass with headroom", parked and items(L).count("ITEM_P") == 1,
          "parked=%s calls=%s" % (parked, items(L)))

    # CK: each act is decided at the time it is taken: the first resume takes so long that the plan's newest pass has
    # aged past FRESH_S (its timer stopped) by the second, which is parked, not launched on the stale reading
    T8 = T_STOP + 900000
    ck = [rec("ck%d" % i, "ITEM_CK%d" % i, T8 - 3000 + i, brief_src=tsrc, ended=T8 - 2, result="killed: x",
              returned=T8 + 20) for i in (1, 2)]
    set_plan([plan_line("switch", T8, acted=True, to="system"), plan_line("normal", T8 + 300)])
    L = Launcher()
    by = {x["unit"]: x for x in sweep(L, T8 + 310, clock=lambda: T8 + 310 + (SR.FRESH_S + 60 if L.calls else 0))}
    acts = sorted(by.get(u, {}).get("act") or "-" for u in ck)
    check("CK: a pass that ages out mid-sweep is no headroom for the next act", len(L.calls) == 1
          and acts == ["park", "resumed"], "calls=%s acts=%s" % (items(L), acts))

    # GC: two runs launched into one given clone 10 s apart (and a hook test's session begun there first): each run's
    # session is the one whose first prompt names its item, never the other's
    T9 = T_STOP + 1100000
    g_clone = os.path.join(TMP, "kept", "GC.clone")
    os.makedirs(g_clone, exist_ok=True)
    gc = [rec("gc%d" % i, "ITEM_GC%d" % i, T9 - 3000 + 10 * i, clone=g_clone, clone_how="given " + g_clone,
              ended=T9 - 2, result="killed: x", returned=T9 + 20) for i in (1, 2)]
    for sid, t, text in (("13131313-aaaa-bbbb-cccc-000000000013", T9 - 2988, "say ok"),
                         ("14141414-aaaa-bbbb-cccc-000000000014", T9 - 2960, "Build it.\n\nItem: ITEM_GC1"),
                         ("15151515-aaaa-bbbb-cccc-000000000015", T9 - 2950, "Build it.\n\nItem: ITEM_GC2")):
        write(os.path.join(DH.project_dir(g_clone, PROJECTS), sid + ".jsonl"),
              json.dumps({"type": "user", "timestamp": iso(t), "sessionId": sid, "entrypoint": "sdk-cli",
                          "message": {"role": "user", "content": text}}) + "\n")
    set_plan([plan_line("switch", T9, acted=True, to="system"), plan_line("normal", T9 + 300)])
    L = Launcher()
    sweep(L, T9 + 310)
    got = {c["item"]: c.get("resume_session") for c in L.calls}
    check("GC: two runs in one clone each resume their own session",
          got == {"ITEM_GC1": "14141414-aaaa-bbbb-cccc-000000000014", "ITEM_GC2": "15151515-aaaa-bbbb-cccc-000000000015"},
          str(got))

    # IN: a sweep killed right after its first launch (the successor exists, its resumed_from never written): the
    # twin it had not reached yet is resumed on its own, and the claimed run is marked by that successor
    T10 = T_STOP + 1200000
    iw = [rec("iw%d" % i, "ITEM_IW", T10 - 3000 + i, brief_src=tsrc, ended=T10 - 2, result="killed: x",
              returned=T10 + 20) for i in (1, 2)]
    set_plan([plan_line("switch", T10, acted=True, to="system"), plan_line("normal", T10 + 300)])

    class Dies(Launcher):
        def __call__(self, *a_, **kw):
            Launcher.__call__(self, *a_, **kw)
            raise SystemExit("the sweep's unit was killed")
    L = Dies()
    try:
        sweep(L, T10 + 310)
    except SystemExit:
        pass
    first = "rm-detached-bench-relaunch0-%d" % int(T10 + 310)
    claimed = [u for u in iw if (DH.read_record(u, STATE) or {}).get("resume_claim")]
    L2 = Launcher()
    set_plan([plan_line("switch", T10, acted=True, to="system"), plan_line("normal", T10 + 300),
              plan_line("normal", T10 + 600)])
    sweep(L2, T10 + 620)
    set_plan([plan_line("switch", T10, acted=True, to="system"), plan_line("normal", T10 + 300),
              plan_line("normal", T10 + 1500)])
    sweep(L2, T10 + 1510)
    rb = {u: (DH.read_record(u, STATE) or {}).get("resumed_by") for u in iw}
    other = [u for u in iw if u not in claimed]
    check("IN: an interrupted sweep's successor stands for one stopped run only", len(claimed) == 1
          and rb[claimed[0]] == first and len(L2.calls) == 1 and rb[other[0]] not in (None, first),
          "claimed=%s resumed_by=%s later launches=%s" % (claimed, rb, items(L2)))

    # OLD: a run launched four days before a hard stop that stands seven days is still resumed (its launch is 11 d old,
    # its record was written when it was parked)
    T11 = T_STOP + 1300000
    old = rec("old", "ITEM_OLD4", T11 - 4 * 86400, brief_src=tsrc, ended=T11 - 2, result="killed: x", returned=T11 + 20)
    set_plan([plan_line("stop", T11, acted=True), plan_line("stopped", T11 + 300)], notice_state="stop", notice_at=T11 + 300)
    L = Launcher()
    sweep(L, T11 + 310)
    parked = bool((DH.read_record(old, STATE) or {}).get("parked"))
    os.utime(DH.record_path(old, STATE), (T11 + 310, T11 + 310))     # the park's write, on the test's clock
    back = T11 + 7 * 86400
    set_plan([plan_line("stop", T11, acted=True), plan_line("start", back - 300, acted=True), plan_line("normal", back)])
    sweep(L, back + 10)
    check("OLD: a parked run launched 11 d before headroom returns is resumed", parked and items(L).count("ITEM_OLD4") == 1,
          "parked=%s calls=%s" % (parked, items(L)))


def wiring():
    """switching_plan.check() starts the sweep after a live pass: never dry, never under HOLD, never for a test's plan
    dir, and a sweep that cannot load never fails the pass. Every switcher call is fake."""
    from pathlib import Path
    from unittest.mock import patch
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
    import switching_plan as SP
    from pulse import phone_push as PP
    out = Path(TMP) / "plan_out"
    now = T_STOP
    meter = {n: {"source": "MEASURED", "week_pct_left": 90, "week_resets_at": SP.iso(now + 36000), "age_min": 1,
                 "stale": False} for n in SP.load_plan()["order"]}

    def run(argv, **kw):
        if argv[1] == "--json":
            return 0, json.dumps({"machine": "fixture", "live": SP.load_plan()["order"][0], "armed": True})
        return 0, "{}"
    kicks = []
    with patch.object(SP, "OUT", out), patch.object(SP, "SWITCH_LOG", Path(TMP) / "no-acct-log"), \
            patch.object(SP, "run", side_effect=run), patch.object(SP, "clock", return_value=now), \
            patch.object(PP, "STATE", Path(TMP) / "phone.json"), \
            patch.object(PP, "todoist_transport", side_effect=lambda title, body: None), \
            patch.object(SP, "resume_stopped_runs", side_effect=lambda: kicks.append(1)):
        go = lambda dry=False: SP.check(dry=dry, now=now, meter_fn=lambda: meter, poll_fn=lambda: None)  # noqa: E731
        go()
        check("wiring: a test's plan dir never starts the sweep", not kicks, str(len(kicks)))
        with patch.object(SP, "LIVE_OUT", out):
            go(dry=True)
            check("wiring: a dry pass never starts the sweep", not kicks, str(len(kicks)))
            go()
            check("wiring: a live pass starts the sweep once", len(kicks) == 1, str(len(kicks)))
            (out / "HOLD").write_text("test")
            go()
            check("wiring: HOLD stops the sweep too", len(kicks) == 1, str(len(kicks)))
    with patch.dict(sys.modules, {"stop_resume": None}):
        try:
            SP.resume_stopped_runs()
            ok = True
        except Exception:  # noqa: BLE001
            ok = False
    check("wiring: a sweep that cannot load never fails the pass", ok)


if __name__ == "__main__":
    sys.exit(main())
