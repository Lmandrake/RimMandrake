# Stillsand roster fill-out — 2026-09-27

Owner: *"but we need to fill out that roster. That's silly. More!"* — new species proposals
for the Stillsand (`RM_Stillsand`), designed AFTER the 2026-09-27 tier-move rulings
(`stillsand_bedazzle_2026-09-27.md` § Rulings). For review; nothing here is filed or built.
All-DLC assumed. Both frozen sheets' §6 bans bind everywhere (strict intersection); the size
law as ruled today is two-armed — **giants-or-grains on the SURFACE; a subsurface animal of
any size passes (the depth arm)**. Every new name is DRAFT, coined in the Dune Sea accent
(the Desert accent — doubled consonant, -a/-ik/-ok, 5–7 letters — said once into silence,
with one long vowel), checker-passed and Wookieepedia-probed (§5). ⚠️ Per the owner's typed
correction the same sitting: **the Dune Sea is a REGION, not a biome** — `RM_Stillsand` is
the one def; where a design reads strongest in the dune-sea region that is noted as flavour,
never as a roster split.

## 1. What the roster still lacks (measured, post-tier-move)

The cast after today's rulings, read from `WildAnimals_Stillsand.xml` + the two inline defs
+ the rulings (kudda CUT → Long Shade; truffle mole CUT → Long Shade; kreetle/gizka STAY;
qorrax stays terrain-bound to deep sand; vekka KEPT; ikee shrunk to grain; spined-gow/aurrok
grown to giant; sand busters ruukka + oorrik FILED; eemmok filed on the live commensal item;
vaalok drafted with the pack-animal build; cavern beast re-filed as its own items):

- **Giants:** oommok (mirror giant, 0.0005) · vozzik (0.0005) · aurrok (grazer, ~0.15) ·
  canon WarWyrm / Krayt / Greater Krayt · ruukka (event) · vaalok (pack)
- **Grain:** siidda (0.15) · ikee (~0.15) · kreetle (0.2) · gizka (0.01) · scurrier (0.1) ·
  granite slug (0.1) · oorrik (event) · eemmok (giant-shade commensal)
- **Depth arm (mid, subsurface):** vekka (0.5) · drazzik (0.05) · qorrax (deep-sand-bound)
- **Flora:** light-pipe nub (0.1) · ollim (0.01) · canon bloddle (0.05)

**What the sheets name that NOTHING above embodies — checked band by band:**

1. **The sky is empty.** deep_desert §4: *"Flight is a solved problem… Fliers nest here
   because nothing can reach the nest… Their guano, dropped prey and dead chicks are the
   biome's only meaningful organic import."* Zero fliers in the roster. This is a whole
   ruled paragraph of the frozen sheet with no def.
