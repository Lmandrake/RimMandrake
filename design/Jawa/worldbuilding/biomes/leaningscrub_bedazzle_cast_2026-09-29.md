<!-- status: cast bible — commissioned under LEANINGSCRUB_BEDAZZLE_SITTING_1 movement 4 -->
# Leaning Scrub — bedazzle cast bible (movement 4: commission)

**Item:** `LEANINGSCRUB_BEDAZZLE_SITTING_1` · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1 (row 7)
**Date:** 2026-09-29 · **Author:** movement-4 commission agent (Fable)
**Feeds:** `LEANINGSCRUB_RULED_CONTENT_1` (defs) + `LEANINGSCRUB_MECHANICS_BUILD_1` (wind spine)
**Authorities:** `leaningscrub_bedazzle_review_2026-09-29.md` (the review; volley CLOSED),
both tickets above (every ruling below is fixed), the frozen sheet `arid_shrubland.md`
(voice only — never edited; ⚠️ `desert.md` is the Long Shade, a different biome).
Mod: `src/RimMandrake/LeaningScrub/`.

## 0. Shared law — every card obeys this without restating it

- **Voice:** the hush, and the lean. Knee-high silver-green fuzz to every horizon, all of
  it leaning the same way, all of it moving, because the wind never stops. Two floors that
  cannot see each other: the giants' floor above the canopy, the runway floor beneath it.
  No rain — fog on the ground-wind, thinning sunward. The wild has no voice, only posture.
  Descriptions talk ecology: runs, wakes, crossings, the quincunx, the sweetline.
- 🔴 **Trim law (owner, final ruling, carried on every entry):** *"Too much focus on
  constant advanced warning... Players arent that into it."* Ecology, not tactics — no
  alarm framing, no sentinel framing, no warning-instrument flavor anywhere below. A
  creature may be *noticed*; it is never built or described as a warning product.
- **Name register (ruled, mixed):** English compounds lead (thunderstep, yanker,
  fuzzrunner, thornhold), coined names mixed in as the owner admitted them (shokka,
  zellik, surrik, tikkit, vissler).
- **Art register (the Leaning Scrub house style for every job below):** a knee-high
  scrubland under a low, fog-softened sun that never rises or sets — the last ten minutes
  of a sunset that never ends; silver-green fuzz banding grey darkward and waxy gold
  sunward; everything leans one way. Realistic painted natural-history illustration,
  grounded believable anatomy, matte surface texture, never cartoonish, never cute, no
  outlines, alien but biologically plausible. Faced jobs: north is a **true rear view from
  directly behind — no eyes, no face, no frontal features.**
- 🔴 **Palette diversity is LAW on this cast** — owner, verbatim, carried in every
  style_notes: *"Your color palette is too uniform per biome. Needs more variety."*
  Each subject below carries its OWN palette anchor, deliberately distinct from its
  castmates; the silver-green room is where they stand, not the paint they wear.
- **Hard bans from the frozen sheet ride every prompt:** no rain and nothing rain-slicked;
  no dense flora except venomvine (the quincunx law); flora reads fire-resistant, never
  dry-tinder; the size ladder holds (small / medium ≤1.4 / large VOID / huge).
- **One home.** Every fill and menagerie member is Leaning Scrub-only (owner law
  2026-09-21).
- **Numbers are design proposals** — FOUNDRY calibrates in the build tickets; the
  relationships (who hunts what, which floor, what the wind changes) are the ruled part.

## 1. Name sweep (MEASURED this pass, 2026-09-29)

All cast names were swept clean 2026-09-28 at the sitting (probe korrum 70) — not
re-litigated. Re-swept here: only ids coined by THIS pass. Instrument:
`git grep -il <name> -- src/ design/ infrastructure/state/`. **Sanity probe: `korrum` →
72 files** (instrument proven able to see).

| name | files | verdict |
|---|---|---|
| `VisslerArm` | 0 | CLEAR — coined this pass (the shed-arm lure item) |
| `DrippingVenomvine` / `HollowVenomvine` / `CrownVenomvine` | 1 each | CLEAR — the hit is the ruling ticket itself |
| `TwitcherVenomvine` | 2 | CLEAR — ticket + mechanics ticket |
| `Fuzzrunner` / `Thornhold` / `Zellik` | 3 each · `Shokka` 2 | CLEAR — this sitting's own commissioning prose only |

## 2. Art dedup (standing owner law — searched before queuing anything)

Instrument: filename census over `infrastructure/artpipe/` `done/` + `pending/` +
`active/` + `failed/` + `_artsrc/`, content search of `registry.jsonl` and all
`Transient/*.decisions.json`. **Sanity probes: `korrum` → 6 in done/, 2 decision hits;
`imperialtoad` → 6 in done/, 21 registry hits; `fuzz` → 2 in done/, 19 registry hits**
(the instrument sees).

