"""northstar_driver plan for WeepingStones. Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod WeepingStones \\
      --plan src/RimMandrake/WeepingStones/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on the `weepingstones_solo` tier, a quicktest map >= 150x150):
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod WeepingStones \\
      --plan src/RimMandrake/WeepingStones/northstar_plan.py

EXPECT_MODS is `mandrake.rm.biomes`, not the dev folder's own packageId: WeepingStones ships composed
inside the Baroque Biomes mod (Biomes.compose.json), so `mandrake.rm.weepingstones` is never in
ModsConfig. This is the same packaging as Pyrelands."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_site                                    # noqa: E402

MOD = "WeepingStones"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)
NEED_GOD = False
RECT = None                 # the suite builds and clears its own pad; pre-flight checks the map, not a rect
preflight = northstar_site.preflight
# rows that need a live map and read UNMEASURED in a --mock run by construction (validation.LIVE_ONLY_UNMEASURED;
# the selftest's healthy check accepts the same set); cli.py run --mock sets them aside by name, never as a PASS
MOCK_LIVE_ONLY = ("dewsilk.tamed_mirrik_yield_cocoons", "oasis_flora.oasis_map_census")


def mock_extension(game, tool, p):
    """`cli.py run --mock`: the generic MockGame knows no jawa/map_zones, pens or husbandry jobs, so every fixture chain
    FAILed on it (NOT GREEN, 2026-11-03). Adopt it, once, as selftest_weepingstones.WSGame -- the same in-memory
    WeepingStones the selftest proves healthy and breakable -- and point Player.log at a hermetic temp file so the
    mock never reads the machine's real log. None = fall through to the generic mock (after adoption, always: a WSGame
    method that delegates to MockGame.handle must not loop back here)."""
    import game_paths
    import selftest_weepingstones as ST
    if isinstance(game, ST.WSGame):
        return None     # adopted: WSGame.handle answers its own tools first; a call reaching here falls through
    if True:
        game.__class__ = ST.WSGame
        game._ws_init()
        import tempfile
        fd, path = tempfile.mkstemp(prefix="ws_mock_", suffix=".log")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write("Bridge token: mock\n")
        game_paths.PLAYER_LOG = path
    fn = getattr(game, "t_" + tool.replace("/", "_"), None)
    return fn(p) if fn is not None else None
