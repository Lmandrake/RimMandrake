# Generated options still owed (Codex sign-in revoked 2026-11-22)

Item: `RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD`. The shared Codex account's sign-in was revoked at
2:52 PM PST and still at 2:56 PM PST (one test). These are the generated versions of each procedural option, to make when
the sign-in is back. Run each through the `generating-rimworld-sprites` skill (its validator), composite over the same
pit backdrop (`art_source/JettyBridgeRedesign/backdrop.py`), and add them as a fourth column to the sheets. The procedural
sheets are complete without them.

Every prompt shares this frame:

> RimWorld building texture, strict top-down orthographic view, the game's painterly style with soft dark outlines,
> no perspective, no text. A horizontal strip 1024 x 256 px on a transparent background, four 256 x 256 tiles left to
> right: ROOT (meets the anchor at its left edge, a steel joint plate), MID (plain), TIP (end beam and two cable lugs at
> its right edge), SOLO (joint plate on the left and end beam on the right). The deck runs left to right and fills
> about 80% of the tile height, centred. Girders, rails and kerbs run unbroken across all tile edges at the same rows;
> no seam, rivet line or post within 25 px of a tile edge; no frame across the deck at a tile edge. No posts and no
> cables in the strip (the game draws them).

Each prompt below adds the material and finish. Bridge prompts make a 4-tile strip too (the game cuts its linked atlas
from it); for a bridge, ROOT and TIP both read as joint plates.

## Steel jetty (station 59)

- **A, Plate on I-beams** (each of the four looks; material always steel look): Diamond-plate steel on two I-beam stringers, tube rails, twin steel posts at the root, one thick cable a side to the tip.
- **B, Open grating cantilever** (each of the four looks; material always steel look): Bar grating you can see the pit through, box-section edge beams, taller twin posts and two cables a side (mid and tip).
- **C, Gangway truss** (each of the four looks; material always steel look): A narrow ribbed steel gangway between two side trusses, one A-frame mast at the root, a cable from its head to each tip corner.

## Heavy jetty (station 60)

- **A, Cast slab, armoured edges** (each of the four looks; material always concrete and steel look): A thick concrete slab with steel angle armour on both edges, heavy double rails, two concrete pylons with steel caps, DOUBLED cables a side, and a hazard-striped bumper at the tip.
- **B, Steel box girders, concrete topping** (each of the four looks; material always concrete and steel look): Concrete deck panels between two big riveted steel box girders, a steel portal frame at the root, doubled cables, a striped crash beam at the tip.
- **C, Pier with one pylon** (each of the four looks; material always concrete and steel look): A concrete pier deck on steel I-beam outriggers, ONE tall concrete pylon at the root with a fan of four cables (mid and tip, both sides), heavy bumper and cleats at the tip.

## Steel bridge, Scrapper look

- **A, Patchwork plate on pipe towers** (Scrapper look): Mismatched salvaged plates (olive, brick, bare) riveted over each other; towers of welded pipe; a rusty wire-rope main cable with lashed rope hangers.
- **B, Container-rib deck** (Scrapper look): Corrugated sheet cut from old cargo containers (faded red, blue, sand), I-beam offcut towers, wire main cable and chain hangers.
- **C, Hull plate and chain** (Scrapper look): Overlapping chipped green hull plates, CHAIN main cables (link by link), welded pipe towers.

## Steel bridge, Industrial look

- **A, Diamond plate on I-beams** (Industrial look): Gunmetal diamond plate, bolted I-beam stringers, hazard-banded steel box towers, thick black steel main cables.
- **B, Truss-stiffened grating** (Industrial look): A steel grating walkway carried between two heavy side trusses, slate towers, the main cable over the truss.
- **C, Sand-grey standard issue** (Industrial look): Sand-grey plate panels with yellow edge stripes (the setting's standard used-future hardware), slate box girders, cast saddles on the towers.

## Steel bridge, Modern look

- **A, Galvanised grating footbridge** (Modern look): Galvanised bar grating, safety-yellow tube handrails, concrete abutments, slim stainless cables.
- **B, Green steel, anti-slip deck** (Modern look): Sun-faded green painted steel edge beams with touch-up patches, a grey gritted anti-slip deck worn pale down the middle, grey rails.
- **C, Concrete panels, stainless cable rail** (Modern look): Light precast concrete panels with joints, galvanised edge angles, thin stainless cables doubling as the rail.

## Steel bridge, Futuristic look

- **A, White composite, cyan light** (Futuristic look): A seamless white composite deck with cyan light strips down both edges, graphite pylons with lit nodes, graphite cables with glowing hanger clamps.
- **B, Graphite and magenta** (Futuristic look): Matte graphite deck, magenta edge light, one slim pylon per end carrying both cables, amber clamp lights.
- **C, Glass deck in titanium frame** (Futuristic look): Translucent glass panels (the pit shows through) in a brushed titanium frame, pale blue lights, white pylons.

## Heavy truss bridge

- **A, Cast slab, armoured edges** (Industrial, then the other three looks look): A thick concrete slab with steel angle armour on both edges, heavy double rails, two concrete towers with steel caps at each end, DOUBLED main cables.
- **B, Steel box girders, concrete topping** (Industrial, then the other three looks look): Concrete deck panels between two big riveted steel box girders, a steel portal frame at each end, doubled main cables.
- **C, One pylon each end** (Industrial, then the other three looks look): A concrete deck on steel I-beam outriggers, ONE tall concrete pylon behind each end carrying both main cables.

Look briefs that bind every prompt: `design/specs/2026-11-22-flowworks-look-briefs/looks.md`.