- **Empty everywhere — genuinely owed, queued below:** all 4 fills, all 9 menagerie (+
  the vissler arm item), all 4 fuzz flora, all 4 venomvine forms, the fresh thicket base
  (§6's verdict), thunderstep/shrublandgiant, yanker/tunnelsnake/klorslug, scrapnestbird,
  blurrg. Every one: 0 in done/, 0 in _artsrc/, 0 registry lines, 0 decisions.
- **Found and NOT queued (wire or nothing owed):** `rutfuzz_v1`, `rut_grellbush`,
  `rut_grellspine`, `rut_wildhealroot` (each: full set in done/ + _artsrc/, ~19 registry
  lines) — the review's wire-only five; plus **35 of the 39 donor-reskin cast members
  already own finished regens** (§7's table — e.g. `desert_swaca_bantha`,
  `canon_whisperbird_v1`, gizka 28 done-files, mossbeetle 18). Re-queuing any of those
  would throw finished, ruled work away.
- **`fambaa_v1` exists (3 facings, done) but is NOT thunderstep cover:** its own prompt
  says *"Star Wars canon Fambaa, the Gungan war beast"* (`CREATURE_ART_REVIEW_SHEET_1`) —
  canon Fambaa art, not our invented giant. Thunderstep still queues.
- **`rmvenomvine_v1` exists and FAILS the showpiece bar for this biome** — verdict and
  evidence in §6.

## 3. Cast entries — the four fills (grounded sprites only)

### RM_Fuzzrunner — the runway nation's staple

**Ruled frame (fixed):** small (~0.2 band), the prey base of the whole interface — a
fog-fat tunnel-hare that never stands in open light; worn runs under the canopy; freezes
when the wind dies. The free tier's first animal.

**Description (in the biome's voice):**

> Nothing on the plain is more common and nothing is harder to see. A fuzzrunner is born,
> fed, bred and dead without once standing in open light — its whole nation lives in the
> worn runs under the canopy, navigated by smell and whisker, walls of stems polished by
> ten thousand shoulders before it. It is round with fog-fat against the lean days, and
> when the wind falters it stops mid-stride and becomes a stone until the canopy moves
> again. Dig where the runs cross and you can live here. The locals do.

**Silhouette/palette brief:** a plump, low-slung tunnel-hare — big hindquarters for the
sprint, small tucked ears (a corridor animal, nothing tall), whiskered blunt muzzle,
mid-lope posture low to the ground. **Palette anchor: FOG-SILVER** — pale silver-buff coat
with a damp grey underside and darker spine-line, the one animal painted the canopy's own
silver so the read is "the fuzz moved". Not cute; workmanlike, watchful.

**Facings:** south, east, north (north = true rear: haunches and spine-line, no face).
Canvas 256. **drawSize intent: ~0.8**, bodySize ~0.2; herbivore, herd-common (the
biome's staple prey), tameable.

### RM_Thornhold — the venom nester that forbids

**Ruled frame (fixed):** small (~0.4 band), venom-armed; forbids rather than flees —
incarnates the frozen sheet's own "thornhold nesters", denning inside venomvine where
nothing big can follow.

**Description:**

> Most small things on the plain answer trouble by running. The thornhold answers it by
> refusing. It dens in the venomvine stands, threading galleries nothing larger can
> follow, and it meets whatever reaches in with a lash of venomed quills and no
> negotiation. A thornhold does not flee its nest, ever — trappers say you can dig one
> out with a shovel and it will still be facing you when you get there. Handled young,
> they extend the same stubbornness to a homestead's walls.

**Silhouette/palette brief:** a compact, armored nester — broad low body behind a blunt
braced head, a mantle of erectile quill-thorns half-raised along back and flanks, short
planted legs (built to hold ground, not cover it). **Palette anchor: BONE-AND-VENOM** —
pale bone-tan plating and quills tipped dark dried-blood umber, echoing the venomvine it
dens in; a dark eye-stripe the only face marking. Reads stubborn, not fierce.

**Facings:** south, east, north (north = true rear: the raised quill-mantle from behind,
no face). Canvas 256. **drawSize intent: ~1.0**, bodySize ~0.4; venomous melee, dens in
thickets, tameable late.

### RM_Shokka — the crossing pouncer

**Ruled frame (fixed):** medium 1.2 — the edge-pouncer of the fog-shadow barrens, the
first of the sheet's three predation routes ("ambush where a runway is forced to
surface") finally incarnated. Pelt is the local camouflage weave.

**Description:**

> Every runway has to surface somewhere — a fog-shadow behind a shrub, a farm's pale
> wake, ground too dry to grow cover — and the shokka owns those crossings the way a
> ferryman owns a river. It lies flat in the last of the fuzz with its dappled pelt
> matching the barrens beyond, and it does nothing at all, sometimes for a day, until
> something small commits to the open. Locals butcher one warily and waste nothing: the
> pelt takes dye badly and light beautifully, and a coat of it is the closest a person
> gets to being hard to see out here.

**Silhouette/palette brief:** a long, low ambush cat-analog held flat in a pounce-crouch —
shoulders below hip line, big forepaws, a wide flat skull with low-set eyes, tail a
counterweight held straight back. **Palette anchor: BARRENS-DAPPLE** — pale dust-gold
ground with broken waxy-buff dappling and a chalk-pale belly: the palette of the dead
wake, not the living fuzz; deliberately the warm pole of a cast painted mostly cool.

**Facings:** south, east, north (north = true rear: flattened shoulders, straight tail,
no face). Canvas 256. **drawSize intent: ~1.7**, bodySize ~1.2 (medium ceiling law: <1.5);
ambush predator, rare-ish.

### RM_Zellik — the stall-hawk (TRUE FLYER, grounded sprite only)

**Ruled frame (fixed):** medium 0.9, REAL 1.6 flight (`MaxFlightTime` stats, Locust
shape). It hunts by reading the canopy: useless in wind, lethal when the wind dies and
every movement under the fuzz shakes a still roof. 🔴 **Flight flip-book frames are NOT
commissioned now** — the flyer law says never block flight on frames; a frameless flyer
flies with no wing-beat, correct behaviour, plainer look. Frames are a named follow-on
(§10).

**Description:**

> On an ordinary day the zellik sits hunched on a sweetline bough or a turbine head and
> looks like a folded umbrella nobody wants. The wind that feeds everything else starves
> it: a shivering canopy tells it nothing. Then a cyclone far over the horizon swallows
> the Hadley flow, the wind dies, the plain goes still — and the zellik goes up. Over a
> stalled canopy every footfall underneath is a ring on a pond, and it drops through the
> roof onto things that believed, until that hour, that the roof was theirs.

**Silhouette/palette brief (grounded):** a tall, hunched wind-hunter at rest — long wings
folded and drooped past the tail like a closed umbrella, a lean keeled body on strong
tarsi, a flat wide-eyed face built for reading texture at distance, posture patient and
slightly wrong. **Palette anchor: SLATE-AND-GLARE** — dark storm-slate mantle over a pale
fog-white underside (invisible from below against the bright haze), one waxy-gold ring
around each eye as the sole hot accent. The cast's cold pole.

**Facings:** south, east, north (north = true rear: the folded wing-drape from behind, no
face). Canvas 256. **drawSize intent: ~1.6 grounded** (the folded wings carry the size),
bodySize ~0.9; predator band, rises with the Stall (mechanics own the wiring).

## 4. Cast entries — the nine menagerie

All nine ruled at the sitting (swept clean 2026-09-28, probe korrum 70). One home each.
Compact entries; the shared law of §0 rides every one.

### RM_Fuzzviper — the run-ambusher

> The runs are safety, and the fuzzviper is the price of believing that. It lies along a
> tunnel wall being a root until the run's own traffic comes to it.

**Silhouette/palette:** a thick-bodied short snake-analog, coiled S-posture, head flat
against the ground; **anchor: CANOPY-MIMIC** — exactly the fuzz's silver-green with
stem-shadow banding, the one cast member deliberately painted the room's own colour (the
point of it). Facings south/east/north (north = dorsal coil from behind). Canvas 256.
drawSize ~0.9, bodySize ~0.3; ambush predator of the runs.

### RM_Surrik — the crust-swimmer

> Below the runs there is one more floor. The surrik swims the root-bound crust itself,
> shouldering through the mat like water, and takes what it takes from underneath.

**Silhouette/palette:** a blunt-headed, thick-necked burrowing snake-analog surfacing
chest-up through cracked crust, tiny useless eyes, polished scales; **anchor:
LOAM-DARK** — deep root-brown body with a pale crust-dust back where it wears the
ground, root-pale belly. Facings south/east/north. Canvas 256. drawSize ~1.0, bodySize
~0.5; subterranean predator, surfaces to strike.

### RM_Ribbonwhip — the canopy-top thread

> The thinnest predator on the plain never touches the ground: a ribbon the width of a
> stem, riding the top of the canopy, moving when the wind moves so nothing reads it.

**Silhouette/palette:** an impossibly slender thread-snake laid in a long shallow wave
across the canopy top, head barely wider than the body; **anchor: WAXY-GOLD** — sunward
waxy gold with a silver sheen down the flank, bright against the cast, matched to the
sunward band of the fuzz. Facings south/east/north. Canvas 256. drawSize ~1.1 (length,
not mass), bodySize ~0.25; takes flutterers and nestlings off the canopy top.

### RM_Vissler — the brittlestar of the runs (+ the shed arm)

> Grab a vissler and you are holding an arm. The rest of it is already gone, and the arm
> is still moving — twitching in the run with a will of its own, and everything hungry
> comes to the twitch. It regrows the arm in a season. Hunters buy them.

**Silhouette/palette:** a five-armed ground brittlestar, central disc low and armored,
arms long and jointed like braided whips, one arm visibly regrowing (shorter, paler);
**anchor: LICHEN-GREY over EMBER CORE** — dry lichen-grey armor plates, joint-lines
glowing faint ember-orange where the living core shows. In the Gale, visslers interlock
into star mats — the sprite is ONE animal; the mat is a spawning behaviour, not this
job. Facings south/east/north. Canvas 256. drawSize ~0.9, bodySize ~0.15.

**RM_VisslerArm (item, single):** the shed arm as a harvestable hunter's lure — a curled,
jointed whip-arm, lichen-grey plates with the ember joint-glow fading toward the broken
end. Item icon read: unmistakably a piece of the animal, still coiled with intent.
Canvas 256, single. (Lure mechanics ride the build ticket, not this commission.)

### RM_Dustflutter — flight as displacement

> Walk the fuzz and the ground ahead of you bursts — a hundred dustflutters up in one
> grey shiver, over your head, and down again forty paces on. They cannot really fly.
> They can only be somewhere else.

**Silhouette/palette:** a palm-sized round-bodied flutterer, wide soft moth-like wings,
almost no tail, mid-burst posture with legs still trailing; **anchor: MOTH-DUST** —
ash-buff body, fog-white wing undersides that flash as the flock turns, faint dark
wing-root crescents. TINY `MaxFlightTime` — flight as displacement, not travel; frames
are the same named follow-on as the zellik's (§10). Facings south/east/north. Canvas
256. drawSize ~0.6, bodySize ~0.08; flock-common, mobs the crown venomvine when the
wind drops (wind-keyed, never day-keyed — ban 3).

### RM_Shirrel — the Gale-glider

> Most of the plain spends a gale hiding. The shirrel spends the year waiting for one.
> It climbs a sweetline tree, opens like a kite, and crosses country in an afternoon
> that would take it a season on foot.

**Silhouette/palette:** a big heavy-bodied glider — cat-sized, a full body-length
gliding membrane furled along the flanks (grounded sprite: membrane folded in loose
pleats), strong climbing claws, a deep-keeled chest; **anchor: STORM-GREY** — charcoal
body with the furled membrane in banded slate and fog-white, like weather rolled up.
Facings south/east/north. Canvas 256. drawSize ~1.2, bodySize ~0.7; rises on the Gale
(mechanics own the wiring), sweetline-tree associate.

### RM_Crustweevil — the lichen grazer

> The crust is a country too. The crustweevil grazes its lichens on a scale of
> centimeters, and the runway nations grow fat on the crustweevil.

**Silhouette/palette:** a domed, long-snouted weevil, legs hidden under the shell rim,
snout down against the ground; **anchor: OXIDE-SHEEN** — near-black shell with an oily
blue-green oxide iridescence, dusted pale at the dome crown. Facings south/east/north.
Canvas 256. drawSize ~0.5, bodySize ~0.05; base of the invertebrate web.

### RM_Rollbug — the run janitor

> Nothing dies in a run and stays there. The rollbug trundles the corridors on a fixed
> beat, packs whatever it finds into a ball bigger than itself, and rolls the runway
> clean back to its larder.

**Silhouette/palette:** a broad flat-backed beetle-analog pushing with its hind legs,
head low, forebody braced (sprite WITHOUT the ball — the animal must read alone);
**anchor: TAR-POLISH** — deep tar-brown chitin polished to a shine on the wear-points,
dull dust film elsewhere. Facings south/east/north. Canvas 256. drawSize ~0.55,
bodySize ~0.06; carrion/waste feeder.

### RM_Tikkit — the click-chorus

> The plain is not silent, whatever the old surveys say — put your head under the canopy
> and it clicks, horizon to horizon, a dry chorus riding the wind. That is the tikkit
> nation talking to itself. About what, nobody has ever needed to know.

**Silhouette/palette:** a slight, long-legged cricket-analog, big-eyed, serrated
click-limbs half-raised; **anchor: DRY-GRASS** — dried-grass tan with dark banding on
the click-limbs and a pale throat. Soundscape richness is the point
(`LEANINGSCRUB_MECHANICS_BUILD_1` §7) — 🔴 NOT a warning device, and its entry text
never frames the chorus as one. Facings south/east/north. Canvas 256. drawSize ~0.5,
bodySize ~0.04; swarm-common, the click-chorus ambient's face.

## 5. Cast entries — the four fuzz flora

All four ban-9 compliant by ruling (fire-resistant living flora — the permanent fix the
roster's own notes said no donor could provide). All single-facing plant sprites;
Graphic_Random variants derive from each master. Every prompt carries the lean: the
whole plant bent the same way, permanently.

### RM_Whipfuzz — the grassy fuzz

> The between-plant grass of the quincunx: thin silver blades that lie almost flat in
> the wind and never stop moving.

**Palette anchor: SILVER-GREEN** — the biome's signature register, carried by exactly
one plant so the rest of the flora is free to differ: pale silver-green blades, darker
at the root, all bent sunward. Sparse, struggling, never a lush tuft (quincunx law —
the gaps are the structure). Canvas 256, single. drawSize ~1.0.

### RM_Pillowmoss — the fog-condenser

> A fat, low cushion that drinks the wind — fog beads on it all day, and the ground
> under a pillowmoss is the only reliably wet ground on the plain.

**Palette anchor: DEEP FOG-GREEN with DEW-SILVER** — the darkest green in the cast,
dense wet-looking pile, beaded with condensed silver droplets on the windward face
(vaporator synergy lives in MECHANICS; the art only shows a plant that drinks fog).
Canvas 256, single. drawSize ~0.8; low dome, leans barely — too low for the wind to
bully.

### RM_Tanglefuzz — the den anchor

> Where a tanglefuzz grows the runs converge: a woody, knotted bush whose root-ball
> holds a hollow, and half the runway nation is dug in under one.

**Palette anchor: DUSKY OLIVE over DARK HEART** — grey-olive foliage over a visibly
woody, near-black knotted core and exposed root-flare (the den mouth shadowed at the
base, readable at zoom). The biggest of the four; still knee-high, still leaning.
Canvas 256, single. drawSize ~1.2.

### RM_Cruststar — the crust lichen

> A hand-span star of pale lichen flat against the root-bound crust, rimmed gold where
> it fruits. The crustweevils graze it like a herd on a pasture the size of a plate.

**Palette anchor: LICHEN-WHITE and GOLD RIM** — chalk-pale rosette, thin waxy-gold
fruiting rim, pressed dead flat (the one plant the wind cannot lean because it has no
height at all). Canvas 256, single. drawSize ~0.6.

## 6. The venomvine five-form showpiece

🔴 **Owner verbatim — this is the art centerpiece:** *"The art for the venomvine should
be especially rich, varied, interesting... its the strange showpiece here."* Five forms,
five entries, five renders — one family, one near-black register, and deliberate
variety inside it.

### The base thicket — verdict on `rmvenomvine_v1`: DOES NOT MEET THE BAR; fresh base QUEUED

**MEASURED this pass:** `rmvenomvine_v1` (done/, facts PASS, wired 2026-09-26 as
`RM_Venomvine/RM_Venomvine_a.png`) was authored for **the desert shade-vine ruling**,
and its own prompt forbids exactly what this biome's venomvine IS: *"a low, matted
tangle... sprawling flat across the ground... nothing stands tall... an ankle-high
thicket rather than a bush... It is a ground-hugging mat, never a standing shrub."*
The frozen sheet's ruling (owner, 2026-09-21) is the opposite: **venomvine stands
man-height or more** — the only vegetation in the biome that does, the reason a thicket
reads as a dungeon and a hedge-fort is a curtain wall. The render also carries a heavy
black outline register the current house style has dropped. It is not a richness
shortfall to iterate on; it is the wrong plant's silhouette. ⇒ **A fresh base
`RM_VenomvineThicket` render is queued**; `rmvenomvine_v1` stays valid where it was
made for (`RM_Venomvine`, the Long Shade ground mat) and comes OFF this biome's
wire-only list. ⚠️ Both defs share one texPath today *on purpose* (each def's header
says so) — FOUNDRY must split the thicket onto its own texPath when the new render
lands, or the desert mat inherits a man-height sprite. Handoff note §11.

### RM_VenomvineThicket — the fortress (fresh base)

> The one plant that refuses the quincunx. A mature stand is a dungeon: near-black
> canes man-height and better, woven too dense to cut, venom on every scratch, and
> everything the plain wants — nests, dens, shade, secrets — locked inside where only
> the small can thread.

**Silhouette/palette:** a standing thicket WALL, not a bush — vertical woven canes
rising past man-height, recurved thorns in ranks, one narrow dark threading-gap
readable low; **anchor: NEAR-BLACK ISLAND** — blackened green-umber canes, bone-pale
thorn tips, the darkest mass in the biome (the sheet's "venomvine as near-black
islands"). Leans sunward like everything else, which on a plant this size reads as
menace. Canvas 256, single. drawSize ~2.2.

### RM_DrippingVenomvine — the overproducer

> Some stands make more venom than their thorns can hold. A dripping stand hangs it in
> amber beads along every cane, and the harvest is real money for whoever works
> bare-headed under a plant that sweats poison.

**Silhouette/palette:** the base thicket form hung with visible bead-strings of venom
along the cane undersides, ground beneath faintly stained; **anchor: AMBER ON BLACK** —
the family near-black plus the cast's one jewel note: translucent amber-gold drops,
lit. (Harvest job → raw venom stock rides `LEANINGSCRUB_RULED_CONTENT_1` §4.)
Canvas 256, single. drawSize ~2.2.

### RM_TwitcherVenomvine — the lash

> A twitcher stand strikes once at whatever comes close — one whip-crack of a cane,
> fast as a snake — and then spends an hour drooping, visibly spent, earning the next
> one.

**Silhouette/palette:** the family form with ONE long lash-cane held cocked in a
drawn-back arc above the mass, the surrounding canes slack; **anchor: GREY-GREEN
FLUSH** — near-black body but the lash-cane flushed a live grey-green along its length
(the working muscle, the one green note in the family). The visible recovery droop is
the def's other state — a retint/derive, not a second commission. (⛔ The lash is a
MapComponent, never a plant CompTick — plants only TickLong; mechanics ticket §9.)
Canvas 256, single. drawSize ~2.2.

### RM_HollowVenomvine — the grown gates

> Old stands die from the inside and stand anyway: tubes of grey cane, galleries wide
> enough that the runway nations thread them like streets — and a person the Jawas'
> size can crawl where the streets go.

**Silhouette/palette:** aged tubular architecture — the thicket as a cluster of open
weathered tubes, dark gallery mouths readable at zoom, thorns worn blunt; **anchor:
DRIFTWOOD-GREY** — the family's black weathered out to silvered grey, the palest form,
age made visible. Canvas 256, single. drawSize ~2.2.

### RM_CrownVenomvine — the flowering landmark

> Rarest of all: a stand that crowns. It climbs past man-height-and-more into a single
> black column and flowers at the top — the only flower this plain owns — and when the
> wind drops, the dustflutters mob it in a grey cloud you can see from a day's walk.

**Silhouette/palette:** a vertical landmark — the thicket drawn up into one leaning
column, crowned with a burst of pale-violet flowers; **anchor: VIOLET ON BLACK** — the
family near-black carrying the biome's single flower-colour, pale luminous violet,
nothing else in the cast may use it. Wind-keyed mobbing (⛔ no day/night dependency —
ban 3) is behaviour, not art. **Canvas 512** (landmark showpiece — it must carry at
map zoom the way the sweetline trees do), single. drawSize ~3.5.

## 7. The regen-all list (owner-typed: "Regen all art to become our own")

**Donor-reskin sweep (MEASURED this pass):** every PawnKindDef of the 39 patch-cast RSW_
species + RSW_ShrublandGiant read from `src/RimStarWars/SWBestiary/` — **all 40 declare
donor `swanimals/...` texPaths** (SWBestiary ships loose PNGs at those paths). The art
dedup (§2) then splits them:

**Queued — donor-reskin with NO owned render anywhere (0 done / 0 registry):**

| subject | today's donor skin | the regen brief |
|---|---|---|
| **RM_Thunderstep** (`RSW_ShrublandGiant`, bs 6.0) | Fambaa (`swanimals/Fambaa/`) — and `fambaa_v1` in done/ is the CANON Fambaa, not this animal | The huge grazer as the sheet paints it: *"giants as walking hills with lit flanks"* — a vast dun-and-slate grazing hill on pillar legs, raised long-necked head (the only sightline in the biome), wool snagging in sheets along the flanks, utterly indifferent posture. **Anchor: WALKING HILL** — dun hide, slate shadow mass, one lit flank in the low gold light. Same silhouette ROLE as today (huge quadruped grazer), our own animal. 512 canvas, 3 facings, drawSize ~7.0. |
| **RM_Yanker** (`RM_TunnelSnake`, ported from `RSW_TunnelSnake` 2026-10-08) | Klorslug (`swanimals/Klorslug/`) | The corridor predator: long, thin, terrible, shaped exactly like the runs it hunts — a muscular tube of an animal, blunt armored ram of a head, mouth built to take prey head-on in a space with no sideways. **Anchor: CORRIDOR-DARK** — deep earth-umber above shading to root-black, pale gullet the only light. Same silhouette role (elongate tunnel serpent), ours. 256, 3 facings, drawSize ~1.8. |
| **RM_ScrapNestBird** (`RSW_ScrapNestBird`) | Whisperbird (`swanimals/Whisperbird/`) — shared with `RSW_Whisperbird`, TWO defs on ONE donor image today | The scavenger bird-analog of the vine: a wiry, quick, longer-necked diver with clever feet, built for threading thorns and carrying glitter. **Anchor: SOOT-AND-GLITTER** — dark soot plumage with oil-slick iridescent glints at throat and wing-edge (the magpie read: a thing that loves shine). Same silhouette role (medium bird-analog), ours — and it finally splits the two defs' art. 256, 3 facings, drawSize ~1.3. |

*(The ticket's four names resolve to three defs: "yanker" and "tunnel snake" are both
`RM_TunnelSnake` (was `RSW_TunnelSnake`, ported to the RimMandrake tier 2026-10-08, owner note on the Leaning Scrub sheet) — ruled name and def name of one creature.)*

**Job ids keep the live defNames as subjects** (`rsw_shrublandgiant_v1`,
`rsw_tunnelsnake_v1`, `rsw_scrapnestbird_v1`) so the dedup instrument finds them by
either spelling later; any RM_ re-tiering of these three is `LEANINGSCRUB_RULED_CONTENT_1`
def work, not an art id question.

**REGENS, not reskins — no `reference=` on any job** (standing law: reference triggers
reskin-validate); the existing silhouette/role is described in style_notes instead.

**Skipped — donor-reskin but a finished owned regen already exists (wire, don't regen):**
the remaining 36 cast members, each with a complete set in `done/` (census §2; e.g.
`desert_swaca_bantha` 3 facings, `canon_whisperbird_v1` 3 facings covering
`RSW_Whisperbird`, gizka 28 done-files, mossbeetle 18, iriaz 18, anooba 24, imperialtoad
6): FrilledGorg · Gorg · Iriaz · LongtailGorg · Eopie · Lothcat · Mudhorn · Ronto ·
Scurrier · Sketto · Kreetle · Igitz · Urusai · ImperialToad · Kybuck · Massiff · Bantha ·
Pufferpig · Anooba · Corinathoth · Gizka · Nuna · Worrt · MossBeetle · Grank · Qormot ·
Strill · Cannok · Whisperbird · Pikobis · Convor · Skalder · Vulptex · FeralNerf · Porg ·
Voorpak · KowakianMonkeyLizard. Queuing any of these would throw ruled work away.
⚠️ Whether each done set is actually WIRED over the donor pixels at the def's
`swanimals/` path was NOT verified per-subject here — that wiring audit is FOUNDRY's
(§11).

**Not regen candidates at all:** the 5 inline donor rows (`Terrorworm`, `AA_Cactipine`,
`AA_Needlepost`, `AA_Wildpawn`, `AA_Wildpod`) are RAW DONOR DEFS, not our reskins —
regenerating their art would not make them ours. Their fate is roster work at a sitting,
not an art queue (§11).

## 8. Blurrg — the tamed-only mount (canon subject)

**Ruled frame (fixed, card decision 2026-09-28):** TAMED-ONLY — never spawns wild, which
threads frozen ban 4 (large-band void, bs 2.5) as written. Arrives by trade, scenario or
quest. 🔴 **The `RSW_Blurrg` port (Utinni/RSW layer per Q11) and the `canon_references/`
entry are FOUNDRY/design owed** — neither exists yet (git grep: zero; canon entry: none).
Canon library law: the entry is the acceptance target, so **the render queued here is
judged against that entry once written** — the prompt is written from canon directly
(The Mandalorian; Wookieepedia-sourced at the review).

**Description:**

> A blurrg is two legs, one appetite, and a temper that respects exactly one thing:
> whoever broke it. Nothing about it belongs to this plain — it was carried here, the
> way saddles are — and the plain has not been consulted. Under a rider it will cross
> the fuzz at a pace nothing local cares to match, and at the picket line it will eat
> anything it is shown and several things it is not.

**Silhouette/palette brief:** the canon animal — a heavy bipedal reptilian mount: two
massive columnar legs, no functional forelimbs, a huge rounded body sloping to a thick
tapered tail, a broad blunt wide-mouthed head low on a short neck. **Anchor: CANON
HIDE** — mottled tan and grey-brown leathery hide, paler belly, dark mottling across the
back; canon appearance outranks palette invention (the diversity law is satisfied by
canon itself — nothing else in the cast is tan leather on two legs).

**Facings:** south, east, north (north = true rear: the great haunches and tail root, no
face). Canvas 256. **drawSize intent: ~2.4**, bodySize 2.5 (legal because tamed-only);
rideable, work-beast temperament.

## 9. Wire-only (validated renders under old RUT_ subjects — never queue; FOUNDRY wires)

| render (done/ + _artsrc/) | wires onto | note |
|---|---|---|
| `rutfuzz_v1` | `RM_Fuzz` texPath | THE signature canopy plant — zero PNGs on the RM_ def today |
| `rut_grellbush` | `RM_Grellbush` | ditto |
| `rut_grellspine` | `RM_Grellspine` | ditto |
| `rut_wildhealroot` | `RM_WildHealroot` | ditto |
| `rmvenomvine_v1` | **`RM_Venomvine` ONLY (already wired 2026-09-26)** | ⛔ NOT kept as the thicket base — §6 verdict. Comes OFF this biome's wire list; the fresh `RM_VenomvineThicket` render replaces it here, and the shared texPath must split (§11). |

## 10. Queued art — 27 subjects (17 faced sets + 10 singles), 61 job files — FILED, 0 refused

**CSV:** `infrastructure/artpipe/art_lists/leaningscrub_bedazzle_cast.csv` —
`rimflow_item_id LEANINGSCRUB_BEDAZZLE_SITTING_1`, channel codex, transparent,
priority 70, `reference` empty on every row (regens, never reskins). Queued via
`fill_queue.py` (derive-facings default: east is the master, north/south derive —
ARTPIPE_FACING_COHERENCE_1). Jobs land in `infrastructure/artpipe/pending/`; the daemon
claiming one is success.

| group | id | canvas | facings | anchor |
|---|---|---|---|---|
| fill | `RM_Fuzzrunner` | 256 | s,e,n | fog-silver |
| fill | `RM_Thornhold` | 256 | s,e,n | bone-and-venom |
| fill | `RM_Shokka` | 256 | s,e,n | barrens-dapple |
| fill | `RM_Zellik` | 256 | s,e,n | slate-and-glare (grounded only) |
| menagerie | `RM_Fuzzviper` | 256 | s,e,n | canopy-mimic |
| menagerie | `RM_Surrik` | 256 | s,e,n | loam-dark |
| menagerie | `RM_Ribbonwhip` | 256 | s,e,n | waxy-gold |
| menagerie | `RM_Vissler` | 256 | s,e,n | lichen-grey / ember core |
| menagerie | `RM_VisslerArm` | 256 | single | item — the shed lure |
| menagerie | `RM_Dustflutter` | 256 | s,e,n | moth-dust |
| menagerie | `RM_Shirrel` | 256 | s,e,n | storm-grey |
| menagerie | `RM_Crustweevil` | 256 | s,e,n | oxide-sheen |
| menagerie | `RM_Rollbug` | 256 | s,e,n | tar-polish |
| menagerie | `RM_Tikkit` | 256 | s,e,n | dry-grass |
| flora | `RM_Whipfuzz` | 256 | single | silver-green |
| flora | `RM_Pillowmoss` | 256 | single | fog-green / dew-silver |
| flora | `RM_Tanglefuzz` | 256 | single | dusky olive / dark heart |
| flora | `RM_Cruststar` | 256 | single | lichen-white / gold rim |
| venomvine | `RM_VenomvineThicket_v2` | 256 | single | near-black island (fresh base) |
| venomvine | `RM_DrippingVenomvine` | 256 | single | amber on black |
| venomvine | `RM_TwitcherVenomvine` | 256 | single | grey-green flush |
| venomvine | `RM_HollowVenomvine` | 256 | single | driftwood-grey |
| venomvine | `RM_CrownVenomvine` | **512** | single | violet on black (landmark) |
| regen | `rsw_shrublandgiant_v1` | **512** | s,e,n | walking hill (thunderstep) |
| regen | `rsw_tunnelsnake_v1` | 256 | s,e,n | corridor-dark (yanker) |
| regen | `rsw_scrapnestbird_v1` | 256 | s,e,n | soot-and-glitter |
| Blurrg | `rsw_blurrg_v1` | 256 | s,e,n | canon hide |

**Named follow-ons (not commissioned now, deliberately):**
- `RM_Zellik` flight flip-book frames (whole-body directional flip-book,
  `flyingAnimationFramePathPrefix` shape, Sparrow template) — the flyer law says never
  block flight on frames; file after the grounded sprite is accepted.
- `RM_Dustflutter` burst flip-book — same law, same shape, tiny frame count.
- `RM_TwitcherVenomvine` recovery-droop state — a derive/retint of the master once
  accepted, not a fresh commission.
- Vissler Gale star-mat — behaviour/spawning dressing, only if FOUNDRY wants a mat
  graphic at all.

## 11. Handoff notes (defects/finds observed — nothing filed, per this brief)

- **The thicket/mat texPath must SPLIT when `RM_VenomvineThicket_v2` lands.**
  `RM_Venomvine` and `RM_VenomvineThicket` share `Things/Plant/RM_Venomvine` *on
  purpose* today (each def's header says so, wired 2026-09-26). The fresh man-height
  base makes that sharing wrong in both directions — FOUNDRY gives the thicket its own
  texPath or the desert ground-mat inherits a man-height sprite.
- **`rmvenomvine_v1` is the Long Shade mat, not this biome's thicket** — its prompt
  hard-forbids standing ("never a standing shrub") while this biome's ruling is
  man-height-plus. Anyone about to wire it onto the thicket should read §6 first.
- **The 36-species wiring audit is real owed work:** every patch-cast def still declares
  a donor `swanimals/` texPath, and this pass did NOT verify per-subject that the
  finished owned regens (desert_swaca_*, canon_*_v1, etc.) were wired over the donor
  pixels at those paths. If they were not, the campaign is still showing donor art for
  species whose owned renders sit finished in `done/`. That audit belongs with
  `LEANINGSCRUB_RULED_CONTENT_1` §6's wire half / the absorption items.
- **`RSW_ScrapNestBird` and `RSW_Whisperbird` ship on ONE donor image today** — two
  species, one texture. `rsw_scrapnestbird_v1` splits them; the whisperbird side keeps
  `canon_whisperbird_v1` (already done).
- **The 5 inline donor fauna rows (Terrorworm + 4 AA_) are raw donor defs** — not
  reskins, so "regen to own" cannot apply; making them ours means new species or ports,
  a sitting/roster question, not art. Same family as the `VAEWaste_Hydra` dead row
  (UNRULED, strike-candidate, confirm with the owner at art review — ticket §7).
- **Blurrg render precedes its canon_references entry** (queued on the parent's
  explicit brief). The entry is design-owed; when written, the render is judged against
  it — if the entry's Must-show contradicts the render, the render loses.
- **Palette-diversity law is carried verbatim in every style_notes** of this cast's
  CSV — 27 sprite sets, no two sharing an anchor (the venomvine family shares its
  near-black REGISTER but each form carries a distinct accent by design). If a rendered
  batch comes back tonally uniform anyway, that is a prompt-adherence defect for the
  daemon channel, not a reason to re-rule the cast.
- **Trim law was applied to inherited prose:** the review's fill table called the
  thornhold a "living perimeter alarm" and the tikkit risked the same shape — both
  entries here carry the ecology only, per the final ruling. Nothing warning-flavored
  ships in any prompt or description in this bible.
