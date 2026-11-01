#!/usr/bin/env python3
"""relentless_wall.py - what a mode may not see, as data, and the Marker's walled packet.

Design: relentless_agent_design_2026-11-01.md section 8. The profile lives in relentless_rules.json `walls`. A profile
with enforce false changes no launch: `audit` reports what it would have denied, from the runs' own tool calls.
The wall stops accident, not a hostile worker on the same host.

The Marker runs in a box: an exported tree with no .git, the supervisor's diff, a verdict script that writes only into
the box, and its own transcript folder bound over the real one. Its env carries no store root.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

HOME = str(Path.home())
VERDICT_SCRIPT = '''#!/usr/bin/env python3
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
if len(sys.argv) != 3 or sys.argv[1].upper() not in ("PASS", "FAIL"):
    sys.exit('usage: verdict PASS|FAIL "what you ran and saw"')
with open(HERE + "/verdict.tmp", "w", encoding="utf-8") as f:
    json.dump({"word": sys.argv[1].upper(), "reasons": sys.argv[2], "at": time.time()}, f)
os.replace(HERE + "/verdict.tmp", HERE + "/verdict.json")
print("recorded")
'''


def profile(rules, mode="marker"):
    """-> the mode's profile, or None. A profile names what it denies; a missing mode walls nothing and says so."""
    return (rules.get("walls") or {}).get(mode)


def enforced(rules, mode="marker"):
    return bool((profile(rules, mode) or {}).get("enforce"))


def denied(prof, extra=()):
    """Every path the unit may not see. deny_children: each thing under a root, so a clone made tomorrow is walled too."""
    out = list(prof["deny"]) + list(extra)
    for root in prof.get("deny_children", ()):
        out += [str(p) for p in sorted(Path(root).iterdir()) if str(p) not in prof.get("tmpfs", ())]
    return sorted(set(out))


def props(prof, box, extra=()):
    """systemd properties. Shared scratch comes up empty. A missing denied path fails the launch: a typo must not unwall.
    The transcript folder is the box's: other runs' memory stays out, this run's stays in."""
    out = []
    for p in denied(prof, extra):
        out += ["-p", "InaccessiblePaths=" + p]
    for p in prof.get("tmpfs", ()):
        out += ["-p", "TemporaryFileSystem=" + p]
    return out + ["-p", "BindPaths=%s:%s/.claude/projects" % (Path(box, "projects"), HOME)]


def excludes(prof):
    return [":(exclude)" + p for p in prof["tree_exclude"]]


def make_box(prof, source, sha, nonce):
    """-> the box's path. Tree at sha with no .git and none of tree_exclude, the diff against sha's parent, the verdict script."""
    box = Path(prof["box_root"], nonce)
    tree = box / "tree"
    tree.mkdir(parents=True)
    (box / "projects").mkdir()
    ex = excludes(prof)
    a = subprocess.Popen(["git", "archive", "--format=tar", sha, "--", ".", *ex], cwd=source, stdout=subprocess.PIPE)
    x = subprocess.run(["tar", "-x", "-C", str(tree)], stdin=a.stdout, capture_output=True, timeout=500)
    a.stdout.close()
    if a.wait(timeout=60) or x.returncode:
        raise RuntimeError("export failed: %s" % x.stderr[-200:])
    d = subprocess.run(["git", "diff", "--no-renames", sha + "^", sha, "--", ".", *ex], cwd=source, capture_output=True,
                       timeout=300, check=True)
    (box / "change.diff").write_bytes(d.stdout)
    (box / "nonce").write_text(nonce, encoding="ascii")
    (box / "verdict").write_text(VERDICT_SCRIPT, encoding="utf-8")
    os.chmod(box / "verdict", 0o755)
    return str(box)


def remove_box(box):
    shutil.rmtree(box, ignore_errors=True)


def marker_prompt(st, text, box):
    """The checker's words, its way to the change and its way to a verdict being the box's."""
    c = st["candidate"]
    return "\n".join([
        "You are a blind checker. You did not do this work and you have no record of how it went. Your cwd is a clean "
        "export of commit %s, with no git history." % c["sha"],
        "Decide one thing: did this commit do what the item says, proven by running it? Run the proof yourself. Judge "
        "the contract against the item's words: a contract that is easier than the item is a FAIL. A proof that "
        "cannot run is a FAIL. Do not fix anything, do not push, do not touch the ledger.",
        "Then run exactly one of:",
        "  python3 %s/verdict PASS \"what you ran and saw\"" % box,
        "  python3 %s/verdict FAIL \"what is wrong, so the next worker can fix it\"" % box,
        "", "Contract: %s" % json.dumps(st["contract"]), "Evidence the commit names: %s" % c["evidence"][:1500],
        "See the change in: %s/change.diff" % box, "", "--- item ---", text])


def read_verdict(box):
    """-> {word, reasons, at}, or None. The box is the Marker's to write: only well-formed words pass."""
    try:
        v = json.loads(Path(box, "verdict.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(v, dict) or v.get("word") not in ("PASS", "FAIL"):
        return None
    return {"word": v["word"], "reasons": str(v.get("reasons") or ""), "at": float(v.get("at") or time.time())}


def would_deny(inputs, prof):
    """-> the denied paths a run's tool calls named. For enforce false: the wall's report."""
    hits = set()
    for inp in inputs:
        text = json.dumps(inp)
        hits.update(p for p in denied(prof) if p in text)
        hits.update(p for p in prof["tree_exclude"] if ("/" + p) in text or (" " + p) in text)
    return sorted(hits)


def audit(store, rules, sessions_of, inputs_of):
    """Report only. -> [{item, unit, would_deny}] for each check in the store that has a session."""
    prof = profile(rules)
    out = []
    for st in store.states():
        chk = st.get("check") or {}
        session = sessions_of(chk.get("run"))
        inputs = inputs_of(session) if session else None
        if inputs is not None:
            out.append({"item": st["item"], "unit": chk.get("unit"), "would_deny": would_deny(inputs, prof)})
    return out


PROBE = r'''
for p in "$@"; do
  if [ -d "$p" ]; then ls -A "$p" >/dev/null 2>&1 && echo "SEEN $p" || echo "DENIED $p"
  elif [ -e "$p" ] || [ -L "$p" ]; then cat "$p" >/dev/null 2>&1 && echo "SEEN $p" || echo "DENIED $p"
  else echo "ABSENT $p"; fi
done
env | grep -c '^RELENTLESS_ROOT=' | sed 's/^/ROOT_ENV /'
'''
