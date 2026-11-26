#!/usr/bin/env python3
"""selftest_shared_start.py — every fresh detached helper's first request is the same bytes as the last one's, so the
prompt cache serves it (RIMMANDRAKE_SHARE_HELPER_START_ONE_STATUS_LINE_REWRITES_IT). One test per promise of
design/specs/2026-11-26-shared-helper-start/boundary.md. Nothing here starts claude or a unit.
"""
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
TMP = tempfile.mkdtemp(prefix="selftest_shared_start_")
sys.path.insert(0, HERE)
sys.path.insert(0, UTILS)

import detached_helper as DH  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def _rec(name, root):
    c = os.path.join(TMP, name)
    os.makedirs(c, exist_ok=True)
    for f, text in (("CLAUDE.md", "# rules of " + "the project\n"), (".mcp.json", "{}")):
        with open(os.path.join(c, f), "w") as fh:
            fh.write(text)
    os.makedirs(DH.runs_dir(root), exist_ok=True)
    b = os.path.join(DH.runs_dir(root), name + ".brief.md")
    with open(b, "w") as fh:
        fh.write("the whole brief of " + name)
    return {"seat": "BENCH", "item": "ITEM_" + name.upper(), "clone": c, "unit": "rm-detached-bench-" + name,
            "model": "sonnet", "max_s": None, "budget_usd": 0.0, "state": root, "at": time.time(),
            "out": os.path.join(root, name + ".out.json"), "err": os.path.join(root, name + ".err"), "brief_file": b}


def _cmd(argv):
    return argv[argv.index("--") + 1:]


def _settings(cmd):
    return json.loads(cmd[cmd.index("--settings") + 1])


def t_a_fresh_run_gets_a_shared_start():
    root = os.path.join(TMP, "state")
    rec = _rec("fresh", root)
    why = DH.shared_start_plan(rec, root)
    argv = DH.launch_argv(rec, "the whole brief of fresh", "/bin/claude")
    cmd, st = _cmd(argv), None
    try:
        st = _settings(cmd)
    except (ValueError, IndexError):
        pass
    check(why is None and rec.get("shared_start") is True and len(rec.get("session") or "") == 36,
          "a-fresh-run-gets-a-shared-start: the plan names the session (%r)" % rec.get("session"))
    check("--session-id" in cmd and cmd[cmd.index("--session-id") + 1] == rec["session"],
          "a-fresh-run-gets-a-shared-start: --session-id")
    check("StandardInput=file:" + rec["prompt_file"] in argv and not any("the whole brief" in a for a in argv),
          "a-fresh-run-gets-a-shared-start: stdin is the fixed prompt; the brief is in no argument")
    check("RM_BRIEF=" + rec["brief_file"] in argv, "a-fresh-run-gets-a-shared-start: RM_BRIEF names the brief")
    check("CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=1" in argv and "CLAUDE_CODE_DISABLE_AUTO_MEMORY=1" in argv,
          "a-fresh-run-gets-a-shared-start: no git block, no auto-memory")
    md = os.path.join(rec["clone"], "CLAUDE.md")
    check("--append-system-prompt-file" in cmd and cmd[cmd.index("--append-system-prompt-file") + 1] == md
          and st is not None and st.get("claudeMdExcludes") == [md],
          "a-fresh-run-gets-a-shared-start: the project CLAUDE.md goes in the system prompt, not message 0")
    check(st is not None and (st.get("hooks") or {}).get("PostToolUse"),
          "a-fresh-run-gets-a-shared-start: the stop channel's PostToolUse hook survives the settings merge")
    check("--strict-mcp-config" in cmd and os.path.join(rec["clone"], ".mcp.json") in cmd,
          "a-fresh-run-gets-a-shared-start: the project's MCP set alone")


def t_a_resume_keeps_its_own_start():
    root = os.path.join(TMP, "state")
    rec = _rec("resumed", root)
    rec["resume_session"] = "00000000-0000-0000-0000-000000000001"
    why = DH.shared_start_plan(rec, root)
    argv = DH.launch_argv(rec, "the whole brief of resumed", "/bin/claude")
    cmd = _cmd(argv)
    check(bool(why) and rec.get("shared_start_off") == why and not rec.get("shared_start"),
          "a-resume-keeps-its-own-start: off (%s)" % why)
    check("--session-id" not in cmd and "StandardInput=file:" + rec["brief_file"] in argv
          and "CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=1" not in argv and "--strict-mcp-config" not in cmd
          and "--append-system-prompt-file" not in cmd and "claudeMdExcludes" not in _settings(cmd),
          "a-resume-keeps-its-own-start: the old argv, the brief on stdin")


