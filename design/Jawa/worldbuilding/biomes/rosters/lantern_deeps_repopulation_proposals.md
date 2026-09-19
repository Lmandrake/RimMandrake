# Lantern Deeps — fauna repopulation proposals

**Status: PROPOSAL, awaiting the owner's picks.** Item `DEEPS_FAUNA_REPOPULATION_1`.
On 2026-09-18 the owner cut or remade 15 of the 16 Lantern Deeps animals and asked for
"more truly alien hydrocarbon-based life forms that are utterly different than anything
on the dayside... we need to repopulate this biome's fauna significantly with surprising
life forms." Below are twelve concepts written in the register of his own remake briefs
(pale-blue glow, yellow hydrocarbon internal liquids, one strange specific mechanic per
creature, each with a plain trade). Nothing here is built, named in a def, or ruled.
He rules line by line on the summary table at the end; `## Invented premises` lists
what this doc assumed that the biome sheet does not state.

## 1. Sipper

**Visual brief.** A swarm vermin the size of a thumbnail: a single clear bead of
liquid held in a pale-blue skin so thin the yellow droplet inside shows as a point of
colour, three hair-fine legs under it, no head, no eyes. Alone it is invisible; the
sprite is a loose cluster of eight to twelve beads in one cell, each bead a faint blue
ring around a yellow dot, drawn at drawSize ~0.6 so a swarm reads as a scatter of
sparks. Palette exactly the house style. It moves in short jittering hops, always
toward the brightest thing on the map, and sits still once it has arrived. The Deeps'
plankton.

**Body size.** 0.08.

**Niche.** Eats light — it drinks photons off any glower and stores them as pentane
in the droplet. It is the bottom of every food chain here: the Shoal (§12), the Hush
(§4) and the Drinker all take Sippers. Very common; breeds against a population cap
wherever glow-fungi grow, and wherever a lamp is lit.

**The one surprising mechanic.** Sippers cluster on light sources and drink them: a
lamp with a swarm on it loses one cell of glow radius per ten Sippers, until a heavily
sipped lamp is a dim coal. Killing them is trivial; they do not fight; they just come
back.

**Trade.** *Gain:* a sipped lamp is a smaller beacon — fewer Cleavers, Hush and
Grabbers are drawn to a half-drunk light, so a colony that tolerates Sippers is
harder to find. *Cost:* you see less, your growing lights underperform, and a
stockpile of Sippers is a permanent tax on every lamp you own.

**Engine feasibility.** New C# on two existing seams: population from
`RM_CompVerminBreeder` (capped lord-free breeder, `RM_MapComponent_VerminPopulation`
for the cap and the vermin alert), movement from a `RM_SeekTargetExtension`-style
JobGiver retargeted at `CompGlower` things. The drain itself is the new part: a
MapComponent that counts Sippers within 1 cell of each glower and overrides that
glower's effective radius (`CompGlower.UpdateLit` after changing the radius is the
expensive call; batch it per few hundred ticks). ~150 lines.

## 2. Drifter

**Visual brief.** A floating bladder the size of a head, one cell, drawn as a
near-spherical translucent balloon of pale blue with a heavy yellow slosh settled in
its lower third, like a half-filled glass held upside down. Faint darker-blue ribbing
where the skin is thicker; a short fringe of dangling threads underneath that never
touch the floor. No face. It does not walk: it drifts a hand's breadth above the
ground, bobbing, and its shadow is the only sign it has weight. The swarm variant is a
loose line of three or four following each other like lanterns on a string. Pure house
palette, and it should visibly glow (a real glower, small radius).

**Body size.** 0.35.

**Niche.** Grazer: it hangs over glow-fungi pastures and drinks their light, and it
is a Sipper's easiest prey to reach because it rises to the same lamps. Eaten by the
Grabber and by anything with reach. Common in the open voids, absent from tight
tunnels. Its bladder is methane — that is how it floats.

**The one surprising mechanic.** A Drifter is a bomb that does not know it. Killed
by a blade it collapses into a harmless sac; killed by fire, a spark, a hot bullet or
anywhere near an open flame, its bladder ignites and it detonates — a small explosion
with a real chance of dropping the roof (the collapse hazard, ruled v1).

