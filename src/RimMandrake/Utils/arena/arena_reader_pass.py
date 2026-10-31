#!/usr/bin/env python3
"""arena_reader_pass.py — an independent reader judges every SCORED hidden check of every vetted survivor task
(ARENA_POOL_FIX_BUNDLED_WRONG_REASON).

A vet proves a hidden check fails at base and passes at the fix. It does not prove the check fails for the reason
the task text gives: a check bundled from a commit that did more than the task says, or one pinned to private names
or source text, fails at base for the wrong reason, and an arm that solves the task as written still fails it. So
a reader that is NOT the builder (GPT through gpt_consult.py, preferred; a fresh `claude -p` Opus call as the
fallback) reads, per task, a PACKET:

    the task text (prompt + criteria), each scored hidden check (type fix_test, as arena_judge.hidden_checks scores
    it) with its body and its failing output tail at base (from the vet cache), and a summary of the fix diff,

and answers two questions per scored check:

    (a) does the check test what the task text asks for, and could a correct solution written from the task text
        alone pass it?
    (b) is it implementation-coupled: private names, source-text anchors, file layout the task text does not name?

and a verdict per check: KEEP / UNSCORE_CHECK (this check is unfair, the task stands on its others) / DROP_TASK (the
task itself cannot be judged fairly), each with a reason. A KEEP is refused when (a) is no or (b) is yes.

RULES v2 (ARENA_READER_FIX_COUPLED_VETO_TOO_EAGER, ARENA_READER_FIX_KEEPS_THE_SELF_OVERWRITE; BENCH audit
D:\\ClaudeWork\\rimmandrake\\arena\\verify_reader\\audit.md). The agent works IN the repo checkout and may read it, so a
name that already exists in the repo at base is discoverable and is not coupling. Each check's packet therefore carries
its base-vs-hidden TEST DIFF (the reader judges the NEW assertions, not old lines the base file already had) and a
NAME LOOKUP over the identifiers on those new lines: at_base (exists at base outside the check file), fix_only (first
appears in the fix, outside the check file) and fix_only_unnamed (fix_only and not named in the task text). (b)
coupled now means: depends on names, text or layout INTRODUCED BY THE FIX or otherwise not discoverable at base. The
veto stays (a "solvable" answer is not always right: TRANSIENT_PIN). Three more refusals: self_overwrite (the requested
work lives in the check file itself, which the hidden copy overwrites: LSCRUB), partial_legs (the task asks for several
legs and the check tests only one: ARTPIPE), and brittle_format without format_stated (an exact output format the task
text does not state and the repo does not already use: TPS, TESTQ, SHADOW_INGEST). validate_reply enforces all of it:
a KEEP contradicting any answer, or listing a fix_only_unnamed name in coupled_names, is refused.

RULES v3 (ARENA_VET_REPAIR_IMPORT_ONLY_FAILS, ARENA_VET_REPAIR_TAIL_EATS_FAIL_LINES; BENCH re-vet
D:\\ClaudeWork\\rimmandrake\\arena\\verify_final2\\report.md: >= 55 of 210 discriminating checks were red at base only on a
missing module or name, 33 showed no reason at all). Each check's packet carries base_failure, read from the stored
base tail (the vet cache record; it is NOT recomputed, so a check vetted before the tail fix keeps its old 600-char
tail until it is re-vetted) plus the name lookup (and a lookup of any cited missing name the '+' lines missed). Its
veto is no_reason_visible (no traceback, *Error, FAIL, assert or compiler error in the tail: nothing proves the
check goes red for the defect) or missing_name_only (every failure is ModuleNotFound/ImportError/AttributeError/
NameError, or the C# kin, on a fix_only_unnamed name, with no behavioural failure beside it). A KEEP is refused when
the packet has a veto or the reader answers fails_for_defect false; such a check is UNSCORE_CHECK or DROP_TASK.

    run     read every survivor without a current verdict; one JSON file per task under the results dir (default
            <arena>/judge/reader/verdicts/, judge-only: the packets hold hidden check bodies). Resumable: a task
            whose verdict file matches its packet's sha256 is skipped; a changed packet (re-vet, new body) is
            STALE and read again. `--budget` stops starting new reads after that many seconds; rerun to continue.
            A task whose base tail is not in the vet cache is NOT READY and skipped (never read blind).
    apply   verdicts -> the reader exclusion file arena_trial.py build reads (default arena_trial.
            reader_exclusions_path(): <arena>/judge/reader/exclusions.json, schema arena_reader_exclusions/1):
            a task with a DROP_TASK check, or with no scored check left after its unscores, is in "drop"; a task
            with some UNSCORE_CHECK checks and at least one KEEP is in "unscore" {task: [check path]}. Refuses while
            any survivor has no current verdict, unless --partial (the file then lists them under "pending").
    packet  print one task's packet (what the reader sees).
    status  done / stale / pending / not-ready counts.
    warm    fill the name-lookup cache (<arena>/judge/reader/name_cache.jsonl) under --budget; resumable. Every
            other command builds every packet, so on a cold cache run `warm` until "0 left" first (each check costs
            up to two full-tree `git grep -P` passes, about 2 s each).

Usage:
    python3 src/RimMandrake/Utils/arena/arena_reader_pass.py warm [--budget 420]
    python3 src/RimMandrake/Utils/arena/arena_reader_pass.py status
    python3 src/RimMandrake/Utils/arena/arena_reader_pass.py run [--reader auto|gpt|claude] [--tasks ID ...]
        [--limit N] [--budget 420] [--force] [--results DIR]
    python3 src/RimMandrake/Utils/arena/arena_reader_pass.py apply [--out PATH] [--partial] [--results DIR]
    python3 src/RimMandrake/Utils/arena/arena_reader_pass.py packet RP_<ITEM>
"""
from __future__ import annotations

