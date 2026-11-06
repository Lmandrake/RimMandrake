#!/usr/bin/env python3
"""selftest_relentless_proof_gate_mend.py: PROOF_GATE_FIX_CONDUCTOR_MEND_FRAMED.

proof_gate read every commit in held..candidate whose message names the item as the proof-only worker's, so a Conductor
mend between runs (MODCHECK_DONOR_ENVIRONMENTS_1: 2890737c6a touched relentless_game.py after held 64e953e516) ended
every later proof-only finish proof_rework. Now a commit counts only when authored inside one of the item's own runs
since the hold (Effects.worker_changed; item_run_windows).
1. Sanity: changed() on the real repo DOES see the mend (the instrument can see what is filtered out).
2. The MODCHECK shape: mend authored before the run, the worker's proof commit inside it -> not proof_rework.
3. The same mend re-committed (publish rebase) inside the window keeps its author time: still not counted.
4. A code commit authored inside the window is still proof_rework.
5. No run recorded since the hold -> every naming commit counts, as before (the mend is rework again).

Runs on a throwaway git repo and Store under TMPDIR; no ledger, clone or game is touched.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless as R  # noqa: E402

FAILS = []
RULES = R.rules()
ITEM = "MEND_ITEM_X"
T0 = 1793797213        # the hold
T_MEND = T0 + 50000    # Conductor mend, between runs
T_RUN = T0 + 60000     # gen 12 starts
T_W = T_RUN + 300      # its proof commit
T_END = T_RUN + 600


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def git(cwd, *a, at=None, cat=None):
    env = dict(os.environ)
    if at is not None:
        env["GIT_AUTHOR_DATE"] = "@%d +0000" % at
        env["GIT_COMMITTER_DATE"] = "@%d +0000" % (cat if cat is not None else at)
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *a],
                          cwd=cwd, check=True, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                          env=env).stdout.strip()


def commit(repo, path, msg, at, cat=None):
    full = os.path.join(repo, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "a") as f:
        f.write("%s\n" % msg)
    git(repo, "add", path)
    git(repo, "commit", "-q", "-m", msg, at=at, cat=cat)
    return git(repo, "rev-parse", "HEAD")


def world(base, runs, mend_cat=None, code_in_window=False):
    repo = os.path.join(base, "books")
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "main")
    held = commit(repo, "src/x/code.py", "%s: the build" % ITEM, T0 - 10)
    commit(repo, "src/RimMandrake/rimflow/relentless_game.py", "%s: Conductor mend" % ITEM, T_MEND, cat=mend_cat)
    if code_in_window:
        commit(repo, "src/x/code.py", "%s: worker moves code" % ITEM, T_W - 10)
    sha = commit(repo, "src/x/selftest_x.py", "%s: proof strengthened" % ITEM, T_W)
    store = R.Store(os.path.join(base, "store"))
    os.makedirs(store.item_dir(ITEM), exist_ok=True)
    store.attempt(ITEM, {"at": R.iso(T0), "gen": 10, "end": "proof_owed", "sha": held})
    for g, s, e in runs:
        store.attempt(ITEM, {"at": R.iso(s), "gen": g, "start": "rm-relentless-work-x-g%d" % g})
        store.attempt(ITEM, {"at": R.iso(e), "gen": g, "end": "finish", "sha": sha})
    fx = types.SimpleNamespace(store=store, books=repo, r={})
    for n in ("git", "changed", "worker_changed", "existed"):
        setattr(fx, n, types.MethodType(getattr(R.Effects, n), fx))
    k0 = {"proof": "python3 src/x/selftest_x.py", "live": None, "by_gen": 12, "why": "w"}
    st = {"item": ITEM, "contract": dict(k0), "proof_only": {"sha": held, "at": T0 + 0.5, "contract": dict(k0)}}
    return fx, st, held, sha


def case(name, runs, **kw):
    base = tempfile.mkdtemp(prefix="pgmend_")
    try:
        fx, st, held, sha = world(base, runs, **kw)
        return fx.changed(held, sha, ITEM), fx.worker_changed(held, sha, ITEM, T0 + 0.5), \
            R.proof_gate(fx, RULES, st, {"sha": sha})
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main():
    gen12 = [(12, T_RUN, T_END)]
    allc, mine, gate = case("modcheck", gen12)
    ok("src/RimMandrake/rimflow/relentless_game.py" in allc, "1 sanity: changed() sees the mend: %s" % allc)
    ok(mine == ["src/x/selftest_x.py"], "2 worker_changed keeps only the run's own commit: %s" % mine)
    ok(gate == (None, None), "2 the MODCHECK shape is not proof_rework: %s" % (gate,))
    _, mine, gate = case("rebased", gen12, mend_cat=T_W - 5)
    ok(gate == (None, None) and "src/RimMandrake/rimflow/relentless_game.py" not in mine,
       "3 a mend re-committed inside the window keeps its author time: %s %s" % (mine, gate))
    _, mine, gate = case("code", gen12, code_in_window=True)
    ok(gate[0] == "proof_rework" and "src/x/code.py" in gate[1], "4 code authored inside the run is rework: %s" % (gate,))
    ok("relentless_game.py" not in gate[1], "4 ... and the mend is not named in it: %s" % gate[1])
    _, mine, gate = case("norun", [])
    ok(gate[0] == "proof_rework" and "relentless_game.py" in gate[1],
       "5 no run since the hold: every naming commit counts, as before: %s" % (gate,))
    ok(R.item_run_windows([{"at": R.iso(T_RUN), "gen": 3, "start": "u"}], T0) == [(T_RUN, None)],
       "a run still going has an open window")
    ok(R.item_run_windows([{"at": R.iso(T0 - 5), "gen": 3, "start": "u"}], T0) is None,
       "a run before the hold is not a proof-only run")
    ok(R.item_run_windows([], None) is None, "no hold time: unreadable")
    print("FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
