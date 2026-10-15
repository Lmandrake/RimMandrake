#!/usr/bin/env python3
"""sheet_freshness.py — an art review sheet never shows a picture that is not what it claims to be.

    python3 sheet_freshness.py verify <sheet.html>...     per-row FRESH / STALE, exit 5 when any row is stale
    python3 sheet_freshness.py scan [--res <texPath>...]  every sheet under Transient/, stale ones listed
    python3 sheet_freshness.py --selftest

THE INVARIANT (ART_SHEET_REDESIGN_FRESH_OR_REFUSE, owner 2026-10-12: "it needs some kind of hook or ensurance that it's
not serving stale information. By construction, by design, by hashes"): every picture a served sheet labels as
installed IS the bytes installed now, every picture installed now for a texPath the sheet shows IS on the sheet as
installed, and every texPath our defs draw (src XML, never a dump or census) is a graphic on the sheet. Candidates
(renders, history, donor originals) are content-addressed by sha256 and cannot go stale.

Nothing here is a cache. `verify` re-measures, on every call: our mods' Textures folders on disk (sha256 of each file),
the def XML in src/ (subject.World), and the sheet's own thumbnails. The sheet's ITEMS block is the claim; so a sheet
built before this module existed is verified too. A sheet built after it also carries a FRESHNESS block (defs per
row, where each texPath came from, the sha256 of every thumbnail and input file), checked the same way.

Where it runs: the gate (scaled_review_gate req 15, so a sheet stale at birth is never written and refresh_sheets
rebuilds one that went stale), serve_gated.py (refuses to start, and re-checks on every page load), and art.py
install / enact --apply (print which sheets the install just made stale).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402

SCHEMA = 1
FRESH_RE = re.compile(r'<script id="FRESHNESS" type="application/json">(.*?)</script>', re.S)
ITEMS_RE = re.compile(r'<script id="ITEMS"[^>]*>(.*?)</script>', re.S)
EXIT_STALE = 5

_SHA: dict = {}


def _sha_file(p: Path) -> str:
    st = p.stat()
    k = (str(p), st.st_size, st.st_mtime_ns)
    if k not in _SHA:
        _SHA[k] = L.sha256_file(p)
    return _SHA[k]


# ─────────────────────────────────────────────────────────── what is installed ──

def texture_roots(repo: Path | None = None) -> list[tuple[str, Path]]:
    """(mod, Textures dir) for every mod of ours under src/, measured now. mod is repo-relative, as the art ledger keys it."""
    repo = repo or L.REPO_ROOT
    out = []
    for dp, dns, _ in os.walk(repo / "src"):
        if "Textures" in dns:
            t = Path(dp) / "Textures"
            out.append((str(Path(dp).relative_to(repo)), t))
        dns[:] = [d for d in dns if d not in ("Textures", "Defs", "Patches", "Languages", "Sounds", "Assemblies", "bin",
                                              "obj", "Source", "node_modules", ".git", "__pycache__", "art_source")]
    return out


def installed(res: str, roots: list[tuple[str, Path]]) -> dict:
    """{(mod, rel): sha256} — every non-mask picture our mods ship on disk NOW for texPath `res`: the file(s) at it
    (`res.png`, `res_<facing>.png`) and, where `res` is a folder (Graphic_Random / Graphic_Collection), each picture
    directly inside it (masks excluded by the same rule as art_sheet.random_folder_variants)."""
    out = {}
    low = res.lower()
    parent, _, name = res.rpartition("/")
    for mod, t in roots:
        d = t / parent if parent else t
        if d.is_dir():
            for f in d.iterdir():
                if f.is_file() and f.suffix.lower() == ".png" and f.name.lower().startswith(name.lower()):
                    rel = f"{parent}/{f.name}" if parent else f.name
                    pt = L.parse_texfile(rel)
                    if pt["res"].lower() == low and not pt["mask"]:
                        out[(mod, rel)] = _sha_file(f)
        fd = t / res
        if fd.is_dir():
            files = {f.name[:-4]: f for f in fd.iterdir() if f.is_file() and f.suffix.lower() == ".png"}
            stems = {}
            for n, f in files.items():
                pt = L.parse_texfile(n + ".png")
                if not pt["mask"]:
                    stems.setdefault(pt["res"], []).append(f)
            for s, fs in stems.items():
                if (s.endswith("_m") and s[:-2] in stems) or (s.endswith("m") and s[:-1] in stems):
                    continue
                for f in fs:
                    out[(mod, f"{res}/{f.name}")] = _sha_file(f)
    return out


# ─────────────────────────────────────────────────────────── what our defs draw ──

def src_texpaths(defs, world) -> dict:
    """{texPath: role} our defs draw, from the src XML now (subject.World: parsed, never a dump or census). {} for a
    def that is not ours (a donor or vanilla def: the dump is the only source there, and it is not verified)."""
    out = {}
    tbd = world.tex_by_def
    slots = world.slots
    for d in defs:
        for tp in sorted(tbd.get(d, ())):
            role = next((s["role"] for s in slots.get(tp, []) if s["subject"].split("#")[0] == d), None) or \
                next((s["role"] for s in slots.get(tp, [])), "body")
            out.setdefault(tp, role)
    return out


def fresh_resources(row: dict, world) -> tuple[list, list]:
    """A census row's art.resources re-resolved from src now. Returns (resources, notes). The census (an Oct-7 list
    while this was written) is a cache: where src disagrees, src wins and the row says so."""
    res = list((row.get("art") or {}).get("resources") or [])
    defs = [x for x in dict.fromkeys([row.get("key"), row.get("port"), *(row.get("defNames") or [])]) if x]
    now = {tp: role for tp, role in src_texpaths(defs, world).items()
           if not tp.lower().endswith(("_dessicated", "_desiccated", "_corpse"))}
    if not now:
        return res, []
    have = {r["res"]: r for r in res}
    if set(have) == set(now):
        return res, []
    keep = [have[tp] for tp in have if tp in now]
    add = [{"res": tp, "role": role, "joined_by": "def (src XML at build)", "subjects": defs}
           for tp, role in now.items() if tp not in have]
    gone = sorted(set(have) - set(now))
    note = (f"{row.get('key')}: census texPaths {sorted(have)} are STALE; our defs draw {sorted(now)} (src XML)"
            + (f" — dropped {gone}" if gone else ""))
    return keep + add, [note]


# ─────────────────────────────────────────────────────────── the manifest ──

def _git_head() -> str:
    try:
        import subprocess
        return subprocess.run(["git", "-C", str(L.REPO_ROOT), "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, timeout=10).stdout.strip()
    except Exception:                                   # noqa: BLE001
        return ""


def build_manifest(items: list, sheet_dir: Path, census_rows: list, inputs: dict | None = None) -> dict:
    by_key = {r.get("key"): r for r in census_rows or []}
    rows = {}
    for it in items:
        r = by_key.get(it.get("id")) or {}
        defs = [x for x in dict.fromkeys([r.get("key"), r.get("port"), *(r.get("defNames") or []),
                                          _desc_def(it)]) if x]
        srcs = {x["res"]: x.get("joined_by") or "?" for x in (r.get("art") or {}).get("resources") or []}
        rows[it["id"]] = {"defs": defs, "texpaths": srcs}
    thumbs = {}
    for it in items:
        for rel in (it.get("thumbs") or {}).values():
            p = Path(sheet_dir) / rel
            if p.is_file():
                thumbs[rel] = _sha_file(p)
    ins = {}
    for k, p in (inputs or {}).items():
        p = Path(p)
        if p.is_file():
            ins[k] = {"path": str(p.relative_to(L.REPO_ROOT)) if p.is_relative_to(L.REPO_ROOT) else str(p),
                      "sha256": _sha_file(p)}
    return {"schema": SCHEMA, "built": L.now(), "git_head": _git_head(), "rows": rows, "thumbs": thumbs, "inputs": ins}


def embed(html: str, manifest: dict) -> str:
    tag = '<script id="FRESHNESS" type="application/json">' + json.dumps(manifest, sort_keys=True).replace("</", "<\\/") + "</script>"
    html = FRESH_RE.sub("", html)
    return html.replace("</body>", tag + "\n</body>", 1) if "</body>" in html else html + tag


def read_manifest(html: str) -> dict | None:
    m = FRESH_RE.search(html)
    if not m:
        return None
    try:
        return json.loads(m.group(1).replace("<\\/", "</"))
    except ValueError:
        return None


def read_items(html: str) -> list | None:
    m = ITEMS_RE.search(html)
    if not m:
        return None
    try:
        v = json.loads(m.group(1).replace("<\\/", "</"))
    except ValueError:
        return None
    return v if isinstance(v, list) else None


# ─────────────────────────────────────────────────────────── verify ──

class Ctx:
    """One measurement of the world: Textures roots, the src defs, the art ledger's purges. Built per verify call
    (a server memoises it for a few seconds only, so a page load never sees a world older than that)."""

    def __init__(self, world=None, idx=None, roots=None):
        import subject as S
        self.world = world or S.World()
        self.idx = idx if idx is not None else L.Index()
        self.roots = roots if roots is not None else texture_roots()
        self.at = time.time()


def _desc_def(it: dict):
    d = it.get("desc")
    return d.get("def") if isinstance(d, dict) else None


def _real(res) -> bool:
    return bool(res) and not str(res).startswith("_")


def verify_items(items: list, sheet_dir: Path, ctx: Ctx, manifest: dict | None = None) -> dict:
    """{row id: [reasons]} for every STALE row ({} = fresh), plus "_sheet" for sheet-level problems."""
    stale: dict = {}
    mrows = (manifest or {}).get("rows") or {}

    def bad(k, why):
        stale.setdefault(k, []).append(why)

    for it in items:
        rid = it.get("id", "?")
        graphics = it.get("graphics") or []
        live_shas, shown = set(), {}
        for g in graphics:
            for c in g.get("cols") or []:
                for sh in (c.get("faces") or {}).values():
                    shown.setdefault(sh, c.get("label", ""))
                    if c.get("kind") == "live" and _real(g.get("res")):
                        live_shas.add(sh)
                if c.get("kind") == "kept" and str(c.get("label", "")).startswith("IN GAME"):
                    bad(rid, f"column {c.get('letter')} is labelled '{c['label'][:80]}' but is a kept set no longer installed")
        # 1. installed now <-> shown as installed
        disk = {}
        for g in graphics:
            if _real(g.get("res")):
                for (mod, rel), sh in installed(g["res"], ctx.roots).items():
                    disk.setdefault(sh, []).append(f"{mod}/Textures/{rel}")
        for sh, paths in sorted(disk.items()):
            if sh in live_shas:
                continue
            if sh not in shown and ctx.idx.is_purged(sh):
                continue          # a purged picture still on disk in a shadowed mod: hidden by req 14, not stale
            where = f" (the sheet shows it only as '{shown[sh][:70]}')" if sh in shown else " (not on the sheet at all)"
            bad(rid, f"installed now but not shown as installed: {paths[0]} sha {sh[:12]}{where}")
        for sh in sorted(live_shas - set(disk)):
            bad(rid, f"shows '{shown.get(sh, '')[:70]}' (sha {sh[:12]}) as installed, but no file of ours holds those bytes now")
        # 2. every texPath our defs draw is on the row
        defs = (mrows.get(rid) or {}).get("defs") if rid in mrows else \
            [x for x in dict.fromkeys([rid, _desc_def(it)]) if x]
        want = {tp for tp in src_texpaths(defs or [], ctx.world)
                if not tp.lower().endswith(("_dessicated", "_desiccated", "_corpse"))}
        have = {g["res"] for g in graphics if _real(g.get("res"))} | \
            {str(g.get("res"))[6:] for g in graphics if str(g.get("res") or "").startswith("_flip:")}
        # missing = a texPath our defs draw that has installed art of ours the row does not show. A texPath with no file of
        # ours (art not made yet, or drawn from a donor/vanilla folder) has no picture the build could show, and one whose
        # bytes are all on the row already (identical files folded by the build's de-duplication) is shown.
        miss = sorted(tp for tp in want - have
                      if (inst := set(installed(tp, ctx.roots).values())) and not inst <= set(shown))
        if miss and have:
            bad(rid, f"our defs ({', '.join(defs)}) draw {miss} (src XML now); the row shows {sorted(have)}")
        # 3. thumbnails
        for rel in (it.get("thumbs") or {}).values():
            p = Path(sheet_dir) / rel
            if not p.is_file():
                bad(rid, f"thumbnail {rel} is missing")
            elif manifest and rel in (manifest.get("thumbs") or {}) and manifest["thumbs"][rel] != _sha_file(p):
                bad(rid, f"thumbnail {rel} changed since the build")
    for k, v in ((manifest or {}).get("inputs") or {}).items():
        p = L.REPO_ROOT / v["path"] if not os.path.isabs(v["path"]) else Path(v["path"])
        if not p.is_file():
            bad("_sheet", f"input {k} ({v['path']}) is gone")
        elif _sha_file(p) != v["sha256"]:
            bad("_sheet", f"input {k} ({v['path']}) changed since the build")
    return stale


def verify_html(html_path: Path, ctx: Ctx | None = None, html: str | None = None) -> dict:
    """{"fresh": bool, "rows": n, "stale": {row: [reasons]}, "manifest": bool, "error": str|None}"""
    html_path = Path(html_path)
    html = html if html is not None else html_path.read_text()
    items = read_items(html)
    if items is None:
        return {"fresh": False, "rows": 0, "stale": {}, "manifest": False,
                "error": "no readable ITEMS block: freshness UNMEASURED, so the sheet cannot be served as fresh"}
    man = read_manifest(html)
    st = verify_items(items, html_path.parent, ctx or Ctx(), man)
    return {"fresh": not st, "rows": len(items), "stale": st, "manifest": man is not None, "error": None}


def report(sheet: str, r: dict, limit: int = 40) -> str:
    if r.get("error"):
        return f"STALE {sheet}: {r['error']}"
    if r["fresh"]:
        return f"FRESH {sheet}: {r['rows']} rows" + ("" if r["manifest"] else " (no FRESHNESS block: built before it; ITEMS verified)")
    lines = [f"STALE {sheet}: {len(r['stale'])} of {r['rows']} rows"]
    n = 0
    for k, whys in r["stale"].items():
        for w in whys:
            n += 1
            if n <= limit:
                lines.append(f"  {k}: {w}")
    if n > limit:
        lines.append(f"  … +{n - limit} more")
    return "\n".join(lines)


def refusal_page(sheet: str, r: dict) -> bytes:
    import html as H
    body = H.escape(report(sheet, r, limit=200))
    return ("<!doctype html><meta charset=utf-8><title>STALE sheet refused</title>"
            "<body style='font:14px sans-serif;background:#2b1a12;color:#f3e3c8;padding:16px'>"
            "<h2 style='color:#ff9a6a'>This sheet is STALE — refused</h2>"
            "<p>Pictures on it are no longer what the game has installed, so it is not shown "
            "(ART_SHEET_REDESIGN_FRESH_OR_REFUSE). Rebuild it with <code>art_sheet.py</code> (same arguments) or "
            "<code>refresh_sheets.py</code>; this page re-checks on every load.</p>"
            f"<pre style='white-space:pre-wrap'>{body}</pre></body>").encode()


def stale_banner(sheet: str, r: dict) -> str:
    import html as H
    return ("<div id='stale-banner' style='position:sticky;top:0;z-index:99999;background:#7a1f1f;color:#fff;"
            "padding:8px 12px;font:13px sans-serif;max-height:40vh;overflow:auto'><b>STALE SHEET</b> — served on request; "
            "these rows do NOT show what is installed now. Do not rule on them.<pre style='white-space:pre-wrap;margin:4px 0'>"
            + H.escape(report(sheet, r, limit=200)) + "</pre></div>")


def all_sheets(root: Path | None = None) -> list[Path]:
    root = root or (L.REPO_ROOT / "Transient")
    return sorted(p for p in root.rglob("*_sheet_*.html") if ".gate.tmp" not in p.name)


def sheets_showing(res_list, root: Path | None = None) -> list[Path]:
    want = set(res_list)
    out = []
    for p in all_sheets(root):
        items = read_items(p.read_text(errors="replace")) or []
        if any(g.get("res") in want for it in items for g in it.get("graphics") or []):
            out.append(p)
    return out


def after_install(res_list, out=sys.stderr) -> list[Path]:
    """The install-side hook: which sheets showing these texPaths are stale now. Printed, never fatal (the install
    has happened; the serve path refuses them regardless)."""
    try:
        hits = sheets_showing(res_list) if res_list is not None else [p for p in all_sheets()
                                                                       if read_items(p.read_text(errors="replace"))]
        if not hits:
            return []
        ctx = Ctx()
        stale = []
        for p in hits:
            r = verify_html(p, ctx)
            if not r["fresh"]:
                stale.append(p)
                print(f"SHEET NOW STALE (refused when served until rebuilt): {p.relative_to(L.REPO_ROOT)} "
                      f"— {len(r['stale'])} row(s)", file=out)
        return stale
    except Exception as e:                              # noqa: BLE001
        print(f"sheet freshness scan after install: UNMEASURED ({type(e).__name__}: {e})", file=out)
        return []


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["verify", "scan"], nargs="?")
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--res", action="append", default=[])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        import selftest_sheet_freshness
        return selftest_sheet_freshness.main()
    ctx = Ctx()
    paths = [Path(p) for p in a.paths] if a.cmd == "verify" else \
        (sheets_showing(a.res) if a.res else all_sheets())
    worst = 0
    res = {}
    for p in paths:
        r = verify_html(p, ctx)
        res[str(p)] = r
        if not a.json:
            print(report(str(p), r, limit=8 if a.cmd == "scan" else 40))
        worst = max(worst, 0 if r["fresh"] else EXIT_STALE)
    if a.json:
        print(json.dumps(res, indent=1))
    return worst


if __name__ == "__main__":
    sys.exit(main())
