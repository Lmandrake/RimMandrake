# Jetty and bridge art: one structure, real materials, cables (FlowWorks stations 59-64)

Item: `RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD`. Written 2026-11-22 by a detached design run.
Status: options for the owner's pick. No art is installed in the mod.

## The owner's words (FlowWorks walk on his full mod list, 2026-11-22, about 3:05 PM PST)

*"The Jetties are almost ok. Their look is good. But they don't join well. It reads very much as "two squares next to
each other" rather than a single jetty as it should. They also both read as simple wood. The Steel Jetty doesn't look
steel at all. The heavy jetty is even worse. It should look cement, steel, industrial and tough. Both of them need cables
shown to connect their support on the ledge to the end of the jetty. Thick taut cables holding up that jetty end. The
bridges would be helped with that kind of art too. And please next time draw some North/South bridges for me to study as
well. It's dangerous just to look at E/W examples. Your examples of bridges are uninspired and boring. 61-64 need art
reworks that emphasize the different art styles much better. Please redo and design."*

His capture: `D:\ClaudeWork\rimmandrake\conductor\walk_20261122\flowworks_walk\stations59_60_jetties_two_squares_wood.png`.

## Where to look

| sheet | what it shows |
|---|---|
| `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD\join.png` | today's jetty beside the redesign, with the cell edges marked |
| `...\steel_jetty.png` | station 59: three options |
| `...\heavy_jetty.png` | station 60: three options |
| `...\bridge_scrapper.png`, `bridge_industrial.png`, `bridge_modern.png`, `bridge_futuristic.png` | stations 61-64: three options per look |
| `...\heavy_bridge.png` | stations 54-55 (the heavy truss bridge): three options |

Every scene sits over the real pit from his capture (spliced, not rotated, for north/south), at close zoom (128 px per
cell) with a vanilla colonist at the same scale, and again at default zoom (40 px per cell). Every jetty is drawn east
2 squares, west 1, north 2 and south 1, and in the four looks. Every bridge is drawn east/west and north/south. Small
copies are in `previews/` beside this page. The generator is
`src/RimMandrake/FlowWorks/art_source/JettyBridgeRedesign/` (`sheets.py OUTDIR` rebuilds every sheet in about a minute).

The mockups are drawn in Python, not generated. Generated art was not possible: the shared Codex sign-in was still
revoked at 2:56 PM PST (`gpt_consult.py` returned `VERDICT=ALLOWANCE exit=21`, "refresh token was revoked"). The
generated options that are still owed, with their prompts, are in `owed_generation_prompts.md`.

## 1. Today's draw, and why a jetty reads as two squares and as wood [measured]

- Each jetty square is its own thing (`RM_SuspensionJetty_Steel`, `RM_SuspensionJetty_Heavy`), drawn with
  `Graphic_Multi`: one 256 px picture per square, turned by the square's rotation.
- Each picture has a frame on all four sides and a transparent margin. Two squares side by side therefore show two
  frames and a dark gap between them. That is the "two squares next to each other" he saw.
- The bridge decks do not have this defect. They already draw from a Basic-linked 4x4 atlas
  (`RM_SuspensionDeckLink`, item `SUSPENSION_DECK_LINKED_NO_SEAMS`). The jetties were never moved onto it.
- His capture shows the **Scrapper** pictures. `RM_SuspensionJetty_Steel_Scrapper` draws
  `Scrapper/RM_SuspensionJetty_Steel` and `RM_SuspensionJetty_Heavy_Scrapper` draws the shared `Scrapper/RM_SuspensionJetty`.
  Both pictures are timber planks with rust-coloured plates. So the steel jetty and the heavy jetty are both drawn as
  wood. The heavy jetty has no Scrapper picture of its own.
- Nothing ties the far end back to the anchor: the jetty has no posts and no cables. Nothing in the picture says why
  the tip does not fall.

## 2. The join: one strip, cut into pieces

- A jetty or a bridge deck is drawn as **one continuous strip** from its root to its tip (or anchor to anchor).
- The strip is cut into square pieces: **ROOT** (meets the anchor; carries the joint plate), **MID** (plain),
  **TIP** (carries the end beam or bumper and the cable lugs), and **SOLO** (a 1-square jetty: joint plate and end
  beam on one piece). A jetty today is at most 2 squares (`RM_SuspensionMath.JettyMaxCells`), so it uses SOLO, or ROOT
  and TIP. MID is ready for a longer jetty.
