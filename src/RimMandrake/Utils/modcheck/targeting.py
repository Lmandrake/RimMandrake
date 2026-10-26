"""Targeted runs: pick the chains a change touches, so a live run proves a fix without the full suite.

Owner, 2026-10-25 (design/RimMandrake/standing_rulings.md "Live runs are TARGETED"): *"Targeted runs should
always have been policy."* A run after a change covers only that change's chains/rows; the full `modcheck run
<Mod> --full` is a scheduled sweep (at most daily). Three ways to name what to run, unioned:

  --chains a,b      chain names, exactly as registered with `@suite.chain("...")`
  --rows r1,r2      row (component) ids; each selects the chain(s) that declare it as a PREFIX: the chain runs from its
                    start (a row's setup lives in its chain) and STOPS after its last requested row (suite.StopAfter);
                    the rows after it are recorded NOT_RUN from the chain's catalogue, never executed. A chain also
                    named whole (--chains, or its source citing --item) overrides the cutoff.
  --item ITEM_ID    a rimflow item. Chains are mapped by two links, both printed with the reason:
                      1. the chain's own source names ITEM_ID (a row written for that item cites it)
                      2. the item's ledger text (`rimflow show`: title, notes, prose file) names a chain or row id --
                         an id with an underscore as a whole token, a one-word chain name only in backticks
                    No link -> refused, naming --chains/--rows. Never a fall-back to the full suite.

Per-chain scope (focused_testing_plan_2026-10-25, option A): resolve() returns `scope` = {chain: {mode: full|prefix,
requested_rows, reasons, executed, skipped}} and preview() prints it -- requested -> prerequisites -> executed ->
skipped -- before anything launches (`modcheck run <Mod> --rows r --preview` prints it and stops). Row targeting is
REFUSED for a chain whose catalogue is incomplete (the declaration probe raised part-way): its stop point and its
NOT_RUN tail would be guesses. Chains declared `offline=True` are left out of a targeted live run (they run at T0);
only --full runs them in the live slot.

Everything here is offline: selection is resolved BEFORE run() swaps the mod list or touches the game, so a typo
costs nothing. Selection never changes how a chain is held: run_suite's per-chain site hold -- hostiles and the
bland map, then Log reset, weather lock, unroof and gas clear -- runs before every selected chain on every live path
(situational or not), exactly as in a full run (MODCHECK_HOLD_FIX_SITUATIONAL_ONLY_ROOF).
"""
import inspect
import re
import subprocess

from suite import FAIL, UNMEASURED, Suite, _DeclarationProbe


class TargetError(ValueError):
    """A targeted run that cannot be resolved; the message says what to type instead."""


def catalogue(suite):
    """-> ({chain: [row ids declared]}, {chain: why its list is INCOMPLETE}) in suite order, via the no-op declaration
    probe (no game). A chain the probe cannot walk to its end keeps the rows declared before the raise -- a PARTIAL
    list -- and is named in the second dict: its NAME still selects it whole, but no row cutoff may be computed on it."""
    out, incomplete = {}, {}
    probe = _DeclarationProbe()
    for name, fn in suite.chains:
        probe.upstream_failed = False
        probe.components = []
        try:
            fn(probe)
        except Exception as ex:     # noqa: BLE001 - recorded: the list is partial, row targeting on it is refused
            incomplete[name] = "the declaration probe raised %s: %s" % (type(ex).__name__, str(ex)[:120])
        # a raise INSIDE a component is swallowed by the component (the chain walks on), but rows nested after the
        # raise in that component were never declared: the list may be partial just the same
        raised = [c for c in probe.components if c.verdict in (FAIL, UNMEASURED) and c.detail]
        if raised and name not in incomplete:
            incomplete[name] = "row %s raised inside the declaration probe (%s): rows nested after it are unknown" % (
                raised[0].name, str(raised[0].detail)[:120])
        out[name] = [c.name for c in probe.components]
        probe.components = []
    return out, incomplete


def rows_by_chain(suite):
    """{chain name: [row ids declared by that chain]}; a list may be PARTIAL -- see catalogue() for which."""
    return catalogue(suite)[0]


def _chain_source(fn):
    try:
        return inspect.getsource(getattr(fn, "__wrapped__", fn))
    except (OSError, TypeError):
        return ""


def _names_in(text, name):
    """True when `name` stands as a whole token in `text`; a name without an underscore only in backticks."""
    if "_" in name or any(ch.isdigit() for ch in name):
        return re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(name), text) is not None
    return ("`%s`" % name) in text


