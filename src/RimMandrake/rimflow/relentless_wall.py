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
WORDS = ("PASS", "WEAK", "FAIL", "UNMEASURED")
UNMEASURED = "UNMEASURED"   # CHECKER_SANDBOX_FIX_BLIND_TO_STEVE: the box could not reach the evidence; no work goes back
REACH_TAG = "CANNOT REACH:"
RULE = (   # both Marker prompts: the unwalled and the walled one must never differ in what the words mean
    "Decide one thing: did this commit do what the item says, proven by running it? Run the proof yourself. Judge "
    "the contract against the item's words: a contract that is easier than the item is a FAIL. A proof that "
    "cannot run because of the commit is a FAIL. Do not fix anything, do not push, do not touch the ledger.",
    "One case is not a FAIL: the work holds and only the proof is short. If you think a clause is unproven or the "
    "contract skipped it, run that clause yourself against the code. Your run shows the clause is done: that is WEAK. "
    "Your run shows it is not done, or you can reach all it needs and still cannot show it either way: that is FAIL.",
    "Being unable to measure is not a FAIL. If the work may be done but what would show it is out of your box's reach - "
    "another machine (ssh, Tailscale), a path this box hides (D:\\ClaudeWork, /mnt/d/ClaudeWork/rimmandrake come up empty "
    "here), the live game, a Windows program that cannot start here - say UNMEASURED and begin the reasons with "
    "'CANNOT REACH:', naming each thing and the command that showed you cannot reach it, then what you did check. It sends "
    "no work back: the box goes up for repair. A proof that runs and is red is FAIL; a clause you can reach is never UNMEASURED.",
    "Keep the two apart when you record the verdict: each wrong thing your own run showed goes in its own --defect (a wrong "
    "number, a red test, a crash, a clause not done), each piece of evidence you could not reach goes in its own --unreached. "
    "Any --defect makes the verdict FAIL, whatever you could not reach; --unreached and no --defect is UNMEASURED, never PASS.",
    "A gap must be in the item's own words: the mutant breaks something a clause of the item asks for. A mutant of an "
    "inner detail, or of an edge the item never named, is no gap, and every test has those.",
    "PASS: every clause of the item is done, you ran it, and you found no gap in the proof that you could show. "
    "WEAK: every clause is done, shown by your own runs, and you can show a gap: a mutant that stays green, or a "
    "clause the proof never reaches. A weak proof is not a pass: the item stays open and the next worker strengthens "
    "the proof without touching the code. FAIL: a clause is not done, or the proof is red, or cannot run for a reason in the commit. A gap you "
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
USAGE = ('usage: verdict PASS|WEAK|FAIL|UNMEASURED "what you ran and saw" [--defect "a wrong thing your run showed"]... '
         '[--unreached "evidence you could not reach, and the command that showed it"]...')
a, defects, unreached = sys.argv[1:], [], []
pos = []
while a:
    x = a.pop(0)
    if x in ("--defect", "--unreached") and a:
        y = " ".join(a.pop(0).split())[:600]      # the reader's own normalisation (relentless_wall.clean_list): agree on it
        if y:
            (defects if x == "--defect" else unreached).append(y)
    else:
        pos.append(x)
if len(pos) != 2 or pos[0].upper() not in ("PASS", "WEAK", "FAIL", "UNMEASURED"):
    sys.exit(USAGE)
if pos[0].upper() == "UNMEASURED" and not unreached:
    sys.exit("UNMEASURED needs at least one --unreached: name what you could not reach")
if pos[0].upper() == "UNMEASURED" and defects:
    sys.exit("a defect your run showed is a FAIL, not UNMEASURED: say FAIL and keep the --unreached lines")
if pos[0].upper() == "PASS" and (defects or unreached):
    sys.exit("a PASS carries no --defect and no --unreached: evidence you could not reach is UNMEASURED, a defect is FAIL")
with open(HERE + "/verdict.tmp", "w", encoding="utf-8") as f:
    json.dump({"word": pos[0].upper(), "reasons": pos[1], "defects": defects, "unreached": unreached, "at": time.time()}, f)
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
        "  python3 %s FAIL \"what is wrong, so the next worker can fix it\" --defect \"one wrong thing\" [--defect ...] "
        "[--unreached \"what you also could not reach\"]" % qv,
        "  python3 %s UNMEASURED \"CANNOT REACH: what, and the command that showed it; then what you did check\" "
        "--unreached \"one thing out of reach, and the command that showed it\" [--unreached ...]" % qv,
        *offbox_lines(st["contract"], box),
        "", "Contract: %s" % json.dumps(st["contract"]), "Evidence the commit names: %s" % c["evidence"][:1500],
        "See the change in: %s/change.diff" % box, "", "--- item ---", text])


