#!/usr/bin/env python3
"""selftest_gpt_consult_rounds.py -- GPT review rounds are metered and reported (GPT_CONSULT_MEASURE_COST_UNLOGGED).

    python3 src/RimMandrake/Utils/selftest_gpt_consult_rounds.py

A faked codex, a temp call log, receipts, yield log and key: nothing live is read or written.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
T = tempfile.mkdtemp(prefix="gcrounds_selftest_")
os.environ["RM_CLOSE_EVIDENCE_KEY"] = os.path.join(T, "close_evidence.key")
os.environ["RM_CONSULT_RECEIPTS"] = os.path.join(T, "receipts.jsonl")
os.environ["RM_CONSULT_ROUNDS"] = os.path.join(T, "rounds.jsonl")
os.environ["RM_GPT_CALL_LOG"] = os.path.join(T, "calls") + "/"
os.environ.pop("RM_CONSULT_ROUND", None)

import gpt_call_log  # noqa: E402
import gpt_consult as GC  # noqa: E402
import gpt_consult_rounds as GR  # noqa: E402

FAILED = []


def ok(name, got, want):
    if got == want:
        print("ok    %s" % name)
    else:
        print("FAIL  %s: got %r, want %r" % (name, got, want))
        FAILED.append(name)


GC.codex_image.CODEX_SCRATCH = Path(T) / "codex"
GC.codex_image.find_codex_cli = lambda: "/bin/true"
GC.codex_image.wsl_to_win = lambda p: str(p)
_real_run = GC.subprocess.run
ANSWER = {"text": "finding 1\n"}


class _Done:
    returncode = 0


def _fake_run(cmd, cwd=None, **kw):
    if ANSWER["text"] is None:
        class _TO:
            returncode = 124
        return _TO()
    Path(cmd[cmd.index("-o") + 1]).write_text(ANSWER["text"])
    kw["stdout"].write(b"tokens used\n1,234\n")
    return _Done()


src = Path(GC.ROOT) / "src" / "RimMandrake" / "Utils" / "gpt_consult_rounds.py"
GC.subprocess.run = _fake_run
try:
    rc1 = GC.main(["review", "-f", str(src), "-m", "m1", "--round", "PARSER_R1"])
    os.environ["RM_CONSULT_ROUND"] = "PARSER_R1"
    rc2 = GC.main(["again", "-m", "m1"])                           # round from the environment
    os.environ.pop("RM_CONSULT_ROUND")
    ANSWER["text"] = None
    rc3 = GC.main(["third", "-m", "m1", "--round", "PARSER_R2"])   # no answer: rc 1, still metered
    ANSWER["text"] = "x\n"
    rc4 = GC.main(["untagged", "-m", "m1"])
    try:
        GC.main(["bad", "--round", "has space"])
        bad_round = "accepted"
    except SystemExit as e:
        bad_round = e.code
finally:
    GC.subprocess.run = _real_run

ok("consults return", (rc1, rc2, rc3, rc4), (0, 0, 1, 0))
ok("a malformed --round is refused before any call", bad_round, 2)
calls, bad = gpt_call_log.read_records()
calls.sort(key=lambda c: c["t"])
ok("every call is metered, none unreadable", (len(calls), bad), (4, 0))
ok("each record names its round (flag, env, flag, none)", [c["round"] for c in calls],
   ["PARSER_R1", "PARSER_R1", "PARSER_R2", None])
ok("real tokens from the codex log", [c["tokens_used"] for c in calls], [1234, 1234, None, 1234])
ok("seconds are measured on every call", all(isinstance(c["secs"], (int, float)) for c in calls), True)
ok("answered is recorded", [c["answered"] for c in calls], [True, True, False, True])
ok("files inlined are named repo-relative", calls[0]["files"], ["src/RimMandrake/Utils/gpt_consult_rounds.py"])
ok("every call has its own job id, even in one process and second", len({c["job"] for c in calls}), 4)

# yield records
GR.write_yield("PARSER_R1", 3, strong=1, weak=2)
GR.write_yield("PARSER_R1", 4, strong=2, weak=1, repeated=1, note="recount")   # the last one wins
for args, name in [(("PARSER_R1", -1), "negative"), (("PARSER_R1", 2, 3), "strong>findings"),
                   (("bad name", 1), "bad round")]:
    try:
        GR.write_yield(*args)
        ok("yield refuses " + name, "accepted", "refused")
    except ValueError:
        ok("yield refuses " + name, "refused", "refused")
ys, ybad = GR.read_yields()
ok("last yield per round wins", (ys["PARSER_R1"]["findings"], ys["PARSER_R1"]["repeated"], ybad), (4, 1, 0))

# review records citing a round's job count toward its yield
reviews = GR.review_jobs([{"reviewer": {"kind": "external", "tool": "gpt_consult", "job": calls[0]["job"]}},
                          {"reviewer": {"kind": "external", "tool": "gpt_consult", "job": calls[0]["job"]}},
                          {"reviewer": {"kind": "self"}}, {"path": "x"}])
ok("review records are counted per job", reviews, {calls[0]["job"]: 2})
rows = GR.build_report(calls, ys, reviews)
by = {r["round"]: r for r in rows}
ok("one row per round plus untagged, untagged last", [r["round"] for r in rows], ["PARSER_R1", "PARSER_R2", GR.UNTAGGED])
r1 = by["PARSER_R1"]
ok("round cost", (r1["calls"], r1["answered"], r1["timeouts"], r1["tokens"], r1["tok_unmeasured"], r1["reviews"]),
   (2, 2, 0, 2468, 0, 2))
ok("round yield", r1["yield"], {"findings": 4, "strong": 2, "weak": 1, "repeated": 1, "note": "recount"})
r2 = by["PARSER_R2"]
ok("a timed-out call: no tokens counted, no yield invented", (r2["timeouts"], r2["tokens"], r2["tok_unmeasured"],
                                                               "yield" in r2), (1, 0, 1, False))
ok("--round filter", [r["round"] for r in GR.build_report(calls, ys, reviews, only="PARSER_R2")], ["PARSER_R2"])
ok("--days filter drops older calls", GR.build_report(calls, ys, reviews, since=calls[-1]["t"] + 1), [])

# legacy records (before rounds): no secs, no answered field
legacy = [{"t": 1.0, "job": "consult-old", "rc": 0, "out_tok_est": 10, "tokens_used": 5},
          {"t": 2.0, "job": "consult-old2", "rc": 124, "out_tok_est": 0, "tokens_used": None}]
lr = GR.build_report(legacy, {}, {})[0]
ok("legacy calls land untagged, a short/absent answer is unmeasured not unanswered, secs UNMEASURED",
   (lr["round"], lr["answered"], lr["ans_unmeasured"], lr["timeouts"], lr["secs_unmeasured"], lr["tokens"]),
   (GR.UNTAGGED, 1, 1, 1, 2, 5))
long_name = "A" * 30 + "_R1"
lt = GR._fmt(GR.build_report([dict(calls[0], round=long_name), dict(calls[0], round="A" * 30 + "_R2")], {}, {}))
ok("long round names print whole", (long_name in lt, ("A" * 30 + "_R2") in lt), (True, True))
text = GR._fmt(GR.build_report(calls + legacy, ys, reviews))
ok("printed report says UNMEASURED for a round with no yield", "UNMEASURED" in text.splitlines()[2], True)
ok("printed report shows the recorded yield", "4 (2/1/1)" in text.splitlines()[1], True)

# the CLI end to end on the temp stores
import io, contextlib  # noqa: E401,E402
GR._code_review_records = lambda: [{"reviewer": {"tool": "gpt_consult", "job": calls[0]["job"]}}]
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = GR.main(["report", "--json"])
out = json.loads(buf.getvalue())
ok("report --json runs on the real stores", (rc, [r["round"] for r in out["rows"]], out["rows"][0]["reviews"]),
   (0, ["PARSER_R1", "PARSER_R2", GR.UNTAGGED], 1))
ok("yield CLI refuses a bad count", GR.main(["yield", "--round", "PARSER_R3", "--findings", "1", "--weak", "2"]), 2)
try:
    GR.main(["report", "--days", "0"])
    days0 = "accepted"
except SystemExit as e:
    days0 = e.code
ok("report --days 0 is refused, not read as 'all time'", days0, 2)

print("\n%s" % ("ALL PASS" if not FAILED else "FAILED: %s" % FAILED))
sys.exit(1 if FAILED else 0)
