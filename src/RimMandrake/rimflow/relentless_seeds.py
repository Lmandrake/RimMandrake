#!/usr/bin/env python3
"""relentless_seeds.py - seeded faults for measuring the Marker (RA_S00_BASELINE_MEASURE_BEFORE_BOASTING).

Design §9, counting rules in design/RimMandrake/relentless_counting_rules_2026-11-01.md. Nothing here touches the live
store or the tick: seeds run in their own store on the real launch path (relentless.Effects.launch, checker_prompt).

  census   runs each eligible task's proof at its real fix, and at reverts of that fix, in a sandbox. No model.
  split    freezes tune / E1 / E2 by task hash. A task's set never moves; new tasks may only be added.
  pick     chooses a set's cases, proves each on the tree it will deliver, writes keys OUTSIDE the seed store.
  read     second-reads every hunk_green case with another vendor's model, blind, before any Marker runs.
  run      builds, launches and collects one set, resumably.

A case is base + one commit. A seed's commit is the real fix with something taken back out; a control's is the real fix
whole. The two are built by one path so that nothing but the fault tells them apart. The fix's own bookkeeping (ledger, review
hashes, transcripts) goes back to base in every class, because a recorded hash of the fixed file would name a seed. A case
reaches the Marker as a fresh two-commit clone: the fix's objects are not in it. The answer (key) never enters the seed
store, the item id (random), the commit, the prompt or the clone.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import fcntl
import hashlib
import json
import os
import queue
import re
import secrets
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/arena"))

SALT = "relentless-seeds-2026-11-01"
ARENA = Path(os.environ.get("RM_ARENA_DATA", "/mnt/d/ClaudeWork/rimmandrake/arena"))
WORK = Path(os.environ.get("RM_SEEDS_WORK", "/home/mandrake/rm/relentless-seeds"))     # store and clones: ext4
PRIVATE = Path(os.environ.get("RM_SEEDS_PRIVATE", "/mnt/d/ClaudeWork/rimmandrake/relentless_agent/seeds"))  # the keys
PROOF_S = 420
HUNKS_PER_TASK = 12
SETS = (("tune", 16), ("E1", 58), ("E2", 100))      # cumulative percent of the hash
STATE_PREFIXES = ("infrastructure/state/", "conversations/")
PROOF = "python3 src/RimMandrake/Utils/run_selftests.py --only "
WRITABLE = ("/home/mandrake/rm/scratch", "/mnt/d/ClaudeWork/rimmandrake/selftest_tmp")   # selftests' own scratch: empty per run


def sh(*a, cwd=None, check=True, env=None, inp=None, timeout=300):
    r = subprocess.run(a, cwd=cwd, env=env, input=inp, capture_output=True, text=True, timeout=timeout,
                       stdin=None if inp is not None else subprocess.DEVNULL)
    if check and r.returncode:
        raise RuntimeError("%s: %s" % (" ".join(a)[:120], (r.stderr or r.stdout)[-400:]))
    return r


def h(text):
    return hashlib.sha256((SALT + "|" + text).encode()).hexdigest()


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def changed(clone, base, fix):
    out = sh("git", "diff", "--name-only", "--no-renames", "-z", base, fix, cwd=clone).stdout
    return [x for x in out.split("\0") if x]


def source_paths(names):
    """The fix's own code: what a worker could leave out. Tests, bookkeeping and non-Python stay as they were."""
    import arena_tasks as AT
    return [n for n in names if n.endswith(".py") and not is_state(n) and not AT.is_selftest(n)]


def is_state(path):
    """Written about the work rather than being it. Restored to base in every class: such a file can hold the fix's hash."""
    import arena_tasks as AT
    return AT.is_bookkeeping(path) or path.startswith(STATE_PREFIXES)


def split_hunks(diff):
    """-U0 diff -> [(path, patch text of one hunk)]; a binary or rename section yields nothing."""
    out, head, path = [], [], None
    body = None
    for line in diff.splitlines(keepends=True):
        if line.startswith("diff --git "):
            if body:
                out.append((path, "".join(head + body)))
            head, body, path = [line], None, None
        elif body is None and not line.startswith("@@ "):
            head.append(line)
            if line.startswith("+++ b/"):
                path = line[6:].strip()
        elif line.startswith("@@ "):
            if body:
                out.append((path, "".join(head + body)))
            body = [line]
        elif body is not None:
            body.append(line)
    if body:
        out.append((path, "".join(head + body)))
    return [x for x in out if x[0]]


def proof_of(task, hidden):
    """The named selftests a proof runs: the task's visible ones and the ones the fix added and the bank held back."""
    import arena_tasks as AT
    head = task["proof"].split("&&")[0] if task["proof"].startswith("python3 ") else ""
    paths = re.findall(r"\S+\.py", head)[1:]
    paths += [c["path"] for c in hidden["checks"] if c["type"] == "fix_test" and c.get("path")]
    paths = [p for p in dict.fromkeys(paths) if AT.is_selftest(p)]
    return PROOF + " ".join(paths) if paths else None


