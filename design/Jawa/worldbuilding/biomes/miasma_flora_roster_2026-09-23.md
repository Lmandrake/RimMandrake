# The Miasma flora roster — 19 invented plants, 2026-09-23

_MACBENCH, authored against the owner's rulings of 2026-09-23 (this sitting) and the
frozen sheet (`the_miasma.md`). Copies the format of
`fever_wood_flora_roster_2026-09-23.md` and `greentide_tree_roster_2026-09-22.md` — the
two sibling wetlands, both authored in the preceding two days._

---

## READ FIRST — what this roster replaces, and why it had to exist

**The Miasma's signature had no content behind it.** The shipped `RUT_Miasma` grows
**four** plants: `AB_MangroveTree` 25, `AB_ParasiticMangrove` 8, `AB_MangrovePalm` 6 — all
three the donor's — and `RUT_Nogtyl` 0.4, which arrived here from the Rot by an unrelated
review. Not one of them is a bloom.

Yet the sheet makes the rainbow flora **§5 always-true**, **§6 hard ban 2**, and the whole
of **§9's artistic thesis** (*"Rainbow blooms in green-gold haze — hope, composting"*). The
only rainbow plant the biome ever had was `BMT_RainbowTongue`, and it was **purged** when
`biomesteam.biomespollutedlands` retired on 2026-09-18. Nothing replaced it. ⇒ The biome
has been shipping its central promise with zero plants able to keep it.

⚠️ **The eviction reason on those purged rows cites `POLLUTED_LANDS_FLORA_PORT_1`, and no
item by that name exists** in `infrastructure/state/items/` or `items/closed/`. Recorded
here as a dangling reference, not resolved by this document.

### Every row here is OURS and INVENTED

Owner's standing instruction (2026-09-23, carried from the sibling rosters): invent a
complete rich roster first, then look for Star Wars injection **opportunistically**. Under
`biome_mod_architecture.md` **Q11a** an invented exotic name is *not* franchise IP, so all
19 rows are **`RM_` tier, cast inline, and the free mod is rich on its own.** Canon
injection is §7, additive, and never a substitute for a row here.

⛔ **No defName here collides** with the Greentide's 22, the Fever Wood's 18, or any shipped
`RM_`/`RUT_` plant — checked against all three lists this pass.

### The silhouette brief is the specification

Same rule as both sibling rosters: the **silhouette FORM** column is what art is
commissioned against and what a reviewer grades. A row whose form duplicates another row's
has failed, because a player must be able to name a plant at a glance from a top-down
sprite. The acceptance matrix is §8.

---

## 0. The owner's rulings this sitting, verbatim where he spoke

| ruling | his words | what the roster owes it |
|---|---|---|
| **The look of every plant** | *"These plants should all be strangely beautiful but also a little sick looking."* | 🔴 **Roster-wide law.** No row is merely pretty and no row is merely grim. Every description below carries a sickness tell — a flush, a crust, a weep, a blotch — and every one is *beautiful because of it*, not despite it |
| **Carnivorous plants, emphatically** | *"Especially add things inspired by real-world cannibal plants"* | §5 — a **five-row predatory clade**, each modelled on a real Earth carnivore's mechanism (pitcher, sundew, bladder-suction, snap-trap, eel-trap) with no Earth-nameable label |
| **What the carnivores may eat** | decision taken by question card | 🔴 **The scuttlers, never a colonist and never a tame animal.** Real pitchers and sundews eat insects and are harmless to people; this is the faithful reading. ⇒ Each predator is a **regulator of the arthropod floor**, which is why this sitting's other half matters to this one |
| **How the ban resolves** | decision taken by question card | **Two families.** The blooms (§4) stay bound by ban 2 exactly as written — beautiful, hopeful, never a trap. The predators (§5) are a **separate clade that was never "the rainbow flora"**, and are visibly, honestly predatory. ⇒ Ban 2 needs no edit |
| **On amending the frozen sheet** | *"Don't be so upset by modifying a frozen document. It's no big deal."* | Recorded so no later pass re-ceremonialises it. Ban 2 is nonetheless left **untouched**, because the two-family answer made an edit unnecessary — not because editing was avoided |

