You are a skeptical senior game-graphics designer. Context: a RimWorld 1.6 mod ("FlowWorks") lets players dig pits and canals that fill with liquids (fresh/salt/boiling/icy/toxic/acid water, tinted waters, tar, oil, chemfuel, astrofuel, liquid propane, four slimes, blood, poison, brine, reaction liquor, lava planned). RimWorld is top-down 2D; a colonist is a stack of sprites (body, apparel, head, hair) drawn by a per-pawn render tree (PawnRenderTree nodes, each a mesh + matrix + material + MaterialPropertyBlock), 3 facings, rotated when lying; far zoom draws one cached atlas quad per pawn. Vanilla 1.6 swimming draws head only. Vanilla has a firefoam overlay: a splatter texture masked by the body texture.

The owner REJECTED the current look: a translucent blue "water sheet" laid over the pawn (it was in fact vanilla's generic 64px head-and-torso silhouette icon, wrong size, no facing, so two blue blobs sat off the body). He wants radically different concepts for how a colonist LOOKS: standing in liquid at ankle/knee/waist/chest, swimming or fully under, lying in it, and afterwards coated/dripping on dry ground. "Don't just play with the mask or layering of the current implementation."

My concepts (differ in kind):
A. CUT AT THE LINE: the pawn's own rendered picture is cut at the surface; below the line it is drawn under the real liquid surface (clear liquid) or not at all (opaque); a ring where the body meets the surface. Depth maps to body landmarks (ankle, knee, waist, chest, neck), not linear metres, because sprites are chibi (head is half the height).
B. TIDE MARK: the liquid is painted on the pawn's own pixels (per-node shader/overlay masked by each node's own texture) up to the highest line reached; persists on dry ground, wears off, washes off. Water = darker wet cloth and sheen; tar = glossy black with rim light.
C. THE SURFACE ANSWERS: pawn drawn plain; the liquid reacts: rings, lip/meniscus hugging the body outline, wake; thick liquids keep an open furrow behind the walker that closes at a rate set by viscosity; wet footprints/drips on dry ground afterwards.
D. BODY UNDER THE SURFACE: submerged part drawn refracted (wobble), dimmed, desaturated, with caustics and a floor shadow offset by depth; in opaque liquid a lying body shows as its own shape draped in the liquid.
E. THE LIQUID'S TELL: each liquid has a signature particle effect on the pawn: steam (boiling), smoke/fizz (acid), frost crystals (icy), flies (blood), heat glow and embers (lava), rainbow sheen (oil/fuel), slow strings (tar/slime).
F. POSE CHANGE: dedicated poses instead of overlays: wading stance, floating face-up for a downed pawn at the surface, face-down float for a corpse, vanilla head-only for swimming with a faint body ghost beneath in clear liquid.
G. LIQUID AS A GARMENT: authored art per body type and facing (like apparel) for ankle/waist/full coat with drippy edges, tinted per liquid.
H. TAR STATUE: a pawn fully coated in a thick opaque liquid is drawn through vanilla's Statue render path in the liquid's colour, eyes showing.
I. STATUS RING: a liquid-coloured puddle disc under the feet plus an icon; cheapest.

My ranking: A (first, fixes the misalignment because it uses the pawn's own picture), then D for clear liquids, then B for after, then C as polish, E per dangerous liquid; F, G, H, I held back.

Please do three things, tersely:
1. Give me at least six concepts I did NOT list that differ in kind (not variants of A-I). Name real top-down or 2D games that do each, and say what exactly they draw, when you know it; say "not sure" when you are not.
2. Attack my ranking: where is it wrong, what will look bad in practice (far zoom, pawn rotation, lying pawns, carried pawns, children, animals, mechs, opaque liquids, lava, readability for gameplay: "is she drowning?"), and what would you rank first instead.
3. For the top three in YOUR ranking, name the cheapest Unity/RimWorld render path (shader keyword, stencil, render texture, MaterialPropertyBlock, Harmony patch point) and its per-pawn cost.
