#!/usr/bin/env python3
"""selftest_live_companion_gate.py -- LIVEROUND_COMPANION_DEPLOY_OLD_DLL_BLAMED: a live proof that drives JawaBench runs
only on a game folder whose companion DLL was built from the build's sources, and the staging deploys it.

BRIDGE_STALL_DIAGNOSTIC_1's companion-only fix e26a661423 read A1 FAIL twice on the hand-deployed d62e3e51 DLL
(companion_identity STALE): the round deployed mod folders only. What must hold, each red under its mutant:
  * `live-companion: JawaBench` is read (wrapped, commented); any other name is refused;
  * a build touching a companion compile input owes the companion without the line; a README there, or a mod, does not;
  * owed and STALE / UNSTAMPED / MISSING -> NOT_ADMITTED "not deployed" (the game phase restages; NOT_ADMITTED since
    LIVELANE_BUILD_PREFLIGHT_REFUSES_UNRUNNABLE ab77ccbdd6), game-stamped, no bridge;
  * owed and FRESH -> the proof runs; FRESH but written after the game started -> "not deployed";
  * an unreadable identity -> NOT_ADMITTED that is not "not deployed" (no restage) and no bridge;
  * not owed -> the companion is never read;
  * the real Fx reads BridgeTools/JawaBench beside the Mods folder and judges it against the build's sources;
  * the round passes companion=True for a file with the line;
  * the stage plan carries the owed shas, the prompt says so, the stager builds in the shutdown window, and refuses
    before anything is written when its clone's build would not hold every owed sha.
COMPANION_DEPLOY_LIVE_ROUND_FORGETS (runs.jsonl 2026-11-06: six STALE rows, each item wanting its own built sha's exact
hash, 4 of 5 of them ancestors of the game's clean a9e5d1f6a3 build; FW_PROOF_TOOLS_HARDEN_READ_GAPS rode
HOSE_SITE_FIX_TERRAIN_WONT_READ_BACK's load, and ./sync for riders moves the stager's clone off the lead's hash):
  * cover: a DLL that is a clean build (embedded == srchash at its stamp) of a descendant of the built sha reads FRESH
    (covered_by); a sibling, an unknown stamp, a dirty build, or cover off read STALE; the real Fx covers;
  * the game phase owes the companion for every rider of the load, not the lead alone (game_companion_owed);
  * the stager accepts a clean, published HEAD holding every owed sha and refuses a dirty tree, an unpublished HEAD,
    or a HEAD lacking one.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "bridgetools"))
import relentless_live as L     # noqa: E402
import relentless_live_round as R     # noqa: E402
import relentless_game as G     # noqa: E402
import relentless_stage as S    # noqa: E402
import companion_identity as CI     # noqa: E402
import selftest_relentless_live as TL   # noqa: E402
import selftest_relentless_stage as TS  # noqa: E402

FAILS = []
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CS = L.COMPANION_SRC + "JawaBenchStallTools.cs"


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append((name, detail))


class CompFx(TL.FakeFx):
    def __init__(self, comp=None, **kw):
        TL.FakeFx.__init__(self, **kw)
        self.comp = comp

    def companion(self, sha):
        self.calls.append(("companion", sha))
        return dict(self.comp)


def v(state, mtime=1500.0):
    return {"state": state, "embedded": "a" * 64 if state in ("FRESH", "STALE") else None,
            "want": None if state == "UNMEASURED" else "a" * 64 if state == "FRESH" else "b" * 64,
            "dll": "/g/BridgeTools/JawaBench/JawaBench.BridgeTools.dll", "build_commit": None, "mtime": mtime}


def go(fx, companion=False):
    root = tempfile.mkdtemp(prefix="rl_comp_")
    return L.run(fx, root, "ROT_X", "A2", "python3 x.py", "--mod TheRot", {}, now=1_800_000_000, companion=companion)


def t_line():
    check("line: bare", R.companion_line("live-companion: JawaBench\n") is True)
    check("line: wrapped and commented", R.companion_line("- `live-companion: JawaBench` # stall tools") is True)
    check("line: absent", R.companion_line("live-mods: Graffiti\nlive-proof A1: echo x") is False)
    try:
        R.companion_line("live-companion: Oracle")
        check("line: another name is refused", False)
    except ValueError:
        check("line: another name is refused", True)


def t_touched():
    check("touched: a companion .cs owes it", L.companion_touched(TL.FakeFx(touched=[CS]), TL.SHA) is True)
    check("touched: a README in the folder does not",
          L.companion_touched(TL.FakeFx(touched=[L.COMPANION_SRC + "README.md"]), TL.SHA) is False)
    check("touched: a mod build does not", L.companion_touched(TL.FakeFx(), TL.SHA) is False)
    check("touched: bin/ is no compile input",
          L.companion_touched(TL.FakeFx(touched=[L.COMPANION_SRC + "bin/x.cs"]), TL.SHA) is False)


def t_gate():
    for st in ("STALE", "UNSTAMPED", "MISSING"):
        fx = CompFx(v(st))
        row = go(fx, companion=True)
        check("gate: %s is not deployed, no bridge" % st, row["outcome"] == "NOT_ADMITTED"
              and row["why"].startswith(L.UNDEPLOYED[0]) and "take" not in fx.verbs() and "proof" not in fx.verbs()
              and row.get("game") is not None and row["companion"]["state"] == st, row)
    fx = CompFx(v("FRESH"))
    row = go(fx, companion=True)
    check("gate: FRESH runs the proof", row["outcome"] == "PASS" and "proof" in fx.verbs()
          and row["companion"]["state"] == "FRESH", (row, fx.calls))
    fx = CompFx(v("FRESH", mtime=2500.0))
    row = go(fx, companion=True)
    check("gate: FRESH but deployed after the game started is not deployed",
          row["outcome"] == "NOT_ADMITTED" and row["why"].startswith(L.UNDEPLOYED[0]) and "take" not in fx.verbs(), row)
    fx = CompFx(v("UNMEASURED"))
    row = go(fx, companion=True)
    check("gate: an unreadable identity is no restage and no bridge",
          row["outcome"] == "NOT_ADMITTED" and not row["why"].startswith(L.UNDEPLOYED) and "take" not in fx.verbs()
          and "identity could not be read" in row["why"], row)
    fx = CompFx(v("STALE"))
    row = go(fx, companion=False)
    check("gate: not owed, never read", row["outcome"] == "PASS" and "companion" not in fx.verbs(), fx.calls)
    fx = CompFx(v("STALE"), touched=TL.TOUCHED + [CS])
    row = go(fx, companion=False)
    check("gate: a build touching the companion owes it without the line",
          row["outcome"] == "NOT_ADMITTED" and row["why"].startswith(L.UNDEPLOYED[0]), row)
    fx = TL.FakeFx()
    row = go(fx, companion=True)
    check("gate: an Fx with no companion reader measures nothing", row["outcome"] == "NOT_ADMITTED"
          and "take" not in fx.verbs(), row)


def t_real_fx():
    want = CI.srchash_at(REPO, "HEAD")
    if want is None:
        check("real fx: HEAD's companion sources hash (sanity probe)", False, "srchash_at gave None")
        return
    with tempfile.TemporaryDirectory() as d:
        mods = os.path.join(d, "RimWorld", "Mods")
        os.makedirs(mods)
        fx = L.Fx(books=REPO, mods_dir=mods)
        check("real fx: no DLL reads MISSING", fx.companion("HEAD")["state"] == "MISSING")
        dll = os.path.join(d, "RimWorld", "BridgeTools", "JawaBench", CI.DLL_NAME)
        CI.write_fixture(dll, want)
        got = fx.companion("HEAD")
        check("real fx: the build's hash reads FRESH, with its mtime",
              got["state"] == "FRESH" and abs(got["mtime"] - os.path.getmtime(dll)) < 1, got)
        CI.write_fixture(dll, "0" * 64)
        check("real fx: another hash reads STALE", fx.companion("HEAD")["state"] == "STALE")


def t_round():
    import selftest_relentless_live_round as TR
    seen = []

    def run(fx, root, item_id, cid, proof, deploy, r, now=None, needs=(), site=None, trees=(), **kw):
        seen.append((item_id, kw.get("companion")))
        return {"item": item_id, "criterion": cid, "outcome": "PASS", "why": "x", "sha": "abc123"}

    class Fx(TR.FakeFx):
        def proofs(self, i):
            return TR.PROSE + ("\nlive-companion: JawaBench\n" if i == "EG_A" else "")
    with tempfile.TemporaryDirectory() as root:
        R.run_round(Fx(), root, {"live": {"round_max": 2}}, now=1_800_000_000, run=run)
    check("round: the line passes companion=True, its absence nothing",
          dict(seen).get("EG_A") is True and dict(seen).get("EG_B") is None, seen)


def t_stage():
    st = {"item": "I0", "gen": 3, "game": {"full": None}}
    p = G.stage_plan(st, {"stage_max_s": 3600}, "abc", [], ["Armoury"], [], None, None, companion=["c" * 40, "e" * 40])
    check("stage plan: carries the owed shas", p.get("companion") == ["c" * 40, "e" * 40], p)
    p = G.stage_plan(st, {"stage_max_s": 3600}, "abc", [], ["Armoury"], [], None, None)
    check("stage plan: none owed, no key", "companion" not in p, p)
    txt = G.stage_prompt(st, {"seat": "BENCH"}, "abc", companion=["c" * 40, "e" * 40])
    check("stage prompt: names build.py --gm --apply and every owed sha",
          "build.py --gm --apply" in txt and "c" * 12 in txt and "e" * 12 in txt)

    class Ops(TS.FakeOps):
        def __init__(self, have, **kw):
            TS.FakeOps.__init__(self, **kw)
            self.have = have

        def companion_covers(self, shas):
            self.calls.append(("covers",))
            return None if self.have == "c" * 64 else "HEAD does not hold build %s" % shas[0][:12]

        def companion_build(self):
            self.calls.append(("companion_build",))
            return 0, "deployed."
    plan = dict(TS.PLAN, companion=["c" * 40], remedy_cmds=[])
    ops = Ops("c" * 64)
    verdict, text = S.run(plan, ops)
    seq = TS.tags(ops)
    check("stager: builds the companion in the shutdown window", verdict == "ready" and "companion_build" in seq
          and seq.index("kill") < seq.index("companion_build") < seq.index("launch") and "companion JawaBench" in text
          and seq.index("covers") < seq.index("kill"),
          (seq, text))
    ops = Ops("d" * 64)
    verdict, text = S.run(plan, ops)
    seq = TS.tags(ops)
    check("stager: a clone whose build would not hold the owed sha stops before anything is written",
          verdict == "snag" and "c" * 12 in text and "kill" not in seq and "apply" not in seq and "companion_build" not in seq, (seq, text))
    ops = Ops("c" * 64)
    ops.companion_build = lambda: (1, "REFUSING TO DEPLOY")
    verdict, text = S.run(plan, ops)
    check("stager: a failed companion build snags", verdict == "snag" and "build.py" in text, text)
    ops = Ops("c" * 64)
    verdict, text = S.run(dict(plan, companion="c" * 64), ops)
    seq = TS.tags(ops)
    check("stager: a plan from older code (a source hash) stops before anything is written",
          verdict == "snag" and "older code" in text and "kill" not in seq and "companion_build" not in seq, (seq, text))
    ops = TS.FakeOps()
    verdict, _ = S.run(dict(TS.PLAN, remedy_cmds=[]), ops)
    check("stager: no companion owed, no build", verdict == "ready" and "companion_build" not in TS.tags(ops))


def git(d, *a):
    r = subprocess.run(["git", "-C", d] + list(a), capture_output=True, text=True, timeout=60)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr[-300:]))
    return r.stdout.strip()


def repo_abc(d):
    """A git repo: A (x.cs v1) <- B (x.cs v2) on main, A <- C (x.cs v3) on a side branch. -> {name: sha}."""
    git(d, "init", "-q", "-b", "main")
    git(d, "config", "user.email", "t@t")
    git(d, "config", "user.name", "t")
    src = os.path.join(d, *CI.SRC_REL.split("/"))
    os.makedirs(src)
    shas = {}
    for name, body, branch in (("A", "v1", None), ("B", "v2", None), ("C", "v3", "side")):
        if branch:
            git(d, "checkout", "-q", "-b", branch, shas["A"])
        with open(os.path.join(src, "x.cs"), "w") as f:
            f.write("class X { /* %s */ }\n" % body)
        git(d, "add", "-A")
        git(d, "commit", "-q", "-m", name)
        shas[name] = git(d, "rev-parse", "HEAD")
    git(d, "checkout", "-q", "main")
    return shas


def stamped(dll, src_hash, commit):
    """A fixture DLL carrying a source hash and the SDK's "+<commit>" build stamp."""
    CI.write_fixture(dll, src_hash)
    with open(dll, "ab") as f:
        f.write(("1.0.0+%s" % commit).encode())
    return dll


