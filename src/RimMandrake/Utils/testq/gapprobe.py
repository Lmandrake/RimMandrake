"""testq/gapprobe.py -- what modcheck knows that the filler's gap order (gaps.py) needs, as one JSON line.

stdin:  {"mod": MOD, "items": {item id: ledger text}, "since": [sha, ...]}
stdout: {"chains": [every chain, suite order], "offline": [offline chains],
         "item_chains": {item id: [live chains it links to]},
         "changed": {sha: [chains modcheck --changed suggests for sha..origin/main] or null}}

Offline (the declaration probe, no game). The item links mirror modcheck targeting.resolve(--item): the chain's
source names the item, or the item's text names the chain or one of its rows. They are computed here in one pass,
because resolve() re-walks the whole catalogue per item (hundreds of items per fill).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MC = os.path.abspath(os.path.join(HERE, "..", "modcheck"))
if MC not in sys.path:
    sys.path.insert(0, MC)


def main():
    req = json.loads(sys.stdin.read() or "{}")
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):       # a validation.py that prints must not corrupt the answer
        import runner
        import targeting
        mod_dir = runner.find_mod_dir(req["mod"])
        suite = runner.load_validation(mod_dir)
        names = [n for n, _ in suite.chains]
        offline = set(getattr(suite, "offline_chains", ()) or ())
        by_chain, _ = targeting.catalogue(suite)
        srcs = {n: targeting._chain_source(fn) for n, fn in suite.chains}
        links = {}
        for iid, text in (req.get("items") or {}).items():
            hit = [n for n in names if n not in offline and (
                targeting._names_in(srcs[n], iid) or targeting._names_in(text, n)
                or any(targeting._names_in(text, r) for r in by_chain.get(n, ())))]
            if hit:
                links[iid] = hit
        changed = {}
        for sha in req.get("since") or []:
            try:
                res = targeting.changed(suite, targeting.changed_files(mod_dir, "%s..origin/main" % sha), mod_dir)
                changed[sha] = sorted(res["suggest"])
            except targeting.TargetError:
                changed[sha] = None
    print(json.dumps({"chains": names, "offline": sorted(offline), "item_chains": links, "changed": changed}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
