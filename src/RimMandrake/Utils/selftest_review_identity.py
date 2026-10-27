#!/usr/bin/env python3
"""selftest_review_identity.py -- gpt_consult receipts and the mac'd review block (CODE_REVIEW_WIRE_REVIEWER_SEAT).

    python3 src/RimMandrake/Utils/selftest_review_identity.py

Temp key, temp receipts file, a faked codex: nothing live is read or written.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
T = tempfile.mkdtemp(prefix="revid_selftest_")
os.environ["RM_CLOSE_EVIDENCE_KEY"] = os.path.join(T, "close_evidence.key")
os.environ["RM_CONSULT_RECEIPTS"] = os.path.join(T, "receipts.jsonl")
for k in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_BRIDGE_SESSION_ID"):
    os.environ.pop(k, None)

import review_identity as RI  # noqa: E402

FAILED = []


def ok(name, got, want):
    if got == want:
        print("ok    %s" % name)
    else:
        FAILED.append(name)
        print("FAIL  %s\n      got  %r\n      want %r" % (name, got, want))


key = RI.ce._key(create=True)
H = RI.sha256_bytes(b"code v1\n")

# receipts
RI.write_receipt("consult-1", "m1", True, [("src/a.py", b"code v1\n")], rc=0)
RI.write_receipt("consult-2", "m1", False, [("src/a.py", b"code v1\n")], rc=1)
ok("a written receipt is found", (RI.find_receipt("consult-1") or {}).get("model"), "m1")
ok("an unknown job has no receipt", RI.find_receipt("consult-9"), None)
ok("the receipt covers the exact bytes it inlined", RI.receipt_covers(RI.find_receipt("consult-1"), "src/a.py", H), True)
ok("other bytes are not covered", RI.receipt_covers(RI.find_receipt("consult-1"), "src/a.py", "0" * 64), False)
ok("an unanswered job covers nothing", RI.receipt_covers(RI.find_receipt("consult-2"), "src/a.py", H), False)
with open(os.environ["RM_CONSULT_RECEIPTS"], "a") as f:     # a hand-written receipt (no valid mac)
    f.write(json.dumps({"job": "consult-forged", "answered": True, "files": [{"path": "src/a.py", "sha256": H}],
                        "mac": "0" * 64}) + "\n")
ok("a receipt with a bad mac is not found", RI.find_receipt("consult-forged"), None)

# the review block and identity()
os.environ["RIMFLOW_SEAT"] = "FOUNDRY"
os.environ["CLAUDE_CODE_BRIDGE_SESSION_ID"] = "session_01Rev"
blk = RI.review_block("src/a.py", H, {"kind": "self"})
os.environ.pop("RIMFLOW_SEAT")
os.environ.pop("CLAUDE_CODE_BRIDGE_SESSION_ID")
rec = dict({"path": "src/a.py", "sha256": H, "verdict": "clean", "seat": "FOUNDRY"}, **blk)
ok("self review by a whoami-sure seat", RI.identity(rec, key), ("self", "FOUNDRY", "session_01Rev"))
ok("no key: unknown", RI.identity(rec, None), ("unknown", "FOUNDRY", None))
ok("a record with no review block (old) is unknown",
   RI.identity({"path": "src/a.py", "sha256": H, "seat": "BENCH"}, key), ("unknown", "BENCH", None))
ok("a review block moved to other content is unknown", RI.identity(dict(rec, sha256="1" * 64), key)[0], "unknown")
ok("an edited reviewer is unknown",
   RI.identity(dict(rec, recorder=dict(rec["recorder"], seat="CHECK")), key)[0], "unknown")
blk = RI.review_block("src/a.py", H, {"kind": "self"}, recorder={"seat": "FOUNDRY", "seat_from": "--seat"})
ok("a self review whose seat was only given is asserted",
   RI.identity(dict(rec, **blk), key), ("asserted", "FOUNDRY", None))
blk = RI.review_block("src/a.py", H, {"kind": "agent", "seat": "CHECK", "session": "session_01C", "agent": None})
ok("an agent reviewer is the recorder's word: asserted", RI.identity(dict(rec, **blk), key),
   ("asserted", "CHECK", "session_01C"))
blk = RI.review_block("src/a.py", H, {"kind": "external", "tool": "gpt_consult", "job": "consult-1", "model": "m1"})
ok("an external review whose receipt covers the bytes", RI.identity(dict(rec, **blk), key),
   ("external", "gpt_consult:consult-1", None))
blk = RI.review_block("src/a.py", H, {"kind": "external", "tool": "gpt_consult", "job": "consult-2", "model": "m1"})
ok("an external review whose job never answered is only asserted", RI.identity(dict(rec, **blk), key)[0], "asserted")

# gpt_consult writes the receipt (codex faked: it writes the answer file)
import gpt_consult as GC  # noqa: E402
GC.codex_image.CODEX_SCRATCH = Path(T) / "codex"
GC.codex_image.find_codex_cli = lambda: "/bin/true"
GC.codex_image.wsl_to_win = lambda p: str(p)
_real_run = GC.subprocess.run


class _Done:
    returncode = 0


def _fake_run(cmd, cwd=None, **kw):
    Path(cmd[cmd.index("-o") + 1]).write_text("looks fine\n")
    return _Done()


src = Path(GC.ROOT) / "src" / "RimMandrake" / "Utils" / "review_identity.py"
GC.subprocess.run = _fake_run
try:
    rc = GC.main(["review this", "-f", str(src), "-m", "m2"])
finally:
    GC.subprocess.run = _real_run
lines = [json.loads(l) for l in open(os.environ["RM_CONSULT_RECEIPTS"]) if l.strip()]
last = lines[-1]
ok("gpt_consult answers", rc, 0)
ok("gpt_consult wrote a receipt naming its job", (last["job"].startswith("consult-"), last["model"], last["answered"]),
   (True, "m2", True))
ok("the receipt holds the repo-relative path and sha256 of the bytes inlined", last["files"],
   [{"path": "src/RimMandrake/Utils/review_identity.py", "sha256": RI.sha256_bytes(src.read_bytes())}])
ok("the receipt verifies", RI.find_receipt(last["job"]) is not None, True)

print("\n%s" % ("ALL PASS" if not FAILED else "FAILED: %s" % FAILED))
sys.exit(1 if FAILED else 0)
