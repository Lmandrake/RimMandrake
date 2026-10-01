# Biome rites pass: what each finished biome teaches the Salvation (2026-10-01)

_Status: BENCH design, PITCHED, owner to rule. Nothing here is built. Applies the program principle
of `design/Jawa/salvation_rites_2026-10-01.md` §(e) to the ten finished bedazzle biomes other than
the Abyss. Machinery (inscription → rubbing techprint → "found rites" row → `Ideo.AddPrecept`) is
§(d) there and is not restated. Gods and appetites: `design/Jawa/divine_satiation_engine.md` §2.0b._


## 0. How to read this pass

**Scope.** 23 new found rites across the ten biomes, 2 or 3 each. With the Abyss's four that is
27. Every rite below is campaign tier: its `PreceptDef`, `RitualPatternDef`, outcome effect and
inscription ship in `mandrake.rut.rites` and nowhere else. The biome mods hold only the free-tier
physics a rite reads (a weather, a terrain, a building); none of them names a god.

**Fields per rite.** *Needs* is the condition the ritual gate checks, the same role absolute
darkness plays for the Abyss four (one `RUT_RitualConditionDef` per condition, §(f) there).
*Found* is where the inscription stands and the condition it must be studied under: studying it
outside its condition fails, the same rule as a lamp brought to an Abyss inscription. *God* names
who the rite is FOR and the kind, from the register's six kinds (feeding, settlement, starving,
venting, consolation, warding). Within one biome no two rites share a kind. *Outcomes* are the
four vanilla quality tiers; each one ends with the Ninefold call it makes (`ApplyDelta`), never a
number on screen. *Inscription* is a draft line for the rubbing letter, which is the owner's pen
to rule.

**Laws checked on every rite.** Other faiths' rites stay theirs: the Sun-Debt's Return, the deep
tribes' fire rite and the Forge's witnessed fire are named only to keep clear of them. There is one
kind of heat: no rite adds a heat hediff, and any heat reads through vanilla temperature. Nothing
vanishes without a readable sign: every rite that consumes, buries or gives away a thing leaves a
mark, a mound, a cairn or a letter. There are no fantasy tropes: no rite grants a power, no god
appears, and an outcome is a mood, a memory, a ledger entry, a meter step, or an ordinary thing.
The Lightless Burial is Ozzik's for now, and `SALVATION_RITES_RENORMALIZE_PASS_1` comes later, so
the balance here is sensible, not final.

**UNMEASURED and owed before any build:** that a `RitualOutcomeComp` can read a live
`GameCondition` or `WeatherDef` as cheaply as it reads `GroundGlowAt`. Most conditions below are
weathers or conditions the biome already ships, or has ruled and not built.

## 1. The Contagion

**What it already has.** The weather is inverted. The Bloom is the standing storm, fogged and
budding. The Burn is a tear in the cloud where raw UV sterilises the valley and everything native
hides. Red water is lethal until the sun has had it; the Unfinished are forms the goo abandons
mid-build and reabsorbs within days; the rim is littered with failed escapes. Its gods mark had no
Salvation content. Source: `design/Jawa/worldbuilding/biomes/the_contagion.md` §3 to §8,
`contagion_grotesque_cast_2026-09-27.md`.

### 1.1 The Sunning (Oomo, feeding)

- **Needs:** a Burn in progress, and red water set out in open vessels on unroofed ground. The
  participants wait in a burn shelter within sight of the vessels. Nobody stands in the light.
- **Found:** carved on the back wall of a burn shelter at a valley mouth, above a row of old
  cistern rings worn into the rock. It is legible only in a Burn, when the red fog lifts.
- **God:** Oomo, feeding. Waters held become life held, and here the only unlimited water on the
  dayside is made drinkable by patience. The poured cup is greeted, the first sip held, in his
  folk gesture.
- **Outcomes:** Poor, the cloud closed too soon and the water is still red (the vessels say so on
  hover; drinking it is the player's choice). Fair, the water is sunned and potable. Good, plus
  "the waters were greeted" for every participant. Excellent, plus one vessel keeps clean through
  the next Bloom. Ninefold: Oomo up, sized by litres sunned.
- **Inscription:** *"The sky that kills the red makes it a cup. Wait in the shade. Let it burn."*

### 1.2 The Unfinished Laid Down (Rekko, consolation)

- **Needs:** the corpse of an Unfinished before it dissolves (hours), carried to the burn line,
  the strip of sterilised matter between the red and the green.
- **Found:** scratched into a half-transformed tree at the infection front, a tree that is both an
  oak and something else. It is legible only from the burn line side.
- **God:** Rekko, consolation. Scrapping the repairable is a tragedy he asks you to feel. The
  Unfinished are the far end of that grief: things begun and abandoned that nobody will ever
  finish. The rite names the three designs each one was trying to be, and lays it down as soil.
- **Outcomes:** Poor, the corpse dissolved before it was laid (it is still a goo stain on the
  ground). Fair, a mulch mound at the burn line, marked, and the mourners' grief memories ease.
  Good, the mound is sunned Contagion mulch the colony may take. Excellent, plus an art tale, "the
  three things it meant to be". Never a gene, a part or a stat: Contagion-touched never upgrades
  you (sheet ban 6). Ninefold: a consolation entry for Rekko.
- **Inscription:** *"It was three things and none of them. Say all three. Then let it feed the
  green."*

### 1.3 The Kept Mistake (Zizzik, warding)

- **Needs:** a party about to go out into the Bloom, and one broken thing (an item below a hit
  point threshold) left unrepaired at the valley mouth before they go.
- **Found:** on a boulder at the rim among the burst husks of a hundred failed aerofleet escapes.
  It is legible only in the Bloom, by touch, because the fog hides it.
- **God:** Zizzik, warding. His folk gesture already keeps one broken thing in every room so the
  wrong spark has somewhere harmless to land. The Contagion is the weapon that ruins itself by
  excess, his kind of place. The rite gives him a target outside the party.
- **Outcomes:** Poor, the decoy is ignored. Fair, the party's first mishap in the Bloom (a jam, a
  tear, a fall) lands on the decoy instead, which visibly breaks further. Good, the first two.
  Excellent, plus the party's return letter says what the decoy took. Ninefold: a warding entry,
  Zizzik's slumber clock does not tick for that expedition's first mishap.
