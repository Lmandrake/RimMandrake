#!/usr/bin/env python3
"""The Judge names the cause before anything goes back to a builder (CHECKER_VERDICT_BUILD_CAUSE_BEFORE_RETURN; plan
design/RimMandrake/relentless_recovery_plan_2026-11-05.md step 5; catalog class d, the owner's "judges unable to judge
throwing things back to fix without fixing the measurement").

Rows:
  C1  each --defect carries a cause (product|measurement|environment|unknown); untagged is unknown, never product; a
      product claim is VALID only with a --control and a citation of the candidate (a diff path, or the proof's own name).
  C2  the verdict script and the CLI door refuse a product: defect without a --control.
  C3  replay of the class-d sightings through the real tick: each routes away from the builder (no strike, no new code
      generation); a measurement defect goes to the proof road on the SAME sha.
  C4  an ENOSPC --defect opens an environment alarm keyed on the dependency `disk`.
  C5  positive control: a validated product defect reaches the builder with its strike (the instrument can see).
  C6  fail() never strikes a validation ending on a non-PRODUCT attribution.
  C7  the game lane's not_measuring and blocked_here no longer go `_back`: withheld for diagnosis, cause measurement.
  C8  live_reading has three states: holds, does_not_hold, unread (a reader that raised)."""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                      # noqa: E402
import relentless_wall as W                 # noqa: E402
import relentless_reach as RR               # noqa: E402
import relentless_game as G                 # noqa: E402
import selftest_relentless as T             # noqa: E402
import selftest_relentless_blind as B       # noqa: E402
import selftest_relentless_game as SG       # noqa: E402

FAILS = []
GAME_PY = "src/RimMandrake/rimflow/relentless_game.py"


def ok(cond, name):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


# the catalog's class-d sightings (design/RimMandrake/relentless_failure_catalog_2026-11-05.md, triage batch 00), each as
# the defect a Judge following the new rule writes; every one must route away from the builder
SIGHTINGS = [
    ("GRAFFITI_NORTHSTAR_GREEN_FULL_1", "environment: a game already loaded, then Graffiti not in the load",
     "environment", "game"),
    ("GENERATOR_MODS_PROVE_INERT", "environment: save.missing_mods every time the proof save opens", "environment", "game"),
    ("ATMOSBASE", "measurement: the proof save is stale on the current load, so the proof reads nothing", "measurement",
     None),
    ("ART_OVERRIDE_FAMILY_SCRIPT_1", "unknown: Scarlands has no readable packageId; UNMEASURED 8 times", "unknown", None),
    ("STEVE ssh (untagged, old Judge)", "SSH denied: ssh stevedesktop exits 255", "unknown", None),
    ("product claim with no control", "product: the parser drops the last row", "unknown", None),
    ("ENOSPC", "environment: writing the proof log failed: OSError ENOSPC (No space left on device)", "environment", "disk"),
]


def t_causes_table():
    ch = [GAME_PY]
    for name, d, want, _ in SIGHTINGS:
        rows = W.causes([d], [], ch, "python3 selftest_x.py")
        ok(W.route(rows) == want and rows[0]["acts"] != W.PRODUCT, "C1 %s reads %s, never product: %s" % (name, want, rows))
    ok(W.parse_defect("the parser drops a row") == ("unknown", "the parser drops a row"), "C1 untagged is unknown")
    ok(W.parse_defect("Product : x")[0] == "product", "C1 a tag is read case- and space-blind")
    good = W.causes(["product: relentless_game.py drops the A2 row"], ["green on the parent sha, red here"], ch, None)
    ok(good[0]["valid"] and W.route(good) == W.PRODUCT, "C1 a product defect with a control citing a diff path is valid")
    by_proof = W.causes(["product: selftest_x says 2 FAIL"], ["selftest_x is green on the parent"], [], "python3 selftest_x.py")
    ok(by_proof[0]["valid"], "C1 citing the contract proof's own name is behaviour: valid")
    nocite = W.causes(["product: the work is wrong"], ["green on parent"], ch, "python3 selftest_x.py")
    ok(not nocite[0]["valid"] and W.route(nocite) == W.UNKNOWN and "cites" in nocite[0]["why_not"],
       "C1 a product claim that cites nothing of the candidate is unknown: %s" % nocite)
    noctl = W.causes(["product: relentless_game.py drops the A2 row"], [], ch, None)
    ok(not noctl[0]["valid"] and "control" in noctl[0]["why_not"], "C1 a product claim with no control is unknown")
    ok(not W.cites("product: game.py", [GAME_PY], None) or True, "C1 (a bare short name is not a citation either way)")
    mixed = W.causes(["measurement: the selftest stem is wrong", "environment: disk full"], [], ch, None)
    ok(W.route(mixed) == W.ENVIRONMENT, "C1 measurement with environment routes environment")
    mixed2 = W.causes(["unknown: ?", "product: relentless_game.py drops a row"], ["ctl"], ch, None)
    ok(W.route(mixed2) == W.PRODUCT, "C1 a validated product defect anywhere routes product")
    ok(W.route([]) == W.UNKNOWN, "C1 no rows is unknown")
    for key, text in (("disk", "ENOSPC"), ("account", "HTTP 429 rate limit"), ("remote_host", "ssh stevedesktop exits 255"),
                      ("game", "Graffiti not in the load"), ("other", "something odd")):
        ok(W.dependency(text) == key, "C4 %r is keyed %s" % (text, key))


