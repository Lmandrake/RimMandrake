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
def add(name, folder, width, mode, wear, prompt, pigmented=False, height=1.0, floor=0.0):
    """floor: raw alpha below it is dropped before bake strengthens the paint (generator haze would become a pale film)."""
    M[name] = dict(folder=folder, width=width, mode=mode, wear=wear, prompt=BASE + prompt, pigmented=pigmented, height=height, floor=floor)

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
for i, (d, t, c) in enumerate([("A", "fat round overlapping bubble shapes", "dusty lilac fill, soot black line, a few chalk white shine flicks"), ("A", "lumpy melting bubble shapes", "rust red fill, soot line"),
                               ("B", "squat rounded blocks shouldering each other", "ochre fill, soot line"), ("B", "cloud-like puffed shapes with a hasty second line", "dull blue fill, chalk line")]):
    add(f"throwup_{d.lower()}_{i % 2}", F + "ThrowUp_" + d, 1.3, "brush", 0.2 + 0.12 * (i % 2), f"A graffiti throw-up: {t} that look like letters but spell nothing. " + ROLLER + PIG.format(c=c) + SQ)
for i, (t, c) in enumerate([("fat round bubble shapes in a row", "chalk fill, soot line"), ("bulging squared bubble shapes", "rust red fill, soot line"), ("drooping melted bubble shapes", "dull violet fill, chalk line"), ("tall crowded bubble shapes shouldering each other", "oxide green fill, chalk line")]):
    add(f"wide_{i}", F + "ThrowUp_Wide", 2, "brush", 0.2 + 0.08 * i, f"A wide graffiti throw-up: {t} that look like letters but spell nothing. " + ROLLER + PIG.format(c=c) + L2)
M["throwup_a_0"]["fill"] = (0.86, 0.45, 0.64)   # pass 16: lilac went grey in a dim storeroom and still read as rock chunks
# ------ pieces
for i, (t, c) in enumerate([("sharp interlocking angular shapes like shattered letters, arrows thrown off them", "rust red, burnt orange, soot black, chalk"), ("huge rounded interlocked shapes with a hard second colour fading through them", "dull blue, lime white, soot black"),
                            ("tall spiky shapes leaning into each other, a crude sun behind", "ochre, oxblood, soot black"), ("flowing ribbon shapes knotting through each other", "oxide green, chalk, dull violet")]):
    add(f"piece_{'abcd'[i]}", F + "Piece", 3, "brush", 0.16, f"A full graffiti piece by someone good, a long wall-burner: {t}, that look like letters but spell nothing. Careful hand, rough materials. Painted with brush and can together: dense coverage, streaky fills, a soft misted glow behind, thin runs falling straight down. " + PIG.format(c=c) + L3)
# ------ vandal: the ugliest, crudest thing on any wall, and plainly paint someone put there on purpose, never filth. Pass 9: the pass-7 set came out
# as bold, confident, saturated loops with tidy drips (louder than a tally, not uglier: owner "not sure", GPT "louder, not uglier"). This set is
# clumsy rather than bold: blotched, starved and over-loaded paint, a hand dragged through it, a grubby fog of overspray, sickly clashing colour.
VANDAL = ("The ugliest, crudest graffiti on any wall: no skill at all, done in a hurry by someone who wanted to spoil the wall, and it does. It is plainly paint "
          "put there on purpose, never dirt, never a stain, never scorch, never brown. It is clumsy, not bold: the paint goes on in blotches and splats, far too thick "
          "in some places and starved and broken in others; the lines wobble, stall into fat blobs where the hand stopped, and double back over themselves; a hand "
          "was dragged through the wet paint and smeared part of it sideways into a grubby streak; and a dirty fog of fine overspray hangs around all of it. "
          "The colours fight each other: cheap loud paint straight from the can in colours that clash and hurt the eye, never clean, never pretty, never neat, and "
          "nothing that could be moss, mould, soot, rust, mud or blood: no green, no olive, no brown, no black, no grey. ")
