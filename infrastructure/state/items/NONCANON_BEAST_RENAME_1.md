# NONCANON_BEAST_RENAME_1 — non-canon beasts get pseudo-Star-Wars names

## the ruling

Owner, 2026-09-20, verbatim: *"Any non canon beasts need renaming as well into
pseudo Star Wars equivalents."*

"As well" attaches it to `DONOR_DEFS_PORT_TO_OURS_1`, said in the same breath:
as each donor creature becomes our own def, a creature whose name is **not Star
Wars canon** gets a name that sounds like it is.

## what this is and is not

- ✅ **In scope:** beasts with Earth names (`Rat`, `GiantSlug`, `CaveSpider`,
  `SmogMoth`, `Pillbug`), donor-invented names that read as generic sci-fi or
  fantasy (`AA_Needleroll`, `AA_BoulderMit`, `AA_Terramorph`,
  `BMT_PustuleHornet`), and anything a player would not place in the galaxy.
- ⛔ **Out of scope — do not touch:** real canon (`Bantha`, `Kreetle`, `Massiff`,
  `Nerf`, `Eopie`, `Ronto`, `Gutkurr`, `Shyrack`, `Gorg`, `Jamel`, `KraytDragon`,
  `WompRat`, `Mynock`, `Anooba`, `Gizka`, `Varactyl`, `Nuna`, `Lothcat`, …).
  Canon names are the point of the setting; renaming one is a defect.
- ⛔ **Not the flora.** He said *beasts*. Flora renaming has been handled per
  biome by its own verdict pass.

🔑 **The canon test is `design/RimStarWars/canon_references/`** — 137 sourced
entries, 45 creatures / 69 species / 23 droid chassis. If a beast has an entry
there, it is canon and keeps its name. If it does not, check before assuming:
absence from the library is not proof of non-canon, the library is not
exhaustive. The `rimworld-canon-references` skill is the operating doc.

## the precedent to follow

The Rot and Lantern Deeps verdict passes already did exactly this, on his
rulings, with campaign names replacing donor ones — `rot_flora_fauna_names.md`
and `lantern_deeps_flora_names.md` are the worked examples, and
`AA_MycoidColossus` → "vorrugath", `RUT_Nuitae` → "nissik gill" are the shape.
Read those before inventing a naming style; there is one already.

## spec

⛔ **Do not bulk-rename.** This is `kind: design` — per `Agent_Policy.md` design
is backgrounded to a Fable subagent, never done in-window, and the owner reacts
rather than composes.

1. **Census first**: every beast in every owned biome roster, split canon /
   non-canon / uncertain, with its current name, its art, and its biome. The
   MEASURED donor table is in `infrastructure/state/facts/biome_rosters.md`.
2. **Draft names in batches by biome**, so a biome's cast sounds like one place.
   Give each a one-line rationale; he reacts.
3. **Apply only after he rules**, then wire label + description together — a
   renamed def with the donor's old description is worse than not renaming.
4. Record each batch's rulings in the biome's own names doc, matching the two
   that exist.

## Watch out

- 🔴 **Rename the LABEL and the DESCRIPTION together.** A "nissik gill" whose
  description still says "nuitae" reads as a bug to the player. The Rot pass hit
  exactly this on marsh/growable sibling variants.
- ⚠️ **Sibling and variant defs share a base name** (`RUT_NuitaeMarsh`,
  `RUT_WrinklecapMarsh`, `*Growable`). Rename the family, not the base def alone.
- ⚠️ **A defName is not a label.** This ruling is about what the PLAYER reads.
  Whether the defName also changes is `DONOR_DEFS_PORT_TO_OURS_1`'s question, and
  keeping the two jobs separate is what makes either checkable.
- ⚠️ Check a new name does not collide with an existing `<label>` anywhere in
  `src/` — the Rot pass ran that sweep and it is cheap.
- ⛔ "Jawa" is lore text only, never a name tier.

## verify

