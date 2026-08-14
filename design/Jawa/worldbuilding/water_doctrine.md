# Water doctrine — the master resource, finally decided

_VISION, 2026-08-13. **Owner's ruling, verbatim, recorded the hour it was made.**
Water has been the declared master resource across the whole faction roster since
the beginning and has had **zero implementation and no decided layer** — every
faction carries a "water doctrine" line resting on a mechanic nobody had ruled
existed. This closes that._

> *"Jawa (and other desert races) should need much less water than other xenotypes
> not native to this planet, and droids don't need any — hence their advantage.
> Potable water-bearing squares should always have significant defenders present
> (reason for them being there). Most desert water will be saline or otherwise
> contaminated, and in v2 there should be some purification tech that can be made
> to handle that to some degree (expensive). In v2, using water bottles as a form
> of currency is pretty exciting — perhaps by making them semi-common while silver
> becomes rare. Feels like a barter economy then, as it should."*

---

## The four rulings, separated because they land at different times

### 1. Thirst is DIFFERENTIAL, not universal — this is the whole design

**Everyone drinks, but not equally, and the gap is the campaign.**

| who | need | why it matters |
|---|---|---|
| **Jawa and desert-native races** | **much less** | the clan can go where others cannot |
| **Off-world xenotypes** | normal | recruits are a liability in the deep desert |
| **Droids** | **none** | ⭐ **this is the Jawa advantage, stated mechanically for the first time** |

⭐ **This is the single most important line in the document.** The roster has said
for months that *droid labour is water security, not tech progression*. **Nothing
made it true.** A differential thirst need makes every restraining bolt an act of
water economics — and the campaign's moral problem (the Free Droid Enclaves call
it slavery) becomes a decision with a number behind it instead of flavour text.

⚠️ **A recruit who drinks normally is a real cost.** That is a feature: it gives
the player a reason to prefer their own kind, and prefer machines over both,
which is exactly what a Jawa clan should feel.

### 2. Potable water is DEFENDED — always, without exception

**Every tile with drinkable water has significant defenders on it, and their
presence is explained by the water.** Not a random garrison; the reason they are
there.

**Why this is the good version:** it converts water from a resource you *find*
into a place you must *take or trade for*. Scarcity you can walk to is not
scarcity. **This also silently solves the tile-augmentation problem** — "what
makes a tile special" is answered for the most important tile type in the setting
(`tile_augmentation_catalogue.md` §0 asked exactly this).

### 3. Most desert water is SALINE or contaminated

Raw water is mostly undrinkable. **v2 adds purification tech, deliberately
expensive** — a capability the clan grows into, not a starting convenience.

**Design consequence to hold onto:** purification is what turns a worthless tile
into a valuable one. It should feel like the moment the map changes shape.

### 4. ⭐ v2 — water bottles are the CURRENCY, and silver goes rare

> *"Semi-common water bottles while silver becomes rare. Feels like a barter
> economy then, as it should."*

**This is the most transformative item in this document and the furthest out.**
Making the drink the coin does something no amount of flavour text can: **every
purchase is measured in survival.** Buying a rifle costs days of life. That is a
desert economy, and it is why the Hutts are frightening rather than merely rich.

⚠️ **It is also the highest-risk change in the whole design**, because RimWorld's
trade, quest reward and raid-loot systems all assume silver. **Do not start it
casually.** It wants its own build slot and its own testing pass.

---

## What this changes for the roster — the audit I now owe

**Twelve factions carry a water-doctrine line each, written before any of this was
decided.** Each must now be re-read against these four rulings, specifically:

- Does the faction's doctrine assume *universal* thirst? Several may.
- Does it hold water tiles? **If yes, it now comes with defenders by rule 2.**
- Is it a desert-native race (low need) or off-world (normal need)? **That
  changes its operating range**, which several dossiers state as a number.

**This is a v2 authoring pass, not a v1 one**, and it is filed as such. Nothing
here blocks the current worldgen.

## Layer discipline — say which one you are speaking in

| layer | what water is |
|---|---|
| **fiction** | the reason every faction is where it is, and the thing wars are about |
| **v1 engine** | **nothing. It is not implemented and does not need to be.** |
| **v2 engine** | differential need · defended sources · purification tech · bottles as currency |

⛔ **Do not let the fiction layer's confidence leak into build talk.** "Water is
the master resource" is true of the setting and false of the current game, and
conflating those has already cost this project a roster full of doctrine lines
resting on nothing.

---

# The roster audit, and the seven rulings it forced

_VISION, 2026-08-13, same day. All twelve NPC dossiers plus the player section
were read against the four rulings above. **The audit found prior art I did not
know about and five genuine contradictions.** Rulings below are final._

## Prior art: the roster was already ~70% there

**A low-water species tier already exists at `faction_roster_v2.md:161–175`** —
Tusken, Desert alien/Impid and Geonosian at *very low*; Nikto, Kaleesh, Iktotchi
at *low*; **all droid chassis at none**. Ruling 1 did not invent differential
thirst; it ratified something already half-written and never enforced.

## W1. ⭐ Add a FOURTH band: ELEVATED

