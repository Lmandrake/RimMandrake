#!/usr/bin/env python3
"""selftest_audit_hardflag_file.py - audit_hardflag_file.py, the no-AI filer of the Auditor pre-screen's hard flags
(item AUDITOR_BUILD_HARD_FLAG_FILER_NO_AI). Temp files and an injected filer only: never writes the ledger or
D:\\ClaudeWork."""
import io, json, os, sys, tempfile, time
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rimflow import audit_hardflag_file as hf  # noqa: E402

FAILED = []


def ok(name, got, want):
    if got != want:
        FAILED.append(name)
        print("FAIL %s: got %r want %r" % (name, got, want))
    else:
        print("ok   %s" % name)


NOW = time.time()
ISO = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))
CONF = hf.load_conf()


def doc(rows, gen=NOW - 60):
    return {"generated": ISO(gen), "closes_seen": len(rows), "ranked": rows,
            "hard_flagged": [r["item"] for r in rows if r["hard"]]}


R1 = {"item": "WIDGET_FIX_LOOSE_BOLT", "sha": "HEAD", "closed_by": "FOUNDRY", "flags": ["sha_head_literal", "many_files"],
      "hard": ["sha_head_literal"]}
R2 = {"item": "GADGET_BUILD_SPRING", "sha": "abc1234", "closed_by": "BENCH", "flags": ["no_check_evidence"], "hard": []}
R3 = {"item": "LEGACY_THING_WIRE_UP", "sha": "", "closed_by": "BUILD", "flags": ["sha_missing"], "hard": ["sha_missing"]}
OWNERS = {"WIDGET_FIX_LOOSE_BOLT": "FOUNDRY", "GADGET_BUILD_SPRING": "BENCH", "LEGACY_THING_WIRE_UP": "BUILD"}

# config: every setting carries a _why
ok("config has a _why", bool(CONF.get("_why")), True)
for k in ("max_prescreen_age_s", "work_seats", "fallback_for", "kind", "needs", "name_prefix"):
    ok("config has " + k, k in CONF, True)

# plan: only rows with hard flags; the owner seat when it is a work seat, else the fallback
todo, have = hf.plan(doc([R1, R2, R3]), [], OWNERS, CONF, set())
ok("one ticket per hard-flagged row", sorted(t["item"] for t in todo), ["LEGACY_THING_WIRE_UP", "WIDGET_FIX_LOOSE_BOLT"])
by = {t["item"]: t for t in todo}
ok("ticket for the owning work seat", by["WIDGET_FIX_LOOSE_BOLT"]["for"], "FOUNDRY")
ok("retired owner seat -> fallback", by["LEGACY_THING_WIRE_UP"]["for"], CONF["fallback_for"])
ok("marker names item and sha", hf.marker("WIDGET_FIX_LOOSE_BOLT", "HEAD") in by["WIDGET_FIX_LOOSE_BOLT"]["why"], True)
ok("empty sha marker is '-'", hf.marker("X", ""), "[hardflag X@-]")
ok("names pass mint rules", all(not hf._model().mint_problems(t["name"], set()) for t in todo), True)
ok("name is deterministic", hf.plan(doc([R1]), [], OWNERS, CONF, set())[0][0]["name"], by["WIDGET_FIX_LOOSE_BOLT"]["name"])
ok("caused_by is the flagged item", by["WIDGET_FIX_LOOSE_BOLT"]["caused_by"], "WIDGET_FIX_LOOSE_BOLT")

# dedupe against the LEDGER: a file event caused_by the item whose why carries the marker
prior = [{"event": "file", "id": by["WIDGET_FIX_LOOSE_BOLT"]["name"], "caused_by": "WIDGET_FIX_LOOSE_BOLT",
          "why": by["WIDGET_FIX_LOOSE_BOLT"]["why"]}]
