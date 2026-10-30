#!/usr/bin/env python3
"""selftest_arena_judge.py - arena_judge.py, each criterion proven by FORCED FAILURE. No model is called: the judges
are in-process fakes, or a fake executable standing in for `claude`/gpt_consult inside the REAL judge sandbox.

ARENA_JUDGES_BUILD_BLIND_TO_THE_ARM criteria, and the failure planted for each:
  neutraliser   an arm diff planted with the arm name (content, a file path, separator/case variants), a trailer, a
                session URL, the clone path, an rm-arm-* branch, AGENTS.md and an out-of-area file. Unscrubbed, the
                leak scan REFUSES it (red); scrubbed, an independent substring check finds none of the plants (green),
                with bookkeeping and out-of-area files stripped
  replay        a hidden check (the original fix's test) passes on a good head (accepted) and fails on a known-bad
                head: REJECTED before any model is asked; the same bad head with the hidden checks removed is
                accepted by the same fakes (so it is the hidden check that rejects)
  votes         both accept -> accept; split -> third fresh run decides both ways; garbage / failing call -> invalid
  arm map       a fake model executable that tries to open the arm map: with the sandbox masks removed it CAN (red:
                the probe can see); through the judge's sandbox it cannot (green), and neither can a hidden check;
                a private dir inside a judge/arm root is refused; no verdict file names the arm
  guess report  exact binomial sanity; a planted leaky judge (reads the map with masks removed) is reported LEAKY;
                a blind one is not; the report file is written
Fix round 1 (judge_test_report.md), one forced failure per defect:
  sandbox rw    a write outside the scratch WORKS with the scratch widened (red) and fails through the judge (green);
                a hidden check cannot rewrite another task's hidden check, the next check's file or the host
  orphans       a timed-out check's detached grandchild survives a plain subprocess timeout (red), not the sandbox
  pass marker   os._exit(0), a hooked excepthook and a forged marker line are never `pass` (no 0 model calls spent)
  gate view     the raw gate record trips the leak scan on head12 (red); the whitelist view carries no folder, time,
                task, sha or step note; the arena event log and gate folders are unreadable in the sandbox
  glued names   RalphLoop / ralphs / myRalph / V3Arm / trioJudge / look-alike unicode / \\wsl$ / model names and
                Assisted-by trip the raw leak scan (red) and are gone after the scrub; `import trio` and 'v3.2'
                survive (reported ambiguous); agent config (CLAUDE.md, .claude/, specs/, .ralph/) is bookkeeping
  chance model  an always-the-majority guesser beats 1/len(labels) on the binomial (red) but is not LEAKY; exact
                hand cases p_high 1/6, two-sided 1/3
  model unset   with the preflight bypassed the GPT call is spent (red); with it, 0 model calls
  bad verdict   a corrupt verdict.json is skipped and counted, the report still written
 fix round 2 (GPT review of round 1; every case below failed against round-1 code):
  exits         sys.exit(0) / SystemExit(None) / atexit+exit / a forged marker raised in an IMPORTED arm module never
                pass; controls: sys.exit(main()) returning 0 passes, sys.exit(1) fails
  git drivers   a planted textconv / diff.external / filter / fsmonitor in the arm clone's .git/config and attributes
                RUNS under plain `git diff` (red) and never under neutralise + materialise
  odd names     tab, newline, non-ASCII, leading-dash, space and glob-star filenames: git quotes them (red); every one
                reaches the diff and the materialised tree
  replay miss   a replay task with no hidden-check file -> invalid, 0 model calls
  glued 2       xralph_afoo / trioxide / PREv3cSUFFIX refused and reported ambiguous; the human allowlist covers
                only what it lists
  isolation     real CLI runners with a spy model: no submission dir, raw tree, clone or judge id in argv/env/prompt/
                cwd; raw tree deleted before the call; planted env var and ARENA_* absent; a fresh empty workspace
                per judge, deleted after
  guess         seeded arm-independent random guesses are not leaky; consistently naming the next arm is LEAKY on
                the low tail; binomial at n=5000 does not overflow; the report states its decision rule
Writes only under a temp dir (ARENA_ROOT / ARENA_CLONES / ARENA_PRIVATE / ARENA_JUDGE_WORK point there).
"""
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arena_judge as J  # noqa: E402
import arena_tasks as A  # noqa: E402

FAILS = []
ARM = "ralph_a"
AREA = ["src/RimMandrake/Utils/demo/*"]


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()


def make_clone(root: Path, arm: str, value: int, plant=True) -> tuple:
    """An arm clone: base has demo/mod.py returning 0; head returns `value`, and (plant) carries every tell."""
    c = root / arm
    d = c / "src/RimMandrake/Utils/demo"
    d.mkdir(parents=True)
    git(c, "init", "-q", "-b", "main")
    git(c, "config", "user.email", "t@example.invalid")
    git(c, "config", "user.name", "t")
    (d / "mod.py").write_text("def value():\n    return 0\n")
    git(c, "add", "-A")
    git(c, "commit", "-q", "-m", "base")
    base = git(c, "rev-parse", "HEAD")
    git(c, "checkout", "-q", "-b", "rm-arm-" + arm)
    body = "def value():\n    return %d\n" % value
    if plant:
        body += ("\n# built by the %s loop; RALPH-A pass 3; Ralph A said so\n"
                 "# log: %s/src/RimMandrake/Utils/demo/run.log\n"
                 "# Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"
                 "# Claude-Session: https://claude.ai/code/session_019qicnDHbR9H6TTx77U9RfF\n"
                 "# pushed from refs/heads/rm-arm-%s\n" % (arm, c, arm))
        (d / ("%s_notes.py" % arm)).write_text("NOTE = 'x'\n")
        (c / "AGENTS.md").write_text("I am the %s arm\n" % arm)
        (c / "outside.txt").write_text("%s was here\n" % arm)
    (d / "mod.py").write_text(body)
    git(c, "add", "-A")
    git(c, "commit", "-q", "-m", "arm %s did it\n\nCo-Authored-By: someone" % arm)
    return c, base, git(c, "rev-parse", "HEAD")


HIDDEN_TEST = ("import sys, os\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\nimport mod\n"
               "assert mod.value() == 2, 'value() is %r' % mod.value()\nprint('hidden ok')\n")


def hidden_for(tid):
    return {"task": tid, "label": "clean",
            "checks": [{"type": "fix_test", "path": "src/RimMandrake/Utils/demo/selftest_demo.py", "added": True,
                        "body": HIDDEN_TEST}], "reworks": []}


def task_for(tid):
    return {"id": tid, "area": AREA, "criteria": "value() returns 2", "live": "none"}


class Fake:
    def __init__(self, answer):
        self.answer, self.calls = answer, 0

    def __call__(self, prompt, work):
        self.calls += 1
        if isinstance(self.answer, Exception):
            raise self.answer
        return self.answer


def ans(v, guess="unknown"):
    return 'thinking...\n{"verdict": "%s", "reasons": ["r"], "arm_guess": "%s"}' % (v, guess)