### The visual brief — six references he supplied, read back and confirmed

| # | reference | what the roster takes from it | row |
|---|---|---|---|
| 1 | Rainbow caladium — heart leaves, magenta→crimson→orange→yellow bleeding along the veins | colour that travels *along the veins*, so the leaf looks like it is circulating something | **vellamine** |
| 2 | Coleus collage — nine varieties, no two alike | ⭐ a species whose **every individual is a different colour scheme** | **ismerrow** |
| 3 | Euphorbia new growth — green flushing red-pink at every tip, faintly furred | 🔑 the purest statement of *"sick looking but healthy"* — inflammation as growth | **aphreen** |
| 4 | Giant purple elephant ear — house-tall fans, deep purple, electric blue rim, near-black stems | the biome's **signature silhouette**, and the only bloom at tree scale | **ollamane** |
| 5 | Bubbled blue-green flower — nested rings of beads, gold-and-purple centre | diseased and jewel-like at once; reads as a growth, not a flower | **nyssolet** |
| 6 | Celosia plumes — flame-orange and magenta feather-crests | something *inflamed* — a crest that looks like a fever chart | **sarrash** |

⚠️ **The reference images themselves could not be persisted to disk** from this session, so
the descriptions above are the durable brief. An art pass should treat this table as the
reference, and a reviewer grading a sprite grades it against these words.

---

## 1. The organising axis is the salt gradient, not height

The Fever Wood's roster sorts by height above the water because that biome is vertical.
The Miasma's does not. Its own §3 names the axis outright:

> *"**The gradient as geography.** Every map has a fresh→brine axis; trees, fauna, disease
> load and muck-color all sort along it; the surge redraws it around whatever the player
> has built."*

⇒ **Every row below declares where on the fresh→brine axis it can stand**, and that is the
roster's spine. It is already a built mechanism: `RM_GradientAxisExtension` and
`RM_GradientSurgeExtension` shipped 2026-09-13 in `RimMandrake.EnvironmentalHazards`, so
these plants land on working code rather than a proposal.

🔴 **And it makes the flora an instrument.** Because the salt line *moves miles per surge*
and nothing here reaches equilibrium, a plant that can only live at the fresh end becomes a
**record of how far the brine last reached** — see `RM_Mirrash`, which is the roster's
single most important row for that reason.

### The other laws this roster serves

| ruling | source | what the roster owes it |
|---|---|---|
| **Zero rain; the trees drink river and sea directly** | sheet §3, ban 5 | 🔴 no row anywhere is rain-fed. The mangals are halophytes: they strain brine through bark and **sweat salt from their leaves**, which is a visible white rime and the biome's best texture idea |
| **The fever-swarms are the mangals' ONLY pollinator** | sheet §4 | 🔑 **every flowering row on this page depends on the disease vector.** You cannot have the flowers without the fever — stated once here rather than repeated per row |
| **No medicine economy — ruled CUT** | sheet ban 3 | ⛔ **zero medicine rows.** The Fever Wood has its halquin; the Miasma may not have an equivalent. The §6 attar is the replacement and the only luxury line |
| **The rainbow flora never lies — absolute** | sheet ban 2 | §4's six rows are **genuinely benign without exception**: no yield that harms, no trap, no mimicry. ⛔ A later pass that gives any §4 row a downside has broken the ban |
| **The stilt-root maze is terrain, architecture and nursery cage** | sheet §3, §4 | `RM_Thessamor` is the species that *is* the maze — the nursery's cage is a plant |
| **Density is refugee crowding, not plenty** | sheet §0, §2 | flora commonalities stay **thick**; forageability 1.0 is doctrine. The delta looks overcrowded because it is |
| **No gene machine; no vanilla-Earth flora** | sheet bans 1, 7 | no directed mechanism on any row; no Earth-nameable label anywhere |

---

## 2. At a glance

