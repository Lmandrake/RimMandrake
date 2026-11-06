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
    "here but for the paths the prompt lists as bound read only), the live game, a Windows program that cannot start here - say UNMEASURED and begin the reasons with "
    "'CANNOT REACH:', naming each thing and the command that showed you cannot reach it, then what you did check. It sends "
    "no work back: the box goes up for repair. A proof that runs and is red is FAIL; a clause you can reach is never UNMEASURED.",
    "Keep the two apart when you record the verdict: each wrong thing your own run showed goes in its own --defect (a wrong "
    "number, a red test, a crash, a clause not done), each piece of evidence you could not reach goes in its own --unreached. "
    "Any --defect makes the verdict FAIL, whatever you could not reach; --unreached and no --defect is UNMEASURED, never PASS.",
    "Begin every --defect with its cause (CHECKER_VERDICT_BUILD_CAUSE_BEFORE_RETURN): 'product:' the commit's own change or "
    "behaviour is wrong - name the changed file or the proof command that shows it, and add one --control saying how you "
    "showed your instrument can see (it goes green on a known-good case, or catches a fault you put in); 'measurement:' "
    "the proof, the contract or the test is what is wrong, not the work; 'environment:' the machine, the disk, the game "
    "load, a remote host, the account; 'unknown:' you cannot tell which (an untagged defect is read as unknown). Only a product defect with a control goes back "
    "to a builder; the others go to the proof, to Operations, or to a diagnosis, never to new code.",
    "A gap must be in the item's own words: the mutant breaks something a clause of the item asks for. A mutant of an "
    "inner detail, or of an edge the item never named, is no gap, and every test has those.",
    "PASS: every clause of the item is done, you ran it, and you found no gap in the proof that you could show. "
    "WEAK: every clause is done, shown by your own runs, and you can show a gap: a mutant that stays green, or a "
    "clause the proof never reaches. A weak proof is not a pass: the item stays open and the next worker strengthens "
    "the proof without touching the code. FAIL: a clause is not done, or the proof is red, or cannot run for a reason in the commit. A gap you "
    "only suspect and did not show is no gap. Look for a clause that is missing before you look for a thin test.",
    "If you say WEAK, begin the reasons with GAP:DIFF when a gap you showed is a part of this commit's own change "
    "that you put back as it was before the commit while the proof stayed green, and that part does what a clause "
    "asks; begin with GAP:OTHER when every gap you showed is something else, such as a mutant you wrote yourself.",
    "A WEAK must say what strong proof would look like (JUDGE_WEAK_RETHINK_NAME_THE_STRONG_PROOF; owner, 2026-11-05: "
    "\"The Judge should have to be able to articulate what strong proof would look like.\"). Put two parts in the reasons: "
    "'STRONG: <the exact command or observation that would prove the clause>' and 'LETS THROUGH: <the real product "
    "defect, in the item's words, that the current proof would let ship>'. A WEAK missing either line is read as PASS. "
    "If you can run that strong check yourself and the work passes it, that is PASS, with your run as the evidence: "
    "never send work back to have a test written for a check you already made. Form, wording, citations, formatting "
    "and missing paperwork are never a gap: note them on a PASS.")
SHADOW = "narrow_weak_1"   # RELENTLESS_WEAK_MEASURE_PASS_COLLAPSE: the narrower WEAK, recorded per verdict; LIVE since 2026-11-03 (acted_weak)


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
USAGE = ('usage: verdict PASS|WEAK|FAIL|UNMEASURED "what you ran and saw" '
         '[--defect "product|measurement|environment|unknown: a wrong thing your run showed"]... '
         '[--control "how you showed your instrument can see"]... '
         '[--unreached "evidence you could not reach, and the command that showed it"]... '
         '[--propose ADAPTER_NAME|/read/path]...')
a, defects, unreached, proposals, controls = sys.argv[1:], [], [], [], []
pos = []
while a:
    x = a.pop(0)
    if x in ("--defect", "--unreached", "--propose", "--control") and a:
        y = " ".join(a.pop(0).split())[:600]      # the reader's own normalisation (relentless_wall.clean_list): agree on it
        if y:
            {"--defect": defects, "--unreached": unreached, "--propose": proposals, "--control": controls}[x].append(y)
    else:
        pos.append(x)
if len(pos) != 2 or pos[0].upper() not in ("PASS", "WEAK", "FAIL", "UNMEASURED"):
    sys.exit(USAGE)
if any(d.split(":", 1)[0].strip().lower() == "product" for d in defects) and not controls:
    sys.exit("a product: defect needs a --control: how you showed your instrument can see (green on a known-good case, "
             "or it catches a fault you put in); without one, say unknown:")
