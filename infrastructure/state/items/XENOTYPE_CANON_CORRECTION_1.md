# XENOTYPE_CANON_CORRECTION_1

Findings from building the species canon library (`SPECIES_CANON_LIBRARY_1`). Roughly 60
species entries were written against sourced canon, and **every single species examined has
at least one def that disagrees with canon.** The individual findings live in each
`design/RimStarWars/canon_references/<slug>/description.md`; this file records the
**patterns**, because they are generator bugs rather than sixty separate mistakes.

⚠️ **Nothing has been fixed.** `RimMandrakeXenotypes.xml` is GENERATED
(`src/RimMandrake/Utils/gen_races_mod.py`), so hand-edits would be overwritten. Fixes belong
in the generator and its inputs. The owner has not ruled on any of this.

## Pattern 1 — wrong-species name-makers

A species is wired to another species' `nameMaker`. Five found, which makes this systematic
rather than clerical:

| species | gets the name-maker of |
|---|---|
| Ithorian | Sullustan |
| Mon Calamari | Quarren (its canon rival) |
| Ugnaught | Devaronian |
| Kel Dor | Duros |
| Kaleesh | Nagai |

Two species have **no `nameMaker` at all** and therefore fall back to default human names:
**Iktotchi** and **Massassi**.

## Pattern 2 — head art borrowed from the wrong species

| species | wears the head of | why it is wrong |
|---|---|---|
| Lasat | Cathar | feline head on a non-feline |
| Nelvaanian | Bothan | no snout, on a long-snouted lupine |
| Ortolan | Kubaz | wrong snout entirely |
| Mimbanese | Tusken Raider | traced via `SW_HeadTypes.xml:507`/`:234` |

## Pattern 3 — placeholder text shipped as player-facing description

`<description>` is a single character. Five found: **Gand** (`.`), **Lasat** (`e`),
**Ugnaught** (`.`), **Defel** (`.`), **Taung** (`.`). These render as tooltips in game.

## Pattern 4 — the species' signature trait has no gene

The thing the species is *known for* is absent from its def:

- 🔴 **FOUR aquatic species cannot breathe water** — Mon Calamari, Nautolan, Gungan,
  **Selkath**. Every one of them sits in the Deepwater faction, which is the faction built
  around being aquatic. Nautolan's temperature genes are additionally inverted. This is the
  single most consistent defect found.
- **Defel** — no light-absorption or stealth gene of any kind. Its entire art inventory is
  four small fangs.
- **Falleen** — no colour-shift mechanism; four skin genes, all green.
- **Kaminoan** — UV vision is its sole canon distinction and has no gene, while **Umbaran**
  receives dark vision for the same trait.
- **Kel Dor** — oxygen-poisoning biology entirely absent.
- **Bothan** — mood-sensitive fur, the species' one listed distinction, absent.
- **Ortolan** — `Hands_Pig` destroys digits that absorb food and play instruments.

## Pattern 5 — genes invented where canon is blank

Body-size and lifespan genes assigned to species whose infobox fields are empty: **Gand**,
**Chadra-Fan**, **Geonosian**, **Feeorin**. Plus two that contradict a *sourced* figure —
**Taung** has accelerated ageing against a sourced 85-year lifespan, and **Ugnaught**'s
doubled lifespan still undershoots canon's 200+ years.

## Pattern 6 — skin colour wrong, missing, or discarded

- **Wrong:** Zygerrian red (canon: "Light") · Bith mid-brown (all Bith are pale) · Chagrian
  orange (canon blue is causally load-bearing — it is evolved radiation resistance) · Umbaran
  grey (evenly-lit plate reads lavender-violet) · Ithorian blue (sourced orange absent).
- **Missing entirely:** Chadra-Fan · Ugnaught · Abednedo's grey/cream · Ewok's black (cited,
  and the centre figure of its own infobox image).
- 🔴 **Discarded:** Bothan, Gungan, **Duros and Twi'lek** head types set
  `useSkinShader: false` over masks measured as pure greyscale, so **no skin gene can ever
  tint those faces.** A different class of bug — the colour is right and thrown away. Duros
  and Twi'lek are the worst: pure-greyscale texture with **no `CutoutComplex` and no mask at
  all**, so nothing supplies the head a colour by any route, and Twi'lek's 18-gene palette may
  never reach the head at all. ⚠️ Needs in-game confirmation of what actually renders — **the
  top item for the next time the game is up.**
- Duros also has three **blue** skin genes on a species canon calls "smooth blue-**green**",
  whose canon infobox image, Legends image and film photograph all read green or grey-green.
  And its `RSW_Eyes_HugeRed` reuses the **Jawa** eye texture.

## Pattern 7 — aptitudes that invert the source

- **Geonosian** — terrible intellectual, for a species that engineered droid foundries.
- **Gungan** — poor intellectual, against an article that explicitly rebuts the stereotype,
  a Gungan hyperspace physicist, and Filoni on record.
- **Mimbanese** — poor intellectual, against "highly intelligent".
- **Nelvaanian** — poor medicine, against elixir-brewing shamans.
- **Abednedo** — mining/construction, against a sourced linguist culture.
- **Bith** — remarkable artistic, encoding a stereotype canon calls a misconception.

## Pattern 8 — Force-sensitivity assigned backwards

Two exact mirrors of each other: **Rakata** carry psychic genes though post-plague Rakata are
Force-blind; **Devaronian** has canon elevated Force-sensitivity and no gene for it. **Cerean**
carries enhanced psychic ability where the source says its sensitivity is ordinary.

## Pattern 8b — a tint mask cannot express a two-tone animal