Every beast a player meets reads as belonging to the galaxy; no canon name was
changed; no label collides; label and description agree on every renamed def.

## criteria

A player who knows Star Wars cannot pick our invented beasts out of the canon
ones by name alone.

---

## 🔴 THE STANDARD — owner, 2026-09-20, after BENCH got it wrong twice

> *"No! I said [pseudo] Star Wars names. I don't want your whining real canon
> names like that. This is the second error. When I say pseudo Star Wars I mean
> it."*
> *"Do not assign canon to non canon."*

**What went wrong:** BENCH drafted 23 names — Sandstrider, Spineroller,
EmberCarpet, Ferroclaw, Dunestalker, Whirlbloom — and **MEASURED 23 of 23 were
built from English stems.** They are fantasy kennings, not Star Wars names. The
whole batch was rejected.

### The two rules, and they are SEPARATE

**1. COINED, NOT COMPOUNDED.** The name reads as an alien word, not English
parts glued together. ⛔ Never `<English adjective><English noun>`.

⚠️ Star Wars does ship a few English compounds — `dewback`, `hawkbat`,
`mudhorn`, `fanback`, `clodhopper`, `whisperbird`, `dragonsnake`. They are **7
of 44** canon creature names, they are homely two-syllable nouns, and they are
NOT the licence this rule denies. When in doubt, coin.

**2. DO NOT ASSIGN CANON TO NON-CANON.** A coined name must not BE a real Star
Wars name. Calling an invented beast "acklay" or "kinrath" is worse than a bad
name — it tells the player a canon creature is present when it is not.

### The phonetic target — MEASURED from the 37 coined creature names in `design/RimStarWars/canon_references/`

| property | canon |
|---|---|
| syllables | **2** (26/37), 3 (6), 1 (3), 4 (2) |
| length | **4–7 letters** (31/37) |
| final char | vowel dominates — a (9), o (4), then r (4), k (3), g (2) |
| doubled letter | 12/37 (`acklay`, `cannok`, `zakkeg`, `orray`, `massiff`) |
| k / q / x / z | 14/37 (`gizka`, `horax`, `vulptex`, `vornskyr`) |

### 🔑 Enforced, not exhorted

`python3 src/RimMandrake/Utils/check_pseudo_sw_name.py <names...>`

Refuses a name built from an English stem, a name that collides with any of the
137 canon entries, and a name outside the measured shape. **Calibrated both
ways before use:** BENCH's rejected drafts are REFUSED on English stems, and
real canon names (`Gizka`, `Zakkeg`, `Kreetle`) are REFUSED on collision — which
is correct, because a non-canon beast must not take them.

⚠️ It checks SHAPE and COLLISION. It cannot tell you a name is GOOD. That is the
owner's ear, and his overrule is the signal worth having — run every draft
through it before he ever sees the list, so his attention is spent on taste
rather than on catching English compounds.

---

## Batch 2 — RULED AND APPLIED 2026-09-20 (`32ecbc8cb`)

✅ **Ruled by the owner and landed the same day**: `32ecbc8cb` *"owner ruled batch 2 —
apply all 22 renames"* rewrote label + labelPlural + description together across 6
SWBestiary files (`RSW_DesertPortMisc_Races.xml` and siblings). The reaction sheet is
`Transient/drafted_creature_names_2026-09-21.md`. Every name passed
`check_pseudo_sw_name.py` before he saw it. (Header corrected 2026-09-24 — it still read
"DRAFTED, NOT RULED" four days after the apply commit.)

