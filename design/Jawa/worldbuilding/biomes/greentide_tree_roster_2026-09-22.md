# Greentide flora roster — 14 invented trees + 7 invented understory plants, 2026-09-22

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

**No new signature giant.** Ruled this session: the signature huge tree is the one **already
built** — `RUT_GreatboleCore`, a structure def you mine into, which cannot be felled. §4. Every
canopy row below is an ordinary (if large) fellable tree, and they are what finally give the
existing tree-felling machinery real content instead of a placeholder.

**Fourteen trees, three strata:**

| canopy — the fall is a map event | mid-storey — the working forest | understory — under the Roil |
|---|---|---|
| **veluthar** — umbrella of paddle leaves | **brunnock** — the hardwood | **quathis** — a single flat fan |
| **mourvel** — willow curtain to the ground | **ghemmel** — bleeds red; the commons | **thalquith** — aquamarine lattice that hums |
| **kaddrath** — roots first; the causeways | **nemmer** — fruit too big for the branch | **cundral** — acid pods, forageable root |
| **sarnstilt** — a tripod standing in the river | **vurmeloth** — the crimson export | **gorbeleth** — a throat that spits |
| | **mirrelbole** — splits and bleeds the fuel sap | |
| | **zhorrel** — the strangler curtain | |

**Seven understory plants:** **brakkel** (fruit), **tumbel** (gourds), **sarquin** (sugar),
**phorrik** (spores), **wollick** (tuber), **maddrick** (the trap), **illurin** (the only light).

**Names:** all 21 coined here and **verified unused** — Wookieepedia search returned zero hits on
every one, and zero matches in our own `src/`. §3g records the check.

**Art:** 4 existing subjects transfer; **17 rows owe art**. All four transferring subjects are
**256×256 and under-resolved** against the canvas law — see §3f.

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
| 12 | `RM_Thalquith` | thalquith | **flat interlocking lattice** | **Aquamarine — the only non-green thing growing here.** Smooth trunk with no bark texture at all, and branches that meet overhead in a flat interlocking lattice rather than a crown. Saplings are literal inverted cones. The lattice **hums** in moving air. | 4 · yes, and the lattice shatters | **The strange one, and a warning system.** Its hum is constant; the hum *stopping* is the tell, which is how it meets §9's *"its scariest signal is silence."* Fragile: hard to keep alive near work. See Q2 — whether the grove behaviour is real or flavour is his call. | **OWED** |
| 13 | `RM_Cundral` | cundral | **skirt of runners under a squat bole** | A squat woody base almost buried under a skirt of tentacle-thick ground runners, with translucent pods hanging among them like fruit you must not pick — you can see the acid moving inside them. | 2 · no | 🔑 **Reward and hazard are the same object, most explicitly on the page.** Left undisturbed it lets you dig its root, a real food staple. Damaged, the pods go. | **OWED** |
| 14 | `RM_Gorbeleth` | gorbeleth | **barrel with an upward throat** | A low mottled purple-brown barrel of a trunk with one upward-facing muscular throat at the top, ringed with tooth-like bracts. It twitches toward movement. Nothing else about it suggests a plant. | 3 · no | The understory's ranged hazard. Its toxin is worth extracting, which means going close. Pairs naturally with the jungle rancor content already in `src/`. | **OWED** |

### 3d. The seven understory plants — the non-tree rows, also ours

These replace the seven borrowed non-tree rows the owner put in scope (*"We work on drafting the
replacements for everything right now. No reason to wait!"*). Same treatment: invented, `RM_` tier.
⚠️ These are `Plant` defs, **not** trees and **not** `HOSTILE_MOBILE_PLANTS_1` creatures — even
`maddrick`, which is a static trap, never a mobile one.

| # | defName | label | replaces the role of | silhouette FORM | what it looks like | job |
|---|---|---|---|---|---|---|
| 15 | `RM_Brakkel` | brakkel | a fruit bush | **low overlapping mound** | A knee-high mound of enormous overlapping paddle leaves with the fruit clustered *underneath* — you have to lift the leaves to see whether there is anything there, and to see what else is under there. | The forageable staple. Candidate to replace the biome's `foragedFood` `RawBerries`, which is a vanilla row (`GREENTIDE_BIOME_DENSITY_1` flags it). |
| 16 | `RM_Tumbel` | tumbel | a gourd plant | **sprawling ground runner** | A long flat runner creeping over the mud with heavy hollow vessels resting on it at intervals, each the size of a crate, dull and leathery-skinned. No vertical presence at all — it is a **texture on the floor**, which is why it belongs here. | Food plus containers: the hollow shells are cut into vessels. A waypoint-marker plant — you can see one from a distance. |
| 17 | `RM_Sarquin` | sarquin | a sugar-producing plant | **whorl with hanging drip-tentacles** | A thick fleshy central whorl with long hanging tentacle-leaves that drip clear sweet sap continuously, each drip-point glazed and crusted. The mud beneath is sugared and crawling. | The sugar source. 🔑 Reward and hazard together: the drip is why insects are there, and the insects are why something bigger is. |
| 18 | `RM_Phorrik` | phorrik | a spore plant | **cluster of taut bladders** | A tight cluster of taut translucent bladders on short stalks, each visibly over-full. They burst when trodden on. | Hazard-with-payoff: the spores are medicinal, and walking through a patch fills the air. Interacts directly with movement cost — a patch you go around. |
| 19 | `RM_Wollick` | wollick | a root plant | **flat ground rosette** | A flat rosette of huge ground-hugging leaves pressed to the mud over a deep starchy tuber. Visually almost pure floor coverage — it *is* the "no square uncovered" ruling in plant form. | Bulk carbohydrate. Digging it slumps the churnmud around it, which is a small honest cost rather than a hazard. |
| 20 | `RM_Maddrick` | maddrick | a trap plant | **inward-curling blade ring** | A ring of inward-curling leaf blades, waxy and wet, around a shallow throat of standing fluid. It closes on what steps in. Completely static — it does not move toward anything. | Pure hazard, with a use: a patch of maddrick is a free perimeter. Something for the player to build *around* rather than clear. |
| 21 | `RM_Illurin` | illurin | a glowing understory plant | **broad low glowing cap** | A broad low fleshy cap on a short thick stem, glowing cyan-green from its underside down onto the mud — lighting the ground and nothing above it. | **The only light under the canopy.** Suppresses nothing, reveals everything within its small radius. Without it the understory is unreadable. **Art EXISTS — `artpipe/done/felucianglowspore_v1.json`** (*"7 wide"*, glowing) 🔴 256², §3f. |

**Art on the other six:** all **OWED**. Nothing in `artpipe/done/` keys to a non-tree Greentide
flora row (§3f is the full measurement).
