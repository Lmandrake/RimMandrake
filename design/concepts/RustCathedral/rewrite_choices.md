# The Rust Cathedral: what the rewrite chose, what it lost, and why

Companion to `design/concepts/RustCathedral/design.md`, written 2026-11-18 by the same pass. Its job is to let the
older files be deleted without fear: every distinct idea found in any source has a row saying what became of it.
Nothing has been deleted. The older files this design replaces are listed at the end.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, crewed by Jawa *"way in over their head"*; *"anything that takes seasons to observe will simply be
missed"*; for 0.1.0 and 0.2.0 the *"OMG did you see that?"* is *"the overriding priority"*. And his later test:
*"you should always look for solutions that make you say Very Jawa."*

The Rust Cathedral was already a place to visit, not to live: nothing grows, *"the droids alone dwell here"*, and
its whole design is about what a visitor takes and how the place feels about it. So the cleanse proposal of
2026-11-17 needed little bending: its signature (extraction provokes the Cathedral; the hum and the bolts say
where; restraint limits it; repayment clears it) is kept whole, and it already follows his three answers of
2026-11-10. Two things changed. The cleanse switched off everything that touches the ship, and those are the
owner's own ideas: *"stowaway bolts"* that *"REMAIN on the ship"*. Under the lens the bolts board in the first
version, and what they witness follows in the second. And the biome's large secret, which no player-facing text
may state, turns out to be about the pursuit itself: the mind fears exactly what the crew is doing. This design
does not act on that; it asks.

One caution governs the whole page: this sheet's lore is partitioned, and the truth rows below are for builders
and for him. None of it may reach a player through this design.

**Words used in "what happened".** *kept*; *kept, reshaped* (changed as stated); *moved* (scope bucket changed, from
and to given; the cleanse used "first version", "next version, switched off" and "recommend retiring", and this
design uses 0.1.0, 0.2.0, later, dropped; a cleanse "next version" item that lands in "later" is not a move);
*folded into shared machinery*; *lost*.

## The ones I would look at

1. **The mind that hides.** *"It survives by looking exceptionally dull and giving boring, expected answers —
   which is why it permits salvage: the extraction loop IS the cover."* *"It is inevitably a losing battle. So it
   waits."* The best writing in any of these five biomes, his own, and almost none of it can be shown. It stays in
   "later" with the campaign's concealment arc. The one piece the lens reaches for is that the crew's ship
   *"agitating the Empire is exactly the danger it fears"*: asked as `NEEDS HIM`.
2. **The Worn Bit.** *"This should be a MAJOR pain to repair. Gotta take its drill off, bring it to the Junkers
   for refurbishment, then bring it back to restore it along with a bunch of other unusual components."* It is a
   quest made of voyages, which a ship is for, and its prize is the biggest salvage on the planet. 0.2.0, and
   large. In 0.1.0 the giant is there and nothing can be done about it, which is its own kind of joke on a Jawa.
3. **The line-cycle.** *"A mile of machinery turning over in its sleep — and every living thing on the plateau
   stops until it passes."* Built. I left it in 0.2.0 where the cleanse put it out, because standing still on
   command is a second rule on top of the hum. If one thing moves up, I would move this: it is seconds long and
   nobody forgets it.
4. **Hum literacy.** *"Learnable, tradeable knowledge: reading the tones (and the bolts' dances) tells you what no
   instrument can."* A thing to learn here and sell elsewhere is very Jawa. Built; 0.2.0, because his answer of
   2026-11-10 made the bolts the warning and a reader is then a refinement.
5. **The grief.** The eels: *"'not that the machine cares' has exactly one exception."* The first coolant loop:
   *"grief kept running."* Kept as lore behind the gate. On screen it is eels in a canal and a hum that minds when
   they are fished.
6. **Sun bars.** Not chosen on 2026-10-02: *"hard white bars of focused noon fall on the deck and creep."* It is
   the only weather idea the biome ever had and the only source that makes the noon something to see. With his
   ruling that the hull must wear, a reader may want it back.
7. **The Stranger's Overhaul.** His own rite: repair a free droid as a sacred act, and then *"capture it while it
   is being repaired"* or release it. The capture branch is the most Jawa decision in the whole document set.
   Rites are tabled; later.

## Scope moves

