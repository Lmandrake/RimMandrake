# The Twilight Deep — the marquee: rewards, experiences, interactions (2026-09-26)

_DESIGN pass on the owner's ask, 2026-09-26: "What FANTASTIC new ideas could we bring in
to really bedazzle this place! Make it comparable with the other oceans in terms of
rewards, experiences, and interaction? ... Feed it the other finished biome descriptions
to normalize it." Written against the frozen sheet `the_twilight_deep.md` (amendments add
detail, never change a ruling) and normalized against `the_grey_deep.md` +
`the_grey_deep_content_2026-09-26.md`, `the_scald.md`, and
`greentide_risk_reward_2026-09-22.md`. Nothing here is a def; nothing here is filed._

**Scope boundary.** The parallel content pass (`the_twilight_deep_content_2026-09-26.md`)
owns the roster: the twelve-plus seaweeds, the clinging micro-fauna, the fish analogs and
their floor bodies, the bioluminescence visual language, the lighting-only weather and
the whale's shadow, and the Deepwater houses. This document is the layer above it — what
a player tells someone about after a dive, what they come back with, what they lose, and
what relationship they enter. Where an idea below needs a creature or plant, it points at
that pass's territory as raw material and does not author one.

**Today's rulings this is built on** (owner, at the bench, 2026-09-26): the mat-roof STAYS,
reskinned as a living canopy in lustrous blue-green — the ceiling mechanism is unchanged
(skylights are holes in it, they drift and expire over years, the ceiling gardens hang from
it, the gardener tends it). The underwater rivers LOOK like dry mud riverbeds but the
denser water inside still carries a pawn along them; hard ban 3 stays live; the banks are
the richest ground. Skylights are literal golden shafts reaching the floor. Fishing is
prolific and unlimited. The Deepwater Compact has SETTLED this sea and cleaned out the
scavenge and open mineral wealth. Access is ship-only.

**The reading of that last ruling that drives everything below:** the absence of loot is
designed, and it is a gift. The Grey pays you in things that were dead before you arrived
and stay dead in your hold. The Twilight cannot — there is nothing lying about, and the
people who took it are still there. So every reward here is **alive, renewable, expiring,
or relational**: something you keep only while you keep it. That is the one register the
Grey cannot enter, because its whole law is that the dead keep forever.

## 0. If we only build three — the ranked shortlist

| rank | idea | one line | why it is in the three |
|---|---|---|---|
| **1** | **§3.1 Skylight tenancy** | You never own a golden well. You hold one, and the roof decides when your lease ends. | It IS the biome's image made playable, it turns hard ban 5 (no skylight permanence) into the loop instead of a restriction, and its engine is mostly already shipped (a glower thing + a timer map component + the fishing/plant systems that light already drives). Cheapest marquee per unit of bedazzle. |
| **2** | **§3.2 The Compact's permits** | The Deepwater do not sell the Deep. They admit you to it, one right at a time, and every right is one they can take back. | The relationship the biome is *for* — the sheet's §7 "hospitality: dock-rights, air, lamplight, charts" — carried on Royalty's faction-tagged title/permit data instead of a new system, with the Inhabited cast (25 people, a hospital ward, the Sharing) as the faces. It is also the enforcement layer every other idea hangs consequences on. |
| **3** | **§3.3 The Ark Seed** | Carry a piece of the last living sea home, alive, and keep it alive. | The thing a player tells someone about. On a dead planet, founding a fishery of the only ordinary life left is the strongest possible reward, and it is *relational* by construction: breeding stock leaves the ark only by the Compact's highest permit, or by theft they will never forgive. It is the most expensive of the three and the one to protect from being built small. |

**If the third is too expensive for its slot, swap in §3.4 Living light** — the cheapest
idea in the document (the GlowTank, the glow hediff and the inert status engine already
exist) and the one that most directly answers "the unique content is in the plants and
animals." It is ranked fourth only because it is a *good* renewable reward where the Ark
Seed is a *marquee* one.

## 1. Why this is not the Grey in green — the thesis

The Grey Deep is a **statuary**: brine that keeps, pillars that never reach the light,
loot locked in mineral, a mind that trades in novelty because it has seen everything once
and needs nothing twice. Every transaction there is *extractive and terminal* — you dig
the dead out, you show the Elder a thing it has never seen, you leave with one of each.
Its emotional shape is dread, then possession.

The Twilight Deep is an **ark**: the last ordinary sea, crowded, lit from within, and
already kept by people who will not raise a hand and will not leave. Every transaction
here is *custodial and continuing* — you are admitted, you hold a well while it lasts,
you carry something living out and it dies if you stop tending it. Its emotional shape is
wonder, then responsibility.

The kind-distinction, stated so a future pass can check an idea against it:

| axis | the Grey | the Twilight | the Scald, for range |
|---|---|---|---|
| what the reward IS | a preserved thing (mineral, jacketed salvage, a one-of-each relic) | a living process (a tenancy, a culture, a breeding line, a standing) | an industry (steam-catch, pigment, baths) |
| how you get it | dig, chisel, show novelty | be permitted, tend, return | build works on the rim, endure the burn |
| what ends it | nothing — the encased never decay (ban 5) | the roof drifts, the tank chills, the Compact revokes | the boil never stops (ban 5) |
| the intelligence you meet | a geological mind that ignores function | a people whose whole doctrine is *we do not ask what it is for* | two faiths reading one shore |
| the light | none; a single moving mark; the murk stays blind (ban 4) | golden shafts, and every creature carrying its own | cyan glow under steam |
| the failure you fear | being kept — encased where you stand | being *unwelcome* — the door closing, the well going dark, the ark-keepers turning their backs | the burn |

