#!/usr/bin/env python3
"""relentless: the item is the owner, workers are replaceable. RELENTLESS_OWNER_DESIGN_NEVER_LETS_GO.

Design: design/RimMandrake/relentless_owner_design_2026-10-31.md. Limits: relentless_rules.json (data). A program, no AI.
`tick` runs from rm-relentless.timer, out of the supervisor's own clone (<root>/books), which it fast-forwards itself,
so a push to main deploys it and nothing here depends on the FOUNDRY tree.

Threat model: a worker is honest but may be STALE (a process that outlived its lease, or a resumed session). Fencing
stops such a process from completing, reporting or pushing by accident. It is not a sandbox against a hostile agent.

Exit codes for worker verbs: 0 done, 2 usage or refused, 3 FENCED (your lease is gone: stop now).
"""
import argparse
import contextlib
import fcntl
import glob
import hashlib
import importlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import circling  # noqa: E402
import relentless_wall  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.join(HERE, "relentless_rules.json")
ALARM_PREFIXES = ("OPS_", "LIVE_RESTORE_")       # rimflow close refuses these without a live line (cli._live_gate)
DEFAULT_ROOT = "/home/mandrake/rm/relentless"
FENCED = 3
LEASED = ("running", "stopping", "candidate", "checking", "closing", "retiring")   # a worker or the supervisor owns the item
OPEN = ("queued",) + LEASED + ("held",)
MAX_WAIT_HOURS = 6     # a worker's word cannot park an item for longer
HOLDS_A_PLACE = ("running", "checking", "candidate", "stopping", "retiring")    # a run that may be live counts
ENDED = ("done", "retired")
SHARD = "infrastructure/state/ledger/events/%s.jsonl"
NOTE_MAX = 400
NOT_READ = object()
ALLOCATION_FRESH_S = 1800
SLUG_RX = re.compile(r"[^a-z0-9_]+")
POOL_REFUSED = "POOL REFUSED"        # scratch_clone's word: the pool said no, the launch path is healthy
CAUSE_TOKEN = re.compile(r"\S*[\d/_]\S*")   # a run name, a path, a number, an item id: what changes between tries of one fault
POOL_FULL = ("pool full", "pool at")  # make_room's holds: what the staffing reading looks for in the tick's acts
# dirt no worker made on purpose: session dumps and ledger shards the seats' projection rewrites. Bundled, never restored
POOL_NOISE = ("conversations/", "infrastructure/state/ledger/events/", "infrastructure/state/code_review/")
POOL_ORPHAN_IDLE_S = 3600
POOL_IGNORED_MAX = 2 * 10**9
LEDGER_DIR = "infrastructure/state/ledger/events/"
ITEMS_DIR = "infrastructure/state/items/"
BOOKS_DERIVED = (LEDGER_DIR, ITEMS_DIR)
GUARDED_VERBS = ("close", "implemented", "renew", "release", "reclaim", "claim", "start")
NOT_AN_APPROACH = ("worker_lost", "checker_lost")       # a dead process or a silent checker tried nothing


def pkg(name):
    """A rimflow module as the package imports it: priority and friends use relative imports."""
    sys.path.insert(0, os.path.dirname(HERE))
    return importlib.import_module("rimflow." + name)


def root():
    return os.environ.get("RELENTLESS_ROOT") or DEFAULT_ROOT


def rules(path=None):
    with open(path or os.environ.get("RELENTLESS_RULES") or RULES, encoding="utf-8") as f:
        return json.load(f)


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


# ---------------------------------------------------------------- the store (host-wide, ext4, one flock)

ALARM_TOLD_EVERY_S = 6 * 3600     # inside incident.py event_quiet_min, so a standing alarm keeps its incident open


