#!/usr/bin/env python3
"""selftest_art_provenance.py — ART_INSTALL_WIRE_BY_CARD_FLAG_MISSING, on a disposable fixture (never real Textures).

Proves `art.py install` takes the owner-authority fields one per kind, as rimflow does (CLAUDE.md "Owner authority on
the ledger"): --by-card and --per-ruling record owner keeps that protect like --owner-said without putting our text in
`said`; --why grants nothing (alone it installs under the mechanical guards, never over a kept picture) and is recorded
on the live event; and `correct-provenance` appends a provenance_fix that re-attributes a card pick filed under `said`
without touching the original event.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from io import BytesIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def png(color):
    from PIL import Image
    b = BytesIO()
    Image.new("RGBA", (8, 8), color).save(b, "PNG")
    return b.getvalue()


def main():
    tmp = Path(tempfile.mkdtemp(prefix="artprov-selftest-"))
    os.environ["ARTSTORE"] = str(tmp / "store")
    os.environ["ART_LEDGER_DIR"] = str(tmp / "ledger")
    os.environ["ART_SRC_ROOT"] = str(tmp / "src")
    os.environ["ART_SEAT"] = "BUILD"
    sys.path.insert(0, str(HERE))
    import artledger as L
    import art

    mod = "src/FixtureMod"
    tex = tmp / mod / "Textures" / "Things" / "Tank"
    tex.mkdir(parents=True)
    # textured 8x8 noise so the geometric-placeholder rule never judges the fixtures
    import random
    def noisy(seed):
        from PIL import Image
        rnd = random.Random(seed)
        im = Image.new("RGBA", (16, 16))
        im.putdata([(rnd.randrange(256), rnd.randrange(256), rnd.randrange(256), 255) for _ in range(256)])
        b = BytesIO(); im.save(b, "PNG"); return b.getvalue()
    a, b, c, d = noisy(1), noisy(2), noisy(3), noisy(4)
    for x in (a, b, c, d):
        L.store_put_bytes(x)
    sa, sb, sc, sd = (L.sha256_bytes(x) for x in (a, b, c, d))
    check(all(L.store_has(s) for s in (sa, sb, sc, sd)), "fixture pictures are in the store")
    rel = "Things/Tank/Tank.png"
    card = "Modern short tank → A white leg tank"

    # --by-card: an owner keep with by_card, nothing in said, and it protects
    r = L.install(mod, rel, sa, by_card=card)
    idx = L.Index()
    rl = next(x for x in idx.rulings if x["id"] == idx.live[(mod, rel)]["ruling_id"])
    check(r["status"] == "installed" and rl.get("by_card") == card and "said" not in rl and rl.get("by") == "owner"
          and rl.get("trust") == "ruled" and rl.get("via") == "art install (by card)",
          "--by-card records an owner keep carrying by_card, never said")
    check(bool(idx.protected(sa)), "a by-card keep protects the picture like his words do")

    # --why alone: grants nothing -> refused over the kept picture
    try:
        L.install(mod, rel, sb, why="delegated: art verdict.json")
        check(False, "--why alone may not displace an owner-kept picture")
    except L.Refused as e:
        check("owner-KEPT" in str(e) and "agent --why" in str(e), "--why alone may not displace an owner-kept picture")

    # --per-ruling: an owner keep citing the ruling; may replace the kept one
    r = L.install(mod, rel, sb, per_ruling="FORD_STONES_REDRAW_LOOK_LIKE_A_SMUDGE", why="applying his ruling")
    idx = L.Index()
    live = idx.live[(mod, rel)]
    rl = next(x for x in idx.rulings if x["id"] == live["ruling_id"])
    check(r["status"] == "installed" and rl.get("per_ruling") == "FORD_STONES_REDRAW_LOOK_LIKE_A_SMUDGE"
          and "said" not in rl and live.get("why") == "applying his ruling",
          "--per-ruling records the cited ruling; --why beside it lands on the live event")

    # --why alone on an unprotected slot: installs under mechanical guards, no ruling
    rel2 = "Things/Tank/Other.png"
    r = L.install(mod, rel2, sc, why="delegated: art verdict.json")
    idx = L.Index()
    live2 = idx.live[(mod, rel2)]
    check(r["status"] == "installed" and "ruling_id" not in live2 and live2.get("why") == "delegated: art verdict.json"
          and live2.get("reason") == "agent-why" and not idx.protected(sc),
          "--why alone installs on a free slot, records why, and protects nothing")
    try:
        L.install(mod, rel2, sd, why="   ")
        check(False, "a blank --why is refused")
    except L.Refused:
        check(True, "a blank --why is refused")
    try:
        L.install(mod, rel2, sd, reason="delegated: art x")
        check(False, "a non-mechanical --reason is still refused (an agent's reason goes in --why)")
    except L.Refused as e:
        check("--why" in str(e), "a non-mechanical --reason is still refused, pointing at --why")

    # a words-only keep keeps its old id (idempotent against keeps recorded before the new fields)
    k = L.owner_keep_ruling(sd, owner_said="blue is better")
    check(k["id"] == L.det_id("ruling-cli", sd, "blue is better") and k.get("said") == "blue is better",
          "a words-only keep keeps its pre-existing id and field")

    # correct-provenance: a card pick filed under said is re-attributed by an appended event
    bad = L.install(mod, "Things/Tank/Old.png", sd, owner_said="(by card 2026-10-22) " + card)
    idx = L.Index()
    rid = idx.live[(mod, L.rel_key("Things/Tank/Old.png"))]["ruling_id"]
    before = L.shard_path().read_bytes()
    rc = art.main(["correct-provenance", rid, "--by-card", card, "--why", "card pick was filed under --owner-said"])
    after = L.shard_path().read_bytes()
    idx = L.Index()
    orig = next(x for x in idx.rulings if x["id"] == rid)
    check(rc == 0 and after.startswith(before) and len(after) > len(before), "the fix is APPENDED; past bytes untouched")
    check(orig.get("said", "").startswith("(by card"), "the original ruling event is unchanged")
    check(idx.authority(orig) == {"by_card": card}, "Index.authority reads the corrected field set")
    check(bool(idx.protected(sd)), "the correction changes the field, not the protection")
    rc2 = art.main(["correct-provenance", rid, "--by-card", card, "--why", "again"])
    check(rc2 == 0 and L.shard_path().read_bytes() == after, "re-running the fix is idempotent")
    check(art.main(["correct-provenance", "nope", "--by-card", card, "--why", "x"]) == 2, "an unknown ruling id is refused")
    check(art.main(["correct-provenance", rid, "--why", "x"]) == 2, "a fix naming no authority field is refused")

    # CLI end to end
    out = subprocess.run([sys.executable, str(HERE / "art.py"), "install", mod, "Things/Tank/Cli.png", sc,
                          "--by-card", "Q → B", "--dry-run"], capture_output=True, text=True, env=os.environ)
    check(out.returncode == 0 and '"planned"' in out.stdout, "art.py install --by-card parses as a CLI")

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{'ALL PASS' if not FAILS else str(len(FAILS)) + ' FAIL'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
