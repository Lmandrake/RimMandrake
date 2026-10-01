<!-- status: cast bible — ticket-out under BLACKCRAGS_BEDAZZLE_SITTING_1 movement 4 (commission waits for the owner) -->
# The Abyss — bedazzle cast bible (movement 4: ticket-out)

**Item:** `BLACKCRAGS_BEDAZZLE_SITTING_1` · **Program:** `BAROQUE_BEDAZZLE_PROGRAM_1` (row 11, the last)
**Date:** 2026-10-01 · **Author:** BENCH movement-4 ticket-out agent
**Art list:** `infrastructure/artpipe/art_lists/abyss_bedazzle_cast.csv` (24 subjects, 56 jobs, **not filed**: the commission waits for the owner)

## 0. Rulings this ticket-out carries

**Authorities:** `blackcrags_bedazzle_review_2026-09-30.md` §§7–14 (the ruling tables are the truth;
§§1–6 predate the rename, so `ForsakenCrags` there is `Abyss` now), every `ABYSS_*` item,
`SALVATION_RITES_UNIFICATION_1` (`design/Jawa/salvation_rites_2026-10-01.md`), and `abyss_free_cryptid_2026-10-01.md`. Card selections are
*decision taken by question card*; only typed words are quoted.

| # | ruling | how | what it means for the cast |
|---|---|---|---|
| 1 | The biome is **the Abyss**, full rename | typed | `RM_Abyss` / `RUT_Abyss`, `src/RimMandrake/Abyss/`, composed into `mandrake.rm.biomes` |
| 2 | The Dark, full: heat folds it, the rare Unveiling, the storm call, a strength slider | card | every sprite must read in near-darkness (§2) |
| 3 | Hidden ship, typed: *"Yes but probe droids will still come that must be avoided."* | typed | campaign tier; the probes are existing Droidworks content, no new art |
| 4 | gharrek, durrgak, krizzak, etchcap all admitted | card | four new subjects, no art anywhere (§3) |
| 5 | Etchfall erodes unroofed stone and steel, leaves tholin that refines to fuel, strength slider | card | tholin as filth + item |
| 6 | Lamp crops kept; **gust turbines CUT** | card | no turbine anywhere in this bible |
| 7 | cindermare and skarnix move to `RM_`; the two placed donor beasts are freed, typed: *"Fully regenerate art and names for those two beasts. No donor dependencies tolerable. Free us."* | card + typed | two new names (§5), fresh art; the old `crags_ghorrumak_*` / `crags_zhurrakor_*` art does **not** count |
| 8 | Lightfall's bottom: the Brood, plus the Ship in the Wall as a salvage site | card + typed | brood-mother, egg, great bone, bone field, wreck |
| 9 | **Alien megafauna, NOT a fantasy dragon**: no fire breath, no hoard, no wings-and-scales heraldry, never the word "dragon" in a label, defName or description | typed | every brief below says so |
| 10 | **Greed wakes an unkillable brood-mother** | typed | she is drawn as a thing to flee, not a boss to fight |
| 11 | **The egg imprints only with a great bone aboard** | typed | the great bone is an installable building, not only a resource |
| 12 | **The beast is bane and boon, UV-sensitive, sees in the dark** | typed | species traits of the freed giant (§4C) |
| 13 | The cryptid is **the Nhaleth** in every tier; the Star Wars layer adds only the Sith whisper; "Forsaken" is reserved for the Rakata | typed | never on screen: **no art** (ban 7) |
| 14 | Fold-lamp: research that warmth pushes the Dark back, then a heater-lamp that holds a clear lane | card | one faced building |
| 15 | Free tier gets no ship touch | card | nothing owed |
| 16 | **Both soundscapes**: the gust register and the Dark that swallows sound (the second half gated by a spike) | card | audio, not sprites |
| 17 | Darkness the only condition; the Abyss's deep dark teaches **four** rites (the Dark Vigil, the Blind Offering, the Snuffing, the Lightless Burial), each appeasing a different god, performed anywhere dark later; they live in The Salvation's suite, `mandrake.rut.rites`, not a new mod (review §14) | card + typed | no build item yet (`SALVATION_RITES_UNIFICATION_1` is design-stage); the four inscriptions are drafted in §6D |