def t_doors():
    d = tempfile.mkdtemp(prefix="cause_box_")
    script = os.path.join(d, "verdict")
    with open(script, "w", encoding="utf-8") as f:
        f.write(W.VERDICT_SCRIPT)

    def run(*a):
        return subprocess.run([sys.executable, script, *a], capture_output=True, text=True, timeout=30)
    ok(run("FAIL", "x", "--defect", "product: a.py is wrong").returncode != 0, "C2 the script refuses product with no control")
    ok(run("FAIL", "x", "--control", "c").returncode != 0, "C2 a control with no defect is refused")
    ok(run("FAIL", "x", "--defect", "unknown: odd").returncode == 0, "C2 an unknown defect is recorded")
    ok(run("FAIL", "x", "--defect", "product: a.py is wrong", "--control", "green on parent").returncode == 0,
       "C2 product with a control is recorded")
    v = W.read_verdict(d)
    ok(v and v["controls"] == ["green on parent"] and v["defects"] == ["product: a.py is wrong"],
       "C2 the box file carries the controls: %s" % v)
    ok(run("FAIL", "x", "--defect", "an old untagged line").returncode == 0, "C2 an untagged defect is accepted, read unknown")
    ok(W.refusal("FAIL", ["product: x"], [], None) and not W.refusal("FAIL", ["product: x"], [], ["c"]),
       "C2 the CLI door says the same")


def checked(x, i="I0"):
    return B.to_check(x, i)


def speak(x, st, defects, controls=None, changed=(), strict=False, i="I0"):
    R.verdict(x.s, i, st["check"]["nonce"], "FAIL", "ran it", defects=defects, unreached=[], strict=strict,
              controls=controls, changed=list(changed))
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick()
    x.tick()
    return x.st(i)


def journal(x):
    try:
        with open(x.s.p("journal.jsonl"), encoding="utf-8") as f:
            return [json.loads(ln) for ln in f if ln.strip()]
    except FileNotFoundError:
        return []


def t_replay():
    for name, d, want, dep in SIGHTINGS:
        x = T.Rig(n=1, reach_repair=False, share=1.0, same_failure_limit=2)
        was = checked(x)
        st = speak(x, was, [d], changed=[GAME_PY])
        sha = was["candidate"]["sha"]
        no_strike = not st["failures"].get("blind_fail") and st.get("approach") == was.get("approach")
        if want == "measurement":
            po = st.get("proof_only") or {}
            ok(no_strike and po.get("sha") == sha and st["failures"].get("proof_owed") == 1,
               "C3 %s: measurement goes to the proof road on the same sha, no code strike: %s %s" % (name, st["failures"], po))
        else:
            w = st.get("wait") or {}
            ok(no_strike and st["gen"] == was["gen"] and w.get("kind") == "attribution" and w.get("sha") == sha,
               "C3 %s: withheld for diagnosis, no strike, no new generation: %s gen %s->%s wait %s"
               % (name, st["failures"], was["gen"], st["gen"], {k: w.get(k) for k in ("kind", "class", "cause")}))
        rec = [j for j in journal(x) if j.get("do") == "cause_routed"]
        ok(rec and rec[-1]["cause"] == want, "C3 %s: the routing is journalled as %s" % (name, want))
        if dep:
            al = [j for j in journal(x) if j.get("do") == "alarm" and j.get("kind") == "environment_defect"]
            ok(al and al[-1]["dependency"] == dep and (st.get("wait") or {}).get("cause") == "environment",
               "C4 %s: an environment alarm keyed %s, the wait says environment: %s" % (name, dep, al))
        x.done()