def item_text(item_id, runner_mod=None):
    """Everything the ledger says about `item_id` (`rimflow show`): title, notes, prose. Raises TargetError if the
    item does not exist."""
    import runner as _R  # noqa: E402
    r = (runner_mod or _R)
    proc = subprocess.run(r.py_cmd(r.RIMFLOW_CLI, "show", item_id), cwd=r.ROOT, capture_output=True, text=True)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise TargetError("--item %s: rimflow show could not read that item (%s)"
                          % (item_id, (proc.stdout + proc.stderr).strip()[-200:]))
    return proc.stdout


def resolve(suite, chains=(), rows=(), item=None, text=None):
    """-> {"chains": [...suite order, live], "of_chains": n, "rows": [...requested], "item": id|None, "by": [reasons],
    "rows_run": [...executed], "scope": {chain: {...}}, "offline_skipped": {chain: why}}.

    `text` is the item's ledger text (item_text); passed in so this stays pure for selftests. Raises TargetError on
    an unknown chain/row, an item with no link to any chain, row targeting on an incomplete catalogue, or a
    selection that is only offline chains."""
    by_chain, incomplete = catalogue(suite)
    # an offline chain never runs live (dropped below), so its partial list can hide nothing from a live selection
    blocking = {n: w for n, w in incomplete.items() if n not in (getattr(suite, "offline_chains", ()) or ())}
    names = [n for n, _ in suite.chains]
    picked, why = set(), []
    whole, want = set(), {}       # chains named whole; chain -> requested rows (a prefix unless also whole)

    def _row(chain, r):
        want.setdefault(chain, [])
        if r not in want[chain]:
            want[chain].append(r)
    unknown = [c for c in chains if c not in by_chain]
    if unknown:
        raise TargetError("unknown chain(s) for %s: %s; chains are: %s"
                          % (suite.name, ", ".join(unknown), ", ".join(names)))
    for c in chains:
        picked.add(c)
        whole.add(c)
        why.append("chain %s: named by --chains" % c)
    unknown_rows = []
    for r in rows:
        owners = [c for c in names if r in by_chain[c]]
        if not owners:
            unknown_rows.append(r)      # judged below, once every whole-chain selection (incl. --item) is known
            continue
        for c in owners:
            _row(c, r)
            picked.add(c)
            why.append("chain %s: declares row %s" % (c, r))
    if item:
        found = False
        for name, fn in suite.chains:
            if _names_in(_chain_source(fn), item):
                picked.add(name)
                whole.add(name)
                found = True
                why.append("chain %s: its source names %s" % (name, item))
        for name in names:
            if text and _names_in(text, name):
                picked.add(name)
                whole.add(name)
                found = True
                why.append("chain %s: named in %s's ledger text" % (name, item))
            for r in by_chain[name]:
                if text and _names_in(text, r):
                    _row(name, r)
                    picked.add(name)
                    found = True
                    why.append("chain %s: its row %s is named in %s's ledger text" % (name, r, item))
        if not found:
            raise TargetError(
                "--item %s maps to no %s chain: no chain's source names it and its ledger text names no chain or "
                "row id. Name them yourself: `modcheck run %s --chains <a,b>` or `--rows <r1,r2>` (chains: %s). "
                "Refusing rather than running the full suite."
                % (item, suite.name, suite.name, ", ".join(names)))
    for r in unknown_rows:
        if set(blocking) - whole:
            raise TargetError(
                "unknown row %r for %s, and the row catalogue is incomplete for chain(s) %s (the declaration "
                "probe could not walk them), so it may live there. Name the chain whole: `--chains <name>`."
                % (r, suite.name, ", ".join(sorted(set(blocking) - whole))))
        raise TargetError("unknown row %r for %s: no chain declares it (`modcheck floor --all` lists rows)"
                          % (r, suite.name))
    for r in sorted(set(x for v in want.values() for x in v)):     # rows from --rows AND from --item text
        owners = [c for c in names if r in by_chain[c]]
        hidden = sorted(set(blocking) - whole - set(owners))
        if hidden:
            raise TargetError(
                "row %r is declared by %s, but the row catalogue is incomplete for chain(s) %s (%s), which may "
                "declare it too: resolving it would silently skip them. Name the chains whole: `--chains <name>`."
                % (r, ", ".join(owners), ", ".join(hidden), "; ".join(blocking[h] for h in hidden)[:300]))
    if not picked:
        raise TargetError("empty selection for %s" % suite.name)
    for n in names:     # a row cutoff on an incomplete catalogue is a guess; a chain also named whole needs none
        if n in want and n in blocking and n not in whole:
            raise TargetError(
                "row(s) %s target chain %s, whose row catalogue is incomplete (%s): its stop point and NOT_RUN tail "
                "would be guesses. Run the whole chain: `--chains %s`." % (", ".join(want[n]), n, incomplete[n], n))
    offline = set(getattr(suite, "offline_chains", ()) or ())
    off = {n: "offline chain: runs at T0 before launch, not in the live slot (only --full runs it live)"
           for n in names if n in picked and n in offline}
    ordered = [n for n in names if n in picked and n not in offline]
    if not ordered:
        raise TargetError(
            "every selected chain of %s is offline (%s): it needs no game -- run it at T0 (its offline selftest / "
            "validation tier), not in a live run. `--full` is the only live run that includes offline chains."
            % (suite.name, ", ".join(sorted(off))))
    scope = {}
    for n in ordered:
        cat = by_chain[n]
        reasons = [w.split(": ", 1)[1] for w in why if w.startswith("chain %s:" % n)]
        if n in whole or n not in want:
            scope[n] = {"mode": "full", "requested_rows": list(want.get(n, [])), "reasons": reasons,
                        "executed": list(cat), "skipped": []}
        else:
            cut = max(cat.index(r) for r in want[n]) + 1
            scope[n] = {"mode": "prefix", "requested_rows": list(want[n]), "reasons": reasons,
                        "executed": cat[:cut], "skipped": cat[cut:]}
    return {"chains": ordered, "of_chains": len(names), "rows": list(rows), "item": item, "by": why,
            "rows_run": [r for n in ordered for r in scope[n]["executed"]], "scope": scope,
            "offline_skipped": off, "incomplete": {n: incomplete[n] for n in ordered if n in incomplete}}


