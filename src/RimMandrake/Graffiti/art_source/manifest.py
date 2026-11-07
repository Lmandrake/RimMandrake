"""Every mark's art: what to generate and how to bake it. `python3 manifest.py gen [--workers N]` generates what's missing into GEN;
bake.py turns GEN into Textures/. Sizes are world cells on the wall's plane (see RM_GraffitiKernel.WallWorldHeight)."""
import os, subprocess, sys, threading, queue, json

GEN = "/mnt/d/ClaudeWork/rimmandrake/ralph_graffiti/gen3"
HOME = "/mnt/d/ClaudeWork/rimmandrake/ralph_graffiti/codexhome_w%d"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))

BASE = ("Fully transparent background, real alpha. Seen straight on, flat. Real paint on a wall, photographed and cut out, with no wall in the picture. "
        "It will be seen very small, about 60 pixels across, so the shape is simple and bold and every stroke is very thick, at least a tenth of the image's height. "
        "No outline around the shape, no shading, no gradient, no clean edge, no drop shadow, no letters, numbers or words of any alphabet, no logo, no real-world sign, no wall texture. ")
PIG = "Muted weathered pigment only: {c}. Never bright, never neon. "
BRUSH = "Made fast by one hand with a wide dry bristle brush: thick uneven strokes, bristle streaks where the brush runs dry, patchy coverage with gaps, ragged stroke ends, a few thin runs of paint falling straight down. "
RAG = "Smeared on with a rag or a bare hand: broad wiped smears, finger drags, thin and thick pressure, grimy, a few thin runs falling straight down. "
SPRAY = "Sprayed from a can held too close: soft fuzzy edges with fine overspray speckle, uneven pressure, the line fattening where the hand slowed, thin runs falling straight down from the heaviest spots. "
ROLLER = "Filled fast with a nearly dry paint roller then lined with a loaded brush: streaky horizontal roller bands, missed patches, thin runs falling straight down. "
CHALK = "Dragged on with a lump of charcoal and burnt lime, gritty and broken, the wall's tooth skipping through every stroke, no runs. "
STENCIL = "Sprayed through a crude hand-cut cardboard stencil, so the shape has blunt bridges, soft misted edges where the card lifted, and speckled overspray outside it, patchy, unevenly loaded, a couple of thin runs. "
PASTE = ("A wheat-pasted poster: one sheet of rough cheap paper, hand block-printed in two inks with a crude carved woodcut, torn at the edges with a chunk ripped away, wrinkled, "
         "paste stains at the edge, faded. Any writing on it is only meaningless carved marks. It fills the picture. ")
L2, L3 = "Wide format, twice as wide as it is tall, filling the width. ", "Very wide format, about three to one, filling the width. "
SQ = "Landscape format about four to three, filling the picture. "
PALE = "One colour only: pale off-white paint, so it can be tinted later. "

M = {}
def add(name, folder, width, mode, wear, prompt, pigmented=False, height=1.0):
    M[name] = dict(folder=folder, width=width, mode=mode, wear=wear, prompt=BASE + prompt, pigmented=pigmented, height=height)

F = "RM_Graffiti_"
# ------ tags: a pale hand, each mark writes it in its own pigment. Three hands per tag def.
TAGK = "A graffiti tag: one fast flowing signature that looks like wild handwriting but is no letters of any alphabet. "
for i, (d, t) in enumerate([("A", "looped, leaning hard to the right, an underline flick"), ("A", "two jagged peaks and a long slash through them"), ("A", "a tight knot of loops with a star-shaped flick"),
                            ("B", "tall thin spikes joined low like a crown of sticks, sprayed"), ("B", "fat lazy loops, one line never lifted"), ("B", "a broken zigzag with an arrow-shaped end"),
                            ("C", "squared blocky hooks, stiff and angry"), ("C", "a whip of a single line with a big bubble at the start"), ("C", "three strokes crossed and a halo ring flicked over them")]):
    add(f"tag_{d.lower()}_{i % 3}", F + "Tag_" + d, 1.25, "spray", 0.2 + 0.1 * (i % 3), TAGK + t.capitalize() + ". " + SPRAY + PALE + SQ, True)
