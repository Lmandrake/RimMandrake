"""The options drawn for the owner's pick: three per kind. Each is a structure (deck, edge members, posts, cables, anchor,
tip) plus the look it is shown in. Text of each option: design/specs/2026-11-22-jetty-bridge-art/design.md.
RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD."""

SEAMS = (0.7, 1.15)

# ---- jetties: the tier sets the MATERIAL (steel; concrete and steel), the look sets the finish
STEEL_JETTY = [
    ("A", "Plate on I-beams",
     "Diamond-plate steel on two I-beam stringers, tube rails, twin steel posts at the root, one thick cable a side to the tip.",
     dict(deck="diamond", deck_w=0.76, girder="ibeam", girder_w=0.09, rail="tube", posts="twin", post_h=1.15, post_w=0.09,
          cable_w=0.055, anchor="steelblock", tip="beam", rivets=True, seam_spacing=SEAMS)),
    ("B", "Open grating cantilever",
     "Bar grating you can see the pit through, box-section edge beams, taller twin posts and two cables a side (mid and tip).",
     dict(deck="grating", deck_w=0.74, girder="box", girder_w=0.1, rail="tube", posts="twin", post_h=1.35, post_w=0.08,
          cable_w=0.045, fan=2, anchor="steelblock", tip="beam")),
    ("C", "Gangway truss",
     "A narrow ribbed steel gangway between two side trusses, one A-frame mast at the root, a cable from its head to each tip corner.",
     dict(deck="plate", deck_w=0.6, girder="truss", girder_w=0.16, rail=None, posts="aframe", post_h=1.45, post_w=0.08,
          post_out=0.12, cable_w=0.05, anchor="steelblock", tip="beam")),
]

HEAVY_JETTY = [
    ("A", "Cast slab, armoured edges",
     "A thick concrete slab with steel angle armour on both edges, heavy double rails, two concrete pylons with steel caps, "
     "DOUBLED cables a side, and a hazard-striped bumper at the tip.",
     dict(deck="concrete", deck_w=0.86, girder="angle", girder_w=0.07, rail="heavy", posts="twin", post_kind="concrete",
          post_h=1.25, post_w=0.17, cable_w=0.06, doubled=True, anchor="concrete", tip="bumper", seam_spacing=SEAMS)),
    ("B", "Steel box girders, concrete topping",
     "Concrete deck panels between two big riveted steel box girders, a steel portal frame at the root, doubled cables, "
     "a striped crash beam at the tip.",
     dict(deck="concrete_panels", deck_w=0.84, girder="box", girder_w=0.15, rail="tube", posts="portal", post_h=1.35,
          post_w=0.13, cable_w=0.06, doubled=True, anchor="concrete", tip="hazard", rivets=True, bolt_pitch=0.1,
          seam_spacing=(0.5, 0.7))),
    ("C", "Pier with one pylon",
     "A concrete pier deck on steel I-beam outriggers, ONE tall concrete pylon at the root with a fan of four cables "
     "(mid and tip, both sides), heavy bumper and cleats at the tip.",
     dict(deck="concrete", deck_w=0.9, girder="ibeam", girder_w=0.1, rail="heavy", posts="pylon", post_kind="concrete",
          post_h=1.7, post_w=0.24, post_inset=0.36, cable_w=0.055, fan=2, anchor="concrete", tip="bumper", seam_spacing=SEAMS)),
]

