#!/usr/bin/env python3
"""selftest_work_bundle_monitor.py - the Temporary Work Bundle Monitor (work_bundle_monitor.py).

Item RIMMANDRAKE_BUILD_TEMPORARY_WORK_BUNDLE_MONITOR_DAILY; page design/specs/2026-11-25-temporary-work-bundle-monitor/
boundary.md (each t_ function is one promise of it, by name). Offline: fake records in a throwaway folder and an
injected model caller; nothing calls a model, writes the real output folder or the Conductor log. The planted faults
that turned each named case red are in that folder's planted_faults.md.
"""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils"), os.path.join(REPO, "src", "RimMandrake")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
TMP = tempfile.mkdtemp(prefix="selftest_wbm_")
os.environ["RM_WBM_OUT"] = os.path.join(TMP, "out")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "dispatcher")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.log")
import work_bundle_monitor as M  # noqa: E402

FAILS = []
NOW = 1795700000.0
T0, T1 = NOW - M.DAY, NOW


def chk(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def iso(t):
    return M.iso(t)


def rec(unit, item, ended, tokens=1000, env=None, session=None, **k):
    r = {"unit": unit, "item": item, "model": "opus", "at": ended - 600, "ended": ended, "status": "finished",
         "tokens": tokens, "token_unit": "weighted_v2", "result": "success (exited 0)", "session": session}
    if tokens is None:
        r.pop("tokens")
    if env:
        r["env"] = env
    r.update(k)
    return r


def ev(event, iid, t, **k):
    return dict({"event": event, "id": iid, "ts": iso(t), "seat": "BENCH"}, **k)


def world(runs=None, bundles=None, events=None, moves=None, live=None):
    def s(v):
        return M.src(v)
    return {"runs": s(runs or {}), "roles": s({}), "bundles": s(bundles if bundles is not None else {}),
            "ledger": s(events or []), "moves": s(moves or []), "live": s(live or {"early": [], "unrun": []}),
            "mods": ["FlowWorks", "ExplosiveKnockback"]}


def bundle(bid, members, units, at, pipeline="workshop", **k):
    return dict({"id": bid, "system": "pipeline:x", "members": members, "units": [{"unit": u, "at": at} for u in units],
                 "at": at, "pipeline": pipeline, "state": "ended"}, **k)


def measure(S):
    return M.measure(S, T0, T1, NOW, transcripts=False)


# --------------------------------------------------------------------------------------------------- promises -----

def t_bundle_unit_is_bundle_run():
    b = bundle("WB-x", ["A", "B", "C"], ["u-b"], T0 + 10)
    runs = {"u-b": rec("u-b", "A", T0 + 100), "u-env": rec("u-env", "D", T0 + 200, env={"RM_WORK_BUNDLE": "WB-y"}),
            "u-s": rec("u-s", "E", T0 + 300)}
    by = {"WB-x": b, "WB-y": bundle("WB-y", ["D", "F"], [], T0 + 20)}
    ub = M.unit_bundles(by)
    chk(M.kind_of(runs["u-b"], ub, by) == "bundle", "bundle-unit-is-bundle-run: a unit in a 3-member record is a bundle run")
    chk(M.kind_of(runs["u-env"], ub, by) == "bundle", "bundle-unit-is-bundle-run: RM_WORK_BUNDLE in the env names its bundle")
    chk(M.kind_of(runs["u-s"], ub, by) == "single", "bundle-unit-is-bundle-run: any other run is single")
    R = measure(world(runs=runs, bundles=by))
    chk(R["share"]["workshop"]["bundle"]["runs"] == 2, "bundle-unit-is-bundle-run: the share counts both bundle runs")


def t_bundle_of_one_counts_single():
    by = {"WB-1": bundle("WB-1", ["A"], ["u1"], T0 + 10)}
    runs = {"u1": rec("u1", "A", T0 + 100), "u2": rec("u2", "B", T0 + 200)}
    R = measure(world(runs=runs, bundles=by))
    sh = R["share"]["workshop"]
    chk(sh["bundle_of_one"]["runs"] == 1 and sh["single"]["runs"] == 1 and sh["bundle"]["runs"] == 0,
        "bundle-of-one-counts-single: its own line in the share")
    chk(R["efficiency"]["today"]["single"]["runs"] == 2 and R["efficiency"]["today"]["bundle"]["runs"] == 0,
        "bundle-of-one-counts-single: counted with the single-ticket runs in efficiency")


def t_unreadable_record_not_zero():
    d = os.path.join(TMP, "unreadable", "detached")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "rm-detached-bench-a-1.json"), "w") as f:
        f.write("{not json")
    with open(os.path.join(d, "rm-detached-bench-b-2.json"), "w") as f:
        json.dump(rec("rm-detached-bench-b-2", "B", T0 + 50, tokens=500), f)
    r = M.read_runs(d)
    chk(r["state"] == "measured" and list(r["value"]) == ["rm-detached-bench-b-2"],
        "unreadable-record-not-zero: the unreadable record adds no run")
    chk(any("rm-detached-bench-a-1" in x for x in r["unreadable"]), "unreadable-record-not-zero: it is named in unreadable")
    S = world(runs=r["value"])
    S["runs"] = r
    R = measure(S)
    chk(R["sources"]["runs"]["unreadable"] and R["share"]["workshop"]["single"]["runs"] == 1
        and R["share"]["workshop"]["single"]["tokens"] == 500, "unreadable-record-not-zero: the reading names it and sums only the readable run")


def t_missing_source_unmeasured():
    r = M.read_runs(os.path.join(TMP, "no-such-dir"))
    chk(r["state"] == M.CNL and r["value"] is None and "does not exist" in r["cause"],
        "missing-source-unmeasured: a missing run folder is could not look")
    S = world()
    S["runs"] = r
    R = measure(S)
    chk(R["share"]["state"] == M.CNL and "does not exist" in R["share"]["cause"],
        "missing-source-unmeasured: the share says could not look with the cause")
    S = world()
    S["ledger"] = M.read_ledger(os.path.join(TMP, "no-ledger"))
    R = measure(S)
    chk(R["deferral"]["state"] == M.CNL and R["efficiency"]["state"] == M.CNL,
        "missing-source-unmeasured: a missing ledger makes deferral and efficiency could not look, not 0")
    L = M.summary(R, None, None, "failed", "2026-11-25")
    chk(L["deferral"].get("state") == M.CNL and L["verdicts"] == M.UNM,
        "missing-source-unmeasured: the summary carries could not look, not 0")


def t_unpriced_run_not_zero_tokens():
    runs = {"u1": rec("u1", "A", T0 + 100, tokens=None), "u2": rec("u2", "B", T0 + 200, tokens=700)}
    R = measure(world(runs=runs, events=[ev("close", "A", T0 + 90, role_unit="u1"),
                                         ev("close", "B", T0 + 190, role_unit="u2")]))
    k = R["efficiency"]["today"]["single"]
    chk(k["unpriced_runs"] == 1 and k["priced_runs"] == 1 and k["tokens"] == 700,
        "unpriced-run-not-zero-tokens: the unpriced run stays out of the sum")
    chk(k["tokens_per_ticket_closed"] == 700, "unpriced-run-not-zero-tokens: its close is not divided into the priced tokens")
    chk(sum(k["unpriced_why"].values()) == 1, "unpriced-run-not-zero-tokens: its cause is counted")
    R2 = measure(world(runs={"u1": rec("u1", "A", T0 + 100, tokens=None)}))
    chk(R2["efficiency"]["today"]["single"]["tokens"] == M.UNM,
        "unpriced-run-not-zero-tokens: only unpriced runs read UNMEASURED, not 0")


