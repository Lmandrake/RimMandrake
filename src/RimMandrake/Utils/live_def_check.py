#!/usr/bin/env python3
"""live_def_check.py -- does the RUNNING game's def carry what a criterion says it must? One read-only jawa/get_defs call.

    python3 src/RimMandrake/Utils/live_def_check.py --has ThingDef/RM_Chittik=CompProperties_WoundLink [--has ...]

Each --has is DefType/defName=TOKEN: the def must resolve in the live game, and TOKEN must appear as a whole value in the
def's reported fields (a comp class, a field value). `--has DefType/defName` with no `=` asks only that it resolves.

Exit 0 every claim holds, 1 a claim is false (the game answered and said no: a real FAIL), 2 UNMEASURED (no bridge, an
answer that is not what get_defs returns, a def the reply never mentions). Callers hold the bridge lock; this never takes it.

A def that does not resolve is a FAIL only when the mod that defines it is in the RUNNING load. Its owners are the repo's
mods whose XML carries <defName>NAME</defName>; the running load is jawa/running_mods (ModsConfig.xml names the NEXT
load, so a mod enabled after launch is absent here). Owner not running, or the running list unreadable: UNMEASURED. A def
no repo mod defines (a typo, a vanilla or donor def) stays a FAIL: the game answered and nothing explains the no.
A mod folded into the composed biomes mod loads under the composed packageId, so an owner or a --needs naming the member
is also met by the composed id (biomes_compose.folded_ids); without that, a composed def that fails to resolve could only
ever read UNMEASURED.

--needs PACKAGEID / --without PACKAGEID state a criterion's load condition ("with Quarry loaded", "on a tier carrying
Warcasket", "with Alpha Biomes absent"): unmet, or the running list unread, is UNMEASURED before any def is judged. A donor
def no repo mod defines is a FAIL when it does not resolve, so a criterion about a donor's def needs its --needs.
RimBridge binds Windows loopback, so the call runs under Windows Python (python.exe), as rimbridge_client.py says.
"""
import argparse
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
CLIENT = os.path.join(HERE, "rimbridge_client.py")
SRC = os.path.normpath(os.path.join(HERE, "..", ".."))      # the repo's src/: every mod we ship lives under it
PASS, FAIL, UNMEASURED = 0, 1, 2


def parse_claims(items):
    """-> [(defkey, token or None)]; ValueError on a claim that is not DefType/defName[=TOKEN]."""
    out = []
    for raw in items:
        key, _, token = raw.partition("=")
        key, token = key.strip(), token.strip()
        if "=" in raw and not token:
            raise ValueError("an empty TOKEN would weaken the claim to existence-only; drop the '=': %r" % raw)
        if key.count("/") != 1 or not all(key.split("/")):
            raise ValueError("not DefType/defName[=TOKEN]: %r" % raw)
        out.append((key, token or None))
    return out


def values(node):
    """Every scalar in a JSON tree, as strings: the token is matched against these whole, never as a substring."""
    if isinstance(node, dict):
        for v in node.values():
            yield from values(v)
    elif isinstance(node, list):
        for v in node:
            yield from values(v)
    elif node is not None:
        yield str(node)


def _no_duplicate_keys(pairs):
    """json keeps the LAST of a repeated key, so found:false,found:true would read as true: that is no answer."""
    keys = [k for k, _ in pairs]
    if len(set(keys)) != len(keys):
        raise ValueError("a JSON object repeats a key")
    return dict(pairs)


def _canon(d):
    """A record as the claim reads it: JSON text, so True and 1 stay different (python's == merges them)."""
    return json.dumps([d.get("found"), d.get("fields")], sort_keys=True, default=str)


