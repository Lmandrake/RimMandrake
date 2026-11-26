#!/usr/bin/env python3
"""selftest_art_provenance.py — ART_INSTALL_WIRE_BY_CARD_FLAG_MISSING, on a disposable fixture (never real Textures).

Proves `art.py install` takes the owner-authority fields one per kind, as rimflow does (CLAUDE.md "Owner authority on
the ledger"): --by-card and --per-ruling record owner keeps that protect like --owner-said without putting our text in
`said`; --why grants nothing (alone it installs under the mechanical guards, never over a kept picture) and is recorded
on the live event; and `correct-provenance` appends a provenance_fix that re-attributes a card pick filed under `said`
without touching the original event — on an owner purge too (PURGE_CARDS_FIX_WRONG_POCKET), which `card-said` audits.
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

    # owner 2026-11-19 (only five acts stay his): a Conductor ruling never displaces a kept picture
    for rul in ("RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS", "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM"):
        try:
            L.install(mod, rel, sb, per_ruling=rul, why="the Conductor prefers this one")
            check(False, "--per-ruling %s may not displace an owner-kept picture" % rul[:24])
        except L.Refused as e:
            check("stays his" in str(e), "--per-ruling %s may not displace an owner-kept picture" % rul[:24])

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

    # PURGE_CARDS_FIX_WRONG_POCKET: an owner purge whose card pick sits in said is corrected the same way, and the
    # card-said audit sees it before and not after
    pz = noisy(9)
    spz = L.store_put_bytes(pz)
    pcard = "Crossed-out pictures → Delete now"
    L.purge(spz, owner_said=pcard)
    idx = L.Index()
    pev = idx.purged[spz]
    check(pev.get("said") == pcard, "fixture: a purge filed with card text under said")
    check(art.main(["card-said"]) == 1 and any(e["id"] == pev["id"] for e in L.card_said_events(idx)),
          "card-said flags the purge (exit 1)")
    before = L.shard_path().read_bytes()
    rc = art.main(["correct-provenance", pev["id"], "--by-card", pcard, "--why", "purge card pick was filed under said"])
    idx = L.Index()
    check(rc == 0 and L.shard_path().read_bytes().startswith(before), "correct-provenance accepts a purge; appended only")
    check(idx.purged[spz].get("said") == pcard, "the original purge event is unchanged")
    check(idx.authority(idx.purged[spz]) == {"by_card": pcard}, "Index.authority reads the purge's corrected fields")
    check(idx.is_purged(spz), "the correction changes the field, not the purge")
    check(not any(e["id"] == pev["id"] for e in L.card_said_events(idx)), "card-said no longer flags the fixed purge")
    check(not L.card_text_in_said("delete it") and L.card_text_in_said("by-card 2026-10-19: Remove all"),
          "card text detection: his words pass, a by-card prefix is caught")
    # the phrasings agents actually filed card picks in (blind check, gen 1: 102 purges missed by a prefix-only test)
    for card in ("reject+purge on sheet leaningscrub_sheet_2026-10-05 (decision taken by question card 2026-10-08)",
                 "decision taken by question card 2026-10-08 19:05: delete all 17 LeaningScrub conflict pictures",
                 "rescale ALL flagged creatures to the ground-camera standard (question card 2026-10-16)",
                 "Shut gate drafts A-D -> Install all four",
                 "Yes, install my picks (card 2026-10-21: install the 12 held bridge-redraw picks?)"):
        check(L.card_text_in_said(card), f"card text detection catches {card[:50]!r}")
    for words in ("Accept Option A, B, C as all live variants. Drop the donor.", "x->y is the pipe", "a card table"):
        check(not L.card_text_in_said(words), f"card text detection passes his words {words!r}")

    # CARD_PARAPHRASE_AUDIT_SAID_IN_DISGUISE: a said holding ONLY the option label of a recorded card pick has no
    # marker; card-said finds it by matching the labels the ledgers record with their question (art by_card, rimflow
    # byCard). A short generic label, or one he is also recorded as typing (ownerSaid), is never matched.
    rf = tmp / "rimflow"
    rf.mkdir()
    (rf / "OWNER.jsonl").write_text("\n".join(json.dumps(e) for e in (
        {"event": "file", "byCard": "Mountains → Peaks lit toward the sun"},
        {"event": "note", "byCard": "Delete this? → Delete it"},
        {"event": "note", "byCard": "Weir style? → but in the four art styles", "ownerSaid": "but in the four art styles"},
    )) + "\n", encoding="utf-8")
    os.environ["ART_CARD_LEDGERS"] = os.pathsep.join([str(L.ledger_dir()), str(rf)])
    labels = L.card_option_labels()
    check("peaks lit toward the sun" in labels, "a rimflow byCard option label is collected")
    check("delete it" not in labels, "a short generic option label is not collected")
    check("but in the four art styles" not in labels, "a label he is also recorded typing is not collected")
    check("delete now" not in labels, "an art by_card option under the length floor is not collected")
    lz = noisy(11)
    slz = L.store_put_bytes(lz)
    L.purge(slz, owner_said="Peaks lit toward the sun")
    lev = L.Index().purged[slz]
    check(any(e["id"] == lev["id"] for e in L.card_said_events()), "card-said flags a bare card option label in said")
    check(art.main(["correct-provenance", lev["id"], "--by-card", "Mountains → Peaks lit toward the sun",
                    "--why", "bare option label"]) == 0 and art.main(["card-said"]) == 0,
          "after the fix card-said reads 0 again")
    wz = noisy(12)
    swz = L.store_put_bytes(wz)
    L.purge(swz, owner_said="but in the four art styles")
    check(art.main(["card-said"]) == 0, "his recorded words matching a card label are not flagged")
    check(art.main(["card_said"]) == 0, "the underscore alias card_said runs the same audit")

    # SHEETSAID_DECIDE_769_TAGS_HE_NEVER_TYPED: a sheet-pick tag of ours under said is caught; --fix cites the
    # sheet's decisions file in per_ruling; his typed words and card text are not this audit's
    for tag in ("reject+purge on sheet greentide_sheet_2026-10-05",
                "✕ on the facings needs-eyes sheet 2026-10-17 (his newest ruling, supersedes the older keep)",
                "Ismerrow pick A; pool add A B C D H G F; E not_needed (sheet decisions)",
                "Gorg sheet row 2026-10-17: variants B-I ticked as random variants",
                "picks_plants_and_gaps_sheet_2026-10-19 row AB_TinkleGrass: drop"):
        check(L.sheet_tag_in_said(tag), f"sheet tag detection catches {tag[:50]!r}")
    for words in ("GREAT job on the container artsheet. 100% approved", "That sheet is causing me a headache.",
                  "reject+purge on sheet x_sheet_2026-10-05 (decision taken by question card 2026-10-08)"):
        check(not L.sheet_tag_in_said(words), f"sheet tag detection passes {words[:50]!r}")
    root = tmp / "repo"
    (root / "Transient" / "biome_ffar").mkdir(parents=True)
    (root / "Transient" / "biome_ffar" / "fx_sheet_2026-10-05.decisions.json").write_text("{}")
    check(L.sheet_decisions_ref({"via": "../../Transient/biome_ffar/fx_sheet_2026-10-05.decisions.json"}, root)
          == "Transient/biome_ffar/fx_sheet_2026-10-05.decisions.json", "decisions ref read from via")
    check(L.sheet_decisions_ref({"via": "art purge", "said": "reject+purge on sheet fx_sheet_2026-10-05"}, root)
          == "Transient/biome_ffar/fx_sheet_2026-10-05.decisions.json", "decisions ref found from the stem in said")
    check(L.sheet_decisions_ref({"via": "art purge", "said": "Gorg sheet row 2026-10-17: B"}, root) is None,
          "no decisions file named: no guess")
    import ingest as IG
    check(IG.sheet_purge_authority("", "Transient/biome_ffar/fx_sheet_2026-10-05.decisions.json")
          == {"per_ruling": "Transient/biome_ffar/fx_sheet_2026-10-05.decisions.json"},
          "ingest: a sheet ✕ with no row note cites the decisions file, never a tag in said")
    check(IG.sheet_purge_authority("drop the donor", "Transient/x.decisions.json")
          == {"owner_said": "drop the donor", "per_ruling": "Transient/x.decisions.json"},
          "ingest: his row note stays his words, beside the decisions file")
    sz = noisy(13)
    ssz = L.store_put_bytes(sz)
    L.purge(ssz, owner_said="reject+purge on sheet fx_sheet_2026-10-05",
            via="Transient/biome_ffar/fx_sheet_2026-10-05.decisions.json")
    sev = L.Index().purged[ssz]
    check(art.main(["sheet-said"]) == 1 and any(e["id"] == sev["id"] for e in L.sheet_said_events()),
          "sheet-said flags a purge with our tag in said (exit 1)")
    old_root = L.REPO_ROOT
    L.REPO_ROOT = root
    try:
        rc = art.main(["sheet-said", "--fix"])
    finally:
        L.REPO_ROOT = old_root
    sidx = L.Index()
    check(rc == 0 and sidx.authority(sidx.purged[ssz])
          == {"per_ruling": "Transient/biome_ffar/fx_sheet_2026-10-05.decisions.json"},
          "sheet-said --fix moves the tag to per_ruling = the decisions file, and then reads 0")
    check(sidx.is_purged(ssz) and sidx.purged[ssz].get("said", "").startswith("reject+purge"),
          "the fix changes the field, not the purge; the original event is unchanged")

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