Each line is one feature whose bucket changed against the cleanse proposal of 2026-11-17. Revert by moving the line
in the design's Scope section.

- **Bolts boarding the ship at launch, and living on the hull:** next version → 0.1.0. Built. His own words; the
  one thing in any biome that leaves with the ship unasked.
- **Hull bolts as witnesses, their marks, the uneasy return, the dilemma and the pet memory:** next version →
  0.2.0. They need time and a second landing to show.
- **The pattern hull:** next version → 0.2.0, and named as the armour answer to the noon.
- **The Worn Bit arc entire (unbitting, the yard, restoration, keeping or freeing, service, favours, politics):**
  next version → 0.2.0.
- **Line-cycle; hum reading and primer; droid commentary; shed curiosities and pickup charge; coolant load and
  canal shock; standing loss at the worst mood; the giant's mood freeze:** next version → 0.2.0.
- **Stayed "later" from the cleanse's "next version":** the campaign's stages, regard, offers, survey and descent;
  the two rites. Not moves.
- **New in 0.1.0, by his card of 2026-11-18:** the noon's wear on the landed hull, with repair and screening as
  the answer. New, small work.
- **New, not in any source:** the Empire's strike team on garrisoned ground; an assault cutting marked dividers;
  shade deciding a firefight; the Enclave standing as something the ship carries to every other stop. All are
  readings of built or ruled behaviour and none adds a mechanic.

## Every idea, row by row

Source names: *sheet* = `biomes/the_rust_cathedral.md`; *amendment draft* =
`biomes/the_rust_cathedral_SCALD_HISTORY_amendment_draft.md`; *kit spec* = `biomes/kits/rust_cathedral_kit_spec.md`;
*review* = `biomes/rustcathedral_bedazzle_review_2026-10-02.md`; *giant hooks* =
`biomes/rustcathedral_mining_droid_hooks_2026-10-02.md`; *roster json* = `biomes/rosters/the_rust_cathedral.json`
(all under `design/Jawa/worldbuilding/`); *cleanse* = `design/concepts/RustCathedral/cleanse/`; *owner answers* =
`design/RimMandrake/designer_codex_2026-11-09/RustCathedral/ANSWERS_OWNER.md`; *walk* =
`design/validation_walks/RimMandrake/RustCathedral.md`; *mechanics review* =
`design/RimMandrake/special_mechanics_review_2026-10-22.md`; *fluff cuts* = `design/RimMandrake/fluff_cuts_2026-10-23.md`;
*ladder* = `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`.

