# The Rot: open questions for the owner, 2026-10-22

Written by FOUNDRY after an offline status audit of the Rot (the free mod `mandrake.rm.therot`, folder
`D:\Luke\dev\RimMandrake\src\RimMandrake\TheRot`). Each question is a card: pick a number, or answer in your own
words. Nothing here is blocked on you tonight; every question is one where the evidence conflicts, one of your
rulings collides with what is built, or one choice closes off another.

**What the audit found, in one paragraph.** The Rot is mostly built: its biome definition (with an animal density
set, 1.9), eighteen wild creatures (twenty in the campaign), nearly forty wild fungi, the Sheen weathers, the warm living mat, the hwelgrue giant
with its swallowed ship core, the gut-mother vat, the Unjoining Draught, and a settings screen whose every control
is wired (a static check proves each one has a reader). Its test script exists and passes offline. One real defect
was found and fixed tonight (commit `69905fd71`): when the borrowed Alpha Animals creatures were retired on
2026-10-18, the wiring that lets three Rot creatures share wounds was deleted with them and never moved to our own
copies. The chittik, durrok and mullgoth had silently stopped doing what their descriptions promise; they do again.
Still owed: one live run of the test script (the game is in BENCH's hands tonight), the Unjoining rite (tabled by
you), and the campaign tiles for the swallowed ship core. A biome of ours sitting on zero tiles of today's planet is
expected (you paint once, at the end) and is not counted as a gap anywhere below.

Local time when written:
Thu Oct 22, 12:14 AM PDT

---

## Q1. The durrok and the mullgoth: whose creatures are they?

**What we learned.** Two shaggy, fungus-matted mound creatures, the **durrok** and the **mullgoth**, are on the
Rot's wild-animal list. You ruled on 2026-10-02 that they **mend among their kin** (when one is hurt, the others
nearby heal it faster): part of "the Rot shares everything". Tonight's fix restored that. But:

- **They live in three places.** Both also roam the **Leaning Scrub** (a dry scrubland biome), and the mullgoth the
  **Cauldron** too. Your rule is *"an animal belongs to ONE biome unless there is an in-game reason"*, and you have
  also said *"stop evictions"*: a multi-homed creature is settled at each biome's own review sitting, never by an
  agent editing a list.
- **Their text says scrubland, not Rot.** The durrok's description calls it *"smaller and less dangerous than its
  wetland kin for lack of water and rot to grow on"*: it was written as the scrub's version of a Rot creature.
- **Their files live in the Star Wars creature mod**, even though their names are our own invented ones. So a
  player running the free Rot without the Star Wars mod gets a Rot with no durrok or mullgoth at all, and with
  them goes the only kin-mending in the biome.

**Terms.** *Kin-mending*: the healing-among-kin behaviour above. *Free Rot*: the standalone mod anyone can install,
with no Star Wars content.

1. **They are Rot creatures. Move them into the Rot mod, rewrite the durrok's text as a Rot hybrid, and leave the
   Leaning Scrub and the Cauldron a hole to fill with a new creature at their own sittings.** Buys: one home each,
   kin-mending ships in the free Rot, the text matches the place. Costs: two other biomes lose a grazer until a new
   one is designed and drawn; a file move between mods (small).
2. **They are scrubland creatures. Take kin-mending off them and give the Rot a new kin-mender of its own.** Buys:
   the descriptions are already right; the scrub keeps its cast. Costs: the Rot loses its only menders today, and a
   new creature means a design, a name and art (the largest option).
3. **Split each into two species: a Rot form (a fungus-grown hybrid that mends) and a scrub form (plain, no
   mending).** Buys: every biome keeps a full cast and the one-biome rule holds. Costs: two new creatures' worth of
   definitions and art; two near-identical animals a player may confuse.
4. **Leave them as they are until each biome's own sitting.** Buys: no work tonight; respects "stop evictions".
   Costs: the free Rot keeps shipping without its menders, and the scrub keeps a Rot creature's healing it never
   asked for.

**Recommended: 1** — the Rot is where their behaviour was ruled and where they are most often met; the two holes
it opens are ordinary roster work.

**ANSWERED 2026-10-22 by question card, write-in:** *"Like needs to move. Wait until biome reviews. But you are right they should not be like this."* = leave them until each biome's review sitting (no eviction now); he agrees the multi-homing is wrong and they will move at the sittings.

---

## Q2. The warm mat versus "no biome-specific heat"

**What we learned.** On 2026-09-17 you ruled by card that the Rot's living mat is **free heating forever**: a room
built on the mat is warmed toward a cap of 21 °C with no fuel (*"It doesn't make enough to trivialize the deep deep
dark. It just helps a lot."*). On 2026-10-19, ruling the Direct Sun feature, you wrote *"no biome-specific heat, no
biome-specific sun ... Ambient heat is normal Rimworld rules."* The mat **is** a heat source found in one biome
only. The two rulings may not collide (the October words were about sun and heatstroke), but read literally, they do,
and the Rot also has a second biome-only warmth: fresh Rot produce gives off heat in storage.

**Terms.** *Direct Sun*: the planned feature where unshaded sunlight raises felt temperature, by sun angle only.
*Ambient heat*: the ordinary room and outdoor temperature the game already simulates.

1. **The mat stays exactly as built: your October ruling is about the sun and heat danger, not about warm ground.**
   Buys: nothing changes; the Rot keeps its signature comfort in a −19 °C median cold. Costs: a reader of the
   rulings will keep tripping on the same apparent conflict unless the ruling's text is narrowed (we would add one
   line saying so).
