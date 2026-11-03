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
  4b. the site (RELENTLESS_LIVE_FIX_GAME_UP_NOTHING_MEASURED): a `live-site <CID>: <cmd>` line in the item's
     live_proofs file is run first, bridge held. It may only be Utils/live_site.py (SITE_CMD), which makes the map the
     proof reads (a biome on the scratch quicktest tile) or loads a named save; exit non-0 is UNMEASURED "site not
     prepared", and the proof does not run. Before it, HORIZON_CARAVAN ran its Stillsand probe on a Leaning Scrub map
     eight times and LEANINGSCRUB_STALL_SHARED_MOVE_1 ran on the very biome its criteria exclude;
  5. the proof runs (exit 0 PASS, 1 FAIL, anything else or a timeout UNMEASURED) and the bridge is released (--mine)
     whatever happened, before anything is written to the ledger. A `python3 ...` proof that dies on the bridge's
     "cannot reach the bridge from WSL" (RimBridge binds Windows loopback) is rerun once under python.exe;
  6. PASS or FAIL is a `verify --criterion --level --sha <built sha>`, so a pass drops the criterion and a fail stands;
     UNMEASURED is a note, never a run. Every outcome, refusals too, is a row in <RELENTLESS_ROOT>/live/runs.jsonl.
     The same cause UNMEASURED `repeat_unmeasured` times running on one game is a RELOAD request, said once in the
     ledger: the row's why starts RELOAD, relentless_game restages on it, and the round skips it until the game changes.
     The repeats between are rows only (eight identical ledger notes in an hour was the old behaviour).

