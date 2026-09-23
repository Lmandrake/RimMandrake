# Greentide jungle tree roster — proposal for ruling, 2026-09-22

**Status: DESIGN PROPOSAL. Nothing authored.** No ThingDef written, no art commissioned, no def
edited. This document exists to be ruled on; a build seat implements whatever survives.

Item: `GREENTIDE_JUNGLE_TREE_ROSTER_1`. Ownership precedent: `TREE_GRAPHICS_OWNERSHIP_1`.

## At a glance

**The signature giant:** **wroshyr** (`RSW_WroshyrTree`) — canon Kashyyyk giant, canonically
*tropical*, canonically sapped for *"fuel, oils, and chemicals"*, and its fossil resin **meryx** is
*"the single rarest gemstone in the galaxy"*. Art already exists; needs one re-render.

**Thirteen ordinary trees**, nine of them canon-named:

| canopy | mid-storey | understory |
|---|---|---|
| **massassi tree** — purple-barked emergent | **hydenock** — bark bleeds red dye & resin | **felucian glowspore** — the only light |
| **brylark tree** — wood *"as strong as metal"* | **jogan tree** — the fruit that wants eating | **bafforr tree** — aquamarine grove-mind |
| **gnarltree** — its roots *are* the causeways | **greel tree** — crimson luxury timber | **orga bole** — acid pods, forageable root |
| **stiltkurr** *(invented)* — stands in the river | **weepbole** *(invented)* — splits and bleeds sap | **yerdua poison-spitter** — animal-plant hybrid |
| | **vesuvague hanging tree** — strangler | |

**Art:** 3 of 13 have finished art on disk; **10 owed**. The giant's art exists and needs a
re-render at the right canvas.

**Already ruled, so not asked:** all four donor trees are ruled `replace` (owner, 2026-09-20, frozen
sheets, *"Yes replace everything."*). **Blocking question:** Q1 — is "the signature huge tree" the
fellable giant or the Greatbole?

## 1. The ruling being served

**Owner, 2026-09-22**, verbatim:

> *"Absolutely not. We should have wild jungle trees with bizarre Starwars names. And lots of
> them, a diversity of perhaps ten types of trees at least. Plus the signature huge tree."*

He was rejecting the generic Greentide's tree list — `Plant_TreeOak` 2.0 and `Plant_TreePoplar`
1.2, two temperate-forest trees under a `World/Biomes/TropicalRainforest` texture.

**And he already ruled the ownership question** (`TREE_GRAPHICS_OWNERSHIP_1`): *"Rather than use
the whole Comingo tree thing, we should simply generate our own tree graphics at the scales we
want and drop all the nonsense of multiple tree mods modifying our designs to who-knows-what
scale."* ⇒ these trees are **ours**, not more donor rows. Not re-asked here.

## 2. What the design must satisfy

Constraints taken as given, not re-litigated:

1. **Tier rule (§7 Q11).** A `RimMandrake`-tier def never names Star Wars. So every tree below is
   `RSW_` (galaxy-wide Star Wars) or `RUT_` (this campaign / this planet only), and reaches the
   biome through a patch file modelled on `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Greentide.xml`
   — a `WildPlants_Greentide.xml` sibling. `RM_Greentide`'s own `wildPlants` block stays a
   dependency-free vanilla floor and is **out of scope**.
2. **Flammability.** `the_greentide.md` §6 hard ban 3: *"No high-Flammability native flora —
   saturated growth does not burn; a flammable Greentide plant def is a violation."* Every tree
   below carries a low `Flammability`. This is load-bearing for the biome, not flavour: §4b says
   *"Fire is not the tool"* precisely so the dry-air blower stays the answer.
3. **No vanilla-Earth flora** (§6 ban 2). Terrestrial-analog *shapes* are allowed; Earth *names*
   are not. "Mangrove", "palm", "fern", "oak" are therefore banned as labels even where the
   silhouette is right — which is why several rows below rename a shape we already have art for.
4. **Three fellers, one fall** (§4, §7b). Every tree is subject to being *gnawed from below,
   cracked from within, or shouldered over from the side*. The tree roster is the input to a
   mechanism that already exists, so each row must declare whether it falls, and how big the fall
   is. `RM_FellableTreeExtension` + `CompProperties_CrackFall` are the wiring.
5. **The wood economy has two grades** (§7). **Greenwood** — *"not quality hardwood but burnable
   and buildable... a major resource"* — comes off ordinary fallen trees in bulk. **True hardwood**
   comes *"only from the heart of fallen giants."* A roster of 12 trees has to make that gap legible,
   so most rows drop greenwood only, and hardwood is restricted.
6. **The canopy has to be a real place.** §4's Swingers *"cross above the river"*; §4c's underlight
   rain *"condenses on the canopy and drips forever"*; §8b's root causeways are *"the giants' roots
   … the roads."* So the roster needs genuine vertical strata — canopy, mid-storey, understory —
   not twelve interchangeable trees at one height.
7. **Names.** Bizarre is the explicit ask. Canon where canon exists; invention labelled as
   invention. ⚠️ `design/RimStarWars/canon_references/` holds **no plant entries at all** (142
   directory entries, the only near-match is `massassi`, which is a species) — so that library
   cannot confirm or deny a plant name, and its silence is worth nothing here either way.