def t_cover():
    with tempfile.TemporaryDirectory() as d:
        s = repo_abc(d)
        h = {k: CI.srchash_at(d, v) for k, v in s.items()}
        check("cover: three distinct companion hashes (sanity probe)", len(set(h.values())) == 3 and None not in h.values(), h)
        dll = stamped(os.path.join(d, "g", CI.DLL_NAME), h["B"], s["B"])
        check("cover: the fixture's stamp reads back (sanity probe)", CI.verdict(dll, d, s["B"])["build_commit"] == s["B"])
        got = CI.verdict(dll, d, s["A"], cover=True)
        check("cover: a clean build of a descendant holds the older build", got["state"] == "FRESH"
              and got.get("covered_by") == s["B"] and "descendant" in CI.describe(got), got)
        check("cover: off, it stays STALE (the exact rule)", CI.verdict(dll, d, s["A"])["state"] == "STALE")
        check("cover: an exact match needs no cover", CI.verdict(dll, d, s["B"], cover=True).get("covered_by") is None)
        check("cover: a sibling's build does not hold it",
              CI.verdict(stamped(dll, h["C"], s["C"]), d, s["B"], cover=True)["state"] == "STALE")
        check("cover: a dirty build (hash not its stamp's) does not",
              CI.verdict(stamped(dll, h["C"], s["B"]), d, s["A"], cover=True)["state"] == "STALE")
        check("cover: a stamp git cannot see does not",
              CI.verdict(stamped(dll, h["B"], "f" * 40), d, s["A"], cover=True)["state"] == "STALE")
        CI.write_fixture(dll, h["B"])
        check("cover: no stamp, no cover", CI.verdict(dll, d, s["A"], cover=True)["state"] == "STALE")
        mods = os.path.join(d, "RimWorld", "Mods")
        os.makedirs(mods)
        stamped(os.path.join(d, "RimWorld", "BridgeTools", "JawaBench", CI.DLL_NAME), h["B"], s["B"])
        got = L.Fx(books=d, mods_dir=mods).companion(s["A"])
        check("cover: the real Fx reads a covering build FRESH", got["state"] == "FRESH" and got.get("covered_by"), got)
        books = os.path.join(d, "books")
        git(d, "clone", "-q", d, books)
        src = os.path.join(d, *CI.SRC_REL.split("/"), "x.cs")
        with open(src, "w") as f:
            f.write("class X { /* v4 */ }\n")
        git(d, "commit", "-q", "-am", "E")
        e = git(d, "rev-parse", "HEAD")
        stamped(os.path.join(d, "RimWorld", "BridgeTools", "JawaBench", CI.DLL_NAME), CI.srchash_at(d, e), e)
        check("cover: the books clone lacks the new stamp (sanity probe)", not CI.known(books, e))
        got = L.Fx(books=books, mods_dir=mods).companion(s["A"])
        check("cover: a stamp the books clone has not fetched is fetched, then held",
              got["state"] == "FRESH" and got.get("covered_by") == e, got)
        fx = CompFx(dict(v("FRESH"), covered_by=s["B"]))
        row = go(fx, companion=True)
        check("cover: the run row names the covering build",
              row["outcome"] == "PASS" and row["companion"].get("covered_by") == s["B"][:12], row)


