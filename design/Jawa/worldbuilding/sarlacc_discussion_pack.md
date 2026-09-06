<!-- status: DISCUSSION PACK for the live sitting — SARLACC_NATIVE_HABITAT_1, DESIGN subagent
     2026-09-06. Nothing here is ruled; nothing decided on the owner's behalf. It sits ON TOP of
     sarlacc_native_habitat_draft.md (the overnight Fable draft, same item) — it does not repeat
     that draft, it frames the CHOICES around it. Read the draft first if only one doc gets read. -->
# The Sarlacc — discussion pack for the sitting

Item: `infrastructure/state/items/SARLACC_NATIVE_HABITAT_1.md`. Premise binding everything:
**the sarlacc is a well, not a predator; killing one is campaign-scale; it reads as grown in
place.** Kept deliberately OUT of `biomes/deep_desert.md` (its ticket, sheet's "Owed" list).

## 1. What exists today (MEASURED unless marked)

| artifact | where | state |
|---|---|---|
| **Donor defs** (mlie.starwarsanimalcollection, vendored) | `vendor/mod_sources/StarWarsAnimalCollection_src/1.6/Defs/ThingDefs_Buildings/SW_Buildings_Natural.xml` | `SarlaccPit` ThingDef (Odyssey-gated): 9×6 impassable `Building_WorkTable`, `FeedCorpse` recipe, `CompProperties_Spawner` regurgitating ChunkSlagSteel, Morbid meditation focus, ambient call — and 🔴 **player-buildable from `SarlacciSpore` + 300 Silica_Meat**. Also `sw_Sarlacc` / `sw_DeadSarlacc` LandmarkDefs → `sw_SarlaccLair`/`sw_DeadSarlaccCave` TileMutatorDefs → GenSteps scattering the building; a MapGeneratorDef with Anomaly `Fleshmass` gensteps |
| **No creature def anywhere.** | `src/RimStarWars/SWBestiary/About/About.xml` | absorption item's own finding, verbatim: "Sarlacc was found not to be a creature at all (an Odyssey-DLC building system) and is out of this item's scope" |
| **Sounds, absorbed** | `src/RimStarWars/SWBestiary/Defs/SoundDefs/SoundDefs_SWBestiary.xml` | `RSW_Pawn_Sarlacc_{Call,Call_Ambient,Eat,Angry,Wounded,Death,Butchered}` — a full vocal set already under our prefix |
| **Landmark icon patches** | `src/RimUtinni/AshkarrLandmarkArt/Patches/LandmarkIcons.xml` | both `sw_Sarlacc` and `sw_DeadSarlacc` patched to `World/Landmarks/Ashkarr/…`; world art itself still owed (`sarlacc_spec.md` §1: all five render magenta) |
| **Placements on Ash'karr** | `sarlacc_spec.md` §1; `src/RimMandrake/Utils/ashkarr_landmarks.py:190` | `sw_DeadSarlacc` ×4 (Glare · Dry Marches · Kiln · Pale Flats), `sw_Sarlacc` ×1 (Dew Belt, tile 2920). ⚠️ Live world-state not re-verified this pass — UNMEASURED against the running game |
| **Engine measurements** | `design/Jawa/worldbuilding/sarlacc_spec.md` (2026-08-31, rimsage-sourced) | emergence = `GroundSpawner` family in XML; **no non-pawn animator → tentacles must be pawns**; `PitGate : MapPortal` self-contained; **pocket-map nesting unenforced = stacked levels legal**; collapse timer reusable; 🔴 frozen save must be created `AmbientHorror` + Custom difficulty |
| **Rulings** (owner, 2026-09-02, verbatim in doc) | `design/Jawa/proposals/sarlacc_deep_design.md` §🔴 RULED | **many sarlaccs, semi-permanent when huge, smaller mobile ones**; compile-digestion ⛔ CUT; evidence-feeding → "rite of offering and forgetting" v1; sneak-up-able v1; Anomaly draws v1; returning-changed v1; sky-seeding ⛔ CUT; castings = "Sarlacc pearls"; cavern root crosslink yes |
| **The overnight draft** | `design/Jawa/worldbuilding/sarlacc_native_habitat_draft.md` (2026-09-06, unruled) | a complete three-stage design (swimmer / anchored / cistern, dead = throat), the press-not-stomach mechanism, dew ring, apron strata, ecosystem table, dungeon levels, carve-out wording, 9 forks |
| **Dungeon siblings** | `infrastructure/state/items/VAULT_DUNGEON_BUILD_1.md` · `ASSAILANT_FLESH_DUNGEON_1.md` | vaults: KCSG `StructureLayoutDef` templates BUILT and geometry-verified, 325×325 maps, ⛔ no Anomaly for them; Assailant: Anomaly fleshmass ALLOWED (the exception the sarlacc tentatively shares, `canon.yml anomaly_content`) |
| **BeastLairs** | `src/RimStarWars/BeastLairs/Defs/ThingDefs_Buildings/RSW_BeastLairs_Buildings.xml` | one def, `RSW_BeastNest_Large` — dressing-only lair building pattern (no spawner comp, never player-buildable). **No sarlacc content**; useful only as the house pattern for inert lair scenery |
| Vision doc | `research/Jawa/rimworld_sarlacc_encounter_current_design.md` | cited by both specs as foundation — UNMEASURED this pass (not re-read) |
| Biome menu | `biomes/_assignment_prep.md:110` | "Sarlacc: its own item … not part of this menu" — the carve-out is already respected there |

🔴 **Immediate defect regardless of any ruling:** the donor `SarlaccPit` is a *buildable
corpse-disposal worktable*. A player growing a sarlacc from a spore and 300 meat contradicts
grown-in-place, campaign-scale, and the well premise all at once. It needs a cherrypick/patch
decision (card D1).

## 2. Three-stage proposals — alternative framings

The item's main design work. Three framings, each honouring: well not predator · killing one
is campaign-scale · grown in place · "many, semi-permanent when huge, smaller mobile ones."

### Framing A — the water ladder (the overnight draft's)
Stage = how much water one individual holds; mass IS the balance sheet (`deep_desert.md` §4).
**I swimmer** (a pawn: sub-sand PawnKindDef, appraises like every biome predator, born from a
canteen-egg, a countdown) → **II anchored** (a building + a few tentacle pawns: rooted on a
seep, pit that breaks the yardang grain, dew forming at the lip) → **III cistern** (landmark +
`PitGate` portal + pocket maps: the water table itself, ecosystem attached) → *(dead) throat*
(the husk delve; most swimmers root badly and this is what failure looks like).
*Player experiences*: a creature, then a hazard-site, then a place. *Strength*: one organism,
one arc, the biome's own physics does all the explaining; failure states (throats) are already
on the map ×4. *Cost*: three engine shapes for one species; a swimmer-pawn must not read as
"just a big animal."

### Framing B — the seep succession (stage is the SITE's, not the animal's)
Sarlacci are a *population*: many small mouths (Stage I, a spawn-pool of modest pawns around
brine seeps and cavern mouths — the "smaller, more mobile ones" as a species, killable, even
huntable for their water). Where a seep is rich, several root and **compete underground for
decades; one absorbs the rest** (Stage II: a contested pit — multiple small mouths in one
depression, occasionally striking each other). Stage III is the winner, centuries later, fused
with the rock. *Player experiences*: sarlacc as vermin, sarlacc as territory war, sarlacc as
god — same name, three registers. *Strength*: makes "many" literal and cheap (Stage I is a
biome roster entry); explains why cisterns are rare without any transition ever firing in play.
*Cost*: dilutes the icon — a killable small sarlacc risks the recognizability carve-out cutting
the other way (the mouth everyone can name, dying to one gunshot); competition-underground is
pure lore, hard to show.

### Framing C — the ecosystem clock (stage = what has grown AROUND it; danger inverts)
All placed individuals are the same organism at different ages of *tenancy*: **young** — bare
pit, no ring, strikes anything (the only predator-acting stage; small kill, small guilt);
**mature** — dew ring + first tenants + silverbole seedlings, tithes rather than hunts;
**ancient** — full ring, almost never strikes, *safest place in the deep desert to stand* and
the worst thing on the planet to kill. *Player experiences*: reading a site's age from its ring
before deciding anything; the moral scale is visible as dressing. *Strength*: zero transition
mechanics (three tuning variants of one building def + dressing per site — the BeastLairs
inert-scenery pattern does the ring); the danger-inversion is the premise stated as gameplay.
*Cost*: no mobile stage at all — "smaller, more mobile ones" must be read as the young pit's
longer tentacle reach, which may not be what the owner meant.

**These compose.** A ⊃ C (A's stages, C's dressing rule) and A ⊃ B's Stage-I-as-roster-entry
are both coherent hybrids; the sitting picks a spine, not a cage. The draft's fork 1
(transitions in play vs authored-only) applies to whichever spine wins.

## 3. Dungeon-module options

How "a dungeon-like module" is done elsewhere: vaults = **KCSG surface templates** (proven,
built, no Anomaly); Assailant = **fixed site + Anomaly fleshmass fabric** (ruled allowed);
sarlacc shares the Anomaly exception "tentatively" (`canon.yml` via VAULT item's Watch-out).

| option | shape | cost/risk | what it buys |
|---|---|---|---|
| **D-1 stacked pocket maps** (`sarlacc_spec.md` §3, the green-lit route) | `RSW_SarlaccMaw` PitGate → nested Undercave-style levels (press → gallery → reservoir per the draft §4.1); swallow-as-entrance; breach-flood collapse; cavern-root second entrance | highest; nesting soft-risks measured (no shuttle/quest targeting below level 1); PitGate is Anomaly machinery → the AmbientHorror save prerequisite hardens | the owner's verbatim "deep sarlacc dungeon experience"; the only route where the kill decision happens *in the room* |
| **D-2 single pocket map, KCSG-laid** | one portal, one level; interior authored as a `StructureLayoutDef` (organic template — the vault pipeline with flesh symbols; Anomaly fleshmass dressing per the exception) | low — reuses the built, geometry-verified vault toolchain; no nesting risk | a real interior at a fraction of D-1; loses depth, flooding drama becomes one-level |
| **D-3 surface complex only** | no interior map: the pit as a large inert building cluster (donor `SarlaccPit` reworked non-buildable + `RSW_BeastNest_Large`-pattern apron dressing + tentacle pawns) | cheapest; v1-shippable now; no DLC-playstyle dependency for the site itself | the landmark reads and plays TODAY; "dungeon-like" only in the sense a lair is |
| **D-4 the ladder** (recommended shape in both specs already) | D-3 ships v1 (matches the standing "v1 takes the mod's landmark" ruling) → D-2 as husk delves → D-1 for THE live cistern(s) | spreads risk along `sarlacc_spec.md` §7's phase gates | every phase is independently shippable; nothing waits on the whole |

⚠️ Whichever option: tentacles are pawns (measured, no building animator), and husk delves may
dodge the AmbientHorror prerequisite if built on our own portal def — `sarlacc_spec.md` §8's
open check, still unchecked.

## 4. The deep-desert carve-out — wording options

Current ban (`deep_desert.md` §6.5): *"No green in the open, and no standing surface water
except brine seeps."* Three ways to carve the sarlacc out, strictest to loosest:

**W-A — the draft's full clause** (`sarlacc_native_habitat_draft.md` §5, verbatim there): the
cistern's water is "neither standing nor surface — inside a body, behind flesh"; names the only
two permitted surface expressions (dew ring: damp, never pooled; breach flood: on the biome's
own hours-to-days bloom clock) plus three disqualifying tests. *Pro*: linter-checkable, closes
the "sarlacc-fed oasis" loophole by construction. *Con*: ~9 lines in a ban list that is
otherwise one line each.

**W-B — minimal amendment**, one line:
> 5. 🔴 No green in the open, and no standing surface water except brine seeps. **Water inside
> a living sarlacc is not surface water; it may reach the surface only as damp sand at a pit's
> lip, or as the transient breach flood, never as a water terrain cell.**
*Pro*: keeps the sheet's register; still names the two expressions. *Con*: the three tests live
only in the sarlacc doc — a future generator author must follow the pointer.

**W-C — pure pointer**:
> 5. 🔴 No green in the open, and no standing surface water except brine seeps. **(Sole
> exception: the sarlacc — carve-out defined in its own item, never in this sheet.)**
*Pro*: honours "kept OUT of the biome sheet" most literally; the sheet never grows sarlacc
content. *Con*: a ban with a non-local exception is exactly the kind of line the two-blind-arms
audit kills later; weakest against drift.

All three keep the green ban and the three-shade-sources rule untouched (the silverbole ring
is already one of the three). Recommended default: **W-B in the sheet, W-A's tests in the
sarlacc design doc**, cross-cited both ways per the superseding rule.

## 5. Decision cards (one line each; ✦ = recommended default)

- **C1 Adopt the overnight draft as the working spine?** ✦ yes, as-amended-in-sitting — it is
  the only doc reconciling the 09-02 rulings; §6 of it lists the strikes `sarlacc_spec.md` needs.
- **C2 Stage framing:** A water-ladder / B seep-succession / C ecosystem-clock / hybrid. ✦ A
  with C's dressing rule (age readable from the ring).
- **C3 Do stage transitions ever fire in play?** ✦ no — authored only; timescales are lore
  (frozen-map-clean; draft fork 1a).
- **C4 Dungeon route:** D-1 / D-2 / D-3 / ladder. ✦ D-4 ladder — v1 surface site, husk delve
  next, live cistern last, per the specs' own phases.
- **C5 Carve-out wording:** W-A / W-B / W-C. ✦ W-B in the sheet + W-A's tests in the design doc.
- **D1 Donor `SarlaccPit` buildability:** ✦ cut/patch the recipe & costList — a spore-built
  sarlacc breaks grown-in-place; keep the def as the v1 site building otherwise.
- **D2 The Dew Belt live sarlacc (tile 2920, not a deep-desert region):** move it deep / keep
  as the "teaching" cistern (draft fork 2b) / demote to dead. ✦ keep as teaching cistern —
  generous, and the deep-desert ones stay the campaign-scale kills.
- **D3 How many live cisterns, where:** ✦ 2–4 total, the rest of "many" carried by swimmers/
  anchored pits and the four existing throats.
- **D4 Are sarlacc clutches THE biome's birth-trap eggs?** ✦ one species of several (draft
  fork 4b) — keeps the biome roster free.
- **D5 Poison-the-rite as a kill route:** ✦ no for v1 — the only kill is the breach, in person.
- **D6 "Campaign-scale" blast radius of a kill:** tile+tribe vs whole-arc roster changes.
  ✦ tile+tribe first (buildable, verifiable), arc-scale as v2.
- **D7 Returning-changed menu (draft §4.5):** which hediffs ship, how many per survivor.
  ✦ one rolled per survivor, matched to how they were taken.
- **D8 Confirm the AmbientHorror+Custom scenario line is filed against the frozen-save item**
  before any save is authored. ✦ yes — it is a deadline, not a preference (`sarlacc_spec.md` §6).
- **D9 Stage names:** swimmer/anchored/cistern/throat vs tribal words as shipped labels.
  ✦ plain nouns in defs/sheets; tribal names in lore text.
- **D10 Swimmer vs the biome's "no large surface herds" ban:** ✦ swimmers are solitary and
  sub-sand — compliant; write the one-line note into the fauna roster when admitted, not the sheet.

## Owed after the sitting
Rulings propagated: strikes into `sarlacc_spec.md` (its §1 "one sarlacc" language, "ONE ever"
pearl, digested-memories layer), the ban-5 edit INTO `deep_desert.md`, the item file updated,
and this pack superseded by the ruled design doc.
