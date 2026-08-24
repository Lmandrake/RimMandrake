#!/usr/bin/env python
"""Roll-test every authored PawnKindDef against the LIVE game and record what it actually
generated holding and wearing.

WHY THIS EXISTS, and why `jawa/pawnkind_audit` does not replace it
------------------------------------------------------------------
The audit answers "could this kind EVER arm itself" by checking `weaponMoney.max` -- the
CEILING. Generation rolls a value in the range. A kind whose ceiling affords a rifle can
still roll a number that affords nothing, and the audit reports it healthy.
`WEAPON_MONEY_ROLL_NOT_CEILING_1` measured 23 of 54 kinds fielding a bare pawn in 5 rolls
while the audit called every one of them fine. So: roll it, do not compute it.

Run from WSL with `python.exe` -- the bridge binds Windows loopback.
"""
import sys, os, json, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
from rimbridge_client import RimBridge, resolve_endpoint          # noqa: E402

# Faction each authored kind generates for, read off the LIVE faction list 2026-08-24.
# A kind whose faction is absent from the world spawns with `none`, which changes the gear
# roll -- so a miss here is a wrong answer, not a missing one.
FACTION_OF = {
    "Blackstar": "Pirate",                    "DeepDesert": "TribeCivil",
    "Deepwater": "Jawa_DeepwaterCompact",     "Droid":      "Jawa_FreeDroidEnclaves",
    "Empire":    "Empire",                    "Geonosian":  "Jawa_GeonosianFoundryHive",
    "Helix":     "Jawa_AscendantHelix",       "Homestead":  "OutlanderCivil",
    "Hutt":      "Jawa_HuttCartel",           "Junkers":    "Jawa_Junkers",
    "TradeMoot": "Jawa_IndigenousTribes",     "Wildsteam":  "Jawa_WildsteamClan",
}


def faction_for(kind):
    parts = kind.split("_")
    return FACTION_OF.get(parts[1] if len(parts) > 1 else "", "none")


def first(d, *names, default=None):
    """Read the first field name that is actually present.

    The companion's shapes are not uniform (`BRIDGE_ARG_SHAPES_INCONSISTENT_1`), and an
    absent key reads exactly like an empty one -- so record which name answered.
    """
    for n in names:
        if isinstance(d, dict) and n in d and d[n] is not None:
            return d[n]
    return default


def summarise(p):
    """Field names measured off a live `jawa/pawn_get` 2026-08-24, not guessed.

    Backstories are `childhood`/`adulthood` (NOT a `backstories` dict); equipment and
    apparel entries are keyed `def` (NOT `defName`) -- entry 3 of
    BRIDGE_ARG_SHAPES_INCONSISTENT_1 is exactly this trap, and reading `.defName` here
    returns [None] for every armed pawn, which looks identical to unarmed.
    """
    def names(seq):
        out = []
        for e in seq or []:
            out.append(e if isinstance(e, str) else first(e, "def", "defName", "label", default="?"))
        return out
    return {
        "id":          first(p, "thingId", "id"),
        "name":        first(p, "name", "nameShort"),
        "kindDef":     p.get("kindDef"),
        "faction":     first(p, "faction", "factionName"),
        "xenotype":    p.get("xenotype"),
        "equipment":   names(p.get("equipment")),
        "apparel":     names(p.get("apparel")),
        "apparelStuff": [(first(e, "def", default="?"), e.get("stuff"))
                         for e in (p.get("apparel") or []) if isinstance(e, dict)],
        "childhood":   p.get("childhood"),
        "adulthood":   p.get("adulthood"),
        "traits":      names(p.get("traits")),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kinds", required=True, help="file with one PawnKindDef defName per line")
    ap.add_argument("--rolls", type=int, default=5)
    ap.add_argument("--x", type=int, default=10)
    ap.add_argument("--z", type=int, default=10)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    # A line may be `KindDefName` (faction derived from the name) or `KindDefName=FactionDef`
    # for kinds whose name does not carry their faction -- mechs, vanilla tribals.
    kinds = []
    for line in open(a.kinds):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        kinds.append(tuple(line.split("=", 1)) if "=" in line else (line, None))
    host, port, token = resolve_endpoint()
    stamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    rows, errors = {}, []

    with RimBridge(host, port, token) as rb:
        # 4b: hostile pawns and a running clock is the combination that killed a colony.
        rb.call("rimworld/pause_game", {})
        for i, (kind, forced) in enumerate(kinds):
            fac = forced or faction_for(kind)
            try:
                r = rb.call("jawa/spawn_pawn", {"kindDef": kind, "x": a.x, "z": a.z,
                                                "faction": fac, "count": a.rolls})
            except Exception as e:                      # noqa: BLE001
                errors.append({"kind": kind, "stage": "spawn", "error": str(e)}); continue
            if not r.get("success"):
                errors.append({"kind": kind, "stage": "spawn",
                               "error": r.get("message"), "faction": fac}); continue

            # spawn_pawn returns pawns[].id in the BARE form (Human945). pawn_get takes
            # that; the rimworld/ tools would want Thing_Human945. Do not "normalise" it.
            ids = [first(x, "id", "pawnId", "thingId")
                   for x in (r.get("pawns") or []) if isinstance(x, dict) and x.get("ok")]
            pawns = []
            for pid in ids:
                try:
                    g = rb.call("jawa/pawn_get", {"pawn": str(pid)})
                    for p in (g.get("pawns") or []):
                        pawns.append(summarise(p))
                except Exception as e:                  # noqa: BLE001
                    errors.append({"kind": kind, "stage": "read", "pawn": pid, "error": str(e)})

            armed = sum(1 for p in pawns if p["equipment"])
            rows[kind] = {"faction": fac, "spawnRaw": {k: v for k, v in r.items()
                                                       if k not in ("operation",)},
                          "rolls": len(pawns), "armed": armed,
                          "bare": len(pawns) - armed, "pawns": pawns}
            print("%3d/%d %-32s faction=%-26s armed %d/%d"
                  % (i + 1, len(kinds), kind, fac, armed, len(pawns)), flush=True)

    out = {"capturedUtc": stamp, "rolls": a.rolls, "kindCount": len(kinds),
           "method": "live spawn roll, not weaponMoney.max -- see WEAPON_MONEY_ROLL_NOT_CEILING_1",
           "kinds": rows, "errors": errors}
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print("\nwrote %s  (%d kinds, %d errors)" % (a.out, len(rows), len(errors)))


if __name__ == "__main__":
    main()
