"""testq/gapprobe.py -- what modcheck knows that the filler's gap order (gaps.py) needs, as one JSON line.

stdin:  {"mod": MOD, "items": {item id: ledger text}, "since": [sha, ...]}; with "only": "reads", just `reads` is answered
stdout: {"chains": [every chain, suite order], "offline": [offline chains],
         "item_chains": {item id: [live chains it links to]},
         "link_kind": {item id: {chain: "source" | "chain" | "row"}}: how each link was made (the chain's source
                      names the item; the item's text names the chain; it names only one of its rows), strongest
                      first. gaps.rank gives a chain several items link to the strongest (TESTQ_FIX_ROW_ITEMS_FIRST_ALPHABETICAL),
         "changed": {sha: [chains modcheck --changed suggests for sha..origin/main] or null},
         "versions": {chain: its code version now (gate.code_version; testq/retest.py), or null},
         "reads": [the repo paths a chain of MOD can read when nothing declares its own: mod_reads()], or null when they
                  cannot be told}

Offline (the declaration probe, no game). The item links mirror modcheck targeting.resolve(--item): the chain's
source names the item, or the item's text names the chain or one of its rows AND names the mod (names_mod). They are computed here in one pass,
because resolve() re-walks the whole catalogue per item (hundreds of items per fill).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MC = os.path.abspath(os.path.join(HERE, "..", "modcheck"))
if MC not in sys.path:
    sys.path.insert(0, MC)


def mod_reads(mod_dir, suite):
    """-> [repo paths] that a chain of the mod can read: the mod's folder, each repo mod the run composes for it (About.xml
    dependencies and the tier, transitively), what a csproj of those folders compiles from outside them, and the Python that
    validation.py imports from outside the harness. None when the Python or a file cannot be read: the chain runs again."""
    import glob
    import re
    import gate
    import runner
    root, ours, todo = gate.ROOT, set(), [os.path.abspath(mod_dir)]
    repo = gate.repo_mods()
    st = gate._status()
    harness = {os.path.abspath(p) for s in ("runner.py", "suite.py") for p in st.test_closure(os.path.join(MC, s), mod_dir)[0]}
    extra = set()
    try:
        while todo:
            d = todo.pop()
            if d in ours:
                continue
            ours.add(d)
            ids = gate.package_ids_for(os.path.basename(d)) if len(ours) == 1 else (
                runner.mod_dependency_ids(d) if os.path.isfile(os.path.join(d, "About", "About.xml")) else [])
            todo.extend(os.path.abspath(repo[i]) for i in ids if i in repo)
            for proj in glob.glob(os.path.join(d, "**", "*.csproj"), recursive=True):
                with open(proj, encoding="utf-8-sig", errors="replace") as f:
                    text = f.read()
                for ref in re.findall(r'(?:Include="|<HintPath>)\s*([^"<]*\.\.[^"<]*)', text):
                    p = os.path.normpath(os.path.join(os.path.dirname(proj), re.split(r"[*?]", ref.replace("\\", "/"))[0]))
                    if p.startswith(root + os.sep):
                        extra.add(p)
        for script in [os.path.join(mod_dir, "validation.py")] + [
                os.path.join(mod_dir, g[len("@closure:"):]) for v in (getattr(suite, "chain_inputs", {}) or {}).values()
                for g in v if g.startswith("@closure:")]:
            files, unresolved = st.test_closure(os.path.abspath(script), mod_dir)
            if unresolved:
                return None
            extra.update(os.path.abspath(f) for f in files if os.path.abspath(f) not in harness)
    except (OSError, ValueError):
        return None
    paths = ours | extra
    return sorted(os.path.relpath(p, root).replace(os.sep, "/") for p in paths
                  if not any(p != o and p.startswith(o + os.sep) for o in ours))


def main():
    req = json.loads(sys.stdin.read() or "{}")
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):       # a validation.py that prints must not corrupt the answer
        import gate
        import runner
        import targeting
        mod_dir = runner.find_mod_dir(req["mod"])
        suite = runner.load_validation(mod_dir)
        if req.get("only") == "reads":
            only = mod_reads(mod_dir, suite)
    if req.get("only") == "reads":
        print(json.dumps({"reads": only}))
        return 0
    with contextlib.redirect_stdout(io.StringIO()):
        names = [n for n, _ in suite.chains]
        offline = set(getattr(suite, "offline_chains", ()) or ())
        by_chain, _ = targeting.catalogue(suite)
        srcs = {n: targeting._chain_source(fn) for n, fn in suite.chains}
        links, kinds = {}, {}
        for iid, text in (req.get("items") or {}).items():
            # TESTQ_ITEMOWED_FIX_DEFS_CHAIN_ADOPTS_ALL: a link by the item's TEXT naming a chain or row holds only when
            # the item also names this mod. Generic names (defs, defs_resolve, site, flora) are declared by many mods,
            # and GREENTIDE_ANTS_MIGRATE_NO_ANT_LEFT_BEHIND was linked to the defs chain of every biome. Measured
            # 2026-11-04: all 32 of FlowWorks' text links name it; the dropped ones were all other mods' items.
            named = targeting.names_mod(req["mod"], iid, text)
            how = {}
            for n in names:
                if n in offline:
                    continue
                if targeting._names_in(srcs[n], iid):
                    how[n] = "source"
                elif named and targeting._names_in(text, n):
                    how[n] = "chain"
                elif named and any(targeting._names_in(text, r) for r in by_chain.get(n, ())):
                    how[n] = "row"
            if how:
                links[iid] = [n for n in names if n in how]
                kinds[iid] = how
        changed = {}
        for sha in req.get("since") or []:
            try:
                res = targeting.changed(suite, targeting.changed_files(mod_dir, "%s..origin/main" % sha), mod_dir)
                changed[sha] = sorted(res["suggest"])
            except targeting.TargetError:
                changed[sha] = None
        try:
            versions = gate.Gate(suite, req["mod"], mod_dir, gate.package_ids_for(req["mod"]), {}).versions()
        except Exception:  # noqa: BLE001 - no version is the identity rule, never a dead probe
            versions = {}
        try:
            reads = mod_reads(mod_dir, suite)
        except Exception:  # noqa: BLE001 - no reads is "cannot be told": the chains run again, the probe lives
            reads = None
    print(json.dumps({"chains": names, "offline": sorted(offline), "item_chains": links, "link_kind": kinds,
                      "changed": changed, "versions": versions, "reads": reads}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