2. **Attritional predation is missing.** dune_sea §4 names exactly two legal hunting modes:
   subsurface (covered — vekka, drazzik, qorrax, krayt) and **attritional** (*"something
   follows you at your own speed and waits for you to run out of water"*). Nothing follows.
3. **The eternal-noon light-feeder niche is now VACANT.** The kudda (light-feeder) was cut
   to the Long Shade this sitting. The law says a hole is filled with a NEW creature, never
   a neighbour's — so the biome that IS eternal noon currently has no organism that eats
   the one thing it has in ruinous surplus.
4. **Carrion has no register.** Both sheets insist on it: nothing rots, *"everything that
   ever died out here is still here, intact and mummified"* — mummified fields are an §8
   inhabited object. Nothing in the roster touches a corpse. The mummified fields have no
   ecology, which also leaves "why are some finds bones only" unexplained.
5. **The ground only lies in one direction.** deep_desert §4: *"both sides evolved to
   falsify the signal: prey that drums dry… and predators with lures that drum juicy."*
   The predator half ships (drazzik, `RM_CompDrumLure`). The prey half — the water-fat
   animal that drums dry — has no def.
6. **The ollim's rent is uncollected.** deep_desert §4b: *"Its shade is rented: tenants pay
   in waste and water, so a silverbole is a small ecosystem standing alone in open ground."*
   No tenant exists; the flagship tree stands in an empty ecosystem.
7. **Flora, three gaps:** the **anhydrobiotic bloom** is ruled mechanism-first (the shipped
   `RM_IncidentWorker_BloomBurst` route) but has **no plant defs** to spawn; the ollim is a
   **family of one** where the sheet describes two growth forms (*"bone-white shields AND
   flat-topped truncates"*) among the bone-fields; and the grain-scale surface fauna
   (kreetle, scurrier, liikka below) has **no graze base** — the light-pipe is a lens, not
   food, and forageability is 0.0 by design, so what the grains eat is currently nothing.

Deliberately NOT filled: more subsurface strikers (three is plenty), more giants-for-their-
own-sake, any ambient scrub, anything for the caverns (re-filed items own that), the sarlacc
(its own build). The admission test stands: everything below is buried, dormant, giant, or
a line — and every commonality is sparse. The roster reads FULL by covering every band the
sheets rule, not by density.

## 2. The new cast

Six species, one per measured gap. Every behaviour names the shipped comp that carries it —
new C# appears only as a priced option, never as a requirement. All names DRAFT (§5).

### 2.1 The soorrak — the flier that owns the sky (gap 1)

**Description.** A sail-winged giant that nests in the deep dune precisely because nothing
alive can afford to walk there. Its sun-face is a single mirror-ceramic sheet — from below,
crossing the white sky, it is nearly invisible except as a moving glare; its shade-face
carries the eyes, the vents and the brood pouch. It drinks at the green line or the Scald's
shore, hundreds of kilometres away, and carries water home in its crop. Its guano rings,
dropped prey and dead chicks are the only organic import the deep dune receives — a soorrak
nesting crag is the richest square kilometre of surface in the biome, and its **eggs are
canteens**: a full one is drink in a rigid shell, and a Jawa will cross a horizon for a
clutch. It ignores anything that cannot reach the nest, which is everything.

**Def sketch.** bs 4.5 (giant band, mass arm), commonality 0.02. Real flight, core stats:
`MaxFlightTime` 30 / `FlightCooldown` 8, `canFlyIntoMap` true, `canLeaveMapFlying` true (it
drinks elsewhere — the sheet's own mechanism). Egg layer; the fertilised egg doubles as the
§4.4 canteen item (ingestible, thirst-flavoured food+mood, heavy). No new C#: flight is
vanilla core (the Locust/Chicken shape), eggs are vanilla `CompEggLayer`. Flip-book flying
frames owed as art, never blocking flight. Reads strongest in the dune-sea region (a moving
glare over the corrugation) — flavour note only, one biome def.

**Art brief.** Top-down soaring silhouette folded at rest: sail wings with a mirror-white
upper sheet, dark soft underside, long condensing snout that reads as plumbing rather than
a face. No nameable Earth bird.

### 2.2 The gaanok — the follower (gap 2)

**Description.** The other legal hunter. A gaunt, stilt-legged walker the colour of bleached
bone, powder-glazed, taller than a wall and thin as famine — and it never attacks. It simply
appears on the horizon behind a caravan and walks, at exactly the caravan's pace, for days.
It is doing arithmetic: a moving party is a sealed cask of water that will open itself if
followed long enough. When something collapses — of heat, of thirst, of wounds — the gaanok
is there within the hour, and it drinks. Shooting it is spending water on a thing that has
not touched you; outrunning it is impossible because it does not run either. The horror is
that it is patient, visible, and correct.

**Def sketch.** bs 5.0 (giant band, mass arm — thermal inertia), commonality 0.01, moveSpeed
~2.6 (a walking pawn's pace, never faster). Predator with `manhunterOnDamageChance` 0 — it
declines fights. v1 ships on vanilla predator AI: the low speed makes a chase structurally
impossible, so it takes only the downed and the slow, which IS the design. Priced option
(small C#): a ThinkNode preferring prey carrying `RM_Hediff_SunScald` (hediff shipped in
creaturebehaviors) — the follower keying on the biome's own scald mechanic. Not required.

**Art brief.** Extreme verticality — the sheet's rare vertical event: column legs, a low
slung condensing head carried at knee height, bone-white with hard black shadow.

### 2.3 The liikka — the light-eater (gap 3, the kudda's vacated niche filled NEW)

**Description.** A thumb-sized surface mite whose back is a domed mirror and whose underside
is the entire rest of the animal. It is the only creature on the planet that meets the
biome's one surplus head-on: it eats light — its dome meters photons down into photolytic
tissue the way the light-pipe nubs do, and it sieves the top centimetre of sand for the
glasscrust it grazes (§3.3). It never drinks; its whole water budget is metabolic. In a
biome that hides everything, the liikka is the thing a traveller actually SEES: a scatter
of stationary glints that turn out, on the next look, to have moved.

**Def sketch.** bs 0.12 (grain band), commonality 0.2 — the most common animal in the biome
and still sparse. Sun-axis polarised: mirror dome up, everything soft below. Feeding rides
the shipped filter-feed stack: `RM_FilterFeedExtension` + `RM_JobGiver_FilterFeedTerrain` /
`RM_JobDriver_FilterFeedTerrain` (creaturebehaviors) against sand terrain. No new C#.
Yields a pinch of biosilica-adjacent chitin on butcher; not worth hunting, which is why it
survives at 0.2.

**Art brief.** A polished hemispherical mirror dome catching one hard specular point, tiny
articulated shade-side legs just visible at the rim. Reads as a glint first, animal second.

### 2.4 The duumma — the prey that drums dry (gap 5)

**Description.** The fattest water-cask in the biome, and the ground's other liar. A
barrel-bodied subsurface burrower, plated in matte dust-glaze, that ferries stored water
between buried moisture pockets. Every subsurface hunter can feel a footfall; the duumma's
answer is to falsify the ledger — when anything heavy moves nearby it goes utterly still
and its gait-drum shifts to the dry, hollow signature of a desiccated husk: *nothing here
worth a strike.* A player who learns the tell (the sand that went quiet) is standing on
more water than a whole clutch of eggs; a predator that learns it, eats. Prey to the vekka,
the drazzik and the krayt; prize to a Jawa.

**Def sketch.** bs 1.8, **depth arm** — mid-band legal because it is subsurface, annotated
in place per today's Q7 ruling. Commonality 0.08. The prize is carried by the shipped
`RM_CompFluidSacs` (creaturebehaviors): butchering a fresh duumma yields fluid-sac items —
drink you can carry, the eggs-as-water economy without an egg. The signal-falsification is
v1 description + stats (no shipped comp expresses it; that is a cost stated honestly); the
audible half can ride `RM_ProximitySoundscapeExtension` (shipped) if the sitting wants the
sand to go quiet audibly. Never surfaces except to die.

**Art brief.** A smooth dust-glazed barrel low in the sand, only the back visible — a
half-buried keel with faint drum-plate ribbing. Powder glaze, never shiny (deep-desert ban 3).

### 2.5 The veessa — the miller of the mummified fields (gap 4)

**Description.** Nothing rots here, so something learned to eat what cannot rot. The veessa
is a grain-scale plated miller that works the mummified fields — the intact dead of ten
thousand years — rasping desiccated tissue into powder its gut chemistry can finally
unlock. It is the only thing on the planet that digests the dry dead: everything else
fights over the wet kill and leaves. Veessa sign is why some finds are bone-bright and
others still wear their leather; a field with no veessa in it has something worse in it.
It never touches the living or the fresh — fresh is water, and water draws things it
cannot afford to meet.

**Def sketch.** bs 0.15 (grain band), commonality 0.1. Vanilla carries it whole: a
corpse-eating diet (`foodType` including Corpse, the vanilla carrion shape) — no new C#.
Secondary option: `RM_EatCleanableExtension` (shipped) if the sitting wants it milling
dust-filth too. Slow, timid, flees everything. Butchers to nearly nothing — hunting one is
spending more water than it holds, which the description says out loud.

**Art brief.** A flat oval grinder, dusty bone-and-tan plates, a broad rasp-mouth on the
shade side; carries a faint powder bloom of the dust it makes. No nameable Earth insect.

### 2.6 The loomma — the ollim's tenant (gap 6)

**Description.** The rent-payer. A soft-bodied, kettle-sized commensal that lives its whole
life inside one ollim's hard-edged permanent shadow — it cannot survive twenty minutes
outside it. It forages the shade line at the shadow's rim, and it pays the tree: its dung
and its water-rich waste go into the sand at the trunk, concentrating exactly the buried
moisture the ollim accretes from. A stand with loomma in it is a working ecosystem; a
stand without them is a dying one. Tame ones will pay rent to a colony instead — a slow,
gentle fertiliser engine — but they die on any caravan that leaves the shade.

**Def sketch.** bs 0.25 (grain band), commonality 0.05, meaningful only where ollim stand.
The rent is the shipped `RM_CompDungSeeder` (creaturebehaviors) — waste that seeds and
feeds, the sheet's "tenants pay in waste and water" made literal. Shade-binding rides the
shipped shade stack: `RM_MapComponent_ShadeGrid` + `RM_ShadeSeekingWanderExtension` /
`RM_JobGiver_WanderInShadeGrid`, with the shipped `RM_Hediff_SunScald` +
`RM_HediffComp_ShadeDrivenSeverity` as the death-outside-shade clock. Evaluate
`RM_TenantTruceExtension` (EnvironmentalHazards) at build for the tree-tenant truce shape,
per the bedazzle doc's own note — grep before inventing holds; nothing new is needed.

**Art brief.** A soft rounded dark-dun body with a pale dust cap, small and low, drawn as
if permanently in shade — the one creature in the set with no hard highlight.

## 3. The new flora

(to fill)

## 4. Review-sheet notes

(to fill)

## 5. Name check results

(to fill)
