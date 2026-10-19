#!/usr/bin/env python3
"""serve_gated.py — the only way to start a biome art sheet server. Refuses an HTML without a valid gate stamp.

    python3 serve_gated.py --no-open --sheet <x_sheet_date>.html --decisions <x_sheet_date>.decisions.json

A sheet that declares `sheet-kind: non-art` takes the checked non-art route (nonart_sheet.py) instead of a stamp — and
that route refuses any sheet whose PICTURES are game art (game_art.classify), whatever it declares.
Same arguments as the review-sheets skill's serve_sheet.py (it is exec'd after the check). A sheet that never passed
`scaled_review_gate` (no stamp), or was edited after it (stamp mismatch), is REFUSED with exit 4 and nothing starts.
Stamp: `python3 scaled_review_gate.py check <sheet> --stamp` (stamps only a passing sheet).
STALE ROWS ARE LABELLED, NOT THE SHEET REFUSED (owner, by card 2026-10-19: "How far do we go to make art review fast
and reliable? → Python command, no agent before you see it", relaxing his 2026-10-14 card "stale sheets are refused" to
"stale rows are refused"). Freshness is still re-measured from disk (sheet_freshness.verify_html) at start and on every
page load. A row that no longer shows what is installed is served with a red `STALE: <reason>` badge and its pick
controls switched off (notes and the per-picture delete still work: both are content-addressed); the other rows are
usable. A sheet-level input change gets a banner. Only a page with NO readable ITEMS block (freshness unmeasurable) is
refused, exit 5; a measurement that throws marks EVERY row stale (fail closed) rather than serving it as fresh.
"""
import hashlib
import json
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

STALE_JS = r"""<script id="STALE_ROWS" type="application/json">%s</script>
<style>.bs-stale{background:#8a1f1f;color:#fff;font:bold 12px/1.35 sans-serif;padding:4px 9px;border-radius:4px;margin:3px 0 5px;display:block}
.row-stale{outline:2px solid #c0392b;outline-offset:-2px}.row-stale [data-act]:not([data-act=purge]){opacity:.45;cursor:not-allowed}
#stale-banner{position:sticky;top:0;z-index:50;background:#8a1f1f;color:#fff;font:bold 13px sans-serif;padding:6px 12px}</style>
<script>(() => {
  const S = JSON.parse(document.getElementById('STALE_ROWS').textContent), rows = S.rows || {}, all = S.all || null;
  const why = id => rows[id] || all;
  const paint = () => {
    if ((S.sheet || all) && !document.getElementById('stale-banner')) {
      const b = document.createElement('div'); b.id = 'stale-banner';
      b.textContent = 'STALE: ' + (all ? all.join(' · ') : 'sheet inputs changed since the build: ' + S.sheet.join(' · ')).slice(0, 400)
        + (S.n ? ' — ' + S.n + ' row(s) labelled; picks on them are off until the sheet is rebuilt, notes still save' : '');
      document.body.prepend(b);
    }
    document.querySelectorAll('.row[data-id]').forEach(el => {
      const w = why(el.dataset.id); if (!w) return;
      el.classList.add('row-stale');
      if (!el.querySelector('.bs-stale')) {
        const b = document.createElement('div'); b.className = 'bs-stale';
        b.textContent = 'STALE: ' + w.join(' · ').slice(0, 300) + ' — picks on this row are off until it is rebuilt; your note still saves';
        el.prepend(b);
      }
    });
  };
  /* window capture runs before the page's own document-level handler: a pick on a stale row never reaches SLX */
  const block = e => { const a = e.target.closest && e.target.closest('[data-act]'); if (!a || a.dataset.act === 'purge') return;
    const r = a.closest('.row[data-id]'); if (!r || !why(r.dataset.id)) return;
    e.preventDefault(); e.stopImmediatePropagation();
    if (e.type === 'click') alert('This row is STALE (' + why(r.dataset.id).join(' · ').slice(0, 200) + '). Picks on it are off until the sheet is rebuilt; type in the note instead.'); };
  addEventListener('click', block, true); addEventListener('change', block, true);
  new MutationObserver(paint).observe(document.documentElement, {childList: true, subtree: true});
  addEventListener('load', paint); paint();
})();</script>"""


def stale_payload(r: dict) -> dict | None:
    """{rows: {row: [reasons]}, sheet: [reasons], all: [reasons]|None, n} or None when nothing is stale."""
    if r.get("error"):
        return {"rows": {}, "sheet": [], "all": [r["error"]], "n": r.get("rows") or 0}
    st = dict(r.get("stale") or {})
    sheet = st.pop("_sheet", [])
    if not st and not sheet:
        return None
    return {"rows": st, "sheet": sheet, "all": None, "n": len(st)}


def label_stale(html: bytes, r: dict) -> bytes:
    """The served page with every stale row badged (and its picks off). A fresh sheet is returned byte-identical."""
    pay = stale_payload(r)
    if pay is None:
        return html
    tag = (STALE_JS % json.dumps(pay).replace("</", "<\\/")).encode("utf-8")
    low = html.lower()
    at = low.rfind(b"</body>")
    return html[:at] + tag + html[at:] if at != -1 else html + tag


def fresh_gate(sheet: Path):
    """Freshness on every page load: returns a function html_bytes -> bytes that re-measures the sheet against disk and
    LABELS each stale row on the served page (owner, by card 2026-10-19). Only a page with no readable ITEMS block is
    replaced by the refusal page: there is nothing to label."""
    import sheet_freshness as FR
    memo = {"at": 0.0, "key": None, "r": None, "said": None}

    def gate(html: bytes) -> bytes:
        key = hashlib.sha256(html).hexdigest()
        if memo["key"] != key or time.time() - memo["at"] > FRESH_MEMO_S:
            try:
                memo["r"] = FR.verify_html(sheet, html=html.decode("utf-8", "replace"))
            except Exception as e:      # noqa: BLE001  unmeasured is labelled stale everywhere, never served as fresh
                memo["r"] = {"fresh": False, "rows": 0, "stale": {}, "manifest": False,
                             "error": f"freshness UNMEASURED ({type(e).__name__}: {e})", "measure_failed": True}
            memo.update(at=time.time(), key=key)
        r = memo["r"]
        if r["fresh"]:
            return html
        line = FR.report(sheet.name, r, limit=10)
        if line != memo["said"]:                       # once per change, not once per page load
            print(line, file=sys.stderr, flush=True)
            memo["said"] = line
        if r.get("error") and not r.get("measure_failed"):
            return FR.refusal_page(sheet.name, r)
        return label_stale(html, r)
    return gate


def startup_freshness(p: Path, ctx=None) -> int:
    """0 = serve (stale rows, if any, are labelled on the page); 5 = refused (no readable ITEMS: nothing to label)."""
    import sheet_freshness as FR
    r = FR.verify_html(p, ctx)
    if r.get("error"):
        print(f"REFUSED serve_gated: {FR.report(p.name, r, limit=20)}", file=sys.stderr)
        return 5
    if not r["fresh"]:
        print(f"SERVING WITH STALE ROWS LABELLED: {FR.report(p.name, r, limit=20)}\nEach stale row shows a STALE badge and "
              f"its picks are off; rebuild (art_sheet.py with the same arguments) to clear them.", file=sys.stderr, flush=True)
    return 0


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
    # freshness re-measured at start and on every page load (owner 2026-10-12); since his card of 2026-10-19 a stale ROW is
    # labelled and its picks switched off, and the rest of the sheet serves
    rc = startup_freshness(p)
    if rc:
        return rc
    return serve_with_followed_guard(argv, fresh=fresh_gate(p))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