if controls and not defects:
    sys.exit("--control backs a product: defect only")
if pos[0].upper() == "UNMEASURED" and not unreached:
    sys.exit("UNMEASURED needs at least one --unreached: name what you could not reach")
if pos[0].upper() == "UNMEASURED" and defects:
    sys.exit("a defect your run showed is a FAIL, not UNMEASURED: say FAIL and keep the --unreached lines")
if proposals and pos[0].upper() != "UNMEASURED":
    sys.exit("--propose is the reach repair of an UNMEASURED verdict only")
if pos[0].upper() == "PASS" and (defects or unreached):
    sys.exit("a PASS carries no --defect and no --unreached: evidence you could not reach is UNMEASURED, a defect is FAIL")
with open(HERE + "/verdict.tmp", "w", encoding="utf-8") as f:
    json.dump({"word": pos[0].upper(), "reasons": pos[1], "defects": defects, "unreached": unreached,
               "proposals": proposals, "controls": controls, "at": time.time()}, f)
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


def props(prof, box, extra=(), through_paths=()):
    """systemd properties. Shared scratch comes up empty. A missing denied path fails the launch: a typo must not unwall.
    The transcript folder is the box's: other runs' memory stays out, this run's stays in. `through_paths` (through()) are
    bound read only over the empty scratch; '-': one gone since it was named is skipped, never a failed launch."""
    out = []
    for p in denied(prof, extra):
        out += ["-p", "InaccessiblePaths=" + unit_path(p)]
    for p in prof.get("tmpfs", ()):
        out += ["-p", "TemporaryFileSystem=" + unit_path(p)]
    for p in readonly(prof):
        out += ["-p", "ReadOnlyPaths=" + unit_path(p)]
    for p in through_paths:
        out += ["-p", "BindReadOnlyPaths=-" + p]
    for src, dst in git_reads(box):     # a git-granted box (grant_git): the shared object stores at box paths, read only;
        out += ["-p", "BindReadOnlyPaths=-%s:%s" % (src, dst)]      # '-': a store gone since is git's error, not a launch's
    for p in prof.get("write_through", ()):     # MARKER_WALL_FIX_HIDES_ONLY_THE_DIARY: the Windows build stage, bound
        out += ["-p", "BindPaths=-" + unit_path(p)]     # as the host's drvfs so dotnet.exe is handed D:\, not a UNC path
    return out + ["-p", "BindPaths=%s:%s/.claude/projects" % (Path(box, "projects"), HOME),
                  "-p", "BindPaths=%s:%s" % (Path(box, "tmp"), UNIT_TMP)]     # tmp_env(): a short TMPDIR, still the box's


# CHECKER_REACH_FIX_NAMED_SCRATCH_READ_ONLY (2026-11-05): 24 items held `unmeasured`, 17 of them on evidence under
# /mnt/d/ClaudeWork/rimmandrake (an ops_watch status.json, a testq tick.log, a backups folder) that the tmpfs over shared
# scratch hides. The wall's table (design section 8) withholds store, memory, attempts, git history, conversations and
# ledger notes - not the program-written state an item's proof reads. So a path the contract, the evidence or the item
# names under a `read_through` root is bound READ ONLY into the box; the rest of scratch stays empty and writable, and
# `never_through` (the worker run folders) is never bound.
THROUGH_MAX = 24
_THROUGH_WORD = re.compile(r"(?<![\w.~$@+/\\-])(?:[A-Za-z]:[\\/]|/)[\w.~@+-]*(?:[/\\][\w.~@+-]*)*")
_SAFE = re.compile(r"^/[\w./@+~-]+$")


def _host(word):
    """-> a path word as a host path: a Windows drive path as /mnt/<drive>/..., no trailing punctuation or slash."""
    w = word.rstrip(".,;:)'\"")
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", w)
    if m:
        w = "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/"))
    return w.rstrip("/") or "/"


def _inside(p, root):
    return p.startswith(root.rstrip("/") + "/")


def through_reachable(path, prof):
    """True when a named `path` would be bound by through(): strictly under a read_through root, outside never_through.
    Prefixes only (no filesystem read): relentless_reach.hidden asks this of a contract's proof."""
    p = os.path.normpath(_host(path))      # "..": resolved before the prefixes are read
    rx = prof.get("never_through_rx")
    return (any(_inside(p, r) for r in prof.get("read_through") or ())
            and not any(p == n.rstrip("/") or _inside(p, n) for n in prof.get("never_through") or ())
            and not (rx and re.search(rx, p)))