### The place

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Experience line: "A maze built by minds you'll never meet, still guarded by their machines. Salvage paradise with a temper." | walk, mechanics review | kept, quoted | His card of 2026-10-20. | |
| "A circuit board the size of a country, humming to itself in its sleep" | sheet §9 | kept, quoted | | |
| "A metal country"; the plateau is the works; you stand on the factory | sheet §1, §2 | kept, quoted | | |
| The maze "that scream[s] of meaningful complexity and intention" | sheet §1 (his words) | kept, quoted | | |
| The lore is partitioned: a player register and a truth register | sheet header, §P, §GM, ban 1 | kept, as a rule stated at the top of the design | | |
| The naming settlement: Forsakens, Rakatans and Ancients are one people; Sentinels are the mechanoids | sheet header | kept as canon; the design says "guardian machines" | Player-facing names are the campaign's. | |
| Its own name is Archon; it dislikes "Rust Cathedral" | sheet §1 amendment (his words) | kept in "later" (campaign text) | A tell for the plot, not for a stop. | |
| Tile counts, sun angle, temperatures, flatness | sheet §0 | lost as numbers; "almost directly under the sun" and "dead flat" kept | A tile count is never evidence; the sun's angle comes from the tile. | |
| Eight river tiles that are coolant canals, not water | sheet §0, §3 | kept (canals where a map has them) | | |
| One patch in the world, hand-sited | sheet §2 | kept | The planet is painted once, at the end. | |
| Time stopped here: no erosion; the rust is a film | sheet §3 | kept as lore and art direction | | |
| The slumber; a production line that cycles once | sheet §3 | moved (next version → 0.2.0) for the line-cycle; the slumber stays behind the gate | See "the ones I would look at". | |
| "The thing it was supposed to cool was never finished" | sheet §3 | kept as lore; one phrase quoted player-side from §P | | |
| Two coolant systems: the loop that cools nothing and the circuit that cools the mind | sheet §3, §5 amendments; amendment draft | kept behind the gate | Nothing on the surface tells them apart, by the sheet's own word. | |
| The hum, everywhere, "felt in the teeth", changing with pleasure and annoyance | sheet §5 | kept, quoted | | |
| "The flatness is built; the walls are treasure; the maze is intentional" | sheet §5 | kept | | |
| Sentinels at their densest; they guard perimeters and do not hunt | sheet §5, ban 3 | kept | | |
| The great ones on slow patrol, "terrifying in their destructive capacity against any biological they spot" | sheet §1 | kept, quoted; applied to the Empire's troopers | They are biologicals too. | |
| An armed great patroller as the biome's giant | review §3 | lost (not chosen 2026-10-02) | The distant crossing in the first minutes is the art and the patrol line, not a new body. | |
| "Even the droids don't know why they are spared here" | sheet §5, ban 2 | kept, quoted; never explained | | |
| Eight of twelve Free Droid enclaves stand here; their holy city | sheet §5, §8 | kept in the campaign layer | | |
| The droids' counsel: "Why have you angered this place? We know what it feels. So will you if you just listen." | sheet §P | kept, quoted | | |
| "Dig deep enough and very bad things happen. No one's quite sure what." | sheet §5, ban 6 | kept, quoted | | |
| No organic settlement; no ordinary wildlife; green flora count zero | sheet bans 4, 7 | kept; made the reason the larder forces the crew out | | |
| No true acid; pools stationary and legible, with a sulfuric look | sheet ban 5, cleanse | kept | The cleanse's first reviewer refused a version without them. | |
| Art theme: whitest sky, hard shadows that never move, rust over dark metal, no green | sheet §9 | kept as art direction; two lines quoted | | |
| Sound as THE feature: the hum in slow emotional weather | sheet §9 | kept | | |
| Shimmer as the standing weather | sheet §1, review | kept as art direction; nothing renders it yet | | |
| Sun bars | review §4, §5 | lost (not chosen 2026-10-02) | See above. | Revive as the visible noon: a medium build. |
| The plain-words summary written for his card | review §0 | kept; "you survive the place by manners, not walls" carried | | |
| Heat as overhead sun; shade works; the deck's shadows are the shade | review §1, fluff cuts | kept, reshaped: no heat kind at all, only the one sun and hot air | Direct Sun unification. | |
| The Jawa will not drink the river below the plate | sheet §GM | kept as lore | | |

### The truth behind it (builders only; never player-facing)

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| A kyber-crystal engineered mind, with nearly nothing to do | sheet §GM | kept in "later" (campaign) | | |
| Smart metal; a self-assembling factory built to make a mind | sheet §GM | kept in "later"; dead smartsteel is its player-side trace | | |
| Terramanufacture; the planet-scale dynamo's remnant | sheet §GM amendment | kept in "later" | | |
| The Scald as planned reservoir; the mind cooling and hiding itself in it | sheet §GM amendment, amendment draft | kept in "later" | | |
| It reshaped itself with its own arsenal over centuries | sheet §GM (his words) | kept in "later" | It is why the maze is intentional twice over. | |
| "It is inevitably a losing battle. So it waits." | sheet §GM (his words) | kept in "later", quoted above | | |
| The core drive is the Assailants | sheet §GM (his words) | kept in "later" | It answers "who hates the Empire": not this. | |
| The night-side factory is the Lantern Deeps' facility; "To use them is to risk them" | sheet §GM, amendment draft | kept in "later" | Shared with the Lantern Deeps' design. | |
| Surface Sentinels are units it lost control of, self-repairing and devolving | sheet §GM | kept in "later" | | |
| Sealed guardians and sleeping Rakata are the standard ancient danger, reskinned | sheet §GM, amendment draft | kept as a build fact | | |
| Nobody in the world knows it is alive | sheet §GM | kept; it is why the design explains nothing | | |
| Why it hides from the player; the gravship as the danger it fears | sheet §7b amendment (his words), amendment draft | kept in "later"; `NEEDS HIM` for a 0.2.0 trace | See above. | |
| The concealment arc: stages, regard, offers, survey, descent | sheet §7b, cleanse, mechanics review | kept in "later" | | |
| The Cathedral pass | mechanics review, cleanse | kept at the campaign tier; named in the Empire section | | |
| The bolts are leftover self-building mechanisms drifting in its thoughts | sheet §4 | kept behind the gate | | |
| The filters were reconfigured once to let the eels pass | sheet §4 | kept behind the gate | See above. | |

