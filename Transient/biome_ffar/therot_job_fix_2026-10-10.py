#!/usr/bin/env python3
"""The Rot variant jobs (therot_verify_2026-10-10.md, items 2 and 8).

Grading fix (job field only, no daemon change): canon_check grades an owner job against `owner_note`, one line per
sentence, so the whole note ("Rename, improve description, make two other improved variants ...") was graded on
ONE render and failed it for not showing two variants. Each rotvar job's `owner_note` becomes a LIST of acceptance
lines for that job's own single-variant brief (canon_check takes a list verbatim); his verbatim note stays quoted in
line 1 and in the prompt.
  - pending rotvar_* jobs: owner_note rewritten in place (atomic replace, only while still in pending/)
  - rotvar_violetwimple_a/b_v1, rotvar_wrinklecap_a/b_v1: referenced the cartoon A retired by the owner card of
    2026-10-09; withdrawn to _withdrawn/, re-filed as _v2 referencing the picture that holds his pick's slot now
  - failed rotvar_* jobs that failed on the whole-note line: re-filed as _v2
    python3 Transient/biome_ffar/therot_job_fix_2026-10-10.py [--apply]
"""
import json, os, re, shutil, sys, time
from pathlib import Path
sys.path.insert(0, "src/RimMandrake/Utils/art")
sys.path.insert(0, "src/RimMandrake/Utils/artpipe")
import artledger as L  # noqa: E402
import fill_queue as FQ  # noqa: E402

A = Path("/mnt/d/Luke/dev/_artpipe")
PEND, ACT, DONE, FAIL, WD = (A / d for d in ("pending", "active", "done", "failed", "_withdrawn"))
PLANT = "src/RimMandrake/TheRot/Textures/RotSporeKit/Things/Plant/"
REPICK = {"rotvar_violetwimple": PLANT + "VioletWimple/VioletWimple_A.png",   # render D, the 10-09 card's kept picture
          "rotvar_wrinklecap": PLANT + "Wrinklecap/Wrinklecap_A.png"}       # render D, same
QUOTE = "make two other improved variants that are more realistic"


def lines_for(job):
    p = job["prompt"].split("CANON CORRECTIONS")[0]
    m = re.search(r"sprite of the (.+?) \((.+?)\), painterly", p)
    lab, desc = (m.group(1), m.group(2)) if m else (job["target_def"], "")
    f = re.search(r"variant of the same species, (.+?), so it can sit", p)
    form = f.group(1) if f else "a different individual"
    first = re.split(r"(?<=[.!?])\s", desc.strip())[0] if desc else ""
    out = [f"One single {lab} plant, drawn as {form}. The owner asked to \"{QUOTE}\"; this job draws ONE of those "
           f"two (the other is a separate job), so a single plant is correct.",
           "Realistic natural-history rendering: believable form and matte texture, not cartoonish, not cute, no outlines."]
    if first:
        out.append(f"Reads as the species described: {first}")
    return out


def refile(job, apply, new_ref=None):
    nj = {k: v for k, v in job.items()}
    nj["id"] = re.sub(r"_v1$", "_v2", job["id"])
    nj["prompt"] = job["prompt"].split(" CANON CORRECTIONS")[0]
    nj["owner_note"] = lines_for(job)
    nj["created"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if new_ref:
        nj["canon_reference"] = [new_ref]
    FQ.write_job(nj, PEND, ACT, DONE, FAIL, dry_run=not apply)
    return nj["id"]


def main(apply):
    log = []
    for p in sorted(PEND.glob("rotvar_*.json")):
        job = json.loads(p.read_text())
        key = next((k for k in REPICK if job["id"].startswith(k + "_")), None)
        if key:
            live = Path(REPICK[key])
            sha = L.sha256_file(live)
            if not L.store_has(sha) and apply:
                L.store_put_file(live)
            ref = str(L.store_path(sha))
            if apply:
                WD.mkdir(exist_ok=True)
                shutil.move(str(p), WD / p.name)
            log.append(f"withdrew {job['id']} (ref {Path(job['canon_reference'][0]).name[:8]}, retired cartoon)")
            log.append(f"filed {refile(job, apply, ref)} ref {sha[:8]} ({live.name})")
        else:
            job["owner_note"] = lines_for(job)
            if apply:
                tmp = p.with_name(f".{p.name}.tmp.{os.getpid()}")
                tmp.write_text(json.dumps(job, indent=2, sort_keys=True) + "\n")
                if p.exists():
                    os.replace(tmp, p)
                    log.append(f"rewrote owner_note {job['id']}")
                else:
                    tmp.unlink()
                    log.append(f"SKIPPED {job['id']}: claimed by the daemon mid-edit")
            else:
                log.append(f"would rewrite owner_note {job['id']}")
    for p in sorted(FAIL.glob("rotvar_*_v1.json")):
        man = json.loads(p.with_name(p.stem + ".manifest.json").read_text())
        bad = [l for l in (man.get("canon_check") or {}).get("lines", []) if l["verdict"] == "fail"]
        if bad and all("two other" in l["line"] for l in bad):
            job = json.loads(p.read_text())
            log.append(f"filed {refile(job, apply)} (re-file of failed {job['id']})")
    print("\n".join(log))


if __name__ == "__main__":
    main("--apply" in sys.argv)
