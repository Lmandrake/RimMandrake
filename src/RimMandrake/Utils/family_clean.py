#!/usr/bin/env python3
r"""family_clean.py — expire the trash families that scratch_reap.py does not cover. Dry run by default.

scratch_reap.py covers ~/rm/scratch, ~/.seat-tmp, /tmp and landed orphan bundles. This tool covers the rest of the
places we write (scan: D:\ClaudeWork\rimmandrake\conductor\trash_scan_20261124.md). Each family has ONE rule: the
reader that would still want a unit, checked unit by unit, and the age line past which a unit with no reader goes.
Item: RIMMANDRAKE_EXTEND_CLEANER_TO_FAMILIES_NO_CLEANER_COVERS_265_GB_ON_D.

    family_clean.py                    dry run: each family's rows, with the reader that was checked
    family_clean.py --family transient  one family (repeat the flag for more)
    family_clean.py --all              print every row (default: units to remove one by one, kept units grouped)
    family_clean.py --json             machine-readable rows
    family_clean.py --apply            remove the REMOVE rows (each judged again just before its delete)
    family_clean.py check              0 the timer runs and its last --apply run is fresh and whole; 1 it is not

Families (age line: a unit whose newest mtime is younger stays YOUNG):
  transient    Transient/ of the seat clone, file by file, 14 d. Reader: a pin or tracked file (git check-ignore), any
               *.decisions.json (owner picks), a path that a live item or ledger evidence cites (transient_pin cited).
  saves        the Saves folder, by saves_prune.py's own rules (debug 72 h, backup 24 h). Reader: canonical guard
               (CANONICAL_SAVE.md), saves_awaiting_review.txt, a citation. The canonical saves are never listed.
  backups      D:\...\backups/*, 14 d.        Reader (every D: family): a live item of the unit's name, a citation
  codex_wsl    D:\...\codex_wsl/* and its */*-raw/saves_before_* backups, 14 d.   of its name in tracked files (not
  showings     D:\...\showings/*, 14 d.                                           the ledger, not closed items), a
  scratch      D:\...\scratch/* except save_keepers (save_guard's store), 14 d.   process whose cwd or command line
  kept_clones  D:\...\kept_clones/*, 14 d.                                        is in it, unlanded git work (a
  build        D:\...\build selftest stages (selftest_*, *SelfTest*, VV_*), 14 d; clone or a bundle), or a copy of a
               every other stage and tool dir stays: winbuild and the tools reuse.  canonical save the live one lacks.
  detached     D:\...\dispatcher/detached: KEPT. Reader: detached_helper.all_records (run history, spend, streaks).
  claude_projects  ~/.claude/projects: COVERED by Claude Code's own cleanupPeriodDays (default 30 d); measured here.

Verdicts: REMOVE (no reader, past the age line) · YOUNG · KEEP (a reader holds it) · REFUSE (unlanded work or a
canonical copy: judge by hand) · COVERED (another cleaner owns it) · UNMEASURED (could not look; never removed).
Env for tests: FAMILY_CLEAN_DATA (data root), FAMILY_CLEAN_REPOS (pathsep list of clones whose Transient/ is cleaned),
FAMILY_CLEAN_SAVES (Saves folder), FAMILY_CLEAN_CLAUDE (projects dir), FAMILY_CLEAN_STATE (state dir).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

DAY = 86400.0
AGE_D = 14.0
CLAUDE_AGE_D = 30.0
# danger: Claude Code's own cleanup stopped and transcripts pile up; measured residue past 30 d on 2026-11-25: 57 files, <0.1 GB
CLAUDE_RESIDUE_GB = 1.0
# danger: a timer that died leaves trash growing unseen; the timer is daily, so 30 h is one missed run plus slack
CHECK_MAX_AGE_H = 30.0
FAMILIES = ("transient", "saves", "backups", "codex_wsl", "showings", "scratch", "kept_clones", "build", "detached",
            "claude_projects")
# Hang guards: each stops one call that hangs, so the daily run does not stall for good (systemd starts no second run).
# budget: danger=a hung git call stalls the daily run; longest=25s (git grep -l, 2026-11-25)
HANG_GIT_S = 3600
# budget: danger=a hung du on D: stalls the run; longest=45s per backups child (trash scan 2026-11-24); a timeout leaves the size unknown
HANG_DU_S = 3600
# budget: danger=a hung saves_prune stalls the run; longest=100s (its citation search, saves_prune.py docstring)
HANG_SAVES_S = 3600
# budget: danger=a hung rm on D: stalls the run; longest=a few s (27 GB of bundles, 2026-11-25); a tree of many files is slower
HANG_RM_S = 7200
# budget: danger=a hung systemctl stalls check; longest=under 1s
HANG_SYSTEMCTL_S = 120
BUILD_SELFTEST = re.compile(r"(^selftest_|SelfTest|^VV_)")
PROTECTED = {"scratch": {"save_keepers": "save_guard's keeper store (saves_prune reports it; save_guard reads it)"}}
TRANSIENT_DIR = "Transient"


# ---------------------------------------------------------------- places
def data_root() -> Path:
    v = os.environ.get("FAMILY_CLEAN_DATA")
    if v:
        return Path(v)
    from rmpaths import rm_data_root
    return Path(rm_data_root())


def repos() -> list[Path]:
    v = os.environ.get("FAMILY_CLEAN_REPOS")
    if v is not None:
        return [Path(x) for x in v.split(os.pathsep) if x]
    return [Path("/home/mandrake/rm/bench")]


def saves_dir() -> Path:
    v = os.environ.get("FAMILY_CLEAN_SAVES")
    if v:
        return Path(v)
    from game_paths import SAVES
    return Path(SAVES)


def claude_dir() -> Path:
    return Path(os.environ.get("FAMILY_CLEAN_CLAUDE", str(Path.home() / ".claude" / "projects")))


def state_dir() -> Path:
    v = os.environ.get("FAMILY_CLEAN_STATE")
    return Path(v) if v else data_root() / "family_clean"


# ---------------------------------------------------------------- readers
def canonical_guard():
    """-> (names, starts) from CANONICAL_SAVE.md; raises canonical_saves.Unreadable when it cannot be read."""
    import canonical_saves
    return canonical_saves.read(str(ROOT))


def is_canonical(name: str, guard) -> bool:
    names, starts = guard
    i = name.lower().find(".rws")
    stem = name[:i] if i > 0 else name
    return stem in names or any(stem.startswith(s) for s in starts)


CORPUS = ["*.py", "*.sh", "*.ps1", "*.md", "*.yml", "*.yaml", "*.toml", "*.service", "*.timer",
          "src/RimMandrake/Utils/*.json", "src/RimMandrake/rimflow/*.json", "infrastructure/state/*.json",
          ":!infrastructure/state/ledger", ":!infrastructure/state/items/closed", ":!conversations", ":!Transient"]
RUN = re.compile(r"[\w.-]+")
SEP = re.compile(r"[.-]")


def tokens(text: str) -> set[str]:
    """Every string grep -w could match in text: each run of [A-Za-z0-9_.-], and each part of a run cut at its '.' and
    '-' (a non-word character is a word boundary, so `fw-drain` is found in `codex_wsl/fw-drain/x` and `fw` too)."""
    out: set[str] = set()
    for run in set(RUN.findall(text)):
        out.add(run)
        if "." in run or "-" in run:
            cuts = [0] + [m.end() for m in SEP.finditer(run)]
            ends = [m.start() for m in SEP.finditer(run)] + [len(run)]
            out.update(run[x:y] for x in cuts for y in ends if y > x)
    return out


class Readers:
    """The readers every D: unit is checked against, read once per run (live process state is read again before a
    delete)."""

    def __init__(self, names: list[str]):
        self.errors: list[str] = []
        self.live_items = {p.stem for p in (ROOT / "infrastructure" / "state" / "items").glob("*.md")}
        self.cites = self._cited(sorted({n for n in names if n}))
        self.procs = live_processes()
        try:
            self.guard = canonical_guard()
        except Exception as e:                       # noqa: BLE001 — could not look is named, never "no guard"
            self.guard = None
            self.errors.append("canonical guard unreadable: %s" % e)
        self._saves: set[str] | None = None

    def _cited(self, names: list[str]) -> dict[str, str]:
        """name -> the first file that names it, word-bounded (as grep -w): tracked code, docs, configs and live items,
        and the systemd user units. The ledger and closed items are log lines (a past mention is not a reader);
        conversations/ and Transient/ are output. `git grep -l` finds the files that name any name (~25 s); a token
        set per file then says which name (a `git grep -o` over the same files took 5 min, over the whole repo >50)."""
        hits: dict[str, str] = {}
        want = set(names)
        if not want:
            return hits
        cmd = ["git", "-C", str(ROOT), "grep", "-z", "-I", "-F", "-w", "-l", "-f", "-", "--"] + CORPUS
        try:
            r = subprocess.run(cmd, input="\n".join(sorted(want)) + "\n", capture_output=True, text=True,
                               timeout=HANG_GIT_S)
        except subprocess.TimeoutExpired:
            self.errors.append("citation search hung past %d s" % HANG_GIT_S)
            return hits
        if r.returncode not in (0, 1):
            self.errors.append("citation search exited %d: %s" % (r.returncode, (r.stderr or "").strip()[:200]))
            return hits
        files = [ROOT / f for f in r.stdout.split("\0") if f]
        units = Path.home() / ".config" / "systemd" / "user"
        files += sorted(units.glob("*.service")) if units.is_dir() else []
        for f in files:
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                self.errors.append("citation search could not read %s: %s" % (f, e))
                continue
            for n in tokens(text) & want:
                hits.setdefault(n, os.path.relpath(f, ROOT) if str(f).startswith(str(ROOT)) else str(f))
        return hits

    def live_saves(self) -> set[str] | None:
        """The file names in the live Saves folder; None when it cannot be listed."""
        if self._saves is None:
            try:
                self._saves = {e.name for e in os.scandir(saves_dir())}
            except OSError as e:
                self._saves = set()
                self.errors.append("Saves folder unreadable: %s" % e)
        return self._saves


def live_processes() -> list[tuple[str, str]]:
    """(cwd, command line) of every process we can read."""
    out = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            cwd = os.readlink("/proc/%s/cwd" % pid)
        except OSError:
            cwd = ""
        try:
            cmd = open("/proc/%s/cmdline" % pid, "rb").read().replace(b"\0", b" ").decode(errors="replace")
        except OSError:
            cmd = ""
        out.append((cwd, cmd))
    return out


def win_form(p: Path) -> str:
    s = str(p)
    m = re.match(r"^/mnt/([a-z])/(.*)$", s)
    return ("%s:\\%s" % (m.group(1).upper(), m.group(2).replace("/", "\\"))) if m else s


def process_in(p: Path, procs) -> str | None:
    s, w = str(p), win_form(p)
    for cwd, cmd in procs:
        if cwd == s or cwd.startswith(s + "/"):
            return "a process works in it (cwd %s)" % cwd
        if s in cmd or w in cmd:
            return "a process names it: %s" % cmd[:160]
    return None


# ---------------------------------------------------------------- measures
def newest_mtime(p: Path, depth: int = 2) -> float | None:
    """The newest mtime of p and of the entries down to `depth` levels; None when p cannot be read."""
    try:
        best = p.lstat().st_mtime
    except OSError:
        return None
    if depth <= 0 or not p.is_dir() or p.is_symlink():
        return best
    try:
        it = list(os.scandir(p))
    except OSError:
        return None
    for e in it:
        m = newest_mtime(Path(e.path), depth - 1)
        if m is None:
            return None
        best = max(best, m)
    return best


def size_of(p: Path) -> int | None:
    if p.is_file() or p.is_symlink():
        try:
            return p.lstat().st_size
        except OSError:
            return None
    try:
        r = subprocess.run(["du", "-sk", "--", str(p)], capture_output=True, text=True, timeout=HANG_DU_S)
    except subprocess.TimeoutExpired:
        return None
    try:
        return int(r.stdout.split()[0]) * 1024
    except (IndexError, ValueError):
        return None


def human(n) -> str:
    if n is None:
        return "?"
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return "%.0f %s" % (n, u) if u in ("B", "KB") else "%.1f %s" % (n, u)
        n /= 1024
    return "%.1f TB" % n


def walk_some(p: Path, depth: int):
    """Yield (path, is_dir) of entries under p down to depth (p itself first)."""
    yield p, p.is_dir()
    if depth <= 0 or not p.is_dir() or p.is_symlink():
        return
    try:
        it = list(os.scandir(p))
    except OSError:
        return
    for e in it:
        yield from walk_some(Path(e.path), depth - 1)


def git_work(p: Path) -> str | None:
    """A reason when p holds work that exists nowhere else: a clone with unlanded commits or dirty files (scratch_reap's
    judge), or a bundle whose heads are not on main. None when it holds none."""
    for q, is_dir in walk_some(p, 3):
        if is_dir and (q / ".git").exists():
            import scratch_reap
            st = scratch_reap.clone_state(q)
            if st["hard"] or st["soft"]:
                return "git clone %s: %s" % (q, (st["hard"] + st["soft"])[0])
        elif not is_dir and q.name.endswith(".bundle"):
            heads = bundle_heads(q)
            if heads is None:
                return "bundle %s: its heads cannot be read" % q
            lost = [h for h in heads if not on_main(h)]
            if lost:
                return "bundle %s: %d head(s) not on main (%s)" % (q, len(lost), lost[0][:12])
    return None


def bundle_heads(p: Path) -> list[str] | None:
    try:
        with open(p, "rb") as f:
            head = f.read(65536).split(b"\n\n", 1)[0].decode(errors="replace").splitlines()
    except OSError:
        return None
    if not head or not head[0].startswith("# v") or "git bundle" not in head[0]:
        return None
    return [ln.split()[0] for ln in head[1:] if ln and not ln.startswith(("-", "@")) and len(ln.split()[0]) == 40]


def on_main(sha: str) -> bool:
    r = subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", sha, "origin/main"], capture_output=True,
                       timeout=HANG_GIT_S)
    if r.returncode == 0:
        return True
    # a head that is a branch still on the remote is not lost either
    r = subprocess.run(["git", "-C", str(ROOT), "branch", "-r", "--contains", sha], capture_output=True, text=True,
                       timeout=HANG_GIT_S)
    return r.returncode == 0 and bool(r.stdout.strip())


def canonical_copy(p: Path, rd: Readers) -> str | None:
    """A reason when p holds a save of a guarded (canonical) name whose save the live Saves folder lacks: then p may
    hold its only copy. A copy (or a .bak of one) of a canonical save that the Saves folder holds is not its only copy:
    the live file is the canonical one (CANONICAL_SAVE.md)."""
    if rd.guard is None:
        return "canonical guard unreadable: could not look"
    for q, is_dir in walk_some(p, 3):
        n = q.name
        i = n.lower().find(".rws")
        if is_dir or i <= 0 or not is_canonical(n, rd.guard):
            continue
        if n[:i] + ".rws" not in rd.live_saves():
            return "holds %s, and the live Saves folder has no %s.rws" % (q, n[:i])
    return None


# ---------------------------------------------------------------- D: families
def d_units(family: str, root: Path) -> list[Path]:
    base = {"backups": root / "backups", "codex_wsl": root / "codex_wsl", "showings": root / "showings",
            "scratch": root / "scratch", "kept_clones": root / "kept_clones", "build": root / "build"}[family]
    try:
        kids = sorted(Path(e.path) for e in os.scandir(base))
    except FileNotFoundError:
        return []
    if family == "build":
        kids = [k for k in kids if BUILD_SELFTEST.search(k.name)]
    return kids


def inner_units(family: str, unit: Path) -> list[Path]:
    """Units judged inside a kept unit: codex_wsl's raw saves backups (saves_before_*)."""
    if family != "codex_wsl" or not unit.is_dir():
        return []
    out = []
    for raw in sorted(unit.glob("*-raw")):
        out += sorted(raw.glob("saves_before_*"))
    return out