**Trade.** *Gain:* butchered cold it yields a full sac of methane-rich fluid, the best
fuel-per-kill in the Deep, and a tamed string of Drifters is a herd you can walk into a
raider tunnel and shoot. *Cost:* every lamp-lit hunt is a hunt with explosives, and one
incendiary round near a herd rewrites the map.

**Engine feasibility.** XML only. Vanilla `CompProperties_Explosive` with
`explodeOnKilled true` and a `requiredDamageTypeToExplode`-style gate (vanilla exposes
`explodeOnKilled`; the fire-only gate is `damageDefs`-conditioned — verify the exact field
on build, and if absent it is a ten-line `Notify_Killed` check). Flight is drawSize,
an offset, and a `MoveSpeed` stat; there is no real hover in the engine.

## 3. Candler

**Visual brief.** A slow slab: a low, flattened ovoid two cells long and one wide,
like a loaf pressed down, skin pale blue and slightly translucent so that a long
yellow reservoir shows along its spine — a swollen dorsal sac, brighter and more
opaque than the rest, the way a full wineskin looks. Underneath, a broad soft foot; it
has no legs and moves as a single slow ripple. At the front, three short blunt
feelers, no eyes, no mouth visible (it feeds through the foot). When full the sac
stands proud of the back; when milked it sags. House palette, but the sac should be
the most saturated yellow on any creature here — it is the point of the animal.

**Body size.** 1.2.

**Niche.** Grazer on mycelium and ossk bramble; the Deep's cow. Preyed on by the
Grabber and the Hush. Uncommon but steady, in small groups on the fungal pastures near
water.

**The one surprising mechanic.** It stores its energy as wax — solid pentane-heavy fat
in the dorsal sac — and it can be milked for it. "Cold wax" burns like chemfuel and
needs no refinery. But it is hydrocarbon organics: above roughly 0 °C it softens,
sweats and spoils, and a warm store of it is a fire waiting for a reason.

**Trade.** *Gain:* fuel and lamp-oil on the hoof, without a refinery or a chemfuel
line. *Cost:* the wax must be stored cold — a warm freezer failure ruins the stockpile
(and a warm stockpile near fire ignites it), so the Candler ties your fuel economy to
your cold chain. Tameable, and worth taming for exactly this.

**Engine feasibility.** XML only. `CompProperties_Milkable` on the pawn producing a
`RUT_ColdWax` item; the item carries vanilla `CompProperties_TemperatureRuinable`
(the egg/produce comp: ruined above a threshold) plus high `Flammability`. Nothing to
write in C#.

## 4. Hush

**Visual brief.** The one thing down here that does not glow — a deliberate break
from the house palette, and the reason it works. A wide flat sheet, two cells across
and less than a hand thick, matte black with the faintest blue edge-light only where a
lamp catches its rim; the yellow interior fluid is there but shows only at the seam
when it lifts to strike, a thin bright line. No limbs visible at rest: it lies flat
over mycelium like a spill of shadow and the sprite at rest is almost a hole in the
floor. When it lunges it peels up from the front edge and folds over its prey, and the
underside — seen only then — is a field of small pale-blue hooks. It moves by a slow
flowing slide, and only in the dark.

**Body size.** 1.6.

**Niche.** Ambush predator of anything that walks: Candlers, Shoals, tamed animals,
colonists. Nothing eats an adult Hush except the Grabber. Rare per map — one or two
— and always on unlit fungal floor near a pasture, never in the crystal galleries,
because there the lanternstone would show it.

**The one surprising mechanic.** It cannot be seen on an unlit cell. On any cell below
a light threshold the Hush is undrawn and untargetable; step within two cells and it
lunges. Carry a lamp and it is a plain black slab you can shoot from across the room.

