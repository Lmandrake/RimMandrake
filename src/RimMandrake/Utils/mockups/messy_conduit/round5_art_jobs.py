"""round5_art_jobs.py -- MessyConduit art round 5 (owner review 2026-10-04 of the per-style map): generation jobs.

    python3 src/RimMandrake/Utils/mockups/messy_conduit/round5_art_jobs.py wave1|wave2 [--only name ...]

Runs Codex $imagegen (skills/generating-images/scripts/codex_image.py) 6 at a time, each worker on its own CODEX_HOME.
Inputs/outputs live outside git at D:\\Luke\\dev\\_rmscratch\\mc_r5\\{in,raw}. Report: Transient/mc_art_round5_report.md.
Conform + install: round5_art_install.py (same folder).
"""
import os, subprocess, sys, threading, queue, time

R = "/mnt/d/Luke/dev/_rmscratch/mc_r5"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5))
CI = os.path.join(REPO, "skills/generating-images/scripts/codex_image.py")

BASE = ("RimWorld game sprite, seen from directly above (top-down, as RimWorld draws buildings and items), hand-painted "
        "painterly style with crisp detail and a thin dark outline, like RimWorld's own shipping art. One object only, centred. "
        "Real transparent background (alpha channel): no ground, no floor, no cast shadow, no text, no labels, no border. ")

LOOK = {
    "Scrapper": "Look: JUNKER/SCRAPPER - crude, hacked together from salvaged scrap: rusty dented tin, mismatched bolts, copper, frayed tape, wire twists.",
    "Industrial": "Look: INDUSTRIAL (Star Wars industrial, like a Tatooine moisture farm or Imperial hangar) - heavy angular gunmetal/charcoal steel plates, chamfered corners, bolts, black rubber, small yellow-black hazard stripes.",
    "Modern": "Look: MODERN real-world (present day hardware store) - painted steel and grey/white moulded plastic, real-world product proportions.",
    "Futuristic": "Look: FUTURISTIC/CYBERTEK - sleek silver-white alloy and graphite panels, seamless rounded forms, thin glowing cyan light strips.",
}
FAM2LOOK = {"Jawa": "Scrapper", "StarWars": "Industrial", "ExtCord": "Modern", "Cybertek": "Futuristic"}

SW = {
    "Scrapper": "a crude scrap-built KNIFE SWITCH: an open copper blade lever with a wooden handle hinged on a rusty scrap plate, the blade pressed DOWN into its copper contact clips (switch ON, closed).",
    "Industrial": "a heavy industrial DISCONNECT SWITCH box with a big angular throw lever on its face, lever thrown to the ON position, a small green status lamp lit.",
    "Modern": "a real-world electrical SAFETY DISCONNECT SWITCH: a grey painted steel enclosure with a big red THROW-SWITCH handle on its side, handle thrown UP to ON, like the fused disconnect box on the side of a house or factory wall.",
    "Futuristic": "a sleek futuristic power breaker module with a recessed glowing THROW LEVER slid to the ON position, cyan light strip lit.",
}
JX = {
    "Jawa": "a small square scrap JUNCTION BRICK made of a rusty dented tin box with tape and rivets",
    "StarWars": "a small square heavy JUNCTION BRICK of angular gunmetal steel with bolted corners and a tiny hazard stripe",
    "ExtCord": "a small square real-world 4-WAY EXTENSION-CORD ADAPTER BRICK in white/light-grey moulded plastic (like a cube tap)",
    "Cybertek": "a small square sleek futuristic JUNCTION BRICK of silver-white alloy with a thin cyan glowing seam",
}
MAST = {
    "Scrapper": "a BARE INCANDESCENT LIGHT BULB (warm, softly lit, NOT a sparkle or star) sitting in a crude dented scrap-metal REFLECTOR DISH, hanging from a bent scrap arm",
    "Industrial": "an ANGULAR INDUSTRIAL lamp: a boxy chamfered steel lamp housing with a protective cage grille over a flat lens, softly lit warm white (NOT a sparkle)",
    "Modern": "a real-world STREETLIGHT head: a cobra-head street lamp on a curved arm, flat lens underneath softly lit (NOT a sparkle)",
    "Futuristic": "a VERY FUTURISTIC lamp head: a sleek floating silver-white alloy blade with a thin glowing cyan-white light strip lens (NOT a sparkle)",
}
FLOOR = {
    "Scrapper": "a junker STANDING FLOOR LAMP: a bare incandescent light bulb in a crude dented scrap-metal reflector dish on a rusty pipe stand with a scrap-plate base",
    "Industrial": "an industrial STANDING FLOOR LAMP: an angular caged steel work lamp on a heavy chamfered gunmetal stand",
    "Modern": "a modern real-world STANDING FLOOR LAMP: a round lamp shade on a slim black metal pole with a round weighted base",
    "Futuristic": "a futuristic STANDING FLOOR LAMP: a sleek silver-white alloy column with a floating ring-shaped cyan-white light",
}
CLAMP = {
    "Scrapper": "rusty scrap metal with copper jaws and worn red-brown rubber handle grips",
    "Industrial": "gunmetal steel with serrated steel jaws, black rubber grips and small yellow-black hazard stripes",
    "Modern": "steel jaws with safety-orange rubber insulated handles, like real jumper-cable clamps",
    "Futuristic": "silver-white alloy with cyan light accents and graphite grips",
}