GATE = {"verdict": "pass", "arm": ARM, "steps": {"tests": "pass"}, "log": "/x/%s/gate.log" % ARM}


# ------------------------------------------------------------------ neutraliser

def t_neutraliser(tmp):
    clone, base, head = make_clone(Path(os.environ["ARENA_CLONES"]), ARM, 2)
    try:
        J.neutralise(clone, base, head, AREA, do_scrub=False)
        check(False, "forced: unscrubbed diff containing the arm name is refused by the leak scan")
    except J.NeutraliserLeak as ex:
        check("ralph" in str(ex).lower(), "forced: unscrubbed diff containing the arm name is refused (%s)" %
              str(ex)[:70])
    try:
        nd = J.neutralise(clone, base, head, AREA)
    except J.NeutraliserLeak as ex:
        check(False, "scrubbed diff passes the leak scan (%s)" % str(ex)[:80])
        return
    check(True, "scrubbed diff passes the leak scan")
    low = nd.text.lower()
    plants = {"arm name": "ralph", "clone path": str(clone).lower(), "trailer": "co-authored-by",
              "session": "session_019", "branch": "rm-arm-", "head sha": head[:7], "base sha": base[:7]}
    for what, s in plants.items():
        check(s not in low, "scrubbed diff holds no %s (%r)" % (what, s))
    check(nd.redactions.get("arm", 0) >= 4, "arm redactions counted (%s)" % nd.redactions.get("arm"))
    check("AGENTS.md" in nd.stripped and "outside.txt" in nd.stripped, "AGENTS.md and out-of-area file stripped")
    check("AGENTS" not in nd.text and "outside.txt" not in nd.text, "stripped files absent from the diff")
    check(any("<ARM>_notes.py" in f for f in nd.files) and "<ARM>_notes.py" in nd.text,
          "arm name in a file path re-written to <ARM>")
    check("+    return 2" in nd.text, "the real change survives neutralising")
    check(not J.find_leaks("value() returns 2\n", clone=clone), "leak scan is quiet on clean text (not vacuous)")
    check(bool(J.find_leaks("made by the V3C loop")), "leak scan sees another arm's name in upper case")
    g = J._gate_view(GATE, clone=clone)
    check("arm" not in g and ARM not in json.dumps(g), "gate record shown to judges carries no arm")


# ------------------------------------------------------------------ replay: known-bad rejected; votes

def t_replay(tmp):
    root = Path(os.environ["ARENA_CLONES"]) / "replay"
    good, gb, gh = make_clone(root / "good", "trio", 2, plant=False)
    bad, bb, bh = make_clone(root / "bad", "v3", 1, plant=False)
    o, g, t = Fake(ans("accept")), Fake(ans("accept")), Fake(ans("accept"))
    r = J.judge(task=task_for("T_GOOD"), hidden=hidden_for("T_GOOD"), clone=good, base=gb, head=gh, arm="trio",
                gate=GATE, judges=J.Judges(o, g, t))
    check(r["verdict"] == "accept" and r["hidden"][0]["result"] == "pass",
          "control: good replay output passes the hidden check and is accepted (%s)" % r["verdict"])
    o, g, t = Fake(ans("accept")), Fake(ans("accept")), Fake(ans("accept"))
    r = J.judge(task=task_for("T_BAD"), hidden=hidden_for("T_BAD"), clone=bad, base=bb, head=bh, arm="v3",
                gate=GATE, judges=J.Judges(o, g, t))
    check(r["verdict"] == "reject" and r["hidden"][0]["result"] == "fail",
          "forced: known-bad replay output is REJECTED by its hidden check (%s)" % r.get("why", "")[:60])
    check(o.calls == g.calls == 0, "known-bad output never reached a model")
    o, g, t = Fake(ans("accept")), Fake(ans("accept")), Fake(ans("accept"))
    r = J.judge(task=task_for("T_BAD"), hidden=None, clone=bad, base=bb, head=bh, arm="v3", gate=GATE,
                judges=J.Judges(o, g, t))
    check(r["verdict"] == "accept", "same bad output with hidden checks removed is accepted by the same fakes")
    unauth = {"checks": [], "reworks": [{"item": "X", "tests": []}]}
    r = J.judge(task=task_for("T_U"), hidden=unauth, clone=good, base=gb, head=gh, arm="trio", gate=GATE,
                judges=J.Judges(Fake(ans("accept")), Fake(ans("accept")), Fake(ans("accept"))))
    check(r["hidden"][0]["result"] == "UNMEASURED", "an unauthored rework check is UNMEASURED, never pass")

    def run(a, b, c):
        fs = [Fake(x) for x in (a, b, c)]
        rr = J.judge(task=task_for("T_V"), hidden=None, clone=good, base=gb, head=gh, arm="trio", gate=GATE,
                     judges=J.Judges(*fs))
        return rr, fs
    rr, fs = run(ans("accept"), ans("reject"), ans("reject"))
    check(rr["verdict"] == "reject" and fs[2].calls == 1, "split -> third fresh run, majority reject")
    rr, fs = run(ans("reject"), ans("accept"), ans("accept"))
    check(rr["verdict"] == "accept" and fs[2].calls == 1, "split -> third fresh run, majority accept")
    rr, fs = run(ans("reject"), ans("reject"), ans("accept"))
    check(rr["verdict"] == "reject" and fs[2].calls == 0, "agreement -> no third run")
    rr, fs = run("I think it is fine", ans("accept"), ans("accept"))
    check(rr["verdict"] == "invalid", "an unparseable judge answer is invalid, never accept")
    rr, fs = run(ans("accept"), RuntimeError("codex died"), ans("accept"))
    check(rr["verdict"] == "invalid", "a failed judge call is invalid, never accept")
    r = J.judge(task=task_for("T_G"), hidden=None, clone=good, base=gb, head=gh, arm="trio",
                gate=dict(GATE, verdict="fail"), judges=J.Judges(Fake(ans("accept")), Fake(ans("accept")),
                                                                 Fake(ans("accept"))))
    check(r["verdict"] == "reject", "a failed gate is not accepted")


# ------------------------------------------------------------------ arm map unreadable from the judge process

FAKE_MODEL = r'''
import json, sys
MAP = %r
try:
    m = json.load(open(MAP)); readable = True
except OSError as ex:
    m, readable = {}, False
import os
guess = "unknown"
if readable and m:
    # a judge with the masks gone finds its submission as the one sibling dir with no verdict yet (its own cwd is
    # now an anonymous workspace), then reads that judge id's arm from the map
    import glob
    cur = [os.path.basename(d) for d in glob.glob(os.path.join(os.path.dirname(os.path.dirname(MAP)), "guess_*", "J*"))
           if not os.path.exists(os.path.join(d, "verdict.json"))]
    guess = (m[cur[0]] if cur and cur[0] in m else next(iter(m.values())))["arm"]
out = json.dumps({"verdict": "accept", "reasons": ["map_readable=%%s" %% readable], "arm_guess": guess})
if "--prompt-file" in sys.argv:
    open(sys.argv[sys.argv.index("--out") + 1], "w").write(out)
else:
    sys.stdin.read(); print(out)
'''