**Trade.** *Gain:* your light is your safety — a lit corridor has no Hush in it, only a
visible one. *Cost:* the same lamp is the beacon the sheet says it is (§5: "light
draws what lives here"), so you buy safety from the Hush by advertising yourself to
the Cleavers and the Grabber. Genuinely dangerous; not tameable (it has no reason to
be).

**Engine feasibility.** New C# on an existing seam. The ambush is
`RM_CompAquaticAmbusher`'s pattern (idle-and-hidden until a target is within radius,
then `RM_JobDriver_LungeAttack`) with the terrain test swapped for a mycelium-floor
test. The invisibility is a Harmony prefix on the pawn's draw and on targeting that
reads `map.glowGrid.GroundGlowAt(cell)` against a threshold — Anomaly's
`HediffCompProperties_Invisibility` is the vanilla shape but is DLC-gated and does
not read light, so write our own (~80 lines).

## 5. Knocker

**Visual brief.** A blind tripod. Three long stilt-legs of pale blue, jointed once
and bending backward, meet under a small round body no bigger than a fist, and from
the front of that body a long neck ends in a heavy translucent hammer-head of dense
horn with the yellow fluid pooled inside it like a plumb-bob. No eyes anywhere; it
sees by tapping. One cell, tall silhouette, ~1.2 cells high, so it reads as a walking
tuning-fork. It walks with a deliberate high-stepping gait and stops every few cells
to tap the rock twice — the animation is the head dipping. Palette: house style, the
hammer the brightest part.

**Body size.** 0.6.

**Niche.** Eats mycelium and the small things in it (Sippers it can pin). Prey for the
Hush and Drinker. Uncommon, in the tunnels rather than the voids — it lives where the
roof is close enough to read.

**The one surprising mechanic.** It hears rock before it fails. A Knocker standing
near an unstable roof or a collapse about to fire drums a fast alarm and runs for the
sound side; a tamed one does it on your map, raising a collapse warning with the
danger cells marked before the fall.

**Trade.** *Gain:* the only early warning of the Deep's collapse hazard, and a guide
for which tunnels are safe to mine. *Cost:* its drumming is noise, and noise here is
the same beacon light is — a colony with Knockers is a colony every Cleaver can hear.
Tameable; worth one or two, never a herd.

**Engine feasibility.** New C#, small, on two existing seams. The alarm side is
`RM_CompPlantAlarm` / `RM_AlarmResponderExtension` (a thing detects, responders
react) and an `Alert` subclass in the `RM_Alert_VerminPopulationBase` mould. The
detection reads vanilla `RoofCollapseCellsFinder` / `RoofCollapseUtility` for
unsupported roof within its radius. ⚠️ The Deep's own collapse mechanic is "ruled v1"
in the caverns sitting but its implementation is unmeasured here — if collapse is only
vanilla roof-support, the Knocker warns of that, which is still real.

## 6. Tapper

**Visual brief.** A flat plate on many feet: a rounded disc one cell wide, low as a
hand, pale blue and semi-opaque, with the yellow fluid visible not as a pool but as
branching veins — a lightning-tree pattern from the centre to the rim, which brightens
and dims in a slow pulse. Around the rim a fringe of dozens of tiny identical feet, so
it moves like a coin sliding across a table. On the underside (seen when flipped) a
single central sucker of dull blue. No head, no eyes; the veins are the whole
personality. It is drawn to power the way the Sipper is drawn to light, and it climbs
onto conduits and batteries and sits there pulsing.

**Body size.** 0.5.

**Niche.** It eats electricity. In the wild it feeds from the piezoelectric lattices
wired to the aurora (sheet §3) and a reconnection storm is its feast day; on a
colonised map it seeks conduits and batteries. Eaten by the Hush. Uncommon, in the
crystal galleries near the largest lanternstone.

**The one surprising mechanic.** A wild Tapper sits on your battery and drains it —
a slow flat drain per Tapper, and a bank of them empties a battery bank in a night. A
tamed one is a living battery: it charges from the lattices when the aurora storms,
and can be "milked" for charge into an adjacent battery.

**Trade.** *Gain:* free power on storm days with no wiring to the surface, and a
battery that walks. *Cost:* wild ones are a standing tax on your grid and you cannot
fence a thing that eats through the fence's own conduit. Tameable; worth taming in
numbers.

