"""stage_dispute.py -- the arbiter seam role_launch calls when a stage's check is disputed (role_stage_dispute) and the arbiter run it starts.

Moved verbatim from rimflow/relentless_dispute.py (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES):
only the functions live code reaches (design/RimMandrake/retired_eras_index_2026-11-18.md).
"""
import contextlib
import fcntl
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import item_exam as E  # noqa: E402

CONFIG = os.path.join(HERE, "relentless_dispute.json")
WINNERS = ("setter", "builder", "environment", "bar")


def config(path=None):
    try:
        with open(path or os.environ.get("RELENTLESS_DISPUTE_CONFIG") or CONFIG, encoding="utf-8") as f:
            got = json.load(f)
        return got if isinstance(got, dict) else {"mode": "off"}
    except (OSError, ValueError):
        return {"mode": "off"}


def now_iso():
    return E.iso(time.time())


@contextlib.contextmanager
def _flock(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def exam_of(store, item):
    recover_publish(store, item)
    return E._read(os.path.join(E.item_dir(store, item), "exam.json"))


# ----------------------------------------------------------------------------------------------------------- worker
def find_session(sid):
    """-> the cwd a Claude session was started in (its transcript's first `cwd`), or None when no transcript exists."""
    if not sid:
        return None
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    for p in glob.glob(os.path.join(base, "projects", "*", sid + ".jsonl")):
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                for n, line in enumerate(f):
                    if n > 200:
                        break
                    try:
                        cwd = json.loads(line).get("cwd")
                    except (ValueError, AttributeError):
                        continue
                    if cwd:
                        return cwd
        except OSError:
            continue
    return None


ARBITER_BRIEF = """You are the ARBITER of one dispute on RimMandrake pipeline item {item}. You are not its builder, its exam
Setter, nor its Marker, and you never will be. Your working directory is a read-only export of the repo at the item's
base sha {base}; the exam's own test files are under .exam/. You may run commands here.

The item, in its own words:
---
{text}
---
{body}

{choices}
Write {ruling} as JSON: {{"winner": "{winners}", "why": "<what you read and ran>"}}. Your ruling is final for this run.
End with one line: RULING WRITTEN."""


class Deps:
    """The worker's seams: the Setter/arbiter runner (claude -p), the box, item text, session lookup."""
    def __init__(self, setter=None, boxer=None, text_of=None, find=None, rules=None):
        self.setter = setter or E.run_setter
        self.boxer = boxer or E.box_runner
        self.text_of = text_of or E._item_text
        self.find = find or find_session
        self.rules = rules


def _rules(deps):
    if deps.rules is None:
        import run_store
        deps.rules = run_store.rules()
    return deps.rules


# ------------------------------------------------------------------------------------- the journaled amend publish
PUBLISH_STEPS = ("history", "files", "exam", "status")


def _publish_paths(d):
    return {"journal": os.path.join(d, "amend.journal.json"), "lock": os.path.join(d, "publish.lock"),
            "stage": os.path.join(d, "files.amend"), "files": os.path.join(d, "files")}


def files_of(d, exam_hash):
    """Where a superseded exam's test files are kept (publish moves them there)."""
    return os.path.join(d, "files.%s" % re.sub(r"[^0-9A-Za-z]", "", str(exam_hash or "none"))[:32])


def recover_publish(store, item):
    """Finish an amend publish a dead worker left half-done (its journal is still there). Idempotent; cheap when none."""
    d = E.item_dir(store, item)
    p = _publish_paths(d)
    if not os.path.exists(p["journal"]):
        return False
    with _flock(p["lock"]):
        return _roll_forward(store, item, p)


def _roll_forward(store, item, p, crash_after=None):
    jn = E._read(p["journal"])
    if not isinstance(jn, dict):
        return False
    old, frozen, done = jn.get("old") or {}, jn.get("frozen") or {}, list(jn.get("done") or [])
    d = E.item_dir(store, item)
    for step in PUBLISH_STEPS:
        if step in done:
            continue
        if step == "history":
            hp = os.path.join(d, "exam_history.jsonl")
            if not any(h.get("exam_hash") == old.get("exam_hash") and h.get("superseded_by") == frozen.get("exam_hash")
                       for h in (E._lines(hp) if os.path.exists(hp) else [])):     # a crash after the append: once only
                    E._append(hp, dict(old, superseded_at=jn.get("at") or now_iso(), superseded_by=frozen.get("exam_hash")))
        elif step == "files":
            if os.path.isdir(p["stage"]):        # absent: an earlier pass already moved it in (rename is atomic)
                if os.path.isdir(p["files"]):    # the old exam's files are kept by hash: an arbiter of a dispute the
                    arch = files_of(d, old.get("exam_hash"))          # Setter defended on that exam judges THEM
                    shutil.rmtree(arch, ignore_errors=True)
                    os.replace(p["files"], arch)
                os.replace(p["stage"], p["files"])
        elif step == "exam":
            E._write(os.path.join(d, "exam.json"), frozen)
        elif step == "status":
            E.set_status(store, item, exam_hash=frozen.get("exam_hash"), amended_at=frozen.get("validated_at"))
        done.append(step)
        E._write(p["journal"], dict(jn, done=done))
        if crash_after == step:
            raise RuntimeError("test crash after %s" % step)
    os.remove(p["journal"])
    return True


def _arbiter_run(store, item, base, prompt, ruling_path, out, cfg, deps, winners, files=None):
    """A fresh arbiter (Marker's Judge-mode agent) in a box at base. -> (ruling dict or None, session)."""
    d = E.item_dir(store, item)
    acfg = {"setter_agent": cfg.get("arbiter_agent", "rm-judge"), "setter_model": cfg.get("arbiter_model", "opus"),
            "setter_max_s": cfg.get("arbiter_max_s", 1500)}
    try:
        os.remove(ruling_path)
    except OSError:
        pass
    run, read_file, close = deps.boxer(_rules(deps), os.path.join(store.root, "books"), base, files or os.path.join(d, "files"),
                                       item=item)
    try:
        sid = deps.setter(getattr(read_file, "tree", d), prompt, acfg, out)
    finally:
        close()
    excl = os.path.join(d, "excluded.json")
    with _flock(excl + ".lock"):
        cur = E._read(excl, {"sessions": []}) or {"sessions": []}
        cur["sessions"] = sorted(set(cur.get("sessions", [])) | {sid})
        cur["why"] = "arbiters of this item's disputes: never its Marker (redesign_final G13)"
        E._write(excl, cur)
    r = E._read(ruling_path)
    if isinstance(r, dict) and r.get("winner") in winners:
        return {"winner": r["winner"], "why": str(r.get("why", "")), "session": sid, "at": now_iso()}, sid
    return None, sid


# ------------------------------------------------------------------------------ WP-15: the rejected role stage's arbiter
ROLE_BODY = """The role {role} ({concept}) had its stage close REJECTED by the supervisor twice with the same signature
{sig}. The reasons given:
{reasons}"""
ROLE_CHOICES = ("Rule ONE of: builder (the role's output is right; the stage check is wrong), setter (the check is right; "
                "the role must meet it), environment (the check cannot run where it must), bar (the item text is the problem).")


def role_stage_dispute(role, concept, item, sig, reasons, store=None, cfg=None, deps=None):
    """role_launch.to_arbiter's entry (a 2nd identical rejected role stage): one fresh arbiter rules, the who-was-right
    row is logged under the item's exam dir, nothing is filed. Shadow like the rest: mode off -> None. -> a sentence for
    the ledger, or None (any fault, no mode, no base: today's behaviour, the alarm stands)."""
    try:
        cfg = config() if cfg is None else cfg
        if cfg.get("mode", "off") == "off":
            return None
        import run_store
        store = store or run_store.Store()
        deps = deps or Deps()
        key = item or "ROLE_" + re.sub(r"\W+", "_", os.path.basename(os.path.normpath(concept or "none")))[:60]
        base = (E.status(store, key) or {}).get("base") or (exam_of(store, key) or {}).get("base_sha")
        if not base:
            r = subprocess.run(["git", "-C", HERE, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=60)
            base = r.stdout.strip()
        if not base:
            return None
        d = E.item_dir(store, key)
        ruling_path = os.path.join(d, "role_ruling.json")
        prompt = ARBITER_BRIEF.format(
            item=key, base=base, text=deps.text_of(item) if item else "(no ledger item)",
            body=ROLE_BODY.format(role=role, concept=concept, sig=sig, reasons="\n".join("- %s" % r for r in reasons)),
            ruling=ruling_path, choices=ROLE_CHOICES, winners="|".join(WINNERS))
        ruling = None
        for _ in range(int(cfg.get("arbiter_tries", 2))):
            ruling, _sid = _arbiter_run(store, key, base, prompt, ruling_path, os.path.join(d, "role_arbiter.out"),
                                        cfg, deps, WINNERS)
            if ruling:
                break
        ruling = ruling or {"winner": "void", "why": "the arbiter wrote no ruling", "by": "supervisor", "at": now_iso()}
        E._append(os.path.join(d, "role_dispute.jsonl"), {
            "role": role, "concept": concept, "sig": sig, "winner": ruling["winner"], "final": True,
            "arbiter": ruling.get("session"), "at": now_iso()})
        return "arbiter ruled %s (shadow; %s; nothing filed)" % (ruling["winner"], str(ruling.get("why", "")))
    except Exception:  # noqa: BLE001 - the caller's alarm already stands; a fault here must not break the role launch
        return None