- **Inscription:** *"Leave him something broken at the door. He will play with it, and not with
  you."*

## 2. The Wasteland

**What it already has.** Nothing recycles: water, fallout and history all end here, and nothing
rots. Ash storms re-deal the map and exhume what was buried (a trench line, a hull, a cache, a
crime). War salvage is priced in dose, and every failed expedition adds its own wreck to the
hoard. The Junkers charge the tipping fee for dropping waste, an income they call a rite. That fee
is the Junkers' business, not a faith and not the Salvation's, and nothing below imitates it.
Source: `design/Jawa/worldbuilding/biomes/wasteland.md` §4b to §8,
`wasteland_survivor_cast_2026-09-28.md`.

### 2.1 The Storm's Receipt (Mob'Unloo, feeding)

- **Needs:** a storm-exhumation site, uncovered by an ash storm within the last few days and not
  yet stripped. The organiser walks it and tallies aloud every find before anything is lifted.
- **Found:** stamped on a buried cargo plate that the storm turned face-up, a list of goods with
  the last line left blank. It can be studied only on an exhumation site, so the plate itself only
  surfaces after a storm.
- **God:** Mob'Unloo, feeding. Successful theft is his highest art, something for nothing. Ground
  that nobody can live on is ground nobody has stripped, and what the storm lays bare belongs to
  whoever counts it first. The tally is his: a thing counted is a thing owned.
- **Outcomes:** Poor, the count is wrong and a find is missed (it stays on the map, marked by the
  tally as "uncounted"). Fair, the finds are logged as the clan's, a ledger entry. Good, plus a
  better haggle at the next trade. Excellent, plus the storm's next exhumation on this map is
  named in advance by the bearing on the plate. Ninefold: Mob'Unloo up, sized by the tally's value.
- **Inscription:** *"The wind has opened the hold. Count it before you lift it. What is counted is
  ours."*

### 2.2 The Salted Keeping (Ozzik, venting)

- **Needs:** a vitrified crater, and the colony's finest made thing (a masterwork or legendary
  item, or a high-tech component) carried there and buried in the salt.
- **Found:** fused into the glass of a crater rim, where an old army wrote something in the moment
  before its own weapon arrived. It is legible only at low light, when the stormwall glow catches
  the glass.
- **God:** Ozzik, venting. His pride-meter draws Sh'kaar and Zizzik. The Unburdening vents it by
  destroying wealth, and the Lightless Burial vents it by laying grief down. This vents it by
  humility: the proudest thing the clan owns is shown to the place where pride ended, and then put
  out of reach. It is not destroyed. The Wasteland preserves everything, so the item lies exactly
  as it fell, and can be dug up again later, at the price of the ground's dose.
- **Outcomes:** Poor, the item is buried and nothing is eased. Fair, Ozzik's pride-meter vents one
  step. Good, two steps, and the upward bias on Sh'kaar's and Zizzik's rolls lowers. Excellent,
  plus an art tale. Readable sign: a salt cairn marks the spot and the item's name is on its hover.
  Ninefold: a venting entry for Ozzik.
- **Inscription:** *"We were greater than this. Bury the best of you where the great ones ended.
  The salt will keep it."*

### 2.3 The Inherited Wreck (Rekko, settlement)

- **Needs:** the wreck of an earlier failed expedition (a dead vehicle or crashed ship already on
  the map, or exhumed by a storm), and one piece of it carried out of the hot ground.
- **Found:** written inside the wreck on its crew's own log panel, the last entry unfinished. It
  can be studied only by a pawn inside the dose zone, so the reading costs dose.
- **God:** Rekko, settlement. He owns history and ancestral debt: taking a piece of salvage takes
  on its story and the reason it was made. These crews died wanting one thing out. The rite takes
  their debt on by doing it for them. This settles a debt of history, not of trade, so it does not
  overlap Mob'Unloo's ledger.
- **Outcomes:** Poor, the piece is carried out and the story stays unread. Fair, the piece carries
  the dead crew's name in its description (the salvage-within-salvage of `wasteland.md` §7). Good,
  plus the crew's log names one more cache on the map. Excellent, plus a memory for the carriers,
  "we finished their walk". Ninefold: a settlement entry for Rekko.
- **Inscription:** *"We came for the core. We did not get out. Whoever reads this: take it the rest
  of the way."*

## 3. The Blue Desert

**What it already has.** It lies on the deep nightside, cold and clear and nearly empty. The
ablation line gives back what fell from orbit: a meteorite, a hull, a freeze-dried body, a cocoon
from the war. The plants run on hydrocarbon plumbing and go off as an explosive chain when they
burn, and ion detonates a living vhaulk. Silence and then a boom. Source:
`design/Jawa/worldbuilding/biomes/the_blue_desert.md`, `bluedesert_bedazzle_review_2026-09-28.md`.

