#!/usr/bin/env python3
"""refresh_sheets.py — rebuild only the biome art sheets whose candidate renders changed, keep their URLs stable.

    python3 src/RimMandrake/Utils/art/refresh_sheets.py              # backfill renders, rebuild changed sheets
    python3 src/RimMandrake/Utils/art/refresh_sheets.py --dry-run    # say what would change, write nothing
    python3 src/RimMandrake/Utils/art/refresh_sheets.py --force      # rebuild every sheet
    python3 src/RimMandrake/Utils/art/refresh_sheets.py --selftest

What it does, in order:
 1. `art.py backfill artpipe` (finished renders into the ledger; --no-backfill skips it).
 2. For each sheet Transient/biome_ffar/<slug>_sheet_<date>.html (biome read from its snapshot) it computes a
    CANDIDATE FINGERPRINT: every ledger picture bound to the biome's rows' texPaths plus every artpipe render whose
    job family whole-token-matches a row's name (subject.token_match), plus which of those failed the canon gate.
    A sheet whose fingerprint equals the one recorded at its last build is left alone.
 3. A changed sheet is rebuilt with art_sheet.generate_biome. Decisions are never overwritten: generate_biome
    refuses a file the sidecar wrote, and a sheet with any saved decisions is rebuilt HTML-only (sheet_only).
    THE SCALED-REVIEW GATE is hard: generate_biome builds to a temp file, runs scaled_review_gate, and only a pass
    replaces the sheet. A failing rebuild is reported "GATE FAILED (previous sheet kept)" and the last good sheet
    keeps being served untouched; its fingerprint is NOT recorded, so it is retried every cycle. A sheet left alone is
    still re-verified, and one that no longer passes (e.g. a subject since ruled elsewhere) or was built before the
    gate (no stamp) is rebuilt through the same gate. The exit code is nonzero when any sheet fails the gate; the
    systemd loop ignores it, and no sheet is ever taken down.
 4. URLs stay STABLE: the running serve_sheet.py re-reads the sheet and decisions on every request, so rebuilt
    files are live on the same port and token. Only a sheet whose server no longer answers is restarted, and then
    TONIGHT and SHEETS_INDEX are rewritten with the new URL.
 5. TONIGHT's "donor awaiting: N" is recomputed for every sheet (rows whose pictures are all donor-kind).

State: Transient/biome_ffar/sheets_state.json {sheet: {fp, built}}. No state = rebuild (first run seeds it).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402
import subject as S  # noqa: E402
import scaled_review_gate as SG  # noqa: E402

OUT = L.REPO_ROOT / "Transient" / "biome_ffar"
STATE = "sheets_state.json"
SERVE = HERE / "serve_gated.py"      # the only server launcher: refuses an HTML without a passing gate stamp
CHECK = Path.home() / ".claude" / "skills" / "review-sheets" / "assets" / "check_sheet.py"
SHEET_RE = re.compile(r"^([a-z_]+_sheet_(\d{4}-\d{2}-\d{2}))\.html$")
URL_RE = re.compile(r"http://localhost:\d+/\?t=[A-Za-z0-9_-]+")


# ───────────────────────────────────────────────────────── pure helpers ──

def donor_only_count(html: str) -> int:
    """Rows of a built sheet whose every picture is donor-kind (not our deployed copy)."""
    m = re.search(r'<script id="ITEMS" type="application/json">(.*?)</script>', html, re.S)
    n = 0
    for i in json.loads(m.group(1)) if m else []:
        cols = [c for g in i.get("graphics", []) for c in g["cols"]]
        if cols and not any(c["kind"] != "donor" or c.get("ours") or str(c.get("label", "")).startswith("our deployed")
                            for c in cols):
            n += 1
    return n


def fingerprint(row_keys: list[list[str]], row_res: list[list[str]], idx, failed: set) -> str:
    """Hash of the candidate pictures a biome's rows could show. row_keys: per row, its name keys (normalised)."""
    shas = set()
    for res in {r for rs in row_res for r in rs}:
        shas |= {s for s in idx.by_res.get(res, ()) if not idx.is_purged(s)}
    keys = {k for ks in row_keys for k in ks if len(k) >= S.MIN_KEY}
    for sha, vs in idx.variants.items():
        if idx.is_purged(sha):
            continue
        for v in vs:
            if v.get("kind") == "artpipe":
                fam = re.sub(r"_(north|east|south|west)(_r\d+)?$", "", v.get("job", ""))
                if any(S.token_match(fam, k) for k in keys):
                    shas.add(sha)
                    if v.get("job") in failed or fam in failed:
                        shas.add("FC:" + sha)
    return hashlib.sha256("\n".join(sorted(shas)).encode()).hexdigest()[:20]


