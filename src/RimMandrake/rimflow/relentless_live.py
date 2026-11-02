#!/usr/bin/env python3
"""relentless_live.py -- Relentless's live tier: one built item's live criterion, proved on the running game.

Owner ruling by card, 2026-11-02 (ledger note on PLANNING_BUILD_DAYS_OF_ORDERS_NO_HOME): "Relentless learns live testing
(Foundry stays paused, the 512 built items wait on that build)". Design relentless_agent_design_2026-11-01.md section 13
step 9: "A real live leaf closes through a testq or pilot receipt on the deployed hash".

    python3 src/RimMandrake/rimflow/relentless_live.py run --item ID --criterion A2 \\
        --proof "python3 src/RimMandrake/Utils/live_def_check.py --has ThingDef/RM_Chittik=CompProperties_WoundLink" \\
        --deploy "--compose biomes --with SWBestiary"

ONE RUN, in this order. Every refusal before step 5 leaves the item untouched and the bridge where it was:
  1. the item is built or validated and still owes the criterion, at a live level (LIVE_LEVELS);
  2. not a flyer: a title, criterion or proof naming flight is refused (standing ruling: never live-test a flyer's flight);
  3. the build is deployed: deploy_custom_mods.py's plan (with --deploy's args) covers every mod the built commit changed,
     lists none of its game files as drift or held, and the running game started after the newest of them was written;
  4. the bridge: `rimflow bridge take --idle-ok`; refused means busy, and nothing runs;
  5. the proof runs (exit 0 PASS, 1 FAIL, anything else or a timeout UNMEASURED) and the bridge is released (--mine)
     whatever happened, before anything is written to the ledger;
  6. PASS or FAIL is a `verify --criterion --level --sha <built sha>`, so a pass drops the criterion and a fail stands;
     UNMEASURED is a note, never a run. Every outcome, refusals too, is a row in <RELENTLESS_ROOT>/live/runs.jsonl.

Proofs here are the item's own read of the game. Nothing in this file changes the game; a proof that would restart it or
swap the mod list is refused (rules live.forbid_re): the running game is the owner's, and a load is another tier.
"""
import argparse
import glob
import json
import os
import re
import shlex
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BOOKS = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RULES = os.path.join(HERE, "relentless_rules.json")
GAME_MODS = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
LIVE_LEVELS = ("L1", "L2", "GREEN-MIN", "GREEN-FULL")       # model.LEVEL_NEEDS says bridge; L3 is a judge, L4 a human
TESTABLE = ("built", "validated")
PASS, FAIL = 0, 1
DEFAULTS = {
    "flyer_re": r"\b(fly|flies|flying|flyers?|flight|wings?|airborne|takes? off|take-off)\b",
    "forbid_re": r"modlist_swap|modcheck\s+run|deploy_custom_mods\.py\b.*--apply|(^|[\s/])game\s+(UP|DOWN|DEPLOYING|LOADING)\b"
                 r"|stop_game|launch_game|load_game|execute_debug_action|--yes-i-know-this-is-live",
    "proof_max_s": 600,
    "plan_max_s": 500,
}
SRC_MOD = re.compile(r"^src/(Rim[A-Za-z]+)/([^/]+)/(.+)$")     # src/<tier>/<Mod>/<path in the mod>
DRIFT = re.compile(r"^\s{2,6}([~+\-H])\s+(\S.*?)(?:\s{2,}\(.*\))?\s*$")
SECTION = re.compile(r"^(\S+)\s+(mandrake\.\S+)(.*)$")      # deploy_custom_mods prints one per mod, drift or not
COMPOSED = re.compile(r"^\s*compose\s+(\S+)\s+(mandrake\.\S+)\s.*->\s*(\S+)\s*$")


def live_rules(r):
    out = dict(DEFAULTS)
    out.update((r or {}).get("live") or {})
    return out


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


# ---------------------------------------------------------------- pure checks