def t_arm_map(tmp):
    os.environ["ARENA_JUDGE_OPUS_MODEL"] = "fake-model-for-selftest"
    priv = Path(os.environ["ARENA_PRIVATE"])
    amap = J.ArmMap()
    amap.assign("trio", "T0", "b", "h")
    mp = amap.path
    check(mp.is_file() and (mp.stat().st_mode & 0o077) == 0, "arm map exists, mode 0600")
    fake = tmp / "fake_model.py"
    fake.write_text(FAKE_MODEL % str(mp))
    work = Path(os.environ["ARENA_JUDGE_WORK"]) / "probe"
    work.mkdir(parents=True)
    opener = [sys.executable, "-c", "open(%r).read()" % str(mp)]
    real_masks = J.judge_masks
    try:
        J.judge_masks = lambda priv=None: []
        r = J.run_sandboxed(opener, work=work)
        check(r.returncode == 0, "forced: with the sandbox masks removed, the judge process CAN open the map")
        out = J.OpusCLI(prefix=[sys.executable, str(fake)])("prompt", work)
        check('"map_readable=True"' in out and '"unknown"' not in out, "forced: unmasked fake model reads the map")
    finally:
        J.judge_masks = real_masks
    r = J.run_sandboxed(opener, work=work)
    err = r.stderr.decode("utf-8", "replace")
    last = err.strip().splitlines()[-1][:70] if err.strip() else "rc=%d, no stderr" % r.returncode
    check(r.returncode != 0 and "FileNotFoundError" in err, "judge process cannot open the arm map (%s)" % last)
    check(mp.is_file(), "the map is still there outside the sandbox (the mask hid it, nothing deleted it)")
    for name, call in (("opus", J.OpusCLI(prefix=[sys.executable, str(fake)])),
                       ("gpt", J.GptConsult(prefix=[sys.executable, str(fake)]))):
        out = call("prompt", work)
        check('"map_readable=False"' in out and '"unknown"' in out, "%s judge runner, sandboxed: map unreadable" % name)
    r = J.run_sandboxed([sys.executable, "-c", "import os; print(os.listdir(%r))" % os.environ["ARENA_CLONES"]],
                        work=work)
    check(r.returncode == 0 and r.stdout.strip() == b"[]", "the arm clone root is empty to the judge process")
    clone, base, head = make_clone(Path(os.environ["ARENA_CLONES"]) / "mapcheck", "v3c", 2, plant=False)
    sneaky = {"checks": [{"type": "fix_test", "path": "src/RimMandrake/Utils/demo/selftest_sneak.py",
                          "body": "open(%r).read()\n" % str(mp)}], "reworks": []}
    r = J.judge(task=task_for("T_S"), hidden=sneaky, clone=clone, base=base, head=head, arm="v3c", gate=GATE,
                judges=J.Judges(Fake(ans("accept")), Fake(ans("accept")), Fake(ans("accept"))))
    check(r["hidden"][0]["result"] == "fail" and "FileNotFoundError" in r["hidden"][0]["tail"],
          "a hidden check cannot open the arm map either")
    for f in Path(os.environ["ARENA_JUDGE_WORK"]).glob("J*/verdict.json"):
        rec = json.loads(f.read_text())
        if amap.arm_of(rec["judge_id"]) and amap.arm_of(rec["judge_id"]) in f.read_text():
            check(False, "verdict %s names its arm" % f.parent.name)
            break
    else:
        check(True, "no verdict file names its arm")
    p = A.paths()
    for bad in (Path(os.environ["ARENA_JUDGE_WORK"]) / "priv", p["tasks"] / "priv",
                Path(os.environ["ARENA_CLONES"]) / "priv", p["root"] / "judge" / "priv"):
        try:
            J.ArmMap(p, bad)
            check(False, "private dir inside a judge/arm root is refused: %s" % bad)
        except J.PrivateLocationError:
            check(True, "private dir inside a judge/arm root is refused: %s" % bad.parent.name)
    J.ArmMap(p, priv)  # the real one is accepted
    os.environ.pop("ARENA_JUDGE_OPUS_MODEL", None)
    os.environ.pop("ANTHROPIC_DEFAULT_OPUS_MODEL", None)
    try:
        J.opus_model()
        check(False, "no Opus model in the environment -> refuse")
    except J.JudgeUnavailable:
        check(True, "no Opus model in the environment -> refuse (no model id in code)")


# ------------------------------------------------------------------ arm-guess report

