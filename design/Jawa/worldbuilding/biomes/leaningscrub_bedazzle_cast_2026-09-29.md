<!-- status: cast bible — commissioned under LEANINGSCRUB_BEDAZZLE_SITTING_1 movement 4 -->
# Leaning Scrub — bedazzle cast bible (movement 4: commission)

**Item:** `LEANINGSCRUB_BEDAZZLE_SITTING_1` · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1 (row 7)
**Date:** 2026-09-29 · **Author:** movement-4 commission agent (Fable)
**Feeds:** `LEANINGSCRUB_RULED_CONTENT_1` (defs) + `LEANINGSCRUB_MECHANICS_BUILD_1` (wind spine)
**Authorities:** `leaningscrub_bedazzle_review_2026-09-29.md` (the review; volley CLOSED),
both tickets above (every ruling below is fixed), the frozen sheet `arid_shrubland.md`
(voice only — never edited; ⚠️ `desert.md` is the Long Shade, a different biome).
Mod: `src/RimMandrake/LeaningScrub/`.

## 0. Shared law — every card obeys this without restating it

- **Voice:** the hush, and the lean. Knee-high silver-green fuzz to every horizon, all of
  it leaning the same way, all of it moving, because the wind never stops. Two floors that
  cannot see each other: the giants' floor above the canopy, the runway floor beneath it.
  No rain — fog on the ground-wind, thinning sunward. The wild has no voice, only posture.
  Descriptions talk ecology: runs, wakes, crossings, the quincunx, the sweetline.
- 🔴 **Trim law (owner, final ruling, carried on every entry):** *"Too much focus on
  constant advanced warning... Players arent that into it."* Ecology, not tactics — no
  alarm framing, no sentinel framing, no warning-instrument flavor anywhere below. A
  creature may be *noticed*; it is never built or described as a warning product.
- **Name register (ruled, mixed):** English compounds lead (thunderstep, yanker,
  fuzzrunner, thornhold), coined names mixed in as the owner admitted them (shokka,
  zellik, surrik, tikkit, vissler).
- **Art register (the Leaning Scrub house style for every job below):** a knee-high
  scrubland under a low, fog-softened sun that never rises or sets — the last ten minutes
  of a sunset that never ends; silver-green fuzz banding grey darkward and waxy gold
  sunward; everything leans one way. Realistic painted natural-history illustration,
  grounded believable anatomy, matte surface texture, never cartoonish, never cute, no
  outlines, alien but biologically plausible. Faced jobs: north is a **true rear view from
  directly behind — no eyes, no face, no frontal features.**
- 🔴 **Palette diversity is LAW on this cast** — owner, verbatim, carried in every
  style_notes: *"Your color palette is too uniform per biome. Needs more variety."*
  Each subject below carries its OWN palette anchor, deliberately distinct from its
  castmates; the silver-green room is where they stand, not the paint they wear.
- **Hard bans from the frozen sheet ride every prompt:** no rain and nothing rain-slicked;
  no dense flora except venomvine (the quincunx law); flora reads fire-resistant, never
  dry-tinder; the size ladder holds (small / medium ≤1.4 / large VOID / huge).
- **One home.** Every fill and menagerie member is Leaning Scrub-only (owner law
  2026-09-21).
- **Numbers are design proposals** — FOUNDRY calibrates in the build tickets; the
  relationships (who hunts what, which floor, what the wind changes) are the ruled part.

## 1. Name sweep (MEASURED this pass, 2026-09-29)

All cast names were swept clean 2026-09-28 at the sitting (probe korrum 70) — not
re-litigated. Re-swept here: only ids coined by THIS pass. Instrument:
`git grep -il <name> -- src/ design/ infrastructure/state/`. **Sanity probe: `korrum` →
72 files** (instrument proven able to see).

| name | files | verdict |
|---|---|---|
| `VisslerArm` | 0 | CLEAR — coined this pass (the shed-arm lure item) |
| `DrippingVenomvine` / `HollowVenomvine` / `CrownVenomvine` | 1 each | CLEAR — the hit is the ruling ticket itself |
| `TwitcherVenomvine` | 2 | CLEAR — ticket + mechanics ticket |
| `Fuzzrunner` / `Thornhold` / `Zellik` | 3 each · `Shokka` 2 | CLEAR — this sitting's own commissioning prose only |

