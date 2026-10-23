FIRST LINE OF YOUR ANSWER: list each attached image you can see and one visible detail in it (proves you can see them). If you cannot see the images, say so and stop.

You are an art director reviewing two tiny sprites in a RimWorld mod (painterly vanilla-RimWorld style, top-down building camera).

CONTEXT. A hose coupled to a fixture port (tank, pump) draws an UNDER-COUPLER beneath the fixture's art: a COLLAR at the port point and a straight PIPE running inward until it disappears under the fixture's opaque body. Four material "looks": Scrapper (rusty copper/brass, rope, wood skids, junkyard repairs), Industrial (rusted steel, rivets, yellow-black hazard stripes, heavy straps), Modern (clean painted/stainless, bolted flanges), Futuristic (white ceramic-like panels, cyan light seams, dark grey clamps). The owner's verdict: the couplers "look a little... plain and generic compared to the luxurious art they were coupling to."

The attached *_current.png panels show, per look, the current procedural UnderCollar and UnderPipe at 8x (nearest neighbour, over a checker) and three composites at 4x (AFTER render). The other images are the fixtures' own textures for each look (LiquidTank, UniversalCargoTank).

HARD GEOMETRY CONTRACT (from the C# that draws them; cannot change):
- UnderCollar.png: canvas 36 px wide x 80 px tall, RGBA. +x (left->right) points INTO the fixture; the LEFT edge is the port face where the hose's brass coupling meets it. Drawn as a quad 0.140625 x 0.3125 cells (256 px/cell). The collar's cross-axis is vertical in the texture.
- UnderPipe.png: canvas 32 x 56, RGBA. It is STRETCHED along x to any length (0.1 to ~1.5 cells), so anything that varies along x (bands, rivets, seams across the pipe) smears; only the cross-section profile (variation along y) survives. Width 0.21875 cell.
- The quad is ROTATED to face N/S/E/W, so the same texture is seen in four orientations. A baked directional light (e.g. highlight on the upper edge) will appear on the wrong side for some orientations. The fixtures themselves are lit from upper-left/overhead.
- At play zoom a cell is ~64 px on screen, so the collar is ~9x20 screen px and the pipe ~14 px wide; at close zoom (256 px/cell) they show at native size.
- The images will be produced by an image model (gpt-image, via Codex $imagegen) at a legal size (both edges multiples of 16, >=655,360 px), then downscaled to the exact canvas with premultiplied alpha. It can take reference images (the fixture texture) as style input.

WHAT I WANT, per look (Scrapper, Industrial, Modern, Futuristic):
1. A blunt critique: how the current collar and pipe fail to match that look's fixture art in material, detail level, palette, wear, edge/outline treatment and rendering style. Be specific (name colours, features in the fixture art they should echo).
2. A concrete image-generation prompt for the COLLAR and one for the PIPE, written for the image model (positive phrasing only: describe the state you want, never "no X"), short (under ~120 words each), constraints first. Include: the generation canvas and aspect (collar 9:20 portrait, pipe something that downscales to 32x56 and stays uniform along x), straight-down orthographic top view of a horizontal pipe fitting, how the lighting should be handled given the 4-way rotation, fully transparent background, the subject filling the canvas edge to edge across the right axis, and which features from the fixture art to echo (e.g. rivets, hazard stripe, cyan seam, rope wrap, brass bolts).
3. A short "must not be drawn" list per sprite (things that would break the contract: e.g. ground shadow, perspective end-caps, details along the pipe's length that would smear when stretched, glow halos outside the silhouette).
4. Your recommendation on whether the PIPE is better generated as a long pipe image then collapsed to its average cross-section profile (making it uniform along x), or generated directly; and whether any along-axis detail can survive at all.
5. Anything about detail density at 9x20 screen px: what reads, what turns to mud.

Answer in Markdown with one section per look, then a short general section. Do not include shell commands.
