You are a senior game designer consulting on a RimWorld mod campaign. The owner wants recommendations to ENRICH one biome that has already been through a design sitting. Be concrete, vivid and buildable in RimWorld 1.6 (XML defs, C# comps, Harmony, incidents, map components, weather, sounds).

BIOME: The Leaning Scrub

Standing rules of this project (binding on every recommendation):
- RimWorld 1.6 with ALL five DLCs assumed present; a Star Wars (old Tatooine / Jawa scavenger clan) campaign on one hand-made fixed planet. No worldgen, no alternative planets.
- Each animal lives in ONE biome unless there is an in-game reason (migration, life stage).
- Invented exotic names are fine; genuine Star Wars canon goes in a separate Star Wars layer.
- Heat is ONE planet-wide kind riding vanilla heatstroke; biomes differ by heat kind (overhead sun, low sun, ambient steam/volcanic).
- Animals or pawns must never vanish without a readable sign of what happened.
- If it flies in the fiction, it flies in the game.
- Every mod ships real Mod Settings.
- A biome's ideas must NOT echo another biome's signature; each biome has its own voice.
- The "bedazzle" bar is nine marks: unique mechanic, discoverable technology, unique resources, surprising creatures, a GIANT beast, a gravship touch, an interesting soundscape, interesting weather, a relationship to the gods.

WHAT THE OWNER HAS ALREADY RULED for this biome (ledger, verbatim; do NOT contradict or re-propose anything cut here):
- 2026-09-29: VOLLEY TURN 2, owner typed. Ruling 1: "No, we dont need a downwind lee around the ship." - slate 3 wind-shadow/lee CUT (herds-converge-on-launch half not addressed, carried to turn 3 flagged). Ruling 2: "yes Blurrg here." - Blurrg ADMITTED to Leaning Scrub, threads frozen ban 4; port chain owed (RSW port, canon entry, art). Ruling 3: "Mix up the Starwars-esque and compound word names." Ruling 4: "Regen all art to become our own." - every donor-reskin in this biome cast gets owned art.
- 2026-09-29: Ruling 5, cast expansion, owner verbatim: "Needs a lot of different kinds of fuzz (grassy, mossy, bushy, lichen-like, etc.). Needs a lot more creatures of all sorts. Good place for snake-like analogs, maybe even some brittlestar-like weirdness. Flapping, gliding creatures (flutterers) that rise up and land elsewhere when disturbed. Good place for bugs too."
- 2026-09-29: Ruling 6, venomvine showpiece, owner verbatim: "The art for the venomvine should be especially rich, varied, interesting... its the strange showpiece here. Maybe one variant of it can be a dripping kind that is overproducing the venom and thus can be harvested. Another kind could be a Twitcher, that when you get near lashes out and strikes you once."
- 2026-09-29: TURN 4a, owner typed: "Yes in 1. 2) not needed." - the ENTIRE mechanics slate spine is ADMITTED (Stall+Gale, the Lean, vaporator/V-blight, smother-craft, calling-pyre + fire-stamping giants, the ripple, soundscape); herds-converge-on-launch CUT, so mark 6 gravship touch is fully cut for this biome, owner-accepted miss. Ban-4 explanation + Blurrg admission route card delivered; enrichment pass (his "make it richer") delivered same turn.
- 2026-09-29: Blurrg route: decision taken by question card 2026-09-28 - TAMED-ONLY (traders/scenarios/quests, never wild). Threads frozen ban 4 as written; no sheet amendment needed. Port chain still owed: RSW_Blurrg port via Utinni layer, canon_references entry, own art. Enrichment pass delivered in-window (fuzz mosaic jobs, creature interaction web, five-form venomvine family incl. Hollow + Crown); awaiting owner final ruling to ticket out.
- 2026-09-29: TURN 5 FINAL, owner typed: "Too much focus on constant advanced warning. They enough of that theme. Players arent that into it. A rich soundscape of bugs and birds and stranger animals in the wind. Lots of inhabited injections all over here from ruins to current living denizens. Ok. Ticket out and record everywhere, then finish fully and hand off." RULINGS: warning-instrument framing TRIMMED everywhere (creatures/ecology stay, radar/alarm framings go); soundscape REVERSED from silence-and-alarm to RICH ambient calls (bugs, birds, stranger animals in the wind) - the earlier no-creature-calls slate line is dead; inhabited injections commissioned (ruins through living denizens, all over). Volley closed; ticket-out + handoff proceeding.
- 2026-09-29: Movement 4 commission DONE (31ef2aa43): cast bible leaningscrub_bedazzle_cast_2026-09-29.md + 61 art jobs queued across 27 subjects (fills 12, menagerie 28 incl. vissler arm item, fuzz 4, venomvine showpiece 5 incl. FRESH base - rmvenomvine_v1 fails the bar, it is the Long Shade ankle-mat silhouette, and the shared RM_Venomvine/RM_VenomvineThicket texPath must SPLIT when the v2 lands, bible section 11; regen-all 9 - yanker and tunnel snake are ONE def; Blurrg 3). 5 wire-only, 36 donor-reskins already have finished owned sets in done/. Sitting now open for ART REVIEW only - all four movements complete.

THE BIOME'S DESIGN DOCS:
===== design/Jawa/worldbuilding/biomes/leaningscrub_bedazzle_review_2026-09-29.md =====
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


===== design/Jawa/worldbuilding/biomes/leaningscrub_bedazzle_cast_2026-09-29.md =====
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

## 4. Cast entries — the nine menagerie

All nine ruled at the sitting (swept clean 2026-09-28, probe korrum 70). One home each.
Compact entries; the shared law of §0 rides every one.

### RM_Fuzzviper — the run-ambusher

> The runs are safety, and the fuzzviper is the price of believing that. It lies along a
> tunnel wall being a root until the run's own traffic comes to it.

**Silhouette/palette:** a thick-bodied short snake-analog, coiled S-posture, head flat
against the ground; **anchor: CANOPY-MIMIC** — exactly the fuzz's silver-green with
stem-shadow banding, the one cast member deliberately painted the room's own colour (the
point of it). Facings south/east/north (north = dorsal coil from behind). Canvas 256.
drawSize ~0.9, bodySize ~0.3; ambush predator of the runs.

