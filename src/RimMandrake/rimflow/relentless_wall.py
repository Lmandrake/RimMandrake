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
import re
import shlex
import shutil
import subprocess
import time
from pathlib import Path

HOME = str(Path.home())
WORDS = ("PASS", "WEAK", "FAIL")
RULE = (   # both Marker prompts: the unwalled and the walled one must never differ in what the words mean
    "Decide one thing: did this commit do what the item says, proven by running it? Run the proof yourself. Judge "
    "the contract against the item's words: a contract that is easier than the item is a FAIL. A proof that "
    "cannot run is a FAIL. Do not fix anything, do not push, do not touch the ledger.",
    "One case is not a FAIL: the work holds and only the proof is short. If you think a clause is unproven or the "
    "contract skipped it, run that clause yourself against the code. Your run shows the clause is done: that is WEAK. "
    "Your run shows it is not done, or you cannot show it either way: that is FAIL.",
    "A gap must be in the item's own words: the mutant breaks something a clause of the item asks for. A mutant of an "
    "inner detail, or of an edge the item never named, is no gap, and every test has those.",
    "PASS: every clause of the item is done, you ran it, and you found no gap in the proof that you could show. "
    "WEAK: every clause is done, shown by your own runs, and you can show a gap: a mutant that stays green, or a "
    "clause the proof never reaches. A weak proof is not a pass: the item stays open and the next worker strengthens "
    "the proof without touching the code. FAIL: a clause is not done, or the proof is red or cannot run. A gap you "
    "only suspect and did not show is no gap. Look for a clause that is missing before you look for a thin test.",
    "If you say WEAK, begin the reasons with GAP:DIFF when a gap you showed is a part of this commit's own change "
    "that you put back as it was before the commit while the proof stayed green, and that part does what a clause "
    "asks; begin with GAP:OTHER when every gap you showed is something else, such as a mutant you wrote yourself.")
SHADOW = "narrow_weak_1"   # RELENTLESS_WEAK_MEASURE_PASS_COLLAPSE: what the narrower WEAK would have said, recorded only


def narrow_word(word, reasons):
    """The verdict under the narrower WEAK: a gap counts only when it is a hunk of this commit's own diff. Shadow only:
    nothing acts on it. A WEAK with no tag is UNTAGGED, never guessed."""
    if word != "WEAK":
        return word
    head = (reasons or "").lstrip().upper()
    return "WEAK" if head.startswith("GAP:DIFF") else "PASS" if head.startswith("GAP:OTHER") else "UNTAGGED"
