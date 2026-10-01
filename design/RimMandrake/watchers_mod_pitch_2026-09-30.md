# Watchers: a cross-biome mod of shy creatures (pitch, 2026-09-30)

Item: WATCHER_CREATURES_MOD_1. Design only, nothing built.

## 1. The behaviour kit

### The cycle, as four states

| state | what the player sees | what the engine does |
|---|---|---|
| **Hidden** | a sign on the ground: a hole, a mound, a ring of ripples, a shut shell | the pawn carries a hidden hediff (invisible, untargetable) and stays still; a small sign Thing marks its cell |
| **Emerging** | a dust puff or splash, then the creature's head and shoulders | the hediff comes off; one fleck + one sound; the sign Thing comes off with it |
| **Watching** | it sits still and turns to face the nearest pawn, and keeps turning as that pawn moves | one toil with `handlingFacing = true`, re-aiming every ~30 ticks |
| **Flinch** | a jerk back: a puff, a small sound, the sign appears again | the hediff goes back on, and a cooldown starts before it can emerge again |

Re-emergence comes after a random delay (default 1–3 in-game hours) **and** only once no
pawn is inside the flinch radius. Without the second condition a colonist standing on it
would see it pop up and down over and over.

### Mechanism, in RimWorld 1.6 terms (checked against the decompiled source on RimSage, 2026-09-30)

**One opt-in extension, one global think-tree insert, one job.** This is the same shape as
`RM_BurrowOnFireExtension` / `RM_JobGiver_BurrowOnFire` (Pyrelands) and the shade-follow
mechanism before it:

- `RM_WatcherExtension : DefModExtension` on the race's ThingDef. It holds:
  `flinchRadius` (default 6), `watchRadius` (default 14), `hideTicks` (an IntRange),
  `hiddenHediff`, `signDef` (the ground mark), `emergeFleck`/`emergeSound`, `medium` (an enum:
  sand, crack, water, foliage, shell), and `warnOnLargeBurrower` (a bool, the piinnok's
  geophone, see below). A race without the extension is invisible to the kit. **No species is
  named in C#.**
- `RM_JobGiver_Watch : ThinkNode_JobGiver`, spliced at Core's `Animal_PreWander` insert tag
  through a `ThinkTreeDef` with `<insertTag>Animal_PreWander</insertTag>`, exactly as
  `RM_BurrowOnFireThinkTree.xml` does. Its first line is the null-extension check, so it costs
  nothing for every other animal. Hunger, sleep, fleeing and taming all sit above PreWander in
  Core's animal tree, so a watcher still eats, sleeps and runs from a predator normally.
- `RM_JobDriver_Watch : JobDriver`, which holds the four states as toils. It is modelled on
  `RM_JobDriver_Burrow` and `RM_JobDriver_MurrekBurrow`. Their key pattern is that **one
  `AddFinishAction` removes the hidden hediff and the sign on every exit path** (emergence,
  interruption, damage, capture, death), so the hidden state can never outlive the job that
  granted it.

**Facing (verified).** `Pawn_RotationTracker.UpdateRotation()` returns early when
`pawn.jobs.HandlingFacing` is true. That property reads `CurToil.handlingFacing`. Fifty-odd
vanilla drivers use this, among them `JobDriver_Spectate`, `JobDriver_WatchBuilding` and
`JobDriver_Wait`. So the Watching toil sets `handlingFacing = true` and calls the public
`pawn.rotationTracker.FaceTarget(nearest)` (or `FaceCell`) from its `tickAction`. Facing is
**Rot4**, four directions, biased by `RotFromAngleBiased` (north below 30° or from 330°, east
up to 150°, south up to 210°, west up to 330°). So "it tracks you" will read as a quarter-turn
snap when you cross a 60°/120° boundary, never as a smooth swivel. For a twitchy creature that
snap helps. ⚠️ A member whose art has no distinct north view (a dome, a lens) shows no turn at
all, so every member needs a readable east/south/north difference.

**Hidden (verified).** `RM_JobDriver_MurrekBurrow` already does this: a hediff with vanilla
`HediffComp_Invisibility` (`visibleToPlayer: false`) drives `Pawn.IsHiddenFromPlayer()`. In
`PawnRenderer.ParallelGetPreRenderResults` that returns **before anything is drawn**: body,
hediff render nodes, shadow, all of it. `FoodUtility.IsAcceptablePreyFor` refuses hidden
prey (murrek header, RimSage 2026-09-29). The comp needs Royalty or Anomaly, which is fine
because every DLC is assumed present.
⇒ **Consequence:** while hidden, the creature itself can draw nothing, not even an overlay.
The readable sign therefore has to be a **separate Thing on the cell**, not a render node on
the pawn.

