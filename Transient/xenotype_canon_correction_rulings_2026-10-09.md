# XENOTYPE_CANON_CORRECTION_1 — re-measured 2026-10-09, with draft rulings

READ-ONLY audit. No defs changed. Instrument: python census over
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml` (69 XenotypeDefs;
sanity probe: Abednedo carries `Skin_Orange`, minimum description length is 69 chars so
"0 placeholders" is a real zero), `HeadTypeDefs/SW_HeadTypes.xml`, `RulePackDefs/SW_NameMakers.xml`,
git log, and the ledger notes. Canon claims below are the item's / library's own; nothing was
re-sourced tonight, so each row that rests on canon says "per library".
Already settled and EXCLUDED: every ability gene the sister audit covered
(`UNSUBSTANTIATED_SPECIES_ABILITIES_1`, applied `87888849a`), including Rakata KEEP,
Iktotchi KEEP, Cerean psychic removed, Duelist KEEP, Gungan poor-intellectual ruled to STAY.

## 1. Pattern status (originally filed vs now)

| # | pattern | filed | now | fixed by |
|---|---|---|---|---|
| 1a | wrong-species name-makers | 5 | **0 wrong** — but see 1c | `24c711562` (removed, not replaced) |
| 1b | no nameMaker (Iktotchi, Massassi) | 2 | **1** (Iktotchi) | Massassi `5d5a16577` |
| 1c | NEW: species with no name-maker at all | - | **23 of 69** fall back to human names | n/a |
| 1d | NEW: surname file never referenced | 2 (Togruta, Twi'lek) | **39 of 45** namers | n/a |
| 2 | borrowed heads | 4 | **4** (Lasat, Nelvaanian, Ortolan, Mimbanese); art rendered in artpipe (`xeno_head_*_v1`, 12 jobs), not wired | open |
| 3 | placeholder descriptions | 5 (really 9) | **0** | `24c711562` |
| 4 | signature trait has no gene | 7 | aquatic x4 fixed; **6 open** | `e7c8042db` |
| 5 | invented body/lifespan genes | 6 | **6 open** | open |
| 6 | skin colour | ~12 | most fixed; **4 open**; discarded-skin class fixed | `f60d197b0`, `b2a800d5c`, `2aa93993b`, `9234b1db4`, `185518a53`, `bb51a1aac` |
| 7 | inverted aptitudes | 6 | 5 fixed, Gungan ruled STAY; **1 new question** (Nelvaanian) | `d1cfa1d69` |
| 8 | Force-sensitivity backwards | 3 | Rakata/Cerean settled by sister audit; **Devaronian open** | sister `87888849a` |
| 9 | invented names | 3 | Pureblood label + Zugurak spelling fixed; Kissai defName renamed; **Yoder open**; generator table stale | `24c711562`, `f894fe574` |
| 10 | Togruta montrals decorative | 1 | **1 open** | open |
| - | Twi'lek trope genes | 1 | done | `fc16d5507`, closed `b479016a8` |

Fixed-pattern totals: 3 fully fixed (3, 7-except-Nelvaanian, 9-labels), 4 partly, 5 open.

## 2. NON-COSMETIC draft rulings (ranked by effect / cost)

1. **Surnames are drawn from the first-name list for 39 of 45 name files.** Each namer ships a real
   `Last.txt` (probe: Bith/Last.txt exists) but the rule text never uses it, so a pawn is "Gorn Vell"
   with two given names. Draft: point surnames at the surname file for all 39. Changes: pawn names
   read as real first+last names. Cost: mechanical, one pass, existing pawns keep names.
2. **23 species have no name-maker and get plain human names** (incl. Ithorian, Mon Calamari,
   Ugnaught, Kel Dor, Kaleesh, Iktotchi, Zuguruk, Rakata, Selkath, Kaminoan). The 5 wrong ones were
   removed rather than replaced. Draft: author a name list per species from canon names, start with
   the 6 owner-visible ones. Changes: a Mon Calamari is named "Raddus", not "Brian". Cost: real
   authoring (lists), no code. Or accept human names as a deliberate gap.
3. **Devaronian lacks the Force-sensitivity canon gives them (per library).** Draft: add one
   `PsychicAbility_Enhanced`-class gene, or decide Devaronians are not special. Changes: Devaronians
   get a modest psychic bonus. Cost: one gene.
4. **Taung age too fast.** Sourced lifespan is 85 years; `Outland_AcceleratedAgeing` contradicts it
   (owner already ruled "sourced figure wins"). Draft: remove that gene. Changes: Taung stop dying
   young. Cost: one gene.
5. **Invented size/lifespan with nothing in canon** (owner rule: borrow the nearest documented
   relative and say which): Gand (small, half lifespan), Chadra-Fan (smaller, half), Geonosian
   (small, accelerated ageing), Feeorin (bigger; quad lifespan was KEPT by sister ruling R4).
   Draft: keep Gand/Chadra-Fan/Geonosian as deliberate flavour, name the borrow in the description.
   Changes: nothing in play. Cost: text only. Alternative: strip them.
6. **Ugnaught lifespan** doubled but canon is 200+ (per library; sister audit flags the same).
   Draft: raise to the next multiplier. Changes: Ugnaughts outlive humans by more. Cost: one gene.
7. **Nelvaanian carries `AptitudePoor_Intellectual` and `AptitudePoor_Plants`** after only Poor_Medicine
   was removed. Canon: shamans who brew elixirs. Not in his earlier rulings. Draft: remove Poor_Intellectual.
   Changes: Nelvaanians no longer dim. Cost: one gene.
8. **Missing function for signature traits (no vanilla gene exists):** Kaminoan UV vision (Umbaran has
   DarkVision for the same kind of trait), Defel light-absorbing stealth, Kel Dor oxygen biology,
   Bothan mood-sensitive fur. Draft: Kaminoan get `DarkVision` as stand-in; the other three wait for
   `SPECIES_TRAITS_OVER_APTITUDES_1` (custom traits). Changes: only Kaminoan now. Cost: one gene / design.
9. **Twi'lek `Turn_Gene_FrailDigestion`** inverts canon's multiple stomachs. Draft: remove it, or
   swap for `StrongStomach`. Changes: Twi'lek stop getting food-poisoned easily. Cost: one gene.
10. **Yoda's species is named "Yoder"/"Force Gremlin" (repo invention).** Canon withheld a name.
    Draft: keep the invented label but write in the description that it is unnamed in canon. Changes:
    tooltip text. Cost: text. Naming it is authoring, so only if he wants.
11. **Generator hazard (not a def bug):** `gen_races_mod.py` still holds a rescued-species table whose
    SithZ entry says "Zugurak (Pureblood)" (line ~1439). It is not wired, but wiring it would revert
    both fixes. Draft: correct it in the generator now. Cost: text. (Safe to do without him; listed
    for completeness.)

Not asked: Gungan poor-intellectual (ruled STAY), Chagrian blue-only and Ugnaught pink (ruled
departures), Sith three-caste split (ruled keep, no invented biology).

## 3. COSMETIC items — NEED HIS EXPLICIT PERMISSION (can break animated faces)

C1. **Four borrowed heads** Lasat/Cathar, Nelvaanian/Bothan, Ortolan/Kubaz, Mimbanese/Tusken
    ("Devolved"): replacement art already rendered (12 files, `xeno_head_*_v1`, artpipe done/).
    Draft: wire the new heads and re-run the xeno grid. Changes: those four stop wearing another
    species' face. Cost: wiring + one grid shot. Also note Zygerrian wears the Cathar head (unflagged
    before; check against canon).
C2. **Duros skin**: three blue genes, canon "smooth blue-green"; eyes reuse the Jawa eye texture.
    Draft: add a green-blue gene, new eye. Cost: art.
C3. **Falleen**: all four skin genes green; colour-shift has no mechanism. Draft: add yellow-green to grey-green
    variety only (the shift needs a mechanic). Cost: genes now, mechanic later.
C4. **Twi'lek palette**: no red (Lethan), black, grey, pale. Draft: add Lethan red + pale.
C5. **Zuguruk** has no red skin gene though it is a Red Sith; five-digit hands. Draft: add red skin gene.
C6. **Togruta montrals** (also half functional: no hearing/echolocation stat) and Herglic two-tone
    (needs art, a mask cannot do it), Iktotchi horn hue, Dathomirian striping, Yoder big eyes and
    `Hands_Pig`, Ortolan/Kel Dor/Gand `Hands_Pig`. Draft: park all as art jobs; ask one at a time.
C7. **Skin-shader flags**: the "discarded skin" class (Bothan/Gungan/Duros/Twi'lek) was fixed by
    `bb51a1aac` (29 faces); 3 baked-colour heads (Bith, Nikto, Geonosian) keep the flag on purpose.
    Nothing owed unless the grid review finds a grey face.

## 4. Caveats
- Canon assertions (Devaronian, Kaminoan, Taung 85 y) come from the item/library; Taung's figure is
  quoted from `canon_references/taung/description.md`.
- Nautolan's temperature genes were filed as "inverted"; not re-checked here (gene semantics unmeasured).
- Gene lists inspected by presence only; whether a gene renders is not established (see skill §3a).
