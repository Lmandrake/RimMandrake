<!-- status: design brief — nothing here is built -->
# The Gelatinous Slime Biome — GELATINOUS_SLIME_MOD_1 (RimMandrake tier)

_Design brief, 2026-09-10, Fable pass. Supersedes and absorbs
`design/Jawa/worldbuilding/creatures/RUT_slime_transformation_system.md` (v1, commit
`beaf2687`) — that file is now a pointer here; git is the provenance. This doc
**specifies**: no XML, no C#, no art. Every rule INVENTED here rather than derived
from a ruling, sheet law, or measurement is flagged **[INVENTED]**._

**The ruling this executes (owner, 2026-09-10, verbatim):** *"This feels like it
should be made into a RimMandrake-level mod: the Gelatinous Slime Biome (with full
credit to inspiration from Alpha Biomes). Creates the Biome, the strange
relationship to genetic archiving, the machine that allows a player to select a
target gene, identify it, extract some slime and inject it into their body,
collapse into coma and then... turn into slime unless they have a friend nearby to
administer the slime antidote in time. … With this cool concept, we don't need to
make this have anything to do with Star Wars. It's universal. Make sure we pull
everything in that belongs here, but nothing more."*

**Companion rulings folded in as LAW (same sitting):** colonists ride the **full
ladder to dissolution** (option 1); slimified creatures are **never hostile**
(confirmed); GR_Chickenrabbit is renamed **MURREL** (campaign-side, §9); and the
caravan question is answered by a new mechanic — **drying biomes**: desert/arid
(maybe the salt ocean) **halt slimification**. Cure geography: the threat has a
map-scale answer — walk it dry (§4).

## 0. Identity and naming (per `design/NAMING_SCHEME_PLAN.md`)

| surface | value |
|---|---|
| tier | **RimMandrake** — passes the test: *a medieval-tribe player installs this alone and understands it* |
| packageId | `mandrake.rm.gelatinousslime` |
| display name | `RimMandrake: The Gelatinous Slime` |
| defName prefix | `RM_` throughout — **no `RUT_`, no Star Wars references anywhere in the shipped mod** |
| folder | `src/RimMandrake/GelatinousSlime/` |
| C# namespace | `RimMandrake.GelatinousSlime` |
| About.xml credit | explicit, per the owner's words: *"Inspired by the Gelatinous Superorganism of Alpha Biomes — full credit to the Alpha Biomes team for the original concept."* Inspiration credit, NOT a dependency: the mod ships standalone (§1) |
| DLC posture | biome + slimification ladder: **base game**. The gene machine (§5) requires **Biotech** (genes are Biotech machinery — `Pawn_GeneTracker`); without Biotech the machine does not spawn and everything else works. Honest split, stated in About |

**Lore register (universalized):** an ancient bioweapon that ate everything it was
sent against and was unmade by victory — now a country-sized body that reads
everything that touches it, a living genetic archive still filing entries for a
master long dead. No named factions, no named war, no named planet: the archetype
travels. (The Assailant framing, the Rot siblingship, and every campaign name stay
behind — §1.)

---

## 1. The gather pass — everything that belongs, nothing more

### PULLED IN (becomes RM_ content)

