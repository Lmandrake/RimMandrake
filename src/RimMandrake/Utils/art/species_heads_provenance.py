#!/usr/bin/env python3
"""species_heads_provenance.py — record, and prove, where the RimMandrakeSW/OR and /SWX textures came from
(SPECIES_HEADS_AUDIT_PROVENANCE_BEFORE_REDRAW).

StarWarsRaces carries copies of two donor mods' art under Textures/RimMandrakeSW/<tag>/:
  OR   Outer Rim - Galactic Diversity   Neronix17.OuterRim.GalacticDiversity   workshop 2980427615
  SWX  Star Wars Xenotypes              guy762.StarWarsXenotypes               workshop 2915192253
The art ledger never recorded that, so the regen eligibility gate (regen_eligibility.py) refused every species head
REFUSED_UNCONFIRMED. A copy is DONOR only when its bytes are IDENTICAL (sha256) to a file in that donor mod; an edited
copy matches nothing and stays unconfirmed (listed under "unmatched", never guessed).

    record [--apply]   hash every PNG under our OR/SWX trees against the donor trees on disk; write the manifest
                       (species_heads_provenance.json, beside this file) and, with --apply, one kind=donor variant event
                       per matched sha into the art ledger (idempotent: deterministic ids). Needs the Steam workshop.
    check              offline: every manifest row's repo bytes still hash to its sha, and the eligibility gate itself
                       (Gate.judge_bytes, game index stubbed out: it judges bytes from the ledger alone) calls each
                       matched sha DONOR or a stronger known state (REFUSED_REGEN / REFUSED_KEPT / PLACEHOLDER), never
                       REFUSED_UNCONFIRMED; the 8 probe textures of 2026-10-26 must be matched and DONOR. Exit 0/1.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
REPO = HERE.parents[3]
OURS = "src/RimStarWars/StarWarsRaces/Textures/RimMandrakeSW"
MANIFEST = HERE / "species_heads_provenance.json"
WORKSHOP = Path(os.environ.get("RM_WORKSHOP_ROOT")
                or "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100")
DONORS = {"OR": ("2980427615", "neronix17.outerrim.galacticdiversity", "Outer Rim - Galactic Diversity"),
          "SWX": ("2915192253", "guy762.starwarsxenotypes", "Star Wars Xenotypes")}
# the probe of 2026-10-26 (/mnt/d/ClaudeWork/rimmandrake/xenotype_canon/elig_probe.txt): all eight REFUSED_UNCONFIRMED
PROBES = [
    "OR/Things/Pawn/Humanlike/Heads/Togruta/Male_Togruta0_south.png",
    "OR/Things/Pawn/Humanlike/Heads/Twilek/Male_Normal_south.png",
    "OR/Things/Pawn/Humanlike/Heads/Duros/Male_Normal_south.png",
    "OR/Things/Pawn/Humanlike/Heads/Bothan/Male_Bothan_south.png",
    "OR/Things/Pawn/Humanlike/Heads/Gungan/Male_Normal_south.png",
    "OR/Things/Pawn/Humanlike/Heads/Herglic/Herglic_south.png",
    "OR/Things/Pawn/Humanlike/Heads/Dathomirian/Male_Dathomirian0_south.png",
    "OR/OuterRim/Genes/Headbone/Montrals_south.png",
]
OK_STATES = {"DONOR", "REFUSED_REGEN", "REFUSED_KEPT", "PLACEHOLDER"}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def donor_index(donor_dir: Path) -> tuple[dict, dict]:
    """-> ({sha: [donor path]}, {rel-under-Textures lowercased: [donor path]}) over every Textures/ in the mod."""
    by_sha, by_rel = {}, {}
    for p in donor_dir.rglob("*.png"):
        s = p.as_posix()
        if "/Textures/" not in s:
            continue
        rel = s.split("/Textures/", 1)[1].lower()
        by_sha.setdefault(sha256(p), []).append(s)
        by_rel.setdefault(rel, []).append(s)
    return by_sha, by_rel


def build_manifest(repo: Path = REPO, workshop: Path = WORKSHOP) -> dict:
    rows, unmatched, blind = [], [], []
    for tag, (wid, pkg, name) in DONORS.items():
        ddir = workshop / wid
        ours = repo / OURS / tag
        if not (ddir / "About").is_dir():
            blind.append(f"{ddir} absent: {tag} UNMEASURED")
            continue
        by_sha, by_rel = donor_index(ddir)
        for p in sorted(ours.rglob("*.png")):
            rel = p.relative_to(repo / OURS).as_posix()
            s = sha256(p)
            hits = by_sha.get(s)
            if not hits:
                same_rel = by_rel.get(p.relative_to(ours).as_posix().lower(), [])
                unmatched.append({"ours": rel, "sha": s, "donor_same_path_differs": bool(same_rel)})
                continue
            want = p.relative_to(ours).as_posix().lower()
            hits = sorted(hits, key=lambda h: (not h.lower().endswith("/textures/" + want), h))
            rows.append({"ours": rel, "sha": s, "donor_pkg": pkg, "donor_mod": name, "donor_loc": hits[0]})
    return {"ours_root": OURS, "donors": {t: {"workshop_id": w, "packageId": p, "name": n}
                                          for t, (w, p, n) in DONORS.items()},
            "rows": rows, "unmatched": unmatched, "blind": blind}


def write_manifest(m: dict, path: Path = MANIFEST):
    head = {k: v for k, v in m.items() if k not in ("rows", "unmatched")}
    lines = ["{", f' "head": {json.dumps(head, sort_keys=True)},', ' "rows": [']
    lines += [("  " + json.dumps(r, sort_keys=True) + ",") for r in m["rows"]]
    if m["rows"]:
        lines[-1] = lines[-1][:-1]
    lines += [" ],", ' "unmatched": [']
    lines += [("  " + json.dumps(r, sort_keys=True) + ",") for r in m["unmatched"]]
    if m["unmatched"]:
        lines[-1] = lines[-1][:-1]
    lines += [" ]", "}"]
    path.write_text("\n".join(lines) + "\n")


def load_manifest(path: Path = MANIFEST) -> dict:
    d = json.loads(path.read_text())
    return dict(d["head"], rows=d["rows"], unmatched=d["unmatched"])


def donor_events(m: dict) -> list[dict]:
    """One kind=donor variant per manifest row — the fields backfill.py's loose-donor step writes."""
    import artledger as L
    evs = []
    for r in m["rows"]:
        pt = L.parse_texfile(r["ours"].split("/", 1)[1])
        evs.append({"type": "variant", "id": L.det_id("variant", "donor", r["sha"], "loose:" + r["donor_loc"]),
                    "sha": r["sha"], "kind": "donor", "how": "loose", "loc": "loose:" + r["donor_loc"],
                    "donor_pkg": r["donor_pkg"], "donor_mod": r["donor_mod"], "date": "",
                    "res": pt["res"], "facing": pt["facing"], "mask": pt["mask"],
                    "bound_by": f"sha256-identical to {r['donor_mod']} copy; ours at {OURS}/{r['ours']}",
                    "item": "SPECIES_HEADS_AUDIT_PROVENANCE_BEFORE_REDRAW"})
    return evs