| the mangals (the canopy) | the rainbow blooms (benign, always) | the predators (eat scuttlers only) | the muck and the silt |
|---|---|---|---|
| **thessamor** — the maze itself | **ollamane** — the signature fan | **ullavess** — the standing pitcher | **immarel** — the attar is in its root-bed |
| **brelloch** — farthest into the brine | **vellamine** — colour in the veins | **nemreth** — the jewelled sticky mat | **thrannock** — combs the flotsam out |
| **quennath** — drinks its host, not the sea | **ismerrow** — no two alike | **velluric** — the trap is underwater | **pallasheen** — grows only on loam |
| **mirrash** — ⭐ the salt-line gauge | **aphreen** — inflamed and perfectly well | **braskeen** — the only plant that moves | **wessaline** — the salt-pan skin |
| | **nyssolet** — a jewel that looks like a growth | **ommolyn** — the trap is buried | |
| | **sarrash** — the fever crest | | |

---

## 3. The mangals — four trees, and they are the terrain

Multi-tile. These four **replace the three donor rows** and extend them by one. The donor
set is generic alien filler that a player cannot tell apart; worse, `mandrake.rm.miasma`
may not depend on Alpha Biomes at all, so a free-tier Miasma with donor trees has no
canopy. ⇒ Under the owner's Q11a ruling the free mod must look *the same* as the campaign
one, so these are not a thin fallback — they are the canopy.

| # | defName | label | silhouette FORM | what it looks like | gradient | cells | job | art |
|---|---|---|---|---|---|---|---|---|
| 1 | `RM_Thessamor` | thessamor | **tripod prop-root cage under a broad low crown** | The trunk never touches the water — it begins a full metre up, carried on a splayed cage of prop-roots you can see straight through. Below the tide-mark the bark is wet black and polished; above it, grey-green and furred with a **white salt rime it has sweated out**, which flakes when touched. The crown is broad and low and permanently dripping. | anywhere brackish | **9** | 🔑 **The biome's structural unit and its most important object.** The stilt-root maze *is* this species — so the terrain, the architecture and the nursery cage of every horror the Grey Sea still holds are all one plant. Replaces `AB_MangroveTree`. | **OWED** — the largest canvas here |
| 2 | `RM_Brelloch` | brelloch | **squat, thick, encrusted — wider than it is tall** | A low heavy thing that looks half-buried, its whole upper surface armoured in a **crust of its own excreted salt** an inch thick, grey-white and cracked like old glaze. Where the crust has flaked, the living bark beneath is a startling wet green. Leaves small, thick, and rimed shut. | 🔴 **the brine end, and only there** | 6 | ⭐ **The seaward marker.** Brelloch is the last living thing before the salt wins, so a stand of it tells you exactly where the gradient ends. Its crust is a harvestable salt — the cheapest good in the biome, and the one the stills need. | **OWED** |
| 3 | `RM_Quennath` | quennath | **a second crown growing out of another tree's roots** | It has no trunk of its own. A knotted mass clamped into a thessamor's prop-root cage sends up a slender stem and a crown that is **visibly more colourful and healthier than its host's** — because it is drinking water another plant already strained. Its leaves are the deepest green in the canopy, veined violet. | wherever its host is | 3 | **The parasite, and the biome's thesis in one plant**: it never touches the brine at all, it just takes from something that did. Replaces `AB_ParasiticMangrove`. ⚠️ Must only spawn adjacent to a thessamor, or it reads as an ordinary shrub. | **OWED** |
| 4 | `RM_Mirrash` | mirrash | **tall bare stem under a single thin fan — and often dead standing** | A slim pale stem well above the mangal crowns carrying one sparse fan of ribbon-leaves. Living mirrash are yellow-green and translucent at the edges. **Dead ones stay standing for years**, bleached white, fan collapsed into a drooping rag — and they are everywhere in a band. | 🔴 **the fresh end only; killed by brine** | 4 | ⭐ 🔑 **The salt-line gauge, and the roster's single best row.** Mirrash die where brine reaches and their skeletons remain, so **a line of dead mirrash records how far the last surge pushed** — the map's only readable history of the one process that governs it. ⇒ This converts an invisible simulation into something a player learns to read, exactly as corvath does for the Fever Wood's pools. Replaces `AB_MangrovePalm`. | **OWED** — needs a **live** and a **dead** variant |