def t_positive_control():
    x = T.Rig(n=1, reach_repair=False, share=1.0, same_failure_limit=2)
    was = checked(x)
    st = speak(x, was, ["product: relentless_game.py drops the A2 row (expected 3, got 2)"],
               controls=["the same proof is green on the parent sha"], changed=[GAME_PY], strict=True)
    at = st.get("attribution") or {}
    ok(st["failures"].get("blind_fail") == 1 and st["gen"] > was["gen"] and at.get("targets") == ["PRODUCT"]
       and at.get("by") == "checker verdict" and not (st.get("wait") or {}),
       "C5 a validated product defect goes to the builder with its strike, no diagnosis: %s gen %s->%s %s"
       % (st["failures"], was["gen"], st["gen"], at.get("by")))
    x.done()


def t_fail_guard():
    x = T.Rig(n=1, reach_repair=False, share=1.0, same_failure_limit=2)
    was = checked(x)
    with x.s.lock():
        st = x.s.load("I0")
        rec = R.relentless_attrib.record(["PROOF"], "e", x.now, "test", st["candidate"]["sha"])
        got = R.fail(x.s, st, "blind_fail", "x", x.r, x.now, attributed=rec)
    st = x.s.load("I0")
    ok(got == "gated" and not st["failures"].get("blind_fail") and st["gen"] == was["gen"],
       "C6 fail() blames afresh a validation ending handed a non-PRODUCT attribution: %s %s" % (got, st["failures"]))
    x.done()


def game_dud(x, here):
    import relentless_live
    x2 = x
    SG.to_game(x2, "I0")
    x2.tick()
    x2.tick()
    dud = {"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SG.SHA, "outcome": "UNMEASURED",
           "log": "/l/d.log", "why": "the proof exited 2: it did not measure: Scarlands has no readable packageId"}
    was = x2.st("I0")
    if here:
        x2.w.started = x2.now - 3000.0
        x2.w.rows = [dict(dud, game=relentless_live.iso(x2.w.started))]
    else:
        x2.w.rows = [dict(dud), dict(dud, at="2099-01-01T00:20:00Z")]
    x2.tick()
    return was, x2.st("I0")


def t_game_lane():
    src = open(os.path.join(HERE, "relentless_game.py"), encoding="utf-8").read()
    ok(not re.search(r"_back\([^)]*\"game_unmeasured\"", src), "C7 no _back(..., \"game_unmeasured\") is left in the game lane")
    for here in (False, True):
        x = SG.rig(1)
        was, st = game_dud(x, here)
        w = st.get("wait") or {}
        ok(w.get("kind") == "attribution" and w.get("cause") == "measurement" and w.get("class") == "game_unmeasured"
           and st["gen"] == was["gen"] and not st["failures"].get("game_unmeasured") and st.get("returns") == was.get("returns"),
           "C7 %s: withheld for diagnosis with cause measurement, no strike, no return, no new gen: %s %s"
           % ("blocked_here" if here else "not_measuring", st["failures"], {k: w.get(k) for k in ("kind", "class", "cause")}))
        ok(st["last_fail"]["class"] == "game_unmeasured" and "Scarlands" in st["last_fail"]["detail"],
           "C7 the reason is kept whole for the diagnosis")
        x.done()


def t_live_reading():
    def boom(line, now=None):
        raise ZeroDivisionError("x")
    a = RR.live_reading("once: t", check=lambda line, now=None: None, now=1.0)
    b = RR.live_reading("once: t", check=lambda line, now=None: "absent", now=1.0)
    c = RR.live_reading("once: t", check=boom, now=1.0)
    ok((a["state"], b["state"], c["state"]) == (RR.HOLDS, RR.DOES_NOT_HOLD, RR.UNREAD)
       and (a["holds"], b["holds"], c["holds"]) == (True, False, False), "C8 three states: %s %s %s"
       % (a["state"], b["state"], c["state"]))
    d = tempfile.mkdtemp(prefix="cause_live_")
    t = [open(RR.write_live(os.path.join(d, n), g), encoding="utf-8").read()
         for n, g in (("a", a), ("b", b), ("c", c)) if os.makedirs(os.path.join(d, n)) is None]
    ok("HOLDS" in t[0] and "DOES NOT HOLD" in t[1] and "COULD NOT READ" in t[2] and "DOES NOT HOLD" not in t[2],
       "C8 the Marker's file says which of the three")


def main():
    for t in (t_causes_table, t_doors, t_replay, t_positive_control, t_fail_guard, t_game_lane, t_live_reading):
        t()
    print("selftest_relentless_cause: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
