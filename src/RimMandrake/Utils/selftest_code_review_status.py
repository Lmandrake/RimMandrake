#!/usr/bin/env python3
"""selftest_code_review_status.py — the hash-based clean/dirty core, live.

    python3 src/RimMandrake/Utils/selftest_code_review_status.py

Runs `code_review_status.py`'s real commands (mark-clean/check/reopen/
migrate-hashes) against a throwaway git repo built in a temp dir
(CODE_REVIEW_STATUS_ROOT redirect — same discipline as rimflow's
RIMFLOW_LEDGER/RIMFLOW_ITEMS) — never touches this repo's own ledger.

Covers the 2026-09-05 rewrite (owner: "this isn't scaling properly, it's a
bottleneck" — git-status/git-log-per-path replaced by a SHA-256 content
hash):

  1. mark-clean -> check round trip, on a fresh commit.
  2. Editing the file after mark-clean reads DIRTY (content differs), with
     NO commit required to detect it — the whole point of hashing bytes
     instead of asking git.
  3. mark-clean refuses on an uncommitted change (CLAUDE.md's documented
     contract; must survive the rewrite unchanged).
  4. mark-clean refuses on an untracked (never-committed) file.
  5. reopen puts a path back to "never marked clean".
  6. Binary content (a fake PNG header) round-trips through mark-clean and
     the migrate-hashes path — this is a live regression: git()'s original
     text=True decode crashed with UnicodeDecodeError on the first real
     binary file measured during the rewrite.
  7. migrate-hashes backfills a legacy {sha, date, cleanCount}-only entry
     (no hash) by reading the file's content AT THAT SHA, not the current
     working copy — proven by mutating the file AFTER the legacy commit and
     confirming the backfilled hash matches the OLD content, and that
     `check` then correctly reads DIRTY (current bytes differ from what was
     actually reviewed).
  8. migrate-hashes is idempotent and leaves an unresolvable sha hash-less
     (reads DIRTY "needs re-verification"), matching the pre-rewrite tool's
     "recorded sha not found — log is stale" outcome.
  9. prune drops an entry only when its path no longer exists on disk at
     all (a deleted or `git mv`'d-with-no-new-entry file), leaves everything
     else alone, and does nothing without --apply.
 10. find_untracked() (list --show-untracked) surfaces a src/*.xml file that
     is tracked by git but has NEVER been given an entry at all — the gap
     the owner caught 2026-09-05 questioning a reported "0 DIRTY" that was
     only true for the ~917 paths ever entered, not the ~1,402 real files.
 11. git()'s timeout path returns a failed CompletedProcess rather than
     raising — a hung/contended git call must degrade, never hang the caller.
"""
import os
import shutil
import subprocess
import sys
import tempfile

TMP = tempfile.mkdtemp(prefix="crs_selftest_")
os.environ["CODE_REVIEW_STATUS_ROOT"] = TMP

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FAILS = []


def eq(got, want, what):
    if got != want:
        FAILS.append("%s: got %r, want %r" % (what, got, want))


def sh(*args, cwd=TMP):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        FAILS.append("setup command failed: %r -> %s%s" % (args, r.stdout, r.stderr))
    return r


def write(relpath, content, binary=False):
    p = os.path.join(TMP, relpath)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    mode = "wb" if binary else "w"
    with open(p, mode) as f:
        f.write(content)


# ---- repo scaffold --------------------------------------------------------
os.makedirs(os.path.join(TMP, "infrastructure", "state"), exist_ok=True)
sh("git", "init", "-q")
sh("git", "config", "user.email", "selftest@example.com")
sh("git", "config", "user.name", "selftest")
write("a.xml", "<Defs>v1</Defs>\n")
sh("git", "add", "a.xml")
sh("git", "commit", "-q", "-m", "add a.xml v1")

import code_review_status as CRS  # noqa: E402  (import AFTER the env var + repo exist)


def run(*args):
    """Invoke a subcommand as main() would, capturing its return code."""
    old_argv = sys.argv
    sys.argv = ["code_review_status.py"] + list(args)
    try:
        try:
            CRS.main()
        except SystemExit as e:
            return e.code or 0
    finally:
        sys.argv = old_argv


