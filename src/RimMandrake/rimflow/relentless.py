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

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.join(HERE, "relentless_rules.json")
ALARM_PREFIXES = ("OPS_", "LIVE_RESTORE_")       # rimflow close refuses these without a live line (cli._live_gate)
DEFAULT_ROOT = "/home/mandrake/rm/relentless"
FENCED = 3
LEASED = ("running", "stopping", "candidate", "checking", "closing", "retiring")   # a worker or the supervisor owns the item
OPEN = ("queued",) + LEASED + ("held",)
HOLDS_A_PLACE = ("running", "checking", "candidate", "stopping", "retiring")    # a run that may be live counts
ENDED = ("done", "retired")
SHARD = "infrastructure/state/ledger/events/%s.jsonl"
NOTE_MAX = 400
NOT_READ = object()
ALLOCATION_FRESH_S = 1800
SLUG_RX = re.compile(r"[^a-z0-9_]+")
GUARDED_VERBS = ("close", "implemented", "renew", "release", "reclaim", "claim", "start")


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

class Store:
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


def queue_order(states):
    """Returned items first, oldest return first, then fresh in enrol order. Pure."""
    q = [s for s in states if s["status"] == "queued"]
    return sorted(q, key=lambda s: (0, s["returned_at"], s["item"]) if s["returned_at"] is not None
                  else (1, s["enrolled_at"], s["item"]))


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


def snag(store, item, gen, klass, detail, r, section=None, now=None):
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
        self.git(self.books, "pull", "--ff-only", "--quiet")
        self._ledger = None
        self._budget = self._helpers = NOT_READ

    def flush(self):
        """Publish the shard: retried each tick until it lands, so a close never stays local."""
        shards = [SHARD % self.r["seat"], SHARD % "RUNNER"]     # RUNNER: the alarm's `live` line
        got = self.git(self.books, "status", "--porcelain", "--", *shards).stdout.strip()
        ahead = self.git(self.books, "rev-list", "--count", "origin/main..HEAD").stdout.strip()
        if not got and ahead in ("0", ""):
            return None
        dirty = [x for x in shards if x in got]
        a = ["./publish"] + (["-m", "ledger: relentless supervisor", *dirty] if dirty else [])
        r = subprocess.run(a, cwd=self.books, capture_output=True, text=True, timeout=90, stdin=subprocess.DEVNULL)
        return None if r.returncode == 0 else "publish exit %d: %s" % (r.returncode, (r.stderr or r.stdout)[-300:])

    def ledger_items(self):
        if self._ledger is None:
            model = pkg("model")
            evs = model.read()
            self._ledger = (evs, model.replay(evs))
        return self._ledger

    def pool_order(self, r):
        """Open items in the pool, best first: raised, then Test Pilot bouncers, then rank()."""
        priority, testpilot_route, model = pkg("priority"), pkg("testpilot_route"), pkg("model")
        evs, w = self.ledger_items()
        bounce = self.bounce = {v["id"] for v in testpilot_route.routed(w, evs)}
        targets = r.get("pool_targets") or ["v1"]
        # not priority.rank(): `next` offers only what a seat already took up, and the pool is the proposed backlog.
        # The same sort, so raised work and the campaign rows still go first
        words = self.seat_words()
        pool = [it for it in w.items.values() if eligible(it, r) and it.target in (None, *targets)
                and (it.owner != foreign_seat(r) or (words is not None and it.id not in words))]
        pool.sort(key=lambda i: (i.id not in bounce, model.raise_key(i), not i.this_deployment, priority._row_key(i),
                                 i.created_at or "", i.id))
        return [i.id for i in pool], w

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
        r = self.rimflow("close", item, "--sha", sha, "--reason", reason, "--why", "relentless: blind check passed",
                         *(("--live", live) if live else ()))     # the sweep keeps checking what the contract promised
        if r.returncode == 0:
            return None
        return None if self.closed(item) else (r.stderr or r.stdout)[-400:]

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
        with open(os.path.join(c, ".git", "relentless.json"), "w", encoding="utf-8") as f:
            json.dump({"item": st["item"], "gen": st["gen"]}, f)
        return None

    def remove_clone(self, st):
        c = st.get("clone")
        if c and os.path.abspath(c).startswith(os.path.join(self.base, "clones") + os.sep):
            shutil.rmtree(c, ignore_errors=True)

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
        env = dict(os.environ, RM_SCRATCH_ROOT=os.path.dirname(os.path.dirname(d)), RM_SEAT="clones")
        r = subprocess.run(["python3", os.path.join(self.books, "src/RimMandrake/Utils/scratch_clone.py"), "clone",
                            "relentless check " + st["item"], "--name", os.path.basename(d), "--checkout", "--fetch"],
                           cwd=self.books, env=env, capture_output=True, text=True, timeout=400,
                           stdin=subprocess.DEVNULL)
        if r.returncode:
            return None, "checker clone failed: %s" % (r.stderr or r.stdout)[-300:]
        r = self.git(d, "checkout", "--quiet", "--detach", sha)
        return (d, None) if r.returncode == 0 else (None, "checkout %s: %s" % (sha, r.stderr[-200:]))

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
    def launch(self, st, run, prompt, agent, clone, max_s, extra_env):
        """-> None, or why it did not start. The caller persisted `run` before this call."""
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
        argv = argv[:at] + env + argv[at:]
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
            "Set the contract BEFORE you edit, from the item's own words. A line of `learn` after every finding and "
            "at least every 20 minutes. Commit explicit paths and land with ./publish; every commit subject names the item id; `finish` names a sha on "
            "origin/main. Then a blind checker reruns your proof on that sha; it does not see your notes. Never run "
            "`rimflow close`, `implemented`, `release` or `claim` on this item: the supervisor owns its ledger state.",
            "A hook, systemd unit, dispatcher_schedule.json or ops_watch_rules.json change, or an OPS_ alarm item, needs --live with one of: "
            "`unit=rm-foo.timer reading=<path> max_age=6h`, `hook=block_foo.py`, `once: why`.",
            "Hit a wall? `snag` and exit: the item goes back to the top with your finding. Do not ask anyone. Only a "
            "true design/RimMandrake/delegation_policy.md section 2 call goes up: `snag --class owner_call --section "
            "<what, quoted> ...`.",
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
    return "\n".join(head + ["", "--- item ---", text, "", "--- learned so far ---", learned[-8000:]])


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
    return v, budget, head, min(room, r["max_workers"])


