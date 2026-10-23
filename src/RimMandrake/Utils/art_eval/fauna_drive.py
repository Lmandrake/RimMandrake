#!/usr/bin/env python3
"""Drive the art-eval regen loop for live fauna: rows -> artpipe jobs, finished jobs -> candidate specs -> install.

    python3 fauna_drive.py rows <run-id>... --out rows.json [--file]     # regen_jobs.json -> fill_queue rows
    python3 fauna_drive.py candidates <DEF>... --round N --out <dir>      # done arteval_<DEF>_rN_* renders -> specs
    python3 fauna_drive.py install <DEF> --round N --run <run-id>         # accepted candidate -> art.py install

Why `rows` rewrites the prompt: the regen prompt edit speaks about every facing at once ("the rear view shows ...",
"all facings"), but each artpipe job draws exactly ONE facing and the daemon stamps that facing's view direction
(common._refuse_contradicted_facing refuses the contradiction). So the prompt is rewritten facing-neutral — the visual
spec only, no view words — by a sonnet call, checked mechanically (no view words may remain; else sentences naming a
view are dropped), and the canvas follows the shipping rule (smallest power of two >= adult drawSize x 128, min 256).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import runner as R  # noqa: E402
import cards as C  # noqa: E402
import policy as P  # noqa: E402

ROOT = C.ROOT
P_KEPT_CARD = P.KEPT_ART_CARD
VIEWWORDS = re.compile(r"\b(facings?|views?|profile|front|rear|side|north|south|east|west|top-down|overhead|"
                       r"from behind|toward the viewer|camera)\b", re.I)


def canvas_for(draw: float) -> int:
    need = draw * 128
    c = 256
    while c < need and c < 1024:
        c *= 2
    return c


def neutral_prompt(prompt: str) -> tuple[str, str]:
    if not VIEWWORDS.search(prompt):
        return prompt, "unchanged"
    ask = ("Rewrite this image-generation prompt so it describes ONLY what the single creature looks like (body, "
           "colours, materials, markings, anatomy, expression, pose, style). Delete every word about camera, view, "
           "facing, side, front, rear, profile, top, direction, or which way anything points; where a sentence says what "
           "a feature looks like from some angle, keep the feature and drop the angle. Keep it positively phrased, "
           "keep the painterly realistic style and transparent background sentence, one paragraph. Return only the "
           "new prompt.\n\n" + prompt)
    text, meta = R.call_claude(ask, R.storage_root(), "sonnet", timeout=200, tools="")
    text = text.strip().strip('"')
    if text and not VIEWWORDS.search(text):
        return text, "sonnet"
    sents = re.split(r"(?<=[.!?])\s+", prompt)
    kept = [s for s in sents if not VIEWWORDS.search(s)]
    return " ".join(kept), "sentence-drop"


def cmd_rows(a):
    rows = []
    for rid in a.runs:
        rows += json.loads((ROOT / f"infrastructure/state/art_eval/runs/{rid}/regen_jobs.json").read_text())
    specs = {}
    for p in Path(a.specs).glob("**/*.spec.json"):
        s = json.loads(p.read_text())
        specs[s["subject"]] = s

    nreg = {}
    for f in (ROOT / "infrastructure/state/art_eval/runs").glob("fauna_*/decisions.jsonl"):
        for line in f.read_text().splitlines():
            d = json.loads(line)
            if d["decision"] == "REGEN":
                nreg[d["subject"]] = nreg.get(d["subject"], 0) + 1

    def fix(r):
        # the round is the number of REGEN verdicts on the subject, counted from the decision logs (the shared
        # regen_rounds.json lost updates under parallel runs); a subject's own two first-pass rows count once
        r["id"] = f"arteval_{r['target_def']}_r{min(nreg.get(r['target_def'], 1), 3)}"
        s = specs[r["target_def"]]
        d = s["size"]["drawSize"][0]
        r["prompt"], r["_prompt_by"] = neutral_prompt(r["prompt"])
        r["canvas_w"] = r["canvas_h"] = canvas_for(d)
        r["drawsize"] = d
        r["biome_neutral"] = True
        r.pop("source_run", None)
        return r

    with ThreadPoolExecutor(4) as ex:
        rows = list(ex.map(fix, rows))
    for r in rows:
        r.pop("_prompt_by", None)
    Path(a.out).write_text(json.dumps(rows, indent=1))
    print(f"{len(rows)} rows -> {a.out}")
    if a.file:
        subprocess.run([sys.executable, str(ROOT / "src/RimMandrake/Utils/artpipe/fill_queue.py"), "--input", a.out],
                       check=False, timeout=300)


ART = Path("/mnt/d/ClaudeWork/rimmandrake/artpipe")


def job_png(job: str):
    """Path of a finished job's render, or None (not done / not ok)."""
    m = ART / "done" / f"{job}.manifest.json"
    if not m.is_file() or json.loads(m.read_text()).get("status") != "ok":
        return None
    p = ART / "_artsrc" / job / f"{job}.png"
    return p if p.is_file() else None


