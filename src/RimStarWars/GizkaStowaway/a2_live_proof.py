"""GIZKA_STOWAWAY_UNMEASURED_ROWS_1 criterion A2 -- the live line's judge.

    python3 src/RimStarWars/GizkaStowaway/a2_live_proof.py --result <northstar_driver run result JSON>

Run right after `northstar_driver run --mod GizkaStowaway` (a LIVE run records itself into
infrastructure/state/modcheck_status.json through status.record_run). Exit 0 only when ALL of:

  RESULT (the same provenance `modcheck record` demands, record.provenance/judge):
    * mod GizkaStowaway, mode "live", not refused, not partial, no chain skipped, all_green true;
    * its mod_hash equals status.mod_hash of the mod folder NOW (a result older than the last edit is stale);
    * >= 50 bars, every bar PASS (no FAIL / UNMEASURED / SKIP / UNBUILT / UNCOVERED);
    * no bar or component carries validity "invalid" or freshness "reused@..." (never OK, record._invalid/_reused);
    * every required preflight check PASS;
    * every row that replaced one of the ten 2026-10-07 UNMEASURED rows (the item's A1 table) is present.
  LOAD: the RUNNING game (jawa/running_mods) holds exactly the `gizkastowaway` tier's resolved packageIds as a set
    (modset_builder.resolve_tier, the list `modcheck record` compares) -- no extra mod, none missing.
  REGISTRY: modcheck_status.json's GizkaStowaway entry was written by THIS result (source.result names it), its hash
    is the mod hash NOW, components.not_ok is empty, and its status is exactly status.verdict_for(True, walk) -- the
    verdict an all-green run earns at the walk's current state: GREEN, or DRAFT-CHECKLIST / PENDING-OWNER-REVIEW
    while the owner has not validated/reviewed the north star (that gate is his; it is not an UNMEASURED row).

Exit 1 with every failed clause printed. The checks are pure functions over injected readings (selftest seams); only
main() touches the bridge and the registry.
"""
import argparse
import json
import ntpath
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
MODCHECK = os.path.join(UTILS, "modcheck")
for _p in (UTILS, MODCHECK):
    if _p not in sys.path:
        sys.path.insert(0, _p)

MOD = "GizkaStowaway"
TIER = "gizkastowaway"
MIN_BARS = 50
# The rows that resolve the ten UNMEASURED rows of 2026-10-07 (item A1 table): each must have run and PASSed.
REQUIRED_BARS = (
    "discovery_triggers.gravship_landing_delivers_one_tame_gizka",
    "discovery_triggers.cooldown_blocks_a_second_discovery",
    "discovery_triggers.salvage_deconstruction_delivers_one_and_other_things_none",
    "discovery_triggers.trade_delivers_one_and_an_empty_trade_none",
    "discovery_triggers.quest_success_delivers_one_and_failure_none",
    "discovery_triggers.every_off_switch_silences_its_trigger",
    "fecundity_live.fecundity_replicates_while_fed_and_warm",
    "fecundity_live.population_cap_stops_breeding",
    "fecundity_live.cold_below_breeding_gate_stalls_replication",
    "chewing_live.infestation_stage_chews_powered_buildings",
    "cull_guilt_live.cull_weighs_on_watching_colonists",
    "global_breeding_slider.global_breeding_slider_rescales_donor_fields",
    "fecundity_state.gizka_with_fecundity_carries_it_control_does_not",
    "bait_poison.poison_hediff_advances_on_a_gizka",
    "donor_patch.gizka_market_value_flattened_to_15",
)
ACCEPTED = ("GREEN", "DRAFT-CHECKLIST", "PENDING-OWNER-REVIEW")


def _invalid(x):
    return isinstance(x, dict) and x.get("validity") == "invalid"


def _reused(x):
    return isinstance(x, dict) and str(x.get("freshness") or "").startswith("reused@")


