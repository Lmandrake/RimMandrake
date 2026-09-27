# The Grey Deep — danger + floor design pass (2026-09-27)

Status: DESIGN DRAFT — written by a DESIGN subagent for BENCH, not yet ruled on.
Items: `GREYSEA_SHIP_CRYSTALLISATION_1` · `DARKSEA_LIGHT_ATTRACTION_1` · the Grey slice
of `SEA_FISHABLES_ALIVE_IN_DEPTHS_1`.

Sources this pass stands on (read, not summarised from memory):
`design/Jawa/worldbuilding/biomes/the_grey_deep.md` (the frozen sheet, incl. the
2026-09-26 additive merge) · `the_grey_deep_content_2026-09-26.md` (the owner's verbatim
drop) · `the_twilight_deep_danger_pass_2026-09-27.md` §D3 (the cut lamp-lure, redirected
here by owner ruling) and §D8 (the cross-sea ship-touch grammar, where the owner typed
the Grey's mechanism) · `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_GreySea.xml` ·
`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_GreySeaFish_Items.xml` ·
`src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_GreySeaFloorLife.xml` ·
`src/RimMandrake/TerminalBiomes/Source/RM_JobGiver_SeekGlow.cs` + `RM_SeekGlowExtension.cs`.

Binding constraints honoured throughout, not re-argued: the ship is the ONLY way down
and back (owner 2026-09-26, verbatim: *"It's ship or nothing"*); the sea floors are
becoming a seabed planet layer, so nothing below depends on pocket-map caching or
per-hatch persistence; the Grey's creatures are the Grey's alone; every DLC is present;
the sheet's six hard bans all hold, ban 4 (*"the only glow in the Grey Deep is the
giant's mark"*) doing the most work in §2.

## 1. Ship crystallisation (GREYSEA_SHIP_CRYSTALLISATION_1)

**The ruling this section executes.** Owner, typed, 2026-09-26 (recorded in the Twilight
danger pass §D8): *"Yes. The grey sea should crystallize the hull, freeze doors shut.
twilight drops sky panes on the ship that need to be cleared off."* Each sea claims a
parked hull in its own register. The Twilight buries; **the Grey encases** — the same
thing it does to everything else that holds still, because the sheet's oldest line is
that the sea builds on anything that holds still long enough, and a parked gravship is
the stillest, largest thing that has ever held still down there. The ship is not being
attacked. It is being *filed* — the statuary reaching for its newest exhibit.

### 1.1 What accretes

**The jacket mineral — the same one, not a new substance.** The sheet's §4d already
rules the Grey's encasement medium: a salt twin of Odyssey's `SolidIce` (mineable,
yields the salt-crystal item; defName still unassigned, deliberately — see the sheet's
"Still open"). Hull crystallisation is that mineral growing on the ship instead of on a
skeleton, laid as **crust things spawned on and against the hull's footprint cells**,
plus a **salted-shut state on doors**. One mineral family for the statuary, the pool
loot, an encased pawn, and now the hull — a player who has chiselled a salt cameo
already knows exactly what is happening to their ship the first time they see rime on
the plating.

Two feeds, both already designed elsewhere and reused here:

- **Salt snow** (sheet §4c, shipped as `RM_GreySaltSnow` on `RM_GreySea`) — during the
  weather, accretion runs faster. The snow that feeds the sessile layer also feeds the
  jacket. The floor's one visible motion is also the hull's clock.
- **Standing still in supersaturated water** — the baseline. No weather needed; parking
  IS the trigger. Proximity to a brine channel or a chimney field (sheet §4b) is a
  faster neighbourhood — the super-brine gradient the floor already teaches ("the
  gradient always points at the danger") now prices parking spots.

**Doors first.** His sentence names doors specifically, and the mechanism should too:
door cells and hull-edge seams accrete ahead of open plating (crevice nucleation — the
fiction is real chemistry). So the first *functional* bite is always the same: a door
that will not open until it is chipped, well before the hull as a whole is in trouble.

### 1.2 Pace and stages

The Grey is slow everywhere; the crystallisation is slow, legible, and never a surprise
— the same "rent, not raid" grammar as the Twilight's light famine. Proposed ladder
(numbers are design targets for tuning, not ruled):

| stage | parked time (baseline) | what it is |
|---|---|---|
| **Rime** | from ~1 day | cosmetic bloom on hull cells; no function lost; the warning IS the beauty |
| **Salted seams** | ~2–3 days | exterior doors acquire the salted-shut state one by one; each is a small chipping job |
| **Jacketing** | ~a quadrum of neglect | crust things thicken along the whole footprint; launch gate reads a crust count, departure delayed behind clearing work |
| **The exhibit** | never reached by an attended colony | a fully jacketed hull — in practice only ever seen on the wreck read (§1.6) |

Salt snow roughly doubles the rate while it falls; a chimney-field or channel-adjacent
berth is faster again. Every stage is reversible by work at any point — there is no
ratchet and no point of no return (§1.5).

### 1.3 What the player sees

The spectacle is the gauge, exactly as ruled for the Twilight's panes. No hidden
severity float that surfaces as a surprise letter:

- **Rime** renders as crust things appearing on and against the hull — white,
  cauliflower-textured, the image-02 shoreline crust grown onto plating. Marred, never
  perfect (his one aesthetic rule binds this art like all Grey art).
- **A salted door** reads on the door itself (label/overlay: *salted shut*) and greys
  out like a jammed door; the un-salt job is right-clickable on it.
- **A letter fires once** at the first salted door — teach the mechanism the first
  time, then trust the visible crust to carry the information forever after.
- **The launch gate says why**: attempting departure with crust on the footprint lists
  the count outstanding, the same read as the Twilight's pane gate — floor grammar
  shared, voice per sea.

A crystallising gravship under grey murk, doors rimed white, is also simply the best
image this biome can put on the player's own property — the statuary aesthetic applied
to the thing they love. The danger pass and the art pass are the same pass here.

### 1.4 Fighting it

- **Chipping.** Crust things are mineable/deconstruct-shaped work (the statuary's
  chisel idiom, not a new job family), each yielding a small amount of the salt-crystal
  item — **the sea pays you for evicting it**, the same bribe grammar as the Twilight's
  harvestable panes. A salted door is the same job on the door's cell.
- **Prevention by heat.** Warm hulls accrete slower: interior heating pushed to the
  hull line measurably slows the ladder. This matches the planet's one ruled softening
  mechanism (temperature, per the pit ruling) and gives engineers a fuel-for-time trade
  without adding any new machinery — it reads off room temperature the engine already
  tracks. (Position, not ruled — question 3.)
- **Prevention by motion.** Leaving resets nothing retroactively but stops the clock:
  crust only grows while parked in the Grey. A colony that works the floor in short
  visits never meets the ladder's upper stages.
- **Mod Settings** (standing rule, every mod): accretion rate slider · salt-snow
  multiplier · off-switch. Defaults = shipped behaviour.

### 1.5 Full encasement

**Never a stranding — the Twilight's binding bar is inherited verbatim.** Crust DELAYS
departure behind work the colony can always do; it never disables the engine, and it
never fires against an emergency launch already in progress. Additionally, for the
Grey's sharper tooth:

- **Doors salt from the OUTSIDE and always yield from the INSIDE.** A pawn inside can
  always force a salted door open (a short job, no tools, breaking the crust outward);
  the salt is a wall against entry and a delay against exit, never a tomb. Sealing
  pawns inside a hull they cannot leave crosses from danger into softlock, and the
  sheet's own encasement rule for pawns (mined out, recoverable) sets the register:
  dangerous, recoverable, never unwinnable.
- **The "full encasement" state is therefore a fiction the player is shown, not a
  gameplay state they suffer**: it exists on the wreck (§1.6), on the statuary's
  vehicles, and as the visible endpoint of a ladder an attended colony never lets
  finish. What full encasement *means* mechanically is simply: every hull cell carries
  crust, every door is salted, and the launch gate's count is at its maximum — hours of
  chipping, not a lost ship.

### 1.6 Cross-sea grammar (D8): every sea touches your ship in its own voice

The Twilight pass §D8(d) already names the grammar; this section is the Grey's row and
the running table:

| sea | the touch | state |
|---|---|---|
| **Twilight** | veil-fall panes bury the deck; launch gated on clearing; panes harvestable | RULED, designed (§D8) |
| **Grey** | the hull crystallises, doors freeze shut; launch gated on chipping; crust yields salt | RULED (same typed ruling), designed here |
| **Scald** | unruled — its voice is presumably heat/scale (a boiling sea furring the hull like a kettle) | question 6 |
| **Propane Lake** | unruled — presumably cold/condensate | question 6 |

Shared bones, per-sea voice: one launch-gate pattern (count things on the footprint,
delay behind a job), one never-strand bar, one bribe rule (the removal job pays), and
each sea's own material, art and fiction on top. The Grey's twist the others lack:
**its touch is also its museum** — a hull the Grey finished claiming is indistinguishable
from the statuary's war vehicles, so any wrecked ship placed on the Grey floor as
content (the picked-wreck read the Twilight pass gives its own sea) arrives
pre-explained: *a ship nobody chipped, generations on.* The wreck is the tutorial's
final panel, standing in crystal.

Engine note (design-level only): accretion state lives on the ship's own map as things
and door states — it travels with the gravship and survives the seabed-layer migration
because nothing about it belongs to the sea's map. The Grey needs no memory of your
hull; your hull carries the Grey's fingerprints.

## 2. Light attraction on the Grey (DARKSEA_LIGHT_ATTRACTION_1)

**The redirect this section executes.** The Twilight pass proposed the lamp-lure (D3:
player light draws prey, predators follow the prey into the lamplight) and the owner
cut it there and sent it here — typed, 2026-09-26: *"Actually attacking light makes
more sense in the Grey and Scald (dark on the bottom) than it does on the beautiful
lighted Twilight floor with lots of lighted everything."* On a floor full of living
light one more lamp is no signal. On the Grey, where ban 4 keeps the murk blind and
the only glow that has ever existed is the giant's mate-mark, **a player lamp is the
brightest thing this sea has contained in its whole history.** The mechanism is not a
punishment for using light; it is the sea noticing.

### 2.1 The mechanism as built (read from the source, not the doc)

`RM_JobGiver_SeekGlow` + `RM_SeekGlowExtension`
(`src/RimMandrake/TerminalBiomes/Source/`) already ship the whole light-brain, built
for the Twilight's suulk and explicitly designed shared (*"build it once as
RM_JobGiver_SeekGlow, shared"*):

- The **extension attaches per-RACE** (`DefModExtension` on the ThingDef), so casting a
  Grey creature into the system is one XML block, zero new C#. The think-tree insert is
  GLOBAL (`Animal_PreMain`) and no-ops instantly for races without the extension.
- Tunables per race: `seekChancePerCheck` (0.05), `minGlowRadiusToTarget` (1.5),
  `ticksBetweenFeeds` (180), `glowRadiusLossPerFeed` (0.15), `destroyBelowRadius` (0.3).
- It targets the brightest **player-owned live `CompGlower`** on the map — which on a
  seabed map means the ship's lamps and worklights, exactly the surface this pass wants.

Two small deltas the Grey needs from the shared base (both deliberately tiny):

1. **The settings gate is suulk-named.** `RM_TerminalBiomesSettings.SuulkActive` hard-
   gates the JobGiver; the Grey (and later the Scald) needs the gate generalised to a
   per-sea/per-behaviour Mod Setting rather than piggybacking on the Twilight's toggle.
2. **A drawn-to mode beside the feed mode.** The suulk's job (`RM_FeedOnGlow`) dims and
   eventually destroys the glower. Most Grey attractees should *approach and linger*,
   not eat the light — a second, simpler JobDef (`RM_BaskInGlow`-shaped: go near, wait,
   wander off) driven by the same extension with a mode flag. The lamp is bait, not
   food, on this sea.

### 2.2 Grey Sea tuning — who comes, and what follows

The Grey's cast is mostly **eyeless** (the essarn, the oomal, the immu, the haarn — the
murk bred sight out of nearly everything), which the design should treat as a gift, not
an obstacle: attraction here is selective, slow and readable, never a zerg. Three
layers, escalating:

**Layer 1 — the prey drifts in (the bribe).** The sighted small things come to the
light: **RM_Nissik** (the litter-pickers — illuminated water is visible marine snow),
**RM_Sallik** (crust-crabs working the lit ground), **RM_Immu** (the one animal in the
Grey with any colour, and the description already says its pink only shows *"in a
lamp"* — this creature was written for this mechanic before the mechanic existed).
Extension in drawn-to mode, generous `seekChancePerCheck`, low stakes. Player-visible
payoff: the floor around a lit hull slowly becomes the busiest ground on the map —
easier hunting, richer fishing at the lit shore cells (position: a small fishing-yield
bonus near a strong glower formalises the bribe; question 5 in spirit, cheap either
way). The lamp is the best harvesting tool the Grey sells, and the first week of using
one teaches only the upside.

**Layer 2 — the watcher arrives (the tell).** **RM_Fessk**, the ossuary shrimp, gets
the extension in drawn-to mode at long range and extreme timidity: it comes to the
*edge* of the light and stands there, half-behind a pillar, watching. It never enters
the lit circle, never attacks (ban 3 is absolute), and leaves when approached. This is
pure atmosphere and pure information: a fessk at the rim of your lamplight means the
light is being read by things with eyes — the biome telling you, in its own voice,
that layer 3 exists. The sheet already owns this beat: *"the shrimp saw you first."*

**Layer 3 — the giant answers (the danger).** The Grey deliberately has no mid-tier
predator to follow the prey in — solitude is the law — so the D3 sketch's "predators
follow" resolves onto the only thing it can: **RM_Reefback**, the crusted giant. And
the fiction writes itself off the sheet's own lines: the one glow in the Grey Deep is
the giant's saturated mate-mark, seen before anything else in the murk — so a strong,
steady, unfamiliar light burning for hours is, to the only creature wired to respond
to glow, **a rival's mark standing on its ground.** An ill-tempered solitary answers
that. Mechanically: the reefback's extension entry fires only above a high
`minGlowRadiusToTarget` (a worklight or a lit hull cluster, never a torch), at a very
low check chance — hours of burn, not minutes — and its job IS the feed mode: it comes
and it breaks the light (and whatever stands too near the light while it works). The
escalation is slow, telegraphed by layers 1–2, and entirely under the player's
control: dim the lamps, or dowse them when fresh scrape-sign appears, and the giant
never comes. Light discipline — running dark, lighting only for work windows — becomes
the Grey's survival craft, which is exactly the D3 sketch's decision surface
transplanted to the sea that earns it.

Ban 4 audit: nothing here adds a glow to the biome. Every light in this design is the
player's, brought down at their own judgement; the sea's response consumes and removes
light. The murk stays blind, and the mechanism makes the player *complicit* in every
exception to it.

### 2.3 The same mechanism on the Scald (forward note for that pass)

The Scald is the other dark-floored sea and inherits this design wholesale when its
danger pass comes up; what it needs is one XML block per participating race and its
own answer to one question:

- **Shared, free:** the JobGiver, the extension, the drawn-to job, the generalised
  settings gate — all of it race-agnostic once delta 1–2 above land. Casting Scald
  creatures is per-race XML, zero further C#.
- **The Scald's own decision:** which of its cast plays each layer. Its floor roster
  (3 inline + 3 canon patch-added, per the 2026-09-26 re-measure) needs sorting into
  attractees and an answerer — and the Scald *may* actually have a true predator to
  play layer 3 straight (prey gathers, hunter follows), where the Grey had to route it
  through the rival-mark read. That is that pass's design work, not this one's.
- **One warning carried forward:** the Scald's floor glows with heat fiction (vents,
  `RUT_ScaldVent`); its pass must decide whether natural heat-glowers are exempt from
  the attraction scan (they are not player-Faction, so the shipped code already
  ignores them — the exemption is free as built, and should be kept).

## 3. Fishables alive — the Grey's seven (SEA_FISHABLES_ALIVE_IN_DEPTHS_1, Grey slice)

🔴 **MEASURED FIRST, PER THE STANDING RULE, AND THE ANSWER IS: THIS IS BUILT.** This
pass was briefed to design living floor counterparts for the seven catch-only species.
Before inventing, the source was read — and
`src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_GreySeaFloorLife.xml`
(authored 2026-09-26, header: *"SEA_FISHABLES_ALIVE_IN_DEPTHS_1 — the GREY SEA
portion"*) already gives **all seven** a living body, each derived from its own catch
item's description exactly as the brief asks, each `wildGroupSize 1` (ban 2), and all
seven are **wired into `RM_GreySea.xml`'s `<wildAnimals>` with commonalities.** The
`RM_Essarn ↔ RM_EssarnCatch` pattern is followed (with the tier caveat below). This
section therefore does what a design pass owes a built thing: verify the derivations
against the item texts, record the shipped state as the design of record, and design
only the genuine remainder.

### 3.1 The seven, verified against their own item descriptions

Each row was checked sentence-against-field. Every one holds; the two judgement calls
the builder made are flagged and endorsed.

| species | item text (the design) | the body it got | verdict |
|---|---|---|---|
| **RM_Sallik** | thumb-sized crab-thing wearing excreted salt crust; disturb the water and it becomes a pebble | bodySize 0.1, MoveSpeed 1.0, tiny claw, Wildness 0.6 | ✅ faithful; the pebble-freeze is prose only — see 3.2 |
| **RM_Karrud** | slab-flat, palm-wide, gave up swimming; mineral plate; moves a hand's width at a time | bodySize 0.2, **MoveSpeed 0.6** ("that sentence in a number", per its own comment) | ✅ faithful |
| **RM_Hessal** | crystal-shelled bivalve, seals for years, nobody has seen one open | bodySize 0.18, MoveSpeed 0.3 (a literal 0 cannot satisfy the job graph — right call), hungerRate 0.08, lifeExpectancy 40 | ✅ faithful |
| **RM_Oomal** | blind arm-long brine-eel, always sick, never fast, lives in pillar-foot silt | bodySize 0.25, MoveSpeed 1.8, carnivore, `waterSeeker` | ✅ faithful ("never fast" vs 1.8: it is the fastest mover on this floor bar the immu, which is the item text's own relative register — nothing in the Grey is fast) |
| **RM_Maalu** | grey jelly bell half turned to stone, drifts sagging, **"It is not luminous — nothing down here is"** | bodySize 0.15, MoveSpeed 0.8, healthScale 0.25 — and the def's comment marks the no-glower clause as ban 4 written into owner-facing text | ✅ faithful; the ban-4 comment is exactly right |
| **RM_Immu** | finger-long, eyeless, lodges in dead hessal shells, most timid thing in the Grey, faint pink **"which you only see in a lamp"** | bodySize 0.08, MoveSpeed 2.2, **Wildness 0.95**, nip power 1 — "timidity in three numbers" | ✅ faithful; and §2.2 layer 1 now gives its lamp-pink line a mechanic |
| **RM_Haarn** | helmet-sized closed mineral jacket that moves pillar to pillar leaving a scrape-line *"like a very small version of the giant's"*; lives where nothing else survives | bodySize 0.4, MoveSpeed 0.5, healthScale 0.9, hooks, `manhunterOnDamageChance 0.1`, rarest of the seven | ✅ faithful; the manhunter chance is the one creature on this floor allowed to hurt you, and the item text ("divers who find one do not report it") supports leave-it-alone-or-else |

Size classes as shipped: immu (0.08) < sallik (0.1) < maalu (0.15) < hessal (0.18) <
karrud (0.2) < oomal (0.25) < haarn (0.4) — a floor of small things under a bodySize-32
giant, which is the sheet's silhouette law (verticals, one enormity, nothing in
between) expressed in numbers.

Danger as shipped: six of seven are harmless (combatPower 3–8, predator false
throughout); the haarn alone bites back when damaged. Endorsed — the Grey's danger
budget lives in the pools, the giant and §1–§2 of this pass, not in its fauna.

### 3.2 Floor-roster commonality — shipped, and endorsed as the design of record

Already wired in `RM_GreySea.xml` `<wildAnimals>`:

`RM_Sallik 0.5 · RM_Karrud 0.45 · RM_Hessal 0.55 · RM_Oomal 0.35 · RM_Maalu 0.3 ·
RM_Immu 0.3 · RM_Haarn 0.08` — beneath the sessile layer's 0.9/0.8/0.7 and above the
anchors (essarn 0.6 aside). The gradient is right: litter-pickers everywhere, the
strange stuff occasional, the haarn (0.08) a rumour. Two couplings the numbers already
respect and future edits must keep respecting:

- **RM_Hessal (0.55) and RM_Immu (0.3) travel together** — the immu lives in dead
  hessal shells; the def file's own warning (*"do not cut one without the other"*)
  is hereby repeated in the design layer.
- **RM_Haarn's rarity is load-bearing**: its scrape-line is a deliberate false
  positive against the sheet's *"fresh scrape-sign means the giant is near"* — common
  haarn would destroy the giant's tell; at 0.08 it sharpens it (a diver must learn to
  read scrape *width*).

### 3.3 The genuine remainder — what this slice still owes

1. **The catch-side tier migration (owed, recorded, not this pass's to execute).** The
   floor residents are `RM_`; their catch items are still `RUT_Sallik` etc.,
   MayRequire-gated in the Utinni layer — yet every name is an invented word, so per
   Q11a they belong in `RM_`. `RM_GreySeaFloorLife.xml`'s header records the owed
   cross-mod rename (incl. `RUT_RareGreyCatches`/`RUT_SaltCameo`). Until it lands, a
   player without `mandrake.rut.patches` gets the animals but not the catch — the free
   mod's sea is alive but not fully fishable, which is against the Q11a "looks
   precisely the same" bar. This is the slice's one real defect. ⛔ Never "fix" it by
   making the floor animals RUT_.
2. **Behaviour flourishes the descriptions promise (small, optional, ranked).** The
   defs are honest without these; each would make one sentence of item text playable:
   - *Sallik pebble-freeze* — on threat proximity, hold still (a freeze-in-place
     response instead of flee). Small C#; also makes the lit-ground forager of §2.2
     readable (pebbles that were walking a moment ago).
   - *Hessal sealing* — sealed hessal are invalid hunt/fish targets during brine
     events (salt snow): the bed "reads as frost" and closes. Ties the weather to the
     larder; teaches the fog-season rhythm.
   - *Immu shell-lodging* — flee-to-a-hessal-corpse instead of flee-to-map-edge.
     Pure charm, lowest priority.
   - *Haarn scrape-line* — a filth trail (`scrape-line in the silt`), which is also
     the giant's tell made literal; one filth def shared with the reefback at
     different widths. This one earns its place in the danger grammar (§3.2) and
     should go first of the four.
3. **Art.** All seven ship placeholder flat texPaths; real art is owed via artpipe —
   and per the standing rule, `done/` and `_artsrc/` must be searched by subject
   before queuing any of the seven.
4. **Light-attraction wiring** (§2.2): extension blocks for nissik/sallik/immu
   (layer 1), fessk (layer 2), reefback (layer 3). One XML block each once the two
   §2.1 deltas exist.

## Ruled — decisions taken by question card, 2026-09-26

1. **Hull salt: the sea pays you.** Chipped crust yields the same salt-crystal item as
   the floor jacket, in small amounts — D8's bribe grammar stands.
2. **Never a tomb.** Doors salt shut from the outside only and always force open from
   the inside. The danger is the ship's readiness, never the crew's air.
3. **No fuel-for-time trade.** Crust pace is time alone; the counters are chipping and
   leaving. Interior heat does nothing to it.
4. **The giant breaks lamps.** A strong steady player light reads as a rival's
   mate-mark; the crusted giant comes to break the light — not the ship, not the pawns.
5. **Lit cells yield more.** The fishing/gathering bonus on lit cells is in — the bribe
   half of the lure made mechanical; danger and reward share one dial.
7. **The fessk watcher is in.** It stands at the edge of lamplight and watches — never
   entering, never attacking — the layer-2 tell.
9. **RUT_→RM_ catch rename: filed for execution now** — `GREYSEA_CATCH_TIER_RENAME_1`
   (FOUNDRY), all seven invented-name catch items.
10. **All four description-promised behaviours build** with the fish-body wave (haarn
    scrape-line, sallik pebble-freeze, hessal sealing, immu shell-lodging) — the
    descriptions are the spec.

BENCH engineering decision, owner may veto: (8) the suulk-named settings gate
generalises to a per-sea light-attraction toggle when the Grey wiring lands.

## Questions for the owner — still open

6. The Scald and the Propane Lake have no ruled ship-touch voice yet (Grey crystallises,
   Twilight drops panes) — do you want to name theirs now or at their own passes?
