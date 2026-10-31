#!/usr/bin/env python3
"""Nothing that reaches the owner carries a path his Windows browser cannot open.

Owner, 2026-10-31: "And you provided wsl links that don't work when I try to link from the Windows browser as well."
Refused: /home/..., /mnt/<drive>/..., \\\\wsl.localhost\\..., \\\\wsl$\\... and file: links. Give a served http://localhost URL for
a sheet, and a D:\\... path for a file.

Owner-facing means an owner pile, anything under a ClaudeWork Transient folder (a human reads it once), and a question card.
Called by .claude/hooks/block_owner_doc_wsl_paths.py (before the write) and infrastructure/githooks/pre-commit (staged piles).

    python3 src/RimMandrake/Utils/owner_doc_lint.py <file>...      exit 1 and the offending lines
    python3 src/RimMandrake/Utils/owner_doc_lint.py --staged       the same over staged owner docs
"""
from __future__ import annotations

import re
import subprocess
import sys

BAD = re.compile(r"(?<![\w.-])(/home/\w|/mnt/[a-zA-Z]/)|\\\\wsl(\.localhost|\$)|\bfile:/", re.I)
DOC_EXT = (".md", ".txt", ".html", ".htm")
OWNER_DOC = re.compile(r"(^|/)Transient/[^/]+\.(md|txt)$|(^|/)Transient/owner_pile[^/]*\.\w+$|ClaudeWork/[^/]+/Transient/", re.I)
BASH_TARGET = re.compile(r""">>?\s*(?:"([^"]+)"|'([^']+)'|([^\s"'<>;|&]+))""")
FIX = "give the owner a served http://localhost URL for a sheet, or a D:\\ path for a file"


def is_owner_doc(path: str) -> bool:
    p = str(path).replace("\\", "/")
    return p.lower().endswith(DOC_EXT) and bool(OWNER_DOC.search(p))


def problems(text: str) -> list[str]:
    return [f"line {n}: {line.strip()[:120]}" for n, line in enumerate(str(text).splitlines(), 1) if BAD.search(line)]


def bash_doc_text(cmd: str) -> str:
    """What a heredoc or echo into an owner doc would write, or "". Generated output cannot be judged here; a pile still meets
    pre-commit. The target path itself is dropped, because an owner doc on D: is written through /mnt/d from WSL."""
    cmd = str(cmd)
    hit = []

    def drop(m):
        if not is_owner_doc(m.group(1) or m.group(2) or m.group(3)):
            return m.group(0)
        hit.append(m)
        return ""
    rest = BASH_TARGET.sub(drop, cmd)
    return rest if hit and re.search(r"<<|\b(echo|printf)\b", cmd) else ""


def staged() -> list[str]:
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"], capture_output=True, text=True)
    return [p for p in out.stdout.splitlines() if is_owner_doc(p)]


def staged_text(path: str) -> str:
    return subprocess.run(["git", "show", f":{path}"], capture_output=True, text=True, errors="replace").stdout


def main(argv: list[str]) -> int:
    use_index = argv[:1] == ["--staged"]
    bad = 0
    for path in staged() if use_index else argv:
        text = staged_text(path) if use_index else open(path, encoding="utf-8", errors="replace").read()
        for line in problems(text):
            print(f"{path}: {line}", file=sys.stderr)
            bad += 1
    if bad:
        print(f"REFUSED owner_doc_lint: {FIX}", file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