def t_batch():
    class Fx(object):
        def __init__(self, owes):
            self.owes = owes

        def game_companion(self, item, sha):
            return sha if item in self.owes else None
    b = [("LEAD", "a" * 40), ("RIDER", "b" * 40), ("RIDER2", "a" * 40), ("CLEAN", "c" * 40)]
    check("batch: a rider owing the companion is owed though the lead is not",
          G.game_companion_owed(Fx({"RIDER"}), b) == ["b" * 40])
    check("batch: every owing sha once, in order",
          G.game_companion_owed(Fx({"LEAD", "RIDER", "RIDER2"}), b) == ["a" * 40, "b" * 40])
    check("batch: none owed is None", G.game_companion_owed(Fx(set()), b) is None)
    check("batch: an fx with no reader is None", G.game_companion_owed(object(), b) is None)
    gf = G.GameFx.__new__(G.GameFx)

    class RF(object):
        def touched(self, sha):
            return [CS]

        def companion(self, sha):
            return self.v
    rf = RF()
    gf._round_fx = lambda: rf
    gf._mods_text = lambda item, sha: ""
    rf.v = {"state": "STALE", "want": "9" * 64}
    check("batch: GameFx.game_companion names the built sha, not a source hash",
          gf.game_companion("I", "a" * 40) == "a" * 40)
    rf.v = {"state": "FRESH", "want": "9" * 64, "covered_by": "b" * 40}
    check("batch: a covered build owes nothing", gf.game_companion("I", "a" * 40) is None)


