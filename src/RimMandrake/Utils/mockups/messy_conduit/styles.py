"""Selectable art styles and messiness levels for the Messy Conduit mock-ups.

A STRAND KIND is one cable type: width (in cells), colours and a surface pattern.
A STYLE is a weighted mix of strand kinds plus its decal vocabulary (junctions,
splices, caps, hookups, grime). A LEVEL is how ropey the routing is.
Colours are hex strings; the renderer derives outline/shade/highlight when absent.
"""

PATTERNS = ("plain", "gloss", "metal", "rubber", "corrugated", "coil", "twin", "braid", "copper")


def K(name, width, base, pattern="plain", **kw):
    d = {"name": name, "width": width, "base": base, "pattern": pattern}
    d.update(kw)
    return d


STYLES = {
    "cybertek": {
        "num": 1, "title": "Cybertek",
        "blurb": "ultra-sleek grey metallic cables, chrome ferrules, hex junction pods with a cyan status light",
        "kinds": [
            (K("silver", 0.085, "#b7bec6", "metal", dark="#14171a", hi="#ffffff"), 3),
            (K("graphite", 0.095, "#4a5058", "metal", dark="#0d0f11", hi="#d8e2ea",
               accent="#46d8ee"), 2),
            (K("gunmetal", 0.07, "#7d858e", "metal", dark="#121417", hi="#f4f8fb"), 2),
        ],
        "junction_t": "hexpod", "junction_x": "hexpod_big", "splice": "ferrule",
        "splice_mode": "strand", "cap": "endcap", "plug": "ferrule",
        "wander_scale": 0.7, "grease": 0.0, "tape": None, "staple": "#c9d0d6",
        "fray_live": "#ffd27a", "fray_dead": "#7a6a5a",
    },
    "extcord": {
        "num": 2, "title": "Extension cord",
        "blurb": "glossy modern extension cords in orange, green, brown, yellow and blue; power-strip junctions, plug-into-socket joiners",
        "kinds": [
            (K("orange", 0.09, "#ee7a1c", "gloss"), 3),
            (K("green", 0.085, "#3d9c3c", "gloss"), 2),
            (K("brown", 0.085, "#7a4a26", "gloss"), 2),
            (K("yellow", 0.09, "#efc824", "gloss"), 2),
            (K("blue", 0.085, "#2f6fd6", "gloss"), 2),
        ],
        "junction_t": "powerstrip", "junction_x": "powerstrip_big", "splice": "plugjoin",
        "splice_mode": "strand", "cap": "plughead", "plug": "plughead_in",
        "wander_scale": 1.0, "grease": 0.0, "tape": ["#262626"], "staple": "#e8e8e0",
        "fray_live": "#ffc070", "fray_dead": "#9a6a40",
    },
    "starwars": {
        "num": 3, "title": "Star Wars friendly",
        "blurb": "solid black thick power cables, corrugated steel conduit hose, coiled black cord; greebled junction boxes",
        "kinds": [
            (K("black_thick", 0.135, "#1d1d20", "rubber", hi="#7a7e86"), 3),
            (K("corrugated", 0.12, "#8f918c", "corrugated", dark="#1c1d1b", hi="#e6e8e2"), 2),
            (K("coiled", 0.1, "#202024", "coil", hi="#8c9098"), 2),
        ],
        "junction_t": "greeble", "junction_x": "greeble_big", "splice": "collar",
        "splice_mode": "strand", "cap": "boot", "plug": "collar",
        "wander_scale": 0.85, "grease": 0.25, "tape": None, "staple": "#9a9c98",
        "fray_live": "#ffcf70", "fray_dead": "#7a5838",
    },
    "jawa": {
        "num": 4, "title": "Jawa: truck drivers in space",
        "blurb": "nothing matches: faded orange cord, ribbed armoured grey, red/black twin-lead, bare copper, braided green; tape lumps, grease, ration-tin junction box",
        "kinds": [
            (K("orange_cord", 0.1, "#d2681f", "gloss"), 3),
            (K("armoured", 0.1, "#7f817b", "corrugated", dark="#1b1c1a", hi="#d8dad2"), 3),
            (K("twin_lead", 0.085, "#3a3a3a", "twin", c1="#c8261e", c2="#151515"), 2),
            (K("bare_copper", 0.05, "#c4733a", "copper", hi="#ffd2a0", dark="#3a1e0c"), 2),
            (K("braided_green", 0.085, "#6c7a36", "braid"), 1),
            (K("greasy_black", 0.095, "#26221d", "rubber", hi="#6e655a"), 1),
        ],
        "junction_t": "tapelump", "junction_x": "rationtin", "splice": "tape",
        "splice_mode": "bundle", "cap": "ragcap", "plug": "tape",
        "wander_scale": 1.15, "grease": 1.0, "tape": ["#1c1c1c", "#d8b21e", "#b8b4a8", "#2f5aa0"],
        "staple": "#b0a890", "fray_live": "#ffb860", "fray_dead": "#9a6a3c",
    },
}

LEVELS = {
    "tidy": {"num": 1, "title": "tidy-ropey", "strands": (1, 2), "spread": 0.05, "wander": 0.025,
             "sag": 0.05, "loop_p": 0.0, "splice_p": 0.05, "coil_p": 0.0, "tape_p": 0.03,
             "grease_p": 0.15, "hook_strands": (1, 1), "hook_sag": 0.12},
    "default": {"num": 2, "title": "ropey / jury-rigged (DEFAULT)", "strands": (2, 3), "spread": 0.09,
                "wander": 0.06, "sag": 0.12, "loop_p": 0.35, "splice_p": 0.14, "coil_p": 0.25,
                "tape_p": 0.12, "grease_p": 0.45, "hook_strands": (1, 2), "hook_sag": 0.2},
    "ratsnest": {"num": 3, "title": "rat's nest", "strands": (3, 4), "spread": 0.14, "wander": 0.15,
                 "sag": 0.22, "loop_p": 0.8, "splice_p": 0.25, "coil_p": 0.7, "tape_p": 0.25,
                 "grease_p": 0.8, "hook_strands": (2, 3), "hook_sag": 0.3},
}

STYLE_ORDER = ["cybertek", "extcord", "starwars", "jawa"]
LEVEL_ORDER = ["tidy", "default", "ratsnest"]
