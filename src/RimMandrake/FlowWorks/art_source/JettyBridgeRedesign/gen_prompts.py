"""Prompts for the GENERATED options (Codex image_gen), one per piece. RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD.

Each option is built on one procedural geometry option of specs.py (same deck width, posts, cable layout); the picture adds
the painted material. Picks (2026-11-22): steel jetty B and C, heavy jetty A and B (GPT asked with the sheets attached,
agreed); bridges Scrapper A+C, Industrial A+C, Modern A+B, Futuristic A+B, heavy A+B (chosen for the widest spread between
the four looks). Look briefs: design/specs/2026-11-22-flowworks-look-briefs/looks.md.

Rules from generating-images/references/prompting.md: constraints first, short, and every constraint stated as the state
wanted, never as a prohibition."""

DECK_FRAME = (
    "Game texture for RimWorld. Strict top-down orthographic view looking straight down, the game's painterly building "
    "style with soft dark outlines. Fully transparent background with a real alpha channel. The image holds ONE long "
    "straight walkway deck lying horizontally across almost the whole width, about seven times longer than it is wide, "
    "perfectly straight and level, its top and bottom edges exactly horizontal and parallel, centred vertically with empty "
    "transparent space above and below. Even, flat light from straight above. Between its two ends the deck is uniform "
    "along its length: edge beams and rails run unbroken at the same rows from end to end. ")

JOINT = "a heavy bolted steel joint plate where it meets the ledge"
# Futuristic: the look brief bars exposed bolts and rivets (looks.md); its first strips took bolts from JOINT
# Modern: its first strip took heavy bolted plates from JOINT and read as Industrial (GPT judge, 2026-11-22)
JOINT_MOD = "a slim galvanised steel end angle with a small neat bolted connection where it meets the ledge"
JOINT_FUT = "a sleek seamless composite coupling collar with smooth rounded corners and a thin light seam where it meets the ledge"