def judge(claims, reply, owners=None, running=None):
    """-> (exit code, lines). `reply` is get_defs' JSON object. `owners` {defkey: set of lower-case packageIds defining
    it}; `running` the lower-case packageIds of the RUNNING load, or None when unread. With no `owners` an unresolved
    def is a FAIL, as before."""
    if not isinstance(reply, dict) or not isinstance(reply.get("defs"), list):
        return UNMEASURED, ["UNMEASURED: the reply is not a get_defs answer"]
    by_key, bad = {}, set()
    for d in reply["defs"]:
        if not isinstance(d, dict) or not isinstance(d.get("requested"), str) or not d["requested"]:
            return UNMEASURED, ["UNMEASURED: a def record without a string `requested`: %r" % (d,)]
        if d["requested"] in by_key and _canon(by_key[d["requested"]]) != _canon(d):
            bad.add(d["requested"])          # two records that disagree: neither is the answer
        by_key[d["requested"]] = d
    seen, lines = set(), []
    for key, token in claims:
        d = by_key.get(key)
        if d is None:
            seen.add(UNMEASURED)
            lines.append("UNMEASURED %s: the reply does not mention it" % key)
            continue
        if key in bad or not isinstance(d.get("found"), bool) or (
                token is not None and d.get("found") and not isinstance(d.get("fields"), (dict, list))):
            seen.add(UNMEASURED)
            lines.append("UNMEASURED %s: the record is malformed or contradicts another (found=%r)" % (key, d.get("found")))
            continue
        if not d.get("found"):
            if owners and key in owners and owners[key] is None:
                seen.add(UNMEASURED)
                lines.append("UNMEASURED %s: does not resolve, and the search for the mod that defines it failed" % key)
                continue
            mods = sorted((owners or {}).get(key) or ())
            if mods and running is None:
                seen.add(UNMEASURED)
                lines.append("UNMEASURED %s: does not resolve, and the running mod list is unread, so whether %s is "
                             "loaded is unknown" % (key, "/".join(mods)))
            elif mods and not set(mods) & set(running):
                seen.add(UNMEASURED)
                lines.append("UNMEASURED %s: does not resolve because %s is not in the RUNNING load (ModsConfig names "
                             "the next load)" % (key, "/".join(mods)))
            else:
                seen.add(FAIL)
                lines.append("FAIL %s: does not resolve in the live game%s" % (
                    key, " though %s is loaded" % "/".join(sorted(set(mods) & set(running))) if mods else ""))
            continue
        where = "%s from %s" % (key, d.get("packageId") or "?")
        if token is None:
            lines.append("PASS %s resolves" % where)
        elif token in set(values(d.get("fields"))):
            lines.append("PASS %s carries %s" % (where, token))
        else:
            seen.add(FAIL)
            lines.append("FAIL %s lacks %s" % (where, token))
    return (FAIL if FAIL in seen else UNMEASURED if UNMEASURED in seen else PASS), lines   # a real FAIL stands


def aliases(src=SRC):
    """-> {folded member packageId (lower): composed packageId}; None when the compose manifest cannot be read (then a
    member's absence cannot be established, so --without is UNMEASURED)."""
    try:
        sys.path.insert(0, HERE)
        import biomes_compose
        return biomes_compose.folded_ids(src)
    except Exception:
        return None


def loaded(pid, running, alias):
    """Is `pid` in the running load, directly or through the composed mod it is folded into?"""
    pid = pid.strip().lower()
    return pid in running or (pid in (alias or {}) and alias[pid] in running)


def condition(needs, without, running, alias):
    """-> (UNMEASURED, lines) when the criterion's load condition is unmet or unreadable, else (None, lines)."""
    if not needs and not without:
        return None, []
    if not all(p.strip() for p in list(needs) + list(without)):
        return UNMEASURED, ["UNMEASURED: an empty --needs/--without names no mod"]
    if alias is None and without:
        return UNMEASURED, ["UNMEASURED: the compose manifest is unread, so a mod folded into the composed one may be "
                            "loaded unseen: --without cannot be checked"]
    if running is None:
        return UNMEASURED, ["UNMEASURED: the running mod list is unread, so the load condition cannot be checked"]
    miss = [p for p in needs if not loaded(p, running, alias)]
    extra = [p for p in without if loaded(p, running, alias)]
    if miss or extra:
        return UNMEASURED, ["UNMEASURED: the running load %s; the criterion is about another load" % "; ".join(
            (["lacks %s" % ", ".join(miss)] if miss else []) + (["holds %s" % ", ".join(extra)] if extra else []))]
    return None, ["load condition met: %s" % ", ".join(["has %s" % p for p in needs] + ["lacks %s" % p for p in without])]


def with_aliases(owners, alias):
    """owners with each folded member's composed packageId added beside it."""
    alias = alias or {}
    return {k: (None if v is None else set(v) | {alias[p] for p in v if p in alias}) for k, v in owners.items()}


def defs_param(keys):
    """get_defs' `defs` argument: SEMICOLON-separated DefType/defName pairs (JawaBenchTerrainTools.cs GetDefs).
    A comma-joined list reads as one unknown key and every claim comes back unmentioned."""
    return ";".join(keys)


def mod_package_id(path, src=SRC):
    """-> the lower-case packageId of the mod holding `path` (nearest ancestor with About/About.xml), or None."""
    d = os.path.dirname(os.path.abspath(path))
    while d.startswith(os.path.abspath(src)) and len(d) >= len(os.path.abspath(src)):
        about = os.path.join(d, "About", "About.xml")
        if os.path.isfile(about):
            try:
                pid = ET.parse(about).getroot().findtext("packageId")
            except (ET.ParseError, OSError):
                return None
            return pid.strip().lower() if pid and pid.strip() else None
        d = os.path.dirname(d)
    return None


