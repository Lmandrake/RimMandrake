#!/usr/bin/env python3
"""rimflow/lease.py — expiring claim leases and the dispatcher lock (rimflow redesign STEP 3).

Design: `design/RimMandrake/rimflow_gpt_review_2026-10-07.md` §"Claims should be leases"
and Q4; owner's build order 2026-10-06 (*"In order, 1, 2, 3, 4"* — this is 3).

THE FAILURE IT FIXES
====================
Several subagents of ONE window ran `rimflow next` and got the SAME top item, because
`next` was a pure read: nothing recorded that the item had been handed out. And `claim`
put an item straight back into the offered pool (`claim` -> `ready`, and `rank()` offers
exactly `ready`), so claiming advertised the work instead of hiding it.

WHAT A LEASE IS
===============
A `lease` ledger event (`model.VERBS["lease"]`): `action` take|renew|release, an opaque
`token`, and an absolute `expires` timestamp. The rules are in `model._apply_lease` —
this module only mints tokens and holds the lock.

  * `next` (not `--peek`) TAKES a lease on the item it offers, under the dispatcher lock.
  * `claim` takes one (or renews the caller's own with `--token`) and STARTS the item.
  * `renew <ID> --token T` every ~10 min; a lease lapses LEASE_TTL_S after its last
    take/renew. `release <ID> --token T` gives it back early.
  * Only the token holder may renew or release. Renewal needs the lease still live — an
    expired worker must reacquire through `next`/`claim` like anyone else.
  * Liveness is judged from lease timestamps (`expires`) only — never from notes, claims
    or any other item activity.
  * A lapsed lease makes the item offerable again, but `next` runs it through the step-1
    git check (`reconcile.assess`) and labels it LAPSED; it is never silently "build this".

🔴 WHAT THIS DOES NOT DO — TWO CLONES ARE NOT COORDINATED
=========================================================
The lock is an `fcntl.flock` on a file inside THIS clone's git dir. It serialises every
`next`/`claim`/`renew`/`release` run from the same checkout — a window and all of its
subagents — and nothing else. BENCH (`/home/mandrake/rm/bench`) and FOUNDRY
(`/home/mandrake/rm/foundry`) are separate clones with separate git dirs, so each has its
own lock, and each appends lease events to its OWN shard; the two only meet after a push
and a `merge=union` pull. Two clones can therefore both take a lease on one item, and both
events survive the merge. Today that is mostly harmless because `rank()` filters by owner
seat (BENCH never gets FOUNDRY's items), but it is NOT exclusivity: a second FOUNDRY clone,
or an OWNER-override claim from BENCH, would race unprotected.

A cross-clone design needs ONE authoritative reservation store that every clone reaches
before it answers: e.g. a lock + lease table in a single host-wide path both clones mount
(`/home/mandrake/rm/.rimflow-dispatch/`, same machine only), or a compare-and-swap on a
remote (a lease ref pushed with `--force-with-lease`, where a rejected push means "someone
else won"), or a small service. Appending to per-clone files and merging later can never
provide it (review §"Claims should be leases": "Separate clones cannot safely allocate
reservations by independently appending files and later merging them").

⚠️ OLD READERS. A clone running rimflow from before this step (0884bcc72 and earlier) does
not know the `lease` verb: each lease event lands in its `world.errors` (counted, never
fatal) and changes nothing there. What it DOES see of a claim is the `claim` + `start`
pair the new `claim` writes, so a claimed item is `doing` and hidden on old clones too.
An item merely reserved by `next` is still plain `ready` to an old clone and an old `next`
would offer it (selftest_lease.py pins all of this).
"""
import contextlib
import fcntl
import os
import secrets

try:
    from . import model
except ImportError:                                         # script invocation
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rimflow import model                               # noqa: E402

# Review §"Claims should be leases": 45 minutes, renewed every 10. `RIMFLOW_LEASE_TTL`
# (seconds) exists for the selftests, which cannot wait 45 minutes for an expiry.
LEASE_TTL_S = 45 * 60
RENEW_EVERY_S = 10 * 60
LOCK_NAME = "rimflow-dispatch.lock"


def ttl_seconds():
    raw = os.environ.get("RIMFLOW_LEASE_TTL")
    try:
        v = int(raw) if raw else LEASE_TTL_S
    except ValueError:
        v = LEASE_TTL_S
    return max(1, min(v, model.LEASE_MAX_S))


def new_token(seat):
    """-> an opaque lease token: seat, run/session identity, worker nonce.

    Subagents have no stable identity (system doc §3.8), and they do not need one: the
    token IS the identity of this one reservation, and only its holder knows it."""
    sess = (os.environ.get("CLAUDE_SESSION_ID") or "pid%d" % os.getpid())
    sess = "".join(c for c in sess if c.isalnum())[:8] or "anon"
    return "%s.%s.%s" % (seat or "SEAT", sess, secrets.token_hex(4))


def expires_at(now_epoch=None, ttl=None):
    """-> the `expires` stamp for a lease taken or renewed now."""
    return model.stamp(model.epoch_now() if now_epoch is None else now_epoch,
                       ttl if ttl is not None else ttl_seconds())


def _git_dir(root):
    """-> the git dir of the clone at `root` (a `.git` dir, or a `.git` file's
    `gitdir:` target), or None. No subprocess: this runs on every `next`."""
    dotgit = os.path.join(root, ".git")
    if os.path.isdir(dotgit):
        return dotgit
    if os.path.isfile(dotgit):
        try:
            with open(dotgit, encoding="utf-8") as fh:
                line = fh.read().strip()
        except OSError:
            return None
        if line.startswith("gitdir:"):
            g = line[len("gitdir:"):].strip()
            return g if os.path.isabs(g) else os.path.normpath(os.path.join(root, g))
    return None


def lock_path():
    """-> the dispatcher lock file for the ledger IN USE.

    The real ledger locks in this clone's git dir (never tracked, never pushed, one per
    clone — see the module docstring for why that is the limit of what it protects). A
    redirected test ledger (`RIMFLOW_LEDGER`) locks beside itself so a selftest can never
    contend with, or be serialised behind, a live window."""
    forced = os.environ.get("RIMFLOW_DISPATCH_LOCK")
    if forced:
        return forced
    led_dir = os.path.dirname(os.path.abspath(model.EVENTS))
    real = os.path.join(os.path.abspath(model.STATE), "ledger")
    if led_dir == real:
        g = _git_dir(model.ROOT)
        if g:
            return os.path.join(g, LOCK_NAME)
    return os.path.join(led_dir, "." + LOCK_NAME)


@contextlib.contextmanager
def dispatch_lock():
    """Hold the clone-wide dispatcher lock: replay, choose and record the lease inside it.

    `fcntl.flock(LOCK_EX)` blocks until the holder leaves; the kernel drops it if the
    holder dies, so a crashed subagent can never wedge dispatch. Advisory, like the ledger
    lock in `model.append`: it binds only code that takes it, which is every lease writer
    in this package."""
    path = lock_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            yield path
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def instructions(iid, token, expires):
    """The lines every lease-taking command prints. One wording, so `next` and `claim`
    cannot drift apart."""
    return [
        "🔒 RESERVED for you until %s — lease token %s" % (expires, token),
        "   Nobody else's `rimflow next` will offer %s while this lease is live." % iid,
        "   keep it:  rimflow renew %s --token %s     (every %d min; it lapses at %d)"
        % (iid, token, RENEW_EVERY_S // 60, ttl_seconds() // 60),
        "   give up:  rimflow release %s --token %s" % (iid, token),
    ]