# ---- 1. mark-clean -> check round trip ------------------------------------
rc = run("mark-clean", os.path.join(TMP, "a.xml"))
eq(rc, 0, "mark-clean a fresh commit succeeds")
rc = run("check", os.path.join(TMP, "a.xml"))
eq(rc, 0, "check exits 0 for a clean file")

# ---- 2. edit without committing -> DIRTY, no commit needed to detect it --
write("a.xml", "<Defs>v2 EDITED</Defs>\n")
state, detail = CRS.clean_state("a.xml", CRS.load().get("a.xml"))
eq(state, "DIRTY", "editing the file flips it to DIRTY before any commit")
eq("content changed" in detail, True, "the reason names content change, not git history")

# restore + commit the edit so the next checks start from a known state
sh("git", "add", "a.xml")
sh("git", "commit", "-q", "-m", "edit a.xml v2")

# ---- 3. mark-clean refuses on an uncommitted change -----------------------
write("a.xml", "<Defs>v3 UNCOMMITTED</Defs>\n")
rc = run("mark-clean", os.path.join(TMP, "a.xml"))
eq(rc, 2, "mark-clean refuses while the file has uncommitted changes")
sh("git", "checkout", "--", "a.xml")  # discard, back to v2 committed

# ---- 4. mark-clean refuses on an untracked file ---------------------------
write("untracked.xml", "<Defs>never committed</Defs>\n")
rc = run("mark-clean", os.path.join(TMP, "untracked.xml"))
eq(rc, 2, "mark-clean refuses an untracked file")

# ---- 5. reopen ------------------------------------------------------------
rc = run("mark-clean", os.path.join(TMP, "a.xml"))
eq(rc, 0, "mark-clean v2 (committed) succeeds")
rc = run("reopen", os.path.join(TMP, "a.xml"), "--reason", "selftest")
eq(rc, 0, "reopen succeeds")
state, detail = CRS.clean_state("a.xml", CRS.load().get("a.xml"))
eq(state, "DIRTY", "a reopened file is never marked clean")
eq(detail, "never marked clean", "reopen's reason matches a brand-new file")

# ---- 6. binary content round-trips (the real crash this rewrite hit) ------
png_header = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]) + b"fake png body"
write("art.png", png_header, binary=True)
sh("git", "add", "art.png")
sh("git", "commit", "-q", "-m", "add art.png")
rc = run("mark-clean", os.path.join(TMP, "art.png"))
eq(rc, 0, "mark-clean succeeds on a binary file (git()'s old text=True decode crashed here)")
rc = run("check", os.path.join(TMP, "art.png"))
eq(rc, 0, "a freshly-marked binary file checks CLEAN")

# ---- 7. migrate-hashes backfills from the RECORDED SHA, not current bytes -
write("legacy.xml", "<Defs>legacy v1 — the reviewed content</Defs>\n")
sh("git", "add", "legacy.xml")
sh("git", "commit", "-q", "-m", "add legacy.xml v1")
legacy_sha = sh("git", "rev-parse", "--short", "HEAD").stdout.strip()
legacy_v1_hash = CRS.file_hash("legacy.xml")

data = CRS.load()
data["legacy.xml"] = {"sha": legacy_sha, "date": "2020-01-01", "cleanCount": 1}  # no "hash" — pre-rewrite shape
CRS.save(data)

# drift the working copy AFTER the legacy commit, same as any real repo
# that kept moving after an old clean mark
write("legacy.xml", "<Defs>legacy v2 — drifted after the old review</Defs>\n")
sh("git", "add", "legacy.xml")
sh("git", "commit", "-q", "-m", "drift legacy.xml to v2")

rc = run("migrate-hashes")
eq(rc, 0, "migrate-hashes exits 0")
migrated_entry = CRS.load()["legacy.xml"]
eq(migrated_entry.get("hash"), legacy_v1_hash,
   "migrate-hashes backfills the hash of the REVIEWED (old) content, not today's drifted copy")
