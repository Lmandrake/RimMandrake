#!/usr/bin/env python3
"""relentless_wall.py - what a mode may not see, as data, and the Marker's walled packet.

Design: relentless_agent_design_2026-11-01.md section 8. The profile lives in run_rules.json `walls`. A profile
with enforce false changes no launch: `audit` reports what it would have denied, from the runs' own tool calls.
The wall stops accident, not a hostile worker on the same host.

The Marker runs in a box: an exported tree with no .git, the supervisor's diff, a verdict script that writes only into
the box, and its own transcript folder bound over the real one. Its env carries no store root.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import time
from pathlib import Path

from checker_box import (  # noqa: E402,F401
    BOX_CONFIG, GIT_COPY_MAX, GIT_GRANT, GIT_NOTE, GRANTS, HIDDEN, HOME, ITEMS, ITEM_GRANT, ITEM_NOTE, UNIT_TMP,
    VERDICT_SCRIPT, _ABSENT, _SAFE, _carve, _copy_objects, _link, _object_chain, _snapshot, box_config,
    box_path_prepend, change_range, default_grants, denied, excludes, git_reads, grant_git, grant_items,
    item_rev, make_box, profile, props, read_always, readonly, remove_box, skill_targets, tmp_env, unit_env,
    unit_path,)

from weak_reading import (  # noqa: E402,F401
    _LETS, _STRONG, acted_weak, names_strong, narrow_word,)
WORDS = ("PASS", "WEAK", "FAIL", "UNMEASURED")
UNMEASURED = "UNMEASURED"   # CHECKER_SANDBOX_FIX_BLIND_TO_STEVE: the box could not reach the evidence; no work goes back
REACH_TAG = "CANNOT REACH:"
RULE = (   # both Marker prompts: the unwalled and the walled one must never differ in what the words mean
    "Decide one thing: did this commit do what the item says, proven by running it? Run the proof yourself. Judge "
    "the contract against the item's words: a contract that is easier than the item is a FAIL. A proof that "
    "cannot run because of the commit is a FAIL. Do not fix anything, do not push, do not touch the ledger.",
    "One case is not a FAIL: the work holds and only the proof is short. If you think a clause is unproven or the "
    "contract skipped it, run that clause yourself against the code. Your run shows the clause is done: that is WEAK. "
    "Your run shows it is not done, or you can reach all it needs and still cannot show it either way: that is FAIL.",
    "Being unable to measure is not a FAIL. If the work may be done but what would show it is out of your box's reach - "
    "another machine (ssh, Tailscale), a path this box hides (D:\\ClaudeWork, /mnt/d/ClaudeWork/rimmandrake come up empty "
    "here but for the paths the prompt lists as bound read only), the live game, a Windows program that cannot start here - say UNMEASURED and begin the reasons with "
    "'CANNOT REACH:', naming each thing and the command that showed you cannot reach it, then what you did check. It sends "
    "no work back: the box goes up for repair. A proof that runs and is red is FAIL; a clause you can reach is never UNMEASURED.",
    "Keep the two apart when you record the verdict: each wrong thing your own run showed goes in its own --defect (a wrong "
    "number, a red test, a crash, a clause not done), each piece of evidence you could not reach goes in its own --unreached. "
    "Any --defect makes the verdict FAIL, whatever you could not reach; --unreached and no --defect is UNMEASURED, never PASS.",
    "Begin every --defect with its cause (CHECKER_VERDICT_BUILD_CAUSE_BEFORE_RETURN): 'product:' the commit's own change or "
    "behaviour is wrong - name the changed file or the proof command that shows it, and add one --control saying how you "
    "showed your instrument can see (it goes green on a known-good case, or catches a fault you put in); 'measurement:' "
    "the proof or contract is wrong. This includes demonstrated incompatible acceptance demands. Quote the demands, "
    "explain the incompatibility, and state the clarification needed to make passing attainable. 'environment:' the machine, the disk, the game "
    "load, a remote host, the account; 'unknown:' you cannot tell which (an untagged defect is read as unknown). Only a product defect with a control goes back "
    "to a builder; the others go to the proof, to Operations, or to a diagnosis, never to new code.",
    "A gap must be in the item's own words: the mutant breaks something a clause of the item asks for. A mutant of an "
    "inner detail, or of an edge the item never named, is no gap, and every test has those.",
    "PASS: every clause of the item is done, you ran it, and you found no gap in the proof that you could show. "
    "WEAK: every clause is done, shown by your own runs, and you can show a gap: a mutant that stays green, or a "
    "clause the proof never reaches. A weak proof is not a pass: the item stays open and the next worker strengthens "
    "the proof without touching the code. FAIL: a clause is not done, or the proof is red, or cannot run for a reason in the commit. A gap you "
    "only suspect and did not show is no gap. Look for a clause that is missing before you look for a thin test.",
    "If you say WEAK, begin the reasons with GAP:DIFF when a gap you showed is a part of this commit's own change "
    "that you put back as it was before the commit while the proof stayed green, and that part does what a clause "
    "asks; begin with GAP:OTHER when every gap you showed is something else, such as a mutant you wrote yourself.",
    "A WEAK must say what strong proof would look like (JUDGE_WEAK_RETHINK_NAME_THE_STRONG_PROOF; owner, 2026-11-05: "
    "\"The Judge should have to be able to articulate what strong proof would look like.\"). Put two parts in the reasons: "
    "'STRONG: <the exact command or observation that would prove the clause>' and 'LETS THROUGH: <the real product "
    "defect, in the item's words, that the current proof would let ship>'. A WEAK missing either line is read as PASS. "
    "If you can run that strong check yourself and the work passes it, that is PASS, with your run as the evidence: "
    "never send work back to have a test written for a check you already made. Form, wording, citations, formatting "
    "and missing paperwork are never a gap: note them on a PASS.")
SHADOW = "narrow_weak_1"   # RELENTLESS_WEAK_MEASURE_PASS_COLLAPSE: the narrower WEAK, recorded per verdict; LIVE since 2026-11-03 (acted_weak)


def enforced(rules, mode="marker"):
    return bool((profile(rules, mode) or {}).get("enforce"))


# CHECKER_REACH_FIX_NAMED_SCRATCH_READ_ONLY (2026-11-05): 24 items held `unmeasured`, 17 of them on evidence under
# /mnt/d/ClaudeWork/rimmandrake (an ops_watch status.json, a testq tick.log, a backups folder) that the tmpfs over shared
# scratch hides. The wall's table (design section 8) withholds store, memory, attempts, git history, conversations and
# ledger notes - not the program-written state an item's proof reads. So a path the contract, the evidence or the item
# names under a `read_through` root is bound READ ONLY into the box; the rest of scratch stays empty and writable, and
# `never_through` (the worker run folders) is never bound.
THROUGH_MAX = 24
_THROUGH_WORD = re.compile(r"(?<![\w.~$@+/\\-])(?:[A-Za-z]:[\\/]|/)[\w.~@+-]*(?:[/\\][\w.~@+-]*)*")


def _host(word):
    """-> a path word as a host path: a Windows drive path as /mnt/<drive>/..., no trailing punctuation or slash."""
    w = word.rstrip(".,;:)'\"")
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", w)
    if m:
        w = "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/"))
    return w.rstrip("/") or "/"


def _inside(p, root):
    return p.startswith(root.rstrip("/") + "/")


def through_reachable(path, prof):
    """True when a named `path` would be bound by through(): strictly under a read_through root, outside never_through.
    Prefixes only (no filesystem read): relentless_reach.hidden asks this of a contract's proof."""
    p = os.path.normpath(_host(path))      # "..": resolved before the prefixes are read
    rx = prof.get("never_through_rx")
    return (any(_inside(p, r) for r in prof.get("read_through") or ())
            and not any(p == n.rstrip("/") or _inside(p, n) for n in prof.get("never_through") or ())
            and not (rx and re.search(rx, p)))