def judge_unit(family: str, p: Path, rd: Readers, now: float) -> dict:
    row = {"family": family, "path": str(p), "verdict": None, "reader": None, "why": "", "age_d": None, "bytes": None}
    prot = PROTECTED.get(family, {}).get(p.name)
    if prot:
        row.update(verdict="KEEP", reader=prot, why="protected by the family rule")
        return row
    m = newest_mtime(p)
    if m is None:
        row.update(verdict="UNMEASURED", reader="could not look", why="its age cannot be read")
        return row
    row["age_d"] = round((now - m) / DAY, 1)
    checked = []
    if p.name in rd.live_items:
        row.update(verdict="KEEP", reader="the live item %s" % p.name)
        return row
    checked.append("no live item")
    if p.name in rd.cites:
        row.update(verdict="KEEP", reader="named by %s" % rd.cites[p.name])
        return row
    checked.append("no citation")
    pr = process_in(p, rd.procs)
    if pr:
        row.update(verdict="KEEP", reader=pr)
        return row
    checked.append("no process")
    if now - m < AGE_D * DAY:
        row.update(verdict="YOUNG", reader=", ".join(checked), why="newest %.1f d < %.0f d" % (row["age_d"], AGE_D))
        return row
    gw = git_work(p)
    if gw:
        row.update(verdict="REFUSE", reader=gw, why="unlanded work: judge by hand")
        return row
    checked.append("no unlanded git")
    cc = canonical_copy(p, rd)
    if cc:
        row.update(verdict="REFUSE", reader=cc, why="a canonical save copy: judge by hand")
        return row
    checked.append("no canonical copy")
    if rd.errors:                                  # a blind reader is never "no reader"
        row.update(verdict="UNMEASURED", reader="could not look: " + rd.errors[0], why="would be removed")
        return row
    row.update(verdict="REMOVE", reader=", ".join(checked), why="%.1f d old, no reader" % row["age_d"])
    return row