### RM_Surrik — the crust-swimmer

> Below the runs there is one more floor. The surrik swims the root-bound crust itself,
> shouldering through the mat like water, and takes what it takes from underneath.

**Silhouette/palette:** a blunt-headed, thick-necked burrowing snake-analog surfacing
chest-up through cracked crust, tiny useless eyes, polished scales; **anchor:
LOAM-DARK** — deep root-brown body with a pale crust-dust back where it wears the
ground, root-pale belly. Facings south/east/north. Canvas 256. drawSize ~1.0, bodySize
~0.5; subterranean predator, surfaces to strike.

### RM_Ribbonwhip — the canopy-top thread

> The thinnest predator on the plain never touches the ground: a ribbon the width of a
> stem, riding the top of the canopy, moving when the wind moves so nothing reads it.

**Silhouette/palette:** an impossibly slender thread-snake laid in a long shallow wave
across the canopy top, head barely wider than the body; **anchor: WAXY-GOLD** — sunward
waxy gold with a silver sheen down the flank, bright against the cast, matched to the
sunward band of the fuzz. Facings south/east/north. Canvas 256. drawSize ~1.1 (length,
not mass), bodySize ~0.25; takes flutterers and nestlings off the canopy top.

### RM_Vissler — the brittlestar of the runs (+ the shed arm)

> Grab a vissler and you are holding an arm. The rest of it is already gone, and the arm
> is still moving — twitching in the run with a will of its own, and everything hungry
> comes to the twitch. It regrows the arm in a season. Hunters buy them.

**Silhouette/palette:** a five-armed ground brittlestar, central disc low and armored,
arms long and jointed like braided whips, one arm visibly regrowing (shorter, paler);
**anchor: LICHEN-GREY over EMBER CORE** — dry lichen-grey armor plates, joint-lines
glowing faint ember-orange where the living core shows. In the Gale, visslers interlock
into star mats — the sprite is ONE animal; the mat is a spawning behaviour, not this
job. Facings south/east/north. Canvas 256. drawSize ~0.9, bodySize ~0.15.