def _clean_dir(d, prof, cap=4000):
    """True when a folder may be bound whole: nothing in it is a path through_reachable() refuses (a worker's progress
    file inside a readings folder), and it is small enough to have looked at all of it."""
    n = 0
    for top, dirs, files in os.walk(d):
        for f in dirs + files:
            n += 1
            if n > cap or not through_reachable(os.path.join(top, f), prof):
                return False
    return True


def through(prof, texts, cap=THROUGH_MAX):
    """-> the host paths to bind read only into the box: each path word of `texts` that through_reachable() takes, walked
    up to the nearest one that exists while still strictly under its root (a reading not written yet shows its folder),
    whose real path stays inside the root and outside never_through, once each, a path under another one dropped."""
    roots = [os.path.realpath(r) for r in prof.get("read_through") or ()]
    never = [os.path.realpath(n) for n in prof.get("never_through") or ()]
    env = prof.get("env") or {}
    got = []
    for t in texts:
        t = re.sub(r"\$\{?(\w+)\}?", lambda v: env.get(v.group(1), v.group(0)), t or "")   # "$RM_DATA_ROOT/x", as needs() reads it
        for m in _THROUGH_WORD.finditer(t):
            p = os.path.normpath(_host(m.group(0)))
            if not through_reachable(p, prof):
                continue
            while not os.path.lexists(p) and any(_inside(os.path.dirname(p), r) for r in prof["read_through"]):
                p = os.path.dirname(p)
            if not os.path.lexists(p):
                continue
            rp = os.path.realpath(p)
            if (not through_reachable(rp, dict(prof, read_through=roots, never_through=never))   # a link stays inside
                    or not _SAFE.match(rp) or rp in got):
                continue
            if os.path.isdir(rp) and not _clean_dir(rp, prof):
                continue
            got.append(rp)
    got = sorted(got)
    out = [p for p in got if not any(_inside(p, q) for q in got if q != p)]
    return out[:cap]


def through_lines(paths):
    """The Marker's words about what was bound."""
    if not paths:
        return []
    return ["", "Bound read only from the host into your box (the rest of shared scratch is still empty here): %s. Read "
            "them as the evidence they are; a path in this list is never --unreached." % ", ".join(paths)]


UNIT_TMP = "/tmp"


def tmp_env(box):
    """A walled run's TMPDIR: its box's tmp, which props() binds over the unit's /tmp. run_tmp's root (~/.seat-tmp/runs)
    sits behind the wall, and Claude dies at start on a TMPDIR it cannot mkdir in, so no checker ever gave a verdict.
    Named as /tmp, not <box>/tmp: 50 bytes of box path plus run_selftests' selftest_run_* dir and a test's own mkdtemp
    passed AF_UNIX's 107-byte limit (CHECKER_TMPDIR_FIX_SOCKETS_DONT_FIT). relentless_disk.reap_boxes takes it with the tree."""
    return {"TMPDIR": UNIT_TMP, "TMP": UNIT_TMP, "TEMP": UNIT_TMP}


def unit_env(prof, box):
    """A walled unit's environment: its TMPDIR, and the profile's `env`. Lodestar's helper is behind the wall, so without
    RM_DATA_ROOT named here anything importing rmpaths crashes before its first check (207 Markers met that and worked round it)."""
    return dict(tmp_env(box), **prof.get("env", {}))


def excludes(prof):
    """The pathspec the Marker's tree and diff leave out: tree_exclude, and tree_from_parent (that comes in as a parent snapshot)."""
    return [":(exclude)" + p for p in list(prof["tree_exclude"]) + list(prof.get("tree_from_parent", ()))]


def make_box(prof, source, sha, nonce, grants=()):
    """-> the box's path. Tree at sha with no .git and none of tree_exclude, the diff against sha's parent, the verdict script.
    `grants` (a passed reach repair's, relentless_reachfix.grants): GIT_GRANT adds a read-only git history at sha (grant_git)."""
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
    if ITEM_GRANT in (grants or ()):
        try:    # the candidate's items (item_rev): the rev the reach probe granted, so a passed probe is what the box shows
            grant_items(box, source, item_rev(sha))
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as e:
            shutil.rmtree(tree / ITEMS, ignore_errors=True)
            (box / ITEM_NOTE).unlink(missing_ok=True)
            (box / "item_grant_failed").write_text(str(e)[-400:], encoding="utf-8")
    if GIT_GRANT in (grants or ()):
        try:
            grant_git(box, source, sha)
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as e:
            # a grant that cannot be made leaves the plain box (its prompt says no git history), never a crashed tick
            shutil.rmtree(tree / ".git", ignore_errors=True)
            (box / GIT_NOTE).unlink(missing_ok=True)
            (box / "git_grant_failed").write_text(str(e)[-400:], encoding="utf-8")
    return str(box)


# CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS gen 3: the git/gh/proc reach repairs gave adapters (a reading outside the box) and
# the Judges stayed blind, because their IN-BOX proofs run git themselves: git rev-parse HEAD (testq_steward), git show
# <rev>:path (scratch_reap's committed-saves guard), the objects of a fixed.sha (jam_classes), code commits (close_gate).
# A passed git reach repair grants the box a history: tree/.git with HEAD detached at the candidate and no ref at all. Its
# objects: the clean clone's own (a --shared clone holds tens of MB) COPIED in, and each object store it borrows from
# (~/rm/store.git/objects) bound READ ONLY at a box path the alternates file names. The deny list is untouched: nothing
# but those object stores becomes readable (a carve down to them opened every folder on the way; GPT-free opus review).
# What it opens that the bare export does not: commit messages, and through `git show` the tree_exclude folders - the
# prompt says those are workers' words. The wall stops accident, not a hostile Marker (module doc); refs to later commits
# (origin/main, the supervisor's verdict commits) are never written, so --all walks the candidate's ancestry only.
GIT_GRANT = "git_history"
GIT_NOTE = "gitobj.json"
# CHECKER_REACH_FIX_OTHER_STILL_DARK gen 3: tree_exclude keeps infrastructure/state/items out of every box, and a proof that
# reads the live item glob (NIGHTSIDE_TITAN_JUDGE_GIANTS_IN_THE_DARK's selftest: "UMBRA_TITAN_POPULATE_BURNS_TO_WALK.md ...
# whole items dir absent in export") classed `other`, whose repair binds HOST paths: it passed its probe and the Judge
# stayed blind, since no bind puts a file into the exported tree. A passed items repair grants the box that folder from
# git at the candidate (item_rev), read only. The prompt calls it filers' prose and says to judge by runs, not by it.
# CHECKER_REACH_FIX_ITEMS_STILL_DARK: it was granted at the candidate's PARENT while the probe granted at the candidate.
# A build may edit item prose (LEDGER_ONLY only makes a commit touching nothing else "no work"): WORLD_BEAUTY_VERIFY_
# OFFLINE_BEAT_THE_GAME's candidate rewrote items/closed/PLANETARY_LOADSCREEN_RENDERS_2.md's verify clause, the probe read
# the new text, the box held the old, and the Judge stayed blind. One rev, item_rev, serves the box and the probe.
ITEM_GRANT = "item_prose"
ITEMS = "infrastructure/state/items"
ITEM_NOTE = "items.json"
GRANTS = (GIT_GRANT, ITEM_GRANT)
GIT_COPY_MAX = 2 << 30      # a borrower's own objects past this are no --shared check clone: no grant, the plain box


def _object_chain(source):
    """-> [(real path, borrows)] for source's object folder and every alternate it borrows from, transitively."""
    top = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=source,
                         capture_output=True, text=True, timeout=60, check=True).stdout.strip()
    todo, out, seen = [os.path.join(top, "objects")], [], set()
    while todo:
        d = os.path.realpath(todo.pop(0))
        if d in seen or not os.path.isdir(d):
            continue
        seen.add(d)
        alts = []
        try:
            with open(os.path.join(d, "info", "alternates"), encoding="utf-8") as f:
                alts = [ln.strip() for ln in f.read().splitlines() if ln.strip() and not ln.strip().startswith("#")]
        except OSError:
            pass
        out.append((d, bool(alts)))
        todo += [a if os.path.isabs(a) else os.path.join(d, a) for a in alts]
    return out


def _copy_objects(src, dst):
    """A borrower's own objects (packs and loose), never its info/: its alternates name paths the box hides."""
    total = 0
    for dp, dn, fn in os.walk(src):
        rel = os.path.relpath(dp, src)
        if rel == "info" or rel.startswith("info" + os.sep):
            dn[:] = []
            continue
        for n in fn:
            total += os.path.getsize(os.path.join(dp, n))
    if total > GIT_COPY_MAX:
        raise RuntimeError("git grant: %s holds %d bytes of its own objects (cap %d)" % (src, total, GIT_COPY_MAX))
    shutil.copytree(src, dst, ignore=lambda d, names: ["info"] if os.path.realpath(d) == os.path.realpath(src) else [],
                    dirs_exist_ok=True)


