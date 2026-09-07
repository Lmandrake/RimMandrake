#!/usr/bin/env python3
"""Round-1 mockups for LIVESTOCK_STARTER_TRIO_1 (onnik / karrask / moornak).

9 options (3 creatures x 3), side-profile concept PNGs on a chroma key, then
three labeled contact sheets. Pattern proven by SeaBeasts/art/gen_sea_mockups.py.
Skip-existing; rerunnable if Transient ages out. Art direction is the ruled
table in design/Jawa/proposals/ludicrous_livestock_deep_design.md.
"""
import subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path("/mnt/d/Luke/dev/Rimworld")
OUT = REPO / "Transient" / "livestock_mockups"
OUT.mkdir(parents=True, exist_ok=True)
GEN = REPO / "skills/generating-images/scripts/codex_image.py"

STYLE = ("Game creature sprite in the art style of RimWorld: flat cel shading, "
         "clean shapes, hard dark outline, muted painterly palette, full side-profile "
         "view facing left, standing on the ground, the whole animal fully inside the "
         "frame with margin on every side, no text, no watermark, and a GENUINELY "
         "TRANSPARENT background - output a real alpha channel, no backdrop, no floor, "
         "no shadow")

CREATURES = {
    "onnik": [
        "The onnik, a desert kiln-beast: an ox-sized squat quadruped shaped like a barrel with "
        "short thick legs, its shell a tortoise-carapace of kiln-brick segments with visible "
        "mortar-like seams, a faint heat-shimmer rising off its back, small placid head, "
        "terracotta and fired-clay colors",
        "The onnik, a living kiln: heavy squat tortoise-ox hybrid, dome shell built from cracked "
        "ceramic plates glowing faintly orange between the seams, stumpy elephantine feet, drowsy "
        "half-closed eyes, ash-grey and brick-red palette, a wisp of smoke from a blowhole vent",
        "The onnik kiln-belly: a round-bodied desert beast like a giant horned toad crossed with a "
        "potbelly stove, plated underbelly, chimney-like dorsal vents in a row along the spine, "
        "warm sandstone colors with soot streaks, contented expression",
    ],
    "karrask": [
        "The karrask, a molt-plate grazer: a calf-sized armadillo-pangolin beast, overlapping "
        "armor plates in muted desert tan and dusty brown, a single visible pale seam line along "
        "the flank where the next shed will split, low to the ground, short digging claws, small "
        "mild-mannered head",
        "The karrask molt-plate: pangolin-like quadruped with large keeled scale plates layered "
        "like roof tiles, one loose half-lifted plate showing the pale new shell beneath, stocky "
        "legs, lichen stains on the older plates, sandy grey-brown palette",
        "The karrask: an armored grazing beast like a horned armadillo the size of a sheep, broad "
        "hexagonal plate segments with weathered edges, dust-caked shell, a fresh bright band of "
        "new armor at the shoulder seam, calm downturned head cropping lichen",
    ],
    "moornak": [
        "The moornak, a grief-eater: a small-to-medium unsettling beast with matte-black faintly "
        "damp-looking hide, seven small dark eyes set asymmetrically across its brow, slow "
        "deliberate stance, slightly hunched, no visible mouth, quiet and watchful, near-black "
        "palette with a wet sheen",
        "The moornak: cat-large and wrong, smooth lightless black skin like oiled leather, a "
        "cluster of mismatched beady eyes on one side of its skull, thin careful limbs mid slow "
        "step, an air of eerie patience, charcoal-on-black palette with faint violet undertone",
        "The moornak grief-eater: a compact hunched creature draped in matte black hide that "
        "swallows light, many small unblinking eyes scattered across the head, short soft-footed "
        "legs, a posture of calm attention like a mourner at a grave, darkest palette with pale "
        "grey eye glints",
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
             "--prompt", full, "--timeout", "420"],
            capture_output=True, text=True)
        dt = int(time.time() - t0)
        if r.returncode == 0 and out.exists():
            return f"OK   {out.name} ({dt}s, try {attempt})"
        time.sleep(3)
    tail = (r.stderr or r.stdout or "").strip().splitlines()[-1:] or ["no output"]
    return f"FAIL {out.name}: {tail[0][:120]}"

def sheets():
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("SHEETS SKIPPED: no PIL"); return
    for name in CREATURES:
        opts = [OUT / f"{name}_opt{i}.png" for i in (1, 2, 3)]
        if not all(p.exists() for p in opts):
            print(f"SHEET {name}: missing options, skipped"); continue
        imgs = [Image.open(p).convert("RGBA") for p in opts]
        h = 440; pads = 8; label_h = 26
        scaled = []
        for im in imgs:
            w = int(im.width * (h - label_h - 2 * pads) / im.height)
            scaled.append(im.resize((w, h - label_h - 2 * pads)))
        W = sum(s.width for s in scaled) + pads * 4
        sheet = Image.new("RGBA", (W, h), (12, 12, 14, 255))
        d = ImageDraw.Draw(sheet)
        x = pads
        for i, s in enumerate(scaled, 1):
            d.text((x + 2, 6), f"{name} option {i}", fill=(230, 230, 225, 255))
            sheet.paste(s, (x, label_h + pads), s)
            x += s.width + pads
        outp = OUT / f"SHEET_{name}.png"
        sheet.convert("RGB").save(outp)
        print(f"SHEET {outp.name} written")

if __name__ == "__main__":
    jobs = [(n, i + 1, p) for n, ps in CREATURES.items() for i, p in enumerate(ps)]
    with ThreadPoolExecutor(max_workers=1) as ex:
        for res in ex.map(one, jobs):
            print(res, flush=True)
    sheets()
    print("DONE")
