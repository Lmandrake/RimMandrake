"""Proof that the second mountain pass left biomes and surface settlement tiles alone
(MOUNTAINS2_PLAN_DEPLOY_805_TILES_PACKED, clause "biomes ... must be unchanged").

    python3 src/RimMandrake/Utils/selftest_mountain2_base_pins.py [<save.rws>]

The pre-pass base (ASHKARR_DEV_START_2026-10-20_RECORDLINKS.rws) lives outside the repo, in
D:\\ClaudeWork\\backups\\saves_pre_cleanup_20261020T2220\\, so its tileBiome array and its sorted
surface settlement tiles are PINNED here as sha256 digests (measured from that base 2026-11-03).
The save must reproduce both digests exactly. When the base is readable, the pins are first
re-derived from it (a pin that no longer matches its own base is a FAIL, not a skip).
Sanity probes: a copy of the save's arrays with ONE biome tile changed, and with one settlement
tile moved, must each miss the pin - so a pass means the instrument can see one tile.
Default save: world/ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws. Exit 0 = unchanged.
"""
import hashlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mountain2_save_check as m2  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SAVE = os.path.join(REPO, "world", "ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws")
BASE = "/mnt/d/ClaudeWork/backups/saves_pre_cleanup_20261020T2220/ASHKARR_DEV_START_2026-10-20_RECORDLINKS.rws"
TILES = 21872
PIN_BIOME = "af24d020b96286f77fdf3267df9034fdcfd36d92dcf65cc58331ffd8a36135f6"
PIN_SETTL = "1cb873360838e5343cc354a5286370f170be094782c366e590b81775f71a6691"


def digest(seq):
    return hashlib.sha256(repr(tuple(seq)).encode()).hexdigest()


def main(argv):
    save = argv[0] if argv else SAVE
    fails = []
    arr, _, settl = m2.read_save(save)
    biome = arr["tileBiome"]
    if len(biome) != TILES:
        fails.append("tileBiome has %d tiles, not %d" % (len(biome), TILES))
    if os.path.exists(BASE):
        barr, _, bsettl = m2.read_save(BASE)
        if digest(barr["tileBiome"]) != PIN_BIOME or digest(bsettl) != PIN_SETTL:
            fails.append("pins no longer match the base %s" % BASE)
        nb = sum(x != y for x, y in zip(barr["tileBiome"], biome))
        print("base readable: %d biome tiles differ from it" % nb)
    else:
        print("base not readable at %s; using the pins alone" % BASE)
    # sanity probes: one changed tile must miss each pin
    other = next(v for v in set(biome) if v != biome[0])
    if digest((other,) + tuple(biome[1:])) == PIN_BIOME:
        fails.append("probe: a one-tile biome change still matches the pin")
    moved = list(settl)
    if moved:
        moved[0] = (moved[0] + 1) % TILES
    if digest(sorted(moved)) == PIN_SETTL:
        fails.append("probe: a moved settlement still matches the pin")
    db, ds = digest(biome), digest(settl)
    if db != PIN_BIOME:
        fails.append("tileBiome differs from the pre-pass base (sha %s)" % db[:12])
    if ds != PIN_SETTL:
        fails.append("surface settlement tiles differ from the pre-pass base (sha %s)" % ds[:12])
    print("biome sha %s, %d distinct biomes; %d surface settlements sha %s"
          % (db[:12], len(set(biome)), len(settl), ds[:12]))
    for f in fails:
        print("FAIL", f)
    print("PASS" if not fails else "FAIL")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