def clean_list(v):
    """THE one normalisation of a verdict's defects / unreached (script, CLI, box file, store all go through it): whitespace
    collapsed, blank entries dropped, each <= 600 chars, at most 20. -> a list, or None when the field was not given at all
    (an old-format verdict, read from its prose)."""
    if v is None:
        return None
    if not isinstance(v, (list, tuple)):
        v = [v]
    return [y for y in (" ".join(str(x).split())[:600] for x in v) if y][:20]


_strs = clean_list


def refusal(word, defects, unreached):
    """-> why a structured verdict is refused at the door (the CLI and the verdict script say the same), or None. Only ever
    used where a checker is there to read it: a verdict already on disk is never refused, read_as reads it."""
    if defects is None and unreached is None:
        return None
    if word == UNMEASURED and not unreached:
        return "UNMEASURED needs at least one --unreached: name what you could not reach"
    if word == UNMEASURED and defects:
        return "a defect your run showed is a FAIL, not UNMEASURED: say FAIL and keep the --unreached lines"
    if word == "PASS" and (defects or unreached):
        return "a PASS carries no --defect and no --unreached: evidence you could not reach is UNMEASURED, a defect is FAIL"
    return None


def read_verdict(box):
    """-> {word, reasons, defects, unreached, at}, or None. The box is the Marker's to write: only well-formed words pass.
    defects / unreached are None when the file did not carry them (written before the structured verdict)."""
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
    return {"word": v["word"], "reasons": str(v.get("reasons") or ""), "defects": clean_list(v.get("defects")),
            "unreached": clean_list(v.get("unreached")), "at": at}


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


# ---- blindness (CHECKER_SANDBOX_FIX_BLIND_TO_STEVE). Owner 2026-11-04: "the checker was unable to measure something, and
# interpreted that as a wrong value rather than an inability that should have been reported up for fix and repair".
# STEVE_DISK_MEASURE_ONLY_FORTY_GIGS_LEFT was done at gen 1 (ssh-verified) and went to gen 9 on FAILs that said "ssh
# fails in this sandbox" and "/mnt/d/ClaudeWork/rimmandrake is an empty directory here". A FAIL that only says the box is
# blind is read as UNMEASURED: it sends no work back. Measured on the store's 142 FAIL reasons (selftest_relentless_blind).
HIDDEN = ("/mnt/d/ClaudeWork", "D:\\ClaudeWork", "D:/ClaudeWork", "/home/mandrake/rm/", "/home/mandrake/dev/", "~/dev/")
_ABSENT = (r"\b(empty|absent|missing|not there|does not exist|doesn't exist|no such file|not found|FileNotFoundError|"
           r"not visible|unreadable|cannot be read|could not be read|not reachable|unreachable|masked|mask\b|tmpfs|UNC path|"
           r"Invalid argument|NOT VISIBLE)\b")
