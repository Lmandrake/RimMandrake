#!/usr/bin/env python3
"""An owner doc or card never carries a WSL path: called from the hooks already wired for those tools.

block_hand_edited_sheet.py (Write|Edit|MultiEdit) and block_delegated_cards.py (AskUserQuestion) call refuse(ev), so this
needs no line of its own in settings.json. The rule and its pattern live in src/RimMandrake/Utils/owner_doc_lint.py.

    python3 .claude/hooks/selftest_owner_doc_lint.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src", "RimMandrake", "Utils"))
import owner_doc_lint as L  # noqa: E402


def after_edit(ti: dict) -> list:
    """Lines the edit would bring into being, judged whole: a fragment can complete a path, and a line already bad stays
    someone else's to fix rather than freezing the document."""
    try:
        old = open(ti.get("file_path") or "", encoding="utf-8", errors="replace").read()
    except OSError:
        old = ""
    edits = ti.get("edits") if isinstance(ti.get("edits"), list) else [ti]
    new = old
    for e in edits:
        a, b = str(e.get("old_string") or ""), str(e.get("new_string") or "")
        new = new.replace(a, b) if a and a in new else new + "\n" + b
    return L.problems("\n".join(sorted(set(new.splitlines()) - set(old.splitlines()))))


def findings(tool: str, ti: dict) -> list:
    if tool == "AskUserQuestion":
        return L.problems(json.dumps(ti, ensure_ascii=False).replace("\\\\", "\\").replace("\\n", "\n"))
    if tool == "Bash":
        return L.problems(L.bash_doc_text(ti.get("command") or ""))
    if tool in ("Write", "Edit", "MultiEdit") and L.is_owner_doc(ti.get("file_path") or ""):
        return L.problems(ti.get("content")) if tool == "Write" else after_edit(ti)
    return []


def refuse(ev: dict) -> bool:
    """Print the deny and return True if this event is refused. Fails open: a broken lint never stops a write."""
    try:
        bad = findings(ev.get("tool_name", ""), ev.get("tool_input") or {})
    except Exception:       # noqa: BLE001
        return False
    if bad:
        why = "Blocked: this reaches the owner and holds a path his Windows browser cannot open: " + "; ".join(bad[:3]) + ". " + L.FIX + "."
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": why}}))
    return bool(bad)
