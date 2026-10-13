"""Probe C: retire the quicktest colony on the loaded p8a (settle_site path), read back every colonist on the site,
then a governed 2000-tick step (clockgate.advance_chunk -> jawa/safe_advance) and ToxicBuildup before/after."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("src/RimMandrake/Utils", "src/RimMandrake/Utils/modcheck", "src/RimMandrake/Pyrelands"):
    sys.path.insert(0, os.path.join(HERE, *p.split("/")))
import northstar_site as S  # noqa: E402
import clockgate as cg  # noqa: E402
from northstar_driver.session import FastSession  # noqa: E402

OUT = {}


def tox(s):
    rows = s.call("jawa/list_pawns", includeHealth=True, faction="player", limit=100).get("pawns") or []
    return {str(p.get("name")): max([h.get("severity") or 0 for h in (p.get("health") or {}).get("hediffs") or []
                                     if (h.get("def") or h.get("defName")) == "ToxicBuildup"] or [0.0]) for p in rows}


def ncol(s, cur):
    r = s.call("rimworld/list_colonists", currentMapOnly=cur)
    return len(r.get("colonists") or [])


s = FastSession(strict=False)
with s:
    OUT["before"] = {"all": ncol(s, False), "site": None}
    mi = S.settle_site(s, 5, 1)
    OUT["settled"] = {"tile": mi.get("tile"), "biome": mi.get("mapBiome")}
    OUT["after_retire"] = {"all": ncol(s, False), "site": ncol(s, True),
                           "playerSettlements": [(o.get("id"), o.get("tile"), o.get("label")) for o in
                                                 s.call("jawa/world_objects_get", faction="PlayerColony", limit=50).get("objects") or []]}
    s.call("jawa/vitals", action="arm", ttlMin=30, row="probe_c_toxic", why="BENCH 13c toxic step")
    seq0 = (s.call("jawa/vitals").get("latched") or {}).get("seq") or 0
    OUT["tox0"] = tox(s)
    OUT["gov"] = cg.has_safe_advance(s)
    t0 = s.call("jawa/time_clock").get("ticksGame")
    OUT["executed"] = cg.advance_chunk(s, 2000)
    OUT["ticks"] = s.call("jawa/time_clock").get("ticksGame") - t0
    OUT["tox1"] = tox(s)
    ev = s.call("jawa/vitals", action="events", sinceSeq=seq0, limit=200).get("triggers") or []
    OUT["triggers"] = [(t.get("kind"), t.get("severity"), t.get("subject"), t.get("detail")) for t in ev]
    OUT["all_end"], OUT["site_end"] = ncol(s, False), ncol(s, True)
print(json.dumps(OUT, indent=1, default=str))
with open(os.path.join(HERE, "probe_c.json"), "w") as f:
    json.dump(OUT, f, indent=1, default=str)