def t_reopened_close_not_stayed():
    old = NOW - 5 * M.DAY
    evs = [ev("close", "A", old), ev("start", "A", old + M.DAY),            # reopened within 3 days
           ev("close", "B", old),                                          # stayed
           ev("close", "C", NOW - M.DAY),                                  # pending
           ev("close", "D", old), ev("claim", "D", old + 4 * M.DAY)]        # reopened after 3 days: stayed
    cl = {c["item"]: M.stayed(c, NOW) for c in M.closes_index(evs)}
    chk(cl == {"A": "reopened", "B": "stayed", "C": "pending", "D": "stayed"},
        "reopened-close-not-stayed: reopened, stayed, pending, late reopen (%s)" % cl)
    evs2 = [ev("close", "E", old), ev("verify", "E", old + 3600, result="fail", afterClose=True)]
    chk(M.stayed(M.closes_index(evs2)[0], NOW) == "reopened", "reopened-close-not-stayed: a verify fail after close")


def t_headline_tokens_per_stayed_close():
    rip = NOW - 3 * M.DAY - M.DAY / 2
    runs = {"u1": rec("u1", "A", rip, tokens=900), "u2": rec("u2", "B", rip + 60, tokens=300)}
    evs = [ev("close", "A", rip - 10, role_unit="u1"), ev("close", "B", rip + 50, role_unit="u2"),
           ev("start", "B", rip + 3600)]
    R = measure(world(runs=runs, events=evs))
    h = R["efficiency"]["headline_window"]["single"]
    chk(h["stayed"] == 1 and h["reopened"] == 1 and h["tokens_per_ticket_stayed_closed"] == 1200 and h["runs"] == 2,
        "headline-tokens-per-stayed-close: 1200 tokens over 1 stayed ticket, 2 runs (%s)" % h["tokens_per_ticket_stayed_closed"])
    chk(h["reopened_tickets"] == ["B"], "headline-tokens-per-stayed-close: the reopened ticket is named")
    runs = {"u4": rec("u4", "D", rip, tokens=600)}
    evs = [ev("close", "D", rip - 20, role_unit="u4"), ev("close", "D", rip - 10, role_unit="u4")]
    h = measure(world(runs=runs, events=evs))["efficiency"]["headline_window"]["single"]
    chk(h["close_events"] == 2 and h["tickets_closed"] == 1 and h["tokens_per_ticket_stayed_closed"] == 600,
        "headline-tokens-per-stayed-close: a ticket closed twice counts once (%s)" % h["tokens_per_ticket_stayed_closed"])
    runs = {"u3": rec("u3", "C", T0 + 100, tokens=400)}
    R = measure(world(runs=runs, events=[ev("close", "C", T0 + 90, role_unit="u3")]))
    chk(R["efficiency"]["today"]["single"]["tokens_per_ticket_stayed_closed"] == "pending",
        "headline-tokens-per-stayed-close: today's young close reads pending")


def t_program_filing_not_setdown():
    evs = [ev("spawn", None, T0 + 10, name="P1", not_now={"program": "maturation_dispatch.file_and_publish"}),
           ev("file", "F1", T0 + 20, not_now={"class": "fix-unknown", "evidence": "tried x"}, role_unit="u1")]
    sd, prog = M.setdowns(evs, T0, T1)
    chk(len(sd) == 1 and sd[0]["id"] == "F1" and prog == 1, "program-filing-not-setdown: 1 set-down, 1 program filing")


def t_setdowns_by_class_and_role():
    runs = {"rm-detached-bench-x-1": rec("rm-detached-bench-x-1", "A", T0 + 500,
                                         env={"RM_CONTROL_STAGE": "in_game"})}
    evs = [ev("file", "F1", T0 + 20, not_now={"class": "fix-unknown", "evidence": "e"}, role_unit="rm-detached-bench-x-1"),
           ev("file", "F2", T0 + 30, not_now={"class": "fix-unknown", "evidence": "e"}, role_unit="rm-role-operations-5"),
           ev("file", "F3", T0 + 40, not_now={"class": "owner-act", "evidence": "e"}, role_unit="rm-role-operations-6")]
    R = measure(world(runs=runs, events=evs))
    d = R["deferral"]
    chk(d["by_class"] == {"fix-unknown": 2, "owner-act": 1}, "setdowns-by-class-and-role: by class %s" % d["by_class"])
    chk(d["by_role"] == {"maturation in_game": 1, "operations": 2}, "setdowns-by-class-and-role: by role %s" % d["by_role"])


def t_backward_moves_classed():
    mv = [{"mod": "M", "from": "in_game", "to": "offline_build", "at": iso(T0 + 1), "t": T0 + 1},
          {"mod": "M", "from": "in_game", "to": "in_game", "at": iso(T0 + 2), "t": T0 + 2},
          {"mod": "M", "from": "offline_build", "to": "blind_challenge", "at": iso(T0 + 3), "t": T0 + 3}]
    kinds = [M.move_kind(m) for m in mv]
    chk(kinds == ["backward", "backward", "forward"], "backward-moves-classed: %s" % kinds)
    R = measure(world(moves=mv))
    chk(R["moves"]["per_mod"]["M"] == {"forward": 1, "backward": 2, "unknown": 0} and len(R["moves"]["backward"]) == 2,
        "backward-moves-classed: per mod and listed")