def t_guess(tmp):
    check(abs(J.binom_sf(0, 10, 0.2) - 1.0) < 1e-12 and abs(J.binom_sf(1, 1, 0.2) - 0.2) < 1e-12,
          "binomial tail sanity: P(X>=0)=1, P(X>=1|n=1)=q")
    check(abs(J.binom_sf(3, 3, 0.5) - 0.125) < 1e-12, "binomial tail sanity: 3/3 at q=.5 is .125")
    amap = {"J%d" % i: {"arm": J.ARMS[i % 5]} for i in range(30)}
    leaky = [{"judge_id": j, "votes": [{"judge": "opus", "arm_guess": a["arm"]}]} for j, a in amap.items()]
    rng = random.Random(20261029)                # GPT review #10: blind = guesses drawn WITHOUT looking at the arm
    blind = [{"judge_id": j, "votes": [{"judge": "opus", "arm_guess": rng.choice(J.ARMS)}]} for j in amap]
    wrong = [{"judge_id": j, "votes": [{"judge": "opus", "arm_guess": J.ARMS[(J.ARMS.index(a["arm"]) + 1) % 5]}]}
             for j, a in amap.items()]
    rl, rb, rw = J.guess_report(leaky, amap), J.guess_report(blind, amap), J.guess_report(wrong, amap)
    floor = 2.0 / (J.MC_DRAWS + 1)               # two-sided: twice the one-sided Monte Carlo floor
    check(rl["blinding"] == "LEAKY" and rl["pooled"]["p_value"] <= floor + 1e-12,
          "forced: 30/30 correct guesses -> LEAKY (p=%.1e, the two-sided permutation floor)" % rl["pooled"]["p_value"])
    check(rb["blinding"] == "not shown leaky",
          "arm-independent seeded random guesses (%d/30) -> not shown leaky (p=%.2f)"
          % (rb["pooled"]["correct"], rb["pooled"]["p_value"]))
    check(rw["blinding"] == "LEAKY" and rw["pooled"]["correct"] == 0 and rw["pooled"]["p_high"] == 1.0,
          "forced: consistently naming the NEXT arm (0/30) -> LEAKY on the low tail (p=%.1e; one-sided p_high=1)"
          % rw["pooled"]["p_value"])
    check("PERMUTATION" in rl["decision"] and "binomial" in rl["decision"] and "binom_p" in rl["pooled"],
          "report states LEAKY is the permutation test, not the naive binomial, and still prints binom_p")
    big = J.binom_sf(1200, 5000, 0.2)
    check(0.0 < big < 1.0 and abs(J.binom_sf(1000, 5000, 0.2) - 0.5) < 0.02 and J.binom_sf(2500, 5000, 0.2) == 0.0,
          "binomial at n=5000 does not overflow and is sane (P(X>=1200)=%.1e, P(X>=1000)~.5)" % big)
    many = {"J%d" % i: {"arm": J.ARMS[i % 5]} for i in range(5000)}
    rbig = J.guess_report([{"judge_id": j, "votes": [{"judge": "opus", "arm_guess": J.ARMS[0]}]} for j in many], many)
    check(rbig["pooled"]["guesses"] == 5000 and 0.0 <= rbig["pooled"]["binom_p"] <= 1.0,
          "a 5000-submission report is produced (binom_p=%.2f)" % rbig["pooled"]["binom_p"])
    check(J.guess_report([], {})["blinding"] == "UNMEASURED", "no guesses -> UNMEASURED, not 'not leaky'")
    # end to end: a judge that can read the map (masks removed) is caught by the report; a sandboxed one is not
    fake = tmp / "fake_model.py"
    os.environ["ARENA_JUDGE_OPUS_MODEL"] = "fake-model-for-selftest"
    root = Path(os.environ["ARENA_CLONES"]) / "guess"
    real_masks = J.judge_masks

    def batch(tag, masked):
        wb = tmp / ("guess_" + tag)
        for i in range(10):
            arm = J.ARMS[i % 5]
            c, b, h = make_clone(root / tag / str(i), arm, 2, plant=False)
            call = [sys.executable, str(fake)]
            if not masked:
                J.judge_masks = lambda priv=None: []
            try:
                J.judge(task=task_for("T_E%d" % i), hidden=None, clone=c, base=b, head=h, arm=arm, gate=GATE,
                        judges=J.Judges(J.OpusCLI(prefix=call), J.GptConsult(prefix=call), J.OpusCLI(prefix=call)),
                        work_base=wb)
            finally:
                J.judge_masks = real_masks
        return J.write_report(work_base=wb)
    out = batch("leaky", masked=False)
    rep = json.loads(out.read_text())
    check(out.is_file() and rep["blinding"] == "LEAKY" and rep["pooled"]["correct"] == 20,
          "forced: report from a map-reading judge is produced and says LEAKY (%s)" % out.name)
    out = batch("blind", masked=True)
    rep = json.loads(out.read_text())
    check(rep["blinding"] == "not shown leaky" and rep["pooled"]["guesses"] == 20 and rep["pooled"]["correct"] == 0,
          "report from sandboxed judges: 0/20 correct, not shown leaky")
    check(set(rep["per_judge"]) == {"opus", "gpt"}, "report has a row per judge")


# ------------------------------------------------------------------ fix round 1 (judge_test_report.md)

def t_sandbox_rw(tmp):
    work = Path(os.environ["ARENA_JUDGE_WORK"]) / "rwprobe"
    work.mkdir(parents=True)
    host = tmp / "host_write_probe.txt"
    w = [sys.executable, "-c", "open(%r, 'w').write('x')" % str(host)]
    r = J.run_sandboxed(w, work=work, rw=[work, tmp])
    check(r.returncode == 0 and host.is_file(), "forced: with the host dir made writable, the probe CAN write it")
    host.unlink(missing_ok=True)
    r = J.run_sandboxed(w, work=work)
    check(r.returncode != 0 and not host.exists(), "judge sandbox: a write outside the scratch fails (read-only root)")
    p = A.paths()
    p["judge"].mkdir(parents=True, exist_ok=True)
    other = p["judge"] / "OTHER.json"
    other.write_text('{"checks": []}')
    clone, base, head = make_clone(Path(os.environ["ARENA_CLONES"]) / "tamper", "trio", 2, plant=False)
    evil = ("import os\n"
            "for t in (%r, %r, os.path.join(os.getcwd(), '..', 'tree', 'src/RimMandrake/Utils/demo/selftest_demo.py'),"
            " os.path.abspath(%r)):\n"
            "    try:\n"
            "        os.makedirs(os.path.dirname(t), exist_ok=True); open(t, 'w').write('raise SystemExit(0)\\n')\n"
            "        print('WROTE', t)\n"
            "    except OSError as ex:\n"
            "        print('blocked', type(ex).__name__)\n") % (str(other), str(host), J.__file__)
    hidden = {"checks": [{"type": "fix_test", "path": "src/RimMandrake/Utils/demo/selftest_evil.py", "body": evil},
                         {"type": "fix_test", "path": "src/RimMandrake/Utils/demo/selftest_demo.py",
                          "body": HIDDEN_TEST.replace("== 2", "== 3")}], "reworks": []}
    jsrc = Path(J.__file__).read_bytes()
    r = J.judge(task=task_for("T_RW"), hidden=hidden, clone=clone, base=base, head=head, arm="trio", gate=GATE,
                judges=J.Judges(Fake(ans("accept")), Fake(ans("accept")), Fake(ans("accept"))))
    tails = r["hidden"][0].get("tail", "")
    check("WROTE" not in tails and other.read_text() == '{"checks": []}' and not host.exists()
          and Path(J.__file__).read_bytes() == jsrc,
          "a hidden check cannot rewrite another task's hidden check, the judge code or the host (%s)"
          % " ".join(x for x in tails.split() if x in ("blocked", "WROTE"))[:40])
    check(r["hidden"][1]["result"] == "fail" and r["verdict"] == "reject",
          "the next check still runs its own body (value()==3 fails -> reject), not a planted exit")


GRANDCHILD = ("import subprocess, sys, time\n"
              "subprocess.Popen(['sh', '-c', 'sleep 4; echo alive > %s'], start_new_session=True)\n"
              "time.sleep(60)\n")


def t_orphans(tmp):
    import time
    work = Path(os.environ["ARENA_JUDGE_WORK"]) / "orphan"
    work.mkdir(parents=True)
    flag = work / "alive"
    try:
        subprocess.run([sys.executable, "-c", GRANDCHILD % flag], timeout=2)
    except subprocess.TimeoutExpired:
        pass
    time.sleep(4)
    check(flag.is_file(), "forced: a plain subprocess timeout leaves the detached grandchild running (it wrote)")
    flag.unlink(missing_ok=True)
    t0 = time.time()
    r = J.run_sandboxed([sys.executable, "-c", GRANDCHILD % flag], work=work, timeout=2)
    time.sleep(4)
    check(r.returncode == 124 and not flag.exists() and time.time() - t0 < 30,
          "sandbox timeout kills the whole tree: the grandchild never wrote (rc %d)" % r.returncode)