# ---- the steel suspension bridge in each look (stations 61-64): three options per look
BRIDGE = {
    "Scrapper": [
        ("A", "Patchwork plate on pipe towers",
         "Mismatched salvaged plates (olive, brick, bare) riveted over each other; towers of welded pipe; a rusty wire-rope main "
         "cable with lashed rope hangers.",
         dict(deck="patchwork", deck_w=0.78, girder="angle", girder_w=0.06, rail="rope", posts="twin", post_kind="pipe",
              post_h=1.3, post_w=0.08, cable_w=0.045, cable_style="rope", anchor="scrap", hanger_w=0.6)),
        ("B", "Container-rib deck",
         "Corrugated sheet cut from old cargo containers (faded red, blue, sand), I-beam offcut towers, wire main cable and "
         "chain hangers.",
         dict(deck="corrugated", deck_w=0.8, girder="ibeam", girder_w=0.07, rail="tube", posts="twin", post_h=1.25,
              post_w=0.1, cable_w=0.05, anchor="scrap", hanger_w=0.6)),
        ("C", "Hull plate and chain",
         "Overlapping chipped green hull plates, CHAIN main cables (link by link), welded pipe towers.",
         dict(deck="hull", deck_w=0.78, girder="angle", girder_w=0.06, rail="rope", posts="twin", post_kind="pipe",
              post_h=1.35, post_w=0.08, cable_w=0.06, cable_style="chain", anchor="scrap", hanger_w=0.5, rivets=True)),
    ],
    "Industrial": [
        ("A", "Diamond plate on I-beams",
         "Gunmetal diamond plate, bolted I-beam stringers, hazard-banded steel box towers, thick black steel main cables.",
         dict(deck="diamond", deck_w=0.78, girder="ibeam", girder_w=0.09, rail="tube", posts="twin", post_h=1.35, post_w=0.11,
              cable_w=0.055, anchor="steelblock", hanger_w=0.4, rivets=True, seam_spacing=SEAMS)),
        ("B", "Truss-stiffened grating",
         "A steel grating walkway carried between two heavy side trusses, slate towers, the main cable over the truss.",
         dict(deck="grating", deck_w=0.62, girder="truss", girder_w=0.17, rail=None, posts="twin", post_h=1.4, post_w=0.1,
              post_out=0.1, cable_w=0.05, anchor="steelblock", hanger_w=0.45)),
        ("C", "Sand-grey standard issue",
         "Sand-grey plate panels with yellow edge stripes (the setting's standard used-future hardware), slate box girders, "
         "cast saddles on the towers.",
         dict(deck="plate", deck_col=(150, 140, 118), deck_w=0.8, girder="box", girder_w=0.1, girder_col=(84, 90, 98),
              hazard_edge=True, rail="tube", posts="twin", post_col=(84, 90, 98), post_h=1.3, post_w=0.12, cable_w=0.055,
              anchor="steelblock", anchor_col=(150, 140, 118), hanger_w=0.4, seam_spacing=SEAMS)),
    ],
    "Modern": [
        ("A", "Galvanised grating footbridge",
         "Galvanised bar grating, safety-yellow tube handrails, concrete abutments, slim stainless cables.",
         dict(deck="galvgrating", deck_w=0.76, girder="box", girder_w=0.07, rail="tube", posts="twin", post_kind="steel",
              post_col=(150, 154, 152), post_h=1.25, post_w=0.08, cable_w=0.035, anchor="concrete", hanger_w=0.4)),
        ("B", "Green steel, anti-slip deck",
         "Sun-faded green painted steel edge beams with touch-up patches, a grey gritted anti-slip deck worn pale down the "
         "middle, grey rails.",
         dict(deck="antislip", deck_col=(128, 130, 126), deck_w=0.8, girder="box", girder_w=0.09, girder_col=(76, 104, 80),
              rail="tube", rail_col=(140, 144, 140), posts="twin", post_col=(76, 104, 80), post_h=1.3, post_w=0.1,
              cable_w=0.04, anchor="concrete", hanger_w=0.4)),
        ("C", "Concrete panels, stainless cable rail",
         "Light precast concrete panels with joints, galvanised edge angles, thin stainless cables doubling as the rail.",
         dict(deck="concrete_panels", deck_w=0.82, girder="angle", girder_w=0.05, girder_col=(150, 154, 152), rail="cable",
              rail_col=(200, 204, 208), posts="twin", post_kind="concrete", post_h=1.3, post_w=0.13, cable_w=0.035,
              anchor="concrete", hanger_w=0.35, seam_spacing=(0.45, 0.6))),
    ],
    "Futuristic": [
        ("A", "White composite, cyan light",
         "A seamless white composite deck with cyan light strips down both edges, graphite pylons with lit nodes, graphite "
         "cables with glowing hanger clamps.",
         dict(deck="composite", deck_w=0.78, girder="trim", girder_w=0.06, glow_edge=True, rail="glass", posts="twin",
              post_kind="composite", post_h=1.45, post_w=0.09, cable_w=0.035, anchor="composite", tip="light", hanger_w=0.35)),
        ("B", "Graphite and magenta",
         "Matte graphite deck, magenta edge light, one slim pylon per end carrying both cables, amber clamp lights.",
         dict(deck="composite", deck_col=(52, 56, 62), deck_w=0.78, girder="trim", girder_w=0.06, glow_edge=True,
              glow_col=(236, 72, 200), rail="glass", posts="pylon", post_kind="composite", post_h=1.6, post_w=0.11, post_inset=0.36,
              cable_w=0.035, anchor="composite", hanger_w=0.35)),
        ("C", "Glass deck in titanium frame",
         "Translucent glass panels (the pit shows through) in a brushed titanium frame, pale blue lights, white pylons.",
         dict(deck="glass", deck_w=0.78, girder="box", girder_w=0.07, girder_col=(176, 182, 188), glow_edge=True,
              glow_col=(150, 200, 255), rail="glass", posts="twin", post_kind="steel", post_col=(226, 229, 232),
              post_h=1.4, post_w=0.08, cable_w=0.03, anchor="composite", hanger_w=0.35)),
    ],
}

HEAVY_BRIDGE_TEXT = {
    "A": "A thick concrete slab with steel angle armour on both edges, heavy double rails, two concrete towers with steel caps "
         "at each end, DOUBLED main cables.",
    "B": "Concrete deck panels between two big riveted steel box girders, a steel portal frame at each end, doubled main cables.",
    "C": "A concrete deck on steel I-beam outriggers, ONE tall concrete pylon behind each end carrying both main cables.",
}
HEAVY_BRIDGE = [(k, n.replace("Pier with one pylon", "One pylon each end"), HEAVY_BRIDGE_TEXT[k], dict(s, tip="joint"))
                for k, n, t, s in HEAVY_JETTY]