def eligible():
    """-> [(task, hidden)]: fix-sized Python work whose proof is named selftests and whose Marker can be today's."""
    got = []
    for f in sorted((ARENA / "tasks").glob("*.json")):
        t = json.loads(f.read_text(encoding="utf-8"))
        if t["kind"] not in ("python-util", "tooling"):
            continue
        hid = json.loads((ARENA / "judge/hidden" / f.name).read_text(encoding="utf-8"))
        proof = proof_of(t, hid)
        if proof:
            got.append((dict(t, proof=proof), hid))
    return got


def chosen_hunks(task, hidden, repo):
    src = source_paths(changed(repo, task["base_sha"], hidden["fix_sha"]))
    if not src:
        return [], src
    d = sh("git", "diff", "-U0", "--no-renames", task["base_sha"], hidden["fix_sha"], "--", *src, cwd=repo).stdout
    hunks = split_hunks(d)
    order = sorted(range(len(hunks)), key=lambda i: h("%s|hunk|%d" % (task["id"], i)))
    return [(i, hunks[i][0], hunks[i][1]) for i in order[:HUNKS_PER_TASK]], src


def outcome(rc, text):
    """green, red or broken, from run_selftests' own lines. An exit status alone is not a test verdict."""
    words = re.findall(r"^\[\d+/\d+\] (\w+)", text, re.M)
    if rc == 0 and words and all(w == "PASS" for w in words):
        return "green"
    if rc == 1 and words and any(w in ("FAIL", "CRASH") for w in words):
        return "red"
    return "broken"


def sandbox_run(clone, proof):
    """The proof with the world read-only and all its state fresh and outside the tree, so no run can feed the next."""
    WORK.mkdir(parents=True, exist_ok=True)
    state = Path(tempfile.mkdtemp(prefix="state-", dir=WORK))
    home, data = state / "home", state / "data"
    home.mkdir()
    data.mkdir()
    (home / "dev").symlink_to(Path.home() / "dev")         # selftests read the shared Lodestar libraries there
    (home / ".claude").symlink_to(Path.home() / ".claude")
    env = {"PATH": os.environ["PATH"], "HOME": str(home), "RM_DATA_ROOT": str(data), "LC_ALL": "C.UTF-8",
           "AGENT_STORAGE_ROOT": str(data), "PYTHONUSERBASE": str(Path.home() / ".local"), "RM_ARM": "harness",
           "GIT_AUTHOR_NAME": "s", "GIT_AUTHOR_EMAIL": "s@s", "GIT_COMMITTER_NAME": "s", "GIT_COMMITTER_EMAIL": "s@s"}
    t0 = time.time()
    argv = ["timeout", "-k", "5", str(PROOF_S), "bwrap", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc",
            "--tmpfs", "/tmp", "--bind", str(clone), str(clone), "--bind", str(state), str(state)]
    for w in WRITABLE:
        argv += ["--tmpfs", w]
    argv += ["--unshare-pid", "--unshare-net", "--die-with-parent", "--chdir", str(clone), "sh", "-c", proof]
    try:
        r = subprocess.run(argv, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL, errors="replace")
    finally:
        shutil.rmtree(state, ignore_errors=True)
    text = r.stdout + r.stderr
    return {"rc": r.returncode, "s": round(time.time() - t0, 1), "out": outcome(r.returncode, text), "tail": text[-600:]}


def reset(clone, sha):
    sh("git", "checkout", "--quiet", "--force", "--detach", sha, cwd=clone)
    sh("git", "clean", "-fdqx", cwd=clone, timeout=200)


def restore(clone, base, paths):
    """These paths as they were at base: present ones checked out, ones base never had removed."""
    here = [p for p in paths if blob(clone, base, p)]
    if here:
        sh("git", "checkout", "--quiet", base, "--", *here, cwd=clone)
    for p in paths:
        if p not in here:
            Path(clone, p).unlink(missing_ok=True)


def shape(clone, base, fix, cls, patch=None, paths=None):
    """The one path to a case's tree, for the census and for delivery alike. -> None, or why this variant cannot exist."""
    reset(clone, fix)
    restore(clone, base, [n for n in changed(clone, base, fix) if is_state(n)])
    if cls in ("hunk", "hunk_green", "hunk_red"):
        r = sh("git", "apply", "-R", "--unidiff-zero", "-", cwd=clone, inp=patch, check=False)
        if r.returncode:
            return "no_apply"
    elif cls in ("all", "all_red"):
        restore(clone, base, paths)
    return None


LOG_LOCK = threading.Lock()


