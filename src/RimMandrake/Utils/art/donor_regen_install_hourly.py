#!/usr/bin/env python3
"""donor_regen_install_hourly.py - hourly: install finished dregen_ renders (accepted-for-now), commit ONLY what the
run touched, publish. Owner decision 2026-10-19 (question card): finished donor-replacement renders install every hour.

    python3 src/RimMandrake/Utils/art/donor_regen_install_hourly.py [--dry-run]

Runs bulk_accept_renders.py plan + apply (art_accept_finished.py was retired by eaf051b8f; every finished render waiting is installed, dregen_ ones included). Skips (exit 0, logged)
when a git index lock is held. A refused push (ART_VERSION_WRANGLING_1 pre-push hook etc.) is logged; the local commit
stays and the next run's ./publish retries it. Never forces, never stages anything but the run's own paths + the
FOUNDRY art-events shard. Log: Transient/donor_regen_install.log (untracked).
Timer: rm-donor-regen-install.timer (transient systemd-run; dies on WSL restart, re-create it - see the item
DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO).
"""
import json, os, re, subprocess, sys, tempfile, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
LOG = REPO / "Transient" / "donor_regen_install.log"
EVENTS = "infrastructure/state/art/events/FOUNDRY.jsonl"
TOOL = "src/RimMandrake/Utils/art/bulk_accept_renders.py"
os.environ.setdefault("RIMFLOW_SEAT", "FOUNDRY")
os.environ["BULK_ACCEPT_NO_OWNER_OVERRIDE"] = "1"  # owner-KEPT/rejected destinations are refused, never overridden  # the art ledger refuses to guess the seat
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
    plan = Path(tempfile.mkdtemp(prefix="dregen_plan_")) / "plan.json"
    r = run("python3", TOOL, "plan", "--out", str(plan))
    if r.returncode:
        return log(f"FAIL plan rc={r.returncode} (no commit): {(r.stdout + r.stderr)[-400:]!r}")
    r = run("python3", TOOL, "apply", "--plan", str(plan), *(["--dry-run"] if DRY else []))
    out = r.stdout + r.stderr
    m = re.search(r"^log: (.+)$", r.stdout, re.M)
    if r.returncode or not m:
        return log(f"FAIL rc={r.returncode} (no commit): {out[-400:]!r}")
    d = json.loads(Path(m.group(1)).read_text())
    if DRY:
        return log(f"plan: {len(json.loads(plan.read_text())['rows'])} installable rows (dry run installs nothing)")
    d = {k: d.get(k, []) for k in ("installed", "repointed", "retired", "refused", "already")} | d
    # owner-KEPT refusals are SHELVED (owner 2026-10-19: the renders wait as unassigned candidates on the item's sheet,
    # the kept picture stays): logged as a count, never re-reported as new. Anything else refused is still "refused".
    shelved = [x for x in d["refused"] if "owner-KEPT" in (x.get("why") or "")]
    d["refused"] = [x for x in d["refused"] if x not in shelved]
    SH = REPO / "Transient" / "donor_regen_shelved.json"
    try:
        seen = set(json.loads(SH.read_text()))
    except (OSError, ValueError):
        seen = set()
    fresh = sorted({x["job"] for x in shelved if x["job"]} - seen)
    SH.write_text(json.dumps(sorted(seen | {x["job"] for x in shelved if x["job"]})))
    log(f"{len(d['installed'])} installed, {len(shelved)} shelved (owner-KEPT, {len(fresh)} newly), "
        f"{len(d['refused'])} refused, plan-log={m.group(1)}")
    if fresh:
        log("newly shelved (back-fill them onto sheets: art.py backfill artpipe, refresh_sheets.py): " + ", ".join(fresh))
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