**Engine feasibility.** New C# on an existing seam. Seeking and sitting on a target
building is exactly `RM_JobGiver_GnawTargets` + `RM_GnawTargetExtension` (generic
"go gnaw buildings matching X") with `CompPowerBattery` as the filter; the gnaw
driver's per-tick effect becomes `CompPowerBattery.DrawPower(n)`. The tame side is a
`CompMilkable`-shaped comp whose product is charge pushed into an adjacent
`CompPowerBattery.AddEnergy` rather than an item (~60 lines).

## 7. Pooler

**Visual brief.** A creature that is a puddle. One cell, drawn as a rounded meniscus
of pale-blue liquid with a raised centre, the way a drop sits on a cold plate, and in
the centre a slowly rotating yellow core the size of a coin. No limbs, no skin edge
that reads as solid — the rim is a soft gradient into the floor, and it should look
wet. It moves by flowing: the sprite's rear edge thins and the front edge thickens as
it goes, and it pours itself around obstacles. It leaves a brief darker-blue damp mark
behind it that fades. House palette but colder and paler than the others; it is
mostly solvent.

**Body size.** 0.9.

**Niche.** It lives in the solutions that seep down (sheet §2: fuel snow, ammonia)
and it is drawn to heat the way everything else here is drawn to light. It eats the
warm — the fine skin of methane vapour that any warm thing raises off the cold floor.
Eaten by nothing; it is not food. Uncommon, in wet galleries and the shallows around
the vellok reed.

**The one surprising mechanic.** It seeks the warmest thing on the map and drapes
itself over it. A campfire or a heater under a Pooler goes out — flat, at once, no
smoke — and a warm-blooded pawn under one takes fast hypothermia until they push it
off. It cannot burn; it is the one thing down here fire does not touch.

**Trade.** *Gain:* a tamed Pooler is the only safe fire brigade in a cave full of
methane and Drifters — send it at a fire and the fire dies without a spark. *Cost:*
wild ones hunt your heaters, and a colony whose heaters keep going out at −40 °C
loses colonists to the thing that was only looking for warmth.

**Engine feasibility.** New C# on an existing seam. Seeking is a
`RM_SeekTargetExtension` / `RM_JobGiver_SeekMarkedTerrain`-shaped JobGiver whose
target is the map's hottest `CompHeatPusher` building or `Fire` (or a warm pawn). On
arrival: `Fire.Destroy()` for fires, and for heaters a hediff/"smothered" state that
zeroes the pusher's `heatPerSecond` while it sits there. The hypothermia is vanilla
`Hypothermia` severity added by a small `HediffComp` on the victim. ~120 lines. Trained
"go to fire" for the tame version uses the vanilla firefighting work tag on animals
(`TrainableDefOf`-style) — verify animals can be given `Firefighter`; if not, a
zone-target job.

## 8. Blinker

**Visual brief.** A prey animal built around one organ. A soft upright teardrop, one
cell, about a metre tall, pale blue and a little translucent, and where a face would
be a single large lens-window through which the yellow interior fluid shows — not an
eye, a lamp with nothing behind it. Two thin trailing arms it walks on like crutches
and a third, shorter, it holds against the lens like a hand over a torch. Its rest
state is dim, shuttered by that arm; its alarm state, drawn as a second sprite frame
or a mote, is the arm flung wide and the whole body white-blue, the yellow bleached
out. House palette, with the flash as a pure overexposed burst.

**Body size.** 0.45.

**Niche.** Grazer on brellik bulb and zivvit taper — it eats the plants that glow, and
it lives in the lit pastures. Prey for everything: Hush, Drinker, Grabber. Common, in
skittish groups of three to five.

**The one surprising mechanic.** When hurt or cornered it flashes — a one-tick burst
of blinding light that leaves every pawn facing it half-blind for a few seconds and,
for one breath, lights the whole chamber. Every light-drawn predator on the map turns
toward that spot.

