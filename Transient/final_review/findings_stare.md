# WORLDMAP_FINAL_REVIEW_1 — Phase 2 STARE findings (in-game, SEEN)

Judge: Fable subagent (L3 Fable-evaluation carve-out), 2026-09-11.
Inputs: all 30 PNGs in `Transient/final_review/stare_shots/` + `stare_recheck.png`
(unmanifested 31st, extreme-zoom recheck of the western-pan smears), read in full.
Extends WORLDMAP_REVIEW_REPORT.md §7 — nothing here repeats the flat-render read.
Capture caveats honored: right-edge alert stack, bottom toolbar, orbital ring décor
and fixed 3 AM lighting judged around, not reported as map defects.

Engine fact that frames everything: **text labels render only at closeup altitude
(~350); every 800-altitude global shot is label-free.** Global "label barrenness"
is zoom behavior, not authoring. Second engine fact: **the fixed game hour paints a
hard night shadow over the antistellar hemisphere** — at globe zoom the cap is
near-black; at 350 the same terrain reads fine (see Umbra).

## Per-shot notes (SEEN)

### Globals, 800 altitude

- **stare_substellar.png** — Dayside disc composes as a place: Scald lake + green
  halo west, grey Anvil massif center-right with the dark Rust mass, cream desert
  with dune stipple. Directions are tellable — the anti-bullseye doctrine passes
  from orbit, not just on the equirect. Snag (−): droid landmark icons cluster
  ×5–6 in the Anvil/Rust area, reading copy-paste; gold hive-flower icons repeat
  nearby. Snag (+): the two Empire roundels flanking the Scald read as "the Empire
  watches the water" — accidental storytelling, keep.
- **stare_dayside_N.png** — Terminator band curves across the top; road hairlines
  visible but subordinate. Icon density comfortable. Coast at NW limb ragged, good.
- **stare_dayside_S.png** — The south emptiness reads intentional-desolate, not
  unfinished — dune stipple carries it. Confirms §7's crowded-east/empty-south as
  defensible contrast. DNA-helix landmark icons at the limb repeat identically.
- **stare_dayside_E.png** — Twilight Sea fills the east limb with a convincingly
  ragged coast; Anvil grey at west edge. Colony marker (cyan house) is the most
  saturated object on screen — engine UI, but note it will dominate every player
  screenshot taken near start.