2. **Keep the mat, but make it ordinary physics: the mat is a terrain that gives off heat like a heater would,
   usable anywhere the mat is grown or carried.** Buys: no biome exception; the mat becomes a building material
   other biomes could use. Costs: rework of a finished mechanic; the warmth stops being the Rot's own.
3. **Remove the mat's warmth (and the produce warmth); the Rot's cold is met with ordinary heaters.** Buys: the
   October ruling holds with no reading needed. Costs: deletes a mechanic you ruled and called a draw; the Rot loses
   one of its six unique mechanics.

**Recommended: 1** — the September ruling is specific and deliberate, and the October one names the sun; a one-line
clarification is cheaper than either rebuild.

**ANSWERED 2026-10-22 by question card, write-in:** *"Make it work anywhere but it not naturally occurs in the rot. Can be installed on the gravship to help with heating in cold places as a reward. Needs food. Would grow in other biomes if tended with food. Rot doesn't require feeding due to sharing lore."* = a new design (filed as a build item).

---

## Q3. The swallowed ship core's campaign tiles: pick them now or after the new world?

**What we learned.** In the campaign, exactly one hwelgrue (the Rot's giant) carries a piece of an old ship drive,
and its log reveals up to four salvage sites. You ruled on 2026-10-09 that agents pick the carrier's tile and the
site tiles from existing Rot tiles and you veto later. Picking them now has a catch we found tonight: the world
remake plan lists this exact job as **"easier after the remake"**, because a remade planet renumbers its tiles. The
code restricts the core to a hwelgrue **on the named tile**: if that tile stops being Rot, or stops existing, no
hwelgrue anywhere ever carries the core, silently, and the whole swallowed-navigator story never starts.

**Terms.** *Tile*: one hexagon of the world map, known by a number. *Remake*: the planned rebuild of the campaign
planet (design folder `world_remake_2026-10-19`).

1. **Pick the tiles now from today's record of the planet, and redo them after the remake.** Buys: the campaign
   story works on today's save. Costs: done twice; if the redo is forgotten, the core silently never appears.
2. **Wait for the remake (and the one-time paint), then pick.** Buys: done once, on the real planet. Costs: on
   today's save the campaign behaves like the free mod (the first wild hwelgrue to settle claims the core) until then.
3. **Name the place by a rule, not a number: "the Rot tile nearest the stormwall's night edge", resolved when the
   game starts.** Buys: survives any remake and repaint with no redo. Costs: a small new piece of code; the
   location is less hand-placed than you may want.
4. **Drop the authored tile: the campaign uses the free rule (any wild hwelgrue may claim the core) and only the
   salvage sites get authored places.** Buys: no tile can ever break the claim. Costs: the carrier is not in a
   chosen spot, so the story can start anywhere the clan meets a hwelgrue.

**Recommended: 2** — your paint-once ruling already says the planet is settled last, and option 1's silent failure
is exactly the kind this project keeps paying for.

**ANSWERED 2026-10-22 by question card: option 2, wait for the remake and the paint, then pick the tiles.**

---

## Q4. The Unjoining rite is tabled: what happens to it now?

**What we learned.** You chose the Rot's rite on 2026-10-02: **the Unjoining**, for the god Ta'Baa (the Unrooted): a
colonist who has taken a Rot symbiont is held through a brutal purge until the symbiont dies, just before the clan
flies away. On 2026-10-03 you tabled every rite *"until the biome mod is fully complete and checked out"*. The rite
also needs machinery that does not exist yet (rites found in the world as inscriptions, studied, then added to the
religion). Meanwhile, its half that was not tabled is built: the **Unjoining Draught** (the purge itself, as a drug
learned by research). Your ruling said the draught is learned *from* the rite; today it is learned by ordinary
research, because there is no rite.

**Terms.** *Symbiont*: a living Rot organism a colonist takes in for a benefit (no sleep, fast healing, Sheen
immunity). *Found rite*: a rite the clan discovers in a biome rather than starting with.

1. **Keep it tabled; the Rot is "complete" without it.** Buys: no work; your ruling stands as written. Costs: the
   Rot's god mark stays partial; the draught's "learned from the rite" story stays untold.
2. **Untable it for the Rot alone: build the found-rite machinery with the Unjoining as its first user.** Buys: the
   machinery every biome's rite needs gets built once, against a real case. Costs: the largest option; it reopens
   rites before the biomes are checked out, which is what you tabled them to avoid.
3. **Build the Unjoining as an ordinary ritual (available from the start, no discovery), and add discovery later.**
   Buys: the rite is playable soon and small. Costs: loses "biomes teach rites", the reason you liked rites in the
   first place, until discovery lands.
4. **Drop the rite; keep the draught as plain research.** Buys: one less thing owed. Costs: Ta'Baa loses one of
   four rites; the purge-before-flight drama is gone.

**Recommended: 1** — the draught already gives players the purge, and your tabling reason (finish and check the
biomes first) still holds tonight.

**ANSWERED 2026-10-22 by question card: option 1, keep the Unjoining tabled.**

---

## Q5. The dustveil: a moth that does not fly, from a laboratory

**What we learned.** One of the Rot's small creatures, the **dustveil** (a broad-winged moth whose shorn silk is one
of the Rot's unique resources), is a renamed copy of a borrowed creature. It breaks three of your rulings at once:
it **does not fly** (*"If it flies in the fiction, it flies in the game"*), it is a **plain animal**, not a fungus
hybrid (the Rot's review ruled every resident a hybrid), and its text says it was *"bred long ago for some
forgotten waste-eating project"* (the review struck the same laboratory origin from the brullith). Your flight rule
fires when the creature's definition is touched; nobody has touched it since.

**Terms.** *Real flight*: the game's own flying stat plus a flapping animation; a flier crosses walls and water.

1. **Make it fly, rewrite it as a fungus-grown moth, and drop the laboratory.** Buys: all three rulings honoured;
   the Rot gets a true flying lure-moth. Costs: a flight animation needs new art frames, and flight can only be
   checked with you present.
2. **Make it fly and leave the text.** Buys: the flight rule holds with the least change. Costs: the hybrid and
   laboratory problems stay.
3. **Rewrite the text only (hybrid, no laboratory); it stays a walking moth.** Buys: cheap, no art. Costs: breaks
   the flight rule knowingly.
4. **Replace it with a new Rot creature that makes the silk.** Buys: a creature designed for the place. Costs: a
   new design and art; the silk's source changes.

**Recommended: 1** — every half-measure leaves a known ruling broken, and the flip-book art is the only real cost.

**ANSWERED 2026-10-22 by question card: option 1, make the dustveil fly, fungus-grown, no laboratory origin.** Build filed.

---

## Q6. The free Rot's most common fungi wear plain-game art

**What we learned.** The Rot's three most common wild fungi (bryolux, weighted 10; glowstool, 3; the cap that
replaced the agarilux, 2) draw the **base game's own cave-plant pictures** in the free mod. Our painted
replacements exist, but they sit in the campaign layer, where they repaint the base game's cave plants everywhere.
So the free Rot, whose experience you chose as *"a cathedral of mushrooms in the dark"*, looks mostly like a
vanilla cave floor, while the campaign shows our art. Moving art is a cosmetic change, so it waits for your word.

**Terms.** *Campaign layer*: the Utinni patches that only load in your Star Wars campaign. *Free mod*: the Rot as
anyone installs it.

1. **Give the free Rot's fungi their own art paths and install our painted versions there.** Buys: the free Rot
   looks like ours; the campaign is unchanged. Costs: two copies of each picture to keep in step (or one moved and
   the campaign pointed at it).
2. **Move the paintings into the free Rot so they repaint the base game's cave plants for anyone who installs it.**
   Buys: one copy. Costs: installing the Rot would change the look of every cave in a player's game, outside our
   biome.
3. **Leave it: the free Rot keeps the plain art.** Buys: no work. Costs: the free mod's commonest sight is not ours.

**Recommended: 1** — it is the only option that changes nothing outside the Rot.

---

## Q7. The Rot's first north-star bars: which experiences get a pass/fail bar?

**What we learned.** You chose the Rot's experience by card on 2026-10-20: *"A cathedral of mushrooms in the dark,
generous and hungry. The Rot shares everything, including you."* The Rot has no north-star bars yet, so no test of
the mod checks that experience. Bars cost a live check each, so the first three or four decide what the Rot is
judged on. Several can be picked.

**Terms.** *North-star bar*: a one-line, hash-bound pass/fail statement only you validate; a test then checks it on
every run.

1. **"Hurt one, the grove comes": striking one network creature brings its kin.** Buys: bars the core "shares
   everything" promise, the thing that silently broke this month. Costs: needs live creatures and a fight.
2. **"The gut takes the fallen": a downed colonist on open ground is swallowed and can be cut out.** Buys: bars the
   hungry, "including you" half. Costs: needs a hwelgrue on the map; the longest live check.
3. **"The mat keeps you": a room built on the mat warms without fuel, never past 21 °C.** Buys: bars "generous";
   cheap to check. Costs: depends on Q2's answer.
4. **"The Sheen marks you": standing in Sheen-fall walks a colonist up the exposure ladder.** Buys: bars the
   weather, the Rot's most visible feature. Costs: weather must be forced, which is reliable.
5. **Bars 1, 2 and 4 together** — *the three cover generous, hungry and the place itself; the mat (3) waits on Q2*.

**Recommended: 5** — it covers every clause of your sentence and does not build on the unsettled heat question.
