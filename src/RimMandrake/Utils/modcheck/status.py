"""modcheck.status -- the GREEN/STALE registry, `infrastructure/state/modcheck_status.json`.

Same discipline as `code_review_status.py` (CLAUDE.md's "Code isn't clean
until a review says so", the sibling policy this one exists next to): a hash
comparison, never a timestamp, and an atomic lock+tmp+`os.replace` write so
two concurrent windows recording a run never lose one's entry (this repo is
shared by BENCH/FOUNDRY).

    modcheck run <mod>            # records a fresh GREEN/RED entry
    modcheck status               # GREEN/STALE/NEVER RUN per mod
    modcheck declare <mod> minor --why "..."   # re-green after a trivial edit

Gate law (spec §4): the playtest offer path checks GREEN. No green, no
playtest. A hash mismatch with no `declare minor` is STALE, full stop.
"""
import contextlib
import hashlib
import json
import os
import subprocess
import time

# `runner.py` (this module's caller for a live `modcheck run`) executes
# under WINDOWS `python.exe` -- everything touching the actual bridge
# socket must, per the WSL-loopback limitation in rimbridge_client.py -- so
# `fcntl` (POSIX-only) is not always importable here, unlike in
# `code_review_status.py`'s WSL-only context this module's lock pattern was
# borrowed from. Fall back to `msvcrt` file locking on Windows. MEASURED
# 2026-09-12: the first live `modcheck run` crashed on exactly this before
# a single component ran.
try:
    import fcntl

    def _lock(fd):
        fcntl.flock(fd, fcntl.LOCK_EX)

    def _unlock(fd):
        fcntl.flock(fd, fcntl.LOCK_UN)
except ImportError:
    import msvcrt

    # MEASURED live 2026-09-12: locking a huge byte range (1 GiB) on the
    # LOCK file -- which is separate from the tmp file `save()` actually
    # writes into, and stays empty or near-empty forever -- raised
    # `PermissionError` from msvcrt on Windows; locking beyond a file's
    # actual extent is not reliable there the way POSIX `flock` is. The
    # portable fix every cross-platform-lock library uses: the lock file
    # holds exactly one byte (write it if missing) and only that byte is
    # ever locked. This file is a pure mutex -- the real content always
    # lives in `LOG_PATH` itself, written by `save()` below.
    def _ensure_one_byte(fd):
        if os.fstat(fd).st_size < 1:
            os.write(fd, b"\0")
            os.fsync(fd)

    # MEASURED 2026-10-06: since the seat clones moved to ext4 (2026-10-02) python.exe reaches the repo over
    # \\wsl.localhost (9p), where byte-range locks are unsupported -- LK_LOCK raises OSError 36 (EDEADLK, surfacing
    # as PermissionError) and LK_NBLCK OSError 22 -- so EVERY live run's record_run failed and no suite status was
    # updated. There the mutex falls back to an atomic mkdir beside the lock file (stale after 120 s).
    _MKDIR_HELD = {}

    def _mkdir_lock(fd):
        import time as _t
        d = LOCK_PATH + ".d"
        if any(_MKDIR_HELD.values()):         # re-entrant: save() locks its tmp fd inside _locked()
            _MKDIR_HELD[fd] = None
            return
        deadline = _t.time() + 60
        while True:
            try:
                os.mkdir(d)
                _MKDIR_HELD[fd] = d
                return
            except FileExistsError:
                try:
                    if _t.time() - os.stat(d).st_mtime > 120:
                        os.rmdir(d)
                        continue
                except OSError:
                    pass
                if _t.time() > deadline:
                    raise
                _t.sleep(0.2)

    def _lock(fd):
        _ensure_one_byte(fd)
        os.lseek(fd, 0, os.SEEK_SET)
        try:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        except OSError as e:
            if e.errno == 22:                 # EINVAL: no byte-range locks on this filesystem (9p)
                _mkdir_lock(fd)
            else:                             # genuinely held by another process: wait for it (LK_LOCK retries 10 s)
                msvcrt.locking(fd, msvcrt.LK_LOCK, 1)

    def _unlock(fd):
        if fd in _MKDIR_HELD:
            d = _MKDIR_HELD.pop(fd)
            if d is not None:
                try:
                    os.rmdir(d)
                except OSError:
                    pass
            return
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))
LOG_PATH = os.path.join(ROOT, "infrastructure", "state", "modcheck_status.json")
LOCK_PATH = LOG_PATH + ".lock"