def t_marker(tmp):
    clone, base, head = make_clone(Path(os.environ["ARENA_CLONES"]) / "marker", "v3", 2, plant=False)
    check(J._check_result(0, b"hidden ok\n", "ab" * 16) == "no_marker",
          "rc 0 alone is not a pass (the pre-fix rule would call this pass)")
    bodies = {"os._exit(0) on import": "import os\nos._exit(0)\nassert False\n",
              "hooked excepthook": "import sys, os\nsys.excepthook = lambda *a: os._exit(0)\nassert False, 'x'\n",
              "forged marker": "import os\nprint('ARENA_CHECK_DONE ' + 'f' * 32)\nos._exit(0)\n",
              "atexit exit 0": "import atexit, os\natexit.register(lambda: os._exit(0))\nassert False\n"}
    for what, body in bodies.items():
        hidden = {"checks": [{"type": "fix_test", "path": "src/RimMandrake/Utils/demo/selftest_x.py", "body": body}],
                  "reworks": []}
        fs = [Fake(ans("accept")) for _ in range(3)]
        r = J.judge(task=task_for("T_M"), hidden=hidden, clone=clone, base=base, head=head, arm="v3", gate=GATE,
                    judges=J.Judges(*fs))
        res = r["hidden"][0]["result"]
        check(res in ("no_marker", "fail") and r["verdict"] in ("invalid", "reject") and fs[0].calls == 0,
              "%s is never a pass (%s -> %s, 0 model calls)" % (what, res, r["verdict"]))
    good = {"checks": [{"type": "fix_test", "path": "src/RimMandrake/Utils/demo/selftest_demo.py",
                        "body": HIDDEN_TEST}], "reworks": []}
    r = J.judge(task=task_for("T_M"), hidden=good, clone=clone, base=base, head=head, arm="v3", gate=GATE,
                judges=J.Judges(Fake(ans("accept")), Fake(ans("accept")), Fake(ans("accept"))))
    check(r["hidden"][0]["result"] == "pass" and "<NONCE>" in r["hidden"][0].get("tail", "<NONCE>"),
          "control: a real check that runs to its end passes via the marker")


def t_gate_view(tmp):
    head, base = "a1b2c3d4e5f6" + "0" * 28, "f" * 40
    stamp = "20261029T120000Z"
    gate = {"verdict": "pass", "passed": True, "task": "T1", "arm": ARM, "base": base, "head": head, "ts": stamp,
            "log_dir": "/arena/judge/gate/%s_T1_%s_%s" % (ARM, head[:12], stamp),
            "record_file": "/arena/judge/gate/%s_T1_%s_%s/gate.json" % (ARM, head[:12], stamp),
            "steps": {"tests": {"status": "pass", "why": "builder b-17 ran it"}}, "unmeasured": []}
    raw = {k: v for k, v in gate.items() if k != "arm"}
    raw["log_dir"] = raw["log_dir"].replace(ARM, "x")
    check(bool(J.find_leaks(json.dumps(raw), shas=(base, head))),
          "forced: the raw gate record (arm key dropped) still trips the leak scan on head12")
    g = J._gate_view(gate, shas=(base, head))
    txt = json.dumps(g)
    check(set(g) <= {"verdict", "passed", "steps", "unmeasured"} and head[:12] not in txt and stamp not in txt
          and "b-17" not in txt and "T1" not in txt and g["steps"] == {"tests": "pass"},
          "gate view is a whitelist: verdict + step status only (%s)" % txt[:60])
    p = A.paths()
    ev = p["root"] / "events"
    ev.mkdir(parents=True, exist_ok=True)
    (ev / "harness.jsonl").write_text('{"arm": "%s", "head": "%s"}\n' % (ARM, head))
    gd = p["root"] / "judge" / "gate" / ("%s_T1_%s_%s" % (ARM, head[:12], stamp))
    gd.mkdir(parents=True, exist_ok=True)
    (gd / "gate.json").write_text(json.dumps(gate))
    work = Path(os.environ["ARENA_JUDGE_WORK"]) / "gateprobe"
    work.mkdir(parents=True)
    rd = [sys.executable, "-c", "import os,sys; r=sys.argv[1]; print([os.path.join(d, f) for d, _, fs in os.walk(r) "
          "for f in fs]); print(open(os.path.join(r, 'events', 'harness.jsonl')).read())", str(p["root"])]
    r = subprocess.run(rd, capture_output=True)
    check(r.returncode == 0 and ARM.encode() in r.stdout, "forced: unsandboxed, the event log names the arm")
    r = J.run_sandboxed(rd, work=work)
    check(r.returncode != 0 and ARM.encode() not in r.stdout and head[:12].encode() not in r.stdout,
          "in the sandbox the arena root (event log, gate folders) is empty")


GLUED = {"camel suffix": "class RalphLoop:", "plural": "the ralphs ran", "camel prefix": "myRalph = 1",
         "arm camel": "V3Arm()", "arm camel 2": "trioJudge.run()", "fullwidth": "ｒａｌｐｈ was here",
         "cyrillic": "rаlph was here", "zero width": "ral​ph was here",
         "model": "reviewed with GPT and Claude", "assisted": "# Assisted-by: Claude", "generated": "# Generated-by: Codex",
         "opus": "ask Opus first", "wsl$": None}
KEEP = ("import trio\n", "from trio.lowlevel import x\n", "VERSION = 'v3.2'\n")


def t_glued(tmp):
    clone = Path(os.environ["ARENA_CLONES"]) / "gluedclone"
    clone.mkdir(parents=True)
    GLUED["wsl$"] = "log at \\\\wsl$\\Ubuntu%s\\src" % str(clone).replace("/", "\\")
    for what, s in GLUED.items():
        raw = J.find_leaks(s, clone=clone)
        out, _ = J.scrub(s, clone=clone)
        after = J.find_leaks(out, clone=clone)
        low = out.lower()
        gone = all(w not in low for w in ("ralph", "v3", "trio", "gpt", "claude", "codex", "opus", "wsl$"))
        check(bool(raw) and not after and gone, "%s: raw scan refuses, scrub removes (%r -> %r)" % (what, s[:24],
                                                                                                   out[:28]))
    for s in KEEP:
        amb = []
        out, _ = J.scrub(s)
        check(out == s and not J.find_leaks(s, ambiguous=amb), "code kept intact: %r" % s.strip())
    amb = []
    J.find_leaks("import trio\nVERSION = 'v3.2'\n", ambiguous=amb)
    check(len(amb) >= 2, "the kept import/version are reported as ambiguous (%s)" % amb)
    for f in ("CLAUDE.md", "sub/CLAUDE.md", ".claude/settings.json", "specs/plan.md", ".ralph/state",
              "GEMINI.md", ".codex/config.toml"):
        check(J.is_arm_bookkeeping(f), "agent config is bookkeeping: %s" % f)
    check(not J.is_arm_bookkeeping("src/RimMandrake/Utils/demo/mod.py"), "real code is not bookkeeping")


# ------------------------------------------------------------------ fix round 2 (GPT review of round 1)

