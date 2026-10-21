#!/usr/bin/env python3
"""selftest_sheet_freshness.py — an art review sheet never shows a picture that is not what it claims to be
(ART_SHEET_REDESIGN_FRESH_OR_REFUSE, owner 2026-10-12).

  (a) a sheet built, then the art changed on disk -> verify flags the changed row, gate req 15 fails, and serve_gated
      serves the sheet with THAT ROW badged STALE and its picks off (owner, by card 2026-10-19; was: refused whole)
  (b) location resolution never uses a stale snapshot: a census row (creature AND plant) whose texPath is out of date is
      re-resolved from the src XML, and a sheet showing the old texPath is flagged
  (c) the Pyrelands sheet of 2026-10-14 (built before its art was installed) is reported stale now
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artledger as L  # noqa: E402
import sheet_freshness as FR  # noqa: E402
import subject as S  # noqa: E402

FAILS = []
PYR = L.REPO_ROOT / "Transient" / "pyrelands_art_2026-10-14" / "pyrelands_art_sheet_2026-10-14.html"


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def png(rgb) -> bytes:
    from PIL import Image
    b = BytesIO()
    Image.new("RGBA", (8, 8), rgb + (255,)).save(b, "PNG")
    return b.getvalue()


THING = """<Defs><ThingDef><defName>RM_Foo</defName><graphicData><texPath>Things/Plant/RM_Foo</texPath></graphicData>
<plant/></ThingDef></Defs>"""
RACE = """<Defs><ThingDef><defName>RM_Beast</defName><race><body>Bird</body></race></ThingDef>
<PawnKindDef><defName>RM_Beast</defName><race>RM_Beast</race><lifeStages><li><bodyGraphicData>
<texPath>Things/Pawn/Animal/RM_Beast/RM_Beast</texPath></bodyGraphicData></li></lifeStages></PawnKindDef></Defs>"""


def fixture(d: Path):
    mod = d / "src" / "RimMandrake" / "ModX"
    (mod / "Defs").mkdir(parents=True)
    (mod / "Defs" / "foo.xml").write_text(THING)
    (mod / "Defs" / "beast.xml").write_text(RACE)
    t = mod / "Textures" / "Things" / "Plant"
    t.mkdir(parents=True)
    (t / "RM_Foo.png").write_bytes(png((10, 120, 30)))
    (t / "RM_Foo_m.png").write_bytes(png((255, 255, 255)))     # a mask-named sibling of another stem: not the picture
    b = mod / "Textures" / "Things" / "Pawn" / "Animal" / "RM_Beast"
    b.mkdir(parents=True)
    for f in ("south", "east", "north"):
        (b / f"RM_Beast_{f}.png").write_bytes(png((90, 60, 20)))
        (b / f"RM_Beast_{f}m.png").write_bytes(png((0, 0, 0)))  # masks never count
    w = S.World(src_root=d / "src", canon_root=d / "canon", artpipe_root=d / "artpipe", facts_root=d / "facts",
                read_jobs=False)
    ctx = FR.Ctx(world=w, idx=L.Index(events=[]), roots=FR.texture_roots(d))
    return ctx, t / "RM_Foo.png", b


def sheet(d: Path, ctx, live_sha: str, render_sha: str, beast_faces: dict, beast_res="Things/Pawn/Animal/RM_Beast/RM_Beast",
          beast_kind="live"):
    img = d / "sheetdir" / "img"
    img.mkdir(parents=True, exist_ok=True)
    (img / "a.webp").write_bytes(b"thumbA")
    items = [
        {"id": "RM_Foo", "desc": {"def": "RM_Foo"}, "thumbs": {live_sha: "img/a.webp"},
         "graphics": [{"res": "Things/Plant/RM_Foo", "cols": [
             {"kind": "live", "label": "IN GAME — ModX", "faces": {"single": live_sha}, "letter": "A", "winner": True},
             {"kind": "artpipe", "label": "render rm_foo", "faces": {"single": render_sha}, "letter": "B"}]}]},
        {"id": "RM_Beast", "desc": "not a dict on older sheets", "thumbs": {},
         "graphics": [{"res": beast_res, "cols": [
             {"kind": beast_kind, "label": "IN GAME — ModX" if beast_kind == "live" else "donor original — swanimals",
              "faces": beast_faces, "letter": "A", "winner": beast_kind == "live"}]}]},
    ]
    html = ('<!doctype html><html><head><title>t</title></head><body><script id="ITEMS" type="application/json">'
            + json.dumps(items) + "</script></body></html>")
    man = FR.build_manifest(items, d / "sheetdir", [{"key": "RM_Foo", "defNames": ["RM_Foo"]},
                                                     {"key": "RM_Beast", "defNames": ["RM_Beast"]}])
    html = FR.embed(html, man)
    p = d / "sheetdir" / "fix_sheet_2026-10-14.html"
    p.write_text(html)
    return p, html


def main() -> int:
    import scaled_review_gate as SG
    import serve_gated as SVG
    import art_sheet as A
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        ctx, foo, beast_dir = fixture(d)
        foo_sha = L.sha256_file(foo)
        beast = {f: L.sha256_file(beast_dir / f"RM_Beast_{f}.png") for f in ("south", "east", "north")}
        render_sha = L.sha256_bytes(png((200, 10, 10)))

        # ── installed() measures disk: masks out, facings in
        inst = FR.installed("Things/Pawn/Animal/RM_Beast/RM_Beast", ctx.roots)
        check(sorted(r.rsplit("_", 1)[1] for _, r in inst) == ["east.png", "north.png", "south.png"],
              "installed(): three facings of the creature, its masks excluded")
        check(set(FR.installed("Things/Plant/RM_Foo", ctx.roots).values()) == {foo_sha},
              "installed(): the plant's one file; a `_m` sibling is a different texPath, not this picture")

        # ── (a) built fresh, then the art changes on disk
        p, html = sheet(d, ctx, foo_sha, render_sha, beast)
        r = FR.verify_html(p, ctx)
        check(r["fresh"] and r["manifest"], f"a sheet matching disk is FRESH ({FR.report('fix', r)[:160]})")
        foo.write_bytes(png((10, 10, 200)))                       # the art is replaced (an install, a hand copy, anything)
        FR._SHA.clear()
        r = FR.verify_html(p, ctx)
        whys = " | ".join(r["stale"].get("RM_Foo", []))
        check(not r["fresh"] and list(r["stale"]) == ["RM_Foo"], "art changed on disk -> exactly the changed row is STALE")
        check("installed now but not shown as installed" in whys and "no file of ours holds those bytes" in whys,
              "both halves are named: the new bytes are not on the sheet, the shown bytes are gone")
        foo.write_bytes(png((200, 10, 10)))                       # the RENDER is installed: same bytes as column B
        FR._SHA.clear()
        r = FR.verify_html(p, ctx)
        check(any("render rm_foo" in w for w in r["stale"].get("RM_Foo", [])),
              "a render installed since the build is flagged: the sheet still calls it a render, not what the game shows")
        gate = SG.check_fresh({"html": html, "html_path": p, "fresh_ctx": ctx}, [])
        check(not gate.ok and gate.req == "15", "gate req 15 fails the stale sheet (a stale-at-birth sheet is never written)")
        (d / "sheetdir" / "img" / "a.webp").write_bytes(b"other")
        r = FR.verify_html(p, ctx)
        check(any("thumbnail img/a.webp changed" in w for w in r["stale"].get("RM_Foo", [])),
              "a thumbnail rewritten after the build is flagged (FRESHNESS block sha256)")

        # serve path (owner, by card 2026-10-19, relaxing 2026-10-14): a stale ROW is labelled on the served page and its
        # picks are off; the sheet still starts and serves. Only a page with no readable ITEMS is refused.
        stamped = d / "sheetdir" / "stamped_sheet_2026-10-14.html"
        stamped.write_text(SG.stamp(html))
        dec = d / "sheetdir" / "stamped_sheet_2026-10-14.decisions.json"
        dec.write_text("{}")
        real_ctx = FR.Ctx
        FR.Ctx = lambda: ctx
        try:
            rc = SVG.startup_freshness(stamped, ctx)
            check(rc == 0, f"serve_gated STARTS a sheet with a stale row (rc {rc}); the row is labelled, not the sheet refused")
            body0 = stamped.read_bytes()
            out = SVG.fresh_gate(stamped)(body0)
            m = re.search(rb'<script id="STALE_ROWS" type="application/json">(.*?)</script>', out, re.S)
            pay = json.loads(m.group(1).replace(b"<\\/", b"</")) if m else {}
            check(b"STALE sheet refused" not in out and out.startswith(body0[:out.find(b"<script id=\"STALE_ROWS\"")])
                  and list((pay.get("rows") or {})) == ["RM_Foo"] and pay.get("n") == 1,
                  "a page load serves the sheet itself with exactly the stale row named in STALE_ROWS")
            check(b"'STALE: '" in out and b"stopImmediatePropagation" in out and b"data-act=purge" in out,
                  "the served page badges 'STALE: <reason>' and switches the row's picks off (delete stays: content-addressed)")
            noitems = d / "sheetdir" / "noitems_sheet_2026-10-14.html"
            noitems.write_text(SG.stamp("<html><body>no items</body></html>"))
            check(SVG.startup_freshness(noitems, ctx) == 5 and b"refused" in SVG.fresh_gate(noitems)(noitems.read_bytes()),
                  "a page with no readable ITEMS block is still refused (freshness unmeasurable, nothing to label)")
            boom = SVG.fresh_gate(stamped)
            real_v = FR.verify_html
            FR.verify_html = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("disk gone"))
            try:
                o2 = boom(body0 + b" ")
            finally:
                FR.verify_html = real_v
            check(b'"all": ["freshness UNMEASURED' in o2, "a measurement that throws labels EVERY row stale (fail closed), never fresh")
            foo.write_bytes(png((10, 120, 30)))                   # put the original back: fresh again
            (d / "sheetdir" / "img" / "a.webp").write_bytes(b"thumbA")
            FR._SHA.clear()
            body = stamped.read_bytes()
            check(SVG.fresh_gate(stamped)(body) == body, "a fresh sheet is served byte-for-byte unchanged")
        finally:
            FR.Ctx = real_ctx

        # ── (b) locations come from src XML now, never a cached census: plant AND creature
        stale_plant = {"key": "RM_Foo", "defNames": ["RM_Foo"],
                       "art": {"resources": [{"res": "Things/OldPlace/RM_Foo", "role": "body", "joined_by": "def"}]}}
        stale_beast = {"key": "RM_Beast", "defNames": ["RM_Beast"],
                       "art": {"resources": [{"res": "swanimals/Beast/Beast", "role": "body", "joined_by": "def"}]}}
        for row, want, what in ((stale_plant, "Things/Plant/RM_Foo", "plant"),
                                (stale_beast, "Things/Pawn/Animal/RM_Beast/RM_Beast", "creature")):
            new, notes = FR.fresh_resources(row, ctx.world)
            check([x["res"] for x in new] == [want] and notes and "STALE" in notes[0],
                  f"{what}: a census texPath out of date is replaced by the src XML's ({[x['res'] for x in new]})")
        donor = {"key": "AA_Thing", "defNames": ["AA_Thing"], "art": {"resources": [{"res": "Donor/AA_Thing"}]}}
        check(FR.fresh_resources(donor, ctx.world) == (donor["art"]["resources"], []),
              "a donor/vanilla row (no src XML) keeps its resolved texPath and says nothing")
        p2, _ = sheet(d, ctx, foo_sha, render_sha, {"south": render_sha}, beast_res="swanimals/Beast/Beast", beast_kind="donor")
        r = FR.verify_html(p2, ctx)
        check(any("draw ['Things/Pawn/Animal/RM_Beast/RM_Beast']" in w for w in r["stale"].get("RM_Beast", [])),
              "a sheet showing a creature's OLD texPath (the tap-clamp case) is flagged: our def draws another one now")
        p3, _ = sheet(d, ctx, foo_sha, render_sha, beast, beast_res="swanimals/Beast/Beast")
        check("RM_Beast" in FR.verify_html(p3, ctx)["stale"],
              "the same pictures labelled IN GAME under the old texPath are flagged too (no file there holds them)")
        gb = Path(A.__file__).read_text()
        check("FR.fresh_resources(r, _fw)" in gb and "FR.embed(" in gb,
              "art_sheet.generate_biome re-resolves every row from src and embeds the FRESHNESS block before the gate")
        kept = A._kept_cols([{"letter": "A"}], {"columns": {"B": {"south": "x"}}, "labels": {"B": "IN GAME — ModX"}}, {"B"})
        check(kept and not kept[0]["label"].startswith("IN GAME"), "a kept set no longer installed never says IN GAME")

    # ── (c) the real Pyrelands sheet AS BUILT (d2a724c08d), before its art was installed — read from git, because the
    # file on disk has since been rebuilt fresh (2026-10-14) and must not be what this proves
    import subprocess
    built = subprocess.run(["git", "-C", str(L.REPO_ROOT), "show", f"d2a724c08d:{PYR.relative_to(L.REPO_ROOT)}"],
                           capture_output=True, text=True)
    if built.returncode or not PYR.parent.is_dir():
        print(f"SKIPPED (c): {PYR.relative_to(L.REPO_ROOT)} at d2a724c08d is unreadable (Transient shelf life)")
    else:
        r = FR.verify_html(PYR, html=built.stdout)
        st = r["stale"]
        # The sheet is frozen but the art it is checked against is LIVE: later installs (2026-10-16 facings batch, ...) legitimately
        # made 2 of the 9 rows match again (7 of 9 stale on 2026-10-20). The proof is that the verifier still flags stale rows.
        check(not r["fresh"] and 0 < len(st) <= r["rows"] == 9, f"Pyrelands 2026-10-14 sheet as built: {len(st)} of {r['rows']} rows STALE")
        check(any("RM_BarbslingerSpike.png" in w and "render pyr_barbslinger_spike" in w for w in st.get("PYR_BarbslingerSpike", [])),
              "its spike row says the installed RM_BarbslingerSpike.png is shown only as a render")
    print(f"{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failing")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