⭐ **`RM_Mirrash` needs two graphics, not one.** The dead standing form is the entire point
of the row and it is not a damage state — it is a distinct, permanent, common sight. An art
pass that delivers only the living plant has delivered none of its value.

---

## 4. The rainbow blooms — six plants, and every one is genuinely benign

🔴 **Hard ban 2 binds this whole section and is unchanged by this sitting**: *"never a
trap, never a mimic, never toxic… Both stay absolute."* These six are beautiful, they are
hopeful, and the colour means exactly what it appears to mean. ⛔ **No row here gains a
downside in any later pass.** The predators in §5 are a different family and are not
covered by this.

But all six obey the sitting's other law — **strangely beautiful, and a little sick
looking.** That is not a contradiction of benignity: the Miasma is a fever-hot compost heap,
and a plant that grows gorgeously out of it should look like it has been through something.

| # | defName | label | silhouette FORM | what it looks like | gradient | cells | job | art |
|---|---|---|---|---|---|---|---|---|
| 5 | `RM_Ollamane` | ollamane | **enormous single-plane fans on near-black stalks, at tree height** | Three or four vast fan-leaves on separate stalks rising far above everything around them, each fan a deep saturated purple shot through with darker veins and **rimmed in a hard electric blue line** that reads almost like light. The stalks are so dark they are nearly black, and glossy. Undersides mottled with grey blotching. | mid-gradient | **6** | ⭐ 🔑 **The biome's signature silhouette** — the thing on the key art and the thing you see first standing in the delta. §9 asks for rainbow blooms in green-gold haze; this is that sentence as one plant. Its fans are cut for roofing and for Bitterleaf's stilt-architecture. | **OWED** — highest-value single sprite on the page |
| 6 | `RM_Vellamine` | vellamine | **low overlapping heart-leaves, no stem visible** | A dense clump of broad heart-shaped leaves lying over one another so no stem shows, each leaf carrying colour **along its veins** — magenta at the midrib bleeding out through crimson and orange into a yellow-green margin. No two leaves on one plant have travelled the same distance. Edges slightly curled and dry. | fresh to mid | 2 | **The groundcover that carries the biome's palette**, and the one a player will plant in a garden for beauty. Reads as circulating something, which is the biome's whole idea made decorative. | **OWED** |
| 7 | `RM_Ismerrow` | ismerrow | **serrated upright rosette — and a different colour on every plant** | A knee-high rosette of sharply toothed leaves. ⭐ **Each individual is a different scheme**: electric blue-teal with a magenta edge, purple over lime, near-black with a lit yellow centre, rose bleeding to cream. The toothing and the posture are constant; the colour never is. Every plant looks faintly scorched at the leaf-tips. | fresh to mid | 1 | ⭐ 🔑 **The only plant on the planet whose individuals differ**, straight from reference 2. It makes a stand of one species look like a garden of many, which is precisely §1's *"threaded through the stink, improbably, beauty."* ⚠️ **Needs a colour-randomised graphic, not one sprite** — if it ships as a single texture the row's entire point is lost. | **OWED** — and it is a *set* |
| 8 | `RM_Aphreen` | aphreen | **narrow whorled leaves, every growing tip flushed and furred** | An upright bushy thing of narrow leaves in tight whorls, mature growth a plain dusty green — and **every new tip flushed hot pink-red and covered in fine pale fur**, as if inflamed. The flush fades as each leaf matures, so one plant shows the whole progression at once. | anywhere brackish | 2 | 🔑 **The purest statement of the sitting's law**: it looks diseased and it is perfectly healthy, and a player who learns that about aphreen has learned how to read this biome. The most common plant in the delta; the visual ground the rarer blooms sit on. | **OWED** |
| 9 | `RM_Nyssolet` | nyssolet | **nested rings of beads, not a flower shape at all** | Concentric rings of glossy blue-green spheres, each ring smaller than the last, closing on a centre of gold and violet filaments. It does not read as a flower — it reads as **a growth, or a cluster of eggs, and it is stunning.** Individual beads are semi-translucent with a darker fluid visible inside. | mid to brine | 1 | **The uncanny one.** Ban 2 guarantees it is harmless, and it looks least harmless of anything here — which is the ban working as designed. The beads are the attar's fixative (§6), which is why an expensive luxury smells of this delta and nowhere else. | **OWED** |
| 10 | `RM_Sarrash` | sarrash | **upright feather-crest plumes, tallest in the middle** | Dense soft plumes of fine filaments in flame-orange and hot magenta, held upright in a group with the centre plume tallest, so the outline is a ragged crest. Up close the filaments are damp and slightly clumped, and the base of each plume is browned and spent. | fresh to mid | 2 | **The colour mass at eye level** — where ollamane works above and vellamine below, sarrash fills the middle and gives the green-gold haze something to burn through. Plume fibre is the delta's cheap textile. | **OWED** |