_REACH = [re.compile(x, re.I) for x in (
    r"\b(could|can)\s?not\s+(be\s+)?(reach|see|read|run|start|open|ssh|measure|be run|be shown)\w*[^.;]{0,60}?"
    r"\b(here|sandbox|box|checker|walled)\b",
    r"\b(sandbox|this box|walled|checker'?s? (env|view|box|sandbox))\b[^.;]{0,60}?(cannot|can't|could not|not visible|"
    r"not reachable|empty|masks?\b|tmpfs|blocked|fails?\b|failed)",
    r"\bnot (reachable|visible) (from|in) (this|the|my) (sandbox|box|checker)",
    r"\bssh\s+\S+[^.;]{0,40}?(fail|exit(s|ed)? 255|permission denied|bad owner|could not resolve|timed out)",
    r"\benvironment (block|problem|fault|failure)\b|\benv only\b|\bnot a code defect\b",
    r"\b(is|are) empty here\b|\bempty (tmpfs|mask|directory)\b",
    r"\b(can't|cannot|could not|unable to) reach\b",
)]
_HIDDEN_ABSENT = re.compile(r"(%s)[^.;]{0,120}?%s|%s[^.;]{0,80}?(%s)" % (
    "|".join(re.escape(h) for h in HIDDEN), _ABSENT, _ABSENT, "|".join(re.escape(h) for h in HIDDEN)), re.I)
# what a Marker writes when its own run showed the work wrong: then the FAIL stands, blind parts or not
# GPT review of 0135b04912: old-format prose is read biased to FAIL - a named defect beats any blindness beside it.
_DEFECT = re.compile(r"cause is in (this|the) commit|\bis false\b|\bleaks?\b|\bproof is red\b|\bnot done\b|"
                     r"\b\d+ FAIL(ED|ING|S)?\b|\bFAIL with \d|\b(stays?|leaves \S+( \S+)?) (green|OK)\b|\bclause \d+ is missing|"
                     r"\bdoes not (do|fix|hold)\b|\bwrong\b|\bregress|"
                     r"\bexpected\b[^.;]{0,40}?\b(got|but (was|is|found|saw)|found|saw|actual)\b|\bdrops?\b|\bdropped\b|"
                     r"\bcrash(es|ed)?\b|\btraceback\b|\b(raises|raised)\b|\bassert(ion)?(Error)?\b|\bbug\b|\boff[- ]by[- ]one\b|"
                     r"\bmismatch|\bbroken\b|\bincorrect\b|\bmiscount|\bdoes not match\b|\bnot equal\b", re.I)


def blind_reason(reasons):
    """-> the words that say the checker could not reach its evidence, or None. Pure: a reading of the reasons."""
    text = reasons or ""
    if text.lstrip().upper().startswith(REACH_TAG):
        return text.lstrip()[:200]
    for rx in _REACH + [_HIDDEN_ABSENT]:
        m = rx.search(text)
        if m:
            return text[max(0, m.start() - 40):m.end() + 40].strip()
    return None


def defect_said(reasons):
    """True when the reasons say the checker's own run showed the work wrong: a real FAIL, whatever else it could not see."""
    return bool(_DEFECT.search(reasons or ""))


def read_as(word, reasons, defects=None, unreached=None):
    """-> (word the supervisor acts on, the blind words or None). Structured (defects / unreached lists, the verdict script's
    own fields): any observed defect is FAIL whatever the word; otherwise any unreached evidence is UNMEASURED - under PASS
    too (GPT round 2: a PASS that names evidence it could not reach is not a close). WEAK keeps its word: it closes nothing.
    Old format (both None): the prose, biased to FAIL - a defect named anywhere keeps or makes it FAIL, even under UNMEASURED."""
    if defects is not None or unreached is not None:
        defects, unreached = clean_list(defects) or [], clean_list(unreached) or []
        if defects:
            return "FAIL", None
        if word in ("PASS", "FAIL", UNMEASURED) and unreached:
            return UNMEASURED, "; ".join(unreached)[:600]
        if word == UNMEASURED:      # the script refuses this; a hand-written file is read as prose
            return read_as(word, reasons)
        return word, None
    if word == UNMEASURED:
        if defect_said(reasons):
            return "FAIL", None
        return UNMEASURED, blind_reason(reasons) or (reasons or "")[:200]
    if word == "FAIL":
        b = blind_reason(reasons)
        if b and not defect_said(reasons):
            return UNMEASURED, b
    return word, None


