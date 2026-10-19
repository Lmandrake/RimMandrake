#!/usr/bin/env python3
"""art_accept_finished.py — install every FINISHED artpipe render that has a single safe destination over a donor
copy, StandIn/ stand-in, placeholder or missing texture, as an accepted-for-now install. Dry run by default.

Owner, 2026-10-18 (relayed by the FOUNDRY coordinator): "Yes. Simply accept all art as currently rendered to get
this done. We will re review at a later time. No more art blockers."  Every install here is provisional
(`accepted_for_now: true` in its provenance) and goes back on a sheet at his re-review.

    python3 src/RimMandrake/Utils/art/art_accept_finished.py                 # dry run: what would go in, what is refused
    python3 src/RimMandrake/Utils/art/art_accept_finished.py --apply         # install through the art ledger
            [--only <dest substring>] [--prefix dregen_] [--item <rimflow item id>]

Destinations and the replace rule are bulk_accept_renders.py's plan (install_to > target_texpath > target_def >
name-join; only DONOR / PLACEHOLDER / MISSING / StandIn-drawn files are replaced; FlowWorks never). What differs:
  * MECHANICAL ONLY. Each install is artledger.install(reason="script:<this file>"). Where the ledger refuses — an
    owner-KEPT picture, a rejected/redo sha, purged bytes — the row is REPORTED as needing his words and skipped.
    His typed words are never passed for him (the 16 FloodedCanyon keeps were released by his words on 2026-10-18;
    nothing else is).
  * A destination whose case-insensitive twin already sits in the folder is skipped (PaleTree_B / PaleTree_b,
    4c8371290: Windows cannot hold both).
  * After installs, a Graphic_Random folder drawn as StandIn/<folder> is pointed back at <folder> only once every
    StandIn picture of that folder has a render of ours beside it at <folder>.
Then rebuild the art sheets / deploy as usual; nothing is deployed here.
"""
from __future__ import annotations

import argparse
import json
import socket
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as A            # noqa: E402
import bulk_accept_renders as BA  # noqa: E402

REPO = BA.REPO
ART = BA.ART
OWNER_SAID = BA.OWNER_SAID
REASON = "script:src/RimMandrake/Utils/art/art_accept_finished.py accept-for-now (DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO)"


def case_twin(dest: str) -> bool:
    p = REPO / dest
    if not p.parent.is_dir():
        return False
    return any(q.name != p.name and q.name.lower() == p.name.lower() for q in p.parent.iterdir())


def job_item(job_id: str) -> str:
    f = ART / "done" / f"{job_id}.json"
    try:
        return json.loads(f.read_text()).get("rimflow_item_id") or ""
    except (OSError, ValueError):
        return ""


