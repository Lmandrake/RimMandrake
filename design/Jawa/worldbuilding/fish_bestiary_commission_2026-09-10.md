# The Ash'karr fish bestiary — FISH_BESTIARY_COMMISSION_1, the proposal

_Design proposal, 2026-09-10, Fable seat. This doc **PROPOSES** — no XML, no
roster JSON, nothing in `src/` is written by it. It ratifies into a build item
(the `_fish_assignment_proposal.md` → `FISH_TYPES_PATCH_BUILD_1` pattern). Every
name, stat and weight below is an offer for the owner to keep, strike or rename._

**The commission, verbatim (owner, 2026-09-10):** *"Commission lots of fishes! I
would like there to be a plethora of different kinds for each biome actually. Fish
are easy. Lets get creative! Squid like. Octopus like. Eel like. Crustaceans.
Floaters. Jellyfish. Cucumbers. Bring in that Star Wars creature richness."*

**What it delivers:** 32 new catchable species across the seven waters that can
carry a fishing table, in eight registers; 4 new prize items; 6 rare-catch tables;
and the four owed defs (Scald thermophile shoal, Cathedral coolant eel, Wasteland
brine-battery, Twilight shoal) fully specified in §4. The `swfish_` donor tables on
the Weeping Stones retire when their replacements land; nothing ratified this
morning is reopened.

**Evening reconciliation (same day, second Fable pass):** checked against the
sea-beast family built tonight (`src/RimStarWars/SWBestiary/Defs/SeaBeasts/`, the
Miasma nursery `4b1f5b71`) and the hydrocarbon commission — no duplicate species,
one sibling entry folded in (§2E, the bladderboil catch), and 🔴 one engine finding
that changes the Greentide table: the live `BiomeFishTypes_Greentide.xml` wires the
scalefish **race** defs into `fishTypes`, and the engine makes catches with
`ThingMaker.MakeThing` (§0) — three scalefish **catch items** are now owed (§2C,
§6.7). Everything else stands as written this morning.

---

## 0. The rules every entry obeys

**Engine (MEASURED, `rosters/_fish_candidates.json` `mechanics`):** a fish is an
ordinary ThingDef, `ParentName="FishBase"`, in `thingCategories: Fish`. The only
binding is `BiomeDef.fishTypes` — four buckets (`freshwater_Common/Uncommon`,
`saltwater_Common/Uncommon`, `{defName: weight}`), plus `rareCatchesSetMaker` and
`maxFishPopulation`. Fresh vs salt is chosen **per cell by the TerrainDef's
`waterBodyType`**; there is no per-fish water field and no per-terrain species
scoping inside a biome. So each water below is one table, and "lives in the seep
mouth" / "hangs from the roof" is flavor and art, never a spawn rule.

**Engine, read (RimSage, 2026-09-10 evening — `FishChance`, `WaterBody.SetFishTypes`,
`FishingUtility.GetCatchesFor`, `ThingMaker.MakeThing`):** a bucket entry is
`FishChance {fishDef: ThingDef, chance}`; each water body rolls one def per bucket
at map start; the catch is `ThingMaker.MakeThing(def)` with `stackCount` set —
**no guard anywhere on `category` or `thingCategories`.** A creature's *race*
ThingDef in a bucket therefore yields a bare `Pawn` from `Activator.CreateInstance`
with no kindDef and a stack count: not a creature, not a fish, and nothing logs it
at load. 🔴 **Law for every table here: a `fishTypes` entry is an item def
(`FishBase` lineage), never a race def.** A species that is both seen and netted
(the scalefish, the bladderboil) is TWO defs — the pawn on `wildAnimals`, the
catch item on `fishTypes` — and the engine never links them; the fiction does.

**Anti-exponential (standing, `RSW_SandSwimmer_Items.xml` header):** Nutrition and
MarketValue at or below vanilla `FishBase` (Nutrition 0.25, MarketValue 6.5, Mass
0.5, rot 2 days). Richness is in *kinds*, never in yield. The population cap stays
on the biome side (`maxFishPopulation`).

**Recognizability (owner, 2026-09-05):** if a player can name what it is meant to
be, it is cut. The registers do most of this work — a floater or a cucumber has no
Earth silhouette to fall into. The one exception is the **shoal** register, which
is allowed to look like a fish because the Naboo scalefish (mee/faa/laa) are canon
Star Wars fish and already ours.

**Names — two registers, both grounded:**
- **Water names are soft.** Canon Star Wars water-life is vowel-led and worn
  smooth: *mee, faa, laa, opee, colo, sando, yobshrimp*. Everything soft-bodied,
  drifting or schooling below takes that register: `ullo`, `niim`, `saal`, `veen`.
- **Armour takes the land roots.** Anything chitinous, plated or predatory takes
  `Alien_Bestiary.md` §1's clade roots — `karr-`/`-rrik` chitin, `vh-`/`kr-` apex,
  `-ik`/`-ek` small-quick — so a player who has met a `mirrik` over the pools
  knows a `tarrik` in them is kin: `tarrik`, `karrun`, `karrash`, `vhessa`.
- The name never describes the mechanic; the nickname carries the warning.
  Every entry gives both. Collision-checked against `creature_names_ashkarr.md`,
  `Alien_Bestiary.md`, `sea_beasts_roster.md` and the biome sheets (§7 records the
  sweep).

**Tier:** every def here is endemic to a named Ash'karr water, so all are
campaign-tier — `RUT_` prefix, packageId under `mandrake.rut.*`
(`design/NAMING_SCHEME_PLAN.md` §1/§2). The three Naboo scalefish stay `RSW_`;
they are canon, not ours.

**Art:** every entry is owed a sprite (`generating-rimworld-sprites`, a later
wave). The build may land with the SandSwimmer placeholder convention — reuse a
sprite physically present in the mod's own `Textures/` — but ⚑ no placeholder may
be a fish silhouette, and none may be shared by two species in the same table
(the player must be able to tell the catch apart in the stockpile).

**Stat direction by register** (the build item picks exact numbers; these are the
deltas from `FishBase` each register carries so the stockpile reads as varied):

| register | nutrition | market | mass | rot | notes |
|---|---|---|---|---|---|
| shoal | 0.25 | 6.5 | 0.5 | 2 d | the baseline; the "ordinary" catch |
| crustacean | 0.20 | 7 | 0.6 | 3 d | shell keeps; heavier to haul |
| squid | 0.25 | 6 | 0.4 | 1.5 d | spoils fast; some carry ink (a prize item, not a stat) |
| octopus | 0.25 | 8 | 0.5 | 2 d | uncommon tier by default — clever things are scarce |
| eel | 0.25 | 6.5 | 0.5 | 2 d | baseline stats, wrong shape |
| floater | 0.10 | 3 | 0.2 | 1 d | thin food, common filler, the signature silhouette of its water |
| jellyfish | 0.08 | 4 | 0.3 | 1 d | `FoodPoisonChanceFixedHuman` 0.05 raw; cook it |
| cucumber | 0.20 | 5 | 0.5 | 4 d | leathery, keeps, nobody's favourite |

