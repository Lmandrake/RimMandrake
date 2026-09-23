# Greentide flora roster — 15 invented trees + 7 invented understory plants, 2026-09-22

**Status: DESIGN PROPOSAL. Nothing authored.** No ThingDef written, no art commissioned, no def
edited. This document exists to be ruled on; a build seat implements whatever survives.

Item: `GREENTIDE_JUNGLE_TREE_ROSTER_1`. Ownership precedent: `TREE_GRAPHICS_OWNERSHIP_1`.
Density and economy: `GREENTIDE_BIOME_DENSITY_1`.

---

## READ FIRST — every plant on this page is OURS and INVENTED

**Owner ruling, 2026-09-22**, which this revision serves:

> *"I don't think it's important to use actual Star Wars trees. They're not a primary part of the
> universe. Let's just make our own tree and thus the mod isn't encumbered with Star Wars plant lore
> that no one even remembers, easier for the non-star-wars version anyway. You may get inspired by
> the star wars versions you found, but we're making our own. There should be no conniferous plants
> here, but rather large-leafed lush plants, plants with hanging tentacle-like leaves, willow-like
> canopies... get wild with them."*

⇒ **No row carries a canon name.** Every defName is `RM_`-tier, every label is a coined word, and
the roster sits in `RM_Greentide`'s own `wildPlants` — there is no Star Wars plant patch layer for
this biome's flora at all. The franchise-free mod is therefore exactly as rich as the campaign one,
which is what the 2026-09-22 tier ruling required and what this item previously could not deliver.

**The canon research that preceded this is kept as Appendix A — inspiration notes, not live rows.**
It earned its place: it produced a set of proven silhouettes and economic roles. It makes no claim
about anything that ships.

### The silhouette brief is the specification

- ⛔ **No coniferous forms.** No needles, no spires, no pines. Hard, biome-wide.
- ✅ **Large-leafed and lush** — leaf mass is the motif.
- ✅ **Hanging, tentacle-like leaves.**
- ✅ **Willow-like canopies.**
- ✅ *"Get wild with them."* Strange beats tasteful.

🔑 **Silhouette variety is load-bearing, not decoration.** `GREENTIDE_BIOME_DENSITY_1` rules
*"virtually no squares uncovered by lush foliage"* — so a roster of similar round crowns becomes an
unreadable green smear at exactly the moment the player most needs to parse the map. §3e is a
form-and-colour matrix proving no two rows share a silhouette, and it is the acceptance test for
this roster, not a nicety.

---

## At a glance

**Two giants, differing by LIFE STAGE.** Ruled 2026-09-22: the *signature* giant is the one
**already built** — `RUT_GreatboleCore`, a structure you mine into, which cannot be felled — **and a
separate fellable giant also exists**, because choosing a non-fellable landmark had silently deleted
the rung premium hardwood came from. They are the same species at different ages: the fellable one is
a mature tree, the landmark is what one becomes after centuries. §4.

**Fifteen trees in four strata.** The fourteen below sit in three; the giant is the fourth, above them
all — which is where the hugeness comes from. His ruling was *keep the range and add above it*, so no
mid-storey row was inflated:

| canopy — the fall is a map event | mid-storey — the working forest | understory — under the Roil |
|---|---|---|
| **veluthar** — umbrella of paddle leaves | **brunnock** — the hardwood | **quathis** — a single flat fan |
| **mourvel** — willow curtain to the ground | **ghemmel** — bleeds red; the commons | **thalquith** — aquamarine lattice that hums |
| **kaddrath** — roots first; the causeways | **nemmer** — fruit too big for the branch | **cundral** — acid pods, forageable root |
| **sarnstilt** — a tripod standing in the river | **vurmeloth** — the crimson export | **gorbeleth** — a throat that spits |
| | **mirrelbole** — splits and bleeds the fuel sap | |
| | **zhorrel** — the strangler curtain | |

**Above all of them: `RM_Greatbole`, the fellable giant — 16 cells.** Row 22, §3a0.

**Seven understory plants:** **brakkel** (fruit), **tumbel** (gourds), **sarquin** (sugar),
**phorrik** (spores), **wollick** (tuber), **maddrick** (the trap), **illurin** (the only light).
**All seven are now sight-blocking**, per his ruling that the ground cover must be tall and broad
enough that a colonist cannot see over or past it — §3d.

**Names:** all 21 coined here and **verified unused** — Wookieepedia search returned zero hits on
every one, and zero matches in our own `src/`. Row 22's `greatbole` is deliberately **not** new: it is
our own existing word for the species, and it was canon-checked too (no hits). §3g records both.

**Art:** 4 existing subjects transfer; **18 rows owe art**, the greatbole among them at the largest
canvas on the page. All four transferring subjects are **256×256 and under-resolved** against the
canvas law — see §3f.

## 1. The rulings being served

Three, all 2026-09-22, all verbatim.

1. **The roster exists at all.** *"Absolutely not. We should have wild jungle trees with bizarre
   Starwars names. And lots of them, a diversity of perhaps ten types of trees at least. Plus the
   signature huge tree."* — rejecting `Plant_TreeOak` 2.0 and `Plant_TreePoplar` 1.2 under a
   `World/Biomes/TropicalRainforest` texture.
2. **It is ours, invented, no canon** — the ruling quoted at the top of this page, which also
   supplies the silhouette brief.
3. **It is choked, and reward and hazard are the same object** (`GREENTIDE_BIOME_DENSITY_1`):
   *"most are useful, many are dangerous. There should be virtually no squares uncovered by lush
   foliage. Choked with foliage. Immediately intimidating to hack through, movement extremely
   difficult."*

And the ownership question was ruled earlier on `TREE_GRAPHICS_OWNERSHIP_1` — *"we should simply
generate our own tree graphics at the scales we want"* — so these are ours, not more donor rows.
Not re-asked.

## 2. What the design must satisfy

Constraints taken as given, not re-litigated:

1. **Tier.** Every name here is invented, so no name is Star Wars IP, so **the whole roster is
   `RM_` tier** and belongs in `RM_Greentide`'s own `wildPlants`. ✅ MEASURED 2026-09-22:
   `src/RimMandrake/Greentide/Defs/BiomeDefs/RM_Greentide_Biome.xml` carries **no GENERATED
   header** and `design/Jawa/mods/biome_flora.py` contains **no reference to `RM_Greentide`** — its
   outputs are all under `src/RimUtinni/UtinniPatches/`. ⇒ that file is hand-owned and the roster
   lands in it directly. ⚠️ The **campaign twin is different**: `biome_flora.py` line 144 owns a
   `RUT_Greentide` entry, so rows reaching the campaign biome must go through that generator (or a
   separate hand-owned patch it does not own) — **never a hand edit of `BiomeFlora_Ashkarr.xml`**.
   §6 carries this.
2. **Adding our own invented flora to `RM_Greentide` is not "enriching the generic def."** The item's
   Watch-out forbids copying the *campaign* twin's body into the generic def — Star Wars content
   crossing the tier line. Franchise-free flora of ours is the generic def's whole intended
   substance, and after this ruling it is the *only* place the roster can live.
3. **Fire.** Owner, 2026-09-22: *"Fire will harm and burn things, but no they do not catch fire
   themselves, just take damage."* §5 states this as a roster-wide property and flags what needs
   measuring, because it is **not** obviously expressible as a single `Flammability` number.
