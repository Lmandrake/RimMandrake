#!/usr/bin/env python3
"""donor_regen_install_hourly.py - hourly: install finished dregen_ renders (accepted-for-now), commit ONLY the changes
the run itself made, publish only its own commits. Owner decision 2026-10-19 (question card): finished donor-replacement
renders install every hour.

    python3 src/RimMandrake/Utils/art/donor_regen_install_hourly.py [--dry-run]

Runs bulk_accept_renders.py plan + apply (art_accept_finished.py was retired by eaf051b8f; every finished render waiting
is installed, dregen_ ones included). Hardened after the GPT review of 2026-10-19 (#8-#11):
  * exactly the run's own change is committed: every path the plan may touch is snapshotted before apply; a path that
    was clean commits its new content, a path someone else had already edited commits HEAD + (our pre->post change)
    via `git merge-file`, and the append-only FOUNDRY art-events shard commits HEAD + only the lines this run appended.
    A change that cannot be separated from someone else's edit commits NOTHING this run (logged).
  * the commit is built in a PRIVATE index (GIT_INDEX_FILE in a temp dir, read-tree HEAD) and lands by compare-and-swap
    (`commit-tree` + `update-ref HEAD <new> <old>`): the shared index is never staged into, a concurrent commit makes
    this run's commit fail instead of reverting it, and a failure leaves nothing staged. Afterwards only the shared
    index entries of the committed paths that still matched the old HEAD are moved to the new blobs, so `git status`
    stays truthful; any other entry is left alone and logged.
  * every git call runs with GIT_LITERAL_PATHSPECS=1 (a file named Icon[1].png is never a glob for Icon1.png).
  * ./publish runs only when every commit not on origin/main carries this script's trailer (a refused push is retried
    next hour); any foreign unpublished commit -> logged, publish skipped.
  * every child process has a timeout.
Log: Transient/donor_regen_install.log (untracked).
Timer: rm-donor-regen-install.timer (transient systemd-run; dies on WSL restart, re-create it - see the item
DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO).
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EVENTS = "infrastructure/state/art/events/FOUNDRY.jsonl"
TOOL = "src/RimMandrake/Utils/art/bulk_accept_renders.py"
TRAILER = "Hourly-Install: donor_regen_install_hourly"
TIMEOUT = {"tool": 1800, "git": 120, "fetch": 180, "publish": 900}
ZERO = "0" * 40
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils"))
from selftest_no_case_twins import case_twins  # noqa: E402


class Stop(Exception):
    """End the run: logged, nothing (more) committed."""


class Run:
    def __init__(self, repo=REPO, tool=TOOL, publish=("./publish",), events=EVENTS, dry=False):
        self.repo, self.tool, self.publish, self.events, self.dry = Path(repo), tool, list(publish), events, dry
        self.log_p = self.repo / "Transient" / "donor_regen_install.log"
        self.env = dict(os.environ, GIT_LITERAL_PATHSPECS="1", RIMFLOW_SEAT=os.environ.get("RIMFLOW_SEAT", "FOUNDRY"),
                        BULK_ACCEPT_NO_OWNER_OVERRIDE="1")  # owner-KEPT/rejected destinations are refused, never overridden

    def log(self, msg):
        self.log_p.parent.mkdir(exist_ok=True)
        line = f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {'[dry] ' if self.dry else ''}{msg}"
        with self.log_p.open("a") as fh:
            fh.write(line + "\n")
        print(line)

    def run(self, *a, timeout="git", env=None, input=None, text=True):
        try:
            return subprocess.run(a, cwd=self.repo, capture_output=True, text=text, input=input,
                                  env=env or self.env, timeout=TIMEOUT[timeout])
        except subprocess.TimeoutExpired:
            raise Stop(f"TIMEOUT after {TIMEOUT[timeout]} s: {' '.join(map(str, a))[:160]}")

    def git(self, *a, env=None, input=None, text=True, ok=True):
        r = self.run("git", *a, env=env, input=input, text=text)
        if ok and r.returncode:
            err = r.stderr if text else r.stderr.decode(errors="replace")
            raise Stop(f"git {' '.join(a[:3])} failed rc={r.returncode}: {err.strip()[-300:]!r}")
        return r

    # ─────────────────────────────────────────────────────────── content ──
    def head_blob(self, head, path):
        r = self.git("cat-file", "blob", f"{head}:{path}", text=False, ok=False)
        return r.stdout if r.returncode == 0 else None

    def disk(self, path):
        p = self.repo / path
        return p.read_bytes() if p.is_file() else None

    def our_change(self, path, head_b, pre, post):
        """-> the content to commit for `path` (None = deleted), or raise Stop when our change cannot be separated."""
        if post == pre:
            return head_b                                    # this run did not change it
        if pre == head_b:
            return post                                      # it was clean: everything that changed is ours
        if path == self.events:                              # append-only shard: commit HEAD + only our lines
            if pre is None or post is None or not post.startswith(pre):
                raise Stop(f"{path}: not a pure append by this run; commit skipped")
            base = head_b or b""
            if base and not base.endswith(b"\n"):
                base += b"\n"
            return base + post[len(pre):]
        if post is None or pre is None or head_b is None or b"\0" in (pre + post + head_b)[:8192]:
            return post                                      # binary / created / deleted: the install replaced it whole
        with tempfile.TemporaryDirectory(prefix="dregen_merge_") as td:
            fs = []
            for n, b in (("head", head_b), ("pre", pre), ("post", post)):
                f = Path(td) / n
                f.write_bytes(b)
                fs.append(str(f))
            r = self.run("git", "merge-file", "-p", "--quiet", *fs, text=False)
            if r.returncode != 0:
                raise Stop(f"{path}: our edit overlaps an uncommitted edit by someone else; commit skipped")
            return r.stdout

    # ─────────────────────────────────────────────────────────── commit ──
    def commit(self, head, changes, n):
        """changes: {path: bytes|None}. Private index + compare-and-swap onto `head`. -> new commit sha."""
        with tempfile.TemporaryDirectory(prefix="dregen_idx_") as td:
            env = dict(self.env, GIT_INDEX_FILE=str(Path(td) / "index"))
            self.git("read-tree", head, env=env)
            info = []
            for path, b in sorted(changes.items()):
                if b is None:
                    info.append(f"0 {ZERO}\t{path}")
                    continue
                blob = self.git("hash-object", "-w", "--stdin", input=b, text=False).stdout.decode().strip()
                mode = self.git("ls-tree", "-r", head, "--", path).stdout.split(" ", 1)[0] or "100644"
                info.append(f"{mode} {blob}\t{path}")
            self.git("update-index", "--index-info", env=env, input="\n".join(info) + "\n")
            tree = self.git("write-tree", env=env).stdout.strip()
        names = self.git("ls-tree", "-r", "-z", "--name-only", tree, text=False).stdout.decode("utf-8", "surrogateescape")
        twins = case_twins([p for p in names.split("\0") if p])
        if twins:                                            # Windows/Mac clones cannot hold these (PaleTree_B, 2026-10-19)
            raise Stop(f"commit would hold case-twin paths {twins[:5]}; nothing committed")
        if tree == self.git("rev-parse", f"{head}^{{tree}}").stdout.strip():
            return None
        msg = (f"Donor art: hourly install of {n} finished dregen_ renders (accepted-for-now)\n\n{TRAILER}\n"
               "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n")
        new = self.git("commit-tree", tree, "-p", head, input=msg).stdout.strip()
        r = self.git("update-ref", "-m", "donor_regen_install_hourly", "HEAD", new, head, ok=False)
        if r.returncode:
            raise Stop(f"HEAD moved while committing (someone else committed); nothing committed, retry next hour: "
                       f"{r.stderr.strip()[-200:]!r}")
        self.sync_shared_index(head, new, sorted(changes))
        return new

    def sync_shared_index(self, old, new, paths):
        """Move shared-index entries of OUR committed paths from the old HEAD blob to the new one, and only those that
        still equal the old HEAD (nobody staged anything there)."""
        def entries(args):
            out = {}
            for ln in self.git(*args, "--", *paths).stdout.splitlines():
                meta, p = ln.split("\t", 1)
                mode, _type, sha = meta.split()
                out[p] = (mode, sha)
            return out
        idx = {}
        for ln in self.git("ls-files", "-s", "--", *paths).stdout.splitlines():
            meta, p = ln.split("\t", 1)
            mode, sha, _stage = meta.split()
            idx[p] = (mode, sha)
        told, tnew = entries(["ls-tree", "-r", old]), entries(["ls-tree", "-r", new])
        info, left = [], []
        for p in paths:
            if idx.get(p) != told.get(p):
                left.append(p)
                continue
            if p in tnew:
                info.append(f"{tnew[p][0]} {tnew[p][1]}\t{p}")
            elif p in idx:
                info.append(f"0 {ZERO}\t{p}")
        if info:
            r = self.git("update-index", "--index-info", input="\n".join(info) + "\n", ok=False)
            if r.returncode:
                self.log(f"WARN shared index not updated ({r.stderr.strip()[-160:]!r}); `git status` shows the "
                         f"committed paths as staged reversions until `git reset -q -- <path>`: {', '.join(paths)[:400]}")
        if left:
            self.log(f"shared index: {len(left)} committed path(s) had someone else's staged entry, left alone: "
                     f"{', '.join(left)[:300]}")

    # ─────────────────────────────────────────────────────────── publish ──
    def maybe_publish(self):
        f = self.run("git", "fetch", "-q", "origin", "main", timeout="fetch")
        if f.returncode:
            return self.log(f"SKIP publish: fetch failed ({f.stderr.strip()[-160:]!r})")
        shas = self.git("rev-list", "origin/main..HEAD").stdout.split()
        if not shas:
            return self.log("nothing to publish")
        foreign = [s for s in shas if TRAILER not in self.git("log", "-1", "--format=%B", s).stdout]
        if foreign:
            return self.log(f"SKIP publish: {len(foreign)} unpublished commit(s) not made by this script "
                            f"({', '.join(s[:9] for s in foreign[:5])}); its own {len(shas) - len(foreign)} wait")
        p = self.run(*self.publish, timeout="publish")
        if p.returncode:
            return self.log(f"PUSH REFUSED/FAILED, retry next hour: {(p.stdout + p.stderr)[-400:]!r}")
        self.log("publish: " + (p.stdout.strip().splitlines() or [""])[-1])

    # ─────────────────────────────────────────────────────────── main ──
    def main(self):
        lock = Path(self.git("rev-parse", "--git-path", "index.lock").stdout.strip())
        lock = lock if lock.is_absolute() else self.repo / lock
        if lock.exists():
            return self.log(f"SKIP: git index lock held ({lock})")
        plan = Path(tempfile.mkdtemp(prefix="dregen_plan_")) / "plan.json"
        r = self.run(sys.executable, self.tool, "plan", "--out", str(plan), timeout="tool")
        if r.returncode:
            return self.log(f"FAIL plan rc={r.returncode} (no commit): {(r.stdout + r.stderr)[-400:]!r}")
        P = json.loads(plan.read_text())
        may = {self.events} | {x["dest"] for x in P.get("rows", [])} | set(P.get("retire", [])) \
            | {x for rp in P.get("repoint", []) for x in rp.get("xml", [])}
        head = self.git("rev-parse", "HEAD").stdout.strip()
        pre = {p: self.disk(p) for p in may}
        r = self.run(sys.executable, self.tool, "apply", "--plan", str(plan), *(["--dry-run"] if self.dry else []),
                     timeout="tool")
        m = re.search(r"^log: (.+)$", r.stdout, re.M)
        if r.returncode or not m:
            return self.log(f"FAIL rc={r.returncode} (no commit): {(r.stdout + r.stderr)[-400:]!r}")
        if self.dry:
            return self.log(f"plan: {len(P['rows'])} installable rows (dry run installs nothing)")
        d = json.loads(Path(m.group(1)).read_text())
        d = {k: d.get(k, []) for k in ("installed", "repointed", "retired", "refused", "already")} | d
        # owner-KEPT refusals are SHELVED (owner 2026-10-19: the renders wait as unassigned candidates on the item's
        # sheet, the kept picture stays): logged as a count, never re-reported as new.
        shelved = [x for x in d["refused"] if "owner-KEPT" in (x.get("why") or "")]
        d["refused"] = [x for x in d["refused"] if x not in shelved]
        sh = self.repo / "Transient" / "donor_regen_shelved.json"
        try:
            seen = set(json.loads(sh.read_text()))
        except (OSError, ValueError):
            seen = set()
        fresh = sorted({x["job"] for x in shelved if x["job"]} - seen)
        sh.parent.mkdir(exist_ok=True)
        sh.write_text(json.dumps(sorted(seen | {x["job"] for x in shelved if x["job"]})))
        self.log(f"{len(d['installed'])} installed, {len(shelved)} shelved (owner-KEPT, {len(fresh)} newly), "
                 f"{len(d['refused'])} refused, plan-log={m.group(1)}")
        if fresh:
            self.log("newly shelved (back-fill them onto sheets: art.py backfill artpipe, refresh_sheets.py): "
                     + ", ".join(fresh))
        touched = sorted(set(d["installed"]) | set(d["repointed"]) | set(d["retired"]) | {self.events})
        stray = [p for p in touched if p not in pre]
        if stray:
            raise Stop(f"apply touched path(s) outside its plan, not snapshotted: {', '.join(stray)[:300]}; commit skipped")
        changes = {}
        for p in touched:
            hb = self.head_blob(head, p)
            new = self.our_change(p, hb, pre[p], self.disk(p))
            if new != hb:
                changes[p] = new
        if changes:
            c = self.commit(head, changes, len(d["installed"]))
            if c:
                self.log(f"committed {c[:10]}: {len(changes)} paths ({len(d['installed'])} installed)")
        else:
            self.log("nothing installed")
        self.maybe_publish()


def main(argv=None, **kw):
    argv = sys.argv[1:] if argv is None else argv
    R = Run(dry="--dry-run" in argv, **kw)
    try:
        R.main()
    except Stop as e:
        R.log(f"STOP: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
