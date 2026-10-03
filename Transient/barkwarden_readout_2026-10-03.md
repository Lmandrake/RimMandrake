# The sweetline tree, its wool, and the bark-warden: a full readout (2026-10-03)

Written for the owner, who said: *"I need an entire readout of what you currently have for these
guardians and how they relate to the wool. This is all reading as very sketchy right now."*

Every claim carries one of four tags:

- **BUILT**: exists in the repo, with the file named.
- **RULED**: the owner decided it, with the date and where it is recorded.
- **PROPOSED**: written in a design doc only. Nobody ruled it and nothing is built.
- **UNDECIDED / CONTRADICTORY**: open, or two sources disagree.

**The short version.** The tree and the wool are built. The bark-warden is not: no creature def,
no art, no code, only two design docs that partly disagree. The wool's in-world story (giants
rub wool onto the bark) is **only a story**. No giant ever goes near a tree in code, and the
giant carries no wool at all. The tree makes its wool from nothing on a timer. And as built,
harvesting the wool makes you **worse off** than leaving the tree alone (§2.5). That is the main
reason this reads as sketchy.

Sources read in full: `design/Jawa/worldbuilding/biomes/sweetline_guardian_spec.md` (the
"spec", 2026-09-21), `…/leaningscrub_sweetline_guardian_activation_2026-10-02.md` (the
"activation doc"), `…/arid_shrubland.md` (the biome sheet), `…/leaningscrub_bedazzle_review_2026-09-29.md`
and `…_bedazzle_cast_2026-09-29.md`, `…/leaningscrub_sweetline_name_register_2026-10-03.md`, the
four items (`LEANINGSCRUB_SWEETLINE_GUARDIAN_1`, `SHRUBLAND_TREE_GUARDIAN_1`,
`TREE_GRAPHICS_OWNERSHIP_1`, `SHRUBLAND_GIANT_ENRAGE_1`), and the built defs and C# named below.
Engine facts marked "engine" were read from the decompiled 1.6 source.

---

## 1. The tree

### 1.1 What it is

| | | tag |
|---|---|---|
| Player name | "sweetline tree" (defName `RM_SweetlineTree`) | BUILT. The player-facing name was never formally ruled (biome sheet: "likely settled by use … confirm"), so it is UNDECIDED. |
| Where defined | `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_SweetlineTree.xml` (mod `mandrake.rm.leaningscrub`) | BUILT |
| Old twin | `RUT_SweetlineTree` in `src/RimUtinni/AshkarrFlora/`, frozen and left in place until the old world def is deleted | BUILT (legacy) |
| Fiction | "Huge, ancient, powerful things, never small trees." Grows only on the sweetline, is a surveyor's mark seen from a day's walk, has a name, and the roads run tree to tree. | RULED (biome sheet §4, owner) |

### 1.2 Stats (BUILT, `RM_SweetlineTree.xml`)

| stat | value | note |
|---|---|---|
| Hit points | 650 | flavour, "not a balance pass" (`TREE_GRAPHICS_OWNERSHIP_1`) |
| Flammability | 0.1 | the biome bans flammable living flora |
| Mass / outdoor beauty | 900 / 10 | flavour |
| Drawn size | 7.7 to 10 cells wide, on a **one-cell** footprint | a big picture on one tile, not a multi-tile object |
| Grow time | 240 days | four in-game years from seed to full size |
| Harvest work | 4200 | long; the activation doc's meter is timed against this |
| Harvest product | giant-wool, 20 at full growth | see §2 |
| After harvest | growth resets to 5%; the tree is **not** killed | engine: a non-zero `harvestAfterGrowth` means a harvest never destroys the plant |
| Cut vs Harvest | the same act on this tree; both give wool, neither fells it | engine (activation doc §3) |
| How it dies | damage only: weapons, explosives, fire | engine |
| Art | 14 variants (A to N) in `src/RimMandrake/LeaningScrub/Textures/Things/Plant/RM_SweetlineTree/` | BUILT, but see §6: `TREE_GRAPHICS_OWNERSHIP_1` is still BLOCKED waiting for you to pick among 14 recovered art candidates, so whether these 14 are your pick is UNDECIDED. |