def preview(sel):
    """The plan, one block per chain, BEFORE launch: requested -> prerequisites -> executed -> skipped (NOT_RUN)."""
    out = ["PREVIEW %d of %d chains, %d rows to execute" % (len(sel["chains"]), sel.get("of_chains", 0),
                                                          len(sel.get("rows_run", [])))]
    for n in sel["chains"]:
        sc = sel["scope"][n]
        req = sc["requested_rows"]
        pre = [r for r in sc["executed"] if r not in req]
        out.append("  chain %s [%s]: %s" % (n, sc["mode"], "; ".join(sc["reasons"][:2]) +
                                            (" (+%d more)" % (len(sc["reasons"]) - 2) if len(sc["reasons"]) > 2 else "")))
        if sc["mode"] == "prefix":
            out.append("    requested %s | prerequisites %s | executed %d | skipped NOT_RUN %s"
                       % (", ".join(req), ", ".join(pre) or "-", len(sc["executed"]), ", ".join(sc["skipped"]) or "-"))
        else:
            out.append("    whole chain: executed %d row(s)%s%s"
                       % (len(sc["executed"]), " | requested %s" % ", ".join(req) if req else "",
                          " | catalogue INCOMPLETE (%s): rows past the probe are not listed" % sel["incomplete"][n]
                          if n in sel.get("incomplete", {}) else ""))
    for n, w in sorted(sel.get("offline_skipped", {}).items()):
        out.append("  chain %s SKIPPED: %s" % (n, w))
    return out


def filtered(suite, chain_names):
    """A copy of `suite` holding only `chain_names`, in suite order, with every other attribute kept (toggles,
    biome, hold_site, preconditions, chain_caps ...)."""
    keep = set(chain_names)
    out = Suite.__new__(Suite)
    out.__dict__.update(suite.__dict__)
    out.chains = [(n, fn) for n, fn in suite.chains if n in keep]
    out.chain_caps = {k: v for k, v in getattr(suite, "chain_caps", {}).items() if k in keep}
    return out


def config_tag(sel):
    """The scope words for the rimflow verify --config string: a targeted record never reads as a full verdict."""
    if not sel:
        return "full"
    return "TARGETED chains=%s%s" % (",".join(sel["chains"]),
                                     (" rows=%s" % ",".join(sel["rows"])) if sel.get("rows") else "")


# ============================================================================ --changed (focused_testing_plan option B)
# Changed files -> chains, as SUGGESTIONS only: `modcheck run <Mod> --changed <range|WORKTREE>` prints them and exits;
# nothing runs from a guess. A file maps to a chain by (1) the chain's declared `inputs=` globs (Suite.chain_inputs:
# shared helpers, inherited XML, patches its source does not name), (2) the chain source naming the file's basename or
# stem as a token, (3) for XML, a defName on a changed line (or, with none, any defName in the file) named in the chain
# source. A file no rule maps is listed as impact unknown: select explicitly, with a reason.
_DEFNAME = re.compile(r"<defName>\s*([A-Za-z0-9_]+)\s*</defName>")


