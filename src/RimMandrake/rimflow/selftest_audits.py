#!/usr/bin/env python3
"""selftest_audits.py - audits.py: the Auditor's audits.jsonl schema, ensure, idempotent append, waiting index
(item AUDITOR_BUILD_AUDITS_FILE). Temp files only; never touches D:\\ClaudeWork."""
import io, json, os, sys, tempfile
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rimflow import audits  # noqa: E402

FAILED = []


def ok(name, got, want):
    if got != want:
        FAILED.append(name)
        print("FAIL %s: got %r want %r" % (name, got, want))
    else:
        print("ok   %s" % name)


def quiet(fn, *a):
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        return fn(*a)


L = {"ts": "2026-10-27T00:00:00Z", "item": "A", "sha": "abc1234", "run": "rm-role-auditor-1", "why_picked": "rank",
     "flags": ["many_files"], "verdict": "SOUND", "defect_class": None, "evidence": []}

# the schema holds the waiting index and the idempotency key; the module reads them from it
sch = audits.schema()
ok("schema names the idempotency key", sch["x-idempotency-key"], ["item", "sha", "run"])
ok("module key = schema key", audits.key_fields(), ("item", "sha", "run"))
ok("schema has waiting_for and the waiting index", ("waiting_for" in sch["properties"], "x-waiting-index" in sch),
   (True, True))
ok("run is required", "run" in sch["required"], True)

# problems(): one per broken rule, [] for a valid line
ok("valid SOUND", audits.problems(L), [])
ok("valid DEFECT", audits.problems(dict(L, verdict="DEFECT", defect_class="check")), [])
ok("valid waiting", audits.problems(dict(L, verdict="UNRESOLVED", waiting_for="/mnt/d/x.json")), [])
for name, d in (("no run", {k: v for k, v in L.items() if k != "run"}), ("bad verdict", dict(L, verdict="sound")),
                ("bad why", dict(L, why_picked="vibes")), ("HEAD sha", dict(L, sha="HEAD")),
                ("flags not list", dict(L, flags="x")), ("evidence item not str", dict(L, evidence=[1])),
                ("DEFECT without class", dict(L, verdict="DEFECT")),
                ("SOUND with class", dict(L, defect_class="check")),
                ("waiting_for on SOUND", dict(L, waiting_for="x")), ("empty item", dict(L, item="")),
                ("not an object", ["A"])):
    ok("refused: " + name, bool(audits.problems(d)), True)

d = tempfile.mkdtemp()
p = os.path.join(d, "auditor", "audits.jsonl")
# a missing file is UNMEASURED for every reader
try:
    audits.read(p)
    ok("missing file raises", "no raise", "OSError")
except OSError:
    ok("missing file raises", "OSError", "OSError")
ok("check on a missing file exits 2", quiet(audits.main, ["check", "--path", p]), 2)

# ensure: creates (folder too), then idempotent, never truncates
ok("ensure creates", audits.ensure(p), "created")
ok("created empty", os.path.getsize(p), 0)
ok("empty file = no audits", audits.read(p), [])
ok("ensure again: exists", audits.ensure(p), "exists")
ok("ensure CLI exits 0", quiet(audits.main, ["ensure", "--path", p]), 0)

# append: validated, idempotent by (item, sha, run)
ok("append writes", audits.append(L, p), True)
ok("same key again refused", audits.append(dict(L, ts="2026-10-27T01:00:00Z"), p), False)
ok("other run, same item+sha written", audits.append(dict(L, run="rm-role-auditor-2"), p), True)
try:
    audits.append(dict(L, run="r3", verdict="nope"), p)
    ok("schema-breaking append refused", "written", "ValueError")
except ValueError:
    ok("schema-breaking append refused", "ValueError", "ValueError")
ok("two lines on disk", len(audits.read(p)), 2)
size = os.path.getsize(p)
ok("ensure never truncates", (audits.ensure(p), os.path.getsize(p)), ("exists", size))

# waiting index: a wait ends only with a LATER SOUND/DEFECT for the same item+sha
W = dict(L, item="B", run="r1", verdict="UNRESOLVED", waiting_for="/mnt/d/proof.json")
rows = [W, dict(W, run="r2", waiting_for=None),                         # a later UNRESOLVED settles nothing
        dict(W, item="C"), dict(W, item="C", run="r2", verdict="DEFECT", waiting_for=None, defect_class="module"),
        dict(W, item="D", run="r9", verdict="SOUND", waiting_for=None), dict(W, item="D", run="r10")]
ok("waiting: B (no settler), D (settler came BEFORE the wait)", [r["item"] for r in audits.waiting(rows)], ["B", "D"])
ok("past_failed = DEFECT items", audits.past_failed(rows), {"C"})

# a torn line is UNMEASURED, and ensure reports it rather than papering over it
with open(p, "a") as f:
    f.write('{"item": "X", "verd')
ok("torn line: check exits 2", quiet(audits.main, ["check", "--path", p]), 2)
ok("torn line: ensure exits 2", quiet(audits.main, ["ensure", "--path", p]), 2)

print("FAILED: %s" % FAILED if FAILED else "all ok")
sys.exit(1 if FAILED else 0)
