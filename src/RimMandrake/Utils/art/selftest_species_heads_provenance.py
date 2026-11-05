#!/usr/bin/env python3
"""selftest_species_heads_provenance.py — species_heads_provenance.py on a fake repo + fake workshop.

Proves: only sha-identical copies are claimed (an edited copy at the donor's own path stays unmatched); a missing
donor mod makes the manifest blind, never empty-and-clean; check() fails on changed bytes, a missing probe, a probe the
gate does not call DONOR, and an UNCONFIRMED row; the donor events carry kind=donor and a non-mandrake donor_pkg, which
is what regen_eligibility's donor rule reads; and the real Gate.judge_bytes calls those bytes DONOR once the events exist.
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import species_heads_provenance as S  # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def png(seed: int) -> bytes:
    from PIL import Image
    im = Image.new("RGBA", (8, 8), (seed % 256, (seed * 7) % 256, 40, 255))
    im.putpixel((seed % 8, 3), (0, 0, 0, 0))
    b = io.BytesIO(); im.save(b, "PNG")
    return b.getvalue()


def put(p: Path, b: bytes):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b)


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        repo, ws = t / "repo", t / "ws"
        ours = repo / S.OURS
        orw, swx = ws / S.DONORS["OR"][0], ws / S.DONORS["SWX"][0]
        (orw / "About").mkdir(parents=True)
        (swx / "About").mkdir(parents=True)
        probe_bytes = {}
        for i, pr in enumerate(S.PROBES):
            b = png(i + 1)
            probe_bytes[pr] = b
            put(ours / pr, b)
            put(orw / "Common_Old" / "Textures" / pr.split("/", 1)[1], b)
        put(ours / "SWX/Pawn/HeadAttachments/x/eye.png", png(50))
        put(swx / "Textures/Pawn/HeadAttachments/x/eye.png", png(51))           # edited copy: same path, other bytes
        put(ours / "SWX/Pawn/HeadType/ours/Head_south.png", png(60))            # ours alone
        put(ours / "SWX/Pawn/moved/Moved_south.png", png(70))
        put(swx / "1.5/Textures/Pawn/elsewhere/Moved_south.png", png(70))       # identical bytes, other path
        m = S.build_manifest(repo, ws)
        rows = {r["ours"]: r for r in m["rows"]}
        un = {u["ours"]: u for u in m["unmatched"]}
        ok(not m["blind"], "both donors seen")
        ok(all(p in rows for p in S.PROBES), "all 8 probes matched to Outer Rim")
        ok(rows[S.PROBES[0]]["donor_pkg"] == "neronix17.outerrim.galacticdiversity", "probe donor is Outer Rim")
        ok("SWX/Pawn/HeadAttachments/x/eye.png" in un and un["SWX/Pawn/HeadAttachments/x/eye.png"]["donor_same_path_differs"],
           "edited copy at the donor's path is NOT claimed")
        ok("SWX/Pawn/HeadType/ours/Head_south.png" in un, "our own art is not claimed")
        ok(rows.get("SWX/Pawn/moved/Moved_south.png", {}).get("donor_pkg") == "guy762.starwarsxenotypes",
           "identical bytes at another donor path still count")
        mpath = t / "m.json"
        S.write_manifest(m, mpath)
        m2 = S.load_manifest(mpath)
        ok(m2["rows"] == m["rows"] and m2["unmatched"] == m["unmatched"], "manifest round-trips")

        import shutil
        shutil.rmtree(swx)
        ok(any("UNMEASURED" in b for b in S.build_manifest(repo, ws)["blind"]), "absent donor is blind, not clean")

        donor = lambda b, w: ("DONOR", "x")                                     # noqa: E731
        ok(S.check(m, repo, donor) == [], "check passes when the gate says DONOR")
        ok(S.check(m, repo, lambda b, w: ("REFUSED_UNCONFIRMED", "x")), "check fails on UNCONFIRMED")
        ok(S.check(m, repo, lambda b, w: ("REFUSED_REGEN", "x")), "a probe must be DONOR, not merely known")
        nonprobe = lambda b, w: ("REFUSED_REGEN", "x") if w not in S.PROBES else ("DONOR", "x")  # noqa: E731
        ok(S.check(m, repo, nonprobe) == [], "a non-probe row in a known state passes")
        mm = dict(m, rows=[r for r in m["rows"] if r["ours"] != S.PROBES[3]])
        ok(any("probe" in f for f in S.check(mm, repo, donor)), "check fails on a missing probe")
        put(ours / S.PROBES[2], png(99))
        ok(any("changed" in f for f in S.check(m, repo, donor)), "check fails on changed bytes")
        put(ours / S.PROBES[2], probe_bytes[S.PROBES[2]])
        ok(S.check(dict(m, blind=["x"]), repo, donor), "a blind manifest never passes")

        evs = S.donor_events(m)
        ok(len(evs) == len(m["rows"]) and all(e["kind"] == "donor" and not e["donor_pkg"].startswith("mandrake.")
                                              for e in evs), "events are kind=donor, foreign package")
        ok(len({e["id"] for e in evs}) == len({(e["sha"], e["loc"]) for e in evs}), "event ids are deterministic per sha+loc")

        # the real gate's byte rule, on a fake repo and an in-memory ledger holding those events
        import artledger as L
        from regen_eligibility import Gate
        (repo / "src").mkdir(exist_ok=True)
        g = Gate(repo=repo, idx=L.Index(events=evs), game_classify=lambda r: {}, game_file=lambda r: [],
                 placeholder_reason=lambda b: None, allowlist={"entries": []})
        ok(g.judge_bytes(probe_bytes[S.PROBES[0]], "p")[0] == "DONOR", "real gate: probe bytes are DONOR with the events")
        g0 = Gate(repo=repo, idx=L.Index(events=[]), game_classify=lambda r: {}, game_file=lambda r: [],
                  placeholder_reason=lambda b: None, allowlist={"entries": []})
        ok(g0.judge_bytes(probe_bytes[S.PROBES[0]], "p")[0] == "REFUSED_UNCONFIRMED",
           "real gate: same bytes UNCONFIRMED without them")
    print("PASS" if not FAILS else f"FAIL ({len(FAILS)})")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