# Pass 16: a blind judge read the bile-green, olive and liver-purple set as moss and mould at play zoom. Ugly is clumsy and garish, not the colours of growth.
HEAVY = "Far too much paint in the blobs: uneven runs falling straight down from them, some long, some short, none tidy. "
for i, (t, tool, c) in enumerate([
        ("a clotted scribble scrawled over and over on the same spot until it is one shapeless knot, with a second scribble in another colour dragged through it and "
         "a smeared handprint wiped across one end", SPRAY, "loud cheap pink over a harsh cyan underlayer"),
        ("an attempt at a tag that went wrong: four wobbly shapes that were meant to be letters of no alphabet, the last ones cramped and sliding downhill, then the "
         "whole thing angrily scribbled over", SPRAY, "salmon pink, the scribble over it in harsh mustard yellow"),
        ("three scrawled tags that spell nothing, sprayed right over each other in three clashing colours until they knot into one ugly tangle, splattered where a can spat",
         SPRAY, "sour mustard yellow, harsh violet and loud cheap pink"),
        ("a careless fat zigzag dragged the whole width in thick opaque paint, blotted into fat blobs where the can stuck, with a second clumsy zigzag in another colour "
         "sprayed crookedly over it and a burst of spatter where the can was shaken against the wall", SPRAY, "harsh cyan, the second zigzag in loud cheap pink"),
        ("a loaded brush flicked at the wall again and again, then a lopsided scrawl hacked through the splats and a wet smear wiped half of it away", BRUSH,
         "harsh violet splats, the scrawl in sour mustard yellow"),
        ("one furious scribble hacked back and forth with an over-loaded brush, peaks of wildly different heights crossing over themselves into a dense tangle, never "
         "forming letters, a second messier scribble smeared over it with a hand", BRUSH, "harsh cyan over salmon pink"),
]):
    add(f"vandal_{i}", F + "Vandal", 2, "brush" if tool is BRUSH else "spray", 0.08, VANDAL + "It is " + t + ". " + tool + HEAVY + "Colours only: " + c + ", cheap paint that clashes, not neon. " + L2, floor=0.04)
    M[f"vandal_{i}"].update(mute=0.85 if i in (1, 2, 4) else 0.6, drop_grey=True)   # their mustard went olive (moss) at 0.6
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
add("stencil_crown_0", F + "Stencil_Crown", 1.25, "spray", 0.3, "A crude crown of five blunt uneven spikes, an insult to nobility, sprayed badly through a torn cardboard stencil: one spike broken short where the card tore, ragged gaps, "
    "a misted double edge along one side where the card slipped, and a thick sloppy slash of paint sprayed right through it on the diagonal. Not tidy, not symmetrical, not an icon. " + STENCIL + PIG.format(c="pale lime white crown, the slash in rust red") + SQ, floor=0.04)
# Pass 16: the blue-and-red cog read as a gear icon (blind judge). One can, a hammer slammed across a hacked-out cog, sprayed through card.
add("stencil_gear_0", F + "Stencil_Gear", 1.25, "spray", 0.3, "A work gang's mark: a crude lopsided cog hacked out of cardboard with a knife, blunt uneven teeth, a ragged hole in the middle, "
    "with a heavy hammer laid slanting across it, the two sprayed through the card in one colour; one side sprayed heavy and running, the other starved and broken. "
    "Not clean, not symmetrical, not clip-art, not a logo. " + STENCIL + PALE + SQ, True, floor=0.04)
# Pass 14: the old fist (four knuckle lumps in oxblood) read at play zoom as a blood smear on the wall. A raised fist and forearm is a silhouette.
# Pass 16: the ochre disc behind it read as a logo or badge (blind judge). A street stencil is the shape alone on bare wall, in whatever can was to hand.
add("stencil_fist_0", F + "Stencil_Fist", 1.25, "spray", 0.3, "A raised fist and its forearm thrust straight up, the fist clenched with the thumb across the fingers, sprayed through a crude cardboard stencil "
    "with blunt bridges cut between the fingers, the forearm running off the bottom. No disc, no circle, no ring, no shape behind it: bare wall all round, only overspray speckle. "
    "Defiant, not tidy, not symmetrical, not an icon. " + STENCIL + PALE + SQ, True, floor=0.04)
