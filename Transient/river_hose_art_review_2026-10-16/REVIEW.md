# River works and hose joins: art review (2026-10-16, ledger RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS)

Art is unchanged and nothing was commissioned. Critics: Codex `gpt-6.1-sol`, effort high, images passed with `codex exec -i`
(`ask.py`; prompts in `prompts/`, raw answers in `answers/`). Two independent passes per subject (A = engineer+artist brief,
B = fresh-eyes readability brief). Codex output is guidance, not authority. Its pixel sizes are untested at game zoom.
Overview: `overview.png`.

## Evidence honesty

| subject | evidence |
|---|---|
| A. River works (weir, stake, silt trap, ferry, sluice, panning, ford) | **OFFLINE composites only.** No in-game capture of any river work exists in Transient (searched filenames and recent bench_live/fw/gssfw/review captures). Water in the composites is synthetic. |
| B. Hose, pump, tank, reel | **LIVE** crops of the owner's 2026-10-16 screenshots (pump + hose + rigid pipe + tank + orange hose) plus **offline** reel|pump|tank adjacency composites. No live capture of a reel, pump and tank touching exists (the dark tall rectangle in the live shots is not the reel sprite; unidentified, Codex also could not tell). |

## What to fix first (each line is a candidate owner decision)

1. **Weir: redraw as a low blunt sill with a crest, plus a spill/foam toe and an upstream-pool tint** (building sprite plus a water overlay). Today it reads as a fish trap. Both passes agree this is the biggest river failure.
2. **Weir: author per-direction art, not a 90-degree rotation of the baked 3/4 view** (rotatable=true today), and decide how a 1x2 weir spans a river (chain of connected sections, or accept an open tip with a bypass wake).
3. **Hose joins: give tank, pump and reel visible facing ports and a bridge piece** (nozzle root on the object, flange or union, exposed 8-12 px of spool). Both passes rank this first for hoses. Pipe into a tank must show a nozzle, not vanish behind the foot.
4. **Hose/coupling gauge: shrink hose and coupling to one family of sizes.** Passes disagree on numbers (A: hose 10-12 px, coupling 16-20; B: hose 6, pipe 8, union 12). Both say the 70 px coupling is wider than the pump cell. The existing 0.65x proposal is directionally right but may not go far enough.
5. **Pump: a bigger/heftier pump.** Passes DISAGREE on footprint: A endorses the 2x1 skid, B says keep 1x1 (about 54 x 44 px body) and drop the striped collars. Owner decision: 2x1 versus 1x1.
6. **Reel: shrink it (about 120 px wide against today's about 170), keep the drum visible, and add a tangential payout guide (about 16x10 px fairlead)**; the hose leaves from the drum's lower tangent, not a dangling coupling. Plus a visible supply swivel on the pump-facing side.
7. **Pump flow arrow (about 10x6 px, pump top)** so adjacency shows direction. B only; cheap.
8. **Stake line: draw a connected ridge or wall between stakes** so it reads as a levee, not lamps. Lamp itself is fine; both passes say leave it.
9. **Ferry: let the existing rope strip run visibly from post to post** (the post alone reads as a winch/bollard). B ranks this second in value per effort.
10. **Silt trap: show water contact and a sediment wedge against the upstream face.** Ford: see section A6.

## A. River works (offline composites)

Images: `weir_scene_3x.png`, `weir_scene_true_scale.png`, `river_works_textures_zoom.png`, `ford_composite.png`, `ford_png_512.png`.
Source facts: weir texture 512, drawSize 2.2, size 1x2, rotatable; stake 0.6 drawn; silt trap 1.2; ferry post 0.8; ferry rope 256x64 strip.

### A1. Weir
- **Reads as** (both passes, high confidence): a tapered fishing net, fish corral or collapsed walkway with a basket at the broad end; the weir does not read as a low dam.
- **Should look like:** a continuous level crest across the flow, water falling over a spill face, broad calm tinted pool upstream, broken white foam toe and eddies downstream, bank end tied into the shore with no slit; the bank-end store as a separate readable box or basket.
- **Fixes, ranked:**
  1. Replace the tapered silhouette with a low blunt timber sill (Codex B: 128x64 native for the 1x2 rotated footprint, crest beam about 6 px, 3-4 squat supports, no fan of tall poles).
  2. Add water cues as an overlay: upstream pool tint with current streaks suppressed, 10-14 px spill face, 3-5 px broken foam toe, a few eddies (Codex: overlay or mote layer, not baked, but a baked static version is the minimum).
  3. Per-heading art; a rotated 3/4 bitmap rotates its lighting and elevation cues sideways.
  4. Resolve the span: 2 cells cannot dam a wider river; chain sections or show a bypass wake round the tip.
  5. Breach variant: removed crest section plus a foam plume (flood failure currently has no art).
- **Confidence:** high on diagnosis (both passes), medium on every pixel number. **Disagreement:** none on diagnosis; A suggested keeping the building within one-cell depth and spelling stages of mote layers, B gave a detailed pixel table; they are compatible. Codex could not check actual in-game rotation, draw offset or water masking (synthetic water).
- Side finding (unverified): the old review image `Transient/biome_ffar/img/scale_RM_BankWeir_2171178d19_28528d_full.png` shows a distillery, not a weir, so it is a stale or mislabeled sheet image; do not use it as evidence.

### A2. Bank stake (levee)
- **Reads as:** a lantern on a bollard (success as a lamp). A separated line holds nothing back.
- **Should look like:** an uninterrupted earth ridge or filled timber wall with stakes as secondary markers, corners and endpoints connected.
- **Fixes:** connected ridge or crib piece between neighbours (graphic linking) with a 3-4 px crest highlight; shrink the dominance of the long post face; damp strip on the water side.

### A3. Silt trap
- **Reads as:** a short timber fence.
- **Should look like:** a wet baffle entering the margin water with a sheltered pocket and a sediment deposit.
- **Fixes:** show the baffle entering water (wet band); a sediment tongue (about 24x40 px) on the sheltered side; a ripple at the tip. B: asymmetric silt apron on the upstream face with water passages.

### A4. Ferry post and rope
- **Reads as:** winch or mooring bollard; the 256x64 rope strip is fine but only shows as a pale line at game zoom.
- **Should look like:** post tops on both banks and a continuous taut line, rope leaving the spool tangentially, a raft or landing.
- **Fixes:** run the rope visibly between posts (both passes); a landing or raft cue; B warns against redrawing the post first.

### A5. Sluice box and panning spot
- Codex only saw these on the raw sheet. Sluice reads as a trough but can read as a ladder: add a continuous wet ribbon and a discharge fan. Panning spot: pebble halo competes with the pan; simplify, two or three gold glints. Low priority.

### A6. Ford stones (my own read, not sent to Codex; Codex covered ford only generically)
- `RM_FordStones` TerrainDef sets `texturePath` to vanilla `Terrain/Surfaces/Flagstone` tinted (128,124,112). The custom `Terrain/Surfaces/RM_FordStones.png` (1024) is NOT what the def loads, so any art work on it changes nothing; confirm before spending art effort.
- Flagstone tiles read as a paved strip (`ford_composite.png`), i.e. a bridge or road, not stepping stones in water. Codex's generic guidance: bank-to-bank alignment, broad stone tops, water visible between stones, approaches meeting both banks, no continuous crest.

## B. Hose, pump, tank, reel

Images: LIVE `live_pump_reel_hose_crop.png`, `live_pipe_tank_crop.png`, `live_reel_hose_crop.png` (crops of `Transient/bench_live_20261016/owner_hose_1.jpg`, full shots `owner_hose_2/3.jpg`, `owner_pump.png`). OFFLINE `reel_pump_tank_adjacent_Industrial.png`, `reel_pump_tank_adjacent_Modern.png`, `reel_deployed_vs_pumphookup_industrial.png`; existing mock `Transient/liquid_connections_2026-10-16/mock/pump_to_tank_Industrial.png`. This extends `design/RimMandrake/liquid_connections_visuals_2026-10-16.md` (not redone).

### B1. Tank, pump and reel side by side
- **Reads as** (A and B): a large hose dispenser, a small loose pump accessory, a storage tank. The reel's big valve housing looks like it pumps by itself; pump mouths point nowhere; the tank has no receiving socket; nothing says which way fluid goes. Reel envelope is about 170 x 140 px against the tank's 120 x 94 although both are 2x2.
- **Should look like:**
  - Flow order first. Dispensing: tank -> pump suction (axial port), pump discharge (radial outlet, elbowed) -> reel supply swivel at the hub; the reel does not make pressure. If the tank is being filled, connect the tank to the discharge instead.
  - Ports sit on cell-edge lanes (32 or 96 px along a 2-cell edge, not the 64 px side midpoint) and only compatible facing ports connect; a join is drawn once, owned by one object.
  - Join kit per look (Codex B, sizes native px at 64/cell): port stub 8x8, flange collar 3x14, spool 4x8 (stretched), hose union 8x12, hose ferrule 10x12, blanking cap 3x10 (shows an unused port), optional elbow 14x14 and saddle 10x10. A and B agree on pieces: nozzle neck + flange pair + short spool for rigid, union + ferrule for hose, flexible whip + union into the reel swivel.
  - Hose leaves the reel tangentially from the lower or front drum tangent through a guide, traceable 12-18 px before its first bend, then ends under the coupling lip; parked end sits in a cradle, never both a dangling coupling and a deployed hose.
  - Minimum convincing join: two rooted sockets, an uninterrupted exposed bridge (8-12 px), one dark seam and a contact shadow.
- **Fixes, ranked:** (1) sockets plus bridges, incl. an explicit tank nozzle; (2) one gauge for hose, pipe and fittings; (3) reel scale and a readable drum plus payout guide; (4) pump mass and opposed ports; (5) flow arrow.
- **Disagreements between the two passes:**
  - Pump footprint: A prefers the proposed 2x1 skid (108-116 x 46-54 px body) and wants a more elevated view, a distinct radial outlet and fewer striped collars; B rejects the 2-cell width (a 135 px assembly for a 1x1 machine), wants a 48-54 x 38-44 px close-coupled silhouette. Owner call. A also says: if 1x1 is mandatory, redraw compact at 52-58 px, do not shrink the skid.
  - Hose numbers: A hose 10-12 px, coupling 16-20 px; B hose 6 px, pipe 8, union 12 (B is much thinner than the 0.65x proposal's 0.25-0.30 cell = 16-19 px). Needs a mock at both sizes before choosing.
  - A frames flow tank -> pump -> reel with the tank feeding the pump; B suggests the same but flags the reverse is possible. Gameplay must say which.
  - A flagged the mock's pump as a side elevation (raise the camera); B did not mention it.

### B2. Live crops
- **Pump + hose (live):** the pump reads as a small motorised fitting; the lightning bolt covers its casing; the brass coupling plus tan hose wrap dominate. The thin orange hose with a frayed-looking end reads as an electrical cable, not a hose (B).
- **Pipe into tank (live):** the rigid pipe disappears near the tank's lower-left foot, so it reads as passing behind the tank; no entry nozzle (A, high confidence for these crops).
- **Reel (live):** the shot contains a dark tall rectangle with the orange hose attached; neither pass could tell what it is and the reel sprite (see `reel_deployed_vs_pumphookup_industrial.png`) is a drum on a stand, so this rectangle is NOT the reel art as drawn offline. Needs a joint look; whether the sprite drawn there is a rendering fault is undetermined.
- Codex's decisive next check: one real in-game tank -> pump -> reel placement, one connected hose-to-pipe branch and one unconnected crossing, at ordinary zoom.

## Reproduce
`make_composites.py`, `make_hose.py`, `make_overview.py`, `ask.py <name> prompts/<name>.md <images...>` (runs `codex.exe exec -i`, needs the Windows scratch drive). Answers: `answers/{weir_A,weir_B,hose_A,hose_B}.answer.md`.