Rites are allowed in every biome (owner ruling, 2026-10-01), the Blue Desert included. Its rites live
in `mandrake.rut.rites`, not the biome mod.

### 3.1 The Returned (Ta'Baa, consolation)

_Status: ruled-kept (card, 2026-10-01)._

- **Needs:** a freeze-dried body that the ablation line has given up, carried back to the ship and
  sealed in a sarcophagus aboard (not buried), so that it leaves with the clan on the next launch.
- **Found:** a line scratched on the inside of a returned hull's hatch, in the clan's own trade
  script, by someone who fell. It can be studied only at the ablation line, where the ice is
  thinnest.
- **God:** Ta'Baa, consolation. He is hope, and despair is his one blasphemy. A dead traveller is
  grief, and the rite lays that grief down the Ta'Baa way: the sky gave back someone who went
  farther than anyone alive, and the clan takes him farther still. The dead are the Far Walker's
  own kind.
- **Outcomes:** Poor, the body is aboard and nothing more. Fair, the crew's next launch carries "a
  passenger who went farther". Good, plus the despair moods of the crew shorten for a season.
  Excellent, plus an art tale, and the sarcophagus shows on the ship's inspect as "the Returned".
  Readable sign: the body is never lost; it rides in the hold until the player chooses to bury it.
  Ninefold: a consolation entry for Ta'Baa.
- **Inscription:** *"I went higher than any of us. The ice brought me back. Take me with you when
  you go."*

### 3.2 The Charged Reed (Ishko, feeding)

_Status: ruled, reworked from its pitch (card, 2026-10-01)._

- **Needs:** the party walks to the live, charged heart of a ripe whistle-reed or floss field and
  cuts one charged reed without setting it off. No fire, ion weapon or powered light may be carried
  by anyone present. If anyone sparks, the field may go, which keeps the biome's silence-then-boom.
- **Found:** a Rakatan Warning panel at a quarry mouth whose last line is in a second, later hand.
  It can be studied only in the Haze, when the field's charge sits low.
- **God:** Ishko, feeding by a danger passed undetected. He is pleased when a live danger is
  reached, handled and left without ever noticing the clan. This differs from the Dark Vigil: the
  Vigil offers stillness in a sealed dark, while this offers a party working at the heart of a live
  charge. Darkness here is the ordinary nightside, so the rite never reads the Abyss's
  absolute-darkness gate.
- **The holy object:** the cut reed becomes a reed whistle, a readable warning item. It sounds when
  danger is near, and its quality and range scale with the outcome tier below.
- **Outcomes:** Poor, the reed is cut but spoiled: a short-range whistle, and the field stirs and
  whistles the party's line on the map (the readable sign). Fair, a clean cut and a whistle of
  ordinary range. Good, plus a longer range, and Ishko's satiation rises. Excellent, plus the
  whistle sounds earlier and the party's "we cut it and it never knew" is shared by all. Any spark
  fails the rite and the field may go. Ninefold: Ishko up.
- **Inscription:** *"The ones who dug cut one reed from the heart of the field and carried nothing
  that sparks. Keep it. It will sing before the ground does."*

## 4. The Cracked Lands (Flooded Canyon, `RM_FloodedCanyon`)

**What it already has.** The flood is the clock. Ancient chimes, tuned to the water before anyone
alive, ring ahead of the wall, and refuge ledges line the roads. The flood is the planet's one
lethal water. Each recede exposes buried wreckage for a few days, a salvage strike for anyone in
the mud, and the one commandment on the roads is that settled water is legal water. Source:
`design/Jawa/worldbuilding/biomes/floodedcanyon_bedazzle_review_2026-09-28.md` (slate G, H, I),
`the_cracked_lands.md`. Slate G proposed biome-local lore (the Blue Desert precedent); these rites
sit in `mandrake.rut.rites`, so the free biome mod stays god-free either way.

### 4.1 The Chime Vigil (Oomo, warding)