def clone_files(root: Path, files: dict, msg="head") -> tuple:
    """A clone whose head adds/changes `files` (relpath -> text) over a base holding demo/mod.py returning 0."""
    c = root
    d = c / "src/RimMandrake/Utils/demo"
    d.mkdir(parents=True)
    git(c, "init", "-q", "-b", "main")
    git(c, "config", "user.email", "t@example.invalid")
    git(c, "config", "user.name", "t")
    (d / "mod.py").write_text("def value():\n    return 0\n")
    git(c, "add", "-A")
    git(c, "commit", "-q", "-m", "base")
    base = git(c, "rev-parse", "HEAD")
    for rel, text in files.items():
        f = c / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)
    git(c, "add", "-A")
    git(c, "commit", "-q", "-m", msg)
    return c, base, git(c, "rev-parse", "HEAD")


DEMO = "src/RimMandrake/Utils/demo/"
UNFINISHED = ("import sys, os\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\nimport mod\n"
              "assert False, 'the check never got past the import'\n")


def t_exits(tmp):
    """GPT review #2: an exit raised INSIDE an imported arm module must not finish the check."""
    mods = {"sys.exit(0) in arm module": "import sys\nsys.exit(0)\n",
            "SystemExit(None) in arm module": "raise SystemExit(None)\n",
            "os._exit(0) in arm module": "import os\nos._exit(0)\n",
            "atexit + sys.exit(0) in arm module": "import atexit, os, sys\natexit.register(lambda: os._exit(0))\n"
                                                  "sys.exit(0)\n",
            "exit inside an atexit handler": "import atexit, sys\natexit.register(sys.exit, 0)\nsys.exit(0)\n",
            "forged marker without the nonce": "import sys\nprint('ARENA_CHECK_DONE')\nprint('ARENA_CHECK_DONE ' + "
                                               "'0' * 32)\nsys.stdout.flush()\nsys.exit(0)\n"}
    hidden = {"checks": [{"type": "fix_test", "path": DEMO + "selftest_unfinished.py", "body": UNFINISHED}],
              "reworks": []}
    for i, (what, body) in enumerate(mods.items()):
        c, b, h = clone_files(Path(os.environ["ARENA_CLONES"]) / "exits" / str(i), {DEMO + "mod.py": body})
        fs = [Fake(ans("accept")) for _ in range(3)]
        r = J.judge(task=task_for("T_X"), hidden=hidden, clone=c, base=b, head=h, arm="v3", gate=GATE,
                    judges=J.Judges(*fs))
        res = r["hidden"][0]["result"] if r["hidden"] else r.get("why", "")[:40]
        check(res in ("fail", "no_marker") and r["verdict"] in ("reject", "invalid") and fs[0].calls == 0,
              "forced: %s is never a pass (%s -> %s, 0 model calls)" % (what, res, r["verdict"]))
    c, b, h = clone_files(Path(os.environ["ARENA_CLONES"]) / "exits" / "ok",
                          {DEMO + "mod.py": "def value():\n    return 2\n"})
    for what, body, want in (
            ("sys.exit(main()) returning 0", "import sys, os\nsys.path.insert(0, os.path.dirname("
             "os.path.abspath(__file__)))\ndef main():\n    import mod\n    return 0 if mod.value() == 2 else 1\n"
             "sys.exit(main())\n", "pass"),
            ("sys.exit(1) from the check itself", "import sys\nsys.exit(1)\n", "fail")):
        hd = {"checks": [{"type": "fix_test", "path": DEMO + "selftest_ctl.py", "body": body}], "reworks": []}
        r = J.judge(task=task_for("T_X"), hidden=hd, clone=c, base=b, head=h, arm="v3", gate=GATE,
                    judges=J.Judges(Fake(ans("accept")), Fake(ans("accept")), Fake(ans("accept"))))
        check(r["hidden"][0]["result"] == want, "control: %s -> %s (%s)" % (what, want, r["hidden"][0]["result"]))


EVIL = "#!/bin/sh\ntouch %s/ran_$$\n[ -n \"$1\" ] && [ -f \"$1\" ] && cat \"$1\" || cat\n"


def t_git_drivers(tmp):
    """GPT review #3: an arm clone's .git/config + attributes naming commands must never run as the harness."""
    sent = tmp / "sentinel"
    sent.mkdir()
    evil = tmp / "evil.sh"
    evil.write_text(EVIL % sent)
    evil.chmod(0o755)
    c, b, h = clone_files(Path(os.environ["ARENA_CLONES"]) / "drivers" / "v3",
                          {DEMO + "mod.py": "def value():\n    return 2\n", ".gitattributes": "* diff=evil filter=evil\n"})
    (c / ".git" / "info").mkdir(exist_ok=True)
    (c / ".git" / "info" / "attributes").write_text("* diff=evil filter=evil export-subst\n")
    with open(c / ".git" / "config", "a") as f:
        f.write('[diff "evil"]\n\ttextconv = %s\n[diff]\n\texternal = %s\n[filter "evil"]\n\tsmudge = %s\n'
                '\tclean = %s\n\trequired = true\n[core]\n\tfsmonitor = %s\n' % ((evil,) * 5))
    subprocess.run(["git", "-C", str(c), "diff", b, h, "--", "src"], capture_output=True)
    n1 = len(list(sent.iterdir()))
    subprocess.run(["git", "-C", str(c), "diff", "--no-ext-diff", b, h, "--", "src"], capture_output=True)
    n2 = len(list(sent.iterdir())) - n1
    check(n1 > 0 and n2 > 0, "forced: plain `git diff` in the arm clone RUNS the planted external diff (%d) and, "
                             "with --no-ext-diff, the textconv (%d)" % (n1, n2))
    for f in sent.iterdir():
        f.unlink()
    nd = J.neutralise(c, b, h, AREA)
    tree = J.materialise(c, h, AREA, tmp / "drivers_tree")
    ran = sorted(x.name for x in sent.iterdir())
    check(not ran and "+    return 2" in nd.text and (tree / DEMO / "mod.py").read_text().endswith("return 2\n"),
          "neutralise + materialise run NO planted textconv/external/filter/fsmonitor command (%d ran) and still "
          "produce the real diff and tree" % len(ran))


ODD = {"tab": DEMO + "a\tb.py", "newline": DEMO + "new\nline.py", "non-ascii": DEMO + "naïve_été.py",
       "leading dash": DEMO + "-dash.py", "spaces": DEMO + "sp ace s.py", "star": DEMO + "st*r.py"}