def grant_git(box, source, sha):
    """tree/.git at sha: HEAD detached, no refs, the index read from sha, the shared stores bound read only (git_reads)."""
    box = Path(box)
    tree = box / "tree"
    fmt = subprocess.run(["git", "rev-parse", "--show-object-format"], cwd=source, capture_output=True, text=True,
                         timeout=60, check=True).stdout.strip() or "sha1"
    subprocess.run(["git", "init", "-q", "--template=", "--object-format=" + fmt, str(tree)], capture_output=True,
                   timeout=60, check=True)
    gd = tree / ".git"
    binds, host = [], []
    for d, borrows in _object_chain(source):
        if borrows:
            _copy_objects(d, str(gd / "objects"))
            continue
        if not _SAFE.match(d):
            raise RuntimeError("git grant: an object store systemd cannot bind: %s" % d[:200])
        dst = str(box / "gitobj" / str(len(binds)))
        os.makedirs(dst)
        binds.append([d, dst])
        host.append(d)
    (gd / "objects" / "info").mkdir(parents=True, exist_ok=True)
    (gd / "objects" / "info" / "alternates").write_text("".join(b[1] + "\n" for b in binds), encoding="utf-8")
    (gd / "HEAD").write_text(sha + "\n", encoding="ascii")
    env = dict(os.environ, GIT_DIR=str(gd), GIT_WORK_TREE=str(tree), GIT_ALTERNATE_OBJECT_DIRECTORIES=":".join(host))
    r = subprocess.run(["git", "read-tree", sha], env=env, capture_output=True, text=True, timeout=300)
    if r.returncode:
        raise RuntimeError("git grant: read-tree %s: %s" % (sha, r.stderr[-200:]))
    # the tree_exclude folders are not in the export: skip-worktree, so `git status` shows the tree, not 3000 deletions
    names = subprocess.run(["git", "ls-files", "-z"], env=env, capture_output=True, timeout=300, check=True).stdout
    gone = [n for n in names.split(b"\0") if n and not os.path.lexists(os.path.join(os.fsencode(str(tree)), n))]
    if gone:
        subprocess.run(["git", "update-index", "-z", "--skip-worktree", "--stdin"], env=env, input=b"\0".join(gone) + b"\0",
                       capture_output=True, timeout=300, check=True)
    (box / GIT_NOTE).write_text(json.dumps({"sha": sha, "binds": binds}), encoding="utf-8")


def item_rev(sha):
    """The rev the item_prose grant reads: the candidate itself, for make_box and the reach probe alike."""
    return sha


def grant_items(box, source, rev):
    """tree/infrastructure/state/items as of rev, read only (_snapshot); a rev with no item file is no grant."""
    box = Path(box)
    tree = box / "tree"
    _snapshot(source, rev, [ITEMS], tree, box)
    n = sum(len(fn) for _, _, fn in os.walk(tree / ITEMS))
    if not n:
        raise RuntimeError("item grant: no %s at %s" % (ITEMS, str(rev)[:12]))
    (box / ITEM_NOTE).write_text(json.dumps({"rev": rev, "files": n}), encoding="utf-8")


def item_reads(box):
    """-> {rev, files} when the box was made with the item_prose grant, else {}."""
    try:
        with open(os.path.join(str(box), ITEM_NOTE), encoding="utf-8") as f:
            got = json.load(f)
        return got if isinstance(got, dict) and got.get("files") else {}
    except (OSError, ValueError):
        return {}


def git_reads(box):
    """-> [(object store, its path in the box)] a git-granted box binds read only, else []."""
    try:
        with open(os.path.join(str(box), GIT_NOTE), encoding="utf-8") as f:
            binds = json.load(f).get("binds") or []
    except (OSError, ValueError, AttributeError):
        return []
    root = os.path.abspath(str(box)) + "/"
    return [(s, d) for s, d in (b for b in binds if isinstance(b, list) and len(b) == 2)
            if isinstance(s, str) and isinstance(d, str) and _SAFE.match(s) and _SAFE.match(d) and d.startswith(root)]


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


# What a blind checker reads of the work: the obligations and the paths, never the worker's account of them. A finish's
# evidence ("I rejected A and B because ...; 3 passed") and a contract's `why`, `by_gen` and game `why` are reasoning and
# history (CHECKER_PROMPT_FIX_WORKER_REASONING_LEAK). `no_offline` stays: it is a claim the checker is told to test.
BLIND_CONTRACT = ("proof", "live", "offbox")
PATH_RX = re.compile(r"(?:[A-Za-z]:\\|/|~/)?(?:[\w.~-]+[/\\])+[\w.-]+")