- **Needs:** the chime window (the flood clock's warning phase), held on a refuge ledge above the
  wall's path. Nobody goes down to the water until it has settled, and nobody drinks flood water.
- **Found:** chime-tenders' marks cut into the oldest refuge ledge, beside a chime bracket. They can
  be studied only while the chimes ring, because the marks are cut to read in the shadow a hanging
  chime throws.
- **God:** Oomo, warding. He governs sickness as surely as health, and his own standing water lets
  disease in. The flood is the most water this land sees and the most dangerous. The rite keeps
  his foul side away: the waters are honoured from above, untouched, until they are legal.
- **Outcomes:** Poor, someone went down early (the prints in the mud say who). Fair, the colony's
  first drink after the recede is settled water, and no flood-borne illness can be caught from
  this flood. Good, plus "we let the water pass" for the vigil. Excellent, plus the chime's next
  ring arrives earlier in the letter. Ninefold: a warding entry for Oomo.
- **Inscription:** *"When it sings, climb. Let the water go by. Drink only what has stopped
  moving."*

### 4.2 The Mud Claim (Rekko, feeding)

- **Needs:** flood-touched cells within the salvage-strike window after a recede, and a piece of
  exposed wreckage dug out and set upright on dry ground before it is broken down.
- **Found:** on a wrecked hull that floods have turned over for an age, its old plate polished bare
  by the water except where a hand-cut line survives. It can be studied only in the strike window,
  because the next flood buries it again.
- **God:** Rekko, feeding. The discarded are only sleeping, and his folk gesture rights a tool lying
  face-down. Here the flood itself is the second hand that brings old things back up, and the rite
  rights each one and asks what it was before deciding whether it is scrap.
- **Outcomes:** Poor, the piece is broken down unread. Fair, its description names what it was
  ("a crawler's drive coupling, from before the water"). Good, plus a repair bonus on any job that
  uses it. Excellent, plus a rival crawler crew working the same mud leaves the claimed pieces
  alone (a visitor-band courtesy, slate H). Ninefold: Rekko up, sized by pieces righted.
- **Inscription:** *"The water digs for us. Stand each thing up before you take it apart. Ask it
  what it was."*

## 5. The Cauldron

**What it already has.** A twilight terminator forest of chemical vents, with no heat source at
all. The ground is loud, like a slow steam engine, and silence is the alarm (vent bloom coming).
The discoverable tech is filtering one fluid into another. Vent gas is very flammable, burns with
toxic smoke, and should be capped. The vexxiss inhales vents and puts fires out. The gods mark is
ruled: **Oomo dislikes the Cauldron but does not refuse to go** (the refusal was softened to a
grimace). Source: `design/Jawa/worldbuilding/biomes/cauldron_bedazzle_review_2026-09-28.md`,
rulings 1 to 6.

### 5.1 The Filtered Cup (Oomo, consolation)

- **Needs:** the first water a filter-craft converter has drawn out of the Cauldron's poison,
  shared at the converter by the whole party, one held sip each.
- **Found:** etched on a spent filter cartridge housing in a corroded ruin, beside the hauled-in
  water tanks the review reads as offerings that failed. It can be studied only beside a running
  filter (the etching reads under its condensation).
- **God:** Oomo, consolation. He grimaces at this land, the wettest-looking country on the planet
  where no drop can be kept. The rite does not feed him; it eases his dislike by showing him water
  kept here by hand, which he would not keep himself. This is the ruled grimace given a liturgy.
- **Outcomes:** Poor, the sip is drunk, nothing more. Fair, "Oomo's grimace" mood debuffs for
  Salvation colonists on Cauldron maps shorten (if `CAULDRON_RULED_CONTENT_1` builds one; else a
  plain memory). Good, plus the converter's first week runs cleaner. Excellent, plus an art tale.
  Ninefold: a consolation entry for Oomo.
- **Inscription:** *"He will not keep water here. So we do it for him, through the cloth, slowly.
  Show him the cup."*

### 5.2 The Engine Hour (Ohm, feeding)

- **Needs:** the ground's standing engine sound (not a vent bloom's silence), and a party sat
  still on open ground for about an hour, hands on the earth, every machine they carried switched
  on and idling beside them.
- **Found:** cut into a capped ruin wellhead's housing, where an old crew marked the ground's
  rhythm as if it were a gauge. It can be studied only while the ground is loud; in a silence the
  marks mean nothing.
- **God:** Ohm, feeding. He is the living machine and wants it revered. The Cauldron is the one
  place where the land itself sounds like a running engine. The rite treats it as one. It keeps
  Ohm company, and the idling machines are his.
- **Outcomes:** Poor, the hour is broken by a falter. Fair, a shared memory, "we heard it run".
  Good, the party's machines show reduced breakdown chance for a few days. Excellent, plus the
  next vent bloom's silence is called a few hours early by a letter in the clan's voice. If the
  ground falls silent mid-rite, the rite ends at once and the letter says why: the bloom is coming.
  Ninefold: Ohm up.
- **Inscription:** *"The ground is an engine. Listen until you can count it. When it stops, run."*

### 5.3 The Capping (Zizzik, starving)

- **Needs:** an uncapped vent cell and a gas-tap cap built on it, closed by the rite in the open
  with no flame within a radius (ruling 4: vent gas burns, and should be stopped).
- **Found:** on the inside of an old capping collar beside a vent that blew it off, the collar
  scorched. It can be studied only on a still day between blooms, with no fire on the map.
- **God:** Zizzik, starving. Fires and explosions fatten him. A vent left open is a spark waiting
  for him, and a capped one is a disaster he will never get to throw. A well-run, sane colony
  starves him; this is that, done as a rite.
- **Outcomes:** Poor, the cap holds and that is all. Fair, the vent's local bloom chance falls.
  Good, plus a starving entry for Zizzik and the cap's yield of vent-gas stock begins (ruling 4's
  reagents). Excellent, plus the next bloom on this map is weaker. If a flame is lit inside the
  radius mid-rite, the rite fails and the vent may flash: the readable sign is the scorch on the
  collar. Ninefold: Zizzik down (starved).
- **Inscription:** *"He sleeps in the vent. Close it while he sleeps. Bring no fire to the door."*

## 6. The Forge

**What it already has.** A volcanic mountain where fire costs nothing: the ForgeStill and its
boiling-rain bursts (`RM_ForgePulse`, shipped), vent smelters and forges (F6, shipped), foundry
towers, the herds grazing the smoke. Its gods mark is ruled at the freeze as **two faiths, one
mountain**. The Jawa see **Sh'kaar's forge**, the war-sun's anvil, at his lava lakes and craters.
The Deep Desert Tribes see the unstolen fire, whose precept is *"Forge fire is only witnessed"*.
The witnessed fire is the Tribes' rite and stays theirs. Nothing below carries Forge fire away,
which also keeps hard ban 4. Source: `design/Jawa/worldbuilding/biomes/the_forge.md` §8,
`forge_bedazzle_review_2026-09-28.md` (mark 9, slate F).

### 6.1 The Anvil Gift (Sh'kaar, venting)

- **Needs:** a lava lake or lava crater (Sh'kaar's anvil), and a weapon the clan made or took,
  thrown into the melt by its last user before the party.