# ------ stencil portraits (the defs keep their Paste_ names): sprayed straight onto the wall, no paper, the wall between every part.
PORTRAIT = ("A big street stencil portrait sprayed straight onto a bare wall. No paper, no sheet, no poster, no rectangle, no backing, no border, no frame, no background panel. "
            "First a few loose patchy clouds of the second colour were misted on with a can, thin, uneven, fading out at their edges, never a block. "
            "Then the subject was sprayed over them in soot black through a crude hand-cut cardboard stencil: separate islands of black paint with blunt bridges, "
            "soft misted edges where the card lifted, speckled overspray. Bare wall, left fully transparent, shows between every part: in the face's highlights, "
            "between the black shapes, through the mist and all around the outside. Only the sprayed paint. ")
SQP = "About as wide as it is tall, the subject filling the picture. "
for i, (t, c) in enumerate([("a howling head with wild flying hair, mouth wide open, hair thrown out in jagged spikes", "ochre"),
                            ("a hunched crouching beast with far too many eyes, claws hanging down", "rust red")]):
    add(f"paste_flyer_{i}", F + "Paste_Flyer", 1.1, "spray", 0.3, PORTRAIT + "The subject: " + t + ". " + SPRAY + PIG.format(c="soot black over misted " + c) + SQP, floor=0.04)
for i, (t, c) in enumerate([("a blunt masked face looking straight out, a cloth mask over the lower face, hard flat eyes", "soot black over a heavy patchy mist of rust red, wider than the head"),
                            ("a crude figure seen from the chest up, its head crossed out by a big fat X sprayed over it in the second colour", "soot black over misted ochre, the X in heavy ochre")]):
    add(f"paste_wanted_{i}", F + "Paste_Wanted", 1.1, "spray", 0.35, PORTRAIT + "The subject: " + t + ". " + SPRAY + PIG.format(c=c) + SQP, floor=0.04)
add("gig_0", F + "Paste_Gig", 2, "spray", 0.28, PORTRAIT + "The subject, for a fight night: two big heads side by side, on the left a screaming wild-haired head, on the right a snarling beast's head, "
    "and behind both a jagged sunburst of sprayed rays in the second colour, separate spikes with bare wall between them. " + SPRAY + PIG.format(c="soot black over misted rust red") + L2, floor=0.04)
# ------ sigil frames (ideoligion icon goes in the middle, leave it empty)
# Pass 16: the ring of radiating stabs read as a clip-art burst (blind judge). A believer's halo is one loose loop of a can.
add("halo_0", F + "SigilFrame_Halo", 1.3, "spray", 0.2, "A ragged halo sprayed fast in one loose loop of a spray can around an empty middle, the loop not quite closing, thick and thin where the hand sped and slowed, "
    "a second faster loop slipping off it, three or four short flicks thrown outward, and runs falling straight down from its bottom. The middle left completely empty and transparent. "
    "Not a burst, not rays, not a badge. " + SPRAY + PIG.format(c="chalk white") + SQ)
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
 ("Tunneler", "a ragged hole rammed into a heaped mound: the mound three or four rough dry strokes, the hole a jagged flat black gouge in it, not round, and short rays scratched and brushed out of the hole like pick strikes. Flat paint only: no sphere, no dome, no ball, no highlight, no shading", BRUSH, "soot and ochre"),
 ("TreeConnection", "a huge gnarled tree trunk dragged with a filthy rag, branches like arms, its crown wiped out", RAG, "oxide green and soot"),
 ("HighLife", "a grinning lopsided face with two big spiral eyes, its open mouth breathing out a thick ring. Pass 14: the old smoke plume read as a smudge on the wall; a staring spiral eye was tried beside this and was tidier", BRUSH, "oxide green and soot"),
 ("Proselytizer", "a screaming open mouth in profile with three thick lines of shout flying out of it", BRUSH, "ochre and soot"),
 ("Ritualist", "a ring of squat figures dancing around a blot of fire, thumbed on", RAG, "burnt orange and soot"),
 ("Shipborn", "a blunt star-tailed ship shape rising over a wiped curve of a planet", SPRAY, "dull blue and lime white"),
]
for name, t, tool, c in G:
    add(name.lower() + "_0", F + "Glyph_" + name, 1.25, "brush" if tool is not CHALK else "chalk", 0.22, f"A crude emblem by a believer, not a centred icon, lopsided and fast, filling the frame: {t}. " + tool + PIG.format(c=c) + SQ, name in ("Nudism", "Loyalist"),
        floor=0.04 if name == "Tunneler" else 0.0)
