# Sweetline tree name register — the Leaning Scrub (DRAFT 2026-10-03)

**DRAFT for the owner. Nothing here is ruled.** Item: `LEANINGSCRUB_SWEETLINE_NAME_REGISTER_1`.
The vocabulary below is already written into `RM_NamerSweetlineTree`
(`src/RimMandrake/LeaningScrub/Defs/RulePackDefs/RM_LeaningScrub_Namers.xml`) so it can be
judged in a save, but it is **not deployed**. Strike what you dislike, or say *"all fine"*.
Trees already named in a save keep their saved name whatever is ruled here.

## Who names the trees

The sweetline trees are huge, ancient and each grows only on the optimum, so each one is a
surveyor's mark visible for a day's walk; the roads run tree to named tree
(`arid_shrubland.md` §4 "The sweetline trees", §8 "The sweetline tree-roads"). The people who
need those names are **the road-folk**: the moisture farmers and hedge-fort households who walk
the tree-roads between farmsteads, and give directions by them ("two trees past Gomaun, then
downwind").

That gives the register two layers, and the draft uses both:

- **An old name, in an older tongue.** The trees are older than any farm. Their names were
  given long ago and are said, not understood — the way a river keeps a name nobody can
  translate. These are coined words.
- **Plain speech laid on top.** What the road-folk add themselves: an epithet for how the tree
  looks or behaves, or a name for something that happened there. These are English.

Nothing in it is campaign- or franchise-specific, so it is fit for the `RM_` tier (Q11a: an
invented word is not Star Wars IP). No canon name appears anywhere in the def.

## Phonology and morphology

1. **Heavy, slow and open — the opposite of the runway creatures.** The shrubland's small fast
   beasts carry a bright accent of doubled *p* and *t* (`pattu`, `tuppi` in the beast-names
   draft). The trees get the other end of the mouth: sonorants (*m, n, l, r*), voiced stops
   (*b, d, g*), back and open vowels (*o, u, au, a*). No *p, t, k* at all.
2. **Two parts: a stressed root, then an ending.** Root is one heavy syllable
   (`Barr`, `Dolm`, `Gom`, `Hul`, `Lom`, `Morr`, `Ombr`, `Rhun`, `Ulb`, `Aud`, `Bel`, `Gaur`);
   the ending is unstressed. Two or three syllables, stress always first: **GO**-maun,
   **OM**-bra-ra.
3. **Endings carry a half-remembered meaning** (flavour for the doc and future descriptions;
   the player is never told it): `-ol` *the one that stands*, `-aun` *the first, the old*,
   `-ara` *the one that leans*, `-umo` *the rubbed one* (by giants), `-ond` *on the road*.
4. **Plain-speech additions follow the farmers' manners:** blunt, practical, one word where
   possible — what a traveller would actually say to tell one landmark from the next.

Every coined word (50 of them) passed `src/RimMandrake/Utils/check_pseudo_sw_name.py`
(50/50, shape + no collision with the 138 canon entries), a sweep against every `<label>` in
`src/` (17,878 labels, probe `bokka` hit 8, 0 collisions), and a Wookieepedia `list=search`
sweep (probe `bantha` hit, `zzqxxv` missed). Two near-misses were dropped (`Barrara` → *Barra*,
`Barrond` → *Barron*), and a few that read as English words or real places were dropped by ear
(`Barrol` *barrel*, `Belond` *blond*, `Lomond`, `Hulara` *hula*).

## Patterns and samples

The engine rolls one pattern per tree (weights from the def), title-cases it, and re-rolls
until the name is unique among the sweetline trees on the map. It shows in game as
*"Gomaun (sweetline tree)"*; the history panel opens with *"named Gomaun."*

### A. The old name alone — weight 4 of 9

The plainest and most common: just the tree's word.

> Gomaun · Dolmara · Lomara · Hulol · Audumo · Ombrara · Rhunumo · Morraun · Ulbond ·
> Gaurol · Belumo · Audond

### B. The old name with a plain-speech epithet — weight 3 of 9

`[name] the [epithet]` (2) or `Old [name]` (1). Epithets: *Leaner, Patient, Unburnt,
Far-Seen, Woolgiver, Rubbed, Grey, Waymark*.

> Dolmaun the Woolgiver · Barrumo the Far-Seen · Gaurol the Woolgiver · Morrara the Leaner ·
> Ombrond the Waymark · Hulaun the Unburnt · Lomol the Patient · Rhunara the Grey ·
> Old Gomumo · Old Belaun · Old Ulbara

*Unburnt* is a nod to §4's fire lore (a tree that has outlived a calling-pyre); *Woolgiver* to
the giant-wool harvest; *Rubbed* to the giants scratching their flanks on it.

### C. The event name — weight 2 of 9

`Where the [Giant | Giants | Wind] [Knelt | Slept | Turned | Waited | Lay Down | Stood Still]`
— a name for something the road-folk saw there once, kept because it was strange.

> Where the Giant Knelt · Where the Giants Slept · Where the Wind Stood Still ·
> Where the Giant Waited · Where the Wind Turned · Where the Giants Lay Down ·
> Where the Wind Knelt

*"Where the Wind Stood Still"* is a Stall remembered (§5: a still hour is an event).

The full space is 50 + 400 + 50 + 18 = **518 distinct names**, far more than any map holds.

## Questions for the owner

1. **Is the two-layer register right?** (a) As drafted: old coined names plus plain-speech
   epithets and event names — reads as a lived-in road culture, but mixes two languages.
   (b) Coined names only (pattern A alone) — the most alien and uniform, but every tree reads
   alike and the player gets no hint what any of them is like. (c) Plain English only (event
   and epithet names with no coined word) — instantly readable, but loses the sense that the
   trees are older than the people.
2. **Should a tree ever be named after a person** — *"Ossa's Mark"*, *"the Widow's Tree"* — as
   the item asked? Yes adds human history to the roads and fits "my grandmother darkened this
   stand" (§8), but it needs a source of person names and pulls attention from the trees
   themselves toward the farmers; no keeps the trees impersonal and ancient. The draft leaves
   it out.
3. **Is "Where the …" too long for the map?** It is the most evocative pattern but the longest
   label (up to 24 letters plus "(sweetline tree)"). Options: keep it at weight 2 of 9 as
   drafted; drop it to a rare 1 in 9; or cut it and add more epithets instead.
