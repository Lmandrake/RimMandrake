# The flood, witnessed — design draft

**Queue item:** `FLOOD_WITNESS_EVENT_1` · **Status:** DRAFT — nothing here is ruled.
**Sources:** `design/Jawa/worldbuilding/biomes/the_cracked_lands.md` §3/§4b (the flood
event chain), §9 (smell/sound order), §10 (the Sealed wake), §10b (explosive growth —
this event is its guaranteed showcase), §11 (water chimes; refuge ledges; 🔴 NEVER build
the bottom), §12 (a flood is a Jawa salvage strike);
`infrastructure/state/items/FLOOD_WITNESS_EVENT_1.md` (the brief);
`design/Jawa/explosive_plant_growth_draft.md` (the growth spine and the four
terminal-moment options — **unruled**; this draft parameterizes over all four and
picks none). Engine claims below marked CONFIRMED were read from decompiled 1.6
source via RimSage this session. Naming follows `design/NAMING_SCHEME_PLAN.md`;
every name is a placeholder (`<RUT_...>`), none coined.

**The ruling this draft serves** (owner, on filing): the flood mostly won't happen
while the player is in the canyons, so **the plot organizes an event where they
witness it at least once** — chimes, wall of water, explosive growth. Constraints
from the item: the player must survive witnessing it (refuge ledges exist for this);
it must sell **both faces at once — disaster and fertilizer; death, then soil, then
the bloom**; timing rides the plot, not weather RNG.

---

## 1. What the event must deliver (the contract)

1. **Guaranteed once.** Every campaign sees the full cycle at least once, on the
   plot's clock. Natural floods stay rare and unscheduled forever after.
2. **The whole chain, in canon order** (§3/§4b/§9/§11): storm on the peaks → wet
   clay on the wind → the flats tick as the Sealed wake → the water chimes ring up
   through the stone → the wall of red-brown water → drowning and deposition → the
   surge of visible growth → the terminal moment en masse → the dry returns.
3. **Survivable by design, lethal by disobedience.** The refuge ledge is the seat;
   the canyon floor is the show. A player who stays where the event puts them lives.
   A player who goes down early — and the loot will tempt them down — is genuinely
   in the flood's world, not a cutscene's.
4. **Both faces.** The same water that drowns is the water that feeds: the drowned
   dead, then the soil, then the bloom. The event's staging must land the turn from
   horror to harvest, not just the horror.
5. **Terminal-moment agnostic.** Phase 7 below is a slot. Whatever
   `EXPLOSIVE_PLANT_GROWTH_1`'s cards return — Burst, Bloom, Deadfall, Surge, or the
   per-biome split — the event delivers a soaked canyon floor dense with surging
   flora and lets the growth mechanic do what it was ruled to do. §5 carries one
   staging note per option; no choice is made here.

---

## 2. The witness beat, phase by phase

The seat: a **refuge ledge** (§11 — cut along the roads for exactly this) or a
Moisture Farmer high bench, depending on route (§3). The event map is a slot canyon
with a readable floor, flood-marked ruins on the walls (§8 — the farm built one
meter too low, so the map itself argues NEVER build the bottom), and water chimes
seated in the crack network.

- **Phase 0 — the still.** Dry canyon, standing heat, nothing moving. The player
  has a reason to be near or on the floor (route-dependent: salvage, a road, a
  trade). The longer this holds, the harder the turn lands.
- **Phase 1 — the storm on the peaks.** Dry lightning at the ridge; a letter names
  the Contagion's storm upslope (§4b). No local rain — R-H1 holds; the danger is
  arriving from somewhere the player cannot see.
- **Phase 2 — the nose and the ground.** Wet clay on the wind; the flats begin to
  *tick* as the Sealed wake underfoot (§9/§10 — the canon order: smell and ground
  before any sound). An experienced-Farmer line (route 3) or a flavor letter says
  what a local would know: trust the ground before the chimes.