def worker_cap(fx, r, extra=0, store=None):
    """The places a run may take now: the stage and the budget under max_workers, stepped back to 1 while available
    memory is under step_back_mem_gb. `extra` is the place a check gets on top (a check runs even at budget 0: it holds
    a place already, and finishing work is never what a budget cut stops)."""
    cap = stage_places(store, fx, r)[3] if store is not None and r.get("staffing") else r["max_workers"]
    if cap > 1 and fx.mem_gb() < r.get("step_back_mem_gb", 0):
        cap = 1
    return cap + extra


def admission(store, fx, r, now, active, extra=0):
    """-> None when one more run may start, else why not."""
    br = load_breaker(store)
    if br.get("until", 0) > now:
        return "breaker open until %s" % iso(br["until"])
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


def launch_failed(store, r, now, why):
    br = load_breaker(store)
    br["fails"] = br.get("fails", 0) + 1
    if br["fails"] >= r["launch_breaker"]:
        n = br["fails"] - r["launch_breaker"]
        br["until"] = now + min(r["breaker_cool_s"] * (2 ** n), r["breaker_cool_max_s"])
    br["why"] = why[:300]
    store._write(store.p("breaker.json"), json.dumps(br))


def launch_ok(store):
    if load_breaker(store):
        store._write(store.p("breaker.json"), "{}")


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
    queued = sum(1 for s in live if s["status"] == "queued")
    want = target - len(live)
    if r.get("staffing"):       # the filler: a free place is reason enough, whatever the share says of the backlog
        want = max(want, worker_cap(fx, r, 0, store) - sum(1 for s in live if s["status"] in HOLDS_A_PLACE) - queued)
    room = min(want, r["enrol_per_tick"], r["max_queued"] - queued)
    took = []
    for i in order:
        if room <= 0:
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


def enrol_one(store, item, why, now):
    """A person's or the Conductor's pick. It queues in enrol order like any other and takes no lease by itself."""
    with store.lock():
        st = store.load(item)
        if st is None:
            st = new_state(item, now, why)
            store.save(st)
            store.journal({"at": iso(now), "do": "enrol", "item": item, "why": why})
        return st


def run_of(st, key):
    return st.get("run") if key == "run" else (st.get("check") or {}).get("run")


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
                                       "clone": cur["clone"] if key == "run" else (cur["check"] or {}).get("clone"),
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
        if hold:
            acts.append({"do": "check_waits", "item": item, "why": hold})
            return
        acts.append({"do": "clone_try"})
        clean, why = fx.clean_checkout(st, c["sha"])
        if why:
            launch_failed(store, r, now, why)
            acts.append({"do": "check_waits", "item": item, "why": why})
            return
        gb = fx.mem_gb()
        acts.append({"do": "mem_after_clone", "gb": gb})
        if gb < r["min_mem_available_gb"]:      # the clone itself costs gigabytes; admission saw the host before it
            fx.remove_clone({"clone": clean})
            with store.lock():                  # others go first: the same clone every tick would starve them
                st["clone_again_at"] = now + 600
                store.save(st)
            acts.append({"do": "check_waits", "item": item, "why": "memory after the clone"})
            return
        nonce = hashlib.sha256(os.urandom(16)).hexdigest()[:24]
        n = (st.get("check_count") or 0) + 1
        unit = unit_name("check", item, st["gen"]) + "-c%d" % n
        desc = run_desc(store, r, unit, now)
        with store.lock():              # the whole identity is on disk before the unit exists
            st = store.load(item)
            st["status"] = "checking"
            st["check_count"] = n
            st["check"] = {"nonce": nonce, "unit": unit, "at": now, "clone": clean, "run": desc}
            store.save(st)
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


