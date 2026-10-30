#!/usr/bin/env python3
r"""arena_gate.py - the ONE gate every arm passes; run by the harness, never self-reported.

ARENA_GATE_BUILD_UNMEASURED_NEVER_PASSES; design/RimMandrake/architecture_switch_harness_2026-10-29.md §1.2 and §1.8,
testpilot_merged_2026-10-29.md §2.3. Usage:

    python3 src/RimMandrake/Utils/arena/arena_gate.py --task T --base <sha> --head <sha> --arm X [--repo DIR]

A SEPARATE process, run from the judge's own checkout (the script refuses to run from inside an arm clone,
`$ARENA_CLONES`), checks out `head` into a fresh clone under `<arena>/judge/gate_work/` and runs, in order:
  1 scope        every changed path inside the task's `area` (arm bookkeeping stripped first, not refused)
  2 placeholders non-empty diff; no TODO/FIXME/NotImplemented, no stub function (pass/.../raise NotImplementedError)
                 in changed code; no deleted selftest, no selftest def dropped
  3 tests        run_selftests.py --only <selftests of the changed paths + every selftest the diff added>
  4 xml          validate_patch.py --live <dump> --defs <Data, workshop, Mods> on changed Defs/Patches
  5 csharp       winbuild.py <mod> for each mod with a changed .cs
  6 deploy_plan  deploy_custom_mods.py --mod <m> (plan only); a plan naming a mod outside the area, or BLOCKING, fails
  7 proof        the task's own `proof` (each `python3 ...` segment; prose segments such as the held-back note are
                 the judge's business and are skipped; a proof with no runnable segment is UNMEASURED)
  8 live         live tasks only: records in the arm's SIGNED event log: canary (sha == head, verdict pass, detail
                 modcheck true) and live_release (verdict). A failed canary or a record for another sha is INVALID.
  9 test_record  a `test_start` for this sha from an agent id other than the builder's (build_end.detail.builder),
                 and a test_end verdict by that tester. No test_start refuses (FAIL).

Step results: PASS | FAIL | INVALID | UNMEASURED | NA (not applicable to this diff; NA is decided only from the diff).
A step that cannot run (missing tool, dump absent, timeout, unparsable output, tool edited by this very diff,
no signed log, no token) is UNMEASURED. UNMEASURED NEVER PASSES.
Overall verdict is exactly one of pass | fail | invalid:
  fail    any step FAIL;  else invalid   any step INVALID or UNMEASURED (the run is re-queued, the arm is not blamed);
  else pass  (every step PASS or NA, and steps 1, 2 and 9 are PASS).
NOT SELF-REPORTABLE: the result is a signed `gate` event appended through arena_eventlog.HarnessWriter (HMAC token
outside every arm-readable root) and a JSON record under `<arena>/judge/gate/`, which is outside them too. An arm
cannot sign a line, so a hand-written "gate pass" is rejected by verify(). An arm's edit of a gate instrument
(run_selftests/validate_patch/winbuild/deploy_custom_mods/arena_*) makes that tool's step UNMEASURED.
Output: one JSON record on stdout. Exit 0 only for `pass`.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import fnmatch
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arena_eventlog as L  # noqa: E402
import arena_tasks as A  # noqa: E402

PASS, FAIL, INVALID, UNMEASURED, NA = "PASS", "FAIL", "INVALID", "UNMEASURED", "NA"
VERDICTS = ("pass", "fail", "invalid")
STEPS = ("scope", "placeholders", "tests", "xml", "csharp", "deploy_plan", "proof", "live", "test_record")
MUST_PASS = ("scope", "placeholders", "test_record")
STEP_TIMEOUT = 480

ARM_BOOKKEEPING = ("*/AGENTS.md", "IMPLEMENTATION_PLAN.md", "fix_plan.md", "PLAN.md", "plan.md")
TOOLS = {                                   # relative to the clone; the arm may not have edited them
    "tests": "src/RimMandrake/Utils/run_selftests.py",
    "xml": "skills/rimworld-modding/scripts/validate_patch.py",
    "csharp": "src/RimMandrake/Utils/winbuild.py",
    "deploy_plan": "src/RimMandrake/Utils/deploy_custom_mods.py",
}
GAME = "/mnt/c/Program Files (x86)/Steam/steamapps"
DEFS_ROOTS = (GAME + "/common/RimWorld/Data", GAME + "/workshop/content/294100", GAME + "/common/RimWorld/Mods")
DUMP_DEFAULT = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump"
# built from parts so this file does not trip its own scan
PLACEHOLDER_RE = re.compile(r"\b(TO" + r"DO|FIX" + r"ME|XX" + r"X)\b|Not" + r"Implemented")
CODE_EXT = (".py", ".cs", ".xml", ".sh", ".json")
DEF_RE = re.compile(r"^\s*(?:def|async def)\s+(\w+)")


class GateError(Exception):
    pass


def step(status, why="", **extra):
    d = {"status": status, "why": why}
    d.update(extra)
    return d


def unmeasured(why, **extra):
    return step(UNMEASURED, why, **extra)


# ---------------------------------------------------------------- process / git helpers

def run(argv, cwd, log: Path, timeout=STEP_TIMEOUT, env=None):
    """-> (rc or None when it could not run / timed out, text). Always writes the log."""
    log.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, env=env,
                           errors="replace")
        text = "$ %s\n%s%s\n[rc=%s]\n" % (" ".join(shlex.quote(a) for a in argv), r.stdout, r.stderr, r.returncode)
        log.write_text(text, encoding="utf-8")
        return r.returncode, text
    except subprocess.TimeoutExpired:
        log.write_text("$ %s\n[TIMEOUT after %ss]\n" % (" ".join(argv), timeout), encoding="utf-8")
        return None, "timeout"
    except OSError as e:
        log.write_text("$ %s\n[cannot run: %s]\n" % (" ".join(argv), e), encoding="utf-8")
        return None, "cannot run: %s" % e


def git(repo: Path, *args, check=True) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=120, errors="replace")
    if check and r.returncode != 0:
        raise GateError("git %s: %s" % (" ".join(args), r.stderr.strip()[:200]))
    return r.stdout if r.returncode == 0 else ""


def is_bookkeeping(path: str) -> bool:
    return A.is_bookkeeping(path) or any(fnmatch.fnmatch(path, g) for g in ARM_BOOKKEEPING)


def in_area(path: str, area) -> bool:
    return any(fnmatch.fnmatch(path, g) or path == g for g in area)


# ---------------------------------------------------------------- the gate

class Gate:
    def __init__(self, task: dict, base: str, head: str, arm: str, repo: Path, p: dict, workdir: Path | None = None,
                 dump: str | None = None, defs_roots=DEFS_ROOTS, writer=None, run_id: str | None = None,
                 lane: str = "gate"):
        self.task, self.base, self.head, self.arm, self.repo, self.p = task, base, head, arm, Path(repo), p
        self.dump = dump if dump is not None else os.environ.get("ARENA_GATE_DUMP", DUMP_DEFAULT)
        self.defs_roots = tuple(defs_roots)
        self.writer, self.lane = writer, lane
        self.stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.run_id = run_id or "gate-%s-%s" % (task.get("id"), self.stamp)
        tag = "%s_%s_%s_%s" % (arm, task.get("id"), head[:12], self.stamp)
        self.logdir = p["root"] / "judge" / "gate" / tag
        self.work = Path(workdir) if workdir else p["root"] / "judge" / "gate_work" / tag
        self.clone = self.work / "co"
        self.files: list[dict] = []        # {"path","status"} after stripping bookkeeping
        self.stripped: list[str] = []
        self.results: dict = {}

    # ------------------------------------------------------------ checkout and diff
    def checkout(self):
        for sha in (self.base, self.head):
            if not re.fullmatch(r"[0-9a-fA-F]{7,40}", sha or ""):
                raise GateError("not a sha: %r" % (sha,))
        if self.work.exists():
            shutil.rmtree(self.work)
        self.work.mkdir(parents=True)
        subprocess.run(["git", "clone", "--quiet", "--no-checkout", str(self.repo), str(self.clone)],
                       capture_output=True, text=True, timeout=300, check=True)
        git(self.clone, "-c", "advice.detachedHead=false", "checkout", "--quiet", self.head)
        got = git(self.clone, "rev-parse", "HEAD").strip()
        if not got.startswith(self.head.lower()) and not self.head.lower().startswith(got[:len(self.head)]):
            raise GateError("checkout is %s, not head %s" % (got, self.head))
        self.head_full = got
        self.base_full = git(self.clone, "rev-parse", "--verify", self.base + "^{commit}").strip()
        out = git(self.clone, "diff", "--no-renames", "--name-status", self.base_full, self.head_full)
        for line in out.splitlines():
            st, _, path = line.partition("\t")
            if is_bookkeeping(path):
                self.stripped.append(path)
            else:
                self.files.append({"path": path, "status": st[:1]})

    def paths(self, *statuses):
        return [f["path"] for f in self.files if not statuses or f["status"] in statuses]

    def alive(self):
        return [f["path"] for f in self.files if f["status"] != "D"]

    def added_lines(self, path):
        """-> {lineno: text} of lines added in head for `path`."""
        out = git(self.clone, "diff", "--no-renames", "-U0", self.base_full, self.head_full, "--", path, check=False)
        res, ln = {}, 0
        for l in out.splitlines():
            m = re.match(r"@@ -\S+ \+(\d+)", l)
            if m:
                ln = int(m.group(1)); continue
            if l.startswith("+") and not l.startswith("+++"):
                res[ln] = l[1:]; ln += 1
        return res

    def removed_lines(self, path):
        out = git(self.clone, "diff", "--no-renames", "-U0", self.base_full, self.head_full, "--", path, check=False)
        return [l[1:] for l in out.splitlines() if l.startswith("-") and not l.startswith("---")]

    def tool_edited(self, key):
        return TOOLS[key] in self.paths()

    def tool_path(self, key):
        tp = self.clone / TOOLS[key]
        if self.tool_edited(key):
            return None, "the diff edits the instrument %s: it cannot judge itself" % TOOLS[key]
        if not tp.is_file():
            return None, "instrument %s is absent from the checkout" % TOOLS[key]
        return tp, ""

    # ------------------------------------------------------------ steps
    def s_scope(self):
        area = self.task.get("area") or []
        if not area:
            return unmeasured("task has no area")
        out = [f["path"] for f in self.files if not in_area(f["path"], area)]
        if out:
            return step(FAIL, "%d path(s) outside area" % len(out), outside=out[:20])
        return step(PASS, "%d path(s), all inside area; %d bookkeeping stripped" % (len(self.files), len(self.stripped)))

    def s_placeholders(self):
        if not self.files:
            return step(FAIL, "empty diff (nothing outside bookkeeping)")
        if not self.alive():
            return step(FAIL, "the diff only deletes files")
        bad = []
        for f in self.files:
            path, st = f["path"], f["status"]
            if A.is_selftest(path) and st == "D":
                bad.append("%s: selftest deleted" % path); continue
            if st == "D" or not path.endswith(CODE_EXT):
                continue
            added = self.added_lines(path)
            for ln, text in sorted(added.items()):
                if PLACEHOLDER_RE.search(text):
                    bad.append("%s:%d: %s" % (path, ln, text.strip()[:60]))
            if path.endswith(".py"):
                bad += self.stub_functions(path, added)
            if A.is_selftest(path) and st == "M":
                dropped = {m.group(1) for m in map(DEF_RE.match, self.removed_lines(path)) if m} - \
                    {m.group(1) for m in map(DEF_RE.match, added.values()) if m}
                bad += ["%s: selftest def %s dropped" % (path, d) for d in sorted(dropped)]
        if bad:
            return step(FAIL, "%d placeholder/empty/deleted-test finding(s)" % len(bad), findings=bad[:20])
        return step(PASS, "non-empty; no placeholder, stub or dropped test in %d file(s)" % len(self.alive()))

    def stub_functions(self, path, added):
        try:
            tree = ast.parse((self.clone / path).read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, ValueError, OSError):
            return ["%s: unparsable python" % path]
        out = []
        for n in ast.walk(tree):
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not any(n.lineno <= ln <= (n.end_lineno or n.lineno) for ln in added):
                continue
            body = list(n.body)
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                    and isinstance(body[0].value.value, str):
                body = body[1:]
            stub = not body or all(isinstance(b, ast.Pass) or (isinstance(b, ast.Expr) and isinstance(
                getattr(b, "value", None), ast.Constant) and b.value.value is Ellipsis) for b in body)
            if len(body) == 1 and isinstance(body[0], ast.Raise):
                src = ast.dump(body[0].exc) if body[0].exc is not None else ""
                stub = stub or "Not" + "ImplementedError" in src
            if stub:
                out.append("%s:%d: stub function %s" % (path, n.lineno, n.name))
        return out

    def selftests_for(self):
        """-> sorted selftest paths (existing in head): changed/added selftests + siblings of changed python."""
        tests = {f for f in self.alive() if A.is_selftest(f)}
        for f in self.alive():
            if f.endswith(".py") and not A.is_selftest(f):
                d, stem = (self.clone / f).parent, Path(f).stem
                for t in sorted(d.glob("selftest*.py")):
                    try:
                        txt = t.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        continue
                    if stem in t.name or re.search(r"\b(import|from)\s+%s\b" % re.escape(stem), txt):
                        tests.add(str(t.relative_to(self.clone)))
        return sorted(tests)

    def s_tests(self):
        changed_py = [f for f in self.alive() if f.endswith(".py")]
        tests = self.selftests_for()
        if not changed_py and not tests:
            return step(NA, "no python changed")
        if not tests:
            return unmeasured("python changed but no selftest maps to it", changed=changed_py[:10])
        tp, why = self.tool_path("tests")
        if tp is None:
            return unmeasured(why)
        rc, text = run([sys.executable, str(tp), "--no-cache", "--only", *tests], self.clone, self.logdir / "tests.log")
        if rc is None:
            return unmeasured("run_selftests could not run: " + text, log=str(self.logdir / "tests.log"))
        m = re.search(r"PASS (\d+)/(\d+)\s+FAIL (\d+)/\d+\s+UNMEASURED (\d+)/\d+\s+CRASH (\d+)/\d+\s+SKIPPED (\d+)/\d+", text)
        if not m:
            return unmeasured("run_selftests summary unparsable (rc=%s)" % rc, log=str(self.logdir / "tests.log"))
        ps, n, fl, um, cr, sk = map(int, m.groups())
        if n != len(tests):
            return unmeasured("ran %d test(s), asked for %d" % (n, len(tests)))
        if fl or cr:
            return step(FAIL, "%d FAIL, %d CRASH of %d" % (fl, cr, n), tests=tests)
        if um or sk or ps != n or rc != 0:
            return unmeasured("%d PASS of %d (UNMEASURED %d, SKIPPED %d, rc=%s)" % (ps, n, um, sk, rc), tests=tests)
        return step(PASS, "%d/%d selftests pass" % (ps, n), tests=tests)

    def s_xml(self):
        xml = [f for f in self.alive() if A.is_defxml(f)]
        if not xml:
            return NA_STEP("no Defs/Patches xml changed")
        tp, why = self.tool_path("xml")
        if tp is None:
            return unmeasured(why)
        if not Path(self.dump).is_dir():
            return unmeasured("--live dump %s is absent" % self.dump)
        argv = [sys.executable, str(tp), *xml, "--live", self.dump]
        for r in self.defs_roots:
            argv += ["--defs", r]
        rc, text = run(argv, self.clone, self.logdir / "xml.log")
        log = str(self.logdir / "xml.log")
        if rc is None:
            return unmeasured("validate_patch could not run: " + text, log=log)
        if rc == 0 and "UNMEASURED" not in text:
            return step(PASS, "validate_patch --live --defs clean on %d file(s)" % len(xml), log=log)
        if rc == 1:
            return step(FAIL, "validate_patch reported errors", log=log)
        return unmeasured("validate_patch rc=%s%s" % (rc, " with UNMEASURED in its output" if "UNMEASURED" in text else ""), log=log)

    def mods_changed(self, ext=None):
        return sorted({A._mod_of(f) for f in self.alive() if (ext is None or f.endswith(ext))} - {None})

    def s_csharp(self):
        mods = self.mods_changed(".cs")
        if not [f for f in self.alive() if f.endswith(".cs")]:
            return NA_STEP("no .cs changed")
        if not mods:
            return unmeasured(".cs changed outside src/RimMandrake/<mod>/")
        tp, why = self.tool_path("csharp")
        if tp is None:
            return unmeasured(why)
        res = {}
        for m in mods:
            log = self.logdir / ("csharp_%s.log" % m)
            rc, text = run([sys.executable, str(tp), m], self.clone, log)
            if rc is None:
                return unmeasured("winbuild could not run for %s: %s" % (m, text), log=str(log))
            if rc != 0 and re.search(r"dotnet\.exe not found|no such csproj|no csproj under|WINBUILD_DOTNET", text):
                return unmeasured("winbuild cannot run: " + text.strip().splitlines()[-2][:120], log=str(log))
            res[m] = rc
        bad = [m for m, rc in res.items() if rc != 0]
        if bad:
            return step(FAIL, "build failed: " + ", ".join(bad), log=str(self.logdir))
        return step(PASS, "built " + ", ".join(mods))

    def s_deploy_plan(self):
        mods = self.mods_changed()
        if not mods:
            return NA_STEP("no mod file changed")
        tp, why = self.tool_path("deploy_plan")
        if tp is None:
            return unmeasured(why)
        allowed = {A._mod_of(g.replace("*", "x")) for g in (self.task.get("area") or [])} - {None}
        seen = set()
        for m in mods:
            log = self.logdir / ("deploy_%s.log" % m)
            rc, text = run([sys.executable, str(tp), "--mod", m], self.clone, log)
            if rc is None:
                return unmeasured("deploy plan could not run for %s: %s" % (m, text), log=str(log))
            heads = re.findall(r"^(\S+)\s{2,}mandrake\.\S+", text, re.M)
            if not heads:
                return unmeasured("deploy plan for %s printed no mod section" % m, log=str(log))
            seen |= set(heads)
            if rc != 0 or "BLOCKING" in text:
                return step(FAIL, "deploy plan for %s is blocked (rc=%s)" % (m, rc), log=str(log))
        out = sorted(seen - allowed)
        if out:
            return step(FAIL, "plan touches mod(s) outside the task area: " + ", ".join(out))
        return step(PASS, "plan touches only " + ", ".join(sorted(seen)))

    def s_proof(self):
        proof = (self.task.get("proof") or "").strip()
        segs = [s.strip() for s in proof.split(" && ") if s.strip()]
        runnable = [s for s in segs if s.startswith("python3 ")]
        if not runnable:
            return unmeasured("task proof has no runnable `python3 ...` segment", proof=proof[:120])
        for i, s in enumerate(runnable):
            try:
                argv = shlex.split(s)
            except ValueError:
                return unmeasured("proof segment unparsable: " + s[:80])
            argv[0] = sys.executable
            log = self.logdir / ("proof_%d.log" % i)
            rc, text = run(argv, self.clone, log)
            if rc is None:
                return unmeasured("proof could not run: " + text, log=str(log))
            if rc != 0:
                return step(FAIL, "proof segment %d exited %s" % (i, rc), log=str(log))
        return step(PASS, "%d proof segment(s) exit 0" % len(runnable),
                    skipped_prose=[s for s in segs if s not in runnable])

    # ------------------------------------------------------------ signed-log steps
    def accepted(self):
        try:
            return L.verify(self.p, self.arm)["accepted"], ""
        except Exception as e:  # noqa: BLE001 - no token / unreadable log: the record cannot be judged
            return None, "signed event log unreadable: %s" % e

    def s_live(self, recs, why):
        if self.task.get("live", "none") == "none":
            return NA_STEP("task is live: none")
        if recs is None:
            return unmeasured(why)
        mine = [r for r in recs if r.get("task") == self.task["id"]]
        can = [r for r in mine if r["event"] == "canary"]
        if not can:
            return unmeasured("no signed canary record for this task")
        c = can[-1]
        d = c.get("detail") or {}
        cs = str(c.get("sha") or "")
        if not cs or not (self.head_full.startswith(cs) or cs.startswith(self.head_full)):
            return step(INVALID, "canary record is for sha %s, not head" % c.get("sha"))
        if c.get("verdict") != "pass":
            return step(INVALID, "canary %s: the run is re-queued, not failed" % c.get("verdict"), detail=d)
        if d.get("modcheck") is not True:
            return step(INVALID, "no modcheck recorded with this deploy")
        rel = [r for r in mine if r["event"] == "live_release" and r.get("sha") == c.get("sha")]
        if not rel:
            return unmeasured("canary passed but the lane recorded no live verdict")
        v = rel[-1].get("verdict")
        if v == "pass":
            return step(PASS, "live verdict pass, canary and modcheck recorded for head")
        if v == "fail":
            return step(FAIL, "live verdict fail")
        return unmeasured("live verdict %r is neither pass nor fail" % v)

    def s_test_record(self, recs, why):
        if recs is None:
            return unmeasured(why)
        t = self.task["id"]
        builds = [r for r in recs if r["event"] == "build_end" and r.get("task") == t and r.get("sha") == self.head_full]
        builder = ((builds[-1].get("detail") or {}).get("builder")) if builds else None
        if not builder:
            return unmeasured("no signed build_end (with builder) for head: the tester cannot be compared")
        starts = [r for r in recs if r["event"] == "test_start" and r.get("task") == t and r.get("sha") == self.head_full]
        if not starts:
            return step(FAIL, "no test_start for this sha: no different-agent test record")
        # the stamped rule is a convenience; recompute from the detail ids
        others = [r for r in starts if (r.get("detail") or {}).get("tester") not in (None, "", builder)]
        if not others:
            return step(FAIL, "every test_start is by the builder %r (or has no tester id)" % builder)
        testers = {(r.get("detail") or {}).get("tester") for r in others}
        ends = [r for r in recs if r["event"] == "test_end" and r.get("task") == t and r.get("sha") == self.head_full
                and (r.get("detail") or {}).get("tester") in testers]
        if not ends:
            return unmeasured("test_start by %s but no test_end yet" % ", ".join(sorted(testers)))
        v = ends[-1].get("verdict")
        if v == "pass":
            return step(PASS, "tester %s (builder %s) verdict pass" % ((ends[-1].get("detail") or {}).get("tester"), builder))
        if v == "fail":
            return step(FAIL, "different-agent tester verdict fail")
        return unmeasured("tester verdict %r" % v)

    # ------------------------------------------------------------ driver
    def execute(self) -> dict:
        self.logdir.mkdir(parents=True, exist_ok=True)
        try:
            self.checkout()
        except (GateError, subprocess.SubprocessError, OSError) as e:
            self.results = {s: unmeasured("no checkout: %s" % str(e)[:160]) for s in STEPS}
            return self.finish()
        recs, why = self.accepted()
        fns = {"scope": self.s_scope, "placeholders": self.s_placeholders, "tests": self.s_tests, "xml": self.s_xml,
               "csharp": self.s_csharp, "deploy_plan": self.s_deploy_plan, "proof": self.s_proof,
               "live": lambda: self.s_live(recs, why), "test_record": lambda: self.s_test_record(recs, why)}
        for s in STEPS:
            try:
                self.results[s] = fns[s]()
            except Exception as e:  # noqa: BLE001 - a step that crashed is UNMEASURED, never a pass
                self.results[s] = unmeasured("step crashed: %s: %s" % (type(e).__name__, str(e)[:160]))
        return self.finish()

    def finish(self) -> dict:
        return finish(self.results, self.task.get("id"), self.arm, self.base, self.head, self.logdir, self)


def NA_STEP(why):
    return step(NA, why)


def verdict_of(results: dict) -> str:
    """The whole rule in one place. UNMEASURED and missing steps can never produce `pass`."""
    st = {s: (results.get(s) or {}).get("status", UNMEASURED) for s in STEPS}
    if FAIL in st.values():
        return "fail"
    if INVALID in st.values() or UNMEASURED in st.values():
        return "invalid"
    if any(st[s] != PASS for s in MUST_PASS):
        return "invalid"
    return "pass"


def finish(results, task_id, arm, base, head, logdir, gate=None) -> dict:
    v = verdict_of(results)
    rec = {"verdict": v, "passed": v == "pass", "task": task_id, "arm": arm, "base": base, "head": head,
           "ts": L.now_ts(), "steps": {s: results.get(s) or unmeasured("step missing") for s in STEPS},
           "unmeasured": [s for s in STEPS if (results.get(s) or {}).get("status", UNMEASURED) == UNMEASURED],
           "log_dir": str(logdir), "recorded": False}
    if gate is not None:
        try:
            rec["record_file"] = str(logdir / "gate.json")
            (logdir / "gate.json").write_text(json.dumps(rec, indent=1, sort_keys=True), encoding="utf-8")
            w = gate.writer or L.HarnessWriter(gate.p)
            w.emit(arm, "gate", lane=gate.lane, run_id=gate.run_id, task=task_id, sha=head, verdict=v,
                   detail={"steps": {s: rec["steps"][s]["status"] for s in STEPS}, "log_dir": str(logdir)})
            rec["recorded"] = True
        except Exception as e:  # noqa: BLE001 - not signable: still report, say so, and never upgrade the verdict
            rec["record_error"] = str(e)[:200]
        if gate.work.exists():
            shutil.rmtree(gate.work, ignore_errors=True)
    return rec


def refuse_arm_location(file=__file__):
    clones = Path(os.environ.get("ARENA_CLONES", "/home/mandrake/rm/arena"))
    if A._inside(Path(file), clones):
        raise GateError("the gate is running from inside an arm clone (%s): the judge runs it from its own checkout"
                        % clones)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--task", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True)
    ap.add_argument("--arm", required=True)
    ap.add_argument("--repo", default=None, help="repo holding head (default: the arm's clone under $ARENA_CLONES, "
                                                 "else this checkout)")
    ap.add_argument("--lane", default="gate")
    a = ap.parse_args(argv)
    try:
        refuse_arm_location()
    except GateError as e:
        print(json.dumps({"verdict": "invalid", "passed": False, "error": str(e)}))
        return 2
    p = A.paths()
    clones = Path(os.environ.get("ARENA_CLONES", "/home/mandrake/rm/arena"))
    repo = Path(a.repo) if a.repo else (clones / a.arm if (clones / a.arm / ".git").exists() else A.REPO)
    try:
        task = A.load_frozen(a.task, p)
    except Exception as e:  # noqa: BLE001 - unfrozen/changed task: the gate cannot judge it
        rec = finish({s: unmeasured("task not loadable: %s" % str(e)[:160]) for s in STEPS}, a.task, a.arm, a.base,
                     a.head, p["root"] / "judge" / "gate" / "unloadable")
        print(json.dumps(rec, sort_keys=True))
        return 2
    rec = Gate(task, a.base, a.head, a.arm, repo, p, lane=a.lane).execute()
    print(json.dumps(rec, sort_keys=True))
    return 0 if rec["verdict"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
