"""round6_art_jobs.py -- MessyConduit art round 6 (owner review 2026-10-04, station 11): generation jobs.

    python3 src/RimMandrake/Utils/mockups/messy_conduit/round6_art_jobs.py prep|wave1|wave2 [--only name ...]

Owner: "The hose reel for the scrapper needs to look hacked together out of piecemeal [scrap parts]. The modern hose
should not be neon, it should look like a real firehose."
Codex $imagegen via skills/generating-images/scripts/codex_image.py, 5 at a time, reusing round 5's CODEX_HOMEs.
Inputs/outputs outside git at D:\\Luke\\dev\\_rmscratch\\mc_r6\\{in,raw}. Strands, Mouth and the Modern reel's coil are
procedural (round6_art_install.py), not generated. Report: Transient/mc_art_round6_report.md.
"""
import os, subprocess, sys, threading, queue, time
from PIL import Image

R = "/mnt/d/Luke/dev/_rmscratch/mc_r6"
HOMES = "/mnt/d/Luke/dev/_rmscratch/mc_r5/homes"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5))
CI = os.path.join(REPO, "skills/generating-images/scripts/codex_image.py")
HOSE = os.path.join(REPO, "src/RimMandrake/MessyConduit/Textures/RimMandrake/MessyConduit/Hose")

BASE = ("RimWorld game sprite, seen from directly above (top-down, as RimWorld draws buildings and items), hand-painted "
        "painterly style with crisp detail and a thin dark outline, like RimWorld's own shipping art. One object only. "
        "Real transparent background (alpha channel): no ground, no floor, no cast shadow, no text, no labels, no border. ")
FIREHOSE = ("a REAL FIRE HOSE: a flat woven canvas/polyester jacket in muted OFF-WHITE / CREAM (slightly dusty, matte, "
            "fine woven texture visible), NOT neon, NOT glossy, NOT green, NOT orange plastic")
JUNK = ("hacked together out of piecemeal salvaged scrap: the spool drum is a cut-down rusty oil barrel, its end plates are "
        "two mismatched old wheel rims (one rusty red, one dull green-grey), the frame is bent angle-iron and a scrap of "
        "pipe welded on with crude bead welds, a bent pipe crank handle, wire twists and rope lashings holding parts "
        "together, a riveted patch panel of a different colour (faded blue tin), mismatched bolts and nuts")

INS = {  # name -> (source under HOSE, upscale factor)
    "reel_stored_S": ("Reel_PumpHookup.png", 1), "reel_laid_S": ("Reel_Deployed.png", 1),
    "coup_M": ("Styles/Modern/Coupling_Bare.png", 2), "nozzle_M": ("Styles/Modern/Nozzle_Bare.png", 2),
    "endcap_M": ("Styles/Modern/EndCap_Bare.png", 2), "binding_M": ("Styles/Modern/Binding.png", 4),
}


def prep():
    for n, (rel, k) in INS.items():
        im = Image.open(os.path.join(HOSE, rel)).convert("RGBA")
        if k > 1:
            im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
        im.save(R + "/in/" + n + ".png")
        print("in", n, im.size)


def jobs(wave):
    J = []
    if wave == "wave1":
        J.append(("reel_stored_S", "edit", [R + "/in/reel_stored_S.png"],
                  "Redraw this hose reel as a JUNK-BUILT reel, " + JUNK + ". Keep the same overall layout, pose, size and "
                  "framing: pump/valve body with hand-wheel on the left, the spool drum in the middle with the brown canvas "
                  "hose coiled on it, the same footprint. It must clearly look improvised from scavenged parts, not a tidy "
                  "manufactured reel. Rusty, dented, patched. " + BASE))
        J.append(("coup_M", "edit", [R + "/in/coup_M.png"],
                  "Redraw this hose coupling as a REAL-WORLD FIRE HOSE STORZ COUPLING: a cast ALUMINIUM coupling body (bare "
                  "brushed silver-grey metal) with the two curved Storz lugs and a BRASS locking ring, realistic fire-service "
                  "hardware. No orange plastic, no garden hose parts, no neon. Same pose, orientation, size and position. " + BASE))
        J.append(("nozzle_M", "edit", [R + "/in/nozzle_M.png"],
                  "Redraw this hose nozzle as a REAL-WORLD FIREFIGHTER'S BRANCH NOZZLE: a brushed aluminium/chrome nozzle with "
                  "a black rubber bumper at the tip, a BRASS coupling at the hose end and a black bale shut-off lever. "
                  "No orange plastic, no garden hose parts, no neon. Same pose, orientation, size and position. " + BASE))
        J.append(("endcap_M", "edit", [R + "/in/endcap_M.png"],
                  "Redraw this capped hose end as " + FIREHOSE + " ending in an ALUMINIUM STORZ COUPLING closed by a matching "
                  "aluminium blank cap on a short steel chain, realistic fire-service hardware. Replace the green hose with the "
                  "cream canvas fire hose. No orange plastic. Same pose, orientation, size and position. " + BASE))
        J.append(("binding_M", "edit", [R + "/in/binding_M.png"],
                  "Redraw this short hose segment as " + FIREHOSE + ", running straight left to right edge to edge, with a "
                  "real hinged ALUMINIUM HOSE-JACKET / hose-band repair clamp closed around its middle (bare metal, two "
                  "bolted latches). No orange plastic, no green. Same framing: the hose fills the full width of the image. " + BASE))
    elif wave == "wave2":
        J.append(("reel_laid_S", "edit", [R + "/raw/reel_stored_S.png"],
                  "Show this exact same junk-built hose reel with the hose fully UNREELED: the drum is now EMPTY, showing the "
                  "bare rusty barrel drum, with a short hose inlet stub/socket at the CENTRE of the drum where the hose leaves. "
                  "Change nothing else: same scrap parts, same frame, same pump body, same colours, same pose, framing and size. "
                  "Transparent background."))
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
    if wave == "prep":
        prep()
        sys.exit(0)
    only = sys.argv[sys.argv.index("--only") + 1:] if "--only" in sys.argv else None
    J = [j for j in jobs(wave) if not only or j[0] in only]
    q = queue.Queue()
    for j in J:
        q.put(j)
    log = open(R + "/" + wave + ".log", "a")
    homes = ["w0", "w1", "w2", "w3", "w4"]

    def worker(h):
        while True:
            try:
                j = q.get_nowait()
            except queue.Empty:
                return
            run(j, HOMES + "/" + h, log)
    ts = [threading.Thread(target=worker, args=(h,)) for h in homes]
    [t.start() for t in ts]
    [t.join() for t in ts]
    log.write("DONE %s\n" % wave)