VERDICT_SCRIPT = '''#!/usr/bin/env python3
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
if len(sys.argv) != 3 or sys.argv[1].upper() not in ("PASS", "WEAK", "FAIL"):
    sys.exit('usage: verdict PASS|WEAK|FAIL "what you ran and saw"')
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


def skill_targets(prof):
    """-> the real paths the Marker's skill symlinks point at, when the profile names a skills folder. These are read only."""
    root = prof.get("allow_read_skills")
    if not root or not os.path.isdir(root):
        return []
    return sorted({os.path.realpath(os.path.join(root, n)) for n in os.listdir(root)} - {os.path.realpath(root)})


def _carve(p, targets):
    """-> the paths to deny in place of p so that every target stays reachable: p itself when no target is in it or under it,
    nothing when p is inside a target, else p's children, each carved in turn."""
    rp = os.path.realpath(p)
    if any(rp == t or rp.startswith(t + "/") for t in targets):
        return []
    if not any(t.startswith(rp + "/") for t in targets):
        return [p]
    out = []
    for c in sorted(os.listdir(rp)):
        out += _carve(os.path.join(rp, c), targets)
    return out


def denied(prof, extra=()):
    """Every path the unit may not see. deny_children: each thing under a root, so a clone made tomorrow is walled too.
    Skill symlink targets (allow_read_skills) are carved out of the deny list; readonly() makes them read only."""
    out = list(prof["deny"]) + list(extra)
    for root in prof.get("deny_children", ()):
        out += [str(p) for p in sorted(Path(root).iterdir()) if str(p) not in prof.get("tmpfs", ())]
    targets = skill_targets(prof)
    if targets:
        out = [q for p in out for q in _carve(p, targets)]
    return sorted(set(out))


def readonly(prof):
    """The paths the unit may read and not write: the skill targets that sit inside a walled root (the ones the deny list
    was carved around). A target elsewhere, such as under ~/.claude, is left as the host has it."""
    roots = [os.path.realpath(r) for r in list(prof["deny"]) + list(prof.get("deny_children", ()))]
    return [t for t in skill_targets(prof) if any(t == r or t.startswith(r + "/") for r in roots)]


def unit_path(p):
    """One path as a systemd list property reads it: unquoted, a space would split it into two entries."""
    if not re.search(r"""[\s"'\\]""", p):
        return p
    return '"%s"' % p.replace("\\", "\\\\").replace('"', '\\"')


def props(prof, box, extra=()):
    """systemd properties. Shared scratch comes up empty. A missing denied path fails the launch: a typo must not unwall.
    The transcript folder is the box's: other runs' memory stays out, this run's stays in."""
    out = []
    for p in denied(prof, extra):
        out += ["-p", "InaccessiblePaths=" + unit_path(p)]
    for p in prof.get("tmpfs", ()):
        out += ["-p", "TemporaryFileSystem=" + unit_path(p)]
    for p in readonly(prof):
        out += ["-p", "ReadOnlyPaths=" + unit_path(p)]
    return out + ["-p", "BindPaths=%s:%s/.claude/projects" % (Path(box, "projects"), HOME)]


def tmp_env(box):
    """A walled run's TMPDIR: inside its box. run_tmp's root (~/.seat-tmp/runs) sits behind the wall, and Claude dies at
    start on a TMPDIR it cannot mkdir in, so no checker ever gave a verdict. relentless_disk.reap_boxes takes this with the tree."""
    d = os.path.join(box, "tmp")
    return {"TMPDIR": d, "TMP": d, "TEMP": d}


def unit_env(prof, box):
    """A walled unit's environment: its TMPDIR, and the profile's `env`. Lodestar's helper is behind the wall, so without
    RM_DATA_ROOT named here anything importing rmpaths crashes before its first check (207 Markers met that and worked round it)."""
    return dict(tmp_env(box), **prof.get("env", {}))


def excludes(prof):
    """The pathspec the Marker's tree and diff leave out: tree_exclude, and tree_from_parent (that comes in as a parent snapshot)."""
    return [":(exclude)" + p for p in list(prof["tree_exclude"]) + list(prof.get("tree_from_parent", ()))]


def make_box(prof, source, sha, nonce):
    """-> the box's path. Tree at sha with no .git and none of tree_exclude, the diff against sha's parent, the verdict script."""
    if any(c.isspace() for c in str(prof["box_root"]) + nonce):
        raise RuntimeError("box root with whitespace: systemd splits BindPaths on it")
    box = Path(os.path.abspath(Path(prof["box_root"], nonce)))      # git runs in the source: a relative path would move
    tree = box / "tree"
    tree.mkdir(parents=True)
    (box / "projects").mkdir()
    (box / "tmp").mkdir(mode=0o700)
    ex = excludes(prof)
    # not `git archive`: it honours export-ignore, which would drop tracked proof files from the Marker's tree
    env = dict(os.environ, GIT_INDEX_FILE=str(box / "export.index"))
    subprocess.run(["git", "read-tree", sha], cwd=source, env=env, capture_output=True, timeout=300, check=True)
    names = subprocess.run(["git", "ls-files", "-z", "--", ".", *ex], cwd=source, env=env, capture_output=True,
                           timeout=300, check=True).stdout
    x = subprocess.run(["git", "checkout-index", "-z", "--stdin", "--prefix=%s/" % tree], cwd=source, env=env,
                       input=names, capture_output=True, timeout=500)
    (box / "export.index").unlink(missing_ok=True)
    if x.returncode:
        raise RuntimeError("export failed: %s" % x.stderr[-200:])
    if subprocess.run(["git", "rev-parse", "-q", "--verify", sha + "^"], cwd=source, capture_output=True).returncode:
        # a root commit's change is all of it: diff from the empty tree, named by the repo's own hash
        parent = subprocess.run(["git", "hash-object", "-t", "tree", "--stdin"], cwd=source, input=b"", capture_output=True,
                                timeout=60, check=True).stdout.decode("ascii").strip()
    else:
        parent = sha + "^"
    d = subprocess.run(["git", "diff", "--no-renames", parent, sha, "--", ".", *ex], cwd=source, capture_output=True,
                       timeout=300, check=True)
    (box / "change.diff").write_bytes(d.stdout)
    snap = prof.get("tree_from_parent") or []
    if snap and parent == sha + "^":
        # the ledger and review state as of the candidate's parent: what a proof may read, never what the builder wrote since
        _snapshot(source, parent, snap, tree, box)
    (box / "nonce").write_text(nonce, encoding="ascii")
    (box / "verdict").write_text(VERDICT_SCRIPT, encoding="utf-8")
    os.chmod(box / "verdict", 0o755)
    return str(box)


def _snapshot(source, parent, paths, tree, box):
    env = dict(os.environ, GIT_INDEX_FILE=str(box / "snap.index"))
    try:
        subprocess.run(["git", "read-tree", parent], cwd=source, env=env, capture_output=True, timeout=300, check=True)
        names = subprocess.run(["git", "ls-files", "-z", "--", *paths], cwd=source, env=env, capture_output=True,
                               timeout=300, check=True).stdout
        if names:
            x = subprocess.run(["git", "checkout-index", "-z", "--stdin", "--prefix=%s/" % tree], cwd=source, env=env,
                               input=names, capture_output=True, timeout=500)
            if x.returncode:
                raise RuntimeError("snapshot failed: %s" % x.stderr[-200:])
    finally:
        (box / "snap.index").unlink(missing_ok=True)
    for p in paths:     # read only: a proof reads this state and cannot change it
        for dp, dn, fn in os.walk(tree / p):
            for n in fn:
                os.chmod(os.path.join(dp, n), 0o444)


def remove_box(box):
    shutil.rmtree(box, ignore_errors=True)


def marker_prompt(st, text, box):
    """The checker's words, its way to the change and its way to a verdict being the box's."""
    c = st["candidate"]
    qv = shlex.quote(str(box) + "/verdict")     # a box path with a space still runs
    return "\n".join([
        "You are a blind checker. You did not do this work and you have no record of how it went. Your cwd is a clean "
        "export of commit %s, with no git history." % c["sha"],
        *RULE,
        "Then run exactly one of:",
        "  python3 %s PASS \"what you ran and saw\"" % qv,
        "  python3 %s WEAK \"the runs you made and what each showed, then each gap and the mutant or probe that "
        "shows it, so the next worker can pin it\"" % qv,
        "  python3 %s FAIL \"what is wrong, so the next worker can fix it\"" % qv,
        "", "Contract: %s" % json.dumps(st["contract"]), "Evidence the commit names: %s" % c["evidence"][:1500],
        "See the change in: %s/change.diff" % box, "", "--- item ---", text])


def read_verdict(box):
    """-> {word, reasons, at}, or None. The box is the Marker's to write: only well-formed words pass."""
    try:
        v = json.loads(Path(box, "verdict.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(v, dict) or v.get("word") not in WORDS:
        return None
    try:
        at = float(v.get("at") or time.time())
    except (TypeError, ValueError, OverflowError):     # the Marker writes this file: a bad stamp is its to get wrong, not ours to crash on
        at = time.time()
    return {"word": v["word"], "reasons": str(v.get("reasons") or ""), "at": at}


def would_deny(inputs, prof):
    """-> the denied paths a run's tool calls named. For enforce false: the wall's report."""
    hits = set()
    for inp in inputs:
        text = json.dumps(inp, ensure_ascii=False)
        hits.update(p for p in denied(prof) + list(prof.get("tmpfs", ()))
                    if re.search(r"(?<![\w.-])" + re.escape(p) + r"(?![\w.-])", text))
        # the path at a word edge: after a slash, space, quote, = ( ; | & < > : or the start - shell quoting does not hide it
        hits.update(p for p in prof["tree_exclude"] if re.search(r"(?<![\w.-])" + re.escape(p) + r"(?![\w.-])", text))
    return sorted(hits)


def audit(store, rules, sessions_of, inputs_of):
    """Report only. -> [{item, unit, would_deny}] for each check in the store that has a session."""
    prof = profile(rules)
    out = []
    if prof is None:        # no wall configured: nothing to report against
        return out
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
