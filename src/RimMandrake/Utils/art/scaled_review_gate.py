#!/usr/bin/env python3
"""scaled_review_gate.py — a biome art sheet that fails a scaled-game-image-review requirement is never written or served.

    python3 scaled_review_gate.py check <sheet.html>... [--urls] [--stamp] [--out report.txt]
    python3 scaled_review_gate.py all [--urls] [--stamp] [--out report.txt]     every Transient/biome_ffar/*_sheet_*.html
    python3 scaled_review_gate.py verify-stamp <sheet.html>                     exit 0 only if the gate stamp matches

The spec is `skills/scaled-game-image-review/SKILL.md` (its 12 rulings). Each check below passes or fails and names
the rows and the requirement number. A check that cannot be measured FAILS and says UNMEASURED — it is never a
silent pass. Nothing here is weakened to make a sheet pass: a failing sheet is reported, and the previous good
sheet stays where it is.

Where it is wired (all hard):
  art_sheet.generate_biome   builds to `<sheet>.gate.tmp`, runs `run_gate`, and only then moves the HTML into place
                             (stamped). Failure raises GateFailed; the previous sheet, snapshot and decisions are untouched.
  refresh_sheets.py          calls generate_biome, so it inherits that; also re-verifies sheets it left alone.
  serve_gated.py             the only way to start a sheet server; refuses an HTML without a valid stamp.
  ingest.py / art.py ingest  `--redo-jobs`: every regen job must carry the decision's note verbatim as owner_note (req 9).
  .claude/hooks/block_hand_edited_sheet.py   refuses hand-writing a sheet or starting a server outside these tools.

The stamp is `<meta name="scaled-review-gate" content="v1 sha256:<hex>">`, the hash of the HTML without that tag, so any
hand edit after the gate invalidates it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402
import subject as S  # noqa: E402

GATE_VERSION = "v1"
SHEET_DIR = L.REPO_ROOT / "Transient" / "biome_ffar"
CHECK_SHEET = Path.home() / ".claude" / "skills" / "review-sheets" / "assets" / "check_sheet.py"
SHEET_RE = re.compile(r"^([a-z_]+_sheet_\d{4}-\d{2}-\d{2})\.html$")
STAMP_RE = re.compile(r'<meta name="scaled-review-gate" content="([^"]*)">')
FAILED_CANON_BADGE = " — failed canon check"
RULED_GROUP = "Already ruled on another sheet"
SIZE_FALLBACK_FLAG = "SIZE FALLBACK"
SKIP_BROWSER = False   # selftests of OTHER tools that build throwaway fixture sheets set this; the real tools never do
ARTPIPE_DEFAULT = "/mnt/d/Luke/dev/_artpipe"


class GateFailed(Exception):
    def __init__(self, sheet: str, checks: list):
        self.sheet, self.checks = sheet, checks
        super().__init__(f"{sheet}: " + "; ".join(f"req {c.req} {c.name}" for c in checks if not c.ok))


class Check:
    def __init__(self, req: str, name: str, problems: list[str] | None = None, note: str = ""):
        self.req, self.name, self.problems, self.note = req, name, list(problems or []), note

    @property
    def ok(self) -> bool:
        return not self.problems

    def line(self, limit: int = 12) -> str:
        if self.ok:
            return f"  PASS req {self.req:<4} {self.name}" + (f" ({self.note})" if self.note else "")
        shown = self.problems[:limit]
        more = f" … +{len(self.problems) - limit} more" if len(self.problems) > limit else ""
        return f"  FAIL req {self.req:<4} {self.name}: " + "; ".join(shown) + more


# ───────────────────────────────────────────────────────────────── stamp ──

def _body_hash(html: str) -> str:
    return hashlib.sha256(STAMP_RE.sub("", html).encode()).hexdigest()


def stamp(html: str) -> str:
    html = STAMP_RE.sub("", html)
    tag = f'<meta name="scaled-review-gate" content="{GATE_VERSION} sha256:{hashlib.sha256(html.encode()).hexdigest()}">'
    if "<head>" in html:
        return html.replace("<head>", "<head>" + tag, 1)
    return tag + html


def verify_stamp(html: str) -> tuple[bool, str]:
    m = STAMP_RE.search(html)
    if not m:
        return False, "no gate stamp — this HTML never passed scaled_review_gate"
    ver, _, h = m.group(1).partition(" sha256:")
    if ver != GATE_VERSION:
        return False, f"gate stamp version {ver!r} != {GATE_VERSION!r} — re-run the gate"
    if h != _body_hash(html):
        return False, "gate stamp does not match the HTML — it was edited after the gate (hand edit)"
    return True, f"stamp ok ({GATE_VERSION})"


# ───────────────────────────────────────────────────────────────── inputs ──

def _json_block(html: str, tag_id: str):
    m = re.search(r'<script id="%s"[^>]*>(.*?)</script>' % tag_id, html, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1).replace("<\\/", "</"))
    except ValueError:
        return None


def artpipe_dir() -> Path:
    return Path(os.environ.get("ARTPIPE_STATE_DIR") or ARTPIPE_DEFAULT)


def job_ids(kind_dirs=("pending", "active")) -> tuple[set, list[str]]:
    """(subject strings of every pending/active job, problems). A job contributes its id and target_def."""
    root, subs, bad = artpipe_dir(), set(), []
    for d in kind_dirs:
        p = root / d
        if not p.is_dir():
            bad.append(f"UNMEASURED: artpipe {d}/ not found at {p}")
            continue
        for f in p.glob("*.json"):
            if "worker_" in f.name or f.name.endswith(".manifest.json"):
                continue
            subs.add(f.stem)
            try:
                td = json.loads(f.read_text()).get("target_def")
                if td:
                    subs.add(str(td))
            except (OSError, ValueError):
                pass
    return subs, bad


def failed_canon() -> set:
    root = artpipe_dir() / "failed"
    out = set()
    if root.is_dir():
        for m in root.glob("*.manifest.json"):
            try:
                if json.loads(m.read_text()).get("worker_status") == "failed_canon":
                    out.add(m.name[:-len(".manifest.json")])
            except (OSError, ValueError):
                pass
    return out


def _ground_for(biome: str) -> dict | None:
    try:
        return json.loads((SHEET_DIR / "scale_ground_measured.json").read_text()).get(biome)
    except (OSError, ValueError):
        return None


def load_ctx(html_path: Path) -> dict:
    """Everything the gate needs for an ALREADY-BUILT sheet on disk."""
    html_path = Path(html_path)
    sid = html_path.stem
    sd = html_path.parent
    snap_path = L.ledger_dir() / "sheets" / f"{sid}.snapshot.json"
    dp = sd / f"{sid}.decisions.json"
    ctx = {"html": html_path.read_text(), "sheet_id": sid, "sheet_dir": sd, "html_path": html_path,
           "snap_path": snap_path, "decisions_path": dp, "snap": None, "decisions": None, "census_rows": None,
           "problems": []}
    try:
        ctx["snap"] = json.loads(snap_path.read_text())
    except (OSError, ValueError):
        ctx["problems"].append(f"UNMEASURED: snapshot {snap_path.name} unreadable")
    try:
        ctx["decisions"] = json.loads(dp.read_text()) if dp.is_file() else None
    except ValueError:
        ctx["problems"].append(f"UNMEASURED: decisions file {dp.name} is not JSON")
    biome = (ctx["snap"] or {}).get("biome") or ""
    ctx["biome"] = biome
    ctx["ground"] = _ground_for(biome)
    try:
        import art_sheet
        census = json.loads(Path(art_sheet.CENSUS).read_text())
        ctx["census_rows"] = (census["biomes"].get(biome) or {}).get("rows")
    except Exception as e:  # noqa: BLE001
        ctx["problems"].append(f"UNMEASURED: census unreadable ({type(e).__name__}: {e})")
    return ctx


# ───────────────────────────────────────────────────────────────── checks ──

def _items(ctx):
    return _json_block(ctx["html"], "ITEMS")


def _rownames(r: dict) -> list[str]:
    return [x for x in [r.get("key"), r.get("port")] + list(r.get("defNames") or []) if x]


def _is_ours_label(label: str) -> bool:
    return str(label or "").startswith("our deployed")


def _has_ours(c: dict) -> bool:
    """A column that is art of ours: not a donor original, and not a live placeholder (placeholder_detect)."""
    if c.get("placeholder"):
        return False
    return c.get("kind") != "donor" or bool(c.get("ours")) or _is_ours_label(c.get("label"))


def _donor_only(it: dict) -> bool:
    """No art of ours: donor art only, or donor/placeholder art only (a placeholder badge counts as no art)."""
    cols = [c for g in it.get("graphics", []) for c in g.get("cols", [])]
    return bool(cols) and not any(_has_ours(c) for c in cols)


def check_one_biome(ctx, items) -> Check:
    p = []
    if not ctx.get("biome"):
        p.append("UNMEASURED: the snapshot names no biome")
    cfg = _json_block(ctx["html"], "CONFIG") or {}
    if cfg.get("sheetId") != ctx["sheet_id"]:
        p.append(f"CONFIG.sheetId {cfg.get('sheetId')!r} != file {ctx['sheet_id']!r}")
    rows = ctx.get("census_rows")
    if rows is None:
        p.append(f"UNMEASURED: no census rows for biome {ctx.get('biome')!r}")
    else:
        keys = {r["key"] for r in rows}
        foreign = [it["id"] for it in items if it["id"] not in keys]
        if foreign:
            p.append("rows not in this biome's census (another biome merged in?): " + ", ".join(foreign))
        subs = [k for k in (ctx["snap"] or {}).get("rows", {}) if k not in keys and not ctx["snap"]["rows"][k].get("rowGone")]
        if subs:
            p.append("snapshot rows outside this biome's census: " + ", ".join(subs[:10]))
    return Check("1", "one biome per sheet", p)


def check_scale(ctx, items) -> Check:
    p = []
    ground = ctx.get("ground")
    g_rgb = (ground or {}).get("rgb")
    if not ground:
        p.append(f"UNMEASURED: no ground-colour record for biome {ctx.get('biome')!r}")
    elif not (isinstance(g_rgb, list) and len(g_rgb) == 3 and all(isinstance(x, (int, float)) for x in g_rgb)):
        p.append(f"ground colour not measured ({(ground or {}).get('source')!r}) — the panel would sit on a default tan")
    elif not (ground.get("source") or "").strip():
        p.append("ground colour has no source")
    if "bs-scale" not in ctx["html"]:
        p.append("the page has no scale-panel renderer")
    n_img, art_rows = 0, 0
    for it in items:
        if not any(g.get("cols") for g in it.get("graphics", [])):
            continue
        art_rows += 1
        s = it.get("scale") or {}
        if "scale_" not in str(s.get("img") or ""):
            p.append(f"{it['id']}: no scale panel ({s.get('why') or 'scale missing'})")
            continue
        n_img += 1
        if not (s.get("source") or "").strip():
            p.append(f"{it['id']}: size has no source")
        elif s.get("status") == "fallback":
            if not str(s.get("source")).startswith("FALLBACK"):
                p.append(f"{it['id']}: fallback size whose source does not say FALLBACK")
            if not any(str(f).startswith(SIZE_FALLBACK_FLAG) for f in it.get("flags") or []):
                p.append(f"{it['id']}: FALLBACK size not flagged on the row")
        elif s.get("status") != "measured":
            p.append(f"{it['id']}: size status {s.get('status')!r} is neither measured nor flagged fallback")
        if s.get("zoomPpc") is None:
            p.append(f"{it['id']}: no max-zoom px/cell recorded")
        for key in ("img", "full"):
            f = ctx["sheet_dir"] / str(s.get(key) or "")
            if not s.get(key) or not f.is_file():
                p.append(f"{it['id']}: scale {key} image missing on disk ({s.get(key)})")
    if art_rows == 0:
        p.append("no row has art — nothing to scale (zero panels is a failed build)")
    elif n_img == 0:
        p.append("zero scale panels on the sheet")
    return Check("2", "scale panel + size source + measured ground on every row with art", p,
                 f"{n_img}/{art_rows} rows")


def check_donor_only(ctx, items) -> Check:
    p = []
    donors = [it for it in items if _donor_only(it)]
    if not donors:
        return Check("3", "no donor-only or placeholder-only row without a pending/active job", [], "0 donor-only rows")
    subs, bad = job_ids()
    if bad:
        return Check("3", "no donor-only or placeholder-only row without a pending/active job",
                     bad + [f"{len(donors)} donor-only row(s) cannot be matched to a job: " + ", ".join(d['id'] for d in donors[:8])])
    by_key = {r["key"]: r for r in (ctx.get("census_rows") or [])}
    waiting = 0
    for it in donors:
        r = by_key.get(it["id"], {"key": it["id"]})
        keys = {S.norm(S.stem(x)) for x in _rownames(r)}
        keys = {k for k in keys if len(k) >= S.MIN_KEY}
        names = set(_rownames(r))
        hit = any(s in names or any(S.token_match(s, k) for k in keys) for s in subs)
        if hit:
            waiting += 1
        else:
            ph = any(c.get("placeholder") for g in it.get("graphics", []) for c in g.get("cols", []))
            p.append(f"{it['id']}: " + ("placeholder art only (script-drawn or borrowed vanilla texture)" if ph else "donor art only")
                     + " and no pending/active render job")
    return Check("3", "no donor-only or placeholder-only row without a pending/active job", p, f"{waiting} donor-only awaiting a render")


def check_donor_column(ctx, items) -> Check:
    p = []
    by_key = {r["key"]: r for r in (ctx.get("census_rows") or [])}
    if ctx.get("census_rows") is None:
        return Check("4", "donor-sourced rows keep their donor column", ["UNMEASURED: no census rows to know which rows are donor-sourced"])
    for it in items:
        r = by_key.get(it["id"])
        if not r or not (r.get("donors") or it.get("tier") == "donor"):
            continue
        if it.get("donorPurged"):
            continue    # the owner purged the donor original: it was shown and rejected, not omitted
        if not any(c.get("kind") == "donor" and not _is_ours_label(c.get("label")) and not c.get("ours")
                   for g in it.get("graphics", []) for c in g.get("cols", [])):
            p.append(f"{it['id']}: UNMEASURED donor art - donor-sourced ({', '.join(r.get('donors') or ['donor tier'])[:60]}) but no donor original is shown or recorded as purged (only our own copy)")
    return Check("4", "donor-sourced rows keep their donor column", p)


def check_canon(ctx, items) -> Check:
    p = []
    if ctx.get("census_rows") is None:
        return Check("5", "canon beside the row, or says none", ["UNMEASURED: no census rows"])
    by_key = {r["key"]: r for r in ctx["census_rows"]}
    html = ctx["html"]
    for s in ("entry has no images", "lists no Must show"):
        if s not in html:
            p.append(f"the page cannot say '{s}' for a thin canon entry")
    for it in items:
        r = by_key.get(it["id"]) or {}
        c = it.get("canon")
        if c:
            if "imgs" not in c or "must" not in c:
                p.append(f"{it['id']}: canon block lacks images/Must show fields")
        else:
            if (r.get("canon") or {}).get("entry"):
                p.append(f"{it['id']}: census has canon entry {Path(r['canon']['entry']).name} but the row shows none")
            if not (it.get("canonTag") or it.get("noCanon")):
                p.append(f"{it['id']}: no canon entry and the row does not say so")
    return Check("5", "canon beside the row, or says none", p)


def check_failed_canon(ctx, items) -> Check:
    p = []
    fc = ctx.get("failed_canon")
    if fc is None:
        fc = failed_canon()
    fam_re = re.compile(r"_(north|east|south|west)(_r\d+)?$")
    for it in items:
        for g in it.get("graphics", []):
            for c in g.get("cols", []):
                lab = str(c.get("label") or "")
                if c.get("kind") != "artpipe" or not lab.startswith("render "):
                    continue
                fam = lab[len("render "):].removesuffix(FAILED_CANON_BADGE)
                failed = any(j == fam or fam_re.sub("", j) == fam for j in fc)
                if failed and FAILED_CANON_BADGE not in lab:
                    p.append(f"{it['id']} {c.get('letter')}: render {fam} failed the canon gate but is not badged")
                if not failed and FAILED_CANON_BADGE in lab:
                    p.append(f"{it['id']} {c.get('letter')}: badged failed-canon but the gate record says it passed")
    if not artpipe_dir().joinpath("failed").is_dir():
        p.append(f"UNMEASURED: no artpipe failed/ dir at {artpipe_dir() / 'failed'} — badges cannot be verified")
    return Check("6", "failed-canon renders badged", p)


def check_ruled_elsewhere(ctx, items) -> Check:
    p = []
    try:
        import art_sheet as A
        ents = A.ruled_elsewhere(ctx["sheet_dir"], ctx["sheet_id"], {})
    except Exception as e:  # noqa: BLE001
        return Check("7", "rows ruled elsewhere are collapsed", [f"UNMEASURED: {type(e).__name__}: {e}"])
    own = {k for k, v in ((ctx.get("decisions") or {}).get("decisions") or {}).items() if isinstance(v, dict) and v.get("at")}
    by_key = {r["key"]: r for r in (ctx.get("census_rows") or [])}
    n = 0
    for it in items:
        if it["id"] in own:
            continue
        r = by_key.get(it["id"], {"key": it["id"]})
        names = set().union(*[A._subject_names(x) for x in _rownames(r)])
        hit = A.ruled_elsewhere_for(names, ents)
        if not hit:
            continue
        n += 1
        if not it.get("ruledElsewhere") or it.get("group") != RULED_GROUP:
            p.append(f"{it['id']}: ruled on {hit['sheet_id']} ({hit['decision']}) but shown as a live row")
    items_ids = [it["id"] for it in items]
    tail = [it for it in items if it.get("ruledElsewhere")]
    if tail and items_ids[-len(tail):] != [it["id"] for it in tail]:
        p.append("collapsed rows are not all at the bottom")
    return Check("7", "rows ruled elsewhere are collapsed, not repeated", p, f"{n} collapsed")


def check_letters(ctx, items) -> Check:
    dec = ctx.get("decisions")
    touched = bool(dec) and (bool(dec.get("savedBy")) or bool(dec.get("writeCount")) or
                             any(isinstance(v, dict) and v.get("at") for v in (dec.get("decisions") or {}).values()))
    if not touched:
        return Check("8", "his picks never move (letter_mismatches == 0)", [], "decisions untouched by him")
    snap = ctx.get("snap")
    if snap is None:
        return Check("8", "his picks never move (letter_mismatches == 0)", ["UNMEASURED: no snapshot to compare against"])
    sid = dec.get("snapshotId")
    if not sid:
        return Check("8", "his picks never move (letter_mismatches == 0)", ["UNMEASURED: touched decisions name no snapshotId"])
    ruled = L.snapshot_by_id(ctx["snap_path"], sid)
    if ruled is None:
        return Check("8", "his picks never move (letter_mismatches == 0)",
                     [f"UNMEASURED: the snapshot {sid} his decisions name is neither on disk nor in git history"])
    bad = L.letter_mismatches(dec, ruled, snap)
    return Check("8", "his picks never move (letter_mismatches == 0)",
                 [f"{r}:{l} names different pictures than in snapshot {sid}" for r, l in bad], f"snapshot {sid}")


def check_purge_wired(ctx, items) -> Check:
    return Check("11", "per-picture x is reject-and-purge", [] if "purge" in ctx["html"] else ["the page has no purge control"])


def check_no_purged(ctx, items) -> Check:
    """Req 14 (exception: a purged picture that is still the live IN GAME column is allowed when flagged purgedLive and
    non-pickable) (owner 2026-10-05: "delete the graphics I already indicated we should purge, so I don't keep seeing and
    reviewing them"): no picture the art ledger has purged is rendered as a column, on any sheet."""
    fn = ctx.get("is_purged")
    if fn is None:
        try:
            idx = L.Index()
        except Exception as e:  # noqa: BLE001
            return Check("14", "no purged picture shown", [f"UNMEASURED: art ledger unreadable ({type(e).__name__}: {e})"])
        fn = idx.is_purged
    p = []
    for it in items:
        for g in it.get("graphics", []):
            for c in g.get("cols", []):
                bad = [sh[:10] for sh in (c.get("faces") or {}).values() if fn(sh)]
                if bad and c.get("purgedLive") and c.get("winner"):
                    # purged but still the game's IN GAME picture: shown for reference, must be non-pickable
                    if c.get("purgeable") or c.get("letter") in (it.get("letters") or []):
                        p.append(f"{it['id']} {c.get('letter')}: purged-but-live picture is pickable")
                    continue
                if bad:
                    p.append(f"{it['id']} {c.get('letter')}: purged {', '.join(bad)} still shown")
    return Check("14", "no ledger-purged picture is shown as a column", p)


def check_urls(ctx, items) -> Check:
    base = ctx["sheet_id"]
    log = ctx["sheet_dir"] / f"{base}.serve.log"
    if not log.is_file():
        return Check("10", "served link answers 200", [f"UNMEASURED: no {log.name}"])
    m = re.search(r"http://localhost:\d+/\?t=[A-Za-z0-9_-]+", log.read_text(errors="replace"))
    if not m:
        return Check("10", "served link answers 200", [f"UNMEASURED: no URL in {log.name}"])
    try:
        with urllib.request.urlopen(m.group(0), timeout=5) as r:
            ok = r.status == 200
    except Exception as e:  # noqa: BLE001
        return Check("10", "served link answers 200", [f"{m.group(0)} did not answer: {type(e).__name__}"])
    return Check("10", "served link answers 200", [] if ok else [f"{m.group(0)} answered non-200"])


def check_check_sheet(ctx, items) -> Check:
    fn = ctx.get("check_sheet_fn")
    if fn is None:
        def fn(path, dec):
            if not CHECK_SHEET.is_file():
                return 2, f"{CHECK_SHEET} missing"
            cmd = [sys.executable, str(CHECK_SHEET), str(path)] + (["--decisions", str(dec)] if dec else [])
            r = subprocess.run(cmd, capture_output=True, text=True)
            return r.returncode, (r.stdout + r.stderr)
    dp = ctx.get("decisions_path")
    rc, out = fn(ctx["html_path"], dp if dp and Path(dp).is_file() else None)
    if rc == 0:
        return Check("9/chk", "check_sheet exits 0", [])
    fails = [l.strip() for l in str(out).splitlines() if "FAIL" in l][:4]
    return Check("9/chk", "check_sheet exits 0", [f"check_sheet exit {rc}" + (": " + " | ".join(fails) if fails else "")])


EDGE = "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"


def browser_render(html_path, decisions_path=None):
    import gate_browser
    return gate_browser.browser_render(html_path, decisions_path)


def check_browser(ctx, items) -> Check:
    """Req 13 (owner 2026-10-05, empty sheets): the page must RENDER in a real browser — no uncaught error, and the
    rendered <img> count not far below what the data holds (one row with a null field once blanked a whole sheet)."""
    fn = ctx.get("browser_fn") or browser_render
    call = (lambda: fn(ctx["html_path"])) if ctx.get("browser_fn") else (lambda: fn(ctx["html_path"], ctx.get("decisions_path")))
    n, errs, prob = call()
    if (prob and "Timeout" in prob) or (not prob and n == 0 and not ctx.get("browser_fn")):
        n, errs, prob = call()          # Edge flakes under load (timeouts, an early empty dump): one retry before a FAIL
    if prob:
        return Check("13", "page renders in a real browser", [prob])
    p = [f"uncaught console error: {e}" for e in errs[:3]]
    rows = [it for it in items if not it.get("ruledElsewhere")]
    want = sum(1 for it in rows if (it.get("scale") or {}).get("img"))      # every live row with art shows at least its scale panel
    if n < max(1, want // 2):
        p.append(f"only {n} <img> rendered for {len(rows)} live rows ({want} with scale panels) — the sheet renders blank")
    return Check("13", "page renders in a real browser", p, f"{n} img")


CHECKS = (check_one_biome, check_scale, check_donor_only, check_donor_column, check_canon, check_failed_canon,
          check_ruled_elsewhere, check_letters, check_purge_wired, check_check_sheet, check_no_purged, check_browser)


def run_gate(ctx: dict, urls: bool = False) -> list[Check]:
    """Run every check. ctx: html, sheet_id, sheet_dir, html_path, snap, snap_path, decisions, decisions_path,
    biome, ground, census_rows, [problems, failed_canon, check_sheet_fn]."""
    out = [Check("0", "inputs readable", ctx.get("problems") or [])]
    items = _items(ctx)
    if not isinstance(items, list) or not items:
        out.append(Check("0", "ITEMS block", ["UNMEASURED: the page has no readable ITEMS list"]))
        return out
    for fn in CHECKS:
        if fn is check_browser and (ctx.get("skip_browser") or SKIP_BROWSER):
            continue
        try:
            out.append(fn(ctx, items))
        except Exception as e:  # noqa: BLE001  a check that blows up is a FAIL, never a pass
            out.append(Check("?", fn.__name__, [f"UNMEASURED: check crashed {type(e).__name__}: {e}"]))
    if urls:
        out.append(check_urls(ctx, items))
    return out


def report(sheet: str, checks: list[Check], limit: int = 12) -> str:
    bad = [c for c in checks if not c.ok]
    head = f"{'PASS' if not bad else 'FAIL'} {sheet}" + (f"  ({len(bad)} failing: req " + ", ".join(c.req for c in bad) + ")" if bad else "")
    return "\n".join([head] + [c.line(limit) for c in (bad if bad else [])])


def _move_into_place(tmp: Path, final: Path) -> None:
    for i in range(5):
        try:
            os.replace(tmp, final)
            return
        except OSError:
            import time
            time.sleep(0.4 * (i + 1))
    final.write_text(tmp.read_text())   # drvfs rename refused while a Windows process holds the file
    tmp.unlink(missing_ok=True)


def banner(checks: list[Check], reason: str) -> str:
    bad = "; ".join(f"req {c.req} {c.name}" for c in checks if not c.ok)
    return ('<div style="background:#7a1f1f;color:#fff;padding:6px 10px;font:13px sans-serif">GATE OVERRIDE — this sheet FAILS the '
            f'scaled-review gate ({bad}). Shown only because: {reason}. Not stamped; it will be replaced when it passes.</div>')


def enforce(html: str, ctx: dict, out_html: Path, allow_failing: str | None = None) -> list[Check]:
    """The build-time hard gate. Writes HTML to `<out_html>.gate.tmp`, runs the gate on it, and only on a pass moves it
    (stamped) onto OUT_HTML. On failure the tmp file is removed, the previous out_html is untouched, GateFailed is raised."""
    out_html = Path(out_html)
    tmp = out_html.with_name(out_html.stem + ".gate.tmp.html")
    tmp.write_text(html)
    try:
        ctx = dict(ctx, html=html, html_path=tmp)
        checks = run_gate(ctx)
        if any(not c.ok for c in checks):
            # the ONE exception: the sheet being replaced is itself unusable (renders blank), so a rendering sheet that
            # still fails other requirements is shown, UNSTAMPED and with a red banner naming what fails
            if allow_failing and not any(c.req == "13" and not c.ok for c in checks):
                m = re.search(r"<body[^>]*>", html)
                tmp.write_text(html[:m.end()] + banner(checks, allow_failing) + html[m.end():] if m else banner(checks, allow_failing) + html)
                return checks
            raise GateFailed(out_html.name, checks)
        tmp.write_text(stamp(html))
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    return checks


def commit(tmp_final: Path, out_html: Path) -> None:
    _move_into_place(Path(tmp_final), Path(out_html))


# ───────────────────────────────────────────────────────────────── cli ──

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["check", "all", "verify-stamp"])
    ap.add_argument("sheets", nargs="*")
    ap.add_argument("--urls", action="store_true", help="also require each sheet's served link to answer 200 (req 10)")
    ap.add_argument("--stamp", action="store_true", help="stamp every sheet that PASSES (a passing sheet only; failing ones are untouched)")
    ap.add_argument("--out", help="write the full report here")
    a = ap.parse_args(argv)
    if a.cmd == "verify-stamp":
        rc = 0
        for s in a.sheets:
            ok, msg = verify_stamp(Path(s).read_text())
            print(("OK   " if ok else "REFUSED ") + f"{s}: {msg}")
            rc |= 0 if ok else 1
        return rc
    paths = [Path(s) for s in a.sheets] if a.cmd == "check" else [p for p in sorted(SHEET_DIR.glob("*_sheet_*.html")) if SHEET_RE.match(p.name)]
    if not paths:
        print("no sheets given/found")
        return 2
    lines, npass = [], 0
    for p in paths:
        ctx = load_ctx(p)
        checks = run_gate(ctx, urls=a.urls)
        ok = all(c.ok for c in checks)
        npass += ok
        lines.append(report(p.name, checks, limit=40 if a.out else 6))
        if ok and a.stamp:
            new = stamp(ctx["html"])
            if new != ctx["html"]:
                tmp = p.with_name(p.stem + ".gate.tmp.html")
                tmp.write_text(new)
                _move_into_place(tmp, p)
    text = "\n".join(lines) + f"\n{npass}/{len(paths)} sheets pass the scaled-review gate"
    if a.out:
        Path(a.out).write_text(text + "\n")
        print("\n".join(l.split("\n")[0] for l in lines) + f"\n{npass}/{len(paths)} pass; report -> {a.out}")
    else:
        print(text)
    return 0 if npass == len(paths) else 1


if __name__ == "__main__":
    sys.exit(main())
