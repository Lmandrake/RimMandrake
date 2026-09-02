<!-- status: DRAFT PROPOSAL for owner review — brainstorm sitting 2026-08-31, not ruled. -->
# Tar pits, deep design — what a Jawa does with a hole full of the past

Canon anchor: `design/Jawa/worldbuilding/hydrology_and_fire_ecology.md` R-H9 (the
tar pits are the Pyrelands' geological receipt — ash, water, ash, water,
compressed over eons into "gooey, thick, biologically rich tar," interspersed
with the burning savanna rather than banded past it) and R-H6b (the hydrocarbon
reconciliation: tar is one of three fuel paths, priced by access cost, not
yield). Ties to `design/Jawa/ownership_settlement_spec.md` where noted — a tar
pit is unclaimed ground by nature, and that has consequences.

The owner's framing, verbatim: *"What are all the things that could be done
with tar pits? Could we dig canals to let the tar flow out, then light them on
fire?"* and *"perhaps there are creatures that live in even small pools (and
propane, and tar) that emerge when disturbed... maybe that's why the stuff is
there to begin with."* Both are expanded fully below, not summarized.

## 🔴 RULED — owner sitting 2026-09-01 (review sheet, all ten tar rows answered)

**Every tar concept is v1.** The §8 ladder below is restated to match; the old
v2/dream placements for these rows are superseded. His notes are design content,
verbatim:

| row | ruling | owner's note (verbatim) |
|---|---|---|
| entrapment-hediff | v1 | "amazing defensibility of difficult areas, to be used by deep desert tribes and other primitives" |
| sinking-render | v2→**v1** | "Test of our ability to make meaningful animation. We should spend some good time on this to really demo what we know how to do, or perhaps study other mods that make custom animations to inspire ourselves." |
| stratified-dig-sites | v2→**v1** | "This is pure gold. Fossils, dead bodies with inventory stuck on them, each one a piece of a story from the past that goes more ancient as you dig. But the digging gets slower and harder as you go. Would perhaps need to install a pump that removes the tar elsewhere on the map to enable the digging at all, while it continues to ooze in from deep sources below." |
| canal-flow-engineering | v2→**v1**, and 🔴 **promoted to a GENERAL RimMandrake-tier mechanic** | "This is a general new mechanic that we can use in many places. Dig channels that flood with water, ooze, slime, oil, tar, propane fuel... let's explore this deeply. Could be amazing realism. I'm inspired! This allows bases to dig trenches and flood them as a real defense. Will pay off in many more scenarios. This isn't Utinni or even Star Wars scope, this is general RimMaster level awesomeness mod." |
| flood-and-ignite | v2→**v1** | "Not kill outright, just burns like normal fire. But yes, toxic thick smoke that obscures and produces coughing and stinging eyes and stink." |
| tar-moats | dream→**v1** | "nope, this is in! Pawns with goals inside a region make the call to go across it, while if there's any way around it they do so." |
| tar-creatures | dream→**v1** | "Very star wars to reveal that a tar pit harbors a huge creature that not only thrives in tar but actually excretes it as a biological outcome. If captured, continues to do so at a very slow rate (not magical, very slow). However, even pits without one of these creatures still fill trenches and such from the tar sources deep underground." |
| geyser-incident | v1 | "Superb vile shock. Add creatures that consume tar too and run towards these events/moments. Able to mode through the tar easily unlike trapped creatures. They may like to eat tar-encrusted pawns too." |
| pit-wakes-setpiece | dream→**v1** | "Totally! The things in ancient dangers are the source, but also egg forms of creatures that hatch when disturbed (tar beasts), as well as things people maliciously put down there (grenades/bombs). Especially if it's in the territory of a terrible faction that's vindictive against territory thieves." |
| chemfuel-economy | v2→**v1** | "Yes, but it's slow and gross. Tar oozes out of the pipe joints. Only slowly produces chemfuel." |

---

## 1. Prior art, and where we go past it

