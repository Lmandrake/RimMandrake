#!/usr/bin/env python3
"""serve_gated.py — the only way to start a biome art sheet server. Refuses an HTML without a valid gate stamp.

    python3 serve_gated.py --no-open --sheet <x_sheet_date>.html --decisions <x_sheet_date>.decisions.json

Same arguments as the review-sheets skill's serve_sheet.py (it is exec'd after the check). A sheet that never passed
`scaled_review_gate` (no stamp), or was edited after it (stamp mismatch), is REFUSED with exit 4 and nothing starts.
Stamp: `python3 scaled_review_gate.py check <sheet> --stamp` (stamps only a passing sheet).
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scaled_review_gate as SG  # noqa: E402

SERVE = Path.home() / ".claude" / "skills" / "review-sheets" / "assets" / "serve_sheet.py"
READ_ONLY = ("--status", "--selftest", "--help", "-h")


def main(argv: list[str]) -> int:
    if any(a in READ_ONLY for a in argv):
        os.execv(sys.executable, [sys.executable, str(SERVE)] + argv)
    sheet = None
    for i, a in enumerate(argv):
        if a == "--sheet" and i + 1 < len(argv):
            sheet = argv[i + 1]
        elif a.startswith("--sheet="):
            sheet = a.split("=", 1)[1]
    if not sheet:
        print("REFUSED serve_gated: no --sheet given, so no gate stamp could be checked", file=sys.stderr)
        return 4
    p = Path(sheet)
    if not p.is_file():
        print(f"REFUSED serve_gated: {p} does not exist", file=sys.stderr)
        return 4
    ok, msg = SG.verify_stamp(p.read_text())
    if not ok:
        print(f"REFUSED serve_gated: {p.name}: {msg}.\nBuild it with art_sheet.py --biome <RM_X> (gated), or stamp a sheet that "
              f"passes with `scaled_review_gate.py check {p.name} --stamp`.", file=sys.stderr)
        return 4
    os.execv(sys.executable, [sys.executable, str(SERVE)] + argv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
