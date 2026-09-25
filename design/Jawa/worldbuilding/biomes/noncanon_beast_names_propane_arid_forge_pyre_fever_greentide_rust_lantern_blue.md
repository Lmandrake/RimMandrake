# Non-canon beast names — Propane Lakes, Arid Shrubland, the Forge, the Pyrelands, Fever Wood, Greentide, Rust Cathedral, Lantern Deeps, Blue Desert

**DRAFT for the owner, 2026-09-24. Nothing applied.** Phase 1, batch 3 — the wrap-up — of
`NONCANON_BEAST_RENAME_1` (census + drafted names, by biome), continuing
`noncanon_beast_names_crags_nightside_contagion_slime.md` (batch 1; its Appendix A/B census is
the source here and is not re-derived) and
`noncanon_beast_names_poison_miasma_desert_scar_rot_dune_waste_cracked.md` (batch 2). Beasts
only; flora is its own track. Every drafted name and alternate below (**44 words**) passed
`python3 src/RimMandrake/Utils/check_pseudo_sw_name.py` (44/44, shape + no collision with the 137
canon entries; two earlier drafts were refused on English stems — *rathai* "rat", *querrock* "rock"
— and replaced), a sweep against every `<label>` in `src/` (5,522 labels, probe `bokka` hit, 0
collisions), a first-four-letter stem sweep against 1,099 coined stems in the prior names docs and
the September roster docs plus all 5,522 labels (probes `vrakka`, `thrizzik`, `gulveth` hit; **13
overlaps found and swapped**, among them *tobbi* → a canon character's given name, *rukhai* → *Rukh*,
a canon character already in our own `CastRoster_BLACKSTAR.xml`, *voorhun* → the canon *voorpak*),
and a Wookieepedia `list=search` sweep (probes `bantha` hit, `zzqxxv` missed; one exact page found
and swapped: *tebbi*). The checker judges shape; the owner judges taste. Strike what you dislike,
say what it should be, or say *"all fine"*.

Format follows the four precedents: current label → **drafted label** (alternate), one-line
rationale, lowercase RimWorld labels, **defNames do not change here** (that is
`DONOR_DEFS_PORT_TO_OURS_1`'s question). Label and description are wired together on acceptance,
never the label alone.

## What is already ruled or settled, so it is not re-drafted

- **Batch 2 (DesertPort) is RULED and APPLIED** (`32ecbc8cb`). **Batches 1 and 2 of this series
  are DRAFTED, not ruled** — their names are cross-referenced here, never re-drafted.
- 🔑 **A sitting's own `RM_` successor IS the name** (the port-named rule, extended): where a
  September roster doc has already replaced a donor row with an invented `RM_` creature carrying a
  coined name, that name is the beast's and no second one is drafted. Four Sump rows go this way
  (batch 5j). The successor is the port; when the sitting lands it, the name comes with it.
- **Two census corrections, MEASURED this pass against Wookieepedia's own text** (corrected in
  batch 1's Appendix A/B and batch 2's flag 5 in the same commit — correctness outranks seat):
  - `Vapaad` *vapaad* is **CANON (Legends)**: *Vaapad/Legends* — "brown ball-shaped, multi-tentacled
    creatures with two yellow eyes… native to the Galactic Republic energy-world of Sarapin". Our
    description is that text; Mlie misspelt the title. **Keep**; whether the label should read
    *vaapad* is a canon-label question, not this item's.
  - `TetnissCrab` *tet'niss crab* is **CANON**: *Tet'niss* is "a gigantic female trash crab on
    Lanupa" (*Skeleton Crew*, 2024) — the species is the canon *trash crab*, the label carries the
    individual's name. **Keep**; sea batch anyway.
  - ⇒ **No UNCERTAIN rows remain anywhere in the census.**
