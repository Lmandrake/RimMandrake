#!/usr/bin/env python3
"""selftest_art_install_authority.py: RIMMANDRAKE_FIX_ART_INSTALL_MINTS_OWNER_KEEP_SIXTEEN_FALSE.

An install by a run is not the owner's keep. Proves, on a disposable fixture (never real Textures):
  * an install that cites a Conductor ruling records no owner keep and protects nothing, and keeps the cited ruling and
    the --why text on the live event;
  * `correct_keep` (art.py correct-keep) releases a keep that a run recorded by this mistake, by appending an event;
  * the cases that stay refused: a Conductor install over a keep carrying `said`, `by_card` or another `per_ruling`, and
    the correction command on those kinds of keep.
Each `t_<promise>` below is a promise of design/specs/art-install-authority/boundary.md.
"""
from __future__ import annotations

import os
import random
import sys
import tempfile
from io import BytesIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILS = []
COND_A = "RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS"
COND_B = "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM"
WHY = "the Conductor's ruling of 2026-11-25: a helper run installed this piece and the tool recorded the install as a keep"


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def noisy(seed):
    from PIL import Image
    rnd = random.Random(seed)
    im = Image.new("RGBA", (16, 16))
    im.putdata([(rnd.randrange(256), rnd.randrange(256), rnd.randrange(256), 255) for _ in range(256)])
    b = BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


class Fix:
    """A fixture ledger + slots. `pic(n)` makes picture n (in the store); `slot(n)` is a fresh texture path."""

    def __init__(self):
        tmp = Path(tempfile.mkdtemp(prefix="artinstauth-selftest-"))
        os.environ["ARTSTORE"] = str(tmp / "store")
        os.environ["ART_LEDGER_DIR"] = str(tmp / "ledger")
        os.environ["ART_SRC_ROOT"] = str(tmp / "src")
        os.environ["ART_SEAT"] = "BUILD"
        sys.path.insert(0, str(HERE))
        import artledger
        self.L = artledger
        self.mod = "src/FixtureMod"
        (tmp / self.mod / "Textures" / "Things").mkdir(parents=True)
        self.n = 0

    def pic(self):
        self.n += 1
        data = noisy(self.n)
        self.L.store_put_bytes(data)
        return self.L.sha256_bytes(data)

    def slot(self):
        self.n += 1
        return f"Things/Slot{self.n}.png"


def refused(fn, *a, **kw):
    """-> (True, message) when fn raised Refused; (False, text) when it returned or raised anything else."""
    try:
        r = fn(*a, **kw)
        return False, "returned %r" % (r,)
    except Fix_L.Refused as e:
        return True, str(e)
    except Exception as e:  # noqa: BLE001  a missing function or a crash is not a refusal
        return False, "%s: %s" % (type(e).__name__, e)


Fix_L = None


def keep_of(L, sha):
    return [r for r in L.Index().rulings if r.get("verdict") == "keep" and (r.get("target") or {}).get("sha") == sha]


def t_conductor_install_mints_no_owner_keep(F):
    L = F.L
    for rul in (COND_A, COND_B):
        rel, s = F.slot(), F.pic()
        r = L.install(F.mod, rel, s, per_ruling=rul, why=WHY)
        idx = L.Index()
        live = idx.live[(F.mod, rel)]
        owner_keeps = [k for k in keep_of(L, s) if k.get("by") == "owner"]
        check(r["status"] == "installed" and not owner_keeps and not idx.protected(s),
              "an install citing %s records no owner keep and protects nothing" % rul[:20])
        check(live.get("per_ruling") == rul and live.get("why") == WHY and "ruling_id" not in live,
              "the live event of a Conductor install keeps the cited ruling and the --why text (%s)" % rul[:20])
        # a picture the same install left in place (already live): still no owner keep
        r2 = L.install(F.mod, rel, s, per_ruling=rul, why=WHY)
        check(not [k for k in keep_of(L, s) if k.get("by") == "owner"] and r2["status"] == "already-live",
              "re-citing a Conductor ruling for the picture already live mints no owner keep (%s)" % rul[:20])
        # not protected: a later install by the pipeline (a mechanical --why install) replaces it
        s2 = F.pic()
        r3 = L.install(F.mod, rel, s2, why="delegated: art verdict.json")
        check(r3["status"] == "installed", "a Conductor install does not protect the picture against a later pipeline install (%s)" % rul[:20])


def t_conductor_install_never_displaces_other_authority(F):
    """Green before and after the change: a Conductor ruling never replaces a picture whose keep carries his words,
    his card, or another ruling's id (fail closed)."""
    L = F.L
    keeps = {
        "said": dict(owner_said="blue is better"),
        "by_card": dict(by_card="Which tank? → the white one"),
        "other per_ruling": dict(per_ruling="FORD_STONES_REDRAW_LOOK_LIKE_A_SMUDGE", why="applying his ruling"),
    }
    for kind, kw in keeps.items():
        rel, kept, other = F.slot(), F.pic(), F.pic()
        L.install(F.mod, rel, kept, **kw)
        for rul in (COND_A, COND_B):
            ok, msg = refused(L.install, F.mod, rel, other, per_ruling=rul, why=WHY)
            check(ok and "stays his" in msg, "a Conductor install (%s) over a keep carrying %s stays refused" % (rul[:20], kind))