# Never part of a mod's behavioural hash: editing the validator does not
# change what the mod DOES. Case-insensitive basename match. `northstar` is the
# functional-script harness folder (FlowWorks/northstar: validation_v2.py, its
# site spec, mock game and the result JSONs each live run writes BESIDE it) --
# without this, every recorded run changed the hash it was recorded at, so a
# run could never be current (MEASURED 2026-10-02, `modcheck record`).
# `human_review.py` is the Northstar "for the human" review-map builder (design/RimMandrake/northstar_human_review.md):
# it stages a map for the owner to look at and changes nothing the mod does.
_EXCLUDED_BASENAMES = {"validation.py", "__pycache__", "northstar", "human_review.py"}


def _hashignore(mod_dir):
    """Paths a mod lists in `<mod>/.hashignore` (one relpath prefix per line, `#` comments, trailing `*` = prefix).
    Only for files that never ship or change what the mod does -- art sources, review tooling, held scaffolds -- so
    adding them cannot make a finished run read STALE. A mod without the file hashes exactly as before."""
    try:
        with open(os.path.join(mod_dir, ".hashignore"), encoding="utf-8") as f:
            return [l.split("#")[0].strip() for l in f if l.split("#")[0].strip()]
    except OSError:
        return []


def mod_hash(mod_dir):
    """SHA-256 over every file under `mod_dir` except the validator itself
    and cache noise -- (relpath, content) pairs, sorted, so the hash is
    stable regardless of filesystem walk order."""
    parts = []
    ignore = _hashignore(mod_dir)
    for root, dirs, files in os.walk(mod_dir):
        dirs[:] = [d for d in dirs if d.lower() not in _EXCLUDED_BASENAMES
                  and d != ".git"]
        for name in sorted(files):
            if name.lower() in _EXCLUDED_BASENAMES or name.endswith(".pyc"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, mod_dir).replace(os.sep, "/")
            if any(rel == g or rel.startswith(g.rstrip("/") + "/") or (g.endswith("*") and rel.startswith(g[:-1]))
                   for g in ignore):
                continue
            with open(path, "rb") as f:
                parts.append((rel, f.read()))
    parts.sort(key=lambda kv: kv[0])
    h = hashlib.sha256()
    for rel, content in parts:
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(content)
        h.update(b"\0")
    return h.hexdigest()


# ------------------------------------------------------------------------------------------------- run manifests
# focused_testing_plan_2026-10-25 option B: an external live driver's result is keyed on WHAT IT MEASURED, not on the
# whole-mod hash -- so an edit that cannot change the measurement (C# source not yet rebuilt into the committed DLL, a
# doc, a selftest, review tooling) no longer voids it. mod_hash is kept, unchanged, beside it: a result at the current
# mod_hash is FRESH; a result whose manifest equals the current one is only REUSABLE (modcheck/reuse.py decides).
MANIFEST_SCHEMA = 1
# Under the mod dir, never part of the RUNTIME hash: the game cannot see them. Source/ is compiled into the committed
# Assemblies/*.dll, which IS hashed -- so a C# change counts the moment the DLL is rebuilt, and an unbuilt change has
# not reached the game. Mod-root *.py are selftests and review tooling (the runtime never runs Python).
_NON_RUNTIME_DIRS = ("Source/", "art_source/")
_DATA_EXT = (".json", ".xml", ".txt", ".yaml", ".yml", ".csv", ".md")