# key: (kind, geometry option letter, look, ends: (left end, right end), material text)
DECKS = {
    # ---- steel jetty (station 59), Industrial finish
    "steel_jetty_B": ("steel_jetty", "B", "Industrial", (JOINT, "a gunmetal steel end beam with yellow-black hazard "
                      "stripes and a big steel cable lug at each of its two corners"),
                      "Heavy steel bar grating with a crisp see-through grid of dark gaps, framed along both long edges by "
                      "thick gunmetal box-section steel beams with bolted splice plates, slim steel tube handrails on both "
                      "edges. Painted dark gunmetal and slate grey, honest working wear: scuffed paint on the edges, a few "
                      "small rust weeps at bolts. It reads unmistakably as heavy STEEL."),
    "steel_jetty_C": ("steel_jetty", "C", "Industrial", (JOINT, "a gunmetal steel end beam with yellow-black hazard "
                      "stripes and a big steel cable lug at each of its two corners"),
                      "A narrow ribbed steel-plate gangway carried between two deep steel side trusses; along each long edge "
                      "the truss diagonals form one continuous zigzag of steel angle with bolted gusset plates at every node. "
                      "Painted gunmetal and slate grey, scuffed at the edges, a little grease at joints. It reads "
                      "unmistakably as a STEEL truss."),
    # ---- heavy jetty (station 60), Industrial finish
    "heavy_jetty_A": ("heavy_jetty", "A", "Industrial", (JOINT, "a massive concrete bumper block painted with "
                      "yellow-black hazard stripes, a huge steel cable lug at each corner"),
                      "A thick cast-concrete slab, light grey and weathered, with formwork marks and a few chipped edges; "
                      "both long edges armoured with heavy bolted dark steel angle; heavy double steel guard rails along both "
                      "edges. Brutalist heavy industry: massive, tough, cement and steel."),
    "heavy_jetty_B": ("heavy_jetty", "B", "Industrial", (JOINT, "a steel crash beam with bold yellow-black hazard "
                      "stripes, a huge steel cable lug at each corner"),
                      "Grey precast concrete deck panels laid between two massive riveted steel box girders along both long "
                      "edges; the girders dark gunmetal with dense rows of big rivets; the concrete scuffed, dusty, with "
                      "faint tyre marks. Brutalist heavy industry: massive, tough, cement and steel."),
    # ---- steel bridge, four looks (stations 61-64); both ends are joint plates
    "bridge_Scrapper_A": ("bridge", "A", "Scrapper", (JOINT, JOINT),
                          "Hand-built from salvage, unmistakably METAL: mismatched salvaged steel plates riveted and patched "
                          "over each other, many of them bare blue-grey steel, some faded olive or brick-red, salvaged steel "
                          "angle edges, steel wire-rope handrails held by hose clamps. Rust streaks at the rivets and dents: "
                          "salvaged and kept running."),
    "bridge_Scrapper_C": ("bridge", "C", "Scrapper", (JOINT, JOINT),
                          "Overlapping chipped green ship-hull plates riveted in uneven rows, paint flaking to rust at the "
                          "overlaps, salvaged steel angle edges, rope handrails tied to the plates. Heavy honest rust: "
                          "salvaged and kept running."),
    "bridge_Industrial_A": ("bridge", "A", "Industrial", (JOINT, JOINT),
                            "Gunmetal steel diamond plate on bolted dark I-beam stringers along both edges, steel tube "
                            "handrails, big bolts and flanges. Painted steel, mostly whole paint: honest working wear, "
                            "scuffed edges, grease and dust. Grim functional used-future heavy industry."),
    "bridge_Industrial_C": ("bridge", "C", "Industrial", (JOINT, JOINT),
                            "Sand-grey bolted steel plate panels with yellow edge stripes, slate-grey box girders along "
                            "both edges, heavy bolts, small stencilled hazard plates. Standard-issue used-future military "
                            "hardware: maintained, scuffed, dusty."),
    "bridge_Modern_A": ("bridge", "A", "Modern", (JOINT, JOINT),
                        "A present-day galvanised steel bar-grating footbridge: dull silver hot-dip galvanised grating with "
                        "a fine see-through grid, galvanised edge channels, safety-yellow tube handrails on both edges. "
                        "Realistic normal wear: dust, water stains, scuffed yellow paint. Photoreal industrial catalogue "
                        "product, not cartoonish."),
    "bridge_Modern_B": ("bridge", "B", "Modern", (JOINT_MOD, JOINT_MOD),
                        "A present-day steel footbridge: sun-faded green painted steel edge beams with patches of darker "
                        "touch-up paint, a grey gritted anti-slip deck surface worn paler down the middle by footsteps, "
                        "plain grey tube rails, slim neat connections. Realistic normal wear: dust, smudges, water stains. Not cartoonish."),
    "bridge_Futuristic_A": ("bridge", "A", "Futuristic", (JOINT_FUT, JOINT_FUT),
                            "A sleek seamless white composite deck with flush panel lines, thin glowing cyan light strips "
                            "running down both edges, brushed titanium trim, small flush access ports and tiny status "
                            "lights. Every surface smooth and flush, fasteners hidden. Clean, elegant, computerised high-tech."),
    "bridge_Futuristic_B": ("bridge", "B", "Futuristic", (JOINT_FUT, JOINT_FUT),
                            "A sleek matte graphite-black composite deck with flush panel lines, glowing magenta neon light "
                            "strips running down both edges, small amber status lights, flush access ports. Every surface "
                            "smooth and flush, fasteners hidden. Cyberpunk: dark, elegant, computerised."),
    # ---- heavy truss bridge (stations 54-55), Industrial finish
    "heavy_bridge_A": ("heavy_bridge", "A", "Industrial", (JOINT, JOINT),
                       "A thick cast-concrete slab, light grey and weathered, with formwork marks and chipped edges; both "
                       "long edges armoured with heavy bolted dark steel angle; heavy double steel guard rails along both "
                       "edges. Brutalist heavy industry: massive, tough, cement and steel."),
    "heavy_bridge_B": ("heavy_bridge", "B", "Industrial", (JOINT, JOINT),
                       "Grey precast concrete deck panels between two massive riveted steel box girders along both long "
                       "edges; the girders dark gunmetal with dense rows of big rivets; the concrete scuffed and dusty. "
                       "Brutalist heavy industry: massive, tough, cement and steel."),
}


