# The flora commission template — proposal

**Item:** FLORA_COMMISSION_TEMPLATE_1 · Fable design pass, 2026-09-10 · **PROPOSAL, not
ratified — nothing here is built, no art is generated** (art generation HELD until the
Codex channel is fixed; this template is what makes the un-hold productive).

Owner, verbatim (2026-09-10, after ruling the flora review): *"Seems like making plants
might need a different template then animals, so the ecosystem stays coherent and the
renderer likely needs a lot more guidance on what's a good idea. Worth thinking very
deeply about that."*

Inputs this answers: the round-2 flora review
(`design/Jawa/worldbuilding/review/round2/flora_decisions_propagated.json` — 169
existing-plant rows, 118 new-thing demand rows, 60 owner notes, the edit-once-inherit
principle), the biome sheets (`design/Jawa/worldbuilding/biomes/*.md`), the size-bin
CONFIG in `design/Jawa/worldbuilding/review/flora_assignment_register.html`, the
"redo" ruling (`infrastructure/artpipe/README.md`), the scale-ownership precedent
(`infrastructure/state/items/TREE_GRAPHICS_OWNERSHIP_1.md`), and the creature-art
contract (`skills/generating-rimworld-sprites/SKILL.md`).

House style: every rule this doc INVENTS (rather than derives from a ruling, a sheet
law, or a measurement) is flagged **[INVENTED]**.

---

## 1. Why a plant is not a creature — the diagnosis

A creature commission specifies **one individual**: silhouette, facings, palette, style
match against a reference. It is reviewed the way it is played — one thing on screen,
looked at.

A plant is judged as a **population**. Five engine facts (all confirmed in
`Source/RimWorld/Plant.cs` / `PlantProperties.cs`) change what the art must survive:

1. **The same sprite is drawn at every growth stage.** `visualSizeRange` (default
   0.9–1.1) is lerped through `growth` — the sprite is scaled, not swapped, unless an
   `immatureGraphicPath` is authored. A commission that only looks right at full
   growth is wrong for most of the plant's life.
2. **One def, many sprites per cell.** `maxMeshCount` (1/4/9/25) draws up to 25 copies
   of the sprite inside one cell for grasses. A grass commission is really a
   commission for a *texture element* that tiles against itself.
3. **Variants are random, side by side.** `Graphic_Random` scatters the A/B/C files
   across one field. Variants that differ too much read as different species growing
   mixed; too little and the field bands visibly.
4. **The plant never stands alone.** `wildClusterRadius`/`wildClusterWeight` and
   `commonality` decide whether it appears as lawn, copse, or lone landmark — and its
   neighbours are the *other* plants of the same biome roster. The unit of review is
   the biome's ground at default zoom, not the sprite.
5. **The engine owns motion and shadow.** `topWindExposure` sways the top of the mesh;
   `shadowData` (if declared) draws the shadow. Anything baked into the PNG — a cast
   shadow, a lighting direction, a horizon — fights the engine and every neighbour.

So the creature template's core question ("does this individual read?") becomes three
questions for flora: **does the individual read · does the field of them read · does
the biome's whole roster read as ONE flora?** The template below is structured around
those three, and around the owner's edit-once-inherit principle from the review sheet:
*"each plant edited ONCE; plant-level properties inherit across all rows."*

---

## 2. Two layers: the biome flora register, then the plant card

Mirroring the inheritance principle: everything true of a whole biome's flora is
written **once**, in a per-biome **FLORA REGISTER HEADER**; each commissioned plant is
a short **PLANT CARD** that inherits the header and states only its deltas. A renderer
prompt is assembled mechanically as *header clauses + card clauses* — the header is
what makes 27 biome groups' worth of commissions consistent without 118 hand-written
prompts drifting apart.

