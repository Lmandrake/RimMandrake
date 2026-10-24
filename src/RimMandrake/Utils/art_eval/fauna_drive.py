#!/usr/bin/env python3
"""Drive the art-eval regen loop for live fauna: rows -> artpipe jobs, finished jobs -> candidate specs -> install.

    python3 fauna_drive.py rows <run-id>... --out rows.json [--file]     # regen_jobs.json -> fill_queue rows
    python3 fauna_drive.py candidates <DEF>... --round N --out <dir>      # done arteval_<DEF>_rN_* renders -> specs
    python3 fauna_drive.py install <DEF> --round N                        # accepted candidate -> art.py install
    python3 fauna_drive.py reset <DEF>... --source-run <run> --by-card "<q -> pick>"   # fresh round series (owner's call)
    python3 fauna_drive.py owner-prompt <DEF> --text "<his words>" --owner-said "<his words>"  # his prompt for DEF
    python3 fauna_drive.py prompts [<DEF>...]                             # owner prompts found, and where from

Fresh rounds: `reset` appends to round_resets.jsonl (round_series.py); from then on every counter here and in
runner.py counts the new series (1 + REGENs after the reset, cap 3) and job ids carry it (arteval_<DEF>_s1r1_south),
so nothing old is edited and no id collides. `rows <source run> --only <DEF>...` then files round 1 of the series.
Owner prompts: `rows` uses his text VERBATIM, wrapped in the template's style/alpha/size sentences, instead of the
pipeline's own regen prompt, and never sends it through the facing-neutral rewrite; if his text trips the per-facing
gate the row is held (printed) rather than reworded. Notes he adds later are re-read on every `rows` call.

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
import round_series as RS  # noqa: E402

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
    if a.only:
        rows = [r for r in rows if r["target_def"] in a.only]
        missing = sorted(set(a.only) - {r["target_def"] for r in rows})
        if missing:
            print(f"no regen row for {missing} in {a.runs}")
    specs = {}
    for p in Path(a.specs).glob("**/*.spec.json"):
        s = json.loads(p.read_text())
        specs[s["subject"]] = s

    rs = RS.resets()
    for t in sorted({r["target_def"] for r in rows if RS.stopped(r["target_def"], rs)}):
        print(f"{t}: fresh series STOPPED ({RS.stopped(t, rs).get('why') or RS.stopped(t, rs).get('by_card')}) - no row")
    rows = [r for r in rows if not RS.stopped(r["target_def"], rs)]
    nreg = RS.regen_counts(RS.decisions(), rs)
    owner = RS.owner_prompts()
    held = []

    def fix(r):
        # the round is the number of REGEN verdicts on the subject in its current series, counted from the decision
        # logs (the shared regen_rounds.json lost updates under parallel runs); round_series.py owns the count
        t = r["target_def"]
        r["id"] = f"arteval_{t}_{RS.tag(t, min(nreg.get(t, 1), 3), rs)}"
        s = specs[t]
        d = s["size"]["drawSize"][0]
        if t in owner:
            r["prompt"] = RS.compose_owner_prompt(RS.label_of(s), owner[t]["text"])
            r["_prompt_by"] = "owner"
            r["style_notes"] = (r.get("style_notes", "") + f"; owner prompt verbatim from {owner[t]['source']}").lstrip("; ")
            hits = R._gate_hits(r["prompt"])
            if hits:
                held.append((t, hits))
        else:
            r["prompt"], r["_prompt_by"] = neutral_prompt(r["prompt"])
        r["canvas_w"] = r["canvas_h"] = canvas_for(d)
        r["drawsize"] = d
        r["biome_neutral"] = True
        r.pop("source_run", None)
        return r

    with ThreadPoolExecutor(4) as ex:
        rows = list(ex.map(fix, rows))
    for t, hits in held:
        print(f"HELD {t}: the owner's prompt names {hits}, which the per-facing gate refuses; not reworded - ask him")
    rows = [r for r in rows if r["target_def"] not in {t for t, _ in held}]
    for r in rows:
        print(f"{r['id']}: prompt by {r.pop('_prompt_by', None)}")
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
    rs = RS.resets()
    recs = list(RS.decisions())
    judged = {(r["subject"], r.get("candidate")) for _, r in recs}
    nreg = RS.regen_counts(recs, rs)
    for d in a.defs:
        if RS.stopped(d, rs):
            print(f"{d}: fresh series STOPPED - no candidate")
            continue
        if a.auto:
            a.round = min(nreg.get(d, 0), 3)
            if a.round == 0 or (d, RS.tag(d, a.round, rs)) in judged or (d, RS.tag(d, a.round + 1, rs)) in judged:
                continue
        tg = RS.tag(d, a.round, rs)
        base = next(Path(a.specs).glob(f"**/{d}.spec.json"), None)
        if base is None:
            continue
        s = json.loads(base.read_text())
        jobs = {f: f"arteval_{d}_{tg}_{f}" for f in ("south", "east", "north")}
        pngs = {f: job_png(j) for f, j in jobs.items()}
        if not all(pngs.values()):
            waiting.append(d)
            continue
        imgs = {f: str(p) for f, p in pngs.items()}
        sz = s["size"]["drawSize"][0]
        cp = out / "panels" / f"{d}_{tg}_scale.png"
        SP.render_panel(pngs["east"].read_bytes(), {"kind": "animal", "drawSize": (sz, sz)}, cp,
                        out / "panels" / f"{d}_{tg}_scale_full.png")
        imgs["scale"] = str(cp)
        s.update({"candidate": tg, "images": imgs, "artpipe_job": f"arteval_{d}_{tg}",
                  "provenance": f"art-eval regen round {tg}, artpipe jobs arteval_{d}_{tg}_*",
                  "previous_prompt": (rows.get(f"arteval_{d}_{tg}") or {}).get("prompt")})
        s.pop("images_flight_note", None)
        (out / f"{d}_{tg}.spec.json").write_text(json.dumps(s, indent=1))
        made.append(d)
        readyrounds.append((d, tg))
    print(f"candidate specs: {len(made)} made, {len(waiting)} waiting {waiting}")
    print(" ".join(made))
    (out / "ready.txt").write_text("\n".join(str(out / f"{d}_{rr}.spec.json") for d, rr in readyrounds) + "\n")


def latest(defname: str, cand: bool):
    """The latest decision record for the subject: candidate runs (…_rN_NN) or first-pass runs (…_NN)."""
    out = None
    for run, r in RS.decisions():
        iscand = "_r" in run.split("fauna_", 1)[1]
        if iscand != cand or r["subject"] != defname:
            continue
        if out is None or RS._instant(r.get("at")) >= RS._instant(out.get("at")):   # newest by time, not run name
            out = r
    return out


def cmd_install(a):
    """Install an ACCEPTed candidate's three facings over the installed art through the art ledger (art.py install).

    Gates (all must hold): the candidate's pipeline decision is ACCEPT; the head-to-head compare says B; and when any
    installed file is owner-KEPT the first pass must have been REALLY_BAD (the owner's card 2026-10-23 06:42 says "kept
    art JUDGED REALLY BAD ... redraw on its own, show me after") — then the install carries that card and the revert
    (old kept sha) is logged in infrastructure/state/art_eval/fauna_installs.jsonl."""
    import shutil
    if RS.stopped(a.defname):
        print(f"{a.defname}: fresh series STOPPED ({RS.stopped(a.defname)}) - not installed")
        return 2
    sys.path.insert(0, str(HERE.parent / "art"))
    import artledger as AL
    base = next(Path(a.specs).glob(f"**/{a.defname}.spec.json"))
    spec = json.loads(base.read_text())
    verdict = f"infrastructure/state/delegated/2026-10-23/{a.defname}.json"
    cand = latest(a.defname, True)
    first = latest(a.defname, False)
    tg = RS.tag(a.defname, a.round)
    cmpf = R.storage_root() / "fauna_cands" / "cmp" / f"{a.defname}_{tg}" / "compare.json"
    if cand and cand.get("candidate") != tg:
        print(f"{a.defname}: newest candidate decision is for {cand.get('candidate')}, not {tg} - not installed")
        return 3
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
        src = job_png(f"arteval_{a.defname}_{tg}_{f}")
        if not src:
            print(f"SKIP {f}: no render")
            rc = 1
            continue
        local = dest / f"{tg}_{f}.png"
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
        rec = {"at": R.now(), "def": a.defname, "round": a.round, "tag": tg, "verdict": verdict, "compare": {k: cmp.get(k) for k in ("winner", "reason")},
               "replaced_kept": anykept, "files": done,
               "revert": [["python3", "src/RimMandrake/Utils/art/art.py", "install", x["mod"], x["rel"], x["old_sha"], "--by-card", P_KEPT_CARD]
                          for x in done if x["kept"]] +
                         [["python3", "src/RimMandrake/Utils/art/art.py", "install", x["mod"], x["rel"], x["old_sha"], "--reason", "script:src/RimMandrake/Utils/art_eval/fauna_drive.py"]
                          for x in done if not x["kept"]]}
        with (ROOT / "infrastructure/state/art_eval/fauna_installs.jsonl").open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
    return rc


def cmd_reset(a):
    jobs = ROOT / f"infrastructure/state/art_eval/runs/{a.source_run}/regen_jobs.json"
    have = {r["target_def"] for r in json.loads(jobs.read_text())} if jobs.is_file() else set()
    for d in a.defs:
        if d not in have:
            print(f"{d}: no regen row in {jobs} - not reset")
            return 2
    for d in a.defs:
        rec = RS.add_reset(d, a.source_run, {"by_card": a.by_card, "owner_said": a.owner_said,
                                              "per_ruling": a.per_ruling, "why": a.why})
        print(f"{d}: series {rec['series']} from {a.source_run}; next job arteval_{d}_{RS.tag(d, 1)}")
    return 0


def cmd_stop(a):
    for d in a.defs:
        try:
            rec = RS.add_stop(d, {"by_card": a.by_card, "owner_said": a.owner_said, "per_ruling": a.per_ruling,
                                  "why": a.why})
        except ValueError as e:
            print(f"{d}: {e}")
            return 2
        print(f"{d}: series {rec['series']} STOPPED; rows/candidates/install now refuse it")
    return 0


def cmd_owner_prompt(a):
    if not (a.owner_said or a.by_card):
        print("the text must be his: give --owner-said (his words) or --by-card")
        return 2
    rec = {"at": R.now(), "def": a.defname, "text": a.text, "source": a.source}
    rec.update({k: v for k, v in (("owner_said", a.owner_said), ("by_card", a.by_card)) if v})
    with RS.OWNER_PROMPTS.open("a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(f"{a.defname}: owner prompt recorded; next `rows` uses it verbatim")
    return 0


def cmd_prompts(a):
    found = RS.owner_prompts()
    for d in (a.defs or sorted(found)):
        f = found.get(d)
        print(f"{d}: " + (f"{f['source']} @ {f['at']}: {f['text']}" if f else "no owner prompt"))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("rows")
    r.add_argument("runs", nargs="+")
    r.add_argument("--specs", default=str(R.storage_root() / "fauna_specs"))
    r.add_argument("--out", required=True)
    r.add_argument("--file", action="store_true")
    r.add_argument("--only", nargs="+", help="only these defs' rows")
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
    z = sub.add_parser("reset", help="start a fresh round series (owner's decision; appends round_resets.jsonl)")
    z.add_argument("defs", nargs="+")
    z.add_argument("--source-run", required=True, help="run whose regen_jobs.json row is round 1 of the series")
    z.add_argument("--by-card")
    z.add_argument("--owner-said")
    z.add_argument("--per-ruling")
    z.add_argument("--why")
    st = sub.add_parser("stop", help="end a fresh series (e.g. he kept/picked its art); appends round_resets.jsonl")
    st.add_argument("defs", nargs="+")
    st.add_argument("--by-card")
    st.add_argument("--owner-said")
    st.add_argument("--per-ruling")
    st.add_argument("--why")
    o = sub.add_parser("owner-prompt", help="record the owner's prompt text for a creature (used verbatim)")
    o.add_argument("defname")
    o.add_argument("--text", required=True)
    o.add_argument("--owner-said")
    o.add_argument("--by-card")
    o.add_argument("--source", default="chat")
    q = sub.add_parser("prompts", help="owner prompts found and where from")
    q.add_argument("defs", nargs="*")
    a = ap.parse_args(argv)
    return {"rows": cmd_rows, "candidates": cmd_candidates, "install": cmd_install, "reset": cmd_reset,
            "stop": cmd_stop, "owner-prompt": cmd_owner_prompt, "prompts": cmd_prompts}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