**The readable sign (the "no animal vanishes" rule).** Every hide spawns a `signDef` on the
cell, and every exit path destroys it. It is a small, non-blocking, selectable
`ThingDef` (category Ethereal or a no-pathcost Building). Its label tells the player what it
is ("sand dimple — something is under it"), and its inspect string names the medium. Five
sign families cover every medium: **hole** (crack/rock), **dimple** (sand),
**ripple ring** (water), **trembling leaves** (foliage, a cheap sway shader on a plant-like
graphic), **shut shell** (shell). Vanilla already does this kind of thing: Anomaly's
`PitBurrow` is a `Crater` subclass that stands for where things went into the ground.
Our sign is lighter (no collapse timer, no spawn queue).
- **Rule kept:** a watcher is **never invisible while it moves.** It only hides on its own
  cell. If it relocates (its cell got built over, a fire, a flood), it scuttles there
  visibly and then hides. Hidden travel would be a vanishing.
- **Dig it out:** selecting the sign gives a "flush" designation. A pawn who goes to it ends
  the hide, and the watcher emerges and flees. That is the murrek's dig-the-drift lesson, at
  small scale. It is also the hunting and taming route: you flush a watcher, you do not
  target a hole.

**The emerged look.** The kit does **not** need a graphic swap. A watcher's normal kind
graphic **is** the peek pose: head and forebody over a rim of its medium, drawn in the art.
That makes the whole family cheap to draw (one directional set, no extra layers). The
alternative is a hediff render node (`HediffDef.renderNodeProperties`, verified on 1.6) that
adds a rim of sand or water only while emerged. That is optional polish, and it is
listed in §3.

**The flinch trigger.** `flinchRadius` counts **any pawn not of the watcher's own race**:
colonists, visitors, raiders and other animals alike. A watcher is shy of everything. That
also means a map full of grazers keeps it down more often, which is an emergent
"busy ground, quiet watchers" read. Optional modifiers, all on the extension:
- a **sneak modifier**: a pawn moving slowly gets a smaller radius, so the player can creep up
  on one. Candidate signal: the current job's `locomotionUrgency` below Jog. **UNVERIFIED**, so
  check how a player can actually order a slow walk in 1.6 before building on it;
- the **geophone flag** (the piinnok): a subsurface pawn above a body size threshold (a
  hidden murrek, a burrowing threat, a tunnelling predator) within `watchRadius` makes
  **every** watcher with the flag in that radius hide at once. That is a readable warning
  the player sees as a field of lenses going dark.

### Mod Settings (per the 2026-09-12 ruling)

| toggle / slider | default | off means |
|---|---|---|
| Watchers enabled (master) | on | watchers behave as ordinary sessile animals: they sit and wander a little, and never hide |
| Hide and flinch | on | they watch (turn to face) but never hide |
| Turn to face | on | they hide and flinch but don't track |
| Readable sign while hidden | **on, locked when hiding is on** | (cannot be turned off while hiding is on: the sign is the rule, not a feature) |
| Geophone warning (lenses sink for buried threats) | on | lenses ignore subsurface movement |
| Flinch radius | 6 cells | slider 3–12 |
| Re-emerge delay | 1–3 h | slider |
| Max active watchers per map | 40 | above this, extras sit as plain animals (the performance cap) |

The kit gate for other biomes follows the biome-kit rule: the behaviour is per-race, not
per-biome, so any modder's animal opts in with the extension alone.

### Performance budget

- **Think-tree cost for non-watchers:** one `GetModExtension` lookup on PreWander. That is
  the price `RM_BurrowOnFire` already pays, and it is negligible.
- **Per watcher:** the Watching and Hidden toils throttle with `IsHashIntervalTick(30)`
  for facing and `(60)` for the flinch scan. JobDriver ticks every tick (murrek header,
  verified 2026-09-29), so the throttle has to be inside the toil. The scan walks
  `map.mapPawns.AllPawnsSpawned` once and compares squared distances. On a map with 200
  pawns and 40 watchers at 60-tick spacing, that is ~133 distance checks per tick. It is
  cheap, and a cap exists.
- **Cheaper still, if needed:** one `MapComponent_Watchers` does a single scan every 60
  ticks: it buckets pawns by region and pushes "pawn near" flags to watchers. That is only
  worth building if a profile shows the per-watcher scan matters. It is not owed up front.