def rewrite_line(line: str, base: str, url: str | None, donors: int | None) -> str:
    """In a TONIGHT / INDEX line naming sheet BASE: refresh the URL (when given) and the donor-awaiting count."""
    if base not in line:
        return line
    if url:
        line = URL_RE.sub(url, line)
    if donors is not None:
        line = re.sub(r"donor awaiting: \d+", f"donor awaiting: {donors}", line)
    return line


def rewrite_doc(text: str, urls: dict, donors: dict) -> str:
    out = []
    for line in text.split("\n"):
        for base in urls.keys() | donors.keys():
            if base + ".html" in line:
                line = rewrite_line(line, base + ".html", urls.get(base), donors.get(base))
                break
        out.append(line)
    return "\n".join(out)


# ───────────────────────────────────────────────────────────── servers ──

def served_url(base: str) -> str | None:
    log = OUT / f"{base}.serve.log"
    if not log.is_file():
        return None
    m = URL_RE.search(log.read_text(errors="replace"))
    return m.group(0) if m else None


def alive(url: str | None) -> bool:
    if not url:
        return False
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            return r.status == 200
    except Exception:  # noqa: BLE001
        return False


def restart(base: str) -> str | None:
    log = OUT / f"{base}.serve.log"
    with open(log, "w") as fh:
        subprocess.Popen([sys.executable, str(SERVE), "--no-open", "--sheet", f"{base}.html", "--decisions",
                          f"{base}.decisions.json"], cwd=str(OUT), stdout=fh, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, start_new_session=True)
    for _ in range(30):
        time.sleep(0.5)
        u = served_url(base)
        if u and alive(u):
            return u
    return None


# ──────────────────────────────────────────────────────────────── main ──

def sheets() -> list[tuple[str, str, str]]:
    out = []
    for p in sorted(OUT.glob("*_sheet_*.html")):
        m = SHEET_RE.match(p.name)
        if not m:
            continue
        snap = L.ledger_dir() / "sheets" / f"{m.group(1)}.snapshot.json"
        if snap.is_file():
            out.append((m.group(1), m.group(2), json.loads(snap.read_text()).get("biome", "")))
    return out


