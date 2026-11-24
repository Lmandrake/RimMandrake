#!/usr/bin/env python3
"""orphan_bundles.py — judge the orphan store's bundles against origin/main; delete the ones fully landed.

RIMMANDRAKE_PRUNE_ORPHAN_BUNDLES_FULLY_LANDED (2026-11-16): relentless.bundle_clone writes a bundle for every
returned clone that held anything (store/orphans/bundles/<stamp>-<ITEM>/), and nothing ever pruned them: 357 bundles,
7.7 GB. A bundle is LANDED when every piece of work in it is on origin/main in content:

    real.patch, index.patch   the tracked edits: reverse-apply cleanly to origin/main's tree (temp index, no clone touched)
    real_untracked.tar        each file: origin/main holds the same bytes at that path, or origin's .gitignore ignores it
    commits.bundle            each commit not on origin: its diff reverse-applies to origin/main's tree
    ignored.tar               ignored files: derived by definition, never work

    orphan_bundles.py judge [--json OUT]     one line per bundle: LANDED | UNLANDED <why> | UNJUDGED <why>
    orphan_bundles.py prune --apply          delete the LANDED ones; the rest are listed, never touched
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
STORE = os.environ.get("RM_ORPHAN_BUNDLES", "/home/mandrake/rm/relentless/store/orphans/bundles")
DERIVED = ("ignored.tar", "HEAD", "diff.patch")    # diff.patch: real.patch plus pool noise (a hard link when equal)


def git(*a, env=None, inp=None, check=False):
    return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=inp is None or isinstance(inp, str),
                          input=inp, env=env, timeout=600)


class Origin:
    """origin/main's tree, read once: path -> blob id, plus a temp index seeded from it for reverse-apply checks."""

    def __init__(self, ref="origin/main"):
        self.ref = ref
        out = git("ls-tree", "-r", "-z", ref).stdout
        self.blobs = {}
        for rec in out.split("\0"):
            if "\t" in rec:
                meta, path = rec.split("\t", 1)
                self.blobs[path] = meta.split()[2]
        self._hist = {}
        self.tmp = tempfile.mkdtemp(prefix="orphan_judge.")
        self.idx = os.path.join(self.tmp, "index")
        self.env = dict(os.environ, GIT_INDEX_FILE=self.idx)
        git("read-tree", ref, env=self.env)

    def history(self, path):
        """-> every blob id origin's history ever held at path (the work landed, maybe edited later)."""
        if path not in self._hist:
            out = git("log", self.ref, "--format=", "--raw", "--no-abbrev", "--no-renames", "--", path).stdout
            self._hist[path] = {ln.split()[3] for ln in out.splitlines() if ln.startswith(":") and len(ln.split()) >= 5}
        return self._hist[path]

    def blob_landed(self, path, blob):
        """A deletion lands when origin no longer holds the path; content lands when origin ever held those bytes."""
        if set(blob) == {"0"}:
            return path not in self.blobs
        return self.blobs.get(path, "").startswith(blob) or any(b.startswith(blob) for b in self.history(path))

    def lines_landed(self, path, added):
        """Append-mostly files (ledger shards, docs edited by several clones) never held one writer's exact bytes: the
        edit landed when every non-blank line it added is in origin's current file."""
        want = [x.strip() for x in added if x.strip()]
        if not want or path not in self.blobs:
            return False
        have = set(x.strip() for x in git("cat-file", "-p", self.blobs[path], inp=None).stdout.splitlines())
        return all(x in have for x in want)

    def patch_files_landed(self, patch_path):
        """-> [paths] of a git patch whose post-image (its `index old..new` line) origin never held."""
        files, cur = [], None
        with open(patch_path, "rb") as f:
            for raw in f:
                ln = raw.decode("utf-8", "replace").rstrip("\n")
                if ln.startswith("diff --git "):
                    cur = {"path": ln.split(" b/", 1)[-1], "new": None, "added": []}
                    files.append(cur)
                elif cur and ln.startswith("index ") and cur["new"] is None:
                    cur["new"] = ln.split()[1].split("..")[1]
                elif cur and ln.startswith("+") and not ln.startswith("+++"):
                    cur["added"].append(ln[1:])
        left = [x["path"] for x in files if x["new"] and not self.blob_landed(x["path"], x["new"])
                and not self.lines_landed(x["path"], x["added"])]
        derived = self.ignored(left)     # an edit to a file origin has since stopped tracking and ignores
        return [p for p in left if p not in derived]

    def patch_landed(self, patch_path):
        """-> None when the patch is empty or already in origin's tree, else a reason."""
        if os.path.getsize(patch_path) == 0:
            return None
        r = git("apply", "--cached", "--reverse", "--check", patch_path, env=self.env)
        if r.returncode == 0:
            return None
        left = self.patch_files_landed(patch_path)
        return "%d file(s) whose edit origin never held: %s" % (len(left), ", ".join(left[:4])) if left else None

    def ignored(self, paths):
        if not paths:
            return set()
        r = git("check-ignore", "--no-index", "--stdin", "-z", inp="\0".join(paths) + "\0")
        # a path origin tracks is work even when a pattern matches it (pins, force-added files)
        return set(p for p in r.stdout.split("\0") if p and p not in self.blobs)

    def tar_landed(self, tar_path):
        """-> [paths] in the tar that origin holds neither in the same bytes nor ignores."""
        pending = {}
        with tarfile.open(tar_path) as t:
            for m in t.getmembers():
                if not m.isfile():
                    continue
                data = t.extractfile(m).read()
                blob = git("hash-object", "--stdin", inp=data).stdout.strip().decode()
                if not self.blob_landed(m.name, blob):
                    pending[m.name] = True
        ign = self.ignored(sorted(pending))
        return sorted(p for p in pending if p not in ign)

    def commits_landed(self, bundle_path):
        """-> None when every commit of the bundle is in origin in content, else a reason."""
        heads = git("bundle", "list-heads", bundle_path)
        if heads.returncode != 0:
            return "unreadable commits.bundle"
        ns = "refs/orphan-judge/"
        names = [ln.split()[1] for ln in heads.stdout.splitlines() if len(ln.split()) == 2]
        specs = ["+%s:%s%d" % (ref, ns, i) for i, ref in enumerate(names)]
        if not specs:
            return None
        r = git("fetch", "-q", "--no-tags", bundle_path, *specs)
        if r.returncode != 0:
            return "fetch from commits.bundle failed: " + r.stderr.strip()
        try:
            refs = [x for x in git("for-each-ref", "--format=%(objectname)", ns).stdout.split() if x]
            shas = git("rev-list", "--no-merges", *refs, "--not", self.ref).stdout.split()
            for c in shas:
                raw = git("diff-tree", "-r", "--no-commit-id", "--no-abbrev", "--no-renames", c + "^", c).stdout
                for ln in raw.splitlines():
                    meta, path = ln.split("\t", 1)
                    if self.blob_landed(path, meta.split()[3]):
                        continue
                    d = git("diff", c + "^", c, "--", path, inp=b"").stdout.decode("utf-8", "replace").splitlines()
                    if not self.lines_landed(path, [x[1:] for x in d if x.startswith("+") and not x.startswith("+++")]):
                        return "commit %s: %s, whose edit origin never held" % (c[:10], path)
            return None
        finally:
            for ref in git("for-each-ref", "--format=%(refname)", ns).stdout.split():
                git("update-ref", "-d", ref)

    def close(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


def judge(bundle, o):
    """-> ("LANDED" | "UNLANDED" | "UNJUDGED", why)."""
    names = set(os.listdir(bundle))
    known = set(DERIVED) | {"real.patch", "index.patch", "real_untracked.tar", "untracked.tar", "commits.bundle"}
    other = sorted(names - known)
    for p in ("real.patch", "index.patch"):
        if p in names:
            why = o.patch_landed(os.path.join(bundle, p))
            if why:
                return "UNLANDED", "%s: %s" % (p, why)
    if "real_untracked.tar" in names:
        left = o.tar_landed(os.path.join(bundle, "real_untracked.tar"))
        if left:
            return "UNLANDED", "%d untracked file(s) not on origin: %s" % (len(left), ", ".join(left[:4]))
    elif "untracked.tar" in names:
        return "UNJUDGED", "untracked.tar without real_untracked.tar (older bundle format)"
    if "commits.bundle" in names:
        why = o.commits_landed(os.path.join(bundle, "commits.bundle"))
        if why:
            return "UNLANDED", why
    if other:
        return "UNJUDGED", "unknown member(s): " + ", ".join(other[:4])
    return "LANDED", ""


def size(d):
    seen, n = set(), 0
    for root, _, files in os.walk(d):
        for f in files:
            st = os.lstat(os.path.join(root, f))
            if (st.st_dev, st.st_ino) not in seen:
                seen.add((st.st_dev, st.st_ino))
                n += st.st_blocks * 512
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=("judge", "prune"))
    ap.add_argument("--store", default=STORE)
    ap.add_argument("--json")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    o = Origin()
    rows = []
    try:
        for name in sorted(os.listdir(a.store)):
            d = os.path.join(a.store, name)
            if not os.path.isdir(d):
                continue
            try:
                verdict, why = judge(d, o)
            except Exception as e:  # noqa: BLE001 - one unreadable bundle is listed, never deleted
                verdict, why = "UNJUDGED", "error: %s" % str(e)
            rows.append({"bundle": name, "verdict": verdict, "why": why, "bytes": size(d)})
            print("%-9s %s %s" % (verdict, name, why), flush=True)
    finally:
        o.close()
    if a.json:
        with open(a.json, "w") as f:
            json.dump(rows, f, indent=1)
    tot = {v: (sum(1 for r in rows if r["verdict"] == v), sum(r["bytes"] for r in rows if r["verdict"] == v))
           for v in ("LANDED", "UNLANDED", "UNJUDGED")}
    print("SUMMARY " + "  ".join("%s %d (%.2f GB)" % (v, n, b / 1e9) for v, (n, b) in tot.items()))
    if a.cmd == "prune" and a.apply:
        for r in rows:
            if r["verdict"] == "LANDED":
                shutil.rmtree(os.path.join(a.store, r["bundle"]))
        print("pruned %d landed bundle(s), %.2f GB" % (tot["LANDED"][0], tot["LANDED"][1] / 1e9))
    return 0


if __name__ == "__main__":
    sys.exit(main())