def _clean_dir(d, prof, cap=4000):
    """True when a folder may be bound whole: nothing in it is a path through_reachable() refuses (a worker's progress
    file inside a readings folder), and it is small enough to have looked at all of it."""
    n = 0
    for top, dirs, files in os.walk(d):
        for f in dirs + files:
            n += 1
            if n > cap or not through_reachable(os.path.join(top, f), prof):
                return False
    return True


def through(prof, texts, cap=THROUGH_MAX):
    """-> the host paths to bind read only into the box: each path word of `texts` that through_reachable() takes, walked
    up to the nearest one that exists while still strictly under its root (a reading not written yet shows its folder),
    whose real path stays inside the root and outside never_through, once each, a path under another one dropped."""
    roots = [os.path.realpath(r) for r in prof.get("read_through") or ()]
    never = [os.path.realpath(n) for n in prof.get("never_through") or ()]
    env = prof.get("env") or {}
    got = []
    for t in texts:
        t = re.sub(r"\$\{?(\w+)\}?", lambda v: env.get(v.group(1), v.group(0)), t or "")   # "$RM_DATA_ROOT/x", as needs() reads it
        for m in _THROUGH_WORD.finditer(t):
            p = os.path.normpath(_host(m.group(0)))
            if not through_reachable(p, prof):
                continue
            while not os.path.lexists(p) and any(_inside(os.path.dirname(p), r) for r in prof["read_through"]):
                p = os.path.dirname(p)
            if not os.path.lexists(p):
                continue
            rp = os.path.realpath(p)
            if (not through_reachable(rp, dict(prof, read_through=roots, never_through=never))   # a link stays inside
                    or not _SAFE.match(rp) or rp in got):
                continue
            if os.path.isdir(rp) and not _clean_dir(rp, prof):
                continue
            got.append(rp)
    got = sorted(got)
    out = [p for p in got if not any(_inside(p, q) for q in got if q != p)]
    return out[:cap]


