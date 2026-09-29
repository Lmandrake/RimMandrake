# Leaning Scrub — bedazzle review (movements 1–2), 2026-09-29

Program row 7 of `BAROQUE_BEDAZZLE_PROGRAM_1`. Biome lives under TWO names: ruled name
**Leaning Scrub** (`src/RimMandrake/LeaningScrub/`, BiomeDef `RM_LeaningScrub`) and legacy
campaign label **"desert"** (roster `rosters/desert.json`, frozen sheet `desert.md`).
`arid_shrubland` is a different biome and is not covered here.

## Name mapping confirmation — 🔴 the brief's mapping was WRONG; corrected from the files' own headers

**Leaning Scrub's legacy campaign label is `arid_shrubland`, NOT "desert".** Confirmed from
the files themselves, three independent ways:

1. `src/RimMandrake/LeaningScrub/About/About.xml` (its own description): *"It generalizes
   the biome sketched for a frozen campaign world's own arid shrubland
   (design/Jawa/worldbuilding/biomes/arid_shrubland.md)"*.
2. `RM_LeaningScrub_Biome.xml` header: *"the RimMandrake-tier twin of the frozen
   src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_AridShrubland.xml"*. The Utinni patch
   `WildAnimals_LeaningScrub.xml` copies its 40 rows *"verbatim from the LIVE
   RUT_AridShrubland.xml wildAnimals block"*.
3. The other direction: `desert.md`'s own thematic handle is **"the long shade"**, and
   `long_shade_bedazzle_2026-09-27.md` names its subject `RUT_Desert` → `RM_LongShade`
   against `rosters/desert.json`. Desert = **Long Shade** (program row 8, sitting held
   2026-09-27) — not this biome.

So this review reads: frozen sheet **`arid_shrubland.md`** (🧊 FROZEN
`BIOME_FREEZE_FABLE_REVIEW_1` 2026-09-07, +2026-09-21 knee-height amendment), roster
**`rosters/arid_shrubland.json`** (authored 2026-09-09; `"sheet": "arid_shrubland"`,
`"defNames": ["RUT_AridShrubland"]`), twins `RM_LeaningScrub`/`RUT_AridShrubland`.
`desert.md`/`desert.json` appear below only where they carry this biome's material — the
Blurrg reservation does route here (Long Shade Q8: *"Blurrg OUT (keeps a home for the
Leaning Scrub sitting)"*), so the brief's Blurrg pointer was right even though its name
mapping was backwards. No pre-rename residue: mod folder, packageId
(`mandrake.rm.leaningscrub`), BiomeDef and all owned defs already carry the
LeaningScrub/RM_ spelling, so no Rename census section is owed.

## What's there

Sources read this pass: all of `src/RimMandrake/LeaningScrub/`, the frozen twin
`RUT_AridShrubland.xml`, `UtinniPatches/Patches/WildAnimals_LeaningScrub.xml`,
`rosters/arid_shrubland.json`, frozen `arid_shrubland.md`,
`long_shade_bedazzle_2026-09-27.md` (Blurrg ruling), the desert accent batch,
`LEANINGSCRUB_RM_MOD_BUILD_1` (closed), artpipe registry/done/_artsrc, and the design
record for the shrubland kit pieces (`SHRUBLAND_GIANT_ENRAGE_1`,
`sweetline_guardian_spec.md`, `TREE_GRAPHICS_OWNERSHIP_1`).

### BiomeDef(s)

Twin architecture, both live:

- **`RM_LeaningScrub`** — `src/RimMandrake/LeaningScrub/Defs/BiomeDefs/RM_LeaningScrub_Biome.xml`,
  ships in `mandrake.rm.leaningscrub` ("RimMandrake: Leaning Scrub"), built 2026-09-25
  (`LEANINGSCRUB_RM_MOD_BUILD_1`, Phase A row 9). animalDensity 1.8, plantDensity 0.35,
  forageability 0.5, workerClass vanilla-Core `BiomeWorker_AridShrubland` (deliberate — no
  RM worker owed), vanilla `World/Biomes/AridShrubland` worldmap texture. Weather is
  stock defs re-weighted: Clear 30 / **Fog 45** / DryThunderstorm 1 / rain+snow all 0 /
  GrayPall 1 / Overcast 5. All values byte-copied from the frozen twin (its header,
  MEASURED 2026-09-25). Hard modDependency: `mandrake.rm.environmentalhazards`.