def owed(item, criterion):
    """-> (level, text) of a live criterion the item owes, or raise ValueError saying why it is not one."""
    if item is None:
        raise ValueError("no such item")
    if item["state"] not in TESTABLE:
        raise ValueError("%s is %s: only a built or validated item has a build to test" % (item["id"], item["state"]))
    if not item.get("built_sha"):
        raise ValueError("%s has no built sha" % item["id"])
    crit = {c["id"]: c for c in item.get("criteria") or []}
    if criterion not in crit:
        raise ValueError("%s has no criterion %s" % (item["id"], criterion))
    if criterion not in (item.get("outstanding") or []):
        raise ValueError("%s %s is not owed" % (item["id"], criterion))
    level = crit[criterion]["level"]
    if level not in LIVE_LEVELS:
        raise ValueError("%s %s is %s, not a live level (%s)" % (item["id"], criterion, level, ", ".join(LIVE_LEVELS)))
    return level, crit[criterion].get("text") or ""


def refused_proof(lr, title, text, proof):
    """-> why this run may not happen on the live game, or None."""
    for what, s in (("title", title), ("criterion", text), ("proof", proof)):
        m = re.search(lr["flyer_re"], s or "", re.I)
        if m:
            return "flyer: the %s names %r; a flyer's flight is never live-tested (standing ruling)" % (what, m.group(0))
    m = re.search(lr["forbid_re"], proof or "")
    if m:
        return "the proof would change the running game (%r): a load or a mutation is not this tier" % m.group(0)
    return None


def game_files(paths, shippable):
    """The built commit's paths that ship to the game -> [(mod folder, path in the mod)]."""
    out = []
    for p in paths:
        m = SRC_MOD.match(p)
        if m and shippable(m.group(3)):
            out.append((m.group(2), m.group(3)))
    return out


def plan_sections(text):
    """deploy_custom_mods.py's plan -> ({mod folder it covers}, [(section folder, flag, entry)] drifting or held,
    {section folder: why it is not live}: a header flagged NOT DEPLOYED or not enabled)."""
    covered, drift, section, off = set(), [], None, {}
    for line in text.splitlines():
        c = COMPOSED.match(line)
        if c:
            covered.add(c.group(1))
            continue
        s = SECTION.match(line)
        if s:
            section = s.group(1)
            covered.add(section)
            for flag in ("NOT DEPLOYED", "not enabled in ModsConfig"):
                if flag in s.group(3):
                    off[section] = flag
            continue
        d = DRIFT.match(line)
        if d and section:
            drift.append((section, d.group(1), d.group(2)))
    return covered, drift, off


def deploy_gap(files, plan_rc, plan_text):
    """-> why the built commit's game files are not what the game folder holds, or None."""
    if plan_rc != 0:
        return "the deploy plan failed (exit %s): %s" % (plan_rc, plan_text[-300:])
    if "def guard" in plan_text and "REFUSED" in plan_text:
        return "the deploy plan refused: %s" % plan_text[-300:]
    covered, drift, off = plan_sections(plan_text)
    if off:
        return "the plan says %s" % "; ".join("%s: %s" % kv for kv in sorted(off.items()))
    missing = sorted({mod for mod, _ in files} - covered)
    if missing:
        return "the deploy plan does not cover %s: name it in --deploy" % ", ".join(missing)
    for mod, rel in files:
        for section, flag, entry in drift:
            if (section == mod and entry == rel) or entry.endswith("/%s/%s" % (mod, rel)) or entry == "%s/%s" % (mod, rel):
                return "%s/%s is %s in the game folder (%s): the build is not what the game holds" % (
                    mod, rel, "held" if flag == "H" else "out of date", section)
    return None


def deployed_paths(mods_dir, mod, rel):
    """Where a mod file sits in the game folder: Mods/<Mod>/<rel>, or inside a composed mod, Mods/*/*/<Mod>/<rel>."""
    return [p for p in [os.path.join(mods_dir, mod, rel)] + glob.glob(os.path.join(glob.escape(mods_dir), "*", "*",
                                                                                     glob.escape(mod), rel))
            if os.path.isfile(p)]