def _transcript(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for x in lines:
            f.write(json.dumps(x) + "\n")


def _turn(mid, tool=None, inp=0, out=0, t=None, text=None):
    c = [{"type": "tool_use", "name": tool, "input": {"file_path": "x"}}] if tool else []
    if text:
        c.append({"type": "text", "text": text})
    return {"type": "assistant", "timestamp": iso(t or T0), "message": {
        "id": mid, "model": "claude-opus-5-5", "content": c,
        "usage": {"input_tokens": inp, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
                  "output_tokens": out}}}


def t_tokens_before_first_edit():
    proj = os.path.join(TMP, "projects")
    _transcript(os.path.join(proj, "p1", "s-edit.jsonl"),
                [_turn("m1", inp=100), _turn("m1", inp=100), _turn("m2", tool="Read", inp=50),
                 _turn("m3", tool="Edit", inp=1000), _turn("m4", inp=1000)])
    _transcript(os.path.join(proj, "p1", "s-none.jsonl"), [_turn("m1", inp=100), _turn("m2", tool="Bash", inp=10)])
    n, why = M.first_edit_tokens({"session": "s-edit"}, proj)
    chk(n == 150 and why is None, "tokens-before-first-edit: 150 input tokens before the Edit, each message once (%s)" % n)
    n2, _w = M.first_edit_tokens({"session": "s-none"}, proj)
    chk(n2 == "no edit", "tokens-before-first-edit: a run with no edit reads 'no edit', not 0")
    n3, w3 = M.first_edit_tokens({"session": "s-gone"}, proj)
    chk(n3 is None and "no transcript" in w3, "tokens-before-first-edit: a lost transcript is could not look")


def t_bundle_live_ran_and_unrun():
    b = bundle("WB-l", ["A", "B"], ["u"], T0 + 10, live_runs=[{"at": T0 + 20, "rc": 0}, {"at": T0 + 30, "unrun": True}])
    live = {"early": [{"item": "A", "at": iso(T0 + 40)}, {"item": "Z", "at": iso(T0 + 40)}],
            "unrun": [{"item": "B", "at": iso(T0 + 50)}, {"item": "B"}]}
    R = measure(world(bundles={"WB-l": b}, live=live))
    row = R["live"]["bundles"]["WB-l"]
    chk(row["bundle_live_ran"] == 1 and row["bundle_live_unrun"] == 1, "bundle-live-ran-and-unrun: the record's live runs")
    chk(row["early_rows"] == 1 and row["unrun_rows"] == 1 and row["unrun_rows_undated"] == 1,
        "bundle-live-ran-and-unrun: members' early and UNRUN rows, an undated row apart (%s)" % row)


def t_judge_failure_could_not_judge():
    row = {"id": "F1", "ts": iso(T0 + 5), "kind": "set-down", "unit": "", "class": "fix-unknown", "evidence": "e"}
    v = M.judge_row(row, {}, {}, caller=lambda *a, **k: (None, "exit 1: usage limit", None, 1.0))
    chk(v["verdict"] == "COULD NOT JUDGE" and "usage limit" in v["cause"], "judge-failure-could-not-judge: a failed call")
    v = M.judge_row(row, {}, {}, caller=lambda *a, **k: ("I think it is fine.", None, 10, 1.0))
    chk(v["verdict"] == "COULD NOT JUDGE" and "no verdict line" in v["cause"], "judge-failure-could-not-judge: no verdict line")
    seen = []
    M.judge_row(row, {}, {}, caller=lambda prompt, *a, **k: (seen.append(prompt), (None, "x", None, 0))[1])
    chk("(no act before this point)" not in seen[0] and "acts are unknown" in seen[0],
        "judge-failure-could-not-judge: a lost transcript is shown as unknown acts, never as no acts")
    ok = 'reasoning\n{"verdict": "NOT SINCERE", "evidence": "ran nothing", "cause": "the gate"}'
    v = M.judge_row(row, {}, {}, caller=lambda *a, **k: (ok, None, 10, 1.0))
    chk(v["verdict"] == "NOT SINCERE" and v["evidence"] == "ran nothing", "judge-failure-could-not-judge: a good line parses")


def t_judge_told_no_spend():
    seen = {}

    def runner(argv, **k):
        seen["argv"], seen["input"] = argv, k.get("input")

        class R:
            returncode, stdout, stderr = 0, json.dumps({"result": "x", "modelUsage": {}}), ""
        return R()
    M.call_model("PROMPT", "sonnet", 5, "n", runner=runner)
    chk(not any("budget" in a for a in seen["argv"]) and seen["input"] == "PROMPT",
        "judge-told-no-spend: no budget flag; the prompt goes on stdin")
    row = {"id": "F1", "ts": iso(T0), "class": "c", "evidence": "e"}
    p = M.judge_prompt(row, "brief", "acts")
    R = measure(world())
    rp = M.report_prompt(R, [{"verdict": "SINCERE", "tokens": 123456}], "2026-11-25")
    chk("123456" not in rp and "monitor_tokens" not in rp, "judge-told-no-spend: the report prompt carries no judge spend")
    chk(not any(w in p.lower() for w in ("budget", "weighted", "cost", "token")),
        "judge-told-no-spend: the judge prompt names no spend figure")


def _latest(od, **k):
    os.makedirs(od, exist_ok=True)
    R = measure(world(runs={"u1": rec("u1", "A", T0 + 100, tokens=999777)},
                      events=[ev("file", "F1", T0 + 20, not_now={"class": "fix-unknown", "evidence": "e"})]))
    L = M.summary(R, [{"verdict": "NOT SINCERE", "role": "detached helper"}],
                  "/mnt/d/ClaudeWork/rimmandrake/work_bundle_monitor/report_2026-11-25.md", "written", "2026-11-25")
    L.update(k)
    L["monitor_tokens"] = {"judge_tokens": 4242424, "unit": "weighted_v2"}
    M.write_json(os.path.join(od, "latest.json"), L)
    return M.latest(od)


def t_page_section_no_tokens():
    L = _latest(os.path.join(TMP, "page"))
    md = "\n".join(M.page_md(L))
    html = M.page_html(L)
    chk("Temporary Work Bundle Monitor" in md and "Temporary Work Bundle Monitor" in html, "page-section-no-tokens: the title")
    chk("999777" not in md + html and "4242424" not in md + html and "token" not in (md + html).lower()
        and "weighted" not in (md + html).lower(), "page-section-no-tokens: no token or spend figure")
    chk("D:\\ClaudeWork\\rimmandrake\\work_bundle_monitor\\report_2026-11-25.md" in md,
        "page-section-no-tokens: the report's full Windows path")
    chk("1 of 1 not honest" in md and "helper runs" in md, "page-section-no-tokens: the verdicts and the role (%s)" % md)
    bad = M.latest(os.path.join(TMP, "nothing-here"))
    chk("Could not look" in "\n".join(M.page_md(bad)), "page-section-no-tokens: an unreadable reading says could not look")


def t_digest_line_blind():
    from contracts import blind as BL
    import datetime as dt
    L = _latest(os.path.join(TMP, "digest"))
    f = M.digest_fields(L)
    chk("monitor_tokens" not in f and f.get("set_downs") == 1 and f.get("not_sincere") == 1,
        "digest-line-blind: the fields are counts and the report path")
    cut = dt.datetime(2026, 11, 25, 12, tzinfo=dt.timezone.utc)
    text = BL.render_digest(BL.project_digest("2026-11-25", None, cut, [], {}, None, None, None, f))
    chk("## Temporary Work Bundle Monitor" in text and "set downs 1" in text and "NOT SINCERE 1" in text,
        "digest-line-blind: the line renders through the blind page")
    chk("ClaudeWork" not in text and any(v["value"].endswith("report_2026-11-25.md") for v in text.handles.values()),
        "digest-line-blind: the report is a handle, never the raw path")
    t2 = BL.render_digest(BL.project_digest("2026-11-25", None, cut, [], {}, None, None, None, None))
    chk("UNMEASURED: the monitor could not be read" in t2, "digest-line-blind: an unreadable monitor reads UNMEASURED")


def t_baseline_same_system_before_first_bundle():
    first = T0 + 100
    by = {"WB-p": bundle("WB-p", ["A", "B"], ["u-b"], first, system="pipeline:judges")}
    by["WB-p"]["system"] = "pipeline:judges"
    runs = {"u-b": rec("u-b", "A", T0 + 500),
            "u-old": rec("u-old", "J1", first - 2 * M.DAY, tokens=800),          # same home, inside 14 days
            "u-older": rec("u-older", "J2", first - 20 * M.DAY, tokens=50),      # same home, too old
            "u-other": rec("u-other", "K1", first - M.DAY, tokens=70)}           # other home
    evs = [ev("home", "J1", T0 - 30 * M.DAY, home="pipeline:judges"), ev("home", "J2", T0 - 30 * M.DAY,
                                                                          home="pipeline:judges"),
           ev("home", "K1", T0 - 30 * M.DAY, home="pipeline:docs"),
           ev("close", "J1", first - 2 * M.DAY - 10, role_unit="u-old")]
    R = measure(world(runs=runs, bundles=by, events=evs))
    b = R["efficiency"]["baseline"].get("pipeline:judges") or {}
    chk(b.get("state") == "measured" and b.get("runs") == 1 and b.get("tokens") == 800 and b.get("tickets_closed") == 1,
        "baseline-same-system-before-first-bundle: one run of the home in the 14 days before (%s)" %
        {k: b.get(k) for k in ("state", "runs", "tokens", "tickets_closed")})


def t_report_needs_four_sections():
    od = os.path.join(TMP, "daily")
    os.environ["RM_WBM_OUT"] = od
    said = []
    S = world(runs={"u1": rec("u1", "A", T0 + 100)})
    try:
        rc = M.daily(NOW, caller=lambda prompt, tier, *a: ("## The day's numbers\nonly one", None, 1, 1.0), S=S,
                     say=lambda t, n: said.append(t))
        chk(rc == 1 and not os.path.exists(os.path.join(od, "report_%s.md" % M.dt.datetime.fromtimestamp(
            NOW, M.dt.timezone.utc).astimezone().strftime("%Y-%m-%d"))), "report-needs-four-sections: no report written")
        fails = [n for n in os.listdir(od) if n.endswith(".FAILED.md")]
        chk(len(fails) == 1 and "failed" in M.latest(od)["report_state"] and said and "FAILED" in said[0],
            "report-needs-four-sections: the failure is written and said")
        chk(not os.path.exists(os.path.join(od, M.NEWEST)), "report-needs-four-sections: a failed report renews no newest copy")
        good = "\n\n".join(s + "\ntext" for s in M.SECTIONS)
        rc = M.daily(NOW, caller=lambda prompt, tier, *a: (good, None, 1, 1.0), S=S, say=lambda t, n: said.append(t))
        chk(rc == 0 and M.latest(od)["report_state"] == "written", "report-needs-four-sections: a whole report is written")
        nw = open(os.path.join(od, M.NEWEST)).read()
        chk(nw.startswith("# Temporary Work Bundle Monitor") and 0 < nw.find(M.REPORT_TOP) < nw.find("## The day's numbers"),
            "report-needs-four-sections: a written report renews the newest copy, the five answers on top")
    finally:
        os.environ["RM_WBM_OUT"] = os.path.join(TMP, "out")


# ------------------------------------------------------------------- the polish watch (born, regressions, polish) --
# Item RIMMANDRAKE_WATCH_POLISH_FOR_NEW_BUGS_HE_FEARS_THE_OLD_NOISE: the three measures on planted records.

NP = M.POLISH_RULE_T + 10 * M.DAY        # a "now" well after the polish: rule, so a 3-day window can be ripe
MEMBER = "RIMMANDRAKE_PAINT_WALLS_GREEN_TODAY"


def cm(n, t, subject, files):
    return {"sha": ("%x" % n).rjust(40, "0"), "t": float(t), "subject": subject, "files": list(files)}


def _pw_world(tb, commits, nights=None, events=None, members=(MEMBER,), published=None):
    """One bundle (unit u-b, launched at tb, ended an hour later) and the planted commits."""
    by = {"WB-p": bundle("WB-p", list(members), ["u-b"], tb)}
    runs = {"u-b": rec("u-b", members[0], tb + 3600)}
    return by, runs, (published or {}), commits, (nights if nights is not None else []), M.closes_index(events or [])


def _col(rows, path):
    hit = [r for r in rows if r["file"] == path]
    return hit[0] if len(hit) == 1 else {"column": "rows=%d" % len(hit)}


def t_polish_then_fix_one_regression():
    tb = NP - 5 * M.DAY
    commits = [cm(1, tb + 100, MEMBER + ": paint the walls", ["src/x/a.py", "src/x/b.py"]),
               cm(2, tb + 200, "polish: " + MEMBER + ": two names in a.py", ["src/x/a.py"]),
               cm(3, tb + 200 + M.DAY, "RIMMANDRAKE_MEND_A_AFTER_THE_NAMES: fix the crash the rename made", ["src/x/a.py"])]
    rows = M.regress_rows(*_pw_world(tb, commits), t_lo=tb, t_hi=tb + M.DAY, now=NP)
    a = _col(rows, "src/x/a.py")
    chk(a.get("column") == "polish" and a.get("state") == "ripe" and len(a.get("fixes") or []) == 1,
        "polish-then-fix-one-regression: the polished file reads polish, ripe, one fix (%s)" % a.get("column"))
    s = M.regress_summary(rows)
    chk(s["polish"]["ripe"] == 1 and s["polish"]["ripe_regressed"] == 1 and s["polish"]["events"]["fix"] == 1,
        "polish-then-fix-one-regression: the polish column counts exactly one regression (%s)" % s["polish"])
    chk(s["no_polish"]["ripe"] == 1 and s["no_polish"]["ripe_regressed"] == 0,
        "polish-then-fix-one-regression: the bundle's other file is a clean no-polish row (%s)" % s["no_polish"])


def t_no_polish_fix_counts_no_polish():
    tb = NP - 5 * M.DAY
    commits = [cm(1, tb + 100, MEMBER + ": paint", ["src/x/b.py"]),
               cm(4, tb + 100 + 2 * M.DAY, "RIMMANDRAKE_REPAIR_B_WALL_SEAM_LEAKS: repair the seam", ["src/x/b.py"])]
    rows = M.regress_rows(*_pw_world(tb, commits), t_lo=tb, t_hi=tb + M.DAY, now=NP)
    s = M.regress_summary(rows)
    chk(_col(rows, "src/x/b.py").get("column") == "no_polish" and s["no_polish"]["ripe_regressed"] == 1
        and s["polish"]["files"] == 0, "no-polish-fix-counts-no-polish: the later fix counts in the no-polish column (%s)"
        % s["no_polish"])


def t_regression_kinds_and_window():
    tb = NP - 5 * M.DAY
    other = "RIMMANDRAKE_TILE_THE_FLOOR_BLUE_AFTER"
    commits = [cm(1, tb + 100, MEMBER + ": paint", ["src/x/c.py", "src/x/d.py", "src/x/e.py", "infrastructure/state/ledger/events/BENCH.jsonl"]),
               cm(5, tb + 100 + 2 * 3600, 'Revert "%s: paint"' % MEMBER, ["src/x/c.py"]),    # after the bundle's life
               cm(6, tb + 100 + 4 * M.DAY, "RIMMANDRAKE_FIX_E_LATE_FOUR_DAYS_ON: fix e", ["src/x/e.py"]),
               cm(7, tb + 100 + M.DAY, other + ": fix nothing, a tidy pass", ["src/x/f.py"]),
               cm(8, tb + 300, "ledger: %s close" % MEMBER, ["src/x/e.py"]),
               cm(11, tb + 100 + M.DAY, "RIMMANDRAKE_VET_HOST_SWITCH_SEEN_AGAIN: one host switch that every lane reads, "
                  "so a lane no longer writes a line where it can fix", ["src/x/d.py"]),
               cm(12, tb + 100 + M.DAY, "RIMMANDRAKE_BUILD_CALM_PROFILE_LOG_AND_LEASE: fresh-reader fixes: the deadline "
                  "carried over a re-arm", ["src/x/g.py"]),
               cm(13, tb + 100 + M.DAY, "RIMMANDRAKE_RULE_REBOUND_NEAR_WALL_FIRST_LEG: bar reworded to the leaf; loosens "
                  "a bar: undo by reverting this commit", ["src/x/e.py"])]
    commits[0]["files"] += ["src/x/g.py", "design/concepts/FlowWorks/version/in_game/early_rows.jsonl"]
    nights = [{"t": tb + 100 + M.DAY, "reds": {"src/x/selftest_d.py"}}]
    events = [ev("close", MEMBER, tb + 400, role_unit="u-b"), ev("claim", MEMBER, tb + 400 + M.DAY)]
    rows = M.regress_rows(*_pw_world(tb, commits, nights=nights, events=events), t_lo=tb, t_hi=tb + M.DAY, now=NP)
    c, d, e = _col(rows, "src/x/c.py"), _col(rows, "src/x/d.py"), _col(rows, "src/x/e.py")
    chk(len(c.get("reverts") or []) == 1 and not c.get("fixes"), "regression-kinds-and-window: a revert counts as a revert")
    chk(len(d.get("reds") or []) == 1, "regression-kinds-and-window: a nightly red of the file's own selftest counts")
    chk(MEMBER in (c.get("reopened") or []), "regression-kinds-and-window: a reopened member counts on the files its commit named")
    chk(not e.get("fixes") and not e.get("reverts"),
        "regression-kinds-and-window: a fix after 3 days does not count, nor a ledger commit, nor 'reverting' in prose")
    chk(not any(r["file"].startswith("infrastructure/state/") or r["file"].endswith(".jsonl") for r in rows),
        "regression-kinds-and-window: a ledger shard or a run record (.jsonl) is no file row")
    chk(not d.get("fixes"), "regression-kinds-and-window: 'fix' late in a long subject's prose is no fix commit")
    chk(len(_col(rows, "src/x/g.py").get("fixes") or []) == 1,
        "regression-kinds-and-window: a description that opens with 'fixes' is a fix commit")
    pend = M.regress_rows(*_pw_world(NP - M.DAY, [cm(9, NP - M.DAY + 50, MEMBER + ": paint", ["src/x/g.py"])]),
                          t_lo=NP - M.DAY, t_hi=NP, now=NP)
    s = M.regress_summary(pend)
    chk(s["no_polish"]["pending"] == 1 and s["no_polish"]["ripe"] == 0 and s["no_polish"]["ripe_regressed"] == 0,
        "regression-kinds-and-window: a row younger than 3 days is pending, never clean (%s)" % s["no_polish"])
    pub = M.regress_rows(*_pw_world(tb, [cm(10, tb + 100, "a subject naming nothing", ["src/x/h.py"])],
                                    published={"u-b": [("%x" % 10).rjust(40, "0")]}), t_lo=tb, t_hi=tb + M.DAY, now=NP)
    chk([r["file"] for r in pub] == ["src/x/h.py"], "regression-kinds-and-window: a sha the run printed as PUBLISHED is the bundle's")


def t_before_rule_not_measured():
    tb = M.POLISH_RULE_T - M.DAY
    commits = [cm(1, tb + 100, "polish: " + MEMBER + ": names", ["src/x/k.py"]),
               cm(2, tb + 100 + M.DAY, "RIMMANDRAKE_MEND_K_NAMES_SPLIT: fix", ["src/x/k.py"])]
    rows = M.regress_rows(*_pw_world(tb, commits), t_lo=tb, t_hi=tb + M.DAY, now=NP)
    s = M.regress_summary(rows)
    chk(_col(rows, "src/x/k.py").get("column") == "before_rule" and s["no_polish"]["files"] == 0
        and s["polish"]["files"] == 0, "before-rule-not-measured: a change before the rule is in its own column (%s)"
        % _col(rows, "src/x/k.py").get("column"))
    P = M.polish_numbers(commits, {}, M.src({"flags": [], "marks": []}), tb, tb + M.DAY, NP, probe=(True, None))
    chk(P["state"] == "not measured" and "changes" not in P, "before-rule-not-measured: a day before the rule reads not measured (%s)"
        % P["state"])


def t_polish_zero_needs_probe():
    lo = M.POLISH_RULE_T + M.DAY
    commits = [cm(1, lo + 100, MEMBER + ": paint", ["src/x/a.py"])]
    rv = M.src({"flags": [], "marks": []})
    P = M.polish_numbers(commits, {}, rv, lo, lo + M.DAY, NP, probe=(True, None))
    chk(P["state"] == "measured" and P["changes"] == 0, "polish-zero-needs-probe: a seen-able day with none reads 0 (%s)" % P)
    P = M.polish_numbers(commits, {}, rv, lo, lo + M.DAY, NP, probe=(False, "the probe saw 0 of its 1 planted polish: commit"))
    chk(P["state"] == M.CNL and "changes" not in P, "polish-zero-needs-probe: a failed probe reads could not look (%s)" % P["state"])
    ok, why = M.polish_probe()
    chk(ok is True, "polish-zero-needs-probe: the real probe sees its planted polish: commit (%s)" % why)
    ok, why = M.polish_probe(reader=lambda repo, since: M.src([]))
    chk(ok is False and why, "polish-zero-needs-probe: a blind reader fails the probe")


def t_polish_findings_from_reader():
    lo = M.POLISH_RULE_T + M.DAY
    commits = [cm(1, lo + 100, "polish: X_Y_Z_W: g", ["src/x/g.py"]),
               cm(2, lo + 200, "polish: X_Y_Z_W: h", ["src/x/h.py"]),
               cm(3, lo + 300, "polish: X_Y_Z_W: i", ["src/x/i.py"]),
               cm(4, lo + 400, "polish: X_Y_Z_W: j", ["src/x/j.py"]),
               cm(5, lo + 900, "X_Y_Z_W: the fresh read's significant finding in j, test first", ["src/x/j.py"])]
    rv = M.src({"flags": [{"path": "src/x/g.py", "t": lo + 600, "why": "w"}],
                "marks": [{"path": "src/x/h.py", "t": lo + 700, "verdict": "clean"},
                          {"path": "src/x/i.py", "t": lo + 50, "verdict": "clean"}]})
    P = M.polish_numbers(commits, {("%x" % 1).rjust(40, "0"): "WB-p"}, rv, lo, lo + M.DAY, NP, probe=(True, None))
    by = {r["files"][0]: r["read"] for r in P["rows"]}
    chk(P["changes"] == 4 and P["in_bundles"] == 1 and P["in_other_runs"] == 3,
        "polish-findings-from-reader: four polish changes, one in a bundle (%s)" % {k: P.get(k) for k in ("changes", "in_bundles")})
    chk(by == {"src/x/g.py": "finding", "src/x/h.py": "read clean", "src/x/i.py": "no recorded read",
               "src/x/j.py": "finding"}, "polish-findings-from-reader: each change classed by the reader's record after it (%s)" % by)
    chk(P["with_finding"] == 2 and P["read_clean"] == 1 and P["no_recorded_read"] == 1,
        "polish-findings-from-reader: the counts")


def _born_world(prev_bundle=(0, 0), today_bundle=(3, 2), single=(1, 2)):
    tb = T0 + 100
    units = ["rm-detached-b"] + (["rm-detached-b0"] if prev_bundle != (0, 0) else [])
    by = {"WB-x": bundle("WB-x", ["M%d" % i for i in range(1, 9)], units, T0 - M.DAY + 10)}
    runs = {"rm-detached-b": rec("rm-detached-b", "M1", tb + 3000), "rm-detached-s": rec("rm-detached-s", "S1", tb + 4000)}
    evs = []
    for i in range(today_bundle[0]):
        evs.append(ev("file", "NEW_B%d" % i, tb + 10 + i, role_unit="rm-detached-b"))
    for i in range(today_bundle[1]):
        evs.append(ev("close", "M%d" % (i + 1), tb + 100 + i, role_unit="rm-detached-b"))
    for i in range(single[0]):
        evs.append(ev("file", "NEW_S%d" % i, tb + 200 + i, role_unit="rm-detached-s"))
    for i in range(single[1]):
        evs.append(ev("close", "S%d" % (i + 1), tb + 300 + i, role_unit="rm-detached-s"))
    if prev_bundle != (0, 0):
        runs["rm-detached-b0"] = rec("rm-detached-b0", "M5", T0 - 1000)
        for i in range(prev_bundle[0]):
            evs.append(ev("file", "OLD_B%d" % i, T0 - 3000 + i, role_unit="rm-detached-b0"))
        for i in range(prev_bundle[1]):
            evs.append(ev("close", "M%d" % (i + 5), T0 - 2000 + i, role_unit="rm-detached-b0"))
    evs.sort(key=lambda e: e["ts"])
    return world(runs=runs, bundles=by, events=evs)


def t_born_per_closed_per_bundle_and_day():
    R = measure(_born_world())
    b = R["born"]
    chk(b["bundles"]["WB-x"]["born"] == 3 and b["bundles"]["WB-x"]["closed"] == 2 and b["bundles"]["WB-x"]["ratio"] == 1.5,
        "born-per-closed-per-bundle-and-day: a bundle that files 3 and closes 2 reads 1.5 (%s)" % b["bundles"].get("WB-x"))
    chk(b["by_kind"]["bundle"]["ratio"] == 1.5 and b["by_kind"]["single"]["ratio"] == 0.5,
        "born-per-closed-per-bundle-and-day: per kind (%s)" % b["by_kind"])
    chk(b["day"]["born"] == 4 and b["day"]["closed"] == 4 and b["day"]["ratio"] == 1.0,
        "born-per-closed-per-bundle-and-day: the day over the whole ledger (%s)" % b["day"])
    R = measure(_born_world(today_bundle=(2, 0), single=(0, 0)))
    chk(R["born"]["day"]["ratio"] == "no close" and R["born"]["bundles"]["WB-x"]["ratio"] == "no close",
        "born-per-closed-per-bundle-and-day: no close reads 'no close', never a ratio or 0 (%s)" % R["born"]["day"])
    R = measure(world(runs={}, events=None))
    chk(R["born"]["day"]["ratio"] == "no close" and R["born"]["day"]["born"] == 0,
        "born-per-closed-per-bundle-and-day: an empty day is 0 born and no close")
    S = _born_world()
    S["ledger"] = M.src(None, M.CNL, "no ledger")
    chk(measure(S)["born"]["state"] == M.CNL, "born-per-closed-per-bundle-and-day: an unread ledger reads could not look")


def t_born_line_two_days():
    R = measure(_born_world(prev_bundle=(2, 1)))
    L = R["lines"]["bundle_born_per_closed"]
    chk(L["crossed"] is True and L["today"] == 1.5 and L["day_before"] == 2.0,
        "born-line-two-days: over 1 on the day and the day before crosses (%s)" % L)
    R = measure(_born_world(prev_bundle=(1, 2)))
    chk(R["lines"]["bundle_born_per_closed"]["crossed"] is False, "born-line-two-days: one day over does not cross")
    R = measure(_born_world(today_bundle=(0, 0)))
    chk(R["lines"]["bundle_born_per_closed"]["crossed"] is False, "born-line-two-days: no bundle work does not cross")
    for k in ("regress", "polish"):
        chk(R["lines"].get(k, {}).get("line") is None, "born-line-two-days: %s draws no line (no evidence yet)" % k)


def t_lines_crossed_section():
    R = measure(_born_world(prev_bundle=(2, 1)))
    four = "\n\n".join(s + "\ntext" for s in M.SECTIONS)
    chk(M.report_ok(four, R) == M.LINES_SECTION, "lines-crossed-section: a crossed line needs its section")
    chk(M.report_ok(four + "\n\n" + M.LINES_SECTION + "\ntext", R) is None, "lines-crossed-section: with it the report passes")
    chk(M.report_ok(four, measure(_born_world())) is None, "lines-crossed-section: no crossed line, no section owed")
    chk("bundle_born_per_closed" in M.report_prompt(R, [], "2026-11-25", template="{READING}"),
        "lines-crossed-section: the report reads the lines")


def t_polish_watch_on_page_and_digest():
    od = os.path.join(TMP, "pw")
    os.makedirs(od, exist_ok=True)
    R = measure(_born_world(prev_bundle=(2, 1)))
    R["regress"] = {"state": "measured", "ripe_day": {"summary": M.regress_summary([])},
                    "today": {"summary": M.regress_summary([])}}
    R["polish"] = {"today": {"state": "measured", "changes": 3, "with_finding": 1, "read_clean": 0,
                             "no_recorded_read": 2, "in_bundles": 1, "in_other_runs": 2, "rows": []},
                   "ripe_day": {"state": "not measured", "cause": "before the polish: rule"}}
    L = M.summary(R, [], "/mnt/d/ClaudeWork/rimmandrake/work_bundle_monitor/report_2026-11-25.md", "written", "2026-11-25")
    M.write_json(os.path.join(od, "latest.json"), L)
    L = M.latest(od)
    md = "\n".join(M.page_md(L))
    chk("1.5 new tickets for each ticket closed" in md and "alarm is on" in md and "polish changes" not in md,
        "polish-watch-on-page-and-digest: the page shows the born answer and the line, and leaves the counts that "
        "answer no question to the report (%s)" % md[-600:])
    chk("token" not in md.lower() and "weighted" not in md.lower(), "polish-watch-on-page-and-digest: no token figure on the page")
    f = M.digest_fields(L)
    chk(f.get("born") == 4 and f.get("closed") == 4 and f.get("bundle_born") == 3 and f.get("bundle_closed") == 2
        and f.get("polish_changes") == 3 and f.get("polish_findings") == 1,
        "polish-watch-on-page-and-digest: the digest fields carry the counts (%s)" % f)
    from contracts import blind as BL
    import datetime as dt
    cut = dt.datetime(2026, 11, 25, 12, tzinfo=dt.timezone.utc)
    text = BL.render_digest(BL.project_digest("2026-11-25", None, cut, [], {}, None, None, None, f))
    chk("tickets born 4" in text and "closed 4" in text and "polish changes 3" in text and "LINE CROSSED" in text,
        "polish-watch-on-page-and-digest: the digest line renders the counts and the crossed line (%s)" %
        text.split("## Temporary Work Bundle Monitor")[-1][:500])


# ------------------------------------------------------------------------- the page section by meaning (owner, 2026-11-25)

import re as _re  # noqa: E402

ANSWER_LABELS = ("Are bundles used?", "Are bundles cheaper?", "Do bundles make new tickets?",
                 "Is work set down honestly?", "What needs a person?")
TICKET_RX = _re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,}\b")          # RIMMANDRAKE_FIX_..., HARNESS_REPAIR_...
BUNDLE_RX = _re.compile(r"\bWB-[A-Za-z0-9-]+")
STAMP_RX = _re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d|\b\d\d:\d\d:\d\dZ\b|\bUTC\b")
FIELD_RX = _re.compile(r"\b[a-z]+_[a-z_]+\b|\b[a-z]+\.[a-z_]+\.[a-z_]+\b|\bfix-unknown\b|\bno-tool\b|\bowner-act\b")
REAL_BID = "WB-mod-FlowWorks-20261125-080228"