- **Found:** a line hammered into an obsidian slab on a crater lip, among the twisted remains of
  older weapons fused to the rock. It can be studied only during a ForgeStill, when the air is
  clear enough to read the glass.
- **God:** Sh'kaar, venting. Destruction feeds him, even the clan's own: *"an explosion burning
  your own stuff pleases him; he's fed, then lenient a while"*. His battle-escalation meter is the
  dangerous one. The Snuffing starves him and the Shade Tithe (§8.1) wards him off. This is the
  third way, a deliberate small feeding that buys a quiet spell, the controlled version of what a
  fight gives him for free.
- **Outcomes:** Poor, the weapon is gone and he is not satisfied. Fair, his escalation meter drops
  a step. Good, two steps, and the next brute attack on the colony comes later. Excellent, plus a
  memory, "the anvil took it". Readable sign: the weapon's name joins the slab's hover list of
  gifts. Ninefold: a venting entry for Sh'kaar. The cost is real: the weapon is lost for good.
- **Inscription:** *"This is where the sun hammers. Give him a blade and he will not come for
  yours. For a while."*

### 6.2 The Flawed Masterwork (Ozzik, feeding)

_Status: ruled-kept, pending a buildability check: can the gods' engine damp the knock-on to Sh'kaar and Zizzik for one call? Item `FLAWED_MASTERWORK_ENGINE_CHECK_1`._

- **Needs:** an item of masterwork or legendary quality finished at a vent forge or vent smelter,
  and its maker scratching one small, deliberate flaw into it in front of the clan.
- **Found:** a tower tender's tool rack in a foundry tower (F4), where every tool bears the same
  small scratch. It can be studied only inside the tower.
- **God:** Ozzik, feeding, and deliberately dangerous. Fine work, high tech and art please him,
  and his pleasure is a pride-meter that draws Sh'kaar and Zizzik. The Salvation's answer is his
  own folk gesture: every fine work carries a deliberate flaw *"so the crown never quite fits"*.
  The rite lets the clan please him for once, at the mountain where Sh'kaar has just been paid,
  without letting the work be perfect.
