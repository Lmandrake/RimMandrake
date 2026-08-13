"""Paint an impact crater, cell by cell, with no meteor and no cheating.

TECHNIQUE. A real crater is not a disc of one texture. It is four concentric
zones with fuzzy boundaries, and the fuzz is what sells it:

    0.00 - 0.30 R   melt sheet   dense ash, slag, almost nothing intact
    0.30 - 0.65 R   inner bowl   heavy ash thinning outward, shattered rock
    0.65 - 1.00 R   rim wall     rubble and chunks piled up, ash sparse
    1.00 - 1.60 R   ejecta       scattered debris on clean ground, rays

Two things stop it reading as a bullseye:
  * DITHERED BOUNDARIES. Each cell's zone is decided by radius plus a per-cell
    noise term, so the edges interlock instead of drawing a circle.
  * ELLIPSE + RAYS. Impacts are rarely vertical. The crater is squashed on one
    axis and ejecta is thrown along a preferred direction.

Deterministic: the noise is a hash of (x, z, seed), so the same seed paints the
same crater and a re-run is idempotent rather than additive.
"""
import math
import os
import sys

# This used to sys.path.insert a per-session scratchpad that held a throwaway
# `rb` shim -- a path that both encoded the old G: project root and expired with
# the session. Resolved from this file instead, matching core.py/terrain.py.
_UTILS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _UTILS not in sys.path:
    sys.path.insert(0, _UTILS)
from rimbridge_client import RimBridge, resolve_endpoint


class _Bridge(object):
    """The old shim's surface: one lazy connection, kwargs-style call()."""

    def __init__(self):
        self._c = None

    def call(self, tool, **params):
        if self._c is None:
            host, port, token = resolve_endpoint()
            self._c = RimBridge(host, port, token)
            self._c.__enter__()
        return self._c.call(tool, params)


rb = _Bridge()

ASH = "Filth_Ash"
RUBBLE = "Filth_RubbleRock"
SLAG = "ChunkSlagSteel"


def noise(x, z, seed):
    """Cheap deterministic hash noise in [0,1)."""
    h = (x * 73856093) ^ (z * 19349663) ^ (seed * 83492791)
    h &= 0x7FFFFFFF
    h = (h ^ (h >> 13)) * 1274126177
    h &= 0x7FFFFFFF
    return (h % 10007) / 10007.0


def paint(cx, cz, R=12, seed=7, squash=0.82, ray_dir=0.6):
    placed = {"ash": 0, "rubble": 0, "slag": 0}
    span = int(R * 1.7) + 1
    for dx in range(-span, span + 1):
        for dz in range(-span, span + 1):
            x, z = cx + dx, cz + dz
            # ellipse: squash one axis so it is not a perfect circle
            ex = dx
            ez = dz / squash
            d = math.sqrt(ex * ex + ez * ez) / R
            n = noise(x, z, seed)
            # dither the radius so zone edges interlock
            d += (n - 0.5) * 0.18

            ang = math.atan2(dz, dx)
            ray = 0.5 + 0.5 * math.cos((ang - ray_dir) * 3.0)   # 3 lobes

            if d < 0.30:
                if n < 0.92:
                    rb.call("rimworld/spawn_thing", defName=ASH, x=x, z=z); placed["ash"] += 1
                if n > 0.80:
                    rb.call("rimworld/spawn_thing", defName=SLAG, x=x, z=z); placed["slag"] += 1
            elif d < 0.65:
                if n < 0.72:
                    rb.call("rimworld/spawn_thing", defName=ASH, x=x, z=z); placed["ash"] += 1
                if n > 0.88:
                    rb.call("rimworld/spawn_thing", defName=RUBBLE, x=x, z=z); placed["rubble"] += 1
            elif d < 1.00:
                if n < 0.34:
                    rb.call("rimworld/spawn_thing", defName=ASH, x=x, z=z); placed["ash"] += 1
                if n > 0.62:
                    rb.call("rimworld/spawn_thing", defName=RUBBLE, x=x, z=z); placed["rubble"] += 1
                if n > 0.94:
                    rb.call("rimworld/spawn_thing", defName=SLAG, x=x, z=z); placed["slag"] += 1
            elif d < 1.60:
                fade = (1.60 - d) / 0.60
                if n < 0.30 * fade * ray:
                    rb.call("rimworld/spawn_thing", defName=RUBBLE, x=x, z=z); placed["rubble"] += 1
                if n > 1.0 - 0.10 * fade * ray:
                    rb.call("rimworld/spawn_thing", defName=SLAG, x=x, z=z); placed["slag"] += 1
    return placed


if __name__ == "__main__":
    cx, cz = 150, 150
    rb.call("rimworld/set_god_mode", enabled=True)
    out = paint(cx, cz, R=11, seed=7)
    print("placed:", out, "total", sum(out.values()))
    rb.call("rimworld/jump_camera_to_cell", x=cx, z=cz)
    rb.call("rimworld/take_screenshot", fileName="crater", suppressMessage=True)
    print("screenshot -> Screenshots/crater.png")
