# The Webwork — owner species, silk name, nest and egg economy (sitting record)

_Owner + BENCH, 2026-09-23 sitting; drafted by a Fable design subagent against the frozen sheet._

**Status: DESIGN PROPOSAL. Nothing authored.**

## READ FIRST — what this record is

This is the **sitting record** for the Webwork's own roster sitting of 2026-09-23. It records six
rulings taken by question card and turns them into design detail under the frozen sheet's own rule
(`the_webwork.md`: *amendments add detail; they never change a ruling*). Companions, same sitting,
same naming register:

- `webwork_flora_roster_2026-09-23.md` — the invented flora (the thicket, the root-mat, the pale
  flowers, the tap-trees, the nightmare plants).
- `webwork_fauna_roster_2026-09-23.md` — the thin resident cast besides the owner species.

🔴 **Nothing here changes a sheet ruling.** Where a design question could not be answered without
changing one, it is in §6 (needs owner ruling), not written as fact. Every mechanism in sheet §4
(mouth-loom, commandable adhesive, mandibles, leg-blades, venom, web-sense, hates droids,
sun-helpless, untameable, fecund and self-predating) is **mechanism, not IP**, and carries to the
free-tier species unchanged. Every hard ban in sheet §6 still holds.

🔑 **The precedent this copies:** `fever_wood_deep_and_mud_2026-09-23.md` §1/§1a — the Fever Wood's
invented **Sekkulaath** in the free tier, mapped to the dianoga when the campaign layer is active.
Same shape here: an invented spider of ours, mapped to the Wyyyschokk under Utinni.

Tier law cited, not re-derived: `design/RimMandrake/biome_mod_architecture.md` §7 **Q11** (a `RM_`
def never names Star Wars content), **Q11a** (an invented exotic name is not IP — the line is
provenance, not flavour, and the free mod must look the same as the campaign one), **Q12** (`RSW_`
→ `RM_` renames happen per biome at its sitting — this is that sitting), **Q13** (content in two
mods is duplicated then diverged, never shared), **Q15** (biome mods are top-level; campaign
patches apply beneath).

## §0 The six rulings of this sitting (data)

All six are **decisions taken by question card** (clicked options), 2026-09-23. None is a quote of
the owner; ⛔ do not cite any of these as owner-verbatim.