**RM_VisslerArm (item, single):** the shed arm as a harvestable hunter's lure — a curled,
jointed whip-arm, lichen-grey plates with the ember joint-glow fading toward the broken
end. Item icon read: unmistakably a piece of the animal, still coiled with intent.
Canvas 256, single. (Lure mechanics ride the build ticket, not this commission.)

### RM_Dustflutter — flight as displacement

> Walk the fuzz and the ground ahead of you bursts — a hundred dustflutters up in one
> grey shiver, over your head, and down again forty paces on. They cannot really fly.
> They can only be somewhere else.

**Silhouette/palette:** a palm-sized round-bodied flutterer, wide soft moth-like wings,
almost no tail, mid-burst posture with legs still trailing; **anchor: MOTH-DUST** —
ash-buff body, fog-white wing undersides that flash as the flock turns, faint dark
wing-root crescents. TINY `MaxFlightTime` — flight as displacement, not travel; frames
are the same named follow-on as the zellik's (§10). Facings south/east/north. Canvas
256. drawSize ~0.6, bodySize ~0.08; flock-common, mobs the crown venomvine when the
wind drops (wind-keyed, never day-keyed — ban 3).

### RM_Shirrel — the Gale-glider

> Most of the plain spends a gale hiding. The shirrel spends the year waiting for one.
> It climbs a sweetline tree, opens like a kite, and crosses country in an afternoon
> that would take it a season on foot.

**Silhouette/palette:** a big heavy-bodied glider — cat-sized, a full body-length
gliding membrane furled along the flanks (grounded sprite: membrane folded in loose
pleats), strong climbing claws, a deep-keeled chest; **anchor: STORM-GREY** — charcoal
body with the furled membrane in banded slate and fog-white, like weather rolled up.
Facings south/east/north. Canvas 256. drawSize ~1.2, bodySize ~0.7; rises on the Gale
(mechanics own the wiring), sweetline-tree associate.

### RM_Crustweevil — the lichen grazer

> The crust is a country too. The crustweevil grazes its lichens on a scale of
> centimeters, and the runway nations grow fat on the crustweevil.

**Silhouette/palette:** a domed, long-snouted weevil, legs hidden under the shell rim,
snout down against the ground; **anchor: OXIDE-SHEEN** — near-black shell with an oily
blue-green oxide iridescence, dusted pale at the dome crown. Facings south/east/north.
Canvas 256. drawSize ~0.5, bodySize ~0.05; base of the invertebrate web.

### RM_Rollbug — the run janitor

> Nothing dies in a run and stays there. The rollbug trundles the corridors on a fixed
> beat, packs whatever it finds into a ball bigger than itself, and rolls the runway
> clean back to its larder.

**Silhouette/palette:** a broad flat-backed beetle-analog pushing with its hind legs,
head low, forebody braced (sprite WITHOUT the ball — the animal must read alone);
**anchor: TAR-POLISH** — deep tar-brown chitin polished to a shine on the wear-points,
dull dust film elsewhere. Facings south/east/north. Canvas 256. drawSize ~0.55,
bodySize ~0.06; carrion/waste feeder.

### RM_Tikkit — the click-chorus

> The plain is not silent, whatever the old surveys say — put your head under the canopy
> and it clicks, horizon to horizon, a dry chorus riding the wind. That is the tikkit
> nation talking to itself. About what, nobody has ever needed to know.

**Silhouette/palette:** a slight, long-legged cricket-analog, big-eyed, serrated
click-limbs half-raised; **anchor: DRY-GRASS** — dried-grass tan with dark banding on
the click-limbs and a pale throat. Soundscape richness is the point
(`LEANINGSCRUB_MECHANICS_BUILD_1` §7) — 🔴 NOT a warning device, and its entry text
never frames the chorus as one. Facings south/east/north. Canvas 256. drawSize ~0.5,
bodySize ~0.04; swarm-common, the click-chorus ambient's face.

## 5. Cast entries — the four fuzz flora

