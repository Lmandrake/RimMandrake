"""relentless_exam.py -- the acceptance exam, set BEFORE the build by a Setter that is not the builder
(RELENTLESS_BUILD_EXAM_BEFORE_BUILDER; owner-ordered pipeline redesign 2026-11-06, redesign_final.md §2 G3/G4, §3.2, §5 row 03).

Owner, 2026-11-05 ~23:20 PST: "So how are we ever going to overcome this failure of our testing apparatus, weak evidence,
poorly specified tests, etc?" Today the builder writes its own exam (relentless.contract), so a misread item yields a proof
that agrees with the misreading and both pass together, silently. Here a fresh Opus Setter (Judge mode, never the builder)
writes the exam against the item's base sha, and the supervisor VALIDATEs it mechanically before it counts:

  * every check runs in the Marker's box (relentless_wall.make_box, WP-02 toolchain) and must go RED on the base sha
    (`break.kind: base_red`, new behaviour) or GREEN on base and RED under the Setter's planted break (`patch`, preserved
    behaviour). A red counts only as an ASSERTION failure: an exit code the clause declares (default 1), its declared
    marker if any, and none of the not-a-measurement signatures (ImportError, missing file/tool, SyntaxError, timeout,
    exit 2/124/126/127/signal). `refusal codes: RED_NOT_ASSERTION, STAYS_GREEN, BASE_NOT_GREEN, PATCH_FAILED`.
  * a behavioural clause (`kind: behaviour`, the default) refuses an existence/grep-only check, linted by argv shape
    (test/ls/stat/grep/find/cat/wc..., or a shell/python -c body made only of those): EXISTENCE_ONLY. `kind: artifact` is
    allowed only where the item's own words ask for an artifact (a file, report, finding...): ARTIFACT_NOT_ASKED.
  * a planted break must change behaviour, not delete the file the check names or only delete files: BREAK_DELETES.
  * every clause is mapped from a sentence quoted out of the item's text, and every `## Done when` bullet of the item's
    prose is mapped: MAP_UNKNOWN_SENTENCE, MAP_UNMAPPED_CLAUSE, MAP_DONE_WHEN.
  * `exam_hash` = sha256 over the clauses + maps JSON, the item text, and the sha256 of EVERY file a check argv names
    (repo files at the base sha, and the Setter's own test files): a named test file that changes moves the hash.

Hold-outs are not written here (G4): the Marker writes them at mark time, so they never exist during the build.

SHADOW (this landing). relentless.contract() calls on_contract() when the FIRST contract of an item is set (the moment
before the builder edits): an exam is owed and one detached unit (`relentless_exam.py run ID`, the supervisor's own books
code) runs SET -> VALIDATE -> one resumed Setter turn on a refusal -> (second refusal: `arbiter_owed`, the arbiter is
WP-08's). Nothing here gates a close. The same unit then runs `catch`: for each candidate a Marker returned
(blind_fail/proof_weak) the validated exam is run at that sha; an assertion red is a return the exam WOULD have caught.
`relentless.py reading` carries summary() as `exam_shadow`. Shadow ends on a sample count (config `shadow_target`
items with a Marker verdict), never on elapsed days (G25).

Files (store-only in shadow: the builder's clone never holds them): <root>/store/exams/<ID>/
  owed.json, exam.json (frozen, with exam_hash), validation.json, files/ (the Setter's tests, run as tree/.exam/<name>),
  catch.jsonl, setter.out/.err. Format: infrastructure/state/exams/README.md.
"""
import argparse
import fcntl
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

CONFIG = os.path.join(HERE, "relentless_exam.json")
EXAM_DIR = ".exam"                  # the Setter's own files, copied into the box tree under this name for each run
REJECTS = ("blind_fail", "proof_weak")
STATES = ("owed", "setting", "validated", "refused", "arbiter_owed", "setter_failed")
TIMEOUT_MAX = 540
# a planted break of equal size inside the same second leaves a .pyc the import trusts: the break would read green
RUN_ENV = {"PYTHONDONTWRITEBYTECODE": "1"}

# a non-zero exit carrying one of these did not measure the clause: it never counts as a red (redesign_final G3 (1))
NOT_ASSERTION = (
    ("ImportError", re.compile(r"\b(ImportError|ModuleNotFoundError)\b")),
    ("missing file", re.compile(r"No such file or directory|can't open file|cannot find the path|FileNotFoundError")),
    ("missing tool", re.compile(r"command not found|not recognized as an internal or external command")),
    ("SyntaxError", re.compile(r"\b(SyntaxError|IndentationError)\b")),
    ("permission", re.compile(r"Permission denied|PermissionError")),
    ("usage", re.compile(r"^usage: ", re.M)),
)
NOT_ASSERTION_EXITS = {2: "exit 2 (usage/cannot start)", 124: "timeout", 126: "not executable", 127: "missing tool"}

EXISTENCE_TOOLS = {"test", "[", "[[", "ls", "stat", "grep", "egrep", "fgrep", "rg", "find", "cat", "wc", "head", "tail",
                   "file", "true", "echo", "realpath", "readlink"}
# a python -c body whose every call is one of these only asks whether a path exists or holds a string
_PY_EXIST_CALLS = {"os.path.exists", "os.path.isfile", "os.path.isdir", "os.path.getsize", "Path", "pathlib.Path", "exists",
                   "is_file", "is_dir", "open", "read", "read_text", "print", "sys.exit", "exit", "len", "any", "all"}
ARTIFACT_WORDS = re.compile(r"\b(file|report|finding|findings|document|doc|spec|table|list|page|sheet|note|record|"
                            r"inventory|census|ledger|log|csv|json|md|readme|plan|write[- ]?up|audit)\b", re.I)