def through_lines(paths):
    """The Marker's words about what was bound."""
    if not paths:
        return []
    return ["", "Bound read only from the host into your box (the rest of shared scratch is still empty here): %s. Read "
            "them as the evidence they are; a path in this list is never --unreached." % ", ".join(paths)]


def toolchain(cfg=None):
    """-> [(name, shell command, why)] from checker_box.json toolchain."""
    cfg = box_config() if cfg is None else cfg
    return [(str(t["name"]), str(t["cmd"]), str(t.get("why") or "")) for t in cfg.get("toolchain") or []
            if isinstance(t, dict) and t.get("name") and t.get("cmd")]


def toolchain_lines(cfg=None):
    """The Marker's words about what its box can run (only the tools checker_box.json names)."""
    names = [n for n, _, _ in toolchain(cfg)]
    if not names:
        return []
    out = ["Your box carries the builder's toolchain: run the proof as written."]
    if "python_cv2" in names:
        out.append("  python3 imports cv2 and numpy.")
    if "windows_build" in names:
        out.append("  The Windows build stage works here: `python3 src/RimMandrake/Utils/winbuild.py <Mod or csproj>` builds "
                   "this tree's C# with dotnet.exe (WSL interop; call a Windows program by its /mnt/c path, it is not on PATH).")
    return out


def toolchain_probe(prof, box, extra=(), cfg=None, timeout=300):
    """-> [{name, exit, out}]: each toolchain command run from the box's tree in one throwaway unit carrying the Marker's
    own systemd properties and environment, as at a launch. A check that cannot start is exit -1 with the reason."""
    rows = []
    for name, cmd, _ in toolchain(cfg):
        argv = (["systemd-run", "--user", "--wait", "--pipe", "--collect", "--quiet",
                 "-p", "WorkingDirectory=" + os.path.join(str(box), "tree")] + props(prof, box, extra)
                + sum((["--setenv", "%s=%s" % kv] for kv in unit_env(prof, box, cfg).items()), [])
                + ["--", "/bin/bash", "-c", cmd])
        try:
            import control as C     # Relentless is retired: its family is OFF in the control store
            p = C.launch_unit(argv, {"family": "relentless"}, capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)
            rows.append({"name": name, "exit": p.returncode, "out": ((p.stdout or "") + (p.stderr or "")).strip()})
        except (OSError, subprocess.SubprocessError) as e:
            rows.append({"name": name, "exit": -1, "out": "%s: %s" % (type(e).__name__, e)})
    return rows


def item_reads(box):
    """-> {rev, files} when the box was made with the item_prose grant, else {}."""
    try:
        with open(os.path.join(str(box), ITEM_NOTE), encoding="utf-8") as f:
            got = json.load(f)
        return got if isinstance(got, dict) and got.get("files") else {}
    except (OSError, ValueError):
        return {}


# What a blind checker reads of the work: the obligations and the paths, never the worker's account of them. A finish's
# evidence ("I rejected A and B because ...; 3 passed") and a contract's `why`, `by_gen` and game `why` are reasoning and
# history (CHECKER_PROMPT_FIX_WORKER_REASONING_LEAK). `no_offline` stays: it is a claim the checker is told to test.
BLIND_CONTRACT = ("proof", "live", "offbox")
PATH_RX = re.compile(r"(?:[A-Za-z]:\\|/|~/)?(?:[\w.~-]+[/\\])+[\w.-]+")


def blind_contract(contract):
    c = contract or {}
    out = {k: c[k] for k in BLIND_CONTRACT if c.get(k)}
    g = c.get("game") or {}
    if g:
        out["game"] = {k: g[k] for k in ("clauses", "no_offline") if g.get(k)}
    return out


def evidence_paths(evidence, cap=20):
    """The path-shaped words of a finish's evidence, in order, once each; the prose around them is dropped."""
    seen = []
    for m in PATH_RX.finditer(evidence or ""):
        w = m.group(0).rstrip(".,;:)")
        if w not in seen:
            seen.append(w)
    return seen[:cap]


