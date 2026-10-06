# The Gelatinous Slime: bedazzle review (grandfathered sitting, turn 1 ruled and ticketed)

Program: `BEDAZZLE_TOP_SHAPE_PROGRAM_1`, track (a), worst-first, sitting 11. Item to be filed by the
parent (`GELATINOUSSLIME_SCORING_SITTING_1` shape).

_BENCH design pass, 2026-10-02. Eleventh sitting of the grandfathered track, in the order of
`grandfathered_bedazzle_scores_2026-10-01.md` (§ Gelatinous Slime; sitting order row 11), the one after the
Weeping Stones. The sheet `the_slime.md` is frozen (`BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07; amendments add
detail). Already ruled and **not re-argued here**: the biome and its four lobes; slimification at about a
week and the cure geography; slime rain as the body irrigating itself (the ruled carve-out from R-H1); the
cure that starts a clock; farms fail by conversion; the gene machine and the frozen gene lists
(`the_slime_gene_lists.md`, owner-accepted 2026-09-06); the Slime Pit; the farm ruins; the flying
aristocracy and the filter-feeder line (both *"owner's ruling"*); the titanoslime (owner's ask 2026-09-20);
the survivor mod (`mandrake.rm.gelatinousslime`, by card 2026-09-21); the 2026-09-24 slime-law names; and
**Q14** (by card 2026-09-23): the free def **stays donor-free** and its holes are filled with creatures of
ours. (The brief cited this as Q13; in `biome_mod_architecture.md` §7 Q13 is "duplicate, then diverge" and
Q14 is the Slime's.) The eight hard bans of sheet §6 bind every slate row; the ones that bite hardest:
**no sentience** (it only reads; the planet-eater stays a fear), **no meteorological rain**, **no
shelf-stable or remote gene extraction**, and **no re-arming**._

Sources read, all in the BENCH clone: `src/RimMandrake/GelatinousSlime/` (BiomeDef
`Defs/BiomeDefs/GelatinousSlime.xml`, every def file parsed, `About.xml`, the 12 `Source/*.cs` by grep, the
settings readers, the visitors' and the weather's headers, the two patches), the frozen twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Slime.xml`, `RUT_SlimeGrazer.xml`,
`RUT_SlimeGeneArchive.xml`, `Slime_Rename.xml`, every other file under `src/` naming the twin, our def or
the donor `AB_GelatinousSuperorganism` (`BiomeNames_Ashkarr.xml`, `BiomeDescriptions_Ashkarr.xml`,
`AncientDangerGenSteps_AmbientDoctrine.xml`, `FishTypesStrip_NoFishBiomes.xml`,
`BiomeCastEvictions_WildBiomes.xml`, `AnimalBiomeDuplicates_Generated.xml`, `JawaWorld_BiomeMix.xml`), the
sheet, the gene lists, `rosters/the_slime.json`, `noncanon_beast_names_crags_nightside_contagion_slime.md`
(batch 3d), `biome_mod_architecture.md` §4b and §7, the open items (`GELATINOUS_SLIME_FIRST_SCRIPT_1`,
`SLIME_SEEKER_LOAD_TOOL_1`), the register `design/Jawa/salvation_rites_2026-10-01.md`, the ledger's
2026-10-02 rulings (Lantern Deeps, Pyrelands, the Sump, Webwork, Greentide, Rust Cathedral, the Rot, the
Fever Wood), and the Weeping Stones review for shape. Rosters were parsed as XML elements; the creature
census reads descriptions; art was searched with `artpipe_state.py find`.

## 0. The Gelatinous Slime in plain words (for the card)

The Slime is a body the size of a country, lying in the mildest weather on the planet where the dead
rivers used to end. It was a weapon once. It ate everything it was sent against, read every genome it
ate, and was unmade by winning: now it only files. Its grass, its trees and its herds are all its own
flesh; there is no rock and no soil, only slime, from dry crust to running channels. Stand on it for a week
unprotected and it reads you so thoroughly that you become an entry and there is nothing left to bury.
Raw slime cures any poison you have swallowed and then starts on you, so you need an antidote. When it
is thirsty it sweats into the sky and pulls down a warm green rain that fills every barrel. Its herds are
small knee-high lobes that wander off and pool together at night, and its giant is a hill of green jelly
that swallows things whole to read them. Its one wonder is the gene seeker: pick a gene from everything
that ever touched it, walk out onto the body and stand in the current that carries it, and come home with
that gene plus one you did not choose, on a clock. The place makes no sound of its own, it does nothing to
your ship, no god is tied to it, and the campaign layer adds almost nothing on top of the free mod.

## 1. What is there: ruled vs built

### The richest free mechanic kit of the twelve, carried by two animals and borrowed art

`src/RimMandrake/GelatinousSlime/` (`mandrake.rm.gelatinousslime`, survivor by card 2026-09-21,
`SLIME_STANDALONE_MOD_1`; 12 C# files, about 3,900 lines) ships: its own biome worker with a rarity
slider; the five-step slime terrain ladder (hardened, rich, slime-grass, mud, liquid); **slimification**
(`HediffComp_Slimification`, four stages, about a week, alert, no corpse), with **cure geography**
(`DryingBiomeExtension` on five vanilla dry biomes, one modExtension any mod can add); **field conversion**
of your farms (`MapComponent_SlimeFieldConversion`); **the wandering visitors**
(`MapComponent_SlimeVisitors` + `GenStep_SlimeVisitorSeed`: arrivals pulled from the neighbouring world
tiles' own rosters, already part-read, never hostile); raw slime as the universal antitoxin and the
antidote that ends the clock; the **slime compressor** (slime blocks as stuff, the no-rock economy) and the
**slime pit** (slime into a simple meal); **slime rain** (30 of 86 weight, potable, fills barrels, washes the
smear off); the four flora (slime-grass, bellows, thumbstalk, readerbloom); the **gene seeker** end to end
(prime against the archive, extract at the marked current, inject, coma, rider, antidote race:
`SLIME_GENE_ARCHIVE_BUILD_1`, live-verified); the full A/B gene lists (57 GeneDefs, 17 condition hediffs);
and the **titanoslime** (bs 6, five life stages, engulf, grows as it eats, sheds gelatids, six settings).
The campaign layer adds the frozen twin `RUT_Slime` (Alpha Biomes terrain and flora, the donor cast),
`RUT_SlimeGeneArchive` (the Ash'karr archive, priority 100, the 33 frozen targets and 25 riders),
`RUT_SlimeGrazer` and `Slime_Rename.xml` (labels for eleven donor creatures). **No campaign patch touches
`RM_GelatinousSlime` at all** (searched every `xpath` in `src/`).

### 🔴 The systemic defects of the last sittings: checked, and the Slime carries all three

- **(a) Ratified-but-unbuilt creatures: YES, the largest gap of the twelve by share.** The free roster is
  **two animals**: the gelatid 3.0 and the titanoslime 0.12. The BiomeDef's header still calls this
  *"deliberately thin… Spike C"* (the visitors are the cast), but **Q14 overruled it** (by card 2026-09-23,
  `biome_mod_architecture.md` §7: *"`RM_GelatinousSlime` keeps its standalone-without-Alpha-Biomes promise…
  Holes are filled with new creatures of ours"*), and Q11a asks every `RM_` roster to be *"rich enough to
  stand alone"*. Lines the owner ruled on the sheet with **no creature of ours built for them, in either
  tier**:
  1. **The filter-feeder line** (sheet §4, *"owner's ruling… a whole family of scooping-mouthed animals"*):
     one flagship was built, `RUT_SlimeGrazer` (see b), on the twin only; no family, no free-tier member.
  2. **Flyers are the aristocracy** (sheet §4, *"owner's ruling… immune to the wading trap"*): **no flier
     exists**. The donor aerofleet named as the template went to the homeless reserve (roster evictions);
     nothing replaced it. The standing flyer rule (*"we make flyers flyers"*) would apply to whatever is built.
  3. **The resistant characters** (sheet §4: the trash-eating amoeba, the corrosive slug, the iron-shelled
     snail, *"rendered down or milked, the resistant natives supply the resistance economy"*): exist only as
     `AA_` donors on the frozen twin (named oomb, bileworm, bezzul by the 2026-09-24 batch). Q14 bars them
     from the free def; **no remake of ours exists**, and nothing is rendered down or milked anywhere.
  4. **The trace tail of experiments** (sheet §4, 0.001 to 0.07): donor-only on the twin (hennul, mubbaro,
     wuppik, yollum).
  5. **Three owner-ruled round-2 imports are on neither def**: the greater oomb (`AA_AcanthamoebaGiganteaHuge`),
     the thummorak (`AA_OvergrownColossus`, *"make the trees into slime trees"*) and the vohhm
     (`AA_TeratogenicOriginator`, *"tint green… drawSize 3 ONLY"*, sitting ruling 2026-09-10). All three are in
     `rosters/the_slime.json` as ruled imports and all three were named on 2026-09-24; none appears in
     `RUT_Slime/wildAnimals`. Under Q14 they are now design input for our own remakes, not rows to paste.
  6. **And the reverse:** `AA_Thunderbeast` was moved to the Blue Desert by owner review (roster evictions,
     *"round2 move mapping: blue desert"*) and is **still on the twin** at 0.005.
  Census by description: the gelatid (*"a knee-high lobe of the body… entirely harmless"*) and the
  titanoslime (*"a hill of green jelly that has learned to go and fetch"*) are both lobes of the body; there
  is no grazer, no flier, no resistant character and no experiment of ours. **Art:** artpipe
  (`artpipe_state.py find`) has **zero** hits for the gelatid, the three plants, the pit, the compressor or
  the seeker; the titanoslime has its own three facings in `src/`; `RUT_SlimeGrazer` has **two finished
  generations** (`rutslimegrazer_v1_*`, `v2_*`, `done/`) and **no PNG in `src/`**, so its texPath resolves to
  nothing today. 🔴 **The free kit's visible art is almost all vanilla stand-ins:** the gelatid draws as the
  vanilla **tortoise** (`Things/Pawn/Animal/Tortoise/Tortoise`), the three flora as `Bush`, `Dandelion` and
  `Grass`, the compressor as the stonecutter's table and the pit as a fueled stove, the slime block as stone
  blocks, the antidote as penoxycyline, the seeker as a persona core. A biome the sheet calls *"the one biome
  that shines by day"* renders as a tortoise on a lawn.
- **(b) Invented-name content in the campaign tier: YES.** `RUT_SlimeGrazer` (*"slime grazer"*, *"built to
  sieve the Slime's own flesh"*) is an invented creature with no canon claim, authored in
  `UtinniPatches/Defs/ThingDefs_Races/` and wired **only to the frozen twin**, so it is both on the wrong tier
  (Q11a: invented names belong in `RM_`) and lost at the repaint (`RUT_Slime.xml` is deleted at Phase B step 4,
  architecture §4b). Its own header says it was kept off the `RM_` def on purpose, pending a build pass that
  has since closed. Its label is also plain English, against the 2026-09-24 slime law (one long held syllable
  for a gel-body; a scoop-mouthed solid body takes the -o/-um endings).
- **(b′) The inverse leak: Star Wars IP inside the free mod.** The 57 A/B GeneDefs ship in
  `mandrake.rm.gelatinousslime`, and **19 label or description strings** name canon species or terms
  (Selkath, Trandoshan, Wookiee, Rodian, Hutt, Twi'lek, lekku, bantha, kolto, Jawa, Jawaese). The free
  archive (`RM_Archive_Default`) offers only vanilla genes, so a free player never reaches them through the
  machine, but they load, show in the gene list and in dev mode, and the free mod is franchise-free by law.
  The frozen gene lists are canon content: they belong under Utinni beside `RUT_SlimeGeneArchive`, or their
  text is made franchise-free. (Scores doc flagged three; there are nineteen strings.)
- **(c) Campaign patches that replace a free list or gate on a donor or frozen def: no replace, but the
  campaign's sheet law reaches only the donor.** No campaign op targets `RM_GelatinousSlime`, so nothing is
  wholesale-replaced. But every campaign op that carries a Slime ruling targets the donor
  `AB_GelatinousSuperorganism` or the twin: the label and description (`BiomeNames_Ashkarr.xml`,
  `BiomeDescriptions_Ashkarr.xml`), the ancient-shrine denial (`AncientDangerGenSteps_AmbientDoctrine.xml`,
  `preventGenSteps ScatterShrines` on the donor only, the Fever Wood's family), the fish strip
  (`FishTypesStrip_NoFishBiomes.xml`, donor only; harmless, since neither our def nor the twin carries
  `fishTypes`), and the cast evictions. 🔴 **The one that matters is the sky.** Sheet ban 2 (*"No
  meteorological rain… a water-rain weather def is a violation (R-H1)"*) is campaign law; the free def
  rightly keeps vanilla `Rain` 8 and `FoggyRain` 6 for generated planets (its weather def's header says R-H1
  is campaign-only), but **no campaign patch strips them from `RM_GelatinousSlime`**, and the twin carrying
  today's world has `Rain` 8 itself. So the Slime breaks its own hard ban in both tiers today. Same family
  as the Weeping Stones' donor-only oasis mutator.
- **(d) Mod Settings that do nothing: none; but the core hazard has no switch.** All ten `SlimeSettings`
  fields have a reader outside `SlimeMod.cs` (rarity, two flavour toggles, the archive preference, six
  titanoslime). **Slimification itself, field conversion and the visitors have no on/off and no tuning**
  (the week-long clock, the conversion rate and the arrival rate are `[INVENTED]` constants). The Mod
  Settings law asks for a switch per major mechanic; listed, folded into row 0.
- **(e) Heat kind: not owed.** Median 13.4 °C, max 21.9 °C, *"the mildest, most stable climate on Ash'karr"*
  (sheet §0). Not an extreme-heat biome.

### Fauna, merged (inline + patch-added), read as XML elements, census by description

**Free tier, `RM_GelatinousSlime/wildAnimals` (2 rows, `animalDensity 1.4`):** `RM_Gelatid` 3.0,
`RM_Titanoslime` 0.12. Plus the visitors (not roster rows): whatever lives on the neighbouring tiles,
arriving part-read, about one every day and a half, capped.

**Campaign patch-adds to `RM_GelatinousSlime`:** none.

**The frozen twin, `RUT_Slime/wildAnimals` (11 rows, `animalDensity 2.0`):** `AA_GreenGoo` 2.0 (wuum),
`RUT_SlimeGrazer` 0.5, `AA_AcanthamoebaGiganteaLarge` 0.15 (oomb), `RM_Titanoslime` 0.12, `AA_Plasmorph` 0.1
(bezzul), `AA_Helixien` 0.075 (bileworm), `AA_DecayDrake` 0.02 (mubbaro), `AA_Mime` 0.01 (hennul),
`AA_Thunderbeast` 0.005 (ruled moved away), `GR_Chickenrabbit` 0.005 (wuppik), `GR_Manbear` 0.002 (yollum).
Nine donors, all retired from the free def by Q14; at the repaint the world moves onto the two-animal def.

**Flora:** free four rows, all ours (slime-grass 10, bellows 2.2, thumbstalk 1.6, readerbloom 0.7), each
with a real use (forage, clean slime, softwood, a prospecting sign); twin five Alpha Biomes rows. Not a
roster gap; an art gap (above).

**Multi-homed species:** the titanoslime is in both Slime defs (one biome, two tiers; correct). No owned
creature is cast elsewhere.

### Ruled mechanics, built and unbuilt

- **Built (free):** slimification and the cure geography; field conversion; the visitors; raw slime's cure
  and the antidote; the compressor and slime blocks; the pit (as a kitchen); slime rain, potable; the gene
  seeker and both archives; the titanoslime.
- **Built (campaign):** the Ash'karr archive (the frozen SW gene lists, live-verified); the donor cast's
  names; the grazer's def (no art in `src/`, twin only).
- **Ruled, unbuilt:**
  1. The creatures of (a): the filter-feeder family, the flying aristocracy, the resistant characters and
     their **resistance economy** (rendered down or milked), the experiment tail, the three ruled imports.
  2. **The slime pit as a solvent** (sheet §7, *"used to render down an ingredient — the indigestible, the
     toxic, the dangerous… the Rot's finest included… The gourmet chain now spans three biomes"*): built as
     one recipe that turns raw slime into a simple meal. Nothing is rendered down.
  3. **The Rot injection** (sheet §3, *"an intentionally toxic injection derived from the Rot"*): the free
     antidote is slime plus neutroamine (right for a free mod); the campaign's Rot-derived form is unbuilt.
  4. **The farm ruins** (sheet §8, *"owner's ruling"*: fence lines and dead irrigation sinking into
     slime-grass): no genstep or structure anywhere in `src/`.
  5. **The Helix as the machine's vendor** (sheet §7, §8; Owed): the campaign gene seeker is crafted, never
     sold; the Helix's survey relics are unbuilt.
  6. **Slime-in-eyes** (sheet §0, §5, *"the ground can strike back"*): no terrain attack found in `src/`.
  7. **The Throat experiment** (sheet §7, cross-written to `wasteland.md` §10): unbuilt; it is a Wasteland
     quest and stays there.
- **Hard bans, checked:** 1 no sentience: clean (every description says it only reads). 2 no
  meteorological rain: **broken in both tiers** (c). 3 no natural rock: clean (`hasBedrock false`). 4 no
  permanent farmland: clean (conversion). 5 no unprotected residents: clean by identity (every resident is
  a lobe of the body; visitors arrive converting). 6 no shelf-stable extraction: clean (extraction is on
  the current, in the open). 7 no re-arming: clean. 8 recognisability: the gelatid wears a tortoise.
- **Unruled marks:** a ship touch (6), a sound (7), a god and a rite (9).

### Mechanisms already in `src/` that the slate can reuse (searched before proposing)

- `HediffComp_Slimification` + `SlimeUtility`, `MapComponent_SlimeExposure`: anything about being read,
  how far along, and what dries it off.
- `DryingBiomeExtension`: one modExtension makes any def a cure; usable on a building or a ship room by
  the same reading.
- `MapComponent_SlimeVisitors` (neighbour-roster arrivals, part-read): the visitor pipe is the body's
  inbox, ready for anything that should *arrive* on the body.
- `CompGeneSeeker` + `JobDriver_ExtractSlimeSample` (the marked current, the stand-here flow) and
  `GeneArchiveDef` priority swap: anything that asks the archive for an entry.
- `RM_CompEngulfer` (hold, digest, absorb, `IThingHolder`) + `RM_Verb_MeleeEngulf`: a body that holds things
  inside it, already save-safe.
- `MapComponent_SlimeFieldConversion`: anything the body takes back.
- `RM_MapComponent_ProximitySoundscape` (the Greentide's): a per-object sound.
- The Rites tab in `mandrake.rut.rites` (`src/RimUtinni/Rites/`, tab and five research projects built);
  the found-rites row and its grant are register §d's spec, not yet in `src/` (searched).

## 2. Scorecard

Ruled counts as HIT; built is reported beside it. Marks come from the scores doc, re-read against the
sheet, Q14 and the source. **One mark moves** (mark 4, free tier) and two HITs are qualified (marks 5, 8).

| # | Mark | Free (ruled) | Campaign (ruled) | Built today | Note |
|---|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | slimification with cure geography, field conversion, the visitors, the antitoxin and its clock | the core hazard has no settings switch |
| 2 | Discoverable technology | **HIT** | **HIT** | slime chemistry and gene seeking, learned here, the seeker used on the body | the only tech HIT of the twelve; extraction stays on the body by ban 6 |
| 3 | Unique resources | **HIT** | **HIT** | raw slime, slime blocks (stuff), slime meal, the antidote, thumbstalk softwood, bellows slime, the archive's genes | the pit as a solvent and the resistance economy are unbuilt |
| 4 | Surprising creatures | **PARTIAL** (was HIT) | **HIT** (twin only) | free: 2 rows, both lobes of the body, the gelatid drawn as a tortoise; campaign: 9 named donors and the grazer, all on the twin | Q14 rules the free holes filled with creatures of ours: the filter-feeders, the fliers, the resistant characters; none built. The campaign HIT is lost at the repaint |
| 5 | GIANT beast | **HIT** (no story) | **HIT** (no story) | the titanoslime, bs 6, five stages, engulf, growth, shedding, six settings | the best-built giant of the twelve, with no hook; every giant ruled this week has one |
| 6 | Gravship touch | MISS | MISS | 0 | |
| 7 | Soundscape | MISS | MISS | `Ambient_NightInsects_Standard`; slime rain borrows `Ambient_Rain` | the sheet keeps the donor silence on purpose (§9: *"wet stillness"*) |
| 8 | Interesting weather | **HIT** | **HIT** (ban broken) | slime rain 30 of 86 | the campaign never strips vanilla `Rain`/`FoggyRain` from our def, and the twin has `Rain` 8: ban 2 broken in both |
| 9 | Relationship to the gods | MISS | MISS | 0 | no god, precept, shrine or rite; the sheet names none |

**Free 5 HIT / 1 PARTIAL / 3 MISS. Campaign 6 HIT / 0 PARTIAL / 3 MISS** (the scores doc read 6/0/3 for
both; the free creatures mark drops because Q14 ruled the holes filled with ours and the free def has two
animals). Unlike the last two sittings, the top problem is **not missing marks alone**: the mechanics are
the best-built of the twelve, but **the cast and the art are not there**. The free biome is two lobes of
itself plus borrowed neighbours, drawn with a vanilla tortoise, bushes and dandelions; the campaign cast is
nine donors on a twin that is deleted at the repaint; the one creature of ours in the campaign is on the
wrong tier with its finished art unwired. Then the usual three blanks: ship, sound, god.

**Rite: none today.** The scores doc's seed: *"a willing offering of a genome to the library, held by Ozzik
(venting) or Oomo"*. Ozzik is now at the cap; §6 answers it.

## 3. Roster fill

### The gaps, read from the sheet's bands (§4) and Q14 only

Q14 (by card 2026-09-23): *"Holes are filled with new creatures of ours"*, not donor rows. The admission
test is the sheet's own (§3): *"everything living here is resistant or being transformed"*. Every fill is
free tier, invented, alien-coloured (translucent green, amber, membrane pink), soft-bodied except where the
band says otherwise, and one home. Names follow the 2026-09-24 slime law (rule 8: a true gel-body takes one
long held syllable; a solid-bodied resident keeps the -o/-um endings) and avoid the planet's slime
monosyllables (ghaaz, zhool, wuum, oomb, vohhm, the offered baahm). **Drafted names**, each passed
`check_pseudo_sw_name.py` (shape and the 138 canon entries), has no stem collision in `src/` or `design/`
(`boll-`, `dobb-`, `hool-`, `loob-` were taken and dropped), and returns no Wookieepedia title by the search
API (probe *dewback* returns its page).

| band (sheet §4) | free tier today | campaign today | fill |
|---|---|---|---|
| The substrate | gelatid 3.0 (draws as a tortoise) | wuum 2.0 (donor) | none owed; **commission the gelatid's own art** (zero artpipe hits) |
| The filter-feeder line (owner's ruling: *"a whole family"*) | none | `RUT_SlimeGrazer` 0.5, twin only, art finished twice and unwired | **the gappo family**: move the grazer to `RM_` as the **gappo** (the family's middle size; wire its finished `v2` art, artpipe `done/rutslimegrazer_v2_*`, after checking for a ruling on it), add a **lesser gappo** (a skimming swarm) and a **greater gappo** (a slow bs-3 bulk feeder whose scoop leaves a clean channel behind it). One stem, three sizes, the oomb precedent |
| The fliers (owner's ruling: *"the aristocracy… immune to the wading trap"*) | none | none | **the dwommo**: a gas-float lobe-eater, a translucent amber bladder trailing feeding fronds, drifting over the body and landing only on hardened slime; real flight (`MaxFlightTime`, no flip-book needed). The template the sheet names (the aerofleet's hydrogen-float) is a donor and stays in reserve |
| The resistant characters (*"rendered down or milked… the resistance economy"*) | none | oomb, bileworm, bezzul (donors) | **the glurro**: a solid-bodied, iron-crusted crawler that grazes the liquid channels and is never read; tamed and **milked**, its sweat is a resistance salve (slows slimification; it does not stop it), and **rendered down** in the pit it is the salve's concentrate. Lands the resistance economy on one creature of ours |
| The conventional munchers (*"browse the pseudo-plants and hunt the pseudo-herds"*) | none | none | **the fubbum**: the body's one hunter, a low, leathery, wide-footed stalker that hunts gelatid herds at their night pooling and is resistant by its hide. Rare (about 0.15) and never hunts a pawn first |
| The trace tail (*"the database running experiments"*) | the visitors (built: neighbours wander in part-read) | hennul, mubbaro, wuppik, yollum (donors) | **none owed: the visitors are the tail.** Q14 bars the donor experiments; the built visitor pipe already delivers *"recombinations walking around in small numbers"*, honestly sourced from the real neighbours |
| The giant | titanoslime 0.12 | same | **the card asks which story it carries** (below) |
| ⚠ Twin hygiene | — | `AA_Thunderbeast` 0.005 | ruled moved to the Blue Desert; still here. Twin-only, deleted at the repaint; listed, not slated |

**The art debt is the bigger half.** Beyond the four new creatures, the free kit's visible things are
vanilla stand-ins: the gelatid (tortoise), slime-grass (grass), bellows (bush), thumbstalk, readerbloom
(dandelion), the compressor, the pit, the slime block, the antidote, the seeker, the loaded seeker. None has
an artpipe job or finished art (searched). This is row 0's art commission, not a design question.

**The giant needs a story, not a body.** The titanoslime is the best-built giant of the twelve (engulf,
digest, growth to a colossus, gelatids shed when cut, shrinking off the body, six settings). Its own text is
already the seed: *"Shapes drift inside them — a shell, a jawbone, a tool haft — entries not yet filed."* Ban
1 shapes every story: it **fetches by reflex**, never by intent. Three stories, none sharing a neighbour's
shape (the Rot's gut is a treasure map you kill; the Rust Cathedral's borehulk is a machine you mend; the
Fever Wood's deep is bargained with through its young; the Webwork's is a skeleton read bone by bone; the
Weeping Stones' pitches are a crab that carries a machine, a caravan or squats on a hatch):

- **The Unfiled Hull** (BENCH; recommended). The oldest titanoslime swallowed a whole ship ages ago, a small
  hull the body has never finished reading, and it carries it still: a dark keel visible through the
  jelly, drifting as the colossus moves. **It cannot be cut out** (cut it and it leaks gelatids and closes);
  the only way to get the hull is the built weakness: **lead the colossus off the body onto dry ground** and
  hold it there while it shrinks, until the jelly is thin enough to break and the hull drops out. Leading it
  means baiting it with what it fetches (a slime-marked colonist, a load of raw organics, an animal) across
  a dry road while it engulfs whatever it catches. **The hook: whose ship it is.** The Ascendant Helix say it
  is their lost survey ship, carrying the original genome harvest, and will pay to have it back sealed; the
  clan can sell it to them unopened, strip it for a **ship-grade part for the gravship** (an old
  bio-sealed hold that keeps cargo from spoiling or reading), or open its archive and sell the harvest to the
  highest bidder, which the Helix will not forgive. Readable: the keel inside the jelly from the first day,
  the shrinking colossus, three letters. **Reuses:** `RM_CompEngulfer` (an `IThingHolder` that already holds
  things), the off-body shrink, `RM_SlimeMarked` (what it follows), the Helix faction. New: one held
  object, a quest, the ship part. Size L.
- **The Return to Sender** (BENCH). Every colonist who used the gene seeker carries the body's mark
  (`RM_SlimeMarked`, built), and the library wants its book back: once per marked colonist, a titanoslime
  **comes off the body after them**, wherever the colony is, shrinking every day it spends on foreign
  ground. A siege by attrition: hold it off until it shrinks to nothing, **give it a willing substitute**
  (a loaded seeker carrying the same entry, which it takes and turns home with), or let it read the
  colonist (gone, no corpse, a readable letter). Ties the giant to the tech; it is the bill for gene
  seeking, paid anywhere. Size M. ⚠ It reaches far from the biome, and a creature crossing the planet after
  a pawn edges toward ban 1; it must read as chemistry (it follows a scent the body left), never pursuit.
- **The Last Feeding** (BENCH, trade). A titanoslime that has reached the colossus stage starts to **bud**:
  it leaks gelatids by the dozen and, at the end, splits, and the split leaves a field of fresh entries on
  the ground: whatever it held comes out unread (gear, bones, a live animal or two, once a stranger in a
  coma). The clan can feed a colossus to bring the split on, and harvest; every Helix and margin trader on
  the planet comes to bid on the pile. Size M.

## 4. The slate

Proposed for owner turn 1. Row 0 executes existing rulings (the sheet's owner's rulings on the cast and the
kit, Q14, Q11a, ban 2, the Mod Settings law); rows 1 onward need his word. Nothing here grants the body
intent, rains real water, takes a gene off the body, or arms the slime.

**0. Land what was already ruled.** Three parts, all named and ruled; the cast's bodies and names are this
sitting's drafts (§3) under Q14's standing instruction.
- **0a. The cast and its art (free tier, `mandrake.rm.gelatinousslime`):**
  - the **gappo** family: port `RUT_SlimeGrazer` to `RM_` as the gappo (wire its finished art after checking
    for an existing ruling on it), add the lesser and greater gappo; remove the `RUT_` def and its twin row;
  - the **dwommo** (the flying aristocracy, real flight), the **glurro** (milked and rendered for a
    resistance salve: the resistance economy), the **fubbum** (the hunter of the gelatid herds);
  - wire all four inline on `RM_GelatinousSlime/wildAnimals`; correct the BiomeDef's *"deliberately thin…
    Spike C"* header, which Q14 overruled (the visitors stay, as the trace tail);
  - **art for the whole free kit**, none of which exists: the gelatid (today a tortoise), the four flora,
    the compressor, the pit, the slime block, raw slime, the antidote, both seekers, and the four new
    creatures. Check the artpipe first (`artpipe_state.py find`; searched today, zero hits but the grazer).
- **0b. The laws and the tiers:**
  - **the sky (campaign patch):** strip vanilla `Rain` and `FoggyRain` from `RM_GelatinousSlime` on
    Ash'karr (ban 2; the free mod keeps them for generated planets, as its weather header says), and the
    same from the twin while it carries the world;
  - **retarget the campaign's donor-only Slime ops** onto `RM_GelatinousSlime`: the ancient-shrine denial
    (`AncientDangerGenSteps_AmbientDoctrine.xml`); the label and description ops are already redundant (our
    def carries both) and go to `BIOME_TIER_CLEANUP_1`'s list;
  - **the gene text:** move the 57 A/B GeneDefs (and their 17 condition hediffs and 8 thoughts) from the free
    mod into the campaign layer beside `RUT_SlimeGeneArchive`, the only archive that offers them (19 strings
    name canon species); the free archive's vanilla list is untouched;
  - **Mod Settings:** a switch and a slider each for slimification (on/off, clock length), field conversion
    (on/off, rate) and the visitors (on/off, arrival rate), beside the ten that exist.
- **0c. The ruled kit, unbuilt:**
  - **the Slime Pit as a solvent:** recipes that render a toxic or indigestible ingredient into cuisine
    (free: vanilla toxic inputs; campaign: the Rot's finest, the gourmet chain across three biomes);
  - **the farm ruins:** a map genstep of failed farms sinking into slime-grass (fences, dead irrigation, a
    collapsed shed), each a readable story;
  - **slime-in-the-eyes:** the ground striking back (a terrain hazard on liquid slime and mud);
  - **campaign:** the Rot-derived antidote recipe beside the free one; the Ascendant Helix stocking blank
    seekers (the machine's vendor).
Size L (most of it is defs and art; the real C# is the solvent recipes' outputs, the ruins genstep, the
salve, and the settings wiring).

| order | package | marks | reuses | size |
|---:|---|---|---|---|
| 1 | **The giant's story** (§3): the Unfiled Hull, the cook's giant (§5 idea 1), the Return to Sender or the Last Feeding. | 5 | `RM_CompEngulfer` (holds things), the off-body shrink, gelatid shedding, `RM_SlimeMarked`, the Helix | M to L |
| 2 | **The Landing You Cannot Take Back** (ship; §5 idea 2, GPT): a landed gravship's organic contact is read; clean it, or sell one passenger's gene to the archive through a Helix broker, and later meet a rival wearing it. | 6 | `MapComponent_SlimeExposure`, the archive (`GeneArchiveDef`), the seeker's open-body extraction for the client | M |
| 3 | **Two Hammers Make a Mouth** (sound; §5 idea 3, GPT): compressors near each other fall into one beat and liquefy the jelly under them; stagger or separate them. | 7 | `RM_SlimeCompressor`, `RM_Slime_Liquid` terrain | M |
| 4 | **A Salvation rite** (§6 R1 or R2, or GPT's All-Due). | 9 | the seeker's targeting (R1), the cure geography (R2), found-rites row | M (L for All-Due) |
| 5 | **Art commission:** the free kit (row 0), the four new creatures, the hull inside the giant, the pink contact patches, the rite's inscription. Check the artpipe first (`artpipe_state.py find`). | all | artpipe | — |

Held in the doc: **the Last Feeding** (§3, a giant alternative). First-Tear Lacquer (§5 idea 5, a second
learned tech) is offered on the card as a pick-any option, not slated.

🔴 **Sequencing:** row 0 first. The giant's story needs the off-body shrink exposed in settings and real
art for a hull inside it; the landing needs the archive to hold a new entry per map; every rite and story
plays on creatures and art that do not exist yet. `GELATINOUS_SLIME_FIRST_SCRIPT_1` (and its seeker tool,
`SLIME_SEEKER_LOAD_TOOL_1`) should be run against row 0's state.

## 5. GPT consult: five ideas

Consult: `Transient/bedazzle_gpt_enrich_2026-10-02/gelatinousslime_gpt.md` (prompt beside it,
`gelatinousslime_gpt.prompt.md`), run 2026-10-02 under the standing rule (`BEDAZZLE_TOP_SHAPE_PROGRAM_1`,
ruling 2026-10-01): exactly five ideas, different from each other (GPT's own check: verbs carve / disclose /
desynchronize / accelerate / seal; systems animal harvesting / gravship contact records / production
acoustics / ritual and quest deadlines / cargo authentication) and from every other biome's signature, which
the prompt listed in full, **including today's rulings** (Webwork, Greentide, Rust Cathedral, the Rot, the
Fever Wood) **and every Weeping Stones pitch still on its unruled card** (the Walking Array, the Last
Caravan, the Crab on the Hatch, the Fish Walk, the Stone Lets Go, the Pilgrim Passage, the Dewsilk Casket,
Teach the Fish to Lie, the Open Water, the Refused Toll). Model `gpt-6.1-sol`, high effort, via
`gpt_consult.py`, answered first try (started 13:13, written 13:30 PDT). GPT cites Dwarf Fortress butchery,
Against the Storm's trade routes, Death Stranding's cargo sensors and cargo condition, Biotech, Vintage
Story's helve hammer, Oxygen Not Included's visco-gel, Frostpunk 2's promises, Ideology rituals and VFE
Ancients' sealed vaults; its links are not verified here. **GPT offered one rite** (idea 4, Mob'Unloo). It
offered no new creature and no weather.

**Names checked:** *first-tear*, *all-due*, *two hammers* return zero files in `src/`, `design/`,
`infrastructure/state/items`. ⚠ GPT's name for its giant, **Qellum**, fails the stem rule (*quell-* is
taken by *quellan* and *quellith*, and said aloud they are one sound) and the slime law (a gel-body takes
one long held syllable); the card calls it "the cook's giant".

| # | GPT's idea | mark | tier | size | BENCH read |
|---|---|---|---|---|---|
| 1 | **Qellum, Sold by the Slice:** a titanoslime that feeds by reflex at a dead margin-cook's waste hatch; her executor sells the clan her three unfinished raw-slime contracts; you carve the promised mass from a moving, engulfing giant, catch the lobes it sheds and render them before the buyers leave; leading it onto dry ground is safer but shrinks the stock already sold. | 5 | free | M | **A real giant hook, the most trader of the five, and it uses all three built behaviours at once** (engulf, shed when cut, shrink off the body) against a contract. Lighter than BENCH's Unfiled Hull (no ship tie, no faction), and repeatable per contract. **On the card** as the second giant option. |
| 2 | **The Landing You Cannot Take Back:** landing on the body exposes the hull's organic residue to reading; clean the contact points, or take a Helix broker's fee to leave one passenger's sample open through a full reading, which adds that gene to the local archive for good; the broker's client later extracts it in person, and you meet a rival wearing your clan's rarity. | 6 | free | M | **The only ship idea any sitting has offered that is about the body reading the ship**, in its own voice: a landing is a contact, and the library files it. The decision is a sale of your own uniqueness. Honours ban 6 (the client extracts on the body, by the built procedure). **On the card** as the ship mark. ⚠ It needs a world-persistent archive entry (an archive per map tile, saved). |
| 3 | **Two Hammers Make a Mouth:** two compressors near each other fall into one beat; the gel under them yields and whistles; stagger, separate or lose the workshop. | 7 | free | M | **The only sound idea that changes what you build**, and it lives on the biome's own industry (no rock, so every block is pressed on jelly). Narrow (one building pair) but honest. **On the card** as the sound mark. |
| 4 | **Mob'Unloo's All-Due:** found in a drowned farm's clearinghouse (*"When the keeper dies, every account comes due"*); performing it brings every outstanding consignment debt due on one day; collectors arrive armed; honour what you can. | 9 | campaign | L | **Strong and dramatic, and Mob'Unloo's own.** But it is not about the Slime: the farm ruin is a backdrop, and the debt-ledger system it needs (campaign consignment debts as quest parts) does not exist. Against BENCH's **Moving Grave** (also Mob'Unloo, built on the seeker's targeting and the body's no-corpse reading). **On the card** as the second rite. |
| 5 | **First-Tear Lacquer:** learned from the thumbstalk's setting membrane, a slime lacquer seals a freight crate so the first breach leaves an unrepeatable fracture; carry the evidence when a buyer says you swapped the contents; usable everywhere. | 2 | free | M | **The most Jawa of the five** (custody as a thing a trader sells) and a learned tech that travels. But mark 2 is already the Slime's one tech HIT, and it needs a dispute system in trade to matter. **On the card** as a pick-any option, not recommended. |

GPT's ranking: the cook's giant first, the lacquer second, the landing third.

## 6. Discoverable rites

Per `design/Jawa/salvation_rites_2026-10-01.md` (e): found at a site with a reason to be there,
learned through the Rites tab's found-rites row (`mandrake.rut.rites`), performable anywhere after.
Campaign tier. The binding rulings: **no god is evil**; **a rite gives cohesion, never a power**;
**favour shows only through events, world state and subtle odds**, voiced by the Narrator; a rite's
effect may be a dramatic, risky world event. **Per-god cap: five** (by card 2026-10-02 09:23 PDT).

⚠ **He has answered "none" at two of the last three sittings** (the Fever Wood, *"none, move on"*; the
Sump, where he declined all three and wrote his own). So this section offers two, both built on a
mechanic the Slime already ships, and the card says plainly that "none" is a fine answer (by write-in).

**Cap count, by hand from the register's tables B2, B4, B7 to B14** (found rites only; B4's controlled
waking counted for Zizzik as the register does; read from the register at the time of writing):

| God | Found rites | Count |
|---|---|---|
| Ishko | Dark Vigil (B2), Charged Reed, Stall-Hold (B7), the Sinking (B14) | 4, one slot |
| Ohm | Engine Hour, Last Track, Deserter's Welcome (B7), the Answering (B8), the Stranger's Overhaul (B12) | **5, at cap** |
| Oomo | Sunning, Chime Vigil, Filtered Cup, Unspilled March (B7) (the Unlit Wedding is a variant) | 4, one slot ⚠ |
| Mob'Unloo | Blind Offering (B2), Storm's Receipt, Cold Ledger (B7), Mob'Unloo's Price (B14) | 4, one slot ⚠ |
| Sh'kaar | Snuffing (B2), Anvil Gift, Shade Tithe (B7), Felled Noon (B10) | 4, one slot |
| Ozzik | Lightless Burial (B2), Salted Keeping, Flawed Masterwork (B7), Ceded Room, Open Boast (B11) | **5, at cap** |
| Zizzik | controlled waking (B4), Kept Mistake, Capping (B7), Nine Faults (B8), Struck Glass (B9) | **5, at cap** |
| Rekko | Unfinished Laid Down, Inherited Wreck, Mud Claim (B7), Mending Weld (B12) | 4, one slot |
| Ta'Baa | the Returned, Shadow Walk, Vindication Walk (B7), the Unjoining (B13) | 4, one slot |

⚠ **The Weeping Stones card, drafted today and not yet ruled, pitches the Open Water for Oomo and the
Refused Toll for Mob'Unloo.** If he takes either, that god is at the cap and the matching Slime pitch below
cannot be his. **The scores doc's seed (Ozzik, venting) is closed: Ozzik is at the cap.** No god is the
Slime's by the sheet; the sheet names none.

**Not taken, and why:** a willing genome offered to the library for nothing (the scores doc's seed: it is a
gift with no exchange, Ozzik's venting shape, and he is full); drinking the slime rain (offering water, and
a cup); a rite in the farm ruins (the Inherited Wreck and the Mud Claim already own the failed-settler
salvage shape); rescuing a colonist mid-reading (a rescue, and the antidote already does it); a vigil
waiting for the titanoslime (stillness vigils are taken); purging the slime with the antidote before
leaving (the Unjoining is exactly that shape for Ta'Baa); burying in the slime (the Lightless Burial owns
burial, and the body leaves no corpse to bury, which R1 builds on).

### R1. The Moving Grave, for Mob'Unloo: settlement, by laying a read ghost where its entry passes (PITCHED)

- **Grounding:** Mob'Unloo is debt and the sacred exchange, and **ghosts laid to rest**. The Slime is the one
  place on Ash'karr where the dead leave nothing: *"returned to the flow… there is no corpse"* (built). A
  Jawa read by the body has no grave, so the debt of their death is never settled and the ghost walks. The
  body did not destroy them; it **filed** them, and the entry is still out on the tide.
- **Found:** on the Slime, a ring of upright slime-blocks pressed by hand (the compressor's own bricks) in
  the open on the hardened margin, each scratched with a name, and none with a body under it; in the ring,
  a dead gene seeker, its prime dial set to a person's name instead of a gene.
- **Asks:** for a colonist (or kin of a colonist) the body has read, the participants take a primed seeker
  out onto the body: it marks **where the current carrying that person's entry will pass**, using the
  built stand-here targeting, and the funeral is held **there, in the open, standing on the body**. The
  spot drifts as the current moves, so the party follows it, and the rite lasts until the entry has passed.
- **Risk (the point):** every mourner is being read for the whole rite (the slimification clock runs on all
  of them; the antidote stock decides how long they can stay); a titanoslime fetches toward a still crowd;
  a slime rain mid-rite slows everyone. Abandoning the spot breaks the rite. Success is a funeral finished on
  the body with everyone walked home.
- **Outcomes (cohesion only):** the read dead count as properly mourned (the standard funeral thoughts, by
  quality); Mob'Unloo's favour told by the Narrator (*the debt is closed*), shown only in his odds. Nothing
  is retrieved; no gene, no body.
- **Readable signs:** the seeker's moving marker, the funeral circle drawn on the current, each mourner's
  slimification stage in the alert, the Narrator's line at the end.
- **Collision check:** the Cold Ledger **pays** a frozen dead man's debt with a gift sealed in ice (Mob'Unloo,
  B7); the Lightless Burial **buries** in darkness (Ozzik). The Moving Grave buries **no one**: it mourns a
  person with no body, at a place that will not hold still, at the price of being read. ⚠ It is a second
  dead-man rite for Mob'Unloo; and it is pointless until someone has been read, so it is a rite a colony
  learns here and may never need. It spends Mob'Unloo's last slot, which the Weeping Stones may take first.

### R2. The Walked-Off Reading, for Ta'Baa: feeding, by refusing to be filed (PITCHED)

- **Grounding:** Ta'Baa is *"the Unrooted — flight, the refusal to root"*. The Slime is the deepest root
  on the planet: it keeps every entry it ever takes, for ever. To be read and **not kept** is the
  Unrooted's own act.
- **Found:** at the edge of the body where the dry country begins, a line of old footprints pressed into
  hardened slime, walking off the body, that the body never filled back in; beside them, a cracked antidote
  ampoule, full, never used.
- **Asks:** the participants walk out onto the body **unprotected** (no resistance gene, no symbiont), stand
  in the open until the sheen is on every one of them (slimification stage one, readable), then walk **off
  the body by the dry road** without the antidote, letting the dry country strip the film away (the built
  cure geography). The rite is complete when every participant is clean.
- **Risk (the point):** the dry road may be far and the walk slow (film slows them); a titanoslime fetches
  the slowest; a raid that finds them filmed and slowed finds them weak; anyone who takes the antidote
  breaks the rite, so a participant sliding toward stage two is a real choice between the rite and the
  person.
- **Outcomes (cohesion only):** shared memories by quality; Ta'Baa's favour told by the Narrator, shown only
  in his odds (his own clock eases for a while, the way a launch eases it). Nothing is gained.
- **Readable signs:** the sheen on each participant, the dry road marked, the alert counting stages, the
  footprints that stay.
- **Collision check:** the Unjoining (Ta'Baa, B13) **purges** a hold already inside a colonist before the
  clan leaves; the Vindication Walk (B7) walks until the wind lifts the prints. The Walked-Off Reading
  **takes the hold on purpose** and walks it off without a cure. ⚠ Both are Ta'Baa refusing a body's hold,
  so he may read them as one shape. It spends Ta'Baa's last slot.

GPT offered one rite, **Mob'Unloo's All-Due** (§5 idea 4): it is on the card as the second rite option.

## 7. Draft turn-1 card

Plain language, no def names in option labels, headers 12 characters or fewer, every question ends in
"?", and no option is a "none" (the card's own write-in line covers that, and above question 4 say that
"none" is a fine answer there). Above the card, read him §0's description of the Slime, per the standing
rule that he is never assumed to remember. Say in one line above it that **the free Slime has only two
animals and almost no art of its own (its little herd animal is drawn as a vanilla tortoise, its plants as
grass and dandelions), none of the creatures you ruled for it (the scoop-mouthed grazers, the fliers, the
resistant natives) was ever built for the free mod, the one grazer that was built sits in the campaign
layer with its finished art unused, and the campaign never removes ordinary rain from it, which the Slime's
own rules ban**; and that the gene seeker, the hazard and the giant are the best-built kit of the twelve.

**1. Build first** (header `Build first`) — *What should be built first for the Slime?*
- **Land what was already decided (recommended):** build the creatures you ruled for it as our own: a
  family of scoop-mouthed grazers (the existing grazer moved over, with its finished art, plus a small and a
  large one), a gas-float flier, an iron-crusted grazer you milk and render for a slime-resistance salve,
  and one hunter of the little herds; give the whole biome real art; strip ordinary rain from it in the
  campaign; move the Star Wars gene names into the campaign layer; add switches for the hazard, the farm
  conversion and the wanderers; make the slime pit render toxic food safe, as you ruled; add the ruined
  farms. Buys: the free Slime stands alone, as you ruled twice. Costs: a large batch, mostly art, and no
  new mark this round. *Why: everything below lands on creatures and art that do not exist yet.*
- **Land it and add the giant's story together:** Buys: a hook on the jelly giant now. Costs: a bigger
  first batch.
- **New ideas first, landing later:** Buys: new marks sooner. Costs: the free biome stays two animals and a
  tortoise.

**2. The giant** (header `The giant`) — *Which story should the jelly giant carry?*
- **The unfiled hull (recommended):** the oldest jelly giant swallowed a whole small ship ages ago and still
  carries it, a dark keel you can see through the jelly. You can't cut it out (it leaks and closes); you
  lure the giant off the slime onto dry ground and hold it there while it shrinks, until the hull drops out.
  Then decide: sell it sealed to the gene cult who say it is their lost survey ship, strip it for a ship
  part (a sealed hold that keeps cargo from spoiling), or open its records and sell them, which the cult
  never forgives. Buys: a giant tied to the ship, a faction and the trade, using its built weakness.
  Costs: a large build. *Why: it uses what the giant already does (hold things, shrink off the slime) and
  gives the clan a scavenger's choice.*
- **The cook's giant:** a jelly giant comes back by habit to a dead slime-cook's waste hatch; her executor
  sells the clan her three unfinished slime contracts cheap. You carve the promised slime off a giant that
  swallows whoever gets close and sheds little lobes when cut, and render it before the buyers leave;
  leading it onto dry ground is safer but shrinks the stock you already sold. Buys: the most trader story,
  using everything the giant already does. Costs: a medium build; no ship tie.
- **The return to sender:** everyone who used the gene seeker carries the slime's mark, and once each, a
  jelly giant comes off the slime after them, wherever the colony is, shrinking every day on foreign ground.
  Hold it off, hand it a seeker carrying the same gene to take home instead, or lose the colonist. Buys: the
  gene seeker gets a bill you pay anywhere. Costs: a medium build; it must read as a scent followed, never
  as the slime choosing to hunt.

**3. New marks** (header `New marks`) — *Which new ideas should be built (pick any)?*
- **The landing that can't be taken back (recommended):** land on the Slime and it reads whatever living
  traces your ship touches it with. Clean the contact points first, or take a gene broker's fee to leave
  one passenger's sample open until the slime has filed their gene; it's then in the archive for good, the
  broker's client comes to take it, and one day you meet a rival wearing what made your clan rare. Buys:
  the place acting on your ship in its own voice, and a sale you can't undo. Costs: a medium build. *Why:
  it is the only ship idea yet that is about this biome's one act, reading.*
- **Two hammers make a mouth:** two slime presses working near each other fall into one beat, and the
  jelly under them softens and starts to whistle; stagger them or space them out, or the workshop slumps
  and spills its goods into the slime. Buys: a sound that changes how you build. Costs: a medium build.
- **The tamper-proof seal:** learn from a slime plant how to make a lacquer that seals a crate so the first
  opening leaves a crack nobody can fake, usable anywhere; carry the proof when a buyer says you swapped the
  goods. Buys: a trader's tool the clan can sell. Costs: a medium build, and the Slime already has its
  learned tech.

**4. Rite** (header `Rite`) — *Which rite should the Salvation find at the Slime?*
- **The walked-off reading, for the god of flight (recommended):** the participants walk onto the slime
  unprotected, stand until it starts reading every one of them, then walk off the dry way with no antidote
  and let the dry country clean them; anyone who takes the antidote breaks it. Buys: the god who refuses to
  put down roots, shown on the one place that keeps everything. Costs: a medium build; risky (the giant
  takes the slowest, a raid finds them weak); close in spirit to the purge rite you took at the Rot; it uses
  that god's last free rite. *Why: it is built entirely from the slime's own hazard and cure, and that god's
  last slot is not wanted by another sitting.*
- **The moving grave, for the god of debts:** for someone the slime read (no body is ever left), the gene
  seeker finds where that person's trace is passing in the slime's currents, and the clan holds the funeral
  there, standing on the slime and following the spot as it drifts, every mourner being read for as long
  as it takes. Buys: a funeral for the dead it took, and a real risk. Costs: a medium build; only useful
  once someone has been lost; the Weeping Stones may take that god's last free rite first.
- **All accounts come due, for the god of debts:** a rite found in a drowned farm's trading house brings
  every debt the clan owes due on the same day; armed collectors arrive and you honour what you can.
  Buys: a dramatic, risky day. Costs: a large build (the debt system is new); not tied to the Slime itself;
  the same last free rite.

Held off the card (in the doc only): the last feeding (§3, a giant alternative).

## 8. Turn 1 rulings (2026-10-02) and ticket-out

Card asked 2026-10-02 ~14:25 PDT. Item 1 decision taken by question card (seat BENCH). Items 2, 3 and 4 the owner
answered in typed words, quoted verbatim below; **none of the pitched options on 2, 3 or 4 was chosen**, and each
typed answer replaces them.

| Card item | Ruling | Ticket |
|---|---|---|
| 1. Build first | **Land what was already decided.** Decision taken by question card. §4 row 0 as the card listed it: the ruled creatures built in the free mod (the gappo family: the existing grazer moved to `RM_` with its finished art, plus a lesser and a greater; the dwommo, a gas-float flier; the glurro, iron-crusted, milked and rendered for a slime-resistance salve; the fubbum, the one hunter of the little herds); real art for the whole biome in place of the vanilla stand-ins; ordinary rain stripped in the campaign (both tiers); the 19 Star Wars gene strings moved to the campaign layer; switches for the hazard, farm conversion and the wanderers; the slime pit renders toxic food safe; the ruined farms. "Land it and add the giant's story together" and "new ideas first" are **NOT CHOSEN**. Not in this batch (not on the card's list): slime-in-the-eyes, the Rot-derived antidote, the Helix stocking blank seekers. | `GELATINOUSSLIME_GAPPO_FAMILY_1`, `GELATINOUSSLIME_DWOMMO_FLIER_1`, `GELATINOUSSLIME_GLURRO_SALVE_1`, `GELATINOUSSLIME_FUBBUM_HUNTER_1`, `GELATINOUSSLIME_KIT_ART_1`, `GELATINOUSSLIME_RAIN_STRIP_1`, `GELATINOUSSLIME_GENE_TEXT_TIER_1`, `GELATINOUSSLIME_SETTINGS_SWITCHES_1`, `GELATINOUSSLIME_PIT_SOLVENT_1`, `GELATINOUSSLIME_FARM_RUINS_1`; amended: `BIOME_TIER_CLEANUP_1` (the donor-only label, description and fish ops) |
| 2. The giant | Owner, typed: *"Grab a chunk of the giant and it becomes a terrible bomb like weapon to use on someone. Bioweapon after all. Can use it to open one of the vault dungeons blocked by assailant seals."* The unfiled hull, the cook's giant and the return to sender are **NOT CHOSEN**. A torn-off chunk of the titanoslime is a carried, thrown or planted bioweapon that drenches its radius into late-stage slimification; off the body it shrinks, so it never stockpiles (ban 6). ⚠ It brushes sheet ban 7 (*no re-arming*): the body still never makes weapons; the clan makes one of a piece of it. Recorded as his ask. **The vaults:** searched; the six Forsaken vaults exist (`VAULT_DUNGEON_BUILD_1`, `VAULT_THAW_QUEST_FAMILY_1`), and V5 sits in **the Slough, the Slime's own largest patch** (a type ② flesh-breached vault, landmark `RUT_Slough_GelatinousBreach`). **No "Assailant seal" exists** anywhere in `src/` or `design/`: the item adds one: an Assailant-flesh plug that a chunk dissolves, **on the Slough vault only, and the only way through it** (decision taken by question card, 2026-10-02 14:44 PDT). The chunk weapon is ruled an exception to sheet ban 7 (decision taken by question card, 2026-10-02 14:44 PDT). | `GELATINOUSSLIME_TITAN_CHUNK_BOMB_1` (free), `GELATINOUSSLIME_VAULT_SEAL_BREACH_1` (campaign) |
| 3. New marks | Owner, typed: *"An ability to resurrect someone from the last time they touched the slime. Requires expensive helix tech."* (followed by his question, *"But are they the same?"*, which is the design: the identity gap is deliberate). The landing, two hammers and the tamper-proof seal are **NOT CHOSEN**. The body files everyone it touches; a procedure grows a dead person back **as of their last touch** (skills, relations, memories as of then). "Helix tech" is the **Ascendant Ladder** (`RUT_Tree_AscendantLadder`, the Helix's faction-locked tree, bought by trade and quests; top rows `Archogenetics`, `Bioregeneration`). Tier: snapshot and procedure in the free mod behind a project needing vanilla `Archogenetics`; in the campaign that project sits on the Ladder. A second tech for mark 2; marks 6 and 7 stay open. | `GELATINOUSSLIME_ARCHIVE_RESURRECTION_1` (free machinery, campaign gate) |
| 4. Rite | Owner, typed: *"Pomp's rite. The joining water. The uncomfortable truth that we are all connected not so unlike the slime. Separate for now. Everyone briefly joins hands holding some slime. Can reduce permanent hediffs on one person to weak hediffs on several instead."* The walked-off reading (Ta'Baa), the moving grave and all accounts come due (Mob'Unloo) are **NOT CHOSEN**. **God: Oomo** (decision taken by question card, 2026-10-02 14:44 PDT); his fifth rite, the cap. The injury-spreading power is ruled an exception to the cohesion-only rule. Register: row B16 (no Slime seed row existed). | `GELATINOUSSLIME_JOINING_WATER_RITE_1` (campaign) |

FOUNDRY items, each `--caused-by GELATINOUSSLIME_SCORING_SITTING_1`:

| slate row | item | tier |
|---:|---|---|
| 0a | `GELATINOUSSLIME_GAPPO_FAMILY_1` (grazer → `RM_` gappo with `v2` art, lesser and greater; `RUT_SlimeGrazer` deleted; the "deliberately thin" header corrected) | free |
| 0a | `GELATINOUSSLIME_DWOMMO_FLIER_1` (real flight) | free |
| 0a | `GELATINOUSSLIME_GLURRO_SALVE_1` (milked salve slows the reading; rendered concentrate) | free |
| 0a | `GELATINOUSSLIME_FUBBUM_HUNTER_1` | free |
| 0a | `GELATINOUSSLIME_KIT_ART_1` (the tortoise, grass, bush, dandelion, stonecutter, stove, persona-core stand-ins replaced) | free |
| 0b | `GELATINOUSSLIME_RAIN_STRIP_1` (`Rain`/`FoggyRain` off `RM_GelatinousSlime` and the twin; shrine denial retargeted) | campaign |
| 0b | `GELATINOUSSLIME_GENE_TEXT_TIER_1` (57 GeneDefs, 17 hediffs, 8 thoughts to Utinni) | free → campaign |
| 0b | `GELATINOUSSLIME_SETTINGS_SWITCHES_1` (hazard, conversion, visitors: on/off and a slider each) | free |
| 0b | `BIOME_TIER_CLEANUP_1`, 2026-10-02 Gelatinous Slime addition | campaign |
| 0c | `GELATINOUSSLIME_PIT_SOLVENT_1` (toxic and indigestible inputs made safe; the Rot's finest in the campaign) | free + campaign recipe |
| 0c | `GELATINOUSSLIME_FARM_RUINS_1` | free |
| 1 | `GELATINOUSSLIME_TITAN_CHUNK_BOMB_1` | free |
| 1 | `GELATINOUSSLIME_VAULT_SEAL_BREACH_1` (needs the owner's word on the seal before build) | campaign |
| new | `GELATINOUSSLIME_ARCHIVE_RESURRECTION_1` | free machinery, campaign gate |
| 4 | `GELATINOUSSLIME_JOINING_WATER_RITE_1` (god to confirm) | campaign |
| 5 | art: `infrastructure/artpipe/art_lists/gelatinousslime_turn1_2026-10-02.csv` (20 jobs: the gelatid, four flora, compressor, pit, block, raw slime, antidote, both seekers, lesser and greater gappo, dwommo, glurro, salve, fubbum, the giant's chunk, the rite's hand-print ring). Searched first (`artpipe_state.py find`, probe `korrum` 12 hits): the grazer has `done/rutslimegrazer_v1_*`, `v2_*` (wired by the gappo item, not regenerated); the titanoslime has `done/rmtitanoslime_v1_*`; every other subject 0 hits. | |

Sequencing: row 0 first (`GELATINOUS_SLIME_FIRST_SCRIPT_1` is written against row 0's state); the gene tier move
before any new gene work; the glurro before the pit's concentrate recipe; the chunk before the vault seal; the
resurrection after the owner sees its snapshot field list; the rite after he names its god.