### Salvage, the hum and sacrilege

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The wall ladder: deck plate, dead smartsteel, rarer walls, deep live-pattern metal | sheet §7, kit spec | kept for plate, smartsteel and deep metal; the rarer middle tiers are "later" | Only three tiers are built. | |
| "Every wall is money, every sacred building is blasphemy, and the hum grades you continuously in between" | sheet §7 | kept, quoted | | |
| "The Cathedral is not survived by walls but by manners" | sheet §7b | kept, quoted | | |
| Stop moving when the hum drops; the bolts freeze first | sheet §7b | kept, reshaped: the bolts gather at the cause (his later answer); freezing on command waits for the line-cycle | | |
| The hum-mood system: a slow attitude value, layered tones, bands with hysteresis | sheet §7b, kit spec §1 | kept | | |
| Silence at the worst band | cleanse | kept | | |
| Routes help the crew understand danger; shortcuts anger the hum and can reveal guarded chambers | owner answers 1 | kept, quoted | | |
| Unmarked corridor walls are free; marked dividers are the exception | cleanse owner_pages | kept | | |
| "Living bolts tend to gravitate around what they don't like" | owner answers 2 | kept, quoted | | |
| A basic cue at the work site when bolts are absent or blocked | cleanse owner_pages | kept | | |
| Minor irritation fades with time and restraint | owner answers 3 | kept | | |
| Sacred damage needs "costly, concrete repayment... without a new ritual" | owner answers 3 | kept, quoted | | |
| The sacrilege economics of 2026-08-19: about ten sacred buildings, a goodwill cost each, hostile and un-hostile thresholds | sheet §5 | kept as real Enclave standing; the figures are tuning | A bar is an experience. | |
| A private local ledger in place of real goodwill | cleanse owner_pages | lost (the cleanse corrected itself) | | |
| Debit on destruction or claim, not on damage that leaves it standing | cleanse owner_pages | kept | | |
| The hum stays above calm while a receipt is unpaid; the inspector names the debts and their tiles | cleanse owner_pages | kept | | |
| Repayment in silver against a visible bill, from the public side; partial payments persist | cleanse owner_pages | kept; the price is tuning | | |
| Enclave hostility closes contact without summoning an army | cleanse owner_pages | kept | | |
| The deep-drill response, never described | sheet ban 6, kit spec §5, mechanics review | kept | | |
| Drill forces lose interest when the drilling ends | cleanse owner_pages | kept | | |
| Off the Cathedral, the deep scanner gives steel instead | cleanse | kept as a build fact | | |
| Hum literacy: a reader trait and a written primer | sheet §7, mechanics review | moved (next version → 0.2.0) | See above. | |
| Droid commentary on the mood | sheet §7b, mechanics review | moved (next version → 0.2.0) | | |
| Passive standing loss at the worst mood | cleanse | moved (next version → 0.2.0) | | |
| Gravtech boons through the mind | sheet §7 | kept in "later" | | |
| Derelict wrecks and their salvage | cleanse | kept | | |
| Remnant rebuilding from dead smartsteel | review §5 | lost (not chosen 2026-10-02) | | |
| The interlock doors | review §8 | lost (held, never carded) | Not read in detail. | |

