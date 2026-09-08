import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

def rb():
    host, port, token = resolve_endpoint()
    return RimBridge(host, port, token)

# 18 creatures: kind, [drawBaby, drawJuv, drawAdult], [ageBaby, ageJuv, ageAdult]
CREATURES = [
    ("RSW_ColoClawFish",      [1.81, 2.63, 3.29], [0.05, 0.20, 1.0], "Colo"),
    ("RSW_AbyssalColo",       [1.98, 2.88, 3.60], [0.05, 0.20, 1.0], "Colo"),
    ("RSW_ThornbackColo",     [1.68, 2.45, 3.06], [0.05, 0.20, 1.0], "Colo"),
    ("RSW_Reefback",          [5.89, 8.56, 10.7], [0.10, 0.40, 2.0], "Colossi"),
    ("RSW_Starmaw",           [6.27, 9.12, 11.4], [0.10, 0.40, 2.0], "Colossi"),
    ("RSW_Lanternwhale",      [6.60, 9.60, 12.0], [0.10, 0.40, 2.0], "Colossi"),
    ("RSW_OpeeSeaKiller",     [1.24, 1.80, 2.25], [0.05, 0.20, 1.0], "Opee"),
    ("RSW_CrimsonOpee",       [1.36, 1.98, 2.48], [0.05, 0.20, 1.0], "Opee"),
    ("RSW_ShaleGorger",       [1.48, 2.15, 2.69], [0.05, 0.20, 1.0], "Opee"),
    ("RSW_SandoAquaMonster",  [3.91, 5.69, 7.11], [0.10, 0.40, 2.0], "Sando"),
    ("RSW_ElderSando",        [4.68, 6.80, 8.50], [0.10, 0.40, 2.0], "Sando"),
    ("RSW_StormSando",        [3.62, 5.26, 6.58], [0.10, 0.40, 2.0], "Sando"),
    ("RSW_Mee",               [0.55, 0.80, 1.00], [0.02, 0.10, 1.0], "Scalefish"),
    ("RSW_Faa",               [0.55, 0.80, 1.00], [0.02, 0.10, 1.0], "Scalefish"),
    ("RSW_Laa",               [0.66, 0.96, 1.20], [0.02, 0.10, 1.0], "Scalefish"),
    ("RSW_Yobshrimp",         [0.55, 0.80, 1.00], [0.05, 0.17, 1.0], "Swarm"),
    ("RSW_SiltLamprey",       [0.55, 0.80, 1.00], [0.05, 0.17, 1.0], "Swarm"),
    ("RSW_RustNipper",        [0.55, 0.80, 1.00], [0.05, 0.17, 1.0], "Swarm"),
]

COLS, ROWS = 3, 6
X0, Z0 = 38, 32
PITCH_X, PITCH_Z = 62, 36

def cell_center(i):
    """Grid cell for creature index i. Row 0 is the SOUTH row (low z)."""
    r, c = divmod(i, COLS)
    return X0 + c * PITCH_X, Z0 + r * PITCH_Z

def stage_positions(i):
    """[(x,z) baby, (x,z) juv, (x,z) adult] laid west->east inside the cell."""
    cx, cz = cell_center(i)
    d = CREATURES[i][1]
    off_baby = -int(round(d[1] / 2 + d[0] / 2 + 2))
    off_adult = int(round(d[1] / 2 + d[2] / 2 + 2))
    return [(cx + off_baby, cz), (cx, cz), (cx + off_adult, cz)]

STAGES = ["baby", "juvenile", "adult"]

def grid_label(i):
    r, c = divmod(i, COLS)
    return "%s%d" % ("ABCDEF"[r], c + 1)