- **Sign Things:** one per hidden watcher. They do not tick (`tickerType Never`), because
  the job, not the sign, owns timing.
- **Population:** watchers come through the biome's ordinary `wildAnimals` roster at low
  commonality, with `herdAnimal` false. A cluster is two to four, placed by the ordinary
  spawner. The kit spawns nothing itself.

## 2. The member family

**Method.** I read every live roster row in `design/Jawa/worldbuilding/biomes/rosters/*.json`
(cut rows excluded) and joined it to the ThingDef **description** in `src/` (2,489 defs). The
descriptions matter because a census by defName misses invented names. I keyword-flagged
55 rows and hand-read the flags. **148 donor rows have no description in `src/`**, so a donor
creature that fits could still be missing from this list. I also searched the biome sheets
for "shy / peek / pokes out". Each new member was checked against its sheet's ban list. Every
new name below returned **zero** hits in `design/` + `src/` and zero Wookieepedia search
results (sanity probes: `korrum` 54 repo hits, `jawa` found on the wiki). Two first-choice
names collided in the repo and were replaced.

**Existing creatures that already are watchers: join them first.** Joining costs one
`RM_WatcherExtension` on the def, plus a sign def and art for its peek pose:

| creature | biome | why it already fits (its own description) | medium |
|---|---|---|---|
| **piinnok** (admitted 2026-09-30, unbuilt) | Stillsand | "the one thing that tracks anything: you"; lenses sink at a buried threat | sand |
| `RM_Fessk`, the ossuary shrimp | Grey Sea / Grey Deep | "watching from half behind a salt pillar … the moment it is noticed, it is already leaving" | cover (pillar), see note |
| `RM_Thollim` | Grey Sea | "valves sitting half down in the sediment with a finger's width of gape" | shell |
| `RM_Peeper` | Contagion | "extra eyes opened in its hide until watching replaced hunting" | goo margin |
| `RM_Tarruq` | Cracked Lands | "shy … answers threat by going vertical", a crack climber | crack |
| `Shiro` (canon, Naboo) | Greentide **and** Miasma | "main defense was to retract its head, legs and tail into its spiny shell" | shell |

- The **Fessk** is mobile, not sessile, so it is a *cover* watcher: it leans out from behind
  a pillar and steps back behind it. Its sign is its own half-visible body at the pillar
  edge, so it is never invisible. That variant (`medium: cover`, no hidden hediff) is cheap,
  and it may suit other mobile shy animals too.
- **Shiro** is canon IP. Its extension goes in through the Utinni patch layer (Q11), never
  inline. It is multi-homed by an earlier placement; joining the kit changes nothing about
  where it lives.
- `RM_Orruhmu` (Grey Sea dome mimic) and `RM_Ikee` (an eye on tentacles) are near-fits
  held in reserve. The Orruhmu already *is* its own disguise; the ikee watches but has nothing
  to hide in.
- `RUT_Ashwallow` (Pyrelands) already hides with the sibling mechanism (`RM_BurrowOnFire`).
  It is a grazer, not a watcher, but the kit could absorb that code (Q7).

**New members (RM_ tier, invented names).** One per biome unless an existing creature
already covers it.

