#!/usr/bin/env python3
"""Round-1 mockup generation for SW_SEA_MONSTERS_ART_1.

18 options (6 creatures x 3), side-profile concept PNGs on a chroma key.
Serial (1 worker), 420s timeout, one retry per call.
"""
import subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path("/mnt/d/Luke/dev/Rimworld")
OUT = REPO / "Transient" / "sea_monsters_mockups"
OUT.mkdir(parents=True, exist_ok=True)
GEN = REPO / "skills/generating-images/scripts/codex_image.py"

STYLE = ("Game creature sprite in the art style of RimWorld: flat cel shading, "
         "clean shapes, hard dark outline, muted painterly palette, full side-profile "
         "view facing left, the whole animal fully inside the frame with margin on "
         "every side, no text, no watermark")

CREATURES = {
    "opee": [
        "The opee sea killer from Star Wars: an armored deep-sea ambush predator the size of a rhino, "
        "crustacean-fish hybrid with a heavy spiny carapace, enormous gaping round mouth filled with "
        "needle teeth, two long lure antennae above the jaw, small tucked crab-like legs, mottled "
        "brown-and-olive shell",
        "The opee sea killer from Star Wars: squat armored anglerfish-crab hybrid, huge hinged mouth "
        "open showing a long sticky tongue, plated ridged shell with barnacle texture, lure stalks, "
        "dull sand-and-rust camouflage colors of a silt-bed ambusher",
        "The opee sea killer from Star Wars: compact heavily-armored ambush fish, shell like layered "
        "volcanic rock, glowing pale eyes, vast round tooth-ringed maw, short powerful claw-legs "
        "folded beneath, dark green-grey palette with pale belly",
    ],
    "colo": [
        "The colo claw fish from Star Wars: a giant serpentine eel predator, long pale segmented body, "
        "flat spade-shaped head with luminescent barbels, enormous hinged jaw bristling with curved "
        "fangs, two clawed pectoral limbs, ghostly white-and-violet deep-sea coloring",
        "The colo claw fish from Star Wars: monstrous deep-sea eel with a wide flattened arrow head, "
        "bioluminescent spots along the flanks, unhinging fanged jaw, hooked pectoral claws, sinuous "
        "ribbon body trailing into a fin, pale grey-green with glowing teal accents",
        "The colo claw fish from Star Wars: nightmare hatchet-headed sea serpent, armored skull plate, "
        "glowing lure whiskers, cavernous fang-lined mouth, muscular snake body with a long dorsal "
        "fin ridge, bone-white and deep purple palette",
    ],
    "sando": [
        "The sando aqua monster from Star Wars: a colossal aquatic leviathan with a muscular "
        "four-limbed mammalian body, webbed clawed paws, long finned tail, cat-like predatory head "
        "with a huge fanged maw, sleek grey-blue hide with a pale underbelly",
        "The sando aqua monster from Star Wars: whale-sized amphibious predator, powerful ape-like "
        "forelimbs with webbed claws, streamlined muscular torso, finned serpent tail, broad feline "
        "skull with rows of teeth, storm-grey hide scarred and barnacled",
        "The sando aqua monster from Star Wars: titanic sea beast blending big-cat and plesiosaur, "
        "four webbed limbs, ridged spine fins down the back, immense jaws mid-roar, deep slate-blue "
        "coloring with bioluminescent streaks along the flanks",
    ],
    "grazer": [
        "A small alien deep-sea shoal fish for a Star Wars ocean: palm-sized grazer with a rounded "
        "silver-blue body, large dark eye, delicate translucent fins, a line of soft bioluminescent "
        "dots along the flank, gentle and harmless",
        "A small alien reef-grazing fish: teardrop body with iridescent green-gold scales, fan tail, "
        "tiny beak-like mouth for scraping kelp, one glowing photophore stripe, schooling species",
        "A small alien deep-sea grazer fish: flat disc-shaped body like an alien angelfish, pale "
        "violet with darker banding, trailing filament fins, luminous blue eye spots",
    ],
    "swarm": [
        "A small alien deep-sea scavenger for a Star Wars ocean: a cat-sized armored isopod-like "
        "crawler, segmented chitin plates, many small legs, feathery antennae, pale bone-white "
        "carapace of a creature that lives on carcasses in the dark",
        "A small alien scavenger: lamprey-eel hybrid the size of a house cat, circular rasping "
        "sucker mouth ringed with teeth, slick dark eel body, milky blind eyes, swarm hunter drawn "
        "to blood",
        "A small alien deep-sea scavenger: crab-spider hybrid, spiny angular legs, low armored body, "
        "glowing red eye cluster, rust-and-black chitin, carrion eater that arrives in numbers",
    ],
    "colossus": [
        "A colossal gentle alien filter-feeder for a Star Wars ocean: a whale-scale creature so large "
        "it reads as terrain, vast cathedral-like baleen mouth permanently agape, hide encrusted with "
        "coral growths and drifting kelp, rows of soft bioluminescent lines, tiny distant eyes, calm "
        "and harmless",
        "A colossal neutral sea creature: mountain-sized filter feeder like a cross between a whale "
        "shark and a floating island, flat encrusted back carrying reef growth, huge passive mouth "
        "straining the water, faint glowing lattice patterns on its flanks",
        "A colossal alien filter-feeder: serene leviathan with a broad manta-like body, immense "
        "gill curtains, moss-green hide plated with age, chains of glowing blue lanterns hanging "
        "beneath its jaw, drifting slowly like weather",
    ],
}

def one(job):
    name, idx, prompt = job
    out = OUT / f"{name}_opt{idx}.png"
    if out.exists():
        return f"SKIP {out.name}"
    full = f"{prompt}. {STYLE}"
    for attempt in (1, 2):
        t0 = time.time()
        r = subprocess.run(
            [sys.executable, str(GEN), "generate", "--out", str(out),
             "--prompt", full, "--chroma-key", "#00ff00", "--timeout", "420"],
            capture_output=True, text=True)
        dt = int(time.time() - t0)
        if r.returncode == 0 and out.exists():
            return f"OK   {out.name} ({dt}s, try {attempt})"
        time.sleep(3)
    tail = (r.stderr or r.stdout or "").strip().splitlines()[-1:] or ["no output"]
    return f"FAIL {out.name}: {tail[0][:120]}"

jobs = [(n, i + 1, p) for n, ps in CREATURES.items() for i, p in enumerate(ps)]
with ThreadPoolExecutor(max_workers=1) as ex:
    for res in ex.map(one, jobs):
        print(res, flush=True)
print("DONE")
