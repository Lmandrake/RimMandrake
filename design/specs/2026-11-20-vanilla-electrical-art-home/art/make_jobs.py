#!/usr/bin/env python3
"""make_jobs.py — the artpipe job list for the 2026-11-20 commissions (item RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART).

    python3 design/specs/2026-11-20-vanilla-electrical-art-home/art/make_jobs.py > /tmp/vea_jobs.json
    python3 src/RimMandrake/Utils/artpipe/fill_queue.py --input /tmp/vea_jobs.json [--dry-run]

Resolution rule (generating-rimworld-sprites, owner 2026-08-23): 128 px per cell of drawSize, rounded up.
  Battery   drawSize (2,3) (Core Buildings_Power.xml) -> north 256x384, east 384x256; rendered square 512 and
            conformed by install_vea_art.py; south = the north picture (vanilla ships no Battery_south either).
  WallLamp  drawSize 1 -> 128 per facing; rendered 256 square, conformed onto vanilla's wall-edge position x2.
  Icons     no world size; a gizmo is drawn at 75 px (UI scale 1) up to ~150 px (UI scale 2): 256 square.
Looks and their words are GSS's own (src/RimMandrake/Utils/mockups/messy_conduit/round5_art_jobs.py LOOK), minus the
retired outline clause (art_judge_brief.md B1a); Modern follows B6 (a thing you would see today, never paint-red).
"""
import json

ITEM = "RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART"
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
LOOK = {
    "Scrapper": "Look: JUNKER/SCRAPPER - crude, hacked together from salvaged scrap: rusty dented tin, mismatched bolts, "
                "copper, frayed tape, wire twists.",
    "Industrial": "Look: INDUSTRIAL (Star Wars industrial, like a Tatooine moisture farm or an Imperial hangar) - heavy "
                  "angular gunmetal and charcoal steel plates, chamfered corners, bolts, black rubber, small yellow-black "
                  "hazard stripes.",
    "Modern": "Look: MODERN real-world, present day - powder-coated steel, brushed aluminium and grey or white moulded "
              "plastic in real product proportions, the way the thing looks in a garage or utility room today.",
    "Futuristic": "Look: FUTURISTIC/CYBERTEK - sleek silver-white alloy and graphite panels, seamless rounded forms, thin "
                  "glowing cyan light strips.",
}
CAMERA = ("Seen from RimWorld's building camera: orthographic, high above and tilted about 35 degrees from the south, so "
          "the top face is fully visible and lit from above and the front, and anything tall extends up the image. ")
SPRITE = ("A RimWorld game sprite of ONE object, centred, filling most of the canvas, on a real transparent background "
          "(alpha channel): the object alone, with bare transparent space around it. ")

BATTERY = {
    "Scrapper": "a junker BATTERY BANK: a row of mismatched salvaged battery cells and old vehicle batteries strapped "
                "together in a dented rusty tin tray, copper bus bars and wire twists joining their terminals, frayed tape",
    "Industrial": "a heavy INDUSTRIAL POWER-CELL BANK: a long armoured gunmetal casing with chamfered corners, bolted "
                  "access plates, two thick black terminal posts at one end, cooling ribs along the sides",
    "Modern": "a present-day BATTERY STORAGE CABINET: a long matte light-grey powder-coated steel enclosure with rounded "
              "edges, a row of vent slots, a small green status LED and a neat cable gland, like a real lithium "
              "battery backup unit",
    "Futuristic": "a sleek FUTURISTIC ENERGY CELL: a long seamless silver-white alloy capsule with graphite end caps "
                  "and thin glowing cyan charge strips along its sides",
}
GAUGE = ("Across the middle of its top face, a flat dark recessed gauge window runs across the battery's short width, "
         "about two-thirds of that width and one-eighth of its length (the game draws the charge bar there). ")