def config(path=None):
    try:
        with open(path or os.environ.get("RELENTLESS_EXAM_CONFIG") or CONFIG, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"mode": "off"}


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


# ---------------------------------------------------------------------------------------------------------------- store
def exam_root(store):
    return store.p("exams")


def item_dir(store, item):
    return os.path.join(exam_root(store), item)


def _read(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    os.replace(tmp, path)


def _append(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")


def status(store, item):
    return _read(os.path.join(item_dir(store, item), "owed.json"))


def set_status(store, item, **kw):
    p = os.path.join(item_dir(store, item), "owed.json")
    rec = _read(p, {}) or {}
    rec.update(kw)
    _write(p, rec)
    return rec


# --------------------------------------------------------------------------------------------------- the contract hook
def owe(store, item, base, now, cfg=None, clone=None, origin="first_contract"):
    """-> True when this call made the exam owed. On an item's first contract, or (`origin` start_backfill) at the next
    start of one contracted before this hook landed; only in shadow/live mode, only while the shadow sample is short of
    `max_items`; never twice for one item."""
    cfg = config() if cfg is None else cfg
    if cfg.get("mode") not in ("shadow", "live") or not base:
        return False
    if status(store, item):
        return False
    root = exam_root(store)
    have = [d for d in (os.listdir(root) if os.path.isdir(root) else []) if os.path.isdir(os.path.join(root, d))]
    if len(have) >= int(cfg.get("max_items", 60)):
        return False
    set_status(store, item, state="owed", base=base, at=iso(now), mode=cfg["mode"], clone=clone, origin=origin)
    return True


def unit_name(item):
    return "rm-relentless-exam-" + hashlib.sha1(item.encode("utf-8")).hexdigest()[:10]


def kick(store, item, cfg=None, runner=subprocess.run):
    """Start the item's exam unit, detached (systemd-run --user): the builder's contract call never waits on a Setter.
    The unit runs the supervisor's books code, not the worker's clone (that may be reaped first). -> None or why not."""
    cfg = config() if cfg is None else cfg
    books = os.path.join(store.root, "books", "src", "RimMandrake", "rimflow", "relentless_exam.py")
    tool = books if os.path.exists(books) else os.path.abspath(__file__)
    d = item_dir(store, item)
    os.makedirs(d, exist_ok=True)
    max_s = int(cfg.get("unit_max_s", 3600))
    argv = ["systemd-run", "--user", "--quiet", "--collect", "--unit", unit_name(item),
            "-p", "StandardOutput=file:" + os.path.join(d, "unit.out"), "-p", "StandardError=file:" + os.path.join(d, "unit.err"),
            "-p", "RuntimeMaxSec=%d" % max_s, "--working-directory", os.path.dirname(tool),
            "--setenv", "RELENTLESS_ROOT=" + store.root, "--setenv", "PATH=" + os.environ.get("PATH", "/usr/bin:/bin"),
            "--", sys.executable, tool, "run", item]
    try:
        r = runner(argv, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        return "%s: %s" % (type(e).__name__, e)
    return ("systemd-run exit %d: %s" % (r.returncode, ((r.stdout or "") + (r.stderr or ""))[-200:])) if r.returncode else None


def live_roots():
    """The host's own supervisor store: only it owes exams. A selftest's temp store (82 relentless selftests call
    contract()) must never start a systemd unit."""
    import relentless
    return [relentless.DEFAULT_ROOT]


def on_contract(store, item, base, now=None, clone=None, cfg=None, kicker=None, roots=None, origin="first_contract"):
    """relentless.contract()'s call: an item's first contract was just set, before its builder edits. Owe the exam and
    start its unit. Never raises: shadow mode must not cost the builder its contract. -> what happened, in words."""
    try:
        if os.path.realpath(store.root) not in {os.path.realpath(x) for x in (live_roots() if roots is None else roots)}:
            return None
        now = time.time() if now is None else now
        cfg = config() if cfg is None else cfg
        if not owe(store, item, base, now, cfg, clone, origin):
            return None
        why = (kicker or kick)(store, item, cfg)
        if why:
            set_status(store, item, state="owed", kick_failed=why[:300])
            return "exam owed; unit did not start: " + why
        return "exam owed; Setter unit " + unit_name(item)
    except Exception as e:  # noqa: BLE001 - shadow: a fault here is recorded, never the builder's
        try:
            set_status(store, item, state="owed", hook_error="%s: %s" % (type(e).__name__, str(e)[:200]))
        except Exception:  # noqa: BLE001
            pass
        return None


def on_start(store, st, now=None, cfg=None, kicker=None, roots=None):
    """relentless._lease()'s call when an item starts a worker (EXAM_SHADOW_FILL_ITEMS_OLDER_THAN_EXAMS). An item whose
    contract was set before on_contract landed (2026-11-06) never had its first-contract moment here, so it would run
    wholly on the old path: at its next start (from queued, after a block or a game snag alike) it owes an exam against
    its current base, as a first contract would. No contract yet: its first contract owes it. Never raises."""
    if not st or not st.get("contract"):
        return None
    try:
        if status(store, st["item"]):
            return None
    except Exception:  # noqa: BLE001 - an unreadable owed.json is on_contract's to record
        pass
    return on_contract(store, st["item"], st.get("base"), now=now, clone=st.get("clone"), cfg=cfg, kicker=kicker,
                       roots=roots, origin="start_backfill")


# ---------------------------------------------------------------------------------------------------------- the lint
def _norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def done_when(prose):
    """-> the bullets under a '## Done when' heading of the item's prose (items/<ID>.md), or []."""
    out, on = [], False
    for ln in (prose or "").splitlines():
        if ln.startswith("#"):
            on = bool(re.match(r"^#+\s*done[- ]when\b", ln, re.I))
            continue
        m = re.match(r"^\s*(?:[-*]|\d+[.)])\s+(.*\S)", ln)
        if on and m:
            out.append(m.group(1))
    return out


def _words(argv):
    """-> the command words of a check: argv itself, or for `bash -c BODY` / `sh -c BODY` every command of BODY."""
    if len(argv) >= 3 and os.path.basename(argv[0]) in ("bash", "sh", "zsh") and argv[1] in ("-c", "-lc", "-ec"):
        cmds = []
        for part in re.split(r"&&|\|\||;|\||\n", argv[2]):
            try:
                w = shlex.split(part)
            except ValueError:
                w = part.split()
            w = [x for x in w if not re.match(r"^\w+=", x)]
            if w:
                cmds.append(w)
        return cmds
    return [argv]


def existence_only(argv):
    """-> why the check only asks whether something exists or contains a string, or None. By argv shape (G3 (2))."""
    if not argv:
        return "empty argv"
    cmds = _words(argv)
    if all(os.path.basename(c[0]) in EXISTENCE_TOOLS for c in cmds):
        return "only %s" % ", ".join(sorted({os.path.basename(c[0]) for c in cmds}))
    if os.path.basename(argv[0]).startswith("python") and len(argv) >= 3 and argv[1] == "-c":
        body = re.sub(r"'[^']*'|\"[^\"]*\"", "''", argv[2])
        imports = set(re.findall(r"(?:^|[;\n])\s*import\s+([\w.]+)", body)) | set(re.findall(r"\bfrom\s+([\w.]+)\s+import", body))
        calls = {re.sub(r"^.*\.(?=(exists|is_file|is_dir|read|read_text)$)", "", c) if not c.startswith(("os.", "sys.")) else c
                 for c in re.findall(r"([A-Za-z_][\w.]*)\s*\(", body)}
        if imports <= {"os", "os.path", "sys", "pathlib"} and calls <= _PY_EXIST_CALLS:
            return "python -c that only tests a path's existence/contents"
    return None


def named_files(argv):
    """-> repo-relative paths (or .exam/<name>) a check argv names: words that look like a file path."""
    out = []
    for c in _words(argv):
        for w in c[1:] if len(c) > 1 else c:
            if w.startswith("-") or "://" in w:
                continue
            if re.match(r"^(\.exam/|src/|infrastructure/|design/|tools/|\.claude/)[\w./@+-]+$", w) or \
                    re.match(r"^[\w.@+-]+(/[\w.@+-]+)+\.(py|sh|json|xml|md|cs|txt|yml|yaml|toml)$", w):
                out.append(w)
    return list(dict.fromkeys(out))


def _patch_paths(patch):
    """-> (paths touched, deleted paths, only_deletes) of a unified diff."""
    touched, deleted = [], []
    cur_a = None
    for ln in (patch or "").splitlines():
        if ln.startswith("--- "):
            cur_a = ln[4:].strip()
            cur_a = cur_a[2:] if cur_a.startswith("a/") else cur_a
        elif ln.startswith("+++ "):
            b = ln[4:].strip()
            if b == "/dev/null":
                deleted.append(cur_a)
                touched.append(cur_a)
            else:
                touched.append(b[2:] if b.startswith("b/") else b)
    return touched, deleted, bool(touched) and len(deleted) == len(touched)


def lint(exam, item_text, prose=""):
    """-> [{"clause", "code", "why"}]: the refusals that need no run. Pure."""
    bad = []

    def no(cid, code, why):
        bad.append({"clause": cid, "code": code, "why": why})

    clauses = exam.get("clauses") if isinstance(exam, dict) else None
    if not isinstance(clauses, list) or not clauses:
        return [{"clause": None, "code": "SCHEMA", "why": "no clauses"}]
    ids = set()
    asks_artifact = bool(ARTIFACT_WORDS.search(item_text or ""))
    for c in clauses:
        cid = c.get("id") if isinstance(c, dict) else None
        if not cid or cid in ids:
            no(cid, "SCHEMA", "every clause needs a unique id")
            continue
        ids.add(cid)
        chk, brk = c.get("check") or {}, c.get("break") or {}
        argv = chk.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x for x in argv):
            no(cid, "SCHEMA", "check.argv must be a non-empty list of strings")
            continue
        if not str(c.get("says") or "").strip():
            no(cid, "SCHEMA", "says: the clause in the item's words")
        kind = c.get("kind", "behaviour")
        if kind not in ("behaviour", "artifact", "live", "owner"):
            no(cid, "SCHEMA", "kind must be behaviour|artifact|live|owner")
        if kind == "behaviour":
            why = existence_only(argv)
            if why:
                no(cid, "EXISTENCE_ONLY", "a behavioural clause needs a check that runs the behaviour, not %s" % why)
        if kind == "artifact" and not asks_artifact:
            no(cid, "ARTIFACT_NOT_ASKED", "kind: artifact only where the item asks for an artifact")
        t = chk.get("timeout_s", 300)
        if not isinstance(t, int) or not 0 < t <= TIMEOUT_MAX:
            no(cid, "SCHEMA", "timeout_s must be 1..%d" % TIMEOUT_MAX)
        bk = brk.get("kind")
        if bk not in ("base_red", "patch"):
            no(cid, "BREAK_KIND", "break.kind must be base_red (new behaviour) or patch (preserved behaviour)")
        elif bk == "patch":
            patch = brk.get("patch") or ""
            touched, deleted, only_del = _patch_paths(patch)
            if not touched:
                no(cid, "SCHEMA", "break.patch is not a unified diff")
            names = set(named_files(argv))
            if only_del:
                no(cid, "BREAK_DELETES", "the break only deletes files; it must change behaviour")
            elif names & set(deleted):
                no(cid, "BREAK_DELETES", "the break deletes %s, which the check names" % ", ".join(sorted(names & set(deleted))))
            if any(p.startswith(EXAM_DIR + "/") for p in touched):
                no(cid, "BREAK_KIND", "the break edits the exam's own test, not the code under test")
        red = chk.get("red") or {}
        ex = red.get("exit", [1])
        if not isinstance(ex, list) or not ex or any((not isinstance(x, int)) or x in NOT_ASSERTION_EXITS or x <= 0 for x in ex):
            no(cid, "SCHEMA", "check.red.exit lists the assertion exit codes (positive, not 2/124/126/127)")
    maps = exam.get("maps") or {}
    if not isinstance(maps, dict) or not maps:
        no(None, "MAP_UNMAPPED_CLAUSE", "maps: {item sentence: [clause ids]} is required")
        maps = {}
    text = _norm(item_text)
    mapped = set()
    for sentence, cids in maps.items():
        if not _norm(sentence) or _norm(sentence) not in text:      # "" is a substring of everything
            no(None, "MAP_UNKNOWN_SENTENCE", "not the item's words: %r" % sentence[:120])
        for cid in cids or []:
            if cid not in ids:
                no(cid, "SCHEMA", "maps names a clause that does not exist")
            mapped.add(cid)
    for cid in sorted(ids - mapped):
        no(cid, "MAP_UNMAPPED_CLAUSE", "no item sentence maps to this clause")
    keys = [_norm(k) for k in maps if _norm(k)]
    for b in done_when(prose):
        if not any(_norm(b) in k or k in _norm(b) for k in keys):
            no(None, "MAP_DONE_WHEN", "done-when not mapped: %r" % b[:120])
    return bad


# ------------------------------------------------------------------------------------------------------ runs and reds
_TB_FRAME = re.compile(r'^\s*File "([^"]+)", line \d+', re.M)
_EXC_LINE = re.compile(r"^([A-Za-z_][\w.]*)(?::.*)?$")


def own_exception(out):
    """-> the exception name when `out` ends in an uncaught non-assertion exception raised in the test's own code (its
    innermost frame is a file under EXAM_DIR), else None. Such a red is a test-writer fault, not the clause failing:
    COMPANION_DEPLOY_LIVE_ROUND_FORGETS c1 (a TypeError in its own print) and c2 (its own raise) passed VALIDATE as reds."""
    frames = list(_TB_FRAME.finditer(out or ""))
    if not frames:
        return None
    last = frames[-1]
    path = last.group(1).replace("\\", "/")
    if not ("/%s/" % EXAM_DIR in path or path.startswith(EXAM_DIR + "/")):
        return None
    for ln in out[last.end():].splitlines()[1:]:
        if not ln or ln[0].isspace():
            continue                                    # the frame's source line, its ~~~^^^ markers, blank lines
        m = _EXC_LINE.match(ln)
        if not m:
            return None
        name = m.group(1)
        return None if name.rsplit(".", 1)[-1] == "AssertionError" else name
    return None


def red_kind(clause, exit_code, out, timed_out=False):
    """-> "green" | "assert" | "infra:<why>". An infra red is not evidence the check can fail (G3 (1))."""
    if timed_out:
        return "infra:timeout"
    if exit_code == 0:
        return "green"
    red = (clause.get("check") or {}).get("red") or {}
    if exit_code is None or exit_code < 0:
        return "infra:signal/cannot start"
    if exit_code in NOT_ASSERTION_EXITS:
        return "infra:" + NOT_ASSERTION_EXITS[exit_code]
    for name, rx in NOT_ASSERTION:
        if rx.search(out or ""):
            return "infra:" + name
    own = own_exception(out)
    if own:
        return "infra:uncaught %s in the test's own code" % own
    if exit_code not in (red.get("exit") or [1]):
        return "infra:exit %d is not a declared assertion exit" % exit_code
    marker = red.get("marker")
    if marker and marker not in (out or ""):
        return "infra:declared marker %r absent" % marker
    return "assert"


def exam_hash(exam, files, item_text):
    """sha256 over the clauses + maps, the item text, and {path: sha256 of bytes | None} of every named file (G3 (6))."""
    h = hashlib.sha256()
    body = {"clauses": exam.get("clauses"), "maps": exam.get("maps"), "no_code": bool(exam.get("no_code"))}
    h.update(json.dumps(body, sort_keys=True).encode("utf-8"))
    h.update(b"\0item\0" + hashlib.sha256((item_text or "").encode("utf-8")).hexdigest().encode("ascii"))
    for p in sorted(files):
        b = files[p]
        h.update(("\0file\0%s\0%s" % (p, hashlib.sha256(b).hexdigest() if b is not None else "-")).encode("utf-8"))
    return h.hexdigest()


def all_named(exam):
    return sorted({p for c in exam.get("clauses") or [] if isinstance(c, dict) for p in named_files((c.get("check") or {}).get("argv") or [])})


def validate(exam, run, item_text, prose="", read_file=None):
    """VALIDATE (supervisor, no agent). run(argv, patch, timeout) -> (exit, out, timed_out) at the base sha, with `patch`
    applied first when not None (its own failure: exit None, out "PATCH_FAILED: ..."). read_file(path) -> bytes|None at
    the base sha (for exam_hash). -> {"ok", "refusals", "rows", "exam_hash"}."""
    refusals = lint(exam, item_text, prose)
    rows = []
    linted = {r["clause"] for r in refusals if r["code"] in ("SCHEMA", "BREAK_KIND", "BREAK_DELETES", "EXISTENCE_ONLY")}
    for c in exam.get("clauses") or []:
        if not isinstance(c, dict):
            continue
        cid = c.get("id")
        if cid in linted or c.get("kind") in ("live", "owner"):
            continue
        chk, brk = c["check"], c["break"]
        t = int(chk.get("timeout_s", 300))
        if brk["kind"] == "base_red":
            e, out, to = run(chk["argv"], None, t)
            k = red_kind(c, e, out, to)
            rows.append({"clause": cid, "at": "base", "exit": e, "kind": k, "out": (out or "")[-800:]})
            if k == "green":
                refusals.append({"clause": cid, "code": "STAYS_GREEN", "why": "base_red: the check passes on the base sha"})
            elif k != "assert":
                refusals.append({"clause": cid, "code": "RED_NOT_ASSERTION", "why": "red on base, but %s" % k[6:]})
        else:
            e, out, to = run(chk["argv"], None, t)
            k = red_kind(c, e, out, to)
            rows.append({"clause": cid, "at": "base", "exit": e, "kind": k, "out": (out or "")[-800:]})
            if k != "green":
                refusals.append({"clause": cid, "code": "BASE_NOT_GREEN",
                                 "why": "patch: preserved behaviour must pass on the base sha first (%s)" % k})
                continue
            e, out, to = run(chk["argv"], brk["patch"], t)
            if e is None and str(out).startswith("PATCH_FAILED"):
                rows.append({"clause": cid, "at": "break", "exit": None, "kind": "patch_failed", "out": str(out)[-800:]})
                refusals.append({"clause": cid, "code": "PATCH_FAILED", "why": str(out)[:300]})
                continue
            k = red_kind(c, e, out, to)
            rows.append({"clause": cid, "at": "break", "exit": e, "kind": k, "out": (out or "")[-800:]})
            if k == "green":
                refusals.append({"clause": cid, "code": "STAYS_GREEN", "why": "the check stays green under the planted break"})
            elif k != "assert":
                refusals.append({"clause": cid, "code": "RED_NOT_ASSERTION", "why": "red under the break, but %s" % k[6:]})
    files = {p: (read_file(p) if read_file else None) for p in all_named(exam)}
    return {"ok": not refusals, "refusals": refusals, "rows": rows, "exam_hash": exam_hash(exam, files, item_text)}


# --------------------------------------------------------------------------------------------------------- the box
def box_runner(rules, source, sha, files_dir, item=None, nonce=None, runner=subprocess.run):
    """-> (run, read_file, close): checks run in a fresh Marker box at `sha` (relentless_wall.make_box with the WP-02
    toolchain: git history, cv2 venv) under the Marker's own systemd properties; the Setter's files at tree/.exam/."""
    import relentless_wall
    prof = relentless_wall.profile(rules, "marker")
    if not prof:
        raise RuntimeError("no marker wall profile in the rules")
    nonce = nonce or "exam-%s" % uuid.uuid4().hex[:12]
    box = relentless_wall.make_box(prof, source, sha, nonce, base=None, item=item)
    tree = os.path.join(box, "tree")
    if files_dir and os.path.isdir(files_dir):
        shutil.copytree(files_dir, os.path.join(tree, EXAM_DIR), dirs_exist_ok=True)

    def run(argv, patch, timeout):
        if patch:
            p = runner(["git", "apply", "--unsafe-paths", "-"], cwd=tree, input=patch,
                       capture_output=True, text=True, timeout=60)
            if p.returncode:
                return None, "PATCH_FAILED: " + (p.stderr or p.stdout)[-300:], False
        unit = ["systemd-run", "--user", "--wait", "--pipe", "--collect", "--quiet", "-p", "WorkingDirectory=" + tree,
                "-p", "RuntimeMaxSec=%d" % (timeout + 30)] + relentless_wall.props(prof, box) \
            + sum((["--setenv", "%s=%s" % kv] for kv in dict(relentless_wall.unit_env(prof, box), **RUN_ENV).items()), []) \
            + ["--"] + list(argv)
        try:
            q = runner(unit, capture_output=True, text=True, timeout=timeout + 60, stdin=subprocess.DEVNULL)
            res = (q.returncode, ((q.stdout or "") + (q.stderr or ""))[-6000:], False)
        except subprocess.TimeoutExpired as e:
            res = (None, str(e)[-300:], True)
        finally:
            if patch:
                runner(["git", "apply", "-R", "--unsafe-paths", "-"], cwd=tree, input=patch,
                       capture_output=True, text=True, timeout=60)
        return res

    def read_file(path):
        try:
            with open(os.path.join(tree, path), "rb") as f:
                return f.read()
        except OSError:
            return None

    def close():
        relentless_wall.remove_box(box)

    read_file.tree = tree               # the Setter's cwd when this box is the Setter's

    return run, read_file, close


# -------------------------------------------------------------------------------------------------------- the Setter
SETTER_BRIEF = """You are the SETTER for RimMandrake pipeline item {item} (RELENTLESS_BUILD_EXAM_BEFORE_BUILDER). You are NOT
its builder and will never build or mark it. Write the acceptance exam a builder will build towards, BEFORE any build.
Your working directory is a read-only export of the repo at the item's base sha {base} (no work for this item exists yet).

The item, in its own words:
---
{text}
---

Write {exam_json} (JSON) and, if a check needs its own test script, put it under {files} and name it in argv as
`.exam/<name>` (it is copied into the tree at .exam/ for every run). Write nothing else anywhere.

Format: {{"item": "{item}", "clauses": [{{"id": "c1", "says": "<the clause, quoting the item>",
  "kind": "behaviour|artifact", "check": {{"argv": ["python3", ".exam/test_x.py"], "timeout_s": 300,
  "red": {{"exit": [1], "marker": "FAIL"}}}}, "break": {{"kind": "base_red"}} or {{"kind": "patch", "patch": "<unified diff>"}}}}],
 "maps": {{"<sentence copied verbatim from the item text>": ["c1"]}}, "no_code": false}}

Rules the supervisor enforces mechanically (a refusal comes back to you once, then goes to an arbiter):
- Observable OUTCOMES only (what must be true when done), never HOW. The builder sees this exam and may not edit it.
- Every check must be able to fail, proven now: `base_red` = it FAILS on this base sha (new behaviour); `patch` = it PASSES
  on this base and FAILS once your planted patch (a behavioural change to the code under test; never deleting a file the
  check names, never editing .exam/) is applied.
- A red counts only as an ASSERTION failure: exit with a code you list in red.exit (not 2/124/126/127) and print red.marker.
  ImportError, a missing file or tool, SyntaxError or a timeout is NOT a red. So a check of a not-yet-written module must
  fail by assertion (e.g. your .exam script catches the missing behaviour and prints FAIL, exit 1), not by crashing.
- `kind: behaviour` checks must exercise the behaviour: an existence/grep-only check (test -f, grep, ls, cat, wc, a python -c
  that only tests a path) is refused. `kind: artifact` only where the item asks for an artifact.
- Every clause is mapped from a sentence copied VERBATIM from the item text; every '## Done when' bullet must be mapped.
- No live-game, flyer-flight or owner-look clauses here (they stay with the existing live lane in shadow).
- Run your checks here to see them fail before you finish (cd here; python3 .exam/... after copying your files to .exam/ is
  fine for trying; the supervisor reruns everything in its own box).
End with one line: EXAM WRITTEN <n clauses>."""


def setter_prompt(item, text, base, exam_json, files):
    return SETTER_BRIEF.format(item=item, text=(text or "")[:8000], base=base, exam_json=exam_json, files=files)


def refusal_prompt(v):
    lines = ["The supervisor REFUSED your exam. Fix every refusal below and rewrite the same files; this is your one retry.", ""]
    lines += ["- %s %s: %s" % (r["code"], r.get("clause") or "", r["why"]) for r in v["refusals"]]
    lines += ["", "Runs:"] + ["- %s at %s: exit %s, %s; %s" % (x["clause"], x["at"], x["exit"], x["kind"], x["out"][-300:])
                              for x in v["rows"]]
    return "\n".join(lines)


def run_setter(cwd, prompt, cfg, out, session=None, resume=None, runner=subprocess.run):
    """Run the Setter (claude -p, Judge-mode agent, fresh or resumed) in the foreground of the exam unit. -> session id."""
    claude = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    sid = resume or session or str(uuid.uuid4())
    argv = [claude, "-p", prompt, "--agent", cfg.get("setter_agent", "rm-judge"), "--model", cfg.get("setter_model", "opus"),
            "--output-format", "json", "--dangerously-skip-permissions"] + (["--resume", resume] if resume else ["--session-id", sid])
    with open(out, "a", encoding="utf-8") as f:
        try:
            r = runner(argv, cwd=cwd, stdout=f, stderr=subprocess.STDOUT, timeout=int(cfg.get("setter_max_s", 1200)),
                       stdin=subprocess.DEVNULL)
            f.write("\n[setter exit %s]\n" % getattr(r, "returncode", "?"))
        except (OSError, subprocess.SubprocessError) as e:
            f.write("\n[setter failed %s: %s]\n" % (type(e).__name__, e))
    return sid


def _item_text(item):
    cli = os.path.join(HERE, "cli.py")
    try:
        r = subprocess.run([sys.executable, cli, "show", item], capture_output=True, text=True, timeout=120)
        return (r.stdout or "")[:12000]
    except (OSError, subprocess.SubprocessError):
        return ""


def _prose(source, sha, item):
    try:
        r = subprocess.run(["git", "show", "%s:infrastructure/state/items/%s.md" % (sha, item)], cwd=source,
                           capture_output=True, text=True, timeout=60)
        return r.stdout if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def run_item(store, item, rules, cfg=None, now=None, setter=run_setter, boxer=box_runner, text_of=_item_text):
    """The exam unit's body: SET -> VALIDATE -> one resumed retry -> frozen exam or arbiter_owed. -> final state."""
    cfg = config() if cfg is None else cfg
    st = status(store, item) or {}
    base = st.get("base")
    if not base or st.get("state") not in ("owed", "setting"):
        return st.get("state")
    source = os.path.join(store.root, "books")
    d = item_dir(store, item)
    files = os.path.join(d, "files")
    text = text_of(item)
    prose = _prose(source, base, item)
    set_status(store, item, state="setting", set_at=iso(time.time() if now is None else now))
    sbox = boxer(rules, source, base, None, item=item)
    try:
        work = os.path.join(d, "setter")
        os.makedirs(work, exist_ok=True)
        exam_json = os.path.join(work, "exam.json")
        wfiles = os.path.join(work, "files")
        os.makedirs(wfiles, exist_ok=True)
        tree = sbox[1].tree
        sid = setter(tree, setter_prompt(item, text, base, exam_json, wfiles), cfg, os.path.join(d, "setter.out"))
        verdict = None
        for attempt in (1, 2):
            exam = _read(exam_json)
            if not isinstance(exam, dict):
                verdict = {"ok": False, "refusals": [{"clause": None, "code": "SCHEMA", "why": "no exam.json written"}],
                           "rows": [], "exam_hash": None}
            else:
                shutil.rmtree(files, ignore_errors=True)
                shutil.copytree(wfiles, files)
                run, read_file, close = boxer(rules, source, base, files, item=item)
                try:
                    verdict = validate(exam, run, text, prose, read_file)
                finally:
                    close()
            _append(os.path.join(d, "validation.jsonl"), dict(verdict, attempt=attempt, at=iso(time.time())))
            if verdict["ok"] or attempt == 2:
                break
            setter(tree, refusal_prompt(verdict), cfg, os.path.join(d, "setter.out"), resume=sid)
    finally:
        sbox[2]()
    if verdict["ok"]:
        frozen = dict(exam, item=item, base_sha=base, exam_hash=verdict["exam_hash"], mode=cfg.get("mode"),
                      setter={"session": sid, "model": cfg.get("setter_model", "opus"), "agent": cfg.get("setter_agent")},
                      validated_at=iso(time.time()))
        _write(os.path.join(d, "exam.json"), frozen)
        set_status(store, item, state="validated", exam_hash=verdict["exam_hash"], validated_at=frozen["validated_at"])
        return "validated"
    set_status(store, item, state="arbiter_owed", refusals=verdict["refusals"][:12])
    return "arbiter_owed"


# ------------------------------------------------------------------------------------------------- shadow: would-catch
def returns(attempts, descends=None):
    """-> ([(sha, end, at)] each Marker return with the candidate sha it returned, done sha or None). `descends(sha)`
    -> bool restricts the done sha to one built on the exam's base: a done from an earlier round (CHECKER_REACH_FIX_
    STORE_STILL_DARK done at 0d7517539, exam base 5148369a5) is older code than the exam judges."""
    out, last, done = [], None, None
    for a in attempts:
        if a.get("end") == "finish" and a.get("sha"):
            last = a["sha"]
        elif a.get("end") in REJECTS and last:
            out.append((last, a["end"], a.get("at")))
            last = None
        elif a.get("end") == "done" and a.get("sha") and (descends is None or descends(a["sha"])):
            done = a["sha"]
    return out, done


def exam_base(store, item, exam=None):
    exam = _read(os.path.join(item_dir(store, item), "exam.json")) if exam is None else exam
    return (exam or {}).get("base_sha") or (status(store, item) or {}).get("base")


def descender(repo, base, runner=subprocess.run):
    """-> descends(sha): True when `base` is an ancestor of (or is) `sha` in `repo` (git merge-base --is-ancestor). No
    base -> None (no restriction). An unknown sha, or git failing, reads False: it is not shown to descend."""
    if not base:
        return None
    memo = {}

    def descends(sha):
        if sha not in memo:
            try:
                p = runner(["git", "-C", repo, "merge-base", "--is-ancestor", base, sha], capture_output=True, timeout=60)
                memo[sha] = p.returncode == 0
            except (OSError, subprocess.SubprocessError):
                memo[sha] = False
        return memo[sha]
    return descends


class _Lock:
    """flock on <item>/catch.lock: two exam units catching one item serialise, so a sha is checked and written once."""
    def __init__(self, d):
        os.makedirs(d, exist_ok=True)
        self.path = os.path.join(d, "catch.lock")

    def __enter__(self):
        self.f = open(self.path, "a")
        fcntl.flock(self.f, fcntl.LOCK_EX)
        return self

    def __exit__(self, *a):
        fcntl.flock(self.f, fcntl.LOCK_UN)
        self.f.close()


def run_exam(exam, run):
    """-> [{"clause", "exit", "kind"}] for every offline clause at the runner's sha."""
    rows = []
    for c in exam.get("clauses") or []:
        if not isinstance(c, dict) or c.get("kind") in ("live", "owner"):
            continue
        e, out, to = run(c["check"]["argv"], None, int(c["check"].get("timeout_s", 300)))
        rows.append({"clause": c["id"], "exit": e, "kind": red_kind(c, e, out, to), "out": (out or "")[-400:]})
    return rows


def catch(store, item, rules, boxer=box_runner, repo=None):
    """Run the validated exam at each candidate a Marker returned (and at the done sha, if it descends from the exam's
    base) not yet run. Idempotent per (item, sha, role): each sha is re-checked against catch.jsonl and run under the
    item's lock, so two concurrent units never both write it (7 duplicate rows, 2026-11-06). -> rows written."""
    d = item_dir(store, item)
    exam = _read(os.path.join(d, "exam.json"))
    if not exam:
        return []
    source = os.path.join(store.root, "books")
    rets, done = returns(store.attempts(item), descender(repo or source, exam_base(store, item, exam)))
    todo = [(s, "return", end) for s, end, _ in rets] + ([(done, "done", "done")] if done else [])
    wrote = []
    path = os.path.join(d, "catch.jsonl")
    for sha, role, end in todo:
        with _Lock(d):
            if (sha, role) in {(r.get("sha"), r.get("role")) for r in _lines(path)}:
                continue
            try:
                run, _, close = boxer(rules, source, sha, os.path.join(d, "files"), item=item)
            except Exception as e:  # noqa: BLE001 - an unexportable sha is recorded, not retried for ever
                row = {"sha": sha, "role": role, "end": end, "error": "%s: %s" % (type(e).__name__, str(e)[:200]),
                       "at": iso(time.time())}
                _append(path, row)
                wrote.append(row)
                continue
            try:
                rows = run_exam(exam, run)
            finally:
                close()
            reds = [r["clause"] for r in rows if r["kind"] == "assert"]
            row = {"sha": sha, "role": role, "end": end, "exam_hash": exam.get("exam_hash"), "rows": rows, "at": iso(time.time()),
                   # a return the exam would have caught: some clause is an assertion red at the returned candidate
                   "caught": bool(reds) if role == "return" else None,
                   # at the done sha the exam should be green; red there is a Setter-wrong (or false-close) signal
                   "green_at_done": (not reds and all(r["kind"] == "green" for r in rows)) if role == "done" else None,
                   "red_clauses": reds}
            _append(path, row)
            wrote.append(row)
    return wrote


def _lines(path):
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for ln in f:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    except OSError:
        pass
    return out


def catch_some(store, rules, limit=3, boxer=box_runner):
    """Piggybacked at the end of every exam unit: `limit` items with a validated exam and an unrun return/done sha."""
    n = 0
    root = exam_root(store)
    for item in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        if n >= limit:
            break
        if (status(store, item) or {}).get("state") != "validated":
            continue
        if catch(store, item, rules, boxer):
            n += 1
    return n


def _reds(row):
    """The row's assertion reds, re-read: a stored "assert" whose output shows the test's own uncaught exception (rows
    written before red_kind knew that) is not a red."""
    return [r["clause"] for r in row.get("rows") or [] if r.get("kind") == "assert" and not own_exception(r.get("out"))]


def summary(store, cfg=None, repo=None):
    """The `exam_shadow` block of relentless.py reading: how far the shadow sample is, and what the exam would have caught.
    Counts distinct (item, sha) per role, first row kept (concurrent units once wrote duplicates); a done sha that does
    not descend from the exam's base is not counted (`done_off_base`); reds are re-read through _reds."""
    cfg = config() if cfg is None else cfg
    root = exam_root(store)
    items = sorted(os.listdir(root)) if os.path.isdir(root) else []
    states, codes = {}, {}
    rets = caught = done_runs = done_green = done_red = verdicts = dupes = off_base = 0
    caught_items, red_items = [], []
    source = repo or os.path.join(store.root, "books")
    for item in items:
        s = status(store, item) or {}
        states[s.get("state", "?")] = states.get(s.get("state", "?"), 0) + 1
        for v in _lines(os.path.join(item_dir(store, item), "validation.jsonl")):
            for r in v.get("refusals") or []:
                codes[r["code"]] = codes.get(r["code"], 0) + 1
        rows = _lines(os.path.join(item_dir(store, item), "catch.jsonl"))
        if rows:
            verdicts += 1
        seen, descends = set(), None
        for r in rows:
            key = (r.get("sha"), r.get("role"))
            if key in seen:
                dupes += 1
                continue
            seen.add(key)
            if r.get("error") or not isinstance(r.get("rows"), list):
                continue
            reds = _reds(r)
            if r.get("role") == "return":
                rets += 1
                caught += bool(reds)
                if reds:
                    caught_items.append(item)
            elif r.get("role") == "done":
                if descends is None:
                    descends = descender(source, exam_base(store, item)) or (lambda sha: True)
                if not descends(r.get("sha")):
                    off_base += 1
                    continue
                done_runs += 1
                if reds:
                    done_red += 1
                    red_items.append(item)
                elif all(x.get("kind") == "green" for x in r["rows"]):
                    done_green += 1
    return {"mode": cfg.get("mode"), "items": len(items), "states": states, "refusal_codes": codes,
            "with_marker_verdict": verdicts, "target": int(cfg.get("shadow_target", 30)),
            "returns_run": rets, "returns_caught": caught, "caught_items": sorted(set(caught_items))[:20],
            "done_runs": done_runs, "done_green": done_green, "done_red": done_red,
            "done_unclear": done_runs - done_green - done_red, "done_red_items": sorted(set(red_items))[:20],
            "done_off_base": off_base, "duplicate_rows": dupes}


# --------------------------------------------------------------------------------------------------------------- CLI
def _store():
    import relentless
    return relentless.Store(), relentless.rules()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run", help="the exam unit: SET, VALIDATE, one retry; then catch_some")
    p.add_argument("item")
    p = sub.add_parser("catch", help="run validated exams at Marker-returned candidates")
    p.add_argument("item", nargs="?")
    sub.add_parser("summary", help="the exam_shadow reading block")
    p = sub.add_parser("lint", help="lint an exam file against an item text file (no runs)")
    p.add_argument("exam")
    p.add_argument("text")
    a = ap.parse_args(argv)
    if a.cmd == "lint":
        bad = lint(_read(a.exam) or {}, open(a.text, encoding="utf-8").read())
        print(json.dumps(bad, indent=1))
        return 1 if bad else 0
    store, rules = _store()
    if a.cmd == "run":
        try:
            state = run_item(store, a.item, rules)
            print(state)
            if state == "arbiter_owed":          # R4: the second refusal's arbiter (relentless_dispute, WP-08)
                import relentless_dispute
                print("arbiter: %s" % relentless_dispute.arbitrate_exam(store, a.item))
        except Exception as e:  # noqa: BLE001 - recorded on the item, the unit ends
            set_status(store, a.item, state="setter_failed", error="%s: %s" % (type(e).__name__, str(e)[:300]))
            print("setter_failed: %s" % e)
        print("catch: %d item(s)" % catch_some(store, rules))
        return 0
    if a.cmd == "catch":
        if a.item:
            print(json.dumps(catch(store, a.item, rules), indent=1))
        else:
            print("catch: %d item(s)" % catch_some(store, rules, limit=1000))
        return 0
    print(json.dumps(summary(store), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