def t_stager_covers():
    with tempfile.TemporaryDirectory() as d:
        s = repo_abc(d)
        git(d, "update-ref", "refs/remotes/origin/main", s["B"])
        ops = S.Ops.__new__(S.Ops)
        ops.cwd = d
        check("stager covers: a clean published HEAD holding both builds", ops.companion_covers([s["A"], s["B"]]) is None,
              ops.companion_covers([s["A"], s["B"]]))
        why = ops.companion_covers([s["C"]])
        check("stager covers: a HEAD lacking a build is refused", why and "does not hold" in why and s["C"][:12] in why, why)
        src = os.path.join(d, *CI.SRC_REL.split("/"), "x.cs")
        with open(src) as f:
            body = f.read()
        with open(src, "a") as f:
            f.write("// dirty\n")
        why = ops.companion_covers([s["A"]])
        check("stager covers: uncommitted companion work is refused", why and "uncommitted" in why, why)
        with open(src, "w") as f:
            f.write(body)
        git(d, "commit", "-q", "--allow-empty", "-m", "D")
        why = ops.companion_covers([s["A"]])
        check("stager covers: an unpublished HEAD is refused", why and "origin/main" in why, why)
    with tempfile.TemporaryDirectory() as d:     # a lead alone never ./syncs: its stale origin/main ref is fetched
        up = os.path.join(d, "up")
        os.makedirs(up)
        s = repo_abc(up)
        clone = os.path.join(d, "clone")
        git(d, "clone", "-q", "-b", "main", up, clone)
        git(clone, "update-ref", "refs/remotes/origin/main", s["A"])
        ops = S.Ops.__new__(S.Ops)
        ops.cwd = clone
        why = ops.companion_covers([s["B"]])
        check("stager covers: a published HEAD behind a stale origin/main ref is fetched, then accepted", why is None, why)


def main():
    for t in (t_line, t_touched, t_gate, t_real_fx, t_round, t_stage, t_cover, t_batch, t_stager_covers):
        try:
            t()
        except Exception as e:      # noqa: BLE001  a crash is a red, named
            import traceback
            traceback.print_exc()
            FAILS.append((t.__name__, "crashed: %r" % e))
    if FAILS:
        print(json.dumps(FAILS, default=str)[:2000])
    print("selftest_live_companion_gate:", "FAIL" if FAILS else "OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