def result_failures(res, current_hash):
    """Every reason the driver result is not a fresh, live, all-PASS GizkaStowaway run. Pure."""
    out = []
    if res.get("mod") != MOD:
        out.append("result is for mod %r, not %s" % (res.get("mod"), MOD))
    if res.get("mode") != "live":
        out.append("not a live run (mode=%r)" % res.get("mode"))
    if res.get("refused"):
        out.append("run REFUSED: %s" % str(res["refused"])[:200])
    if res.get("aborted"):
        out.append("run ABORTED: %s" % str(res["aborted"])[:200])
    if res.get("partial") is not False:
        out.append("partial run (partial=%r)" % res.get("partial"))
    if res.get("chains_skipped"):
        out.append("chains skipped: %s" % res["chains_skipped"])
    if res.get("all_green") is not True:
        out.append("all_green is %r" % res.get("all_green"))
    rh = res.get("mod_hash")
    if not current_hash:
        out.append("current mod hash unreadable")
    elif rh != current_hash:
        out.append("STALE or missing mod_hash: run %s, mod now %s" % (str(rh)[:12], current_hash[:12]))
    bars = res.get("bars") or []
    if len(bars) < MIN_BARS:
        out.append("%d bars, fewer than %d" % (len(bars), MIN_BARS))
    bad = [(b.get("id"), b.get("status")) for b in bars if b.get("status") != "PASS"]
    if bad:
        out.append("%d bars not PASS: %s" % (len(bad), bad[:12]))
    flagged = [b.get("id") for b in bars if _invalid(b) or _reused(b)]
    flagged += ["%s.%s" % (c.get("chain"), c.get("name")) for c in res.get("components") or []
                if _invalid(c) or _reused(c)]
    if flagged:
        out.append("invalid or reused measurements: %s" % flagged[:12])
    pre = [(p.get("name"), p.get("status")) for p in res.get("preflight") or []
           if p.get("required") and p.get("status") != "PASS"]
    if pre:
        out.append("required preflight not PASS: %s" % pre[:8])
    ids = {b.get("id") for b in bars}
    missing = [r for r in REQUIRED_BARS if r not in ids]
    if missing:
        out.append("required rows absent: %s" % missing)
    return out


def load_failures(running, tier_pids, tier_problems=()):
    """The running load against the tier, as a SET (record.provenance's comparison). Pure."""
    out = ["tier %s: %s" % (TIER, p) for p in tier_problems or ()]
    if not tier_pids:
        out.append("tier %s could not be resolved" % TIER)
        return out
    if not running:
        out.append("running mod list unread (jawa/running_mods)")
        return out
    got, want = {p.lower() for p in running}, {p.lower() for p in tier_pids}
    if got != want:
        out.append("running load is not the %s tier: extra %s, missing %s"
                   % (TIER, sorted(got - want)[:8], sorted(want - got)[:8]))
    return out


def registry_failures(entry, current_hash, result_path, expected_status):
    """modcheck_status.json's entry for the mod against this run. Pure."""
    if not entry:
        return ["modcheck_status.json has no %s entry (the driver did not record the run)" % MOD]
    out = []
    src = ((entry.get("source") or {}).get("result")) or ""
    if not src or ntpath.basename(src.replace("/", "\\")) != ntpath.basename(result_path.replace("/", "\\")):
        out.append("registry entry was not written by this result (source.result=%r)" % src)
    if entry.get("hash") != current_hash:
        out.append("registry hash %s is not the mod hash now %s" % (str(entry.get("hash"))[:12], str(current_hash)[:12]))
    not_ok = (entry.get("components") or {}).get("not_ok")
    if not_ok is None or not_ok:
        out.append("registry components.not_ok is %r" % (not_ok if not_ok is None else not_ok[:12],))
    st = entry.get("status")
    if st not in ACCEPTED:
        out.append("modcheck status %r is not one of %s" % (st, ACCEPTED))
    elif st != expected_status:
        out.append("modcheck status %r, but an all-green run at the walk's current state earns %r" % (st, expected_status))
    if entry.get("refused"):
        out.append("registry entry refused: %s" % entry["refused"])
    return out


def judge(res, current_hash, running, tier_pids, tier_problems, entry, result_path, expected_status):
    return (result_failures(res, current_hash) + load_failures(running, tier_pids, tier_problems)
            + registry_failures(entry, current_hash, result_path, expected_status))


def _running_now():
    import runner
    import live_def_check
    import rimbridge_client as rb
    host, port, token = rb.resolve_endpoint()
    c = rb.RimBridge(host=host, port=port, token=token, timeout=60.0)
    c.connect()
    return live_def_check.running_ids(runner._rb_call(c, "jawa/running_mods", {"details": False, "assembly": ""}))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--result", required=True, help="northstar_driver run --out JSON (WSL path)")
    a = ap.parse_args(argv)
    import runner
    import status
    import northstar
    import modset_builder as mb
    with open(a.result, encoding="utf-8") as f:
        res = json.load(f)
    mod_dir = runner.find_mod_dir(MOD)
    current = status.mod_hash(mod_dir)
    pids, missing, refusals = mb.resolve_tier(TIER, mb.scan())
    problems = (["tier mods not installed: %s" % missing] if missing else []) + list(refusals)
    try:
        running = _running_now()
    except Exception as e:  # noqa: BLE001 -- an unread load is a failed clause, printed
        running = None
        print("jawa/running_mods raised (%s: %s)" % (type(e).__name__, e))
    entry = status.load().get(MOD)
    expected = status.verdict_for(True, northstar.find_walk(runner.ROOT, MOD), "", bool((entry or {}).get("owner_review")))
    fails = judge(res, current, running, pids, problems, entry, a.result, expected)
    print("A2 %s: %d bars, registry %s at %s, expected %s" % (
        "PASS" if not fails else "FAIL", len(res.get("bars") or []), (entry or {}).get("status"),
        str((entry or {}).get("hash"))[:12], expected))
    for x in fails:
        print("  - " + x)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