def judge_d_families(families: list[str], now: float) -> list[dict]:
    """Every unit of the D: families, judged against ONE reading of the readers (one citation search)."""
    root = data_root()
    units = {f: d_units(f, root) for f in families}
    names = []
    for f, us in units.items():
        for u in us:
            names += [u.name] + [q.name for q in inner_units(f, u)]
    rd = Readers(names)
    rows = []
    for f in families:
        for u in units[f]:
            r = judge_unit(f, u, rd, now)
            rows.append(r)
            if r["verdict"] == "KEEP":
                rows += [judge_unit(f, q, rd, now) for q in inner_units(f, u)]
        for e in rd.errors:
            rows.append({"family": f, "path": str(root), "verdict": "UNMEASURED", "reader": "could not look",
                         "why": e, "age_d": None, "bytes": None})
    return rows


# ---------------------------------------------------------------- transient
def transient_rows(now: float) -> list[dict]:
    rows = []
    for repo in repos():
        tdir = repo / TRANSIENT_DIR
        if not tdir.is_dir():
            rows.append({"family": "transient", "path": str(tdir), "verdict": "UNMEASURED", "reader": "could not look",
                         "why": "no Transient/ here", "age_d": None, "bytes": None})
            continue
        rows += transient_repo(repo, now)
    return rows


