# Non-canon beast names — Forsaken Crags, Nightside Ice, the Contagion, the Slime

**DRAFT for the owner, 2026-09-24. Nothing applied.** Phase 1 of `NONCANON_BEAST_RENAME_1`
(census + drafted names, by biome). Beasts only — flora renaming is its own track and is
not touched here. Every drafted name below passed
`python3 src/RimMandrake/Utils/check_pseudo_sw_name.py` (shape + no collision with the 137
canon entries), a sweep against every `<label>` in `src/` (5,521 labels), a sweep against
every coined stem already ruled in `rot_flora_fauna_names.md`, `lantern_deeps_flora_names.md`
and batch 2, and a Wookieepedia title search (a coined word that turns out to be a real Star
Wars name was swapped — rule 2). The checker judges shape; the owner judges taste. Strike
what you dislike, say what it should be, or say *"all fine"*.

Format follows the two precedents: current label → **drafted label** (alternate), one-line
rationale, lowercase RimWorld labels, **defNames do not change here** (that is
`DONOR_DEFS_PORT_TO_OURS_1`'s question). Label and description are wired together on
acceptance, never the label alone.

## What is already ruled, so it is not re-drafted

- **Batch 2 (the DesertPort sixteen) is RULED and APPLIED**, not "awaiting the owner's ear"
  as the item file said until today: `32ecbc8cb` (2026-09-20, *"owner ruled batch 2 —
  apply all 22 renames"*) rewrote label + labelPlural + description across 6 SWBestiary
  files. `RSW_Stoneback` reads *bokka*, `RSW_Voltmaw` *vozzik*, `RSW_Ferroclaw` *khorrak*,
  `RSW_Dunestalker` *vosska*, `RSW_Korrum` *korrum*, and so on. The reaction sheet is
  `Transient/drafted_creature_names_2026-09-21.md`.
- **The Rot's six fauna** (rennok, gromma, durrok, mullgoth, vorrugath, chittik) and the two
  keep-renames (skerrith, grellik) are ruled in `rot_flora_fauna_names.md`.
- **The ikee** (`AA_Eyeling`) is the owner's own ruling of 2026-08-15.
- **The dusk rat stays** — `forsaken_crags.md` §4 and §Owed: *"the name stays; owner ruled
  the name IS the joke."* Not drafted.

🔑 **A donor def and its `RSW_` port are one beast and get one name.** Several donor rows in
these four rosters already have a ruled name sitting on their DesertPort port (MEASURED from
the port descriptions, which are the donor's text rewritten): `AA_SandProwler` = `RSW_Dunestalker`
*vosska*; `AA_BoulderMit` = `RSW_Korrum` *korrum*; `AA_TetraSlug` = `RSW_Voltmaw` *vozzik*;
`AA_Terramorph` = `RSW_Ferroclaw` *khorrak*. Those rows are listed as **port-named** below and
draw no second name — when `DONOR_DEFS_PORT_TO_OURS_1` swaps the roster row to the port, the
name comes with it.

## Style rules applied

The Rot/Lantern rules unchanged, plus the item's STANDARD:

1. **Coined, not compounded.** An alien word, never `<English adjective><English noun>`. The
   phonetic target is the 37 coined canon creature names: two syllables (three for a giant),
   4–7 letters, a doubled consonant or a k/q/x/z in most, a vowel or -k/-r/-g ending.
2. **Never a real Star Wars name** on a beast that is not that creature — checked against the
   canon library and Wookieepedia. Three drafts were swapped for this (a hand-bolt, a
   surname, a character).
3. **One stem per species; kinship goes in the description.** The nightling family shares an
   *accent*, not a stem. Nothing here shares a four-letter opening with any name already
   ruled anywhere on the planet.
4. **Variants take the canon variant shape** — plain English modifier on the coined stem
   (*greater krayt dragon, jungle worrt, white loth-cat*): *blistered bulloo*, *greater
   wollub*. A life stage keeps its plain stage word (*fezzira larva*, as *megaspider* does).
5. **Each biome has one accent, so its cast sounds like one place.** Crags: hard voiced
   stops, k/g/r clusters. Nightside: hushed, long vowels, sibilants, almost no plosives.
   Contagion: wet liquids — l, v, zh, gl — and open endings. Slime: soft rounded m/b/l,
   doubled, -o/-um.
6. **A def that lives in several biomes has one name planet-wide**, drafted in the biome that
   gives it its job and cross-referenced in the others (evictions are stopped; multi-homing is
   not resolved here).

---

## Batch 3a — Forsaken Crags (`forsaken_crags.json`, 16 rows)

*Obsidian teeth in a fog light cannot cross.* The donor roster is the population by the
owner's wholesale ruling — a single transplanted nocturnal family. The accent is the crags
themselves: hard, dark, consonant-heavy, said in a gust. 14 drafted; 2 not.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `AA_Nightling` | nightling | sleek quill-throwing nocturnal apex predator (bs 1.0) | **vrakka** | skravva | The quill volley in one word: *vr-* the lunge, *-kk-* the snap of quills leaving the back; open ending like gizka, acklay. The family's root sound — the rest share the accent, not the stem. |
| `AA_NightRam` | nightram | stubborn horned herbivore, the nightling's kin (bs 2.5) | **dhukkor** | dhorrak | Low and blunt, head down: *dh-* a hoof on obsidian, *-kkor* the impact. Kinship to the vrakka is written in the description, not the name. |
| `AA_NightMule` | nightmule | the domestic pack line; quills it cannot throw; stronger than a muffalo (bs 2.8) | **hulggar** | hrukkal | A hauling grunt — heavy *-lgg-* under load, *-ar* trailing off as a beast of burden's name should. The tame one, so the softest consonants in the set. |
| `AA_NightAve` | night ave | large flightless black bird, faster than a horse, ridden into battle (bs 1.1) | **zekkra** | tsavik | Speed: a *z* start, the clipped *-kk-*, a runner's name said quickly; bird-shape ending like nuna. |
| `AA_Murkling` | murkling | small clever pack scavenger; snout-organs hum to the pack; "thief of the night" (bs 0.35) | **kessik** | pizzik | Small and sibilant — the hush of a pack passing, the hiss the snout-organs make; diminutive *-ik* like pikobi. |
| `AA_CrepuscularBeetle` | Crepuscular Beetle | huge Hercules-beetle herbivore, dusk-active beast of burden (bs 3.0) | **brekkug** | kollugg | Armour on armour: *br-* the bulk, *-kk-* carapace plates knocking, *-ug* heavy. "Crepuscular" is a Latin lab word no colonist would say. |
| `AA_ShadowCharger` | shadow charger | long-horned, passive, milk and meat; females lock horns in season (bs 2.5) | **korrag** | valluk | Horns locking: the rolled *rr* is horn grinding on horn; a herd word short enough to shout across a pen. |
| `AA_Thunderox` | thunderox | shaggy, stumpy-horned; brays at the dawn of thunderstorms; milk, wool, regenerates (bs 2.5) | **bhoruk** | hurrogh | Its own call — *bho-* the bray farmers listen for before the gust-storm, *-ruk* the shaggy bulk behind it. |
| `AA_DarkVandal` | dark vandal | pure-muscle boar-thing, digs for truffles, brood-protective rampage (bs 1.2) | **gruzzak** | brokkur | Snout in the ground: *gruzz* is a rooting, grunting sound; *-ak* the sudden charge. |
| `AA_DuskProwler` | dusk prowler | weaponised killing machine; back-protrusions are accelerators and weapons (bs 1.5) | **shekkur** | vrixxa | Something made, not born — a clipped, mechanical *shek-* and a hard stop; nothing soft anywhere in it. |
| `AA_Darkbeast` | darkbeast | mechanoid-infused thunderbeast that wears a trailing halo of Dark (owner ruling §4) (bs 1.5) | **ulkhorr** | vhommag | A hole in the glow: the swallowed *ulkh-* is a word said into darkness, the long *-orr* the halo trailing behind. ⚠️ Also removes a false canon read — "Dark Beast" is a real Wookieepedia entry and this is not it. |
| `AA_Frostling` | frostling | the nightling's polar cousin; spd 6.0 predator of the frozen wastes (bs 1.5) | **thrizzik** | kirrisk | Ice in the mouth: *thr-* a shiver, *-zz-* claws skittering on rime, *-ik* small and quick. |
| `AA_Behemoth` | Behemoth | the Forsaken "dragon": fire breath, regeneration, "the thunder is their voice", 16 squares (bs 8.0) | **ghorrumak** | dhuvrakka | Three syllables for the biggest thing in the crags (canon allows it: varactyl, dianoga): *ghorr-* the thunder-voice, *-umak* the weight coming down. "Behemoth" is an Earth word from a book. |
| `GR_Nighthrumbo` | nighthrumbo | nocturnal thrumbo-line predator with ranged quills (bs 3.0) | **zhurrak** | khurrog | "Thrumbo" is a RimWorld word, not a galaxy word. *zhurr-* the low nocturnal growl, *-ak* the quill strike. |

**Not drafted:** `AA_DuskRat` — KEPT by owner ruling (the name is the joke; art redo owed
separately). `AA_SandProwler` — port-named *vosska* (`RSW_Dunestalker`, ruled 2026-09-20).

Read aloud: vrakka, dhukkor, hulggar, zekkra, kessik, brekkug, korrag, bhoruk, gruzzak,
shekkur, ulkhorr, thrizzik, ghorrumak, zhurrak — fourteen different openings, one accent.

---

## Batch 3b — Nightside Ice (`nightside_ice.json`, 10 rows)

*A chemistry set the size of a hemisphere, switched off, under the aurora.* The sheet's
own admission test bars "anything instantly nameable", which is this item's test stated
harder. Two of these renames were asked for by the owner in the roster itself. The accent
is silence: long vowels, sibilants, no hard stop unless the beast earns one. 4 drafted; 6 not.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `AA_SummitCrab` | summit crab | bs 15 landform giant, spd 1.0 — "a ridge is an organism" (§4) | **ohmurra** | suhllak | Three slow syllables and no stop anywhere — a name you would say about a ridge, not shout at an animal. The *ohm* is a hum in the ice. "Crab" is the Earth animal it must not read as. |
| `AA_Slurrypede` | slurrypede | bio-mechanoid crawler that renders anything into slurry; spd 1.9 (also Miasma, Propane Lakes — one name) | **thollum** | sulmokk | Soft *th-*, swallowed *-oll-*, closed on *-um*: something slow working its way through matter. Named here because the nightside is where its slowness is the whole point. |
| `AA_ShockGoat` | shock goat | static-charged, six-eyed; **owner: refashion for the nightside, pale blue aura, thermal-only sensing, rename** | **zhissa** | tsirrak | The owner asked for this rename in the roster. *zh-* hushed, *-ss-* the crackle of static in cold dry air, an open ending. Nothing of goat left in it. |
| `RSW_CaveLemming` | cave lemming | big solitary herbivore that springs away; **owner: "ice sheet, rename"** | **mahllik** | sohmma | The owner asked for this rename in the roster. A soft *mah-* lump on the ice that becomes a sudden *-llik* spring. "Lemming" is an Earth animal. |

**Not drafted:** `Tauntaun`, `Wampa` — canon visitors, keep. `AA_BoulderMit` — port-named
*korrum* (`RSW_Korrum`, live). `AA_TetraSlug` — port-named *vozzik* (`RSW_Voltmaw`).
`AA_Terramorph` — port-named *khorrak* (`RSW_Ferroclaw`). `AA_RedGoo` — named in the
Contagion batch below (*ghelluva*), where it is the body; here it is a 0.003 trace.

---

## Batch 3c — the Contagion (`the_contagion.json`, 16 rows)

*A red valley under a storm that never stops, where the clear sky is the thing to fear.*
Everything here is wet, warm and unfinished; the sheet's §4 table already gives each beast a
job (the body, the eyes, the sower, the leaker, the drinker, the undertaker, the thieves,
the basker, the pickers). The accent is water — l, v, zh, gl — with open endings; the one
hard name belongs to the one beast that is not carbon. 14 drafted (16 labels, counting the
two aerofleet siblings pulled in from other biomes); 2 not.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `AA_RedGoo` | red goo | **the body** — creeps to the rain line, eats the dead, buds new forms every Bloom (also Nightside Ice at 0.003) | **ghelluva** | ollumaq | The one name in the valley with nothing hard in it: *gh-* a wet exhalation, *-ell-* liquid, *-uva* formless. Three syllables because it is never the same shape twice. |
| `AA_OcularJelly` | ocular jelly | **the eyes** — drifts at canopy height watching the cloud; sinks seconds before a Burn (the player's tell) | **ozhilla** | zhellix | An eye hanging in the rain: round *o-*, *zh* the drift, *-illa* slack and floating. The tell the player learns to read should have a soft name. |
| `AA_InfectedAerofleet` | infected aerofleet | **the sower** — spore-loaded hydrogen float that rides the updraft and pops in sunlight | **blistered bulloo** | red bulloo | The base **aerofleet** (Forge, Grey Sea, Twilight Sea, Slime) becomes **bulloo** — a bounce of a word for a thing that bounces off everything — and the infected variant takes the canon variant shape (*jungle worrt*): plain modifier on the coined stem. Sibling rule: `AA_ColossalAerofleet` → **greater bulloo**. |
| `AA_RedSpore` | red spore | **the leaker** — gallium-based, unstable, walks into the light and cooks; the rare survivor seeds a bloom | **vezzok** | skovva | The pop: *vezz-* a fizz building, *-ok* the burst. Not carbon-based, so it gets the valley's one hard *k* — it does not belong to the wet register and should not. |
| `AA_BloodShrimp` | blood shrimp | **the drinker** — vampiric and fast; why visitors die at the red pools | **zhirrik** | sivvra | Small and fast in the shallows: *zh-* under the water, *-irr-* the dart, *-ik* the bite. "Shrimp" is the Earth animal, "blood" the English kenning. |
| `AA_Helixien` | helixien | **the undertaker** — giant corrosive slug, bs 4 / spd 0.6 (also Slime, Poison Forest, Miasma, Scarlands — one name) | **vulloth** | ghessum | The slowest word in the set: *vull-* the wet bulk, *-oth* the corrosive exhale. Named here because the Contagion is where its job is written. |
| `AA_Drainer` · `AA_DrainerLarva` | drainer · drainer larva | **the thieves** — cat-sized bright electrovore butterfly that taps the ocular trees; short larval stage | **fezzira** · **fezzira larva** | nixxa | A flicker with a static sting: *fezz-* the wingbeat and the crackle, *-ira* bright. The larva keeps the plain stage word (as *megaspider* / *megascarab* do), not a second stem. |
| `AA_RoughPlatedMonitor` | rough-plated monitor | **the basker** — acid-immune, UV-armoured; comes OUT in the Burn; eggs that explode | **brossak** | ghorrix | Plate on plate: *br-* and *-ss-* the scrape of armour, *-ak* the snap. The predator of the window gets the hardest name in the valley after the leaker. |
| `AA_Razorjack` | razorjack | **the pickers** — dual-jawed rodent-canine omnivore; infecting bites (also Pyrelands) | **skezzar** | vrizzo | Two jaws: *sk-* one, *-zz-* the other, *-ar* the tearing. |
| `AA_FungalHusk` | fungal husk | shambling corpse animated by weaponised fungus; virulent, treatable; ruled 2 cells | **ghuvva** | drollum | A wet breath through a dead mouth: *gh-*, *-uvv-*, open *-a*. Nothing in it says fungus or corpse — the description does that. |
| `AA_OcularNightling` | ocular nightling | mutated, eye-studded nightling; sturdier and docile | **gollivra** | ozzavra | Kin to the crags' vrakka — the *-vra* tail echoes it without sharing the stem (Rot rule 3); the *goll-* is the goo it came out of. |
| `AG_OcularSlinger` | ocular slinger | large mutated scorpion, twitching eyes (bs 2.5) | **pellorax** | quizzak | Three syllables ending *-x* like horax and vulptex: *pell-* the many eyes, *-orax* the raised tail. |
| `GR_Fleshling` | fleshling | wretched failing chimera that needs love to live another day (bs 0.2) | **pibbo** | ubbi | The smallest, softest word in the valley — two puffs of breath. The player should feel sorry for it on hearing the name, which "fleshling" prevents. |

**Not drafted:** `AA_Swarmling` — *chittik*, ruled in the Rot pass. `AA_Eyeling` — *ikee*,
owner ruling 2026-08-15 (⚠️ see flag 2 below: its DesertPort port `RSW_Stareling` carries a
second ruled name, *oxxa*).

Read aloud: ghelluva, ozhilla, bulloo, vezzok, zhirrik, vulloth, fezzira, brossak, skezzar,
ghuvva, gollivra, pellorax, pibbo.

---

## Batch 3d — the Slime (`the_slime.json`, 12 rows)

*A body the size of a country, reading everything that touches it.* Soft-bodied
everything; translucent greens and ambers; slow. The accent is round and wet — m, b, l,
doubled, ending -o or -um. The Latin binomials go first: nobody in a cantina says
"acanthamoeba gigantea". 10 drafted (11 labels, counting the Scarlands' small amoeba); 2 not.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `AA_GreenGoo` | green goo | **the substrate** — countless cells of one superorganism, commonality 2.0 | **wummo** | bubbloq | Round and wet: *w-*, *-mm-*, *-o*. A herd of it is "wummo", plural and singular alike, as bantha is. |
| `AA_AcanthamoebaGiganteaLarge` · `…Huge` · `…Small` | acanthamoeba gigantea, large / huge / small | giant spiked amoeba that eats trash and splits when engorged; three size defs (Small lives in the Scarlands) | **wollub** · **greater wollub** · **lesser wollub** | gumbra | *woll-* the lobe, *-ub* the blunt spikes. The three sizes take the canon *greater/lesser* shape rather than three stems, and drop the one Latin binomial a player would never hear said. |
| `AA_Plasmorph` | plasmorph | iron-sulphide-shelled snail that sparks and lobs burning spit; the resistant native (also Poison Forest) | **bezzul** | quobbin | *bezz-* the spark, *-ul* the shell it hides in. |
| `AA_Mime` | mime | human-derived psionic parasite that wears a person's face; trace experiment | **hennul** | sabbek | Deliberately gentle — a name that sounds like a neighbour's. The horror is in the description, where it belongs. "Mime" is an Earth stage word. |
| `AA_DecayDrake` | decay drake | winged flightless lizard whose pheromones ferment plants; four livers; drunk (also Miasma, Poison Forest — one name) | **mubbrak** | zollubb | A sozzled, sagging word: *mubb-* slack, *-rak* the reptile under it. "Drake" is an Earth dragon word. |
| `GR_Chickenrabbit` | chickenrabbit | harmless, hopping, breeds without limit; trace tail | **wuppik** | fippa | Small, quick, silly-soft — the Slime's one joke, and sayable by a child. Both halves of the donor name are Earth animals. |
| `GR_Manbear` | manbear | waist-high teddy-bear humanoid that talks prisoners round; trace tail | **yollum** | bubbal | Round and companionable: *yoll-* the soft bulk, *-um* the murmur it keeps up. |
| `AA_OvergrownColossus` | overgrown colossus | six-legged, six-eyed grove-walker with trees on its back (bs 6.0) | **thummorak** | dhollumar | Three syllables for a bs-6 body, as the Rot's vorrugath (its mycoid sibling) has: *thumm-* the footfall, *-orak* the ridge of trees. Own stem; kinship in the description. |
| `AA_TeratogenicOriginator` | teratogenic originator | translucent stem-cell colony with limbs floating in it; drawSize ruled 3, tinted green | **vubbola** | nulloq | Wobble made into a word: *vubb-* and the trailing *-ola*. The current label reads as a lab report. |

**Not drafted:** `AA_Helixien` — *vulloth*, Contagion batch. `RM_Titanoslime` — the owner's
own creature, named in his ask of 2026-09-20; "titanoslime" is an English compound but it is
his word. If he wants it in register the offer is **mogguloth** (alt *ossumar*); otherwise it
stands. `AA_AcanthamoebaGiganteaSmall` is not in this roster (Scarlands) but takes *lesser
wollub* by the sibling rule.

Read aloud: wummo, wollub, bezzul, hennul, mubbrak, wuppik, yollum, thummorak, vubbola.

---

## Flags for the owner — things a name cannot fix

1. **The item file said batch 2 was unruled; it was ruled and applied four days ago.** The
   stale header in `NONCANON_BEAST_RENAME_1.md` is corrected in the same commit as this doc
   (correctness outranks seat). Nothing else in the item changes.
2. **Three beasts carry TWO ruled names**, one on the donor def and one on its DesertPort
   port — both by the owner's hand, on different days:
   `AA_Wildpod` *mullgoth* (Rot, 2026-09-19) vs `RSW_Sporemass` *grommo* (batch 2, 09-20);
   `AA_Wildpawn` *durrok* (Rot) vs `RSW_Sporepaw` *pukko* (batch 2 — its description is the
   Wildpawn's donor text, "adapted to life outside the swamp"); `AA_Eyeling` *ikee*
   (2026-08-15) vs `RSW_Stareling` *oxxa* (batch 2). The 2026-09-21 sheet flagged the first
   two as UNMEASURED; they are now MEASURED. One of each pair should stand — or the port is
   declared a distinct desert variant and keeps its own. Not decided here.
3. **Six non-canon beasts wear a REAL Wookieepedia title** (rule 2 in reverse, on existing
   labels): `AA_FireWasp` *fire wasp* (a canon creature), `RUT_FireHawk` *fire-hawk*
   (*Firehawk*), `RSW_Screecher` *screecher* (a canon Sith creature), `AA_Darkbeast` *Dark
   Beast* (drafted *ulkhorr* above), `AA_GreatDevourer` *Great Devourer*, `GR_Spidercat`
   *Spidercat*. Each tells the player a canon thing is present when it is not. Two of the Rot's
   own ruled names also land on real titles — *grellik* is a person, *glowbulb* a canon item —
   harmless but worth knowing.
4. **Five roster rows are vanilla/DLC or third-party defs, not ours to relabel casually:**
   `Toxalope` (Biotech), `LavaSnail`, `StoneCrab`, `ColossusToad` (Odyssey), `GiantAnt_Race`
   (They!). A label patch on a vanilla def changes every RimWorld game the mod loads in. Scope
   question, no draft.
5. **No UNCERTAIN rows remain.** `Vapaad` and `TetnissCrab` were listed here as uncertain until
   2026-09-24; batch 5 measured both as canon (Wookieepedia *Vaapad/Legends* is our def's text;
   *Tet'niss* is a named trash crab) — see Appendix B. (`WarWyrm` and `FeralGrazer` were listed
   here the same way until batch 4 measured them canon.)
6. **Sea cast:** the Miasma/Scald/Grey Sea/Twilight Sea rosters carry canon Naboo fish
   (mee, faa, laa, yobshrimp, opee, sando, colo — keep, including the *young* and *elder*
   variants) beside a non-canon sea cast (silt lamprey, rust nipper, pod worm, tumorfish,
   reefback, lanternwhale, starmaw, polluwog, nautilant, atispec, ray-hound). Those want one
   batch with one sea accent, after `TERMINALBIOMES_RM_MOD_BUILD_1` settles which defs exist.

## What remains — biomes not drafted in this pass

Counts are **distinct in-scope defs** (NONCANON + NONCANON\*) per roster from Appendix A,
before subtracting rows already port-named:

| roster | in scope | notes |
|---|---:|---|
| `the_miasma` | 15 | mostly RSW\_ sea juveniles + AA (raptor shrimp, mantrap, lockjaw, thermadon); helixien/decay drake/slurrypede already named above |
| `poison_forest` | 17 | AA/AM dryads, bedbug, silkie, luciferbug, radyak, ripper hound; helixien/decay drake/plasmorph/ocular jelly/infected aerofleet named above |
| `desert` | 15 | most AA rows are port-named by batch 2; left: sand lion, great devourer, groundrunner, mature fleshbeast, jellypot, truffle mole, cephalope, landopus |
| `the_scarlands` | 12 | Insectoids-2 `SW_Electric*` family, rimclaw, acanthamoeba small (→ lesser wollub), RSW\_ foundry beetle / fairy mole / megaphorid / shale gorger |
| `the_rot` | 10 | angel moth, anima colossus, the pustule hornet family (5 defs), smog moth, thrumbungus, yooka (shiro-trap is canon — corrected 2026-09-24) |
| `dune_sea_deep_desert` | 8 | dunealisk, spined gow, sand lion, truffle mole, cephalope; bouldermit/tetra slug/terramorph port-named |
| `wasteland` | 9 | swarmlings ×2, bloodletter petrel, screecher, megatardi, beetlefleet, spidercat, sacapillar; terramorph port-named |
| `the_cracked_lands` | 7 | RSW\_ norphea, sand leaper, mantrap, sandpillar; rock troll; sand squid port-named |
| `the_twilight_sea` | 7 · `the_grey_sea` 5 · `the_scald` 4 | the sea batch (flag 6) |
| `the_propane_lakes` | 6 | frostbound behemoth, frostmite, aurora sylph, sky eel; terramorph port-named, slurrypede named above |
| `arid_shrubland` | 6 | imperial toad, needlepost (port-named *skorra*), cactipine (*chikka*), terrorworm (*vurra*), moss beetle, hydra |
| `the_forge` 5 · `the_pyrelands` 5 · `the_fever_wood` 4 · `the_greentide` 4 · `the_sump` 4 · `the_webwork` 3 · `the_rust_cathedral` 2 · `the_lantern_deeps` 1 · `the_blue_desert` 1 | | |

Total in scope planet-wide: **161** distinct defs (162 until 2026-09-24; shiro-trap is canon); **45** labels drafted here — **42** roster
defs across the four biomes plus the aerofleet / colossal aerofleet / small amoeba siblings
pulled in by rule 4. Two of the 42 are renames the owner asked for in the roster itself
(shock goat, cave lemming); one is a name he ruled to keep and is not drafted (dusk rat).

## On acceptance

- Wire **label + description together** on every accepted row, then re-run the `src/` label
  collision sweep and `check_pseudo_sw_name.py` on the final list.
- Donor defs (`AA_`, `GR_`, `AG_`) take a label/description patch in
  `src/RimUtinni/UtinniPatches/Patches/` on the `Ikee_Rename.xml` /
  `RotSpecies_NamesAndSizes.xml` pattern; `RSW_`/`RUT_` defs are edited in place. When
  `DONOR_DEFS_PORT_TO_OURS_1` ports a donor def, the port is born with the ruled label.
- Record the rulings in this file (strike-throughs and his words), as the two precedents do.

---

## Appendix A — planet-wide census, per biome roster (MEASURED 2026-09-24)

Source: every `fauna[]` row in `design/Jawa/worldbuilding/biomes/rosters/*.json` (29 files, 403 rows, 309 distinct defs), joined to `design/Jawa/worldbuilding/review/creature_register_rows.json` for label/mod/texPath, to `design/RimStarWars/canon_references/` and a Wookieepedia `list=search` sweep (probes: bantha, gizka, worrt hit; nonsense missed) for the canon test, and to `infrastructure/artpipe/_artsrc/` + `done/*.manifest.json` for art. Classes: **CANON** keep · **RULED** already carries an owner-ruled coined name · **KEPT** owner ruled the name stays · **OURS** owner-commissioned def · **NONCANON** in scope · **NONCANON\*** in scope and currently wearing a real Wookieepedia title · **UNCERTAIN** do not draft until checked · **SCOPE?** vanilla/DLC def.

| biome roster | rows | CANON | RULED | KEPT | OURS | NONCANON | NONCANON* | UNCERTAIN | SCOPE? |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `arid_shrubland` | 41 | 34 | 1 |  |  | 6 |  |  |  |
| `desert` | 53 | 37 | 1 |  |  | 14 | 1 |  |  |
| `dune_sea_deep_desert` | 16 | 7 | 1 |  |  | 8 |  |  |  |
| `forsaken_crags` | 16 |  |  | 1 |  | 14 | 1 |  |  |
| `nightside_ice` | 10 | 2 |  |  |  | 8 |  |  |  |
| `poison_forest` | 24 | 6 | 1 |  |  | 16 | 1 |  |  |
| `the_blue_desert` | 2 | 1 |  |  |  | 1 |  |  |  |
| `the_contagion` | 16 |  | 2 |  |  | 14 |  |  |  |
| `the_cracked_lands` | 12 | 5 |  |  |  | 7 |  |  |  |
| `the_fever_wood` | 12 | 7 | 1 |  |  | 4 |  |  |  |
| `the_forge` | 9 | 3 |  |  |  | 5 |  |  | 1 |
| `the_greentide` | 22 | 16 | 1 |  |  | 4 |  |  | 1 |
| `the_grey_sea` | 8 | 3 |  |  |  | 5 |  |  |  |
| `the_lantern_deeps` | 2 |  | 1 |  |  | 1 |  |  |  |
| `the_miasma` | 32 | 17 |  |  |  | 15 |  |  |  |
| `the_propane_lakes` | 6 |  |  |  |  | 6 |  |  |  |
| `the_pyrelands` | 14 | 7 |  |  | 2 | 4 | 1 |  |  |
| `the_rot` | 20 | 2 | 8 |  |  | 10 |  |  |  |
| `the_rust_cathedral` | 3 |  |  |  | 1 | 2 |  |  |  |
| `the_scald` | 8 | 4 |  |  |  | 4 |  |  |  |
| `the_scarlands` | 15 | 1 |  |  | 2 | 12 |  |  |  |
| `the_slime` | 12 |  |  |  | 1 | 11 |  |  |  |
| `the_sump` | 5 | 1 |  |  |  | 4 |  |  |  |
| `the_twilight_sea` | 14 | 6 |  |  |  | 7 |  |  | 1 |
| `the_webwork` | 6 | 3 |  |  |  | 3 |  |  |  |
| `wasteland` | 15 | 1 | 4 |  |  | 7 | 2 |  | 1 |
| `weeping_stones` | 10 | 8 | 1 |  |  |  |  |  | 1 |
| **distinct defs** | **309** | **120** | **16** | **1** | **6** | **156** | **5** | **0** | **5** |

## Appendix B — every beast, one row per def

| defName | current label | biome roster(s) | source mod | class | art | note |
|---|---|---|---|---|---|---|
| `Anooba` | anooba | arid_shrubland, the_miasma, the_pyrelands | Star Wars Animal Collection | CANON | regen:6 done:12 | canon_references/ |
| `Bantha` | bantha | arid_shrubland, desert, weeping_stones | Star Wars Animal Collection | CANON |  done:3 | canon_references/ |
| `Beldon` | beldon | the_forge | Star Wars Animal Collection | CANON |  done:3 | canon_references/ |
| `Blarth` | blarth | the_miasma | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Blarth/Legends, Blarth |
| `Blixus` | blixus | the_grey_sea, the_miasma | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Blixus, Blixus/Legends |
| `Bogwing` | bogwing | the_miasma | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Bogwing, Bogwing/Legends |
| `Bolotaur` | bolotaur | desert | Star Wars Animal Collection | CANON |  done:9 | canon_references/ |
| `Boma` | boma | weeping_stones | Star Wars Animal Collection | CANON | regen:5 done:6 | canon_references/ |
| `Borcatu` | Borcatu | wasteland | Star Wars Animal Collection | CANON | regen:3 done:6 | canon_references/ |
| `CanCell` | can-cell | the_cracked_lands | Star Wars Animal Collection | CANON |  done:3 | canon_references/ |
| `Cannok` | cannok | arid_shrubland | Star Wars Animal Collection | CANON |  done:3 | canon_references/ |
| `Clodhopper` | clodhopper | desert, the_greentide | Star Wars Animal Collection | CANON |  done:3 | canon_references/ |
| `Convor` | convor | arid_shrubland, the_cracked_lands, the_fever_wood, the_greentide | Star Wars Animal Collection | CANON |  done:3 | canon_references/ |
| `Corinathoth` | corinathoth | arid_shrubland | Star Wars Animal Collection | CANON |  done:3 | canon_references/ |
| `Dactillion` | dactillion | weeping_stones | Star Wars Animal Collection | CANON | regen:4 done:3 | canon_references/ |
| `Dalgo` | dalgo | the_pyrelands | Star Wars Animal Collection | CANON |  done:3 | canon_references/ |
| `Dewback` | dewback | weeping_stones | Star Wars Animal Collection | CANON | regen:5 done:7 | canon_references/ |
| `Dragonsnake` | Dragonsnake | the_greentide | Star Wars Animal Collection | CANON | regen:4 done:3 | canon_references/ |
| `Eopie` | eopie | arid_shrubland, desert, the_cracked_lands, weeping_stones | Star Wars Animal Collection | CANON |  done:6 | canon_references/ |
| `Falumpaset` | falumpaset | desert, the_greentide | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Falumpaset, Falumpaset/Legends |
| `Fambaa` | fambaa | the_fever_wood, the_greentide | Star Wars Animal Collection | CANON | regen:3 done:3 | canon_references/ |
| `Fanback` | fanback | weeping_stones | Star Wars Animal Collection | CANON | regen:5 done:6 | canon_references/ |
| `FeralNerf` | feral nerf | arid_shrubland | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Nerf, Nerf/Legends |
| `FrilledGorg` | frilled gorg | arid_shrubland, desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Frilled newt |
| `Gelagrub` | gelagrub | the_fever_wood, the_greentide | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Gelagrub/Legends, Gelagrub |
| `Gizka` | gizka | arid_shrubland, desert, dune_sea_deep_desert, the_greentide, the_pyrelands | Star Wars Animal Collection | CANON |  done:14 | canon_references/ |
| `Gorg` | gorg | arid_shrubland, desert | Star Wars Animal Collection | CANON |  done:9 | Wookieepedia: Gorg, Gorg/Legends |
| `Gornt` | gornt | the_cracked_lands | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Gornt, Gornt/Legends |
| `GraniteSlug` | granite slug | dune_sea_deep_desert, poison_forest | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Granite slug, Granite slug/Legends |
| `Grank` | Grank | arid_shrubland, the_miasma | Star Wars Animal Collection | CANON | regen:3 done:6 | canon_references/ |
| `GreaterKraytDragon` | greater krayt dragon | dune_sea_deep_desert | Star Wars Animal Collection | CANON | regen:3 done:6 | canon_references/ |
| `Gutkurr` | gutkurr | desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Gutkurr, Gutkurr/Legends |
| `Hawkbat` | hawk-bat | the_greentide | Star Wars Animal Collection | CANON | regen:3 done:6 | canon_references/ |
| `Horax` | horax | desert | Star Wars Animal Collection | CANON | regen:3 done:6 | canon_references/ |
| `Hrumph` | hrumph | desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Hrumph, Hrumph/Legends |
| `Hssiss` | hssiss | the_sump | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Hssiss |
| `Igitz` | igitz | arid_shrubland | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Igitz |
| `Iriaz` | iriaz | arid_shrubland, desert, the_pyrelands | Star Wars Animal Collection | CANON |  done:9 | canon_references/ |
| `IridonianReek` | iridonian reek | desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Reek/Legends |
| `Jakobeast` | jakobeast | desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Jakobeast/Legends, Jakobeast |
| `Jamel` | Jamel | desert, weeping_stones | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Jamel |
| `Jimvu` | jimvu | desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Jimvu |
| `Kinrath` | kinrath | the_greentide | Star Wars Animal Collection | CANON | regen:3 done:6 | canon_references/ |
| `Klorslug` | k'lor'slug | the_greentide | Star Wars Animal Collection | CANON | donor art | Wookieepedia: K'lor'slug/Legends, K'lor'slug |
| `KowakianMonkeyLizard` | kowakian monkey-lizard | arid_shrubland | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Kowakian monkey-lizard, Kowakian monkey-lizard/Legends |
| `KraytDragon` | krayt dragon | dune_sea_deep_desert | Star Wars Animal Collection | CANON |  done:9 | Wookieepedia: Krayt dragon, Krayt dragon/Legends |
| `Kreetle` | kreetle | arid_shrubland, desert, dune_sea_deep_desert, the_webwork | Star Wars Animal Collection | CANON | regen:3 done:10 | canon_references/ |
| `Krykna` | krykna | desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Krykna |
| `Kwi` | Kwi | desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Kwi |
| `Kybuck` | kybuck | arid_shrubland | Star Wars Animal Collection | CANON |  done:2 | Wookieepedia: Kybuck, Kybuck/Legends |
| `LavaFlea` | lava flea | the_forge | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Lava flea, Lava flea/Legends |
| `LongtailGorg` | longtail gorg | arid_shrubland, desert, the_fever_wood | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Gorg/Legends |
| `Lothcat` | loth-cat | arid_shrubland | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Loth-cat, Loth-cat/Legends |
| `Lylek` | lylek | poison_forest | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Lylek/Legends, Lylek |
| `MarshHaunt` | marsh haunt | the_miasma | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Marsh haunt |
| `Massiff` | massiff | arid_shrubland | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Massiff, Massiff/Legends |
| `Mott` | mott | the_greentide | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Mott, Mott/Legends |
| `Mudhorn` | mudhorn | arid_shrubland | Star Wars Animal Collection | CANON |  done:3 | canon_references/ |
| `Mynock` | mynock | poison_forest, the_scarlands | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Mynock, Mynock/Legends |
| `Neebray` | neebray | poison_forest | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Neebray, Neebray/Legends |
| `Nerf` | nerf | desert | Star Wars Animal Collection | CANON |  done:6 | Wookieepedia: Nerf, Nerf/Legends |
| `Nuna` | nuna | arid_shrubland, desert, the_fever_wood, the_greentide, the_pyrelands | Star Wars Animal Collection | CANON |  done:9 | canon_references/ |
| `Ollopom` | ollopom | weeping_stones | Star Wars Animal Collection | CANON | regen:3 done:3 | canon_references/ |
| `Orray` | orray | the_pyrelands | Star Wars Animal Collection | CANON | regen:4 done:7 | canon_references/ |
| `PekoPeko` | Peko-peko | the_greentide | Star Wars Animal Collection | CANON | regen:4 done:3 | canon_references/ |
| `Pikobis` | pikobis | arid_shrubland | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Pikobi/Legends, Pikobi |
| `Porg` | porg | arid_shrubland | Star Wars Animal Collection | CANON |  done:3 | canon_references/ |
| `Pufferpig` | Pufferpig | arid_shrubland | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Puffer pig |
| `Qormot` | qormot | arid_shrubland | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Qormot |
| `RSW_AbyssalColo` | abyssal colo | the_twilight_sea | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Naboo Abyss/Legends |
| `RSW_ColoClawFish` | colo claw fish | the_scald | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Colo claw fish, Colo claw fish/Legends |
| `RSW_CrimsonOpee` | crimson opee | the_twilight_sea | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Crimson Dawn |
| `RSW_ElderSando` | elder sando | the_grey_sea | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Star Wars: Episode I The Phantom Menace (junior novelization) |
| `RSW_Faa` | faa scalefish | the_scald | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Faa |
| `RSW_FaaJuv` | young faa scalefish | the_miasma | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Faa |
| `RSW_Laa` | laa scalefish | the_twilight_sea | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Laa |
| `RSW_LaaJuv` | young laa scalefish | the_miasma | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Laa |
| `RSW_Mee` | mee scalefish | the_scald | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Mee |
| `RSW_MeeJuv` | young mee scalefish | the_miasma | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Mee |
| `RSW_OpeeSeaKiller` | opee sea killer | the_twilight_sea | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Opee sea killer/Legends, Opee sea killer |
| `RSW_OpeeSeaKillerJuv` | sub-adult opee sea killer | the_miasma | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Opee sea killer/Legends, Opee sea killer |
| `RSW_SandoAquaMonster` | sando aqua monster | the_miasma | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Sando aqua monster/Legends, Sando aqua monster |
| `RSW_StormSando` | storm sando | the_twilight_sea | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Learning Patience |
| `RSW_ThornbackColo` | thornback colo | the_scald | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia:  |
| `RSW_YobshrimpJuv` | young pale yobshrimp | the_miasma | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Yobshrimp |
| `Ronto` | ronto | arid_shrubland, desert | Star Wars Animal Collection | CANON | regen:3 done:6 | canon_references/ |
| `Runyip` | runyip | desert, the_miasma | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Runyip, Runyip/Legends |
| `Scurrier` | scurrier | arid_shrubland, dune_sea_deep_desert | Star Wars Animal Collection | CANON |  done:2 | Wookieepedia: Scurrier, Scurrier/Legends |
| `Shaak` | shaak | desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Shaak/Legends, Shaak |
| `Shiro` | shiro | the_greentide, the_miasma | Star Wars Animal Collection | CANON | regen:3 done:6 | canon_references/ |
| `Shyrack` | shyrack | desert, the_webwork | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Shyrack/Legends, Shyrack |
| `Silooth` | silooth | poison_forest | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Silooth/Legends, Silooth |
| `Skalder` | skalder | desert, poison_forest | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Skalder/Legends, Skalder |
| `Sketto` | sketto | arid_shrubland, desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Sketto/Legends, Sketto |
| `Snoruuk` | snoruuk | the_rot | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Snoruuk/Legends |
| `Strill` | strill | arid_shrubland | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Strill/Legends, Strill |
| `Tauntaun` | tauntaun | nightside_ice | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Tauntaun, Tauntaun/Legends |
| `TeeMuss` | tee muss | desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Tee-muss, Tee-muss/Legends |
| `Tibidee` | tibidee | the_forge | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Tibidee |
| `Urusai` | urusai | arid_shrubland, the_fever_wood | Star Wars Animal Collection | CANON |  done:2 | Wookieepedia: Urusai, Urusai/Legends |
| `Uvak` | uvak | desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Uvak |
| `Varactyl` | varactyl | desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Varactyl, Varactyl/Legends |
| `Voorpak` | voorpak | arid_shrubland, desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Voorpak, Voorpak/Legends |
| `Vornskyr` | vornskyr | the_miasma | Star Wars Animal Collection | CANON | regen:3 done:6 | canon_references/ |
| `Vulptex` | vulptex | arid_shrubland | Star Wars Animal Collection | CANON |  done:6 | canon_references/ |
| `Wampa` | Wampa | nightside_ice | Star Wars Animal Collection | CANON |  done:3 | canon_references/ |
| `Whisperbird` | whisperbird | arid_shrubland, the_fever_wood, the_greentide, the_miasma | Star Wars Animal Collection | CANON | regen:3 done:9 | canon_references/ |
| `WompRat` | womp rat | desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Womp rat, Womp rat/Legends |
| `Woolamander` | woolamander | the_cracked_lands | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Woolamander/Legends, Woolamander |
| `Worrt` | worrt | arid_shrubland, desert, the_greentide | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Worrt, Worrt/Legends |
| `Wraid` | wraid | desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Wraid |
| `Wyyyschokk` | wyyyschokk | the_webwork | Star Wars Animal Collection | CANON | regen:4 done:4 | canon_references/ |
| `Yobshrimp` | yobshrimp | the_twilight_sea | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Yobshrimp, Yobshrimp/Legends |
| `Zakkeg` | zakkeg | the_miasma | Star Wars Animal Collection | CANON | regen:3 done:6 | canon_references/ |
| `Zeer` | zeer | desert, the_pyrelands | Star Wars Animal Collection | CANON |  done:6 | canon_references/ |
| `AA_Agaripawn` | rennok | the_rot | Alpha Animals | RULED |  done:3 | already carries a ruled coined name |
| `AA_Agaripod` | gromma | the_rot | Alpha Animals | RULED | donor art | already carries a ruled coined name |
| `AA_Eyeling` | ikee | dune_sea_deep_desert, the_contagion, weeping_stones | Alpha Animals | RULED | donor art | port-named: RSW_Stareling oxxa — SECOND ruled name beside ikee (flag 2); already carries a ruled coined name |
| `AA_MycoidColossus` | vorrugath | the_rot | Alpha Animals | RULED |  done:5 | already carries a ruled coined name |
| `AA_Swarmling` | chittik | the_contagion, the_rot | Alpha Animals | RULED |  done:3 | already carries a ruled coined name |
| `AA_Wildpawn` | durrok | the_greentide, the_rot | Alpha Animals | RULED |  done:3 | port-named: RSW_Sporepaw pukko — SECOND ruled name beside durrok (flag 2); already carries a ruled coined name |
| `AA_Wildpod` | mullgoth | arid_shrubland, poison_forest, the_rot | Alpha Animals | RULED |  done:3 | port-named: RSW_Sporemass grommo — SECOND ruled name beside mullgoth (flag 2); already carries a ruled coined name |
| `GR_Molebear` | grutt | wasteland | Vanilla Genetics Expanded | RULED | donor art | already carries a ruled coined name |
| `GR_ParagonRat` | grithe | wasteland | Vanilla Genetics Expanded | RULED | donor art | already carries a ruled coined name |
| `RSW_FacetMothLarvae` | soulchime | the_lantern_deeps | RimMandrake: SW — Bestiary | RULED | donor art | already carries a ruled coined name |
| `RSW_FleeceSpider` | puffmite | wasteland | RimMandrake: SW — Bestiary | RULED | donor art | already carries a ruled coined name |
| `RSW_FungalMantis` | skerrith | the_rot | RimMandrake: SW — Bestiary | RULED | donor art | already carries a ruled coined name |
| `RSW_FungalWeevil` | grellik | the_rot | RimMandrake: SW — Bestiary | RULED |  done:3 | already carries a ruled coined name |
| `RSW_GlowSlug` | glowbulb | the_fever_wood | RimMandrake: SW — Bestiary | RULED | donor art | already carries a ruled coined name |
| `RSW_Maligoat` | kroffa | wasteland | RimMandrake: SW — Bestiary | RULED | donor art | already carries a ruled coined name |
| `RSW_Stoneback` | bokka | desert | RimMandrake: SW — Bestiary | RULED | regen:3 | already carries a ruled coined name |
| `AA_DuskRat` | dusk rat | forsaken_crags | Alpha Animals | KEPT | donor art | KEPT — owner ruled the name IS the joke (forsaken_crags.md §4/§Owed); art redo owed, name stays |
| `RM_Titanoslime` | None | the_slime | ? | OURS | UNMEASURED | owner's own creature, named in his ask 2026-09-20 |
| `RSW_Korrum` | None | the_scarlands | ? | OURS | regen:3 done:3 | our DesertPort def, label 'korrum' |
| `RUT_CathedralRoach` | cathedral roach | the_rust_cathedral | RimMandrake: Utinni — Rust Cathedral Roaches | OURS | donor art | our def (Rust Cathedral) |
| `RUT_FireHawk` | fire-hawk | the_pyrelands | RimUtinni Patches (Jawa campaign) | OURS | regen:19 done:18 | our def (Pyrelands), owner-commissioned |
| `RUT_FurnaceBeast` | furnace-beast | the_pyrelands | RimUtinni Patches (Jawa campaign) | OURS | regen:1 done:3 | our def (Pyrelands), owner-commissioned |
| `RUT_ScarRoach` | scar-roach | the_scarlands | RimMandrake: Utinni — Rust Cathedral Roaches | OURS | donor art | our def (Scarlands) |
| `AA_AcanthamoebaGiganteaHuge` | acanthamoeba gigantea, huge | the_slime | Alpha Animals | NONCANON | donor art | DRAFTED HERE: greater wollub |
| `AA_AcanthamoebaGiganteaLarge` | acanthamoeba gigantea, large | the_slime | Alpha Animals | NONCANON | donor art | DRAFTED HERE: wollub |
| `AA_AcanthamoebaGiganteaSmall` | acanthamoeba gigantea, small | the_scarlands | Alpha Animals | NONCANON | donor art | DRAFTED HERE: lesser wollub |
| `AA_Aerofleet` | aerofleet | the_forge, the_grey_sea, the_twilight_sea | Alpha Animals | NONCANON | donor art | DRAFTED HERE: bulloo |
| `AA_AngelMoth` | angel moth | the_rot | Alpha Animals | NONCANON | donor art |  |
| `AA_AnimaColossus` | anima colossus | the_rot | Alpha Animals | NONCANON | donor art |  |
| `AA_Atispec` | atispec | the_scald | Alpha Animals | NONCANON | donor art |  |
| `AA_AuroraSylph` | Aurora sylph | the_propane_lakes | Alpha Animals | NONCANON | donor art |  |
| `AA_Barbslinger` | barbslinger | the_pyrelands | Alpha Animals | NONCANON | regen:6 done:10 |  |
| `AA_BedBug` | bedbug | poison_forest | Alpha Animals | NONCANON | donor art |  |
| `AA_Behemoth` | Behemoth | forsaken_crags | Alpha Animals | NONCANON | donor art | DRAFTED HERE: ghorrumak |
| `AA_BloodShrimp` | blood shrimp | the_contagion | Alpha Animals | NONCANON | donor art | DRAFTED HERE: zhirrik |
| `AA_BoulderMit` | bouldermit | dune_sea_deep_desert, nightside_ice | Alpha Animals | NONCANON | donor art | port-named: RSW_Korrum korrum |
| `AA_Bumbledrone` | bumbledrone | the_sump | Alpha Animals | NONCANON | donor art |  |
| `AA_BumbledroneHierophant` | bumbledrone hierophant | the_sump | Alpha Animals | NONCANON | donor art |  |
| `AA_BumbledroneQueen` | bumbledrone queen | the_sump | Alpha Animals | NONCANON | donor art |  |
| `AA_Cactipine` | cactipine | arid_shrubland | Alpha Animals | NONCANON | donor art | port-named: RSW_Spinerat chikka |
| `AA_ColossalAerofleet` | colossal aerofleet | the_forge, the_grey_sea, the_twilight_sea | Alpha Animals | NONCANON | donor art | DRAFTED HERE: greater bulloo |
| `AA_CrepuscularBeetle` | Crepuscular Beetle | forsaken_crags | Alpha Animals | NONCANON | donor art | DRAFTED HERE: brekkug |
| `AA_CrescendoAnole` | crescendo anole | the_forge | Alpha Animals | NONCANON | donor art |  |
| `AA_CrystalMit` | crystalmit | poison_forest | Alpha Animals | NONCANON | donor art |  |
| `AA_DarkVandal` | dark vandal | forsaken_crags | Alpha Animals | NONCANON | donor art | DRAFTED HERE: gruzzak |
| `AA_DecayDrake` | decay drake | poison_forest, the_miasma, the_slime | Alpha Animals | NONCANON | donor art | DRAFTED HERE: mubbrak |
| `AA_DesertAve` | desert ave | desert | Alpha Animals | NONCANON | donor art | port-named: RSW_Sandstrider ossik |
| `AA_Drainer` | drainer | the_contagion | Alpha Animals | NONCANON | donor art | DRAFTED HERE: fezzira |
| `AA_DrainerLarva` | drainer larva | the_contagion | Alpha Animals | NONCANON | donor art | DRAFTED HERE: fezzira larva |
| `AA_Dunealisk` | dunealisk | dune_sea_deep_desert | Alpha Animals | NONCANON | donor art |  |
| `AA_DuskProwler` | dusk prowler | forsaken_crags | Alpha Animals | NONCANON | donor art | DRAFTED HERE: shekkur |
| `AA_Feralisk` | feralisk | the_webwork | Alpha Animals | NONCANON | donor art |  |
| `AA_FrostboundBehemoth` | frostbound behemoth | the_propane_lakes | Alpha Animals | NONCANON | donor art |  |
| `AA_Frostling` | frostling | forsaken_crags | Alpha Animals | NONCANON | donor art | DRAFTED HERE: thrizzik |
| `AA_Frostmite` | frostmite | the_propane_lakes | Alpha Animals | NONCANON | regen:3 done:3 |  |
| `AA_FungalHusk` | fungal husk | the_contagion | Alpha Animals | NONCANON | donor art | DRAFTED HERE: ghuvva |
| `AA_GiantCrownedSilkie` | giant crowned silkie | poison_forest | Alpha Animals | NONCANON | donor art |  |
| `AA_Gigantelope` | gigantelope | desert | Alpha Animals | NONCANON | donor art | port-named: RSW_Sandhorn thurra (per the 2026-09-21 sheet) |
| `AA_GreenGoo` | green goo | the_slime | Alpha Animals | NONCANON | donor art | DRAFTED HERE: wummo |
| `AA_Groundrunner` | groundrunner | desert | Alpha Animals | NONCANON | donor art |  |
| `AA_Helixien` | helixien | poison_forest, the_contagion, the_miasma, the_scarlands, the_slime | Alpha Animals | NONCANON | donor art | DRAFTED HERE: vulloth |
| `AA_InfectedAerofleet` | infected aerofleet | poison_forest, the_contagion | Alpha Animals | NONCANON | donor art | DRAFTED HERE: blistered bulloo |
| `AA_LarvalAtispec` | larval atispec | the_scald | Alpha Animals | NONCANON | donor art |  |
| `AA_Lockjaw` | lockjaw | the_miasma | Alpha Animals | NONCANON | regen:21 |  |
| `AA_LuciferBug` | luciferbug | poison_forest | Alpha Animals | NONCANON | donor art |  |
| `AA_MammothWorm` | mammoth worm | desert | Alpha Animals | NONCANON | donor art | port-named: RSW_Tuskcoil ulgga |
| `AA_Mantrap` | mantrap | the_miasma | Alpha Animals | NONCANON | regen:12 |  |
| `AA_MatureFleshbeast` | mature fleshbeast | desert | Alpha Animals | NONCANON | donor art |  |
| `AA_Metallovore` | metallovore | the_forge | Alpha Animals | NONCANON | donor art |  |
| `AA_Mime` | mime | the_slime | Alpha Animals | NONCANON | donor art | DRAFTED HERE: hennul |
| `AA_Murkling` | murkling | forsaken_crags, the_cracked_lands | Alpha Animals | NONCANON | donor art | DRAFTED HERE: kessik |
| `AA_Needlepost` | needlepost | arid_shrubland, the_greentide | Alpha Animals | NONCANON | donor art | port-named: RSW_Barbthorn skorra |
| `AA_Needleroll` | needleroll | desert, dune_sea_deep_desert | Alpha Animals | NONCANON | donor art | port-named: RSW_Spineroller kudda |
| `AA_NightAve` | night ave | forsaken_crags | Alpha Animals | NONCANON | donor art | DRAFTED HERE: zekkra |
| `AA_NightMule` | nightmule | forsaken_crags | Alpha Animals | NONCANON | donor art | DRAFTED HERE: hulggar |
| `AA_NightRam` | nightram | forsaken_crags | Alpha Animals | NONCANON | donor art | DRAFTED HERE: dhukkor |
| `AA_Nightling` | nightling | forsaken_crags | Alpha Animals | NONCANON | donor art | DRAFTED HERE: vrakka |
| `AA_OcularJelly` | ocular jelly | poison_forest, the_contagion | Alpha Animals | NONCANON | donor art | DRAFTED HERE: ozhilla |
| `AA_OcularNightling` | ocular nightling | the_contagion | Alpha Animals | NONCANON | donor art | DRAFTED HERE: gollivra |
| `AA_OvergrownColossus` | overgrown colossus | the_slime | Alpha Animals | NONCANON | donor art | DRAFTED HERE: thummorak |
| `AA_Plasmorph` | plasmorph | poison_forest, the_slime | Alpha Animals | NONCANON | donor art | DRAFTED HERE: bezzul |
| `AA_Radyak` | radyak | poison_forest | Alpha Animals | NONCANON | donor art |  |
| `AA_RaptorShrimp` | raptor shrimp | the_miasma | Alpha Animals | NONCANON | donor art |  |
| `AA_RayHound` | ray-hound | the_scald | Alpha Animals | NONCANON | donor art |  |
| `AA_Razorjack` | razorjack | the_contagion, the_pyrelands | Alpha Animals | NONCANON |  done:3 | DRAFTED HERE: skezzar — ⚠️ CONFLICTS with the owner's own card pick *sytheclaw* (2026-09-14, `RAZORJACK_IDENTITY_RESTYLE_1`), live on the Pyrelands port `RUT_Sytheclaw`; batch 5 flag 1 |
| `AA_RedGoo` | red goo | nightside_ice, the_contagion | Alpha Animals | NONCANON | donor art | DRAFTED HERE: ghelluva |
| `AA_RedSpore` | red spore | the_contagion | Alpha Animals | NONCANON | donor art | DRAFTED HERE: vezzok |
| `AA_RipperHound` | ripper hound | poison_forest | Alpha Animals | NONCANON | donor art |  |
| `AA_RoughPlatedMonitor` | rough-plated monitor | the_contagion | Alpha Animals | NONCANON | donor art | DRAFTED HERE: brossak |
| `AA_SandLion` | sand lion | desert, dune_sea_deep_desert | Alpha Animals | NONCANON | donor art |  |
| `AA_SandProwler` | sand prowler | desert, forsaken_crags | Alpha Animals | NONCANON | donor art | port-named: RSW_Dunestalker vosska |
| `AA_SandSquid` | sand squid | desert, the_cracked_lands | Alpha Animals | NONCANON | donor art | port-named: RSW_Sandmaw ommok |
| `AA_ShadowCharger` | shadow charger | forsaken_crags | Alpha Animals | NONCANON | regen:3 done:3 | DRAFTED HERE: korrag |
| `AA_ShockGoat` | shock goat | nightside_ice | Alpha Animals | NONCANON | donor art | DRAFTED HERE: zhissa |
| `AA_Skyeel` | arcturan sky eel | the_propane_lakes | Alpha Animals | NONCANON | donor art |  |
| `AA_Slurrypede` | slurrypede | nightside_ice, the_miasma, the_propane_lakes | Alpha Animals | NONCANON | donor art | DRAFTED HERE: thollum |
| `AA_SmallButterfly` | small butterflies | the_fever_wood, the_greentide | Alpha Animals | NONCANON | donor art |  |
| `AA_SpinedGow` | spined gow | dune_sea_deep_desert | Alpha Animals | NONCANON | donor art |  |
| `AA_SummitCrab` | summit crab | nightside_ice | Alpha Animals | NONCANON | donor art | DRAFTED HERE: ohmurra |
| `AA_TarGuzzler` | tar guzzler | the_sump | Alpha Animals | NONCANON | donor art |  |
| `AA_TeratogenicOriginator` | teratogenic originator | the_slime | Alpha Animals | NONCANON | donor art | DRAFTED HERE: vubbola |
| `AA_Terramorph` | terramorph | desert, nightside_ice, the_propane_lakes, wasteland | Alpha Animals | NONCANON | regen:5 done:3 | port-named: RSW_Ferroclaw khorrak |
| `AA_TetraSlug` | tetra slug | dune_sea_deep_desert, nightside_ice | Alpha Animals | NONCANON | donor art | port-named: RSW_Voltmaw vozzik |
| `AA_Thermadon` | thermadon | the_miasma | Alpha Animals | NONCANON | donor art |  |
| `AA_Thunderbeast` | thunderbeast | the_blue_desert | Alpha Animals | NONCANON | donor art |  |
| `AA_Thunderox` | thunderox | forsaken_crags | Alpha Animals | NONCANON | regen:3 done:3 | DRAFTED HERE: bhoruk |
| `AG_OcularSlinger` | ocular slinger | the_contagion | Alpha Genes | NONCANON | donor art | DRAFTED HERE: pellorax |
| `AM_Dryad_Corruptor` | corruptor dryad | poison_forest | Alpha Memes | NONCANON | donor art |  |
| `AM_Dryad_Ocular` | ocular dryad | poison_forest | Alpha Memes | NONCANON | donor art |  |
| `AM_Dryad_Tumorous` | tumorous dryad | poison_forest | Alpha Memes | NONCANON | donor art |  |
| `DA_RockTroll` | rock troll | the_cracked_lands | Dark Ages : Beasts and Monsters | NONCANON | donor art |  |
| `GR_Beetlefleet` | beetlefleet | poison_forest, wasteland | Vanilla Genetics Expanded | NONCANON | donor art |  |
| `GR_Boomsnake` | boomsnake | the_pyrelands | Vanilla Genetics Expanded | NONCANON |  done:2 |  |
| `GR_Chickenrabbit` | chickenrabbit | the_slime | Vanilla Genetics Expanded | NONCANON | donor art | DRAFTED HERE: wuppik |
| `GR_Chickenspider` | chickenspider | the_webwork | Vanilla Genetics Expanded | NONCANON | donor art |  |
| `GR_Fleshling` | fleshling | the_contagion | Vanilla Genetics Expanded | NONCANON | donor art | DRAFTED HERE: pibbo |
| `GR_Manbear` | manbear | the_slime | Vanilla Genetics Expanded | NONCANON | donor art | DRAFTED HERE: yollum |
| `GR_Mantistanis` | None | the_pyrelands | ? | NONCANON | regen:1 done:11 |  |
| `GR_Mechachicken` | mecha-chicken | the_rust_cathedral | Vanilla Genetics Expanded | NONCANON | donor art |  |
| `GR_Mecharat` | mecha-rat | the_rust_cathedral | Vanilla Genetics Expanded | NONCANON | donor art |  |
| `GR_Nighthrumbo` | nighthrumbo | forsaken_crags | Vanilla Genetics Expanded | NONCANON | donor art | DRAFTED HERE: zhurrak |
| `JOE_Cephalope` | cephalope | desert, dune_sea_deep_desert | RimUtinni Patches (Jawa campaign) | NONCANON | donor art |  |
| `JOE_Landopus` | landopus | desert | RimUtinni Patches (Jawa campaign) | NONCANON | donor art |  |
| `JOE_Nautilant` | nautilant | the_scald | RimUtinni Patches (Jawa campaign) | NONCANON | donor art |  |
| `JRWBeelzebufo` | None | the_miasma | ? | NONCANON | UNMEASURED |  |
| `RG_Rimclaw` | rimclaw | the_scarlands | ReGrowth 2 | NONCANON | donor art |  |
| `RSW_AaroxisDendoria` | aaroxis dendoria | the_miasma | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_AcidSlug` | acid slug | the_fever_wood | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_BloodletterPetrel` | bloodletter petrel | wasteland | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_CaveLemming` | cave lemming | nightside_ice | RimMandrake: SW — Bestiary | NONCANON | donor art | DRAFTED HERE: mahllik |
| `RSW_ColonyPustuleHornet` | pustule hornet | the_rot | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_ColonyPustuleHornetQueen` | pustule queen | the_rot | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_Creature_Mantrap` | mantrap | the_cracked_lands | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_CrestedDragon` | crested dragon | the_miasma | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_CrystalFairyMole` | crystal fairy mole | the_scarlands | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_Diggerpede` | diggerpede | the_greentide | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_FoundryBeetle` | foundry beetle | the_scarlands | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_Gembug` | gembug | the_lantern_deeps | RimMandrake: SW — Bestiary | NONCANON |  done:3 |  |
| `RSW_ImperialToad` | imperial toad | arid_shrubland | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_Jellypot` | jellypot | desert | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_JewelBeetle` | jewel beetle | the_fever_wood, the_webwork | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_Lanternwhale` | lanternwhale | the_twilight_sea | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_Maguana` | maguana | the_forge | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_MegaphoridLarva` | megaphorid maggot | the_scarlands | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_MossBeetle` | moss beetle | arid_shrubland | RimMandrake: SW — Bestiary | NONCANON |  done:3 |  |
| `RSW_MutagenicNorphea` | mutagenic norphea | the_cracked_lands | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_MutatingTumorfishAdult` | mutating tumorfish | the_twilight_sea | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_MutatingTumorfishFry` | mutating tumorfish fry | the_twilight_sea | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_MutatingTumorfishSpawn` | mutating tumorfish spawn | the_twilight_sea | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_PodWorm` | pod worm | the_miasma | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_Polluwog` | polluwog | the_grey_sea | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_PustuleHornet` | pustule hornet | the_rot | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_PustuleHornetQueen` | pustule queen | the_rot | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_PustuleHornetSpawned` | pustule hornet | the_rot | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_Reefback` | reefback | the_grey_sea | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_RustNipperJuv` | young rust nipper | the_miasma | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_Sacapillar` | sacapillar | wasteland | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_SandLeaper` | sand leaper | the_cracked_lands | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_SandPillar` | sandpillar | the_cracked_lands | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_ShaleGorger` | shale gorger | the_scarlands | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_SiltLamprey` | silt lamprey | the_grey_sea | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_SiltLampreyJuv` | young silt lamprey | the_miasma | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_SmogMoth` | smog moth | the_rot | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_Starmaw` | starmaw | the_twilight_sea | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_Thrumbungus` | thrumbungus | the_rot | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_TruffleMole` | truffle mole | desert, dune_sea_deep_desert | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `RSW_Yooka` | yooka | the_rot | RimMandrake: SW — Bestiary | NONCANON | donor art |  |
| `SW_Electricfish` | Electricfish | the_scarlands | Insectoids 2 - Isopoda geneline | NONCANON | donor art |  |
| `SW_Electricgryllotalpa` | Electricgryllotalpa | the_scarlands | Insectoids 2 - Isopoda geneline | NONCANON | donor art |  |
| `SW_Electrictick` | Electrictick | the_scarlands | Insectoids 2 - Isopoda geneline | NONCANON | donor art |  |
| `SW_Grenadierworm` | Grenadierworm | the_scarlands | Insectoids 2 - Isopoda geneline | NONCANON | donor art |  |
| `SW_Juggernautbeetles` | Juggernautbeetles | the_scarlands | Insectoids 2 - Isopoda geneline | NONCANON | donor art |  |
| `Terrorworm` | terrorworm | arid_shrubland | Horrors | NONCANON | donor art | port-named: RSW_Ashworm vurra |
| `VAEWaste_Hydra` | None | arid_shrubland | ? | NONCANON | UNMEASURED |  |
| `VAEWaste_Megatardi` | megatardi | wasteland | RimUtinni Patches (Jawa campaign) | NONCANON | regen:3 done:3 |  |
| `VFEI2_BlackSwarmling` | black swarmlings | the_miasma, wasteland | Alpha Animals | NONCANON | donor art |  |
| `VFEI2_Megathrips` | megathrips | the_fever_wood | Vanilla Factions Expanded - Insectoids 2 | NONCANON | donor art |  |
| `VFEI2_Swarmling` | swarmlings | the_greentide, the_miasma, wasteland | Vanilla Factions Expanded - Insectoids 2 | NONCANON | donor art |  |
| `Visceral` | visceral | poison_forest | Horrors | NONCANON | donor art |  |
| `AA_Darkbeast` | darkbeast | forsaken_crags | Alpha Animals | NONCANON* | donor art | DRAFTED HERE: ulkhorr; non-canon beast wearing a REAL Wookieepedia title ('Dark Beast') — rename fixes a false canon read |
| `AA_FireWasp` | fire wasp | the_pyrelands | Alpha Animals | NONCANON* | regen:1 done:3 | non-canon beast wearing a REAL Wookieepedia title ('Fire wasp') — rename fixes a false canon read |
| `AA_GreatDevourer` | great devourer | desert | Alpha Animals | NONCANON* | donor art | non-canon beast wearing a REAL Wookieepedia title ('Great Devourer') — rename fixes a false canon read |
| `GR_Spidercat` | spidercat | wasteland | Vanilla Genetics Expanded | NONCANON* | regen:3 done:3 | non-canon beast wearing a REAL Wookieepedia title ('Spidercat') — rename fixes a false canon read |
| `RSW_Screecher` | screecher | poison_forest, wasteland | RimMandrake: SW — Bestiary | NONCANON* | donor art | non-canon beast wearing a REAL Wookieepedia title ('Screecher') — rename fixes a false canon read |
| `RSW_ShiroTrap` | shiro-trap | the_rot | RimMandrake: SW — Bestiary | CANON | donor art | Wookieepedia: Shiro-trap — the Naboo Shiro/Tooke-trap symbiote; our description IS that text (corrected 2026-09-24, batch 4: was wrongly NONCANON*) |
| `FeralGrazer` | feral grazer | desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Grazer (Alderaan) — "related to the Nerf… wild grazers were significantly leaner"; our description is that text (corrected 2026-09-24, batch 4: was UNCERTAIN) |
| `TetnissCrab` | tet'niss crab | the_grey_sea | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Tet'niss — "a gigantic female trash crab on Lanupa" (*Skeleton Crew*, 2024); the species is the canon *trash crab*, the label carries the individual's name (corrected 2026-09-24, batch 5: was UNCERTAIN). Sea batch. |
| `Vapaad` | vapaad | the_blue_desert | Star Wars Animal Collection | CANON | donor art | Wookieepedia: Vaapad/Legends — "brown ball-shaped, multi-tentacled creatures with two yellow eyes… native to Sarapin"; our description is that text, Mlie misspelt the title (corrected 2026-09-24, batch 5: was UNCERTAIN). Keep; *vaapad* spelling is a canon-label question. |
| `WarWyrm` | war wyrm | dune_sea_deep_desert | Star Wars Animal Collection | CANON |  done:3 | Wookieepedia: Sith wyrm — "originally an infant exogorth… Naga Sadow… fourth moon of Yavin"; the def's own text says "sometimes called the 'sith wyrm'" (corrected 2026-09-24, batch 4: was UNCERTAIN) |
| `ColossusToad` | colossus toad | weeping_stones | Odyssey | SCOPE? | donor art | Odyssey — renaming a vanilla/DLC label is a game-wide patch; scope question |
| `GiantAnt_Race` | giant ant | the_greentide | They! (Giant Ants) | SCOPE? | donor art | They! (Giant Ants) — Earth animal, donor mod — renaming a vanilla/DLC label is a game-wide patch; scope question |
| `LavaSnail` | lava snail | the_forge | Odyssey | SCOPE? | donor art | Odyssey — renaming a vanilla/DLC label is a game-wide patch; scope question |
| `StoneCrab` | stone crab | the_twilight_sea | Odyssey | SCOPE? | donor art | Odyssey — renaming a vanilla/DLC label is a game-wide patch; scope question |
| `Toxalope` | toxalope | wasteland | Biotech | SCOPE? | donor art | Biotech — renaming a vanilla/DLC label is a game-wide patch; scope question |

Art column: `regen:N` = N regenerated renders in `infrastructure/artpipe/_artsrc/`; `done:N` = N finished artpipe manifests naming the def; `donor art` = only the donor texPath in the register; `UNMEASURED` = def not in the register (5 defs: `VAEWaste_Hydra`, `JRWBeelzebufo`, `GR_Mantistanis`, `RSW_Korrum`, `RM_Titanoslime`).