def t_correct_keep_releases_conductor_only_keep(F):
    """A keep that carries only a Conductor ruling (recorded before the fix) is released by an appended event."""
    L = F.L
    for rul in (COND_A, COND_B):
        rel, s = F.slot(), F.pic()
        # the keep as the old tool wrote it: by owner, per_ruling only
        old = L.owner_keep_ruling(s, per_ruling=rul)
        old["via"] = "art install (per ruling)"
        w = L.Writer({e["id"] for e in L.Index().events})
        w.add(old)
        w.flush()
        L._absorb(list(w.buf))
        check(bool(L.cached_index().protected(s)), "fixture: the old Conductor-only keep protects (%s)" % rul[:20])
        n_before = len(L.read_events())
        ok, msg = refused(L.correct_keep, s[:12], why=WHY, per_ruling=rul, dry_run=True)
        check(not ok and "returned" in msg and len(L.read_events()) == n_before,
              "--dry-run plans the correction and writes nothing (%s)" % rul[:20])
        r = L.correct_keep(s[:12], why=WHY, per_ruling=rul)
        idx = L.Index()
        rl = next((x for x in idx.rulings if x.get("releases") == old["id"]), {})
        check(r["status"] == "recorded" and not idx.protected(s) and rl.get("by") != "owner"
              and rl.get("per_ruling") == rul and rl.get("why") == WHY and len(L.read_events()) == n_before + 1,
              "correct_keep appends one event that releases the keep and keeps the ruling and the why (%s)" % rul[:20])
        check(any(e["id"] == old["id"] for e in L.read_events()), "the corrected keep stays in the ledger: no history is deleted")
        r2 = L.correct_keep(s[:12], why=WHY, per_ruling=rul)
        check(r2["status"] == "already-corrected" and len(L.read_events()) == n_before + 1,
              "a second correction of the same keep writes nothing")
        # by event id too
        s3 = F.pic()
        old3 = L.owner_keep_ruling(s3, per_ruling=rul)
        old3["via"] = "art install (per ruling)"
        w = L.Writer({e["id"] for e in L.Index().events})
        w.add(old3)
        w.flush()
        L._absorb(list(w.buf))
        L.correct_keep(old3["id"], why=WHY, per_ruling=rul)
        check(not L.Index().protected(s3), "an event id names a Conductor-only keep too (%s)" % rul[:20])
        rel2 = F.slot()
        check(L.install(F.mod, rel2, s, why="delegated: art verdict.json")["status"] == "installed",
              "a released picture installs again under the mechanical guards (%s)" % rul[:20])


def t_correct_keep_refuses_his_keeps(F):
    """Stays refused, green before (no command) and after: the correction never touches a keep with his words, his
    card, or another ruling's id."""
    L = F.L
    cases = {
        "said": dict(owner_said="blue is better"),
        "by_card": dict(by_card="Which tank? → the white one"),
        "other per_ruling": dict(per_ruling="FORD_STONES_REDRAW_LOOK_LIKE_A_SMUDGE", why="applying his ruling"),
    }
    for kind, kw in cases.items():
        rel, s = F.slot(), F.pic()
        L.install(F.mod, rel, s, **kw)
        keep = keep_of(L, s)[0]
        n_before = len(L.read_events())
        for rul in (COND_A, COND_B):
            ok, msg = refused(L.correct_keep, s[:12], why=WHY, per_ruling=rul)
            check(ok and L.Index().protected(s), "correct_keep by picture refuses a keep carrying %s" % kind)
            if kind != "said":
                ok, msg = refused(L.correct_keep, keep["id"], why=WHY + " " + keep["id"], per_ruling=rul)
                check(ok and L.Index().protected(s), "correct_keep by event id refuses a keep carrying %s" % kind)
        check(len(L.read_events()) == n_before, "a refused correction of a keep carrying %s writes nothing" % kind)
    # his words AND a card (or another ruling) on one install keep: not "said alone", so refused by event id
    for extra in (dict(by_card="Which tank? → the white one"), dict(per_ruling="FORD_STONES_REDRAW_LOOK_LIKE_A_SMUDGE")):
        rel, s = F.slot(), F.pic()
        L.install(F.mod, rel, s, owner_said="blue is better", **extra)
        keep = keep_of(L, s)[0]
        ok, msg = refused(L.correct_keep, keep["id"], why=WHY + " " + keep["id"], per_ruling=COND_A)
        check(ok and L.Index().protected(s), "correct_keep by event id refuses a keep carrying said and %s" % next(iter(extra)))
    # a keep that is his words but NOT an install (a sheet ruling): refused by event id too
    s = F.pic()
    sheet = {"id": "sheetkeep-" + s[:8], "type": "ruling", "target": {"sha": s}, "verdict": "keep", "by": "owner",
             "said": "keep this", "via": "decisions/tank.decisions.json", "trust": "ruled", "subject_key": ""}
    w = L.Writer({e["id"] for e in L.Index().events})
    w.add(sheet)
    w.flush()
    L._absorb(list(w.buf))
    ok, msg = refused(L.correct_keep, sheet["id"], why=WHY + " " + sheet["id"], per_ruling=COND_A)
    check(ok and L.Index().protected(s), "correct_keep by event id refuses his words on a sheet ruling (not an install)")
    # an event that is no ruling at all
    live_id = next(e["id"] for e in L.read_events() if e.get("type") == "live")
    ok, msg = refused(L.correct_keep, live_id, why=WHY + " " + live_id, per_ruling=COND_A)
    check(ok, "correct_keep refuses an event that is not an install ruling")
    # the correction is the Conductor's act and needs its words
    s = F.pic()
    old = L.owner_keep_ruling(s, per_ruling=COND_A)
    old["via"] = "art install (per ruling)"
    w = L.Writer({e["id"] for e in L.Index().events})
    w.add(old)
    w.flush()
    L._absorb(list(w.buf))
    for kw in (dict(why="", per_ruling=COND_A), dict(why=WHY, per_ruling="SOME_OTHER_RULING"), dict(why=WHY, per_ruling=None)):
        ok, msg = refused(L.correct_keep, s[:12], **kw)
        check(ok and L.Index().protected(s), "correct_keep needs a Conductor ruling and a --why (%s)" % (kw["per_ruling"] or "none")[:20])


