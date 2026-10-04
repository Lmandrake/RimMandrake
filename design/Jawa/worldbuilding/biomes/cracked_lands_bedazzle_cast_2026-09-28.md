# The Cracked Lands — bedazzle cast bible (movement 4: commission)

**Item:** FLOODEDCANYON_BEDAZZLE_SITTING_1 · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1
**Date:** 2026-09-28 · **Author:** DESIGN subagent (Fable)
**Slate:** owner full-accepted (volley turns 2–4 + final, ledger notes on the item).
**Biome:** `RM_FloodedCanyon`, labelled "the Cracked Lands"; full rename to CrackedLands
is `CRACKEDLANDS_FULL_RENAME_1`'s scope, not this document's — current names ship.

## RM_Muttavaq — the pan giant

**The Sealed band's logical extreme, and the biome's set-piece decision.** A canyon-floor
giant that sleeps for YEARS under a clay pan the player reads as terrain: a low mounded
polygon field slightly out of pattern — the polygons a touch too regular, the mounding a
touch too high, the cracks radiating from a center the way dried clay never does. Walk the
famous cracked-pan flats and you walk on sleeping animals; walk THIS pan and you walk on
one animal. The Farmers know every muttavaq pan in their reach by name and route around
them; a newcomer farms on top of one.

**Wake.** The flood wakes it wherever the water reaches — the built
`CompWaterWakeTrigger` family (`RUT_CompWaterWakeTrigger.cs`: terrain-turns-to-water
trigger calling straight into the stock `CompCanBeDormant.WakeUp()` path, wake state
Scribed) is exactly this mechanism at sleeper scale; the muttavaq is the same comp on a
body two orders of magnitude larger. Awake, it spends the flood-weeks **feeding as a
walking weir**: wading the wet canyon floor, straining mud and carrion and the irqit
carpet through its jaw-plates, re-cutting the floor as it goes (FlowWorks depth edits on
its trail — the terrain-writer is the mechanics item's C#, not this document's). At the
dry, it digs in wherever it stands, seals its burrow-lining, and becomes terrain again —
somewhere new.

