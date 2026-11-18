#!/usr/bin/env python3
"""selftest_spend_blind_agents — no agent we launch is told its spend, its cap or what remains (owner 2026-11-16:
"I don't like how you're telling the agent how much it's spent. This has been shown to reduce their creativity and
obsess on cost savings..."), and the hard per-run stop still holds, enforced from outside (spend_watchdog.py).
Item RIMMANDRAKE_HIDE_SPEND_FROM_BUILDERS_CAP_NAGGED_EVERY_TURN.

  A  every launcher's built argv carries no --max-budget-usd (the flag makes the harness inject a `budget_usd` reminder
     every turn) and its prompt, footer, resume or packet text states no spend, cap or remainder; a capped launcher
     wraps claude in spend_watchdog with its cap.
  B  the watchdog stops a fake transcript over cap and leaves one under cap alone; empty, missing and malformed
     transcripts never stop a run; a real child process over cap is stopped and its out holds one cap result JSON.
  C  mutants that re-add the flag (wrap, source) or the footer's spend line are caught.
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
FAILS = []


def check(ok, what):
    print("%s  %s" % ("PASS" if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


# words that state spend to the agent; a launch text holding one fails
SPEND_RX = re.compile(r"(?i)spend bound|budget|already used|weighted tokens|\bspent\b|remaining|\$\s?\d")
FLAG = "--max-budget-usd"


def flag_lines(text):
    """-> the code lines (not comments, not a docstring line that only names the flag in prose) that pass the flag."""
    out = []
    for ln in text.splitlines():
        code = ln.split("#", 1)[0]
        if re.search(r"""["']--max-budget-usd["']|--max-budget-usd\s+["$%]""", code):
            out.append(ln.strip())
    return out


# ------------------------------------------------------------------ A: launchers
try:
    import spend_watchdog as SW
except ImportError as e:
    SW = None
    check(False, "A spend_watchdog imports (%s)" % e)

import detached_helper as DH  # noqa: E402
import role_launch as RL  # noqa: E402

rec = {"clone": "/tmp/clone", "unit": "rm-detached-bench-x-1", "seat": "BENCH", "item": "X_ITEM", "max_s": None,
       "model": "opus", "budget_usd": 15.0, "out": "/tmp/o.json", "err": "/tmp/e.txt", "state": "/tmp/st"}


def detached_argv():
    return DH.launch_argv(dict(rec), "the brief", "/usr/bin/claude")


a = detached_argv()
check(FLAG not in a, "A detached argv carries no %s" % FLAG)
check(any(str(x).endswith("spend_watchdog.py") for x in a) and "--cap-usd" in a and a[a.index("--cap-usd") + 1] == "15",
      "A detached argv wraps claude in spend_watchdog --cap-usd 15")
a0 = DH.launch_argv(dict(rec, budget_usd=0.0), "the brief", "/usr/bin/claude")
check(FLAG not in a0 and "--cap-usd" not in a0, "A detached --budget-usd 0 launches uncapped: no flag, no watchdog")
foot = DH.FOOTER.format(clone="/c", item="X", seat="BENCH", bound_text="no wall-time bound", budget="15")
check(not SPEND_RX.search(foot), "A detached footer states no spend or cap (%r)" % (SPEND_RX.search(foot) or [""])[0])

role = {"name": "Operations", "clone": "/tmp/clone", "model": "opus", "run_budget_usd": 6, "seat": "BENCH",
        "instructions": "roles/operations.md", "token_aware": True}
ra = RL.launch_argv(dict(role), "rm-role-operations-1", "msg", "/tmp/o", "/tmp/e", "/usr/bin/claude", session="s-1")
flat = [str(x) for x in ra]
check(FLAG not in flat, "A role argv carries no %s" % FLAG)
check("--cap-usd" in flat and flat[flat.index("--cap-usd") + 1] == "6", "A role argv wraps claude in spend_watchdog --cap-usd 6")
reading = {"runway": 2.0, "runway_m": "[A]", "week_left": 50, "week_left_m": "[A]", "at": "now"}
p = RL.prompt(role, "run", "tick", "green", reading, 300000, 300000, 1.0, 120000, "rm-role-operations-1")
check(not SPEND_RX.search(p), "A token_aware role prompt states no budget or spend (%r)" % (SPEND_RX.search(p) or [""])[0])
rp = RL.resume_prompt({"name": "Designer"}, {"unit": "u0", "error": "rate limit", "tokens": 1234, "budget": 9999, "n": 1},
                      "u1")
check(not SPEND_RX.search(rp), "A role resume prompt states no budget or spend (%r)" % (SPEND_RX.search(rp) or [""])[0])

import designer_stage as DS  # noqa: E402
st = {"stage": 1, "mod": "M", "running": {"run": "r1"}, "budget": {"cap": 900000, "spent": 400000, "reserve": 50000},
      "history": []}
try:
    pk = DS.packet("/tmp/d", st, {}, 300000)
except Exception as e:  # noqa: BLE001 - a packet that needs files: read its head line from source instead
    pk = None
    src = open(DS.__file__, encoding="utf-8").read()
    pk = src[src.index("def packet("):src.index("def packet(") + 1200]
check(not re.search(r"(?i)spent|task cap|weighted tokens", pk.split("End by writing")[0]),
      "A designer stage packet states no cap or spend")

import maturation_dispatch as MD  # noqa: E402
cb = MD.cert_brief("Pyrelands", {"t1": "ITEM_A"}, 12, {"t1": ["bar"]})
check(not SPEND_RX.search(cb), "A certificate brief states no spend bound (%r)" % (SPEND_RX.search(cb) or [""])[0])
import maturation_autonomy as MA  # noqa: E402
for kind in ("blocked", None):
    fb = MA.fixer_brief("ITEM_B", "Pyrelands", 9, fix_for=kind)
    check(not SPEND_RX.search(fb.split(MA.M.SELF_FIX_RULE)[0]), "A %s fixer brief states no spend bound" % (kind or "road-back"))
masrc = open(MA.__file__, encoding="utf-8").read()
check("Spend bound" not in masrc, "A maturation_autonomy writes no 'Spend bound' into any brief")
import maturation as MT  # noqa: E402
mtsrc = open(MT.__file__, encoding="utf-8").read()
check("Spend bound" not in mtsrc and "see your spend" not in mtsrc, "A maturation briefs state no spend bound")

sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "testq"))
import steward as TS  # noqa: E402
seen = []
real_run = TS.subprocess.run
TS.subprocess.run = lambda argv, **k: (seen.append(argv), subprocess.CompletedProcess(argv, 0, "", ""))[1]
try:
    TS.launch_wake("/tmp/clone", "/tmp/brief.md", "/tmp/log.txt", 5, 2700)