def transient_repo(repo: Path, now: float) -> list[dict]:
    tdir = repo / TRANSIENT_DIR
    files: list[tuple[str, float, int]] = []
    for dp, dns, fns in os.walk(tdir):
        dns[:] = [d for d in dns if d != ".git"]
        for fn in fns:
            fp = os.path.join(dp, fn)
            try:
                st = os.lstat(fp)
            except OSError:
                continue
            files.append((os.path.relpath(fp, repo), st.st_mtime, st.st_size))
    old = [f for f in files if now - f[1] >= AGE_D * DAY]
    # git check-ignore without --no-index: a tracked file is never "ignored", so a pin and a tracked file both read kept
    try:
        r = subprocess.run(["git", "-C", str(repo), "check-ignore", "--stdin", "-z"], capture_output=True,
                           input="\0".join(f[0] for f in old) + ("\0" if old else ""), text=True, timeout=HANG_GIT_S)
    except subprocess.TimeoutExpired:
        r = subprocess.CompletedProcess([], 124, "", "hung past %d s" % HANG_GIT_S)
    if r.returncode not in (0, 1):
        return [{"family": "transient", "path": str(tdir), "verdict": "UNMEASURED", "reader": "could not look",
                 "why": "git check-ignore exited %d: %s" % (r.returncode, r.stderr.strip()[:200]), "age_d": None,
                 "bytes": None}]
    ignored = set(x for x in r.stdout.split("\0") if x)
    os.environ["TRANSIENT_PIN_ROOT"] = str(repo)
    import transient_pin
    try:
        cited = [c.rstrip("/") for c in transient_pin.cited()]
    finally:
        os.environ.pop("TRANSIENT_PIN_ROOT", None)
    rows = []
    for rel, mt, sz in sorted(files):
        row = {"family": "transient", "path": str(repo / rel), "verdict": None, "reader": None, "why": "",
               "age_d": round((now - mt) / DAY, 1), "bytes": sz}
        if rel.endswith(".decisions.json"):
            row.update(verdict="KEEP", reader="owner picks (*.decisions.json stay)")
        elif now - mt < AGE_D * DAY:
            row.update(verdict="YOUNG", reader="age line", why="%.1f d < %.0f d" % (row["age_d"], AGE_D))
        elif rel not in ignored:
            row.update(verdict="KEEP", reader="pinned or tracked (Transient/.gitignore)")
        else:
            c = next((c for c in cited if rel == c or rel.startswith(c + "/")), None)
            if c:
                row.update(verdict="KEEP", reader="cited by a live item or ledger evidence: %s" % c)
            else:
                row.update(verdict="REMOVE", reader="not pinned, not tracked, not cited, not a decisions file",
                           why="%.1f d old" % row["age_d"])
        rows.append(row)
    return rows


