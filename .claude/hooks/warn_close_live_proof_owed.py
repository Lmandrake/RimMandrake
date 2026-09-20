#!/usr/bin/env python3
"""PreToolUse/Bash hook — warn when a `rimflow close` names live-proof debt in
the commit and spawns no successor to carry it. CLOSE_OWED_LIVE_PROOF_1.

WHY
===
A close whose evidence is entirely offline (`dotnet build`, `validate_patch`,
selftests) is a legitimate close, and the debt it still owes — a deploy, a
live-game proof, "follow-on work" — is real and honestly named... in the
commit message. No queue, dashboard or `rimflow next` ever reads a commit
body, so the moment the session ends nobody is looking for it. MEASURED
2026-09-20 against two real closes (`ALPHA_MECHANICS_KIT_1`,
`BRAINWORM_MOD_BUILD_1`) that both told the truth in prose nothing durable
then read; the whole-ledger sweep in `live_proof_lint.py` found 5 such closes
with no successor, ever.

The fix already exists and was simply never reached for at close time:

    rimflow spawn --from <this item> --for <seat> --name <SUCCESSOR_ID>

WARN, NOT REFUSE — the item's own spec, verbatim: "the honest wording is the
signal, and a hook that punishes it would teach seats to stop writing it,
which is strictly worse than the defect." This never blocks a close. Same
contract as `warn_unclosed_queue_item.py`: exit 1 is a non-blocking notice
(stderr shown, command still runs); exit 2 is the only code that gates, and
this file never returns it.

WHAT IT CHECKS
==============
A Bash command that runs `rimflow/cli.py ... close <ID> [--sha SHA]`. The sha
(explicit, or HEAD if omitted — matching `cmd_close`'s own default) names a
commit whose body is checked against the four phrases from the item's spec.
If it matches and the ledger has no `spawn` event anywhere naming this ID (or
a run under it) as `from`, warn and name the exact command to run.

⚠️ Runs BEFORE the close lands, so "the ledger has no spawn" is read from the
CURRENT file — exactly the question that matters: has this sitting already
spawned the successor, as the rule asks, before closing?
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "src", "RimMandrake", "rimflow"))
try:
    import live_proof_lint as lpl
except ImportError:
    lpl = None


CLOSE_CMD_RE = re.compile(
    r"rimflow[/\\]cli\.py['\"]?\s+close\b")
ID_RE = re.compile(r"\bclose\s+['\"]?([A-Za-z][A-Za-z0-9._-]*)")
SHA_RE = re.compile(r"--sha[= ]\s*['\"]?([0-9a-fA-F]{4,40})")


def git(root, *args):
    import subprocess
    try:
        p = subprocess.run(["git", "-C", root, *args], capture_output=True,
                           text=True, timeout=8)
    except Exception:                                   # noqa: BLE001
        return None
    return p.stdout.strip() if p.returncode == 0 else None


def main():
    if lpl is None:
        return 0                      # fail open: cannot import the detector
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return 0
    cmd = (ev.get("tool_input") or {}).get("command") or ""
    if not CLOSE_CMD_RE.search(cmd):
        return 0
    m = ID_RE.search(cmd)
    if not m:
        return 0
    iid = m.group(1)

    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    m = SHA_RE.search(cmd)
    sha = m.group(1) if m else git(root, "rev-parse", "--short", "HEAD")
    if not sha:
        return 0

    body = lpl.commit_body(root, sha)
    phrase = lpl.matched_phrase(body)
    if not phrase:
        return 0

    ledger = os.path.join(root, "infrastructure", "state", "ledger", "events.jsonl")
    froms = lpl.spawn_froms(ledger)
    if lpl.has_spawned_successor(iid, froms):
        return 0

    print(
        "⚠️  %s's commit (%s) says %r, and no `rimflow spawn` names it as `from`.\n\n"
        "That debt only lives in the commit message right now — no queue, dashboard\n"
        "or `rimflow next` will ever look for it again once this session ends.\n"
        "CLOSE_OWED_LIVE_PROOF_1's rule: spawn the successor in this sitting, BEFORE\n"
        "the close, so the debt survives it:\n\n"
        "    python3 src/RimMandrake/rimflow/cli.py spawn --from %s --for <SEAT> \\\n"
        "      --name <NEW_ID> --kind task --spec \"<what live proof is still owed>\"\n\n"
        "This is a notice, not a refusal — the close will still go through."
        % (iid, sha, phrase, iid), file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)                   # fail open, never gate on a crash