---

## 5. The predators — five plants, and they eat the scuttlers

⭐ **The owner's own emphasis this sitting**, and each row is built on a real Earth
carnivore's *mechanism* rather than its name (ban 7 forbids Earth-nameable labels, and
"pitcher plant" would fail on sight).

🔴 **Ruled: they take the armoured scuttlers, never a colonist and never a tame animal.**
That is not a softening — it is what real carnivorous plants do, and it makes this clade the
**predator tier of the arthropod floor**, tying it to the other half of this sitting. The
scuttlers are *"eaten by everything"* and the *"entire food pyramid stands on their backs"*
(sheet §4); these five are the part of that pyramid that cannot chase.

⛔ **These are NOT "the rainbow flora"** and ban 2 does not bind them. They are honestly,
visibly predatory — nothing here is disguised as something safe, which is the distinction
the owner's two-family ruling turns on.

| # | defName | label | silhouette FORM | what it looks like | mechanism it is built on | cells | job | art |
|---|---|---|---|---|---|---|---|---|
| 11 | `RM_Ullavess` | ullavess | **upright open-mouthed vessels in a loose cluster** | A group of tall tapering vessels standing mouth-up, each half-full of clear fluid you can see into. The outer wall is veined maroon over yellow-green; the **rim is a hard iridescent lip** and the inside wall is glassy and visibly slick. Spent vessels below are brown and collapsed. | pitcher plant — a pitfall trap of fluid and a slippery rim | 2 | **The clade's anchor and the one a player recognises instantly as a predator.** Its fluid is a gathered liquid used in the stills; a vessel that has fed is cloudy, which makes the plant a readout of how thick the scuttler floor is nearby. | **OWED** |
| 12 | `RM_Nemreth` | nemreth | **flat mat of fine stalks, every stalk bead-tipped** | A low mat of hair-fine red stalks, each ending in a clear glistening bead that **holds the light like dew and never dries**. From a distance the whole mat glitters. Close, the beads are thick and drawn into threads, and older stalks are curled inward around what they caught. | sundew — glandular adhesive | 1 (spreads) | 🔑 **The most beautiful thing in the biome that is also a killer**, and it is not a contradiction because it never pretended otherwise. The glitter is the honest advertisement. Its adhesive is the attar's binder. | **OWED** |
| 13 | `RM_Velluric` | velluric | **a single bloom on open water, and nothing else visible** | Above the channel, one small pale flower on a thin stalk, unremarkable. **Everything else is submerged**: a drifting mass of fine bladders, each with an inward trapdoor, invisible from the bank. The water above a velluric bed is very slightly clearer than the water beside it. | bladderwort — underwater suction traps | 1 | ⭐ 🔴 **The row that makes the channels themselves dangerous to small things**, without ever threatening a colonist. It is also the one predator a player will not see coming, and learning that the too-clear water is a velluric bed is a real piece of biome literacy. | **OWED** — needs a submerged read |
| 14 | `RM_Braskeen` | braskeen | **floating whorl of paired hinged blades** | A flat whorl lying on the surface, each arm ending in a pair of hinged blades held slightly open, fringed with stiff interlocking teeth. **The blades visibly close** when something touches them, and stay shut for a day with the catch showing between the teeth. Blade interiors are a raw wet pink. | waterwheel plant / snap-trap — a hinged closure | 1 | ⭐ 🔑 **The only plant on the page with motion**, which §9 explicitly asks for (*"constant small life"*). A channel of braskeen snapping shut one after another as scuttlers cross is the biome's best ambient moment. | **OWED** — needs open and closed states |
| 15 | `RM_Ommolyn` | ommolyn | **a small flower over nothing — the plant is underground** | Above the mud, a single modest cream flower on a short stalk and a few limp surface leaves. Below, **a buried maze of forked hollow tubes lined with inward-pointing hairs** that admit and never release. Nothing on the surface suggests it. The mud within a tile or two is conspicuously free of scuttlers. | corkscrew plant — a subterranean eel-trap | 1 | **The invisible predator, and a prospector's tell inverted**: bare mud around a modest flower means ommolyn is working below. Its tube-fibre is the only cordage that survives the brine. | **OWED** |