### 1.3 Where it grows: nowhere yet

**It spawns on no map** (BUILT that way on purpose). It is left out of the biome's wild-plant list
(comment in `src/RimMandrake/LeaningScrub/Defs/BiomeDefs/RM_LeaningScrub_Biome.xml` around line
208), because a sweetline tree is meant to be a hand-placed landmark, not random scatter. Placing
them is owed as a world-editing pass under `TREE_GRAPHICS_OWNERSHIP_1`. **Nobody has decided how
a tree reaches a map**: hand-placed in the frozen world, a map-generation step on sweetline tiles,
or a rare wild entry. So today the only way to see one is to dev-spawn it. (UNDECIDED)

### 1.4 Naming (BUILT, with the vocabulary still a DRAFT)

- Each tree rolls a name the first time it spawns, unique among sweetline trees on that map, and
  keeps it in the save. It shows as *"Gomaun (sweetline tree)"*. Code:
  `src/RimMandrake/LeaningScrub/Source/RM_SweetlineStation.cs`.
- The word list is `RM_NamerSweetlineTree` in
  `src/RimMandrake/LeaningScrub/Defs/RulePackDefs/RM_LeaningScrub_Namers.xml`. It has three
  patterns: an old coined name (*Gomaun*), the old name with an epithet (*Dolmaun the Woolgiver*,
  *Old Belaun*), or an event name (*Where the Giant Knelt*).
- The register is a **DRAFT awaiting your three answers**
  (`leaningscrub_sweetline_name_register_2026-10-03.md`): keep the two layers? name trees after
  people? is "Where the …" too long?

### 1.5 The History button (BUILT, same file)

Selecting a tree shows a **History** button. It opens a list of up to 12 dated entries: when the
tree was named, each time it shed wool, "struck by <whoever>" (at most once a day), and road-party
camps and pilgrim visits (the visitors feature, home maps only, gated by its own setting). The
inspect pane also counts visitors and shows when the next wool shed is due.

### 1.6 Wool shedding (BUILT, same file)

A **fully grown** tree drops **5 giant-wool every 5 days** on the ground beside its trunk. The
first shed is staggered so the trees on one map do not all shed at once. It is gated by the
**"Named sweetline trees"** Mod Setting (`RM_LeaningScrubMod.cs`, around line 207). Details and
the problem with it are in §2.

---

## 2. The wool: the part that reads as sketchy

### 2.1 How many wools exist?

**One item in play: giant-wool**, defName `RM_SweetlineWool`, in
`src/RimMandrake/LeaningScrub/Defs/ThingDefs_Items/RM_SweetlineTree_Items.xml`.

- Its old twin `RUT_SweetlineWool` (`src/RimUtinni/AshkarrFlora/Defs/ThingDefs_Items/RUT_SweetlineTree_Items.xml`)
  is identical and frozen. It only exists for the old world def.
