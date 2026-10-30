#!/usr/bin/env python3
r"""selftest_judge_codex_home.py — the GPT judge's own Codex home, lockdown flags and tool-call tripwire
(ARENA_GPTJUDGE_HARDEN_ISOLATED_CODEX_HOME). Offline: a fake codex, a fake shared home, event-stream fixtures shaped
like the live codex-cli 0.164 --json streams measured 2026-10-30. Never launches codex, never reads the real login.

  prompt     the judge prompt carries PROMPT_NO_TOOLS
  tripwire   clean / refused-tool (lockdown) streams are valid; a web item, an unknown tool item, a command naming a
             path outside the job folder (drive, UNC, WSL, ~, .., a sibling job, $env:, output listing) is INVALID;
             a missing / non-JSON / incomplete / failed stream or no job folder is INVALID (fail closed)
  wipe       per-call state (sessions, history, sqlite stores, tmp) goes; login, config, sandbox state stay
  setup      the login is a byte copy; config is OUR template (no plugins / MCP / notify from the shared home);
             a tampered config, a missing login or a differing sandbox state is refused per call
  auth       sync-in takes a newer shared login; sync-back is compare-and-swap
  session    overlapping calls: only the last one out wipes
  consult    gpt_consult --codex-home/--lockdown/--events: argv, CODEX_HOME+WSLENV, events + meta, real tokens
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import judge_codex_home as JH  # noqa: E402

FAILS = []
JOB = r"C:\Users\u\AppData\Local\Temp\codex\consult-1"
PS = r'"C:\\WINDOWS\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '   # doubled, as codex shows it


def check(ok, msg):
    print(("PASS  " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def stream(*items, completed=True, extra=()):
    ev = [{"type": "thread.started", "thread_id": "t"}, {"type": "turn.started"}]
    for i, it in enumerate(items):
        it = dict(it, id="item_%d" % i)
        if it["type"] not in ("agent_message", "error"):
            ev.append({"type": "item.started", "item": it})
        ev.append({"type": "item.completed", "item": it})
    ev += list(extra)
    if completed:
        ev.append({"type": "turn.completed", "usage": {"input_tokens": 100, "cached_input_tokens": 0,
                                                       "output_tokens": 20}})
    return "\n".join(json.dumps(e) for e in ev) + "\n"


MSG = {"type": "agent_message", "text": '{"verdict": "accept"}'}
REFUSED = {"type": "error", "message": "Code Mode is unavailable because code-mode host is disabled"}


def cmd(c, out=""):
    return {"type": "command_execution", "command": c, "aggregated_output": out, "exit_code": 0,
            "status": "completed"}


def t_prompt():
    import arena_judge as J                                          # noqa: PLC0415
    p = J.build_prompt("criteria", {"verdict": "pass"}, [], "diff --git a/x b/x", ("ralph_a", "trio"))
    check(JH.PROMPT_NO_TOOLS in p, "the judge prompt carries the no-commands/no-files/no-web line")
    check(all(w in JH.PROMPT_NO_TOOLS for w in ("command", "file", "web")), "the line names commands, files, web")


def t_tripwire():
    ok = JH.tripwire(stream(MSG), JOB)
    check(ok["valid"] and ok["n_tools"] == 0 and ok["web"] == 0, "clean transcript -> valid, 0 tools (%s)" % ok["why"])
    r = JH.tripwire(stream(REFUSED, MSG), JOB)
    check(r["valid"], "lockdown-shaped transcript (codex's own 'Code Mode is unavailable' error item) -> valid")
    inside = [PS + '"Get-ChildItem"', PS + '"Get-Content prompt.md"', PS + '"Get-Content %s\\\\prompt.md"'
              % JOB.replace("\\", "\\\\"), "Get-Content '%s\\prompt.md'" % JOB, "type .\\prompt.md"]
    for c in inside:
        r = JH.tripwire(stream(cmd(c), MSG), JOB)
        check(not r["valid"] and r["n_tools"] == 1 and r["commands"] == [c]
              and not any("outside" in w for w in r["why"]),
              "ANY command, even one confined to its job folder -> INVALID, counted, recorded, not called outside: %s"
              % c[-40:])
    outside = {
        "drive path": PS + '"Get-Content C:\\\\Windows\\\\win.ini"',
        "other drive": "Get-ChildItem D:\\ClaudeWork\\rimmandrake\\arena",
        "bare drive": "Get-ChildItem D:",
        "sibling job (prefix of the name)": "Get-Content %s0\\prompt.md" % JOB,
        "parent dir": "Get-Content ..\\consult-2\\answer.md",
        "parent dir bare": "cd ..",
        "UNC wsl": "Get-ChildItem \\\\wsl.localhost\\Ubuntu\\home\\u\\rm\\arena",
        "UNC doubled": PS + '"Get-ChildItem \\\\\\\\wsl$\\\\Ubuntu\\\\home"',
        "wsl path": "cat /mnt/d/ClaudeWork/x",
        "home tilde": "Get-ChildItem ~\\.codex",
        "env var": "Get-ChildItem $env:USERPROFILE",
        "cmd env var": "dir %USERPROFILE%",
        "registry drive": "Get-ChildItem HKCU:\\Software",
        "encoded": "powershell -EncodedCommand ZQBjAGgAbwA=",
        "network": "Invoke-WebRequest https://example.com",
        "wsl hop": "wsl ls",
    }
    for name, c in outside.items():
        r = JH.tripwire(stream(cmd(c), MSG), JOB)
        check(not r["valid"] and r["n_tools"] == 1, "command naming a location outside the job (%s) -> INVALID (%s)"
              % (name, (r["why"] or ["-"])[0][:90]))
    r = JH.tripwire(stream(cmd("Get-ChildItem", out="\r\n    Directory: D:\\ClaudeWork\\rimmandrake\r\n"), MSG), JOB)
    check(not r["valid"], "a harmless-looking command whose output lists an outside directory -> INVALID")
    r = JH.tripwire(stream(cmd("Get-ChildItem", out="    Directory: %s\r\n" % JOB), MSG), JOB)
    check(not any("output lists" in w for w in r["why"]), "output listing the job folder itself is not called outside")
    r = JH.tripwire(stream({"type": "web_search", "query": "rimworld"}, MSG), JOB)
    check(not r["valid"] and r["web"] == 1 and r["n_tools"] == 1, "a web_search item -> INVALID, web=1")
    r = JH.tripwire(stream({"type": "web_fetch_v2", "url": "x"}, MSG), JOB)
    check(not r["valid"] and r["web"] == 1, "any web* item type -> INVALID")
    r = JH.tripwire(stream({"type": "mcp_tool_call", "server": "s", "tool": "read"}, MSG), JOB)
    check(not r["valid"] and "cannot be vetted" in " ".join(r["why"]), "an unknown tool item -> INVALID (cannot vet)")
    r = JH.tripwire(stream({"type": "file_change", "changes": []}, MSG), JOB)
    check(not r["valid"], "a file_change item -> INVALID")
    for name, text, job in (("empty stream", "", JOB), ("no stream", None, JOB),
                            ("non-JSON line", stream(MSG) + "garbage\n", JOB),
                            ("no turn.completed", stream(MSG, completed=False), JOB),
                            ("turn.failed", stream(MSG, extra=[{"type": "turn.failed", "error": {}}]), JOB),
                            ("no job folder", stream(MSG), None), ("non-object event", "[1]\n" + stream(MSG), JOB)):
        r = JH.tripwire(text, job)
        check(not r["valid"] and r["why"], "%s -> INVALID, fail closed (%s)" % (name, (r["why"] or ["-"])[0][:60]))
    # GPT review r1 #7: completeness is the lifecycle, not one completion marker anywhere
    started = {"type": "item.started", "item": dict(cmd("Get-ChildItem"), id="late")}
    for name, text in (("a lone turn.completed", json.dumps({"type": "turn.completed"}) + "\n"),
                       ("a second turn started after the completed one",
                        stream(MSG) + json.dumps({"type": "turn.started"}) + "\n"),
                       ("a second turn with an item started, never completed",
                        stream(MSG) + json.dumps({"type": "turn.started"}) + "\n" + json.dumps(started) + "\n"),
                       ("a started item never completed, inside a completed turn", stream(MSG, extra=[
                           {"type": "item.started", "item": {"type": "reasoning", "id": "r9"}}])),
                       ("an orphan turn.completed then a new unfinished turn (net balance zero)",
                        stream(MSG) + json.dumps({"type": "turn.completed"}) + "\n"
                        + json.dumps({"type": "turn.started"}) + "\n"),
                       ("no turn at all (thread.started + a message only)",
                        json.dumps({"type": "thread.started"}) + "\n"
                        + json.dumps({"type": "item.completed", "item": dict(MSG, id="m")}) + "\n"),
                       ("an event type codex does not emit", stream(MSG, extra=[{"type": "tool.called"}])),
                       ("a top-level stream error", stream(MSG, extra=[{"type": "error", "message": "x"}]))):
        r = JH.tripwire(text, JOB)
        check(not r["valid"], "%s -> INVALID (%s)" % (name, (r["why"] or ["-"])[0][:60]))


def t_wipe(tmp):
    h = tmp / "wipehome"
    (h / "sessions" / "2026" / "10").mkdir(parents=True)
    (h / "sessions" / "2026" / "10" / "rollout.jsonl").write_text("x")
    (h / "shell_snapshots").mkdir()
    (h / "shell_snapshots" / "s.sh").write_text("x")
    (h / "tmp").mkdir()
    (h / "skills" / ".system").mkdir(parents=True)
    (h / ".sandbox").mkdir()
    for n in ("history.jsonl", "session_index.jsonl", "logs_2.sqlite", "logs_2.sqlite-wal", "state_5.sqlite",
              "state_5.sqlite-shm", "goals_1.sqlite", "auth.json", "config.toml", "models_cache.json", "version.json",
              "installation_id", "cap_sid"):
        (h / n).write_text("x")
    check(JH.leftover_state(h) == ["goals_1.sqlite", "history.jsonl", "logs_2.sqlite", "logs_2.sqlite-wal",
                                   "session_index.jsonl", "sessions", "shell_snapshots", "state_5.sqlite",
                                   "state_5.sqlite-shm"],
          "before the wipe: leftover_state sees the per-call state (%s)" % JH.leftover_state(h))
    gone = JH.wipe_call_state(h)
    left = sorted(p.name for p in h.iterdir())
    check({"sessions", "history.jsonl", "session_index.jsonl", "logs_2.sqlite", "logs_2.sqlite-wal", "state_5.sqlite",
           "state_5.sqlite-shm", "goals_1.sqlite", "shell_snapshots", "tmp"} <= set(gone),
          "wipe removes sessions, history, session index, sqlite stores (+wal/shm), snapshots, tmp (%d)" % len(gone))
    check(left == sorted(["auth.json", "config.toml", "models_cache.json", "version.json", "installation_id",
                          "cap_sid", "skills", ".sandbox"]), "wipe keeps login, config, sandbox state, skills (%s)" % left)
    check(JH.leftover_state(h) == [], "after the wipe nothing per-call is left")
    (h / "tmp").mkdir()
    (h / "log").mkdir()
    check(JH.leftover_state(h) == [], "empty tmp/ and log/ dirs are not leftovers")
    (h / "tmp" / "x").write_text("x")
    (h / "log" / "codex-tui.log").write_text("x")
    check(JH.leftover_state(h) == ["log", "tmp"], "POPULATED log/ and tmp/ (a delete that failed) are leftovers (%s)"
          % JH.leftover_state(h))


def fake_base(root: Path, sandbox=False) -> Path:
    b = root / "base"
    b.mkdir(parents=True)
    (b / "auth.json").write_bytes(b'{"tokens": {"refresh_token": "rt-A"}, "last_refresh": "2026-10-30T10:00:00Z"}\n')
    (b / "models_cache.json").write_text("{}")
    (b / "config.toml").write_text('model = "x"\nnotify = ["node", "n.js"]\n[plugins.slack]\nenabled = true\n'
                                   '[mcp_servers.node_repl]\ncommand = "node"\n[windows]\nsandbox = "elevated"\n')
    if sandbox:
        (b / ".sandbox").mkdir()
        (b / ".sandbox" / "setup_marker.json").write_text('{"created_at": "2026-10-01T00:00:00Z"}')
        (b / ".sandbox-secrets").mkdir()
        (b / ".sandbox-secrets" / "sandbox_users.json").write_text('{"u": 1}')
    return b


def t_setup(tmp):
    b = fake_base(tmp / "s1", sandbox=True)
    h = tmp / "s1" / "judge"
    msg = JH.setup(h, b, machine_check=False)
    check((h / "auth.json").read_bytes() == (b / "auth.json").read_bytes(), "setup: the login is a byte copy (%s)"
          % msg[-40:])
    cfg = (h / "config.toml").read_text()
    check(cfg == JH.config_template(b), "setup: config.toml is the judge template")
    check(not any(w in cfg for w in ("[plugins", "mcp_servers", "notify", "node")),
          "the template carries nothing of the shared config's plugins / MCP servers / notify hook")
    check('web_search = "disabled"' in cfg and 'sandbox = "elevated"' in cfg
          and all("%s = false" % f in cfg for f in JH.lockdown_features()),
          "the template: web search off, the shared [windows] sandbox mode, every lockdown feature false")
    try:
        JH.verify_home(h, b)
        check(True, "verify accepts the freshly set-up home")
    except JH.HomeError as ex:
        check(False, "verify accepts the freshly set-up home (%s)" % ex)
    check(JH.setup(h, b, machine_check=False).endswith("(already set up)"), "setup is idempotent")

    def refused(label, mutate, restore):
        mutate()
        try:
            JH.verify_home(h, b)
            check(False, "verify refuses: %s" % label)
        except JH.HomeError as ex:
            check("setup" in str(ex), "verify refuses: %s (%s)" % (label, str(ex)[-60:]))
        restore()
    good = cfg
    refused("config edited (a plugin added)", lambda: (h / "config.toml").write_text(good + "[plugins.x]\n"),
            lambda: (h / "config.toml").write_text(good))
    refused("config missing", lambda: (h / "config.toml").unlink(), lambda: (h / "config.toml").write_text(good))
    a = (h / "auth.json").read_bytes()
    refused("no login", lambda: (h / "auth.json").unlink(), lambda: (h / "auth.json").write_bytes(a))
    m = (h / ".sandbox" / "setup_marker.json").read_text()
    refused("sandbox state differs from the shared home",
            lambda: (h / ".sandbox" / "setup_marker.json").write_text('{"created_at": "2020"}'),
            lambda: (h / ".sandbox" / "setup_marker.json").write_text(m))
    b2 = tmp / "s2" / "base"
    b2.mkdir(parents=True)
    try:
        JH.setup(tmp / "s2" / "judge", b2, machine_check=False)
        check(False, "setup refuses a shared home with no login")
    except JH.HomeError:
        check(True, "setup refuses a shared home with no login")


def auth(rt, when):
    return ('{"tokens": {"refresh_token": "%s"}, "last_refresh": "%s"}\n' % (rt, when)).encode()


def t_auth(tmp):
    b, h = tmp / "a" / "base", tmp / "a" / "home"
    b.mkdir(parents=True)
    h.mkdir(parents=True)
    (b / "auth.json").write_bytes(auth("B2", "2026-10-30T12:00:00Z"))
    (h / "auth.json").write_bytes(auth("B1", "2026-10-30T10:00:00Z"))
    JH.sync_auth_in(h, b)
    check((h / "auth.json").read_bytes() == (b / "auth.json").read_bytes(), "sync-in: a newer shared login is taken")
    (h / "auth.json").write_bytes(auth("J3", "2026-10-30T13:00:00Z"))
    bs = JH.sync_auth_in(h, b)
    check(b"J3" in (h / "auth.json").read_bytes(), "sync-in: an older shared login never overwrites a newer judge one")
    hs = JH._sha(h / "auth.json")                                   # noqa: SLF001
    check(not JH.sync_auth_back(h, b, bs, hs), "sync-back: judge login unchanged during the call -> no write")
    (h / "auth.json").write_bytes(auth("J4", "2026-10-30T14:00:00Z"))
    check(JH.sync_auth_back(h, b, bs, hs) and b"J4" in (b / "auth.json").read_bytes(),
          "sync-back: a login rotated during the call is written back when the shared one is untouched")
    bs = JH._sha(b / "auth.json")                                   # noqa: SLF001
    hs = JH._sha(h / "auth.json")                                   # noqa: SLF001
    (h / "auth.json").write_bytes(auth("J5", "2026-10-30T15:00:00Z"))
    (b / "auth.json").write_bytes(auth("X9", "2026-10-30T14:30:00Z"))     # older than J5: only CAS refuses
    check(not JH.sync_auth_back(h, b, bs, hs) and b"X9" in (b / "auth.json").read_bytes(),
          "sync-back: the shared login changed meanwhile -> compare-and-swap refuses, shared copy untouched")


def t_session(tmp):
    os.environ["ARENA_JUDGE_LOCK_DIR"] = str(tmp / "locks")
    b, h = tmp / "c" / "base", tmp / "c" / "home"
    b.mkdir(parents=True)
    h.mkdir(parents=True)
    (b / "auth.json").write_bytes(auth("B2", "2026-10-30T12:00:00Z"))
    (h / "auth.json").write_bytes(auth("B1", "2026-10-30T10:00:00Z"))
    s1 = JH.CallSession(h, b).__enter__()
    check(b"B2" in (h / "auth.json").read_bytes(), "first call in syncs the shared login in")
    s2 = JH.CallSession(h, b).__enter__()
    (h / "sessions").mkdir()
    (h / "sessions" / "r.jsonl").write_text("x")
    (h / "history.jsonl").write_text("x")
    p1 = s1.after()
    s1.__exit__()
    check(not p1["last_out"] and (h / "sessions").exists(), "a call leaving while another is in flight does not wipe")
    p2 = s2.after()
    s2.__exit__()
    check(p2["last_out"] and "sessions" in p2["wiped"] and not (h / "history.jsonl").exists() and not p2["leftover"],
          "the last call out wipes the per-call state (%s)" % p2["wiped"])
    with JH.CallSession(h, b) as s3:
        (h / "history.jsonl").write_text("x")
        p3 = s3.after()
    check(p3["last_out"] and p3["wiped"] == ["history.jsonl"], "a lone call wipes after itself")
    # GPT review r1 #5: one lock per physical home, whatever the seat's temp dirs or the spelling of the path
    old = {k: os.environ.get(k) for k in ("TMPDIR", "XDG_RUNTIME_DIR", "ARENA_JUDGE_LOCK_DIR")}
    os.environ.pop("ARENA_JUDGE_LOCK_DIR")
    l1 = JH._lock_path(h)                                             # noqa: SLF001
    os.environ["TMPDIR"], os.environ["XDG_RUNTIME_DIR"] = str(tmp), str(tmp)
    try:
        check(str(l1.parent) == JH.LOCK_DIR and JH._lock_path(Path(str(h.parent) + "/./home")) == l1  # noqa: SLF001
              and JH._lock_path(h.parent / "x" / ".." / "home") == l1,  # noqa: SLF001
              "the lock is one per physical home in one fixed dir: other TMPDIR/XDG_RUNTIME_DIR and aliases share it")
    finally:
        for k, v in old.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
    # GPT review r1 #4: an entrant slipping in between the last call's unlock and relock must not lose the rotation
    import fcntl                                                      # noqa: PLC0415
    (b / "auth.json").write_bytes(auth("R1", "2026-10-30T16:00:00Z"))
    a = JH.CallSession(h, b).__enter__()
    check(b"R1" in (h / "auth.json").read_bytes(), "race setup: the cohort starts on the shared R1")
    (h / "auth.json").write_bytes(auth("R2", "2026-10-30T17:00:00Z"))   # codex rotated during A's call
    fcntl.flock(a.fd, fcntl.LOCK_UN)                                   # A's after(): unlocked, not yet relocked
    bsess = JH.CallSession(h, b).__enter__()                           # B gets in first-exclusive in the window
    pa = a.after()
    a.__exit__()
    pb = bsess.after()
    bsess.__exit__()
    check(not pa["last_out"] and pb["last_out"] and pb["auth_back"] and b"R2" in (b / "auth.json").read_bytes(),
          "race: B in between A's unlock and relock -> B's last out still writes A's rotated R2 back (%s)" % pb)
    s = json.loads(a.snap.read_text())
    check(s["base"] == s["home"] == JH._sha(b / "auth.json"),                # noqa: SLF001
          "once reconciled the snapshot is the new baseline (both shas = the written-back login)")
    # GPT review r2 #1: an entrant that never held the exclusive lock (it waited out the last-out) still has a baseline
    c = JH.CallSession(h, b)
    c.fd = os.open(str(c.lock), os.O_RDWR | os.O_CREAT, 0o600)
    fcntl.flock(c.fd, fcntl.LOCK_SH)                                   # admitted shared only, no initialisation
    (h / "auth.json").write_bytes(auth("R3", "2026-10-30T18:00:00Z"))
    pc = c.after()
    c.__exit__()
    check(pc["last_out"] and pc["auth_back"] and b"R3" in (b / "auth.json").read_bytes(),
          "an entrant admitted without initialising still writes its rotated R3 back (%s)" % pc)
    check(JH._lock_path(Path("/mnt/c/Users/Alice/.codex_arena_judge"))        # noqa: SLF001
          == JH._lock_path(Path("/mnt/c/users/alice/.codex_arena_judge")),   # noqa: SLF001
          "a Windows-drive home's case aliases share one lock")


FAKE_CODEX = r'''#!%s
import json, os, sys
rec = {"argv": sys.argv, "CODEX_HOME": os.environ.get("CODEX_HOME"), "WSLENV": os.environ.get("WSLENV", ""),
       "stdin": sys.stdin.read()}
open(%r, "w").write(json.dumps(rec))
a = sys.argv
open(a[a.index("-o") + 1] if os.path.isabs(a[a.index("-o") + 1]) else os.path.join(os.getcwd(), "answer.md"),
     "w").write('{"verdict": "accept"}')
if "--json" in a:
    print(json.dumps({"type": "thread.started"}))
    print(json.dumps({"type": "turn.started"}))
    print(json.dumps({"type": "turn.completed", "usage": {"input_tokens": 1000, "output_tokens": 234}}))
    sys.stderr.write("tools::router: error=code-mode host is disabled\n")
else:
    print("tokens used\n4,321")
'''


def t_consult(tmp):
    sys.path.insert(0, str(HERE.parent))
    import gpt_consult as gc                                        # noqa: PLC0415
    ci = gc.codex_image
    rec = tmp / "fake_codex_rec.json"
    fake = tmp / "fake_codex"
    fake.write_text(FAKE_CODEX % (sys.executable, str(rec)))
    fake.chmod(0o755)
    home = tmp / "consult_home"
    home.mkdir()
    saved = (ci.find_codex_cli, ci.CODEX_SCRATCH, ci.wsl_to_win, gc._receipt)
    old_log = os.environ.get("RM_GPT_CALL_LOG")
    os.environ["RM_GPT_CALL_LOG"] = str(tmp / "calls.jsonl")
    try:
        ci.find_codex_cli = lambda: fake
        ci.CODEX_SCRATCH = tmp / "scratch"
        ci.wsl_to_win = lambda p: str(p)                             # the fake runs on Linux and needs real paths
        gc._receipt = lambda *a, **k: None
        q = tmp / "q.md"
        q.write_text("judge this")
        try:
            gc.main(["--prompt-file", str(q), "--codex-home", str(home), "--lockdown", "--events", str(tmp / "e.jsonl")])
            check(False, "--codex-home with no login is refused")
        except SystemExit as ex:
            check("auth.json" in str(ex) and not rec.exists(), "--codex-home with no login is refused before codex runs")
        (home / "auth.json").write_text("{}")
        ev = tmp / "ev" / "events.jsonl"
        rc = gc.main(["--prompt-file", str(q), "--out", str(tmp / "ans.md"), "--codex-home", str(home), "--lockdown",
                      "--events", str(ev)])
        r = json.loads(rec.read_text())
        argv = r["argv"]
        check(rc == 0, "hardened consult answered (rc %s)" % rc)
        need = ["--json", "--ephemeral", "--ignore-rules", "--strict-config", 'web_search="disabled"', "-C"]
        check(all(x in argv for x in need), "argv carries %s" % ", ".join(need))
        dis = {argv[i + 1] for i, x in enumerate(argv) if x == "--disable"}
        check(dis == set(gc.LOCKDOWN_FEATURES) and {"shell_tool", "unified_exec", "code_mode_host"} <= dis,
              "argv disables every lockdown feature, incl. shell_tool, unified_exec, code_mode_host (%d)" % len(dis))
        cdir = argv[argv.index("-C") + 1]
        check(Path(cdir).parent == tmp / "scratch" and Path(cdir).name.startswith("consult-")
              and argv[argv.index("-o") + 1] == str(Path(cdir) / "answer.md"), "-C is the call's own job folder")
        check(r["CODEX_HOME"] == ci.wsl_to_win(home) or r["CODEX_HOME"] == str(home),
              "codex ran with CODEX_HOME = the judge home (%s)" % r["CODEX_HOME"])
        if ci.in_wsl():
            check("CODEX_HOME" in r["WSLENV"], "CODEX_HOME is named in WSLENV (else it never reaches codex.exe)")
        check(ev.is_file() and '"turn.completed"' in ev.read_text(), "the --json event stream is written to --events")
        meta = json.loads(Path(str(ev) + ".meta.json").read_text())
        check(meta["job_win"] == argv[argv.index("-C") + 1] and meta["lockdown"] and meta["refused_tool_calls"] == 1,
              "meta names the job folder, lockdown, and counts the refused tool attempt (%s)" % meta)
        cl = tmp / "calls.jsonl"
        logs = [json.loads(x) for x in cl.read_text().splitlines() if x.strip()] if cl.is_file() else []
        check(gc.events_tokens(ev.read_text()) == 1234, "events_tokens = input + output from turn.completed")
        check(len(logs) == 1 and logs[0].get("tokens_used") == 1234,
              "the metered record carries the real token count from the event stream (%d record(s))" % len(logs))
        rec.unlink()
        gc.main(["--prompt-file", str(q), "--out", str(tmp / "ans2.md")])
        argv = json.loads(rec.read_text())["argv"]
        check(not any(x in argv for x in ("--json", "--ephemeral", "--disable", "-C")),
              "no flags -> the old argv (an ordinary consult is unchanged)")
    finally:
        ci.find_codex_cli, ci.CODEX_SCRATCH, ci.wsl_to_win, gc._receipt = saved
        os.environ.pop("RM_GPT_CALL_LOG", None) if old_log is None else os.environ.__setitem__("RM_GPT_CALL_LOG",
                                                                                             old_log)


def main():
    tmp = Path(tempfile.mkdtemp(prefix="judge_codex_home_st_"))
    saved = {k: os.environ.get(k) for k in ("ARENA_JUDGE_LOCK_DIR", "ARENA_JUDGE_CODEX_HOME", "ARENA_JUDGE_CODEX_BASE")}
    try:
        os.environ["ARENA_JUDGE_CODEX_HOME"] = str(tmp / "unused_home")
        os.environ["ARENA_JUDGE_CODEX_BASE"] = str(tmp / "unused_base")
        t_prompt()
        t_tripwire()
        t_wipe(tmp)
        t_setup(tmp)
        t_auth(tmp)
        t_session(tmp)
        t_consult(tmp)
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