def _non_runtime(rel):
    return (any(rel.startswith(d) for d in _NON_RUNTIME_DIRS) or rel.lower().endswith(".md")
            or ("/" not in rel and rel.endswith(".py")))


def runtime_hash(mod_dir):
    """SHA-256 over the files mod_hash covers MINUS what the game cannot load (_non_runtime): Defs, Patches, Languages,
    Textures, Sounds, About, Tools and the committed Assemblies. Same (relpath, content) scheme as mod_hash."""
    parts = []
    ignore = _hashignore(mod_dir)
    for root, dirs, files in os.walk(mod_dir):
        dirs[:] = [d for d in dirs if d.lower() not in _EXCLUDED_BASENAMES and d != ".git"]
        for name in sorted(files):
            if name.lower() in _EXCLUDED_BASENAMES or name.endswith(".pyc"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, mod_dir).replace(os.sep, "/")
            if _non_runtime(rel) or any(rel == g or rel.startswith(g.rstrip("/") + "/")
                                        or (g.endswith("*") and rel.startswith(g[:-1])) for g in ignore):
                continue
            with open(path, "rb") as f:
                parts.append((rel, f.read()))
    parts.sort(key=lambda kv: kv[0])
    h = hashlib.sha256()
    for rel, content in parts:
        h.update(rel.encode("utf-8") + b"\0" + content + b"\0")
    return h.hexdigest()


def _import_dirs(mod_dir, script_dir):
    utils = os.path.join(os.path.dirname(os.path.abspath(mod_dir)), "Utils")
    return [script_dir, os.path.abspath(mod_dir), utils, os.path.join(utils, "modcheck")]


def test_closure(script, mod_dir):
    """(files, unresolved): `script` plus every LOCAL module it imports, transitively (AST: every `import`/`from`
    anywhere in the file, function bodies included; every parent package __init__ of a dotted name; relative imports
    against the importing file's package), resolved against the script's dir, the mod root, Utils/ and
    Utils/modcheck/ -- plus every data file a string literal in those files names (a spec JSON) that exists beside
    the file, under one of those dirs, or one directory below the file. An absolute name that resolves nowhere is
    stdlib/third-party and is not hashed. `unresolved` lists what makes the closure unprovable (a non-literal
    importlib/__import__, a relative import that resolves nowhere, an unreadable file): a manifest with any is never
    reusable. LIMIT: a data path built at run time from pieces none of which is the file's own name (a computed
    file name) is not seen. Pure but for the reads."""
    import ast
    script = os.path.abspath(script)
    dirs = _import_dirs(mod_dir, os.path.dirname(script))
    seen, unresolved, todo = set(), [], [script]

    def _find(mod, among=None):
        rel = mod.replace(".", os.sep)
        for d in among or dirs:
            for cand in (os.path.join(d, rel + ".py"), os.path.join(d, rel, "__init__.py")):
                if os.path.isfile(cand):
                    return os.path.abspath(cand)
        return None

    def _data(here, value):
        """A data file a literal names: beside the file, under one of the import dirs, or one directory below the file
        (os.path.join(HERE, "specs", "x.json") names only "x.json" as a data literal)."""
        for d in [here] + dirs:
            cand = os.path.join(d, value)
            if os.path.isfile(cand):
                return [os.path.abspath(cand)]
        if "/" in value or os.sep in value:
            return []
        try:
            subs = sorted(e.path for e in os.scandir(here) if e.is_dir() and e.name != "__pycache__")
        except OSError:
            return []
        return [os.path.abspath(os.path.join(d, value)) for d in subs if os.path.isfile(os.path.join(d, value))]

    while todo:
        path = todo.pop()
        if path in seen:
            continue
        seen.add(path)
        if not path.endswith(".py"):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=path)
        except (OSError, SyntaxError, ValueError) as ex:
            unresolved.append("%s: %s" % (os.path.basename(path), type(ex).__name__))
            continue
        here = os.path.dirname(path)
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level:
                # relative import: resolved against the importing file's package; one that resolves nowhere makes the
                # closure unprovable (it is always local code)
                base = here
                for _ in range(node.level - 1):
                    base = os.path.dirname(base)
                mods = [node.module] if node.module else []
                mods += ["%s.%s" % (node.module, a.name) if node.module else a.name for a in node.names]
                got = [p for p in (_find(m, [base]) for m in mods) if p]
                if not got:
                    unresolved.append("%s:%d relative import %s%s unresolved" % (
                        os.path.basename(path), node.lineno, "." * node.level, node.module or ""))
                todo.extend(got)
                init = os.path.join(base, "__init__.py")
                if os.path.isfile(init):
                    todo.append(os.path.abspath(init))
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module] + ["%s.%s" % (node.module, a.name) for a in node.names]
            elif isinstance(node, ast.Call):
                fn = node.func
                fname = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
                if fname in ("import_module", "__import__"):
                    arg = node.args[0] if node.args else None
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        names = [arg.value]
                    else:
                        unresolved.append("%s:%d non-literal %s" % (os.path.basename(path), node.lineno, fname))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.lower().endswith(_DATA_EXT) \
                    and "*" not in node.value and len(node.value) < 200:
                todo.extend(_data(here, node.value))
            for n in names:
                # `import pkg.worker` also executes pkg/__init__.py: hash every parent package initializer
                parts = n.split(".")
                for k in range(1, len(parts) + 1):
                    p = _find(".".join(parts[:k]))
                    if p:
                        todo.append(p)
    return sorted(seen), unresolved