---

## 1. Register coverage — the plethora, at a glance

| water (live def · buckets) | shoal | squid | octopus | eel | crustacean | floater | jellyfish | cucumber | new | + existing |
|---|---|---|---|---|---|---|---|---|---|---|
| Weeping Stones (`ZBiome_DesertOasis` · fresh) | — | — | vobbal | ozhu | tarrik | ikkal | ullo | duul | **6** | swfish_ ×4 → retire |
| Cracked Lands (`ZBiome_Badlands` · fresh) | — | vhessa | — | zhurr | — | tubbik | — | hurrok | **4** | RSW_DuneCrawler, BMT ×2 stay |
| Greentide (`BiomeCypreJungle` · fresh) | (mee/faa/laa **catch items**, owed — §2C) | zeev | tuun | lozh | karrun | uvva | saava | dubbol | **7** | RSW_Mee/Faa/Laa creatures stay on `wildAnimals`; +3 catch items |
| Twilight Deep (`RUT_TwilightSea` · salt, HELD) | **niim** | kellu | oobo | murrol | tikkarr | pallu | hollu | nuudal | **8** | — |
| The Scald (`RUT_TheScald` · UNMEASURED) | **eesh** | — | — | — | karrash | (bladderboil catch — sibling doc, §2E) | saal | muddal | **4** | — |
| Rust Cathedral (`AB_MechanoidIntrusion` · canals) | — | — | — | **veen** | — | — | — | — | **1** | — (ruling: the eels alone) |
| Wasteland brine (`Wasteland` · salt) | — | — | — | — | tekk | — | — | **drazz** | **2** | — |
| | | | | | | | | | **32** | |

Bold = one of the four owed defs. Every register the owner named appears in at
least three waters; every fished water gets at least four kinds except where a
ruling caps it (the Cathedral) or the chemistry does (the Wasteland).

---

## 2. The waters — species, tables, flavor

Weights follow the vanilla convention: the *bucket* carries the rarity tier, the
weight is a mild lean inside it. Each water lists its table first, then the
entries. Descriptions are written as the in-game `description` — campaign voice,
one nickname each.

### 2A. The Weeping Stones — the truce pools (`ZBiome_DesertOasis`)

Standing fresh water, seep-fed from below and vent-warmed, mineral-tasting; the
pools are breeding, ritual and romance grounds under the truce (`weeping_stones.md`
§4). Hard constraints carried: **nothing pollution-flavored, nothing that makes
the pool a hunting story** (§6, §10). Every native carries the comb (§5). The
`mirrik` dew-smoke falls into these pools every wind-hour, and that is the whole
food web's top-up.

| bucket | contents |
|---|---|
| `freshwater_Common` | RUT_Ikkal 1.2 · RUT_Tarrik 1 · RUT_Duul 0.8 |
| `freshwater_Uncommon` | RUT_Ullo 1 · RUT_Ozhu 0.8 · RUT_Vobbal 0.5 |
| `rareCatchesSetMaker` | **RUT_RareOasisCatches** (§2A.rare) |
| `maxFishPopulation` | donor default stands (UNMEASURED here; the build reads it) |
| retires | `swfish_Burra/Daggert/Nyork/See` — out of the table, mod untouched; they were the v1 placeholder by ruling (§5.4 of the fish proposal) |

**ikkal** — floater, common. *dew-cup.*
> A palm-wide bladder that hangs at the surface with a comb of fringe trailing
> below it, sieving the dew-smoke out of the water as it falls. At wind-hour the
> whole pool is dimpled with them, tilted to the same side like cups set out. It
> has no fight in it; a child can lift one out. Thin eating, and nobody minds —
> pilgrims cook them for the broth, which tastes faintly of the stones.

Mechanism: baseline floater. Nothing else — it is the common catch and the pool's
first signature.

**tarrik** — crustacean, common. *comb-shrimp.*
> A thumb-length shrimp-thing with antennae grown into two fine combs that it
> holds up into the current and licks clean. Kin to the mirrik above the water,
> and it shows: the same chitin, the same fringed silhouette, the same habit of
> mist-dancing at wind-hour, only underwater. It breeds in the shallows during the
> truce, in the open, in crowds — which is why nobody who has sat at a pool at
> dusk can eat one without a small pang.

Mechanism: crustacean stats. Shares the `-rrik` root with the mirrik deliberately.

**duul** — cucumber, common. *the janitor.*
> A slow grey sock of a thing that lies on the pool floor and eats what settles —
> silt, dung, dead dew-smoke, the ash blown in from the desert. A pool with duul
> in it stays clear; a pool without them clouds in a season. Every oasis keeper
> knows the count. It is edible in the sense that most things are.

Mechanism: cucumber stats, the lowest market value in the table. ⚑ Flavor only —
no clarity mechanic proposed.

**ullo** — jellyfish, uncommon. *the wedding bell.*
> A soft bell the size of two cupped hands, near-invisible by day, that lights a
> slow blue pulse from dusk. Ullo rise together and drift as a lit crowd while the
> fan-dancers display on the bank; the pools are places of romance and the ullo
> have never been told otherwise. Netted, it is a sting and a disappointment —
> mostly water, a little meat, and the light goes out in your hands.

Mechanism: jellyfish stats. ⚑ Optional later: a small mood thought on catching
one (the way the truce flavour runs) — NOT proposed for v1.

**ozhu** — eel, uncommon. *spring-throat.*
> A blind, comb-gilled eel that lives in the warm throat of the seep itself, down
> where the spring comes up through the stones. It surfaces at wind-hour to feed
> on the fallen dew-smoke and goes back down. Warm to the touch when landed, and
> it stays warm for a while, which unsettles people. The oldest pools have the
> longest ozhu; oasis-keepers claim they can taste which spring one came from.

Mechanism: eel stats. `-zh` is the sibilant root — reptile-adjacent, right for a
warm-water burrower.

**vobbal** — octopus, uncommon (weight 0.5). *stone-stacker.*
> Eight soft arms and a bulb of a body, living in the hollows where the seep
> water enters the pool. It takes things. Pebbles, offerings, a dropped tool, a
> ring — and it stacks them, carefully, in towers in the shallows, and knocks them
> down, and stacks them again. Some oases forbid catching them; most simply
> don't. The ones who do eat them say it is very good, in a voice that suggests
> they would rather not have.

Mechanism: octopus stats, deliberately scarce. Its stacking is the rare-catch
table's fiction (below); no C#.

**§2A.rare — RUT_RareOasisCatches** (ParentName `RareFishingCatchesBase`, two
options, thin on purpose): (weight 4) **RUT_SeepStone** ×1–2 — a mineral
concretion grown in the spring throat, *the* Stones beneath the oasis in
miniature, sold as ExoticMisc (MarketValue ~30, Beauty 3; the oasis sibling of
`RSW_GlassPearl`); (weight 1) a **vobbal tower** — `ThingSetMaker_StackCount` on
`Silver` 8–20, "somebody's offering, stacked and re-stacked for a decade." ⛔ No
corpses in this table — the pool is never a hunting story.

