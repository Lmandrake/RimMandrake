#!/usr/bin/env python3
"""selftest_testq_schema.py - the job/result interface (testq/schema.py) accepts sound records and refuses bad ones."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schema as S  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def refused(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except S.SchemaError as e:
        return str(e)
    return None


def main():
    j = S.make_job("FlowWorks", {"chains": ["core_offline"]}, "fix", "BENCH", "5403169aab", item="SOME_ITEM_FIX_IT")
    check(S.JOB_ID_RE.match(j["id"]) and j["lane"] == "stevedesktop" and j["canary"], "make_job fills defaults")
    check(S.modcheck_args(j) == ["FlowWorks", "--chains", "core_offline", "--canary", "--validity", "--reuse", "on"],
          "a fix job asks modcheck for its chains with the gate on: %s" % S.modcheck_args(j))
    j2 = S.make_job("FlowWorks", {"rows": ["v2_O1", "v2_O2"]}, "commission", "BENCH", "5403169aab", canary=False)
    check(S.modcheck_args(j2)[-2:] == ["--reuse", "off"] and "--canary" not in S.modcheck_args(j2),
          "a commission job bypasses the known-good gate")
    check(refused(S.make_job, "FlowWorks", {}, "fix", "BENCH", "abc1234"), "an empty selector is refused")
    check(refused(S.make_job, "FlowWorks", {"full": True}, "fix", "BENCH", "abc1234"), "--full outside a sweep is refused")
    check(not refused(S.make_job, "FlowWorks", {"full": True}, "sweep", "BENCH", "abc1234"), "--full in a sweep is fine")
    check(refused(S.make_job, "Flow Works", {"chains": ["x"]}, "fix", "BENCH", "abc1234"), "a mod name with a space")
    check(refused(S.make_job, "FlowWorks", {"chains": ["x;rm"]}, "fix", "BENCH", "abc1234"), "a chain name with ;")
    check(refused(S.make_job, "FlowWorks", {"chains": ["x"]}, "fix", "BENCH", "HEAD"), "source_sha HEAD is refused")
    check(refused(S.make_job, "FlowWorks", {"chains": ["x"]}, "fix", "BENCH", "abc1234", colour="red"),
          "an unknown field is refused")
    check(refused(S.make_job, "FlowWorks", {"chains": ["x"]}, "fix", "BENCH", "abc1234", not_before="tomorrow"),
          "a non-ISO not_before is refused")
    check(abs(S.parse_ts("2026-10-25T12:00:00Z") - 1792929600) < 1, "parse_ts is UTC, not local time")

    summary = {"chains": [{"name": "core_offline", "components": [
        {"name": "v2_O1", "verdict": "PASS", "detail": "527 defs"},
        {"name": "v2_O2", "verdict": "fail", "detail": "x", "freshness": "reused@r7"}]}]}
    rows = S.rows_from_summary(summary)
    check([r["verdict"] for r in rows] == ["PASS", "FAIL"] and rows[1]["freshness"] == "reused@r7",
          "rows come from chain components, verdicts upper-cased, freshness kept")
    long_ = S.rows_from_summary({"chains": [{"name": "c", "components": [{"name": "r", "verdict": "fail", "detail": "d" * 2500}]}]})
    check(len(long_[0]["detail"]) == 2500, "a 2,500-char row detail is kept whole (the old 300 cap hid FAIL evidence)")
    res = {"schema": S.RESULT_SCHEMA, "job": j["id"], "attempt": j["id"] + ".a1", "outcome": "DONE", "cause": None,
           "rows": rows}
    check(not refused(S.validate_result, res), "a DONE result validates")
    check(refused(S.validate_result, dict(res, outcome="INVALID")), "a non-DONE result without a cause is refused")
    check(refused(S.validate_result, dict(res, attempt="other.a1")), "an attempt id not under the job is refused")
    import json
    committed = json.load(open(S.SCHEMA_FILE))
    check(committed == json.loads(json.dumps(S.json_schema())),
          "testq_schema.json is the committed form of schema.py (regenerate: python3 schema.py --emit)")
    jd, rd = committed["$defs"]["job"], committed["$defs"]["result"]
    check(set(jd["required"]) <= set(j) and set(j) <= set(jd["properties"]),
          "a made job carries every required key and only declared ones: %s" % sorted(set(j) - set(jd["properties"])))
    check(set(rd["required"]) <= set(res) and jd["properties"]["purpose"]["enum"] == list(S.PURPOSES)
          and rd["properties"]["cause"]["enum"] == list(S.CAUSES), "result keys and enums match the constants")
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
