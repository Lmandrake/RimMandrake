#!/usr/bin/env python3
"""LIVE: stage fresh Lasat/Nelvaanian/Mimbanese/Ortolan pawns, shoot them in 4 facings, record proof.

Item XENO_HEADS_SCENE_PROVE_ALIENS_WEAR_THEM (owner, 2026-10-20: "I REALLY want to see a screenshot
of aliens with these head types installed."). The 2026-10-20 08:24 shots predate the 17:39-18:04 head
refit, so they show old art; this retakes them against whatever is deployed now and writes a manifest
that xeno_heads_installed_check.py binds to the deployed art by sha256.

RUN WITH python.exe (the bridge binds Windows loopback), on a loaded map with StarWarsRaces active:
    python.exe "$(wslpath -w src/RimMandrake/Utils/art/xeno_heads_live_shot.py)" [--at 70,70]

Steps: stage_xenotype_grid.py (clear, pale floor, spawn one stripped drafted pawn per xenotype, a
Baseliner first) -> jawa/pawn_get on each subject (headType, hair, apparel) -> move any old
xeno_heads_v3A/v3B shots to backups -> shoot_lineup_facings.py twice (A: Baseliner, Lasat, Nelvaanian;
B: Nelvaanian, Mimbanese, Ortolan) -> manifest. Exit 0 = every species drew its RSW_<S>_Head and all 8
shots were written by this run; 1 = a clause failed (printed); 2 = no bridge / no map.
The PNGs are a cache, not an observation: someone still has to LOOK at them before the owner does.
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
sys.path.insert(0, UTILS)
import rimbridge_client as rc  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

SPECIES = ("Lasat", "Nelvaanian", "Mimbanese", "Ortolan")   # grid reading order after the Baseliner
GROUP_A = ("Baseliner", "Lasat", "Nelvaanian")
GROUP_B = ("Nelvaanian", "Mimbanese", "Ortolan")
FACINGS = ("south", "east", "north", "west")
WIN = os.name == "nt"
GAME_MODS = os.environ.get("RM_GAME_MODS", r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods"
                           if WIN else "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods")
from game_paths import LOCALLOW  # noqa: E402
SHOTS = os.environ.get("RM_GAME_SCREENSHOTS", os.path.expanduser(
    r"~\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots") if WIN else
    LOCALLOW + "/Screenshots")
WORK = os.environ.get("RM_CLAUDEWORK", r"D:\ClaudeWork\rimmandrake" if WIN else "/mnt/d/ClaudeWork/rimmandrake")
MANIFEST = os.environ.get("RM_XENO_MANIFEST", os.path.join(WORK, "scratch", "xeno_heads", "xeno_heads_v3_manifest.json"))
HEAD_TEX = "Textures/RimMandrakeSW/Heads"


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def species_of(xeno):
    return "Baseliner" if not xeno else xeno.replace("RSW_RimMandrake", "")


def head_pngs():
    """Every deployed PNG of the four heads, keyed by its path under the mod folder."""
    out = {}
    for s in SPECIES:
        d = os.path.join(GAME_MODS, "StarWarsRaces", *HEAD_TEX.split("/"), s)
        for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if n.endswith(".png"):
                out[f"{HEAD_TEX}/{s}/{n}"] = sha(os.path.join(d, n))
    return out


def run(args):
    print("$", os.path.basename(args[0]), *args[1:])
    return subprocess.run([sys.executable] + args, timeout=300).returncode


def rect(cells):
    xs, zs = [c[0] for c in cells], [c[1] for c in cells]
    return "%d,%d,%d,%d" % (min(xs) - 1, min(zs) - 1, max(xs) - min(xs) + 3, max(zs) - min(zs) + 3)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--at", default="70,70", help="line-up centre cell x,z (not the map centre)")
    ap.add_argument("--zoom", type=float, default=11, help="camera rootSize for the close shots")
    a = ap.parse_args()
    started = time.time()
    xenos = ["Baseliner"] + [f"RSW_RimMandrake{s}" for s in SPECIES]
    rcode = run([os.path.join(UTILS, "stage_xenotype_grid.py"), "--at", a.at, "--per", "1", "--cols", "5",
                 "--spread", "4", "--shot", "xeno_heads_v3_grid", "--xenotypes", ",".join(xenos)])
    if rcode != 0:
        print(f"FAIL staging exited {rcode}")
        return 2 if rcode == 2 else 1

    fails, reads = [], {}
    host, port, token = rc.resolve_endpoint()
    if not token:
        print("UNMEASURED: no bridge token in Player.log")
        return 2
    with rc.RimBridge(host=host, port=port, token=token) as b:
        cx, cz = (int(v) for v in a.at.split(","))
        pawns = b.call("jawa/list_pawns", {}, check=False).get("pawns") or []
        near = [p for p in pawns if not p.get("dead") and p.get("x") is not None
                and abs(p["x"] - cx) <= 14 and abs(p["z"] - cz) <= 8]
        for p in near:
            g = b.call("jawa/pawn_get", {"pawn": str(p["id"])}, check=False)
            snap = (g.get("pawns") or [{}])[0]
            sp = species_of(snap.get("xenotype"))
            if sp in reads:
                fails.append(f"two subjects read as {sp}")
                continue
            reads[sp] = {"id": p["id"], "cell": [p["x"], p["z"]], "xenotype": snap.get("xenotype"),
                         "headType": snap.get("headType"), "hair": snap.get("hair"),
                         "apparel": len(snap.get("apparel") or [])}
    for s in SPECIES:
        r = reads.get(s)
        if r is None:
            fails.append(f"{s}: no subject on the map")
        elif r["headType"] != f"RSW_{s}_Head":
            fails.append(f"{s}: draws headType {r['headType']}, not RSW_{s}_Head")
        elif r["apparel"]:
            fails.append(f"{s}: still wears {r['apparel']} apparel (head hidden?)")
    if any(g not in reads for g in GROUP_A + GROUP_B):
        for line in fails:
            print("FAIL", line)
        print("FAIL: cannot frame the line-ups without every subject")
        return 1

    # Old shots of the same name are moved aside, so a file present below was written by THIS run.
    names = [f"xeno_heads_v3{g}_{f}.png" for g in "AB" for f in FACINGS]
    old = [n for n in names if os.path.isfile(os.path.join(SHOTS, n))]
    if old:
        bk = os.path.join(WORK, "backups", "xeno_heads_shots_" + time.strftime("%Y%m%d_%H%M%S"))
        os.makedirs(bk, exist_ok=True)
        for n in old:
            shutil.move(os.path.join(SHOTS, n), os.path.join(bk, n))
        print(f"moved {len(old)} old shots to {bk}")
    for g, members in (("A", GROUP_A), ("B", GROUP_B)):
        run([os.path.join(UTILS, "shoot_lineup_facings.py"), "--rect", rect([reads[m]["cell"] for m in members]),
             "--shot", f"xeno_heads_v3{g}", "--zoom", str(a.zoom)])
    shots = {}
    for n in names:
        pth = os.path.join(SHOTS, n)
        if not os.path.isfile(pth):
            fails.append(f"shot not written: {n}")
        elif os.path.getmtime(pth) < started:
            fails.append(f"shot older than this run: {n}")
        else:
            shots[n] = sha(pth)

    heads = head_pngs()
    if len(heads) < 12:
        fails.append(f"saw only {len(heads)} deployed head PNGs under {GAME_MODS}")
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump({"item": "XENO_HEADS_SCENE_PROVE_ALIENS_WEAR_THEM",
                   "taken_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                   "pawns": reads, "shots": shots, "head_pngs": heads, "failures": fails}, fh, indent=1)
    for line in fails:
        print("FAIL", line)
    print(f"{'PASS' if not fails else 'FAIL'}: {len(reads)} subjects read, {len(shots)}/8 shots written, "
          f"{len(heads)} head PNGs hashed; manifest {MANIFEST}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