def _sentences(text):
    t = _re.sub(r"`[^`]*`", "PATH", _re.sub(r"\*\*|<[^>]+>", "", text))
    return [s.strip() for s in _re.split(r"(?<=[.?!:;])\s+(?=[A-Z(])|\n+", t) if s.strip()]


def _words(s):
    return len([w for w in s.split() if _re.search(r"[A-Za-z0-9]", w)])


def _planted_reading(prev_bundle=(0, 0), today_bundle=(1, 4), bundle_at=None, headline=None):
    """A reading with real-shaped names: a bundle id and ticket ids that must never reach the page."""
    tb = T0 + 100
    at = T0 - M.DAY + 10 if bundle_at is None else bundle_at
    mem = ["RIMMANDRAKE_FIX_FLOW_PIPE_%s_TWICE" % w for w in ("ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX")]
    units = ["rm-detached-b"] + (["rm-detached-b0"] if prev_bundle != (0, 0) else [])
    by = {REAL_BID: bundle(REAL_BID, mem, units, at, system="mod:FlowWorks", pipeline="maturation")}
    runs = {"rm-detached-b": rec("rm-detached-b", mem[0], tb + 3000),
            "rm-detached-s": rec("rm-detached-s", "RIMMANDRAKE_SOLO_TICKET_ALONE", tb + 4000)}
    evs = [ev("file", "RIMMANDRAKE_NEW_FROM_BUNDLE_%d" % i, tb + 10 + i, role_unit="rm-detached-b")
           for i in range(today_bundle[0])]
    evs += [ev("close", mem[i], tb + 100 + i, role_unit="rm-detached-b") for i in range(today_bundle[1])]
    evs += [ev("close", "RIMMANDRAKE_SOLO_TICKET_ALONE", tb + 300, role_unit="rm-detached-s"),
            ev("file", "RIMMANDRAKE_SET_DOWN_FOR_LATER", tb + 400, role_unit="rm-detached-s",
               not_now={"class": "fix-unknown", "evidence": "e"})]
    if prev_bundle != (0, 0):
        runs["rm-detached-b0"] = rec("rm-detached-b0", mem[4], T0 - 1000)
        evs += [ev("file", "RIMMANDRAKE_OLD_FROM_BUNDLE_%d" % i, T0 - 3000 + i, role_unit="rm-detached-b0")
                for i in range(prev_bundle[0])]
        evs += [ev("close", mem[i + 4], T0 - 2000 + i, role_unit="rm-detached-b0") for i in range(prev_bundle[1])]
    evs.sort(key=lambda e: e["ts"])
    R = measure(world(runs=runs, bundles=by, events=evs))
    if headline:
        for k, v in headline.items():
            R["efficiency"]["headline_window"][k]["tokens_per_ticket_stayed_closed"] = v
    return R