def _rel_to(path, base):
    return os.path.relpath(path, base).replace(os.sep, "/")


def run_manifest(mod_dir, script):
    """The reuse key of one live driver run (focused_testing_plan_2026-10-25 option B): {schema, script, runtime,
    test, test_files, unresolved}. `runtime` = runtime_hash(mod_dir); `test` = sha over test_closure(script) by
    (relpath to the mod's parent, content). The live mod list (env.running) and the DLL the game ran
    (env.assembly_sha256) are already in a result's env and are judged there. Never raises: a field it cannot read is
    None and the reason is in `unresolved`, which makes the manifest unusable for reuse."""
    out = {"schema": MANIFEST_SCHEMA, "script": None, "runtime": None, "test": None, "test_files": [], "unresolved": []}
    base = os.path.dirname(os.path.abspath(mod_dir))
    try:
        out["script"] = _rel_to(os.path.abspath(script), os.path.abspath(mod_dir))
        out["runtime"] = runtime_hash(mod_dir)
        files, unresolved = test_closure(script, mod_dir)
        h = hashlib.sha256()
        for p in files:
            with open(p, "rb") as f:
                h.update(_rel_to(p, base).encode("utf-8") + b"\0" + f.read() + b"\0")
        out["test"], out["test_files"], out["unresolved"] = h.hexdigest(), [_rel_to(p, base) for p in files], unresolved
    except Exception as ex:  # noqa: BLE001 - a manifest that cannot be computed is recorded as such, never raised
        out["unresolved"].append("manifest: %s: %s" % (type(ex).__name__, ex))
    return out


def _git(args, timeout=10):
    try:
        r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                           text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


@contextlib.contextmanager
def _locked():
    os.makedirs(os.path.dirname(LOCK_PATH), exist_ok=True)
    fd = os.open(LOCK_PATH, os.O_WRONLY | os.O_CREAT, 0o644)
    try:
        _lock(fd)
        yield
    finally:
        _unlock(fd)
        os.close(fd)


def load():
    if not os.path.isfile(LOG_PATH):
        return {}
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except ValueError as e:
            raise RuntimeError(
                "%s is not valid JSON (merge conflict markers?): %s"
                % (LOG_PATH, e))