for i, t in enumerate(["three different hands stacked, each a fast scribble", "a long row of small crowded scrawled signatures, some crossed out", "four fat scrawls side by side, each by another hand"]):
    add(f"rollcall_{i}", F + "Tag_RollCall", 2, "spray", 0.3, "A roll call of graffiti tags that spell no letters of any alphabet: " + t + ". " + SPRAY + PIG.format(c="chalk white, soot black, rust red, ochre") + L2)
# ------ throw-ups
for i, (d, t, c) in enumerate([("A", "fat round overlapping bubble shapes", "chalk fill, soot black line"), ("A", "lumpy melting bubble shapes", "rust red fill, soot line"),
                               ("B", "squat rounded blocks shouldering each other", "ochre fill, soot line"), ("B", "cloud-like puffed shapes with a hasty second line", "dull blue fill, chalk line")]):
    add(f"throwup_{d.lower()}_{i % 2}", F + "ThrowUp_" + d, 1.3, "brush", 0.2 + 0.12 * (i % 2), f"A graffiti throw-up: {t} that look like letters but spell nothing. " + ROLLER + PIG.format(c=c) + SQ)
for i, (t, c) in enumerate([("fat round bubble shapes in a row", "chalk fill, soot line"), ("bulging squared bubble shapes", "rust red fill, soot line"), ("drooping melted bubble shapes", "dull violet fill, chalk line"), ("tall crowded bubble shapes shouldering each other", "oxide green fill, chalk line")]):
    add(f"wide_{i}", F + "ThrowUp_Wide", 2, "brush", 0.2 + 0.08 * i, f"A wide graffiti throw-up: {t} that look like letters but spell nothing. " + ROLLER + PIG.format(c=c) + L2)
# ------ pieces
for i, (t, c) in enumerate([("sharp interlocking angular shapes like shattered letters, arrows thrown off them", "rust red, burnt orange, soot black, chalk"), ("huge rounded interlocked shapes with a hard second colour fading through them", "dull blue, lime white, soot black"),
                            ("tall spiky shapes leaning into each other, a crude sun behind", "ochre, oxblood, soot black"), ("flowing ribbon shapes knotting through each other", "oxide green, chalk, dull violet")]):
    add(f"piece_{'abcd'[i]}", F + "Piece", 3, "brush", 0.16, f"A full graffiti piece by someone good, a long wall-burner: {t}, that look like letters but spell nothing. Careful hand, rough materials. Painted with brush and can together: dense coverage, streaky fills, a soft misted glow behind, thin runs falling straight down. " + PIG.format(c=c) + L3)
# ------ vandal: the ugliest things on any wall. Violent, filthy, carelessly huge.
for i, t in enumerate(["furious tangled tar strokes with a brown filth smear dragged across them", "a mess of crossed-out slashes, black tar over sick yellow-brown, hand-prints wiped through it",
                       "a crude ugly face of three gashes and a smeared mouth, in tar and rust, wiped half away", "dozens of hateful stabbing strokes radiating from a blot of tar, filthy brown drips",
                       "a huge careless wipe of filth with a stick-drawn scribble dragged through it while wet", "black tar flung and scraped in big arcs, greasy brown underneath, disgusting"]):
    add(f"vandal_{i}", F + "Vandal", 1.5, "brush", 0.15, "The ugliest vandalism imaginable, hateful, filthy, no skill at all: " + t + ". " + RAG + PIG.format(c="soot black tar, sick greasy brown, dull rust") + SQ)
# ------ small glyphs: scratches gouged, tallies, warnings, cross-outs
for i, t in enumerate(["four parallel claw gouges slashed downward at a slant", "two sets of deep crossing gouges", "one long raking scrape with splintered ends"]):
    add(f"scratches_{i}", F + "Scratches", 1, "scratch", 0.1, "Gouges scratched into a surface with a nail, no paint at all: " + t + ". Pale bare exposed material with a darker lip along one side of each gouge, jagged and irregular, very thick. " + SQ)
for i, t in enumerate(["two neat bundles of tally strokes", "one bundle of tally strokes and three spare strokes", "three bundles of short tally strokes, the last unfinished"]):
    add(f"tally_{i}", F + "TallyMarks", 1, "chalk", 0.12, "Prisoner's tally marks counting days: " + t + ", careful, patient, small. " + CHALK + PALE + SQ, True, height=0.75)
