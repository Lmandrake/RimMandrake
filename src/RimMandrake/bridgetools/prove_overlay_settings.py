#!/usr/bin/env python3
"""Live E1/E2 on ArchSmall, a fresh quicktest with FlowWorks and Explosive Knockback.
Keep the map and screenshot for inspection. Exit 1 for a wrong reading, 2 when it could not be made.
"""
import argparse
import hashlib
from pathlib import Path
import re
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Utils"))
import scene
from scene import cond as c

TOOL = "jawa/mod_settings_field"
FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
KB = "RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings"


class CouldNotLook(Exception):
    pass


def reading(reply, key):
    if key not in reply or reply[key] is None:
        raise CouldNotLook(f"{key} is unreadable: {reply}")
    return reply[key]


def proof(s, pit, blast):
    def call(tool, *, write=False, **params):
        r = s.raw(tool, **params)
        if r.get("success") is not True:
            error = scene.CallFailed if write and r.get("success") is False else CouldNotLook
            raise error(f"{tool}: {r}")
        return r

    def setting(type_name, field, value=None):
        args = {"action": "get"} if value is None else {"action": "set", "value": str(value), "driver": s.id}
        return call(TOOL, write=value is not None, typeName=type_name, field=field, **args)

    def spawn(x, z):
        return reading(reading(call("jawa/spawn_pawn", write=True, kindDef="Colonist", x=x, z=z, faction="player"), "pawns")[0], "id")

    def step():
        if not s.run(c.ticks(180), limit=180).hit:
            raise CouldNotLook("the pawn's flight could not be stepped to its end")

    def drop(p):
        x, z = p
        pawn = spawn(x - 3, z)
        try:
            reply = call("jawa/static_call", type="RimMandrake.FlowWorks.RM_PromotionProofs",
                         method="ProofForcedFlyer", args=f"{pawn},{x},{z}")
            if "launched=True" not in reading(reply, "result"):
                raise CouldNotLook(f"no forced flight for {pawn}: {reply}")
            step()
            sample = call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofTrap", args=pawn)
            latest = re.search(r"\blast=(\S+)", reading(sample, "result"))
            if not latest:
                raise CouldNotLook(f"no descent reading for {pawn}: {sample}")
            fall = re.search(r"(\d+)@.*_fall=([0-9.]+)", latest[1])
            if not fall or not pawn.endswith(fall[1]):
                raise CouldNotLook(f"the latest descent was not {pawn}: {sample}")
            return float(fall[2])
        finally:
            call("jawa/pawn_force_incapacitate", write=True, pawn=pawn, action="vanish")

    def detonate(p):
        x, z = p
        pawn = spawn(x + 3, z)
        try:
            call("jawa/explosion_at", write=True, at=f"{x},{z}", radius=3.9, damType="Bomb")
            step()
            pos = reading(reading(call("jawa/pawn_get", pawn=pawn), "pawns")[0], "position")
            return ((pos["x"] - x - 3) ** 2 + (pos["z"] - z) ** 2) ** 0.5
        finally:
            call("jawa/pawn_force_incapacitate", write=True, pawn=pawn, action="vanish")

    def config():
        folder = Path(reading(loaded, "dataFolder")) / "Config"
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file()}

    loaded = reading(call("jawa/running_mods", loadedOf="ours"), "loaded")
    original = config()
    fw0 = float(reading(setting(FW, "fallDamageMultiplier"), "value"))
    kb0 = float(reading(setting(KB, "strength"), "value"))
    x, z = pit
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            call("jawa/flowworks_excavation_drive", write=True, x=x + dx, z=z + dz, deepenLevels=4, setBodyWaterM=-1)
    if fw0 != 1:
        raise CouldNotLook(f"E1 needs baseline multiplier 1, read {fw0}")
    before = drop(pit)
    setting(FW, "fallDamageMultiplier", 2)
    tuned = reading(call(TOOL, typeName=FW, action="deviations"), "deviation")
    shot = call("jawa/take_screenshot", fileName="overlay_" + s.id)
    after = drop(pit)
    unchanged = config() == original
    call(TOOL, write=True, typeName=FW, action="revert", driver=s.id)
    restored = drop(pit)
    start = time.monotonic()
    throws = []
    for strength in (0.5, 0.75, 1, 1.5, 2):
        setting(KB, "strength", strength)
        throws.append(detonate(blast))
        unchanged &= config() == original
    reverted = reading(call(TOOL, write=True, typeName=KB, action="revert", driver=s.id), "deviation")
    unchanged &= config() == original
    e1 = before > 0 and 1.7 * before <= after <= 2.3 * before and abs(restored - before) <= 0.2 * before
    e2 = throws == sorted(throws) and throws[-1] > throws[0]
    record = (tuned["tainted"] is True and tuned["overlay"] != "none" and reverted["tainted"] is True
              and reverted["overlay"] == "none" and float(reading(setting(FW, "fallDamageMultiplier"), "value")) == fw0
              and float(reading(setting(KB, "strength"), "value")) == kb0)
    print(f"E1 injury {before:g} -> {after:g} -> {restored:g}; E2 distances {throws}, {time.monotonic() - start:.1f}s")
    print(f"Config unchanged={unchanged}; record and restore={record}; inspect OVERLAY {tuned['overlay']} in {shot.get('filePath')}")
    return 0 if e1 and e2 and unchanged and record else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pit", nargs=2, type=int, default=(25, 25), metavar=("X", "Z"))
    parser.add_argument("--blast", nargs=2, type=int, default=(55, 55), metavar=("X", "Z"))
    args = parser.parse_args()
    try:
        with scene.open("ArchSmall", needs={"map": "fresh:quicktest", "mods": ["FlowWorks", "ExplosiveKnockback"],
                                           "overlay": "none"}) as s:
            return proof(s, args.pit, args.blast)
    except scene.CallFailed as exc:
        print(f"FAILED: {exc}")
        return 1
    except (CouldNotLook, scene.Refused, scene.Fault, OSError, IndexError, KeyError, ValueError) as exc:
        print(f"COULD NOT LOOK: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
