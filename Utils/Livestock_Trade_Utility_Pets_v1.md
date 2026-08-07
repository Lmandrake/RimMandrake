# The Livestock Trade — Utility, Pet & Companion Creatures

_Companion to `Alien_Bestiary.md` (the VGE + creature-mod SW naming layer). Scanned across RimWorld 1.6 + Odyssey, Alpha Animals, Alpha Biomes, Alpha Memes, Vanilla Genetics Expanded, **Star Wars Animal Collection (Continued), Megafauna, Jurassic Rimworld – Dinosaurs Only, Biomes! family (Core/Caverns/Polluted Lands), and Cephaloids** — the full adopted creature stack per `required_mods.md`. Created August 2026; expanded 2026-08-07 (rest-of-menagerie pass + critique)._

---

## 0-bis. Critique & corrections (2026-08-07 pass — read before building)

The v1 draft is strong: the "who would keep this, and what does it say about them?" lens is the right organizing question, and §6 (the black-market tier) and the d20 stall are genuinely usable. Three issues need fixing before any of it goes to a `Patches/` file, and one whole class of animal was missing a guardrail.

1. **⛔ NAMING COLLISION — `mynock` and `dianoga` are already taken.** *Established from `required_mods.md` §389 (Star Wars Animal Collection roster, source-verified):* **Mynock and Dianoga are real, separate ThingDefs that ship in Star Wars Animal Collection.** The v1 draft reuses both names for *different* Alpha Animals creatures — Metallovore→**"mynock"** and Slurrypede→**"slurrik, *juvenile dianoga*."** If built as written, the spawn log would show two unrelated animals both called mynock and two associated with dianoga — the exact "stray bearchicken" failure the bestiary's naming rules exist to prevent. **Fix (applied below):** Metallovore keeps the *concept* but takes a new name (**`korrik`** — hull-eater); Slurrypede's dianoga tie is demoted to a *nickname only* (people say it looks like a baby dianoga; it is not one), keeping `slurrik`. Cross-check every future rename against the SW Animal Collection roster in §1-bis before coining it.
2. **⚠️ The resource-excreting animals carry an anti-exponential guardrail — now DOWNGRADED to "the ship enforces it."** `urrak`/radyak (excretes refinable uranium), `vokka`/tetraslug (recharges batteries), `hessa`/aerofleet (→ blue gel → power reactor), `hellik`/helixien (gas) are, mechanically, **passive resource generators that eat and breed** — the same *class* as the *rejected* BioRanch. In a fixed base a breeding herd of any of them is a printer. **But on the Kolyska it isn't**, because you can't take anything that won't fit on the ship, and the loop keeps sending you to tiles where a herd can't graze or can't survive the heat — so the hold-cap and the itinerary cull production herds *automatically*. The guardrail box under §1 now states this in full: keep and fly a working few, let the loop cap them; the only permanent ban is a **sessile printer building** (which bypasses ship-cap and grazing), and the old sterilize/don't-breed discipline only re-arms during a long dig-in on one hospitable tile. Still a *pillar* item — just one the core loop mostly self-solves, which is a strength of the nomadic premise, not a hole in it.
3. **Stale companion filename.** v1's header pointed at `Alien_Bestiary_SW_Naming_v1.md`; the file on disk is `Alien_Bestiary.md`. Fixed in the header above. (Low stakes, but the two docs share a generator script and a naming system, so the pointer needs to resolve.)

