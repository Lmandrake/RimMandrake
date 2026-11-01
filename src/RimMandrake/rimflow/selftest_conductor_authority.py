#!/usr/bin/env python3
"""CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM stays made "everywhere": every rule file a seat or helper reads names the
ruling, and each tool gate that took only his typed words takes the ruling with the Conductor's text in --why, while a
bare agent reason and any other ruling are still refused."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UTILS = ROOT / "src/RimMandrake/Utils"
sys.path.insert(0, str(UTILS))
import conductor_authority as CA  # noqa: E402
import repair_torn_ledger as RTL  # noqa: E402

fails = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


FILES = ["CLAUDE.md", "design/RimMandrake/standing_rulings.md", "design/RimMandrake/delegation_policy.md",
         "infrastructure/agents/CHARTER.md", "infrastructure/agents/BENCH.md", "infrastructure/agents/CONDUCTOR.md",
         "infrastructure/agents/FOUNDRY.md"]
FILES += sorted(str(p.relative_to(ROOT)) for p in (ROOT / "src/RimMandrake/rimflow/roles").glob("*.md"))
FILES += sorted(str(p.relative_to(ROOT)) for p in (ROOT / ".claude/agents").glob("rm-*.md"))
check(len(FILES) >= 19, "the census sees the role and agent files (%d)" % len(FILES))
for f in FILES:
    check(CA.RULING in (ROOT / f).read_text(encoding="utf-8"), f + " names the ruling")

check(CA.carried(CA.RULING, "do it"), "the ruling with the Conductor's text is carried")
check(not CA.carried(CA.RULING, "  "), "the ruling without the Conductor's text is not")
check(not CA.carried("SOME_OTHER_RULING", "do it"), "another ruling is not")
check(not CA.carried(None, "do it"), "a bare agent reason is not")



# The parsers, on a nonexistent sha: a refused-by-authority line must not appear when the route is taken.
for verb in ("unpurge", "unban"):
    h = subprocess.run([sys.executable, str(UTILS / "art/art.py"), verb, "-h"], capture_output=True, text=True)
    check("--per-ruling" in h.stdout and "--why" in h.stdout, "art.py %s takes --per-ruling and --why" % verb)
h = subprocess.run([sys.executable, str(UTILS / "slot_allocator.py"), "set", "--n", "3", "--why", "my reason"],
                   capture_output=True, text=True, env=dict(os.environ))
check(h.returncode == 2 and CA.RULING in h.stderr, "slot_allocator set refuses a bare reason and names the route")
with tempfile.TemporaryDirectory() as tmp:
    h = subprocess.run([sys.executable, str(UTILS / "slot_allocator.py"), "set", "--n", "3", "--hours", "1", "--per-ruling",
                        CA.RULING, "--why", "run three"], capture_output=True, text=True,
                       env=dict(os.environ, RM_STREAMS_DIR=tmp))
    ov = Path(tmp) / "slot_override.json"
    check(h.returncode == 0 and ov.exists() and CA.RULING in ov.read_text(encoding="utf-8"),
          "slot_allocator set takes the Conductor's instruction and says so on the override")

with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp) / "shard.jsonl"
    p.write_text('{"a": 1}\n{torn\n', encoding="utf-8")
    bak = Path(tmp) / "bak"
    with contextlib.redirect_stdout(io.StringIO()):
        rc = RTL.repair(p, apply=True, owner_said=None, backup_dir=bak, why="my reason")
    check(rc == 1, "repair_torn_ledger --apply refuses a bare reason")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = RTL.repair(p, apply=True, owner_said=None, backup_dir=bak, per_ruling=CA.RULING, why="repair it")
    check(rc == 0 and CA.RULING in out.getvalue(), "repair_torn_ledger --apply takes the Conductor's instruction")

check("CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM" in (ROOT / "src/RimMandrake/rimflow/model.py").read_text(encoding="utf-8"),
      "the seat refusal names the Conductor's route")
print("%d failure(s)" % len(fails))
sys.exit(1 if fails else 0)