4. **Three fellers, one fall** (`the_greentide.md` §4, §7b). Every tree is subject to being *gnawed
   from below, cracked from within, or shouldered over from the side*. Each row below declares
   whether it falls and how big the fall is. `RM_FellableTreeExtension` + `CompProperties_CrackFall`
   are the wiring, and **MEASURED 2026-09-22 they are def-agnostic** — `RM_TreeFallUtility.cs:67`
   reads `GetModExtension<RM_FellableTreeExtension>() ?? Default`, whose own comment says *"Used for
   any Plant with no RM_FellableTreeExtension of its own."* ⇒ only rows wanting non-default fall
   behaviour need an extension block. Nobody should author fourteen.
5. **The wood economy has two grades** (§7). **Greenwood** — *"not quality hardwood but burnable and
   buildable... a major resource"* — off ordinary fallen trees in bulk. **True hardwood** *"only
   from the heart of fallen giants."* A roster of fourteen has to keep that gap legible, so most
   rows drop greenwood only and hardwood is restricted to one row plus the Greatbole.
6. **The canopy has to be a real place.** §4's Swingers *"cross above the river"*; §4c's underlight
   rain *"condenses on the canopy and drips forever"*; §8b's causeways are *"the giants' roots …
   the roads."* Hence genuine strata, not fourteen trees at one height.
7. **No vanilla-Earth flora names** (§6 ban 2). Terrestrial-analog *shapes* are fine; Earth *names*
   are not — "mangrove", "palm", "fern", "willow", "oak" are banned as labels even where the
   silhouette is right. The brief's word *"willow-like"* is a description of a form, and it is
   rendered here as **mourvel**, not as a willow.
8. **A rooted ambusher hides among these plants.** `HOSTILE_MOBILE_PLANTS_1` is approved and is
   **animal** content — ⛔ nothing on this page is one, and none is designed here. But two rows
   exist partly to give it cover: **kaddrath**'s walk-through root gaps and **mourvel**'s curtain,
   which is why both are described as concealment as well as scenery.

## 3. The roster

`cells` is the visual footprint in the project's own "N cells wide" convention, not a multi-cell
`size`. All rows are intended `ParentName="TreeBase"`, single-tile footprint, oversized sprite — the
idiom `RUT_SweetlineTree` and `RUT_GreatboleCore` already established here. ⚠️ Every field beyond
that is **UNMEASURED** from this machine; §8.

### 3a0. The fellable giant — one tree, above the whole ladder

Ruled in **after** the 21 rows below were proposed, which is why it is numbered 22 and not 1 —
⛔ the other rows are cited by number in §3f and §6 and must not be renumbered.

| # | defName | label | silhouette FORM | what it looks like | cells · falls | job | art |
|---|---|---|---|---|---|---|---|
| 22 | `RM_Greatbole` | greatbole | **colossal fluted column under a raft of leaves** | A single grey-brown column so broad at the base that its fluting reads as separate trunks fused together, rising far past every other crown before opening into one horizontal raft of paddle leaves — the same leaf as `RUT_GreatboleCore`'s, at the same proportions, on a tree a third its age. Bark in long vertical plates that shed. Nothing grows in its shadow, so it stands in a clearing of its own making. | **16** · yes — and the fall is the largest event on the map | 🔑 **The hardwood jackpot.** `the_greentide.md:214`'s ladder — *normal trees (fall) → giants (crack, fall, hardwood jackpot)* — ends here, and this is the only tree that pays true hardwood by being felled. Also what `RM_FellableTreeExtension` / `CompProperties_CrackFall` were built for. | **OWED** — and it is the largest canvas on the page |

**Why 16.** Veluthar is 10 and is the largest *ordinary* tree. A giant one rung up reads as a big
canopy tree, not as a different class of object, so 16 puts it 60% above the canopy — far enough that
it is unmistakable at a glance, which is what *"well past 10"* asked for. ⚠️ **The cost, stated:** at
the project's `128 px/cell` canvas law that is a **2048²** sprite, twice veluthar's 1280² in each
dimension. That is a real art-pipeline constraint and it is flagged rather than assumed — if 2048² is
not renderable, the number moves, not the ruling.

🔑 **Same species, different life stage — and that must be legible without text.** His ruling makes the
landmark what a greatbole becomes after centuries. ⇒ **They share a visual family by construction:
same leaf, same bark plating, same fluting, different scale.** ⛔ Do not design them as two species
that happen to be big.

⚠️ **The stated cost he accepted:** the game will not simulate that growth, so an attentive player may
wonder why none of their greatboles ever becomes a landmark. ⛔ Do not build a growth path to fix it —
the relationship is fiction, and the description carrying it *is* the implementation.

🔴 **A tier problem this creates, flagged not decided.** `RM_Greatbole` is franchise-free tier, but the
ancient form it grows into is `RUT_GreatboleCore` — **campaign tier only**. ⇒ A player of the free mod
gets the mature giant and can never encounter the landmark, so the life-stage fiction has no payoff
for them. That contradicts the 2026-09-22 tier ruling that the free mod *"will look precisely the same
as the star wars enhanced one save for any star wars beasts"* — and "greatbole" is an invented name, so
nothing about the landmark is IP that requires it to stay in the campaign layer. ⇒ Owed: either the
landmark moves to `RM_` tier or the free mod gets its own. Neither is mine to choose.

### 3a. Canopy / emergent — four trees. The fall is a map event.

| # | defName | label | silhouette FORM | what it looks like | cells · falls | job | art |
|---|---|---|---|---|---|---|---|
| 1 | `RM_Veluthar` | veluthar | **broad-leaf umbrella** | A bare grey column for most of its height, then one single tier of enormous paddle leaves radiating flat from the very top like an opened umbrella — no crown mass below it at all. Deep green above; the undersides pale and permanently wet, because §4c's underlight rain drips off it. | 10 · yes, the biggest ordinary fall | **The dominant canopy tree and the Swingers' road.** Bulk greenwood. The one row that reads as *ceiling*. | **EXISTS — `artpipe/done/jungletree_v1.json`** 🔴 256², under-resolved (§3f) |
| 2 | `RM_Mourvel` | mourvel | **weeping curtain** | The brief's *"willow-like canopy"* taken literally and then further: a low wide dome whose entire outer surface is hanging cord-like leaf strands that reach the mud, so the tree is a **room with walls**. Bark violet-black; the strands blue-green. Nothing is visible through it. | 8 · yes | **The concealment tree.** You cannot see into or out of one. Leaf-cords are cordage. This is where a rooted ambusher is not visible until you are inside the curtain. | **OWED** |
| 3 | `RM_Kaddrath` | kaddrath | **buttress tripod / arcade** | Roots first, tree second. Wide-splayed above-ground root buttresses taller than a pawn, with walk-through gaps between them; the trunk is shorter than the root mass is wide, and the crown is modest plates of olive leaf. Reads as **architecture**. | 9 · yes, but the root arcade survives the fall | **The Boughway generator** — §8b's *"the giants' roots are the roads."* Its roots are the causeway, not decoration. Its gaps are also the best hiding place on the map. | **OWED** |
| 4 | `RM_Sarnstilt` | sarnstilt | **stilt tripod over water** | Stands *in* the channel on a tripod of prop roots, trunk starting clear of the surface, crown leaning hard out over the water and shedding huge single leaves onto it. Bark salt-crusted pale on the downstream rows. | 7 · yes, and it falls **across** the channel | River-margin only. §4's Lungers wait in the shade beneath it — **this is the tree that makes crossing water frightening.** Its salt-cured timber is the good boat wood. | **OWED** |

### 3b. Mid-storey — six trees. The working forest, and where greenwood comes from.

