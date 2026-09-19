# Lantern Deeps — flora names (second proposal)

Status: DRAFT for the owner, 2026-09-18. Flora only. `Lantern Deeps`, `lanternstone`,
`mycelium`, `still air`, every sound/GenStep/mechanic name: KEPT.

## Rulings

Owner, 2026-09-18, on the first (canon-lookup) proposal
`lantern_deeps_rename_proposal.md` — verbatim:

> "Lantern deep was our name so it's already ok. Lantern stone is too. I just
> wanted new names for the mushrooms and edible things. And I didn't want you to
> look up specific canon because it doesn't make sense in this context. New names
> please just in the style of Star Wars. Try again. No nova please."

> "Actually we need two different mushrooms here. It makes no sense that the rot
> has something growing in the lantern deeps as well. Totally different biomes. So
> generate a new strange mushroom for the lantern deep. Perhaps a big swollen ball
> with small tentacles growing out of it. Called twitching puffer."

Consequences taken as given here:

- The biome, generator, packageId, folder, namespace, texPath root, `lanternstone`
  and every crystal/wall/floor/formation def: **KEPT**. The first proposal's §1 and §2
  tables are dead; only its utility census (nutrition / harvest / light) was reused.
- Flora only. `mycelium` is a plain word and stays. `still air`, the sound names, the
  GenSteps and the weather stay.
- **No web research, no canon names.** Every name below is campaign-original. If a
  name below collides with something real I did not remember, that is a defect to
  swap for its alternate, not a source.
- **Dulcis leaves the Deeps.** `RUT_RawDulcis` stays RotSporeKit's (ruling of the same
  day, `DEEP_DULCIS_DEDUP_1`); the Deeps grow their own food mushroom, the
  **twitching puffer**, with its own harvested item (§ The twitching puffer).

## Style rules

What makes a name read as Star Wars in this campaign (the register of bantha, nerf,
jogan, meiloorun, nysillin, tauntaun, dianoga):

1. **Short coined noun, consonant-forward**, one or two syllables, often a doubled
   consonant or a hard cluster (`-rr-`, `-sk`, `-th`, `-nt`, `-kk`), never Latin or Greek.
2. **Coined noun + plain English category**: `<vresk> cap`, `<morrl> bulb`, `<kesh> lace`.
   The English half says what it is; the coined half says it is not from here.
3. **The English half is the plant's JOB**: cap, bulb, bramble, lace, reed, spout,
   fern, puffer — a word a farmer or a cook would use, not a botanist.
4. **Names are informed by what the plant does and what the kitchen will do with it**
   (`cantina_kitchen_spec.md`): the edible ones must sound like something a cantina
   serves; the timber/fibre ones like a trade good.
5. **One coined stem per plant, no shared stems** — nothing reads as a family or a
   grade of another. Nothing that is also a lanternstone or crystal word.
6. **Lowercase RimWorld labels**; defNames `RUT_` + CamelCase of the label with the
   category word attached (`RUT_VreskCap`). No `Deep` prefix any more — the texPath
   root already scopes the mod, and `Deep` was the donor's habit.

## The names

Utility figures are read from `RUT_DeepFlora.xml` (2026-09-18), not from the first
proposal's prose. "Nutrition" is the plant's own stat (what a grazer gets); "harvest" is
`harvestedThingDef` × `harvestYield`.