def def_owners(keys, src=SRC):
    """-> {defkey: set of packageIds} for the repo mods whose XML names <defName>NAME</defName>. Missing keys own nothing;
    a key whose search failed maps to None (owner unknown, so an unresolved def cannot be called a FAIL)."""
    out = {}
    for key in keys:
        name = key.split("/", 1)[1]
        try:
            r = subprocess.run(["grep", "-rlF", "--include=*.xml", "<defName>%s</defName>" % name, src],
                               capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired):
            out[key] = None
            continue
        if r.returncode not in (0, 1):          # 1 is grep's "no match"; 2 is an error, matches or not
            out[key] = None
            continue
        pids = {p for p in (mod_package_id(f, src) for f in r.stdout.splitlines() if f) if p}
        if pids:
            out[key] = pids
    return out


def running_ids(reply):
    """jawa/running_mods' reply -> lower-case packageIds, or None when it is not that answer."""
    rm = reply.get("result", reply) if isinstance(reply, dict) else None
    if not isinstance(rm, dict):
        return None
    ids = rm.get("packageIds")
    if not isinstance(ids, list) or not ids or not all(isinstance(x, str) and x for x in ids):
        return None
    return {x.lower() for x in ids}


def _bridge(tool, params, timeout, read_only_static=False):
    """-> (reply or None, why). Read-only; runs the client under Windows Python. read_only_static: declare a jawa/static_call
    a read (the client accepts it only for its reviewed READ_ONLY_STATIC_CALLS, else refuses with exit 3)."""
    try:
        path = subprocess.run(["wslpath", "-w", CLIENT], capture_output=True, text=True, timeout=20).stdout.strip()
        r = subprocess.run(["python.exe", path, "--timeout", str(timeout), "--call", tool, "--json", json.dumps(params)]
                           + (["--read-only-static"] if read_only_static else []),
                           capture_output=True, text=True, timeout=timeout + 30, stdin=subprocess.DEVNULL)
    except (OSError, ValueError, subprocess.TimeoutExpired) as e:      # ValueError: UnicodeDecodeError on the reply bytes
        return None, "the bridge call did not finish: %s" % str(e)
    if r.returncode:
        return None, "bridge call exit %d: %s" % (r.returncode, (r.stderr or r.stdout))
    try:
        return json.loads(r.stdout, object_pairs_hook=_no_duplicate_keys), None
    except (ValueError, RecursionError):
        return None, "the bridge answered something that is not JSON: %s" % r.stdout


def call_running_mods(timeout):
    """-> set of lower-case packageIds the RUNNING game loaded, or None."""
    reply, _ = _bridge("jawa/running_mods", {"details": False, "assembly": ""}, timeout)
    return running_ids(reply)


def call_get_defs(keys, timeout):
    """-> (reply dict or None, why). Read-only; runs the client under Windows Python."""
    return _bridge("jawa/get_defs", {"defs": defs_param(keys)}, timeout)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--has", action="append", required=True, metavar="DefType/defName[=TOKEN]")
    ap.add_argument("--needs", action="append", default=[], metavar="PACKAGEID",
                    help="the criterion's load holds this mod: UNMEASURED unless the RUNNING load has it")
    ap.add_argument("--without", action="append", default=[], metavar="PACKAGEID",
                    help="the criterion's load lacks this mod: UNMEASURED when the RUNNING load has it")
    ap.add_argument("--timeout", type=int, default=60)
    a = ap.parse_args(argv)
    try:
        claims = parse_claims(a.has)
    except ValueError as e:
        print("UNMEASURED: %s" % e)
        return UNMEASURED
    alias, running, pre = aliases(), None, []
    if a.needs or a.without:
        running = call_running_mods(a.timeout)
        code, pre = condition(a.needs, a.without, running, alias)
        if code is not None:
            print("\n".join(pre))
            print("VERDICT UNMEASURED")
            return code
    reply, why = call_get_defs(sorted({k for k, _ in claims}), a.timeout)
    if reply is None:
        print("UNMEASURED: %s" % why)
        return UNMEASURED
    try:
        owners = {}
        if isinstance(reply, dict) and isinstance(reply.get("defs"), list) and any(
                isinstance(d, dict) and d.get("found") is False for d in reply["defs"]):
            owners = with_aliases(def_owners(sorted({k for k, _ in claims})), alias)
            if owners and running is None:
                running = call_running_mods(a.timeout)
        code, lines = judge(claims, reply, owners, running)
        lines = pre + lines
    except Exception as e:      # an uncaught crash would exit 1, which the runner records as a FAIL
        print("UNMEASURED: the reply could not be judged: %s: %s" % (type(e).__name__, str(e)))
        return UNMEASURED
    print("\n".join(lines))
    print({PASS: "VERDICT PASS", FAIL: "VERDICT FAIL", UNMEASURED: "VERDICT UNMEASURED"}[code])
    return code


def safe_main(argv=None):
    """main(), where nothing may escape: an uncaught exception exits 1 and the runner would record it as a FAIL."""
    try:
        return main(argv)
    except SystemExit:
        raise
    except BaseException as e:
        sys.stdout.write("UNMEASURED: " + ascii("%s: %s" % (type(e).__name__, str(e))) + "\n")
        return UNMEASURED


if __name__ == "__main__":
    sys.exit(safe_main())