- **The giant does not have a wool.** The giant is the thunderstep, `RSW_ShrublandGiant`
  (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_ShrublandGiant.xml`). It has no shearing
  comp, no wool product and no wool drop. Its leather is reused Fambaa leather and its meat is
  reused gorg meat. Its description never mentions wool.
- So "the sweetline wool" and "the giant's wool" are **the same item**, and **the tree is its only
  source** in the game.
- A third wool-like thing exists: the **pilgrim's token** (`RM_SweetlineToken`), "a knot of
  braided silver-grey wool" that visitors leave at the trunk. It is a trinket worth 3, not a
  material, and it is not made from giant-wool by any recipe.

### 2.2 Where does the wool on the bark come from?

| question | fiction (biome sheet, item descriptions) | what the game actually does |
|---|---|---|
| Who grows the wool? | The giants. They rub their flanks on the tree and the bark snags their wool. | **The tree.** Wool appears on a timer (the shed) and as the tree's harvest growth. Nothing involving a giant. |
| Do giants visit trees? | Yes; the bark is "scarred smooth where the giants have rubbed". | **No.** No code or def makes a giant walk to, rub or stand near a tree. |
| Does the tree need giants nearby? | Implied, since no giants means no wool. | **No.** A tree sheds and regrows wool on a map with no giants at all. |
| Are giants even on the map? | Yes, the giants are the biome's centrepiece. | Only in the **campaign layer**: `RSW_ShrublandGiant` is added at commonality 0.35 by `src/RimUtinni/UtinniPatches/Patches/WildAnimals_LeaningScrub.xml`. The free `RM_` Leaning Scrub roster has **no giant at all** (the art plan renames it `RM_Thunderstep`, not done). |
| Is there wool "on the bark" you can see? | "long silver hanks" on the bark | **No object or graphic.** The harvestable wool is just the tree's growth number. The tree art shows no wool. |

**Verdict: CONTRADICTORY.** The fiction says the wool is the giants'. The mechanics make it the
tree's. The tree's description and the shed's History line ("snagged from passing giants") tell
the player a story the game does not simulate.

Real choices, for you (none is ruled):

- **(a) Keep it as fiction.** The tree "grows" the wool; the text just explains it. Cheapest, and
  it is how things work today.
- **(b) Tie wool to giants nearby.** For example, a tree only refills (or refills faster) if a
  giant has grazed within some radius recently. Real ecology, but a map with no giants then has
  no wool.
- **(c) Make giants actually go to trees and rub.** A behaviour where a giant now and then walks
  to a tree and stands at it, and each visit adds wool. The most alive, and the most work.

### 2.3 Yields and rates (BUILT, numbers from the defs plus the engine)

| route | amount | timing |
|---|---|---|
| **Harvest** (Harvest or Cut job on the tree) | **10 to 20**. 20 needs a full-grown, undamaged tree; 10 at the earliest harvestable point; a damaged tree yields less (down to half). The harvester's plant-yield stat applies on top. | First harvest when growth reaches 40%. After a harvest growth drops to 5%, so the **next harvest is about 84 growing days later** (240 × 0.35). Trees do not grow at night or in bad temperatures, so in real time it is longer. |
| **Shed** (free, on the ground) | **5** | every 5 days, **only while the tree is 100% grown** |

### 2.4 What the wool is worth and what uses it (BUILT)

- **Value:** 5.5 silver each, so a 20-wool harvest is about 110 silver.
- **Fabric (it is a "wool" stuff):** sharp armour 0.42, heat armour 1.3, cold insulation 36, heat
  insulation 14. The description calls it "warmer than any sheared fleece". It can make clothes
  like any wool. It is set as rare in random generation (0.04).
- **The one recipe:** a **smother-blanket** takes **15 giant-wool + 40 fuzz fiber** at a tailoring
  bench (`src/RimMandrake/LeaningScrub/Defs/ThingDefs_Items/RM_SmotherCraft.xml`). The blanket is
  thrown over a venomvine thicket to kill it slowly and produce dead venomvine fuel. This is the
  wool's only special use. A full harvest buys about one blanket.
- **Its stack icon:** the def points at `Things/Item/Resource/RM_SweetlineWool`, and no such file
  is in the mod. The def header says this is expected; a note in the Sump mod claims the wool
  "omits texPath" to inherit a default icon, which is **false**. It may show the missing-texture
  placeholder in game. UNMEASURED live.

### 2.5 The built numbers punish harvesting (CONTRADICTORY, found in this pass)

The shed only runs while the tree is **100% grown** (engine: a plant counts as "mature" only
above 99.9% growth). A harvest drops it to 5%. So:

- **Leave the tree alone:** 5 wool every 5 days, free, forever. That is about **1 wool a day, 60
  per in-game year** (a RimWorld year is 60 days), with no risk and no fight.
- **Harvest it:** 10 to 20 wool once. The shed then **stops** until the tree regrows to 100%,
  which is 240 × 0.95 = **228 growing days** (nearly four in-game years). You give up roughly 228
  free wool to get 20.

So the "rare hanging harvest for whoever dares the traffic" is the **worse deal**, and the danger
the bark-wardens add (§5) guards the worse option. The shed was tuned as "a trickle beside the
20-hank harvest" (comment in `RM_SweetlineTree.xml`), but it is not a trickle: in the 84 days a
harvest takes to come back, the shed gives about 84 wool, four harvests' worth. The shed also has **no cap**, so an unvisited tree keeps piling wool by
its trunk.

Picking up shed wool is **never** harm (activation doc §3, PROPOSED, and consistent with today's
ruling that only harvesting wakes them). So the safe free wool is unguarded and the dangerous
harvest is guarded.

This needs your call (§6). The obvious fixes: shed much less (say 1 to 2 wool per 10 to 15
days, capped at a small pile); let a harvested tree keep shedding; or make the shed the
"windfall" and the harvest clearly the big prize.

### 2.6 "The harvest and the nest are the same object" (PROPOSED)

The spec (§5) says the bark-warden's bower **is** the wool on the bark: *"the harvest and the roost
are one object, which is why harvesting is an attack on it."* That is the whole reason a harvest
angers them. In the game:

- The bower is **not a Thing**. There is no nest object, no nest graphic, and no link between the
  wool and the wardens beyond the rule "working the tree raises the disturbance meter".
- The spec says they "line their bower with the giant-wool snagged on the bark" and that the coat
  is "the silver-grey of the wool it sleeps in". Both are flavour text.
- If the tree's wool is harvested, nothing happens to the wardens' comfort, numbers or mood.
  Nothing was proposed for that either.

So "harvest = robbing the nest" is an **idea with no mechanism**. If you want it to be real, the
simplest version is: after a harvest, the wardens stay restless (the meter drains slower) until
the wool regrows past some point, which shows the nest has been stripped.

---

## 3. The bark-warden (nothing built)

**Nothing is built.** There are zero hits for `RM_Barkwarden` in `src/`: no def, no art, no
code. Everything below comes from the spec unless the activation doc changed it.

| aspect | what we have | tag |
|---|---|---|
| Exists at all, as **one generic species** (not one unique per tree) | card 2026-09-21, option (b) | **RULED** (`SHRUBLAND_TREE_GUARDIAN_1`) |
| Name "bark-warden", defName `RM_Barkwarden` | card 2026-09-25 | **RULED** |
| Lives in the Leaning Scrub's own free `RM_` mod (invented name, so not Star Wars IP) | Q11a test, 2026-09-26 | **RULED** |
| Gated by the "Named sweetline trees" setting | item criteria | **RULED** (by the item) |
| Body | a knuckle-walking climber about the mass of a large dog, long arms, hook claws, flat wide head, silver-grey coat | PROPOSED (spec §1) |
| Size and stats | body size 1.2, health ×1.6, speed 4.8, armour 0.20 sharp / 0.15 blunt, combat power 110, market value 420 | PROPOSED (spec §4) |
| Attacks | bite 15; two hook-claws 12 each with a stun-6 opener (the "drop from the crown"); headbutt 6 | PROPOSED |
| Why medium | the biome bans residents between body size 1.5 and 3.5; the guardian is capped at 1.4 | the ban is RULED (biome sheet); the 1.2 is PROPOSED |
| Weight of a full tree | 2 to 3 wardens = 220 to 330 combat points: one colonist alone loses, two with guns win | PROPOSED |
| Flight | **does not fly**; it climbs and drops | PROPOSED (spec §8), consistent with the flyer rule |
| Diet | omnivore animal, eats fuzz; **not a predator** (a predator would leave the tree to hunt and attack your pets) | PROPOSED |
| "Eats the bark-lickers" | spec §1: it eats "bark-lickers, the runway animals that come to the trunk" | **INVENTED.** No creature called a bark-licker exists in any roster or def. The spec also says the line is "description text, not a predator". |
| Day to day | Activation doc: **asleep on the tree** (vanilla dormancy), hunger and rest frozen while asleep. Spec: **awake**, wandering within 12 cells and walked back by a leash. | CONTRADICTORY between the two docs. Your ruling today ("they watch") fits the sleeper version. |
| Seen in the crown? | Spec §1: *"invisible in the crown until it is not."* Activation doc: visible pawns on the tree from the start, with an inspect line "Roosting in the crown of <tree>". | **UNDECIDED.** This is the question you deferred today. |
| Where it physically is | Code can only place a pawn on a ground cell. "In the crown" can only mean standing on or next to the trunk cell, drawn under (or over) the canopy. Nothing proposed draws it up in the branches. | gap, see §6 |
| Number per tree | 2 to 3 (activation doc setting: 0 to 4) | PROPOSED |
| Spawning | spawn with the tree, near the trunk, as wild animals with no faction; **never** in the biome's wild-animal list | PROPOSED |
| Refill after deaths | spec: one every **8 to 14 days**; activation doc: **30 to 60 days**, so that clearing a tree buys about one harvest | CONTRADICTORY, unreconciled |
| Leash | spec: walked home past 12 cells; activation doc: leashed within 3 cells only while "watchful" after a fight | CONTRADICTORY (follows from asleep vs awake) |
| Breeding | spec: young born on the map inherit the mother's tree if there is room. Activation doc: sleepers with frozen needs, so whether they ever breed is unaddressed. | UNDECIDED |
| Who it can attack | Only tool-users and humanlikes. The engine's manhunt targeting cannot pick an animal, so pets and wild animals are always safe. | engine fact (spec §2, measured 2026-09-21) |
| Shooting one | Wakes that one (vanilla wake-on-damage), then it charges the shooter as ordinary revenge (100% revenge chance) | PROPOSED |
| Hunting | allowed. Whether you can order a hunt on a **sleeping** one is **UNMEASURED** (activation doc). | PROPOSED + UNMEASURED |
| Taming | allowed but hard (wildness 0.95, trainability Advanced). A tamed one stops guarding and its tree refills the slot. Taming means standing in the zone with food. | PROPOSED |
| Drops | meat and leather reused from whatever body it borrows. **No wool, no special drop**, on purpose: if killing them gave wool, the tree would be scenery. | PROPOSED |
| If the tree dies | the wardens become ordinary wild animals; they never vanish | PROPOSED |
| Sound | breath and claws, no roar ("danger announces itself by posture, never by voice") | PROPOSED, from the RULED biome register |
| Art | **none exists, none queued.** Plan: reskin an existing quadruped body in silver-grey (as the giant reskinned the Fambaa); new art only after you see the reskin. No canon target exists because it is an invented species. | PROPOSED (spec §10) |

The **leftover stale lines** in the spec are listed in §6.

---

## 4. The ecology loop

What the fiction says, and which links the game actually runs:

```
   GIANT (thunderstep) ──rubs flanks──▶ TREE BARK ──snags──▶ GIANT-WOOL
        │   (fiction only: no rubbing,       │                 │
        │    no giant wool in game)          │ grows / sheds    │ harvested by Jawa
        │                                    │ (BUILT: timer)   │ (BUILT) or picked
        │ stamps out fire and its source     ▼                  ▼ up from the shed
        │ (RULED, not built)          BARK-WARDENS ◀──"nest"── wool (fiction only)
        │                              sleep in the crown (PROPOSED)
        │                                    │
        │                     harvest work / wounding the tree
        │                     fills the meter (RULED today)
        │                                    ▼
        └───────────────────────▶ JAWA HARVESTER ◀── wardens drop on them ~halfway
                                                     (RULED today)

   Other fauna:  zellik perches on sweetline boughs; shirrel climbs a tree to glide on the Gale
                 (both in the bedazzle cast, description only, no tree code).
                 "Bark-lickers" that the wardens eat: INVENTED, no such creature exists.
                 Wardens can never attack an animal (engine).
```

Running in the game today: **tree → wool (timer and harvest) → smother-blanket**. Everything else
on the diagram is text.

---

## 5. Activation, as ruled today

**RULED by question card, 2026-10-03** (ledger note on `LEANINGSCRUB_SWEETLINE_GUARDIAN_1`):

1. **Walking up is not hostile.** The wardens watch you, and you can see they are watching.
   Traders and travellers are safe; a colony can live next to a tree.
2. **Harvesting the wool wakes them gradually.** They stir, then grow restless, then drop on the
   harvester **about halfway** through the job.
3. **A harmed tree forgives in about 5 days** (adjustable in settings).
4. **Open:** are the wardens visible in the crown from the start (the activation doc's
   recommendation) or hidden until they drop?

**The mechanics behind those rulings** (PROPOSED in the activation doc, every number a proposal):

| piece | how it works |
|---|---|
| The meter | Each tree stores a "disturbance" value from 0 to 100%. |
| What fills it | Harvest or Cut work on the tree: +10% per 250 ticks of work. A finished harvest: +25%. Wounding the tree with a pawn behind it: + damage ÷ 20 (two rifle shots wake them). Fire with nobody behind it: fills the meter, but they wake "watchful" with nobody to attack. |
| What never fills it | walking, standing, camping nearby; picking up shed wool; animals (even tamed ones) doing anything |
| Stages | 30% "stirring": a caution message, "whoever is working the tree should stop". 60% "restless": a threat message, "about to drop". 100% "awake": they drop on the person who last caused harm, with a threat message naming them, plus a History entry. No letter. |
| Timing | At normal work speed a harvest reaches 100% after about 2500 ticks, about 60% of the job. This matches "about halfway". |
| Who they attack | **Only** the pawn who caused the harm. They use the already-built scoped rage (`src/RimMandrake/CreatureBehaviors/Source/RM_MentalState_ScopedAggression.cs`, BUILT, first written for the giants), which is hostile to one pawn and never sets off a faction war. It ends when that pawn is dead, downed, gone, or more than 18 cells from the tree, or after about 1 in-game hour. Others can shoot them, and they will turn on whoever shoots them (normal revenge). |
| Taming one | does not protect its handler; a harvest by the handler still counts |
| After the fight | they go back to the trunk and stay awake and "watchful" until the meter drops below 30%, then go back to sleep |
| Forgiveness | the meter drains 20% a day, so it is fully calm within 5 days |
| Watching sign | a tool-user within 9 cells gets a "watching" icon over the wardens and an inspect line "watching <pawn>". No hostility. |
| Tree inspect | "Bark-wardens roost here (3). Calm." plus a disturbance bar with 30% and 60% marks |
| Settings | 5 switches under "Named sweetline trees": guardians on/off, wardens per tree (0 to 4), how fast harvesting disturbs them (0 to 3×; 0 = harvesting is never harm), days to forgive (1 to 30, default 5), and an **opt-in** "also charge anyone who lingers" (off by default) |

**Built today:** only the History log's "struck by" line and the scoped rage state. The meter,
messages, roost, guardian code, settings and creature are all unbuilt. The build is about 450
lines of C# plus 3 to 4 XML files, one FOUNDRY pass and one quicktest (activation doc §6).

**One engine risk, UNMEASURED:** every vanilla sleeping creature belongs to a faction or a group.
Nobody knows whether a factionless wild animal **stays** asleep. If it gets up, a small extra
think-tree piece puts it back to sleep. The first quicktest step is "wait 2 days, are they still
asleep?"

---

## 6. What is thin, contradictory or invented, and what needs you

### 6.1 The list, worst first

1. **Harvesting is worse than not harvesting** (§2.5). The free shed (about 1 wool a day, uncapped,
   unguarded) outproduces the guarded harvest (20 every 84+ days), and a harvest **switches the
   shed off** for about 228 growing days. The danger guards the worse option.
2. **The giant–wool link does not exist in the game** (§2.2). The giant has no wool, never visits
   a tree, and is only on the map in the campaign layer. The tree's description and its History
   line ("snagged from passing giants") narrate an event that never happens.
3. **The tree is on no map, and nobody has decided how it gets there** (§1.3). Every guardian
   mechanic is invisible to players until that is solved. The item that owns it,
   `TREE_GRAPHICS_OWNERSHIP_1`, is BLOCKED on your pick among 14 recovered art candidates.
4. **"The harvest is their nest" has no mechanism** (§2.6). There is no nest object, and taking the
   wool changes nothing for the wardens beyond the meter.
5. **The two design docs disagree, and the older spec still carries text the newer one replaced:**
   - asleep (activation doc) vs awake and wandering on a 12-cell leash (spec §2 C, §3);
   - refill after deaths 8 to 14 days (spec) vs 30 to 60 (activation doc);
   - settings in the shared creature-behaviour mod as 4 switches (spec §6) vs in the Leaning Scrub
     mod as 5 switches (activation doc §5);
   - "invisible in the crown" (spec §1) vs visible sleepers (activation doc §4);
   - the spec's Home-area mitigation and "eternal harvest job" notes (§9.1, §9.3) assume the
     proximity-charge version you ruled out today;
   - the activation doc's own "where the spec is now wrong" list (§1.3) is itself partly stale:
     the spec already uses the long tick and the existing rage state;
   - both docs gate on the package id `mandrake.rm.creaturebehaviors`; the giant's own wiring now
     uses `mandrake.rm.biomes` (the behaviour kit was folded into the unified biomes mod). The build
     must use whichever id is current.
6. **"Bark-lickers" are invented.** The spec's diet line names a creature that exists nowhere.
7. **"In the crown" has no mechanism.** A pawn stands on a ground cell. Whether a sleeping warden is
   drawn at the trunk's foot, on the trunk, or hidden under the canopy art is undesigned, and that
   is really what your open visibility question is about.
8. **The body is unpicked.** The plan is "reskin some long-armed, low, clawed quadruped", but no
   donor is named and no art exists.
9. **The stats are calibration guesses** against Anooba and the giant, never tested.
10. **The wool's icon may be the missing-texture placeholder** (§2.4), UNMEASURED live.
11. **Hunting a sleeping warden** is UNMEASURED (activation doc).
12. **Breeding** for sleepers with frozen needs is unaddressed.

### 6.2 Questions that genuinely need you

1. **Should the wardens be visible on the tree before you harm it?** (The one you deferred.)
   - (a) Yes, curled asleep at the foot of the trunk or against it, with "Roosting in the crown of
     Gomaun" when selected. You can see the danger and can hunt or tame them first.
   - (b) Hidden. The tree only says "something lives in the crown", and they appear when they drop.
     More surprising, but it bends your "readable sign" rule.
2. **Where does the wool come from, really?** (a) the tree grows it and the giants are only the
   story, as today; (b) the tree refills only if giants graze near it; (c) giants actually walk to
   trees and rub, and each visit adds wool.
3. **Which is the prize: the free shed or the harvest?** As built, the free shed wins by a mile
   and the harvest shuts it off. Options: (a) cut the shed to a small capped windfall so the
   harvest is the prize; (b) keep the shed generous but let a harvested tree keep shedding;
   (c) drop the free shed entirely, so all wool is guarded.
4. **Should taking the wool upset the wardens beyond the fight** (the "you robbed the nest"
   idea)? For example, a stripped tree stays touchy until its wool grows back. Or is "harvesting
   fills the meter" enough?
5. **How do sweetline trees reach a map?** Hand-placed in the frozen world, a map step that plants
   one on sweetline tiles, or a rare wild spawn? Nothing players see happens until this is decided.

Not for you, builder's business: the refill timing, the leash behaviour, the settings home and
the package id, once questions 1 and 3 are answered.