8. **Precedent says off-world canon plants are allowed on Ash'karr.** The campaign twin already
   ships jogan (Naboo), muja (Naboo), hubba gourd (Tatooine), chak-root, felucian glowspore
   (Felucia). So a canon species from another world appearing here is established practice, not a
   new licence I am taking.

## 3. The roster — 13 trees in three strata

**All canon sourced live by `curl` to the Wookieepedia API this session** (the route
`canon_references/AGENT_BRIEF.md` prescribes — it worked, HTTP 200 on every page). Quoted facts
are from the article wikitext, not from memory. Rows marked **INVENTED** have no canon source and
say so.

⚠️ **Canon tier is mixed and labelled per row.** Some of these are current canon (wroshyr, brylark,
gnarltree, massassi, hydenock, orga, syren, uneti); some are Legends only (vesuvague, bafforr,
greel, yerdua). Legends is established practice in this campaign — gizka, kinrath, hssiss and
chak-root are all Legends and all already shipped — but the owner may want the distinction to
matter, so it is on the page.

`cells` is the visual footprint in the project's own "N cells wide" convention, not a multi-cell
`size`. All rows are `ParentName="TreeBase"`, single-tile footprint, oversized sprite — the idiom
`RUT_SweetlineTree` and `RUT_GreatboleCore` already established here.

### A. Canopy / emergent — four trees. The fall is a map event.

| # | defName | label | canon basis (sourced) | what it looks like | cells / role | art |
|---|---|---|---|---|---|---|
| 1 | `RSW_MassassiTree` | massassi tree | **Canon.** *"Massassi trees were purple-barked giant trees … was the habitat of various animal species, including the woolamanders and the stintarils"* (Yavin 4; canonised in *Ultimate Star Wars*, 2015). | Colossal **purple-to-black bark** on a straight bole, crown starting high and spreading flat. The one tree on the page that is not green — a violet trunk against §9's *"every green at once"* is the strongest silhouette read in the roster. | 8 · the dominant canopy tree, the Swingers' road. Falls hard. | **OWED** |
| 2 | `RSW_BrylarkTree` | brylark tree | **Canon.** *"a type of tree whose wood was as strong as metal and was sometimes used for lightsaber hilts"* — Huyang states Brylark is the only wood strong enough for a hilt (*The Clone Wars*, "A Test of Strength"). | Dense, dark, narrow-crowned, visibly *heavy* — short internodes, tight grain showing through cracked bark, the trunk disproportionately thick for the crown. | 6 · **the only hardwood source besides the giant.** Rare, slowest `growDays` on the page, highest `MaxHitPoints`. | **OWED** |
| 3 | `RSW_Gnarltree` | gnarltree | **Canon.** *"They grew best in swampy terrains and had large, twisted roots. Bogwings made their homes in the trees, and dragonsnakes and scrange hid amongst gnarltree roots"* (Dagobah). Also: *"Knobby white spiders … later grew into the trees"* — the tree **is** the adult stage of a spider. | Wide-splayed above-ground root buttresses with walk-through gaps, trunk shorter than the root mass is wide, crown modest. Reads as *roots first, tree second*. | 7 · **the Boughway generator** (§8b: *"the giants' roots are the roads"*). Its roots are the causeway, not decoration. | **OWED** |
| 4 | `RUT_Stiltkurr` | stiltkurr | **INVENTED** (name and species). Fills a shape the biome needs and canon does not supply. | Stands *in* the water on a tripod of prop roots, trunk starting a metre clear of the surface, crown leaning out over the channel. Bark salt-crusted and pale on the downstream rows. | 6 · river-margin only. §4's Lungers wait in the shade under it — this is the tree that makes crossing water frightening. | **OWED** |

### B. Mid-storey — five trees. The working forest, and where greenwood comes from.