**Herglic is an orca.** The Narloch reference shows a white eye-patch and white throat, and
the two canon comic appearances are slate-lavender and blue-purple rather than black. **A
single-channel tint mask cannot produce a patterned animal**, so no gene value fixes this —
it needs art. The same limitation blocks Lasat striping and Cathar stripes, and it means
Iktotchi horns cannot differ in hue from Iktotchi skin (red-channel-only mask).

This is worth separating from the colour-value bugs, because those are data and this is not.

## Pattern 9 — names the repo invented or took from the wrong place

- 🔴 **All three Sith castes are mislabelled "(Pureblood)".** Purebloods are *hybrids*; a
  caste member is a Red Sith. The error is in all three defNames at once.
- **`RSW_RimMandrakeSithZ` spells the caste "Zugurak"; canon is "Zuguruk".** It appears to
  have been taken from a wiki image *filename*, whose own caption reads Zuguruk.
- **Yoda's species has no canonical name — deliberately.** Lucas withheld it, both Databank
  entries say "Unknown", and the wiki title carries a conjecture banner. The repo's "Yoder"
  and "Force Gremlin" are inventions. Naming it is authoring, not correcting.

## The Sith caste split does not survive canon

The repo ships Kissai, Massassi and Zuguruk as three xenotypes. Canon supports a physical
distinction for only two of them:

| caste | canon-exclusive physical trait |
|---|---|
| **Massassi** | 2–3 m and hulking; whole-eye pupil-less yellow |
| **Zuguruk** | five digits, against the usual tridactyl |
| **Kissai** | **none** — nothing physically distinguishes a Kissai from a mainline Sith |

So the split is **occupational, not physical.** Three xenotypes is a design choice, not a
canon requirement — and if it stays, Kissai needs a reason to look different that canon will
not supply.

Worst individual wirings in this group: **Zuguruk has no red skin gene at all**; **Massassi
has no `nameMaker`** while the tough-hide gene sits on Kissai instead; **Dathomirian has no
striping or tattoo gene** and carries the Sith namer; and **Yoder's `RSW_Eyes_Big` models
Grogu's infant face**, with `Hands_Pig` replacing sourced clawed tridactyl hands.

## A methodological finding worth keeping

**Reference images beat prose repeatedly, which is the reason this library exists.** Anooba
text says "varying tones of gray" while three independent images show tiger stripes. Chagrian
lethorns are fleshy lobes, not cream horns. Ithorian hands are blunt, not elongated.

And **lighting is a trap**: Umbaran reads green-teal in a screencap and near-white on one
character, purely from ambient light; Ugnaught reads salmon in Cloud City furnace light while
live-action Kuiil is dun grey-brown. Only evenly-lit plates were trusted, and misleading
images are kept as **labelled negative references** rather than deleted — including two in
`rakata/` that Wookieepedia explicitly disowns (a mislabelled Mon Calamari, and a figure
Lucasfilm confirmed is "generic alien extra #3457").

## Not everything came back a complaint

Worth recording so the library reads as evidence rather than advocacy:

- **Batch H's four existing name-makers were all the right species**, and none of its five
  species invented a body-size or lifespan gene. The bugs are not uniform.
- **The Mirialan and Pantoran head graphics already bake canonically-placed markings, and
  Pantoran's gold really is gold.** Do not "fix" these.
- **`RSW_Beard_chinspines` exactly matches the Zygerrian chin spurs.**
- **One finding reversed in the def's favour:** the Iktotchi reference images support the
  def's reds *against* Wookieepedia's own "Tan/Pink" infobox. The images won, which is the
  rule working in the direction nobody expected.

## Pattern 10 — a gene that is decoration where canon makes it an organ

**Togruta montrals** are the clearest case. `RSW_TogrutaMontrals` and its abstract base carry
`renderNodeProperties` **and nothing else** — no `capMods`, no `statFactors` — and the gene's
description never mentions hearing. In canon the montrals *are* the auditory system, with 25 m
echolocation. The art compounds it: montrals tint from **hair** colour, the xenotype's six hair
genes are all saturated with `Hair_Grayless`, and canon montrals are pale with dark bands in
every reference. The montral texture has **no banding at all**, the lekku stop at jaw level,
and the third and thickest rear lek is missing entirely. Head variants 0–3 are byte-identical
apart from the mask.

Same shape as Kaminoan UV vision and Kel Dor's oxygen biology: the species' defining organ is
present as a shape and absent as a function.

## Two smaller findings

- **Twi'lek has no red gene, so there are no Lethan Twi'leks** — one of only two named canon
  races. Black, grey and pale are also missing, and pale is roughly a third of every crowd
  shot. `Turn_Gene_FrailDigestion` inverts canon's multiple stomachs.
- **Name-maker files that no rule references.** Togruta and Twi'lek both bind a `Last` name
  file that appears in no rule, so **surnames are drawn from the first-name list.** Worth
  checking across all 69, since it would be invisible in play except as odd names.

## 🔴 One finding that is an owner call, not a bug

The Twi'lek def carries `Turn_Gene_AgressionSubmissive`, `Libido_High` and `Beauty_Beautiful`.
Together these **encode the slavery trope as biology** — the in-fiction stereotype becomes a
species-level fact about every Twi'lek in the game. Canon treats the trope as something done
*to* Twi'leks, not something true of them.

Flagged, not touched. This is a content decision and it is his alone.

## Open for the owner

- Fix in the generator, or accept some of these as deliberate game-design departures from
  canon? Several (aptitudes, lifespans) may be balance choices rather than errors.
- The three aquatic species and the `useSkinShader` masks look like straightforward bugs.
  Do they go to FOUNDRY now, or wait for a full ruling pass?
- Bothan is a special case: canon deliberately has **no** appearance for them. Choosing one
  is authoring, not correcting — his call alone.
