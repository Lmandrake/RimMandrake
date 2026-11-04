#!/usr/bin/env python3
"""selftest_repro_miss.py -- RELENTLESS_DIAGNOSE_REPRO_MISS_AS_GAME_FAIL.

A defect-repro proof that ran on its site and did not see the defect ("NOT REPRODUCED: ...", "NOT SHARED: ...", exit 1)
is a repro MISS: never a game_fail strike (LEANINGSCRUB_STALL_SHARED_MOVE_1's NOT SHARED was booked "A1 FAIL on the
running game") and never a dud sent to a new builder (its NOT REPRODUCED was). What must hold, each red under its mutant:
  M1 the log readers: NOT REPRODUCED and NOT SHARED are kind "miss"; a FAIL row beside one keeps the FAIL; an all-UNMEASURED
     log stays a dud;
  M2 relentless_live.run: a miss writes no verify, an UNMEASURED row flagged miss whose why starts REPRO_MISS and names
     the verdict line; that why is no same-game dud (the round may run it again);
  M3 relentless_game: one miss keeps the item in its game phase; repro_miss_limit (2) misses on the build hold it as
     not_reproduced, last_fail carrying both verdict lines, no worker sent; an unhold buys fresh tries;
  M4 a game_fail's detail names the proof's last verdict line, not only the log path (from the row, or read from an
     older row's log), and relentless_breakers still keys it by its clause.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless as R                  # noqa: E402
import relentless_breakers as B         # noqa: E402
import relentless_game as G             # noqa: E402
import relentless_live as L             # noqa: E402
import relentless_live_round as LR      # noqa: E402
import selftest_relentless as S         # noqa: E402
import selftest_relentless_game as SG   # noqa: E402
import selftest_relentless_live as T    # noqa: E402

FAILS = []
SHARED = ("ON  RM_Thornhold path 6.5 net (-5, -4) jobs-during-move ['Goto']\n"
          "NOT SHARED: the two net moves (-5, -4) and (-3, 5) differ by more than 4 cells; the job is not named\n"
          "record: D:/ClaudeWork/rimmandrake/X/repro_stall_move.json")
NOTREP = ("ON  RM_Shirrel path 5.0 net (0, -5) jobs-during-move ['GotoWander']\n"
          "NOT REPRODUCED: neither animal moved >= 6 cells in 300 ticks; the job is not named\n"
          "record: D:/ClaudeWork/rimmandrake/X/repro_stall_move.json")


def check(name, cond, detail=""):
    print("%s %s" % ("ok  " if cond else "FAIL", name))
    if not cond:
        FAILS.append((name, str(detail)[:400]))


def logfile(text):
    fd, p = tempfile.mkstemp(suffix=".log", prefix="rmiss_")
    with os.fdopen(fd, "w") as f:
        f.write("$ python.exe repro.py\n" + text + "\n")
    return p


def t_m1_readers():
    check("M1 NOT SHARED is a miss", (L.could_not_ask(logfile(SHARED)) or ("",))[0] == "miss",
          L.could_not_ask(logfile(SHARED)))
    k = L.could_not_ask(logfile(NOTREP))
    check("M1 NOT REPRODUCED is a miss, its line kept", k and k[0] == "miss" and k[1].startswith("NOT REPRODUCED"), k)
    check("M1 a FAIL row beside a miss keeps the FAIL",
          L.could_not_ask(logfile(NOTREP + "\nT2 FAIL: the stall lock dropped")) is None)
    check("M1 every verdict UNMEASURED is still a dud",
          (L.could_not_ask(logfile("VERDICT UNMEASURED: no animal spawned")) or ("",))[0] == "dud")
    check("M1 last_verdict reads the verdict line", L.last_verdict(logfile(SHARED)).startswith("NOT SHARED"),
          L.last_verdict(logfile(SHARED)))


def t_m2_run_row():
    root = tempfile.mkdtemp(prefix="rl_live_")
    proof = "python.exe src/RimMandrake/LeaningScrub/repro_stall_move.py"
    fx = T.ScriptFx({proof: (1, SHARED)})
    row = L.run(fx, root, "ROT_X", "A2", proof, "--compose biomes", {}, now=1_800_000_000)
    check("M2 a miss is no FAIL", row["outcome"] == "UNMEASURED" and row.get("miss") is True, row)
    check("M2 no verify written", "verify" not in fx.verbs(), fx.verbs())
    check("M2 its why is a repro miss naming the verdict", row["why"].startswith(L.REPRO_MISS) and "NOT SHARED" in
          row["why"], row["why"])
    check("M2 not a same-game dud: the round may run it again", not LR.SAME_GAME_DUD.search(row["why"])
          and not G.RAN_DUD.search(row["why"]) and LR.due(row, row.get("sha"), 2_000_000_000, 0, row.get("game"),
                                                         per_game=False) is None, row)
    fx = T.ScriptFx({proof: (1, "T1 FAIL: the stall lock dropped\nproof FAILED")})
    row = L.run(fx, root, "ROT_X", "A2", proof, "--compose biomes", {}, now=1_800_000_100)
    check("M2 a real FAIL row carries its verdict line", row["outcome"] == "FAIL"
          and row.get("verdict_line") == "T1 FAIL: the stall lock dropped", row)


def miss_row(at, log, sha=SG.SHA, line=SHARED.splitlines()[1]):
    return {"at": at, "item": "I0", "criterion": "A2", "sha": sha, "outcome": "UNMEASURED", "miss": True, "log": log,
            "why": "%s: the defect-repro proof ran on its site and did not reproduce the defect: %s" % (L.REPRO_MISS,
                                                                                                         line)}


def t_m3_game_holds_after_two():
    x = SG.rig(1)
    SG.to_game(x, "I0")
    x.tick()
    x.tick()
    x.w.rows = [miss_row(L.iso(x.now - 60), "/l/m1.log")]
    x.tick()
    st = x.st("I0")
    check("M3 one miss: still in the game phase, no worker", st["status"] == "game" and not st.get("last_fail"),
          (st["status"], st.get("last_fail")))
    x.w.rows.append(miss_row(L.iso(x.now - 30), "/l/m2.log", line=NOTREP.splitlines()[1]))
    x.tick()
    st = x.st("I0")
    check("M3 two misses: held", st["status"] == "held" and (st.get("hold") or {}).get("kind") == "game", st.get("hold"))
    lf = st.get("last_fail") or {}
    check("M3 last_fail is not_reproduced with both verdict lines", lf.get("class") == "not_reproduced"
          and "NOT SHARED" in lf.get("detail", "") and "NOT REPRODUCED" in lf.get("detail", "")
          and "/l/m2.log" in lf.get("detail", ""), lf)
    check("M3 no strike, no new generation", st["gen"] == 1 and not st["failures"].get("game_fail")
          and not st["failures"].get("game_unmeasured"), (st["gen"], st["failures"]))
    check("M3 the ledger is told", any("not reproduced" in n for n in x.w.notes), x.w.notes[-2:])
    R.unhold(x.s, "I0", "test: try again", now=x.now)
    x.tick()
    st = x.st("I0")
    check("M3 unhold: back to proving with fresh tries", st["status"] == "game" and not st.get("hold"),
          (st["status"], st.get("hold")))
    x.w.rows.append(miss_row(L.iso(x.now + 10), "/l/m3.log"))
    x.tick()
    check("M3 after unhold one new miss is not yet a hold", x.st("I0")["status"] == "game", x.st("I0").get("hold"))
    x.done()


def t_m4_fail_detail():
    log = logfile("T1 FAIL: the stall lock dropped\nproof FAILED")
    d = G.fail_detail("A1", {"log": log})
    check("M4 an older row: the line is read from its log", d.startswith("A1 FAIL on the running game (%s): " % log)
          and d.endswith(": T1 FAIL: the stall lock dropped"), d)
    d2 = G.fail_detail("A2", {"log": "/l/x.log", "verdict_line": "FAIL: a; b"})
    check("M4 the row's line is used, its ';' cannot split a clause", d2.endswith("FAIL: a, b"), d2)
    check("M4 the breakers still key it by clause",
          B.signature("game_fail", d + "; " + d2) == B.signature("game_fail", "A1 FAIL on the running game (/a); "
                                                                              "A2 FAIL on the running game (/b)"))
    x = SG.rig(1)
    SG.to_game(x, "I0")
    x.tick()
    x.tick()
    x.w.rows = [{"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SG.SHA, "outcome": "FAIL",
                 "log": "/l/A2.log", "verdict_line": "A2 FAIL MOD: the pump never ran"}]
    x.tick()
    S.blame_product(x, "I0")
    lf = x.st("I0").get("last_fail") or {}
    check("M4 game_fail last_fail.detail carries the verdict line", lf.get("class") == "game_fail"
          and "the pump never ran" in lf.get("detail", "") and "/l/A2.log" in lf.get("detail", ""), lf)
    x.done()


def main():
    for t in (t_m1_readers, t_m2_run_row, t_m3_game_holds_after_two, t_m4_fail_detail):
        try:
            t()
        except Exception as e:     # noqa: BLE001  a crash is a red, named
            import traceback
            traceback.print_exc()
            FAILS.append((t.__name__, "crashed: %r" % e))
    FAILS.extend(T.FAILS + S.FAILS)
    if FAILS:
        print(json.dumps(FAILS, default=str)[:3000])
    print("selftest_repro_miss:", "FAIL" if FAILS else "OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
