# The Fever Wood flora roster — 18 invented plants, 2026-09-23

_MACBENCH, authored against the owner's rulings of 2026-09-23
(`fever_wood_deep_and_mud_2026-09-23.md`) and the frozen sheet
(`the_fever_wood.md`). Companion to `greentide_tree_roster_2026-09-22.md`, which is
the sibling wetland's roster and the format this copies._

---

## READ FIRST — every plant on this page is OURS and INVENTED

**Owner's standing instruction, 2026-09-23:**

> *"we should just invent our own complete roster of fauna, flora, etc. that make it a
> rich place THEN look for Star Wars specific injection opportunistically (as long as it
> makes sense, not trying to inject any-old-thing just because it's not obviously wrong)."*

⇒ Every row here is **`RM_` tier — franchise-free, invented, and cast inline.** Under
`biome_mod_architecture.md` **Q11a**, an invented exotic name is *not* Star Wars IP even
when it sounds alien, so it lives in the free mod and the free mod is **rich on its own**.
Canon injections are a **separate section at the end** (§6) and are additive — they never
substitute for a row here.

🔴 **These 18 REPLACE the 7 donor rows currently on `RUT_FeverWood`.** What ships today is
5 Alpha Biomes plants, 3 genuine canon Star Wars plants, and one ported stopgap — including
`AB_KeeningCordax`, whose own roster note calls it an *"interim single-tile body for the
tower-trunks."* A single-tile shrub is standing in for towers *"much more than one tile
wide"* (§1 of the sheet). ⛔ They are placeholders to replace, not a base to extend.

⛔ **No name here collides with the Greentide's 22.** Checked against that roster's own
defName list this pass.

### The silhouette brief is the specification

Same rule as the sibling roster: the **silhouette FORM** column is what art is commissioned
against and what a reviewer grades. A row whose form duplicates another row's has failed,
because the player must be able to name a plant at a glance from a top-down sprite.

---

## At a glance

The Fever Wood's layers are **not** the Greentide's canopy/mid/understory. This biome's
frame is vertical and only one half is inhabited (`the_fever_wood.md` §7b: *"the crown
versus the water"*), so the roster is organised by **height above the water**:

| the giants (towers) | the crown (on bough-soil) | the pool margin | the ground (thin) |
|---|---|---|---|
| **thulvane** — the fused tower | **plennith** — makes the crown's soil | **claithe** — binds the potter's clay | **skimmel** — hides the sink-mud |
| **skethral** — grows the roads | **ossagrel** — bleeds the sugar the herds drink | **corvath** — grows only where it has fed | **wanlith** — the pale one |
| **varnoth** — stands in the water | **cistrel** — the only safe water | **sodderel** — the bog-timber | **tullick** — the tuber |
| | **maulith** — a room with walls | **seepril** — sits in the oil | |
| | **verrow** — the crown's fruit | | |
| | **nubrith** — the only light | | |
| | **halquin** — the medicine | | |
| | **ammeth** — the roof panels | | |

---

## 1. The rulings this roster serves

| ruling | source | what the roster owes it |
|---|---|---|
| **Crown flora grows on a fertile bough-soil terrain** | owner, 2026-09-23 §6b | the crown layer exists at all — and ⭐ **one row MAKES that soil** |
| **Trunks are destructible but cannot fall; you mine through them** | owner, verbatim §6a | 🔴 **no row on this page falls.** There is no fall event in this biome |
| **Three sap-suckers with three defences** | owner, ruled §6 | a **host plant** they drink from — the guild is otherwise unfed |
| **Reach scales with pool size; mud only kills near water** | owner, §3 / §2b | the margin rows are the *reason* to enter reach, and one ground row **disguises** the mud |
| **The pools' treasure is a renewing trickle** | owner, §2 | the margin is worth working, so its plants are worth authoring |
| **Nothing goes in the water here** | sheet §5, §6 ban | ⭐ **the crown holds the only drinkable water** |
| **The ground is dim, wet, quiet and mostly empty** | sheet §3 | the ground layer is deliberately only **3 rows** — thinness is the doctrine, not a gap |
| **No fungal miracle; no rain; no vanilla-Earth flora** | sheet §6 bans 5, 7 | zero fungi, zero Earth-nameable plants |

---

## 2. The giants — three towers. None of them falls.

Multi-tile. `RUT_FeverTrunkHeartwood` already ships as the mineable body and
`RUT_FeverTrunkCore` as its bookkeeping marker; these three rows are the **living species**
that body belongs to, differentiated by what each one does with its crown.

| # | defName | label | silhouette FORM | what it looks like | cells | job | art |
|---|---|---|---|---|---|---|---|
| 1 | `RM_Thulvane` | thulvane | **colossal fused column, crown lost overhead** | A grey-green column so broad its base reads as several trunks grown together, rising past the top of the frame so **you never see its crown from the ground** — the canopy is simply a permanent green ceiling. Bark in wet vertical plates, black in the grooves, permanently damp. | **16** | 🔑 **The biome's structural unit.** The ceiling, the interlock that makes nothing able to fall, and the body you mine rooms into. Bore-caves are cut from this. | **OWED** — the largest canvas here |
| 2 | `RM_Skethral` | skethral | **arch-thrower — boughs reaching sideways, not up** | Shorter and wider than a thulvane, and visibly *reaching*: its heavy limbs grow horizontally toward its neighbours and **fuse where they meet**, so two skethrals read as one arch. Bark smooth and pale at the joins, scarred where limbs have knitted. | **12** | ⭐ **This is the tree that grows the roads.** The boughway network anchors on it, and it is the in-fiction reason the crown is interlocked — i.e. the reason §6a's ruling is true. | **OWED** |
| 3 | `RM_Varnoth` | varnoth | **stilt-tripod standing in black water** | Rooted **in a mirror pool itself**, on a tripod of prop-roots clear of the surface, trunk leaning out over the water. Its lower bark is stained and polished to a wet black by the pool. Nothing grows beneath it. | **9** | 🔴 **The bravest harvest on the map.** Its timber is the best in the biome — and it stands inside the reach. ⇒ Reward and hazard are the same object, in the pools' key. | **OWED** |

⚠️ **All three are `Graphic_Single` mineable bodies today**, so they have no edge-vs-interior
distinction — the same defect `GREATBOLE_BARK_EDGE_ART_1` records for the sibling biome's
blob. A tower whose outer cells do not read as *bark* will look like painted rock.

---

## 3. The crown — eight plants on bough-soil. The biome actually lives here.

🔴 **This whole layer is blocked until bough-soil exists** (§6b): `RUT_Boughway` ships
`fertility 0`, so nothing can root in the crown as built.

| # | defName | label | silhouette FORM | what it looks like | cells | job | art |
|---|---|---|---|---|---|---|---|
| 4 | `RM_Plennith` | plennith | **flat spreading mat, no vertical element at all** | A dense low mat of overlapping grey-green scales lying directly along bark and bough, thickening into a spongy bed that visibly **holds silt and rot**. Reads as a *surface*, never as a plant. | 1 (spreads) | ⭐ 🔑 **It MAKES the bough-soil.** The crown's fertility is biological, not geological — where plennith has run, things can grow. ⇒ The one row that explains the whole layer, and the right anchor for the bough-soil genstep pass. | **OWED** |
| 5 | `RM_Ossagrel` | ossagrel | **swollen jointed cane weeping at every node** | A thick segmented cane clamped along a bough, each joint swollen and split, weeping clear syrup that glazes and crusts below it. The whole plant looks *over-full*, and the bark under it is sugared and crawling. | 3 | 🔴 ⭐ **The host the sap-suckers drink from.** All three of the owner's ruled sap-suckers clamp to this — without it the guild has no food and the nectar economy has no source. Also the sugar line for stills and nectar-liquor. | **OWED** |
| 6 | `RM_Cistrel` | cistrel | **upright ring of leaves holding a visible pool** | A tight rosette of stiff waxy leaves forming a cup at chest height, **holding clear standing water you can see into** — the only water on this map that is not black. Outer leaves rust-red, inner pale. | 2 | ⭐ 🔑 **The only safe water in the Fever Wood.** The ground water kills; this is where people and tame animals drink. ⇒ It converts the biome's central prohibition into a positive resource, and makes a crown holding worth defending. | **OWED** |
| 7 | `RM_Maulith` | maulith | **hanging curtain to the boughway deck** | A crossbeam of stiff branches carrying a dense curtain of flat ribbon-leaves that falls to the walkway below, so the plant is **a room with walls**. Leaves olive above, silver-backed and always moving slightly. | 5 | **The concealment plant of the crown**, and the boughway's privacy screen. You cannot see into or out of one — which is what makes the crown ambushable despite ban 3 forbidding native chase predators. Ribbon-leaf is cordage. | **OWED** |
| 8 | `RM_Verrow` | verrow | **pendant gourds under a sparse frond crown** | Few fronds, held high and thin, with heavy dull-skinned gourds hanging well below them on long stalks — the fruit is the visual mass, not the leaves. | 4 | **The crown's staple food**, reachable from a boughway without climbing. Free calories that draw the crown's grazers, and then the things that wait for grazers. | **OWED** |
| 9 | `RM_Nubrith` | nubrith | **domed cap glowing from beneath, on a short thick stalk** | A low leathery dome on a squat stalk, glowing a steady warm amber **downward onto the deck** — deliberately warm, to sit beside the Wildsteam's steam-lamp gold rather than fight it. | 3 | 🔑 **The only natural light in the crown**, and it must not read as fungal — ban 5 reserves the fungal register for the Rot. It is a leaf that glows, not a mushroom. | **OWED** |
| 10 | `RM_Halquin` | halquin | **paired blades splayed flat against bark** | Two broad blade-leaves lying flat and opposite against the trunk like a pressed specimen, dark and leathery, with a swollen joint between them that beads resin. | 2 | **The medicine.** The resin is the biome's herbal medicine line, gathered by scraping — a safe, patient, crown-side income. The roster needs one wholly benign row and this is it. | **OWED** |
| 11 | `RM_Ammeth` | ammeth | **single rigid fan in one plane** | One stiff flat fan of fused leaf held in a single plane from a short base, so it reads as **a panel from one side and a line edge-on** — the only row whose silhouette changes with facing. Waxy, rain-shedding, pale underneath. | 3 | **Roofing and decking.** The cheapest building material in the biome, and the thing stilt-and-bough architecture is actually made of. Cut, never felled. | **OWED** |

---

## 4. The pool margin — four plants. This is where the danger is worth it.

The margin already carried three economies before this sitting — **bog-timber, potter's clay,
and the seep-oils** (sheet §7) — and the owner's 2026-09-23 ruling added the beast's
**treasure trickle** as a fourth. These four rows are what makes standing inside the reach
pay.

| # | defName | label | silhouette FORM | what it looks like | cells | job | art |
|---|---|---|---|---|---|---|---|
| 12 | `RM_Claithe` | claithe | **low rosette with visible pale root-plate** | A flat rosette of blunt grey leaves over a broad pale root-plate that lifts clear of the mud, **caked in grey clay** it has bound out of the water. | 2 | **The potter's clay is harvested from its root-plate** (sheet §7). Turns a raw-terrain resource into a plant you can find, judge and farm — at the water's edge. | **OWED** |
| 13 | `RM_Corvath` | corvath | **gorged dark spike, singular, never in patches** | A single thick dark-purple spike standing alone out of the mud, glossy and swollen, obviously **better fed than anything around it**. Always solitary. Never more than a few at one pool. | 1 | ⭐ 🔴 **The indicator plant — it grows only where the thing below has fed.** A pool ringed with corvath is an occupied pool. ⇒ This is the environmental tell that makes the pools *readable* rather than an unfair coin-flip, and it is the botanical companion to the town's pool-list. **Do not make it edible or valuable** — its whole worth is as information. | **OWED** |
| 14 | `RM_Sodderel` | sodderel | **leaning waterlogged spar, half-dead by nature** | A lopsided spar of a tree, half its limbs already dead and black with water, leaning permanently toward the pool. Living growth only on the high side. It looks like a wreck and is not one. | 5 | **The bog-timber** (sheet §7): the biome's ordinary construction wood, since the towers cannot be felled and varnoth is lethal to reach. ⚠️ Must read as *naturally* half-dead, or players will think it is diseased. | **OWED** |
| 15 | `RM_Seepril` | seepril | **squat barrel ringed by an oil sheen** | A low dull barrel of a stem sitting in its own iridescent slick, the rainbow film spreading a cell or two around its base. Leafless above; just the barrel and the sheen. | 2 | **The seep-oils** (sheet §7) gather around it — perfume, lubricant, fuel. 🔑 Its rainbow is one of the planet's rainbow registers and must stay the *honest* one: the Miasma's blooms are beauty, the Scarlands' pools lie, and this is *just oil, just useful*. | **OWED** |

✅ **RESOLVED 2026-09-23 — `RM_Seepril` owns the seep-oils.** Decision taken by question card:
they are **a plant you harvest**. ⛔ `LIQUID_TYPES_MOD_1` does **not** own them, despite being
named as their owner in the frozen sheet's cross-flow ledger — that pointer is superseded. ⛔ The
terrain-feature route was offered and declined. Accepted cost: seepage stops being a property of
the ground; the compensation is that the oils become findable and farmable at the margin.

---

## 5. The ground — three plants, and thinness is the point

`animalDensity` 2.3 and a dim, wet, quiet, *mostly empty* floor are doctrine (sheet §0, §3).
⛔ **Do not expand this layer to match the crown.** Three rows is the design.

| # | defName | label | silhouette FORM | what it looks like | cells | job | art |
|---|---|---|---|---|---|---|---|
| 16 | `RM_Skimmel` | skimmel | **unbroken flat skin across the mud** | A continuous pale-green film lying perfectly flat over the mud, **indistinguishable from firm ground until it is stepped on**. Its only tell is that it is *too even* — no texture, no debris, and it never grows on ground that is actually solid. | 1 (spreads) | 🔴 ⭐ **It disguises the sink-mud.** The mud ruling (§3) needs a visual tell a player can learn, and this is it — a skimmel sheet means the mud beneath will catch you. ⇒ Learning to read it is the skill the ground level teaches. | **OWED** |
| 17 | `RM_Wanlith` | wanlith | **thin bleached stalks in loose stands** | Sparse colourless stalks a knee high, translucent and unbranched, standing in loose groups. Almost no biomass. Reads as *absence* — the visual proof that the floor is starved of light. | 1 | **The floor's baseline cover**, and the row that makes the ground read as empty rather than unfinished. Deliberately worth almost nothing. | **OWED** |
| 18 | `RM_Tullick` | tullick | **squat whorl over a buried swelling** | A tight low whorl of dull ribbed leaves with the ground visibly domed beneath it by the tuber below. | 2 | **The ground's one real reward** — a bulk starch for the people working the causeway, who the sheet calls *"the brave and the poor."* Digging it churns the mud around it, which is an honest small cost. | **OWED** |

---

## 6. Star Wars injection — opportunistic, and only where it earns the slot

Per the owner's method: ours first, canon **added** afterward where it genuinely fits. These
ride the campaign patch layer (`UtinniPatches/Patches/WildPlants_*`), never the `RM_` tier.

| candidate | canon status | why it earns a slot here | verdict |
|---|---|---|---|
| **Dianoga's Kiss** | ✅ **SOURCED** — a canon *"species of brown tentacled plant"* on Balnab, growing alongside umbrella trees. Named in *The Visual Encyclopedia* (2017); see `canon_references/dianoga/description.md` §expansion | 🔑 A **tentacled plant at the water's edge of a biome whose god is a tentacled thing.** It rhymes with the pools without explaining them, and its canon name literally invokes the creature. The single best injection available to this biome. | ⭐ **RECOMMEND** — margin layer, low commonality |
| `Plant_HydenockTree_Wild` | canon SW; **currently shipped on this biome at 1.5** | A wroshyr-analog crown tree, and the sheet's §4/§8 Wookiee canton works exactly that. Genuine fit — but it is currently doing the work `RM_Thulvane` should do. | **KEEP, demote** — additive crown flavour, not the structural tower |
| `Plant_JoganTree_Wild` | canon SW; currently shipped at 0.6 | Crown fruit, which the biome wants. Overlaps `RM_Verrow`'s job. | **KEEP at low commonality** — a second fruit is fine; it must not replace verrow |
| `Plant_Chakroot_Wild` | canon SW; currently shipped at 0.4 | A root plant read as a water-table feeder. Overlaps `RM_Tullick`. | **KEEP at low commonality** |
| the 5 `AB_*` donor rows | donor, not canon | They are generic alien filler and three of them are groundcover, which the ground layer now supplies deliberately. | ⛔ **CUT** — replaced by §5 |

⚠️ **One sourcing discipline note.** `canon_references/` holds 137 entries **by design**, so
absence from it proves nothing about canonicity — and a donor mod's own defName is **not** a
source. Any further injection must be verified through the search API
(`action=query&list=search&srsearch=`), never a guessed page title, which returns MISSING for
real subjects constantly.

---

## 7. The legibility matrix — the acceptance test for this roster

Every form must be nameable from a top-down sprite at display size. A duplicated row here is
a failed roster.

| form | row | reads as |
|---|---|---|
| colossal fused column, crown out of frame | thulvane | a building that is alive |
| limbs reaching sideways and fusing | skethral | an arch, or a bridge under construction |
| stilt tripod in black water | varnoth | a pier you must not walk to |
| flat spreading scale mat | plennith | a surface, not a plant |
| swollen jointed weeping cane | ossagrel | a leaking pipe |
| upright leaf-ring holding clear water | cistrel | a cup |
| hanging ribbon curtain to the deck | maulith | a curtained doorway |
| pendant gourds under sparse fronds | verrow | fruit on a bare frame |
| glowing downward dome | nubrith | a lamp |
| paired blades flat on bark | halquin | a pressed specimen |
| single rigid fan, one plane | ammeth | a panel — and a line edge-on |
| rosette over a clay-caked root-plate | claithe | a dug-up thing |
| solitary gorged dark spike | corvath | a grave marker |
| leaning half-dead waterlogged spar | sodderel | a wreck |
| squat barrel in a rainbow slick | seepril | a spill |
| unbroken flat skin over mud | skimmel | **firm ground — which is the lie** |
| thin bleached stalks | wanlith | starvation |
| squat whorl over a domed tuber | tullick | something buried |

🔑 **Two rows are deliberately deceptive** and the matrix records it on purpose: **skimmel**
must read as safe ground, and **sodderel** must read as already dead. Both are traps for the
eye, and an art pass that "fixes" either has broken the design.

---

## 8. What is owed

- 🔴 **All 18 need art.** Nothing on this page exists as a sprite. ⚠️ Before any of it is
  queued, **search `infrastructure/artpipe/done/`, `_artsrc/` and any review sheet's
  `.decisions.json` by subject** — finished, already-ruled art has sat unused here for days
  at a time, and three Greentide plants were nearly regenerated on top of validated art on
  2026-09-20.
- 🔴 **The crown layer is blocked on bough-soil** (§6b) — a fertile terrain painted by
  `RM_GenStep_RootCauseways`' existing `additionalPasses` field. Eight of these 18 rows
  cannot grow until it exists.
- **Free-tier commonalities and `growDays`** — every number here is a slot, not a value.
- **The 7 donor rows on `RUT_FeverWood` are not removed by this document.** Replacing them is
  a def-editing pass, and `BIOME_PAINT_ONCE_AT_THE_END_1` governs anything touching the
  live biome def.
- ⛔ **No fall behaviour on any row.** If a later pass reaches for
  `RM_FellableTreeExtension` or `RM_CompCrackFall` here, it has misread §6a.
