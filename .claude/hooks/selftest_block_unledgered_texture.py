#!/usr/bin/env python3
"""Selftest for block_unledgered_texture.py + src/RimMandrake/Utils/art/art_guard.py.

Throwaway git repo (bare remote + clone) holding one fixture mod and its own art ledger;
feeds the hook real commit/publish/push commands and the git-native --git-pre-push mode.
Proves it bites on a raw write into Textures/ and passes an `install_bytes` write.

    python3 .claude/hooks/selftest_block_unledgered_texture.py
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "block_unledgered_texture.py")
REPO = os.path.dirname(os.path.dirname(HERE))
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def png(color):
    from PIL import Image
    b = io.BytesIO()
    Image.new("RGBA", (8, 8), color).save(b, "PNG")
    return b.getvalue()


def git(cwd, *a):
    r = subprocess.run(["git", "-C", cwd, *a], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr))
    return r.stdout


def hook(cmd, cwd):
    r = subprocess.run([sys.executable, HOOK], input=json.dumps({"tool_input": {"command": cmd}, "cwd": cwd}),
                       capture_output=True, text=True, timeout=120)
    out = r.stdout.strip()
    return ("deny" if out and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny" else "allow"), out


def prepush(cwd, local_sha, remote_sha):
    line = "refs/heads/main %s refs/heads/main %s\n" % (local_sha, remote_sha)
    r = subprocess.run([sys.executable, HOOK, "--git-pre-push"], input=line, cwd=cwd,
                       capture_output=True, text=True, timeout=120)
    return r.returncode


def main():
    tmp = tempfile.mkdtemp(prefix="art-guard-selftest-")
    try:
        remote, clone = os.path.join(tmp, "remote.git"), os.path.join(tmp, "clone")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", remote], check=True)
        subprocess.run(["git", "clone", "-q", remote, clone], check=True, capture_output=True)
        git(clone, "config", "user.email", "t@t")
        git(clone, "config", "user.name", "t")
        git(clone, "config", "core.hooksPath", "/dev/null")
        os.environ["ARTSTORE"] = os.path.join(tmp, "store")
        os.environ["ART_LEDGER_DIR"] = os.path.join(clone, "infrastructure", "state", "art")
        os.environ["ART_SRC_ROOT"] = os.path.join(clone, "src")
        os.environ["ART_SEAT"] = "BENCH"
        os.environ.pop("RIMFLOW_SEAT", None)
        sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "art"))
        import artledger as L

        tex = os.path.join(clone, "src", "FixMod", "Textures", "Things", "Beast")
        os.makedirs(tex)
        with open(os.path.join(clone, "README"), "w") as fh:
            fh.write("x\n")
        git(clone, "add", "README")
        git(clone, "commit", "-qm", "init")
        git(clone, "push", "-q", "origin", "HEAD:main")
        base = git(clone, "rev-parse", "HEAD").strip()
        red, blue, green = png((255, 0, 0, 255)), png((0, 0, 255, 255)), png((0, 255, 0, 255))
        raw = os.path.join(tex, "Raw_south.png")
        rel_raw = "src/FixMod/Textures/Things/Beast/Raw_south.png"
        shard = "infrastructure/state/art/events/BENCH.jsonl"

        # 1. a raw write into Textures, pathspec commit -> refused
        with open(raw, "wb") as fh:
            fh.write(red)
        v, out = hook("git commit %s -m raw" % rel_raw, clone)
        check(v == "deny" and "no art-ledger record" in out, "raw write + pathspec commit refused")
        v, _ = hook("./publish -m raw %s" % rel_raw, clone)
        check(v == "deny", "raw write + ./publish refused")
        git(clone, "add", rel_raw)
        v, _ = hook("git commit -m raw", clone)
        check(v == "deny", "raw write + index commit refused")
        git(clone, "reset", "-q", "--", rel_raw)
        os.unlink(raw)

        # 2. install_bytes -> allowed, but only together with its ledger shard
        dest = os.path.join(tex, "Beast_south.png")
        rel = "src/FixMod/Textures/Things/Beast/Beast_south.png"
        r = L.install_bytes(dest, red, reason="script:selftest")
        check(r["status"] == "installed", "install_bytes installs on a mechanical reason")
        v, out = hook("./publish -m art %s" % rel, clone)
        check(v == "deny" and "art-ledger lines behind" in out, "ledgered PNG without its shard refused")
        v, out = hook("./publish -m art %s %s" % (rel, shard), clone)
        check(v == "allow", "ledgered PNG + shard allowed (%s)" % out[:200])
        v, _ = hook("git commit -m art -- %s infrastructure" % rel, clone)
        check(v == "allow", "pathspec commit naming a parent dir of the shard allowed")
        git(clone, "add", rel, shard)
        git(clone, "commit", "-qm", "art")
        head = git(clone, "rev-parse", "HEAD").strip()
        v, out = hook("git push origin HEAD:main", clone)
        check(v == "allow", "push of an install commit allowed (%s)" % out[:200])
        check(prepush(clone, head, base) == 0, "pre-push passes an install commit")

        # 3. a second install chained twice before one commit: chain walk
        L.install_bytes(dest, blue, reason="script:selftest")
        L.install_bytes(dest, green, reason="script:selftest")
        v, out = hook("./publish -m art2 %s %s" % (rel, shard), clone)
        check(v == "allow", "two chained installs before one commit allowed (%s)" % out[:200])
        git(clone, "add", rel, shard)
        git(clone, "commit", "-qm", "art2")

        # 4. a raw overwrite of a ledgered file -> refused at commit, push and pre-push
        with open(dest, "wb") as fh:
            fh.write(red + b"\0")
        v, out = hook("git commit -m over -- %s" % rel, clone)
        check(v == "deny" and "no `live` event" in out, "raw overwrite of a ledgered file refused")
        git(clone, "add", rel)
        git(clone, "commit", "-qm", "over")
        h2 = git(clone, "rev-parse", "HEAD").strip()
        v, _ = hook("git push origin HEAD:main", clone)
        check(v == "deny", "push carrying a raw overwrite refused")
        v, _ = hook("./publish", clone)
        check(v == "deny", "bare ./publish (push) carrying a raw overwrite refused")
        check(prepush(clone, h2, base) == 1, "git-native pre-push refuses a raw overwrite")
        git(clone, "reset", "-q", "--soft", "HEAD~1")
        git(clone, "reset", "-q", "--", rel)
        git(clone, "checkout", "-q", "--", rel)

        # 5. a hand-appended live line that skips the committed picture -> refused
        sg = L.sha256_bytes(green)
        bad = L.sha256_bytes(blue + b"x")
        L.store_put_bytes(blue + b"x")
        L.append({"type": "live", "mod": "src/FixMod", "rel": "Things/Beast/Beast_south.png",
                  "sha": bad, "prev": "f" * 64, "reason": "script:hand"})
        with open(dest, "wb") as fh:
            fh.write(blue + b"x")
        v, out = hook("git commit -m skip -- %s %s" % (rel, shard), clone)
        check(v == "deny" and "chain breaks" in out, "hand-appended live skipping a transition refused")
        git(clone, "checkout", "-q", "--", rel, shard)

        # 6. owner-kept picture: mechanical install refused; hand-appended mechanical live refused
        L.append({"type": "ruling", "id": "keepgreen", "target": {"sha": sg}, "verdict": "keep",
                  "by": "owner", "trust": "ruled", "said": "fixture"})
        try:
            L.install_bytes(dest, red, reason="script:selftest")
            check(False, "mechanical install over an owner-kept picture refused")
        except L.Refused:
            check(True, "mechanical install over an owner-kept picture refused")
        L.append({"type": "live", "mod": "src/FixMod", "rel": "Things/Beast/Beast_south.png",
                  "sha": L.sha256_bytes(red), "prev": sg, "reason": "script:hand"})
        with open(dest, "wb") as fh:
            fh.write(red)
        v, out = hook("git commit -m k -- %s %s" % (rel, shard), clone)
        check(v == "deny" and "owner-kept" in out, "hand-appended mechanical live over a keep refused")
        git(clone, "checkout", "-q", "--", rel, shard)

        # 7. retire through the ledger -> deletion allowed; raw delete refused
        os.unlink(dest)
        v, _ = hook("git commit -m del -- %s" % rel, clone)
        check(v == "deny", "raw delete of a ledgered file refused")
        git(clone, "checkout", "-q", "--", rel)
        L.append({"type": "ruling", "id": "rel", "verdict": "release", "releases": "keepgreen",
                  "by": "owner", "trust": "ruled", "target": {"sha": sg}})
        r = L.retire(dest, reason="script:selftest")
        check(r["status"] == "retired", "retire archives and removes")
        v, out = hook("git commit -m del -- %s %s" % (rel, shard), clone)
        check(v == "allow", "ledger retire + commit allowed (%s)" % out[:200])

        # 8. commits that touch no PNG are never examined; unparseable ledger fails closed on PNGs
        v, _ = hook("git commit -m readme -- README", clone)
        check(v == "allow", "non-texture commit untouched")
        with open(os.path.join(clone, shard), "a") as fh:
            fh.write("{not json\n")
        v, out = hook("git commit -m del -- %s %s" % (rel, shard), clone)
        check(v == "deny" and "could not be read" in out, "unparseable ledger fails CLOSED for a PNG commit")
        v, _ = hook("git commit -m readme -- README", clone)
        check(v == "allow", "unparseable ledger leaves a non-PNG commit alone")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\nALL PASS" if not FAILS else "\n%d FAIL" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
