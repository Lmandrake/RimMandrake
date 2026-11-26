#!/usr/bin/env python3
"""live_retired_mutator_ports.py - DONOR_MUTATORS_MIGRATE_TWENTY_TWO_CAME_HOME A1/A2, on the RUNNING game.

The need: our own defs replace the retired donors' world-tile mutators and landmarks, and they load in game. The list
of ports is design/RimMandrake/retired_mutators_port_map.json (every entry with a "new" name; dropped and
not-reproduced ones carry none).

What it reads (the running game; ModsConfig names only the next load):
  L1 jawa/mod_inventory holds every package that ships a port: mandrake.rm.biomes (EnvironmentalHazards, TheRot,
     TheSump and Pyrelands are composed into it and then have no package id of their own) and
     mandrake.rsw.swbestiary (Sarlacc); else exit 2 (COULD NOT LOOK).
  L2 jawa/get_defs resolves every port as its own type (TileMutatorDef/<new>, LandmarkDef/<new>). A vanilla control
     (TileMutatorDef/Caves) must resolve too, or the instrument is blind.
  L3 the game's Player.log holds no "Config error in <port>" line (a literal search per port name).
Not read: a generated map on a vent or tar tile. The vent ports reuse vanilla's vent layout and vanilla game
conditions (port map "how"), so a port that resolves with no config error places what vanilla places; a map scene
would test vanilla (cheaper_why).
Exit 0 = holds, 1 = a reading refutes it, 2 = no reading. Run under python.exe with RM_DATA_ROOT set.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

PACKAGES = ("mandrake.rm.biomes", "mandrake.rsw.swbestiary")   # EnvironmentalHazards etc. are composed into biomes
PORT_MAP = os.path.join(REPO, "design/RimMandrake/retired_mutators_port_map.json")


def ports():
    d = json.load(open(PORT_MAP))
    return sorted({"%s/%s" % (k, v["new"]) for k in ("TileMutatorDef", "LandmarkDef") for v in d[k].values() if v.get("new")})


def main():
    want = ports()
    host, port, token = rb.resolve_endpoint()
    S = rb.RimBridge(host=host, port=port, token=token, timeout=120.0)
    S.connect()

    def call(tool, **p):
        r = S.call(tool, p) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:
                pass
        return r

    inv = json.dumps(call("jawa/mod_inventory")).lower()
    absent = [p for p in PACKAGES if '"%s"' % p not in inv]
    if absent:
        print("UNMEASURED: not in the RUNNING mod list (jawa/mod_inventory): %s" % ", ".join(absent))
        return 2
    res = call("jawa/get_defs", defs=";".join(want + ["TileMutatorDef/Caves"]), fields="label", limit=200)
    rows = res.get("defs") or res.get("rows") or []
    found = {r.get("defName") for r in rows if isinstance(r, dict) and r.get("found", True)}
    if "Caves" not in found:
        print("UNMEASURED: the vanilla control TileMutatorDef/Caves did not resolve: the instrument is blind (%s)"
              % res.get("message"))
        return 2
    fails = ["L2: %s does not load in the running game" % w for w in want if w.split("/", 1)[1] not in found]

    log = None
    for cand in rb._player_log_candidates():
        if os.path.isfile(cand):
            log = cand
            break
    if not log:
        print("UNMEASURED: no Player.log of the running game found")
        return 2
    text = open(log, encoding="utf-8", errors="replace").read()
    for w in want:
        name = w.split("/", 1)[1]
        if "Config error in " + name in text:
            fails.append("L3: Player.log has a config error in %s" % name)

    for f in fails:
        print("FAIL:", f)
    if fails:
        return 1
    print("PASS: %d ports load in the running game (control Caves resolves); no config error names one (%s)"
          % (len(want), log))
    return 0


if __name__ == "__main__":
    sys.exit(main())