def blind_lines(st):
    paths = evidence_paths(st["candidate"].get("evidence"))
    return ["", "Contract: %s" % json.dumps(blind_contract(st["contract"])),
            "Paths the worker named (its account of them is withheld: judge by your own runs): %s"
            % (", ".join(paths) or "none")]


def marker_prompt(st, text, box, adapter_names=()):
    """The checker's words, its way to the change and its way to a verdict being the box's."""
    c = st["candidate"]
    qv = shlex.quote(str(box) + "/verdict")     # a box path with a space still runs
    return "\n".join([
        "You are a blind checker. You did not do this work and you have no record of how it went. Your cwd is a clean "
        "export of commit %s, with no git history." % c["sha"] if not git_reads(box) else
        "You are a blind checker. You did not do this work and you have no record of how it went. Your cwd is a clean "
        "export of commit %s with a read-only git history at it: HEAD is that commit, "
        "there is no branch or remote, and every ancestor reads. Commit messages, and the excluded folders git can still "
        "show, are workers' words, not evidence: judge by your own runs." % c["sha"],
        *RULE,
        *toolchain_lines(),
        *(["%s/ is in your tree as of %s (a reach repair granted it), read only: it is the filers' item prose, not "
           "evidence the work was done." % (ITEMS, str(item_reads(box)["rev"])[:12])] if item_reads(box) else []),
        "Then run exactly one of:",
        "  python3 %s PASS \"what you ran and saw\"" % qv,
        "  python3 %s WEAK \"the runs you made and what each showed, then each gap and the mutant or probe that "
        "shows it, then a STRONG: line and a LETS THROUGH: line\"" % qv,
        "  python3 %s FAIL \"For each defect, state what you ran and saw, the attainable command result or observation "
        "that would satisfy its clause, and the smallest product fix, proof repair, environment repair or clarification "
        "needed to reach it\" --defect \"CAUSE: one wrong thing\" [--defect ...] "
        "[--control \"how your instrument showed it can see\"] [--unreached \"what you also could not reach\"]" % qv,
        "  python3 %s UNMEASURED \"CANNOT REACH: what, and the command that showed it; then what you did check\" "
        "--unreached \"one thing out of reach, and the command that showed it\" [--unreached ...] "
        "[--propose NAME_OR_PATH ...]" % qv,
        "If you say UNMEASURED, you own the repair of your own eyes: add one --propose per fix, either the name of a "
        "supervisor offbox adapter that would read it from outside (%s) or an absolute path that, bound read only into "
        "this box, would let you read it. Relentless probes your proposal from inside this wall, applies it as its own "
        "change and checks this same commit once more; only if your proposal fails its probe is a ticket filed. A "
        "proposal only adds read access: the store, transcripts, memory and credentials are never opened."
        % (", ".join(sorted(adapter_names)) or "see run_rules.json offbox_adapters"),
        *offbox_lines(st["contract"], box),
        *blind_lines(st),
        "See the change in: %s/change.diff" % box, "", "--- item ---", text])


def clean_list(v):
    """THE one normalisation of a verdict's defects / unreached (script, CLI, box file, store all go through it): whitespace
    collapsed, blank entries dropped, each <= 600 chars, at most 20. -> a list, or None when the field was not given at all
    (an old-format verdict, read from its prose)."""
    if v is None:
        return None
    if not isinstance(v, (list, tuple)):
        v = [v]
    return [y for y in (" ".join(str(x).split()) for x in v) if y][:20]


_strs = clean_list


def refusal(word, defects, unreached, controls=None):
    """-> why a structured verdict is refused at the door (the CLI and the verdict script say the same), or None. Only ever
    used where a checker is there to read it: a verdict already on disk is never refused, read_as reads it."""
    if defects is None and unreached is None:
        return None
    if any(parse_defect(d)[0] == "product" for d in defects or []) and not clean_list(controls):
        return ("a product: defect needs a --control: how you showed your instrument can see (green on a known-good case, "
                "or it catches a fault you put in); without one, say unknown:")
    if clean_list(controls) and not defects:
        return "--control backs a product: defect only"
    if word == UNMEASURED and not unreached:
        return "UNMEASURED needs at least one --unreached: name what you could not reach"
    if word == UNMEASURED and defects:
        return "a defect your run showed is a FAIL, not UNMEASURED: say FAIL and keep the --unreached lines"
    if word == "PASS" and (defects or unreached):
        return "a PASS carries no --defect and no --unreached: evidence you could not reach is UNMEASURED, a defect is FAIL"
    return None


