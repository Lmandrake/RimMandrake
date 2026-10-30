#!/usr/bin/env python3
"""selftest_arena_git_stragglers.py - ARENA_GIT_FETCHES_AUDIT_STRAGGLERS: every git call on a BUILDER-controlled clone
goes through arena_safe_git. Each site: a trap planted in a throwaway clone (arena_safe_git_traps), plain git shown
fooled (a marker file, or a wrong answer), the migrated call not. Run against the pre-migration files these are red.

  arena.clone_dirt        fsmonitor + filter + include.path fsmonitor + uploadpack/sshCommand (fetch): no marker
  arena.remote_refresh    uploadpack: plain `git fetch origin` runs it, the migrated fetch does not (and still fetches)
  arena.remote_refresh    url.*.insteadOf: refused (fail closed: RemoteUnreachable)
  arena_replay.audit_clone  replace ref: plain `rev-parse F^{commit}` finds an object the store does not hold
  arena_tasks._cat_batch  replace ref: plain `cat-file --batch` shows other content than the object holds
  v3_control / trio_loop  go through SG.git_run (spy) and still refuse/export correctly under replace + graft
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arena_safe_git as SG  # noqa: E402
import arena_safe_git_traps as T  # noqa: E402
import arena as AR  # noqa: E402
import arena_replay as R  # noqa: E402
import arena_tasks as AT  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def with_origin(root, name, traps):
    """A builder clone with a bare origin one commit ahead, `traps` planted -> (repo, a, b, markers)."""
    repo, a, b = T.make_repo(root, name)
    bare = Path(root) / (name + "_origin.git")
    subprocess.run(["git", "clone", "-q", "--bare", str(repo), str(bare)], check=True, capture_output=True, env=T.ENV)
    T.git(repo, "remote", "add", "origin", str(bare))
    T.git(repo, "fetch", "-q", "origin")
    mk = T.plant(repo, a, b, traps)
    for f in Path(mk).iterdir():                      # setup itself may have fired a trap: only later firings count
        f.unlink()
    (repo / "dirty.txt").write_text("x\n")            # an untracked + a modified file: status reads the index
    (repo / "g.txt").write_text("changed\n")
    return repo, a, b, mk


def main():
    with tempfile.TemporaryDirectory(prefix="stragglers_") as td:
        td = Path(td)
        # ---- arena.clone_dirt: status/for-each-ref/rev-list on the builder's clone
        repo, a, b, mk = with_origin(td, "dirt", ("fsmonitor", "filter", "hooksPath", "uploadpack", "sshCommand"))
        T.plain(repo, "status", "--porcelain")
        check("fsmonitor" in T.fired(mk), "control: plain `git status` runs the planted fsmonitor")
        for f in Path(mk).iterdir():
            f.unlink()
        try:
            out = AR.clone_dirt(repo, refresh=False)
        except Exception as e:                        # noqa: BLE001
            out = [{"what": "EXC %r" % e}]
        check(not T.fired(mk), "clone_dirt runs no planted code (fired: %s)" % T.fired(mk))
        check(any("dirty.txt" in o["what"] for o in out), "clone_dirt still reports the untracked file")

        # ---- include.path hiding an fsmonitor
        repo2, a2, b2, mk2 = with_origin(td, "incl", ())
        inc = td / "incl.cfg"
        inc.write_text("[core]\n\tfsmonitor = %s\n" % T._script(td / "incl_fsm.sh", "touch '%s/include'\nexit 1\n" % mk2))
        T.git(repo2, "config", "include.path", str(inc))
        T.plain(repo2, "status", "--porcelain")
        check("include" in T.fired(mk2), "control: plain status runs an fsmonitor named by include.path")
        for f in Path(mk2).iterdir():
            f.unlink()
        AR.clone_dirt(repo2, refresh=False)
        check(not T.fired(mk2), "clone_dirt: include.path fsmonitor does not run (fired: %s)" % T.fired(mk2))

        # ---- remote_refresh: fetch + ls-remote with uploadpack / sshCommand planted
        repo3, a3, b3, mk3 = with_origin(td, "net", ("uploadpack", "sshCommand"))
        subprocess.run(["git", "-C", str(repo3), "fetch", "-q", "origin"], capture_output=True, env=T.ENV)
        check("uploadpack" in T.fired(mk3), "control: plain `git fetch origin` runs remote.origin.uploadpack")
        for f in Path(mk3).iterdir():
            f.unlink()
        try:
            tags = AR.remote_refresh(repo3)
            ok = isinstance(tags, dict)
        except Exception as e:                        # noqa: BLE001
            ok = False
            print("      remote_refresh raised %r" % e)
        check(ok and not T.fired(mk3), "remote_refresh: fetch + ls-remote succeed and run no planted code (fired: %s)" % T.fired(mk3))
        try:
            AR.remote_arm_refs(repo3, "v3")
            ok = True
        except AR.RemoteUnreachable:
            ok = True                                 # no refs there is fine; unreachable only if the call itself broke
        except Exception as e:                        # noqa: BLE001
            ok = False
            print("      remote_arm_refs raised %r" % e)
        check(ok and not T.fired(mk3), "remote_arm_refs runs no planted code (fired: %s)" % T.fired(mk3))

        # ---- url.insteadOf: the clone redirects URLs -> refused, fail closed
        repo4, *_ = with_origin(td, "redir", ())
        T.git(repo4, "config", "url.file:///nonexistent/.insteadOf", "file://" + str(td))
        try:
            AR.remote_refresh(repo4)
            refused = False
        except AR.RemoteUnreachable:
            refused = True
        check(refused, "remote_refresh refuses a clone with url.*.insteadOf (RemoteUnreachable)")

        # ---- arena_replay.audit_clone: replace ref makes an absent sha look present
        rp, a5, b5 = T.make_repo(td, "audit")
        absent = "e" * 40
        T.git(rp, "replace", "-f", absent, b5, check=False)   # replace needs the object to exist: write the ref by hand
        refs = rp / ".git" / "refs" / "replace"
        refs.mkdir(parents=True, exist_ok=True)
        (refs / absent).write_text(b5 + "\n")
        plain = subprocess.run(["git", "-C", str(rp), "rev-parse", "--verify", "-q", absent + "^{commit}"],
                               capture_output=True, text=True, env=T.ENV)
        check(plain.returncode == 0, "control: plain rev-parse finds an absent sha through a replace ref")
        findings = R.audit_clone(rp, [absent])
        check(not any("rev-parse finds" in f or "cat-file -e finds" in f for f in findings),
              "audit_clone ignores replace refs (findings: %s)" % findings)

        # ---- arena_tasks._cat_batch: replace ref changes what an object reads as
        rt, a6, b6 = T.make_repo(td, "tasks")
        T.plant(rt, a6, b6, ("replace",))
        real = subprocess.run(["git", "-C", str(rt), "cat-file", "commit", b6], capture_output=True, text=True,
                              env=dict(T.ENV, GIT_NO_REPLACE_OBJECTS="1")).stdout
        fooled = subprocess.run(["git", "-C", str(rt), "cat-file", "commit", b6], capture_output=True, text=True,
                                env=T.ENV).stdout
        check(fooled != real, "control: plain cat-file shows the replacement for the object")
        got = {o: d for o, t, d in AT._cat_batch(rt / ".git", [b6])}
        check(got.get(b6, b"").decode() == real, "_cat_batch returns the object's own content, not the replacement")

        # ---- v3_control / trio_loop go through SG.git_run
        import v3_control as V3
        import trio_loop as TL
        calls = []
        orig = SG.git_run

        def spy(root, *a, **kw):
            calls.append(a[0] if a else "")
            return orig(root, *a, **kw)
        SG.git_run = spy
        try:
            rv, a7, b7 = T.make_repo(td, "v3")
            T.plant(rv, a7, b7, ("replace", "graft", "fsmonitor", "filter", "hooksPath"))
            dest = td / "v3_export"
            V3.export_tree(rv, b7, dest)
            check((dest / "f.txt").read_text() == "beta\n", "v3_control.export_tree exports the real tree under replace/graft")
            check("ls-tree" in calls and "cat-file" in calls, "v3_control git calls go through SG.git_run (%s)" % sorted(set(calls)))
            # a forged loose blob (other bytes under f.txt's object name): export_tree must refuse, as ralph_a's does
            import zlib
            rf, a8, b8 = T.make_repo(td, "v3forge")
            blob = T.git(rf, "rev-parse", b8 + ":f.txt").strip()
            op = rf / ".git" / "objects" / blob[:2] / blob[2:]
            op.chmod(0o644)
            op.write_bytes(zlib.compress(b"blob 6\0EVIL!\n"))
            try:
                V3.export_tree(rf, b8, td / "v3_forged")
                refused = False
            except V3.Refused:
                refused = True
            check(refused, "v3_control.export_tree refuses a tree holding a forged blob")
            # a filter planted in the clone: v3 safe_git status must not run it
            rs, a9, b9 = T.make_repo(td, "v3filt")
            mks = T.plant(rs, a9, b9, ("filter",))
            (rs / "f.txt").write_text("dirty\n")
            for f in Path(mks).iterdir():
                f.unlink()
            V3.safe_git(rs, "status", "--porcelain")
            check(not T.fired(mks), "v3_control.safe_git status runs no planted filter (fired: %s)" % T.fired(mks))
            calls.clear()
            lp = TL.RA.SG.git_run(rv, "cat-file", "-e", b7 + "^{commit}", capture_output=True)
            check(lp.returncode == 0, "SG.git_run cat-file -e works on the trio root")
            import inspect
            src = inspect.getsource(TL)
            check('["git", "-C", str(self.root), "cat-file"' not in src and '["git", "-C", str(self.root), "merge-base"' not in src,
                  "trio_loop recover has no plain git on the builder clone")
        finally:
            SG.git_run = orig
    print("\n%s" % ("ALL OK" if not FAILS else "FAILED: %d" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
