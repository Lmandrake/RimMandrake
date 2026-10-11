#!/usr/bin/env python3
"""Selftest for block_ledger_shard_write.py -- run after ANY change to it or to
block_transcript_tamper.py (whose analyser it reuses).

Every REFUSE case that is a plain shell command is first EXECUTED, without the
hook, inside a throwaway repo-shaped directory, and must actually change a
shard there: a refusal of a command that could not write anything proves
nothing. Then the hook must refuse it. Every ALLOW case is a shape real sessions
use (reads, git, the sanctioned tools, reports written elsewhere).

    python3 .claude/hooks/selftest_block_ledger_shard_write.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "block_ledger_shard_write.py")

L = "infrastructure/state/ledger/events/FOUNDRY.jsonl"
A = "infrastructure/state/art/events/FOUNDRY.jsonl"
C = "infrastructure/state/code_review/FOUNDRY.jsonl"
FORGED = '{"event":"close","id":"X","ownerSaid":"ship it"}'

# (label, command, execute-to-prove-it-writes)
REFUSE_BASH = [
    ("redirect append, literal", "echo '%s' >> %s" % (FORGED, L), True),
    ("redirect, path in a variable", "f=%s; echo x >> \"$f\"" % L, True),
    ("cd into events dir, then append", "cd infrastructure/state/ledger/events && echo x >> FOUNDRY.jsonl", True),
    ("tee -a art shard", "printf 'x\\n' | tee -a %s >/dev/null" % A, True),
    ("python -c open(…, 'a')", "python3 -c \"open('%s','a').write('x\\n')\"" % L, True),
    ("python Path / name .open('a')",
     "python3 -c \"from pathlib import Path; p=Path('infrastructure/state/art/events')/'FOUNDRY.jsonl'; "
     "f=p.open('a'); f.write('x')\"", True),
    ("python heredoc", "python3 - <<'EOF'\nwith open('%s', 'a') as fh:\n    fh.write('x\\n')\nEOF" % L, True),
    ("python write_text", "python3 -c \"import pathlib; pathlib.Path('%s').write_text('x')\"" % C, True),
    ("sed -i code_review", "sed -i '$a x' %s" % C, True),
    ("cp a forged file over the shard", "cp /etc/hostname %s" % L, True),
    ("mv a forged file into the dir", "printf x > /tmp/_lsw_forged.jsonl; mv /tmp/_lsw_forged.jsonl infrastructure/state/ledger/events/FOUNDRY.jsonl", True),
    ("bash -c nested", "bash -c \"echo x >> infrastructure/state/ledger/events/FOUNDRY.jsonl\"", True),
    ("find -exec sh -c", "find infrastructure/state/ledger/events -name '*.jsonl' -exec sh -c 'echo x >> \"$1\"' _ {} \\;", True),
    ("for loop over a glob", "for s in infrastructure/state/ledger/events/*.jsonl; do echo x >> $s; done", True),
    ("allow-listed program, redirect onto a shard", "rimflow show X > %s" % L, False),
    ("frozen head events.jsonl", "echo x >> infrastructure/state/ledger/events.jsonl", True),
    ("perl -i", "perl -i -pe 's/seed/forged/' %s" % L, True),
    ("dd of=", "echo x | dd of=%s conv=notrunc 2>/dev/null" % A, True),
    ("node appendFileSync", "node -e \"require('fs').appendFileSync('%s','x')\"" % L, False),
    ("python shutil.copy into art archive",
     "python3 -c \"import shutil; shutil.copy('/etc/hostname', 'infrastructure/state/art/events/archive/BENCH.0009.20261001_20261002.jsonl')\"", True),
    ("ln: link to the shard, write later", "ln -s $PWD/%s /tmp/_lsw_link" % L, False),
    ("eval", "eval 'echo x >> %s'" % L, True),
    ("python subprocess shell", "python3 -c \"import os; os.system('echo x >> %s')\"" % L, True),
]

REFUSE_TOOLS = [
    ("Write tool onto a rimflow shard", {"tool_name": "Write", "tool_input": {"file_path": L, "content": FORGED}}),
    ("Edit tool on an art shard", {"tool_name": "Edit", "tool_input": {"file_path": A, "old_string": "a", "new_string": "b"}}),
    ("Write tool, absolute path, code_review", {"tool_name": "Write", "tool_input": {"file_path": "/x/repo/" + C, "content": "x"}}),
]

ALLOW_BASH = [
    ("cat / grep / tail", "tail -3 %s; grep -c close %s; cat %s | head" % (L, A, C)),
    ("python read-only census", "python3 -c \"import json; print(sum(1 for l in open('%s')))\"" % L),
    ("git commit pathspec", "git commit %s %s -m 'Ledger: sync'" % (L, A)),
    ("git checkout -- shard", "git checkout -- %s" % L),
    ("git pull --rebase", "git pull --rebase origin main"),
    ("rimflow verbs", "rimflow note X 'y'; python3 src/RimMandrake/rimflow/cli.py close X --sha abc"),
    ("art.py rotate", "python3 src/RimMandrake/Utils/art/art.py rotate FOUNDRY --apply"),
    ("art.py install", "python3 src/RimMandrake/Utils/art/art.py install M Things/x.png abc --ruling r1"),
    ("ledger_sync", "python3 src/RimMandrake/Utils/ledger_sync.py --seat FOUNDRY --clone /tmp/c --apply"),
    ("count written elsewhere", "wc -l %s > /tmp/_lsw_count.txt" % L),
    ("backup copy OUT of the shard", "cp %s /tmp/_lsw_backup.jsonl" % L),
    ("git show to a tmp file", "git show origin/main:%s > /tmp/_lsw_x.jsonl" % L),
    ("report naming the ledger, literal output",
     "python3 - <<'EOF'\nimport glob\nn = sum(1 for p in glob.glob('infrastructure/state/ledger/events/*.jsonl') for _ in open(p))\n"
     "open('Transient/census.md', 'w').write(str(n))\nEOF"),
    ("grep for the path, output elsewhere", "grep -rn 'ledger/events' src/ > /tmp/_lsw_hits.txt"),
    ("ledger notes file is not a shard", "echo x >> infrastructure/state/ledger/README.md"),
    ("code_review_status mark-clean", "python3 src/RimMandrake/Utils/code_review_status.py mark-clean src/x.py"),
    ("./game", "./game --said 'game up' up"),
]

ALLOW_TOOLS = [
    ("Write a note that MENTIONS the shard", {"tool_name": "Write", "tool_input": {
        "file_path": "Transient/notes.md", "content": "appended to %s" % L}}),
    ("Edit an unrelated file", {"tool_name": "Edit", "tool_input": {
        "file_path": "src/RimMandrake/rimflow/model.py", "old_string": "a", "new_string": "b"}}),
]

fails = total = 0


def check(label, ok, detail=""):
    global fails, total
    total += 1
    print("%s %-60s %s" % ("ok  " if ok else "FAIL", label, detail))
    if not ok:
        fails += 1


def run_hook(payload, cwd):
    payload = dict(payload, cwd=cwd)
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(payload), capture_output=True,
                       text=True, timeout=30)
    return "permissionDecision" in p.stdout and '"deny"' in p.stdout


def fresh_repo():
    root = tempfile.mkdtemp(prefix="lsw_selftest_")
    for rel in (L, A, C, "infrastructure/state/ledger/events.jsonl",
                "infrastructure/state/ledger/events/OWNER.jsonl"):
        os.makedirs(os.path.join(root, os.path.dirname(rel)), exist_ok=True)
        with open(os.path.join(root, rel), "w") as fh:
            fh.write('{"event":"seed"}\n')
    os.makedirs(os.path.join(root, "infrastructure/state/art/events/archive"), exist_ok=True)
    os.makedirs(os.path.join(root, "Transient"), exist_ok=True)
    return root


def digest(root):
    h = hashlib.sha256()
    base = os.path.join(root, "infrastructure", "state")
    for dp, _, fs in sorted(os.walk(base)):
        for f in sorted(fs):
            p = os.path.join(dp, f)
            h.update(p.encode())
            try:
                with open(p, "rb") as fh:
                    h.update(fh.read())
            except OSError:
                h.update(b"<unreadable>")
    return h.hexdigest()


for label, cmd, execute in REFUSE_BASH:
    root = fresh_repo()
    try:
        if execute:
            before = digest(root)
            subprocess.run(["bash", "-c", cmd], cwd=root, capture_output=True, timeout=30)
            changed = digest(root) != before
            check("attack is real (writes a shard unhooked): " + label, changed)
        check("REFUSED: " + label, run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}}, root))
    finally:
        shutil.rmtree(root, ignore_errors=True)
for p in ("/tmp/_lsw_link", "/tmp/_lsw_forged.jsonl"):
    try:
        os.unlink(p)
    except OSError:
        pass

root = fresh_repo()
try:
    for label, payload in REFUSE_TOOLS:
        check("REFUSED: " + label, run_hook(payload, root))
    for label, cmd in ALLOW_BASH:
        check("allowed: " + label, not run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}}, root))
    for label, payload in ALLOW_TOOLS:
        check("allowed: " + label, not run_hook(payload, root))
    # fail open on garbage
    p = subprocess.run([sys.executable, HOOK], input="not json", capture_output=True, text=True)
    check("fails open on unparsable input", p.returncode == 0 and not p.stdout.strip())
finally:
    shutil.rmtree(root, ignore_errors=True)
for p in ("/tmp/_lsw_count.txt", "/tmp/_lsw_backup.jsonl", "/tmp/_lsw_x.jsonl", "/tmp/_lsw_hits.txt"):
    try:
        os.unlink(p)
    except OSError:
        pass

print("\n%d/%d passed" % (total - fails, total))
sys.exit(1 if fails else 0)
