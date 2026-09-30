<!-- status: cast bible — commissioned under LONGSHADE_BEDAZZLE_SITTING_1 movement 4 -->
# Long Shade — bedazzle cast bible (movement 4: commission)

**Item:** `LONGSHADE_BEDAZZLE_SITTING_1` · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1 (row 8)
**Date:** 2026-09-29 · **Author:** movement-4 commission agent
**Feeds:** `LONGSHADE_BEDAZZLE_CONTENT_1` (defs + wiring) · `LONGSHADE_BEDAZZLE_MECHANICS_1`
(mirrak, swimmer kill signs, Crawler Road) · `SHADE_GEAR_FAMILY_1` (parasol, shade tent, sun shield)
**Authorities:** `longshade_bedazzle_review_2026-09-29.md` ("Art status per cast member",
"Proposed fills", "Art already generated"), `longshade_shade_ideation_2026-09-29.md` §3.2, §6
and "Rulings — volley turn 4", the three items above, and the frozen sheet `desert.md` (voice
and hard bans only; never edited). Mod: `src/RimMandrake/LongShade/`.
**Art list:** `infrastructure/artpipe/art_lists/longshade_bedazzle_cast.csv`. Its `prompt` and
`style_notes` cells are the exact text each job carries. This bible gives the intent behind them.

## 0. Shared law. Every entry obeys this without restating it

- **The light (§3.2, owner: *"A perpetual beautiful sunset."*).** The sun is pinned on the
  horizon: apricot at the horizon, rose overhead, and it never moves. Lit faces are warm amber,
  ochre and rust, and every shadow is a long, cool violet-blue. That warm/cool split across
  every object is the biome's signature (`desert.md` §9). Every sprite is lit with a warm
  apricot key from the front-top and cool violet in its own undersides and recesses.
- 🔴 **No baked cast shadow.** The engine draws the long parallel shadows from the pinned
  vector (§3.1, `OverrideShadowVector`). A shadow painted into a sprite would point the wrong
  way on half the maps. The mirrak is the one subject that *is* a shadow, and its shadow look
  is its body, never a cast shadow.
- 🔴 **Palette diversity is law.** Owner, verbatim, carried in every `style_notes`: *"Your
  color palette is too uniform per biome. Needs more variety."* Each subject has its own anchor
  (§4 table), and no two anchors are the same.
- **Hard bans from `desert.md` §6 apply to every prompt:** no night and nothing
  dusk-triggered; no rain and nothing rain-slicked (dew is fine); no pursuit predators, so
  every predator is drawn as an ambusher or a lunger, never a runner; no lush (the only greens
  are pale and sparse: the dew line and the ultracactus); and the recognizability rule (familiar
  body architecture, never a nameable Earth animal).
- **House style:** realistic painted natural-history illustration, matte, no outlines, never
  cute. On faced jobs, north is a **true rear view with no face**. Facings derive from the
  accepted east master (`fill_queue.py` default, ARTPIPE_FACING_COHERENCE_1).
- **Stuffable gear is painted in neutral values.** The parasol canopy, the tent canopy and the
  sun-shield panel are pale warm grey-cream with value shading only, so the stuff they are made
  from tints them. Mirrak hide is the best shade cloth and must be able to turn them near-black.
- **Tier (Q11a).** Invented names are `RM_`. The two Crawler Road hulks that are canon Star Wars
  vehicles (the repulsor skiff and the sandcrawler tread) are `RSW_`.

## 1. Art dedup sweep (MEASURED 2026-09-29, before anything was queued)

Instrument: one python sweep over `infrastructure/artpipe/{done,_artsrc,pending,active,failed,_withdrawn}`
filenames (4,199 / 2,104 / 0 / 0 / 104 / 40 files), `registry.jsonl`, and all 22
`Transient/**/*.decisions.json`. Every subject was searched by its current name AND its old
or drafted names. A second sweep read the PNG paths of every `src/*/*/Textures` tree (7,190 PNGs).