**Where they live [proposal]:** the register header as a new `flora_register` block in
the biome's existing roster JSON (`design/Jawa/worldbuilding/biomes/rosters/<sheet>.json`
— already the data home the generators read, per `rosters/_SCHEMA.md`); the plant
cards as entries under it. The biome *sheet* (§4/§6/§9) stays the authority; the
header **cites sheet laws by section number and never restates them** (per the
2026-09-09 deletion ruling: where only discipline enforces a duplicate, write a
pointer).

---

## 3. The biome flora register header (written once per biome)

```
flora_register:
  sheet:            <biomes/<name>.md>                # the law source, cited not copied
  palette_family:   3-5 anchor colors (hex) + banned hues, derived from sheet §9
  light_regime:     the biome's light, as a prompt clause (see below)
  silhouette_register: the biome's shape grammar, as a prompt clause, from sheet §9
  ladder:           the biome's flora slots and their fill state (see below)
  hard_bans:        sheet §6 rule numbers that bind flora, listed by number only
  contrast_law:     how co-occurring layers stay distinguishable (see below)
  renderer_base:    the assembled prompt preamble every plant in this biome shares
```

**palette_family.** Every biome sheet already carries §9 "Artistic theme" with a
palette in prose ("scattering-blue at distance, glass-clear and grey underfoot…").
The header turns that prose into **3–5 named hex anchors plus explicitly banned
hues**, so an offline validator can measure a candidate sprite's mean color against
the family (§7). Deriving hexes from prose is a judgment pass — proposed as a
BENCH-with-owner conversation per biome, one sitting, same loop as the biome sheets
themselves. **[INVENTED: the 3–5 anchor count; the sheets rule the palette, the
number is just enough to gamut-check against.]**

**light_regime.** Plants are lit by their biome, and Ash'karr's light is ruled per
biome: the dryland ladder is literally a sun-angle table
(`README_BIOME_GRAMMAR.md` — AridShrubland 9.2° above horizon, Wasteland 0%), the
Lantern Deeps ban free light (sheet §6.6), the Contagion lives in a storm shadow with
UV law (sheet §6.2), the nightside is geothermal-only. The header states this as a
**prompt clause** ("lit by dim low-angle amber light, no visible light source, no
directional shadow") — but see §5: the sprite itself must stay direction-neutral;
light regime drives *palette temperature and contrast*, never a baked sun.

**silhouette_register.** The biome's shape grammar, from sheet §9's "silhouette
language" ("fractal — ferns, dandelion-heads, fuzzballs, transparent and small" for
the Blue Desert). Planet-wide, on top of it, the **recognizability rule**: nothing
Earth-nameable — applied to flora by name in the review (the register purged
Earth-nameable plants; the one question card, `q:the_forge:earth-plant-names`, was
ruled **in**). The clause is written positively for the renderer: *what the shapes
are*, not what they aren't.

