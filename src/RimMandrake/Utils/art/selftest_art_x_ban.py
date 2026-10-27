#!/usr/bin/env python3
"""selftest_art_x_ban.py — his ✕ deletes a picture for ever and bans it (owner card 2026-10-26 19:54, "X = delete
forever + ban"; his words: "I constantly mark things with x and even explicitly do for them to never return. Yet they
do time and time again wasting my focus").

Every route a ✕'d picture came back by (measured 2026-10-26: bytes reinstalled, re-shown on a later sheet, redrawn as
a near-duplicate) is closed and checked here:
  * x_delete removes the game file AND the store bytes, records a ban {sha, ph, subject, mark}; the art guard accepts
    the removal on his mark and refuses it on a forged one;
  * an exact banned sha and a near-duplicate are refused by install / install_bytes, hidden by the sheet builders
    (art_sheet._gone, sheet_to_artifact.build_rows), discarded by artpipe (ban_failure, re-rolled twice then left) and
    by art_eval (banned_candidates); every pipeline discard is logged (ban_hit) and in the digest;
  * a distinct variant passes all of them;
  * only his typed words lift a ban (art.py unban --owner-said); a re-✕ on the lifted mark is refused.
Fixture under /home/mandrake/rm/scratch/BENCH (never /tmp).
"""
from __future__ import annotations

import io
import json
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import selftest_enact as T  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def sprite(seed: int, shift: int = 0) -> bytes:
    """A creature-like sprite (body, head, legs on alpha); `shift` brightens it (a near-duplicate redraw)."""
    from PIL import Image, ImageDraw
    r = random.Random(seed)
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = tuple(min(255, r.randrange(40, 200) + shift) for _ in range(3)) + (255,)
    dark = tuple(max(0, c - 60) for c in col[:3]) + (255,)
    bx, by = r.randrange(8, 20), r.randrange(14, 30)
    d.ellipse([bx, by, bx + r.randrange(28, 40), by + r.randrange(14, 24)], fill=col, outline=dark, width=2)
    hx, hy = r.choice((4, 40)), r.randrange(4, 20)
    d.ellipse([hx, hy, hx + 18, hy + 16], fill=dark)
    for k in range(r.randrange(2, 5)):
        x = bx + 6 + 8 * k
        d.rectangle([x, by + 16, x + 3, min(63, by + 16 + r.randrange(10, 20))], fill=dark)
    b = io.BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


def near_dup(png: bytes) -> bytes:
    """The same sprite as a redraw drifts: resampled down to 60 px and back (different bytes, same look)."""
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert("RGBA")
    b = io.BytesIO()
    im.resize((60, 60), Image.LANCZOS).resize(im.size, Image.LANCZOS).save(b, "PNG")
    return b.getvalue()


WHY = "script:src/RimMandrake/Utils/art/selftest_art_x_ban.py"