# ---------------------------------------------------------------- the one run

class Fx(object):
    """Everything that touches the world. The selftest swaps it."""

    def __init__(self, books=BOOKS, seat="BENCH", mods_dir=GAME_MODS):
        self.books, self.seat, self.mods_dir = books, seat, mods_dir

    def item(self, item_id):
        sys.path.insert(0, HERE)
        import model
        it = model.replay(model.read()).items.get(item_id)
        if it is None:
            return None
        return {"id": it.id, "state": it.state, "built_sha": it.built_sha, "title": it.title or "",
                "criteria": list(it.criteria or []), "outstanding": list(it.outstanding or [])}

    def touched(self, sha):
        r = subprocess.run(["git", "show", "--name-only", "--format=", sha], cwd=self.books, capture_output=True,
                           text=True, timeout=60, stdin=subprocess.DEVNULL)
        if r.returncode:
            raise ValueError("git show %s: %s" % (sha, r.stderr[-200:]))
        return [p for p in r.stdout.splitlines() if p.strip() and os.path.exists(os.path.join(self.books, p))]

    def shippable(self, rel):
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
        import deploy_custom_mods
        return deploy_custom_mods.shippable(rel.replace("/", os.sep))

    def deploy_plan(self, args, timeout):
        try:
            r = subprocess.run(["python3", os.path.join(self.books, "src/RimMandrake/Utils/deploy_custom_mods.py"),
                                *shlex.split(args)], cwd=self.books, capture_output=True, text=True, timeout=timeout,
                               stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return None, "the deploy plan took over %ds" % timeout
        return r.returncode, r.stdout + r.stderr

    def mtime(self, mod, rel):
        got = deployed_paths(self.mods_dir, mod, rel)
        return max(os.path.getmtime(p) for p in got) if got else None

    def game_started(self):
        """The running RimWorld's start, epoch seconds; None when none runs or it cannot be read."""
        try:
            r = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                                "(Get-Process RimWorldWin64 -ErrorAction SilentlyContinue | Select-Object -First 1)"
                                ".StartTime.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')"],
                               capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
            return time.mktime(time.strptime(r.stdout.strip(), "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
        except (OSError, ValueError, subprocess.TimeoutExpired):
            return None

    def rimflow(self, *args, timeout=120):
        env = dict(os.environ, RIMFLOW_SEAT=self.seat, AGENT_SEAT=self.seat, CLAUDE_PROJECT_DIR=self.books)
        return subprocess.run(["python3", os.path.join(self.books, "src/RimMandrake/rimflow/cli.py"), *args],
                              cwd=self.books, env=env, capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)

    def run_proof(self, proof, log, timeout):
        """-> the proof's exit code, or None when it outran `timeout`. Output goes to `log`."""
        with open(log, "w", encoding="utf-8") as f:
            f.write("$ %s\n" % proof)
            f.flush()
            try:
                return subprocess.run(proof, shell=True, cwd=self.books, stdout=f, stderr=subprocess.STDOUT,
                                      timeout=timeout, stdin=subprocess.DEVNULL, executable="/bin/bash").returncode
            except subprocess.TimeoutExpired:
                f.write("\nTIMEOUT after %ds\n" % timeout)
                return None


def run(fx, root, item_id, criterion, proof, deploy, r, now=None):
    """-> the run's row (also appended to <root>/live/runs.jsonl). row["outcome"] is PASS, FAIL, UNMEASURED or REFUSED."""
    now = time.time() if now is None else now
    lr = live_rules(r)
    row = {"at": iso(now), "item": item_id, "criterion": criterion, "proof": proof, "deploy": deploy}
    os.makedirs(os.path.join(root, "live"), exist_ok=True)

    def done(outcome, why, **kw):
        row.update(kw, outcome=outcome, why=why)
        with open(os.path.join(root, "live", "runs.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
        return row

    try:
        item = fx.item(item_id)
        level, text = owed(item, criterion)
    except ValueError as e:
        return done("REFUSED", str(e))
    sha = item["built_sha"]
    row.update(sha=sha, level=level)
    why = refused_proof(lr, item["title"], text, proof)
    if why:
        return done("REFUSED", why)
    try:
        files = game_files(fx.touched(sha), fx.shippable)
    except ValueError as e:
        return done("UNMEASURED", "cannot read the built commit: %s" % e)
    if files:
        rc, plan = fx.deploy_plan(deploy or "", lr["plan_max_s"])
        why = deploy_gap(files, rc, plan)
        if why:
            return done("UNMEASURED", "not deployed: %s" % why)
        stamps = [fx.mtime(mod, rel) for mod, rel in files]
        if None in stamps:
            lost = [("%s/%s" % f) for f, t in zip(files, stamps) if t is None]
            return done("UNMEASURED", "not deployed: no game copy of %s" % ", ".join(lost[:5]))
        started = fx.game_started()
        if started is None:
            return done("UNMEASURED", "no running game to test")
        if started <= max(stamps):
            return done("UNMEASURED", "the game started %s, before the build's files were deployed %s: it runs the old "
                                      "build" % (iso(started), iso(max(stamps))))
        row.update(game_started=iso(started), deployed=iso(max(stamps)), files=len(files))
    took = fx.rimflow("bridge", "take", "--idle-ok", "--for",
                      "relentless live test: %s %s (%s), read-only proof" % (item_id, criterion, level))
    if took.returncode != 0:
        return done("UNMEASURED", "bridge not taken: %s" % (took.stderr or took.stdout).strip()[-300:])
    log = os.path.join(root, "live", "%s-%s-%s.log" % (item_id, criterion, time.strftime("%Y%m%dT%H%M%SZ",
                                                                                       time.gmtime(now))))
    try:
        code = fx.run_proof(proof, log, lr["proof_max_s"])
    finally:
        gave = fx.rimflow("bridge", "release", "--mine")
        row["released"] = gave.returncode == 0
    if code not in (PASS, FAIL):
        why = "the proof %s" % ("timed out" if code is None else "exited %d: it did not measure" % code)
        note = fx.rimflow("note", item_id, "--text", "relentless live %s %s UNMEASURED: %s (%s)" % (criterion, level, why,
                                                                                                  log)[:400],
                          "--why", "relentless live tier: no verdict, no run recorded")
        return done("UNMEASURED", why, log=log, noted=note.returncode == 0)
    result = "pass" if code == PASS else "fail"
    v = fx.rimflow("verify", item_id, "--criterion", criterion, "--level", level, "--sha", sha, "--result", result,
                   "--config", ("relentless-live: %s" % proof)[:300], "--evidence", log,
                   "--why", "relentless live tier: the running game, deployed build, supervisor-run proof")
    if v.returncode != 0:
        return done("UNMEASURED", "the verdict %s did not land: %s" % (result.upper(), (v.stderr or v.stdout)[-300:]),
                    log=log)
    return done("PASS" if code == PASS else "FAIL", "proof exit %d" % code, log=log)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run", help="one live criterion of one built item")
    p.add_argument("--item", required=True)
    p.add_argument("--criterion", required=True)
    p.add_argument("--proof", required=True, help="a shell command run from the repo root; exit 0 PASS, 1 FAIL")
    p.add_argument("--deploy", default="", help="deploy_custom_mods.py plan arguments covering the item's mods")
    a = ap.parse_args(argv)
    with open(os.environ.get("RELENTLESS_RULES") or RULES, encoding="utf-8") as f:
        r = json.load(f)
    root = os.environ.get("RELENTLESS_ROOT") or "/home/mandrake/rm/relentless"
    row = run(Fx(seat=r.get("seat") or "BENCH"), root, a.item, a.criterion, a.proof, a.deploy, r)
    print(json.dumps(row, indent=1, sort_keys=True))
    return {"PASS": 0, "FAIL": 1}.get(row["outcome"], 2 if row["outcome"] == "UNMEASURED" else 3)


if __name__ == "__main__":
    sys.exit(main())
