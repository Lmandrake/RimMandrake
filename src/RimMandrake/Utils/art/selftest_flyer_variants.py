#!/usr/bin/env python3
"""selftest_flyer_variants.py — the owner's variant picks are alternate graphics (FLYER_VARIANTS_INSTALL_MORE_FACES_PLEASE).

Fleet Flier ("Use B, C, D as variants. They're beautiful!") and Murrelith ("B, C, D, E , F, G, H are all beautiful and
wonderful."). The letters are the columns of the snapshots he ruled on, since rebuilt with other letters; the shas below
are copied from those: fleetflier_alien snapshot at 2c3a7f10e3, flyer_north_redraw snapshot at 9a08e9fe3f.

For each creature, from parsed XML, the PNGs on disk and the art ledger:
  * the base graphic draws the main pick, one alternate per other letter, and nothing else;
  * alternateGraphicChance gives every picture the same share;
  * every facing is byte-equal to the column he ruled on, or (alternates only) is that column after the roster rescale
    he ordered by card (RESCALE_CARD): the ledger's prev chain from the file reaches the pinned sha, every step on the
    way is under that card, and the pixels are still his column's, moved or evenly scaled (same_art);
  * every alternate's facing has a ledger install tied to a ruling carrying his words.

The pins stay what he ruled on. 8605d39e4b moved 13 of these pictures under that card; a rescale is the only thing that may.
"""
from __future__ import annotations

import hashlib
import io
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

REPO = Path(__file__).resolve().parents[4]
EVENTS = REPO / "infrastructure/state/art/events"
ANIMAL = "Things/Pawn/Animal"
RULED_COMMIT = "67a8bfeabf"  # the commit that installed every ruled column, byte-equal to the pins
RESCALE_CARD = "Rescale all ~345 (scripted rescale, body size untouched)"
ALPHA_OUTLINE = 8  # faint halo pixels stretch a raw alpha bbox
ALPHA_SOLID = 128
MAX_ASPECT_DRIFT = 0.02  # a rescale keeps the outline's shape: bbox w and h scale alike
MAX_RGB_DRIFT = 15.0  # mean per-channel, opaque pixels. Measured: his rescaled columns at most 10.5, a different column at least 38.9

CASES = [
    {"kind": "RM_FleetFlier", "mod": "src/RimMandrake/TheForge", "defs": "Defs/ThingDefs_Races/RM_FleetFlier.xml",
     "base": f"{ANIMAL}/RM_FleetFlier/RM_FleetFlier", "said": "Use B, C, D as variants",
     "main": {"south": "a51f796ab1a6", "east": "ca55948c3b70", "north": "ccd8b08dc4f5"},
     "alts": {"B": {"south": "45ce9cdb339e", "east": "88fdf28220e1", "north": "b70b4ee7347c"},
              "C": {"south": "1749a36dd973", "east": "ea1762ebba0c", "north": "978d2dafdaac"}}},
    {"kind": "RM_Murrelith", "mod": "src/RimMandrake/FeverWood", "defs": "Defs/ThingDefs_Races/RM_FeverWoodBirds.xml",
     "base": f"{ANIMAL}/RM_FeverWoodBirds/RM_Murrelith", "said": "are all beautiful and wonderful",
     "main": {"south": "0c867cabba1d", "east": "d27f262073e7", "north": "dc4f8d33a1d4"},
     "alts": {"C": {"south": "a229dad60388", "east": "641a15c1be9d", "north": "21cb2c25114c"},
              "D": {"south": "4cf8b40151e4", "east": "d72a08a2064b", "north": "384c97f7c94e"},
              "E": {"south": "f529f88240d4", "east": "12c76db6b423", "north": "62e4cf875a47"},
              "F": {"south": "5cf46eea6825", "east": "9cb5b19c17b1", "north": "21fdabcf883e"},
              "G": {"south": "5e3371935d6a", "east": "db1a170d870a", "north": "db899189ce25"},
              "H": {"south": "0bf1f96e97ca", "east": "4cf5bdffe576", "north": "8140e74b3c63"}}},
]


