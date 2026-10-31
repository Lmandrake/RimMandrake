#!/usr/bin/env python3
"""selftest_arena_anchor_publish.py - the periodic ledger-anchor publisher (ARENA_ANCHOR_FIX_PUBLISH_BEFORE_ANALYSIS).

REAL signed logs (arena_eventlog.HarnessWriter, temp token, file witness) and a THROWAWAY rimflow ledger (the real
`rimflow note` through RIMFLOW_LEDGER): the publisher's note makes arena_analysis.verified_logs (the loader of both
arena_analysis run and arena_spend) read the arms TRUSTED; a second tick with nothing new writes no note; growth is
reported as anchor_lag/STALE_ANCHORS until the next tick; a truncated or tampered log is REFUSED (never re-anchored)
and reads UNMEASURED; a witness that lags the log is not published; --final fails on any unanchored replay arm.
Mutants: an arm skipped by the publisher, the stale report removed, the refusal guard removed -> each caught.
Never touches the real token, ledger, clone or units.

    python3 src/RimMandrake/Utils/arena/selftest_arena_anchor_publish.py
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_analysis as AA  # noqa: E402
import arena_anchor_publish as P  # noqa: E402

L = AA.L
FAILS: list[str] = []
ENV = ("ARENA_ROOT", "ARENA_EVENT_TOKEN_FILE", "ARENA_ANCHOR_FILE", "ARENA_WITNESS", "ARENA_ARM_TOML",
       "RIMFLOW_LEDGER", "RIMFLOW_ITEMS")


def check(name, ok, detail=""):
    if not ok:
        FAILS.append(name)
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -- " + str(detail)[:400]) if detail and not ok else ""))


def seed_ledger(led: Path):
    """A throwaway ledger holding the item the notes go to (filed through the real CLI)."""
    led.parent.mkdir(parents=True, exist_ok=True)
    (led.parent / "items").mkdir(exist_ok=True)
    led.write_text("")
    env = dict(os.environ, RIMFLOW_LEDGER=str(led), RIMFLOW_ITEMS=str(led.parent / "items"))
    r = subprocess.run([sys.executable, str(P.REPO / "src/RimMandrake/rimflow/cli.py"), "file", P.DEFAULT_ITEM,
                        "--seat", "FOUNDRY", "--title", "selftest anchor item", "--kind", "task", "--target", "v1",
                        "--needs", "offline", "--for", "FOUNDRY", "--why", "selftest"], env=env, capture_output=True,
                       text=True, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr


def anchor_notes(led: Path) -> list[str]:
    sys.path.insert(0, str(HERE.parent.parent))
    from rimflow import model
    return [e["text"] for fn in model.ledger_files(str(led)) for e in model.read(fn)
            if e.get("event") == "note" and str(e.get("text", "")).startswith("ARENA_ANCHOR")]


def tick(led, *extra):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = P.main(["--ledger", str(led), "--arms", "trio,v3", *extra])
    return rc, json.loads(buf.getvalue().strip().splitlines()[-1])


def um(logs, arm):
    return "unmeasured" in logs.get(arm, {"unmeasured": "absent"})


def run():
    saved = {k: os.environ.get(k) for k in ENV}
    d = Path(tempfile.mkdtemp(prefix="anchor_pub_"))
    try:
        os.environ.update(ARENA_ROOT=str(d / "arena"), ARENA_EVENT_TOKEN_FILE=str(d / "secret" / "event_token"),
                          ARENA_ANCHOR_FILE=str(d / "secret" / "anchors.jsonl"),
                          ARENA_WITNESS=str(d / "secret" / "witness.jsonl"), ARENA_ARM_TOML=str(d / "no_arm.toml"))
        for k in ("RIMFLOW_LEDGER", "RIMFLOW_ITEMS"):
            os.environ.pop(k, None)
        p = AA.A.paths()
        L.init_token(p)
        w = L.HarnessWriter(p)

        def emit(arm, i):
            w.emit(arm, "assign", lane="build", run_id="%s.%d" % (arm, i), task="T%03d" % i,
                   ts="2026-11-01T%02d:00:00Z" % i)

        for arm in ("trio", "v3"):
            for i in range(4):
                emit(arm, i)
        led = d / "led" / "events.jsonl"
        seed_ledger(led)

        # before any publish: nothing trusted, both lagging
        logs0, tr0 = AA.verified_logs(None, led)
        check("before publish: both arms UNMEASURED and reported in anchor_lag",
              um(logs0, "trio") and um(logs0, "v3") and set(tr0.get("anchor_lag", {})) >= {"trio", "v3"}, tr0)

        # 1 genuine tick
        rc, r1 = tick(led)
        n1 = anchor_notes(led)
        check("tick: one ARENA_ANCHOR note with trio:4, v3:4 and @roster", rc == 0 and len(n1) == 1
              and all(t in n1[0] for t in (" trio:4:", " v3:4:", " @roster:")), (rc, r1, n1))
        logs1, tr1 = AA.verified_logs(None, led)
        check("tick: arena_analysis loader reads both arms TRUSTED, no anchor_lag",
              tr1.get("trusted_arms") == ["trio", "v3"] and "anchor_lag" not in tr1
              and len(logs1["v3"]["recs"]) == 4, tr1)

        # 2 idempotent
        rc, r2 = tick(led)
        check("idempotent: a second tick with nothing new writes NO note", rc == 0 and r2["note"] is None
              and len(anchor_notes(led)) == 1 and r2["arms"]["v3"]["action"] == "current", r2)

        # 3 growth -> stale reported, then re-anchored
        emit("v3", 4)
        logs3, tr3 = AA.verified_logs(None, led)
        check("stale: v3 grew past its anchor -> anchor_lag v3 5>4, STALE_ANCHORS names --final, v3 UNMEASURED",
              tr3.get("anchor_lag", {}).get("v3") == {"accepted": 5, "ledger_anchored_upto": 4}
              and "--final" in tr3.get("STALE_ANCHORS", "") and um(logs3, "v3") and not um(logs3, "trio"), tr3)
        real_lag = AA.anchor_lag
        AA.anchor_lag = lambda rep: {}
        try:
            _, trm = AA.verified_logs(None, led)
        finally:
            AA.anchor_lag = real_lag
        check("MUTANT stale report removed -> the stale row's condition goes false (caught)",
              "anchor_lag" not in trm and "STALE_ANCHORS" not in trm, trm)
        # mutant: the publisher skips v3 -> --final catches it, analysis keeps v3 UNMEASURED
        real_cover = P.arms_to_cover
        P.arms_to_cover = lambda p_, req=None: (lambda rc_: (rc_[0], [a for a in rc_[1] if a != "v3"]))(
            real_cover(p_, req))
        try:
            rcm, rm_ = tick(led, "--final")
        finally:
            P.arms_to_cover = real_cover
        logsm, _ = AA.verified_logs(None, led)
        check("MUTANT publisher skips v3 -> --final exits 3 naming v3, v3 still UNMEASURED (caught)",
              rcm == 3 and any(s.startswith("v3:") for s in rm_["final_problems"]) and um(logsm, "v3"), rm_)
        rc, r3 = tick(led, "--final")
        n3 = anchor_notes(led)
        check("re-anchor: next tick publishes v3:5 only (+roster); --final exits 0",
              rc == 0 and len(n3) == 2 and " v3:5:" in n3[-1] and " trio:" not in n3[-1]
              and not r3["final_problems"], (rc, r3.get("final_problems"), n3[-1:]))
        logs3b, tr3b = AA.verified_logs(None, led)
        check("re-anchor: both TRUSTED again, no anchor_lag", tr3b.get("trusted_arms") == ["trio", "v3"]
              and "anchor_lag" not in tr3b, tr3b)

        # 4 witness lagging the log -> not published
        os.environ["ARENA_WITNESS"] = str(d / "secret" / "other_witness.jsonl")
        emit("v3", 5)
        os.environ["ARENA_WITNESS"] = str(d / "secret" / "witness.jsonl")
        rc, r4 = tick(led)
        check("witness behind the log (n=6, witness 5) -> v3 skipped, no note", r4["arms"]["v3"]["action"] == "skip"
              and "witness n=5" in r4["arms"]["v3"]["why"] and r4["note"] is None, r4["arms"]["v3"])
        rc, r4f = tick(led, "--final")
        check("--final with an unpublishable arm exits 3", rc == 3 and r4f["final_problems"], r4f)
        # restore: re-witness by appending the anchor of record 6 to the witness file (as close() would)
        acc = L.verify(p, "v3", L._read_token(p))["accepted"]
        L.witness_append(p, dict(L.make_anchor("v3", acc, L._read_token(p)), kind="anchor"))
        rc, r4b = tick(led)
        check("witness caught up -> v3:6 published", r4b["arms_after"]["v3"]["action"] == "current"
              and r4b["arms"]["v3"]["action"] == "publish", r4b["arms"]["v3"])

        # 5 truncated copy of trio
        tf = p["events"] / "trio.jsonl"
        lines = tf.read_text().splitlines(True)
        tf.write_text("".join(lines[:-1]))
        nb = len(anchor_notes(led))
        rc, r5 = tick(led, "--final")
        logs5, _ = AA.verified_logs(None, led)
        check("truncated trio -> publisher REFUSES it (no shorter tip anchored), --final 3, analysis UNMEASURED",
              r5["arms"]["trio"]["action"] == "refused" and rc == 3 and um(logs5, "trio")
              and not any(" trio:" in t for t in anchor_notes(led)[nb:]), (rc, r5["arms"]["trio"]))
        real_ca = L.check_anchors
        L.check_anchors = lambda acc_, anchors, errors=None: []
        try:
            _, r5m = tick(led, "--dry-run")
        finally:
            L.check_anchors = real_ca
        check("MUTANT refusal guard removed -> trio no longer 'refused' (the truncated row above catches it)",
              r5m["arms"]["trio"]["action"] != "refused", r5m["arms"]["trio"])
        # 6 tampered trio (one byte of record 2)
        bad = json.loads(lines[1])
        bad["task"] = "T999"
        tf.write_text("".join([lines[0], json.dumps(bad, sort_keys=True) + "\n"] + lines[2:]))
        rc, r6 = tick(led)
        logs6, _ = AA.verified_logs(None, led)
        check("tampered trio -> refused by the publisher, UNMEASURED in analysis",
              r6["arms"]["trio"]["action"] == "refused" and um(logs6, "trio") and not um(logs6, "v3"),
              r6["arms"]["trio"])
        tf.write_text("".join(lines))
        logs7, tr7 = AA.verified_logs(None, led)
        check("control: restored trio is TRUSTED again", tr7.get("trusted_arms") == ["trio", "v3"], tr7)

        # 7 dry-run writes nothing; unreadable ledger refuses
        emit("trio", 4)
        nb = len(anchor_notes(led))
        rc, r8 = tick(led, "--dry-run")
        check("--dry-run plans trio:5 but writes no note", str(r8["note"]).startswith("DRY-RUN") and
              len(anchor_notes(led)) == nb, r8["note"])
        rc, r9 = tick(d / "nowhere" / "events.jsonl")
        check("missing ledger -> ERROR exit 2, never publishes blind", rc == 2 and "ERROR" in r9, r9)

        # 8 units
        u = P.units(Path("/home/mandrake/rm/anchor"), 10, "/mnt/d/x/publisher.log")
        svc, tmr = u[P.UNIT + ".service"], u[P.UNIT + ".timer"]
        svc_body = "\n".join(x for x in svc.splitlines() if not x.startswith("#"))
        check("units: service in rm-harness.slice, oneshot, runs this script with --clone, no token path, no PartOf",
              "Slice=rm-harness.slice" in svc and "Type=oneshot" in svc and "arena_anchor_publish.py --clone "
              "/home/mandrake/rm/anchor" in svc and "event_token" not in svc and "PartOf" not in svc_body
              and "@" not in svc_body, svc_body)
        check("units: timer fires every 10 min and is WantedBy timers.target",
              "OnUnitActiveSec=10min" in tmr and "WantedBy=timers.target" in tmr, tmr)
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(d, ignore_errors=True)


def main():
    run()
    print("\n%d failure(s)%s" % (len(FAILS), (": " + ", ".join(FAILS)) if FAILS else ""))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