⚠️ **One design risk worth stating plainly.** Three of these five (velluric, ommolyn, and
arguably braskeen) do their work out of sight, and a mechanic a player never sees is a
mechanic that does not exist. ⇒ Each needs a **visible consequence**: velluric's too-clear
water, ommolyn's scuttler-free mud, braskeen's closed blades with the catch showing. Those
are written into the rows above deliberately and are not decoration.

---

## 6. The muck and the silt — four plants, and three of the §7 economies

The sheet's §7 goods are **attar**, **delta loam**, **the arthropod harvest**, and **the
flotsam yard**. The arthropod harvest belongs to this sitting's fauna half; the other three
need plants, because a good a player cannot find is not a good.

| # | defName | label | silhouette FORM | what it looks like | gradient | cells | job | art |
|---|---|---|---|---|---|---|---|---|
| 16 | `RM_Immarel` | immarel | **dense stand of jointed reeds, all leaning one way** | Tight stands of hollow jointed reeds, all leaning downstream together, stems banded olive and rust with a **greasy iridescent film** where they leave the water. Tops bear a spent brown tassel. The mud in an immarel bed is black, fine and slick, and smells extraordinary. | mid-gradient, in flowing channel | 2 | ⭐ 🔑 **The attar is dug from its root-bed.** The sheet says the delta silt refines into the oil that restores beauty; immarel is what *concentrates* that silt into a findable, workable bed. ⇒ The planet's loveliest luxury has a plant you can stand next to, which is what makes Bitterleaf's stills an industry instead of a description. | **OWED** |
| 17 | `RM_Thrannock` | thrannock | **a coarse aerial root-mass like a thrown net** | Almost no foliage — a sprawling tangle of stiff aerial roots spanning the water between two mangals, coarse as rope and hung with everything the current brought: rags, shell, splintered wood, salt-bleached plastic. The living root beneath is a dull purple-brown. Always visibly full of debris. | anywhere with current | 4 | 🔑 **The flotsam yard is this plant.** §8's Jawa *"flotsam-combing crews working the root-lines after every surge"* are combing thrannock, so the biome's salvage economy gets a physical object crews can be sent to. ⇒ It also makes the surge legible: a freshly loaded thrannock means the water came up recently. | **OWED** |
| 18 | `RM_Pallasheen` | pallasheen | **a broad thin single leaf lying flat, almost translucent** | One wide pale leaf pressed flat to the ground, thin enough that the soil colour shows through, edged in a fine pink line. It never stands up and never clumps. | anywhere there is loam | 1 | ⭐ **The loam prospector's tell.** Pallasheen germinates *only* on composter castings, so where it grows the exportable delta loam is already under it. ⇒ Converts an invisible animal by-product into something a player can walk up to and dig, and it pays the composters off visually. | **OWED** |
| 19 | `RM_Wessaline` | wessaline | **an unbroken brittle crust across bare flat ground** | A continuous white-and-grey skin lying over the salt pans, crazed into plates that lift at the edges and **crunch underfoot**. Barely reads as living; only a faint green bloom in the fissures gives it away. | 🔴 the brine end, on bare pan | 1 (spreads) | **The ground cover that makes the brine end look terminal rather than unfinished** — the salt-crust white §9 asks for, as a plant rather than a terrain. Worth almost nothing, deliberately. ⚠️ Must **not** read as a trap: the Fever Wood already owns the deceptive-flat-skin idea with skimmel, and a second one dilutes it. | **OWED** |