def ledger() -> tuple[dict, dict, dict]:
    """({mod/rel: latest live event}, {ruling id: event}, {mod/rel: {sha: live event}}) from every seat's art events."""
    live, rulings, history = {}, {}, {}
    for f in sorted(EVENTS.glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            if e.get("type") == "live":
                live[f"{e.get('mod')}/{e.get('rel')}"] = e
                history.setdefault(f"{e.get('mod')}/{e.get('rel')}", {})[e.get("sha")] = e
            if e.get("id"):
                rulings[e["id"]] = e
    return live, rulings, history


def same_art(ruled: bytes, now: bytes) -> str | None:
    """None if `now` is `ruled` moved or evenly scaled; else what differs. Compares the alpha bboxes, resampled to match."""
    a, b = (Image.open(io.BytesIO(x)).convert("RGBA") for x in (ruled, now))
    box_a, box_b = (x.getchannel("A").point(lambda v: 255 if v > ALPHA_OUTLINE else 0).getbbox() for x in (a, b))
    if not box_a or not box_b:
        return "an empty picture"
    wa, ha, wb, hb = box_a[2] - box_a[0], box_a[3] - box_a[1], box_b[2] - box_b[0], box_b[3] - box_b[1]
    if abs(wb / wa - hb / ha) > MAX_ASPECT_DRIFT:
        return f"outline {wa}x{ha} became {wb}x{hb}"
    a = a.crop(box_a).resize((wb, hb), Image.LANCZOS)
    b = b.crop(box_b)
    solid = ImageChops.multiply(*(x.getchannel("A").point(lambda v: 255 if v >= ALPHA_SOLID else 0) for x in (a, b)))
    if not solid.getbbox():
        return "no opaque pixel in common"
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    drift = sum(ImageStat.Stat(diff, solid).mean) / 3
    return f"colours drift {drift:.1f}" if drift > MAX_RGB_DRIFT else None


def ruled_bytes(mod: str, rel: str) -> bytes:
    """The column as installed at RULED_COMMIT; raises if git cannot produce it, so a blind instrument is not a pass."""
    return subprocess.run(["git", "-C", str(REPO), "show", f"{RULED_COMMIT}:{mod}/Textures/{rel}"],
                          check=True, capture_output=True).stdout


def descent_fault(by_sha: dict, sha: str, want_sha: str, said: str, rulings: dict) -> str | None:
    """Walk the ledger from `sha` to the pinned column. None if every step is the rescale card and the root carries his words."""
    seen = set()
    while sha and sha not in seen:
        seen.add(sha)
        e = by_sha.get(sha)
        if not e:
            return f"ledger chain breaks at {sha[:12]}"
        words = json.dumps(rulings.get(e.get("ruling_id"), {}), ensure_ascii=False)
        if sha.startswith(want_sha):
            return None if said in words else f"ruling {e.get('ruling_id')} does not carry his words"
        if RESCALE_CARD not in words:
            return f"step {sha[:12]} is under ruling {e.get('ruling_id')}, not his rescale card"
        sha = e.get("prev")
    return "ledger chain never reaches the column he ruled on"


def check_case(c: dict, live: dict, rulings: dict, history: dict) -> list[str]:
    bad = []
    kinds = [k for k in ET.parse(REPO / c["mod"] / c["defs"]).getroot().findall("PawnKindDef")
             if k.findtext("defName") == c["kind"]]
    if len(kinds) != 1:
        return [f"{c['kind']}: {len(kinds)} PawnKindDefs, want 1"]
    k = kinds[0]
    base_paths = {(g.findtext("texPath") or "").strip() for g in k.findall("lifeStages/li/bodyGraphicData")}
    if base_paths != {c["base"]}:
        bad.append(f"{c['kind']}: body texPaths {sorted(base_paths)}")
    want = {f"{c['base']}V_{letter}" for letter in c["alts"]}
    got = [(li.findtext("texPath") or "").strip() for li in k.findall("alternateGraphics/li")]
    if sorted(got) != sorted(want):
        bad.append(f"{c['kind']}: alternates {got}, want {sorted(want)}")
    n = len(c["alts"])
    chance = float(k.findtext("alternateGraphicChance") or -1)
    if abs(chance - n / (n + 1)) > 0.001:
        bad.append(f"{c['kind']}: chance {chance}, want {n}/{n + 1}")
    tex = REPO / c["mod"] / "Textures"
    for name, stem, shas in [("main", c["base"], c["main"])] + [(x, f"{c['base']}V_{x}", s) for x, s in c["alts"].items()]:
        for facing, want_sha in shas.items():
            rel = f"{stem}_{facing}.png"
            p = tex / rel
            if not p.is_file():
                bad.append(f"{c['kind']} {name}: missing {rel}")
                continue
            sha = hashlib.sha256(p.read_bytes()).hexdigest()
            if name == "main":
                if not sha.startswith(want_sha):
                    bad.append(f"{c['kind']} {name} {facing}: {sha[:12]} is not the column he ruled on ({want_sha})")
                continue
            e = live.get(f"{c['mod']}/{rel}")
            if not e or e.get("sha") != sha:
                bad.append(f"{c['kind']} {name} {facing}: no ledger install of this sha")
                continue
            fault = descent_fault(history.get(f"{c['mod']}/{rel}", {}), sha, want_sha, c["said"], rulings)
            if not fault and not sha.startswith(want_sha):
                fault = same_art(ruled_bytes(c["mod"], rel), p.read_bytes())
            if fault:
                bad.append(f"{c['kind']} {name} {facing}: {sha[:12]} is not the column he ruled on ({want_sha}): {fault}")
    return bad


def main() -> int:
    live, rulings, history = ledger()
    if not live or not rulings:
        print("FAIL: art ledger read empty, instrument blind")
        return 1
    bad = [b for c in CASES for b in check_case(c, live, rulings, history)]
    for b in bad:
        print("FAIL:", b)
    if bad:
        return 1
    print(f"selftest_flyer_variants: PASS ({sum(len(c['alts']) + 1 for c in CASES)} pictures, 2 creatures)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
