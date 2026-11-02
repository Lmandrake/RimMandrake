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


def repo(attr=False):
    d = tempfile.mkdtemp(prefix="wallrepo")
    git(d, "init", "-q")
    git(d, "config", "user.email", "t@t")
    git(d, "config", "user.name", "t")
    for rel, body in (("a.py", "one\n"), ("conversations/c.md", "chat\n"), ("infrastructure/state/ledger/x.jsonl", "{}\n")):
        p = Path(d, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    if attr:
        Path(d, ".gitattributes").write_text("tests/proof.py export-ignore\n", encoding="utf-8")
        Path(d, "tests").mkdir()
        Path(d, "tests/proof.py").write_text("p\n", encoding="utf-8")
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
    sp = W.props({"deny": ["/srv/private data"], "tmpfs": ["/tmp/a b"]}, "/b")
    check("a path with a space stays one entry", 'InaccessiblePaths="/srv/private data"' in sp and 'TemporaryFileSystem="/tmp/a b"' in sp, sp)
    check("a quote in a path is escaped", W.unit_path('/a"b') == '"/a\\"b"' and W.unit_path("/plain") == "/plain")
    live = json.loads(Path(HERE, "relentless_rules.json").read_text(encoding="utf-8"))
    check("the live profile is enforced (RA_S03: the wall lets a correct Marker work, proved on seed cases)", W.enforced(live))


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
    d = tempfile.mkdtemp(prefix="wallsha256")
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    subprocess.run(["git", "init", "-q", "--object-format=sha256", d], check=True)
    Path(d, "a.py").write_text("one\n", encoding="utf-8")
    subprocess.run(["git", "-C", d, "add", "a.py"], check=True)
    subprocess.run(["git", "-C", d, "commit", "-qm", "root"], check=True, env=env)
    root_sha = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    box3 = W.make_box(p, d, root_sha, "n3")
    check("a sha256 root commit's diff is all of it", "+one" in Path(box3, "change.diff").read_text(encoding="utf-8"))
    W.remove_box(box3)
    src2, sha2 = repo(attr=True)
    box2 = W.make_box(p, src2, sha2, "n2")
    check("export-ignore does not drop a tracked proof", Path(box2, "tree/tests/proof.py").exists() and not Path(box2, "tree/.git").exists()
          and not Path(box2, "export.index").exists())
    W.remove_box(box2)
    check("the box goes", not Path(box).exists())


def test_skills_and_snapshot():
    root = tempfile.mkdtemp(prefix="wallskill")
    for rel in ("kids/one", "kids/wf/skills/s1", "kids/wf/other", "kids/other2", "kids/wf/tools/p", "skills", "transcripts"):
        Path(root, rel).mkdir(parents=True)
    Path(root, "kids/wf/skills/s1/SKILL.md").write_text("s\n", encoding="utf-8")
    os.symlink(str(Path(root, "kids/wf/skills/s1")), str(Path(root, "skills/s1")))
    os.symlink(str(Path(root, "kids/wf/tools/p")), str(Path(root, "skills/p")))
    p = {"enforce": False, "box_root": str(Path(root, "boxes")), "deny": [str(Path(root, "kids"))], "deny_children": [],
         "tmpfs": [], "tree_exclude": ["conversations"], "tree_from_parent": ["infrastructure/state/ledger"],
         "allow_read_skills": str(Path(root, "skills"))}
    d = W.denied(p)
    kids = str(Path(root, "kids"))
    check("a skill target is not denied", str(Path(kids, "wf/skills/s1")) not in d and str(Path(kids, "wf/tools/p")) not in d, d)
    check("a file inside a skill target is reachable", not any(x == str(Path(kids, "wf/skills/s1/SKILL.md")) for x in d), d)
    check("a sibling of the skill target stays denied", str(Path(kids, "wf/other")) in d and str(Path(kids, "other2")) in d
          and str(Path(kids, "one")) in d and str(Path(kids, "wf/tools")) not in d, d)
    check("the walled root itself is carved, not denied whole", kids not in d and str(Path(kids, "wf")) not in d, d)
    check("skill targets are read only", sorted(W.readonly(p)) == sorted([os.path.realpath(Path(kids, "wf/skills/s1")),
          os.path.realpath(Path(kids, "wf/tools/p"))]), W.readonly(p))
    o = W.props(p, "/b")
    check("read only property", "ReadOnlyPaths=" + os.path.realpath(Path(kids, "wf/skills/s1")) in o, o)
    check("nothing is writable that was denied", not set(W.readonly(p)) & set(d))
    p2 = dict(p, allow_read_skills=None)
    check("no skills key walls the root whole", W.denied(p2) == [kids] and W.readonly(p2) == [])
    live = json.loads(Path(HERE, "relentless_rules.json").read_text(encoding="utf-8"))["walls"]["marker"]
    check("the live wall lets the skills be read", live.get("allow_read_skills") == W.HOME + "/.claude/skills")
    check("the live wall still denies the builder's transcripts and scratch", "conversations" in live["tree_exclude"]
          and "/home/mandrake/.seat-tmp" in live["deny"] and "/home/mandrake/rm/scratch" in live["tmpfs"]
          and "/home/mandrake/.claude/history.jsonl" in live["deny"])
    check("the live ledger comes as a snapshot, not as tree_exclude", "infrastructure/state/ledger" not in live["tree_exclude"]
          and "infrastructure/state/ledger" in live["tree_from_parent"] and "infrastructure/state/code_review" in live["tree_from_parent"])
    check("a transcript path in a tool call is still reported", W.would_deny([{"command": "cat conversations/x.md"}], live) == ["conversations"])
    # the box: ledger as of the parent, read only; the builder's own conversation still out
    src = tempfile.mkdtemp(prefix="wallsnap")
    git(src, "init", "-q")
    git(src, "config", "user.email", "t@t")
    git(src, "config", "user.name", "t")
    for rel, body in (("a.py", "one\n"), ("conversations/c.md", "chat\n"), ("infrastructure/state/ledger/x.jsonl", "old\n")):
        q = Path(src, rel)
        q.parent.mkdir(parents=True, exist_ok=True)
        q.write_text(body, encoding="utf-8")
    git(src, "add", ".")
    git(src, "commit", "-qm", "base")
    Path(src, "a.py").write_text("two\n", encoding="utf-8")
    Path(src, "infrastructure/state/ledger/x.jsonl").write_text("new, the builder's note\n", encoding="utf-8")
    Path(src, "infrastructure/state/ledger/y.jsonl").write_text("born in the change\n", encoding="utf-8")
    git(src, "add", ".")
    git(src, "commit", "-qm", "change")
    sha = git(src, "rev-parse", "HEAD")
    box = W.make_box(p, src, sha, "n9")
    led = Path(box, "tree/infrastructure/state/ledger")
    check("the Marker's tree holds the ledger as of the parent", (led / "x.jsonl").read_text(encoding="utf-8") == "old\n"
          and not (led / "y.jsonl").exists(), list(led.glob("*")))
    check("the ledger copy is read only", not os.access(led / "x.jsonl", os.W_OK) or os.geteuid() == 0)
    check("the diff holds no ledger line", "builder's note" not in Path(box, "change.diff").read_text(encoding="utf-8"))
    check("the conversations are still out of the box", not Path(box, "tree/conversations").exists())
    W.remove_box(box)
    check("a box with read only files still goes", not Path(box).exists())


def test_read_verdict_malformed():
    box = tempfile.mkdtemp(prefix="wallv")
    check("no file, no verdict", W.read_verdict(box) is None)
    for name, body in (("torn", '{"word": "PA'), ("list", "[1]"), ("word", '{"word": "pass"}'), ("none", "{}")):
        Path(box, "verdict.json").write_text(body, encoding="utf-8")
        check("malformed refused: " + name, W.read_verdict(box) is None)
    Path(box, "verdict.json").write_text('{"word": "PASS", "at": "invalid"}', encoding="utf-8")
    got = W.read_verdict(box)
    check("a bad stamp keeps the word", got is not None and got["word"] == "PASS" and isinstance(got["at"], float))
    check("no wall profile, nothing to audit", W.audit(None, {}, None, None) == [])


def test_would_deny():
    root = tempfile.mkdtemp(prefix="walld")
    p = prof(root)
    kid = str(Path(root, "kids/one"))
    check("a clean run denies nothing", W.would_deny([{"command": "python3 x.py"}], p) == [])
    check("a read in a seat clone is reported", W.would_deny([{"file_path": kid + "/a"}], p) == [kid])
    check("an excluded folder is reported", W.would_deny([{"command": "cat conversations/x"}], p) == ["conversations"])
    q = {"deny": [], "tree_exclude": ["secret.txt"]}
    check("a quoted relative path is reported", W.would_deny([{"command": "cat 'secret.txt'"}], q) == ["secret.txt"])
    check("a longer name is not the path", W.would_deny([{"command": "cat my-secret.txt"}], q) == [])


def test_review_two():
    q = {"deny": ["/srv/private", "/srv/café"], "tree_exclude": ["secrets"]}
    check("a longer path is not the denied one", W.would_deny([{"command": "cat /srv/private-copy/f secrets-public/f"}], q) == [])
    check("a unicode path is seen", W.would_deny([{"command": "cat /srv/café/f"}], q) == ["/srv/café"])
    check("the denied path itself is seen", W.would_deny([{"command": "cat /srv/private/f"}], q) == ["/srv/private"])
    box = tempfile.mkdtemp(prefix="wallv")
    Path(box, "verdict.json").write_text('{"word": "PASS", "at": %s}' % ("1" + "0" * 400), encoding="utf-8")
    got = W.read_verdict(box)
    check("a huge stamp keeps the word", got is not None and got["word"] == "PASS")
    st = {"candidate": {"sha": "s", "evidence": "e"}, "contract": {}}
    check("a box path with a space is quoted", "python3 '/t m/n/verdict' PASS" in W.marker_prompt(st, "I", "/t m/n"))
    check("a plain box path is not", "python3 /t/n/verdict PASS" in W.marker_prompt(st, "I", "/t/n"))
    root = tempfile.mkdtemp(prefix="wallrel")
    src, sha = repo()
    cwd = os.getcwd()
    os.chdir(root)
    try:
        box = W.make_box({"box_root": "boxes", "tree_exclude": []}, src, sha, "n3")
    finally:
        os.chdir(cwd)
    root_sha = git(src, "rev-list", "--max-parents=0", "HEAD")
    b2 = W.make_box({"box_root": root, "tree_exclude": []}, src, root_sha, "n4")
    check("a root commit exports, its diff is all of it", "+one" in Path(b2, "change.diff").read_text(encoding="utf-8"))
    W.remove_box(b2)
    try:
        W.make_box({"box_root": root + "/a b", "tree_exclude": []}, src, sha, "n5")
        check("a box root with whitespace is refused", False)
    except RuntimeError:
        check("a box root with whitespace is refused", True)
    check("a path inside another is not the denied one", W.would_deny([{"command": "cat /tmp/store/f"}], {"deny": ["/store"], "tree_exclude": []}) == [])
    check("a relative box root exports", Path(box, "tree/a.py").exists() and os.path.isabs(box), box)
    W.remove_box(box)


def main():
    test_profile_and_props()
    test_box()
    test_skills_and_snapshot()
    test_read_verdict_malformed()
    test_would_deny()
    test_review_two()
    if FAILS:
        print(json.dumps(FAILS, default=str)[:1500])
    print("selftest_relentless_wall:", "FAIL" if FAILS else "OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