import argparse
import datetime as dt
import builtins
import difflib
import hashlib
import json
import keyword
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_tasks as A  # noqa: E402
import arena_trial as T  # noqa: E402

VERDICT_SCHEMA = "arena_reader_verdict/3"   # /3: rules v3 (see docstring); /1 and /2 verdicts read as pending
VERDICTS = ("KEEP", "UNSCORE_CHECK", "DROP_TASK")
BOOL_FIELDS = ("tests_task", "solvable_from_text", "coupled", "self_overwrite", "partial_legs", "brittle_format",
               "format_stated", "fails_for_defect")
SCORED_TYPE = "fix_test"                # arena_judge.hidden_checks scores exactly these
TAIL_CHARS = 3000
DIFF_CHARS = 8000
BODY_CHARS = 20000
TEST_DIFF_CHARS = 10000
MAX_NAMES = 200                        # identifiers looked up per check (new lines only)
NAME_CACHE = "name_cache.jsonl"         # beside the verdicts dir: lookups over immutable commits never go stale
READER_TIMEOUT = 360
GPT_CONSULT = HERE.parent / "gpt_consult.py"


class ReaderError(Exception):
    pass


# ---------------------------------------------------------------- paths

def results_dir(p=None) -> Path:
    return (p or A.paths())["freeze"].parent / "reader" / "verdicts"


def _write_atomic(path: Path, doc) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix="." + path.name + ".")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


# ---------------------------------------------------------------- packets

def survivors(p=None) -> list[str]:
    """Task ids with a task file AND a judge file holding at least one scored check, minus the committed pool
    exclusions (arena_tasks.load_pool_exclusions, by source item)."""
    p = p or A.paths()
    ex = A.load_pool_exclusions()
    out = []
    for f in sorted(Path(p["tasks"]).glob("*.json")):
        h = Path(p["judge"]) / f.name
        try:
            t = json.loads(f.read_text(encoding="utf-8"))
            hid = json.loads(h.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if t.get("source_item") in ex:
            continue
        if any(c.get("type") == SCORED_TYPE for c in hid.get("checks") or []):
            out.append(t["id"])
    return out


def _clip(s, n, tail=False):
    s = s or ""
    if len(s) <= n:
        return s
    return ("[... %d chars cut ...]\n" % (len(s) - n) + s[-n:]) if tail else (s[:n] + "\n[... %d chars cut ...]" % (len(s) - n))


def fix_diff_summary(repo, fix_sha, skip_paths=()) -> str:
    """`git show --stat` of the fix plus its diff outside the hidden check files, clipped to DIFF_CHARS."""
    if not fix_sha:
        return "(no fix sha recorded)"
    def g(*a):
        r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, timeout=60)
        return r.stdout if r.returncode == 0 else "(git %s failed: %s)" % (a[0], r.stderr.strip()[:200])
    stat = g("show", "--stat", "--format=%H%n%s%n", fix_sha)
    excl = [":(exclude)" + s for s in skip_paths]
    diff = g("show", "--format=", "-U2", fix_sha, "--", ".", *excl)
    return stat.rstrip() + "\n\n" + _clip(diff, DIFF_CHARS)


def _git_out(repo, *a, timeout=180):
    r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout


def base_file(repo, base_sha, path):
    """The check file as it stood at base, or None when the fix created it."""
    if not base_sha:
        return None
    rc, out = _git_out(repo, "show", "%s:%s" % (base_sha, path), timeout=60)
    return out if rc == 0 else None


def test_diff(base_body, body, path) -> str:
    """Unified diff base -> hidden copy. '+' lines are what the fix ADDED to the check: the reader judges those."""
    a = (base_body or "").splitlines(keepends=True)
    b = (body or "").splitlines(keepends=True)
    d = "".join(difflib.unified_diff(a, b, "a/" + path if base_body is not None else "/dev/null", "b/" + path, n=2))
    return d or "(no difference: the hidden copy equals the base file)"


_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_CODE_POS = re.compile(r"(?:\.\s*([A-Za-z_]\w*))|(?:([A-Za-z_]\w*)\s*\()|(?:\b(?:import|from)\s+([A-Za-z_][\w.]*))")
_SKIP = set(keyword.kwlist) | set(dir(builtins)) | {"self", "cls", "true", "false", "null", "None", "True", "False"}


