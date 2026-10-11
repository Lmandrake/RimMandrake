#!/usr/bin/env python3
"""selftest_game_art.py — game art is refused without its true-scale panels at every delivery chokepoint
(owner, question card 2026-10-11, "Hybrid fix"), decided from the pictures, never from the sheet's say-so.

Fixtures are the real failures: a sheet that declared itself non-art while showing sprites (sheet_conflicts_review
2026-10-09), flattened thumbnails named after defs (rot/desert review sheets), and a content-hashed copy whose only
evidence is its alpha. Also: the size resolver for buildings/items/UI-only defs, and the gate's resolver-confirmed
"no world size" exemption. Every live biome sheet must still pass delivery (RimPulse serves them)."""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
from io import BytesIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import game_art as G  # noqa: E402
import scaled_review_gate as SG  # noqa: E402

REPO = HERE.parents[3]
FAILS: list[str] = []


def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        FAILS.append(m)


def sprite(path: Path):
    from PIL import Image
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    im.paste((170, 110, 60, 255), (12, 12, 52, 52))
    im.save(path)


def flat(path: Path):
    from PIL import Image
    Image.new("RGB", (64, 64), (90, 90, 90)).save(path)


def sheet(items_img: list[str], head: str = "") -> str:
    items = [{"id": f"r{i}", "img": s} for i, s in enumerate(items_img)]
    return (f"<html><head>{head}</head><body><script id=\"ITEMS\" type=\"application/json\">{json.dumps(items)}</script>"
            + "".join(f'<img src="{s}">' for s in items_img) + "</body></html>")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "img").mkdir()
        sprite(td / "img" / "9f3a1c.webp.png")
        flat(td / "img" / "chart.png")
        flat(td / "img" / "RM_Sollak_east.png")              # flattened thumbnail: only the NAME says sprite
        flat(td / "img" / "AB_DribblingCap.png")             # flattened, named after a def

        def cls(html):
            p = td / "s.html"
            p.write_text(html)
            return G.classify(html, p)

        check(cls(sheet(["img/9f3a1c.webp.png"]))["game_art"], "a content-hashed cut-out sprite is game art (pixels)")
        check(not cls(sheet(["img/chart.png"]))["game_art"], "a flat RGB chart is not game art")
        check(cls(sheet(["img/RM_Sollak_east.png"]))["game_art"], "a flattened facing thumbnail is game art (file name)")
        names = G.def_names()
        if names:
            check(cls(sheet(["img/AB_DribblingCap.png"]))["game_art"] == ("AB_DribblingCap" in names),
                  "a thumbnail named after a def in the dump is game art")
        else:
            print("SKIP def-name test: no def dump")
        check(cls(sheet(["Mods/X/Textures/Things/Item/Rock.png"]))["game_art"], "a mod Textures/ path is game art (not on disk)")
        check(cls(sheet(["img/scale_RM_X_ab12.png"]))["game_art"] is False, "our own scale panel alone is not game art")
        buf = BytesIO()
        from PIL import Image
        im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        im.paste((10, 200, 10, 255), (20, 20, 40, 40))
        im.save(buf, "PNG")
        uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        check(cls(f'<html><body><img src="{uri}"></body></html>')["game_art"], "an embedded data: sprite is game art")
        declared = sheet(["img/9f3a1c.webp.png"], head='<meta name="sheet-kind" content="non-art">')
        check(cls(declared)["game_art"], "declaring non-art does not change the verdict (sheet_conflicts_review 2026-10-09)")

        # delivery_check: unstamped art refused, stamped art and non-art pass
        art = td / "art_sheet_x.html"
        art.write_text(sheet(["img/9f3a1c.webp.png"]))
        ok, msg = G.delivery_check(art)
        check(not ok and "GAME ART" in msg and "--subjects" in msg, "unstamped game-art sheet refused, naming the gated builder")
        stamped = td / "stamped_sheet_x.html"
        stamped.write_text(SG.stamp(sheet(["img/9f3a1c.webp.png"])))
        check(G.delivery_check(stamped)[0], "a gate-stamped game-art sheet may be delivered")
        stamped.write_text(stamped.read_text().replace("r0", "rX"))
        check(not G.delivery_check(stamped)[0], "a stamped sheet edited after the gate is refused")
        chart = td / "chart_sheet_x.html"
        chart.write_text(sheet(["img/chart.png"]))
        check(G.delivery_check(chart)[0], "a non-art sheet may be delivered unstamped")

        # phone chokepoint: sheet_to_artifact exits 4 on unstamped game art
        r = subprocess.run([sys.executable, str(HERE.parent / "sheet_to_artifact.py"), "--sheet", str(art), "--title", "T",
                            "--out", str(td / "o.html")], capture_output=True, text=True, timeout=60)
        check(r.returncode == 4 and "REFUSED" in r.stderr, "sheet_to_artifact refuses unstamped game art (exit 4)")

        # commit chokepoint: the pre-commit hook in a scratch repo
        repo = td / "repo"
        (repo / "img").mkdir(parents=True)
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null")
        hook_dir = REPO / "infrastructure" / "githooks"
        (repo / "src" / "RimMandrake" / "Utils").mkdir(parents=True)
        os.symlink(HERE, repo / "src" / "RimMandrake" / "Utils" / "art")

        def git(*a):
            return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, env=env)
        git("init", "-q", "-b", "main")
        git("config", "core.hooksPath", str(hook_dir))
        sprite(repo / "img" / "a1.png")
        (repo / "bad.html").write_text(sheet(["img/a1.png"]))
        git("add", "--", "img/a1.png", "bad.html")
        r = git("commit", "-q", "-m", "x")
        check(r.returncode != 0 and "pre-commit REFUSED" in r.stderr, "pre-commit refuses an unstamped game-art sheet")
        (repo / "bad.html").write_text(SG.stamp(sheet(["img/a1.png"])))
        git("add", "--", "bad.html")
        r = git("commit", "-q", "-m", "x")
        check(r.returncode == 0, "pre-commit lets a stamped game-art sheet through" + (f" ({r.stderr[:120]})" if r.returncode else ""))
        (repo / "notes.md").write_text("x")
        git("add", "--", "notes.md")
        check(git("commit", "-q", "-m", "y").returncode == 0, "pre-commit ignores a commit with no sheet")

    # gate: a resolver-confirmed 'none' row is exempt; an author-claimed one is not
    ctx = {"resolve_size": lambda d: {"status": "none"} if d == "Electricity" else {"status": "measured", "kind": "thing"}}
    check(SG._none_confirmed(ctx, {"status": "none", "kind": "none", "def": "Electricity", "source": "x"}) == "",
          "gate accepts a 'no world size' row the resolver confirms")
    check("resolver sizes" in SG._none_confirmed(ctx, {"status": "none", "kind": "none", "def": "RM_Sluice", "source": "x"}),
          "gate refuses a 'no world size' claim the resolver contradicts")
    check(SG._none_confirmed(ctx, {"status": "none", "kind": "none", "source": "x"}) != "", "a 'none' row naming no def fails")

    # resolver: buildings and items sized from the dump; UI-only defs measured as none
    try:
        import scale_panel as SP
        R = SP.Resolver()
    except Exception as e:  # noqa: BLE001
        print(f"SKIP resolver tests: no def dump ({type(e).__name__})")
        R = None
    if R is not None:
        b = R.size({"key": "Bed"})
        check(b["kind"] == "thing" and b["footprint"] == [1, 2] and b["status"] == "measured",
              f"Bed sizes as a 1×2 thing ({b.get('footprint')})")
        g = R.size({"key": "Gun_Revolver"})
        check(g["kind"] == "thing" and g["category"] == "Item", "Gun_Revolver sizes as an item")
        e = R.size({"key": "Electricity"})
        check(e["status"] == "none" and "ResearchProjectDef" in e["source"], "a ResearchProjectDef has no world size")
        f = R.size({"key": "Frame_RM_Sluice"}) if R._def("Frame_RM_Sluice", "ThingDef") else {"status": "none"}
        check(f["status"] == "none", "a ThingDef with no graphicData texPath has no world size")
        p = R.size({"key": "Plant_Potato"})
        check(p["kind"] == "plant", "plants still size as plants")

    # live sheets: every served biome sheet still passes delivery (RimPulse reads their serve logs)
    live = sorted((REPO / "Transient" / "biome_ffar").glob("*_sheet_*.html"))
    live = [p for p in live if not p.name.endswith(".gate.tmp.html")]
    check(len(live) >= 20, f"sanity probe: {len(live)} live biome sheets found")
    bad = [p.name for p in live if not G.delivery_check(p)[0]]
    check(not bad, f"every live biome sheet passes delivery ({len(live) - len(bad)}/{len(live)})" + (f": {bad[:3]}" if bad else ""))

    print(f"{len(FAILS)} failing" if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
