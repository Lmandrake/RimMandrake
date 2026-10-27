#!/usr/bin/env python3
"""selftest_art_x_ban_hardening.py — the holes an independent review of the ✕ = delete forever + ban build found
(owner card 2026-10-26 19:54: his ✕ deletes the picture for ever and bans it and its near-duplicates; only his typed
words lift a ban). Each check below failed on the code as built (a9a6c82cd6):
  * a failed ledger append part-way through x_delete left his picture DELETED BUT NOT BANNED (the files and store
    bytes were unlinked before the one flush that wrote the ban) - the ban is now on disk before any byte goes;
  * the ban fold depended on shard order: a newer ✕ folded before an older, since-lifted one was lost;
  * `restore` (undo of a 19:06 archive) put back a near-duplicate of a banned picture on a standing ruling alone;
  * art_eval discarded a candidate because a REFERENCE panel (the living animal, siblings) showed a banned picture;
  * archived_shas still listed a restored (live) picture that carried an archive ruling
    (ARCHIVED_SHAS_FIX_LIVE_SUBTRACTION).
Coverage added with them: a mirrored redraw is a near-duplicate; an owner-kept look-alike is exempt from the near
check while the kept exact banned sha is still refused; install's refusal names the ban.
Fixture under /home/mandrake/rm/scratch/BENCH (never /tmp)."""
from __future__ import annotations

import io
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import selftest_enact as T  # noqa: E402
import selftest_art_x_ban as XB  # noqa: E402

FAILS = []
WHY = "script:src/RimMandrake/Utils/art/selftest_art_x_ban_hardening.py"


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def mirrored(png: bytes) -> bytes:
    from PIL import Image, ImageOps
    b = io.BytesIO()
    ImageOps.mirror(Image.open(io.BytesIO(png)).convert("RGBA")).save(b, "PNG")
    return b.getvalue()


def fold_order(L):
    """A newer ✕ (ban2) folded BEFORE an older ✕ (ban1) whose ban his words lifted (unban1): ban2 stays in force."""
    s = "ab" * 32
    ban1 = {"type": "ban", "id": "ban1", "sha": s, "ph": "0" * 64, "mark": {"at": "2026-10-26T10:00:00Z"},
            "ts": "2026-10-26T10:00:01"}
    ban2 = {"type": "ban", "id": "ban2", "sha": s, "ph": "0" * 64, "mark": {"at": "2026-10-26T12:00:00Z"},
            "ts": "2026-10-26T12:00:01"}
    un1 = {"type": "unban", "id": "un1", "sha": s, "follows": "ban1", "said": "bring it back", "ts": "2026-10-26T11:00:00"}
    for order in ((ban2, ban1, un1), (ban1, un1, ban2), (un1, ban2, ban1), (ban1, ban2, un1)):
        idx = L.Index(list(order))
        check((idx.bans.get(s) or {}).get("id") == "ban2",
              f"ban fold order {[e['id'] for e in order]}: the unlifted newer ban stays in force")
    un2 = {"type": "unban", "id": "un2", "sha": s, "follows": "ban2", "said": "and that one", "ts": "2026-10-26T13:00:00"}
    check(s not in L.Index([ban2, un2, ban1, un1]).bans, "both bans lifted -> not banned, whatever the order")


def archived_live(L):
    """A restored picture that carries an archive ruling is live, not archived (ARCHIVED_SHAS_FIX_LIVE_SUBTRACTION)."""
    s = "cd" * 32
    evs = [{"type": "live", "id": "l1", "mod": "M", "rel": "a.png", "sha": s, "prev": None, "reason": "x",
            "ts": "2026-10-26T10:00:00"},
           {"type": "ruling", "id": "r1", "target": {"sha": s}, "verdict": "archive", "ts": "2026-10-26T10:00:01"}]
    check(s not in L.archived_shas(L.Index(evs)), "archived_shas does not list a live picture with an archive ruling")
    check(s in L.archived_shas(L.Index(evs[1:])), "archived_shas still lists an archive-ruled picture in no game file")