def save(data):
    tmp = "%s.tmp.%d.%d" % (LOG_PATH, os.getpid(), time.time_ns())
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    # O_BINARY: on Windows os.open defaults to TEXT mode and turned every \n into \r\n (MEASURED 2026-10-06, the first
    # python.exe recording rewrote all 676 lines of the file).
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o644)
    try:
        try:
            _lock(fd)
            try:
                body = json.dumps(data, indent=2, sort_keys=True) + "\n"
                os.write(fd, body.encode("utf-8"))
                os.fsync(fd)
            finally:
                _unlock(fd)
        finally:
            os.close(fd)
        os.replace(tmp, LOG_PATH)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _checklist_state(walk):
    """`(present, effective_state)` of a walk's `## north star`, or
    `(False, None)` when there is no walk. Read here rather than passed in as a
    boolean so a caller cannot hand this function a flattering answer."""
    if not walk or not os.path.isfile(walk):
        return False, None
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import northstar  # noqa: E402
    ns = northstar.parse(walk)
    return ns["present"], ns["state"]


def verdict_for(all_green, walk, refused="", reviewed=False):
    """The GREEN definition of north_star_validation_spec.md §5, in one place.

    GREEN requires all five: state assertions pass, every validated must-show
    line is claimed, every claim is judged, the checklist is VALIDATED, and he
    has reviewed the sheet once. The last three are what this function adds.

      REFUSED              the visual floor or an orphaned `shows=` (never ran)
      RED                  something failed -- state or judge
      DRAFT-CHECKLIST      both halves passed against a bar that is not his yet
      PENDING-OWNER-REVIEW both halves passed; his own eyes not yet on a sheet
      GREEN                all five

    ⚠️ A mod whose walk has NO `## north star` section reaches GREEN exactly as
    it did before this system existed. Enforcement is per mod, as he validates
    (owner, 2026-09-15) -- that is what makes the whole change additive.
    """
    if refused:
        return "REFUSED"
    if not all_green:
        return "RED"
    present, state = _checklist_state(walk)
    if present and state != "VALIDATED":
        return "DRAFT-CHECKLIST"
    if present and not reviewed:
        return "PENDING-OWNER-REVIEW"
    return "GREEN"


def record_run(mod, mod_dir, run_id, all_green, walk=None, refused="", extra=None):
    """Called once per `modcheck run <mod>`. Never hand-called mid-run --
    the runner calls this exactly once, after every chain has finished.

    `all_green` is the run's BOTH-HALVES verdict (state and judge); `walk` is the
    mod's validation walk, whose checklist state and the owner's recorded review
    decide whether an all-green run is allowed to be called GREEN.

    `extra` (optional) is merged into the entry -- `modcheck record` stores the
    run's per-row tally and its environment fingerprint there (`components`,
    `source`). It can never override the verdict fields above."""
    with _locked():
        data = load()
        prior = data.get(mod) or {}
        review = prior.get("owner_review")
        data[mod] = {
            "hash": mod_hash(mod_dir),
            "run_id": run_id,
            "status": verdict_for(all_green, walk, refused, bool(review)),
            "ts": time.time(),
            "minor": None,
            # His review survives a re-run: it is required only for a mod's
            # FIRST green, and it names the run whose sheet he actually read.
            "owner_review": review,
            "refused": refused or None,
        }
        for k, v in (extra or {}).items():
            if k not in data[mod]:
                data[mod][k] = v
        save(data)
    return data[mod]


def record_owner_review(mod, said, run_id=None):
    """Record that the owner personally reviewed this mod's sheet -- spec §5.5,
    required once, before a mod's first GREEN, mirroring the whole-file-then-
    incremental rule of `code_review_status.py`.

    OWNER-AUTHORISED ONLY: `said` is his verbatim words, which the CLI requires
    and this function records rather than re-derives. Promotes a run that was
    waiting on exactly this to GREEN, and refuses a mod with no run to review --
    there is no sheet to have read."""
    with _locked():
        data = load()
        entry = data.get(mod)
        if not entry:
            raise RuntimeError(
                "%s has no recorded run -- there is no sheet to review. Run "
                "`modcheck run %s` first." % (mod, mod))
        entry["owner_review"] = {"run_id": run_id or entry.get("run_id"),
                                 "said": said, "ts": time.time()}
        if entry.get("status") == "PENDING-OWNER-REVIEW":
            entry["status"] = "GREEN"
        data[mod] = entry
        save(data)
    return entry