def blind_contract(contract):
    c = contract or {}
    out = {k: c[k] for k in BLIND_CONTRACT if c.get(k)}
    g = c.get("game") or {}
    if g:
        out["game"] = {k: g[k] for k in ("clauses", "no_offline") if g.get(k)}
    return out


def evidence_paths(evidence, cap=20):
    """The path-shaped words of a finish's evidence, in order, once each; the prose around them is dropped."""
    seen = []
    for m in PATH_RX.finditer(evidence or ""):
        w = m.group(0).rstrip(".,;:)")
        if w not in seen:
            seen.append(w)
    return seen[:cap]


def blind_lines(st):
    paths = evidence_paths(st["candidate"].get("evidence"))
    return ["", "Contract: %s" % json.dumps(blind_contract(st["contract"])),
            "Paths the worker named (its account of them is withheld: judge by your own runs): %s"
            % (", ".join(paths) or "none")]


def marker_prompt(st, text, box, adapter_names=()):
    """The checker's words, its way to the change and its way to a verdict being the box's."""
    c = st["candidate"]
    qv = shlex.quote(str(box) + "/verdict")     # a box path with a space still runs
    return "\n".join([
        "You are a blind checker. You did not do this work and you have no record of how it went. Your cwd is a clean "
        "export of commit %s, with no git history." % c["sha"] if not git_reads(box) else
        "You are a blind checker. You did not do this work and you have no record of how it went. Your cwd is a clean "
        "export of commit %s with a read-only git history at it (a reach repair granted it): HEAD is that commit, "
        "there is no branch or remote, and every ancestor reads. Commit messages, and the excluded folders git can still "
        "show, are workers' words, not evidence: judge by your own runs." % c["sha"],
        *RULE,
        *(["%s/ is in your tree as of %s (a reach repair granted it), read only: it is the filers' item prose, not "
           "evidence the work was done." % (ITEMS, str(item_reads(box)["rev"])[:12])] if item_reads(box) else []),
        "Then run exactly one of:",
        "  python3 %s PASS \"what you ran and saw\"" % qv,
        "  python3 %s WEAK \"the runs you made and what each showed, then each gap and the mutant or probe that "
        "shows it, then a STRONG: line and a LETS THROUGH: line\"" % qv,
        "  python3 %s FAIL \"what is wrong, so the next worker can fix it\" --defect \"CAUSE: one wrong thing\" [--defect ...] "
        "[--control \"how your instrument showed it can see\"] [--unreached \"what you also could not reach\"]" % qv,
        "  python3 %s UNMEASURED \"CANNOT REACH: what, and the command that showed it; then what you did check\" "
        "--unreached \"one thing out of reach, and the command that showed it\" [--unreached ...] "
        "[--propose NAME_OR_PATH ...]" % qv,
        "If you say UNMEASURED, you own the repair of your own eyes: add one --propose per fix, either the name of a "
        "supervisor offbox adapter that would read it from outside (%s) or an absolute path that, bound read only into "
        "this box, would let you read it. Relentless probes your proposal from inside this wall, applies it as its own "
        "change and checks this same commit once more; only if your proposal fails its probe is a ticket filed. A "
        "proposal only adds read access: the store, transcripts, memory and credentials are never opened."
        % (", ".join(sorted(adapter_names)) or "see relentless_rules.json offbox_adapters"),
        *offbox_lines(st["contract"], box),
        *blind_lines(st),
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


def refusal(word, defects, unreached, controls=None):
    """-> why a structured verdict is refused at the door (the CLI and the verdict script say the same), or None. Only ever
    used where a checker is there to read it: a verdict already on disk is never refused, read_as reads it."""
    if defects is None and unreached is None:
        return None
    if any(parse_defect(d)[0] == "product" for d in defects or []) and not clean_list(controls):
        return ("a product: defect needs a --control: how you showed your instrument can see (green on a known-good case, "
                "or it catches a fault you put in); without one, say unknown:")
    if clean_list(controls) and not defects:
        return "--control backs a product: defect only"
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
            "unreached": clean_list(v.get("unreached")), "proposals": clean_list(v.get("proposals")),
            "controls": clean_list(v.get("controls")), "at": at}


# ---- the cause of each defect (CHECKER_VERDICT_BUILD_CAUSE_BEFORE_RETURN; plan design/RimMandrake/
# relentless_recovery_plan_2026-11-05.md step 5, catalog class d: "judges unable to judge throwing things back to fix
# without fixing the measurement"). Only a VALIDATED product defect goes back to a builder or earns a strike: the cause is
# product, the defect cites the candidate's change (a path its diff touches) or behaviour (the contract's proof), and the
# Marker says how its instrument passed a control. A measurement defect goes to the proof road on the same sha; an
# environment defect opens an Operations alarm keyed on the dependency and waits for diagnosis; unknown - and anything
# untagged, or a product claim that fails validation - waits for diagnosis, never a builder.
CAUSES = ("product", "measurement", "environment", "unknown")
PRODUCT, MEASUREMENT, ENVIRONMENT, UNKNOWN = CAUSES
_TAG = re.compile(r"^\s*\[?\s*(product|measurement|environment|unknown)\s*\]?\s*:\s*", re.I)


def tagged(line):
    """-> the cause a defect line opens with, or None when it carries none."""
    m = _TAG.match(line or "")
    return m.group(1).lower() if m else None


def parse_defect(line):
    """-> (cause, text). An untagged line (an old verdict, a hand-written file) is unknown: never guessed product."""
    m = _TAG.match(line or "")
    if not m:
        return UNKNOWN, (line or "").strip()
    return m.group(1).lower(), line[m.end():].strip()


# which dependency an environment defect names: the key Operations groups one incident under
DEPENDENCIES = (
    ("disk", re.compile(r"ENOSPC|no space left|disk (is )?full|out of (disk|space)|quota exceeded on|\bdf\b", re.I)),
    ("account", re.compile(r"\b429\b|rate[- ]limit|usage limit|out of tokens|credit|overloaded|\b529\b", re.I)),
    ("remote_host", re.compile(r"\bssh\b|tailscale|steve|host (is )?(down|unreachable)|connection (refused|reset|timed out)",
                                re.I)),
    ("game", re.compile(r"\bgame\b|bridge|mod list|modsconfig|not in the load|missing_mods|\bsave\b|player\.log|rimworld",
                         re.I)),
    ("network", re.compile(r"\bdns\b|network|unreachable|timed? ?out", re.I)),
)


def dependency(text):
    """-> the dependency an environment defect's words name (disk, account, remote_host, game, network), else other."""
    for key, rx in DEPENDENCIES:
        if rx.search(text or ""):
            return key
    return "other"


_PATH_RX = re.compile(r"^diff --git a/(\S+) b/(\S+)", re.M)


def changed_paths(box):
    """-> the paths the candidate's change.diff touches ([] when the box or its diff is gone)."""
    try:
        d = Path(box, "change.diff").read_text(encoding="utf-8", errors="replace")
    except (OSError, TypeError):
        return []
    return sorted({p for m in _PATH_RX.finditer(d) for p in m.groups()})


_STOP = {"python3", "python", "bash", "sh", "src", "rimmandrake", "rimflow", "utils", "only", "run", "selftests", "py",
         "no", "cache", "the", "and", "with", "item", "run_selftests"}


def _proof_tokens(proof):
    """The proof's own identifiers a defect may cite as behaviour: script stems, test names (selftest_x), long words."""
    out = set()
    for w in re.findall(r"[A-Za-z_][A-Za-z0-9_.\-/]{3,}", proof or ""):
        stem = w.rsplit("/", 1)[-1]
        stem = stem[:-3] if stem.endswith(".py") else stem
        if stem.lower() not in _STOP and ("_" in stem or "." in w or "/" in w):
            out.add(stem.lower())
    return out


def cites(text, changed, proof):
    """True when a defect's words point at the candidate: a path its diff touches (whole, or its file name), or one of the
    contract proof's own identifiers (the behaviour the proof runs)."""
    t = (text or "").lower()
    for p in changed or []:
        p = p.lower()
        name = p.rsplit("/", 1)[-1]
        if p in t or (len(name) >= 5 and re.search(r"(?<![\w.])%s(?![\w])" % re.escape(name), t)):
            return True
    return any(re.search(r"(?<![\w])%s(?![\w])" % re.escape(k), t) for k in _proof_tokens(proof))


def causes(defects, controls=None, changed=(), proof=None):
    """-> one row per defect: {cause (what the Marker said), text, valid (product only: a control and a citation),
    acts (the cause the supervisor routes on: an unvalidated product is unknown)}."""
    rows = []
    has_control = bool(clean_list(controls))
    for d in clean_list(defects) or []:
        c, text = parse_defect(d)
        row = {"cause": c, "text": text[:600]}
        if c == PRODUCT:
            row["valid"] = has_control and cites(text, changed, proof)
            if not row["valid"]:
                row["why_not"] = ("no --control showed the instrument can see" if not has_control else
                                  "cites neither a path the candidate's diff touches nor the contract's proof")
        row["acts"] = c if c != PRODUCT or row["valid"] else UNKNOWN
        rows.append(row)
    return rows


def route(rows):
    """-> the cause a FAIL verdict is routed on: a validated product defect anywhere goes to the builder; else any
    unknown (an unvalidated product included) waits for diagnosis; else environment; else measurement. Empty -> unknown."""
    acts = [r["acts"] for r in rows or []]
    for c in (PRODUCT, UNKNOWN, ENVIRONMENT, MEASUREMENT):
        if c in acts:
            return c
    return UNKNOWN


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
    own fields): any observed defect is FAIL whatever the word; otherwise any unreached evidence is UNMEASURED under EVERY
    word, PASS and WEAK too (GPT round 2: a PASS that names evidence it could not reach is not a close). Only then is a WEAK
    read by acted_weak: only GAP:DIFF holds.
    Old format (both None): the prose, biased to FAIL - a defect named anywhere keeps or makes it FAIL, even under UNMEASURED."""
    if defects is not None or unreached is not None:
        defects, unreached = clean_list(defects) or [], clean_list(unreached) or []
        if defects:
            return "FAIL", None
        if unreached:       # every word, WEAK included: a GAP:OTHER WEAK narrows to PASS (CHECKER_WEAK_FIX_UNREACHED_READ_AS_PASS)
            return UNMEASURED, "; ".join(unreached)[:600]
        if word == UNMEASURED:      # the script refuses this; a hand-written file is read as prose
            return read_as(word, reasons)
        return acted_weak(word, reasons), None
    if word == UNMEASURED:
        if defect_said(reasons):
            return "FAIL", None
        return UNMEASURED, blind_reason(reasons) or (reasons or "")[:200]
    if word == "FAIL":
        b = blind_reason(reasons)
        if b and not defect_said(reasons):
            return UNMEASURED, b
    return acted_weak(word, reasons), None


def acted_weak(word, reasons):
    """The narrower WEAK is the live rule (owner by card 2026-11-03, "Narrow it now": 172 of 207 shadowed WEAKs were
    PASS under it). A WEAK holds only on GAP:DIFF, a hunk of this commit's own change put back with the proof still
    green; GAP:OTHER (a mutant the checker wrote elsewhere) is a PASS; an untagged WEAK stays WEAK, never guessed."""
    n = narrow_word(word, reasons)
    n = "WEAK" if n == "UNTAGGED" else n
    return n if n != "WEAK" or names_strong(reasons) else "PASS"


_STRONG = re.compile(r"(?i)\bSTRONG:\s*\S.{8,}")
_LETS = re.compile(r"(?i)\bLETS THROUGH:\s*\S.{8,}")


def names_strong(reasons):
    """JUDGE_WEAK_RETHINK_NAME_THE_STRONG_PROOF (owner 2026-11-05): a WEAK holds only when it names the strong proof and
    the product defect the current proof lets through. Measured before the change: 269 returns in
    7 days, 2 of a 15-sample fixed a product defect; the rest rewrote a test for a check the Judge had already run."""
    return bool(_STRONG.search(reasons or "") and _LETS.search(reasons or ""))


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


# An adapter's argv may name what the SUPERVISOR knows about this check, never worker text (CHECKER_REACH_BUILD_GIT_AND_GH_
# ADAPTERS: 5 holds wanted git history the box has no .git for): {sha} the candidate commit, {repo} the check's clean clone
# outside the wall (full history, checked out at {sha}). Each value is shape-checked before it fills a token.
_SLOT = re.compile(r"\{([a-z_]+)\}")
_SLOT_OK = {"sha": re.compile(r"^[0-9a-f]{40}$"), "repo": re.compile(r"^/[^\x00-\x1f{}]+$"),
            # the item under check (CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK gen 3: relentless_live_evidence reads its runs)
            "item": re.compile(r"^[A-Z][A-Z0-9_]{1,120}$")}


def fill_argv(argv, values):
    """-> (argv with every {slot} filled, None) or (None, why it cannot run). A slot outside _SLOT_OK, a missing value or a
    value of the wrong shape refuses the reading: nothing half-filled ever runs."""
    out = []
    for tok in argv:
        for slot in _SLOT.findall(tok):
            v = (values or {}).get(slot)
            if slot not in _SLOT_OK:
                return None, "refused: {%s} is not a supervisor value (%s)" % (slot, ", ".join(sorted(_SLOT_OK)))
            if not isinstance(v, str) or not _SLOT_OK[slot].match(v):
                return None, "not run: this check has no valid {%s}" % slot
            tok = tok.replace("{%s}" % slot, v)
        out.append(tok)
    return out, None


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