# ---- off-box measurements: a contract's `offbox` ADAPTER NAMES. Each name is a fixed command in relentless_rules.json
# "offbox_adapters", which the supervisor runs outside the wall at check launch; raw output and exit go read only into the
# box, so the Marker judges a fresh measurement, never a number a worker typed. GPT review of 0135b04912: a worker-authored
# command ran with the supervisor's reach and could carry transcripts or store files into the box - so a worker (or unhold)
# may only NAME an adapter; what runs is supervisor-owned code, run as argv (no shell) from an empty folder.
OFFBOX_MAX = 4
OFFBOX_OUT_MAX = 20000
_NAME = re.compile(r"^[a-z][a-z0-9_]{1,40}$")


def adapters(rules):
    """-> {name: {what, argv}} from the rules' offbox_adapters; keys starting _ are notes."""
    got = (rules or {}).get("offbox_adapters") or {}
    return {k: v for k, v in got.items() if not k.startswith("_") and isinstance(v, dict) and isinstance(v.get("argv"), list)
            and v["argv"] and all(isinstance(x, str) for x in v["argv"])}


def check_offbox_names(names, rules):
    """-> the names, cleaned. Raises ValueError for anything that is not a known adapter name: no shell crosses the wall."""
    names = [x.strip() for x in (names or []) if x and x.strip()]
    known = adapters(rules)
    bad = [x for x in names if not _NAME.match(x) or x not in known]
    if bad:
        raise ValueError("--offbox takes an adapter name from relentless_rules.json offbox_adapters (%s), never a command: "
                         "%s. A new reading is a new adapter, added by a reviewed change to the rules"
                         % (", ".join(sorted(known)) or "none defined", ", ".join(repr(x[:80]) for x in bad)))
    if len(names) > OFFBOX_MAX:
        raise ValueError("at most %d offbox adapters" % OFFBOX_MAX)
    return names


def offbox_cmds(contract):
    """-> the contract's offbox adapter names (an old contract may hold free text: it is refused at run time, never run)."""
    got = (contract or {}).get("offbox") or []
    return [got] if isinstance(got, str) else list(got)


def write_offbox(box, results):
    """results: [{cmd, exit, out, at}]. -> the folder. Each file is read only: the Marker reads a measurement, never edits it."""
    d = Path(box, "offbox")
    d.mkdir(exist_ok=True)
    for n, r in enumerate(results, 1):
        f = d / ("%d.txt" % n)
        f.write_text("$ %s\nmeasured_at=%s exit=%s\n%s\n" % (r["cmd"], time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(r["at"])),
                                                         r["exit"], (r["out"] or "")[-OFFBOX_OUT_MAX:]), encoding="utf-8")
        os.chmod(f, 0o444)
    return str(d)


def offbox_lines(contract, box):
    """The Marker's words about the supervisor's off-box readings, when the contract declares any."""
    cmds = offbox_cmds(contract)
    if not cmds:
        return []
    return ["", "Off-box readings: the supervisor ran the contract's offbox adapter(s) %s outside your box just before you "
            "started, and wrote each command, its exit and its raw output to %s/offbox/<n>.txt (read only). They are fresh "
            "measurements, not the worker's words: judge them as the reading of what your box cannot reach, and judge "
            "whether each one really measures what its clause asks. A reading that is missing or failed to run is "
            "--unreached, not a --defect." % (", ".join(cmds), box)]


PROBE = r'''
for p in "$@"; do
  if [ -d "$p" ]; then ls -A "$p" >/dev/null 2>&1 && echo "SEEN $p" || echo "DENIED $p"
  elif [ -e "$p" ] || [ -L "$p" ]; then cat "$p" >/dev/null 2>&1 && echo "SEEN $p" || echo "DENIED $p"
  else echo "ABSENT $p"; fi
done
env | grep -c '^RELENTLESS_ROOT=' | sed 's/^/ROOT_ENV /'
'''