- **Alpha Biomes' "The Tar Pits"** ships tar as biome-level terrain — "tar pits
  make movement quite difficult" — **decoration with a movement tax**, no
  entrapment, excavation, fire, or fauna. What it looks like, never what it does.
- **"More Fun Quicksand"** treats tar as liquid quicksand: instant immobilize,
  escape pulled back in by "higher than normal suction." The entrapment
  *feel*, with no depth axis and no economy.
- **"Buildable Terrain" (B18-era)** shipped quicksand as "far harder to walk
  through," and its own notes planned "mechanics that get pawns stuck and pull
  them under to their death" — **planned, never shipped.** The gap this doc closes.
- **Rimefeller** proves the adjacent half already exists: pipes carrying a
  viscous hydrocarbon that rupture, spill, and burn — infrastructure *built
  over* terrain. Nothing has the inverse — terrain you **dig canals INTO**.
- **What nothing ships**: tar as an archaeological medium (La Brea-style,
  richer with depth), tar as a routed and ignited weapon, or tar with an
  ecology explaining why it's there. All open ground.

⇒ Not a movement-tax tile — a **system**: terrain state, dig-site
stratigraphy, fluid engineering, economy and horror, tied to one premise
nothing else has: the tar is *made*, continuously, by a burning world, and
*made of* that world's dead.

---

## 2. Tar as terrain — the base state

**Two layers.** `RUT_TarSurface` (a crusted, walkable skin that looks solid
and is a trap) and `RUT_TarOpen` (visibly liquid, once the crust breaks or
never formed). Two failure textures: the surface kills by deception, the open
pit kills by daring you anyway.

**Movement.** `pathCost` alone gets "slow to cross" for free — Alpha Biomes
proves that much needs no code. The real piece is the **entrapment hediff**:

- `RUT_TarStuck` — applied on a failed resist check entering `RUT_TarOpen`, or
  breaking `RUT_TarSurface` (chance scales with bodySize — a rat doesn't break
  the crust, a Zoril does). Severity rises per tick stuck; escape is a
  strength-gated check per tick, the same shape as vanilla's existing
  stuck-state pattern (traps, Anomaly bindings) — a new applier, not a new
  verb.
- **Sinking is the depth axis, and it should be visible.** Past a severity
  threshold, "stuck" becomes "submerging" — a render offset sinking the
  sprite tile by tile, mirroring deep-water wading visuals. Full submersion:
  suffocation damage, the drowning clock. The single most ownable visual in
  the doc — nothing in the workshop shows a pawn actually going under.
- **Mechs sink faster, but corrode instead of suffocating** — a slow
  EMP-adjacent malfunction hediff, making tar an anti-mech hazard distinct
  from anti-organic and reinforcing R-H9's "biologically rich" framing by
  contrast.