def _planted_latest(name, R, verdicts=None, report_state="written"):
    od = os.path.join(TMP, name)
    os.makedirs(od, exist_ok=True)
    V = verdicts if verdicts is not None else [
        {"verdict": "NOT SINCERE", "role": "maturation in_game"}, {"verdict": "NOT SINCERE", "role": "maturation in_game"},
        {"verdict": "NOT SINCERE", "role": "detached helper"}, {"verdict": "SINCERE", "role": "bundle worker"}]
    L = M.summary(R, V, "/mnt/d/ClaudeWork/rimmandrake/work_bundle_monitor/report_2026-11-25.md", report_state,
                  "2026-11-25")
    L["monitor_tokens"] = {"judge_tokens": 4242424, "unit": "weighted_v2"}
    M.write_json(os.path.join(od, "latest.json"), L)
    return M.latest(od)


def _answers_of(md):
    """-> {label: the text after it on its line}, and the labels in the order they appear."""
    found = []
    for ln in md.splitlines():
        for lab in ANSWER_LABELS:
            if ("**%s**" % lab) in ln:
                found.append((lab, ln.split("**%s**" % lab, 1)[1].strip()))
    return dict(found), [f[0] for f in found]


def _section_ok(md, what):
    chk(not TICKET_RX.search(md), "%s: no ticket id (%s)" % (what, TICKET_RX.findall(md)[:3]))
    chk(not BUNDLE_RX.search(md), "%s: no bundle id (%s)" % (what, BUNDLE_RX.findall(md)[:3]))
    chk(not STAMP_RX.search(md), "%s: no ISO or UTC stamp (%s)" % (what, STAMP_RX.findall(md)[:3]))
    chk(not FIELD_RX.search(_re.sub(r"`[^`]*`", "", md)), "%s: no field, class or role key as a word (%s)" % (
        what, FIELD_RX.findall(_re.sub(r"`[^`]*`", "", md))[:3]))
    long = [s for s in _sentences(md.split("\n", 1)[1]) if _words(s) > 20]
    chk(not long, "%s: no sentence over 20 words (%s)" % (what, long[:2]))