| material | source | disposition in the mod |
|---|---|---|
| The biome concept whole: living-registry body, walking-on-it-is-being-read, movement-punishing terrain, footprints, forage "edible barely," no natural rock, compressor economy, farms-fail-by-conversion, slime rain (organism-induced, potable), eat-slime-cures-poison-then-the-clock-runs | `biomes/the_slime.md` §1–§5 | `RM_GelatinousSlime` BiomeDef + authored terrain suite + weather + buildings (§2). ⚠️ The campaign's terrain/compressor are Alpha Biomes DONOR defs — the mod authors its OWN equivalents (def + art cost inventoried §7); nothing of AB's is shipped or required |
| The slimification ruling (~1-week conversion, resistance-or-transformation) and the v1 four-stage ladder, colonists included | sheet §3 + v1 brief | `RM_Slimification` hediff, §3 — colonists FULL ladder (ruled) |
| The genetic-archive relationship: distributed circulating genome, "every genome that ever touched it is in circulation," trace-tail-as-experiments register | sheet §3–§4 | The machine's fiction (§5) + biome lore text. The trace-tail *concept* ships as lore + the dynamic-visitor system; the campaign's specific AA/GR experiment creatures stay behind |
| The gene machine: select target gene → locate in the currents → the vulnerable walk → coma → antidote race | sheet §7 + owner's new verbatim flow | Fully specced §5 — the mod's centerpiece |
| The verified gene-grant primitive: `AddGene` + `XenogerminationComa`, zero new gene-storage code | `biomes/edible_genepack_native_mechanism.md` (IL-cited, FROZEN) | §5's engine backbone — the machine's inject step calls exactly this pair |
| Machine framework laws from the accepted gene-lists doc: **P4** anti-exponential (every gene is a trade), **P5** riders visible AND felt, **P7** Slime-marked romance/opinion penalty per machine gene, **P8** heritable endogenes | `biomes/the_slime_gene_lists.md` (FROZEN/ACCEPTED) | Carried as the machine's universal design grammar (§5d). The doc's actual A/B gene LISTS are campaign property and stay behind |
| The antidote concept: an intentionally toxic injection that kills the slime in you before conversion completes | sheet §3 / `the_rot.md` | `RM_SlimeAntidote`, universalized (§6): craftable purgative; the campaign re-sources it as Rot-derived in the RUT layer |
| v1's art strategy (shared overlay), spike scoping, Contagion-distinction grammar (film/tint/drip, never eyes, never buds) | v1 brief | §7, §8; the never-eyes grammar survives as the mod's own art law even with the Contagion left behind |
| Drying-biome halt (new ruling) | owner card | §4 |

### DELIBERATELY LEFT BEHIND (stays campaign-side; the thin RUT layer, §9)

| material | why it stays |
|---|---|
| All Star Wars content: the SW-race gene lists (A1–B25, Nautolan/Wookiee/etc. provenance), Mnggal-Mnggal fear, P1–P3 curation rules (SW provenance/Force/bloodline exclusions) | Owner: "nothing to do with Star Wars." The frozen `the_slime_gene_lists.md` stays the CAMPAIGN's archive contents, loaded via the RUT layer |
| Assailant-weapon origin, Rot siblingship, the pharmacological entanglement lore, the Throat experiment, terminator/dead-river placement, R-H1 rain carve-out | Ash'karr canon — names the planet and its history |
| The Ascendant Helix vendor role, Wildsteam disapproval, farm-ruins inhabited objects | Campaign factions and map dressing |
| The campaign CAST: AA_GreenGoo substrate, the acanthamoebas, AA_OvergrownColossus, AA_TeratogenicOriginator, the AA/GR trace-tail (Mime/DecayDrake/etc.), **Murrel** (né GR_Chickenrabbit) | Alpha Biomes / Vanilla Genetics defs — third-party content we cannot ship; they remain the campaign INSTANCE's residents (§9) |
| The Contagion's ocular mechanism | A different weapon-fate; the distinction (v1 §0) is campaign canon. The mod keeps only the resulting art law: film/tint/drip, never eyes, never buds |
| The Slime Pit cuisine chain's cross-biome gourmet wiring | The building generalizes (pulled in, §2); the three-biome gourmet CHAIN is campaign |
| `EDIBLE_GENEPACK_NATIVE_1`'s campaign gating (gene lists authored first) | The mod's machine replaces that dependency for ITSELF; the campaign item's status is unchanged until the RUT layer lands |

**Architecture ruling proposed:** the campaign's Slime becomes an **instance /
consumer of the universal mod** — the RUT integration layer (§9) points the
campaign biome at the mod's systems and swaps in campaign content. One mechanic,
two skins; the frozen campaign sheets stay authoritative for the campaign skin.

---

## 2. The biome — `RM_GelatinousSlime`

Authored equivalents of everything the campaign borrowed from the donor (all-new
defs and art, inventory in §7):

- **Terrain suite** (5–6 TerrainDefs): hardened slime (buildable-ish, slow), rich
  slime, slime-grass (fertility 1.0 — the farm lure), slimy mud, liquid slime.
  Movement difficulty high; footprints always. **[Values at build; donor values
  are the calibration reference, not the source.]**