- **Rescue is a real verb.** A stuck ally can be hauled out (rope/chain job on
  vanilla's rescue-haul skeleton), gated by a strength check that can fail and
  drag the rescuer in too — the two-pawn-down trap.

**Mechanics sketch:** two `TerrainDef`s (`pathCost`, `extraDeteriorationFactor`);
`HediffDef RUT_TarStuck` with a per-tick severity comp and `JobDriver_EscapeTar`
(new C#); a small comp deciding surface-break odds by bodySize (nearest vanilla
precedent: fire's spread roll). No DLC required; Biotech's mech-corrosion
interactions are the nearest existing lever for the mech-sink behavior.

---

## 3. Excavation as archaeology — better the deeper you dig

Makes tar **the scavenger clan's terrain**, not just a hazard. R-H9 already
rules the payoff: *bones, whole carcasses, and — the part that matters to this
campaign — things that are not bones.*

**Dig sites are stratified, not single-pull.** `RUT_TarDigSite` is a
**column**: each dig goes one layer deeper, and depth correlates with age,
preservation and danger, per the ash-water-ash-water compression R-H9
describes:

| depth band | contents | flavor |
|---|---|---|
| crust (0–1) | modern debris: scrap, a lost caravan's kit | recent, safe-ish |
| shallow (2–4) | megafauna skeletons, mostly intact (R-H2 gigantism) | archaeology begins |
| deep (5–8) | intact ancient machinery, sometimes *keyed*; soft-tissue organics | the Jawa payoff |
| bottom (9+, rare) | pre-Pyrelands strata; §6's "preserved mid-struggle"; possible Forsaken-era material | horror-adjacent, best loot |

**Intact ancient machinery is the sharpest hook**: tar preserves by excluding
oxygen and microbes, so a deep find can be **functional or near-functional**
rather than the corroded husk everything else on this world arrives in —
inverting the normal salvage loop (strip a ruin, most of it is junk) into a
rare best-case worth a slow, skill-gated dig.

**Digging costs, and should hurt:** time scales steeply with depth
(`JobDriver_ExcavateTar`, vanilla mining's yield-vs-time curve); entrapment
risk scales with depth too, since late layers sit closer to `RUT_TarOpen` —
the archaeology and the hazard are the same terrain doing two jobs, no
separate danger meter needed; and a pit past a threshold depth should be
markable as a project (mark it, staff it, defend it) rather than a one-click
harvest.

**Mechanics sketch:** `ThingDef RUT_TarDigSite` holding `CompTarStrata` (new
C#) tracking depth and rolling a per-layer loot table (junk shallow, valuable
deep) via `ThingSetMakerDef`. No DLC required.

---

## 4. TAR ENGINEERING — the owner's canal spark, built out in full

> *"Could we dig canals to let the tar flow out, then light them on fire?"*

The best idea in the brief. Three sub-systems: **flow, moats, the burn.**

### 4a. Canals — tar as a fluid you can move

Not water's (nonexistent) fluid sim, and not teleport — the right model is
**cellular spread**, the category RimWorld already ships for fire and gas: an
open tar cell with a lower neighbor (a dug canal, a breach) has a per-tick
chance to push volume into it, and the neighbor becomes `RUT_TarOpen` once its
volume crosses a threshold. Slow, visible, directional — a canal dug toward a
trench will, over hours, **fill that trench with tar**, exactly as asked.

- **Built, not automatic.** `Designator_DigCanal` carves `RUT_TarChannel`
  (lower pathCost than open tar, still flammable) as the valid downhill path
  for the spread algorithm.
- **Grade matters.** Maps aren't ruled to carry per-tile elevation today, so
  the v1 slice fakes grade with a designated flow direction on the channel;
  true elevation-driven flow is a v2+ ask if the layout tooling grows one.
- **Volume is finite per pit.** `CompTarReservoir` depletes as canals drain
  it — a colony that floods its whole perimeter has spent a resource (fewer
  archaeology finds, dryer moats), not pulled a free lever.

### 4b. Tar moats — passive base defense

A canal-fed ring around a perimeter is a moat with **no new mechanic** beyond
§2/§4a — raiders pathing through it eat the entrapment roll like a player
would. The interesting question is asymmetry: a defender who mapped their own
channels can path around them (as RimWorld minefields already handle known
vs. unknown hazards for the AI), so the moat slots into solved pathing
behavior.

### 4c. Flood-and-ignite, and why it beats grass fire

> *"...then light them on fire?"* — yes, and it should feel like the
> structural opposite of R-H4's dry-thunderstorm grass fire.

R-H4's fire is fast, self-renewing, migrating. Tar fire is the inverse, and
the contrast is the payoff:

| | grass fire (R-H4) | tar fire (proposed) |
|---|---|---|
| speed | fast, eager spread | slow-burning, low spread |
| duration | burns out, regrows | very long burn per cell — dense fuel |
| smoke | thin, brief | heavy, persistent — a screening tool |
| stopping it | rain (never here) or fuel exhaustion | fuel exhaustion only, and there's a LOT |
| tactical use | avoided | **weaponized** — flooded on your schedule, lit on your schedule |

**Mechanically:** since RimWorld's fire is mostly hardcoded to one `Fire`
Thing rather than data-driven burn profiles, this is the doc's one plausible
small Harmony patch or `Fire` subclass (`RUT_Fire_Tar`) — longer lifetime,
slower spread roll, heavier smoke via the existing `Gas`/`FleckMaker` path.
Ignition needs **zero** new mechanic: any existing fire source already
ignites `Flammability > 0` terrain, which tar terrain simply carries.

**Smoke-screening is a second payoff hiding in the first**: sustained smoke
over a burning channel degrades sight lines using vanilla's existing
smoke-accuracy mechanic, letting a Jawa base blind an approach rather than
kill it outright — fitting R-H5's ①/② faction answers (burrow, move) and the
Jawa's "avoid, don't confront" posture even in an offensive tool.

**Mechanics sketch:** flammability (data); `Designator_DigCanal` +
`CompTarReservoir` + a per-tick spread `MapComponent` — the single biggest
lift in the doc; an optional `Fire` subclass or Harmony postfix for the
slow/smoky profile (verify against source which route swaps in cleanly). No
DLC required.

---

## 5. Tar creatures — what lives in it, and why it's there at all

> *"perhaps there are creatures that live in even small pools (and propane,
> and tar) that emerge when disturbed... maybe that's why the stuff is there
> to begin with."*

The most generative line in the brief — it inverts cause and effect. Three
readings, not mutually exclusive, offered rather than ruled:

**Reading A — the tar is a digestive secretion.** A subterranean (or colony)
organism metabolizes R-H9's ash-and-flood slurry and excretes tar as waste —
every pit is a midden, which means a canal-drained pit (§4a) can **replenish
over time**, explaining tar as a renewable fuel path (R-H9) rather than a
strip-mine. It also explains soft-tissue preservation: a digestive secretion
is mildly anaerobic/preservative by design, the same real-world mechanism
that makes tar pits good fossil traps.

**Reading B — the creatures ARE the trap.** Ambush predators camouflaged as
tar-crust, striking when a pawn's weight breaks through — the direct payoff
of "emerge when disturbed." A `PawnKind` dormant/hidden (reusing RimWorld's
own dormant-until-disturbed pattern from insect nests and Anomaly hidden
entities) until the surface-break roll fires, at which point it attacks the
now-stuck, vulnerable pawn. Cleanest mechanically, scariest at the table.

**Reading C — the answer is a corpse, not a creature.** Something enormous
died (or is dying, §6) in the pit, and its slow ongoing decomposition *is*
the tar. Least new mechanical surface; pairs best with §6, at the cost of no
"emerges when disturbed" payoff unless Reading B's scavengers are drawn to it.

**Recommendation, offered not ruled:** A explains the renewable economy (§7
needs it), B delivers the horror beat directly, and they layer — one
planetary-scale secretor (A), several small ambush tenants living in its
output like barnacles on a whale (B). Gives DECIDE one creature to name and
place, unexplained per R-H8's "who deployed it stays unknowable" register,
plus a reusable dormant-PawnKind pattern for any tar tile.

**Mechanics sketch:** `PawnKindDef` (placeholder prefix only) with a dormancy
comp on Anomaly's hidden-entity pattern; `CompTarReservoir` refill tick if
Reading A adopted (data-only, reuses §4a). No new Thing categories.

---

## 6. The horror register — something big, preserved mid-struggle

R-H9 already licenses this ("things that are not bones") — the explicit
set-piece deep dig sites (§3, bottom band) should guarantee at least once.

**The beat:** a deep excavation uncovers a megafauna carcass (R-H2 gigantism)
frozen mid-motion — limbs splayed as if still struggling, sometimes a second
skeleton locked in its jaws, sometimes wrapped around ancient machinery it
died reaching for. **The tar preserves the moment, not just the remains.**
Per R-H8's house style, this needs no cause — it's more disturbing unexplained.

**As a mechanic:** a rare "the pit wakes" incident/quest hook, where a deep
dig disturbs something reading as freshly dead rather than fossilized
(physically defensible given tar's anaerobic preservation) and triggers a
Reading-B-scale emergence beyond the normal ambush tenant — rare, expensive,
rewarding, reusing the Ancient Danger risk/reward shape rather than inventing
one.

**A tar geyser** is the cheap, frequent cousin: a pressurized pocket erupts,
spraying `RUT_TarOpen` across a radius (instant, the inverse of §4a's slow
spread) and coating anyone caught in it (a "tarred" filth/hediff state,
cleaned by washing — reuses existing filth systems). Low build cost, useful
on any authored tile without needing the full dig-site or creature systems.

---

## 7. Economic uses — tar as a resource, not just a hazard

R-H9 calls the tar "biologically rich" as a resource claim to be honoured.
Cheap to expensive:

1. **Torch/lamp fuel.** Raw tar burns crude and dirty — usable immediately,
   no refining, bad smoke cost. The poor person's chemfuel.
2. **Waterproofing and adhesive.** A crafting reagent for apparel (against
   R-H2's flash floods) and construction (roofing seal, Utinni hull patching).
   Data-only, feeds existing Bill/recipe patterns.
3. **Chemfuel feedstock.** Tar cracked via refinery, parallel to Rimefeller's
   crude-to-chemfuel and Vanilla Chemfuel Expanded's deepchem chain — where
   tar formally becomes R-H9's third fuel path alongside helixien and
   propane, priced by entrapment risk and dig time rather than distance or
   cold. Reuses the Vanilla Expanded Framework `PipeNet` class wholesale.
4. **Archaeology-grade salvage** (§3) — low-volume, high-value: the
   occasional intact machine worth more than any amount of raw tar.

**Ownership tie-in:** per `ownership_settlement_spec.md`'s claim model, a tar
pit outside any settlement's territory is unclaimed ground by default — no
faction blob resolves ownership over open wilderness tar. That makes wild
dig sites one of the few genuinely no-provenance-risk salvage sources on the
planet, unlike battle loot or settlement theft. An authored pit sitting
inside a settlement's territory (a Hutt tar operation) takes the same claim
math as any other resource node there — a location-design note, not a new
rule.

---

## 8. Build ladder — RULED: everything is v1 (owner, 2026-09-01)

The old v1/v2/dream split is superseded by the sitting above: **all ten rows are
v1.** What was a scope ladder is now a build SEQUENCE (FOUNDRY orders it;
earlier stages still gate later ones technically, not by scope):

1. Terrain + entrapment: `RUT_TarSurface`/`RUT_TarOpen`, `RUT_TarStuck` hediff
   + `JobDriver_EscapeTar`; raw tar as fuel/reagent (§7.1–7.2); tar-geyser
   incident (§6) **plus the ruled tar-consumer creatures that run toward it**.
2. Canal engineering (§4a) — 🔴 build as the GENERAL RimMandrake-tier
   fluid/canal mod per the ruling (water, ooze, slime, oil, tar, propane), with
   tar as its first client; `RUT_Fire_Tar` flood-and-ignite (§4c: normal-fire
   lethality, toxic obscuring smoke); moats fall out of it (§4b).
3. Archaeology: `RUT_TarDigSite` stratified digs (§3) **plus the ruled
   tar-removal pump prerequisite** (dig enabled only while pumping against
   deep-source ooze-in).
4. Creatures: tar-secretor (§5A, slow non-magical excretion in captivity),
   ambush lurker (§5B); chemfuel refinery (§7.3: slow, gross, oozing joints);
   sinking-render for `RUT_TarStuck` — ruled a showcase: invest in real
   animation, study animation mods first.
5. "The pit wakes" set-piece (§6) with the ruled additions: tar-beast eggs
   that hatch on disturbance, maliciously buried ordnance, vindictive-faction
   territory flavor.