### 2B. The Cracked Lands — the lethal water (`ZBiome_Badlands`)

One freshwater table serves both the 27 slot-canyon water tiles and the
`RM_DeepSand` pools (ratified merge, `_fish_assignment_proposal.md` §2). No truce:
sightlines are gone under the roof, and the kill happens at the water. The fauna
divides by TIME — the Sealed, the Spenders, the Patient (`the_cracked_lands.md`
§10). The table below is the water's version of those three sorts.

| bucket | contents (ratified entries in plain text, new in bold) |
|---|---|
| `freshwater_Common` | RSW_DuneCrawler 1 · **RUT_Tubbik 1** · **RUT_Zhurr 0.6** |
| `freshwater_Uncommon` | BMT_Rocktooth 1 · BMT_Boneblade 1 · **RUT_Hurrok 0.8** · **RUT_Vhessa 0.4** |
| `rareCatchesSetMaker` | `RSW_RareSandCatches` stands, **+1 option** (below) |
| `maxFishPopulation` | 90 stands (the committed first-pass cut) |

⚑ The BMT pair stays as ratified this morning; the day their art fails the
recognizability look, hurrok and vhessa are already in the bucket to carry it.

**tubbik** — floater, common. *flood-fry.*
> A Spender. A pea-sized gas-bladder animal that exists for the flood-weeks and
> nothing else: the first rise lifts a billion of them out of the clay, they
> feed, they breed, they die, and the carpet of them on the falling water is what
> the fliers commute in for. Between floods the water holds only stragglers.
> Cooked in a mass it is a paste; the Farmers call it flood-bread and are not
> joking.

Mechanism: floater stats. ⚑ The engine has no season hook in `fishTypes`; the
flood-timing is flavor plus whatever `EXPLOSIVE_PLANT_GROWTH_1`'s event layer can
later drive (a `maxFishPopulation` bump during a flood event is the natural hook,
not proposed here).

**zhurr** — eel, common (0.6). *pan-sleeper.*
> A Sealed one. For the dry years it lies in a wax-lined cell under the cracked
> pan, banked to almost nothing — you have walked on thousands. Water wakes it;
> it rises through the softened clay into the canyon pools, feeds, breeds, and
> seals itself down again before the pan cracks. Its shed cell-lining is the
> crack-wax the Farmers trade. Landed, it is cool and dry and does not struggle,
> as if it has already decided to wait this out too.

Mechanism: eel stats. Crack-wax stays `the_cracked_lands.md` §11's item; ⚑ a
butcher-product link is NOT proposed (fish are not butchered).

**hurrok** — cucumber, uncommon. *crack-tongue.*
> A Patient one. A ridged, rubbery, arm-long thing that wedges itself into the
> seep-cracks where the hidden water is and lies there, year-round, filtering. The
> shade-line's browsers step over it. It is armored where it faces the canyon and
> soft where it faces the rock, and it does not come out — you catch one by
> catching the crack it lives in. Chewy. The name is the sound it makes when
> pulled.

Mechanism: cucumber stats.

**vhessa** — squid, uncommon (0.4). *the wall.*
> A Patient one, and the reason the canyon water has no truce. A pale slot-canyon
> squid that hangs in the roofed water with its arms laid flat along the rock wall
> like roots, invisible, and takes what comes down to drink. It has no need to
> hurry. Landed, it is mostly arm, and the arms keep working for a while. The
> Farmers say you have not caught one — it has let go of the wall to see what you
> are.

Mechanism: squid stats, `vh-` apex root. Scarce on purpose; the water's threat
is otherwise carried by the `RSW_SandStalker` corpse in the rare table.

**§2B.rare addition:** one option appended to `RSW_RareSandCatches` — (weight 1)
**RUT_Vhessa ×2–3** as a stack: "the wall let go all at once." Keeps the table
at three options; the glass pearl stays the headline.

### 2C. The Greentide — the living river (`BiomeCypreJungle`)

The planet's one *lush* water: explosive growth, fruit that yearns to be eaten,
churnmud that swallows things, root causeways, and the Lungers — huge submerged
predators for whom crossing water is the scariest routine act in the biome
(`the_greentide.md` §4, §8b). Ratified: mee 0.4 common, faa/laa 0.3 uncommon,
`maxFishPopulation` 720 — the scalefish stay and the commission builds the rest of
the river around them. This is the fresh water the owner's "plethora" most
obviously wants.

