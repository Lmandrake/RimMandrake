#!/usr/bin/env python3
"""selftest_relentless_wall_base_diff.py - MARKER_DIFF_FIX_EARLIER_WORK_LOOKS_EMPTY: the Marker's change.diff covers the
item's work since its base, not only the candidate commit. The work lands in commit A, another seat's commit lands, then
the candidate is a report commit B: sha^..sha showed only B, so the blind checker read "no change"."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent / "Utils"))
from selftest_own_dirs import own_dir_for_run  # noqa: E402
own_dir_for_run("relentless_wall_base_diff")
import relentless_wall as W     # noqa: E402

ITEM = "THING_FIX_REPORT_LANDS_LAST"
FAILS = []


def check(name, ok, got=None):
    print("%s %s" % ("ok  " if ok else "FAIL", name))
    if not ok:
        FAILS.append((name, got))


def git(d, *a):
    return subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, check=True).stdout.strip()


def commit(d, files, msg):
    for rel, body in files.items():
        p = Path(d, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    git(d, "add", *files)
    git(d, "commit", "-qm", msg)
    return git(d, "rev-parse", "HEAD")


def repo():
    d = tempfile.mkdtemp(prefix="wallbase")
    git(d, "init", "-q")
    git(d, "config", "user.email", "t@t")
    git(d, "config", "user.name", "t")
    base = commit(d, {"fix.py": "old\n", "other.py": "o1\n", "infrastructure/state/ledger/x.jsonl": "{}\n",
                      "conversations/c.md": "chat\n"}, "base")
    work = commit(d, {"fix.py": "new\n", "conversations/c.md": "planted\n"}, "%s: the fix" % ITEM)
    commit(d, {"other.py": "o2 by another seat\n"}, "SOMEONE_ELSE: unrelated")
    report = commit(d, {"docs/report.md": "proof notes\n"}, "%s: report" % ITEM)
    return d, base, work, report


def prof(root):
    return {"enforce": False, "box_root": str(Path(root, "boxes")), "tree_exclude": ["conversations"],
            "tree_from_parent": ["infrastructure/state/ledger"]}


def main():
    root = tempfile.mkdtemp(prefix="wallbaseprof")
    p = prof(root)
    src, base, work, report = repo()

    old = W.make_box(p, src, report, "b0")
    od = Path(old, "change.diff").read_text(encoding="utf-8")
    check("instance: without the base the fix is invisible (sha^..sha)", "+new" not in od and "+proof notes" in od, od)

    box = W.make_box(p, src, report, "b1", base=base, item=ITEM)
    d = Path(box, "change.diff").read_text(encoding="utf-8")
    check("the earlier commit's work is in change.diff", "+new" in d and "-old" in d, d)
    check("the candidate's own change is in change.diff", "+proof notes" in d, d)
    check("another seat's commit since base stays out", "other.py" not in d, d)
    check("tree_exclude still holds", "planted" not in d and "conversations" not in d, d)
    check("tree is still at the candidate", Path(box, "tree/fix.py").read_text(encoding="utf-8") == "new\n")

    same = W.make_box(p, src, report, "b2", base=report, item=ITEM)
    check("base == sha falls back to sha^..sha",
          Path(same, "change.diff").read_text(encoding="utf-8") == od)
    gone = W.make_box(p, src, report, "b3", base="0" * 40, item=ITEM)
    check("an unknown base falls back", Path(gone, "change.diff").read_text(encoding="utf-8") == od)
    noitem = W.make_box(p, src, report, "b4", base=base)
    check("no item id falls back", Path(noitem, "change.diff").read_text(encoding="utf-8") == od)
    check("change_range of a non-ancestor base is the parent",
          W.change_range(src, report + "^", base, report, ITEM) == (report + "^", None))
    frm, only = W.change_range(src, report + "^", report, base, ITEM)
    check("change_range names the base and the item's paths",
          frm == base and only == [":(literal)conversations/c.md", ":(literal)docs/report.md", ":(literal)fix.py"], (frm, only))
    for b in (old, box, same, gone, noitem):
        W.remove_box(b)
    if FAILS:
        print(json.dumps(FAILS, default=str)[:1500])
    print("selftest_relentless_wall_base_diff:", "FAIL" if FAILS else "OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
