#!/usr/bin/env python3
"""selftest_dewback_owned.py -- offline guard for MOOKEE_TRADE_ANIMAL_IDENTIFY_1.

"Mookee" (a pet name from RSW_Jawa_NamerPetSW) was worn by a donor `Dewback` from mlie.starwarsanimalcollection,
which has the donor's cartoonish art. The item closed because our port owns that animal. This test keeps it owned:
  1. RSW_Dewback is a ThingDef whose bodyGraphicData texPath is RimStarWars/SWBestiary/Dewback/Dewback, and the
     Dewback_{east,north,south}.png it reads exist as RGBA PNGs (owner's set C, 34bb644a86; footprint refit eafa695642);
  1b. the three bound PNGs ARE that art: their sha256 is pinned (the eafa695642 refit), and each one is proven to
     derive from set C by a VENDORED fingerprint (FIXTURE; the proof runs in a clean export with no git history):
     per facing, set C's alpha-box aspect and its alpha crop composited on grey and resized to FP_N x FP_N. The
     fixture records the set-C blob sha256s, which must equal the sheet snapshot's column C. Each bound facing,
     fingerprinted the same way, must match the aspect within 5% and sit within MAD_MAX (a Tauntaun probe must
     land above it, so the comparison can see a swap). `--regen` rebuilds the fixture from git at 34bb644a86;
  2. no def under src/ has the bare defName `Dewback` (that name is the donor's race);
  3. the donor packageId is absent from the shipping candidate list and from ModsConfig.FULL.LATEST (parsed
     activeMods; each list must hold all five DLC packageIds, or the parse is blind).
The defName scanner is probed on planted text first, so a blind scanner cannot pass.
Run bare: python3 src/RimStarWars/SWBestiary/selftest_dewback_owned.py   (exit 0 = clean; needs no git)
"""
import base64
import hashlib
import io
import json
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(ROOT, "src")
RACE = os.path.join(HERE, "Defs", "ThingDefs_Races", "RSW_Dewback.xml")
TEX = os.path.join(HERE, "Textures", "RimStarWars", "SWBestiary", "Dewback")
TEXPATH = "RimStarWars/SWBestiary/Dewback/Dewback"
LISTS = [os.path.join(ROOT, "infrastructure", "state", "modlists", n) for n in
         ("ModsConfig.FULL.CANDIDATE_DONORS_RETIRED_2026-10-18.xml", "ModsConfig.FULL.LATEST.xml")]
SNAPSHOT = os.path.join(ROOT, "infrastructure", "state", "art", "sheets", "dewback_reconcile_sheet_2026-10-16.snapshot.json")
SET_C_SHA = "34bb644a86"  # "Dewback reconciled: owner's set C"
# the bound art after eafa695642 (ROSTER_FACINGS_SHRINK_FRONT_VIEWS_STAND_TALL re-seated set C: shift, south shrunk).
# A deliberate art change updates these AND must still pass the set-C derivation below.
BOUND_SHA256 = {
    "east": "49577c5778b0ce45e6af732c7e7edf006573bad9025b931a85775f5761307ae7",
    "north": "c75607cd190968610c714bfd1dd362de56db01128d85bceb3956088523d47317",
    "south": "156f5ffa5b68397abd49ce9d9b5168fd9dd3974c1464ef4530bce27c3cf0a447",
}
FIXTURE = os.path.join(HERE, "Source", "selftest_fixtures", "dewback_setC_fingerprint.json")  # Source/ is not deployed
FP_N = 32
MAD_MAX = 8.0  # measured 2026-11-03 at FP_N=32: bound~C 0.00/0.27/0.31, Tauntaun~C 29.4/30.8/21.3
PROBE = os.path.join(HERE, "Textures", "Things", "Pawn", "Animal", "RSW_Tauntaun_Canon", "RSW_Tauntaun_Canon_%s.png")
DONOR = "mlie.starwarsanimalcollection"
DLC = ("ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
       "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey")
SKIP = {"obj", "bin", "Textures", ".git", "node_modules"}
COMMENT = re.compile(r"<!--.*?-->", re.S)
BARE = re.compile(r"<defName>\s*Dewback\s*</defName>")

FAILS = []