**ladder.** The biome's flora niches and how many species fill each. Proposed slots
**[INVENTED — the slot names; the underlying structure is in every sheet's §4]**:

| slot | reads as | typical engine params |
|---|---|---|
| ground cover | the biome's "grass" — the color of the ground at zoom-out | small bin, maxMeshCount 4–25, high commonality, no cluster |
| mid flora | shrubs, blades, fruiting bodies — the texture of walking | small–medium, maxMeshCount 1, moderate commonality, often clustered |
| vertical landmark | trees, towers, titans — navigation and identity | large–TITAN, commonality low or hand-placed (sweetline precedent) |
| films & mats | crusts, sheets, roof-organisms — reads as terrain-adjacent | special: may be terrain or Filth-like rather than Plant; card must say which |

The ladder is the coherence instrument: a commission names its slot, and the header
shows the slot's current occupancy — so we can see a biome with three landmark trees
and no ground cover *before* art is drawn. It also enforces each biome's density
laws: arid_shrubland §6.6 caps the whole ladder at "no dense flora except venomvine"
(the quincunx law); the Rot's §6.1 requires every slot be fungal; the Blue Desert's
§6.2 bans sowable versions of any of it.

**contrast_law.** Two rules so a biome's flora reads as ONE flora yet stays
distinguishable **[INVENTED, both]**:
- *One family, stepped in value:* every plant's palette sits inside the biome family;
  **adjacent ladder slots separate by VALUE (lightness), not by hue.** Value survives
  zoom-out and colorblindness; hue contrast at small sprite sizes reads as noise.
  (Consistent with the render-offline lesson already in memory: "value beats hue for
  contrast.")
- *One accent per biome:* at most one flora species carries a saturated accent color
  outside the family (a bloom, a glow). Two accent species compete; zero is allowed.
  The accent slot is named in the header so commissions don't each claim it.

**renderer_base.** The literal shared prompt preamble (§5) with the family, light and
silhouette clauses substituted in. Stored so every worker and every retry uses the
same words — the anchor-with-words pattern the sprite skill already proved for
multi-facing creatures.

---

## 4. The plant card (one per commissioned plant)

Fields marked ⊕ are the ones a creature commission does not have.

```
plant_card:
  name:             working name (recognizability rule applies; Ash'karr register, not Earth)
  from:             the demand row (ledger:<biome>:<slug>) or the improve row it serves
  slot: ⊕           ground cover | mid flora | vertical landmark | films & mats
  function:         one line: what it does in the biome ENGINE (sheet §3/§4 citation)
  admission:        the sheet law that admits it, cited by section — no bare verdicts
                    (roster-schema convention)

  ecology: ⊕
    commonality:    design choice (roster convention)
    cluster:        wildClusterRadius/Weight intent — lawn / copse / solitary / hand-placed
                    (hand-placed = the sweetline precedent: NOT in wildPlants at all)
    terrain:        fertility band / terrain affordance it grows on
    co_reads_with:  the 2-3 roster plants it will most often share a screen with —
                    the contact-sheet reviewers must see them TOGETHER (§6)

  scale: ⊕
    size_bin:       owner's bin (small <1 · medium 1–2.2, person=1.5 · large 2.2–5 · TITAN 5+
                    — squares on screen at full growth, register CONFIG)
    visual_size:    visualSizeRange min~max in cells. THE BIN IS THE CONTRACT: max sits
                    inside the bin; an owner note like "7 cells wide" IS this field.
    footprint:      single-tile with oversized visual (TREE_GRAPHICS_OWNERSHIP precedent)
                    unless the card argues otherwise
    growth_floor:   what the sprite looks like scaled to min growth — reviewer checks
                    the SMALL end too, not just full growth

  graphics: ⊕
    graphic_class:  Graphic_Random (default for plants) | Graphic_Single
    variants:       count (default 3: A/B/C — vanilla convention) + variance budget (§5)
    mesh_count:     maxMeshCount (1 unless ground cover; 4/9/25 draws that many copies
                    per cell — ground cover art is a tiling ELEMENT)
    immature:       immatureGraphicPath needed? (engine scales the adult sprite otherwise;
                    needed when growth must be READ, e.g. the Cracked Lands bloom-crop's
                    "visible growth" demand). leafless* paths: normally NO — no seasons
                    on Ash'karr (TreeBase-not-DeciduousTreeBase precedent) — unless a
                    harvested/stripped state is designed.
    wind:           topWindExposure intent (stiff crust vs swaying blade — engine-side,
                    but the ART must have a top that can shear without looking broken)
    shadow:         engine shadowData or none — NEVER baked into the PNG

  special:          mechanic_load, roster-schema style: none | C#: <what> — carries the
                    owner-note behaviors (twinkling lights = animation question §8;
                    "spawns red slime masses when damaged"; "hatches ocular creature
                    when damaged") so a commission that needs code is visibly not
                    art-only
  prompt_deltas:    the plant's OWN clauses appended to the biome renderer_base
  validation:       PROVE / EXPECT / LIES three-liner (sprite-skill format), written
                    at commission time, before any art exists
```

The card is deliberately short — the header carries the weight. A commission that
cannot fill `function` and `admission` from the sheet is the sheet's problem, not the
artist's: it goes back to the biome conversation, per "the sheet drives the roster."

**The 162 art:"improve" rows ride the same card** with `from:` pointing at the
existing def: ecology and scale prefill from the def (and the owner's 60 notes — the
"N cells wide" notes are `visual_size` orders, the move-notes are roster edits, not
art), and only `graphics`/`prompt_deltas`/`validation` are authored fresh. Per the
2026-09-10 "redo" ruling: `improve` keeps identity and refines; `redo` (1 row:
`forsaken_crags` dusk-rat — a fauna row on the flora sheet's ledger) is full
regeneration.

---

## 5. Renderer guidance — the plant delta over the creature skill

`generating-rimworld-sprites/SKILL.md` already owns: canvas math (128 px/cell of
*visual* size, generator ceiling ~1024–1280), chroma-key alpha, legal generation
sizes, downscale-survival ("silhouette, not surface"), and the offline validator.
All of it applies. What it **lacks for plants**, to be added to the skill only after
this template is ratified and a first commission proves the clauses:

1. **Perspective clause.** Creatures are reviewed east-facing side profile (artpipe
   ruling). Plants ship ONE sprite, no facings, drawn in RimWorld's slightly
   elevated near-side-on view: *"viewed from slightly above, straight on, the whole
   plant visible, base at the bottom of frame."* Not top-down (that reads as a map
   icon), not eye-level (that reads as a photograph).
2. **Ground contact.** *"The stem/base terminates cleanly at a defined ground line;
   no ground patch, no soil disc, no cast shadow, no pot."* The engine composites
   onto its own terrain and draws its own shadow; a baked shadow doubles up and
   drags a lighting direction with it.
3. **No environment.** *"Flat solid <chroma> background, no horizon, no sky, no
   other plants, no objects, no text"* — the sweetline prompt already models this.
   Light is ambient and direction-neutral; the biome's light regime enters as color
   temperature ("lit dimly in cold blue-grey ambient light"), never as a sun.
4. **Repetition tolerance — the 200-instances rule [INVENTED].** A ground-cover or
   mid-flora sprite will appear dozens-to-hundreds of times on one screen. *No
   distinctive blotch, no face-like feature, no strong left-right asymmetry* — any
   unique mark becomes a visible repeating pattern. The **asymmetry/detail budget
   scales inversely with commonality**: lawn plants are near-symmetric texture
   elements; a solitary TITAN may be as individual as a creature (every sweetline
   "has a name"). This is the single biggest divergence from creature prompting,
   where a distinctive mark is an asset.
5. **Variant budget [INVENTED].** Default 3 variants (vanilla A/B/C convention).
   Variance allowed: **silhouette and pose vary; palette, material and style do
   not** — same plant on a different day, not siblings. Ground cover may warrant
   more variants (it tiles hardest); a unique landmark may ship 1. The validator
   checks the band both ways (§7).
6. **Growth-floor clause.** State in the prompt that the silhouette must survive
   being scaled to ~40% *(the default visualSizeRange floor is 0.9× but commissioned
   ranges are wider — compute the actual floor from the card)*: no load-bearing fine
   detail; the read is the outline. Same law as "silhouette, not surface," applied
   to scale instead of downsampling.
7. **Canvas from VISUAL size, not footprint.** `texture edge = visual_size.max ×
   128 px`, capped by the generator ceiling with achieved px/cell stated (skill
   rule). Footprint stays 1×1; occupancy on canvas is checked against the declared
   bin (§7). For maxMeshCount grasses the canvas is per-element, so grass is small
   canvas by construction — do not inflate it.
8. **Negative list, phrased positively where possible.** The failure modes an image
   model reaches for on "plant": produce/crate/market shots, a botanical
   illustration on white with roots exposed, a potted specimen, a photograph with
   depth of field, a landscape containing the plant. The base prompt's positive
   framing ("single plant, whole plant visible, game asset, flat background")
   forecloses most; the rest ride the negative tail as in the sweetline prompt.

---

## 6. Coherence review — how a biome's flora is judged before and after art

- **At commission time (no art yet):** the ladder table (§3) is filled for the whole
  biome — slots, occupancy, palette anchors, the accent claim. One page per biome;
  BENCH sanity-checks it against the sheet, flags oversubscribed/empty slots.
- **After art, before deploy:** an offline **biome contact sheet** — every roster
  plant plus the new candidates at true relative scale with the colonist figure (the
  review register already renders exactly this; reuse its renderer), composited over
  a neutral card in the biome's terrain color. Judged Fable-tier per the standing
  art-review ruling (owner sees art only in staged review environments); graded on:
  reads as one flora · ladder slots distinguishable at default zoom · accent
  discipline holds · no Earth-nameable silhouette.
- **In game, eventually:** one quicktest map per biome group with the roster live,
  screenshot at default zoom — the only place cluster behavior and maxMeshCount
  tiling are real. Rides existing game-up batching rules; never a per-plant load.

---

## 7. Offline validation — what a machine checks before art costs a review

Extends `validate_sprite.py`'s existing gates (canvas, alpha, fringe, fragments,
coverage). New plant checks, all computable from the PNG + the card — **all four are
[INVENTED] and their thresholds must be CALIBRATED against known-good vanilla/donor
plant textures before any is trusted to reject** (per the instruments-that-lie
standing lesson — validate against a known answer first):

1. **Palette distance.** Mean color and dominant-cluster colors inside the biome
   family gamut; banned hues absent. Catches the renderer drifting to Earth-green in
   a silver biome.
2. **Occupancy vs bin.** Subject span / canvas edge compared to the declared
   size_bin mapping — the plant equivalent of the creature validator's span check.
   Catches a "TITAN" drawn as a centered small object in a big canvas.
3. **Variant self-similarity band.** Perceptual distance between A/B/C: below the
   floor = wasted variant (near-identical); above the ceiling = reads as another
   species. Palette distance between variants near zero even when silhouette
   distance is large.
4. **Baked-environment detector.** Dark mass below the ground line (shadow), or
   near-opaque pixels spanning the full canvas width at any row (horizon/ground
   strip). Catches the two most common environment leaks mechanically.

A tiling/repetition check (autocorrelation of a synthetic 3×3 self-tile) was
considered and **deliberately left out of v1**: the biome contact sheet catches
repetition artifacts by eye more reliably than an uncalibrated metric, and §6 already
mandates that sheet. Revisit only if the contact sheet keeps catching the same
defect.

---

## 8. Open questions — the owner's, not ours

1. **Palette anchors per biome** — §3 needs the §9 prose turned into hexes; proposed
   as one conversation sitting, same loop as the sheets. Ratify or delegate?
2. **Animated flora** — the owner's own note (AB_WildRadagast: *"Is it possible to
   animate a bush like this so that its little lights twinkle slowly?"*). Vanilla
   plants are static; twinkle needs a shader/comp lift (C#). Worth a spike item, or
   ruled out?
3. **Films & mats slot** — several demands (mold-mat roof organism, welcome
   blankets, glower crust, weep-mats) may be terrain/Filth-like rather than Plant
   defs. Each card must declare which; does the owner want a standing preference?
4. **The accent-per-biome cap and the contrast law (§3)** are invented coherence
   rules — ratify, amend, or strike.
5. **Set-demands** (rainbow suite "3–4 blooms", the fractal-flora set, the twilight
   kelp forest) — one card per species, so the 118-row census under-counts actual
   art. Confirm the set sizes when each card is filled?

---

## Appendix A — MEASURED census of the demand rows

Source: `flora_decisions_propagated.json`, parsed whole (65 KB, 288 decision rows).
⚠️ **Honesty note:** the register's own subtitle says *"118 new THINGS to create"* —
the ledger rows are each biome's full outstanding demand (plants, creatures AND
mechanisms), all ruled **in** (commissioned). They are NOT 118 plants. Kind tags
below are slug-derived guesses for planning only (**flora** = clearly a plant,
**?** = plausibly flora, untagged = fauna/mechanism/other): **33 clear-flora + 6
possible-flora rows**, several of which are multi-species sets — so the plant-card
count will land near or above 40 once sets are expanded. The other ~79 rows ride the
existing creature/mechanism templates.

Also measured, same file: existing-plant rows 169 (143 distinct defNames); art
verdicts improve **162** / keep 6 / redo 1; placement in 150 / move 15 / out 4;
size bins small 46 / medium 80 / large 35 / titan 8; explicit sizeBin rescales vs
prefill: 3 (all the_rot); owner notes: 60 (dominated by "N cells wide" visual-size
orders — i.e. the `visual_size` field of §4 is the thing the owner already edits by
hand).

Demand rows per biome group (27 groups, Σ=118):

| biome group | rows | flora-tagged rows |
|---|---|---|
| arid_shrubland | 7 | sweetline-trees · the-fuzz · venomvine-fortress · tree-guardian-uniques? |
| desert | 7 | defending-shade-plants · staggerseed-cycle-plant · ultracactus |
| dune_sea + deep_desert | 8 | glass-nub-light-pipe · silverbole · mirror-plated-sun-axis-giant? |
| fall_line | 3 | wreck-shade-flora-pockets |
| forsaken_crags | 4 | — |
| nightside_ice | 6 | chemical-frosts? · sessile-catalytic-sheets? |
| poison_forest | 3 | dark-crust-phototroph |
| terminator_sea + the_grey_deep | 5 | salt-rimed-blade (grey variant) · pillar-mason-film? |
| terminator_sea + the_twilight_deep | 7 | salt-rimed-blade (black-sail) · mold-mat-roof · kelp-forest set (deferred, diving mods) |
| the_blue_desert | 4 | transparent-fractal-flora set |
| the_contagion | 1 | — |
| the_cracked_lands | 4 | bloom-crop · twisted-trees + shade-line grasses/mosses (set) |
| the_fever_wood | 4 | — |
| the_forge | 3 | — |
| the_greentide | 5 | digestive-accelerant-fruit · greatbole-living-tower |
| the_miasma | 5 | rainbow-flora suite (3–4 blooms) · the-stranded? |
| the_propane_lakes | 2 | — |
| the_pyrelands | 5 | quickgrass · scorch-fruit |
| the_rot | 5 | tea-source guardian-mushrooms · pale-tree (anima reskin) |
| the_rust_cathedral | 2 | — |
| the_scald | 3 | welcome-blanket mats |
| the_scarlands | 3 | glowers radiotrophic crust |
| the_slime | 1 | — |
| the_sump | 4 | edge-chemotroph ring · wick-plant |
| the_webwork | 4 | pale-flowers · parasitic-root-mat |
| wasteland | 5 | radiotroph dosimeter-lawn + vault-root tree (set) |
| weeping_stones | 8 | blade-flora bladder-fruit · weep-mat drip-garden |

Sanity check the template holds against this demand: every flora-tagged row lands in
a §3 ladder slot (lawns: dosimeter-lawn, quickgrass, shade-line grasses · mid: blades,
fuzz, staggerseed, wick, pale-flowers · landmarks: sweetline, silverbole, greatbole,
ultracactus, pale-tree, sun-axis giant · films & mats: mold-mat, welcome-blanket,
glower crust, weep-mat, chemotroph ring, root-mat, phototroph crust, catalytic
sheets) — no demanded plant falls outside the four slots, and the films & mats slot
is the busiest, which is why §8 Q3 exists.
