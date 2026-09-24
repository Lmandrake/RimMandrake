# The Webwork — invented flora roster

_Owner + BENCH, 2026-09-23 sitting; drafted by a Fable design subagent against the frozen sheet._

**Status: DESIGN PROPOSAL. Nothing authored.**

## READ FIRST — every plant on this page is OURS and INVENTED

**Owner's standing instruction, 2026-09-23** (quoted first in
`fever_wood_flora_roster_2026-09-23.md` READ FIRST, binding here the same way):

> *"we should just invent our own complete roster of fauna, flora, etc. that make it a
> rich place THEN look for Star Wars specific injection opportunistically (as long as it
> makes sense, not trying to inject any-old-thing just because it's not obviously wrong)."*

⇒ Every row here is **`RM_` tier — franchise-free, invented, and cast inline.** Under
`biome_mod_architecture.md` **Q11a**, an invented exotic name is *not* Star Wars IP even
when it sounds alien, so it lives in the free mod and the free mod is **rich on its own**.
Canon injection is a **separate section at the end** (§8) and is additive — it never
substitutes for a row here.

🔴 **These 16 REPLACE the 7 donor rows currently on `RUT_Webwork`** (dispositions
PROPOSED in §7, executed by nobody here). What ships today is 4 Alpha Biomes plants, one
Regrowth chokevine, and one genuine canon Star Wars plant — a donor tree standing in for
the thicket that drank a river. ⛔ They are placeholders to replace, not a base to extend.

This roster is a companion to `webwork_owner_and_nest_2026-09-23.md` (the sitting record —
its §0 rulings govern here) and `webwork_fauna_roster_2026-09-23.md` (same sitting, same
naming register). Rows this record already cites by name and which therefore exist here
exactly as cited: **`RM_Kollavane`** (§2 row 1 — the nest is woven from its young masses),
**`RM_Ruddreth`** (§5 row 13 — the nest-bloom), **`RM_Kessaroth`** (§4 row 9 — the free
tier's snap-trap, §8).

### The silhouette brief is the specification

Same rule as the sibling rosters: the **silhouette FORM** column is what art is
commissioned against and what a reviewer grades. A row whose form duplicates another
row's has failed, because the player must be able to name a plant at a glance from a
top-down sprite.

---

## At a glance

The Webwork's frame is not vertical layers — it is **one organism of shade** (sheet §3):
a thicket that drank its river, the plumbing that moves the stolen water, the nightmare
plants the thicket is made of, and the white half that traces the web. The roster is
organised by which part of the organism each row is:

| the thicket (green) | the plumbing (the stolen river) | the nightmare plants | the white half and the margin |
|---|---|---|---|
| **kollavane** — the churn-tree, the thicket's body | **threllick** — the root-mat that drank the river | **kessaroth** — the snap-trap | **pellareth** — the pale flowers that trace the web |
| **vessark** — the strangler the thicket fights | **sellith** — lines the silk gutters | **norrveth** — casts needles | **ruddreth** — blooms only on hide-rot |
| **tavrosk** — the still-tree the Wildsteam tap | **varrisk** — the reach, jungle without rain | **sorrivel** — the spider's bait | **fellome** — the plantation's gleanings |
| **dulloth** — seals the canopy shut | | | **grennick** — the creep made visible |
| **brimlock** — the river, held in flesh | | | **brennoth** — the margin's tinder |

---

## 1. The rulings this roster serves

| ruling | source | what the roster owes it |
|---|---|---|
| **The thicket drank its river; the water is inside** | sheet §1, §5; §0 MEASURED: 0 river tiles, 0 water tiles | ⭐ the plumbing layer exists at all — the root-mat, the gutter-weed, and one row that **holds the river in its flesh** |
| **The thicket churns against itself; paths are temporary** | sheet §4c (`EXPLOSIVE_PLANT_GROWTH_1` in self-consuming mode) | the thicket layer's rows are churn participants, not scenery — and the churn is why timber exists without felling a living wall |
| **The pale flowers follow the web's architecture** | sheet §4c; roster JSON `new_defs` row 2 | `RM_Pellareth` — fresh blooms mean an active line, withered means the safe path |
| **The nest is woven from young trees and read at a distance by its colour** | sitting record §3a | `RM_Kollavane` (the young masses) and `RM_Ruddreth` (the ring of rust-red on hide-rot) |
| **A parasitic root-mat is the stolen river's plumbing** | sheet §3; roster JSON `new_defs` row 4 | `RM_Threllick` — and the donor's movementDifficulty 2 becomes *walking on the plumbing* |
| **The still-burners are fueled by liquors and oils tapped from the trees** | sheet §7 | `RM_Tavrosk` — tap the jungle's trees to burn the jungle's owner |
| **Fire is architecture; the light-moat maintains itself only as long as you do** | sheet §7b | `RM_Grennick` (regrowth working against you) and `RM_Brennoth` (the fuel that makes a burn-ring cheap — and wild fire fast) |
| **The spiders sow as they hunt — this is a plantation** | sheet §3, §4c | `RM_Fellome` and `RM_Sorrivel` — forageability 1.0 is *gleaning someone's fields*, and one plant is openly on the owner's side |
| **No vanilla-Earth flora; no surface water; no safe dense-canopy cell** | sheet §6 bans 3, 6; §5 | zero Earth-nameable rows; nothing here is a pond; `RM_Dulloth` is the *reason* the canopy is total, and no row makes covered ground safe |
| **Silence is doctrine — the free mod must be rich alone** | §0 ruling 5 register; Q11a | 16 rows is a full flora with no donor and no canon needed |

## Rows — sixteen plants in four registers

### 2. The thicket — the green half of the hellscape (5 rows)

The thicket is not a forest; it is a wall that grew inward until it drank its own river.
Everything in this register participates in the churn.

| # | defName | label | silhouette FORM | what it looks like | job | mechanism | art |
|---|---|---|---|---|---|---|---|
| 1 | `RM_Kollavane` | kollavane | **braided column of many young trunks grown as one** | Not one tree but a standing braid of dozens — pale green whips fused into a dark trunk, new shoots erupting from the base while the crown's older wood dies black. It is visibly *several ages at once*. | 🔑 **The thicket's body and its unit of churn.** THE canopy tree; the young whip-masses are what the nest is woven from (sitting record §3a); its churn-dead wood is the biome's only timber — you never fell a living one, you salvage what the braid discarded. | churn engine (`EXPLOSIVE_PLANT_GROWTH_1`, self-consuming mode) | **OWED** — the biggest canvas here |
| 2 | `RM_Vessark` | vessark | **thick coiling cable wrapped visibly AROUND other rows** | A muscular grey-green cable as thick as a leg, coiled around kollavane braids and around its own kind, bark scarred where it constricts. Never freestanding — it is always *on* something. | **The churn made legible.** The strangler the thicket fights; where vessark wins, a braid dies and a gap opens; where it loses, a path closes. It is why "paths are temporary" reads on screen. | churn engine | **OWED** |
| 3 | `RM_Tavrosk` | tavrosk | **swollen bottle-bole under a thin ragged crown** | A squat tree that is mostly trunk — a glossy, distended bole streaked with dried amber runs where old taps wept, under a mean little crown. It looks *kept*, like a barrel someone owns. | ⭐ **The still-tree.** Its sweet volatile sap is the Wildsteam's liquor-fuel line (sheet §7): one tapped item that is drink, trade good and still-burner fuel. Tap the jungle's trees to burn the jungle's owner. | tap/harvest recipe; fuel-item wiring rides the Wildsteam kit | **OWED** |
| 4 | `RM_Dulloth` | dulloth | **flat black-green leaf-panes held horizontally, edge to edge** | Broad rigid leaves the size of doors, held flat and level, meeting neighbouring dulloth pane-to-pane with almost no gap. From below it is a ceiling; from above, a sealed floor of dark green. | 🔴 **The canopy sealer — the reason the gloom is total.** It is the *mechanism* of "dim green gloom under total canopy" (sheet §9), and cutting dulloth is how a clearing is made: the light-moat begins with felling these. ⛔ It never generates a *safe* covered cell (ban 6). | none beyond growth; the light-moat interacts by its removal | **OWED** |
| 5 | `RM_Brimlock` | brimlock | **taut, veined bladder-trunk, visibly full** | A leaning trunk swollen into a drum-tight bladder, its skin stretched and traced with dark water-veins, faintly translucent where the sun ever reaches it. It audibly sloshes when struck. | ⭐ 🔑 **The drunk river, held in flesh.** Cut one and water runs out — the only water a traveller will find in 161 tiles of jungle (sheet §0: 0 water tiles; §1: the water is *inside* — this row makes that literally true at map scale). The spill draws churn regrowth to the cut. | harvest-for-water job; spill triggers a local churn pulse | **OWED** |

---

### 3. The plumbing — the stolen river (3 rows)

Half the biome gets zero rain and is jungle anyway (sheet §0). These three rows are how.

| # | defName | label | silhouette FORM | what it looks like | job | mechanism | art |
|---|---|---|---|---|---|---|---|
| 6 | `RM_Threllick` | threllick | **surface-running root lattice, no upright part at all** | A dense mat of interlaced surface roots, grey-brown and slick, running in visible strands between the thicket's trunks. It is the *ground* over most of the biome — you walk on it, and it is why walking is hard. | 🔑 **The parasitic root-mat — the stolen river's first plumbing** (sheet §3; roster JSON `new_defs` row 4). Shared, or stolen rather: every plant here is plumbed into it. The donor's movementDifficulty 2 stops being arbitrary — you are walking on pipework. | terrain-adjacent groundcover; the biome's movement cost is its fiction | **OWED** |
| 7 | `RM_Sellith` | sellith | **pale fringe hanging in a LINE, never a patch** | A pale green weed that grows only along the silk irrigation gutters, rooted into the drip, hanging in neat fringes under the lines. Its shape is the web's shape — it never occurs except in runs. | **The gutter-weed.** It maps the spiders' irrigation at a glance: a sellith run overhead means a live gutter, means stolen water moving. The botanical half of the web's own geometry (sheet §9: catenary lines, gutter-runs). | placement follows silk Things (`GenStep_ScatterWebworkSilk` scatter + web-line adjacency) | **OWED** |
| 8 | `RM_Varrisk` | varrisk | **stiff knee-high sedge in drilled, regular stands** | A dull green sedge standing in oddly *even* stands — spaced, aligned, unmistakably planted rather than grown. Dry-country foliage, waxed against the heat. | **The reach.** The irrigated lowland cover at the end of the plumbing: the jungle the zero-rain tiles carry. Where varrisk stands, silk water reaches; where it stops, the desert has won. The biome's outer boundary is drawn in this plant. | grows only within the irrigation footprint | **OWED** |

---

### 4. The nightmare plants (3 rows)

Sheet §1: *"a thicket of terrible, nightmare plants ever churning against itself."* Three
hostilities, three mechanisms — and one of them is on the owner's side.

| # | defName | label | silhouette FORM | what it looks like | job | mechanism | art |
|---|---|---|---|---|---|---|---|
| 9 | `RM_Kessaroth` | kessaroth | **paired toothed jaws held open at knee height** | A low plant that is mostly trap: two ribbed, in-curved jaw-leaves held sprung and open, dull green outside, bone-pale within — the biome's palette in a mouth. A swallowed bulge shows in the stem of a fed one. | 🔴 **The free tier's snap-trap** (sitting record §6 item 8). It bites what steps in it — pinning damage, not death; in this biome being *held* is the death. The canon `Plant_TookeTrap_Wild` injects over it, additively, under Utinni (§8). | snap-trigger on pawn entry; brief immobilize | **OWED** |
| 10 | `RM_Norrveth` | norrveth | **bare upright wand ringed with glassy spikes** | A leafless dark wand, chest high, ringed at intervals with collars of translucent needle-spikes that shiver when anything passes. Spent collars leave bare rings — a norrveth's history is written on its stem. | **The needle-cast.** Disturbed, it flings a collar of glassy needles — a short-range fragmentation hazard that punishes pushing through the thicket off the paths. The reason "the churn opens a gap" is not automatically an invitation. | proximity-triggered needle burst (small ranged verb on the plant) | **OWED** |
| 11 | `RM_Sorrivel` | sorrivel | **drooping dark bell on a bowed stalk, glistening** | A single heavy bell-flower, wine-dark and wet-looking, bowed to head height on a bent stalk, dripping a syrup whose sweetness carries absurdly far. Nothing about it is pale. | 🔑 **The bait — the plant that is openly on the owner's side.** Its scent draws animals in, and it grows where the web is thickest: the plantation's lure crop, sown by the spiders themselves (sheet §4c — they sow as they hunt). A sorrivel in bloom means you are standing in a larder. ⛔ Do not make it valuable; its worth is as a warning to whoever knows it. | scent-lure job on wild herbivores toward web-line cells | **OWED** |

---

### 5. The white half and the margin (5 rows)

The palette is the map (sheet §4c, §9): dead white silk, bone-white blooms, the red-brown
of the nests — and at the edges, the front.

| # | defName | label | silhouette FORM | what it looks like | job | mechanism | art |
|---|---|---|---|---|---|---|---|
| 12 | `RM_Pellareth` | pellareth | **tall bone-white bloom cluster, faintly luminous** | Great strangely pale flowers on grey stalks, bone-white and slightly glowing in the gloom, growing in runs and arcs that are never random — the white traces the web. Withered heads go grey and papery but stand. | 🔴 ⭐ **The pale flowers of sheet §4c, and the biome's map.** Fresh blooms mean an active line; withered runs mean abandoned web and the safe path. The one row every player must learn to read, and the route-lights of the art brief (sheet §9). | placement follows web architecture; fresh/withered state as route-signal (roster JSON `new_defs` row 2 — the state machine is the build's one novelty) | **OWED** |
| 13 | `RM_Ruddreth` | ruddreth | **low rust-red rosette on visibly foul ground** | A squat rosette of rust-red blooms — the only warm colour in the biome — growing in a ring on darkened, grease-stained ground. It is never anywhere clean. | 🔑 **The nest-bloom** (sitting record §3a): it grows only on hide-rot, so a ring of ruddreth is a nest read at a distance, before you see a single silk Thing. Information, like the Fever Wood's corvath — ⛔ not edible, not valuable. | placement keyed to nest-cluster Things (`RM_Webwork_HideMass`) | **OWED** |
| 14 | `RM_Fellome` | fellome | **hanging strings of plump bone-white pods** | Strings of fat pale pods hanging from a modest scrambling vine, heaviest along the web-lines where the pollen-dusted owners pass. The pods are dusty with sticky pollen. | **The plantation's gleanings — forageability 1.0 made honest.** The spiders sow as they hunt (sheet §4c), and fellome is the accidental crop: good calories, everywhere, free. ⇒ Foraging the Webwork is gleaning someone's fields, on their silk, under their sense. | none; density biased toward web-line cells | **OWED** |
| 15 | `RM_Grennick` | grennick | **low advancing turf with one hard, visible EDGE** | A dense dark turf whose leading edge is abrupt — a clean line of new green over burned or open ground, visibly further along every time you look. Behind the line, threllick and the thicket follow. | 🔴 **The creep made visible.** The margin's advancing front (sheet §8) as a plant: `RM_MapComponent_FrontCreep` is already shipped and live-verified, and grennick is its groundcover — the thing that regrows into an untrimmed light-moat (sheet §7b: the moat maintains itself only as long as you do). | front-creep MapComponent (shipped); grows on the advancing margin | **OWED** |
| 16 | `RM_Brennoth` | brennoth | **dry contorted scrub, resin-varnished, half dead** | A knotted waist-high scrub of the margins and clearings, varnish-shiny with dry resin, always carrying dead grey wood among the live. It looks like kindling because it is. | **The margin's tinder.** It burns hot, fast and clean — the fuel that makes a burn-ring cheap to cut and keep (fire is architecture, sheet §7b) and the reason a careless fire at the margin runs. Reward and hazard in one flammability stat. | high flammability; no custom code | **OWED** |

## 6. Legibility matrix — the acceptance test

Every form must be nameable from a top-down sprite at display size. A duplicated row here
is a failed roster.

| form | row | reads as |
|---|---|---|
| braided column of many trunks, several ages at once | kollavane | a wall still under construction |
| thick cable coiled around other plants | vessark | a fight in slow motion |
| swollen bottle-bole, amber tap-runs | tavrosk | a barrel someone owns |
| flat black-green panes meeting edge to edge | dulloth | a ceiling |
| taut veined bladder-trunk | brimlock | a waterskin the size of a tree |
| surface root lattice, no upright part | threllick | pipework underfoot |
| pale fringe hanging in a line | sellith | a dripping gutter |
| stiff sedge in drilled, even stands | varrisk | a planted field nobody tends |
| paired toothed jaws held open | kessaroth | a trap, honestly declared |
| bare wand ringed with glassy spikes | norrveth | a weapon on a stand |
| drooping wet dark bell, sweet at range | sorrivel | **an invitation — which is the lie** |
| bone-white blooms in runs and arcs | pellareth | route-lights |
| rust-red rosette on foul ground | ruddreth | a warning flag |
| strings of plump pale pods | fellome | free food |
| low turf with one hard advancing edge | grennick | a tide line |
| dry varnished scrub, half dead | brennoth | kindling |

🔑 **Two rows are deliberately deceptive** and the matrix records it on purpose:
**sorrivel** must read as attractive (it is the bait), and **fellome** must read as free
(gleaning the plantation is never free). An art pass that "fixes" either has broken the
design. And **pellareth** carries the biome's one navigation system — its fresh and
withered states must be distinguishable at a glance or sheet §4c's promise is dead art.

---

## 7. What is replaced — disposition of the 7 donor rows (PROPOSED)

The live `RUT_Webwork` `<wildPlants>` carries 7 rows (`rosters/the_webwork.json`, flora
block). ⛔ **PROPOSED only — evictions are stopped as a sweep; this is the Webwork's own
sitting, so each disposition below is the owner's call here and nowhere else
(sitting record §6 item 8 carries the one canon case). Nothing is executed by this
document.**

| donor row | comm. | disposition (PROPOSED) | why, in one line |
|---|---|---|---|
| `AB_JungleTree` | 1.1 | **CUT** | the donor tree standing in for the thicket's body — `RM_Kollavane` (§2 row 1) is that body, designed for the churn and the nest |
| `RG_Plant_TropicalChokevine` | 1.0 | **CUT** | the hostile vine mass's job passes whole to `RM_Vessark` (§2 row 2), which is authored against the churn rather than borrowed for it |
| `AB_TangleTea` | 0.4 | **CUT** | generic donor tangle-understory; the churn understory is now vessark/norrveth work |
| `Plant_TookeTrap_Wild` | 0.3 | **MOVE to the Utinni injection layer, kept low** | genuine canon (a *tooke*-trap is Star Wars IP — Q11); it cannot sit in the free roster, and `RM_Kessaroth` is the free tier's snap-trap. See §8 — awaiting the owner's card (sitting record §6 item 8) |
| `AB_Gomphoeria` | 0.15 | **CUT** | generic donor understory filler; the floor's work is done by named rows now |
| `AB_RedBugloss` | 0.07 | **CUT** | donor understory the JSON itself flagged for the eye pass — and "bugloss" is an Earth plant name besides (ban 3 by the letter) |
| `AB_Aaklac` | 0.05 | **CUT** | generic donor understory filler |

The 5 already-purged vanilla rows (`flora_purged` in the JSON — grass, tall grass, low
shrub, alocasia, berry) are prior work under ban 3 and are not re-dispositioned here.

---

## 8. Canon injection (additive, Utinni layer)

Per the owner's method: ours first, canon **added** afterward where it genuinely fits.
Injections ride the campaign patch layer (`UtinniPatches/Patches/WildPlants_Webwork.xml`),
never the `RM_` tier, and never substitute for a row above (Q11a).

| candidate | canon status | framing | verdict |
|---|---|---|---|
| `Plant_TookeTrap_Wild` | ✅ genuine canon (tooke-trap — named in the tier law itself, `biome_mod_architecture.md` §7 Q11, as an example of a name that IS IP) | Exactly as the sitting record §6 item 8 frames it: **PROPOSED kept low via a Utinni `WildPlants_Webwork` patch**, with `RM_Kessaroth` (§4 row 9) as the free tier's snap-trap. The canon trap injects *beside* ours at low commonality — a second, recognisable jaw in the thicket for campaign players — or is cut outright. | ⚠️ **AWAITING THE OWNER'S CARD** — §6 item 8 of the sitting record. Both readings written; neither executed |

**No other canon flora is recommended for this biome.** The Webwork's flora story is the
thicket, the plumbing and the white half — all invented, all load-bearing — and the
opportunistic-injection bar (*"not trying to inject any-old-thing just because it's not
obviously wrong"*) is not met by any candidate surveyed. The Fever Wood's canon trees
(hydenock, jogan, chak-root) belong to that biome's crown and are not multi-homed here.

⚠️ **Sourcing discipline** (standing): `canon_references/` holds 137 entries **by
design**, so absence from it proves nothing — and a donor mod's own defName is **not** a
source. Any future injection must be verified through the Wookieepedia search API
(`action=query&list=search&srsearch=`), never a guessed exact title.

---

## Appendix — collision sweep (MEASURED, this pass)

Python sweep (never a zsh loop), case-insensitive, over all `.md/.xml/.json/.cs/.py/.txt/.csv`
under `design/` and `src/` — 4,581 files scanned. **Sanity probes first** (a search that
finds nothing must first prove it can find something): `korrum` 37 occurrences in 9
files, `stoneback` 162 in 41, `hawkbat` 259 in 48. ✅ The instrument sees.

**Result: every flora defName on this page has 0 occurrences outside the three Webwork
sitting docs** (this file, the fauna roster, `webwork_owner_and_nest_2026-09-23.md`) —
per-name totals inside the sitting docs ranged 4–9, all expected self-citations.

🔑 **The sweep caught one real collision and it was fixed before this appendix was
written:** the margin-tinder row was first named *skarrow* — 9 occurrences outside the
sitting docs, including the live Rot patches (`RotSpecies_NamesAndSizes.xml`,
`PlantTolerances_Ashkarr.xml`: the Rot's **"skarrow dome"** shelf-fungus label). Renamed
**`RM_Brennoth`**, re-swept: 0 occurrences anywhere outside this roster.