- **Outcomes:** Poor, the flaw spoils the item a quality step. Fair, the item keeps its quality and
  carries "the maker's mark" in its description. Good, Ozzik up, and the rise draws less of
  Sh'kaar's and Zizzik's attention than the same item made without the rite. Excellent, plus an art
  tale. Ninefold: Ozzik up, with the amplifier onto Sh'kaar and Zizzik damped for this one delta
  (UNMEASURED: whether Ninefold's `ApplyDelta` can take a per-call amplifier factor; if not, a
  separate small Sh'kaar settlement call stands in).
- **Inscription:** *"Make it as fine as you can. Then mark it, so that it is not perfect, so that
  no one comes for it."*

## 7. The Leaning Scrub

**What it already has.** Everything leans. One fixed wind runs darkward to sunward. The Stall kills
the wind (true silence; every small creature freezes; anything moving under the fuzz is lit up),
and the Gale whites the canopy out, with raids riding it. Thunderstep giants stamp out any fire
and its source. The sheet's **calling-pyre** is the plain's one prayer: torch your own fields to
bring the herds down on all who remain, a last rite *"spoken of the way sailors speak of running
aground on purpose"*. It is already in the register (B6), PITCHED, god unassigned. Source:
`design/Jawa/worldbuilding/biomes/leaningscrub_bedazzle_review_2026-09-29.md` (slate 1, 6, 7, 8).

### 7.1 The Calling-Pyre (Zizzik, settlement)

_Status: ruled (card, 2026-10-01): MERGED with the controlled waking (register B4). The calling-pyre is the controlled waking's Leaning Scrub form. The controlled waking stays a general rite and still needs forms in other biomes._

- **Needs:** the colony's own field of dry fuzz or scrub, thunderstep herds on the map, and enemies
  present or arriving. The organiser sets the field alight on purpose. It is a last rite: it
  summons the herds onto everyone, the clan included.
- **Found:** a charred stake ring on the plain, the stakes still leaning with the wind, one of them
  carved. It can be studied only in the Gale, when the stakes hum.
- **God:** Zizzik, settlement (the bank spent). This is **the controlled waking** (register B4) in its Leaning Scrub form: Zizzik's slumber bank is a
  thing to manage, *when, not whether*, and spending it at a chosen moment is the only control the
  clan has. The pyre spends the bank on the player's schedule and points the disaster at the enemy:
  the clan picks the moment the catastrophe falls, and makes sure it falls on them too. Pyrrhic
  victories are his.
- **Outcomes:** Poor, the herds come and stamp the colony harder than the enemy (the stamped ground
  and the prints show it). Fair, the herds break the attack, and the clan pays in fields. Good,
  plus Zizzik's slumber bank is spent and his next waking will be gentle. Excellent, plus an art
  tale, "the day we called the giants". Ninefold: a settlement entry that spends Zizzik's bank.
- **Inscription:** *"When there is no way out, burn your own field. The giants will come for the
  fire. Let them find everyone."*

### 7.2 The Stall-Hold (Ishko, feeding)

- **Needs:** a Stall in progress, and every participant holding still under the canopy, in the open,
  for its length. Anyone moving breaks it (the ripple lights them up).
- **Found:** a thornhold hide woven into the base of a sweetline tree, a word cut into the trunk
  where a sitting Jawa's eyes would rest. It can be studied only during a Stall, because in wind the
  canopy moves across it.
- **God:** Ishko, feeding. Stillness itself pleases him, and here stillness is the only defence the
  plain gives. The Dark Vigil sits still in a dark nobody can see into; this holds still in the
  open, where everything can see, and nothing does. The stallhawk passes over.
- **Outcomes:** Poor, someone moved; the stallhawk dives or a scout spots the colony (a readable
  letter). Fair, the Stall passes without the colony being seen. Good, plus Ishko up and
  "nothing saw us" for all. Excellent, plus the next raid on this map arrives without knowing the
  colony's layout. Ninefold: Ishko up.
- **Inscription:** *"When the wind stops, so do you. Everything is looking. Be the thing it does
  not see."*

## 8. The Long Shade

**What it already has.** The one biome where the sun never looks away: a fixed low sun, the
golden hour, shade as currency, a roof as the most powerful act. The gloomcast, a bs-16 grazer,
carries its own shade across the plain. Slate 2 proposed **Sh'kaar's country** and a ritual called
**the Shade Tithe**: cutting a new roofed patch as liturgy. The Long Shade's gods mark is the sun
itself. Source: `design/Jawa/worldbuilding/biomes/longshade_bedazzle_review_2026-09-29.md`
(slate 1, 2, 9); the Holy Flame precept (`RUT_HolyFlamePrecepts.xml`) is any Ritualist ideo's, and
is not reused.

### 8.1 The Shade Tithe (Sh'kaar, warding)

- **Needs:** open, lit ground in the golden hour, and a new roof raised over it by the participants
  in one sitting. Not during the Searing, the rare white-out condition (slate 2c).
- **Found:** carved under the overhang of the oldest roofed patch at Shipfall Commons, cut so that
  only someone standing in its shade can read it. It can be studied only from inside shade.
- **God:** Sh'kaar, warding. He cannot be fought, only hidden from, and in this biome there is
  nowhere to hide but what you build. The Snuffing starves him of light in a dark place; this keeps
  his eye off the clan in the one place he never looks away from, by making new shade. No pause at
  the shade line is skipped. His folk gesture is the rite's first and last step.
- **Outcomes:** Poor, the roof stands and nothing more. Fair, the new patch counts double on the
  shade-harbour ladder (ruled #1) for a season. Good, plus a warding entry: Sh'kaar's escalation
  meter does not rise from this map's open-ground work for a few days. Excellent, plus devout
  colonies get the Searing's one-day warning (slate 2c) for the rest of the year. Ninefold: a
  warding entry for Sh'kaar.
- **Inscription:** *"He sees all of this. Build him something he cannot see into. Pause at the line,
  then go under."*

### 8.2 The Shadow Walk (Ta'Baa, feeding)

- **Needs:** a gloomcast crossing the map, and a party (with their leaving-bags) walking inside its
  moving shadow from one edge of its route to the other, never stepping into the light.
- **Found:** on a midden in the lee of a shadespire, a ring of leaving-bags long since emptied, one
  stone among them marked. It can be studied only while a gloomcast's shadow is over it.
- **God:** Ta'Baa, feeding. He and Ishko reconcile in exactly one posture, *hidden and watching for
  the instant to flee*. A Jawa walking inside a giant's shadow is that posture made into a road:
  moving, covered, ready. Ishko is pleased in passing, but the rite is aimed at Ta'Baa, because it
  is a journey, not a sit.
- **Outcomes:** Poor, the party fell behind the shadow and walked the last stretch exposed (the
  sun-heat they took is ordinary vanilla temperature). Fair, the walk is made; "we went with the
  shade". Good, plus Ta'Baa up and the party's despair moods lift. Excellent, plus the gloomcast's
  route is drawn on the map for a season. Ninefold: Ta'Baa up.
- **Inscription:** *"The big one carries the dark. Walk inside it, bag on your back. It is always
  leaving. So are you."*

## 9. The Stillsand

**What it already has.** Old Tatooine: the place Jawas were made for. A flat to every horizon, one
wind from one bearing, every shadow pointing at the star. The sand keeps tracks until the wind
erases them, crawler treads among them, sometimes with a dead crawler at the end. The rumble moves
under the sand. The mirage shows water that is not there. **The Return** is the Sun-Debt's ritual
(built, `RUT_TheReturn.xml`): the Deep Desert Tribes pour water into the sand at a debt stone.
That rite is theirs, and a Salvation colony cannot learn it (ruled 2026-10-01). Nothing below
pours, pays or owes the sun. Source: `design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md`
§1, §2.3, §2.6, §3.2, §4.

### 9.1 The Last Track (Ohm, consolation)

- **Needs:** a crawler tread on the map that ends at a dead sandcrawler, and the crawler's drive
  turned over by the party until it runs, however briefly, before any of it is stripped.
- **Found:** inside the dead crawler's cab, scratched on the dash in the clan's own trade script,
  the last driver's note. It can be studied only while the tread leading to it is still readable,
  so a gale that erases the track also closes the reading until the next one is found.
- **God:** Ohm, consolation. Machines abandoned broken grieve him, and he is lonely for what he
  lost. The crawler is the Jawa's own ancestral machine, dead on the sand that made them. The rite
  is not salvage and not a waking for keeps: the drive is turned over once, so the machine ends
  heard and not abandoned, and only then is it judged. (The Deserter's Welcome, §10.1, is the
  feeding counterpart: a machine that comes back.)
- **Outcomes:** Poor, the drive will not turn; the crawler is salvage as usual. Fair, it runs for a
  minute, a shared memory, "the crawler spoke". Good, plus Ohm's grief eases and a better yield
  from its salvage. Excellent, plus the driver's note names one more feature on the map (a cave, a
  seep). Ninefold: a consolation entry for Ohm.
- **Inscription:** *"We ran her until the sand had her. If you find her, start her once before you
  take her apart. She will know you."*

### 9.2 The Unspilled March (Oomo, feeding)

_Status: ruled-kept, as the Tribes' Return's opposite (card, 2026-10-01)._

- **Needs:** a mirage showing water on the horizon, and a party walking toward it carrying full
  water and drinking none of it until the mirage recedes.
- **Found:** a ring of sealed, still-full water jars half buried on a glasscrust line, the oldest
  route on the map. One jar is marked. It can be studied only while a mirage stands on the horizon.
- **God:** Oomo, feeding. His own form is *"the mirage-pool that recedes"*. He is pleased by water
  endured with disciplined rationing, and this is the one place where he is visibly in the sky. The
  rite is held next to the Sun-Debt's Return on purpose and is its opposite: the Tribes pour water
  out to settle a debt, while the Salvation carries it untouched toward the god who never falls.
- **Outcomes:** Poor, someone drank (the jar they carried says so). Fair, "we did not spill" for
  all. Good, plus Oomo up and the party's thirst moods ease for a day. Excellent, plus an art tale.
  Ninefold: Oomo up. The water is not consumed by the rite; it comes home.
- **Inscription:** *"He is the pool that walks away. Walk after him with full skins. Do not drink.
  He is watching the water."*

## 10. The Warscar

**What it already has.** A place where everyone already lost: slag terraces, fortifications facing
outward, the Settling (the war falls when the wind stops; the film keeps footprints until the wind
lifts the page clean), the hospice where deserter machines are woken in stages, the old tongue on
every panel, and the pilgrim camps facing the Rust Cathedral. Two things are already decided here.
**The Watch** (stand a night facing outward) was **RULED OUT** at turn 2, and nothing below
resembles it. **The pilgrim camps** are lore rungs on `RUT_ScarlandsLadder`, not rites, and stay
so. Source: `design/Jawa/worldbuilding/biomes/warscar_turn3_development_2026-09-30.md` §0, §2.1,
§2.7, §2.8, §2.10.

### 10.1 The Deserter's Welcome (Ohm, feeding)

- **Needs:** a hospice cradle on its last stage (day 7+, the waking), and the clan gathered round
  the cradle when the machine stands.
- **Found:** a campaign-tier fourth panel type among the old-tongue panels (§2.8; the free tier's
  three subtypes stay as built), on the chassis plate of a machine that knelt facing the Cathedral
  and never stood. It is read by the same Intellectual-8 job, and only after one deserter has
  reached its voice-fragments stage, because the panel's script is the one the deserters speak.
- **God:** Ohm, feeding. He is lonely for his lost hands and presses the clan to bring them back.
  Every deserter left its owner, ran and died slowly. The rite is the welcome it never had: its
  three memory lines are said back to it, and it joins as one of his.
- **Outcomes:** Poor, it wakes, nothing more. Fair, it joins with a memory, "welcomed", and its bio
  carries the clan's name for it. Good, plus Ohm up and a mood bonus for the machine. Excellent,
  plus an art tale of its desertion. The failed-chassis path is untouched: a failed repair is still
  `RM_FailedChassis`, named, never a blank chunk. Ninefold: Ohm up.
- **Inscription:** *"You ran. So did we, once. Say what you remember. Then stand up; you are
  ours."*

### 10.2 The Vindication Walk (Ta'Baa, consolation)

- **Needs:** a Settling in progress (the film down, the wind dead), and a party walking the length
  of the old outward-facing line across the film, in daylight, then back to the ship. The rite
  completes only when the wind returns and lifts their prints with everyone else's.
- **Found:** chalked on the inside of a firing slit in the old line, facing inward, the only
  inscription on the line that does. It can be studied only during a Settling, when the film shows
  the chalk.
- **God:** Ta'Baa, consolation. Old battlefields are his holy ground: to stand in the ruins of
  others is proof you made the right calls and they did not. Despair is his one blasphemy, and the
  Warscar is despair made into terrain. The walk lays it down. It is not a watch: the party
  walks, does not stand, faces the way home, and is gone before night.
- **Outcomes:** Poor, the wind returned before the walk was done, and the half-line of prints shows
  where they turned back. Fair, despair and "lost" moods ease for the walkers. Good, plus Ta'Baa up
  and an inspiration chance. Excellent, plus an art tale, "we walked where they stood". Ninefold: a
  consolation entry for Ta'Baa.
- **Inscription:** *"They stood here facing out and they all lost. Walk it facing home. Let the
  wind take your tracks."*

## 11. Summary: every new rite and its god

| # | Biome | Rite | God | Kind | Condition (the gate) |
|---|---|---|---|---|---|
| 1.1 | Contagion | The Sunning | Oomo | feeding | a Burn; red water in the open |
| 1.2 | Contagion | The Unfinished Laid Down | Rekko | consolation | an undissolved Unfinished at the burn line |
| 1.3 | Contagion | The Kept Mistake | Zizzik | warding | a broken thing left before a Bloom sortie |
| 2.1 | Wasteland | The Storm's Receipt | Mob'Unloo | feeding | a fresh storm-exhumation site |
| 2.2 | Wasteland | The Salted Keeping | Ozzik | venting | a vitrified crater; the colony's finest thing |
| 2.3 | Wasteland | The Inherited Wreck | Rekko | settlement | a failed expedition's wreck in the hot ground |
| 3.1 | Blue Desert | The Returned | Ta'Baa | consolation | a body the ablation line gave up |
| 3.2 | Blue Desert | The Charged Reed | Ishko | feeding | a ripe reed field's charged heart; no fire, ion or light |
| 4.1 | Cracked Lands | The Chime Vigil | Oomo | warding | the chime window, on a refuge ledge |
| 4.2 | Cracked Lands | The Mud Claim | Rekko | feeding | the salvage-strike window after a recede |
| 5.1 | Cauldron | The Filtered Cup | Oomo | consolation | first water from a filter converter |
| 5.2 | Cauldron | The Engine Hour | Ohm | feeding | the ground loud (not a bloom's silence) |
| 5.3 | Cauldron | The Capping | Zizzik | starving | an uncapped vent; no flame in radius |
| 6.1 | Forge | The Anvil Gift | Sh'kaar | venting | a lava lake or crater; a weapon given |
| 6.2 | Forge | The Flawed Masterwork | Ozzik | feeding | a masterwork made at a vent forge |
| 7.1 | Leaning Scrub | The Calling-Pyre | Zizzik | settlement | own field fired; herds and enemies present |
| 7.2 | Leaning Scrub | The Stall-Hold | Ishko | feeding | a Stall; everyone still in the open |
| 8.1 | Long Shade | The Shade Tithe | Sh'kaar | warding | golden hour; a new roof raised; no Searing |
| 8.2 | Long Shade | The Shadow Walk | Ta'Baa | feeding | a gloomcast crossing the map |
| 9.1 | Stillsand | The Last Track | Ohm | consolation | a crawler tread ending at a dead crawler |
| 9.2 | Stillsand | The Unspilled March | Oomo | feeding | a mirage on the horizon |
| 10.1 | Warscar | The Deserter's Welcome | Ohm | feeding | a hospice waking (day 7+) |
| 10.2 | Warscar | The Vindication Walk | Ta'Baa | consolation | a Settling; the walk ends when wind lifts the prints |

### God coverage across all eleven biomes (the Abyss's four included)

Counted by hand from the table above plus register B2 (not an instrument).

| God | Found rites | Where | Kinds | Read |
|---|---|---|---|---|
| ① Ishko | 3 | Abyss, Blue Desert, Leaning Scrub | feeding ×3 | balanced count; ⚠️ only ever fed, never another kind |
| ② Ohm | 3 | Cauldron, Stillsand, Warscar | feeding ×2, consolation | balanced; the Last Track (a machine ended, heard) and the Deserter's Welcome (a machine returned) want telling apart in play |
| ③ Oomo | **4** | Contagion, Cracked Lands, Cauldron, Stillsand | feeding ×2, warding, consolation | 🔴 **overfed**: the most of any god. It follows from water being the planet's scarcity, so every wet biome pulls toward him. First trim for the renormalize pass. |
| ④ Mob'Unloo | **2** | Abyss, Wasteland | settlement, feeding | 🔴 **starved**: the fewest. Candidates the renormalize pass could take: the Long Shade's shade currency (a rented shade patch), or the Cracked Lands' Hutt toll gate. |
| ⑤ Rekko | 3 | Contagion, Wasteland, Cracked Lands | consolation, settlement, feeding | balanced, and the widest spread of kinds |
| ⑥ Ta'Baa | 3 | Blue Desert, Long Shade, Warscar | consolation ×2, feeding | balanced |
| ⑦ Zizzik | 3 | Contagion, Cauldron, Leaning Scrub | warding, starving, settlement | balanced |
| ⑧ Sh'kaar | 3 | Abyss, Forge, Long Shade | starving, venting, warding | balanced; never fed outright, as an evil god should be |
| ⑨ Ozzik | 3 | Abyss, Wasteland, Forge | consolation (interim), venting, feeding | balanced; the Lightless Burial row is interim per `SALVATION_RITES_RENORMALIZE_PASS_1` |

**Total: 27 found rites** (4 Abyss + 23 here). Every god has at least two, none more than four.
Every biome carries two or three, and no biome repeats a kind.

### Collision check against the register (b)

- **Ozzik:** the Salted Keeping vents by humility and keeps the item, the Unburdening (B4/B5)
  vents by destroying wealth, and the Lightless Burial (B2) vents by laying grief down. They are
  three acts, not one.
- **Zizzik:** the Calling-Pyre is the controlled waking (B4) in its Leaning Scrub form: one rite,
  one register row. The waking still needs forms in other biomes.
- **Ohm:** the machine-funeral (B4, a machine's end) is not the Deserter's Welcome (a machine's
  return).
- **Oomo, Stillsand:** the Unspilled March sits beside the Sun-Debt's Return (B6) and is its
  opposite: it carries water, it does not pour or pay. It is not a Salvation copy of the Return.
- **Sh'kaar, Long Shade:** the Shade Tithe is slate 2's own name, so this pass keeps it. Revering
  the Holy Flame (B6) is a different faith's precept and is untouched.
- **Leaning Scrub:** the B6 row "the calling-pyre, unassigned" is this pass's 7.1, merged into B4's controlled waking.
- **The Watch** (B6, RULED OUT) has no successor here. The Vindication Walk is a daytime walk
  toward home, not a night stood facing out.

### Rulings (cards, 2026-10-01, 13:43 to 14:03 PDT)

1. **Rites are allowed everywhere** (typed): the Blue Desert carries rites. The Returned (§3.1) is kept.
2. **The Charged Reed** (§3.2): Ishko, a charged reed cut and carried as a warning whistle.
3. **The Calling-Pyre** (§7.1) merged into the controlled waking (B4); register is one row.
4. **The Flawed Masterwork** (§6.2) kept, pending `FLAWED_MASTERWORK_ENGINE_CHECK_1`.
5. **The Unspilled March** (§9.2) kept as the Tribes' Return's opposite.