def t_odd_names(tmp):
    """GPT review #7: filenames git would quote are diffed and materialised, not silently dropped."""
    files = {rel: "TOKEN_%d = 1\n" % i for i, rel in enumerate(ODD.values())}
    files[DEMO + "mod.py"] = "def value():\n    return 2\n"
    c, b, h = clone_files(Path(os.environ["ARENA_CLONES"]) / "odd" / "v3", files)
    plain = subprocess.run(["git", "-C", str(c), "diff", "--name-only", b, h], capture_output=True, text=True).stdout
    check(any(l.startswith('"') for l in plain.splitlines()),
          "forced: git's default --name-only QUOTES such names (the round-1 reader's input)")
    nd = J.neutralise(c, b, h, AREA)
    for i, (what, rel) in enumerate(ODD.items()):
        check("TOKEN_%d = 1" % i in nd.text, "%s in a filename: the file's change reaches the diff" % what)
    check(len(nd.files) == len(files), "every changed file is listed (%d of %d)" % (len(nd.files), len(files)))
    tree = J.materialise(c, h, AREA, tmp / "odd_tree")
    got = [rel for rel in ODD.values() if (tree / rel).is_file()]
    check(len(got) == len(ODD), "every odd name is materialised for the hidden checks (%d of %d)" % (len(got), len(ODD)))


def t_replay_missing(tmp):
    """GPT review #8: a replay task with its hidden-check file missing fails CLOSED."""
    c, b, h = make_clone(Path(os.environ["ARENA_CLONES"]) / "replaymiss", "v3", 1, plant=False)
    fs = [Fake(ans("accept")) for _ in range(3)]
    task = dict(task_for("RP_T_MISSING"), source_item="SOME_ITEM_FIXED")
    r = J.judge(task=task, hidden=None, clone=c, base=b, head=h, arm="v3", gate=GATE, judges=J.Judges(*fs))
    check(r["verdict"] == "invalid" and fs[0].calls == fs[1].calls == 0 and "hidden-check" in r.get("why", ""),
          "forced: replay task without its hidden-check file -> invalid, 0 model calls (%s)" % r["verdict"])


def t_glued2(tmp):
    """GPT review #6: an arm name glued inside a longer identifier is refused unless a human allowlisted it."""
    for s in ("xralph_afoo = 1\n", "trioxide = 1\n", "PREv3cSUFFIX = 2\n"):
        amb = []
        hits = J.find_leaks(s, ambiguous=amb, allow=())
        check(bool(hits) and any(a.startswith("glued:") for a in amb),
              "forced: glued arm name refused and reported ambiguous: %r (%s)" % (s.strip(), hits[:1]))
    check(not J.find_leaks("xralph_afoo = 1\n", allow=("xralph_afoo",)), "an allowlisted identifier is accepted")
    al = A.paths()["root"] / "glued_allowlist.txt"
    al.write_text("# human-ruled: not arm names\ntrioxide\n")
    try:
        check(not J.find_leaks("trioxide = 1\n") and bool(J.find_leaks("xralph_afoo = 1\n")),
              "the allowlist FILE covers only what it lists")
    finally:
        al.unlink()
    check(not J.find_leaks("value() returns 2\nimport trio\nVERSION = 'v3.2'\n", allow=()),
          "glued scan is quiet on clean text and on the reported import/version exemptions")
    c, b, h = clone_files(Path(os.environ["ARENA_CLONES"]) / "glued" / "v3", {DEMO + "mod.py": "xralph_afoo = 2\n"})
    fs = [Fake(ans("accept")) for _ in range(3)]
    r = J.judge(task=task_for("T_GL"), hidden=None, clone=c, base=b, head=h, arm="v3", gate=GATE, judges=J.Judges(*fs))
    check(r["verdict"] == "invalid" and fs[0].calls == 0, "a submission carrying a glued arm name is invalid, unjudged")


SPY_MODEL = r"""
import json, os, sys
prompt = open(sys.argv[sys.argv.index("--prompt-file") + 1]).read() if "--prompt-file" in sys.argv else sys.stdin.read()
dump = {"argv": sys.argv, "cwd": os.getcwd(), "env": dict(os.environ), "prompt": prompt, "ls": sorted(os.listdir("."))}
open("spy_dump.json", "w").write(json.dumps(dump))
out = json.dumps({"verdict": "accept", "reasons": ["r"], "arm_guess": "unknown"})
if "--out" in sys.argv:
    open(sys.argv[sys.argv.index("--out") + 1], "w").write(out)
else:
    print(out)
"""


class Spy:
    """Wraps a real CLI runner; after the call reads what the fake model saw, and what existed while it ran."""
    def __init__(self, inner, wb):
        self.inner, self.wb, self.seen = inner, wb, []

    def __call__(self, prompt, work):
        raw_left = [str(x) for x in self.wb.glob("J*/tree")] + [str(x) for x in self.wb.glob("J*/check_*")]
        text = self.inner(prompt, work)
        d = json.loads((work / "spy_dump.json").read_text())
        d["raw_left"], d["work"] = raw_left, str(work)
        self.seen.append(d)
        return text


def t_isolation(tmp):
    """GPT review #1/#4/#5: models see only the prompt; no raw-tree path; a fresh empty workspace each; allow-listed env."""
    os.environ["ARENA_JUDGE_OPUS_MODEL"] = "fake-model-for-selftest"
    os.environ["PLANTED_HARNESS_SECRET"] = "planted-value-xyz"
    spy = tmp / "spy_model.py"
    spy.write_text(SPY_MODEL)
    wb = tmp / "iso_work"
    c, b, h = make_clone(Path(os.environ["ARENA_CLONES"]) / "iso", "v3", 2, plant=False)
    call = [sys.executable, str(spy)]
    so, sg = Spy(J.OpusCLI(prefix=call), wb), Spy(J.GptConsult(prefix=call), wb)
    try:
        r = J.judge(task=task_for("T_I"), hidden=hidden_for("T_I"), clone=c, base=b, head=h, arm="v3", gate=GATE,
                    judges=J.Judges(so, sg, Spy(J.OpusCLI(prefix=call), wb)), work_base=wb)
    finally:
        os.environ.pop("PLANTED_HARNESS_SECRET", None)
    jdir = wb / r["judge_id"]
    seen = so.seen + sg.seen
    check(r["hidden"] and r["hidden"][0]["result"] == "pass" and len(seen) == 2,
          "isolation fixture ran: hidden check passed, 2 model calls (%s)" % r["verdict"])
    forbidden = [str(jdir), os.path.realpath(jdir), str(jdir / "tree"), str(c), r["judge_id"]]
    for d in seen:
        blob = json.dumps([d["argv"], d["env"], d["prompt"], d["cwd"]])
        bad = [f for f in forbidden if f in blob]
        check(not bad, "%s: no submission dir / raw tree / clone / judge id in its argv, env, prompt or cwd (%s)"
              % (d["argv"][1] if "--prompt-file" in d["argv"] else "opus", bad))
        check(not d["raw_left"], "the raw tree and check copies were deleted before the model call (%s)" % d["raw_left"])
        check("PLANTED_HARNESS_SECRET" not in d["env"] and not any(k.startswith("ARENA_") for k in d["env"]),
              "a planted harness env var and every ARENA_* var are absent from the judge env")
        check(set(d["ls"]) <= {"prompt.md"} and Path(d["work"]).parent == J.work_root() / ".jw",
              "the call ran in a fresh private workspace holding only its own prompt (%s)" % d["ls"])
        check(not Path(d["work"]).exists(), "the workspace is deleted after the call")
    check(len({d["cwd"] for d in seen}) == 2, "each judge got its OWN workspace (no shared directory)")
    check(not (jdir / "tree").exists() and not list(jdir.glob("check_*")), "no raw tree left in the submission dir")


