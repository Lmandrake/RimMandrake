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