**Trade.** *Gain:* tamed Blinkers are a living alarm and a flare: wound one in a raid
and the raiders are blind for a moment and the wild Cleavers are coming for them.
*Cost:* they are coming for you too — every Blinker hunt, tamed or wild, tells the
cave exactly where you are. Tameable, cheap, and a liability you choose.

**Engine feasibility.** New C#, small. The trigger is `RM_CompWoundLink`'s
post-damage-notification seam (`Notify_DamageTaken` on a ThingComp); the blind is a
short-lived hediff on pawns in line of sight with a sight-capacity offset (XML
hediff); the flare is a spawned short-lifespan glower building (XML: a `CompGlower`
+ `CompLifespan` thing, radius 20, 60 ticks) at the Blinker's cell. The "predators
turn toward it" needs no code — the flare IS light, and the ruled light-draw behaviour
is what answers it.

## 9. Yolk — the set-piece

**Visual brief.** A sun hung under the mountain. One enormous bladder, four cells
across (drawSize ~5 on a 3×3 or 4×4 body), a sphere of pale blue skin so thin the
yellow inside is the picture: a great slow-turning yolk of hydrocarbon fluid, brightest
at the centre, with darker convection cells visible in it like the surface of a star.
No limbs, no face, a crown of soft dangling filaments from its underside that stir in
no wind. It is drawn from below as a hanging thing: it is pinned to the cavern roof
and never moves (MoveSpeed effectively 0), and it is a true glower with the largest
radius of any creature — it lights its whole chamber a warm blue-gold. House palette
pushed to its limit: this is where all the yellow in the biome went.

**Body size.** 6.

**Niche.** It eats the light of the entire chamber's fungal pasture — the fungi under
it are fat and the ones at the chamber's edge are starved — and the Deep's animals
gather beneath it, because it is the biggest light there is. Nothing eats it. One per
Deep at most, and many Deeps have none; where it exists the chamber is the map's
landmark and its most crowded room.

**The one surprising mechanic.** It is a chamber-sized light source and a
chamber-sized methane bomb in one body. Leave it and you have a lit hall — and
everything light-drawn in the Deep is under it. Kill it and its glow dies with it and
its bladder comes down: if anything hot touches it the chamber detonates and the roof
comes down over the whole footprint.

**Trade.** *Gain:* killed cleanly (cold, blades, no fire) and butchered it is a
fortune in fuel — the single richest harvest in the biome — and the chamber is yours in
darkness. *Cost:* the light goes out for good, the room that was lit is now the
room where everything came to feed, and one spark during the kill collapses the
landmark on everyone under it. A set-piece rarity: not tameable, not repeatable.

**Engine feasibility.** XML only. `CompProperties_Glower` on the pawn (large radius),
`CompProperties_Explosive` with `explodeOnKilled` and a big radius, a `MoveSpeed`
of ~0.1 and a `Building`-sized `size`/`drawSize`; roof collapse from the explosion is
vanilla behaviour where the roof is unsupported. Placement as one-per-map is a
`GenStep` or a biome `wildAnimal` commonality so low it is effectively a landmark —
that choice is the only design call left.

## 10. Chiller

**Visual brief.** A creature that is colder than the cave. A squat barrel body one
cell wide on four thick short columns, skin pale blue and heavily frosted — the only
animal here whose surface is opaque, crusted white with rime that flakes off as it
walks, so it leaves a faint powder trail. Where the frost cracks the yellow fluid shows
through in fine lines. Along its back a row of tall thin fins, vanes of nearly clear
blue, that stand up and fan when it is working hard. No visible eyes; a broad blunt
front. It moves slowly and deliberately and the air around it should be drawn with a
faint distortion or a fall of frost motes. Palette: house style under a white crust.

**Body size.** 1.4.

**Niche.** Grazer on nurrik gill and the wet-ground fungi. It has no predator but the
Grabber; nothing else wants to bite something that cold. Uncommon; the deep wet
galleries, where the seep is coldest.

**The one surprising mechanic.** It pumps heat out of itself and into the rock, and
the rock is the cave, so the air around it drops: a Chiller in a room holds that room
some degrees below the cave's ambient, permanently, with no power.