⇒ **The test for any Twilight idea: does the player have to keep coming back to keep
it?** If a reward survives in a stockpile with nobody tending it, it belongs to the Grey
(or the Scald) and should be moved there or cut. Every idea in §3 passes that test; §4's
cost column says what it takes.

## 2. What is already built that this rides on (MEASURED from src/, 2026-09-26)

Read before inventing; each idea in §3 names which of these it reuses.

- **Ship-only access, persistent floor.** `RM_SeaDiveHatch` (`src/RimMandrake/DivingInteraction/`)
  is a `MapPortal` subclass gated by `PlaceWorker_NeedsGravEngine`. The base `MapPortal`
  holds its pocket map by `Scribe_References` and only `PocketMapUtility.DestroyPocketMap`
  clears it (`CompSealable`, `PitGate` and the labyrinth call it; **our hatch does not**) —
  so **a hatch's floor persists between dives**: what you built under a well is still there
  next dive. Cargo goes through the portal (`leftToLoad`, `Dialog_EnterPortal`,
  `ITab_ContentsMapPortal`) — hauling kelp and catch up is a load-into-portal job the
  engine already owns. ⚠️ **Build risk found in passing:** because the map is keyed to the
  hatch and not to the tile, a ship that dives the Twilight, launches, and dives the Grey
  would re-enter its *Twilight* floor. The build must either destroy on launch or key the
  map per sea tile; §6 Q8 asks which, because the choice decides whether §3.1's tenancy can
  persist at all.
- **The floor's cast and catch.** `RM_TwilightSea` (`src/RimMandrake/TerminalBiomes/`): 6
  `wildAnimals`, 12 `fishTypes`, `maxFishPopulation` 700, rare table
  `RM_RareTwilightCatches`. Floor bodies: `RM_Noolim` (the shoal, the one legal school),
  `RM_Loohn` (the predator), `RM_Weloon`, `RM_Lunoowa`, and **`RM_Lanternwhale`** — bodySize
  in the 30s, combatPower 2500, *"moss-shrouded and trailing blue lantern tendrils … It does
  not notice you. That is the whole of its character, until you make it."* ⇒ 🔑 The
  sheet's **gardener** and the owner's **great whale analog** are one creature already
  built; §3.6 treats them as one. The content pass owns the ten catch items that still
  lack floor bodies.
- **Luminous Pigment** (`mandrake.rm.luminouspigment`, deployed today): crowncarpet mat →
  Deepfire pigment via the press → `RM_GlowTank` (a `Building_PlantGrower`-shaped culture
  vat seeded with one fresh mat, dies after 6 h without power — `CompMatVitality`), 14
  glow-hediff families on pawns (`HediffComp_DeepfireGlow`), a research gate that hides
  until a colonist has *seen* the mat (`GameComponent_Deepfire.matSeen`), and the
  sumptuary "purple engine" — **built, generic, and currently inert: its thoughts fire once
  something is tagged as status.** Its own header records the GlowTank's FlowWorks
  salt-water gate as owed follow-on. §3.4 is that follow-on's natural home.
- **Inhabited** (`mandrake.rm.inhabited`): PLACE/CAST/ROUTE/FATE; a cast is a
  `ThingOwner<Pawn>` on a WorldObject; the placeless pool; FATE default *nothing — they
  live here*. `CastRoster_DEEPWATER.xml`: **25 named people**, among them a harbourmaster
  who greets Imperial quartermasters by name, a ration-keeper who has cut the Hold's
  household draw four times against no shortage, a quartermaster who *"has an exact figure
  for how much of the Empire's operational water … comes off his jetty … He will trade it.
  He has not yet decided for what,"* and Ilma Sook, who *"runs the Sharing — the ceremonial
  water-gift to anyone who arrives in need."* `SettlementManifestDefs_DeepwaterHold.xml`
  ships four districts including a **hospital ward** with medic and patient slots. Their
  wiring into a pocket map is the content pass's §9; §3.2 assumes it lands.
- **The Compact's ruled doctrine** (`04_factions.md` block 7; `JawaDeepwaterCompact.xml`):
  `raidsForbidden true` — wardens dehydrate off-water; the Balance is *"we sell to
  everyone, the Empire included, and interrupting ANYONE's water costs their goodwill: the
  campaign's central dilemma."* Ideo `the Balance`, memes water-primacy / pacifist /
  individualist / trader. ⇒ Their only lever on the player is **admission and price**, and
  §3.2 makes that lever the biome's interaction.
- **Lighting surfaces.** `GameCondition_Aurora` (RimSage, `Source/RimWorld/`) is the vanilla
  shape for a condition that overrides `SkyTarget` colour and glow with a timed lerp — the
  whale-shadow weather the content pass owns, and §3.6's gardener events, are that shape.
  Our own `RM_GlowMultiplierOverrideExtension` (`mandrake.rm.environmentalhazards`, built
  for Breaklight) already lets any `GameConditionDef` multiply a map's sun glow. LanternDeeps'
  `RM_DeepFlora.xml` ships glowing plants on an underground pocket map via plain
  `CompProperties_Glower` — the skylight-as-glower pattern is proven.
