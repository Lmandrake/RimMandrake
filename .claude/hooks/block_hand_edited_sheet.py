#!/usr/bin/env python3
"""PreToolUse (Bash|Write|Edit|MultiEdit): a biome art sheet is only ever produced by the GATED tools.

Owner, 2026-10-05: "Add hooks to the scaled image review sheet so it MUST pass its requirements to be generated."
Spec: skills/scaled-game-image-review/SKILL.md. The instrument is
`src/RimMandrake/Utils/art/scaled_review_gate.py`, run by `art_sheet.py --biome` / `refresh_sheets.py`; servers start only
through `src/RimMandrake/Utils/art/serve_gated.py`, which refuses an HTML without a valid gate stamp.

Refused here:
  * Write/Edit/MultiEdit on Transient/biome_ffar/*_sheet_*.html
  * a Bash command that writes, edits, copies over, moves or deletes such a file (redirect, sed -i, tee, cp, mv, rm,
    python write_text/open(...,'w'), perl -i, truncate ...) unless it runs a gated tool itself
  * a Bash command that starts review-sheets' serve_sheet.py for a sheet (use serve_gated.py)

Reading (cat, grep, ls, head, git add/commit of the file) is fine. Fail open on unreadable input.

    python3 .claude/hooks/selftest_block_hand_edited_sheet.py
"""
import json
import re
import sys

SHEET = r"[\w./\\:~-]*biome_ffar[\w./\\-]*_sheet_[\w.-]*\.html"
SHEET_PATH = re.compile(SHEET)
GATED_TOOLS = re.compile(r"\b(art_sheet\.py|refresh_sheets\.py|scaled_review_gate\.py|serve_gated\.py)\b")
WRITE_VERB = re.compile(
    r"(>>?\s*[\"']?" + SHEET + r"|\bsed\s+(-[A-Za-z]*i|--in-place)|\bperl\s+-[A-Za-z]*i|(?:^|[;&|(]|\bsudo)\s*(?:tee|cp|mv|rm|truncate|dd|install)\b|"
    r"\bwrite_text\b|\bwrite_bytes\b|open\([^)]*[\"'][wa]b?\+?[\"']|\bshutil\.(copy|move)|\bos\.(replace|rename|remove|unlink)\b|"
    r"\bgit\s+(checkout|restore)\b)")
SERVER = re.compile(r"\bserve_sheet\.py\b")
SERVER_READONLY = re.compile(r"--(status|selftest|help)\b")

REASON = (
    "Blocked: a biome art sheet (Transient/biome_ffar/*_sheet_*.html) may only be produced by the gated tools "
    "(owner, 2026-10-05: the scaled-image review sheet MUST pass its requirements to be generated).\n\n"
    "The instrument is src/RimMandrake/Utils/art/scaled_review_gate.py (spec: skills/scaled-game-image-review/SKILL.md). "
    "It runs inside `python3 src/RimMandrake/Utils/art/art_sheet.py --biome <RM_X>` and `refresh_sheets.py`, which build to a "
    "temp file, check all 12 rulings, and only then replace the sheet (stamped); a failing sheet is never written and the last "
    "good one stays. Servers start only through `python3 src/RimMandrake/Utils/art/serve_gated.py --sheet <html> --decisions <json>`, "
    "which refuses an HTML without a valid stamp.\n\n"
    "If the tool fails a requirement, fix the TOOL and add a selftest — never patch one HTML file. To check a sheet: "
    "`python3 src/RimMandrake/Utils/art/scaled_review_gate.py check <html>`."
)


def deny():
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": REASON}}))


def refused(tool: str, ti: dict) -> bool:
    if tool in ("Write", "Edit", "MultiEdit"):
        return bool(SHEET_PATH.fullmatch(str(ti.get("file_path") or "").replace("\\", "/")) or
                    re.search(r"biome_ffar/[^/]*_sheet_[^/]*\.html$", str(ti.get("file_path") or "").replace("\\", "/")))
    if tool == "Bash":
        cmd = str(ti.get("command") or "")
        if SERVER.search(cmd) and not SERVER_READONLY.search(cmd) and "serve_gated.py" not in cmd:
            return True
        if SHEET_PATH.search(cmd) and WRITE_VERB.search(cmd) and not GATED_TOOLS.search(cmd):
            return True
    return False


def main() -> int:
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return 0
    if refused(ev.get("tool_name", ""), ev.get("tool_input") or {}):
        deny()
    return 0


if __name__ == "__main__":
    sys.exit(main())