def t_chance(tmp):
    labels = ("a", "b", "c", "d")
    amap = {"J%d" % i: {"arm": "a" if i < 6 else "b"} for i in range(10)}
    recs = [{"judge_id": j, "votes": [{"judge": "opus", "arm_guess": "a"}]} for j in amap]
    rep = J.guess_report(recs, amap, labels)
    check(rep["per_judge"]["opus"]["binom_p"] < 0.05,
          "forced: an always-majority guesser (6/10) beats 1/4 on the binomial (p=%.3f)" % rep["per_judge"]["opus"]["binom_p"])
    check(rep["blinding"] == "not shown leaky" and abs(rep["per_judge"]["opus"]["p_value"] - 1.0) < 1e-12
          and abs(rep["pooled"]["chance"] - 0.6) < 1e-12,
          "the permutation test calls it chance (p=1, chance 0.6), not LEAKY")
    amap3 = {"J0": {"arm": "a"}, "J1": {"arm": "b"}, "J2": {"arm": "c"}}
    recs3 = [{"judge_id": j, "votes": [{"judge": "opus", "arm_guess": m["arm"]}]} for j, m in amap3.items()]
    r3 = J.guess_report(recs3, amap3, labels)
    o3 = r3["per_judge"]["opus"]
    check(o3["method"] == "exact" and abs(o3["p_high"] - 1 / 6) < 1e-12 and abs(o3["p_value"] - 1 / 3) < 1e-12,
          "hand case: 3/3 on arms a,b,c -> exact p_high = 1/3! = 1/6, two-sided 1/3")
    amap4 = {"J%d" % i: {"arm": "aabb"[i]} for i in range(4)}
    recs4 = [{"judge_id": j, "votes": [{"judge": "opus", "arm_guess": m["arm"]}]} for j, m in amap4.items()]
    r4 = J.guess_report(recs4, amap4, labels)
    o4 = r4["per_judge"]["opus"]
    check(abs(o4["p_high"] - 4 / 24) < 1e-12 and abs(o4["p_value"] - 1 / 3) < 1e-12,
          "hand case: 4/4 on a,a,b,b -> p_high = 2!2!/4! = 1/6, two-sided 1/3")
    check(rep["tests"] == 2 and abs(rep["alpha_per_test"] - 0.025) < 1e-12, "Bonferroni: 1 judge + pooled -> 0.05/2")


def t_model_unset(tmp):
    os.environ.pop("ARENA_JUDGE_OPUS_MODEL", None)
    os.environ.pop("ANTHROPIC_DEFAULT_OPUS_MODEL", None)
    clone, base, head = make_clone(Path(os.environ["ARENA_CLONES"]) / "nomodel", "trio", 2, plant=False)
    fake = tmp / "fake_model.py"
    real = J.OpusCLI.preflight
    try:
        J.OpusCLI.preflight = lambda self: None
        g = Fake(ans("accept"))
        r = J.judge(task=task_for("T_N"), hidden=None, clone=clone, base=base, head=head, arm="trio", gate=GATE,
                    judges=J.Judges(J.OpusCLI(prefix=[sys.executable, str(fake)]), g, Fake(ans("accept"))))
        check(r["verdict"] == "invalid" and g.calls == 1,
              "forced: preflight bypassed -> invalid, but only after the GPT judge was paid")
    finally:
        J.OpusCLI.preflight = real
    g = Fake(ans("accept"))
    r = J.judge(task=task_for("T_N"), hidden=None, clone=clone, base=base, head=head, arm="trio", gate=GATE,
                judges=J.Judges(J.OpusCLI(prefix=[sys.executable, str(fake)]), g, Fake(ans("accept"))))
    check(r["verdict"] == "invalid" and g.calls == 0 and "unavailable" in r.get("why", ""),
          "no Opus model -> invalid before ANY judge call (gpt calls %d)" % g.calls)


def t_bad_verdict(tmp):
    wb = tmp / "badverdict"
    (wb / "Jbad").mkdir(parents=True)
    (wb / "Jbad" / "verdict.json").write_text("{not json")
    (wb / "Jlist").mkdir()
    (wb / "Jlist" / "verdict.json").write_text('{"votes": ["x"], "ts": "2026"}')
    (wb / "Jok").mkdir()
    (wb / "Jok" / "verdict.json").write_text(json.dumps({"judge_id": "Jok", "ts": "2026-10-29T00:00:00Z",
                                                         "votes": []}))
    try:
        out = J.write_report("2026-10-29", work_base=wb)
        rep = json.loads(out.read_text())
        check(rep["unreadable"] == 2 and rep["unmapped"] == 1, "corrupt verdict.json files skipped and counted (%d)"
              % rep["unreadable"])
    except Exception as ex:                                              # noqa: BLE001
        check(False, "corrupt verdict.json crashed the report: %r" % ex)


def main():
    if not shutil.which("bwrap"):
        print("FAIL  bwrap not installed: the judge cannot run, and this test cannot prove the map is hidden")
        return 1
    tmp = Path(tempfile.mkdtemp(prefix="arena_judge_st_"))
    keys = ("ARENA_ROOT", "ARENA_CLONES", "ARENA_PRIVATE", "ARENA_JUDGE_WORK", "ARENA_JUDGE_OPUS_MODEL",
            "ANTHROPIC_DEFAULT_OPUS_MODEL", "ARENA_ARMS", "ARENA_ARM_TOKENS")
    saved = {k: os.environ.get(k) for k in keys}
    try:
        for k in ("ARENA_ARMS", "ARENA_ARM_TOKENS"):
            os.environ.pop(k, None)
        os.environ.update(ARENA_ROOT=str(tmp / "arena"), ARENA_CLONES=str(tmp / "clones"),
                          ARENA_PRIVATE=str(tmp / "private"), ARENA_JUDGE_WORK=str(tmp / "work"))
        for k in ("ARENA_ROOT", "ARENA_CLONES", "ARENA_JUDGE_WORK"):
            Path(os.environ[k]).mkdir(parents=True)
        t_neutraliser(tmp)
        t_replay(tmp)
        t_arm_map(tmp)
        t_guess(tmp)
        t_sandbox_rw(tmp)
        t_orphans(tmp)
        t_marker(tmp)
        t_gate_view(tmp)
        t_glued(tmp)
        t_exits(tmp)
        t_git_drivers(tmp)
        t_odd_names(tmp)
        t_replay_missing(tmp)
        t_glued2(tmp)
        t_isolation(tmp)
        t_chance(tmp)
        t_model_unset(tmp)
        t_bad_verdict(tmp)
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