def t_page_answers_five_questions():
    L = _planted_latest("answers", _planted_reading())
    md = "\n".join(M.page_md(L, now=NOW + 60))
    html = M.page_html(L, now=NOW + 60)
    _section_ok(md, "page-answers-five-questions")
    ans, order = _answers_of(md)
    chk(order == list(ANSWER_LABELS), "page-answers-five-questions: the five labels, once each, in order (%s)" % order)
    for lab in ANSWER_LABELS:
        body = _re.sub(r"\s*\([^)]*\)\s*$", "", ans.get(lab, ""))          # the one evidence number, in brackets
        n = len([s for s in _re.split(r"(?<=[.!?])\s+", body) if s.strip()])
        chk(n == 1, "page-answers-five-questions: one verdict sentence under %r (%r)" % (lab, ans.get(lab)))
    chk("Nov 25" in md and "PST" in md, "page-answers-five-questions: the day in local Pacific (%s)" % md[:300])
    chk("D:\\ClaudeWork\\rimmandrake\\work_bundle_monitor\\report_2026-11-25.md" in md,
        "page-answers-five-questions: the report's full Windows path, once")
    chk(md.count("report_2026-11-25.md") == 1, "page-answers-five-questions: the path is given once")
    chk("(4 of 5 closes, 80%)" in ans.get("Are bundles used?", ""),
        "page-answers-five-questions: the share of closes through a bundle is the evidence (%s)" % ans.get("Are bundles used?"))
    chk("in-game" in ans.get("Is work set down honestly?", "") and "3 of 4 not honest" in ans.get("Is work set down honestly?", ""),
        "page-answers-five-questions: not sincere count and the one role with the most, in plain words (%s)" %
        ans.get("Is work set down honestly?"))
    chk(ans.get("What needs a person?", "").startswith("Nothing"), "page-answers-five-questions: nothing crossed reads "
        "Nothing (%s)" % ans.get("What needs a person?"))
    chk(all(lab in html for lab in ANSWER_LABELS) and not BUNDLE_RX.search(html) and not TICKET_RX.search(html),
        "page-answers-five-questions: the HTML carries the same five answers and no id")
    chk("token" not in (md + html).lower() and "weighted" not in (md + html).lower() and "4242424" not in md + html,
        "page-answers-five-questions: still no token figure")