All four ban-9 compliant by ruling (fire-resistant living flora — the permanent fix the
roster's own notes said no donor could provide). All single-facing plant sprites;
Graphic_Random variants derive from each master. Every prompt carries the lean: the
whole plant bent the same way, permanently.

### RM_Whipfuzz — the grassy fuzz

> The between-plant grass of the quincunx: thin silver blades that lie almost flat in
> the wind and never stop moving.

**Palette anchor: SILVER-GREEN** — the biome's signature register, carried by exactly
one plant so the rest of the flora is free to differ: pale silver-green blades, darker
at the root, all bent sunward. Sparse, struggling, never a lush tuft (quincunx law —
the gaps are the structure). Canvas 256, single. drawSize ~1.0.

### RM_Pillowmoss — the fog-condenser

> A fat, low cushion that drinks the wind — fog beads on it all day, and the ground
> under a pillowmoss is the only reliably wet ground on the plain.

**Palette anchor: DEEP FOG-GREEN with DEW-SILVER** — the darkest green in the cast,
dense wet-looking pile, beaded with condensed silver droplets on the windward face
(vaporator synergy lives in MECHANICS; the art only shows a plant that drinks fog).
Canvas 256, single. drawSize ~0.8; low dome, leans barely — too low for the wind to
bully.

### RM_Tanglefuzz — the den anchor

> Where a tanglefuzz grows the runs converge: a woody, knotted bush whose root-ball
> holds a hollow, and half the runway nation is dug in under one.

**Palette anchor: DUSKY OLIVE over DARK HEART** — grey-olive foliage over a visibly
woody, near-black knotted core and exposed root-flare (the den mouth shadowed at the
base, readable at zoom). The biggest of the four; still knee-high, still leaning.
Canvas 256, single. drawSize ~1.2.

### RM_Cruststar — the crust lichen

> A hand-span star of pale lichen flat against the root-bound crust, rimmed gold where
> it fruits. The crustweevils graze it like a herd on a pasture the size of a plate.

**Palette anchor: LICHEN-WHITE and GOLD RIM** — chalk-pale rosette, thin waxy-gold
fruiting rim, pressed dead flat (the one plant the wind cannot lean because it has no
height at all). Canvas 256, single. drawSize ~0.6.

## 6. The venomvine five-form showpiece

🔴 **Owner verbatim — this is the art centerpiece:** *"The art for the venomvine should
be especially rich, varied, interesting... its the strange showpiece here."* Five forms,
five entries, five renders — one family, one near-black register, and deliberate
variety inside it.

### The base thicket — verdict on `rmvenomvine_v1`: DOES NOT MEET THE BAR; fresh base QUEUED

**MEASURED this pass:** `rmvenomvine_v1` (done/, facts PASS, wired 2026-09-26 as
`RM_Venomvine/RM_Venomvine_a.png`) was authored for **the desert shade-vine ruling**,
and its own prompt forbids exactly what this biome's venomvine IS: *"a low, matted
tangle... sprawling flat across the ground... nothing stands tall... an ankle-high
thicket rather than a bush... It is a ground-hugging mat, never a standing shrub."*
The frozen sheet's ruling (owner, 2026-09-21) is the opposite: **venomvine stands
man-height or more** — the only vegetation in the biome that does, the reason a thicket
reads as a dungeon and a hedge-fort is a curtain wall. The render also carries a heavy
black outline register the current house style has dropped. It is not a richness
shortfall to iterate on; it is the wrong plant's silhouette. ⇒ **A fresh base
`RM_VenomvineThicket` render is queued**; `rmvenomvine_v1` stays valid where it was
made for (`RM_Venomvine`, the Long Shade ground mat) and comes OFF this biome's
wire-only list. ⚠️ Both defs share one texPath today *on purpose* (each def's header
says so) — FOUNDRY must split the thicket onto its own texPath when the new render
lands, or the desert mat inherits a man-height sprite. Handoff note §11.

### RM_VenomvineThicket — the fortress (fresh base)

> The one plant that refuses the quincunx. A mature stand is a dungeon: near-black
> canes man-height and better, woven too dense to cut, venom on every scratch, and
> everything the plain wants — nests, dens, shade, secrets — locked inside where only
> the small can thread.

**Silhouette/palette:** a standing thicket WALL, not a bush — vertical woven canes
rising past man-height, recurved thorns in ranks, one narrow dark threading-gap
readable low; **anchor: NEAR-BLACK ISLAND** — blackened green-umber canes, bone-pale
thorn tips, the darkest mass in the biome (the sheet's "venomvine as near-black
islands"). Leans sunward like everything else, which on a plant this size reads as
menace. Canvas 256, single. drawSize ~2.2.

### RM_DrippingVenomvine — the overproducer

> Some stands make more venom than their thorns can hold. A dripping stand hangs it in
> amber beads along every cane, and the harvest is real money for whoever works
> bare-headed under a plant that sweats poison.

**Silhouette/palette:** the base thicket form hung with visible bead-strings of venom
along the cane undersides, ground beneath faintly stained; **anchor: AMBER ON BLACK** —
the family near-black plus the cast's one jewel note: translucent amber-gold drops,
lit. (Harvest job → raw venom stock rides `LEANINGSCRUB_RULED_CONTENT_1` §4.)
Canvas 256, single. drawSize ~2.2.

### RM_TwitcherVenomvine — the lash

> A twitcher stand strikes once at whatever comes close — one whip-crack of a cane,
> fast as a snake — and then spends an hour drooping, visibly spent, earning the next
> one.

**Silhouette/palette:** the family form with ONE long lash-cane held cocked in a
drawn-back arc above the mass, the surrounding canes slack; **anchor: GREY-GREEN
FLUSH** — near-black body but the lash-cane flushed a live grey-green along its length
(the working muscle, the one green note in the family). The visible recovery droop is
the def's other state — a retint/derive, not a second commission. (⛔ The lash is a
MapComponent, never a plant CompTick — plants only TickLong; mechanics ticket §9.)
Canvas 256, single. drawSize ~2.2.

### RM_HollowVenomvine — the grown gates

> Old stands die from the inside and stand anyway: tubes of grey cane, galleries wide
> enough that the runway nations thread them like streets — and a person the Jawas'
> size can crawl where the streets go.

**Silhouette/palette:** aged tubular architecture — the thicket as a cluster of open
weathered tubes, dark gallery mouths readable at zoom, thorns worn blunt; **anchor:
DRIFTWOOD-GREY** — the family's black weathered out to silvered grey, the palest form,
age made visible. Canvas 256, single. drawSize ~2.2.

### RM_CrownVenomvine — the flowering landmark

> Rarest of all: a stand that crowns. It climbs past man-height-and-more into a single
> black column and flowers at the top — the only flower this plain owns — and when the
> wind drops, the dustflutters mob it in a grey cloud you can see from a day's walk.

**Silhouette/palette:** a vertical landmark — the thicket drawn up into one leaning
column, crowned with a burst of pale-violet flowers; **anchor: VIOLET ON BLACK** — the
family near-black carrying the biome's single flower-colour, pale luminous violet,
nothing else in the cast may use it. Wind-keyed mobbing (⛔ no day/night dependency —
ban 3) is behaviour, not art. **Canvas 512** (landmark showpiece — it must carry at
map zoom the way the sweetline trees do), single. drawSize ~3.5.

## 7. The regen-all list (owner-typed: "Regen all art to become our own")

**Donor-reskin sweep (MEASURED this pass):** every PawnKindDef of the 39 patch-cast RSW_
species + RSW_ShrublandGiant read from `src/RimStarWars/SWBestiary/` — **all 40 declare
donor `swanimals/...` texPaths** (SWBestiary ships loose PNGs at those paths). The art
dedup (§2) then splits them:

**Queued — donor-reskin with NO owned render anywhere (0 done / 0 registry):**

| subject | today's donor skin | the regen brief |
|---|---|---|
| **RM_Thunderstep** (`RSW_ShrublandGiant`, bs 6.0) | Fambaa (`swanimals/Fambaa/`) — and `fambaa_v1` in done/ is the CANON Fambaa, not this animal | The huge grazer as the sheet paints it: *"giants as walking hills with lit flanks"* — a vast dun-and-slate grazing hill on pillar legs, raised long-necked head (the only sightline in the biome), wool snagging in sheets along the flanks, utterly indifferent posture. **Anchor: WALKING HILL** — dun hide, slate shadow mass, one lit flank in the low gold light. Same silhouette ROLE as today (huge quadruped grazer), our own animal. 512 canvas, 3 facings, drawSize ~7.0. |
| **RM_Yanker** (`RSW_TunnelSnake`) | Klorslug (`swanimals/Klorslug/`) | The corridor predator: long, thin, terrible, shaped exactly like the runs it hunts — a muscular tube of an animal, blunt armored ram of a head, mouth built to take prey head-on in a space with no sideways. **Anchor: CORRIDOR-DARK** — deep earth-umber above shading to root-black, pale gullet the only light. Same silhouette role (elongate tunnel serpent), ours. 256, 3 facings, drawSize ~1.8. |
| **RM_ScrapNestBird** (`RSW_ScrapNestBird`) | Whisperbird (`swanimals/Whisperbird/`) — shared with `RSW_Whisperbird`, TWO defs on ONE donor image today | The scavenger bird-analog of the vine: a wiry, quick, longer-necked diver with clever feet, built for threading thorns and carrying glitter. **Anchor: SOOT-AND-GLITTER** — dark soot plumage with oil-slick iridescent glints at throat and wing-edge (the magpie read: a thing that loves shine). Same silhouette role (medium bird-analog), ours — and it finally splits the two defs' art. 256, 3 facings, drawSize ~1.3. |

*(The ticket's four names resolve to three defs: "yanker" and "tunnel snake" are both
`RSW_TunnelSnake` — ruled name and def name of one creature.)*

**Job ids keep the live defNames as subjects** (`rsw_shrublandgiant_v1`,
`rsw_tunnelsnake_v1`, `rsw_scrapnestbird_v1`) so the dedup instrument finds them by
either spelling later; any RM_ re-tiering of these three is `LEANINGSCRUB_RULED_CONTENT_1`
def work, not an art id question.

**REGENS, not reskins — no `reference=` on any job** (standing law: reference triggers
reskin-validate); the existing silhouette/role is described in style_notes instead.

**Skipped — donor-reskin but a finished owned regen already exists (wire, don't regen):**
the remaining 36 cast members, each with a complete set in `done/` (census §2; e.g.
`desert_swaca_bantha` 3 facings, `canon_whisperbird_v1` 3 facings covering
`RSW_Whisperbird`, gizka 28 done-files, mossbeetle 18, iriaz 18, anooba 24, imperialtoad
6): FrilledGorg · Gorg · Iriaz · LongtailGorg · Eopie · Lothcat · Mudhorn · Ronto ·
Scurrier · Sketto · Kreetle · Igitz · Urusai · ImperialToad · Kybuck · Massiff · Bantha ·
Pufferpig · Anooba · Corinathoth · Gizka · Nuna · Worrt · MossBeetle · Grank · Qormot ·
Strill · Cannok · Whisperbird · Pikobis · Convor · Skalder · Vulptex · FeralNerf · Porg ·
Voorpak · KowakianMonkeyLizard. Queuing any of these would throw ruled work away.
⚠️ Whether each done set is actually WIRED over the donor pixels at the def's
`swanimals/` path was NOT verified per-subject here — that wiring audit is FOUNDRY's
(§11).

**Not regen candidates at all:** the 5 inline donor rows (`Terrorworm`, `AA_Cactipine`,
`AA_Needlepost`, `AA_Wildpawn`, `AA_Wildpod`) are RAW DONOR DEFS, not our reskins —
regenerating their art would not make them ours. Their fate is roster work at a sitting,
not an art queue (§11).

## 8. Blurrg — the tamed-only mount (canon subject)

**Ruled frame (fixed, card decision 2026-09-28):** TAMED-ONLY — never spawns wild, which
threads frozen ban 4 (large-band void, bs 2.5) as written. Arrives by trade, scenario or
quest. 🔴 **The `RSW_Blurrg` port (Utinni/RSW layer per Q11) and the `canon_references/`
entry are FOUNDRY/design owed** — neither exists yet (git grep: zero; canon entry: none).
Canon library law: the entry is the acceptance target, so **the render queued here is
judged against that entry once written** — the prompt is written from canon directly
(The Mandalorian; Wookieepedia-sourced at the review).

**Description:**

> A blurrg is two legs, one appetite, and a temper that respects exactly one thing:
> whoever broke it. Nothing about it belongs to this plain — it was carried here, the
> way saddles are — and the plain has not been consulted. Under a rider it will cross
> the fuzz at a pace nothing local cares to match, and at the picket line it will eat
> anything it is shown and several things it is not.

**Silhouette/palette brief:** the canon animal — a heavy bipedal reptilian mount: two
massive columnar legs, no functional forelimbs, a huge rounded body sloping to a thick
tapered tail, a broad blunt wide-mouthed head low on a short neck. **Anchor: CANON
HIDE** — mottled tan and grey-brown leathery hide, paler belly, dark mottling across the
back; canon appearance outranks palette invention (the diversity law is satisfied by
canon itself — nothing else in the cast is tan leather on two legs).

**Facings:** south, east, north (north = true rear: the great haunches and tail root, no
face). Canvas 256. **drawSize intent: ~2.4**, bodySize 2.5 (legal because tamed-only);
rideable, work-beast temperament.

## 9. Wire-only (validated renders under old RUT_ subjects — never queue; FOUNDRY wires)

| render (done/ + _artsrc/) | wires onto | note |
|---|---|---|
| `rutfuzz_v1` | `RM_Fuzz` texPath | THE signature canopy plant — zero PNGs on the RM_ def today |
| `rut_grellbush` | `RM_Grellbush` | ditto |
| `rut_grellspine` | `RM_Grellspine` | ditto |
| `rut_wildhealroot` | `RM_WildHealroot` | ditto |
| `rmvenomvine_v1` | **`RM_Venomvine` ONLY (already wired 2026-09-26)** | ⛔ NOT kept as the thicket base — §6 verdict. Comes OFF this biome's wire list; the fresh `RM_VenomvineThicket` render replaces it here, and the shared texPath must split (§11). |

## 10. Queued art — 27 subjects (17 faced sets + 10 singles), 61 job files — FILED, 0 refused

**CSV:** `infrastructure/artpipe/art_lists/leaningscrub_bedazzle_cast.csv` —
`rimflow_item_id LEANINGSCRUB_BEDAZZLE_SITTING_1`, channel codex, transparent,
priority 70, `reference` empty on every row (regens, never reskins). Queued via
`fill_queue.py` (derive-facings default: east is the master, north/south derive —
ARTPIPE_FACING_COHERENCE_1). Jobs land in `infrastructure/artpipe/pending/`; the daemon
claiming one is success.

| group | id | canvas | facings | anchor |
|---|---|---|---|---|
| fill | `RM_Fuzzrunner` | 256 | s,e,n | fog-silver |
| fill | `RM_Thornhold` | 256 | s,e,n | bone-and-venom |
| fill | `RM_Shokka` | 256 | s,e,n | barrens-dapple |
| fill | `RM_Zellik` | 256 | s,e,n | slate-and-glare (grounded only) |
| menagerie | `RM_Fuzzviper` | 256 | s,e,n | canopy-mimic |
| menagerie | `RM_Surrik` | 256 | s,e,n | loam-dark |
| menagerie | `RM_Ribbonwhip` | 256 | s,e,n | waxy-gold |
| menagerie | `RM_Vissler` | 256 | s,e,n | lichen-grey / ember core |
| menagerie | `RM_VisslerArm` | 256 | single | item — the shed lure |
| menagerie | `RM_Dustflutter` | 256 | s,e,n | moth-dust |
| menagerie | `RM_Shirrel` | 256 | s,e,n | storm-grey |
| menagerie | `RM_Crustweevil` | 256 | s,e,n | oxide-sheen |
| menagerie | `RM_Rollbug` | 256 | s,e,n | tar-polish |
| menagerie | `RM_Tikkit` | 256 | s,e,n | dry-grass |
| flora | `RM_Whipfuzz` | 256 | single | silver-green |
| flora | `RM_Pillowmoss` | 256 | single | fog-green / dew-silver |
| flora | `RM_Tanglefuzz` | 256 | single | dusky olive / dark heart |
| flora | `RM_Cruststar` | 256 | single | lichen-white / gold rim |
| venomvine | `RM_VenomvineThicket_v2` | 256 | single | near-black island (fresh base) |
| venomvine | `RM_DrippingVenomvine` | 256 | single | amber on black |
| venomvine | `RM_TwitcherVenomvine` | 256 | single | grey-green flush |
| venomvine | `RM_HollowVenomvine` | 256 | single | driftwood-grey |
| venomvine | `RM_CrownVenomvine` | **512** | single | violet on black (landmark) |
| regen | `rsw_shrublandgiant_v1` | **512** | s,e,n | walking hill (thunderstep) |
| regen | `rsw_tunnelsnake_v1` | 256 | s,e,n | corridor-dark (yanker) |
| regen | `rsw_scrapnestbird_v1` | 256 | s,e,n | soot-and-glitter |
| Blurrg | `rsw_blurrg_v1` | 256 | s,e,n | canon hide |

**Named follow-ons (not commissioned now, deliberately):**
- `RM_Zellik` flight flip-book frames (whole-body directional flip-book,
  `flyingAnimationFramePathPrefix` shape, Sparrow template) — the flyer law says never
  block flight on frames; file after the grounded sprite is accepted.
- `RM_Dustflutter` burst flip-book — same law, same shape, tiny frame count.
- `RM_TwitcherVenomvine` recovery-droop state — a derive/retint of the master once
  accepted, not a fresh commission.
- Vissler Gale star-mat — behaviour/spawning dressing, only if FOUNDRY wants a mat
  graphic at all.

## 11. Handoff notes (defects/finds observed — nothing filed, per this brief)

- **The thicket/mat texPath must SPLIT when `RM_VenomvineThicket_v2` lands.**
  `RM_Venomvine` and `RM_VenomvineThicket` share `Things/Plant/RM_Venomvine` *on
  purpose* today (each def's header says so, wired 2026-09-26). The fresh man-height
  base makes that sharing wrong in both directions — FOUNDRY gives the thicket its own
  texPath or the desert ground-mat inherits a man-height sprite.
- **`rmvenomvine_v1` is the Long Shade mat, not this biome's thicket** — its prompt
  hard-forbids standing ("never a standing shrub") while this biome's ruling is
  man-height-plus. Anyone about to wire it onto the thicket should read §6 first.
- **The 36-species wiring audit is real owed work:** every patch-cast def still declares
  a donor `swanimals/` texPath, and this pass did NOT verify per-subject that the
  finished owned regens (desert_swaca_*, canon_*_v1, etc.) were wired over the donor
  pixels at those paths. If they were not, the campaign is still showing donor art for
  species whose owned renders sit finished in `done/`. That audit belongs with
  `LEANINGSCRUB_RULED_CONTENT_1` §6's wire half / the absorption items.
- **`RSW_ScrapNestBird` and `RSW_Whisperbird` ship on ONE donor image today** — two
  species, one texture. `rsw_scrapnestbird_v1` splits them; the whisperbird side keeps
  `canon_whisperbird_v1` (already done).
- **The 5 inline donor fauna rows (Terrorworm + 4 AA_) are raw donor defs** — not
  reskins, so "regen to own" cannot apply; making them ours means new species or ports,
  a sitting/roster question, not art. Same family as the `VAEWaste_Hydra` dead row
  (UNRULED, strike-candidate, confirm with the owner at art review — ticket §7).
- **Blurrg render precedes its canon_references entry** (queued on the parent's
  explicit brief). The entry is design-owed; when written, the render is judged against
  it — if the entry's Must-show contradicts the render, the render loses.
- **Palette-diversity law is carried verbatim in every style_notes** of this cast's
  CSV — 27 sprite sets, no two sharing an anchor (the venomvine family shares its
  near-black REGISTER but each form carries a distinct accent by design). If a rendered
  batch comes back tonally uniform anyway, that is a prompt-adherence defect for the
  daemon channel, not a reason to re-rule the cast.
- **Trim law was applied to inherited prose:** the review's fill table called the
  thornhold a "living perimeter alarm" and the tikkit risked the same shape — both
  entries here carry the ecology only, per the final ruling. Nothing warning-flavored
  ships in any prompt or description in this bible.


TASK: Give 8 to 12 recommendations that would make The Leaning Scrub richer, more memorable and more distinct, filling the weakest of the nine marks first. Improve and extend what is ruled rather than restarting it. For each recommendation:
- **Name** and a one-line pitch
- What the player sees, hears and feels
- Which of the nine marks it lifts
- How it could be built in RimWorld 1.6 and a rough size (XML only / small C# / large C#)
- Why it belongs to THIS biome and no other

Then list your TOP 3 in rank order with one line of why each. Reply in Markdown, at most about 1500 words. Do not ask questions; do not modify any files.