✅ **Authored decision, flagged for the owner (§10).** The sheet says the attar refines from
*"the delta silt"*, which reads as a terrain property. I have given it a **plant** —
immarel's root-bed — following the precedent he set on 2026-09-23 for the Fever Wood's
seep-oils, where the terrain route was offered and **declined** in favour of a harvestable
plant (`RM_Seepril`). The silt is still the source; immarel is where it accumulates. ⛔ If
he wants the terrain route after all, this is the row to change and nothing else moves.

---

## 7. Star Wars injection — opportunistic, and only where it earns the slot

Ours first; canon **added** afterward where it genuinely fits, riding the campaign patch
layer (`UtinniPatches/Patches/WildPlants_*`), never the `RM_` tier.

| candidate | canon status | why it might earn a slot here | verdict |
|---|---|---|---|
| `RUT_Nogtyl` | currently shipped here at 0.4, moved in from the Rot by a 2026-09-20 owner review | It is already his ruling and already on the biome. Nothing in this roster displaces it. | ✅ **KEEP as-is** |
| the 3 `AB_*` mangal rows | donor, not canon | Generic alien filler, and they are the canopy — which the free-tier mod may not source from a donor at all. | ⛔ **CUT** — replaced by §3 |
| a canon brackish/delta flora | **UNVERIFIED — nothing proposed** | The sheet offers no canon plant for this biome and I am not inventing a candidate to fill the row. | ⏸ **NONE THIS PASS** |

🔴 **Sourcing discipline, and it has already cost this project a false claim.** A donor
mod's own defName is **not** evidence of canonicity, and absence from
`design/RimStarWars/canon_references/` proves nothing either — it holds 137 entries *by
design*. Any future injection must be verified through the Wookieepedia search API
(`action=query&list=search&srsearch=`), never a guessed exact page title, which returns
MISSING for genuinely canon subjects constantly.

---

## 8. The legibility matrix — the acceptance test for this roster

Every form must be nameable from a top-down sprite at display size. A duplicated row here
is a failed roster.

| form | row | reads as |
|---|---|---|
| tripod prop-root cage under a low crown | thessamor | a structure standing in water |
| squat thing armoured in cracked salt glaze | brelloch | old pottery |
| a second crown out of another tree's roots | quennath | a guest |
| tall bare stem, one thin fan — **or bleached and dead standing** | mirrash | a flagpole, and a graveyard of them |
| enormous single-plane fans on near-black stalks | ollamane | held-up hands |
| low overlapping heart-leaves, colour along the veins | vellamine | something circulating |
| serrated rosette, **a different colour every plant** | ismerrow | a garden of many species that is one |
| whorled leaves, every growing tip flushed and furred | aphreen | inflammation |
| nested rings of glossy beads | nyssolet | a clutch of eggs |
| upright feather-crest plumes | sarrash | a flame, or a fever chart |
| upright open-mouthed vessels holding fluid | ullavess | cups set out |
| flat mat of bead-tipped stalks that never dry | nemreth | frost that glitters in the heat |
| one small bloom on open water, nothing else | velluric | **safe water — and the water is the trap** |
| floating whorl of hinged blades that **close** | braskeen | a machine |
| a modest flower over bare mud | ommolyn | **an ordinary flower, which is the point** |
| dense jointed reeds all leaning downstream | immarel | a current made visible |
| coarse aerial root-mass hung with debris | thrannock | a net someone left |
| one broad thin leaf pressed flat | pallasheen | a stain |
| unbroken brittle crust over bare pan | wessaline | dried mud, and it is not |

