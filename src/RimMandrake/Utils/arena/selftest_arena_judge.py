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
Writes only under a temp dir (ARENA_ROOT / ARENA_CLONES / ARENA_PRIVATE / ARENA_JUDGE_WORK point there).
"""
import json
import os
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
    guess = (m.get(os.path.basename(os.getcwd())) or next(iter(m.values())))["arm"]
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
    blind = [{"judge_id": j, "votes": [{"judge": "opus", "arm_guess": J.ARMS[(i + 1) % 5] if i % 5 else
                                        amap[j]["arm"]}]} for i, j in enumerate(amap)]
    rl, rb = J.guess_report(leaky, amap), J.guess_report(blind, amap)
    check(rl["blinding"] == "LEAKY" and rl["pooled"]["p_value"] < 1e-10, "forced: 30/30 correct guesses -> LEAKY")
    check(rb["blinding"] == "not shown leaky" and rb["pooled"]["correct"] == 6,
          "chance-rate guesses (6/30 at q=.2) -> not shown leaky (p=%.2f)" % rb["pooled"]["p_value"])
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
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
