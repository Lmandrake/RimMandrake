"""load_policy.py - the ONE declared cold-load deadline policy (load_policy.json beside this file).

Before 2026-10-10 the tree carried five disagreeing budgets (launch_and_wait ~5-7 min, live_session 15 min,
belt_watchdog 25 min, docs 25/33 min) and one of them was read as a kill trigger. Every caller now asks here:

    import load_policy
    p = load_policy.profile_for(active_count)      # 'full' or 'minimal' numbers
    p["process_to_bridge_warn_s"]                  # past this: investigate, capture evidence
    p["process_to_bridge_deadline_s"]              # past this: the ATTEMPT ends; the process is NOT killed

kill_on_deadline is asserted False on load: a policy file that turns a clock into a kill is refused.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "load_policy.json")
KEYS = ("launch_to_process_s", "process_to_bridge_warn_s", "process_to_bridge_deadline_s",
        "bridge_to_dispatcher_s", "kill_existing_grace_s")


class PolicyError(ValueError):
    pass


def load(path=PATH):
    with open(path, encoding="utf-8") as fh:
        pol = json.load(fh)
    if pol.get("kill_on_deadline") is not False:
        raise PolicyError("%s: kill_on_deadline must be false - a deadline never kills by itself" % path)
    for name, prof in pol.get("profiles", {}).items():
        missing = [k for k in KEYS if not isinstance(prof.get(k), int) or prof[k] <= 0]
        if missing:
            raise PolicyError("%s: profile %s lacks positive int %s" % (path, name, missing))
        if prof["process_to_bridge_warn_s"] >= prof["process_to_bridge_deadline_s"]:
            raise PolicyError("%s: profile %s warn must be < deadline" % (path, name))
    for need in ("full", "minimal"):
        if need not in pol.get("profiles", {}):
            raise PolicyError("%s: profile %r missing" % (path, need))
    return pol


def profile_name(active_count, pol=None):
    """'minimal' for a small list, else 'full'. None (count unknown) is 'full' - the generous one."""
    pol = pol or load()
    if active_count is not None and active_count <= pol["minimal_max_active_mods"]:
        return "minimal"
    return "full"


def profile_for(active_count=None, pol=None):
    pol = pol or load()
    prof = dict(pol["profiles"][profile_name(active_count, pol)])
    prof["name"] = profile_name(active_count, pol)
    return prof


def active_count_from_modsconfig(path=None):
    """Parsed activeMods count of the ModsConfig the NEXT load reads, or None if unreadable."""
    import xml.etree.ElementTree as ET
    if path is None:
        try:
            from game_paths import MODS_CONFIG as path
        except ImportError:
            return None
    try:
        am = ET.parse(path).getroot().find("activeMods")
        return None if am is None else len(am.findall("li"))
    except (OSError, ET.ParseError):
        return None


if __name__ == "__main__":
    n = active_count_from_modsconfig()
    print("active mods %s -> profile %s: %s" % (n, profile_name(n), json.dumps(profile_for(n))))