M["highlife_0"]["rim"] = False   # its black grin lies at the face's edge and break_rim took it for an outline (pass 14)


# ------ marks about somebody: the subject's own head goes in the gap, painted at runtime (WallPlane.PaintedPortrait).
GAP = "The top centre of the picture is left completely empty, a clear round gap about a third of the picture's width, because a head is painted there later. "
for i, t in enumerate(["a fat crude donkey's body on stumpy legs seen from the side, a flicking tail, its neck ending in the empty gap where its head should be",
                       "two huge curling devil horns rising either side of the gap, a forked beard hanging under it, jagged stink lines coming off",
                       "a tall crooked dunce cap on top, a row of little pointing hands from both sides aimed in at the gap",
                       "a crude gallows and a headless stick body hanging from it, the rope going into the gap"]):
    add(f"mock_{i}", F + "Mockery", 1.25, "brush", 0.15, "A cruel joke about someone, drawn on a wall by somebody who hates them: " + t + ". " + GAP + BRUSH + PIG.format(c="oxblood and soot black") + SQ)
# Pass 15: a blind judge read the laurel ring and the winged sun as badges or clip-art, careful and symmetrical. A street tribute is sprayed loud
# and fast by a friend: a crown thrown on their head, roses and a sprayed ring, stars and shine flicks. The heart already read as paint.
TRIB = ("A street tribute to someone, sprayed fast and loud on a wall at night by a friend who rates them: {t}. Proud and rough, lopsided, not careful, "
        "not symmetrical, not a badge, not an emblem, not clip-art. ")
for i, (t, tool) in enumerate([("a fat crude three-pointed crown sprayed sitting right on top of the gap as if on the person's head, a ragged sprayed ring around the gap, "
                                "short fat shine flicks bursting off it and two clumsy five-point stars", SPRAY),
                               ("a big lopsided heart outline around the gap with little flicks of love around it", BRUSH),
                               ("two crude sprayed roses with long thorny stems crossing under the gap, a lumpy hand-sprayed ring around the gap and a few four-point sparkles "
                                "flicked off it", SPRAY)]):
    add(f"tribute_{i}", F + "Tribute", 1.25, "brush", 0.15, (TRIB.format(t=t) if tool is SPRAY else "A loving tribute to someone, painted carefully on a wall by a friend: " + t + ". ")
        + GAP.replace("top centre", "centre") + tool + PIG.format(c="ochre and chalk white") + SQ)
for i, t in enumerate(["three melting candles in a row along the bottom, long runs of wax falling, a thin ring around the gap", "a wreath of crude flowers under the gap and long weeping lines falling from it", "two crude folded wings either side of the gap, a ring of small dots around it, drips falling"]):
    add(f"memorial_{i}", F + "Memorial", 1.25, "brush", 0.25, "A memorial for someone who has died, painted on a wall by someone who misses them: " + t + ". " + GAP.replace("top centre", "centre") + BRUSH + PIG.format(c="chalk white and ash grey") + SQ)
for i, t in enumerate(["a stupid little stick man bending over and showing his bare backside, looking back over his shoulder with a huge grin", "a potato-shaped little man with a huge nose peering over a line, both hands up waggling his fingers",
                       "a tiny naked-looking blob of a man with a huge head, dancing badly, arms waving, big dumb smile", "a grinning little man thumbing his nose with one hand and waggling the fingers, his tongue stuck out, on wobbly legs"]):
    add(f"rude_{i}", F + "RudeLittleMan", 1, "brush", 0.2, "A silly rude doodle, the kind bored people draw on any wall anywhere: " + t + ". Childish, funny, thick wobbly lines. " + BRUSH + PALE + SQ, True)
M["rude_3"]["floor"] = 0.3   # pass 16: the generator washed a pale haze behind him, and baked it read on the wall as a faint ochre blob
for i, t in enumerate(["two heavy slashes crossed over the gap, a wet gob of spit falling through it, a row of sneering teeth under it", "a ring of jagged angry scrawl around the gap and one long strike diagonally across it"]):
    add(f"insult_{i}", F + "FactionInsult", 1.3, "brush", 0.15, "An insult to a hated faction, defacing their emblem: " + t + ". " + GAP.replace("top centre", "centre") + BRUSH + PIG.format(c="soot black and rust red") + SQ)

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