def deck_prompt(key):
    kind, opt, look, (left, right), material = DECKS[key]
    return (DECK_FRAME + "The LEFT end finishes in " + left + "; the RIGHT end finishes in " + right + ". Material: "
            + material)


POST_FRAME = (
    "Game texture for RimWorld, the game's painterly style with soft dark outlines, drawn the way RimWorld draws tall "
    "things from its top-down camera: an upright front view, foot at the bottom, head at the top. Fully transparent "
    "background with a real alpha channel. FOUR separate tall slender upright posts standing side by side in a row, evenly "
    "spaced with wide empty transparent gaps between them, each one about ten times taller than it is wide, each filling "
    "the full image height, each with a cable saddle or clevis at its head. Left to right: ")

# post key: (description); grouped four to an image
POSTS = {
    "jetty": [
        ("steel_jetty_B", "a gunmetal steel box-section post with bolted base plate and a yellow-black hazard band near the "
                          "foot, steel cable clevis at the head"),
        ("steel_jetty_C", "a gunmetal steel lattice mast leg of bolted angle with cross bracing, a steel pulley head"),
        ("heavy_jetty_A", "a massive square cast-concrete pylon with a heavy dark steel cap and a big cable saddle, "
                          "weathered grey concrete with formwork lines, wider than the others"),
        ("heavy_jetty_B", "a massive riveted dark gunmetal steel box column with a heavy bolted head plate and two cable "
                          "clevises, wider than the first two"),
    ],
    "bridge1": [
        ("Scrapper_A", "a tower of welded salvaged pipe sections of different diameters, rusty with olive paint patches, "
                       "rope lashings and wire wraps"),
        ("Scrapper_C", "a tower of welded rusty pipe and old green hull plate scraps, chain wrapped at the head"),
        ("Industrial_A", "a gunmetal steel box tower with yellow-black hazard bands, big bolts, a cast steel cable saddle"),
        ("Industrial_C", "a slate-grey steel box tower with a sand-grey cast saddle at the head and a stencilled hazard "
                         "plate"),
    ],
    "bridge2": [
        ("Modern_A", "a present-day galvanised steel tubular mast, dull silver, with a stainless clevis head and a "
                     "concrete footing, realistic dust and water stains"),
        ("Modern_B", "a present-day sun-faded green painted steel I-section mast with darker touch-up paint patches and "
                     "a grey clevis head, realistic wear"),
        ("Futuristic_A", "a sleek tapering graphite-black composite pylon with glowing cyan light nodes and a brushed "
                         "titanium head"),
        ("Futuristic_B", "a sleek slim matte graphite pylon with a glowing magenta light strip and small amber status "
                         "lights at the head"),
    ],
}


def post_prompt(group):
    return POST_FRAME + "; ".join("(%d) %s" % (i + 1, d) for i, (_, d) in enumerate(POSTS[group])) + "."


CABLES = [
    ("black", "thick black-grey greased steel wire rope, helical strands clearly twisted"),
    ("galv", "slim bright galvanised stainless steel wire rope, silver, helical strands"),
    ("rusty", "rusty brown steel wire rope with rope lashings wrapped around it every so often"),
    ("chain", "heavy rusty steel chain, links alternating face-on and edge-on"),
    ("cyan", "smooth graphite-black composite cable with glowing cyan clamp bands evenly spaced"),
    ("magenta", "smooth graphite-black composite cable with glowing magenta clamp bands evenly spaced"),
]

CABLE_PROMPT = (
    "Game texture for RimWorld, painterly style with soft dark outlines, seen from straight above. Fully transparent "
    "background with a real alpha channel. SIX separate straight horizontal cables, each running the full width of the "
    "image, perfectly straight and level, stacked one above another with wide empty transparent gaps between them. Top to "
    "bottom: " + "; ".join("(%d) %s" % (i + 1, d) for i, (_, d) in enumerate(CABLES)) + ".")