# ---------------------------------------------------------------- saves
def saves_rows(apply: bool) -> list[dict]:
    env = dict(os.environ)
    if os.environ.get("FAMILY_CLEAN_SAVES"):
        env["SAVES_PRUNE_DIR"] = os.environ["FAMILY_CLEAN_SAVES"]
    cmd = [sys.executable, str(HERE / "saves_prune.py"), "--json"] + (["--apply"] if apply else [])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=HANG_SAVES_S)
    except subprocess.TimeoutExpired:
        r = subprocess.CompletedProcess(cmd, 124, "", "saves_prune hung past %d s" % HANG_SAVES_S)
    out = r.stdout
    i = out.find("{")
    try:
        data = json.loads(out[i:]) if i >= 0 else None
    except ValueError:
        data = None
    if r.returncode or not isinstance(data, dict):
        return [{"family": "saves", "path": str(saves_dir()), "verdict": "UNMEASURED", "reader": "could not look",
                 "why": "saves_prune exit %d: %s" % (r.returncode, (out[:i] if i > 0 else out + r.stderr).strip()[:300]),
                 "age_d": None, "bytes": None}]
    try:
        guard = canonical_guard()
    except Exception as e:                           # noqa: BLE001
        return [{"family": "saves", "path": str(saves_dir()), "verdict": "UNMEASURED", "reader": "could not look",
                 "why": "canonical guard unreadable: %s" % e, "age_d": None, "bytes": None}]
    rows, canon = [], 0
    for s in data.get("saves", []):
        if is_canonical(s["name"], guard):
            canon += 1                               # the canonical saves are never listed, whatever their verdict
            continue
        v = {"PRUNE": "REMOVE", "PRUNED": "REMOVED", "HOLD": "YOUNG" if s["why"].startswith("young") else "KEEP",
             "KEEP": "KEEP"}.get(s["verdict"], "UNMEASURED")
        rows.append({"family": "saves", "path": str(saves_dir() / s["name"]), "verdict": v, "reader": s["why"],
                     "why": "saves_prune.py", "age_d": s["age_d"], "bytes": s["bytes"]})
    rows.append({"family": "saves", "path": "(canonical saves)", "verdict": "KEEP", "reader": "CANONICAL_SAVE.md guard",
                 "why": "%d canonical saves, never listed by name" % canon, "age_d": None, "bytes": None})
    return rows


