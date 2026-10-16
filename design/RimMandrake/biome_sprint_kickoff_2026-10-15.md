# Biome sprint kickoff packet — Cauldron, Contagion, LeaningScrub (BENCH, 2026-10-15)

**Owner, by card 2026-10-15 ~16:45 PDT:** *"Which shape should the next sprint take? → Three biomes deep"*. That is
option 2 of `design/RimMandrake/next_sprint_plan_2026-10-15.md`. Item: `BIOME_SPRINT_PROVE_SCRUB_SETS_PACE`. The plan's
exit criterion: a per-biome criteria list he approves at sprint start (S0), and his sign-off cites that list.

**Status, 2026-10-16 ~00:50 PDT: the kickoff cards are ANSWERED.** Every Q1-Q12 is RULED in §2 (his answers are ledger
notes on the item). The ruled scope is bigger than the draft's recommendations: Cauldron gets the Filter-Works, ruins and
the Oomo shrine; the Scrub gets the calling-pyre with three beliefs and living camps; FOUNDRY builds and BENCH tests. §1
and §4 below are revised to that scope. Four new open questions the rulings created are in §2.3.

This packet holds:

- §1, the criteria list for each biome at the ruled scope, for him to approve, edit or cut at S0;
- §2, his rulings on the kickoff cards, and the new open questions as question cards;
- §3, the LeaningScrub art redo;
- §4, the day-by-day schedule with his sittings marked, re-estimated.

Every fact was re-measured on 2026-10-15 from the item files, the ledger, the design sheets, each biome's walk file
(`design/validation_walks/RimMandrake/<Biome>.md`, which holds its `## north star`) and the 2026-10-08 modcheck records
(`Transient/modcheck/<Biome>_20261008*.json`). Those runs used fresh maps at pre-pilot HEADs: they show how far each suite
reaches, not today's state.

**Said to him in these words (plan §2.2):** "done" means *done against the scope he froze at S0*, which is the ruled scope
in §2.1. Only the Seismometer is cut; nothing else was deferred.

---

## 0. Corrections to the plan found while building this packet

| plan said | measured |
|---|---|
| Cauldron blocked on "falter-tell foreknowledge" | **Settled by the build, not by a question.** `src/RimMandrake/Cauldron/Source/RM_CauldronVents.cs` uses the weather-transition ramp as the tell and needs no foreknowledge. `vents.vent_falter_precedes_bloom` PASSed live on 2026-10-08. Dropped from the cards. |
| Cauldron: 4 overlay textures missing | **7.** The 2 assay-fleck overlays (`Things/Plant/RM_AssayFlecks/Flecks_{Light,Heavy}`), plus 5 dew variants `Things/Plant/RM_Dewfall/<def>_dew` for CrystalFlower, BloodBouquet, RedBugloss, KeeningCordax and GiantToxicFlower. The lint does not count the dew variants. |
| Contagion blocked on the "grown-limbs owner sheet" | **Answered twice.** At the bedazzle sitting on 2026-09-27 he said *"Approved, this looks great!"*; all five limbs were built to the sheet's recommendations (`CONTAGION_GROWN_LIMBS_BUILD_1` and `_REST_1` are closed). On 2026-10-15 he asked by card for a design sheet early and to build what he keeps. So the built five get reviewed on an early S1 sheet (§3), and what remains is a live proof and real art for three placeholder limbs. |
| Contagion blocked on the "rattle render seam" | It is engineering, not design. It stays a scope card (Q6) only because it is polish that could be cut. |
| LeaningScrub blocked on the "calling-pyre ritual" | **The concept is ruled.** By card on 2026-10-01 it was merged with the controlled waking: the calling-pyre is the controlled waking's Scrub form (`design/Jawa/biome_rites_pass_2026-10-01.md` §7.1). Only the precept shape and the build size are open (Q7). |
| "Patch-added RM_ cast" for every biome | Contagion has no `WildAnimals_Contagion.xml`: its whole roster is inline in `RM_Contagion.xml`. LeaningScrub's patch-added cast (about 38 rows in `src/RimUtinni/UtinniPatches/Patches/WildAnimals_LeaningScrub.xml`) is all `RSW_`, not `RM_`. The manifests list the real files. |
| north-star line counts 7 / 8 / 8 | Those are the must-show lines. Each biome also has 2 cannot-show lines. In all three, `### the experience` is "(not yet dictated)". |

---

## 1. Draft criteria lists (for S0 approval)

**Shared lines.** These apply to all three biomes, from plan §3 "Exit criterion", and are not repeated below. All hold at
ONE HEAD on the `biomes_sprint` tier, each recorded by `rimflow verify`:

- **M1** `northstar_driver run --mod <Biome> --plan src/RimMandrake/<Biome>/northstar_plan.py` on the biome's registered
  saved site gives 0 FAIL and 0 UNMEASURED. Its row count equals the manifest's, so the run is not EMPTY. INFERRED rows
  are allowed only where listed below.
- **M2** Every manifest roster def's texture resolves offline against the deployed composite, with zero missing.
- **M3** `modcheck floor --all` reads "bar met" with bars > 0.
- **M4** Every manifest item is done, or deferred by a manifest revision he approved.
- **M5** `run_selftests.py --only` passes on the changed files, and `code_review_status.py check` reads CLEAN on them,
  marked by a reviewer who is not the builder.
- **M6** The pilot guards (GSS, FlowWorks, Pyrelands) are green at matching inputs.
- **O1** He dictates `### the experience` (his words; agents never fill it).
- **O2** He accepts the visual bars against the review save.
- **O3** His sign-off cites the manifest hash.

All three suites keep their rows in `validation.py`; `northstar_plan.py` is a thin `USE_SUITE=True` wrapper.

**Bars are written as state-independent prose**, so they can go straight into each `## north star` once he edits them.
Each one says what a map shows, never what is built today.

### 1.1 Cauldron

**Experience (from `design/Jawa/worldbuilding/biomes/cauldron.md` §1, for him to replace with his own words):** a low,
wet-black forest in permanent dusk, over ground that breathes cold, metal-rich gas; trees weep metal; the water and meat
are poison but prized.

**Machine rows.** The suite has 63 components in 15 chains: load, weather, settings, items, acid, fauna, suush, flora,
yield, bloom, water, fire, vents and log. The 2026-10-08 result was 58 PASS / 1 FAIL / 4 UNMEASURED.

| row | what closes it | kind of fix |
|---|---|---|
| `yield.yield_factor_scales` FAIL, plus `yield_toggle_off` UNMEASURED | The Harvest order is now sent with queue=False (`09d32ba8f`, proven offline only); `CAULDRON_YIELD_LIVE_RERUN_1` owes a live rerun | harness |
| `suush.suush_detonates_when_shot` | Move the control suush out of blast reach | site spacing |
| `bloom.bloom_spares_natives` | Run on a real `RM_Cauldron` site with a native and a non-native herbivore | the saved site |
| `water.water_poison_toggle_off` | Pen the test vexxiss in the pond so it cannot wander off | site |
| New, cheap rows (in only if he keeps the visuals) | Dewfall bead count; dew swap and reverse; fleck overlay draw on a graded tree; footprint ledger read | new rows |
| New rows (Q1 ruled) | Vents emit drifting gas clouds through the game's gas system; the cloud ignites and burns into toxic smoke; the vexxiss attacks an igniter | new rows |
| New rows (Q2 ruled) | Filter-Works refines vent gas into reagents; ruin set-pieces present on a generated map; Oomo shrine present and usable | new rows |

Proposed INFERRED rows: none.

**Visual bars (draft):**

- *Must show:*
  - A noon map reads as a dim, even, shadowless dusk forest, never full daylight.
  - Under a vent bloom the air visibly thickens with a coloured haze.
  - Martyr and thornwood read as sweating metal, unlike vanilla trees. A mature tree's assay grade shows as flecks.
  - Under dewfall, beads form and the accent plants change to their dew look, then change back.
  - The two soils read as dark, gassy ground, and the rich one differs visibly from the plain one.
  - Vent gas reads as a drifting cloud that moves with the air, not a static patch.
  - A Filter-Works reads as a working gas refinery; the ruins read as ruins; the Oomo shrine reads as a shrine.
  - The four natives read as four different animals.
  - The suush floats above the ground.
  - A vexxiss leaves footprints.
- *Cannot show:*
  - A bright day.
  - Rain or snow.
  - A magenta square.

**Art set:**

- The 7 missing textures (2 fleck overlays and 5 dew variants).
- New for the ruled scope: the Filter-Works, the ruin set-piece kit, and the Oomo shrine. All need an art sheet round.
- The bedazzle sheet's open picks from 2026-09-29, still unverified as actioned:
  - Eskith "improve" (five eyes, so the side profile shows three);
  - Vexxiss "improve" (as colourful as the vents).
- *Rider for the S1 art sheet:* which accent plants get dew variants. The XML default of five stands until he picks.

**Mechanics.**

- *In scope, built:* the four weathers; vents with the falter tell; the bloom metal-load hediff; vexxiss vent-drinking,
  fire warden and water poisoning; metal yield and assay; nettle gardens; vexxith acid immunity; the dewfall, fleck and
  footprint visuals; 27 settings.