| # | defName | label | canon basis (sourced) | what it looks like | cells / role | art |
|---|---|---|---|---|---|---|
| 5 | `RSW_HydenockTree` | hydenock | **Canon.** *"a strong red dye could be obtained by crushing and boiling its bark"*; a Naboo strain's *"bark was used by the native Gungans to produce bubble wort, the raw material for all Gungan bubble buildings."* | Gnarled trunk, dense rounded crown of small dark leaves, wind-bent — and **bark that bleeds red where it is cut or split**, which in this biome is everywhere. | 6 · the commonest mid tree. Its bark is §7's lacquer/waterproofing line, already canon, no invention needed. | **EXISTS — `infrastructure/artpipe/done/hydenocktree_v1.json`** (see §3c) |
| 6 | `RSW_JoganTree` | jogan tree | **Canon.** Jogan fruit is canon produce (Naboo/Felucia); the donor row `Plant_JoganTree_Wild` is the wild tree. | Slender pale smooth trunk, sparse wispy crown of drooping fronds, and fruit **too large for the branch**, hanging low enough to be taken from the ground. | 5 · **§4's *"the fruit yearns to be eaten"* row** — huge, sweet, everywhere, free calories with a tax. The roster's `harvestedThingDef` tree. | **EXISTS — `jogantree_v1.json`** |
| 7 | `RSW_GreelTree` | greel tree | **Legends.** *"The crimson timber — greel wood — was in great demand as a luxury item"*; native to Pii III/IV, *"the only planets with the proper ecosystem to support the fastidious trees."* | Modest, almost tidy tree; unremarkable until cut, when the heartwood is **arterial crimson**. Fussy about where it grows — appears in small pure stands, never mixed. | 5 · **the export.** Not a bulk wood: a premium timber the Jawa caravans carry out at a markup. "Fastidious" earns a very low commonality and tight clustering. | **OWED** |
| 8 | `RUT_Weepbole` | weepbole | **INVENTED** (name and species). Direct dramatisation of §4: *"Trees grow until they crack and fall"* and §7's *"tapped from trees growing too fast not to bleed."* | Trunk visibly **split down its own length** by its growth rate, the wounds glazed over with amber resin that never sets in the humidity. Sheds bark plates. Permanently wet-looking. | 4 · the sap tap. §7's *"rendered chemfuel — the dayside's fuel economy"* has a plant. Highest crack-fall rate on the page, by design. | **OWED** |
| 9 | `RSW_VesuvagueTree` | vesuvague hanging tree | **Legends.** *"a carnivorous, semi-sentient, red-barked tree from the planet of Ithor … able to detect and move itself towards motion by sensing air vibrations in its leaves and ground vibrations in its roots … used its quickly growing vines and roots, capable of extending multiple meters in mere seconds, to seize, strangle, and crush its food."* | Red bark, no real crown — a hanging curtain of slack vines from a low crossbeam of branches. The vines are visibly **not still**. | 5 · §6 ban 1 (*"no truce, ever"*) made literal. Ambush. Under the Roil you meet it at chest height without seeing it. | **OWED** |

### C. Understory — four. Under the Roil, where the floor is hidden.

| # | defName | label | canon basis (sourced) | what it looks like | cells / role | art |
|---|---|---|---|---|---|---|
| 10 | `RSW_Glowspore` | felucian glowspore | 🔴 **NOT CANON — corrected 2026-09-22 by BENCH.** This cell originally read *"Canon. Felucian glowspore is canon Felucia flora; the donor row `Plant_FelucianGlowspore_Wild` is the wild form"* — which cites the donor mod as evidence for its own canonicity. Circular, and false. MEASURED by Wookieepedia search: `glowspore` → **NO HITS**; `felucian glowspore` → **NO HITS**. The name is the donor mod's invention. Canon Felucia flora that does exist: *Felucian spore plant*, *Felucian spike plant*, *Carnivorous plant (Felucia)*. ⇒ Treat this row as **INVENTED**, or rename it onto a real canon plant. "Felucia" is canon; "glowspore" is not. | Squat, broad, fleshy — a low bioluminescent cap on a short thick stem, glowing cyan-green from the underside onto the mud. | 7 wide but **low** · **the only light under the canopy.** Structurally a tree def; visually a floor organism. Suppresses nothing, lights everything. | **EXISTS — `felucianglowspore_v1.json`** |
| 11 | `RSW_BafforrTree` | bafforr tree | **Legends.** *"Bafforr branches formed a sharp, interlocking web. The bafforr trees were aquamarine in color … Sapling bafforr trees looked like inverted cones … A total of seven bafforr trees were required for true sentience. Below that number, a grove became befuddled, losing its memories … the smooth bark hummed under his touch."* | **Aquamarine** — the one blue thing in a green biome. Smooth trunk with no bark texture at all; branches meeting in a flat interlocking lattice overhead; saplings are literal inverted cones. | 4 · **the strange one.** Its canon carries a mechanic for free: a grove of **seven or more** is a mind. See §6 Q4. | **OWED** |
| 12 | `RSW_OrgaBole` | orga bole | **Canon.** *"The orga was a plant found on the lowest levels of the Wookiee homeworld of Kashyyyk. They could react violently to anyone who sought to harm them, using their sharp vines, acid-filled pods, or strong tentacles. When treated with respect, however, they allowed their roots to be foraged."* | Squat woody base under a skirt of tentacle-thick runners and **translucent acid pods** hanging like fruit that you must not pick. | 2 · forageable if undisturbed, hostile if damaged. ⚠️ Canon calls orga a **plant, not a tree** — this row gives it a woody bole to qualify. Flagged, §6 Q5. | **OWED** |
| 13 | `RSW_YerduaSpitter` | yerdua poison-spitter | **Legends.** *"The Yerdua poison-spitter was a vicious animal-plant hybrid. The vicious nature of the Jungle rancor may have been due in part to the hybrid."* | Low barrel of a trunk with a single upward-facing muscular throat at the top, ringed with tooth-like bracts. Twitches toward movement. | 3 · **ties straight into content we already ship** — `RSW_Pawn_JungleRancor_*` defs exist in `src/`, and canon links the jungle rancor's temperament to this plant. A ranged hazard in the understory. | **OWED** |

### 3b. Deliberately considered and NOT proposed

- **`Uneti tree`** (canon, *"incredibly rare … mildly Force-sensitive"*, Ahch-To/Coruscant/Yavin 4).
  A superb strange tree, but its whole meaning is Jedi, and this is a Jawa scavenger campaign with
  no Force thread in the Greentide. Held as a one-per-map curiosity if he wants it — §6 Q6.
