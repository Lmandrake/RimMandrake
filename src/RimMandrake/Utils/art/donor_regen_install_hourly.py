#!/usr/bin/env python3
"""donor_regen_install_hourly.py - hourly: install finished dregen_ renders (accepted-for-now), commit ONLY what the
run touched, publish. Owner decision 2026-10-19 (question card): finished donor-replacement renders install every hour.

    python3 src/RimMandrake/Utils/art/donor_regen_install_hourly.py [--dry-run]

Runs art_accept_finished.py --prefix dregen_ (donor-coat AND SWBestiary jobs share that prefix). Skips (exit 0, logged)
when a git index lock is held. A refused push (ART_VERSION_WRANGLING_1 pre-push hook etc.) is logged; the local commit
stays and the next run's ./publish retries it. Never forces, never stages anything but the run's own paths + the
FOUNDRY art-events shard. Log: Transient/donor_regen_install.log (untracked).
Timer: rm-donor-regen-install.timer (transient systemd-run; dies on WSL restart, re-create it - see the item
DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO).
"""
import json, re, subprocess, sys, tempfile, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
LOG = REPO / "Transient" / "donor_regen_install.log"
EVENTS = "infrastructure/state/art/events/FOUNDRY.jsonl"
TOOL = "src/RimMandrake/Utils/art/art_accept_finished.py"
DRY = "--dry-run" in sys.argv


def log(msg):
    LOG.parent.mkdir(exist_ok=True)
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {'[dry] ' if DRY else ''}{msg}"
    with LOG.open("a") as fh:
        fh.write(line + "\n")
    print(line)


def run(*a, **k):
    return subprocess.run(a, cwd=REPO, capture_output=True, text=True, **k)


def main():
    lock = Path(run("git", "rev-parse", "--git-path", "index.lock").stdout.strip())
    lock = lock if lock.is_absolute() else REPO / lock
    if lock.exists():
        return log(f"SKIP: git index lock held ({lock})")
    args = ["python3", TOOL, "--prefix", "dregen_"] + ([] if DRY else ["--apply"])
    r = run(*args)
    out = r.stdout + r.stderr
    m = re.search(r"^log: (.+)$", r.stdout, re.M)
    if r.returncode or not m:
        return log(f"FAIL rc={r.returncode} (no commit): {out[-400:]!r}")
    first = next((l for l in r.stdout.splitlines() if l.startswith(("APPLIED", "DRY RUN"))), "")
    d = json.loads(Path(m.group(1)).read_text())
    log(f"{first} plan-log={m.group(1)}")
    if DRY:
        return log(f"would install {len(d['would_install'])}, needs his words {len(d['needs_his_words'])}")
    paths = sorted(set(d["installed"]) | set(d["repointed"]) | set(d["retired"]))
    n = len(d["installed"])
    if not paths:
        log("nothing installed")
    else:
        pf = Path(tempfile.mkdtemp(prefix="dregen_inst_")) / "paths.txt"
        pf.write_text("\n".join(paths + [EVENTS]) + "\n")
        a = run("git", "add", "--all", f"--pathspec-from-file={pf}")
        if a.returncode:
            return log(f"git add failed: {a.stderr[-300:]!r}")
        msg = (f"Donor art: hourly install of {n} finished dregen_ renders (accepted-for-now)\n\n"
               "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n")
        c = run("git", "commit", "-m", msg, f"--pathspec-from-file={pf}")
        if c.returncode:
            return log(f"git commit failed: {(c.stdout + c.stderr)[-300:]!r}")
        log(f"committed {len(paths)} paths ({n} installed)")
    p = run("./publish")
    if p.returncode:
        return log(f"PUSH REFUSED/FAILED, retry next hour: {(p.stdout + p.stderr)[-400:]!r}")
    log("publish: " + (p.stdout.strip().splitlines() or [""])[-1])


main()