- Art rules, which make the pieces join with no seam:
  1. The girders, rails and kerbs run edge to edge at the same rows in every piece.
  2. No plate seam, rivet line or rail post lies within 0.1 cell of a piece edge. Seams sit at irregular places along
     the strip, so the cell grid never shows.
  3. There is no frame and no transparent margin across the deck at a piece edge.
  4. Only ROOT and TIP carry end detail.
- One picture per tier per look: a 4-tile strip (ROOT, MID, TIP, SOLO), each tile 256 x 256, drawn with the deck
  running east. The tiles have no lighting that depends on direction (bevels are symmetric), so the draw code may turn
  a tile to any of the four directions.
- The bridge decks keep their linked atlas. Rule 2 applies to their atlases too: the bridge redraw must keep seams off
  the tile edges.

## 3. The cables

- **Posts.** Each anchor carries posts at its deck-side edge: twin posts, a portal (twin posts and a crossbeam), an
  A-frame, or one pylon at the back of the anchor. The kind is part of each option.
- **Height is drawn the RimWorld way.** A post of height H is drawn rising H cells north (up the screen) from its foot.
  So a post head is a screen point north of its foot, in every direction the jetty faces.
- **Cables.** A thick taut cable runs from each post head to a lug on its own side of the jetty tip. The heavy
  options double each cable; some options add a second cable to the middle of the jetty (a fan). Each post also has a
  short backstay to the back corner of the anchor, so the post reads as held, not balanced.
- **Shadows sell the height.** Each post and cable prints a soft shadow offset south-east by its height. The shadow of
  a cable meets the cable at the tip, where the cable reaches deck height. In a north/south view, the cable lies along
  the deck edge, so the shadow on the pit floor is what shows the height. The north/south mockups prove this works only
  with a light steel cable colour and posts set outside the deck edge (both are in the options).
- **Bridges.** The same posts become towers at both anchors. The main cable is a curve that sags between the two tower
  heads (printed as short straight runs), and hangers drop from it to the deck edge every half cell. East/west, this
  reads as a suspension bridge seen from the side. North/south, the sag shows in the shadow.
- **Over pawns.** Cables and post heads print at `AltitudeLayer.PawnUnused` (24), directly above `Pawn` (23)
  [measured: the engine enum]. A colonist on the deck is under the cables, as in the mockups. The post shafts print at
  `Building`. That printing at a section-layer altitude above `Pawn` really draws over a moving pawn is
  [guess ~80%]; the first build checks it in game.
- **Any length, any direction.** Every point is computed from the record (anchor cell, direction, length), never
  painted into a picture. So 1 square, 2 squares and any bridge span use the same code, and north/south is the same
  geometry as east/west.

## 4. The options (per kind; he picks one per kind)

Jetties take their **material from the tier** and their **finish from the look**. Each jetty sheet shows the options
in the Industrial look and each option again in all four looks.

| kind | A | B | C |
|---|---|---|---|
| steel jetty | plate on I-beams: diamond plate, I-beam stringers, tube rails, twin posts, one thick cable a side | open grating cantilever: you see the pit through it, box edge beams, taller posts, two cables a side | gangway truss: a narrow ribbed deck between side trusses, one A-frame mast. Weakness: north view is busy (the two cables cross over the deck) |
| heavy jetty | cast slab: concrete with steel angle armour, heavy double rails, two concrete pylons, doubled cables, striped bumper | steel box girders with concrete panels, steel portal frame, doubled cables, striped crash beam | pier: concrete on I-beam outriggers, one tall concrete pylon behind the root, a fan of four cables |
| steel bridge, Scrapper (61) | patchwork salvaged plates, welded pipe towers, rope-lashed wire cable | corrugated container sheet in faded red/blue/sand, I-beam offcut towers | chipped green hull plates, CHAIN main cables |
| steel bridge, Industrial (62) | gunmetal diamond plate on bolted I-beams, hazard-banded box towers | grating walkway between heavy side trusses | sand-grey standard-issue panels with yellow edge stripes, slate girders |
| steel bridge, Modern (63) | galvanised grating footbridge, safety-yellow handrails, concrete abutments, stainless cables | faded green painted steel, gritted anti-slip deck worn pale down the middle, soft touch-up patches | light precast concrete panels, galvanised edges, thin stainless cables as the rail |
| steel bridge, Futuristic (64) | white composite, cyan edge light, graphite pylons, lit cable clamps | matte graphite, magenta edge light, one slim pylon each end | glass deck in a titanium frame, the pit shows through, pale blue lights |
| heavy truss bridge (54-55) | the heavy jetty A as a bridge | the heavy jetty B as a bridge | the heavy jetty C as a bridge (one pylon behind each end) |

Wood stays for the wooden kinds (rope, timber). They take the same cable geometry later: timber towers, rope main
cables. No mockup of them is made here; he did not fault their decks.

