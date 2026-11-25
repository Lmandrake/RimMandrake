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
    chk(k["tokens_per_close"] == 700, "unpriced-run-not-zero-tokens: its close is not divided into the priced tokens")
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
    chk(h["stayed"] == 1 and h["reopened"] == 1 and h["tokens_per_stayed_close"] == 1200 and h["runs"] == 2,
        "headline-tokens-per-stayed-close: 1200 tokens over 1 stayed close, 2 runs (%s)" % h["tokens_per_stayed_close"])
    runs = {"u3": rec("u3", "C", T0 + 100, tokens=400)}
    R = measure(world(runs=runs, events=[ev("close", "C", T0 + 90, role_unit="u3")]))
    chk(R["efficiency"]["today"]["single"]["tokens_per_stayed_close"] == "pending",
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
    chk("NOT SINCERE 1" in md and "Set-downs 1" in md, "page-section-no-tokens: the verdicts and the set-downs")
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
    chk(b.get("state") == "measured" and b.get("runs") == 1 and b.get("tokens") == 800 and b.get("closes") == 1,
        "baseline-same-system-before-first-bundle: one run of the home in the 14 days before (%s)" %
        {k: b.get(k) for k in ("state", "runs", "tokens", "closes")})


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
        chk(open(os.path.join(od, M.NEWEST)).read().startswith("## The day's numbers"),
            "report-needs-four-sections: a written report renews the newest copy")
    finally:
        os.environ["RM_WBM_OUT"] = os.path.join(TMP, "out")


def main():
    for t in [t_bundle_unit_is_bundle_run, t_bundle_of_one_counts_single, t_unreadable_record_not_zero,
              t_missing_source_unmeasured, t_unpriced_run_not_zero_tokens, t_reopened_close_not_stayed,
              t_headline_tokens_per_stayed_close, t_program_filing_not_setdown, t_setdowns_by_class_and_role,
              t_backward_moves_classed, t_tokens_before_first_edit, t_bundle_live_ran_and_unrun,
              t_judge_failure_could_not_judge, t_judge_told_no_spend, t_page_section_no_tokens, t_digest_line_blind,
              t_baseline_same_system_before_first_bundle, t_report_needs_four_sections]:
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