- **`RUT_AridShrubland`** — the frozen campaign twin, still serving the live world; its
  own `wildPlants` still names the old RUT_ flora under
  `MayRequire="mandrake.rut.ashkarrflora"` (that mod is deliberately NOT dissolved yet —
  Phase B step 4 deletes both together, per the RM def's own header).

### Flora (def-inline; no Utinni flora patch for this biome)

11 rows on `RM_LeaningScrub` (shorthand `<DefName>commonality</DefName>` form, parsed as
such): **`RM_Fuzz` 0.9** (THE signature canopy plant, renamed from RUT_ per Q8),
`RG_Plant_AridGrass` 0.5, `Plant_Brambles` 0.3, **`RM_Grellbush`/`RM_Grellspine`** 0.3
each, **`RM_WildHealroot`** 0.25, `Plant_Nysyllin_Wild` 0.22 (not IP per Q11a),
`RG_Plant_CreepStern`/`RG_Plant_CrimsonCushion`/`RG_Plant_Dervish` 0.2 each,
**`RM_VenomvineThicket` 0.15** (fortress flora, shipped by the EnvironmentalHazards kit).
**`RM_SweetlineTree`** ships as a def in this mod but is deliberately NOT in wildPlants —
the frozen twin never wired it either, and `TREE_GRAPHICS_OWNERSHIP_1` owns how the
landmark tree places (hand-placed surveyor's mark, not scatter). `RM_SweetlineWool`
("giant-wool") ships as the tree's harvest item.

⚠️ Roster's own ban-9 finding stands unfixed: 10 of 11 landed flora rows measure
Flammability 0.6–1.3 against the sheet's hard ban 9 (*"no flammable living flora"*) —
every note reads "KEPT, not re-picked — no Flammability-0 donor exists that fits". Only
`RM_VenomvineThicket` (0.1) satisfies it as authored. The permanent fix is OUR flora
replacing donors, which is exactly what a bedazzle fill can do.

### Fauna (def + patch-added, merged)

- **RM def inline, 5 non-SW donor rows (Q9):** `Terrorworm` 0.7 (mlie.horrors),
  `AA_Cactipine` 0.25, `AA_Needlepost` 0.1, `AA_Wildpawn` 0.1, `AA_Wildpod` 0.025.
- **Patch-added (`WildAnimals_LeaningScrub.xml`, one PatchOperationConditional +
  PatchOperationAdd onto `RM_LeaningScrub/wildAnimals`, all
  `MayRequire="mandrake.rsw.swbestiary"` — no donor-mod gate remains):** 39 RSW_ rows,
  read from the op's own value: FrilledGorg/Gorg/Iriaz/LongtailGorg 1.0 ·
  Eopie/Lothcat/Mudhorn/Ronto/Scurrier/Sketto/Kreetle 0.8 · Igitz/Urusai/ImperialToad 0.7 ·
  Kybuck/Massiff 0.6 · Bantha/Pufferpig/TunnelSnake 0.5 · ScrapNestBird 0.45 ·
  Anooba/Corinathoth/Gizka/Nuna/Worrt 0.4 · **ShrublandGiant 0.35** · MossBeetle 0.3 ·
  Grank/Qormot/Strill 0.2 · Cannok 0.16 · Whisperbird 0.15 · Pikobis 0.1 ·
  Convor/Skalder/Vulptex 0.08 · FeralNerf/Porg 0.04 · Voorpak 0.02 ·
  KowakianMonkeyLizard 0.01.
- **Campaign cast: 44 wired species.** RM-standalone cast with no donors installed:
  **0 creatures** — every inline row is MayRequire-gated donor fauna. See Q11a gap below.

The roster's invented signature pieces are BUILT and named (`ARIDSHRUBLAND_SHIPPING_NAMES_1`,
4 of 5 ruled 2026-09-21): **thunderstep** (`RSW_ShrublandGiant`, bs 6.0, the huge grazer;
parental enrage shipped 2026-09-20 as `RM_ParentalEnrageExtension`/`RM_CompParentalEnrage`/
`RM_MentalState_ParentalEnrage` in `mandrake.rm.creaturebehaviors` — no Harmony needed),
**yanker** (`RSW_TunnelSnake`, the corridor predator), `RSW_ScrapNestBird` (treasure-nest
bird), plus `RSW_ImperialToad`. Still owed from that card: the player-facing name of **the
fuzz** (BENCH item, do not pick ahead of it) and the bird-analog/sweetline-tree names.

### Terrain / weather / mechanics / C#

- Terrain: stock Sand/Soil/SoilRich by fertility (copied from the twin). ⚠️ The sheet's
  ban 7 says **no open sand terrain** on core shrubland ("root-bound crust") — the def
  still opens with `Sand` below fertility 0.45. Latent sheet-vs-def contradiction, held
  since the frozen twin; a candidate for an owned crust terrain at this sitting.
- Weather: no biome-owned WeatherDefs. **The Stall and the Gale are RULED player-facing
  names (2026-09-21, locked "ahead of their WeatherDefs being built") and remain
  UNBUILT.** The sheet's ban 5 (every ordinary weather carries wind; calm only as the
  Stall event) is unenforced by stock defs.