# ---------------------------------------------------------------- kept and covered families
def detached_rows() -> list[dict]:
    d = data_root() / "dispatcher" / "detached"
    try:
        n = sum(1 for _ in os.scandir(d))
    except OSError as e:
        return [{"family": "detached", "path": str(d), "verdict": "UNMEASURED", "reader": "could not look",
                 "why": str(e), "age_d": None, "bytes": None}]
    return [{"family": "detached", "path": str(d), "verdict": "KEEP",
             "reader": "detached_helper.all_records (maturation_dispatch, follow_through, left_open_continue, spend)",
             "why": "the run history; no age line: %d files" % n, "age_d": None, "bytes": None}]


def claude_rows(now: float) -> list[dict]:
    d = claude_dir()
    if not d.is_dir():
        return [{"family": "claude_projects", "path": str(d), "verdict": "UNMEASURED", "reader": "could not look",
                 "why": "not a directory", "age_d": None, "bytes": None}]
    n = old = 0
    old_b = 0
    for dp, _, fns in os.walk(d):
        for fn in fns:
            try:
                st = os.lstat(os.path.join(dp, fn))
            except OSError:
                continue
            n += 1
            if now - st.st_mtime >= CLAUDE_AGE_D * DAY:
                old += 1
                old_b += st.st_size
    covered = old_b < CLAUDE_RESIDUE_GB * 1024 ** 3
    return [{"family": "claude_projects", "path": str(d), "verdict": "COVERED" if covered else "UNMEASURED",
             "reader": "Claude Code (--resume) and the relevant-transcripts skill",
             "why": ("Claude Code's cleanupPeriodDays (default 30 d) removes old transcripts; %d files, %d past 30 d "
                     "(%s)" % (n, old, human(old_b))) + ("" if covered else ": OVER %.0f GB, its cleanup is not "
                                                          "running" % CLAUDE_RESIDUE_GB),
             "age_d": None, "bytes": old_b}]