def check(ok, what):
    print("%s  %s" % ("ok  " if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


def bare_hits(text):
    return len(BARE.findall(COMMENT.sub("", text)))


def png_rgba(path):
    with open(path, "rb") as f:
        head = f.read(26)
    return head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR" and head[25] == 6 and struct.unpack(">I", head[16:20])[0] > 0


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def fingerprint(data):
    """(alpha-box aspect, FP_N x FP_N RGB of the alpha crop on grey) or None if the image has no opaque pixel."""
    from PIL import Image
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    box = im.split()[3].getbbox()
    if not box:
        return None
    im = im.crop(box)
    grey = Image.alpha_composite(Image.new("RGBA", im.size, (128, 128, 128, 255)), im).convert("RGB")
    return im.width / im.height, grey.resize((FP_N, FP_N), Image.LANCZOS)


def mad(fp, ref):
    """Mean abs RGB difference of two fingerprints; 255 if either is empty or the aspects disagree by >5%."""
    from PIL import ImageChops, ImageStat
    if fp is None or ref is None or abs(fp[0] - ref[0]) > 0.05 * ref[0]:
        return 255.0
    return sum(ImageStat.Stat(ImageChops.difference(fp[1], ref[1])).mean) / 3


def regen():
    """Rebuild FIXTURE from the set-C blobs in git; refuses unless each blob hashes to snapshot column C."""
    import subprocess
    with open(SNAPSHOT, encoding="utf-8") as f:
        column = json.load(f)["rows"]["RSW_Dewback"]["columns"]["C"]
    out = {"source": "git %s, %s" % (SET_C_SHA, os.path.relpath(TEX, ROOT).replace(os.sep, "/")),
           "fp_n": FP_N, "facings": {}}
    for facing in ("east", "north", "south"):
        rel = os.path.relpath(os.path.join(TEX, "Dewback_%s.png" % facing), ROOT).replace(os.sep, "/")
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (SET_C_SHA, rel)], capture_output=True)
        if r.returncode != 0 or sha256(r.stdout) != column.get(facing):
            sys.exit("regen: %s at %s is missing or does not hash to column C" % (rel, SET_C_SHA))
        aspect, img = fingerprint(r.stdout)
        out["facings"][facing] = {"blob_sha256": sha256(r.stdout), "aspect": round(aspect, 6),
                                  "rgb_b64": base64.b64encode(img.tobytes()).decode("ascii")}
    os.makedirs(os.path.dirname(FIXTURE), exist_ok=True)
    with open(FIXTURE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print("wrote %s" % FIXTURE)
    return 0


def check_art():
    try:
        from PIL import Image
    except ImportError:
        check(False, "PIL importable (the art comparison cannot run blind)")
        return
    if not os.path.isfile(FIXTURE):
        check(False, "set-C fingerprint fixture exists at %s (rebuild with --regen in a git clone)" % FIXTURE)
        return
    with open(SNAPSHOT, encoding="utf-8") as f:
        column = json.load(f)["rows"]["RSW_Dewback"]["columns"]["C"]
    with open(FIXTURE, encoding="utf-8") as f:
        fixture = json.load(f)
    check(fixture.get("fp_n") == FP_N, "fixture fingerprint size is %d" % FP_N)
    for facing in ("east", "north", "south"):
        with open(os.path.join(TEX, "Dewback_%s.png" % facing), "rb") as f:
            bound = f.read()
        check(sha256(bound) == BOUND_SHA256[facing], "Dewback_%s.png sha256 is the pinned set-C refit" % facing)
        entry = fixture.get("facings", {}).get(facing, {})
        check(bool(column.get(facing)) and entry.get("blob_sha256") == column.get(facing),
              "fixture set C %s was taken from the blob in the sheet snapshot's column C" % facing)
        raw = base64.b64decode(entry.get("rgb_b64", ""))
        if len(raw) != FP_N * FP_N * 3:
            check(False, "fixture set C %s fingerprint is %d bytes, not %d" % (facing, len(raw), FP_N * FP_N * 3))
            continue
        ref = (entry["aspect"], Image.frombytes("RGB", (FP_N, FP_N), raw))
        d = mad(fingerprint(bound), ref)
        check(d <= MAD_MAX, "Dewback_%s.png derives from set C (MAD %.2f <= %.1f)" % (facing, d, MAD_MAX))
        with open(PROBE % facing, "rb") as f:
            fp = fingerprint(f.read())
        dp = 0.0 if fp is None else mad((ref[0], fp[1]), ref)  # pixels only (aspect alone would catch it); empty = blind
        check(dp > MAD_MAX, "probe: Tauntaun %s is NOT set C on pixels alone (MAD %.2f > %.1f)" % (facing, dp, MAD_MAX))


def main():
    # probe: the scanner sees a bare Dewback, ignores a commented one and the port's name
    check(bare_hits("<ThingDef><defName>Dewback</defName></ThingDef>") == 1, "probe: scanner sees a bare Dewback def")
    check(bare_hits("<!-- <defName>Dewback</defName> --><defName>RSW_Dewback</defName>") == 0,
          "probe: scanner skips comments and RSW_Dewback")

    root = ET.parse(RACE).getroot()
    race = [d for d in root.iter("ThingDef") if (d.findtext("defName") or "").strip() == "RSW_Dewback"]
    check(len(race) == 1, "RSW_Dewback ThingDef defined once in RSW_Dewback.xml")
    paths = {(t.text or "").strip() for t in root.iter("texPath")}
    check(TEXPATH in paths, "RSW_Dewback.xml binds texPath %s" % TEXPATH)
    for facing in ("east", "north", "south"):
        p = os.path.join(TEX, "Dewback_%s.png" % facing)
        check(os.path.isfile(p) and png_rgba(p), "Dewback_%s.png is an RGBA PNG" % facing)
    check_art()

    hits, seen = [], 0
    for dp, dns, fns in os.walk(SRC):
        dns[:] = [d for d in dns if d not in SKIP]
        for fn in fns:
            if not fn.endswith(".xml"):
                continue
            seen += 1
            with open(os.path.join(dp, fn), encoding="utf-8", errors="replace") as f:
                if bare_hits(f.read()):
                    hits.append(os.path.relpath(os.path.join(dp, fn), ROOT))
    check(seen > 100, "scanned %d XML files under src/ (instrument sees the tree)" % seen)
    check(not hits, "no bare <defName>Dewback</defName> under src/%s" % ("" if not hits else ": " + ", ".join(hits[:5])))

    for lst in LISTS:
        active = [(li.text or "").strip().lower() for li in ET.parse(lst).getroot().find("activeMods")]
        name = os.path.basename(lst)
        check(all(d in active for d in DLC), "%s parses: all five DLC present (%d active)" % (name, len(active)))
        check(DONOR not in active, "%s does not load %s" % (name, DONOR))

    print("RESULT: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(regen() if sys.argv[1:] == ["--regen"] else main())