Proofs here are the item's own read of the game. Nothing in this file changes the game; a proof that would restart it or
swap the mod list is refused (rules live.forbid_re): the running game is the owner's, and a load is another tier. The
one change allowed is the site step above, through one reviewed tool that refuses a game past two in-game days.
"""
import argparse
import calendar
import glob
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BOOKS = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RULES = os.path.join(HERE, "relentless_rules.json")
GAME_MODS = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
LIVE_LEVELS = ("L1", "L2", "GREEN-MIN", "GREEN-FULL")       # model.LEVEL_NEEDS says bridge; L3 is a judge, L4 a human
# PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS (owner 2026-11-02): "small mod lists should always be the way to test until a
# final verification pass on the whole huge mod list." Every live level but FINAL runs on any game that holds the item's
# mods and their dependencies; a FINAL clause is the full-list verification, run only when the full list is up.
FINAL = "GREEN-FULL"
FINAL_WAIT = "final verification waits for the full list"     # relentless_game reads this prefix: batch, never restage
FULL_LIST = os.path.join(BOOKS, "infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")
FULL_TIER_SHARE = 0.5       # northstar_driver.preflight's: under half the full list running is another tier
TESTABLE = ("built", "validated")
PASS, FAIL = 0, 1
DEFAULTS = {
    "flyer_re": r"\b(fly|flies|flying|flyers?|flight|wings?|airborne|takes? off|take-off)\b",
    "forbid_re": r"modlist_swap|modcheck\s+run|deploy_custom_mods\.py\b.*--apply|(^|[\s/])game\s+(UP|DOWN|DEPLOYING|LOADING)\b"
                 r"|stop_game|launch_game|load_game|execute_debug_action|--yes-i-know-this-is-live",
    "proof_max_s": 600,
    "plan_max_s": 500,
    "site_max_s": 480,
    "repeat_unmeasured": 3,
}
RELOAD = "reload needed"        # relentless_game RESTAGE reads this prefix; the round skips it on the same game
SITE_CMD = re.compile(r"^python\.exe src/RimMandrake/Utils/live_site\.py(?: --[a-z][a-z-]*(?: [A-Za-z0-9_.\-]+)?)+$")
# rimbridge_client.resolve_endpoint's refusal under WSL python3: the proof never reached the game
WSL_BRIDGE = ("cannot reach the bridge from WSL", "Re-run under Windows Python")
SRC_MOD = re.compile(r"^src/(Rim[A-Za-z]+)/([^/]+)/(.+)$", re.S)     # src/<tier>/<Mod>/<path in the mod>
DRIFT = re.compile(r"^\s{2,6}([~+\-H])\s+(\S.*?)(?:\s{2,}\(.*\))?\s*$")
SECTION = re.compile(r"^(\S+)\s+(mandrake\.\S+)(.*)$")      # deploy_custom_mods prints one per mod, drift or not
COMPOSED = re.compile(r"^\s*compose\s+(\S+)\s+(mandrake\.\S+)\s.*->\s*(\S+)\s*$")


WINDOWS_DIRS = ("/mnt/c/WINDOWS/system32", "/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0")


def windows_path(path):
    """`path` plus the Windows tools a live read needs (powershell.exe finds the game, tasklist/netstat measure it,
    python.exe reaches the bridge). The systemd unit's PATH has none of them, so from the tick every game read was None
    ("no running game") while the game ran: ten game-phase items held on the owner for it
    (RELENTLESS_LIVE_REPAIR_QUITS_BEFORE_THE_LOAD)."""
    have = path.split(os.pathsep) if path else []
    extra = [d for d in WINDOWS_DIRS + tuple(sorted(glob.glob("/mnt/c/Users/*/AppData/Local/Microsoft/WindowsApps")))
             if d not in have and os.path.isdir(d)]
    return os.pathsep.join(have + extra)


def live_rules(r):
    out = dict(DEFAULTS)
    out.update((r or {}).get("live") or {})
    return out


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


# ---------------------------------------------------------------- pure checks

sys.path.insert(0, HERE)
import model                                   # noqa: E402  the ledger's own cap and criterion line, not a copy

CUT_AT = model.CRITERION_TEXT_MAX
CRIT_LINE = model.CRITERION_LINE_RE


def whole_criterion(c, prose):
    """The ledger cuts a criterion's text at CUT_AT; the item's prose may hold the whole line. -> a copy with the
    whole text, or marked `cut` when the ledger copy is at the cap and no prose line extends it."""
    c, text = dict(c), c.get("text") or ""
    if len(text) < CUT_AT:
        return c
    for line in (prose or "").splitlines():
        m = CRIT_LINE.match(line)
        if m and m.group("cid") == c["id"] and m.group("level") == c["level"] and m.group("text").strip().startswith(text):
            c["text"] = m.group("text").strip()
            return c
        if m and m.group("cid") == c["id"]:
            c["retiered"] = True     # a line of that id says something else: the ledger holds an older criterion
    c["cut"] = True
    return c


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
    if crit[criterion].get("cut") and crit[criterion].get("retiered"):
        raise ValueError("%s %s is cut at %d chars on the ledger and the item's criteria now say something else under "
                         "that id (re-tiered): re-record them (`rimflow implemented --criteria-file`, the supervisor's "
                         "verb) before a proof can be judged" % (item["id"], criterion, CUT_AT))
    if crit[criterion].get("cut"):
        raise ValueError("%s %s is cut at %d chars on the ledger and no prose holds the rest: a proof cannot be judged "
                         "against a criterion nobody can read whole" % (item["id"], criterion, CUT_AT))
    if level not in LIVE_LEVELS:
        raise ValueError("%s %s is %s, not a live level (%s)" % (item["id"], criterion, level, ", ".join(LIVE_LEVELS)))
    return level, crit[criterion].get("text") or ""


def refused_proof(lr, title, text, proof):
    """-> why this run may not happen on the live game, or None."""
    for what, s in (("title", title), ("criterion", text), ("proof", proof)):
        m = re.search(lr["flyer_re"], s or "", re.I)
        if m:
            return "flyer: the %s names %r; a flyer's flight is never live-tested (standing ruling)" % (what, m.group(0))
    m = re.search(r"\$|`|\\\n|\beval\b|\{[^}]*,[^}]*\}", proof or "")     # expansion: bash builds the command at run time
    if m:
        return "the proof text builds its command at run time (%r): a gate cannot read what bash will run" % m.group(0)
    m = re.search(lr["forbid_re"], re.sub(r"[\'\"\\]", "", proof or ""))     # bash drops quotes: ap''ply is --apply
    if m:
        return "the proof would change the running game (%r): a load or a mutation is not this tier" % m.group(0)
    return None


def refused_site(site):
    """-> why a live-site command may not run, or None. Only live_site.py, plain arguments: the site step is the one
    change this tier makes to the game, so it is one reviewed tool, never a free command."""
    if site and not SITE_CMD.match(site.strip()):
        return "the live-site command %r is not `python.exe src/RimMandrake/Utils/live_site.py <plain args>`" % site[:200]
    return None


def cause(why):
    """An UNMEASURED why -> the key two runs share when the same thing stopped them: no paths, numbers or times."""
    w = re.sub(r"\([^()]*\.log\)|/\S+|\b\d[\d:.TZ-]*\b", "", why or "")
    return re.sub(r"\s+", " ", w).strip()[:120]


def repeats(rows, item_id, criterion, sha, key, game):
    """runs.jsonl rows -> how many of the newest rows for (item, criterion, sha), running back, are UNMEASURED on `key`
    on the same game. Any other outcome, cause or game ends the run."""
    n = 0
    for row in reversed(rows):
        if (row.get("item"), row.get("criterion"), row.get("sha")) != (item_id, criterion, sha):
            continue
        if row.get("outcome") != "UNMEASURED" or row.get("game") != game or (row.get("cause") or cause(row.get("why"))) != key:
            break
        n += 1
    return n


def wsl_rerun(proof, log_text):
    """-> the proof under python.exe when it is a plain `python3 <script>` that died on the WSL bridge refusal, else None."""
    if proof.startswith("python3 ") and any(s in (log_text or "") for s in WSL_BRIDGE):
        return "python.exe " + proof[len("python3 "):]
    return None


def last_line(path):
    """The last non-blank line of a log, cut to 200, or "" when it cannot be read."""
    lines = [x.strip() for x in read_text(path).splitlines() if x.strip()]
    return lines[-1][:200] if lines else ""


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def read_rows(path):
    """runs.jsonl -> its rows; a torn line is skipped."""
    out = []
    for line in read_text(path).splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def game_iso(fx):
    """The running game's start as the row's `game` key, or None when it cannot be read."""
    try:
        t = fx.game_started()
    except Exception:       # noqa: BLE001  a fake or a failing read: the key is only a grouping
        return None
    return iso(t) if t else None


def refused_deploy(deploy):
    """-> why the --deploy arguments may not run before the bridge is held, or None. They are a PLAN: anything that writes
    the game folder is another tier."""
    m = re.search(r"(^|\s)(--apply|--pull|--yes\S*|--force\S*)(\s|=|$)", re.sub(r"[\'\"\\]", "", deploy or ""))
    return "--deploy %r would write the game folder (%s): the plan only reads" % (deploy, m.group(2)) if m else None


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
    # a plan exits 1 when ANY mod drifts; that plan is still read, the drift that matters is this commit's files
    drift_only = plan_rc == 1 and plan_text.rstrip().endswith("Drift found. Re-run with --apply to deploy.")
    if plan_rc != 0 and not drift_only:
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
    for mod in sorted({m for m, _ in files}):      # a file this commit did not touch, in a mod it ships, may be the one it needs
        for section, flag, entry in drift:      # an untouched H file is held out of the game on purpose (DEPLOY_HOLD.txt)
            if flag != "H" and entry.lower().endswith((".xml", ".dll")) and (section == mod or entry.startswith(mod + "/")
                                                              or ("/%s/" % mod) in entry):
                return "%s has %s drift in the game folder (%s %s): the build is not what the game holds" % (
                    mod, "held" if flag == "H" else "out-of-date", section, entry)
    return None


def deployed_paths(mods_dir, mod, rel):
    """Where a mod file sits in the game folder: Mods/<Mod>/<rel>, or inside a composed mod, Mods/*/*/<Mod>/<rel>."""
    return [p for p in [os.path.join(mods_dir, mod, rel)] + glob.glob(os.path.join(glob.escape(mods_dir), "*", "*",
                                                                                     glob.escape(mod), glob.escape(rel)))
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
                "criteria": [whole_criterion(c, self.prose(it.id)) for c in it.criteria or []],
                "outstanding": list(it.outstanding or [])}

    def prose(self, item_id):
        """The item's prose, then its live_proofs/<ID>.criteria: the game mode adds its clauses to the ledger from that
        file (`rimflow implemented`), which cuts them at CUT_AT; the file still holds each whole line. Without it every
        long game clause read as cut and each round was REFUSED before the bridge (RELENTLESS_LIVE_REPAIR_QUITS_BEFORE_THE_LOAD)."""
        out = []
        for d in ("infrastructure/state/items", "infrastructure/state/items/closed"):
            p = os.path.join(self.books, d, item_id + ".md")
            if os.path.isfile(p):
                with open(p, encoding="utf-8", errors="replace") as f:
                    out.append(f.read())
                break
        p = os.path.join(self.books, "infrastructure/state/live_proofs", item_id + ".criteria")
        if os.path.isfile(p):
            with open(p, encoding="utf-8", errors="replace") as f:
                out.append(f.read())
        return "\n".join(out)

    def touched(self, sha):
        """Every path the built commit touched, including ones HEAD no longer has: changed_since sees those as changed."""
        return self._paths([], sha)

    def deleted(self, sha):
        """-> the paths the built commit DELETED: a stale game copy of one is still deployed and nothing else notices."""
        return self._paths(["--diff-filter=D"], sha)

    def _paths(self, extra, sha):
        """NUL-delimited, so a non-ASCII name is the real name and not git's quoted spelling. A merge is refused: its
        combined diff leaves out what only one parent changed."""
        r = subprocess.run(["git", "rev-list", "--parents", "-n", "1", sha], cwd=self.books, capture_output=True, text=True,
                           timeout=60, stdin=subprocess.DEVNULL)
        if r.returncode or not r.stdout.strip():
            raise ValueError("git rev-list %s: %s" % (sha, r.stderr[-200:]))
        if len(r.stdout.split()) > 2:
            raise ValueError("%s is a merge commit: its game files cannot be listed" % sha)
        r = subprocess.run(["git", "diff-tree", "-z", "--root", "--no-commit-id", "--name-only", "-r", *extra, sha],
                           cwd=self.books, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        if r.returncode:
            raise ValueError("git diff-tree %s: %s" % (sha, r.stderr[-200:]))
        return [p for p in r.stdout.split("\0") if p.strip()]

    def changed_since(self, sha, paths):
        """-> [(path, newest commit touching it after sha)] for each path whose bytes differ from sha's."""
        r = subprocess.run(["git", "diff", "-z", "--name-only", sha, "HEAD", "--", *paths], cwd=self.books,
                           capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        if r.returncode:
            raise ValueError("git diff %s: %s" % (sha, r.stderr[-200:]))
        out = []
        for p in (x for x in r.stdout.split("\0") if x.strip()):
            c = subprocess.run(["git", "log", "-1", "--format=%h", "%s..HEAD" % sha, "--", p], cwd=self.books,
                               capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
            out.append((p, c.stdout.strip() or "?"))
        return out

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
                                "Get-Process RimWorldWin64 -ErrorAction SilentlyContinue | ForEach-Object "
                                "{ $_.StartTime.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') }"],
                               capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL,
                               env=dict(os.environ, PATH=windows_path(os.environ.get("PATH", ""))))
            lines = [x.strip() for x in r.stdout.splitlines() if x.strip()]
            if len(lines) != 1:      # two games: the bridge may answer from either, so neither start time is the answer's
                return None
            return calendar.timegm(time.strptime(lines[0], "%Y-%m-%dT%H:%M:%SZ"))
        except (OSError, ValueError, subprocess.TimeoutExpired):
            return None

    def rimflow(self, *args, timeout=120):
        env = dict(os.environ, RIMFLOW_SEAT=self.seat, AGENT_SEAT=self.seat, CLAUDE_PROJECT_DIR=self.books)
        return subprocess.run(["python3", os.path.join(self.books, "src/RimMandrake/rimflow/cli.py"), *args],
                              cwd=self.books, env=env, capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)

    def running_load_gap(self, mods):
        """None when the RUNNING load holds every mod folder in `mods` (its packageId read from the deployed About.xml,
        checked against jawa/running_mods: the running load's own list, never ModsConfig.xml, which names the NEXT load);
        else why not. Asked with the bridge held, so the answer is the game the proof is about to read."""
        utils = os.path.join(os.path.dirname(HERE), "Utils")
        if utils not in sys.path:
            sys.path.insert(0, utils)
        import live_def_check
        want = {}
        for mod in sorted(set(mods)):
            try:
                with open(os.path.join(self.mods_dir, mod, "About", "About.xml"), encoding="utf-8-sig") as f:
                    text = f.read()
            except OSError:
                text = ""
            m = re.search(r"<packageId>\s*([^<\s]+)\s*</packageId>", text, re.I)
            if not m:
                return "not in the running load: %s has no readable packageId in its deployed About.xml" % mod
            want[mod] = m.group(1).lower()
            deps = re.search(r"<modDependencies>(.*?)</modDependencies>", text, re.S | re.I)   # its dependencies too
            for d in re.findall(r"<packageId>\s*([^<\s]+)\s*</packageId>", deps.group(1) if deps else "", re.I):
                want.setdefault("%s needs %s" % (mod, d.lower()), d.lower())
        running = live_def_check.call_running_mods(60)
        if running is None:
            return "the running load's mod list could not be read (jawa/running_mods)"
        lost = ["%s (%s)" % (m, p) for m, p in sorted(want.items()) if p not in running]
        return ("not in the running load: %s" % ", ".join(lost[:5])) if lost else None

    def full_list_gap(self):
        """None when the RUNNING load is the full-list tier (at least FULL_TIER_SHARE of FULL.LATEST's ids running); else
        why not, starting FINAL_WAIT. Whether it EQUALS the list is the final proof's own question, never this gate's."""
        utils = os.path.join(os.path.dirname(HERE), "Utils")
        if utils not in sys.path:
            sys.path.insert(0, utils)
        import live_def_check
        import modmanifest
        try:
            full = [i.lower() for i in modmanifest.read_modsconfig(FULL_LIST)]
        except Exception as e:      # noqa: BLE001  an unread list is no reason to call the game the full list
            return "%s: %s unreadable (%s)" % (FINAL_WAIT, os.path.basename(FULL_LIST), e)
        running = live_def_check.call_running_mods(60)
        if running is None:
            return "the running load's mod list could not be read (jawa/running_mods)"
        held = sum(1 for i in full if i in running)
        if held < FULL_TIER_SHARE * len(full):
            return "%s: the running game has %d mods, %d of FULL.LATEST's %d" % (FINAL_WAIT, len(running), held, len(full))
        return None

    def run_proof(self, proof, log, timeout):
        """-> the proof's exit code, or None when it outran `timeout`. Output goes to `log`."""
        with open(log, "w", encoding="utf-8") as f:
            f.write("$ %s\n" % proof)
            f.flush()
            p = subprocess.Popen(proof, shell=True, cwd=self.books, stdout=f, stderr=subprocess.STDOUT,
                                 stdin=subprocess.DEVNULL, executable="/bin/bash", start_new_session=True)
            try:
                return p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                f.write("\nTIMEOUT after %ds\n" % timeout)
                p.kill()
                p.wait()
                return None
            finally:
                try:
                    os.killpg(p.pid, signal.SIGKILL)       # the whole group, exit or timeout: no probe child outlives the release
                except OSError:
                    pass