## 1. Build-item audit

Every ruled feature and the item that carries it. **One item was missing and is now filed:**
`ABYSS_FREE_TIER_BODY_1` (FOUNDRY), the review's §5 #12 pre-ticket lines that nothing carried.

| ruled feature | item | state |
|---|---|---|
| The Dark, the Unveiling, the storm call | `ABYSS_DARK_BUILD_1` | exists; its storm-call line **corrected this pass** (it still named `AA_Behemoth` and the donor art; now points at the freed giant) |
| Fold-lamp + heat-folding research | `ABYSS_FOLD_LAMP_BUILD_1` | exists |
| Hidden ship + probe droids (campaign) | `ABYSS_HIDDEN_SHIP_PROBES_1` | exists; the `surveyShadowBiomes` fix landed with the rename |
| gharrek (+ the minimal gust signal) | `ABYSS_GHARREK_BUILD_1` | exists |
| durrgak (rings, caches, tamed tidying) | `ABYSS_DURRGAK_BUILD_1` | exists |
| krizzak (light-thief, real flight) | `ABYSS_KRIZZAK_BUILD_1` | exists |
| etchcap + etch-hollow | `ABYSS_ETCHCAP_BUILD_1` | exists |
| Etchfall + tholin | `ABYSS_ETCHFALL_BUILD_1` | exists |
| Lamp crops | `ABYSS_LAMP_CROPS_BUILD_1` | exists |
| cindermare, skarnix to `RM_` | `ABYSS_INVENTED_CREATURES_TO_RM_1` | exists |
| The two freed beasts | `ABYSS_DONOR_BEASTS_FREED_1` | exists; its "check whether the donor art satisfies" line **corrected** (§9 settled it: it does not), names pointer added |
| Brood, egg, great bone, wreck, greed meter, bane-and-boon beast | `ABYSS_LIGHTFALL_BROOD_WRECK_1` | exists |
| The Nhaleth | `ABYSS_FREE_CRYPTID_1` | exists |
| Both soundscapes | `ABYSS_SOUNDSCAPE_BUILD_1` | exists |
| The four found dark rites | `SALVATION_RITES_UNIFICATION_1` | BENCH design stage; no build item yet (home ruled: `mandrake.rut.rites`) |
| Free-tier labels, the 12 finished `crags_*` sets wired, dusk-rat redo, 8 flora rows guarded or owned, Etchfall/Witchfire owned names, About.xml Forsakens line, paint list | **`ABYSS_FREE_TIER_BODY_1`** | **filed this pass** |
| Gust turbines | — | CUT, no item |
| Free-tier ship touch | — | ruled out, no item |
| Ulkhorr's halo (slate #6), Lightfall rung ladder (slate #9c) | — | never put on a card; not admitted, nothing filed |

## 2. Shared law. Every entry obeys this without restating it

- **The light.** Permanent night under the Dark. There is no sun and no sky-light. A sprite is lit
  only by a **dim cool rim light** from above-behind and, where the subject has one, **its own
  glow**. Silhouettes must still read at game zoom against near-black obsidian: rim and value
  carry the read, never a bright fill. 🔴 **No baked cast shadow**, and no daylight anywhere.
- 🔴 **Palette diversity is law.** Owner, verbatim, carried in every `style_notes`: *"Your color
  palette is too uniform per biome. Needs more variety."* A biome of black needs it most. Each
  subject has its own anchor (§7), no two the same.
- **The admission test** (review §3): *every new thing must either live by the Dark, or trade in
  light.* Hard bans: nothing sun-fed (ban 6), no steady wind (ban 2), no geothermal (ban 1), no
  on-screen Nhaleth (ban 7), and nothing that vanishes without a readable sign.
- 🔴 **No fantasy dragons** (ruling 9). The storm giant and its brood are alien megafauna in the
  krayt / rancor / zillo register: a biology, not a heraldry. No fire, no wings-and-scales
  silhouette, no hoard, and the word "dragon" never reaches a label, defName or description.
