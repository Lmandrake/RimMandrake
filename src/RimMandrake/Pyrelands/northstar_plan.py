"""northstar_driver plan for Pyrelands (the suite in validation.py). Live, python.exe, bridge held, game up on the
`pyrelands` (or `ratchet_pilot`) tier, current map = the site fixture, reloaded and settled by northstar_site.py:
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands \\
      --plan src/RimMandrake/Pyrelands/northstar_plan.py
The deploy of the composed mod is gated by preflight_pyrelands.py gate A (rows 3.2.x, 3.8.1-3.8.7).

Wall time (MEASURED 2026-10-12, 250x250 site, 23-mod tier): waits <= 5000 ticks step ~60 ticks/s, longer ones run
Ultrafast at ~200 ticks/s. embergrass_regrow waits 423,000 ticks (~36 min) for a CALIBRATING row that reads
UNMEASURED whatever it sees; scorchfruit_spoils waits up to 270,000 (~22 min). Split the run so neither shell
timeout eats the other half; the driver rewrites --out after every chain (`partial: true`) either way:
  ... run --mod Pyrelands --plan <this> --skip-chains embergrass_regrow --out Transient/northstar/Pyrelands_main.json
  ... run --mod Pyrelands --plan <this> --chains embergrass_regrow --out Transient/northstar/Pyrelands_regrow.json

preflight(s) re-runs gate B (rows 3.8.8-3.8.11, 3.8.dialogs-B) on the live site and returns every non-PASS row as a
refusal, so cli.py exits 2 (REFUSED) instead of running the suite on a site gate B refused. MEASURED 2026-10-11: the
ratchet pilot ran the whole suite NOT GREEN on a fixture whose gate B had refused it (3.8.8 cells 59.0 vs outdoor
55.7, 3.8.10 a queued HarbingerTreeSpawn), because nothing tied the gate to the run."""
import os
import sys

MOD = "Pyrelands"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)
NEED_GOD = False
RECT = None


def _preflight_module():
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import preflight_pyrelands
    return preflight_pyrelands


def preflight(s, tile=None, expect_temp=50.0):
    """Gate B on the CURRENT map -> ['<row id>: <status> <observed>', ...]; [] = clean.

    tile=None checks biome/size/latitude/temperature without pinning the tile id (the site record is not on
    the plan's path). Gate B's own 3.8.10 probe clears the incident queue, so a refusal on 3.8.10 alone is cured
    by re-running; re-settle with northstar_site.py --reload-only rather than retrying blind."""
    P = _preflight_module()
    rows, _out = P.gate_b(s, None, tile=tile, expect_temp=expect_temp)
    return ["gateB %s: %s %s" % (r.id, r.status, str(r.observed)[:240]) for r in rows
            if r.required and r.status != P.PASS]
