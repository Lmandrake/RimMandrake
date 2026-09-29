<!-- status: cast bible — commissioned under FORGE_BEDAZZLE_SITTING_1 movement 4 -->
# The Forge — bedazzle cast bible (movement 4: commission)

**Item:** `FORGE_BEDAZZLE_SITTING_1` · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1 (row 6)
**Date:** 2026-09-29 · **Author:** movement-4 commission agent (Fable)
**Feeds:** `FORGE_RULED_CONTENT_1` (defs) + `FORGE_CYCLE_MECHANICS_1` (the grand cycle)
**Authorities:** `forge_bedazzle_review_2026-09-28.md` (the review; volley CLOSED),
both tickets above (every ruling below is fixed), the frozen sheet `the_forge.md`
(voice only — never edited). Mod: `src/RimMandrake/TheForge/`.

## 0. Shared law — every card obeys this without restating it

- **Voice:** the Forge is the only unstolen fire — native heat that owes nothing to
  the sun. Dark towers against the glare, herds grazing the smoke, the closed rain
  that boils, falls, and flashes. The quotas below are still being run for no one.
  Descriptions talk foundry: anvil, seam, slag, quench, quota.
- **Name accent** (Batch 5c, ruled): heat — a `j` or breathed `dh` at the front, a
  back vowel, a coda that closes like a vent: -ur/-osh/-ox. Register: jibbur,
  dhommur, jorrosh — now dhokkur, julmox, jossur, dhuvvox.
- **Art register (the Forge house style for every job below):** a volcanic massif
  under doubled furnace light — hard white sun above, seam-red from below; basalt
  black, ash grey, obsidian gloss, steam-white plumes, seam-red ONLY where the melt
  actually shows. Realistic painted natural-history illustration, grounded
  believable anatomy, matte mineral surface texture, never cartoonish, never cute,
  no outlines, alien but biologically plausible. Faced jobs: north is a **true rear
  view from directly behind — no eyes, no face, no frontal features.**
- 🔴 **Palette diversity is LAW on this cast** — owner, verbatim, carried in every
  style_notes: *"Your color palette is too uniform per biome. Needs more variety."*
  Each subject below is assigned its OWN palette anchor, deliberately distinct from
  its castmates; the register above is the room they stand in, not the paint they
  wear.
- **Hard bans from the frozen sheet ride every prompt:** nothing lives in the lava
  (no lava-native read); no furred, chilled or lush-register anatomy; no ordinary
  rain anywhere in a prompt.
- **One home.** All four natives are Forge-only (owner law 2026-09-21).
- **Numbers are design proposals** — FOUNDRY calibrates in the build tickets; the
  relationships (who is biggest, what is dormant when, what the freeze is worth)
  are the ruled part.

## 1. Name sweep (MEASURED this pass, 2026-09-29)

Instrument: `git grep -il <name> -- src/ design/ infrastructure/state/`.
**Sanity probe: `korrum` → 67 files** (instrument proven able to see).

| name | files | verdict |
|---|---|---|
| `dhokkur` | 5 | CLEAR — all 5 are this sitting's own commissioning prose (review doc, both tickets, BENCH ledger, queue render). No def, no other subject. |
| `julmox` | 4 | CLEAR — same set, review-pass sweep already paid |
| `jossur` | 4 | CLEAR — same set |
| `dhuvvox` | 4 | CLEAR — same set |
| `floatstone` | 4 | CLEAR — the owner's own turn-7 word; hits are the two tickets, BENCH ledger, queue render |
| `FloatstoneGarden` | 0 | CLEAR — coined this pass |
| `BasaltShingle` | 0 | CLEAR — coined this pass (terrain, FOUNDRY-owed) |
| `PumiceChunk` | 0 | CLEAR — coined this pass (terrain, FOUNDRY-owed) |
| `GlowingCrack` | 0 | CLEAR — coined this pass (terrain, FOUNDRY-owed) |