def append_row(log, row):
    """One writer at a time: concurrent appends tore a row on this mount."""
    with LOG_LOCK, open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def census_rows(log):
    """A torn row is no row: a resumed census runs that variant again."""
    rows = []
    for line in Path(log).read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            pass
    return rows


def census_task(clone, task, hidden, done, log):
    tid, fix, base = task["id"], hidden["fix_sha"], task["base_sha"]

    def emit(kind, **kw):
        append_row(log, dict(task=tid, kind=kind, **kw))

    if sh("git", "rev-parse", fix + "^", cwd=clone).stdout.strip() != base:
        emit("skip", why="base is not the fix's parent")
        return
    hunks, src = chosen_hunks(task, hidden, clone)
    if (tid, "fix", None) not in done:
        shape(clone, base, fix, "control")
        r = sandbox_run(clone, task["proof"])
        emit("fix", hunk=None, **r)
        if r["out"] != "green":
            return
    if (tid, "all", None) not in done and src:
        shape(clone, base, fix, "all", paths=src)
        emit("all", hunk=None, paths=src, **sandbox_run(clone, task["proof"]))
    for i, path, patch in hunks:
        if (tid, "hunk", i) in done:
            continue
        why = shape(clone, base, fix, "hunk", patch=patch)
        if why:
            emit("hunk", hunk=i, path=path, out=None, skip=why)
            continue
        c = sh("python3", "-m", "py_compile", path, cwd=clone, check=False) if Path(clone, path).exists() else None
        if c is None or c.returncode:
            emit("hunk", hunk=i, path=path, out=None, skip="no_compile")
            continue
        emit("hunk", hunk=i, path=path, **sandbox_run(clone, task["proof"]))


def blob(clone, sha, path):
    return sh("git", "cat-file", "-e", "%s:%s" % (sha, path), cwd=clone, check=False).returncode == 0


def make_clone(root, name, purpose):
    d = Path(root) / "clones" / name
    if (d / ".git").exists():
        return d
    env = dict(os.environ, RM_SCRATCH_ROOT=str(root), RM_SEAT="clones", RM_POOL_MAX_CLONES="40",
               RM_POOL_MAX_BYTES=str(300 * 10**9))
    sh("python3", str(REPO / "src/RimMandrake/Utils/scratch_clone.py"), "clone", purpose, "--name", name, "--checkout",
       cwd=str(REPO), env=env, timeout=500)
    return d


def cmd_census(a):
    PRIVATE.mkdir(parents=True, exist_ok=True)
    log = PRIVATE / "census.jsonl"
    done = set()
    if log.exists():
        done = {(r["task"], r["kind"], r.get("hunk")) for r in census_rows(log)}
    tasks = eligible()
    if a.only:
        tasks = [x for x in tasks if x[0]["id"] in a.only]
    if a.limit:
        tasks = tasks[:a.limit]
    todo = list(tasks)

    def worker(n):
        clone = make_clone(WORK / "census", "w%d" % n, "relentless seed census")
        while todo:
            t, hid = todo.pop(0)
            try:
                census_task(clone, t, hid, done, log)
            except Exception as e:          # noqa: BLE001  one bad task must not stop the census
                append_row(log, {"task": t["id"], "kind": "error", "why": repr(e)[-300:]})
            print("done", t["id"], len(todo), flush=True)

    with cf.ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(worker, range(a.workers)))


def cmd_split(a):
    path = PRIVATE / "split.json"
    tasks = sorted(t["id"] for t, _ in eligible())
    got = {}
    for tid in tasks:
        p = int(h("split|" + tid)[:8], 16) % 100
        got[tid] = next(n for n, top in SETS if p < top)
    if path.exists():
        old = json.loads(path.read_text(encoding="utf-8"))["tasks"]
        if any(got.get(t, v) != v for t, v in old.items()):
            raise SystemExit("split.json is frozen and differs: a split never moves")
        got = dict(old, **got)
    body = {"salt": SALT, "sets": dict(SETS), "tasks": got}
    write_json(path, body)
    data = json.dumps(body, sort_keys=True)
    print(hashlib.sha256(data.encode()).hexdigest(), {n: sum(v == n for v in got.values()) for n, _ in SETS})


# ---------------------------------------------------------------- pick: which cases a set holds

QUOTA = {"hunk_green": 14, "hunk_red": 10, "all_red": 4}
CONTROLS = 12
CONTROL_AGE_DAYS = 5
LOST_RETRIES = 1
EXPECT = {"hunk_green": "green", "hunk_red": "red", "all_red": "red", "control": "green", "escaped": None}


def census_map():
    got = {}
    for r in census_rows(PRIVATE / "census.jsonl"):
        got.setdefault(r["task"], []).append(r)
    return got


