"""stage6_site.py - sweep (optional) and read the current map before a Stage 6 check (Windows python: the bridge binds
Windows loopback). Prints `SITE_JSON {...}`; exit 0 when the site was read and is usable, 2 when not. Never a verdict."""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def judge(site, biome):
    """-> why the site cannot hold a check, or None."""
    if not site.get("biome"):
        return "no current map"
    if biome and site["biome"] != biome:
        return "the map is %s, not %s" % (site["biome"], biome)
    if site.get("hostile"):
        return "hostiles on the map: %s" % site["hostile"]
    return None


def read(rb, sweep):
    out = {}
    if sweep:
        r = rb.call("jawa/destroy_bulk", {"filter": "nonColonists", "dryRun": False}) or {}
        out["swept"] = r.get("matchedCount")
        rb.call("jawa/incident_queue_clear", {})
    info = rb.call("jawa/map_info", {}) or {}
    out["biome"] = info.get("mapBiome")
    out["ticksGame"] = (rb.call("jawa/time_clock", {}) or {}).get("ticksGame")
    live = [q for q in (rb.call("jawa/list_pawns", {}) or {}).get("pawns") or [] if q.get("spawned") and not q.get("dead")]
    out["hostile"] = [q.get("def") for q in live if q.get("hostile")][:10]
    out["colonists"] = sum(1 for q in live if q.get("isPlayer") and q.get("intelligence") == "Humanlike")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--biome")
    a = ap.parse_args(argv)
    try:
        from rimbridge_client import RimBridge, resolve_endpoint
        host, port, token = resolve_endpoint()
        # budget: danger=a dead bridge holds one game of the lane; never reached in the 14 days to 2026-11-24; no record of its
        # budget: run
        with RimBridge(host=host, port=port, token=token, timeout=120.0) as rb:
            site = read(rb, a.sweep)
    except Exception as e:  # noqa: BLE001 - a site that could not be read is said, never a verdict
        print("SITE UNREAD: %s: %s" % (type(e).__name__, e))
        return 2
    why = judge(site, a.biome)
    if why:
        print("SITE NOT USABLE: %s" % why)
        return 2
    print("SITE_JSON " + json.dumps(site))
    return 0


if __name__ == "__main__":
    sys.exit(main())