def touched(base: str) -> bool:
    d = OUT / f"{base}.decisions.json"
    try:
        j = json.loads(d.read_text())
    except (OSError, ValueError):
        return False
    return bool(j.get("savedBy") or j.get("writeCount"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="rebuild every sheet regardless of fingerprint")
    ap.add_argument("--no-backfill", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.no_backfill and not a.dry_run:
        subprocess.run([sys.executable, str(HERE / "art.py"), "backfill", "artpipe"], cwd=str(L.REPO_ROOT), check=True,
                       stdout=subprocess.DEVNULL)
    import art_sheet
    census_path = art_sheet.CENSUS
    census = json.loads(census_path.read_text())
    idx = L.Index()
    failed = art_sheet.failed_canon_jobs()
    sp = OUT / STATE
    state = json.loads(sp.read_text()) if sp.is_file() else {}
    urls, donors, report, gate_reports = {}, {}, [], []
    for base, date, biome in sheets():
        rows = (census["biomes"].get(biome) or {}).get("rows") or []
        keys = [[S.norm(S.stem(x)) for x in [r["key"], r.get("port"), r.get("label")] + list(r.get("defNames") or [])
                 + list(r.get("donors") or []) if x] for r in rows]
        res = [[x["res"] for x in (r.get("art") or {}).get("resources") or []] for r in rows]
        fp = fingerprint(keys, res, idx, failed)
        stale, prev_blank = "", False
        try:                      # re-verify the sheet on disk (stamp + every requirement, incl. rendering in a real browser)
            st_ok, st_msg = SG.verify_stamp((OUT / f"{base}.html").read_text())
            bad = [c for c in SG.run_gate(dict(SG.load_ctx(OUT / f"{base}.html"), skip_browser=True)) if not c.ok]
        except Exception as e:  # noqa: BLE001
            st_ok, st_msg, bad = False, f"{type(e).__name__}: {e}", []
        if not a.force and state.get(base, {}).get("fp") == fp:
            stale = ("" if st_ok else st_msg + "; ") + ("failing req " + ",".join(c.req for c in bad) if bad else "")
        changed = a.force or state.get(base, {}).get("fp") != fp or bool(stale)
        status = "unchanged"
        if changed and not a.dry_run and biome:
            try:
                art_sheet.generate_biome(biome, census_path, None, date, sheet_only=touched(base))
            except SG.GateFailed as e:
                status = "GATE FAILED (previous sheet kept): req " + ",".join(c.req for c in e.checks if not c.ok)
                gate_reports.append(SG.report(e.sheet, e.checks))
                if not SG.check_browser(SG.load_ctx(OUT / f"{base}.html"), SG._items(SG.load_ctx(OUT / f"{base}.html")) or []).ok:
                    prev_blank = True
                if prev_blank:    # the served sheet is itself blank: a rendering sheet that fails other reqs beats it
                    try:
                        art_sheet.generate_biome(biome, census_path, None, date, sheet_only=touched(base),
                                                 allow_failing="the previous sheet rendered blank (req 13)")
                        status = "OVERRIDE: previous sheet was blank; rebuilt unstamped+bannered, still failing req " + ",".join(
                            c.req for c in e.checks if not c.ok)
                    except Exception as e2:  # noqa: BLE001
                        status += f" (override failed: {type(e2).__name__})"
            except Exception as e:  # noqa: BLE001  a crashing build must never take the served sheet down
                status = f"BUILD ERROR (previous sheet kept): {type(e).__name__}: {str(e)[:120]}"
            else:
                ok = subprocess.run([sys.executable, str(CHECK), str(OUT / f"{base}.html"), "--decisions",
                                     str(OUT / f"{base}.decisions.json")], capture_output=True).returncode == 0
                status = "rebuilt" if ok else "FAILED check_sheet"
                if ok:
                    state[base] = {"fp": fp, "built": time.strftime("%Y-%m-%dT%H:%M:%S"), "gate": SG.GATE_VERSION}
        elif changed:
            status = "would rebuild" + (f" ({stale})" if stale else "")
        u = served_url(base)
        if not alive(u) and not a.dry_run:
            u = restart(base)
            urls[base] = u
            status += " (server restarted: NEW URL)" if u else " (SERVER DOWN and not restarted: no passing gate stamp)"
        donors[base] = donor_only_count((OUT / f"{base}.html").read_text())
        report.append((base, status, donors[base]))
    if not a.dry_run:
        sp.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n")
        for f in ("TONIGHT_2026-10-05.md", "SHEETS_INDEX_2026-10-05.md"):
            p = OUT / f
            if p.is_file():
                p.write_text(rewrite_doc(p.read_text(), urls, donors if f.startswith("TONIGHT") else {}))
    for b, s, d in report:
        print(f"{b:45} {s:28} donor-only {d}")
    print(f"total donor-only {sum(d for _, _, d in report)}; sheets rebuilt "
          f"{sum(s.startswith('rebuilt') for _, s, _ in report)}/{len(report)}")
    for g in gate_reports:
        print(g)
    return 1 if any(x in s for _, s, _ in report for x in ("FAILED", "SERVER DOWN", "ERROR")) else 0


def selftest() -> int:
    fails = []

    def check(c, m):
        print(("PASS " if c else "FAIL ") + m)
        if not c:
            fails.append(m)
    items = [{"id": "a", "graphics": [{"cols": [{"kind": "donor", "label": "donor original — x"}]}]},
             {"id": "b", "graphics": [{"cols": [{"kind": "donor", "label": "our deployed art — m", "ours": True}]}]},
             {"id": "c", "graphics": [{"cols": [{"kind": "donor", "label": "x"}, {"kind": "artpipe", "label": "render y"}]}]},
             {"id": "d", "graphics": []}]
    html = '<script id="ITEMS" type="application/json">' + json.dumps(items) + "</script>"
    check(donor_only_count(html) == 1, "donor_only_count: only the all-donor row counts")
    base = "x_sheet_2026-10-05"
    line = f"1. X | donor awaiting: 9 | http://localhost:1/?t=old | `D:\\a\\{base}.html`"
    new = rewrite_line(line, base + ".html", None, 3)
    check("donor awaiting: 3" in new and "localhost:1/?t=old" in new, "rewrite_line: count changes, stable URL untouched")
    new = rewrite_line(line, base + ".html", "http://localhost:2/?t=new", 3)
    check("localhost:2/?t=new" in new and "t=old" not in new, "rewrite_line: URL rewritten only when given")
    doc = rewrite_doc(line + "\nother line donor awaiting: 7", {}, {base: 0})
    check("donor awaiting: 0" in doc and "other line donor awaiting: 7" in doc, "rewrite_doc touches only the named sheet's line")

    class Idx:
        by_res = {"T/a": {"s1"}}
        variants = {"s1": [], "s2": [{"kind": "artpipe", "job": "brambles_v1_south"}]}

        def is_purged(self, s):
            return False
    f1 = fingerprint([["brambles"]], [["T/a"]], Idx(), set())
    f2 = fingerprint([["brambles"]], [["T/a"]], Idx(), {"brambles_v1_south"})
    f3 = fingerprint([["othername"]], [["T/a"]], Idx(), set())
    check(f1 != f3, "fingerprint: a render matching a row name changes it")
    check(f1 != f2, "fingerprint: a failed-canon flip changes it")
    check(not alive("http://localhost:9/?t=x"), "alive: a dead URL is not alive")
    print(f"{'ALL PASS' if not fails else str(len(fails)) + ' FAIL'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