- **stare_dayside_W.png** — The best global: Scald bullseye-with-character, rose
  canyon bands SW, sea NW. Hero-globe material (see Strongest #4).
- **stare_terminator_000.png** — Clean day→twilight→ice gradient; navy Twilight
  Sea patch reads as water even unlabeled. Colony marker center (start sits near
  this meridian). Ring-edge-on line is décor, ignored.
- **stare_terminator_045.png** — Fungal purple lower-right vs cream left: night
  reads different from day at a glance. Minor icon pile-up at the bottom limb
  (foreshortening, not authoring).
- **stare_terminator_090.png** — The north transect is a textbook climate ladder:
  dark nightwood band → lavender fungus → cream. Strong. DNA icons on the ice
  again, identical ×3 in frame.
- **stare_terminator_135.png** — Reads fine; east-limb icons stack by
  foreshortening. Gold snowflake-ish icons cluster bottom-center.
- **stare_terminator_180.png** — Strongest terminator shot: Twilight Sea crossed
  by the terminator, white pack-ice on the night shore, green Dew shore on the day
  side. Snag (−): two Empire roundels sit nearly overlapping on the east shore —
  the one true icon collision seen at global zoom.
- **stare_terminator_225.png** — Balanced but quiet; sparse center-south. OK.
- **stare_terminator_270.png** — Weakest global: a broad pale lavender/cream wash
  with low internal contrast between the top vegetation line and the bottom
  night-grey mass. Nothing wrong, nothing to hold the eye.
- **stare_terminator_315.png** — Dashed road reading top-left (roads render as
  dashes at this zoom — legible, subordinate, correct). East-limb ice clean.
- **stare_nightside_N.png / _S.png / _E.png / _W.png / stare_antistellar.png** —
  All five dominated by the hard night shadow: a featureless near-black disc over
  the antistellar cap. The lit ring around it — white NightsideIce, purple fungal
  belt — composes handsomely (nightside_S's crescent layering is genuinely
  pretty). Inside the black: faint pale road dashes catching grazing light read as
  eerie traces (+, lore-true for a dark side), and R2-droid landmark icons float
  in blackness (−, three identical in one void). Everything authored under the cap
  — Deadstone Umbra, the ice ovals, the named regions — is invisible from orbit at
  the shipped fixed hour. That is lighting, not paint: no map corrective exists
  short of engine ambient changes. Accept as lore ("the dark side is dark") and
  do nightside marketing/review shots at closeup altitude.

### Closeups, 350 altitude

- **stare_closeup_Scald.png** — The centerpiece confirms in-engine: blue disc,
  green ring hugging the shore, mesa rim, rose-banded canyon terraces SW, roads
  winding with acute natural bends, rivers braiding through the ring. **Rivers
  and roads pass the shape doctrine here — winding, acute, zero comb teeth.**
  Snag (−): the "Scald" and "Scald Spine" labels overlap/cross, with an Empire
  roundel and a landmark icon sitting on the text — the map's marquee name is its
  messiest label.
- **stare_closeup_Anvil.png** — The white emptiness of the Anvil against the dark
  Rust Cathedral/Scorch mass is the best value contrast on the planet. Snag (−):
  "Scorch" and "Rust Cathedral" labels overlap at frame-left (confirmed again in
  Fall_Line). Snag (waiver-grade): the road crossing the Anvil runs long smooth
  arcs plus one straight dashed stretch — the only CAD-flavored road seen, and
  it crosses a dead-flat pan, where straight is what a road would do. Waive.
- **stare_closeup_Dune_Sea.png** — Gold drift stipple sells the Dune Sea; Fever
  Wood's braided winding rivers west of it are the best hydrology on the map.
  Road skirts the dune margin organically. "Glare" region reads. No defects.
- **stare_closeup_Twilight_Sea.png** — Pack-ice floe texture on the sea is
  excellent; tan hex archipelago mid-sea is a nice surprise; coasts ragged.
  Snag (minor −): the west shore, where sea-blue meets Nightspill slate, is
  tonally close — the coastline there is found by texture, not color.
- **stare_closeup_Fall_Line.png** — Golden talus stipple reads as debris slopes;
  Grey Sea ice-speck water good. Snags (−): "Fall Line"/"Fall Line Barrens"
  labels are white-on-cream, the lowest label contrast seen; Scorch/Rust
  Cathedral label overlap again; three identical droid icons inside Rust
  Cathedral. Colony marker + settlement + landmark icons make a small pile at
  The Abandoned Mines — the start neighborhood is the busiest icon spot on the
  planet.
- **stare_closeup_Pyrelands.png** — Sulfur greens distinct from every other
  band; road web converges naturally. Snags (minor): "Pyrelands" and "Salt Gate"
  labels stack tightly; the mottled purple/tan/white patchwork west of Salt Gate
  reads noisy/undecided at this zoom — transitional mottle, defensible.
- **stare_closeup_Cinders.png** — Pan gradations read. Snags (−): a landmark icon
  sits mid-word on "Cinders"; **three pale elongated pill-smears on the pan west
  of Notch** catch the eye as possible render artifacts.
- **stare_closeup_Umbra.png** — The revelation shot: at 350 the "black" cap is a
  readable slate expanse of dense dark debris stipple, with a truly darker
  charcoal heart top-center and a single pale road worming into it. "Umbra",
  "Lantern Deeps", "Fuelmere", "Frostvein", "Cinderdark" — best label set on the
  planet, evocative and cleanly spaced. Horror landing-site sell, ready-made.
- **stare_closeup_Long_Sand.png** — Road trunk-and-branch across Long Sand:
  winding, junctions natural, no comb. Twilight woods (Sweatwood/Stepwood) with
  pale blossom speckle are quietly lovely. Clean.
- **stare_closeup_Notch.png** — Confirms the Cinders smears at identical world
  positions (so terrain/decal, not a render glitch); start area reads coherent:
  mines + salt shore + roads. "Cinders" icon-through-label again.
- **stare_closeup_Dew_Belt.png** — The habitable-ribbon transect: sea → olive Dew
  Horn/Belt → rose Scald terraces. Sells the whole tidally-locked premise in one
  frame. Snag (−): Scald/Scald Spine label collision visible from this angle too
  (twice-confirmed). Two roads run close-parallel near Dew Horn for a stretch —
  minor.
- **stare_closeup_Pan.png** — Rimewall's dark diagonal crag band is a strong
  graphic element; Pan's cracked-clay texture already reads at 350; Glass Reach's
  dark-green glassy streak is distinct. Tiny green rectangles on far-west ice —
  too small to judge, not an eyesore.
- **stare_recheck.png** (extreme zoom, unmanifested) — The pan smears resolve to
  flat tan rock-formation decal art with hard paper-cutout outlines plus a swirl
  decal on cracked-clay terrain. So: real placed art, but it reads as an artifact
  at mid-zoom and as a flat sticker up close — the smallest genuine eyesore found.

## Synthesis

### The 5 strongest visual moments

1. **The Scald** (`stare_closeup_Scald.png`) — crater lake, green ring, rose
   terraces, winding roads. THE key art: trailer orbit-pull shot, box/store hero,
   loading screen #1.
2. **Terminator over the Twilight Sea** (`stare_terminator_180.png`) — one frame
   holds day, night, water, ice and the green shore. Loading screen #2 / the
   "tidally locked" one-image explainer.
3. **The Umbra's dark heart** (`stare_closeup_Umbra.png`) — slate darkness, a
   charcoal core, one road in. The horror-scenario landing-site sell; also the
   proof the nightside is authored, for anyone who only saw the black cap.
4. **Dayside from orbit** (`stare_dayside_W.png`) — the bullseye-with-character
   globe. Store-page planet beauty shot; the anti-bullseye argument as one image.
5. **Fever Wood braid against the Dune Sea** (`stare_closeup_Dune_Sea.png`) —
   braided rivers vs gold drift. The caravan-fantasy sell; strongest landing-site
   pitch for a "normal" start.

### The 5 weakest, with correctives

1. **Global-zoom nightside is a featureless black disc** (all five night
   globals) — authored content invisible from orbit at the shipped fixed hour.
   Corrective: none to the map (it is lighting and it is lore-true); present
   nightside content at closeup altitude only. **Cost: S** (presentation
   discipline, zero edits) — engine ambient change would be L and is not
   recommended.
2. **Label collisions on marquee names** — Scald/Scald Spine overlap (seen from
   two angles), Scorch/Rust Cathedral overlap (two angles), icons sitting mid-word
   on "Cinders" and on "Scald". Corrective: shorten/rename one of each colliding
   pair or shift the feature extents that drive label placement. **Cost: S.**
3. **Pale rock-decal smears on the western pans** (Cinders/Notch, recheck) —
   flat paper-cutout landmark art reading as render artifacts at mid-zoom.
   Corrective: swap, shrink or restyle that decal (or delete the 3–4 placements).
   **Cost: S–M.**
4. **Identical landmark icons repeat in-frame** — DNA helix ~10× around the
   nightside ice ring, R2-droid ×3–6 in Rust Cathedral and the Umbra cap. This is
   the visible face of punch row 4's 42 duplicate landmark names. Corrective:
   thin duplicates / diversify icon defs in the same sitting as row 4's renames.
   **Cost: S.**
5. **The 270° terminator quadrant is a pale wash** (`stare_terminator_270.png`,
   echoed by the mottle west of Salt Gate) — the one viewing angle with nothing
   to hold the eye. Corrective: accept (every planet has a boring longitude), or
   anchor the NW mid-band with one named feature/mutator. **Cost: none / M.**

### What this changes in WORLDMAP_REVIEW_REPORT.md

- **PENDING §(a) river/road shape — CLEARED, positively.** Scald, Dune_Sea,
  Dew_Belt, Long_Sand, Pyrelands all show winding rivers, braids, acute
  confluences and organic road junctions. Zero comb teeth, zero ruler roads
  (sole waiver: the straight Anvil pan crossing, defensible). The one risk the
  report said could demote the verdict is gone.
- **Punch row 11, Gelatinous streak — CLEARED at globe scale.** From all 18
  global angles no magenta band reads on the sphere; the equirect polar
  exaggeration explanation holds. Demote to no-action (tile-grain check optional).
- **Punch row 6 (nightside road dead-ends) — visual harm demoted.** Under the
  night shadow they are near-invisible from orbit and read as eerie traces where
  they catch light. Topological cleanup still owed; urgency down.
- **Punch row 4 — strengthened.** Duplicate landmarks are not just a data smell;
  the repeats are visible in single frames (see Weakest #4).
- **ADD punch rows** for Weakest #2 (label collisions, S) and #3 (pan decal
  smears, S–M). Both are polish, neither ship-blocking.
- **Provisional verdict: the YES stands and hardens** — the STARE was the named
  acceptance test ("the picture is the acceptance test") and the picture passes.
  Nothing seen calls for re-authoring anything; everything new is S-cost polish.