def retire(store, fx, states, now, acts, r=None):
    """The ledger closed an item from outside (his drop, a supersede): fence first, then step() drains the runs."""
    for st in states:
        if st["status"] not in OPEN or st["status"] in ("closing", "retiring"):
            continue
        led = fx.item_state(st["item"])
        if r and st["status"] == "queued" and st["item"] in r.get("pool_ids_exclude", []):
            with store.lock():
                cur = store.load(st["item"])
                cur["status"] = "retired"
                store.save(cur)
            # started means the ledger says doing with no one on it: hand it back or it reads as worked on for good
            why = fx.ledger_reclaim(st["item"]) if st["ledger_started"] else None
            acts.append({"do": "retire", "item": st["item"], "why": "excluded in the rules", "ledger": why})
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
    for st in queue_order(store.states()):
        if cfg and launched >= cfg["launch_per_tick"]:   # prepare() blocks and the tick has a timeout
            return
        # a stopping item holds its place: its slot is not free for a fresh item while it returns to the top
        active = sum(1 for x in store.states() if x["status"] in HOLDS_A_PLACE)
        why = admission(store, fx, r, now, active)
        if why:
            acts.append({"do": "wait", "why": why})
            return
        item = st["item"]
        if st.get("needs_back"):       # the ledger still says owner: the next step() clears it first
            continue
        if item in r.get("pool_ids_exclude", []):   # back from a stop this tick: retire() takes it on the next
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
                if reserved:        # handed over, so it stays in line; the breaker paces a start that keeps refusing
                    give_back(store, item, "start refused", "queued")
                    launch_failed(store, r, now, why)
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
                launch_failed(store, r, now, why)
                acts.append({"do": "launch_fail", "item": item, "why": why})
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
           "breaker": br or None, "acts": acts[-20:],
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
    queued = sum(1 for x in states if x["status"] == "queued")
    ready = queued + sum(1 for i in order if i not in ours)
    stepped = 0 < target < room
    why = stuck = None
    if float(r["share"]) <= 0:
        why = "share 0"
    elif budget == 0:
        why = "budget 0"
    else:
        stuck = admission(store, fx, r, now, k, extra=k + 1)    # whatever else stops a run, the places aside
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
           "stage": cfg["stages"][s["stage"]], "target": target, "running": k, "live": live, "ready": ready,
           "under": under, "foreign_tree_read": words_read, "alarm_fail": alarm_fail,
           "minutes_under": minutes, "why": why, "alarmed": bool(s.get("alarmed")), "rise_lacks": lack,
           "spent_today": spent_today(store, now), "day_spend_limit": r["day_spend_limit"],
           "checks": {"waiting": len(cand), "running": sum(1 for x in states if x["status"] == "checking"),
                      "oldest_wait_s": round(now - min((x.get("candidate") or {}).get("at", now) for x in cand)) if cand else 0}}
    store._write(store.p("staffing.json"), json.dumps(rec, indent=1, sort_keys=True))
    with open(store.p("staffing.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


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
        fx = fx or Effects(r, store)
        acts = []
        if not r.get("enabled"):
            reading(store, r, now, [{"do": "disabled"}])
            return acts
        fx.sync()
        retire(store, fx, store.states(), now, acts, r)
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
        reap_quarantined(store, fx, r, now, acts)
        spend_holds(store, fx, r, now, acts)
        enrol_acts = enrol(store, fx, r, now)
        acts += [{"do": "enrol", "item": i} for i in enrol_acts]
        try:
            lease(store, fx, r, now, acts)
        except Exception as e:  # noqa: BLE001  a hung rimflow must not lose the tick's flush; a reservation resumes next tick
            acts.append({"do": "error", "item": None, "why": "lease %s: %s" % (type(e).__name__, e)})
            store.journal({"at": iso(now), "do": "alarm", "kind": "lease_raised", "why": str(e)[:300]})
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
        if name == "finish":
            p.add_argument("--sha", required=True)
            p.add_argument("--evidence", required=True)
    p = sub.add_parser("verdict")
    p.add_argument("--item", required=True)
    p.add_argument("--nonce", required=True)
    p.add_argument("word")
    p.add_argument("reasons")
    p = sub.add_parser("enrol", help="carry one named item, ahead of the share's next picks")
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
            snag(store, a.item, a.gen, a.klass, a.text, rules(), a.section)
        elif a.cmd == "finish":
            finish(store, a.item, a.gen, a.sha, a.evidence)
        elif a.cmd == "enrol":
            st = enrol_one(Store(), a.item, a.why, time.time())
            print("%s %s" % (a.item, st["status"]))
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