finally:
    TS.subprocess.run = real_run
wake = " ".join(str(x) for x in (seen[0] if seen else []))
check(seen and FLAG not in wake and "spend_watchdog.py" in wake and "--cap-usd 5" in wake,
      "A testq wake carries no %s and is wrapped with --cap-usd 5" % FLAG)

import coverage_judge as CJ  # noqa: E402
got = []
CJ.llm_reader("/tmp/d", "/tmp/repo", "u", charge=False,
              runner=lambda argv, repo, env, t: (got.append(argv), (0, "null"))[1])([{"id": "a"}])
check(got and FLAG not in got[0] and "--cap-usd" in got[0], "A coverage second reader carries no %s, wrapped" % FLAG)

# the whole tree: no code line passes the flag (the watchdog replaces it everywhere)
hits = []
for root in (os.path.join(REPO, "src"),):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ("bin", "obj", "__pycache__", "node_modules", "acceptance")]  # tests, not launchers
        for f in fn:
            if not f.endswith((".py", ".sh")) or f.startswith("selftest_") or f == "spend_watchdog.py":
                continue
            try:
                text = open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            hits += ["%s: %s" % (os.path.relpath(os.path.join(dp, f), REPO), x) for x in flag_lines(text)]
check(not hits, "A no launcher in src/ or whittle passes %s (%d: %s)" % (FLAG, len(hits), hits[:4]))