**My three-row table topped out at "normal" and three faction doctrines depend on
above-normal thirst.** The roster's own elevated list is at `:175` — Wookiee,
Wookiee-kin, Herglic, Mon Cal, Quarren, Selkath, Gungan, Chagrian, Aqualish,
Trandoshan, Rodian, Ithorian, Ewok.

| band | who |
|---|---|
| **none** | all droid chassis |
| **very low / low** | desert-natives — Tusken, Desert alien, Geonosian, Nikto, Kaleesh, Iktotchi, **and Jawa (W2)** |
| **normal** | off-world humanlikes — baseliners, Chiss, Umbaran, Arkanian, most of the Imperial roster |
| ⭐ **elevated** | aquatics and heavy-bodied species — the `:175` list |

**Elevated is not a penalty, it is a leash**, and it is what makes the Wookiee
Freeholds *devastating at home and near-useless expeditionary* — the best-written
water consequence in the roster.

## W2. 🔴 Jawa are MISSING from the low-water tier — add them

`:165–173` lists no Jawa. **The most desert-native race in the setting is
currently specified as an ordinary drinker**, while the player section (`:2329`)
asserts *"Dry-adapted"* with nothing behind it, and the owner's ruling names Jawa
first. **Add Jawa at *low*.** The Jawa Trade Moot's "normal raid range" (`:1859`) is
corrected by the same stroke.

## W3. Tusken short raid duration is DOCTRINAL, not physiological

`:794` gives Tuskens the shortest range in the roster *because of water*, while
`:167` puts them in the same *very low* tier as Geonosians, who get **the longest
reach on the map** (`:1355`). Under differential thirst that reasoning is dead.

**Keep the short duration. Change its cause.** Tuskens **Forbid** water by taboo
(`:790`) and fight hit-and-run by culture. **They could range far and choose not
to.** Fiction preserved, contradiction removed, and it is a better characterisation
than dehydration was.

## W4. Ruling 2 covers NATURAL sources only — manufactured stores are exempt

The Homestead holds stored water behind the roster's weakest guard (6–16
poor-gear militia, `:680`), which looked like a violation.

**It is not, and the carve-out is the honest one:** *"potable water-bearing
squares always have defenders"* means **natural, renewable sources** — aquifers,
oases, springs. **A vaporator farm is a trickle, not a source**, and `:663`
already says its water is not worth capturing. **Manufactured and stored water is
not a defended tile type.**

⚠️ **This is load-bearing for the player**, who will also manufacture. It means
the clan's own stills do not automatically become raid magnets.

## W5. Purification is cheap for those who HAVE it, expensive to BUILD

`:1218` and `:1247` make desalination the Deepwater Compact's cheap industrial
export *today*, and the Jawa Trade Moot's crawler stills (`:1849`) are salvage-grade —
both against ruling 3's "expensive v2 tech".

**Both stand. The ruling was underspecified, not wrong:**

- **The League's monopoly IS their power.** Cheap purification in their hands is
  exactly why everyone tolerates them — remove it and the faction has no reason
  to exist.
- **Jawa Trade Moot stills are low-yield salvage** — enough to live, never enough to
  trade.
- ⭐ **What is expensive is the PLAYER building their own at scale.** That is the
  v2 tech, and it is a *strategic* unlock: the day the clan stops buying from the
  League is the day the map changes shape.

## W6. The League holds every AQUIFER, not every water tile

`:1202` says the Deepwater Compact holds **every** natural water tile — which cannot
coexist with the Cartel's oases (`:148`, `:159`) or the Wookiee upland springs
(`:1071`, `:1081`).

**Ruling: the League holds the deep, renewable water — the aquifers they are
named for. Oases and upland springs are surface features and belong to whoever
sits on them.** Three factions keep their holdings; the contradiction is gone.

## W7. Industrial water demand is a SEPARATE axis — noted, not resolved

The Consortium (`:1486`) consumes water for vats and biosculpters, not for
pawns. **None of the four rulings covers industrial draw.** Flagged rather than
invented: it matters only when water becomes a tracked good, which is v2.

---

## Where each faction now stands

| verdict | factions |
|---|---|
| **consistent, no change** | Hutt Cartel · Imperial Directorate · Free Droid Enclaves · Geonosian Hive · Blackstar Company · player expedition |
| **fixed by W1 (elevated band)** | Wildsteam Clan · Deepwater Compact |
| **fixed by W2 (Jawa tier)** | Jawa Trade Moot |
| **fixed by W3 (doctrinal range)** | Deep Desert Tribes |
| **fixed by W4 (natural-source carve-out)** | Outer-Rim Homestead |
| **fixed by W6 (aquifer vs surface)** | Deepwater Compact · Hutt Cartel · Wildsteam Clan |
| **still assumes universal thirst** | ⚠️ **the Junkers** — range set from one undifferentiated stolen pool while its roster is 14% low and 25% elevated. **Draw rate sets their reach, not volume.** Rewrite when faction 12 is authored |
| **silent on ruling 4 (bottle currency)** | **all thirteen** — expected, it is the furthest-out item |

**Nothing above blocks v1.** These are corrections to a v2 authoring surface,
made now because the ruling was fresh and the contradictions were cheap to see.