- **Phase 3 — the chimes.** The water chimes ring up through the stone — the
  seep-cracks fill ahead of the surface wall (§11). This is the hard alarm and the
  evacuation clock: an alert, a sound the player will never mistake again, and
  (route-dependent) NPCs visibly climbing to the ledges. Everything on the floor
  has this window, and only this window.
- **Phase 4 — the wall.** The roar from upstream, then the wall of red-brown water
  down the canyon — red at the head, brown behind (§1, `WORLD_RIVER_COLORS_1`'s
  gradient). The floor floods end to end. Anything still down there drowns or is
  swept; pack animals included. This is the disaster face, played straight.
- **Phase 5 — the drowned and the delivered.** The water settles and begins to
  seep away into the cracks. The flood's own dead surface; carrion fliers wheel in
  (§4 — the commuters' feast). Deposition: flood mulch and fresh soil where there
  was cracked clay. The first face-turn: the letter here says *fertilizer*, not
  *aftermath*.
- **Phase 6 — the surge.** The growth spine (growth draft §1) at showcase scale:
  the whole soaked floor enters the surge — wet-dark, then visibly growing on
  screen, silhouettes climbing while the player watches from the ledge. The
  Spenders hatch and swarm among it (§10) — a carpet of frantic life where an hour
  ago there was nothing.
- **Phase 7 — the terminal moment, en masse.** The slot. Whatever is ruled on
  `EXPLOSIVE_PLANT_GROWTH_1`, it happens here at canyon scale, witnessed from
  safety at exactly the distance the growth draft's REFUGE verb promises works.
- **Phase 8 — the dry returns, and the ledger.** Water gone to the cracks, the
  floor open again: the aftermath drop (per terminal option), fresh-washed salvage
  (§12), crack-wax on the flats where the Sealed sealed again, the bloom economy's
  window. The player walks down onto ground the event just made — the second
  face-turn, underfoot.

**Safe enough / dangerous enough.** The design is a greed loop, not a rail: the
ledge is unconditionally safe through every phase (the flood cannot climb; terminal
effects respect distance/elevation per the growth draft's REFUGE constraint — a
build-time obligation, flagged there). The danger is entirely in *when you go
down*: salvage is richest while the mud is fresh (§12), the bloom crop is richest
at the tell (growth draft TAP), and both windows sit inside the surge-and-terminal
danger. Lingering on the floor is punished by whichever terminal moment is ruled;
lingering on the ledge costs only yield. Phase 3's chime window must be long enough
that a prudent player on the floor at Phase 2 can always reach a ledge — tuning,
not stated in ticks.

---

## 3. Routes to the canyon — how the player gets brought there

Three routes, plus the layering that makes "at least once" a guarantee rather than
an offer. The route choice is CARD 1.

### Route A — FLOOD-NEWS (the salvage strike)

The Jawa route (§12 verbatim: *a flood is a salvage strike; crawler crews follow
flood-news the way prospectors follow gold*). A contact — trader, comms, another
crawler crew — sells word that a Contagion storm is building over a named canyon.
A quest offers a timed destination site: get there before the water does. The
player arrives in Phase 0–1, sets up on the ledge, and the chain runs. Reward
skews material: first pick of the fresh-mud salvage.

- **Trade:** the best identity fit (the player is a Jawa doing the most Jawa thing
  on the planet) and the best reward — but it is an **offer**, declinable and
  missable, so alone it cannot guarantee the witnessing.

### Route B — THE ROAD CATCHES YOU (caravan interception)

The Cracked Lands are *on the way* (§7 — the roads thread the slots). The first
time a player caravan crosses the biome after the arming condition (§4), the plot
stops it: the chimes are already ringing. The map opens at Phase 3 — an NPC road
party (a Hutt toll crew, a Farmer train) is already climbing, the refuge ledge is
marked, and the player has the chime window to get the caravan up. Then the wall.

- **Trade:** guaranteed and fully diegetic — the flood happens *to* you, which is
  the truest version of the fantasy — but it is ambush-shaped: it commandeers a
  caravan mid-errand, opens at the alarm rather than the still (losing Phases 0–2),
  and fires only if the player travels the roads at all.

### Route C — THE FARMER'S GALLERY (the invitation)

The Moisture Farmers read the signs days out (§9 — the ground before the chimes).
A high-bench homestead sends word: the peaks are storming; come stand on our walls
— framed as hospitality, trade in flood-goods, or payment on a **discovery survey**
(§11's item-as-quest-seed: the newly found water this flood will reveal). The
player watches the full chain from inside a walled compound with a Farmer naming
each phase as it comes — the teaching version, canon-narrated.

- **Trade:** the safest seat, the best teacher, and it opens the Farmer relationship
  (surveys, cistern trade) — but it is a guided tour: the least visceral of the
  three, danger only if the player walks out the gate, and it too is a declinable
  offer.

### The guarantee (layering — CARD 1's option d)

Offers first, interception as backstop: Routes A and C are offered on the plot's
clock; if both lapse unaccepted, Route B arms and the next Cracked Lands road
crossing fires it. The residual hole — a player who never caravans — is closed by
the plot itself: an early campaign errand whose destination is across the Cracked
Lands (the roads are the through-route by canon), making Route B's trigger
near-certain in any played campaign. Whether that errand is hard-required is
CARD 2. *(Speculation as to which existing early errand serves; no current campaign
beat is claimed to already do this.)*

---

## 4. Plot integration

**When it fires.** Proposed: early — inside the first campaign act, after the
player can field a caravan, and **before** water-soaked growth matters on the home
map. The witness event is the world mechanic's teaching moment: the player should
meet the surge and the terminal moment for the first time from a ledge in a canyon,
not from two tiles away in their own irrigated field. Early also pays into the
early-game Jawa economy (salvage, the fungal-soil trade's farm customers). This is
a proposal, not a ruling — timing is CARD 4.

**What witnessing grants.**

- **The tells, learned.** The chain's warnings become player knowledge: wet clay →
  ticking flats → chimes → wall, and the growth spine's tell before the terminal
  moment (the growth draft's READ verb — its first-encounter alert can treat this
  event as the first encounter). Delivered as the event's letters, kept as a
  readable record (mechanism §5). *Proposal, unruled: gate the home-map "your plant
  has reached the tell" alert on having witnessed — knowledge as a real unlock
  rather than flavor.*
- **Material.** Route-dependent: fresh-mud salvage (A), flood-goods trade and a
  discovery-survey thread (C), the survivor's haul (B); in all routes, first
  contact with the bloom crop (§10b's boom-bust economy) and crack-wax off the
  flats.
- **Social.** A standing flood-news contact (A) and/or Farmer goodwill (C) — the
  hooks that make the *natural* replays reachable.
- **The thesis.** NEVER build the bottom, taught by a wall of water instead of a
  tooltip — the lesson that transfers to every soaked tile on the planet.

**Replay behavior.** The witness event fires once per campaign (a plot flag) and
never again. Afterwards the flood belongs to nature and to opportunism: natural
flood incidents on Cracked Lands maps at canon rarity (weather RNG, unscheduled),
and recurring opt-in flood-news salvage quests (Route A's shape, minus the staging
guarantees) for players chasing the strike. The guaranteed event is the only
scripted one; "at least once" is satisfied and then the plot's hands come off.

---

## 5. Mechanism sketch (register: design; C#-vs-def notes are sketches)

**Recommended shape: a quest wrapping a map-side director — not a bare incident,
not a global map condition.** A quest (`QuestScriptDef`) owns the hook, the site,
the once-per-campaign flag, and the letters; a C# **flood director** on the event
map (a MapComponent or spawned Thing) owns the phase clock and fires the staged
signals the quest listens to. Incidents alone can't stage an eight-phase scripted
sequence; a GameCondition alone can't own hooks, rewards, or the guarantee.

**What already exists (CONFIRMED in decompiled 1.6 source, read this session):**

- **Vanilla Odyssey flood machinery.** `RimWorld/Flood.cs`: abstract
  `Flood : Thing`, subclasses `SeasonalFlood` and `TorrentialRainFlood` (ThingDefs
  of the same names), `IncidentDef SeasonalFlooding`, and floodwater terrain
  (`ShallowFloodwater` and variants, via TerrainDef `floodTerrain`). It spreads
  from initial cells (`GetInitialCells`), respects buildings/foundations as
  blockers, and recedes. Gated by `ModLister.CheckOdyssey("Flood")` — the campaign
  runs 1.6 with Odyssey content in play, but this dependency should be stated at
  build. Source constants, for scale not as our tuning: flood width range 10–12,
  default `MaxFloodDurationTicks` 120000 (~2 in-game days).
- **Quest machinery** — QuestScriptDef node trees, sites, signals, letters, per
  the `rimworld-quests` skill; caravan-incident → generated-map machinery exists
  for the ambush pattern Route B needs.
- **The growth mechanic** — `EXPLOSIVE_PLANT_GROWTH_1`'s comp system, once built.
  **Interface contract:** the event's obligation ends at *a soaked floor and
  surge-capable flora at showcase density*; soak triggers the growth mod's comp
  and everything after — surge, tell, terminal moment, aftermath drop — is the
  growth mod's, unmodified. This is what makes the event terminal-agnostic.

**What is new C# (sketch):**

- `<RUT_...>` **flood subclass** of vanilla `Flood`: initial cells at the canyon
  head, custom terrain/color (the red-to-brown gradient), drowning-grade harm, and
  a pace override — the vanilla creep over days must become a wall over minutes.
  Whether accelerated `Flood` spread visually *reads* as a wall, and whether
  vanilla floodwater harms pawns at all, are UNKNOWN below; if either fails, the
  wall becomes a custom front (a moving effect line ahead of terrain conversion),
  which is more C# but owns its look.
- **The flood director**: phase clock, staged signals (`storm` → `smell/tick` →
  `chimes` → `wall` → `recede` → `soak`), sound triggers for the chimes, the
  Sealed-wake ground effect, and the soak call into the growth comp. Small but
  central.
- **Route B's interception worker**: a caravan incident that generates the canyon
  map at Phase 3 — reuses the ambush pattern; small.
- **The natural replay incident**: an IncidentDef patterned on `SeasonalFlooding`,
  Cracked-Lands-gated, minus the staging guarantees; small once the subclass
  exists.
- **Def-side, no C#**: the water-chimes building (§11 — placed by the site's map
  gen; the director rings them), refuge-ledge and flood-marked-ruin map elements,
  letters/rulepack text, the readable tells-record item.

**Per-terminal-option staging notes (Phase 7 slot — no choice made here):**

- **A (Burst):** the strongest ledge spectacle — a canyon floor going off like
  popcorn reads perfectly at distance. Only note: burst radii must respect the
  REFUGE distance rule so the ledge stays safe.
- **B (Bloom):** the showcase gains a second act — a canyon of crowns holding
  their window is an *invitation down*, so Phase 8's descent becomes a timed
  harvest against the rot. The greed loop sharpens; staging unchanged.
- **C (Deadfall):** the growth draft itself flags mass falls as chaos to read —
  under C the showcase leans on fewer, landmark-scale towers on the floor rather
  than hundreds, with the lean aimed cross-canyon for legibility. The one option
  needing showcase-specific density direction.
- **D (Surge):** the green tide running the canyon floor wall-to-wall is the
  biggest possible version of this event — and the growth draft's perf gate bites
  hardest here; the showcase inherits that build gate and may need the director to
  cap or wave the runner front.
- **E (per-biome split):** the Cracked Lands' assigned moment plays; no change to
  the event's shape.

---

## UNKNOWN (could not be grounded in the docs and source read)

- Whether vanilla floodwater terrain harms or drowns pawns at all — the wall's
  lethality (Phase 4) may be entirely new C#; not read this session.
- Whether an accelerated vanilla `Flood` spread visually reads as a *wall* rather
  than fast creep — unmeasured; decides subclass-vs-custom-front above.
- Which existing early-campaign errand (if any) already routes travel through the
  Cracked Lands for the §3 guarantee backstop — no campaign-beat doc was read that
  states one.
- All numeric tuning: phase durations, the chime window, salvage/bloom yields,
  flood damage — nothing above states a number as ours; the two source constants
  cited are vanilla's, for scale only.
- Whether the growth mod's first-encounter READ alert and this event's
  tells-record should be one system — depends on `EXPLOSIVE_PLANT_GROWTH_1`'s
  build, not ruled there yet.

---

## Owner cards

### CARD 1 — HOW THE PLAYER GETS THERE (pick one, or d)
- **(a) Flood-news — the salvage strike.** A tip is sold: a storm is building over
  a named canyon. You race there, watch from the ledge, take first pick of the
  fresh-mud salvage. *Trade: the most Jawa and the best loot — but it's an offer;
  a player can decline it and never see the flood.*
- **(b) The road catches you.** Your first caravan through the canyons gets stopped
  by ringing chimes — climb or drown, then watch. *Trade: guaranteed and it
  happens TO you, the scariest version — but it hijacks a caravan mid-errand,
  skips the quiet build-up, and needs you to travel at all.*
- **(c) The Farmer's gallery.** A Moisture Farmer homestead invites you onto their
  high walls to watch, naming each sign as it comes. *Trade: the safest seat and
  the best teacher, and it opens the Farmer relationship — but it's a guided tour,
  the least frightening, and also declinable.*
- **(d) Layered: offers first, road as backstop.** (a) and (c) are offered; if
  both lapse, the next road crossing fires (b). *Trade: the guarantee without
  forcing anyone's hand — but it's the most build (all routes exist), and the
  backstop can land mid-errand at a bad time.*

### CARD 2 — HOW HARD IS THE GUARANTEE
- **(a) Hard: the plot routes an early errand through the canyons**, so the
  backstop trigger is certain. *Trade: every campaign truly sees it — but one
  early destination is now fixed for every player.*
- **(b) Soft: offers escalate but nothing reroutes the campaign.** *Trade: the
  campaign stays free — but a stay-home player can technically miss the flood,
  and the item says "at least once."*

### CARD 3 — CAN THE FIRST WITNESSING KILL
- **(a) Real stakes:** the ledge is safe but nothing else is — pawns and animals
  left on the floor at the wall die for real. *Trade: the dread is honest and the
  lesson sticks — but a first-time player can eat a loss at a scripted event and
  resent it.*
- **(b) Staged-safe first time:** the script arranges that a prudent player cannot
  lose anyone at the guaranteed viewing; danger is fully live only in natural
  floods after. *Trade: no unfair first loss — but a disaster that visibly pulls
  its punch teaches less fear.*

### CARD 4 — WHEN IN THE CAMPAIGN
- **(a) Early (first act):** the flood is the world mechanic's teacher — you meet
  the growth from a ledge before it ever happens near home. *Trade: maximum
  teaching value and early-economy fit — but spent early, it can't be saved as a
  mid-game showpiece.*
- **(b) Mid-campaign set piece:** fires when stakes and colony scale are bigger.
  *Trade: a grander moment landing on a stronger colony — but players may meet
  water-soaked growth at home first, unwarned, which defeats the item's point.*

### CARD 5 — DOES WITNESSING UNLOCK THE WARNING
- **(a) Knowledge is real:** the home-map "your plant has reached the tell" alert
  only exists after you've witnessed the flood (or a natural surge). *Trade:
  witnessing genuinely grants something — but a player who somehow meets growth
  first gets no alert, once.*
- **(b) Knowledge is flavor:** alerts always fire; witnessing grants letters,
  loot, and contacts only. *Trade: nobody is ever unwarned — but the reward for
  witnessing is thinner.*