todo2, have2 = hf.plan(doc([R1, R3]), prior, OWNERS, CONF, {prior[0]["id"]})
ok("already-filed (item, sha) is not refiled", [t["item"] for t in todo2], ["LEGACY_THING_WIRE_UP"])
ok("already-filed is reported", [h["item"] for h in have2], ["WIDGET_FIX_LOOSE_BOLT"])
# a NEW sha on the same item is a new defect
todo3, _ = hf.plan(doc([dict(R1, sha="deadbee", hard=["sha_unresolvable"])]), prior, OWNERS, CONF, {prior[0]["id"]})
ok("same item, new sha -> filed", len(todo3), 1)
ok("its name avoids the taken one", todo3[0]["name"] != prior[0]["id"], True)
# a file event with the marker but caused_by another item does not count
todo4, _ = hf.plan(doc([R1]), [dict(prior[0], caused_by="OTHER")], OWNERS, CONF, {prior[0]["id"]})
ok("marker on another item's ticket does not dedupe", len(todo4), 1)

# fail closed: missing, torn, stale, or shapeless pre-screen -> exit 2 and no filing
d = tempfile.mkdtemp()
calls = []


def filer(t, seat):
    calls.append(t["name"])
    return 0, "filed"


def run(path, events=(), owners=OWNERS, f=filer, out=None):
    out = out or os.path.join(d, "hardflag_filed.json")
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as e:
        rc = hf.main(["--prescreen", path, "--out", out, "--seat", "BENCH", "--no-prose"],
                     events=list(events), owners=owners, filer=f)
    return rc, e.getvalue()


ok("missing pre-screen -> 2", run(os.path.join(d, "nope.json"))[0], 2)
p = os.path.join(d, "prescreen.json")
open(p, "w").write("{torn")
ok("torn pre-screen -> 2", run(p)[0], 2)
json.dump(doc([R1], gen=NOW - CONF["max_prescreen_age_s"] - 10), open(p, "w"))
ok("stale pre-screen -> 2", run(p)[0], 2)
json.dump({"generated": ISO(NOW)}, open(p, "w"))
ok("pre-screen without ranked -> 2", run(p)[0], 2)
json.dump(dict(doc([R1]), ranked=[{"item": "X", "sha": "", "flags": []}]), open(p, "w"))
ok("row without hard -> 2", run(p)[0], 2)
json.dump(dict(doc([R1]), hard_flagged=["SOMETHING_ELSE"]), open(p, "w"))
ok("hard_flagged disagrees with rows -> 2", run(p)[0], 2)
ok("nothing filed on any refusal", calls, [])

# the happy path writes the record the Auditor confirms against
json.dump(doc([R1, R2, R3]), open(p, "w"))
out = os.path.join(d, "rec.json")
rc, err = run(p, out=out)
rec = json.load(open(out))
ok("ok run -> 0", rc, 0)
ok("both filed", len(calls), 2)
ok("record status OK", rec["status"], "OK")
ok("record lists filed", sorted(x["item"] for x in rec["filed"]), ["LEGACY_THING_WIRE_UP", "WIDGET_FIX_LOOSE_BOLT"])
ok("record names its pre-screen stamp", rec["prescreen_generated"], doc([])["generated"])

# a failing filing is loud and recorded, but never costs the audit (exit 0, status PARTIAL)
calls.clear()
rc, err = run(p, out=out, f=lambda t, s: (1, "refused: boom"))
rec = json.load(open(out))
ok("failed filing -> exit 0 (the Auditor still runs)", rc, 0)
ok("failed filing -> status PARTIAL", rec["status"], "PARTIAL")
ok("failed rows listed", len(rec["failed"]), 2)
ok("failed filing said on stderr", "FAILED" in err, True)

# zero hard flags: a record still lands, saying so
json.dump(doc([R2]), open(p, "w"))
rc, _ = run(p, out=out)
rec = json.load(open(out))
ok("no hard flags -> 0, OK, empty", (rc, rec["status"], rec["filed"]), (0, "OK", []))

# LIVE wiring: the Auditor's pre_launch runs the filer right after the pre-screen (removing it fails here)
sch = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dispatcher_schedule.json")))
aud = [r for r in sch["roles"] if r.get("name") == "Auditor"][0]
steps = [" ".join(s) for s in aud["pre_launch"]]
pi = [i for i, s in enumerate(steps) if s.endswith("audit_prescreen.py")]
fi = [i for i, s in enumerate(steps) if s.endswith("audit_hardflag_file.py")]
ok("Auditor pre_launch runs the filer after the pre-screen", bool(pi and fi and fi[0] == pi[0] + 1), True)

print("\n%s: %d failed" % ("FAIL" if FAILED else "PASS", len(FAILED)))
sys.exit(1 if FAILED else 0)