def read_verdict(box):
    """-> {word, reasons, defects, unreached, at}, or None. The box is the Marker's to write: only well-formed words pass.
    defects / unreached are None when the file did not carry them (written before the structured verdict)."""
    try:
        v = json.loads(Path(box, "verdict.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(v, dict) or v.get("word") not in WORDS:
        return None
    try:
        at = float(v.get("at") or time.time())
    except (TypeError, ValueError, OverflowError):     # the Marker writes this file: a bad stamp is its to get wrong, not ours to crash on
        at = time.time()
    return {"word": v["word"], "reasons": str(v.get("reasons") or ""), "defects": clean_list(v.get("defects")),
            "unreached": clean_list(v.get("unreached")), "proposals": clean_list(v.get("proposals")),
            "controls": clean_list(v.get("controls")), "at": at}


# ---- the cause of each defect (CHECKER_VERDICT_BUILD_CAUSE_BEFORE_RETURN; plan design/RimMandrake/
# relentless_recovery_plan_2026-11-05.md step 5, catalog class d: "judges unable to judge throwing things back to fix
# without fixing the measurement"). Only a VALIDATED product defect goes back to a builder or earns a strike: the cause is
# product, the defect cites the candidate's change (a path its diff touches) or behaviour (the contract's proof), and the
# Marker says how its instrument passed a control. A measurement defect goes to the proof road on the same sha; an
# environment defect opens an Operations alarm keyed on the dependency and waits for diagnosis; unknown - and anything
# untagged, or a product claim that fails validation - waits for diagnosis, never a builder.
CAUSES = ("product", "measurement", "environment", "unknown")
PRODUCT, MEASUREMENT, ENVIRONMENT, UNKNOWN = CAUSES
_TAG = re.compile(r"^\s*\[?\s*(product|measurement|environment|unknown)\s*\]?\s*:\s*", re.I)


def tagged(line):
    """-> the cause a defect line opens with, or None when it carries none."""
    m = _TAG.match(line or "")
    return m.group(1).lower() if m else None


def parse_defect(line):
    """-> (cause, text). An untagged line (an old verdict, a hand-written file) is unknown: never guessed product."""
    m = _TAG.match(line or "")
    if not m:
        return UNKNOWN, (line or "").strip()
    return m.group(1).lower(), line[m.end():].strip()


# which dependency an environment defect names: the key Operations groups one incident under
DEPENDENCIES = (
    ("disk", re.compile(r"ENOSPC|no space left|disk (is )?full|out of (disk|space)|quota exceeded on|\bdf\b", re.I)),
    ("account", re.compile(r"\b429\b|rate[- ]limit|usage limit|out of tokens|credit|overloaded|\b529\b", re.I)),
    ("remote_host", re.compile(r"\bssh\b|tailscale|steve|host (is )?(down|unreachable)|connection (refused|reset|timed out)",
                                re.I)),
    ("game", re.compile(r"\bgame\b|bridge|mod list|modsconfig|not in the load|missing_mods|\bsave\b|player\.log|rimworld",
                         re.I)),
    ("network", re.compile(r"\bdns\b|network|unreachable|timed? ?out", re.I)),
)


def dependency(text):
    """-> the dependency an environment defect's words name (disk, account, remote_host, game, network), else other."""
    for key, rx in DEPENDENCIES:
        if rx.search(text or ""):
            return key
    return "other"


_PATH_RX = re.compile(r"^diff --git a/(\S+) b/(\S+)", re.M)


def changed_paths(box):
    """-> the paths the candidate's change.diff touches ([] when the box or its diff is gone)."""
    try:
        d = Path(box, "change.diff").read_text(encoding="utf-8", errors="replace")
    except (OSError, TypeError):
        return []
    return sorted({p for m in _PATH_RX.finditer(d) for p in m.groups()})


_STOP = {"python3", "python", "bash", "sh", "src", "rimmandrake", "rimflow", "utils", "only", "run", "selftests", "py",
         "no", "cache", "the", "and", "with", "item", "run_selftests"}


def _proof_tokens(proof):
    """The proof's own identifiers a defect may cite as behaviour: script stems, test names (selftest_x), long words."""
    out = set()
    for w in re.findall(r"[A-Za-z_][A-Za-z0-9_.\-/]{3,}", proof or ""):
        stem = w.rsplit("/", 1)[-1]
        stem = stem[:-3] if stem.endswith(".py") else stem
        if stem.lower() not in _STOP and ("_" in stem or "." in w or "/" in w):
            out.add(stem.lower())
    return out


_NOT_ATTRIBUTES = "py|pyc|json|jsonl|md|txt|log|csv|xml|cs|sh|bak"     # stem.json is another file, no attribute of stem.py


def cites(text, changed, proof):
    """True when a defect's words point at the candidate: a path its diff touches (whole, or its file name, or a .py file's
    module.attribute spelling), or one of the contract proof's own identifiers (the behaviour the proof runs).
    OPS_CHURN_DIAGNOSE_PROOFLINT_JMAL_SKJL: three true defects of relentless_live.py, written relentless_live.proof_scripts,
    read as citing nothing, and routed unknown past the builder."""
    t = (text or "").lower()
    for p in changed or []:
        p = p.lower()
        name = p.rsplit("/", 1)[-1]
        if p in t or (len(name) >= 5 and re.search(r"(?<![\w.])%s(?![\w])" % re.escape(name), t)):
            return True
        if name.endswith(".py") and len(name) >= 8 and re.search(
                r"(?<![\w.])%s\.(?!(?:%s)\b)[a-z_]\w*" % (re.escape(name[:-3]), _NOT_ATTRIBUTES), t):
            return True
    return any(re.search(r"(?<![\w])%s(?![\w])" % re.escape(k), t) for k in _proof_tokens(proof))


def causes(defects, controls=None, changed=(), proof=None):
    """-> one row per defect: {cause (what the Marker said), text, valid (product only: a control and a citation),
    acts (the cause the supervisor routes on: an unvalidated product is unknown)}."""
    rows = []
    has_control = bool(clean_list(controls))
    for d in clean_list(defects) or []:
        c, text = parse_defect(d)
        row = {"cause": c, "text": text}
        if c == PRODUCT:
            row["valid"] = has_control and cites(text, changed, proof)
            if not row["valid"]:
                row["why_not"] = ("no --control showed the instrument can see" if not has_control else
                                  "cites neither a path the candidate's diff touches nor the contract's proof")
        row["acts"] = c if c != PRODUCT or row["valid"] else UNKNOWN
        rows.append(row)
    return rows


def route(rows):
    """-> the cause a FAIL verdict is routed on: a validated product defect anywhere goes to the builder; else any
    unknown (an unvalidated product included) waits for diagnosis; else environment; else measurement. Empty -> unknown."""
    acts = [r["acts"] for r in rows or []]
    for c in (PRODUCT, UNKNOWN, ENVIRONMENT, MEASUREMENT):
        if c in acts:
            return c
    return UNKNOWN


def would_deny(inputs, prof):
    """-> the denied paths a run's tool calls named. For enforce false: the wall's report."""
    hits = set()
    for inp in inputs:
        text = json.dumps(inp, ensure_ascii=False)
        hits.update(p for p in denied(prof) + list(prof.get("tmpfs", ()))
                    if re.search(r"(?<![\w.-])" + re.escape(p) + r"(?![\w.-])", text))
        # the path at a word edge: after a slash, space, quote, = ( ; | & < > : or the start - shell quoting does not hide it
        hits.update(p for p in prof["tree_exclude"] if re.search(r"(?<![\w.-])" + re.escape(p) + r"(?![\w.-])", text))
    return sorted(hits)


def audit(store, rules, sessions_of, inputs_of):
    """Report only. -> [{item, unit, would_deny}] for each check in the store that has a session."""
    prof = profile(rules)
    out = []
    if prof is None:        # no wall configured: nothing to report against
        return out
    for st in store.states():
        chk = st.get("check") or {}
        session = sessions_of(chk.get("run"))
        inputs = inputs_of(session) if session else None
        if inputs is not None:
            out.append({"item": st["item"], "unit": chk.get("unit"), "would_deny": would_deny(inputs, prof)})
    return out
_REACH = [re.compile(x, re.I) for x in (
    r"\b(could|can)\s?not\s+(be\s+)?(reach|see|read|run|start|open|ssh|measure|be run|be shown)\w*[^.;]{0,60}?"
    r"\b(here|sandbox|box|checker|walled)\b",
    r"\b(sandbox|this box|walled|checker'?s? (env|view|box|sandbox))\b[^.;]{0,60}?(cannot|can't|could not|not visible|"
    r"not reachable|empty|masks?\b|tmpfs|blocked|fails?\b|failed)",
    r"\bnot (reachable|visible) (from|in) (this|the|my) (sandbox|box|checker)",
    r"\bssh\s+\S+[^.;]{0,40}?(fail|exit(s|ed)? 255|permission denied|bad owner|could not resolve|timed out)",
    r"\benvironment (block|problem|fault|failure)\b|\benv only\b|\bnot a code defect\b",
    r"\b(is|are) empty here\b|\bempty (tmpfs|mask|directory)\b",
    r"\b(can't|cannot|could not|unable to) reach\b",
)]
_HIDDEN_ABSENT = re.compile(r"(%s)[^.;]{0,120}?%s|%s[^.;]{0,80}?(%s)" % (
    "|".join(re.escape(h) for h in HIDDEN), _ABSENT, _ABSENT, "|".join(re.escape(h) for h in HIDDEN)), re.I)
# what a Marker writes when its own run showed the work wrong: then the FAIL stands, blind parts or not
# GPT review of 0135b04912: old-format prose is read biased to FAIL - a named defect beats any blindness beside it.
_DEFECT = re.compile(r"cause is in (this|the) commit|\bis false\b|\bleaks?\b|\bproof is red\b|\bnot done\b|"
                     r"\b\d+ FAIL(ED|ING|S)?\b|\bFAIL with \d|\b(stays?|leaves \S+( \S+)?) (green|OK)\b|\bclause \d+ is missing|"
                     r"\bdoes not (do|fix|hold)\b|\bwrong\b|\bregress|"
                     r"\bexpected\b[^.;]{0,40}?\b(got|but (was|is|found|saw)|found|saw|actual)\b|\bdrops?\b|\bdropped\b|"
                     r"\bcrash(es|ed)?\b|\btraceback\b|\b(raises|raised)\b|\bassert(ion)?(Error)?\b|\bbug\b|\boff[- ]by[- ]one\b|"
                     r"\bmismatch|\bbroken\b|\bincorrect\b|\bmiscount|\bdoes not match\b|\bnot equal\b", re.I)


def blind_reason(reasons):
    """-> the words that say the checker could not reach its evidence, or None. Pure: a reading of the reasons."""
    text = reasons or ""
    if text.lstrip().upper().startswith(REACH_TAG):
        return text.lstrip()
    for rx in _REACH + [_HIDDEN_ABSENT]:
        m = rx.search(text)
        if m:
            return text[max(0, m.start() - 40):m.end() + 40].strip()
    return None


def defect_said(reasons):
    """True when the reasons say the checker's own run showed the work wrong: a real FAIL, whatever else it could not see."""
    return bool(_DEFECT.search(reasons or ""))


def read_as(word, reasons, defects=None, unreached=None):
    """-> (word the supervisor acts on, the blind words or None). Structured (defects / unreached lists, the verdict script's
    own fields): any observed defect is FAIL whatever the word; otherwise any unreached evidence is UNMEASURED under EVERY
    word, PASS and WEAK too (GPT round 2: a PASS that names evidence it could not reach is not a close). Only then is a WEAK
    read by acted_weak: only GAP:DIFF holds.
    Old format (both None): the prose, biased to FAIL - a defect named anywhere keeps or makes it FAIL, even under UNMEASURED."""
    if defects is not None or unreached is not None:
        defects, unreached = clean_list(defects) or [], clean_list(unreached) or []
        if defects:
            return "FAIL", None
        if unreached:       # every word, WEAK included: a GAP:OTHER WEAK narrows to PASS (CHECKER_WEAK_FIX_UNREACHED_READ_AS_PASS)
            return UNMEASURED, "; ".join(unreached)
        if word == UNMEASURED:      # the script refuses this; a hand-written file is read as prose
            return read_as(word, reasons)
        return acted_weak(word, reasons), None
    if word == UNMEASURED:
        if defect_said(reasons):
            return "FAIL", None
        return UNMEASURED, blind_reason(reasons) or (reasons or "")
    if word == "FAIL":
        b = blind_reason(reasons)
        if b and not defect_said(reasons):
            return UNMEASURED, b
    return acted_weak(word, reasons), None


# ---- off-box measurements: a contract's `offbox` ADAPTER NAMES. Each name is a fixed command in run_rules.json
# "offbox_adapters", which the supervisor runs outside the wall at check launch; raw output and exit go read only into the
# box, so the Marker judges a fresh measurement, never a number a worker typed. GPT review of 0135b04912: a worker-authored
# command ran with the supervisor's reach and could carry transcripts or store files into the box - so a worker (or unhold)
# may only NAME an adapter; what runs is supervisor-owned code, run as argv (no shell) from an empty folder.
OFFBOX_MAX = 4
OFFBOX_OUT_MAX = 20000
_NAME = re.compile(r"^[a-z][a-z0-9_]{1,40}$")


def adapters(rules):
    """-> {name: {what, argv}} from the rules' offbox_adapters; keys starting _ are notes."""
    got = (rules or {}).get("offbox_adapters") or {}
    return {k: v for k, v in got.items() if not k.startswith("_") and isinstance(v, dict) and isinstance(v.get("argv"), list)
            and v["argv"] and all(isinstance(x, str) for x in v["argv"])}


def check_offbox_names(names, rules):
    """-> the names, cleaned. Raises ValueError for anything that is not a known adapter name: no shell crosses the wall."""
    names = [x.strip() for x in (names or []) if x and x.strip()]
    known = adapters(rules)
    bad = [x for x in names if not _NAME.match(x) or x not in known]
    if bad:
        raise ValueError("--offbox takes an adapter name from run_rules.json offbox_adapters (%s), never a command: "
                         "%s. A new reading is a new adapter, added by a reviewed change to the rules"
                         % (", ".join(sorted(known)) or "none defined", ", ".join(repr(x[:80]) for x in bad)))
    if len(names) > OFFBOX_MAX:
        raise ValueError("at most %d offbox adapters" % OFFBOX_MAX)
    return names


# An adapter's argv may name what the SUPERVISOR knows about this check, never worker text (CHECKER_REACH_BUILD_GIT_AND_GH_
# ADAPTERS: 5 holds wanted git history the box has no .git for): {sha} the candidate commit, {repo} the check's clean clone
# outside the wall (full history, checked out at {sha}). Each value is shape-checked before it fills a token.
_SLOT = re.compile(r"\{([a-z_]+)\}")
_SLOT_OK = {"sha": re.compile(r"^[0-9a-f]{40}$"), "repo": re.compile(r"^/[^\x00-\x1f{}]+$"),
            # the item under check (CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK gen 3: relentless_live_evidence reads its runs)
            "item": re.compile(r"^[A-Z][A-Z0-9_]{1,120}$")}


def fill_argv(argv, values):
    """-> (argv with every {slot} filled, None) or (None, why it cannot run). A slot outside _SLOT_OK, a missing value or a
    value of the wrong shape refuses the reading: nothing half-filled ever runs."""
    out = []
    for tok in argv:
        for slot in _SLOT.findall(tok):
            v = (values or {}).get(slot)
            if slot not in _SLOT_OK:
                return None, "refused: {%s} is not a supervisor value (%s)" % (slot, ", ".join(sorted(_SLOT_OK)))
            if not isinstance(v, str) or not _SLOT_OK[slot].match(v):
                return None, "not run: this check has no valid {%s}" % slot
            tok = tok.replace("{%s}" % slot, v)
        out.append(tok)
    return out, None


def offbox_cmds(contract):
    """-> the contract's offbox adapter names (an old contract may hold free text: it is refused at run time, never run)."""
    got = (contract or {}).get("offbox") or []
    return [got] if isinstance(got, str) else list(got)


def write_offbox(box, results):
    """results: [{cmd, exit, out, at}]. -> the folder. Each file is read only: the Marker reads a measurement, never edits it."""
    d = Path(box, "offbox")
    d.mkdir(exist_ok=True)
    for n, r in enumerate(results, 1):
        f = d / ("%d.txt" % n)
        f.write_text("$ %s\nmeasured_at=%s exit=%s\n%s\n" % (r["cmd"], time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(r["at"])),
                                                         r["exit"], (r["out"] or "")[-OFFBOX_OUT_MAX:]), encoding="utf-8")
        os.chmod(f, 0o444)
    return str(d)


def offbox_lines(contract, box):
    """The Marker's words about the supervisor's off-box readings, when the contract declares any."""
    cmds = offbox_cmds(contract)
    if not cmds:
        return []
    return ["", "Off-box readings: the supervisor ran the contract's offbox adapter(s) %s outside your box just before you "
            "started, and wrote each command, its exit and its raw output to %s/offbox/<n>.txt (read only). They are fresh "
            "measurements, not the worker's words: judge them as the reading of what your box cannot reach, and judge "
            "whether each one really measures what its clause asks. A reading that is missing or failed to run is "
            "--unreached, not a --defect." % (", ".join(cmds), box)]


PROBE = r'''
for p in "$@"; do
  if [ -d "$p" ]; then ls -A "$p" >/dev/null 2>&1 && echo "SEEN $p" || echo "DENIED $p"
  elif [ -e "$p" ] || [ -L "$p" ]; then cat "$p" >/dev/null 2>&1 && echo "SEEN $p" || echo "DENIED $p"
  else echo "ABSENT $p"; fi
done
env | grep -c '^RELENTLESS_ROOT=' | sed 's/^/ROOT_ENV /'
'''