def main():
    import artledger as L
    fold_order(L)
    archived_live(L)
    F = T.build(T.SCRATCH / f"art_x_ban_hard_{os.getpid()}")
    L.MARK_ROOT = F["root"]
    try:
        banned_b, near_b, other_b = XB.sprite(23), XB.near_dup(XB.sprite(23)), XB.sprite(97)
        texdir = F["src"] / "RimMandrake/TestMod/Textures/Things/Pawn/Animal/RM_Ban"
        texdir.mkdir(parents=True, exist_ok=True)
        tex = texdir / "RM_Ban_east.png"
        sha = L.install_bytes(tex, banned_b, reason=WHY).get("new") or L.sha256_bytes(banned_b)
        # a near-duplicate archived under the 19:06 rule before the ✕ (bytes in the store, slot empty)
        rel_near = "Things/Pawn/Animal/RM_Ban/RM_Ban_north.png"
        near_sha = L.install_bytes(texdir / "RM_Ban_north.png", near_b, reason=WHY).get("new") or L.sha256_bytes(near_b)
        live_near = L.Index().live.get((T.MOD, rel_near)) or {}
        (texdir / "RM_Ban_north.png").unlink()
        L.append({"type": "live", "mod": T.MOD, "rel": rel_near, "sha": None, "prev": near_sha, "reason": "archive",
                  "follows": live_near.get("id"), "why": WHY})

        at = "2026-10-26T19:54:00.000Z"
        via = str(F["decisions"].relative_to(F["root"]))
        doc = json.loads(F["decisions"].read_text())
        doc["decisions"] = {"RM_Ban": {"decision": "redo", "at": at, "decidedAt": at, "purge": [sha]}}
        F["decisions"].write_text(json.dumps(doc))
        mark = {"sheet": "test_sheet", "row": "RM_Ban", "at": at, "via": via, "kind": "x"}

        # ── a ledger append failing after the ban: his picture must never be deleted yet unbanned
        real_flush = L.Writer.flush

        def failing_flush(self):
            if any(e.get("type") != "ban" for e in self.buf):
                raise OSError("simulated: disk full while appending the ledger")
            return real_flush(self)
        L.Writer.flush = failing_flush
        try:
            L.x_delete(sha, mark, subject="RM_Ban")
            check(False, "fixture: the simulated append failure raised")
        except OSError:
            pass
        finally:
            L.Writer.flush = real_flush
        idx = L.Index()
        check(sha in idx.bans or (tex.is_file() and L.store_has(sha)),
              "an x_delete cut short by a failed append leaves the picture either present or BANNED, never deleted "
              f"and unbanned (file {tex.is_file()}, store {L.store_has(sha)}, banned {sha in idx.bans})")
        res = L.x_delete(sha, mark, subject="RM_Ban")
        idx = L.Index()
        check(res["status"] == "deleted" and not tex.exists() and not L.store_has(sha) and sha in idx.bans
              and idx.is_purged(sha) and sum(1 for e in idx.events if e.get("type") == "ban") == 1,
              "re-running the ✕ finishes it: file and bytes gone, purged, one ban")

        # ── restore cannot bring back a near-duplicate of a banned picture
        try:
            L.restore(near_sha[:12], per_ruling="standing ruling")
            check(False, "restore refuses a near-duplicate of a banned picture")
        except L.Refused as e:
            check("banned" in str(e) and not (texdir / "RM_Ban_north.png").exists(),
                  "restore refuses a near-duplicate of a banned picture")

        # ── install's refusal names the ban
        try:
            L.install(T.MOD, "Things/Pawn/Animal/RM_Ban/RM_Ban_west.png", sha, reason=WHY)
            check(False, "install refuses the banned sha")
        except L.Refused as e:
            check("banned" in str(e), f"install refuses the banned sha and says why ({str(e)[:60]}...)")

        # ── mirror: a horizontally flipped redraw is a near-duplicate
        m = mirrored(banned_b)
        hit = L.ban_match(L.cached_index(), data=m)
        check(bool(hit) and hit["how"] == "near", f"a mirrored redraw is a near-duplicate ({hit and hit['d']})")

        # ── an owner keep of a look-alike exempts it from the near check, never the exact banned bytes
        kept_sha = L.store_put_bytes(near_dup(banned_b, 58))
        check(bool(L.ban_match(L.cached_index(), sha=kept_sha)), "fixture: the look-alike is a near-duplicate")
        for s_ in (kept_sha, sha):
            L.append({"type": "ruling", "id": f"keep_{s_[:8]}", "target": {"sha": s_, "row": "RM_Ban"},
                      "verdict": "keep", "by": "owner", "trust": "ruled", "at": "2026-10-26T20:00:00Z", "via": via})
        idx = L.Index()
        check(L.ban_match(idx, sha=kept_sha) is None, "an owner-kept look-alike is not refused as a near-duplicate")
        check((L.ban_match(idx, sha=sha) or {}).get("how") == "exact", "a keep never lets the exact banned sha in")

        # ── art_eval: a banned picture in a reference panel does not discard the candidate
        sys.path.insert(0, str(HERE.parent / "art_eval"))
        import runner as RU
        out = F["root"] / "renders"
        out.mkdir(exist_ok=True)
        (out / "other.png").write_bytes(other_b)
        (out / "exact.png").write_bytes(banned_b)
        spec = {"subject": "RM_BanCatch", "images": {"east": str(out / "other.png"),
                                                     "living_reference": {"east": str(out / "exact.png")},
                                                     "siblings": [str(out / "exact.png")]}}
        check(not RU.banned_candidates(spec), "art_eval judges a distinct candidate whose reference panels show a "
                                              "banned picture")
        spec_v = {"subject": "RM_BanCatch", "images": {"east": str(out / "other.png"), "variants": [str(out / "exact.png")]}}
        check(len(RU.banned_candidates(spec_v)) == 1, "art_eval still discards a banned picture among the variants")
    finally:
        shutil.rmtree(F["root"], ignore_errors=True)
    print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAILED'}")
    return 1 if FAILS else 0


def near_dup(png: bytes, size: int) -> bytes:
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert("RGBA")
    b = io.BytesIO()
    im.resize((size, size), Image.LANCZOS).resize(im.size, Image.LANCZOS).save(b, "PNG")
    return b.getvalue()


if __name__ == "__main__":
    sys.exit(main())