(All four creature names also passed the review pass's collision sweep +
`check_pseudo_sw_name.py`, per the review doc — not re-litigated here.)

## 2. Art dedup (standing owner law — searched before queuing anything)

Instrument: filename search over `infrastructure/artpipe/` `done/` + `pending/` +
`active/` + `failed/` + `_artsrc/`, content search of `registry.jsonl` and all
`Transient/*.decisions.json`. **Sanity probes: `suush` → 6 files in done/, 24
registry hits; `korrum` → 6 in done/, 2 decision hits** (the instrument sees).

- **Empty everywhere — genuinely owed, queued below:** dhokkur (both states),
  julmox, jossur, dhuvvox (both states), floatstone garden, floatstone item.
  Also swept empty: basalt / basaltshingle / pumice / glowingcrack (no terrain
  art exists to reuse — see §6).
- **Found and NOT queued:** `RM_FleetFlier` — **6 files in done/ + 3 in
  `_artsrc/`** (`rutfleetflier_v1` east/north/south). This is a WIRE for FOUNDRY
  (`FORGE_RULED_CONTENT_1` §1 "wire in all waiting"), never a queue. ⛔ Nothing in
  the review's art table may be re-queued; the three DEPLOY_HOLD debts
  (`RUT_TibannaGas`, `RUT_FoundryTowerEntrance`, `RUT_FoundrySalvageCache`) belong
  to that same wire-in ticket, not to this commission.

## 3. Cast entries — the four admitted natives

### RM_Dhokkur — the giant on the clock (two visual states)

**Ruled frame (fixed, `FORGE_RULED_CONTENT_1` §2):** GIANT. Obsidian-backed
rain-drinker; dormant through the still heat — reads as terrain — and unfurls to
walk and drink only during boiling rain. Neutral, immensely tough, slow; butchers
to heat-shielding hide. Dormancy behavior lives in `FORGE_CYCLE_MECHANICS_1`
(CanBeDormant precedent, keyed to the rain phase; path-memory kept light).