class Store:
    on_alarm = None     # the real Fx sets it: an alarm on the journal is a signal on the told ledger

    def __init__(self, base=None):
        self.root = base or root()
        self.dir = os.path.join(self.root, "store")
        os.makedirs(os.path.join(self.dir, "items"), exist_ok=True)

    def p(self, *a):
        return os.path.join(self.dir, *a)

    def item_dir(self, item):
        return self.p("items", item)

    @contextlib.contextmanager
    def lock(self):
        """Every transition holds this. Never held across a blocking effect (a stop, a launch, a publish)."""
        fd = os.open(self.p(".lock"), os.O_CREAT | os.O_RDWR, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            os.close(fd)

    def _write(self, path, text):
        tmp = "%s.tmp.%d" % (path, os.getpid())
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        d = os.open(os.path.dirname(path), os.O_RDONLY)
        try:
            os.fsync(d)
        finally:
            os.close(d)

    def _append(self, path, line):
        with open(path, "a", encoding="utf-8") as f:
            f.write(line.rstrip("\n") + "\n")
            f.flush()
            os.fsync(f.fileno())

    def load(self, item):
        try:
            with open(os.path.join(self.item_dir(item), "state.json"), encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def save(self, st):
        os.makedirs(os.path.join(self.item_dir(st["item"]), "receipts"), exist_ok=True)
        self._write(os.path.join(self.item_dir(st["item"]), "state.json"), json.dumps(st, indent=1, sort_keys=True))

    def items(self):
        return sorted(os.listdir(self.p("items")))

    def states(self):
        return [s for s in (self.load(i) for i in self.items()) if s]

    def journal(self, rec):
        self._append(self.p("journal.jsonl"), json.dumps(rec, sort_keys=True))
        if self.on_alarm and rec.get("do") == "alarm":
            self.on_alarm(rec)

    def attempts(self, item):
        try:
            with open(os.path.join(self.item_dir(item), "attempts.jsonl"), encoding="utf-8") as f:
                lines = f.readlines()
        except (OSError, ValueError):
            return []
        out = []
        for ln in lines:        # one torn line loses that line, never the record around it
            try:
                out.append(json.loads(ln))
            except ValueError:
                pass
        return out

    def attempt(self, item, rec):
        self._append(os.path.join(self.item_dir(item), "attempts.jsonl"), json.dumps(rec, sort_keys=True))

    def learn(self, item, text):
        self._append(os.path.join(self.item_dir(item), "learned.md"), text)

    def learned(self, item):
        try:
            with open(os.path.join(self.item_dir(item), "learned.md"), encoding="utf-8") as f:
                return f.read()
        except OSError:
            return ""

    def receipt_path(self, item, gen):
        return os.path.join(self.item_dir(item), "receipts", "gen%d.json" % gen)

    def read_receipt(self, item, gen):
        try:
            with open(self.receipt_path(item, gen), encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return None


def new_state(item, now, why):
    return {"item": item, "status": "queued", "gen": 0, "enrolled_at": now, "why": why, "returned_at": None,
            "returns": 0, "failures": {}, "total_failures": 0, "approach": "build", "approach_changes": 0,
            "spent": 0, "attempts": 0, "unit": None, "scope": None, "clone": None, "started_at": None,
            "last_beat": None, "stopping_since": None, "contract": None, "candidate": None, "check": None,
            "hold": None, "last_fail": None, "last_sha": None, "sha_at_change": None, "run": None,
            "not_before": 0, "ledger_started": False, "start_intent": False, "done_at": None, "quarantined": []}


def queue_order(states, plan=None):
    """The priority list first (`plan`: {item: place}, DI3), then returned items, oldest return first, then fresh in
    enrol order. Pure."""
    plan = plan or {}
    q = [s for s in states if s["status"] == "queued"]
    return sorted(q, key=lambda s: (0, plan[s["item"]], s["item"]) if s["item"] in plan
                  else (1, s["returned_at"], s["item"]) if s["returned_at"] is not None
                  else (2, s["enrolled_at"], s["item"]))


def fail(store, st, klass, detail, r, now):
    """Under the lock. Fence first: gen moves here, before anything is stopped. The item goes to the TOP."""
    klass = SLUG_RX.sub("_", (klass or "snag").lower()).strip("_")[:40] or "snag"
    st["gen"] += 1
    st["status"] = "stopping"
    st["stopping_since"] = now
    st["returned_at"] = now
    st["returns"] += 1
    st["failures"][klass] = st["failures"].get(klass, 0) + 1
    st["total_failures"] += 1
    st["last_fail"] = {"class": klass, "detail": (detail or "")[:2000], "at": now}
    limit = r["same_failure_limit"]
    # rotating slugs cannot dodge this: enough returns with no new sha also change the approach
    unchanged = st["total_failures"] - (st.get("total_at_change") or 0) >= r.get("unchanged_returns_limit", limit * 3)
    if st["failures"][klass] >= limit or unchanged:
        st["failures"][klass] = 0
        st["total_at_change"] = st["total_failures"]
        st["approach_changes"] += 1
        wanted = "pilot" if st.get("pilot_wanted") else "redesign"
        st["approach"] = ("redesign" if st["approach"] == "pilot" else
                          "pilot" if st["approach"] == "redesign" else wanted)
    store.attempt(st["item"], {"at": iso(now), "gen": st["gen"] - 1, "end": klass, "detail": (detail or "")[:600],
                               "approach_next": st["approach"]})
    store.learn(st["item"], "- %s gen %d ended %s: %s" % (iso(now), st["gen"] - 1, klass, (detail or "")[:600]))
    if klass == "circling":     # under this lock, so no tick can lease the next worker ahead of the consult
        st["circling_hits"] = st.get("circling_hits", 0) + 1
        force_help(store, st, r, now)
    store.save(st)


def day_key(now):
    return time.strftime("%Y%m%d", time.gmtime(now))


def _day(store, now):
    try:
        with open(store.p("spend-%s.json" % day_key(now)), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"spent": 0, "runs": {}}


def spent_today(store, now):
    return int(_day(store, now).get("spent", 0))


def charge(store, st, tokens, now, r, unit):
    """Under the lock. A run with no measured usage is charged the reserve, never less. The day file is keyed by run,
    so a crash before the item's own marker is saved cannot count a run twice."""
    n = int(tokens) if tokens else r["run_reserve"]
    d = _day(store, now)
    if unit not in d["runs"] and unit not in _day(store, now - 86400)["runs"]:
        d["runs"][unit] = n
        d["spent"] += n
        store._write(store.p("spend-%s.json" % day_key(now)), json.dumps(d))
    st["spent"] += n
    return n


# ---------------------------------------------------------------- what a worker may call (all fenced)

class Fenced(Exception):
    pass


def _fence(st, item, gen):
    if st is None:
        raise Fenced("%s is not enrolled" % item)
    if st["gen"] != gen or st["status"] != "running":
        raise Fenced("%s: your lease gen %d is gone (now gen %d, %s). Stop now." % (item, gen, st["gen"], st["status"]))


def beat(store, item, gen, now=None):
    with store.lock():
        st = store.load(item)
        _fence(st, item, gen)
        st["last_beat"] = time.time() if now is None else now
        store.save(st)


def learn(store, item, gen, text, now=None):
    with store.lock():
        st = store.load(item)
        _fence(st, item, gen)
        st["last_beat"] = time.time() if now is None else now
        store.learn(item, "- %s gen %d: %s" % (iso(st["last_beat"]), gen, text))
        store.save(st)


def contract(store, item, gen, proof, live=None, why=None, now=None):
    """Set by the first worker before it edits; only a redesign may change it, and says why."""
    import live_line
    if live:
        live_line.parse(live)
    now = time.time() if now is None else now
    with store.lock():
        st = store.load(item)
        _fence(st, item, gen)
        if st["contract"] and st["approach"] != "redesign":
            raise ValueError("the contract is set; only a redesign attempt may change it")
        if st["contract"] and not why:
            raise ValueError("changing the contract needs --why")
        st["contract"] = {"proof": proof, "live": live, "by_gen": gen, "why": why}
        st["last_beat"] = now
        store.attempt(item, {"at": iso(now), "gen": gen, "contract": st["contract"]})
        store.save(st)


def snag(store, item, gen, klass, detail, r, section=None, now=None, wait_hours=0):
    """`wait_hours`: what stopped the worker is time, not work (a metric's sample filling); no worker starts before then."""
    now = time.time() if now is None else now
    with store.lock():
        st = store.load(item)
        _fence(st, item, gen)
        if klass == "owner_call" and section:
            st["gen"] += 1
            st["status"] = "stopping"
            st["stopping_since"] = now
            st["hold"] = {"why": "delegation_policy section 2: %s: %s" % (section, (detail or "")[:600]),
                          "kind": "owner_call", "delivered": False, "at": now}
            store.attempt(item, {"at": iso(now), "gen": gen, "end": "owner_call", "detail": st["hold"]["why"]})
            store.save(st)
            return
        st["not_before"] = now + min(wait_hours or 0, MAX_WAIT_HOURS) * 3600
        fail(store, st, klass, detail, r, now)


def finish(store, item, gen, sha, evidence, now=None):
    """The durable receipt. The result never depends on a notification: the tick finds it here."""
    now = time.time() if now is None else now
    with store.lock():
        st = store.load(item)
        _fence(st, item, gen)
        if not st["contract"]:
            raise ValueError("no contract: set it with `contract` before finishing")
        rec = {"item": item, "gen": gen, "sha": sha, "evidence": evidence, "at": iso(now), "contract": st["contract"],
               "hash": hashlib.sha256(json.dumps(st["contract"], sort_keys=True).encode()).hexdigest()}
        store._write(store.receipt_path(item, gen), json.dumps(rec, indent=1, sort_keys=True))
        _take_receipt(store, st, rec, now)


def _take_receipt(store, st, rec, now):
    st["candidate"] = {"sha": rec["sha"], "gen": rec["gen"], "evidence": rec["evidence"], "at": now}
    st["status"] = "candidate"
    st["last_sha"] = rec["sha"]
    store.attempt(st["item"], {"at": iso(now), "gen": rec["gen"], "end": "finish", "sha": rec["sha"]})
    store.save(st)


# ---------------------------------------------------------------- calling for help (RW3, design relentless_agent 7)

def failed_approaches(store, item):
    """What was tried and ended in failure, from the record the supervisor wrote, never a worker's say-so."""
    return [a for a in store.attempts(item) if "approach_next" in a and a.get("end") not in NOT_AN_APPROACH]


def help_pending(st):
    return ((st or {}).get("help") or {}).get("status") in ("wanted", "running")


def help_cool_left(st, r, now):
    last = st.get("help_last_at")
    return max(0, last + r["circling"]["help_cool_h"] * 3600 - now) if last is not None else 0


def _want_help(store, st, why, by, now):
    """Any consult uses up the hits so far: a worker's own call and the forced one are not two."""
    st["help"] = {"status": "wanted", "why": (why or "")[:600], "by": by, "at": now, "tries": 0, "gen": st["gen"]}
    st["help_last_at"] = now
    st["help_hits_used"] = st.get("circling_hits", 0)
    store.journal({"at": iso(now), "do": "help_wanted", "item": st["item"], "by": by})


def force_help(store, st, r, now):
    """Under the lock; the caller saves. -> True when this call asked for the consult."""
    n = (r.get("circling") or {}).get("help_after_circling")
    if not n or st.get("circling_hits", 0) - st.get("help_hits_used", 0) < n:
        return False
    if help_pending(st) or help_cool_left(st, r, now) or not failed_approaches(store, st["item"]):
        return False
    _want_help(store, st, "forced: %d circling stops" % st["circling_hits"], "tick", now)
    return True


def ask_help(store, item, gen, why, r, now=None):
    """A worker's call, any time. `gen` None is someone outside the lease (an operator): nothing to fence."""
    now = time.time() if now is None else now
    with store.lock():
        st = store.load(item)
        if gen is not None:
            _fence(st, item, gen)
        elif st is None:
            raise ValueError("%s is not enrolled" % item)
        if st["status"] in ENDED:
            raise ValueError("%s is %s" % (item, st["status"]))
        if not failed_approaches(store, item):
            raise ValueError("%s has no failed approach on record: nothing for a fresh eye to read. Fail first." % item)
        if help_pending(st):
            raise ValueError("%s already has a consult %s" % (item, st["help"]["status"]))
        left = help_cool_left(st, r, now)
        if left:
            raise ValueError("%s had a consult; the next in %d min (help_cool_h)" % (item, left // 60 + 1))
        _want_help(store, st, why, "gen %d" % gen if gen is not None else "operator", now)
        if gen is not None:
            st["last_beat"] = now
        store.save(st)


def parse_options(options, r):
    """'idea | the one observation that confirms or kills it', each. A hypothesis with no test is refused."""
    most = r["circling"]["help_options_max"]
    if not options or len(options) > most:
        raise ValueError("give 1 to %d options" % most)
    out = []
    for o in options:
        idea, _, see = o.partition("|")
        if not idea.strip() or not see.strip():
            raise ValueError("an option is 'idea | the one observation that confirms or kills it': %s" % o[:80])
        out.append({"idea": idea.strip()[:600], "observe": see.strip()[:600]})
    return out


def help_answer(store, item, nonce, options, r, now=None):
    """The consult's return. Into the state file at once, so nothing past this line depends on the unit."""
    now = time.time() if now is None else now
    got = parse_options(options, r)
    with store.lock():
        st = store.load(item)
        h = (st or {}).get("help") or {}
        if not h or h.get("status") != "running" or h.get("nonce") != nonce or h.get("expired") or h.get("answered_at"):
            raise Fenced("%s: no consult is waiting for that nonce" % item)
        h["answered_at"] = now
        st["help_options"] = {"options": got, "at": now, "by_unit": h["run"]["unit"]}
        store.attempt(item, {"at": iso(now), "gen": st["gen"], "help": "answered", "options": len(got)})
        store.save(st)


def verdict(store, item, nonce, word, reasons, now=None):
    now = time.time() if now is None else now
    word = word.upper()
    if word not in ("PASS", "FAIL"):
        raise ValueError("verdict is PASS or FAIL")
    with store.lock():
        st = store.load(item)
        chk = (st or {}).get("check") or {}
        if not st or st["status"] != "checking" or chk.get("nonce") != nonce or chk.get("expired"):
            raise Fenced("%s: no check is waiting for that nonce" % item)
        chk["verdict"] = word
        chk["reasons"] = (reasons or "")[:4000]
        chk["verdict_at"] = now
        store.save(st)


def fence_check(store, item, gen):
    """-> None when this generation may push, else why not. A generation in candidate or later has finished: the
    worker's unit is on its way out, so it may no longer land anything."""
    st = store.load(item)
    if st is None:
        return None if not item else "%s is not enrolled" % item
    if st["gen"] != gen or st["status"] != "running":
        return "%s: lease gen %d is gone (now gen %d, %s)" % (item, gen, st["gen"], st["status"])
    return None


def hook_fence(toplevel, store=None):
    """pre-push. No marker file in .git: not a relentless clone, nothing to say."""
    try:
        with open(os.path.join(toplevel, ".git", "relentless.json"), encoding="utf-8") as f:
            m = json.load(f)
    except (OSError, ValueError):
        return None
    gen = os.environ.get("RELENTLESS_GEN")     # set at launch, so a resumed old session cannot read the new marker
    return fence_check(store or Store(), m["item"], int(gen) if gen else m["gen"])


def guard(verb, item, argv, env=None, store=None):
    """rimflow calls this. A leased item's ledger state belongs to the supervisor; his own word always passes.
    -> None, or why not."""
    env = os.environ if env is None else env
    if verb not in GUARDED_VERBS or not item or env.get("RELENTLESS_SUPERVISOR") == "1":
        return None
    if any(a == "--owner-said" or a.startswith("--owner-said=") for a in argv):
        return None
    if store is None and not os.path.isdir(os.path.join(root(), "store")):
        return None
    st = (store or Store()).load(item)
    if st and st["status"] in LEASED:
        return ("%s is carried by relentless (gen %d, %s). `%s` belongs to its supervisor; a worker reports with "
                "relentless.py, and the owner's word (--owner-said) always passes." % (item, st["gen"], st["status"],
                                                                                       verb))
    return None


def _conductor_authority():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Utils"))
    import conductor_authority
    return conductor_authority


def unhold(store, item, said, now=None):
    now = time.time() if now is None else now
    with store.lock():
        st = store.load(item)
        if not st or st["status"] != "held":
            raise ValueError("%s is not held" % item)
        st["hold"] = None
        st["status"] = "queued"
        st["returned_at"] = now
        st["spent_grace"] = st["spent"]         # his yes buys another full limit from here
        st["needs_back"] = True
        store.attempt(item, {"at": iso(now), "end": "unhold", "said": said})
        store.save(st)


# ---------------------------------------------------------------- what the world does (the selftest plants these)

class Effects:
    """The real one. Every method here blocks, so none is called under the store lock."""

    def __init__(self, r, store):
        self.r = r
        self.store = store
        self.base = store.root
        self.books = os.path.join(self.base, "books")
        self._ledger = None
        self._budget = self._helpers = NOT_READ
        self.bounce = set()
        self.marked = set()
        import role_launch as RL
        self.RL = RL

    # the ledger, through the books clone
    def rimflow(self, *args, timeout=60, seat=None):
        env = dict(os.environ, RIMFLOW_SEAT=seat or self.r["seat"], AGENT_SEAT=seat or self.r["seat"],
                   RELENTLESS_SUPERVISOR="1", CLAUDE_PROJECT_DIR=self.books)
        return subprocess.run(["python3", os.path.join(self.books, "src/RimMandrake/rimflow/cli.py"), *args],
                              cwd=self.books, env=env, capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)

    def git(self, cwd, *args, timeout=120):
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)

    def sync(self):
        """The engine runs from books, so a clone that cannot move freezes the engine. -> None, or why it is behind.
        --ff-only fails without a word on one rimflow-moved item file or one landed ledger commit: 15 hours, 2026-11-01."""
        self._ledger = None
        self._budget = self._helpers = NOT_READ
        try:
            got = self.git(self.books, "fetch", "--quiet", "origin")
            if got.returncode:      # every check below reads origin/main: an old one passes them all and says nothing
                return "books cannot fetch: %s" % got.stderr[-300:]
            why = self.ignored_collision()
            if why:
                return why
            self.git(self.books, "merge", "--ff-only", "--quiet", "origin/main")
            return self.level_books()
        except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as e:
            return "books cannot level: %s" % str(e)[:300]

    def ignored_collision(self):
        """-> why, when origin newly tracks a path the clone holds as an IGNORED file with other bytes. Neither a merge
        nor `reset --keep` protects it and `status` cannot see it, so the check is the only thing between it and loss."""
        new = self.git_ok(self.books, "diff", "--name-only", "--no-renames", "--diff-filter=A", "-z", "HEAD", "origin/main").split("\0")
        for p in filter(None, new):
            src = os.path.join(self.books, p)
            parts = p.split("/")
            for q in ("/".join(parts[:i]) for i in range(1, len(parts))):       # a file where origin wants a folder
                at = os.path.join(self.books, q)
                if os.path.lexists(at) and not os.path.isdir(at) and \
                        self.git(self.books, "ls-files", "--error-unmatch", "--", q).returncode != 0:
                    return "books behind: ignored file %s stands where origin now tracks %s" % (q, p)
            if os.path.isdir(src) and not os.path.islink(src):                  # a folder where origin wants a file
                if self.git_ok(self.books, "ls-files", "--others", "-z", "--", p).strip("\0"):
                    return "books behind: ignored files under %s stand where origin now tracks a file" % p
                continue
            if not os.path.isfile(src) or self.git(self.books, "ls-files", "--error-unmatch", "--", p).returncode == 0:
                continue
            with open(src, "rb") as f:
                here = f.read()
            there = subprocess.run(["git", "-C", self.books, "show", "origin/main:" + p], capture_output=True,
                                   check=True, timeout=60).stdout
            if here != there:
                return "books behind: ignored file %s differs from what origin now tracks there" % p
        return None

    def level_books(self):
        """Behind origin: level the clone when all it holds is ledger already landed and item files rimflow rewrites."""
        behind = self.git_ok(self.books, "rev-list", "--count", "HEAD..origin/main").strip()
        if behind in ("0", ""):
            return None
        out = self.git_ok(self.books, "status", "--porcelain", "--no-renames", "-z", "--untracked-files=all")
        rows = [(x[:2], x[3:]) for x in out.split("\0") if x]
        staged = self.git_ok(self.books, "diff", "--cached", "--name-only").split()
        if staged:      # the index is nobody's projection, and the checks below read the working tree
            return "books %s behind: staged: %s" % (behind, ", ".join(staged[:5]))
        alien = [p for _s, p in rows if not p.startswith(BOOKS_DERIVED)]
        if alien:
            return "books %s behind: dirty outside the ledger: %s" % (behind, ", ".join(alien[:5]))
        changed = self.git_ok(self.books, "diff", "--name-only", "origin/main...HEAD").split()
        alien = [p for p in changed if not p.startswith(BOOKS_DERIVED)]
        if alien:
            return "books %s behind: own commits outside the ledger: %s" % (behind, ", ".join(alien[:5]))
        read = {}
        for p in sorted({p for p in changed if p.startswith(LEDGER_DIR)} | {p for _s, p in rows if p.startswith(LEDGER_DIR)}):
            with open(os.path.join(self.books, p), "rb") as f:
                read[p] = f.read()
            lost = set(read[p].decode("utf-8").splitlines()) - set(self.git_ok(self.books, "show", "origin/main:" + p).splitlines())
            if lost:
                return "books %s behind: %d lines of %s not landed" % (behind, len(lost), p)
        keep = self.store.p("books_dirt", time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
        for state, p in rows:
            src = os.path.join(self.books, p)
            if p in read:
                with open(src, "rb") as f:
                    if f.read() != read[p]:     # a writer came in behind the check
                        return "books %s behind: %s moved while levelling" % (behind, p)
            if os.path.isfile(src):
                os.makedirs(os.path.dirname(os.path.join(keep, p)), exist_ok=True)
                shutil.copy2(src, os.path.join(keep, p))
            if state == "??":
                os.remove(src)
            else:
                os.makedirs(os.path.dirname(src), exist_ok=True)
                with open(src, "wb") as f:
                    f.write(subprocess.run(["git", "-C", self.books, "show", "HEAD:" + p], capture_output=True, check=True, timeout=60).stdout)
        self.git(self.books, "update-index", "-q", "--refresh")   # same bytes, new stat: reset --keep reads that as dirt
        self.git_ok(self.books, "reset", "--keep", "origin/main")
        return None

    def flush(self):
        """Publish the shard: retried each tick until it lands, so a close never stays local."""
        shards = [SHARD % self.r["seat"], SHARD % "RUNNER"]     # RUNNER: the alarm's `live` line
        got = self.git(self.books, "status", "--porcelain", "--", *shards).stdout.strip()
        moved = self.prose_moves()
        ahead = self.git(self.books, "rev-list", "--count", "origin/main..HEAD").stdout.strip()
        if not got and not moved and ahead in ("0", ""):
            return None
        dirty = [x for x in shards if x in got] + moved
        a = ["./publish"] + (["-m", "ledger: relentless supervisor", *dirty] if dirty else [])
        r = subprocess.run(a, cwd=self.books, capture_output=True, text=True, timeout=90, stdin=subprocess.DEVNULL)
        return None if r.returncode == 0 else "publish exit %d: %s" % (r.returncode, (r.stderr or r.stdout)[-300:])

    def prose_moves(self):
        """-> both paths of each item whose prose `rimflow close` moved to items/closed/. The ledger line lands; unpublished,
        the move sits dirty here until level_books undoes it, and selftest_items_glob_live goes red on the done item.
        A pair only: a lone deletion or a lone new file is not a close, so it stays out of the commit."""
        rows = self.git(self.books, "status", "--porcelain", "--no-renames", "-z", "--untracked-files=all", "--",
                        ITEMS_DIR).stdout.split("\0")
        rows = [(x[:2], x[3:]) for x in rows if x]
        gone = {p[len(ITEMS_DIR):] for s, p in rows if "D" in s and "/" not in p[len(ITEMS_DIR):]}
        new = {p[len(ITEMS_DIR) + len("closed/"):] for s, p in rows if s == "??" and p.startswith(ITEMS_DIR + "closed/")}
        return [p for n in sorted(gone & new) for p in (ITEMS_DIR + n, ITEMS_DIR + "closed/" + n)]

    def ledger_items(self):
        if self._ledger is None:
            model = pkg("model")
            evs = model.read()
            self._ledger = (evs, model.replay(evs))
        return self._ledger

    def pool_order(self, r):
        """Open items in the pool, best first: the priority list, then Test Pilot bouncers, raised, then rank().
        A list that cannot be obeyed gives no order, and ops_watch's plan family reads that as distressed."""
        priority, testpilot_route, model = pkg("priority"), pkg("testpilot_route"), pkg("model")
        plist = pkg("priority_list")
        orders = plist.order_map(plist.load(self.books)["entries"])
        evs, w = self.ledger_items()
        bounce = self.bounce = {v["id"] for v in testpilot_route.routed(w, evs)}
        targets = r.get("pool_targets") or ["v1"]
        # not priority.rank(): `next` offers only what a seat already took up, and the pool is the proposed backlog.
        # The same sort, so raised work and the campaign rows still go first
        words = self.seat_words()
        pool = [it for it in w.items.values() if eligible(it, r) and it.target in (None, *targets)
                and (it.owner != foreign_seat(r) or (words is not None and it.id not in words))]
        pool.sort(key=lambda i: (plist.position(i, orders), i.id not in bounce, model.raise_key(i), not i.this_deployment,
                                 priority._row_key(i), i.created_at or "", i.id))
        pool = [i for i in pool if i.kind != "mod" or not self.concept_refusal(i.id)]   # no tree, no worker
        self.plan = {i.id: plist.position(i, orders) for i in pool if plist.position(i, orders) <= plist.MAX_ENTRIES}
        return [i.id for i in pool], w

    def concept_refusal(self, item):
        """Why this item may not reach a worker, or None: a mod needs a well-defined tree (concept_tree.gate)."""
        _, w = self.ledger_items()
        it = w.items.get(item)
        return concept_refused(self.books, item, getattr(it, "kind", None))

    def item_state(self, item):
        _, w = self.ledger_items()
        it = w.items.get(item)
        return None if it is None else {"state": it.state, "lease": getattr(it, "lease", None), "needs": it.needs,
                                        "owner": it.owner}

    # the other seat: read from its tree, never pulled, never written
    def seat_words(self):
        """Ids the other seat has said something about that the books have not heard: a claim, start or close it has
        not published. Raw lines, not a replay, so no reading of its state can go wrong. None when that tree cannot be
        read or a line is torn: then none of its items may be taken."""
        cfg = self.r.get("staffing") or {}
        out = set()
        try:
            for seat in (cfg["foreign_seat"], "OWNER"):
                rel = SHARD % seat
                with open(os.path.join(cfg["foreign_tree"], rel), encoding="utf-8") as f:
                    there = set(f)
                try:
                    with open(os.path.join(self.books, rel), encoding="utf-8") as f:
                        there -= set(f)
                except FileNotFoundError:
                    pass
                out.update(json.loads(ln).get("id") for ln in there)
        except (KeyError, OSError, ValueError, AttributeError):
            return None
        return out - {None}

    def seat_heard(self, item, since):
        """True once the other seat's tree holds this close of this item (`since` an iso time before it), so its own
        ledger shows the item gone. Parsed: a substring would answer for another id, an old event or a torn line."""
        cfg = self.r["staffing"]
        try:
            with open(os.path.join(cfg["foreign_tree"], SHARD % self.r["seat"]), encoding="utf-8") as f:
                for ln in f:
                    if item not in ln:
                        continue
                    try:
                        ev = json.loads(ln)
                    except ValueError:
                        continue
                    if ev.get("id") == item and ev.get("event") == "close" and str(ev.get("ts", "")) >= since:
                        return True
        except OSError:
            pass
        return False

    def foreign_fits(self, item):
        """The whole eligibility again at launch: what was true at enrol may have changed on the ledger."""
        _, w = self.ledger_items()
        it = w.items.get(item)
        return it is not None and eligible(it, self.r) and it.target in (None, *(self.r.get("pool_targets") or ["v1"]))

    def settle_wait(self, s):
        time.sleep(s)       # a claim that passed the guard just before the reservation reaches its shard in this time

    def ledger_take(self, item):
        r = self.rimflow("reassign", item, "--to", self.r["seat"], "--reason", "relentless staffs it",
                         "--why", "relentless filler takes a proposed item of the other seat")
        self._ledger = None
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    def focus_cap(self):
        """The Producer's WIP cap from the schedule (RO2), the number `next` holds: relentless's open work obeys it too.
        Absent: no limit. Damaged: 1, the lowest, like an unreadable budget."""
        try:
            c = pkg("priority").focus_config()
        except ValueError:
            return 1
        return c["per_seat"] if c else None

    # the staffing readings
    def budget(self):
        """The budget of the staffed seat as published; None when not trustworthy now."""
        if self._budget is NOT_READ:
            rec = pkg("helper_budget").read()
            self._budget = (rec or {}).get("seats", {}).get(self.r["staffing"]["seat"]) if rec else None
        return self._budget

    def allocation(self):
        """The allocator's last inputs, when fresh enough to mean now; {} otherwise. Both readers below degrade to
        None, which the reading shows."""
        try:
            with open(pkg("helper_budget")._sa().streams_dir() / "allocation.json", encoding="utf-8") as f:
                rec = json.load(f)
            return rec.get("inputs") or {} if time.time() - rec["t"] < ALLOCATION_FRESH_S else {}
        except (OSError, ValueError, KeyError, TypeError, ImportError):
            return {}

    def head_helpers(self):
        """Helpers the staffed seat's head runs itself: they are on the same budget. None unmeasured (counted 0)."""
        if self._helpers is NOT_READ:
            v = (self.allocation().get("helpers_running") or {}).get(self.r["staffing"]["seat"])
            self._helpers = v if isinstance(v, int) else None
        return self._helpers

    def burn(self):
        """The account's %/h as the allocator last measured it, or None."""
        v = self.allocation().get("rate_pct_per_h")
        return float(v) if isinstance(v, (int, float)) else None

    def oom_kills(self):
        """The kernel's count of OOM kills since boot, cgroup ceilings included; None unreadable."""
        try:
            with open("/proc/vmstat") as f:
                for ln in f:
                    if ln.startswith("oom_kill "):
                        return int(ln.split()[1])
        except (OSError, ValueError):
            pass
        return None

    def staffing_alarm(self, item, text):
        """One fixed item: filed once, a note while open, reopened when it was closed. -> None, or why it did not land."""
        st = self.item_state(item)
        if st is None:
            r = self.rimflow("file", item, "--for", self.r["seat"], "--kind", "bug", "--needs", "offline",
                             "--title", text[:200], "--why", "relentless filler: staffing alarm")
        elif st["state"] in ("done", "built", "validated"):
            r = self.rimflow("live", item, "--result", "broken", "--detail", text[:300], seat="RUNNER")
        elif st["state"] in ("dropped", "superseded"):
            return "%s is %s: nowhere for the alarm to land" % (item, st["state"])
        else:
            r = self.rimflow("note", item, "--text", text[:NOTE_MAX], "--why", "relentless filler: staffing alarm")
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    def item_text(self, item):
        r = self.rimflow("show", item)
        return (r.stdout or "")[:12000]

    def ledger_start(self, item):
        r = self.rimflow("start", item, "--why", "relentless supervisor takes the item")
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    def ledger_reclaim(self, item):
        r = self.rimflow("reclaim", item, "--why", "relentless supervisor: excluded in the rules, back to the pool")
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    def ledger_close(self, item, sha, reason, live=None):
        # the blind PASS on that sha is the check `close` asks for; RUNNER may record it on any seat's item
        if (item, sha) not in self.marked:
            r = self.rimflow("verify", item, "--sha", sha, "--result", "pass", "--level", "L0",
                             "--config", "marker:blind-check", "--evidence", reason[:300], seat="RUNNER")
            if r.returncode != 0:
                return (r.stderr or r.stdout)[-400:]
            self.marked.add((item, sha))
        r = self.rimflow("close", item, "--sha", sha, "--reason", reason, "--why", "relentless: blind check passed",
                         *(("--live", live) if live else ()))     # the sweep keeps checking what the contract promised
        if r.returncode == 0:
            return None
        if self.closed(item):
            return None
        out = r.stderr or r.stdout
        return out[:600] if "has not earned its close" in out else out[-400:]     # the gate's reasons are at the top

    def closed(self, item):
        self.sync()
        st = self.item_state(item)
        return bool(st and st["state"] == "done")

    def ledger_note(self, item, text):
        r = self.rimflow("note", item, "--text", text[:NOTE_MAX], "--why", "relentless supervisor")
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    def ledger_needs_owner(self, item, why):
        return self.ledger_needs(item, "owner", why)

    def ledger_needs(self, item, to, why):
        r = self.rimflow("needs", item, "--to", to, "--reason", why[:NOTE_MAX], "--why", "relentless supervisor")
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    # the clones
    def clone_path(self, item, q=0):
        return os.path.join(self.base, "clones", item + (".q%d" % q if q else ""))

    def prepare(self, st):
        """The item's clone (made once, kept across workers) and its fence marker."""
        c = st["clone"]
        if not os.path.isdir(os.path.join(c, ".git")):
            env = dict(os.environ, RM_SCRATCH_ROOT=os.path.dirname(os.path.dirname(c)), RM_SEAT="clones")
            r = subprocess.run(["python3", os.path.join(self.books, "src/RimMandrake/Utils/scratch_clone.py"), "clone",
                                "relentless " + st["item"], "--name", os.path.basename(c), "--checkout", "--fetch"],
                               cwd=self.books, env=env, capture_output=True, text=True, timeout=400,
                               stdin=subprocess.DEVNULL)
            if r.returncode:
                return "clone failed: %s" % (r.stderr or r.stdout)[-300:]
        if st.get("bundle"):      # outside the clone's making: a tick that died between the two still restores
            self.restore_bundle(st["item"], st["bundle"], c)
            with self.store.lock():
                cur = self.store.load(st["item"])
                cur.pop("bundle", None)
                self.store.save(cur)
        with open(os.path.join(c, ".git", "relentless.json"), "w", encoding="utf-8") as f:
            json.dump({"item": st["item"], "gen": st["gen"]}, f)
        return None

    def scratch_clone(self):
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
        return importlib.import_module("scratch_clone")

    def pool_clones(self):
        return sorted(d for d in glob.glob(os.path.join(self.base, "clones", "*")) if self.clone_present(d))

    def clone_present(self, c):
        return os.path.isdir(c)   # a half-removed clone still takes its path and its bytes

    def pool_load(self):
        """-> (clones, bytes, cap on clones, cap on bytes). The caps are scratch_clone's, the owner's numbers."""
        sc = self.scratch_clone()
        got = self.pool_clones()
        cmax, bmax = sc.pool_cap()
        return len(got), sum(sc.clone_bytes(sc.Path(c)) for c in got), cmax, bmax

    def clone_busy(self, c):
        sc = self.scratch_clone()
        return sc.clone_in_use(sc.Path(c))

    def clone_idle_s(self, c):
        sc = self.scratch_clone()
        return sc.clone_idle_s(sc.Path(c))

    def clone_wip(self, c):
        """-> {"kept": commits or a stash no remote has, "real": changed paths a worker meant}. An unreadable clone is
        kept: nothing about it is known. Commits have no way back into a fresh clone, so only a dead item's may go."""
        try:
            kept = self.git_ok(c, "rev-list", "HEAD", "--branches", "--tags", "--not", "--remotes").strip() != ""
            kept = kept or self.git_ok(c, "stash", "list").strip() != ""
            return {"kept": kept, "real": [p for p in self.changed_paths(c) + self.ignored_paths(c) if not p.startswith(POOL_NOISE)]}
        except (RuntimeError, OSError, ValueError, subprocess.SubprocessError):
            return {"kept": True, "real": []}

    def git_ok(self, cwd, *args):
        r = self.git(cwd, *args, timeout=300)
        if r.returncode:
            raise RuntimeError("git %s: %s" % (args[0], r.stderr[-200:]))
        return r.stdout

    def changed_paths(self, c):
        out = self.git_ok(c, "--no-optional-locks", "status", "--porcelain", "--untracked-files=normal", "--no-renames", "-z")
        return [x[3:] for x in out.split("\0") if x]

    def ignored_paths(self, c):
        """Ignored files are nobody else's copy either. Bytecode is the one thing that is only ever derived."""
        out = self.git_ok(c, "ls-files", "-z", "--others", "--ignored", "--exclude-standard").split("\0")
        return [p for p in out if p and "__pycache__/" not in p and not p.endswith(".pyc")]

    def bundle_clone(self, item, c):
        """Everything no remote has, on the store's disk, before a clone goes. -> the bundle dir, None when there is
        nothing. Raises when it cannot be sure: the caller then keeps the clone."""
        paths = self.changed_paths(c)
        commits = self.git_ok(c, "rev-list", "HEAD", "--branches", "--tags", "--not", "--remotes").strip()
        stash = self.git_ok(c, "stash", "list", "--format=%H").split()
        ignored = self.ignored_paths(c)
        if not paths and not commits and not stash and not ignored:
            return None
        if sum(os.lstat(os.path.join(c, p)).st_size for p in ignored) > POOL_IGNORED_MAX:
            raise RuntimeError("ignored files over %d bytes: read them before this clone goes" % POOL_IGNORED_MAX)
        home = self.store.p("items", item) if os.path.isdir(self.store.p("items", item)) else self.store.p("orphans")
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        out = os.path.join(home, "bundles", "%s-%s" % (stamp, os.path.basename(c)))
        os.makedirs(out, exist_ok=True)
        real = [":(top)" + p for p in paths if not p.startswith(POOL_NOISE)]
        untracked = self.git_ok(c, "ls-files", "-z", "--others", "--exclude-standard").split("\0")
        untracked = [p for p in untracked if p]
        with open(os.path.join(out, "HEAD"), "w", encoding="utf-8") as f:
            f.write(self.git_ok(c, "rev-parse", "HEAD"))
        with open(os.path.join(out, "diff.patch"), "wb") as f:
            subprocess.run(["git", "-C", c, "diff", "--binary", "HEAD"], stdout=f, check=True, timeout=300)
        with open(os.path.join(out, "index.patch"), "wb") as f:   # staged content the working file no longer shows
            subprocess.run(["git", "-C", c, "diff", "--binary", "--cached", "HEAD"], stdout=f, check=True, timeout=300)
        with open(os.path.join(out, "real.patch"), "wb") as f:
            if real:
                subprocess.run(["git", "-C", c, "diff", "--binary", "HEAD", "--"] + real, stdout=f, check=True, timeout=300)
        for name, want in (("untracked.tar", untracked), ("ignored.tar", ignored),
                           ("real_untracked.tar", [p for p in untracked if not p.startswith(POOL_NOISE)])):
            if want:
                subprocess.run(["tar", "-C", c, "--null", "-T", "-", "-cf", os.path.join(out, name)],
                               input="\0".join(want).encode(), check=True, timeout=300)
        for i, sha in enumerate(stash):   # refs/stash names only the newest; the rest live in a reflog no bundle carries
            self.git_ok(c, "update-ref", "refs/rm-stash/%d" % i, sha)
        if commits or stash:
            r = self.git(c, "bundle", "create", os.path.join(out, "commits.bundle"), "HEAD", "--all", "--not", "--remotes")
            if r.returncode:
                raise RuntimeError("git bundle: %s" % r.stderr[-200:])
        return out

    def restore_bundle(self, item, bundle, c):
        """A fresh clone takes the WIP of the one evicted. What will not apply stays in the bundle and the record says so."""
        bad = []
        patch = os.path.join(bundle, "real.patch")
        if os.path.exists(patch) and os.path.getsize(patch):
            r = self.git(c, "apply", "--3way", "--whitespace=nowarn", patch, timeout=300)
            if r.returncode:
                bad.append("patch: %s" % r.stderr[-200:])
        index, whole = (os.path.join(bundle, x) for x in ("index.patch", "diff.patch"))
        if os.path.exists(index) and os.path.getsize(index):
            with open(index, "rb") as a, open(whole, "rb") as b:
                if a.read() != b.read():
                    bad.append("the index held content the working tree did not: see index.patch")
        for name in ("real_untracked.tar", "ignored.tar"):
            tar = os.path.join(bundle, name)
            if not os.path.exists(tar):
                continue
            listed = subprocess.run(["tar", "-tf", tar], capture_output=True, text=True, timeout=300)
            clash = [p for p in listed.stdout.splitlines() if os.path.isfile(os.path.join(c, p))]
            if clash:   # upstream has since tracked the name: never overwritten, and said
                bad.append("%s kept in the bundle, upstream has them: %s" % (name, ", ".join(clash[:5])))
            r = subprocess.run(["tar", "--skip-old-files", "-C", c, "-xf", tar], capture_output=True, text=True, timeout=300)
            if r.returncode:
                bad.append("%s: %s" % (name, r.stderr[-200:]))
        if bad:
            self.store.learn(item, "\n%s relentless: your clone was evicted from a full pool and its WIP did not all "
                             "come back; it is in %s (%s)\n" % (iso(time.time()), bundle, "; ".join(bad)))
        return bad

    def remove_clone(self, st, before=None):
        """Nothing leaves the pool unbundled. -> the bundle dir or None; a bundle that fails keeps the clone."""
        c = st.get("clone")
        if not c or not os.path.abspath(c).startswith(os.path.join(self.base, "clones") + os.sep):
            return None
        out = None
        if os.path.exists(os.path.join(c, ".git")):
            try:
                out = self.bundle_clone(st.get("item") or clone_item(c), c)
            except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as e:
                self.store.journal({"at": iso(time.time()), "do": "alarm", "kind": "bundle_failed", "clone": c, "why": str(e)[:300]})
                return None
        if before and out:
            before(out)         # the record learns of the bundle while the clone still stands
        try:
            shutil.rmtree(c)
        except OSError as e:   # still present, so still counted; the bundle stands
            self.store.journal({"at": iso(time.time()), "do": "alarm", "kind": "remove_failed", "clone": c, "why": str(e)[:300]})
        return out

    def conductor_alarm(self, text):
        """The line the Conductor reads first. -> None, or why it did not land."""
        path = (self.r.get("staffing") or {}).get("conductor_log")
        if not path:
            return "no conductor_log in the rules"
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write("\n%s — RELENTLESS JAM: %s\n  RAISE FIRST: relentless is stalled\n" % (iso(time.time()), text))
        except OSError as e:
            return str(e)[:200]
        return None

    def told(self, row):
        """One row of the told ledger (OP3), beside ops_watch's alarms.json. -> None, or why it did not land."""
        d = os.environ.get("RM_OPS_WATCH_DIR") or self.r["ops_watch_dir"]
        try:
            with open(os.path.join(d, "told.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps(row, sort_keys=True) + "\n")
        except OSError as e:
            return str(e)[:200]
        return None

    def alarm_signal(self, rec):
        """A journalled alarm joins the told ledger, each kind at most once in ALARM_TOLD_EVERY_S: step_raised can fire
        every tick. A failure stays on the journal and never stops the tick that alarmed."""
        import incident as IN
        path, now = self.store.p("alarm_told.json"), time.time()
        try:
            try:
                with open(path, encoding="utf-8") as f:
                    said = json.load(f)
            except (OSError, ValueError):
                said = {}
            if now - said.get(rec["kind"], -1e18) < ALARM_TOLD_EVERY_S:
                return
            d = os.environ.get("RM_OPS_WATCH_DIR") or self.r["ops_watch_dir"]
            if IN.signal({"incident": {"enabled": True}}, rec["kind"], rec.get("why"), now, os.path.join(d, "told.jsonl")):
                said[rec["kind"]] = now
                self.store._write(path, json.dumps(said))
        except Exception as e:  # noqa: BLE001
            self.store._append(self.store.p("journal.jsonl"), json.dumps({
                "at": iso(now), "do": "told_failed", "kind": rec["kind"], "why": "%s: %s" % (type(e).__name__, str(e)[:200])}))

    def check_path(self, st):
        """A new path per check: a quarantined checker may still be running in the last one."""
        return os.path.join(self.base, "clones", "check-%s-c%d" % (st["item"], (st.get("check_count") or 0) + 1))

    def old_checks(self, st):
        """This item's earlier check clones, less any an unreaped quarantined run is still in."""
        keep = {q.get("clone") for q in st["quarantined"] if not q.get("reaped")}
        got = glob.glob(os.path.join(self.base, "clones", "check-%s-c*" % st["item"]))
        return [d for d in got if d not in keep]

    def clean_checkout(self, st, sha):
        """A clean tree at exactly `sha`, for the checker. Tracked files only: no worker scratch leaks in."""
        d = self.check_path(st)
        for old in self.old_checks(st):
            shutil.rmtree(old, ignore_errors=True)
        return self._detached_clone(d, sha, "check", st["item"])

    def _detached_clone(self, d, sha, what, item):
        env = dict(os.environ, RM_SCRATCH_ROOT=os.path.dirname(os.path.dirname(d)), RM_SEAT="clones")
        r = subprocess.run(["python3", os.path.join(self.books, "src/RimMandrake/Utils/scratch_clone.py"), "clone",
                            "relentless %s %s" % (what, item), "--name", os.path.basename(d), "--checkout", "--fetch"],
                           cwd=self.books, env=env, capture_output=True, text=True, timeout=400,
                           stdin=subprocess.DEVNULL)
        if r.returncode:
            return None, "%s clone failed: %s" % ({"check": "checker"}.get(what, what), (r.stderr or r.stdout)[-300:])
        r = self.git(d, "checkout", "--quiet", "--detach", sha)
        return (d, None) if r.returncode == 0 else (None, "checkout %s: %s" % (sha, r.stderr[-200:]))

    def help_path(self, st):
        return os.path.join(self.base, "clones", "help-%s-c%d" % (st["item"], (st.get("help_count") or 0) + 1))

    def help_checkout(self, st, sha):
        """The consult's clean tree. Not the item's clone: its uncommitted work is the story being withheld."""
        d, why = self._detached_clone(self.help_path(st), sha, "help", st["item"])
        if d:
            self.git(d, "remote", "set-url", "--push", "origin", "read-only-consult")
        return d, why

    def published(self, sha):
        self.git(self.books, "fetch", "--quiet", "origin", "main")
        return self.git(self.books, "merge-base", "--is-ancestor", sha, "origin/main").returncode == 0

    def head(self):
        return self.git(self.books, "rev-parse", "origin/main").stdout.strip() or None

    def changed(self, base, sha, item):
        """Files of the final commit plus every commit since the item's base that names the item (the brief makes
        workers name it), so a hook change followed by a doc commit does not escape its live line."""
        r = self.git(self.books, "show", "--format=", "--name-only", sha)
        got = set(x for x in r.stdout.splitlines() if x.strip()) if r.returncode == 0 else set()
        if base:
            r = self.git(self.books, "log", "--format=", "--name-only", "--grep=" + item, "%s..%s" % (base, sha))
            got |= set(x for x in r.stdout.splitlines() if x.strip())
        return sorted(got)

    def commit_time(self, sha):
        r = self.git(self.books, "show", "-s", "--format=%ct", sha)
        return int(r.stdout.strip() or 0) if r.returncode == 0 else 0

    # the units
    def launch(self, st, run, prompt, agent, clone, max_s, extra_env, wall=()):
        """-> None, or why it did not start. The caller persisted `run` before this call. wall: systemd properties."""
        rl = self.RL
        role = {"name": "relentless", "seat": self.r["seat"], "clone": clone, "model": self.r["model"],
                "run_max_s": max_s}
        claude = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
        os.makedirs(os.path.dirname(run["out"]), exist_ok=True)
        argv = rl.launch_argv(role, run["unit"], prompt, run["out"], run["err"], claude)
        at = argv.index("--")
        env = []
        for k, v in extra_env.items():
            env += ["--setenv", "%s=%s" % (k, v)]
        argv = argv[:at] + list(wall) + env + argv[at:]
        o = argv.index("--output-format")
        argv[o:o] = ["--agent", agent]
        r = subprocess.run(argv, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        return ("systemd-run exit %d: %s" % (r.returncode, (r.stdout + r.stderr)[-200:])) if r.returncode else None

    def alive(self, run):
        """Unit, scope, or a marked process: any one of them means the run is not over."""
        if not run:
            return False
        rl = self.RL
        for u in (run.get("unit"), run.get("scope")):
            if u and rl.unit_state(u) in rl.ACTIVE:
                return True
        try:
            return bool(rl.scan_marked(run.get("marker"), since=run.get("at"))[0])
        except Exception:  # noqa: BLE001
            return False

    def stop(self, run, force):
        self.RL.stop(run["unit"], run.get("scope"), marker=run.get("marker"), force=force, seat=self.r["seat"])

    def tokens(self, run):
        if not run:
            return 0
        try:
            res = self.RL.read_result({"out": run.get("out"), "err": run.get("err")})
            return int(self.RL.run_tokens(res) or 0)
        except Exception:  # noqa: BLE001
            return 0

    def circling_tree(self, st, outputs=()):
        return circling.tree_reading(st["clone"], st.get("base") or "HEAD", POOL_NOISE, outputs)

    def transcripts(self, st):
        return circling.transcript_paths(st["clone"], st["started_at"])

    def activity(self, st):
        """Newest write in the item's transcripts: a worker in a long test is not silent, only its beat is."""
        slug = re.sub(r"[^A-Za-z0-9]", "-", st["clone"] or "")
        d = os.path.expanduser("~/.claude/projects/" + slug)
        best = 0
        try:
            for e in os.scandir(d):
                best = max(best, e.stat().st_mtime)
        except OSError:
            pass
        return best

    def mem_gb(self):
        with open("/proc/meminfo") as f:
            for ln in f:
                if ln.startswith("MemAvailable:"):
                    return int(ln.split()[1]) / 1048576.0
        return 0.0

    def paused(self):
        try:
            import dispatcher
            return bool(dispatcher.paused_now())
        except Exception:  # noqa: BLE001
            return False

    def live_check(self, line, not_before):
        import live_line
        return live_line.check(line, not_before=not_before)


def clone_item(c):
    """The item a pool clone's folder is named for: ITEM, ITEM.qN, check-ITEM-cN or help-ITEM-cN."""
    name = os.path.basename(c.rstrip("/"))
    for pre in ("check-", "help-"):
        if name.startswith(pre):
            return name[len(pre):].rsplit("-c", 1)[0]
    return re.sub(r"\.q\d+$", "", name)


def foreign_seat(r):
    return (r.get("staffing") or {}).get("foreign_seat")


def foreign_ok(it, r):
    """An item of the other seat a worker may take. Only `proposed`: its `next` offers only `ready`, so a head reaches a
    proposed item through `claim`, which the guard refuses from the reservation on. The classes it must not take are
    in the rules; design section 13 says why each."""
    cfg = r["staffing"]
    return (it.state == "proposed" and getattr(it, "kind", None) not in cfg.get("foreign_kinds_exclude", [])
            and not re.search(cfg.get("foreign_exclude") or "(?!)", "%s %s" % (it.id, it.title or ""), re.I))


def eligible(it, r):
    return (it.owner in r["pool_seats"] and it.state in ("proposed", "ready") and not it.blocked
            and it.needs != "owner" and it.needs in r["pool_needs"]
            and getattr(it, "kind", None) not in r.get("pool_kinds_exclude", [])
            and it.id not in r.get("pool_ids_exclude", []) and not getattr(it, "lease", None)
            and (it.owner != foreign_seat(r) or foreign_ok(it, r)))


# ---------------------------------------------------------------- prompts

def worker_prompt(st, text, learned, r):
    i, g = st["item"], st["gen"]
    rc = "python3 src/RimMandrake/rimflow/relentless.py"
    head = ["You carry one item until it is proven. You are one worker in a line: others came before you and another "
            "follows if you stop. Everything you know must be on disk.",
            "Item %s, generation %d, attempt %d, approach %s." % (i, g, st["attempts"], st["approach"]),
            "Your cwd is this item's own clone; uncommitted work from earlier workers is yours to continue.",
            "Report ONLY with these (a refusal with exit 3 means your lease is gone: stop at once, push nothing):",
            "  %s beat --item %s --gen %d" % (rc, i, g),
            "  %s learn --item %s --gen %d \"what you found, what failed, what to try next\"" % (rc, i, g),
            "  %s contract --item %s --gen %d --proof \"the command or look that proves it\" "
            "[--live \"<live line>\"] [--why ...]" % (rc, i, g),
            "  %s snag --item %s --gen %d --class <slug> \"what stopped you\"" % (rc, i, g),
            "  %s finish --item %s --gen %d --sha <published sha> --evidence \"<paths and results>\"" % (rc, i, g),
            "  %s help --item %s --gen %d \"what you need a fresh eye on\"" % (rc, i, g),
            "Set the contract BEFORE you edit, from the item's own words. A line of `learn` after every finding and "
            "at least every 20 minutes. Commit explicit paths and land with ./publish; every commit subject names the item id; `finish` names a sha on "
            "origin/main. Then a blind checker reruns your proof on that sha; it does not see your notes. Never run "
            "`rimflow close`, `implemented`, `release` or `claim` on this item: the supervisor owns its ledger state.",
            "A hook, systemd unit, dispatcher_schedule.json or ops_watch_rules.json change, or an OPS_ alarm item, needs --live with one of: "
            "`unit=rm-foo.timer reading=<path> max_age=6h`, `hook=block_foo.py`, `once: why`.",
            "Hit a wall? `snag` and exit: the item goes back to the top with your finding. Do not ask anyone. Only a "
            "true design/RimMandrake/delegation_policy.md section 2 call goes up: `snag --class owner_call --section "
            "<what, quoted> ...`. `help` sends a fresh agent the failed approaches on record (refused if there are "
            "none); its options land in the state file (`relentless.py show <item>`) and in the next worker's brief.",
            "Never live-test a flyer's flight. No worldgen. Foreground commands, timeouts under 540 s, no subagents, "
            "bulk output to files. FOUNDRY's tree and src/RimMandrake/Utils/arena/ are not yours to touch."]
    if st["approach"] == "redesign":
        head.append("REDESIGN: the same failure came back too often. Read the record below, write a DIFFERENT approach "
                    "with `learn` before you edit anything, and change the contract with --why if it was the problem.")
    if st["approach"] == "pilot":
        head.append("PILOT: this needs eyes on the running thing. Run `python3 src/RimMandrake/rimflow/cli.py pilot %s`, "
                    "follow that brief yourself, and report what you saw with `learn`." % i)
    if st["contract"]:
        head.append("Contract so far: %s" % json.dumps(st["contract"]))
    if st["last_fail"]:
        head.append("Last ending: %s: %s" % (st["last_fail"]["class"], st["last_fail"]["detail"]))
    if st.get("help_options"):
        head.append("FRESH EYES: an agent with no history read the failed approaches and offers these hypotheses. Pick "
                    "one, or refute each with evidence; record which with `learn` before you edit.")
        head += ["  %d. %s (confirm or kill by: %s)" % (n + 1, o["idea"], o["observe"])
                 for n, o in enumerate(st["help_options"]["options"])]
    return "\n".join(head + ["", "--- item ---", text, "", "--- learned so far ---", learned[-8000:]])


def help_prompt(st, text, tried, nonce, r):
    """Cold on purpose: the record of what ended and how, never learned.md, the story that drove the circling."""
    rc = "python3 src/RimMandrake/rimflow/relentless.py"
    most = r["circling"]["help_options_max"]
    rows = ["  gen %s ended %s: %s" % (a.get("gen"), a.get("end"), a.get("detail") or "") for a in tried[-12:]]
    return "\n".join([
        "You are a fresh pair of eyes. You have no history with this item and no stake in it. Workers tried, and the "
        "attempts below failed. Your cwd is a clean tree at origin/main. Read anything; change nothing: no edits, no "
        "push, no ledger.",
        "Give up to %d options the workers have not tried. Each is a hypothesis, never a verdict, and carries the "
        "single observation that would confirm or kill it." % most,
        "Then run this once and stop:",
        "  %s help-answer --item %s --nonce %s --option \"idea | the one observation\" [--option ...]" % (rc, st["item"], nonce),
        "", "Why you were called: %s" % st["help"]["why"], "Contract: %s" % json.dumps(st["contract"]),
        "", "--- failed approaches ---"] + rows + ["", "--- item ---", text])


def checker_prompt(st, text, nonce):
    i = st["item"]
    c = st["candidate"]
    rc = "python3 src/RimMandrake/rimflow/relentless.py"
    return "\n".join([
        "You are a blind checker. You did not do this work and you have no record of how it went. Your cwd is a clean "
        "tree at exactly commit %s." % c["sha"],
        "Decide one thing: did this commit do what the item says, proven by running it? Run the proof yourself. Judge "
        "the contract against the item's words: a contract that is easier than the item is a FAIL. A proof that "
        "cannot run is a FAIL. Do not fix anything, do not push, do not touch the ledger.",
        "Then run exactly one of:",
        "  %s verdict --item %s --nonce %s PASS \"what you ran and saw\"" % (rc, i, nonce),
        "  %s verdict --item %s --nonce %s FAIL \"what is wrong, so the next worker can fix it\"" % (rc, i, nonce),
        "", "Contract: %s" % json.dumps(st["contract"]), "Evidence the commit names: %s" % c["evidence"][:1500],
        "See the change with: git show %s" % c["sha"], "", "--- item ---", text])


# ---------------------------------------------------------------- the tick

def short(item):
    return hashlib.sha1(item.encode()).hexdigest()[:10]


def run_desc(store, r, unit, now):
    """A run's whole identity, known and persisted before the unit exists (role_launch.role_scope's name)."""
    d = os.path.join(store.dir, "runs", "roles")
    return {"unit": unit, "marker": unit, "at": now, "charged": None, "out": os.path.join(d, unit + ".json"),
            "err": os.path.join(d, unit + ".err"), "scope": "claude-seat-%s-%s.scope" % (r["seat"], unit)}


def unit_name(kind, item, gen):
    return "rm-relentless-%s-%s-g%d" % (kind, short(item), gen)


def stage_load(store):
    try:
        with open(store.p("staffing_state.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def stage_places(store, fx, r):
    """What the current stage allows and what the budget leaves. -> (stage value, budget, head helpers, places)."""
    cfg = r["staffing"]
    stages = cfg["stages"]
    v = stages[min(stage_load(store).get("stage", 0), len(stages) - 1)]
    low = min((x for x in stages if x != "budget"), default=1)
    budget, head = fx.budget(), fx.head_helpers()
    if budget is None:          # unreadable: the lowest stage at any stage, and the reading says so
        v = low
    elif v == "budget":
        v = budget
    room = v if budget is None else min(v, max(budget - (head or 0), 0))
    if head is None:            # helpers nobody counted are not free places
        room = min(room, low)
    return v, budget, head, min(room, places_ceiling(fx, r))


def places_ceiling(fx, r):
    """max_workers under the WIP cap (RO2). A budget caps workers, not open focus, so the same number binds here; a
    `held` item is relentless's wait and holds no place. `extra` in worker_cap stays on top: a check always runs."""
    focus = getattr(fx, "focus_cap", lambda: None)()
    return r["max_workers"] if focus is None else min(r["max_workers"], focus)


def worker_cap(fx, r, extra=0, store=None):
    """The places a run may take now: the stage and the budget under max_workers, stepped back to 1 while available
    memory is under step_back_mem_gb. `extra` is the place a check gets on top (a check runs even at budget 0: it holds
    a place already, and finishing work is never what a budget cut stops)."""
    cap = stage_places(store, fx, r)[3] if store is not None and r.get("staffing") else places_ceiling(fx, r)
    if cap > 1 and fx.mem_gb() < r.get("step_back_mem_gb", 0):
        cap = 1
    return cap + extra


def admission(store, fx, r, now, active, extra=0):
    """-> None when one more run may start, else why not."""
    br = load_breaker(store)
    if br.get("until", 0) > now + r["breaker_cool_max_s"]:      # set under a higher cap: the rule binds what is on disk
        br["until"] = now + r["breaker_cool_max_s"]
        store._write(store.p("breaker.json"), json.dumps(br))
    if br.get("until", 0) > now:        # the cause, not only the state: the alarm quotes this line
        return "breaker open until %s: %s" % (iso(br["until"]), (br.get("why") or "no cause recorded").strip()[:200])
    if active >= worker_cap(fx, r, extra, store):
        return "max_workers"
    if fx.paused():
        return "paused"
    if fx.mem_gb() < r["min_mem_available_gb"]:
        return "memory"
    if spent_today(store, now) + (active + 1 + unreaped(store)) * r["run_reserve"] > r["day_spend_limit"]:
        return "day_spend_limit"
    return None


def load_breaker(store):
    try:
        with open(store.p("breaker.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def cause_key(why):
    """Same fault, same key: run names, paths and numbers differ between tries, the words do not. The tail, because
    launch and clone errors arrive cut to their last 200-300 characters, so their first words shift with a name's length."""
    return re.sub(r"\s+", " ", CAUSE_TOKEN.sub("#", why)).strip().lower()[-120:]


def launch_failed(store, r, now, why):
    """The launcher failed. A refusal is not that: the launch path is healthy and something else said no, so it charges
    nothing here, at any call site. `opens` counts by cause and outlives launch_ok: a flap between two opens is still one fault."""
    if any(w in why for w in r["breaker_refusal_words"]):
        return
    br = load_breaker(store)
    was_open = br.get("until", 0) > now
    br["fails"] = br.get("fails", 0) + 1
    if br["fails"] >= r["launch_breaker"]:
        n = br["fails"] - r["launch_breaker"]
        br["until"] = now + min(r["breaker_cool_s"] * (2 ** n), r["breaker_cool_max_s"])
        if not was_open:            # a second failure of the same tick extends this open, it is not another one
            c = br.setdefault("opens", {}).setdefault(cause_key(why), {"n": 0})
            c.update(n=c["n"] + 1, last=now, why=why[:300])
    br["why"] = why[:300]
    store._write(store.p("breaker.json"), json.dumps(br))


def launch_ok(store):
    br = load_breaker(store)
    if br.get("fails") or br.get("until"):
        store._write(store.p("breaker.json"), json.dumps({"opens": br["opens"]} if br.get("opens") else {}))


def breaker_emergency(store, fx, r, now, acts):
    """The same cause opened the breaker `breaker_same_cause_opens` times inside the window: one incident, told once on
    each road, a road that failed retried next tick. A cause silent for the window is forgotten and may be told again.
    Outside launch_failed because that runs under the lock and this blocks."""
    br = load_breaker(store)
    opens = {k: c for k, c in br.get("opens", {}).items() if now - c["last"] < r["breaker_same_cause_window_s"]}
    changed = len(opens) != len(br.get("opens", {}))
    item = (r.get("staffing") or {}).get("alarm_item")
    for key, c in opens.items():
        if c["n"] < r["breaker_same_cause_opens"]:
            continue
        said = c.setdefault("said", [])
        text = "EMERGENCY: the breaker opened %d times on the same cause: %s" % (c["n"], c["why"][:200])
        row = {"class": "emergency", "cause": "relentless.breaker:" + key, "metric": "relentless.breaker_same_cause",
               "reader": r["breaker_reader"], "told_at": iso(now), "ack_due": iso(now + r["breaker_ack_min"] * 60),
               "recover_by": None, "item": item, "opens": c["n"], "why": c["why"]}
        roads = [("told", lambda: fx.told(row)), ("conductor", lambda: fx.conductor_alarm(text))]
        if item:
            roads.append(("item", lambda: fx.staffing_alarm(item, text)))
        for name, road in roads:
            if name in said:
                continue
            fail = road()
            if fail:
                acts.append({"do": "alarm_retry", "why": "%s: %s" % (name, fail)})
            else:
                said.append(name)
                changed = True
                acts.append({"do": "breaker_emergency", "road": name, "cause": key})
                store.journal({"at": iso(now), "do": "alarm", "kind": "breaker_emergency", "road": name, "why": c["why"]})
    if changed:
        br["opens"] = opens
        store._write(store.p("breaker.json"), json.dumps(br))


def pool_rows(store, fx, r):
    """Every pool clone and who holds it. -> [{clone, item, kind, state, rank}], rank 0 dead, 1 parked, 2 live.
    Dead: its item ended, a check that is not running, or nobody's and idle. Parked: nothing runs in it, a later run may
    want it (a fresh clone serves as well, with the bundle). Live: never touched."""
    own = {}
    for st in store.states():
        if st.get("clone"):
            own[os.path.abspath(st["clone"])] = ("work", st)
        if (st.get("check") or {}).get("clone"):
            own[os.path.abspath(st["check"]["clone"])] = ("check", st)
        if (st.get("help") or {}).get("clone"):
            own[os.path.abspath(st["help"]["clone"])] = ("help", st)
    for st in store.states():
        for q in st["quarantined"]:
            if q.get("clone") and not q.get("reaped"):
                own[os.path.abspath(q["clone"])] = ("quarantine", st)
    rows = []
    for c in fx.pool_clones():
        kind, st = own.get(os.path.abspath(c), (None, None))
        status = st["status"] if st else None
        if st is None:
            rank = 0 if fx.clone_idle_s(c) >= POOL_ORPHAN_IDLE_S else 2
        elif kind == "quarantine" or (run_of(st, "run" if kind == "work" else kind) or {"charged": 0}).get("charged") is None:
            rank = 2
        elif kind == "help":
            rank = 2 if help_pending(st) else 0
        elif status in ENDED:
            rank = 0
        elif kind == "check":
            rank = 0 if status in ("queued", "held", "candidate") else 2
        else:
            rank = 1 if status in ("queued", "held", "candidate") else 2
        rows.append({"clone": c, "item": st["item"] if st else clone_item(c), "kind": kind, "status": status, "rank": rank})
    return rows


def evict(store, fx, row, now, acts, why, before=None):
    bundle = fx.remove_clone({"clone": row["clone"], "item": row["item"]}, before)
    gone = not fx.clone_present(row["clone"])
    if gone:
        store.journal({"at": iso(now), "do": "clone_released", "clone": os.path.basename(row["clone"]), "why": why, "bundle": bundle})
        acts.append({"do": "clone_released", "clone": os.path.basename(row["clone"]), "why": why})
    return gone, bundle


def reclaim_dead(store, fx, r, now, acts):
    """A dead run gives its clone back on the next tick, whichever road it ended by."""
    for row in pool_rows(store, fx, r):
        if row["rank"] == 0 and not fx.clone_busy(row["clone"]):
            evict(store, fx, row, now, acts, "dead: %s %s" % (row["kind"] or "nobody's", row["status"] or ""))


def bundle_pointer(store, row, carry):
    """Records the bundle on the item, so its next clone restores it."""
    def point(bundle):
        if carry:
            with store.lock():
                cur = store.load(row["item"])
                cur["bundle"] = bundle
                store.save(cur)
    return point


def release_parked(store, fx, r, now, acts):
    """A parked item's idle clone goes back before scratch_clone's idle hour calls it stranded: FLYER_STABLE_BODY_GATE_1 and
    SEAT_MEMORY_STANDARD_FALLBACK_1 sat held on the owner with real WIP until disk.pool_breach fired, because only pool
    pressure ever moved them. WIP travels in the bundle; commits stay, no fresh clone can restore them, and the alarm is right."""
    for row in pool_rows(store, fx, r):
        if row["rank"] != 1 or fx.clone_busy(row["clone"]) or fx.clone_idle_s(row["clone"]) < r["pool_parked_release_s"]:
            continue
        wip = fx.clone_wip(row["clone"])
        if not wip["kept"]:
            evict(store, fx, row, now, acts, "parked: %s %s" % (row["kind"], row["status"]),
                  bundle_pointer(store, row, wip["real"] and row["kind"] == "work"))


def make_room(store, fx, r, now, acts, reserve=0):
    """Room for one more clone, or the hold that names who has the pool. Parked clones go first with nothing of theirs
    at risk, then those whose WIP a bundle carries; commits and stashes stay, and a live clone is never touched.
    `reserve`: places a builder may not take, so a finished item can always get its check."""
    n, size, cmax, bmax = fx.pool_load()
    reserve = min(reserve, cmax - 1)   # a pool of one still has to take a builder
    if n < cmax - reserve and size < bmax:
        return None
    rows, order = pool_rows(store, fx, r), {"candidate": 0, "held": 1, "queued": 2}
    parked = []
    for row in rows:
        if row["rank"] == 2 or fx.clone_busy(row["clone"]):
            row["hold"] = "live"
            continue
        wip = fx.clone_wip(row["clone"])
        if wip["kept"] and row["rank"]:
            row["hold"] = "commits"
            continue
        parked.append((row["rank"], bool(wip["real"]), order.get(row["status"], 0), row, wip))
    for rank, real, _o, row, wip in sorted(parked, key=lambda p: p[:3]):
        gone, _b = evict(store, fx, row, now, acts, "for room: %s %s" % (row["kind"] or "nobody's", row["status"] or ""),
                         bundle_pointer(store, row, real and row["kind"] == "work" and rank))
        if not gone:
            row["hold"] = "bundle failed"
            continue
        n, size, cmax, bmax = fx.pool_load()
        if n < cmax - reserve and size < bmax:
            return None
    held = ", ".join("%s (%s)" % (clone_item(x["clone"]), x.get("hold") or x["status"]) for x in rows if fx.clone_present(x["clone"]))
    if size >= bmax:
        return "pool at %.1f GB, cap %.0f GB, nothing to release: %s" % (size / 1e9, bmax / 1e9, held)
    return "pool full: %d clones, cap %d%s, nothing to release: %s" % (
        n, cmax, " (%d kept for checks)" % reserve if reserve else "", held)


def enrol(store, fx, r, now):
    """Top up to ceil(share x pool). Store-only: an enrolled item stays open to the seats until a lease is taken."""
    states = store.states()
    live = [s for s in states if s["status"] in OPEN]
    share = float(r["share"])
    if share <= 0:
        return []
    order, _ = fx.pool_order(r)
    ours = {s["item"] for s in states}
    pool = len(order) + sum(1 for s in live if s["item"] not in order)
    target = math.ceil(share * pool)
    queued = sum(1 for s in live if in_line(s))
    want = target - len(live)
    if r.get("staffing"):       # the filler: a free place is reason enough, whatever the share says of the backlog
        want = max(want, worker_cap(fx, r, 0, store) - sum(1 for s in live if s["status"] in HOLDS_A_PLACE) - queued)
    room = min(want, r["enrol_per_tick"], r["max_queued"] - queued)
    took = []
    plan = getattr(fx, "plan", None) or {}      # a listed item never waits for room: the list holds under 30 (DI3)
    for i in order:
        if room <= 0 and i not in plan:
            break
        if i in ours:
            continue
        with store.lock():
            if store.load(i) is None:
                st = new_state(i, now, "share %.2f of %d" % (share, pool))
                st["pilot_wanted"] = i in getattr(fx, "bounce", ())
                store.save(st)
                store.journal({"at": iso(now), "do": "enrol", "item": i})
                took.append(i)
                room -= 1
    return took


def ledger_has(item):
    """The caller's own ledger, published or not: a typed id that names nothing never enters the line. Unreadable: yes."""
    try:
        return any(e.get("id") == item for e in pkg("model").read())
    except Exception:  # noqa: BLE001
        return True


def concept_refused(repo, item, kind):
    """The Concept gate, shut when it cannot read: None for anything that is not a mod and cites no tree."""
    tree = pkg("concept_tree")
    return tree.relentless_refusal(repo, item, kind, tree.item_file_text(repo, item))


def enrol_one(store, item, why, now):
    """A person's or the Conductor's pick. It queues in enrol order like any other and takes no lease by itself."""
    with store.lock():
        st = store.load(item)
        if st is None:
            st = new_state(item, now, why)
            store.save(st)
            store.journal({"at": iso(now), "do": "enrol", "item": item, "why": why})
        return st


def reenrol(store, item, why, now):
    """Back in line after `retired`, which is otherwise for good: a named verb, journalled, for a retirement that was
    wrong. A fresh start with the old spend: `gen` moves on, so a run of the old life stays fenced, and `check_count`
    stays, so a new checker never lands in the path a quarantined one may still be running in."""
    if not (why or "").strip():
        raise ValueError("reenrol: --why is required")
    with store.lock():
        old = store.load(item)
        if not old or old["status"] != "retired":
            raise ValueError("%s is %s, only a retired item can be re-enrolled" % (
                item, old["status"] if old else "not enrolled"))
        st = new_state(item, now, why)
        st.update(gen=old["gen"] + 1, spent=old.get("spent", 0), quarantined=old.get("quarantined", []),
                  attempts=old.get("attempts", 0), check_count=old.get("check_count", 0))
        store.save(st)
        store.journal({"at": iso(now), "do": "reenrol", "item": item, "why": why})
        return st


def run_of(st, key):
    return st.get("run") if key == "run" else (st.get(key) or {}).get("run")


def settle(store, fx, r, item, key, since, now, acts):
    """Bring one run to its end: stop it, force it, at last quarantine it (the reaper goes on trying and charges it).
    True when the run is over as far as the item is concerned. Blocking calls are outside the lock."""
    st = store.load(item)
    run = run_of(st, key)
    if not run or run.get("charged") is not None:
        return True
    age = now - (since or now)
    if fx.alive(run):
        if age < r["stop_quarantine_s"]:
            fx.stop(run, force=age >= r["stop_force_s"])
            return False
        with store.lock():
            cur = store.load(item)
            live = run_of(cur, key)
            cur["quarantined"].append({"run": dict(live), "at": now,
                                       "clone": cur["clone"] if key == "run" else (cur[key] or {}).get("clone"),
                                       "reaped": False})
            live["charged"] = 0
            if key == "run":
                cur["clone"] = None           # the next worker gets a new clone, from what was pushed
            store.journal({"at": iso(now), "do": "alarm", "kind": "quarantine", "item": item,
                           "why": "unit %s would not die" % run["unit"]})
            store.save(cur)
        fx.ledger_note(item, "relentless: unit %s would not die, quarantined; carrying on" % run["unit"])
        acts.append({"do": "quarantine", "item": item, "unit": run["unit"]})
        return True
    tok = fx.tokens(run)
    with store.lock():
        cur = store.load(item)
        live = run_of(cur, key)
        if live and live.get("charged") is None:
            live["charged"] = charge(store, cur, tok, now, r, live["unit"])
            live["measured"] = tok
            store.save(cur)
    return True


def reap_quarantined(store, fx, r, now, acts):
    for st in store.states():
        for i, q in enumerate(st["quarantined"]):
            if q.get("reaped"):
                continue
            if fx.alive(q["run"]):
                fx.stop(q["run"], force=True)
                continue
            tok = fx.tokens(q["run"])
            with store.lock():
                cur = store.load(st["item"])
                if not cur["quarantined"][i].get("reaped"):
                    cur["quarantined"][i]["reaped"] = True
                    charge(store, cur, tok, now, r, q["run"]["unit"])
                    store.save(cur)
            fx.remove_clone({"clone": q.get("clone")})
            acts.append({"do": "reaped", "item": st["item"], "unit": q["run"]["unit"]})


def unreaped(store):
    return sum(1 for s in store.states() for q in s["quarantined"] if not q.get("reaped"))


def overdue(st, activity, now, r):
    """-> (class, why) when a live worker has run out of time or gone silent. Pure."""
    if now - st["started_at"] >= r["run_max_s"]:
        return "worker_full", "hit run_max_s"
    seen = max(st["started_at"] + r["launch_grace_s"], st["last_beat"] or 0, activity)
    if now - seen >= r["stale_s"]:
        return "worker_stale", "silent for %d s" % (now - seen)
    return None


def step(store, fx, r, item, now, acts):
    """One item, one transition. Crash anywhere and the next tick resumes from the persisted status."""
    st = store.load(item)
    s = st["status"]
    if s == "queued" and st.get("needs_back"):
        if not fx.ledger_needs(item, "offline", "relentless: the owner lifted the hold"):
            with store.lock():
                st = store.load(item)
                st["needs_back"] = False
                store.save(st)
    if s in ENDED or s == "queued":
        return

    if s == "retiring":
        since = st["stopping_since"]
        if settle(store, fx, r, item, "run", since, now, acts) and settle(store, fx, r, item, "check", since, now, acts):
            with store.lock():
                st = store.load(item)
                st["status"] = "retired"
                store.save(st)
            fx.remove_clone(st)
            acts.append({"do": "retired", "item": item})
        return

    if s == "held":
        h = st["hold"]
        if not h.get("delivered") and not fx.ledger_needs_owner(item, h["why"]):
            with store.lock():
                st = store.load(item)
                if st["hold"]:
                    st["hold"]["delivered"] = True
                    store.save(st)
            acts.append({"do": "held_delivered", "item": item})
        return

    if s == "stopping":
        if not settle(store, fx, r, item, "run", st["stopping_since"], now, acts):
            return
        with store.lock():
            st = store.load(item)
            if st["status"] != "stopping":
                return
            st["run"] = None
            st["status"] = "held" if st["hold"] else "queued"
            store.save(st)
        acts.append({"do": "returned", "item": item, "to": st["status"]})
        return

    if s == "running" and st.get("reserving"):
        # a crash between the reservation and the launch: the item goes back to the line, its ledger as it stands
        with store.lock():
            st = store.load(item)
            st.pop("reserving", None)
            st["status"] = "queued"
            store.save(st)
        acts.append({"do": "reservation_returned", "item": item})
        return

    if s == "running":
        rec = store.read_receipt(item, st["gen"])
        if rec:         # a crash between the receipt and the status: the receipt wins
            with store.lock():
                st = store.load(item)
                if st["status"] == "running":
                    _take_receipt(store, st, rec, now)
            return
        run = st.get("run")
        if fx.alive(run):
            act = fx.activity(st)
            if overdue(st, act, now, r):
                with store.lock():
                    st = store.load(item)
                    late = overdue(st, act, now, r) if st["status"] == "running" else None
                    rec = store.read_receipt(item, st["gen"]) if late else None
                    if rec:
                        _take_receipt(store, st, rec, now)
                        return
                    if late:
                        fail(store, st, late[0], late[1], r, now)
                if late:
                    fx.stop(run, force=False)
                    acts.append({"do": late[0], "item": item})
            return
        if not settle(store, fx, r, item, "run", st["started_at"], now, acts):
            return
        with store.lock():
            st = store.load(item)
            if st["status"] != "running":
                return
            rec = store.read_receipt(item, st["gen"])   # finish may have landed while the unit went down
            if rec:
                _take_receipt(store, st, rec, now)
                return
            tok = (st.get("run") or {}).get("measured")
            if not tok and not st["last_beat"] and now - st["started_at"] < r["launch_grace_s"]:
                # dead at once, nothing spent: auth or quota, not the item's fault. Its place is kept
                st["gen"] += 1
                st["status"] = "queued"
                st["returned_at"] = st["returned_at"] or now
                st["run"] = None
                store.attempt(item, {"at": iso(now), "gen": st["gen"] - 1, "end": "launch_fail"})
                store.save(st)
                launch_failed(store, r, now, "%s died at once with no usage" % (run or {}).get("unit"))
                acts.append({"do": "launch_fail", "item": item})
                return
            launch_ok(store)
            fail(store, st, "worker_lost", "unit %s ended with no receipt" % (run or {}).get("unit"), r, now)
        acts.append({"do": "worker_lost", "item": item})
        return

    if s == "candidate":
        c = st["candidate"]
        why = None
        if not fx.published(c["sha"]):
            why = "%s is not on origin/main" % c["sha"]
        else:
            import live_line
            paths = fx.changed(st.get("base"), c["sha"], item)
            if not paths:
                why = "%s changes nothing" % c["sha"]
            elif (live_line.needs_line(paths) or item.startswith(ALARM_PREFIXES)) and not (st["contract"] or {}).get("live"):
                why = "%s needs a live line in the contract: %s" % (c["sha"], (live_line.needs_line(paths) or ["alarm item"])[0])
        if why:
            with store.lock():
                st = store.load(item)
                if st["status"] == "candidate":
                    fail(store, st, "bad_candidate", why, r, now)
            acts.append({"do": "bad_candidate", "item": item})
            return
        # the finishing worker leaves first: nothing of its survives into the check
        if not settle(store, fx, r, item, "run", c["at"], now, acts):
            return
        # checks get a place, and a waiting candidate runs nothing: counted, two would wait on each other for good
        active = sum(1 for x in store.states() if x["status"] in HOLDS_A_PLACE and x["status"] != "candidate")
        hold = admission(store, fx, r, now, active, extra=1)
        if not hold and r.get("staffing") and clones_this_tick(acts) >= r["staffing"]["launch_per_tick"]:
            hold = "clones per tick"
        hold = hold or ("memory after its last clone" if now < st.get("clone_again_at", 0) else None)
        hold = hold or make_room(store, fx, r, now, acts)
        if hold:
            acts.append({"do": "check_waits", "item": item, "why": hold})
            return
        acts.append({"do": "clone_try"})
        clean, why = fx.clean_checkout(st, c["sha"])
        if why:
            if POOL_REFUSED not in why:     # a full pool is a wait: the launch path is fine, the engine must not back off
                launch_failed(store, r, now, why)
            acts.append({"do": "check_waits", "item": item, "why": "pool full: " + why if POOL_REFUSED in why else why})
            return
        gb = fx.mem_gb()
        acts.append({"do": "mem_after_clone", "gb": gb})
        if gb < r["min_mem_available_gb"]:      # the clone itself costs gigabytes; admission saw the host before it
            fx.remove_clone({"clone": clean})
            with store.lock():                  # others go first: the same clone every tick would starve them
                st = store.load(item)           # make_room may have written this record since it was read
                st["clone_again_at"] = now + 600
                store.save(st)
            acts.append({"do": "check_waits", "item": item, "why": "memory after the clone"})
            return
        nonce = hashlib.sha256(os.urandom(16)).hexdigest()[:24]
        n = (st.get("check_count") or 0) + 1
        unit = unit_name("check", item, st["gen"]) + "-c%d" % n
        desc = run_desc(store, r, unit, now)
        box = None
        if relentless_wall.enforced(r):
            box = relentless_wall.make_box(relentless_wall.profile(r), clean, c["sha"], nonce)
        with store.lock():              # the whole identity is on disk before the unit exists
            st = store.load(item)
            st["status"] = "checking"
            st["check_count"] = n
            st["check"] = {"nonce": nonce, "unit": unit, "at": now, "clone": clean, "run": desc}
            if box:
                st["check"]["box"] = box
            store.save(st)
        if box:
            why = fx.launch(st, desc, relentless_wall.marker_prompt(st, fx.item_text(item), box), r["checker_agent"],
                            os.path.join(box, "tree"), r["check_max_s"], {},
                            relentless_wall.props(relentless_wall.profile(r), box, [store.root]))
        else:
            why = fx.launch(st, desc, checker_prompt(st, fx.item_text(item), nonce), r["checker_agent"], clean,
                            r["check_max_s"], {"RELENTLESS_ROOT": store.root})
        with store.lock():
            st = store.load(item)
            if why:
                st["status"] = "candidate"
                st["check"] = None
                launch_failed(store, r, now, why)
            store.save(st)
        acts.append({"do": "check_started" if not why else "check_launch_failed", "item": item})
        return

    if s == "checking":
        chk = st["check"]
        got = relentless_wall.read_verdict(chk["box"]) if chk.get("box") and not chk.get("expired") else None
        if got and chk.get("verdict") is None:      # the box is the walled Marker's way out: the nonce is the store's own
            verdict(store, item, chk["nonce"], got["word"], got["reasons"], now)
            chk = store.load(item)["check"]
        word = chk.get("verdict")
        if word is None and fx.alive(chk.get("run")) and now - chk["at"] < r["check_max_s"] + r["launch_grace_s"]:
            return
        if word is None and not chk.get("expired"):    # fence the nonce before the stop: late is no verdict
            with store.lock():
                cur = store.load(item)
                if cur["status"] == "checking":
                    cur["check"]["expired"] = cur["check"].get("verdict") is None
                    store.save(cur)
        since = chk.get("verdict_at") or chk["at"] + r["check_max_s"] + r["launch_grace_s"]
        if not settle(store, fx, r, item, "check", min(since, now), now, acts):
            return
        c = st["candidate"]
        with store.lock():
            st = store.load(item)
            if st["status"] != "checking":
                return
            word = st["check"].get("verdict")
            if word is None:
                n = st.get("check_lost", 0) + 1
                st["check_lost"] = n
                if n >= r["same_failure_limit"]:
                    st["check_lost"] = 0
                    fail(store, st, "checker_lost", "%d checkers gave no verdict" % n, r, now)
                else:
                    st["status"] = "candidate"
                    st["check"] = None
                    store.save(st)
                acts.append({"do": "checker_lost", "item": item})
                return
            if word == "FAIL":
                fail(store, st, "blind_fail", st["check"].get("reasons"), r, now)
                acts.append({"do": "blind_fail", "item": item})
                return
        live = (st["contract"] or {}).get("live")
        broken = fx.live_check(live, fx.commit_time(c["sha"])) if live else None
        if not broken and not fx.published(c["sha"]):
            broken = "%s left origin/main" % c["sha"]
        with store.lock():
            st = store.load(item)
            if st["status"] != "checking":
                return
            if broken:
                fail(store, st, "live_broken", broken, r, now)
                acts.append({"do": "live_broken", "item": item})
                return
            st["status"] = "closing"
            store.save(st)
        s = "closing"

    if s == "closing":
        st = store.load(item)
        c = st["candidate"]
        if st.get("tomb_since"):
            # closed on the ledger; `closing` stays the guard's word until the other seat's stale tree shows it gone
            if fx.seat_heard(item, iso(st["started_at"])) or now - st["tomb_since"] >= r["staffing"]["tomb_max_s"]:
                finished(store, fx, item, c, now, acts)
            return
        reason = "relentless: blind PASS at %s after %d return(s): %s" % (c["sha"], st["returns"],
                                                                         (st["check"].get("reasons") or "")[:220])
        why = fx.ledger_close(item, c["sha"], reason, (st["contract"] or {}).get("live"))
        if why and "has not earned its close" in why:    # a refusal is no transient: a retry would refuse for ever
            with store.lock():
                st = store.load(item)
                fail(store, st, "close_refused", why, r, now)
            acts.append({"do": "close_refused", "item": item, "why": why})
            return
        if why:
            acts.append({"do": "close_retry", "item": item, "why": why})
            return
        if st.get("foreign"):
            with store.lock():
                st = store.load(item)
                st["tomb_since"] = now
                store.attempt(item, {"at": iso(now), "end": "done", "sha": c["sha"]})
                store.save(st)
            fx.remove_clone(st)
            fx.remove_clone({"clone": (st.get("check") or {}).get("clone")})
            acts.append({"do": "closed_waiting_for_seat", "item": item})
            return
        finished(store, fx, item, c, now, acts, attempt=True)


def help_over(store, fx, item, word, now, acts):
    """One consult done with, however. Under no lock on entry; removes its clone unless a quarantined run still sits in it."""
    with store.lock():
        st = store.load(item)
        h = st["help"]
        h["status"] = word
        keep = any(q.get("clone") == h.get("clone") and not q.get("reaped") for q in st["quarantined"])
        store.attempt(item, {"at": iso(now), "gen": st["gen"], "help": word})
        store.save(st)
    if h.get("clone") and not keep:
        fx.remove_clone({"clone": h["clone"], "item": item})
    if word == "failed":
        fx.ledger_note(item, "relentless: a consult gave no options (%s); the item carries on without" % h.get("end", "no answer"))
    acts.append({"do": "help_" + word, "item": item})


def help_retry(store, fx, item, why, r, now, acts):
    """No options from this try. Another, or the item carries on: a consult never holds a worker back for good."""
    with store.lock():
        st = store.load(item)
        h = st["help"]
        h["end"] = why[:200]
        again = h["tries"] < r["circling"]["help_launch_tries"]
        if again:
            h.update(status="wanted", run=None, nonce=None, clone=None)
        store.save(st)
    if again:
        acts.append({"do": "help_retry", "item": item, "why": why[:200]})
    else:
        help_over(store, fx, item, "failed", now, acts)


def help_start(store, fx, r, item, now, acts):
    """Launch the fresh agent. The shape of the check's launch: a place, room, a clean clone, identity on disk first."""
    st = store.load(item)
    h = st["help"]
    if now - h["at"] >= r["circling"]["help_wait_s"]:
        h_end = "no room in %d s" % (now - h["at"])
        with store.lock():
            cur = store.load(item)
            cur["help"]["end"] = h_end
            store.save(cur)
        help_over(store, fx, item, "failed", now, acts)
        return
    active = sum(1 for x in store.states() if x["status"] in HOLDS_A_PLACE and x["status"] != "candidate") + helps_running(store)
    hold = admission(store, fx, r, now, active, extra=1)
    if not hold and r.get("staffing") and clones_this_tick(acts) >= r["staffing"]["launch_per_tick"]:
        hold = "clones per tick"
    hold = hold or ("memory after its last clone" if now < st.get("clone_again_at", 0) else None)
    hold = hold or make_room(store, fx, r, now, acts)
    if hold:
        acts.append({"do": "help_waits", "item": item, "why": hold})
        return
    acts.append({"do": "clone_try"})
    sha = fx.head()
    clean, why = fx.help_checkout(st, sha) if sha else (None, "origin/main not read")
    if why:
        if POOL_REFUSED not in why:
            launch_failed(store, r, now, why)
        acts.append({"do": "help_waits", "item": item, "why": "pool full: " + why if POOL_REFUSED in why else why})
        return
    gb = fx.mem_gb()
    acts.append({"do": "mem_after_clone", "gb": gb})
    if gb < r["min_mem_available_gb"]:
        fx.remove_clone({"clone": clean, "item": item})
        with store.lock():
            st = store.load(item)
            st["clone_again_at"] = now + 600
            store.save(st)
        acts.append({"do": "help_waits", "item": item, "why": "memory after the clone"})
        return
    nonce = hashlib.sha256(os.urandom(16)).hexdigest()[:24]
    n = (st.get("help_count") or 0) + 1
    desc = run_desc(store, r, unit_name("help", item, st["gen"]) + "-h%d" % n, now)
    with store.lock():              # the whole identity is on disk before the unit exists
        st = store.load(item)
        st["help_count"] = n
        h = st["help"]
        h.update(status="running", nonce=nonce, clone=clean, run=desc, started_at=now, tries=h["tries"] + 1)
        store.save(st)
    tried = failed_approaches(store, item)
    why = fx.launch(st, desc, help_prompt(st, fx.item_text(item), tried, nonce, r), r["help_agent"], clean,
                    r["circling"]["help_max_s"], {"RELENTLESS_ROOT": store.root})
    if why:
        fx.remove_clone({"clone": clean, "item": item})
        launch_failed(store, r, now, why)
        help_retry(store, fx, item, why, r, now, acts)
        return
    acts.append({"do": "help_started", "item": item, "unit": desc["unit"]})


def help_step(store, fx, r, item, now, acts):
    """One item's consult, beside its run and independent of it. Pure lifecycle: the worker's status only ends it."""
    st = store.load(item)
    if not st or not r.get("circling"):
        return
    gone = st["status"] in ENDED or st["status"] == "retiring"
    if not help_pending(st):
        if gone:
            return
        with store.lock():
            cur = store.load(item)
            if not force_help(store, cur, r, now):      # one held back by the cool, now over
                return
            store.save(cur)
        st = cur
    h = st["help"]
    if h["status"] == "wanted":
        if gone:
            help_over(store, fx, item, "dropped", now, acts)
        else:
            help_start(store, fx, r, item, now, acts)
        return
    limit = h["started_at"] + r["circling"]["help_max_s"]
    answered = h.get("answered_at")
    if not gone and not answered and fx.alive(h.get("run")) and now < limit:
        return
    if not answered and not h.get("expired"):       # fence the nonce before the stop: late is no answer
        with store.lock():
            cur = store.load(item)
            cur["help"]["expired"] = cur["help"].get("answered_at") is None
            store.save(cur)
    if not settle(store, fx, r, item, "help", min(answered or limit, now), now, acts):
        return
    cur = store.load(item)
    if cur["help"].get("answered_at"):
        help_over(store, fx, item, "answered", now, acts)
    elif gone:
        help_over(store, fx, item, "dropped", now, acts)
    else:
        with store.lock():      # the next try is a new consult: its nonce must not read as expired
            cur = store.load(item)
            cur["help"]["expired"] = False
            store.save(cur)
        if not any(q.get("clone") == h.get("clone") for q in cur["quarantined"]):
            fx.remove_clone({"clone": h.get("clone"), "item": item})
        help_retry(store, fx, item, "no answer", r, now, acts)


def helps_running(store):
    return sum(1 for x in store.states() if (x.get("help") or {}).get("status") == "running")


def finished(store, fx, item, c, now, acts, attempt=False):
    with store.lock():
        st = store.load(item)
        st["status"] = "done"
        st["done_at"] = now
        if attempt:
            store.attempt(item, {"at": iso(now), "end": "done", "sha": c["sha"]})
        store.save(st)
    fx.remove_clone(st)
    fx.remove_clone({"clone": (st.get("check") or {}).get("clone")})
    store.journal({"at": iso(now), "do": "done", "item": item, "sha": c["sha"], "returns": st["returns"]})
    acts.append({"do": "done", "item": item})


def in_line(st):
    """Queued and able to start: an item the books have not heard of holds no place, or unpublished work stops enrolment."""
    return st["status"] == "queued" and not st.get("awaiting_ledger")


def retire(store, fx, states, now, acts, r=None):
    """The ledger closed an item from outside (his drop, a supersede): fence first, then step() drains the runs."""
    for st in states:
        if st["status"] not in OPEN or st["status"] in ("closing", "retiring"):
            continue
        led = fx.item_state(st["item"])
        if st.get("awaiting_ledger") and led is not None:       # published: it takes its place in the count again
            with store.lock():
                cur = store.load(st["item"])
                cur["awaiting_ledger"] = False
                store.save(cur)
        if r and st["status"] == "queued" and st["item"] in r.get("pool_ids_exclude", []):
            # started means the ledger says doing with no one on it: hand it back or it reads as worked on for good.
            # Back first: `retired` is never looked at again, so a refused hand-back must come round next tick.
            ours = st["ledger_started"] and led and led["state"] == "doing" and led.get("owner") == r.get("seat")
            why = fx.ledger_reclaim(st["item"]) if ours else None    # a reassigned item was handed back already
            if why:
                acts.append({"do": "retire_waits", "item": st["item"], "why": why})
                continue
            with store.lock():
                cur = store.load(st["item"])
                cur["status"] = "retired"
                store.save(cur)
            acts.append({"do": "retire", "item": st["item"], "why": "excluded in the rules"})
        elif led is None and st["status"] == "queued" and not st["ledger_started"]:
            # filed but not published yet: the books have not heard of it, and that is no close (five items ended
            # this way, 2026-11-01). It waits in line; the launch skips it until the ledger names it.
            if not st.get("awaiting_ledger"):
                with store.lock():
                    cur = store.load(st["item"])
                    cur["awaiting_ledger"] = True
                    store.save(cur)
                    store.journal({"at": iso(now), "do": "awaiting_ledger", "item": st["item"]})
                acts.append({"do": "awaiting_ledger", "item": st["item"]})
        elif led is None or led["state"] in ("done", "dropped", "superseded"):
            with store.lock():
                cur = store.load(st["item"])
                cur["gen"] += 1
                cur["status"] = "retiring"
                cur["stopping_since"] = now
                store.save(cur)
            acts.append({"do": "retire", "item": st["item"]})
        elif not st["ledger_started"] and st["status"] == "queued" and (
                led["state"] not in ("proposed", "ready") or led.get("lease")) and (
                not st.get("start_intent") or led.get("lease")):
            with store.lock():
                cur = store.load(st["item"])
                cur["status"] = "retired"           # a seat took it first; it was never ours
                store.save(cur)
            acts.append({"do": "retire", "item": st["item"], "why": "a seat took it"})


def spend_holds(store, fx, r, now, acts):
    for st in store.states():
        limit = r["item_spend_limit"] + (st.get("spent_grace") or 0)
        owed = sum(1 for q in st["quarantined"] if not q.get("reaped")) * r["run_reserve"]   # charged when reaped
        if st["status"] == "queued" and st["spent"] + owed >= limit:
            with store.lock():
                cur = store.load(st["item"])
                cur["status"] = "held"
                cur["hold"] = {"why": "item spend limit: %d of %d weighted tokens. Lift with relentless.py unhold"
                               % (cur["spent"] + owed, limit), "kind": "spend", "delivered": False, "at": now}
                store.save(cur)
            acts.append({"do": "hold_spend", "item": st["item"]})


def clones_this_tick(acts):
    """A clone blocks the tick for minutes, builders' and checkers' alike, and the tick has a timeout."""
    return sum(1 for a in acts if a.get("do") == "clone_try")


def give_back(store, item, why, to="retired"):
    """`retired`: the other seat's after all, never ours. `queued`: the ledger already says ours, so it must stay in
    the line: retired, nothing would ever pick it up again."""
    with store.lock():
        cur = store.load(item)
        cur.pop("reserving", None)
        cur["status"] = to
        store.save(cur)
    store.journal({"at": iso(time.time()), "do": "give_back", "item": item, "why": why})


def reserve_foreign(store, fx, r, item, now, acts):
    """Take an item of the other seat without pulling its tree. Its old code reads `running` as leased, so from the
    write below its own claim, start and close are refused; then wait out a claim that passed the guard just before,
    look at what its tree has not published, and only then move the item. -> True when it is ours."""
    cfg = r["staffing"]
    with store.lock():
        cur = store.load(item)
        if cur["status"] != "queued":
            return False
        cur["status"] = "running"
        cur["reserving"] = now
        cur["started_at"] = now
        cur["run"] = None
        cur["foreign"] = True
        store.save(cur)
    fx.settle_wait(cfg["settle_s"])
    words = fx.seat_words()
    theirs = (fx.item_state(item) or {}).get("owner") == foreign_seat(r)
    if words is None or item in words:
        why = "its tree is unreadable" if words is None else "its seat has an unpublished word on it"
        # a crash or a failed launch brings it back here already handed over: retired, it would strand as ours
        # and a word on it waits too: once published the ledger says what it was, and `retire` or the line acts on that
        give_back(store, item, why, "retired" if theirs and words is not None else "queued")
        acts.append({"do": "give_back", "item": item, "why": why})
        return False
    why = fx.ledger_take(item) if theirs else None
    if why:     # often a passing failure, and `retired` is for good: only a take that keeps failing ends the item here
        with store.lock():
            cur = store.load(item)
            cur["take_fails"] = fails = cur.get("take_fails", 0) + 1
            store.save(cur)
        give_back(store, item, why, "retired" if fails >= 3 else "queued")
        acts.append({"do": "give_back", "item": item, "why": why})
        return False
    return True


def lease(store, fx, r, now, acts):
    """Fill the free places, top of the queue first. An item the machine cannot run now keeps its place."""
    cfg = r.get("staffing") or {}
    launched = clones_this_tick(acts)
    if float(r["share"]) <= 0:      # the off switch: nothing new starts, what runs finishes
        acts.append({"do": "wait", "why": "share 0"})
        return
    if cfg:
        waiting = sum(1 for x in store.states() if x["status"] == "candidate")
        if waiting > cfg["check_backlog_max"]:          # more builders would only lengthen the line at the checkers
            acts.append({"do": "wait", "why": "check_backlog"})
            return
    for st in queue_order(store.states(), getattr(fx, "plan", None)):
        if not st["ledger_started"] and fx.item_state(st["item"]) is None:     # not published yet: see retire()
            continue
        if st.get("not_before", 0) > now:
            continue
        if help_pending(st):        # the next brief is the point of the consult; help_step bounds this wait
            continue
        if cfg and launched >= cfg["launch_per_tick"]:   # prepare() blocks and the tick has a timeout
            return
        # a stopping item holds its place: its slot is not free for a fresh item while it returns to the top
        active = sum(1 for x in store.states() if x["status"] in HOLDS_A_PLACE) + helps_running(store)
        why = admission(store, fx, r, now, active)
        if not why and not fx.clone_present(st["clone"] or fx.clone_path(st["item"], len(st["quarantined"]))):
            why = make_room(store, fx, r, now, acts, r.get("pool_check_reserve", 0))
        if why:
            acts.append({"do": "wait", "why": why})
            return
        item = st["item"]
        refusal = getattr(fx, "concept_refusal", lambda _item: None)(item)
        if refusal:     # enrolled by hand, or its tree went stale in the line: it keeps its place, no worker starts
            acts.append({"do": "concept_refused", "item": item, "why": refusal})
            continue
        if st.get("needs_back"):       # the ledger still says owner: the next step() clears it first
            continue
        if item in r.get("pool_ids_exclude", []):   # back from a stop this tick: retire() takes it on the next
            continue
        if now < st.get("start_again_at", 0):
            continue
        reserved = False
        theirs = cfg and (fx.item_state(item) or {}).get("owner") == foreign_seat(r)
        if cfg and (theirs or st.get("foreign")):
            # also on the way back in line: the guard does not cover `queued`, so its seat may have reached it
            if theirs and not fx.foreign_fits(item):
                give_back(store, item, "no longer a kind of item the filler may take")
                acts.append({"do": "give_back", "item": item})
                continue
            reserved = reserve_foreign(store, fx, r, item, now, acts)
            if not reserved:
                continue
        if not st["ledger_started"]:
            with store.lock():      # said before the ledger hears it: a crash after `start` must not read as a seat's take
                cur = store.load(item)
                if cur["status"] != ("running" if reserved else "queued"):
                    continue
                cur["start_intent"] = True
                store.save(cur)
            why = fx.ledger_start(item)
            if why:
                if reserved:        # handed over, so it stays in line
                    give_back(store, item, "start refused", "queued")
                with store.lock():  # a ledger refusal is this item's, not the launcher's: it waits, the belt does not
                    cur = store.load(item)
                    cur["start_again_at"] = now + r["breaker_cool_s"]
                    store.save(cur)
                acts.append({"do": "start_refused", "item": item, "why": why})
                continue
        with store.lock():
            st = store.load(item)
            if st["status"] != ("running" if reserved else "queued"):
                continue
            st.pop("reserving", None)
            st["gen"] += 1
            st["attempts"] += 1
            st["ledger_started"] = True
            if not st["clone"]:
                q = len(st["quarantined"])
                st["clone"] = fx.clone_path(item, q)
            st["status"] = "running"
            st["started_at"] = now
            st["last_beat"] = None
            st["base"] = st.get("base") or fx.head()
            st["run"] = run_desc(store, r, unit_name("work", item, st["gen"]), now)
            store.save(st)
        acts.append({"do": "clone_try"})
        why = fx.prepare(st)
        if not why:
            gb = fx.mem_gb()
            acts.append({"do": "mem_after_clone", "gb": gb})
            if gb < r["min_mem_available_gb"]:      # the clone itself costs gigabytes
                why = "memory %.1f GB after the clone" % gb
        if not why:
            prompt = worker_prompt(st, fx.item_text(item), store.learned(item), r)
            agent = r["pilot_agent"] if st["approach"] == "pilot" else r["worker_agent"]
            why = fx.launch(st, st["run"], prompt, agent, st["clone"], r["run_max_s"],
                            {"RELENTLESS_ROOT": store.root, "RELENTLESS_GEN": str(st["gen"])})
        with store.lock():
            cur = store.load(item)
            if why:
                cur["gen"] += 1
                cur["status"] = "queued"
                cur["returned_at"] = cur["returned_at"] or now
                cur["run"] = None
                store.attempt(item, {"at": iso(now), "gen": cur["gen"] - 1, "end": "launch_fail", "detail": why[:300]})
                store.save(cur)
                if POOL_REFUSED not in why:
                    launch_failed(store, r, now, why)
                acts.append({"do": "launch_fail", "item": item, "why": "pool full: " + why if POOL_REFUSED in why else why})
                return
            store.attempt(item, {"at": iso(now), "gen": cur["gen"], "start": cur["run"]["unit"],
                                 "approach": cur["approach"]})
            store.save(cur)
        launched += 1
        acts.append({"do": "lease", "item": item, "gen": st["gen"], "unit": st["run"]["unit"]})


def reading(store, r, now, acts):
    states = store.states()
    counts = {}
    for s in states:
        counts[s["status"]] = counts.get(s["status"], 0) + 1
    br = load_breaker(store)
    rec = {"at": iso(now), "share": r["share"], "counts": counts, "spent_today": spent_today(store, now),
           "breaker": br or None, "acts": acts[-20:], "circling": circling.summary(store, r, now),
           "items": [{"item": s["item"], "status": s["status"], "gen": s["gen"], "returns": s["returns"],
                      "approach": s["approach"], "spent": s["spent"]} for s in states if s["status"] in OPEN]}
    store._write(store.p("reading.json"), json.dumps(rec, indent=1, sort_keys=True))
    return rec


NO_ALARM = ("paused", "budget 0", "share 0")


def clean_window(store, s, fx, r, now):
    """-> None when the current stage has earned the next, else what it still lacks. The stage's own window only."""
    cfg = r["staffing"]
    since = iso(s["stage_since"])
    ends = []
    for st in store.states():
        got = [a for a in store.attempts(st["item"])
               if a.get("end") in ("done", "blind_fail") and str(a.get("at", "")) > since]
        ends += [a["end"] for a in got if a["end"] == "blind_fail"]
        # a crash in closing can write the same `done` twice; one sha is one pass
        ends += ["done"] * len({a.get("sha") for a in got if a["end"] == "done"})
    bad = ends.count("blind_fail")
    if s.get("full_s", 0) < cfg["hold_s"]:
        return "held full for %d of %d s" % (s.get("full_s", 0), cfg["hold_s"])
    if len(ends) < cfg["min_verdicts"]:
        return "%d of %d verdicts" % (len(ends), cfg["min_verdicts"])
    if bad / len(ends) > cfg["max_reject_share"]:
        return "rejected %d of %d" % (bad, len(ends))
    if s["mem_min"] < r["step_back_mem_gb"]:
        return "memory touched %.1f GB" % s["mem_min"]
    if fx.budget() is None:
        return "budget unreadable"
    if fx.head_helpers() is None:
        return "head helpers unmeasured"
    if fx.oom_kills() is None:
        return "OOM count unreadable"
    b = fx.burn()
    if b is None:
        return "burn unmeasured"
    if b > cfg["burn_max_pct_h"]:
        return "burn %.2f%%/h" % b
    return None


def staffing(store, fx, r, now, acts):
    """The no-AI filler's reading: budget, running, ready, minutes under; the staged rise; the one alarm."""
    cfg = r["staffing"]
    s = stage_load(store)
    if "stage_since" not in s:
        s = {"stage": 0, "stage_since": now, "full_s": 0, "mem_min": fx.mem_gb(), "oom": fx.oom_kills()}
    states = store.states()
    v, budget, head, room = stage_places(store, fx, r)
    k = sum(1 for x in states if x["status"] in HOLDS_A_PLACE)
    live = sum(1 for x in states if x["status"] in ("running", "checking"))
    target = worker_cap(fx, r, 0, store)
    order, _ = fx.pool_order(r)
    ours = {x["item"] for x in states}
    queued = sum(1 for x in states if in_line(x))
    ready = queued + sum(1 for i in order if i not in ours)
    stepped = 0 < target < room
    why = stuck = None
    if float(r["share"]) <= 0:
        why = "share 0"
    elif budget == 0:
        why = "budget 0"
    else:
        # whatever else stops a run, the places aside; a clone the pool cannot give stops it as surely
        stuck = next((a["why"] for a in acts if str(a.get("why", "")).startswith(POOL_FULL)), None) or admission(
            store, fx, r, now, k, extra=k + 1)   # pool first: a breaker flapping over it must not reset the jam's clock
        why = stuck
        if why is None and stepped:
            why = "memory step-back"
        elif why is None and head and room < v:
            why = "head helpers"
        elif why is None and head is None and room < v:
            why = "head helpers unmeasured"
    words_read = not foreign_seat(r) or fx.seat_words() is not None
    under = k < min(target, k + ready)
    if not words_read and k < target:       # taking fails closed; the reading must not show the pool as simply empty
        under, why = True, why or "the other seat's tree is unreadable"
    if stuck and any(x["status"] == "candidate" for x in states):   # a place held by a check that cannot start
        under = True
    dt = min(max(now - s.get("at", now), 0), cfg["tick_gap_max_s"])
    s["at"] = now
    if under:
        s["under_since"] = s.get("under_since") or now
        if why is None:
            last = [a["why"] for a in acts if a.get("do") == "wait"]
            why = last[-1] if last else "filling"
        if why not in NO_ALARM:             # minutes watched, so a stopped timer or a pause is not read as under
            s["under_s"] = s.get("under_s", 0) + dt
    else:
        s.pop("under_since", None)
        s.pop("under_s", None)
        s.pop("alarmed", None)
    minutes = round(s.get("under_s", 0) / 60.0, 1) if under else 0
    alarm_fail = None
    if under and minutes >= cfg["alarm_after_min"] and not s.get("alarmed") and why not in NO_ALARM:
        fail = fx.staffing_alarm(cfg["alarm_item"], "Under-staffed %.0f min: running %d of %d (budget %s), %d ready, "
                                 "why: %s" % (minutes, k, target, budget, ready, why))
        if fail:
            alarm_fail = fail
            acts.append({"do": "alarm_retry", "why": fail})
        else:
            s["alarmed"] = True
            store.journal({"at": iso(now), "do": "alarm", "kind": "understaffed", "minutes": minutes, "why": why})
            acts.append({"do": "alarm", "item": cfg["alarm_item"]})
    # a jam: nothing runs, or the pool refuses, while work waits. Named within minutes, in the log the Conductor reads
    pool_why = next((a["why"] for a in acts if str(a.get("why", "")).startswith(POOL_FULL)), None)
    why_jam = why if pool_why is None else pool_why
    if pool_why or (under and why not in NO_ALARM and live == 0):
        s["jam_since"] = s.get("jam_since") or now
        if now - s["jam_since"] >= cfg["jam_alarm_s"] and not s.get("jam_said"):
            fail = fx.conductor_alarm("%d live of %d wanted, %d checks waiting, %d ready, stalled %.0f min: %s" % (
                live, target, sum(1 for x in states if x["status"] == "candidate"), ready, (now - s["jam_since"]) / 60.0, why_jam))
            if fail:
                alarm_fail = fail
                acts.append({"do": "alarm_retry", "why": fail})
            else:
                s["jam_said"] = True
                store.journal({"at": iso(now), "do": "alarm", "kind": "jam", "why": why_jam})
                acts.append({"do": "jam_alarm", "why": why_jam})
    else:
        s.pop("jam_since", None)
        s.pop("jam_said", None)
    # the staged rise: each step only after a clean reading. An OOM kill anywhere on the host steps one back down
    s["mem_min"] = min([s["mem_min"], fx.mem_gb()] + [a["gb"] for a in acts if a.get("do") == "mem_after_clone"])
    if s["mem_min"] < r["step_back_mem_gb"]:        # a dip restarts the clean window; it does not end it for good
        s.update(stage_since=now, full_s=0, mem_min=fx.mem_gb(), was_full=False)
    full = k >= v and live > 0
    if full and s.get("was_full"):          # both ends full: a gap is not credited to workers launched just now
        s["full_s"] = s.get("full_s", 0) + dt
    s["was_full"] = full
    oom, top = fx.oom_kills(), len(cfg["stages"]) - 1
    moved = None
    if oom is not None and s.get("oom") is not None and oom > s["oom"]:
        moved, s["stage"] = "down: OOM kill", max(s["stage"] - 1, 0)
    elif oom is not None and s.get("oom") is None:
        moved = "restart: OOM count readable again, what it missed is unknown"
    if oom is not None:
        s["oom"] = oom
    lack = None
    if not moved and s["stage"] < top:
        lack = clean_window(store, s, fx, r, now)
        if lack is None:
            moved, s["stage"] = "up: clean reading", s["stage"] + 1
    if moved:
        s.update(stage_since=now, full_s=0, mem_min=fx.mem_gb())
        store.journal({"at": iso(now), "do": "stage", "stage": s["stage"], "why": moved})
        acts.append({"do": "stage", "stage": s["stage"], "why": moved})
    store._write(store.p("staffing_state.json"), json.dumps(s))
    cand = [x for x in states if x["status"] == "candidate"]
    rec = {"at": iso(now), "t": now, "budget": budget, "budget_measured": budget is not None, "head_helpers": head,
           "stage": cfg["stages"][s["stage"]], "target": target, "running": live, "places": k, "live": live, "ready": ready,
           "under": under, "foreign_tree_read": words_read, "alarm_fail": alarm_fail,
           "minutes_under": minutes, "why": why, "alarmed": bool(s.get("alarmed")), "rise_lacks": lack,
           "spent_today": spent_today(store, now), "day_spend_limit": r["day_spend_limit"],
           "checks": {"waiting": len(cand), "running": sum(1 for x in states if x["status"] == "checking"),
                      "oldest_wait_s": round(now - min((x.get("candidate") or {}).get("at", now) for x in cand)) if cand else 0}}
    store._write(store.p("staffing.json"), json.dumps(rec, indent=1, sort_keys=True))
    with open(store.p("staffing.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def books_alarm(store, fx, stale, now, acts, r):
    """Frozen books are a frozen engine however green its readings look: said once, and said to the Conductor."""
    path = store.p("books_stale.json")
    try:
        with open(path, encoding="utf-8") as f:
            was = json.load(f)
    except (OSError, ValueError):       # absent, or torn by a killed tick: a new count, never a dead supervisor
        was = None
    if not stale:
        if os.path.exists(path):
            os.remove(path)
        return
    was = was or {"since": now}
    acts.append({"do": "books_stale", "why": stale})
    if now - was["since"] >= ((r.get("staffing") or {}).get("jam_alarm_s") or 300) and not was.get("said"):
        was["said"] = not fx.conductor_alarm("the engine is not deploying, a push does nothing: %s" % stale)
        store.journal({"at": iso(now), "do": "alarm", "kind": "books_stale", "why": stale})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(was, f)


def tick(store=None, fx=None, r=None, now=None):
    r = r or rules()
    store = store or Store()
    now = time.time() if now is None else now
    os.makedirs(store.dir, exist_ok=True)
    with open(store.p("tick.lock"), "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return [{"do": "skip", "why": "a tick is running"}]
        if fx is None:
            fx = Effects(r, store)
            store.on_alarm = fx.alarm_signal
        acts = []
        if not r.get("enabled"):
            reading(store, r, now, [{"do": "disabled"}])
            return acts
        books_alarm(store, fx, fx.sync(), now, acts, r)
        retire(store, fx, store.states(), now, acts, r)
        reclaim_dead(store, fx, r, now, acts)
        release_parked(store, fx, r, now, acts)
        for final in (False, True):       # the second pass lets a return that ended this tick reach the top now
            for item in store.items():
                if final and (store.load(item) or {}).get("status") != "stopping":
                    continue
                try:
                    step(store, fx, r, item, now, acts)
                except Exception as e:  # noqa: BLE001  one bad item never stops the others; next tick resumes it
                    acts.append({"do": "error", "item": item, "why": "%s: %s" % (type(e).__name__, e)})
                    store.journal({"at": iso(now), "do": "alarm", "kind": "step_raised", "item": item,
                                   "why": str(e)[:300]})
        for item in store.items():
            try:
                help_step(store, fx, r, item, now, acts)
            except Exception as e:  # noqa: BLE001  a consult is an extra: it never costs the tick its workers
                acts.append({"do": "error", "item": item, "why": "help %s: %s" % (type(e).__name__, e)})
                store.journal({"at": iso(now), "do": "alarm", "kind": "help_raised", "item": item, "why": str(e)[:300]})
        try:
            circling.watch(store, fx, r, now, acts, fail)
        except Exception as e:  # noqa: BLE001  the watch never stops the belt
            acts.append({"do": "error", "item": None, "why": "circling %s: %s" % (type(e).__name__, e)})
        reap_quarantined(store, fx, r, now, acts)
        spend_holds(store, fx, r, now, acts)
        enrol_acts = enrol(store, fx, r, now)
        acts += [{"do": "enrol", "item": i} for i in enrol_acts]
        try:
            lease(store, fx, r, now, acts)
        except Exception as e:  # noqa: BLE001  a hung rimflow must not lose the tick's flush; a reservation resumes next tick
            acts.append({"do": "error", "item": None, "why": "lease %s: %s" % (type(e).__name__, e)})
            store.journal({"at": iso(now), "do": "alarm", "kind": "lease_raised", "why": str(e)[:300]})
        try:
            breaker_emergency(store, fx, r, now, acts)
        except Exception as e:  # noqa: BLE001  a torn cause record must not lose the tick's flush
            acts.append({"do": "error", "item": None, "why": "breaker_emergency %s: %s" % (type(e).__name__, e)})
        if r.get("staffing"):
            try:
                staffing(store, fx, r, now, acts)
            except Exception as e:  # noqa: BLE001  the reading never stops the workers; a dead reading shows as stale
                acts.append({"do": "error", "item": None, "why": "staffing %s: %s" % (type(e).__name__, e)})
        why = fx.flush()
        if why:
            acts.append({"do": "flush_retry", "why": why})
        reading(store, r, now, acts)
        if acts:
            store.journal({"at": iso(now), "do": "tick", "acts": acts})
        return acts


def stats(store, fx=None):
    done = [s for s in store.states() if s["status"] == "done"]
    days = {}
    for s in done:
        d = day_key(s["done_at"])
        days[d] = days.get(d, 0) + 1
    rows = [{"day": d, "relentless_closed": n} for d, n in sorted(days.items())]
    return {"done": len(done), "by_day": rows, "mean_returns": (sum(s["returns"] for s in done) / len(done)) if done
            else None, "spent": sum(s["spent"] for s in done)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("tick")
    sub.add_parser("reading")
    sub.add_parser("stats")
    sub.add_parser("fence-hook")
    p = sub.add_parser("show")
    p.add_argument("item")
    for name in ("beat", "learn", "contract", "snag", "finish"):
        p = sub.add_parser(name)
        p.add_argument("--item", required=True)
        p.add_argument("--gen", required=True, type=int)
        if name in ("learn", "snag"):
            p.add_argument("text")
        if name == "contract":
            p.add_argument("--proof", required=True)
            p.add_argument("--live")
            p.add_argument("--why")
        if name == "snag":
            p.add_argument("--class", dest="klass", required=True)
            p.add_argument("--section")
            p.add_argument("--wait-hours", type=float, default=0, help="time, not work: no worker before then (at most %g)" % MAX_WAIT_HOURS)
        if name == "finish":
            p.add_argument("--sha", required=True)
            p.add_argument("--evidence", required=True)
    p = sub.add_parser("help", help="send a fresh agent the failed approaches; its options reach the next brief")
    p.add_argument("--item", required=True)
    p.add_argument("--gen", type=int, help="your lease; default RELENTLESS_GEN, set at launch")
    p.add_argument("text", nargs="?", default="")
    p = sub.add_parser("help-answer", help="the consult's return")
    p.add_argument("--item", required=True)
    p.add_argument("--nonce", required=True)
    p.add_argument("--option", action="append", required=True, help="idea | the one observation that confirms or kills it")
    sub.add_parser("wall", help="report only: what the Marker's wall would deny, from the checks' tool calls")
    p = sub.add_parser("trust")
    p.add_argument("--set", default="E1")
    p = sub.add_parser("verdict")
    p.add_argument("--item", required=True)
    p.add_argument("--nonce", required=True)
    p.add_argument("word")
    p.add_argument("reasons")
    p = sub.add_parser("enrol", help="carry one named item, ahead of the share's next picks")
    p.add_argument("--item", required=True)
    p.add_argument("--why", required=True)
    p = sub.add_parser("reenrol", help="put a retired item back in line; journals why")
    p.add_argument("--item", required=True)
    p.add_argument("--why", required=True)
    p = sub.add_parser("unhold")
    p.add_argument("item")
    p.add_argument("--owner-said")
    p.add_argument("--per-ruling", help="with --why: a Conductor instruction (conductor_authority.RULING)")
    p.add_argument("--why")
    a = ap.parse_args(argv)
    store = Store()
    try:
        if a.cmd == "tick":
            print(json.dumps(tick(store)))
        elif a.cmd == "reading":
            print(open(store.p("reading.json"), encoding="utf-8").read())
        elif a.cmd == "stats":
            print(json.dumps(stats(store), indent=1))
        elif a.cmd == "show":
            print(json.dumps(store.load(a.item), indent=1))
        elif a.cmd == "fence-hook":
            top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
            why = hook_fence(top, store)
            if why:
                print("RELENTLESS_FENCE: %s" % why, file=sys.stderr)
                return 1
        elif a.cmd == "beat":
            beat(store, a.item, a.gen)
        elif a.cmd == "learn":
            learn(store, a.item, a.gen, a.text)
        elif a.cmd == "contract":
            contract(store, a.item, a.gen, a.proof, a.live, a.why)
        elif a.cmd == "snag":
            snag(store, a.item, a.gen, a.klass, a.text, rules(), a.section, wait_hours=a.wait_hours)
        elif a.cmd == "finish":
            finish(store, a.item, a.gen, a.sha, a.evidence)
        elif a.cmd == "help":
            env_gen = os.environ.get("RELENTLESS_GEN")
            gen = a.gen if a.gen is not None else int(env_gen) if env_gen else None
            ask_help(store, a.item, gen, a.text, rules())
        elif a.cmd == "help-answer":
            help_answer(store, a.item, a.nonce, a.option, rules())
        elif a.cmd == "enrol":
            if not ledger_has(a.item):
                print("relentless: REFUSED: %s has never been filed" % a.item, file=sys.stderr)
                return 2
            filed = [e.get("kind") for e in pkg("model").read() if e.get("id") == a.item and e.get("event") == "file"]
            refusal = concept_refused(pkg("concept_tree").REPO, a.item, filed[-1] if filed else None)
            if refusal:
                print("relentless: REFUSED: %s" % refusal, file=sys.stderr)
                return 2
            st = enrol_one(Store(), a.item, a.why, time.time())
            print("%s %s" % (a.item, st["status"]))
        elif a.cmd == "reenrol":
            st = reenrol(Store(), a.item, a.why, time.time())
            print("%s %s gen %d" % (a.item, st["status"], st["gen"]))
        elif a.cmd == "wall":
            import relentless_seeds

            def session(run):
                try:
                    with open((run or {}).get("out") or "", encoding="utf-8") as f:
                        return json.load(f).get("session_id")
                except (OSError, ValueError):
                    return None
            print(json.dumps(relentless_wall.audit(store, rules(), session, relentless_seeds.tool_inputs), indent=1))
        elif a.cmd == "trust":
            import relentless_trust
            print(relentless_trust.report(store, set_name=a.set)[1], end="")
        elif a.cmd == "verdict":
            verdict(store, a.item, a.nonce, a.word, a.reasons)
        elif a.cmd == "unhold":
            said = _conductor_authority().words(a.owner_said, a.per_ruling, a.why)
            if not said:
                raise ValueError("unhold needs --owner-said or " + _conductor_authority().ROUTE)
            unhold(store, a.item, said)
    except Fenced as e:
        print("FENCED: %s" % e, file=sys.stderr)
        return FENCED
    except ValueError as e:
        print("refused: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    sys.exit(main())