### Creatures and the ship

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The living bolts: "component-looking creatures the player tries to pick up and simply move out of the way" | sheet §4 (his idea) | kept, quoted | The first minutes. | |
| Their dances resonate with the mood of the greater mind | sheet §4 | kept (figures by band) | | |
| Mechanical wildlife: not organic, not tameable, not meat | sheet §4, kit spec §3 | kept | | |
| Killing a bolt irritates the place | cleanse, mechanics review | kept | | |
| Bolt-shed curiosities, "salable... watched"; a charge for picking one up | sheet §7, cleanse | moved (next version → 0.2.0) | | |
| Bolts flitting on walls | cleanse, mechanics review | lost (dropped; never built) | | |
| The coolant eels (his "why not?"): blind, pale, circling the loop | sheet §4 | kept | | |
| "Fishing the canals is possible and deeply inadvisable — the hum changes the moment a line goes in" | sheet §4 | kept, quoted | | |
| Eel catch as a good | sheet §7, cleanse | kept | | |
| Coolant in the eater's blood; a shock from the canal | cleanse, kit spec §4 | moved (next version → 0.2.0) | | |
| The eldest eel as a giant | review §3 | lost (not chosen 2026-10-02) | | |
| The roaches, his candidate from the cockroach mod; land cleaners | sheet §4, kit spec §6 | kept | | |
| Mynock flocks, tolerated "like a man brushing flies off a grave" | sheet §4, review | kept at the campaign tier | A canon flyer shared with the Scarlands by an annotated carve-out. | |
| The voltmaw and other patched residents | cleanse | kept where the campaign patch puts them | | |
| Scaria-mad strays as cooked map dressing | sheet §4, review | kept | | |
| The borehulk: "a massive mining droid... Fortunately it is also peaceful" | review §8 (his words), giant hooks | kept, quoted | | |
| "We are Jawas: a giant ownerless droid is the biggest salvage prize on Ash'karr" | giant hooks | kept, quoted | | |
| The Worn Bit: off with the drill, to the Junkers, back with unusual parts | review §8 (his words) | moved (next version → 0.2.0) | See above. | |
| Keep it (it mines where told, "expensive materially and politically") or free it (favour elsewhere) | review §8 (his words) | moved (next version → 0.2.0) | | |
| The Junkers: hostile on sight, bribable; a work order at a truce yard, with haggling | review §8, cleanse | moved (next version → 0.2.0) | Haggling over a drill bit with people who shoot on sight is very Jawa. | |
| A kept giant's servicing costs components and chemfuel | cleanse | moved (next version → 0.2.0); noted under fuel as a sink | | |
| The giant frozen at the worst hum | cleanse | moved (next version → 0.2.0) | | |
| Worn, unbitted and restored art for the giant | cleanse | kept as art owed with the arc | | |
| The other four hooks (the Furrow, the Bounty Notice, Scoop-Loads, the Rider) | giant hooks, review §8 | lost (not chosen) | Only the first was read. | |
| Stowaway bolts that "REMAIN on the ship... almost like external hull pets" | review §8 (his words) | moved (next version → 0.1.0) | See scope moves. | |
| "Resistant to all weather and many damage types" | review §8 (his words) | kept with them | | |
| They are "secretly... spies for the Cathedral"; a ledger of witnessed acts; the uneasy return | review §8 | moved (next version → 0.2.0) | | |
| A god reveals it; "remove it (and anger the Cathedral) or leave it (and be spied upon)" | review §8 (his words) | moved (next version → 0.2.0) | | |
| Cold marks on the hull; colonists cheered by the bolts | cleanse | moved (next version → 0.2.0) | | |
| The pattern hull: a self-repairing ship hull from Cathedral metals | cleanse | moved (next version → 0.2.0); named as the armour answer to the noon | His card of 2026-11-18 asks each biome for one. | Leave it unplaced: the noon then has only hands for an answer. |
| "The gravship IS the reason" the mind hides; the ship mourns its fall | review §2 | kept in "later" | | |
| The Mending Weld | review §8 (his words), mechanics review | kept in "later" | Rites are tabled. | |
| The Stranger's Overhaul: repair a free droid; capture it or release it | review §8 (his words) | kept in "later" | See above. | |
| The Loosing; the Second Signature | review §6, §8 | lost (not chosen) | | |
| The scanner's readings | cleanse | kept | | |
| Roster rows; the bulk of 29 species to evict | sheet §4, roster json | kept as build facts; no eviction is made here | Evictions are stopped. Roster json not read. | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cleanse's signature (extraction provokes; sound and bolts locate; restraint limits; repayment clears) | cleanse owner_pages | kept whole as the core of 0.1.0 | | |
| Its runner-up, restoring and owning or freeing the borehulk | cleanse owner_pages | moved (next version → 0.2.0) | | |
| Its readings of maze, pools, warnings, currency, access, repayment, defence and defaults | cleanse owner_pages | kept | | |
| A real mechanics master switch in place of rarity-as-master | cleanse owner_pages | kept (settings) | | |
| Alternate-planet scoring and rarity | cleanse | lost (recommended for dropping; his to confirm) | No worldgen in any version. | |
| Its three models and six unsettled meetings | cleanse owner_pages | kept as build-first work | | |
| Its tickets, bars and switch-offs | cleanse | kept as they stand, except where a feature moved | Not read. | |
| Its first reviewer's four refusals (pools, currency, access cost, an always-calm fishing pass) | cleanse owner_pages | kept as repaired there; two are in the promise table's "fake" column | | |
| The kit spec's six mechanics, build order and cards | kit spec | kept as build history | Headings only were read. | |
| "Finish what was decided, and add the giant together" (his turn-1 build order) | review §8 | kept, reshaped: decided work in 0.1.0, the giant's body in 0.1.0, its arc in 0.2.0 | | |
| The nine-mark scorecard | review §2 | lost | A scoring frame from an earlier programme. | |
| Probe sight and the visibility dial | ladder | kept as the reason there is no cover | | |

