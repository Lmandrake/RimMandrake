# Weeping Stones — The Stocked Pool: pool-fish bestiary, husbandry loop, cuisine hooks

**Item:** `WEEPING_STONES_FISH_HUSBANDRY_1` · **Date:** 2026-09-24 · **Status:** DRAFT for owner review

**Owner ruling (typed 2026-09-24, binding):**
> "love it. Moisture farmers specializing in fish. Ripe possibilities for rimcuisine stuff too.
> Make the fish nasty and way too active. And some shouldn't be fish but alien beasts you
> really wonder if we should be eating."

Builds on: `weeping_stones_shine_options_2026-09-24.md` option 1 (greenlit by the ruling above),
the frozen sheet `weeping_stones.md`, the ruled fauna roster
`weeping_stones_fauna_roster_2026-09-24.md`, and the fish naming voice in
`design/Jawa/worldbuilding/fish_bestiary_commission_2026-09-10.md`.

Laws honored: Q11a (invented RM_ names, franchise-free, rich standalone); §6 ambush ban
(violence lives in the handling and the catch, never ambush-at-water); R21 (condensate
fiction, no rain); comb rule (silhouettes that break the surface); ecosystem pyramid.

## 0. What already stands — the two tables, reconciled

🔑 **The fish commission's Weeping Stones table is RULED and untouched here.**
`fish_bestiary_commission_2026-09-10.md` §2A specifies six gentle wild species
(`RUT_Ikkal/Tarrik/Duul/Ullo/Ozhu/Vobbal`) and its §6 rulings (owner, 2026-09-18)
retire the `swfish_` four when they land, with fish defs living in each biome's
own mod. That is the **wild catch** — what nature put in a pool nobody tends.

**This doc is the STOCKED line** — what moisture farmers breed on purpose, plus
what turns up in a pen whether they meant it or not. New rows are `RM_` tier
(invented, franchise-free, Q11a) inside the `RM_WeepingStones` mod, same subject
as the ruled fauna roster. `RM_Murrin` (fauna roster §2g) stays the gentle
baseline and its species selection stays owed to `FISH_BY_BIOME_1` — this doc
designs the mechanism around whatever that lane casts, per the greenlit option's
own validity floor.

**The two-def law binds every row** (commission §0, engine-read): a `fishTypes`
entry is an **item def** (`FishBase` lineage), never a race def — a race def in a
bucket yields a broken bare Pawn. A species that is both *seen in the pool* and
*netted from it* is TWO defs — pawn on `wildAnimals`/pen, catch item on the
table — and the fiction links them, the engine never does. The three beast rows
below are exactly that shape.

## 1. The fantasy

Everywhere else on this planet a moisture farmer's crop is water. Here, the
water has a crop of its own. A wild pool holds a thin wild stock; a *tended*
pool is stocked, fed, and read — the comb-fins cutting rings at wind-hour are
the pool telling you it is well, and a silent pool is the first word of trouble
before the green ring even starts to brown (§10b's dead-oasis image,
underwater). A colonist nets breeding stock at a strange oasis, carries it home
in a wet skin, and three seasons later their own water is alive.

And then the owner's amendment, which is the whole flavor of the profession:
**the stock does not want to be farmed.** The pool fish of the Weeping Stones
are nasty and way too active — they jump the pen walls at wind-hour, they bite
the hand on the feed schedule, they strip a wound to the bone if you wade in
bleeding, and the biggest of them eat the rest. A fish farmer here wears
handling leathers and counts fingers. And below the fish, in the same pens,
live the other catches — the ones that are *not* fish: soft warm things with
something like breath, things that learn your call and give it back, things
that watch you work with too many eyes and know the feed hour better than you
do. They are the best eating in the biome. Everyone says so. Nobody says it
comfortably.

The truce holds at the water (§4) — and the pen is not the truce. What happens
inside a stocked pool is husbandry, and husbandry here is a contact sport.
Violence lives in the handling and the catch, never in ambush at the margin
(§6): nothing below hunts the drinkers; everything below fights the farmer.

## 2. The bestiary — the stocked line

Eight rows: the gentle baseline (unchanged), four fish that earn the owner's
"nasty and way too active" in four different directions, and three catches that
are not fish at all. Names follow the commission's two registers — soft
vowel-led for water-soft things, land clade roots (`karr-`/`-rrik` chitin,
`vh-` apex, `-zh` sibilant, `-ik`/`-ek` small-quick) for anything armored or
predatory — and every name below extends the murrin's `-rrin` pool-kin root or
a sibling root deliberately. Every silhouette carries the comb (§5), and every
row's comb is what breaks the surface: the rings a farmer reads ARE comb-fins.