def new_line_names(diff_text) -> list[str]:
    """Identifiers on the ADDED lines of a test diff that look like code: anything with an underscore, a digit or a
    case change (snake/camel/CONST), plus any word in call, attribute or import position. Sorted, capped."""
    names = set()
    for ln in (diff_text or "").splitlines():
        if not ln.startswith("+") or ln.startswith("+++"):
            continue
        s = ln[1:]
        for tok in _IDENT.findall(s):
            if len(tok) >= 3 and ("_" in tok.strip("_") or any(ch.isdigit() for ch in tok)
                                  or (tok != tok.lower() and tok != tok.capitalize())):
                names.add(tok)
        for m in _CODE_POS.finditer(s):
            for g in m.groups():
                if g:
                    names.update(x for x in g.split(".") if x)
    return sorted(n for n in names if n not in _SKIP and len(n) >= 3)[:MAX_NAMES]


_DEFINED = re.compile(r"(?:\b(?:def|class|void|bool|int|string|var|static)\s+([A-Za-z_]\w*))|(?:^\s*([A-Za-z_]\w*)\s*=[^=])",
                      re.M)


def defined_in(body) -> set:
    """Names the check body defines itself (def/class/typed declaration/top-of-line assignment): they travel with the
    hidden copy, so they are never coupling and are not looked up (an absent name costs a full-tree grep)."""
    return {g for m in _DEFINED.finditer(body or "") for g in m.groups() if g}