**Batch 3 (Forsaken Crags, Nightside Ice, the Contagion, the Slime) — RULED AND APPLIED
2026-09-24 (`d9b150ab5`).** The owner ruled the batch with two new laws, typed same day:
syllable VARIETY (some one-, some three-syllable — no wall of twos) and the PLANET-WIDE
slime law (slime/goo/gel creatures take long-vowel monosyllables: ghaaz, zhool, wuum,
oomb, vohhm). Doc records the rulings + strike-throughs:
`design/Jawa/worldbuilding/biomes/noncanon_beast_names_crags_nightside_contagion_slime.md`.
Applied as 4 conditional patch files (`UtinniPatches/Patches/*_Rename.xml`) + in-place
`RSW_CaveLemming` → mahllik; 42 labels, validate 0 errors, 0 collisions. **Left open:**
`AA_Razorjack` (skezzar/sytheclaw conflict — owner warned 2026-09-24 the sytheclaw was
mistakenly removed from the Pyrelands; settle at the Pyrelands sitting, never by renaming
razorjack to sytheclaw) and `RM_Titanoslime` (offer *baahm* unaccepted; his word
"titanoslime" stands). Art: 114 jobs queued same day under ruled names.

🔴 **Batch 1 is the rejected one** (Sandstrider, Spineroller, EmberCarpet,
Ferroclaw, Dunestalker, Whirlbloom — 23/23 English compounds). Those labels are
still live in `src/RimStarWars/SWBestiary/Defs/DesertPort/`. Batch 1 was lost off
disk once already; this section exists so batch 2 cannot be.

🔑 **defNames do NOT change here.** This item renames what the PLAYER reads.
Whether the defName follows is `DONOR_DEFS_PORT_TO_OURS_1`'s question.

### Fauna (16)

| defName | current label (rejected) | drafted label | the creature |
|---|---|---|---|
| `RSW_Ashworm` | ashworm | **vurra** | worm that trails larger things |
| `RSW_Barbthorn` | barbthorn | **skorra** | mobile cactus, toxic barbs |
| `RSW_Cindermite` | cindermite | **zhakka** | mite that synthesizes chemfuel |
| `RSW_Dunestalker` | dunestalker | **vosska** | cat/shark/skink hunter, swims sand |
| `RSW_Ferroclaw` | ferroclaw | **khorrak** | crustacean that eats iron |
| `RSW_Sandhorn` | sandhorn | **thurra** | muffalo-kin pack beast |
| `RSW_Sandmaw` | sandmaw | **ommok** | cephalopod/cone-snail desert cattle |
| `RSW_Sandstrider` | sandstrider | **ossik** | armoured flightless bird |
| `RSW_Spinerat` | spinerat | **chikka** | rat spliced with cactus |
| `RSW_Spineroller` | spineroller | **kudda** | cactus-form, rolls across sand |
| `RSW_Sporemass` | sporemass | **grommo** | mycoid bulk; shrugs bullets, burns |
| `RSW_Sporepaw` | sporepaw | **pukko** | fungal quadruped |
| `RSW_Stareling` | stareling | **oxxa** | enlarged eye on tentacles |
| `RSW_Stoneback` | stoneback | **bokka** | crab wearing a boulder |
| `RSW_Tuskcoil` | tuskcoil | **ulgga** | giant armoured tusked worm |
| `RSW_Voltmaw` | voltmaw | **vozzik** | slug used as a power plant |

### Flora (7)

Canon plant names are a coined stem plus a plain noun — `chak-root`,
`hubba gourd`, `nysyllin`. These follow that shape, not the fauna shape.

| defName | current label (rejected) | drafted label |
|---|---|---|
| `RSW_Dunegrass` | dune grass | **surra grass** |
| `RSW_Scrubgrass` | scrubgrass | **jekka grass** |
| `RSW_Starvine` | starvine | **tanni vine** |
| `RSW_EmberCarpet` | ember carpet | **ruzzo carpet** |
| `RSW_Whirlbloom` | whirlbloom | **quissa bloom** |
| `RSW_SweetbarkTree` | sweetbark tree | **dommo tree** |
| `RSW_VellaraBloom` | vellara bloom | **vellara bloom** — NO CHANGE, already a coinage |

### On acceptance

Wire **label and description together** on every row — a renamed def carrying the
donor's old description reads to the player as a bug. Then re-run the label
collision sweep across `src/`.
