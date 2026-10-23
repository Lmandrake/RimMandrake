#!/usr/bin/env python3
"""review_queue.py — `art.py review awaiting-pick`: every row waiting on the owner's pick, on ONE gated page, with no
agent composing it (owner, by question card 2026-10-19: "How far do we go to make art review fast and reliable? →
Python command"; design: design/RimMandrake/art_sheet_speedup_2026-10-19.md, option B). Since 2026-10-22 an agent READS
it before he does (owner: "Read it first and see if it's obviously broken"): build with --no-serve, look at every row,
write the record (prereview.py), then serve; serve() refuses a page with no complete pre-review record.

    python3 src/RimMandrake/Utils/art/art.py review awaiting-pick              # build, serve, open in his browser
    python3 src/RimMandrake/Utils/art/art.py review awaiting-pick --dry-run    # list the rows and where they come from
            [--no-open] [--no-serve] [--name awaiting_pick] [--date YYYY-MM-DD]

AWAITING HIS PICK, exactly (measured, never an agent's judgment):
  an OPEN sheet = Transient/biome_ffar/<x>_sheet_<date>.html with its .decisions.json, not frozen, reviewStatus not
  `ruled`, not returned, and not a texture-manifest sheet (C#-drawn textures: --subjects cannot rebuild those rows;
  they are listed as skipped). A row of an open sheet AWAITS when
    · it is not collapsed as already ruled on another sheet (ruledElsewhere), and no other sheet holds his ruling on
      the subject made after this sheet was built, and
    · he has left it alone there: no decision of his (decisions_v2.decision_is_his), no note, no followed note, no slot
      state, no use / not-needed, no ✕, no pool / retire / old-tick / question answer, and
    · it has something to pick: a candidate set of ours in a slot that is not what the game draws, an unassigned render,
      or a required slot with nothing in game.
  Rows of the queue's OWN page that he has touched stay on it (he sees his picks until enact). The same subject on
  several sheets is one row; its artpipe jobs are merged, each bound to the subject (JOB=DEF).

The page is built by art_sheet.subjects_census + generate_biome (the scaled-review gate, all requirements) as
<name>_sheet_<date>.html. A rebuild never rewrites a decisions file he has touched (generate_biome). If the gate
fails ONLY on freshness at birth (req 15: the ledger lags the disk for some rows), those rows are dropped, named, and
the page is built once more without them. Serving: one serve_gated server for this page (stale rows are badged on the
page, never the sheet refused); a live server already serving this file is reused, since it re-reads the sheet on
every request. Its URL is printed and opened with `powershell.exe Start-Process`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402

OUT = L.REPO_ROOT / "Transient" / "biome_ffar"
NAME = "awaiting_pick"
SHEET_RE = re.compile(r"^([a-z0-9_]+)_sheet_(\d{4}-\d{2}-\d{2})\.html$")
URL_RE = re.compile(r"http://localhost:\d+/\?t=[A-Za-z0-9_-]+")
TOUCH_KEYS = ("slots", "assign", "purge", "pool", "reject", "retire", "legacyRuled", "q", "asks", "notes_followed", "picks")


def _t(msg: str, t0: float) -> None:
    print(f"[{time.time() - t0:6.1f} s] {msg}", flush=True)


# ─────────────────────────────────────────────────────────── what awaits ──

def open_sheets(out: Path = OUT) -> tuple[list[dict], list[str]]:
    """([{base, html, dpath, doc, census, key}], skipped lines)."""
    sheets, skipped = [], []
    for html in sorted(out.glob("*_sheet_*.html")):
        if ".gate.tmp" in html.name or not SHEET_RE.match(html.name):
            continue
        base = html.stem
        dpath = out / f"{base}.decisions.json"
        try:
            doc = json.loads(dpath.read_text())
        except (OSError, ValueError):
            continue
        rs = doc.get("reviewStatus") if isinstance(doc.get("reviewStatus"), dict) else {}
        if doc.get("frozen") or rs.get("state") == "ruled" or doc.get("returned"):
            continue
        biome = doc.get("biome") or ""
        census = None
        if biome.startswith("SUBJECTS_"):
            cp = out / f"{biome[len('SUBJECTS_'):]}.subjects.json"
            try:
                census = (json.loads(cp.read_text())["biomes"].get(biome) or {})
            except (OSError, ValueError, KeyError):
                census = None
            if census and census.get("textures_manifest"):
                skipped.append(f"{base}: texture-manifest sheet (C#-drawn textures) — review it on its own page")
                continue
        sheets.append({"base": base, "html": html, "dpath": dpath, "doc": doc, "census": census, "key": biome})
    return sheets, skipped


def owner_touched(v) -> bool:
    import decisions_v2 as DV
    if not isinstance(v, dict):
        return False
    if DV.decision_is_his(v) or (v.get("note") or "").strip():
        return True
    return any(v.get(k) for k in TOUCH_KEYS)


def pickable(it: dict) -> bool:
    for g in it.get("graphics") or []:
        cols = g.get("cols") or []
        if g.get("lane") == "unassigned" and cols:
            return True
        if g.get("lane") != "slot":
            continue
        live = [c for c in cols if c.get("winner") and not c.get("purgedLive")]
        if (g.get("slot") or {}).get("required") and not live:
            return True
        for c in cols:
            if c.get("winner") or c.get("noSelect") or c.get("purgedLive"):
                continue
            if c.get("kind") == "donor" and not c.get("ours") and not c.get("oursRender"):
                continue
            return True
    return False


SETTLE_VERDICTS = {"keep", "redo", "hold", "out", "reject", "release", "accept", "cut"}


def ledger_settled(it: dict, names: set, idx) -> str:
    """Why the ART LEDGER says this row no longer waits on him, or '' (owner, 2026-10-21: verify the dedupe against the
    ledger, not sheet-to-sheet only). Settled when every candidate set of ours on it is already ruled by him (a keep,
    redo or reject naming its bytes), purged, or live somewhere — or when he ruled the subject (any sheet, any enact)
    AFTER its newest candidate was drawn. A required slot with nothing in game always waits."""
    cands = []
    for g in it.get("graphics") or []:
        if g.get("lane") == "slot" and (g.get("slot") or {}).get("required") and not any(
                c.get("winner") and not c.get("purgedLive") for c in g.get("cols") or []):
            return ""
        if g.get("lane") not in ("slot", "unassigned"):
            continue
        for c in g.get("cols") or []:
            if c.get("winner") or c.get("noSelect") or c.get("purgedLive"):
                continue
            if c.get("kind") == "donor" and not c.get("ours") and not c.get("oursRender"):
                continue
            cands.append([s for s in (c.get("faces") or {}).values() if s])
    if not cands:
        return "nothing of ours left to pick"

    def owner_ruled(sha):
        return any(r.get("by") == "owner" and r.get("trust") == "ruled" and r.get("verdict") in SETTLE_VERDICTS
                   for r in idx.rulings_by_sha.get(sha, ()))
    if all(all(owner_ruled(s) or idx.is_purged(s) or idx.live_anywhere(s) for s in shas) for shas in cands):
        return "every candidate is already ruled, purged or installed (art ledger)"
    drawn = max((e.get("ts") or "" for shas in cands for s in shas for e in idx.variants.get(s, ())), default="")
    subj = {L.subject_key(n) for n in names if n}
    later = [r for r in idx.subject_rulings(subj) if r.get("by") == "owner" and r.get("trust") == "ruled"
             and r.get("verdict") in SETTLE_VERDICTS and drawn and (r.get("ts") or "") > drawn]
    if later:
        r = max(later, key=lambda x: x.get("ts") or "")
        return f"you ruled it {r.get('verdict')} on {(r.get('ts') or '')[:10]} after its newest candidate was drawn (art ledger)"
    return ""


def _census_rows(sh: dict) -> dict:
    if sh["census"] is not None:
        return {r.get("key"): r for r in sh["census"].get("rows") or []}
    import art_sheet as A
    try:
        c = json.loads(Path(A.CENSUS).read_text())
    except (OSError, ValueError):
        return {}
    return {r.get("key"): r for r in (c["biomes"].get(sh["key"]) or {}).get("rows") or []}


def awaiting(name: str = NAME, date: str | None = None, out: Path = OUT, exclude_sheets=(), ledger: bool = False) -> dict:
    """{"rows": [{subject, jobs, sheets, kind, label}], "skipped": [...], "sheets": n, "per_sheet": {base: n},
    "settled": {subject: why}}. exclude_sheets: subjects on these sheets are ruled THERE, so left off here. ledger: every
    row (the queue's own untouched rows too) is checked against the art ledger (ledger_settled)."""
    import art_sheet as A
    import sheet_freshness as FR
    own_prefix = f"{name}_sheet_"
    sheets, skipped = open_sheets(out)
    idx = L.cached_index() if ledger else None
    settled: dict = {}
    excl_names: set = set()
    for ex in exclude_sheets:
        exb = ex[:-5] if ex.endswith(".html") else ex
        try:
            for it in FR.read_items((out / f"{exb}.html").read_text(errors="replace")) or []:
                excl_names |= A._subject_names(it.get("id") or "")
        except OSError:
            raise SystemExit(f"--exclude-sheet {ex}: no {out / (exb + '.html')}")
    later = A.ruled_elsewhere(out, f"{name}_sheet_{date or time.strftime('%Y-%m-%d')}")
    rows: dict = {}
    per = {}
    for sh in sheets:
        try:
            items = FR.read_items(sh["html"].read_text(errors="replace")) or []
        except OSError:
            continue
        own = sh["base"].startswith(own_prefix)
        built = sh["html"].stat().st_mtime
        dec = sh["doc"].get("decisions") or {}
        crow = _census_rows(sh)
        n = 0
        for it in items:
            sid = it.get("id")
            if not sid or it.get("ruledElsewhere"):
                continue
            v = dec.get(sid)
            if owner_touched(v) and not own:
                continue
            if excl_names & A._subject_names(sid):
                settled.setdefault(sid, "ruled on its own sheet: " + ", ".join(sorted(exclude_sheets))[:80])
                continue
            if idx is not None and not (own and owner_touched(v)):
                why = ledger_settled(it, set().union(*[A._subject_names(x) for x in [sid] + list((crow.get(sid) or {}).get("defNames") or []) if x]), idx)
                if why:
                    settled.setdefault(sid, why)
                    continue
            if not own and not pickable(it):
                continue
            if not own:
                names = set().union(*[A._subject_names(x) for x in [sid] + list((crow.get(sid) or {}).get("defNames") or []) if x])
                hit = [e for e in later if e["names"] & names and e["sheet_id"] != sh["base"]
                       and A._epoch(e.get("at") or "") > built]
                if hit:
                    continue
            r = rows.setdefault(sid, {"subject": sid, "jobs": [], "sheets": [], "kind": it.get("kind") or "",
                                      "label": it.get("label") or sid, "row": None})
            if r["row"] is None and crow.get(sid):
                r["row"] = json.loads(json.dumps(crow[sid]))     # the source sheet's census row: no re-resolve needed
            for j in (crow.get(sid) or {}).get("artpipe_state_jobs") or []:
                if j not in r["jobs"]:
                    r["jobs"].append(j)
            r["sheets"].append(sh["base"])
            if "_sig" not in r:
                # twins draw the very same texture paths (three liquids in one RM_Barrel, a tier twin): one ruling
                # installs for all of them. Colour variants at their own texPaths are not twins. Keyed on the graphics,
                # not the candidate bytes, so a row the queue page already tidied still matches its untidied twin.
                r["_sig"] = frozenset(g.get("key") for g in it.get("graphics") or []
                                      if g.get("lane") == "slot" and g.get("key") and not str(g.get("key")).startswith("_"))
            n += 1
        if n:
            per[sh["base"]] = n
    order = {"fauna": 0, "flora": 1, "fish": 2}
    out_rows = sorted(rows.values(), key=lambda r: (order.get(r["kind"], 3), r["kind"], r["label"].lower()))
    # the SAME pictures under two subject names (a tier twin, three liquids sharing one barrel) are ruled once: the
    # first row carries them, the others are named on the page
    first: dict = {}
    for r in list(out_rows):
        sig = r.pop("_sig", frozenset())
        if not ledger:
            continue
        if sig and sig in first:
            settled[r["subject"]] = f"the same pictures as {first[sig]} (ruled once, on that row)"
            out_rows.remove(r)
        elif sig:
            first[sig] = r["subject"]
    for r in out_rows:
        settled.pop(r["subject"], None)      # waiting on one sheet beats settled on another
    return {"rows": out_rows, "skipped": skipped, "sheets": len(sheets), "per_sheet": per, "settled": settled}


def apply_leave_off(q: dict, tidy: dict | None) -> dict:
    """tidy[subject].leave_off = why: after LOOKING, the row has nothing he can use (every new set of ours is a copy of
    the in-game one or broken) — it leaves the page, named with the reason in the settled list."""
    off = {k: v["leave_off"] for k, v in (tidy or {}).items() if isinstance(v, dict) and v.get("leave_off")}
    if not off:
        return q
    q = dict(q, rows=[r for r in q["rows"] if r["subject"] not in off], settled=dict(q.get("settled") or {}))
    for k, why in off.items():
        q["settled"][k] = "left off after looking: " + why
    return q


# ─────────────────────────────────────────────────────────── build ──

def _lead(q: dict, dropped: dict) -> str:
    import html as H
    src = ", ".join(f"{H.escape(b)} ({n})" for b, n in sorted(q["per_sheet"].items(), key=lambda x: -x[1])[:30])
    more = len(q["per_sheet"]) - 30
    drop = ("<p><b>Left off this page</b> (stale at build — the ledger lags the disk; they return on the next run): "
            + H.escape(", ".join(sorted(dropped))) + "</p>") if dropped else ""
    sett = q.get("settled") or {}
    if sett:
        drop += ("<details><summary class='sub'>Left off because already settled (" + str(len(sett)) + ")</summary><p class='sub'>"
                 + "<br>".join(H.escape(f"{k}: {v}") for k, v in sorted(sett.items())) + "</p></details>")
    return (f"<p><b>Everything waiting on your pick — {len(q['rows'])} rows from {len(q['per_sheet'])} open sheets.</b> "
            "Built by <code>art.py review awaiting-pick</code> with no agent in the loop. Click a picture to use it, "
            "<b>redraw this slot</b>, or type anything else in the note. A row whose pictures changed on disk since this "
            "page was built shows a red <b>STALE</b> badge and its picks are off; the rest of the page works. Nothing "
            f"installs until you say you are done.</p><p class='sub'>From: {src}{f' and {more} more' if more > 0 else ''}.</p>{drop}")


def write_census(name: str, rows: list, label: str, lead_html: str, tidy: dict | None = None,
                 rationalize: bool = True) -> tuple[Path, str]:
    """The queue page's census, in art_sheet.subjects_census's shape. Each row is REUSED from its source sheet's census
    (generate_biome re-resolves texPaths from src XML at build anyway, FR.fresh_resources), with the jobs of every sheet
    it came from; only a row with no source census row is re-resolved from the def dump (art_sheet.subject_row, ~1 s
    each on the /mnt/c dump — 218 s for 241 rows, which is why rows are reused)."""
    import art_sheet as A
    R = None
    out_rows = []
    for r in rows:
        row = r.get("row")
        if row is None:
            if R is None:
                import scale_panel
                R = scale_panel.Resolver()
            row = A.subject_row(R, r["subject"], r["jobs"])
        row = dict(row, key=r["subject"])
        row["artpipe_state_jobs"] = sorted(set(row.get("artpipe_state_jobs") or []) | set(r["jobs"]))
        row.pop("reopen", None)
        for k in ("set_merges", "drop_sets", "drop_why"):
            if (tidy or {}).get(r["subject"], {}).get(k):
                row[k] = tidy[r["subject"]][k]
        out_rows.append(row)
    key = f"SUBJECTS_{name}"
    path = OUT / f"{name}.subjects.json"
    census = {"schema": 1, "generated": L.now(), "git_head": None, "biome_order": [key],
              "biomes": {key: {"label": label, "slug": name, "subjects": True, "ground_terrain": A.SUBJECT_GROUND,
                               "title": f"{label} — game art", "lead_html": lead_html, "rows": out_rows,
                               "rationalize": rationalize,
                               "built_by": "review_queue.py (art.py review awaiting-pick)"}}}
    path.write_text(json.dumps(census, indent=1))
    return path, key


RETRIES = 2


def build(q: dict, name: str = NAME, date: str | None = None, t0: float | None = None, tidy: dict | None = None,
          opts: dict | None = None) -> dict:
    """Build + gate the page. A gate failure ONLY on req 7 (he ruled a row on another sheet while this one was being
    built: he is often mid-sitting) and/or req 15 (a row stale at birth: the ledger lags the disk) re-collects the queue,
    drops the stale rows (named on the page and in the output) and builds again, at most RETRIES times; so does req 13
    reporting ZERO rendered <img> (an Edge flake under load). Anything else
    fails loudly with the gate's report."""
    import art_sheet as A
    import refresh_sheets as R
    import scaled_review_gate as SG
    t0 = t0 or time.time()
    date = date or time.strftime("%Y-%m-%d")
    base = f"{name}_sheet_{date}"
    dropped: dict = {}
    for attempt in range(RETRIES + 1):
        rows = [r for r in q["rows"] if r["subject"] not in dropped]
        cpath, key = write_census(name, rows, f"Waiting on your pick ({len(rows)})", _lead(dict(q, rows=rows), dropped), tidy)
        _t(f"census written: {len(rows)} rows, {sum(len(r['jobs']) for r in rows)} jobs -> {cpath.name}", t0)
        try:
            res = A.generate_biome(key, cpath, OUT / f"{base}.html", date, sheet_only=R.touched(base))
            _t(f"built and gated: {base}.html", t0)
            return {"base": base, "html": OUT / f"{base}.html", "decisions": OUT / f"{base}.decisions.json",
                    "rows": len(rows), "dropped": dropped, "result": res}
        except SG.GateFailed as e:
            bad = [c for c in e.checks if not c.ok]
            # req 13 with ZERO <img> is headless Edge flaking under load (an early empty dump: the same page rendered
            # 1982 <img> in 14 s on a re-check, 2026-10-19); any other req 13 failure is real and stops the build
            flake = lambda c: c.req == "13" and all("only 0 <img>" in x for x in c.problems)
            if attempt < RETRIES and bad and all(c.req in ("7", "15") or flake(c) for c in bad):
                ids = {r["subject"] for r in rows}
                for c in bad:
                    if c.req != "15":
                        continue
                    for prob in c.problems:
                        k, _, why = prob.partition(": ")
                        if k in ids:
                            dropped.setdefault(k, why)
                _t(f"gate refused on req {', '.join(sorted({c.req for c in bad}))}: re-collecting"
                   + (f"; {len(dropped)} stale-at-birth row(s) left off: " + ", ".join(sorted(dropped)[:12]) if dropped else ""), t0)
                q = dict(apply_leave_off(awaiting(name, date, **(opts or {})), tidy), skipped=q.get("skipped", []))
                continue
            print(SG.report(e.sheet, e.checks, limit=20), file=sys.stderr)
            raise
    raise RuntimeError("unreachable")


# ─────────────────────────────────────────────────────────── serve ──

def _server_file(base: str) -> Path:
    return OUT / f"{base}.server.json"


def _alive_pid(pid: int, needle: str) -> bool:
    try:
        cmd = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
    except OSError:
        return False
    return "serve_gated.py" in cmd and needle in cmd


def serve(base: str, t0: float) -> str:
    import refresh_sheets as R
    sf = _server_file(base)
    html, dec = OUT / f"{base}.html", OUT / f"{base}.decisions.json"
    import prereview as PR  # checked before reusing a live server too: a rebuilt page may hold unread rows
    ok, msg = PR.verify(html)
    if not ok:
        raise SystemExit(f"REFUSED review_queue serve: nothing reaches the owner unread: {msg}")
    try:
        cur = json.loads(sf.read_text())
    except (OSError, ValueError):
        cur = {}
    if cur.get("pid") and _alive_pid(int(cur["pid"]), html.name) and R.alive(cur.get("url")):
        _t(f"reusing the live server pid {cur['pid']} (it re-reads the sheet on every request)", t0)
        return cur["url"]
    # one server per queue page: a dead or stale one of OURS (its pid file, its sheet on the command line) is stopped
    if cur.get("pid") and _alive_pid(int(cur["pid"]), html.name):
        try:
            os.kill(int(cur["pid"]), signal.SIGTERM)
        except OSError:
            pass
    log = OUT / f"{base}.serve.log"
    fh = open(log, "w")
    p = subprocess.Popen([sys.executable, str(HERE / "serve_gated.py"), "--no-open", "--sheet", str(html), "--decisions", str(dec)],
                         stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, cwd=str(OUT), start_new_session=True)
    url = None
    for _ in range(150):
        time.sleep(0.2)
        m = URL_RE.search(log.read_text(errors="replace"))
        if m:
            url = m.group(0)
            break
        if p.poll() is not None:
            break
    if not url:
        raise SystemExit(f"serve_gated printed no URL (exit {p.poll()}); see {log}")
    sf.write_text(json.dumps({"pid": p.pid, "url": url, "sheet": str(html), "started": L.now()}, indent=1))
    _t(f"serving pid {p.pid}", t0)
    return url


def open_url(url: str) -> bool:
    try:
        subprocess.run(["powershell.exe", "-NoProfile", "-Command", f"Start-Process '{url}'"], timeout=30,
                       stdin=subprocess.DEVNULL, capture_output=True)
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def native(p: Path) -> str:
    return "\\\\wsl.localhost\\Ubuntu" + str(p).replace("/", "\\")


# ─────────────────────────────────────────────────────────── cli ──

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("query", choices=["awaiting-pick"])
    ap.add_argument("--dry-run", action="store_true", help="list the rows awaiting his pick and where they come from")
    ap.add_argument("--no-serve", action="store_true")
    ap.add_argument("--no-open", action="store_true")
    ap.add_argument("--name", default=NAME)
    ap.add_argument("--date")
    ap.add_argument("--exclude-sheet", action="append", default=[], metavar="SHEET",
                    help="a sheet (base name) whose subjects are ruled THERE: left off this page")
    ap.add_argument("--no-ledger", action="store_true", help="skip the art-ledger check (rows already ruled/installed)")
    ap.add_argument("--tidy", metavar="FILE", help="JSON {subject: {set_merges, drop_sets, drop_why}} — the agent's "
                    "set tidying, written after LOOKING at the pictures (art_sheet.rationalize_row)")
    a = ap.parse_args(argv)
    t0 = time.time()
    opts = {"exclude_sheets": a.exclude_sheet, "ledger": not a.no_ledger}
    tidy = json.loads(Path(a.tidy).read_text()) if a.tidy else None
    q = awaiting(a.name, a.date, **opts)
    q = apply_leave_off(q, tidy)
    _t(f"{len(q['rows'])} rows awaiting his pick, from {len(q['per_sheet'])} of {q['sheets']} open sheets", t0)
    for s in q["skipped"]:
        print("  skipped:", s)
    if a.dry_run:
        for r in q["rows"]:
            print(f"  {r['kind']:<8} {r['subject']:<40} jobs {len(r['jobs']):>2}  from {', '.join(r['sheets'])[:90]}")
        for k, v in sorted((q.get("settled") or {}).items()):
            print(f"  settled  {k:<40} {v}")
        return 0
    if not q["rows"]:
        print("nothing awaits his pick")
        return 0
    b = build(q, a.name, a.date, t0, tidy=tidy, opts=opts)
    if b["dropped"]:
        print(f"  left off (stale at build): {len(b['dropped'])}: " + ", ".join(sorted(b["dropped"])[:30]))
    print(f"SHEET {native(b['html'])}  ({b['rows']} rows)")
    if a.no_serve:
        return 0
    url = serve(b["base"], t0)
    opened = False if a.no_open else open_url(url)
    _t(f"URL {url}" + ("  (opened in his browser)" if opened else ""), t0)
    print(f"URL {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