def cmd_candidates(a):
    sys.path.insert(0, str(HERE.parent / "art"))
    import scale_panel as SP
    out = Path(a.out)
    (out / "panels").mkdir(parents=True, exist_ok=True)
    rows = {}
    for rf in Path(a.rows).glob("*.json"):
        for r in json.loads(rf.read_text()):
            rows[r["id"]] = r
    made, waiting, readyrounds = [], [], []
    judged = set()
    nreg = {}
    for f in (ROOT / "infrastructure/state/art_eval/runs").glob("fauna_*/decisions.jsonl"):
        for line in f.read_text().splitlines():
            r = json.loads(line)
            judged.add((r["subject"], r.get("candidate")))
            if r["decision"] == "REGEN":
                nreg[r["subject"]] = nreg.get(r["subject"], 0) + 1
    for d in a.defs:
        if a.auto:
            a.round = min(nreg.get(d, 0), 3)
            if a.round == 0 or (d, f"r{a.round}") in judged or (d, f"r{a.round + 1}") in judged:
                continue
        base = next(Path(a.specs).glob(f"**/{d}.spec.json"), None)
        if base is None:
            continue
        s = json.loads(base.read_text())
        jobs = {f: f"arteval_{d}_r{a.round}_{f}" for f in ("south", "east", "north")}
        pngs = {f: job_png(j) for f, j in jobs.items()}
        if not all(pngs.values()):
            waiting.append(d)
            continue
        imgs = {f: str(p) for f, p in pngs.items()}
        sz = s["size"]["drawSize"][0]
        cp = out / "panels" / f"{d}_r{a.round}_scale.png"
        SP.render_panel(pngs["east"].read_bytes(), {"kind": "animal", "drawSize": (sz, sz)}, cp,
                        out / "panels" / f"{d}_r{a.round}_scale_full.png")
        imgs["scale"] = str(cp)
        s.update({"candidate": f"r{a.round}", "images": imgs, "artpipe_job": f"arteval_{d}_r{a.round}",
                  "provenance": f"art-eval regen round {a.round}, artpipe jobs arteval_{d}_r{a.round}_*",
                  "previous_prompt": (rows.get(f"arteval_{d}_r{a.round}") or {}).get("prompt")})
        s.pop("images_flight_note", None)
        (out / f"{d}_r{a.round}.spec.json").write_text(json.dumps(s, indent=1))
        made.append(d)
        readyrounds.append((d, a.round))
    print(f"candidate specs: {len(made)} made, {len(waiting)} waiting {waiting}")
    print(" ".join(made))
    (out / "ready.txt").write_text("\n".join(str(out / f"{d}_r{rr}.spec.json") for d, rr in readyrounds) + "\n")


def latest(defname: str, cand: bool):
    """The latest decision record for the subject: candidate runs (…_rN_NN) or first-pass runs (…_NN)."""
    out = None
    for f in sorted((ROOT / "infrastructure/state/art_eval/runs").glob("fauna_*/decisions.jsonl")):
        iscand = "_r" in f.parent.name.split("fauna_", 1)[1]
        if iscand != cand:
            continue
        for line in f.read_text().splitlines():
            r = json.loads(line)
            if r["subject"] == defname:
                out = r
    return out