**Sanity probes: the instrument can find things.** `whisperbird` has 42 registry lines, 18 in
`done/` and 2 decisions files. (The brief said 78 registry lines. The measured count this pass
is 42. It is nonzero either way, which is all the probe has to show.) `sollak` has 36 registry
lines and 12 in `done/`. `qorrax` has 24 and 6. `staggerseed` has 4 in `done/`. `korrum` has 6
in `done/` and is visible in `SWBestiary/Textures`.

| subject | spellings searched | result |
|---|---|---|
| mirrak | mirrak | 0 everywhere, so **queued** |
| gloomcast | gloomcast, shadewhale, shade_whale | 0. Its `Textures/swanimals/Gloomcast/` is a copied Horax, so **queued** |
| great devourer | greatdevourer, great_devourer, hakkro | 0 (texPath is `AA_GreatDevourer`, a donor), so **queued** |
| groundrunner | groundrunner, dobbak | 0 (donor `AA_GroundRunner`), so **queued** |
| mature fleshbeast | fleshbeast, vukkoroth | 0 (donor `AA_MatureFleshbeast`), so **queued** |
| truffle mole | trufflemole, truffle_mole, pikkut | 0 in artpipe. The only PNG is the BMT donor copy in SWBestiary, so **queued** |
| dewfringe sprig | sprig, dewfringe | Only the plant has art (`RM_Dewfringe`, 2 in done, KEEP). The sprig has none, so **queued** |
| parasol / shade tent / sun shield | parasol, parisol, umbrella, shadetent, shade_tent, tent, sunshield, sun_shield, awning | 0 in artpipe. The `tent`/`shield` hits in Textures are tentacles, terminals and armoury items, so **queued** |
| wrecked landspeeder | speeder, landspeeder, wreck | **EXISTS**: `src/RimStarWars/StarWarsPatches/Textures/Things/Building/Ruins/WreckedLandspeeder.png` (512×256, re-textures vanilla `AncientPodCar` via `PodCarIsLandspeeder.xml`). **Skipped** |
| dead sandcrawler | crawler, sandcrawler, DeadCrawler | **EXISTS as a structure**: the `RSW_DeadCrawler` tile mutator and `RSW_GenStep_DeadCrawler`, which lays `Templates/dead_crawler.txt` (25×9) out of `CrustySandcrawlerHull` walls (`src/RimStarWars/Armoury/Textures/Buildings/Walls/`). **Skipped**. The build gives it a tall `staticSunShadowHeight` |
| other wreck/hulk art | wreck, hulk, skiff | Only the `scald*_wreck{hull,tank,frame}` sea wrecks (Scald shipping hulks, a different biome's register), `sporehulk` (a creature) and WreckedMachines' smelter. Desert vehicle hulks: 0, so the skiff, tread and cart are **queued** |
| Inhabited / AshkarrInhabited / DesertVehicleReskin | (whole mod trees, deployed copies) | Inhabited has 0 PNGs and AshkarrInhabited has 0 PNGs (both are XML only: cast rosters, settlement manifests, security profiles). DesertVehicleReskin has 30 PNGs: **live** Tier-0 draught vehicles (Chariot, CoveredCarriage, DogSled, OxCart, WarChariot, each s/e/n + masks). None of them is wrecked. The cart hulk is queued as its own wreck, not a retint of `AV_OxCart` |
| kill signs | drag, dragmark, smear, disturbed, filth, remains, sarlacc, swimmer | 0 relevant. The `drag` hits are all krayt *dragon*/dragonsnake art, and the only `sarlacc` PNG is a world-map landmark, so **queued** |
| skarrok · vrekka · sippra · tazzok | plus the review's alternates hollik · brokka · lorrik · mullok | 0 everywhere, so **queued (review-gated)** |
| maidenbloom · shadespire · pavecrust | plus middenbloom · torrak | 0 everywhere, so **queued (review-gated)** |

`fill_queue.py --dry-run` also checked every id against the existing job stores: 47 would be
filed, 0 refused as duplicates, 0 row errors.

## 2. Cast entries

### 2A. The mirrak: the shadow that points the wrong way (mechanics, `LONGSHADE_BEDAZZLE_MECHANICS_1` §2)

`RM_Mirrak` · 256 · s/e/n · bs ~1.0, drawSize ~2.0 · anchor **FALSE-SHADOW**.
A wafer-thin oblong ambusher pressed flat to the open ground. It has short limbs folded under
a wide, soft-edged mantle-skirt and a flat wedge head with a slit mouth the full width of the
skull. From above, its back reads as the shadow a boulder would throw, except there is no boulder.
The back is matte, light-swallowing ink-violet, exactly the biome's shadow colour, and its edges
are feathered. The dusty ochre underside shows only as a thin rim. It must **not** read as a lit
object: it is the one subject painted as shade itself. The sprite rotates with the animal, not
the sun. That mismatch is how a player learns to spot it (§6.2), and the smoke haze gives it
away when every real shadow lengthens and this one does not. Its hide is the deepest shade cloth
in `SHADE_GEAR_FAMILY_1`. Its rear view shows the flat back, the skirt edge and a short flat tail.

### 2B. Owned creatures that still wear someone else's face (`LONGSHADE_BEDAZZLE_CONTENT_1` §5–6)

**`RM_Gloomcast`: the colossus gets its own face.** 1024 · s/e/n · bs 16, drawSize 8.8, so
1024 is at the drawSize×128 ceiling and within it. Anchor **HEAT-SOAKED DUSK**. It is a
hill-sized grazer with a vast high-domed back like a wind-carved mesa, the only moving shadow
in the desert. It walks on four column legs, with a low slung head and a wide flat lip-scoop
that sieves sand. Heavy hide folds hang from its flanks like awnings. The saddle across the
back is sun-bleached apricot and rust, deepening to maroon at the shoulders and a cool
slate-violet on the flanks and belly: the giant painted as a piece of the sky. **Not a
Horax**: no tusks and no horn crown, because it replaces a copied Horax sprite. No riders are
drawn on it, because the pirrik are their own def.

**`RM_GreatDevourer`: the gorger.** 512 · s/e/n · bs 2.5, drawSize 3.5. Anchor **BONE-PLATE
AND BRUISE**. It is a heavy armoured worm in overlapping dusty plates, with a ring-mouth
fringed in rasping teeth and soft pale joints where it dies easily (the description's "not very
resilient"). The plates are pale bone-cream, edged in bruise-purple, with raw pink at the joints.
It gorges on small things and never runs anything down.

**`RM_Groundrunner`: the prospector's digger.** 256 · s/e/n · bs 2, drawSize 2.5. Anchor
**IRON-OXIDE**. It is a bear-and-mole chimera, hunched, with spade fore-claws, heavy shoulders
and a long bare snout. It stands square and calm, because it is docile and tameable. Its fur is
rust-red, with a grey rock-dust mantle and horn-yellow claws.

**`RM_MatureFleshbeast`: the lunger.** 512 · s/e/n · bs 6, drawSize 6. Anchor **SUN-CURED
TERRACOTTA**. It is a massive assembled-looking quadruped of layered muscle-folds under
scar-seamed hide, with a lopsided head, a few uneven eyes and a too-wide jaw. It crouches to
lunge from shade (ban 3). The hide is dry, cracked terracotta splitting over livid rose seams,
matte with no wet sheen. It must not look like the Anomaly fleshbeast.

**`RM_TruffleMole`: the shade-root forager.** 256 · s/e/n · bs 0.9, drawSize 1.6. Anchor
**VELVET PLUM**. A stout low digger with a big fleshy many-lobed scenting nose, tiny eyes and
spade forefeet, drawn snout-down mid-sniff. Its coat is dusk plum-grey velvet and its nose is
pale rose. (Its description is still donor text, which is a def-pass note, §5.)

**`RM_DewfringeSprig`: the dew line's harvest.** 256 · single · item icon. Anchor
**DEW-SILVER**. A loose handful of hair-fine pale silver-green filaments, twisted at the base
and beaded with clear dew that catches apricot highlights. Pale and sparse, because it is the
dew line's only green.

### 2C. Shade gear (`SHADE_GEAR_FAMILY_1`, cross-biome)

The owner's words: *"Parisols, shade tents, simple shields you can stand behind."* All three
are stuffable, so their cloth and hide parts are painted in neutral values (§0).

- **`RM_Parasol`** (256, item icon) and **`RM_ParasolWorn`** (256, s/e/n, overhead worn
  layer). A broad shallow canopy on thin ribs, a long pole and a wrapped grip. The canopy is pale
  warm grey-cream for stuff tint, and the pole is dark oiled wood. The worn set is the parasol
  alone, with no person, sized to sit over a standing colonist. South shows the underside, east
  shows the profile, and north shows the canopy's top. It is drawn worn because the shade has to
  be *seen* on the colonist. If the def pass picks a different apparel layer, the icon still stands.
- **`RM_ShadeTent`** (512, single, about 3×3). A low open-sided awning on four slim poles with
  guy-ropes pegged into the sand and a slight sag. It is the tool for the Long Carry (§6.5),
  and the moving rectangle of violet shade the ideation describes.
- **`RM_SunShield`** (256, s/e/n, about 2 cells, rotatable). A tall panel of stretched hide on
  a lashed frame, braced by two splayed legs behind it. It is the one piece that works under a
  low sun. South is the face, east is edge-on with the braces, and north is the back with both
  braces toward the viewer.

### 2D. The Crawler Road: only the missing links (`LONGSHADE_BEDAZZLE_MECHANICS_1` §4)

The road is a dotted chain of dead machines, each one human dash apart, ending at the dead
sandcrawler (§6.4). The landspeeder and the crawler already exist (§1), so only three links
are queued:

- **`RSW_WreckedSkiff`** (512×256, about 4×2, anchor **BLEACHED GUNMETAL**). A repulsor
  cargo skiff lying tilted, with one deck rail torn off, dead pods and a snapped steering post.
  Its khaki paint flakes off grey gunmetal. It is a canon vehicle, so it is RSW tier.
- **`RSW_CrawlerTreadWreck`** (512×256, about 4×2, anchor **DEEP RUST**). A detached
  sandcrawler tread section lying on its side, with missing plates and exposed drive wheels. It
  is a canon vehicle part, so it is RSW tier. It is the "length of crawler tread" in §6.4.
- **`RM_WreckedCart`** (256, about 2×2, anchor **DRIFTWOOD**). A draught cart with a broken
  axle, a wheel lying flat, split grey planks and a faded hide scrap. It is its own wreck, not a
  retint of DesertVehicleReskin's live `AV_OxCart`.

These three are also minifiable salvage: when the player hauls one into a gap, the road is
re-linked (§6.4). The build sets `staticSunShadowHeight` on each one.

### 2E. Kill signs: nothing vanishes without a trace (`LONGSHADE_BEDAZZLE_MECHANICS_1` §3)

The owner: *"we can't have animals "disappear spontaneously." There needs to be SOME kind of
indication of what happened to them."*

- **`RM_Filth_DragMark`** (256, top-down decal, Graphic_Random master, anchor **CHURNED
  OCHRE**). A smeared trough with furrow edges, scuffed prints and a thin dried rust-brown
  smear. It marks where something was hauled away. It serves the mirrak, which pulls its prey
  under its mantle and drags it, and it can also serve any taker.
- **`RM_Filth_DisturbedSand`** (256, top-down decal, anchor **SUNK SAND**). A shallow collapsed
  funnel ringed with slumped, cracked crust, fed by a low wake-furrow that ends at the funnel. It
  is the young sarlacc swimmer's take, "a wake that ends" drawn literally.

A letter/message on each take is still owed as code in the build. The decals are only the
visible half.

### 2F. REVIEW-GATED fills: art first, owner sheet next, defs only for what he keeps

These were **never ruled** (`LONGSHADE_BEDAZZLE_CONTENT_1` §8, the 09-27 filler precedent).
Their jobs run at priority 60, so the owed renders above (priority 70) land first. **No def is
built until the owner rules on a review sheet.**

| id | brief | anchor |
|---|---|---|
| `RM_Skarrok` (s/e/n, bs ~0.9, ds 1.6) | Scarp-drop ambusher, **grounded sprite only**: narrow wings folded tight, a keeled chest, hooked feet and a wedge beak, hunched as if on a ledge. It is a true flyer, but the flight flip-book is a separate follow-on, per the flyer law | SOOTY BRONZE (a copper throat) |
| `RM_Vrekka` (s/e/n, bs ~0.5, ds 1.1) | Squat bone-crushing midden scavenger: blunt skull, oversized jaws, short thick legs and a bristled back. It follows corpses into the open | BONE MIDDEN (bone-white jaw plates, an umber mask) |
| `RM_Sippra` (s/e/n, bs ~0.25, ds 0.9) | Stilt-legged dew-drinker of the one-cell shade line: a fine muzzle and large ears, head down mid-sip | SAND CREAM (silver-green leg bands echo the dewfringe) |
| `RM_Tazzok` (s/e/n, bs ~0.3, ds 0.9) | Ash-keyed grain-grazer, drawn surfacing with sand spilling off an armoured back, with shovel forefeet | ASH GREY (an ember eye-ring) |
| `RM_Maidenbloom` (single, ds 1.0) | A fat low rosette on fertilised ground, with heavy pale blooms sunk in its heart. The owner's name: **maidenbloom**, not middenbloom | DUN AND RUST (a wine heart, apricot blooms, never green) |
| `RM_Shadespire` (512, single, ds 3.0) | The only vertical that grows: a 3–4 m ridged column succulent with pale wood showing at a split. It is a shade-caster and a landmark, with no saguaro read | PALE BONE COLUMN (a faint sage bloom, rust spines) |
| `RM_Pavecrust` (single, top-down, ds 1.0) | A thin lichen crust following the cracks of hardpan, with no height | GREY AMBER |

## 3. Wire-only and skipped. Never queued: the art exists

**Finished renders waiting on WIRING, which is FOUNDRY's job under `LONGSHADE_BEDAZZLE_CONTENT_1`
§1–4.** Counts are from the review, and the sweep in §1 re-saw `sollak`, `qorrax` and
`staggerseed`:
`rsw_sandstrider` → `RM_Ossik` · `rsw_spineroller` → `RM_Kudda` · `rsw_sandhorn` → `RM_Thurra` ·
`rsw_dunestalker` → `RM_Vosska` · `rsw_ferroclaw` + `aa_terramorph_v1` → `RM_Khorrak` (two jobs,
reconcile) · `rsw_sandmaw` → `RM_Ommok` · `rsw_tuskcoil` → `RM_Ulgga` · `rsw_stoneback` →
`RM_Bokka` · `desertportb_jellypot` → `RM_Jellypot` · `desertportb_landopus` → `JOE_Landopus` ·
`rutstaggerseed` + `rutstaggerseeddish` → the `RM_Vorrel` family · `RM_Qorrax` (6, KEEP) →
the `JOE_Cephalope` rename · the filler sets `RM_Sollak`/`_b`, `RM_Gennok`/`_b`,
`RM_Tebbra`/`_b`, `RM_Pirrik`/`_b`, `RM_Dakkra` (owner-ruled on the 09-27 sheet).

**Skipped, with art already in the game:** the wrecked landspeeder (`WreckedLandspeeder.png`)
and the dead sandcrawler (the `RSW_DeadCrawler` plan built from `CrustySandcrawlerHull` walls).
The Crawler Road build places them, and neither needs a job.

## 4. Queued art: 23 subjects (12 faced sets + 11 singles), 47 job files: FILED, 0 refused

**CSV:** `infrastructure/artpipe/art_lists/longshade_bedazzle_cast.csv`. Channel codex,
transparent, `reference` empty on every row (these are fresh designs, never reskins), with a
`drawsize` column. The `rimflow_item_id` is the item that will wire each one. Queued with
`fill_queue.py` using the derive-facings default. Jobs land in `infrastructure/artpipe/pending/`,
and the daemon claiming one counts as success. The filing result is in §5.

| group | id | canvas | facings | item | anchor |
|---|---|---|---|---|---|
| mirrak | `RM_Mirrak` | 256 | s,e,n | MECHANICS_1 | false-shadow ink-violet |
| owed | `RM_Gloomcast` | 1024 | s,e,n | CONTENT_1 | heat-soaked dusk |
| owed | `RM_GreatDevourer` | 512 | s,e,n | CONTENT_1 | bone-plate and bruise |
| owed | `RM_Groundrunner` | 256 | s,e,n | CONTENT_1 | iron-oxide |
| owed | `RM_MatureFleshbeast` | 512 | s,e,n | CONTENT_1 | sun-cured terracotta |
| owed | `RM_TruffleMole` | 256 | s,e,n | CONTENT_1 | velvet plum |
| owed | `RM_DewfringeSprig` | 256 | single | CONTENT_1 | dew-silver |
| gear | `RM_Parasol` | 256 | single | SHADE_GEAR | neutral cloth |
| gear | `RM_ParasolWorn` | 256 | s,e,n | SHADE_GEAR | neutral cloth |
| gear | `RM_ShadeTent` | 512 | single | SHADE_GEAR | neutral cloth |
| gear | `RM_SunShield` | 256 | s,e,n | SHADE_GEAR | neutral hide |
| road | `RSW_WreckedSkiff` | 512×256 | single | MECHANICS_1 | bleached gunmetal |
| road | `RSW_CrawlerTreadWreck` | 512×256 | single | MECHANICS_1 | deep rust |
| road | `RM_WreckedCart` | 256 | single | MECHANICS_1 | driftwood |
| signs | `RM_Filth_DragMark` | 256 | single | MECHANICS_1 | churned ochre |
| signs | `RM_Filth_DisturbedSand` | 256 | single | MECHANICS_1 | sunk sand |
| gated | `RM_Skarrok` | 256 | s,e,n | CONTENT_1 | sooty bronze |
| gated | `RM_Vrekka` | 256 | s,e,n | CONTENT_1 | bone midden |
| gated | `RM_Sippra` | 256 | s,e,n | CONTENT_1 | sand cream |
| gated | `RM_Tazzok` | 256 | s,e,n | CONTENT_1 | ash grey |
| gated | `RM_Maidenbloom` | 256 | single | CONTENT_1 | dun and rust |
| gated | `RM_Shadespire` | 512 | single | CONTENT_1 | pale bone column |
| gated | `RM_Pavecrust` | 256 | single | CONTENT_1 | grey amber |

## 5. Handoff notes (observed; nothing filed)

- **Filing result:** `fill_queue.py` reported 47 jobs filed, 0 duplicates refused and 0 row errors. The pending/ `*.json` glob then counted 46 of ours in `pending/` plus 1 already claimed into `active/` by the daemon: 47 of 47.
- `RM_TruffleMole`, `RM_GreatDevourer`, `RM_Groundrunner` and `RM_MatureFleshbeast` still carry
  donor description text (the "truffle pigs of Earth", Alpha Animals lore). The new art is drawn
  as our own animals, so the def pass should rewrite the descriptions to match.
- The gloomcast render is 1024. If the legibility checker or the owner prefers the 512 that
  sollak got, re-file at 512. The 1024 is within the drawSize×128 rule for ds 8.8.
- The parasol's worn set assumes an overhead-style layer with no body-type variants. If the
  def pass chooses otherwise, the worn set is re-cut from the accepted east master.
- The review-gated seven need a review sheet (`review-sheets` skill) once their renders land.
  That is the gate before any def.