def declare_minor(mod, mod_dir, why):
    """Re-green `mod` at its CURRENT hash. Only valid for a trivial,
    no-gameplay-effect change (owner ruling 2026-09-12) -- this function
    trusts the caller's judgment call but records the diff --stat alongside
    the why so the claim is checkable later, same as the spec requires.
    Refuses a mod with no prior GREEN entry: there is nothing to re-green."""
    with _locked():
        data = load()
        entry = data.get(mod)
        if not entry or entry.get("status") != "GREEN":
            raise RuntimeError(
                "%s has no prior GREEN run to declare minor against -- "
                "run `modcheck run %s` first." % (mod, mod))
        diff_stat = _git(["diff", "--stat", "HEAD", "--", mod_dir]) or \
                   "(git diff --stat unavailable)"
        entry["hash"] = mod_hash(mod_dir)
        entry["minor"] = {"why": why, "diff_stat": diff_stat, "ts": time.time()}
        data[mod] = entry
        save(data)
    return entry


def rename_key(old, new, why):
    """Move `old`'s recorded entry to `new` -- for a mod renamed since it was
    last run (MEASURED 2026-09-17: `FluidCanals` sat GREEN under its dead
    pre-rename name while the mod ships as `FlowWorks`, and a fresh run under
    the new name writes a SEPARATE entry rather than updating the old one, so
    the stale key sits unreferenced forever). This is the rename/forget verb
    the naming migration owed this registry -- hand-editing the JSON is
    forbidden (module docstring), so this is the only sanctioned way to move
    a key.

    Refuses if `old` has no entry (nothing to move) or `new` already has one
    (a rename must never silently clobber a live mod's own run history --
    `forget_key` the dead one first if that is genuinely what is wanted)."""
    with _locked():
        data = load()
        if old not in data:
            raise RuntimeError(
                "%s has no recorded entry -- nothing to rename." % old)
        if new in data:
            raise RuntimeError(
                "%s already has a recorded entry -- renaming %s onto it would "
                "overwrite that entry's own run history. `forget %s` first if "
                "the old key is genuinely dead and disposable, or resolve by "
                "hand." % (new, old, old))
        entry = data.pop(old)
        entry["renamed_from"] = {"old": old, "why": why, "ts": time.time()}
        data[new] = entry
        save(data)
    return entry


def forget_key(key, why):
    """Delete `key`'s entry outright -- for an orphaned key with no successor
    worth preserving (never for a live mod's own bad run; a fresh `run` is
    the way to replace that). Refuses a key with no entry: nothing to forget.
    `why` is recorded nowhere durable past this call's own log line -- if the
    reason matters later, it belongs in the commit message that calls this."""
    with _locked():
        data = load()
        if key not in data:
            raise RuntimeError("%s has no recorded entry -- nothing to forget." % key)
        del data[key]
        save(data)


_NOT_GREEN_WHY = {
    "RED": "RED (last run failed)",
    "REFUSED": "REFUSED (visual floor -- see `refused` in the registry)",
    "DRAFT-CHECKLIST": "DRAFT-CHECKLIST (both halves passed, but the "
                       "must-show bar is not the owner's yet)",
    "PENDING-OWNER-REVIEW": "PENDING-OWNER-REVIEW (both halves passed; needs "
                            "`modcheck review <mod> --owner-said ...` once)",
}


# Step 4 of a checkout (FLOWWORKS_CHECKOUT_SCOPE_1): a mod that ships this script runs its feature chains as a
# SEPARATE live run after the core proof, and its checkout is not green until that run's result is recorded beside
# the core one (`modcheck record <mod> --result <core> --extensions <step4>`, record.py). The script's presence is
# the declaration: no list to keep in sync.
STEP4_SCRIPT = ("northstar", "extension_proof.py")