| # | ruling | consequence recorded here |
|---|---|---|
| 1 | The free-tier Webwork's owner species is an **invented spider of ours**. When the campaign (Utinni) layer is active it **maps to the Wyyyschokk**. Same shape as the Fever Wood's Sekkulaath → dianoga. | §1. The `RM_` biome is whole without Star Wars; the Wyyyschokk is an over-mapping, never a substitute for an impoverished base (Q11a). |
| 2 | **ONE race, ONE kind.** No castes, no guild. The parked guild names nettik / chirrik / rothrik are **not used**. | §1a. `rosters/the_webwork.json` `new_defs` row "Wyyyschokk guild pawnkinds (nettik/chirrik/rothrik)" is dead, and the sheet's Owed line offering those clade names is discharged negative. Ambusher vs. roamer is a *state* of the one kind (dormant or not), never a second PawnKindDef. |
| 3 | Its name is **Ollathrix** (the owner's pick from three proposed). | §1b fixes the plural and the register. |
| 4 | The silk (hyperweave renamed, sole source — sheet §7) is named **after the spider in the free tier**; under Utinni it patches to **Shokkweave**. | §2 picks the word-form and makes the rename two-layered. |
| 5 | Resident cast besides the spider is **very thin, 4–6 rows**: anchor-beetle, egg-mite, one or two trace prey, one trace flier. Every row carries a war or a use; **silence is doctrine**. | `webwork_fauna_roster_2026-09-23.md` — 5 rows. |
| 6 | **Nests and the egg economy are designed this sitting**: the nest as a raidable place, eggs as the smuggler's jackpot, the carried-eggs mark (sheet §7, §8). | §3, §4. |

Standing rules that also bind this record: invent-first-then-inject (owner, 2026-09-23, quoted in
`fever_wood_flora_roster_2026-09-23.md` READ FIRST); one animal one biome (CLAUDE.md); evictions
are stopped as a sweep but this is the Webwork's own sitting, so dispositions are PROPOSED in the
roster docs and executed by nobody here; if it flies in the fiction it flies in the game.

## §1 The Ollathrix — one race, one kind

### 1a. What it is — `RM_Ollathrix`, and nothing beside it

**One `ThingDef` race, one `PawnKindDef`, both `RM_Ollathrix`**, cast inline in `RM_Webwork`'s own
`<wildAnimals>` (Q11a: an invented name is not IP, so the free biome carries its own owner species).
No castes, no guild, no juvenile kind, no "ambusher" kind: **the dormant ambusher and the roaming
hunter are the same PawnKindDef in two states** (kit spec §2 — `CompCanBeDormant` on the kind; a
woken ambusher *is* a hunter). ⛔ The parked names nettik / chirrik / rothrik are dead (§0 ruling 2);
⛔ `GR_Chickenspider` ("baby evil spider", roster JSON unwired row) is not a second kind either — it
is a donor chimera and the sheet's "1,000 eggs a year" is expressed by the **egg economy (§4)**, not
by a hatchling pawn.

**Frame** (sheet §4, mechanism carried unchanged): as large as an elephant, as massive as a horse —
mostly nimble sharp legs. ⇒ `bodySize` modest (❓ ~2.0–3.0, the donor Wyyyschokk is 3.0 MEASURED per
the roster JSON), `drawSize` large (❓ ~4.5–5.5, so the sprite covers the "too large a shadow" of
sheet §9), and 🔴 **melee authored explicitly — body size never scales damage**
(`ceiling-fields-break-when-doubled` memory; the sheet says the same). Mandible bite, leg-blade
slash (the armour-penetration benchmark), venom on bite for large prey.

**Register and look — ours, and visibly not the Wyyyschokk.** The canon entry
(`design/RimStarWars/canon_references/wyyyschokk/description.md`, RULED 2026-09-13) fixes the
Wyyyschokk as *blue-grey body, bold yellow-orange abdomen cross, spiky bristle tufts, blue-black
legs, clustered black eyes*. The Ollathrix must be **distinct in every one of those five marks**
while keeping the mechanics, because the two will share one defName and the Utinni patch swaps art
(§1c) — if the free-tier sprite already looks like a Wyyyschokk the swap is pointless and the free
mod is carrying IP by resemblance:

| mark | Wyyyschokk (canon, ruled) | Ollathrix (ours) |
|---|---|---|
| body colour | blue-grey | **bone-white to dead-silk cream** — the biome's own palette (sheet §9: *dead white silk, bone-white blooms*). A white spider in a green gloom is the "green and white hellscape" made animal |
| abdomen mark | yellow-orange cross | ⛔ **no cross, no marking**. A smooth, faintly translucent abdomen through which the darker gut shows — the loom is in the mouth, so the abdomen is *empty* of story on purpose (ban 5) |
| bristles | spiky tufts | **hairless, glossy chitin** with a matte silk-dust bloom on the upper surfaces |
| legs | blue-black | **pale, with a dark blade-edge** along each foreleg — the leg-blades read as weapons at a glance |
| eyes | clustered black | **one pale ring of small colourless eyes** around a raised head-boss — reads blind, which is right for a creature that hunts by web-sense, not sight |

Silhouette FORM for the art commission: **too many sharp legs under a low, wide, white body; the
head carried forward and low, mouthparts open** — the mouth-loom must read in the sprite (ban 5:
web always from the mouth). Facing set: standard `_north/_east/_south` plus masks; no flight.

**Every sheet §4 mechanism, and where it lives** (kit spec `kits/webwork_kit_spec.md`; state from
`WEBWORK_RM_MOD_BUILD_1` §8, MEASURED 2026-09-23):

| sheet §4 mechanism | kit piece | shipped? | what changes for the Ollathrix |
|---|---|---|---|
| mouth-loom (ranged adhesive spit) | `CompProperties_TurretGun` → `RSW_Gun_ShokkSpit` / `RSW_Bullet_ShokkSpit` / `RSW_Damage_ShokkSpit` (`src/RimStarWars/Shokk`) | ✅ shipped, patched onto donor `Wyyyschokk` | moves to the RM_ race def inline; defs re-token `RM_` (§5) |
| Shokk-bound (helplessness hediff) | `RSW_ShokkBound` HediffDef | ✅ shipped | re-tokens `RM_LoomBound` (mechanism name, not species name — the species name is the Utinni skin) |
| commandable adhesive (slick vs locked) | none — kit §3 defers it to the web-Things work | ⛔ unbuilt | unchanged; stays deferred, noted in §5 so it is not lost |
| mandibles / leg-blades / venom | melee verbs on the race def | ⛔ not authored (the donor race's own verbs are what ships today) | authored explicitly on `RM_Ollathrix`; venom = `additionalHediffs` on the bite DamageDef, cardiac-arrest stage only above a bodySize threshold ❓ |
| web-sense (felt, converge) | `RM_MapComponent_SenseWeb` + `RM_CompSenseWebNode` (shipped, `mandrake.rm.creaturebehaviors`); `RM_JobGiver_SenseWebConverge` | ⚠️ PARTIAL — the JobGiver and the race ThinkTree are unbuilt | the Ollathrix's own `ThinkTreeDef` is the missing consumer; building the race builds the tree |
| ambush burst | vanilla `CompCanBeDormant`/`CompWakeUpDormant` + concealment Thing (kit ruling 7: a debris-pile) | ⛔ unbuilt | one kind, dormant state — no ambusher kind |
| hates droids | scorer clause in the convergence JobGiver; `priorityFleshTypes` on a DefModExtension, `RSW_DW_FleshType_Droid` named only in RSW/RUT XML | ⛔ unbuilt (rides the JobGiver) | unchanged; the RM_ field stays generic |
| sun-helpless (light-moat) | `RSW_Webwork_SunScald` HediffDef via `startingHediffs`; C# `RM_Hediff_SunScald` | ✅ shipped (hediff in the Shokk RSW mod) | re-tokens `RM_Webwork_SunScald` and attaches to `RM_Ollathrix`'s kind inline |
| untameable | `race.wildness` 1.0 / no `trainability`; ban 1 | authored on the race | inline |
| fecund and self-predating | not a mechanic today | — | **the egg economy (§4)** carries "1,000 eggs a year"; self-predation stays flavour plus the kit's "hostile to everything including each other" faction-of-none (no truce, ban 2) |
| margin creep | `RM_MapComponent_FrontCreep` + `RM_FrontCreepExtension` on the biome | ✅ shipped, live-verified | unchanged |
| beetle anchor-chewing | `RM_JobGiver_ChewAnchors` + `RM_ChewableExtension` | ✅ shipped, **no consumer race** | consumer is the fauna roster's anchor-beetle (`RM_Quarrok`) |

### 1b. The name, the plural, the register

**Ollathrix** (owner's pick, ruling 3). In-game label `ollathrix`; description text uses "the
Ollathrix" as the species and "an ollathrix" for one animal.

**Plural: invariant — one ollathrix, three ollathrix.** Why: the two Latinate options both fail
in the mouth (*ollathrixes* is clumsy; *ollathrices* invites a learned mispronunciation and reads as
a joke), and the campaign name it maps to is already invariant in canon usage ("the Wyyyschokk").
An invariant plural also keeps every generated string safe — RimWorld pluralises labels by
`labelPlural`, so the def sets `<labelPlural>ollathrix</labelPlural>` explicitly and nothing
downstream appends an *-s*.

⚠️ **Near-neighbours, noted, not collisions:** `RM_Ollareth` (Fever Wood sap-drinker) and
`RM_Ollamane` (a sibling roster) share the first four letters. The owner picked this name knowing
the register; the difference of ending is enough at label length. MEASURED this pass: `ollathrix`
has 0 hits in any sibling roster or shipped `<defName>`/`<label>` (sweep in Python; probes
`thulvane` 6, `RM_Greatbole` 9, `skellick` 4).

### 1c. The Utinni mapping — what "maps to the Wyyyschokk" means concretely

**Recommendation: ONE defName, `RM_Ollathrix`, in the free mod; the campaign layer patches label,
description, `labelPlural`, `graphicData.texPath` (all facings + masks) and the leather label onto
that same def. No separate `RSW_Wyyyschokk` race.** Reasons, in order of weight:

1. **The Shokkweave precedent already set "label, never defName" as this campaign's rename law**
   (`kits/shokkweave_sole_source_spec.md` §1: Hyperweave keeps its defName because hundreds of
   inbound refs would orphan). The species has the same shape of inbound refs — the nest's
   `spawnablePawnKinds`, the kit's ThinkTree, `RSW_CompEmergentSpawnOnDestroy`'s soft PawnKindDef
   lookup, `GenStep_ScatterWebworkSilk`, every `wildAnimals` row, and the savegame's Things. One
   defName means one wiring; a second def means every one of those must be patched twice.
2. **Q13 does not apply, and is the reason NOT to make two defs.** Q13 ("duplicate, then diverge")
   governs one piece of content wired into *two biome mods* at the same tier. This is one piece of
   content in *one* biome at two *tiers*, which is the Q15 shape: the top-level mod carries the
   thing, the deeper layer patches it. Duplicating would produce two spiders that are the same
   animal with different skins living in the same biome, which is the impoverished-base failure Q11a
   forbids in reverse.
3. **The Sekkulaath precedent** (`fever_wood_deep_and_mud_2026-09-23.md` §1a): one species at two
   layers, *"with the dianoga mapped over it when the campaign layer is active"* — mapped *over*, not
   spawned beside. Same verb here.
4. **Savegame safety.** A player who removes the campaign layer keeps every spawned Ollathrix,
   because the defName never changed — the Wyyyschokk skin simply comes off. A second def would
   leave `Could not load reference` errors in the save.

What the mapping patch swaps (all `PatchOperationReplace` on `RM_Ollathrix`, ⛔ nothing on
mechanics): `label` → `wyyyschokk`; `labelPlural` → `wyyyschokk`; `description` → the canon text
(blue-grey, the cross, the bristles — the sheet's "Wyyyschokk to the galaxy, Feralisk on this
world" line survives in the description); `graphicData.texPath` → the Wyyyschokk art; `leatherDef`
label if a bespoke leather exists. Sheet §4's mechanisms are untouched by the patch because they are
already on the def.

⚠️ **UNCERTAIN — where the mapping patch lives.** Ruling 1 says *"when the campaign (Utinni) layer
is active"*. The existing home for Wyyyschokk-specific content is the RimStarWars-tier mod
`mandrake.rsw.shokk` (2026-09-11 kit ruling 6), and a Wyyyschokk is a Star Wars thing rather than
a campaign thing, so the tier grammar puts the skin patch in **RSW**, which Utinni loads anyway.
Recommended: patch in `mandrake.rsw.shokk`, retargeted from donor `Wyyyschokk` to `RM_Ollathrix`;
the mechanism defs that mod carries today re-token `RM_` and move down to `mandrake.rm.webwork`
(§5). Listed in §6 for confirmation because it inverts ruling 6's "the Shokk is its own RSW mod":
after today the *mechanisms* are RM and only the *skin* is RSW.

**Consequences for the donor `Wyyyschokk` (`mlie.starwarsanimalcollection`):** it stops being this
biome's owner species. The `RUT_Webwork.xml` row and the `RUT_Webwork_Nest` guardian both retarget
to `RM_Ollathrix`; the donor def stays in the game but homeless (disposition PROPOSED in
`webwork_fauna_roster_2026-09-23.md` §7). The canon entry's header line *"defName `Wyyyschokk`
(bare, third-party)"* becomes false the day the mapping ships and is corrected then, not now.

## §2 The silk name and the free-tier rename rule

### 2a. The word-form: **thrixweave**

Free tier: Hyperweave's label becomes **`thrixweave`** (description: *ollathrix silk, cut whole from
the Webwork's living loom…*). Under Utinni it patches on to **`shokkweave`** exactly as today.

**Why this form, in one line:** it is the same morphology as *shokkweave* — a clipped species
syllable plus *-weave* — so the campaign patch swaps one word for one word, and "thrixweave duster"
reads as a **material** the way "shokkweave duster" does, where "ollathrix silk duster" reads as a
description and is three words long in every apparel label the null `stuffAdjective` derives.

Rejected: *ollathrixweave* (five syllables, and the apparel labels become absurd); *ollathrix silk*
(two words, so `stuffAdjective` would have to be set and patched separately — a second patch point
the Shokkweave spec deliberately avoided); *loomweave* (mechanism-named, but the ruling says
*named after the spider*).

MEASURED this pass: `thrixweave` has 0 hits in any roster or shipped def.

### 2b. The rename becomes two-layered — what `SHOKKWEAVE_SOLE_SOURCE_1` must change

Today `src/RimUtinni/ShokkweaveEconomy/Patches/ShokkweaveRename.xml` replaces Hyperweave's
`label`/`description` once, in the Utinni mod. After ruling 4 the rename is **two patches at two
tiers**, and the *sole-source strip* is tier-independent:

| layer | mod | what it does | notes |
|---|---|---|---|
| free tier | `mandrake.rm.webwork` (the biome mod, `WEBWORK_RM_MOD_BUILD_1`) | `PatchOperationReplace` Hyperweave `label` → `thrixweave`, `description` → the ollathrix text | 🔑 the **trader strip, quest-reward tag strip, `tradeability: Sellable`, `stuffProps.commonality` 0.05** move here too — sole-source is the *biome's* law (sheet §6 ban 4 says "from any source but the Webwork"), not the campaign's, and the free mod must be whole (Q11a) |
| campaign | `mandrake.rut.shokkweaveeconomy` | `PatchOperationReplace` the same two fields again → `shokkweave` / the Wyyyschokk text. Loads after the biome mod, so the last replace wins | keeps: butchery yield patch (retargets to `RM_Ollathrix`), creep-web yield, the nest/silk-knot scatter, `GenStep_ScatterWebworkSilk` — ⚠️ but see §5: those are biome content too and most of it belongs in the RM mod |

Everything that *names* the silk in shipped text must follow the same split: `RUT_Webwork_Anchor`
(*"A thick catenary of shokkweave"*), `RUT_Webwork_SilkKnot`, `RUT_Webwork_Nest` (*"shokkweave
nest"*) each say *shokkweave* in a def that becomes RM_ — those descriptions say **thrixweave** in
the RM def and the campaign patch replaces them alongside Hyperweave's. ⚠️ A `keyed` sweep for the
literal word is owed at build, both tiers.

⛔ **Ban 4 is unchanged by any of this:** no hyperweave — under either name — from any source but the
Webwork.

## §3 The nest as a place

Sheet §8: *"woven from great masses of young trees and the rotting hides of victims; eggs inside,
Shokkweave in the walls, the mother above; the mites can lead you there."* Today that is one
1-cell `RUT_Webwork_Nest` ThingDef (`src/RimUtinni/ShokkweaveEconomy/Defs/`, `killedLeavings`
Hyperweave 60, dormant `CompSpawnerPawn` guardian, scattered by `RUT_WebworkNestScatter` at
near-zero density — "a map either has one nest or none"). ⛔ That def is the **economy's harvest
node**, not the sheet's *place*. This section designs the place; the node becomes one part of it.

### 3a. Structure — a nest is a cluster, not a Thing

A nest is a **mapgen cluster** (one `GenStepDef`, same `GenStep_ScatterWebworkSilk` class with a
multi-Thing group), ❓ radius 5–7 cells, on `SoilRich` or `AB_DenseGrass`-class fertility (the
richest ground on the map — the nest sits where the stolen river is thickest, because the mother
irrigates it). Its parts, inside-out:

| part | Thing | what it is | yield on deliberate harvest | notes |
|---|---|---|---|---|
| **the clutch** | `RM_Webwork_EggClutch` (new, `Building`, several per nest) | a pale mass of leathery eggs packed in silk on the floor of the nest (canon egg-sac reference: *tan/cream leathery sacs in web* — `wookieepedia_eggs.jpg`; ours are **bone-white**, not tan) | **`RM_OllathrixEgg` ×❓3–6 per clutch** — the jackpot (§4) | harvesting is a Deconstruct/Hack-style job that *rings the line*: every clutch carries `RM_CompSenseWebNode` |
| **the silk walls** | `RUT_Webwork_Nest` → **`RM_Webwork_NestWall`** (the existing node, re-tokened, ❓2–4 per nest) | hide-woven silk packed and hardened to a wall; the mother's guardian spawner rides these | thrixweave ❓40–80 total across the walls (the spec's nest-raid figure, spread rather than stacked on one cell) | keeps the existing dormancy/spawner comps; `spawnablePawnKinds` → `RM_Ollathrix` |
| **the hide-woven mass** | `RM_Webwork_HideMass` (new, `Building`, 1–2 per nest) | the rotting hides of victims — the red-brown of sheet §9's palette, the only warm colour in the biome | the victims' gear: a `killedLeavings`-style drop of **random apparel/weapon remnants** (the bones and armour that the mandibles broke, sheet §4) | reads as loot *and* as the biome's warning: a nest is where the missing went |
| **the mother above** | `RM_Ollathrix`, one, dormant on the nest's canopy `RM_Webwork_NestWall` | 🔑 **the one place a guaranteed Ollathrix sits** — every other one on the map is a roll. Spawned by the wall's `CompSpawnerPawn` as today, but ⚠️ *"above"* is fiction: RimWorld has no vertical layer, so she is a dormant pawn adjacent to the clutch, woken on approach (`wakeUpIfAnyTargetClose`, the 2026-09-12 live fix) | her mandibles (the Wildsteam bounty, sheet §7) and a butchery yield of silk | ⛔ no second kind; she is an ordinary `RM_Ollathrix` in the dormant state |
| **the mite-trail** | `RM_Vennick` pawns (fauna roster row 2) with a job that paths along registered SenseWeb cells *toward the nearest clutch* | fist-sized silk-runners, harmless, streaming along lines toward eggs — the *living treasure map* (sheet §4b) | none | needs a small `RM_JobGiver_RunToEggs` (kit §5 "deferred" — now owed, §5 below) |
| **the flowers** | `RM_Ruddreth` (flora roster) ringing the hide-mass | the rust-red nest-bloom that grows only on hide-rot | none — information only, like the Fever Wood's `RM_Corvath` | the nest is readable at a distance by its colour before you see a single Thing |

**Sheet §9 palette check:** the nest is the one place all four colours meet — dead white silk
(walls), bone-white (clutch), red-brown (hide mass), and the green of the young trees it is woven
from (the churning thicket's `RM_Kollavane` saplings, flora roster).

### 3b. Raid routes — how you get in, and what rings

Three ways in, each with a cost the biome already owns:

1. **Follow the mites.** Free, slow, and it puts you on silk the whole way — you arrive *felt*.
2. **Burn a corridor.** Fire is architecture (sheet §5); a burned approach is unfelt but it is a
   light-moat pointing *at* the nest, so every Ollathrix on the map converges on the fire.
3. **Herd the quarrok** (fauna roster row 1). Beetle-cut anchors deregister SenseWeb cells (kit §5),
   so a beetle-cut corridor is a *blind* corridor — the only silent approach, and the reason the
   corridor-cutter exists.

What rings: touching any clutch or wall (all are `RM_CompSenseWebNode` carriers) marks the raider
`RUT_Webwork_FeltMark` and the mother wakes; the whole map's Ollathrix converge (kit §1). ⛔ Ban 6
holds — no cell of the nest, roofed or not, is ever safe by construction.

### 3c. What a raid yields

Deliberately ranked, so the player chooses what to carry out under convergence:

| take | value | risk it adds |
|---|---|---|
| **eggs** | highest per kg (§4) | 🔴 the carried-eggs mark — you are *felt* until they leave your inventory (§4c) |
| **thrixweave from the walls** | high, bulky | the walls are the guardian's spawner; cutting them wakes her if she has not already |
| **mandibles** (kill the mother) | the Wildsteam bounty quest faucet (sheet §7) | the fight itself |
| **the hide-mass gear** | random, sometimes very good | none beyond being there — the *consolation* take |

**Sole-source guard, restated:** every yield above fires only on deliberate harvest / deconstruct
(`DestroyMode.Vanish`-class jobs, the edge `RSW_CompEmergentSpawnOnDestroy` keys on). Beetle- and
fire-destroyed nest parts drop **nothing** — the spec's rule that a beetle lawnmower is not a silk
farm extends to the nest.

### 3d. Density and the "one nest or none" rule

The existing scatter ("a map either has one nest or none") is the right instinct and stays: one
nest cluster per map at most, ❓ ~60% of Webwork maps. ⚠️ A nest that never appears is dead content;
a nest on every map is a farm. The 60% is a placeholder, flagged.

## §4 The egg economy and the carried-eggs mark

Sheet §7: *"The eggs — extremely valuable smuggled offworld; carrying stolen eggs marks you to every
web you pass. The smuggler's jackpot, priced in risk."* And §4: 1,000 eggs a year, self-predating.

### 4a. The item — `RM_OllathrixEgg`

| field | value | why |
|---|---|---|
| defName / label | `RM_OllathrixEgg` / `ollathrix egg` — Utinni patches label to `wyyyschokk egg` | same one-def rule as §1c |
| category | `Items` (an animal-product-class item), **not** `AnimalProductRaw` with `CompHatcher` | 🔴 **it must NOT hatch.** A hatching egg is a tamed Ollathrix by the back door (ban 1: no tamed, traded or negotiated). No `CompHatcher`, no `CompTemperatureRuinable` hatch path — it is inert cargo |
| mass | ❓ 2 kg | heavy enough that a clutch is a real carry decision |
| market value | ❓ 350–500 silver each — above a `RM_OllathrixEgg`'s weight in thrixweave, below a component-class item | the jackpot must beat the walls per kilo, or nobody carries the mark |
| `tradeability` | **`Sellable` only** | nobody stocks them — the only source is a nest (sheet §7 "smuggled") |
| `tradeTags` | `RM_Contraband` (new tag, empty of buyers in the free tier by default; the free tier's orbital/exotic traders *buy* via `Sellable` alone) | the offworld route below hangs on this tag |
| rot | `CompRottable` ❓ 15 days | ⭐ **the eggs are perishable**, so a stolen clutch is a countdown to a buyer — it is smuggling, not hoarding |
| ban check | no recipe consumes it, no `ingestible` | an egg that is food or medicine is a reason to farm nests |

**"1,000 eggs a year" is expressed here**, not by a hatchling: the clutches regrow. A raided nest's
walls do not, but a surviving mother re-lays — `RM_Webwork_EggClutch` respawns at the nest ❓ every
20–30 days while any `RM_Ollathrix` is alive on the map. A map with no mother is a map with a dying
nest, which is the sheet's own logic (the eggs are hers). ⛔ No Ollathrix is ever *spawned by* an
egg — self-predation ("their own main predator") is why the clutch count never becomes a
population count, and that stays flavour plus the faction-of-none hostility.

### 4b. The offworld sale route

- **Free tier:** any trader that buys `Items` with `Sellable` — orbital traders in particular —
  buys eggs at full value. That is the sale route with no campaign content at all: sell them to the
  sky. It is enough for the free mod to be whole.
- **Campaign (Utinni):** a `RM_Contraband` buyer premium. The Bazaar's broker (memory:
  `bazaar-trade-window-ruled` — the broker is a Bazaar tab) and the Hutt/Czerka orbital kinds
  (`guy762_TraderKind_HuttGalleon`, the same kinds the trader strip already patches) get a
  `StockGenerator_BuyTradeTag` on `RM_Contraband` at ❓ ×1.5. ⚠️ Whether the Wildsteam ever buy
  eggs is a **needs-owner-ruling** (§6): they are at war with the spiders and pay for mandibles; eggs
  in a Wildsteam seat could read as either a bounty (destroy them) or a betrayal (they resent
  smugglers). Not designed here.
- ⛔ **No quest reward, no cargo pod, no ancient-danger loot.** Same strip as Hyperweave: the egg's
  `thingSetMakerTags` is empty. An egg that arrives by any route but a nest breaks *"the only source
  is a nest"*.

### 4c. The carried-eggs mark — how the web "knows"

**Already half-built, and the half that exists is the right half.** `RM_MapComponent_SenseWeb.cs`
(lines 116–146, read this pass) already looks up `RUT_Webwork_Egg` by defName at scan time and
treats *"pawn's inventory contains the egg"* as equivalent to *"pawn is standing on a registered web
cell"*: it applies `RUT_Webwork_FeltMark` either way. ⇒ The carried-eggs mark is one string
constant away from live: the lookup name becomes `RM_OllathrixEgg` (or the constant is read from
a DefModExtension on the biome so the RM assembly never names content — cleaner, and the same
pattern `priorityFleshTypes` uses).

What it does, stated as the player will feel it:

| question | answer |
|---|---|
| **how does the web know?** | fiction: the eggs *are* web — the mother's silk and pollen are on the shell, and every line she has ever laid answers to them. Mechanism: inventory check at the SenseWeb scan interval (~250 ticks), **map-wide** — carrying eggs marks you whether or not you are touching silk |
| **what does it trigger?** | the same `FeltMark` convergence as touching silk — every Ollathrix on the map paths to the carrier (kit §1). No new behaviour; the eggs make you a *permanent* felt-mark instead of a decaying one |
| **how long does it last?** | while the eggs are in a pawn's inventory, the mark is re-applied every scan, so it never decays. Once dropped, the ordinary ❓ ~1 day decay runs from the last scan. ⇒ **drop the eggs and the web loses you within a day; keep them and it never does** |
| **what about a stockpile?** | ⚠️ eggs on the ground or in a stockpile mark **nothing** — the mark is on the *carrier*. A colony that stores eggs in a shelf is not converged on. That is deliberate: the risk is the carry (smuggling), not the ownership. 🔑 It also means a **caravan** carrying eggs across the Webwork is felt on every Webwork map it enters — "marks you to every web you pass" is literally true for a caravan route through the biome, and *that* is the smuggler's price |
| **off-biome?** | the SenseWeb component gates on the map's biome / creep front, so a marked pawn on a non-Webwork map with no creep is felt by nothing. The mark is not a curse; it is a signal only web can hear |

⚠️ **UNCERTAIN, engine, Desktop-only:** whether `pawn.inventory.innerContainer.Contains(def)` sees
a caravan pawn's *carried* goods on arrival (caravan inventory is transferred on map entry; it
should, but this is an engine question and UNMEASURABLE on the Mac).

## §5 What this changes for open items

| item | state today | what changes |
|---|---|---|
| **`WEBWORK_RM_MOD_BUILD_1`** (Phase A: build `mandrake.rm.webwork`) | steps 1–4 OWED; its plan ships `wildAnimals` **empty** at step 2 per `SW_FAUNA_NEVER_IN_RM_TIER_1` | 🔴 **`wildAnimals` no longer ships empty**: it carries `RM_Ollathrix` and the five fauna-roster rows inline (all invented, Q11a). The planned `WildAnimals_Webwork.xml` Utinni patch shrinks to canon *injections* only (fauna roster §8) and the Wyyyschokk **skin** patch (§1c). `wildPlants` is replaced by the flora roster's 16 rows; the 7 donor rows are dispositioned there. The mod also takes: the three web Things (`RUT_WebworkStructures.xml` — the ticket's own §6 already judged them "plausibly RM_"; they are), the silk knot, the nest cluster (§3), the egg (§4), the free-tier rename + strip (§2b), and the Shokk mod's mechanism defs re-tokened `RM_` (`RM_LoomBound`, `RM_Damage_LoomSpit`, `RM_Gun_LoomSpit`, `RM_Bullet_LoomSpit`, `RM_Webwork_SunScald`, `RM_CompEmergentSpawnOnDestroy`). `GenStep_ScatterWebworkSilk.cs`'s literal `"RUT_Webwork"` gate becomes `RM_Webwork` when it moves (the ticket's §7d already flags this file). |
| **`SHOKKWEAVE_SOLE_SOURCE_1`** (`ready`/`needs game-up`) | one rename patch, one trader strip, butchery/creep/nest yields, all Utinni | becomes **two-layered** (§2b): free-tier `thrixweave` rename + strip in the RM mod; campaign `shokkweave` re-rename in `mandrake.rut.shokkweaveeconomy`. Butchery patch retargets to `RM_Ollathrix`. The live trader-generation proof runs **once per tier** (a free-tier list without the Utinni mod must also generate zero hyperweave). Nest-raid yield spreads across `RM_Webwork_NestWall` ×2–4 instead of one 60-stack. |
| **`WEBWORK_MECHANICS_1` / the unbuilt think tree** | `RM_JobGiver_SenseWebConverge`, the race ThinkTree, droid-priority scorer, ambush concealment Thing — all UNBUILT, "needs the Wyyyschokk race's own ThinkTree" | the missing race is now **ours** — `RM_Ollathrix` is authored in the RM mod, so the ThinkTree has a home and the blocker on mechanics 1, 2 and 7 is gone. Two small JobGivers join the list: `RM_JobGiver_RunToEggs` (the mite-trail, kit §5's deferred item, now owed by §3a) and the beetle's consumer race (`RM_Quarrok`, fauna roster). Commandable adhesive stays deferred, still noted. |
| **`RUT_WebworkStructures` placeholder art** | Hive texture retinted, ×3; nest uses Hive too | bespoke sprites owed for: anchor line, sheet web, gutter, nest wall, egg clutch, hide mass, egg item, plus the Ollathrix's own facing set. ⚠️ Search `infrastructure/artpipe/done/` and `_artsrc/` by subject before queueing — UNMEASURED this pass whether any web/nest art already sits finished. |
| **`SHOKK_RSW_MOD_1`** (closed, done) | `mandrake.rsw.shokk` patches donor `Wyyyschokk` with the spit comp and sun-scald | retargets to `RM_Ollathrix`; sheds its mechanism defs to RM (above); keeps only the Wyyyschokk skin patch (label/description/art). ⚠️ Needs a re-open or a successor item — §6. |
| **`DONOR_DEFS_PORT_TO_OURS_1`** | port Mlie's Star Wars animals to `RSW_` | the Wyyyschokk is **not** ported to an `RSW_` race — it becomes a skin on `RM_Ollathrix`. One fewer port. |
| **`DUPLICATE_CANON_DEFNAME_PAIRS_1`** | flags `Kreetle` vs `RSW_Kreetle` across 5 biomes | the Webwork's `RSW_Kreetle` row is PROPOSED cut (fauna roster §7), which removes this biome from that item's count. |
| **`rosters/the_webwork.json`** | 6 fauna (2 dead/unwired), 7 flora, 4 `new_defs` | a regeneration is owed once the owner rules on the two roster docs: `new_defs` rows 1, 2, 4 are now designed (mite, pale flowers, root-mat), row 3 (guild pawnkinds) is **dead** by ruling 2. |
| **`design/RimStarWars/canon_references/wyyyschokk/description.md`** | header says defName `Wyyyschokk` bare third-party | becomes "a skin patch on `RM_Ollathrix`" the day the mapping ships; the Must-show checklist is unchanged and still grades the *campaign* sprite. ⚠️ Correct it at build, not now (it is true today). |

## §6 Needs owner ruling

Everything I could not settle without changing a ruling — a sheet ruling, a kit-sitting ruling, or
an item's recorded scope. Each is one card. None is written as fact above.

1. **The 2026-09-11 kit ruling 6 ("the Shokk is its own RimStarWars-tier mod; ShokkBound and the
   spit go RSW") is inverted by today's ruling 1.** With the species invented and RM-tier, its
   mechanisms (bound hediff, spit, sun-scald, emergent-spawn comp) are mechanism-not-IP and belong
   in `mandrake.rm.webwork`; `mandrake.rsw.shokk` shrinks to the Wyyyschokk **skin** patch only.
   Confirm that reading, and whether `SHOKK_RSW_MOD_1` re-opens or a successor item is filed.
2. **Do the Wildsteam buy eggs, refuse them, or punish them?** Sheet §7 gives them the mandible
   bounty and §5 says they are at war here. Three readings: (a) bounty — they pay to *destroy*
   eggs; (b) refusal — no Wildsteam trader buys contraband; (c) betrayal — selling eggs at a
   Wildsteam seat costs faction goodwill. §4b designs the free-tier sky route only.
3. **Nest frequency.** "One nest or none" is kept; the placeholder is ❓60% of Webwork maps. A
   number is his to pick, and it decides whether the egg economy exists for a given colony.
4. **Egg respawn while the mother lives** (❓ every 20–30 days) — this is the mechanism that makes
   "1,000 eggs a year" true without a hatchling. Confirm that a *living* nest re-lays; the
   alternative is one clutch per nest, ever, which makes eggs a one-shot rather than a smuggling
   economy.
5. **`tradeability: Sellable` on the egg removes it from every trader's stock, including
   campaign smugglers.** If he wants a *black-market* trader that *stocks* eggs (to be bought as
   well as sold), that is a second route and it contradicts "the only source is a nest". Default
   written: nests only.
6. **The Utinni skin-patch home** (§1c UNCERTAIN): RSW (`mandrake.rsw.shokk`, tier-correct for a
   Star Wars creature) or RUT (literal reading of "when the Utinni layer is active"). Default
   written: RSW.
7. **The Wyyyschokk donor row and the two donor multi-homers (`RSW_Kreetle`, `Shyrack`) are
   PROPOSED cut from this biome** (fauna roster §7). Evictions are stopped as a sweep; this is the
   biome's own sitting, so it is his call here and nowhere else.
8. **`Plant_TookeTrap_Wild`** — genuine canon; PROPOSED kept low under a Utinni `WildPlants_Webwork`
   patch (flora roster §8), with the invented `RM_Kessaroth` as the free tier's snap-trap. Confirm,
   or cut the canon row outright.