Looks follow `design/specs/2026-11-22-flowworks-look-briefs/looks.md`. Each look's three options differ in structure,
not only in colour.

## 5. What the code must change

1. **Jetty draw.** `RM_SuspensionJetty_Steel` and `RM_SuspensionJetty_Heavy` (and their 8 ThingStyleDefs) change from
   `Graphic_Multi` to a 4-tile strip picture. `Building_SuspensionDeck.Print` for a jetty square picks the tile by the
   square's index on its record (0 = ROOT, last = TIP, length 1 = SOLO, else MID) and prints it turned to the jetty's
   direction (east 0°, south 90°, west 180°, north 270°). A new helper beside `RM_SuspensionDeckLink` holds the piece
   choice, so a selftest can read it without the game.
2. **Posts and cables.** `Building_SuspensionAnchor.Print` prints the posts and cables from the record geometry: posts
   as upright quads at `Building`, cables through the existing tiled rope printer (`RM_DrawbridgeArt.PrintRopeRun`,
   which already tiles a painted rope along any straight run) at `PawnUnused`, and the shadows as soft strips at
   `Shadows`. A bridge prints the sagging main cable as 8 to 12 runs and the hangers as short runs.
3. **Re-print.** The anchor re-prints when a square of its jetty or bridge is built, lost or raised. The drawbridge
   code already marks the neighbours dirty (`RM_Drawbridges.NotifyToggled` → `DirtyAround`); the jetty build and
   collapse paths do the same.
4. **Art.** One strip picture per tier per look for the jetties (2 tiers x 4 looks), a post picture and a cable
   strip per option and look, and redrawn bridge deck atlases that keep seams off the tile edges.
5. **Checks.** An offline selftest that (a) feeds the piece chooser every length and direction and checks the tile
   and turn, and (b) reads every deck strip and atlas picture and fails when a tile edge column shows a seam (edge
   contrast far above the interior). It must go red on today's jetty pictures, which have frames.

## 6. Build order

1. He picks one option per kind on these sheets.
2. The art for his picks (generated when the Codex sign-in is back, using the saved prompts; otherwise hand-built from
   these procedural pieces), judged by a second agent against `design/RimMandrake/art_judge_brief.md`.
3. Code change 1 (jetty strip) and its piece selftest. This alone fixes the seam.
4. Code changes 2 and 3 (posts and cables), jetties first, then bridges.
5. The review map's new north/south row (below) is staged on a free game; he walks it.

## 7. Convergent or Divergent (he rules on the split)

FlowWorks is at Design Version 0.1.0. Recommendation:

- **Convergent, Problems (stay in 0.1.0):** the jetty seam (two squares instead of one jetty); a steel jetty and a
  heavy jetty that read as wood; the four looks of stations 61-64 not reading as four different styles. Each is a
  thing he called wrong on the walk.
- **Divergent (next version, written up as their own items):** posts, towers and cables on jetties and bridges, and
  the heavy truss bridge redesign. They add new drawn structure and new draw code. His words "Both of them need
  cables" can make the jetty cables a Problem instead; then they move into 0.1.0 with change 2 for jetties only.

## 8. The review map: north/south stations and a fire under a deck (done in this run)

`src/RimMandrake/FlowWorks/northstar/owner_review_stage.py` has a new default row, `bars_bridges_ns`, staged after
station 64 so the numbers 1-64 of the earlier walks do not move:

- 65-68: the steel bridge north/south in the four looks;
- 69: **fire under a deck**: a timber bridge north/south over 1 m of chemfuel in a 4 m pit, staged UNLIT. Its caption
  names the call that lights it (`jawa/map_fire action=start` on the four pit squares under the deck), or throw a
  molotov from the lip;
- 70-75: the rope, timber, steel, heavy and both grated bridges north/south;
- 76-79: the steel and heavy jetties reaching north (rooted on the south ledge) and reaching south (rooted on the north
  ledge).

Offline test: `python3 src/RimMandrake/FlowWorks/northstar/selftest_owner_review_stage.py` reads 45 ok, 0 failures.
The new checks went red on four planted faults: a jetty rooted over the pit, a plan without the north/south row, a lit
fire station, and chemfuel beside rather than under the deck. The row has not been staged on any game.

## 9. Untested

- Nothing here was seen in game. The mockups imitate the game's draw; the cable altitude over a moving pawn is a guess
  (above).
- The north/south stage row ran only against the offline fake; the real `ProofJetty` and `ProofFillWithFluid` replies
  on north/south lines are unread.
- No second agent has judged the options yet.
