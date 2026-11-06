#!/usr/bin/env python3
"""ENGINE_REVIEW_FIX_LEFTOVERS_STILL_WARM: one case per finding Codex left open on cd905b46d6
(infrastructure/state/lessons/20261105T082718Z-BENCH-review-cd905b-leftovers.md).

relentless_game: G1 finals_waiting ranks expedited finals as expedited_ahead does (no deadlock). G2 (stage_idle_s
counted load time) and G3 (riders' remedies) were fixed by 0a2ec71ec9; their cases live in
selftest_relentless_codex_keeps.py, which this file runs too.
relentless_live: L1 an off mod the build does not ship is no gap; L2 a drift plan (exit 1) keeps its game; L3 a take
that raises still releases and leaves a row; L4 a fileless build still holds the game's identity; L5 a launch that
raised is INFRA, never a FAIL verdict; L6 a log holding a violation is never rerun under python.exe; L7 a proof that
times out on two games reaches the defect cap.
modset_builder: M1 a failed tasklist reads live; M2 one ModsConfig writer at a time; M3 restores copy atomically."""
import json
import os
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless_game as G               # noqa: E402
import relentless_live as L               # noqa: E402
import selftest_relentless_live as B      # noqa: E402  FakeFx, go, PLAN, item
import modset_builder as M                # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    if not cond:
        FAILS.append((name, detail))


# ------------------------------------------------------------------ relentless_game

def t_g1_expedited_finals_rank_like_expedited_ahead():
    st = lambda iid, since, level, at: {"item": iid, "status": G.GAME, "game": {"phase": "final", "final_since": since},
                                        "expedite": {"level": level, "at": at}}
    states = [st("OLD_EXPEDITED", 100, "expedited", 50), st("NEW_INTERRUPT", 900, "interrupt", 800),
              {"item": "PLAIN", "status": G.GAME, "game": {"phase": "final", "final_since": 10}}]
    q = [i for _, i in G.finals_waiting(states)]
    check("G1: the interrupt heads the finals queue", q == ["NEW_INTERRUPT", "OLD_EXPEDITED", "PLAIN"], q)
    check("G1: the head is not held behind anyone", G.expedited_ahead(states, q[0]) is None,
          G.expedited_ahead(states, q[0]))
    check("G1 sanity: the older one IS held behind the interrupt",
          G.expedited_ahead(states, "OLD_EXPEDITED") == "NEW_INTERRUPT")


# ------------------------------------------------------------------ relentless_live

OFF_LINE = "Pyrelands        mandrake.rm.pyrelands          NOT DEPLOYED\n"
DRIFT_TAIL = "\nDrift found. Re-run with --apply to deploy.\n"


def t_l1_unrelated_off_mod_is_no_gap():
    plan = B.PLAN.replace(DRIFT_TAIL, "\n" + OFF_LINE + DRIFT_TAIL)
    check("L1 fixture keeps the drift tail", plan.rstrip().endswith(L.PLAN_DRIFT_TAIL))
    files = [("TheRot", "Defs/Fauna/RM_Chittik.xml")]
    why = L.deploy_gap(files, 1, plan)
    check("L1: an off mod the build does not ship is not its gap", why is None, why)
    why = L.deploy_gap(files + [("Pyrelands", "Defs/A.xml")], 1, plan)
    check("L1 sanity: the shipped off mod still is", why and "Pyrelands" in why and "NOT DEPLOYED" in why, why)


def t_l2_drift_plan_keeps_its_game():
    check("L2: plan_failed reads", L.plan_failed(1, "Traceback") and L.plan_failed(None, "took over")
          and not L.plan_failed(1, B.PLAN) and not L.plan_failed(0, ""))
    plan = B.PLAN.replace(DRIFT_TAIL, "\n" + OFF_LINE + DRIFT_TAIL)
    row = B.go(B.FakeFx(plan=(1, plan), touched=["src/RimMandrake/Pyrelands/Defs/A.xml"]))
    check("L2: an undeployed row on a drift plan names its game", row["why"].startswith(L.UNDEPLOYED) and row.get("game"),
          row)
    row = B.go(B.FakeFx(plan=(1, "Traceback")))
    check("L2 sanity: a failed plan has no game", not row.get("game"), row)


class TakeRaises(B.FakeFx):
    def rimflow(self, *args, timeout=120):
        if args[:2] == ("bridge", "take"):
            self.calls.append(("rimflow",) + args)
            raise subprocess.TimeoutExpired("rimflow bridge take", 120)
        return B.FakeFx.rimflow(self, *args, timeout=timeout)