Pyramid: the baseline and the two small biters are common in a stocked pool;
the escaper and the beasts are uncommon; the tyrant is one per pool at most.

### 2.0 `RM_Murrin` — the baseline (UNCHANGED, fauna roster §2g)

The gentle hand-length pool fish, comb-fin cutting rings at wind-hour. Species
selection rides `FISH_BY_BIOME_1`; nothing here re-adjudicates it. In this
doc's economy it is the *telemetry species* (§3): murrin rings are the pool's
health gauge, and the nasty rows below are graded by what they do to a murrin
stock as much as to a farmer.

### 2a. `RM_Skarrin` — fish. *ring-breaker.*

| field | value |
|---|---|
| FORM | **deep-keeled fish, the murrin's comb-fin grown into an oversized blade, body held bent like a spring** |
| look | A forearm-long pool fish that spends as much time above the water as in it — at wind-hour a stocked pool *boils* with them, silver arcs snapping at the falling dew-smoke. |
| nastiness | **It jumps, and it bites what it lands on.** Clears a pen wall from standing water; a handler leaning over the pool takes a face-strike; escapes flop toward the next wet thing, which is sometimes the murrin pen. |
| catch method | Netted mid-air at wind-hour — the one catch you make *above* the water; a missed net is a bite. |
| food value + the doubt | Good ordinary fish-flesh, the stocked line's volume crop. No doubt at all — which is why farmers keep it despite everything. |
| commonality | common in stocked pools; thin in the wild |

### 2b. `RM_Karrek` — fish (chitin-finned). *flenser.*

| field | value |
|---|---|
| FORM | **finger-length, fin-rays hardened into serrated chitin combs — a swarm silhouette, never single** |
| look | The tarrik and mirrik's ugliest cousin (`karr-` root, deliberate kinship): a boiling crowd of little armored fish that hit thrown feed like one animal and leave nothing. |
| nastiness | **It bites everything, together.** Feed-throwing is safe; wading is not — a karrek swarm strips a bleeding cut white in seconds. Handlers bandage BEFORE tending this pen. Left hungry two days, the swarm starts on its own smallest. |
| catch method | Basket-trap on a feed lure — never a line, never bare hands. |
| food value + the doubt | Individually nothing, rendered by the basketful into a rich paste that keeps (§4). Doubt-free, handler-hostile. |
| commonality | common; the default second species in any working pool |

### 2c. `RM_Vizhik` — eel-fish. *pot-eel; the walker.*

| field | value |
|---|---|
| FORM | **wrist-thin eel, comb-gills fanned along the whole neck like a ruff** |
| look | Kin to the wild ozhu (`-zh` sibilant root) but cold, quick, and never where you left it. Its comb-gills let it breathe the weep-film itself. |
| nastiness | **It leaves.** At wind-hour, when every stone face runs wet, a vizhik pours itself out of the pen and crosses open rock on its gill-comb — into the next pool, the cistern, the water barrel, the kitchen stock-pot. Its bite is small and goes septic more often than it should. |
| catch method | You don't catch it in the pool; you catch it *traveling* — pick it off wet stone at wind-hour, gloved. |
| food value + the doubt | Excellent, and the pens keep breeding it because it keeps arriving on its own. The mild doubt is where it's been: nobody eats a vizhik pulled from the cistern without thinking about the cistern. |
| commonality | uncommon; every developed oasis has some whether it stocked them or not |

### 2d. `RM_Vhorrin` — fish. *the cull.*

| field | value |
|---|---|
| FORM | **the murrin silhouette scaled wrong — arm-long, dorsal comb ragged, deep-bodied; ONE ring on a still pool** |
| look | The `vh-` apex root wearing the `-rrin` pool-kin suffix, and that is the whole horror: it IS a pool fish, the same stock, grown past the point where the pen can hold anything else. |
| nastiness | **It eats the farm.** Any stocked pool left crowded and unculled grows one; the murrin rings thin week by week until one wide slow ring is doing all the surfacing. It takes fingers. It has taken a wading child's arm, in the stories farmers tell to make the cull happen on time. |
| catch method | The cull: a deliberate, planned, two-handler catch — the stocked line's set-piece job, and the feast that follows is §4's. |
| food value + the doubt | An enormous single harvest of rich flesh. The doubt is arithmetic, not flavor: everyone at the feast knows what it grew fat on. |
| commonality | zero when husbandry is good — a vhorrin IS the "pool turned nasty" state made flesh (§3) |