| # | defName | label | silhouette FORM | what it looks like | cells · falls | job | art |
|---|---|---|---|---|---|---|---|
| 5 | `RM_Brunnock` | brunnock | **squat heavy dome** | Visibly *heavy*: a trunk far too thick for its height under a tight low dome of black-green leathery leaves the size of a shield, overlapping like armour plate. Short internodes, tight grain through cracked near-black bark. Nothing about it looks fast. | 6 · yes, hardest and slowest | **The only true hardwood besides the Greatbole.** Slowest `growDays` on the page, highest `MaxHitPoints`, deliberately scarce. Felling one is a project. | **OWED** |
| 6 | `RM_Ghemmel` | ghemmel | **gnarled rounded crown** | The ordinary one, and the roster needs one: gnarled wind-bent trunk, dense rounded crown of medium dark leaves. Its distinguishing feature is not shape but **blood** — the bark bleeds thick red wherever it is cut or split, and in this biome it is split everywhere. | 6 · yes | **The commons.** Commonest mid tree, bulk greenwood, and the source of §7's red dye / lacquer / waterproofing line. The safe row — most of the harvest economy's floor. | **EXISTS — `artpipe/done/hydenocktree_v1.json`** (6 cells, matches) 🔴 256² |
| 7 | `RM_Nemmer` | nemmer | **sparse drooping fronds** | Slender pale smooth trunk, deliberately *thin* crown — a few long drooping fronds rather than a mass — and fruit far too large for the branch holding it, hanging low enough to take from the ground. The lightest silhouette on the page, by design, so it reads against its neighbours. | 5 · yes, easily | **§4's *"the fruit yearns to be eaten"* row.** Free calories with a tax: the fruit-fall draws everything that eats fruit, and then everything that eats *those*. The roster's `harvestedThingDef` tree. | **EXISTS — `artpipe/done/jogantree_v1.json`** (5 cells, *"lighter/sparser silhouette"* — matches exactly) 🔴 256² |
| 8 | `RM_Vurmeloth` | vurmeloth | **tidy narrow ovoid** | Almost suspiciously tidy — a neat narrow crown of even mid-green leaves on a straight clean bole, the one plant here that looks *cultivated*. Unremarkable until cut, when the heartwood is arterial crimson. Grows only in small pure stands, never mixed in. | 5 · yes | **The export.** Not a bulk wood — a premium timber the Jawa caravans carry out at a markup. Very low commonality, tight clustering. | **OWED** |
| 9 | `RM_Mirrelbole` | mirrelbole | **split bleeding column** | Trunk visibly **split down its own length** by the speed it grew, the wounds glazed with amber resin that never sets in the humidity. Sheds bark plates. Permanently wet-looking, and the mud at its foot is sticky. Crown thin and ragged — all the growth went into the trunk. | 4 · yes, **highest crack-fall rate on the page** | **The sap tap** — §7's *"rendered chemfuel, the dayside's fuel economy."* 🔑 Reward and hazard are the same object: the tree you tap is the tree most likely to crack and come down on the pawn tapping it. | **OWED** |
| 10 | `RM_Zhorrel` | zhorrel | **hanging tentacle curtain, no crown** | No crown at all. A low crossbeam of branches with a hanging curtain of slack finger-thick tentacle-leaves, red-barked above. The tentacles are visibly **not still** — the tell is that they move against the wind rather than with it. | 5 · yes | **The strangler.** §6 ban 1 (*"no truce, ever"*) made literal. Under the Roil you meet it at chest height without having seen it. Kill one and the tentacles are excellent cordage. | **OWED** |

### 3c. Understory — four trees. Under the Roil, where the floor is hidden.

| # | defName | label | silhouette FORM | what it looks like | cells · falls | job | art |
|---|---|---|---|---|---|---|---|
| 11 | `RM_Quathis` | quathis | **single flat fan** | One flat vertical fan of gigantic leaves, all in a single plane from a short thick base — so it reads as a **wide bright blade from one side and a line from the other**, the only row on the page whose silhouette changes with facing. Bright lime, translucent at the edges. | 4 · no, it is cut not felled | Its leaves are single-piece roofing and thatch panels — the biome's cheapest building material. Safe. The colour relief in a dark understory. | **OWED** |
| 12 | `RM_Thalquith` | thalquith | **flat interlocking lattice** | **Aquamarine — the only non-green thing growing here.** Smooth trunk with no bark texture at all, and branches that meet overhead in a flat interlocking lattice rather than a crown. Saplings are literal inverted cones. The lattice **hums** in moving air. | 4 · yes, and the lattice shatters | **The strange one, and a warning system.** Its hum is constant; the hum *stopping* is the tell, which is how it meets §9's *"its scariest signal is silence."* Fragile: hard to keep alive near work. The grove behaviour is real and lives on `GREENTIDE_HUMMING_GROVE_1`, settled as a generic camera-relative hum. | **OWED** |
| 13 | `RM_Cundral` | cundral | **skirt of runners under a squat bole** | A squat woody base almost buried under a skirt of tentacle-thick ground runners, with translucent pods hanging among them like fruit you must not pick — you can see the acid moving inside them. | 2 · no | 🔑 **Reward and hazard are the same object, most explicitly on the page.** Left undisturbed it lets you dig its root, a real food staple. Damaged, the pods go. | **OWED** |
| 14 | `RM_Gorbeleth` | gorbeleth | **barrel with an upward throat** | A low mottled purple-brown barrel of a trunk with one upward-facing muscular throat at the top, ringed with tooth-like bracts. It twitches toward movement. Nothing else about it suggests a plant. | 3 · no | The understory's ranged hazard. Its toxin is worth extracting, which means going close. Pairs naturally with the jungle rancor content already in `src/`. | **OWED** |

### 3d. The seven understory plants — the non-tree rows, also ours

