#!/usr/bin/env python3
"""selftest_regen_eligibility.py — the dregen_ eligibility gate (regen_eligibility.py; owner 2026-10-19: "I ONLY want
art queued that has either confirmed NONE, PLACEHOLDER, or DONOR art. If you can't confirm one of those three, do not
queue. If it was previously regenerated and renamed, do not queue.").

A fake repo in scratch + a synthetic art ledger + stub game-texture lookups. Covers each class (NONE, PLACEHOLDER,
DONOR by ledger, DONOR by census, KEPT, REGEN by hash, unknown bytes), the renamed cases (def repointed to a render of
ours, case twin, render registered at the path before, a finished render bound to the def+path), a mandrake-packaged
"donor" variant that is NOT donor, the stand-in ruling that is not a keep, and fail-closed (the gate cannot be built
-> submit files nothing; a row that errors is refused).
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as A  # noqa: E402
import regen_eligibility as RE  # noqa: E402

FAILS = []


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:600]}]"))
    if not cond:
        FAILS.append(msg)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


B = {k: f"{k}-bytes".encode() for k in ("donor", "donorown", "kept", "regen", "unknown", "standin", "twin", "newregen")}
B["ph"] = b"PH-geometric"
M = "src/RimMandrake/Fake"

DEFS = """<Defs>
 <ThingDef><defName>RM_None</defName><graphicData><texPath>Things/RM_None/RM_None</texPath></graphicData></ThingDef>
 <ThingDef><defName>RM_Ph</defName><graphicData><texPath>Things/RM_Ph</texPath></graphicData></ThingDef>
 <ThingDef><defName>RM_Donor</defName><graphicData><texPath>Things/RM_Donor</texPath></graphicData></ThingDef>
 <ThingDef><defName>RM_DonorOwn</defName><graphicData><texPath>Things/RM_DonorOwn</texPath></graphicData></ThingDef>
 <ThingDef><defName>RM_Kept</defName><graphicData><texPath>Things/RM_Kept</texPath></graphicData></ThingDef>
 <ThingDef><defName>RM_Regen</defName><graphicData><texPath>Things/RM_Regen</texPath></graphicData></ThingDef>
 <ThingDef><defName>RM_Unknown</defName><graphicData><texPath>Things/RM_Unknown</texPath></graphicData></ThingDef>
 <ThingDef><defName>RM_Standin</defName><graphicData><texPath>StandIn/Things/RM_Standin</texPath></graphicData></ThingDef>
 <ThingDef><defName>RM_Twin</defName><graphicData><texPath>Things/RM_Twin</texPath></graphicData></ThingDef>
 <ThingDef><defName>RM_Leather</defName><graphicData><texPath>Things/Item/Resource/Leather</texPath></graphicData></ThingDef>
 <ThingDef><defName>RM_Moved</defName><graphicData><texPath>Things/RM_Moved_new/RM_Moved_new</texPath></graphicData></ThingDef>
 <ThingDef><defName>RM_Repointed</defName><graphicData><texPath>Things/Item/RM_Repointed/RM_Repointed</texPath></graphicData></ThingDef>
 <ThingDef><defName>RM_Was</defName><graphicData><texPath>Things/RM_Was</texPath></graphicData></ThingDef>
 <ThingDef><defName>RM_Bound</defName><graphicData><texPath>Things/Item/Cloth</texPath></graphicData></ThingDef>
 <ThingDef><defName>RM_Err</defName><graphicData><texPath>Things/Item/Err</texPath></graphicData></ThingDef>
