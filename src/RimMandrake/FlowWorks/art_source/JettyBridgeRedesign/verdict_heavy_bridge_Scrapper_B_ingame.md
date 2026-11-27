# Judge 3: Scrapper heavy bridge as the game draws it (in game), 2026-11-27

Judge: claude-opus-5-5, a blind judge. I did not make the work, and I am not judge 1 or judge 2.
Brief: design/RimMandrake/art_judge_brief.md (clone RIMMANDRAKE_ADD_LIGHT_ANYTHING_FLAMMABLE_ORDER_TO_ALL_COLONISTS.det, HEAD 1d217829ff).
Item: RIMMANDRAKE_DRAW_SCRAPPER_JETTIES_HEAVY_BRIDGE_IN_HIS_PICKED_MANNER. The owner's words: "FlowWorks, default look Scrapper: the
heavy bridge and both jetties still draw the OLD art ... Generate Scrapper versions in the manner of his picks, art judge first,
install through art install; the art judge also rules cables drawn over a colonist and posts on old anchor frames."
Subject: the installed pieces src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/SuspensionBridge/Scrapper/RM_SuspensionDeck_Heavy_Strip_{root,mid,tip,solo}.png,
as RimWorld draws them (ArchSmall, FlowWorks deployed). sha1 prefixes: root 378354d8ec6d, mid b71ab8a8973c, tip 571ee0e021d7,
solo 58f4835bce0d. These are byte-identical to the pieces that judge 2 kept offline (generated/tiles/heavy_bridge_Scrapper_B_*).
The game's own reading (readings.json): all three bridges draw RimMandrake/FlowWorks/SuspensionBridge/Scrapper/RM_SuspensionDeck_Heavy_Strip,
complete=True, ends=own,own; ew2 draws root,tip; ew4 and ns4 draw root,mid,mid,tip. Post = Scrapper/RM_SuspensionDeck_Steel_Post,
cable = Cables/RM_Cable_Chain. The anchors draw Scrapper/RM_SuspensionAnchor_Heavy (style def RM_SuspensionAnchor_Heavy_Scrapper).
Not judged (harness): the black pit edge and the "norm" label.
This is the in-game look that judge 2 left open (his Q1 and Q2). Root and tip are the only pieces that ew2 draws, and mid is drawn by
ew4 and ns4. No captured bridge is one square long, so the game draws no solo piece here. Solo stays on judge 2's offline KEEP.

## Verdict: KEEP (deck pieces). Cables over a colonist: NOT ACCEPTABLE for the far-side hanger (code fix, pieces untouched). Posts on anchors: ACCEPTABLE

| piece / question | verdict | notes |
|---|---|---|
| root | KEEP | The 6-bolt end plate meets the anchor's deck edge at the west end (EW) and the south end (NS) |
| mid  | KEEP | Olive and brick-red plates and rust girders. The mid,mid joints do not show in ew4 or ns4 at 131 px/cell |
| tip  | KEEP | The mirror of root: the end plate meets the anchor at the east end (EW) and the north end (NS) |
| solo | KEEP (offline only) | The captures draw no 1-square bridge. Judge 2's offline KEEP stands |
| (a) near cables over the colonist | ACCEPTABLE | Correct depth: the near cable is between the camera and him |
| (a) far hanger over the colonist's head | NOT ACCEPTABLE | Depth error, a code fix. The pieces are not touched and it does not block their KEEP |
| (b) posts on the anchors, EW and NS, both ends | ACCEPTABLE | His pick B's geometry. Both ends face the deck |
| (b) anchor in the same hand as the deck | NO, polish | The anchor is a clean grey concrete slab with a dark lattice frame, the only part not in the Scrapper hand |