- **House style:** painterly vanilla-RimWorld, matte, no outlines, never cute. On faced jobs north
  is a true rear view with no face; facings derive from the accepted east master (`fill_queue.py`
  default). Flight frames are a **whole-body flip-book**, never a wing layer (CLAUDE.md flight
  rule; Locust ships 5 frames).
- **Tier (Q11a):** everything invented is `RM_`. The Lightfall lair's unique things (brood-mother,
  egg, great bone, bone field, wreck) are campaign content and take `RUT_`; the brood **species**
  is the free giant, so the brood-mother is a `RUT_` PawnKind on the `RM_` race.

## 3. Art dedup sweep

**MEASURED 2026-10-01, before anything was listed.** One python sweep over the on-disk
`infrastructure/artpipe/{done,_artsrc,pending,active,failed,_withdrawn}` (4,634 entries in `done/`,
2,087 in `_artsrc/`), `registry.jsonl`, `art_status.json` and all 16 `Transient/*.decisions.json`,
plus `git ls-files src` for PNGs. Each subject searched by current, alternate and old names.

**Sanity probes, so a zero means zero:** `mynock` 6 in `done/`, 3 in `_artsrc/`, 12 registry lines,
2 decisions files; `korrum` 6 in `done/`; `vrakk` 6 in `done/`, 18 registry lines.