def standin_folder_repoints(installed: list[str]) -> list[dict]:
    """StandIn/<folder> texts whose every StandIn picture now has a counterpart at <folder> in the same mod."""
    repo = BA.Repo()
    out = []
    for text, xmls in repo.drawn.items():
        if not text.startswith("StandIn/"):
            continue
        orig = text.removeprefix("StandIn/")
        for m in repo.mods_with_dir(text):
            sd = REPO / m / "Textures" / text
            od = REPO / m / "Textures" / orig
            if not sd.is_dir():
                continue
            pics = [q.name for q in sd.glob("*.png") if not q.stem.endswith("_m")]
            if pics and all((od / n).is_file() for n in pics) and any(f"{m}/Textures/{orig}/" in d for d in installed):
                ed = [x for x in xmls if "/Defs/" in x and not any(x.startswith(n) for n in BA.NO_XML_EDIT)]
                out.append({"from": text, "to": orig, "xml": sorted(ed)})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="install (default: dry run)")
    ap.add_argument("--only", help="only destinations containing this substring")
    ap.add_argument("--item", help="only renders whose job carries this rimflow_item_id")
    ap.add_argument("--prefix", help="only renders whose job id starts with this (dregen_ = the donor regen queue)")
    ap.add_argument("--plan", type=Path, help="reuse a bulk_accept_renders plan instead of building one")
    a = ap.parse_args()

    if a.plan:
        plan_p = a.plan
    else:
        plan_p = Path(tempfile.mkdtemp(prefix="art_accept_")) / "plan.json"
        BA.plan(plan_p)
    P = json.loads(plan_p.read_text())
    idx = A.cached_index()
    log = {"installed": [], "would_install": [], "needs_his_words": [], "refused": [], "case_twin": [],
           "already": [], "repointed": [], "retired": []}
    for r in P["rows"]:
        d = r["dest"]
        if a.only and a.only not in d:
            continue
        if a.item and job_item(r["job"]) != a.item:
            continue
        if a.prefix and not r["job"].startswith(a.prefix):
            continue
        if case_twin(d):
            log["case_twin"].append(d)
            continue
        data = Path(r["png"]).read_bytes()
        sha = BA.sha_of(Path(r["png"]))
        mod, rel = A.locate(REPO / d)
        if not a.apply:
            old = REPO / d
            old_sha = A.sha256_file(old) if old.is_file() else None
            why = (("purged" if idx.is_purged(sha) or idx.was_purged(sha) else None)
                   or A.rejection_refusal(idx, rel, sha)
                   or ("owner-KEPT live picture" if old_sha and idx.protected(old_sha) else None))
            (log["needs_his_words"] if why else log["would_install"]).append(
                {"dest": d, "job": r["job"], **({"why": why} if why else {})})
            continue
        A.store_put_bytes(data)
        prov = {"kind": "artpipe", "job": r["job"], "accepted_for_now": True, "owner_said": OWNER_SAID,
                "relayed_by": "FOUNDRY coordinator", "via": "art_accept_finished.py"}
        try:
            res = A.install(mod, rel, sha, reason=REASON, provenance=prov)
        except A.Refused as e:
            msg = str(e)
            k = "needs_his_words" if any(w in msg for w in ("owner-KEPT", "REJECTED", "redo", "purged")) else "refused"
            log[k].append({"dest": d, "job": r["job"], "why": msg[:300]})
            continue
        if res.get("status") == "already-live":
            log["already"].append(d)
            continue
        log["installed"].append(d)
        rec = {"job_id": r["job"], "dest": d, "sha256": BA.sha_of(REPO / d), "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               "clone": str(REPO), "host": socket.gethostname(), "via": "art_accept_finished.py",
               "accepted_for_now": True, "owner_said": OWNER_SAID, "relayed_by": "FOUNDRY coordinator"}
        with (ART / "collected.jsonl").open("a") as fh:
            fh.write(json.dumps(rec) + "\n")

    if a.apply:
        done = set(log["installed"]) | set(log["already"])
        for x in P.get("retire", []):
            folder = x.rsplit("/", 1)[0]
            if (a.only and a.only not in x) or not any(d.startswith(folder + "/") for d in done):
                continue
            try:
                A.retire(REPO / x, reason=REASON)
                log["retired"].append(x)
            except A.Refused as e:
                log["refused"].append({"dest": x, "why": "retire: " + str(e)[:300]})
        for rp in P["repoint"]:
            if not any(d.startswith(rp["mod"] + "/") for d in done):
                continue                       # only repoint where a render of ours actually went in
            for x in rp["xml"]:
                p = REPO / x
                t = p.read_text(encoding="utf-8")
                n = BA.repoint_text(t, rp)
                if n != t:
                    p.write_text(n, encoding="utf-8")
                    log["repointed"].append(x)
        for rp in standin_folder_repoints(log["installed"]):
            for x in rp["xml"]:
                p = REPO / x
                t = p.read_text(encoding="utf-8")
                n = t.replace(f">{rp['from']}<", f">{rp['to']}<")
                if n != t:
                    p.write_text(n, encoding="utf-8")
                    log["repointed"].append(x)

    print(("APPLIED " if a.apply else "DRY RUN ") + json.dumps({k: len(v) for k, v in log.items()}))
    out = plan_p.with_suffix(".accept_finished." + ("applied" if a.apply else "dry") + ".json")
    out.write_text(json.dumps(log, indent=1))
    print("log:", out)
    if log["needs_his_words"]:
        print(f"{len(log['needs_his_words'])} destination(s) need his words (owner keep / rejection / purge): see the log")
    if a.apply and (log["installed"] or log["repointed"]):
        print("next: commit the touched Textures/ + Defs/ paths by name, and the art ledger shard; deploy as usual")


if __name__ == "__main__":
    main()