def t_the_first_prompt_is_the_same_bytes():
    root = os.path.join(TMP, "state")
    a, b = _rec("pa", root), _rec("pb", root)
    for r in (a, b):
        DH.shared_start_plan(r, root)
    ta, tb = open(a["prompt_file"], "rb").read(), open(b["prompt_file"], "rb").read()
    named = [x for r in (a, b) for x in (r["item"], r["unit"], r["clone"], r["brief_file"], TMP) if x.encode() in ta]
    check(ta == tb and not named and b"RM_BRIEF" in ta,
          "the-first-prompt-is-the-same-bytes: same=%s, names %r" % (ta == tb, named))


def t_a_shared_start_transcript_is_found_by_its_session():
    import stop_resume as SR
    projects = os.path.join(TMP, "projects")
    root = os.path.join(TMP, "state")
    rec = _rec("tr", root)
    DH.shared_start_plan(rec, root)
    folder = DH.project_dir(rec["clone"], projects)
    os.makedirs(folder, exist_ok=True)
    mine = os.path.join(folder, rec["session"] + ".jsonl")
    with open(mine, "w") as fh:     # its first prompt is the fixed one: it names no item (the old reader's key)
        fh.write(json.dumps({"type": "user", "timestamp": "2026-11-26T09:00:00Z", "entrypoint": "sdk-cli",
                             "message": {"content": DH.SHARED_PROMPT}}) + "\n")
    DH.write_record(rec, root)
    got = (DH.session_of(rec["unit"], root, projects)[0], SR.session_of(rec, projects))
    check(got == (rec["session"], rec["session"]),
          "a-shared-start-transcript-is-found-by-its-session: %r (want the session named at launch)" % (got,))


def t_the_outcome_check_reads_the_newest_pair():
    import helper_start_share as HS
    d = os.path.join(TMP, "share")
    os.makedirs(d, exist_ok=True)

    def tr(name, read, wrote):
        p = os.path.join(d, name + ".jsonl")
        with open(p, "w") as fh:
            fh.write(json.dumps({"type": "assistant", "message": {"model": "m", "usage": {
                "input_tokens": 2, "cache_read_input_tokens": read, "cache_creation_input_tokens": wrote}}}) + "\n")
        return name

    class FakeDH:
        @staticmethod
        def find_transcript(sid):
            p = os.path.join(d, sid + ".jsonl")
            return p if os.path.exists(p) else None

        @staticmethod
        def run_session(unit):
            return None, None, "none"

    def r(u, at, model="sonnet", sid=None, **kw):
        return dict(unit=u, at=at, model=model, clone="/c/" + u, status="ended", session=sid, **kw)
    tr("hi", 53000, 7000)
    tr("lo", 11000, 50000)
    runs = lambda new_sid: [r("a", 100, sid="x"), r("b", 200, model="opus", sid="y"), r("c", 300, sid=new_sid),
                            r("z", 400, sid="q", resume_session="s")]      # a resume is not a fresh start
    q = ["--min-share", "0.7", "--model", "any"]
    got = (HS.main(q, runs("hi"), FakeDH), HS.main(q, runs("lo"), FakeDH),
           HS.main(q + ["--window-s", "50"], runs("hi"), FakeDH), HS.main(q, [], FakeDH),
           HS.main(q, runs("gone"), FakeDH), HS.main(q, [r("b", 200, model="opus", sid="y"), r("c", 300, sid="hi")],
                                                    FakeDH))
    got += (HS.main(["--min-share", "0.7"], runs("hi"), FakeDH),)     # default: opus only; one opus start, no pair
    check(got == (0, 1, 4, 3, 3, 4, 4), "the-outcome-check-reads-the-newest-pair: (pass, fail, no pair, empty records, "
                                     "no transcript, only another model before, default opus) = %r, want (0, 1, 4, 3, 3, 4, 4)" % (
                                         got,))


def main():
    tests = [t_a_fresh_run_gets_a_shared_start, t_a_resume_keeps_its_own_start, t_the_first_prompt_is_the_same_bytes,
             t_a_shared_start_transcript_is_found_by_its_session, t_the_outcome_check_reads_the_newest_pair]
    try:
        for t in tests:
            try:
                t()
            except Exception as e:  # noqa: BLE001  a raise is a red, named, never a crash that hides the rest
                check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("FAIL %d: %s" % (len(FAILS), "; ".join(FAILS)) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