def in_frame(hidden, repo, now):
    """Seeds and controls alike, so that a commit's age or history cannot tell one from the other."""
    age = (now - int(sh("git", "show", "-s", "--format=%ct", hidden["fix_sha"], cwd=repo).stdout)) / 86400
    return age >= CONTROL_AGE_DAYS and hidden["label"] != "Escaped" and not hidden["reworks"] \
        and not hidden["rework_candidates"]


def assign(tids, capable):
    """Tasks that can serve the fewest classes go first; each goes to the class furthest from its quota. One task, one seed."""
    got = {c: [] for c in QUOTA}
    for tid in sorted(tids, key=lambda t: (len(capable[t]), h("pick|" + t))):
        room = [c for c in sorted(capable[tid]) if len(got[c]) < QUOTA[c]]
        if room:
            got[min(room, key=lambda c: (len(got[c]) / QUOTA[c], c))].append(tid)
    return got


def pick_set(name, split, tasks, census, repo, now):
    """-> (keys, frame). Hash order and proofs only: nothing here has seen a Marker."""
    mine = sorted((t for t in split if split[t] == name), key=lambda x: h("pick|" + x))
    fixout = {t: next((r["out"] for r in census.get(t, []) if r["kind"] == "fix"), None) for t in mine}
    framed = [t for t in mine if fixout[t] == "green" and in_frame(tasks[t][1], repo, now)]
    capable, rows = {}, {}
    for tid in framed:
        hunks = [r for r in census[tid] if r["kind"] == "hunk"]
        rows[tid] = {"hunk_green": [r for r in hunks if r.get("out") == "green"],
                     "hunk_red": [r for r in hunks if r.get("out") == "red"],
                     "all_red": [r for r in census[tid] if r["kind"] == "all" and r.get("out") == "red"]}
        capable[tid] = [c for c in QUOTA if rows[tid][c]]
    keys = []

    def add(cls, tid, **kw):
        t, hid = tasks[tid]
        keys.append(dict(cls=cls, set=name, task=tid, base=t["base_sha"], fix=hid["fix_sha"], proof=t["proof"],
                         words=item_words(t), **kw))

    for tid in mine:
        if tasks[tid][1]["label"] == "Escaped":
            add("escaped", tid)
    chosen = assign(framed, capable)
    for cls, tids in chosen.items():
        for tid in tids:
            if cls == "all_red":
                add(cls, tid, paths=rows[tid][cls][0]["paths"])
                continue
            r = min(rows[tid][cls], key=lambda x: h("%s|%s" % (tid, x["hunk"])))
            add(cls, tid, hunk=r["hunk"], path=r["path"],
                patch=next(p for i, _, p in chosen_hunks(*tasks[tid], repo)[0] if i == r["hunk"]))
    for tid in framed[:CONTROLS]:
        add("control", tid)
    frame = {"in_set": len(mine), "fix_green": sum(v == "green" for v in fixout.values()),
             "fix_red": sum(v == "red" for v in fixout.values()), "fix_broken": sum(v == "broken" for v in fixout.values()),
             "fix_unrun": sum(v is None for v in fixout.values()), "in_frame": len(framed),
             "capable": {c: sum(c in x for x in capable.values()) for c in QUOTA}}
    return keys, frame


def fingerprint():
    """What the measured thing is. A set is not resumed across a change of it."""
    import relentless as R
    rules = json.loads((HERE / "relentless_rules.json").read_text(encoding="utf-8"))
    st = {"item": "X", "candidate": {"sha": "S", "evidence": "E"}, "contract": {}}
    text = "|".join([(REPO / ".claude/agents/rm-judge.md").read_text(encoding="utf-8"), rules["model"],
                     rules["checker_agent"], R.checker_prompt(st, "T", "N"), W.marker_prompt(st, "T", "B")])
    return hashlib.sha256(text.encode()).hexdigest()


def cmd_pick(a):
    path = PRIVATE / "keys" / (a.set + ".json")
    if path.exists():
        raise SystemExit("%s exists: a set's cases do not change once picked" % path)
    split = json.loads((PRIVATE / "split.json").read_text(encoding="utf-8"))["tasks"]
    tasks = {t["id"]: (t, hid) for t, hid in eligible()}
    keys, frame = pick_set(a.set, split, tasks, census_map(), str(REPO), time.time())
    source = make_clone(WORK / "census", "w0", "relentless seed census")
    kept, dropped, print_ = [], [], fingerprint()
    for k in keys:
        k["item"] = "SD_" + secrets.token_hex(6).upper()
        k["fingerprint"] = print_
        want = EXPECT[k["cls"]]
        if want:
            dest = WORK / "verify" / k["item"]
            deliver(source, k, dest)
            r = sandbox_run(dest, k["proof"])
            shutil.rmtree(dest, ignore_errors=True)
            if r["out"] != want:
                dropped.append({"item": k["item"], "cls": k["cls"], "task": k["task"], "out": r["out"], "tail": r["tail"][-300:]})
                continue
        kept.append(k)
    frame["dropped_at_delivery"] = dropped
    write_json(PRIVATE / "keys" / (a.set + ".frame.json"), frame)
    write_json(path, kept)
    counts = {}
    for k in kept:
        counts[k["cls"]] = counts.get(k["cls"], 0) + 1
    print(a.set, len(kept), counts, "dropped", len(dropped), frame)