| subject | spellings searched | result |
|---|---|---|
| gharrek, durrgak, krizzak, etchcap | + krovvak, gillfan, dhagga, cairn, drekkis, lightthief, etchhollow | 0 everywhere, **listed** |
| tholin, gill-ash, fold-lamp, great bone, egg, wreck, rumor sites | + heaterlamp, bonefield, giantbone, broodegg, gravshipwreck, rescueship, stonecircle | 0 everywhere, **listed** |
| brood-mother | brood | only `rm_thrummelbroodmother_*` (another biome's creature), **listed** |
| the two new names | rukkadh, grokkath, khaggar, tukkrag, gekkor, drokkat | 0, **listed** |
| ghorrumak, zhurrakor | + behemoth, nighthrumbo | `crags_ghorrumak_*`, `crags_zhurrakor_*` done (3 facings each), approved 2026-09-06 (`art_review_2026-09-06.decisions.json`). 🔴 **Does NOT count:** donor-bodied, and the owner ruled "fully regenerate" (review §9). **Fresh jobs listed.** |
| cindermare, skarnix | — | 0 in artpipe, but **shipped PNGs exist**: `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/{Cindermare,Skarnix}/*.png`. No ruling on either. **Reused** (move with the defs), 0 jobs |
| the 12 other `crags_*` sets | vrakk, dhukk, hulggarok, zekkra, kessik, brekkugar, korrag, bhoruk, gruzz, shekkur, ulkhorr, thrizzik | done, 3 facings each, unwired. **Reused** (`ABYSS_FREE_TIER_BODY_1` wires them), 0 jobs. ⚠ `crags_kessik_east` also has a `failed/` entry; the `done/` copy is the live one |
| dusk rat | duskrat, dusk_rat | no art; owner "replace" ruling 2026-09-20 (`port_alphaanimals_2026-09-20.decisions.json`). **Listed** |
| gamma family (lamp-crop body) | gamma, stikehr, radagast, septimum | `giantgamma_v1`, `giantstikehr_v1`, `septimum_v1`, `giantseptimum_v1` (+ siblings) done 2026-09-13, unwired; owner "replace with our own def and our own art" 2026-09-20 (`port_tail`, `desert_family_review`). **Reuse candidate** for the lamp crop: `giantgamma_v1`, 0 jobs, fallback 1 if he rejects it on sight |
| the Nhaleth | — | **no art by law** (ban 7) |

## 4. Cast entries

The CSV's `prompt` and `style_notes` cells are the exact text each job carries; this is the intent.
Every creature is single-homed in the Abyss.

### 4A. The web of the Dark (free, `RM_`)

**gharrek** · `RM_Gharrek` · bs ~0.6 · `ABYSS_GHARREK_BUILD_1`
- *Plain:* a flat, many-gilled crawler the size of a dinner plate that clings in the lee of the
  crags.
- *Behaviour:* dormant in the still, plates shut, cold, nearly invisible on obsidian. At every
  gust every gharrek on the map **opens at once** and feeds on the stirred air: a map-wide carpet
  of fluttering gill-fans with a faint flameless chemical glow, then shut again. Harmless; the
  prey that makes the vrakk and the shekkur hunt in the gusts. Penned, it fattens only in gusts
  and gives **gill-ash** (chemfuel feedstock beside tholin).
- *Art:* drawn **half-open**, so both states read: overlapping slate plates lifting off a ring
  of frilled gill-fans with a faint verdigris-teal inner glow. Anchor **slate and verdigris**.
  256, faced. Item: `RM_GillAsh` (a pinch of pale grey-green ash, a few glowing flecks).

**durrgak** · `RM_Durrgak` · bs ~1.2 · `ABYSS_DURRGAK_BUILD_1`
- *Plain:* a slow, stoop-backed digger with very long, jointed fingers.
- *Behaviour:* it **arranges things**: obsidian shards into rings and rows, glow-berries into
  neat caches, its den lined with what it finds, dropped steel included. The rings go up whether
  or not one is in sight; pawns who find one get a small "someone was here" thought. The
  description never says who. Shy. Tamed, it **tidies**: it hauls small items to stockpiles at a
  crawl.
- *Art:* a patient, almost thoughtful posture, one long hand holding a shard. Hide the warm
  dusty umber of a mole, fingers pale. Anchor **umber and bone**. 256, faced.
- *Its works:* `RM_DurrgakCairn`, a low ring of upright obsidian shards (256 single). 🔑 **The
  Nhaleth rumor circle reuses this exact art** (`ABYSS_FREE_CRYPTID_1`: neither may be told
  apart with certainty), so one job serves both. `RM_AbyssStockedDen` (a den mouth lined with
  arranged scrap and a too-neat berry pile) and `RM_AbyssSalvageCache` (a tidy stack of salvage
  on a shard ring) serve both the durrgak and the rumor sites.

**krizzak** · `RM_Krizzak` · bs ~0.3 · flier · `ABYSS_KRIZZAK_BUILD_1`
- *Plain:* a soft, dark moth-thing the size of a hand, with a mouth like a lamp-glass.
- *Behaviour:* it **eats light**. Swarms settle on glow plants and dim them, and cluster on
  powered lamps, smothering the lit radius: a perimeter going dark one lamp at a time is the
  warning. It takes no power, only the glow. Scatters from heat. **Real flight**
  (`MaxFlightTime`, race flags, PawnKindDef flip-book); never live-tested unattended.
- *Art:* velvet wings the deep plum of a bruise, a pale glassy domed mouth that holds a faint
  stolen glow. Anchor **plum and lamp-amber**. 256, faced ground set (wings folded) **plus 5
  whole-body flight frames × 3 directions** (`RM_Krizzak_Flying_1..5`, wings tucked → spread →
  tucked).

**etchcap** · `RM_Etchcap` · plant · `ABYSS_ETCHCAP_BUILD_1`
- *Plain:* a dense black-and-violet cap fungus that grows only in etch-hollows, the low cells
  where the Dark's collapse-grain settles.
- *Behaviour:* not sun-fed; it lives on grain chemistry. Slow, low yield, a **delicacy**: a
  lavish-meal ingredient and an off-world trade good. Wild only, or sown on `RM_EtchHollow`
  (terrain, authored with its def, not a sprite job).
- *Art:* a tight cluster of glossy black caps with violet gill-edges, crusted with fine grey
  grain at the base. Anchor **black and violet**. Plant 256 single; produce `RM_EtchcapCap`
  (three harvested caps, violet undersides showing) 256 single.

**tholin** · `RM_Tholin` (item), `RM_Filth_Tholin` · `ABYSS_ETCHFALL_BUILD_1`
- The swept residue of etchfall: a rust-brown, faintly oily dust that refines to chemfuel. Item:
  a heap of reddish-brown powder in a rough sack mouth, a greasy sheen. Filth: a drift of the same
  dust in rings, thickest at the edge of a warm clearing (GPT's ring rule). Anchor **rust-brown
  and tar**. Both 256 single.

### 4B. The two inventions moved in (free, `RM_`, `ABYSS_INVENTED_CREATURES_TO_RM_1`)

- **cindermare** · `RM_Cindermare` · a mouthless predator that kills by grip, draining the
  warmth. Its existing shipped PNG moves with the def. 0 jobs.
- **skarnix** · `RM_Skarnix` · a cat-sized ambush stalker that will not cross firelight or a
  heated space. Its existing PNG moves with the def. 0 jobs.
- Their descriptions' "Forsaken Crags" text becomes "the Abyss". If he wants faced sets in this
  bible's register rather than the shipped singles, that is 6 jobs, held.

### 4C. The freed beasts (free, `RM_`, `ABYSS_DONOR_BEASTS_FREED_1`)

Names are proposals (§5), **owner to confirm**.

**The storm giant** · proposed **rukkadh** · `RM_Rukkadh` · bs ~8 (the donor's value was
UNMEASURED; 8 is proposed)
- *Plain:* a vast, low, many-legged grazer of the deep crags whose voice is the thunder.
- *Behaviour:* it feeds on the charge the Dark carries; in a Witchfire storm, the roll you hear a
  few seconds before a flash with no lightning is a rukkadh calling (`ABYSS_DARK_BUILD_1`). One may
  come down and cross the map in the storm. It regenerates. **UV-sensitive** (it suffers in
  daylight off the Abyss) and **sees in darkness and the Dark unimpaired**. Wild, it is a passing
  terror; tamed (§4D), it is bane and boon.
- *Art:* krayt / zillo register, never a dragon. A long armoured body slung low on six thick
  limbs, a broad blunt head with no horns or crest, **great resonating throat-sacs** down the
  neck and chest that faintly glow a storm-violet when charged, tiny deep-set eyes adapted to the
  dark, hide like wet-dark basalt with pale lichen-grey plating. No wings, no fire, no scales in
  a heraldic pattern. Anchor **basalt and storm-violet**. 1024, faced.
- *Juvenile:* `RM_Rukkadh_Juvenile`, the hatchling's life stage: oversized head and throat-sac
  buds, soft pale hide not yet plated, already hungry and hostile. Anchor **pale ash and
  violet**. 512, faced.

**The quill predator** · proposed **tukkrag** · `RM_Tukkrag` · bs ~3
- *Plain:* a heavy, low-slung night hunter whose back is a crown of long sensory quills.
- *Behaviour:* in the Dark it hunts by feel: its quills pick up the tremor of anything moving,
  and it **raises them in a clattering hackle** before it lunges and pins. It does not throw them
  (that is the vrakk's lane). An ambusher, not a pursuer.
- *Art:* powerful forequarters, a short broad muzzle, quills banded bone and rust that fan up
  from the neck to the haunch, dark ochre hide. Anchor **ochre and banded bone**. 512, faced.

### 4D. The Brood and the Ship in the Wall (campaign, `RUT_`, `ABYSS_LIGHTFALL_BROOD_WRECK_1`)

- **The brood-mother** · `RUT_RukkadhBroodMother` (PawnKind on the `RM_Rukkadh` race, much larger
  draw size). *Plain:* the oldest rukkadh, asleep coiled round her clutch among giant bones.
  *Behaviour:* light and noise from egg theft and salvage feed one **wake meter**; her stirring
  and a low rumble are the readable signs; **past the greed line she wakes and is essentially
  unkillable**: you flee. *Art:* the species, but ancient: plating grown into a ridged shell
  scarred white, throat-sacs vast and dark, lichen and grain crusted on her back so she reads as
  part of the cavern floor until she moves. Anchor **bone-white scar on black**. 1024, faced.
- **The egg** · `RUT_RukkadhEgg`. A leathery, heavy egg the size of a barrel, dark violet veins
  under a grey grain-dusted shell, a faint inner pulse of light. Its inspect text must say plainly
  why it has not bonded when no great bone is aboard. Anchor **grey and pulse-violet**. 256
  single.
- **The great bone** · `RUT_GreatBone` (installable, minified building) and `RUT_BroodBone`
  (the stuff, from the bone field). *Behaviour:* one great bone **installed aboard the gravship**
  is what lets the egg imprint; without it the hatchling stays wild. *Art:* the great bone is one
  colossal curved rib or vertebra, ivory gone amber with age, light for its size, lashed to a
  cradle so it can stand on a ship deck (1024×512 single). The stuff is a stack of cut pale bone
  planks (256 single). Anchor **old amber ivory**.
- **The bone field** · `RUT_BroodRibArch`, a scatter building: a half-buried arch of giant ribs
  the brood nests among. 1024×512 single. Anchor **grey chalk bone**.
- **The Ship in the Wall** · `RUT_WallWreckHull` and `RUT_WreckDebris`. A wrecked rescue gravship
  driven nose-first into the chasm wall: not a second ship, a **salvage site**. The haul is
  existing ship parts and components (no new art); the player's own ship takes only some of them
  and says so in plain words. *Art:* the hull section as a map building, 1024 single (torn plating,
  a dead running light, grain drifted into the seams, faded rescue stripes); a debris pile 512
  single. Anchor **faded rescue orange on grey**.
- **The tamed beast, bane and boon:** the hatchling raised is the `RM_Rukkadh` race. Very hungry
  and very aggressive (it kills wildlife indiscriminately and semi-randomly), deeply tough and
  powerful, UV-sensitive, sees in the dark. Its art is the species set above; no extra job.

### 4E. Light that grows, and light you build (free, `RM_`)

- **The lamp crop** · `ABYSS_LAMP_CROPS_BUILD_1`. A glowing tree transplanted to light a farm
  against the Dark. Our own def (`RM_LampCrop` proposed), not the donor `AB_GiantGamma`. Art
  **reuse candidate:** `giantgamma_v1` (done, unwired, our own redraw). 0 jobs; 1 if he rejects
  it on sight.
- **The fold-lamp** · `RM_FoldLamp` · `ABYSS_FOLD_LAMP_BUILD_1`. A fuelled heater-lamp with a
  directional throat that holds a lane of clear air open. Not a sensor (ban 5): a squat iron
  firebox with a flared brass throat, a warm orange glow pouring out of the mouth. It points, so
  it is faced (256, s,e,n). Anchor **iron and ember**.

### 4F. The donor cast, kept and wired (`ABYSS_FREE_TIER_BODY_1`)

The 12 finished `crags_*` sets (vrakk, dhukk, hulggarok, zekkra, kessik, brekkugar, korrag,
bhoruk, gruzz, shekkur, ulkhorr, thrizzik) are reused as they are; the free tier gains their
invented labels. **The dusk rat** (`RM_DuskRat`, the name is the joke, kept) gets its owed art
redo: a lean, bald-tailed kitchen-soiling rat-analog with oversized night eyes, smoke-grey fur with
a dusk-rose belly. Anchor **smoke and dusk-rose**. 256, faced.

### 4G. Not drawn

- **The Nhaleth:** never on screen (ban 7). Art tales only, by grammar.
- **The Dark, the Unveiling, etchfall's overlay, the etch-hollow terrain:** authored with their
  engine and terrain defs, not sprite jobs.
- **Probe droids:** existing Droidworks content.
- **The dark rite:** no object of its own is ruled yet.

## 5. Names for the two freed beasts (owner to confirm)

Accent rule (batch-3a names doc rule 5): *"Crags: hard voiced stops, k/g/r clusters… said in a
gust."* No four-letter opening shared with the crag names (vrakk, dhukk, hulggarok, zekkra, kessik,
brekkugar, korrag, bhoruk, gruzz, shekkur, ulkhorr, thrizzik, gharrek, durrgak, krizzak, skarnix,
cindermare) or with `korrum`; and nothing echoing the old names (ghorrumak, zhurrakor).
⛔ `goddrak` from the review's spares is **excluded**: its `-drak` reads as "dragon" (ruling 9).

**Checked 2026-10-01:** `git grep -il` over `src design infrastructure skills` on `origin/main`
(probe `mynock` 243 files, `gharrek` 9): each candidate hits **1** file, the review's own spares
list, and nothing else. Wookieepedia search API (`list=search&srsearch=`; probe `mynock` returns
*Mynock, Mynock/Legends, Ord Mynock*): **0 results** for every candidate.

| beast | proposed | alternates | why |
|---|---|---|---|
| the storm giant (ex-ghorrumak) | **rukkadh** (*ROOK-kahd*) | grokkath, khaggar | a rolled *r*, a hard stop, and a breathy *-dh* like thunder dying in the rocks |
| the quill predator (ex-nighthrumbo/zhurrakor) | **tukkrag** (*TUK-rag*) | gekkor, drokkat | a dry double stop, the sound of quills clattering up |

DefNames follow the names: `RM_Rukkadh`, `RM_Rukkadh_Juvenile`, `RUT_RukkadhBroodMother`,
`RUT_RukkadhEgg`, `RM_Tukkrag`. **If he picks an alternate, the CSV ids change before filing.**

## 6. Lore for his pen

Drafts only, as Warscar §6 did. **Each is marked for his pen: accept, rewrite or strike.**

### 6A. The storm giant's biology (`ABYSS_LIGHTFALL_BROOD_WRECK_1` owes "why it nests here, why the storms answer it") — DRAFT, FOR HIS PEN

> The rukkadh grazes on the Dark itself. The Dark holds a charge, and the rukkadh's throat-sacs
> gather it as it feeds, until the beast is heavy with it and must call it out: that is the
> thunder. The Witchfire storms gather where the most charge has been drawn down, so a storm does
> not bring the rukkadh; the rukkadh brings the storm. They nest at Lightfall's bottom because the
> Dark is thickest there and has never once lifted, and an egg must lie a year in perfect dark to
> hatch. Sunlight burns them. They see by the faint glow of their own throats.

### 6B. The ship's refusals (the wreck's "refused parts say so") — DRAFT, FOR HIS PEN

> *"The ship will not take this. It does not want to be something else."*
> *"It knows its own shape. This part is not its shape."*
> *"It accepts the coupling. Something in the old frame settles, as if it remembered."* (an accepted repair)

### 6C. The wreck's story (description text) — DRAFT, FOR HIS PEN

> A rescue ship, by its faded stripes. It came down into Lightfall after someone, and it is
> still here. Whatever it came for, nobody climbed out with it.

### 6D. The four found rites (`SALVATION_RITES_UNIFICATION_1`, review §14) — DRAFT, FOR HIS PEN

Each inscription is the rite's `CompStudiable` find, studied in the dark; its rubbing is learned on
the Rites tab (`design/Jawa/salvation_rites_2026-10-01.md` §d). Sites are candidates.

- **The Dark Vigil** (Ishko), where no light has ever reached:
  > "Sit where the dark is whole. Make no light. Do not speak until the dark speaks first."
- **The Blind Offering** (Mob'Unloo), at the Nhaleth circle (`RM_DurrgakCairn`):
  > "Name what is owed. Set it down. Go, and do not turn. What is taken is paid."
- **The Snuffing** (Sh'kaar), at a ring of lamps all put out by hand, long ago:
  > "He sees by what you light. Put it out, one and then the next, until he forgets where you are."
- **The Lightless Burial** (Ozzik), cut beside the rescue ship's dead in Lightfall:
  > "We were more once. Bury that with them, in the dark, and close it before the light comes back."

Names, wording and sites are **his**; Sh'kaar's answer when the dark breaks is ruled (it fails and
he answers). Nothing here is a build input until he rules.

## 7. Art list: 24 subjects, 56 jobs (NOT filed; the commission waits for the owner)

**CSV:** `infrastructure/artpipe/art_lists/abyss_bedazzle_cast.csv`. Channel codex, transparent,
`reference` empty on every row (fresh designs). Not queued. `fill_queue.py --dry-run` 2026-10-01: 56 would be filed, 0 duplicates refused, 0 row errors; re-run it
when he commissions it. **10 faced sets (one of them the 5-frame flight set) + 14 singles = 24
subjects, 56 job files.** Reused, 0 jobs: **15 subjects** (12 `crags_*` sets, cindermare,
skarnix, the lamp crop via `giantgamma_v1`).

| item | id | canvas | facings | jobs | anchor |
|---|---|---|---|---:|---|
| GHARREK | `RM_Gharrek` | 256 | s,e,n | 3 | slate and verdigris |
| GHARREK | `RM_GillAsh` | 256 | single | 1 | grey-green ash |
| DURRGAK | `RM_Durrgak` | 256 | s,e,n | 3 | umber and bone |
| DURRGAK | `RM_DurrgakCairn` (also the Nhaleth circle) | 256 | single | 1 | obsidian and frost |
| DURRGAK | `RM_AbyssStockedDen` / `RM_AbyssSalvageCache` | 256 | single | 2 | dusty steel / scrap brass |
| KRIZZAK | `RM_Krizzak` | 256 | s,e,n | 3 | plum and lamp-amber |
| KRIZZAK | `RM_Krizzak_Flying_1..5` | 256 | s,e,n ×5 | 15 | plum and lamp-amber |
| ETCHCAP | `RM_Etchcap` / `RM_EtchcapCap` | 256 | single | 2 | black and violet |
| ETCHFALL | `RM_Tholin` / `RM_Filth_Tholin` | 256 | single | 2 | rust-brown and tar |
| FREED | `RM_Rukkadh` | 1024 | s,e,n | 3 | basalt and storm-violet |
| FREED | `RM_Rukkadh_Juvenile` | 512 | s,e,n | 3 | pale ash and violet |
| FREED | `RM_Tukkrag` | 512 | s,e,n | 3 | ochre and banded bone |
| LIGHTFALL | `RUT_RukkadhBroodMother` | 1024 | s,e,n | 3 | bone-white scar on black |
| LIGHTFALL | `RUT_RukkadhEgg` | 256 | single | 1 | grey and pulse-violet |
| LIGHTFALL | `RUT_GreatBone` | 1024×512 | single | 1 | old amber ivory |
| LIGHTFALL | `RUT_BroodBone` | 256 | single | 1 | pale bone plank |
| LIGHTFALL | `RUT_BroodRibArch` | 1024×512 | single | 1 | grey chalk bone |
| LIGHTFALL | `RUT_WallWreckHull` / `RUT_WreckDebris` | 1024 / 512 | single | 2 | faded rescue orange on grey |
| FOLDLAMP | `RM_FoldLamp` | 256 | s,e,n | 3 | iron and ember |
| BODY | `RM_DuskRat` | 256 | s,e,n | 3 | smoke and dusk-rose |
| | **total** | | | **56** | |

## 8. Handoff notes

- **Owner to confirm before the commission:** the two names (§5), and whether `giantgamma_v1`
  serves as the lamp crop. A changed name changes CSV ids; re-run the dedup check on it.
- **Then:** `fill_queue.py --dry-run` on the CSV, expect 56 filed and 0 refused, then file.
- The krizzak's flight frames follow the Locust count (5). If the def pass chooses 8 (the
  Chicken/Sparrow count), add three frames × 3 directions.
- The brood-mother shares the species' anatomy; if her accepted east master drifts from
  `RM_Rukkadh`'s, re-cut from the species master rather than re-generating both.
- The great bone is drawn standing in a cradle so it reads aboard a ship deck; if the build makes
  it a wall-mounted fitting instead, re-cut.
- The cindermare and skarnix move with their shipped single PNGs; faced sets in this register are
  6 jobs, held unless he asks.
