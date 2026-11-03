#!/usr/bin/env python3
"""selftest_live_verdict.py -- the three-way live verdict and the health check before a proof (LIVE_VERDICT_BUILD_INFRA_NOT_FAIL;
design/RimMandrake/build_system_practices_2026-11-03.md top-5 #1).

No game, no bridge, no ledger. Planted faults, each of which must read INFRA and never FAIL: the bridge down, a game
file that is not the built commit's bytes, a health check that cannot run, a site that refuses, a refusal before the
bridge. A proof that ran after a healthy check is PASS on exit 0 and FAIL otherwise. INFRA writes no `verify` and
relentless_game charges it no strike; INFRA on `infra_games` games for one build is a `harness` row, which the game
phase sends to _harness (an alarm and a restage), never to a worker. Fx.health itself is run against a real git
commit and a fake game folder, with only wslpath and python.exe faked.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless_live as L            # noqa: E402
import selftest_relentless_live as T   # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s %s" % ("ok  " if cond else "FAIL", name))
    if not cond:
        FAILS.append((name, str(detail)[:400]))


def verbs(fx):
    return fx.verbs()


def t_bridge_down_is_infra():
    fx = T.FakeFx(health="the bridge does not answer rimbridge/ping from python.exe (exit 2): refused")
    row = T.go(fx)
    check("bridge down: INFRA", row["verdict"] == "INFRA" and row["outcome"] == "UNMEASURED", row)
    check("bridge down: the why says health", row["why"].startswith(L.UNHEALTHY), row["why"])
    check("bridge down: no proof, no verify, released", "proof" not in verbs(fx) and "verify" not in verbs(fx)
          and "release" in verbs(fx), verbs(fx))
    check("bridge down: health recorded not ok", row.get("health", {}).get("ok") is False, row.get("health"))


def t_deploy_mismatch_is_infra_and_undeployed():
    fx = T.FakeFx(health="not deployed: TheRot/Defs/Fauna/RM_Chittik.xml in the game folder is not the built commit's bytes")
    row = T.go(fx)
    check("hash mismatch: INFRA", row["verdict"] == "INFRA", row)
    check("hash mismatch: an UNDEPLOYED why, so the round retries it on another game only",
          row["why"].startswith(L.UNDEPLOYED) and row.get("game"), row)
    check("hash mismatch: no proof, no verify", "proof" not in verbs(fx) and "verify" not in verbs(fx), verbs(fx))


def t_health_crash_is_infra():
    fx = T.FakeFx(health=RuntimeError("wslpath vanished"))
    row = T.go(fx)
    check("health crash: INFRA, fail closed", row["verdict"] == "INFRA" and "could not run" in row["why"]
          and "proof" not in verbs(fx), (row, verbs(fx)))


def t_site_refusal_is_infra():
    fx = T.ScriptFx({T.SITE: (1, "no Stillsand tile")})
    root = tempfile.mkdtemp(prefix="rl_verdict_")
    row = L.run(fx, root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=1_800_000_000, site=T.SITE)
    check("site refusal: INFRA", row["verdict"] == "INFRA" and row["why"].startswith("site not prepared"), row)
    check("site refusal: health ran before the site", verbs(fx).index("health") < verbs(fx).index("proof"), verbs(fx))
    check("site refusal: the proof never ran", [c for c in fx.calls if c[0] == "proof"] == [("proof", T.SITE)],
          fx.calls)


def t_refusals_before_the_bridge_are_infra():
    fx = T.FakeFx(it=T.item(title="Chittik takes flight"))
    row = T.go(fx)
    check("flyer refusal: INFRA", row["outcome"] == "REFUSED" and row["verdict"] == "INFRA", row)
    fx = T.FakeFx(gap="not in the running load: TheRot (mandrake.rm.therot)")
    row = T.go(fx)
    check("no slot: INFRA, no health spent", row["verdict"] == "INFRA" and "health" not in verbs(fx), (row, verbs(fx)))
    fx = T.FakeFx(take_rc=1)
    row = T.go(fx)
    check("bridge busy: INFRA", row["verdict"] == "INFRA", row)


def t_after_the_proof_started_it_is_the_mods():
    for code, outcome, verdict in ((0, "PASS", "PASS"), (1, "FAIL", "FAIL"), (2, "UNMEASURED", "FAIL"),
                                   (None, "UNMEASURED", "FAIL")):
        fx = T.FakeFx(proof=code)
        row = T.go(fx)
        check("proof exit %s: %s/%s" % (code, outcome, verdict), (row["outcome"], row["verdict"]) == (outcome, verdict),
              row)
        check("proof exit %s: health ok before it" % code, row.get("health", {}).get("ok") is True, row.get("health"))
    fx = T.FakeFx(proof=1)
    T.go(fx)
    v = [c for c in fx.calls if c[:2] == ("rimflow", "verify")]
    check("a FAIL is still a verify fail", v and v[0][v[0].index("--result") + 1] == "fail", v)


def t_legacy_rows_keep_their_meaning():
    check("legacy FAIL", L.verdict({"outcome": "FAIL"}) == "FAIL")
    check("legacy PASS", L.verdict({"outcome": "PASS"}) == "PASS")
    for o in ("UNMEASURED", "REFUSED", None):
        check("legacy %s is INFRA" % o, L.verdict({"outcome": o}) == "INFRA")
    check("a written verdict wins", L.verdict({"outcome": "FAIL", "verdict": "INFRA"}) == "INFRA")


def t_infra_on_three_games_is_a_harness_row():
    root = tempfile.mkdtemp(prefix="rl_verdict_")
    rows = []
    for i, started in enumerate((2000.0, 3000.0, 4000.0, 4000.0)):
        fx = T.FakeFx(health="the bridge does not answer rimbridge/ping from python.exe (exit 2): refused",
                      started=started)
        rows.append(L.run(fx, root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=1_800_000_000 + i))
        rows[-1]["_notes"] = sum(1 for c in fx.calls if c[:2] == ("rimflow", "note"))
    check("games 1-2: INFRA, no harness, no defect", not any(r.get("harness") or r.get("defect") for r in rows[:2]),
          rows[:2])
    check("game 3: a harness row", rows[2].get("harness") and rows[2]["why"].startswith(L.HARNESS), rows[2])
    check("game 3: said once on the ledger", rows[2]["_notes"] == 1, rows[2])
    check("again after it: a row, no second note", rows[3].get("harness") and rows[3]["_notes"] == 0, rows[3])
    check("never a verify", all(r["verdict"] == "INFRA" for r in rows), [r["verdict"] for r in rows])
    # a row that never held the bridge does not count toward the cap
    root = tempfile.mkdtemp(prefix="rl_verdict_")
    for i, (started, gap) in enumerate(((2000.0, "not in the running load: TheRot (mandrake.rm.therot)"),
                                         (3000.0, "not in the running load: TheRot (mandrake.rm.therot)"), (4000.0, None))):
        fx = T.FakeFx(gap=gap, started=started, health="the bridge does not answer rimbridge/ping (exit 2)")
        r = L.run(fx, root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=1_800_000_000 + i)
    check("no-slot rows never count toward a harness row", r.get("health") and not r.get("harness"), r)


def t_game_phase_charges_infra_no_strike():
    import selftest_relentless_game as SG
    x = SG.rig(1)
    SG.to_game(x, "I0")
    x.tick()
    x.tick()
    x.w.rows = [{"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SG.SHA, "outcome": "FAIL",
                 "verdict": "INFRA", "log": "/l/A2.log"}]
    x.tick()
    st = x.st("I0")
    check("an INFRA verdict is no game_fail strike", not (st.get("last_fail") or {}).get("class") == "game_fail",
          st.get("last_fail"))
    x.done()
    x = SG.rig(1)
    SG.to_game(x, "I0")
    x.tick()
    x.tick()
    x.w.rows = [{"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SG.SHA, "outcome": "UNMEASURED",
                 "verdict": "INFRA", "harness": True, "why": L.HARNESS + ": INFRA on 3 games", "health": {"ok": False},
                 "log": "/l/A2.log"}]
    x.tick()
    st = x.st("I0")
    check("a harness row: no worker strike", not st.get("last_fail"), st.get("last_fail"))
    check("a harness row: _harness put it down to restage", (st.get("game") or {}).get("harness") == 1,
          st.get("game"))
    x.done()


def t_fx_health_reads_bytes_and_ping():
    """The real Fx.health on a real commit: only wslpath and python.exe are faked."""
    d = tempfile.mkdtemp(prefix="rl_health_")
    books, mods = os.path.join(d, "books"), os.path.join(d, "Mods")
    rel = "Defs/X.xml"
    os.makedirs(os.path.join(books, "src", "RimMandrake", "Rot", "Defs"))
    os.makedirs(os.path.join(books, "src", "RimMandrake", "Rot", "Cmp", "Defs"))
    body = b"<Defs><ThingDef/></Defs>\n"
    with open(os.path.join(books, "src", "RimMandrake", "Rot", rel), "wb") as f:
        f.write(body)
    git = lambda *a: subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *a], cwd=books,  # noqa: E731
                                    capture_output=True, text=True, timeout=60, check=True)
    git("init", "-q")
    git("add", "-A")
    git("commit", "-q", "-m", "x")
    sha = git("rev-parse", "HEAD").stdout.strip()
    real = subprocess.run
    ping = {"rc": 0}

    def fake(cmd, *a, **k):
        if cmd[0] == "wslpath":
            return types.SimpleNamespace(returncode=0, stdout="C:\\client.py\n", stderr="")
        if cmd[0] == "python.exe":
            check("ping is rimbridge/ping", "rimbridge/ping" in cmd, cmd)
            return types.SimpleNamespace(returncode=ping["rc"], stdout="", stderr="connection refused")
        return real(cmd, *a, **k)

    def put(path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)

    fx = L.Fx(books=books, mods_dir=mods)
    L.subprocess.run = fake
    try:
        put(os.path.join(mods, "Rot", rel), body)
        h = fx.health([("Rot", rel)], sha, 30)
        check("bytes match: healthy, hashed", h["why"] is None and h["hashed"] == 1, h)
        put(os.path.join(mods, "Rot", rel), body + b"<!-- stale -->")
        h = fx.health([("Rot", rel)], sha, 30)
        check("direct copy differs: not deployed", (h["why"] or "").startswith(L.UNDEPLOYED[0]), h)
        os.remove(os.path.join(mods, "Rot", rel))
        put(os.path.join(mods, "RimMandrake.Biomes", "Biomes", "Rot", rel), body.replace(b"<ThingDef/>", b"<ThingDef MayRequire=\"x\"/>"))
        h = fx.health([("Rot", rel)], sha, 30)
        check("composed copy rewritten: unhashed, not a failure", h["why"] is None and h["unhashed"] == 1, h)
        h = fx.health([("Rot", "Defs/Missing.xml")], sha, 30)
        check("a file the commit lacks: named", "no such file" in (h["why"] or ""), h)
        ping["rc"] = 2
        h = fx.health([("Rot", rel)], sha, 30)
        check("ping refused: unhealthy, before any bytes", "rimbridge/ping" in (h["why"] or "") and h["ping"] == 2, h)
    finally:
        L.subprocess.run = real


def main():
    for t in (t_bridge_down_is_infra, t_deploy_mismatch_is_infra_and_undeployed, t_health_crash_is_infra,
              t_site_refusal_is_infra, t_refusals_before_the_bridge_are_infra, t_after_the_proof_started_it_is_the_mods,
              t_legacy_rows_keep_their_meaning, t_infra_on_three_games_is_a_harness_row,
              t_game_phase_charges_infra_no_strike, t_fx_health_reads_bytes_and_ping):
        try:
            t()
        except Exception as e:     # noqa: BLE001  a crash is a red, named
            FAILS.append((t.__name__, "crashed: %r" % e))
    import selftest_relentless as S
    FAILS.extend(T.FAILS + S.FAILS)     # go()'s one-row check, the game rig's own
    if FAILS:
        print(json.dumps(FAILS, default=str)[:3000])
    print("selftest_live_verdict:", "FAIL" if FAILS else "OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
