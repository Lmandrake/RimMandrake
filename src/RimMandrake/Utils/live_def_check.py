#!/usr/bin/env python3
"""live_def_check.py -- does the RUNNING game's def carry what a criterion says it must? One read-only jawa/get_defs call.

    python3 src/RimMandrake/Utils/live_def_check.py --has ThingDef/RM_Chittik=CompProperties_WoundLink [--has ...]

Each --has is DefType/defName=TOKEN: the def must resolve in the live game, and TOKEN must appear as a whole value in the
def's reported fields (a comp class, a field value). `--has DefType/defName` with no `=` asks only that it resolves.

Exit 0 every claim holds, 1 a claim is false (the game answered and said no: a real FAIL), 2 UNMEASURED (no bridge, an
answer that is not what get_defs returns, a def the reply never mentions). Callers hold the bridge lock; this never takes it.
RimBridge binds Windows loopback, so the call runs under Windows Python (python.exe), as rimbridge_client.py says.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLIENT = os.path.join(HERE, "rimbridge_client.py")
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


def judge(claims, reply):
    """-> (exit code, lines). `reply` is get_defs' JSON object."""
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
            seen.add(FAIL)
            lines.append("FAIL %s: does not resolve in the live game" % key)
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


def defs_param(keys):
    """get_defs' `defs` argument: SEMICOLON-separated DefType/defName pairs (JawaBenchTerrainTools.cs GetDefs).
    A comma-joined list reads as one unknown key and every claim comes back unmentioned."""
    return ";".join(keys)


def call_get_defs(keys, timeout):
    """-> (reply dict or None, why). Read-only; runs the client under Windows Python."""
    try:
        path = subprocess.run(["wslpath", "-w", CLIENT], capture_output=True, text=True, timeout=20).stdout.strip()
        r = subprocess.run(["python.exe", path, "--timeout", str(timeout), "--call", "jawa/get_defs",
                            "--json", json.dumps({"defs": defs_param(keys)})],
                           capture_output=True, text=True, timeout=timeout + 30, stdin=subprocess.DEVNULL)
    except (OSError, ValueError, subprocess.TimeoutExpired) as e:      # ValueError: UnicodeDecodeError on the reply bytes
        return None, "the bridge call did not finish: %s" % str(e)[:200]
    if r.returncode:
        return None, "bridge call exit %d: %s" % (r.returncode, (r.stderr or r.stdout)[-300:])
    try:
        return json.loads(r.stdout, object_pairs_hook=_no_duplicate_keys), None
    except (ValueError, RecursionError):
        return None, "the bridge answered something that is not JSON: %s" % r.stdout[:200]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--has", action="append", required=True, metavar="DefType/defName[=TOKEN]")
    ap.add_argument("--timeout", type=int, default=60)
    a = ap.parse_args(argv)
    try:
        claims = parse_claims(a.has)
    except ValueError as e:
        print("UNMEASURED: %s" % e)
        return UNMEASURED
    reply, why = call_get_defs(sorted({k for k, _ in claims}), a.timeout)
    if reply is None:
        print("UNMEASURED: %s" % why)
        return UNMEASURED
    try:
        code, lines = judge(claims, reply)
    except Exception as e:      # an uncaught crash would exit 1, which the runner records as a FAIL
        print("UNMEASURED: the reply could not be judged: %s: %s" % (type(e).__name__, str(e)[:200]))
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
        sys.stdout.write("UNMEASURED: " + ascii("%s: %s" % (type(e).__name__, str(e)[:200])) + "\n")
        return UNMEASURED


if __name__ == "__main__":
    sys.exit(safe_main())
