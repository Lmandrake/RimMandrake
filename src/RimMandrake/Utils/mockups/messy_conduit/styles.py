"""Selectable art styles and messiness levels for the Messy Conduit mock-ups.

A STRAND KIND is one cable type: width (in cells), colours and a surface pattern.
A STYLE is a weighted mix of strand kinds plus its decal vocabulary (junctions,
splices, caps, hookups, grime). A LEVEL is how ropey the routing is.

Structure (owner, 2026-10-02): THREE families -- 1 Cybertek, 2 Extension cord, 3 Star Wars --
and Jawa is a VARIANT of the Star Wars family ("03j"), not a fourth pile. The Star Wars family
carries no white cable or tape at all.
Colours are hex strings; the renderer derives outline/shade/highlight when absent.
"""

PATTERNS = ("plain", "matte", "gloss", "metal", "rubber", "corrugated", "coil", "twin", "braid", "copper")


def K(name, width, base, pattern="plain", **kw):
    d = {"name": name, "width": width, "base": base, "pattern": pattern}
    d.update(kw)
    return d


STYLES = {
    "cybertek": {
        "num": 1, "file": "01", "family": "Cybertek", "title": "Cybertek",
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
        "num": 2, "file": "02", "family": "Extension cord", "title": "Extension cord",
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
        "num": 3, "file": "03", "family": "Star Wars", "title": "Star Wars family: base",
        "blurb": "mostly smooth matte black power cable (low shine); a few dark corrugated-steel hoses and coiled black cords; greebled junction boxes. No white anywhere",
        "kinds": [
            (K("black_matte", 0.12, "#1b1b1d", "matte", hi="#3c3e42", dark="#060607"), 5),
            (K("black_heavy", 0.145, "#202022", "matte", hi="#404246", dark="#070708"), 2),
            (K("corrugated", 0.115, "#55574f", "corrugated", dark="#141512", hi="#8e9087"), 1),
            (K("coiled", 0.1, "#1e1e21", "coil", hi="#4a4c52"), 1),
        ],
        "junction_t": "greeble", "junction_x": "greeble_big", "splice": "collar",
        "splice_mode": "strand", "cap": "boot", "plug": "collar",
        "wander_scale": 0.85, "grease": 0.25, "tape": None, "staple": "#5a5c58",
        "fray_live": "#ffcf70", "fray_dead": "#7a5838",
    },
    "jawa": {
        "num": 4, "file": "03j", "family": "Star Wars", "title": "Star Wars family: Jawa variant",
        "blurb": "the Star Wars set gone feral: matte black cable dominates, a few dark corrugated and coiled pieces; dark/ochre/oil-stained tape, hose clamps, rag caps, ration-tin box, grease. No white anywhere",
        "kinds": [
            (K("black_matte", 0.11, "#1c1b1a", "matte", hi="#3d3b37", dark="#070606"), 5),
            (K("greasy_black", 0.125, "#24211d", "matte", hi="#45403a", dark="#080706"), 2),
            (K("corrugated_rust", 0.11, "#5a5246", "corrugated", dark="#16130f", hi="#8a7e6a"), 1),
            (K("coiled", 0.095, "#1f1e1c", "coil", hi="#4a4740"), 1),
        ],
        "junction_t": "tapelump", "junction_x": "rationtin", "splice": "tape",
        "splice_mode": "bundle", "cap": "ragcap", "plug": "tape",
        "wander_scale": 1.15, "grease": 1.0, "tape": ["#1a1917", "#3a3128", "#8a6a2a", "#4e4230"],
        "tape_lump": "#8a6a2a", "clamp": "#6e7072", "rag": ["#6a5a40", "#5a4c36", "#7a6648"],
        "tin_hi": "#8a8a7e", "tin_shade": 0.72,
        "staple": "#5e5648", "fray_live": "#ffb860", "fray_dead": "#9a6a3c",
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