- **Royalty is a prerequisite, and its title system is faction-tagged data.**
  `FactionDef.royalTitleTags` (`Source/RimWorld/FactionDef.cs:291-318`) selects which
  `RoyalTitleDef`s a faction awards; `RoyalTitlePermitDef` is its own Def. Our factions can
  carry their own ladders without touching the Empire's. ⚠️ Whether the *bestowing
  ceremony* quest is Empire-hardcoded is UNMEASURED; §3.2 awards favour through our own
  quests instead and never depends on it.
- **Precedents for "it dies if you stop":** `CompMatVitality` (LuminousPigment),
  `RM_MapComponent_LivingRegrowth` timers (Greentide), and the Rot's live-prep recipes (no
  bulk variant on purpose — the shape `greentide_risk_reward` §2c adopted for every
  high-value expiring good).
- **The Bazaar** (`mandrake.rm.bazaar`): slice 1 only — `RM_BazaarIntelLayerDef` and the
  other plugin defs exist; the intercept, grid, price engine and haggle duel are **not yet
  shipped** (its About says so). §3.7 depends on slice 2 and is priced that way.
- **Not built, and not this document's to build:** skylights (zero defs), rivers/channels
  (zero), plants (zero), Compact presence on the floor (zero), own weather (zero). The
  content pass's §0 measured the same.

## 3. The marquee ideas

Each idea: the pitch · what the player does · what they get · what it costs them · the
engine surface · what it reuses · how it ranks against the Grey's and the Scald's
equivalent · build cost (detail in §4). Names are placeholders in the project's grammar;
everything is `RM_` — invented, not IP.

### 3.1 Skylight tenancy — the expiring golden well

**Pitch.** You never own a skylight. You hold one, for a while, and the roof decides when
your lease ends.