def changed_files(mod_dir, rev_range="WORKTREE", root=None):
    """[(path relative to mod_dir, changed text or None)] of files under `mod_dir` changed in `rev_range` PLUS the
    uncommitted (staged, unstaged, untracked) ones; "WORKTREE" = uncommitted only. `changed text` is the +/- lines
    of the diff (None for an untracked file). Raises TargetError when git cannot answer."""
    import os
    root = root or subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=mod_dir, capture_output=True,
                                  text=True).stdout.strip()
    if not root:
        raise TargetError("--changed: %s is not inside a git work tree" % mod_dir)
    rel_mod = os.path.relpath(os.path.abspath(mod_dir), root).replace(os.sep, "/")

    def git(*a):
        p = subprocess.run(["git"] + list(a), cwd=root, capture_output=True, text=True)
        if p.returncode != 0:
            raise TargetError("--changed: git %s failed: %s" % (" ".join(a), (p.stderr or p.stdout).strip()[-200:]))
        return p.stdout

    specs = [["HEAD"]] + ([] if rev_range in (None, "", "WORKTREE") else [[rev_range]])
    names = {}
    for sp in specs:
        for n in git("diff", "--name-only", *sp, "--", rel_mod).splitlines():
            names.setdefault(n.strip(), sp)
    untracked = set(n.strip() for n in git("ls-files", "--others", "--exclude-standard", "--", rel_mod).splitlines())
    out = []
    for n in sorted(set(names) | untracked):
        if not n:
            continue
        text = None
        if n in names:
            d = git("diff", "-U0", *names[n], "--", n)
            text = "\n".join(l[1:] for l in d.splitlines() if l[:1] in "+-" and l[:3] not in ("+++", "---"))
        out.append((os.path.relpath(os.path.join(root, n), os.path.join(root, rel_mod)).replace(os.sep, "/"), text))
    return out


def changed(suite, files, mod_dir=None):
    """{"suggest": {chain: [reason, ...]}, "unknown": [file, ...]} for `files` [(rel path, changed text or None)].
    Pure but for reading an XML file under `mod_dir` that has no defName on a changed line."""
    import fnmatch
    import os
    srcs = {n: _chain_source(fn) for n, fn in suite.chains}
    inputs = getattr(suite, "chain_inputs", {}) or {}
    suggest, unknown = {}, []
    for rel, text in files:
        base = rel.rsplit("/", 1)[-1]
        stem = base.rsplit(".", 1)[0]
        hit = False
        for n, _ in suite.chains:
            why = None
            for g in inputs.get(n, ()):
                if g.startswith("@"):        # a gate token (gate.inputs_hash: @mod_hash, @closure:), not a path glob
                    continue
                g = g[1:] if g.startswith("?") else g
                if fnmatch.fnmatch(rel, g):
                    why = "%s matches declared input %s" % (rel, g)
                    break
            by_base = re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(base), srcs[n]) is not None
            if why is None and (by_base or (len(stem) > 3 and _names_in(srcs[n], stem))):
                why = "chain source names %s" % (base if by_base else stem)
            if why is None and base.lower().endswith(".xml"):
                defs = _DEFNAME.findall(text or "")
                if not defs and mod_dir:
                    try:
                        with open(os.path.join(mod_dir, rel), encoding="utf-8", errors="replace") as f:
                            defs = _DEFNAME.findall(f.read())
                    except OSError:
                        defs = []
                named = sorted(d for d in set(defs) if _names_in(srcs[n], d))
                if named:
                    why = "%s: defName %s named in chain source" % (base, ", ".join(named[:4]))
            if why:
                suggest.setdefault(n, []).append(why)
                hit = True
        if not hit:
            unknown.append(rel)
    return {"suggest": suggest, "unknown": unknown}


def changed_report(res):
    """Lines for `run --changed`: one per suggested chain with its reasons, then the files of unknown impact."""
    out = ["changed files -> SUGGESTED chains (nothing runs from this; select with --chains/--rows/--item):"]
    for n, why in res["suggest"].items():
        out.append("  %s: %s" % (n, "; ".join(why)[:300]))
    if not res["suggest"]:
        out.append("  (none)")
    for f in res["unknown"]:
        out.append("  %s: impact unknown -- select explicitly with a reason" % f)
    if res["suggest"]:
        out.append("  e.g. modcheck run <Mod> --chains %s" % ",".join(res["suggest"]))
    return out