🔴 **Finding (evening pass):** the ratified weights stand, but the live patch
`src/RimUtinni/UtinniPatches/Patches/BiomeFishTypes_Greentide.xml` (closed under
`FISH_TYPES_PATCH_BUILD_1`, `689195d3`) puts `RSW_Mee`/`RSW_Faa`/`RSW_Laa` in the
buckets — and those defNames are the **race** defs
(`SeaBeasts_Scalefish.xml`, `ParentName="AnimalThingBase"` with a `PawnKindDef` of
the same name). The census (`_fish_candidates.json`) called RSW_Faa/RSW_Laa
"migrations of swfish_Faa/swfish_Laa"; they are not — the race carries
`specificMeatDef swfish_Faa`/`swfish_Laa` (Mlie's items, `MayRequire`), and RSW_Mee
has no item at all. Per §0's engine read, a net in this river makes a bare `Pawn`
with a stack count. Engine-read, not live-tested: the quicktest fishing pass (§5.4)
proves or disproves it, but the patch names race defs either way and must not.
So the table names three **catch items**, ⚑ `RSW_MeeCatch` / `RSW_FaaCatch` /
`RSW_LaaCatch` (RSW_ because the scalefish are canon; the `-Catch` suffix is the
bladderboil precedent, `RUT_BladderboilCatch`) — shoal register, vanilla `FishBase`
stats, laa at MarketValue 9 as the prized one; art is the scalefish mockup at
item scale. The alternative — Mlie's `swfish_Faa`/`swfish_Laa` under `MayRequire`,
no mee — is §6.7's other option.

| bucket | contents |
|---|---|
| `freshwater_Common` | **RSW_MeeCatch 0.4** · **RUT_Zeev 0.4** · **RUT_Uvva 0.3** · **RUT_Karrun 0.3** · **RUT_Dubbol 0.2** |
| `freshwater_Uncommon` | **RSW_FaaCatch 0.3** · **RSW_LaaCatch 0.3** · **RUT_Lozh 0.3** · **RUT_Saava 0.25** · **RUT_Tuun 0.15** |
| `rareCatchesSetMaker` | **RUT_RareGreentideCatches** (§2C.rare) |
| `maxFishPopulation` | 720 stands |
| creatures, untouched | `RSW_Mee`/`RSW_Faa`/`RSW_Laa` stay on `wildAnimals` (`BiomeCast_Ashkarr.xml`, `RUT_Miasma.xml`) — the dual-placement ruling is honoured with the right def on each side |

**zeev** — squid, common. *jet.*
> A hand-long river squid, green-gold, that lives in the fast clean reaches and
> moves the way the river does — one hard pulse and gone. Shoals of them ride the
> current down through the root causeways and pulse back up at night. Fast to
> catch, faster to spoil; the Wildsteam eat them off the line. Its ink is nothing
> special. Its cousin's is.

Mechanism: squid stats. The "cousin" is the Twilight kellu (§2D).

**uvva** — floater, common. *fruit-drunk.*
> A bladder-bodied grazer that hangs under the surface with its mouth open,
> waiting for the fruit-fall. When a giant drops its crop the uvva rise in a
> crowd and gorge — and the fruit's accelerants work on them as on everything, so
> a fed uvva bloats, spins slowly, passes seed downstream and starts again. The
> river's seed-carrier. Sweet, faintly fizzy, and it does the same to you.

Mechanism: floater stats. ⚑ Optional: the `ingestible` carries the fruit's own
digestive-accelerant hediff if `EXPLOSIVE_PLANT_GROWTH_1` ships one — v1 flavor.

**karrun** — crustacean, common. *churn-crab.*
> A flat, wide, root-brown crab-thing that lives in the churnmud between the
> giants, walking on the same swallowed things the mud hides — and it *finds*
> them. A dropped tool, a lost boot, a coin: the karrun carries it about for a
> while for reasons of its own. Line-fishers along the causeways pull them up
> holding things. The claws are the eating; the rest is mud.

Mechanism: crustacean stats, `karr-` chitin root. The rare table (below) is where
"holding things" pays out.

**dubbol** — cucumber, common (0.2). *the sweeper.*
> The Greentide is carpeted in filth and sprouts, and this is what eats the
> filth. A thick, warty, arm-long sweeper of the river floor, moving through the
> settled muck below the causeways at the pace of a thing that has never been
> chased. Where the dubbol are thick the water runs clean enough to drink,
> nearly. The Wildsteam plant them in their channels the way a farmer plants a
> hedge. Leathery, and it keeps.

Mechanism: cucumber stats. ⚑ Flavor only.

**lozh** — eel, uncommon. *root-eel.*
> Lives inside the drowned root causeways, in the channels the roots leave when
> they rot from within — an eel the colour of wet bark, thick as a wrist, that
> hunts along the root-roads at night and ambushes from the same holes travelers
> step over by day. It is why the causeways are contested by everything that
> prefers dry footing, and why nobody sleeps with a hand in the water.

Mechanism: eel stats.

**saava** — jellyfish, uncommon. *the roil-veil.*
> A wide, thin, freshwater bell that rides the Roil — the steam-fog over the
> river — half in the water and half in the air, trailing stinging threads a
> body-length down. Under the fog you cannot see them; you feel them. Not lethal.
> Memorable. A dozen drying on a line is a Wildsteam camp's fly-screen.

Mechanism: jellyfish stats; raw poison chance 0.05.

**tuun** — octopus, uncommon (0.15). *root-thief.*
> The water's Swinger. A small, quick, bark-mottled octopus that climbs the root
> causeways *out of the water* to reach the fruit-fall, and has been seen on the
> lower boughs. It steals. Lines, bait, small bright things, a fisher's whole
> catch left on the bank. Rare on the hook because it is usually the one holding
> the hook. Good eating, if you can find it.

Mechanism: octopus stats, the scarcest common-water catch on the planet.

**§2C.rare — RUT_RareGreentideCatches** (ParentName `RareFishingCatchesBase`,
three options): (weight 4) **RUT_LungerFry** ×1 — a fish item, not a creature:
"a Lunger no longer than your arm, which means its mother is under this bank;
eat it now, before it eats you next year" — shoal stats, MarketValue 12, the
Greentide's one prize fish; (weight 2) **a karrun's find** — `ThingSetMaker_StackCount`
on `ComponentIndustrial` ×1, the churnmud giving back what it swallowed; (weight 1)
`RSW_LaaCatch` ×3–4 — "fruit-fat, a whole family at once." No corpses; the Lungers
themselves are creature defs owed to the Greentide roster, not this table.

### 2D. The Twilight Deep — under the roof (`RUT_TwilightSea` · saltwater · HELD)

The only ordinary fishing on the planet: nets in the light columns under the
mat-roof, kelp forests, the ceiling gardens dripping detritus, the mud channels,
the gardener tending the roof, one fast ordinary predator, and the ruling that
here the roster populates *generously* — "yes, and another" (`the_twilight_deep.md`
§4, §7). The surface above the roof is ruled no-fish (`the_twilight_sea.json`),
and 🔴 **the live def is one BiomeDef for surface and deep** (`_def_bindings`
row 25). So: **the eight defs land now; the `fishTypes` binding is HELD** until the
under-roof water is separable (its own def or the diving-mods map layer). Until
then the patch ships under `DEPLOY_HOLD.txt` with this paragraph as its reason.
Brine water → the **saltwater** buckets.

| bucket | contents |
|---|---|
| `saltwater_Common` | **RUT_Niim 1.5** · **RUT_Pallu 1** · **RUT_Tikkarr 0.8** · **RUT_Nuudal 0.6** |
| `saltwater_Uncommon` | **RUT_Kellu 1** · **RUT_Murrol 0.8** · **RUT_Hollu 0.8** · **RUT_Oobo 0.4** |
| `rareCatchesSetMaker` | **RUT_RareTwilightCatches** (§2D.rare) |
| `maxFishPopulation` | ⚑ high — this is the fishing economy; the build sets it against the Greentide's 720 as the ceiling, not above it |

**niim** — shoal, common (1.5). *the silver.* — **Owed def; full spec §4.4.**

**pallu** — floater, common. *sun-cup.*
> A saucer-sized floater that lives only in the light columns, holding a green
> symbiont mat on its upper skin to the skylight like a face turned to the sun.
> A bright column is *crowded* with them, stacked in the water at every depth the
> light reaches, and a column the gardener lets close goes dark and the pallu
> sink out of it in a slow rain. The Compact counts them to price a skylight.
> Thin, green, slightly sweet.

Mechanism: floater stats. ⚑ The skylight-rights link is flavor; the Compact's
metering is `the_twilight_deep.md` §7's own mechanism.

**tikkarr** — crustacean, common. *kelp-cutter.*
> A long-legged, kelp-coloured crab-thing that lives up in the kelp forest, not
> on the floor — clinging, cutting, carrying fronds down to its holes. It is the
> sea-farm's pest and its pollinator both; cut kelp plots without tikkarr in them
> grow back slow. Armored, a good meal in the legs, and fond of nets.

Mechanism: crustacean stats, `-karr-` chitin root.

**nuudal** — cucumber, common (0.6). *the rain-eater.*
> The ceiling gardens shed a constant detritus rain, and the floor is nuudal:
> long, soft, mottled, moving through the fall like cattle through a snowfall,
> eating it. The richest ground in the sea is the mud under a busy skylight, and
> nuudal are what turn it over. Every net in the columns comes up with a few.
> Filling, and nobody has ever asked for seconds.

Mechanism: cucumber stats.

**kellu** — squid, uncommon. *lamp-black.*
> The kelp squid: arm-long, forest-dark, hiding in the fronds by day and hunting
> the shoals in the dark between columns by night. Its ink is the thing — thick,
> lightfast, black as the Grey. The Compact's charts are drawn in it, and it is
> the black in every dye-house that trades with the deep. A kellu on the line is
> half a catch and half an inkwell.

Mechanism: squid stats; the ink is **RUT_LampBlack** in the rare table, not a
butcher product.

**murrol** — eel, uncommon. *the fat slow thing.*
> The mud channels' river-fauna made specific: a thick, blunt, near-blind eel that
> rides the invisible current along the channel banks, mouth open, fat on the
> nutrient-fed silt, so slow that bank-harvesters pick them up by hand. The
> deep's comfort food. Nothing about it is difficult, and the Compact's dock
> kitchens serve nothing else on a bad day.

Mechanism: eel stats.

**hollu** — jellyfish, uncommon. *roof-drip.*
> A bell that forms on the underside of the mat, in the ceiling gardens, and lets
> go — falling slowly through the whole column, pulsing, stinging what it passes,
> to lie on the floor and be eaten by nuudal. A big garden sheds them all night.
> Divers learn the fall pattern of their skylight the way farmers learn rain.
> Netted mid-fall it is a sting and a bell of salt water; cooked, it is a
> delicacy in exactly one dock.

Mechanism: jellyfish stats; raw poison chance 0.05.

**oobo** — octopus, uncommon (0.4). *drop-hand.*
> Lives in the ceiling gardens, hanging from the roof among the filter-feeders,
> and hunts by letting go — a soft, wide-armed drop through the dark onto whatever
> is below, and a slow climb back up a kelp stem. The gardener tolerates it; the
> oobo groom the roof-underside as they go. Divers hate it with the specific
> hatred of people who have had one land on them. Very good eating.

Mechanism: octopus stats.

**§2D.rare — RUT_RareTwilightCatches** (ParentName `RareFishingCatchesBase`,
three options): (weight 4) **RUT_LampBlack** ×1–2 — kellu ink, a dye-and-chart
resource, ExoticMisc, MarketValue ~24, "the black the Compact draws its world in";
(weight 2) `RUT_Niim` ×8–12 — a net that hit the shoal; (weight 1) **`RSW_ColoClawFish`
corpse** (5–10 days) — the one true predator, reserved for this water by the
fish proposal §1 row 5: "something in the dark between columns had already
finished with it."

### 2E. The Scald — the margin harvest (`RUT_TheScald`)

Boiling, fouled mineral brine, never potable (ban 1); bottom-walker herds mow the
thermophile mats and their dung is the water column's whole budget; the silver
shoals work the dung-fall; the bubble-sailors ride the boil (`the_scald.md` §4).
"The silver harvest — margin-fishing in water that burns and comforts in the same
step" (§7). Ruling: fish **analogs only**, nothing existing survives the water.
⚑ Which buckets apply is **UNMEASURED** — the crater terrain's `waterBodyType`
decides it and nobody has read it; the build starts there. The burn at the
margin is `SCALD_MECHANICS_1`'s, not this table's.

| bucket (fresh or salt per the terrain read) | contents |
|---|---|
| `_Common` | **RUT_Eesh 1.5** · **RUT_Muddal 0.8** |
| `_Uncommon` | **RUT_Karrash 1** · **RUT_Saal 0.5** · `RUT_BladderboilCatch` 0.5 (sibling doc, below) |
| `rareCatchesSetMaker` | **RUT_RareScaldCatches** (§2E.rare) |
| `maxFishPopulation` | ⚑ low — a margin harvest, a third of the Cracked Lands' 90 in spirit |

**Fifth line, from a sibling commission:** `RUT_BladderboilCatch` — the kettle-jelly
of `creatures/RUT_hydrocarbon_ecology_commission.md` §10c, a floater-register catch
item (nutrition 0.10, market 3, this doc's §0 envelope) paired with its own
`wildAnimals` pawn, two defs by that doc's design. It is specified THERE and only
*placed* here; this table does not re-describe it. ⚑ Bucket and weight are that
doc's proposal (uncommon); §6.8 asks whether it rides this build or its own.

**eesh** — shoal, common (1.5). *the silver.* — **Owed def; full spec §4.1.**

**muddal** — cucumber, common. *mat-mouse.*
> The bottom-walkers' small cousin: a hand-long, armored, heat-glossed thing that
> grazes the welcome blankets at the margins where the boil gentles, moving along
> the rainbow bands and taking the pigment into its skin, so a muddal is banded
> too — a little strip of the Scald's oldest truth. Pilgrims gather them at the
> baths with a cloth. Cooked the moment it leaves the water, which is to say
> already.

Mechanism: cucumber stats. ⚑ `preferability RawTasty` — it comes up cooked; the
one register-break in this doc, justified by the water.

**karrash** — crustacean, uncommon. *vent-crab.*
> Lives on the vent chimneys themselves, in the hottest water anything survives,
> plated in mineral crust it grows from the brine — a crab-thing that looks like
> a piece of the vent walked off. It eats the mat where the mat is thickest and is
> eaten by nothing, because nothing else goes there. Landed, the crust cracks off
> as it cools and the meat inside is white and sweet. The shells are sold as
> rim-pilgrim keepsakes.

Mechanism: crustacean stats, `karr-` root, MarketValue at the top of its band.

**saal** — jellyfish, uncommon (0.5). *the sailor.*
> The bubble-sailor, netted: a bell no bigger than a fist with a single stiff
> sail-vane that it sets into the trailing lines of boiling bubbles and rides —
> up the vent columns, drifting down, riding again. The Scald's kindest resident
> and its signature silhouette; pilgrims read their traffic the way sailors read
> gulls. Nobody fishes for them on purpose. One in a margin-net is let go more
> often than not, and the margin-net that keeps one is not spoken of.

Mechanism: jellyfish stats. This is the *item* face of the roster's bubble-sailor
creature (`the_scald.json` new_defs): the creature def (C# bubble-line locomotion,
later) is unchanged and separate; the catch is the same animal, small.

**§2E.rare — RUT_RareScaldCatches** (ParentName `RareFishingCatchesBase`, two
options): (weight 3) **RUT_Karrash** ×2 — a chimney's worth; (weight 1)
**`Dye`-class rainbow pigment** ×2–4 — a scrap of welcome-blanket brought up with
the net; ⚑ uses whatever pigment product def the mats' own roster entry ships
(`the_scald.json` new_defs row 1); if none exists at build time this option is
omitted, not invented.

### 2F. The Rust Cathedral — the coolant canals (`AB_MechanoidIntrusion`)

The eight "river" tiles are coolant canals, circulating after all this time
(`the_rust_cathedral.md` §3). Ruling: *the canals' only life is the coolant eels*
(`the_rust_cathedral.json` fish) — the one table on the planet with one species,
and the commission does not reopen it. Fishing them is possible and deeply
inadvisable: the hum changes the moment a line goes in
(`RUST_CATHEDRAL_MECHANICS_1` owns that consequence).

| bucket (canal terrain's `waterBodyType` — fresh until `LIQUID_TYPES_MOD_1` says otherwise) | contents |
|---|---|
| `_Common` | **RUT_Veen 1** |
| `_Uncommon` | empty (explicitly, the sibling patches' safe-no-op pattern) |
| `rareCatchesSetMaker` | none — nothing else is in there |
| `maxFishPopulation` | ⚑ 20 — a closed loop's whole population; it does not restock the way a river does |

**veen** — eel, common. *coolant eel.* — **Owed def; full spec §4.2.**

### 2G. The Wasteland — the brine batteries (`Wasteland`)

Hypersaline pools over mineral beds, sealed dead-river termini — half a voltaic
cell; what lives in them runs on ion gradients and discharges them as defense.
"The pool you want to mine has an owner, and the owner is a capacitor"
(`wasteland.md` §4). Ruling: *no fish — nothing vertebrate lives here; the pools'
owners are the brine-battery archetype* — and the commission folds that
archetype in as its fishable members, both invertebrate. Brine → **saltwater**
buckets; ⚑ the pool terrain's `waterBodyType` is UNMEASURED and the build reads it.
`FISH_TYPES_PATCH_BUILD_1`'s strip (`689195d3`) may have emptied this def; this
table re-fills it deliberately.

| bucket | contents |
|---|---|
| `saltwater_Common` | **RUT_Tekk 1** |
| `saltwater_Uncommon` | **RUT_Drazz 1** |
| `rareCatchesSetMaker` | **RUT_RareBrineCatches** (§2G.rare) |
| `maxFishPopulation` | ⚑ 30 — three pools on the whole planet |

**tekk** — crustacean, common. *plate-scraper.*
> A salt-white, flat-bodied scraper the size of a thumb, living on the mineral
> beds under the brine and grazing the crust the drazz lay down. It carries a
> charge — a small one; picking one up bare-handed is a tingle and a lesson. They
> swarm on a carcass in the pool and strip it, and on a drazz that has spent its
> charge, which is how the pool's owner eventually dies. Edible after a long
> soak. The Junkers do not bother.

Mechanism: crustacean stats, `-ek` small-quick root. ⚑ No shock mechanic on the
item in v1; the tingle is the description's.

**drazz** — cucumber, uncommon. *the owner.* — **Owed def; full spec §4.3.**

**§2G.rare — RUT_RareBrineCatches** (ParentName `RareFishingCatchesBase`, two
options): (weight 3) **RUT_BrinePlate** ×1–2 — a drazz's spent electrode plate,
a stacked mineral wafer that still holds a whisper of charge; ExoticMisc,
MarketValue ~28, and ⚑ a recipe candidate (2 plates → 1 `ComponentIndustrial` at a
crafting spot) if the build wants the Wasteland's tipping-fee economy to have a
hook here — the recipe is optional, the item is not; (weight 1) **drowned cargo** —
`ThingSetMaker_StackCount` on `Steel` 10–25, the salt basins' "drowned cargo"
injection (`wasteland.md` §10) fished up a piece at a time.

---

## 3. Not reopened — the no-fish rulings stand

Every ruling in `_fish_assignment_proposal.md` §3 is untouched: the Grey Sea
(surface and deep), the Twilight *surface*, the Propane Lakes (creatures, never
fishTypes), the Contagion, the Rot, the Slime, the Scarlands, the Sump, the Fever
Wood, the Poison Forest, the Forsaken Crags, the Fall Line, the Lantern Deeps, and
every dry biome. The Miasma stays a fauna register (nursery juveniles as
`wildAnimals`, ruled) — ⚑ one note for the Greentide/Miasma dual-placement
precedent: `RUT_LungerFry` (§2C.rare) is a *fish item*, not a juvenile creature,
and does not touch that register. The 16-biome strip (`689195d3`) stands, with the
one deliberate re-fill in §2G.

**The sea-beast family is not duplicated.** The 18 `RSW_` creatures of
`sea_beasts_roster.md` (`SeaBeasts_Colo/Colossi/Opee/Sando/Scalefish/Swarm.xml`)
and the Miasma nursery juveniles (`RUT_MiasmaNurseryJuveniles.xml`, `4b1f5b71`) are
race defs on `wildAnimals` — the Grey Sea's fauna and the Miasma's nursery, both
ruled no-`fishTypes` waters. Nothing in this doc shares a def, a name or a water
with them: the swarm trio (pale yobshrimp, silt lamprey, rust nipper) are
creature-scale carcass-strippers of the brine; this doc's crustaceans and eels are
catch-scale and live in fresh or under-roof water. The kinship of register is
deliberate. The only two contacts are the ones already written: the scalefish catch
items (§2C) and the colo corpse in the Twilight rare table (§2D.rare — the vanilla
`RareFishingCatches_Hot` predator-corpse pattern, already used by
`RSW_RareSandCatches`).

---

## 4. The four owed defs — full specification

Each block is the complete ThingDef the build writes, in the field vocabulary of
`RSW_SandSwimmer_Items.xml` and vanilla `FishBase`. Numbers here are the proposal;
the stat-direction table (§0) is the envelope they were chosen inside.

### 4.1 The Scald thermophile shoal — `RUT_Eesh`

```
defName        RUT_Eesh          label  eesh          ParentName FishBase
register       shoal             water  RUT_TheScald, _Common bucket, weight 1.5
statBases      Nutrition 0.25 · MarketValue 6.5 · Mass 0.4 · MaxHitPoints 80 ·
               FoodPoisonChanceFixedHuman 0.0 · DeteriorationRate 3
ingestible     foodType Meat · preferability RawTasty (⚑ it comes up cooked) ·
               ingestEffect EatMeat · tasteThought none (no raw-food penalty)
comps          CompProperties_Rottable daysToRotStart 1 (cooked flesh; keeps worse)
stackLimit     25
graphicData    Graphic_StackCount · texPath RimUtinni/AshkarrWaters/Eesh (owed art:
               a finger-long silver sliver, heat-shimmer edge, NO fins drawn —
               a shoal-silhouette, not a fish-silhouette; placeholder must not
               be any fish sprite)
```
> The silver of the Scald. A finger-long, finless, mirror-skinned sliver that
> lives in the boiling column and feeds on the dung-fall of the herds below —
> clouds of them, darting, the water's whole budget in a single restless shape.
> It has no scales; the skin is a heat-mirror, and a shoal turning is a flash
> you can see from the rim. Netted at the margin it dies instantly and is
> already cooked, and it is the one thing on the crater that people call
> delicious without a caveat. "As always, there are." — pilgrims' saying, of the
> shoals and of most things.

Dependencies: `SCALD_MECHANICS_1` (the burn at the margin — fishing here should
cost); `RUT_TheScald`'s water terrain `waterBodyType` (UNMEASURED; picks the
bucket). Lands as an item with no C#.

### 4.2 The Cathedral coolant eel — `RUT_Veen`

```
defName        RUT_Veen          label  veen          ParentName FishBase
register       eel               water  AB_MechanoidIntrusion canals, _Common, weight 1
statBases      Nutrition 0.20 · MarketValue 2 · Mass 0.5 · MaxHitPoints 80 ·
               FoodPoisonChanceFixedHuman 0.02 · Beauty -4 · DeteriorationRate 1
ingestible     foodType Meat · preferability RawBad · ingestEffect EatMeat ·
               tasteThought AteRawFood ·
               ⚑ outcomeDoers: HediffGiver → a small "coolant load" hediff
               (toxic-buildup-like, severity 0.08/serving, decays) — OPTIONAL,
               v1 may ship without it and say so in the description
comps          CompProperties_Rottable daysToRotStart 6 (it barely rots; the
               canal water is a preservative)
stackLimit     25
graphicData    Graphic_StackCount · texPath RimUtinni/AshkarrWaters/Veen (owed art:
               pale, eyeless, translucent — the ribbing of the spine visible
               through the skin; cold-blue cast)
```
> A coolant eel. Blind, pale, and cold to the touch, it has circled the
> Cathedral's closed loop for uncounted generations eating the microfouling —
> dead micromachines, scale, silt — and the filters were reconfigured, once, to
> let it pass. The machine keeps them: living maintenance for a cooling system
> whose purpose died unfinished, tended anyway. Fishing them is possible. The hum
> changes the moment a line goes in. Eating one is like eating a very old cold
> thought, and it sits in you.

Dependencies: `RUST_CATHEDRAL_MECHANICS_1` (canal-locked movement for the creature
face if one is ever built; the hum-mood consequence on fishing);
`LIQUID_TYPES_MOD_1` (if coolant becomes its own liquid, the bucket follows its
`waterBodyType`). One-species table by ruling; no rare catches. Lands as an item
with no C# — the hediff is the only optional C#-free extra and uses vanilla
`IngestionOutcomeDoer_GiveHediff`.

### 4.3 The Wasteland brine-battery — `RUT_Drazz`

```
defName        RUT_Drazz         label  drazz         ParentName FishBase
register       cucumber          water  Wasteland brine pools, saltwater_Uncommon, weight 1
statBases      Nutrition 0.15 · MarketValue 9 · Mass 0.8 · MaxHitPoints 100 ·
               FoodPoisonChanceFixedHuman 0.03 · Flammability 0 · DeteriorationRate 1
ingestible     foodType Meat · preferability RawBad · tasteThought AteRawFood ·
               ⚑ outcomeDoers: HediffGiver → "shock" (a short stun-class hediff,
               vanilla-shaped) on RAW ingestion only — OPTIONAL v1; cooking
               discharges it and the cooked product is ordinary
comps          CompProperties_Rottable daysToRotStart 5
stackLimit     10 (heavy, awkward)
tradeTags      ⚑ ExoticMisc in addition to Fish — traders who buy oddities want it
graphicData    Graphic_StackCount · texPath RimUtinni/AshkarrWaters/Drazz (owed art:
               a stacked-wafer body, salt-white plates alternating with dark
               mineral, a faint arc across the top plate — a battery that grew)
```
> The owner. A forearm-long, plated, sea-cucumber-shaped thing whose body is a
> stack of living electrode wafers, salt-white and mineral-dark by turns, lying
> on the bed of a hypersaline pool and running on the ion gradient between the
> brine and the metal beneath it. It discharges as defense. The pool you want
> to mine has one, and it is a capacitor, and it does not want you there. Landed
> — carefully, on a dry line, by people who have done it before — it goes on
> discharging for an hour. Cooked, it is meat. Raw, it is a lesson.

Dependencies: the pool terrain's `waterBodyType` (UNMEASURED); the Wasteland dose
layer is unrelated (the pools are the *conventional* poison of the war legacy,
not the radiological one — `wasteland.md` §0). `RUT_BrinePlate` (§2G.rare) is its
prize item and the archetype's economic hook. Lands as an item with no C#.

### 4.4 The Twilight shoal — `RUT_Niim`

```
defName        RUT_Niim          label  niim          ParentName FishBase
register       shoal             water  RUT_TwilightSea under-roof, saltwater_Common, weight 1.5 — HELD
statBases      vanilla FishBase verbatim (Nutrition 0.25 · MarketValue 6.5 · Mass 0.5)
ingestible     vanilla FishBase verbatim (RawBad, AteRawFood)
comps          vanilla FishBase verbatim (rot 2 d)
stackLimit     25
graphicData    Graphic_StackCount · texPath RimUtinni/AshkarrWaters/Niim (owed art:
               a scalefish-shaped silver fish with the Naboo dot-line — the ONE
               entry allowed to look like a fish, because scalefish are canon;
               a blue-white cast against the mee's silver-blue so the two never
               read as the same item)
```
> The silver of the Twilight — the shoal fish, the ordinary fish, the fish that
> behaves like a fish, and the only one on the planet that does. Blue-white,
> hand-long, a dot-line of cold light along the flank, it schools in the light
> columns under the roof in crowds that make the column *flash* when they turn.
> The Compact's whole under-roof economy is a net dropped into a niim column.
> Hunted by the kellu in the dark between columns and by one fast ordinary thing
> nobody has a good name for. Tastes like fish. That is the point of it.

Dependencies: 🔴 the surface/deep single-def problem (§2D) — the def lands, the
binding is HELD under `DEPLOY_HOLD.txt`; the diving-mods layer (deferred) or a
separate under-roof BiomeDef unblocks it. `RSW_ColoClawFish` stays the reserved
apex body (corpse in the rare table). Lands as an item with no C#.

---

## 5. What the build item does (sketch for the ratifying pass)

0. 🔴 **Repair before anything else**: `BiomeFishTypes_Greentide.xml` names race
   defs (§2C). Whether the deployed copy matches the repo copy is UNMEASURED from
   this seat; either way the fix is the three catch items (or §6.7's Mlie option)
   and a rewrite of the patch's three entries. It is a defect in a *closed* item —
   file it as its own item (⚑ `GREENTIDE_FISH_ITEMS_FIX_1`) so it can land before
   the full bestiary does, and so a quicktest fishing pass proves the §0 read.
1. **One new mod folder**, campaign tier: `src/RimUtinni/AshkarrWaters/`
   (packageId `mandrake.rut.ashkarrwaters`, display "RimUtinni: Ash'karr Waters"),
   holding `Defs/ThingDefs_Items/` (32 fish + 4 prizes, one file per water; the
   3 scalefish catch items go in `SWBestiary` beside their creatures, RSW_ tier),
   `Defs/ThingSetMakerDefs/` (6 tables), `Textures/RimUtinni/AshkarrWaters/`.
   ⚑ Alternative: fold into `UtinniPatches/Defs/` — a question for the owner
   (§6.3); a separate mod keeps the art wave and the deploy tool's unique-folder
   rule simple.
2. **Biome bindings** as patches in `UtinniPatches/Patches/` — one file per water,
   the existing `BiomeFishTypes_*.xml` conditional-replace shape, `MayRequire`
   on `mandrake.rut.ashkarrwaters` per entry: rewrite `BiomeFishTypes_Ashkarr.xml`
   (weeping stones, swfish_ out), edit `SandFishing_CrackedLands.xml` (+4, +1 rare
   option), edit `BiomeFishTypes_Greentide.xml` (+7, new rare table), new
   `BiomeFishTypes_Scald.xml`, `BiomeFishTypes_RustCathedral.xml`,
   `BiomeFishTypes_Wasteland.xml`, and `BiomeFishTypes_TwilightDeep.xml` under
   `DEPLOY_HOLD.txt`.
3. **Measure first**: the `waterBodyType` of the painted water terrain on
   `RUT_TheScald`, `Wasteland` and the Cathedral canals (UNMEASURED ×3 in this
   doc); whether `689195d3` emptied `Wasteland`; the donor's `maxFishPopulation`
   on `ZBiome_DesertOasis`. `design/Jawa/mods/gen_fish_types.py` generates from
   the census JSON — the build either extends the census with these defs or
   retires the generator for hand-written patches; ⚑ recommend the latter, the
   generator's input was a donor census and this is authored content.
4. **Validate**: `validate_patch.py` both `--live` and `--defs`; the
   PatchOperationConditional trap (matches nothing, logs nothing); a quicktest
   fishing pass on the minimal list, not a cold load.
5. **Art wave**, separate item: 36 sprites, `generating-rimworld-sprites`, with
   the placeholder rule from §0 in force until each lands.
6. **Roster JSON** `fish.list` rows for the seven waters, written by the build
   (this doc writes none), and `sea_beasts_roster.md` gains a one-line pointer to
   the Twilight table so the two registers do not drift.

---

## 6. Questions for the owner (cardable — free text overrides)

1. **Retire the `swfish_` four on the Weeping Stones** when the six RUT species
   land? (Proposed yes; they were the placeholder by ruling.) Or keep Burra/
   Daggert/Nyork/See alongside for a ten-species pool?
2. **The BMT pair on the Cracked Lands** — ratified this morning; keep them
   permanently, or treat them as the next placeholder, retired when hurrok/vhessa
   art passes the look?
3. **Mod shape** — a separate `AshkarrWaters` mod, or fold the defs into
   `UtinniPatches`?
4. **The two optional hediffs** (veen's coolant load, drazz's raw shock) — ship
   them in v1 or hold them?
5. **Names** — every one is an offer. The four you have already named in the
   sheets keep their nicknames (*coolant eel*, *the silver*, *the owner*, *the
   sailor*); the true names are mine.
6. **`RUT_LungerFry`** puts a Lunger on the Greentide table before the Lunger
   creature exists in the roster. Keep the fry now, or hold it until the
   Greentide roster names its Lunger?
7. **The scalefish catch items (§2C)** — (a) our own `RSW_MeeCatch`/`FaaCatch`/
   `LaaCatch`, three new item defs with the mockup art at item scale (proposed:
   the river's headline fish should not depend on a donor mod), or (b) Mlie's
   `swfish_Faa`/`swfish_Laa` under `MayRequire` and no mee catch at all, or (c) both
   — ours by default, Mlie's as the `MayRequire` fallback. And: does the repair
   ride this build or its own item (§5.0)?
8. **The bladderboil catch (§2E)** — accept the hydrocarbon commission's fifth
   Scald line at uncommon 0.5 as written there, and does it build with this mod
   or with that commission's own item?

---

## 7. Provenance

- Sources read: `rosters/_fish_assignment_proposal.md` (all five rulings honored),
  `rosters/*.json` `fish` rows for the seven waters, `sea_beasts_roster.md`,
  `Alien_Bestiary.md` §1, `creature_names_ashkarr.md`,
  `creature_recognizability_rule.md`, the seven biome sheets' §3/§4/§7/§10,
  `_def_bindings_2026-09-09.md`, `RSW_SandSwimmer_Items.xml`,
  `RSW_RareSandCatches.xml`, `SeaBeasts_Scalefish.xml`, vanilla
  `Items_Resource_Fish.xml`, the four `FISH_TYPES_PATCH_BUILD_1` commits.
- The four owed defs had prose but no spec anywhere in the repo (grep of
  "thermophile / coolant eel / brine-battery / twilight shoal" across `design/`,
  `src/`, `infrastructure/state/`): §4 is their first specification.
- Names: 32 candidates swept word-bounded across `design/`, `src/`, `skills/`,
  `infrastructure/state/`; two were changed before writing for real-canon
  collisions (*lekku*, *Ossus*). Three hits remain and are judged
  non-collisions, recorded so the owner can overrule: `tarrik` appears in a
  Nagai first-name pool, `ullo` in an Arkanian nickname pool (both
  `StarWarsRaces/Languages/.../RimMandrakeSWNames/`), `oobo` in a JawaVoice
  string (`JawaVoice_prisoners.xml`) — pawn-name and vocable pools, a different
  register from creature labels. Nothing here reuses a name from the land
  bestiary; shared roots (`-rrik`, `karr-`, `vh-`) are deliberate kinship.
- Evening reconciliation (second Fable pass, same day): read the six
  `SeaBeasts_*.xml` race files, `sea_beasts_roster.md`,
  `sea_beasts_family_review_grid_key.md`, `RUT_MiasmaNurseryJuveniles.xml` and
  the Miasma/Greentide `wildAnimals` wiring (`BiomeCast_Ashkarr.xml`,
  `RUT_Miasma.xml`); `creatures/RUT_hydrocarbon_ecology_commission.md` §10c (it
  cites this doc's Scald table and adds the bladderboil line — folded in, §2E);
  the four live `BiomeFishTypes_*`/`SandFishing_*` patches; the engine path
  `FishChance` → `WaterBody.SetFishTypes` → `FishingUtility.GetCatchesFor` →
  `ThingMaker.MakeThing` via RimSage (§0's second paragraph and §2C's finding).
  The 32 names re-swept against everything built tonight: no new collision
  (`vhessa`/`eesh` hits in the hydrocarbon doc are citations of this one).
- ⚑ marks an invented rule or an unmeasured assumption throughout; nothing
  marked ⚑ is presented as ruled.