# ------------------------------------------------------------------ B: the watchdog
if SW:
    td = tempfile.mkdtemp(prefix="spendblind_")
    proj = os.path.join(td, "projects", "-tmp-clone")
    os.makedirs(proj)

    def line(mid, out_tok, ts="2026-11-16T10:00:00Z", model="claude-opus-5-5"):
        return json.dumps({"type": "assistant", "timestamp": ts, "message": {
            "id": mid, "model": model, "usage": {"input_tokens": 0, "cache_creation_input_tokens": 0,
                                                 "cache_read_input_tokens": 0, "output_tokens": out_tok}}}) + "\n"

    def put(sid, text):
        with open(os.path.join(proj, sid + ".jsonl"), "w", encoding="utf-8") as f:
            f.write(text)
    P = os.path.join(td, "projects")
    # opus at its rate: $1 = 1e6 / rate weighted tokens; an output token weighs 5
    one_usd = int(1e6 / SW.rate("claude-opus-5-5") / 5) + 1
    put("over", line("m1", one_usd * 3) + line("m2", one_usd * 3))          # ~$6 against a $5 cap
    put("under", line("m1", one_usd))                                        # ~$1
    put("empty", "")
    put("malformed", "{not json\n" + '{"type": "assistant", "message": {"id": "q", "usage": {"output_tokens": "x"}}}\n')
    check(SW.over_cap("over", 5, "claude-opus-5-5", P)[0] is True, "B over-cap transcript is stopped")
    check(SW.over_cap("under", 5, "claude-opus-5-5", P)[0] is False, "B under-cap transcript is left alone")
    for sid in ("empty", "missing", "malformed"):
        check(SW.over_cap(sid, 5, "claude-opus-5-5", P)[0] is False, "B %s transcript never stops a run" % sid)
    # a resumed session counts only the turns from its launch on
    put("resumed", line("old", one_usd * 9, ts="2026-11-01T00:00:00Z") + line("new", one_usd, ts="2026-11-16T10:00:00Z"))
    since = time.mktime(time.strptime("2026-11-10", "%Y-%m-%d"))
    check(SW.over_cap("resumed", 5, "opus", P, since=since)[0] is False, "B a resume does not count its earlier turns")
    # weighted_v2 (RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT): one list rate for every model, and a model not in
    # MODEL_PRICES is weighed as no other: the run is stopped, naming it (it was priced at the dearest v1 rate before)
    check(SW.rate("claude-fable-5-2") == SW.rate("claude-opus-5-5") == 4.0, "B one list rate, $4 per M weighted_v2")
    put("newmodel", line("m1", 10, model="claude-nonesuch-9-9"))
    oc = SW.over_cap("newmodel", 5, "opus", P)
    check(oc[0] is True and "claude-nonesuch-9-9" in (oc[3] or {}).get("unknown_model", ""),
          "B a transcript of a model not in the table stops the run, naming it (%r)" % (oc,))
    # argv: the session is pinned (injected when absent), a resume watches its own id
    w, sid, res = SW.pin_session(["claude", "-p", "x", "--model", "opus"])
    check(sid and "--session-id" in w and w[w.index("--session-id") + 1] == sid and not res, "B a fresh run gets a pinned session")
    w, sid, res = SW.pin_session(["claude", "-p", "x", "--resume", "abc"])
    check(sid == "abc" and res and "--session-id" not in w, "B a resume watches the resumed session")

    # a real child: writes a transcript past the cap then sleeps; the watchdog stops it and writes one cap result
    child = os.path.join(td, "fakeclaude.py")
    with open(child, "w") as f:
        f.write("import sys, time, os\nargv = sys.argv\nsid = argv[argv.index('--session-id') + 1]\n"
                "big = int(sys.argv[1])\n"
                "open(os.path.join(%r, sid + '.jsonl'), 'w').write(%r %% big)\n"
                "print('partial', flush=True)\nif big > 1: time.sleep(60)\nprint('{\"type\":\"result\",\"subtype\":\"success\"}')\n"
                % (proj, line("k", 0).replace('"output_tokens": 0', '"output_tokens": %d')))
    for big, want_stop in ((one_usd * 9, True), (1, False)):
        out = os.path.join(td, "out%d.json" % want_stop)
        t0 = time.time()
        with open(out, "w") as fo:
            rc = subprocess.run([sys.executable, SW.__file__, "--cap-usd", "5", "--poll-s", "0.3", "--projects", P,
                                 "--grace-s", "3", "--", sys.executable, child, str(big), "--model", "opus"],
                                stdout=fo, stderr=subprocess.DEVNULL, timeout=90).returncode
        txt = open(out).read()
        try:
            res = json.loads(txt)
        except ValueError:
            res = None
        if want_stop:
            check(isinstance(res, dict) and res.get("subtype") == "error_max_budget_usd" and res.get("is_error") is True
                  and res.get("stopped_by") == "spend_watchdog" and RL.run_tokens(res) and time.time() - t0 < 30
                  and rc != 0, "B a live child over cap is stopped; out is one cap result JSON (rc %s, %r)" % (rc, txt[:120]))
        else:
            check(rc == 0 and "partial" in txt and '"subtype":"success"' in txt,
                  "B a live child under cap runs to its end, its output passed through whole (rc %s)" % rc)

# ------------------------------------------------------------------ C: mutants
if SW:
    real_wrap = SW.wrap
    SW.wrap = lambda argv, cap, **k: real_wrap(argv, cap, **k) + [FLAG, "%g" % cap]
    try:
        m = detached_argv()
    finally:
        SW.wrap = real_wrap
    check(FLAG in m, "C mutant wrap that re-adds the flag is seen in the detached argv (the A check bites)")
check(flag_lines('cmd = [x, "--max-budget-usd", "%g" % b]') and flag_lines("claude -p --max-budget-usd $USD")
      and not flag_lines("# was --max-budget-usd, now the watchdog"), "C the source sweep catches a re-added flag, not a comment")
check(SPEND_RX.search(DH.FOOTER.replace("{bound_text}.", "{bound_text}; spend bound ${budget}.").format(
    clone="/c", item="X", seat="B", bound_text="b", budget="15")), "C a footer mutant restating the spend bound is caught")

print("\n%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