Everything below §1 is the v1 content (lightly corrected for #1 and #3) followed by the **rest-of-menagerie expansion (§10–§14)** the campaign actually needs — because v1 by design only covered creatures *worth renaming*, and most of the adopted roster (Bantha, Dewback, Rancor, the dinosaurs, the Megafauna heavies) already has canonical SW names and needs *placement/trade framing*, not a new label.

---

## 0. What this document is for

The previous bestiary covered **fauna** — things that live on the world and are encountered. This one covers **commerce**: creatures a settlement keeps on purpose, and creatures a trader will sell you out of a cage.

That distinction matters more in Star Wars than in almost any other setting, because the franchise's most memorable worldbuilding is transactional. A rancor under a trapdoor. A dewback tied outside a cantina. A creature stall in Mos Eisley with something wrong in it. Jabba's court is defined less by its architecture than by the fact that somebody there decided a Kowakian monkey-lizard was worth feeding.

So the organizing question for every entry below is not "does this make ecological sense" but **"who would keep this, and what does keeping it say about them?"**

Nine categories, roughly ordered from "profitable" to "you should not have bought that."

**Verification note:** mechanics below come from the Alpha Animals bestiary wiki, the RimWorld wiki, and mod changelogs. Entries marked ⚠ are ones where I'm working from a name or a partial description and you should confirm in-game before building lore on them.

---

## 1. Living machinery — creatures kept instead of infrastructure

The single most Star Wars category in the game. In a setting where the player faction strips machines for parts, the trader who sells you *a machine that eats and breeds* is offering something meaningfully different.

| Creature | Mod | What it actually does | SW name | Why it's shocking |
|---|---|---|---|---|
| **Slurrypede** | Alpha Animals | Mechanoid-built prisoner-feeding unit. Devours almost anything and processes it into homogeneous organic slurry — barely edible. Harvests 10 Disgusting Nutrient Paste Meals every 1.5 days. Docile, near-never hostile, and uniquely tameable *despite being a mechanoid*. | **slurrik** — nickname *"looks like a baby dianoga"* (⚠ it is NOT one; the real Dianoga is a separate SW-Collection creature — nickname only) | It was built to feed prisoners. Anyone keeping one is either feeding prisoners or has decided not to think about where the design came from. Jawa clans keep them because they eat garbage and produce food, which is the entire Jawa economic philosophy in one animal. |
| **Tetraslug** | Alpha Animals | A massive slug used across Glitterworld territory as a glorified power plant, and deployed as mobile power for research expeditions. Recharges batteries directly. Rarely spawns wild — usually bought from farming merchants. | **vokka** | A settlement whose lights are on because of a slug. The Directorate finds this offensive on principle; the Free Droid Enclaves find it fascinating. |
| **Aerofleet** | Alpha Animals | Small floating gelatinous creature propelled by hydrogen collected from water and plant matter, bouncing aimlessly off obstacles. Genderless, reproduces by strobilation (asexual fission). Explodes on death. Tamed ones produce **Blue Gel** → refined to **hexagel** → a hexagel core reactor consuming uranium and gel for large power. Trainables: *Cycle Severance* (stop fission) and *Controlled detonation* (kill itself on command). | **hessa** | A herd of drifting bombs that powers your base and can be ordered to explode. "Controlled detonation" as a *training option* is the darkest line item in any RimWorld animal tab. |
| **Radyak** | Alpha Animals | Produces unrefined uranium crystals at 1 per 10 days; each refines into 15 uranium. | **urrak** | A domestic animal that excretes fissile material. Every faction wants one and none of them want to explain why. |
| **Shock Goat** | Alpha Animals | Domesticated cattle that store static electricity in bony structures and discharge it defensively. | **zharn** | Livestock that shocks you. Comedy until a herd is between you and the door. |
| **Drainer** | Alpha Animals | Mostly harmless cat-sized lepidopteran, originally blue morpho butterflies mutated by heavy radiation exposure. Feeds on batteries and capacitors. | **sikka** | A beautiful butterfly that drains your power storage. Sold as an ornamental. It is not an ornamental. |
| **Helixien** ⚠ | Alpha Animals | Gas-producing creature; wildness lowered to 40% specifically to make training maintainable. Confirm the exact output. | **hellik** | Ties directly to your tibanna framing — a herd animal that fills tanks. |
| **Chemfuel Myrmidon** ⚠ | Alpha Biomes (Tar Pits) | Chemfuel-associated insectoid of the tar pits. Confirm production mechanics. | **tibbik** | Cousin to your `tibbak`. The Cartel's tar-margin herd. |

**Narrative frame:** these are the animals that make the Hutt Cartel's livestock trade *strategic* rather than culinary. A Cartel boss who controls the region's radyak breeding stock controls its uranium. Give this to Section 4 of your faction roster and the Cartel gains a reason to exist beyond vice.

> **⚠️ ANTI-EXPONENTIAL GUARDRAIL — the living-machinery category, restated & DOWNGRADED (2026-08-07, upgraded same day).** Every animal in §1 is, mechanically, a *passive resource generator that eats and breeds* — `urrak` excretes refinable uranium, `vokka` recharges batteries, `hessa` produces power-gel, `hellik` fills gas tanks, `zharn`/`sikka` touch the power economy. In a *sessile* colony this is the banned BioRanch pattern: a tamed breeding herd becomes a per-tick resource printer. **But this campaign is not a sessile colony, and that changes the ruling from a rule-you-must-obey to a tripwire the core loop already trips for you.**
>
> **Why the gravship self-limits production herds (user insight, 2026-08-07):** *you cannot take with you anything that will not fit on the ship.* Three structural brakes fall out of that, and they are load-bearing enough that this whole category is **less of an exponential threat than a static "it breeds → it prints" analysis suggests:**
> 1. **Berth/cargo cap.** The Kolyska has a finite hold (interior PASS 1: cargo is *the* constrained resource — see `ship15_interior.md`). Every animal you keep displaces cargo and costs a berth. A radyak *barn* can't board; at most a *few* head fly with you. The ship is the herd-cap, enforced automatically at every jump.
> 2. **Forage-hostile destinations.** The loop deliberately sends you to tiles where a grazer *cannot eat* — salt flats, deep desert, ash, polluted rock with no edible flora. A meat/wool/resource herd that can't graze on arrival either starves or forces you to haul feed (more cargo cost). The tiles cull the herd for you.
> 3. **Heat-intolerant destinations.** Same logic on temperature: many target tiles are lethally hot (or, for the cold-clade mounts, lethally cold). An animal that can't stand the destination climate doesn't survive the campaign's itinerary. The route is the predator.
>
> **So the practical ruling relaxes:** you do NOT need to police these animals with an iron rule, because *the ship and the itinerary already do it.* Keep them, buy them, fly a working few — the loop will not let a tamed breeding herd quietly out-scale you the way it would in a fixed base. **The one hard line that remains is the sessile printer BUILDING** — BioRanch, insect-vats, anything that generates resources *without* needing to board, graze, or survive the next tile. Those bypass all three brakes and stay **banned** (BioRanch already rejected in `required_mods.md`). And if you ever *do* dig in on one hospitable, well-watered tile for many seasons (the §13 oasis is exactly such a place), the old discipline snaps back on: at that point a radyak pair *can* print, so sterilize/don't-breed (the Cherry-Pick reproduction lever) until you lift again. The Hutt Cartel — sessile, planet-bound, unconstrained by a hold — is *allowed* to run the real herds off-screen; that asymmetry is precisely **why you trade with them instead of becoming them.**

---

## 2. Waste, decay and disposal — the unglamorous trade

Every settlement has a problem it doesn't discuss. On a desert world with a water economy, disposal is not a minor issue.

| Creature | Mod | What it does | SW name | The shock |
|---|---|---|---|---|
| **Angel Moth** | Alpha Animals | Beautiful metamorphosing lepidopteran — explicitly described as an abandoned genetically engineered waste-disposal project whose subjects got loose. Eats apparel (including modded apparel). | **nimm** | It is genuinely lovely and it will eat your clothes. Kept in cathedral-like halls by people who find this poetic. |
| **Metallovore** | Alpha Biomes | Repulsive creature engineered to eat metals; writhing mouth-tentacles secrete a substance that rapidly rusts and dissolves most common metals. | **korrik** — nickname *"hull-rot"* (⚠ NOT "mynock" — Mynock is a separate real SW-Collection creature; see §0-bis #1) | Jawas keeping a thing that eats hulls is a joke that tells itself. Zone them or they will eat the wrong pile. The nickname does the canon work without stealing the real mynock's name. |
| **Decay Drake** | Alpha Animals | Large winged flightless carnivorous lizards that release a nauseating enzyme cocktail greatly accelerating rot. Will also drink your liquor. | **korrash** | An animal you keep specifically to rot things faster. Corpse disposal without questions. Also an alcoholic. |
| **Murkling** | Alpha Animals | Weak pack scavengers, above-average intellect, snout tendrils producing vibrational sequences for discreet pack communication; nicknamed *thief of the night* for stealing supplies across the rim. Bite inflicts bubonic plague. Tendrils dissolve non-mechanoid corpses within 3 tiles into carrion — even asleep, even through walls under 3 cells thick, even frozen ones. Trainable: *controlled corpse decay*. | **skreev** | The most Jawa animal in the game — small, hooded, clicks, steals — and it will rot your entire freezer through the wall while it naps. |
| **Crystalmit / Bouldermit / Pebblemit** ⚠ | Alpha Animals | Mite-family creatures that consume materials; zoning matters. Confirm exact diets. | **mitt** family | Small things that eat your stockpile. Sold as pest control by people who know better. |

---

## 3. Weaponized companions — the bodyguard trade

The Bounty Hunters' Compact and the Directorate both buy here.

| Creature | Mod | What it does | SW name | The shock |
|---|---|---|---|---|
| **Ray-Hound** | Alpha Animals | Tentacle attacks that deal *extra EMP damage specifically to mechanoids* (mechanoids can adapt to it over time). | **thrass** | **The droid-killer.** For a Jawa clan whose wealth is droids, and an Imperial garrison whose ordnance is droid-adjacent, an animal bred to fry machines is a political object. Whoever sells thrass pups to the Enclaves has picked a side. |
| **Ripper Hound** | Alpha Animals | Purely biological anti-insectoid weapon — engineered canines with two viciously sharp claws designed for killing insects. | **grissk** | Bred as a weapon against a specific enemy. The Foundry Hive considers ownership of one an act of war, which makes it exactly the pet a Compact hunter walks into a Foundry meet with. |
| **Hive Queen** | Odyssey | Tameable with enormous difficulty (Animals 14 + inspiration, or a sentience catalyst, and a tank to absorb hits that tear off limbs). Trainable *Egg Spew* on command — launches acidic sludge and births offensive larvae. Tamed queens spawn *tamed* larvae. Eggs give 50% illumination in a radius and never deteriorate; a fully trained queen spews one per hour, making a free light source. | **karramat** | Someone in your settlement owns the mother of an insect hive and has trained her to lay on command. The Foundry Hive's reaction to a human keeping a queen as *property* should be the single most hostile diplomatic event in your campaign. |
| **Megalouse** | Alpha Animals | Armored engineered pill-bug, 30% sharp/blunt armor, lays eggs, hauls 38. 90% wildness, min handling 9, 20% manhunter on taming and 100% when attacked. Formerly frontline anti-mechanoid skirmishers of an insect hive. | **karrik** | Not a starter pet — an earned one. A veteran's animal. |
| **Feralisk** | Alpha Animals | Supersized silk-production spiders whose homeworld got sterilized by atomic fire. Attacks by throwing stunning webs. | *keep "feralisk"* | Your Feralisk Jungle tile is named for them; leave the name and let the terrain carry the story. |
| **Skiphound** ⚠ | Alpha Animals | Teleporting canine (name and mod context; confirm mechanics). | **skipp** | A dog that arrives inside your walls. Sold by nobody honest. |

---

## 4. Grotesque status pets — the Hutt court tier

Creatures with no utility whatsoever, kept because keeping them is a statement. This is the Salacious Crumb category and your setting badly needs it.

| Creature | Mod | What it is | SW name | Who keeps it |
|---|---|---|---|---|
| **Eyeling** | Alpha Memes | A grotesquely enlarged eye crawling on a few fleshy tentacles, created by infusing an animal with energies from an extradimensional corruption. Explicitly *"not very useful at all."* Doesn't spawn wild — comes from the Ocular Warping Ritual, but colonies without Ideology can buy one from caravan and settlement traders. | **vissa** | Cartel bosses. The purchase route *is* the story: a crate arrives, and inside is an eye. |
| **Unblinking Eye** | Alpha Memes | A floating chitinous creature covered in spikes and unblinking eyes, made by infusing a very large animal with extradimensional corruption. Same ritual/trader availability. | **vissarath** | The elder form of the vissa, per your naming rule. One exists in the region. Its owner is a named NPC by definition. |
| **Engorged Tentacular Aberration** | Alpha Memes | A grotesque mass of writhing tentacles, mouths and eyes, quivering in violent spasms as it strives to breathe; knows only pain and will gladly inflict it. | **the wailing thing** | Nobody keeps this on purpose. It is what you find when you open a container in a Consortium ruin. Pair it with your `shudderflesh`. |
| **Ocular Jelly** | Alpha Animals | Converts nearby trees into instantly-grown alien trees; carries a −100% beauty aura. | **ojja** | An animal that makes your settlement *actively ugly* while making it rich in red wood. The trade-off is the character. |
| **Fission Mouse** | Alpha Animals | Kangaroo-rat-like jumping rodent, another example of human genetic engineering gone wrong. | **rikk** | A pocket pet with a name that should worry you. Sold to children. |
| **Bed Bug** | Alpha Animals | Oversized pest insects considered a nuisance on every world they infest; bite carries a powerful paralyzing toxin. Lays eggs. | **kribb** | Kept in a crate under a bunk. Traded between Jawas as currency-adjacent novelties. |
| **Crescendo Anole** ⚠ | Alpha Animals | Sound-based lizard that applies a hediff (it was buggy enough that the author had to stop it affecting non-targets — confirm current behavior). | **shrikka** | The closest thing available to a Kowakian monkey-lizard: a small creature whose entire function is *noise*. |

---

## 5. The medical and comfort trade

| Creature | Mod | What it does | SW name | Note |
|---|---|---|---|---|
| **Cactipine** | Alpha Animals | Desert-colonization engineered creature. Quills are coated in a powerful anesthetic and serve as an alternative to herbal medicine — weaker than industrial, but useful in emergencies. | **hubbak** | Your deep-desert medical supply. A settlement with a hubbak pen doesn't need to buy glitterworld medicine, which changes its relationship with every trader who arrives. Genuinely strategic. |
| **Vanilla comfort pets** (cat, lapdog, panda) | Core / Odyssey | Nuzzle for mood. Odyssey added therapy-trained pandas and cats that comfort colonists. | reflavor per faction | Worth naming, because "the Jawa clan keeps a nuzzling animal" is a humanizing detail the setting otherwise lacks. |
| **Sentience catalyst** *(item, not creature)* | Odyssey | Mechanite drug that permanently improves an animal's consciousness and trainability. One per animal, effects permanent, not inherited by offspring. Lowers wildness 25%, cutting minimum handling skill by 2–3 levels; boosts consciousness 10%, improving manipulation and combat accuracy. Unlocks species-specific work options in untrainable animals. Purchasable from **exotic goods traders, shaman merchants, slavers and faction bases**, plus ancient stockpiles, quest rewards and fishing. | **the obedience bolt** | **Design this one deliberately.** Jawas sell restraining bolts for droids; a mechanite injection that makes a living animal obedient is the same technology pointed at flesh. Sold by *slavers*, per the vanilla trader list — the game has already made the association for you. Whether your clan uses them is a charter question. |

---

## 6. Things that should not be for sale, and are

The black-market tier. One each, at most, per campaign.

**Mime** *(Alpha Animals)* — arrives on your map **indistinguishable from a normal colonist**. Its info panel gives no extra insight. Up to 1.5 days later it begins to feel hungry, and then it stops pretending. It butchers as a humanoid corpse. The author's own changelog note on the redesign reads, in full: *there is no god that can help you.*

SW name: **nessik** — vernacular *"the guest."* Frame it as a Clawdite-adjacent shapeshifter sold in a covered cage by a trader who leaves quickly. This is the single best one-shot horror set-piece available to you, and it costs nothing to set up: the trader sells you a "worker," and you don't find out for a day and a half.

**Fungal Husk** *(Alpha Animals)* — a bloated shambling corpse animated by an engineered strain of caterpillar fungus, built as a biological weapon; it exists to reach living animals and maul them, spreading the fungus. Butchers as a humanoid corpse.

SW name: **mossik**. Sold by nobody. Found in the Mycotic Jungle. The corpse-category detail is the horror: the game classifies it as a person.

**Mature Fleshbeast** *(Alpha Animals, VGE synergy)* — swallows prey whole and *retains it alive inside for one day*; kill it during that window and there's a good chance the prey comes out damaged but living. After that it digests, and excretes skeletons. With Genetic Rim/VGE installed, aberrant fleshbeasts mature into these after 15 days.

SW name: **sarlik** — *a juvenile sarlacc*. This is the closest the game gets to canon's most famous creature, and the one-day digestion window is a rescue-mission timer handed to you for free. A Cartel boss who keeps one under a floor grate is not an homage; it's the same idea arrived at independently.

**Infected Aerofleet** *(Alpha Biomes)* — an aerofleet whose prolonged exposure to ocular forest gases has raised red pustules and blisters across its membrane, converting its hydrogen into an acidic gas of unknown origin. Explodes acidically on death.

SW name: **blight-hessa**. Sold cheap by someone who says it's just a normal one.

---

## 7. Faction ownership — who deals in what

Mapping to `faction_roster_v2.md`:

| Faction | Their livestock trade | Signature creature |
|---|---|---|
| **Jawa clans (player)** | Anything that eats waste or metal; droid-adjacent utility | `slurrik`, `korrik`, `skreev` |
| **Hutt Cartel** | Power, uranium, vice, spectacle pets | `vokka`, `urrak`, `vissa`, `sarlik` |
| **Tusken / Sand Clans** | Mounts and medicine; they do not sell breeding stock | `obbak`, `hubbak` |
| **Homestead Compact** | Honest livestock, comfort animals, pest control | `zharn`, `kiba-fowl`, cats |
| **Bounty Hunters' Compact** | Weaponized companions, sentience catalysts | `thrass`, `grissk`, `vokkir` |
| **Geonosian Foundry Hive** | Castes, not animals — and regards `karramat` ownership as atrocity | `karrak`, `karrik` |
| **Gene Consortium** | The catalysts themselves, and anything that shouldn't exist | `vissarath`, labour-line Models |
| **Imperial Directorate** | Officially nothing; unofficially `thrass` suppression | — |
| **Free Droid Enclaves** | Buy `vokka` for power; fear `thrass` existentially | `dunnik` |

The `thrass` line is the good one. An animal that EMPs machines is simultaneously a Jawa tool, an Enclave nightmare, and an Imperial counter-droid asset. Three factions with incompatible interests in one dog.

---

## 8. The creature stall — the arrival, the haggle, the d20

This section used to be one table. It should be a small ritual, because the *arrival of a beast-monger* is one of the campaign's best recurring set-pieces and the mechanic to make them frequent is designed in §16. Use this when a livestock trader reaches you (a caravan on the ground, a visitor group at the ship, or — rarely — an orbital hold).

**Step 1 — who showed up (sets the stock).** Before rolling the cage, note *which faction's* trader it is, because that determines what's even possible to be inside (per the §16 per-faction stock table). A Tusken outrider will never have a `vissa` in a jar; a Cartel barge will never sell you honest nerf breeding stock. The faction is the first and most important filter — it's what makes "a livestock merchant arrived" a different sentence depending on whose banner is on the crate.

**Step 2 — the cage (d20 below).** Roll once for the headline animal. On a caravan carrying several head, roll 1–2 more times for the rest of the string and treat duplicates as "a matched pair" (which matters — a bonded pair is the only way most of these breed, and the guardrail in §1 says whether you *should*).

**Step 3 — what's wrong with it (d6, optional).** Every animal in a stall has a catch the seller isn't volunteering. This is where the horror and the comedy live.

| d6 | The catch |
|---|---|
| 1 | Nothing — it's exactly what it looks like. (The rarest and most unsettling result.) |
| 2 | Underfed / sick — cheap now, a vet bill later. |
| 3 | Wrong temperament — the "tame" tag is optimistic; expect a manhunter roll on transfer. |
| 4 | Bonded to something it lost — will pine, mood-debuff its handler for a season. |
| 5 | Not what the seller thinks it is (a `korrik` sold as a "metal-polisher"; a juvenile of something much larger). |
| 6 | Not an animal at all (see d20 roll 19 — the `nessik`). |

**Step 4 — the haggle.** Livestock is the one trade good where condition, temperament and *what happens on the ship* are all negotiable fictions. Prices below are relative; the hard silver numbers are in §17.

### The d20 cage table

Roll when a trade caravan arrives with livestock. Written for the journaling layer.

| d20 | In the cage | Asking price |
|---|---|---|
| 1 | `slurrik`, half-starved, eating the cage | Cheap |
| 2 | Three `kribb` in a jar | Trivial |
| 3 | `korrik`, muzzled (metal-eater; keep it off the hull) | Fair |
| 4 | `hubbak`, pregnant | Fair |
| 5 | `sikka`, sold as ornamental | Overpriced |
| 6 | `zharn` kid, "perfectly safe" | Fair |
| 7 | `nimm` moth, in a dress bag it is eating | Cheap |
| 8 | `skreev` pair, seller unaware they're related | Cheap |
| 9 | `hessa`, tethered, drifting | Fair |
| 10 | `rikk`, in a child's toy carrier | Trivial |
| 11 | `korrash`, drunk | Cheap |
| 12 | `ojja`, described only as "a jelly" | Fair |
| 13 | `vokka`, wired to the trader's own generator | Expensive |
| 14 | `thrass` pup — seller checks the road twice | Very expensive |
| 15 | `urrak` yearling, papers forged | Very expensive |
| 16 | `karrik`, sedated, waking up | Expensive |
| 17 | `vissa`, in a covered jar, no explanation offered | Absurd |
| 18 | `grissk`, ex-Compact, scarred | Expensive |
| 19 | **`nessik`** — presented as a hired worker, not livestock | Suspiciously reasonable |
| 20 | Seller has one **sentience catalyst** and wants to know what you'd use it on | Name your price |

Rolls 17, 19 and 20 are the ones that change a campaign. Rolls 1–12 are texture. That ratio is deliberate — a stall that offers a horror every time stops being frightening by the third visit.

---

## 9. Implementation notes

**Mods required for full coverage:** Alpha Animals (the bulk), Alpha Biomes (Metallovore, Chemfuel Myrmidon, Infected Aerofleet), Alpha Memes + Ideology (Eyeling, Unblinking Eye, Engorged Aberration — though all three are trader-obtainable without Ideology), Odyssey (hive queen, sentience catalyst, comfort pets), VGE (fleshbeast maturation chain).

**Load-order caution:** the Alpha Animals author warns that any mod adding animals to orbital traders indiscriminately breaks trade-tag handling. Check this before adding a "more traders" mod, or your creature stall becomes a random list instead of a curated one — which would waste every table above.

**Renames:** all of the above go into the same `Patches/` file as the bestiary, as `PatchOperationReplace` on `<label>` and `<description>`. Same generator script.

**Six ⚠ entries to verify in-game:** Helixien output, Chemfuel Myrmidon production, the mite family's diets, Skiphound mechanics, Crescendo Anole's current hediff behavior, and whether Fission Mouse actually carries a radiation effect or merely a suggestive name.

**Pricing — see §17 (now built, in silver).** v1 flagged that these creatures had no *prices*. That's resolved: §17 is a source-verified silver price list (denominated in the game's normalized economy per user direction, not water-liters). The water-liter phrasing survives only as *narration* — the journal can still say "that slug cost four days of drinking water," but the number the player pays is silver.

---

# THE REST OF THE MENAGERIE (expansion, 2026-08-07)

**Why this half exists.** Everything above (§1–§9) is the creatures *worth renaming* — Earth-portmanteau Alpha Animals and grotesque Alpha Memes things that need a Star Wars label to belong here. But the adopted stack is ~400+ animal defs, and the *majority* of the commerce-relevant ones **already have canonical Star Wars names** because they ship in Star Wars Animal Collection, or are self-evidently themselves (a T-rex is a T-rex). Those don't need a `PatchOperationReplace` on `<label>` — they need the same thing the renamed ones got: **a decision about who keeps them, who sells them, and what keeping them says.** That's what §10–§14 supply.

**Scope discipline (per campaign rules):** every creature named below is *confirmed present* in a mod already adopted in `required_mods.md` — Star Wars Animal Collection (Continued) `3497316713` (~150 defs), Megafauna `1440469633` (38 defs), Jurassic Rimworld – Dinosaurs Only `3541510004` (~120 defs), the Biomes! family (Core ~10 / Caverns ~71 / Polluted Lands ~31), Cephaloids `3753477123`, plus Odyssey/VGE. **Where I'm naming a specific creature from memory of the roster rather than from a re-read defName, it carries a ⚠ and must be confirmed in-game before any lore is built on the exact spelling.** Combat-power figures for Megafauna are source-verified (`required_mods.md` §Megafauna); SW-Collection and dino stats are *not* individually audited here and should be treated as "present, stats TBD."

---

## 10. The canonical Star Wars beasts — no rename, all placement

These ship with their real names in Star Wars Animal Collection. The work is entirely *where they live in the economy*, not what they're called. Grouped by the trade they belong to.

### 10.1 The mount & freight tier (the working animals)

This is the layer that makes the **Giddy-Up + Large Pawns + Bantha-caravan** stack (all adopted) mean something. These are bought to *work*, and their trade is honest, high-volume, and Compact/Tusken-owned.

| Creature | Mod | Trade role | Who deals in it | Note |
|---|---|---|---|---|
| **Bantha** | SW Animal Collection | The freight & wool spine. Wool, milk, meat, and it will defend a caravan line. | Jawa clans (wealth measured in bantha, per the bestiary's `ghorn` framing), Tusken, Compact | The single most important domestic animal in the campaign. Large Pawns makes it a genuine 2×2–3×3 footprint → real corridor/loading geometry on the ship. **Grazer guardrail applies: a bantha herd is fine as caravan muscle; don't turn it into a meat/wool printer.** |
| **Dewback** | SW Animal Collection | Riding + light freight reptile, heat-immune. | Tusken (signature), Compact patrols | The iconic desert mount. Pairs with the reptile-clade heat-tolerance fiction. Giddy-Up mount. |
| **Tauntaun** | SW Animal Collection | Cold-biome mount (Glowforest / cavern / polluted-cold tiles). | Compact, cavern settlements | Its niche is the *cold* tiles — a mount that works where the dewback can't. Gives the dark/cavern refuge tiles their own rideable animal. |
| **Kaadu** ⚠ | SW Animal Collection | Fast wetland/river runner. | Homestead Compact (river corridor) | Ties to the water-ecology layer (§13): a river-valley animal, abundant where it's wet. |
| **Varactyl** ⚠ | SW Animal Collection | Large climbing/riding lizard, forsaken-crags terrain. | Compact, wealthy Tusken | The prestige mount — big, colorful, expensive. A Varactyl string signals a rich clan. |
| **Ronto** ⚠ | SW Animal Collection | Heavy pack beast. | Jawa clans (canon Jawa animal!), Compact | **Canon-perfect for the player faction** — Ronto are literally the beasts Jawas drive in the films. Make this a starting-plausible Jawa freight animal. |
| **Nerf** ⚠ | SW Animal Collection | Herd meat/leather/milk animal ("nerf-herder"). | Homestead Compact | The Compact's honest livestock. **This is the one the grazer guardrail exists for** — a nerf herd is the textbook ranchable printer, so it belongs to the *NPC* economy you trade with, not a player barn. |
| **Massiff** | SW Animal Collection | Small vicious guard-reptile. | Tusken (camp guards), bounty hunters | The Tusken watchdog. Cheap, mean, everywhere in Sand-People fiction. |

### 10.2 The Hutt arena & spectacle tier (the dangerous purchases)

The Salacious-Crumb category's big brother: creatures kept not for utility but to *display power*, and the Cartel's arena economy. These are all high-combat-power and most are barely tameable — which is the point. Owning one is the flex.

| Creature | Mod | What it is | Who keeps it | Note |
|---|---|---|---|---|
| **Rancor** (+ **Chrysalide / Jungle Rancor** variants) | SW Animal Collection | The pit monster. Enormous, deadly, iconic. | Hutt Cartel (arena + trapdoor) | The canonical "under the trapdoor" set-piece. Near-untameable by design; a tamed one is a named-NPC-level event. Pairs with the `rannok`/*rancor-kin* thrumbear elder-form in the bestiary — so you get both the real Rancor AND a wild "rancor-kin" heavy. |
| **Acklay** | SW Animal Collection | Six-legged Geonosian arena killer. | Cartel arena, Geonosian Foundry Hive | Geonosis arena canon → gives the Foundry Hive a signature monster that isn't an insectoid caste. |
| **Reek** | SW Animal Collection | Horned arena charger, herbivore-but-deadly. | Cartel arena | The "looks like livestock, fights like a threat" animal. |
| **Nexu** | SW Animal Collection | Fast, vicious arena cat. | Cartel arena, exotic-pet buyers | The feline apex of the spectacle tier. |
| **Wampa** | SW Animal Collection | Cold-biome ambush predator. | (wild threat; trophy trade) | Belongs to the Glowforest/cavern/cold tiles as a wild ④-threat more than a kept animal — its "trade" is the pelt and the story. |
| **Krayt Dragon** + **Greater Krayt Dragon** | SW Animal Collection | The desert apex. | (wild; the pearl is the trade) | Deep-desert / forsaken-crags apex. Not kept — *hunted*. The gut-pearl is the exotic-treasure payoff, tying to the bestiary's `krayt dragon` = thrumbolizard elder-form ruling (real Krayt + wild krayt-kin both exist). |
| **Varactyl / Reek / Nexu as "tamed prestige"** | — | — | Cartel bosses, wealthy Directorate officers | The common thread: a tamed arena-tier animal on a leash is a *status display*, and its market price should be absurd (d20 roll 17-tier). |

### 10.3 The small canon fauna (vermin, pets, ambient life)

| Creature | Mod | Trade role | Note |
|---|---|---|---|
| **Womp Rat** | SW Animal Collection | Vermin / cheap pest, ambient desert life. | The "bullseye womp rats in my T-16" animal. Your ambient desert life-signal, canon-named — pairs with / can replace the bestiary's `gorrel` vermin niche. |
| **Gizka** | SW Animal Collection (+ **Rimwars – Gizka** `2885638908`) | Fast-breeding small pet/pest. | ⚠ **Grazer-guardrail flag:** Gizka are canonically a breeding-plague gag (KotOR's Gizka infestation). If the mod models fast breeding, it's a cute pet that becomes an infestation — *keep it a pest/pet novelty, don't let a tamed population print*. Good comedy, watch the mechanic. |
| **Porg** ⚠ | SW Animal Collection | Comfort/novelty pet. | The cute-pet slot — a humanizing animal for the Jawa hold, same role as the vanilla-comfort-pet note in §5. |
| **Vulptex** ⚠ ("crystal fox") | SW Animal Collection | Crystalline exotic pet. | Salt-flat / cavern crystalline creature; an exotic pet whose trade value is its appearance. Pairs with Biomes! Caverns crystal biomes. |
| **Dianoga** | SW Animal Collection | Trash/water-tank scavenger. | **The real one** (see §0-bis #1). A garbage-eating tank creature — genuinely Jawa-adjacent utility; keep it distinct from the `slurrik`. |
| **Mynock** | SW Animal Collection | Power/cable-leeching flyer. | **The real one** (see §0-bis #1). Drains power/ship systems — pairs conceptually with `sikka` and `korrik` but is its own canonical animal. |

---

## 11. Megafauna as commerce — the "walking mountain" trade

*Source-verified roster & combat-power in `required_mods.md` §Megafauna.* 38 prehistoric heavies, 24 desert-spawning, 16 predators; the top third are thrumbo-class (cp 500–750). In *commerce* terms these are almost never kept — they're **hunted for bulk, feared as territory, and occasionally tamed as a single prestige beast of burden.** Their "trade" is mostly the carcass.

| Creature (verified present) | cp | Commerce framing |
|---|---|---|
| **Purussaurus** (cp 750), **Titanoboa** (650), **Gigantophis** (600) | apex | Not traded — territory. A tile with one is a tile you time your exit off of. The "trade" is the hide/meat if you can kill it and the story if you can't. |
| **Paraceratherium**, **Elasmotherium**, **Deinotherium**, **Diprotodon** (herbivore heavies) | ~500–550 | The rare tamed *freight* prestige animal — a single one hauls enormous loads (Large Pawns 3×3). **Grazer guardrail: one working beast is fine; a breeding herd of a large grazer is exactly the slow meat/leather printer the standing rule bans — don't ranch it** (mod ships a per-species spawn toggle + global multiplier to help). |
| **Titanis** (terror bird), **Andrewsarchus**, **Short-faced Bear**, **Megalania**, **Dinocrocuta**, **Daeodon** | ~375–500 | Pure ④-threat wildlife. Trophy/carcass trade only. Manhunter-prone (many at `manhunterOnDamageChance` 1.0) → wound one, the pack turns. |
| **Doedicurus**, **Pulmonoscorpius**, **Procoptodon** | mid | Desert-native texture; occasional exotic-pet or trophy interest. |

**Frame:** Megafauna are the reason the Homestead Compact posts bounties and the Cartel runs arenas. A Cartel that can deliver a *live* cp-550 heavy to an arena is powerful; the fact that "nobody has managed it twice" (the `rannok` note) is the flavor. This is the layer that makes the wild desert feel *inhabited by things bigger than you*, and its commerce is bounty + trophy + the very rare tamed titan, never a herd.

---

## 12. The dinosaur trade + Cephaloids + cavern & polluted fauna

### 12.1 Jurassic Rimworld – Dinosaurs Only (`3541510004`, ~120 defs, pillar-clean bestiary — no buildables/research)

Verified in `required_mods.md`: this is a *pure bestiary* (the "Dinos Only" branch strips the parent's park buildings). So dinosaurs enter the campaign exactly like Megafauna — **wild threat, hunted carcass, rare tamed prestige beast** — with the same grazer guardrail on any tamed breeding herd.

| Creature (confirmed in roster) | Commerce framing |
|---|---|
| **T-rex, Giganotosaurus, Spinosaurus** | Apex predators. Territory & trophy, not kept. Excellent Krayt-Dragon-adjacent reskin candidates if you ever want more "dragons" without a dragon mod. |
| **Argentinosaurus** (titanic sauropod) | The single largest freight-prestige candidate in the stack — a living cargo hauler. Grazer guardrail: one, not a herd. |
| **Therizinosaurus**, the **raptor line** (Velociraptor/Deinonychus etc.) | Pack hunters → the "flock that runs down the wounded" threat. Raptors as a *trained pack* = a Bounty-Compact signature (parallels the `grissk`/`thrass` weaponized-companion tier). |
| **Indominus / Indoraptor** (JP apexes) | The exotic super-predator — a Cartel/Consortium "we made something we shouldn't have" set-piece animal, once. |

**Roster-dilution note (carried from `required_mods.md`):** SW + dinos + Megafauna + VGE + Alpha + Polluted = ~400+ defs. The risk is *encounter dilution* (biomes read as a random zoo). Mitigation is the commonality-tuning pass, not cuts — in the Phase-A playtest, dial **desert/SW-appropriate** creatures UP and off-theme dinos/fauna DOWN so the sea-of-desert keeps its identity. The creature-*trade* is unaffected (traders can offer anything), but *wild spawns* should stay themed.

### 12.2 Cephaloids (`3753477123`) — the bizarre-beast slot

Adopted with the explicit **pets-not-herds guardrail** (per `required_mods.md`). ⚠ I have not re-read the Cephaloid defNames this session, so specific creature names are deferred to an in-game check. Commerce framing: whatever they are, they're the "there's something genuinely alien in the cage" exotic — Cartel/Consortium curiosity trade, single specimens, never a breeding stock. Confirm defNames + whether any produce a resource (if so, apply the §1 living-machinery guardrail).

### 12.3 Biomes! Polluted Lands fauna (~31 defs, source-verified in `required_mods.md`)

These appear on *polluted/toxic tiles* the rogue-android faction sours (they ride the pollution mechanic, patched into existing biomes incl. AridShrubland). In commerce terms they're the **wasteland-scavenger trade** — ugly, hardy, and mostly sold cheap by people working poisoned ground.

| Creature (verified `BMT_` roster) | Commerce framing |
|---|---|
| **⚠ Tox-wool sheep (`BMT_ToxSheep`)** | **THE flagged fast-breeder** — `gestationPeriodDays` 5.661, shearable every 9 days. A tamed flock is a wool printer = the banned BioRanch pattern. **Ruling (from required_mods.md): adopt as wild fauna; do NOT ranch a tamed tox-wool flock.** Belongs to the NPC wasteland economy, not a player barn. |
| **Waste hound, fenrid stoat, carrion vulture, screecher, swarmcaller** | Wasteland predators/scavengers → guard-animal & threat trade on poisoned tiles. |
| **Varmot** (crop-stealer), **maligoat, gastro toad, giant snail, polluwog, tainted turtle** | Vermin/nuisance tier → the "poisoned-ground version of the womp rat." |
| **Pustule hornet** (+ queen/colony/domesticated variants), **mutating tumorfish** (multi-stage spawner), **megaphorid** (+larva) | **Brood/breeder guardrail:** the queen and multi-stage spawners get the "wild threat, not a player brood" treatment — don't domesticate into printers, same as the insect-hive rulings. |
| **Mucklurker catfish, megakrill, lyncus seal, bloodletter petrel** | Polluted-water fauna → ties to the water-ecology layer (§13): abundant where it's wet, even where the water is poisoned. |
| **Tox-wool sheep aside**, the rest are pillar-clean wild fauna. | — |

### 12.4 Biomes! Caverns fauna (~71 defs) + Biomes! Core (~10)

⚠ Roster not individually re-read this session. Commerce framing (safe to state without exact names): the cavern fauna populate the **dark/refuge tiles** (Crystal Caverns / Earthen Depths / Fungal Forest), so their trade is tied to the cavern-settlement economy — cave-adapted mounts (pairs with the bestiary's `dunnik`/*cave-runner*), fungal-forage grazers, and lightless predators. These are the animals the **Free Droid Enclaves and cavern-dwellers** deal in. Confirm specific defNames before renaming any; most may not need renaming if they're already opaque/alien.

---

## 13. Water-ecology layer — where the trade is densest (user directive, 2026-08-07)

*Primary home for this mechanic is `desert_world_design.md` §3(f); summarized here because it directly drives the creature trade.*

On this world, **water changes the rules of both flora and fauna:**

- **Wild vegetation on any watered tile grows *freakishly* fast** — aggressively, not decoratively. Jungle, vines, and scrub on oasis/river/coast/polluted-wet tiles reclaim cleared ground constantly; the player must **mow it down just to hold paths and safe zones**. This is a maintenance *cost* of operating near water, and it pairs with the hostile-flora hazards (Agarilux Prime spore-fields, §3(c) of the world doc) — the growth both hides threats and re-hides them after you've cleared them.
- **Animal spawns are unusually frequent and abundant near water.** Watered tiles are *thick* with wildlife where the desert is empty. 

**Commerce consequence (the reason it's in this doc):** the **water-adjacent tiles are the campaign's densest wild-capture and creature-trade grounds.** If you want to *tame* rather than *buy*, the oasis/river/coast waterline is where you do it — but it's also where the vegetation fights you and the predator density is highest, so the reward (abundant tameable stock, including the water-clade animals: Kaadu, mucklurker catfish, megakrill, the polluted-water fauna) is gated behind the ④-threat of a crowded, overgrown, ambush-friendly shoreline. This is the anti-exponential shape again: the richest capture grounds are the most dangerous and most labor-intensive to hold, so wild-taming can't quietly out-scale the honest trade.

**Design payoff:** it gives the water tiles a *fauna* identity to match their *flora* aggression and their water-abundance rating in the §3A partition — the oasis isn't just "the food/water tile," it's "the tile crawling with life you can catch if you can survive the crowd and keep the jungle off your paths."

---

## 14. Updated faction ownership — the full menagerie (supersedes §7 where they overlap)

§7 mapped the *renamed utility* creatures. This folds in the canonical SW beasts, Megafauna, dinos and polluted fauna. Where a faction appears in both, this is the fuller picture.

| Faction | Full livestock/creature trade | Signature creatures |
|---|---|---|
| **Jawa clans (player)** | Waste/metal-eaters + droid-adjacent utility + canon Jawa beasts of burden | `slurrik`, `korrik`, `skreev`, **Ronto**, **Dianoga** (the real one), a comfort **Porg** |
| **Hutt Cartel** | Power/uranium/vice pets + the **arena & spectacle** trade | `vokka`, `urrak`, `vissa`, `sarlik`, **Rancor**, **Acklay**, **Reek**, **Nexu**, tamed Megafauna titans |
| **Tusken / Sand Clans** | Mounts + medicine; do not sell breeding stock | `obbak`, `hubbak`, **Dewback**, **Massiff**, **Varactyl** (prestige) |
| **Homestead Compact** | Honest livestock, comfort animals, pest control, **the nerf-herd meat trade** | `zharn`, `kiba-fowl`, cats, **Bantha**, **Nerf**, **Kaadu** |
| **Bounty Hunters' Compact** | Weaponized companions, trained predator packs, sentience catalysts | `thrass`, `grissk`, `vokkir`, **raptor pack**, **Nexu** |
| **Geonosian Foundry Hive** | Castes, not animals — plus the **arena monsters** (Acklay canon) | `karrak`, `karrik`, **Acklay** |
| **Gene Consortium** | The catalysts + anything that shouldn't exist + the JP-apex "we made it" set-pieces | `vissarath`, labour-line Models, **Indominus/Indoraptor** |
| **Imperial Directorate** | Officially nothing; unofficially `thrass` suppression + prestige tamed arena beasts for officers | — |
| **Free Droid Enclaves / cavern-dwellers** | Buy `vokka` for power; cave-adapted fauna trade | `dunnik`, **Tauntaun**, Biomes! Caverns fauna |
| **Rogue-android faction (wasteland)** | Sours tiles → deals implicitly in the polluted fauna that follow | tox-wool sheep (wild), waste hounds, wasteland scavengers |

---

## 15. Implementation notes (expansion)

- **Renames vs. placement — two different jobs.** §1–§6 creatures get `PatchOperationReplace` on `<label>`/`<description>` (same `Patches/` file + generator script as `Alien_Bestiary.md`). §10–§12 creatures **mostly do NOT get renamed** — they already have canonical names. Their "implementation" is (a) spawn-commonality tuning per the roster-dilution pass, (b) trader-stock/faction assignment, and (c) the d20-stall additions below. Only rename a canonical creature if its shipped label is *wrong* for the setting (rare).
- **⚠ Confirm-before-build list (defNames not re-read this session):** Kaadu, Varactyl, Ronto, Nerf, Porg, Vulptex spellings/presence in SW Animal Collection; the full Cephaloids roster; the Biomes! Caverns + Core rosters. Pull the About/Defs from `mod_sources/` (SW Animal Collection is confirmed there) before coining lore on any exact name. The Megafauna list and the Polluted Lands `BMT_` list ARE source-verified (via `required_mods.md`).
- **The grazer/printer guardrail spans this whole document — but the gravship does most of the enforcing (see the upgraded §1 box).** Renamed resource-excreters (§1: radyak/tetraslug/aerofleet/helixien), the tox-wool sheep (§12.3), Gizka (§10.3), Nerf and the large Megafauna/dino grazers (§10.1/§11/§12.1), and the insect broods (§12.3) are all the same *class* of animal — a thing that eats and breeds — but on a nomadic ship they are **structurally self-limiting**: the hold caps how many can board, and the forage-hostile / heat-hostile destination tiles cull whatever you do bring. So the working posture is "keep and fly a working few; let the loop cap them," NOT an iron no-ranch rule. The rule only re-arms in two cases: (a) a **sessile resource-printer building** (BioRanch etc.) — permanently banned, it bypasses ship-cap and grazing entirely; and (b) a **long dig-in on one hospitable tile** (the §13 oasis), where breeding *can* run away — then apply sterilize/don't-breed until you lift. The NPC factions (Cartel, Compact) are planet-bound and *allowed* to run the real herds off-screen — that asymmetry is *why you trade with them.*
- **d20-stall additions (optional roll-expansion):** slot the new tier onto a d20+ or a second table — e.g. a **Rancor cub "guaranteed docile" (it is not)**, a **raptor "pair, bonded"**, a **Ronto "sound, papers real for once"**, a **tamed Bantha "in milk"**, a **Vulptex "crystal fox, sold as jewelry"**, and the horror-tier **"nerf that isn't a nerf"** (a Mime/`nessik` reskin). Keep the same ratio: mostly texture, rarely a campaign-changer.
- **Pricing lives in §17 now (silver, not water).** The v1 doc twice recommended a price sheet denominated in *days of drinking water*. Per user direction 2026-08-07 that's **superseded**: the price list is denominated in the game's **normalized silver economy** (§17), because silver is what the trade UI actually uses and what every price above ("cheap / expensive / absurd") should resolve to. The water-liter framing is still a nice *narration* device — a journal entry can say "that slug cost us a season of water" — but the number the player pays is silver.

---

## 16. Frequent livestock merchants — the beast-monger subsystem

**The pitch (why this is deeply Star Wars).** The franchise's economy is *transactional and alive*. Mos Eisley has a creature stall. Jabba's palace runs on somebody deciding a monkey-lizard was worth feeding. A dewback is tied outside every cantina. Unlike most RimWorld settings — where a "trader" is an abstract stock list — Star Wars trade is defined by the *animal in the cage* and *the person selling it*. So making **livestock merchants frequent and faction-flavored** isn't a QoL tweak; it's one of the highest-leverage worldbuilding moves available, and it's also the *acquisition-gate that makes the §1 guardrail work* — if you can reliably **buy** the strange beasts, you never need to breed them, which is exactly the anti-exponential posture this campaign wants.

**Established vs. designed:** everything in §16.1 (the field names, tags, and def classes) is **source-verified** from the mod stack this session (`StarWarsAnimalCollection_src`, `BiomesCore_src`, `Outer-Rim-Core-main`, `BiomesFossils_src`). The per-faction *assignments* in §16.3 are **design** — my mapping of verified animals+tags onto the `faction_roster_v2.md` factions.

### 16.1 How to add them natively — the verified mechanism (no exotic mod needed)

RimWorld already has every hook this needs. The whole subsystem is **XML-only** (new `TraderKindDef`s + edits/patches to faction defs); no assembly, so it's 1.6-safe and Cherry-Pick-clean.

**(a) A trader's animal stock is a `StockGenerator_Animals` line, filtered by trade tag.** Verified from `BiomesCore_src/1.6/Defs/BMT_TraderKinds.xml`:

```xml
<li Class="StockGenerator_Animals">
  <tradeTagsSell>          <!-- what the trader SELLS to you -->
    <li>AnimalFighter</li>
  </tradeTagsSell>
  <tradeTagsBuy>           <!-- what it will BUY from you -->
    <li>AnimalUncommon</li>
    <li>AnimalExotic</li>
  </tradeTagsBuy>
</li>
```

The key realization: **`tradeTagsSell` is the entire per-faction lever.** Give the Cartel trader `AnimalExotic` + `BadassAnimal` + `Sithspawn` and it sells arena monsters; give the Homestead Compact trader `AnimalFarm` + `AnimalCommon` and it sells honest herd stock. You never have to name individual animals — the tags already ship on the defs (§16.2).

**(b) The tags already exist on the animals — verified from the SWAC source.** `StarWarsAnimalCollection_src/1.6/Defs/ThingDefs_Races/Races_Animal_SW.xml` tags all ~160 canonical beasts with vanilla trade tags **plus a custom `Sithspawn` tag** (found on `Gundark`, `Tukata`, and 8 others). Confirmed examples:

| Animal | Actual `tradeTags` (verified) |
|---|---|
| Bantha | `StandardAnimal, AnimalCommon, BadassAnimal, AnimalFarm` |
| Nerf / Shaak / Kybuck / Nuna / Eopie | `AnimalCommon, AnimalFarm` (the honest-herd cluster) |
| Dewback | `StandardAnimal, AnimalCommon, BadassAnimal, AnimalFighter` |
| Massiff | `AnimalPet, AnimalFighter` |
| Kaadu | `AnimalCommon, AnimalFighter` |
| Varactyl / Bordok / Blurrg / Orray | `AnimalUncommon` (+`AnimalFighter`/`AnimalFarm`) |
| Rancor / Nexu / Reek / KraytDragon / Wampa / Roggwart | `AnimalExotic, BadassAnimal, AnimalFighter` |
| Acklay / Fambaa / Dianoga / Hssiss / Lylek / Ronto / Vornskyr | `AnimalExotic, AnimalFighter` |
| **Gundark / Tukata** | `AnimalExotic, **Sithspawn**, AnimalFighter` |
| KowakianMonkeyLizard | `AnimalExotic, AnimalPet` — **the real Salacious-Crumb animal ships in SWAC** |
| Porg | `AnimalExotic, AnimalFarm` · Vulptex | `AnimalPet, AnimalExotic` |
| WompRat / Mynock / Bogwing | `AnimalCommon` (ambient/vermin tier) |

*This is a gift:* the mod authors already sorted the whole SW bestiary into exactly the buckets a per-faction trader needs. The Cartel's "arena tier" is literally the set tagged `AnimalExotic + BadassAnimal`; the Compact's "honest herd" is the `AnimalFarm` set; the sinister factions get `Sithspawn`.

**(c) Wire the trader to a faction — three verified list fields.** From `Outer-Rim-Rebel-Alliance-main/.../FactionDefs.xml`, a `FactionDef` carries:

```xml
<visitorTraderKinds>  <li>YourFaction_BeastMonger_Visitor</li>  </visitorTraderKinds>
<caravanTraderKinds>  <li>YourFaction_BeastMonger_Caravan</li>  </caravanTraderKinds>
<baseTraderKinds>     <li>YourFaction_BeastMonger_Base</li>     </baseTraderKinds>
```

`caravanTraderKinds` = the trade caravans that *walk to you* (the primary "a beast-monger arrived" event). `visitorTraderKinds` = trader groups that visit. `baseTraderKinds` = what you can buy when *you* caravan to their settlement. For existing modded factions we don't own, add these via a `PatchOperationAdd` into the faction def (same patch discipline as the bestiary renames) rather than editing the mod.

**(d) Frequency — the "frequent" in "frequent merchants" — is `commonality` on the `TraderKindDef`.** Verified: `BMT_Caravan_Paleontologist` sets `<commonality>0.25</commonality>`. To make beast-mongers *frequent*, give the livestock `TraderKindDef`s a **high commonality** relative to other trader kinds, and/or lower the world's overall trade-caravan interval. This is the single knob that turns "you see a livestock trader every few seasons" into "the creature stall is a fixture of the campaign." Recommend tuning it up in the Phase-A playtest until arrivals *feel* Mos-Eisley-frequent without swamping the other trade types.

**(e) This route also fixes the §9 orbital-noise caution.** The Alpha Animals author warns that any mod dumping animals into orbital traders indiscriminately breaks trade-tag curation. By building **our own curated `TraderKindDef`s with explicit `tradeTagsSell` lists**, we get frequency *without* that breakage — the stock stays hand-shaped per faction instead of becoming a random zoo. So the mechanism and the earlier warning resolve together: don't install a generic "more animal traders" mod; ship a small `Patches/` + `Defs/` pair of our own.

**Optional mods (only if we want the plumbing pre-built) — VERIFY 1.6 before adopting:**
- A "trader diversity / more frequent caravans" mod would raise arrival frequency globally, but risks the orbital-noise problem in (e). ⚠ Prefer our own `commonality` tuning first.
- **Vanilla Trading Expanded**-family (if present for 1.6) adds trader ships/settlement stock depth. ⚠ Not currently in the adopted stack — treat as a *later* consideration, not a dependency. The subsystem above needs **nothing beyond base RimWorld + the animals we already have.**

### 16.2 The five beast-monger archetypes (the merchant, not just the stock)

A merchant is a *character*, and the delivery mode is part of the fiction. Five archetypes, each mapped to a faction and a `TraderKindDef` shape:

1. **The Sand-Caravaneer** (Tusken / *caravan*). Arrives on foot/dewback across the dunes with mounts and medicine. Sells working reptiles, never breeding stock. High commonality — the everyday beast-monger. `tradeTagsSell: AnimalCommon (reptile-clade), AnimalPet(Massiff)`.
2. **The Homestead Drover** (Homestead Compact / *caravan + base*). The honest herd-trader: bantha, nerf, shaak, poultry, comfort pets. This is the one you buy your *working* animals from. `tradeTagsSell: AnimalFarm, AnimalCommon`.
3. **The Cartel Beast-Barge** (Hutt Cartel / *visitor + base*, rare + expensive). Rolls in heavy: arena monsters, grotesque status pets, the "resource" beasts, and the one-shot horrors. Lower commonality, absurd prices. `tradeTagsSell: AnimalExotic, BadassAnimal, AnimalFighter` + hand-added grotesques.
4. **The Compact Hunter's Kennel** (Bounty Hunters' Compact / *visitor*). Sells weaponized companions and trained predator *packs* — the `thrass`/`grissk`/raptor tier — and carries sentience catalysts. `tradeTagsSell: AnimalFighter, AnimalPet(Anooba/Strill)`.
5. **The Consortium Specimen Courier** (Gene Consortium / *rare visitor*, sinister). Doesn't sell "animals" — sells *specimens*: `Sithspawn`-tagged beasts, VGE aberrations, the "we made this" set-pieces, and the black-market `nessik`/`sarlik` tier. Rarest arrival; every visit is a set-piece. `tradeTagsSell: Sithspawn, AnimalExotic` + hand-added aberrations.

### 16.3 Per-faction stock specialization — WHO sells WHAT (and who sells nothing)

Design layer, built on the verified tags in §16.1. The important discipline the user asked for: **be specific about which animals each faction sells, *if any* — some factions sell no livestock at all**, and that absence is characterization.

| Faction | Sells livestock? | `tradeTagsSell` (the lever) | Signature stock | Never sells |
|---|---|---|---|---|
| **Jawa clans (player)** | Buys more than sells | (player — buys via any of the above) | Trades *droids*, not beasts; keeps `slurrik`/`korrik`/`skreev`, a **Ronto** (canon Jawa beast), a comfort **Porg** | Doesn't run a herd trade — Jawa acquire, they don't ranch |
| **Homestead Compact** | ✅ **Yes — the herd trade** | `AnimalFarm, AnimalCommon` | **Bantha, Nerf, Shaak, Kybuck, Nuna, Eopie**, comfort cats/pandas, **Kaadu** (river) | Arena monsters, `Sithspawn`, grotesques |
| **Tusken / Sand Clans** | ✅ Yes — **mounts & medicine only** | `AnimalCommon` (reptile), `AnimalPet` | **Dewback, Massiff**, `hubbak` (cactipine medicine), **Varactyl** (prestige) | **Breeding stock** (cultural — they sell the animal, never the *bloodline*) |
| **Hutt Cartel** | ✅ Yes — **the spectacle & vice trade** | `AnimalExotic, BadassAnimal, AnimalFighter` | **Rancor, Acklay, Reek, Nexu, KowakianMonkeyLizard**, `vissa`, `sarlik`, resource beasts (`urrak`/`vokka`), tamed Megafauna titans | Nothing is off-limits — that's the point |
| **Bounty Hunters' Compact** | ✅ Yes — **weaponized companions** | `AnimalFighter, AnimalPet` | `thrass`, `grissk`, **Anooba, Strill, CorellianHound**, trained **raptor packs**, **sentience catalysts** | Farm/food animals (beneath them) |
| **Gene Consortium** | ✅ Rarely — **specimens, not livestock** | `Sithspawn, AnimalExotic` | `Gundark`, `Tukata`, VGE aberrations, `vissarath`, the `nessik`/black-market tier, "we made it" JP-apexes | Anything honest or useful |
| **Geonosian Foundry Hive** | ❌ **No — sells no animals** | — | Deals in *castes*, not property; regards a kept `karramat` (hive queen) as atrocity | **Everything** — the refusal *is* the characterization |
| **Imperial Directorate** | ❌ **Officially no** | — (unofficial `thrass` suppression only) | Officers privately buy prestige arena beasts; the state sells none | Publicly, all livestock (beneath imperial dignity) |
| **Free Droid Enclaves** | ❌ **No — they buy, don't sell** | — (buyer of `vokka` for power) | Fear `thrass` existentially; have no herds to sell | They're droids — livestock is alien to them |
| **Rogue-android wasteland** | ~ Implicitly — **poisoned-ground fauna** | `AnimalCommon` (polluted-tile) | Tox-wool sheep (wild), waste hounds, wasteland scavengers follow their soured tiles | Anything clean or healthy |

**The design payoffs:** (1) *Frequency + faction filter = flavor.* "A livestock merchant arrived" now resolves to five very different sentences. (2) *Three factions selling nothing* (Foundry, Directorate, Enclaves) is as characterful as the seven that do — the Foundry's refusal to treat life as property is a whole worldview in one empty stock list. (3) *The buy-not-breed loop:* because the Compact reliably sells working stock and the Cartel reliably sells the strange beasts, the player's correct move is almost always **buy the one you need and fly on** — which is precisely the §1 anti-exponential posture, now delivered by the *economy* rather than by a rule.

### 16.4 Encounter tables per merchant (keeping the horror ratio)

Each archetype gets its own d20-style stock lean, but **all of them preserve the §8 ratio: mostly texture, rarely a campaign-changer.** The Sand-Caravaneer and Homestead Drover are ~95% honest stock; the Cartel Beast-Barge is where roll-17-tier horrors cluster; the Consortium Courier is *entirely* the dangerous tail (which is why it's the rarest arrival). Build these as `commonality`-weighted sub-tables when the subsystem goes to `Defs/` — the frequent merchants stay *safe and useful* so the rare one stays *frightening*.

---

## 17. The price list — normalized silver (per user, 2026-08-07)

**Denomination:** the game's own **silver market economy**, not water-liters (that recommendation is retired; see §15). These are the numbers the trade UI actually resolves, so they're the ones worth pinning down.

**What's established vs. designed:** the SWAC and Megafauna columns below are **source-verified `<MarketValue>` reads** from the installed mod sources this session (`StarWarsAnimalCollection_src/.../Races_Animal_SW.xml`, `Megafauna_src`). The Alpha Animals / Alpha Memes / Biomes rows are **design targets** (⚠ — I did not re-read those defNames' market values this session; confirm in-game before treating them as exact). *Trade price ≠ market value:* a trader typically **sells to you above** market value (price multiplier + a livestock premium) and **buys from you below** it, so treat every number as the base the UI multiplies, and read the "player pays roughly" band as the practical out-the-door cost.

**The pricing doubles as a second economic brake.** Deliberately, the resource/spectacle beasts sit high enough that *price itself* is an anti-exponential lever: you can afford **one** radyak or **one** arena monster, not a herd. This is the §1 guardrail expressed in silver — the ship caps how many can travel, the destination tiles cull what can't graze, and the price caps how many you can acquire in the first place. Three independent brakes on the same exponential.

### 17.1 Canonical SW beasts — VERIFIED market values (silver)

Straight from SWAC source. Sorted low→high; "player pays roughly" applies a typical ~1.4× sell multiplier as a planning band (confirm against your actual trade-price settings).

| Animal | `MarketValue` (verified) | Player pays roughly | Tier / why |
|---|---|---|---|
| **Porg** | 75 | ~105 | Comfort/novelty — the cheap humanizing pet |
| **Gizka** | 100 | ~140 | Cheap pest-pet (⚠ breeding-plague — buy one, don't farm) |
| **Vulptex** ("crystal fox") | 100 | ~140 | Exotic *looks*, trivial cost — value is cosmetic |
| **Kowakian Monkey-Lizard** | 100 | ~140 | The real Salacious-Crumb animal — cheap, useless, perfect court pet |
| **Womp Rat** | 150 | ~210 | Ambient vermin / cheapest "livestock" |
| **Eopie / Shaak** | 200 | ~280 | Bottom of the honest-herd tier |
| **Kaadu** | 300 | ~420 | River-runner mount (water-ecology, §13) |
| **Nerf / Massiff / Anooba** | 400 | ~560 | Herd meat-animal / guard-reptile / war-hound |
| **Strill** | 450 | ~630 | Bounty-hunter companion |
| **Varactyl** | 500 | ~700 | Prestige mount — a string of these signals a rich clan |
| **Bantha** | 650 | ~910 | The freight & wool spine — the campaign's key domestic |
| **Dewback / Tauntaun / Blurrg** | 700 | ~980 | Working mounts (hot / cold / all-terrain) |
| **Dianoga** | 750 | ~1,050 | Trash-tank scavenger (the *real* one, §10.3) |
| **Nexu / Ronto** | 1,000 | ~1,400 | Arena cat / heavy Jawa pack-beast |
| **Reek** | 1,500 | ~2,100 | Arena charger |
| **Acklay** | 1,800 | ~2,500 | Geonosian arena killer |
| **Wampa / Gundark / Tukata** | 2,500 | ~3,500 | Ambush predator / **`Sithspawn`-tagged** monsters |
| **Rancor** | 3,000 | ~4,200 | The pit monster — a tamed one is a named-NPC event |
| **Krayt Dragon** | 3,600 | ~5,000 | Desert apex — usually *hunted* for the pearl, not bought |
| **Greater Krayt Dragon** | 7,000 | ~9,800 | The single most expensive kept beast in the SW set |

### 17.2 Megafauna — VERIFIED market values (silver)

From `Megafauna_src`. These are the "walking mountain" trade — mostly hunted/feared, rarely a single tamed prestige beast (§11). Note the *products* are the real trade for the apexes.

| Creature | `MarketValue` (verified) | Note |
|---|---|---|
| **Titanis** (terror bird) | 1,000 | Trained-pack threat tier |
| **Diprotodon / Elasmotherium** | 1,300 | Herbivore freight-prestige (one, not a herd) |
| **Daeodon** | 1,600 | Manhunter-prone predator |
| **Deinotherium** | 1,750 | Freight heavy; tusk alone = 600 |
| **Andrewsarchus** | 2,200 | Apex predator |
| **Gigantophis / Titanoboa** | 2,500 / 2,700 | Serpent apexes — territory, not livestock |
| **Purussaurus** | 3,200 | cp-750 apex; the "time your exit off it" tile-owner |
| **Paraceratherium** | 3,700 | Largest verified freight-prestige beast in Megafauna |
| *Fertilized eggs* (Titanis 80 / Gigantophis 180 / Titanoboa & Purussaurus 200) | 80–200 | The **cheap** way in — buy an egg, not the adult (and a great trader-stock item) |

### 17.3 The renamed utility beasts — DESIGN TARGETS (⚠ confirm in-game)

Alpha Animals / Alpha Biomes / Alpha Memes market values not re-read this session. Prices below are *design intent* calibrated to the verified anchors above — set high on the resource/horror beasts on purpose (the price brake).

| Creature | Target silver | Player pays roughly | Rationale |
|---|---|---|---|
| `slurrik` (slurrypede) | ~250 | ~350 | Cheap — it eats garbage, which is the appeal |
| `korrik` (hull-eater) | ~200 | ~280 | Cheap and slightly cursed; muzzle included |
| `skreev` (murkling) | ~300 | ~420 | The Jawa-perfect scavenger |
| `hubbak` (cactipine, medicine) | ~500 | ~700 | Strategic — a pen replaces buying medicine |
| `zharn` (shock goat) / `sikka` (drainer) | ~350 / ~250 | ~490 / ~350 | Utility with a catch |
| `vokka` (tetraslug, power) | ~1,800 | ~2,500 | **Priced as a power plant** — you buy one, not a herd |
| `urrak` (radyak, uranium) | ~3,500 | ~4,900 | **Priced like a Rancor** — the scarcity *is* the story; a barn is unaffordable by design |
| `hessa` (aerofleet, power-gel) | ~1,200 | ~1,700 | Priced above comfort, below the uranium beast |
| `vissa` (eyeling) / `vissarath` (elder) | ~1,500 / ~4,000 | ~2,100 / ~5,600 | Status-pet absurdity; the elder is a named-NPC object |
| `sarlik` (juvenile sarlacc) | ~3,000 | ~4,200 | Cartel-boss trapdoor tier |
| **`nessik` (the Mime "worker")** | **~600, "suspiciously reasonable"** | ~840 | The horror is that it's *cheap* — the low price is the bait, not a discount |
| **sentience catalyst** (item) | ~1,000–1,700 | market | Per the vanilla exotic-goods/slaver price band; "name your price" in-fiction |

### 17.4 How to say it in the fiction (the water framing survives as narration)

The silver number is what the player pays; the *water* line is how the journal remembers it. Both can coexist: the trade log shows "Bantha — 910 silver," and the campaign narration says "we gave up a season's water ration for the bantha." Silver is the mechanic; water is the memory. That keeps the desert-economy texture the water framing was reaching for **without** overriding the game's normalized economy the user asked to price in.