for i, (t, c) in enumerate([("a jagged eye with a slash through it, meaning keep out", "rust red"), ("three spikes pointing at a ragged blot, meaning danger here", "ochre and soot"), ("a skull-like blot with two gouged eyes and no teeth, meaning death", "chalk and soot"), ("a crude open maw of teeth, meaning something bites", "rust red and soot")]):
    add(f"warn_{i}", F + "WarningGlyph", 1.2, "brush", 0.25, "A settler's warning daubed on a wall, not any real-world sign: " + t + ". " + BRUSH + PIG.format(c=c) + SQ)
for i, t in enumerate(["two great angry slashes crossed over a scribble", "a big scrubbing back and forth scribble blotting something out"]):
    add(f"crossout_{i}", F + "CrossOut", 1.3, "brush", 0.15, "Someone's mark furiously crossed out: " + t + ". " + BRUSH + PIG.format(c="oxblood over soot") + SQ)
# ------ stencils
add("stencil_crown_0", F + "Stencil_Crown", 1.25, "spray", 0.3, "A crude crown of five blunt spikes with a slash of paint knocked through it, an insult to nobility. " + STENCIL + PIG.format(c="soot black") + SQ)
add("stencil_gear_0", F + "Stencil_Gear", 1.25, "spray", 0.3, "A blunt-toothed cog with a hole in the middle, a work gang's emblem. " + STENCIL + PIG.format(c="dull blue") + SQ)
add("stencil_fist_0", F + "Stencil_Fist", 1.25, "spray", 0.3, "A brawler's knuckles seen from the front, four blunt lumps above a block, bloody-minded. " + STENCIL + PIG.format(c="oxblood") + SQ)
# ------ paste-ups
for i, t in enumerate(["a howling wild-haired head printed huge", "a hunched beast with too many eyes"]):
    add(f"paste_flyer_{i}", F + "Paste_Flyer", 1.1, "paste", 0.3, PASTE + "The picture: " + t + ". Inks: soot black on dirty ochre paper. Portrait sheet, slightly taller than wide.")
for i, t in enumerate(["a blunt masked face looking straight out", "a crude figure with its head crossed through"]):
    add(f"paste_wanted_{i}", F + "Paste_Wanted", 1.1, "paste", 0.35, PASTE + "A wanted poster. The picture: " + t + ". Inks: soot black and oxblood on grimy lime-white paper. Portrait sheet, slightly taller than wide.")