- **`Syren plant`** (canon, Kashyyyk carnivore). Sourced text is a **single sentence** with no
  appearance at all, and it would be the third carnivore on the page after vesuvague and the
  already-shipped tooke-trap. Cut for redundancy, not for canon.
- **`Blba tree`** (canon, Dantooine) — the article carries no description whatsoever. Nothing to
  design from.
- **`Nysillin`** (canon Felucia healing herb) — a herb, not a tree. Belongs to §7's *"the most
  biochemically frantic pharmacopoeia on the planet"*, not to this roster.
- **Earth-named shapes we already have art for** — "mangrove", "palm", "fern". §6 ban 2 forbids the
  names even where the silhouette is right. `RUT_Stiltkurr` is the licit version of the mangrove
  shape.

### 3c. Art — MEASURED, and the item's open question is now answered

The item recorded: *"⚠️ UNVERIFIED which of those subjects are replacement art for the donor rows
versus free for a new def of ours."* **Answered, MEASURED 2026-09-22** by reading every candidate's
own `done/<id>.json`. Each carries a `style_notes` field naming its `Source row:
flora:<biome_sheet>:<donorDefName>`:

| subject | source row | biome sheet | canvas | verdict for this roster |
|---|---|---|---|---|
| `jungletree_v1` | `AB_JungleTree`, large, *"10 cells wide"* | **the_greentide** | 256² | **the signature giant's art** — see §4 |
| `felucianglowspore_v1` | `Plant_FelucianGlowspore_Wild`, large, *"7 wide"* | **the_greentide** | 256² | **free for row 10** |
| `hydenocktree_v1` | `Plant_HydenockTree_Wild`, medium, *"6 cells wide"* | the_fever_wood | 256² | **free for row 5** (same donor def, two biomes) |
| `jogantree_v1` | `Plant_JoganTree_Wild`, medium, *"5 cells wide"* | the_fever_wood | 256² | **free for row 6** |
| `alientree_v1/v2`, `alientreepolluted_v1`, `halfalientree_v1` | `AB_AlienTree` family | the_contagion | v2 = 1024² | **NOT free** — the Contagion's |
| `mangrovetree_v1`, `mangrovepalm_v1`, `tanglerootmangrove_v1` | `AB_MangroveTree` / `AB_MangrovePalm` / `BMT_Plant_TreeTanglerootMangrove` | the_miasma | 256² | **NOT free** — the Miasma's |
| `firevinetree_v1` | `AB_FirevineTree` | the_forge | 256² | **NOT free** |
| `largeslimytree_v1`, `slimytree_v1`, `slimyfern_v1` | `AB_LargeSlimyTree` / `AB_SlimyTree` / `AB_SlimyFern` | the_slime | 256² | **NOT free** |
| `twistingthornwood_v1` | `BMT_Plant_TreeTwistingThornwood` | the_cracked_lands | 256² | **NOT free** — and `RUT_TwistingThornwood` already exists as our port |
| `tropicalchokevine_v1` | `RG_Plant_TropicalChokevine` | the_webwork | 256² | **NOT free** |
| `greenrockfern_v1` | `AB_GreenRockFern` | weeping_stones | 256² | **NOT free** |
| `rut_paletree_v1`, `rot_paletree_v2/v3` | `RUT_PaleTree` | the_rot | — | **NOT free** |
| `fungusfern_a..d_v1` | Lantern Deeps `Fungusfern` | the_lantern_deeps | 128² | **NOT free** |
| `rswollimwood_v1` | `RSW_OllimWood` (a harvested-resource *icon*, not a tree) | deep_desert | 256² | **NOT free** |

⇒ **Three of thirteen ordinary trees have art on disk. Ten are genuinely owed, plus a re-render for
the giant.** `registry.jsonl` contains **zero** entries for any of these ids (checked), so `done/`
is the only record.

🔴 **And the three reusable subjects are UNDER-RESOLVED at their own declared scale.** All were
rendered at **256×256** while their own source notes say 5–10 cells wide. The project's canvas law
is `128 px/cell × cells`, and this exact defect already has a worked fix: `alientree_v2.json` says
`alientree_v1` *"shipped at 256×256 because drawsize_backfill.json's 'alientree' stem was wrongly
resolved"* and re-rendered it at **1024²** for a 5-cell tree under `FLORA_LEGIBILITY_BAR_1`. The
same correction was **never applied to the four Greentide/Fever-Wood tree subjects.** So each needs
a `_v2` at its proper canvas (`hydenock` 768², `jogan` 640², `glowspore` 896², **`jungletree` 1280²**)
before it ships. That is a re-render of an existing, already-approved concept — cheap — not a new
design job.

## 4. The signature giant — `RSW_WroshyrTree`, "wroshyr"