def jobs(wave):
    J = []
    if wave == "wave1":
        for L, s in SW.items():
            J.append(("sw_" + L, "edit", [R + "/in/sw_" + L + ".png"],
                      "Redesign this power switch completely, keeping only its size, square framing and the fact that power cords "
                      "connect at the middle of its four sides. Make it " + s + " " + LOOK[L] + " " + BASE))
        for F, s in JX.items():
            J.append(("jx_" + F, "edit", [R + "/in/jx_" + F + ".png"],
                      "Redraw this cable junction as " + s + ", with a THREE-PRONG plug pushed into a socket on EACH of its four "
                      "sides (north, south, east, west): each plug head is short and chunky and sits flush against the brick. "
                      "The brick is THICK and square, about half the image wide; the plugs end at the image edges with NO cable "
                      "after them (the game draws the cables). Keep the colour palette of the reference. " + LOOK[FAM2LOOK[F]] + " " + BASE))
        for L, s in MAST.items():
            J.append(("mast_" + L, "edit", [R + "/in/mast_" + L + ".png"],
                      "Edit this power pole sprite: replace ONLY the lamp head on its side arm with " + s + ". Keep the pole, the "
                      "crossarm, the insulators, the framing, the canvas and everything else exactly identical, same position and "
                      "size. " + LOOK[L] + " Keep the transparent background."))
        for L, s in FLOOR.items():
            J.append(("floor_" + L, "generate", [], "Draw " + s + ", lamp lit softly (an ordinary lit lamp, no sparkle or star "
                      "flare), seen from above at RimWorld's slight top-down angle so the lamp head and the base both read. "
                      + LOOK[L] + " " + BASE))
        for L, s in CLAMP.items():
            J.append(("clamp_" + L, "edit", [R + "/in/clamp_" + L + ".png"],
                      "Redraw this power-tap clamp (a big crocodile/jumper-cable clamp biting a power line) at high resolution, "
                      "crisp and clean, same pose and orientation (jaws pointing left, handles to the right), in " + s + ". "
                      "IMPORTANT: remove the black cable/conduit stub sticking out of the back of the handles: the handles end "
                      "cleanly with nothing behind them. " + BASE))
        J.append(("reel_stored", "edit", [R + "/in/reel_stored.png"],
                  "Repaint this hose reel: the reel housing, frame, pump body and end plates become FIRE-HYDRANT RED painted metal "
                  "(glossy, slightly worn), the valve hand-wheel on top and the bolts become BARE STEEL, the brass/chrome "
                  "fittings stay metal. Keep the green hose coiled on the drum exactly as it is. No neon, no orange, no white "
                  "plastic. Keep pose, framing, size and transparent background identical."))
        J.append(("strip", "generate", [],
                  "Draw a real-world POWER STRIP (a long rectangular grey/white plastic multi-socket bar, 4 outlets in a row, a "
                  "small orange power LED at the right end) seen from directly above, with a black THREE-PRONG PLUG pushed into "
                  "EACH outlet from the top (you see the backs of the plug heads), each plug's short black cord curling off the "
                  "strip. Very wide and low: the strip fills the width of the image. " + BASE))
    elif wave == "retry":
        # first mast edits for Industrial/Futuristic barely changed the head: ask for a clearly different, larger head
        RETRY = {
            "Industrial": "a LARGE ANGULAR INDUSTRIAL FLOODLIGHT: a wide flat rectangular chamfered gunmetal housing tilted down, "
                          "heavy bolted yoke bracket, a broad flat glass lens softly lit warm white, small hazard stripe on the "
                          "housing. Clearly different from the old small caged lantern",
            "Futuristic": "a STRIKING FUTURISTIC LAMP HEAD: a long curved silver-white alloy blade/visor cantilevered off the pole "
                          "with a continuous glowing cyan-white light strip along its whole underside and a small floating ring "
                          "accent. Clearly different from the old plain flat lamp",
        }
        for L, s in RETRY.items():
            J.append(("mast2_" + L, "edit", [R + "/in/mast_" + L + ".png"],
                      "Edit this power pole sprite: REMOVE the existing lamp and its arm on the right side and draw in its place "
                      + s + ", on a short sturdy arm from the pole at the same height. Keep the pole, the crossarm, the insulators, "
                      "the framing and the canvas exactly identical. " + LOOK[L] + " Keep the transparent background."))
    else:
        for L, s in SW.items():
            J.append(("swoff_" + L, "edit", [R + "/raw/sw_" + L + ".png"],
                      "Show this exact same switch turned OFF: the throw lever / blade thrown to the OPEN, disconnected position "
                      "and any status light dark. Change nothing else: same object, same size, same framing, same colours, "
                      "transparent background."))
        # T junctions are not rendered: round5_art_install.py derives each T from its look's + image (same brick).
        J.append(("reel_laid", "edit", [R + "/in/reel_laid.png", R + "/raw/reel_stored.png"],
                  "Repaint the FIRST image (an empty hose reel) to match the SECOND image's paint exactly: fire-hydrant red painted "
                  "metal housing and frame, bare steel valve wheel and bolts. Keep the first image's empty drum, pose, framing and "
                  "size identical. No neon, no orange, no white. Transparent background."))
    return J