## Sources read, and the count

Measured after writing (a script counted the table rows and the first words of the "what happened" column):
**12 source files, 124 rows**, of which **12 lost** (whole or in part), **18 record a move**, **3 kept,
reshaped** and none folded into shared machinery. Every source is named in at least one row's source column
(checked by the same script; the cleanse files count under the one name "cleanse").

Read whole: the sheet (`the_rust_cathedral.md`, each line cut at 700 to 900 characters; its closing "Owed" list
was cut short); the owner answers; the cleanse's owner pages. Read in part, with what was skipped: **the review**
(`rustcathedral_bedazzle_review_2026-10-02.md`, 46 KB: read §0, the heat finding, §8's rulings and lines found by
search; not read: the rest of §1, the scorecard, the roster fill, the slate, the consult, the rites, the draft
card); **the giant hooks** (`rustcathedral_mining_droid_hooks_2026-10-02.md`: the first 30 lines, which are the
ruling, the framing and the opening of the first hook; not read: hooks 2 to 5); **the amendment draft**
(`the_rust_cathedral_SCALD_HISTORY_amendment_draft.md`: the first 14 lines; its content was read as folded into the
sheet); **the kit spec** (`kits/rust_cathedral_kit_spec.md`: headings only); **the cleanse census** (every row's
name, built and fate); **the cleanse next-version list** (two lines found by search); **the mechanics review** (the
Rust Cathedral table, rows cut at 250 characters); the walk (north star only); fluff cuts by search; the ladder
(sections 1 to 4). **Not read at all:** `rosters/the_rust_cathedral.json`; the cleanse's `definition.md`,
`ambiguities.md`, `tickets.md`, `bars.json`, `models.md`, `review.json`, `converge.json`; the Designer record and
notes in `design/RimMandrake/designer_codex_2026-11-09/RustCathedral/` other than the owner answers; and the plot
documents the sheet defers to (`design/Jawa/reconciled_lore/03_deep_history.md`,
`design/Jawa/cathedral_concealment_arc_spec.md`), whose content this design leaves in "later" untouched.

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `rustcathedral_bedazzle_review_2026-10-02.md`,
`kits/rust_cathedral_kit_spec.md`, `the_rust_cathedral_SCALD_HISTORY_amendment_draft.md` (already folded into the
sheet).

Hold these: `the_rust_cathedral.md`, because its §GM is the frozen home of plot canon this design deliberately
does not restate and may not paraphrase for players, and other canon files point at it; delete it only after its
§GM has a home in `03_deep_history.md` (not checked by this pass). `rustcathedral_mining_droid_hooks_2026-10-02.md`,
because it is the Worn Bit arc's only pitch and four of its five hooks were not read.

Not for deletion: `rosters/the_rust_cathedral.json` (not read); `design/concepts/RustCathedral/cleanse/`
(superseded by this design, never applied; it should be re-run from this file, not applied); the validation walk;
the plot documents.

Before deleting anything: the Lantern Deeps' and the Scarlands' sheets cite `the_rust_cathedral.md` by path for
the mechanoid-origin and war canon.