WALLLAMP = {
    "Scrapper": "a junker WALL LAMP: a bare incandescent bulb, softly lit warm, in a small dented scrap-tin reflector "
                "bolted to a rusty flat bracket",
    "Industrial": "an industrial caged WALL LIGHT: a short chamfered gunmetal housing with a protective steel cage over a "
                  "flat lens, softly lit warm white",
    "Modern": "a present-day outdoor WALL LIGHT: a slim rectangular dark-grey aluminium bulkhead fixture with a frosted "
              "white lens, softly lit",
    "Futuristic": "a sleek futuristic WALL LIGHT: a silver-white alloy bar with a continuous glowing cyan-white light "
                  "strip along its face",
}
LOOKICON = {
    "Scrapper": "a small square badge made of a rusty dented tin plate with mismatched bolts in its corners, a strip of "
                "frayed tape across one corner and a twisted copper wire",
    "Industrial": "a small square badge made of a heavy chamfered gunmetal steel plate with four bolts and a yellow-black "
                  "hazard stripe band along its bottom edge",
    "Modern": "a small square badge made of a clean white moulded-plastic plate, like a present-day wall-switch plate, "
              "with a single grey three-prong socket in it",
    "Futuristic": "a small square badge made of a seamless silver-white alloy plate with rounded corners and a thin "
                  "glowing cyan light strip across it",
}
POLEICON = {
    "LinkWire": "A UI command icon: two white ceramic power-line insulators, one at the left and one at the right, joined "
                "by a single dark power wire hanging between them in a gentle sag, and a bright green round badge with a "
                "white plus sign over the wire's middle.",
    "UnlinkWire": "A UI command icon: a single dark power wire running between two white ceramic insulators, cut through "
                  "in the middle by a pair of red-handled wire cutters, the two cut ends curling apart with a small "
                  "yellow spark.",
    "UnlinkAll": "A UI command icon: one white ceramic insulator on a short pole top at the left, with three dark power "
                 "wires running from it to the right, every wire cut short and its loose end dropping, and a bright red "
                 "round badge with a white diagonal bar in the lower right corner.",
}
# The eligibility gate binds a render to a def in OUR XML; vanilla Battery/WallLamp are not, and their ThingStyleDefs
# (<Def>_<Look>, as StandingLamp_<Look>) are owed by Gimme Some Slack's next version. Installed by install_vea_art.py.
NO_SUBJECT = ("the %s look of the vanilla def %s: that def is not in our XML and its ThingStyleDef is owed by "
              "Gimme Some Slack's next version; installed by install_vea_art.py")
ICON_STYLE = ("Painted in RimWorld's own UI icon register: a few large clear shapes, readable at 64 pixels, centred, "
              "filling about 80% of a square canvas, on a real transparent background (alpha channel). ")


def rows():
    out = []
    for L in LOOKS:
        out.append({
            "id": "vea_battery_v1_%s_east" % L.lower(), "rimflow_item_id": ITEM, "priority": 20,
            "prompt": SPRITE + CAMERA + "Draw " + BATTERY[L] + ". It is a large stationary building that stands on a 1x2 "
                      "cell footprint, lying with its long axis running left-right across the image. " + GAUGE + LOOK[L],
            "canvas_w": 512, "canvas_h": 512, "facings": [],
            "no_subject": NO_SUBJECT % (L, "Battery"), "target_texpath": "RimMandrake/GimmeSomeSlack/Styles/%s/Battery" % L,
            "drawsize": 3, "biome_neutral": True,
        })
        out.append({
            "id": "vea_walllamp_v1_%s_east" % L.lower(), "rimflow_item_id": ITEM, "priority": 20,
            "prompt": SPRITE + CAMERA + "Draw " + WALLLAMP[L] + ", a small lamp fixed flat against a wall. The wall is "
                      "at the LEFT edge of the image: the lamp's flat back plate is flush against the left edge and the "
                      "lamp projects to the right, shining right. " + LOOK[L],
            "canvas_w": 256, "canvas_h": 256, "facings": [],
            "no_subject": NO_SUBJECT % (L, "WallLamp"), "target_texpath": "RimMandrake/GimmeSomeSlack/Styles/%s/WallLamp" % L,
            "drawsize": 1, "biome_neutral": True,
        })
        out.append({
            "id": "vea_lookicon_v1_" + L.lower(), "rimflow_item_id": ITEM, "priority": 20,
            "prompt": "A UI icon for the '" + L.lower() + "' look of a building style menu: " + LOOKICON[L] + ". "
                      + ICON_STYLE + LOOK[L],
            "canvas_w": 256, "canvas_h": 256, "facings": [],
            "no_subject": "UI icon of a style look, shared by every mod that offers the four looks", "biome_neutral": True,
        })
    for k, p in POLEICON.items():
        out.append({
            "id": "vea_poleicon_v1_" + k.lower(), "rimflow_item_id": ITEM, "priority": 20,
            "prompt": p + " " + ICON_STYLE, "canvas_w": 256, "canvas_h": 256, "facings": [],
            "no_subject": "UI gizmo icon for the power pole's " + k + " command", "biome_neutral": True,
        })
    return out