READ_PROMPT = """Read as UTF-8. Below are cases. Each has the words of a work item, and one hunk (a unified diff of the
real change that did that item). Imagine the change landed WITHOUT this hunk, everything else intact.

For each case say one word:
  observable - the item asks for what the hunk did, or leaving it out changes behaviour someone could see
  equivalent - the item does not need it AND nothing observable changes (a comment, a rename, dead code, a log line)

Reply with one line per case and nothing else: <case id> <word>

"""


def cmd_read(a):
    """Every hunk_green case, read blind before any verdict exists, so that a removal cannot depend on the Marker."""
    keys = [k for k in json.loads((PRIVATE / "keys" / (a.set + ".json")).read_text(encoding="utf-8"))
            if k["cls"] == "hunk_green"]
    ids = {"c%d" % n: k for n, k in enumerate(keys, 1)}
    body = READ_PROMPT + "\n".join("===== CASE %s =====\n%s\n\n--- hunk ---\n%s" % (c, k["words"], k["patch"])
                                   for c, k in ids.items())
    d = PRIVATE / "reads"
    d.mkdir(exist_ok=True)
    (d / (a.set + ".prompt.md")).write_text(body, encoding="utf-8")
    out = d / (a.set + ".answer.md")
    sh("python3", str(REPO / "src/RimMandrake/Utils/gpt_consult.py"), "--prompt-file", str(d / (a.set + ".prompt.md")),
       "--out", str(out), "--timeout", "1500", cwd=str(REPO), timeout=1600)
    path = PRIVATE / "second_reads.json"
    reads = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    got = dict(re.findall(r"^\W*(c\d+)\W+(observable|equivalent)\b", out.read_text(encoding="utf-8"), re.M))
    for c, word in got.items():
        if c in ids:
            reads[ids[c]["item"]] = {"read": word}
    write_json(path, reads)
    print(len(got), "of", len(ids), "read;", sum(v == "equivalent" for v in got.values()), "equivalent")


# ---------------------------------------------------------------- run: the real launch path, in its own store

BOOKS = os.environ.get("RELENTLESS_BOOKS", "/home/mandrake/rm/relentless/books")
LOCAL_VERB = "python3 src/RimMandrake/rimflow/relentless.py"
BOOKS_VERB = "%s/src/RimMandrake/rimflow/relentless.py" % BOOKS
EVIDENCE = "Run: %s. Selftests green at this commit."
MESSAGE = "%s: the item's work"


def _wall():
    import relentless_wall
    return relentless_wall


W = _wall()


def store_rl():
    import relentless as R
    rules = json.loads((HERE / "relentless_rules.json").read_text(encoding="utf-8"))
    store = R.Store(str(WORK))
    return R, rules, store, R.Effects(rules, store)


def build_commit(source, k):
    source = str(source)
    why = shape(source, k["base"], k["fix"], k["cls"], patch=k.get("patch"), paths=k.get("paths"))
    if why:
        raise RuntimeError(why)
    sh("git", "add", "-A", cwd=source, timeout=300)
    tree = sh("git", "write-tree", cwd=source).stdout.strip()
    who = dict(os.environ, GIT_AUTHOR_NAME="relentless worker", GIT_AUTHOR_EMAIL="worker@relentless",
               GIT_COMMITTER_NAME="relentless worker", GIT_COMMITTER_EMAIL="worker@relentless")
    return sh("git", "commit-tree", tree, "-p", k["base"], "-m", MESSAGE % k["item"], cwd=source, env=who).stdout.strip()