These replace the seven borrowed non-tree rows the owner put in scope (*"We work on drafting the
replacements for everything right now. No reason to wait!"*). Same treatment: invented, `RM_` tier.
⚠️ These are `Plant` defs, **not** trees and **not** `HOSTILE_MOBILE_PLANTS_1` creatures — even
`maddrick`, which is a static trap, never a mobile one.

🔴 **All seven block sight — owner ruling, 2026-09-22.** The bar he set is functional, not a number:
**tall and broad enough that a colonist cannot see over or past them.** ⇒ That is the mechanism behind
the whole biome — a hidden floor is what lets `HOSTILE_MOBILE_PLANTS_1`'s rooted ambushers genuinely
hide, and what makes *"choked with foliage"* real at ground level instead of decorative.

⚠️ **Four of these rows were originally written as deliberately LOW** — brakkel *"knee-high"*, tumbel
*"no vertical presence at all"*, wollick *"pressed to the mud"*, illurin *"a broad low cap"*. Those
descriptions predate the ruling and contradict it, so **they are rewritten below rather than left to be
read as still current.** Every row's *job* is unchanged; only its height is. ⇒ Two side effects worth
seeing: tumbel is no longer a floor texture (it still reads from a distance — better, in fact), and
wollick is no longer the literal illustration of *"no square uncovered"*, a role the mass of all seven
now carries between them.

| # | defName | label | replaces the role of | silhouette FORM | what it looks like | cells | job |
|---|---|---|---|---|---|---|---|
| 15 | `RM_Brakkel` | brakkel | a fruit bush | **overlapping leaf mound, over head height** | A mound of enormous overlapping paddle leaves standing taller than a pawn, with the fruit clustered *underneath* in the dark — you have to push into it to see whether there is anything there, and to see what else is in there with you. | 4 | The forageable staple. Replaces the biome's `foragedFood` `RawBerries`, ruled 2026-09-22 — ⚠️ so its nutrition and value now matter where a stock berry's did not; set them deliberately. |
| 16 | `RM_Tumbel` | tumbel | a gourd plant | **arching runner on standing props** | A thick runner arching up on woody props well above pawn height, carrying heavy hollow vessels slung along its length, each the size of a crate, dull and leathery-skinned. You walk *under* it and cannot see out through the vessels. | 5 | Food plus containers: the hollow shells are cut into vessels. Still the waypoint-marker plant — a raised one is visible from further away than a flat one was. |
| 17 | `RM_Sarquin` | sarquin | a sugar-producing plant | **whorl with hanging drip-tentacles** | A thick fleshy central whorl at chest height with long hanging tentacle-leaves falling from above it, dripping clear sweet sap continuously, each drip-point glazed and crusted. The curtain of strands is what blocks the view; the mud beneath is sugared and crawling. | 4 | The sugar source. 🔑 Reward and hazard together: the drip is why insects are there, and the insects are why something bigger is. |
| 18 | `RM_Phorrik` | phorrik | a spore plant | **thicket of taut bladders on stalks** | A dense thicket of taut translucent bladders held at head height on springy stalks, each visibly over-full. You cannot see through the mass of them, and pushing through bursts them. | 3 | Hazard-with-payoff: the spores are medicinal, and walking through a patch fills the air. Interacts directly with movement cost — a patch you go around. |
| 19 | `RM_Wollick` | wollick | a root plant | **upright rosette of blade leaves** | A rosette of huge leaves standing upright rather than lying flat, each a blade taller than a pawn, fanning out over a deep starchy tuber. From inside a patch you can see nothing but leaf. | 4 | Bulk carbohydrate. Digging it slumps the churnmud around it, which is a small honest cost rather than a hazard. |
| 20 | `RM_Maddrick` | maddrick | a trap plant | **inward-curling blade ring** | A ring of inward-curling leaf blades standing shoulder-high, waxy and wet, around a throat of standing fluid you cannot see into until you are at its lip. It closes on what steps in. Completely static — it does not move toward anything. | 3 | Pure hazard, with a use: a patch of maddrick is a free perimeter. Something for the player to build *around* rather than clear. |
| 21 | `RM_Illurin` | illurin | a glowing understory plant | **broad glowing cap on a tall stem** | A broad fleshy cap held above pawn height on a thick stem, glowing cyan-green from its underside down onto the mud — so it lights the ground beneath it and blocks the view across. | 7 | **The only light under the canopy.** Suppresses nothing, reveals everything within its small radius. Without it the understory is unreadable. **Art EXISTS — `artpipe/done/felucianglowspore_v1.json`** (*"7 wide"* — which is why this row is 7 and not smaller) 🔴 256², §3f. |

🔴 **How a plant blocks sight in this engine is UNMEASURED and must not be guessed.** Plant cover and
line-of-sight involve `fillPercent` and cover mechanics; ⛔ do not name a field or a value from
reasoning. ⚠️ And the **side effects are owed testing before these seven ship**: sight-blocking growth
interacts with shooting, with pathing, and with the player's ability to see their own colonists. A
biome the player cannot read is a different failure from a biome that is dangerous.

**Art on the other six:** all **OWED**. Nothing in `artpipe/done/` keys to a non-tree Greentide
flora row (§3f is the full measurement).

### 3e. The legibility matrix — the acceptance test for this roster

🔑 **This is the section to judge the roster by.** Because virtually no square is uncovered, a
player parses the Greentide by **form first and colour second** — so no two rows may share both.
Twenty-two rows, twenty-two forms:

| form | rows | reads as |
|---|---|---|
| colossal fluted column under a leaf raft | greatbole | a building that is alive |
| broad-leaf umbrella | veluthar | a ceiling on a pole |
| weeping curtain to the ground | mourvel | a walled room |
| buttress arcade | kaddrath | architecture |
| stilt tripod over water | sarnstilt | a bridge pier |
| squat heavy dome | brunnock | armour |
| gnarled rounded crown | ghemmel | an ordinary tree — the baseline the others read against |
| sparse drooping fronds | nemmer | almost bare, deliberately light |
| tidy narrow ovoid | vurmeloth | cultivated, out of place |
| split bleeding column | mirrelbole | a wound |
| hanging tentacle curtain, no crown | zhorrel | a bead curtain that moves |
| single flat fan | quathis | a blade — and a line edge-on |
| flat interlocking lattice | thalquith | a ceiling grid |
| skirt of runners | cundral | a heap |
| barrel with an upward throat | gorbeleth | a mouth |
| overlapping leaf mound, over head height | brakkel | a thicket you push into |
| arching runner on standing props | tumbel | a loaded rack you walk under |
| whorl with hanging drip-tentacles | sarquin | a chandelier |
| thicket of taut bladders on stalks | phorrik | eggs at head height |
| upright rosette of blade leaves | wollick | a stand of blades |
| inward-curling blade ring | maddrick | a trap, and it looks like one |
| broad glowing cap on a tall stem | illurin | a lamp on a post |

**Colour is the second axis, and it is spent deliberately** — only three rows are not green, so each
one carries weight instead of cancelling the others out:

- **thalquith — aquamarine.** The only genuinely non-green growing thing. It is the landmark.
- **mourvel — violet-black bark** under blue-green strands. A dark mass in a bright biome.
- **quathis — bright lime, translucent.** The one light-emitting-looking leaf that is not illurin.
- Everything else is green, differing in *value* (near-black brunnock → pale wet veluthar
  undersides) rather than hue. Hue restraint is what keeps three exceptions readable.

⚠️ **This cannot be signed off from a table.** Per the standing rule, density-and-legibility is a
LOOK-AT-IT judgement: build one map with all 22 rows on it, save the game, and give him a grid key.
🔴 **And the seven sight-blockers make that review mandatory rather than advisable** — a map where the
ground cover blocks line of sight is exactly the map a table cannot predict.
`GREENTIDE_BIOME_DENSITY_1`'s own Watch-out says the same thing.

### 3f. Art — MEASURED 2026-09-22, and the transfer is honest but small

**Four subjects key to this biome (or to the Fever Wood, a sibling jungle) and transfer.** Each was
read from its own `infrastructure/artpipe/done/<id>.json` this session. 🔑 **The transfer is sound
for a reason worth stating:** every one of the four carries `style_notes` beginning *"Non-SW name,
general kind … fixed, flavor free"* — they were deliberately generated as **generic, non-Star-Wars
jungle forms**, so serving an invented def is what they were built for, not a repurposing.

| subject | its own source row | declared size | canvas on disk | assigned to | why it fits |
|---|---|---|---|---|---|
| `jungletree_v1` | `flora:the_greentide:AB_JungleTree` | large, *"10 cells wide"* | **256²** | **row 1, veluthar** | Largest declared tree subject; matches veluthar's 10 cells. ⚠️ colour caveat below. |
| `hydenocktree_v1` | `flora:the_fever_wood:Plant_HydenockTree_Wild` | medium, *"6 cells wide"* | **256²** | **row 6, ghemmel** | Exact cell match, and ghemmel is deliberately the *ordinary* crown — what a generic jungle tree renders as. |
| `jogantree_v1` | `flora:the_fever_wood:Plant_JoganTree_Wild` | medium, *"5 cells wide"* | **256²** | **row 7, nemmer** | Exact cell match, and its notes say *"distinguished … by a lighter/sparser silhouette"* — which **is** nemmer's brief. |
| `felucianglowspore_v1` | `flora:the_greentide:Plant_FelucianGlowspore_Wild` | large, *"7 wide"* | **256²** | **row 21, illurin** | The only glowing subject; glowing low cap is illurin's whole job. |

🔴 **All four are UNDER-RESOLVED, and this is a carried-forward known defect.** The project's canvas
law is `128 px/cell × cells`; all four rendered at **256×256**. `alientree_v2.json` is the worked
precedent for exactly this correction — it records that `alientree_v1` *"shipped at 256×256 because
drawsize_backfill.json's 'alientree' stem was wrongly resolved"* and was re-rendered at **1024²**
for a 5-cell tree under `FLORA_LEGIBILITY_BAR_1`. **That fix was never applied to these four.** Owed
re-renders, cheap because the concept is already approved:

| row | subject | owed canvas |
|---|---|---|
| veluthar | `jungletree_v2` | **1280²** (10 cells) |
| illurin | `felucianglowspore_v2` | **896²** (7 cells) |
| ghemmel | `hydenocktree_v2` | **768²** (6 cells) |
| nemmer | `jogantree_v2` | **640²** (5 cells) |

⚠️ **One colour caveat, stated rather than hidden.** `jungletree_v1` is a generic large jungle tree
and no PNG for it was located from this machine (`_artsrc/` holds none of the four, and
`registry.jsonl` has zero entries for these ids). So **whether the render actually resembles
veluthar's bare-column-plus-flat-umbrella form is UNVERIFIED** — the assignment is made on declared
size and kind only. veluthar was written green-and-neutral precisely so a generic jungle tree can
serve it; if the render turns out to be an ordinary round crown, the honest answer is to swap
veluthar and ghemmel's art and re-render, not to rewrite veluthar's silhouette. Decide by looking at
the PNG on the Desktop.

**⛔ Nothing is commissioned here.** 18 of 22 rows owe art — the 17 measured this session, plus
`RM_Greatbole`, which was ruled in afterwards and is the **largest canvas on the page** (2048² at
16 cells, §3a0). ⚠️ The greatbole's art has a constraint none of the others has: it must share leaf,
bark and fluting with `RUT_GreatboleCore` so the life-stage claim reads without text, so it should be
generated **against that existing landmark's art as reference**, not from the brief alone. Per the
standing check-before-queuing rule, `artpipe/done/`, `_artsrc/` and `registry.jsonl` were all searched
for every one of the other 17 subjects before saying so — and the answer came back negative, so there is no already-ruled art
being thrown away. ~14 other tree/fern subjects in `done/` belong to **other biomes** (the
Contagion, Miasma, Slime, Forge, Rot, Webwork, Lantern Deeps, Cracked Lands, Weeping Stones) and are
**not free**; the full table of who owns what is in Appendix B.

### 3g. The names — verified unused, 2026-09-22

🔴 **Every one of the 21 coined names was checked**, because the previous pass shipped a row
claiming canon (`felucian glowspore`) that turned out to be a donor mod author's invention. Method:
the Wookieepedia search API, per row —

```
curl -s -m 20 -G "https://starwars.fandom.com/api.php" --data-urlencode "action=query" \
  --data-urlencode "list=search" --data-urlencode "srsearch=<name>" \
  --data-urlencode "srlimit=3" --data-urlencode "format=json"
```

⚠️ **A gotcha for whoever repeats this:** on zero results the API returns
`{"query":{"search":[]}}` with **no `searchinfo` key at all**, so a parser that reads
`searchinfo.totalhits` raises on exactly the case you care about and can be misread as an error
rather than a clean pass. Read the **`search` array's emptiness**, not the hit count.

**Result: NO HITS on all 21** — veluthar, mourvel, kaddrath, sarnstilt, brunnock, ghemmel, nemmer,
vurmeloth, mirrelbole, zhorrel, quathis, thalquith, cundral, gorbeleth, brakkel, tumbel, sarquin,
phorrik, wollick, maddrick, illurin.

**Row 22, `RM_Greatbole`, is different and its provenance is stated separately.** It is **not** newly
coined — "greatbole" is existing project vocabulary, MEASURED in **20 files** under `src/` including
`RUT_GreatboleCore.xml` and `RUT_GreatboleHeartwood.xml`, which is the point: the fellable giant and
the landmark are the same species and must share the word. The exact defName `RM_Greatbole` returned
**zero matches** in `src/`, so it is free to take.

🔑 **It needed the canon check anyway, for a reason specific to it:** the name was previously
campaign-tier only, and putting it in `RM_` tier makes its IP status matter where it did not before.
**MEASURED 2026-09-23 by the method above: `greatbole` → NO HITS.** (The bare word `bole` returns hits,
but only unrelated pages — `Bolle bol`, Shyriiwook — matching on substring, which is the fuzzy-hit
behaviour this section already documents. `bole` is an ordinary English word for a tree trunk, not a
plant name, so §6's Earth-name ban does not reach it.)

**Two candidates were rejected and replaced** on fuzzy hits, which is the check doing its job:
`haddrel` → matched *Halidrell Setsyn* (replaced by **ghemmel**); `drennok` → matched *Dranok*
(replaced by **wollick**). Also cleared but unused, available if a row is added or renamed:
`tarrowan`, `calloch`, `bhorrun`, `vessquith`.

**And no collision with our own content:** a case-insensitive grep for all 21 names across `src/`
returned **zero matches**.

## 4. Two giants, and they differ by life stage

🔴 **The SIGNATURE giant is the one ALREADY BUILT** — a structure def, not a plant, which cannot be
felled. MEASURED 2026-09-22 from our own files:

- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_GreatboleCore.xml` —
  `ParentName="BuildingBase"`, label `greatbole core`, `size (1,1)`, `passability Impassable`,
  `fillPercent 1.0`, `deconstructible false`. Placed by
  `RUT_Greentide_LivingBolesGenStep`, with `RUT_GreatboleHeartwood` and `RUT_ToxinSealant` around it.
  It is in no `wildPlants` list and it does not fall.

🔴 **And a FELLABLE giant exists too — `RM_Greatbole`, row 22, §3a0.** Choosing a non-fellable
landmark had silently removed the rung premium hardwood came from: `the_greentide.md:199` says *"True
hardwood — only from the heart of fallen giants"* and `:214` runs the ladder *normal trees (fall) →
giants (crack, fall, hardwood jackpot)*. Put to him as a card, he ruled **keep a fellable giant too**
— the landmark stays the thing you mine, and a separate huge tree also comes down.

⛔ **Their roles must stay visibly distinct** — one is a landmark you mine into, one is a tree that
falls — or they read as redundant. The thing that makes them one species rather than two is scale and
shared art, not overlapping function.

### 4a. What that changes for the roster — it gets *more* important, not less

The canopy rows are now **ordinary fellable trees**, and they are the point: MEASURED 2026-09-22,
the tree-felling machinery is currently proven against **a placeholder only**.
`RUT_Placeholder_GreentideGiantTree.xml` is a `ParentName="TreeBase"` stub whose own header says it
exists *"only so `RM_TreeFallUtility` / `RM_CompCrackFall` / `RM_FellableTreeExtension` are provably
wired"* and that it is *"NOT the real roster giant."* ⇒ **these canopy rows are what finally give
that mechanism real content.**

Recommended assignment of the extension, carrying the placeholder's values forward as a **starting
point, not a tuned baseline** (its own header calls them INVENTED):

- **`RM_Greatbole`** takes the giant-fall extension (`fellLength` ~16, `hardwoodDef`) — the largest
  fall on the map and the **only** source of true hardwood by felling. ✅ This is what closes Q1.
- **veluthar** takes the big-fall extension (`fellLength` ~10, `greenwoodDef`) — the largest
  *ordinary* fall.
- **brunnock** stays the slow, scarce, hard mid-storey row, but it is **no longer the hardwood
  route** — it pays bulk greenwood at the highest hit points on the page. ⛔ Do not give it
  `hardwoodDef`; that was a workaround for a gap the fellable giant has since filled.
- **mirrelbole** takes `CompProperties_CrackFall` at the highest rate on the page.
- **Everything else takes nothing.** The `Default` extension covers them (§2.4). ⛔ Do not author
  fourteen extension blocks.

### 4b. Two defects in the placeholder to fix when it is retired, not inherit

1. 🔴 **`MayRequire="mandrake.rm.environmentalhazards"` sits on the whole `ThingDef`** (line 48,
   MEASURED). A real roster tree gated that way **vanishes from the biome** for a player without
   that mod. Gate only the `modExtensions`/`comps` entries, as `RUT_GreatboleCore` already does with
   `<li MayRequire=...>`.
2. ⚠️ **`<Flammability>0.5</Flammability>`** (line 59, MEASURED). See §5 — under the new fire ruling
   this number is the wrong shape of answer entirely, not merely too high.

**Retiring it** is small: MEASURED 2026-09-22 it appears in exactly three places — its own file and
two C# doc comments (`RM_FellableTreeExtension.cs`, `RM_CompCrackFall.cs`). It is in no BiomeDef's
`wildPlants`. So: put the extensions on veluthar/brunnock/mirrelbole, **delete the placeholder file
outright** per the repo's delete-don't-supersede law, and update the two doc comments to name a real
def.

## 5. Fire — the roster-wide property, and what still needs measuring

**Owner, 2026-09-22, verbatim:** *"Fire will harm and burn things, but no they do not catch fire
themselves, just take damage."*

⇒ **Roster-wide property, all 22 rows:** fire **damages** these plants and can destroy them; they
are **not ignition sources**, they do not sustain a burn, and they do not propagate fire to
neighbours. A dropped incendiary in the Greentide leaves a scorched hole, not a burning jungle.

This is the biome's existing design, tightened. `the_greentide.md` §6 hard ban 3 reads *"No
high-Flammability native flora — saturated growth does not burn; a flammable Greentide plant def is
a violation"*, and §4b makes it load-bearing: *"Fire is not the tool"*, precisely so the dry-air
blower stays the answer. His ruling supplies the number-free version of that ban and extends it from
"not very flammable" to **"not flammable at all, but still destructible by fire."**

🔴 **The exact field and value are UNMEASURED and must be confirmed on the Windows machine.** Do not
take a number from this page. Specifically:

- **Whether a single `Flammability` value can express this at all is genuinely unknown from here.**
  In RimWorld `Flammability` governs *ignition*, and the two halves of his ruling may not both hang
  off it: a value low enough to prevent ignition may also prevent fire from damaging the plant,
  which would break the first half of the sentence. If so this needs a comp or a patch, not a stat
  edit — ⛔ and shipping `Flammability 0` on the assumption it means "takes damage, does not ignite"
  is the silent-wrong-answer failure mode.
- **`TreeBase`'s default `Flammability`** — UNMEASURED. There is no def dump, no vanilla def and no
  decompiler on this machine.
- Datapoints from our own files only: the placeholder giant carries **0.5**; `RUT_SweetlineTree` was
  cut to **0.1** under the arid shrubland's analogous ban.

⇒ **Nothing here asks him anything about fire** — he already ruled it. The open work is a measurement on the
Desktop, not a question for him.

## 6. Wiring, and the commonalities

### 6a. Where the roster lands

**The generic biome takes it directly.** MEASURED: `RM_Greentide_Biome.xml` has no GENERATED header
and `biome_flora.py` never names `RM_Greentide`. Today its `wildPlants` is six vanilla temperate
rows (`Plant_TreeOak` 2.0, `Plant_TreePoplar` 1.2, `Plant_Bush` 1.5, `Plant_Grass` 2.0,
`Plant_TallGrass` 1.0, `Plant_Berry` 0.6) — the list the owner rejected. The 22 rows replace the two
trees and the bush outright; whether the three grass rows survive as ground filler is a small
decision for the build seat, not a card.

🔴 **The campaign twin is generator-owned and must NOT be hand-edited.** `biome_flora.py` carries a
`RUT_Greentide` entry (line 144) and writes into `src/RimUtinni/UtinniPatches/`;
`BiomeFlora_Ashkarr.xml`'s own header says *"GENERATED … do not hand-edit."* ⇒ rows reaching the
campaign biome go through that generator's pool, or through a separate hand-owned patch file the
generator does not own. `TREE_GRAPHICS_OWNERSHIP_1` already hit this once.

Notes that apply to any patch route, from `WildAnimals_Greentide.xml`'s own header:

- **Shorthand form only** — `<DefName>commonality</DefName>`. `<li><plant>` children read as empty;
  the item records this costing a contradictory measurement.
- **Ours carry no `MayRequire`.** A `MayRequire` on our own def silently loses the row for a player
  without that mod.
- **A patch that matches nothing logs nothing.** A clean `validate_patch.py` is not proof a row landed.
- ⚠️ A `<li>` in the wrong place discards the **whole def**, silently.

### 6b. Proposed commonalities — relative weights, not a density figure

⛔ **Density is not expressed here.** `GREENTIDE_BIOME_DENSITY_1` rules it explicitly: *"Do not
express density by inflating `wildPlants` commonalities. Those are relative weights; raising them
all changes nothing about total coverage."* The *"virtually no squares uncovered"* ruling is a
separate mechanism on that item, and the field governing it is UNMEASURED.

```
canopy      RM_Veluthar   1.60   RM_Kaddrath  1.00   RM_Mourvel   0.80   RM_Sarnstilt 0.70 (river margin)
mid-storey  RM_Ghemmel    1.50   RM_Nemmer    1.20   RM_Mirrelbole 0.90  RM_Zhorrel   0.50
            RM_Brunnock   0.20 (the hardwood — deliberately scarce)      RM_Vurmeloth 0.12 (pure stands)
understory  RM_Quathis    1.30   RM_Illurin   0.90   RM_Cundral   0.50   RM_Thalquith 0.45
            RM_Gorbeleth  0.30
plants      RM_Wollick    1.60   RM_Brakkel   1.20   RM_Phorrik   0.90   RM_Sarquin   0.70
            RM_Tumbel     0.60   RM_Maddrick  0.40
```

Flavour, not a balance pass — the same posture `TREE_GRAPHICS_OWNERSHIP_1` recorded for
`RUT_SweetlineTree`'s stats. Tuning is a live job on the Desktop.

### 6c. The economy ruling, checked against the roster

*"Most are useful, many are dangerous"*, with reward and hazard *"frequently the same object."*

- **Useful: 19 of 21.** Only zhorrel and maddrick exist primarily to hurt you — and both yield
  something (cordage; a free perimeter).
- **Dangerous: 9 of 21** — sarnstilt, mirrelbole, zhorrel, cundral, gorbeleth, sarquin, phorrik,
  maddrick, nemmer.
- **Reward and hazard are literally the same object in 6 rows** — mirrelbole (tap the tree most
  likely to fall on you), cundral (dig the root past the acid pods), nemmer (free fruit that baits
  predators), sarquin (sweet drip that feeds the food chain), gorbeleth (valuable toxin, you must go
  close), phorrik (medicinal spores that you release by treading on them).

✅ **And the foraged yield is ruled** (2026-09-22): `RM_Greentide`'s `foragedFood` moves off the vanilla
`RawBerries` row to **brakkel**. ⚠️ A stock berry's nutrition and value were inherited and invisible;
brakkel's are a deliberate choice and are owed one.

## 7. Nothing on this page is waiting on the owner

The three questions this section used to carry are all answered, so they are removed rather than left
standing with a note. Where each went:

1. **Where true hardwood comes from** — answered by the fellable giant. `RM_Greatbole` (row 22) is the
   only tree that pays true hardwood by falling; brunnock is bulk greenwood. §3a0 and §4a.
2. **Whether thalquith's grove is a real mechanic or flavour** — real, and it moved to its own item,
   `GREENTIDE_HUMMING_GROVE_1`, where the mechanism is settled as a **generic** camera-relative hum
   rather than anything biome-local. ⛔ Do not re-decide it here.
3. **Whether foraged food stops being a vanilla berry** — ruled 2026-09-22: **brakkel replaces
   `RawBerries`.** ⚠️ Its nutrition and value now matter where a stock berry's did not, so set them
   deliberately rather than inheriting.

⇒ 🔴 **What remains is not a question but a measurement**: the fire ruling may not be expressible as a
single `Flammability` value at all (§5, §8.2), and that must be settled against the engine before 21
rows are authored on top of it. It needs the Desktop, not a decision.

## 8. UNMEASURED — needs the Windows machine

Authored on the Mac laptop. No game, no def dump, no `measure`, and RimSage has never connected
here — so the following are genuinely unknown, not merely unchecked.

1. **Every vanilla and donor defName.** ⛔ **This page names none it did not read from our own files.**
   `TreeBase`, `RUT_Greenwood`, `RUT_Hardwood`, `RUT_ToxinSealant`, `RUT_GreatboleHeartwood`,
   `RM_FellableTreeExtension`, `CompProperties_CrackFall`, `RUT_GreatboleCore`,
   `RUT_Greentide_LivingBolesGenStep`, `Plant_TreeOak`/`TreePoplar`/`Bush`/`Grass`/`TallGrass`/`Berry`,
   `RawBerries` and the donor names in Appendix B were all **read from `src/` XML/C# this session**.
   Every other field a real `Plant` ThingDef needs — `harvestedThingDef`, `immatureGraphicPath`,
   `sowTags`, `shadowData`, `visualSizeRange`, `growDays`, `MaxHitPoints` — is **UNMEASURED**. Copy
   them from a live sibling; ⛔ do not take them from this document.
2. **How to express the fire ruling.** §5. The most consequential unknown on the page: whether
   "takes fire damage but never ignites" is one stat, two stats, or a comp.
3. **The field that governs total plant coverage**, and whether *"virtually no squares uncovered"* is
   reachable through density alone. `GREENTIDE_BIOME_DENSITY_1` records that **no `plantDensity`-style
   field is set on `RM_Greentide`** (MEASURED absent) and that naming one from here would be a guess.
4. **What the four donor tree defs actually do.** Their yields, `growDays`, harvest products,
   `visualSizeRange`, comps — all UNMEASURED. 🔴 **This is the only real risk in replacing them:** a
   donor tree with a comp nobody noticed is lost silently. **Dump all four before authoring
   replacements.**
5. **Whether the four reusable art PNGs exist on disk, and at what real resolution.** `done/*.json`
   records a *requested* 256×256; `_artsrc/` holds none of the four and `registry.jsonl` has zero
   entries for these ids. Confirm with `validate_sprite.py --describe` before assuming §3f's work is
   only a re-render — and look at `jungletree_v1` to settle §3f's colour caveat.
6. **Whether `wildPlants` on `RM_Greentide` accepts these defs at all.** A post-load def dump is the
   only proof a row landed.
7. **Whether 22 rows is too many for one map to read.** §3e is a paper argument. This is a
   look-at-it judgement and should ship as a savegame on one map with a grid key.
8. **How much of the movement penalty is mud versus plants.** `RM_GreentideChurnmud` already ships a
   high-`pathCost` mire with an escalating `RM_Mired` hediff. That is *terrain* difficulty; *"hack
   through"* is *vegetation* difficulty. `GREENTIDE_BIOME_DENSITY_1` warns the two stack and the
   biome can become impassable by accident. Nothing on this page sets a path cost.

---

# Appendix A — canon inspiration notes

⛔ **Nothing in this appendix ships, and nothing in it is a claim about anything that does.** No
defName, label, or description on this page derives its authority from a canon source. This appendix
exists for one reason: an earlier pass sourced real Star Wars trees live from Wookieepedia, and the
**silhouettes and economic roles** it surfaced were good enough that the owner said *"You may get
inspired by the star wars versions you found."* This records what inspired what, so the reasoning
behind a row is traceable and nobody re-does the research.

⚠️ **Do not reintroduce any name from this appendix as a row.** The ruling is that Star Wars plant
lore encumbers the mod for no gain.

| canon tree (inspiration only) | the idea taken | invented row it became |
|---|---|---|
| **wroshyr** (Kashyyyk) — tropical giant, sap used *"to produce fuel, oils, and chemicals"*, settlements built *inside* the tree | tapping a tree for the fuel economy; living inside a tree | the sap economy went to **mirrelbole**; living-inside stays with the already-built Greatbole, which is not a plant |
| **massassi** (Yavin 4) — *"purple-barked giant trees … habitat of various animal species"* | a non-green trunk as the canopy's visual anchor; canopy as animal habitat | **mourvel**'s violet-black bark; the canopy-as-road job went to **veluthar** |
| **brylark** — *"wood as strong as metal"* | one scarce tree that is the hardwood, worth a project to fell | **brunnock** |
| **gnarltree** (Dagobah) — *"large, twisted roots"*, things *"hid amongst the gnarltree roots"* | roots as architecture and as cover, not decoration | **kaddrath** |
| **hydenock** — *"a strong red dye could be obtained by crushing and boiling its bark"* | the common tree whose value is in its bleeding bark | **ghemmel** |
| **jogan** — a fruit tree whose produce is the point | oversized low-hanging fruit as free calories with a tax | **nemmer** |
| **greel** — *"the crimson timber … in great demand as a luxury item"*, *"fastidious"* | a premium export timber in small pure stands | **vurmeloth** |
| **vesuvague** (Ithor) — carnivorous, *"vines and roots … to seize, strangle, and crush"* | a crownless hanging curtain whose leaves are not still | **zhorrel** |
| **bafforr** — *"aquamarine in color"*, *"branches formed a sharp, interlocking web"*, *"the smooth bark hummed under his touch"*, a grove of seven being a mind | the one non-green plant; an overhead lattice instead of a crown; the hum | **thalquith** (the grove-mind is its own item, `GREENTIDE_HUMMING_GROVE_1`, and was **not** designed here) |
| **orga** (Kashyyyk) — *"sharp vines, acid-filled pods, or strong tentacles … when treated with respect they allowed their roots to be foraged"* | forage-if-undisturbed, acid-if-damaged — reward and hazard in one object | **cundral** |
| **yerdua poison-spitter** — *"a vicious animal-plant hybrid"* | a static plant with a ranged attack | **gorbeleth** |
| **felucian glowspore** | a low glowing cap as the understory's only light | **illurin**. 🔴 Note: this name was **never canon** — a 2026-09-22 search returned no hits for either `glowspore` or `felucian glowspore`. It was a donor mod author's invention presented as canon, and it is precisely why §3g verifies every coined name. |
| **uneti** — *"incredibly rare … mildly Force-sensitive"* | nothing. Its whole meaning is Jedi, which has no place in a Jawa scavenger jungle. Moot now in any case. | — |
| **syren plant**, **blba tree**, **nysillin** | nothing usable — the first is one sentence with no appearance, the second has no description at all, the third is a herb | — |

**Two invented rows in this roster owe nothing to canon at all** and came straight from the biome
sheet: **sarnstilt** (§4's Lungers waiting in the water's shade) and **quathis** (a building material
the biome needed). A third, **mirrelbole**, dramatises `the_greentide.md` §4's *"Trees grow until they
crack and fall"* more than it does the wroshyr.

⚠️ **The old canon-tier bookkeeping is gone, not archived.** Which rows were current canon versus
Legends, and the two canon-admission edge questions, were all questions about whether something
could *ship* as canon. Nothing ships as canon, so they are moot rather than deferred.

# Appendix B — the other art subjects, and why they are not free

MEASURED 2026-09-22 by reading each subject's own `done/<id>.json` `style_notes`, which names its
`Source row: flora:<biome_sheet>:<donorDefName>`. This is the evidence for §3f's *"17 rows owe
art"* — it is a negative result, and it is why nobody should plan on reuse.

| subject(s) | source row | biome | canvas | verdict |
|---|---|---|---|---|
| `alientree_v1/v2`, `alientreepolluted_v1`, `halfalientree_v1` | `AB_AlienTree` family | the Contagion | v2 = 1024² | **not free** — and `v2` is the worked precedent for §3f's re-render |
| `mangrovetree_v1`, `mangrovepalm_v1`, `tanglerootmangrove_v1` | `AB_MangroveTree` / `AB_MangrovePalm` / `BMT_Plant_TreeTanglerootMangrove` | the Miasma | 256² | **not free** |
| `firevinetree_v1` | `AB_FirevineTree` | the Forge | 256² | **not free** |
| `largeslimytree_v1`, `slimytree_v1`, `slimyfern_v1` | `AB_LargeSlimyTree` / `AB_SlimyTree` / `AB_SlimyFern` | the Slime | 256² | **not free** |
| `twistingthornwood_v1` | `BMT_Plant_TreeTwistingThornwood` | the Cracked Lands | 256² | **not free** — `RUT_TwistingThornwood` is already our port |
| `tropicalchokevine_v1` | `RG_Plant_TropicalChokevine` | the Webwork | 256² | **not free** |
| `greenrockfern_v1` | `AB_GreenRockFern` | Weeping Stones | 256² | **not free** |
| `rut_paletree_v1`, `rot_paletree_v2/v3` | `RUT_PaleTree` | the Rot | — | **not free** |
| `fungusfern_a..d_v1` | `Fungusfern` | the Lantern Deeps | 128² | **not free** |
| `rswollimwood_v1` | `RSW_OllimWood` — a harvested-resource *icon*, not a tree | Deep Desert | 256² | **not free** |

⚠️ **`registry.jsonl` contains zero entries for any Greentide tree subject id** (checked), so
`done/` is the only record of them.

# Appendix C — the donor rows were already ruled, and this is not a re-ask

The item asked a design pass to *"decide the donor rows' fate."* **He decided it on 2026-09-20.**
MEASURED 2026-09-22 from the frozen decision files: `Transient/port_tail_2026-09-20.decisions.json`
and `Transient/port_swac_2026-09-20.decisions.json` are both `"frozen": true`, both carry
`"approvedSaid": "Yes replace everything."`, and both record
`"frozenMeaning": "Owner ruled every row 'replace' on 2026-09-20. Reopen only on his word."` The
sheet's own key defines `replace` as *"Replace with owned."*

| donor row | commonality today | ruled | succeeded by |
|---|---:|---|---|
| `AB_JungleTree` | 3.0 | `replace` | **`RM_Veluthar`** (row 1) — and it is that row's art |
| `Plant_HydenockTree_Wild` | 1.5 | `replace` | **`RM_Ghemmel`** (row 6) — and it is that row's art |
| `Plant_JoganTree_Wild` | 1.2 | `replace` | **`RM_Nemmer`** (row 7) — and it is that row's art |
| `Plant_FelucianGlowspore_Wild` | 0.6 | `replace` | **`RM_Illurin`** (row 21) — and it is that row's art |
| `Plant_MujaFruit_Wild` | 1.0 | in scope per *"replacements for everything"* | **`RM_Brakkel`** (row 15) |
| `Plant_HubbaGourd_Wild` | 0.8 | ″ | **`RM_Tumbel`** (row 16) |
| `AB_SugarFamewort` | 0.6 | ″ | **`RM_Sarquin`** (row 17) |
| `Plant_Bubblespore_Wild` | 0.5 | ″ | **`RM_Phorrik`** (row 18) |
| `Plant_Chakroot_Wild` | 0.5 | ″ | **`RM_Wollick`** (row 19) |
| `Plant_TookeTrap_Wild` | 0.5 | ″ | **`RM_Maddrick`** (row 20) |

⇒ **Nothing is cut.** Every borrowed row is succeeded by a def of ours carrying the concept forward,
and `RUT_GiantLeaf` at 1.0 is already ours and stays. The only true loss is donor-specific behaviour
unreadable from this machine — §8.4.

⚠️ **Two of the non-tree rows already have ports** — `RSW_Plant_HubbaGourd_Wild` and
`RSW_Plant_Chakroot_Wild` in `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortB_Plants.xml`.
They are `RSW_`-tier ports of canon names, so they are **not** superseded by rows 16 and 19 and must
not be deleted for them: `tumbel` and `wollick` are the franchise-free biome's own plants, and the
canon gourd and chak-root remain available to the campaign tier. ⛔ Read
`DONOR_DEFS_PORT_TO_OURS_1` before touching either — and do not duplicate a port that exists.

---

## Provenance

- **Invented names:** coined here, all 21 verified against
  `https://starwars.fandom.com/api.php?action=query&list=search` — zero hits each (§3g), plus a
  case-insensitive grep across `src/` returning zero matches. Two candidates were rejected on hits
  and replaced.
- **Canon text in Appendix A:** sourced by an earlier pass this same day via
  `https://starwars.fandom.com/api.php?action=parse&page=<Page>&format=json&prop=wikitext`, the route
  `design/RimStarWars/canon_references/AGENT_BRIEF.md` prescribes. Retained as inspiration only.
- **Repo facts, read this session:** `src/RimMandrake/Greentide/Defs/BiomeDefs/RM_Greentide_Biome.xml`,
  `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_Placeholder_GreentideGiantTree.xml`,
  `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_GreatboleCore.xml`,
  `src/RimMandrake/EnvironmentalHazards/Source/`, `src/RimStarWars/SWBestiary/Defs/DesertPort/`,
  `design/Jawa/mods/biome_flora.py`, `infrastructure/artpipe/done/`,
  `infrastructure/artpipe/registry.jsonl`, `Transient/port_*.decisions.json`.
- **Design authority:** `infrastructure/state/items/GREENTIDE_JUNGLE_TREE_ROSTER_1.md`,
  `GREENTIDE_BIOME_DENSITY_1.md`, `HOSTILE_MOBILE_PLANTS_1.md`, `TREE_GRAPHICS_OWNERSHIP_1.md`,
  `design/Jawa/worldbuilding/biomes/the_greentide.md`.
- ⛔ **No claim on this page is live-proven.** There is no game, no def dump and no decompiler on this
  machine. Everything engine-side is marked UNMEASURED in §8.