def t_correct_keep_by_event_id_releases_install_said(F):
    """A keep that an install recorded with `said` (a run passed the owner's order as --owner-said) is corrected by
    its event id, when the Conductor's --why names the install."""
    L = F.L
    rel, s = F.slot(), F.pic()
    L.install(F.mod, rel, s, owner_said="the jetties still look like two blocks, FIX")
    keep = keep_of(L, s)[0]
    check(keep.get("via") == "art install (owner words)", "fixture: an install recorded his words as a keep")
    ok, msg = refused(L.correct_keep, s[:12], why=WHY, per_ruling=COND_B)
    check(ok and L.Index().protected(s), "by picture, the correction still refuses a keep carrying said")
    ok, msg = refused(L.correct_keep, keep["id"], why="the owner never kept this", per_ruling=COND_B)
    check(ok and L.Index().protected(s), "by event id, a --why that does not name the install is refused")
    r = L.correct_keep(keep["id"], why=WHY + " [install event %s]" % keep["id"], per_ruling=COND_B)
    check(r["status"] == "recorded" and not L.Index().protected(s) and any(e["id"] == keep["id"] for e in L.read_events()),
          "by event id, a --why that names the install releases the said keep and deletes no history")


def t_art_cli_correct_keep_and_install_help(F):
    import art
    L = F.L
    rel, s = F.slot(), F.pic()
    old = L.owner_keep_ruling(s, per_ruling=COND_A)
    old["via"] = "art install (per ruling)"
    w = L.Writer({e["id"] for e in L.Index().events})
    w.add(old)
    w.flush()
    L._absorb(list(w.buf))
    try:
        rc = art.main(["correct-keep", s[:12], "--per-ruling", COND_B, "--why", WHY])
    except SystemExit as e:
        rc = e.code
    check(rc == 0 and not L.Index().protected(s), "art.py correct-keep <sha> --per-ruling --why releases the keep (exit 0)")
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = art.main(["correct-keep", s[:12], "--per-ruling", "NOT_A_RULING", "--why", WHY])
    check(rc == 2 and "REFUSED" in buf.getvalue(), "art.py correct-keep prints REFUSED and exits 2 when refused")
    import subprocess
    out = subprocess.run([sys.executable, str(HERE / "art.py"), "install", "--help"], capture_output=True, text=True).stdout
    flat = " ".join(out.split())
    check("--owner-said on an install means that the owner chose this picture" in flat,
          "art.py install --help says --owner-said means the owner chose this picture")
    check("an order of the owner to fix a thing goes in --why" in flat, "art.py install --help says an order to fix a thing goes in --why")


def main():
    global Fix_L
    F = Fix()
    Fix_L = F.L
    for t in (t_conductor_install_mints_no_owner_keep, t_conductor_install_never_displaces_other_authority,
              t_correct_keep_releases_conductor_only_keep, t_correct_keep_refuses_his_keeps,
              t_correct_keep_by_event_id_releases_install_said, t_art_cli_correct_keep_and_install_help):
        try:
            t(F)
        except Exception as e:  # noqa: BLE001  a crash in one promise is that promise's FAIL, the rest still run
            check(False, "%s crashed: %s: %s" % (t.__name__, type(e).__name__, e))
    print("\n%d failure(s)" % len(FAILS))
    for f in FAILS:
        print("  FAIL:", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