DERIVE = {
    ("battery", "north"): "Turn this same battery a quarter turn so its long axis runs UP-DOWN the image (it now stands on "
                          "a 1x2 footprint that runs north-south), seen from the same camera; the gauge window still runs "
                          "across its short width at its middle. Keep the object, materials, colours, detail and scale "
                          "identical; only its orientation changes.",
    ("walllamp", "north"): "Turn this same wall lamp so the wall is at the BOTTOM edge of the image: the lamp's back plate "
                           "is flush against the bottom edge and the lamp faces away from the viewer, shining up the "
                           "image; we see its top and back. Keep the object, materials, colours and scale identical.",
    ("walllamp", "south"): "Turn this same wall lamp so the wall is at the TOP edge of the image: the lamp's back plate is "
                           "flush against the top edge and the lamp faces the viewer, shining down the image; we see its "
                           "lit front. Keep the object, materials, colours and scale identical.",
}


def wave2():
    """The north/south facings, each an edit of its look's accepted east master (file after the masters are done)."""
    out = []
    for L in LOOKS:
        for (kind, facing), p in DERIVE.items():
            canvas = 512 if kind == "battery" else 256
            out.append({
                "id": "vea_%s_v1_%s_%s" % (kind, L.lower(), facing), "rimflow_item_id": ITEM, "priority": 20,
                "prompt": p + " Real transparent background (alpha channel). " + LOOK[L],
                "canvas_w": canvas, "canvas_h": canvas, "facings": [],
                "derive_from": "vea_%s_v1_%s_east" % (kind, L.lower()),
                "no_subject": NO_SUBJECT % (L, "Battery" if kind == "battery" else "WallLamp"),
                "target_texpath": "RimMandrake/GimmeSomeSlack/Styles/%s/%s" % (L, "Battery" if kind == "battery" else "WallLamp"),
                "biome_neutral": True,
            })
    return out


# Judge REDOs of 2026-11-20 (infrastructure/state/delegated/2026-11-20/Battery.json, WallLamp.json), both C2: the north
# facing came out a different size or shape from its look's other facings. v2 restates the size; same master image.
REDO = {
    "vea_battery_v2_modern_north": ("vea_battery_v1_modern_east", "Battery",
        "Redraw this same battery cabinet turned a quarter turn so its long axis runs UP-DOWN the image, seen from the same "
        "camera. It is the SAME full-size enclosure: exactly as long, as wide and as tall as in this image, so its long "
        "side spans nearly the whole height of the canvas and it is about twice as long as it is wide. Keep the vent "
        "slots, the green status LED, the cable gland and the dark gauge window across its short width at its middle."),
    "vea_walllamp_v2_modern_north": ("vea_walllamp_v1_modern_south", "WallLamp",
        "Turn this same broad rectangular wall light so its flat back plate is flush against the BOTTOM edge of the image "
        "and it faces away from the viewer: we see the top and back of the SAME broad horizontal housing, just as wide "
        "as in this image, its frosted lens hidden underneath. Keep the materials, colours, width and scale identical."),
    # second reader (same date): battery north's front face drawn too tall; Modern wall lamp east thinner than south
    "vea_battery_v3_modern_north": ("vea_battery_v1_modern_east", "Battery",
        "Redraw this same LOW battery cabinet turned a quarter turn so its long axis runs UP-DOWN the image, seen from the "
        "same camera: we look down on its long flat top, which fills most of the picture, and see only its SHORT end "
        "face along the bottom edge, a low strip exactly as tall as the front face in this image (about one third of "
        "the cabinet's width). Same length, width, height, vents, green LED, cable gland and dark gauge window."),
    "vea_walllamp_v2_modern_east": ("vea_walllamp_v1_modern_south", "WallLamp",
        "Turn this same broad rectangular wall light so its flat back plate is flush against the LEFT edge of the image and "
        "it projects to the right, seen from the same high camera: the SAME housing, just as thick and as deep as in "
        "this image, its frosted lens on its underside. Keep the materials, colours and scale identical."),
}


def redo():
    out = []
    for rid, (master, kind, p) in REDO.items():
        out.append({"id": rid, "rimflow_item_id": ITEM, "priority": 20,
                    "prompt": p + " Real transparent background (alpha channel). " + LOOK["Modern"],
                    "canvas_w": 512 if kind == "Battery" else 256, "canvas_h": 512 if kind == "Battery" else 256,
                    "facings": [], "derive_from": master, "no_subject": NO_SUBJECT % ("Modern", kind),
                    "target_texpath": "RimMandrake/GimmeSomeSlack/Styles/Modern/%s" % kind, "biome_neutral": True})
    return out


if __name__ == "__main__":
    import sys
    w = sys.argv[1:]
    print(json.dumps(wave2() if w == ["wave2"] else redo() if w == ["redo"] else rows(), indent=1))