**Proposed defName** `RSW_WroshyrTree` · **label** `wroshyr` · **tier** `RSW_` (a galaxy-wide Star
Wars species, not an Ash'karr endemic) · **footprint** 10 cells.

### 4a. Why this one, and not an invention

Sourced canon (Wookieepedia, `Wroshyr tree`, pulled this session), with the Greentide line each fact
serves:

| canon, verbatim | what it already pays for |
|---|---|
| *"a species of giant, long-lived, cone-bearing trees"*; lifespan *"Up to 50,000 years"* | §7b's tree ladder needs a top rung that is old rather than merely large. |
| *"the tropical wroshyr of Wawaatt Archipelago … averaged 300 to 400 meters in height. The deep-forest variety was much bigger, reaching several kilometers"* | It is canonically a **tropical** giant. Nothing has to be imported from a temperate world and re-explained. And canon itself supplies the two scales the ladder wants. |
| *"The Wookiees used the sap of the wroshyr trees to make medicine, food, and beverage, and as a base material to produce fuel, oils, and chemicals"* | §7 verbatim: *"Sap and resin … glue, lacquer, waterproofing, and **rendered chemfuel** — the dayside's fuel economy."* This is already the biome's economy; canon hands it to us whole. |
| *"Wookiee settlements consisted of individual tree communities … made of wroshyr wood that was thousands of years old"* | §7b's Greatboles — *"you dig chambers INTO the tree"*. The canon precedent for living inside the tree exists. |
| *"there remained lumps of their fossilized resin, which were called **meryx** and were considered the single rarest gemstone in the galaxy"* | A ready-made premium scavenger export: a Jawa clan cutting meryx out of a fallen giant's heart is this campaign's fantasy with no invention at all. Pairs with §7's *"True hardwood — only from the heart of fallen giants."* |
| *"over 1,000 different varieties … adapted to growing everywhere"* | Licenses future variants (a saline downstream wroshyr at the river graves, §3) without a canon argument. |

**The one thing invention still owes:** canon gives no bark colour or crown shape for a tropical
wroshyr, so the visual brief is ours. Proposed: a **buttressed grey-brown bole far too wide for its
cell**, bark in vertical plates deep enough to climb, and a crown that starts high and closes
over — dark green above, and the underside wet, because §4c's underlight rain drips off it.

### 4b. It is the MIDDLE rung, not the top — and this needs confirming

`the_greentide.md` §7b defines a three-rung ladder: *"normal trees (fall) → giants (crack, fall,
hardwood jackpot) → **Greatboles**: terrain-scale living towers, multi-cell, too big to fall."*

- **The Greatbole is already built, and it is not a plant.** `RUT_GreatboleCore` is a
  `ParentName="BuildingBase"` ThingDef in `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/`,
  `passability Impassable`, `deconstructible false`, placed by `RUT_Greentide_LivingBolesGenStep`,
  with `RUT_GreatboleHeartwood` and `RUT_ToxinSealant` around it. It cannot fall and is not in any
  `wildPlants` list.
- **The placeholder is unambiguously the middle rung.** `RUT_Placeholder_GreentideGiantTree` carries
  `RM_FellableTreeExtension` with `isGiantClass=true`, `fellLength=10`, `hardwoodDef RUT_Hardwood`.
  It falls.

⇒ I read *"the signature huge tree"* as **the fellable giant**, and `RSW_WroshyrTree` is proposed as
that. But see §6 Q1: on the wroshyr's own canon the Greatbole is *also* a wroshyr, and the Greatbole
currently **has no name at all**.

### 4c. Its art exists, and it needs one cheap re-render

`infrastructure/artpipe/done/jungletree_v1.json` — its own `style_notes`: *"Source row:
flora:**the_greentide**:AB_JungleTree, sizeBin large, note: '10 cells wide'"*, and the placeholder's
own header reserves it as *"already roster-tracked art … for the flora roster pass's own real
giant."* Both point the same way: **this is the giant's art.** No new generation needed.

🔴 **But it was rendered at 256×256 for a declared 10-cell tree.** Under the project's
`128 px/cell × cells` canvas law a 10-cell tree is **1280×1280** — the same figure
`TREE_GRAPHICS_OWNERSHIP_1` landed for `RUT_SweetlineTree` at 10 cells. `alientree_v2` is the
worked precedent for exactly this correction (256² → 1024² for a 5-cell tree, under
`FLORA_LEGIBILITY_BAR_1`), and it was never applied here. ⇒ **`jungletree_v2` at 1280×1280 is owed,
as a re-render of an approved concept.** Shipping `jungletree_v1` as the signature giant would put
a 5×-upscaled 256px sprite at the visual centre of the biome.

### 4d. Retiring the placeholder — smaller than the item implies

MEASURED 2026-09-22: `RUT_Placeholder_GreentideGiantTree` appears in **exactly three places** —
its own file, and two **C# doc comments** (`RM_FellableTreeExtension.cs:16`, `RM_CompCrackFall.cs:9`).
It is in **no** BiomeDef's `wildPlants` and no other def references it.

And the mechanisms are **def-agnostic**: `RM_TreeFallUtility.cs:67` reads
`tree.def.GetModExtension<RM_FellableTreeExtension>() ?? Default`, with a static `Default`
described in its own comment as *"Used for any Plant with no RM_FellableTreeExtension of its own"*.

⇒ The "three mechanisms need re-pointing" work is:

1. Put `RM_FellableTreeExtension` (`isGiantClass=true`, `fellLength` ~10, `hardwoodDef RUT_Hardwood`,
   `greenwoodDef RUT_Greenwood`) and `CompProperties_CrackFall` on `RSW_WroshyrTree`, carrying the
   placeholder's values forward as a starting point — the header says they are **INVENTED**, so they
   are not a tuned baseline.