| current defName | current label | what it is / does | proposed defName | proposed label | cuisine role | description rewrite (≤ 30 words) |
|---|---|---|---|---|---|---|
| `RUT_Crystalcap` | crystalcap | mushroom TREE with a crystal-plated cap; 30 growDays, 40 WoodLog, Beauty 6, tough, grows in anything | `RUT_ThrakkCap` | thrakk cap | none today; the cap's crystal plating is a future **plate/serving-ware** stuff, never food | A strong crystal-capped mushroom tree. Slow-growing, but thrakk wood is very tough and very handsome, and it does not much care what it grows in. |
| `RUT_CrystaltipBrambles` | crystaltip brambles | thorny shoots with crystalline tips; pathCost 14; Nutrition 0.5, eaten raw in place, no harvest product | `RUT_OsskBramble` | ossk bramble | **raw graze / forage** — the thorn-tips are a future pickled cantina bar snack ("ossk tips") | Tangled, thorny shoots tipped with crystal. Ossk grows in clusters and slows anyone moving over it; grazers strip it anyway. |
| `RUT_DeepArpeau` | arpeau | aquatic fungus tall enough to log; 5 growDays, 20 WoodLog, glows cyan r4, Nutrition 2.0 as tree fodder | `RUT_VellokReed` | vellok reed | none; **glowing reed-timber** — future cantina fittings (a lit bar-front made of vellok) | An aquatic fungus tall enough to be logged, lit from inside. Vellok grows fast in the shallows, but it does not yield much usable material. |
| `RUT_DeepDulcisPlant` | dulcis | 7 growDays, 12 `RUT_RawDulcis`, humanFoodPlant, the biome's foragedFood — **RotSporeKit's mushroom, leaving** | `RUT_TwitchingPuffer` | twitching puffer | **the Deep's food mushroom** — see the section below; the harvested tendrils are the cantina's "squirming bowl" that is not actually alive | (see The twitching puffer) |
| `RUT_DeepGreyLady` | Grey Lady | grey fungus that grows cloth-like lace from its cap; 8 growDays, 16 Cloth, the Deep's one fabric | `RUT_PrennaLace` | prenna lace | none — fabric; future **table linen / trade cloth** | A grey fungus that grows cloth-like lace from under its cap. Prenna is the Deeps' one source of fabric. |
| `RUT_DeepMycelium` | mycelium | ground carpet, Nutrition 0.2, grazed, purpose Misc | `RUT_DeepMycelium` **KEEP** | mycelium | fodder only | (unchanged) |
| `RUT_DeepNuitae` | nuitae | near-black cap, glowing underside; wet ground and shallow water; Nutrition 0.6, eaten raw in place, harvestWork 80, no product | `RUT_NurrikGill` | nurrik gill | **the pot mushroom** — future broth/stew base (the glowing gills are the flavour and the colour of the bowl) | Its cap is almost black; its gills glow brightly beneath. Nurrik grows in water, or in ground wet enough to pass for it. |
| `RUT_Fungusfern` | fungusfern | bush: two mushrooms and a fern in symbiosis; 3 growDays, no harvest, no glow | `RUT_QuorrFern` | quorr fern | none — scenery | A symbiosis between two species of mushroom and a fern, unique to the crystal voids. Quorr is what the Deeps have instead of undergrowth. |
| `RUT_Gleamtip` | gleamtip | tall narrow mushroom, glowing cap tip; "used the way other people use flowers"; Nutrition 0.2, no harvest | `RUT_ZivvitTaper` | zivvit taper | none — **the table candle**; future decorative item on a cantina table | A mushroom with a long narrow cap that glows at the tip. Cave dwellers use zivvit the way other people use flowers, or candles. |
| `RUT_LuminousSpout` | luminous spout | aquatic fungus, upside-down cone, glows cyan r3.9; Nutrition 0.3, no harvest, clustered | `RUT_KuvraSpout` | kuvra spout | none today; the dried cone is a future **drinking cup** (the cantina's glowing cup) | An aquatic fungus that grows as an upside-down cone and glows in the dark. Kuvra cones, dried, hold liquid. |
| `RUT_YumBulbs` | yum bulbs | squat bulbs with amber glowing tips; Nutrition 1.0 (highest here), Beauty 12, glower r3, attracts animals to spread spores, decorative sowable | `RUT_BrellikBulb` | brellik bulb | **the sweet one / animal bait** — future candied brellik, and the feed that stocks a live tank | With brightly glowing amber tips, brellik draws animals to eat it and unwittingly carry its durable spores through the dark. |

Reading the set aloud: thrakk, ossk, vellok, puffer, prenna, mycelium, nurrik, quorr,
zivvit, kuvra, brellik — eleven different initials, no shared stems, nothing that is also
a crystal word. The edible four (ossk, nurrik, brellik, puffer) are the cantina's Deep
lane: a bar snack, a broth, a sweet, and the squirming bowl.

## The twitching puffer

The Deep's own food mushroom, replacing dulcis one for one. Dulcis and `RUT_RawDulcis`
stay RotSporeKit's, untouched; the Lantern Deeps mod stops referencing either.

### Fiction

A swollen grey-violet ball the size of a cook-pot, sitting on a stubby foot, with a
fringe of finger-length tentacles growing out of its upper half. The ball is a pressure
bladder: it pumps a sugary spore-fluid out along the tentacles and back, and every pulse
makes them **twitch**. That is all the twitching is — hydraulics, not nerves; the puffer
has no more mind than a heart valve. Grazers eat the tentacles; the ball is left alone,
because a ball that is torn **puffs** — a dry spore cloud that stings the eyes and is how
the thing spreads. Harvesting means cutting the tentacles at the base with the ball
intact; they regrow in a few days and the ball swells again.

Why it is safe to eat: the tentacles are the puffer's fruit — it grows them to be eaten,
the same bargain brellik strikes with its glowing tips, and the sting is only in the
spores of a burst ball. Cut tendrils go on twitching for hours as the fluid settles.
That is the cantina hook: a bowl of puffer tendrils is the **squirming bowl that is not
alive**, and the faith matrix of `cantina_kitchen_spec.md` §2 reads it three ways —
reverent, indifferent, revolted — while the cook knows it is a mushroom.

### Plant def — `RUT_TwitchingPuffer`

Same numbers dulcis had (read from `RUT_DeepFlora.xml`), with only the names moved:

| field | value | note |
|---|---|---|
| ParentName | `BushBase` | as dulcis |
| defName | `RUT_TwitchingPuffer` | |
| label | `twitching puffer` | |
| description | A swollen spore-bladder ringed with finger-length tentacles that twitch as it pumps. The tentacles are its fruit and regrow when cut; the ball, if torn, puffs stinging spores. | ≤ 40 words |
| texPath | `RUT_LanternDeeps/Things/Plant/TwitchingPuffer/PufferGrown` | `Graphic_Random` folder |
| immatureGraphicPath | `RUT_LanternDeeps/Things/Plant/TwitchingPuffer/PufferImmature` | |
| leaflessGraphicPath | `RUT_LanternDeeps/Things/Plant/TwitchingPuffer/PufferHarvested` | |
| Nutrition / Flammability | 0.20 / 0.1 | as dulcis |
| growMinGlow / growOptimalGlow | 0 / 0 | |
| growth temperature | −45 → 352.222 (min = optimal) | as dulcis |
| mustBeWildToSow | true | |
| fertilityMin | 0.70 | |
| wildClusterRadius / Weight | 5 / 250 | |
| growDays | 7 | |
| dieIfLeafless | true | |
| harvestWork / harvestYield | 200 / 12 | |
| harvestTag / harvestAfterGrowth | Standard / 0.1 | |
| harvestedThingDef | `RUT_PufferTendrils` | **the change** |
| sowMinSkill / sowTags | 4 / Ground | |
| topWindExposure / wildOrder | 0 / 2 | |
| visualSizeRange | 0.5~1.3 | |
| purpose / humanFoodPlant / pollution | Food / true / Any | |
| interferesWithRoof | false | |

### Item def — `RUT_PufferTendrils` (proposed over `RUT_RawPuffer`)

"Raw puffer" would say the ball is eaten; it is not. The tendrils are the harvest, the
ingredient and the dish, so the item is named for them.

| field | value |
|---|---|
| ParentName | `PlantFoodRawBase` (as `RUT_RawDulcis`) |
| defName | `RUT_PufferTendrils` |
| label | `puffer tendrils` |
| description | Cut tentacles of the twitching puffer. They keep twitching for hours after harvest — pressure, not life — and are good to eat, even raw, if you can watch them. |
| texPath | `RUT_LanternDeeps/Things/Item/Crops/PufferTendrils` |
| MarketValue / Mass | 1.2 / 0.027 (as `RUT_RawDulcis`) |
| CompProperties_Rottable | daysToRotStart 16, rotDestroys true |
| ingestible | preferability `RawTasty`, foodType `Fungus` |
| ingredient.mergeCompatibilityTags | `Fungus` (MayRequire Ideology) |
| nutrition | inherited from `PlantFoodRawBase` (0.05), as dulcis |

Biome: `RUT_LanternDeeps.xml` `<foragedFood>` → `RUT_PufferTendrils`; `wildPlants` row
`RUT_DeepDulcisPlant 0.02` → `RUT_TwitchingPuffer 0.02`. The mod then has no
`RUT_RawDulcis` reference and the About.xml note explaining the RotSporeKit dependency
for dulcis goes with it (`DEEP_DULCIS_DEDUP_1` closes as "the Deeps no longer grow
dulcis" rather than "the Deeps borrow it").

### Art brief — four jobs (write the job JSONs from this; do not copy the dulcis ones)

House format is `infrastructure/artpipe/done/dulcisgrown_a_v1.json`: `id`, `prompt`,
`canvas {width,height}`, `drawsize`, `background "transparent"`, `channel "codex"`,
`priority 40`, `facing null`, `facings []`, `reference null`, `rimflow_item_id`,
`style_notes` naming the ART_JOBS.md row, texPath and target file. **`reference` stays
null** — a reference triggers reskin-validate, and this is new art, not a restyle.
`rimflow_item_id`: the item that carries this rename (not `CAVERNS_PARITY_BUILD_1`,
which is done).

Standing prompt tail for every job, verbatim from the dulcis jobs: *"Lantern Deeps biome
art (the_lantern_deeps.md §9, owner ruling: "a blue lantern burning under the mountain,
and a dead miner's suit walking toward it"). Palette: blue-on-black, fungal grey and
green, lanternstone blue as the only ambient light. Silhouette language: facets, geodes,
lattices — angular crystal forms, never rounded gems. Painterly vanilla-RimWorld art
style."* — then `tint_organics.py --apply` shifts the blue band +70° to purple, so
render **blue** and let the script make it violet; do not prompt for purple.

| id | texPath → file | canvas | drawsize | subject (prompt head) |
|---|---|---|---|---|
| `puffergrown_a_v1` | `RUT_LanternDeeps/Things/Plant/TwitchingPuffer/PufferGrown/a.png` | 256×256 | 1.0 | A single swollen grey-blue fungal ball on a stubby foot, taut and faintly translucent as if inflated, ringed on its upper half by a fringe of short finger-like tentacles caught mid-twitch — some curled, some extended, blurred at the tips. Pale spore-veins under the skin lit by the ambient blue. No face, no eyes, no mouth. Ready-to-harvest stage. |
| `pufferimmature_a_v1` | `RUT_LanternDeeps/Things/Plant/TwitchingPuffer/PufferImmature/a.png` | 256×256 | 1.0 | The same fungus young: a fist-sized ball, dull and wrinkled, not yet inflated, with tentacle nubs showing as bumps. Smaller silhouette inside the same footprint. |
| `pufferharvested_a_v1` | `RUT_LanternDeeps/Things/Plant/TwitchingPuffer/PufferHarvested/a.png` | 256×256 | 1.0 | The same fungus after harvest: the ball intact but sagging, half-deflated, its tentacles cut to stubs. Nothing broken open — the ball never bursts in any state. |
| `puffertendrils_v1` | `RUT_LanternDeeps/Things/Item/Crops/PufferTendrils.png` | 256×256 | 1.0 | Harvested crop item: a small heap of cut fungal tentacles, finger-length, grey-blue, a few curled as if still moving. Replaces ART_JOBS.md job 12 (the dulcis heap). One of the few non-crystal things down here; must read as food at inventory scale. |

Silhouette rule the brief must carry: the ball is a **rounded** form, the one deliberate
exception to "never rounded gems" — it is organic, not crystal; the crystal language
stays in the background veins only. Sizes match the dulcis set so `drawSize` and the
texPath folder shape are unchanged.

`wire_art.py` gains four rows in place of the three `dulcis*` rows and `dulciscropitem_v1`;
`build_art_sheet.py` the same; ART_JOBS.md rows 12 and 18/18b/18c are rewritten, not
appended.

## Alternates

Two runners-up per plant, same category word, so a swap is a one-cell change with no
second round. Each keeps its own initial distinct from the rest of the set where possible.

| plant | proposed | alternate 1 | alternate 2 |
|---|---|---|---|
| crystalcap | thrakk cap | dorrusk cap | kethrin cap |
| crystaltip brambles | ossk bramble | skeer bramble | vellith bramble |
| arpeau | vellok reed | dunnok reed | jhassa reed |
| dulcis → puffer | twitching puffer (owner's) | — (ruled) | — (ruled) |
| Grey Lady | prenna lace | veshti lace | sillu lace |
| mycelium | mycelium (KEEP) | — | — |
| nuitae | nurrik gill | tesska gill | hollom gill |
| fungusfern | quorr fern | pellik fern | wisshk fern |
| gleamtip | zivvit taper | ruvi taper | ilvenn taper |
| luminous spout | kuvra spout | gharr spout | tummok spout |
| yum bulbs | brellik bulb | haffa bulb | lurra bulb |
| puffer item | puffer tendrils (`RUT_PufferTendrils`) | raw puffer (`RUT_RawPuffer`) | puffer cuts (`RUT_PufferCuts`) |

If a category word is the objection rather than the stem: gill ↔ hood (nuitae), taper ↔
wick (gleamtip), reed ↔ stalk (arpeau), spout ↔ cone (luminous spout) all read cleanly
with the same stems.

## Execution notes

### What one rename touches

For every label+defName change (ten plants; mycelium untouched), in this order:

1. **Defs** — `src/RimUtinni/LanternDeeps/Defs/ThingDefs_Plants/RUT_DeepFlora.xml`
   (defName, label, description, `texPath`, and for the two staged plants
   `immatureGraphicPath` / `leaflessGraphicPath`); `Defs/Biomes/RUT_LanternDeeps.xml`
   `<wildPlants>` rows (11) and `<foragedFood>`.
2. **C#** — `Source/GenStep_DeepFloraGate.cs` lines 31–41 carry all eleven defNames as
   **string literals**; a stale one there passes the compiler and fails at runtime.
   `Source/DeepFloraPlanter.cs` 61–62 names Arpeau/LuminousSpout/Nuitae in a comment
   only. Rebuild and redeploy the DLL (game closed).
3. **Textures** — `git mv` the folders under
   `Textures/RUT_LanternDeeps/Things/Plant/<Old>/` → `<New>/` (Dulcis and GreyLady
   are two-level: `Dulcis/DulcisGrown|Immature|Harvested`, `GreyLady/GreyLadyGrown|Immature`);
   the puffer gets a new `TwitchingPuffer/Puffer{Grown,Immature,Harvested}/` tree and
   `Things/Item/Crops/PufferTendrils.png`. Texture binds by texPath: a moved folder with
   an unmoved def renders magenta.
4. **`ART_JOBS.md`** — rows 12, 13–23 (texPath column and subject prose); rows 12 and
   18/18b/18c become the puffer rows.
5. **`wire_art.py`** — the job-id → texPath table (lines 80–119 cover the flora); the ids
   are the artpipe's and the **paths** are ours, so only the right-hand side changes for a
   rename, and the `dulcis*` / `dulciscropitem_v1` rows are replaced by the four puffer
   ids. **`build_art_sheet.py`** lines 61–80+ mirror the same ids with a texPath fragment
   and caption; same edit. **`tint_organics.py`** names YumBulbs once (docstring) —
   the amber-exclusion is by hue, not by name, so nothing functional changes.
6. **`validation.py`** — **0 hits** on any flora name; nothing to do there unless a
   must-show bar is added.
7. **artpipe** — `infrastructure/artpipe/registry.jsonl`, `throughput.jsonl`,
   `art_status.json`, `drawsize_backfill.json` and the `done/*.json` +
   `*.manifest.json` pairs are **history, not config**: their ids
   (`crystalcap_a_v1`, `greyladygrown_b_v1`, …) stay as they are — a renamed job id would
   orphan its manifest. New ids appear only for new art (the four puffer jobs). ⚠️ The
   deleted `pending/*.json` files in the working tree at the time of writing are someone
   else's in-flight change; do not touch them.
8. **`BiomeFlora_Ashkarr.xml`** — **0 rows reference our flora.** The file names the
   donor's `BMT_Nuitae`, `BMT_Arpeau`, `BMT_GreyLady` and vanilla `Plant_Brambles`
   (lines 202–216, 379), never a `RUT_Deep*` def — so it is not a rename site; it is a
   separate stale-donor finding (those rows match nothing once Biomes! Caverns is gone
   and log nothing when they don't).
9. **`EXPECTED_FAILURES_next_load.md`** — line 41–42 (`DEEP_DULCIS_DEDUP_1`): rewrite the
   expectation to "`RUT_DeepRawDulcis` ABSENT, `RUT_DeepDulcisPlant` ABSENT,
   `RUT_TwitchingPuffer` and `RUT_PufferTendrils` PRESENT, foragedFood resolves".
   `About.xml` line 23 and `RUT_LanternstoneItems.xml` lines 14–16 carry the dulcis
   dependency note — delete both (the dependency ceases to exist).
10. **The sheet** — `the_lantern_deeps.md` line 41 lists the donor inventory by donor name
    ("gleamtip, crystalcap for mushroom logs, grey lady for lace"). That is a record of
    what was taken in and is frozen; add a one-line pointer to this file under Owed
    rather than editing the inventory sentence. `caverns_replacement_scoping.md` has 0
    hits on the flora names.
11. **Delete `lantern_deeps_rename_proposal.md`** once this is ruled — its content is
    rejected material, and the owner's rule is delete, not supersede-in-place.

### Grep census, current names (MEASURED 2026-09-18, `grep -rIl -i`, scoped to
`src/RimUtinni/LanternDeeps`, `infrastructure/artpipe`, `EXPECTED_FAILURES_next_load.md`,
`design/Jawa/worldbuilding/biomes`)

| name | files | of which artpipe history (done/ json+manifest, registry, throughput, status) | live sites to edit |
|---|---|---|---|
| Crystalcap | 12 | 6 | DeepFlora.xml, biome def, GenStep_DeepFloraGate.cs, ART_JOBS.md, wire_art.py, build_art_sheet.py |
| CrystaltipBrambles | 11 | 6 | same six |
| Arpeau | 11 | 8 | same six + DeepFloraPlanter.cs (comment) |
| Dulcis | 11 | 10 | same six + About.xml, RUT_LanternstoneItems.xml, EXPECTED_FAILURES |
| GreyLady | 11 | 12 | same six (the one `active/` hit is `rut_regenerantveil_v1.json`, an unrelated job whose prompt mentions the name — not a rename site) |
| Nuitae | 11 | 8 | same six + DeepFloraPlanter.cs (comment) |
| Fungusfern | 12 | 10 | same six |
| Gleamtip | 12 | 6 | same six |
| LuminousSpout | 11 | 6 | same six + DeepFloraPlanter.cs (comment) |
| YumBulbs | 12 | 6 | same six + tint_organics.py (docstring) |
| DeepMycelium | — | — | KEEP; appears in the same six, unchanged |

Repo-wide the bare stems inflate: `Dulcis` 39 files / 160 hits, `GreyLady` 45 / 141,
`Arpeau` 37 / 109, `Nuitae` 35 / 108 — those counts include RotSporeKit's own dulcis, the
donor `BMT_*` names in UtinniPatches, and the review sheets in `Transient/`. None of
those are rename sites. The `Deep`-prefixed defNames themselves are 4–5 files each.

### Order of work

Defs + C# + texture moves + wire/build tables in one commit (a half-renamed mod is
magenta and NRE at once); puffer art jobs filed in a second; docs/expected-failures in a
third. Deploy with `deploy_custom_mods.py --mod LanternDeeps`, then a minimal-list
quicktest proves the eleven defs load and the gate GenStep finds all eleven names.