**Trade.** *Gain:* a tamed Chiller in your store room is a freezer that needs no
electricity — the cold chain that makes cold wax (§3) and every hydrocarbon harvest
storable in a heated base. *Cost:* the same room is deadly to stand in for long, and
a Chiller that wanders into the barracks is a hypothermia incident at −40 °C. Tameable;
you want exactly one, penned, and the pen decides what it keeps.

**Engine feasibility.** XML only, pending one check. Vanilla `CompProperties_HeatPusher`
with a negative `heatPerSecond` on the pawn's ThingDef — the comp is a plain
`ThingComp` and pawns are `ThingWithComps`, so it should tick; **verify on a quicktest
that `CompHeatPusher` pushes from a pawn** (it checks `parent.Spawned` and the room
of `parent.Position`; the Glowbulb's `CompGlower` on a pawn is the precedent). If it
does not, a twenty-line `ThingComp` calling `GenTemperature.PushHeat` is the same
thing.

## 11. Slick

**Visual brief.** A long low thing that is mostly its own trail. A narrow segmented
body two cells long and a third of a cell wide, pale blue and glossy, made of a dozen
identical bead-segments each with a yellow drop inside, joined by clear necks — a
string of drops rather than a worm. No head worth the name: the front segment is a
little larger and has a ring of short feelers. It has no legs; it moves by pumping the
segments in sequence, and it is always wet, sitting in a shine of its own liquid. The
trail it leaves is the important part of the art: a glossy darker-blue streak with a
faint yellow sheen, drawn as filth, that catches lamplight.

**Body size.** 0.7.

**Niche.** A bottom-feeder: it eats fungal rot, the mycelium's dead layer and the
corpses of Sippers. Eaten by the Hush and the Drinker. Common, in the tunnels between
voids — it is the thing you meet in corridors.

**The one surprising mechanic.** It sweats pentane. Every cell it crosses is left
with a slick of liquid hydrocarbon that does not evaporate at −40 °C, and that slick
burns: one spark on a Slick's path and the fire runs the corridor end to end as fast
as a fuse.

**Trade.** *Gain:* follow the slicks and they lead you to its warren, and the slicks
themselves can be mopped up as fuel by anyone with a bucket and the patience. *Cost:*
every corridor a Slick has used is a fuse laid for you, and with Drifters (§2) in the
same tunnel a single ricochet becomes a chain of explosions. A hazard, not a fighter;
not tameable (a tame one would fuse your own base).

**Engine feasibility.** Small C# on XML. The trail is vanilla `Filth_Fuel`
(flammable filth already in the game) or a `RUT_` copy with a longer life; a
~30-line `ThingComp` calls `FilthMaker.TryMakeFilth` on the cell it leaves each
time `Position` changes. Fire propagation along filth is vanilla — nothing to write.
The "mop up as fuel" is a stretch goal: a `RM_JobDriver_EatCleanable`-shaped job
that yields an item instead of eating (that driver is the nearest idiom).

## 12. Shoal

**Visual brief.** Many bodies sharing one blood. Each individual is a small lozenge,
half a cell, pale blue, pointed at both ends, with a bright yellow thread running its
length — and the thread does not stop at the body: it continues out both ends as a
fine glowing filament that joins the next lozenge, so a Shoal of eight to fifteen
moves as a loose net of blue beads on a single yellow string. Individually each has
no face, no legs; they glide (the filament is the muscle) and they turn as one. When
one is hurt the yellow in ITS thread dims and the threads of its neighbours brighten
for a moment: the fluid is moving between them. The art job is the individual lozenge
plus a filament-end that reads as cut when it is alone.

**Body size.** 0.2.

**Niche.** Filter-feeder on Sippers and on the light-rich fluid of the fungal shallows.
Prey for everything larger. Very common in the open voids, in shoals of ten or more,
and never alone for long — a lone Shoal-lozenge dies within the day.

**The one surprising mechanic.** They share a circulation. Damage to one lozenge is
spread as fresh wounds across every linked lozenge in range, so no single one dies
of a single shot; and linked lozenges heal each other far faster than one alone. To
kill one you must wound the shoal; to kill the shoal you must kill them all.

**Trade.** *Gain:* a tame Shoal is a herd that shrugs off any one predator's bite,
and cheap to keep. *Cost:* you never get a clean, quiet kill — every hunt is a
drawn-out fight with the whole net, in the light, with the noise, and a shoal that has
been hurt is fifteen healing bodies that want to go back to the lamp. Tameable, but
that is not why it is here; it is here to be the thing the Hush and the Drinker live
on.

**Engine feasibility.** Existing comps, no new C#. `RM_CompWoundLink` +
`RM_WoundLinkExtension` (post-damage, move an injury fraction to same-tag pawns in
radius as fresh injuries on equivalent parts) and `RM_HediffComp_KinMending` (+50 %
healing while ≥ 2 same-tag kin in radius) are exactly this, built for the Rot's
health-sharing and name-blind by tag. XML wires the tag; the filament is art.

## Summary table

Rule line by line. "Tame" marks the ones with a reason to want one; ⚠ marks the
genuinely dangerous; ⭐ the set-piece.

| # | name | bodySize | niche | mechanic | trade (gain / cost) | feasibility |
|---|---|---|---|---|---|---|
| 1 | Sipper | 0.08 | swarm vermin, eats light, bottom of every chain | clusters on lamps and drinks their radius | smaller beacon, fewer predators drawn / you see less, every lamp taxed | new C# (~150 lines) on `RM_CompVerminBreeder` + a glower-seeking JobGiver |
| 2 | Drifter | 0.35 | floating methane grazer, common in voids | explodes if killed by fire or spark, harmless to a blade | best fuel-per-kill, walkable herd-bomb / every lamp-lit hunt is with explosives | XML: `CompProperties_Explosive` `explodeOnKilled` |
| 3 | Candler | 1.2 | grazer, the Deep's cow — **tame** | milked for cold wax, a fuel that spoils and ignites when warm | fuel with no refinery / fuel tied to your cold chain | XML: `CompMilkable` + `CompTemperatureRuinable` |
| 4 | Hush ⚠ | 1.6 | ambush predator on unlit fungal floor, 1–2 per map | undrawn and untargetable on unlit cells; lunges at 2 cells | your lamp makes it visible / your lamp is the beacon | new C# (~80) on `RM_CompAquaticAmbusher` + glow-gated draw/target patch |
| 5 | Knocker | 0.6 | blind tunnel grazer — **tame** | drums before a roof fails; tamed = collapse alert with cells marked | early warning of collapse / the drumming is noise, noise draws | new C# on `RM_CompPlantAlarm` + `Alert`; reads `RoofCollapseUtility` |
| 6 | Tapper | 0.5 | eats electricity, gallery-dweller — **tame** | wild: drains your batteries; tame: charges from the aurora and gives it back | free storm-day power / a standing tax on the grid | new C# (~60) on `RM_JobGiver_GnawTargets` → `CompPowerBattery.DrawPower` |
| 7 | Pooler | 0.9 | living puddle, seeks warmth — **tame** | drapes over the hottest thing: fires die, heaters stop, pawns chill | fire brigade that makes no spark / heaters go out at −40 °C | new C# (~120) on `RM_SeekTargetExtension`; `Fire.Destroy` |
| 8 | Blinker | 0.45 | grazer on glowing plants, common prey — **tame** | flashes when hurt: blinds attackers, lights the chamber, draws every predator | living flare and alarm / tells the cave where you are | small C#: damage-notify seam + XML blind hediff + spawned glower |
| 9 | Yolk ⭐ ⚠ | 6 | ceiling sun, one per Deep at most, nothing eats it | chamber-scale glower AND chamber-scale methane bomb | fortune in fuel if killed cold / light lost, room collapses on a spark | XML: `CompGlower` + `CompExplosive`, MoveSpeed ~0 |
| 10 | Chiller | 1.4 | frosted grazer in the wet galleries — **tame** | pumps heat out of the room, no power | a freezer with no electricity / deadly to stand near | XML: `CompHeatPusher` negative, one quicktest to confirm on a pawn |
| 11 | Slick | 0.7 | corridor bottom-feeder, common | sweats a flammable trail that burns like a fuse | trails lead to its warren, mop-able fuel / every corridor it used is a fuse | small C# (~30): `FilthMaker.TryMakeFilth` of `Filth_Fuel` on move |
| 12 | Shoal | 0.2 | linked filter-feeders, very common, the Hush's food — tame-able | one shared circulation: wounds spread across the net, kin heal each other | a herd no single bite kills / never a clean kill | existing: `RM_CompWoundLink` + `RM_HediffComp_KinMending`, XML only |

Counts against the brief: tameable with a reason **6** (3, 5, 6, 7, 8, 10; 12 is
tameable without much reason); genuinely dangerous **3** (4, 9, and 2 in any lit
hunt); set-piece **1** (9); resource on legs **3** (3 wax, 6 charge, 9 the fuel
fortune); no two mechanics alike; sizes 0.08 → 6. Chains that make it an ecology,
not a list: Sipper → Shoal/Blinker/Knocker → Hush/Drinker → Grabber; Drifter + Slick
in one tunnel is the fire hazard; Candler + Chiller is the fuel economy; Blinker's
flash and Knocker's drum both feed the ruled light/noise draw rather than replacing it.

Hard-ban check (sheet §6): nothing here is a crystal-studded animal (the Knocker's
hammer is horn, the Chiller's crust is frost); nothing removes the darkness mechanic
or the light-draw (the Yolk and Blinker ADD light and pay for it in draw, per §5);
no kyber mechanic anywhere; nothing above −40 °C.

## Invented premises

Things this doc assumes that `the_lantern_deeps.md` does not state. Each is a
one-line ruling if he wants it; strike the concept if he does not.

1. **The Deep's animal life is hydrocarbon-based on the Blue Desert model** — the
   sheet's cast is crystal life plus "ordinary dark-cave life"; the pale-blue/yellow
   hydrocarbon register comes from his regen briefs tonight and from
   `the_blue_desert.md` §"Hydrocarbon biology", not from the Deeps sheet itself.
2. **Warm-reactive applies to animal products** — cold wax spoils/ignites above ~0 °C
   (Blue Desert ban 3 says this of hydrocarbon organics; the Deeps sheet is silent).
3. **Hydrocarbon animals are not food** — butchering yields fuel-class items, never
   meat a colonist eats. Follows from the Drinker dying on iron blood in reverse, but
   it is a ruling, not a fact, and it decides what the Deep's kitchen gets.
4. **Methane is a body gas** — the Drifter and the Yolk float on it and detonate; the
   sheet names methane only as the exchange basis of Blue Desert life, not as a
   bladder gas.
5. **Light is drinkable by animals**, not just by the crystals — the sheet gives
   photonic metabolism to crystal life; the Sipper, Drifter, Shoal and Yolk extend it
   to fauna.
6. **Noise draws the Deep the way light does** — the Knocker's and Blinker's costs
   rest on it; the sheet has "the hum" and "light draws" but no ruled noise-draw.
7. **The auroral ground currents are tappable by an animal** — the Tapper feeds on the
   piezo lattices; the sheet wires the crystals to the sky, not animals.
8. **A collapse can be heard before it fires** — the Knocker; the collapse hazard is
   ruled v1 with dust and sand warnings, and this adds an animal warning.
9. **The seep solutions can host a free-living liquid organism** — the Pooler.
10. **Roof-pinned sessile fauna exist** — the Yolk; nothing in the sheet puts a living
    thing on the ceiling.
11. **A creature can be non-glowing on purpose** — the Hush breaks the "everything
    here is lit from within" register; the sheet does not forbid it, but the house
    style implies it.
12. **Tamed Deep fauna survive a surface colony** — every "tame" trade assumes the
    animal lives at the colony's temperature; if hydrocarbon animals die above −40 °C
    (consistent with premise 2), then the tameable six are tameable only in the Deep
    or in a Chiller's room, which is a stronger and stranger trade and may be the
    better ruling.