2. Delete the placeholder file outright (per the repo's delete-don't-supersede law).
3. Update the two C# doc comments to name the real def.
4. The other twelve rows need **no** extension unless they want non-default fall behaviour — the
   `Default` covers them. That is worth knowing before anyone authors thirteen extension blocks.

⚠️ `MayRequire="mandrake.rm.environmentalhazards"` on the placeholder gates the whole ThingDef on
the hazards mod. The real giant **must not** be gated that way — it would vanish from the biome
without that mod. Gate only the `modExtensions`/`comps` entries, as `RUT_GreatboleCore` already does
with `<li MayRequire=...>`.

### 4e. One defect found in the placeholder, worth fixing when it is replaced

`RUT_Placeholder_GreentideGiantTree` sets `<Flammability>0.5</Flammability>`. `the_greentide.md` §6
hard ban 3 is *"No high-Flammability native flora — saturated growth does not burn; a flammable
Greentide plant def is a violation"*, and §4b makes it load-bearing (*"Fire is not the tool… keeping
the blower load-bearing"*). The analogous ban in the arid shrubland drove `RUT_SweetlineTree` to
`0.1`. **0.5 reads high against that precedent.** I am not asserting it breaches the ban — "high"
has no numeric threshold on the sheet and vanilla's `TreeBase` default is UNMEASURED here — but the
real giant should not inherit 0.5 unexamined. §6 Q3 asks for the ceiling.

## 5. The donor tree rows — **already ruled, not a question**

The item asks me to *"decide the donor rows' fate"*. **He decided it two days ago.** MEASURED
2026-09-22 from the frozen decision files:

`Transient/port_tail_2026-09-20.decisions.json` and `Transient/port_swac_2026-09-20.decisions.json`
— both `"frozen": true`, both `"approvedSaid": "Yes replace everything."`, both
`"frozenMeaning": "Owner ruled every row 'replace' on 2026-09-20. Reopen only on his word."`, with
execution assigned to `DONOR_DEFS_PORT_TO_OURS_1`. The sheet's own option key defines `replace` as
**"Replace with owned"**, and its brief carries his ruling verbatim: *"Everything should be moved to
our own thing defs."*

Every donor tree in the Greentide is on those pages and ruled `replace`:

| donor row | commonality today | ruled | becomes |
|---|---:|---|---|
| `AB_JungleTree` | 3.0 | `replace` (port_tail) | **`RSW_WroshyrTree`** — the signature giant, §4 |
| `Plant_HydenockTree_Wild` | 1.5 | `replace` (port_swac) | **`RSW_HydenockTree`** — row 5 |
| `Plant_JoganTree_Wild` | 1.2 | `replace` (port_swac) | **`RSW_JoganTree`** — row 6 |
| `Plant_FelucianGlowspore_Wild` | 0.6 | `replace` (port_swac) | **`RSW_Glowspore`** — row 10 |

⇒ **Nothing is lost**, because nothing is being cut — each donor def is succeeded by a def of ours
carrying the same concept, and in three of four cases the replacement art was already generated for
that concept. The only true loss is donor-specific behaviour I cannot inspect from this machine
(see §7).

**The four non-tree donor rows are out of this item's scope** and untouched here — `Plant_MujaFruit_Wild`,
`Plant_HubbaGourd_Wild`, `AB_SugarFamewort`, `Plant_Bubblespore_Wild`, `Plant_Chakroot_Wild`,
`Plant_TookeTrap_Wild`. Two of them (`HubbaGourd`, `Chakroot`) **already have our ports** —
`RSW_Plant_HubbaGourd_Wild` and `RSW_Plant_Chakroot_Wild` in
`src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortB_Plants.xml`. `RUT_GiantLeaf` at 1.0 is
already ours and stays.

⚠️ **Naming inconsistency to settle once** (§6 Q7): those two existing ports are named
`RSW_Plant_HubbaGourd_Wild` — the donor's whole name with a prefix bolted on — while the tier
grammar in `design/NAMING_SCHEME_PLAN.md` and every other port (`RSW_Gizka`, `RSW_Kinrath`) uses the
clean form. This roster proposes the clean form (`RSW_HydenockTree`, not
`RSW_Plant_HydenockTree_Wild`). Whether the two existing outliers get renamed to match is his call,
not mine to front-run.

### 5b. Where the roster is wired

A new `src/RimUtinni/UtinniPatches/Patches/WildPlants_Greentide.xml`, modelled exactly on its
already-shipped sibling `WildAnimals_Greentide.xml`: `PatchOperationConditional` on
`Defs/BiomeDef[defName="RM_Greentide"]/wildPlants`, then `PatchOperationReplace`/`Add` in the
shorthand-dictionary form `<RSW_WroshyrTree>3.0</RSW_WroshyrTree>`. Notes from that file that apply
here unchanged:

- **Shorthand form only.** `<li><plant>` children are read as empty — the item records this costing
  a contradictory measurement.