🔑 **Two rows are deliberately concealed and the matrix records it on purpose** — velluric's
water and ommolyn's flower. ⚠️ **But neither is a *lie* in ban 2's sense**, because neither
can harm the player; they hide from *scuttlers*, not from people. That distinction is the
whole load-bearing content of the owner's two-family ruling, and an art or design pass that
collapses it has broken the sitting.

---

## 9. What is owed

- 🔴 **All 19 need art, and nothing here exists as a sprite.** ⚠️ Before a single job is
  queued, **search `infrastructure/artpipe/done/`, `_artsrc/`, `registry.jsonl` and any
  review sheet's `.decisions.json` by subject** — the owner's standing rule of 2026-09-20,
  after three Greentide plants were nearly regenerated on top of already-validated art.
  ⚠️ And the artpipe daemon does **not** run on the Mac, so queueing here generates nothing
  until a Desktop session runs it.
- ⭐ **Three rows need more than one graphic**, and each will silently lose its entire point
  if it ships as a single sprite: **mirrash** (live and dead-standing), **ismerrow**
  (colour-randomised set), **braskeen** (open and closed).
- 🔴 **`RM_Velluric` needs a submerged read** — a plant whose body is under water is not a
  solved art problem in this project and should be checked against the existing
  `RM_DiveEligible` terrain work in `mandrake.rm.divinginteraction` before art is briefed.
- **Commonalities and `growDays` are slots, not values.** Every number is owed a tuning
  pass, and density must stay thick per the refugee-crowding doctrine.
- **This document removes nothing from the live biome def.** Replacing the four shipped
  rows is a def-editing pass, and `BIOME_PAINT_ONCE_AT_THE_END_1` governs anything touching
  the live biome. The natural home is `MIASMA_RM_MOD_BUILD_1`, which already owns copying
  content onto `RM_Miasma`.
- ⛔ **No medicine row, ever** (ban 3). If a later pass reaches for a cure-herb or a
  pharmacopoeia here it has misread the sheet — the attar is the replacement and it is a
  cosmetic luxury, not a medicine.
- 🔴 **The predators' carnivory needs a mechanism decision that is UNMEASURABLE on the Mac.**
  Whether a plant can consume a small wild animal at all — and whether "scuttlers only" can
  be expressed without a custom comp — is an engine question. The nearest existing precedent
  in this repo is `RM_CompVerminBreeder` + `RM_MapComponent_VerminPopulation`, which already
  tracks a small-creature population and would be the natural thing for these five to draw
  down. ⇒ **Read that before writing any new C#**; four of six mechanisms in the last
  comparable sitting turned out to be already built.

---

## 10. For the owner

1. ⭐ **The salt-line gauge is the row I would defend hardest.** `RM_Mirrash` dies where
   brine reaches and its skeletons stay standing, so the band of dead ones is a permanent
   record of the last surge. It turns the biome's central invisible process into something a
   player reads off the landscape. It needs two graphics to work at all.
2. ⚠️ **I gave the attar a plant rather than a terrain** (§6, immarel), on the precedent of
   your Fever Wood seep-oils ruling. The sheet says "delta silt", so this is my call
   overriding a sheet phrasing and it deserves your eye.
3. ⚠️ **`RM_Ismerrow` is only worth building if it can be colour-randomised.** If a
   per-plant colour variant is not achievable, the row should be cut rather than shipped as
   one sprite — it exists solely to be never-alike.
4. 🔴 **Ban 2 is untouched.** Your two-family answer meant the blooms stayed absolutely
   benign and the predators became a separate clade, so no frozen text needed editing. I am
   flagging that I *did not* edit it, since you had explicitly cleared me to.
5. ⚠️ **The `POLLUTED_LANDS_FLORA_PORT_1` reference is dangling** — four purged flora rows
   cite an item that does not exist in the ledger. Small, but it means the reason the
   rainbow tongue left the biome is not actually recorded anywhere retrievable.
