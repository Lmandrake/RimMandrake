#!/usr/bin/env python3
"""selftest_prereview.py — nothing reaches the owner unread (owner, 2026-10-22). The record's own checks (prereview.py
--selftest), and the wiring: serve_gated, sheet_to_artifact and review_queue.serve each refuse a sheet with no complete
pre-review record before anything is served or written, and let a pre-reviewed one through."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import prereview as PR  # noqa: E402

FAILS = []


def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        FAILS.append(m)


def sheet_html(items):
    return '<html><head><style>body{}</style></head><body><script id="ITEMS" type="application/json">' + json.dumps(items) + "</script></body></html>"


def complete(sp: Path):
    PR.init(sp, "seat:SELFTEST")
    rp = PR.record_path(sp)
    rec = json.loads(rp.read_text())
    for e in rec["rows"].values():
        e["verdict"] = "OK"
    rec["caught"] = "nothing"
    rp.write_text(json.dumps(rec))


def main() -> int:
    r = subprocess.run([sys.executable, str(HERE / "prereview.py"), "--selftest"], capture_output=True, text=True, timeout=60)
    check(r.returncode == 0 and "GREEN" in r.stdout, "prereview.py --selftest GREEN" + ("" if r.returncode == 0 else ": " + r.stdout[-300:]))

    import serve_gated as SV
    items = [{"id": "R1", "label": "hose reel", "graphics": [{"res": "x", "cols": [{"faces": {"south": "aa"}}]}]}]
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        sp = td / "pr_sheet_2026-10-22.html"
        sp.write_text(sheet_html(items))
        dp = td / "pr_sheet_2026-10-22.decisions.json"
        dp.write_text("{}")

        # serve_gated: a stamped sheet (stamp check stubbed) with no record is refused before freshness or serving
        calls = []
        SV.SG.verify_stamp = lambda html: (True, "stub stamp")
        SV.startup_freshness = lambda p, ctx=None: calls.append("fresh") or 0
        SV.serve_with_followed_guard = lambda argv, fresh=None: calls.append("serve") or 0
        rc = SV.main(["--no-open", "--sheet", str(sp), "--decisions", str(dp)])
        check(rc == 4 and not calls, f"serve_gated refuses an unread stamped sheet, serves nothing (rc {rc}, calls {calls})")
        complete(sp)
        rc = SV.main(["--no-open", "--sheet", str(sp), "--decisions", str(dp)])
        check(rc == 0 and calls == ["fresh", "serve"], f"serve_gated serves a pre-reviewed sheet (rc {rc}, calls {calls})")
        # the non-art route is gated the same way
        PR.record_path(sp).unlink()
        calls.clear()
        SV.SG.verify_stamp = lambda html: (False, "no stamp")
        SV.NA.declares_nonart = lambda html: True
        SV.NA.verify = lambda p, d: (True, "stub non-art")
        rc = SV.main(["--no-open", "--sheet", str(sp), "--decisions", str(dp)])
        check(rc == 4 and not calls, f"serve_gated refuses an unread non-art sheet (rc {rc})")
        complete(sp)
        rc = SV.main(["--no-open", "--sheet", str(sp), "--decisions", str(dp)])
        check(rc == 0 and calls == ["serve"], f"serve_gated serves a pre-reviewed non-art sheet (rc {rc}, calls {calls})")

        # sheet_to_artifact (the phone): a non-art sheet with no record is refused and no page is written
        PR.record_path(sp).unlink()
        out = td / "phone.html"
        r = subprocess.run([sys.executable, str(HERE.parent / "sheet_to_artifact.py"), "--sheet", str(sp), "--title", "T",
                            "--out", str(out)], capture_output=True, text=True, timeout=120)
        check(r.returncode == 4 and "unread" in r.stderr and not out.exists(),
              f"sheet_to_artifact refuses an unread sheet (rc {r.returncode}: {r.stderr.strip()[-120:]})")
        complete(sp)
        r = subprocess.run([sys.executable, str(HERE.parent / "sheet_to_artifact.py"), "--sheet", str(sp), "--title", "T",
                            "--out", str(out)], capture_output=True, text=True, timeout=120)
        # past the gate the fixture is not a real template, so patch() may refuse it: only the gate's verdict is tested
        check(r.returncode != 4 and "unread" not in r.stderr, f"sheet_to_artifact lets a pre-reviewed sheet past the gate (rc {r.returncode})")

        # review_queue.serve: refuses before reusing or starting any server
        import review_queue as RQ
        RQ.OUT = td
        PR.record_path(sp).unlink()
        try:
            RQ.serve(sp.stem, 0.0)
            check(False, "review_queue.serve refuses an unread page")
        except SystemExit as e:
            check("unread" in str(e) and not (td / f"{sp.stem}.serve.log").exists(),
                  "review_queue.serve refuses an unread page before starting a server")
    print(f"{'FAILED' if FAILS else 'ALL PASS'} ({len(FAILS)} failing)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
