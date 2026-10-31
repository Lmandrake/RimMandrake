#!/usr/bin/env python3
"""Selftest for owner_doc_lint.py, block_owner_doc_wsl_paths.py and their wiring into the two live hooks."""
import json, subprocess, sys, tempfile
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
sys.path.insert(0, str(HOOKS))
import block_owner_doc_wsl_paths as H

L = H.L
fails = 0


def check(name, ok):
    global fails
    print(("ok   " if ok else "FAIL ") + name)
    fails += not ok


for bad in ("/home/mandrake/rm/bench/x.html", "see /mnt/d/ClaudeWork/x", r"\\wsl.localhost\Ubuntu\home\x", r"\\wsl$\Ubuntu\x", "file:///D:/x.html", "(/home/m/x)"):
    check(f"refuses {bad}", L.problems(bad))
for good in (r"D:\ClaudeWork\rimmandrake\x.html", "http://localhost:51234/?t=abc", "/homework is done", "foo/home/bar", "/mnt is a word", "profile: x"):
    check(f"passes {good}", not L.problems(good))

check("a pile is an owner doc", L.is_owner_doc("/x/bench/Transient/owner_pile_2026-10-31.md"))
check("a repo pile path is an owner doc", L.is_owner_doc("Transient/owner_pile_2026-10-31.md"))
check("ClaudeWork Transient is an owner doc", L.is_owner_doc("/mnt/d/ClaudeWork/rimmandrake/Transient/foo/bar.md"))
check("windows slashes too", L.is_owner_doc(r"D:\ClaudeWork\rimmandrake\Transient\bar.html"))
check("scratch is not", not L.is_owner_doc("/mnt/d/ClaudeWork/rimmandrake/scratch/bar.md"))
check("a png is not", not L.is_owner_doc("/mnt/d/ClaudeWork/rimmandrake/Transient/a.png"))
check("design docs are not", not L.is_owner_doc("design/RimMandrake/x.md"))

PILE = "/x/Transient/owner_pile_1.md"
check("Write refused", H.findings("Write", {"file_path": PILE, "content": "/mnt/d/x"}))
check("Edit judges the new text only", H.findings("Edit", {"file_path": PILE, "new_string": "/home/m/y", "old_string": "z"}) and
      not H.findings("Edit", {"file_path": PILE, "new_string": "fine", "old_string": "/home/m/y"}))
with tempfile.TemporaryDirectory() as td:
    doc = Path(td) / "Transient" / "owner_pile_2.md"
    doc.parent.mkdir()
    doc.write_text("see /mnt/DRIVE/report.html\nold /home/m/bad\n")
    check("an edit completing a path is refused", H.findings("Edit", {"file_path": str(doc), "old_string": "DRIVE", "new_string": "d"}))
    check("a line already bad does not freeze the doc", not H.findings("Edit", {"file_path": str(doc), "old_string": "old /home/m/bad", "new_string": "gone"}) and
          not H.findings("Edit", {"file_path": str(doc), "old_string": "DRIVE", "new_string": "e-drive"}))
check("a repo Transient note is an owner doc", L.is_owner_doc("Transient/review.md"))
check("another ClaudeWork project too", L.is_owner_doc("/mnt/d/ClaudeWork/other/Transient/x.md"))
check("a sheet under Transient is not lint's business", not L.is_owner_doc("Transient/biome_ffar/a.html"))
DOC = "/mnt/d/ClaudeWork/rimmandrake/Transient/x.md"
check("heredoc into an owner doc refused", H.findings("Bash", {"command": f"cat > {DOC} <<E\nsee /home/m/x\nE"}))
check("echo into an owner doc refused", H.findings("Bash", {"command": f"echo see /mnt/d/x >> {DOC}"}))
check("its own target path does not count", not H.findings("Bash", {"command": f"cat > {DOC} <<E\nsee http://localhost:1/\nE"}))
check("a quoted target with a space", H.findings("Bash", {"command": 'cat > "/mnt/d/ClaudeWork/My Project/Transient/o.md" <<E\n/home/m/x\nE'}))
check("the same path as payload still counts", H.findings("Bash", {"command": f"echo {DOC} >> {DOC}"}))
check("heredoc elsewhere passes", not H.findings("Bash", {"command": "cat > /tmp/a.md <<E\n/home/m/x\nE"}))
check("MultiEdit refused", H.findings("MultiEdit", {"file_path": PILE, "edits": [{"new_string": "fine"}, {"new_string": "/mnt/d/x"}]}))
check("a non-owner file passes", not H.findings("Write", {"file_path": "/x/src/a.md", "content": "/mnt/d/x"}))
card = {"questions": [{"question": "open \\\\wsl.localhost\\Ubuntu\\x?", "options": [{"label": "ok"}]}]}
check("card refused", H.findings("AskUserQuestion", card))
check("clean card passes", not H.findings("AskUserQuestion", {"questions": [{"question": "open D:\\x?"}]}))


def fire(hook, ev):
    r = subprocess.run([sys.executable, str(HOOKS / hook)], input=json.dumps(ev), capture_output=True, text=True)
    return r.stdout


w = {"tool_name": "Write", "tool_input": {"file_path": PILE, "content": "/home/m/x"}}
check("live: the wired Write hook denies", "deny" in fire("block_hand_edited_sheet.py", w))
w["tool_input"]["content"] = "D:\\x"
check("live: the wired Write hook passes clean text", "deny" not in fire("block_hand_edited_sheet.py", w))
check("live: the wired card hook denies", "deny" in fire("block_delegated_cards.py", {"tool_name": "AskUserQuestion", "tool_input": card}))
sys.exit(1 if fails else 0)
