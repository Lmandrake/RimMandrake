#!/usr/bin/env python3
"""doc_claims.py - split a doctrine file into atomic, numbered CLAIMS.

The point is that two independent assessments judge the SAME list. If each side
re-reads the prose, they are grading different things and their agreement means
nothing. So extraction is mechanical and deterministic here, and judgement is not.

A claim is one directive or one fact. Headings, code fences and tables are carried
as single units because splitting them destroys their meaning.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path


def claims(text: str):
    out, buf, in_fence, fence_hdr = [], [], False, None
    heading = ""
    in_table = False

    def flush(kind="prose"):
        nonlocal buf, in_table
        body = "\n".join(buf).strip()
        buf = []
        was_table, in_table = in_table, False
        if not body:
            return
        if kind == "prose" and was_table:
            kind = "table"
        if kind == "prose":
            # one claim per sentence-ish bullet or paragraph line
            for part in re.split(r"(?<=[.!?])\s+(?=[A-Z🔴⛔✅⚠️🔑⭐📌])", body):
                part = part.strip()
                if len(part) > 3:
                    out.append({"heading": heading, "kind": "prose", "text": part})
        else:
            out.append({"heading": heading, "kind": kind, "text": body})

    for line in text.split("\n"):
        if line.strip().startswith("```"):
            if in_fence:
                buf.append(line); flush("code"); in_fence = False
            else:
                flush(); buf.append(line); in_fence = True
            continue
        if in_fence:
            buf.append(line); continue
        if line.startswith("#"):
            flush(); heading = line.lstrip("#").strip(); continue
        if line.strip().startswith("|"):
            buf.append(line); in_table = True; continue
        if not line.strip():
            flush(); continue
        buf.append(line)
    flush()

    for i, c in enumerate(out, 1):
        c["id"] = i
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--out")
    a = ap.parse_args()
    src = Path(a.path)
    cs = claims(src.read_text(encoding="utf-8"))
    payload = {"file": str(src), "claimCount": len(cs), "claims": cs}
    if a.out:
        Path(a.out).write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{src}: {len(cs)} claims")
    return 0


if __name__ == "__main__":
    sys.exit(main())