</Defs>"""


def build_repo() -> Path:
    root = Path(tempfile.mkdtemp(prefix="regen_elig_"))
    (root / M / "Defs").mkdir(parents=True)
    (root / M / "Defs" / "d.xml").write_text(DEFS)
    tex = root / M / "Textures"
    files = {"Things/RM_Ph": "ph", "Things/RM_Donor": "donor", "Things/RM_DonorOwn": "donorown",
             "Things/RM_Kept": "kept", "Things/RM_Regen": "regen", "Things/RM_Unknown": "unknown",
             "StandIn/Things/RM_Standin": "standin", "Things/rm_twin": "twin",
             "Things/RM_Moved_new/RM_Moved_new": "newregen", "Things/Item/RM_Repointed/RM_Repointed": "newregen"}
    for rel, k in files.items():
        p = tex / (rel + ".png")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(B[k])
    return root


def var(i, s, **kw):
    return dict({"type": "variant", "id": f"v{i}", "sha": s, "ts": "2026-10-18T00:00:00-0700"}, **kw)


def events():
    return [
        var(1, sha(B["donor"]), kind="donor", donor_pkg="sarg.alphabiomes"),
        var(2, sha(B["donorown"]), kind="donor", donor_pkg="mandrake.rm.biomes"),     # our own deployed mod: NOT donor
        var(3, sha(B["kept"]), kind="donor", donor_pkg="sarg.alphabiomes"),
        {"type": "ruling", "id": "r1", "verdict": "keep", "by": "owner", "trust": "ruled",
         "target": {"sha": sha(B["kept"])}, "said": "", "via": "x_sheet.decisions.json"},
        var(4, sha(B["regen"]), kind="artpipe", job="dregen_RM_Regen_v1"),
        var(5, sha(B["standin"]), kind="donor", provenance={"kind": "donor", "standin": True}),
        {"type": "ruling", "id": "r2", "verdict": "keep", "by": "owner", "trust": "ruled",
         "target": {"sha": sha(B["standin"])}, "via": "art install (owner words)",
         "said": "Just put in placeholder art for now or donor copies and retire these mods!!! Just get it done."},
        var(6, sha(B["twin"]), kind="install", provenance={"accepted_for_now": True}),
        var(7, sha(B["newregen"]), kind="artpipe", job="dregen_RM_Moved_v1"),
        var(8, "f" * 64, kind="artpipe", job="texregen_RM_Was_v1", res="Things/RM_Was"),
        var(9, "e" * 64, kind="artpipe", job="dregen_RM_Bound_v1"),
        {"type": "binding", "id": "b1", "sha": "e" * 64, "subject": "RM_Bound", "texpath": "Things/Item/RM_Bound/RM_Bound",
         "job": "dregen_RM_Bound_v1"},
    ]


def game_classify(res):
    if res.startswith("Things/Item/Resource/Leather"):
        return {"cat": "VANILLA", "by": "ludeon.rimworld"}
    if res == "Things/Item/Err":
        raise RuntimeError("index blind")
    return {"cat": "MISSING", "by": None}


def gate(root, **kw):
    a = dict(repo=root, idx=A.Index(events()), game_classify=game_classify, game_file=lambda res: [],
             placeholder_reason=lambda b: "geometric circle" if bytes(b).startswith(b"PH") else None,
             allowlist={"entries": []})
    a.update(kw)
    return RE.Gate(**a)


def row(dn, **kw):
    return dict({"id": f"dregen_{dn}_v1", "target_def": dn, "facings": []}, **kw)


def it(rel):
    return f"{M}/Textures/{rel}.png"


def main() -> int:
    root = build_repo()
    g = gate(root)
    cases = [
        ("NONE: nothing anywhere for a path a def draws", row("RM_None", install_to=it("Things/RM_None/RM_None")), "NONE"),
        ("PLACEHOLDER: geometric bytes", row("RM_Ph", install_to=it("Things/RM_Ph")), "PLACEHOLDER"),
        ("DONOR: ledger donor variant from a donor package", row("RM_Donor", install_to=it("Things/RM_Donor")), "DONOR"),
        ("DONOR: a StandIn/ copy with standin provenance; the stand-in ruling is not a keep",
         row("RM_Standin", install_to=it("Things/RM_Standin")), "DONOR"),
        ("DONOR: vanilla serves the path (census)", row("RM_Leather", target_texpath="Things/Item/Resource/Leather"), "DONOR"),
        ("refused: 'donor' variant recorded from our own mandrake.* deployed mod is NOT donor",
         row("RM_DonorOwn", install_to=it("Things/RM_DonorOwn")), "REFUSED_UNCONFIRMED"),
        ("refused KEPT: owner keep on donor bytes", row("RM_Kept", install_to=it("Things/RM_Kept")), "REFUSED_KEPT"),
        ("refused REGEN: bytes are an artpipe render (hash)", row("RM_Regen", install_to=it("Things/RM_Regen")), "REFUSED_REGEN"),
        ("refused UNCONFIRMED: bytes of unknown provenance", row("RM_Unknown", install_to=it("Things/RM_Unknown")),
         "REFUSED_UNCONFIRMED"),
        ("renamed: case twin holds an accepted render", row("RM_Twin", install_to=it("Things/RM_Twin")), "REFUSED_REGEN"),
        ("renamed: install_to no def draws any more; def now draws a render of ours",
         row("RM_Moved", install_to=it("Things/RM_Moved_old")), "REFUSED_REGEN"),
        ("renamed: external job whose def was repointed to a render of ours",
         row("RM_Repointed", target_texpath="Things/Item/Repointable"), "REFUSED_REGEN"),
        ("renamed: file gone but a render was registered at the path", row("RM_Was", install_to=it("Things/RM_Was")),
         "REFUSED_REGEN"),
        ("regenerated: a finished render is bound to the def's own path (awaiting install)",
         row("RM_Bound", target_texpath="Things/Item/Cloth"), "REFUSED_REGEN"),
        ("renamed/removed def: target_def gone from our XML", row("RM_Gone", install_to=it("Things/RM_Gone")),
         "REFUSED_UNCONFIRMED"),
        ("fail closed per row: a classifier error refuses the row", row("RM_Err", target_texpath="Things/Item/Err"),
         "REFUSED_UNCONFIRMED"),
        ("a row naming no destination is refused", row("RM_None"), "REFUSED_UNCONFIRMED"),
    ]
    for msg, r, want in cases:
        v = g.classify(r)
        check(v["verdict"] == want and v["eligible"] == (want in RE.ELIGIBLE), msg, v)
    # facings: every facing must be confirmed; one regenerated facing refuses the row
    (root / M / "Textures/Things/RM_Fac").mkdir(parents=True)
    (root / M / "Textures/Things/RM_Fac/RM_Fac_east.png").write_bytes(B["donor"])
    (root / M / "Textures/Things/RM_Fac/RM_Fac_south.png").write_bytes(B["regen"])
    (root / M / "Defs" / "e.xml").write_text("<Defs><ThingDef><defName>RM_Fac</defName><graphicData>"
                                             "<texPath>Things/RM_Fac/RM_Fac</texPath></graphicData></ThingDef></Defs>")
    g2 = gate(root)
    v = g2.classify(row("RM_Fac", install_to=it("Things/RM_Fac/RM_Fac_{facing}"), facings=["east", "south"]))
    check(v["verdict"] == "REFUSED_REGEN" and not v["eligible"], "one regenerated facing refuses the whole row", v)
    v = g2.classify(row("RM_Fac", install_to=it("Things/RM_Fac/RM_Fac_east"), facing="east"))
    check(v["verdict"] == "DONOR", "a per-facing job file is judged on its own facing", v)

    # fail closed: the gate cannot be built -> GateError, and submit files nothing
    class Blind:
        @property
        def variants(self):
            raise OSError("ledger unreadable")
    try:
        gate(root, idx=Blind())
        check(False, "a gate whose ledger is unreadable raises GateError")
    except RE.GateError:
        check(True, "a gate whose ledger is unreadable raises GateError")
    import donor_regen_jobs as DJ
    calls = []
    orig_gate, orig_run, orig_if = DJ.RE.Gate, DJ.subprocess.run, DJ.in_flight

    def boom(*a, **k):
        raise RE.GateError("synthetic")
    jf = root / "jobs.json"
    jf.write_text(json.dumps({"rows": [row("RM_None", install_to=it("Things/RM_None/RM_None"))]}))
    try:
        DJ.RE.Gate = boom
        DJ.subprocess.run = lambda *a, **k: calls.append(a)
        DJ.in_flight = lambda: 0
        rc = DJ.submit([jf], 40, True)
        check(rc == 2 and not calls, "submit with a broken gate exits 2 and calls fill_queue zero times", (rc, calls))
        # a working gate that refuses every row: submit files nothing
        DJ.RE.Gate = orig_gate
        jf.write_text(json.dumps({"rows": [row("RM_Regen", install_to=it("Things/RM_Regen"))]}))
        orig_qv = DJ.queue_view
        DJ.queue_view = lambda: ({}, set())
        rc = DJ.submit([jf], 40, True, gate=g, journal=lambda: 0, requeue_pool=False)
        check(not calls, "submit never files a refused row", calls)
        DJ.queue_view = orig_qv
    finally:
        DJ.RE.Gate, DJ.subprocess.run, DJ.in_flight = orig_gate, orig_run, orig_if
    # requeue: 429-failed + gate-eligible only, batch cap, room cap, backoff, fail closed
    art = Path(tempfile.mkdtemp(prefix="regen_art_"))
    for d in ("pending", "active", "failed"):
        (art / d).mkdir()

    def fail(dn, cause="ERROR: exceeded retry limit, last status: 429 Too Many Requests", **kw):
        j = row(dn, install_to=it(f"Things/{dn}"), **kw)
        (art / "failed" / (j["id"] + ".json")).write_text(json.dumps(j))
        (art / "failed" / (j["id"] + ".manifest.json")).write_text(json.dumps({"worker_stderr_tail": cause}))
        return j["id"]
    for i in range(12):
        fail("RM_Donor")                                   # same id rewritten: one file; vary below
    ids = []
    for i in range(12):
        j = row("RM_Donor", id=f"dregen_RM_Donor_n{i}_v1", install_to=it("Things/RM_Donor"))
        (art / "failed" / (j["id"] + ".json")).write_text(json.dumps(j))
        (art / "failed" / (j["id"] + ".manifest.json")).write_text(json.dumps({"worker_stderr_tail": "HTTP 429"}))
        ids.append(j["id"])
    kept = fail("RM_Kept")
    regen = fail("RM_Regen")
    other = fail("RM_Donor", cause="derivation impossible", id="dregen_RM_Donor_other_v1")
    g2 = gate(root)
    pool = DJ.eligible_failed(art, g2)
    pid = {j["id"] for j, _ in pool}
    check(kept not in pid and regen not in pid, "requeue pool excludes KEPT and regenerated jobs", pid)
    check("dregen_RM_Donor_other_v1" not in pid, "requeue pool excludes non-429 failures")
    check(len(pool) == 13, "requeue pool = the 429 + gate-eligible jobs", len(pool))
    check(DJ.requeue(art, 40, 10, True, g2, journal=lambda: 0) == 0 and len(list((art / "pending").iterdir())) == 0,
          "requeue dry run moves nothing")
    DJ.requeue(art, 40, 10, False, g2, journal=lambda: 0)
    npend = len([f for f in (art / "pending").iterdir()])
    check(npend == 10, "requeue moves at most 10 per run", npend)
    check(not [f for f in (art / "failed").iterdir() if f.name.startswith(sorted(pid)[0]) and f.exists()
               and (art / "pending" / (f.name)).exists()], "moved job left failed/")
    DJ.requeue(art, 40, 10, False, g2, journal=lambda: 3)
    check(len(list((art / "pending").iterdir())) == 10, "a 429 in the journal files nothing (backing off)")
    DJ.requeue(art, 12, 10, False, g2, journal=lambda: 0)
    check(len(list((art / "pending").iterdir())) == 12, "requeue honours the cap on pending+active",
          len(list((art / "pending").iterdir())))

    def unreadable():
        raise OSError("no journal")
    DJ.requeue(art, 99, 10, False, g2, journal=unreadable)
    check(len(list((art / "pending").iterdir())) == 12, "an unreadable journal backs off (fail closed)")

    def boom2(*a, **k):
        raise RE.GateError("synthetic")
    orig_g2 = DJ.RE.Gate
    DJ.RE.Gate = boom2
    try:
        rc = DJ.requeue(art, 99, 10, False, None, journal=lambda: 0)
    finally:
        DJ.RE.Gate = orig_g2
    check(rc == 2 and len(list((art / "pending").iterdir())) == 12, "requeue with a broken gate files nothing")
    DJ.in_flight = lambda: 0
    print(f"\n{'FAILED' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