**What the player does.** Dives, finds a golden shaft standing on the floor, and moors a
**claim-buoy** under it (a small buildable, the sheet's §8 *"skylight claim-buoys"*). The
lit ground under the shaft is the only ground where the kelp analogs grow fast and where
the shoals crowd — so the tenancy is a farm plot and a fishing ground in one. They sow
under the well, set a fishing zone at its edge, load the harvest into the hatch, and come
back. Over in-fiction years the roof's slow life closes the well and opens another
somewhere else: the light walks away from the buoy, the plot goes dim, the fish go with
the light. The player moves — or negotiates a new well from the Compact (§3.2), who meter
them.

**What they get.** The sheet's §7 economies, made real and made *located*: kelp agriculture
(food, fibre, the wet lattice-timber), the only ordinary fishing on the planet at its most
prolific, and the sight the owner asked for — a golden column standing in green water with
your plot under it. The well is where the biome is most beautiful and where the player's
stake is.

**What it costs.** The lease ends, always (ban 5 is the mechanism, not a limit). A buoy
under an unlicensed well costs Compact goodwill every day it stands (§3.2). And the ship
must return: nothing under a well is reachable from home, so a tenancy is a *schedule*, the
Greentide's "you stop surviving it and start scheduling it" arc taken underwater.

**Engine surface.** A skylight **thing** carrying `CompProperties_Glower` (golden, large
radius) placed by a Twilight-only genstep — the content pass's §6.3 mechanism, shared;
plants and fishing already respond to light and terrain, so the plot works with zero new
rules once the light is real. A **MapComponent** (the `RM_MapComponent_LivingRegrowth`
timer shape) that ages each well and, at expiry, despawns it and spawns a new one at a
random floor cell — persisted, because the floor persists (§2, and §6 Q8). The claim-buoy
is a plain building whose comp checks §3.2's permit on a rare tick and applies
`Faction.TryAffectGoodwillWith` when unlicensed. ⚠️ **UNMEASURED:** whether Odyssey fishing
yield can be boosted per zone by nearby light (a Harmony patch on fish-population regen
keyed to a glower in range). Without it, the well still concentrates the *plants*; the
"fish crowd the light" half is then the shoal's own spawn weighting near glowers, which
`GenStep_SeaFloorFauna` could bias for free.

**Reuses.** `CompProperties_Glower` (LanternDeeps precedent), the LivingRegrowth timer
shape, the persistent pocket map, Odyssey fishing zones, the Compact's goodwill.

**Rank.** The Grey's equivalent is the soluble-mineral treasury and the pools' locked loot —
dug once, kept forever. The Scald's is steam-catch rights on the rim — a standing industry.
The Twilight's is a *lease*: richer than either while it lasts, and it never lasts. That is
the distinction §1 asks for, in one building.

**Cost.** Small C# (~1 map component, ~1 comp), XML for the well and buoy, art for both.
The fishing-boost patch is optional and separately priced.

### 3.2 The Compact's permits — dock, air, lamplight, charts, the ward, the Sharing

**Pitch.** The Deepwater do not sell the Deep. They admit you to it, one right at a time,
and every right is one they can take back.

**What the player does.** Earns standing with the Compact — by trade at the Hold, by the
quests §3.7 and §3.6 seed, by never once interrupting anyone's water — and spends it on
**permits**, each unlocking one thing the sheet's §7 already promises:

| permit | what it unlocks | the shipped thing it rides |
|---|---|---|
| **dock-rights** | the hatch may be opened over a Compact-kept tile without goodwill loss; a Compact **mooring** on the floor (a lit bank-hold beside the river) is where your pawns may shelter | `RM_SeaDiveHatch.IsEnterable` already refuses on conditions; add one. The bank-hold is the content pass's Inhabited house, used as a guest-house |
| **air** | a Compact **air-line** to your mooring: your pawns' floor stay is no longer bounded by the ship's own supply (if the gear gate lands — the generator's own header calls the no-air × temperature matrix follow-on work) | a `RoyalTitlePermitDef` worker that spawns a comfort/need building, the shape of vanilla's drop-resources permit |
| **lamplight** | the Compact strings lamps along *your* bank: real light on your plot between wells | a placed glower building, granted, not built |
| **charts** | the current well positions and the gardener-ways revealed on your floor map (§3.7) | a `CompUsable` item that marks the map |
| **the ward** | your wounded treated in the bank-hold's **hospital ward** by their medic — the only friendly non-player medicine under the sea, on a planet where every other faction is a raid | the Hold manifest's hospital district and medic/patient cast slots, already defined |
| **the Sharing** | Ilma Sook's ceremonial water-gift: a standing, capped water grant to a colony *in need*, the Compact's one charity — on a desert planet, from the water monopolists | a permit whose worker delivers water through FlowWorks' haulable-liquid route — ⚠️ UNMEASURED whether a carried liquid becomes a haulable thing (LuminousPigment's own header flags the same gap) |
| **the ark-key** (highest) | breeding stock may leave the sea — §3.3 | a permit checked by the tank |

**What they get.** A *standing*, not a stockpile — the relationship the biome is for. And
the reveal the sheet promises: the surface knows the Compact as water-sellers; only a
permitted diver learns what the water bought.

**What it costs.** Goodwill spent as favour, and the Balance itself: **interrupt anyone's
water — theirs, the Empire's, a farmer's — and the permits lapse in reverse order,
highest first.** Wardens cannot come for you (ban 4, `raidsForbidden`); they simply stop
opening the door, and the well you hold goes unlicensed (§3.1). This is the campaign's
central dilemma (`04_factions.md`) given a floor to stand on.

**Engine surface.** Royalty's faction-tagged title ladder: `royalTitleTags` on
`RUT_Jawa_DeepwaterCompact`, three or four `RoyalTitleDef`s (guest → moored → chartered →
ark-keeper's friend), `RoyalTitlePermitDef`s with our workers, favour granted by our own
quest rewards. Revocation is a small Harmony postfix on the goodwill change that strips
titles below a threshold. All five DLCs are assumed, so Royalty is a hard prerequisite and
this is not a fallback design.

**Reuses.** Royalty titles/permits, Inhabited's cast and Hold manifest (the content pass's
wiring), `Faction.TryAffectGoodwillWith`, FlowWorks' liquids, the Compact's ruled doctrine.

**Rank.** The Grey's equivalent is the Elder's novelty trade — a per-tile market with a
mind that ignores function. The Scald's is the two-faith shore and the baths. The
Twilight's is *hospitality with terms*: you are a guest of a people, and the terms are
their whole religion. Nothing in either other sea can make the player feel unwelcome.

**Cost.** Medium: XML ladder + 4–6 small permit workers + one revocation postfix + the
quests that grant favour. Depends on the content pass's Inhabited wiring for the
bank-hold, the ward and the Sharing's faces.

### 3.3 The Ark Seed — carry the last living sea home

**Pitch.** Carry a piece of the last ordinary sea home, alive, and keep it alive.

**What the player does.** With the ark-key permit (or without it — theft), captures a
breeding pair of a floor species (the floor bodies ARE pawns — `RM_Noolim`, `RM_Weloon`,
whichever the content pass's roster marks breedable), carries them up through the hatch in
a **stock-tank** (a building that is a `ThingOwner` of live pawns, the hatch's own cargo
shape), and installs them at home in a **sea-pen**: FlowWorks brine poured into a dug
basin, the tank set in it, fed on kelp from §3.1. If the pair lives, the pen *stocks*: the
home map's fishing zones on that basin draw from the ark's species, by type, name and
appearance — the owner's own rule for the sea, exported.

**What they get.** The only fishery on the dayside, of the only ordinary fish in the
world, at home. Food that is not a berry. And the thing a player tells someone: *I carried
the last sea back in a tank and it lived.* On a planet whose premise is that nothing
grows, this is the Twilight's answer to the Greentide's regrown limb — the setting's
strongest inversion, built from the biome's strongest fact.

**What it costs.** Everything the Greentide's R5 bloodstock costs, and one thing more. The
pen dies if the brine is wrong, the water chills, the feed stops, or the pair is one sex —
the `CompMatVitality` shape on a pawn line. The pen is superlinear upkeep forever (a bigger
ark costs strictly more per day — the Greentide's shipped negative-feedback stance). And
the price: **without the ark-key, taking breeding stock is the one act the Compact never
forgives** — permits stripped to zero, the door closed, the Sharing withdrawn. They will
not raid. They will not need to.

**Engine surface.** Capture is vanilla (down/tame and haul; the floor bodies are animals).
The stock-tank is a building with a `ThingOwner<Pawn>` (Inhabited's own cast container,
`Caravan`'s container). Breeding rides `RM_CompVerminBreeder` (`src/`, shipped for the
Greentide grubs) or vanilla egg-layer/hatcher comps. The pen's stocking is **one Harmony
patch** on Odyssey's fish-population source so a map component's "stocked species" list
is read where the biome's `fishTypes` would be — ⚠️ UNMEASURED where that read sits;
this is the single mechanism the idea rests on and it must be read from the decompiled
source before pricing is trusted. FlowWorks supplies the brine basin.

**Reuses.** The hatch's cargo, Inhabited's container shape, `RM_CompVerminBreeder`,
FlowWorks, §3.1's kelp for feed, §3.2's permit and revocation.

**Rank.** The Grey's equivalent is the Elder's one-of-each treasures — singular, dead,
kept. The Scald's is the rainbow pigment — harvested. The Twilight's is a *lineage*: it
breeds, it dies, and its provenance is a relationship you either honoured or broke.

**Cost.** Medium-high: the tank/pen buildings (XML + small C#), the breeding wiring, the
stocking patch (medium C#, and UNMEASURED), FlowWorks basin behaviour, art for tank and
pen. The marquee to protect; build it after §3.1 and §3.2 exist so it has a price and a
permit to hang off.

### 3.4 Living light — the lamp that must be fed

**Pitch.** Bring the light home alive.

**What the player does.** The content pass gives the biome creatures with *luminous balls,
bladders or patches*. One of them — a small sessile or slow one, the pass's choice — is a
**living lamp**: captured, carried up, and kept in a **lamp-tank** (the `RM_GlowTank`
pattern: seeded with one live creature, powered or brine-fed, dies in hours if chilled).
While it lives it glows — real light, a `CompGlower` on the tank whose colour is the
species'. Cultured, it is the **second source of Deepfire**: the sea creature's light is
the same pigment as crowncarpet's, and a lamp-tank culture presses into Deepfire at a
better yield than the shore mat, on the condition LuminousPigment's own header already
owes — salt water when FlowWorks is loaded.

**What they get.** Light without power, in a species' own colour; pigment for the whole
Deepfire chain (glow meals, the 14 hediff families, painted status); and — the reason
this is a *marquee* and not a lamp — the **first tagged status object** for the sumptuary
engine that shipped inert today: a living Twilight lamp in your hall is the thing the
purple engine exists to be jealous of.

**What it costs.** It is alive. Feed (kelp or catch, §3.1), warmth, brine; miss any and it
dies at once, and the Deepfire stops. No bulk: one tank, one creature, the Rot's live-prep
stance verbatim. And it is dim — the owner's *dim but well populated by local
illumination* — a lamp, not a floodlight, or the biome's light language is cheapened.

**Engine surface.** `RM_GlowTank` subclass (or the same class with a different seed
filter), `CompMatVitality`, `CompProperties_Glower`, `HediffComp_DeepfireGlow` for the
creature's own glow while free, a refining recipe on the existing press, and one
`ThingDef` tag for the sumptuary engine.

**Reuses.** Almost everything — this is why it is the cheapest idea here.

**Rank.** The Grey's equivalent is the Elder's resonant storage crystal — one per world,
mineral, and the Grey has *no* glow by ban 4; the contrast is the point. The Scald's is
crowncarpet pigment — harvested from a mat. The Twilight's is *tended light*: the only
light on the planet that is somebody.

**Cost.** Small: XML + a seed-filter change + a recipe + art. The FlowWorks water gate is
the only C#, and it is owed to LuminousPigment anyway.

### 3.5 Ride the dry river — the current as the lane, the bank as the wealth

**Pitch.** The rivers look dry. Step in and you go where they go.

**What the player does.** Reads the floor: braided mud channels, banked, apparently
empty. The banks are the richest ground — the only bank-terrain fertility, the burrowers
and sifters, the Compact's plots and moorings. The channel itself is the biome's **lane**
(`README_BIOME_GRAMMAR.md`'s lanes doctrine: *what is this biome's lane, who owns it, and
what does walking off it cost?*): a pawn or a thing that enters is **carried** — pushed
downstream cell by cell, unable to path out until the channel widens at a bank-eddy, and
lost if it reaches the sink where the channel leaves the map. The Compact's practice, which
the player learns by watching: drop the bundle in upstream, collect it at the weir. Their
**weirs** on the bank-eddies are where the current delivers the catch — a fishing zone on
a weir cell is the biome's second-richest fishing after the wells.

**What they get.** Free one-way freight across the floor; the bank harvest; the weir
catch; and the experience — the first time a colonist steps on "dry mud" and is swept
thirty cells to an eddy, the biome has taught its one lesson.

**What it costs.** The sink. A pawn carried past the last eddy is gone with the current —
the sheet's *"swimming into one means sinking with it"* as a real loss, the biome's only
lethal terrain in a place with no minerals to guard. Bulk freight by river is cheap, so
the brake is that everything worth carrying is alive or expiring (§3.1, §3.3, §3.4) and
the eddy is not where the ship is.

**Engine surface.** Channel **terrain** (a `TerrainDef` with `avoidWander`, mud art) laid by
a Twilight-only genstep along a braided path from a source edge to a sink edge; a
**MapComponent** that, per tick-interval, moves every pawn and item standing on channel
terrain one cell along the channel's stored direction vector (the Roil vortex spawner and
the mire component are the two shipped movers of things-on-terrain; `RM_MapComponent_
MudSwallow` is the item-side precedent); bank terrain with fertility; the weir as a
building that ends the carry and holds a fishing-zone bonus. ⚠️ UNMEASURED: whether
FlowWorks already carries a *current* on any liquid terrain — if it does, the mover is a
configuration, not new code.

**Reuses.** The Greentide's terrain-mover components, FlowWorks (possibly), Odyssey fishing,
`GenStep_SeaFloorTerrain`.

**Rank.** The Grey's equivalent is pillar-to-pillar navigation and the brine channels that
run *to the danger*; the Grey's channels kill and the Twilight's carry. The Scald's is the
boiling-lift and the bubble-sailors riding the vent columns. Three seas, three ways the
water moves you.

**Cost.** Medium C# (the mover, ~200–300 lines, plus the genstep), XML terrain and weir,
art. **See §5: this strains hard ban 3 and is left for the owner** — the narrow version
(items only; pawns are swept as a hazard, never as a chosen lane) is priced the same.

### 3.6 The gardener's ways — the whale as an actor, and the one catastrophe

**Pitch.** It does not notice you. That is the whole of its character, until you make it.

**What the player does.** Lives under the gardener. The content pass owns its **shadow**
as weather (the sky darkens as it passes over, the Aurora-shaped condition); this idea owns
what it *does*. Three events, on the floor, on the shipped `RM_Lanternwhale`:

- **The well opens.** The gardener grazes the canopy overhead and a new skylight spawns
  under it — a golden column standing where there was none, unclaimed for the moment. The
  Compact's charts (§3.7) age by exactly this event.
- **The well closes.** It patches a tear with its own secretions, and a well — perhaps
  yours — is gone. §3.1's expiry is not a timer in the fiction; it is *this*.
- **The gardener-way.** Where it descends to graze the floor, a lane of crushed kelp and
  disturbed bank: nothing built on a gardener-way survives its next pass. The Compact's
  moorings *"respectfully skirt"* them (sheet §8); the charts mark them; an unlicensed
  tenant learns the hard way.

And the interaction the sheet's ban 2 exists to threaten: **make it notice you** — attack
it, wound it, kill it — and the roof it tends begins to fail. No dramatic collapse (that
would remove the biome; ban 2 forbids removing the gardener and *leaving* the mat, and it
equally forbids a story that removes both): the wells stop opening. The floor's light
budget only shrinks from that day. And every permit the Compact ever gave you is void
(§3.2), because you have killed the thing they keep the sea for.

**What they get.** The set-piece the owner's *"shadow of the great whale analog would be
welcome"* implies, made consequential: a biome whose light is *managed by an animal*, and
whose richest events are a placid giant doing its work over your head. And one true
tragedy available to a player who wants one.

**What it costs.** Nothing, unless they choose the catastrophe — then everything the
biome gives, permanently, save-wide (a `WorldComponent` flag: *the last gardener is
dead*). It is the Twilight's version of "a player who kills the last one has killed the
last one" (`terminator_sea.md` §4), and it is the only irreversible thing in the sea.

**Engine surface.** Three `IncidentDef`s with workers that (a) call §3.1's map component
to spawn/despawn a well at the gardener's position, (b) lay gardener-way terrain along its
path; one `GameConditionDef` (Aurora shape, our `RM_GlowMultiplierOverrideExtension`) for
the descent's dimming; one Harmony postfix on damage-taken/`Kill` for the whale that sets
the world flag and calls §3.2's revocation; the map component reading the flag to stop
opening wells. Whether §3.6 also wants `CompStudiable` (Anomaly, shipped) on the whale so a
patient researcher can learn its ways without hurting it — a knowledge reward with no
harvest — is §6 Q6.

**Reuses.** `RM_Lanternwhale`, `GameCondition_Aurora`'s shape, the glow override,
§3.1's component, §3.2's revocation.

**Rank.** The Grey's equivalent is the Elder's discharge and the crusted giant's
scrape-sign — tells that let the observant survive. The Scald's is a bottom-walker's back
breaking the surface, rare and enormous. The Twilight's giant is not a threat you read; it
is a **keeper you live beneath**, and the only way it hurts you is if you hurt it.

**Cost.** Small-medium C#: three incident workers, one condition, one postfix, one world
flag — most of it shared with §3.1.

### 3.7 The charts and the ledgers — knowledge as the trade good

**Pitch.** The Compact's charts age as the roof drifts, and their ledgers know how all
three seas die.

**What the player does.** Buys, earns or steals paper. Two grades:

- **The chart** — a `CompUsable` item that, used on the floor, marks every current well
  and every gardener-way on the persistent map. It is dated: the map component stamps
  each well-change (§3.6), and a chart older than the last change is *aged* — it shows
  wells that have closed. A fresh chart is the Compact's to sell and is worth a permit's
  price; an aged one is what the wrecks of the impatient were carrying (sheet §8).
- **The ledger** — the Compact's own record, and the cast already holds three: Osso Reeth's
  fifty-minute recital of every sale to the Empire; Perrik's private cross-reference of
  Nossara's ration cuts against the harvest years; Bel Nossik's *exact figure* for the
  Empire's water off his jetty, which *"he will trade. He has not yet decided for what."*
  These are **Bazaar intel layers** (`RM_BazaarIntelLayerDef` exists): a found ledger
  unlocks a column — what the Compact charges the Empire, when the fleet fills, what the
  Hold is short of — that changes every later deal with them and with the Empire's
  quartermasters. And the sheet's third ledger, the **soundings** of all three seas'
  fates: the only place a player can read the world's clock.

**What they get.** Foreknowledge — the purest "changes what you can do rather than what you
have" (`greentide_risk_reward` R7's own phrase). And three of the best-written people in
the project become quest-givers with something to sell.

**What it costs.** A chart expires (it is the biome's motif, again). A ledger is *stolen*
from people whose whole doctrine is *we do not ask what it is for* — and Bel Nossik trades
his because it is the one thing the Hold has no copy of, which means the Hold will know
who has it.

**Engine surface.** `CompUsable` + a small use-effect that reads the map component's well
list; a `WorldComponent`/map stamp for chart age; two or three `QuestScriptDef`s on the
shipped quest pattern (`StrandedQuest`, `RUT_FungalSoilTradeRequest` are our precedents)
whose reward is a ledger item; Bazaar intel-layer defs. ⚠️ The Bazaar half **waits on
slice 2** (the grid and intel rendering are not shipped); the chart half does not.

**Reuses.** The Deepwater cast's authored hooks, the Bazaar's def scaffolding, the quest
system, §3.1/§3.6's well ledger.

**Rank.** The Grey's equivalent is *Deepwater's soundings* dropped from above and the
Elders' memory of the Reshapers — history read in chemistry. The Scald's is the dark
tower's control systems. The Twilight's knowledge is *current* — the only intelligence on
the planet that goes stale on a clock you can watch.

**Cost.** Small for the chart (XML + one use-effect + the stamp); the ledgers are quest XML
plus Bazaar defs and are gated on Bazaar slice 2.

## 4. Cost table

Sizes are rough and honest: **small** ≈ under 150 lines of C# or none; **medium** ≈ one
real component or patch, 150–400 lines; **large** ≈ a new system. "UNMEASURED" marks a
mechanism that must be read from the decompiled engine on this Desktop before the size is
trusted. Everything needs its Mod Settings toggle (standing rule) — not itemised.

| # | idea | new defs (rough) | new C# | size | UNMEASURED gate | depends on |
|---|---|---|---|---|---|---|
| 3.1 | Skylight tenancy | skylight thing, claim-buoy, genstep (3) | well-drift/expiry MapComponent; buoy licence comp | **small–medium** | fishing yield near light (optional) | Q8 (floor persistence); content pass §6.3 shares the skylight thing |
| 3.2 | The Compact's permits | 3–4 RoyalTitleDefs, 6–7 RoyalTitlePermitDefs, faction tag, 2–3 quests, lamp building | 4–6 permit workers; hatch permit check; revocation postfix | **medium** | Sharing's haulable liquid (FlowWorks gap, already flagged by LuminousPigment); bestowing-ceremony hardcoding (avoided by design) | content pass §9 (Inhabited wiring on the floor) |
| 3.3 | The Ark Seed | stock-tank, sea-pen, permit (3) | tank ThingOwner; breeding wiring; **stocking patch on Odyssey fishing** | **medium–high** | where fishing reads the species table — the whole idea rests on it | 3.1 (feed), 3.2 (permit/revocation), FlowWorks basin |
| 3.4 | Living light | lamp-tank (or GlowTank seed filter), recipe, status tag (2–3) | none beyond the FlowWorks water gate LuminousPigment already owes | **small** | none | content pass's luminous creature roster |
| 3.5 | Ride the dry river | channel terrain, bank terrain, weir, genstep (4) | terrain mover MapComponent; genstep | **medium** | whether FlowWorks already carries current | §5 ban-3 ruling |
| 3.6 | The gardener's ways | 3 IncidentDefs, 1 GameConditionDef, gardener-way terrain (5) | 3 incident workers; kill/damage postfix; world flag; (optional `CompStudiable` on the whale) | **small–medium** | none | 3.1's component; 3.2's revocation |
| 3.7 | Charts and ledgers | chart item, 2–3 ledger items, 2–3 quests, 2–3 Bazaar intel layers | chart use-effect; well-change stamp | **small** (chart) / **blocked** (ledgers) | none | Bazaar slice 2 for the ledgers |

**Shared infrastructure the top three need once:** the skylight thing + drift component
(3.1) is used by 3.6 and 3.7; the permit ladder and its revocation (3.2) are used by 3.1,
3.3 and 3.6. Building 3.1 and 3.2 first pays for most of the rest.

**Build order that keeps each step visible on its own:** 3.1 skylights and buoy (the
floor gets its light and its loop) → 3.4 living light (cheapest crossover, needs only the
roster) → 3.6 the gardener opens and closes wells (3.1 becomes fiction, not a timer) → 3.2
the permit ladder (once there is something to license) → 3.7 the chart (once wells have a
ledger) → 3.3 the Ark Seed (once there is a permit to gate it and feed to keep it) → 3.5
the river (after the owner rules §5) → 3.7 the ledgers (after Bazaar slice 2).

## 5. Where an idea strains a ban — left for the owner

Stated plainly; none is resolved here.

1. **§3.5 vs hard ban 3** — *"No swimmable river — entering a bottom channel means sinking
   with it; harvest and travel happen on the banks."* Today's ruling adds that the denser
   water *"still carries a pawn along them."* A river that carries is one a player will
   *use* as a lane, and "travel happens on the banks" is the ban's plain wording. The
   narrow reading that stays inside it: things dropped in are carried (the Compact's
   freight practice), pawns who enter are swept as a hazard and are lost at the sink,
   and no pawn ever chooses the channel as a road. The wide reading — the river as the
   biome's lane, ridden on purpose — is the better experience and is outside the letter.
   His call; §6 Q1.
2. **§3.3 vs the sheet's §5 and `terminator_sea.md` §4** — *"Everything ordinary that
   survives anywhere survives only here"* and *"each sea is an island … nothing crosses …
   every large organism in a terminator sea exists in that sea and nowhere else."* A
   home sea-pen stocked from the ark establishes ordinary marine life outside the
   Twilight. It is small, artificial, dependent and revocable — an aquarium, not a sea —
   and the canon line is about *wild* populations and *large* organisms. But it is the
   premise, and the Ark Seed is the one idea here that touches it. §6 Q2.
3. **§3.6's catastrophe vs hard ban 2** — *"No roof without the gardener — no story, def,
   or event removes the giant and leaves the mat standing."* The design deliberately does
   NOT collapse the roof when the gardener dies (that would delete the biome); it makes
   the wells stop opening, so the mat stands, un-tended, dimming. Is a standing,
   un-gardened mat "the mat standing" in the ban's sense? BENCH reads the ban as
   forbidding a *convenient* separation (kill the giant, keep the sea); an irreversible
   slow ruin is its opposite. §6 Q3.
4. **§3.2's revocation vs hard ban 4** — *"No Compact hostility canon."* Closing the door,
   voiding permits and withdrawing the Sharing are refusals, not hostilities; no warden
   raises a hand and no holding becomes a war camp. Recorded so a later pass does not
   escalate "they stopped opening the door" into "they came for us." No question needed
   unless he sees one.
5. **§3.1's licensed wells vs hard ban 5** — *"no fixed sacred/owned skylight outlives the
   mat's drift."* A licence expires with the well by construction; a licence must never
   *hold a well open*. The build note is the whole guard. No question needed.

## 6. Open questions for the owner

Each can be answered in a word; the BENCH position is stated so "yes" is enough.

1. **The river: lane or hazard?** May a pawn deliberately ride a channel as one-way travel
   (the wide reading, §5.1), or is the channel freight-only and a pawn who enters is simply
   swept (the narrow reading, inside ban 3's letter)? *Position: the narrow reading first;
   it costs the same, keeps the ban's wording, and the wide one can be opened later by a
   ruling if the swept-pawn experience turns out to be the thing players want to do on
   purpose.*
2. **The Ark Seed: may the last sea's life live in a tank on the dayside?** A dependent,
   revocable, artificial pen — yes or no to the idea at all (§5.2). *Position: yes, as an
   aquarium and never a wild population — nothing escapes a pen into any map's water,
   and a pen that dies leaves nothing behind.*
3. **The dead gardener: slow ruin, or nothing?** If the last gardener is killed, do the
   wells stop opening save-wide (§3.6, the biome dims forever), or is the whale simply
   un-killable / respawning so the ban is never testable? *Position: slow ruin. The
   terminator's own canon says a player who kills the last one has killed the last one,
   and the Twilight should be the place that sentence is felt.*
4. **Permits on Royalty's title system, or a system of our own?** §3.2 rides
   `royalTitleTags` and `RoyalTitlePermitDef` because all five DLCs are assumed. *Position:
   Royalty. It is data, it persists per pawn, and it is the shape the Compact's
   "standing" already has.* If he would rather the standing be *colony*-wide than
   per-pawn (a title belongs to one pawn), say so — that changes the surface to a
   `WorldComponent` and the cost to medium either way.
5. **Who holds the highest permit — the ark-key?** Per pawn (a Compact-trusted colonist
   who can be lost), or the colony? *Position: a pawn. A named ark-friend who can die in
   a raid is a stake; a colony flag is a checkbox.*
6. **May the gardener be studied?** Anomaly's `CompStudiable` on the whale would let a
   patient researcher learn its ways (charts for free, a knowledge unlock) without
   touching it. *Position: yes, and it should be the ONLY way to learn the gardener-ways
   without buying the chart — a reward for patience in a biome whose keeper rewards being
   left alone.*
7. **The Sharing: does the Compact's charity reach the player's colony at all?** Ilma
   Sook's water-gift *to anyone who arrives in need* is authored; whether "arrives" means
   at the Hold only, or a permit can carry it to a colony in a drought event, is his.
   *Position: the permit — it is the most surprising thing the water monopolists can do,
   and it is what makes losing their goodwill hurt.*
8. **Engine, not design, but he should know:** the hatch's floor persists between dives
   and is keyed to the hatch, not the tile (§2). Keep the floor per sea tile (tenancies,
   plots and moorings persist — §3.1 needs this) or regenerate every dive (simpler, and
   every tenancy is lost at launch)? *Position: per tile, and the build must stop a ship
   re-entering its Twilight floor over the Grey.* This is a bar on `SEA_DIVE_MAPS_BUILD_1`
   or its successor whichever way he rules; nothing here files it.
9. **Ranking:** does the top three in §0 stand — tenancy, permits, Ark Seed — or does
   Living light (§3.4, cheapest) take the third slot and the Ark Seed wait? *Position: as
   §0 — but if the Ark Seed's stocking patch measures large, swap without a second
   sitting.*