- C#: `RM_LeaningScrubMod.cs` is settings-only (master toggle + venomvine passability
  gate via the shared `RM_MechanicGates` registry). The two live mechanics are library
  pieces wired by def reference: **venomvine body-size barrier**
  (`RM_MapComponent_BodySizeBarrier`, EnvironmentalHazards) and **parental enrage**
  (creaturebehaviors, on the thunderstep). Nothing else: no Stall/Gale, no canopy
  concealment, no vaporator desertification, no nest-theft, no fire-stamping — all named
  in the About.xml's own "NOT in this mod" list as unbuilt.
- `Patches/BetterTrees_SweetlineTree_Immunity.xml` — defensive tree-mod immunity for
  `RM_SweetlineTree` (matches nothing today, by design).

### Art status per cast member

- **Has art:** `RM_SweetlineTree` (14 variants A–N shipped in this mod's Textures).
  RSW_ bestiary cast rides `mandrake.rsw.swbestiary`'s own textures (ports).
- **Zero PNGs anywhere (each def's own header, MEASURED 2026-09-25):** `RM_Fuzz` — the
  signature plant of the whole biome — plus `RM_Grellbush`, `RM_Grellspine`,
  `RM_WildHealroot`, and `RM_SweetlineWool`. The def headers note existing artpipe jobs
  target the OLD RUT_ texPaths in mandrake.rut.ashkarrflora and do not benefit the RM_
  defs. Artpipe census this pass (registry.jsonl + done/ + _artsrc/, searched by both
  RUT_ and RM_ spellings): see the art table below.

## Nine-mark scorecard

| # | Mark | Verdict | Evidence |
|---|---|---|---|
| 1 | Unique mechanic | **HAVE** | Venomvine body-size barrier is live C# (`RM_MapComponent_BodySizeBarrier`, EnvironmentalHazards; no other biome consumes it today) + parental enrage on the thunderstep (built 2026-09-20). But the sheet's marquee mechanics — Stall/Gale, ripple concealment, V-blight — are RULED (frozen sheet 2026-09-07; names locked 2026-09-21) and UNBUILT. |
| 2 | Discoverable technology | **MISS** | Nothing teaches a keepable craft. The smother-craft (blanket → banked claim → premium fuel) and the moisture-farm trade are both in the frozen sheet (§4/§7, 2026-09-07) with zero defs — RULED-but-unbuilt. |
| 3 | Unique resources | **PARTIAL** | `RM_SweetlineWool` shipped (SWEETLINE_WOOL_HARVEST_1 closed); scrap-nest treasure mechanism shipped (SHRUBLAND_SCRAPNEST_BIRDS_1 closed; `SCRAPNEST_BIRD_LIVE_VERIFY_1` still owed). Dead-venomvine fuel and the smother-blanket trade good: no defs. |
| 4 | Surprising creatures | **HAVE** | `RSW_ScrapNestBird` with real nest-theft C# (RimMandrakeBeastMechanicsRSW.dll); yanker (`RSW_TunnelSnake`) the corridor-shaped predator; `AA_Wildpod` huge-sessile. |
| 5 | GIANT beast | **HAVE (art caveat)** | Thunderstep `RSW_ShrublandGiant`, bs 6.0, enrage comp live — but its art is a reskinned Fambaa (`texPath swanimals/Fambaa/...`); own art never queued (artpipe: 0 jobs under shrublandgiant/thunderstep, probe imperialtoad=12 proves the instrument sees). |
| 6 | Gravship touch | **MISS** | Nothing anywhere references the ship in this biome's voice. Slate targets it. |
| 7 | Soundscape | **MISS (register RULED)** | The frozen sheet §9 rules the register — *"the eternal hiss of wind... under it, nothing. The wild has no voice, only posture"* (2026-09-07) — no SoundDef, no ambient, nothing built. |
| 8 | Interesting weather | **MISS (names RULED 2026-09-21)** | **The Stall and the Gale are locked player-facing names "ahead of their WeatherDefs being built"** — still no WeatherDefs. Worse, the def's stock weather list leaves ban 5 (every ordinary day carries wind) unenforced. |
| 9 | Relationship to the gods | **MISS** | No ideoligion/lore-layer content. The sheet's calling-pyre (§4, a Pyrrhic last rite *"spoken of the way sailors speak of running aground on purpose"*) is the obvious hook, unbuilt and never wired to any precept. |

Score as built: **3 HAVE / 1 PARTIAL / 5 MISS** — consistent with the program table's
"content today: 2". The distinctive fact: an unusually deep bench of RULED-but-unbuilt
design (Stall/Gale, smother-craft, V-blight, calling-pyre, ripple, fire-stamping — all
frozen-sheet law since 2026-09-07), so movement 3 here is less invention than incarnation.

## The Blurrg sitting row — the owner's, not a fill

**Where it stands today (all MEASURED this pass):**

- `rosters/arid_shrubland.json` carries it in **evictions** as the only
  `"disposition": "homeless-reserve"` row: *"ban 4 large-band void: bs 2.5 (MEASURED);
  predator-flag conflict noted at desert.json"*.
- Long Shade sitting, ruled 2026-09-27 (Q8): **"Blurrg OUT (keeps a home for the Leaning
  Scrub sitting)"** — the reservation is live and this sitting is where it lands.
  `desert.json`'s confidence blob records the same: *"Blurrg's twin CONFLICT is closed —
  ruled OUT, reserved for the Leaning Scrub sitting"*.
- **No `RSW_Blurrg` port exists** (git grep over src/: zero), no canon_references entry
  (`find -iname '*blurrg*'`: none — absence proves nothing about canon; the Blurrg is
  genuine canon, the Mandalorian's mount), **no artpipe job ever filed** (registry: 0
  hits; probe fuzz=10/imperialtoad=12). The only def is the donor's bare `Blurrg`
  (mlie.starwarsanimalcollection), wired into no biome of ours.

**What admitting it costs:**

1. **A ruling against the frozen sheet's ban 4.** bs 2.5 sits square in the large-band
   void (1.5–3.5), a hard ban with its own numeric amendment. Options for the card:
   (a) admit as **tamed-only** — trader/quest/starting-mount stock, never a `wildAnimals`
   row, which threads the ban's own wording (*"no RESIDENT creature in the LARGE band"*)
   and matches its canon read as a ridden work-beast; (b) an owner waiver amending the
   frozen sheet at this sitting (the legal unfreeze path); (c) decline again — but Long
   Shade Q8 forecloses "somewhere else": this was the home being kept.
2. **Canon routes through the RSW/Utinni layer (Q11/Q11a)** — an `RSW_Blurrg` port in
   SWBestiary plus a `WildAnimals_LeaningScrub.xml` row (or livestock/trader wiring),
   never the RM def. The free `RM_LeaningScrub` looks identical minus the Blurrg.
3. **A canon_references entry before art** (canon library is the acceptance target),
   then either the donor's loose PNGs or an artpipe regen judged against it.
4. **Measure the predator flag first** (the roster's own suspicion: it reads as an
   omnivore mount; flag noise) — same treatment the Dewback got at the Long Shade
   sitting. Note spd 5.0 was flagged at desert.json under Long Shade's pursuit ban;
   *this* sheet has no speed ban, so only ban 4 binds here.
5. **The one-home law is satisfied by construction** — Long Shade already ruled itself
   out; no other biome claims it.

## Roster gaps + Proposed fills

### The Q11a hole, stated plainly

**The free-tier `RM_LeaningScrub` fields ZERO standalone creatures.** All 5 inline fauna
rows are MayRequire-gated donors (Terrorworm + 4 Alpha Animals) and all 39 campaign rows
ride the Utinni patch — with no donors installed the plain spawns no animal at all. Q11a's
bar ("rich enough to stand alone; the free mod looks the same as the campaign one") fails
harder here than anywhere: even the biome's own invented signatures (thunderstep, yanker,
scrap-nest bird) were born `RSW_` with donor-reskin art, so not one reaches the free tier.
Flora is healthier: 6 owned defs stand alone (`RM_Fuzz`, grellbush, grellspine, wild
healroot, venomvine thicket, sweetline tree), though the 5 RG_/Nysyllin donor rows carry
no MayRequire (disclosed copy-through gap) and 10 of 11 rows still violate ban 9
(flammability) — the fills below are the permanent fix the roster's own notes said no
donor could provide.