- **Ours carry no `MayRequire`.** A `MayRequire` on our own def silently loses the row.
- **A patch that matches nothing logs nothing.** A clean `validate_patch.py` is not proof a row landed.
- `WildAnimals_Greentide.xml`'s header already records that *"THE 8 STAR WARS wildPlants"* block is
  deliberately absent and waiting on `DONOR_DEFS_PORT_TO_OURS_1`. **This roster is what unblocks
  it** — the header's stated reason for waiting is that only two of eight had ports. Approving this
  page resolves four of the remaining six.

### 5c. Proposed commonalities

Sums kept in the same range as today's 11-row block (10.2). Canopy rare, mid-storey common,
understory scattered:

```
RSW_WroshyrTree   0.35   (the giant — rare enough to be an event, common enough to see)
RSW_MassassiTree  1.60   RSW_HydenockTree 1.50   RSW_JoganTree  1.20
RSW_Gnarltree     1.00   RUT_Weepbole     0.90   RUT_Stiltkurr  0.80  (river margin only)
RSW_Glowspore     0.60   RSW_VesuvagueTree 0.50  RSW_OrgaBole   0.50
RSW_BafforrTree   0.45   RSW_YerduaSpitter 0.30  RSW_BrylarkTree 0.20  (the hardwood, deliberately scarce)
RSW_GreelTree     0.12   (fastidious, small pure stands)
```

These are **flavour, not a balance pass** — the same posture `TREE_GRAPHICS_OWNERSHIP_1` recorded for
`RUT_SweetlineTree`'s stats. Density is a live-tuning job on the Desktop.

## 6. Open questions for the owner

Five. Everything else on this page was settled from files on disk rather than asked. Q1 is the only
one that blocks building.

### Q1 🔴 "The signature huge tree" — which rung, and what is the Greatbole called?

Your sheet's §7b has three rungs, and **two of them are already built as separate things**: the
fellable giant (placeholder, a Plant) and the Greatbole (`RUT_GreatboleCore`, a Building you mine
into). I have read your ruling as the **middle** rung and proposed `RSW_WroshyrTree` there.

The complication: on the wroshyr's own canon, the tree you live inside *is* a wroshyr — *"Wookiee
settlements consisted of individual tree communities."* So the two rungs may want to be the same
species at two scales, which canon explicitly supports (*"over 1,000 different varieties"*, the
tropical at 300–400 m and the deep-forest variety *"reaching several kilometers"*).

- **(a) One species, two scales** — `RSW_WroshyrTree` falls; `RSW_GreatWroshyr` is the Greatbole.
  The ladder becomes legible in one word, and the Greatbole finally gets a name. *Cost: renaming
  `RUT_GreatboleCore`'s label and touching a shipped map-gen def.*
- **(b) Two species** — the wroshyr falls, the Greatbole is a different tree and needs its own
  bizarre name. *Cost: one more name to invent; ladder reads as three unrelated things.*
- **(c) The Greatbole is the signature and the wroshyr is just the top ordinary tree** — i.e. I have
  read your ruling one rung too low. *Cost: the 13-row roster is unaffected either way; only the
  giant's identity moves.*
- **(d) Something else** — say it and I will re-shape the page.