- **The substrate creature** — `RM_Gelatid` **[INVENTED name]**: slow goo-herd
  cells of the body itself, the biome's always-visible native. Resistant by
  identity.
- **Flora**: slime-grass + 2–3 pseudo-plants (rounded, soft-bodied silhouette
  language per the sheet's §9 register, genericized).
- **Weather**: `RM_SlimeRain` — organism-induced, brief intense flooding,
  fast-draining, **potable** (the body waters itself; the mod carries the fiction
  without Ash'karr's R-H1 law).
- **Buildings/economy**: `RM_SlimeCompressor` (ooze → building stone — the no-rock
  economy), `RM_SlimePit` (render-down cuisine vessel), raw slime as barely-food.
- **Farms fail by conversion**: cultivated fields on slime terrain revert within a
  few harvests (small C#, §8 build list).
- **The universal antitoxin**: eating slime instantly cures poisons and most
  radiation-analog hediffs — and applies `RM_Slimification` at stage 1+ severity
  bump. The wondrous and the fatal are one mechanism.
- **Worldgen**: the biome generates on new planets (temperate-wet band placement
  **[INVENTED — build call]**), rare. *(Campaign note: Ash'karr worldgen is
  frozen/hand-authored — the RUT layer places the campaign instance; the mod's
  worldgen serves other players' planets.)*

---

## 3. The slimification ladder — `RM_Slimification` (v1 carried, three laws folded in)

Unchanged from v1 except where marked: one hediff, severity 0→1.0 over ~7 days
on-biome; stages **TOUCHED** (0–0.2: sheen, −5% move, self-reverses off slime
terrain) → **SLICKED** (0.2–0.5: green tint, −15% move/−10% manip/−10% sight,
behavior unchanged, no longer self-reverses) → **HALF-ABSORBED** (0.5–0.9: heavy
overlay, −40% move, pain ×0, **placid** — stops fleeing/hunting) →
**RETURNED-TO-FLOW** (1.0: dissolution, no corpse, slime smear + raw slime).
All numbers **[INVENTED]**; the 7-day total is ruled.

**Laws (owner, 2026-09-10):**

1. 🔴 **Colonists ride the FULL ladder** — all four stages, dissolution included.
   Humanlikes get the alert cascade (stage 1 letter, stage 2 "spend the antidote
   or leave" alert, stage 3 red alert with the clock). The resistance economy is
   therefore real: the mod ships resistance as an acquirable state (§5's
   archive carries a slime-resistance gene at the machine's standard price;
   campaign adds the mycoid-symbiote route in the RUT layer).
2. 🔴 **Never hostile** — no slimification stage ever grants aggression, manhunter,
   or faction change, on any creature, ever. (The library files entries; it does
   not recruit soldiers.) Standing rule for FOUNDRY.
3. 🔴 **Drying biomes reverse it** — §4.

Reversibility ladder, restated with §4: stage 1 self-reverses off slime terrain;
stages 2–3 **hold** in ordinary biomes, **decay** in drying biomes, and clear
instantly with the antidote (§6); stage 4 is final.

---

## 4. Cure geography — the drying biomes (owner's mechanic, replacing any caravan exemption)

**The ruling:** desert and arid biomes (maybe the salt ocean) **halt
slimification** — dry heat and desiccation kill the film. Severity in a drying
biome doesn't just hold: it **decays** (full clear from stage 3 in ~4–5 days
**[INVENTED rate]** — slower than it grew; the walk must be earned).

- **Mechanism:** `RM_DryingBiome` ModExtension on BiomeDef. The mod tags vanilla
  `Desert`, `ExtremeDesert`, `AridShrubland` **[+ owner's "maybe the salt ocean" —
  no vanilla equivalent; left as the RUT layer's call for Ash'karr's salt
  registers, §9]**. Any mod (or the campaign) tags its own biomes by adding the
  extension — the cure geography is data, not code.
- **World-scale:** the check runs for CARAVAN pawns by world-tile biome, not just
  map pawns — a caravan that leaves the Slime through desert country dries out on
  the road. This is the answer to AI/caravan losses: trade caravans path away
  through dry land and survive naturally; no scripted exemption, no special case.
  (World-pawn hediff ticking is real C# — priced into SPIKE A, §8.)
- **What the player learns:** the Slime's threat has a *map answer*. Settle beside
  it with desert at your back and the biome becomes farmable-adjacent risk;
  settle in its wet heart and every trip is a countdown. The biome placement
  itself becomes the difficulty slider.
- **Fiction:** the read requires the medium — the film is the Slime's reach, and
  it cannot live dry. (Also quietly explains why the body sits where it's wet and
  why deserts border it as scar tissue.)

---

## 5. The machine — `RM_GeneArchiveConsole` (Biotech required)

The owner's flow, verbatim, specced step by step: **select a target gene →
identify → extract some slime → inject it into their body → collapse into coma →
turn into slime unless a friend administers the slime antidote in time.**

### 5a. SELECT — the archive menu

A building (`RM_GeneArchiveConsole`, buildable only on/adjacent to slime terrain
**[INVENTED constraint — the machine reads the body; flagged]**). Opening it lists
the **archive**: the curated target-gene list. The universal mod ships a default
list drawn from **vanilla Biotech GeneDefs** framed as "what has wandered in over
the centuries" — robust ears, night vision, strong melee, fast runner, the
slime-resistance gene, etc. **[Default list curated at build under the P-laws,
§5d.]** The list is a def-list the campaign (or any mod) replaces — this is how
the frozen SW gene lists become the CAMPAIGN's archive without touching the mod
(§9).

### 5b. IDENTIFY + EXTRACT — the vulnerable walk

The archive is a circulating library (ruled): the gene you want is *somewhere on
the tide*. The console computes **where the current carrying it will pass** — a
map cell on the slime, marked with a countdown window **[INVENTED: window ~1–2
days]**. A pawn walks there with an empty `RM_ExtractionCanister`, works the
extraction job standing in the open on the body (a real job with a work timer —
minutes of exposure, slimification ticking, ambient fauna wandering), and comes
back with **`RM_GeneSlurry`** — extracted slime holding the target gene.
Slurry is perishable (~5 days unrefrigerated **[INVENTED]**): the archive does
not keep, it circulates — no stockpiling a gene bank (this is the mod's
no-shelf-stable-extraction law, generalized from the sheet's ban 6).

### 5c. INJECT → COMA → THE RACE

Injection is a use-action on a pawn (self or doctor), anywhere — including home
in bed, which is the point: *bring it back to your people.* On injection:

1. **The genes land immediately** — target gene **plus one hidden rider gene**
   rolled from the archive's rider list (the "something fun but odd," ruled).
   Engine: exactly the verified primitive — `Pawn_GeneTracker.AddGene` per gene,
   then the coma (`edible_genepack_native_mechanism.md`, IL-cited: zero new
   gene-storage code). Genes are **endogenes** (P8, ruled: heritable — the
   bloodline is a decision made one coma at a time).
2. **The coma**: vanilla `XenogerminationComa` semantics, plus the injection
   applies `RM_Slimification` at stage 2 with a **fast clock** — the concentrated
   slime converts in ~3 days, not 7 **[INVENTED: 3d]**. The pawn is down; the
   countdown is visible.
3. **THE RACE**: a friend must administer `RM_SlimeAntidote` (§6) **after the
   genes integrate, before dissolution**. Antidote given during the coma kills
   the slime — the pawn wakes on the coma's own schedule, genes kept, alive.
   No antidote in time → **returned-to-flow at the bedside**: dissolution, no
   corpse, a smear in the bed. The letter writes itself.
   - Grace design: coma ~2 days, dissolution at ~3 → a ~1-day administration
     window after wake-adjacent alerts **[INVENTED timings — tune at build]**.
   - **A lone pawn cannot do this and live.** That is the social mechanic the
     owner specced ("unless they have a friend nearby") and it ships as-is: no
     self-administration while comatose, no timer pause. Solo-colony players get
     one warning dialog at injection **[INVENTED: the warning]**.

### 5d. Why a player does this — the honest Biotech comparison

What exists (cited): Biotech gene acquisition is **random-find genepacks**, the
**gene extractor** (takes genes something already has, damages the donor), and
xenogermination (architite costs, random assembly of what you own). **Nothing in
Biotech lets you point at a gene you don't own and go get it.** That is the
machine's slot: **chosen genes, paid in risk instead of RNG** — the rider roll,
the coma, the antidote economy, the vulnerable walk, and the P-laws carried from
the accepted campaign framework: **P4** every gene is a trade (the default list
prices gifts with real costs, never pure upside); **P5** riders are visible and
felt; **P7** each machine gene stacks the **Slime-marked** social/romance penalty
— the marked are hard to love; **P8** heritable. The machine is a devil's bargain
engine, not a gene shop.

---

## 6. The antidote — `RM_SlimeAntidote`

- **What it is (ruled fiction, universalized):** an intentionally toxic purgative
  — poison aimed at the reader in your blood. Clears `RM_Slimification` at any
  stage below 1.0, and costs the patient a short toxic malaise (minor toxic
  buildup on administration **[INVENTED]**) — the cure is honestly a poisoning.
- **Acquisition:** craftable at the drug lab (neutroamine + raw slime — you make
  the antidote FROM the thing, ruled pattern **[INVENTED recipe]**); occasionally
  trade-stocked. Cheap enough to keep two in the fridge, dear enough that a
  caravan carrying none made a decision.
- **Campaign reskin (§9):** Ash'karr sources it from the Rot ("derived from the
  Rot," ruled) — the RUT layer swaps recipe/fiction; item behavior identical.
- **Administration:** doctor use-action, works on downed/comatose pawns —
  verified against real administration routes at build (Anomaly serum pattern —
  🔴 never guess a field; build seat verifies against RimSage).

---

## 7. Art strategy — carried from v1, plus the biome's own bill

**The transformation overlay (unchanged recommendation):** ONE shared green-tint +
drip overlay set attached via hediff render nodes — 2 overlay states × 3 size
buckets × 3 rotations = **18 sprites, flat forever**; species #13 costs nothing.
Bespoke-per-species (60+ and growing) rejected. Humanlikes now included (colonist
full ladder): +1 humanlike overlay bucket over apparel = **+6 sprites** (⚠️ the
apparel-layering question is SPIKE B's to answer). **Art law kept from v1: film,
tint, drip — never eyes, never buds, never new limbs.**

**The biome's own bill (new — standalone means authoring what the donor lent):**
terrain suite ~6 textures; flora 3–4 defs × 2–3 variants ≈ 9; `RM_Gelatid` ~3;
buildings (console, compressor, pit) ~3–5; slime rain effect + smear ~3; items
(slurry, canister, antidote, raw slime) ~4. **Biome total ≈ 28–32 sprites/textures;
grand total with overlays ≈ 52–56.** This is the real cost of "make it a mod" —
inventoried, not hidden.

---

## 8. The spike list — re-priced for the machine and the geography

Sizing per the twinkle-spike precedent: prove on ONE def, measure tick cost,
report.

| spike | proves | size (v1 →) |
|---|---|---|
| **A — LADDER+GEOGRAPHY** | biome-conditional hediff driver (apply/advance on slime maps, resistance gate) **+ drying-biome decay via ModExtension + world-pawn (caravan) ticking by tile biome** | **M → L** (the world-pawn leg is new) |
| **B — OVERLAY** | hediff render-node overlay on animal AND humanlike (over apparel) bodies, severity-staged, drawSize-scaled | S → **M** (humanlike/apparel added) |
| **C — DYNAMIC VISITORS** | ambient density: spawn pulls from **neighboring world tiles' biomes' wildAnimals** (universal — works on any planet, any mod set), arriving pre-staged | S → **M** (neighbor-biome read is new; replaces v1's hand-curated visitor list) |
| **D — DISSOLUTION** | stage-4 deathAction: no corpse, smear + raw slime, works in beds (the machine's failure case) | **S** (unchanged) |
| **E — THE MACHINE** (new) | console UI (gene list → pick), current-locator target + timed extraction job, slurry item, inject use-action calling the verified AddGene+coma primitive, fast-clock slimification, antidote administration on a comatose pawn | **L** — the largest piece; the gene-grant core is proven free (IL-cited), the job/UI chain is the work |
| **F — FIELD CONVERSION** (new) | cultivated soil on slime reverts over harvests | **S** |
| dropped | v1's optional flow-drift wander | cut — density now comes from SPIKE C |

Non-spike build: hediff/biome/terrain/weather XML, default gene list curation
under the P-laws, antidote recipe, About.xml credit, the art bill (§7).

---

## 9. The RUT integration layer (thin, campaign-side — separate small mod)

`mandrake.rut.slimeinstance` **[INVENTED modname — naming at build]**, the
campaign's consumer of the universal mod:

- Points Ash'karr's slime patches at `RM_GelatinousSlime` systems (or maps the
  campaign biome def onto the mod's mechanics — build call; the frozen campaign
  sheets stay authoritative for the campaign skin).
- **Murrel** (owner-ruled rename of GR_Chickenrabbit): the campaign instance's
  native demonstrator, living in rolling stage-2 conversion (v1 §5 carried
  verbatim — equilibrium breeder, ban-5's transforming band, the bespoke
  slimified art pass calibrates the overlay). Label rename now; defName migration
  rides `NAMING_SCHEME_EXECUTION_1`.
- Loads the FROZEN SW gene lists (`the_slime_gene_lists.md`, P1–P3 provenance
  intact) as the campaign's archive, replacing the mod's vanilla default list.
- Re-sources the antidote as Rot-derived; wires the mycoid-symbiote resistance
  route; keeps Assailant/Helix/Wildsteam/Throat lore and the Contagion
  distinction as campaign canon.
- Tags the campaign's drying biomes (deserts; **the salt registers if the owner's
  "maybe the salt ocean" firms up** — open, §10).
- Keeps the campaign cast (AA substrate + arrivals + trace-tail) as the instance's
  residents alongside the mod's dynamic visitors.

---

## 10. Open questions — the owner's, not ours

1. **The salt ocean as a drying biome** — his "maybe": does salt water dry the
   film (salt kills it) or is it wet enough to sustain it? One-word ruling tags
   or skips the salt registers.
2. **Machine placement constraint** (§5a): console must sit on/adjacent to slime
   terrain — keep (the machine reads the body) or allow anywhere with slurry
   brought to it? [INVENTED either way]
3. **Default archive size** for the universal list: ~12–20 vanilla/Biotech genes
   under the P-laws proposed [INVENTED] — curate at a sitting or delegate to
   build?
4. **The library flavor hook** (v1): dissolved species named in console flavor
   ("Entry recorded: …") — keep or cut? [INVENTED]
5. **Injection scars** ("read-marks" — small permanent debuff after a stage-3
   antidote): keep or cut? [INVENTED]
6. **Worldgen commonality** of the biome on other players' planets: rare-exotic
   (recommended) or common? [INVENTED]

*(Resolved since v1: colonist full ladder — ruled option 1; manhunter — ruled
never-hostile as law; Chickenrabbit — ruled MURREL; caravan exemption — replaced
by drying biomes.)*

---

## 11. Sources read

- `design/Jawa/worldbuilding/biomes/the_slime.md` (FROZEN — all rulings pulled or
  left per §1), `the_slime_gene_lists.md` (FROZEN/ACCEPTED — P-laws pulled, lists
  left), `edible_genepack_native_mechanism.md` (FROZEN — the IL-verified
  primitive), `the_rot.md` (the two Rot exports), `the_contagion.md` (the
  distinction, left behind as canon; its art law kept)
- `design/Jawa/worldbuilding/review/round2/biome_findings.md` +
  `move_mapping_v2.md` + `biomes/rosters/the_slime.json` (cast provenance)
- `design/NAMING_SCHEME_PLAN.md` (tier test, grammar, engine-vs-content split rule
  — this mod is the "engine takes the highest tier it honestly passes" case)
- v1: `creatures/RUT_slime_transformation_system.md` @ `beaf2687` (absorbed)
- `creatures/RUT_hydrocarbon_ecology_commission.md` (format + spike-sizing
  precedent)