def cmd_install(a):
    """Install an ACCEPTed candidate's three facings over the installed art through the art ledger (art.py install).

    Gates (all must hold): the candidate's pipeline decision is ACCEPT; the head-to-head compare says B; and when any
    installed file is owner-KEPT the first pass must have been REALLY_BAD (the owner's card 2026-10-23 06:42 says "kept
    art JUDGED REALLY BAD ... redraw on its own, show me after") — then the install carries that card and the revert
    (old kept sha) is logged in infrastructure/state/art_eval/fauna_installs.jsonl."""
    import shutil
    sys.path.insert(0, str(HERE.parent / "art"))
    import artledger as AL
    base = next(Path(a.specs).glob(f"**/{a.defname}.spec.json"))
    spec = json.loads(base.read_text())
    verdict = f"infrastructure/state/delegated/2026-10-23/{a.defname}.json"
    cand = latest(a.defname, True)
    first = latest(a.defname, False)
    cmpf = R.storage_root() / "fauna_cands" / "cmp" / f"{a.defname}_r{a.round}" / "compare.json"
    if not (cand and cand["decision"] == "ACCEPT"):
        print(f"{a.defname}: candidate decision is {cand and cand['decision']} - not installed")
        return 3
    cmp = json.loads(cmpf.read_text()) if cmpf.is_file() else {}
    if not cmp.get("install_b"):
        print(f"{a.defname}: head-to-head says {cmp.get('winner')} (install_b={cmp.get('install_b')}) - not installed")
        return 3
    idx = AL.cached_index()
    files, anykept = [], False
    for f in ("south", "east", "north"):
        old = spec["images"].get(f)
        if old:
            sha = AL.sha256_file(Path(old))
            k = bool(idx.protected(sha))
            anykept |= k
            mod_rel, rel = old.split("/src/", 1)[1].split("/Textures/", 1)
            files.append({"face": f, "mod": mod_rel, "rel": rel, "old_sha": sha, "kept": k})
    if anykept and first["opus"]["band"] != "REALLY_BAD":
        print(f"{a.defname}: owner-kept art, first pass band {first['opus']['band']} (not REALLY_BAD) - flagged, not replaced")
        return 3
    dest = ROOT / "Transient" / "fauna_regen" / a.defname
    dest.mkdir(parents=True, exist_ok=True)
    rc = 0
    done = []
    for fl in files:
        f = fl["face"]
        src = job_png(f"arteval_{a.defname}_r{a.round}_{f}")
        if not src:
            print(f"SKIP {f}: no render")
            rc = 1
            continue
        local = dest / f"r{a.round}_{f}.png"
        shutil.copy(src, local)
        cmd = [sys.executable, str(ROOT / "src/RimMandrake/Utils/art/art.py"), "install", fl["mod"], fl["rel"],
               "--file", str(local.relative_to(ROOT))]
        cmd += (["--by-card", P_KEPT_CARD] if fl["kept"] else
                ["--reason", "script:src/RimMandrake/Utils/art_eval/fauna_drive.py",
                 "--why", f"delegated: art {verdict} (pipeline ACCEPT + head-to-head B)"])
        if a.dry_run:
            cmd.append("--dry-run")
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        tail = (r.stdout + r.stderr).strip().splitlines()
        print(f"{a.defname} {f}: kept={fl['kept']} rc={r.returncode} {tail[-1][:160] if tail else ''}")
        if r.returncode == 0:
            fl["new_sha"] = AL.sha256_file(local)
            done.append(fl)
        rc |= r.returncode
    if done and not a.dry_run:
        rec = {"at": R.now(), "def": a.defname, "round": a.round, "verdict": verdict, "compare": {k: cmp.get(k) for k in ("winner", "reason")},
               "replaced_kept": anykept, "files": done,
               "revert": [["python3", "src/RimMandrake/Utils/art/art.py", "install", x["mod"], x["rel"], x["old_sha"], "--by-card", P_KEPT_CARD]
                          for x in done if x["kept"]] +
                         [["python3", "src/RimMandrake/Utils/art/art.py", "install", x["mod"], x["rel"], x["old_sha"], "--reason", "script:src/RimMandrake/Utils/art_eval/fauna_drive.py"]
                          for x in done if not x["kept"]]}
        with (ROOT / "infrastructure/state/art_eval/fauna_installs.jsonl").open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
    return rc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("rows")
    r.add_argument("runs", nargs="+")
    r.add_argument("--specs", default=str(R.storage_root() / "fauna_specs"))
    r.add_argument("--out", required=True)
    r.add_argument("--file", action="store_true")
    c = sub.add_parser("candidates")
    c.add_argument("defs", nargs="+")
    c.add_argument("--round", type=int, default=1)
    c.add_argument("--specs", default=str(R.storage_root() / "fauna_specs"))
    c.add_argument("--rows", default=str(R.storage_root() / "fauna_rows"))
    c.add_argument("--out", required=True)
    c.add_argument("--auto", action="store_true", help="round per def = its REGEN count; skip defs already judged")
    i = sub.add_parser("install")
    i.add_argument("defname")
    i.add_argument("--round", type=int, default=1)
    i.add_argument("--specs", default=str(R.storage_root() / "fauna_specs"))
    i.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    {"rows": cmd_rows, "candidates": cmd_candidates, "install": cmd_install}[a.cmd](a)


if __name__ == "__main__":
    main()
