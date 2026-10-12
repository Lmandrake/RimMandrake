#!/usr/bin/env python3
"""Offline selftest: the driver writes partial results after every chain, and --chains / --skip-chains select
chains without a skipped bar ever reading as absent or green. No game, no bridge (MockTransport).

Motivation (MEASURED 2026-10-12): a 50-min shell timeout killed the Pyrelands run inside embergrass_regrow and
NO result JSON was written -- 23 finished rows survived only as stderr lines."""
import json
import os
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
for p in (_UTILS, os.path.join(_UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

from northstar_driver import PASS, FAIL, UNMEASURED, cli                  # noqa: E402
from northstar_driver import bars as B                                    # noqa: E402
from northstar_driver.session import FastSession                          # noqa: E402
from northstar_driver.transport import MockTransport, MockGame            # noqa: E402
from suite import Suite, ExpectationFailed                                # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


class Killed(Exception):
    """Stands in for the shell timeout: not an ExpectationFailed, so run_suite propagates it."""


def make_suite(kill_at=None):
    s = Suite("Fake")

    @s.chain("alpha")
    def alpha(t):
        with t.component("alpha_ok", shows=["fake_alpha"]):
            pass

    @s.chain("beta")
    def beta(t):
        with t.component("beta_fails", shows=["fake_beta"]):
            if t.session is not None:
                raise ExpectationFailed("beta is red on purpose")

    @s.chain("gamma")
    def gamma(t):
        if t.session is not None and kill_at == "gamma":
            raise Killed("killed inside gamma")
        with t.component("gamma_ok", shows=["fake_gamma"]):
            pass
        with t.component("gamma_functional"):
            pass

    return s


EXPECTED = ["fake_alpha", "fake_beta", "fake_gamma"]


def session():
    return FastSession(transport=MockTransport(MockGame()), strict=False)


def main():
    # 1. selection
    chains = make_suite().chains
    run, skipped = cli.select_chains(chains, None, ["gamma"])
    check("skip drops the named chain", [n for n, _ in run] == ["alpha", "beta"] and [n for n, _ in skipped] == ["gamma"])
    run, skipped = cli.select_chains(chains, ["gamma"], None)
    check("only keeps the named chain", [n for n, _ in run] == ["gamma"] and len(skipped) == 2)
    try:
        cli.select_chains(chains, ["gama"], None)
        check("a typo'd chain name is refused", False)
    except SystemExit as ex:
        check("a typo'd chain name is refused", "gama" in str(ex), str(ex)[:80])

    # 2. partial writes survive a kill mid-suite
    out = os.path.join(tempfile.mkdtemp(prefix="ns_incr_"), "r.json")
    writes = []

    def progress(d):
        writes.append(json.loads(json.dumps(d, default=str)))
        B.write_results(out, d)

    doc = {"mod": "Fake", "bars": [], "preflight": []}
    s = session()
    killed = False
    with s:
        try:
            cli._suite_rows(s, "Fake", EXPECTED, doc, progress=progress, suite=make_suite(kill_at="gamma"))
        except Killed:
            killed = True
    check("the kill propagates (a script bug is still a crash)", killed)
    check("one partial write per finished chain", len(writes) == 2, str(len(writes)))
    on_disk = json.load(open(out))
    check("the file on disk is the last partial", on_disk.get("partial") is True
          and on_disk.get("chains_done") == ["alpha", "beta"] and on_disk.get("chains_pending") == ["gamma"],
          str({k: on_disk.get(k) for k in ("partial", "chains_done", "chains_pending")}))
    by = {r["id"]: r for r in on_disk.get("bars") or []}
    check("finished rows are on disk with their verdicts", by.get("fake_beta", {}).get("status") == FAIL
          and by.get("fake_alpha", {}).get("state_status") == PASS, str({k: v.get("status") for k, v in by.items()}))
    check("an unfinished chain's bar reads UNMEASURED, never PASS", by.get("fake_gamma", {}).get("status") == UNMEASURED)
    check("a partial is never green", on_disk.get("all_green") is False and on_disk["summary"][FAIL] == 1)

    # 3. a skipped chain records 'chain not run' for every declared component
    doc = {"mod": "Fake", "bars": [], "preflight": []}
    with session() as s2:
        rows = cli._suite_rows(s2, "Fake", EXPECTED, doc, skip=["gamma"], suite=make_suite())
    by = {r["id"]: r for r in rows}
    g = by.get("fake_gamma") or {}
    check("skipped chain's bar is UNMEASURED 'chain not run'", g.get("status") == UNMEASURED
          and "chain not run" in str(g.get("state_evidence") or g.get("evidence")), str(g)[:200])
    fn = [r for r in rows if r.get("functional")]
    check("skipped chain's functional component is a row too", any(r["id"].startswith("gamma.") and r["status"] == UNMEASURED
                                                                 for r in fn), str([r["id"] for r in fn]))
    check("doc names what ran and what was skipped", doc.get("chains_selected") == ["alpha", "beta"]
          and doc.get("chains_skipped") == ["gamma"])
    check("a split run is not green", not cli.run_all_green(rows, EXPECTED))

    print("selftest_incremental: %s (%d failed)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
