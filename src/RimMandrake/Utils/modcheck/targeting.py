"""Targeted runs: pick the chains a change touches, so a live run proves a fix without the full suite.

Owner, 2026-10-25 (design/RimMandrake/standing_rulings.md "Live runs are TARGETED"): *"Targeted runs should
always have been policy."* A run after a change covers only that change's chains/rows; the full `modcheck run
<Mod> --full` is a scheduled sweep (at most daily). Three ways to name what to run, unioned:

  --chains a,b      chain names, exactly as registered with `@suite.chain("...")`
  --rows r1,r2      row (component) ids; each selects the chain(s) that declare it -- the WHOLE chain runs, since a
                    row's setup lives in its chain -- and the record names the requested rows separately
  --item ITEM_ID    a rimflow item. Chains are mapped by two links, both printed with the reason:
                      1. the chain's own source names ITEM_ID (a row written for that item cites it)
                      2. the item's ledger text (`rimflow show`: title, notes, prose file) names a chain or row id --
                         an id with an underscore as a whole token, a one-word chain name only in backticks
                    No link -> refused, naming --chains/--rows. Never a fall-back to the full suite.

Everything here is offline: selection is resolved BEFORE run() swaps the mod list or touches the game, so a typo
costs nothing. Selection never changes what a chain does: run_suite's per-chain site hold (hostiles, unroof, gas,
weather) runs for every selected chain exactly as in a full run.
"""
import inspect
import re
import subprocess

from suite import Suite, _DeclarationProbe


class TargetError(ValueError):
    """A targeted run that cannot be resolved; the message says what to type instead."""


def rows_by_chain(suite):
    """{chain name: [row ids declared by that chain]} in suite order, via the no-op declaration probe (no game)."""
    out = {}
    probe = _DeclarationProbe()
    for name, fn in suite.chains:
        probe.upstream_failed = False
        probe.components = []
        try:
            fn(probe)
        except Exception:     # noqa: BLE001 - a chain the probe cannot walk declares no rows; its NAME still selects it
            pass
        out[name] = [c.name for c in probe.components]
        probe.components = []
    return out


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
    """-> {"chains": [...suite order], "of_chains": n, "rows": [...requested], "item": id|None, "by": [reasons], "rows_run": [...]}.

    `text` is the item's ledger text (item_text); passed in so this stays pure for selftests. Raises TargetError on
    an unknown chain/row, or an item with no link to any chain."""
    by_chain = rows_by_chain(suite)
    names = [n for n, _ in suite.chains]
    picked, why = set(), []
    unknown = [c for c in chains if c not in by_chain]
    if unknown:
        raise TargetError("unknown chain(s) for %s: %s; chains are: %s"
                          % (suite.name, ", ".join(unknown), ", ".join(names)))
    for c in chains:
        picked.add(c)
        why.append("chain %s: named by --chains" % c)
    for r in rows:
        owners = [c for c in names if r in by_chain[c]]
        if not owners:
            raise TargetError("unknown row %r for %s: no chain declares it (`modcheck floor --all` lists rows)"
                              % (r, suite.name))
        for c in owners:
            picked.add(c)
            why.append("chain %s: declares row %s" % (c, r))
    if item:
        found = False
        for name, fn in suite.chains:
            if _names_in(_chain_source(fn), item):
                picked.add(name)
                found = True
                why.append("chain %s: its source names %s" % (name, item))
        for name in names:
            if text and _names_in(text, name):
                picked.add(name)
                found = True
                why.append("chain %s: named in %s's ledger text" % (name, item))
            for r in by_chain[name]:
                if text and _names_in(text, r):
                    picked.add(name)
                    found = True
                    why.append("chain %s: its row %s is named in %s's ledger text" % (name, r, item))
        if not found:
            raise TargetError(
                "--item %s maps to no %s chain: no chain's source names it and its ledger text names no chain or "
                "row id. Name them yourself: `modcheck run %s --chains <a,b>` or `--rows <r1,r2>` (chains: %s). "
                "Refusing rather than running the full suite."
                % (item, suite.name, suite.name, ", ".join(names)))
    if not picked:
        raise TargetError("empty selection for %s" % suite.name)
    ordered = [n for n in names if n in picked]
    return {"chains": ordered, "of_chains": len(names), "rows": list(rows), "item": item, "by": why,
            "rows_run": [r for n in ordered for r in by_chain[n]]}


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
