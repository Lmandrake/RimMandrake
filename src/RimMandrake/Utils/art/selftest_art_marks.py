#!/usr/bin/env python3
"""selftest_art_marks.py - newest mark wins, X archives (owner card 2026-10-26 19:06, ART_MARKS_BUILD_NEWEST_WINS_ARCHIVE).

On a disposable clone: his newer pick installs over an older keep and the guard accepts the commit shape; an older
pick never replaces a newer keep; his X moves an in-game picture to the art archive (bytes kept, no purge) and
`restore` brings the identical bytes back; an agent-made or unstamped mark never qualifies; each act is a digest line.
"""
from __future__ import annotations

import atexit as _a, os as _o, shutil as _s, tempfile as _t  # noqa: E401
_t.tempdir = _o.environ["TMPDIR"] = _t.mkdtemp(prefix="st_selftest_art_marks_")
_a.register(_s.rmtree, _t.tempdir, True)
import json
import os
import sys
import tempfile
from io import BytesIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FAILS = []
MOD = "src/RimStarWars/SWBestiary"
REL = "Things/Nuna/Nuna_south.png"
T0, T1, T3, T5 = "2026-10-26T01:00:00-0700", "2026-10-26T02:00:00-0700", "2026-10-26T03:00:00-0700", "2026-10-26T05:00:00-0700"


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