### 2e. `RM_Loomu` — NOT a fish. *the caller.*

| field | value |
|---|---|
| FORM | **a soft bell-bodied swimmer trailing a throat-comb of organ-pipes — the comb breaks the surface to speak** |
| look | A cat-sized, boneless, dove-grey thing that hangs in the warm seep-throat water and repeats what it hears at the bank: the feed whistle, the wind through the vanes, a child's laugh, its keeper's name for it. |
| nastiness | Mild in the flesh, terrible in the ear — a loomu pen at night runs through its whole collection. Handlers stop teaching them words on purpose and cannot stop teaching them by accident. |
| catch method | Called. It comes to the feed whistle. That IS the catch method, and everyone hates it. |
| food value + the doubt | The tenderest meat in the biome, faintly sweet. **The doubt: it learned the whistle, and it answers the whistle, and you are netting it with the whistle.** Some farms keep one loomu only as the caller for the rest and swear they would never eat that one. |
| commonality | uncommon; two or three per farm, deliberately stocked |

### 2f. `RM_Huldu` — NOT a fish. *the warm one.*

| field | value |
|---|---|
| FORM | **a forearm-length velvet-skinned swimmer, dorsal comb folded flat like wet fur; clings when handled** |
| look | Warm to the touch — not seep-warm like the wild ozhu, body-warm, with a pulse you can feel through the skin. Lifted from the water it does not thrash: it grips the handler's forearm and presses close, and it shivers. |
| nastiness | None whatsoever, which is its own kind of problem in a bestiary the owner asked to make nasty: the huldu is the row that makes the HANDLER the uneasy party. It is the easiest catch on the farm. |
| catch method | Picked up. It holds on. |
| food value + the doubt | Rich and fatty, the winter-feast meat, renders a fine cooking fat. **The doubt: it is warm, it clings, it has something like breath, and it is quiet all the way to the kitchen.** |
| commonality | uncommon; breeds slowly, which the farms call mercy and the ledgers call a supply problem |

### 2g. `RM_Ivvol` — NOT a fish. *the tally.*

| field | value |
|---|---|
| FORM | **a flat bottom-dweller, its comb a raised dorsal ridge set with a row of eyes — the ridge surfaces, the eyes count** |
| look | A doormat-sized floor-thing that knows the feed schedule better than the apprentice does. The eye-ridge tracks the handler around the pool; at feed hour it is already waiting at the right stone. Ivvol in neighboring pools surface at the same moment, for no reason anyone has proved. |
| nastiness | Passive — but it *learns*. Pens with an ivvol have fewer vizhik escapes and no vhorrin has ever grown in one, and no farmer can tell you the mechanism, and most decide not to ask and quietly stock one. |
| catch method | Lifted from the floor at night, when the eye-ridge closes. By day it sees the net coming, every time. |
| food value + the doubt | Dense, mild, good keeping-meat. **The doubt: when finally netted it does not struggle — it goes still, and the whole ridge of eyes turns to the farmer, and it watches.** Eating the thing that ran your pool better than you did feels like eating the foreman. |
| commonality | rare; one per pool, and the pool is better for it |

## 3. The husbandry loop

The player verbs, in the order a farm learns them. R21 holds throughout: the
pool's income is wind and seep, never rain; the feed is thrown scrap, never a
rain-fed bloom.