def run(fx, root, item_id, criterion, proof, deploy, r, now=None, needs=(), site=None):
    """-> the run's row (also appended to <root>/live/runs.jsonl). row["outcome"] is PASS, FAIL, UNMEASURED or REFUSED.
    needs: mod folders the proof declares (live_proofs `live-mods:`) beyond the ones the built commit changed; with
    those, each one's About.xml modDependencies must be in the RUNNING load, or the row is UNMEASURED (restage), never
    run. A FINAL (GREEN-FULL) criterion also needs the full-list tier up: else UNMEASURED FINAL_WAIT, never run.
    site: the item's `live-site` command for this criterion (refused_site), run with the bridge held before the proof."""
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
    why = refused_deploy(deploy) or refused_site(site)
    if why:
        return done("REFUSED", why)
    if site:
        row["site"] = site
    try:
        gone = [p for p in fx.deleted(sha) if SRC_MOD.match(p) and fx.shippable(SRC_MOD.match(p).group(3))]
        if gone:
            return done("UNMEASURED", "the build deleted %s: a stale game copy cannot be told from the build" % ", ".join(gone[:5]))
        touched = fx.touched(sha)
        files = game_files(touched, fx.shippable)
        paths = [p for p in touched if SRC_MOD.match(p) and SRC_MOD.match(p).group(2, 3) in files]
        later = fx.changed_since(sha, paths) if paths else []
    except ValueError as e:
        return done("UNMEASURED", "cannot read the built commit: %s" % e)
    if later:
        # the game folder holds today's bytes; a verdict on them is not a verdict on the built sha
        return done("UNMEASURED", "changed since the built commit, so the game cannot run %s: %s" % (
            sha, ", ".join("%s (%s)" % pc for pc in later[:5])))
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
    else:
        stamps, started = [], None
    took = fx.rimflow("bridge", "take", "--idle-ok", "--for",
                      "relentless live test: %s %s (%s), read-only proof" % (item_id, criterion, level))
    if took.returncode != 0:
        return done("UNMEASURED", "bridge not taken: %s" % (took.stderr or took.stdout).strip()[-300:])
    log, n = None, 0
    while log is None or os.path.exists(log):      # a retry in the same second must not overwrite the evidence of the last
        log = os.path.join(root, "live", "%s-%s-%s%s.log" % (item_id, criterion, time.strftime("%Y%m%dT%H%M%SZ",
                                                              time.gmtime(now)), "" if not n else "-%d" % n))
        n += 1
    crashed = None
    try:
        if files and (started != fx.game_started() or stamps != [fx.mtime(m, rel) for m, rel in files]):
            crashed = "the game or its deployed files changed while the bridge was being taken"
            code = None
        else:
            # the build is deployed and older than the game, but the running list may not load its mod (or a mod it
            # declares, or their dependencies) at all (owner 2026-11-02: a game fits an item by its RUNNING mods, not
            # ModsConfig); a FINAL clause also needs the full-list tier. Asked with the bridge held, one read each.
            need = sorted({m for m, _ in files} | set(needs))
            crashed = (fx.running_load_gap(need) if need else None) or (fx.full_list_gap() if level == FINAL else None)
            code = None
        if crashed is None and code is None and site:
            slog = log[:-len(".log")] + "-site.log"
            row["site_log"] = slog
            sc = fx.run_proof(site, slog, lr["site_max_s"])
            if sc != 0:
                crashed = "site not prepared: %s" % (last_line(slog) or ("timed out" if sc is None else "exit %d" % sc))
        if crashed is None and code is None:
            code = fx.run_proof(proof, log, lr["proof_max_s"])
            again = wsl_rerun(proof, read_text(log)) if code not in (PASS, FAIL) else None
            if again:
                os.replace(log, log[:-len(".log")] + "-wsl.log")
                row["rerun"] = again
                code = fx.run_proof(again, log, lr["proof_max_s"])
            if code in (PASS, FAIL) and files and (started != fx.game_started()
                                                   or stamps != [fx.mtime(m, rel) for m, rel in files]):
                crashed, code = "the game or its deployed files changed while the proof ran", None
    except Exception as e:                          # the proof never ran to an exit code: no verdict, but the row stands
        crashed, code = "the proof could not run: %s: %s" % (type(e).__name__, str(e)[:200]), None
    finally:
        try:
            gave = fx.rimflow("bridge", "release", "--mine")
            row["released"], gave_why = gave.returncode == 0, (gave.stderr or gave.stdout).strip()[-200:]
        except Exception as e:                      # a timed-out release still leaves the row
            row["released"], gave_why = False, "%s: %s" % (type(e).__name__, str(e)[:150])
    if not row["released"]:
        return done("UNMEASURED", "the bridge release failed (%s), so no verdict is written" % gave_why, log=log)
    if code not in (PASS, FAIL):
        why = crashed or "the proof %s" % ("timed out" if code is None else "exited %d: it did not measure: %s"
                                           % (code, last_line(log)))
        if why.startswith(FINAL_WAIT):      # the expected state of a final clause on a small game: a row, no ledger note
            return done("UNMEASURED", why, log=log)
        game = iso(started) if started else game_iso(fx)
        key = cause(why)
        n = 1 + repeats(read_rows(os.path.join(root, "live", "runs.jsonl")), item_id, criterion, sha, key, game)
        row.update(game=game, repeat=n, cause=key)
        if n == lr["repeat_unmeasured"]:
            why = "%s: the same cause %d times on this game (%s): %s" % (RELOAD, n, game, why)
        elif n > 1:     # said once already, or the reload request stands: a row, no ledger note
            return done("UNMEASURED", why, log=log)
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
    p.add_argument("--site", default=None, help="a live_site.py command run, bridge held, before the proof")
    a = ap.parse_args(argv)
    with open(os.environ.get("RELENTLESS_RULES") or RULES, encoding="utf-8") as f:
        r = json.load(f)
    root = os.environ.get("RELENTLESS_ROOT") or "/home/mandrake/rm/relentless"
    row = run(Fx(seat=r.get("seat") or "BENCH"), root, a.item, a.criterion, a.proof, a.deploy, r, site=a.site)
    print(json.dumps(row, indent=1, sort_keys=True))
    return {"PASS": 0, "FAIL": 1}.get(row["outcome"], 2 if row["outcome"] == "UNMEASURED" else 3)


if __name__ == "__main__":
    sys.exit(main())
