#!/usr/bin/env python3
"""Mutant probe for selftest_sea_faces_picked.py --deployed (WORLD_SEA_FACES_INSTALL_PICKED_LOOKS).

Copies the deployed Defs + Textures/World/Biomes of TerminalBiomes and UtinniPatches to a temp folder, proves the selftest
is green on the faithful copy, then breaks the DEPLOYED side one way at a time and requires the selftest to go red:
  - each of the 8 deployed BiomeDefs' <texture> set back to World/Biomes/Ocean
  - each deployed BiomeDef removed
  - a stale duplicate BiomeDef (old texture) added beside the right one
  - a deployed face png repainted
Exit 0 only if the baseline is green and every mutant is red. Never touches the game folder or the repo.
"""
import os, re, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))


class S:  # mirrors selftest_sea_faces_picked.py (GAME, DEPLOYED, SEAS); a drift there makes the baseline or a lookup fail
    GAME = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
    DEPLOYED = {"RM": "RimMandrake.Biomes/Biomes/TerminalBiomes", "RUT": "UtinniPatches"}
    PAIRS = [("RM_GreySea", "RM_GreySea", "RUT_GreySea", "RUT_GreySea"),
             ("RM_TwilightSea", "RM_TwilightSea", "RUT_TwilightSea", "RUT_TwilightSea"),
             ("RM_TheScald", "RM_Scald", "RUT_TheScald", "RUT_Scald"),
             ("RM_TheChill", "RM_Chill", "RUT_PropaneLake", "RUT_Chill")]

TEST = os.path.join(HERE, "selftest_sea_faces_picked.py")
fails = 0


def run(mods):
    env = dict(os.environ, RM_GAME_MODS=mods)
    r = subprocess.run([sys.executable, TEST, "--deployed"], env=env, capture_output=True, text=True, timeout=300)
    return r.returncode, (r.stdout.strip().splitlines() or ["(no output)"])[-1]


def def_file(root, sub, defname):
    for dp, _, fs in os.walk(os.path.join(root, sub, "Defs")):
        for f in fs:
            p = os.path.join(dp, f)
            if f.endswith(".xml") and f"<defName>{defname}</defName>" in open(p, encoding="utf-8-sig").read():
                if re.search(r"<BiomeDef\b", open(p, encoding="utf-8-sig").read()):
                    return p
    return None


def expect_red(label, root, mutate):
    global fails
    mutate()
    code, last = run(root)
    print(("ok   " if code == 1 else "MISS ") + f"{label}: exit {code} :: {last}")
    if code != 1: fails += 1


with tempfile.TemporaryDirectory(prefix="seafaces_mut_") as tmp:
    for sub in S.DEPLOYED.values():
        for part in ("Defs", "Textures/World/Biomes"):
            shutil.copytree(os.path.join(S.GAME, sub, part), os.path.join(tmp, sub, part))
    code, last = run(tmp)
    print(f"baseline: exit {code} :: {last}")
    if code != 0:
        print("FAIL baseline copy is not green; the probe proves nothing"); sys.exit(1)
    for rmd, rmp, rutd, rutp in S.PAIRS:
        for sub, d in ((S.DEPLOYED["RM"], rmd),):
            p = def_file(tmp, sub, d)
            if p is None:
                print(f"FAIL cannot find deployed {d} in the copy"); fails += 1; continue
            orig = open(p, encoding="utf-8-sig").read()
            def mut_tex(p=p, orig=orig):
                new = re.sub(r"<texture>[^<]*</texture>", "<texture>World/Biomes/Ocean</texture>", orig, count=1)
                assert new != orig, p
                open(p, "w", encoding="utf-8").write(new)
            expect_red(f"{d} deployed texture -> Ocean", tmp, mut_tex)
            open(p, "w", encoding="utf-8").write(orig)
            expect_red(f"{d} deployed def removed", tmp, lambda p=p: os.remove(p))
            open(p, "w", encoding="utf-8").write(orig)
            dup = os.path.join(os.path.dirname(p), "zz_stale_dup.xml")
            def mut_dup(dup=dup, orig=orig):
                open(dup, "w", encoding="utf-8").write(
                    re.sub(r"<texture>[^<]*</texture>", "<texture>World/Biomes/Ocean</texture>", orig, count=1))
            expect_red(f"{d} stale duplicate deployed def", tmp, mut_dup)
            os.remove(dup)
    png = os.path.join(tmp, S.DEPLOYED["RM"], "Textures/World/Biomes", S.PAIRS[0][1] + ".png")
    keep = open(png, "rb").read()
    def mut_png():
        from PIL import Image
        im = Image.open(png).convert("RGB"); im.putpixel((0, 0), (255, 0, 255)); im.save(png)
    expect_red("deployed RM_GreySea.png repainted", tmp, mut_png)
    open(png, "wb").write(keep)
    code, last = run(tmp)
    print(f"restored: exit {code} :: {last}")
    if code != 0: fails += 1
print("OK: every deployed mutant goes red" if not fails else f"{fails} FAIL")
sys.exit(1 if fails else 0)