| verb | what the player does | what goes wrong |
|---|---|---|
| **STOCK** | Net breeders at a wild oasis, carry them home in a wet skin (a carry-job to a pool cell), release into a designated pool zone. Species mix is the strategy: murrin for safety, skarrin/karrek for volume, a loomu or huldu for the feast line, an ivvol if you can get one. | Stock the wrong mix and the pool decides for you — karrek out-eat murrin; a crowded pen is a vhorrin waiting to happen. |
| **FEED** | A scheduled throw-job: mirrik cocoon waste, bladder-fruit scrap, kitchen offal to the water's edge. Feeding from the bank is safe; feeding late is not. | Two missed days and the karrek start on each other; three and the whole pool's stock curve bends down. |
| **READ** | Ring density on the water IS the stock gauge — art states, no inspector-diving. Murrin rings = healthy; thin rings = hungry or predated; one wide slow ring = vhorrin; **no rings = the silent pool**, the dead-oasis image (§10b) as farm telemetry. | Misreading costs a season. The silence cue is the alarm the biome already speaks. |
| **HARVEST** | Sustainable netting below the replacement rate; per-species catch jobs (net mid-air, basket-trap, whistle-call, night-lift — §2's catch methods are the job flavors). | Handling injuries are real: skarrin face-strikes, karrek stripping, vizhik septic bites. The farm has a medical bill. |
| **OVERDRAW** | Fish above replacement and the stock crashes for a year — the pool goes quiet, and quiet pools attract nothing good. | The crash state is also the vhorrin state's front door: a stressed pool turns nasty before it turns silent. |
| **CULL** | The set-piece: the two-handler vhorrin catch that rescues a failing pool, and the feast after. | Skip it and the pool ends as one fat fish and a silence. |
| **RECAPTURE** | At wind-hour, walk the wet stone and pick traveling vizhik off the rock before they reach the cistern. | Ignore it and the kitchen finds one in the stock-pot; a barrel-vizhik event is the comedy beat, the septic bite is the cost. |

**Pens and pool zones.** A stocked pool is a designated zone over contiguous
pool-water cells (an Area/zone designator, not a building); pen walls are
ordinary low walls at the waterline that raise the skarrin escape bar and keep
the karrek off the drinking margin — the truce's drinkers and the farm's stock
share the water, and the pen line is what keeps husbandry violence out of the
truce's sight (§6, §4 both honored by geometry).

**Reused machinery (paths verified on disk, 2026-09-24):**

- `src/RimMandrake/CreatureBehaviors/Source/RM_CompVerminBreeder.cs` +
  `RM_MapComponent_VerminPopulation.cs` — the per-map stock that breeds, caps,
  and crashes (built for the Fever Wood grubs); a pool stock is the same math
  wearing fins, per the greenlit option's own read.
- `src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_SilenceCue.cs` —
  the built "the absence is the signal" register; the silent pool rides it.
- `src/RimMandrake/SeaShores/Source/RM_SeaShoreExtension.cs` — the opt-in
  DefModExtension that makes a biome fishable with no whitelist; plus the
  Scald's `fishTypes MayRequire Odyssey` precedent for the catch tables.

**New build, sized honestly:**

| piece | size | note |
|---|---|---|
| `RM_MapComponent_PoolStock` — per-pool-body bookkeeping | **M** | The honest hard part, named in the greenlit option: contiguous water bodies identified, tracked across terrain edits, scribed. `RM_LiquidBody` (FlowWorks) does it for excavations — its region logic is the pattern to steal, not the object to reuse. |
| Stock/feed/harvest jobs + pool zone designator | **M** | Carry-to-water, scheduled throw, four catch-job flavors. |
| Ring-density art states (incl. the vhorrin single-ring and the silence) | **S** | Overlay art keyed to PoolStock state; the gauge is readable at a glance or the feature fails. |
| Handler-injury on handling jobs | **S** | Toil failure → vanilla bite/cut injury with per-species weight; no new damage system. |
| Vizhik escape events at wind-hour | **S** | Spawn-at-wet-cells event + recapture job; barrel/cistern arrival is a flavor letter. |
| Vhorrin emergence + cull set-piece | **S–M** | A state flip on PoolStock plus a two-pawn job; the feast is §4's. |
| Beast rows (3 pawn defs + 3 catch items + thoughts) | **S** | Defs only under the two-def law; no new C#. |

Total: a solid **M** with one M-sized core risk (pool-body bookkeeping), which
matches the greenlit option's own sizing. Feature-gated per the Mod Settings
law (2026-09-12): stocked pools off = wild fishing only, degrades clean.

## 4. Rimcuisine hooks — what a colony makes of a thing it wonders about eating

Shape law for all six: **recipes and ThoughtDefs only, no new C#.** The
doubt-meat rows ship as distinct meat/catch items with their own
`thingCategories`, so an installed RimCuisine-style mod's recipes accept them
via ordinary category membership, and our own patches ride `MayRequire` — the
free mod's kitchen is complete without any third party, per Q11a.

1. **Pool-fry basket** — skarrin + karrek, the volume line: a cheap simple-meal
   recipe, the stocked farm's daily bread. No thought hooks; this is the
   control group the doubt is measured against.
2. **Murrin-and-seep-salt broth** — murrin + seep-salt (sheet §11's item): the
   pilgrim's comfort dish, small mood buff, the taste of the stones. The dish
   that says the pool is well.
3. **Karrek paste** — a basketful rendered at a stove into a dense ration that
   keeps for a season (the commission's flood-bread register): caravan food for
   the oasis string, eaten with resignation.
4. **The Cull Feast** — one vhorrin → a feast-scale meal batch plus a colony-wide
   thought: relief and unease in one dish (+mood "the pool is saved", with a
   small stacking debuff for pawns who knew what it grew fat on — flavor text
   does the work, vanilla thought machinery carries it).
5. **The doubt-meat line** — loomu, huldu and ivvol flesh are each their OWN
   meat def with an `Ate X` ThoughtDef, graded: *ate loomu* (it answered the
   whistle) a real mood hit for most pawns, shrugged off by psychopaths and
   bloodlust; *ate huldu* (it was warm) a small hit; *ate ivvol* (it watched)
   a small hit that certain colonists — the ones who ran the pool — feel twice.
   Cooked into mixed meals the thought dilutes; served as the named roast it
   does not. An ideoligion food-taboo hook (doubt-meat as forbidden or as
   sacrament) is listed as a question, not assumed.
6. **Rendered huldu fat** — a cooking-fat ingredient that upgrades any meal
   recipe's mood outcome by a point: the best cooking on the planet, priced in
   exactly the discomfort the owner asked for. (Category-tagged so modded
   baking/frying recipes pick it up for free.)

## 5. Collision sweep

Instrument proven first: `git grep -il murrin -- design/ src/` returns 3 files
(the roster JSON, the fauna roster, the shine options) — the probe finds a
known-present name. Then each coinage, same instrument, 2026-09-24:

| coinage | hits in design/ + src/ | verdict |
|---|---|---|
| `skarrin` | 0 | clean |
| `karrek` | 0 | clean (shares `karr-` chitin root with karrun/karrash/tarrik by design — kinship, not collision) |
| `vizhik` | 0 | clean (shares `-zh` sibilant root with ozhu/zhurr by design) |
| `vhorrin` | 0 | clean (`vh-` apex + `-rrin` pool-kin, the deliberate blend) |
| `loomu` | 0 | clean |
| `huldu` | 0 | clean |
| `ivvol` | 0 | clean |

All seven are offers; the owner renames at will. None is a canon Star Wars
name (invented per Q11a; no Wookieepedia standing needed or claimed — these
live franchise-free in the RM_ tier by design).

## 6. Questions for the owner

**Category-level first:**

1. **Do the ruled wild six stay gentle?** The fish commission's §2A table
   (ikkal the dew-cup, duul the janitor, ullo the wedding bell — ruled
   2026-09-18) is the *wild* catch and reads pastoral. Your nasty ruling was
   typed against the STOCKED line. Proposal: wild table stands as ruled, the
   nastiness is what domestication and crowding do — the pen makes the
   monster. Confirm, or extend the nasty pass to the wild table too?
2. **How real is the doubt?** The doubt-meat thoughts in §4.5 — real mood
   economy (small but permanent trade-offs), or pure flavor text v1? And is
   an ideoligion hook (doubt-meat forbidden / doubt-meat as sacrament) wanted,
   or does that over-machine a joke that lands fine as prose?
3. **How real are the injuries?** Handler bites as genuine medical events
   (infections, lost fingers on a bad roll) or as flavor-scratches? The
   "nasty" reads strongest if a careless farm actually bleeds.
4. **Tier confirm:** the whole stocked-pool mechanism lives in
   `RM_WeepingStones` (free mod, feature-gated) with nothing canon in it —
   confirmed by Q11a as we read it, flagged only because the mechanism could
   also be a general RimMandrake kit other biomes borrow later.

**Per-row:**

5. `RM_Vhorrin` — emergence as a *state* of the pool (our proposal: it IS the
   mismanagement state) or as a rare wild monster you can also net? The first
   is better husbandry drama; the second is more bestiary.
6. `RM_Ivvol` — its pool-improving effect (fewer escapes, no vhorrin): real
   small mechanical bonus, or farmer superstition the numbers never confirm?
   Superstition is funnier; the bonus is better game.
7. `RM_Loomu` — the whistle-catch implies tamability. Tamable-but-you-eat-it
   is the sharpest version of the doubt; is a loomu ever a PET, or does that
   cross a line the kitchen can't come back from?
8. Names: all seven are offers, nicknames included.

---

_Compiled read-only against the frozen sheet (§4 truce, §5 comb, §6 ambush ban,
§10b, §11), the ruled fauna roster (2026-09-24), the greenlit shine option 1,
and the fish commission (naming voice + §2A ruled table + §0 two-def law).
Comp paths verified on disk; collision sweep run with a proven instrument.
Nothing filed, nothing committed, no roster re-adjudicated._
