#!/usr/bin/env python3
"""selftest_canon_save.py — CANONICAL_SAVE.md and canon.yml name the same canonical start.

  1. the doc's lead line names the file canon_save.py resolves from canon.yml;
  2. the frozen record is a different file, and no longer called `planet.start_savegame`;
  3. the instrument sees: a doc naming the wrong start, or a yml with no start line, fails.
"""
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canon_save

DOC = os.path.join(os.path.dirname(canon_save.CANON_YML), "CANONICAL_SAVE.md")
_LEAD = re.compile(r"canonical start, what tools load by default:\s*`([^`]+\.rws)`")
_FROZEN = re.compile(r"^  frozen_record_savegame:\s*(\S+)\s*$", re.M)


def problems(doc_text, yml_text):
    """Every way the doc and the yml disagree about the canonical start."""
    found = []
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "canon.yml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(yml_text)
        try:
            start = canon_save.start_savegame_name(path)
        except RuntimeError as e:
            return [str(e)]
    lead = _LEAD.search(doc_text)
    if not lead:
        found.append("doc has no lead line naming the canonical start")
    elif lead.group(1) != start:
        found.append(f"doc lead names {lead.group(1)}, canon.yml names {start}")
    frozen = _FROZEN.search(yml_text)
    if not frozen:
        found.append("canon.yml has no planet.frozen_record_savegame")
    else:
        name = frozen.group(1)
        if name == start:
            found.append(f"frozen record and canonical start are the same file: {name}")
        if f"`{name}`" not in doc_text:
            found.append(f"doc does not name the frozen record {name}")
    if re.search(r"(?i)same file is\s+`planet\.start_savegame`", doc_text):
        found.append("doc still calls the frozen file planet.start_savegame")
    return found


def main():
    with open(DOC, encoding="utf-8") as f:
        doc = f.read()
    with open(canon_save.CANON_YML, encoding="utf-8") as f:
        yml = f.read()
    fails = []
    real = problems(doc, yml)
    if real:
        fails.append(f"live files: {real}")
    start = canon_save.start_savegame_name()
    probes = {
        "wrong start": doc.replace(f"`{start}`", "`OTHER.rws`", 1),
        "stale phrase": doc + "\nThe same file is\n`planet.start_savegame` here.\n",
    }
    for name, text in probes.items():
        if not problems(text, yml):
            fails.append(f"sanity probe saw nothing: {name}")
    if not problems(doc, yml.replace("  start_savegame:", "  start_save:")):
        fails.append("sanity probe saw nothing: yml with no start line")
    for line in fails:
        print("FAIL", line)
    print("selftest_canon_save:", "FAIL" if fails else "PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