def main():
    F = T.build(T.SCRATCH / f"art_x_ban_{os.getpid()}")
    import artledger as L
    import art_guard as G
    import art_sheet as S
    import sheet_to_artifact as SA
    L.MARK_ROOT = F["root"]
    try:
        banned_b, near_b, other_b = sprite(23), near_dup(sprite(23)), sprite(97)
        d_near = (int(L.dhash(banned_b)[0], 16) ^ int(L.dhash(near_b)[0], 16)).bit_count()
        d_far = (int(L.dhash(banned_b)[0], 16) ^ int(L.dhash(other_b)[0], 16)).bit_count()
        check(0 < d_near <= L.BAN_NEAR < d_far, f"fixture: near-duplicate d={d_near}, distinct d={d_far} "
                                               f"(threshold {L.BAN_NEAR})")
        tex = F["src"] / "RimMandrake/TestMod/Textures/Things/Pawn/Animal/RM_Ban/RM_Ban_east.png"
        tex.parent.mkdir(parents=True, exist_ok=True)
        r0 = L.install_bytes(tex, banned_b, reason=WHY)
        sha = r0.get("new") or L.sha256_bytes(banned_b)
        check(tex.is_file() and L.store_has(sha), "fixture: the picture is live in Textures and in the store")

        at = "2026-10-26T19:54:00.000Z"
        via = str(F["decisions"].relative_to(F["root"]))
        doc = json.loads(F["decisions"].read_text())
        doc["decisions"] = {"RM_Ban": {"decision": "redo", "at": at, "decidedAt": at, "purge": [sha]}}
        F["decisions"].write_text(json.dumps(doc))
        mark = {"sheet": "test_sheet", "row": "RM_Ban", "at": at, "via": via, "kind": "x"}

        # ── an agent's guess is not his ✕
        forged = {**mark, "at": "2026-10-26T20:00:00.000Z"}
        try:
            L.x_delete(sha, forged, subject="RM_Ban")
            check(False, "x_delete refuses a mark with no owner click behind it")
        except L.Refused:
            check(L.store_has(sha) and tex.is_file(), "x_delete refuses a mark with no owner click behind it")

        # ── X purges and leaves no file
        res = L.x_delete(sha, mark, subject="RM_Ban")
        idx = L.Index()
        check(res["status"] == "deleted" and not tex.exists() and not L.store_has(sha),
              "✕ deletes the game file and the store bytes (no file left)")
        b = idx.bans.get(sha) or {}
        check(b.get("ph") == L.dhash(banned_b)[0] and b.get("subject") == "RM_Ban" and (b.get("mark") or {}).get("at") == at
              and idx.is_purged(sha), "ban records sha, perceptual hash, subject and his mark; the bytes are purged")
        rel_path = str(tex.relative_to(F["src"].parent))
        check(not G.check([(rel_path, sha, None)], idx.events),
              "art guard accepts the ✕ removal on his mark")
        evs = [dict(e) for e in idx.events]
        for e in evs:
            if e.get("type") == "live" and e.get("reason") == "x-delete":
                e["mark"] = {**e["mark"], "at": "2026-10-26T21:00:00.000Z"}
        check(bool(G.check([(rel_path, sha, None)], evs)), "art guard refuses an x-delete whose mark he never clicked")

        # ── install / install_bytes
        dest2 = tex.parent / "RM_Ban_south.png"
        for label, data in (("exact banned bytes", banned_b), ("a near-duplicate", near_b)):
            try:
                L.install_bytes(dest2, data, reason=WHY)
                check(False, f"install_bytes refuses {label}")
            except L.Refused as e:
                check("banned" in str(e) and not dest2.exists(), f"install_bytes refuses {label}")
        try:
            L.install(T.MOD, "Things/Pawn/Animal/RM_Ban/RM_Ban_west.png", sha, reason=WHY)
            check(False, "install refuses the banned sha")
        except L.Refused:
            check(True, "install refuses the banned sha")
        r_ok = L.install_bytes(dest2, other_b, reason=WHY)
        check(dest2.is_file() and r_ok.get("status") != "refused", "install_bytes allows a distinct variant")

        # ── sheets
        near_sha, other_sha = L.store_put_bytes(near_b), L.sha256_bytes(other_b)
        idx = L.cached_index()
        check(S._gone(idx, sha) and S._gone(idx, near_sha) and not S._gone(idx, other_sha),
              "art_sheet hides the banned sha and its near-duplicate, shows the distinct variant")
        pics = F["root"] / "pics"
        pics.mkdir(exist_ok=True)
        for s_, data in ((sha, banned_b), (near_sha, near_b), (other_sha, other_b)):
            (pics / f"{s_[:12]}.png").write_bytes(data)
        thumbs = {s_: f"{s_[:12]}.png" for s_ in (sha, near_sha, other_sha)}
        items = [{"id": "RM_Ban", "thumbs": thumbs, "fulls": {}, "graphics": [{"key": "g", "cols": [
            {"letter": "A", "winner": True, "faces": {"east": sha}},
            {"letter": "B", "faces": {"east": near_sha, "south": other_sha}},
            {"letter": "C", "faces": {"east": sha}}]}]}]
        rows = SA.build_rows(items, {}, {}, SA.Images(pics, F["root"] / "artifact"), banned=SA.ban_checker())
        cols = {c["L"]: c for c in rows[0]["lanes"][0]["cols"]}
        check(set(cols) == {"A", "B"} and [f["face"] for f in cols["B"]["faces"]] == ["south"]
              and cols["A"]["purgedLive"] and len(rows[0]["withheld"]) == 2,
              "sheet_to_artifact withholds banned + near-duplicate faces (counted), drops the emptied column, keeps the "
              "distinct face; the in-game column shows it as purged, never pickable")

        # ── pipeline: artpipe + art_eval
        sys.path.insert(0, str(HERE.parent / "artpipe"))
        sys.path.insert(0, str(HERE.parent / "art_eval"))
        import artpiped as AP
        import runner as RU
        out = F["root"] / "renders"
        out.mkdir(exist_ok=True)
        for name, data in (("exact", banned_b), ("near", near_b), ("other", other_b)):
            (out / f"{name}.png").write_bytes(data)
        check(bool(AP.ban_failure(out / "exact.png", "j_exact")) and bool(AP.ban_failure(out / "near.png", "j_near"))
              and not AP.ban_failure(out / "other.png", "j_other"),
              "artpipe discards an exact or near-duplicate banned render, passes a distinct one")
        q = F["root"] / "artpipe"
        (q / "failed" / "j_exact.json").write_text(json.dumps({"id": "j_exact", "prompt": "p"}))
        n1 = AP.ban_reroll(q / "failed" / "j_exact.json", "j_exact", q / "pending")
        shutil.copy(q / "pending" / f"{n1}.json", q / "failed" / f"{n1}.json")
        n2 = AP.ban_reroll(q / "failed" / f"{n1}.json", n1, q / "pending")
        shutil.copy(q / "pending" / f"{n2}.json", q / "failed" / f"{n2}.json")
        n3 = AP.ban_reroll(q / "failed" / f"{n2}.json", n2, q / "pending")
        check((n1, n2, n3) == ("j_exact_ban1", "j_exact_ban2", "") and
              json.loads((q / "pending" / "j_exact_ban2.json").read_text()).get("prompt") == "p",
              f"artpipe re-rolls a banned render {AP.BAN_REROLLS} times, then leaves it in failed/ ({n1}, {n2}, {n3!r})")
        spec_b = {"subject": "RM_Ban", "images": {"east": str(out / "near.png")}}
        spec_o = {"subject": "RM_Ban", "images": {"east": str(out / "other.png")}}
        check(len(RU.banned_candidates(spec_b)) == 1 and not RU.banned_candidates(spec_o),
              "art_eval routes a near-duplicate candidate to regen, judges a distinct one")
        hits = [e for e in L.Index().events if e.get("type") == "ban_hit"]
        check({e.get("where") for e in hits} >= {"artpipe", "art_eval"}, "each pipeline discard is logged (ban_hit)")
        dig = "\n".join(L.marks_digest())
        check("deleted forever + banned" in dig and "discarded" in dig and "✕ removed" in dig,
              "the daily digest shows the ✕ delete, the ban and the pipeline discards")

        # ── unban needs his words
        art = HERE / "art.py"
        p = subprocess.run([sys.executable, str(art), "unban", sha[:12]], capture_output=True, text=True, timeout=120)
        check(p.returncode != 0 and sha in L.Index().bans, "art.py unban without --owner-said is refused")
        try:
            L.unban(sha[:12], owner_said="  ")
            check(False, "unban with blank words is refused")
        except L.Refused:
            check(True, "unban with blank words is refused")
        p = subprocess.run([sys.executable, str(art), "unban", sha[:12], "--owner-said", "bring the beetle back"],
                           capture_output=True, text=True, timeout=120)
        idx = L.Index()
        check(p.returncode == 0 and sha not in idx.bans and not idx.is_purged(sha),
              "art.py unban --owner-said lifts the ban and the ✕'s purge")
        dest3 = tex.parent / "RM_Ban_north.png"
        L.store_put_bytes(banned_b)
        r3 = L.install(T.MOD, str(dest3.relative_to(F["src"] / "RimMandrake/TestMod/Textures")), sha,
                       owner_said="bring the beetle back")
        check(dest3.is_file() and r3.get("status") != "refused", "after unban the picture installs again (on his words)")
        try:
            L.x_delete(sha, mark, subject="RM_Ban")
            check(False, "the lifted ✕ cannot be replayed")
        except L.Refused:
            check(sha not in L.Index().bans, "the lifted ✕ cannot be replayed")
        check("ban lifted on his words" in "\n".join(L.marks_digest()), "the digest shows the unban")
    finally:
        shutil.rmtree(F["root"], ignore_errors=True)
    print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAILED'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
