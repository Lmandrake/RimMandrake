#!/usr/bin/env python3
"""serve_gated.py — the only way to start a biome art sheet server. Refuses an HTML without a valid gate stamp.

    python3 serve_gated.py --no-open --sheet <x_sheet_date>.html --decisions <x_sheet_date>.decisions.json

A sheet that declares `sheet-kind: non-art` takes the checked non-art route (nonart_sheet.py) instead of a stamp — and
that route refuses any sheet whose PICTURES are game art (game_art.classify), whatever it declares.
Same arguments as the review-sheets skill's serve_sheet.py (it is exec'd after the check). A sheet that never passed
`scaled_review_gate` (no stamp), or was edited after it (stamp mismatch), is REFUSED with exit 4 and nothing starts.
Stamp: `python3 scaled_review_gate.py check <sheet> --stamp` (stamps only a passing sheet).
FRESH OR REFUSE (ART_SHEET_REDESIGN_FRESH_OR_REFUSE): a stamped sheet any row of which no longer shows what is installed
(sheet_freshness.verify_html, re-measured from disk) is REFUSED with exit 5; a running server re-checks on every page
load and serves a refusal page in place of a sheet that went stale. There is NO override (owner, by card 2026-10-14:
remove the escape hatch): a stale sheet is never served; the only way forward is a rebuild.
"""
import hashlib
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scaled_review_gate as SG  # noqa: E402
import nonart_sheet as NA  # noqa: E402

SERVE = Path.home() / ".claude" / "skills" / "review-sheets" / "assets" / "serve_sheet.py"
READ_ONLY = ("--status", "--selftest", "--help", "-h")


def guard_ops(ops: dict, disk_decisions: dict) -> dict:
    """Server-side half of "a followed note comes off the open notes" (owner, 2026-10-08). A browser tab holding a stale
    copy of a row re-posts the note enact already followed; drop it, and carry the on-disk `notes_followed` history
    through so the post cannot erase it. A note that differs from every followed one (he typed a new one) is kept."""
    out = {}
    for row, val in ops.items():
        disk = disk_decisions.get(row) if isinstance(disk_decisions, dict) else None
        if isinstance(val, dict) and isinstance(disk, dict) and disk.get("notes_followed"):
            val = dict(val)
            past = {str(f.get("note") or "").strip() for f in disk["notes_followed"] if isinstance(f, dict)}
            if str(val.get("note") or "").strip() in past:
                val["note"] = ""
            have = val.get("notes_followed") or []
            keys = {(f.get("note"), f.get("when")) for f in have if isinstance(f, dict)}
            val["notes_followed"] = list(have) + [f for f in disk["notes_followed"] if (f.get("note"), f.get("when")) not in keys]
        out[row] = val
    return out


FRESH_MEMO_S = 5.0     # a page load never sees a measurement of the world older than this


def fresh_gate(sheet: Path):
    """Freshness on every page load (ART_SHEET_REDESIGN_FRESH_OR_REFUSE): returns a function html_bytes -> bytes that
    re-measures the sheet against disk and serves the REFUSAL page instead of a sheet any row of which is stale."""
    import sheet_freshness as FR
    memo = {"at": 0.0, "key": None, "r": None}

    def gate(html: bytes) -> bytes:
        key = hashlib.sha256(html).hexdigest()
        if memo["key"] != key or time.time() - memo["at"] > FRESH_MEMO_S:
            try:
                memo["r"] = FR.verify_html(sheet, html=html.decode("utf-8", "replace"))
            except Exception as e:      # noqa: BLE001  unmeasured is refused, never served as fresh
                memo["r"] = {"fresh": False, "rows": 0, "stale": {}, "manifest": False,
                             "error": f"freshness UNMEASURED ({type(e).__name__}: {e})"}
            memo.update(at=time.time(), key=key)
        r = memo["r"]
        if r["fresh"]:
            return html
        print(FR.report(sheet.name, r, limit=10), file=sys.stderr, flush=True)
        return FR.refusal_page(sheet.name, r)
    return gate


def serve_with_followed_guard(argv: list[str], fresh=None) -> int:
    """Run the review-sheets sidecar in-process with write_ops wrapped by guard_ops (the skill's own file stays untouched)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("serve_sheet", str(SERVE))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["serve_sheet"] = mod
    spec.loader.exec_module(mod)
    orig = mod.DecisionsFile.write_ops

    def write_ops(self, ops, force=False):
        try:
            disk = self.read().get("decisions") or {}
        except Exception:        # noqa: BLE001 - the original raises the real, typed error
            disk = {}
        return orig(self, guard_ops(ops, disk) if isinstance(ops, dict) else ops, force=force)

    mod.DecisionsFile.write_ops = write_ops
    if fresh is not None:
        orig_inject = mod.inject_sidecar

        def inject_sidecar(html, cfg):
            return orig_inject(fresh(html), cfg)
        mod.inject_sidecar = inject_sidecar
    sys.argv = [str(SERVE)] + argv
    return mod.main()


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
    if not ok and NA.declares_nonart(p.read_text()):
        # Non-art route (owner card 2026-10-09): only a sheet that DECLARES non-art, carries no art stamp, is not a biome_ffar
        # sheet, and passes check_sheet + the decisions schema. An art sheet never reaches this; see nonart_sheet.verify.
        dpath = None
        for i, a in enumerate(argv):
            if a == "--decisions" and i + 1 < len(argv):
                dpath = argv[i + 1]
            elif a.startswith("--decisions="):
                dpath = a.split("=", 1)[1]
        if not dpath:
            print("REFUSED serve_gated: non-art sheet needs --decisions to be checked", file=sys.stderr)
            return 4
        ok, msg = NA.verify(p, Path(dpath))
        if not ok:
            print(f"REFUSED serve_gated: {p.name}: non-art route: {msg}", file=sys.stderr)
            return 4
        return serve_with_followed_guard(argv)
    if not ok:
        print(f"REFUSED serve_gated: {p.name}: {msg}.\nBuild it with art_sheet.py --biome <RM_X> (gated), or stamp a sheet that "
              f"passes with `scaled_review_gate.py check {p.name} --stamp`.", file=sys.stderr)
        return 4
    # FRESH OR REFUSE (owner 2026-10-12): a stamped art sheet any row of which no longer shows what is installed is not
    # started, and a running one re-checks on every page load (a stale page is replaced by the refusal page)
    import sheet_freshness as FR
    r = FR.verify_html(p)
    if not r["fresh"]:
        print(f"REFUSED serve_gated: {FR.report(p.name, r, limit=20)}\nRebuild it (art_sheet.py with the arguments that "
              f"built it, or refresh_sheets.py); this check re-measures disk, so a rebuilt sheet serves.", file=sys.stderr)
        return 5
    return serve_with_followed_guard(argv, fresh=fresh_gate(p))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