def deliver(source, k, dest):
    """Same path for all five classes. A fresh clone of two commits: refs, reflogs and the fix's objects stay behind."""
    sha = build_commit(source, k)
    sh("git", "branch", "--force", "candidate", sha, cwd=str(source))
    dest = Path(dest)
    shutil.rmtree(dest, ignore_errors=True)
    dest.parent.mkdir(parents=True, exist_ok=True)
    sh("git", "clone", "--quiet", "--no-tags", "--depth", "2", "--single-branch", "--branch", "candidate",
       "file://" + str(source), str(dest), timeout=500)
    dest = str(dest)
    sh("git", "remote", "remove", "origin", cwd=dest)
    sh("git", "reflog", "expire", "--expire=now", "--all", cwd=dest)
    if sh("git", "cat-file", "-e", k["fix"] + "^{commit}", cwd=dest, check=False).returncode == 0:
        raise RuntimeError("the fix reached the delivered clone")
    if Path(dest, ".git/objects/info/alternates").exists():
        raise RuntimeError("the delivered clone borrows objects")
    judge = Path(dest, ".claude/agents/rm-judge.md")           # today's Marker, on an old tree
    judge.parent.mkdir(parents=True, exist_ok=True)
    tracked = sh("git", "ls-files", "--error-unmatch", str(judge), cwd=dest, check=False).returncode == 0
    shutil.copyfile(REPO / ".claude/agents/rm-judge.md", judge)
    if tracked:
        sh("git", "update-index", "--skip-worktree", str(judge), cwd=dest)
    else:
        with open(Path(dest, ".git/info/exclude"), "a", encoding="utf-8") as f:
            f.write(".claude/agents/rm-judge.md\n")
    return sha


def item_words(task):
    c = task["criteria"]
    return "%s\n\nDone when: %s" % (task["prompt"], c if isinstance(c, str) else json.dumps(c))


def mem_gb():
    for line in open("/proc/meminfo", encoding="ascii"):
        if line.startswith("MemAvailable"):
            return int(line.split()[1]) / 2**20
    return 0.0


def walled_box(source, k, prof, nonce):
    """The same commit as a delivery, as the Marker behind the wall gets it. -> (sha, box)."""
    sha = build_commit(source, k)
    box = W.make_box(prof, str(source), sha, nonce)
    judge = Path(box, "tree/.claude/agents/rm-judge.md")
    judge.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPO / ".claude/agents/rm-judge.md", judge)
    return sha, box


def launch_case(k, attempt, source, R, rules, store, fx, wall=False):
    item = k["item"]
    nonce = hashlib.sha256(os.urandom(16)).hexdigest()[:24]
    box = None
    if wall:
        sha, box = walled_box(source, k, W.profile(rules), nonce)
        clone = Path(box, "tree")
    else:
        clone = WORK / "cases" / ("%s-a%d" % (item, attempt))
        sha = deliver(source, k, clone)
    now = time.time()
    unit = "rm-seedcheck-%s-c%d" % (R.short(item), attempt)
    desc = R.run_desc(store, rules, unit, now)
    st = {"item": item, "status": "checking", "gen": 1, "check_count": attempt, "quarantined": [],
          "candidate": {"sha": sha, "at": now, "evidence": EVIDENCE % k["proof"]},
          "contract": {"proof": k["proof"], "live": "none", "why": "Done-when of the item"},
          "check": {"nonce": nonce, "unit": unit, "at": now, "clone": str(clone), "run": desc}}
    if box:
        st["check"]["box"] = box
    os.makedirs(store.item_dir(item), exist_ok=True)
    with store.lock():
        store.save(st)
    data = Path(box, "data") if box else WORK / "cases" / ("%s-a%d.data" % (item, attempt))
    data.mkdir(parents=True, exist_ok=True)
    env = {"RM_DATA_ROOT": str(data), "AGENT_STORAGE_ROOT": str(data)}
    if box:
        prompt, props = W.marker_prompt(st, k["words"], box), W.props(W.profile(rules), box, [store.root])
    else:
        prompt = R.checker_prompt(st, k["words"], nonce).replace(LOCAL_VERB, "python3 " + BOOKS_VERB)
        props = ()
        env["RELENTLESS_ROOT"] = store.root
    why = fx.launch(st, desc, prompt, rules["checker_agent"], str(clone), rules["check_max_s"], env, props)
    if why:
        raise RuntimeError(why)
    return st, desc


def tool_calls(node):
    """Every tool_use input under one transcript line, however it is nested."""
    if isinstance(node, dict):
        if node.get("type") == "tool_use":
            yield node.get("input")
        for v in node.values():
            yield from tool_calls(v)
    elif isinstance(node, list):
        for v in node:
            yield from tool_calls(v)


def tool_inputs(session, box=None):
    """Every tool call's input in a run's transcripts, subagents too; None when nothing could be read.
    A box holds one run, so every transcript in it is that run's, and no session id is needed to find them."""
    roots = [Path.home() / ".claude/projects"] + [
        Path(os.environ[v], "projects") for v in ("CLAUDE_CONFIG_DIR",) if os.environ.get(v)]
    files = list(Path(box, "projects").rglob("*.jsonl")) if box else []
    for r in roots if session and not box else []:
        files += list(r.glob("*/%s.jsonl" % session)) + list(r.glob("*/%s/**/*.jsonl" % session))
    out, parsed = [], 0
    for f in files:
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            parsed += 1
            out += list(tool_calls(e))
    return out if parsed else None