def _grep_names(repo, sha, names, exclude_path) -> set:
    """Which of `names` occur as whole words anywhere in the tree at `sha`, outside `exclude_path`, or as the stem of
    a file or directory name there (a module name is discoverable from the layout)."""
    if not sha or not names:
        return set()
    found = set()
    rc, tree = _git_out(repo, "ls-tree", "-r", "-t", "--name-only", sha)
    if rc == 0:
        found |= {Path(x).stem for x in tree.splitlines() if x != exclude_path} & set(names)
    # ONE PCRE pass per commit: `git grep -o -P '\b(?:a|b|...)\b'` over the whole tree takes ~2 s here. Measured on
    # one real task (9 names, 38.8k files): -F -w -o with many -e took 45 s, -q per name ~1.6 s each.
    rest = sorted(n for n in names if n not in found and _IDENT.fullmatch(n))
    if not rest:
        return found
    pat = r"\b(?:" + "|".join(rest) + r")\b"
    pr = subprocess.Popen(["git", "-C", str(repo), "grep", "-o", "-h", "-I", "-P", pat, sha, "--", ".",
                           ":(exclude)" + exclude_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    want = set(rest)
    try:
        for ln in pr.stdout:              # streamed: a common name prints 10^5 lines, none of them kept
            found.add(ln.strip())
            if want <= found:
                break
    finally:
        if pr.poll() is None:
            pr.kill()
        pr.stdout.close()
        err = pr.stderr.read()
        pr.stderr.close()
        rc = pr.wait()
    if not want <= found and rc not in (0, 1):
        raise ReaderError("git grep -P at %s failed (exit %d): %s" % (sha[:10], rc, err.strip()[:200]))
    return found & set(names)


def _cache_read(cache):
    out = {}
    if cache and Path(cache).is_file():
        for ln in Path(cache).read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(ln)
                out[r["k"]] = r["v"]
            except (ValueError, KeyError, TypeError):
                continue
    return out


def name_lookup(repo, base_sha, fix_sha, path, names, task_text, cache=None, _mem={}) -> dict:
    """{at_base, fix_only, fix_only_unnamed}: where each new-line identifier is discoverable. A name at base outside
    the check file is something an agent working in the repo can read; a fix_only name it has to invent, which is
    fair only when the task text names it (fix_only_unnamed is the residue)."""
    key = hashlib.sha256(json.dumps([str(repo), base_sha, fix_sha, path, names]).encode()).hexdigest()
    if cache is not None and str(cache) not in _mem:
        _mem[str(cache)] = _cache_read(cache)
    store = _mem.setdefault(str(cache), {})
    if key not in store:
        at_base = _grep_names(repo, base_sha, names, path)
        in_fix = _grep_names(repo, fix_sha, [n for n in names if n not in at_base], path)
        store[key] = {"at_base": sorted(at_base), "fix_only": sorted(in_fix)}
        if cache is not None:
            Path(cache).parent.mkdir(parents=True, exist_ok=True)
            with open(cache, "a", encoding="utf-8") as f:
                f.write(json.dumps({"k": key, "v": store[key]}) + "\n")
    v = dict(store[key])
    words = set(_IDENT.findall(task_text or ""))
    v["fix_only_unnamed"] = [n for n in v["fix_only"] if n not in words]
    return v


# RULES v3 (ARENA_VET_REPAIR_IMPORT_ONLY_FAILS): what the base output says about WHY the check failed there.
_MISSING_NAME = [re.compile(p) for p in (
    r"No module named '([\w.]+)'",                                   # ModuleNotFoundError
    r"cannot import name '(\w+)'",                                   # ImportError
    r"has no attribute '(\w+)'",                                     # AttributeError
    r"\bname '(\w+)' is not defined",                                # NameError
    r"error CS0103: The name '(\w+)' does not exist",                # C#
    r"error CS0117: '[\w.]+' does not contain a definition for '(\w+)'",
    r"error CS1061: '[\w.<>]+' does not contain a definition for '(\w+)'",
    r"error CS0246: The type or namespace name '(\w+)' could not be found",
    r"error CS0234: The type or namespace name '(\w+)' does not exist")]
_REASON = re.compile(r"Traceback \(most recent call last\)|\b[A-Z]\w*(?:Error|Exception)\b|\bFAIL|\bassert\b"
                     r"|\berror [A-Z]{2,}\d+:|\bnot ok\b|\bexpected\b")
_BEHAVIOUR = re.compile(r"AssertionError|\bassert\b|\bFAIL\b(?!ED \()|\bexpected\b|\bnot ok\b")


def missing_names_cited(tail) -> list[str]:
    """Names the base output reports as missing (no module / cannot import / no attribute / not defined / C# CS0103
    and kin); a dotted module contributes its last part (the part that is absent)."""
    out = set()
    for rx in _MISSING_NAME:
        for m in rx.finditer(tail or ""):
            out.add(m.group(1).split(".")[-1])
    return sorted(out)


def base_failure(tail, names: dict, extra: dict | None = None) -> dict:
    """Why the check is red at base, read from its stored base tail plus the name lookups. veto:
    no_reason_visible  the tail shows no failure reason at all (no traceback, *Error, FAIL, assert, compiler
                       error): nothing proves the check goes red for the defect, so it may not be KEPT;
    missing_name_only  every failure line is a missing module/name that the FIX introduced and the task text does
                       not name (fix_only_unnamed), with no behavioural failure line beside it: the check is red at
                       base for the missing name, not the defect, and pins the fix's private API."""
    tail = tail or ""
    cited = missing_names_cited(tail)
    unnamed = set((names or {}).get("fix_only_unnamed") or []) | set((extra or {}).get("fix_only_unnamed") or [])
    fix_missing = [n for n in cited if n in unnamed]
    behaviour = [ln for ln in tail.splitlines()
                 if _BEHAVIOUR.search(ln) and not any(rx.search(ln) for rx in _MISSING_NAME)]
    visible = bool(_REASON.search(tail))
    veto = ("no_reason_visible" if not visible else
            "missing_name_only" if fix_missing and not behaviour else None)
    return {"reason_visible": visible, "missing_names": cited, "missing_fix_only_unnamed": fix_missing,
            "behaviour_lines": len(behaviour), "veto": veto}


def build_packet(task_id, p=None, repo=None, vet=None, cache=None) -> dict:
    """The reader's whole input for one task. `vet` {vet key: record} (default: the judge's vet cache). `cache` the
    name-lookup cache file (default beside the verdicts dir; False disables it)."""
    p = p or A.paths()
    repo = repo or A.REPO
    t = json.loads((Path(p["tasks"]) / (task_id + ".json")).read_text(encoding="utf-8"))
    hid = json.loads((Path(p["judge"]) / (task_id + ".json")).read_text(encoding="utf-8"))
    vet = A.read_vet_cache(A.vet_cache_path(p)) if vet is None else vet
    if cache is None:
        cache = results_dir(p).parent / NAME_CACHE
    fix_sha = hid.get("fix_sha")
    base_sha = t.get("base_sha") or hid.get("base_sha") or (fix_sha + "^" if fix_sha else None)
    task_text = (t.get("prompt") or "") + "\n" + (t.get("criteria") or "")
    checks, missing = [], []
    for c in hid.get("checks") or []:
        if c.get("type") != SCORED_TYPE:
            continue
        rec = vet.get((c.get("vet") or {}).get("key") or "")
        tail = rec.get("base_tail") if rec else None
        if tail is None:
            missing.append(c["path"])
        old = base_file(repo, base_sha, c["path"])
        td = test_diff(old, c.get("body"), c["path"])
        local = defined_in(c.get("body"))
        looked = [n for n in new_line_names(td) if n not in local]
        names = name_lookup(repo, base_sha, fix_sha, c["path"], looked, task_text, cache or None)
        # a missing name the base output cites but the '+' lines did not yield (e.g. a module imported by a helper)
        # gets its own lookup, so the missing_name_only veto never rests on a name nobody looked up
        extra_names = sorted(n for n in missing_names_cited(tail) if n not in looked and n not in local)
        extra = (name_lookup(repo, base_sha, fix_sha, c["path"], extra_names, task_text, cache or None)
                 if extra_names and tail is not None else None)
        checks.append({"path": c["path"], "command": c.get("command"), "body": _clip(c.get("body"), BODY_CHARS),
                       "base_result": (rec or {}).get("base_result"),
                       "base_tail": _clip(tail, TAIL_CHARS, tail=True) if tail is not None else None,
                       "new_file": old is None, "test_diff": _clip(td, TEST_DIFF_CHARS),
                       "check_named_in_task": Path(c["path"]).name in task_text or c["path"] in task_text,
                       "names": names, **({"cited_names": extra} if extra is not None else {}),
                       "base_failure": base_failure(tail, names, extra) if tail is not None else None})
    return {"task": task_id, "prompt": t.get("prompt"), "criteria": t.get("criteria"), "kind": t.get("kind"),
            "fix_diff": fix_diff_summary(repo, fix_sha, [c["path"] for c in checks]),
            "checks": checks, "missing_tails": missing}


def packet_sha(packet: dict) -> str:
    return hashlib.sha256(json.dumps(packet, sort_keys=True).encode("utf-8")).hexdigest()


def _bf_line(bf) -> str:
    if not bf:
        return "(no base output recorded)"
    return ("reason_visible: %s; missing names cited: %s; of them fix_only_unnamed: %s; behavioural failure lines: "
            "%d; veto: %s" % (bf.get("reason_visible"), json.dumps(bf.get("missing_names") or []),
                              json.dumps(bf.get("missing_fix_only_unnamed") or []), bf.get("behaviour_lines") or 0,
                              bf.get("veto") or "none") +
            {"no_reason_visible": " (KEEP forbidden: nothing shows it red for the defect)",
             "missing_name_only": " (KEEP forbidden: red at base only on a fix-introduced unnamed name)"}
            .get(bf.get("veto"), ""))


def render_prompt(packet: dict) -> str:
    paths = [c["path"] for c in packet["checks"]]
    parts = [
        "You are an independent reader auditing a coding benchmark. An agent is given the TASK TEXT below and a "
        "checkout of the repository at base, which it may read freely, and must change that repository so that "
        "hidden checks pass. Each hidden check below was taken from the real fix commit; it fails before the fix and "
        "passes after it. Before it runs, the hidden copy of the check file REPLACES the agent's copy of that path. "
        "Your job: decide whether each check is a FAIR test of the task text.",
        "", "Each check comes with its TEST DIFF (base file -> hidden copy; a new file is all '+'). Judge the NEW "
        "('+') assertions: old lines the base file already had were passing before and are not the task's. It also "
        "comes with a NAME LOOKUP over the identifiers on the new lines: at_base names already exist in the repo at "
        "base (outside the check file), so an agent working in the repo can find them; fix_only names first appear "
        "in the real fix; fix_only_unnamed are fix_only names the task text never mentions.",
        "", "For EACH check answer:",
        "(a) tests_task: does the check test what the task text asks for? solvable_from_text: could a correct "
        "solution written from the task text by a developer working in that repo (reading its code, but without "
        "seeing the real fix) pass it?",
        "(b) coupled: does the check depend on names, exact text or file layout INTRODUCED BY THE FIX (fix_only_"
        "unnamed names, a new message string, a new file path) or otherwise not discoverable in the repo at base, "
        "that the task text does not name? Names listed at_base, and names the task text gives, are NOT coupling. "
        "List the coupling names in coupled_names (empty when coupled is false).",
        "(c) self_overwrite: does the task ask for work INSIDE the check file itself (e.g. fix or extend this test "
        "or its fakes)? The hidden copy overwrites that file, so the agent's work there is never scored; only the "
        "rest of the fix is. check_named_in_task in the packet says whether the task text names the check file.",
        "(d) partial_legs: does the task ask for several parts (legs, call sites, clauses, files) while the check "
        "tests only one of them, so a fix of that one leg passes and the rest goes unscored?",
        "(e) brittle_format: does the check pin an exact output format (wording, number/units format, list order, "
        "stream such as stderr vs stdout) where other correct outputs exist? format_stated: is that exact format "
        "given in the task text, or already the repo's convention at base (the same form is used for the same kind "
        "of output elsewhere)? A brittle format that is neither is UNSCORE_CHECK (or DROP_TASK), never KEEP.",
        "(f) fails_for_defect: does the output at base show the check going red FOR THE DEFECT the task describes? "
        "It is false when the base output shows no failure reason at all, or when it is red only because a module "
        "or name the fix introduced (and the task text does not name) is missing (ModuleNotFoundError, ImportError, "
        "AttributeError, NameError, a C# 'does not exist' error): that proves the name was absent, not the defect. "
        "Each check's BASE FAILURE line gives the mechanical reading; a veto there forbids KEEP.",
        "Then a verdict: KEEP (fair), UNSCORE_CHECK (unfair; the task can still be judged on its other checks), or "
        "DROP_TASK (the task text cannot be judged fairly at all). KEEP is only allowed when tests_task and "
        "solvable_from_text are true, coupled, self_overwrite and partial_legs are false, and brittle_format is "
        "false or format_stated is true, and fails_for_defect is true. A 'solvable' answer is not enough on its own: if the new assertions need a "
        "name the fix invented and the task text does not give, that is coupling. Give a one or two sentence reason.",
        "", "Reply with ONE JSON object and nothing else:",
        '{"checks": [{"path": "<check path>", "tests_task": true|false, "solvable_from_text": true|false, '
        '"coupled": true|false, "coupled_names": ["..."], "self_overwrite": true|false, "partial_legs": true|false, '
        '"brittle_format": true|false, "format_stated": true|false, "fails_for_defect": true|false, "verdict": "KEEP|UNSCORE_CHECK|DROP_TASK", '
        '"reason": "..."}]}',
        "with exactly one entry for each of these paths: " + json.dumps(paths),
        "", "=== TASK TEXT (prompt) ===", packet.get("prompt") or "",
        "", "=== TASK CRITERIA ===", packet.get("criteria") or "",
        "", "=== FIX DIFF SUMMARY (the real fix; the agent never sees it) ===", packet["fix_diff"]]
    for i, c in enumerate(packet["checks"]):
        nm = c.get("names") or {}
        parts += ["", "=== CHECK %d: %s ===" % (i + 1, c["path"]), "command: %s" % (c.get("command") or ""),
                  "new file (absent at base): %s; check_named_in_task: %s" % (c.get("new_file"),
                                                                              c.get("check_named_in_task")),
                  "--- test diff (base -> hidden copy; judge the '+' lines) ---",
                  "(new file: every line of the full body below is new)" if c.get("new_file")
                  else (c.get("test_diff") or ""),
                  "--- name lookup (identifiers on the '+' lines) ---",
                  "at_base: " + json.dumps(nm.get("at_base") or []),
                  "fix_only: " + json.dumps(nm.get("fix_only") or []),
                  "fix_only_unnamed: " + json.dumps(nm.get("fix_only_unnamed") or []),
                  "--- full body (hidden copy) ---", c.get("body") or "",
                  "--- BASE FAILURE (mechanical reading of the base output) ---", _bf_line(c.get("base_failure")),
                  "--- output at base (before the fix; result %s), tail ---" % c.get("base_result"),
                  c.get("base_tail") or ""]
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------- readers

def _extract_json(text: str):
    s = (text or "").strip()
    dec = json.JSONDecoder()
    i = s.find("{")
    while i >= 0:
        try:
            obj, _ = dec.raw_decode(s, i)
            if isinstance(obj, dict) and "checks" in obj:
                return obj
        except ValueError:
            pass
        i = s.find("{", i + 1)
    raise ReaderError("no JSON object with \"checks\" in the reply (%d chars)" % len(s))


def gpt_reader(prompt: str, timeout=READER_TIMEOUT) -> str:
    with tempfile.TemporaryDirectory(prefix="reader_gpt_") as d:
        pf, of = Path(d, "prompt.md"), Path(d, "answer.md")
        pf.write_text(prompt, encoding="utf-8")
        r = subprocess.run([sys.executable, str(GPT_CONSULT), "--prompt-file", str(pf), "--out", str(of),
                            "--lockdown", "--timeout", str(timeout)],
                           capture_output=True, text=True, timeout=timeout + 60)
        if r.returncode != 0 or not of.is_file():
            raise ReaderError("gpt_consult exit %d: %s" % (r.returncode, (r.stderr or "")[-300:]))
        return of.read_text(encoding="utf-8")


def claude_reader(prompt: str, timeout=READER_TIMEOUT) -> str:
    with tempfile.TemporaryDirectory(prefix="reader_claude_") as d:
        r = subprocess.run(["claude", "-p", "--model", "opus", "--tools", "", "--no-session-persistence",
                            "--strict-mcp-config"], input=prompt, capture_output=True, text=True, cwd=d,
                           timeout=timeout)
        if r.returncode != 0 or not r.stdout.strip():
            raise ReaderError("claude -p exit %d: %s" % (r.returncode, (r.stderr or "")[-300:]))
        return r.stdout


def make_reader(kind: str, gpt=None, claude=None):
    """-> callable(prompt) -> (reply text, reader name). auto: GPT, then claude -p on a GPT failure."""
    gpt, claude = gpt or gpt_reader, claude or claude_reader
    if kind == "gpt":
        return lambda pr: (gpt(pr), "gpt")
    if kind == "claude":
        return lambda pr: (claude(pr), "claude-opus")
    if kind != "auto":
        raise ReaderError("unknown reader %r" % kind)

    def auto(pr):
        try:
            return gpt(pr), "gpt"
        except (ReaderError, OSError, subprocess.SubprocessError) as e:
            return claude(pr), "claude-opus (gpt failed: %s)" % str(e)[:120]
    return auto


# ---------------------------------------------------------------- verdicts

def validate_reply(reply: dict, packet: dict) -> list[dict]:
    """The reader's per-check rows, checked against the packet; raises ReaderError (no verdict is written)."""
    want = [c["path"] for c in packet["checks"]]
    by_path = {c["path"]: c for c in packet["checks"]}
    rows = reply.get("checks")
    if not isinstance(rows, list):
        raise ReaderError("checks is not a list")
    seen, out = set(), []
    for r in rows:
        if not isinstance(r, dict) or r.get("path") not in want or r["path"] in seen:
            raise ReaderError("unknown or repeated check %r" % (r.get("path") if isinstance(r, dict) else r))
        seen.add(r["path"])
        for k in BOOL_FIELDS:
            if not isinstance(r.get(k), bool):
                raise ReaderError("%s: %s is not a bool" % (r["path"], k))
        if r.get("verdict") not in VERDICTS:
            raise ReaderError("%s: verdict %r" % (r["path"], r.get("verdict")))
        if not (isinstance(r.get("reason"), str) and r["reason"].strip()):
            raise ReaderError("%s: no reason" % r["path"])
        names = r.get("coupled_names") or []
        names = [str(x) for x in names] if isinstance(names, list) else []
        if r["verdict"] == "KEEP":
            bad = [k for k in ("tests_task", "solvable_from_text", "fails_for_defect") if not r[k]] + \
                  [k for k in ("coupled", "self_overwrite", "partial_legs") if r[k]] + \
                  (["brittle_format without format_stated"] if r["brittle_format"] and not r["format_stated"] else [])
            if bad:
                raise ReaderError("%s: KEEP contradicts its own answers (%s)" % (r["path"], ", ".join(bad)))
            # rules v3: the base output must show the check red for the defect; a packet veto is final. A check with
            # no base_failure reading (built before v3, or no tail) cannot be KEPT either: no proof is no KEEP.
            bf = by_path[r["path"]].get("base_failure")
            if not bf:
                raise ReaderError("%s: KEEP without a base_failure reading in the packet" % r["path"])
            if bf.get("veto"):
                raise ReaderError("%s: KEEP vetoed by the base output (%s%s)" % (
                    r["path"], bf["veto"], (": " + ", ".join(bf.get("missing_fix_only_unnamed") or []))
                    if bf["veto"] == "missing_name_only" else ""))
            # the veto stays in code: a KEEP may not cite as coupling a name the fix invented and the task never gave
            unnamed = set(((by_path[r["path"]].get("names") or {}).get("fix_only_unnamed")) or [])
            hit = sorted(unnamed & set(names))
            if hit:
                raise ReaderError("%s: KEEP while coupled_names holds fix-introduced unnamed %s" % (r["path"], hit))
        out.append({"path": r["path"], **{k: r[k] for k in BOOL_FIELDS}, "coupled_names": names,
                    "verdict": r["verdict"], "reason": r["reason"].strip()})
    if seen != set(want):
        raise ReaderError("no verdict for %s" % sorted(set(want) - seen))
    return out


def task_verdict(rows: list[dict]) -> tuple[str, str, list]:
    """-> (task verdict, reason, [unscored paths]). DROP_TASK if any check says so or no scored check is kept."""
    drops = [r for r in rows if r["verdict"] == "DROP_TASK"]
    un = [r["path"] for r in rows if r["verdict"] == "UNSCORE_CHECK"]
    if drops:
        return "DROP_TASK", "; ".join("%s: %s" % (r["path"], r["reason"]) for r in drops), []
    if un and len(un) == len(rows):
        return "DROP_TASK", "no scored check left (all %d unscored)" % len(un), []
    if un:
        return "UNSCORE_CHECK", "%d of %d checks unscored" % (len(un), len(rows)), un
    return "KEEP", "every scored check kept", []


def read_verdict(path: Path):
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) and d.get("schema") == VERDICT_SCHEMA else None


def state(p=None, results=None, repo=None, vet=None) -> dict:
    """{task: (status, packet, verdict-or-None)}; status done / stale / pending / not_ready."""
    p = p or A.paths()
    results = Path(results or results_dir(p))
    vet = A.read_vet_cache(A.vet_cache_path(p)) if vet is None else vet
    out = {}
    for tid in survivors(p):
        pk = build_packet(tid, p, repo, vet)
        v = read_verdict(results / (tid + ".json"))
        if pk["missing_tails"]:
            st = "not_ready"
        elif v is None:
            st = "pending"
        elif v.get("packet_sha256") != packet_sha(pk):
            st = "stale"
        else:
            st = "done"
        out[tid] = (st, pk, v)
    return out


def run(reader, p=None, results=None, repo=None, tasks=None, limit=None, budget=None, force=False, vet=None,
        log=print) -> dict:
    """Read every task that is not done; -> counts. `reader` callable(prompt) -> (text, name)."""
    p = p or A.paths()
    results = Path(results or results_dir(p))
    st = state(p, results, repo, vet)
    if tasks:
        unknown = sorted(set(tasks) - set(st))
        if unknown:
            raise ReaderError("not survivors: %s" % unknown)
    counts = {"read": 0, "skipped_done": 0, "not_ready": 0, "errors": 0, "left": 0}
    t0 = time.monotonic()
    for tid in sorted(st):
        if tasks and tid not in tasks:
            continue
        s, pk, _ = st[tid]
        if s == "not_ready":
            counts["not_ready"] += 1
            continue
        if s == "done" and not force:
            counts["skipped_done"] += 1
            continue
        if (limit is not None and counts["read"] + counts["errors"] >= limit) or \
                (budget is not None and time.monotonic() - t0 > budget):
            counts["left"] += 1
            continue
        try:
            text, name = reader(render_prompt(pk))
            rows = validate_reply(_extract_json(text), pk)
        except (ReaderError, OSError, subprocess.SubprocessError) as e:
            counts["errors"] += 1
            log("ERROR %s: %s" % (tid, e))
            continue
        tv, why, un = task_verdict(rows)
        _write_atomic(results / (tid + ".json"), {
            "schema": VERDICT_SCHEMA, "task": tid, "packet_sha256": packet_sha(pk), "reader": name,
            "at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "checks": rows, "task_verdict": tv, "reason": why, "unscore": un})
        counts["read"] += 1
        log("%-13s %s (%s)" % (tv, tid, name))
    return counts


def apply(p=None, results=None, out=None, partial=False, repo=None, vet=None) -> dict:
    """Verdicts -> the reader exclusion document (written to `out`, default arena_trial.reader_exclusions_path)."""
    p = p or A.paths()
    st = state(p, results, repo, vet)
    pending = sorted(t for t, (s, _, _) in st.items() if s != "done")
    if pending and not partial:
        raise ReaderError("%d survivor(s) have no current verdict (pending/stale/not ready), e.g. %s; run first or "
                          "pass --partial" % (len(pending), pending[:5]))
    drop, unscore, keep = {}, {}, []
    for tid, (s, _, v) in sorted(st.items()):
        if s != "done":
            continue
        tv, why, un = task_verdict(v["checks"])        # recomputed: the file's own summary is not trusted
        if tv == "DROP_TASK":
            drop[tid] = "reader: " + why
        elif tv == "UNSCORE_CHECK":
            unscore[tid] = un
        else:
            keep.append(tid)
    doc = {"schema": T.READER_SCHEMA, "drop": drop, "unscore": unscore, "keep": keep, "pending": pending,
           "made_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "verdicts": str(Path(results or results_dir(p)))}
    _write_atomic(Path(out or T.reader_exclusions_path(p)), doc)
    return doc


def warm(p=None, repo=None, budget=None, log=print) -> dict:
    """Fill the name-lookup cache task by task (each lookup is appended as it lands) so status/run/apply, which build
    every packet, stay fast. Resumable: a warm task costs nothing. Stops starting tasks after `budget` seconds."""
    p = p or A.paths()
    vet = A.read_vet_cache(A.vet_cache_path(p))
    t0, done, left = time.monotonic(), 0, 0
    for tid in survivors(p):
        if budget is not None and time.monotonic() - t0 > budget:
            left += 1
            continue
        build_packet(tid, p, repo, vet)
        done += 1
    log("warm: %d task(s) built, %d left (%.0fs)" % (done, left, time.monotonic() - t0))
    return {"built": done, "left": left}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "apply", "status", "packet", "warm"):
        s = sub.add_parser(name)
        s.add_argument("--results", help="verdicts dir (default <arena>/judge/reader/verdicts)")
        if name == "warm":
            s.add_argument("--budget", type=float, default=420.0, help="start no new task after this many seconds")
        if name == "run":
            s.add_argument("--reader", default="auto", choices=("auto", "gpt", "claude"))
            s.add_argument("--tasks", nargs="+")
            s.add_argument("--limit", type=int)
            s.add_argument("--budget", type=float, default=420.0, help="start no new read after this many seconds")
            s.add_argument("--force", action="store_true", help="re-read tasks already done")
        if name == "apply":
            s.add_argument("--out", help="exclusion file (default arena_trial.reader_exclusions_path())")
            s.add_argument("--partial", action="store_true")
        if name == "packet":
            s.add_argument("task")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "run":
            print(json.dumps(run(make_reader(a.reader), results=a.results, tasks=a.tasks, limit=a.limit,
                                 budget=a.budget, force=a.force)))
        elif a.cmd == "apply":
            d = apply(results=a.results, out=a.out, partial=a.partial)
            print(json.dumps({k: len(d[k]) for k in ("drop", "unscore", "keep", "pending")}))
        elif a.cmd == "warm":
            print(json.dumps(warm(budget=a.budget, log=lambda s: print(s, file=sys.stderr))))
        elif a.cmd == "status":
            c = {}
            for s, _, _ in state(results=a.results).values():
                c[s] = c.get(s, 0) + 1
            print(json.dumps(c))
        else:
            print(render_prompt(build_packet(a.task)))
    except (ReaderError, A.ArenaError, OSError, ValueError) as e:
        print("arena_reader_pass: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