def git(tmp, *a):
    import subprocess
    r = subprocess.run(["git", "-C", str(tmp), "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *a],
                       capture_output=True, text=True, timeout=60)
    if r.returncode:
        raise RuntimeError(r.stderr)
    return r.stdout.strip()


def main():
    tmp = Path(tempfile.mkdtemp(prefix="art-marks-"))
    os.environ.update(ARTSTORE=str(tmp / "store"), ART_LEDGER_DIR=str(tmp / "infrastructure/state/art"),
                      ART_SRC_ROOT=str(tmp / "src"), ART_SEAT="BUILD")
    (tmp / "infrastructure/state/art/events").mkdir(parents=True)
    git(tmp, "init", "-q")
    (tmp / "src" / "RimStarWars" / "SWBestiary" / "Textures").mkdir(parents=True)
    import artledger as L
    import art_guard as G
    L.MARK_ROOT = tmp                                   # decisions files are looked up inside the clone
    dest = tmp / MOD / "Textures" / REL
    path = f"{MOD}/Textures/{REL}"
    A, B, C = (L.store_put_bytes(png(c)) for c in ((200, 0, 0, 255), (0, 200, 0, 255), (0, 0, 200, 255)))

    def sheet(name, at, purge=()):
        (tmp / "sheets").mkdir(exist_ok=True)
        v = {"decidedAt": at, "at": at, "purge": list(purge)} if at else {"purge": list(purge)}
        (tmp / "sheets" / f"{name}.json").write_text(json.dumps({"decisions": {"RM_Nuna": v}}))
        return f"sheets/{name}.json"

    def keep(name, sha, at):
        via = sheet(name, at)
        ev = {"type": "ruling", "id": f"keep-{name}", "verdict": "keep", "by": "owner", "trust": "ruled", "at": at,
              "via": via, "target": {"row": "RM_Nuna", "column": "A", "shas": [sha]}, "said": "sheet"}
        L.append(ev)
        L._absorb([ev])
        return ev

    # 1 an older keep is in the game; his NEWER pick of B installs over it, carrying the mark
    keep("s1", A, T1)
    L.install(MOD, REL, A, ruling_id="keep-s1")
    git(tmp, "add", "-A"); git(tmp, "commit", "-qm", "base")
    base = git(tmp, "rev-parse", "HEAD")
    keep("s3", B, T3)
    r = L.install(MOD, REL, B, ruling_id="keep-s3")
    check(r["status"] == "installed" and L.sha256_file(dest) == B, "newest mark (pick) installs over an older keep")
    ev = [e for e in L.read_events() if e.get("type") == "live" and e.get("sha") == B][-1]
    check(ev.get("mark", {}).get("at") == T3 and ev.get("why") == L.MARKS_WHY, "the live event carries the mark and the delegated why")
    check(G.check([(path, A, B)], L.read_events()) == [], "guard accepts the newer-pick-over-older-keep transition")
    git(tmp, "add", "-A"); git(tmp, "commit", "-qm", "pick B")

    # 2 an OLDER pick never replaces a newer keep
    keep("s0", C, T0)
    why = refused(L.install, MOD, REL, C, ruling_id="keep-s0")
    check(why is not None and "NEWER" in why and L.sha256_file(dest) == B, "an older pick never beats a newer keep (install refuses)")
    forged = {"id": "forged", "type": "live", "mod": MOD, "rel": REL, "sha": C, "prev": B, "reason": "install",
              "ruling_id": "keep-s0", "ts": L.now(), "mark": L.mark_of_ruling(next(e for e in L.read_events() if e["id"] == "keep-s0")),
              "why": L.MARKS_WHY}
    check(G.check([(path, B, C)], L.read_events() + [forged]) != [], "guard refuses a hand-made older-mark transition over a newer keep")
    unmarked = {k: v for k, v in forged.items() if k not in ("mark", "why")}
    check(G.check([(path, B, C)], L.read_events() + [unmarked]) != [],
          "guard refuses the same older pick when the event simply omits its mark (judged from the ruling's stamp)")
    odd = {"id": "odd", "type": "ruling", "verdict": "keep", "by": "owner", "trust": "ruled", "at": "not-a-time",
           "ts": "also-not", "target": {"shas": [B]}}
    stub = type("Stub", (), {"protected": lambda self, sha: [odd]})()
    check([k["id"] for k in L.newer_keeps(stub, B, T5)] == ["odd"],
          "a keep whose time cannot be read counts as NEWER (an unreadable stamp never lets a mark win)")

    # 3 his X archives the in-game picture; no purge; restore returns identical bytes
    xs = sheet("sx", T5, [B])
    mark = {"sheet": "sx", "row": "RM_Nuna", "at": T5, "via": xs}
    r = L.archive(dest, mark=mark)
    check(r["status"] == "archived" and not dest.exists(), "X moves the in-game picture out of the game")
    check(L.store_has(B) and not L.cached_index().is_purged(B), "the bytes stay in the art store; nothing purged")
    check(G.check([(path, B, None)], L.read_events()) == [], "guard accepts the archive commit (range check shape)")
    git(tmp, "add", "-A"); git(tmp, "commit", "-qm", "X archive")
    bad = G.check_range(tmp, base, "HEAD")
    check(bad == [], f"guard range check passes for the pick and archive commits {bad[:1]}")
    check(not L.cached_index().protected(B), "the older keep on the archived picture is released")
    check(B in L.archived_shas() and refused(L.purge, B, owner_said="reject+purge on sheet sy", via=sheet("sy", T5, [B]),
                                             release_from_sheet=("sheets/sy.json", "RM_Nuna")) is not None
          and L.store_has(B), "a bare purge (another stamp) never deletes an archived picture (a newer ✕ goes through x_delete)")
    check(refused(L.restore, "sx", ) is not None, "restore refuses without his words")
    ar = [e for e in L.archive_events()][-1]
    rr = L.restore(ar["id"][:10], owner_said="put it back")
    check(rr["status"] == "restored" and L.sha256_file(dest) == B and dest.read_bytes() == png((0, 200, 0, 255)),
          "restore brings back identical bytes")
    check(G.check([(path, None, B)], L.read_events()) == [], "guard accepts the restore")

    # 4 an X older than a keep, an unstamped (agent) mark, a mark for another row: never qualify
    keep("s6", B, "2026-10-26T06:00:00-0700")
    check("NEWER" in (refused(L.archive, dest, mark={"sheet": "sx", "row": "RM_Nuna", "at": T5, "via": xs}) or ""),
          "an older X never archives a picture kept later")
    xa = sheet("sagent", None, [B])
    check(refused(L.archive, dest, mark={"sheet": "sagent", "row": "RM_Nuna", "at": "2026-10-26T09:00:00-0700", "via": xa}) is not None,
          "a mark with no owner click stamp (an agent's guess) is refused")
    check(refused(L.archive, dest, mark={"sheet": "sx", "row": "RM_Nuna", "at": "2026-10-26T09:00:00-0700", "via": xs}) is not None,
          "a mark time that is not on the row is refused")
    check(dest.is_file(), "nothing was removed by the refusals")

    # 5 digest
    d = L.marks_digest()
    check(len(d) == 3 and any("archived" in x for x in d) and any("restored" in x for x in d)
          and any("installed over an older keep" in x for x in d), "every act is a digest line (install, archive, restore)")
    print("ALL PASS" if not FAILS else f"{len(FAILS)} FAIL")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