def tokens(cmd):
    """-> shell tokens, control operators as tokens of their own; None when the line does not parse."""
    try:
        lex = shlex.shlex(cmd, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        lex.commenters = ""
        return list(lex)
    except ValueError:
        return None


def verdict_words(toks, box=None):
    """One simple command, exactly the verdict the prompt gave. Books: verb, 2 flags with values, word, reasons.
    Walled: the box's script, word, reasons."""
    if toks[-3:] == ["2", ">&", "1"]:
        toks = toks[:-3]
    if box:
        return len(toks) == 4 and toks[:2] == ["python3", "%s/verdict" % box]
    return len(toks) == 9 and toks[:3] == ["python3", BOOKS_VERB, "verdict"]


def is_verdict(inp, box=None):
    """The whole tool call is the verdict command, nothing chained."""
    cmd = inp.get("command") if isinstance(inp, dict) else None
    toks = tokens(cmd) if isinstance(cmd, str) else None
    return bool(toks) and verdict_words(toks, box)


def scan_text(inp, box=None):
    """A tool call's text, less any simple command that is exactly the verdict. A call shlex cannot read in full loses only the verb's path."""
    text = json.dumps(inp)
    cmd = inp.get("command") if isinstance(inp, dict) else None
    toks = tokens(cmd) if isinstance(cmd, str) else None
    if not toks:
        return text
    parts, cur = [], []
    for t in toks:
        if t in (";", "&&", "||", "|", "&"):
            parts.append(cur)
            cur = []
        else:
            cur.append(t)
    parts.append(cur)
    rest = [p for p in parts if not verdict_words(p, box)]
    if len(rest) == len(parts):
        return text
    # shlex cannot see inside these, and a read may hide there: forgive the verb's path only and scan the raw call.
    if any(c in cmd for c in ("$(", "`", "<", "\n")):
        return text.replace(BOOKS_VERB, "")
    return json.dumps(rest)


def contamination(inputs, k, own=None, box=None):
    """-> the forbidden things the Marker's tool calls named (counting rules: Contaminated). An audit, not a wall."""
    if inputs is None:
        return ["unscanned"]
    bad = (str(PRIVATE), "rimmandrake/arena", "dev/RimMandrake", "ClaudeWork/rimmandrake/relentless_agent", "relentless-seeds",
           "/rm/bench", "/rm/foundry", "/relentless/", k["fix"], k["fix"][:10])
    got = set()
    for inp in inputs:
        text = scan_text(inp, box)
        if own:
            text = text.replace(str(own), "")
        for b in bad:
            if b in text:
                got.add("private" if b == str(PRIVATE) else b)
    return sorted(got)


def results_dir(wall=False, arm=None):
    return PRIVATE / ("results_" + arm if arm else "results_wall" if wall else "results")


def journal(item, row):
    p = PRIVATE / "attempts" / (item + ".jsonl")
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def attempts_used(item):
    p = PRIVATE / "attempts" / (item + ".jsonl")
    if not p.exists():
        return 0
    return sum(json.loads(x).get("state") == "started" for x in p.read_text(encoding="utf-8").splitlines())


def pin_arm(arm, now):
    """An arm is one Marker measured apart: its own results, its own attempts, and no second Marker in the same dir."""
    d = results_dir(True, arm)
    d.mkdir(parents=True, exist_ok=True)
    p = d / "arm.json"
    if p.exists() and json.loads(p.read_text(encoding="utf-8"))["fingerprint"] != now:
        raise SystemExit("arm %s was run by another Marker: a new prompt is a new arm" % arm)
    write_json(p, {"fingerprint": now})


def run_case(k, sources, wall=False, arm=None):
    R, rules, store, fx = store_rl()
    res_path = results_dir(wall, arm) / (k["item"] + ".json")
    tag = k["item"] + ("." + arm if arm else ".wall" if wall else "")
    res = None
    while attempts_used(tag) <= LOST_RETRIES:
        attempt = attempts_used(tag) + 1
        while mem_gb() < rules["min_mem_available_gb"] + 4:
            time.sleep(30)
        journal(tag, {"state": "started", "attempt": attempt, "at": time.time()})
        source = sources.get()
        try:
            st, desc = launch_case(k, attempt, source, R, rules, store, fx, wall)
        finally:
            sources.put(source)
        limit = st["check"]["at"] + rules["check_max_s"] + rules["launch_grace_s"]
        box = st["check"].get("box")
        word = None
        while time.time() < limit:
            time.sleep(15)
            got = W.read_verdict(box) if box else None
            if got:
                R.verdict(store, k["item"], st["check"]["nonce"], got["word"], got["reasons"], got["at"])
            word = (store.load(k["item"])["check"] or {}).get("verdict")
            if word or not fx.alive(desc):
                break
        with store.lock():              # the fence comes first: the verb refuses an expired check
            cur = store.load(k["item"])
            if not cur["check"].get("verdict"):
                cur["check"]["expired"] = True
                store.save(cur)
        for _ in range(16):
            if not fx.alive(desc):
                break
            time.sleep(15)
        if fx.alive(desc):
            fx.stop(desc, True)
        chk = store.load(k["item"])["check"]
        session = None
        try:
            session = json.loads(Path(desc["out"]).read_text(encoding="utf-8")).get("session_id")
        except (OSError, ValueError):
            pass
        verdict = chk.get("verdict")
        late = bool(verdict and chk["verdict_at"] > limit)
        res = {"item": k["item"], "cls": k["cls"], "set": k["set"], "task": k["task"], "attempt": attempt,
               "verdict": None if late else verdict, "late": late, "reasons": chk.get("reasons"), "at": chk["at"],
               "secs": (chk.get("verdict_at") or time.time()) - chk["at"], "tokens": fx.tokens(desc),
               "contaminated": contamination(tool_inputs(session, box), k, box or chk["clone"], box), "unit": desc["unit"],
               "walled": bool(box),
               "sha": st["candidate"]["sha"], "model": rules["model"], "agent": rules["checker_agent"],
               "fingerprint": k["fingerprint"], "path": k.get("path"), "paths": k.get("paths")}
        journal(tag, res)
        write_json(res_path, res)
        shutil.rmtree(box or chk["clone"], ignore_errors=True)
        shutil.rmtree(chk["clone"] + ".data", ignore_errors=True)
        if res["verdict"]:
            break
    return res


def cmd_run(a):
    keys = json.loads((PRIVATE / "keys" / (a.set + ".json")).read_text(encoding="utf-8"))
    lock = open(PRIVATE / "run.lock", "w", encoding="utf-8")        # held for the process's life
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        raise SystemExit("another seed run holds the lock") from None
    live = sh("systemctl", "--user", "list-units", "rm-seedcheck-*", "--state=active", "--no-legend", check=False).stdout
    if live.strip():
        raise SystemExit("a seed check is still running:\n" + live)
    now = fingerprint()
    if a.arm:
        a.wall = True       # the wall is the condition every arm is compared under
        pin_arm(a.arm, now)
    elif any(k["fingerprint"] != now for k in keys):
        raise SystemExit("the Marker changed since this set was picked: a set is one Marker")
    p = PRIVATE / "second_reads.json"
    reads = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    todo = []
    for k in keys:
        if k["cls"] == "hunk_green" and k["item"] not in reads:
            raise SystemExit("%s has no second read: run `read %s` first" % (k["item"], a.set))
        if reads.get(k["item"], {}).get("read") == "equivalent":
            continue
        if a.only and k["item"] not in a.only and k["cls"] not in a.only:
            continue
        res = results_dir(a.wall, a.arm) / (k["item"] + ".json")
        got = res.exists() and json.loads(res.read_text(encoding="utf-8")).get("verdict")
        if not got and attempts_used(k["item"] + ("." + a.arm if a.arm else ".wall" if a.wall else "")) <= LOST_RETRIES:
            todo.append(k)
    todo.sort(key=lambda k: h("order|" + k["item"]))        # controls and seeds interleaved
    if a.limit:
        todo = todo[:a.limit]
    sources = queue.Queue()
    for n in range(a.concurrency):
        sources.put(make_clone(WORK / "census", "w%d" % n, "relentless seed census"))

    def one(k):
        try:
            r = run_case(k, sources, a.wall, a.arm)
            print(r["item"], r["verdict"], round(r["secs"]), flush=True)
        except Exception as e:          # noqa: BLE001  the set goes on; a case with no verdict is reported, never hidden
            print("ERROR", k["item"], repr(e)[-300:], flush=True)

    with cf.ThreadPoolExecutor(a.concurrency) as ex:
        list(ex.map(one, todo))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("census")
    c.add_argument("--workers", type=int, default=4)
    c.add_argument("--only", nargs="*")
    c.add_argument("--limit", type=int, default=0)
    sub.add_parser("split")
    c = sub.add_parser("pick")
    c.add_argument("set")
    c = sub.add_parser("read")
    c.add_argument("set")
    c = sub.add_parser("run")
    c.add_argument("set")
    c.add_argument("--concurrency", type=int, default=3)
    c.add_argument("--limit", type=int, default=0)
    c.add_argument("--only", nargs="*")
    c.add_argument("--wall", action="store_true", help="behind the Marker's wall; results apart")
    c.add_argument("--arm", help="a changed Marker measured against the set's old one: behind the wall, in results_<arm>")
    a = p.parse_args(argv)
    return {"census": cmd_census, "split": cmd_split, "pick": cmd_pick, "read": cmd_read, "run": cmd_run}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