# ---------------------------------------------------------------- run
def judge(families: list[str], apply_saves: bool = False) -> list[dict]:
    now = time.time()
    rows: list[dict] = []
    d_fams = [f for f in families if f in ("backups", "codex_wsl", "showings", "scratch", "kept_clones", "build")]
    for f in families:
        if f == "transient":
            rows += transient_rows(now)
        elif f == "saves":
            rows += saves_rows(apply_saves)
        elif f == "detached":
            rows += detached_rows()
        elif f == "claude_projects":
            rows += claude_rows(now)
    if d_fams:
        rows += judge_d_families(d_fams, now)
    return rows


def remove(row: dict) -> tuple[bool, str]:
    p = Path(row["path"])
    if row["family"] == "transient":
        try:
            p.unlink()
            return True, "removed"
        except OSError as e:
            return False, str(e)
    try:
        r = subprocess.run(["rm", "-rf", "--", str(p)], capture_output=True, text=True, timeout=HANG_RM_S)
    except subprocess.TimeoutExpired:
        return False, "rm hung past %d s (part may be gone)" % HANG_RM_S
    if r.returncode or p.exists():
        return False, "rm exit %d: %s" % (r.returncode, r.stderr.strip()[:200])
    return True, "removed"


def apply_rows(rows: list[dict], acts: Path) -> None:
    acts.parent.mkdir(parents=True, exist_ok=True)
    now = time.time()
    procs = live_processes()
    for row in rows:
        if row["verdict"] != "REMOVE" or row["family"] == "saves":
            continue
        p = Path(row["path"])
        # judged again just before the delete: its age and the processes in it
        if row["family"] == "transient":
            try:
                fresh = now - p.lstat().st_mtime < AGE_D * DAY
            except OSError:
                row.update(verdict="KEEP", why="vanished since the scan")
                continue
        else:
            m = newest_mtime(p)
            fresh = m is None or now - m < AGE_D * DAY
        held = process_in(p, procs)
        if fresh or held:
            row.update(verdict="KEEP", why="changed since the scan: %s" % (held or "touched"))
            continue
        if row["family"] != "transient" and row["bytes"] is None:
            row["bytes"] = size_of(p)
        ok, said = remove(row)
        row.update(verdict="REMOVED" if ok else "FAILED", why=said if not ok else row["why"])
        with open(acts, "a", encoding="utf-8") as f:
            f.write(json.dumps({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "family": row["family"],
                                "path": row["path"], "bytes": row["bytes"], "result": row["verdict"],
                                "reader": row["reader"], "why": row["why"]}) + "\n")
    for repo in repos():                         # empty dirs left in Transient/ by the removals
        tdir = repo / TRANSIENT_DIR
        for dp, dns, fns in os.walk(tdir, topdown=False):
            if dp != str(tdir) and not dns and not fns and ".git" not in dp:
                try:
                    os.rmdir(dp)
                except OSError:
                    pass


def summary(rows: list[dict], families: list[str]) -> dict:
    out = {}
    for f in families:
        fr = [r for r in rows if r["family"] == f]
        c: dict[str, int] = {}
        for r in fr:
            c[r["verdict"]] = c.get(r["verdict"], 0) + 1
        out[f] = {"rows": len(fr), "verdicts": c,
                  "remove_bytes": sum(r["bytes"] or 0 for r in fr if r["verdict"] in ("REMOVE", "REMOVED")),
                  "unsized": sum(1 for r in fr if r["verdict"] in ("REMOVE", "REMOVED") and r["bytes"] is None),
                  "unmeasured": [r["why"] for r in fr if r["verdict"] == "UNMEASURED"][:5]}
    return out