| biome | member | one-line pitch | medium | what the player gets |
|---|---|---|---|---|
| Arid Shrubland | **vellisk** | a crust-lizard under venomvine roots that leans out toward the light, and toward you, like everything here | crust hole | food (small), and a tame-able base alarm |
| Desert / Long Shade | **ennuk** | a palm-sized sitter under shade-plant root plates, out only while it is in shade. Kept off hardpan (desert ban 6) | sand dimple | its dimples mark damp sand: a readable "dig here" for the water table |
| Stillsand | **piinnok** *(existing)* | the watching glass | sand | geophone warning of buried threats; better biosilica |
| Abyss | **skeyr** | a fog-crevice sitter whose pale throat-pouch is all that shows. It "sees" only your light (no clean sensing) | crack | it ducks from carried light, so a skeyr in view means your pawn is dark-adapted and unseen. Leather |
| Nightside Ice | **hessarn** | a seam-grazer in ice cracks that turns a heat-pit face toward warm bodies and draws down into the crack. **Thermal sensing only**; it retracts in place and never flees (ban 7/8) | ice crack | food; a "warm thing near" tell in a biome where you can see little |
| Poison Forest | **ulvoss** | a black-purple vent-crust sitter peering from chemical-vent holes | crust hole | it also flinches from tox gas in its cell, so a field going down is a gas warning. Chem-resistant hide |
| Blue Desert | **kuvvel** | a hydrocarbon-blooded drift-sitter with one eyestalk above the ice-sand | ice-sand dimple | geophone flag tuned to **buried murrek**: a drift whose kuvvel all sink holds one. *(The same flag as the piinnok, said plainly: that is the kit's point)* |
| Contagion | **`RM_Peeper`** *(existing; ban 3: no new natives)* | the watcher-kin | goo margin | sky-reader; nothing new owed |
| Cracked Lands | **`RM_Tarruq`** *(existing)* | clings at a slot-wall crack, watches, slips in | crack | already the biome's second warning (the hush); the kit adds the visible half |
| Fever Wood | **phennu** | a soft six-eyed thing in crown-tree knot-holes; only the eye-ring shows | knot-hole (foliage) | mood: a small "watched by the wood" thought (sign chosen in Q4) |
| The Forge | **zhaskel** | an ember-dark plated sitter in cooling-crust fissures, never in lava (ban 1) | crack | its fissures are cool ground. If Odyssey's `LavaEmergence` has a pre-signal (**unverified**), zhaskel going down is the warning |
| Greentide | **Shiro** *(existing, canon)* + **wennoq** | wennoq lives rolled inside a broad leaf and unrolls to look | leaf-roll (foliage) | wennoq: tame-able, a pet with a mood bonus |
| Grey Sea / Grey Deep | **`RM_Fessk`** + **`RM_Thollim`** *(both existing)* | the undertaker who watches divers; the clam that gapes | cover; shell | Fessk: an eerie read, never tamed or fought (ban 3). Thollim: food, as now |
| Lantern Deeps | **thrennick** | a void-wall sitter that sinks for anything big in the dark | wall pocket | a dark wall of shut thrennick ahead means something is already there. No glow (ban 6) |
| Miasma | **Shiro** *(shared)* + **lussaq** | a six-legged root-sitter whose eye-fan is banded like the rainbow flora | mangrove-root hole | mood (beautiful); food |
| Propane Lakes / the Chill | **pralq** | a frost-crust sitter on the lake margin that flinches from **heat**, not just bodies | frost crust | a field going down means something hot is near the propane: a fire-risk read. Never transportable (R-H10). ⚠️ Spawns nowhere until `PROPANELAKE_ANIMALDENSITY_ZERO_1` closes |
| Pyrelands | **ttekku** | an ash-hole sitter at burn edges that pops up into the fertilized ash after a fire passes | ash hole | after a burn, ttekku up = the ground is safe to walk. Food |
| The Rot | **mollugh** | a fungus/animal hybrid (ban 2) that pulls itself under its own cap and becomes one more mushroom | own cap (shell) | food, fresh only (ban 4) |
| Rust Cathedral | **none proposed** | ban 7: no ordinary wildlife; anything here would be machine and touch the §GM ban | n/a | see Q8 |
| The Scald | **hveshk** | a sinter-rim sitter on the mineral shore, never in the boil (ban 4) | sinter hole | it also flinches from steam bursts: a boil warning |
| Scarlands | **okkash** | lives under fused-glass plates and peeks from the plate edge | glass plate (shell) | it goes down when a Sentinel patrol passes, so it maps where the lines are. Sharp glass flakes |
| The Slime | **uuloq** | a nodule living inside the slime body as a pocket; a bubble-eye breaks the surface. The Slime is its armour (ban 5) | gel | jelly food. No sentience read (ban 1) |
| The Sump | **thossa** | only its eye-blister breaks the tar surface | tar | thossa gone = the tar is unsafe to cross. Wax/bitumen |
| Twilight Sea / Deep | **yennith** | a fan of three eyestalks rising from a silt tube | silt tube | food. ⚠️ The sea rule: owes a floor def **and** a `fishTypes` catch def |
| The Webwork | **qellith** | a thread-hermit in abandoned silk cocoons, peering out of the exit hole | cocoon (shell) | it goes down for a Wyyyschokk: an early spider warning |
| Wasteland | **haddoq** | lives in spent ordnance casings and peeks from the barrel mouth: war-shaped, per ban 4 | casing (shell) | its casing is salvage. It is never the headline threat (ban 3) |
| Weeping Stones | **ommeth** | a pool-rim sitter in weep-stone pores whose upright comb stays out when it hides, so the comb *is* the sign (the comb ban) | stone pore | mood (serene); never ambushes at water (ban 5) |

**Count:** 27 biomes. 26 get at least one member, Rust Cathedral gets none. That makes **29
member rows**: 7 existing creatures (piinnok, Fessk, Thollim, Peeper, Tarruq, and Shiro in two
biomes) and **22 new**. The Fall Line is a region with no roster of its own, so it is not
counted.

**Ban-check notes.** Watchers never pursue, so the desert/Fever Wood chase bans hold. No
member is medium-sized in the Stillsand. The Nightside member uses thermal sensing only. No
member glows in the Grey or Lantern Deeps. Every sea member owes the floor+catch pair.

## 3. Open questions for the owner

Each is a plain choice. The first three decide the build; the rest can be ruled at each biome's
sitting.

**Q1. How does a watcher hide?**
- **(a) Invisible in place + a sign on the cell** (recommended). This reuses the murrek's
  verified hediff. It is cheap to flip many times an hour, and the job keeps its state. The
  sign is a separate Thing the code must keep in step with the hediff, with one finish
  action cleaning both.
- **(b) It goes *into* a den Thing (despawned, held inside it).** A hidden watcher then
  costs zero ticks, and the den is the sign by construction, so it can never be missing. But
  every flinch is a despawn/respawn (heavier, and the job is lost), and save/load holds a
  pawn inside a building.
- Trade: (a) is lighter for frequent flinching; (b) makes the readable-sign rule impossible
  to break.

**Q2. Who makes it flinch?**
- **(a) Anything that isn't its own kind** (recommended): colonists, raiders, other animals.
  It reads as truly shy, and busy ground keeps watchers down.
- **(b) Only people** (humanlike pawns). The player feels singled out: "it watches *you*."
  But a predator walking past is ignored, which reads oddly.
- **(c) People plus anything bigger than itself.**

**Q3. One mod, or the kit inside the unified biomes mod?**
- **(a) Its own mod, `RimMandrake.Watchers`**, holding the kit and the RM_ members. Each
  biome adds its member through its own roster. The family can be switched off whole, and
  you suggested it "might even be a mod of its own".
- **(b) The kit as a feature inside `RimMandrake.Biomes`** (the Q17 unification), with
  members living in each biome's file. Fewer mods, but no way to turn the family off as one
  thing except a settings toggle.
- Trade: (a) is cleaner to share and toggle; (b) is one fewer dependency for the player.

**Q4. Does seeing one do anything to a pawn's mood?**
- **(a) Nothing.** It's ambience and information only.
- **(b) A small positive thought** ("a little watcher peeked out at me").
- **(c) Per biome:** cute in the Greentide/Miasma, eerie in the Grey Deep/Lantern Deeps
  (the Fessk *should* feel unsettling).

**Q5. Can a tamed watcher be a living alarm?**
- **(a) Yes:** a tamed watcher at your base still hides when a **hostile** comes near, and the
  sign is a readable alarm. That is a real reason to tame one.
- **(b) No:** tamed watchers are pets only, and tameness switches the behaviour off.
- Some members are never tameable either way (the Fessk by ban; the pralq, which cannot be
  transported).

**Q6. How do you hunt or catch one?**
- **(a) Flush only** (recommended): you can't target a hole. A pawn sent to "flush" the
  sign makes it emerge and bolt, and then it's fair game. This matches the murrek's
  dig-the-drift.
- **(b) It can be shot while peeking.** Simpler, but hunting it becomes a reaction-time game
  the AI always wins.

**Q7. Should the kit absorb the Pyrelands burrow-on-fire code?**
- **(a) Yes:** one "hide" engine, with fire as one more trigger. Fewer parallel mechanisms,
  but it touches shipped, working Pyrelands code.
- **(b) No:** keep them separate; the watchers copy the pattern and leave the burrow alone.

**Q8. The Rust Cathedral: a machine watcher, or none?**
- **(a) None** (as written). Ban 7 (no ordinary wildlife) stands untouched.
- **(b) A machine watcher**: something in the cables that turns to follow you. This needs
  care with the §GM ban (no truth about the mind in player text).

**Q9. Peek art: baked in, or a rim layer?**
- **(a) Baked:** the creature's only sprite *is* its peek pose over a rim of its medium. One
  art set each, cheapest.
- **(b) A plain creature sprite plus a rim layer** drawn by a hediff while emerged
  (`HediffDef.renderNodeProperties`, verified in 1.6). The creature looks right when it
  scuttles to a new spot too, but it doubles the art and needs a medium-specific rim.

**Q10. How many new creatures, and when?**
- **(a) Wave 1 = the kit + the 7 existing members** (piinnok first). The 22 new ones are
  admitted biome by biome at each sitting (recommended: the per-biome review process you
  set, not a sweep).
- **(b) All 29 at once.** That is 22 creature defs and 22 art sets.
