# The Rust Cathedral's giant: five plot hooks for the mining droid (pitch, 2026-10-02)

**The ruling (owner, typed, same sitting as `rustcathedral_bedazzle_review_2026-10-02.md`):**
*"A massive mining droid, more like a digging tank with drill and scoop, having escaped the abandoned
mines to this place. Not very intelligent but ridiculously armored and strong. Fortunately it is also
peaceful. Needs a plot hook (feel free to share some ideas)"*

**What it is pitched against:** the Rust Cathedral's manners (the hum answers how you behave; mine the
plain plate freely, touch nothing sacred, stop when the hum drops), the slow guardian patrols, the
dancing bolts, the coolant eels and the line-cycle. The same sitting also ruled stowaway bolts that ride
the ship as the Cathedral's spies, a droid-repair rite (repair a free droid, then capture it mid-repair
or release it, with god reactions), and the Mending Weld (restore old structure into a room, Rekko's
rite). We are Jawas: a giant ownerless droid is the biggest salvage prize on Ash'karr.

**Lore tie found:** the abandoned mines exist only as a placement note in
`design/Jawa/worldbuilding/worldgen_interactive_def.md` (Scarlands: *"the abandoned mine areas"*,
where heavy industry was active) and as the ancient-mine expedition missions in
`design/Jawa/mods/required_mods.md`. Nothing says why the mines were abandoned, so every hook below is
free to answer it.

Working name used below: **the Delver** (placeholder, not a defName).

Peaceful by default in all five. Nothing below makes it hunt.

---

## 1. The Delver's Furrow (a recurring map event: the threat that isn't)

Every few days the Delver grinds across the map on a slow, visible lane, drilling a furrow through
plain plate and dumping tailings (steel, a little smartsteel ore) behind it. It has learned the
Cathedral's manners better than anyone: when the hum drops it stops dead, drill idling, like every
other living thing during the line-cycle. The trouble is that it is too dim to read the walls. Now and
then its lane points at a sacred conduit wall, and if it bores through, the hum goes to Alarm and the
guardians come for whoever is nearest, which is never the Delver. The player diverts it (block the lane
with plain plate, lure it with a scrap pile, or let it through and pay for it), so the giant becomes a
clock and a puzzle you live beside, not a fight.

**Cost: M.** Big-body mechanoid-race pawn with no hostile think tree; a lane walker reusing the
patrol-route laying already in the kit; a "dig cell and spawn tailings" job; a hook into
`RM_MapComponent_BiomeAttitude` so freezing on low hum and sacrilege-by-proxy both use what is built.

## 2. The Worn Bit (a relationship arc through the repair rite)

The Delver's drill head is worn to a stub; it scrapes plate uselessly and makes a grinding moan that
the hum echoes as a sour tone. A Jawa who walks up during a calm hum can start the droid-repair rite on
it: a long job needing a replacement bit (smartsteel, or a bit salvaged from the abandoned mines) and
several visits, because it wanders off between them. At the end comes the choice the sitting already
ruled. Bolt it (Rekko approves of salvage kept, Ta'Baa takes offence, the hum cools for a season),
release it (Ta'Baa is pleased, the Delver now waits by your camp each visit and digs where you mark),
or leave the work half done. Every Jawa instinct says bolt it, and the player has to decide whether a
tank that cannot be traded is worth more as a friend.

**Cost: M.** Reuses the ruled droid-repair rite (owed anyway) on one special target; a multi-visit
progress record on the pawn; a "follower that digs a designated area" job for the released branch.
Capture needs a tameable-mechanoid path; check the rite's capture build first.

## 3. The Bounty Notice (a quest: someone wants it back)

A trader or a Scarlands mining concern sends a notice: their digger walked off the job years ago and
they will pay well for its return, or for its memory core. Going after it means walking it out of the
Cathedral. It is too heavy to carry and too armoured to stop, so you lead it with lures across the
plateau without tripping a wall or the guardians. Midway the player can read the core and find out why
it fled: the miners left it running alone in the dark, or something in the deep shafts woke up. Then
the choice is to hand it over (silver, and a faction contact), sell them a fake core and keep the
droid (Jawa deceit, a risk later), or refuse. The Cathedral reacts to a machine being led away the way
it reacts to sacrilege: the hum sours, and stowaway bolts may follow you home to report.

**Cost: L.** A QuestScriptDef with an escort-by-lure objective (new: a "follow the bait" duty on a
non-colonist pawn), a reward branch, a memory-core item with readable lore, and a link to the
abandoned-mine missions. Best built after the concealment arc's quest scaffolding exists.

## 4. Scoop-Loads (an economy hook: the ore it brings)

The Delver still does its old job without a mine to do it in. It carries ore in its scoop from far
places (dead smartsteel, rare ore from the abandoned mines it walks back to) and dumps it in a heap
wherever it decides to rest. A heap is free to take, but taking it while the Delver watches drops the
hum a band, because the plateau treats the heap as its own offering. Trade it a gift instead
(lubricant, a power cell, scrap left on its path) and it dumps the next load at your marked spot.
Jawas turn this into a standing contract with a machine too dim to know it is in one, and Rekko
reads the gift exchange as salvage given back.

**Cost: S to M.** An ore-heap spawn on a timer at the Delver's rest cell, a "gift left in path"
trigger (pick up item, set a destination), and one hum-band hook for taking unpaid. No quest code.

## 5. The Rider (a mystery: who is steering the tank)

The Delver is too stupid to have found the Cathedral on its own, and colonists who study it notice it
always turns toward the hum's highest tone. The answer is a nest of living bolts in its cab, guiding
it the way they guide their own dances. The Cathedral called it home and the bolts are its drivers.
This connects it to the stowaway-spy ruling: if the player bolts or salvages the Delver, the bolts move
out onto the ship. If they leave it free, the bolts sometimes give it a gift for the camp instead, and a
reader of the hum can learn to ask it for a direction. The choice puts a bigger question to the player:
does the Cathedral own the giant, does the giant own itself, or do the Jawas?

**Cost: M.** A "cab occupants" container on the Delver (bolts spawn when it is disabled or opened),
direction-picking that follows the strongest hum source, and a tie to the stowaway bolt mechanic
(ruled, unbuilt). Works best after hum literacy is built.

---

## Recommended: 2, The Worn Bit

It is the only hook built from the sitting's own ruled rite and gods, and it gives the player the
strongest Jawa choice (salvage the prize or befriend it). It also makes hooks 1 and 4 better later on:
a released Delver is the one whose furrows you can steer and whose loads come to you.