add("gig_0", F + "Paste_Gig", 2, "paste", 0.28, PASTE + "Two sheets pasted edge to edge advertising a fight or a noise night: a screaming wild head on one, a snarling beast on the other, jagged sunburst behind both. Inks: soot black and rust red on dirty ochre paper. Twice as wide as tall.")
# ------ sigil frames (ideoligion icon goes in the middle, leave it empty)
add("halo_0", F + "SigilFrame_Halo", 1.3, "brush", 0.2, "A rough ring of short radiating stabs around an empty middle, the middle left completely empty and transparent. " + BRUSH + PIG.format(c="chalk white") + SQ)
add("stencilbox_0", F + "SigilFrame_StencilBox", 1.3, "spray", 0.25, "A rough hand-sprayed box frame with broken corners around an empty middle, the middle left completely empty and transparent. " + SPRAY + PIG.format(c="soot black") + SQ)
add("dripframe_0", F + "SigilFrame_DripFrame", 1.3, "brush", 0.2, "A heavy dragged ring of paint around an empty middle, the middle left completely empty and transparent, long runs falling straight down from its bottom. " + BRUSH + PIG.format(c="oxblood") + SQ)
# ------ meme glyphs: each its own tool, none a centred pictogram
G = [
 ("Cannibal", "a gnawed long bone with a bite-mark ring of teeth around its end", BRUSH, "oxblood and lime white"),
 ("MaleSupremacy", "a great jutting horned head in profile above a row of little bowed figures", BRUSH, "rust red and soot"),
 ("FemaleSupremacy", "a tall crowned woman's head with flying hair over a row of little bowed figures", SPRAY, "dull violet and soot"),
 ("Nudism", "a naked running stick figure of four fast strokes, arms flung wide", CHALK, "lime white"),
 ("Inhuman", "a head that is only a jagged starburst with too many eyes", SPRAY, "dull violet and soot"),
 ("PainIsVirtue", "a wreath of long thorns dragged in one go, a blot of blood falling from it", BRUSH, "oxblood"),
 ("Raider", "a boot stamping down on a heap, smeared by the heel", RAG, "rust red and soot"),
 ("Supremacist", "a sword thrust straight down into a heap of little heads", BRUSH, "soot and oxblood"),
 ("Loyalist", "a blunt three-spiked banner on a pole, hung and dripping", BRUSH, "ochre"),
 ("Individualist", "a single big open eye with a line slashed under it, alone", SPRAY, "dull blue"),
 ("Collectivist", "a mob of a dozen thumb-print heads pressed close, one blot", RAG, "ochre and soot"),
 ("Guilty", "a head bowed to the ground with long dragging lines of weeping", CHALK, "ash grey and soot"),
 ("Darkness", "a huge wiped blot of black with a ragged pale ring left around it", RAG, "soot black and lime white"),
 ("Blindsight", "an eye gouged out with two heavy scratches across it", BRUSH, "soot and lime white"),
 ("Bloodfeeding", "two long fangs and a wiped smear of blood running from them", RAG, "oxblood"),
 ("Transhumanist", "half a human head joined to a blocky machine half, seen from the side, stencil-hard on one side, brush-loose on the other", SPRAY, "ash grey and dull blue"),
 ("FleshPurity", "a heart wrapped in a dragged scrawl, wet and heavy", BRUSH, "oxblood"),
 ("HumanPrimacy", "a big open human hand print, pressed and dragged downward", RAG, "lime white"),
 ("NaturePrimacy", "a thick twisted root system clawing down, dragged in three strokes", BRUSH, "oxide green and soot"),
 ("AnimalPersonhood", "the head of a wolf in five thick strokes, its eye the same size as a person's", BRUSH, "soot and ochre"),
 ("Rancher", "the wide horns and long face of a muskox, daubed fast", RAG, "burnt orange and soot"),
 ("Tunneler", "a black hole rammed into a mound, pick-gouged rays fanning out of it", BRUSH, "soot and ochre"),
 ("TreeConnection", "a huge gnarled tree trunk dragged with a filthy rag, branches like arms, its crown wiped out", RAG, "oxide green and soot"),
 ("HighLife", "a long curling plume of smoke rising and thickening into a blot, the plume made with one wet drag", SPRAY, "oxide green and ash grey"),
 ("Proselytizer", "a screaming open mouth in profile with three thick lines of shout flying out of it", BRUSH, "ochre and soot"),
 ("Ritualist", "a ring of squat figures dancing around a blot of fire, thumbed on", RAG, "burnt orange and soot"),
 ("Shipborn", "a blunt star-tailed ship shape rising over a wiped curve of a planet", SPRAY, "dull blue and lime white"),
]
for name, t, tool, c in G:
    add(name.lower() + "_0", F + "Glyph_" + name, 1.25, "brush" if tool is not CHALK else "chalk", 0.22, f"A crude emblem by a believer, not a centred icon, lopsided and fast, filling the frame: {t}. " + tool + PIG.format(c=c) + SQ, name in ("Nudism", "Loyalist"))


def gen(workers):
    q = queue.Queue()
    for n, m in M.items():
        if not os.path.exists(f"{GEN}/{n}.png"):
            q.put((n, m))
    total = q.qsize()
    print("generating", total, flush=True)

    def work(w):
        while True:
            try:
                n, m = q.get_nowait()
            except queue.Empty:
                return
            for attempt in range(2):
                r = subprocess.run([sys.executable, f"{REPO}/skills/generating-images/scripts/codex_image.py", "generate", "--out", f"{GEN}/{n}.png",
                                    "--codex-home", HOME % w, "--timeout", "900", "--prompt", m["prompt"]], capture_output=True, text=True, cwd=REPO)
                if r.returncode == 0:
                    break
            print(n, "rc", r.returncode, (r.stderr or "")[-200:] if r.returncode else "", flush=True)

    ts = [threading.Thread(target=work, args=(w,)) for w in range(workers)]
    [t.start() for t in ts]
    [t.join() for t in ts]


if __name__ == "__main__":
    if sys.argv[1:2] == ["gen"]:
        gen(int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8)
    else:
        print(len(M), "marks")
        for n, m in M.items():
            print(n, m["folder"], m["width"], m["mode"])
