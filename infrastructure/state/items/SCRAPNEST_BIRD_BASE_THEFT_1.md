# SCRAPNEST_BIRD_BASE_THEFT_1 — owner card: should scrap-nest birds steal from player bases?

## the ask

`design/Jawa/worldbuilding/biomes/arid_shrubland.md` §4 "Venomvine — the
fortress flora" ends its scrap-nest paragraph with a parenthesis, and that
parenthesis is the whole of this card:

> **The scrap nests.** The bird-analogs are scavengers too: they line their
> nests in the vine with glittering scrap — wire, lens-glass, chips of hull —
> beautiful creations, and a treasure worth seeking for a Jawa. […]
> *(Candidate: the birds also steal from player bases.)*

**What already shipped** (`SHRUBLAND_SCRAPNEST_BIRDS_1`): `RSW_ScrapNestBird`
is a real animal in `RUT_AridShrubland`; it builds `RSW_ScrapNest` buildings
in the wild and carries loose components, precious metals and steel back to
them; a nest slowly accumulates scrap on its own and pays out a hoard when it
is smashed or burned. All of that is the "treasure worth seeking" half, and
none of it touches your colony.

**What was deliberately NOT built:** the theft. `JobGiver_HoardScrap` refuses
any item inside a player home area or in any storage, and a bird will not site
a nest inside a home area either. There is no Mod Setting that relaxes it —
turning the guard into a toggle *is* building the mechanic, so it waits on
your word.

## the decision this needs

Whether the birds should rob you, and if so how hard:

- **(a) No — leave it as shipped.** The birds are pure treasure: dangerous to
  reach, never a nuisance. Simplest; loses the two-sided character the
  parenthesis hints at.
- **(b) Yes, but only the unstored.** They take loose items lying in the open
  inside your base — never out of a stockpile, a shelf or a building. Reads as
  "don't leave your components in the dirt", costs the player almost nothing
  if they are tidy. Cheapest to build from what exists (one predicate).
- **(c) Yes, properly.** They take from stockpiles too, which makes them a
  real pest you must roof, net or shoot — and makes finding the nest a
  RECOVERY, not just a windfall, because your own components are in it. The
  most interesting version and the most annoying one.
- **(d) Yes, but rare and event-shaped.** Ordinary birds never steal; a
  periodic incident brings a flock that raids once and leaves, and a tracked
  nest somewhere on the map holds what they took.
- **(e) something else entirely** — your words, verbatim, land straight on
  the design.

If the answer is anything but (a), say whether it should ship **on by default**
or **off by default** in Mod Settings — the setting already exists
(`RSW_BeastMechanicsSettings.scrapHoardingEnabled`) and a theft flag would sit
beside it.

## why it matters

A wild animal that removes items from a player's base is a large tonal
decision, not a tuning value: it changes the bird from flavour-plus-loot into
a threat class the player must defend against, and it is the kind of mechanic
that reads as a bug the first time it happens if it was never announced. The
source text calls it a candidate rather than a design, so building it on a
builder's judgement is exactly the rework `COMMISSION_LEDGER_CLEANUP_1` warns
against for mechanics-shaped slugs — the same caution `SHRUBLAND_TREE_GUARDIAN_1`
got for the sweetline-tree guardians.

## Watch out

- **The guard is in two places, not one.** `JobGiver_HoardScrap.IsTakeable`
  refuses items in `map.areaManager.Home` or `IsInAnyStorage()`, and
  `TryFindNestCell` refuses home-area cells. Whoever implements a ruling must
  relax the right one: (b) needs only the storage half loosened, (c) needs
  both, and neither should let a nest appear inside the colony.
- **Do not conflate this with `DESERT_GLITTER_BIRDS_COMMENSALS_1`.** That is a
  different bird mechanic on the desert sheet — shade-follow commensalism, not
  theft or hoarding.
- **The nest is where the evidence goes.** Option (c) only works well because
  the stolen goods are recoverable from a findable nest; if nests were ever
  made to despawn or to sit off-map, (c) silently becomes pure loss and should
  be re-ruled.
- Options for you to LOOK at would be cheap here: the bird, a nest and a hoard
  can all be staged on one map through the bridge and saved
  (`rimworld-live-review`), so a ruling need not be made from prose alone.