def check(m: dict, repo: Path, judge) -> list[str]:
    """-> failures (empty = proven). judge(bytes, where) -> (verdict, why): the eligibility gate's own rule."""
    bad = []
    if m.get("blind"):
        bad += [f"manifest was built blind: {b}" for b in m["blind"]]
    rows = {r["ours"]: r for r in m["rows"]}
    for pr in PROBES:
        if pr not in rows:
            bad.append(f"probe {pr}: not matched to a donor in the manifest")
    for rel, r in rows.items():
        p = repo / m.get("ours_root", OURS) / rel
        if not p.is_file():
            bad.append(f"{rel}: missing from the repo")
            continue
        b = p.read_bytes()
        if hashlib.sha256(b).hexdigest() != r["sha"]:
            bad.append(f"{rel}: repo bytes changed since the manifest (sha {r['sha'][:12]})")
            continue
        v, why = judge(b, rel)
        if rel in PROBES and v != "DONOR":
            bad.append(f"probe {rel}: gate says {v} ({why})")
        elif v not in OK_STATES:
            bad.append(f"{rel}: gate says {v} ({why})")
    return bad


def real_judge():
    from regen_eligibility import Gate
    g = Gate(game_classify=lambda res: {}, game_file=lambda res: [])   # bytes are judged from the ledger alone
    return g.judge_bytes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("record"); p.add_argument("--apply", action="store_true")
    sp.add_parser("check")
    a = ap.parse_args(argv)
    if a.cmd == "record":
        m = build_manifest()
        if m["blind"]:
            print("UNMEASURED: " + "; ".join(m["blind"]))
            return 2
        write_manifest(m)
        print(f"manifest {MANIFEST.relative_to(REPO)}: {len(m['rows'])} donor-identical, "
              f"{len(m['unmatched'])} unmatched ({sum(u['donor_same_path_differs'] for u in m['unmatched'])} "
              f"differ from the donor file at the same path)")
        if a.apply:
            import artledger as L
            w = L.Writer()
            for ev in donor_events(m):
                w.add(ev)
            n = len(w.buf)
            for r in m["rows"]:
                L.store_put_file(REPO / OURS / r["ours"])
            w.flush()
            print(f"art ledger: {n} new donor variant event(s) in {L.shard_path().relative_to(REPO)}")
        return 0
    m = load_manifest()
    bad = check(m, REPO, real_judge())
    for b in bad[:40]:
        print("FAIL", b)
    print(f"{'PASS' if not bad else 'FAIL'}: {len(m['rows'])} donor-identical rows, {len(PROBES)} probes, "
          f"{len(bad)} failure(s), {len(m['unmatched'])} unmatched (not claimed)")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