def t_l3_take_that_raises_releases():
    fx = TakeRaises()
    try:
        row = B.go(fx)
    except Exception as e:      # noqa: BLE001
        check("L3: a raising take leaves a row", False, repr(e))
        return
    check("L3: a raising take is not admitted and runs no proof", row["outcome"] == L.NOT_ADMITTED
          and "proof" not in fx.verbs(), row)
    check("L3: it gives the bridge back", "release" in fx.verbs(), fx.verbs())


FILELESS = ["src/RimMandrake/TheRot/validation.py"]


def t_l4_fileless_build_holds_the_game():
    fx = B.FakeFx(touched=FILELESS, start_after_take=3000.0)
    row = B.go(fx)
    check("L4: a fileless build whose game restarted at the take runs no proof", "proof" not in fx.verbs()
          and row["outcome"] == "UNMEASURED" and "changed" in row["why"], (row, fx.verbs()))
    fx = B.FakeFx(touched=FILELESS)
    row = B.go(fx)
    check("L4 sanity: the same build on a steady game runs and passes", "proof" in fx.verbs()
          and row["outcome"] == "PASS", (row, fx.verbs()))


def t_l5_launch_that_raised_is_infra():
    row = B.go(B.FakeFx(proof_raises=True))
    check("L5: a launch that raised is no FAIL verdict", row.get("verdict") == "INFRA" and "proof_exit" not in row
          and row["outcome"] == "UNMEASURED", row)
    row = B.go(B.FakeFx(proof=1))
    check("L5 sanity: a proof exit 1 still is", row.get("verdict") == "FAIL", row)


class WslFx(B.FakeFx):
    def run_proof(self, proof, log, timeout):
        self.calls.append(("proof", proof))
        with open(log, "w", encoding="utf-8") as f:
            f.write("$ %s\n%s\n" % (proof, L.WSL_BRIDGE[0]))
        return 1


def t_l6_violation_is_never_rerun():
    keep = L.violated
    try:
        for held, want in ((True, 1), (False, 2)):
            L.violated = lambda log, crit, held=held: held
            fx = WslFx()
            B.go(fx, proof="python3 src/RimMandrake/Utils/some_proof.py")
            n = sum(1 for c in fx.calls if c[0] == "proof")
            check("L6: violation=%s -> %d proof run(s)" % (held, want), n == want, fx.calls)
    finally:
        L.violated = keep
    d = tempfile.mkdtemp(prefix="rl_viol_")
    check("L6: a missing log holds no violation", L.violated(os.path.join(d, "none.log"), "A2") is False)


def t_l7_timeout_on_two_games_is_a_defect():
    root = tempfile.mkdtemp(prefix="rl_timeout_")
    proof = "python3 live_def_check.py --has ThingDef/RM_Chittik=CompProperties_WoundLink"
    r1 = L.run(B.FakeFx(proof=None, started=2000.0), root, "ROT_X", "A2", proof, "--compose biomes", {},
               now=1_800_000_000)
    r2 = L.run(B.FakeFx(proof=None, started=5000.0), root, "ROT_X", "A2", proof, "--compose biomes", {},
               now=1_800_000_100)
    check("L7 sanity: the first timeout is a plain UNMEASURED", r1["outcome"] == "UNMEASURED"
          and not r1.get("defect"), r1)
    check("L7: the same timeout on a second game is a defect", r2.get("defect") and r2["why"].startswith(L.DEFECT), r2)


# ------------------------------------------------------------------ modset_builder

def t_m1_failed_tasklist_reads_live():
    keep, keep_log = M.subprocess.run, getattr(M, "PLAYERLOG", None)
    M.PLAYERLOG = os.path.join(tempfile.mkdtemp(prefix="modset_nolog_"), "Player.log")   # a quiet/missing log is no answer
    cases = [(types.SimpleNamespace(returncode=1, stdout="", stderr="interop down"), True),
             (types.SimpleNamespace(returncode=0, stdout="RimWorldWin64.exe  123 Console", stderr=""), True),
             (types.SimpleNamespace(returncode=0, stdout="INFO: No tasks are running", stderr=""), False),
             (OSError("no tasklist.exe"), True)]
    try:
        for ans, want in cases:
            def fake(*a, ans=ans, **k):
                if isinstance(ans, Exception):
                    raise ans
                return ans
            M.subprocess.run = fake
            got = M.game_running()
            check("M1: %r -> live=%s" % (ans, want), got is want, got)
    finally:
        M.subprocess.run = keep
        if keep_log is not None:
            M.PLAYERLOG = keep_log