def print_rows(rows: list[dict], families: list[str], show_all: bool) -> None:
    for f in families:
        fr = [r for r in rows if r["family"] == f]
        print("== %s (%d rows)" % (f, len(fr)))
        if f == "transient" and not show_all:
            groups: dict[tuple, list] = {}
            for r in fr:
                rel = r["path"].split("/%s/" % TRANSIENT_DIR, 1)[-1].split("/", 1)[0]
                groups.setdefault((rel, r["verdict"], r["reader"]), []).append(r)
            for (top, v, rdr), rs in sorted(groups.items(), key=lambda kv: (kv[0][1] != "REMOVE", kv[0])):
                print("  %-8s %5d files %9s  Transient/%s  reader: %s" % (v, len(rs), human(sum(x["bytes"] or 0 for x in rs)),
                                                                          top, rdr))
            continue
        loud = [r for r in fr if show_all or r["verdict"] not in ("KEEP", "YOUNG")]
        for r in loud:
            age = "%6.1fd" % r["age_d"] if r["age_d"] is not None else "      -"
            print("  %-10s %9s %s  %s  reader: %s%s" % (r["verdict"], human(r["bytes"]) if r["bytes"] is not None else "",
                                                        age, r["path"], r["reader"], ("  (%s)" % r["why"]) if r["why"] else ""))
        if not show_all:
            quiet: dict[tuple, list] = {}
            for r in fr:
                if r["verdict"] in ("KEEP", "YOUNG"):
                    key = (r["verdict"], r["reader"] if r["verdict"] == "YOUNG" else r["reader"].split(":")[0][:70])
                    quiet.setdefault(key, []).append(r)
            for (v, rdr), rs in sorted(quiet.items()):
                ex = ", ".join(Path(x["path"]).name for x in rs[:3])
                print("  %-10s %4d units  reader: %s  (e.g. %s)" % (v, len(rs), rdr, ex))


def cmd_check() -> int:
    p = state_dir() / "last_run.json"
    try:
        lr = json.loads(p.read_text())
    except (OSError, ValueError) as e:
        print("FAILS: no readable last run at %s (%s)" % (p, e))
        return 1
    age_h = (time.time() - lr.get("at_epoch", 0)) / 3600
    bad = []
    if age_h > CHECK_MAX_AGE_H:
        bad.append("last run %.1f h old (line %.0f h)" % (age_h, CHECK_MAX_AGE_H))
    if not lr.get("apply"):
        bad.append("the last run was a dry run")
    missing = [f for f in FAMILIES if f not in lr.get("families", {})]
    if missing:
        bad.append("families not run: %s" % ", ".join(missing))
    blind = [f for f, s in lr.get("families", {}).items() if s.get("rows", 0) and
             s.get("verdicts", {}).get("UNMEASURED", 0) == s.get("rows")]
    if blind:
        bad.append("families wholly unmeasured: %s" % ", ".join(blind))
    if os.environ.get("FAMILY_CLEAN_SKIP_TIMER") != "1":
        r = subprocess.run(["systemctl", "--user", "is-enabled", "rm-family-clean.timer"], capture_output=True, text=True,
                           timeout=HANG_SYSTEMCTL_S)
        if r.stdout.strip() != "enabled":
            bad.append("rm-family-clean.timer is %s" % (r.stdout.strip() or "unknown"))
    if bad:
        print("FAILS: " + "; ".join(bad))
        return 1
    print("HOLDS: last --apply run %.1f h ago, %d families, removed %s" % (
        age_h, len(lr["families"]), human(sum(s.get("remove_bytes", 0) for s in lr["families"].values()))))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("verb", nargs="?", choices=("run", "check"), default="run")
    ap.add_argument("--family", action="append", choices=FAMILIES)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args(argv)
    if a.verb == "check":
        return cmd_check()
    fams = a.family or list(FAMILIES)
    t0 = time.time()
    rows = judge(fams, apply_saves=a.apply)
    if a.apply:
        apply_rows(rows, state_dir() / "acts.jsonl")
    summ = summary(rows, fams)
    if a.json:
        print(json.dumps({"rows": rows, "summary": summ}, indent=1))
    else:
        print_rows(rows, fams, a.all)
        print()
        for f, s in summ.items():
            print("%-16s %s; %s %s%s" % (f, ", ".join("%s %d" % kv for kv in sorted(s["verdicts"].items())) or "no rows",
                                        "removed" if a.apply else "would remove", human(s["remove_bytes"]),
                                        (" + %d unit(s) sized only at removal" % s["unsized"]) if s["unsized"] else ""))
        if not a.apply:
            print("(dry run: --apply removes the REMOVE rows)")
    if not a.family:          # a whole run is a reading; only an --apply run is the one the timer's promise reads
        sd = state_dir()
        sd.mkdir(parents=True, exist_ok=True)
        tmp = sd / "last_run.json.tmp"
        tmp.write_text(json.dumps({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "at_epoch": time.time(),
                                   "apply": a.apply, "seconds": round(time.time() - t0, 1), "families": summ}, indent=1))
        os.replace(tmp, sd / ("last_run.json" if a.apply else "last_dry_run.json"))
    return 2 if any(r["verdict"] == "FAILED" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