**Danger frame: neutral but unstoppable.** It never hunts, never raids, never
manhunters. It also never stops: walls, crops, buildings and pawns on its feeding line
are things it walks through, and its wake is a FlowWorks event, not a combat one. The
player's decisions are all placement decisions: quarry a sleeping fortune and answer for
it (killing one asleep is easy and shameful, and yields a fortune in crack-wax and meat —
its burrow-lining is the planet's largest single crack-wax deposit), or farm around a
thing that will someday stand up under the barn.

**Stats sketch** (FOUNDRY calibrates; the frame is Middenshell-class):
`baseBodySize ~5.0`, `baseHealthScale ~12`, `MoveSpeed ~2.0` (it does not need to be
fast), `manhunterOnDamageChance 0` awake and asleep — damage while waking it is answered
by the wake itself, not by rage. Wildness 1.0, untrainable, `lifeExpectancy` in
centuries. Butcher/kill yield: meat at giant scale + a large `RUT_CrackWax` drop (the
wake-drop mechanism already ships on the sleeper; the muttavaq's is the same drop scaled
up). Not a pack/herd animal — one per pan, pans rare.

**Marked by:** the out-of-pattern pan (sleeping); the wet-season silhouette of a hill
that wades (awake); its trail — a fresh-cut channel of churned wet clay that was not
there before the flood.

## RM_Uttaqar — the rock troll, ported as ours

**Port of `DA_RockTroll` (Dinonysus's donor mod), taken as OURS with the donor's read
honored.** The donor def (read this pass from the installed mod, `1.6/Defs/ThingDefs_Races/
Animal_RockTroll.xml`): *"a colossal, eyeless creature often found living in caves and
underground chasms… will only surface from its underground lair when provoked. Lacking
regenerative abilities, the rock troll makes up for it through a strange process known as
self-petrification. Any open wound will almost immediately be closed by ultra-fast blood
clotting that ossifies soon after, creating dense stone-like formations that provide the
beast with temporary ablative armor."* Donor numbers, which the port keeps as its
baseline: `baseBodySize 4.5`, `baseHealthScale 10`, `MoveSpeed 3.5`,
`manhunterOnDamageChance 1.0`, armor 1.2 sharp / 0.7 blunt / 0.8 heat, `MarketValue
5300`, `lifeExpectancy 750`, trainability Intermediate, hediff `DA_BloodPetrification`
(five severities). The donor even ships a dormant-disguise cousin mechanic —
`DA_HibernatingRockTroll`, spawned as a *"strange stone formation"* — which the port
keeps in spirit: an uttaqar at rest against a crag wall reads as rockfall.

**Re-voiced in our register.** In the Cracked Lands the uttaqar is the crag-walls giant
against the muttavaq's pans — **the two giants never share a band**: the muttavaq owns
the flats and the flood-floor; the uttaqar owns the walls, the talus, the slot-canyon
dark and the chasms under them. It is the biome's answer to what lives where even the
seep does not reach: a thing that eats stone-dwelling life and minerals, needs no water
the cracks don't already hold, and treats its own wounds as quarry — every fight it
survives leaves it more stone than flesh. Old uttaqar are effectively walking petroglyphs,
seamed with ossified wound-stone in layers a Farmer can read like tree rings.

**Port shape:** our own ThingDef + PawnKindDef `RM_Uttaqar`, our own art (this
commission), the self-petrification hediff rebuilt as `RM_` (mechanics item); the donor
def leaves the roster (`CRACKEDLANDS_RULED_CONTENT_1` step 4). **Label ships as "rock
troll"** — *uttaqar*-as-label is a batch-4h DRAFT the owner passed on twice; current
names ship, the defName carries the invented word per the commission.

**Marked by:** the eyeless head; the wound-stone seams; a "rockfall" at the crag base
that was not in yesterday's survey.

## RM_Irqit — the mudflat breeder

**The Spenders' missing core, made real** (§10: *"mudflat breeders, a sudden carpet of
small frantic life"*). Palm-sized, soft-bodied, quick — the irqit exists as eggs in the
dry clay for years, then the recede turns every flood-touched cell into a nursery: a
sudden CARPET of small frantic life between the roar and the dry. Each irqit breeds
exactly once, lays into the wet clay, and dies as the mud stiffens — a living calendar of
the flood, and the reason the fliers commute in (§4's ruling seen from below: the irqit
carpet IS the feeding run). The muttavaq strains them by the thousand; the gornt and the
fang leaf take the stragglers at the seep; the vultures take everything that misses the
timing.

**Mechanism:** spawned as a cohort on the flood component's soaked-cell list at recede
(the list exists — slate H already planned placement off it), aging on a fast lifecycle
clock; at dry-out the cohort dies where it stands, leaving small meat/carrion. No
year-round population: outside flood-weeks the biome shows zero irqit and that is
correct, not a defect.

**Stats sketch:** `baseBodySize ~0.12`, herd-spawning, `MoveSpeed ~4.5`, wildness 1.0,
no manhunter, trivial combat stats — its defense is number and calendar. Tiny meat
yield; the point of hunting it is that for two weeks it is free food carpeting the floor.

**Marked by:** the carpet itself — motion where the biome's rule is "none, then the
flood"; drying windrows of spent irqit at the flood line afterward.

## RM_Tarruq — the voice

**The biome heard, in fauna form** (mark 7's fauna half). A crack-dweller at the seep
line — a lean, long-limbed climber built for the vertical dark — whose territorial calls
resonate down the crack network: long low tones the canyon carries for hundreds of
meters, each animal answering its neighbors down the line. On an ordinary day the
Cracked Lands' soundscape is wind, then tarruq, then wind. **It goes silent when the
cracks begin to fill** — the seep-water rising through its galleries drives it up and
mute — and that silence is the biome's living second warning, arriving BEFORE even the
chimes: an experienced Farmer trusts the ground (the ticking flats), then the tarruq
hush, then the chimes, then runs. The warning ladder the sheet's §9 smell-then-tick
sequence began now has its middle rung.

**Mechanism:** an ambient call (SoundDef, slate E's pipeline) keyed to tarruq presence,
gated OFF by the flood map component's pre-chime phase — one boolean read on machinery
that exists. The silence costs no C# beyond the gate.

**Stats sketch:** `baseBodySize ~0.45`, `MoveSpeed ~4.8`, agile, shy (high wildness, no
manhunter — it answers threat by going vertical), modest predator diet (crack-life,
irqit stragglers, eggs). Year-round Patient-band resident; commonality low enough that
hearing one is common and seeing one is an event.

**Marked by:** the call; the hush; claw-polished runs down the slot walls at the seep
line.

## RM_Veqma — the dowsing flora

**The Farmers' first survey instrument, growing wild** (marks 2+3 support; §11's dowsing
craft in flora form). A wiry, near-leafless plant of the shade line — mostly taproot,
the visible plant a sparse fan of grey-green whips — whose root finds the hidden water,
and whose **tip blushes green in proportion to how near the water table sits**. A stand
of veqma is a contour map: dull grey where the water lies deep, brightening cell by cell
toward the seep, vivid green directly over a find. Reading a veqma field is the first
thing a Farmer teaches a child and the first thing the survey loop (below) teaches a
player.

**Placement law:** grows ONLY on the shade line — ban 2 (*"no green outside the shade
line"*) is respected by placement, not exception. A veqma on open sun-flats is a
linter-catchable violation.

**Mechanism:** graphic tint (or small variant set) keyed to the survey component's
hidden-water proximity score for its cell — the same score the dowsing ladder reads, so
the plant IS the UI. Wild-sown at low commonality in the shade band; not farmable (its
value is where it grows, not what it yields — harvest gives a little herbal/raw
plantmatter only).

**Marked by:** the blush gradient; a vivid-green stand is worth a survey flag on sight.

## The Swale (RM_Swale) — the seep canal

**Owner's own addition (volley turn 2), named THE SWALE at turn 4.** A FlowWorks canal
variant, intentionally graded and **perforated**: while it carries water, it deliberately
loses some of it sideways — the water seeps into the surrounding ground, and **adjacent
cells climb in fertility** for as long as the swale runs. The trade is the design: a
sealed `RM_Channel` delivers everything downstream; a swale delivers less and farms its
own banks on the way. A homestead ringed by green swale-lines is the Cracked Lands'
signature of wealth.

**Tier law (owner-ruled, turn 4):** the swale is a **normal buildable in FlowWorks**
(`RM_` tier — any RimWorld world gets it with the mod), but **in the Utinni campaign it
is LOCKED and must be discovered as an unlock from this biome** — the mark-2
discoverable technology, confirmed shape. Build implementation rides the FlowWorks
channel family (`RM_Channel_*` defs + the fill terrains); the perforation is a fertility
write on adjacent cells while the fill terrain is wet — mechanics item's C#.

**The discovery loop — reworked for TRANSIENT gravship players (owner, turn 2).** The
original A/B ladder assumed a settled colony accumulating dowsing reads over years; a
gravship player stays a while and leaves. The loop is now **per-visit shaped**, with one
durable prize:

1. **Read the land** (one visit's work): veqma blush gradients, Sealed-sleeper cluster
   density (living dowsing rods, §10), crack-wax finds, tarruq territories. The survey
   component scores cells from things already placed — zero new liquid code.
2. **Complete a survey** → a **discovery survey item** naming a real hidden-water site
   on THIS map. Per-visit payoff, spend it either way before you leave:
   **sell it** (§11's "exceptionally valuable thing to sell" — the Farmers pay
   handsomely for fresh data), or **dig it**: a cistern head at the site — a FlowWorks
   water source that yields slowly between floods, refills at each flood, and wants a
   crack-wax lining or it loses a share to seepage. The cistern serves the stay and
   remains on the map as the player's mark on the biome.
3. **The durable prize:** the first completed survey **unlocks the swale for the
   campaign** — the one thing that leaves on the ship. The player didn't find water;
   they learned how the Farmers make ground grow, and that knowledge works on any map
   with a FlowWorks line. Dowsing reads (veqma tint, sleeper-cluster overlay) also stay
   visible once earned.

So a transient player's arc is complete in one stay — read, survey, sell-or-dig — and
the biome still changes their game forever. **No wax tank** (owner, final: dropped); the
crack-wax loop closes through the cistern lining and the wax suit instead.

## Fossils — the canyon-wall strata

**Owner's own addition (volley turn 2, uncontested at turn 4): the canyon walls are
FULL of the dead — something special.** The flood has been cutting this country for
geological time, and the walls are the ledger: **fossil-bearing strata** ship as
mineable defs seeded in canyon-wall generation (RockBase-family mineables, the
Greatbole-Heartwood pattern — a wall cell the player can see is different and dig).
Mining a seam yields the fossil item family:

- **Common impressions** — fern-mats, shell-beds, trackway slabs; modest value, stack
  well, honest trade goods and a beauty bump raw.
- **Articulated skeletons** — rare; a whole small animal in the stone; serious value
  and the centerpiece tier for display.
- **Deep-stratum uniques** — the quest-grade tier, found only deep in the walls or
  where a flood has cut a fresh face; each one a named, one-off piece.

**The flood re-cuts the ledger:** after each flood, the map component converts a few
flood-scoured wall cells to FRESH exposed seams — the recede is a mining opportunity as
well as a farming one, and the salvage-strike rhythm (§12's Jawa face) gets a geological
verse. Post-flood, walls near the water line are worth walking.

**Display furniture:** a mounted-display family (sculpture-shaped: quality-bearing,
beauty-scaled by the fossil tier mounted) — the wall slab, the free-standing skeleton
mount. A Farmer homestead with a mounted deep-stratum piece over the door is saying
something; so is a gravship galley with one bolted to the bulkhead.

**The quiet lore line (owner's "something special", kept quiet on purpose):** the deep
strata hold **pan-giants** — articulated sleepers the size of a muttavaq and larger, in
layers older than the canyons themselves, some still curled in the seal position. The
pans have been sleeping here a very long time; not all of them woke. No tooltip says
this outright — the deep-stratum unique descriptions let the player assemble it.

## The wax suit — crack-wax sealed underwater suit

**Owner's final ruling of the volley: crack-wax makes SEALED UNDERWATER SUITS.** The
Sealed sleeper survives years underground behind a crack-wax membrane; the Farmers
line cisterns with the same material; the suit is the third use of the one substance —
a full-body sealed apparel piece, crack-wax over a stiffened frame, that lets a pawn
**survive water and underwater TERRAIN**: working flooded slot-canyon cells during the
flood-weeks, crossing and working the biome's 27 measured open-water tiles (the
planet's ONE lethal water, freeze ruling R6 — the suit is how a pawn survives standing
in it), and hidden-water digs — cutting into a seep gallery or a drowned cistern
without drowning in the attempt.

🔴 **Terrain survival ONLY — stated in the def, the doc and the review.** The suit
grants survival on water/underwater TERRAIN a pawn can already path to. It grants **no
sea-floor access**: sea-floor maps remain **ship-only** (owner, 2026-09-26, verbatim:
*"You can't 'dive' as an individual pawn nor return as one. It's ship or nothing."*),
there is **no pawn dive verb, mechanism or menu option anywhere in this feature**, and
`RM_SeaDiveHatch` remains the single way onto a sea floor. This is the same
reconciliation `WARCASKET_SUIT_CLASS_1` carries: an apparel class may make hostile
terrain survivable; it may never become a travel mechanism. A future reader who finds
this suit and thinks "so pawns can dive now" has it backwards — see
`CRACKEDLANDS_RULED_CONTENT_1` step 6.

**Item shape:** apparel, shell layer + full body coverage, crafted from `RUT_CrackWax`
(+ fabric/frame component), heavy move/work penalty appropriate to a sealed suit,
modest armor. The stat/hediff mechanism that reads "this pawn survives water terrain"
is the mechanics item's; the reconciliation line above binds it whatever the mechanism.
Utinni-side the recipe is discovered here (crack-wax is this biome's material); the
RM_ tier ships it with the biome mod per the standing Q11a face rule.

## Roster wiring summary

Executable summary — the build ticket is `CRACKEDLANDS_RULED_CONTENT_1`; wildAnimals /
wildPlants use the **shorthand element form** (`<DefName>commonality</DefName>`),
never `<li>` (a `<li>` silently discards the whole entry).

**OUT — the vanilla terrestrial zoo** (owner, turn 2: *"remove all terrestrial
(vanilla Earth) life from the roster as usual"*). `RM_FloodedCanyon_Biome.xml`'s
inline rows all go: Iguana 1.0, Dromedary 0.4, Fox_Fennec 0.3, Warg 0.15, Rat 0.6,
Cougar 0.06 — and the inline vanilla flora (Plant_Grass, PincushionCactus,
SaguaroCactus, Agave, Bush, Dandelion) goes with it, replaced by the owned flora set.
`animalDensity`/`plantDensity` stay explicitly set after the eviction.

**MIGRATES to owned RM_ defs — reusing existing art, queue nothing** (Q11a: the free
mod looks the same as the campaign one; Q12–Q15 per-sitting migration):

| current def | band | note |
|---|---|---|
| `RUT_SealedSleeper` 0.2 | Sealed (signature) | also fix: today missing from the RM_ patch entirely |
| `RUT_EmperorVulture` 0.15 | Patient (sky) | real flight; also missing from the RM_ patch |
| `RSW_SandLeaper` 0.2 | Spenders | invented exotic, not canon |
| `RSW_SandPillar` 0.5 | small | invented exotic |
| `RSW_Creature_Mantrap` 0.15 | Patient | **the Fang Leaf relabel lands here — verified this pass against both defs' own descriptions.** Both cite the Venus flytrap, so ancestry does not discriminate; FORM does: this one is *"proto-feet… can move very slowly"* at spd 0.15 — a near-stationary lure predator that reads as a plant. The Miasma's `AA_Mantrap` (Alpha Animals) is the engineered war-animal form — bs 2.0, mobile, *"concentrated formic acid spit launchers"* — and keeps its label; it is that biome's business. New label here: **fang leaf**. defNames untouched. |
| `RSW_MutagenicNorphea` 0.4 | Sealed | label ships as-is (batch-4h *qattora*/*norphea* DRAFT) |

**NEW natives** (this document, art this commission): `RM_Muttavaq` (pan giant),
`RM_Uttaqar` (crag giant — donor `DA_RockTroll` row leaves, ours replaces),
`RM_Irqit` (Spenders), `RM_Tarruq` (Patient), `RM_Veqma` (flora).

**OFF the roster, onto the roads:** `RSW_Eopie` — owner, turn 2: common beasts have
**one native biome** and TRAVEL to the others; the eopie leaves this roster (and its
other guest rosters at their own sittings) and arrives with merchants — trader stock /
caravan pack-animal availability instead of a wild row.

**STAYS — canon on the RSW_/Utinni layer:** `RSW_Gornt` 0.3, the two fliers
`RSW_CanCell` 0.2 / `RSW_Convor` 0.2 — owner, turn 4: the fliers are **guests and
migrants** here under the migration carve-out (they nest in the Desert, ban 4 holds);
and `RSW_Woolamander` 0.15 as a **walking resident** — owner, 2026-10-03: follow canon
(arboreal, no flight). Donor rows `AA_Murkling` 0.2 / `AA_SandSquid` 0.1 stay
inline per the standing donor-fauna acceptance.

**Names:** batch-4h renames (qattora, qetta, saqqat, luttaq, uttaqar-as-label) remain
DRAFT — owner passed twice; **current names ship**, and only the ruled Fang Leaf
relabel applies. The full FloodedCanyon→CrackedLands rename is
`CRACKEDLANDS_FULL_RENAME_1`, gated on its own live-tile/savegame check.

---

*Art register for everything above (sheet §9): cracked clay grey-white, red-brown
flood stain, moss green only in the blue slot-shade, the hardest light contrast on the
planet — dry then sudden. Queued this sitting in
`infrastructure/artpipe/art_lists/cracked_lands_bedazzle_cast.csv`.*