def t_page_too_young_says_too_early():
    R = _planted_reading()                         # the bundle began two days ago: the ripe day predates it
    L = _planted_latest("young", R)
    ans, _o = _answers_of("\n".join(M.page_md(L, now=NOW + 60)))
    a = ans.get("Are bundles cheaper?", "")
    first = M.when(NOW + 2 * M.DAY)
    chk("too early to tell" in a.lower() and first in a, "page-too-young-says-too-early: too early, with %r (%s)" % (first, a))
    R2 = _planted_reading(headline={"bundle": 400000, "single": 1000000})
    R2["efficiency"]["first_bundle"] = iso(NOW - 10 * M.DAY)
    a2 = _answers_of("\n".join(M.page_md(_planted_latest("ripe", R2), now=NOW + 60)))[0].get("Are bundles cheaper?", "")
    chk(a2.startswith("Yes") and "too early" not in a2.lower(), "page-too-young-says-too-early: a ripe cheaper bundle "
        "reads Yes (%s)" % a2)
    R3 = _planted_reading(headline={"bundle": 1500000, "single": 1000000})
    R3["efficiency"]["first_bundle"] = iso(NOW - 10 * M.DAY)
    a3 = _answers_of("\n".join(M.page_md(_planted_latest("dear", R3), now=NOW + 60)))[0].get("Are bundles cheaper?", "")
    chk(a3.startswith("No"), "page-too-young-says-too-early: a ripe dearer bundle reads No (%s)" % a3)