def step4_required(mod_dir):
    return bool(mod_dir) and os.path.isfile(os.path.join(mod_dir, *STEP4_SCRIPT))


def step4_live(entry, mod_dir):
    """The step-4 state as it stands NOW: None for a mod with no step 4, else PASS / FAIL / UNMEASURED / STALE.
    Only a stored PASS at the mod's current hash reads PASS -- a missing step-4 record is UNMEASURED, never PASS."""
    if not step4_required(mod_dir):
        return None
    s4 = (entry or {}).get("step4") or {}
    st = s4.get("status")
    if st not in ("PASS", "FAIL"):
        return "UNMEASURED"
    if s4.get("mod_hash") != mod_hash(mod_dir):
        return "STALE"
    return st


def _step4_why(entry):
    s4 = (entry or {}).get("step4") or {}
    if not s4:
        return "no step-4 result recorded"
    bits = [s4.get("why") or ""] + ["%s %s" % (k, ",".join(s4.get(k) or [])) for k in ("fail", "unmeasured")
                                    if s4.get(k)]
    return "; ".join(b for b in bits if b) or str(s4.get("status"))


def check(mod, mod_dir):
    """GREEN / STALE / NEVER RUN, or why it is not green. Never touches the
    game. Only the literal string GREEN is a pass -- a gate reading this must
    not treat PENDING-OWNER-REVIEW as one."""
    data = load()
    entry = data.get(mod)
    if not entry:
        return "NEVER RUN"
    recorded = entry.get("status")
    if recorded == "REFUSED" and entry.get("refused"):
        # the stored reason, not the generic visual-floor text: a `modcheck record`
        # refusal names its UNBUILT/UNCOVERED bars, which the generic line would hide
        return "REFUSED (%s)" % entry["refused"]
    s4 = step4_live(entry, mod_dir)
    if recorded == "RED" and s4 in ("FAIL", "UNMEASURED") and entry.get("step4"):
        return "RED (last run failed; step 4 %s: %s)" % (s4, _step4_why(entry))
    if recorded != "GREEN":
        return _NOT_GREEN_WHY.get(recorded, str(recorded))
    if mod_hash(mod_dir) != entry.get("hash"):
        return "STALE"
    if s4 is not None and s4 != "PASS":
        # a GREEN core with no (or a non-PASS) step 4 -- a `modcheck run`, or an entry from before step 4 was wired
        return "%s (step 4 %s: %s)" % ("STALE" if s4 == "STALE" else "UNMEASURED", s4, _step4_why(entry))
    return "GREEN"


def check_or_orphaned(mod):
    """`check(mod, mod_dir)`, but resolves `mod_dir` itself (via
    `runner.find_mod_dir`) instead of trusting a caller-supplied path, and
    returns `"ORPHANED (no such mod folder)"` rather than raising when the
    folder is gone.

    This is the function the aggregate `status` (no-arg) view must call
    per row, in place of printing the stored `entry["status"]` field
    directly -- DETERMINISM_ASSESSMENT.md SS4's first structural fix: "A
    summary must never be able to disagree with the detail it summarises."
    Before this existed, `modcheck status` printed `Pits  GREEN` from the
    stored field while `modcheck status Pits` (which already called
    `check()`) printed `STALE` for the very same mod, and printed
    `FluidCanals  GREEN` for a mod renamed away weeks earlier, because
    `_mod_dir_or_die` (which would have raised) is only reachable from the
    single-mod path, never the no-arg summary loop."""
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import runner  # noqa: E402  local import: avoids a module cycle with runner.py
    try:
        mod_dir = runner.find_mod_dir(mod)
    except RuntimeError:
        return "ORPHANED (no such mod folder)"
    return check(mod, mod_dir)
