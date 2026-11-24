#!/usr/bin/env python3
"""Visit 6 batch driver (ArchSmall): run stage-6 checks of version/test_table.json with their exact commands and write rows.jsonl.

    python.exe design\\concepts\\ExplosiveKnockback\\version\\in_game\\visit_3\\scripts\\batch.py --env env_minimal.json
        [--tests a,b,...] [--kind live_minimal] [--biome AridShrubland] [--suffix _rerun]

Run with python.exe (the bridge binds Windows loopback). Per check: every non-colonist destroyed (jawa/destroy_bulk
nonColonists, the incident queue emptied; --no-sweep keeps them), a site read (jawa/map_info biome and size, the clock,
non-player pawns left on the map), then the check's command (text before its "   (" note) with this interpreter, stdout to
evidence/<test><suffix>.txt, and one row: PASS when the command exits 0 and prints VERDICT PASS, FAIL when a scene reads
FAIL, else UNMEASURED (INVALID, ERROR, a timeout). The row carries the env file (the parsed activeMods), the source sha
and the deployed DLL md5 the caller names. visit 2's driver lived in Transient and was lost with its clone; this one is
committed beside the record it writes.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
VISIT = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(VISIT, *[".."] * 6))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
GAME_DLL = r"D:\ClaudeWork\rimmandrake\instances\b\game\Mods\ExplosiveKnockback\Assemblies\RimMandrakeExplosiveKnockback.dll"


def site(rb, biome):
    out = {}
    try:
        info = rb.call("jawa/map_info", {}) or {}
        out["biome"], out["size"] = info.get("mapBiome"), info.get("size") or [info.get("sizeX"), info.get("sizeZ")]
        out["ticksGame"] = (rb.call("jawa/time_clock", {}) or {}).get("ticksGame")
        pawns = (rb.call("jawa/list_pawns", {}) or {}).get("pawns") or []
        live = [q for q in pawns if q.get("spawned") and not q.get("dead")]
        hostile = [q.get("def") for q in live if q.get("hostile")]
        out["colonists_alive"] = sum(1 for q in live if q.get("isPlayer") and q.get("intelligence") == "Humanlike")
        out["wild_animals"] = sum(1 for q in live if not q.get("isPlayer") and q.get("intelligence") == "Animal")
        out["nonplayer_left"] = hostile[:10]
        out["map_ok"] = bool(out["biome"]) and (not biome or out["biome"] == biome)
    except Exception as e:  # noqa: BLE001 - an unreadable site is a row that does not count
        out["map_ok"], out["exc"] = False, repr(e)[:200]
    return out


def verdict(rc, text):
    m = re.search(r"VERDICT (\w+)", text)
    v = m.group(1) if m else "NONE"
    if rc == 0 and v == "PASS":
        return "PASS", v
    if v == "FAIL" or re.search(r"^\S+\s+FAIL\b", text, re.M):
        return "FAIL", v
    return "UNMEASURED", v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", required=True, help="env file in the visit folder (activeMods, game build)")
    ap.add_argument("--tests", default="")
    ap.add_argument("--kind", default="live_minimal")
    ap.add_argument("--biome", default="AridShrubland")
    ap.add_argument("--suffix", default="")
    ap.add_argument("--rows", default="rows.jsonl", help="planted runs write another file: never the visit rows")
    ap.add_argument("--sha", required=True, help="source sha the deployed DLL was built from")
    ap.add_argument("--timeout", type=int, default=500)
    ap.add_argument("--no-sweep", action="store_true", help="leave non-colonists on the map (default: destroy them first)")
    a = ap.parse_args()
    tt = json.load(open(os.path.join(VISIT, "..", "..", "test_table.json"), encoding="utf-8"))
    tests = [(k, t) for k, t in tt["tests"].items() if isinstance(t, dict) and str(t.get("stage")) == "6"
             and str(t.get("kind", "")).startswith("live")]
    if a.tests:
        want = a.tests.split(",")
        tests = [(k, t) for k, t in tests if k in want]
    else:
        tests = [(k, t) for k, t in tests if t.get("kind") == a.kind]
    ident = json.load(open(os.path.join(VISIT, a.env), encoding="utf-8"))     # build_match.py identity, one per load
    if ident.get("why"):
        sys.exit("identity file names a fault: %s" % ident["why"])
    md5 = hashlib.md5(open(GAME_DLL if os.name == "nt" else "/dev/null", "rb").read()).hexdigest()
    from rimbridge_client import RimBridge, resolve_endpoint
    host, port, token = resolve_endpoint()
    os.makedirs(os.path.join(VISIT, "evidence"), exist_ok=True)
    for tid, t in tests:
        cmd = t["command"].split("   (")[0].strip()
        argv = [sys.executable] + cmd.split()[1:]
        with RimBridge(host=host, port=port, token=token) as rb:
            if not a.no_sweep:      # every non-colonist off the map, the incident queue emptied (reviewmap.sweep_pawns)
                sw = rb.call("jawa/destroy_bulk", {"filter": "nonColonists", "dryRun": False}) or {}
                rb.call("jawa/incident_queue_clear", {})
            st = site(rb, a.biome)
            if not a.no_sweep:
                st["swept_noncolonists"] = sw.get("matchedCount")
        t0 = time.time()
        try:
            p = subprocess.run(argv, cwd=REPO, capture_output=True, text=True, timeout=a.timeout)
            rc, text = p.returncode, p.stdout + ("\n--- stderr ---\n" + p.stderr[-3000:] if p.stderr.strip() else "")
        except subprocess.TimeoutExpired as e:
            rc, text = -9, "TIMEOUT after %d s\n%s" % (a.timeout, (e.stdout or b"")[-3000:] if isinstance(e.stdout, bytes) else e.stdout)
        ev = os.path.join("design", "concepts", "ExplosiveKnockback", "version", "in_game", os.path.basename(VISIT), "evidence",
                          tid + a.suffix + ".txt")
        open(os.path.join(REPO, ev), "w", encoding="utf-8").write(text)
        v, rv = verdict(rc, text)
        held = [] if a.no_sweep else ["non-colonist pawns swept before the check", "incident queue emptied before the check"]
        row = {"test": tid, "verdict": v, "outcome": "SUCCESS" if v == "PASS" else "UNRESOLVED", "forbidden": [], "runner_verdict": rv, "rc": rc, "held": held,
               "site_checked": bool(st.get("map_ok")) and not st.get("nonplayer_left"), "site": st, "game": "archmagi.b",
                              "dll_md5": md5, "modlist": a.env, **ident, "game": "archmagi.b",
               "command": cmd, "evidence": ev.replace("\\", "/"),
               "wall_s": round(time.time() - t0, 1), "at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S PST")}
        with open(os.path.join(VISIT, a.rows), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        print("%-24s %-10s rc=%s %.0fs site=%s" % (tid, v, rc, row["wall_s"], row["site_checked"]), flush=True)


if __name__ == "__main__":
    main()