- *In scope, to build (ruled):*
  - drifting vent gas on the game's native gas system, burning into toxic smoke when lit (Q1);
  - the Filter-Works, the ruin set-pieces and the Oomo shrine (Q2).
- *Falter tell target:* about one in-game hour of warning before a vent bloom (ruled by card). The built tell (the weather
  transition ramp) is checked against this on the first live round. If it is shorter or longer, the ramp is retuned.
- *Cut:* the seismograph / Seismometer (*"I don't like that idea."*). The seismograph art is dropped, not regenerated.
- *Out of scope:* sound, by his 2026-10-03 ruling (vanilla sounds).

### 1.2 Contagion

**Experience (sheet `design/Jawa/worldbuilding/biomes/the_contagion.md`):** *"A red valley under a storm that never
stops, where the clear sky is the thing to fear."*

**Machine rows.** The suite has 59 rows in 12 chains: defs, settings, log, repulsor_clear, spawner, site, burn_forced,
burn_natural, uv, coalescence and genome. The 2026-10-08 result was 52 PASS / 0 FAIL / 7 UNMEASURED.

| row | what closes it | kind of fix |
|---|---|---|
| `defs.biome_roster_animals` | `get_defs` cannot read the non-public `wildAnimals` field. Promote the static XML roster check to the row, or add a bridge read | harness |
| `repulsor_clear.site_ready_baseline` and the 3 rows downstream of it; `site.retile_to_contagion` | All five share one cause. The suite wants a stock-biome start, but a saved Contagion site is already Contagion. Run the off-Contagion arm on the calm site, and keep the retile control there | harness + site |
| `genome.extraction_surgery_yields_sample` | Put the patient in a bed and make the bill giver usable | fixture |
| New rows | Bloom/Burn tells by a state read of `RM_MapComponent_ContagionSky`; a Sunbeam firing fixture; limb install, and limb removal spawning an Unfinished | new rows |
| New rows (Q3-Q6 ruled) | The Sunbeam arrest (stops current mutations, no later protection); the plain mulch item and its drops; Cloud Repulsor and Sunbeam in quest rewards and in a visiting Helix trader's stock; the sink and shake tells by a state read | new rows |

Proposed INFERRED row, to be pre-approved: natural Coalescence formation in a long Bloom. It is a statistical event,
scored from the forced-formation rows plus the Bloom-duration timer.

**Visual bars (draft):**

- *Must show:*
  - A map under its Bloom reads as a red, sick, storm-roofed sky, not an ordinary overcast.
  - At a Burn the light turns to a near-white shaft, and the gawpsacks and rattlegropes give their tells before it.
  - A powered Cloud Repulsor clears the sky around it while the rest stays under the Bloom.
  - The Sunbeam reads as a beam of light striking its target.
  - Before a Burn, gawpsacks visibly sink and rattlegropes visibly shake.
  - Meatvine, toothmoss, eyebark and wombpod read as grown flesh at play zoom.
  - The Unfinished read as half-made, wrong creatures, each different.
  - The Coalescence reads as one living mass, with three stages you can tell apart.
  - A colonist with a Monstrous grown limb looks different from one with a natural arm, in all four facings.
- *Cannot show:*
  - A recoloured vanilla forest.
  - A magenta square.

**Art set:**