### (L) The look as a whole: KEEP
- Play zoom (~60 px/cell; judge/play_three.png, cut from ew4_heavy_Scrapper.png):
  - All three bridges read as one heavy rusted deck: dark bolted end plates, an olive and red plated body and rust-orange girder rails.
  - The deck stands clearly apart from the dug-pit floor and the ground, so it is not grey mud (B2 passes on both faults).
  - It is wider and heavier than the slim Scrapper C bridge, in the layout of his pick B.
  - The rusty posts and chains match the deck.
  - The red panel repeats once per square (judge 2's rhythm polish). At this zoom it reads as plate variety, not as a stripe.
- Close (~131 px/cell; the 656 px captures and the crop3x sheets):
  - The girder rivet rows run straight through every joint.
  - At every end, the root and tip end plates sit against the anchor's deck-facing edge, and both ends mirror.
  - In NS (angle 270), the 2x3 bolt plates turn to 3x2 correctly, and the panels stay upright with no smearing.
  - No keyline is drawn (B1a). The cast shadows are the engine's own and are not baked into the art (D4). The material reads as
    rusted plate, not paint (B4). The deck sits centred in the pit and within its width (D3).
- Defects that the brief names: none on the deck pieces. Passed: B1a, B2, B3 (beside Scrapper C and its own posts and chains), B4,
  C3 (top-down, as pick B), D1 (judged at ~131 and ~60 px/cell), D3, D4, E1, E2, E3 (new art, not owner-kept), and E4 (his note is met:
  new Scrapper art in the manner of pick B, not the old atlas).

### (a) Cables drawn over a colonist: the near cables are ACCEPTABLE. The far hanger is NOT ACCEPTABLE
In every shot the colonist stands drafted on a mid-span deck square. The cables are listed in order, top of screen to bottom.
- EW 2 (crop3x_ew2, Dmitri, on the root square near the west post):
  - Bare head: a far-side (north) hanger drops from the far main chain straight into the top of his head and ends on his scalp.
  - Bare head: the near (south) main chain runs diagonally from the near post top across his neck and chest. A near hanger hangs
    over his torso down to the near girder. Both are acceptable.
  - Hatted: the same far hanger runs down through the hat's crown to its brim, so it reads as a chain pinned through the hat. The
    near main chain and the near hanger cross his chest as in the bare shot. Acceptable.
- EW 4 (crop3x_ew4, Panshen, mid-span):
  - Bare head: the far main chain passes just above his head. A far hanger comes down from it and its end hook lands on his
    forehead and scalp. This is the most visible case.
  - Bare head: the near main chain crosses his hips and legs, and a near hanger hangs over his lower body. Both are acceptable.
  - Hatted: the far hanger runs through the crown and the brim, and the far main chain touches the top of the crown. The near chain
    is as in the bare shot.
- NS 4 (crop3x_ns4, Dejonge): both chain runs pass beside him, left and right. Nothing crosses him, bare or hatted.
- Ruling:
  - A near cable drawn over him is correct, because it is in front of him.
  - A far cable drawn over him is a depth inversion: it is behind him and must be hidden by his head and hat. At ~128 px/cell it
    reads as a chain hooked into his skull. It happens to every colonist who stands mid-square on any E-W heavy bridge, so ordinary
    play reaches it.
  - At play zoom it is a 2-3 px line and hard to see. That is why it does not block the deck KEEP. It is still a fault, not polish.
    The owner asked for this ruling, and the error shows at the zoom where a player looks at a colonist.
  - His installed Industrial pick B has the same fault (judge 2, j2/anchors_and_ind_pawn.png), so the cause is shared code, not this
    art.
- The fix: code only. No art change and no def change. It does not touch the pieces.
  - File: src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_DeckArt.cs. The cable print is at lines 456-459
    (`cableY = AltitudeLayer.PawnUnused.AltitudeFor()`). Lines 547 (`beamY`, the beam-bridge rails) and 601 (a second cable-run
    print) use the same layer. Whoever fixes it must check whether those far sides also cross a pawn.
  - In an E-W run (dir east/west), print the far-side (north) main cable, its hangers and its far backstays below Pawn, for example
    at AltitudeLayer.BuildingOnTop plus a few AltInc, which is still above the deck.
  - Keep the near side at PawnUnused.
  - In an N-S run, both sides may stay where they are, because neither crosses a pawn.
  - The test first: a selftest that asserts the far-side cable altitude is below Pawn and the near-side altitude is above Pawn,
    red on the current code.
  - Then the in-game check: the same mid_hat capture shows the hat brim over the far hanger.
- Not fixed by me. Test-2 evidence: no access. My launcher scopes this run to writing this one file, with no commits and no ledger
  writes. Today this fault sits only as a polish line in design/concepts/FlowWorks/version/polish.md (commit 1d217829ff). My
  ruling makes it a code item. The parent must file it (test 1 passes: the owner asked, and ordinary play reaches it).

### (b) Posts on the anchor frames: ACCEPTABLE. Both ends face the deck. The anchor does not share the deck's hand (polish)
- EW, both ends (ew2/ew4 endA and endB; crop3x rows 2):
  - The near post's foot plate stands on the slab's south (front) edge and overhangs it by a few pixels. The engine's post shadow
    grounds it.
  - The far post stands on the slab's north edge directly behind it. In top-down it lines up with the near post, so the two read
    as one tall post with two chain crowns. His pick B draws the same.
  - The backstays land on the slab's outer corners.
  - The slab's inner panel and its hidden lattice column are on the deck side at both ends (they mirror), so each end faces its deck.
  - The anchor's lattice column is covered by the post and the deck end plate, so no doubled upright shows.
- NS, both ends (ns4 endA south end and endB north end; judge/ns4_ends_x2.png):
  - The posts stand just outside the slab's sides, beside the anchor's own portal columns. Their chain posts and backstays run
    along the axis and land at the slab's outer corners.
  - South end: the anchor's lattice portal is at its deck edge.
  - North end: the portal stands at its deck-side (south) edge and rises up the screen, which is consistent with the ~35° camera.
  - The posts at the north end rise above the slab like the portal, and taller than it.
  - Both ends face the deck.
  - Judge 2's polish still holds: in NS the chains cover most of each post, so a post reads as a column of chain with olive and
    rust showing.
- Same hand? No. The Scrapper heavy anchor (Scrapper/RM_SuspensionAnchor_Heavy_{north,south,east}.png, last changed 2026-11-05
  a4c3e75d29) is the Industrial anchor, a little darker and grainier: clean grey concrete, a dark steel lattice frame and steel rails.
  It has no rust, olive plate or lashing (judge/anchor_scr_vs_ind.png). At play zoom the two pale blocks are the cleanest and
  brightest part of the bridge.
- Why it is acceptable now:
  - It reads as a concrete abutment, and a rusted scrap deck on concrete footings is believable material (B4).
  - His pick B composes with this same anchor.
  - His ticket names the anchors "old anchor frames" and asks only how the posts sit on them. It does not promise new anchors.
  - The posts sit correctly.
  - So this is not a refusal.
- If he wants the anchor in the deck's hand, the fix is art only. Redraw Scrapper/RM_SuspensionAnchor_Heavy_{north,south,east}.png
  and their _m masks in the Scrapper manner of pick B: a rust-streaked slab, rusty bolted foot plates under each post position,
  and a riveted rusty frame in place of the clean lattice. Keep the present outline, the slab extents and the deck-side edge, so
  the post and backstay landings still meet.
  - No def change: RM_SuspensionAnchor_Heavy_Scrapper already points at that path.
  - No code change, and no change to the deck pieces.

## Polish lines (no ticket, block nothing)
- The Scrapper heavy anchor is not in the Scrapper hand. It is clean grey concrete with a lattice frame (see (b) for the art-only
  fix).
- In NS, the chains cover most of each post (judge 2, still true in game).
- The red mid panel repeats once per square. At play zoom it reads as plate variety (judge 2, still true).
- Untested in game: the solo piece. No 1-square heavy bridge was captured.

## Proposals
- None.

## Evidence
Captures (\\wsl.localhost\Ubuntu\home\mandrake\rm\runs\clones\RIMMANDRAKE_ADD_LIGHT_ANYTHING_FLAMMABLE_ORDER_TO_ALL_COLONISTS.det\Transient\heavy_scrapper_look\):
- crop3x_ew2_heavy_Scrapper.png, crop3x_ew4_heavy_Scrapper.png, crop3x_ns4_heavy_Scrapper.png: the (a) cable crossings and the (b) ends at 3x.
- ew4_heavy_Scrapper_endA.png: the EW end at native ~131 px/cell.
- ew4_heavy_Scrapper.png: the whole station at play zoom.
- readings.json: the DECKART readings.

My crops (D:\ClaudeWork\rimmandrake\heavy_scrapper_look\judge\):
- play_three.png: all three bridges at play zoom, native.
- ns4_ends_x2.png: the NS south and north ends at 2x.
- anchor_tex.png: the Scrapper anchor north, south and east textures.
- anchor_scr_vs_ind.png: the Scrapper and the Industrial anchor side by side.

Judge 2's offline evidence (D:\ClaudeWork\rimmandrake\heavy_bridge_scrapper\j2\):
- anchors_and_ind_pawn.png: pick B's ends, and the same far-hanger fault in pick B.

Code (read only): src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_DeckArt.cs:456-459 (and the same layer at 547 and 601).