def t_page_line_crossed_needs_person():
    R = _planted_reading(prev_bundle=(3, 1), today_bundle=(5, 2))
    chk(R["lines"]["bundle_born_per_closed"]["crossed"] is True, "page-line-crossed-needs-person: the planted line is "
        "crossed (%s)" % R["lines"]["bundle_born_per_closed"])
    L = _planted_latest("crossed", R)
    md = "\n".join(M.page_md(L, now=NOW + 60))
    ans, _o = _answers_of(md)
    need = ans.get("What needs a person?", "")
    chk(need and not need.startswith("Nothing") and "Conductor" in need,
        "page-line-crossed-needs-person: the crossed line names an act and who does it (%s)" % need)
    chk(ans.get("Do bundles make new tickets?", "").startswith("Yes"),
        "page-line-crossed-needs-person: the new-ticket answer says yes (%s)" % ans.get("Do bundles make new tickets?"))
    _section_ok(md, "page-line-crossed-needs-person")
    stale = "\n".join(M.page_md(_planted_latest("stale", _planted_reading()), now=NOW + 3 * M.DAY))
    chk("Operations" in _answers_of(stale)[0].get("What needs a person?", ""),
        "page-line-crossed-needs-person: a reading over two days old asks Operations (%s)" %
        _answers_of(stale)[0].get("What needs a person?"))
    failed = "\n".join(M.page_md(_planted_latest("failed", _planted_reading(), report_state="failed: x"), now=NOW + 60))
    chk("Conductor" in _answers_of(failed)[0].get("What needs a person?", ""),
        "page-line-crossed-needs-person: a failed report asks the Conductor")
    bad = "\n".join(M.page_md(M.latest(os.path.join(TMP, "nothing-here-either")), now=NOW))
    a_bad, o_bad = _answers_of(bad)
    chk(o_bad == list(ANSWER_LABELS) and "Could not look" in bad and "Operations" in a_bad.get("What needs a person?", ""),
        "page-line-crossed-needs-person: an unreadable reading answers could not look and asks Operations")


def t_report_opens_with_answers():
    L = _planted_latest("report", _planted_reading())
    body = "# Temporary Work Bundle Monitor: daily report\n\n## The day's numbers\n\nx\n\n## The worst pattern\n\ny\n"
    text = M.compose_report(L, body, now=NOW + 60)
    i_need, i_detail, i_nums = (text.find("## What a person needs to know"), text.find("# Detail"),
                                text.find("## The day's numbers"))
    chk(0 < i_need < i_detail < i_nums, "report-opens-with-answers: the five answers, then a detail heading, then the "
        "tables (%s, %s, %s)" % (i_need, i_detail, i_nums))
    top = text[i_need:i_detail]
    _o = _answers_of(top)[1]
    chk(_o == list(ANSWER_LABELS), "report-opens-with-answers: the five labels in order (%s)" % _o)
    chk(text.count("\n# ") + text.startswith("# ") == 2 and "daily report\n\n## The day" not in text,
        "report-opens-with-answers: one title, the model's own title dropped")
    chk(M.report_ok(text, {}) is None or M.report_ok(text, {}) in M.SECTIONS,
        "report-opens-with-answers: the composed report still carries the model's sections")
    od = os.path.join(TMP, "rerender")
    os.makedirs(od, exist_ok=True)
    R = _planted_reading()
    M.write_json(os.path.join(od, "reading_2026-11-25.json"), R)
    with open(os.path.join(od, "verdicts_2026-11-25.jsonl"), "w") as f:
        f.write(json.dumps({"verdict": "NOT SINCERE", "role": "operations"}) + "\n")
    with open(os.path.join(od, "report_2026-11-25.md"), "w") as f:
        f.write(body)
    M.write_json(os.path.join(od, "latest.json"), {"date": "2026-11-25", "monitor_tokens": {"judge_tokens": 5}})
    chk(M.rerender("2026-11-25", od=od, now=NOW + 60) == 0 and M.rerender("2026-11-25", od=od, now=NOW + 60) == 0,
        "report-opens-with-answers: rerender writes the day again from its files, twice")
    again = open(os.path.join(od, "report_2026-11-25.md")).read()
    chk(again.count(M.REPORT_TOP) == 1 and again.count("## The day's numbers") == 1 and
        again == open(os.path.join(od, M.NEWEST)).read(), "report-opens-with-answers: a second rerender adds no second top")
    L2 = M.latest(od)
    chk(L2.get("cheaper", {}).get("verdict") == "too early" and L2.get("monitor_tokens") == {"judge_tokens": 5},
        "report-opens-with-answers: rerender writes latest.json with the cost word and keeps the old spend record")
    chk(M.rerender("2026-01-01", od=od) == 2, "report-opens-with-answers: a day with no files is could not look")


def main():
    for t in [t_bundle_unit_is_bundle_run, t_bundle_of_one_counts_single, t_unreadable_record_not_zero,
              t_missing_source_unmeasured, t_unpriced_run_not_zero_tokens, t_reopened_close_not_stayed,
              t_headline_tokens_per_stayed_close, t_program_filing_not_setdown, t_setdowns_by_class_and_role,
              t_backward_moves_classed, t_tokens_before_first_edit, t_bundle_live_ran_and_unrun,
              t_judge_failure_could_not_judge, t_judge_told_no_spend, t_page_section_no_tokens, t_digest_line_blind,
              t_baseline_same_system_before_first_bundle, t_report_needs_four_sections,
              t_polish_then_fix_one_regression, t_no_polish_fix_counts_no_polish, t_regression_kinds_and_window,
              t_before_rule_not_measured, t_polish_zero_needs_probe, t_polish_findings_from_reader,
              t_born_per_closed_per_bundle_and_day, t_born_line_two_days, t_lines_crossed_section,
              t_polish_watch_on_page_and_digest, t_page_answers_five_questions, t_page_too_young_says_too_early,
              t_page_line_crossed_needs_person, t_report_opens_with_answers]:
        print("-- %s" % t.__name__)
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            FAILS.append("%s raised %s: %s" % (t.__name__, type(e).__name__, e))
            print("FAIL %s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("selftest_work_bundle_monitor: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