- Placeholder limb art to replace:
  - Eyeburst (tinted vanilla);
  - Caudal Spring (Anomaly's TentacleLimbA);
  - Bellows (no render node).
- The five grown limbs go on an EARLY S1 design sheet (ruled): he keeps or sends back each, and FOUNDRY builds what he
  keeps. This includes real art for the three placeholders above.
- Confirm the cast-review redo wave landed. On 2026-09-29: 40 keep, 6 improve, 1 regen; 10 jobs queued, unverified since.
- The half-transformed tree, still owed by the sheet.
- The visible sink and shake tell animation (Q6 ruled: build).
- *Rider for the S1 art sheet:* one row for the donor/port overlap. `AA_OcularJelly` shares the roster with
  `RM_Gawpsack`, and `AA_InfectedAerofleet` with `RM_Blisterfloat`.

**Mechanics.**

- *In scope, built:*
  - the Burn and the Bloom, with their tells;
  - `RM_BurnDose`;
  - the Coalescence (3 stages, Unfinished emission, Burn collapse into Monstrous samples);
  - the Cloud Repulsor and its ship variant;
  - the Sunbeam as a weapon;
  - the genome loop and the 5 grown limbs;
  - the Unfinished spawner;
  - Draftprints and the Helix contract;
  - 11 settings.
- *In scope, to build (ruled):*
  - the Sunbeam arrest: a slow Contagion-touched condition, which a Sunbeam treatment freezes. Current mutations stop
    and stay; later exposure starts it again (Q3);
  - a plain mulch item: Coalescences and Unfinished drop it and it works as fertilizer, with no sunned or raw states and
    no field infection (Q4);
  - the Cloud Repulsor and Sunbeam as quest rewards plus a visiting Helix trader, added if none exists (Q5);
  - the visible gawpsack sink and rattlegrope shake before a Burn (Q6).
- *Proposed deferral:* the Dive and Bodyprints, parts 2 and 3 of `CONTAGION_GPT_ENRICHMENT_1`, which were never on the
  build list.

### 1.3 LeaningScrub

**Experience (sheet `design/Jawa/worldbuilding/biomes/arid_shrubland.md`):** a flat, wind-scoured fuzz plain under a low
sun. A knee-high canopy leans one way across the whole map, and the wind never stops except in the Stall.

**Machine rows.** The 2026-10-08 suite had 68 components in 17 chains: defs, patches, settings, fauna, flora, stall,
gale, lash, smother, dripping, crown, bloom, stamp, forms, four_forms, sweetline and log. The result was 50 PASS /
1 FAIL / 17 UNMEASURED. The suite has grown since (four more venomvine forms, sweetline guardians and felt), so the
manifest's row count comes from a fresh run on day 2.

| row | what closes it | kind of fix |
|---|---|---|
| `bloom.bloom_toggle_off_quiet` FAIL, plus the 2 bloom rows downstream of it | With `runwayBloomEnabled` OFF, Flee jobs still appeared. Decide whether this is a mod defect or a harness fault (other flee sources) before changing anything | diagnose |
| 12 `forms.*` rows | The live DLL exposes `ProofForm(String)`, and the harness calls a 2-parameter version. Fix the signature on one side | harness/DLL |
| `stamp.*` (2) | No loaded creature carried `RM_FireStamperExtension` on `acc_biomes-15`. `biomes_sprint` loads UtinniPatches and SWBestiary, which should clear this | tier |
| `dripping.dripping_survives_harvest` | The harvest never finished within 1200 ticks. Give the window more time, or pre-position the pawn | harness |
| New, needing a Scrub site | The Lean: the heading locks per map, animals flee upwind, fire biases downwind. `LEANING_SCRUB_LEAN_SITE_1` is cited in code but missing from the ledger; it gets filed | new rows |
| New rows (Q7-Q10 ruled) | Calling-pyre availability and each of its three belief variants; vaporator placement and the wake capping and healing; ripple concealment by weather, with the shimmer; ruins and living camps present on a generated map | new rows |

Proposed INFERRED row, to be pre-approved: downwind fire bias, scored from a compressed run plus the heading-lock row.

**Visual bars (draft):**

- *Must show:*
  - The ground reads as one soft fuzz carpet, leaning the same way across the map, dotted with near-black venomvine
    islands, never vanilla grass.
  - Under the Gale the map reads as driven: dust and fuzz moving.
  - Under the Stall, small animals hold still while big ones move.
  - Each venomvine form can be told apart from the others at play zoom.
  - A sweetline tree stands out as a named landmark, taller than the scrub.
  - The wild cast reads as distinct animals in one line-up.
  - Hidden small creatures show a faint shimmer under the fuzz.
  - The map holds ruined farmsteads and fields and inhabited camps, each reading as a place someone lived or lives.
  - A vaporator reads as a working moisture farm.
  - A runway bloom sends dustflutters up in a burst. This is checked by a flight-state read only; flight is never
    filmed or live-tested without him.
- *Cannot show:*
  - A windless map.
  - Leans in mixed directions.
  - A donor-art stand-in.
  - A magenta square.

**Art set:** see §3, plus the vaporator look, the camp kit and the calling-pyre art, each a sheet round.

**Mechanics.**

- *In scope, built:* the Stall and Gale calendar; the Lean v1; smother-craft; the twitcher lash; fire-stamping
  thunderstep giants; the soundscape on vanilla sounds; the dripping, crown, bloom and sweetline systems; 11 venomvine
  forms; sweetline visitors; vissler-arm scavengers.
- *In scope, to build (ruled):*
  - the calling-pyre ritual, with all three belief variants: forbidden, last rite and venerated (Q7);
  - a plain vaporator, learned by studying a dead farmstead, with no drying scar; one art-sheet round for its look (Q8);
  - the ripple: small creatures hide under the fuzz, with a faint shimmer over the hidden ones (Q9);
  - set-pieces: the ruins (dead farmstead, smother-claimed field, hedge homestead) plus living camps (Q10). The camps
    need a faction choice (new question N1).
- *Agent default, not asked:* no Lean heading readout. The lean shows in the plants themselves (the first bar), and his
  trim law reads *"Too much focus on constant advanced warning... Players arent that into it."*

**Venomvine sitting.** `LEANINGSCRUB_VENOMVINE_SITTING_1` is his own deferred sitting (*"Venomvine is a mechanic as well
as graphics... during Bench settings"*, 2026-10-08). It needs him and the game on a Scrub map, with the run sheet at
`Transient/venomvine_sitting_runsheet_2026-10-09.md`. It is folded into the S2 LeaningScrub review save, so it costs no
extra sitting.

---

## 2. His rulings, and the questions they created

### 2.1 Rulings on the kickoff cards (2026-10-15, all RULED)

Where he typed words they are quoted exactly. Where he took a card, the card's question and option are given. The
alternatives he did not take are deleted. All are notes on `BIOME_SPRINT_PROVE_SCRUB_SETS_PACE`.

**Dropped as already settled; never asked again:**

- **Cauldron falter-tell foreknowledge** — settled by the build (see §0).
- **Contagion grown limbs** — *"Approved, this looks great!"* (2026-09-27); built. His later card asks for an early sheet
  anyway (below).
- **Calling-pyre concept** — merged with the controlled waking by card on 2026-10-01.
- **Sound for all three biomes** — vanilla sounds, by his ruling of 2026-10-03.
- **The Zizzik rite cap** — *"Just leave them all for now"* (2026-10-02).

**Cauldron**

- **Q1, vent gas: RULED.** He typed: *"Drifting gas clouds plus the native gas system already built into rimworld"*.
  Vents emit real drifting gas clouds, built on the game's own gas system. The burning mechanism is left open (N2).
- **Q2, extras: RULED.** He typed: *"Everything except the Seismometer. I don't like that idea."* In: the Filter-Works,
  the ruin set-pieces and the Oomo shrine. Cut: the seismograph.
- **Falter warning length: RULED by card** (*Cauldron falter warning length → About one in-game hour*). The target is
  about one in-game hour before a vent bloom; the built tell is checked against it on the first live round.

**Contagion**

- **Q3, Sunbeam arrest: RULED.** He typed: *"Stops current mutations. No protection if you get exposed again later."*
  The Sunbeam freezes the corruption where it stands. It gives no immunity. The source of the condition is open (N4).
- **Grown limbs: RULED by card** (*Grown limbs this sprint → Design sheet early, build the keepers*). The built five are
  reviewed on a sheet at the first art sitting, and what he keeps gets built or finished.
- **Q4, mulch: RULED by card** (*Contagion mulch scope → Plain fertilizer only*). One fertilizer item. No sunned or raw
  states, no field infection.
- **Q5, who sells the Repulsor and Sunbeam: RULED by card** (*→ Quests plus a visiting Helix trader*). Agents find whether
  a Helix trader exists and add one if not.
- **Q6, Burn tell: RULED by card** (*Build the visible Burn tell motion → Build the visible sink and shake*).

**LeaningScrub**

- **Q7, calling-pyre: RULED by card** (*Calling-pyre size → Ritual plus all three beliefs*): forbidden, last rite and
  venerated. The precept shape is open (N3).
- **Q8, vaporator: RULED by card** (*Vaporator scope → Plain vaporator, no scar*). Learned from a dead farmstead; one
  art-sheet round.
- **Q9, ripple: RULED by card** (*Ripple → Hiding with a faint shimmer*).
- **Q10, set-pieces: RULED by card** (*Scrub set-pieces → Ruins plus living camps*). The faction is open (N1).

**Process**

- **Q11, who builds: RULED by card** (*Who builds during the biome sprint → FOUNDRY builds, BENCH tests*). BENCH runs the
  live tests and integrates. The swept-files risk (plan X3) is managed by committing explicit paths and building DLLs from
  clean exports.
- **Q12, response time: RULED by card** (*How fast can you answer a packet → Within a day*). The calendar assumes one day
  per reply.

### 2.2 What the rulings added to the work

The ruled scope is larger than the draft recommended. Rough builder-days, FOUNDRY, including FOUNDRY's own offline
checks but not BENCH's live rounds:

| item | builder-days |
|---|---|
| Cauldron: drifting vent gas and burning | 2-3 |
| Cauldron: Filter-Works (new FlowWorks liquids, building, cartridges) | 2 |
| Cauldron: ruin kit and Oomo shrine, with art rounds | 1.5-2 |
| Contagion: arrest condition, mulch, Helix trader and quests, visible tell | 3.5 |
| Contagion: finishing the limbs he keeps | 0.5-1.5 |
| Scrub: calling-pyre with three beliefs | 3 |
| Scrub: plain vaporator and study source | 1.5 |
| Scrub: ripple with shimmer | 1 |
| Scrub: ruins and living camps | 3 |
| **Total** | **about 18-22** |

Per mod, in sequence: Cauldron about 6-7, Contagion about 4-5, Scrub about 8.5. Scrub is the critical path.

### 2.3 New open questions (card-ready)

These are the only questions left. Each has a "leave it out" or default choice, so an unanswered card never blocks the
other biomes.

**N1. Which faction lives in the Scrub's living camps?**

You chose ruins plus living camps. A camp needs someone living in it, and the Scrub's setting has more than one
candidate.

- **(A) Scavenger clans (Jawa-type), the wanderers of Ash'karr — recommended.** They fit a flat, wind-scoured plain and
  the "scavengers wearing a vissler arm" already built. The roster, pawn kinds and trade lines mostly exist, so it is
  the cheapest option. The risk is that the Scrub reads like every other scavenger map.
- **(B) A new Scrub-only people who farm the vaporators.** This is the strongest tie to the biome's economy and to the
  dead farmsteads they could be the heirs of. It means new pawn kinds, art and a faction def, about two more days, and
  more sheets for you.
- **(C) Passive settlers who never fight and trade only.** They are cheap and cannot make the map dangerous, but a camp
  with no threat is a decoration.
- **(D) Leave the living camps out and ship the ruins only.** This reverses part of your ruling, so only if you choose
  it.

**N2. How should vent gas burn, now that it drifts on the game's gas system?**

The game's gas list has no burnable gas, and you want real drifting clouds. Fire in a cloud needs a rule.

- **(A) Use an existing gas for the cloud and add a fire rule on top — recommended.** The vent cloud is a real drifting
  gas. Our code watches for fire touching a cell where the cloud is dense, then flashes and releases toxic smoke. It
  looks and behaves right, is small, and cannot break other mods' gases. The cloud is not a unique gas type underneath.
- **(B) Add a new gas type to the engine through patches.** This is the purest version, with a gas that is fully its
  own. It is the riskiest build of the sprint and could disturb other mods' gases.
- **(C) Drifting clouds that never burn.** This is the cheapest, and it drops the "burns into poison smoke" drama you
  ruled on 2026-09-28.

**N3. Where do the calling-pyre's three beliefs live in the ideology?**

Forbidden, last rite and venerated need a home, since a precept belongs to an ideoligion.

- **(A) Three precepts attached to the fire and ritual memes that already exist — recommended.** Any colony that picks
  those memes can choose among the three. It reuses existing content and keeps the cost to about three days.
- **(B) One new Scrub-only meme that carries all three.** This ties the ritual to the biome and gives the Scrub its own
  ideology flavour. It adds a meme def, its art and text, and one more review, about one extra day.
- **(C) Three precepts available to every ideoligion.** This is the simplest, and it makes the ritual show up in
  colonies that have nothing to do with the Scrub.

**N4. What exposes a colonist to the Contagion's condition, so the Sunbeam has something to stop?**

You ruled that the Sunbeam stops current mutations and gives no protection later. That needs a condition that starts
somewhere.

- **(A) Time spent outdoors under a Bloom, building up slowly, and a stronger dose in a Burn — recommended.** The
  Bloom is already the biome's threat. Shelter, the Cloud Repulsor and the Sunbeam then each have a job. About a day.
- **(B) Only a Burn exposes you.** This is simpler and rarer, and the Bloom stops being dangerous to people.
- **(C) Only contact with the Unfinished and Coalescences.** This is the safest to build, and it makes the Contagion a
  creature threat and takes the sky out of it.

---

## 3. LeaningScrub art redo

**Most of the art already exists; do not queue new renders before checking the list below.** Measured on 2026-10-15
with `artpipe_state.py find leaningscrub_` and the sheet's decisions file.

**What exists**

- **Renders.** 68 of the 69 filed redo jobs have renders on disk, under `D:\Luke\dev\_artpipe\_artsrc\leaningscrub_<id>_*\`.
  - The job file is `Transient/biome_ffar/leaningscrub_redo_jobs_2026-10-05.json`. Its 69 jobs make the item's "119"
    stale.
  - Only `leaningscrub_sketto_v2` is missing.
  - Plant variants with renders: the b/c (or a/b/c) variants of brambles, aridgrass, creepstern, crimsoncushion, dervish,
    six venomvine forms, cruststar, fuzz, grellbush, grellspine, pillowmoss, tanglefuzz, whipfuzz, wild healroot and wild
    nysyllin.
  - About 26 creature renders also exist.
- **The sheet already shows them.** `Transient/biome_ffar/leaningscrub_sheet_2026-10-05.html` was rebuilt on 2026-10-14 with
  70 render names. Its decisions file, `leaningscrub_sheet_2026-10-05.decisions.json`, has 86 rows. His rulings are copied
  to `infrastructure/state/art_rulings/2026-10-08_leaningscrub_sheet_2026-10-05.decisions.json`, and 63 rulings were
  ledgered on 2026-10-08.
- **Installed.** 99 PNGs in `src/RimMandrake/LeaningScrub/Textures`. Many of the cast live in SWBestiary and the patch
  mods instead; the 2026-10-05 pass installed Fuzz B, Gorg, Eopie, Iriaz, Mudhorn, Ronto, Skalder, Worrt and others.
- **Texture check.** No broken texPath: 84 texPaths were checked against local PNGs, and the 8 unmatched ones are
  vanilla Core paths.

**What is owed, net of what exists**

1. **His picks on the new variant renders.** Fuzz, Tanglefuzz, Whipfuzz, WildHealroot (a/b/c), Nysyllin_Wild (a/b/c),
   Brambles, CreepStern, and the redo creatures still marked redo: Chikka, Convor, Kybuck, ScrapNestBird. Once picked,
   they install as `<Name>_<letter>.png` variants through `art.py enact`.
2. **Port three donor plants to owned `RM_` defs.** These are pure agent work; his picks are already made.
   - `Plant_Brambles` (pick B);
   - `RG_Plant_CreepStern` (pick B);
   - `RSW_Durrok` (pick B; it shares the `AA_Wildpawn` path, and its description must be rewritten to match the picture).
3. **Re-picks.**
   - `RM_VenomvineThicket` B was refused because the picture was purged by his own mark. It is held for the venomvine
     sitting.
   - `RSW_Nuna`'s pick F has no ruling id, so it is re-confirmed on the sheet (the current decision is A).
4. **Venomvine.** His card of 2026-10-09 already decided that the owned venomvine renders replace the thicket copy on
   the other venomvine plants. The art ledger cannot install over a kept sha on a card path
   (`Transient/belt_art_enact_20261009.md`). **This is not a new question.** It needs one typed sentence from him at S0
   (recorded with `--owner-said`), or the S2 venomvine sitting. Quench and Rearing ("STOP USING THIS GRAPHIC AND MAKE
   VENOMVINE") get new renders only once the sitting confirms those forms stay.
5. **Dustflutter numbers.** The 0.3-cell size is done. "In great numbers" still needs his call on group size (proposal:
   8-20), density and ecosystem weight. This is a rider on the S1 sheet, as one number row.
6. **ScrapNestBird flying frames.** His note was "Make flying frames". No frame job is filed; today it borrows
   Whisperbird's flip-book. File a whole-body directional flip-book job. It is verified by a `Pawn_FlightTracker` state
   read only. Any visual check of flight is a joint session at S2, never unattended.
7. **Small items.**
   - Run Sketto v2 north/south.
   - The Lothcat north/south replacements (jobs done) and the Eopie and Scurrier male replacements (queued) unblock the
     8 remaining purges from `Transient/leaningscrub_conflict17_2026-10-08.md`.
   - Check that the `RSW_Kreetle` 0.3-cell drawSize change landed.
   - Check whether the `RSW_TunnelSnake` row is stale: `RM_TunnelSnake` already exists with 3 PNGs.

**Fastest route to his look (about 10-15 owner minutes, at S1)**

1. Run `refresh_sheets.py --dry-run --only leaningscrub`. The sheet was rebuilt on 10-14, so this is likely a no-op. If
   it changed, refresh and run `remap_decisions.py`.
2. Add the riders as rows on the same page: the Cauldron and Contagion art, the five Contagion grown limbs (reviewed
   early, ruled), the Dustflutter numbers, and Nuna. The Cauldron Filter-Works, ruins and Oomo shrine, and the Scrub
   vaporator, camps and calling-pyre, each get a concept sheet round once their art is drawn (D2-D3).
3. Gate with `scaled_review_gate.py check`, serve with `serve_gated.py`, and send him the URL plus the full path. He only
   needs to look at the rows not yet picked; the rest keep his earlier picks.
4. When he says done, run `art.py enact <decisions.json>` as a dry run, then `--apply`, with `--hold` on the venomvine
   rows.
5. In parallel, needing no new art: the three donor ports, the ScrapNestBird frame jobs, and Sketto v2.

A second round (S1b) happens only for rows he sends back.

---

## 4. Sprint schedule (re-estimated for the ruled scope)

**Honest estimate: about 14-16 calendar days, sign-off around Fri 10-30 to Sun 11-01.** The draft said 7-10 days. The
ruled scope adds roughly 18-22 builder-days (§2.2). FOUNDRY builds, so builders can run per mod in parallel, but the
Scrub alone is about 8.5 builder-days in sequence, and every build then needs a BENCH live round, an art sheet round and a
separate reviewer. If FOUNDRY cannot field three parallel builders, add about 4-5 days. The owner's reply interval is
one day (Q12), and it applies to each sheet round, of which there are four or five, so owner latency is about 5 of the
14-16 days.

Owner sittings are marked **[S#]**. FOUNDRY builds; BENCH runs the tooling slice, the live rounds, integration and the
review saves.

| day | FOUNDRY (builds) | BENCH (tests, integrates) | owner |
|---|---|---|---|
| **D0 (Fri 10-16)** | Starts on the questions-independent work: the Cauldron gas clouds up to the open N2 point, the Contagion mulch and Helix trader. | Send this packet. File `LEANING_SCRUB_LEAN_SITE_1`. Close the pilot's C5 once the nightly selftests are green. Tooling slice, at most one agent-day: the `biomes_sprint` tier in `modset_builder.py`; the preflight; biome sites in `test_site_saves.py`, proven on Cauldron first. | **[S0] about 45-60 min.** Approve the three lists in §1; answer N1-N4. Dictate `### the experience` per biome (can wait until S2). Sign off the pilot (C6). One typed sentence restating his 2026-10-09 venomvine-art card (§3 item 4). |
| **D1 (10-17)** | Contagion: arrest condition, visible tell. Cauldron: gas and fire per N2. | Freeze the three acceptance manifests from his S0 answers and record their hashes. Build the Cauldron and Contagion sites. One live round at one HEAD; check the falter tell against about one in-game hour. Harness fixes (Contagion off-biome arm and surgery fixture; Cauldron suush spacing, vexxiss pen, yield rerun). Build the early art sheet (§3) with the five grown limbs. | **[S1] about 40-60 min.** The LeaningScrub art sheet with riders, and the grown limbs. |
| **D2-D5** | Cauldron: Filter-Works, ruins, Oomo shrine. Contagion: the limbs he keeps, Helix quests. Scrub: calling-pyre with three beliefs, then vaporator. | LeaningScrub harness (`ProofForm`, bloom toggle diagnosis, Scrub site, fresh row count). Install his art picks. Live rounds as builds land; a separate reviewer marks files CLEAN. | **[S1b, S1c] 15-30 min each:** art sheets for the Cauldron kit and the vaporator, one day each reply. |
| **D6-D10** | Scrub: ripple, ruins, living camps. Contagion and Cauldron fix-ups from live rounds. | Second live round Cauldron and Contagion, target 0/0. Camp and ruin placement rows on the Scrub site. | **[S1d] 15-30 min:** camp kit art sheet. |
| **D11-D12** | Fixes. | Build the three review saves with key sheets (Pyrelands pattern), every visual bar plus the venomvine forms and the grown limbs. Live round for LeaningScrub. | — |
| **D13 (about 10-29)** | Standing by for rejections. | Final one-HEAD round for all three, plus the pilot guards (M6). `rimflow verify` per line. | **[S2] about 75-105 min, game up.** Walk the three review saves; accept or reject each bar (O2); venomvine sitting; any flyer look with him present. |
| **D14-D16 (buffer)** | Redo whatever S2 rejected. | Rerun only the suites whose inputs changed (plan X4). | **[S3] about 10 min:** the sign-off card citing the three manifest hashes (O3). |

**Owner total:** about 4.5-5.5 h active in 6-8 sittings (the draft said 3-3.5 h). That is more than plan Option 2's
estimate, and it is the cost of the larger scope. The critical path is the Scrub build chain (calling-pyre, vaporator,
ripple, ruins and camps), then S2.

**If an answer is late:** the agents carry on with the other biomes and the harness work, which need no answers. N1 gates
the camp half of Scrub set-pieces (D6+), N2 gates Cauldron fire (D1), N3 gates the belief half of the calling-pyre (D2),
N4 gates the arrest condition (D1). Silence is never approval.