state, detail = CRS.clean_state("legacy.xml", migrated_entry)
eq(state, "DIRTY", "the drifted file correctly reads DIRTY once its true reviewed hash is known")

# idempotency: running it again must not change an already-hashed entry
before = dict(CRS.load()["legacy.xml"])
run("migrate-hashes")
after = CRS.load()["legacy.xml"]
eq(after, before, "migrate-hashes is a no-op on an entry that already has a hash")

# ---- 8. an unresolvable legacy sha stays hash-less, reads DIRTY -----------
data = CRS.load()
data["ghost.xml"] = {"sha": "0000000", "date": "2019-01-01", "cleanCount": 1}
CRS.save(data)
run("migrate-hashes")
ghost_entry = CRS.load()["ghost.xml"]
eq("hash" in ghost_entry, False, "an unresolvable sha is left without a hash")
state, detail = CRS.clean_state("ghost.xml", ghost_entry)
eq(state, "DIRTY", "a hash-less legacy entry reads DIRTY")
eq("needs re-verification" in detail, True, "the reason says it needs a real review, not a repo fault")

# ---- 9. prune drops only entries whose path no longer exists on disk ------
write("gone.xml", "<Defs>about to be deleted</Defs>\n")
sh("git", "add", "gone.xml")
sh("git", "commit", "-q", "-m", "add gone.xml")
run("mark-clean", os.path.join(TMP, "gone.xml"))
os.remove(os.path.join(TMP, "gone.xml"))

rc = run("prune")  # no --apply: report only
eq(rc, 0, "prune (dry run) exits 0")
eq("gone.xml" in CRS.load(), True, "prune without --apply does not remove anything")

rc = run("prune", "--apply")
eq(rc, 0, "prune --apply exits 0")
eq("gone.xml" in CRS.load(), False, "prune --apply removes an entry for a deleted path")
eq("art.png" in CRS.load(), True, "prune --apply leaves an entry whose path still exists")

rc = run("prune")
eq(rc, 0, "prune is a clean no-op once nothing is orphaned")

# ---- 10. find_untracked surfaces a never-entered src/ file ----------------
write("src/Mod/Defs/never_reviewed.xml", "<Defs><ThingDef><defName>X</defName></ThingDef></Defs>\n")
write("src/Mod/Defs/reviewed.xml", "<Defs><ThingDef><defName>Y</defName></ThingDef></Defs>\n")
sh("git", "add", "src/Mod/Defs/never_reviewed.xml", "src/Mod/Defs/reviewed.xml")
sh("git", "commit", "-q", "-m", "add two src/ files, only one ever reviewed")
run("mark-clean", os.path.join(TMP, "src/Mod/Defs/reviewed.xml"))

untracked = CRS.find_untracked(CRS.load())
eq(untracked is None, False, "find_untracked succeeds against a real git repo")
eq("src/Mod/Defs/never_reviewed.xml" in (untracked or []), True,
   "a tracked src/*.xml file with no entry at all is surfaced as untracked")
eq("src/Mod/Defs/reviewed.xml" in (untracked or []), False,
   "a src/*.xml file that HAS an entry must not appear as untracked, even mid-review-cycle")

rc = run("list", "--show-untracked")
eq(rc, 0, "list --show-untracked exits 0")

# ---- 11. git() degrades on a timeout instead of raising --------------------
real_run = subprocess.run


def _raise_timeout(*a, **kw):
    raise subprocess.TimeoutExpired(cmd=a, timeout=CRS.GIT_TIMEOUT)


subprocess.run = _raise_timeout
try:
    r = CRS.git(["status"])
    eq(r.returncode, -1, "a git() timeout returns a failed CompletedProcess, not an exception")
finally:
    subprocess.run = real_run

shutil.rmtree(TMP, ignore_errors=True)

if FAILS:
    print("FAIL selftest_code_review_status.py")
    for f in FAILS:
        print("  " + f)
    sys.exit(1)
print("ok  selftest_code_review_status.py — hash-based clean/dirty, migration, "
      "binary content, timeout degradation")