- **The Pyrelands' donor rows are already re-authored as ours** (`PYRELANDS_DONOR_PORT_4`,
  `EMBERSCYTHE_MANTIS_REAUTHOR_1`; mapping in `PYRELANDS_RM_MOD_BUILD_1` §5): `AA_FireWasp` →
  `RUT_FireWasp` *fire wasp*, `AA_Barbslinger` → `RUT_Barbslinger` *barbslinger*, `GR_Boomsnake` →
  `RUT_Flamefang` *flamefang*, `AA_Razorjack` → `RUT_Sytheclaw` *sytheclaw*, `GR_Mantistanis` (a
  dead donor) → `RUT_Emberscythe` *emberscythe mantis*. The roster JSON still records the donor
  names (a record of his rulings). Names here are drafted **for the `RUT_` def**, since that is
  what the player meets. Two of the five carry **owner naming cards** and are not drafted (flags 1
  and 3); three never had one (`PYRELANDS_DONOR_PORT_4` §owed: *"barbslinger and fire wasp are still
  the donor's coined names… they can be called anything"*; *emberscythe* was the re-authoring
  agent's word — rule 9).
- **Dead, cut or discharged rows draw no name:** `AA_Feralisk` (the `-lisk` clade is Cherry-Picker
  cut, `WYYYSCHOKK_FERALISK_MERGE_1`); `GR_Chickenspider` (Webwork sitting §0 ruling 2: *"not a
  second kind"* — an unwired row); `GR_Mechachicken` (owner card 2026-09-10, cathedral mech-vermin
  trim, *"name already failed recognizability"*); `RSW_JewelBeetle` **in the Webwork only** (RULED CUT
  by card 2026-09-24, superseded by `RM_Quarrok` — it lives on in the Fever Wood and is named
  there); `VAEWaste_Hydra` (**absent def** — `NOT_IN_XML_SET` in the 2026-09-11 tolerance census,
  no register row; the Arid Shrubland import row names a def the live mod set does not contain, a
  roster-sitting finding like the dunealisk).
- **Scope rows (batch 1 flag 4) stand as questions, not drafts:** `LavaSnail` (Odyssey, the Forge),
  `GiantAnt_Race` (They!, the Greentide — and the Fever Wood roster rules the ants **off-map
  raiders only**, never a `wildAnimals` row), `ColossusToad` (Odyssey, Weeping Stones).

## Style rules applied

Batch 1's six rules and batch 2's rules 7–9 unchanged (coined not compounded · never a real Star
Wars name · one stem per species, kinship in the description · variants take the canon variant
shape · one accent per biome · one name planet-wide, drafted where the job is written · a biome
with ruled names keeps that accent · a passing donor coinage is offered a rename, not forced one ·
agent-invented art/port names are not rulings), plus:

10. **A biome whose September roster doc has an invented `RM_` register takes THAT register.** The
    Fever Wood and Greentide rosters share one word-shape by ruling (*"one planet, one language"*:
    -eth/-ith/-ock/-el endings, doubled *ll/mm/rr*) — the three Fever Wood and two Greentide drafts
    join it rather than start a new accent, and share no four-letter opening with any of its 29 + 22
    names. The Lantern Deeps draft joins the thrakk / ossk / nurrik / quorr / zivvit / brellik set.
11. **New accents only where nothing is ruled yet**, each distinct from the twelve already used:
    **Propane Lakes** — gas and cold: *h-* and *v-* onsets, long *au/oo/ee*, nasal *-n/-m* codas, no
    stop anywhere. **Arid Shrubland** — the runway nation: bright *p/t*, doubled *pp/tt*, open *-i/-u*.
    **The Forge** — heat: *j-* and *dh-* onsets, back vowels *o/u*, *-ur/-osh/-ox* codas. **The
    Pyrelands** — the *acklay / orray* shape nobody had used: vowel or *r-* onset, doubled consonant,
    *-ai* coda. **Rust Cathedral** — metallic *z/d*, *-in*. **Blue Desert** — one *y-* word.
12. **An owner-named English compound stands.** Where he named the beast himself (*flamefang*,
    *fire-hawk*, *furnace-beast*, *titanoslime*), the name is his and is not drafted over; an
    in-register alternative is **offered** in one table (§ His words) exactly as batch 1 did for the
    titanoslime, and it means nothing unless he takes it.

---

## Batch 5a — the Propane Lakes (`the_propane_lakes.json`, 6 rows; 4 drafted here)

*A chemistry set switched off under the aurora; the Blue Desert's dead arrive here and are eaten.*
Two of these were placed by the owner himself (*"Perfect Propane Lake creature"*, *"Electrostatic
flyer over Propane Lakes"*). The accent is cold gas: no stops, long vowels, a hum at the end.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `AA_FrostboundBehemoth` | frostbound behemoth | bs 3.0 herd giant, spd 2.0; "what the polar solvent builds when it has a medium" (§4); peaceful, gives a blue milk-substitute | **haummon** | hoorvan | Two slow open syllables and a hum: *hau-* the cold breath, *-mmon* the bulk moving off. The biggest thing on the flats gets the roundest word. "Behemoth" is an Earth word from a book (the crags' ghorrumak already retired it once). |
| `AA_Frostmite` | frostmite | bs 0.5, spd 6.0 corpse-sweeper; "the pole's undertaker" (§4/§5); burrows when hungry | **veezim** | heevun | Small, quick, thin: *vee-* the whistle of something fast over ice, *-zim* the bite. "Mite" is the Earth animal. |
| `AA_AuroraSylph` | Aurora sylph | bs 0.5 plasma-based artificial life; floats, immune to temperature, fragile, does not eat; owner: *"Perfect Propane Lake creature"* | **auvenn** | hoaven | Vowel-initial like the aurora it hangs in: *au-* the light, *-venn* thinning to nothing. "Sylph" is Earth folklore and "Aurora" a Latin goddess. ⚠️ It floats — flier law applies when the def is touched (Core `MaxFlightTime`, a stat not a bool). |
| `AA_Skyeel` | arcturan sky eel | bs 0.25 floating space-borne eel; electric defence, regenerates, affectionate pet; owner: *"Electrostatic flyer over Propane Lakes"* | **hoozan** | vaumeen | *hoo-* the drift, *-zan* the static snap. "Arcturan" is a real star and "eel" an Earth fish. ⚠️ Flier law as above. |

**Not drafted:** `AA_Terramorph` — port-named *khorrak* (`RSW_Ferroclaw`). `AA_Slurrypede` —
*thollum*, batch 1 (Nightside).

Read aloud: haummon, veezim, auvenn, hoozan — nothing hard in any of them.

---

## Batch 5b — the Arid Shrubland (`arid_shrubland.json`, 41 rows; 6 in scope, 2 drafted here)

*The runway nation: small fast things under the fuzz, in the first true soil.* Thirty-four of the
forty-one are canon. The accent is small and bright — *p* and *t*, doubled, an open vowel.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `RSW_ImperialToad` | imperial toad | bs 0.3 cave-desert toad, easily preyed on, kept as a pet "due to its regal posture" (small-runway 0.7) | **pattu** | tibbu | A fat little two-beat word for a fat little animal that sits well. ⚠️ The current label is also a **false read in this galaxy** — "imperial" names the Empire, and a player will look for the connection; there is none. |
| `RSW_MossBeetle` | moss beetle | bs 0.45 underbrush grazer, poor meat "when little else is available" (small-runway 0.3; cut by the Lantern Deeps sheet, scoped there — stays admitted here) | **tuppi** | pobbi | *tupp-* the shell, *-i* small. "Moss" and "beetle" are both Earth words. ⚠️ Its description still says "fungal forests" — a description rewrite is owed at acceptance regardless of the name. |

**Not drafted:** `AA_Needlepost` *skorra* (`RSW_Barbthorn`), `AA_Cactipine` *chikka* (`RSW_Spinerat`),
`Terrorworm` *vurra* (`RSW_Ashworm`) — port-named. `VAEWaste_Hydra` — **absent def**, see the settled
list; if the Arid sitting absorbs one (the megatardi precedent), the port is born with a name then.
Canon kept: the 34 SWAC creatures of the roster.

---

## Batch 5c — the Forge (`the_forge.json`, 9 rows; 5 in scope, 3 drafted here)

*Dark towers against the sun, herds grazing the smoke.* The accent is heat: a *j* or a breathed
*dh* at the front, a back vowel, and a coda that closes like a vent.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `AA_CrescendoAnole` | crescendo anole | bs 0.3 harmless clever lizard that, threatened, hulks into "a crocodilian nightmare" for a few hours (owner: *"volcanic biomes"*) | **jibbur** | dhurrox | A small word for the small state — *jibb-* a quick lizard — with a hard *-ur* that hints at what it becomes. "Crescendo" is an Italian music term, "anole" an Earth lizard. |
| `AA_Metallovore` | metallovore | bs 2.0 tentacle-mouthed metal-eater; rusts metal to flakes, digs rock for more; on-theme under the foundry towers | **dhommur** | dhugosh | *dh-* the wet breath of the mouth-tentacles, *-omm-* the grind, *-ur* the swallow. "Metallovore" is a Latin lab compound. |
| `RSW_Maguana` | maguana | bs 2.1, spd 0.6 magma-camouflage lizard, fire-immune; ours, ported from BMT (the donor `BMT_Maguana` is Cherry-Picker cut; our port is live in `RUT_TheForge`) | **jorrosh** | **maguana** (as is) · dhavvur | **Offer, not a forced rename (rule 8):** *maguana* passes the checker — but it is magma + iguana, and "iguana" is the Earth animal the item puts in scope. *jorrosh* is the Forge accent on a slow hot body. If he likes *maguana*, it stands. |

**Not drafted:** `AA_Aerofleet` *bulloo* and `AA_ColossalAerofleet` *greater bulloo* — batch 1,
**see flag 2** (the Forge sheet carries a placeholder "fumerider"). `LavaSnail` — Odyssey, scope.
Canon kept: Beldon, Lava flea, Tibidee.

Read aloud: jibbur, dhommur, jorrosh.

---

## Batch 5d — the Pyrelands (`the_pyrelands.json`, 14 rows; 5 in scope, 3 drafted here, 2 owner-named)

*Four igniters keep the burn alive.* The cast here is already **ours**, re-authored under `RUT_`
names, and two of its names are the owner's own (flamefang by card; sytheclaw by card). The three
that nobody ever named take an accent no biome has used yet — the *acklay / orray* shape, ending
*-ai*.

| defName (roster → live) | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `AA_FireWasp` → `RUT_FireWasp` (+ eggs) | fire wasp | bs 0.79, spd 1.5 drifting fire-scaled insect that swarms over a burn and drops on what the fire killed; its eggs run hot enough to start fires (small-predator 0.4) | **izzai** | ezzai | The whine and the drop: *izz-*, then *-ai* open like a mouth. Removes a false canon read — *Fire wasp* is a real Wookieepedia creature and this is not it (`NONCANON*`). The eggs carry the stem (*izzai egg*). ⚠️ It floats — flier law when touched. |
| `AA_Barbslinger` → `RUT_Barbslinger` | barbslinger | bs 2.5 calf-sized shield-backed scorpion that turns the cooling ash for what cooked; barbed tail volley (ash-grazer 0.15, the owner's routing call) | **ekkrai** | urrukai | Vowel-initial, then the two hard knocks of plate and tail: *ekk-*, *-rai*. "Barb" and "slinger" are two English words glued. |
| `GR_Mantistanis` → `RUT_Emberscythe` | emberscythe mantis | bs ~1.4, spd 7.0 quick-striking ember-dark mantis; self-healing suits repeated burns; "takes it in one cut" (large-predator 0.05) | **rovvai** | arrukai | *rovv-* the run at the flame edge, *-ai* the cut. *Emberscythe* was coined by the re-authoring agent for a dead donor (owner: *"fix the mantis. That's silly"* — he named nothing), so rule 9 applies: an English compound, never ruled. The plain "mantis" tail goes with it. |

**Not drafted:** `GR_Boomsnake` → `RUT_Flamefang` *flamefang* — **owner's word** (2026-09-16,
verbatim *"rename this to Flamefang and make it venomous"*; card, `FlamefangIdentity`), stands —
offer in § His words. `AA_Razorjack` → `RUT_Sytheclaw` *sytheclaw* — **owner's card pick**
(2026-09-14, `RAZORJACK_IDENTITY_RESTYLE_1`), stands — **see flag 1**, because batch 1 drafted a
second name for the same beast in the Contagion. `RUT_FireHawk` *fire-hawk*, `RUT_FurnaceBeast`
*furnace-beast* — ours, owner-named; *fire-hawk* wears a real Wookieepedia title (*Firehawk*,
batch 1 flag 3) — offer in § His words. Canon kept: Anooba, Iriaz, Nuna, Orray, Zeer, Dalgo, Gizka.

Read aloud: izzai, ekkrai, rovvai — and beside them his own flamefang and sytheclaw.

---

## Batch 5e — the Fever Wood (`the_fever_wood.json`, 12 rows; 4 in scope, 3 drafted here)

*Canopy grazers and their small patient predators, in ambivalent harmony.* The September roster
(`fever_wood_fauna_roster_2026-09-23.md`) adds eleven invented `RM_` creatures in a ruled register —
vaulm, ollareth, drommath, brathek, lommerel, silloch, chellow, murrelith, thavrik, skellick — and
these three donor/ported rows join it (rule 10). ⚠️ All three sit in bands that roster fills with
`RM_` rows; their dispositions belong to the Fever Wood sitting, and the names exist so that
whichever survives is not nameless.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `VFEI2_Megathrips` | megathrips | bs 0.35 engineered worker-caste thrips of the VFE Insectoids 2 geneline; mandibles + acid glands; fills the wood-borer band at 0.5 | **narrith** | gemmeth | *narr-* the rasp of mandibles in wood, *-ith* the Fever register. "Thrips" is the Earth insect with "mega" in front. ⚠️ **Scope flag 4** — a framework mod's hive caste, the swarmling question again. |
| `RSW_AcidSlug` | acid slug | bs 4.0, spd 1.5 combat-designed acid predator that melts prey to the bone inside its own flesh; trace, "the ground is for the brave" (0.05) | **quollith** | vrollith | The slowest word in the wood: *quoll-* a wet weight, *-ith*. "Acid" and "slug" are both Earth words; the description carries the acid. |
| `RSW_JewelBeetle` | jewel beetle | bs 2.45, spd 3.1 slow bark-working beetle with a shell "valuable for its looks"; crown-grazer import at 0.2 | **jemmock** | cammock | *jemm-* a bright hard shell, *-ock* the register's beetle ending (brunnock, wollick). ⚠️ RULED CUT in the **Webwork** (→ `RM_Quarrok`, card 2026-09-24) — alive here; a sheet's cut is scoped to its biome. `RM_Lommerel` is proposed in this band; if the sitting supersedes it, the name retires with the row. |

**Not drafted:** `RSW_GlowSlug` *glowbulb* — ruled. `AA_SmallButterfly` — named in the Greentide
below (one name, two homes by the owner's own placement). Canon kept: Convor, Fambaa, Gelagrub,
Longtail gorg, Urusai, Whisperbird, Nuna.

Read aloud with the roster's eleven: narrith, quollith, jemmock.

---

## Batch 5f — the Greentide (`the_greentide.json`, 22 rows; 4 in scope, 2 drafted here)

*The filth-and-sprouts carpet is the strategy working.* Sixteen of twenty-two are canon; the tree
roster's register (brakkel, brunnock, ghemmel, kaddrath, skerrel, tumbel, wollick, zhorrel …) is the
one the two drafts join.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `RSW_Diggerpede` | diggerpede | bs 1.5 subterranean predator that burrows "faster than most can run", live-bearing; floor-predator 0.4 — the no-pursuit ban does not apply here | **thandrel** | wemmock | *thand-* the ground giving way, *-rel* the register's tail (skerrel, mourvel). "Digger" + "-pede" is English glued to Latin. |
| `AA_SmallButterfly` | small butterflies | bs 0.01 "a flutter of small butterflies", vanishes on death; owner: *"move to jungle"* — Greentide and Fever Wood | **nellith** | flenneth | A word that is already plural in the mouth: *nell-* soft, *-ith* many. A swarm def, so the label reads as the swarm, as *swarmlings* does. "Butterfly" is the Earth insect. |

**Not drafted:** `VFEI2_Swarmling` *nunda* — batch 2. `AA_Needlepost` *skorra*, `AA_Wildpawn`
*durrok* — port-named / ruled. `GiantAnt_Race` — They! (scope) **and** off-map raider only
(`FEVERWOOD_ANT_HIVE_DUNGEON_1`): not a resident, so not a resident's name. Canon kept: the 16.

---

## Batch 5g — the Rust Cathedral (`the_rust_cathedral.json`, 3 rows; 2 in scope, 1 drafted here)

*A metal wasteland at the foot of the eternal noon.* One mech-vermin survived the owner's trim.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `GR_Mecharat` | mecha-rat | bs 0.2, spd 12 mass-produced cybernetic "suicide weapon" with a short-range stun gun; owner: *"rust cathedral and mechanoid dungeons"* | **zikkin** | dettin | The sound of it: *zikk-* a servo and a stun discharge, *-in* small. "Mecha" and "rat" are both words the item names in scope. |

**Not drafted:** `GR_Mechachicken` — **CUT** (owner card 2026-09-10). `RUT_CathedralRoach` — ours,
the owner's own cockroach call.

---

## Batch 5h — the Lantern Deeps (`the_lantern_deeps.json`, 2 rows; 1 in scope, 1 drafted here)

*A blue lantern burning under the mountain.* The Deeps' names are the hard-cluster set — thrakk,
ossk, vellok, nurrik, quorr, zivvit, kuvra, brellik, soulchime — and the one draft joins it.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `RSW_Gembug` | gembug | bs 0.335 plated hydrocarbon crawler; facet shell "grown out of the same slow crystallisation that grew the caverns", reads as a chip of the wall until it moves, weeps paraffin (owner import: *"Crystal caverns"*) | **quozzik** | vrekkit | *quo-* a stone syllable, *-zzik* the skitter when the chip moves. Its own rewritten description is already ours; only "gem" + "bug" is left of the donor. |

**Not drafted:** `RSW_FacetMothLarvae` *soulchime* — ruled.

---

## Batch 5i — the Blue Desert (`the_blue_desert.json`, 2 rows; 1 in scope, 1 drafted here)

*Deliberately empty of existing defs.* One donor row survives at trace as an experiment.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `AA_Thunderbeast` | thunderbeast | bs 1.5 swine-like electric mammal, jolts at range, worsens the weather when slaughtered; trace-experiment 0.005 | **yuddra** | ozzund | The one *y-* word on the planet: *yudd-* a dull charge building, *-ra* the release. "Thunder" and "beast" are both English. |

**Not drafted:** `Vapaad` — **canon**, corrected this pass.

---

## Batch 5j — the Sump, the Webwork, Weeping Stones (nothing drafted; every row discharged)

| roster | in-scope def | why no name is drafted |
|---|---|---|
| `the_sump` | `AA_Bumbledrone` · `AA_BumbledroneHierophant` · `AA_BumbledroneQueen` | **successor-named** — `RM_Thrummel` / `RM_ThrummelWarden` / `RM_ThrummelBroodmother`, the 1:1 re-founding of the bumbledrone hive as ours (decision taken by question card, 2026-09-24, `sump_fauna_roster_2026-09-24.md` ruling 7). *thrummel* is the name; the donor rows retire with the sitting. |
| `the_sump` | `AA_TarGuzzler` | **successor-named** — `RM_Gulveth`, the tar's own grazer in the same slot (roster §7, PROPOSED for the Sump sitting). If the donor row outlives the proposal, it reads *gulveth*: one beast, one name. |
| `the_webwork` | `RSW_JewelBeetle` | RULED CUT here (card 2026-09-24 → `RM_Quarrok`); named in the Fever Wood (*jemmock*). |
| `the_webwork` | `AA_Feralisk` | dead def (clade cut); stale row. |
| `the_webwork` | `GR_Chickenspider` | discharged by the sitting (§0 ruling 2); stale unwired row. |
| `weeping_stones` | `ColossusToad` | Odyssey — scope question, no draft. Every other row is canon, ruled, or an invented `RM_` native with its own coined name. |

---

## His words — in-register offers on owner-named English compounds (rule 12)

These names are the owner's and **stand**. Batch 1 made one such offer (titanoslime → *mogguloth*);
this table completes the set so THE STANDARD is at least visible beside each. Taking none is the
default.

| def | his name | when | offer | alternate |
|---|---|---|---|---|
| `RUT_Flamefang` | flamefang | typed, 2026-09-16 (*"rename this to Flamefang and make it venomous"*) | **uddai** | arrukai |
| `RUT_FireHawk` | fire-hawk | sheet §4, *"the fire-hawks (ruled: absolutely)"* — ⚠️ a real Wookieepedia title (*Firehawk*) | **okkai** | — |
| `RUT_FurnaceBeast` | furnace-beast | sheet §4, *"the furnace-beasts (owner)"* | **ubbrai** | — |
| `RM_Titanoslime` | titanoslime | his ask, 2026-09-20 | *mogguloth* (batch 1) | ossumar |

`RUT_Sytheclaw` *sytheclaw* is his card pick and is **not** offered against — see flag 1 instead.

---

## Flags for the owner — things a name cannot fix

1. **The razorjack has two names, and one of them is yours.** You picked **sytheclaw** from a card on
   2026-09-14 (`RAZORJACK_IDENTITY_RESTYLE_1`); it ships today on the Pyrelands port `RUT_Sytheclaw`
   with your approved description. Batch 1 (2026-09-24) drafted **skezzar** for the same beast's
   donor def `AA_Razorjack` in the **Contagion**, not knowing. A card pick outranks a draft:
   **skezzar should be withdrawn** and the Contagion row should read *sytheclaw* (or point at the
   `RUT_` port) — unless you read the Contagion's as a different animal. ⚠️ Note that the port
   retired the identity patch, so the donor `AA_Razorjack` where it still spawns has fallen back to
   *razorjack*: the same creature reads two ways on the planet today, and that is a wiring defect
   independent of this item.
2. **The aerofleet carries a sheet placeholder against a draft.** `the_forge.md` §4 (ratified
   2026-09-07) records *"Fumeriders (the Alpha Animals Aerofleet, renamed — recorded for the
   roster)"*; the roster JSON says of it *"flagged for owner review… rename rides the naming pass"*,
   the verdict sitting listed it among the 54 contested rows, and no patch applies it. So
   *fumerider* was never ruled as a name, and it is an English compound. Batch 1 drafted **bulloo**
   (*greater bulloo*, *blistered bulloo*). Nothing to do unless *fumerider* was your word — say so
   and bulloo goes.
3. **Two Pyrelands beasts wear your English names beside a batch of coined ones** — *flamefang*
   (typed) and *sytheclaw* (card). They stand; the offers table exists only so you can see the
   alternative. The three you never named — *fire wasp*, *barbslinger*, *emberscythe mantis* — are
   drafted above; *fire wasp* is additionally a false canon read (`NONCANON*`).
4. **Scope question, drafted anyway so the word exists:** `VFEI2_Megathrips` is a caste of a framework
   mod's insectoid line (batch 2 flag 3's swarmling question).
5. **Four stale roster rows found this pass** (roster-sitting findings, not this item's): `AA_Feralisk`
   in the Webwork (a Cherry-Picker-cut def), `GR_Chickenspider` in the Webwork (discharged by
   ruling), `VAEWaste_Hydra` in the Arid Shrubland (a def absent from the live mod set),
   `GR_Mechachicken` in the Rust Cathedral (cut by your card). Batch 2 found two more (`AA_Dunealisk`,
   `RSW_ShaleGorger`). Six rows in total name something the planet does not have.
6. **Two census rows were UNCERTAIN and are now canon** (`Vapaad`, `TetnissCrab`) — corrected in
   batch 1's Appendix A/B and batch 2's flag 5 in this commit. The census now has **zero**
   UNCERTAIN rows.
7. **The Fever Wood's three drafts may be short-lived.** All three sit in bands the September roster
   fills with `RM_` creatures (wood-borer → brathek, crown-grazer → lommerel, ground-slow → nothing yet);
   if the Fever Wood sitting supersedes a donor row, its name retires with it. Drafting them costs a
   line each; leaving them nameless would have left the census open.

## What remains — Phase 1 status

After this pass **every non-canon beast in the 29 rosters has a drafted name or a documented reason
it draws none.** Appendix C below is the MEASURED roll-up of all 168 in-scope rows (156 NONCANON +
5 NONCANON\* + 2 formerly-UNCERTAIN + 5 SCOPE?), one line each, zero UNRESOLVED:

| status | rows | what it means |
|---|---:|---|
| drafted, batch 1 | 45 | crags / nightside / contagion / slime — awaiting his ear |
| drafted, batch 2 | 59 | poison / miasma / desert / scarlands / rot / dune sea / wasteland / cracked lands — awaiting his ear |
| drafted, batch 3 (this doc) | 20 | propane / arid / forge / pyrelands / fever wood / greentide / rust cathedral / lantern deeps / blue desert |
| port-named | 12 | ruled on the DesertPort port (`32ecbc8cb`); the donor row takes it when swapped |
| excluded, with reason | 11 | owner-named (2), successor-named (4), dead/cut/discharged/absent (5) |
| canon, corrected | 2 | Vapaad, Tet'niss crab |
| SCOPE? | 5 | vanilla/DLC/third-party defs — batch 1 flag 4's question, no draft |
| **sea batch** | **14** | blocked on `TERMINALBIOMES_RM_MOD_BUILD_1` settling which defs exist — **the only Phase 1 work left** |

So Phase 1 is **complete for every land biome**. What is left is the sea batch (14 rows +
`RSW_ShaleGorger` + the two Miasma nursery juveniles counted in the Miasma's 15): one accent, one
pass, after the terminal-biome mod build says which defs survive. Phase 2 — his reaction to
124 drafted rows across three docs — is the sitting this item's `needs: owner` would open.

## On acceptance

- Wire **label + description together** on every accepted row; rename every sibling that carries
  the stem (fire-wasp eggs, and the plain "mantis" tail on the emberscythe); then re-run the `src/`
  label collision sweep and `check_pseudo_sw_name.py` on the final list.
- Donor defs (`AA_`, `GR_`, `VFEI2_`) take a label/description patch in
  `src/RimUtinni/UtinniPatches/Patches/` on the `Ikee_Rename.xml` / `RotSpecies_NamesAndSizes.xml`
  pattern; `RSW_`/`RUT_` defs under `src/` are edited in place (`RUT_PyrelandsPortedFauna.xml`,
  `RUT_Emberscythe.xml`, `RSW_BiomesTeamPort_Races.xml`, `RSW_Maguana.xml`). When
  `DONOR_DEFS_PORT_TO_OURS_1` ports a donor def, the port is born with the ruled label.
- Two floaters touched here (`AA_AuroraSylph`, `AA_Skyeel`) and the fire wasp fall under the flier
  law the moment their defs are opened — `MaxFlightTime`/`FlightCooldown`, a stat not a bool.
- Record the rulings in this file (strike-throughs and his words), as the precedents do.

---

## Appendix C — Phase 1 closing census, every in-scope def (MEASURED 2026-09-24)

Derived from batch 1's Appendix B (309 rows, joined here to the three batches' draft tables and the
exclusions above by script; 168 rows in scope, 0 UNRESOLVED). Class as in Appendix B.

| defName | current label | biome roster(s) | class | Phase 1 status |
|---|---|---|---|---|
| `AA_AcanthamoebaGiganteaHuge` | acanthamoeba gigantea, huge | the_slime | NONCANON | batch 1 · greater wollub |
| `AA_AcanthamoebaGiganteaLarge` | acanthamoeba gigantea, large | the_slime | NONCANON | batch 1 · wollub |
| `AA_AcanthamoebaGiganteaSmall` | acanthamoeba gigantea, small | the_scarlands | NONCANON | batch 1 · lesser wollub |
| `AA_Aerofleet` | aerofleet | the_forge, the_grey_sea, the_twilight_sea | NONCANON | batch 1 · bulloo — Forge sheet placeholder "fumerider" never ruled; flag 2 |
| `AA_AngelMoth` | angel moth | the_rot | NONCANON | batch 2 · mollith |
| `AA_AnimaColossus` | anima colossus | the_rot | NONCANON | batch 2 · kerrugoth |
| `AA_Atispec` | atispec | the_scald | NONCANON | SEA BATCH — blocked on TERMINALBIOMES_RM_MOD_BUILD_1 |
| `AA_AuroraSylph` | Aurora sylph | the_propane_lakes | NONCANON | batch 3 · auvenn |
| `AA_Barbslinger` | barbslinger | the_pyrelands | NONCANON | batch 3 · ekkrai (as RUT_Barbslinger) |
| `AA_BedBug` | bedbug | poison_forest | NONCANON | batch 2 · tsikka |
| `AA_Behemoth` | Behemoth | forsaken_crags | NONCANON | batch 1 · ghorrumak |
| `AA_BloodShrimp` | blood shrimp | the_contagion | NONCANON | batch 1 · zhirrik |
| `AA_BoulderMit` | bouldermit | dune_sea_deep_desert, nightside_ice | NONCANON | port-named · RSW_Korrum korrum |
| `AA_Bumbledrone` | bumbledrone | the_sump | NONCANON | SUCCESSOR RM_Thrummel (Sump card ruling 7, 2026-09-24) |
| `AA_BumbledroneHierophant` | bumbledrone hierophant | the_sump | NONCANON | SUCCESSOR RM_ThrummelWarden (Sump card ruling 7) |
| `AA_BumbledroneQueen` | bumbledrone queen | the_sump | NONCANON | SUCCESSOR RM_ThrummelBroodmother (Sump card ruling 7) |
| `AA_Cactipine` | cactipine | arid_shrubland | NONCANON | port-named · RSW_Spinerat chikka |
| `AA_ColossalAerofleet` | colossal aerofleet | the_forge, the_grey_sea, the_twilight_sea | NONCANON | batch 1 · greater bulloo — same flag 2 |
| `AA_CrepuscularBeetle` | Crepuscular Beetle | forsaken_crags | NONCANON | batch 1 · brekkug |
| `AA_CrescendoAnole` | crescendo anole | the_forge | NONCANON | batch 3 · jibbur |
| `AA_CrystalMit` | crystalmit | poison_forest | NONCANON | batch 2 · skixxet |
| `AA_DarkVandal` | dark vandal | forsaken_crags | NONCANON | batch 1 · gruzzak |
| `AA_DecayDrake` | decay drake | poison_forest, the_miasma, the_slime | NONCANON | batch 1 · mubbrak |
| `AA_DesertAve` | desert ave | desert | NONCANON | port-named · RSW_Sandstrider ossik |
| `AA_Drainer` | drainer | the_contagion | NONCANON | batch 1 · fezzira |
| `AA_DrainerLarva` | drainer larva | the_contagion | NONCANON | batch 1 · fezzira larva |
| `AA_Dunealisk` | dunealisk | dune_sea_deep_desert | NONCANON | DEAD — -lisk clade cut (7bad94185); stale roster row (batch 2) |
| `AA_DuskProwler` | dusk prowler | forsaken_crags | NONCANON | batch 1 · shekkur |
| `AA_Feralisk` | feralisk | the_webwork | NONCANON | DEAD — -lisk clade cut (WYYYSCHOKK_FERALISK_MERGE_1); stale roster row |
| `AA_FrostboundBehemoth` | frostbound behemoth | the_propane_lakes | NONCANON | batch 3 · haummon |
| `AA_Frostling` | frostling | forsaken_crags | NONCANON | batch 1 · thrizzik |
| `AA_Frostmite` | frostmite | the_propane_lakes | NONCANON | batch 3 · veezim |
| `AA_FungalHusk` | fungal husk | the_contagion | NONCANON | batch 1 · ghuvva |
| `AA_GiantCrownedSilkie` | giant crowned silkie | poison_forest | NONCANON | batch 2 · ithessa |
| `AA_Gigantelope` | gigantelope | desert | NONCANON | port-named · RSW_Sandhorn thurra (per the 2026-09-21 sheet) |
| `AA_GreenGoo` | green goo | the_slime | NONCANON | batch 1 · wummo |
| `AA_Groundrunner` | groundrunner | desert | NONCANON | batch 2 · dobbak (as RSW_Groundrunner) |
| `AA_Helixien` | helixien | poison_forest, the_contagion, the_miasma, the_scarlands, the_slime | NONCANON | batch 1 · vulloth |
| `AA_InfectedAerofleet` | infected aerofleet | poison_forest, the_contagion | NONCANON | batch 1 · blistered bulloo |
| `AA_LarvalAtispec` | larval atispec | the_scald | NONCANON | SEA BATCH — blocked on TERMINALBIOMES_RM_MOD_BUILD_1 |
| `AA_Lockjaw` | lockjaw | the_miasma | NONCANON | batch 2 · enduk |
| `AA_LuciferBug` | luciferbug | poison_forest | NONCANON | batch 2 · zithix |
| `AA_MammothWorm` | mammoth worm | desert | NONCANON | port-named · RSW_Tuskcoil ulgga |
| `AA_Mantrap` | mantrap | the_miasma | NONCANON | batch 2 · undakka |
| `AA_MatureFleshbeast` | mature fleshbeast | desert | NONCANON | batch 2 · vukkoroth (as RSW_MatureFleshbeast) |
| `AA_Metallovore` | metallovore | the_forge | NONCANON | batch 3 · dhommur |
| `AA_Mime` | mime | the_slime | NONCANON | batch 1 · hennul |
| `AA_Murkling` | murkling | forsaken_crags, the_cracked_lands | NONCANON | batch 1 · kessik |
| `AA_Needlepost` | needlepost | arid_shrubland, the_greentide | NONCANON | port-named · RSW_Barbthorn skorra |
| `AA_Needleroll` | needleroll | desert, dune_sea_deep_desert | NONCANON | port-named · RSW_Spineroller kudda |
| `AA_NightAve` | night ave | forsaken_crags | NONCANON | batch 1 · zekkra |
| `AA_NightMule` | nightmule | forsaken_crags | NONCANON | batch 1 · hulggar |
| `AA_NightRam` | nightram | forsaken_crags | NONCANON | batch 1 · dhukkor |
| `AA_Nightling` | nightling | forsaken_crags | NONCANON | batch 1 · vrakka |
| `AA_OcularJelly` | ocular jelly | poison_forest, the_contagion | NONCANON | batch 1 · ozhilla |
| `AA_OcularNightling` | ocular nightling | the_contagion | NONCANON | batch 1 · gollivra |
| `AA_OvergrownColossus` | overgrown colossus | the_slime | NONCANON | batch 1 · thummorak |
| `AA_Plasmorph` | plasmorph | poison_forest, the_slime | NONCANON | batch 1 · bezzul |
| `AA_Radyak` | radyak | poison_forest | NONCANON | batch 2 · urrixa |
| `AA_RaptorShrimp` | raptor shrimp | the_miasma | NONCANON | batch 2 · drangok |
| `AA_RayHound` | ray-hound | the_scald | NONCANON | SEA BATCH — blocked on TERMINALBIOMES_RM_MOD_BUILD_1 |
| `AA_Razorjack` | razorjack | the_contagion, the_pyrelands | NONCANON | OWNER CARD sytheclaw (RUT_Sytheclaw, 2026-09-14) — batch-1 *skezzar* CONFLICTS; flag 1 |
| `AA_RedGoo` | red goo | nightside_ice, the_contagion | NONCANON | batch 1 · ghelluva |
| `AA_RedSpore` | red spore | the_contagion | NONCANON | batch 1 · vezzok |
| `AA_RipperHound` | ripper hound | poison_forest | NONCANON | batch 2 · tharrix |
| `AA_RoughPlatedMonitor` | rough-plated monitor | the_contagion | NONCANON | batch 1 · brossak |
| `AA_SandLion` | sand lion | desert, dune_sea_deep_desert | NONCANON | batch 2 · shakkir (as RSW_SandLion; vekka flag) |
| `AA_SandProwler` | sand prowler | desert, forsaken_crags | NONCANON | port-named · RSW_Dunestalker vosska |
| `AA_SandSquid` | sand squid | desert, the_cracked_lands | NONCANON | port-named · RSW_Sandmaw ommok |
| `AA_ShadowCharger` | shadow charger | forsaken_crags | NONCANON | batch 1 · korrag |
| `AA_ShockGoat` | shock goat | nightside_ice | NONCANON | batch 1 · zhissa |
| `AA_Skyeel` | arcturan sky eel | the_propane_lakes | NONCANON | batch 3 · hoozan |
| `AA_Slurrypede` | slurrypede | nightside_ice, the_miasma, the_propane_lakes | NONCANON | batch 1 · thollum |
| `AA_SmallButterfly` | small butterflies | the_fever_wood, the_greentide | NONCANON | batch 3 · nellith |
| `AA_SpinedGow` | spined gow | dune_sea_deep_desert | NONCANON | batch 2 · aurrok |
| `AA_SummitCrab` | summit crab | nightside_ice | NONCANON | batch 1 · ohmurra |
| `AA_TarGuzzler` | tar guzzler | the_sump | NONCANON | SUCCESSOR RM_Gulveth (Sump roster §7, PROPOSED) |
| `AA_TeratogenicOriginator` | teratogenic originator | the_slime | NONCANON | batch 1 · vubbola |
| `AA_Terramorph` | terramorph | desert, nightside_ice, the_propane_lakes, wasteland | NONCANON | port-named · RSW_Ferroclaw khorrak |
| `AA_TetraSlug` | tetra slug | dune_sea_deep_desert, nightside_ice | NONCANON | port-named · RSW_Voltmaw vozzik |
| `AA_Thermadon` | thermadon | the_miasma | NONCANON | batch 2 · skondu |
| `AA_Thunderbeast` | thunderbeast | the_blue_desert | NONCANON | batch 3 · yuddra |
| `AA_Thunderox` | thunderox | forsaken_crags | NONCANON | batch 1 · bhoruk |
| `AG_OcularSlinger` | ocular slinger | the_contagion | NONCANON | batch 1 · pellorax |
| `AM_Dryad_Corruptor` | corruptor dryad | poison_forest | NONCANON | batch 2 · tessik |
| `AM_Dryad_Ocular` | ocular dryad | poison_forest | NONCANON | batch 2 · eyed tessik |
| `AM_Dryad_Tumorous` | tumorous dryad | poison_forest | NONCANON | batch 2 · tumorous tessik |
| `DA_RockTroll` | rock troll | the_cracked_lands | NONCANON | batch 2 · uttaqar |
| `GR_Beetlefleet` | beetlefleet | poison_forest, wasteland | NONCANON | batch 2 · skibbex |
| `GR_Boomsnake` | boomsnake | the_pyrelands | NONCANON | OWNER-NAMED flamefang (RUT_Flamefang) — his word stands; in-register offer only |
| `GR_Chickenrabbit` | chickenrabbit | the_slime | NONCANON | batch 1 · wuppik |
| `GR_Chickenspider` | chickenspider | the_webwork | NONCANON | DISCHARGED — Webwork sitting §0 ruling 2 ("not a second kind"); stale unwired row |
| `GR_Fleshling` | fleshling | the_contagion | NONCANON | batch 1 · pibbo |
| `GR_Manbear` | manbear | the_slime | NONCANON | batch 1 · yollum |
| `GR_Mantistanis` | None | the_pyrelands | NONCANON | batch 3 · rovvai (as RUT_Emberscythe) |
| `GR_Mechachicken` | mecha-chicken | the_rust_cathedral | NONCANON | CUT — owner card 2026-09-10 (cathedral mech-vermin trim) |
| `GR_Mecharat` | mecha-rat | the_rust_cathedral | NONCANON | batch 3 · zikkin |
| `GR_Nighthrumbo` | nighthrumbo | forsaken_crags | NONCANON | batch 1 · zhurrak |
| `JOE_Cephalope` | cephalope | desert, dune_sea_deep_desert | NONCANON | batch 2 · qorrax |
| `JOE_Landopus` | landopus | desert | NONCANON | batch 2 · ippok |
| `JOE_Nautilant` | nautilant | the_scald | NONCANON | SEA BATCH — blocked on TERMINALBIOMES_RM_MOD_BUILD_1 |
| `JRWBeelzebufo` | None | the_miasma | NONCANON | batch 2 · onggada |
| `RG_Rimclaw` | rimclaw | the_scarlands | NONCANON | batch 2 · kettix |
| `RSW_AaroxisDendoria` | aaroxis dendoria | the_miasma | NONCANON | batch 2 · ombuna |
| `RSW_AcidSlug` | acid slug | the_fever_wood | NONCANON | batch 3 · quollith |
| `RSW_BloodletterPetrel` | bloodletter petrel | wasteland | NONCANON | batch 2 · fithrak |
| `RSW_CaveLemming` | cave lemming | nightside_ice | NONCANON | batch 1 · mahllik |
| `RSW_ColonyPustuleHornet` | pustule hornet | the_rot | NONCANON | ruled 2026-09-24 · thozzik |
| `RSW_ColonyPustuleHornetQueen` | pustule queen | the_rot | NONCANON | ruled 2026-09-24 · thozzik queen |
| `RSW_Creature_Mantrap` | mantrap | the_cracked_lands | NONCANON | batch 2 · saqqat |
| `RSW_CrestedDragon` | crested dragon | the_miasma | NONCANON | batch 2 · dunkara |
| `RSW_CrystalFairyMole` | crystal fairy mole | the_scarlands | NONCANON | batch 2 · pittok |
| `RSW_Diggerpede` | diggerpede | the_greentide | NONCANON | batch 3 · thandrel |
| `RSW_FoundryBeetle` | foundry beetle | the_scarlands | NONCANON | batch 2 · takkret |
| `RSW_Gembug` | gembug | the_lantern_deeps | NONCANON | batch 3 · quozzik |
| `RSW_ImperialToad` | imperial toad | arid_shrubland | NONCANON | batch 3 · pattu |
| `RSW_Jellypot` | jellypot | desert | NONCANON | batch 2 · pommik |
| `RSW_JewelBeetle` | jewel beetle | the_fever_wood, the_webwork | NONCANON | batch 3 · jemmock |
| `RSW_Lanternwhale` | lanternwhale | the_twilight_sea | NONCANON | SEA BATCH — blocked on TERMINALBIOMES_RM_MOD_BUILD_1 |
| `RSW_Maguana` | maguana | the_forge | NONCANON | batch 3 · jorrosh (offer; maguana alt) |
| `RSW_MegaphoridLarva` | megaphorid maggot | the_scarlands | NONCANON | batch 2 · tsutta maggot |
| `RSW_MossBeetle` | moss beetle | arid_shrubland | NONCANON | batch 3 · tuppi |
| `RSW_MutagenicNorphea` | mutagenic norphea | the_cracked_lands | NONCANON | batch 2 · qattora (offer; bare norphea alt) |
| `RSW_MutatingTumorfishAdult` | mutating tumorfish | the_twilight_sea | NONCANON | SEA BATCH — blocked on TERMINALBIOMES_RM_MOD_BUILD_1 |
| `RSW_MutatingTumorfishFry` | mutating tumorfish fry | the_twilight_sea | NONCANON | SEA BATCH — blocked on TERMINALBIOMES_RM_MOD_BUILD_1 |
| `RSW_MutatingTumorfishSpawn` | mutating tumorfish spawn | the_twilight_sea | NONCANON | SEA BATCH — blocked on TERMINALBIOMES_RM_MOD_BUILD_1 |
| `RSW_PodWorm` | pod worm | the_miasma | NONCANON | batch 2 · lundoba |
| `RSW_Polluwog` | polluwog | the_grey_sea | NONCANON | SEA BATCH — blocked on TERMINALBIOMES_RM_MOD_BUILD_1 |
| `RSW_PustuleHornet` | pustule hornet | the_rot | NONCANON | ruled 2026-09-24 · thozzik |
| `RSW_PustuleHornetQueen` | pustule queen | the_rot | NONCANON | ruled 2026-09-24 · thozzik queen |
| `RSW_PustuleHornetSpawned` | pustule hornet | the_rot | NONCANON | ruled 2026-09-24 · thozzik |
| `RSW_Reefback` | reefback | the_grey_sea | NONCANON | SEA BATCH — blocked on TERMINALBIOMES_RM_MOD_BUILD_1 |
| `RSW_RustNipperJuv` | young rust nipper | the_miasma | NONCANON | SEA BATCH — blocked on TERMINALBIOMES_RM_MOD_BUILD_1 |
| `RSW_Sacapillar` | sacapillar | wasteland | NONCANON | batch 2 · thoffra |
| `RSW_SandLeaper` | sand leaper | the_cracked_lands | NONCANON | batch 2 · qetta |
| `RSW_SandPillar` | sandpillar | the_cracked_lands | NONCANON | batch 2 · luttaq |
| `RSW_ShaleGorger` | shale gorger | the_scarlands | NONCANON | SEA BATCH — opee benthic morph misfiled on land (batch 2) |
| `RSW_SiltLamprey` | silt lamprey | the_grey_sea | NONCANON | SEA BATCH — blocked on TERMINALBIOMES_RM_MOD_BUILD_1 |
| `RSW_SiltLampreyJuv` | young silt lamprey | the_miasma | NONCANON | SEA BATCH — blocked on TERMINALBIOMES_RM_MOD_BUILD_1 |
| `RSW_SmogMoth` | smog moth | the_rot | NONCANON | batch 2 · illoth |
| `RSW_Starmaw` | starmaw | the_twilight_sea | NONCANON | SEA BATCH — blocked on TERMINALBIOMES_RM_MOD_BUILD_1 |
| `RSW_Thrumbungus` | thrumbungus | the_rot | NONCANON | batch 2 · brullith |
| `RSW_TruffleMole` | truffle mole | desert, dune_sea_deep_desert | NONCANON | batch 2 · pikkut |
| `RSW_Yooka` | yooka | the_rot | NONCANON | ruled 2026-09-24 · brogg |
| `SW_Electricfish` | Electricfish | the_scarlands | NONCANON | batch 2 · chekkit |
| `SW_Electricgryllotalpa` | Electricgryllotalpa | the_scarlands | NONCANON | batch 2 · katchit |
| `SW_Electrictick` | Electrictick | the_scarlands | NONCANON | batch 2 · tzikket |
| `SW_Grenadierworm` | Grenadierworm | the_scarlands | NONCANON | batch 2 · xattuk |
| `SW_Juggernautbeetles` | Juggernautbeetles | the_scarlands | NONCANON | batch 2 · kroxxat |
| `Terrorworm` | terrorworm | arid_shrubland | NONCANON | port-named · RSW_Ashworm vurra |
| `VAEWaste_Hydra` | None | arid_shrubland | NONCANON | ABSENT DEF — NOT_IN_XML_SET (census 2026-09-11), not in the register; stale roster row |
| `VAEWaste_Megatardi` | megatardi | wasteland | NONCANON | batch 2 · thuffor |
| `VFEI2_BlackSwarmling` | black swarmlings | the_miasma, wasteland | NONCANON | batch 2 · black nunda |
| `VFEI2_Megathrips` | megathrips | the_fever_wood | NONCANON | batch 3 · narrith |
| `VFEI2_Swarmling` | swarmlings | the_greentide, the_miasma, wasteland | NONCANON | batch 2 · nunda |
| `Visceral` | visceral | poison_forest | NONCANON | batch 2 · krexxa |
| `AA_Darkbeast` | darkbeast | forsaken_crags | NONCANON* | batch 1 · ulkhorr |
| `AA_FireWasp` | fire wasp | the_pyrelands | NONCANON* | batch 3 · izzai (as RUT_FireWasp) |
| `AA_GreatDevourer` | great devourer | desert | NONCANON* | batch 2 · hakkro (as RSW_GreatDevourer) |
| `GR_Spidercat` | spidercat | wasteland | NONCANON* | batch 2 · khiffet |
| `RSW_Screecher` | screecher | poison_forest, wasteland | NONCANON* | batch 2 · isskra |
| `TetnissCrab` | tet'niss crab | the_grey_sea | UNCERTAIN | CANON — corrected this pass (see settled list) |
| `Vapaad` | vapaad | the_blue_desert | UNCERTAIN | CANON — corrected this pass (see settled list) |
| `ColossusToad` | colossus toad | weeping_stones | SCOPE? | SCOPE? — vanilla/DLC/third-party def (batch-1 flag 4) |
| `GiantAnt_Race` | giant ant | the_greentide | SCOPE? | SCOPE? — vanilla/DLC/third-party def (batch-1 flag 4) |
| `LavaSnail` | lava snail | the_forge | SCOPE? | SCOPE? — vanilla/DLC/third-party def (batch-1 flag 4) |
| `StoneCrab` | stone crab | the_twilight_sea | SCOPE? | SCOPE? — vanilla/DLC/third-party def (batch-1 flag 4) |
| `Toxalope` | toxalope | wasteland | SCOPE? | SCOPE? — vanilla/DLC/third-party def (batch-1 flag 4) |