Other sitting rows found (adjudicate there, nothing done):
- `VAEWaste_Hydra` 0.5 sits in roster fauna but is wired NOWHERE (not in the twin, not in
  the patch) — a dead import row, same shape as desert.json's AA_SandLion (ruled dead at
  its sitting).
- Ban 7 vs the def: the sheet outlaws open sand on core shrubland ("root-bound crust");
  both twins open with `Sand` below fertility 0.45. An owned crust terrain def is the fix
  and pairs with any V-blight mechanic (the blight's wake = the one legal barrens).
- The fuzz's player-facing name is still the owner's (ARIDSHRUBLAND_SHIPPING_NAMES_1,
  live) — nothing below touches it.
- Accent finding: this biome's ruled register is **English compounds** (thunderstep,
  yanker, venomvine, sweetline, the Stall, the Gale) — accent-doc rule 7 ("a biome whose
  cast already carries ruled names keeps THAT accent") points AWAY from the Desert's
  doubled-consonant coinage, and the accent doc's own remains-table lists arid_shrubland
  as 3 rows in scope (imperial toad, moss beetle, hydra), no coined batch ever drafted
  for it. Fills below therefore lead with the English-compound register and carry one
  coined alternate each for the card.

### Proposed fills — 4 NEW invented creatures, RM_ tier, one home each

All collision-swept this pass (`git grep -il` over src/ + design/ + infrastructure/;
sanity probe `korrum` = 79 files; every primary = 0 files except thornhold's 1, which is the sheet's own niche line). First-draft alternates *skirra*/*vekkit*/*hurrik* were CAUGHT by the sweep (skirrak = ruled Wolfscarab name; **vekkit = a live Blue Desert creature**, 44 files; Hurrikaine crystals) and replaced with swept-clean *surrik*/*tokkit*/*zellik* (0 files each; *shokka* clean). Each fills a
sheet-named niche no wired species incarnates in the free tier, and respects the size
ladder (small / medium ≤1.4 / VOID / huge).

| # | name (alt) | band | the creature |
|---|---|---|---|
| 1 | **fuzzrunner** (*surrik*) | small ~0.2 | The runway nation's staple: a fog-fat tunnel-hare that never stands in open light, worn runs under the canopy, freezes on the Stall. The prey base every interface predator implies — and the free tier's first animal. Herd-spooks propagate down the runs (cheap: existing alarm-comp shapes). |
| 2 | **thornhold** (*tokkit*) | small ~0.4, venom | Incarnates the sheet's own noun ("thornhold nesters", §4 — the 1 grep hit IS that line): a venom-armed nester that forbids rather than flees, denning inside venomvine where nothing big can follow. Tameable late = living perimeter alarm. |
| 3 | **wakestalker** (*shokka*) | medium 1.2 | The edge-pouncer of the fog-shadow barrens — the deadly-crossing predator the sheet names as route 1 of 3 and nobody built. Waits where a runway is forced to surface; pelt sells as the local camouflage weave. |
| 4 | **stallhawk** (*zellik*) | medium 0.9, TRUE FLYER | The ripple-reader: hunts by canopy twitch, useless in wind, lethal in the Stall — it rises the moment the map's wind dies. Real core-1.6 flight (`MaxFlightTime`/flip-book owed per the flyer law). The creature that makes the Stall legible as horror. |

Each is invented (free to live in RM_ per Q11a), single-homed here, and none reuses a
neighbour's cast. With these four the free tier fields small herbivore + small venom +
medium ambusher + medium flier: a working food web under and over the fuzz, giants still
supplied by the campaign layer until the thunderstep's tier/art question is put to the
owner (a card worth asking at this sitting: thunderstep and yanker carry invented names —
Q11a would let RM_ twins of them anchor the free tier once they get own art instead of
Fambaa/Horax reskins).

### Art already generated — never re-queue (searched by BOTH spellings)

Finished, validated artpipe output exists under the OLD `RUT_` subjects for exactly the
defs whose RM_ headers say "zero PNGs anywhere": **`rutfuzz_v1`, `rut_grellbush`,
`rut_grellspine`, `rut_wildhealroot`, `rmvenomvine_v1`** — all present in
`infrastructure/artpipe/done/` + `_artsrc/` (probe: fuzz 10 registry lines,
imperialtoad 12). The owed work is *wiring/renaming* those renders onto the RM_ texPaths,
not generating. Nothing exists for: sweetline wool, scrap-nest bird, tunnel snake,
shrubland giant (all donor-reskin or missing), Blurrg.

## Candidate mechanics slate — ranked, aimed at the MISSes

**The name is the hint taken seriously: everything here LEANS.** The biome has one fixed
axis — light from the sunward horizon, water on the wind from the darkward one, every
plant bent the same way — so its signature mechanic family is *directionality*: a plain
where compass orientation is gameplay, and where the one variable that ever changes is
the wind. None of the spines below reuse Blue Desert detonation, Cracked Lands water,
Cauldron gas/filter/loud-ground, Forge freeze-melt, Pyrelands fire-calendar, or Miasma
vermin.

1. **The Stall and the Gale — the wind calendar** *(marks 8+7+1; names RULED 2026-09-21,
   unbuilt)*. Two owned WeatherDefs plus a map wind-state the whole biome reads: an
   ordinary day always carries wind (ban 5 finally enforced); the **Stall** kills it —
   ambient sound cuts to true silence, every small creature freezes, the stallhawk
   rises, and any pawn moving under the fuzz is lit up to predators and raider scouts
   alike; the **Gale** whites the canopy out — hearing/speech shot, turbines surge past
   capacity (breakdown risk with the surplus), **and raids ride it** (raid-arrival
   weighting toward Gale windows — the sheet's own "the wind gauge on every wall").
   *Uniqueness:* no biome runs weather as a stealth/raid clock. *Engine:* WeatherDefs +
   GameCondition + a MapComponent reading `WindManager`; raid weighting via
   StorytellerComp or IncidentWorker prefilter. *Trade-off:* the runway-freeze AI is
   cosmetic in v1 (stat offsets only) or it balloons; ship stat effects first.
2. **The Lean — one true direction** *(mark 1; the name-mechanic)*. Each map locks a
   wind vector (darkward→sunward). Scent and detection travel downwind — predators and
   raider dogs smell you from downwind, hunters approach from upwind or spook the prey;
   fire races downwind and creeps upwind; built windbreaks cast calm wakes (microcells
   where the ripple, the fog harvest and the concealment all change). Base layout
   becomes a bet on a compass direction. *Uniqueness:* no other biome makes orientation
   itself the resource. *Engine:* fixed map wind heading + a directional multiplier in
   hunt/spook checks and fire spread chance; wake cells from an occlusion sweep, the
   same shape as the V-blight below. *Trade-off:* touchs hunting AI; scope v1 to
   animals-smell-pawns and fire bias, both local patches.
3. **Gravship: the tallest thing on the plain** *(mark 6)*. A landed gravship is the
   only object above knee height for a horizon in every direction — so the biome treats
   it as a landform: it casts a real wind-shadow (a calm wake where fog-fat flora
   greens and runway nations move in — free hunting, and thornholds nesting in your
   hull's lee), while the wake's far edge dries to a pale barrens crescent; and at
   spool-up the engine reads as FIRE to the plain — **thunderstep herds converge on a
   launching ship** to stamp the burn, so leaving is an event you schedule around the
   herds, or a Gale you gamble on. *Uniqueness:* every other biome threatens the ship;
   this one *reads* it, in the sheet's own indifferent-giants voice. *Engine:*
   MapComponent keyed on GravEngine presence; terrain/plant-growth modifiers in two
   arcs; enrage reuses the shipped comp shape (fire-response variant). *Trade-off:*
   launch-blocking must never hard-lock — herds delay/damage, never forbid.
4. **The vaporator and the V-blight** *(marks 2+3)*. Buildable moisture farming: water
   and a thin food margin anywhere you stand — and every vaporator dries a V-shaped
   wake downwind (owned crust→barrens terrain morph over days; fixes ban 7 with an
   owned terrain while it's at it): automatic firebreak, automatic sightline moat, and
   an ecological grievance — wild animals raid vaporators like an oasis. The
   discoverable tech: studying a dead farmstead or a sweetline tree teaches the
   pattern. *Uniqueness:* Cracked Lands owns *finding* water; this is *making* it, and
   paying in land. *Engine:* building + MapComponent terrain swap in a cone; animal
   "raid the oasis" via existing need-driven job targeting. *Trade-off:* terrain morphs
   must cap and heal, or a long game strip-mines the map.
5. **The smother-craft** *(marks 2+3)*. The venomvine industry the sheet already wrote:
   weave smother-blankets (fuzz fiber + giant-wool), blanket a thicket (a job; the
   stand becomes a banked claim), wait seasons, harvest **dead venomvine — the finest
   fuel in the region** from a plant that spent its life refusing to burn. A
   multi-season investment economy nobody else has. *Engine:* item + job +
   CompTickLong timer hediff-equivalent on the plant (Scribe the timestamp).
   *Trade-off:* payoff timers must survive save/load and read legibly (inspect string
   with a countdown), or players never trust it.
6. **The calling-pyre** *(marks 9+1)*. The gods-layer: fire implies folly, the giants
   are the plain's indifferent gods, and the calling-pyre is the biome's one prayer —
   an Ideology ritual that torches your own fields to bring the thunderstep herds down
   on ALL who remain, attacker and defender alike. Precept variants: forbidden /
   last-rite / venerated. *Uniqueness:* the only biome whose "relationship to the
   gods" is summoning an ecology onto yourself. *Engine:* RitualBehaviorDef + the
   fire-stamping response below; the herd does the rest. *Trade-off:* needs 7 built
   first; Pyrelands owns fire-as-calendar, so this stays fire-as-*summons*, one ritual,
   no fire economy.
7. **Fire-stamping giants** *(mark 1 support; frozen-sheet law §4)*. Any fire above a
   threshold pulls grazing thunderstep herds to stamp it dead — then stamp its source.
   Raiders' firewall tactic becomes a self-beacon; your own hearth discipline matters.
   Prerequisite spine for 3 and 6. *Engine:* MapComponent fire census + a targeted
   mental-state on the herd (the shipped parental-enrage shape, fire-keyed).
   *Trade-off:* must exempt enclosed/roofed fires or every stove summons gods.
8. **The ripple — canopy concealment** *(mark 1 deepening; sheet §4, feasibility listed
   in the sheet's own Owed)*. Anything ≤ small under the fuzz is concealed from
   targeting beyond short range — except during the Stall, when moving cancels it
   map-wide; the Gale doubles it. Pawns crawling(prone-adjacent, or just "walking low"
   stance flag) borrow a weak version. *Uniqueness:* cover as a *weather-keyed field*,
   not a wall. *Engine:* stat part on concealment/hit-chance reading plant cover +
   wind state — pairs 1:1 with `colony_visibility_stat.md`. *Trade-off:* silently
   strong; needs a visible UI cue (shimmer overlay) or it reads as misses-for-no-reason.
9. **Named sweetline trees + tree-guardians** *(marks 3+9; owner candidate already live
   as `SHRUBLAND_TREE_GUARDIAN_1` — this slate ranks it, doesn't refile it)*. Every map
   sweetline tree spawns named, snags harvestable giant-wool on a respawn timer, and
   hosts a guardian unique that ignores you until you touch the tree. Roads and lore
   hang off named trees later. *Trade-off:* uniques-per-tree needs a spawn budget;
   one guardian species, named instances, is the cheap true version.
10. **The soundscape shipped as content** *(mark 7)*. Biome ambient = the hiss, layered
    by wind state; the wild has NO creature calls by def (soundCall stripped on
    residents); the Stall is the engine's rarest sound — silence as an alarm every
    player learns in one sitting. *Engine:* SoundDef ambients keyed off the weather
    defs from 1; cheap, ships with it. *Trade-off:* none worth naming — it rides
    slate #1.

**Recommended volley opener (movement 3):** 1 + 2 + 3 as the biome's spine ("the wind is
the clock, the compass is the bet, the ship is a landform"), 4 + 5 as the economy pair,
6 + 7 as the gods pair, 8–10 riding along. Slate #1 unlocks four marks by itself.