def t_m2_one_writer_at_a_time():
    path = os.path.join(tempfile.mkdtemp(prefix="modset_lock_"), "x.lock")
    with M.config_lock(path):
        try:
            with M.config_lock(path, wait_s=0.6):
                check("M2: a second writer waits out and is refused", False)
        except M.RestoreRefused as e:
            check("M2: the refusal names the lock", path in str(e), str(e))
    with M.config_lock(path, wait_s=0.6):
        pass        # released: free again
    src = open(M.__file__, encoding="utf-8").read()
    check("M2: apply and every restore write under the lock", src.count("with config_lock():") >= 3)


def t_m3_restore_copies_atomically():
    d = tempfile.mkdtemp(prefix="modset_atomic_")
    src, dst = os.path.join(d, "before.xml"), os.path.join(d, "ModsConfig.xml")
    open(src, "w").write("<before/>")
    open(dst, "w").write("<tier/>")
    keep = M.shutil.copy2

    def half(a, b):
        open(b, "w").write("<bef")
        raise OSError("killed mid-copy")
    M.shutil.copy2 = half
    try:
        M.atomic_copy(src, dst)
    except OSError:
        pass
    finally:
        M.shutil.copy2 = keep
    check("M3: a copy killed mid-way leaves the live list whole", open(dst).read() == "<tier/>", open(dst).read())
    M.atomic_copy(src, dst)
    check("M3: a whole copy lands", open(dst).read() == "<before/>" and not os.path.exists(dst + ".modset-tmp"))


def t_m4_tier_md5_is_stamped_before_the_replace():
    d = tempfile.mkdtemp(prefix="modset_write_")
    src = os.path.join(d, "v.xml")
    open(src, "w").write('<?xml version="1.0" encoding="utf-8"?><ModsConfigData><version>1.6</version>'
                         '<activeMods><li>old</li></activeMods></ModsConfigData>')
    keep = M.CONFIG
    M.CONFIG = os.path.join(d, "ModsConfig.xml")
    seen = []
    try:
        M.write_config(["ludeon.rimworld", M.ZOOM], src, before_replace=lambda h: seen.append((h, os.path.exists(M.CONFIG))))
        check("M4: before_replace ran before the live file existed, with the new file's md5",
              seen and seen[0][1] is False and seen[0][0] == M._md5(M.CONFIG), (seen, M._md5(M.CONFIG)))
    finally:
        M.CONFIG = keep


def t_m5_cameraplus_tier_never_gets_the_rival_zoom():
    names = ("tier_def", "close_over", "order", "tier_guard")
    keep = {n: getattr(M, n) for n in names}
    try:
        M.tier_def = lambda n, i: {"want": ["brrainz.cameraplus"], "dlc": False}
        M.close_over = lambda w, i: (list(w), [])
        M.order = lambda p, i: p
        M.tier_guard = lambda t, o: []
        got = M.resolve_tier("mods__x", {M.ZOOM: {}})[0]
        check("M5: Camera+ asked -> no %s" % M.ZOOM, M.ZOOM not in got and "brrainz.cameraplus" in got, got)
        M.tier_def = lambda n, i: {"want": ["x.y"], "dlc": False}
        check("M5 sanity: other tiers still get the zoom mod", M.ZOOM in M.resolve_tier("mods__y", {M.ZOOM: {}})[0])
    finally:
        for n, f in keep.items():
            setattr(M, n, f)


def t_g2_g3_keeps_still_green():
    p = subprocess.run([sys.executable, os.path.join(HERE, "selftest_relentless_codex_keeps.py")],
                       capture_output=True, text=True, timeout=300)
    check("G2/G3: selftest_relentless_codex_keeps (up_seen idle clock, riders' remedies) passes", p.returncode == 0,
          (p.stdout + p.stderr)[-600:])


def main():
    for t in (t_g1_expedited_finals_rank_like_expedited_ahead, t_l1_unrelated_off_mod_is_no_gap,
              t_l2_drift_plan_keeps_its_game, t_l3_take_that_raises_releases, t_l4_fileless_build_holds_the_game,
              t_l5_launch_that_raised_is_infra, t_l6_violation_is_never_rerun, t_l7_timeout_on_two_games_is_a_defect,
              t_m1_failed_tasklist_reads_live, t_m2_one_writer_at_a_time, t_m3_restore_copies_atomically,
              t_m4_tier_md5_is_stamped_before_the_replace, t_m5_cameraplus_tier_never_gets_the_rival_zoom,
              t_g2_g3_keeps_still_green):
        try:
            t()
        except Exception as e:      # noqa: BLE001  a crash is a red, named
            FAILS.append((t.__name__, "crashed: %r" % e))
    FAILS.extend(B.FAILS)           # go()'s own one-row-per-run checks
    if FAILS:
        print(json.dumps(FAILS, default=str)[:3000])
    print("selftest_engine_review_leftovers:", "FAIL" if FAILS else "OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