## 2. Art dedup (standing owner law — searched before queuing anything)

Instrument: filename census over `infrastructure/artpipe/` `done/` + `pending/` +
`active/` + `failed/` + `_artsrc/`, content search of `registry.jsonl` and all
`Transient/*.decisions.json`. **Sanity probes: `korrum` → 6 in done/, 2 decision hits;
`imperialtoad` → 6 in done/, 21 registry hits; `fuzz` → 2 in done/, 19 registry hits**
(the instrument sees).

- **Empty everywhere — genuinely owed, queued below:** all 4 fills, all 9 menagerie (+
  the vissler arm item), all 4 fuzz flora, all 4 venomvine forms, the fresh thicket base
  (§6's verdict), thunderstep/shrublandgiant, yanker/tunnelsnake/klorslug, scrapnestbird,
  blurrg. Every one: 0 in done/, 0 in _artsrc/, 0 registry lines, 0 decisions.
- **Found and NOT queued (wire or nothing owed):** `rutfuzz_v1`, `rut_grellbush`,
  `rut_grellspine`, `rut_wildhealroot` (each: full set in done/ + _artsrc/, ~19 registry
  lines) — the review's wire-only five; plus **35 of the 39 donor-reskin cast members
  already own finished regens** (§7's table — e.g. `desert_swaca_bantha`,
  `canon_whisperbird_v1`, gizka 28 done-files, mossbeetle 18). Re-queuing any of those
  would throw finished, ruled work away.
- **`fambaa_v1` exists (3 facings, done) but is NOT thunderstep cover:** its own prompt
  says *"Star Wars canon Fambaa, the Gungan war beast"* (`CREATURE_ART_REVIEW_SHEET_1`) —
  canon Fambaa art, not our invented giant. Thunderstep still queues.
- **`rmvenomvine_v1` exists and FAILS the showpiece bar for this biome** — verdict and
  evidence in §6.

## 3. Cast entries — the four fills (grounded sprites only)

### RM_Fuzzrunner — the runway nation's staple

**Ruled frame (fixed):** small (~0.2 band), the prey base of the whole interface — a
fog-fat tunnel-hare that never stands in open light; worn runs under the canopy; freezes
when the wind dies. The free tier's first animal.

**Description (in the biome's voice):**

> Nothing on the plain is more common and nothing is harder to see. A fuzzrunner is born,
> fed, bred and dead without once standing in open light — its whole nation lives in the
> worn runs under the canopy, navigated by smell and whisker, walls of stems polished by
> ten thousand shoulders before it. It is round with fog-fat against the lean days, and
> when the wind falters it stops mid-stride and becomes a stone until the canopy moves
> again. Dig where the runs cross and you can live here. The locals do.

**Silhouette/palette brief:** a plump, low-slung tunnel-hare — big hindquarters for the
sprint, small tucked ears (a corridor animal, nothing tall), whiskered blunt muzzle,
mid-lope posture low to the ground. **Palette anchor: FOG-SILVER** — pale silver-buff coat
with a damp grey underside and darker spine-line, the one animal painted the canopy's own
silver so the read is "the fuzz moved". Not cute; workmanlike, watchful.

**Facings:** south, east, north (north = true rear: haunches and spine-line, no face).
Canvas 256. **drawSize intent: ~0.8**, bodySize ~0.2; herbivore, herd-common (the
biome's staple prey), tameable.

### RM_Thornhold — the venom nester that forbids

**Ruled frame (fixed):** small (~0.4 band), venom-armed; forbids rather than flees —
incarnates the frozen sheet's own "thornhold nesters", denning inside venomvine where
nothing big can follow.

**Description:**

> Most small things on the plain answer trouble by running. The thornhold answers it by
> refusing. It dens in the venomvine stands, threading galleries nothing larger can
> follow, and it meets whatever reaches in with a lash of venomed quills and no
> negotiation. A thornhold does not flee its nest, ever — trappers say you can dig one
> out with a shovel and it will still be facing you when you get there. Handled young,
> they extend the same stubbornness to a homestead's walls.

**Silhouette/palette brief:** a compact, armored nester — broad low body behind a blunt
braced head, a mantle of erectile quill-thorns half-raised along back and flanks, short
planted legs (built to hold ground, not cover it). **Palette anchor: BONE-AND-VENOM** —
pale bone-tan plating and quills tipped dark dried-blood umber, echoing the venomvine it
dens in; a dark eye-stripe the only face marking. Reads stubborn, not fierce.

**Facings:** south, east, north (north = true rear: the raised quill-mantle from behind,
no face). Canvas 256. **drawSize intent: ~1.0**, bodySize ~0.4; venomous melee, dens in
thickets, tameable late.

### RM_Shokka — the crossing pouncer

**Ruled frame (fixed):** medium 1.2 — the edge-pouncer of the fog-shadow barrens, the
first of the sheet's three predation routes ("ambush where a runway is forced to
surface") finally incarnated. Pelt is the local camouflage weave.

**Description:**

> Every runway has to surface somewhere — a fog-shadow behind a shrub, a farm's pale
> wake, ground too dry to grow cover — and the shokka owns those crossings the way a
> ferryman owns a river. It lies flat in the last of the fuzz with its dappled pelt
> matching the barrens beyond, and it does nothing at all, sometimes for a day, until
> something small commits to the open. Locals butcher one warily and waste nothing: the
> pelt takes dye badly and light beautifully, and a coat of it is the closest a person
> gets to being hard to see out here.

**Silhouette/palette brief:** a long, low ambush cat-analog held flat in a pounce-crouch —
shoulders below hip line, big forepaws, a wide flat skull with low-set eyes, tail a
counterweight held straight back. **Palette anchor: BARRENS-DAPPLE** — pale dust-gold
ground with broken waxy-buff dappling and a chalk-pale belly: the palette of the dead
wake, not the living fuzz; deliberately the warm pole of a cast painted mostly cool.

**Facings:** south, east, north (north = true rear: flattened shoulders, straight tail,
no face). Canvas 256. **drawSize intent: ~1.7**, bodySize ~1.2 (medium ceiling law: <1.5);
ambush predator, rare-ish.

### RM_Zellik — the stall-hawk (TRUE FLYER, grounded sprite only)

**Ruled frame (fixed):** medium 0.9, REAL 1.6 flight (`MaxFlightTime` stats, Locust
shape). It hunts by reading the canopy: useless in wind, lethal when the wind dies and
every movement under the fuzz shakes a still roof. 🔴 **Flight flip-book frames are NOT
commissioned now** — the flyer law says never block flight on frames; a frameless flyer
flies with no wing-beat, correct behaviour, plainer look. Frames are a named follow-on
(§10).

**Description:**

> On an ordinary day the zellik sits hunched on a sweetline bough or a turbine head and
> looks like a folded umbrella nobody wants. The wind that feeds everything else starves
> it: a shivering canopy tells it nothing. Then a cyclone far over the horizon swallows
> the Hadley flow, the wind dies, the plain goes still — and the zellik goes up. Over a
> stalled canopy every footfall underneath is a ring on a pond, and it drops through the
> roof onto things that believed, until that hour, that the roof was theirs.

**Silhouette/palette brief (grounded):** a tall, hunched wind-hunter at rest — long wings
folded and drooped past the tail like a closed umbrella, a lean keeled body on strong
tarsi, a flat wide-eyed face built for reading texture at distance, posture patient and
slightly wrong. **Palette anchor: SLATE-AND-GLARE** — dark storm-slate mantle over a pale
fog-white underside (invisible from below against the bright haze), one waxy-gold ring
around each eye as the sole hot accent. The cast's cold pole.

**Facings:** south, east, north (north = true rear: the folded wing-drape from behind, no
face). Canvas 256. **drawSize intent: ~1.6 grounded** (the folded wings carry the size),
bodySize ~0.9; predator band, rises with the Stall (mechanics own the wiring).

## The nine menagerie
PENDING

## The four fuzz flora
PENDING

## The venomvine showpiece
PENDING

## The regen-all list (ownership regens)
PENDING

## Blurrg
PENDING

## Wire-only (no jobs queued)
PENDING

## Queue manifest
PENDING

## Handoff notes
PENDING
