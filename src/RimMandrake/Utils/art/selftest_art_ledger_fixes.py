#!/usr/bin/env python3
"""selftest_art_ledger_fixes.py — the 2026-10-15 art-ledger review fixes, on a disposable fixture.

A  records and files cannot drift apart: a push range is checked event -> PNG as well as PNG -> event (a superseded
   event is fine), `art.py doctor` lists ledger-vs-committed-tree disagreements, and a backfill re-scan reports
   drift instead of relabelling a recorded slot.
B  mod/rel spelling is canonicalised inside install() (alias map at read and write, history never rewritten);
   `art.py put` / `install --file` get bytes into the store with containment and symlink checks.
C  no bypass tags: a `script:` reason must name a writer file in the repo, `retire-duplicate` needs his words (events
   from ENFORCE_REASONS_FROM; older ones keep their rules); a purge never silently releases a keep; kept-but-purged
   pictures are reported, not deleted.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from io import BytesIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILS = []
WRITER = "script:src/RimMandrake/Utils/art/art.py"


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def png(color):
    from PIL import Image
    b = BytesIO()
    Image.new("RGBA", (8, 8), color).save(b, "PNG")
    return b.getvalue()


def refused(fn, *a, **kw):
    import artledger as L
    try:
        fn(*a, **kw)
    except L.Refused as e:
        return str(e)
    return None


def fixture():
    tmp = Path(tempfile.mkdtemp(prefix="art-ledger-fixes-"))
    os.environ["ARTSTORE"] = str(tmp / "store")
    os.environ["ART_LEDGER_DIR"] = str(tmp / "ledger")
    os.environ["ART_SRC_ROOT"] = str(tmp / "src")
    os.environ["ART_SEAT"] = "BUILD"
    (tmp / "ledger" / "events").mkdir(parents=True)
    (tmp / "ledger" / "mod_aliases.json").write_text(json.dumps({"aliases": {"SWBestiary": "src/RimStarWars/SWBestiary"}}))
    (tmp / "src" / "RimStarWars" / "SWBestiary" / "Textures").mkdir(parents=True)
    (tmp / "src" / "RimMandrake" / "FlowWorks" / "Textures").mkdir(parents=True)
    return tmp


def test_b(tmp):
    import artledger as L
    import art
    canon = "src/RimStarWars/SWBestiary"
    # read side: every historical spelling folds to one key
    for spelling in ("SWBestiary", "RimStarWars/SWBestiary", canon, canon + "/", "/home/mandrake/rm/bench/" + canon,
                     str(tmp / canon)):
        check(L.mod_key(spelling) == canon, f"mod_key({spelling!r}) -> {canon}")
    check(L.mod_key("RimMandrake/FlowWorks") == "src/RimMandrake/FlowWorks", "tier-relative spelling gets src/")
    check(L.rel_key("Textures/a/b.png") == "a/b.png" and L.rel_key("a\\b.png") == "a/b.png",
          "rel_key strips a leading Textures/ and backslashes")
    # write side: resolved on disk, contained
    for spelling in ("SWBestiary", "RimStarWars/SWBestiary", canon, str(tmp / canon), str(tmp / canon / "Textures")):
        try:
            got = L.canonical_mod(spelling)
        except L.Refused as e:
            got = f"REFUSED {e}"
        check(got == canon, f"canonical_mod({spelling!r}) -> {canon} (got {got})")
    check(L.canonical_mod("FlowWorks") == "src/RimMandrake/FlowWorks", "a bare name with no alias resolves by folder")
    check(refused(L.canonical_mod, "NoSuchMod") is not None, "an unknown mod is refused (it used to land at <repo>/<mod>/)")
    check(refused(L.canonical_mod, "src/../../etc") is not None, "traversal out of src/ is refused")
    (tmp / "src" / "RimStarWars" / "SWBestiary" / "Defs").mkdir(exist_ok=True)
    (tmp / "src" / "RimMandrake" / "NewMod" / "About").mkdir(parents=True)
    (tmp / "src" / "RimMandrake" / "NewMod" / "About" / "About.xml").write_text("<ModMetaData/>")
    check(refused(L.canonical_mod, "src/RimMandrake/FlowWork") is not None, "a typo'd, nonexistent mod path is refused")
    check(refused(L.canonical_mod, "RimStarWars") is not None, "a bare tier is not a mod")
    check(refused(L.canonical_mod, canon + "/Defs") is not None, "a subfolder of a mod is not a mod")
    check(L.canonical_mod("src/RimMandrake/NewMod") == "src/RimMandrake/NewMod",
          "a mod with About.xml but no Textures/ yet is accepted")
    check(refused(L.canonical_mod, "/home/mandrake/rm/bench/" + canon) is not None
          or not Path("/home/mandrake/rm/bench").exists(),
          "another clone's absolute path is refused at write")
    outside = Path(tempfile.mkdtemp(prefix="art-outside-"))
    (tmp / "src" / "RimMandrake" / "Escape").symlink_to(outside)
    check(refused(L.canonical_mod, "src/RimMandrake/Escape") is not None, "a symlinked mod folder pointing outside is refused")
    check(L.canonical_rel("Textures/Things/X/X_south.png") == "Things/X/X_south.png", "rel accepted with Textures/")
    check(refused(L.canonical_rel, "../x.png") is not None and refused(L.canonical_rel, "/abs.png") is not None,
          "rel with .. or absolute is refused")

    # install with the trap spellings lands at the canonical file and records the canonical key
    red = png((255, 0, 0, 255))
    sred = L.store_put_bytes(red)
    r = L.install("SWBestiary", "Textures/Things/Nuna/Nuna_south.png", sred, reason=WRITER)
    f = tmp / canon / "Textures" / "Things" / "Nuna" / "Nuna_south.png"
    check(r.get("status") == "installed" and f.is_file(), "install('SWBestiary', 'Textures/…') writes the canonical file")
    lv = [e for e in L.read_events() if e.get("type") == "live"]
    check(lv and lv[-1]["mod"] == canon and lv[-1]["rel"] == "Things/Nuna/Nuna_south.png",
          "the live event is keyed canonically")
    check(not (tmp / "SWBestiary").exists() and not (tmp / "src" / "SWBestiary").exists(),
          "nothing written at <repo>/SWBestiary")

    # historical phantom keys fold onto the canonical slot (no false SHADOWED, the guard finds them)
    L.append({"type": "live", "mod": "SWBestiary", "rel": "Things/Nuna/Nuna_south.png", "sha": sred, "prev": None,
              "reason": "backfill-observed", "ts": "2026-10-01T00:00:00-0700"})
    idx = L.Index()
    keys = [k for k in idx.live if k[1] == "Things/Nuna/Nuna_south.png"]
    check(keys == [(canon, "Things/Nuna/Nuna_south.png")], f"a phantom spelling folds into one slot (got {keys})")

    # put: a supported way to get bytes into the store
    good = tmp / "Transient" / "new.png"
    good.parent.mkdir()
    blue = png((0, 0, 255, 255))
    good.write_bytes(blue)
    check(L.put_file_checked(good) == L.sha256_bytes(blue) and L.store_has(L.sha256_bytes(blue)), "put stores a PNG in the clone")
    (outside / "o.png").write_bytes(png((1, 2, 3, 255)))
    check(refused(L.put_file_checked, outside / "o.png") is not None, "put refuses a file outside the clone")
    link = tmp / "Transient" / "link.png"
    link.symlink_to(good)
    check(refused(L.put_file_checked, link) is not None, "put refuses a symlink")
    (tmp / "Transient" / "x.png").write_bytes(b"not a png")
    check(refused(L.put_file_checked, tmp / "Transient" / "x.png") is not None, "put refuses a non-PNG")
    rc = art.main(["put", str(good)])
    check(rc == 0, "art.py put exits 0")
    green = tmp / "Transient" / "green.png"
    green.write_bytes(png((0, 255, 0, 255)))
    rc = art.main(["install", "RimStarWars/SWBestiary", "Things/Nuna/Nuna_east.png", "--file", str(green),
                   "--reason", WRITER])
    check(rc == 0 and (tmp / canon / "Textures" / "Things" / "Nuna" / "Nuna_east.png").read_bytes() == green.read_bytes(),
          "art.py install --file puts and installs in one command")
    rc = art.main(["install", canon, "Things/Nuna/Nuna_west.png", "--reason", WRITER])
    check(rc == 2, "install with neither <sha> nor --file is refused")


def git(cwd, *a):
    import subprocess
    r = subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"git {a}: {r.stderr}")
    return r.stdout.strip()


def git_fixture():
    repo = Path(tempfile.mkdtemp(prefix="art-ledger-drift-"))
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "t")
    git(repo, "config", "core.hooksPath", "/dev/null")
    os.environ["ARTSTORE"] = str(repo.parent / (repo.name + "-store"))
    os.environ["ART_LEDGER_DIR"] = str(repo / "infrastructure" / "state" / "art")
    os.environ["ART_SRC_ROOT"] = str(repo / "src")
    (repo / "infrastructure" / "state" / "art" / "events").mkdir(parents=True)
    (repo / "src" / "RimMandrake" / "Fix" / "Textures" / "T").mkdir(parents=True)
    (repo / "README").write_text("x")
    git(repo, "add", "README")
    git(repo, "commit", "-q", "-m", "root")
    return repo


def test_a():
    import artledger as L
    import art_guard as G
    import backfill as BF
    repo = git_fixture()
    shard = "infrastructure/state/art/events/BUILD.jsonl"
    mod, slot = "src/RimMandrake/Fix", "src/RimMandrake/Fix/Textures/T/Beast_south.png"
    red, blue, green = png((255, 0, 0, 255)), png((0, 0, 255, 255)), png((0, 255, 0, 255))
    sred, sblue, sgreen = (L.store_put_bytes(x) for x in (red, blue, green))

    base = git(repo, "rev-parse", "HEAD")
    L.install(mod, "T/Beast_south.png", sred, reason=WRITER)
    git(repo, "add", shard)
    git(repo, "commit", "-q", "-m", "events only")         # the 10-07 FlowWorks shape: event pushed, PNG left behind
    bad = G.check_range(repo, base, "HEAD")
    check(any(p == slot and "no such file" in w for _c, p, w in bad),
          f"push check: a live event whose PNG is not in the pushed tree is refused ({bad})")
    rows = G.doctor(repo)
    check([r["kind"] for r in rows] == ["LIVE_NOT_IN_TREE"] and rows[0]["uncommitted_install"],
          "doctor lists it as LIVE_NOT_IN_TREE, an install sitting uncommitted in the worktree")
    git(repo, "add", slot)
    git(repo, "commit", "-q", "-m", "png")
    check(G.check_range(repo, base, "HEAD") == [], "push check passes once the PNG travels with its event")
    check(G.doctor(repo) == [], "doctor is clean when the committed tree matches the ledger")

    base2 = git(repo, "rev-parse", "HEAD")
    L.install(mod, "T/Beast_south.png", sblue, reason=WRITER)
    L.install(mod, "T/Beast_south.png", sgreen, reason=WRITER)   # blue's event is superseded inside the range
    git(repo, "add", shard, slot)
    git(repo, "commit", "-q", "-m", "two installs, last one shipped")
    check(G.check_range(repo, base2, "HEAD") == [], "a superseded event in the range is allowed")

    # the tree changes in a commit but the ledger is not told (direction 1 still bites)
    base3 = git(repo, "rev-parse", "HEAD")
    (repo / slot).write_bytes(red)
    git(repo, "add", slot)
    git(repo, "commit", "-q", "-m", "raw revert")
    bad = G.check_range(repo, base3, "HEAD")
    check(len(bad) == 1 and bad[0][1] == slot, f"a raw byte change is reported once, not twice ({bad})")
    git(repo, "reset", "-q", "--hard", base3)

    # backfill re-scan: a differing disk file is DRIFT, reported, not relabelled; an unrecorded file is observed
    (repo / slot).write_bytes(red)                     # disk now disagrees with the ledger's green
    newf = repo / "src" / "RimMandrake" / "Fix" / "Textures" / "T" / "Other.png"
    newf.write_bytes(blue)
    n_before = len(L.read_events())
    r = BF.step_disk()
    lv = [e for e in L.read_events()[n_before:] if e.get("type") == "live"]
    check(r.get("drift") == 1, f"backfill reports the differing slot as drift ({r})")
    check([e["rel"] for e in lv] == ["T/Other.png"], "backfill writes live only for the slot with no record")
    check(L.Index().live[(mod, "T/Beast_south.png")]["sha"] == sgreen, "the recorded live sha is NOT overwritten")
    (repo / slot).write_bytes(green)

    # a hand-written backfill-observed relabel is refused by the guard (enforced from ENFORCE_FROM)
    git(repo, "add", shard, "src/RimMandrake/Fix/Textures/T/Other.png")
    git(repo, "commit", "-q", "-m", "backfill")
    base4 = git(repo, "rev-parse", "HEAD")
    check(G.check_range(repo, base3, base4) == [], "a backfill of a never-recorded slot passes the push check")
    L.append({"type": "live", "mod": mod, "rel": "T/Beast_south.png", "sha": sred, "prev": None,
              "reason": "backfill-observed", "ts": "2099-01-01T00:00:00-0700"})
    (repo / slot).write_bytes(red)
    git(repo, "add", shard, slot)
    git(repo, "commit", "-q", "-m", "relabel")
    bad = G.check_range(repo, base4, "HEAD")
    check(any("backfill" in w for _c, _p, w in bad), f"push check refuses a backfill that relabels a recorded slot ({bad})")
    git(repo, "reset", "-q", "--hard", base4)
    L.append({"type": "live", "mod": mod, "rel": "T/Beast_south.png", "sha": sred, "prev": None,
              "reason": "backfill-observed", "ts": "2099-01-01T00:00:01-0700"})
    git(repo, "add", shard)
    git(repo, "commit", "-q", "-m", "relabel, ledger only (the exact 10-14 shape: tree untouched)")
    bad = G.check_range(repo, base4, "HEAD")
    check(any("backfill" in w for _c, _p, w in bad), f"…also when only the event moves ({bad})")


def test_c():
    import artledger as L
    import art_guard as G
    import art
    tmp = fixture()
    canon = "src/RimStarWars/SWBestiary"
    red, blue, green = png((255, 0, 0, 255)), png((0, 0, 255, 255)), png((0, 255, 0, 255))
    sred, sblue, sgreen = (L.store_put_bytes(x) for x in (red, blue, green))
    rel = "Things/Nuna/Nuna_south.png"
    for bad in ("script:decision taken by question card 2026-10-11", "script:owner-card-2026-10-09-rot",
                "script:src/no/such/writer.py", "retire-duplicate", "script:../../etc/passwd"):
        check(refused(L.install, canon, rel, sred, reason=bad) is not None, f"install refuses reason {bad!r}")
    check(refused(L.install, canon, rel, sred, reason=WRITER + " (note after the path)") is None,
          "install accepts script:<existing repo path> with a trailing note")
    check(refused(L.retire, tmp / canon / "Textures" / rel, reason="retire-duplicate") is not None,
          "retire refuses the hand-typed retire-duplicate tag")

    # the guard: new events judged by the new rules, old events by theirs
    L.append({"type": "ruling", "id": "keepred", "target": {"sha": sred}, "verdict": "keep", "by": "owner",
              "trust": "ruled", "said": "fixture"})
    idx = L.Index()
    NEW, OLD = "2099-01-01T00:00:00-0700", "2026-10-10T00:00:00-0700"
    ev = {"type": "live", "mod": canon, "rel": rel, "sha": sblue, "prev": sred, "reason": "retire-duplicate"}
    check(G._authorized({**ev, "ts": NEW}, idx) is not None, "guard: a new retire-duplicate over a kept picture is refused")
    check(G._authorized({**ev, "ts": NEW, "said": "Yes, retire the duplicate."}, idx) is None,
          "guard: retire-duplicate carrying his words passes")
    check(G._authorized({**ev, "ts": OLD}, idx) is None, "guard: a pre-enforcement retire-duplicate keeps its old rule")
    ev2 = {"type": "live", "mod": canon, "rel": rel, "sha": sblue, "prev": sgreen,
           "reason": "script:decision taken by question card 2026-10-11"}
    check(G._authorized({**ev2, "ts": NEW}, idx) is not None, "guard: a new free-text script: tag is refused")
    check(G._authorized({**ev2, "ts": OLD}, idx) is None, "guard: an old free-text script: tag is not re-judged")
    check(G._authorized({**ev2, "reason": WRITER, "ts": NEW}, idx) is None, "guard: a verifiable script: writer passes")

    # purge never silently releases a keep
    L.append({"type": "ruling", "id": "keepblue_sheetA", "target": {"shas": [sblue], "row": "Nuna"}, "verdict": "keep",
              "by": "owner", "trust": "ruled", "via": "sheetA.decisions.json", "said": "keep"})
    msg = refused(L.purge, sblue, owner_said="cut it", via="sheetB.decisions.json",
                  release_from_sheet=("sheetB.decisions.json", "Nuna"))
    check(msg is not None and "never silently releases" in msg and L.store_has(sblue),
          "purge from another sheet refuses a picture kept elsewhere; bytes stay")
    check(not [e for e in L.read_events() if e.get("verdict") == "release"], "…and writes no release")
    check(refused(L.purge, sblue, owner_said="x", release_keep={"someotherkeep"}) is not None,
          "purge naming a different keep id refuses")
    check(refused(L.purge, sblue, owner_said="x", via="sheetA.decisions.json",
                  release_from_sheet=("sheetA.decisions.json", "Nuna")) is None and not L.store_has(sblue),
          "the same sheet row that minted the keep may release it with its ✕")
    L.store_put_bytes(green)
    L.append({"type": "ruling", "id": "keepgreen", "target": {"sha": sgreen}, "verdict": "keep", "by": "owner",
              "trust": "ruled", "said": "keep"})
    check(refused(L.purge, sgreen, owner_said="delete it, I release the keep", release_keep=True) is None,
          "art purge --release-keep (his explicit words) still releases")

    # kept-but-purged: reported, not deleted
    L.append({"type": "ruling", "id": "late_keep", "target": {"sha": sblue}, "verdict": "keep", "by": "owner",
              "trust": "ruled", "via": "sheetC.decisions.json", "said": "keep this"})
    idx = L.Index()
    kp = idx.kept_but_purged()
    check([r["sha"] for r in kp] == [sblue] and not kp[0]["bytes_in_store"],
          "kept_but_purged lists a purged picture with an active keep (and only it)")
    n = len(L.read_events())
    out = tmp / "kept_but_purged.md"
    check(art.main(["kept-purged", "--out", str(out)]) == 0 and sblue[:16] in out.read_text()
          and len(L.read_events()) == n, "art.py kept-purged writes the report and no events")


def test_d():
    """An extension-less rel is refused (44 twins, 2026-10-18); a duplicate slot of a kept picture retires on a
    mechanical reason, the last slot holding it does not."""
    import artledger as L
    import art_guard as G
    tmp = fixture()
    mod = "src/RimMandrake/FlowWorks"
    sred = L.store_put_bytes(png((255, 0, 0, 255)))
    msg = refused(L.install, mod, "SuspensionBridge/Modern/RM_SuspensionDeck", sred, reason=WRITER)
    check(msg is not None and "image extension" in msg, "install refuses a rel with no image extension")
    check(not (tmp / mod / "Textures" / "SuspensionBridge").exists(), "...and writes nothing")
    L.install(mod, "A/Deck.png", sred, owner_said="fixture keep")
    L.install(mod, "A/DeckTwin.png", sred, reason=WRITER)
    check(refused(L.retire, tmp / mod / "Textures" / "A/DeckTwin.png", reason=WRITER) is None,
          "retire of a duplicate slot of a kept picture needs no owner words")
    check(refused(L.retire, tmp / mod / "Textures" / "A/Deck.png", reason=WRITER) is not None,
          "retire of the last slot holding a kept picture still needs his words")
    # the guard agrees with retire (CHIKKA_HOME_DECIDE_NOT_STAR_WARS, 2026-10-24: it refused the duplicate's retire)
    twin = [e for e in L.read_events() if e.get("type") == "live" and e.get("rel") == "A/DeckTwin.png"][-1]
    check(twin.get("sha") is None and G._authorized(twin, L.Index()) is None,
          "guard: the retire of a duplicate slot of a kept picture passes")
    last = {**twin, "rel": "A/Deck.png"}
    check(G._authorized(last, L.Index()) is not None,
          "guard: a mechanical retire of the last slot holding a kept picture is refused")


def test_e():
    """install --owner-said on an already-live picture records his ruling once, writes nothing else; a different
    hash is a normal install (the ruling names the NEW sha only)."""
    import artledger as L
    tmp = fixture()
    mod = "src/RimMandrake/FlowWorks"
    sred = L.store_put_bytes(png((255, 0, 0, 255)))
    sblue = L.store_put_bytes(png((0, 0, 255, 255)))
    L.install(mod, "E/Alt.png", sred, reason=WRITER)
    tgt = tmp / mod / "Textures" / "E/Alt.png"
    nrul = lambda sha: len(L.cached_index().rulings_by_sha.get(sha, []))
    r = L.install(mod, "E/Alt.png", sred, owner_said="approved by card")
    check(r["status"] == "already-live-ruled" and nrul(sred) == 1, "already-live + same hash records exactly one ruling")
    r = L.install(mod, "E/Alt.png", sred, owner_said="approved by card")
    check(r["status"] == "already-live" and nrul(sred) == 1, "...and a repeat records nothing more")
    L.install(mod, "E/Alt.png", sblue, owner_said="actually the blue")
    check(nrul(sblue) == 1 and nrul(sred) == 1 and L.sha256_file(tgt) == sblue,
          "a different hash is a real install: the ruling names the new sha only")


def main():
    sys.path.insert(0, str(HERE))
    tmp = fixture()
    test_b(tmp)
    test_a()
    test_c()
    test_d()
    test_e()
    print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