def run(job, home, log):
    name, mode, imgs, prompt = job
    out = R + "/raw/" + name + ".png"
    cmd = [sys.executable, CI, mode, "--out", out, "--prompt", prompt, "--codex-home", home, "--timeout", "600", "--force"]
    for i in imgs:
        cmd += ["--image", i]
    t = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    ok = os.path.isfile(out) and p.returncode == 0
    with lock:
        log.write("%s %s rc=%d %.0fs %s\n" % ("OK" if ok else "FAIL", name, p.returncode, time.time() - t,
                                             "" if ok else (p.stderr or p.stdout)[-300:].replace("\n", " | ")))
        log.flush()


lock = threading.Lock()
if __name__ == "__main__":
    wave = sys.argv[1]
    only = sys.argv[sys.argv.index("--only") + 1:] if "--only" in sys.argv else None
    J = [j for j in jobs(wave) if not only or j[0] in only]
    q = queue.Queue()
    for j in J:
        q.put(j)
    log = open(R + "/" + wave + ".log", "a")
    def worker(i):
        home = R + "/homes/w%d" % (i + int(os.environ.get("R5_HOME_OFFSET", "0")))
        while True:
            try:
                j = q.get_nowait()
            except queue.Empty:
                return
            run(j, home, log)
    ts = [threading.Thread(target=worker, args=(i,)) for i in range(6)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    log.write("DONE %s\n" % wave)
