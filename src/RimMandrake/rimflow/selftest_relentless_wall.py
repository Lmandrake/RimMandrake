#!/usr/bin/env python3
"""selftest_relentless_wall.py - the Marker's wall as data and as a box. The wall in force is proved live, not here."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import relentless_wall as W     # noqa: E402

FAILS = []


def check(name, ok, got=None):
    print("%s %s" % ("ok  " if ok else "FAIL", name))
    if not ok:
        FAILS.append((name, got))


def git(d, *a):
    return subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, check=True).stdout.strip()


def repo():
    d = tempfile.mkdtemp(prefix="wallrepo")
    git(d, "init", "-q")
    git(d, "config", "user.email", "t@t")
    git(d, "config", "user.name", "t")
    for rel, body in (("a.py", "one\n"), ("conversations/c.md", "chat\n"), ("infrastructure/state/ledger/x.jsonl", "{}\n")):
        p = Path(d, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    git(d, "add", ".")
    git(d, "commit", "-qm", "base")
    Path(d, "a.py").write_text("two\n", encoding="utf-8")
    Path(d, "conversations/c.md").write_text("the seed was planted\n", encoding="utf-8")
    git(d, "add", ".")
    git(d, "commit", "-qm", "change")
    return d, git(d, "rev-parse", "HEAD")


def prof(root):
    Path(root, "kids/one").mkdir(parents=True)
    Path(root, "kids/scratch").mkdir()
    return {"enforce": False, "box_root": str(Path(root, "boxes")), "deny": ["/x/deny"], "deny_children": [str(Path(root, "kids"))],
            "tmpfs": [str(Path(root, "kids/scratch"))], "tree_exclude": ["conversations", "infrastructure/state/ledger"]}


def test_profile_and_props():
    root = tempfile.mkdtemp(prefix="wallprof")
    p = prof(root)
    rules = {"walls": {"marker": p}}
    check("a profile off is not enforced", not W.enforced(rules))
    check("no profile is not enforced", not W.enforced({}))
    check("enforce true reads", W.enforced({"walls": {"marker": dict(p, enforce=True)}}))
    d = W.denied(p, ["/store"])
    check("children denied one by one", str(Path(root, "kids/one")) in d, d)
    check("a tmpfs child is not denied", str(Path(root, "kids/scratch")) not in d, d)
    check("extra and deny are in", "/store" in d and "/x/deny" in d, d)
    Path(root, "kids/tomorrow").mkdir()
    check("a clone made later is walled at its launch", str(Path(root, "kids/tomorrow")) in W.denied(p), W.denied(p))
    o = W.props(p, "/b", ["/store"])
    check("deny property", "InaccessiblePaths=/store" in o, o)
    check("tmpfs property", "TemporaryFileSystem=" + str(Path(root, "kids/scratch")) in o, o)
    check("transcripts bound into the box", o[-1] == "BindPaths=/b/projects:%s/.claude/projects" % W.HOME, o)
    check("every property has its flag", o[0::2] == ["-p"] * (len(o) // 2), o)
    live = json.loads(Path(HERE, "relentless_rules.json").read_text(encoding="utf-8"))
    check("the live profile is report only", not W.enforced(live))


def test_box():
    root = tempfile.mkdtemp(prefix="wallbox")
    p = prof(root)
    src, sha = repo()
    box = W.make_box(p, src, sha, "n1")
    tree = Path(box, "tree")
    check("tree at the commit", (tree / "a.py").read_text(encoding="utf-8") == "two\n")
    check("no git in the box", not (tree / ".git").exists())
    check("excluded folders out", not (tree / "conversations").exists() and not (tree / "infrastructure/state/ledger").exists())
    diff = Path(box, "change.diff").read_text(encoding="utf-8")
    check("the diff holds the change", "+two" in diff, diff)
    check("the diff holds nothing excluded", "planted" not in diff and "conversations" not in diff, diff)
    check("nonce and transcript folder", Path(box, "nonce").read_text() == "n1" and Path(box, "projects").is_dir())
    txt = W.marker_prompt({"candidate": {"sha": sha, "evidence": "e"}, "contract": {"proof": ["x"]}}, "THE ITEM", box)
    check("the prompt points only into the box", box + "/verdict" in txt and "THE ITEM" in txt and "relentless.py" not in txt, txt)
    v = subprocess.run([sys.executable, box + "/verdict", "fail", 'it "broke"'], capture_output=True, text=True)
    got = W.read_verdict(box)
    check("the verdict round trips", v.returncode == 0 and got and got["word"] == "FAIL" and got["reasons"] == 'it "broke"', got)
    v = subprocess.run([sys.executable, box + "/verdict", "weak", "holds, thin proof"], capture_output=True, text=True)
    got = W.read_verdict(box)
    check("WEAK round trips", v.returncode == 0 and got and got["word"] == "WEAK", got)
    bad = subprocess.run([sys.executable, box + "/verdict", "MAYBE", "x"], capture_output=True, text=True)
    check("a bad word is refused", bad.returncode != 0)
    W.remove_box(box)
    check("the box goes", not Path(box).exists())


def test_read_verdict_malformed():
    box = tempfile.mkdtemp(prefix="wallv")
    check("no file, no verdict", W.read_verdict(box) is None)
    for name, body in (("torn", '{"word": "PA'), ("list", "[1]"), ("word", '{"word": "pass"}'), ("none", "{}")):
        Path(box, "verdict.json").write_text(body, encoding="utf-8")
        check("malformed refused: " + name, W.read_verdict(box) is None)


def test_would_deny():
    root = tempfile.mkdtemp(prefix="walld")
    p = prof(root)
    kid = str(Path(root, "kids/one"))
    check("a clean run denies nothing", W.would_deny([{"command": "python3 x.py"}], p) == [])
    check("a read in a seat clone is reported", W.would_deny([{"file_path": kid + "/a"}], p) == [kid])
    check("an excluded folder is reported", W.would_deny([{"command": "cat conversations/x"}], p) == ["conversations"])


def main():
    test_profile_and_props()
    test_box()
    test_read_verdict_malformed()
    test_would_deny()
    if FAILS:
        print(json.dumps(FAILS, default=str)[:1500])
    print("selftest_relentless_wall:", "FAIL" if FAILS else "OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