**Description (in the biome's voice):**

> Half the outcrops on the skirts are stone. The other half are waiting for rain.
> A dormant dhokkur sits out the still heat as a hill of banked obsidian plates,
> ash drifted into its seams, and the survey crews learn the difference the day
> the sky opens: the hill stands up. It walks its own path — the same path, worn
> a thousand bursts deep — drinking the scald straight off its back while
> everything else on the mountain runs for a roof. It is not angry. It has never
> needed to be. Its hide turns the boiling rain, and the boiling rain is the
> worst thing this mountain knows how to say.

**Two visual states, both commissioned:**

- **Walking form (3 facings):** a hill that walks — vast low body slung between
  four column limbs, back a shingled massif of obsidian plates channeled with
  rain-gutters running to a low drinking maw at the prow; head barely
  differentiated, more cistern than face. Unfurled plate-fans lifted along the
  spine to catch the fall. Mid-stride, ponderous, streaming.
- **Dormant form (single):** the same animal furled — limbs drawn under, plate-fans
  banked flat, silhouette settled into a weathered outcrop dome with ash in the
  seams. 🔑 The tell must be findable and quiet: the gutter-lines converge too
  regularly for stone. The tooltip lies; the sprite may only whisper.

**Silhouette/palette brief:** obsidian gloss over basalt dark — but this subject's
**palette anchor is RAIN-SLICK**: wet blue-grey sheen and mirror glints on black
glass, silver runnels of standing water in the gutters, cool steam-white breath —
the one cast member painted by the water, not the fire. No seam-red anywhere on
the body (nothing lives in the lava; it drinks rain, not melt). No eyes visible
at sprite scale; no fur, ever.

**Facings:** walking form south, east, north (north = true rear: the plated back
massif, banked fans from behind, rear column limbs). Dormant form single.
**Canvas 512 both states** — colossus precedent (Vhaulk/Muttavaq/Vexxiss): scale
must carry in the pixels. **drawSize intent: ~7.5 walking, ~6.5 dormant**;
bodySize ~6.0 class, slow, rare (0.02-class), neutral.

### RM_Julmox — the plate-footed pastoral spine

**Ruled frame (fixed):** the owned ground herd — sealed between bursts, grazes the
flash-window moss film; tamable, the standalone tier's pastoral spine.

**Description:**

> Low and wide as a cooling slab, on feet spread into plates that never sink into
> hot ash. Between rains the julmox squats sealed, lids down over every seam,
> a row of dull kettles on the skirts. Then the burst passes, the rock steams,
> the moss film blooms — and the herd fans open and goes to work, cropping the
> two hours the mountain allows. The Farmers keep them for the same reason the
> mountain does: they are patient, they are sealed against the worst of it, and
> they turn stone-film into meat. Pasture is wherever it last rained.

**Silhouette/palette brief:** broad flat-backed grazer, wide plate-feet the
signature (oversized, splayed, heat-proof soles), a fringed grazing muzzle held
low; sealing lids visible as seam-lines along flank and face, caught HALF-FANNED —
plates lifted, fringe out — so the sprite reads as the grazing hour, not the wait.
**Palette anchor: ASH-AND-BLOOM** — pale kiln-grey and bone body wearing the flash
window's paint: fresh moss-green staining on muzzle, feet and belly, a faint
steam-damp darkening low. The one cast member allowed real green — it is wearing
its food. No fur; the covering reads as fine mineral plating.

**Facings:** south, east, north (north = true rear: sealed back seams, rear
plate-feet, no face). Canvas 256. **drawSize intent: ~1.8**, bodySize ~1.2 class;
herd animal, tamable, 0.4-class commonality — the standalone tier's texture.
*(The fully-sealed squat is a def/state question: if FOUNDRY wires a dormant
graphic to the cycle phase, file the sealed-form single as a follow-on job —
dressing on the mechanic, not part of this commission.)*

### RM_Jossur — the sky apex, grounded sprite

**Ruled frame (fixed):** sky apex column-rider; REAL 1.6 flight (`MaxFlightTime`
stat, Locust shape). 🔴 **Flight flip-book frames are NOT commissioned now** — the
flyer law says never block flight on frames; a frameless flyer flies with no
wing-beat, correct behaviour, plainer look. Frames are a named follow-on (§7).

**Description:**

> The columns are pasture, and every pasture gets its wolf. The jossur rides the
> vent updrafts on wings longer than the rest of it put together, hanging in the
> shimmer where the fleet fliers race and the young fumeriders drift — and then
> it stops hanging. Grounded, it is an awkward folded thing, all wing-knuckle
> and stilt, mantling over its kill in the ash. Airborne, it is the reason the
> herds keep their young in the middle of the smoke.

**Silhouette/palette brief (grounded):** a long-winged stooper at rest — wings
folded high and crossed over the back like furled banners, wing-knuckles standing
above the shoulder line, body lean and keeled, stilt legs, a hooked heat-shielded
head held low and level. The grounded read is "folded weapon", not "walking bird".
**Palette anchor: SCOUR-RUST** — wind-burnished rust-red and hot umber over dark
primaries, pale scald-scarring on the leading edges, beldon-amber eyeshine as the
one hot accent. No lush plumage register; the covering reads as scoured vane and
plate, heat-adapted and few.

**Facings:** south, east, north (north = true rear: folded wing-backs and tail
vanes, no face). Canvas 256. **drawSize intent: ~2.6 grounded** (the folded wings
carry the size), bodySize ~1.6 class; rare apex (0.06-class), predator band.

### RM_Dhuvvox — the flash-swarm (two visual states)

**Ruled frame (fixed):** knuckle-sized skitterers existing as sealed ash nodules
until the rain hits, erupting by the hundred for the two-hour window; despawn /
reseal on window end. The living clock the player learns to read.

**Description:**

> Kick through the ash between rains and you will turn up little glazed nodules,
> heavy for their size, and think them slag. Then the rain comes down boiling,
> and the slag hatches. For two hours the skirts run with dhuvvox — a floor of
> quick glitter stripping the wet rock of everything the flash woke — and when
> the stone dries they seal where they stand and are slag again. The old hands
> tell time by them. When the dhuvvox run, you reap; when they still, you are
> already late for shelter.

**Two visual states, both commissioned:**

- **Skitterer (3 facings):** a knuckle-sized many-legged glassback — domed
  wet-gloss carapace, legs a fringe of motion, short siphon head down against the
  rock. Posture mid-scuttle. At drawSize it must read as a bright fleck; the
  carapace highlight does that work.
- **Sealed nodule (single):** the same animal shut — a glazed teardrop nodule,
  leg-fringe seams just visible as a spiral, half-dusted with ash. Reads as slag
  until you know.

**Silhouette/palette brief:** **palette anchor: EMBER-FLECK** — charcoal-black body
with a hot ember-orange shine along the carapace dome (reflected seam-light, not
inner glow — nothing lives in the lava and nothing here reads volatile), legs pale
glass. The nodule state inverts it: matte ash-grey glaze, the ember tint only in
the seam-spiral. The swarm's brightness is what makes the clock legible from map
zoom.

**Facings:** skitterer south, east, north (north = rear dome and leg-fringe, no
head). Nodule single. Canvas 256 both. **drawSize intent: ~0.5 skitterer, ~0.4
nodule**; bodySize ~0.1, swarm-common inside the window (the mechanics own
spawn/despawn; `FORGE_CYCLE_MECHANICS_1` phase 5 clock).

## 4. Cast entries — the floatstone family

**Ruled frame (fixed, owner verbatim, turn 7 — this enrichment is LAW for the
art):** *"Ultra-light pumice made of what looks like spun glass whirled into
tangles. Super strong and light building material, not flammable, quite valuable,
and the walls it makes look like swirled stone spun sugar made into blocks. Very
beautiful."* Harvested from floatstone-garden growths during the freeze phase;
unharvested globes tear free and drift off-map ahead of the melt
(`FORGE_CYCLE_MECHANICS_1` phase 5).

### RM_FloatstoneGarden — the growth (lace-walled globe)

**Description:**

> When the melt freezes over and the plumes stand tall, the crust blooms. A
> floatstone garden starts as a knot of glass threads and whirls itself outward
> into a lace-walled globe, chamber over chamber, light enough that a grown one
> strains at its own root. Caught ripe, it is the most beautiful quarry on the
> planet. Left standing, it tears free ahead of the melt and drifts away over
> the seams — the one form the lava never gets back.

**Silhouette/palette brief:** a globe of whirled glass lace on a short mineral
root-boss — visible spun-thread structure, wound in swirls like sugar-work,
chambered and translucent-edged, a few threads trailing loose at the crown (the
tear-free foreshadowed). **Palette anchor: OPAL-LACE** — pale spun-glass whites
and warm pearl, faint opal iridescence in the whirls, root-boss basalt-dark for
contrast; steam-white ambience, zero seam-red on the growth itself. The read is
"very beautiful" first — the cast's one pure grace note, standing on the
deadliest ground.

**Facings:** single (growth; Graphic_Random variants derive from the master).
Canvas 256. **drawSize/visualSize intent: ~1.4 cells.** *(Ripening states: ship
as derives/retints of this master — smaller tighter knot → full globe; dressing
on the cycle, not separate commissions.)*

### RM_Floatstone — the material (item + stuff color master)

**Description:**

> A block of floatstone weighs what a lie weighs. Spun glass whirled into
> tangles, frozen mid-swirl, strong the way a woven thing is strong — it will
> not burn, it barely presses on the hand that carries it, and a wall of it
> looks like swirled stone spun sugar cut into blocks. The Farmers sell it by
> the promise instead of the weight. Nobody has ever asked for the weight back.

**Silhouette/palette brief (item icon; the STUFF colour derives from it):** three
cut blocks stacked, each face showing the whirled spun-glass grain in swirls —
the "spun sugar made into blocks" read is the whole job; the cut faces must carry
visible whirl-lamination, never a flat pumice stipple. **Palette anchor:
OPAL-LACE** (shared with the garden — one family, one paint): pearl-white body,
warm cream swirl-bands, faint opal sheen at the corners. Reads light even as a
picture.

**Facings:** single. Canvas 256. Item + StuffProps ride `FORGE_RULED_CONTENT_1`
§3 (strong, very light, flammability 0, high market value).

### Floatstone walls — the stuff route (checked, no art commissioned)

**MEASURED against the repo's own custom stuffs:** owned stuff-capable materials
here (`RM_Lanternstone`, `src/RimMandrake/LanternDeeps/Defs/ThingDefs_Items/
RM_LanternstoneItems.xml`) ship `<stuffProps>` with a `<color>` + `<appearance>`
and **ride the vanilla wall/blocks atlases tinted by that color** — no owned wall
atlas art exists anywhere in `src/`. ⇒ **Floatstone walls take the same route:**
stuffProps color drawn from the item master (pearl-white, warm cream),
`appearance Smooth` for the glass read. The "swirled spun sugar" wall grain
cannot ride a vanilla tint alone — if the owner wants the swirl visible in the
built wall, that is a custom wall atlas, a real follow-on ask (§7), not assumed
here.

## 5. Cycle set pieces — terrain (FOUNDRY-owed, out of artpipe's lane)

**Route checked (MEASURED):** every owned TerrainDef in `src/` reuses a vanilla
`texturePath` (`RM_SeaFloorGround.xml` → `Terrain/Surfaces/Sand`,
`RUT_BoughSoil.xml` → `Terrain/Surfaces/SoilRich`, the DivingInteraction and
FeverWood families throughout) — terrain textures are hand-picked vanilla
surfaces with def-level `color` tints, and `registry.jsonl` holds **zero** real
terrain-texture jobs. ⇒ **Terrain art is not artpipe's lane here. Nothing queued;
the three set pieces below are FOUNDRY-owed on `FORGE_CYCLE_MECHANICS_1`:**

- **`RM_BasaltShingle`** (phase-4 temporary crust) — vanilla rough-stone family
  texturePath tinted basalt-dark with a cooled blue-grey cast; walkable, the
  treasure floor.
- **`RM_PumiceChunk`** (phase-4 companion crust) — vanilla gravel family
  texturePath tinted pale ash-buff; the lighter, rubblier read beside the
  shingle.
- **`RM_GlowingCrack`** (phase-6 warning terrain) — the one that may exceed a
  tint: vanilla texture with an emissive seam-red color pass if the engine's
  terrain `color`/glow fields carry it; if a custom texture proves genuinely
  needed, FOUNDRY files it then — not pre-queued on a guess.

## 6. Wired-by-FOUNDRY — exists already; NOT queued (⛔ standing law)

| subject | evidence | disposition |
|---|---|---|
| `RM_FleetFlier` | `rutfleetflier_v1` — 6 files in `done/`, 3 in `_artsrc/` | **WIRE** into the RM mod's Textures (`FORGE_RULED_CONTENT_1` §1); an art queue here would throw finished work away |
| `RSW_Beldon` | `canon_beldon_v1`, 3 facings, done | nothing owed |
| `RM_FireLavender` / `RM_HeatsinkFungus` | done + deployed in-mod | nothing owed |
| `RUT_TibannaGas` / `RUT_FoundryTowerEntrance` / `RUT_FoundrySalvageCache` | DEPLOY_HOLD "no art yet" | the review's found-unwired list; rides `FORGE_RULED_CONTENT_1` §1's wire-in, **not** this commission (their register is Utinni industry, a different sitting's judgement) |
| `RM_CinderCrust` | no art anywhere (review-confirmed) | Q13 identity regen owed — but that is `FORGE_RULED_CONTENT_1` roster work with an open identity question; queuing art before the identity is written would paint the wrong plant. Handoff note §8. |

## 7. Queued art — 6 subjects (8 sprite sets), 16 job files

**CSV:** `infrastructure/artpipe/art_lists/forge_bedazzle_cast.csv` —
`rimflow_item_id FORGE_BEDAZZLE_SITTING_1`, channel codex, transparent,
priority 70. Queued via `fill_queue.py` (derive-facings default: east is the
master, north/south derive — ARTPIPE_FACING_COHERENCE_1). Jobs in
`infrastructure/artpipe/pending/`; the daemon claiming one is success.

| id | canvas | facings | kind | palette anchor |
|---|---|---|---|---|
| `RM_Dhokkur` | **512** | south,east,north | creature GIANT, walking state | rain-slick obsidian |
| `RM_DhokkurDormant` | **512** | single | the same giant furled as an outcrop | rain-slick obsidian, ash-dusted |
| `RM_Julmox` | 256 | south,east,north | creature, herd | ash-and-bloom |
| `RM_Jossur` | 256 | south,east,north | creature, sky apex GROUNDED | scour-rust |
| `RM_Dhuvvox` | 256 | south,east,north | creature, flash-swarm | ember-fleck |
| `RM_DhuvvoxNodule` | 256 | single | sealed ash-nodule state | ash-glaze inverse |
| `RM_FloatstoneGarden` | 256 | single | growth (lace-walled globe) | opal-lace |
| `RM_Floatstone` | 256 | single | item + stuff color master | opal-lace |

**Named follow-ons (not commissioned now, deliberately):**
- `RM_Jossur` flight flip-book frames (whole-body directional flip-book,
  `flyingAnimationFramePathPrefix` shape, Sparrow template) — the flyer law says
  never block flight on frames; file after the grounded sprite is accepted.
- `RM_Julmox` sealed-squat single — only if FOUNDRY wires a dormant state graphic
  to the cycle phase.
- Floatstone custom wall atlas — only if the owner asks for the swirl grain in
  the built wall (§4's tint route ships first).
- Floatstone garden ripening variants — derives/retints of the master, dressing.

## 8. Handoff notes (defects/finds observed — nothing filed, per this brief)

- **`RM_CinderCrust` still has no art AND no ruled identity** — its texPath
  points at nothing (review-confirmed). The Q13 divergence ("regenerate the
  second copy's identity") must be written before its art is queued, or the art
  paints a plant nobody has designed. That identity is `FORGE_RULED_CONTENT_1`
  roster work; the art job should be filed the same sitting the identity lands.
- **Dhokkur dormant-state wiring has an exact in-repo precedent to read first:**
  the Cauldron commission's §7 note pattern applies — search `src/` before new
  C#; `CanBeDormant`/`WakeUpDormant` comps exist in the engine, and
  `RM_CompScriptedDieOff` (EnvironmentalHazards) shows the kit's comp shape.
- **The dormant dhokkur and the sealed dhuvvox nodule are STATE GRAPHICS** — two
  sprites per def, swapped by comp/mechanics state. If FOUNDRY defs them as
  separate ThingDefs instead (spawner-style), the job ids here still map 1:1;
  nothing about the art changes.
- **Terrain lane finding (§5) is worth keeping:** artpipe has never generated a
  terrain texture; every owned TerrainDef tints a vanilla surface. Anyone about
  to queue "terrain art" should read §5 before spending jobs.
- **Palette-diversity law is now carried verbatim in every style_notes** of this
  cast's CSV — five distinct anchors across six subjects (the floatstone pair
  deliberately shares one; they are one material family). If a rendered batch
  comes back tonally uniform anyway, that is a prompt-adherence defect to raise
  on the daemon channel, not a reason to re-rule the cast.