⚠️ Worth knowing either way: **`RUT_GreatboleCore` currently has no Star Wars name at all** ("greatbole
core"), and it is the most distinctive structure in the campaign. It is the one thing in the Greentide
your *"bizarre Starwars names"* ruling arguably most applies to, and it is out of scope on this item.

### Q2 The bafforr grove-mind — mechanic, or flavour?

Canon hands us this for free: *"A total of seven bafforr trees were required for true sentience.
Below that number, a grove became befuddled, losing its memories,"* and *"the smooth bark hummed
under his touch."*

- **(a) Flavour only** — the description says it, nothing checks it. Costs nothing; ships with the roster.
- **(b) Real** — a grove of ≥7 does something (a mood/inspiration aura, a warning when raiders enter,
  a hum that stops before a predator arrives — which would tie into §9's *"its scariest signal is
  silence"*). *Cost: new C# and its own item; it would not ship with this roster.*
- **(c) Drop bafforr** — it is the most alien thing on the page and the least Greentide-native (Ithor
  is a garden world, not a furnace jungle).

I did not design the mechanic. Inventing one unasked is how a roster question becomes a rule system.

### Q3 What is the Flammability ceiling for Greentide flora?

§6 ban 3 bans "high-Flammability native flora" without a number. Data points: the existing placeholder
giant is **0.5**; `RUT_SweetlineTree` was cut to **0.1** under the arid shrubland's analogous ban.
A single number settles all 14 rows and the placeholder's inheritance at once. Proposed default
**0.10**, with **0.05** on the sap-bleeders (`RUT_Weepbole`) because resin burning would undercut
§4b outright. Say a number, or say "keep 0.5 and I'll tell you if it bothers me."

### Q4 The roster's two edge cases — admit or drop?

Both are honest flags, not hidden problems:

- **`RSW_OrgaBole`** — canon calls orga *"a plant found on the lowest levels of Kashyyyk"*, **not a
  tree**. I gave it a woody bole so it qualifies for a tree roster. Admit it as a tree, or drop it and
  I will invent a 13th?
- **`RSW_UnetiTree`** (not currently on the roster) — canon, *"incredibly rare … mildly
  Force-sensitive"*. A wonderful strange tree, but it drags a Jedi thread into a Jawa scavenger biome.
  In as a one-per-map curiosity, or stays out?

### Q5 Two low-stakes policy calls I did not want to make for you

- **Legends vs canon.** Four rows are Legends-only (vesuvague, bafforr, greel, yerdua). This campaign
  already ships Legends creatures freely (gizka, kinrath, hssiss), so I treated Legends as fine. If
  you want current canon only, those four come out and I owe four replacements.
- **The two naming outliers.** `RSW_Plant_HubbaGourd_Wild` and `RSW_Plant_Chakroot_Wild` keep the
  donor's full name; every other port uses the clean form. I propose the clean form for new rows
  (`RSW_HydenockTree`). Rename the two outliers to match, or leave them?

## 7. UNMEASURED — needs the Windows machine

Authored on the Mac laptop. There is no game, no def dump, no `measure`, and RimSage has never
connected here — so the following are genuinely unknown, not merely unchecked. Each is marked
`UNMEASURED` rather than guessed, per the repo's own rule.

1. **Every vanilla and donor defName I did not read from a file in this repo.** `TreeBase`,
   `RUT_Greenwood`, `RUT_Hardwood`, `RUT_ToxinSealant`, `RUT_GreatboleHeartwood`,
   `RM_FellableTreeExtension`, `CompProperties_CrackFall`, `AB_JungleTree`,
   `Plant_HydenockTree_Wild`, `Plant_JoganTree_Wild`, `Plant_FelucianGlowspore_Wild` and the
   commonality figures were all **read from our own `src/` XML and C#** this session, so they are
   sound. **Nothing else on this page names a vanilla def.** In particular the field names a real
   ThingDef needs beyond what the placeholder already demonstrates (`harvestedThingDef`,
   `immatureGraphicPath`, `sowTags`, `shadowData`) are **UNMEASURED** — copy them from a live
   sibling, do not take them from this document.
2. **`TreeBase`'s default `Flammability`** — UNMEASURED. Q3 cannot be answered numerically against
   vanilla from here.
3. **What the four donor tree defs actually do.** Their yields, `growDays`, harvest products,
   `visualSizeRange`, any comps, and whether any carries behaviour a port must reproduce — all
   **UNMEASURED**. This is the only real risk in §5's "nothing is lost": a donor tree with a comp
   nobody noticed would be lost silently. **Dump all four before authoring their replacements.**
4. **Whether the four reusable art subjects' PNGs are on disk at all, and at what real resolution.**
   `done/*.json` records a requested canvas of 256×256 and `registry.jsonl` has **zero** entries for
   these ids; the actual files were not located from this machine. Confirm with
   `validate_sprite.py --describe` before assuming the re-render in §3c/§4c is only a re-render.
5. **Does `wildPlants` on `RM_Greentide` accept our defs at all.** The patch shape is copied from a
   sibling that is itself marked *"🔴 UNVERIFIED AGAINST A LOAD"* in its own header. A post-load def
   dump is the only proof any row landed.
6. **Whether 14 tree rows is too many for one map to read.** §9's silhouette language wants *"vertical
   giants and Greatbole towers"* to dominate; fourteen species at one density could turn that into
   noise. This is a **look-at-it** judgement on a live map, not a spreadsheet one — and per the
   repo's save-game rule it should ship as a savegame he can walk, on one map, with a grid key.
7. **The `RM_Greentide` vanilla-floor question is untouched and still unruled** — the item says so
   explicitly. Whether that generic fallback's two temperate trees should become vanilla *tropical*
   ones is a separate, smaller ticket. Nothing on this page changes `RM_Greentide`'s own `wildPlants`.

---

## Provenance

- Canon text: `curl` to `https://starwars.fandom.com/api.php?action=parse&page=<Page>&format=json&prop=wikitext`
  — the route `design/RimStarWars/canon_references/AGENT_BRIEF.md` prescribes. HTTP 200 on
  `Wroshyr_tree`, `Brylark_tree`, `Gnarltree`, `Massassi_tree`, `Syren_plant`, `Bafforr_tree`,
  `Vesuvague_tree`, `Greel_tree`, `Blba_tree`, `Hydenock`, `Orga`, `Uneti_tree`, `Nysillin`,
  `Yerdua_poison-spitter`, `Knobby_white_spider`, `Woolamander`. `Orga_plant` 404s — the page is `Orga`.
- Repo facts: `src/RimUtinni/UtinniPatches/` (BiomeDefs, Patches, ThingDefs_Plants, ThingDefs_Buildings),
  `src/RimMandrake/EnvironmentalHazards/Source/`, `src/RimStarWars/SWBestiary/Defs/DesertPort/`,
  `infrastructure/artpipe/done/`, `infrastructure/artpipe/registry.jsonl`, `Transient/port_*.decisions.json`.
- Design authority: `infrastructure/state/items/GREENTIDE_JUNGLE_TREE_ROSTER_1.md`,
  `infrastructure/state/items/TREE_GRAPHICS_OWNERSHIP_1.md`,
  `design/Jawa/worldbuilding/biomes/the_greentide.md`.
- ⛔ No claim on this page is live-proven. There is no game and no def dump on this machine.
