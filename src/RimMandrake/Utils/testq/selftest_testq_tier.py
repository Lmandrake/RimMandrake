#!/usr/bin/env python3
"""selftest_testq_tier.py - exact-tier jobs in the queue (LANE_TIER_WIRE_A_WHOLE_LIST_LOAD).

Owner by card 2026-11-05: SteveDesktop is the exact-tier host. What must hold, with no ssh and no game:
  schema: a job of profile tier:<name> selects proofs and nothing else, names its item, runs on lane stevedesktop only;
  a tier profile without proofs, proofs without a tier, lane archmagi or any, no item, or a malformed tier are refused;
  the worker's proof-line grammar is rimflow's (relentless_live_round.PROOF_LINE), parse for parse;
  submit: `testq.py submit ITEM --proofs A1 --profile tier:<t>` queues it with no modcheck preview; an unknown tier is
  refused; the same request again answers with the pending job (no double);
  batching: admission stays on a tier train while a job for it waits, even past a higher priority; off a tier, priority
  still leads; the Archmagi backfill never takes a tier job, whatever TESTQ_ARCHMAGI_PROFILES says;
  ingest: a proofs job files no RUNNER verify and no finding (Relentless verifies its clauses).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
import schema as S  # noqa: E402

FAILS = []
SHA = "0123456789abcdef0123456789abcdef01234567"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def refused(fn, msg):
    try:
        fn()
        check(False, "refused: " + msg)
    except S.SchemaError as e:
        check(True, "refused: %s (%s)" % (msg, str(e)[:90]))


def tier_job(**kw):
    a = dict(item="VITALS_X", profile="tier:ratchet_pilot", lane="stevedesktop")
    a.update(kw)
    sel = a.pop("sel", {"proofs": ["A1"]})
    return S.make_job("VITALS_X", sel, "fix", "RELENTLESS", SHA, **a)


def t_schema():
    j = tier_job()
    check(S.tier_of(j) == "ratchet_pilot" and S.is_proofs(j), "a tier job: tier_of and is_proofs read it")
    check(S.tier_of({"profile": "targeted"}) is None and not S.is_proofs({"selector": {"rows": ["r"]}}),
          "a modcheck job is neither")
    refused(lambda: tier_job(sel={"rows": ["r1"]}), "a tier profile without proofs")
    refused(lambda: tier_job(sel={"proofs": ["A1"], "rows": ["r1"]}), "proofs beside modcheck rows")
    refused(lambda: tier_job(profile="targeted"), "proofs without a tier profile")
    refused(lambda: tier_job(lane="archmagi"), "a tier job on lane archmagi")
    refused(lambda: tier_job(lane="any"), "a tier job on lane any")
    refused(lambda: tier_job(item=None), "a tier job naming no item")
    refused(lambda: tier_job(profile="tier:Bad Tier"), "a malformed tier profile")
    sch = S.json_schema()
    check("proofs" in json.dumps(sch) and S.TIER_RE.pattern in json.dumps(sch), "the emitted schema names both")
    with open(S.SCHEMA_FILE, encoding="utf-8") as f:
        check(json.load(f) == json.loads(json.dumps(sch)), "testq_schema.json is the regenerated schema")


def t_proof_grammar():
    import relentless_live_round as LR
    text = ("live-proof A1: python.exe a.py < /dev/null\n- `live-proof B2: python3 b.py --x`\nlive-proof a3: no\n"
            "live-proof A1: second wins nothing\nlive-tier: x\n")
    check(S.proof_lines(text) == LR.proof_lines(text) and S.proof_lines(text) == {"A1": "python.exe a.py < /dev/null",
                                                                                    "B2": "python3 b.py --x"},
          "the worker parses proof lines as rimflow does: %s" % S.proof_lines(text))
    check(S.PROOF_LINE.pattern == LR.PROOF_LINE.pattern, "one pattern")


def tq(queue, *args):
    env = dict(os.environ, TESTQ_QUEUE=queue)
    r = subprocess.run([sys.executable, os.path.join(HERE, "testq.py")] + list(args), capture_output=True, text=True,
                       env=env, cwd=REPO, timeout=120, stdin=subprocess.DEVNULL)
    return r.returncode, (r.stdout + r.stderr).strip()


def t_submit(queue):
    base = ("submit", "VITALS_X", "--proofs", "A1", "--purpose", "fix", "--by", "RELENTLESS", "--sha", SHA,
            "--for-item", "VITALS_X", "--no-sha-check", "--lane", "stevedesktop")
    rc, out = tq(queue, *base, "--profile", "tier:ratchet_pilot")
    o = json.loads(out.splitlines()[-1]) if rc == 0 else {}
    check(rc == 0 and o.get("state") == "pending", "a tier proofs job is queued: %s" % out[-200:])
    rec = json.load(open(os.path.join(queue, "pending", o.get("job", "x") + ".json"))) if o.get("job") else {}
    check(rec.get("profile") == "tier:ratchet_pilot" and rec.get("selector") == {"proofs": ["A1"]}
          and rec.get("item") == "VITALS_X", "with its tier, its clause and its item: %s" % rec.get("selector"))
    rc2, out2 = tq(queue, *base, "--profile", "tier:ratchet_pilot")
    check(rc2 == 0 and json.loads(out2.splitlines()[-1]).get("duplicate") is True, "the same request is one job")
    rc3, out3 = tq(queue, *base, "--profile", "tier:no_such_tier_here")
    check(rc3 == 2 and "no modset_builder.py tier" in out3, "an unknown tier is refused at submit: %s" % out3[-120:])
    rc4, out4 = tq(queue, *base[:-2], "--lane", "archmagi", "--profile", "tier:ratchet_pilot")
    check(rc4 == 2 and "lane stevedesktop only" in out4, "and lane archmagi too: %s" % out4[-120:])
    return o.get("job")


def t_admission(queue):
    os.environ["TESTQ_QUEUE"] = queue
    import testq as T
    T.QHOME = queue
    a = dict(tier_job(), priority=50, submitted="2026-11-06T00:00:00Z")
    b = dict(tier_job(profile="tier:gizkastowaway"), priority=70, submitted="2026-11-06T00:00:01Z")
    m = dict(S.make_job("FlowWorks", {"rows": ["r1"]}, "fix", "BENCH", SHA), priority=75, submitted="2026-11-06T00:00:02Z")
    pick = lambda train, js=(a, b, m): sorted(js, key=lambda j: T.admit_key(j, train))[0]
    check(pick("tier:ratchet_pilot") is a, "on the ratchet_pilot train its job (50) goes first, past 70 and 75")
    check(pick("tier:gizkastowaway") is b, "on gizkastowaway, its own")
    check(pick("targeted") is m and pick(None) is m, "off a tier, priority leads as before")
    urgent = dict(m, priority=50 + T.TIER_STAY_BONUS + 10)
    check(pick("tier:ratchet_pilot", (a, b, urgent)) is urgent,
          "the stay is a bonus, not a wall: a job %d above the train still goes first" % (T.TIER_STAY_BONUS + 10))
    for d in ("pending",):
        os.makedirs(os.path.join(queue, d), exist_ok=True)
    os.environ["TESTQ_ARCHMAGI_PROFILES"] = "full-list,targeted,tier:ratchet_pilot"
    try:
        cands = T.archmagi_candidates(False, True)
    finally:
        os.environ.pop("TESTQ_ARCHMAGI_PROFILES", None)
    check(not [j for j in cands if S.tier_of(j)], "the Archmagi backfill takes no tier job: %s" % [j["id"] for j in cands])


def t_ingest():
    import ingest as I
    job = tier_job()
    rec = {"job": job, "result": {"attempt": job["id"] + ".a1", "outcome": "DONE", "cause": None,
                                  "rows": [{"chain": "proofs", "row": "A1", "verdict": "FAIL", "detail": "exit 1"}]}}
    called = []
    saved = I.rimflow
    I.rimflow = lambda *a: called.append(a)
    try:
        out = I.ingest_one(rec)
    finally:
        I.rimflow = saved
    check("skipped" in out and not called, "ingest leaves a proofs job to Relentless: %s %s" % (out, called))


def main():
    queue = tempfile.mkdtemp(prefix="testq_tier_")
    try:
        for name, t in (("schema", t_schema), ("grammar", t_proof_grammar)):
            print("--", name)
            t()
        print("-- submit")
        t_submit(queue)
        print("-- admission")
        t_admission(queue)
        print("-- ingest")
        t_ingest()
    finally:
        shutil.rmtree(queue, ignore_errors=True)
    print("selftest_testq_tier: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
